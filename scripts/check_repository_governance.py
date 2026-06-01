from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODEOWNERS = ROOT / ".github" / "CODEOWNERS"
BRANCH_PROTECTION = ROOT / "docs" / "github_branch_protection.json"
PR_TEMPLATE = ROOT / ".github" / "pull_request_template.md"
DEPENDABOT = ROOT / ".github" / "dependabot.yml"


REQUIRED_CODEOWNER_PATTERNS = {
    "*": "@tiramitree",
    ".github/": "@tiramitree",
    ".github/workflows/": "@tiramitree",
    ".github/dependabot.yml": "@tiramitree",
    "scripts/": "@tiramitree",
    "scripts/check_architecture_boundaries.py": "@tiramitree",
    "scripts/public_safety_scan.py": "@tiramitree",
    "scripts/check_dependency_surface.py": "@tiramitree",
    "scripts/check_frontend_integrity.py": "@tiramitree",
    "scripts/check_runtime_ui_contracts.py": "@tiramitree",
    "scripts/quality_gate.py": "@tiramitree",
    "scripts/ci_quality_gate.py": "@tiramitree",
    "scripts/check_github_readiness.py": "@tiramitree",
    "scripts/review_open_prs.py": "@tiramitree",
    "scripts/configure_github_launch.py": "@tiramitree",
    "docs/github_branch_protection.json": "@tiramitree",
    "secure-enterprise-knowledge-copilot/src/copilot/": "@tiramitree",
    "regulated-customer-operations-agent/src/ops_agent/": "@tiramitree",
}


def read_codeowners() -> dict[str, list[str]]:
    entries: dict[str, list[str]] = {}
    for raw_line in CODEOWNERS.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        entries[parts[0]] = parts[1:]
    return entries


def check_codeowners() -> list[str]:
    failures: list[str] = []
    if not CODEOWNERS.exists():
        return ["missing .github/CODEOWNERS"]
    entries = read_codeowners()
    for pattern, owner in REQUIRED_CODEOWNER_PATTERNS.items():
        owners = entries.get(pattern)
        if not owners:
            failures.append(f"missing CODEOWNERS pattern: {pattern}")
        elif owner not in owners:
            failures.append(f"CODEOWNERS pattern {pattern} does not include {owner}")
    return failures


def check_branch_protection() -> list[str]:
    failures: list[str] = []
    if not BRANCH_PROTECTION.exists():
        return ["missing docs/github_branch_protection.json"]
    try:
        payload = json.loads(BRANCH_PROTECTION.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid branch protection JSON: {exc}"]

    status_checks = payload.get("required_status_checks") or {}
    contexts = set(status_checks.get("contexts") or [])
    reviews = payload.get("required_pull_request_reviews") or {}

    expectations = [
        (status_checks.get("strict") is True, "branch protection must require up-to-date branches"),
        ("quality-gate" in contexts, "branch protection must require quality-gate"),
        (payload.get("enforce_admins") is True, "branch protection must enforce admins"),
        (reviews.get("required_approving_review_count", 0) >= 1, "branch protection must require an approving review"),
        (reviews.get("dismiss_stale_reviews") is True, "branch protection must dismiss stale reviews"),
        (reviews.get("require_code_owner_reviews") is True, "branch protection must require code-owner reviews"),
        (reviews.get("require_last_push_approval") is True, "branch protection must require last-push approval"),
        (payload.get("required_conversation_resolution") is True, "branch protection must require conversation resolution"),
        (payload.get("allow_force_pushes") is False, "branch protection must disallow force pushes"),
        (payload.get("allow_deletions") is False, "branch protection must disallow branch deletion"),
    ]
    failures.extend(message for ok, message in expectations if not ok)
    return failures


def check_pr_template() -> list[str]:
    failures: list[str] = []
    if not PR_TEMPLATE.exists():
        return ["missing .github/pull_request_template.md"]
    text = PR_TEMPLATE.read_text(encoding="utf-8")
    required_phrases = [
        "Permission checks are preserved",
        "Approval gates are preserved",
        "No secrets",
        "Dependency surface",
        "Eval or CI failures are not hidden",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            failures.append(f"PR template missing phrase: {phrase}")
    return failures


def check_dependabot() -> list[str]:
    failures: list[str] = []
    if not DEPENDABOT.exists():
        return ["missing .github/dependabot.yml"]
    text = DEPENDABOT.read_text(encoding="utf-8")
    required_phrases = [
        'package-ecosystem: "github-actions"',
        'package-ecosystem: "docker"',
        'directory: "/secure-enterprise-knowledge-copilot"',
        'directory: "/regulated-customer-operations-agent"',
    ]
    for phrase in required_phrases:
        if phrase not in text:
            failures.append(f"Dependabot config missing phrase: {phrase}")
    return failures


def main() -> int:
    failures = []
    failures.extend(check_codeowners())
    failures.extend(check_branch_protection())
    failures.extend(check_pr_template())
    failures.extend(check_dependabot())

    if failures:
        print("Repository governance check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Repository governance check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
