from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from datetime import datetime
from pathlib import Path

from check_visual_asset_manifest import png_size, sha256


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "visual_assets_manifest.json"
VIEWPORT = [1400, 900]
PROJECTS = [
    {
        "name": "secure-enterprise-knowledge-copilot",
        "path": ROOT / "secure-enterprise-knowledge-copilot",
        "preferred_port": 8765,
        "asset": ROOT / "docs" / "assets" / "secure-knowledge-copilot-screenshot.png",
        "contrast_samples": [
            {
                "name": "title text",
                "kind": "dark_text_on_light",
                "region": [16, 38, 460, 26],
                "background": [20, 20],
                "minimum_ratio": 4.5,
            },
            {
                "name": "primary action text",
                "kind": "light_text_on_fill",
                "region": [346, 354, 668, 40],
                "minimum_ratio": 4.5,
            },
            {
                "name": "quick action text",
                "kind": "dark_text_on_light",
                "region": [345, 166, 162, 33],
                "background": [360, 184],
                "minimum_ratio": 4.5,
            },
        ],
    },
    {
        "name": "regulated-customer-operations-agent",
        "path": ROOT / "regulated-customer-operations-agent",
        "preferred_port": 8770,
        "asset": ROOT / "docs" / "assets" / "regulated-ops-agent-screenshot.png",
        "contrast_samples": [
            {
                "name": "title text",
                "kind": "dark_text_on_light",
                "region": [16, 38, 430, 26],
                "background": [20, 20],
                "minimum_ratio": 4.5,
            },
            {
                "name": "primary action text",
                "kind": "light_text_on_fill",
                "region": [346, 358, 668, 40],
                "minimum_ratio": 4.5,
            },
            {
                "name": "quick action text",
                "kind": "dark_text_on_light",
                "region": [345, 166, 162, 36],
                "background": [360, 184],
                "minimum_ratio": 4.5,
            },
        ],
    },
    {
        "name": "ai-reliability-incident-console",
        "path": ROOT / "ai-reliability-incident-console",
        "preferred_port": 8780,
        "asset": ROOT / "docs" / "assets" / "ai-reliability-incident-console-screenshot.png",
        "contrast_samples": [
            {
                "name": "title text",
                "kind": "dark_text_on_light",
                "region": [16, 38, 390, 26],
                "background": [20, 20],
                "minimum_ratio": 4.5,
            },
            {
                "name": "primary action text",
                "kind": "light_text_on_fill",
                "region": [346, 379, 668, 40],
                "minimum_ratio": 4.5,
            },
            {
                "name": "quick action text",
                "kind": "dark_text_on_light",
                "region": [345, 330, 330, 37],
                "background": [360, 348],
                "minimum_ratio": 4.5,
            },
        ],
    },
]


def reserve_port(preferred: int) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(("127.0.0.1", preferred))
            return preferred
        except OSError:
            sock.bind(("127.0.0.1", 0))
            return int(sock.getsockname()[1])


def wait_for_health(port: int, seconds: int = 20) -> bool:
    url = f"http://127.0.0.1:{port}/api/health"
    for _ in range(seconds):
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return True
        except Exception:
            time.sleep(1)
    return False


def start_service(project: dict, port: int) -> subprocess.Popen:
    return subprocess.Popen(
        [sys.executable, "-B", "app.py", "--reset", "--port", str(port)],
        cwd=project["path"],
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


def browser_candidates() -> list[Path]:
    env_path = os.environ.get("FDE_BROWSER_BIN")
    candidates: list[Path] = [Path(env_path)] if env_path else []
    for name in ("chrome", "google-chrome", "chromium", "chromium-browser", "msedge"):
        found = shutil.which(name)
        if found:
            candidates.append(Path(found))
    candidates.extend(
        [
            Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
            Path("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
            Path("C:/Program Files/Microsoft/Edge/Application/msedge.exe"),
            Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
        ]
    )
    unique: list[Path] = []
    seen = set()
    for candidate in candidates:
        key = str(candidate).lower()
        if key not in seen:
            unique.append(candidate)
            seen.add(key)
    return unique


def find_browser() -> Path:
    for candidate in browser_candidates():
        if candidate.exists():
            return candidate
    raise RuntimeError("No Chrome/Chromium/Edge executable found. Set FDE_BROWSER_BIN to refresh screenshots.")


def capture(browser: Path, url: str, output: Path, profile_dir: Path) -> None:
    if output.exists():
        output.unlink()
    args = [
        str(browser),
        "--headless",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-extensions",
        "--hide-scrollbars",
        f"--user-data-dir={profile_dir}",
        f"--window-size={VIEWPORT[0]},{VIEWPORT[1]}",
        "--virtual-time-budget=5000",
        f"--screenshot={output}",
        url,
    ]
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    if result.returncode != 0:
        detail = (result.stdout + result.stderr).strip()
        raise RuntimeError(f"browser screenshot failed for {url}: {detail}")
    if not output.exists():
        detail = (result.stdout + result.stderr).strip()
        raise RuntimeError(f"browser did not write screenshot for {url}: {detail}")
    size = png_size(output)
    if size != tuple(VIEWPORT):
        raise RuntimeError(f"{output.relative_to(ROOT).as_posix()}: expected {VIEWPORT}, found {size}")
    if output.stat().st_size < 30_000:
        raise RuntimeError(f"{output.relative_to(ROOT).as_posix()}: screenshot is suspiciously small")


def source_files(project: dict) -> list[Path]:
    web = project["path"] / "web"
    files = [web / "index.html", web / "styles.css"]
    files.extend(sorted((web / "js").glob("*.js")))
    return files


def render_manifest() -> dict:
    return {
        "version": 1,
        "purpose": "Keep README screenshots tied to the frontend source files they were captured from.",
        "capture": {
            "date": datetime.now().date().isoformat(),
            "viewport": VIEWPORT,
            "method": "scripts/refresh_visual_assets.py after local demo services reached /api/health",
        },
        "assets": [
            {
                "path": project["asset"].relative_to(ROOT).as_posix(),
                "kind": "readme_screenshot",
                "size": VIEWPORT,
                "sha256": sha256(project["asset"]),
                "source_files": [
                    {
                        "path": source.relative_to(ROOT).as_posix(),
                        "sha256": sha256(source),
                    }
                    for source in source_files(project)
                ],
                "contrast_samples": project["contrast_samples"],
            }
            for project in PROJECTS
        ],
    }


def write_manifest() -> None:
    MANIFEST.write_text(json.dumps(render_manifest(), indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh README screenshots and visual asset manifest.")
    parser.add_argument("--check-browser", action="store_true", help="Only verify that a browser executable is available.")
    args = parser.parse_args()

    try:
        browser = find_browser()
        if args.check_browser:
            print(f"browser found: {browser.name}")
            return 0

        ports = [reserve_port(project["preferred_port"]) for project in PROJECTS]
        processes: list[subprocess.Popen] = []
        with tempfile.TemporaryDirectory(prefix="fde-visual-assets-") as temp_dir:
            temp_root = Path(temp_dir)
            try:
                for project, port in zip(PROJECTS, ports):
                    print(f"Starting {project['name']} on port {port}")
                    processes.append(start_service(project, port))
                for project, port in zip(PROJECTS, ports):
                    if not wait_for_health(port):
                        raise RuntimeError(f"{project['name']} did not become healthy on port {port}")
                for project, port in zip(PROJECTS, ports):
                    print(f"Capturing {project['asset'].relative_to(ROOT).as_posix()}")
                    capture(
                        browser,
                        f"http://127.0.0.1:{port}/",
                        project["asset"],
                        temp_root / f"profile-{project['name']}",
                    )
            finally:
                stop_processes(processes)
        write_manifest()
        print("Refreshed README screenshots and docs/visual_assets_manifest.json")
        return 0
    except Exception as exc:
        print(f"Visual asset refresh failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
