from __future__ import annotations

import bisect
import re
from dataclasses import dataclass


PARAGRAPH_RE = re.compile(r"\S.*?(?=\n\s*\n|\Z)", re.DOTALL)
SOURCE_SPAN_UNIT = "normalized_text"


@dataclass(frozen=True)
class TextChunk:
    text: str
    source_span: dict[str, int | str]


@dataclass(frozen=True)
class _Paragraph:
    text: str
    start_char: int
    end_char: int


def _normalize_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _line_starts(text: str) -> list[int]:
    starts = [0]
    starts.extend(match.end() for match in re.finditer("\n", text))
    return starts


def _line_number(line_starts: list[int], char_index: int) -> int:
    return bisect.bisect_right(line_starts, max(char_index, 0))


def _source_span(text: str, line_starts: list[int], start_char: int, end_char: int) -> dict[str, int | str]:
    safe_end = max(start_char, end_char)
    end_line_index = max(start_char, safe_end - 1)
    return {
        "text_unit": SOURCE_SPAN_UNIT,
        "start_char": start_char,
        "end_char": safe_end,
        "start_line": _line_number(line_starts, start_char),
        "end_line": _line_number(line_starts, end_line_index),
    }


def _paragraphs(text: str) -> list[_Paragraph]:
    paragraphs: list[_Paragraph] = []
    for match in PARAGRAPH_RE.finditer(text):
        raw = match.group(0)
        trimmed = raw.strip()
        if not trimmed:
            continue
        leading = len(raw) - len(raw.lstrip())
        start_char = match.start() + leading
        end_char = start_char + len(trimmed)
        paragraphs.append(_Paragraph(text=trimmed, start_char=start_char, end_char=end_char))
    return paragraphs


def chunk_text_with_spans(text: str, max_chars: int = 900) -> list[TextChunk]:
    normalized = _normalize_text(text)
    line_starts = _line_starts(normalized)
    chunks: list[TextChunk] = []
    current: list[_Paragraph] = []
    current_len = 0

    for paragraph in _paragraphs(normalized):
        if current and current_len + len(paragraph.text) > max_chars:
            chunk_text_value = "\n\n".join(item.text for item in current)
            chunks.append(
                TextChunk(
                    text=chunk_text_value,
                    source_span=_source_span(normalized, line_starts, current[0].start_char, current[-1].end_char),
                )
            )
            current = []
            current_len = 0
        current.append(paragraph)
        current_len += len(paragraph.text)

    if current:
        chunk_text_value = "\n\n".join(item.text for item in current)
        chunks.append(
            TextChunk(
                text=chunk_text_value,
                source_span=_source_span(normalized, line_starts, current[0].start_char, current[-1].end_char),
            )
        )
    return chunks


def chunk_text(text: str, max_chars: int = 900) -> list[str]:
    return [chunk.text for chunk in chunk_text_with_spans(text, max_chars=max_chars)]
