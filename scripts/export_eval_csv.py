"""Export eval summaries from all projects to a CSV file.

Usage:
    python -B scripts/export_eval_csv.py [output.csv]

If no output path is given, results are written to eval_summaries.csv in
the repository root. This script reads captured eval output and does not
modify any runtime state.
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = [
    ROOT / "secure-enterprise-knowledge-copilot",
    ROOT / "regulated-customer-operations-agent",
]

FIELDNAMES = [
    "project",
    "total_cases",
    "passed_cases",
    "pass_rate",
    "unsafe_failures",
]


def _unsafe_count(metrics: dict) -> int:
    """Sum any unsafe-* metric keys present in the metrics dict."""
    return sum(
        v for k, v in metrics.items()
        if k.startswith("unsafe") and isinstance(v, (int, float))
    )


def collect_summaries() -> list[dict]:
    rows: list[dict] = []
    for project in PROJECTS:
        result = subprocess.run(
            [sys.executable, "-B", "scripts/run_eval.py"],
            cwd=project,
            text=True,
            capture_output=True,
        )
        if result.returncode not in (0, 1):
            print(
                f"Warning: {project.name} eval exited with code {result.returncode}",
                file=sys.stderr,
            )
        try:
            payload = json.loads(result.stdout)
            metrics = payload["metrics"]
        except (json.JSONDecodeError, KeyError) as exc:
            print(f"Warning: could not parse eval output for {project.name}: {exc}", file=sys.stderr)
            continue

        rows.append({
            "project": project.name,
            "total_cases": metrics.get("total_cases", ""),
            "passed_cases": metrics.get("passed_cases", ""),
            "pass_rate": metrics.get("pass_rate", ""),
            "unsafe_failures": _unsafe_count(metrics),
        })
    return rows


def write_csv(rows: list[dict], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "eval_summaries.csv"
    rows = collect_summaries()
    if not rows:
        print("No eval summaries collected.", file=sys.stderr)
        return 1
    write_csv(rows, output)
    print(f"Wrote {len(rows)} row(s) to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
