from __future__ import annotations

from .ingestion import IngestionError
from .repositories import KnowledgeRepository


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
    }


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


def _connector_row(connector: str, jobs: list[dict]) -> dict:
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
        "success_count": len(successes),
        "dead_letter_count": len(dead_letters),
        "job_count": len(jobs),
        "last_error_status": latest_error.get("status") if latest_error else None,
        "last_error_retryable": latest_error.get("retryable") if latest_error else None,
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

    connectors = [_connector_row(connector, items) for connector, items in sorted(grouped.items())]
    return {
        "connectors": connectors,
        "connector_count": len(connectors),
        "job_window": len(jobs),
        "status_source": "ingestion_jobs",
    }
