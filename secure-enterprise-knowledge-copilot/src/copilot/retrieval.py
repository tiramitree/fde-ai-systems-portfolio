from __future__ import annotations

import math
import re
from collections import Counter

from .repositories import KnowledgeRepository
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
        return {"hits": [], "blocked_count": 0, "query_tokens": []}

    doc_freq: Counter[str] = Counter()
    tokenized_chunks: dict[str, list[str]] = {}
    for chunk in visible_chunks:
        tokens = tokenize(chunk["title"] + " " + chunk["text"])
        tokenized_chunks[chunk["id"]] = tokens
        for token in set(tokens):
            doc_freq[token] += 1

    n_docs = max(len(visible_chunks), 1)
    query_counter = Counter(query_tokens)
    scored = []

    for chunk in visible_chunks:
        chunk_tokens = tokenized_chunks[chunk["id"]]
        counts = Counter(chunk_tokens)
        length_norm = 1 + math.log(max(len(chunk_tokens), 1))
        bm25_like = 0.0
        for token, q_count in query_counter.items():
            if counts[token] == 0:
                continue
            idf = math.log((n_docs + 1) / (doc_freq[token] + 0.5)) + 1
            tf = counts[token] / (counts[token] + 1.2)
            bm25_like += q_count * idf * tf

        title_tokens = set(tokenize(chunk["title"]))
        title_boost = 0.35 * len(set(query_tokens) & title_tokens)
        phrase_boost = 0.5 if question.lower() in chunk["text"].lower() else 0.0
        score = (bm25_like / length_norm) + title_boost + phrase_boost
        if score <= 0:
            continue

        hit = dict(chunk)
        hit["score"] = round(score, 4)
        hit["security_flags"] = detect_prompt_injection(hit["text"])
        scored.append(hit)

    scored.sort(key=lambda item: item["score"], reverse=True)

    blocked_count = 0
    for chunk in all_chunks:
        if _allowed(chunk, user):
            continue
        inaccessible_tokens = tokenize(chunk["title"] + " " + chunk["text"])
        if set(query_tokens) & set(inaccessible_tokens):
            blocked_count += 1

    return {
        "hits": scored[:k],
        "blocked_count": blocked_count,
        "query_tokens": query_tokens,
    }
