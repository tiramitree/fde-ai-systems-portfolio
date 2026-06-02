from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
STATE_PATH = DATA_DIR / "runtime_state.json"
SEED_PATH = DATA_DIR / "seed_state.json"
STORE_LOCK = threading.RLock()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def empty_state() -> dict:
    return {
        "users": [],
        "releases": [],
        "incidents": [],
        "eval_runs": [],
        "runbooks": [],
        "triage_decisions": [],
        "traces": [],
        "audit_events": [],
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


def init_state(reset: bool = False, state_path: Path = STATE_PATH, seed_path: Path = SEED_PATH) -> None:
    with STORE_LOCK:
        store = JsonStore(state_path)
        if reset or not store.state["users"]:
            payload = json.loads(seed_path.read_text(encoding="utf-8"))
            store.state = empty_state()
            for key in ("users", "releases", "incidents", "eval_runs", "runbooks"):
                store.state[key] = payload[key]
            store.save()


def get_user(store: JsonStore, user_id: str) -> dict | None:
    return next((user for user in store.state["users"] if user["id"] == user_id), None)


def list_users(store: JsonStore) -> list[dict]:
    return sorted(store.state["users"], key=lambda user: (user["role"], user["id"]))


def get_release(store: JsonStore, release_id: str) -> dict | None:
    return next((release for release in store.state["releases"] if release["id"] == release_id), None)


def list_releases(store: JsonStore) -> list[dict]:
    return sorted(store.state["releases"], key=lambda release: release["created_at"], reverse=True)


def get_incident(store: JsonStore, incident_id: str) -> dict | None:
    return next((incident for incident in store.state["incidents"] if incident["id"] == incident_id), None)


def list_incidents(store: JsonStore) -> list[dict]:
    return sorted(store.state["incidents"], key=lambda incident: incident["opened_at"], reverse=True)


def list_eval_runs(store: JsonStore) -> list[dict]:
    return sorted(store.state["eval_runs"], key=lambda run: run["created_at"], reverse=True)


def latest_eval_run(store: JsonStore) -> dict | None:
    runs = list_eval_runs(store)
    return runs[0] if runs else None


def get_eval_run(store: JsonStore, release_id: str) -> dict | None:
    runs = [run for run in store.state["eval_runs"] if run["release_id"] == release_id]
    if not runs:
        return None
    return sorted(runs, key=lambda run: run["created_at"], reverse=True)[0]


def list_runbooks(store: JsonStore) -> list[dict]:
    return sorted(store.state["runbooks"], key=lambda runbook: runbook["id"])


def append_audit(store: JsonStore, user_id: str, action: str, details: dict) -> None:
    store.state["audit_events"].append(
        {
            "id": len(store.state["audit_events"]) + 1,
            "created_at": utc_now(),
            "user_id": user_id,
            "action": action,
            "details": details,
        }
    )


def append_trace(store: JsonStore, trace: dict) -> None:
    store.state["traces"].append(trace)


def append_triage_decision(store: JsonStore, decision: dict) -> None:
    store.state["triage_decisions"].append(decision)


def append_eval_run(store: JsonStore, run: dict) -> None:
    store.state["eval_runs"].append(run)


def list_traces(store: JsonStore, limit: int = 25) -> list[dict]:
    return sorted(store.state["traces"], key=lambda item: item["created_at"], reverse=True)[:limit]


def list_audit(store: JsonStore, limit: int = 50) -> list[dict]:
    return sorted(store.state["audit_events"], key=lambda item: item["created_at"], reverse=True)[:limit]
