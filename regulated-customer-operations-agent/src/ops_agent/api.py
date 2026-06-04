from __future__ import annotations

from urllib.parse import parse_qs

from .agent import process_message
from .evals import run_evals
from .storage import (
    connect,
    get_user,
    init_state,
    latest_eval_run,
    list_approvals,
    list_audit,
    list_cases,
    list_traces,
    list_users,
    load_scenario_snapshot,
)
from .tools import approve_action


class ApiError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(message)


class OpsAgentApi:
    app_name = "regulated-customer-operations-agent"

    def get(self, path: str, query: dict[str, list[str]]) -> dict:
        with connect() as store:
            if path == "/api/health":
                return {"status": "ok", "app": self.app_name}
            if path == "/api/users":
                return {"users": list_users(store)}
            if path == "/api/cases":
                return {"cases": list_cases(store)}
            if path == "/api/approvals":
                return {"approvals": list_approvals(store)}
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

    def post(self, path: str, body: dict) -> dict:
        with connect() as store:
            if path == "/api/agent":
                return process_message(
                    store,
                    body.get("user_id", ""),
                    body.get("message", ""),
                    body.get("case_id"),
                )
            if path == "/api/approval/approve":
                approver_id = body.get("approver_id", "")
                user = get_user(store, approver_id)
                if not user or user["role"] != "supervisor":
                    raise ApiError(403, "Only supervisors can approve actions.")
                return approve_action(store, body.get("approval_id", ""), approver_id)
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
