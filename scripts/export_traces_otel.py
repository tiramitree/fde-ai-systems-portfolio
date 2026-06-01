from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "otel_traces.json"
INSTRUMENTATION_SCOPE = "fde-ai-systems-portfolio.local-trace-exporter"
INSTRUMENTATION_VERSION = "0.1.0"

PROJECTS = [
    {
        "name": "secure-enterprise-knowledge-copilot",
        "kind": "copilot",
        "state_path": ROOT / "secure-enterprise-knowledge-copilot" / "data" / "runtime_state.json",
    },
    {
        "name": "regulated-customer-operations-agent",
        "kind": "ops_agent",
        "state_path": ROOT / "regulated-customer-operations-agent" / "data" / "runtime_state.json",
    },
]


def stable_hex(value: str, chars: int) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:chars]


def trace_id(value: str) -> str:
    compact = value.replace("-", "").lower()
    if len(compact) == 32 and all(char in "0123456789abcdef" for char in compact):
        return compact
    return stable_hex(value, 32)


def span_id(project: str, trace: dict) -> str:
    return stable_hex(f"{project}:{trace.get('id', '')}", 16)


def unix_nano(timestamp: str) -> int:
    if not timestamp:
        return 0
    normalized = timestamp.replace("Z", "+00:00")
    dt = datetime.fromisoformat(normalized)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1_000_000_000)


def any_value(value: Any) -> dict:
    if isinstance(value, bool):
        return {"boolValue": value}
    if isinstance(value, int):
        return {"intValue": str(value)}
    if isinstance(value, float):
        return {"doubleValue": value}
    if value is None:
        return {"stringValue": ""}
    if isinstance(value, (list, dict)):
        return {"stringValue": json.dumps(value, sort_keys=True, separators=(",", ":"))}
    return {"stringValue": str(value)}


def attr(key: str, value: Any) -> dict:
    return {"key": key, "value": any_value(value)}


def event(time_nano: int, name: str, attributes: dict[str, Any] | None = None) -> dict:
    return {
        "timeUnixNano": str(time_nano),
        "name": name,
        "attributes": [attr(key, value) for key, value in sorted((attributes or {}).items())],
    }


def load_state(path: Path) -> dict:
    if not path.exists():
        return {"traces": []}
    return json.loads(path.read_text(encoding="utf-8"))


def copilot_span(project: str, trace: dict) -> dict:
    payload = trace.get("payload", {})
    retrieval = payload.get("retrieval", {})
    output = payload.get("output", {})
    start = unix_nano(trace.get("created_at", ""))
    end = start + 1_000_000

    attributes = {
        "app.project": project,
        "app.trace_type": "knowledge_query",
        "app.user_id": trace.get("user_id", ""),
        "app.question": trace.get("question", ""),
        "app.abstained": output.get("abstain_reason") is not None,
        "app.abstain_reason": output.get("abstain_reason") or "",
        "app.model_provider": output.get("model_provider", ""),
        "app.retrieval.hit_count": len(retrieval.get("hits", [])),
        "app.permission_blocked_count": retrieval.get("permission_blocked_count", 0),
        "app.citation_count": len(output.get("citations", [])),
        "app.security_event_count": len(output.get("security_events", [])),
    }
    events = [
        event(
            start,
            "retrieval.completed",
            {
                "query_tokens": retrieval.get("query_tokens", []),
                "hit_count": len(retrieval.get("hits", [])),
                "permission_blocked_count": retrieval.get("permission_blocked_count", 0),
            },
        )
    ]
    for citation in output.get("citations", []):
        events.append(
            event(
                start,
                "evidence.cited",
                {
                    "doc_id": citation.get("doc_id", ""),
                    "chunk_id": citation.get("chunk_id", ""),
                    "title": citation.get("title", ""),
                    "score": citation.get("score", 0),
                },
            )
        )
    for item in output.get("security_events", []):
        events.append(event(start, "security.event", item))

    return build_span(project, trace, "copilot.query", attributes, events, start, end)


def ops_agent_span(project: str, trace: dict) -> dict:
    result = trace.get("result", {})
    start = unix_nano(trace.get("created_at", ""))
    end = start + 1_000_000
    attributes = {
        "app.project": project,
        "app.trace_type": "agent_message",
        "app.user_id": trace.get("user_id", ""),
        "app.message": trace.get("message", ""),
        "app.intent": trace.get("intent", result.get("intent", "")),
        "app.model_router": result.get("model_router", "local"),
        "app.tool_call_count": len(result.get("tool_calls", [])),
        "app.approval_count": len(result.get("approvals", [])),
        "app.blocked_action_count": len(result.get("blocked_actions", [])),
        "app.cited_policy_count": len(result.get("cited_policies", [])),
    }
    events = []
    for tool_call in result.get("tool_calls", []):
        events.append(event(start, "tool.call", tool_call))
    for approval in result.get("approvals", []):
        events.append(
            event(
                start,
                "approval.requested",
                {
                    "approval_id": approval.get("id", ""),
                    "action_type": approval.get("action_type", ""),
                    "status": approval.get("status", ""),
                },
            )
        )
    for blocked in result.get("blocked_actions", []):
        events.append(event(start, "governance.blocked_action", blocked))
    for policy in result.get("cited_policies", []):
        events.append(event(start, "policy.cited", policy))

    return build_span(project, trace, "ops_agent.process_message", attributes, events, start, end)


def build_span(
    project: str,
    trace: dict,
    name: str,
    attributes: dict[str, Any],
    events: list[dict],
    start: int,
    end: int,
) -> dict:
    return {
        "traceId": trace_id(str(trace.get("id", ""))),
        "spanId": span_id(project, trace),
        "name": name,
        "kind": 1,
        "startTimeUnixNano": str(start),
        "endTimeUnixNano": str(end),
        "attributes": [attr(key, value) for key, value in sorted(attributes.items())],
        "events": events,
        "status": {"code": 1},
    }


def resource_span(project: dict, spans: list[dict]) -> dict:
    return {
        "resource": {
            "attributes": [
                attr("service.name", project["name"]),
                attr("deployment.environment", "local"),
                attr("telemetry.sdk.name", "fde-local-exporter"),
            ]
        },
        "scopeSpans": [
            {
                "scope": {
                    "name": INSTRUMENTATION_SCOPE,
                    "version": INSTRUMENTATION_VERSION,
                },
                "spans": spans,
            }
        ],
    }


def collect_resource_spans() -> tuple[list[dict], int]:
    output = []
    total = 0
    for project in PROJECTS:
        state = load_state(project["state_path"])
        traces = sorted(state.get("traces", []), key=lambda item: (item.get("created_at", ""), item.get("id", "")))
        spans = []
        for trace in traces:
            if project["kind"] == "copilot":
                spans.append(copilot_span(project["name"], trace))
            else:
                spans.append(ops_agent_span(project["name"], trace))
        total += len(spans)
        output.append(resource_span(project, spans))
    return output, total


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export local demo trace records to an OTLP/JSON-compatible resourceSpans payload.",
    )
    parser.add_argument("output", nargs="?", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    resource_spans, total = collect_resource_spans()
    payload = {"resourceSpans": resource_spans}
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {total} span(s) to {output}")
    if total == 0:
        print("No traces found. Run python -B scripts/dev.py replay or smoke first.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
