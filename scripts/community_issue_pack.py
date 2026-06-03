from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ISSUE_PACK = ROOT / "docs" / "github_initial_issues.md"
LABELS_MANIFEST = ROOT / "docs" / "github_labels.json"
ISSUE_TEMPLATE_DIR = ROOT / ".github" / "ISSUE_TEMPLATE"


@dataclass(frozen=True)
class Label:
    name: str
    color: str
    description: str


@dataclass(frozen=True)
class CommunityIssue:
    number: int
    title: str
    labels: tuple[str, ...]
    body: str


def load_labels(path: Path = LABELS_MANIFEST) -> dict[str, Label]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError("labels manifest must be a JSON list")
    labels: dict[str, Label] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("each label row must be a JSON object")
        name = str(row.get("name", "")).strip()
        color = str(row.get("color", "")).strip()
        description = str(row.get("description", "")).strip()
        if not name:
            raise ValueError("label is missing name")
        if name in labels:
            raise ValueError(f"duplicate label: {name}")
        labels[name] = Label(name=name, color=color, description=description)
    return labels


def fenced_block_after(section: str, marker: str) -> str:
    marker_index = section.find(marker)
    if marker_index == -1:
        return ""
    match = re.search(r"```text\s*\n(.*?)\n```", section[marker_index:], flags=re.DOTALL)
    return match.group(1).strip() if match else ""


def parse_issue_pack(path: Path = ISSUE_PACK) -> list[CommunityIssue]:
    text = path.read_text(encoding="utf-8")
    headings = list(re.finditer(r"^## Issue (?P<number>\d+)\s*$", text, flags=re.MULTILINE))
    issues: list[CommunityIssue] = []
    for index, heading in enumerate(headings):
        start = heading.end()
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        section = text[start:end]
        title = fenced_block_after(section, "Title:")
        labels_raw = fenced_block_after(section, "Labels:")
        body = fenced_block_after(section, "Body:")
        labels = tuple(label.strip() for label in labels_raw.split(",") if label.strip())
        issues.append(
            CommunityIssue(
                number=int(heading.group("number")),
                title=title,
                labels=labels,
                body=body,
            )
        )
    return issues


def template_labels(template_dir: Path = ISSUE_TEMPLATE_DIR) -> dict[str, set[str]]:
    labels_by_file: dict[str, set[str]] = {}
    for path in sorted(template_dir.glob("*.md")):
        labels: set[str] = set()
        in_frontmatter = False
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped == "---":
                if not in_frontmatter:
                    in_frontmatter = True
                    continue
                break
            if in_frontmatter and stripped.startswith("labels:"):
                raw = stripped.split(":", 1)[1].strip().strip('"')
                labels.update(label.strip() for label in raw.split(",") if label.strip())
        labels_by_file[path.relative_to(ROOT).as_posix()] = labels
    return labels_by_file


def dev_commands_from_text(text: str) -> set[str]:
    return set(re.findall(r"python\s+-B\s+scripts/dev\.py\s+([a-z0-9-]+)", text))
