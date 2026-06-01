from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from check_github_readiness import (
    EXPECTED_DESCRIPTION,
    EXPECTED_RELEASE_TAG,
    EXPECTED_TOPICS,
    repo_from_remote,
)


ROOT = Path(__file__).resolve().parents[1]
RELEASE_NOTES = ROOT / "docs" / "github_release_notes_v0.1.0.md"
RELEASE_TITLE = "FDE AI Systems Portfolio v0.1.0"


def find_gh() -> str | None:
    discovered = shutil.which("gh")
    if discovered:
        return discovered
    candidates = [
        Path("C:/Program Files/GitHub CLI/gh.exe"),
        Path("C:/Program Files (x86)/GitHub CLI/gh.exe"),
        Path.home() / "AppData/Local/Programs/GitHub CLI/gh.exe",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return None


def quote_arg(value: str) -> str:
    if not value:
        return '""'
    if any(char.isspace() for char in value) or any(char in value for char in '"&|<>'):
        return '"' + value.replace('"', '\\"') + '"'
    return value


def display_command(command: list[str]) -> str:
    return " ".join(quote_arg(part) for part in command)


def run_command(command: list[str]) -> int:
    print(f"$ {display_command(command)}")
    result = subprocess.run(command, cwd=ROOT, text=True)
    return result.returncode


def git_output(args: list[str]) -> tuple[int, str]:
    result = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        text=True,
        capture_output=True,
    )
    return result.returncode, (result.stdout + result.stderr).strip()


def get_repo() -> str:
    code, remote = git_output(["remote", "get-url", "origin"])
    if code != 0:
        raise RuntimeError("origin remote is not configured")
    repo = repo_from_remote(remote)
    if not repo:
        raise RuntimeError(f"origin is not a GitHub repository: {remote}")
    return repo


def build_commands(gh: str, repo: str) -> list[list[str]]:
    topics = sorted(EXPECTED_TOPICS)
    repo_edit = [
        gh,
        "repo",
        "edit",
        repo,
        "--description",
        EXPECTED_DESCRIPTION,
        "--enable-issues",
        "--delete-branch-on-merge",
        "--enable-squash-merge",
        "--enable-merge-commit=false",
        "--enable-rebase-merge=false",
    ]
    for topic in topics:
        repo_edit.extend(["--add-topic", topic])

    release = [
        gh,
        "release",
        "create",
        EXPECTED_RELEASE_TAG,
        "--repo",
        repo,
        "--verify-tag",
        "--title",
        RELEASE_TITLE,
        "--notes-file",
        RELEASE_NOTES.relative_to(ROOT).as_posix(),
        "--latest",
    ]
    return [repo_edit, release]


def release_exists(gh: str, repo: str) -> bool:
    result = subprocess.run(
        [gh, "release", "view", EXPECTED_RELEASE_TAG, "--repo", repo],
        cwd=ROOT,
        text=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare GitHub launch metadata. Default mode is a dry-run; use "
            "--apply only after `gh auth login` and reviewing the commands."
        )
    )
    parser.add_argument("--apply", action="store_true", help="Run the GitHub CLI commands.")
    parser.add_argument(
        "--skip-release",
        action="store_true",
        help="Only configure repository metadata and topics.",
    )
    args = parser.parse_args()

    gh = find_gh()
    if not gh:
        print("GitHub CLI not found. Install it with winget install --id GitHub.cli -e --source winget")
        return 1

    if not RELEASE_NOTES.exists():
        print(f"Release notes file is missing: {RELEASE_NOTES.relative_to(ROOT)}")
        return 1

    repo = get_repo()
    commands = build_commands(gh, repo)
    if args.skip_release:
        commands = commands[:1]

    if not args.apply:
        print("Dry run. Review these commands, then run with --apply after `gh auth login`:")
        for command in commands:
            print(display_command(command))
        print()
        print("Manual after --apply:")
        print("- Upload social preview from docs/assets/github-preview.svg or a PNG export.")
        print("- Pin the repository on the GitHub profile.")
        print("- Re-run: python -B scripts/dev.py github-readiness")
        return 0

    auth_status = subprocess.run([gh, "auth", "status"], cwd=ROOT, text=True)
    if auth_status.returncode != 0:
        print("GitHub CLI is not authenticated. Run `gh auth login`, then retry with --apply.")
        return auth_status.returncode

    for index, command in enumerate(commands):
        if index == 1 and release_exists(gh, repo):
            print(f"Release {EXPECTED_RELEASE_TAG} already exists; skipping release creation.")
            continue
        code = run_command(command)
        if code != 0:
            return code

    print()
    print("GitHub launch metadata command(s) completed.")
    print("Manual remaining: social preview upload and profile pin.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
