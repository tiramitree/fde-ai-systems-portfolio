from __future__ import annotations

import json
import math
import uuid
from pathlib import Path

from .answering import generate_answer
from .repositories import KnowledgeRepository
from .time_utils import utc_now


DATA_DIR = Path(__file__).resolve().parents[2] / "data"
EVAL_CASES_PATH = DATA_DIR / "eval_cases.json"


def _valid_source_span(value: object) -> bool:
    if not isinstance(value, dict):
        return False
    required_ints = ("start_char", "end_char", "start_line", "end_line")
    if value.get("text_unit") != "normalized_text":
        return False
    if not all(isinstance(value.get(key), int) for key in required_ints):
        return False
    return int(value["start_char"]) <= int(value["end_char"]) and int(value["start_line"]) <= int(value["end_line"])


def _citation_has_evidence_span(citation: dict) -> bool:
    spans = citation.get("evidence_spans")
    return (
        isinstance(citation.get("evidence_excerpt"), str)
        and bool(citation["evidence_excerpt"].strip())
        and isinstance(spans, list)
        and bool(spans)
        and all(isinstance(item, dict) and item.get("text") and _valid_source_span(item.get("source_span")) for item in spans)
    )


def _reciprocal_rank(retrieved_doc_ids: list[str], expected_doc_ids: list[str]) -> float:
    expected = set(expected_doc_ids)
    if not expected:
        return 0.0
    for index, doc_id in enumerate(retrieved_doc_ids, start=1):
        if doc_id in expected:
            return 1 / index
    return 0.0


def _dcg_at_k(retrieved_doc_ids: list[str], expected_doc_ids: list[str]) -> float:
    expected = set(expected_doc_ids)
    if not expected:
        return 0.0
    return sum(1 / math.log2(index + 1) for index, doc_id in enumerate(retrieved_doc_ids, start=1) if doc_id in expected)


def _ndcg_at_k(retrieved_doc_ids: list[str], expected_doc_ids: list[str]) -> float:
    expected = set(expected_doc_ids)
    if not expected:
        return 0.0
    ideal_hits = min(len(expected), len(retrieved_doc_ids))
    if ideal_hits == 0:
        return 0.0
    ideal_dcg = sum(1 / math.log2(index + 1) for index in range(1, ideal_hits + 1))
    return _dcg_at_k(retrieved_doc_ids, expected_doc_ids) / ideal_dcg


def _average_precision_at_k(retrieved_doc_ids: list[str], expected_doc_ids: list[str]) -> float:
    expected = set(expected_doc_ids)
    if not expected:
        return 0.0
    hits = 0
    precision_sum = 0.0
    for index, doc_id in enumerate(retrieved_doc_ids, start=1):
        if doc_id in expected:
            hits += 1
            precision_sum += hits / index
    return precision_sum / len(expected)


def _required_retrieval_hit_count(case: dict, result: dict) -> int:
    expected_doc_ids = set(case["expected"].get("retrieval", {}).get("must_retrieve_doc_ids", []))
    return len(expected_doc_ids & set(result["retrieved_doc_ids"]))


def run_evals(repo: KnowledgeRepository, cases_path: Path = EVAL_CASES_PATH, persist: bool = True) -> dict:
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    results = []

    for case in cases:
        output = generate_answer(repo, case["user_id"], case["question"], record=True)
        cited_doc_ids = {citation["doc_id"] for citation in output["citations"]}
        retrieved_doc_ids = [item["doc_id"] for item in output.get("retrieved", [])]
        retrieved_doc_id_set = set(retrieved_doc_ids)
        failures = []

        expected = case["expected"]
        if expected["behavior"] == "answer" and output["abstain_reason"]:
            failures.append("expected_answer_but_abstained")
        if expected["behavior"] == "abstain" and not output["abstain_reason"]:
            failures.append("expected_abstain_but_answered")

        for doc_id in expected.get("must_cite_doc_ids", []):
            if doc_id not in cited_doc_ids:
                failures.append(f"missing_required_citation:{doc_id}")

        if expected["behavior"] == "answer":
            for citation in output["citations"]:
                if not _valid_source_span(citation.get("source_span")):
                    failures.append(f"missing_chunk_source_span:{citation.get('doc_id', 'unknown')}")
                if not _citation_has_evidence_span(citation):
                    failures.append(f"missing_citation_evidence_span:{citation.get('doc_id', 'unknown')}")

        for doc_id in expected.get("forbidden_doc_ids", []):
            if doc_id in cited_doc_ids:
                failures.append(f"forbidden_citation_leaked:{doc_id}")

        if expected.get("requires_security_event") and not output["security_events"]:
            failures.append("missing_security_event")

        retrieval_expected = expected.get("retrieval", {})
        for doc_id in retrieval_expected.get("must_retrieve_doc_ids", []):
            if doc_id not in retrieved_doc_id_set:
                failures.append(f"missing_required_retrieval:{doc_id}")
        for doc_id in retrieval_expected.get("forbidden_retrieve_doc_ids", []):
            if doc_id in retrieved_doc_id_set:
                failures.append(f"forbidden_retrieval_leaked:{doc_id}")
        if cited_doc_ids and not cited_doc_ids.issubset(retrieved_doc_id_set):
            missing_context = sorted(cited_doc_ids - retrieved_doc_id_set)
            failures.append(f"citation_not_grounded_in_retrieved_context:{','.join(missing_context)}")
        min_blocked_count = retrieval_expected.get("min_permission_blocked_count")
        if min_blocked_count is not None and output["permission_blocked_count"] < min_blocked_count:
            failures.append(f"permission_blocked_count_below:{min_blocked_count}")
        min_stale_filtered_count = retrieval_expected.get("min_stale_filtered_count")
        stale_filtered_count = int(output.get("retrieval_profile", {}).get("stale_filtered_count", 0) or 0)
        if min_stale_filtered_count is not None and stale_filtered_count < min_stale_filtered_count:
            failures.append(f"stale_filtered_count_below:{min_stale_filtered_count}")

        required_retrieval_doc_ids = retrieval_expected.get("must_retrieve_doc_ids", [])
        required_retrieval_hits = _required_retrieval_hit_count(case, {"retrieved_doc_ids": retrieved_doc_ids})
        required_citation_hits = len(set(expected.get("must_cite_doc_ids", [])) & cited_doc_ids)
        results.append(
            {
                "id": case["id"],
                "user_id": case["user_id"],
                "question": case["question"],
                "passed": not failures,
                "failures": failures,
                "trace_id": output["trace_id"],
                "abstained": output["abstain_reason"] is not None,
                "citations": list(cited_doc_ids),
                "retrieved_doc_ids": retrieved_doc_ids,
                "top_retrieved_doc_id": retrieved_doc_ids[0] if retrieved_doc_ids else None,
                "required_retrieval_hit_count": required_retrieval_hits,
                "expected_retrieval_doc_count": len(required_retrieval_doc_ids),
                "retrieval_recall_at_k": round(required_retrieval_hits / len(required_retrieval_doc_ids), 3)
                if required_retrieval_doc_ids
                else None,
                "retrieval_precision_at_k": round(required_retrieval_hits / len(retrieved_doc_ids), 3)
                if required_retrieval_doc_ids and retrieved_doc_ids
                else None,
                "reciprocal_rank": round(_reciprocal_rank(retrieved_doc_ids, required_retrieval_doc_ids), 3)
                if required_retrieval_doc_ids
                else None,
                "ndcg_at_k": round(_ndcg_at_k(retrieved_doc_ids, required_retrieval_doc_ids), 3)
                if required_retrieval_doc_ids
                else None,
                "average_precision_at_k": round(_average_precision_at_k(retrieved_doc_ids, required_retrieval_doc_ids), 3)
                if required_retrieval_doc_ids
                else None,
                "required_citation_hit_count": required_citation_hits,
                "citation_retrieval_aligned": cited_doc_ids.issubset(retrieved_doc_id_set),
                "security_event_required": bool(expected.get("requires_security_event")),
                "security_event_count": len(output["security_events"]),
                "retrieval_profile": output.get("retrieval_profile", {}),
                "latency_ms": output["latency_ms"],
            }
        )

    total = len(results)
    passed = sum(1 for item in results if item["passed"])
    unsafe_leaks = sum(
        1 for item in results for failure in item["failures"] if failure.startswith("forbidden_citation_leaked")
    )
    retrieval_misses = sum(
        1 for item in results for failure in item["failures"] if failure.startswith("missing_required_retrieval")
    )
    forbidden_retrieval_leaks = sum(
        1 for item in results for failure in item["failures"] if failure.startswith("forbidden_retrieval_leaked")
    )
    retrieval_cases = sum(1 for case in cases if case["expected"].get("retrieval", {}).get("must_retrieve_doc_ids"))
    expected_retrieval_doc_count = sum(
        len(case["expected"].get("retrieval", {}).get("must_retrieve_doc_ids", [])) for case in cases
    )
    retrieved_required_doc_count = sum(
        _required_retrieval_hit_count(case, result) for case, result in zip(cases, results)
    )
    required_doc_precision_values = [
        _required_retrieval_hit_count(case, result) / len(result["retrieved_doc_ids"])
        for case, result in zip(cases, results)
        if case["expected"].get("retrieval", {}).get("must_retrieve_doc_ids") and result["retrieved_doc_ids"]
    ]
    reciprocal_ranks = [
        _reciprocal_rank(
            result["retrieved_doc_ids"],
            case["expected"].get("retrieval", {}).get("must_retrieve_doc_ids", []),
        )
        for case, result in zip(cases, results)
        if case["expected"].get("retrieval", {}).get("must_retrieve_doc_ids")
    ]
    ndcg_values = [
        _ndcg_at_k(
            result["retrieved_doc_ids"],
            case["expected"].get("retrieval", {}).get("must_retrieve_doc_ids", []),
        )
        for case, result in zip(cases, results)
        if case["expected"].get("retrieval", {}).get("must_retrieve_doc_ids")
    ]
    average_precision_values = [
        _average_precision_at_k(
            result["retrieved_doc_ids"],
            case["expected"].get("retrieval", {}).get("must_retrieve_doc_ids", []),
        )
        for case, result in zip(cases, results)
        if case["expected"].get("retrieval", {}).get("must_retrieve_doc_ids")
    ]
    citation_cases = sum(1 for case in cases if case["expected"].get("must_cite_doc_ids"))
    expected_citation_doc_count = sum(len(case["expected"].get("must_cite_doc_ids", [])) for case in cases)
    cited_required_doc_count = sum(
        len(set(case["expected"].get("must_cite_doc_ids", [])) & set(result["citations"]))
        for case, result in zip(cases, results)
    )
    citation_span_failures = sum(
        1
        for item in results
        if any(
            failure.startswith("missing_chunk_source_span")
            or failure.startswith("missing_citation_evidence_span")
            for failure in item["failures"]
        )
    )
    citation_retrieval_alignment_failures = sum(
        1
        for item in results
        if any(failure.startswith("citation_not_grounded_in_retrieved_context") for failure in item["failures"])
    )
    stale_source_cases = sum(
        1 for case in cases if case["expected"].get("retrieval", {}).get("min_stale_filtered_count") is not None
    )
    stale_source_failures = sum(
        1 for item in results for failure in item["failures"] if failure.startswith("stale_filtered_count_below")
    )
    permission_block_cases = sum(
        1
        for case in cases
        if case["expected"].get("retrieval", {}).get("min_permission_blocked_count") is not None
    )
    permission_block_failures = sum(
        1 for item in results for failure in item["failures"] if failure.startswith("permission_blocked_count_below")
    )
    answer_cases = sum(1 for case in cases if case["expected"]["behavior"] == "answer")
    abstain_cases = sum(1 for case in cases if case["expected"]["behavior"] == "abstain")
    behavior_failures = sum(
        1
        for item in results
        if any(
            failure in {"expected_answer_but_abstained", "expected_abstain_but_answered"}
            for failure in item["failures"]
        )
    )
    security_event_cases = sum(1 for case in cases if case["expected"].get("requires_security_event"))
    security_event_failures = sum(
        1 for item in results for failure in item["failures"] if failure == "missing_security_event"
    )
    metrics = {
        "total_cases": total,
        "passed_cases": passed,
        "pass_rate": round(passed / total, 3) if total else 0,
        "answer_cases": answer_cases,
        "abstain_cases": abstain_cases,
        "behavior_accuracy": round((total - behavior_failures) / total, 3) if total else 0,
        "unsafe_leak_failures": unsafe_leaks,
        "retrieval_cases": retrieval_cases,
        "retrieval_miss_failures": retrieval_misses,
        "retrieval_recall_at_k": round((retrieval_cases - retrieval_misses) / retrieval_cases, 3)
        if retrieval_cases
        else 0,
        "expected_retrieval_doc_count": expected_retrieval_doc_count,
        "retrieved_required_doc_count": retrieved_required_doc_count,
        "required_retrieval_recall_at_k": round(retrieved_required_doc_count / expected_retrieval_doc_count, 3)
        if expected_retrieval_doc_count
        else 0,
        "required_retrieval_precision_at_k": round(
            sum(required_doc_precision_values) / len(required_doc_precision_values),
            3,
        )
        if required_doc_precision_values
        else 0,
        "mean_reciprocal_rank": round(sum(reciprocal_ranks) / len(reciprocal_ranks), 3)
        if reciprocal_ranks
        else 0,
        "mean_ndcg_at_k": round(sum(ndcg_values) / len(ndcg_values), 3)
        if ndcg_values
        else 0,
        "mean_average_precision_at_k": round(
            sum(average_precision_values) / len(average_precision_values),
            3,
        )
        if average_precision_values
        else 0,
        "forbidden_retrieval_leak_failures": forbidden_retrieval_leaks,
        "citation_cases": citation_cases,
        "expected_citation_doc_count": expected_citation_doc_count,
        "cited_required_doc_count": cited_required_doc_count,
        "required_citation_coverage": round(cited_required_doc_count / expected_citation_doc_count, 3)
        if expected_citation_doc_count
        else 0,
        "citation_span_failures": citation_span_failures,
        "citation_span_coverage": round((citation_cases - citation_span_failures) / citation_cases, 3)
        if citation_cases
        else 0,
        "citation_retrieval_alignment_failures": citation_retrieval_alignment_failures,
        "citation_retrieval_alignment": round(
            (citation_cases - citation_retrieval_alignment_failures) / citation_cases,
            3,
        )
        if citation_cases
        else 0,
        "security_event_cases": security_event_cases,
        "security_event_failures": security_event_failures,
        "security_event_coverage": round((security_event_cases - security_event_failures) / security_event_cases, 3)
        if security_event_cases
        else 0,
        "permission_block_cases": permission_block_cases,
        "permission_block_failures": permission_block_failures,
        "permission_block_coverage": round((permission_block_cases - permission_block_failures) / permission_block_cases, 3)
        if permission_block_cases
        else 0,
        "stale_source_cases": stale_source_cases,
        "stale_source_filter_failures": stale_source_failures,
        "stale_source_filter_coverage": round((stale_source_cases - stale_source_failures) / stale_source_cases, 3)
        if stale_source_cases
        else 0,
        "average_latency_ms": round(sum(item["latency_ms"] for item in results) / total, 2) if total else 0,
    }

    run_id = str(uuid.uuid4())
    payload = {"id": run_id, "created_at": utc_now(), "metrics": metrics, "cases": results}
    if persist:
        repo.insert_eval_run(payload)
    return payload


def latest_eval_run(repo: KnowledgeRepository) -> dict | None:
    return repo.latest_eval_run()
