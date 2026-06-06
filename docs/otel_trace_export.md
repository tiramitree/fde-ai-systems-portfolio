# OpenTelemetry Trace Export

The local demos already record trace records for retrieval, governance decisions, tool calls, approvals, blocked side effects, eval regressions, and release triage decisions. `scripts/export_traces_otel.py` converts those local records into an OTLP/JSON-compatible shape:

```text
resourceSpans
  -> resource attributes
  -> scopeSpans
  -> spans
  -> span attributes and events
```

The exporter is deterministic and local-first. It does not require an OpenTelemetry collector, network access, or an API key for the default path. When a collector is available, the same script can optionally POST OTLP/HTTP JSON to a traces endpoint without adding runtime dependencies. For collector handoff notes, see `docs/opentelemetry_collector_handoff_troubleshooting.md`.

## Command

Generate fresh trace evidence, then export:

```bash
python -B scripts/dev.py replay
python -B scripts/dev.py otel-traces
```

Default output:

```text
otel_traces.json
```

That file is generated output and ignored by git.

Validate the optional collector handoff path without a real collector:

```bash
python -B scripts/dev.py otel-collector-handoff
```

Send the generated payload to a local OTLP HTTP collector:

```bash
python -B scripts/dev.py replay
python -B scripts/export_traces_otel.py --send-otlp-http --otlp-http-endpoint http://127.0.0.1:4318
```

The exporter appends `/v1/traces` to `--otlp-http-endpoint`, matching the OTLP/HTTP traces path. If `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` or `--otlp-http-traces-endpoint` is provided, that signal-specific endpoint is used as-is. This handoff intentionally uses OTLP/HTTP JSON; if `OTEL_EXPORTER_OTLP_PROTOCOL` is set, use `http/json`.

## Mapping

Project 1 traces become `copilot.query` spans.

Important attributes:

- `app.project`
- `app.trace_type`
- `app.user_id`
- `app.question`
- `app.abstained`
- `app.abstain_reason`
- `app.model_provider`
- `app.retrieval.hit_count`
- `app.permission_blocked_count`
- `app.source_lifecycle_policy`
- `app.stale_filtered_count`
- `app.citation_count`
- `app.security_event_count`

Important events:

- `retrieval.completed`
- `evidence.cited`, including citation chunk source-span line metadata and sentence-level `evidence_span_count`
- `evidence.sentence_span`, including the cited answer-support sentence and its parser-normalized source-span line metadata
- `security.event`

Project 2 traces become `ops_agent.process_message` spans.

Important attributes:

- `app.project`
- `app.trace_type`
- `app.user_id`
- `app.message`
- `app.intent`
- `app.model_router`
- `app.tool_call_count`
- `app.approval_count`
- `app.blocked_action_count`
- `app.cited_policy_count`

Important events:

- `tool.call`
- `approval.requested`
- `governance.blocked_action`
- `policy.cited`

Project 3 traces become `reliability.release_triage` spans.

Important attributes:

- `app.project`
- `app.trace_type`
- `app.user_id`
- `app.release_id`
- `app.release_status`
- `app.release_traffic_percent`
- `app.incident_id`
- `app.incident_status`
- `app.incident_severity`
- `app.incident_category`
- `app.eval_run_id`
- `app.failed_eval_count`
- `app.recommendation`
- `app.release_blocked`
- `app.runbook_count`
- `app.signal_count`
- `app.audit_event_count`

Important events:

- `release.triage_decision`
- `release.context`
- `release.rollout_blocked`
- `release.rollout_monitored`
- `incident.signal`
- `eval.failure.linked`
- `runbook.linked`
- `audit.linked`

## Production Path

In production, this local exporter would become one of three paths:

1. Native OpenTelemetry SDK instrumentation around API handlers, retrieval, model calls, tool calls, approval writes, release decisions, eval gates, and audit writes.
2. A batch bridge that converts persisted trace records into OTLP JSON and sends them to an OpenTelemetry Collector.
3. A backend-specific exporter adapter for hosted observability platforms when they require authentication, tenancy headers, or vendor-specific ingest URLs.

The production design should preserve the same invariants:

- permission checks happen before evidence reaches the model
- approval gates happen before external side effects
- blocked actions are observable events, not hidden failures
- release rollout decisions link incidents, failed eval cases, runbooks, and audit events
- trace IDs connect UI output, audit events, eval cases, and logs
- eval and demo traces are tagged separately from production traffic

## References

- OpenTelemetry Protocol File Exporter: https://opentelemetry.io/docs/specs/otel/protocol/file-exporter/
- OpenTelemetry Protocol Exporter: https://opentelemetry.io/docs/specs/otel/protocol/exporter/
- OTLP Specification: https://opentelemetry.io/docs/specs/otlp/
