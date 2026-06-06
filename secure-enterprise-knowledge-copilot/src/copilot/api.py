from __future__ import annotations

from urllib.parse import parse_qs

from .answering import generate_answer
from .evals import latest_eval_run, run_evals
from .ingestion import IngestionError, ingest_document, sync_source_batch
from .ingestion_jobs import list_ingestion_jobs, submit_ingestion_job
from .repositories import connect_repository


class ApiError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(message)


class CopilotApi:
    app_name = "secure-enterprise-knowledge-copilot"

    def get(self, path: str, query: dict[str, list[str]]) -> dict:
        with connect_repository() as repo:
            if path == "/api/health":
                return {"status": "ok", "app": self.app_name}
            if path == "/api/users":
                return {"users": repo.list_users()}
            if path == "/api/documents":
                user_id = self._first(query, "user_id", "alice")
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
                        user_id=self._first(query, "user_id", "avery"),
                        limit=self._int(query, "limit", 25),
                    )
                except IngestionError as exc:
                    raise ApiError(exc.status, exc.message) from exc
            if path == "/api/eval/latest":
                return {"eval_run": latest_eval_run(repo)}
            if path == "/api/scenario":
                snapshot = repo.load_scenario_snapshot()
                snapshot["app"] = self.app_name
                return {"scenario": snapshot}
        raise ApiError(404, f"Unknown endpoint: {path}")

    def post(self, path: str, body: dict) -> dict:
        with connect_repository() as repo:
            if path == "/api/query":
                return generate_answer(repo, body.get("user_id", ""), body.get("question", ""))
            if path == "/api/documents/ingest":
                try:
                    return ingest_document(repo, body)
                except IngestionError as exc:
                    raise ApiError(exc.status, exc.message) from exc
            if path == "/api/sources/sync":
                try:
                    return sync_source_batch(repo, body)
                except IngestionError as exc:
                    raise ApiError(exc.status, exc.message) from exc
            if path == "/api/ingestion/jobs":
                try:
                    return submit_ingestion_job(repo, body)
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

    @classmethod
    def _int(cls, query: dict[str, list[str]], key: str, default: int) -> int:
        try:
            return int(cls._first(query, key, str(default)))
        except ValueError as exc:
            raise ApiError(400, f"Invalid integer query parameter: {key}") from exc
