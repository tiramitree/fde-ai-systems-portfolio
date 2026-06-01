from __future__ import annotations

from pathlib import Path

from check_github_readiness import Check, collect_checks


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "docs" / "final_readiness_report.md"


def clean_detail(detail: str) -> str:
    if '"message":"Not Found"' in detail or "status\":\"404" in detail:
        return "missing"
    return detail.replace("|", "\\|") if detail else ""


def display_name(name: str) -> str:
    snapshot_names = {
        "stars observed": "stars observed at generation",
        "forks observed": "forks observed at generation",
        "latest main GitHub Actions run passed": "main GitHub Actions run passed at generation",
    }
    return snapshot_names.get(name, name)


def status_table(checks: list[Check]) -> list[str]:
    lines = [
        "| Check | Status | Detail |",
        "| --- | --- | --- |",
    ]
    for item in checks:
        lines.append(f"| {display_name(item.name)} | {item.status} | {clean_detail(item.detail)} |")
    return lines


def blockers(checks: list[Check]) -> list[str]:
    dynamic = [
        f"- {item.name}: {clean_detail(item.detail)}"
        for item in checks
        if item.status in {"FAIL", "WARN", "MANUAL"}
    ]
    rate_limited = any(
        item.name == "GitHub repository metadata reachable"
        and item.status == "WARN"
        and "rate-limited" in item.detail
        for item in checks
    )
    if rate_limited:
        dynamic.extend(
            [
                "- repository description, topics, branch protection, release page, social preview, and profile pin still require authenticated verification.",
                "- rerun `python -B scripts/dev.py github-readiness` with `GH_TOKEN`, `GITHUB_TOKEN`, or `gh auth login` before claiming GitHub launch completion.",
            ]
        )
    static = [
        "- Docker Compose runtime: not verified on this machine because Docker is not installed.",
        "- Optional OpenAI live mode: not verified without a valid API key.",
        "- Star growth: cannot be claimed as achieved until real launch feedback accumulates.",
    ]
    return dynamic + static


def render() -> str:
    github_checks = collect_checks(strict=False)
    hard_failures = [item for item in github_checks if item.status == "FAIL"]
    soft_blockers = [item for item in github_checks if item.status in {"WARN", "MANUAL"}]

    status = "ready for technical review with manual launch blockers"
    if hard_failures:
        status = "not ready until hard GitHub failures are fixed"
    elif not soft_blockers:
        status = "ready for public launch review"

    lines = [
        "# Final Readiness Report",
        "",
        "This file is the compact launch and interview status report for the portfolio.",
        "Regenerate it with `python -B scripts/dev.py readiness-report` after meaningful publication or evidence changes.",
        "",
        "## Executive Status",
        "",
        f"- Overall status: {status}.",
        "- The portfolio has two runnable enterprise AI systems with evals, traces, approval gates, API contracts, and public docs.",
        "- The repository is suitable for interview walkthroughs after the commands below pass.",
        "- Do not claim full launch completion until the manual/account and environment blockers are closed.",
        "",
        "## Local Git Checks",
        "",
        "Before publishing or interviewing from a fresh checkout:",
        "",
        "```bash",
        "git status --short",
        "git rev-parse --abbrev-ref HEAD",
        "git log -1 --oneline",
        "```",
        "",
        "Expected result: empty status output, branch `main`, and a latest commit that matches the pushed repository.",
        "",
        "## Commands To Prove The Project",
        "",
        "Run these from the repository root before sending the project to an interviewer or reviewer:",
        "",
        "```bash",
        "python -B scripts/dev.py verify",
        "python -B scripts/dev.py fresh-clone",
        "python -B scripts/dev.py api-docs",
        "python -B scripts/dev.py replay",
        "python -B scripts/dev.py replay-artifact",
        "python -B scripts/dev.py eval-csv",
        "python -B scripts/dev.py governance",
        "python -B scripts/dev.py observability",
        "python -B scripts/dev.py threat-model",
        "python -B scripts/dev.py otel-traces",
        "python -B scripts/dev.py pr-policy",
        "python -B scripts/dev.py pr-triage",
        "python -B scripts/dev.py github-launch-setup",
        "python -B scripts/dev.py github-readiness",
        "python -B scripts/post_publish_check.py",
        "```",
        "",
        "Use strict GitHub readiness only when account-level setup is expected to be complete:",
        "",
        "```bash",
        "python -B scripts/check_github_readiness.py --strict",
        "```",
        "",
        "## GitHub Readiness",
        "",
        *status_table(github_checks),
        "",
        "## Remaining Blockers",
        "",
        *blockers(github_checks),
        "",
        "Repository description, topics, branch protection, and the first release can be applied after `gh auth login` with:",
        "",
        "```bash",
        "python -B scripts/configure_github_launch.py --apply",
        "```",
        "",
        "## Interview Walkthrough Order",
        "",
        "1. Start with the README and evidence matrix to frame the two-system portfolio.",
        "2. Run `python -B scripts/dev.py fresh-clone` to prove the public clone path works without hidden local state.",
        "3. Run `python -B scripts/dev.py replay` to show the end-to-end demo path without relying on browser state.",
        "4. Run `python -B scripts/dev.py replay-artifact` to generate release-attachable Markdown and JSON evidence under `out/`.",
        "5. Open Project 1 and show permission-aware retrieval, citations, abstention, and prompt-injection handling.",
        "6. Open Project 2 and show investigation, approval queue, supervisor approval, trace, and audit log evidence.",
        "7. Run `python -B scripts/dev.py observability` to prove response trace IDs, audit events, approvals, and blocked actions line up.",
        "8. Run `python -B scripts/dev.py threat-model` to show threats map to controls, files, and evidence commands.",
        "9. Run `python -B scripts/dev.py pr-policy` before reviewing external contributions to prove the PR triage policy itself has not been weakened.",
        "10. Run `python -B scripts/dev.py api-docs` and show `docs/api_contracts.md` to map UI behavior to backend endpoints.",
        "11. Show `scripts/check_api_contracts.py`, eval files, and the safety scan to prove this is not only a UI demo.",
        "12. Explain the upgrade path: OpenAI runtime adapters, PostgreSQL/pgvector design, OpenTelemetry export, Docker packaging, and approval governance.",
        "",
        "## Quality Bar",
        "",
        "- If `verify` fails, fix the failing local behavior before changing docs.",
        "- If `fresh-clone` fails, fix clone-path assumptions before sending the repository to reviewers.",
        "- If `replay-artifact` fails, do not attach stale release evidence.",
        "- If `github-readiness --strict` fails only on manual/account settings, do not call the launch complete.",
        "- If an external PR appears, run `python -B scripts/dev.py pr-policy` and follow `docs/maintainer_review_policy.md` before merging.",
        "- If generated runtime files appear in Git status, investigate `.gitignore` and the safety scan before publishing.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    REPORT_PATH.write_text(render(), encoding="utf-8")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
