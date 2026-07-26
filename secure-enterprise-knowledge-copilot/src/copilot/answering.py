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


def _with_request_id(payload: dict, request_id: str) -> dict:
    if request_id:
        payload["request_id"] = request_id
    return payload


def _find_sentence_span(text: str, sentence: str) -> tuple[int, int] | None:
    start = text.find(sentence)
    if start >= 0:
        return start, start + len(sentence)
    parts = sentence.split()
    if not parts:
        return None
    pattern = r"\s+".join(re.escape(part) for part in parts)
    match = re.search(pattern, text)
    if not match:
        return None
    return match.start(), match.end()


def _source_span_for_selection(chunk_span: dict, chunk_text: str, start_offset: int, end_offset: int) -> dict:
    if not isinstance(chunk_span, dict) or start_offset < 0 or end_offset <= start_offset:
        return {}
    try:
        chunk_start_char = int(chunk_span["start_char"])
        chunk_start_line = int(chunk_span["start_line"])
    except (KeyError, TypeError, ValueError):
        return {}
    prefix_before_start = chunk_text[:start_offset]
    prefix_before_end = chunk_text[: max(start_offset, end_offset - 1)]
    return {
        "text_unit": chunk_span.get("text_unit", "normalized_text"),
        "start_char": chunk_start_char + start_offset,
        "end_char": chunk_start_char + end_offset,
        "start_line": chunk_start_line + prefix_before_start.count("\n"),
        "end_line": chunk_start_line + prefix_before_end.count("\n"),
    }


def _select_sentence_records(question: str, text: str, chunk_span: dict, limit: int = 4) -> list[dict]:
    query_tokens = set(tokenize(question))
    sentences = [s.strip() for s in SENTENCE_RE.split(text.replace("\n", " ")) if s.strip()]
    scored = []
    for sentence in sentences:
        tokens = set(tokenize(sentence))
        score = len(tokens & query_tokens)
        if score > 0:
            span = _find_sentence_span(text, sentence)
            start_offset, end_offset = span if span else (-1, -1)
            scored.append((score, start_offset if start_offset >= 0 else 10**9, sentence, start_offset, end_offset))
    scored.sort(key=lambda item: (-item[0], item[1], item[2]))
    records = []
    for _, _, sentence, start_offset, end_offset in scored[:limit]:
        records.append(
            {
                "text": sentence,
                "source_span": _source_span_for_selection(chunk_span, text, start_offset, end_offset),
            }
        )
    return records


def generate_answer(repo: KnowledgeRepository, user_id: str, question: str, record: bool = True, request_id: str = "") -> dict:
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
        result = _with_request_id(
            {
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
            },
            request_id,
        )
        if record:
            repo.insert_trace(
                trace_id,
                user_id,
                question,
                _with_request_id(
                    {
                        "latency_ms": result["latency_ms"],
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
                    request_id,
                ),
            )
            repo.insert_audit(
                user_id,
                "query_answered",
                _with_request_id(
                    {
                        "trace_id": trace_id,
                        "question": question,
                        "citation_doc_ids": [],
                        "abstained": True,
                        "permission_blocked_count": 0,
                        "security_event_count": len(security_events),
                    },
                    request_id,
                ),
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
        selected = _select_sentence_records(question, clean_text, hit.get("source_span", {}))
        if not selected:
            continue
        answer_parts.extend(record["text"] for record in selected)
        citations.append(
            {
                "chunk_id": hit["id"],
                "doc_id": hit["doc_id"],
                "title": hit["title"],
                "source_url": hit["source_url"],
                "version": hit["version"],
                "score": hit["score"],
                "source_span": hit.get("source_span", {}),
                "evidence_excerpt": " ".join(record["text"] for record in selected),
                "evidence_spans": selected,
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
                "selected_text": citation.get("evidence_excerpt", ""),
            }
            for citation in citations
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

    result = _with_request_id(
        {
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
        },
        request_id,
    )

    if record:
        repo.insert_trace(
            trace_id,
            user_id,
            question,
            _with_request_id(
                {
                    "latency_ms": result["latency_ms"],
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
                request_id,
            ),
        )
        repo.insert_audit(
            user_id,
            "query_answered",
            _with_request_id(
                {
                    "trace_id": trace_id,
                    "question": question,
                    "citation_doc_ids": [citation["doc_id"] for citation in citations],
                    "abstained": abstain_reason is not None,
                    "permission_blocked_count": retrieval["blocked_count"],
                    "security_event_count": len(security_events),
                },
                request_id,
            ),
        )

    return result
