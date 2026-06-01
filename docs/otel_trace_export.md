# OpenTelemetry Trace Export

The local demos already record trace records for retrieval, governance decisions, tool calls, approvals, and blocked side effects. `scripts/export_traces_otel.py` converts those local records into an OTLP/JSON-compatible shape:

```text
resourceSpans
  -> resource attributes
  -> scopeSpans
  -> spans
  -> span attributes and events
```

The exporter is deterministic and local-first. It does not require an OpenTelemetry collector, network access, or an API key.

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
- `app.citation_count`
- `app.security_event_count`

Important events:

- `retrieval.completed`
- `evidence.cited`
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

## Production Path

In production, this local exporter would become one of two paths:

1. Native OpenTelemetry SDK instrumentation around API handlers, retrieval, model calls, tool calls, approval writes, and audit writes.
2. A batch bridge that converts persisted trace records into OTLP JSON and sends them to an OpenTelemetry Collector.

The production design should preserve the same invariants:

- permission checks happen before evidence reaches the model
- approval gates happen before external side effects
- blocked actions are observable events, not hidden failures
- trace IDs connect UI output, audit events, eval cases, and logs
- eval and demo traces are tagged separately from production traffic

## References

- OpenTelemetry Protocol File Exporter: https://opentelemetry.io/docs/specs/otel/protocol/file-exporter/
- OpenTelemetry Protocol Exporter: https://opentelemetry.io/docs/specs/otel/protocol/exporter/
