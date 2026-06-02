# Architecture

The AI Reliability Incident Console keeps the same local-first architecture as the rest of the repository:

```text
browser UI -> app.py HTTP shell -> ReliabilityApi -> triage/evals/storage modules -> JSON state
```

## Boundaries

- `app.py` owns HTTP routing and static file serving.
- `ReliabilityApi` maps HTTP endpoints to use cases.
- `triage.py` owns release-blocking decisions and remediation assembly.
- `evals.py` owns deterministic regression assertions.
- `storage.py` owns JSON runtime state, traces, and audit events.
- `web/js/*` owns first-party frontend orchestration and rendering.

## Invariant

Release rollout decisions are not model-text claims. They are deterministic decisions from incident severity, linked eval failures, and runbook evidence.
