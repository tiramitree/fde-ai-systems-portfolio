from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = ROOT / "docs" / "reviewed_eval_dataset_ledger.json"
NIGHTLY_WORKFLOW = ROOT / ".github" / "workflows" / "nightly-regression.yml"

sys.path.insert(0, str(ROOT / "scripts"))
from export_trace_eval_candidates import REDACTION_POLICY, review_metadata  # noqa: E402


REQUIRED_CATEGORIES = {
    "secure-enterprise-knowledge-copilot": {
        "p1_permission_abstain",
        "p1_prompt_injection_abstain",
        "p1_grounded_citation_answer",
    },
    "regulated-customer-operations-agent": {
        "p2_side_effect_requires_approval",
        "p2_governance_bypass_refusal",
    },
    "ai-reliability-incident-console": {
        "p3_release_block_from_failed_eval",
        "p3_monitor_only_eval_signal",
    },
}

PRIVATE_MARKERS = [
    re.compile(r"[A-Za-z]:\\"),
    re.compile(r"\b" + "g" + r"ho_[A-Za-z0-9_]+\b"),
    re.compile(r"\b" + "s" + r"k-[A-Za-z0-9_-]+\b"),
    re.compile("One" + "Drive", re.IGNORECASE),
    re.compile("wx" + "id_", re.IGNORECASE),
]


def check(condition: bool, name: str, detail: str) -> bool:
    prefix = "[PASS]" if condition else "[FAIL]"
    print(f"{prefix} {name}: {detail}")
    return condition


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def has_private_marker(value: Any) -> bool:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return any(pattern.search(text) for pattern in PRIVATE_MARKERS)


def fixture_case_count(rel_path: str) -> int:
    path = ROOT / rel_path
    payload = load_json(path)
    if not isinstance(payload, list):
        raise ValueError(f"{rel_path} must be a JSON list")
    return len(payload)


def expected_metadata(project: str, categories: set[str]) -> dict[str, Any]:
    category = sorted(categories)[0]
    return review_metadata(project, category, "high")


def workflow_contains_commands(commands: list[str]) -> bool:
    text = NIGHTLY_WORKFLOW.read_text(encoding="utf-8") if NIGHTLY_WORKFLOW.exists() else ""
    return all(command in text for command in commands)


def main() -> int:
    if not LEDGER_PATH.exists():
        print("Reviewed eval ledger check failed: docs/reviewed_eval_dataset_ledger.json is missing.")
        return 1

    ledger = load_json(LEDGER_PATH)
    datasets = ledger.get("datasets", [])
    projects = {item.get("project") for item in datasets}
    required_project_set = set(REQUIRED_CATEGORIES)
    nightly_commands = ledger.get("regression_schedules", {}).get("nightly", {}).get("commands", [])

    checks = [
        check(ledger.get("schema_version") == "reviewed-eval-dataset-ledger-v1", "ledger schema", ledger.get("schema_version", "")),
        check(ledger.get("redaction_policy") == REDACTION_POLICY, "ledger redaction policy", str(ledger.get("redaction_policy"))),
        check(not has_private_marker(ledger), "ledger public-safe content", "no private path/token markers"),
        check(required_project_set.issubset(projects), "ledger project coverage", ", ".join(sorted(str(item) for item in projects))),
        check(NIGHTLY_WORKFLOW.exists(), "nightly regression workflow exists", NIGHTLY_WORKFLOW.relative_to(ROOT).as_posix()),
        check(workflow_contains_commands(nightly_commands), "nightly workflow runs ledger commands", ", ".join(nightly_commands)),
        check("python -B scripts/dev.py reviewed-eval-ledger" in nightly_commands, "nightly includes ledger gate", "reviewed-eval-ledger"),
        check("python -B scripts/dev.py trace-to-eval-check" in nightly_commands, "nightly includes trace-to-eval gate", "trace-to-eval-check"),
    ]

    for dataset in datasets:
        project = str(dataset.get("project", ""))
        categories = set(dataset.get("candidate_categories", []))
        expected_categories = REQUIRED_CATEGORIES.get(project, set())
        metadata = expected_metadata(project, expected_categories) if expected_categories else {}
        fixture = str(dataset.get("fixture", ""))
        expected_count = fixture_case_count(fixture) if fixture else -1
        commands = dataset.get("required_gate_commands", [])

        checks.extend(
            [
                check(categories == expected_categories, f"{project} candidate categories", ", ".join(sorted(categories))),
                check(dataset.get("owner_role") == metadata.get("owner_role"), f"{project} owner role", str(dataset.get("owner_role"))),
                check(dataset.get("fixture") == metadata.get("promotion_target"), f"{project} promotion target", fixture),
                check(dataset.get("case_count") == expected_count, f"{project} case count", f"ledger={dataset.get('case_count')}; fixture={expected_count}"),
                check(dataset.get("review_status") == "active_reviewed_fixture", f"{project} review status", str(dataset.get("review_status"))),
                check(dataset.get("regression_schedule") in {"nightly", "release-gate"}, f"{project} regression schedule", str(dataset.get("regression_schedule"))),
                check("python -B scripts/dev.py quality" in commands, f"{project} quality gate command", ", ".join(commands)),
                check(bool(dataset.get("tracked_invariants")), f"{project} tracked invariants", str(len(dataset.get("tracked_invariants", [])))),
            ]
        )

    passed = sum(1 for item in checks if item)
    print(f"\nReviewed eval ledger checks: {passed}/{len(checks)} passed")
    return 0 if all(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
