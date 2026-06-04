from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]

LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
IMAGE_SUFFIXES = {".gif", ".png", ".svg"}
REQUIRED_IMAGE_SIZES = {
    "docs/assets/github-preview.png": (1200, 520),
}
REQUIRED_README_CAPTIONS = [
    "Desktop: role-aware knowledge access, visible documents, eval gate, and trace/audit surfaces for permission-aware RAG.",
    "Desktop: investigator workflow with case context, governed action buttons, eval gate, and approval-driven operations controls.",
    "Desktop: release and incident triage workspace with eval evidence, rollout blocking, and audit/trace context.",
    "Mobile: narrow layout keeps user context, visible documents, and permission-aware knowledge controls readable.",
    "Mobile: approval workflow remains usable with case selection, eval gate, and governed action controls stacked for scanning.",
    "Mobile: release gate and incident triage stay readable while preserving blocked-rollout evidence.",
]
REQUIRED_COMMAND_QUICK_REFERENCE = [
    "Command quick-reference:",
    "| Local run | `python -B scripts/dev.py start` |",
    "| Verification | `python -B scripts/dev.py verify`, `python -B scripts/dev.py quality`, `python -B scripts/dev.py smoke`, `python -B scripts/dev.py evals`, `python -B scripts/dev.py contracts`, `python -B scripts/dev.py safety` |",
    "| Release evidence | `python -B scripts/dev.py replay-artifact`, `python -B scripts/dev.py report`, `python -B scripts/dev.py readiness-report`, `python -B scripts/dev.py fresh-clone`, `python -B scripts/post_publish_check.py` |",
    "| Visual assets | `python -B scripts/dev.py visual-assets`, `python -B scripts/dev.py visual-asset-diff`, `python -B scripts/dev.py refresh-visual-assets` |",
    "| GitHub maintenance | `python -B scripts/dev.py github-readiness`, `python -B scripts/dev.py pr-triage`, `python -B scripts/dev.py github-maintenance`, `python -B scripts/dev.py github-community` |",
    "| Optional environment checks | `python -B scripts/dev.py container-release`, `python -B scripts/dev.py docker-runtime`, `python -B scripts/dev.py openai-live` |",
    "Full command index:",
]
REQUIRED_README_GLOSSARY = [
    "## Core Terms",
    "| Release gate | The repository-level checks that keep public docs, evidence, runtime contracts, screenshots, and safety claims aligned before a change is published; see the [Evidence Matrix](#evidence-matrix) and [launch asset hygiene](docs/launch_assets_hygiene.md). |",
    "| Eval gate | Deterministic regression cases that must keep permission leaks, unsafe side effects, and unsafe release approvals at zero; see `python -B scripts/dev.py evals` and the [System Evidence Matrix](docs/portfolio_evidence_matrix.md). |",
    "| Approval gate | Application code that blocks external side effects until an authorized supervisor approves the pending action; see [Project 2](#project-2-regulated-customer-operations-agent) and [observability integrity](docs/observability_integrity.md). |",
    "| Trace ID | A per-response identifier that connects UI output to stored trace records, linked audit events, approvals, blocked actions, or release decisions; see [observability integrity](docs/observability_integrity.md). |",
    "| Audit log | Structured records of security, workflow, approval, and release-decision events that explain what happened after a run; see [threat model](docs/threat_model.md) and [observability integrity](docs/observability_integrity.md). |",
    "| Abstention | The answer behavior used when accessible evidence is missing, unauthorized, or unsafe after filtering; see [Project 1](#project-1-secure-enterprise-knowledge-copilot) and the [System Evidence Matrix](docs/portfolio_evidence_matrix.md). |",
]


def tracked_markdown_files() -> list[Path]:
    return sorted([ROOT / "README.md", *ROOT.glob("docs/**/*.md")])


def strip_code_fences(text: str) -> str:
    lines = []
    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            lines.append("")
            continue
        lines.append("" if in_fence else line)
    return "\n".join(lines)


def markdown_anchor(text: str) -> str:
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text


def anchors_for(path: Path) -> set[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return set()
    anchors = set()
    seen: dict[str, int] = {}
    for line in text.splitlines():
        match = HEADING_RE.match(line)
        if not match:
            continue
        base = markdown_anchor(match.group(2))
        if not base:
            continue
        count = seen.get(base, 0)
        seen[base] = count + 1
        anchors.add(base if count == 0 else f"{base}-{count}")
    return anchors


def is_external(link: str) -> bool:
    parsed = urlparse(link)
    return parsed.scheme in {"http", "https", "mailto"}


def normalize_link(raw: str) -> str:
    link = raw.strip()
    if link.startswith("<") and ">" in link:
        link = link[1 : link.index(">")]
    elif " " in link:
        link = link.split(" ", 1)[0]
    return unquote(link)


def target_for(source: Path, raw_link: str) -> tuple[Path | None, str | None]:
    link = normalize_link(raw_link)
    if not link or is_external(link):
        return None, None
    if link.startswith("#"):
        return source, link[1:]
    if link.startswith(("app://", "file://")):
        return None, None

    path_part, _, fragment = link.partition("#")
    path_part = path_part.split("?", 1)[0]
    if not path_part:
        return source, fragment
    target = (source.parent / path_part).resolve()
    return target, fragment or None


def within_repo(path: Path) -> bool:
    try:
        path.relative_to(ROOT)
        return True
    except ValueError:
        return False


def png_size(path: Path) -> tuple[int, int] | None:
    data = path.read_bytes()
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")


def gif_size(path: Path) -> tuple[int, int] | None:
    data = path.read_bytes()
    if len(data) < 10 or data[:6] not in {b"GIF87a", b"GIF89a"}:
        return None
    return int.from_bytes(data[6:8], "little"), int.from_bytes(data[8:10], "little")


def svg_ok(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False
    return "<svg" in text and "</svg>" in text


def check_image(path: Path) -> list[str]:
    failures = []
    suffix = path.suffix.lower()
    if suffix == ".png":
        size = png_size(path)
        if not size:
            failures.append(f"invalid PNG asset: {path.relative_to(ROOT).as_posix()}")
        elif size[0] < 200 or size[1] < 200:
            failures.append(f"PNG asset too small: {path.relative_to(ROOT).as_posix()} {size[0]}x{size[1]}")
    elif suffix == ".gif":
        size = gif_size(path)
        if not size:
            failures.append(f"invalid GIF asset: {path.relative_to(ROOT).as_posix()}")
        elif size[0] < 400 or size[1] < 300:
            failures.append(f"GIF asset too small: {path.relative_to(ROOT).as_posix()} {size[0]}x{size[1]}")
    elif suffix == ".svg" and not svg_ok(path):
        failures.append(f"invalid SVG asset: {path.relative_to(ROOT).as_posix()}")
    return failures


def check_markdown_links() -> list[str]:
    failures = []
    anchor_cache: dict[Path, set[str]] = {}
    for source in tracked_markdown_files():
        if not source.exists():
            continue
        text = strip_code_fences(source.read_text(encoding="utf-8"))
        for raw_link in LINK_RE.findall(text):
            target, fragment = target_for(source, raw_link)
            if target is None:
                continue
            rel_source = source.relative_to(ROOT).as_posix()
            if not within_repo(target):
                failures.append(f"{rel_source}: link escapes repo: {raw_link}")
                continue
            if not target.exists():
                failures.append(f"{rel_source}: missing local link target: {raw_link}")
                continue
            if fragment:
                anchors = anchor_cache.setdefault(target, anchors_for(target))
                normalized = markdown_anchor(fragment)
                if normalized and normalized not in anchors:
                    failures.append(f"{rel_source}: missing anchor {fragment!r} in {target.relative_to(ROOT).as_posix()}")
    return failures


def check_assets() -> list[str]:
    failures = []
    for path in sorted((ROOT / "docs" / "assets").glob("*")):
        if path.suffix.lower() in IMAGE_SUFFIXES:
            failures.extend(check_image(path))
    for rel_path, minimum in REQUIRED_IMAGE_SIZES.items():
        path = ROOT / rel_path
        if not path.exists():
            failures.append(f"missing required image asset: {rel_path}")
            continue
        size = png_size(path)
        if not size:
            failures.append(f"invalid required PNG asset: {rel_path}")
            continue
        if size[0] < minimum[0] or size[1] < minimum[1]:
            failures.append(f"required image asset too small: {rel_path} {size[0]}x{size[1]}")
    return failures


def check_readme_captions() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for caption in REQUIRED_README_CAPTIONS:
        if caption not in text:
            failures.append(f"README.md: missing screenshot caption: {caption}")
    return failures


def check_command_quick_reference() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_COMMAND_QUICK_REFERENCE:
        if expected not in text:
            failures.append(f"README.md: missing command quick-reference entry: {expected}")
    return failures


def check_readme_glossary() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_README_GLOSSARY:
        if expected not in text:
            failures.append(f"README.md: missing core glossary entry: {expected}")
    return failures


def main() -> int:
    failures = []
    failures.extend(check_markdown_links())
    failures.extend(check_assets())
    failures.extend(check_readme_captions())
    failures.extend(check_command_quick_reference())
    failures.extend(check_readme_glossary())
    if failures:
        print("Public asset check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Public asset check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
