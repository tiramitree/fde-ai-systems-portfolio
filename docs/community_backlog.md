# Community Backlog

This backlog is designed for public GitHub issues after launch. It keeps the repository open-source friendly without weakening the core demo.

## Good First Issues

1. Add a small dark-mode toggle to both demo UIs.
2. Add a copy trace ID button to each trace panel.
3. Add a screenshot refresh script for the README assets.
4. Add a tiny seed-data editor for local demos.
5. Add a copy-to-clipboard button for CSV eval summaries.

## Intermediate Issues

1. Add a hybrid BM25 + vector retrieval path behind a feature flag.
2. Add OpenTelemetry-compatible trace export.
3. Add per-case eval reports with failure diffs.
4. Add Docker Compose healthcheck documentation and screenshots.
5. Add a replayable demo script that resets and runs both project flows.

## Advanced Issues

1. Add PostgreSQL and pgvector storage adapters.
2. Add connector stubs for Google Drive, Slack, Jira, CRM, email, and calendar.
3. Add model-backed eval grading while keeping deterministic safety assertions.
4. Add a multi-tenant permission model with row-level policy examples.
5. Add a state-machine engine for governed operations workflows.

## Guardrails

Contributions should preserve these invariants:

- Project 1 must not expose inaccessible evidence to the model.
- Project 1 must abstain on unknown or unauthorized questions.
- Project 2 must not execute side-effect tools without application-level authorization.
- Project 2 must preserve supervisor approval behavior.
- Eval gates must keep unsafe leak and unsafe direct side-effect failures at zero.
