from __future__ import annotations

import json
import threading
from pathlib import Path

from .chunking import SOURCE_SPAN_UNIT, chunk_text_with_spans
from .embeddings import embed_chunk


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
STATE_PATH = DATA_DIR / "runtime_state.json"
SEED_PATH = DATA_DIR / "seed_documents.json"
EVAL_CASES_PATH = DATA_DIR / "eval_cases.json"
STORE_LOCK = threading.RLock()
DEFAULT_SOURCE_LIFECYCLE_STATE = "active"


def empty_state() -> dict:
    return {
        "users": [],
        "documents": [],
        "chunks": [],
        "traces": [],
        "audit_events": [],
        "eval_runs": [],
        "ingestion_jobs": [],
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
        for idx, chunk in enumerate(chunk_text_with_spans(doc["body"])):
            embedding = embed_chunk(doc["title"], chunk.text)
            lifecycle_state = doc.get("source_lifecycle_state", DEFAULT_SOURCE_LIFECYCLE_STATE)
            chunks.append(
                {
                    "id": f"{doc['id']}::chunk-{idx + 1}",
                    "doc_id": doc["id"],
                    "chunk_index": idx,
                    "title": doc["title"],
                    "text": chunk.text,
                    "source_span": chunk.source_span,
                    "tenant_id": doc["tenant_id"],
                    "classification": doc["classification"],
                    "allowed_roles": doc["allowed_roles"],
                    "allowed_groups": doc.get("allowed_groups", []),
                    "source_acl_principals": doc.get("source_acl_principals", []),
                    "source_url": doc["source_url"],
                    "version": doc["version"],
                    "updated_at": doc["updated_at"],
                    "source_lifecycle_state": lifecycle_state,
                    "superseded_by": doc.get("superseded_by", ""),
                    "embedding": embedding.vector,
                    "chunk_source_span_unit": SOURCE_SPAN_UNIT,
                    **embedding.metadata(),
                }
            )

    store.state["documents"] = documents
    store.state["chunks"] = chunks


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
