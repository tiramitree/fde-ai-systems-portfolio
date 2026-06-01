"""Export eval summaries from all projects to a CSV file.

Usage:
    python -B scripts/export_eval_csv.py [output.csv]

If no output path is given, results are written to eval_summaries.csv in
the repository root. That file is a generated artifact and is not tracked
by git; add it to .gitignore if you do not want it to appear in `git status`.

Note: this script invokes each project's eval runner, which resets and writes
that project's `data/eval_runtime_state.json`. Those files are already listed
in .gitignore and are not committed.

Exit code: non-zero if any project eval exits non-zero, if any eval output
cannot be parsed, or if no summaries were collected.
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


def collect_summaries() -> tuple[list[dict], bool]:
    """Run all project evals and collect their summary metrics.

    Returns a (rows, had_failures) tuple. had_failures is True if any eval
    exited non-zero or its output could not be parsed.
    """
    rows: list[dict] = []
    had_failures = False
    for project in PROJECTS:
        result = subprocess.run(
            [sys.executable, "-B", "scripts/run_eval.py"],
            cwd=project,
            text=True,
            capture_output=True,
        )
        if result.returncode != 0:
            print(
                f"Error: {project.name} eval exited with code {result.returncode}",
                file=sys.stderr,
            )
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            had_failures = True

        try:
            payload = json.loads(result.stdout)
            metrics = payload["metrics"]
        except (json.JSONDecodeError, KeyError) as exc:
            print(f"Error: could not parse eval output for {project.name}: {exc}", file=sys.stderr)
            had_failures = True
            continue

        rows.append({
            "project": project.name,
            "total_cases": metrics.get("total_cases", ""),
            "passed_cases": metrics.get("passed_cases", ""),
            "pass_rate": metrics.get("pass_rate", ""),
            "unsafe_failures": _unsafe_count(metrics),
        })
    return rows, had_failures


def write_csv(rows: list[dict], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "eval_summaries.csv"
    rows, had_failures = collect_summaries()
    if not rows:
        print("No eval summaries collected.", file=sys.stderr)
        return 1
    write_csv(rows, output)
    print(f"Wrote {len(rows)} row(s) to {output}")
    return 1 if had_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
