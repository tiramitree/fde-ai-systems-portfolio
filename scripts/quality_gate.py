from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "PROJECT_CONTENT_INDEX.md",
    "CHANGELOG.md",
    ".gitattributes",
    "LICENSE",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "ROADMAP.md",
    "CODE_OF_CONDUCT.md",
    ".github/pull_request_template.md",
    ".github/workflows/ci.yml",
    ".github/ISSUE_TEMPLATE/bug_report.md",
    ".github/ISSUE_TEMPLATE/eval_case.md",
    ".github/ISSUE_TEMPLATE/feature_request.md",
    ".github/ISSUE_TEMPLATE/config.yml",
    "docs/final_demo_runbook.md",
    "docs/demo_report.md",
    "docs/resume_and_interview_package.md",
    "docs/production_upgrade_notes.md",
    "docs/model_runtime_configuration.md",
    "docs/public_release_audit.md",
    "docs/differentiation_strategy.md",
    "docs/hard_interview_playbook.md",
    "docs/system_design_deep_dive.md",
    "docs/portfolio_evidence_matrix.md",
    "docs/adr_0001_local_first_portfolio.md",
    "docs/adr_0002_model_is_not_security_boundary.md",
    "docs/adr_0003_eval_state_isolated_from_demo_state.md",
    "docs/github_repository_settings.md",
    "docs/community_backlog.md",
    "docs/github_initial_issues.md",
    "docs/case_study_secure_enterprise_knowledge_copilot.md",
    "docs/case_study_regulated_customer_operations_agent.md",
    "docs/demo_video_script.md",
    "docs/star_growth_plan.md",
    "docs/reviewer_perspective_checklist.md",
    "docs/github_release_commands.md",
    "docs/assets/github-preview.svg",
    "docs/assets/architecture-overview.svg",
    "docs/assets/secure-knowledge-copilot-screenshot.png",
    "docs/assets/regulated-ops-agent-screenshot.png",
    "scripts/dev.py",
    "secure-enterprise-knowledge-copilot/.dockerignore",
    "secure-enterprise-knowledge-copilot/README.md",
    "regulated-customer-operations-agent/.dockerignore",
    "regulated-customer-operations-agent/README.md",
]

FORBIDDEN_PATTERNS = [
    "sk-",
    "CV_Runze",
    "C:\\NYU",
    "C:\\Users",
    "OneDrive",
    "xwechat",
]

TEXT_EXTENSIONS = {
    ".md",
    ".py",
    ".json",
    ".yml",
    ".yaml",
    ".html",
    ".css",
    ".js",
    ".example",
    ".dockerignore",
    ".gitignore",
    "",
}


def run(args: list[str]) -> tuple[bool, str]:
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    output = (result.stdout + "\n" + result.stderr).strip()
    return result.returncode == 0, output


def check_required_files() -> list[str]:
    failures = []
    for rel_path in REQUIRED_FILES:
        if not (ROOT / rel_path).exists():
            failures.append(f"missing required file: {rel_path}")
    return failures


def check_forbidden_content() -> list[str]:
    failures = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if ".git/" in rel:
            continue
        if path.suffix not in TEXT_EXTENSIONS and path.name not in {".env.example", "Dockerfile", "LICENSE"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in FORBIDDEN_PATTERNS:
            if pattern in text and rel != "scripts/quality_gate.py":
                failures.append(f"forbidden pattern {pattern!r} in {rel}")
    return failures


def check_runtime_artifacts() -> list[str]:
    failures = []
    git_files = tracked_files()
    if git_files is None:
        return failures
    forbidden_names = {
        "runtime_state.json",
        "eval_runtime_state.json",
        "runtime_state.tmp",
        "server.log",
        "server.err.log",
        "server.job.log",
        "write-test.txt",
    }
    forbidden_suffixes = {".pyc", ".sqlite", ".sqlite-journal"}
    for rel in git_files:
        parts = rel.split("/")
        name = parts[-1]
        if "__pycache__" in parts:
            failures.append(f"runtime artifact present: {rel}")
        elif name in forbidden_names:
            failures.append(f"runtime artifact present: {rel}")
        elif any(name.endswith(suffix) for suffix in forbidden_suffixes):
            failures.append(f"runtime artifact present: {rel}")
    return failures


def tracked_files() -> set[str] | None:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files"],
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        return None
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def main() -> int:
    failures = []
    failures.extend(check_required_files())
    failures.extend(check_forbidden_content())
    failures.extend(check_runtime_artifacts())

    command_checks = [
        ("health", [sys.executable, "-B", "scripts/check_health.py"]),
        ("evals", [sys.executable, "-B", "scripts/run_all_evals.py"]),
        ("smoke", [sys.executable, "-B", "scripts/smoke_test_demo_flows.py"]),
        ("report", [sys.executable, "-B", "scripts/generate_demo_report.py"]),
    ]
    for name, command in command_checks:
        ok, output = run(command)
        print(f"\n=== {name} ===")
        print(output)
        if not ok:
            failures.append(f"command failed: {name}")

    if failures:
        print("\nQuality gate failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("\nQuality gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
