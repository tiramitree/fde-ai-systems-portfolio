from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone

from .chunking import SOURCE_SPAN_UNIT, chunk_text_with_spans
from .embeddings import EMBEDDING_DIMENSIONS, EMBEDDING_MODEL, embed_chunk
from .repositories import KnowledgeRepository
from .source_parsing import SUPPORTED_MIME_TYPES, SourceParseError, parse_source_content


VALID_CLASSIFICATIONS = {"public", "internal", "confidential"}
VALID_ROLES = {"employee", "manager", "admin"}
SLUG_RE = re.compile(r"[^a-z0-9]+")
MAX_SYNC_DOCUMENTS = 10


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


def _as_bool(value: object, field: str, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    raise IngestionError(400, f"{field} must be a boolean")


def _slug(text: str) -> str:
    slug = SLUG_RE.sub("-", text.lower()).strip("-")
    return slug[:72] or "document"


def _document_id(tenant_id: str, title: str, source_url: str, source_hash: str) -> str:
    stable = hashlib.sha256(f"{tenant_id}\n{source_url}\n{source_hash}".encode("utf-8")).hexdigest()[:10]
    return f"ingested-{_slug(title)}-{stable}"


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


def _metadata_int(document: dict, key: str, default: int = 0) -> int:
    value = document.get(key, default)
    if isinstance(value, bool):
        return default
    try:
        numeric_value = int(value)
    except (TypeError, ValueError):
        raise IngestionError(400, f"{key} must be an integer") from None
    return max(numeric_value, 0)


def _public_document(doc: dict) -> dict:
    return {key: value for key, value in doc.items() if key != "body"}


def _metadata_string(document: dict, key: str, default: str, *, max_length: int = 180) -> str:
    value = str(document.get(key) or default).strip()
    if not value:
        value = default
    return value[:max_length]


def _acl_role_drift(previous_document: dict | None, current_allowed_roles: list[str]) -> dict:
    current = sorted(current_allowed_roles)
    if not previous_document:
        return {
            "changed": False,
            "previous_allowed_roles": [],
            "current_allowed_roles": current,
            "added_roles": [],
            "removed_roles": [],
        }
    previous = sorted(str(role) for role in previous_document.get("allowed_roles", []))
    return {
        "changed": previous != current,
        "previous_allowed_roles": previous,
        "current_allowed_roles": current,
        "added_roles": sorted(set(current) - set(previous)),
        "removed_roles": sorted(set(previous) - set(current)),
    }


def _validate_acl_snapshot(value: object) -> dict | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise IngestionError(400, "connector.acl_snapshot must be an object")
    version = _as_string(value.get("version"), "connector.acl_snapshot.version", max_length=180)
    documents = value.get("documents")
    if not isinstance(documents, dict) or not documents:
        raise IngestionError(400, "connector.acl_snapshot.documents must be a non-empty object")
    for key, record in documents.items():
        if not isinstance(key, str) or not key.strip():
            raise IngestionError(400, "connector.acl_snapshot document keys must be non-empty strings")
        if not isinstance(record, dict):
            raise IngestionError(400, "connector.acl_snapshot document records must be objects")
        if "allowed_roles" not in record:
            raise IngestionError(400, f"connector ACL record missing allowed_roles: {key}")
    return {"version": version, "documents": documents}


def _source_acl_record(acl_snapshot: dict | None, external_id: str, doc_id: object) -> dict | None:
    if not acl_snapshot:
        return None
    documents = acl_snapshot["documents"]
    candidates = [external_id, str(doc_id or "").strip()]
    for candidate in candidates:
        if candidate and candidate in documents:
            return documents[candidate]
    raise IngestionError(403, f"source ACL snapshot is missing document permission: {external_id}")


def ingest_document(repo: KnowledgeRepository, payload: dict) -> dict:
    actor_id = _as_string(payload.get("user_id"), "user_id", max_length=80)
    actor = repo.get_user(actor_id)
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

    try:
        parsed_source = parse_source_content(raw_body, source_mime)
    except SourceParseError as exc:
        raise IngestionError(400, str(exc)) from exc

    body = parsed_source.text
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
    source_connector = _metadata_string(document, "source_connector", "manual")
    external_id = _metadata_string(document, "external_id", doc_id, max_length=240)
    acl_source = _metadata_string(document, "acl_source", "manual")
    sync_cursor = _metadata_string(document, "sync_cursor", "", max_length=240)
    allowed_roles_source = _metadata_string(document, "allowed_roles_source", "document_payload", max_length=80)
    source_acl_version = _metadata_string(document, "source_acl_version", "", max_length=180)
    source_acl_permission_id = _metadata_string(document, "source_acl_permission_id", "", max_length=240)
    source_acl_principal_count = _metadata_int(document, "source_acl_principal_count", 0)

    exists = repo.document_exists(doc_id)
    previous_document = repo.get_document(doc_id) if exists else None
    if exists and not replace:
        raise IngestionError(409, f"Document already exists: {doc_id}")
    acl_role_drift = _acl_role_drift(previous_document, allowed_roles)

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
        "parser_name": parsed_source.parser_name,
        "parser_metadata": parsed_source.metadata,
        "parser_warnings": list(parsed_source.warnings),
        "source_connector": source_connector,
        "external_id": external_id,
        "acl_source": acl_source,
        "sync_cursor": sync_cursor,
        "allowed_roles_source": allowed_roles_source,
        "source_acl_version": source_acl_version,
        "source_acl_permission_id": source_acl_permission_id,
        "source_acl_principal_count": source_acl_principal_count,
        "body": body,
    }

    chunks = []
    for idx, chunk in enumerate(chunk_text_with_spans(body)):
        embedding = embed_chunk(title, chunk.text)
        chunks.append(
            {
                "id": f"{doc_id}::chunk-{idx + 1}",
                "doc_id": doc_id,
                "chunk_index": idx,
                "title": title,
                "text": chunk.text,
                "source_span": chunk.source_span,
                "tenant_id": tenant_id,
                "classification": classification,
                "allowed_roles": allowed_roles,
                "source_url": source_url,
                "source_mime": source_mime,
                "source_hash": source_hash,
                "version": version,
                "updated_at": updated_at,
                "parser_name": parsed_source.parser_name,
                "parser_metadata": parsed_source.metadata,
                "parser_warnings": list(parsed_source.warnings),
                "source_connector": source_connector,
                "external_id": external_id,
                "acl_source": acl_source,
                "sync_cursor": sync_cursor,
                "allowed_roles_source": allowed_roles_source,
                "source_acl_version": source_acl_version,
                "source_acl_permission_id": source_acl_permission_id,
                "source_acl_principal_count": source_acl_principal_count,
                "embedding": embedding.vector,
                "chunk_source_span_unit": SOURCE_SPAN_UNIT,
                **embedding.metadata(),
            }
        )

    replaced_existing = repo.replace_document_with_chunks(doc, chunks)
    repo.insert_audit(
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
            "parser_name": parsed_source.parser_name,
            "parser_warnings": list(parsed_source.warnings),
            "source_connector": source_connector,
            "external_id": external_id,
            "acl_source": acl_source,
            "sync_cursor": sync_cursor,
            "allowed_roles_source": allowed_roles_source,
            "source_acl_version": source_acl_version,
            "source_acl_permission_id": source_acl_permission_id,
            "source_acl_principal_count": source_acl_principal_count,
            "acl_role_drift": acl_role_drift,
            "normalized_characters": parsed_source.normalized_characters,
            "chunk_source_span_unit": SOURCE_SPAN_UNIT,
            "chunk_source_span_count": len(chunks),
            "embedding_model": EMBEDDING_MODEL,
            "embedding_dimensions": EMBEDDING_DIMENSIONS,
            "chunk_embedding_count": len(chunks),
            "replaced_existing": replaced_existing,
        },
    )

    return {
        "document": _public_document(doc),
        "chunk_count": len(chunks),
        "ingestion": {
            "actor_user_id": actor_id,
            "replace": replace,
            "replaced_existing": replaced_existing,
            "source_hash": source_hash,
            "supported_mime_types": sorted(SUPPORTED_MIME_TYPES),
            "parser": {
                "name": parsed_source.parser_name,
                "normalized_characters": parsed_source.normalized_characters,
                "metadata": parsed_source.metadata,
                "warnings": list(parsed_source.warnings),
            },
            "source": {
                "connector": source_connector,
                "external_id": external_id,
                "acl_source": acl_source,
                "sync_cursor": sync_cursor,
                "allowed_roles_source": allowed_roles_source,
                "source_acl_version": source_acl_version,
                "source_acl_permission_id": source_acl_permission_id,
                "source_acl_principal_count": source_acl_principal_count,
                "acl_role_drift": acl_role_drift,
            },
            "chunk_source_span_unit": SOURCE_SPAN_UNIT,
            "chunk_source_span_count": len(chunks),
            "embedding": {
                "model": EMBEDDING_MODEL,
                "dimensions": EMBEDDING_DIMENSIONS,
                "chunk_embedding_count": len(chunks),
            },
        },
    }


def sync_source_batch(repo: KnowledgeRepository, payload: dict) -> dict:
    actor_id = _as_string(payload.get("user_id"), "user_id", max_length=80)
    actor = repo.get_user(actor_id)
    if not actor:
        raise IngestionError(404, f"Unknown user_id: {actor_id}")
    if actor["role"] != "admin":
        raise IngestionError(403, "Only admin users can sync sources.")

    connector = payload.get("connector", {})
    if not isinstance(connector, dict):
        raise IngestionError(400, "connector must be an object")
    connector_name = _as_string(connector.get("name"), "connector.name", max_length=80)
    connector_cursor = _as_string(connector.get("cursor") or _utc_date(), "connector.cursor", max_length=240)
    acl_source = _as_string(connector.get("acl_source") or connector_name, "connector.acl_source", max_length=180)
    acl_snapshot = _validate_acl_snapshot(connector.get("acl_snapshot"))
    connector_scheme = _slug(connector_name) or "connector"
    prune_missing = _as_bool(
        payload.get("prune_missing", connector.get("prune_missing")),
        "prune_missing",
        default=False,
    )

    documents = payload.get("documents")
    if not isinstance(documents, list) or not documents:
        raise IngestionError(400, "documents must be a non-empty list")
    if len(documents) > MAX_SYNC_DOCUMENTS:
        raise IngestionError(413, f"source sync accepts at most {MAX_SYNC_DOCUMENTS} documents")

    replace = bool(payload.get("replace", True))
    ingested = []
    parser_warnings: list[str] = []
    replaced_count = 0
    chunk_count = 0
    acl_drift_count = 0
    acl_drift_doc_ids: list[str] = []

    for index, item in enumerate(documents, start=1):
        if not isinstance(item, dict):
            raise IngestionError(400, "each synced document must be an object")
        external_id = _metadata_string(item, "external_id", str(item.get("id") or f"source-{index}"), max_length=240)
        stable_doc_id = str(item.get("id") or f"{connector_scheme}-{_slug(external_id)}").strip()
        acl_record = _source_acl_record(acl_snapshot, external_id, item.get("id"))
        allowed_roles = item.get("allowed_roles")
        allowed_roles_source = "document_payload"
        source_acl_version = ""
        source_acl_permission_id = ""
        source_acl_principal_count = 0
        if acl_record is not None:
            allowed_roles = acl_record.get("allowed_roles")
            allowed_roles_source = "connector_acl_snapshot"
            source_acl_version = acl_snapshot["version"]
            source_acl_permission_id = _metadata_string(
                acl_record,
                "permission_id",
                f"{acl_source}:{external_id}",
                max_length=240,
            )
            source_acl_principal_count = _metadata_int(acl_record, "principal_count", 0)
        source_url = str(
            item.get("source_url")
            or f"{connector_scheme}://{actor['tenant_id']}/{_slug(external_id)}"
        ).strip()
        document = {
            **item,
            "id": stable_doc_id,
            "tenant_id": actor["tenant_id"],
            "source_url": source_url,
            "source_connector": connector_name,
            "external_id": external_id,
            "acl_source": acl_source,
            "sync_cursor": connector_cursor,
            "allowed_roles": allowed_roles,
            "allowed_roles_source": allowed_roles_source,
            "source_acl_version": source_acl_version,
            "source_acl_permission_id": source_acl_permission_id,
            "source_acl_principal_count": source_acl_principal_count,
            "version": str(item.get("version") or connector_cursor or _utc_date()),
        }
        result = ingest_document(
            repo,
            {
                "user_id": actor_id,
                "replace": replace,
                "document": document,
            },
        )
        ingested.append(result["document"])
        replaced_count += 1 if result["ingestion"].get("replaced_existing") else 0
        chunk_count += int(result.get("chunk_count", 0))
        parser_warnings.extend(result["ingestion"]["parser"].get("warnings", []))
        drift = result["ingestion"]["source"].get("acl_role_drift", {})
        if drift.get("changed"):
            acl_drift_count += 1
            acl_drift_doc_ids.append(result["document"]["id"])

    pruned_doc_ids: list[str] = []
    if prune_missing:
        current_doc_ids = {document["id"] for document in ingested}
        existing_connector_docs = repo.list_documents_by_connector(actor["tenant_id"], connector_name)
        pruned_doc_ids = sorted(
            document["id"]
            for document in existing_connector_docs
            if document.get("id") not in current_doc_ids
        )
        repo.delete_documents(actor["tenant_id"], pruned_doc_ids)

    repo.insert_audit(
        actor_id,
        "source_sync_completed",
        {
            "connector": connector_name,
            "cursor": connector_cursor,
            "acl_source": acl_source,
            "document_count": len(ingested),
            "chunk_count": chunk_count,
            "replaced_count": replaced_count,
            "acl_snapshot_version": acl_snapshot["version"] if acl_snapshot else "",
            "acl_drift_count": acl_drift_count,
            "acl_drift_doc_ids": acl_drift_doc_ids,
            "prune_missing": prune_missing,
            "pruned_count": len(pruned_doc_ids),
            "pruned_doc_ids": pruned_doc_ids,
            "doc_ids": [item["id"] for item in ingested],
            "parser_warnings": sorted(set(parser_warnings)),
        },
    )

    return {
        "sync": {
            "actor_user_id": actor_id,
            "connector": connector_name,
            "cursor": connector_cursor,
            "acl_source": acl_source,
            "document_count": len(ingested),
            "chunk_count": chunk_count,
            "replaced_count": replaced_count,
            "acl_snapshot_version": acl_snapshot["version"] if acl_snapshot else "",
            "acl_drift_count": acl_drift_count,
            "acl_drift_doc_ids": acl_drift_doc_ids,
            "prune_missing": prune_missing,
            "pruned_count": len(pruned_doc_ids),
            "pruned_doc_ids": pruned_doc_ids,
            "parser_warnings": sorted(set(parser_warnings)),
        },
        "documents": ingested,
    }
