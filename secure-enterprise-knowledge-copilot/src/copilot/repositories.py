from __future__ import annotations

from pathlib import Path
from typing import Protocol

from .storage import JsonStore, connect as connect_json, load_scenario_snapshot
from .time_utils import utc_now


class KnowledgeRepository(Protocol):
    def get_user(self, user_id: str) -> dict | None: ...
    def list_users(self) -> list[dict]: ...
    def list_visible_documents(self, user: dict) -> list[dict]: ...
    def list_chunks(self, tenant_id: str) -> list[dict]: ...
    def document_exists(self, doc_id: str) -> bool: ...
    def replace_document_with_chunks(self, document: dict, chunks: list[dict]) -> bool: ...
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
            if doc["tenant_id"] == user["tenant_id"] and user["role"] in doc["allowed_roles"]:
                docs.append(_public_document(doc))
        return docs

    def list_chunks(self, tenant_id: str) -> list[dict]:
        return [chunk for chunk in self.store.state["chunks"] if chunk["tenant_id"] == tenant_id]

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


def connect_repository(path: Path | None = None) -> RepositorySession:
    return RepositorySession(path)
