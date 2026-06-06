from __future__ import annotations

import hashlib
import json
import re
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from .ingestion import IngestionError
from .ingestion_jobs import submit_ingestion_job
from .repositories import KnowledgeRepository
from .source_parsing import SUPPORTED_MIME_TYPES
from .time_utils import utc_now


ROOT = Path(__file__).resolve().parents[2]
BUNDLE_ROOT = ROOT / "data" / "source_bundles"
MAX_BUNDLE_DOCUMENTS = 10
MAX_BUNDLE_FILE_BYTES = 80_000
BUNDLE_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{1,80}$")
SLUG_RE = re.compile(r"[^a-z0-9]+")
EXTENSION_MIME_TYPES = {
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".markdown": "text/markdown",
    ".csv": "text/csv",
    ".html": "text/html",
    ".json": "application/json",
}


def _string(value: object, field: str, *, max_length: int = 180) -> str:
    if not isinstance(value, str):
        raise IngestionError(400, f"{field} must be a string")
    normalized = value.strip()
    if not normalized:
        raise IngestionError(400, f"{field} is required")
    if len(normalized) > max_length:
        raise IngestionError(413, f"{field} exceeds {max_length} characters")
    return normalized


def _stable_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _slug(value: str) -> str:
    return SLUG_RE.sub("-", value.lower()).strip("-")[:96] or "source"


def _bundle_name(value: object) -> str:
    bundle = _string(value, "bundle", max_length=80)
    if not BUNDLE_NAME_RE.fullmatch(bundle):
        raise IngestionError(400, "bundle contains unsupported characters")
    return bundle


def _read_json(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise IngestionError(404, "Unknown source bundle") from exc
    except JSONDecodeError as exc:
        raise IngestionError(400, "Source bundle manifest is not valid JSON") from exc
    if not isinstance(payload, dict):
        raise IngestionError(400, "Source bundle manifest must be an object")
    return payload


def _safe_document_path(bundle_dir: Path, raw_path: object) -> tuple[str, Path]:
    relative_path = _string(raw_path, "documents[].path", max_length=240).replace("\\", "/")
    candidate = Path(relative_path)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise IngestionError(400, "bundle document path must stay inside the source bundle")
    resolved = (bundle_dir / candidate).resolve()
    if not resolved.is_relative_to(bundle_dir.resolve()):
        raise IngestionError(400, "bundle document path must stay inside the source bundle")
    if not resolved.is_file():
        raise IngestionError(404, f"Source bundle document not found: {relative_path}")
    return relative_path, resolved


def _read_text_file(path: Path) -> str:
    payload = path.read_bytes()
    if len(payload) > MAX_BUNDLE_FILE_BYTES:
        raise IngestionError(413, f"Source bundle document exceeds {MAX_BUNDLE_FILE_BYTES} bytes")
    try:
        return payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise IngestionError(415, "Source bundle documents must be UTF-8 text") from exc


def _source_mime(item: dict, path: Path) -> str:
    source_mime = str(item.get("source_mime") or EXTENSION_MIME_TYPES.get(path.suffix.lower(), "")).strip().lower()
    if source_mime not in SUPPORTED_MIME_TYPES:
        raise IngestionError(415, f"Unsupported source_mime for source bundle document: {source_mime}")
    return source_mime


def _principal_count(roles: object, groups: object) -> int:
    role_count = len(roles) if isinstance(roles, list) else 0
    group_count = len(groups) if isinstance(groups, list) else 0
    return role_count + group_count


def _source_payload(actor_id: str, bundle: str, manifest: dict, bundle_dir: Path, cursor: str, prune_missing: bool) -> dict:
    manifest_bundle = str(manifest.get("bundle") or bundle).strip()
    if manifest_bundle != bundle:
        raise IngestionError(400, "Source bundle manifest bundle name does not match request")
    documents = manifest.get("documents")
    if not isinstance(documents, list) or not documents:
        raise IngestionError(400, "Source bundle manifest documents must be a non-empty list")
    if len(documents) > MAX_BUNDLE_DOCUMENTS:
        raise IngestionError(413, f"Source bundle accepts at most {MAX_BUNDLE_DOCUMENTS} documents")

    connector_name = str(manifest.get("connector_name") or "source-bundle").strip() or "source-bundle"
    acl_source = str(manifest.get("acl_source") or f"source-bundle:{bundle}:manifest-acl").strip()
    acl_version = str(manifest.get("acl_snapshot_version") or f"source-bundle:{bundle}:{cursor}").strip()
    source_documents: list[dict] = []
    acl_documents: dict[str, dict] = {}

    for index, item in enumerate(documents, start=1):
        if not isinstance(item, dict):
            raise IngestionError(400, "each source bundle document must be an object")
        relative_path, document_path = _safe_document_path(bundle_dir, item.get("path"))
        body = _read_text_file(document_path)
        external_id = str(item.get("external_id") or f"source-bundle:{bundle}:{relative_path}").strip()
        if not external_id:
            raise IngestionError(400, "source bundle document external_id is required")
        title = _string(item.get("title"), "documents[].title", max_length=180)
        allowed_roles = item.get("allowed_roles")
        allowed_groups = item.get("allowed_groups", [])
        source_documents.append(
            {
                "id": str(item.get("id") or f"source-bundle-{_slug(bundle)}-{_slug(relative_path)}").strip(),
                "external_id": external_id,
                "title": title,
                "body": body,
                "classification": str(item.get("classification") or "internal").strip().lower(),
                "allowed_roles": allowed_roles,
                "allowed_groups": allowed_groups,
                "source_mime": _source_mime(item, document_path),
                "source_url": str(item.get("source_url") or f"source-bundle://{bundle}/{relative_path}").strip(),
                "updated_at": str(item.get("updated_at") or cursor).strip(),
                "version": str(item.get("version") or cursor).strip(),
                "source_lifecycle_state": str(item.get("source_lifecycle_state") or "active").strip(),
            }
        )
        acl_documents[external_id] = {
            "allowed_roles": allowed_roles,
            "allowed_groups": allowed_groups,
            "permission_id": str(item.get("permission_id") or f"source-bundle:{bundle}:doc-{index}:visibility").strip(),
            "principal_count": _principal_count(allowed_roles, allowed_groups),
        }

    return {
        "user_id": actor_id,
        "replace": True,
        "prune_missing": prune_missing,
        "connector": {
            "name": connector_name,
            "cursor": cursor,
            "acl_source": acl_source,
            "acl_snapshot": {
                "version": acl_version,
                "documents": acl_documents,
            },
        },
        "documents": source_documents,
    }


def sync_source_bundle(repository: KnowledgeRepository, payload: dict) -> dict:
    actor_id = _string(payload.get("user_id"), "user_id", max_length=80)
    actor = repository.get_user(actor_id)
    if not actor:
        raise IngestionError(404, f"Unknown user_id: {actor_id}")
    if actor["role"] != "admin":
        raise IngestionError(403, "Only admin users can sync source bundles.")

    bundle = _bundle_name(payload.get("bundle"))
    bundle_dir = (BUNDLE_ROOT / bundle).resolve()
    if not bundle_dir.is_relative_to(BUNDLE_ROOT.resolve()):
        raise IngestionError(400, "bundle contains unsupported characters")
    manifest_path = bundle_dir / "manifest.json"
    manifest = _read_json(manifest_path)
    cursor = str(payload.get("cursor") or manifest.get("cursor") or utc_now()).strip()
    prune_missing = bool(payload.get("prune_missing", manifest.get("prune_missing", False)))
    source_payload = _source_payload(actor_id, bundle, manifest, bundle_dir, cursor, prune_missing)
    idempotency_key = str(payload.get("idempotency_key") or "").strip()
    if not idempotency_key:
        idempotency_key = f"source-bundle:{bundle}:{cursor}:{_stable_hash(source_payload)[:16]}"

    job_response = submit_ingestion_job(
        repository,
        {
            "user_id": actor_id,
            "type": "source_sync",
            "idempotency_key": idempotency_key,
            "payload": source_payload,
        },
    )
    job = job_response.get("job", {})
    sync = job_response.get("result", {}).get("sync", {}) if isinstance(job_response.get("result"), dict) else {}
    repository.insert_audit(
        actor_id,
        "source_bundle_synced",
        {
            "bundle": bundle,
            "connector": source_payload["connector"]["name"],
            "cursor": cursor,
            "document_count": len(source_payload["documents"]),
            "job_id": job.get("id"),
            "job_status": job.get("status"),
            "idempotency_key": idempotency_key,
            "idempotency_replayed": bool(job_response.get("idempotency_replayed")),
            "source_payload_sha256": _stable_hash(source_payload),
        },
    )
    return {
        "source_bundle": {
            "bundle": bundle,
            "connector": source_payload["connector"]["name"],
            "cursor": cursor,
            "document_count": len(source_payload["documents"]),
            "synced_document_count": sync.get("document_count", 0),
            "manifest": "manifest.json",
            "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
            "source_payload_sha256": _stable_hash(source_payload),
        },
        **job_response,
    }
