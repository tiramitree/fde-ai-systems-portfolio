from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass


EXPECTED_DESCRIPTION = (
    "Three runnable enterprise AI systems showing secure RAG, governed agents, "
    "AI release reliability, evals, traces, audit logs, and approval gates."
)

EXPECTED_TOPICS = {
    "ai-agents",
    "rag",
    "llm-evals",
    "enterprise-ai",
    "forward-deployed-engineering",
    "openai",
    "responses-api",
    "agentic-workflows",
    "tool-calling",
    "human-in-the-loop",
    "ai-safety",
    "python",
}

EXPECTED_RELEASE_TAG = "v0.1.0"


@dataclass
class Check:
    name: str
    status: str
    detail: str


def run_git(args: list[str]) -> tuple[int, str]:
    result = subprocess.run(["git", *args], text=True, capture_output=True)
    return result.returncode, (result.stdout + result.stderr).strip()


def repo_from_remote(remote: str) -> str | None:
    patterns = [
        r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/.]+)(?:\.git)?$",
        r"https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/.]+)(?:\.git)?$",
    ]
    for pattern in patterns:
        match = re.search(pattern, remote)
        if match:
            return f"{match.group('owner')}/{match.group('repo')}"
    return None


def api_get(repo: str, endpoint: str) -> tuple[int, dict | list | None, str]:
    url = f"https://api.github.com/repos/{repo}{endpoint}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "fde-reference-github-readiness",
    }
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(
        url,
        headers=headers,
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status, json.loads(response.read().decode("utf-8")), ""
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return exc.code, None, body or str(exc)
    except urllib.error.URLError as exc:
        return 0, None, str(exc.reason)


def check(ok: bool, name: str, detail: str = "", warn: bool = False) -> Check:
    if ok:
        return Check(name, "PASS", detail)
    return Check(name, "WARN" if warn else "FAIL", detail)


def is_rate_limited(error: str) -> bool:
    return "rate limit" in error.lower()


def is_network_unavailable(error: str) -> bool:
    normalized = error.lower()
    markers = [
        "actively refused",
        "connection refused",
        "connection reset",
        "name resolution",
        "network is unreachable",
        "nodename nor servname",
        "temporary failure",
        "timed out",
        "winerror 10061",
    ]
    return any(marker in normalized for marker in markers)


def tag_exists_via_git(tag: str) -> bool:
    code, output = run_git(["ls-remote", "--tags", "origin", tag])
    return code == 0 and f"refs/tags/{tag}" in output


def remote_main_sha() -> str:
    code, output = run_git(["ls-remote", "--heads", "origin", "main"])
    if code != 0:
        return ""
    for line in output.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1] == "refs/heads/main":
            return parts[0]
    return ""


def transient_github_detail(error: str, action: str) -> str:
    if is_rate_limited(error):
        return f"{action}: GitHub API rate-limited; authenticate with GH_TOKEN, GITHUB_TOKEN, or gh auth login"
    if is_network_unavailable(error):
        return f"{action}: GitHub API unavailable from this environment; rerun during the authenticated publication check"
    return error


def check_main_actions(repo: str, strict: bool) -> Check:
    target_sha = remote_main_sha()
    if target_sha:
        status, check_data, error = api_get(repo, f"/commits/{target_sha}/check-runs")
        if status == 200 and isinstance(check_data, dict):
            runs = [
                run
                for run in check_data.get("check_runs", [])
                if isinstance(run, dict) and run.get("name") == "quality-gate"
            ]
            if runs:
                completed_success = [
                    run
                    for run in runs
                    if run.get("status") == "completed" and run.get("conclusion") == "success"
                ]
                if completed_success:
                    return check(
                        True,
                        "latest main GitHub Actions run passed",
                        completed_success[0].get("html_url", "") or target_sha[:12],
                    )
                pending = [run for run in runs if run.get("status") != "completed"]
                if pending:
                    return check(
                        False,
                        "latest main GitHub Actions run passed",
                        f"quality-gate pending for {target_sha[:12]}",
                        warn=not strict,
                    )
                failed = runs[0]
                return check(
                    False,
                    "latest main GitHub Actions run passed",
                    failed.get("html_url", "") or f"quality-gate {failed.get('conclusion', 'failed')} for {target_sha[:12]}",
                )
            return check(
                False,
                "latest main GitHub Actions run passed",
                f"quality-gate check run not found for {target_sha[:12]}",
                warn=not strict,
            )
        transient_detail = transient_github_detail(error, f"check-runs for {target_sha[:12]}")
        if transient_detail:
            return check(
                False,
                "latest main GitHub Actions run passed",
                transient_detail,
                warn=not strict and (is_rate_limited(error) or is_network_unavailable(error)),
            )

    status, runs_data, error = api_get(repo, "/actions/runs?branch=main&event=push&per_page=10")
    latest_main = None
    if status == 200 and isinstance(runs_data, dict):
        runs = [
            run
            for run in runs_data.get("workflow_runs", [])
            if isinstance(run, dict)
            and run.get("head_branch") == "main"
            and run.get("event") == "push"
            and (not target_sha or run.get("head_sha") == target_sha)
        ]
        latest_main = runs[0] if runs else None
    if latest_main and latest_main.get("status") == "completed" and latest_main.get("conclusion") == "success":
        return check(True, "latest main GitHub Actions run passed", latest_main.get("html_url", ""))
    if latest_main and latest_main.get("status") != "completed":
        return check(
            False,
            "latest main GitHub Actions run passed",
            f"{latest_main.get('html_url', '')} is {latest_main.get('status', 'pending')}",
            warn=not strict,
        )
    detail = latest_main.get("html_url", "") if latest_main else transient_github_detail(error, "workflow runs") or str(status)
    return check(
        False,
        "latest main GitHub Actions run passed",
        detail,
        warn=not strict and (is_rate_limited(error) or is_network_unavailable(error)),
    )


def collect_checks(strict: bool) -> list[Check]:
    checks: list[Check] = []

    code, remote = run_git(["remote", "get-url", "origin"])
    repo = repo_from_remote(remote) if code == 0 else None
    checks.append(check(bool(repo), "origin points to GitHub", remote))
    if not repo:
        return checks

    status, repo_data, error = api_get(repo, "")
    if status != 200 or not isinstance(repo_data, dict):
        rate_limited = is_rate_limited(error)
        network_unavailable = is_network_unavailable(error)
        if rate_limited:
            detail = "API rate-limited; authenticate with GH_TOKEN, GITHUB_TOKEN, or gh auth login"
        elif network_unavailable:
            detail = "GitHub API unavailable from this environment; rerun during the authenticated publication check"
        else:
            detail = error or str(status)
        checks.append(
            check(
                False,
                "GitHub repository metadata reachable",
                detail,
                warn=not strict and (rate_limited or network_unavailable),
            )
        )
        return checks
    checks.append(check(True, "GitHub repository metadata reachable", f"https://github.com/{repo}"))

    checks.append(
        check(
            repo_data.get("description") == EXPECTED_DESCRIPTION,
            "repository description set",
            repo_data.get("description") or "missing",
            warn=not strict,
        )
    )
    topics = set(repo_data.get("topics") or [])
    missing_topics = sorted(EXPECTED_TOPICS - topics)
    checks.append(
        check(
            not missing_topics,
            "repository topics set",
            "ok" if not missing_topics else "missing: " + ", ".join(missing_topics),
            warn=not strict,
        )
    )
    license_info = repo_data.get("license") or {}
    checks.append(check(license_info.get("key") == "mit", "license detected as MIT", license_info.get("key") or "missing"))
    checks.append(check(repo_data.get("default_branch") == "main", "default branch is main", repo_data.get("default_branch") or "missing"))
    status, branch_data, error = api_get(repo, "/branches/main")
    branch_protected = (
        status == 200
        and isinstance(branch_data, dict)
        and branch_data.get("protected") is True
    )
    checks.append(
        check(
            branch_protected,
            "main branch protection enabled",
            "protected" if branch_protected else error or "not protected",
            warn=not strict,
        )
    )
    checks.append(check(True, "stars observed", str(repo_data.get("stargazers_count", 0))))
    checks.append(check(True, "forks observed", str(repo_data.get("forks_count", 0))))

    checks.append(check_main_actions(repo, strict))

    status, issues_data, error = api_get(repo, "/issues?state=open&per_page=100")
    open_issues = [
        issue for issue in (issues_data or [])
        if isinstance(issue, dict) and "pull_request" not in issue
    ] if status == 200 and isinstance(issues_data, list) else []
    checks.append(
        check(
            status == 200 and not open_issues,
            "no open issues",
            "0" if status == 200 and not open_issues else error or str(len(open_issues)),
            warn=not strict,
        )
    )

    status, pulls_data, error = api_get(repo, "/pulls?state=open&per_page=100")
    open_prs = pulls_data if status == 200 and isinstance(pulls_data, list) else []
    checks.append(
        check(
            status == 200 and not open_prs,
            "no open PRs awaiting review",
            "0" if status == 200 and not open_prs else error or str(len(open_prs)),
            warn=not strict,
        )
    )

    status, tag_data, error = api_get(repo, f"/git/ref/tags/{EXPECTED_RELEASE_TAG}")
    tag_exists = status == 200 or tag_exists_via_git(EXPECTED_RELEASE_TAG)
    tag_detail = "ok" if status == 200 else "ok via git" if tag_exists else error or str(status)
    checks.append(
        check(
            tag_exists,
            f"tag {EXPECTED_RELEASE_TAG} exists",
            tag_detail,
            warn=not strict and is_rate_limited(error),
        )
    )

    status, release_data, error = api_get(repo, "/releases/latest")
    release_tag = release_data.get("tag_name") if isinstance(release_data, dict) else None
    checks.append(
        check(
            status == 200 and release_tag == EXPECTED_RELEASE_TAG,
            f"GitHub release page exists for {EXPECTED_RELEASE_TAG}",
            release_tag or error or str(status),
            warn=not strict,
        )
    )

    checks.append(
        Check(
            "social preview configured",
            "MANUAL",
            "GitHub does not expose a simple unauthenticated check; use docs/github_repository_settings.md",
        )
    )
    checks.append(
        Check(
            "profile repository pin configured",
            "MANUAL",
            "Requires account profile settings",
        )
    )
    return checks


def print_checks(checks: list[Check]) -> None:
    for item in checks:
        suffix = f": {item.detail}" if item.detail else ""
        print(f"[{item.status}] {item.name}{suffix}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Report GitHub repository readiness for public launch and engineering review.")
    parser.add_argument("--strict", action="store_true", help="Treat warnings and manual blockers as failures.")
    args = parser.parse_args()

    checks = collect_checks(strict=args.strict)
    print_checks(checks)
    hard_failures = [item for item in checks if item.status == "FAIL"]
    soft_blockers = [item for item in checks if item.status in {"WARN", "MANUAL"}]

    print()
    print(f"Readiness summary: {len(hard_failures)} failure(s), {len(soft_blockers)} warning/manual item(s).")
    if hard_failures or (args.strict and soft_blockers):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
