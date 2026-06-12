from __future__ import annotations

from dataclasses import dataclass


RERANKER_NAME = "local-evidence-reranker-v1"
RERANK_FEATURES = (
    "base_score",
    "query_overlap",
    "title_overlap",
    "source_metadata",
    "candidate_keyword",
    "candidate_vector",
    "security_penalty",
)


@dataclass(frozen=True)
class RerankDecision:
    score: float
    breakdown: dict


def rerank_hits(hits: list[dict], query_tokens: list[str]) -> list[dict]:
    query_set = set(query_tokens)
    reranked = []
    for hit in hits:
        decision = rerank_hit(hit, query_set)
        enriched = dict(hit)
        enriched["rerank_score"] = decision.score
        enriched["rerank_breakdown"] = decision.breakdown
        reranked.append(enriched)
    reranked.sort(key=lambda item: (item["rerank_score"], item["score"]), reverse=True)
    return reranked


def rerank_hit(hit: dict, query_tokens: set[str]) -> RerankDecision:
    breakdown = hit.get("score_breakdown", {})
    matched_terms = set(breakdown.get("matched_terms", []))
    title_tokens = set(_tokens(hit.get("title", "")))
    candidate_scores = hit.get("candidate_source_scores", {})

    query_overlap = _ratio(matched_terms, query_tokens)
    title_overlap = _ratio(title_tokens & query_tokens, query_tokens)
    source_metadata = _source_metadata_score(hit)
    candidate_keyword = min(float(candidate_scores.get("keyword", 0.0) or 0.0), 1.0)
    candidate_vector = max(0.0, min(float(candidate_scores.get("vector", 0.0) or 0.0), 1.0))
    security_penalty = 1.5 if hit.get("security_flags") else 0.0
    base_score = float(hit.get("score", 0.0))

    total = (
        base_score
        + 0.35 * query_overlap
        + 0.2 * title_overlap
        + 0.05 * source_metadata
        + 0.05 * candidate_keyword
        + 0.05 * candidate_vector
        - security_penalty
    )
    return RerankDecision(
        score=round(total, 4),
        breakdown={
            "base_score": round(base_score, 4),
            "query_overlap": round(query_overlap, 4),
            "title_overlap": round(title_overlap, 4),
            "source_metadata": round(source_metadata, 4),
            "candidate_keyword": round(candidate_keyword, 4),
            "candidate_vector": round(candidate_vector, 4),
            "security_penalty": round(security_penalty, 4),
        },
    )


def _ratio(left: set[str], right: set[str]) -> float:
    if not right:
        return 0.0
    return len(left) / len(right)


def _source_metadata_score(hit: dict) -> float:
    fields = ("source_url", "source_hash", "version", "updated_at")
    present = sum(1 for field in fields if hit.get(field))
    return present / len(fields)


def _tokens(text: str) -> set[str]:
    return {part.strip(".,;:!?()[]{}").lower() for part in text.split() if part.strip()}
