from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, quote, unquote, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

from trace_redaction import REDACTION_POLICY, redact_value


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "otel_traces.json"
INSTRUMENTATION_SCOPE = "fde-ai-systems-portfolio.local-trace-exporter"
INSTRUMENTATION_VERSION = "0.1.0"
DEFAULT_OTLP_HTTP_ENDPOINT = "http://localhost:4318"
DEFAULT_OTLP_HTTP_TIMEOUT_SECONDS = 10.0

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
    {
        "name": "ai-reliability-incident-console",
        "kind": "reliability_console",
        "state_path": ROOT / "ai-reliability-incident-console" / "data" / "runtime_state.json",
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
    return {"key": key, "value": any_value(redact_value(value))}


def event(time_nano: int, name: str, attributes: dict[str, Any] | None = None) -> dict:
    return {
        "timeUnixNano": str(time_nano),
        "name": name,
        "attributes": [attr(key, value) for key, value in sorted((attributes or {}).items())],
    }


def parse_otlp_headers(value: str) -> dict[str, str]:
    if not value.strip():
        return {}
    headers: dict[str, str] = {}
    for raw_pair in value.split(","):
        pair = raw_pair.strip()
        if not pair:
            continue
        if "=" not in pair:
            raise ValueError("OTLP headers must use key=value pairs separated by commas.")
        key, raw_value = pair.split("=", 1)
        key = unquote(key.strip())
        if not key:
            raise ValueError("OTLP header keys cannot be empty.")
        headers[key] = unquote(raw_value.strip())
    return headers


def endpoint_with_traces_path(base_endpoint: str) -> str:
    parsed = urlsplit(base_endpoint)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("OTLP HTTP endpoint must be an http:// or https:// URL with a host.")

    base_path = parsed.path or "/"
    if not base_path.endswith("/"):
        base_path += "/"
    path = base_path + "v1/traces"
    query = urlencode(parse_qsl(parsed.query, keep_blank_values=True), doseq=True, quote_via=quote)
    return urlunsplit((parsed.scheme, parsed.netloc, path, query, ""))


def resolve_otlp_traces_url(base_endpoint: str | None, traces_endpoint: str | None) -> str:
    if traces_endpoint:
        parsed = urlsplit(traces_endpoint)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("OTLP traces endpoint must be an http:// or https:// URL with a host.")
        return traces_endpoint
    return endpoint_with_traces_path(base_endpoint or DEFAULT_OTLP_HTTP_ENDPOINT)


def ensure_http_json_protocol() -> None:
    protocol = (
        os.environ.get("OTEL_EXPORTER_OTLP_TRACES_PROTOCOL")
        or os.environ.get("OTEL_EXPORTER_OTLP_PROTOCOL")
        or "http/json"
    )
    if protocol != "http/json":
        raise ValueError(
            "This dependency-free handoff sends OTLP/HTTP JSON. "
            "Set OTEL_EXPORTER_OTLP_PROTOCOL=http/json or omit the protocol variable."
        )


def merged_otlp_headers(cli_headers: list[str]) -> dict[str, str]:
    merged: dict[str, str] = {}
    for env_name in ("OTEL_EXPORTER_OTLP_HEADERS", "OTEL_EXPORTER_OTLP_TRACES_HEADERS"):
        merged.update(parse_otlp_headers(os.environ.get(env_name, "")))
    for header in cli_headers:
        merged.update(parse_otlp_headers(header))
    return merged


def send_otlp_http_json(payload: dict, url: str, headers: dict[str, str], timeout: float) -> tuple[int, str]:
    request_headers = {
        "Content-Type": "application/json",
        "User-Agent": f"{INSTRUMENTATION_SCOPE}/{INSTRUMENTATION_VERSION}",
        **headers,
    }
    request = Request(
        url,
        data=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
        headers=request_headers,
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OTLP HTTP export failed with status {exc.code}: {body}") from exc
    except URLError as exc:
        raise RuntimeError(f"OTLP HTTP export failed: {exc}") from exc


def load_state(path: Path) -> dict:
    if not path.exists():
        return {"traces": []}
    return json.loads(path.read_text(encoding="utf-8"))


def find_by_id(items: list[dict], item_id: str) -> dict | None:
    return next((item for item in items if item.get("id") == item_id), None)


def latest_eval_for_release(state: dict, release_id: str) -> dict:
    runs = [run for run in state.get("eval_runs", []) if run.get("release_id") == release_id]
    if not runs:
        return {}
    return sorted(runs, key=lambda run: run.get("created_at", ""), reverse=True)[0]


def linked_failed_cases(eval_run: dict, incident: dict) -> list[dict]:
    linked_ids = set(incident.get("linked_eval_case_ids", []))
    failed = [case for case in eval_run.get("cases", []) if not case.get("passed")]
    if linked_ids:
        linked = [case for case in failed if case.get("id") in linked_ids]
        if linked:
            return linked
    return failed


def audit_events_for_trace(state: dict, trace: dict) -> list[dict]:
    trace_id = str(trace.get("id", ""))
    return [
        item
        for item in state.get("audit_events", [])
        if item.get("details", {}).get("trace_id") == trace_id
    ]


def copilot_span(project: str, trace: dict) -> dict:
    payload = trace.get("payload", {})
    retrieval = payload.get("retrieval", {})
    profile = retrieval.get("profile", {}) if isinstance(retrieval.get("profile", {}), dict) else {}
    output = payload.get("output", {})
    start = unix_nano(trace.get("created_at", ""))
    end = start + 1_000_000

    attributes = {
        "app.project": project,
        "app.redaction_policy": REDACTION_POLICY,
        "app.trace_type": "knowledge_query",
        "app.user_id": trace.get("user_id", ""),
        "app.question": trace.get("question", ""),
        "app.abstained": output.get("abstain_reason") is not None,
        "app.abstain_reason": output.get("abstain_reason") or "",
        "app.model_provider": output.get("model_provider", ""),
        "app.retrieval.hit_count": len(retrieval.get("hits", [])),
        "app.permission_blocked_count": retrieval.get("permission_blocked_count", 0),
        "app.source_lifecycle_policy": profile.get("source_lifecycle_policy", ""),
        "app.stale_filtered_count": profile.get("stale_filtered_count", 0),
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
                "source_lifecycle_policy": profile.get("source_lifecycle_policy", ""),
                "stale_filtered_count": profile.get("stale_filtered_count", 0),
            },
        )
    ]
    for citation in output.get("citations", []):
        source_span = citation.get("source_span", {})
        evidence_spans = citation.get("evidence_spans", [])
        events.append(
            event(
                start,
                "evidence.cited",
                {
                    "doc_id": citation.get("doc_id", ""),
                    "chunk_id": citation.get("chunk_id", ""),
                    "title": citation.get("title", ""),
                    "score": citation.get("score", 0),
                    "source_span.text_unit": source_span.get("text_unit", ""),
                    "source_span.start_line": source_span.get("start_line", 0),
                    "source_span.end_line": source_span.get("end_line", 0),
                    "evidence_excerpt": citation.get("evidence_excerpt", ""),
                    "evidence_span_count": len(evidence_spans) if isinstance(evidence_spans, list) else 0,
                },
            )
        )
        if isinstance(evidence_spans, list):
            for item in evidence_spans[:5]:
                item_span = item.get("source_span", {}) if isinstance(item, dict) else {}
                events.append(
                    event(
                        start,
                        "evidence.sentence_span",
                        {
                            "doc_id": citation.get("doc_id", ""),
                            "chunk_id": citation.get("chunk_id", ""),
                            "text": item.get("text", "") if isinstance(item, dict) else "",
                            "source_span.text_unit": item_span.get("text_unit", ""),
                            "source_span.start_line": item_span.get("start_line", 0),
                            "source_span.end_line": item_span.get("end_line", 0),
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
        "app.redaction_policy": REDACTION_POLICY,
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


def reliability_console_span(project: str, trace: dict, state: dict) -> dict:
    result = trace.get("result", {})
    release_id = trace.get("release_id", "")
    incident_id = trace.get("incident_id", "")
    release = find_by_id(state.get("releases", []), release_id) or {}
    incident = find_by_id(state.get("incidents", []), incident_id) or {}
    eval_run = latest_eval_for_release(state, release_id)
    failed_cases = linked_failed_cases(eval_run, incident)
    runbooks = [
        find_by_id(state.get("runbooks", []), runbook_id) or {"id": runbook_id}
        for runbook_id in incident.get("runbook_ids", [])
    ]
    linked_audits = audit_events_for_trace(state, trace)
    start = unix_nano(trace.get("created_at", ""))
    end = start + 1_000_000

    attributes = {
        "app.project": project,
        "app.redaction_policy": REDACTION_POLICY,
        "app.trace_type": "release_triage",
        "app.user_id": trace.get("user_id", ""),
        "app.release_id": release_id,
        "app.release_status": release.get("status", ""),
        "app.release_traffic_percent": release.get("traffic_percent", 0),
        "app.incident_id": incident_id,
        "app.incident_status": incident.get("status", ""),
        "app.incident_severity": incident.get("severity", ""),
        "app.incident_category": incident.get("category", ""),
        "app.eval_run_id": eval_run.get("id", ""),
        "app.failed_eval_count": result.get("failed_eval_count", len(failed_cases)),
        "app.recommendation": result.get("recommendation", ""),
        "app.release_blocked": result.get("release_blocked", False),
        "app.runbook_count": len(runbooks),
        "app.signal_count": len(incident.get("signals", [])),
        "app.audit_event_count": len(linked_audits),
    }

    events = [
        event(
            start,
            "release.triage_decision",
            {
                "release_id": release_id,
                "incident_id": incident_id,
                "recommendation": result.get("recommendation", ""),
                "release_blocked": result.get("release_blocked", False),
                "failed_eval_count": result.get("failed_eval_count", len(failed_cases)),
            },
        ),
        event(
            start,
            "release.context",
            {
                "release_status": release.get("status", ""),
                "owner": release.get("owner", ""),
                "traffic_percent": release.get("traffic_percent", 0),
            },
        ),
    ]
    rollout_event = "release.rollout_blocked" if result.get("release_blocked") else "release.rollout_monitored"
    events.append(event(start, rollout_event, {"recommendation": result.get("recommendation", "")}))
    for signal in incident.get("signals", []):
        events.append(event(start, "incident.signal", {"signal": signal}))
    for case in failed_cases:
        events.append(
            event(
                start,
                "eval.failure.linked",
                {
                    "case_id": case.get("id", ""),
                    "category": case.get("category", ""),
                    "severity": case.get("severity", ""),
                    "details": case.get("details", ""),
                },
            )
        )
    for runbook in runbooks:
        events.append(
            event(
                start,
                "runbook.linked",
                {
                    "runbook_id": runbook.get("id", ""),
                    "title": runbook.get("title", ""),
                    "step_count": len(runbook.get("steps", [])),
                },
            )
        )
    for audit_item in linked_audits:
        events.append(
            event(
                start,
                "audit.linked",
                {
                    "audit_id": audit_item.get("id", ""),
                    "action": audit_item.get("action", ""),
                    "user_id": audit_item.get("user_id", ""),
                },
            )
        )

    return build_span(project, trace, "reliability.release_triage", attributes, events, start, end)


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
                attr("app.redaction_policy", REDACTION_POLICY),
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


def collect_resource_spans() -> tuple[list[dict], int, dict[str, int]]:
    output = []
    total = 0
    counts = {}
    for project in PROJECTS:
        state = load_state(project["state_path"])
        traces = sorted(state.get("traces", []), key=lambda item: (item.get("created_at", ""), item.get("id", "")))
        spans = []
        for trace in traces:
            if project["kind"] == "copilot":
                spans.append(copilot_span(project["name"], trace))
            elif project["kind"] == "ops_agent":
                spans.append(ops_agent_span(project["name"], trace))
            elif project["kind"] == "reliability_console":
                spans.append(reliability_console_span(project["name"], trace, state))
            else:
                raise ValueError(f"Unknown project kind: {project['kind']}")
        total += len(spans)
        counts[project["name"]] = len(spans)
        output.append(resource_span(project, spans))
    return output, total, counts


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export local demo trace records to an OTLP/JSON-compatible resourceSpans payload.",
    )
    parser.add_argument("output", nargs="?", default=str(DEFAULT_OUTPUT))
    parser.add_argument(
        "--send-otlp-http",
        action="store_true",
        help="Also POST the OTLP/JSON payload to an optional OTLP HTTP collector endpoint.",
    )
    parser.add_argument(
        "--otlp-http-endpoint",
        default=os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"),
        help="Base OTLP HTTP endpoint; /v1/traces is appended. Defaults to OTEL_EXPORTER_OTLP_ENDPOINT or http://localhost:4318.",
    )
    parser.add_argument(
        "--otlp-http-traces-endpoint",
        default=os.environ.get("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT"),
        help="Signal-specific traces endpoint used as-is. Defaults to OTEL_EXPORTER_OTLP_TRACES_ENDPOINT.",
    )
    parser.add_argument(
        "--otlp-http-header",
        action="append",
        default=[],
        help="Additional OTLP header in key=value form. May be repeated. Values are not printed.",
    )
    parser.add_argument(
        "--otlp-http-timeout",
        type=float,
        default=DEFAULT_OTLP_HTTP_TIMEOUT_SECONDS,
        help="OTLP HTTP request timeout in seconds.",
    )
    args = parser.parse_args()

    resource_spans, total, counts = collect_resource_spans()
    payload = {"resourceSpans": resource_spans}
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    covered = sum(1 for count in counts.values() if count > 0)
    print(f"Wrote {total} span(s) across {covered}/{len(counts)} project(s) to {output}")
    missing = [name for name, count in counts.items() if count == 0]
    if missing:
        print(
            "Missing spans for: "
            + ", ".join(missing)
            + ". Run python -B scripts/dev.py replay or smoke first.",
            file=sys.stderr,
        )
        return 1
    if args.send_otlp_http:
        try:
            ensure_http_json_protocol()
            url = resolve_otlp_traces_url(args.otlp_http_endpoint, args.otlp_http_traces_endpoint)
            headers = merged_otlp_headers(args.otlp_http_header)
            status, response_body = send_otlp_http_json(payload, url, headers, args.otlp_http_timeout)
        except (RuntimeError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 1
        suffix = f"; response bytes={len(response_body.encode('utf-8'))}"
        print(f"Sent {total} span(s) to OTLP HTTP traces endpoint {url} with status {status}{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
