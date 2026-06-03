from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.parse
from pathlib import Path
from typing import Any

from community_issue_pack import CommunityIssue, Label, load_labels, parse_issue_pack
from configure_github_launch import display_command, find_gh, get_repo


ROOT = Path(__file__).resolve().parents[1]


def run_command(command: list[str], display: list[str] | None = None) -> int:
    print(f"$ {display_command(display or command)}")
    return subprocess.run(command, cwd=ROOT, text=True).returncode


def gh_json(gh: str, args: list[str]) -> tuple[int, Any, str]:
    result = subprocess.run([gh, *args], cwd=ROOT, text=True, capture_output=True)
    output = (result.stdout or "").strip()
    if result.returncode != 0:
        return result.returncode, None, (result.stderr or result.stdout).strip()
    if not output:
        return result.returncode, None, ""
    try:
        return result.returncode, json.loads(output), ""
    except json.JSONDecodeError as exc:
        return result.returncode, None, str(exc)


def gh_authenticated(gh: str) -> bool:
    result = subprocess.run(
        [gh, "auth", "status"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def label_create_command(gh: str, repo: str, label: Label) -> list[str]:
    return [
        gh,
        "api",
        "--method",
        "POST",
        f"repos/{repo}/labels",
        "-f",
        f"name={label.name}",
        "-f",
        f"color={label.color}",
        "-f",
        f"description={label.description}",
    ]


def label_update_command(gh: str, repo: str, label: Label) -> list[str]:
    encoded = urllib.parse.quote(label.name, safe="")
    return [
        gh,
        "api",
        "--method",
        "PATCH",
        f"repos/{repo}/labels/{encoded}",
        "-f",
        f"new_name={label.name}",
        "-f",
        f"color={label.color}",
        "-f",
        f"description={label.description}",
    ]


def sync_labels(gh: str, repo: str, labels: dict[str, Label]) -> int:
    for label in labels.values():
        encoded = urllib.parse.quote(label.name, safe="")
        code, _, _ = gh_json(gh, ["api", f"repos/{repo}/labels/{encoded}"])
        command = label_update_command(gh, repo, label) if code == 0 else label_create_command(gh, repo, label)
        result = run_command(command)
        if result != 0:
            return result
    return 0


def existing_issue_titles(gh: str, repo: str) -> set[str]:
    titles: set[str] = set()
    page = 1
    while True:
        code, data, error = gh_json(gh, ["api", f"repos/{repo}/issues?state=all&per_page=100&page={page}"])
        if code != 0:
            raise RuntimeError(error or f"could not list issues page {page}")
        if not isinstance(data, list):
            raise RuntimeError("GitHub API returned non-list issue data")
        for item in data:
            if not isinstance(item, dict) or "pull_request" in item:
                continue
            title = str(item.get("title") or "")
            if title:
                titles.add(title)
        if len(data) < 100:
            return titles
        page += 1


def issue_create_command(gh: str, repo: str, issue: CommunityIssue) -> list[str]:
    command = [
        gh,
        "issue",
        "create",
        "--repo",
        repo,
        "--title",
        issue.title,
        "--body",
        issue.body,
    ]
    for label in issue.labels:
        command.extend(["--label", label])
    return command


def issue_create_display(gh: str, repo: str, issue: CommunityIssue) -> list[str]:
    command = [
        gh,
        "issue",
        "create",
        "--repo",
        repo,
        "--title",
        issue.title,
        "--body",
        "<body from docs/github_initial_issues.md>",
    ]
    for label in issue.labels:
        command.extend(["--label", label])
    return command


def create_issues(gh: str, repo: str, issues: list[CommunityIssue]) -> int:
    existing = existing_issue_titles(gh, repo)
    for issue in issues:
        if issue.title in existing:
            print(f"Skipping existing issue title: {issue.title}")
            continue
        result = run_command(issue_create_command(gh, repo, issue), issue_create_display(gh, repo, issue))
        if result != 0:
            return result
    return 0


def print_dry_run(gh: str, repo: str, labels: dict[str, Label], issues: list[CommunityIssue], create_issues_enabled: bool) -> int:
    print("Dry run. Review the community GitHub maintenance plan:")
    print(f"Repository: {repo}")
    print()
    print("# Account/auth check")
    print(display_command([gh, "auth", "status"]))
    print()
    print("# Label sync")
    for label in labels.values():
        print(display_command([gh, "label", "create", label.name, "--color", label.color, "--description", label.description, "--force"]))
    print()
    if create_issues_enabled:
        print("# Community issue creation")
        if gh_authenticated(gh):
            try:
                existing = existing_issue_titles(gh, repo)
            except RuntimeError as exc:
                print(f"Could not inspect existing issues through gh: {exc}")
                existing = set()
        else:
            print("Existing issue detection requires `gh auth login`; dry-run will list all candidate issues.")
            existing = set()
        for issue in issues:
            prefix = "# skip existing" if issue.title in existing else "# create"
            print(f"{prefix}: {issue.title}")
            print(display_command(issue_create_display(gh, repo, issue)))
    else:
        print("Community issue creation is disabled. Add --create-issues when applying that policy.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Dry-run or apply GitHub labels and optional community issue creation.",
    )
    parser.add_argument("--apply", action="store_true", help="Run authenticated GitHub community maintenance actions.")
    parser.add_argument("--create-issues", action="store_true", help="Create missing community issues from docs/github_initial_issues.md.")
    args = parser.parse_args()

    gh = find_gh()
    if not gh:
        print("GitHub CLI not found. Install it with winget install --id GitHub.cli -e --source winget")
        return 1

    repo = get_repo()
    labels = load_labels()
    issues = parse_issue_pack()
    if not args.apply:
        return print_dry_run(gh, repo, labels, issues, args.create_issues)

    if not gh_authenticated(gh):
        print("GitHub CLI is not authenticated. Run `gh auth login`, then retry with --apply.")
        return 1

    code = sync_labels(gh, repo, labels)
    if code != 0:
        return code
    if args.create_issues:
        code = create_issues(gh, repo, issues)
        if code != 0:
            return code
    else:
        print("Community issue creation skipped.")

    print("Community GitHub maintenance completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
