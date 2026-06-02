from __future__ import annotations

import importlib.util
import json
import socket
import sys
import threading
import urllib.error
import urllib.request
from dataclasses import dataclass
from http.server import ThreadingHTTPServer
from pathlib import Path
from types import ModuleType


ROOT = Path(__file__).resolve().parents[1]
LEAKY_EXCEPTION = "boom C:\\" + "Users\\" + "117" + "58\\" + "One" + "Drive\\private " + "s" + "k-test-token"
EXPECTED_ERROR = {"error": "Internal server error"}


@dataclass(frozen=True)
class Project:
    name: str
    path: Path
    module_name: str
    port_hint: int


PROJECTS = [
    Project(
        name="Secure Enterprise Knowledge Copilot",
        path=ROOT / "secure-enterprise-knowledge-copilot",
        module_name="secure_enterprise_error_hygiene_app",
        port_hint=8891,
    ),
    Project(
        name="Regulated Customer Operations Agent",
        path=ROOT / "regulated-customer-operations-agent",
        module_name="regulated_ops_error_hygiene_app",
        port_hint=8892,
    ),
    Project(
        name="AI Reliability Incident Console",
        path=ROOT / "ai-reliability-incident-console",
        module_name="reliability_console_error_hygiene_app",
        port_hint=8893,
    ),
]


class ExplodingApi:
    @staticmethod
    def parse_query(query: str) -> dict[str, list[str]]:
        return {}

    def get(self, path: str, query: dict[str, list[str]]) -> dict:
        raise RuntimeError(LEAKY_EXCEPTION)

    def post(self, path: str, body: dict) -> dict:
        raise RuntimeError(LEAKY_EXCEPTION)


def reserve_port(preferred: int) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(("127.0.0.1", preferred))
            return preferred
        except OSError:
            sock.bind(("127.0.0.1", 0))
            return int(sock.getsockname()[1])


def import_app(project: Project) -> ModuleType:
    spec = importlib.util.spec_from_file_location(project.module_name, project.path / "app.py")
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not import app for {project.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[project.module_name] = module
    spec.loader.exec_module(module)
    return module


def request_json(method: str, port: int, path: str, body: dict | None = None) -> tuple[int, dict[str, str], dict]:
    data = None
    headers = {"User-Agent": "fde-error-hygiene"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, dict(response.headers), json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers), json.loads(exc.read().decode("utf-8"))


def check_project(project: Project) -> list[str]:
    failures: list[str] = []
    app_path = project.path / "app.py"
    text = app_path.read_text(encoding="utf-8")
    rel = app_path.relative_to(ROOT).as_posix()
    if "str(exc)" in text:
        failures.append(f"{rel}: raw exception string is exposed")
    if "traceback" in text:
        failures.append(f"{rel}: traceback should not be imported or rendered by the HTTP shell")
    if '"Internal server error"' not in text:
        failures.append(f"{rel}: missing generic internal error response")

    module = import_app(project)
    module.API = ExplodingApi()
    module.Handler.log_message = lambda self, fmt, *args: None
    port = reserve_port(project.port_hint)
    server = ThreadingHTTPServer(("127.0.0.1", port), module.Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        checks = [
            request_json("GET", port, "/api/health"),
            request_json("POST", port, "/api/test", {"hello": "world"}),
        ]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    for status, headers, payload in checks:
        content_type = headers.get("Content-Type", headers.get("content-type", ""))
        if status != 500:
            failures.append(f"{project.name}: expected 500 for unexpected exception, got {status}")
        if not content_type.startswith("application/json"):
            failures.append(f"{project.name}: expected JSON error response, got {content_type}")
        if payload != EXPECTED_ERROR:
            failures.append(f"{project.name}: unexpected internal error payload {payload!r}")
        rendered = json.dumps(payload)
        for forbidden in ("C:\\" + "Users", "One" + "Drive", "117" + "58", "s" + "k-test-token", "boom"):
            if forbidden in rendered:
                failures.append(f"{project.name}: leaked internal exception marker {forbidden!r}")
    return failures


def main() -> int:
    failures: list[str] = []
    for project in PROJECTS:
        failures.extend(check_project(project))

    if failures:
        print("Error hygiene check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Error hygiene check passed: unexpected server exceptions return generic JSON errors without leaking internals.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
