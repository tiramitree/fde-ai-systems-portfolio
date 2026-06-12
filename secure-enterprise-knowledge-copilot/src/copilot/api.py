from __future__ import annotations

from urllib.parse import parse_qs

from .answering import generate_answer
from .auth_tokens import (
    AuthTokenError,
    LOCAL_AUTH_POLICY,
    bearer_token_from_header,
    issue_demo_token,
    verify_demo_token,
)
from .connector_status import list_connector_status
from .evals import latest_eval_run, run_evals
from .github_connector import sync_github_repository
from .ingestion import IngestionError, ingest_document, preview_document_parse, sync_source_batch
from .ingestion_jobs import list_ingestion_jobs, submit_ingestion_job
from .repositories import connect_repository
from .source_bundle_connector import list_source_bundle_catalog, sync_source_bundle
from .source_quality import list_source_quality


class ApiError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(message)


class CopilotApi:
    app_name = "secure-enterprise-knowledge-copilot"

    def get(self, path: str, query: dict[str, list[str]], headers: object | None = None) -> dict:
        with connect_repository() as repo:
            if path == "/api/health":
                return {"status": "ok", "app": self.app_name}
            if path == "/api/ready":
                return self._readiness(repo)
            if path == "/api/users":
                return {"users": repo.list_users()}
            if path == "/api/documents":
                user_id = self._resolve_user_id(repo, headers, self._first_or_none(query, "user_id"), "alice")
                user = repo.get_user(user_id)
                if not user:
                    raise ApiError(404, f"Unknown user_id: {user_id}")
                return {"documents": repo.list_visible_documents(user)}
            if path == "/api/traces":
                return {"traces": repo.list_traces(limit=self._int(query, "limit", 25))}
            if path == "/api/audit":
                return {"events": repo.list_audit_events(limit=self._int(query, "limit", 50))}
            if path == "/api/ingestion/jobs":
                try:
                    return list_ingestion_jobs(
                        repo,
                        user_id=self._resolve_user_id(repo, headers, self._first_or_none(query, "user_id"), "avery"),
                        limit=self._int(query, "limit", 25),
                    )
                except IngestionError as exc:
                    raise ApiError(exc.status, exc.message) from exc
            if path == "/api/connectors/status":
                try:
                    return list_connector_status(
                        repo,
                        user_id=self._resolve_user_id(repo, headers, self._first_or_none(query, "user_id"), "avery"),
                        limit=self._int(query, "limit", 100),
                    )
                except IngestionError as exc:
                    raise ApiError(exc.status, exc.message) from exc
            if path == "/api/sources/quality":
                try:
                    return list_source_quality(
                        repo,
                        user_id=self._resolve_user_id(repo, headers, self._first_or_none(query, "user_id"), "avery"),
                        limit=self._int(query, "limit", 100),
                    )
                except IngestionError as exc:
                    raise ApiError(exc.status, exc.message) from exc
            if path == "/api/connectors/source-bundle/catalog":
                try:
                    payload = {
                        "user_id": self._resolve_user_id(repo, headers, self._first_or_none(query, "user_id"), "avery"),
                        "bundle": self._first_or_none(query, "bundle") or "",
                        "cursor": self._first_or_none(query, "cursor") or "",
                    }
                    prune_missing = self._first_or_none(query, "prune_missing")
                    if prune_missing is not None:
                        payload["prune_missing"] = prune_missing.lower() in {"1", "true", "yes"}
                    return list_source_bundle_catalog(repo, payload)
                except IngestionError as exc:
                    raise ApiError(exc.status, exc.message) from exc
            if path == "/api/eval/latest":
                return {"eval_run": latest_eval_run(repo)}
            if path == "/api/scenario":
                snapshot = repo.load_scenario_snapshot()
                snapshot["app"] = self.app_name
                return {"scenario": snapshot}
        raise ApiError(404, f"Unknown endpoint: {path}")

    def _readiness(self, repo: object) -> dict:
        snapshot = repo.load_scenario_snapshot()
        eval_run = latest_eval_run(repo)
        users = repo.list_users()
        return {
            "status": "ready",
            "app": self.app_name,
            "ready": True,
            "checks": {
                "storage": "ok",
                "seed_data": "ok" if users else "missing",
                "eval_state": "ok" if isinstance(eval_run, dict) else "missing",
                "scenario_snapshot": "ok" if isinstance(snapshot.get("files"), list) else "missing",
                "users": len(users),
                "scenario_files": len(snapshot.get("files", [])) if isinstance(snapshot.get("files"), list) else 0,
            },
        }

    def post(self, path: str, body: dict, headers: object | None = None) -> dict:
        with connect_repository() as repo:
            if path == "/api/auth/demo-token":
                user_id = str(body.get("user_id", "")).strip()
                user = repo.get_user(user_id)
                if not user:
                    raise ApiError(404, f"Unknown user_id: {user_id}")
                return {
                    "token_type": "Bearer",
                    "expires_in": 3600,
                    "auth_policy": LOCAL_AUTH_POLICY,
                    "token": issue_demo_token(user),
                    "auth_context": self._public_auth_context(user, "local_signed_demo_token"),
                }
            if path == "/api/query":
                user_id = self._resolve_user_id(repo, headers, str(body.get("user_id", "")).strip(), "")
                return generate_answer(repo, user_id, body.get("question", ""), request_id=self._header(headers, "X-Request-ID"))
            if path == "/api/documents/ingest":
                try:
                    return ingest_document(repo, self._body_with_resolved_user(repo, body, headers))
                except IngestionError as exc:
                    raise ApiError(exc.status, exc.message) from exc
            if path == "/api/documents/parse-preview":
                try:
                    return preview_document_parse(repo, self._body_with_resolved_user(repo, body, headers))
                except IngestionError as exc:
                    raise ApiError(exc.status, exc.message) from exc
            if path == "/api/sources/sync":
                try:
                    return sync_source_batch(repo, self._body_with_resolved_user(repo, body, headers))
                except IngestionError as exc:
                    raise ApiError(exc.status, exc.message) from exc
            if path == "/api/ingestion/jobs":
                try:
                    return submit_ingestion_job(repo, self._body_with_resolved_user(repo, body, headers))
                except IngestionError as exc:
                    raise ApiError(exc.status, exc.message) from exc
            if path == "/api/connectors/github/sync":
                try:
                    return sync_github_repository(repo, self._body_with_resolved_user(repo, body, headers))
                except IngestionError as exc:
                    raise ApiError(exc.status, exc.message) from exc
            if path == "/api/connectors/source-bundle/sync":
                try:
                    return sync_source_bundle(repo, self._body_with_resolved_user(repo, body, headers))
                except IngestionError as exc:
                    raise ApiError(exc.status, exc.message) from exc
            if path == "/api/eval/run":
                return run_evals(repo)
        raise ApiError(404, f"Unknown endpoint: {path}")

    @staticmethod
    def parse_query(query: str) -> dict[str, list[str]]:
        return parse_qs(query)

    @staticmethod
    def _first(query: dict[str, list[str]], key: str, default: str) -> str:
        return query.get(key, [default])[0]

    @staticmethod
    def _first_or_none(query: dict[str, list[str]], key: str) -> str | None:
        values = query.get(key)
        return values[0] if values else None

    @classmethod
    def _int(cls, query: dict[str, list[str]], key: str, default: int) -> int:
        try:
            return int(cls._first(query, key, str(default)))
        except ValueError as exc:
            raise ApiError(400, f"Invalid integer query parameter: {key}") from exc

    def _body_with_resolved_user(self, repo: object, body: dict, headers: object | None) -> dict:
        explicit_user_id = str(body.get("user_id", "")).strip()
        resolved_user_id = self._resolve_user_id(repo, headers, explicit_user_id, explicit_user_id)
        return {**body, "user_id": resolved_user_id}

    def _resolve_user_id(
        self,
        repo: object,
        headers: object | None,
        explicit_user_id: str | None,
        default_user_id: str,
    ) -> str:
        explicit = (explicit_user_id or "").strip()
        authenticated_user = self._authenticated_user(repo, headers)
        if authenticated_user:
            subject = str(authenticated_user.get("id", ""))
            if explicit and explicit != subject:
                raise ApiError(403, "Request user_id does not match authenticated subject.")
            return subject
        return explicit or default_user_id

    def _authenticated_user(self, repo: object, headers: object | None) -> dict | None:
        raw_header = self._header(headers, "Authorization")
        if not raw_header:
            return None
        try:
            claims = verify_demo_token(bearer_token_from_header(raw_header))
        except AuthTokenError as exc:
            raise ApiError(401, str(exc)) from exc
        user = repo.get_user(str(claims.get("sub", "")))
        if not user:
            raise ApiError(401, "Authenticated subject is no longer available.")
        if (
            claims.get("tenant_id") != user.get("tenant_id")
            or claims.get("role") != user.get("role")
            or list(claims.get("group_ids", [])) != list(user.get("group_ids", []))
        ):
            raise ApiError(401, "Authenticated context no longer matches the user record.")
        return user

    @staticmethod
    def _header(headers: object | None, key: str) -> str:
        if headers is None:
            return ""
        getter = getattr(headers, "get", None)
        if callable(getter):
            return str(getter(key, "") or "")
        return ""

    @staticmethod
    def _public_auth_context(user: dict, mode: str) -> dict:
        return {
            "auth_mode": mode,
            "user_id": user.get("id", ""),
            "tenant_id": user.get("tenant_id", ""),
            "role": user.get("role", ""),
            "group_ids": user.get("group_ids", []),
        }
