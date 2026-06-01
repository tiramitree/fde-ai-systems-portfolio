from __future__ import annotations

import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(args: list[str]) -> tuple[int, str]:
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    return result.returncode, (result.stdout + result.stderr).strip()


def print_check(ok: bool, name: str, detail: str = "") -> bool:
    status = "PASS" if ok else "FAIL"
    suffix = f": {detail}" if detail else ""
    print(f"[{status}] {name}{suffix}")
    return ok


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


def url_exists_once(url: str) -> tuple[bool, str]:
    request = urllib.request.Request(url, headers={"User-Agent": "fde-portfolio-post-publish-check"})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return 200 <= response.status < 400, str(response.status)
    except urllib.error.HTTPError as exc:
        return False, str(exc.code)
    except urllib.error.URLError as exc:
        return False, str(exc.reason)


def url_exists(url: str, attempts: int = 3) -> tuple[bool, str]:
    last_detail = ""
    for attempt in range(1, attempts + 1):
        ok, detail = url_exists_once(url)
        if ok:
            return ok, detail if attempt == 1 else f"{detail} after retry {attempt}"
        last_detail = detail
        if attempt < attempts:
            time.sleep(1)
    return False, last_detail


def main() -> int:
    failures = 0

    code, remote = run(["git", "remote", "get-url", "origin"])
    if not print_check(code == 0 and bool(remote), "origin remote configured", remote):
        return 1

    repo = repo_from_remote(remote)
    if not print_check(repo is not None, "origin points to a GitHub repository", remote):
        return 1

    code, branch = run(["git", "branch", "--show-current"])
    failures += 0 if print_check(code == 0 and branch == "main", "local branch is main", branch) else 1

    code, status = run(["git", "status", "--short"])
    failures += 0 if print_check(code == 0 and not status, "tracked worktree clean") else 1

    code, ls_remote = run(["git", "ls-remote", "--heads", "origin", "main"])
    failures += 0 if print_check(code == 0 and "refs/heads/main" in ls_remote, "remote main branch exists") else 1

    repo_url = f"https://github.com/{repo}"
    ok, detail = url_exists(repo_url)
    failures += 0 if print_check(ok, "GitHub repository page reachable", f"{repo_url} ({detail})") else 1

    raw_readme = f"https://raw.githubusercontent.com/{repo}/main/README.md"
    ok, detail = url_exists(raw_readme)
    failures += 0 if print_check(ok, "raw README reachable", f"{detail}") else 1

    raw_workflow = f"https://raw.githubusercontent.com/{repo}/main/.github/workflows/ci.yml"
    ok, detail = url_exists(raw_workflow)
    failures += 0 if print_check(ok, "GitHub Actions workflow reachable", f"{detail}") else 1

    expected_files = [
        "README.md",
        "PROJECT_CONTENT_INDEX.md",
        "docs/portfolio_evidence_matrix.md",
        "docs/github_branch_protection.json",
        "docs/github_repository_settings.md",
        "docs/github_release_notes_v0.1.0.md",
        "docs/launch_copy_pack.md",
        "docs/postgres_pgvector_adapter_design.md",
        "docs/otel_trace_export.md",
        "docs/final_readiness_report.md",
        "docs/pr_review_runbook.md",
        "docs/assets/demo-walkthrough.gif",
        "scripts/configure_github_launch.py",
        "scripts/review_open_prs.py",
        ".github/workflows/ci.yml",
    ]
    for rel_path in expected_files:
        url = f"https://raw.githubusercontent.com/{repo}/main/{rel_path}"
        ok, detail = url_exists(url)
        failures += 0 if print_check(ok, f"published file: {rel_path}", detail) else 1

    if failures:
        print(f"\nPost-publish check failed with {failures} issue(s).")
        return 1

    print("\nPost-publish check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
