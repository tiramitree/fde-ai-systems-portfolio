from __future__ import annotations

import json
import uuid
from pathlib import Path

from .storage import DATA_DIR, JsonStore, append_eval_run, init_state, utc_now
from .triage import severity_rank, triage_incident


EVAL_CASES_PATH = DATA_DIR / "eval_cases.json"


def run_evals(store: JsonStore, cases_path: Path = EVAL_CASES_PATH) -> dict:
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    results = []

    for case in cases:
        output = triage_incident(
            store,
            case["user_id"],
            case["release_id"],
            case["incident_id"],
        )
        expected = case["expected"]
        decision = output["decision"]
        failures = []

        if expected.get("release_blocked") is not None and decision["release_blocked"] != expected["release_blocked"]:
            failures.append("wrong_release_block_decision")
        if expected.get("minimum_severity") and severity_rank(decision["severity"]) < severity_rank(expected["minimum_severity"]):
            failures.append(f"severity_too_low:{decision['severity']}")
        for eval_case_id in expected.get("must_link_eval_case_ids", []):
            linked = set(output["evidence"]["linked_eval_case_ids"])
            if eval_case_id not in linked:
                failures.append(f"missing_linked_eval:{eval_case_id}")
        for phrase in expected.get("must_recommend_phrases", []):
            if not any(phrase.lower() in step.lower() for step in output["remediation_steps"]):
                failures.append(f"missing_recommendation:{phrase}")

        results.append(
            {
                "id": case["id"],
                "passed": not failures,
                "failures": failures,
                "trace_id": output["trace_id"],
                "release_blocked": decision["release_blocked"],
                "severity": decision["severity"],
                "linked_eval_case_ids": output["evidence"]["linked_eval_case_ids"],
            }
        )

    total = len(results)
    passed = sum(1 for item in results if item["passed"])
    metrics = {
        "total_cases": total,
        "passed_cases": passed,
        "pass_rate": round(passed / total, 3) if total else 0,
        "unsafe_release_approval_failures": sum(
            1
            for result in results
            for failure in result["failures"]
            if failure == "wrong_release_block_decision"
        ),
    }
    run = {
        "id": str(uuid.uuid4()),
        "created_at": utc_now(),
        "release_id": "rel-2026-06-01",
        "metrics": metrics,
        "cases": results,
    }
    append_eval_run(store, run)
    return run


def run_evals_from_fresh_state() -> dict:
    init_state(reset=True)
    with JsonStore() as store:
        return run_evals(store)
