# Observability Integrity Gate

Run:

```bash
python -B scripts/dev.py observability
```

This gate starts both demo systems on isolated ports, resets local demo state, runs the critical technical review flows, and then checks the evidence surfaces that a reviewer would inspect after the fact.

## What It Proves

For Secure Enterprise Knowledge Copilot, the gate verifies:

- accessible HR-policy answers have a persisted trace and linked audit event
- unauthorized finance queries abstain, record `permission_blocked_count`, and do not cite the confidential finance document
- authorized manager finance queries still cite the confidential document
- user-message prompt-injection attempts abstain and persist security-event evidence
- unauthorized trace and audit records do not include confidential document body or citation IDs

For Regulated Customer Operations Agent, the gate verifies:

- investigation flows persist tool calls, blocked side effects, and approval-request evidence
- approval-bypass attempts persist refusal evidence and do not create approval requests
- supervisor approval updates the approval queue and emits an audit event
- audit logs include workflow actions, refusal actions, and trace-linked processing events

## Technical Review Framing

The point is not just that the UI can show traces. The stronger claim is that traces, audit logs, and approval records are internally consistent with the business outcome.

If an technical reviewer asks "How would you debug an unsafe answer or unintended side effect?", the answer is:

1. Find the response `trace_id`.
2. Inspect retrieval/tool evidence in the trace.
3. Inspect linked audit events for user, action, approval, and blocked-side-effect records.
4. Re-run the observability gate to prove the evidence contract still holds after code changes.

## Production Upgrade Path

The local JSON store is intentionally simple. In production, the same evidence contract maps to:

- OpenTelemetry spans for request, retrieval, model, and tool steps
- append-only audit/event tables
- approval workflow tables with idempotency keys
- redaction and retention policies
- trace search by user, case, document, approval, and incident

The local gate keeps the repository honest by proving the semantics before swapping in hosted observability infrastructure.
