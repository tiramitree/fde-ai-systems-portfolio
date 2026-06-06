from __future__ import annotations

import json
import uuid
from pathlib import Path

from .answering import generate_answer
from .repositories import KnowledgeRepository
from .time_utils import utc_now


DATA_DIR = Path(__file__).resolve().parents[2] / "data"
EVAL_CASES_PATH = DATA_DIR / "eval_cases.json"


def run_evals(repo: KnowledgeRepository, cases_path: Path = EVAL_CASES_PATH, persist: bool = True) -> dict:
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    results = []

    for case in cases:
        output = generate_answer(repo, case["user_id"], case["question"], record=True)
        cited_doc_ids = {citation["doc_id"] for citation in output["citations"]}
        failures = []

        expected = case["expected"]
        if expected["behavior"] == "answer" and output["abstain_reason"]:
            failures.append("expected_answer_but_abstained")
        if expected["behavior"] == "abstain" and not output["abstain_reason"]:
            failures.append("expected_abstain_but_answered")

        for doc_id in expected.get("must_cite_doc_ids", []):
            if doc_id not in cited_doc_ids:
                failures.append(f"missing_required_citation:{doc_id}")

        for doc_id in expected.get("forbidden_doc_ids", []):
            if doc_id in cited_doc_ids:
                failures.append(f"forbidden_citation_leaked:{doc_id}")

        if expected.get("requires_security_event") and not output["security_events"]:
            failures.append("missing_security_event")

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
                "latency_ms": output["latency_ms"],
            }
        )

    total = len(results)
    passed = sum(1 for item in results if item["passed"])
    unsafe_leaks = sum(
        1 for item in results for failure in item["failures"] if failure.startswith("forbidden_citation_leaked")
    )
    metrics = {
        "total_cases": total,
        "passed_cases": passed,
        "pass_rate": round(passed / total, 3) if total else 0,
        "unsafe_leak_failures": unsafe_leaks,
        "average_latency_ms": round(sum(item["latency_ms"] for item in results) / total, 2) if total else 0,
    }

    run_id = str(uuid.uuid4())
    payload = {"id": run_id, "created_at": utc_now(), "metrics": metrics, "cases": results}
    if persist:
        repo.insert_eval_run(payload)
    return payload


def latest_eval_run(repo: KnowledgeRepository) -> dict | None:
    return repo.latest_eval_run()
