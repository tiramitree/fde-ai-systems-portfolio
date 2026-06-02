# AI Reliability Incident Console

Local-first demo for AI release reliability, eval regression triage, incident evidence, audit logs, and blocked rollout decisions.

Run:

```bash
python -B app.py --reset --port 8780
```

Open:

```text
http://127.0.0.1:8780
```

## What It Demonstrates

- release and canary monitoring for AI applications
- eval failures connected to incidents
- deterministic triage decisions before widening rollout
- remediation plans linked to failed evals and runbooks
- trace and audit records for incident decisions

## Demo Flow

1. Select `rel-2026-06-01`.
2. Select `inc-2026-014`.
3. Run triage.
4. Show that the release is blocked because unauthorized-answer and citation evals failed.
5. Switch to `inc-2026-015`.
6. Run triage and show monitor-only behavior for a latency-only incident.
7. Run triage evals.

## Technical Review Framing

This project covers what happens after an AI feature is shipped. Companion systems cover secure RAG and governed agent actions; this system covers the operational layer: canary releases, eval regressions, incident triage, rollout blocking, traces, audit logs, and remediation.
