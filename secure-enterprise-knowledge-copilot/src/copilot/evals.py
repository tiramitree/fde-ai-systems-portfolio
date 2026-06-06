from __future__ import annotations

import json
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
        min_blocked_count = retrieval_expected.get("min_permission_blocked_count")
        if min_blocked_count is not None and output["permission_blocked_count"] < min_blocked_count:
            failures.append(f"permission_blocked_count_below:{min_blocked_count}")

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
    retrieval_cases = sum(1 for case in cases if case["expected"].get("retrieval", {}).get("must_retrieve_doc_ids"))
    citation_cases = sum(1 for case in cases if case["expected"].get("must_cite_doc_ids"))
    citation_span_failures = sum(
        1
        for item in results
        if any(
            failure.startswith("missing_chunk_source_span")
            or failure.startswith("missing_citation_evidence_span")
            for failure in item["failures"]
        )
    )
    metrics = {
        "total_cases": total,
        "passed_cases": passed,
        "pass_rate": round(passed / total, 3) if total else 0,
        "unsafe_leak_failures": unsafe_leaks,
        "retrieval_cases": retrieval_cases,
        "retrieval_miss_failures": retrieval_misses,
        "retrieval_recall_at_k": round((retrieval_cases - retrieval_misses) / retrieval_cases, 3)
        if retrieval_cases
        else 0,
        "citation_cases": citation_cases,
        "citation_span_failures": citation_span_failures,
        "citation_span_coverage": round((citation_cases - citation_span_failures) / citation_cases, 3)
        if citation_cases
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
