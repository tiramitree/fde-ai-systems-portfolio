# Implementation Status

Implemented:

- local HTTP app
- modular backend API, triage, eval, and storage layers
- modular frontend JavaScript
- fictional release, incident, eval, runbook, trace, and audit data
- deterministic eval runner
- release-blocking triage flow

Not implemented:

- live production telemetry ingestion
- external incident-management connectors
- hosted observability backend
- model-backed root-cause summarization

Those are production upgrades. The current project is a runnable reference implementation for the release reliability control pattern.
# Threat Model

This project models release reliability decisions for AI systems. The data is fictional and local-first.

| Risk | Control |
| --- | --- |
| Unsafe release is widened after a high-risk eval failure | `triage.py` blocks open high-risk incidents with linked failed evals |
| Latency-only incident is overtreated as a safety rollback | eval category and incident category keep monitor-only behavior distinct |
| Incident decision cannot be explained later | each triage creates a trace and audit event |
| Public demo leaks private operational data | seed data is fictional and scanned by the public safety gate |
| Reviewer mistakes this for production monitoring | docs state this is a local reference implementation |
