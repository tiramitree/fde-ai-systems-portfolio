# ADR 0002: The Model Is Not The Security Boundary

Status: accepted

## Context

LLM applications are often designed as if the model can be instructed to obey permissions or avoid unsafe actions. That is not sufficient for enterprise systems.

## Decision

Security and governance controls live in deterministic application logic:

- Project 1 filters documents before model generation.
- Project 1 removes unsafe retrieved instructions before answer assembly.
- Project 2 blocks side-effect actions unless approval exists.
- Project 2 allows supervisor-only approval for external actions.

The optional model gateway can improve language quality or routing, but it cannot bypass these controls.

## Consequences

Benefits:

- permissions are testable
- side-effect controls are auditable
- evals can catch regressions
- technical review explanation is defensible

Tradeoffs:

- more application code than a pure prompt demo
- model autonomy is intentionally constrained
- production systems still need stronger policy engines and auth providers

## Design Review Explanation

The model can reason, draft, and classify. It should not decide whether confidential evidence is visible or whether an external notice can be sent.

