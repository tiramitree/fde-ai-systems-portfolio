from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass

from .embeddings import EMBEDDING_DIMENSIONS, EMBEDDING_MODEL, cosine_similarity

SCORE_COMPONENTS = ("bm25_like", "title", "phrase", "semantic_family", "vector")

SEMANTIC_FAMILIES = {
    "remote_work": {"remote", "telework", "home", "work", "wfh", "office", "capacity"},
    "pii_handling": {"pii", "personal", "customer", "data", "mask", "masked", "export", "storage"},
    "finance_retention": {"finance", "financial", "retention", "pool", "budget", "nomination"},
    "incident_response": {"incident", "sev1", "commander", "postmortem", "security", "escalation"},
    "auditability": {"audit", "trace", "logging", "evidence", "citation", "model", "latency"},
    "vendor_governance": {"vendor", "onboarding", "questionnaire", "access", "processing"},
}


@dataclass(frozen=True)
class RetrievalScore:
    total: float
    lexical: float
    title: float
    phrase: float
    semantic: float
    vector: float
    length_norm: float
    matched_terms: tuple[str, ...]
    semantic_matches: tuple[str, ...]

    def as_breakdown(self) -> dict:
        return {
            "lexical": round(self.lexical, 4),
            "title": round(self.title, 4),
            "phrase": round(self.phrase, 4),
            "semantic": round(self.semantic, 4),
            "vector": round(self.vector, 4),
            "length_norm": round(self.length_norm, 4),
            "matched_terms": list(self.matched_terms),
            "semantic_matches": list(self.semantic_matches),
        }


def retrieval_profile(
    visible_chunk_count: int,
    candidate_count: int,
    top_k: int,
    candidate_strategy: str = "local_full_scan",
    candidate_source_count: int | None = None,
    reranker: str = "none",
    rerank_features: tuple[str, ...] = (),
    source_lifecycle_policy: str = "active_sources_only",
    stale_filtered_count: int = 0,
) -> dict:
    return {
        "name": "local-hybrid-v1",
        "score_components": list(SCORE_COMPONENTS),
        "permission_filter": "tenant_identity_before_scoring",
        "source_lifecycle_policy": source_lifecycle_policy,
        "stale_filtered_count": stale_filtered_count,
        "candidate_strategy": candidate_strategy,
        "candidate_source_count": candidate_count if candidate_source_count is None else candidate_source_count,
        "reranker": reranker,
        "rerank_features": list(rerank_features),
        "embedding_model": EMBEDDING_MODEL,
        "embedding_dimensions": EMBEDDING_DIMENSIONS,
        "visible_chunk_count": visible_chunk_count,
        "candidate_count": candidate_count,
        "top_k": top_k,
    }


def not_run_profile(reason: str) -> dict:
    return {
        "name": "not-run",
        "reason": reason,
        "score_components": [],
        "permission_filter": "tenant_identity_before_scoring",
        "source_lifecycle_policy": "active_sources_only",
        "stale_filtered_count": 0,
        "visible_chunk_count": 0,
        "candidate_count": 0,
        "top_k": 0,
    }


def score_chunk(
    question: str,
    query_tokens: list[str],
    chunk_text: str,
    title_tokens: list[str],
    chunk_tokens: list[str],
    doc_freq: Counter[str],
    n_docs: int,
    query_embedding: list[float] | None = None,
    chunk_embedding: list[float] | None = None,
) -> RetrievalScore:
    query_counter = Counter(query_tokens)
    counts = Counter(chunk_tokens)
    length_norm = 1 + math.log(max(len(chunk_tokens), 1))
    lexical = 0.0
    matched_terms = []

    for token, q_count in query_counter.items():
        if counts[token] == 0:
            continue
        matched_terms.append(token)
        idf = math.log((n_docs + 1) / (doc_freq[token] + 0.5)) + 1
        tf = counts[token] / (counts[token] + 1.2)
        lexical += q_count * idf * tf

    title = 0.35 * len(set(query_tokens) & set(title_tokens))
    phrase = 0.5 if question.lower() in chunk_text.lower() else 0.0
    semantic_matches = _semantic_matches(query_tokens, chunk_tokens)
    semantic = 0.25 * len(semantic_matches)
    vector = 0.45 * max(0.0, cosine_similarity(query_embedding, chunk_embedding))
    total = (lexical / length_norm) + title + phrase + semantic + vector
    return RetrievalScore(
        total=total,
        lexical=lexical,
        title=title,
        phrase=phrase,
        semantic=semantic,
        vector=vector,
        length_norm=length_norm,
        matched_terms=tuple(sorted(set(matched_terms))),
        semantic_matches=tuple(semantic_matches),
    )


def _semantic_matches(query_tokens: list[str], chunk_tokens: list[str]) -> list[str]:
    query_set = set(query_tokens)
    chunk_set = set(chunk_tokens)
    matches = []
    for family, terms in SEMANTIC_FAMILIES.items():
        if query_set & terms and chunk_set & terms:
            matches.append(family)
    return sorted(matches)
