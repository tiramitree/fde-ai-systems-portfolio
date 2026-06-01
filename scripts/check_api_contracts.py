from __future__ import annotations

import argparse
import json
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROJECT_1_PORT = 8866
DEFAULT_PROJECT_2_PORT = 8871


@dataclass
class Check:
    name: str
    passed: bool
    detail: str


def request_json(method: str, url: str, payload: dict | None = None) -> tuple[int, dict]:
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


def reserve_port(preferred: int) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(("127.0.0.1", preferred))
            return preferred
        except OSError:
            sock.bind(("127.0.0.1", 0))
            return int(sock.getsockname()[1])


def services(project_1_port: int, project_2_port: int) -> list[dict]:
    return [
        {
            "name": "secure-enterprise-knowledge-copilot",
            "path": ROOT / "secure-enterprise-knowledge-copilot",
            "port": project_1_port,
            "health": f"http://127.0.0.1:{project_1_port}/api/health",
        },
        {
            "name": "regulated-customer-operations-agent",
            "path": ROOT / "regulated-customer-operations-agent",
            "port": project_2_port,
            "health": f"http://127.0.0.1:{project_2_port}/api/health",
        },
    ]


def healthy(url: str) -> bool:
    try:
        status, payload = get_json(url)
        return status == 200 and payload.get("status") == "ok"
    except Exception:
        return False


def wait_for_health(url: str, seconds: int = 15) -> bool:
    for _ in range(seconds):
        if healthy(url):
            return True
        time.sleep(1)
    return False


def start_service(service: dict) -> subprocess.Popen:
    print(f"Starting {service['name']} on port {service['port']}")
    return subprocess.Popen(
        [
            sys.executable,
            "-B",
            "app.py",
            "--reset",
            "--port",
            str(service["port"]),
        ],
        cwd=service["path"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )


def get_json(url: str) -> tuple[int, dict]:
    return request_json("GET", url)


def post_json(url: str, payload: dict) -> tuple[int, dict]:
    return request_json("POST", url, payload)


def has_keys(payload: dict, keys: set[str]) -> bool:
    return keys.issubset(payload.keys())


def type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "str"
    if isinstance(value, list):
        return "list"
    if isinstance(value, dict):
        return "dict"
    return type(value).__name__


def check(condition: bool, name: str, detail: str) -> Check:
    return Check(name=name, passed=condition, detail=detail)


def expect_types(payload: dict, expected: dict[str, type | tuple[type, ...]]) -> tuple[bool, str]:
    failures = []
    for key, expected_type in expected.items():
        if key not in payload:
            failures.append(f"missing {key}")
            continue
        if not isinstance(payload[key], expected_type):
            failures.append(f"{key}={type_name(payload[key])}")
    return not failures, ", ".join(failures) or "ok"


def project_1_contracts(base_url: str) -> list[Check]:
    checks: list[Check] = []

    status, health = get_json(f"{base_url}/api/health")
    checks.append(check(status == 200 and health == {"status": "ok", "app": "secure-enterprise-knowledge-copilot"}, "P1 health contract", json.dumps(health)))

    status, users = get_json(f"{base_url}/api/users")
    checks.append(check(status == 200 and isinstance(users.get("users"), list) and users["users"], "P1 users list contract", f"users={len(users.get('users', []))}"))
    if users.get("users"):
        ok, detail = expect_types(users["users"][0], {"id": str, "name": str, "role": str, "tenant_id": str})
        checks.append(check(ok, "P1 user shape contract", detail))

    status, documents = get_json(f"{base_url}/api/documents?user_id=alice")
    checks.append(check(status == 200 and isinstance(documents.get("documents"), list), "P1 visible documents contract", f"documents={len(documents.get('documents', []))}"))
    if documents.get("documents"):
        ok, detail = expect_types(
            documents["documents"][0],
            {"id": str, "tenant_id": str, "title": str, "classification": str, "allowed_roles": list},
        )
        checks.append(check(ok and "body" not in documents["documents"][0], "P1 document shape hides body", detail))

    status, query = post_json(
        f"{base_url}/api/query",
        {
            "user_id": "alice",
            "question": "How many days per week can employees work remotely?",
        },
    )
    query_keys = {
        "trace_id",
        "user",
        "question",
        "answer",
        "citations",
        "confidence",
        "missing_evidence",
        "abstain_reason",
        "security_events",
        "model_provider",
        "openai_gateway_enabled",
        "retrieved",
        "permission_blocked_count",
        "latency_ms",
    }
    ok, detail = expect_types(
        query,
        {
            "trace_id": str,
            "answer": str,
            "citations": list,
            "confidence": (int, float),
            "missing_evidence": list,
            "security_events": list,
            "retrieved": list,
            "permission_blocked_count": int,
            "latency_ms": (int, float),
        },
    )
    checks.append(check(status == 200 and has_keys(query, query_keys) and ok, "P1 query response contract", detail))

    status, blocked = post_json(
        f"{base_url}/api/query",
        {
            "user_id": "alice",
            "question": "What is the finance retention plan?",
        },
    )
    checks.append(
        check(
            status == 200
            and isinstance(blocked.get("abstain_reason"), str)
            and blocked.get("permission_blocked_count", 0) >= 1
            and isinstance(blocked.get("citations"), list)
            and not blocked["citations"],
            "P1 unauthorized query abstention contract",
            f"reason={blocked.get('abstain_reason')}; blocked={blocked.get('permission_blocked_count')}",
        )
    )

    status, error = get_json(f"{base_url}/api/documents?user_id=missing-user")
    checks.append(check(status == 404 and isinstance(error.get("error"), str), "P1 API error contract", json.dumps(error)))

    status, traces = get_json(f"{base_url}/api/traces?limit=2")
    checks.append(check(status == 200 and isinstance(traces.get("traces"), list) and len(traces["traces"]) <= 2, "P1 traces list contract", f"traces={len(traces.get('traces', []))}"))
    if traces.get("traces"):
        ok, detail = expect_types(traces["traces"][0], {"id": str, "created_at": str, "user_id": str, "question": str, "payload": dict})
        checks.append(check(ok, "P1 trace shape contract", detail))

    return checks


def project_2_contracts(base_url: str) -> list[Check]:
    checks: list[Check] = []

    status, health = get_json(f"{base_url}/api/health")
    checks.append(check(status == 200 and health == {"status": "ok", "app": "regulated-customer-operations-agent"}, "P2 health contract", json.dumps(health)))

    status, users = get_json(f"{base_url}/api/users")
    checks.append(check(status == 200 and isinstance(users.get("users"), list) and users["users"], "P2 users list contract", f"users={len(users.get('users', []))}"))
    if users.get("users"):
        ok, detail = expect_types(users["users"][0], {"id": str, "name": str, "role": str})
        checks.append(check(ok, "P2 user shape contract", detail))

    status, cases = get_json(f"{base_url}/api/cases")
    checks.append(check(status == 200 and isinstance(cases.get("cases"), list) and cases["cases"], "P2 cases list contract", f"cases={len(cases.get('cases', []))}"))
    if cases.get("cases"):
        ok, detail = expect_types(cases["cases"][0], {"id": str, "seller_id": str, "product_id": str, "status": str})
        checks.append(check(ok, "P2 case shape contract", detail))

    status, investigation = post_json(
        f"{base_url}/api/agent",
        {
            "user_id": "ivy",
            "case_id": "case-1001",
            "message": "Check whether Market Blue still has an active listing for the recalled RX-900 product.",
        },
    )
    agent_keys = {
        "trace_id",
        "intent",
        "response",
        "tool_calls",
        "approvals",
        "blocked_actions",
        "cited_policies",
        "outputs",
        "case",
        "model_router",
    }
    ok, detail = expect_types(
        investigation,
        {
            "trace_id": str,
            "intent": str,
            "response": str,
            "tool_calls": list,
            "approvals": list,
            "blocked_actions": list,
            "cited_policies": list,
        },
    )
    checks.append(check(status == 200 and has_keys(investigation, agent_keys) and ok, "P2 agent response contract", detail))
    approval_id = investigation["approvals"][0]["id"] if investigation.get("approvals") else ""
    checks.append(check(bool(approval_id) and investigation.get("blocked_actions"), "P2 approval plus blocked-side-effect contract", f"approval={approval_id}"))

    status, forbidden = post_json(
        f"{base_url}/api/approval/approve",
        {
            "approval_id": approval_id,
            "approver_id": "ivy",
        },
    )
    checks.append(check(status == 403 and isinstance(forbidden.get("error"), str), "P2 non-supervisor approval error contract", json.dumps(forbidden)))

    status, approval = post_json(
        f"{base_url}/api/approval/approve",
        {
            "approval_id": approval_id,
            "approver_id": "sam",
        },
    )
    checks.append(
        check(
            status == 200
            and approval.get("result") in {"notice_sent", "already_processed"}
            and isinstance(approval.get("approval"), dict),
            "P2 supervisor approval contract",
            f"approval={approval_id}; result={approval.get('result')}",
        )
    )

    status, approvals = get_json(f"{base_url}/api/approvals")
    checks.append(check(status == 200 and isinstance(approvals.get("approvals"), list), "P2 approvals list contract", f"approvals={len(approvals.get('approvals', []))}"))

    status, traces = get_json(f"{base_url}/api/traces?limit=2")
    checks.append(check(status == 200 and isinstance(traces.get("traces"), list) and len(traces["traces"]) <= 2, "P2 traces list contract", f"traces={len(traces.get('traces', []))}"))
    if traces.get("traces"):
        ok, detail = expect_types(traces["traces"][0], {"id": str, "created_at": str, "user_id": str, "message": str, "intent": str, "result": dict})
        checks.append(check(ok, "P2 trace shape contract", detail))

    return checks


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Start isolated demo services and verify stable API response contracts.",
    )
    parser.add_argument("--project1-port", type=int, default=DEFAULT_PROJECT_1_PORT)
    parser.add_argument("--project2-port", type=int, default=DEFAULT_PROJECT_2_PORT)
    args = parser.parse_args()

    project_1_port = reserve_port(args.project1_port)
    project_2_port = reserve_port(args.project2_port)
    project_1_url = f"http://127.0.0.1:{project_1_port}"
    project_2_url = f"http://127.0.0.1:{project_2_port}"
    service_list = services(project_1_port, project_2_port)

    checks: list[Check] = []
    started: list[subprocess.Popen] = []
    try:
        for service in service_list:
            started.append(start_service(service))
        for service in service_list:
            if not wait_for_health(service["health"]):
                print(f"Service did not become healthy: {service['name']}", file=sys.stderr)
                return 1

        checks.extend(project_1_contracts(project_1_url))
        checks.extend(project_2_contracts(project_2_url))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError) as exc:
        print(f"API contract check failed with exception: {exc}", file=sys.stderr)
        return 1
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
    print(f"\nAPI contract checks: {passed}/{total} passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
