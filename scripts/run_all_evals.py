from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECTS = [
    ROOT / "secure-enterprise-knowledge-copilot",
    ROOT / "regulated-customer-operations-agent",
    ROOT / "ai-reliability-incident-console",
]


def main() -> int:
    failed = False
    for project in PROJECTS:
        print(f"\n=== {project.name} ===")
        result = subprocess.run(
            [sys.executable, "-B", "scripts/run_eval.py"],
            cwd=project,
            text=True,
            capture_output=True,
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        if result.returncode != 0:
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
