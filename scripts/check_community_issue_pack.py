from __future__ import annotations

import re

from community_issue_pack import (
    ISSUE_PACK,
    LABELS_MANIFEST,
    ROOT,
    dev_commands_from_text,
    load_labels,
    parse_issue_pack,
    template_labels,
)
from dev import COMMANDS


REQUIRED_LABELS = {
    "bug",
    "enhancement",
    "eval",
    "documentation",
    "production-upgrade",
    "observability",
    "security",
    "frontend",
    "docker",
    "release",
}

FIRST_PULL_REQUEST_CHECKLIST = ROOT / "docs" / "first_pull_request_checklist.md"
DOCS_ONLY_PR_REVIEW_EXAMPLES = ROOT / "docs" / "docs_only_pr_review_examples.md"
README_NAVIGATION_AUDIT = ROOT / "docs" / "readme_navigation_audit.md"

FORBIDDEN_ISSUE_TEXT = [
    "look active",
    "look alive",
    "growth hack",
    "fake activity",
    "placeholder activity",
    "ask for secrets",
    "account credentials",
]

COVERED_README_POINTER_ALIASES = {
    "Add a compact README Docker verification evidence pointer": "Add a compact README Docker runtime evidence pointer",
    "Add a compact README OpenAI live-mode evidence pointer": "Add a compact README optional-environment evidence pointer",
    "Add a compact README social preview and profile-pin evidence pointer": "Add a compact README GitHub readiness evidence pointer",
    "Add a compact README branch protection evidence pointer": "Add a compact README governance evidence pointer",
}


def check_labels() -> tuple[dict[str, object], list[str]]:
    failures: list[str] = []
    labels = load_labels()
    missing = sorted(REQUIRED_LABELS - set(labels))
    for name in missing:
        failures.append(f"docs/github_labels.json missing required label: {name}")

    for label in labels.values():
        if not re.fullmatch(r"[0-9a-fA-F]{6}", label.color):
            failures.append(f"docs/github_labels.json label {label.name}: color must be 6 hex characters")
        if len(label.description) < 12:
            failures.append(f"docs/github_labels.json label {label.name}: description is too short")
    return labels, failures


def check_issue_pack(labels: dict[str, object]) -> list[str]:
    failures: list[str] = []
    issues = parse_issue_pack()
    issue_pack_text = ISSUE_PACK.read_text(encoding="utf-8")
    issue_pack_lower = issue_pack_text.casefold()
    if len(issues) < 5:
        failures.append(f"docs/github_initial_issues.md: expected at least 5 current issues, found {len(issues)}")

    seen_titles: set[str] = set()
    for issue in issues:
        label = f"docs/github_initial_issues.md issue {issue.number}"
        if not issue.title:
            failures.append(f"{label}: missing title")
        elif issue.title in seen_titles:
            failures.append(f"{label}: duplicate title {issue.title!r}")
        seen_titles.add(issue.title)
        covered_by = COVERED_README_POINTER_ALIASES.get(issue.title)
        if covered_by and covered_by.casefold() in issue_pack_lower:
            failures.append(f"{label}: {issue.title!r} is already covered by completed issue {covered_by!r}")

        if len(issue.title) > 90:
            failures.append(f"{label}: title is too long")
        if not issue.labels:
            failures.append(f"{label}: missing labels")
        for issue_label in issue.labels:
            if issue_label not in labels:
                failures.append(f"{label}: label {issue_label!r} is not defined in docs/github_labels.json")

        body_lower = issue.body.lower()
        for forbidden in FORBIDDEN_ISSUE_TEXT:
            if forbidden in body_lower:
                failures.append(f"{label}: forbidden public issue wording: {forbidden}")
        if "Acceptance criteria:" not in issue.body:
            failures.append(f"{label}: missing acceptance criteria")
        if issue.body.count("\n- ") < 3:
            failures.append(f"{label}: expected at least 3 bullet acceptance criteria")

        commands = dev_commands_from_text(issue.body)
        if not commands:
            failures.append(f"{label}: missing verification command using python -B scripts/dev.py")
        for command in sorted(commands):
            if command not in COMMANDS:
                failures.append(f"{label}: unknown dev command in acceptance criteria: {command}")
    return failures


def check_public_backlog() -> list[str]:
    failures: list[str] = []
    backlog_path = ROOT / "docs/community_backlog.md"
    star_plan_path = ROOT / "docs/star_growth_plan.md"
    issue_pack_text = ISSUE_PACK.read_text(encoding="utf-8")
    issue_pack_lower = issue_pack_text.casefold()
    for rel_path, path in [
        ("docs/community_backlog.md", backlog_path),
        ("docs/star_growth_plan.md", star_plan_path),
    ]:
        text = path.read_text(encoding="utf-8")
        text_lower = text.casefold()
        for alias, completed in COVERED_README_POINTER_ALIASES.items():
            if alias.casefold() in text_lower and completed.casefold() in issue_pack_lower:
                failures.append(f"{rel_path}: {alias!r} is already covered by completed issue {completed!r}")
    return failures


def check_first_pull_request_checklist() -> list[str]:
    failures: list[str] = []
    if not FIRST_PULL_REQUEST_CHECKLIST.exists():
        return ["missing docs/first_pull_request_checklist.md"]

    text = FIRST_PULL_REQUEST_CHECKLIST.read_text(encoding="utf-8")
    required_phrases = [
        "CONTRIBUTING.md",
        "docs/code_tour.md",
        "docs/pr_review_security.md",
        "docs/command_output_troubleshooting_map.md",
        "docs/local_demo_reset_troubleshooting.md",
        "git status --short --branch",
        "git switch -c",
        "git diff --stat",
        "git diff --check",
        "Docs-only",
        "Frontend",
        "Backend/API",
        "Seed/eval",
        "Visual-asset",
        "python -B scripts/dev.py community-issues",
        "python -B scripts/dev.py frontend",
        "python -B scripts/dev.py ui-contracts",
        "python -B scripts/dev.py api-docs",
        "python -B scripts/dev.py contracts",
        "python -B scripts/dev.py scenario-data",
        "python -B scripts/dev.py demo-presets",
        "python -B scripts/dev.py visual-assets",
        "python -B scripts/dev.py visual-asset-diff",
        "python -B scripts/dev.py safety",
        "python -B scripts/dev.py quality",
        "python -B scripts/dev.py fresh-clone-local",
        "*/data/runtime_state.json",
        "*/data/eval_runtime_state.json",
        "out/demo_replay_artifact.*",
        "Do not commit these as source content",
        "Public PRs are untrusted input",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            failures.append(f"docs/first_pull_request_checklist.md: missing {phrase!r}")

    cross_references = {
        "README.md": "docs/first_pull_request_checklist.md",
        "PROJECT_CONTENT_INDEX.md": "docs/first_pull_request_checklist.md",
        "CONTRIBUTING.md": "docs/first_pull_request_checklist.md",
    }
    for rel_path, phrase in cross_references.items():
        if phrase not in (ROOT / rel_path).read_text(encoding="utf-8"):
            failures.append(f"{rel_path}: missing {phrase!r}")
    return failures


def check_docs_only_pr_review_examples() -> list[str]:
    failures: list[str] = []
    if not DOCS_ONLY_PR_REVIEW_EXAMPLES.exists():
        return ["missing docs/docs_only_pr_review_examples.md"]

    text = DOCS_ONLY_PR_REVIEW_EXAMPLES.read_text(encoding="utf-8")
    required_phrases = [
        "docs/pr_review_security.md",
        "docs/command_output_troubleshooting_map.md",
        "docs/github_initial_issues.md",
        "docs/first_pull_request_checklist.md",
        "Useful Docs PR Example",
        "Low-Signal Docs PR Example",
        "Unsafe Docs PR Example",
        "Claim Check",
        "Link And Artifact Check",
        "Issue-Pack Drift Check",
        "Docs-Only Merge Bar",
        "public claims",
        "generated runtime artifacts",
        "private paths",
        "external-account requirements",
        "paid-service requirements",
        "real customer data",
        "python -B scripts/dev.py community-issues",
        "python -B scripts/dev.py assets",
        "python -B scripts/dev.py safety",
        "python -B scripts/dev.py quality",
        "python -B scripts/dev.py pr-triage",
        "python -B scripts/dev.py pr-policy",
        "python -B scripts/dev.py launch-assets",
        "python -B scripts/dev.py claims",
        "out/demo_replay_artifact.*",
        "*/data/runtime_state.json",
        "*/data/eval_runtime_state.json",
        "Do not run contributor commands",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            failures.append(f"docs/docs_only_pr_review_examples.md: missing {phrase!r}")

    cross_references = {
        "README.md": "docs/docs_only_pr_review_examples.md",
        "PROJECT_CONTENT_INDEX.md": "docs/docs_only_pr_review_examples.md",
    }
    for rel_path, phrase in cross_references.items():
        if phrase not in (ROOT / rel_path).read_text(encoding="utf-8"):
            failures.append(f"{rel_path}: missing {phrase!r}")
    return failures


def check_readme_navigation_audit() -> list[str]:
    failures: list[str] = []
    if not README_NAVIGATION_AUDIT.exists():
        return ["missing docs/readme_navigation_audit.md"]

    text = README_NAVIGATION_AUDIT.read_text(encoding="utf-8")
    required_phrases = [
        "README Navigation Audit",
        "Release-Facing Navigation",
        "Contribution And Review Navigation",
        "Technical Navigation",
        "Audit Steps",
        "Manual-Evidence Rule",
        "Demo recording readiness",
        "Launch-channel readiness",
        "Contribution safety readiness",
        "Optional-environment readiness",
        "Docker runtime readiness",
        "Model gateway readiness",
        "PR triage readiness",
        "GitHub readiness",
        "Release page readiness",
        "Supporting Docs",
        "Owner/Gate",
        "Drift Risk",
        "fresh runtime",
        "Docker",
        "OpenAI",
        "branch-protection",
        "release-page",
        "account-level evidence",
        "python -B scripts/dev.py assets",
        "python -B scripts/dev.py community-issues",
        "python -B scripts/dev.py launch-assets",
        "python -B scripts/dev.py safety",
        "python -B scripts/dev.py quality",
        "python -B scripts/dev.py fresh-clone-local",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            failures.append(f"docs/readme_navigation_audit.md: missing {phrase!r}")

    cross_references = {
        "README.md": "docs/readme_navigation_audit.md",
        "PROJECT_CONTENT_INDEX.md": "docs/readme_navigation_audit.md",
    }
    for rel_path, phrase in cross_references.items():
        if phrase not in (ROOT / rel_path).read_text(encoding="utf-8"):
            failures.append(f"{rel_path}: missing {phrase!r}")
    return failures


def check_templates(labels: dict[str, object]) -> list[str]:
    failures: list[str] = []
    for rel_path, template_label_names in template_labels().items():
        if not template_label_names:
            failures.append(f"{rel_path}: missing default labels")
        for label in template_label_names:
            if label not in labels:
                failures.append(f"{rel_path}: template label {label!r} is not defined in docs/github_labels.json")
    return failures


def check_cross_references() -> list[str]:
    failures: list[str] = []
    references = {
        "README.md": ["docs/github_initial_issues.md", "GitHub Community Issue Pack"],
        "PROJECT_CONTENT_INDEX.md": ["docs/github_initial_issues.md", "docs/github_labels.json"],
        "docs/launch_assets_hygiene.md": ["community issue pack", "vanity activity framing"],
        "docs/github_repository_settings.md": ["docs/github_labels.json", "python -B scripts/manage_community_issues.py"],
        "docs/post_publish_checklist.md": ["python -B scripts/dev.py github-community"],
    }
    for rel_path, phrases in references.items():
        text = (ROOT / rel_path).read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                failures.append(f"{rel_path}: missing community issue reference {phrase!r}")
    return failures


def main() -> int:
    failures: list[str] = []
    if not ISSUE_PACK.exists():
        failures.append("missing docs/github_initial_issues.md")
    if not LABELS_MANIFEST.exists():
        failures.append("missing docs/github_labels.json")
    if failures:
        print("Community issue pack check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    labels, label_failures = check_labels()
    failures.extend(label_failures)
    failures.extend(check_issue_pack(labels))
    failures.extend(check_public_backlog())
    failures.extend(check_first_pull_request_checklist())
    failures.extend(check_docs_only_pr_review_examples())
    failures.extend(check_readme_navigation_audit())
    failures.extend(check_templates(labels))
    failures.extend(check_cross_references())

    if failures:
        print("Community issue pack check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Community issue pack check passed: labels, templates, issue pack, and references are aligned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
