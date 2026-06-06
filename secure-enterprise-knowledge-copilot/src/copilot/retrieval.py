from __future__ import annotations

import re
from collections import Counter

from .embeddings import embed_chunk, embed_text
from .repositories import KnowledgeRepository
from .retrieval_scoring import not_run_profile, retrieval_profile, score_chunk
from .security import detect_prompt_injection


TOKEN_RE = re.compile(r"[a-z0-9_]+|[\u4e00-\u9fff]", re.IGNORECASE)
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "do", "for", "from",
    "how", "i", "in", "is", "it", "of", "on", "or", "our", "should", "the",
    "to", "we", "what", "when", "where", "who", "why", "with", "you",
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
    roles = row["allowed_roles"]
    return row["tenant_id"] == user["tenant_id"] and user["role"] in roles


def retrieve(repo: KnowledgeRepository, user: dict, question: str, k: int = 5) -> dict:
    all_chunks = repo.list_chunks(user["tenant_id"])
    visible_chunks = [chunk for chunk in all_chunks if _allowed(chunk, user)]

    query_tokens = tokenize(question)
    if not query_tokens:
        return {
            "hits": [],
            "blocked_count": 0,
            "query_tokens": [],
            "profile": not_run_profile("empty_query"),
        }

    doc_freq: Counter[str] = Counter()
    tokenized_chunks: dict[str, list[str]] = {}
    for chunk in visible_chunks:
        tokens = tokenize(chunk["title"] + " " + chunk["text"])
        tokenized_chunks[chunk["id"]] = tokens
        for token in set(tokens):
            doc_freq[token] += 1

    n_docs = max(len(visible_chunks), 1)
    query_embedding = embed_text(question)
    scored = []

    for chunk in visible_chunks:
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

    blocked_count = repo.count_potentially_blocked_chunks(user, query_tokens)

    return {
        "hits": scored[:k],
        "blocked_count": blocked_count,
        "query_tokens": query_tokens,
        "profile": retrieval_profile(
            visible_chunk_count=len(visible_chunks),
            candidate_count=len(scored),
            top_k=k,
        ),
    }
