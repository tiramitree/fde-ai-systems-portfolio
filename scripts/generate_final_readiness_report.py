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
    deferred_metadata = any(
        item.name == "GitHub repository metadata reachable"
        and item.status == "WARN"
        and ("rate-limited" in item.detail or "unavailable" in item.detail)
        for item in checks
    )
    if deferred_metadata:
        dynamic.extend(
            [
                "- repository description, topics, branch protection, release page, social preview, and profile pin still require authenticated verification.",
                "- rerun `python -B scripts/dev.py github-readiness` during the authenticated publication check before claiming GitHub launch completion.",
            ]
        )
    static = [
        "- Docker Compose runtime: not verified on this machine because Docker is not installed; static container release hygiene is gated and `python -B scripts/dev.py docker-runtime` is available for Docker-enabled machines.",
        "- Optional OpenAI live mode: not verified without a valid API key; `python -B scripts/dev.py openai-live` is available for API-key environments.",
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
        "This file is the compact launch and release review status report for the repository.",
        "Regenerate it with `python -B scripts/dev.py readiness-report` after meaningful publication or evidence changes.",
        "",
        "## Executive Status",
        "",
        f"- Overall status: {status}.",
        "- The repository has three runnable enterprise AI systems with evals, traces, approval gates, release gates, API contracts, and public docs.",
        "- The repository is suitable for technical review after the commands below pass.",
        "- Do not claim full launch completion until the manual/account and environment blockers are closed.",
        "",
        "## Local Git Checks",
        "",
        "Before publishing or reviewing from a fresh checkout:",
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
        "Run these from the repository root before sending the project to a reviewer:",
        "",
        "```bash",
        "python -B scripts/dev.py verify",
        "python -B scripts/dev.py fresh-clone-local",
        "python -B scripts/dev.py fresh-clone",
        "python -B scripts/dev.py api-docs",
        "python -B scripts/dev.py replay",
        "python -B scripts/dev.py replay-artifact",
        "python -B scripts/dev.py container-release",
        "python -B scripts/dev.py docker-runtime  # Docker-enabled machines only",
        "python -B scripts/dev.py visual-assets",
        "python -B scripts/dev.py eval-csv",
        "python -B scripts/dev.py community-issues",
        "python -B scripts/dev.py governance",
        "python -B scripts/dev.py launch-assets",
        "python -B scripts/dev.py observability",
        "python -B scripts/dev.py openai-live  # API-key environments only",
        "python -B scripts/dev.py threat-model",
        "python -B scripts/dev.py otel-traces",
        "python -B scripts/dev.py pr-policy",
        "python -B scripts/dev.py pr-triage",
        "python -B scripts/dev.py github-launch-setup",
        "python -B scripts/dev.py github-community",
        "python -B scripts/dev.py github-maintenance",
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
        "python -B scripts/maintain_github_state.py --apply",
        "```",
        "",
        "## Review Walkthrough Order",
        "",
        "1. Start with the README and evidence matrix to frame the three-system repository.",
        "2. Run `python -B scripts/dev.py fresh-clone-local` before pushing, then `python -B scripts/dev.py fresh-clone` after the pushed commit is visible.",
        "3. Run `python -B scripts/dev.py replay` to show the end-to-end demo path without relying on browser state.",
        "4. Run `python -B scripts/dev.py replay-artifact` to generate release-attachable Markdown and JSON evidence under `out/`.",
        "5. Run `python -B scripts/dev.py container-release` to prove Docker/Compose release hygiene without claiming Docker runtime verification.",
        "6. On a Docker-enabled machine, run `python -B scripts/dev.py docker-runtime` before claiming Compose runtime verification.",
        "7. With a live API key, run `python -B scripts/dev.py openai-live` before claiming OpenAI runtime verification.",
        "8. Run `python -B scripts/dev.py visual-assets` to prove desktop and mobile screenshots are tied to current frontend source hashes.",
        "9. Open Project 1 and show permission-aware retrieval, citations, abstention, and prompt-injection handling.",
        "10. Open Project 2 and show investigation, approval queue, supervisor approval, trace, and audit log evidence.",
        "11. Open Project 3 and show failed eval evidence, blocked rollout, remediation steps, trace records, and audit log evidence.",
        "12. Run `python -B scripts/dev.py observability` to prove response trace IDs, audit events, approvals, blocked actions, and release decisions line up.",
        "13. Run `python -B scripts/dev.py threat-model` to show threats map to controls, files, and evidence commands.",
        "14. Run `python -B scripts/dev.py launch-assets` to prove the public launch materials are complete without claiming unfinished external blockers.",
        "15. Run `python -B scripts/dev.py pr-policy` before reviewing external contributions to prove the PR triage policy itself has not been weakened.",
        "16. Run `python -B scripts/dev.py api-docs` and show `docs/api_contracts.md` to map UI behavior to backend endpoints.",
        "17. Show `scripts/check_api_contracts.py`, eval files, and the safety scan to prove this is not only a UI demo.",
        "18. Explain the upgrade path: OpenAI runtime adapters, PostgreSQL/pgvector design, OpenTelemetry export, Docker packaging, approval governance, and release reliability gates.",
        "",
        "## Quality Bar",
        "",
        "- If `verify` fails, fix the failing local behavior before changing docs.",
        "- If `fresh-clone-local` or `fresh-clone` fails, fix clone-path assumptions before sending the repository to reviewers.",
        "- If `replay-artifact` fails, do not attach stale release evidence.",
        "- If `github-readiness --strict` fails only on manual/account settings, do not call the launch complete.",
        "- If `launch-assets` fails, fix public copy and growth docs before publishing launch posts.",
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
