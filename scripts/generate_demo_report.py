from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from quality_gate import SERVICES, healthy, start_service, wait_for_health


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "docs" / "demo_report.md"


def run_command(args: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    return result.returncode, result.stdout, result.stderr


def parse_eval_summaries(output: str) -> list[str]:
    summaries: list[str] = []
    current_name: str | None = None
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_name, current_lines
        if not current_name or not current_lines:
            return
        payload = json.loads("\n".join(current_lines))
        metrics = payload["metrics"]
        parts = [
            f"{current_name}: {metrics['passed_cases']}/{metrics['total_cases']} passed",
            f"pass_rate = {metrics['pass_rate']}",
        ]
        if "unsafe_leak_failures" in metrics:
            parts.append(f"unsafe_leak_failures = {metrics['unsafe_leak_failures']}")
        if "required_retrieval_recall_at_k" in metrics:
            parts.append(f"required_retrieval_recall_at_k = {metrics['required_retrieval_recall_at_k']}")
        if "mean_reciprocal_rank" in metrics:
            parts.append(f"mean_reciprocal_rank = {metrics['mean_reciprocal_rank']}")
        if "mean_ndcg_at_k" in metrics:
            parts.append(f"mean_ndcg_at_k = {metrics['mean_ndcg_at_k']}")
        if "mean_average_precision_at_k" in metrics:
            parts.append(f"mean_average_precision_at_k = {metrics['mean_average_precision_at_k']}")
        if "required_citation_coverage" in metrics:
            parts.append(f"required_citation_coverage = {metrics['required_citation_coverage']}")
        if "citation_retrieval_alignment" in metrics:
            parts.append(f"citation_retrieval_alignment = {metrics['citation_retrieval_alignment']}")
        if "security_event_coverage" in metrics:
            parts.append(f"security_event_coverage = {metrics['security_event_coverage']}")
        if "permission_block_coverage" in metrics:
            parts.append(f"permission_block_coverage = {metrics['permission_block_coverage']}")
        if "stale_source_filter_coverage" in metrics:
            parts.append(f"stale_source_filter_coverage = {metrics['stale_source_filter_coverage']}")
        if "unsafe_direct_side_effect_failures" in metrics:
            parts.append(
                f"unsafe_direct_side_effect_failures = {metrics['unsafe_direct_side_effect_failures']}"
            )
        if "unsafe_release_approval_failures" in metrics:
            parts.append(f"unsafe_release_approval_failures = {metrics['unsafe_release_approval_failures']}")
        summaries.append("- " + ", ".join(parts))
        current_name = None
        current_lines = []

    for raw_line in output.splitlines():
        line = raw_line.strip()
        if line.startswith("===") and line.endswith("==="):
            flush()
            current_name = line.strip("= ").strip()
            current_lines = []
        elif current_name and line:
            current_lines.append(raw_line)
    flush()
    return summaries


def parse_smoke_summary(output: str) -> str:
    match = re.search(r"Smoke tests: \d+/\d+ passed", output)
    if match:
        return match.group(0)
    return "Smoke test summary unavailable"


def ensure_services() -> list[subprocess.Popen]:
    processes: list[subprocess.Popen] = []
    for service in SERVICES:
        if healthy(service["health"]):
            continue
        process = start_service(service)
        if process is not None:
            processes.append(process)
        if not wait_for_health(service["health"]):
            raise RuntimeError(f"service did not become healthy: {service['name']}")
    return processes


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


def main() -> int:
    processes: list[subprocess.Popen] = []
    startup_error = ""
    try:
        processes = ensure_services()
    except RuntimeError as exc:
        startup_error = str(exc)

    health_code, health_out, health_err = run_command([sys.executable, "-B", "scripts/check_health.py"])
    smoke_code, smoke_out, smoke_err = run_command([sys.executable, "-B", "scripts/smoke_test_demo_flows.py"])
    eval_code, eval_out, eval_err = run_command([sys.executable, "-B", "scripts/run_all_evals.py"])
    stop_processes(processes)

    status = "PASS" if not startup_error and health_code == 0 and eval_code == 0 and smoke_code == 0 else "FAIL"
    eval_summaries = parse_eval_summaries(eval_out) if eval_code == 0 else []
    smoke_summary = parse_smoke_summary(smoke_out)
    failure_details = ""
    if status != "PASS":
        failure_details = f"""
## Failure Details

### Health

```text
{startup_error}
{health_out.strip()}
{health_err.strip()}
```

### Evals

```text
{eval_out.strip()}
{eval_err.strip()}
```

### Smoke

```text
{smoke_out.strip()}
{smoke_err.strip()}
```
"""

    report = f"""# FDE AI Systems Demo Report

Generated by: `python -B scripts/dev.py report`

Overall status: **{status}**

## Demo URLs

- Secure Enterprise Knowledge Copilot: http://127.0.0.1:8765
- Regulated Customer Operations Agent: http://127.0.0.1:8770
- AI Reliability Incident Console: http://127.0.0.1:8780

## Health Check

```text
{health_out.strip()}
{health_err.strip()}
```

## Eval Gate

{chr(10).join(eval_summaries) if eval_summaries else "- Eval summary unavailable"}

## Smoke Test Business Flows

```text
{smoke_summary}
```

{failure_details}

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

Project 3 proves AI release reliability:

- canary release incident triage
- eval regression evidence
- rollout blocking for unsafe regressions
- monitor-only handling for latency-only incidents
- trace and audit records for release decisions

## Recommended Review Flow

1. Open Project 1 and show Alice remote-work answer with HR citation.
2. Ask Alice for the finance plan and show abstention.
3. Switch to Morgan and show finance citation.
4. Run Project 1 evals.
5. Open Project 2 and run Market Blue investigation.
6. Show approval request and blocked direct `send_notice`.
7. Approve as supervisor and show audit.
8. Run Project 2 evals.
9. Open Project 3 and triage the unsafe canary incident.
10. Show linked failed evals and blocked rollout recommendation.
11. Switch to the latency incident and show monitor-only handling.
12. Run Project 3 evals.

"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"Wrote {REPORT_PATH}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
