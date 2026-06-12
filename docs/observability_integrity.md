# Observability Integrity Gate

Run:

```bash
python -B scripts/dev.py observability
python -B scripts/dev.py request-correlation
```

This gate starts the demo systems on isolated ports, resets local demo state, runs the critical technical review flows, and then checks the evidence surfaces that a reviewer would inspect after the fact.

Use `docs/trace_timeline_examples.md` for copyable local timelines that connect each canonical request to its response `trace_id`, persisted trace record, audit event, workflow-run checkpoint, approval queue entry, action-outbox dispatch record, action-run receipt, or release decision. `python -B scripts/dev.py request-correlation` separately proves that the governed `request_id` from `X-Request-ID` is carried through response payloads, persisted traces, and linked audit events for the three core business routes. Use `docs/opentelemetry_collector_handoff_troubleshooting.md` when local OTLP/JSON evidence needs an optional collector handoff without changing the default local proof path. Run `python -B scripts/dev.py otel-collector-handoff` to verify the OTLP/HTTP JSON POST path against a local collector stub.

## What It Proves

For Secure Enterprise Knowledge Copilot, the gate verifies:

- accessible HR-policy answers have a persisted trace, linked audit event, and request correlation evidence
- unauthorized finance queries abstain, record `permission_blocked_count`, and do not cite the confidential finance document
- authorized manager finance queries still cite the confidential document
- user-message prompt-injection attempts abstain and persist security-event evidence
- unauthorized trace and audit records do not include confidential document body or citation IDs

For Regulated Customer Operations Agent, the gate verifies:

- investigation flows persist tool calls, blocked side effects, approval-request evidence, and request correlation evidence
- approval-bypass attempts persist refusal evidence and do not create approval requests
- supervisor approval updates the approval queue, updates the sanitized workflow-run checkpoint, drains or fails a sanitized action-outbox dispatch item, records local worker lease ownership for each dispatch attempt, writes an action-run receipt only after the side effect applies, exposes retry/dead-letter evidence for failed dispatch, and emits audit events
- tool registry, dry-run preview, owner/expiry metadata, and approval rejection/expiry contracts are covered by the API and UI contract gates
- audit logs include workflow actions, refusal actions, and trace-linked processing events

For AI Reliability Incident Console, the gate verifies:

- unsafe canary incidents persist `block_release` trace, audit, and request correlation evidence
- latency-only incidents persist `monitor` trace and audit evidence
- failed eval cases remain linked to the unsafe release decision
- runbook IDs and incident signals are attached to release triage evidence
- each triage decision has exactly one linked audit event for its trace

## Technical Review Framing

The point is not just that the UI can show traces. The stronger claim is that traces, audit logs, workflow-run checkpoints, approval records, action-outbox records, action-run receipts, worker lease evidence, retry/dead-letter states, and release decisions are internally consistent with the business outcome.

If a technical reviewer asks "How would you debug an unsafe answer or unintended side effect?", the answer is:

1. Find the response `request_id` and `trace_id`.
2. Inspect retrieval/tool evidence in the trace and verify the trace carries the same `request_id`.
3. Inspect linked audit events for user, action, workflow-run, approval, action-outbox, action-run, release decision, and blocked-side-effect records.
4. Confirm the linked audit event carries the same `request_id`.
5. Re-run the observability and request-correlation gates to prove the evidence contract still holds after code changes.

## Production Upgrade Path

The local JSON store is intentionally simple. In production, the same evidence contract maps to:

- OpenTelemetry spans for request, retrieval, model, tool, and release-triage steps
- an OTLP/HTTP collector or hosted trace backend receiving the same persisted evidence in batches
- append-only audit/event tables
- approval workflow tables with idempotency keys
- transactional outbox tables with worker leases, attempts, payload hashes, and output refs
- release decision tables linked to eval run IDs and incident IDs
- redaction and retention policies
- trace search by user, case, document, approval, and incident

The local gate keeps the repository honest by proving the semantics before swapping in hosted observability infrastructure.
