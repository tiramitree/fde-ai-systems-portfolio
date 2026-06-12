# ADR 0004: Verification Runtime State Isolation

Status: accepted

## Context

Several verification scripts start all three local services and then create traces, audit events, approvals, workflow runs, action outbox records, and replay evidence. When those scripts share the default `*/data/runtime_state.json` files, parallel local checks can interfere with each other and leave stale demo evidence behind.

## Decision

Each HTTP app accepts `--state-path` for local JSON runtime state isolation. Self-starting verification commands that do not need canonical demo state pass a temporary state path per service.

The default `app.py --reset --port ...` path is still preserved for interactive demos, trace export from canonical local state, and documentation flows that intentionally read `*/data/runtime_state.json`.

## Consequences

Benefits:

- API, UI, observability, visual capture, replay artifact, and opt-in isolated replay checks can run without mutating canonical demo state
- ad hoc parallel verification is less likely to produce false failures
- generated trace, approval, and outbox ids stay scoped to the command that created them

Tradeoffs:

- local JSON state remains a demo/testing persistence layer, not a production concurrency design
- commands that intentionally export canonical traces must keep using the default runtime state files

## Design Review Explanation

This was a real local reliability issue: independent gates could pass alone but contaminate one another when run together. The fix keeps the local demo simple while making verification behavior closer to production-grade test isolation.
