from __future__ import annotations

from .ingestion import IngestionError
from .repositories import KnowledgeRepository
from .source_lifecycle import ACTIVE_SOURCE_STATE, source_lifecycle_state
from .source_parsing import PARSER_QUALITY_SCHEMA_VERSION
from .source_scanning import SOURCE_SCAN_SCHEMA_VERSION


SOURCE_QUALITY_SCHEMA_VERSION = "source_quality_report_v1"


def _safe_int(value: object, default: int = 0) -> int:
    if isinstance(value, bool):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _strings(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return sorted({str(item).strip() for item in value if str(item).strip()})


def _count_by(items: list[dict], key: str, default: str = "unknown") -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        value = str(item.get(key) or default).strip() or default
        counts[value] = counts.get(value, 0) + 1
    return counts


def _quality(document: dict) -> dict:
    metadata = document.get("parser_metadata")
    if not isinstance(metadata, dict):
        return {}
    quality = metadata.get("quality")
    return quality if isinstance(quality, dict) else {}


def _parser_quality_schema(document: dict) -> str:
    return str(_quality(document).get("schema_version") or "missing")


def _source_scan(document: dict) -> dict:
    scan = document.get("source_scan")
    return scan if isinstance(scan, dict) else {}


def _source_scan_schema(document: dict) -> str:
    return str(_source_scan(document).get("schema_version") or "missing")


def _source_scan_categories(document: dict) -> list[str]:
    return _strings(_source_scan(document).get("finding_categories"))


def _source_connector(document: dict) -> str:
    return str(document.get("source_connector") or "manual").strip() or "manual"


def _requires_acl_snapshot(document: dict) -> bool:
    connector = _source_connector(document)
    return connector not in {"manual", "file-upload"}


def _risk_flags(document: dict) -> list[str]:
    flags: list[str] = []
    warnings = _strings(document.get("parser_warnings"))
    quality = _quality(document)
    lifecycle = source_lifecycle_state(document)
    if warnings:
        flags.append("parser_warnings")
    if _parser_quality_schema(document) != PARSER_QUALITY_SCHEMA_VERSION:
        flags.append("parser_quality_missing")
    scan = _source_scan(document)
    if _source_scan_schema(document) != SOURCE_SCAN_SCHEMA_VERSION:
        flags.append("source_scan_missing")
    if scan.get("review_required") is True:
        flags.append("source_scan_review_required")
    if lifecycle != ACTIVE_SOURCE_STATE:
        flags.append("non_active_source")
    if not str(document.get("source_hash") or "").strip():
        flags.append("source_hash_missing")
    if _requires_acl_snapshot(document) and not str(document.get("source_acl_version") or "").strip():
        flags.append("connector_acl_version_missing")
    if _safe_int(quality.get("normalized_non_empty_line_count"), 0) == 0:
        flags.append("empty_normalized_text")
    return flags


def _source_row(document: dict) -> dict:
    quality = _quality(document)
    source_scan = _source_scan(document)
    warnings = _strings(document.get("parser_warnings"))
    flags = _risk_flags(document)
    return {
        "id": document.get("id"),
        "title": document.get("title"),
        "source_connector": _source_connector(document),
        "source_mime": document.get("source_mime") or "unknown",
        "classification": document.get("classification") or "unknown",
        "source_lifecycle_state": source_lifecycle_state(document),
        "parser_name": document.get("parser_name") or quality.get("parser_name") or "unknown",
        "parser_quality_schema": _parser_quality_schema(document),
        "normalized_characters": _safe_int(quality.get("normalized_character_count")),
        "normalized_non_empty_line_count": _safe_int(quality.get("normalized_non_empty_line_count")),
        "section_count": _safe_int(quality.get("section_count")),
        "table_like_line_count": _safe_int(quality.get("table_like_line_count")),
        "parser_warning_count": len(warnings),
        "parser_warnings": warnings,
        "source_scan_schema": _source_scan_schema(document),
        "source_scan_status": source_scan.get("status") or "missing",
        "source_scan_severity": source_scan.get("severity") or "unknown",
        "source_scan_review_required": bool(source_scan.get("review_required")),
        "source_scan_finding_categories": _source_scan_categories(document),
        "acl_source": document.get("acl_source") or "",
        "allowed_roles_source": document.get("allowed_roles_source") or "",
        "allowed_groups": _strings(document.get("allowed_groups")),
        "source_acl_version": document.get("source_acl_version") or "",
        "source_acl_principal_count": _safe_int(document.get("source_acl_principal_count")),
        "source_hash_prefix": str(document.get("source_hash") or "")[:12],
        "updated_at": document.get("updated_at") or "",
        "attention_required": bool(flags),
        "risk_flags": flags,
    }


def _quality_schema_counts(documents: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for document in documents:
        schema = _parser_quality_schema(document)
        counts[schema] = counts.get(schema, 0) + 1
    return counts


def _source_scan_schema_counts(documents: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for document in documents:
        schema = _source_scan_schema(document)
        counts[schema] = counts.get(schema, 0) + 1
    return counts


def _source_scan_finding_counts(documents: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for document in documents:
        scan = _source_scan(document)
        finding_counts = scan.get("finding_counts")
        if not isinstance(finding_counts, dict):
            continue
        for category, value in finding_counts.items():
            count = _safe_int(value)
            if count > 0:
                key = str(category)
                counts[key] = counts.get(key, 0) + count
    return dict(sorted(counts.items()))


def _warning_counts(documents: list[dict]) -> tuple[int, int]:
    warning_count = 0
    warning_docs = 0
    for document in documents:
        warnings = _strings(document.get("parser_warnings"))
        if warnings:
            warning_docs += 1
            warning_count += len(warnings)
    return warning_count, warning_docs


def list_source_quality(repo: KnowledgeRepository, user_id: str, limit: int = 100) -> dict:
    actor = repo.get_user(user_id)
    if not actor:
        raise IngestionError(404, f"Unknown user_id: {user_id}")
    if actor["role"] != "admin":
        raise IngestionError(403, "Only admin users can view source quality.")

    safe_limit = max(1, min(_safe_int(limit, 100), 100))
    documents = sorted(
        repo.list_documents_for_tenant(actor["tenant_id"]),
        key=lambda item: (str(item.get("updated_at") or ""), str(item.get("id") or "")),
        reverse=True,
    )
    rows = [_source_row(document) for document in documents]
    warning_count, warning_document_count = _warning_counts(documents)
    active_count = sum(1 for document in documents if source_lifecycle_state(document) == ACTIVE_SOURCE_STATE)
    attention_required_count = sum(1 for row in rows if row["attention_required"])
    acl_snapshot_coverage_count = sum(1 for document in documents if str(document.get("source_acl_version") or "").strip())
    return {
        "source_quality": {
            "schema_version": SOURCE_QUALITY_SCHEMA_VERSION,
            "actor_user_id": actor["id"],
            "tenant_id": actor["tenant_id"],
            "document_count": len(documents),
            "active_document_count": active_count,
            "filtered_document_count": len(documents) - active_count,
            "attention_required_count": attention_required_count,
            "parser_warning_count": warning_count,
            "parser_warning_document_count": warning_document_count,
            "parser_quality_schema_counts": _quality_schema_counts(documents),
            "source_scan_schema_counts": _source_scan_schema_counts(documents),
            "source_scan_review_required_count": sum(1 for document in documents if _source_scan(document).get("review_required") is True),
            "source_scan_finding_counts": _source_scan_finding_counts(documents),
            "source_mime_counts": _count_by(documents, "source_mime"),
            "connector_counts": _count_by(documents, "source_connector", "manual"),
            "lifecycle_counts": {
                state: sum(1 for document in documents if source_lifecycle_state(document) == state)
                for state in sorted({source_lifecycle_state(document) for document in documents})
            },
            "classification_counts": _count_by(documents, "classification"),
            "acl_snapshot_coverage_count": acl_snapshot_coverage_count,
            "raw_bodies_returned": False,
            "documents": rows[:safe_limit],
        }
    }
