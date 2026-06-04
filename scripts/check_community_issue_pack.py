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
ISSUE_TO_PR_HANDOFF_FLOW = ROOT / "docs" / "issue_to_pr_handoff_flow.md"
EVAL_CSV_TROUBLESHOOTING_EXAMPLES = ROOT / "docs" / "eval_csv_troubleshooting_examples.md"
BRANCH_PROTECTION_VERIFICATION_EXAMPLES = ROOT / "docs" / "branch_protection_verification_examples.md"
POST_PUBLISH_WARNING_EXAMPLES = ROOT / "docs" / "post_publish_warning_examples.md"
GITHUB_AUTHENTICATED_MAINTENANCE_TROUBLESHOOTING_EXAMPLES = ROOT / "docs" / "github_authenticated_maintenance_troubleshooting_examples.md"
GITHUB_PUBLIC_PR_API_FALLBACK_TROUBLESHOOTING_EXAMPLES = ROOT / "docs" / "github_public_pr_api_fallback_troubleshooting_examples.md"
GITHUB_API_RATE_LIMIT_TROUBLESHOOTING_EXAMPLES = ROOT / "docs" / "github_api_rate_limit_troubleshooting_examples.md"
GITHUB_REPOSITORY_METADATA_TROUBLESHOOTING_EXAMPLES = ROOT / "docs" / "github_repository_metadata_troubleshooting_examples.md"
GITHUB_REPOSITORY_SETTINGS_SCREENSHOT_CHECKLIST = ROOT / "docs" / "github_repository_settings_screenshot_checklist.md"
LAUNCH_FEEDBACK_COLLECTION_EXAMPLES = ROOT / "docs" / "launch_feedback_collection_examples.md"
SOCIAL_PREVIEW_VERIFICATION_EXAMPLES = ROOT / "docs" / "social_preview_verification_examples.md"
PROFILE_PIN_VERIFICATION_EXAMPLES = ROOT / "docs" / "profile_pin_verification_examples.md"
GITHUB_ACTIONS_WARNING_EXAMPLES = ROOT / "docs" / "github_actions_warning_examples.md"
GITHUB_LABEL_TROUBLESHOOTING_EXAMPLES = ROOT / "docs" / "github_label_troubleshooting_examples.md"
GITHUB_RELEASE_PAGE_TROUBLESHOOTING_EXAMPLES = ROOT / "docs" / "github_release_page_troubleshooting_examples.md"
GITHUB_LATEST_RELEASE_TROUBLESHOOTING_EXAMPLES = ROOT / "docs" / "github_latest_release_troubleshooting_examples.md"
DOCS_ONLY_PR_REVIEW_EXAMPLES = ROOT / "docs" / "docs_only_pr_review_examples.md"
DOCS_ONLY_REVIEW_COMMENT_EXAMPLES = ROOT / "docs" / "docs_only_review_comment_examples.md"
README_NAVIGATION_AUDIT = ROOT / "docs" / "readme_navigation_audit.md"
README_NAVIGATION_DRIFT_EXAMPLES = ROOT / "docs" / "readme_navigation_drift_examples.md"
OPENTELEMETRY_COLLECTOR_HANDOFF_TROUBLESHOOTING = ROOT / "docs" / "opentelemetry_collector_handoff_troubleshooting.md"
OPENAI_LIVE_MODE_TROUBLESHOOTING = ROOT / "docs" / "openai_live_mode_troubleshooting.md"
DOCKER_RUNTIME_EVIDENCE_CHECKLIST = ROOT / "docs" / "docker_runtime_evidence_checklist.md"
DOCKER_RUNTIME_FAILURE_EXAMPLES = ROOT / "docs" / "docker_runtime_failure_examples.md"

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
        "docs/issue_to_pr_handoff_flow.md",
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


def check_issue_to_pr_handoff_flow() -> list[str]:
    failures: list[str] = []
    if not ISSUE_TO_PR_HANDOFF_FLOW.exists():
        return ["missing docs/issue_to_pr_handoff_flow.md"]

    text = ISSUE_TO_PR_HANDOFF_FLOW.read_text(encoding="utf-8")
    required_phrases = [
        "Issue To PR Handoff Flow",
        "docs/github_initial_issues.md",
        "docs/first_pull_request_checklist.md",
        "docs/docs_only_review_comment_examples.md",
        "docs/pr_review_security.md",
        "Pick One Issue",
        "Create A Small Branch",
        "Keep The Diff Narrow",
        "Review Before Broad Gates",
        "Run The Local Bar",
        "PR Body",
        "Maintainer Review Notes",
        "Done Criteria",
        "Route",
        "Branch Name",
        "python -B scripts/dev.py community-issues",
        "python -B scripts/dev.py assets",
        "python -B scripts/dev.py safety",
        "python -B scripts/dev.py quality",
        "python -B scripts/dev.py fresh-clone-local",
        "generated runtime files",
        "private paths",
        "real customer data",
        "Public PRs are still untrusted input",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            failures.append(f"docs/issue_to_pr_handoff_flow.md: missing {phrase!r}")

    cross_references = {
        "README.md": "docs/issue_to_pr_handoff_flow.md",
        "PROJECT_CONTENT_INDEX.md": "docs/issue_to_pr_handoff_flow.md",
        "CONTRIBUTING.md": "docs/issue_to_pr_handoff_flow.md",
        "docs/first_pull_request_checklist.md": "docs/issue_to_pr_handoff_flow.md",
    }
    for rel_path, phrase in cross_references.items():
        if phrase not in (ROOT / rel_path).read_text(encoding="utf-8"):
            failures.append(f"{rel_path}: missing {phrase!r}")
    return failures


def check_eval_csv_troubleshooting_examples() -> list[str]:
    failures: list[str] = []
    if not EVAL_CSV_TROUBLESHOOTING_EXAMPLES.exists():
        return ["missing docs/eval_csv_troubleshooting_examples.md"]

    text = EVAL_CSV_TROUBLESHOOTING_EXAMPLES.read_text(encoding="utf-8")
    required_phrases = [
        "Eval CSV Troubleshooting Examples",
        "docs/demo_report.md",
        "docs/command_output_troubleshooting_map.md",
        "docs/eval_authoring_guide.md",
        "docs/local_artifact_glossary.md",
        "Expected CSV Output",
        "Missing CSV Output",
        "Stale Eval State",
        "Changed Case IDs",
        "Unsafe Failure Counts",
        "Generated Artifact Handling",
        "Review Checklist",
        "python -B scripts/dev.py eval-csv",
        "python -B scripts/dev.py evals",
        "python -B scripts/dev.py claims",
        "python -B scripts/dev.py safety",
        "eval_summaries.csv",
        "eval_runtime_state.json",
        "runtime_state.json",
        "unsafe_failures",
        "Keep it separate from source content",
        "Do not commit",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            failures.append(f"docs/eval_csv_troubleshooting_examples.md: missing {phrase!r}")

    cross_references = {
        "README.md": "docs/eval_csv_troubleshooting_examples.md",
        "PROJECT_CONTENT_INDEX.md": "docs/eval_csv_troubleshooting_examples.md",
        "docs/eval_authoring_guide.md": "docs/eval_csv_troubleshooting_examples.md",
        "docs/local_artifact_glossary.md": "docs/eval_csv_troubleshooting_examples.md",
    }
    for rel_path, phrase in cross_references.items():
        if phrase not in (ROOT / rel_path).read_text(encoding="utf-8"):
            failures.append(f"{rel_path}: missing {phrase!r}")
    return failures


def check_branch_protection_verification_examples() -> list[str]:
    failures: list[str] = []
    if not BRANCH_PROTECTION_VERIFICATION_EXAMPLES.exists():
        return ["missing docs/branch_protection_verification_examples.md"]

    text = BRANCH_PROTECTION_VERIFICATION_EXAMPLES.read_text(encoding="utf-8")
    required_phrases = [
        "Branch Protection Verification Examples",
        "docs/github_repository_settings.md",
        "docs/github_branch_protection.json",
        "docs/published_repository_status.md",
        "docs/post_publish_checklist.md",
        "Expected Protection Shape",
        "Missing Protection",
        "Stale Payloads",
        "API Warning Rows",
        "Manual Account Settings",
        "Post-Publish Mismatch",
        "Review Checklist",
        "python -B scripts/dev.py governance",
        "python -B scripts/dev.py github-readiness",
        "python -B scripts/check_github_readiness.py --strict",
        "python -B scripts/maintain_github_state.py --apply --skip-release",
        "quality-gate",
        "CODEOWNERS",
        "account-level evidence",
        "remote evidence confirms",
        "not proof that GitHub has applied that policy",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            failures.append(f"docs/branch_protection_verification_examples.md: missing {phrase!r}")

    cross_references = {
        "README.md": "docs/branch_protection_verification_examples.md",
        "PROJECT_CONTENT_INDEX.md": "docs/branch_protection_verification_examples.md",
        "docs/post_publish_checklist.md": "docs/branch_protection_verification_examples.md",
    }
    for rel_path, phrase in cross_references.items():
        if phrase not in (ROOT / rel_path).read_text(encoding="utf-8"):
            failures.append(f"{rel_path}: missing {phrase!r}")
    return failures


def check_post_publish_warning_examples() -> list[str]:
    failures: list[str] = []
    if not POST_PUBLISH_WARNING_EXAMPLES.exists():
        return ["missing docs/post_publish_warning_examples.md"]

    text = POST_PUBLISH_WARNING_EXAMPLES.read_text(encoding="utf-8")
    required_phrases = [
        "Post-Publish Warning Examples",
        "docs/post_publish_checklist.md",
        "docs/published_repository_status.md",
        "docs/github_release_commands.md",
        "docs/github_authenticated_maintenance_troubleshooting_examples.md",
        "docs/github_public_pr_api_fallback_troubleshooting_examples.md",
        "docs/github_api_rate_limit_troubleshooting_examples.md",
        "docs/github_repository_metadata_troubleshooting_examples.md",
        "docs/github_repository_settings_screenshot_checklist.md",
        "docs/launch_feedback_collection_examples.md",
        "docs/social_preview_verification_examples.md",
        "docs/profile_pin_verification_examples.md",
        "docs/command_output_troubleshooting_map.md",
        "Expected Evidence Split",
        "Remote File Lag",
        "Raw README Failures",
        "GitHub Actions Pending State",
        "Readiness Warning Rows",
        "Manual Account Settings",
        "Review Checklist",
        "python -B scripts/dev.py quality",
        "python -B scripts/dev.py fresh-clone-local",
        "python -B scripts/dev.py fresh-clone",
        "python -B scripts/post_publish_check.py",
        "python -B scripts/dev.py github-readiness",
        "python -B scripts/check_github_readiness.py --strict",
        "[WARN]",
        "[MANUAL]",
        "local quality evidence and remote GitHub evidence prove different things",
        "Do not claim published evidence until the remote checks pass",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            failures.append(f"docs/post_publish_warning_examples.md: missing {phrase!r}")

    cross_references = {
        "README.md": "docs/post_publish_warning_examples.md",
        "PROJECT_CONTENT_INDEX.md": "docs/post_publish_warning_examples.md",
        "docs/post_publish_checklist.md": "docs/post_publish_warning_examples.md",
    }
    for rel_path, phrase in cross_references.items():
        if phrase not in (ROOT / rel_path).read_text(encoding="utf-8"):
            failures.append(f"{rel_path}: missing {phrase!r}")
    return failures


def check_github_authenticated_maintenance_troubleshooting_examples() -> list[str]:
    failures: list[str] = []
    if not GITHUB_AUTHENTICATED_MAINTENANCE_TROUBLESHOOTING_EXAMPLES.exists():
        return ["missing docs/github_authenticated_maintenance_troubleshooting_examples.md"]

    text = GITHUB_AUTHENTICATED_MAINTENANCE_TROUBLESHOOTING_EXAMPLES.read_text(encoding="utf-8")
    required_phrases = [
        "GitHub Authenticated Maintenance Troubleshooting Examples",
        "docs/github_repository_settings.md",
        "docs/post_publish_checklist.md",
        "docs/post_publish_warning_examples.md",
        "docs/pr_review_runbook.md",
        "docs/maintainer_review_policy.md",
        "docs/command_output_troubleshooting_map.md",
        "Expected Evidence Split",
        "Missing gh Auth",
        "Wrong Account Or Repository",
        "Dry-Run Versus Apply",
        "Branch Protection Or Release Side Effects",
        "PR Maintenance Safeguards",
        "Review Checklist",
        "python -B scripts/dev.py github-maintenance",
        "python -B scripts/dev.py github-readiness",
        "python -B scripts/maintain_github_state.py --apply",
        "python -B scripts/dev.py pr-triage",
        "python -B scripts/dev.py pr-policy",
        "python -B scripts/dev.py safety",
        "python -B scripts/dev.py quality",
        "python -B scripts/review_open_prs.py --strict",
        "python -B scripts/maintain_github_state.py --apply --skip-release",
        "python -B scripts/maintain_github_state.py --apply --skip-launch --close-runtime-bump-prs",
        "dry-run planning, authenticated account permissions, repository metadata changes, and PR maintenance prove different things",
        "Do not claim remote maintenance applied until authenticated evidence confirms it",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            failures.append(f"docs/github_authenticated_maintenance_troubleshooting_examples.md: missing {phrase!r}")

    cross_references = {
        "README.md": "docs/github_authenticated_maintenance_troubleshooting_examples.md",
        "PROJECT_CONTENT_INDEX.md": "docs/github_authenticated_maintenance_troubleshooting_examples.md",
        "docs/github_repository_settings.md": "docs/github_authenticated_maintenance_troubleshooting_examples.md",
        "docs/post_publish_checklist.md": "docs/github_authenticated_maintenance_troubleshooting_examples.md",
        "docs/post_publish_warning_examples.md": "docs/github_authenticated_maintenance_troubleshooting_examples.md",
        "docs/pr_review_runbook.md": "docs/github_authenticated_maintenance_troubleshooting_examples.md",
        "docs/maintainer_review_policy.md": "github_authenticated_maintenance_troubleshooting_examples.md",
    }
    for rel_path, phrase in cross_references.items():
        if phrase not in (ROOT / rel_path).read_text(encoding="utf-8"):
            failures.append(f"{rel_path}: missing {phrase!r}")
    return failures


def check_github_public_pr_api_fallback_troubleshooting_examples() -> list[str]:
    failures: list[str] = []
    if not GITHUB_PUBLIC_PR_API_FALLBACK_TROUBLESHOOTING_EXAMPLES.exists():
        return ["missing docs/github_public_pr_api_fallback_troubleshooting_examples.md"]

    text = GITHUB_PUBLIC_PR_API_FALLBACK_TROUBLESHOOTING_EXAMPLES.read_text(encoding="utf-8")
    required_phrases = [
        "GitHub Public PR API Fallback Troubleshooting Examples",
        "docs/pr_review_runbook.md",
        "docs/pr_review_security.md",
        "docs/post_publish_warning_examples.md",
        "docs/github_api_rate_limit_troubleshooting_examples.md",
        "docs/maintainer_review_policy.md",
        "docs/command_output_troubleshooting_map.md",
        "Expected Evidence Split",
        "Unauthenticated API Limits",
        "Public Pulls Page Fallback",
        "Missing File-Level Triage",
        "Strict-Mode Review",
        "Stale No-Open-PR State",
        "Review Checklist",
        "python -B scripts/dev.py pr-triage",
        "python -B scripts/review_open_prs.py --strict",
        "python -B scripts/dev.py pr-policy",
        "python -B scripts/dev.py governance",
        "python -B scripts/dev.py workflow-security",
        "python -B scripts/dev.py safety",
        "python -B scripts/dev.py quality",
        "python -B scripts/dev.py github-maintenance",
        "python -B scripts/dev.py github-readiness",
        "public page visibility, API file-level triage, and strict review confidence prove different things",
        "Do not claim no risky PRs until API or authenticated evidence confirms it",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            failures.append(f"docs/github_public_pr_api_fallback_troubleshooting_examples.md: missing {phrase!r}")

    cross_references = {
        "README.md": "docs/github_public_pr_api_fallback_troubleshooting_examples.md",
        "PROJECT_CONTENT_INDEX.md": "docs/github_public_pr_api_fallback_troubleshooting_examples.md",
        "docs/pr_review_runbook.md": "docs/github_public_pr_api_fallback_troubleshooting_examples.md",
        "docs/pr_review_security.md": "docs/github_public_pr_api_fallback_troubleshooting_examples.md",
        "docs/post_publish_checklist.md": "docs/github_public_pr_api_fallback_troubleshooting_examples.md",
        "docs/post_publish_warning_examples.md": "docs/github_public_pr_api_fallback_troubleshooting_examples.md",
        "docs/github_api_rate_limit_troubleshooting_examples.md": "docs/github_public_pr_api_fallback_troubleshooting_examples.md",
        "docs/maintainer_review_policy.md": "github_public_pr_api_fallback_troubleshooting_examples.md",
    }
    for rel_path, phrase in cross_references.items():
        if phrase not in (ROOT / rel_path).read_text(encoding="utf-8"):
            failures.append(f"{rel_path}: missing {phrase!r}")
    return failures


def check_github_api_rate_limit_troubleshooting_examples() -> list[str]:
    failures: list[str] = []
    if not GITHUB_API_RATE_LIMIT_TROUBLESHOOTING_EXAMPLES.exists():
        return ["missing docs/github_api_rate_limit_troubleshooting_examples.md"]

    text = GITHUB_API_RATE_LIMIT_TROUBLESHOOTING_EXAMPLES.read_text(encoding="utf-8")
    required_phrases = [
        "GitHub API Rate-Limit Troubleshooting Examples",
        "docs/published_repository_status.md",
        "docs/post_publish_checklist.md",
        "docs/post_publish_warning_examples.md",
        "docs/github_public_pr_api_fallback_troubleshooting_examples.md",
        "docs/github_actions_warning_examples.md",
        "docs/github_repository_metadata_troubleshooting_examples.md",
        "docs/command_output_troubleshooting_map.md",
        "Expected Evidence Split",
        "Unauthenticated Rate Limits",
        "Transient GitHub API Failures",
        "Pending Actions Lookups",
        "Stale Cached Status",
        "Strict-Mode Review",
        "Review Checklist",
        "python -B scripts/dev.py quality",
        "python -B scripts/dev.py fresh-clone-local",
        "python -B scripts/dev.py fresh-clone",
        "python -B scripts/post_publish_check.py",
        "python -B scripts/dev.py github-readiness",
        "python -B scripts/check_github_readiness.py --strict",
        "python -B scripts/dev.py launch-assets",
        "python -B scripts/dev.py safety",
        "GitHub API availability and local project quality prove different things",
        "Do not claim remote readiness until the readiness command can verify the current repository state",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            failures.append(f"docs/github_api_rate_limit_troubleshooting_examples.md: missing {phrase!r}")

    cross_references = {
        "README.md": "docs/github_api_rate_limit_troubleshooting_examples.md",
        "PROJECT_CONTENT_INDEX.md": "docs/github_api_rate_limit_troubleshooting_examples.md",
        "docs/post_publish_checklist.md": "docs/github_api_rate_limit_troubleshooting_examples.md",
        "docs/post_publish_warning_examples.md": "docs/github_api_rate_limit_troubleshooting_examples.md",
        "docs/github_actions_warning_examples.md": "docs/github_api_rate_limit_troubleshooting_examples.md",
    }
    for rel_path, phrase in cross_references.items():
        if phrase not in (ROOT / rel_path).read_text(encoding="utf-8"):
            failures.append(f"{rel_path}: missing {phrase!r}")
    return failures


def check_github_repository_metadata_troubleshooting_examples() -> list[str]:
    failures: list[str] = []
    if not GITHUB_REPOSITORY_METADATA_TROUBLESHOOTING_EXAMPLES.exists():
        return ["missing docs/github_repository_metadata_troubleshooting_examples.md"]

    text = GITHUB_REPOSITORY_METADATA_TROUBLESHOOTING_EXAMPLES.read_text(encoding="utf-8")
    required_phrases = [
        "GitHub Repository Metadata Troubleshooting Examples",
        "docs/github_repository_settings.md",
        "docs/published_repository_status.md",
        "docs/post_publish_checklist.md",
        "docs/post_publish_warning_examples.md",
        "docs/command_output_troubleshooting_map.md",
        "Expected Evidence Split",
        "Missing Description",
        "Missing Topics",
        "Wrong Repository URL",
        "Stale Public Status",
        "Unauthenticated Maintenance Output",
        "Review Checklist",
        "python -B scripts/dev.py github-readiness",
        "python -B scripts/dev.py github-maintenance",
        "python -B scripts/dev.py launch-assets",
        "python -B scripts/dev.py fresh-clone",
        "python -B scripts/post_publish_check.py",
        "python -B scripts/dev.py safety",
        "python -B scripts/dev.py quality",
        "local launch docs and GitHub account-level repository metadata prove different things",
        "Do not claim metadata is current until GitHub readiness or authenticated maintenance confirms it",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            failures.append(f"docs/github_repository_metadata_troubleshooting_examples.md: missing {phrase!r}")

    cross_references = {
        "README.md": "docs/github_repository_metadata_troubleshooting_examples.md",
        "PROJECT_CONTENT_INDEX.md": "docs/github_repository_metadata_troubleshooting_examples.md",
        "docs/github_repository_settings.md": "docs/github_repository_metadata_troubleshooting_examples.md",
        "docs/post_publish_checklist.md": "docs/github_repository_metadata_troubleshooting_examples.md",
        "docs/post_publish_warning_examples.md": "docs/github_repository_metadata_troubleshooting_examples.md",
    }
    for rel_path, phrase in cross_references.items():
        if phrase not in (ROOT / rel_path).read_text(encoding="utf-8"):
            failures.append(f"{rel_path}: missing {phrase!r}")
    return failures


def check_github_repository_settings_screenshot_checklist() -> list[str]:
    failures: list[str] = []
    if not GITHUB_REPOSITORY_SETTINGS_SCREENSHOT_CHECKLIST.exists():
        return ["missing docs/github_repository_settings_screenshot_checklist.md"]

    text = GITHUB_REPOSITORY_SETTINGS_SCREENSHOT_CHECKLIST.read_text(encoding="utf-8")
    required_phrases = [
        "GitHub Repository Settings Screenshot Checklist",
        "docs/github_repository_settings.md",
        "docs/post_publish_checklist.md",
        "docs/post_publish_warning_examples.md",
        "docs/github_repository_metadata_troubleshooting_examples.md",
        "docs/branch_protection_verification_examples.md",
        "docs/github_release_page_troubleshooting_examples.md",
        "docs/profile_pin_verification_examples.md",
        "docs/social_preview_verification_examples.md",
        "docs/command_output_troubleshooting_map.md",
        "Expected Evidence Split",
        "Description And Topics Screenshots",
        "Branch Protection Screenshots",
        "Social Preview Screenshots",
        "Release Page Screenshots",
        "Profile Pin Screenshots",
        "Screenshot Handling Rules",
        "Review Checklist",
        "python -B scripts/dev.py launch-assets",
        "python -B scripts/dev.py safety",
        "python -B scripts/dev.py quality",
        "python -B scripts/post_publish_check.py",
        "python -B scripts/dev.py github-readiness",
        "python -B scripts/dev.py github-maintenance",
        "local docs, authenticated settings screenshots, and public repository evidence prove different things",
        "Do not commit private account screenshots or claim settings are current until public/account-level evidence confirms them",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            failures.append(f"docs/github_repository_settings_screenshot_checklist.md: missing {phrase!r}")

    cross_references = {
        "README.md": "docs/github_repository_settings_screenshot_checklist.md",
        "PROJECT_CONTENT_INDEX.md": "docs/github_repository_settings_screenshot_checklist.md",
        "docs/github_repository_settings.md": "docs/github_repository_settings_screenshot_checklist.md",
        "docs/post_publish_checklist.md": "docs/github_repository_settings_screenshot_checklist.md",
        "docs/post_publish_warning_examples.md": "docs/github_repository_settings_screenshot_checklist.md",
        "docs/social_preview_verification_examples.md": "docs/github_repository_settings_screenshot_checklist.md",
        "docs/profile_pin_verification_examples.md": "docs/github_repository_settings_screenshot_checklist.md",
    }
    for rel_path, phrase in cross_references.items():
        if phrase not in (ROOT / rel_path).read_text(encoding="utf-8"):
            failures.append(f"{rel_path}: missing {phrase!r}")
    return failures


def check_launch_feedback_collection_examples() -> list[str]:
    failures: list[str] = []
    if not LAUNCH_FEEDBACK_COLLECTION_EXAMPLES.exists():
        return ["missing docs/launch_feedback_collection_examples.md"]

    text = LAUNCH_FEEDBACK_COLLECTION_EXAMPLES.read_text(encoding="utf-8")
    required_phrases = [
        "Launch Feedback Collection Examples",
        "docs/launch_copy_pack.md",
        "docs/star_growth_plan.md",
        "docs/published_repository_status.md",
        "docs/post_publish_checklist.md",
        "docs/post_publish_warning_examples.md",
        "docs/command_output_troubleshooting_map.md",
        "Expected Evidence Split",
        "GitHub Stars And Forks",
        "Issue Feedback",
        "Launch-Post Comments",
        "Private-Message Feedback",
        "Analytics Screenshots",
        "Review Checklist",
        "python -B scripts/dev.py launch-assets",
        "python -B scripts/dev.py safety",
        "python -B scripts/dev.py quality",
        "python -B scripts/dev.py github-readiness",
        "python -B scripts/post_publish_check.py",
        "public feedback, private messages, analytics screenshots, and source evidence prove different things",
        "Do not commit private DMs, account analytics, personal account details, or launch-feedback claims without matching evidence",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            failures.append(f"docs/launch_feedback_collection_examples.md: missing {phrase!r}")

    cross_references = {
        "README.md": "docs/launch_feedback_collection_examples.md",
        "PROJECT_CONTENT_INDEX.md": "docs/launch_feedback_collection_examples.md",
        "docs/launch_copy_pack.md": "docs/launch_feedback_collection_examples.md",
        "docs/star_growth_plan.md": "docs/launch_feedback_collection_examples.md",
        "docs/published_repository_status.md": "docs/launch_feedback_collection_examples.md",
        "docs/post_publish_checklist.md": "docs/launch_feedback_collection_examples.md",
        "docs/post_publish_warning_examples.md": "docs/launch_feedback_collection_examples.md",
    }
    for rel_path, phrase in cross_references.items():
        if phrase not in (ROOT / rel_path).read_text(encoding="utf-8"):
            failures.append(f"{rel_path}: missing {phrase!r}")
    return failures


def check_social_preview_verification_examples() -> list[str]:
    failures: list[str] = []
    if not SOCIAL_PREVIEW_VERIFICATION_EXAMPLES.exists():
        return ["missing docs/social_preview_verification_examples.md"]

    text = SOCIAL_PREVIEW_VERIFICATION_EXAMPLES.read_text(encoding="utf-8")
    required_phrases = [
        "Social Preview Verification Examples",
        "docs/github_repository_settings.md",
        "docs/github_repository_settings_screenshot_checklist.md",
        "docs/assets/github-preview.png",
        "docs/profile_pin_verification_examples.md",
        "docs/post_publish_checklist.md",
        "docs/post_publish_warning_examples.md",
        "docs/command_output_troubleshooting_map.md",
        "Expected Evidence Split",
        "Missing Social Preview",
        "Stale Preview Image",
        "Wrong Uploaded Image",
        "Cache Delay",
        "Profile-Pin Confusion",
        "Review Checklist",
        "python -B scripts/dev.py assets",
        "python -B scripts/dev.py launch-assets",
        "python -B scripts/dev.py github-readiness",
        "python -B scripts/dev.py github-maintenance",
        "python -B scripts/dev.py safety",
        "python -B scripts/dev.py quality",
        "local image asset existence and GitHub account-level social preview setup prove different things",
        "Do not claim social preview setup until the GitHub UI or account-level evidence confirms it",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            failures.append(f"docs/social_preview_verification_examples.md: missing {phrase!r}")

    cross_references = {
        "README.md": "docs/social_preview_verification_examples.md",
        "PROJECT_CONTENT_INDEX.md": "docs/social_preview_verification_examples.md",
        "docs/github_repository_settings.md": "docs/social_preview_verification_examples.md",
        "docs/post_publish_checklist.md": "docs/social_preview_verification_examples.md",
        "docs/post_publish_warning_examples.md": "docs/social_preview_verification_examples.md",
        "docs/profile_pin_verification_examples.md": "docs/social_preview_verification_examples.md",
    }
    for rel_path, phrase in cross_references.items():
        if phrase not in (ROOT / rel_path).read_text(encoding="utf-8"):
            failures.append(f"{rel_path}: missing {phrase!r}")
    return failures


def check_profile_pin_verification_examples() -> list[str]:
    failures: list[str] = []
    if not PROFILE_PIN_VERIFICATION_EXAMPLES.exists():
        return ["missing docs/profile_pin_verification_examples.md"]

    text = PROFILE_PIN_VERIFICATION_EXAMPLES.read_text(encoding="utf-8")
    required_phrases = [
        "GitHub Profile Pin Verification Examples",
        "docs/github_repository_settings.md",
        "docs/github_repository_settings_screenshot_checklist.md",
        "docs/social_preview_verification_examples.md",
        "docs/post_publish_checklist.md",
        "docs/post_publish_warning_examples.md",
        "docs/command_output_troubleshooting_map.md",
        "Expected Evidence Split",
        "Missing Profile Pin",
        "Wrong Pinned Repository",
        "Stale Profile Cache",
        "Social-Preview Confusion",
        "Account Visibility",
        "Review Checklist",
        "python -B scripts/dev.py github-readiness",
        "python -B scripts/dev.py github-maintenance",
        "python -B scripts/dev.py launch-assets",
        "python -B scripts/dev.py safety",
        "python -B scripts/dev.py quality",
        "python -B scripts/post_publish_check.py",
        "repository readiness, social preview setup, and profile pin setup prove different things",
        "Do not claim the profile pin is configured until account-profile evidence confirms it",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            failures.append(f"docs/profile_pin_verification_examples.md: missing {phrase!r}")

    cross_references = {
        "README.md": "docs/profile_pin_verification_examples.md",
        "PROJECT_CONTENT_INDEX.md": "docs/profile_pin_verification_examples.md",
        "docs/github_repository_settings.md": "docs/profile_pin_verification_examples.md",
        "docs/social_preview_verification_examples.md": "docs/profile_pin_verification_examples.md",
        "docs/post_publish_checklist.md": "docs/profile_pin_verification_examples.md",
        "docs/post_publish_warning_examples.md": "docs/profile_pin_verification_examples.md",
    }
    for rel_path, phrase in cross_references.items():
        if phrase not in (ROOT / rel_path).read_text(encoding="utf-8"):
            failures.append(f"{rel_path}: missing {phrase!r}")
    return failures


def check_github_actions_warning_examples() -> list[str]:
    failures: list[str] = []
    if not GITHUB_ACTIONS_WARNING_EXAMPLES.exists():
        return ["missing docs/github_actions_warning_examples.md"]

    text = GITHUB_ACTIONS_WARNING_EXAMPLES.read_text(encoding="utf-8")
    required_phrases = [
        "GitHub Actions Warning Examples",
        ".github/workflows/ci.yml",
        "docs/workflow_security.md",
        "docs/post_publish_checklist.md",
        "docs/post_publish_warning_examples.md",
        "docs/github_api_rate_limit_troubleshooting_examples.md",
        "docs/command_output_troubleshooting_map.md",
        "Expected Actions Evidence",
        "Pending Quality Gate",
        "Missing Workflow Run",
        "Stale Badge",
        "Skipped Workflow",
        "Fork PR Permission Limits",
        "Review Checklist",
        "python -B scripts/dev.py workflow-security",
        "python -B scripts/dev.py quality",
        "python -B scripts/dev.py fresh-clone-local",
        "python -B scripts/dev.py fresh-clone",
        "python -B scripts/post_publish_check.py",
        "python -B scripts/dev.py github-readiness",
        "python -B scripts/check_github_readiness.py --strict",
        "local quality evidence and remote GitHub Actions evidence prove different things",
        "Do not claim a green workflow until the current remote `quality-gate` run passes",
        "permissions remain `contents: read`",
        "persist-credentials: false",
        "does not reference `secrets.*`",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            failures.append(f"docs/github_actions_warning_examples.md: missing {phrase!r}")

    cross_references = {
        "README.md": "docs/github_actions_warning_examples.md",
        "PROJECT_CONTENT_INDEX.md": "docs/github_actions_warning_examples.md",
        "docs/workflow_security.md": "docs/github_actions_warning_examples.md",
        "docs/post_publish_checklist.md": "docs/github_actions_warning_examples.md",
        "docs/post_publish_warning_examples.md": "docs/github_actions_warning_examples.md",
    }
    for rel_path, phrase in cross_references.items():
        if phrase not in (ROOT / rel_path).read_text(encoding="utf-8"):
            failures.append(f"{rel_path}: missing {phrase!r}")
    return failures


def check_github_label_troubleshooting_examples() -> list[str]:
    failures: list[str] = []
    if not GITHUB_LABEL_TROUBLESHOOTING_EXAMPLES.exists():
        return ["missing docs/github_label_troubleshooting_examples.md"]

    text = GITHUB_LABEL_TROUBLESHOOTING_EXAMPLES.read_text(encoding="utf-8")
    required_phrases = [
        "GitHub Label Troubleshooting Examples",
        "docs/github_labels.json",
        "docs/github_initial_issues.md",
        "docs/github_repository_settings.md",
        "docs/post_publish_checklist.md",
        "docs/command_output_troubleshooting_map.md",
        "Expected Label Flow",
        "Missing Labels",
        "Color Drift",
        "Template Mismatch",
        "Dry-Run Output",
        "Issue-Pack Label Mismatch",
        "Review Checklist",
        "python -B scripts/dev.py community-issues",
        "python -B scripts/dev.py github-community",
        "python -B scripts/manage_community_issues.py --apply",
        "python -B scripts/manage_community_issues.py --apply --create-issues",
        "`docs/github_labels.json` is the source of truth",
        "label sync and public roadmap issue creation are separate actions",
        "Public roadmap issues are created only when open issue work is intentionally ready to be visible",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            failures.append(f"docs/github_label_troubleshooting_examples.md: missing {phrase!r}")

    cross_references = {
        "README.md": "docs/github_label_troubleshooting_examples.md",
        "PROJECT_CONTENT_INDEX.md": "docs/github_label_troubleshooting_examples.md",
        "docs/github_repository_settings.md": "docs/github_label_troubleshooting_examples.md",
        "docs/post_publish_checklist.md": "docs/github_label_troubleshooting_examples.md",
    }
    for rel_path, phrase in cross_references.items():
        if phrase not in (ROOT / rel_path).read_text(encoding="utf-8"):
            failures.append(f"{rel_path}: missing {phrase!r}")
    return failures


def check_github_release_page_troubleshooting_examples() -> list[str]:
    failures: list[str] = []
    if not GITHUB_RELEASE_PAGE_TROUBLESHOOTING_EXAMPLES.exists():
        return ["missing docs/github_release_page_troubleshooting_examples.md"]

    text = GITHUB_RELEASE_PAGE_TROUBLESHOOTING_EXAMPLES.read_text(encoding="utf-8")
    required_phrases = [
        "GitHub Release Page Troubleshooting Examples",
        "docs/github_latest_release_troubleshooting_examples.md",
        "docs/github_release_commands.md",
        "docs/github_release_notes_v0.1.0.md",
        "docs/release_attachment_verification_examples.md",
        "docs/post_publish_checklist.md",
        "docs/command_output_troubleshooting_map.md",
        "Expected Release Evidence",
        "Missing Release Page",
        "Wrong Tag",
        "Stale Release Notes",
        "Missing Replay Attachments",
        "Latest-Release Mismatch",
        "Review Checklist",
        "python -B scripts/dev.py replay-artifact",
        "python -B scripts/dev.py launch-assets",
        "python -B scripts/dev.py quality",
        "python -B scripts/dev.py fresh-clone",
        "python -B scripts/post_publish_check.py",
        "python -B scripts/dev.py github-readiness",
        "python -B scripts/dev.py github-maintenance",
        "python -B scripts/maintain_github_state.py --apply",
        "local replay-artifact evidence and published release page evidence prove different things",
        "Do not claim the release page is current until the tag, release notes, and current replay attachments are visible on GitHub",
        "out/demo_replay_artifact.md",
        "out/demo_replay_artifact.json",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            failures.append(f"docs/github_release_page_troubleshooting_examples.md: missing {phrase!r}")

    cross_references = {
        "README.md": "docs/github_release_page_troubleshooting_examples.md",
        "PROJECT_CONTENT_INDEX.md": "docs/github_release_page_troubleshooting_examples.md",
        "docs/release_attachment_verification_examples.md": "docs/github_release_page_troubleshooting_examples.md",
        "docs/post_publish_checklist.md": "docs/github_release_page_troubleshooting_examples.md",
        "docs/github_latest_release_troubleshooting_examples.md": "docs/github_release_page_troubleshooting_examples.md",
    }
    for rel_path, phrase in cross_references.items():
        if phrase not in (ROOT / rel_path).read_text(encoding="utf-8"):
            failures.append(f"{rel_path}: missing {phrase!r}")
    return failures


def check_github_latest_release_troubleshooting_examples() -> list[str]:
    failures: list[str] = []
    if not GITHUB_LATEST_RELEASE_TROUBLESHOOTING_EXAMPLES.exists():
        return ["missing docs/github_latest_release_troubleshooting_examples.md"]

    text = GITHUB_LATEST_RELEASE_TROUBLESHOOTING_EXAMPLES.read_text(encoding="utf-8")
    required_phrases = [
        "GitHub Latest Release Troubleshooting Examples",
        "docs/github_release_page_troubleshooting_examples.md",
        "docs/github_release_commands.md",
        "docs/release_attachment_verification_examples.md",
        "docs/post_publish_checklist.md",
        "docs/post_publish_warning_examples.md",
        "docs/command_output_troubleshooting_map.md",
        "Expected Evidence Split",
        "Missing Latest Release",
        "Wrong Latest Tag",
        "Draft Or Prerelease Confusion",
        "Stale Release Page",
        "Attached Artifact Drift",
        "Review Checklist",
        "python -B scripts/dev.py replay-artifact",
        "python -B scripts/dev.py launch-assets",
        "python -B scripts/dev.py quality",
        "python -B scripts/dev.py fresh-clone",
        "python -B scripts/post_publish_check.py",
        "python -B scripts/dev.py github-readiness",
        "python -B scripts/check_github_readiness.py --strict",
        "tag existence, release-page existence, and latest-release selection prove different things",
        "Do not claim the latest release is current until GitHub readiness or direct release-page evidence confirms it",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            failures.append(f"docs/github_latest_release_troubleshooting_examples.md: missing {phrase!r}")

    cross_references = {
        "README.md": "docs/github_latest_release_troubleshooting_examples.md",
        "PROJECT_CONTENT_INDEX.md": "docs/github_latest_release_troubleshooting_examples.md",
        "docs/github_release_page_troubleshooting_examples.md": "docs/github_latest_release_troubleshooting_examples.md",
        "docs/post_publish_checklist.md": "docs/github_latest_release_troubleshooting_examples.md",
        "docs/post_publish_warning_examples.md": "docs/github_latest_release_troubleshooting_examples.md",
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


def check_docs_only_review_comment_examples() -> list[str]:
    failures: list[str] = []
    if not DOCS_ONLY_REVIEW_COMMENT_EXAMPLES.exists():
        return ["missing docs/docs_only_review_comment_examples.md"]

    text = DOCS_ONLY_REVIEW_COMMENT_EXAMPLES.read_text(encoding="utf-8")
    required_phrases = [
        "docs/docs_only_pr_review_examples.md",
        "docs/pr_review_security.md",
        "docs/first_pull_request_checklist.md",
        "approve",
        "request-changes",
        "close-as-unsafe",
        "close-as-low-signal",
        "Approve",
        "Request Changes: Missing Link Or Evidence",
        "Request Changes: Claim Is Too Broad",
        "Close As Unsafe",
        "Close As Low Signal",
        "Reviewer Checklist Before Posting",
        "Comment Selection Map",
        "python -B scripts/dev.py community-issues",
        "python -B scripts/dev.py assets",
        "python -B scripts/dev.py pr-policy",
        "python -B scripts/dev.py safety",
        "python -B scripts/dev.py quality",
        "generated runtime files",
        "private paths",
        "external accounts",
        "paid-service requirements",
        "real customer data",
        "Do not run contributor commands",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            failures.append(f"docs/docs_only_review_comment_examples.md: missing {phrase!r}")

    cross_references = {
        "README.md": "docs/docs_only_review_comment_examples.md",
        "PROJECT_CONTENT_INDEX.md": "docs/docs_only_review_comment_examples.md",
        "docs/docs_only_pr_review_examples.md": "docs/docs_only_review_comment_examples.md",
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


def check_readme_navigation_drift_examples() -> list[str]:
    failures: list[str] = []
    if not README_NAVIGATION_DRIFT_EXAMPLES.exists():
        return ["missing docs/readme_navigation_drift_examples.md"]

    text = README_NAVIGATION_DRIFT_EXAMPLES.read_text(encoding="utf-8")
    required_phrases = [
        "README Navigation Drift Examples",
        "docs/readme_navigation_audit.md",
        "docs/command_output_troubleshooting_map.md",
        "docs/docs_only_review_comment_examples.md",
        "Stale Link",
        "Unsupported Claim",
        "Missing Source Doc",
        "Manual Evidence Drift",
        "Drift Review Checklist",
        "README.md",
        "PROJECT_CONTENT_INDEX.md",
        "python -B scripts/dev.py assets",
        "python -B scripts/dev.py community-issues",
        "python -B scripts/dev.py launch-assets",
        "python -B scripts/dev.py safety",
        "python -B scripts/dev.py quality",
        "python -B scripts/dev.py fresh-clone-local",
        "generated runtime files",
        "private paths",
        "external accounts",
        "paid-service requirements",
        "real customer data",
        "Do not hide a failing gate",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            failures.append(f"docs/readme_navigation_drift_examples.md: missing {phrase!r}")

    cross_references = {
        "README.md": "docs/readme_navigation_drift_examples.md",
        "PROJECT_CONTENT_INDEX.md": "docs/readme_navigation_drift_examples.md",
        "docs/readme_navigation_audit.md": "docs/readme_navigation_drift_examples.md",
    }
    for rel_path, phrase in cross_references.items():
        if phrase not in (ROOT / rel_path).read_text(encoding="utf-8"):
            failures.append(f"{rel_path}: missing {phrase!r}")
    return failures


def check_opentelemetry_collector_handoff_troubleshooting() -> list[str]:
    failures: list[str] = []
    if not OPENTELEMETRY_COLLECTOR_HANDOFF_TROUBLESHOOTING.exists():
        return ["missing docs/opentelemetry_collector_handoff_troubleshooting.md"]

    text = OPENTELEMETRY_COLLECTOR_HANDOFF_TROUBLESHOOTING.read_text(encoding="utf-8")
    required_phrases = [
        "OpenTelemetry Collector Handoff Troubleshooting",
        "docs/otel_trace_export.md",
        "docs/observability_integrity.md",
        "docs/command_output_troubleshooting_map.md",
        "python -B scripts/dev.py replay",
        "python -B scripts/dev.py otel-traces",
        "python -B scripts/dev.py observability",
        "python -B scripts/dev.py safety",
        "python -B scripts/dev.py quality",
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT",
        "Collector Endpoint Notes",
        "Failure Modes",
        "Rollback",
        "Review Checklist",
        "Claim Wording",
        "hosted collectors",
        "external accounts",
        "paid-service requirements",
        "generated local evidence",
        "Do not claim live collector verification",
        "does not make a hosted collector part of the default demo path",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            failures.append(f"docs/opentelemetry_collector_handoff_troubleshooting.md: missing {phrase!r}")

    cross_references = {
        "README.md": "docs/opentelemetry_collector_handoff_troubleshooting.md",
        "PROJECT_CONTENT_INDEX.md": "docs/opentelemetry_collector_handoff_troubleshooting.md",
        "docs/otel_trace_export.md": "docs/opentelemetry_collector_handoff_troubleshooting.md",
        "docs/observability_integrity.md": "docs/opentelemetry_collector_handoff_troubleshooting.md",
    }
    for rel_path, phrase in cross_references.items():
        if phrase not in (ROOT / rel_path).read_text(encoding="utf-8"):
            failures.append(f"{rel_path}: missing {phrase!r}")
    return failures


def check_openai_live_mode_troubleshooting() -> list[str]:
    failures: list[str] = []
    if not OPENAI_LIVE_MODE_TROUBLESHOOTING.exists():
        return ["missing docs/openai_live_mode_troubleshooting.md"]

    text = OPENAI_LIVE_MODE_TROUBLESHOOTING.read_text(encoding="utf-8")
    required_phrases = [
        "OpenAI Live Mode Troubleshooting",
        "docs/model_runtime_configuration.md",
        "docs/model_gateway_safety.md",
        "docs/command_output_troubleshooting_map.md",
        "python -B scripts/dev.py openai-live",
        "python -B scripts/dev.py model-gateway-safety",
        "python -B scripts/dev.py safety",
        "python -B scripts/dev.py quality",
        "OPENAI_API_KEY",
        "COPILOT_MODEL_PROVIDER",
        "OPS_AGENT_MODEL_ROUTER",
        "local and deterministic",
        "Safe Failure Modes",
        "Rollback",
        "Review Guardrails",
        "never paste API keys",
        "never make OpenAI live mode required",
        "never treat model output as the permission",
        "do not claim live OpenAI evidence unless",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            failures.append(f"docs/openai_live_mode_troubleshooting.md: missing {phrase!r}")

    cross_references = {
        "README.md": "docs/openai_live_mode_troubleshooting.md",
        "PROJECT_CONTENT_INDEX.md": "docs/openai_live_mode_troubleshooting.md",
        "docs/model_runtime_configuration.md": "openai_live_mode_troubleshooting.md",
        "docs/model_gateway_safety.md": "openai_live_mode_troubleshooting.md",
        "docs/readme_navigation_audit.md": "docs/openai_live_mode_troubleshooting.md",
    }
    for rel_path, phrase in cross_references.items():
        if phrase not in (ROOT / rel_path).read_text(encoding="utf-8"):
            failures.append(f"{rel_path}: missing {phrase!r}")
    return failures


def check_docker_runtime_evidence_checklist() -> list[str]:
    failures: list[str] = []
    if not DOCKER_RUNTIME_EVIDENCE_CHECKLIST.exists():
        return ["missing docs/docker_runtime_evidence_checklist.md"]

    text = DOCKER_RUNTIME_EVIDENCE_CHECKLIST.read_text(encoding="utf-8")
    required_phrases = [
        "Docker Runtime Evidence Checklist",
        "docs/container_release_hygiene.md",
        "docs/readme_navigation_audit.md",
        "docs/command_output_troubleshooting_map.md",
        "python -B scripts/dev.py container-release",
        "python -B scripts/dev.py docker-runtime",
        "static config evidence",
        "runtime evidence only on a Docker-enabled machine",
        "Environment Capture",
        "Command Sequence",
        "Expected Evidence",
        "Failure Notes",
        "Review Guardrails",
        "Claim Wording",
        "Docker CLI version output",
        "Docker Compose version output",
        "Smoke tests: 13/13 passed",
        "Docker runtime check passed",
        "Do not claim Docker runtime verification until",
        "Do not commit generated container logs",
        "Do not add required Docker runtime verification to the default",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            failures.append(f"docs/docker_runtime_evidence_checklist.md: missing {phrase!r}")

    cross_references = {
        "README.md": "docs/docker_runtime_evidence_checklist.md",
        "PROJECT_CONTENT_INDEX.md": "docs/docker_runtime_evidence_checklist.md",
        "docs/container_release_hygiene.md": "docker_runtime_evidence_checklist.md",
        "docs/readme_navigation_audit.md": "docs/docker_runtime_evidence_checklist.md",
    }
    for rel_path, phrase in cross_references.items():
        if phrase not in (ROOT / rel_path).read_text(encoding="utf-8"):
            failures.append(f"{rel_path}: missing {phrase!r}")
    return failures


def check_docker_runtime_failure_examples() -> list[str]:
    failures: list[str] = []
    if not DOCKER_RUNTIME_FAILURE_EXAMPLES.exists():
        return ["missing docs/docker_runtime_failure_examples.md"]

    text = DOCKER_RUNTIME_FAILURE_EXAMPLES.read_text(encoding="utf-8")
    required_phrases = [
        "Docker Runtime Failure Examples",
        "docs/docker_runtime_evidence_checklist.md",
        "docs/container_release_hygiene.md",
        "docs/command_output_troubleshooting_map.md",
        "Missing Docker Daemon",
        "Compose Command Mismatch",
        "Unhealthy Service",
        "Stale Generated Logs",
        "Port Conflicts",
        "Merge Bar",
        "Claim Wording",
        "python -B scripts/dev.py container-release",
        "python -B scripts/dev.py docker-runtime",
        "python -B scripts/dev.py safety",
        "python -B scripts/dev.py quality",
        "Docker runtime verification is optional",
        "`python -B scripts/dev.py quality` must not require Docker",
        "Do not claim Docker runtime proof",
        "Do not commit generated container logs",
        "host port(s) already in use",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            failures.append(f"docs/docker_runtime_failure_examples.md: missing {phrase!r}")

    cross_references = {
        "README.md": "docs/docker_runtime_failure_examples.md",
        "PROJECT_CONTENT_INDEX.md": "docs/docker_runtime_failure_examples.md",
        "docs/docker_runtime_evidence_checklist.md": "docs/docker_runtime_failure_examples.md",
        "docs/container_release_hygiene.md": "docker_runtime_failure_examples.md",
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
    failures.extend(check_issue_to_pr_handoff_flow())
    failures.extend(check_eval_csv_troubleshooting_examples())
    failures.extend(check_branch_protection_verification_examples())
    failures.extend(check_post_publish_warning_examples())
    failures.extend(check_github_authenticated_maintenance_troubleshooting_examples())
    failures.extend(check_github_public_pr_api_fallback_troubleshooting_examples())
    failures.extend(check_github_api_rate_limit_troubleshooting_examples())
    failures.extend(check_github_repository_metadata_troubleshooting_examples())
    failures.extend(check_github_repository_settings_screenshot_checklist())
    failures.extend(check_launch_feedback_collection_examples())
    failures.extend(check_social_preview_verification_examples())
    failures.extend(check_profile_pin_verification_examples())
    failures.extend(check_github_actions_warning_examples())
    failures.extend(check_github_label_troubleshooting_examples())
    failures.extend(check_github_release_page_troubleshooting_examples())
    failures.extend(check_github_latest_release_troubleshooting_examples())
    failures.extend(check_docs_only_pr_review_examples())
    failures.extend(check_docs_only_review_comment_examples())
    failures.extend(check_readme_navigation_audit())
    failures.extend(check_readme_navigation_drift_examples())
    failures.extend(check_opentelemetry_collector_handoff_troubleshooting())
    failures.extend(check_openai_live_mode_troubleshooting())
    failures.extend(check_docker_runtime_evidence_checklist())
    failures.extend(check_docker_runtime_failure_examples())
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
