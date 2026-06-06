from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any

from .ingestion import IngestionError, sync_source_batch
from .repositories import KnowledgeRepository
from .time_utils import utc_now


SUPPORTED_JOB_TYPES = {"source_sync"}


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


def _job_id(actor: dict, job_type: str, idempotency_key: str) -> str:
    stable = hashlib.sha256(
        f"{actor['tenant_id']}\n{actor['id']}\n{job_type}\n{idempotency_key}".encode("utf-8")
    ).hexdigest()[:12]
    return f"ingest-job-{stable}"


def _document_summary(document: dict) -> dict:
    raw_body = document.get("body", document.get("content", ""))
    body = raw_body if isinstance(raw_body, str) else json.dumps(raw_body, sort_keys=True)
    return {
        "id": document.get("id"),
        "external_id": document.get("external_id"),
        "title": document.get("title"),
        "classification": document.get("classification", "internal"),
        "allowed_groups": document.get("allowed_groups", []),
        "source_mime": document.get("source_mime", "text/plain"),
        "body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
        "body_characters": len(body),
    }


def _source_sync_input_summary(payload: dict) -> dict:
    connector = payload.get("connector", {}) if isinstance(payload.get("connector", {}), dict) else {}
    documents = payload.get("documents", [])
    acl_snapshot = connector.get("acl_snapshot", {}) if isinstance(connector.get("acl_snapshot"), dict) else {}
    acl_documents = acl_snapshot.get("documents", {}) if isinstance(acl_snapshot.get("documents"), dict) else {}
    return {
        "connector": connector.get("name"),
        "cursor": connector.get("cursor"),
        "acl_source": connector.get("acl_source"),
        "acl_snapshot_version": acl_snapshot.get("version"),
        "acl_snapshot_document_count": len(acl_documents),
        "replace": bool(payload.get("replace", True)),
        "prune_missing": payload.get("prune_missing") is True or connector.get("prune_missing") is True,
        "document_count": len(documents) if isinstance(documents, list) else 0,
        "documents": [_document_summary(item) for item in documents if isinstance(item, dict)],
    }


def _result_summary(result: dict) -> dict:
    sync = result.get("sync", {}) if isinstance(result.get("sync"), dict) else {}
    documents = result.get("documents", []) if isinstance(result.get("documents"), list) else []
    return {
        "connector": sync.get("connector"),
        "cursor": sync.get("cursor"),
        "acl_snapshot_version": sync.get("acl_snapshot_version"),
        "document_count": sync.get("document_count", 0),
        "chunk_count": sync.get("chunk_count", 0),
        "replaced_count": sync.get("replaced_count", 0),
        "acl_drift_count": sync.get("acl_drift_count", 0),
        "acl_drift_doc_ids": sync.get("acl_drift_doc_ids", []),
        "prune_missing": sync.get("prune_missing", False),
        "pruned_count": sync.get("pruned_count", 0),
        "pruned_doc_ids": sync.get("pruned_doc_ids", []),
        "doc_ids": [document.get("id") for document in documents if isinstance(document, dict)],
    }


def _job_response(job: dict, *, result: dict | None = None, idempotency_replayed: bool = False) -> dict:
    response = {
        "job": job,
        "idempotency_replayed": idempotency_replayed,
    }
    if result is not None:
        response["result"] = result
    return response


def submit_ingestion_job(repo: KnowledgeRepository, payload: dict) -> dict:
    actor_id = _string(payload.get("user_id"), "user_id", max_length=80)
    actor = repo.get_user(actor_id)
    if not actor:
        raise IngestionError(404, f"Unknown user_id: {actor_id}")
    if actor["role"] != "admin":
        raise IngestionError(403, "Only admin users can submit ingestion jobs.")

    job_type = _string(payload.get("type", "source_sync"), "type", max_length=80)
    if job_type not in SUPPORTED_JOB_TYPES:
        raise IngestionError(400, f"Unsupported ingestion job type: {job_type}")

    idempotency_key = _string(payload.get("idempotency_key"), "idempotency_key", max_length=180)
    existing = repo.get_ingestion_job_by_key(idempotency_key)
    if existing:
        return _job_response(existing, idempotency_replayed=True)

    job_payload = payload.get("payload")
    if not isinstance(job_payload, dict):
        raise IngestionError(400, "payload must be an object")
    retry_of_job_id = str(payload.get("retry_of_job_id") or "").strip()
    if retry_of_job_id:
        retry_parent = repo.get_ingestion_job(retry_of_job_id)
        if not retry_parent:
            raise IngestionError(404, f"Unknown retry_of_job_id: {retry_of_job_id}")
        if retry_parent.get("status") != "dead_lettered":
            raise IngestionError(409, "Only dead-lettered ingestion jobs can be retried.")

    now = utc_now()
    job = {
        "id": _job_id(actor, job_type, idempotency_key),
        "type": job_type,
        "status": "queued",
        "user_id": actor_id,
        "tenant_id": actor["tenant_id"],
        "idempotency_key": idempotency_key,
        "retry_of_job_id": retry_of_job_id,
        "attempts": 0,
        "created_at": now,
        "updated_at": now,
        "started_at": None,
        "finished_at": None,
        "payload_sha256": _stable_hash(job_payload),
        "input": _source_sync_input_summary(job_payload),
        "result": None,
        "error": None,
    }
    repo.record_ingestion_job(job)

    job["status"] = "running"
    job["attempts"] = 1
    job["started_at"] = utc_now()
    job["updated_at"] = job["started_at"]
    repo.record_ingestion_job(job)

    worker_payload = deepcopy(job_payload)
    worker_payload["user_id"] = actor_id
    try:
        result = sync_source_batch(repo, worker_payload)
    except IngestionError as exc:
        finished_at = utc_now()
        job["status"] = "dead_lettered"
        job["updated_at"] = finished_at
        job["finished_at"] = finished_at
        job["error"] = {
            "status": exc.status,
            "message": exc.message,
            "retryable": exc.status in {400, 403, 409, 413, 415},
            "dead_letter_reason": "worker_validation_failed",
        }
        repo.record_ingestion_job(job)
        repo.insert_audit(
            actor_id,
            "ingestion_job_dead_lettered",
            {
                "job_id": job["id"],
                "type": job_type,
                "idempotency_key": idempotency_key,
                "retry_of_job_id": retry_of_job_id,
                "error_status": exc.status,
                "error_message": exc.message,
                "retryable": job["error"]["retryable"],
            },
        )
        return _job_response(job)

    finished_at = utc_now()
    job["status"] = "succeeded"
    job["updated_at"] = finished_at
    job["finished_at"] = finished_at
    job["result"] = _result_summary(result)
    repo.record_ingestion_job(job)
    repo.insert_audit(
        actor_id,
        "ingestion_job_completed",
        {
            "job_id": job["id"],
            "type": job_type,
            "idempotency_key": idempotency_key,
            "retry_of_job_id": retry_of_job_id,
            **job["result"],
        },
    )
    return _job_response(job, result=result)


def list_ingestion_jobs(repo: KnowledgeRepository, user_id: str, limit: int = 25) -> dict:
    actor = repo.get_user(user_id)
    if not actor:
        raise IngestionError(404, f"Unknown user_id: {user_id}")
    if actor["role"] != "admin":
        raise IngestionError(403, "Only admin users can list ingestion jobs.")
    safe_limit = max(1, min(int(limit), 100))
    return {"jobs": repo.list_ingestion_jobs(limit=safe_limit)}
