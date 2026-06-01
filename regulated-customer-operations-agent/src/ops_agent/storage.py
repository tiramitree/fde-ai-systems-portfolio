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
        "policies": [],
        "products": [],
        "sellers": [],
        "listings": [],
        "cases": [],
        "violations": [],
        "approval_requests": [],
        "notices": [],
        "followups": [],
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


def init_state(reset: bool = False, state_path: Path = STATE_PATH, seed_path: Path = SEED_PATH) -> None:
    with STORE_LOCK:
        store = JsonStore(state_path)
        if reset or not store.state["users"]:
            payload = json.loads(seed_path.read_text(encoding="utf-8"))
            store.state = empty_state()
            for key in (
                "users",
                "policies",
                "products",
                "sellers",
                "listings",
                "cases",
            ):
                store.state[key] = payload[key]
            store.save()


def get_user(store: JsonStore, user_id: str) -> dict | None:
    return next((user for user in store.state["users"] if user["id"] == user_id), None)


def list_users(store: JsonStore) -> list[dict]:
    return sorted(store.state["users"], key=lambda user: (user["role"], user["id"]))


def get_case(store: JsonStore, case_id: str) -> dict | None:
    return next((case for case in store.state["cases"] if case["id"] == case_id), None)


def list_cases(store: JsonStore) -> list[dict]:
    return sorted(store.state["cases"], key=lambda case: case["id"])


def get_listing(store: JsonStore, listing_id: str) -> dict | None:
    return next((listing for listing in store.state["listings"] if listing["id"] == listing_id), None)


def get_product(store: JsonStore, product_id: str) -> dict | None:
    return next((product for product in store.state["products"] if product["id"] == product_id), None)


def get_seller(store: JsonStore, seller_id: str) -> dict | None:
    return next((seller for seller in store.state["sellers"] if seller["id"] == seller_id), None)


def get_policy(store: JsonStore, policy_id: str) -> dict | None:
    return next((policy for policy in store.state["policies"] if policy["id"] == policy_id), None)


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


def list_traces(store: JsonStore, limit: int = 25) -> list[dict]:
    return sorted(store.state["traces"], key=lambda item: item["created_at"], reverse=True)[:limit]


def list_audit(store: JsonStore, limit: int = 50) -> list[dict]:
    return sorted(store.state["audit_events"], key=lambda item: item["created_at"], reverse=True)[:limit]


def list_approvals(store: JsonStore) -> list[dict]:
    return sorted(store.state["approval_requests"], key=lambda item: item["created_at"], reverse=True)


def append_eval_run(store: JsonStore, run: dict) -> None:
    store.state["eval_runs"].append(run)


def latest_eval_run(store: JsonStore) -> dict | None:
    if not store.state["eval_runs"]:
        return None
    return sorted(store.state["eval_runs"], key=lambda item: item["created_at"], reverse=True)[0]
