from __future__ import annotations

import hashlib
import math
import re
from collections import Counter
from dataclasses import dataclass


EMBEDDING_MODEL = "local-hashing-v1"
EMBEDDING_DIMENSIONS = 1536
TOKEN_RE = re.compile(r"[a-z0-9_]+|[\u4e00-\u9fff]", re.IGNORECASE)
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "do",
    "for",
    "from",
    "how",
    "i",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "our",
    "should",
    "the",
    "to",
    "we",
    "what",
    "when",
    "where",
    "who",
    "why",
    "with",
    "you",
}


@dataclass(frozen=True)
class TextEmbedding:
    vector: list[float]
    model: str = EMBEDDING_MODEL
    dimensions: int = EMBEDDING_DIMENSIONS

    @property
    def norm(self) -> float:
        return round(math.sqrt(sum(value * value for value in self.vector)), 6)

    def metadata(self) -> dict:
        return {
            "embedding_model": self.model,
            "embedding_dimensions": self.dimensions,
            "embedding_norm": self.norm,
        }


def embed_text(text: str) -> TextEmbedding:
    tokens = _tokens(text)
    if not tokens:
        return TextEmbedding(vector=[0.0] * EMBEDDING_DIMENSIONS)

    counts = Counter(tokens)
    vector = [0.0] * EMBEDDING_DIMENSIONS
    for token, count in counts.items():
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        index = int.from_bytes(digest[:4], "big") % EMBEDDING_DIMENSIONS
        sign = 1 if digest[4] % 2 == 0 else -1
        vector[index] += sign * math.sqrt(count)

    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return TextEmbedding(vector=[0.0] * EMBEDDING_DIMENSIONS)
    return TextEmbedding(vector=[round(value / norm, 6) for value in vector])


def embed_chunk(title: str, text: str) -> TextEmbedding:
    return embed_text(f"{title}\n\n{text}")


def cosine_similarity(left: list[float] | None, right: list[float] | None) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    return sum(a * b for a, b in zip(left, right))


def _tokens(text: str) -> list[str]:
    raw = [token.lower() for token in TOKEN_RE.findall(text)]
    return [token for token in raw if token not in STOPWORDS and len(token) > 1 and not token.isdigit()]
