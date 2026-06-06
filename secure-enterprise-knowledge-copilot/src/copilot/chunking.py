from __future__ import annotations


def chunk_text(text: str, max_chars: int = 900) -> list[str]:
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    for paragraph in paragraphs:
        if current and current_len + len(paragraph) > max_chars:
            chunks.append("\n\n".join(current))
            current = []
            current_len = 0
        current.append(paragraph)
        current_len += len(paragraph)

    if current:
        chunks.append("\n\n".join(current))
    return chunks
