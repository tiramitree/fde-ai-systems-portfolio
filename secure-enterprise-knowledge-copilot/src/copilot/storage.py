from __future__ import annotations

import hashlib
import json
import os
import threading
from pathlib import Path

from .chunking import SOURCE_SPAN_UNIT, chunk_text_with_spans
from .embeddings import embed_chunk
from .source_parsing import PARSER_CONTRACT_VERSION, SUPPORTED_MIME_TYPES, parse_source_content
from .source_scanning import scan_source_content


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
STATE_PATH = DATA_DIR / "runtime_state.json"
STATE_PATH_ENV = "COPILOT_STATE_PATH"
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


def state_path() -> Path:
    override = os.getenv(STATE_PATH_ENV, "").strip()
    return Path(override) if override else STATE_PATH


class JsonStore:
    def __init__(self, path: Path | None = None):
        self.path = path if path is not None else state_path()
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
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            try:
                self.state = json.loads(self.path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                self.state = empty_state()

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.state, indent=2), encoding="utf-8")


def connect(path: Path | None = None) -> JsonStore:
    return JsonStore(path)


def init_db(reset: bool = False, state_path: Path | None = None, seed_path: Path = SEED_PATH) -> None:
    with STORE_LOCK:
        store = JsonStore(state_path)
        if reset or not store.state["users"]:
            seed(store, seed_path)
            store.save()


def _seed_source_mime(doc: dict) -> str:
    source_mime = str(doc.get("source_mime") or "text/plain").strip().lower()
    if source_mime not in SUPPORTED_MIME_TYPES:
        doc_id = str(doc.get("id") or "unknown")
        raise ValueError(f"Unsupported seed source_mime for {doc_id}: {source_mime}")
    return source_mime


def prepare_seed_document(doc: dict) -> dict:
    raw_body = str(doc.get("body") or "")
    source_mime = _seed_source_mime(doc)
    parsed_source = parse_source_content(raw_body, source_mime)
    source_scan = scan_source_content(raw_body, parsed_source.text)
    source_hash = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()
    lifecycle_state = str(doc.get("source_lifecycle_state") or DEFAULT_SOURCE_LIFECYCLE_STATE).strip()
    return {
        **doc,
        "body": parsed_source.text,
        "source_mime": source_mime,
        "source_hash": source_hash,
        "parser_name": parsed_source.parser_name,
        "parser_contract_version": PARSER_CONTRACT_VERSION,
        "parser_metadata": parsed_source.metadata,
        "parser_warnings": list(parsed_source.warnings),
        "parser_warning_count": len(parsed_source.warnings),
        "source_scan": source_scan,
        "source_connector": str(doc.get("source_connector") or "manual").strip() or "manual",
        "external_id": str(doc.get("external_id") or doc.get("id") or "").strip(),
        "acl_source": str(doc.get("acl_source") or "seed_fixture").strip() or "seed_fixture",
        "allowed_roles_source": str(doc.get("allowed_roles_source") or "seed_fixture").strip() or "seed_fixture",
        "sync_cursor": str(doc.get("sync_cursor") or "").strip(),
        "source_lifecycle_state": lifecycle_state or DEFAULT_SOURCE_LIFECYCLE_STATE,
    }


def build_seed_chunks(doc: dict) -> list[dict]:
    chunks = []
    for idx, chunk in enumerate(chunk_text_with_spans(doc["body"])):
        embedding = embed_chunk(doc["title"], chunk.text)
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
                "source_mime": doc["source_mime"],
                "source_hash": doc["source_hash"],
                "version": doc["version"],
                "updated_at": doc["updated_at"],
                "parser_name": doc["parser_name"],
                "parser_contract_version": doc["parser_contract_version"],
                "parser_metadata": doc["parser_metadata"],
                "parser_warnings": doc["parser_warnings"],
                "parser_warning_count": doc["parser_warning_count"],
                "source_scan": doc["source_scan"],
                "source_connector": doc["source_connector"],
                "external_id": doc["external_id"],
                "acl_source": doc["acl_source"],
                "sync_cursor": doc["sync_cursor"],
                "allowed_roles_source": doc["allowed_roles_source"],
                "source_acl_version": doc.get("source_acl_version", ""),
                "source_acl_permission_id": doc.get("source_acl_permission_id", ""),
                "source_acl_principal_count": doc.get("source_acl_principal_count", 0),
                "source_lifecycle_state": doc["source_lifecycle_state"],
                "superseded_by": doc.get("superseded_by", ""),
                "embedding": embedding.vector,
                "chunk_source_span_unit": SOURCE_SPAN_UNIT,
                **embedding.metadata(),
            }
        )
    return chunks


def seed(store: JsonStore, seed_path: Path = SEED_PATH) -> None:
    payload = json.loads(seed_path.read_text(encoding="utf-8"))
    store.state = empty_state()
    store.state["users"] = payload["users"]

    documents = []
    chunks = []
    for doc in payload["documents"]:
        prepared_doc = prepare_seed_document(doc)
        documents.append(prepared_doc)
        chunks.extend(build_seed_chunks(prepared_doc))

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
