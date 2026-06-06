from __future__ import annotations

import re
from typing import Any


REDACTION_POLICY = "public_trace_export_redaction_v1"

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


def redact_text(value: str) -> str:
    redacted = value
    redacted = EMAIL_RE.sub("[REDACTED_EMAIL]", redacted)
    redacted = SSN_RE.sub("[REDACTED_SSN]", redacted)
    redacted = PHONE_RE.sub("[REDACTED_PHONE]", redacted)
    redacted = SECRET_ASSIGNMENT_RE.sub(lambda match: f"{match.group(1)}=[REDACTED_SECRET]", redacted)
    redacted = OPENAI_KEY_RE.sub("[REDACTED_SECRET]", redacted)
    redacted = GITHUB_TOKEN_RE.sub("[REDACTED_SECRET]", redacted)
    redacted = WINDOWS_PATH_RE.sub("[REDACTED_PATH]", redacted)
    redacted = ONEDRIVE_PATH_RE.sub("[REDACTED_PATH]", redacted)
    redacted = WECHAT_ID_RE.sub("[REDACTED_PRIVATE_ID]", redacted)
    return redacted


def redact_value(value: Any) -> Any:
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, list):
        return [redact_value(item) for item in value]
    if isinstance(value, tuple):
        return [redact_value(item) for item in value]
    if isinstance(value, dict):
        return {key: redact_value(item) for key, item in value.items()}
    return value
