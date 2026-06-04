from __future__ import annotations

import http.client
import json
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROJECT_1_PORT = 8876
DEFAULT_PROJECT_2_PORT = 8877
DEFAULT_PROJECT_3_PORT = 8878


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class Project:
    name: str
    path: Path
    port: int
    health_app: str
    title: str
    primary_label: str
    primary_button: str


def reserve_port(preferred: int) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        if preferred == 0:
            sock.bind(("127.0.0.1", 0))
            return int(sock.getsockname()[1])
        try:
            sock.bind(("127.0.0.1", preferred))
            return preferred
        except OSError:
            sock.bind(("127.0.0.1", 0))
            return int(sock.getsockname()[1])


def projects(project_1_port: int, project_2_port: int, project_3_port: int) -> list[Project]:
    return [
        Project(
            name="P1",
            path=ROOT / "secure-enterprise-knowledge-copilot",
            port=project_1_port,
            health_app="secure-enterprise-knowledge-copilot",
            title="Secure Enterprise Knowledge Copilot",
            primary_label='<label for="question">Question</label>',
            primary_button='id="ask"',
        ),
        Project(
            name="P2",
            path=ROOT / "regulated-customer-operations-agent",
            port=project_2_port,
            health_app="regulated-customer-operations-agent",
            title="Regulated Customer Operations Agent",
            primary_label='<label for="message">Message</label>',
            primary_button='id="runAgent"',
        ),
        Project(
            name="P3",
            path=ROOT / "ai-reliability-incident-console",
            port=project_3_port,
            health_app="ai-reliability-incident-console",
            title="AI Reliability Incident Console",
            primary_label='<label for="incidentSelect">Incident</label>',
            primary_button='id="runTriage"',
        ),
    ]


def start_service(project: Project) -> subprocess.Popen:
    print(f"Starting {project.path.name} on port {project.port}")
    return subprocess.Popen(
        [
            sys.executable,
            "-B",
            "app.py",
            "--reset",
            "--port",
            str(project.port),
        ],
        cwd=project.path,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )


def request(path: str, port: int) -> tuple[int, dict[str, str], bytes]:
    url = f"http://127.0.0.1:{port}{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "fde-runtime-ui-contracts"})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status, dict(response.headers), response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers), exc.read()


def raw_request(path: str, port: int) -> tuple[int, dict[str, str], bytes]:
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    try:
        conn.request("GET", path, headers={"User-Agent": "fde-runtime-ui-contracts"})
        response = conn.getresponse()
        return response.status, dict(response.headers), response.read()
    finally:
        conn.close()


def wait_for_health(project: Project, seconds: int = 15) -> bool:
    for _ in range(seconds):
        try:
            status, _, body = request("/api/health", project.port)
            payload = json.loads(body.decode("utf-8"))
            if status == 200 and payload == {"status": "ok", "app": project.health_app}:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


def content_type(headers: dict[str, str]) -> str:
    return headers.get("Content-Type", headers.get("content-type", ""))


def security_headers_ok(headers: dict[str, str]) -> tuple[bool, str]:
    lower = {key.lower(): value for key, value in headers.items()}
    csp = lower.get("content-security-policy", "")
    checks = {
        "x-content-type-options": lower.get("x-content-type-options") == "nosniff",
        "referrer-policy": lower.get("referrer-policy") == "no-referrer",
        "csp-default-src": "default-src 'self'" in csp,
        "csp-frame-ancestors": "frame-ancestors 'none'" in csp,
    }
    failures = [name for name, ok in checks.items() if not ok]
    return not failures, ", ".join(failures) or "ok"


def check(condition: bool, name: str, detail: str) -> Check:
    return Check(name=name, passed=condition, detail=detail)


def check_text_asset(
    project: Project,
    path: str,
    expected_type: str,
    required_fragments: list[str],
) -> list[Check]:
    status, headers, body = request(path, project.port)
    text = body.decode("utf-8", errors="replace")
    checks = [
        check(status == 200, f"{project.name} {path} status", str(status)),
        check(content_type(headers).startswith(expected_type), f"{project.name} {path} content type", content_type(headers)),
        check(bool(headers.get("Content-Length")), f"{project.name} {path} content length", headers.get("Content-Length", "missing")),
    ]
    ok_headers, header_detail = security_headers_ok(headers)
    checks.append(check(ok_headers, f"{project.name} {path} security headers", header_detail))
    for fragment in required_fragments:
        checks.append(check(fragment in text, f"{project.name} {path} contains {fragment[:32]!r}", "found" if fragment in text else "missing"))
    return checks


def project_checks(project: Project) -> list[Check]:
    checks: list[Check] = []
    checks.extend(
        check_text_asset(
            project,
            "/",
            "text/html",
            [
                f"<title>{project.title}</title>",
                '<link rel="stylesheet" href="/styles.css"',
                '<script type="module" src="/js/app.js">',
                project.primary_label,
                project.primary_button,
                'id="copyTraceId"',
                'id="copyTraceLink"',
                'id="scenarioDraft"',
                'id="scenarioDiff"',
                'id="saveScenarioDraft"',
                'id="copyScenarioDraft"',
            ],
        )
    )
    checks.extend(
        check_text_asset(
            project,
            "/styles.css",
            "text/css",
            [".grid", ".panel", ".quick", ".traceLink:focus-visible", ".scenarioDiff"],
        )
    )
    checks.extend(
        check_text_asset(
            project,
            "/js/app.js",
            "text/javascript",
            ['import { api } from "./api.js"', 'from "./traceLinks.js"', 'from "./scenarioEditor.js"', "boot"],
        )
    )
    checks.extend(
        check_text_asset(
            project,
            "/js/scenarioEditor.js",
            "text/javascript",
            [
                "installScenarioEditor",
                "localStorage",
                "copyText",
                "copyButton",
                "diffRows",
                "scenarioDiffRow",
                "JSON.parse",
                "JSON.stringify",
            ],
        )
    )
    checks.extend(
        check_text_asset(
            project,
            "/js/traceLinks.js",
            "text/javascript",
            [
                "traceHash",
                "traceUrl",
                "selectedTraceId",
                "syncTraceSelection",
                "installTraceKeyboardNavigation",
                "ArrowDown",
                "focus(",
                "[data-trace-id]",
            ],
        )
    )
    checks.extend(
        check_text_asset(
            project,
            "/js/clipboard.js",
            "text/javascript",
            ["copyText", "installCopyButton", "installTraceCopyButton", "navigator.clipboard"],
        )
    )
    checks.extend(
        check_text_asset(
            project,
            "/js/api.js",
            "text/javascript",
            ["export async function api", "fetch(path"],
        )
    )

    status, headers, body = request("/missing-static.js", project.port)
    error_text = body.decode("utf-8", errors="replace")
    checks.append(check(status == 404, f"{project.name} missing static returns 404", str(status)))
    checks.append(check(content_type(headers).startswith("application/json"), f"{project.name} missing static JSON error", content_type(headers)))
    checks.append(check("Not found" in error_text, f"{project.name} missing static error body", error_text[:80]))

    status, headers, body = raw_request("/../app.py", project.port)
    traversal_text = body.decode("utf-8", errors="replace")
    checks.append(check(status == 403, f"{project.name} path traversal is forbidden", str(status)))
    checks.append(check("Forbidden" in traversal_text, f"{project.name} path traversal error body", traversal_text[:80]))
    ok_headers, header_detail = security_headers_ok(headers)
    checks.append(check(ok_headers, f"{project.name} path traversal security headers", header_detail))
    return checks


def main() -> int:
    project_1_port = reserve_port(DEFAULT_PROJECT_1_PORT)
    project_2_port = reserve_port(DEFAULT_PROJECT_2_PORT)
    project_3_port = reserve_port(DEFAULT_PROJECT_3_PORT)
    while project_3_port in {project_1_port, project_2_port}:
        project_3_port = reserve_port(0)
    project_list = projects(project_1_port, project_2_port, project_3_port)

    started: list[subprocess.Popen] = []
    checks: list[Check] = []
    try:
        for project in project_list:
            started.append(start_service(project))
        for project in project_list:
            if not wait_for_health(project):
                print(f"Service did not become healthy: {project.path.name}", file=sys.stderr)
                return 1
        for project in project_list:
            checks.extend(project_checks(project))
    finally:
        for process in started:
            process.terminate()
        for process in started:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

    for item in checks:
        status = "PASS" if item.passed else "FAIL"
        print(f"[{status}] {item.name}: {item.detail}")

    passed = sum(1 for item in checks if item.passed)
    total = len(checks)
    print(f"\nRuntime UI contract checks: {passed}/{total} passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
