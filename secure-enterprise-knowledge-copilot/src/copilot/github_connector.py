from __future__ import annotations

import hashlib
import json
import os
import re
import urllib.parse
import urllib.request
from json import JSONDecodeError
from typing import Any

from .ingestion import IngestionError
from .ingestion_jobs import submit_ingestion_job
from .repositories import KnowledgeRepository
from .time_utils import utc_now


MAX_GITHUB_ITEMS = 10
OWNER_REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+$")


def _string(value: object, field: str, *, max_length: int = 180) -> str:
    if not isinstance(value, str):
        raise IngestionError(400, f"{field} must be a string")
    normalized = value.strip()
    if not normalized:
        raise IngestionError(400, f"{field} is required")
    if len(normalized) > max_length:
        raise IngestionError(413, f"{field} exceeds {max_length} characters")
    return normalized


def _github_name(value: object, field: str, *, max_length: int = 100) -> str:
    name = _string(value, field, max_length=max_length)
    if not OWNER_REPO_RE.match(name):
        raise IngestionError(400, f"{field} contains unsupported characters")
    return name


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:96] or "github-item"


def _stable_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _int(value: object, field: str, *, default: int, minimum: int, maximum: int) -> int:
    if value is None:
        return default
    if isinstance(value, bool):
        raise IngestionError(400, f"{field} must be an integer")
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise IngestionError(400, f"{field} must be an integer") from None
    return max(minimum, min(parsed, maximum))


def _records_from_fixture(payload: dict) -> list[dict]:
    records = payload.get("records")
    if not isinstance(records, list) or not records:
        raise IngestionError(400, "records must be a non-empty list for fixture GitHub sync")
    if len(records) > MAX_GITHUB_ITEMS:
        raise IngestionError(413, f"GitHub connector accepts at most {MAX_GITHUB_ITEMS} records per sync")
    normalized = []
    for record in records:
        if not isinstance(record, dict):
            raise IngestionError(400, "each GitHub record must be an object")
        normalized.append(record)
    return normalized


def _fetch_json(url: str, token: str | None) -> list[dict]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "fde-ai-systems-portfolio-github-connector",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            raw = response.read().decode("utf-8")
    except OSError as exc:
        raise IngestionError(502, f"GitHub connector fetch failed: {exc.__class__.__name__}") from exc
    try:
        data = json.loads(raw)
    except JSONDecodeError as exc:
        raise IngestionError(502, "GitHub connector returned invalid JSON") from exc
    if not isinstance(data, list):
        raise IngestionError(502, "GitHub connector expected a list response")
    return [item for item in data if isinstance(item, dict)]


def _records_from_live_github(owner: str, repo_name: str, payload: dict) -> list[dict]:
    state = str(payload.get("state") or "open").strip().lower()
    if state not in {"open", "closed", "all"}:
        raise IngestionError(400, "state must be open, closed, or all")
    include = payload.get("include") or ["issues", "pulls"]
    if not isinstance(include, list) or not include:
        raise IngestionError(400, "include must be a non-empty list")
    include_set = {str(item).strip().lower() for item in include}
    if not include_set.issubset({"issues", "pulls"}):
        raise IngestionError(400, "include supports issues and pulls")

    per_page = _int(payload.get("per_page"), "per_page", default=MAX_GITHUB_ITEMS, minimum=1, maximum=MAX_GITHUB_ITEMS)
    base = f"https://api.github.com/repos/{urllib.parse.quote(owner)}/{urllib.parse.quote(repo_name)}"
    token = os.environ.get("GITHUB_CONNECTOR_TOKEN") or os.environ.get("GITHUB_TOKEN")
    records: list[dict] = []
    if "issues" in include_set:
        query = urllib.parse.urlencode({"state": state, "sort": "updated", "direction": "desc", "per_page": per_page})
        records.extend(
            item for item in _fetch_json(f"{base}/issues?{query}", token) if not isinstance(item.get("pull_request"), dict)
        )
    if "pulls" in include_set:
        query = urllib.parse.urlencode({"state": state, "sort": "updated", "direction": "desc", "per_page": per_page})
        pulls = _fetch_json(f"{base}/pulls?{query}", token)
        for pull in pulls:
            pull["kind"] = "pull"
        records.extend(pulls)
    records = records[:MAX_GITHUB_ITEMS]
    if not records:
        raise IngestionError(404, "GitHub connector found no records to sync")
    return records


def _record_kind(record: dict) -> str:
    explicit_kind = str(record.get("kind") or "").strip().lower()
    if explicit_kind in {"pull", "pull_request", "pr"}:
        return "pull_request"
    if explicit_kind == "issue":
        return "issue"
    return "pull_request" if isinstance(record.get("pull_request"), dict) else "issue"


def _label_names(record: dict) -> list[str]:
    labels = record.get("labels") or []
    names: list[str] = []
    if isinstance(labels, list):
        for label in labels:
            if isinstance(label, dict):
                name = str(label.get("name") or "").strip()
            else:
                name = str(label or "").strip()
            if name and name not in names:
                names.append(name)
    return names[:12]


def _author_login(record: dict) -> str:
    user = record.get("user") if isinstance(record.get("user"), dict) else {}
    return str(record.get("author") or user.get("login") or "unknown").strip()[:80]


def _allowed_roles(record: dict) -> list[str]:
    roles = record.get("allowed_roles")
    if roles is None:
        return ["employee", "manager", "admin"]
    if not isinstance(roles, list) or not roles:
        raise IngestionError(400, "GitHub record allowed_roles must be a non-empty list")
    return roles


def _github_document(owner: str, repo_name: str, record: dict) -> tuple[dict, dict]:
    number = record.get("number")
    try:
        issue_number = int(number)
    except (TypeError, ValueError):
        raise IngestionError(400, "GitHub record number must be an integer") from None
    if issue_number <= 0:
        raise IngestionError(400, "GitHub record number must be positive")

    kind = _record_kind(record)
    title = _string(record.get("title"), "GitHub record title", max_length=180)
    state = str(record.get("state") or "open").strip().lower()[:40]
    labels = _label_names(record)
    author = _author_login(record)
    updated_at = str(record.get("updated_at") or utc_now()).strip()
    web_path = "pull" if kind == "pull_request" else "issues"
    html_url = str(record.get("html_url") or f"https://github.com/{owner}/{repo_name}/{web_path}/{issue_number}").strip()
    raw_body = str(record.get("body") or "No body was provided for this GitHub record.").strip()
    external_id = f"github:{owner}/{repo_name}:{kind}:{issue_number}"
    doc_id = f"github-{_slug(owner)}-{_slug(repo_name)}-{_slug(kind)}-{issue_number}"
    body = "\n".join(
        [
            f"GitHub {kind.replace('_', ' ').title()} #{issue_number}: {title}",
            "",
            f"Repository: {owner}/{repo_name}",
            f"State: {state}",
            f"Author: {author}",
            f"Labels: {', '.join(labels) if labels else 'none'}",
            f"Source URL: {html_url}",
            "",
            raw_body,
        ]
    )
    document = {
        "id": doc_id,
        "external_id": external_id,
        "title": f"GitHub {kind.replace('_', ' ').title()} #{issue_number}: {title}",
        "body": body,
        "classification": str(record.get("classification") or "internal").strip().lower(),
        "allowed_roles": _allowed_roles(record),
        "source_mime": "text/markdown",
        "source_url": html_url,
        "updated_at": updated_at,
        "version": updated_at,
    }
    acl_record = {
        "allowed_roles": document["allowed_roles"],
        "permission_id": f"{external_id}:visibility",
        "principal_count": len(document["allowed_roles"]),
    }
    return document, acl_record


def _github_source_payload(actor_id: str, owner: str, repo_name: str, cursor: str, records: list[dict]) -> dict:
    documents: list[dict] = []
    acl_documents: dict[str, dict] = {}
    for record in records:
        document, acl_record = _github_document(owner, repo_name, record)
        documents.append(document)
        acl_documents[document["external_id"]] = acl_record

    acl_version = f"github:{owner}/{repo_name}:{cursor}"
    return {
        "user_id": actor_id,
        "replace": True,
        "connector": {
            "name": "github",
            "cursor": cursor,
            "acl_source": f"github:{owner}/{repo_name}:visibility",
            "acl_snapshot": {
                "version": acl_version,
                "documents": acl_documents,
            },
        },
        "documents": documents,
    }


def sync_github_repository(repository: KnowledgeRepository, payload: dict) -> dict:
    actor_id = _string(payload.get("user_id"), "user_id", max_length=80)
    actor = repository.get_user(actor_id)
    if not actor:
        raise IngestionError(404, f"Unknown user_id: {actor_id}")
    if actor["role"] != "admin":
        raise IngestionError(403, "Only admin users can sync GitHub repositories.")

    owner = _github_name(payload.get("owner"), "owner", max_length=80)
    repo_name = _github_name(payload.get("repo"), "repo", max_length=100)
    cursor = _string(payload.get("cursor") or utc_now(), "cursor", max_length=240)
    mode = str(payload.get("mode") or "fixture").strip().lower()
    if mode not in {"fixture", "live"}:
        raise IngestionError(400, "mode must be fixture or live")

    records = _records_from_fixture(payload) if mode == "fixture" else _records_from_live_github(owner, repo_name, payload)
    source_payload = _github_source_payload(actor_id, owner, repo_name, cursor, records)
    idempotency_key = str(payload.get("idempotency_key") or "").strip()
    if not idempotency_key:
        idempotency_key = f"github:{owner}/{repo_name}:{cursor}:{_stable_hash(source_payload)[:16]}"

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
    repository.insert_audit(
        actor_id,
        "github_connector_synced",
        {
            "owner": owner,
            "repo": repo_name,
            "mode": mode,
            "cursor": cursor,
            "record_count": len(records),
            "job_id": job.get("id"),
            "job_status": job.get("status"),
            "idempotency_key": idempotency_key,
            "idempotency_replayed": bool(job_response.get("idempotency_replayed")),
        },
    )
    return {
        "github": {
            "owner": owner,
            "repo": repo_name,
            "mode": mode,
            "cursor": cursor,
            "record_count": len(records),
            "source_payload_sha256": _stable_hash(source_payload),
            "api_reference": "https://docs.github.com/en/rest/issues/issues",
        },
        **job_response,
    }
