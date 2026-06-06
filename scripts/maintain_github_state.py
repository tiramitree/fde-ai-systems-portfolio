from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from configure_github_launch import display_command, find_gh, get_repo
from review_open_prs import PINNED_PYTHON_IMAGE_PREFIX


ROOT = Path(__file__).resolve().parents[1]

RUNTIME_BUMP_CLOSE_COMMENT = (
    "Closing this automated update because it changes the pinned Python container "
    "runtime baseline. Runtime baseline changes are handled as coordinated release "
    "policy work: update all service Dockerfiles together, update the release "
    "hygiene docs and validation scripts, run the full local quality gate, and "
    "verify Docker runtime behavior on a Docker-enabled machine."
)


@dataclass(frozen=True)
class RuntimeBumpDecision:
    number: int
    title: str
    author: str
    url: str
    filename: str
    target_from: str
    reason: str


def run_command(command: list[str]) -> int:
    print(f"$ {display_command(command)}")
    return subprocess.run(command, cwd=ROOT, text=True).returncode


def gh_json(gh: str, args: list[str]) -> Any:
    result = subprocess.run(
        [gh, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout).strip() or f"gh command failed: {display_command([gh, *args])}")
    return json.loads(result.stdout or "null")


def gh_authenticated(gh: str) -> bool:
    result = subprocess.run(
        [gh, "auth", "status"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def open_pull_requests(gh: str, repo: str) -> list[dict[str, Any]]:
    data = gh_json(gh, ["api", f"repos/{repo}/pulls?state=open&per_page=100"])
    if not isinstance(data, list):
        raise RuntimeError("GitHub API returned a non-list response for open PRs")
    return [item for item in data if isinstance(item, dict)]


def pull_request_files(gh: str, repo: str, number: int) -> list[dict[str, Any]]:
    data = gh_json(gh, ["api", f"repos/{repo}/pulls/{number}/files?per_page=100"])
    if not isinstance(data, list):
        raise RuntimeError(f"GitHub API returned a non-list response for PR #{number} files")
    return [item for item in data if isinstance(item, dict)]


def patch_lines(patch: str | None, marker: str) -> list[str]:
    if not patch:
        return []
    ignored = "+++" if marker == "+" else "---"
    lines: list[str] = []
    for line in patch.splitlines():
        if line.startswith(ignored) or not line.startswith(marker):
            continue
        lines.append(line[1:].strip())
    return lines


def title_matches_runtime_bump(title: str) -> bool:
    lowered = title.lower()
    return "bump python" in lowered and "3.12-slim" in lowered


def runtime_bump_target(patch: str | None) -> str:
    removed = patch_lines(patch, "-")
    added = patch_lines(patch, "+")
    baseline_removed = any(line.startswith(PINNED_PYTHON_IMAGE_PREFIX) for line in removed)
    changed_to = [
        line
        for line in added
        if line.startswith("FROM python:") and not line.startswith(PINNED_PYTHON_IMAGE_PREFIX)
    ]
    if baseline_removed and changed_to:
        return changed_to[0]
    return ""


def runtime_bump_decision(pr: dict[str, Any], files: list[dict[str, Any]]) -> RuntimeBumpDecision | None:
    number = int(pr.get("number") or 0)
    title = str(pr.get("title") or "")
    author = str((pr.get("user") or {}).get("login") or "")
    url = str(pr.get("html_url") or "")

    if author != "dependabot[bot]" or not title_matches_runtime_bump(title):
        return None
    if len(files) != 1:
        return None

    file_info = files[0]
    filename = str(file_info.get("filename") or "")
    if not filename.endswith("Dockerfile"):
        return None

    target = runtime_bump_target(file_info.get("patch"))
    if not target:
        return None

    return RuntimeBumpDecision(
        number=number,
        title=title,
        author=author,
        url=url,
        filename=filename,
        target_from=target,
        reason="Dependabot Dockerfile PR changes the pinned Python runtime baseline.",
    )


def collect_runtime_bump_decisions(gh: str, repo: str) -> list[RuntimeBumpDecision]:
    decisions: list[RuntimeBumpDecision] = []
    for pr in open_pull_requests(gh, repo):
        number = int(pr.get("number") or 0)
        if not number:
            continue
        files = pull_request_files(gh, repo, number)
        decision = runtime_bump_decision(pr, files)
        if decision:
            decisions.append(decision)
    return decisions


def print_decisions(decisions: list[RuntimeBumpDecision]) -> None:
    if not decisions:
        print("No guarded runtime-bump PR closure candidates found.")
        return
    print("Guarded runtime-bump PR closure candidates:")
    for decision in decisions:
        print(f"- PR #{decision.number}: {decision.title}")
        print(f"  author: {decision.author}")
        print(f"  file: {decision.filename}")
        print(f"  target: {decision.target_from}")
        print(f"  url: {decision.url}")
        print(f"  reason: {decision.reason}")


def close_runtime_bump_pr(gh: str, repo: str, decision: RuntimeBumpDecision) -> int:
    comment = [
        gh,
        "api",
        "--method",
        "POST",
        f"repos/{repo}/issues/{decision.number}/comments",
        "-f",
        f"body={RUNTIME_BUMP_CLOSE_COMMENT}",
    ]
    close = [
        gh,
        "api",
        "--method",
        "PATCH",
        f"repos/{repo}/pulls/{decision.number}",
        "-f",
        "state=closed",
    ]
    code = run_command(comment)
    if code != 0:
        return code
    return run_command(close)


def print_dry_run(gh: str, repo: str, args: argparse.Namespace) -> int:
    print("Dry run. Review the authenticated maintenance plan:")
    print(f"Repository: {repo}")
    print()
    print("# Account/auth check")
    print(display_command([gh, "auth", "status"]))

    if not args.skip_launch:
        launch = [sys.executable, "-B", "scripts/configure_github_launch.py", "--apply"]
        launch_display = ["python", "-B", "scripts/configure_github_launch.py", "--apply"]
        if args.skip_release:
            launch.append("--skip-release")
            launch_display.append("--skip-release")
        print()
        print("# Repository metadata, topics, merge policy, branch protection, release setup, and replay artifact upload")
        print(display_command(launch_display))

    print()
    print("# Public PR triage report")
    print(display_command(["python", "-B", "scripts/review_open_prs.py"]))

    if args.close_runtime_bump_prs:
        print()
        print("# Guarded PR closure rule")
        print("Only Dependabot PRs that change exactly one Dockerfile from the pinned Python 3.12 baseline to another Python runtime baseline are eligible.")
        if gh_authenticated(gh):
            try:
                print_decisions(collect_runtime_bump_decisions(gh, repo))
            except RuntimeError as exc:
                print(f"Could not inspect closure candidates through gh: {exc}")
        else:
            print("Exact closure candidates require `gh auth login`; no PR will be closed in dry-run mode.")
    else:
        print()
        print("Guarded runtime-bump PR closure is disabled. Add --close-runtime-bump-prs when applying that policy.")

    print()
    print("# Community labels and issue pack")
    community = ["python", "-B", "scripts/manage_community_issues.py"]
    if args.sync_community:
        community.append("--apply")
    if args.create_community_issues:
        community.append("--create-issues")
    print(display_command(community))
    if not args.sync_community:
        print("Community label sync is disabled. Add --sync-community when applying that policy.")

    print()
    print("After apply, run:")
    print("python -B scripts/dev.py github-readiness")
    print("python -B scripts/dev.py pr-triage")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Dry-run or apply authenticated GitHub repository maintenance actions.",
    )
    parser.add_argument("--apply", action="store_true", help="Run authenticated GitHub maintenance actions.")
    parser.add_argument("--skip-launch", action="store_true", help="Skip repository metadata, protection, and release setup.")
    parser.add_argument("--skip-release", action="store_true", help="Pass --skip-release to launch setup.")
    parser.add_argument(
        "--close-runtime-bump-prs",
        action="store_true",
        help="Close guarded Dependabot Docker runtime-baseline PRs after exact diff matching.",
    )
    parser.add_argument("--sync-community", action="store_true", help="Sync GitHub labels from docs/github_labels.json.")
    parser.add_argument(
        "--create-community-issues",
        action="store_true",
        help="Create missing community issues from docs/github_initial_issues.md. Requires --sync-community when applying.",
    )
    args = parser.parse_args()

    gh = find_gh()
    if not gh:
        print("GitHub CLI not found. Install it with winget install --id GitHub.cli -e --source winget")
        return 1

    repo = get_repo()
    if not args.apply:
        return print_dry_run(gh, repo, args)

    if not gh_authenticated(gh):
        print("GitHub CLI is not authenticated. Run `gh auth login`, then retry with --apply.")
        return 1

    if not args.skip_launch:
        launch = [sys.executable, "-B", "scripts/configure_github_launch.py", "--apply"]
        if args.skip_release:
            launch.append("--skip-release")
        code = run_command(launch)
        if code != 0:
            return code

    if args.close_runtime_bump_prs:
        decisions = collect_runtime_bump_decisions(gh, repo)
        print_decisions(decisions)
        for decision in decisions:
            code = close_runtime_bump_pr(gh, repo, decision)
            if code != 0:
                return code
    else:
        print("Guarded runtime-bump PR closure skipped.")

    if args.create_community_issues and not args.sync_community:
        print("--create-community-issues requires --sync-community so labels exist before issue creation.")
        return 1
    if args.sync_community:
        community = [sys.executable, "-B", "scripts/manage_community_issues.py", "--apply"]
        if args.create_community_issues:
            community.append("--create-issues")
        code = run_command(community)
        if code != 0:
            return code
    else:
        print("Community label sync skipped.")

    print()
    print("Authenticated maintenance completed. Re-run github-readiness and pr-triage.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
