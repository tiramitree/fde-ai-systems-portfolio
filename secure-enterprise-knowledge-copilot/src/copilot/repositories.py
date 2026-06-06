from __future__ import annotations

import importlib
import os
from pathlib import Path
from typing import Any, Callable, Protocol

from .identity import has_identity_access
from .postgres_repositories import PostgresKnowledgeRepository, SqlConnection
from .storage import JsonStore, connect as connect_json, load_scenario_snapshot
from .time_utils import utc_now


_POSTGRES_POOL: Any | None = None
_POSTGRES_POOL_DSN: str | None = None


class KnowledgeRepository(Protocol):
    def get_user(self, user_id: str) -> dict | None: ...
    def list_users(self) -> list[dict]: ...
    def list_visible_documents(self, user: dict) -> list[dict]: ...
    def list_chunks(self, tenant_id: str) -> list[dict]: ...
    def list_retrieval_candidates(
        self,
        user: dict,
        question: str,
        query_tokens: list[str],
        query_embedding: list[float],
        limit: int,
    ) -> dict: ...
    def count_potentially_blocked_chunks(self, user: dict, query_tokens: list[str]) -> int: ...
    def get_document(self, doc_id: str) -> dict | None: ...
    def document_exists(self, doc_id: str) -> bool: ...
    def replace_document_with_chunks(self, document: dict, chunks: list[dict]) -> bool: ...
    def list_documents_by_connector(self, tenant_id: str, connector: str) -> list[dict]: ...
    def delete_documents(self, tenant_id: str, doc_ids: list[str]) -> int: ...
    def get_ingestion_job(self, job_id: str) -> dict | None: ...
    def get_ingestion_job_by_key(self, idempotency_key: str) -> dict | None: ...
    def record_ingestion_job(self, job: dict) -> None: ...
    def list_ingestion_jobs(self, limit: int = 25) -> list[dict]: ...
    def insert_trace(self, trace_id: str, user_id: str, question: str, payload: dict) -> None: ...
    def insert_audit(self, user_id: str, action: str, details: dict) -> None: ...
    def list_traces(self, limit: int = 25) -> list[dict]: ...
    def list_audit_events(self, limit: int = 50) -> list[dict]: ...
    def insert_eval_run(self, payload: dict) -> None: ...
    def latest_eval_run(self) -> dict | None: ...
    def load_scenario_snapshot(self) -> dict: ...


def _public_document(doc: dict) -> dict:
    return {key: value for key, value in doc.items() if key != "body"}


class JsonKnowledgeRepository:
    provider = "json"

    def __init__(self, store: JsonStore):
        self.store = store

    def get_user(self, user_id: str) -> dict | None:
        return next((user for user in self.store.state["users"] if user["id"] == user_id), None)

    def list_users(self) -> list[dict]:
        return sorted(self.store.state["users"], key=lambda user: (user["role"], user["id"]))

    def list_visible_documents(self, user: dict) -> list[dict]:
        docs = []
        for doc in self.store.state["documents"]:
            if has_identity_access(doc, user):
                docs.append(_public_document(doc))
        return docs

    def list_chunks(self, tenant_id: str) -> list[dict]:
        return [chunk for chunk in self.store.state["chunks"] if chunk["tenant_id"] == tenant_id]

    def list_retrieval_candidates(
        self,
        user: dict,
        question: str,
        query_tokens: list[str],
        query_embedding: list[float],
        limit: int,
    ) -> dict:
        del question, query_tokens, query_embedding, limit
        visible_chunks = [
            chunk
            for chunk in self.list_chunks(user["tenant_id"])
            if has_identity_access(chunk, user)
        ]
        return {
            "chunks": visible_chunks,
            "visible_chunk_count": len(visible_chunks),
            "candidate_count": len(visible_chunks),
            "candidate_strategy": "local_full_scan",
        }

    def count_potentially_blocked_chunks(self, user: dict, query_tokens: list[str]) -> int:
        query_terms = set(query_tokens)
        blocked_count = 0
        for chunk in self.store.state["chunks"]:
            if chunk["tenant_id"] != user["tenant_id"] or has_identity_access(chunk, user):
                continue
            haystack = f"{chunk['title']} {chunk['text']}".lower()
            if any(term in haystack for term in query_terms):
                blocked_count += 1
        return blocked_count

    def get_document(self, doc_id: str) -> dict | None:
        doc = next((doc for doc in self.store.state["documents"] if doc["id"] == doc_id), None)
        return _public_document(doc) if doc else None

    def document_exists(self, doc_id: str) -> bool:
        return any(doc["id"] == doc_id for doc in self.store.state["documents"])

    def replace_document_with_chunks(self, document: dict, chunks: list[dict]) -> bool:
        doc_id = document["id"]
        replaced = self.document_exists(doc_id)
        if replaced:
            self.store.state["documents"] = [doc for doc in self.store.state["documents"] if doc["id"] != doc_id]
            self.store.state["chunks"] = [chunk for chunk in self.store.state["chunks"] if chunk["doc_id"] != doc_id]
        self.store.state["documents"].append(document)
        self.store.state["chunks"].extend(chunks)
        return replaced

    def list_documents_by_connector(self, tenant_id: str, connector: str) -> list[dict]:
        return [
            _public_document(doc)
            for doc in self.store.state["documents"]
            if doc.get("tenant_id") == tenant_id and doc.get("source_connector") == connector
        ]

    def delete_documents(self, tenant_id: str, doc_ids: list[str]) -> int:
        doc_id_set = set(doc_ids)
        if not doc_id_set:
            return 0
        before = len(self.store.state["documents"])
        self.store.state["documents"] = [
            doc
            for doc in self.store.state["documents"]
            if doc.get("tenant_id") != tenant_id or doc.get("id") not in doc_id_set
        ]
        self.store.state["chunks"] = [
            chunk
            for chunk in self.store.state["chunks"]
            if chunk.get("tenant_id") != tenant_id or chunk.get("doc_id") not in doc_id_set
        ]
        return before - len(self.store.state["documents"])

    def get_ingestion_job(self, job_id: str) -> dict | None:
        return next(
            (job for job in self.store.state.setdefault("ingestion_jobs", []) if job.get("id") == job_id),
            None,
        )

    def get_ingestion_job_by_key(self, idempotency_key: str) -> dict | None:
        if not idempotency_key:
            return None
        return next(
            (
                job
                for job in self.store.state.setdefault("ingestion_jobs", [])
                if job.get("idempotency_key") == idempotency_key
            ),
            None,
        )

    def record_ingestion_job(self, job: dict) -> None:
        jobs = self.store.state.setdefault("ingestion_jobs", [])
        jobs[:] = [existing for existing in jobs if existing.get("id") != job.get("id")]
        jobs.append(job)

    def list_ingestion_jobs(self, limit: int = 25) -> list[dict]:
        jobs = sorted(
            self.store.state.setdefault("ingestion_jobs", []),
            key=lambda item: item.get("updated_at", item.get("created_at", "")),
            reverse=True,
        )
        return jobs[:limit]

    def insert_trace(self, trace_id: str, user_id: str, question: str, payload: dict) -> None:
        self.store.state["traces"].append(
            {
                "id": trace_id,
                "created_at": utc_now(),
                "user_id": user_id,
                "question": question,
                "payload": payload,
            }
        )

    def insert_audit(self, user_id: str, action: str, details: dict) -> None:
        next_id = len(self.store.state["audit_events"]) + 1
        self.store.state["audit_events"].append(
            {
                "id": next_id,
                "created_at": utc_now(),
                "user_id": user_id,
                "action": action,
                "details": details,
            }
        )

    def list_traces(self, limit: int = 25) -> list[dict]:
        traces = sorted(self.store.state["traces"], key=lambda item: item["created_at"], reverse=True)
        return traces[:limit]

    def list_audit_events(self, limit: int = 50) -> list[dict]:
        events = sorted(self.store.state["audit_events"], key=lambda item: item["created_at"], reverse=True)
        return events[:limit]

    def insert_eval_run(self, payload: dict) -> None:
        self.store.state["eval_runs"].append(payload)

    def latest_eval_run(self) -> dict | None:
        if not self.store.state["eval_runs"]:
            return None
        return sorted(self.store.state["eval_runs"], key=lambda item: item["created_at"], reverse=True)[0]

    def load_scenario_snapshot(self) -> dict:
        return load_scenario_snapshot()


class RepositorySession:
    def __init__(self, path: Path | None = None):
        self._store = connect_json(path) if path else connect_json()
        self._repo: JsonKnowledgeRepository | None = None

    def __enter__(self) -> JsonKnowledgeRepository:
        self._store.__enter__()
        self._repo = JsonKnowledgeRepository(self._store)
        return self._repo

    def __exit__(self, exc_type, exc, tb) -> None:
        self._store.__exit__(exc_type, exc, tb)


def connect_repository(path: Path | None = None) -> RepositorySession | "PostgresRepositorySession":
    if path is not None:
        return RepositorySession(path)
    provider = repository_provider()
    if provider == "json":
        return RepositorySession()
    if provider == "postgres":
        return PostgresRepositorySession()
    raise RuntimeError(f"Unsupported COPILOT_REPOSITORY provider: {provider}")


def repository_provider() -> str:
    return os.getenv("COPILOT_REPOSITORY", "json").strip().lower() or "json"


def postgres_tenant_slug() -> str:
    return os.getenv("COPILOT_TENANT_SLUG", "acme").strip() or "acme"


def postgres_dsn() -> str:
    return os.getenv("COPILOT_POSTGRES_DSN", "").strip()


def postgres_pool_enabled() -> bool:
    return os.getenv("COPILOT_POSTGRES_POOL", "0").strip().lower() in {"1", "true", "yes"}


def connect_psycopg(dsn: str) -> SqlConnection:
    if postgres_pool_enabled():
        return _connect_psycopg_pool(dsn)
    try:
        psycopg = importlib.import_module("psycopg")
    except ImportError as exc:
        raise RuntimeError(
            "COPILOT_REPOSITORY=postgres requires a deployment environment with psycopg installed."
        ) from exc
    return psycopg.connect(dsn)


def _connect_psycopg_pool(dsn: str) -> SqlConnection:
    global _POSTGRES_POOL, _POSTGRES_POOL_DSN
    try:
        psycopg_pool = importlib.import_module("psycopg_pool")
    except ImportError as exc:
        raise RuntimeError(
            "COPILOT_POSTGRES_POOL=1 requires a deployment environment with psycopg_pool installed."
        ) from exc
    if _POSTGRES_POOL is None or _POSTGRES_POOL_DSN != dsn:
        min_size = int(os.getenv("COPILOT_POSTGRES_POOL_MIN", "1"))
        max_size = int(os.getenv("COPILOT_POSTGRES_POOL_MAX", "5"))
        _POSTGRES_POOL = psycopg_pool.ConnectionPool(conninfo=dsn, min_size=min_size, max_size=max_size)
        _POSTGRES_POOL_DSN = dsn
    return PooledPostgresConnection(_POSTGRES_POOL.connection())


class PooledPostgresConnection:
    def __init__(self, lease: Any):
        self._lease = lease
        self._connection = lease.__enter__()

    def cursor(self) -> Any:
        return self._connection.cursor()

    def commit(self) -> None:
        self._connection.commit()

    def rollback(self) -> None:
        self._connection.rollback()

    def close(self) -> None:
        self._lease.__exit__(None, None, None)


class PostgresRepositorySession:
    def __init__(
        self,
        dsn: str | None = None,
        tenant_slug: str | None = None,
        connection_factory: Callable[[str], SqlConnection] | None = None,
    ):
        self.dsn = dsn if dsn is not None else postgres_dsn()
        self.tenant_slug = tenant_slug if tenant_slug is not None else postgres_tenant_slug()
        self.connection_factory = connection_factory or connect_psycopg
        self._connection: SqlConnection | None = None
        self._repo: PostgresKnowledgeRepository | None = None

    def __enter__(self) -> PostgresKnowledgeRepository:
        if not self.dsn:
            raise RuntimeError("COPILOT_REPOSITORY=postgres requires COPILOT_POSTGRES_DSN.")
        self._connection = self.connection_factory(self.dsn)
        self._repo = PostgresKnowledgeRepository(self._connection, self.tenant_slug)
        return self._repo

    def __exit__(self, exc_type, exc, tb) -> None:
        if not self._connection:
            return
        try:
            if exc_type is not None:
                self._connection.rollback()
        finally:
            self._connection.close()
