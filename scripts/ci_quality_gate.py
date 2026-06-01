from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
SERVICES = [
    {
        "name": "secure-enterprise-knowledge-copilot",
        "path": ROOT / "secure-enterprise-knowledge-copilot",
        "port": 8765,
        "health": "http://127.0.0.1:8765/api/health",
    },
    {
        "name": "regulated-customer-operations-agent",
        "path": ROOT / "regulated-customer-operations-agent",
        "port": 8770,
        "health": "http://127.0.0.1:8770/api/health",
    },
]


def healthy(url: str) -> bool:
    try:
        with urlopen(url, timeout=2) as response:
            return response.status == 200
    except Exception:
        return False


def wait_for_health(url: str, seconds: int = 15) -> bool:
    for _ in range(seconds):
        if healthy(url):
            return True
        time.sleep(1)
    return False


def start_service(service: dict) -> subprocess.Popen | None:
    if healthy(service["health"]):
        print(f"{service['name']} already healthy on port {service['port']}")
        return None

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
    )


def main() -> int:
    started: list[subprocess.Popen] = []
    try:
        for service in SERVICES:
            process = start_service(service)
            if process is not None:
                started.append(process)

        for service in SERVICES:
            if not wait_for_health(service["health"]):
                print(f"Service did not become healthy: {service['name']}", file=sys.stderr)
                return 1

        result = subprocess.run(
            [sys.executable, "-B", "scripts/quality_gate.py"],
            cwd=ROOT,
            text=True,
        )
        return result.returncode
    finally:
        for process in started:
            process.terminate()
        for process in started:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()


if __name__ == "__main__":
    raise SystemExit(main())

