from __future__ import annotations

import json
import uuid
from typing import Any, Protocol

from .storage import load_scenario_snapshot
from .time_utils import utc_now


class SqlCursor(Protocol):
    def execute(self, sql: str, params: tuple[Any, ...] = ()) -> Any: ...
    def fetchone(self) -> Any: ...
    def fetchall(self) -> list[Any]: ...


class SqlConnection(Protocol):
    def cursor(self) -> Any: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
    def close(self) -> None: ...


def _json_payload(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"), sort_keys=True)


def _coerce_json(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def _uuid_or_none(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return str(uuid.UUID(value))
    except ValueError:
        return None


def _stable_uuid(namespace: str, value: str) -> str:
    return str(uuid.uuid5(uuid.UUID(namespace), value))


def _public_document(doc: dict) -> dict:
    return {key: value for key, value in doc.items() if key != "body"}


class PostgresKnowledgeRepository:
    """PostgreSQL-backed implementation of the Project 1 repository contract.

    The class intentionally accepts a generic DB-API-style connection instead of
    importing a driver. This keeps the public demo dependency-free while making
    the production data-plane boundary executable once a deployment layer
    injects a psycopg-style connection or pool.
    """

    provider = "postgres"

    def __init__(self, connection: SqlConnection, tenant_slug: str):
        self.connection = connection
        self.tenant_slug = tenant_slug
        self._active_user: dict | None = None
        self._tenant_uuid_cache: str | None = None

    def get_user(self, user_id: str) -> dict | None:
        self._apply_context()
        row = self._fetch_one(
            """
            select
              u.id::text,
              u.external_user_id,
              u.display_name,
              u.role,
              coalesce(u.department, ''),
              t.id::text,
              t.slug
            from users u
            join tenants t on t.id = u.tenant_id
            where t.slug = %s and u.external_user_id = %s
            """,
            (self.tenant_slug, user_id),
        )
        if not row:
            return None
        user = {
            "_user_uuid": row[0],
            "id": row[1],
            "name": row[2],
            "role": row[3],
            "department": row[4],
            "_tenant_uuid": row[5],
            "tenant_id": row[6],
        }
        self._active_user = user
        self._tenant_uuid_cache = row[5]
        self._apply_context(user)
        return user

    def list_users(self) -> list[dict]:
        self._apply_context()
        rows = self._fetch_all(
            """
            select
              u.id::text,
              u.external_user_id,
              u.display_name,
              u.role,
              coalesce(u.department, ''),
              t.id::text,
              t.slug
            from users u
            join tenants t on t.id = u.tenant_id
            where t.slug = %s
            order by u.role, u.external_user_id
            """,
            (self.tenant_slug,),
        )
        return [
            {
                "_user_uuid": row[0],
                "id": row[1],
                "name": row[2],
                "role": row[3],
                "department": row[4],
                "_tenant_uuid": row[5],
                "tenant_id": row[6],
            }
            for row in rows
        ]

    def list_visible_documents(self, user: dict) -> list[dict]:
        self._active_user = user
        self._apply_context(user)
        rows = self._fetch_all(
            """
            select
              d.id::text,
              d.external_doc_id,
              t.slug,
              d.title,
              d.sensitivity,
              d.allowed_roles,
              coalesce(d.source_uri, ''),
              coalesce(d.source_mime, ''),
              d.source_hash,
              d.version,
              d.updated_at::text,
              d.metadata
            from documents d
            join tenants t on t.id = d.tenant_id
            where t.slug = %s and %s = any(d.allowed_roles)
            order by d.updated_at desc, d.external_doc_id
            """,
            (user["tenant_id"], user["role"]),
        )
        return [_public_document(self._row_to_document(row)) for row in rows]

    def list_chunks(self, tenant_id: str) -> list[dict]:
        self._apply_context(self._active_user)
        rows = self._fetch_all(
            """
            select
              c.id::text,
              coalesce(c.metadata->>'external_chunk_id', c.id::text),
              d.external_doc_id,
              c.chunk_index,
              t.slug,
              d.title,
              c.content,
              d.sensitivity,
              d.allowed_roles,
              coalesce(d.source_uri, ''),
              coalesce(d.source_mime, ''),
              d.source_hash,
              d.version,
              d.updated_at::text,
              c.metadata
            from document_chunks c
            join documents d on d.id = c.document_id
            join tenants t on t.id = c.tenant_id
            where t.slug = %s
            order by d.external_doc_id, c.chunk_index
            """,
            (tenant_id,),
        )
        return [self._row_to_chunk(row) for row in rows]

    def count_potentially_blocked_chunks(self, user: dict, query_tokens: list[str]) -> int:
        self._active_user = user
        self._apply_context(user)
        if not query_tokens:
            return 0
        row = self._fetch_one(
            "select project1_denied_relevant_chunk_count(%s::text[])",
            (query_tokens,),
        )
        return int(row[0]) if row else 0

    def document_exists(self, doc_id: str) -> bool:
        self._apply_context(self._active_user)
        row = self._fetch_one(
            """
            select 1
            from documents d
            join tenants t on t.id = d.tenant_id
            where t.slug = %s and d.external_doc_id = %s
            limit 1
            """,
            (self.tenant_slug, doc_id),
        )
        return row is not None

    def replace_document_with_chunks(self, document: dict, chunks: list[dict]) -> bool:
        self._apply_context(self._active_user)
        tenant_uuid = self._tenant_uuid(document["tenant_id"])
        doc_uuid = _stable_uuid(tenant_uuid, document["id"])
        replaced = self.document_exists(document["id"])
        self._execute_write(
            """
            delete from documents
            where tenant_id = %s::uuid and external_doc_id = %s
            """,
            (tenant_uuid, document["id"]),
        )
        self._execute_write(
            """
            insert into documents (
              id, tenant_id, external_doc_id, title, source_uri, source_mime,
              source_hash, sensitivity, allowed_roles, version, updated_at, metadata
            )
            values (%s::uuid, %s::uuid, %s, %s, %s, %s, %s, %s, %s, %s, %s::timestamptz, %s::jsonb)
            """,
            (
                doc_uuid,
                tenant_uuid,
                document["id"],
                document["title"],
                document.get("source_url", ""),
                document.get("source_mime", ""),
                document["source_hash"],
                document["classification"],
                document["allowed_roles"],
                document["version"],
                document["updated_at"],
                _json_payload(
                    {
                        "parser_name": document.get("parser_name"),
                        "parser_metadata": document.get("parser_metadata", {}),
                        "parser_warnings": document.get("parser_warnings", []),
                    }
                ),
            ),
        )
        for chunk in chunks:
            chunk_uuid = _stable_uuid(doc_uuid, chunk["id"])
            metadata = {
                "external_chunk_id": chunk["id"],
                "source_hash": chunk.get("source_hash"),
                "updated_at": chunk.get("updated_at"),
                "parser_name": chunk.get("parser_name"),
                "parser_metadata": chunk.get("parser_metadata", {}),
                "parser_warnings": chunk.get("parser_warnings", []),
            }
            self._execute_write(
                """
                insert into document_chunks (
                  id, tenant_id, document_id, chunk_index, content, metadata
                )
                values (%s::uuid, %s::uuid, %s::uuid, %s, %s, %s::jsonb)
                """,
                (
                    chunk_uuid,
                    tenant_uuid,
                    doc_uuid,
                    chunk["chunk_index"],
                    chunk["text"],
                    _json_payload(metadata),
                ),
            )
        self._commit()
        return replaced

    def insert_trace(self, trace_id: str, user_id: str, question: str, payload: dict) -> None:
        user = self._active_user if self._active_user and self._active_user["id"] == user_id else self.get_user(user_id)
        if not user:
            raise ValueError(f"Unknown user_id: {user_id}")
        self._apply_context(user)
        trace_uuid = _uuid_or_none(trace_id) or _stable_uuid(user["_tenant_uuid"], trace_id)
        stored_payload = dict(payload)
        stored_payload["question"] = question
        self._execute_write(
            """
            insert into traces (id, tenant_id, user_id, request_id, route, payload)
            values (%s::uuid, %s::uuid, %s::uuid, %s, %s, %s::jsonb)
            on conflict (tenant_id, request_id) do update
              set payload = excluded.payload
            """,
            (
                trace_uuid,
                user["_tenant_uuid"],
                user["_user_uuid"],
                trace_id,
                "query_answered",
                _json_payload(stored_payload),
            ),
        )
        self._commit()

    def insert_audit(self, user_id: str, action: str, details: dict) -> None:
        user = self._active_user if self._active_user and self._active_user["id"] == user_id else self.get_user(user_id)
        if not user:
            raise ValueError(f"Unknown user_id: {user_id}")
        self._apply_context(user)
        trace_uuid = _uuid_or_none(str(details.get("trace_id", "")))
        self._execute_write(
            """
            insert into audit_events (
              tenant_id, actor_user_id, trace_id, event_type, payload
            )
            values (%s::uuid, %s::uuid, %s::uuid, %s, %s::jsonb)
            """,
            (
                user["_tenant_uuid"],
                user["_user_uuid"],
                trace_uuid,
                action,
                _json_payload(details),
            ),
        )
        self._commit()

    def list_traces(self, limit: int = 25) -> list[dict]:
        self._apply_context(self._active_user)
        rows = self._fetch_all(
            """
            select
              tr.id::text,
              tr.created_at::text,
              coalesce(u.external_user_id, ''),
              tr.request_id,
              tr.payload
            from traces tr
            left join users u on u.id = tr.user_id
            join tenants t on t.id = tr.tenant_id
            where t.slug = %s
            order by tr.created_at desc
            limit %s
            """,
            (self.tenant_slug, limit),
        )
        traces = []
        for row in rows:
            payload = _coerce_json(row[4]) or {}
            traces.append(
                {
                    "id": row[0],
                    "created_at": row[1],
                    "user_id": row[2],
                    "question": payload.get("question", row[3]) if isinstance(payload, dict) else row[3],
                    "payload": payload,
                }
            )
        return traces

    def list_audit_events(self, limit: int = 50) -> list[dict]:
        self._apply_context(self._active_user)
        rows = self._fetch_all(
            """
            select
              ae.id,
              ae.created_at::text,
              coalesce(u.external_user_id, ''),
              ae.event_type,
              ae.payload
            from audit_events ae
            left join users u on u.id = ae.actor_user_id
            join tenants t on t.id = ae.tenant_id
            where t.slug = %s
            order by ae.created_at desc
            limit %s
            """,
            (self.tenant_slug, limit),
        )
        return [
            {
                "id": row[0],
                "created_at": row[1],
                "user_id": row[2],
                "action": row[3],
                "details": _coerce_json(row[4]),
            }
            for row in rows
        ]

    def insert_eval_run(self, payload: dict) -> None:
        tenant_uuid = self._tenant_uuid(self.tenant_slug)
        self._apply_context(self._active_user)
        eval_run_uuid = _uuid_or_none(payload["id"]) or _stable_uuid(tenant_uuid, payload["id"])
        self._execute_write(
            """
            insert into eval_runs (id, tenant_id, suite_id, environment, metrics, created_at)
            values (%s::uuid, %s::uuid, %s, %s, %s::jsonb, %s::timestamptz)
            """,
            (
                eval_run_uuid,
                tenant_uuid,
                "secure-enterprise-knowledge-copilot",
                "local",
                _json_payload(payload.get("metrics", {})),
                payload.get("created_at", utc_now()),
            ),
        )
        for case in payload.get("cases", []):
            case_uuid = _stable_uuid(eval_run_uuid, case["id"])
            trace_uuid = _uuid_or_none(case.get("trace_id"))
            self._execute_write(
                """
                insert into eval_cases (
                  id, tenant_id, eval_run_id, case_id, input, expected, outcome, passed, trace_id
                )
                values (%s::uuid, %s::uuid, %s::uuid, %s, %s::jsonb, %s::jsonb, %s::jsonb, %s, %s::uuid)
                """,
                (
                    case_uuid,
                    tenant_uuid,
                    eval_run_uuid,
                    case["id"],
                    _json_payload({"question": case.get("question"), "user_id": case.get("user_id")}),
                    _json_payload({}),
                    _json_payload(case),
                    bool(case.get("passed")),
                    trace_uuid,
                ),
            )
        self._commit()

    def latest_eval_run(self) -> dict | None:
        self._apply_context(self._active_user)
        run = self._fetch_one(
            """
            select er.id::text, er.created_at::text, er.metrics
            from eval_runs er
            join tenants t on t.id = er.tenant_id
            where t.slug = %s and er.suite_id = %s
            order by er.created_at desc
            limit 1
            """,
            (self.tenant_slug, "secure-enterprise-knowledge-copilot"),
        )
        if not run:
            return None
        cases = self._fetch_all(
            """
            select ec.outcome
            from eval_cases ec
            where ec.eval_run_id = %s::uuid
            order by ec.case_id
            """,
            (run[0],),
        )
        return {
            "id": run[0],
            "created_at": run[1],
            "metrics": _coerce_json(run[2]),
            "cases": [_coerce_json(row[0]) for row in cases],
        }

    def load_scenario_snapshot(self) -> dict:
        return load_scenario_snapshot()

    def _row_to_document(self, row: Any) -> dict:
        metadata = _coerce_json(row[11]) if len(row) > 11 else {}
        return {
            "_document_uuid": row[0],
            "id": row[1],
            "tenant_id": row[2],
            "title": row[3],
            "classification": row[4],
            "allowed_roles": list(row[5]),
            "source_url": row[6],
            "source_mime": row[7],
            "source_hash": row[8],
            "version": row[9],
            "updated_at": row[10],
            "parser_name": metadata.get("parser_name") if isinstance(metadata, dict) else None,
            "parser_metadata": metadata.get("parser_metadata", {}) if isinstance(metadata, dict) else {},
            "parser_warnings": metadata.get("parser_warnings", []) if isinstance(metadata, dict) else [],
        }

    def _row_to_chunk(self, row: Any) -> dict:
        metadata = _coerce_json(row[14]) if len(row) > 14 else {}
        return {
            "_chunk_uuid": row[0],
            "id": row[1],
            "doc_id": row[2],
            "chunk_index": row[3],
            "tenant_id": row[4],
            "title": row[5],
            "text": row[6],
            "classification": row[7],
            "allowed_roles": list(row[8]),
            "source_url": row[9],
            "source_mime": row[10],
            "source_hash": row[11],
            "version": row[12],
            "updated_at": row[13],
            "parser_name": metadata.get("parser_name") if isinstance(metadata, dict) else None,
            "parser_metadata": metadata.get("parser_metadata", {}) if isinstance(metadata, dict) else {},
            "parser_warnings": metadata.get("parser_warnings", []) if isinstance(metadata, dict) else [],
        }

    def _tenant_uuid(self, tenant_slug: str) -> str:
        if tenant_slug == self.tenant_slug and self._tenant_uuid_cache:
            return self._tenant_uuid_cache
        self._set_tenant_slug(tenant_slug)
        row = self._fetch_one("select id::text from tenants where slug = %s", (tenant_slug,))
        if not row:
            raise ValueError(f"Unknown tenant_id: {tenant_slug}")
        if tenant_slug == self.tenant_slug:
            self._tenant_uuid_cache = row[0]
        return row[0]

    def _apply_context(self, user: dict | None = None) -> None:
        self._set_tenant_slug(user["tenant_id"] if user else self.tenant_slug)
        tenant_uuid = user.get("_tenant_uuid") if user else self._tenant_uuid(self.tenant_slug)
        role = user.get("role") if user else "admin"
        user_uuid = user.get("_user_uuid") if user else "00000000-0000-0000-0000-000000000000"
        self._execute_write("select set_config('app.tenant_id', %s, true)", (tenant_uuid,))
        self._execute_write("select set_config('app.role', %s, true)", (role,))
        self._execute_write("select set_config('app.user_id', %s, true)", (user_uuid,))
        self._execute_write("select set_config('app.environment', %s, true)", ("local",))

    def _set_tenant_slug(self, tenant_slug: str) -> None:
        self._execute_write("select set_config('app.tenant_slug', %s, true)", (tenant_slug,))

    def _fetch_one(self, sql: str, params: tuple[Any, ...] = ()) -> Any:
        with self.connection.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchone()

    def _fetch_all(self, sql: str, params: tuple[Any, ...] = ()) -> list[Any]:
        with self.connection.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()

    def _execute_write(self, sql: str, params: tuple[Any, ...] = ()) -> None:
        with self.connection.cursor() as cursor:
            cursor.execute(sql, params)

    def _commit(self) -> None:
        self.connection.commit()
