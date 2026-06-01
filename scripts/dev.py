from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

COMMANDS = {
    "start": ["scripts/start_demo_servers.py"],
    "assets": ["scripts/check_public_assets.py"],
    "health": ["scripts/check_health.py"],
    "evals": ["scripts/run_all_evals.py"],
    "eval-csv": ["scripts/export_eval_csv.py"],
    "otel-traces": ["scripts/export_traces_otel.py"],
    "replay": ["scripts/replay_demo.py"],
    "smoke": ["scripts/smoke_test_demo_flows.py"],
    "report": ["scripts/generate_demo_report.py"],
    "safety": ["scripts/public_safety_scan.py"],
    "quality": ["scripts/quality_gate.py"],
    "verify": ["scripts/ci_quality_gate.py"],
}


def run_script(script: str) -> int:
    return subprocess.run([sys.executable, "-B", script], cwd=ROOT).returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Cross-platform developer entrypoint for the FDE AI Systems Portfolio.",
    )
    parser.add_argument(
        "command",
        choices=sorted(COMMANDS.keys()),
        help=(
            "start: run both demo servers; assets/health/evals/eval-csv/otel-traces/replay/smoke/report/safety/quality: run individual gates; "
            "verify: start services if needed and run the full CI-quality gate."
        ),
    )
    args = parser.parse_args()
    return run_script(COMMANDS[args.command][0])


if __name__ == "__main__":
    raise SystemExit(main())
