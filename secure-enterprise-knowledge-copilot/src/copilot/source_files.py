from __future__ import annotations

import base64
import binascii
import mimetypes
from dataclasses import dataclass
from pathlib import PurePath
from typing import Any

from .source_parsing import SUPPORTED_MIME_TYPES


MAX_FILE_BYTES = 80_000
MAX_FILENAME_LENGTH = 180

EXTENSION_MIME_TYPES = {
    ".csv": "text/csv",
    ".htm": "text/html",
    ".html": "text/html",
    ".json": "application/json",
    ".md": "text/markdown",
    ".markdown": "text/markdown",
    ".txt": "text/plain",
}


class SourceFileError(Exception):
    pass


@dataclass(frozen=True)
class DecodedSourceFile:
    text: str
    mime_type: str
    metadata: dict[str, Any]


def decode_source_file(value: object, source_mime_override: object = None) -> DecodedSourceFile:
    if not isinstance(value, dict):
        raise SourceFileError("document.file must be an object")

    filename = _safe_filename(value.get("filename"))
    encoded = value.get("content_base64")
    if not isinstance(encoded, str) or not encoded.strip():
        raise SourceFileError("document.file.content_base64 is required")

    try:
        raw_bytes = base64.b64decode(encoded.encode("ascii"), validate=True)
    except (UnicodeEncodeError, binascii.Error):
        raise SourceFileError("document.file.content_base64 must be valid base64") from None

    if not raw_bytes:
        raise SourceFileError("document.file.content_base64 decoded to an empty file")
    if len(raw_bytes) > MAX_FILE_BYTES:
        raise SourceFileError(f"document.file exceeds {MAX_FILE_BYTES} bytes")

    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise SourceFileError("document.file content must be UTF-8 text") from None

    mime_type, mime_source = _resolve_mime_type(filename, value, source_mime_override)
    metadata = {
        "file_name": filename,
        "file_size_bytes": len(raw_bytes),
        "file_extension": PurePath(filename).suffix.lower(),
        "file_content_encoding": "base64",
        "mime_type_source": mime_source,
    }
    return DecodedSourceFile(text=text, mime_type=mime_type, metadata=metadata)


def _safe_filename(value: object) -> str:
    if not isinstance(value, str):
        raise SourceFileError("document.file.filename must be a string")
    filename = value.strip()
    if not filename:
        raise SourceFileError("document.file.filename is required")
    if len(filename) > MAX_FILENAME_LENGTH:
        raise SourceFileError(f"document.file.filename exceeds {MAX_FILENAME_LENGTH} characters")
    if any(separator in filename for separator in ("/", "\\", ":")):
        raise SourceFileError("document.file.filename must be a base file name, not a path")
    if filename in {".", ".."}:
        raise SourceFileError("document.file.filename is invalid")
    return filename


def _resolve_mime_type(filename: str, file_payload: dict, override: object) -> tuple[str, str]:
    explicit = file_payload.get("mime_type") or file_payload.get("source_mime") or override
    if explicit:
        mime_type = str(explicit).strip().lower()
        source = "payload"
    else:
        extension = PurePath(filename).suffix.lower()
        guessed = EXTENSION_MIME_TYPES.get(extension) or mimetypes.guess_type(filename)[0]
        mime_type = str(guessed or "text/plain").strip().lower()
        source = "filename"
    if mime_type not in SUPPORTED_MIME_TYPES:
        raise SourceFileError(f"Unsupported document.file mime type: {mime_type}")
    return mime_type, source
