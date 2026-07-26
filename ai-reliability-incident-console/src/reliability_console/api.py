from __future__ import annotations

from urllib.parse import parse_qs

from local_auth_tokens import (
    LOCAL_AUTH_POLICY,
    LOCAL_AUTH_TTL_SECONDS,
    AuthTokenError,
    bearer_token_from_header,
    issue_demo_token,
    verify_demo_token,
)

from .evals import run_evals
from .storage import (
    connect,
    get_user,
    init_state,
    latest_eval_run,
    list_audit,
    list_eval_runs,
    list_incidents,
    list_releases,
    list_runbooks,
    list_traces,
    list_users,
    load_scenario_snapshot,
)
from .triage import triage_incident


class ApiError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(message)


class ReliabilityApi:
    app_name = "ai-reliability-incident-console"
    auth_secret_env = "RELIABILITY_CONSOLE_DEMO_AUTH_SECRET"

    def get(self, path: str, query: dict[str, list[str]], headers: object | None = None) -> dict:
        with connect() as store:
            if path == "/api/health":
                return {"status": "ok", "app": self.app_name}
            if path == "/api/ready":
                return self._readiness(store)
            if path == "/api/users":
                return {"users": list_users(store)}
            if path == "/api/releases":
                return {"releases": list_releases(store)}
            if path == "/api/incidents":
                return {"incidents": list_incidents(store)}
            if path == "/api/eval-runs":
                return {"eval_runs": list_eval_runs(store)}
            if path == "/api/runbooks":
                return {"runbooks": list_runbooks(store)}
            if path == "/api/traces":
                return {"traces": list_traces(store, self._int(query, "limit", 25))}
            if path == "/api/audit":
                return {"events": list_audit(store, self._int(query, "limit", 50))}
            if path == "/api/eval/latest":
                return {"eval_run": latest_eval_run(store)}
            if path == "/api/scenario":
                snapshot = load_scenario_snapshot()
                snapshot["app"] = self.app_name
                return {"scenario": snapshot}
        raise ApiError(404, f"Unknown endpoint: {path}")

    def _readiness(self, store: object) -> dict:
        snapshot = load_scenario_snapshot()
        eval_run = latest_eval_run(store)
        users = list_users(store)
        releases = list_releases(store)
        incidents = list_incidents(store)
        runbooks = list_runbooks(store)
        return {
            "status": "ready",
            "app": self.app_name,
            "ready": True,
            "checks": {
                "storage": "ok",
                "seed_data": "ok" if users and releases and incidents else "missing",
                "eval_state": "ok" if isinstance(eval_run, dict) else "missing",
                "scenario_snapshot": "ok" if isinstance(snapshot.get("files"), list) else "missing",
                "users": len(users),
                "releases": len(releases),
                "incidents": len(incidents),
                "runbooks": len(runbooks),
                "scenario_files": len(snapshot.get("files", [])) if isinstance(snapshot.get("files"), list) else 0,
            },
        }

    def post(self, path: str, body: dict, headers: object | None = None) -> dict:
        with connect() as store:
            if path == "/api/auth/demo-token":
                user_id = str(body.get("user_id", "")).strip()
                user = get_user(store, user_id)
                if not user:
                    raise ApiError(404, f"Unknown user_id: {user_id}")
                return {
                    "token_type": "Bearer",
                    "expires_in": LOCAL_AUTH_TTL_SECONDS,
                    "auth_policy": LOCAL_AUTH_POLICY,
                    "token": issue_demo_token(user, issuer=self.app_name, secret_env=self.auth_secret_env),
                    "auth_context": self._public_auth_context(user, "local_signed_demo_token"),
                }
            if path == "/api/triage":
                try:
                    return triage_incident(
                        store,
                        self._resolve_user_id(store, headers, str(body.get("user_id", "")).strip(), str(body.get("user_id", "")).strip()),
                        body.get("release_id", ""),
                        body.get("incident_id", ""),
                        request_id=self._header(headers, "X-Request-ID"),
                    )
                except ValueError as exc:
                    raise ApiError(404, str(exc)) from exc
            if path == "/api/eval/run":
                init_state(reset=True)
                store.load()
                return run_evals(store)
        raise ApiError(404, f"Unknown endpoint: {path}")

    @staticmethod
    def parse_query(query: str) -> dict[str, list[str]]:
        return parse_qs(query)

    @staticmethod
    def _first(query: dict[str, list[str]], key: str, default: str) -> str:
        return query.get(key, [default])[0]

    @classmethod
    def _int(cls, query: dict[str, list[str]], key: str, default: int) -> int:
        try:
            return int(cls._first(query, key, str(default)))
        except ValueError as exc:
            raise ApiError(400, f"Invalid integer query parameter: {key}") from exc

    def _resolve_user_id(
        self,
        store: object,
        headers: object | None,
        explicit_user_id: str | None,
        default_user_id: str,
    ) -> str:
        explicit = (explicit_user_id or "").strip()
        authenticated_user = self._authenticated_user(store, headers)
        if authenticated_user:
            subject = str(authenticated_user.get("id", ""))
            if explicit and explicit != subject:
                raise ApiError(403, "Request identity does not match authenticated subject.")
            return subject
        return explicit or default_user_id

    def _authenticated_user(self, store: object, headers: object | None) -> dict | None:
        raw_header = self._header(headers, "Authorization")
        if not raw_header:
            return None
        try:
            claims = verify_demo_token(
                bearer_token_from_header(raw_header),
                issuer=self.app_name,
                secret_env=self.auth_secret_env,
            )
        except AuthTokenError as exc:
            raise ApiError(401, str(exc)) from exc
        user = get_user(store, str(claims.get("sub", "")))
        if not user:
            raise ApiError(401, "Authenticated subject is no longer available.")
        if claims.get("tenant_id") != self._tenant_id(user) or claims.get("role") != user.get("role") or list(claims.get("group_ids", [])) != list(user.get("group_ids", [])):
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
    def _tenant_id(user: dict) -> str:
        return str(user.get("tenant_id") or "local-demo")

    def _public_auth_context(self, user: dict, mode: str) -> dict:
        return {
            "auth_mode": mode,
            "user_id": user.get("id", ""),
            "tenant_id": self._tenant_id(user),
            "role": user.get("role", ""),
            "group_ids": user.get("group_ids", []),
        }
