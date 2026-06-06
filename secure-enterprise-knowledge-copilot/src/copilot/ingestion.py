from __future__ import annotations

import hashlib
import html
import re
from datetime import datetime, timezone

from .storage import JsonStore, chunk_text, get_user, insert_audit


VALID_CLASSIFICATIONS = {"public", "internal", "confidential"}
VALID_ROLES = {"employee", "manager", "admin"}
SUPPORTED_MIME_TYPES = {
    "text/plain",
    "text/markdown",
    "text/csv",
    "text/html",
    "application/json",
}
SLUG_RE = re.compile(r"[^a-z0-9]+")
SCRIPT_STYLE_RE = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")


class IngestionError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(message)


def _utc_date() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _as_string(value: object, field: str, *, min_length: int = 1, max_length: int = 40_000) -> str:
    if not isinstance(value, str):
        raise IngestionError(400, f"{field} must be a string")
    normalized = value.replace("\r\n", "\n").replace("\r", "\n").strip()
    if len(normalized) < min_length:
        raise IngestionError(400, f"{field} is required")
    if len(normalized) > max_length:
        raise IngestionError(413, f"{field} exceeds {max_length} characters")
    return normalized


def _slug(text: str) -> str:
    slug = SLUG_RE.sub("-", text.lower()).strip("-")
    return slug[:72] or "document"


def _document_id(tenant_id: str, title: str, source_url: str, source_hash: str) -> str:
    stable = hashlib.sha256(f"{tenant_id}\n{source_url}\n{source_hash}".encode("utf-8")).hexdigest()[:10]
    return f"ingested-{_slug(title)}-{stable}"


def _extract_text(content: str, source_mime: str) -> str:
    if source_mime == "text/html":
        without_scripts = SCRIPT_STYLE_RE.sub(" ", content)
        without_tags = TAG_RE.sub(" ", without_scripts)
        return html.unescape(re.sub(r"[ \t]+", " ", without_tags)).strip()
    if source_mime == "application/json":
        # Keep JSON content searchable while avoiding a parser dependency or hidden schema assumption.
        return re.sub(r"[{}[\]\",:]+", " ", content).strip()
    return content


def _validate_roles(value: object, classification: str) -> list[str]:
    if value is None:
        return ["employee", "manager", "admin"] if classification != "confidential" else ["manager", "admin"]
    if not isinstance(value, list) or not value:
        raise IngestionError(400, "allowed_roles must be a non-empty list")
    roles = []
    for role in value:
        if not isinstance(role, str) or role not in VALID_ROLES:
            raise IngestionError(400, f"Unsupported allowed role: {role}")
        if role not in roles:
            roles.append(role)
    if classification == "confidential" and "employee" in roles:
        raise IngestionError(400, "confidential documents cannot be visible to employee role")
    return roles


def _public_document(doc: dict) -> dict:
    return {key: value for key, value in doc.items() if key != "body"}


def ingest_document(store: JsonStore, payload: dict) -> dict:
    actor_id = _as_string(payload.get("user_id"), "user_id", max_length=80)
    actor = get_user(store, actor_id)
    if not actor:
        raise IngestionError(404, f"Unknown user_id: {actor_id}")
    if actor["role"] != "admin":
        raise IngestionError(403, "Only admin users can ingest documents.")

    document = payload.get("document", payload)
    if not isinstance(document, dict):
        raise IngestionError(400, "document must be an object")

    title = _as_string(document.get("title"), "title", max_length=180)
    raw_body = _as_string(document.get("body") or document.get("content"), "body")
    source_mime = str(document.get("source_mime", "text/plain")).strip().lower()
    if source_mime not in SUPPORTED_MIME_TYPES:
        raise IngestionError(415, f"Unsupported source_mime: {source_mime}")

    body = _extract_text(raw_body, source_mime)
    if len(body) < 20:
        raise IngestionError(400, "body must contain at least 20 searchable characters")

    tenant_id = str(document.get("tenant_id") or actor["tenant_id"]).strip()
    if tenant_id != actor["tenant_id"]:
        raise IngestionError(403, "Admins can ingest only into their own tenant.")

    classification = str(document.get("classification", "internal")).strip().lower()
    if classification not in VALID_CLASSIFICATIONS:
        raise IngestionError(400, f"Unsupported classification: {classification}")
    allowed_roles = _validate_roles(document.get("allowed_roles"), classification)

    source_url = str(document.get("source_url") or f"ingested://{tenant_id}/{_slug(title)}").strip()
    version = str(document.get("version") or _utc_date()).strip()
    updated_at = str(document.get("updated_at") or _utc_date()).strip()
    source_hash = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()
    doc_id = str(document.get("id") or _document_id(tenant_id, title, source_url, source_hash)).strip()
    replace = bool(payload.get("replace") or document.get("replace"))

    existing = next((doc for doc in store.state["documents"] if doc["id"] == doc_id), None)
    if existing and not replace:
        raise IngestionError(409, f"Document already exists: {doc_id}")
    if existing:
        store.state["documents"] = [doc for doc in store.state["documents"] if doc["id"] != doc_id]
        store.state["chunks"] = [chunk for chunk in store.state["chunks"] if chunk["doc_id"] != doc_id]

    doc = {
        "id": doc_id,
        "title": title,
        "tenant_id": tenant_id,
        "classification": classification,
        "allowed_roles": allowed_roles,
        "source_url": source_url,
        "source_mime": source_mime,
        "source_hash": source_hash,
        "version": version,
        "updated_at": updated_at,
        "body": body,
    }

    chunks = []
    for idx, text in enumerate(chunk_text(body)):
        chunks.append(
            {
                "id": f"{doc_id}::chunk-{idx + 1}",
                "doc_id": doc_id,
                "chunk_index": idx,
                "title": title,
                "text": text,
                "tenant_id": tenant_id,
                "classification": classification,
                "allowed_roles": allowed_roles,
                "source_url": source_url,
                "source_mime": source_mime,
                "source_hash": source_hash,
                "version": version,
                "updated_at": updated_at,
            }
        )

    store.state["documents"].append(doc)
    store.state["chunks"].extend(chunks)
    insert_audit(
        store,
        actor_id,
        "document_ingested",
        {
            "doc_id": doc_id,
            "title": title,
            "classification": classification,
            "allowed_roles": allowed_roles,
            "chunk_count": len(chunks),
            "source_url": source_url,
            "source_mime": source_mime,
            "source_hash": source_hash,
            "replaced_existing": existing is not None,
        },
    )

    return {
        "document": _public_document(doc),
        "chunk_count": len(chunks),
        "ingestion": {
            "actor_user_id": actor_id,
            "replace": replace,
            "source_hash": source_hash,
            "supported_mime_types": sorted(SUPPORTED_MIME_TYPES),
        },
    }
