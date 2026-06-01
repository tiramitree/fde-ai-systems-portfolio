from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
SERVICES = [
    {
        "name": "Secure Enterprise Knowledge Copilot",
        "path": ROOT / "secure-enterprise-knowledge-copilot",
        "port": 8765,
        "health": "http://127.0.0.1:8765/api/health",
    },
    {
        "name": "Regulated Customer Operations Agent",
        "path": ROOT / "regulated-customer-operations-agent",
        "port": 8770,
        "health": "http://127.0.0.1:8770/api/health",
    },
]


def wait_for_health(url: str, seconds: int = 10) -> bool:
    last_error = None
    for _ in range(seconds):
        try:
            with urlopen(url, timeout=2) as response:
                return response.status == 200
        except Exception as exc:
            last_error = exc
            time.sleep(1)
    print(f"Health check failed for {url}: {last_error}")
    return False


def main() -> int:
    processes: list[subprocess.Popen] = []
    for service in SERVICES:
        log_path = service["path"] / "server.log"
        err_path = service["path"] / "server.err.log"
        out = open(log_path, "ab")
        err = open(err_path, "ab")
        process = subprocess.Popen(
            [
                sys.executable,
                "-B",
                "app.py",
                "--reset",
                "--port",
                str(service["port"]),
            ],
            cwd=service["path"],
            stdout=out,
            stderr=err,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        processes.append(process)
        print(f"Started {service['name']} on port {service['port']} with PID {process.pid}")

    all_healthy = True
    for service in SERVICES:
        ok = wait_for_health(service["health"])
        all_healthy = all_healthy and ok
        print(f"{service['name']}: {'ok' if ok else 'failed'}")

    print("\nDemo URLs:")
    print("Project 1: http://127.0.0.1:8765")
    print("Project 2: http://127.0.0.1:8770")
    print("\nPress Ctrl+C to stop both demo servers.")

    if not all_healthy:
        for process in processes:
            process.terminate()
        return 1

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping demo servers...")
        for process in processes:
            process.terminate()
        return 0


if __name__ == "__main__":
    raise SystemExit(main())

