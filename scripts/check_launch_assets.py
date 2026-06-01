from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "PROJECT_CONTENT_INDEX.md",
    "docs/launch_assets_hygiene.md",
    "docs/github_launch_plan.md",
    "docs/star_growth_plan.md",
    "docs/launch_copy_pack.md",
    "docs/community_backlog.md",
    "docs/github_initial_issues.md",
    "docs/demo_video_script.md",
    "docs/demo_recording_checklist.md",
    "docs/reviewer_perspective_checklist.md",
    "docs/differentiation_strategy.md",
    "docs/published_repository_status.md",
    "docs/post_publish_checklist.md",
    "docs/github_repository_settings.md",
    "docs/final_readiness_report.md",
    "docs/portfolio_evidence_matrix.md",
]

REQUIRED_SECTIONS = {
    "docs/launch_copy_pack.md": [
        "# Launch Copy Pack",
        "## One-Line Pitch",
        "## Short Post",
        "## LinkedIn Post",
        "## X / Twitter Thread",
        "## Hacker News Show HN",
        "## Reddit / Community Post",
        "## Follow-Up Blog Outline",
    ],
    "docs/star_growth_plan.md": [
        "# Star Growth Plan",
        "## Audience",
        "## Core Message",
        "## Launch Channels",
        "## Content Pieces",
        "## First Issue Labels",
        "## Anti-Hype Rule",
    ],
    "docs/community_backlog.md": [
        "## Good First Issues",
        "## Intermediate Issues",
        "## Advanced Issues",
        "## Guardrails",
    ],
    "docs/github_initial_issues.md": [
        "# GitHub Initial Issues",
        "## Issue 1",
        "## Issue 2",
        "## Issue 3",
        "## Issue 4",
        "## Issue 5",
    ],
    "docs/launch_assets_hygiene.md": [
        "# Launch Assets Hygiene",
        "## What It Checks",
        "## Anti-Hype Boundary",
        "## When To Run",
    ],
}

REQUIRED_PHRASES = {
    "docs/launch_copy_pack.md": [
        "without paid APIs",
        "Optional OpenAI Responses API integration points",
        "the model is not the security boundary",
        "Repo: <repo-url>",
    ],
    "docs/star_growth_plan.md": [
        "GitHub profile pin",
        "LinkedIn technical post",
        "X / Twitter thread",
        "Hacker News Show HN",
        "Reddit communities",
        "Do not claim production readiness",
        "Claim practical reference value",
        "docs/launch_copy_pack.md",
        "python -B scripts/dev.py launch-assets",
    ],
    "docs/community_backlog.md": [
        "Project 1 must not expose inaccessible evidence to the model",
        "Project 2 must not execute side-effect tools without application-level authorization",
        "Eval gates must keep unsafe leak and unsafe direct side-effect failures at zero",
    ],
    "docs/github_initial_issues.md": [
        "Acceptance criteria",
        "python -B scripts/dev.py verify still passes",
    ],
    "README.md": [
        "python -B scripts/dev.py launch-assets",
        "Launch asset hygiene",
        "docs/launch_assets_hygiene.md",
        "docs/star_growth_plan.md",
        "docs/launch_copy_pack.md",
    ],
    "PROJECT_CONTENT_INDEX.md": [
        "launch-assets",
        "scripts/check_launch_assets.py",
        "docs/launch_assets_hygiene.md",
    ],
    "docs/portfolio_evidence_matrix.md": [
        "Launch materials are complete without overclaiming",
        "python -B scripts/dev.py launch-assets",
    ],
    "docs/published_repository_status.md": [
        "Launch asset hygiene: passed",
        "launch copy and star-growth materials",
        "Collect launch feedback and star-growth evidence",
    ],
    "docs/post_publish_checklist.md": [
        "the launch asset hygiene script and documentation are published",
        "python -B scripts/dev.py launch-assets",
    ],
    "docs/final_readiness_report.md": [
        "python -B scripts/dev.py launch-assets",
        "Do not claim full launch completion",
        "Star growth: cannot be claimed as achieved",
    ],
}

PUBLIC_POSITIONING_FILES = [
    "README.md",
    "docs/launch_assets_hygiene.md",
    "docs/launch_copy_pack.md",
    "docs/star_growth_plan.md",
    "docs/github_launch_plan.md",
    "docs/published_repository_status.md",
    "docs/post_publish_checklist.md",
    "docs/final_readiness_report.md",
]

FORBIDDEN_HYPE_PATTERNS = {
    "production-ready claim": re.compile(r"\bproduction[- ]ready\b", re.IGNORECASE),
    "production-grade claim": re.compile(r"\bproduction[- ]grade\b", re.IGNORECASE),
    "completed launch claim": re.compile(r"\b(?:fully\s+)?launch(?:ed)?\s+complete\b", re.IGNORECASE),
    "Docker runtime verified claim": re.compile(r"\bdocker(?: compose)? runtime (?:is )?(?:verified|passed|complete)\b", re.IGNORECASE),
    "OpenAI live verified claim": re.compile(r"\bopenai live(?: mode)? (?:is )?(?:verified|passed|complete)\b", re.IGNORECASE),
    "branch protection enabled claim": re.compile(r"\bbranch protection (?:is )?(?:enabled|complete)\b", re.IGNORECASE),
    "release page created claim": re.compile(r"\brelease page (?:is )?(?:created|published|complete)\b", re.IGNORECASE),
    "star growth achieved claim": re.compile(r"\bstar[- ]growth (?:is )?(?:achieved|complete|proven)\b", re.IGNORECASE),
}

SAFE_CONTEXT_MARKERS = [
    "not verified",
    "before claiming",
    "before claim",
    "do not claim",
    "not claim",
    "cannot be claimed",
    "should not be claimed",
    "still manual",
    "missing",
    "manual",
    "not protected",
    "not yet",
]


def read_text(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")


def require_files() -> list[str]:
    failures = []
    for rel_path in REQUIRED_FILES:
        if not (ROOT / rel_path).exists():
            failures.append(f"missing required launch asset file: {rel_path}")
    return failures


def require_sections() -> list[str]:
    failures = []
    for rel_path, sections in REQUIRED_SECTIONS.items():
        if not (ROOT / rel_path).exists():
            continue
        text = read_text(rel_path)
        for section in sections:
            if section not in text:
                failures.append(f"{rel_path}: missing section {section!r}")
    return failures


def require_phrases() -> list[str]:
    failures = []
    for rel_path, phrases in REQUIRED_PHRASES.items():
        if not (ROOT / rel_path).exists():
            continue
        text = read_text(rel_path)
        for phrase in phrases:
            if phrase not in text:
                failures.append(f"{rel_path}: missing phrase {phrase!r}")
    return failures


def check_issue_pack() -> list[str]:
    rel_path = "docs/github_initial_issues.md"
    if not (ROOT / rel_path).exists():
        return []
    text = read_text(rel_path)
    failures = []
    issue_count = len(re.findall(r"^## Issue \d+\s*$", text, flags=re.MULTILINE))
    acceptance_count = text.count("Acceptance criteria:")
    label_count = text.count("Labels:")
    if issue_count < 5:
        failures.append(f"{rel_path}: expected at least 5 launch issues, found {issue_count}")
    if acceptance_count < issue_count:
        failures.append(f"{rel_path}: every launch issue should include acceptance criteria")
    if label_count < issue_count:
        failures.append(f"{rel_path}: every launch issue should include labels")
    return failures


def check_launch_copy_channels() -> list[str]:
    rel_path = "docs/launch_copy_pack.md"
    if not (ROOT / rel_path).exists():
        return []
    text = read_text(rel_path)
    channels = {
        "LinkedIn": "## LinkedIn Post",
        "X / Twitter": "## X / Twitter Thread",
        "Hacker News": "## Hacker News Show HN",
        "Reddit / Community": "## Reddit / Community Post",
        "blog follow-up": "## Follow-Up Blog Outline",
    }
    failures = []
    for name, marker in channels.items():
        if marker not in text:
            failures.append(f"{rel_path}: missing launch copy channel: {name}")
    if text.count("<repo-url>") < 2:
        failures.append(f"{rel_path}: launch posts should keep explicit <repo-url> placeholders")
    return failures


def check_no_unverified_claims() -> list[str]:
    failures = []
    for rel_path in PUBLIC_POSITIONING_FILES:
        if not (ROOT / rel_path).exists():
            continue
        for line_number, raw_line in enumerate(read_text(rel_path).splitlines(), start=1):
            line = raw_line.strip()
            if not line:
                continue
            lower = line.lower()
            if any(marker in lower for marker in SAFE_CONTEXT_MARKERS):
                continue
            for name, pattern in FORBIDDEN_HYPE_PATTERNS.items():
                if pattern.search(line):
                    failures.append(f"{rel_path}:{line_number}: possible {name}: {line!r}")
    return failures


def main() -> int:
    failures = []
    failures.extend(require_files())
    failures.extend(require_sections())
    failures.extend(require_phrases())
    failures.extend(check_issue_pack())
    failures.extend(check_launch_copy_channels())
    failures.extend(check_no_unverified_claims())

    if failures:
        print("Launch asset hygiene check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Launch asset hygiene check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
