from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class ExpectedClaims:
    project_1_evals: int
    project_2_evals: int
    project_3_evals: int
    smoke_checks: int
    api_contract_checks: int

    @property
    def total_evals(self) -> int:
        return self.project_1_evals + self.project_2_evals + self.project_3_evals


def read_text(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")


def count_eval_cases(rel_path: str) -> int:
    payload = json.loads(read_text(rel_path))
    if not isinstance(payload, list):
        raise ValueError(f"{rel_path} must contain a JSON list")
    return len(payload)


def count_smoke_checks() -> int:
    text = read_text("scripts/smoke_test_demo_flows.py")
    return len(re.findall(r"\bchecks\.append\(", text))


def count_api_contract_checks() -> int:
    text = read_text("scripts/check_api_contracts.py")
    append_count = len(re.findall(r"\bchecks\.append\(", text))
    helper_match = re.search(r"def scenario_contract\(.*?\n\s+return checks", text, flags=re.DOTALL)
    if not helper_match:
        return append_count
    helper_append_count = len(re.findall(r"\bchecks\.append\(", helper_match.group(0)))
    helper_call_count = len(re.findall(r"\bchecks\.extend\(scenario_contract\(", text))
    return append_count - helper_append_count + (helper_append_count * helper_call_count)


def expected_claims() -> ExpectedClaims:
    return ExpectedClaims(
        project_1_evals=count_eval_cases("secure-enterprise-knowledge-copilot/data/eval_cases.json"),
        project_2_evals=count_eval_cases("regulated-customer-operations-agent/data/eval_cases.json"),
        project_3_evals=count_eval_cases("ai-reliability-incident-console/data/eval_cases.json"),
        smoke_checks=count_smoke_checks(),
        api_contract_checks=count_api_contract_checks(),
    )


def require_contains(rel_path: str, expected: str) -> list[str]:
    text = read_text(rel_path)
    if expected not in text:
        return [f"{rel_path}: missing expected claim {expected!r}"]
    return []


def check_expected_absent(rel_path: str, patterns: list[str], expected: ExpectedClaims) -> list[str]:
    text = read_text(rel_path)
    failures = []
    allowed = {
        f"{expected.project_1_evals}/{expected.project_1_evals}",
        f"{expected.project_2_evals}/{expected.project_2_evals}",
        f"{expected.project_3_evals}/{expected.project_3_evals}",
        f"{expected.total_evals}/{expected.total_evals}",
        f"{expected.smoke_checks}/{expected.smoke_checks}",
        f"{expected.api_contract_checks}/{expected.api_contract_checks}",
    }
    for pattern in patterns:
        for match in re.findall(pattern, text):
            ratio = re.search(r"\d+/\d+", match)
            if not ratio or ratio.group(0) not in allowed:
                failures.append(f"{rel_path}: unexpected metric claim {match!r}")
    return failures


def check_demo_report(expected: ExpectedClaims) -> list[str]:
    failures = []
    rel_path = "docs/demo_report.md"
    failures.extend(require_contains(rel_path, "Overall status: **PASS**"))
    failures.extend(
        require_contains(
            rel_path,
            f"secure-enterprise-knowledge-copilot: {expected.project_1_evals}/{expected.project_1_evals} passed",
        )
    )
    failures.extend(
        require_contains(
            rel_path,
            f"regulated-customer-operations-agent: {expected.project_2_evals}/{expected.project_2_evals} passed",
        )
    )
    failures.extend(require_contains(rel_path, "unsafe_leak_failures = 0"))
    failures.extend(require_contains(rel_path, "unsafe_direct_side_effect_failures = 0"))
    failures.extend(require_contains(rel_path, "unsafe_release_approval_failures = 0"))
    failures.extend(require_contains(rel_path, f"Smoke tests: {expected.smoke_checks}/{expected.smoke_checks} passed"))
    return failures


def check_public_claims(expected: ExpectedClaims) -> list[str]:
    failures = []
    expected_strings = {
        "README.md": [
            f"smoke tests: {expected.smoke_checks}/{expected.smoke_checks} passed",
            f"Project 1 eval: {expected.project_1_evals}/{expected.project_1_evals} passed, unsafe_leak_failures = 0",
            f"Project 2 eval: {expected.project_2_evals}/{expected.project_2_evals} passed, unsafe_direct_side_effect_failures = 0",
            f"Project 3 eval: {expected.project_3_evals}/{expected.project_3_evals} passed, unsafe_release_approval_failures = 0",
        ],
        "docs/portfolio_evidence_matrix.md": [
            f"Project 1 eval: {expected.project_1_evals}/{expected.project_1_evals} passed",
            f"Project 2 eval: {expected.project_2_evals}/{expected.project_2_evals} passed",
            f"Project 3 eval: {expected.project_3_evals}/{expected.project_3_evals} passed",
            f"smoke tests: {expected.smoke_checks}/{expected.smoke_checks} passed",
        ],
        "docs/github_release_notes_v0.1.0.md": [
            f"Project 1 evals: {expected.project_1_evals}/{expected.project_1_evals} passed",
            f"Project 2 evals: {expected.project_2_evals}/{expected.project_2_evals} passed",
            f"Project 3 evals: {expected.project_3_evals}/{expected.project_3_evals} passed",
            f"Smoke tests: {expected.smoke_checks}/{expected.smoke_checks} passed",
            f"API contract checks: {expected.api_contract_checks}/{expected.api_contract_checks} passed",
        ],
        "docs/github_repository_settings.md": [
            f"Project 1 evals: {expected.project_1_evals}/{expected.project_1_evals} passed",
            f"Project 2 evals: {expected.project_2_evals}/{expected.project_2_evals} passed",
            f"Project 3 evals: {expected.project_3_evals}/{expected.project_3_evals} passed",
            f"Smoke tests: {expected.smoke_checks}/{expected.smoke_checks} passed",
        ],
        "docs/case_study_secure_enterprise_knowledge_copilot.md": [
            f"{expected.project_1_evals}/{expected.project_1_evals} evals passed",
            "unsafe_leak_failures = 0",
        ],
        "docs/case_study_regulated_customer_operations_agent.md": [
            f"{expected.project_2_evals}/{expected.project_2_evals} evals passed",
            "unsafe_direct_side_effect_failures = 0",
        ],
        "docs/assets/github-preview.svg": [
            f"{expected.smoke_checks}/{expected.smoke_checks} smoke tests",
            f"{expected.total_evals}/{expected.total_evals} evals",
        ],
    }
    for rel_path, claims in expected_strings.items():
        for claim in claims:
            failures.extend(require_contains(rel_path, claim))

    metric_patterns = [
        r"\b\d+/\d+\s+(?:evals|smoke tests|passed)",
    ]
    for rel_path in expected_strings:
        failures.extend(check_expected_absent(rel_path, metric_patterns, expected))
    return failures


def main() -> int:
    expected = expected_claims()
    failures = []
    failures.extend(check_demo_report(expected))
    failures.extend(check_public_claims(expected))

    if failures:
        print("Claim consistency check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(
        "Claim consistency check passed: "
        f"Project 1 {expected.project_1_evals}/{expected.project_1_evals}, "
        f"Project 2 {expected.project_2_evals}/{expected.project_2_evals}, "
        f"Project 3 {expected.project_3_evals}/{expected.project_3_evals}, "
        f"smoke {expected.smoke_checks}/{expected.smoke_checks}, "
        f"total evals {expected.total_evals}/{expected.total_evals}, "
        f"API contracts {expected.api_contract_checks}/{expected.api_contract_checks}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
