from __future__ import annotations

import csv
import html
import json
import re
from dataclasses import dataclass
from io import StringIO
from typing import Any


SUPPORTED_MIME_TYPES = {
    "text/plain",
    "text/markdown",
    "text/csv",
    "text/html",
    "application/json",
}

SCRIPT_STYLE_RE = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
MARKDOWN_DECORATION_RE = re.compile(r"^[#>*\-\s]+|[`*]+")
SPACE_RE = re.compile(r"[ \t]+")


@dataclass(frozen=True)
class ParsedSource:
    text: str
    parser_name: str
    normalized_characters: int
    metadata: dict[str, Any]
    warnings: tuple[str, ...] = ()


class SourceParseError(Exception):
    pass


def parse_source_content(content: str, source_mime: str) -> ParsedSource:
    if source_mime not in SUPPORTED_MIME_TYPES:
        raise SourceParseError(f"Unsupported source_mime: {source_mime}")

    if source_mime == "text/html":
        text = _parse_html(content)
        return _parsed(text, "html-v1", {"source_mime": source_mime})
    if source_mime == "text/markdown":
        text = _parse_markdown(content)
        return _parsed(text, "markdown-v1", {"source_mime": source_mime})
    if source_mime == "text/csv":
        text, metadata, warnings = _parse_csv(content)
        return _parsed(text, "csv-v1", {"source_mime": source_mime, **metadata}, warnings)
    if source_mime == "application/json":
        text, metadata, warnings = _parse_json(content)
        return _parsed(text, "json-v1", {"source_mime": source_mime, **metadata}, warnings)

    return _parsed(content, "plain-text-v1", {"source_mime": source_mime})


def _parsed(text: str, parser_name: str, metadata: dict[str, Any], warnings: tuple[str, ...] = ()) -> ParsedSource:
    normalized = _normalize_text(text)
    return ParsedSource(
        text=normalized,
        parser_name=parser_name,
        normalized_characters=len(normalized),
        metadata=metadata,
        warnings=warnings,
    )


def _normalize_text(text: str) -> str:
    normalized_lines = [
        SPACE_RE.sub(" ", line).strip()
        for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    ]
    blocks: list[str] = []
    previous_blank = False
    for line in normalized_lines:
        if not line:
            if not previous_blank:
                blocks.append("")
            previous_blank = True
            continue
        blocks.append(line)
        previous_blank = False
    return "\n".join(blocks).strip()


def _parse_html(content: str) -> str:
    without_scripts = SCRIPT_STYLE_RE.sub(" ", content)
    without_tags = TAG_RE.sub(" ", without_scripts)
    return html.unescape(without_tags)


def _parse_markdown(content: str) -> str:
    lines = []
    in_fence = False
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            lines.append(line)
            continue
        line = MARKDOWN_LINK_RE.sub(r"\1", line)
        line = MARKDOWN_DECORATION_RE.sub("", line)
        lines.append(line)
    return "\n".join(lines)


def _parse_csv(content: str) -> tuple[str, dict[str, Any], tuple[str, ...]]:
    try:
        rows = list(csv.reader(StringIO(content)))
    except csv.Error as exc:
        raise SourceParseError(f"Could not parse CSV source: {exc}") from exc

    non_empty_rows = [[cell.strip() for cell in row] for row in rows if any(cell.strip() for cell in row)]
    if not non_empty_rows:
        return "", {"row_count": 0, "column_count": 0}, ("empty_csv",)

    header = non_empty_rows[0]
    has_header = len(non_empty_rows) > 1 and all(header)
    data_rows = non_empty_rows[1:] if has_header else non_empty_rows
    column_count = max((len(row) for row in non_empty_rows), default=0)
    warnings = ("ragged_csv_rows",) if any(len(row) != column_count for row in non_empty_rows) else ()
    lines = []

    for index, row in enumerate(data_rows, start=1):
        if has_header:
            cells = []
            for column_index, cell in enumerate(row):
                label = header[column_index] if column_index < len(header) else f"column_{column_index + 1}"
                if cell:
                    cells.append(f"{label}: {cell}")
            if cells:
                lines.append(f"row {index}: " + "; ".join(cells))
        else:
            cells = [cell for cell in row if cell]
            if cells:
                lines.append(f"row {index}: " + " | ".join(cells))

    return "\n".join(lines), {"row_count": len(data_rows), "column_count": column_count, "has_header": has_header}, warnings


def _parse_json(content: str) -> tuple[str, dict[str, Any], tuple[str, ...]]:
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise SourceParseError(f"Could not parse JSON source: {exc.msg}") from exc

    warnings: tuple[str, ...] = ()
    if not isinstance(payload, (dict, list)):
        warnings = ("json_scalar_root",)
    lines = list(_flatten_json(payload))
    return "\n".join(lines), {"json_root_type": type(payload).__name__, "field_count": len(lines)}, warnings


def _flatten_json(value: Any, prefix: str = "root") -> list[str]:
    if isinstance(value, dict):
        lines: list[str] = []
        for key, item in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            lines.extend(_flatten_json(item, child_prefix))
        return lines
    if isinstance(value, list):
        lines = []
        for index, item in enumerate(value):
            lines.extend(_flatten_json(item, f"{prefix}[{index}]"))
        return lines
    return [f"{prefix}: {value}"]
