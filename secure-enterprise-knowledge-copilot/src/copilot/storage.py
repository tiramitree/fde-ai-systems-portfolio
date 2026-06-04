from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
STATE_PATH = DATA_DIR / "runtime_state.json"
SEED_PATH = DATA_DIR / "seed_documents.json"
EVAL_CASES_PATH = DATA_DIR / "eval_cases.json"
STORE_LOCK = threading.RLock()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def chunk_text(text: str, max_chars: int = 900) -> list[str]:
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    for paragraph in paragraphs:
        if current and current_len + len(paragraph) > max_chars:
            chunks.append("\n\n".join(current))
            current = []
            current_len = 0
        current.append(paragraph)
        current_len += len(paragraph)

    if current:
        chunks.append("\n\n".join(current))
    return chunks


def empty_state() -> dict:
    return {
        "users": [],
        "documents": [],
        "chunks": [],
        "traces": [],
        "audit_events": [],
        "eval_runs": [],
    }


class JsonStore:
    def __init__(self, path: Path = STATE_PATH):
        self.path = path
        self.state = empty_state()
        self.load()

    def __enter__(self) -> "JsonStore":
        STORE_LOCK.acquire()
        self.load()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc_type is None:
            self.save()
        STORE_LOCK.release()

    def load(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            try:
                self.state = json.loads(self.path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                self.state = empty_state()

    def save(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.state, indent=2), encoding="utf-8")


def connect(path: Path = STATE_PATH) -> JsonStore:
    return JsonStore(path)


def init_db(reset: bool = False, state_path: Path = STATE_PATH, seed_path: Path = SEED_PATH) -> None:
    with STORE_LOCK:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        store = JsonStore(state_path)
        if reset or not store.state["users"]:
            seed(store, seed_path)
            store.save()


def seed(store: JsonStore, seed_path: Path = SEED_PATH) -> None:
    payload = json.loads(seed_path.read_text(encoding="utf-8"))
    store.state = empty_state()
    store.state["users"] = payload["users"]

    documents = []
    chunks = []
    for doc in payload["documents"]:
        documents.append(doc)
        for idx, text in enumerate(chunk_text(doc["body"])):
            chunks.append(
                {
                    "id": f"{doc['id']}::chunk-{idx + 1}",
                    "doc_id": doc["id"],
                    "chunk_index": idx,
                    "title": doc["title"],
                    "text": text,
                    "tenant_id": doc["tenant_id"],
                    "classification": doc["classification"],
                    "allowed_roles": doc["allowed_roles"],
                    "source_url": doc["source_url"],
                    "version": doc["version"],
                    "updated_at": doc["updated_at"],
                }
            )

    store.state["documents"] = documents
    store.state["chunks"] = chunks


def get_user(store: JsonStore, user_id: str) -> dict | None:
    return next((user for user in store.state["users"] if user["id"] == user_id), None)


def list_users(store: JsonStore) -> list[dict]:
    return sorted(store.state["users"], key=lambda user: (user["role"], user["id"]))


def list_visible_documents(store: JsonStore, user: dict) -> list[dict]:
    docs = []
    for doc in store.state["documents"]:
        if doc["tenant_id"] == user["tenant_id"] and user["role"] in doc["allowed_roles"]:
            visible = {key: value for key, value in doc.items() if key != "body"}
            docs.append(visible)
    return docs


def list_chunks(store: JsonStore, tenant_id: str) -> list[dict]:
    return [chunk for chunk in store.state["chunks"] if chunk["tenant_id"] == tenant_id]


def insert_trace(store: JsonStore, trace_id: str, user_id: str, question: str, payload: dict) -> None:
    store.state["traces"].append(
        {
            "id": trace_id,
            "created_at": utc_now(),
            "user_id": user_id,
            "question": question,
            "payload": payload,
        }
    )


def insert_audit(store: JsonStore, user_id: str, action: str, details: dict) -> None:
    next_id = len(store.state["audit_events"]) + 1
    store.state["audit_events"].append(
        {
            "id": next_id,
            "created_at": utc_now(),
            "user_id": user_id,
            "action": action,
            "details": details,
        }
    )


def list_traces(store: JsonStore, limit: int = 25) -> list[dict]:
    traces = sorted(store.state["traces"], key=lambda item: item["created_at"], reverse=True)
    return traces[:limit]


def list_audit_events(store: JsonStore, limit: int = 50) -> list[dict]:
    events = sorted(store.state["audit_events"], key=lambda item: item["created_at"], reverse=True)
    return events[:limit]


def insert_eval_run(store: JsonStore, payload: dict) -> None:
    store.state["eval_runs"].append(payload)


def latest_eval_run(store: JsonStore) -> dict | None:
    if not store.state["eval_runs"]:
        return None
    return sorted(store.state["eval_runs"], key=lambda item: item["created_at"], reverse=True)[0]


def _record_count(payload: dict | list) -> int:
    if isinstance(payload, list):
        return len(payload)
    return sum(len(value) for value in payload.values() if isinstance(value, list))


def _scenario_file(path: Path, kind: str) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        "path": f"data/{path.name}",
        "kind": kind,
        "record_count": _record_count(payload),
        "content": payload,
    }


def load_scenario_snapshot() -> dict:
    return {
        "draft_mode": "browser_local_storage",
        "write_policy": "read_only_seed_snapshot",
        "files": [
            _scenario_file(SEED_PATH, "seed"),
            _scenario_file(EVAL_CASES_PATH, "eval"),
        ],
    }
