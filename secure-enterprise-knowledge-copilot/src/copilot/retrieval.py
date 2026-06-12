from __future__ import annotations

import re
from collections import Counter

from .embeddings import embed_chunk, embed_text
from .identity import has_identity_access
from .reranking import RERANK_FEATURES, RERANKER_NAME, rerank_hits
from .repositories import KnowledgeRepository
from .retrieval_scoring import not_run_profile, retrieval_profile, score_chunk
from .security import detect_prompt_injection
from .source_lifecycle import SOURCE_LIFECYCLE_POLICY, is_active_source


TOKEN_RE = re.compile(r"[a-z0-9_]+|[\u4e00-\u9fff]", re.IGNORECASE)
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "current", "do", "for", "from",
    "how", "i", "in", "is", "it", "of", "on", "or", "our", "should", "the",
    "to", "must", "we", "what", "when", "where", "who", "why", "with", "you",
}

SYNONYMS = {
    "wfh": {"remote", "work", "home"},
    "remote": {"remote", "telework", "home"},
    "pii": {"pii", "personal", "customer", "data"},
    "finance": {"finance", "financial", "retention", "budget"},
    "retention": {"retention", "finance", "confidential"},
    "incident": {"incident", "security", "escalation"},
    "audit": {"audit", "trace", "logging", "evidence"},
    "citation": {"citation", "source", "evidence"},
}


def tokenize(text: str) -> list[str]:
    raw = [token.lower() for token in TOKEN_RE.findall(text)]
    tokens = [token for token in raw if token not in STOPWORDS and len(token) > 1 and not token.isdigit()]
    expanded = list(tokens)
    for token in tokens:
        expanded.extend(SYNONYMS.get(token, set()))
    return expanded


def _allowed(row: dict, user: dict) -> bool:
    return has_identity_access(row, user)


def retrieve(repo: KnowledgeRepository, user: dict, question: str, k: int = 5) -> dict:
    query_tokens = tokenize(question)
    if not query_tokens:
        return {
            "hits": [],
            "blocked_count": 0,
            "query_tokens": [],
            "profile": not_run_profile("empty_query"),
        }

    query_embedding = embed_text(question)
    candidate_limit = max(k * 4, 20)
    candidate_payload = repo.list_retrieval_candidates(
        user=user,
        question=question,
        query_tokens=query_tokens,
        query_embedding=query_embedding.vector,
        limit=candidate_limit,
    )
    visible_chunks = [chunk for chunk in candidate_payload.get("chunks", []) if _allowed(chunk, user)]
    active_visible_chunks = [chunk for chunk in visible_chunks if is_active_source(chunk)]
    stale_filtered_count = len(visible_chunks) - len(active_visible_chunks)
    visible_chunk_count = int(candidate_payload.get("visible_chunk_count", len(visible_chunks)))
    candidate_source_count = int(candidate_payload.get("candidate_count", len(visible_chunks)))
    candidate_strategy = str(candidate_payload.get("candidate_strategy", "local_full_scan"))

    doc_freq: Counter[str] = Counter()
    tokenized_chunks: dict[str, list[str]] = {}
    for chunk in active_visible_chunks:
        tokens = tokenize(chunk["title"] + " " + chunk["text"])
        tokenized_chunks[chunk["id"]] = tokens
        for token in set(tokens):
            doc_freq[token] += 1

    n_docs = max(visible_chunk_count, 1)
    scored = []

    for chunk in active_visible_chunks:
        chunk_embedding = chunk.get("embedding")
        embedding_model = chunk.get("embedding_model")
        embedding_dimensions = chunk.get("embedding_dimensions")
        if not chunk_embedding:
            generated_embedding = embed_chunk(chunk["title"], chunk["text"])
            chunk_embedding = generated_embedding.vector
            embedding_model = generated_embedding.model
            embedding_dimensions = generated_embedding.dimensions
        scoring = score_chunk(
            question=question,
            query_tokens=query_tokens,
            chunk_text=chunk["text"],
            title_tokens=tokenize(chunk["title"]),
            chunk_tokens=tokenized_chunks[chunk["id"]],
            doc_freq=doc_freq,
            n_docs=n_docs,
            query_embedding=query_embedding.vector,
            chunk_embedding=chunk_embedding,
        )
        if scoring.total <= 0:
            continue

        hit = dict(chunk)
        hit["score"] = round(scoring.total, 4)
        hit["score_breakdown"] = scoring.as_breakdown()
        hit["embedding_model"] = embedding_model
        hit["embedding_dimensions"] = embedding_dimensions
        hit["security_flags"] = detect_prompt_injection(hit["text"])
        scored.append(hit)

    scored.sort(key=lambda item: item["score"], reverse=True)
    reranked = rerank_hits(scored, query_tokens)

    blocked_count = repo.count_potentially_blocked_chunks(user, query_tokens)

    return {
        "hits": reranked[:k],
        "blocked_count": blocked_count,
        "query_tokens": query_tokens,
        "profile": retrieval_profile(
            visible_chunk_count=visible_chunk_count,
            candidate_count=len(scored),
            top_k=k,
            candidate_strategy=candidate_strategy,
            candidate_source_count=candidate_source_count,
            reranker=RERANKER_NAME,
            rerank_features=RERANK_FEATURES,
            source_lifecycle_policy=SOURCE_LIFECYCLE_POLICY,
            stale_filtered_count=stale_filtered_count,
        ),
    }
