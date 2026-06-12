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
REQUEST_ID = "review-check-1234"


@dataclass(frozen=True)
class Project:
    name: str
    path: Path
    port_hint: int
    health_app: str
    post_path: str
    payload: dict[str, Any]


PROJECTS = [
    Project(
        name="Secure Enterprise Knowledge Copilot",
        path=ROOT / "secure-enterprise-knowledge-copilot",
        port_hint=9141,
        health_app="secure-enterprise-knowledge-copilot",
        post_path="/api/query",
        payload={"user_id": "alice", "question": "How many days per week can employees work remotely?"},
    ),
    Project(
        name="Regulated Customer Operations Agent",
        path=ROOT / "regulated-customer-operations-agent",
        port_hint=9142,
        health_app="regulated-customer-operations-agent",
        post_path="/api/agent",
        payload={
            "user_id": "ivy",
            "case_id": "case-1001",
            "message": "Check whether Market Blue still has an active listing for the recalled RX-900 product.",
        },
    ),
    Project(
        name="AI Reliability Incident Console",
        path=ROOT / "ai-reliability-incident-console",
        port_hint=9143,
        health_app="ai-reliability-incident-console",
        post_path="/api/triage",
        payload={"user_id": "maya", "release_id": "rel-2026-06-01", "incident_id": "inc-2026-014"},
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


def service_state_path(state_root: Path, project: Project, mode: str) -> Path:
    return state_root / f"{project.path.name}-{mode}-runtime_state.json"


def start_service(project: Project, port: int, state_root: Path, mode: str, extra_env: dict[str, str]) -> subprocess.Popen:
    env = os.environ.copy()
    env.update(extra_env)
    env["COPILOT_REPOSITORY"] = "json"
    return subprocess.Popen(
        [
            sys.executable,
            "-B",
            "app.py",
            "--reset",
            "--state-path",
            str(service_state_path(state_root, project, mode)),
            "--port",
            str(port),
        ],
        cwd=project.path,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )


def request_json(
    method: str,
    port: int,
    path: str,
    body: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> tuple[int, dict[str, Any], dict[str, str]]:
    data = json.dumps(body or {}).encode("utf-8") if method == "POST" else None
    request_headers = {"User-Agent": "fde-request-governance", **(headers or {})}
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
            payload = json.loads(response.read().decode("utf-8"))
            return response.status, payload, normalize_headers(response.headers.items())
    except urllib.error.HTTPError as exc:
        payload = json.loads(exc.read().decode("utf-8"))
        return exc.code, payload, normalize_headers(exc.headers.items())


def normalize_headers(items: Any) -> dict[str, str]:
    return {str(key).lower(): str(value) for key, value in items}


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


def stop_process(process: subprocess.Popen) -> None:
    process.terminate()
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


def check_static_wiring(failures: list[str]) -> None:
    helper = ROOT / "local_request_governance.py"
    if not helper.exists():
        failures.append("missing local_request_governance.py")
        return
    helper_text = helper.read_text(encoding="utf-8")
    for phrase in [
        'REQUEST_ID_HEADER = "X-Request-ID"',
        'RATE_LIMIT_REQUESTS_ENV = "FDE_RATE_LIMIT_REQUESTS_PER_WINDOW"',
        'RATE_LIMIT_BUDGET_ENV = "FDE_RATE_LIMIT_BUDGET_PER_WINDOW"',
        "class RateLimitExceeded",
        "class LocalRequestGovernor",
        "def request_cost(",
        '"X-RateLimit-Budget-Remaining"',
    ]:
        require_text(helper_text, phrase, "local_request_governance.py", failures)

    for rel_path in [
        "secure-enterprise-knowledge-copilot/app.py",
        "regulated-customer-operations-agent/app.py",
        "ai-reliability-incident-console/app.py",
    ]:
        text = read(rel_path)
        for phrase in [
            "from local_request_governance import LocalRequestGovernor, RateLimitExceeded",
            "GOVERNOR = LocalRequestGovernor()",
            'GOVERNOR.check("GET", parsed.path, self.headers, self.client_address)',
            'GOVERNOR.check("POST", parsed.path, self.headers, self.client_address)',
            "except RateLimitExceeded as exc:",
            '"retry_after_seconds": exc.context.retry_after_seconds',
            "context.response_headers().items()",
        ]:
            require_text(text, phrase, rel_path, failures)


def check_docs(failures: list[str]) -> None:
    expectations = {
        "docs/api_contracts.md": [
            "X-Request-ID",
            "X-RateLimit-Remaining",
            "X-RateLimit-Budget-Remaining",
            "FDE_RATE_LIMIT_REQUESTS_PER_WINDOW",
            "FDE_RATE_LIMIT_BUDGET_PER_WINDOW",
            "Rate limit exceeded.",
            "python -B scripts/dev.py request-governance",
        ],
        "docs/api_error_examples.md": [
            "Rate Limit Exceeded",
            "X-Request-ID",
            "Retry-After",
            '"error": "Rate limit exceeded."',
        ],
        "docs/portfolio_evidence_matrix.md": [
            "All services expose API request governance headers and local 429 limits.",
            "local_request_governance.py",
            "python -B scripts/dev.py request-governance",
        ],
        "PROJECT_CONTENT_INDEX.md": [
            "local_request_governance.py",
            "scripts/check_request_governance.py",
            "python -B scripts/dev.py request-governance",
        ],
    }
    for rel_path, phrases in expectations.items():
        text = read(rel_path)
        for phrase in phrases:
            require_text(text, phrase, rel_path, failures)


def check_request_id_headers(project: Project, port: int, failures: list[str]) -> None:
    status, payload, headers = request_json("GET", port, "/api/health", headers={"X-Request-ID": REQUEST_ID})
    if status != 200 or payload != {"status": "ok", "app": project.health_app}:
        failures.append(f"{project.name}: health request failed during request-id check: {status} {payload!r}")
    if headers.get("x-request-id") != REQUEST_ID:
        failures.append(f"{project.name}: expected echoed request id header")
    for header in [
        "x-ratelimit-limit",
        "x-ratelimit-remaining",
        "x-ratelimit-window-seconds",
        "x-ratelimit-budget-limit",
        "x-ratelimit-budget-remaining",
    ]:
        if header not in headers:
            failures.append(f"{project.name}: missing {header} on governed API response")


def check_request_count_limit(project: Project, port: int, failures: list[str]) -> None:
    statuses = []
    payloads = []
    headers_seen = []
    for attempt in range(3):
        status, payload, headers = request_json(
            "POST",
            port,
            project.post_path,
            project.payload,
            headers={"X-Request-ID": f"{REQUEST_ID}-count-{attempt}"},
        )
        statuses.append(status)
        payloads.append(payload)
        headers_seen.append(headers)
    if statuses[:2] != [200, 200] or statuses[2] != 429:
        failures.append(f"{project.name}: expected request-count 200,200,429; got {statuses}")
    limited_payload = payloads[2]
    limited_headers = headers_seen[2]
    if limited_payload.get("error") != "Rate limit exceeded.":
        failures.append(f"{project.name}: expected safe 429 error, got {limited_payload!r}")
    if limited_payload.get("request_id") != f"{REQUEST_ID}-count-2":
        failures.append(f"{project.name}: 429 payload must include matching request_id")
    if limited_headers.get("retry-after") is None or limited_headers.get("x-request-id") != f"{REQUEST_ID}-count-2":
        failures.append(f"{project.name}: 429 response missing retry-after or request-id headers")


def check_budget_limit(project: Project, port: int, failures: list[str]) -> None:
    statuses = []
    for attempt in range(2):
        status, payload, headers = request_json(
            "POST",
            port,
            project.post_path,
            project.payload,
            headers={"X-Request-ID": f"{REQUEST_ID}-budget-{attempt}"},
        )
        statuses.append(status)
        if attempt == 1:
            if payload.get("error") != "Rate limit exceeded.":
                failures.append(f"{project.name}: expected budget 429 safe error, got {payload!r}")
            if headers.get("x-ratelimit-budget-remaining") is None:
                failures.append(f"{project.name}: budget 429 missing budget remaining header")
    if statuses != [200, 429]:
        failures.append(f"{project.name}: expected budget 200,429; got {statuses}")


def check_runtime_mode(project: Project, port: int, state_root: Path, mode: str, env: dict[str, str], failures: list[str]) -> None:
    process = start_service(project, port, state_root, mode, env)
    try:
        if not wait_for_health(project, port):
            failures.append(f"{project.name}: service did not become healthy for {mode}")
            return
        check_request_id_headers(project, port, failures)
        if mode == "count":
            check_request_count_limit(project, port, failures)
        elif mode == "budget":
            check_budget_limit(project, port, failures)
    finally:
        stop_process(process)


def check_runtime(failures: list[str]) -> None:
    used_ports: set[int] = set()
    with tempfile.TemporaryDirectory(prefix="fde-request-governance-") as tmp:
        state_root = Path(tmp)
        for project in PROJECTS:
            count_port = reserve_port(project.port_hint, used_ports)
            budget_port = reserve_port(project.port_hint + 10, used_ports)
            check_runtime_mode(
                project,
                count_port,
                state_root,
                "count",
                {
                    "FDE_RATE_LIMIT_REQUESTS_PER_WINDOW": "2",
                    "FDE_RATE_LIMIT_BUDGET_PER_WINDOW": "999",
                    "FDE_RATE_LIMIT_WINDOW_SECONDS": "60",
                },
                failures,
            )
            check_runtime_mode(
                project,
                budget_port,
                state_root,
                "budget",
                {
                    "FDE_RATE_LIMIT_REQUESTS_PER_WINDOW": "10",
                    "FDE_RATE_LIMIT_BUDGET_PER_WINDOW": "12",
                    "FDE_RATE_LIMIT_WINDOW_SECONDS": "60",
                },
                failures,
            )


def main() -> int:
    failures: list[str] = []
    check_static_wiring(failures)
    check_docs(failures)
    check_runtime(failures)

    if failures:
        print("Request governance check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Request governance check passed: request ids, rate-limit headers, request-count limits, and budget limits are enforced.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
