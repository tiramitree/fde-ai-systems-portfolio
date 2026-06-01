from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVICES = [
    {
        "name": "secure-enterprise-knowledge-copilot",
        "path": ROOT / "secure-enterprise-knowledge-copilot",
        "preferred_port": 8895,
        "health": "/api/health",
    },
    {
        "name": "regulated-customer-operations-agent",
        "path": ROOT / "regulated-customer-operations-agent",
        "preferred_port": 8896,
        "health": "/api/health",
    },
]


def require_key() -> None:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key or key == "...":
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Set a real key, then rerun "
            "`python -B scripts/dev.py openai-live`."
        )


def reserve_port(preferred: int) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(("127.0.0.1", preferred))
            return preferred
        except OSError:
            sock.bind(("127.0.0.1", 0))
            return int(sock.getsockname()[1])


def wait_for_health(base_url: str, seconds: int = 30) -> bool:
    url = f"{base_url}/api/health"
    for _ in range(seconds):
        try:
            with urllib.request.urlopen(url, timeout=3) as response:
                if response.status == 200:
                    return True
        except Exception:
            time.sleep(1)
    return False


def start_service(service: dict, port: int, env: dict[str, str]) -> subprocess.Popen:
    return subprocess.Popen(
        [sys.executable, "-B", "app.py", "--reset", "--port", str(port)],
        cwd=service["path"],
        env=env,
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


def post_json(url: str, payload: dict) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.loads(response.read().decode("utf-8"))


def service_env() -> dict[str, str]:
    env = os.environ.copy()
    env["COPILOT_MODEL_PROVIDER"] = "openai"
    env["OPS_AGENT_MODEL_ROUTER"] = "openai"
    env.setdefault("OPENAI_MODEL", "gpt-5.2")
    env.setdefault("OPENAI_REASONING_EFFORT", "low")
    env.setdefault("OPENAI_TEXT_VERBOSITY", "low")
    return env


def verify_project_1(base_url: str) -> None:
    result = post_json(
        f"{base_url}/api/query",
        {
            "user_id": "alice",
            "question": "How many days per week can employees work remotely?",
        },
    )
    if result.get("openai_gateway_enabled") is not True:
        raise RuntimeError("Project 1 did not report OpenAI gateway enabled")
    if result.get("model_provider") != "openai":
        raise RuntimeError(
            "Project 1 did not return model_provider=openai; the gateway may have fallen back locally"
        )
    if result.get("abstain_reason") is not None or not result.get("citations"):
        raise RuntimeError("Project 1 OpenAI live response did not preserve grounded answer behavior")
    print(f"Project 1 OpenAI live check passed: trace={result['trace_id']}")


def verify_project_2(base_url: str) -> None:
    result = post_json(
        f"{base_url}/api/agent",
        {
            "user_id": "ivy",
            "case_id": "case-1001",
            "message": "Check whether Market Blue still has an active listing for the recalled RX-900 product.",
        },
    )
    if result.get("model_router") != "openai":
        raise RuntimeError(
            "Project 2 did not return model_router=openai; the router may have fallen back locally"
        )
    if result.get("intent") != "investigate_listing" or not result.get("approvals"):
        raise RuntimeError("Project 2 OpenAI live router did not preserve governed workflow behavior")
    if not result.get("blocked_actions"):
        raise RuntimeError("Project 2 OpenAI live response did not preserve side-effect blocking")
    print(f"Project 2 OpenAI live check passed: trace={result['trace_id']}")


def main() -> int:
    processes: list[subprocess.Popen] = []
    try:
        require_key()
        env = service_env()
        ports = [reserve_port(service["preferred_port"]) for service in SERVICES]
        urls = [f"http://127.0.0.1:{port}" for port in ports]
        for service, port in zip(SERVICES, ports):
            print(f"Starting {service['name']} in OpenAI mode on port {port}")
            processes.append(start_service(service, port, env))
        for service, url in zip(SERVICES, urls):
            if not wait_for_health(url):
                raise RuntimeError(f"{service['name']} did not become healthy at {url}")

        verify_project_1(urls[0])
        verify_project_2(urls[1])
        print("OpenAI live mode check passed: both apps used OpenAI mode and kept safety behavior intact.")
        return 0
    except Exception as exc:
        print(f"OpenAI live mode check failed: {exc}", file=sys.stderr)
        return 1
    finally:
        stop_processes(processes)


if __name__ == "__main__":
    raise SystemExit(main())
