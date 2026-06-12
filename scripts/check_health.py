from __future__ import annotations

import json
import os
import sys
from urllib.request import urlopen


BASE_URLS = [
    os.getenv("FDE_PROJECT_1_URL", "http://127.0.0.1:8765").rstrip("/"),
    os.getenv("FDE_PROJECT_2_URL", "http://127.0.0.1:8770").rstrip("/"),
    os.getenv("FDE_PROJECT_3_URL", "http://127.0.0.1:8780").rstrip("/"),
]


def main() -> int:
    failed = False
    for base_url in BASE_URLS:
        health_url = f"{base_url}/api/health"
        ready_url = f"{base_url}/api/ready"
        try:
            with urlopen(health_url, timeout=5) as response:
                health = json.loads(response.read().decode("utf-8"))
            with urlopen(ready_url, timeout=5) as response:
                readiness = json.loads(response.read().decode("utf-8"))
            ready_checks = readiness.get("checks", {})
            if health.get("status") != "ok":
                raise RuntimeError(f"health status was {health.get('status')}")
            expected_ready_checks = {"storage", "seed_data", "eval_state", "scenario_snapshot", "scenario_files"}
            if (
                readiness.get("status") != "ready"
                or readiness.get("app") != health.get("app")
                or readiness.get("ready") is not True
                or not isinstance(ready_checks, dict)
                or not expected_ready_checks.issubset(ready_checks)
            ):
                raise RuntimeError(f"readiness status was {readiness}")
            print(
                f"{base_url}: health ok ({health['app']}); "
                f"ready checks={','.join(sorted(ready_checks.keys()))}"
            )
        except Exception as exc:
            failed = True
            print(f"{base_url}: failed - {exc}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
