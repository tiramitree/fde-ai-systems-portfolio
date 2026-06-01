from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

STATIC_COMMANDS = [
    "safety",
    "assets",
    "visual-assets",
    "container-release",
    "dependency-surface",
    "governance",
    "model-gateway-safety",
    "pr-policy",
    "threat-model",
]

SERVICES = [
    {
        "name": "secure-enterprise-knowledge-copilot",
        "path": "secure-enterprise-knowledge-copilot",
    },
    {
        "name": "regulated-customer-operations-agent",
        "path": "regulated-customer-operations-agent",
    },
]


def run(args: list[str], cwd: Path, env: dict[str, str] | None = None) -> tuple[bool, str]:
    result = subprocess.run(
        args,
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
    )
    return result.returncode == 0, (result.stdout + result.stderr).strip()


def origin_url() -> str:
    ok, output = run(["git", "remote", "get-url", "origin"], ROOT)
    if not ok or not output:
        raise RuntimeError("origin remote is not configured")
    return output


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def wait_for_health(url: str, seconds: int = 20) -> tuple[bool, str]:
    last_error = ""
    for _ in range(seconds):
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                body = json.loads(response.read().decode("utf-8"))
                return response.status == 200 and body.get("status") == "ok", json.dumps(body)
        except Exception as exc:
            last_error = str(exc)
            time.sleep(1)
    return False, last_error


def start_service(clone_dir: Path, service: dict[str, str], port: int) -> subprocess.Popen:
    project_dir = clone_dir / service["path"]
    return subprocess.Popen(
        [
            sys.executable,
            "-B",
            "app.py",
            "--reset",
            "--port",
            str(port),
        ],
        cwd=project_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
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


def clone_repository(source: str, target: Path) -> None:
    ok, output = run(["git", "clone", "--depth", "1", source, str(target)], ROOT)
    if not ok:
        raise RuntimeError(output or "git clone failed")


def run_static_checks(clone_dir: Path) -> list[str]:
    failures: list[str] = []
    for command in STATIC_COMMANDS:
        print(f"\n=== fresh clone: {command} ===")
        ok, output = run([sys.executable, "-B", "scripts/dev.py", command], clone_dir)
        if output:
            print(output)
        if not ok:
            failures.append(f"fresh clone command failed: {command}")
    return failures


def run_runtime_smoke(clone_dir: Path) -> list[str]:
    failures: list[str] = []
    first_port = free_port()
    second_port = free_port()
    while second_port == first_port:
        second_port = free_port()
    ports = [first_port, second_port]
    urls = [f"http://127.0.0.1:{port}" for port in ports]
    processes: list[subprocess.Popen] = []

    try:
        for service, port in zip(SERVICES, ports):
            print(f"Starting fresh clone {service['name']} on port {port}")
            processes.append(start_service(clone_dir, service, port))

        for service, url in zip(SERVICES, urls):
            ok, detail = wait_for_health(f"{url}/api/health")
            status = "ok" if ok else "failed"
            print(f"{service['name']} health on {url}: {status} ({detail})")
            if not ok:
                failures.append(f"{service['name']} did not become healthy on {url}")

        if failures:
            return failures

        env = os.environ.copy()
        env["FDE_PROJECT_1_URL"] = urls[0]
        env["FDE_PROJECT_2_URL"] = urls[1]

        print("\n=== fresh clone: health ===")
        ok, output = run([sys.executable, "-B", "scripts/dev.py", "health"], clone_dir, env=env)
        if output:
            print(output)
        if not ok:
            failures.append("fresh clone dynamic health check failed")

        print("\n=== fresh clone: smoke ===")
        ok, output = run([sys.executable, "-B", "scripts/dev.py", "smoke"], clone_dir, env=env)
        if output:
            print(output)
        if not ok:
            failures.append("fresh clone dynamic smoke check failed")
    finally:
        stop_processes(processes)

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Clone the public repository into a temp directory and prove the user-facing demo path works.",
    )
    parser.add_argument("--source", help="Git source to clone. Defaults to this repository's origin remote.")
    parser.add_argument("--keep", action="store_true", help="Keep the temporary clone for inspection.")
    args = parser.parse_args()

    source = args.source or origin_url()
    temp_root = Path(tempfile.mkdtemp(prefix="fde-public-clone-")) if args.keep else None
    failures: list[str] = []

    try:
        if temp_root is None:
            with tempfile.TemporaryDirectory(prefix="fde-public-clone-") as temp_dir:
                clone_dir = Path(temp_dir) / "repo"
                print(f"Cloning {source} into a temporary directory")
                clone_repository(source, clone_dir)
                failures.extend(run_static_checks(clone_dir))
                failures.extend(run_runtime_smoke(clone_dir))
        else:
            clone_dir = temp_root / "repo"
            print(f"Cloning {source} into {clone_dir}")
            clone_repository(source, clone_dir)
            failures.extend(run_static_checks(clone_dir))
            failures.extend(run_runtime_smoke(clone_dir))
            print(f"\nKept fresh clone at {clone_dir}")
    except Exception as exc:
        failures.append(str(exc))

    if failures:
        print("\nFresh clone experience check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("\nFresh clone experience check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
