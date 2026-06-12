from __future__ import annotations

from .ingestion import IngestionError
from .repositories import KnowledgeRepository
from .source_lifecycle import ACTIVE_SOURCE_STATE, source_lifecycle_state


def _safe_int(value: object, default: int = 0) -> int:
    if isinstance(value, bool):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _job_connector(job: dict) -> str:
    result = job.get("result") if isinstance(job.get("result"), dict) else {}
    input_summary = job.get("input") if isinstance(job.get("input"), dict) else {}
    connector = result.get("connector") or input_summary.get("connector") or job.get("type")
    return str(connector or "unknown").strip() or "unknown"


def _job_cursor(job: dict) -> str | None:
    result = job.get("result") if isinstance(job.get("result"), dict) else {}
    input_summary = job.get("input") if isinstance(job.get("input"), dict) else {}
    cursor = result.get("cursor") or input_summary.get("cursor")
    return str(cursor).strip() if cursor else None


def _job_counts(job: dict) -> dict:
    result = job.get("result") if isinstance(job.get("result"), dict) else {}
    input_summary = job.get("input") if isinstance(job.get("input"), dict) else {}
    return {
        "document_count": _safe_int(result.get("document_count", input_summary.get("document_count", 0))),
        "chunk_count": _safe_int(result.get("chunk_count", 0)),
        "acl_drift_count": _safe_int(result.get("acl_drift_count", 0)),
        "pruned_count": _safe_int(result.get("pruned_count", 0)),
    }


def _strings(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return sorted({str(item).strip() for item in value if str(item).strip()})


def _document_inventory(documents: list[dict], latest_counts: dict) -> dict:
    lifecycle_counts: dict[str, int] = {}
    classification_counts: dict[str, int] = {}
    warning_names: set[str] = set()
    warning_doc_count = 0
    warning_count = 0

    for document in documents:
        lifecycle = source_lifecycle_state(document)
        lifecycle_counts[lifecycle] = lifecycle_counts.get(lifecycle, 0) + 1
        classification = str(document.get("classification") or "unknown")
        classification_counts[classification] = classification_counts.get(classification, 0) + 1
        warnings = _strings(document.get("parser_warnings"))
        if warnings:
            warning_doc_count += 1
            warning_count += len(warnings)
            warning_names.update(warnings)

    indexed_document_count = len(documents)
    active_document_count = lifecycle_counts.get(ACTIVE_SOURCE_STATE, 0)
    return {
        "indexed_document_count": indexed_document_count,
        "active_document_count": active_document_count,
        "filtered_document_count": indexed_document_count - active_document_count,
        "index_matches_latest_job": indexed_document_count == latest_counts["document_count"],
        "index_health": _index_health(indexed_document_count, warning_count),
        "source_lifecycle_counts": lifecycle_counts,
        "classification_counts": classification_counts,
        "parser_warning_count": warning_count,
        "parser_warning_document_count": warning_doc_count,
        "parser_warnings": sorted(warning_names),
        "latest_indexed_updated_at": max((str(doc.get("updated_at") or "") for doc in documents), default=""),
        "source_mime_types": sorted({str(doc.get("source_mime") or "unknown") for doc in documents}),
        "acl_sources": sorted({str(doc.get("acl_source") or "") for doc in documents if doc.get("acl_source")}),
        "allowed_roles_sources": sorted(
            {str(doc.get("allowed_roles_source") or "") for doc in documents if doc.get("allowed_roles_source")}
        ),
        "source_acl_versions": sorted(
            {str(doc.get("source_acl_version") or "") for doc in documents if doc.get("source_acl_version")}
        ),
        "document_ids": sorted(str(doc.get("id") or "") for doc in documents if doc.get("id")),
    }


def _index_health(indexed_document_count: int, parser_warning_count: int) -> str:
    if indexed_document_count == 0:
        return "empty"
    if parser_warning_count:
        return "parser_warnings"
    return "indexed"


def _job_sort_key(job: dict) -> tuple[str, str, str, str]:
    return (
        str(job.get("updated_at") or ""),
        str(job.get("created_at") or ""),
        _job_cursor(job) or "",
        str(job.get("id") or ""),
    )


def _health(latest_status: str, dead_letter_count: int) -> str:
    if latest_status in {"queued", "running"}:
        return "running"
    if latest_status == "dead_lettered":
        return "needs_attention"
    if latest_status == "succeeded" and dead_letter_count:
        return "recovered"
    if latest_status == "succeeded":
        return "healthy"
    return "unknown"


def _connector_row(connector: str, jobs: list[dict], documents: list[dict]) -> dict:
    latest = jobs[0]
    latest_status = str(latest.get("status") or "unknown")
    dead_letters = [job for job in jobs if job.get("status") == "dead_lettered"]
    successes = [job for job in jobs if job.get("status") == "succeeded"]
    latest_counts = _job_counts(latest)
    latest_error = latest.get("error") if isinstance(latest.get("error"), dict) else None
    return {
        "connector": connector,
        "health": _health(latest_status, len(dead_letters)),
        "latest_job_id": latest.get("id"),
        "latest_job_status": latest_status,
        "latest_job_type": latest.get("type"),
        "latest_cursor": _job_cursor(latest),
        "latest_updated_at": latest.get("updated_at"),
        "document_count": latest_counts["document_count"],
        "chunk_count": latest_counts["chunk_count"],
        "acl_drift_count": latest_counts["acl_drift_count"],
        "pruned_count": latest_counts["pruned_count"],
        "success_count": len(successes),
        "dead_letter_count": len(dead_letters),
        "job_count": len(jobs),
        "last_error_status": latest_error.get("status") if latest_error else None,
        "last_error_retryable": latest_error.get("retryable") if latest_error else None,
        **_document_inventory(documents, latest_counts),
    }


def list_connector_status(repo: KnowledgeRepository, user_id: str, limit: int = 100) -> dict:
    actor = repo.get_user(user_id)
    if not actor:
        raise IngestionError(404, f"Unknown user_id: {user_id}")
    if actor["role"] != "admin":
        raise IngestionError(403, "Only admin users can view connector status.")

    safe_limit = max(1, min(_safe_int(limit, 100), 100))
    jobs = sorted(
        repo.list_ingestion_jobs(limit=safe_limit),
        key=_job_sort_key,
        reverse=True,
    )
    grouped: dict[str, list[dict]] = {}
    for job in jobs:
        if job.get("type") != "source_sync":
            continue
        grouped.setdefault(_job_connector(job), []).append(job)

    connectors = [
        _connector_row(
            connector,
            items,
            repo.list_documents_by_connector(actor["tenant_id"], connector),
        )
        for connector, items in sorted(grouped.items())
    ]
    return {
        "connectors": connectors,
        "connector_count": len(connectors),
        "job_window": len(jobs),
        "status_source": "ingestion_jobs+indexed_documents",
    }
