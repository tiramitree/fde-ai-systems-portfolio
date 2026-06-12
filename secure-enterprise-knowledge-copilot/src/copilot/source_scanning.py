from __future__ import annotations

import re
from typing import Any

from .security import detect_prompt_injection


SOURCE_SCAN_SCHEMA_VERSION = "source_scan_v1"
SOURCE_SCAN_POLICY = "local_source_safety_scan_v1"

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d[\d .()/-]{7,}\d)(?!\d)")
WINDOWS_PATH_RE = re.compile(r"\b[A-Za-z]:[\\/][^\s'\"<>|]+")
SECRET_ASSIGNMENT_RE = re.compile(
    r"\b(bearer|token|api[_-]?key|password|secret)\s*[:=]\s*[^\s,;]+",
    re.IGNORECASE,
)
OPENAI_KEY_RE = re.compile(r"\b" + "s" + r"k-[A-Za-z0-9_-]{8,}\b")
GITHUB_TOKEN_RE = re.compile(r"\b" + "g" + r"h[opusr]_[A-Za-z0-9_]{8,}\b")
WECHAT_ID_RE = re.compile(r"\b" + "wx" + r"id_[A-Za-z0-9_:-]+\b", re.IGNORECASE)
ONEDRIVE_PATH_RE = re.compile(r"\b" + "One" + r"Drive[\\/][^\s'\"<>|]+", re.IGNORECASE)
URL_RE = re.compile(r"https?://[^\s)]+", re.IGNORECASE)


def _match_count(pattern: re.Pattern[str], text: str) -> int:
    return len(pattern.findall(text))


def _severity(finding_counts: dict[str, int]) -> str:
    if any(
        finding_counts.get(category, 0) > 0
        for category in (
            "token_like_secret",
            "secret_like_assignment",
            "private_path_or_identifier",
            "retrieved_instruction_override",
        )
    ):
        return "high"
    if finding_counts.get("personal_identifier", 0) > 0:
        return "medium"
    if finding_counts.get("external_link", 0) > 0:
        return "low"
    return "none"


def scan_source_content(raw_content: str, normalized_text: str = "") -> dict[str, Any]:
    text = f"{raw_content}\n{normalized_text}".strip()
    finding_counts = {
        "retrieved_instruction_override": len(detect_prompt_injection(text)),
        "secret_like_assignment": _match_count(SECRET_ASSIGNMENT_RE, text),
        "token_like_secret": _match_count(OPENAI_KEY_RE, text) + _match_count(GITHUB_TOKEN_RE, text),
        "private_path_or_identifier": (
            _match_count(WINDOWS_PATH_RE, text)
            + _match_count(ONEDRIVE_PATH_RE, text)
            + _match_count(WECHAT_ID_RE, text)
        ),
        "personal_identifier": _match_count(EMAIL_RE, text) + _match_count(SSN_RE, text) + _match_count(PHONE_RE, text),
        "external_link": _match_count(URL_RE, text),
    }
    finding_categories = sorted(category for category, count in finding_counts.items() if count > 0)
    severity = _severity(finding_counts)
    review_required = severity in {"medium", "high"}
    return {
        "schema_version": SOURCE_SCAN_SCHEMA_VERSION,
        "policy": SOURCE_SCAN_POLICY,
        "status": "review_required" if review_required else "passed",
        "severity": severity,
        "review_required": review_required,
        "finding_count": sum(finding_counts.values()),
        "finding_counts": finding_counts,
        "finding_categories": finding_categories,
        "raw_matches_returned": False,
    }


def merge_source_scan_counts(scans: list[dict[str, Any]]) -> dict[str, int]:
    merged: dict[str, int] = {}
    for scan in scans:
        counts = scan.get("finding_counts")
        if not isinstance(counts, dict):
            continue
        for category, value in counts.items():
            try:
                count = int(value)
            except (TypeError, ValueError):
                count = 0
            merged[str(category)] = merged.get(str(category), 0) + max(count, 0)
    return {category: count for category, count in sorted(merged.items()) if count > 0}
