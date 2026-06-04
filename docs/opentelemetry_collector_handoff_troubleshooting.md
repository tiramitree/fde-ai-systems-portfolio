# OpenTelemetry Collector Handoff Troubleshooting

Use this page when a local `otel_traces.json` export needs to be handed to an OpenTelemetry Collector workflow for review or a production-adapter prototype. Read it with `docs/otel_trace_export.md`, `docs/observability_integrity.md`, and `docs/command_output_troubleshooting_map.md`.

This page does not make a hosted collector part of the default demo path. The default proof remains local and deterministic:

```bash
python -B scripts/dev.py replay
python -B scripts/dev.py otel-traces
python -B scripts/dev.py observability
```

The exporter writes `otel_traces.json`, which is generated local evidence and ignored by git.

## Handoff Boundary

The current repository proves that local trace records can be converted into an OTLP/JSON-compatible `resourceSpans` payload. A collector handoff should preserve that boundary:

- local demos still run without Docker, hosted collectors, external accounts, paid-service requirements, or network access
- `scripts/export_traces_otel.py` remains the local exporter
- collector endpoints are optional environment configuration, not checked-in source defaults
- generated collector logs, local trace IDs, and environment dumps stay out of commits
- permission, approval, and release-blocking semantics remain proven by `python -B scripts/dev.py observability`

## Local Export Check

Start with the local path before touching a collector:

```bash
python -B scripts/dev.py replay
python -B scripts/dev.py otel-traces
```

Expected result:

```text
Wrote 13 span(s) across 3/3 project(s) to .../otel_traces.json
```

If this fails, do not debug a collector yet. Inspect:

- `scripts/export_traces_otel.py`
- `docs/otel_trace_export.md`
- `docs/command_output_troubleshooting_map.md`
- recently changed trace, audit, approval, release, or eval files

Then rerun:

```bash
python -B scripts/dev.py observability
python -B scripts/dev.py otel-traces
```

## Collector Endpoint Notes

When a prototype sends the payload to a collector, keep endpoint configuration outside checked-in source. Common local examples are:

```text
OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4318
OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=http://127.0.0.1:4318/v1/traces
```

Review rules:

- do not commit real collector URLs, tenant IDs, API keys, bearer tokens, private hostnames, or local machine paths
- do not make these variables required for `python -B scripts/dev.py quality`
- do not replace local replay, local trace export, or observability gates with hosted collector checks
- document the collector as optional handoff evidence unless a dedicated live exporter issue adds and tests the path

## Failure Modes

| Symptom | Likely Cause | Safe First Fix |
| --- | --- | --- |
| `otel_traces.json` is missing | `replay` or `otel-traces` was not run, or generated artifacts were cleaned. | Run `python -B scripts/dev.py replay`, then `python -B scripts/dev.py otel-traces`. |
| `resourceSpans` is empty | Runtime state was reset without rerunning canonical flows. | Run `python -B scripts/dev.py replay` and inspect `docs/otel_trace_export.md`. |
| Collector rejects payload | Endpoint path, protocol, or collector receiver config does not match the payload. | Keep the failure local, record only generic endpoint shape, and verify `otel_traces.json` first. |
| Collector is unreachable | Collector is not running, port is wrong, or Docker/network setup is unavailable. | Fall back to local JSON export and do not mark hosted collector evidence complete. |
| Spans arrive without useful attributes | Adapter dropped app-specific attributes or events. | Compare with the mapping in `docs/otel_trace_export.md`; rerun `python -B scripts/dev.py observability`. |
| Public docs claim hosted observability is configured | README or launch copy drifted beyond verified evidence. | Narrow the wording and run `python -B scripts/dev.py launch-assets` plus `python -B scripts/dev.py safety`. |

## Rollback

If collector handoff work breaks local verification:

```bash
python -B scripts/dev.py observability
python -B scripts/dev.py otel-traces
python -B scripts/dev.py safety
```

Rollback rules:

- keep the local exporter and `otel_traces.json` path working first
- remove required collector environment variables from default commands
- move hosted collector proof back to manual or optional status
- leave any failed collector evidence out of public claims until the dedicated command passes
- keep generated runtime files and collector logs untracked

## Review Checklist

Before approving collector handoff documentation:

```bash
git diff --stat
git diff -- README.md PROJECT_CONTENT_INDEX.md docs/ scripts/
git diff --check
python -B scripts/dev.py observability
python -B scripts/dev.py otel-traces
python -B scripts/dev.py assets
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Use `docs/readme_navigation_drift_examples.md` if README wording claims hosted collector support too early. Use `docs/docs_only_review_comment_examples.md` for approve, request-changes, close-as-unsafe, or close-as-low-signal comments.

## Claim Wording

Good:

```text
Local traces export to an OTLP/JSON-compatible payload. Collector handoff remains an optional production-adapter path.
```

Avoid:

```text
The repository ships hosted OpenTelemetry Collector integration by default.
```

Do not claim live collector verification until a dedicated command or documented manual proof has passed in the target environment.
