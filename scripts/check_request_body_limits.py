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


ROOT = Path(__file__).resolve().parents[1]
LIMIT_BYTES = 64


@dataclass(frozen=True)
class Project:
    name: str
    path: Path
    port_hint: int
    health_app: str
    post_path: str


PROJECTS = [
    Project(
        name="Secure Enterprise Knowledge Copilot",
        path=ROOT / "secure-enterprise-knowledge-copilot",
        port_hint=9131,
        health_app="secure-enterprise-knowledge-copilot",
        post_path="/api/query",
    ),
    Project(
        name="Regulated Customer Operations Agent",
        path=ROOT / "regulated-customer-operations-agent",
        port_hint=9132,
        health_app="regulated-customer-operations-agent",
        post_path="/api/agent",
    ),
    Project(
        name="AI Reliability Incident Console",
        path=ROOT / "ai-reliability-incident-console",
        port_hint=9133,
        health_app="ai-reliability-incident-console",
        post_path="/api/triage",
    ),
]


def reserve_port(preferred: int) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(("127.0.0.1", preferred))
            return preferred
        except OSError:
            sock.bind(("127.0.0.1", 0))
            return int(sock.getsockname()[1])


def service_state_path(state_root: Path, project: Project) -> Path:
    return state_root / f"{project.path.name}-runtime_state.json"


def start_service(project: Project, port: int, state_root: Path) -> subprocess.Popen:
    env = os.environ.copy()
    env["FDE_MAX_JSON_BODY_BYTES"] = str(LIMIT_BYTES)
    env["COPILOT_REPOSITORY"] = "json"
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


def request_json(method: str, port: int, path: str, body: bytes | None = None) -> tuple[int, dict]:
    headers = {"User-Agent": "fde-request-body-limits"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def wait_for_health(project: Project, port: int, seconds: int = 15) -> bool:
    for _ in range(seconds):
        try:
            status, payload = request_json("GET", port, "/api/health")
            if status == 200 and payload == {"status": "ok", "app": project.health_app}:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


def read(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")


def require_text(text: str, phrase: str, label: str, failures: list[str]) -> None:
    if phrase not in text:
        failures.append(f"{label}: missing {phrase!r}")


def check_static_wiring(failures: list[str]) -> None:
    helper = ROOT / "local_http_limits.py"
    if not helper.exists():
        failures.append("missing local_http_limits.py")
        return
    helper_text = helper.read_text(encoding="utf-8")
    for phrase in [
        'MAX_JSON_BODY_BYTES_ENV = "FDE_MAX_JSON_BODY_BYTES"',
        "DEFAULT_MAX_JSON_BODY_BYTES = 1_048_576",
        "class RequestBodyTooLarge",
        "class InvalidContentLength",
        "class InvalidJsonBody",
        "def read_json_body(",
        "if length > max_json_body_bytes():",
    ]:
        require_text(helper_text, phrase, "local_http_limits.py", failures)

    for rel_path in [
        "secure-enterprise-knowledge-copilot/app.py",
        "regulated-customer-operations-agent/app.py",
        "ai-reliability-incident-console/app.py",
    ]:
        text = read(rel_path)
        for phrase in [
            "from local_http_limits import",
            "body = read_json_body(self.headers, self.rfile)",
            "except RequestBodyTooLarge as exc:",
            'self.send_json({"error": exc.message}, 413)',
            "except (InvalidContentLength, InvalidJsonBody) as exc:",
            'self.send_json({"error": exc.message}, 400)',
        ]:
            require_text(text, phrase, rel_path, failures)
        if "str(exc)" in text:
            failures.append(f"{rel_path}: request-body errors must not render raw exception strings")


def check_docs(failures: list[str]) -> None:
    expectations = {
        "docs/api_contracts.md": [
            "FDE_MAX_JSON_BODY_BYTES",
            "Request body too large.",
            "413",
            "JSON body must be an object.",
            "python -B scripts/dev.py request-body-limits",
        ],
        "docs/portfolio_evidence_matrix.md": [
            "All services bound JSON request bodies.",
            "local_http_limits.py",
            "python -B scripts/dev.py request-body-limits",
        ],
        "PROJECT_CONTENT_INDEX.md": [
            "local_http_limits.py",
            "scripts/check_request_body_limits.py",
            "python -B scripts/dev.py request-body-limits",
        ],
    }
    for rel_path, phrases in expectations.items():
        text = read(rel_path)
        for phrase in phrases:
            require_text(text, phrase, rel_path, failures)


def check_runtime(failures: list[str]) -> None:
    processes: list[subprocess.Popen] = []
    with tempfile.TemporaryDirectory(prefix="fde-request-body-limits-") as tmp:
        state_root = Path(tmp)
        ports = {project.name: reserve_port(project.port_hint) for project in PROJECTS}
        try:
            for project in PROJECTS:
                process = start_service(project, ports[project.name], state_root)
                processes.append(process)
            for project in PROJECTS:
                port = ports[project.name]
                if not wait_for_health(project, port):
                    failures.append(f"{project.name}: service did not become healthy")
                    continue
                oversized = json.dumps({"payload": "x" * 128}).encode("utf-8")
                status, payload = request_json("POST", port, project.post_path, oversized)
                if status != 413 or payload != {"error": "Request body too large."}:
                    failures.append(f"{project.name}: expected 413 oversize response, got {status} {payload!r}")
                status, payload = request_json("POST", port, project.post_path, b"[]")
                if status != 400 or payload != {"error": "JSON body must be an object."}:
                    failures.append(f"{project.name}: expected 400 object-boundary response, got {status} {payload!r}")
        finally:
            for process in processes:
                process.terminate()
            for process in processes:
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()


def main() -> int:
    failures: list[str] = []
    check_static_wiring(failures)
    check_docs(failures)
    check_runtime(failures)

    if failures:
        print("Request body limit check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Request body limit check passed: all services reject oversized JSON before route handling.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
