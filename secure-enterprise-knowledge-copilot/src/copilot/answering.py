from __future__ import annotations

import re
import time
import uuid

from .model_gateway import generate_structured_answer, should_use_openai
from .repositories import KnowledgeRepository
from .retrieval import retrieve, tokenize
from .retrieval_scoring import not_run_profile
from .security import detect_prompt_injection, sanitize_evidence


SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


def _select_sentences(question: str, text: str, limit: int = 4) -> list[str]:
    query_tokens = set(tokenize(question))
    sentences = [s.strip() for s in SENTENCE_RE.split(text.replace("\n", " ")) if s.strip()]
    scored = []
    for sentence in sentences:
        tokens = set(tokenize(sentence))
        score = len(tokens & query_tokens)
        if score > 0:
            scored.append((score, sentence))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [sentence for _, sentence in scored[:limit]]


def generate_answer(repo: KnowledgeRepository, user_id: str, question: str, record: bool = True) -> dict:
    start = time.perf_counter()
    user = repo.get_user(user_id)
    if not user:
        raise ValueError(f"Unknown user_id: {user_id}")

    question_injection_hits = detect_prompt_injection(question)
    if question_injection_hits:
        trace_id = str(uuid.uuid4())
        security_events = [
            {
                "source": "user_message",
                "matched_patterns": question_injection_hits,
                "reason": "prompt_injection_pattern",
            }
        ]
        answer = (
            "I cannot follow instructions that try to bypass citations, access controls, or security policy. "
            "Ask the policy question without override instructions."
        )
        result = {
            "trace_id": trace_id,
            "user": user,
            "question": question,
            "answer": answer,
            "citations": [],
            "confidence": 0.05,
            "missing_evidence": ["User message matched prompt-injection governance patterns."],
            "abstain_reason": "user_prompt_injection_detected",
            "security_events": security_events,
            "model_provider": "local",
            "openai_gateway_enabled": should_use_openai(),
            "retrieved": [],
            "retrieval_profile": not_run_profile("user_prompt_injection_detected"),
            "permission_blocked_count": 0,
            "latency_ms": round((time.perf_counter() - start) * 1000, 2),
        }
        if record:
            repo.insert_trace(
                trace_id,
                user_id,
                question,
                {
                    "retrieval": {
                        "query_tokens": tokenize(question),
                        "hits": [],
                        "profile": result["retrieval_profile"],
                        "permission_blocked_count": 0,
                    },
                    "output": {
                        "answer": answer,
                        "citations": [],
                        "confidence": 0.05,
                        "abstain_reason": "user_prompt_injection_detected",
                        "security_events": security_events,
                        "model_provider": "local",
                    },
                },
            )
            repo.insert_audit(
                user_id,
                "query_answered",
                {
                    "trace_id": trace_id,
                    "question": question,
                    "citation_doc_ids": [],
                    "abstained": True,
                    "permission_blocked_count": 0,
                    "security_event_count": len(security_events),
                },
            )
        return result

    retrieval = retrieve(repo, user, question, k=5)
    hits = retrieval["hits"]
    trace_id = str(uuid.uuid4())
    security_events = []
    citations = []
    answer_parts = []
    top_score = hits[0]["score"] if hits else 0
    min_usable_score = max(0.25, top_score * 0.45)

    for hit in hits:
        if hit["score"] < min_usable_score:
            continue
        clean_text, removed_lines = sanitize_evidence(hit["text"])
        if removed_lines:
            security_events.append(
                {
                    "chunk_id": hit["id"],
                    "doc_id": hit["doc_id"],
                    "removed_lines": removed_lines,
                    "reason": "prompt_injection_pattern",
                }
            )
            continue
        if not clean_text:
            continue
        selected = _select_sentences(question, clean_text)
        if not selected:
            continue
        answer_parts.extend(selected)
        citations.append(
            {
                "chunk_id": hit["id"],
                "doc_id": hit["doc_id"],
                "title": hit["title"],
                "source_url": hit["source_url"],
                "version": hit["version"],
                "score": hit["score"],
                "source_span": hit.get("source_span", {}),
            }
        )
        if len(citations) >= 3:
            break

    has_accessible_evidence = bool(answer_parts and citations and top_score >= 0.25)

    if has_accessible_evidence:
        deduped = []
        seen = set()
        for part in answer_parts:
            if part not in seen:
                deduped.append(part)
                seen.add(part)
        answer = " ".join(deduped[:5])
        confidence = min(0.93, round(0.45 + top_score / 4, 2))
        abstain_reason = None
        missing_evidence = []
        evidence = [
            {
                "citation": citation,
                "selected_text": part,
            }
            for citation, part in zip(citations, deduped)
        ]
        openai_answer = generate_structured_answer(question, evidence, answer)
        model_provider = "openai" if openai_answer else "local"
        if openai_answer:
            answer = openai_answer["answer"]
            confidence = min(0.99, max(0.0, float(openai_answer["confidence"])))
            missing_evidence = openai_answer["missing_evidence"]
    else:
        answer = (
            "I do not have enough accessible, trustworthy evidence to answer this. "
            "Use an approved source or ask an administrator to grant access to the relevant document."
        )
        confidence = 0.15
        abstain_reason = "no_accessible_grounded_evidence"
        missing_evidence = ["No accessible retrieved chunk met the evidence threshold."]
        if retrieval["blocked_count"] > 0:
            missing_evidence.append("Some potentially relevant sources were not accessible to this user identity.")
        model_provider = "local"

    result = {
        "trace_id": trace_id,
        "user": user,
        "question": question,
        "answer": answer,
        "citations": citations,
        "confidence": confidence,
        "missing_evidence": missing_evidence,
        "abstain_reason": abstain_reason,
        "security_events": security_events,
        "model_provider": model_provider,
        "openai_gateway_enabled": should_use_openai(),
        "retrieved": [
            {
                "chunk_id": hit["id"],
                "doc_id": hit["doc_id"],
                "title": hit["title"],
                "score": hit["score"],
                "score_breakdown": hit["score_breakdown"],
                "rerank_score": hit.get("rerank_score"),
                "rerank_breakdown": hit.get("rerank_breakdown", {}),
                "embedding_model": hit.get("embedding_model"),
                "embedding_dimensions": hit.get("embedding_dimensions"),
                "source_span": hit.get("source_span", {}),
                "classification": hit["classification"],
                "security_flags": hit["security_flags"],
                "preview": hit["text"][:320],
            }
            for hit in hits
        ],
        "retrieval_profile": retrieval["profile"],
        "permission_blocked_count": retrieval["blocked_count"],
        "latency_ms": round((time.perf_counter() - start) * 1000, 2),
    }

    if record:
        repo.insert_trace(
            trace_id,
            user_id,
            question,
            {
                "retrieval": {
                    "query_tokens": retrieval["query_tokens"],
                    "hits": result["retrieved"],
                    "profile": retrieval["profile"],
                    "permission_blocked_count": retrieval["blocked_count"],
                },
                "output": {
                    "answer": answer,
                    "citations": citations,
                    "confidence": confidence,
                    "abstain_reason": abstain_reason,
                    "security_events": security_events,
                    "model_provider": model_provider,
                },
            },
        )
        repo.insert_audit(
            user_id,
            "query_answered",
            {
                "trace_id": trace_id,
                "question": question,
                "citation_doc_ids": [citation["doc_id"] for citation in citations],
                "abstained": abstain_reason is not None,
                "permission_blocked_count": retrieval["blocked_count"],
                "security_event_count": len(security_events),
            },
        )

    return result
