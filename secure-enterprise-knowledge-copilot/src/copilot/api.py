from __future__ import annotations

from urllib.parse import parse_qs

from .answering import generate_answer
from .evals import latest_eval_run, run_evals
from .storage import (
    connect,
    get_user,
    list_audit_events,
    list_traces,
    list_users,
    list_visible_documents,
)


class ApiError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(message)


class CopilotApi:
    app_name = "secure-enterprise-knowledge-copilot"

    def get(self, path: str, query: dict[str, list[str]]) -> dict:
        with connect() as conn:
            if path == "/api/health":
                return {"status": "ok", "app": self.app_name}
            if path == "/api/users":
                return {"users": list_users(conn)}
            if path == "/api/documents":
                user_id = self._first(query, "user_id", "alice")
                user = get_user(conn, user_id)
                if not user:
                    raise ApiError(404, f"Unknown user_id: {user_id}")
                return {"documents": list_visible_documents(conn, user)}
            if path == "/api/traces":
                return {"traces": list_traces(conn, limit=self._int(query, "limit", 25))}
            if path == "/api/audit":
                return {"events": list_audit_events(conn, limit=self._int(query, "limit", 50))}
            if path == "/api/eval/latest":
                return {"eval_run": latest_eval_run(conn)}
        raise ApiError(404, f"Unknown endpoint: {path}")

    def post(self, path: str, body: dict) -> dict:
        with connect() as conn:
            if path == "/api/query":
                return generate_answer(conn, body.get("user_id", ""), body.get("question", ""))
            if path == "/api/eval/run":
                return run_evals(conn)
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
