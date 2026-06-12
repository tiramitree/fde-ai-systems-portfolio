from __future__ import annotations

import hashlib
import json
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Service:
    name: str
    path: Path
    preferred_port: int
    health_app: str
    required_keys: tuple[str, ...]

    @property
    def default_state_path(self) -> Path:
        return self.path / "data" / "runtime_state.json"


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str


SERVICES = [
    Service(
        name="secure-enterprise-knowledge-copilot",
        path=ROOT / "secure-enterprise-knowledge-copilot",
        preferred_port=9091,
        health_app="secure-enterprise-knowledge-copilot",
        required_keys=("users", "documents", "traces", "audit_events"),
    ),
    Service(
        name="regulated-customer-operations-agent",
        path=ROOT / "regulated-customer-operations-agent",
        preferred_port=9092,
        health_app="regulated-customer-operations-agent",
        required_keys=("users", "cases", "traces", "audit_events", "approval_requests", "action_outbox"),
    ),
    Service(
        name="ai-reliability-incident-console",
        path=ROOT / "ai-reliability-incident-console",
        preferred_port=9093,
        health_app="ai-reliability-incident-console",
        required_keys=("users", "releases", "incidents", "traces", "audit_events"),
    ),
]


def check(condition: bool, name: str, detail: str) -> Check:
    return Check(name=name, passed=condition, detail=detail)


def file_sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reserve_port(preferred: int) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(("127.0.0.1", preferred))
            return preferred
        except OSError:
            sock.bind(("127.0.0.1", 0))
            return int(sock.getsockname()[1])


def request_json(method: str, url: str, payload: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
    data = json.dumps(payload or {}).encode("utf-8") if method == "POST" else None
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def wait_for_health(service: Service, base_url: str, seconds: int = 15) -> bool:
    for _ in range(seconds):
        try:
            status, payload = request_json("GET", f"{base_url}/api/health")
            if status == 200 and payload == {"status": "ok", "app": service.health_app}:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


def start_service(service: Service, port: int, state_path: Path) -> subprocess.Popen:
    return subprocess.Popen(
        [
            sys.executable,
            "-B",
            "app.py",
            "--reset",
            "--state-path",
            str(state_path),
            "--port",
            str(port),
        ],
        cwd=service.path,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )


def stop_processes(processes: list[subprocess.Popen]) -> None:
    for process in processes:
        if process.poll() is None:
            process.terminate()
    for process in processes:
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def run_service_flow(service: Service, base_url: str) -> tuple[int, dict[str, Any]]:
    if service.name == "secure-enterprise-knowledge-copilot":
        return request_json(
            "POST",
            f"{base_url}/api/query",
            {
                "user_id": "alice",
                "question": "How many days per week can employees work remotely?",
            },
        )
    if service.name == "regulated-customer-operations-agent":
        return request_json(
            "POST",
            f"{base_url}/api/agent",
            {
                "user_id": "ivy",
                "case_id": "case-1001",
                "message": "Check whether Market Blue still has an active listing for the recalled RX-900 product.",
            },
        )
    if service.name == "ai-reliability-incident-console":
        return request_json(
            "POST",
            f"{base_url}/api/triage",
            {
                "user_id": "maya",
                "release_id": "rel-2026-06-01",
                "incident_id": "inc-2026-014",
            },
        )
    raise ValueError(f"Unknown service: {service.name}")


def trace_id_from_payload(payload: dict[str, Any]) -> str:
    trace_id = payload.get("trace_id")
    return trace_id if isinstance(trace_id, str) else ""


def state_contains_trace(state: dict[str, Any], trace_id: str) -> bool:
    traces = state.get("traces", [])
    return isinstance(traces, list) and any(item.get("id") == trace_id for item in traces if isinstance(item, dict))


def verify_service(service: Service, temp_root: Path) -> list[Check]:
    port = reserve_port(service.preferred_port)
    base_url = f"http://127.0.0.1:{port}"
    isolated_state_path = temp_root / f"{service.name}-runtime_state.json"
    default_before = file_sha256(service.default_state_path)
    checks: list[Check] = []
    process = start_service(service, port, isolated_state_path)
    try:
        healthy = wait_for_health(service, base_url)
        checks.append(check(healthy, f"{service.name} isolated health", base_url))
        if not healthy:
            return checks

        status, payload = run_service_flow(service, base_url)
        trace_id = trace_id_from_payload(payload)
        checks.append(check(status == 200 and bool(trace_id), f"{service.name} isolated flow writes trace", f"status={status}; trace={trace_id}"))
        checks.append(check(isolated_state_path.exists(), f"{service.name} isolated state file exists", isolated_state_path.name))

        state = json.loads(isolated_state_path.read_text(encoding="utf-8"))
        missing_keys = [key for key in service.required_keys if key not in state]
        checks.append(check(not missing_keys, f"{service.name} isolated state schema", f"missing={missing_keys}"))
        checks.append(check(state_contains_trace(state, trace_id), f"{service.name} isolated state owns trace", trace_id))
    finally:
        stop_processes([process])

    default_after = file_sha256(service.default_state_path)
    default_text = service.default_state_path.read_text(encoding="utf-8") if service.default_state_path.exists() else ""
    trace_id = ""
    if isolated_state_path.exists():
        try:
            traces = json.loads(isolated_state_path.read_text(encoding="utf-8")).get("traces", [])
            if traces and isinstance(traces[0], dict):
                trace_id = str(traces[0].get("id", ""))
        except json.JSONDecodeError:
            trace_id = ""
    checks.append(
        check(
            default_before == default_after,
            f"{service.name} default state unchanged",
            f"before={default_before or 'missing'}; after={default_after or 'missing'}",
        )
    )
    checks.append(
        check(
            not trace_id or trace_id not in default_text,
            f"{service.name} default state excludes isolated trace",
            trace_id or "no-trace",
        )
    )
    return checks


def main() -> int:
    checks: list[Check] = []
    with tempfile.TemporaryDirectory(prefix="fde-runtime-state-isolation-") as temp_dir:
        temp_root = Path(temp_dir)
        for service in SERVICES:
            checks.extend(verify_service(service, temp_root))

    for item in checks:
        status = "PASS" if item.passed else "FAIL"
        print(f"[{status}] {item.name}: {item.detail}")

    passed = sum(1 for item in checks if item.passed)
    total = len(checks)
    print(f"\nRuntime state isolation checks: {passed}/{total} passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
