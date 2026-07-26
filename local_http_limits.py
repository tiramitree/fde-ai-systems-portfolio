from __future__ import annotations

import json
import os
from typing import BinaryIO, Mapping, Any


MAX_JSON_BODY_BYTES_ENV = "FDE_MAX_JSON_BODY_BYTES"
DEFAULT_MAX_JSON_BODY_BYTES = 1_048_576


class RequestBodyError(ValueError):
    message = "Invalid JSON body."

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.message
        super().__init__(self.message)


class RequestBodyTooLarge(RequestBodyError):
    message = "Request body too large."


class InvalidContentLength(RequestBodyError):
    message = "Invalid Content-Length."


class InvalidJsonBody(RequestBodyError):
    message = "JSON body must be an object."


def max_json_body_bytes() -> int:
    raw = os.getenv(MAX_JSON_BODY_BYTES_ENV, "").strip()
    if not raw:
        return DEFAULT_MAX_JSON_BODY_BYTES
    try:
        value = int(raw)
    except ValueError:
        return DEFAULT_MAX_JSON_BODY_BYTES
    if value < 1:
        return DEFAULT_MAX_JSON_BODY_BYTES
    return value


def parse_content_length(value: Any) -> int:
    raw = str(value or "0").strip()
    if not raw:
        return 0
    try:
        length = int(raw)
    except ValueError as exc:
        raise InvalidContentLength() from exc
    if length < 0:
        raise InvalidContentLength()
    return length


def read_json_body(headers: Mapping[str, Any], rfile: BinaryIO) -> dict:
    length = parse_content_length(headers.get("Content-Length", "0"))
    if length > max_json_body_bytes():
        raise RequestBodyTooLarge()

    raw = rfile.read(length) if length else b"{}"
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RequestBodyError("Invalid JSON body.") from exc

    payload = json.loads(text or "{}")
    if not isinstance(payload, dict):
        raise InvalidJsonBody()
    return payload
