from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "docs" / "demo_report.md"


def run_command(args: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    return result.returncode, result.stdout, result.stderr


def main() -> int:
    health_code, health_out, health_err = run_command([sys.executable, "-B", "scripts/check_health.py"])
    eval_code, eval_out, eval_err = run_command([sys.executable, "-B", "scripts/run_all_evals.py"])
    smoke_code, smoke_out, smoke_err = run_command([sys.executable, "-B", "scripts/smoke_test_demo_flows.py"])

    status = "PASS" if health_code == 0 and eval_code == 0 and smoke_code == 0 else "FAIL"
    now = datetime.now().isoformat(timespec="seconds")
    report = f"""# FDE Portfolio Demo Report

Generated: {now}

Overall status: **{status}**

## Demo URLs

- Secure Enterprise Knowledge Copilot: http://127.0.0.1:8765
- Regulated Customer Operations Agent: http://127.0.0.1:8770

## Health Check

```text
{health_out.strip()}
{health_err.strip()}
```

## Eval Gate

```text
{eval_out.strip()}
{eval_err.strip()}
```

## Smoke Test Business Flows

```text
{smoke_out.strip()}
{smoke_err.strip()}
```

## Demo Narrative

Project 1 proves secure enterprise RAG:

- role-aware retrieval
- citation enforcement
- abstention for inaccessible or unsupported answers
- prompt-injection handling
- trace and audit records

Project 2 proves governed agentic operations:

- tool calling against business objects
- internal action automation
- human approval queue for external side effects
- direct side-effect blocking
- supervisor-only approval
- trace and audit records

## Recommended Interview Flow

1. Open Project 1 and show Alice remote-work answer with HR citation.
2. Ask Alice for the finance plan and show abstention.
3. Switch to Morgan and show finance citation.
4. Run Project 1 evals.
5. Open Project 2 and run Market Blue investigation.
6. Show approval request and blocked direct `send_notice`.
7. Approve as supervisor and show audit.
8. Run Project 2 evals.

"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"Wrote {REPORT_PATH}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

