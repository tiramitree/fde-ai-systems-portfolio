# GitHub Community Issue Pack

Use this file to seed contributor-friendly GitHub issues after a release. The issue list should reflect real engineering work that would make the repository more useful, easier to run, or easier to adapt. Do not create placeholder issues only for activity metrics.

## Wave 1 Completed Issues

The first public issue wave was created after the initial release and is now complete:

- Add README demo GIF
- Add CSV export for eval summaries
- Add OpenTelemetry-compatible trace export
- Add PostgreSQL and pgvector adapter design
- Add replayable demo reset script

Keep this record so future maintainers understand why those capabilities already exist in the repository.

## Issue 1

Title:

```text
Add a FastAPI adapter for one service
```

Labels:

```text
enhancement, production-upgrade
```

Body:

```text
Add a FastAPI adapter for one existing service while keeping the current stdlib HTTP server as the default local path.

Acceptance criteria:

- Adapter lives behind a separate entrypoint or documented optional path.
- Existing API response shapes remain compatible with docs/api_contracts.md.
- The default local demo path still runs without third-party dependencies.
- Update docs/production_upgrade_notes.md with the adapter boundary.
- python -B scripts/dev.py contracts still passes.
- python -B scripts/dev.py verify still passes.
```

## Issue 2

Title:

```text
Implement a PostgreSQL storage adapter prototype
```

Labels:

```text
enhancement, production-upgrade
```

Body:

```text
Prototype a PostgreSQL-backed storage adapter for one service based on docs/postgres_pgvector_adapter_design.md.

Acceptance criteria:

- Local JSON storage remains the default.
- Adapter has a clear feature flag or separate entrypoint.
- Migration/schema notes include audit log, trace, and eval-state isolation.
- Permission checks remain before answer generation or side-effect execution.
- Add focused tests or a deterministic check script for adapter shape.
- python -B scripts/dev.py quality still passes.
```

## Issue 3

Title:

```text
Add per-case eval regression reports
```

Labels:

```text
enhancement, evals
```

Body:

```text
Add a report that compares current eval results with a checked-in baseline and highlights changed cases.

Acceptance criteria:

- Report includes project, case id, pass/fail transition, latency, and unsafe failure counts.
- Generated report artifacts stay ignored unless intentionally committed as release evidence.
- The report does not weaken deterministic safety assertions.
- Documentation explains when to use the report during release review.
- python -B scripts/dev.py evals still passes.
- python -B scripts/dev.py claims still passes.
```

## Issue 4

Title:

```text
Add red-team eval cases for retrieval and agent governance
```

Labels:

```text
security, evals
```

Body:

```text
Expand the eval suite with additional prompt-injection, unauthorized-access, and approval-bypass cases.

Acceptance criteria:

- Project 1 adds retrieval or user-message attack cases that must abstain without leaking inaccessible evidence.
- Project 2 adds approval-bypass cases that must not execute side effects.
- Project 3 adds at least one release-risk case that must block rollout.
- Update docs/threat_model.md or project threat docs if new threat patterns are introduced.
- Unsafe leak, direct side-effect, and release approval failure counts remain zero.
- python -B scripts/dev.py quality still passes.
```

## Issue 5

Title:

```text
Add trace deep links in the demo UI
```

Labels:

```text
enhancement, frontend, observability
```

Body:

```text
Make it easier to inspect a specific trace from the browser demo.

Acceptance criteria:

- Trace IDs in responses can be copied or opened as a local deep link.
- Existing trace-copy controls keep working.
- Frontend modules remain local to each service web boundary.
- Runtime UI contracts are updated if routes or anchors change.
- python -B scripts/dev.py frontend still passes.
- python -B scripts/dev.py ui-contracts still passes.
```

## Issue 6

Title:

```text
Run and document Docker Compose runtime verification
```

Labels:

```text
documentation, docker, release
```

Body:

```text
Run the Docker runtime verification on a Docker-enabled machine and publish the evidence.

Acceptance criteria:

- Run python -B scripts/dev.py docker-runtime on a Docker-enabled machine.
- Record the exact environment and result in docs/container_release_hygiene.md.
- Add screenshots only if they reflect the current running services.
- Do not claim Docker runtime verification until the command passes.
- python -B scripts/dev.py container-release still passes.
```

## Guardrails

- Do not create issues that ask for secrets, tokens, private files, or account access.
- Do not create issues that weaken permission checks, approval gates, evals, traces, or public safety scans.
- Keep local-first behavior intact unless an issue explicitly adds an optional production adapter.
- Every issue should include acceptance criteria and at least one verification command.
