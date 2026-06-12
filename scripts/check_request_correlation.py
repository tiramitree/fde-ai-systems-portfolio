from __future__ import annotations

import json
import os
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
class Project:
    name: str
    path: Path
    port_hint: int
    health_app: str
    request_id: str
    post_path: str
    payload: dict[str, Any]
    expected_audit_action: str


PROJECTS = [
    Project(
        name="Secure Enterprise Knowledge Copilot",
        path=ROOT / "secure-enterprise-knowledge-copilot",
        port_hint=9161,
        health_app="secure-enterprise-knowledge-copilot",
        request_id="corr-p1-query-0001",
        post_path="/api/query",
        payload={"user_id": "alice", "question": "How many days per week can employees work remotely?"},
        expected_audit_action="query_answered",
    ),
    Project(
        name="Regulated Customer Operations Agent",
        path=ROOT / "regulated-customer-operations-agent",
        port_hint=9162,
        health_app="regulated-customer-operations-agent",
        request_id="corr-p2-agent-0001",
        post_path="/api/agent",
        payload={
            "user_id": "ivy",
            "case_id": "case-1001",
            "message": "Check whether Market Blue still has an active listing for the recalled RX-900 product.",
        },
        expected_audit_action="agent_message_processed",
    ),
    Project(
        name="AI Reliability Incident Console",
        path=ROOT / "ai-reliability-incident-console",
        port_hint=9163,
        health_app="ai-reliability-incident-console",
        request_id="corr-p3-triage-0001",
        post_path="/api/triage",
        payload={"user_id": "maya", "release_id": "rel-2026-06-01", "incident_id": "inc-2026-014"},
        expected_audit_action="incident_triaged",
    ),
]


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


def service_state_path(state_root: Path, project: Project) -> Path:
    return state_root / f"{project.path.name}-request-correlation-runtime_state.json"


def start_service(project: Project, port: int, state_root: Path) -> subprocess.Popen:
    env = os.environ.copy()
    env["COPILOT_REPOSITORY"] = "json"
    env["FDE_RATE_LIMIT_REQUESTS_PER_WINDOW"] = "100"
    env["FDE_RATE_LIMIT_BUDGET_PER_WINDOW"] = "1000"
    return subprocess.Popen(
        [
            sys.executable,
            "-B",
            "app.py",
            "--reset",
            "--state-path",
            str(service_state_path(state_root, project)),
            "--port",
            str(port),
        ],
        cwd=project.path,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )


def normalize_headers(items: Any) -> dict[str, str]:
    return {str(key).lower(): str(value) for key, value in items}


def request_json(
    method: str,
    port: int,
    path: str,
    body: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> tuple[int, dict[str, Any], dict[str, str]]:
    data = json.dumps(body or {}).encode("utf-8") if method == "POST" else None
    request_headers = {"User-Agent": "fde-request-correlation", **(headers or {})}
    if data is not None:
        request_headers["Content-Type"] = "application/json"
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=data,
        headers=request_headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, json.loads(response.read().decode("utf-8")), normalize_headers(response.headers.items())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8")), normalize_headers(exc.headers.items())


def wait_for_health(project: Project, port: int, seconds: int = 15) -> bool:
    for _ in range(seconds):
        try:
            status, payload, _ = request_json("GET", port, "/api/health")
            if status == 200 and payload == {"status": "ok", "app": project.health_app}:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


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


def read(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")


def require_text(text: str, phrase: str, label: str, failures: list[str]) -> None:
    if phrase not in text:
        failures.append(f"{label}: missing {phrase!r}")


def find_trace(base_url_port: int, trace_id: str) -> dict[str, Any]:
    status, payload, _ = request_json("GET", base_url_port, "/api/traces?limit=20")
    if status != 200:
        return {}
    traces = payload.get("traces", [])
    if not isinstance(traces, list):
        return {}
    return next((item for item in traces if isinstance(item, dict) and item.get("id") == trace_id), {})


def find_audit_event(base_url_port: int, trace_id: str, action: str) -> dict[str, Any]:
    status, payload, _ = request_json("GET", base_url_port, "/api/audit?limit=50")
    if status != 200:
        return {}
    events = payload.get("events", [])
    if not isinstance(events, list):
        return {}
    return next(
        (
            event
            for event in events
            if isinstance(event, dict)
            and event.get("action") == action
            and isinstance(event.get("details"), dict)
            and event["details"].get("trace_id") == trace_id
        ),
        {},
    )


def nested_request_id(trace: dict[str, Any]) -> str:
    payload = trace.get("payload", {})
    result = trace.get("result", {})
    if isinstance(payload, dict) and payload.get("request_id"):
        return str(payload["request_id"])
    if isinstance(result, dict) and result.get("request_id"):
        return str(result["request_id"])
    return ""


def check_project(project: Project, port: int, failures: list[str]) -> None:
    status, payload, headers = request_json(
        "POST",
        port,
        project.post_path,
        project.payload,
        headers={"X-Request-ID": project.request_id},
    )
    trace_id = str(payload.get("trace_id", ""))
    if status != 200 or not trace_id:
        failures.append(f"{project.name}: expected successful correlated response, got {status} {payload!r}")
        return
    if headers.get("x-request-id") != project.request_id:
        failures.append(f"{project.name}: response header did not echo governed request id")
    if payload.get("request_id") != project.request_id:
        failures.append(f"{project.name}: response payload missing matching request_id")

    trace = find_trace(port, trace_id)
    if not trace:
        failures.append(f"{project.name}: persisted trace not found for {trace_id}")
    elif trace.get("request_id") != project.request_id or nested_request_id(trace) != project.request_id:
        failures.append(f"{project.name}: trace request_id mismatch: {trace!r}")

    audit = find_audit_event(port, trace_id, project.expected_audit_action)
    details = audit.get("details", {}) if isinstance(audit, dict) else {}
    if not audit:
        failures.append(f"{project.name}: linked audit event not found for {trace_id}")
    elif details.get("request_id") != project.request_id:
        failures.append(f"{project.name}: audit request_id mismatch: {audit!r}")


def check_static_wiring(failures: list[str]) -> None:
    helper_text = read("local_request_governance.py")
    for phrase in ["class GovernedHeaders", "def headers_with_request_context(", "REQUEST_ID_HEADER"]:
        require_text(helper_text, phrase, "local_request_governance.py", failures)

    expectations = {
        "secure-enterprise-knowledge-copilot/app.py": ["headers_with_request_context", "API.post(parsed.path, body, headers)"],
        "regulated-customer-operations-agent/app.py": ["headers_with_request_context", "API.post(parsed.path, body, headers)"],
        "ai-reliability-incident-console/app.py": ["headers_with_request_context", "API.post(parsed.path, body, headers)"],
        "secure-enterprise-knowledge-copilot/src/copilot/answering.py": ["request_id: str = \"\"", "_with_request_id("],
        "regulated-customer-operations-agent/src/ops_agent/agent.py": ["request_id: str = \"\"", "_with_request_id("],
        "ai-reliability-incident-console/src/reliability_console/triage.py": ["request_id: str = \"\"", "_with_request_id("],
    }
    for rel_path, phrases in expectations.items():
        text = read(rel_path)
        for phrase in phrases:
            require_text(text, phrase, rel_path, failures)


def check_docs(failures: list[str]) -> None:
    expectations = {
        "docs/api_contracts.md": [
            "request_id",
            "response, persisted trace, and linked audit event",
            "python -B scripts/dev.py request-correlation",
        ],
        "docs/observability_integrity.md": [
            "request_id",
            "python -B scripts/dev.py request-correlation",
        ],
        "docs/portfolio_evidence_matrix.md": [
            "Core API request ids are correlated across responses, traces, and audit events.",
            "scripts/check_request_correlation.py",
        ],
        "PROJECT_CONTENT_INDEX.md": [
            "scripts/check_request_correlation.py",
            "python -B scripts/dev.py request-correlation",
        ],
        "README.md": [
            "python -B scripts/dev.py request-correlation",
            "Request correlation",
        ],
    }
    for rel_path, phrases in expectations.items():
        text = read(rel_path)
        for phrase in phrases:
            require_text(text, phrase, rel_path, failures)


def check_runtime(failures: list[str]) -> None:
    used_ports: set[int] = set()
    processes: list[subprocess.Popen] = []
    with tempfile.TemporaryDirectory(prefix="fde-request-correlation-") as tmp:
        state_root = Path(tmp)
        ports = {project.name: reserve_port(project.port_hint, used_ports) for project in PROJECTS}
        try:
            for project in PROJECTS:
                processes.append(start_service(project, ports[project.name], state_root))
            for project in PROJECTS:
                port = ports[project.name]
                if not wait_for_health(project, port):
                    failures.append(f"{project.name}: service did not become healthy")
                    continue
                check_project(project, port, failures)
        finally:
            stop_processes(processes)


def main() -> int:
    failures: list[str] = []
    check_static_wiring(failures)
    check_docs(failures)
    check_runtime(failures)

    if failures:
        print("Request correlation check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Request correlation check passed: core API request ids match response payloads, traces, and linked audit events.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
