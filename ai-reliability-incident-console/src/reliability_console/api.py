from __future__ import annotations

from urllib.parse import parse_qs

from .evals import run_evals
from .storage import (
    connect,
    init_state,
    latest_eval_run,
    list_audit,
    list_eval_runs,
    list_incidents,
    list_releases,
    list_runbooks,
    list_traces,
    list_users,
)
from .triage import triage_incident


class ApiError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(message)


class ReliabilityApi:
    app_name = "ai-reliability-incident-console"

    def get(self, path: str, query: dict[str, list[str]]) -> dict:
        with connect() as store:
            if path == "/api/health":
                return {"status": "ok", "app": self.app_name}
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
        raise ApiError(404, f"Unknown endpoint: {path}")

    def post(self, path: str, body: dict) -> dict:
        with connect() as store:
            if path == "/api/triage":
                try:
                    return triage_incident(
                        store,
                        body.get("user_id", ""),
                        body.get("release_id", ""),
                        body.get("incident_id", ""),
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
