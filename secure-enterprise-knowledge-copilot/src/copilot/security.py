from __future__ import annotations

import re


INJECTION_PATTERNS = [
    r"\bignore (all )?(previous|prior|system|developer) instructions\b",
    r"\bdisregard (all )?(previous|prior|system|developer) instructions\b",
    r"\breveal\b.*\b(confidential|secret|system prompt|hidden)\b",
    r"\boverride\b.*\bpolicy\b",
    r"\bexfiltrate\b",
    r"\bdo not cite\b",
]


def detect_prompt_injection(text: str) -> list[str]:
    lower = text.lower()
    hits = []
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, lower):
            hits.append(pattern)
    return hits


def sanitize_evidence(text: str) -> tuple[str, list[str]]:
    removed = []
    kept_lines = []
    for line in text.splitlines():
        if detect_prompt_injection(line):
            removed.append(line.strip())
            continue
        kept_lines.append(line)
    return "\n".join(kept_lines).strip(), removed

