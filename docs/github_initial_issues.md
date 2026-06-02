# GitHub Initial Issues

Create these issues after the first push. They are chosen to make the repository look active, useful, and contributor-friendly without distracting from the core FDE demo.

## Issue 1

Title:

```text
Add README demo GIF
```

Labels:

```text
documentation, good first issue
```

Body:

```text
Record a short GIF that shows:

1. Alice asking the remote-work question.
2. Alice being blocked from the finance plan.
3. Morgan receiving the finance answer.
4. The regulated operations agent creating an approval request.
5. Supervisor approval sending the notice.

Acceptance criteria:

- GIF is committed under docs/assets/.
- README embeds the GIF near the screenshots.
- python -B scripts/dev.py verify still passes.
```

## Issue 2

Title:

```text
Add CSV export for eval summaries
```

Labels:

```text
enhancement, good first issue
```

Body:

```text
Add an optional script that exports eval summaries to CSV for quick comparison across runs.

Acceptance criteria:

- New script lives under scripts/.
- CSV includes project, total cases, passed cases, pass rate, and unsafe failure counts.
- The script documents any eval runtime state writes and keeps generated artifacts ignored.
- python -B scripts/dev.py verify still passes.
```

## Issue 3

Title:

```text
Add OpenTelemetry-compatible trace export
```

Labels:

```text
enhancement, observability
```

Body:

```text
Add an export path that converts existing trace records into an OpenTelemetry-compatible JSON shape.

Acceptance criteria:

- Existing trace UI behavior remains unchanged.
- Export is deterministic and local-first.
- Documentation explains how this maps to a production trace backend.
- python -B scripts/dev.py verify still passes.
```

## Issue 4

Title:

```text
Add PostgreSQL and pgvector adapter design
```

Labels:

```text
design, production-upgrade
```

Body:

```text
Write a design note for replacing JSON state with PostgreSQL and pgvector.

Acceptance criteria:

- Covers schema, migrations, row-level security, indexing, and eval isolation.
- Explains how the permission boundary remains before model generation.
- Links back to ADR 0002 and ADR 0003.
```

## Issue 5

Title:

```text
Add replayable demo reset script
```

Labels:

```text
automation, demo
```

Body:

```text
Add a script that resets all demos, runs the expected business flows, and prints the exact trace IDs to inspect.

Acceptance criteria:

- Script runs from the repository root.
- It starts services if needed or fails with a clear message.
- It prints Project 1, Project 2, and Project 3 demo evidence.
- It prints trace IDs and approval IDs for inspection.
- python -B scripts/dev.py verify still passes.
```
