from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT_NAME = "fde-ai-systems-runtime-check"
SERVICES = [
    {
        "name": "secure-enterprise-knowledge-copilot",
        "port": 8765,
        "health": "http://127.0.0.1:8765/api/health",
    },
    {
        "name": "regulated-customer-operations-agent",
        "port": 8770,
        "health": "http://127.0.0.1:8770/api/health",
    },
]


def run(args: list[str], *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, env=env, text=True, capture_output=True)


def print_output(result: subprocess.CompletedProcess[str]) -> None:
    output = (result.stdout + result.stderr).strip()
    if output:
        print(output)


def docker_bin() -> str:
    found = shutil.which("docker")
    if not found:
        raise RuntimeError(
            "Docker CLI is not installed or not on PATH. Install Docker Desktop or Docker Engine, "
            "then rerun `python -B scripts/dev.py docker-runtime`."
        )
    return found


def check_docker_available(docker: str) -> None:
    checks = [
        [docker, "--version"],
        [docker, "compose", "version"],
        [docker, "info"],
    ]
    for command in checks:
        result = run(command)
        if result.returncode != 0:
            print_output(result)
            raise RuntimeError(f"`{' '.join(command)}` failed")
        print_output(result)


def port_is_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        try:
            sock.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def wait_for_health(url: str, seconds: int = 90) -> bool:
    for _ in range(seconds):
        try:
            with urllib.request.urlopen(url, timeout=3) as response:
                if response.status == 200:
                    return True
        except Exception:
            time.sleep(1)
    return False


def compose(docker: str, *args: str) -> subprocess.CompletedProcess[str]:
    return run([docker, "compose", "--project-name", PROJECT_NAME, *args])


def compose_or_raise(docker: str, *args: str) -> None:
    result = compose(docker, *args)
    print_output(result)
    if result.returncode != 0:
        raise RuntimeError(f"`docker compose {' '.join(args)}` failed")


def smoke_env() -> dict[str, str]:
    env = os.environ.copy()
    env["FDE_PROJECT_1_URL"] = "http://127.0.0.1:8765"
    env["FDE_PROJECT_2_URL"] = "http://127.0.0.1:8770"
    return env


def main() -> int:
    docker = ""
    compose_started = False
    try:
        docker = docker_bin()
        check_docker_available(docker)

        static_check = run([sys.executable, "-B", "scripts/check_container_release.py"])
        print_output(static_check)
        if static_check.returncode != 0:
            raise RuntimeError("static container release hygiene failed")

        compose_or_raise(docker, "down", "--remove-orphans")

        blocked_ports = [service["port"] for service in SERVICES if not port_is_free(service["port"])]
        if blocked_ports:
            ports = ", ".join(str(port) for port in blocked_ports)
            raise RuntimeError(
                f"host port(s) already in use: {ports}. Stop local demo servers before Docker runtime verification."
            )

        compose_or_raise(docker, "config")
        compose_or_raise(docker, "up", "--build", "--detach")
        compose_started = True

        for service in SERVICES:
            if not wait_for_health(service["health"]):
                ps = compose(docker, "ps")
                print_output(ps)
                logs = compose(docker, "logs", "--no-color", "--tail", "80", service["name"])
                print_output(logs)
                raise RuntimeError(f"{service['name']} did not become healthy at {service['health']}")
            print(f"{service['name']} healthy at {service['health']}")

        smoke = run([sys.executable, "-B", "scripts/smoke_test_demo_flows.py"], env=smoke_env())
        print_output(smoke)
        if smoke.returncode != 0:
            raise RuntimeError("container smoke flow failed")

        print("Docker runtime check passed: compose build/up, health endpoints, and smoke flows succeeded.")
        return 0
    except Exception as exc:
        print(f"Docker runtime check failed: {exc}", file=sys.stderr)
        return 1
    finally:
        if docker and compose_started:
            result = compose(docker, "down", "--remove-orphans")
            print_output(result)


if __name__ == "__main__":
    raise SystemExit(main())
