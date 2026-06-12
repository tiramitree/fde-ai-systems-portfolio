from __future__ import annotations

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
CLIENT_BUDGET_MS = 5_000
REPORTED_BUDGET_MS = 2_500
SAMPLES_PER_SERVICE = 3


@dataclass(frozen=True)
class Service:
    name: str
    path: Path
    preferred_port: int
    health_app: str
    route: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str


SERVICES = [
    Service(
        name="secure-enterprise-knowledge-copilot",
        path=ROOT / "secure-enterprise-knowledge-copilot",
        preferred_port=9111,
        health_app="secure-enterprise-knowledge-copilot",
        route="/api/query",
        payload={
            "user_id": "alice",
            "question": "How many days per week can employees work remotely?",
        },
    ),
    Service(
        name="regulated-customer-operations-agent",
        path=ROOT / "regulated-customer-operations-agent",
        preferred_port=9112,
        health_app="regulated-customer-operations-agent",
        route="/api/agent",
        payload={
            "user_id": "ivy",
            "case_id": "case-1001",
            "message": "Check whether Market Blue still has an active listing for the recalled RX-900 product.",
        },
    ),
    Service(
        name="ai-reliability-incident-console",
        path=ROOT / "ai-reliability-incident-console",
        preferred_port=9113,
        health_app="ai-reliability-incident-console",
        route="/api/triage",
        payload={
            "user_id": "maya",
            "release_id": "rel-2026-06-01",
            "incident_id": "inc-2026-014",
        },
    ),
]


def check(condition: bool, name: str, detail: str) -> Check:
    return Check(name=name, passed=condition, detail=detail)


def reserve_port(preferred: int, used: set[int]) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        if preferred not in used:
            try:
                sock.bind(("127.0.0.1", preferred))
                used.add(preferred)
                return preferred
            except OSError:
                pass
        while True:
            sock.bind(("127.0.0.1", 0))
            port = int(sock.getsockname()[1])
            if port not in used:
                used.add(port)
                return port


def request_json(method: str, url: str, payload: dict[str, Any] | None = None) -> tuple[int, dict[str, Any], float]:
    data = json.dumps(payload or {}).encode("utf-8") if method == "POST" else None
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method=method,
    )
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            elapsed_ms = (time.perf_counter() - start) * 1000
            return response.status, json.loads(response.read().decode("utf-8")), elapsed_ms
    except urllib.error.HTTPError as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return exc.code, json.loads(exc.read().decode("utf-8")), elapsed_ms


def wait_for_health(service: Service, base_url: str, seconds: int = 15) -> bool:
    for _ in range(seconds):
        try:
            status, payload, _ = request_json("GET", f"{base_url}/api/health")
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


def numeric_latency(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    return None


def trace_latency(service: Service, trace: dict[str, Any]) -> float | None:
    if service.name == "secure-enterprise-knowledge-copilot":
        payload = trace.get("payload", {})
        return numeric_latency(payload.get("latency_ms")) if isinstance(payload, dict) else None
    result = trace.get("result", {})
    return numeric_latency(result.get("latency_ms")) if isinstance(result, dict) else None


def trace_for(base_url: str, trace_id: str) -> dict[str, Any]:
    status, payload, _ = request_json("GET", f"{base_url}/api/traces?limit=20")
    if status != 200:
        return {}
    traces = payload.get("traces", [])
    if not isinstance(traces, list):
        return {}
    return next((item for item in traces if isinstance(item, dict) and item.get("id") == trace_id), {})


def verify_service(service: Service, port: int, temp_root: Path) -> list[Check]:
    base_url = f"http://127.0.0.1:{port}"
    state_path = temp_root / f"{service.name}-latency-runtime_state.json"
    checks: list[Check] = []
    client_latencies: list[float] = []
    reported_latencies: list[float] = []
    trace_latencies: list[float] = []
    process = start_service(service, port, state_path)
    try:
        healthy = wait_for_health(service, base_url)
        checks.append(check(healthy, f"{service.name} latency health", base_url))
        if not healthy:
            return checks

        for sample_index in range(SAMPLES_PER_SERVICE):
            status, payload, elapsed_ms = request_json("POST", f"{base_url}{service.route}", service.payload)
            trace_id = str(payload.get("trace_id", ""))
            reported = numeric_latency(payload.get("latency_ms"))
            trace = trace_for(base_url, trace_id) if trace_id else {}
            observed_trace_latency = trace_latency(service, trace)
            client_latencies.append(elapsed_ms)
            if reported is not None:
                reported_latencies.append(reported)
            if observed_trace_latency is not None:
                trace_latencies.append(observed_trace_latency)
            checks.append(
                check(
                    status == 200 and bool(trace_id),
                    f"{service.name} sample {sample_index + 1} returns trace",
                    f"status={status}; trace={trace_id or 'missing'}",
                )
            )
            checks.append(
                check(
                    reported is not None and 0 <= reported <= REPORTED_BUDGET_MS,
                    f"{service.name} sample {sample_index + 1} reported latency budget",
                    f"latency_ms={reported}; budget={REPORTED_BUDGET_MS}",
                )
            )
            checks.append(
                check(
                    observed_trace_latency is not None and 0 <= observed_trace_latency <= REPORTED_BUDGET_MS,
                    f"{service.name} sample {sample_index + 1} trace latency budget",
                    f"trace_latency_ms={observed_trace_latency}; budget={REPORTED_BUDGET_MS}",
                )
            )
            checks.append(
                check(
                    elapsed_ms <= CLIENT_BUDGET_MS,
                    f"{service.name} sample {sample_index + 1} client latency budget",
                    f"client_ms={elapsed_ms:.2f}; budget={CLIENT_BUDGET_MS}",
                )
            )
    finally:
        stop_processes([process])

    checks.append(
        check(
            len(reported_latencies) == SAMPLES_PER_SERVICE and max(reported_latencies) <= REPORTED_BUDGET_MS,
            f"{service.name} reported latency summary",
            f"max={max(reported_latencies) if reported_latencies else 'missing'}; samples={len(reported_latencies)}",
        )
    )
    checks.append(
        check(
            len(trace_latencies) == SAMPLES_PER_SERVICE and max(trace_latencies) <= REPORTED_BUDGET_MS,
            f"{service.name} trace latency summary",
            f"max={max(trace_latencies) if trace_latencies else 'missing'}; samples={len(trace_latencies)}",
        )
    )
    checks.append(
        check(
            len(client_latencies) == SAMPLES_PER_SERVICE and max(client_latencies) <= CLIENT_BUDGET_MS,
            f"{service.name} client latency summary",
            f"max={max(client_latencies):.2f}; samples={len(client_latencies)}",
        )
    )
    return checks


def main() -> int:
    checks: list[Check] = []
    used_ports: set[int] = set()
    ports = {service.name: reserve_port(service.preferred_port, used_ports) for service in SERVICES}
    with tempfile.TemporaryDirectory(prefix="fde-runtime-latency-") as temp_dir:
        temp_root = Path(temp_dir)
        for service in SERVICES:
            checks.extend(verify_service(service, ports[service.name], temp_root))

    for item in checks:
        status = "PASS" if item.passed else "FAIL"
        print(f"[{status}] {item.name}: {item.detail}")

    passed = sum(1 for item in checks if item.passed)
    total = len(checks)
    print(f"\nRuntime latency budget checks: {passed}/{total} passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
