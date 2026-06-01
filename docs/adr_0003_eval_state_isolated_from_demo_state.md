# ADR 0003: Eval State Isolated From Demo State

Status: accepted

## Context

The services write runtime traces, audits, and eval results. Repeated evals and smoke tests should not corrupt or destabilize the interactive demo.

## Decision

CLI eval scripts use separate eval runtime state files instead of the live demo runtime state.

The JSON store also uses a process-level lock and recovers from malformed state by reseeding.

## Consequences

Benefits:

- repeated quality gates are stable
- demo UI remains usable after evals
- GitHub Actions can run verification without polluting interactive state

Tradeoffs:

- local state is still not a production concurrency solution
- production should use a real database and transactions

## Interview Explanation

This was an actual reliability issue found during testing. The fix demonstrates why eval infrastructure should be isolated and repeatable.

