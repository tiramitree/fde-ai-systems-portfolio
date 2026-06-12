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

from .agent import process_message
from .evals import run_evals
from .storage import (
    connect,
    get_user,
    init_state,
    latest_eval_run,
    list_action_outbox,
    list_action_runs,
    list_approvals,
    list_audit,
    list_cases,
    list_traces,
    list_users,
    load_scenario_snapshot,
)
from .tools import (
    TOOL_REGISTRY_SCHEMA_VERSION,
    approve_action,
    expire_approval,
    list_tool_registry,
    public_action_response,
    public_approval,
    reject_approval,
    retry_action_outbox,
)
from .workflows import list_workflow_runs


class ApiError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(message)


class OpsAgentApi:
    app_name = "regulated-customer-operations-agent"
    auth_secret_env = "OPS_AGENT_DEMO_AUTH_SECRET"

    def get(self, path: str, query: dict[str, list[str]], headers: object | None = None) -> dict:
        with connect() as store:
            if path == "/api/health":
                return {"status": "ok", "app": self.app_name}
            if path == "/api/ready":
                return self._readiness(store)
            if path == "/api/users":
                return {"users": list_users(store)}
            if path == "/api/cases":
                return {"cases": list_cases(store)}
            if path == "/api/approvals":
                return {"approvals": [public_approval(approval) for approval in list_approvals(store)]}
            if path == "/api/tool-registry":
                return {"schema_version": TOOL_REGISTRY_SCHEMA_VERSION, "tools": list_tool_registry()}
            if path == "/api/action-outbox":
                return {"action_outbox": list_action_outbox(store, self._int(query, "limit", 25))}
            if path == "/api/action-runs":
                return {"action_runs": list_action_runs(store, self._int(query, "limit", 25))}
            if path == "/api/workflow-runs":
                return {"workflow_runs": list_workflow_runs(store, self._int(query, "limit", 25))}
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
        cases = list_cases(store)
        approvals = list_approvals(store)
        return {
            "status": "ready",
            "app": self.app_name,
            "ready": True,
            "checks": {
                "storage": "ok",
                "seed_data": "ok" if users and cases else "missing",
                "eval_state": "ok" if isinstance(eval_run, dict) else "missing",
                "scenario_snapshot": "ok" if isinstance(snapshot.get("files"), list) else "missing",
                "users": len(users),
                "cases": len(cases),
                "approvals": len(approvals),
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
            if path == "/api/agent":
                return process_message(
                    store,
                    self._resolve_user_id(store, headers, str(body.get("user_id", "")).strip(), str(body.get("user_id", "")).strip()),
                    body.get("message", ""),
                    body.get("case_id"),
                    request_id=self._header(headers, "X-Request-ID"),
                )
            if path == "/api/approval/approve":
                approver_id = self._resolve_user_id(store, headers, str(body.get("approver_id", "")).strip(), str(body.get("approver_id", "")).strip())
                user = get_user(store, approver_id)
                if not user or user["role"] != "supervisor":
                    raise ApiError(403, "Only supervisors can approve actions.")
                return public_action_response(approve_action(store, body.get("approval_id", ""), approver_id))
            if path == "/api/approval/reject":
                reviewer_id = self._resolve_user_id(store, headers, str(body.get("reviewer_id", "")).strip(), str(body.get("reviewer_id", "")).strip())
                user = get_user(store, reviewer_id)
                if not user or user["role"] != "supervisor":
                    raise ApiError(403, "Only supervisors can reject actions.")
                return public_action_response(
                    reject_approval(store, body.get("approval_id", ""), reviewer_id, body.get("reason", ""))
                )
            if path == "/api/approval/expire":
                operator_id = self._resolve_user_id(store, headers, str(body.get("operator_id", "")).strip(), str(body.get("operator_id", "")).strip())
                user = get_user(store, operator_id)
                if not user or user["role"] != "supervisor":
                    raise ApiError(403, "Only supervisors can expire actions.")
                return public_action_response(
                    expire_approval(store, body.get("approval_id", ""), operator_id, body.get("reason", ""))
                )
            if path == "/api/action-outbox/retry":
                operator_id = self._resolve_user_id(store, headers, str(body.get("operator_id", "")).strip(), str(body.get("operator_id", "")).strip())
                user = get_user(store, operator_id)
                if not user or user["role"] != "supervisor":
                    raise ApiError(403, "Only supervisors can retry action outbox dispatch.")
                return public_action_response(retry_action_outbox(store, body.get("outbox_id", ""), operator_id))
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
