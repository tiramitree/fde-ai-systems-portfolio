# GitHub Community Issue Pack

Use this file to seed contributor-friendly GitHub issues after a release. The issue list should reflect real engineering work that would make the repository more useful, easier to run, or easier to adapt. Do not create placeholder issues only for activity metrics.

## Wave 1 Completed Issues

The first public issue wave was created after the initial release and is now complete:

- Add README demo GIF
- Add CSV export for eval summaries
- Add OpenTelemetry-compatible trace export
- Add PostgreSQL and pgvector adapter design
- Add replayable demo reset script
- Add trace deep links in the demo UI
- Add a local seed-data editor prototype
- Add keyboard-friendly trace navigation for recent trace lists
- Add copyable scenario-draft import/export snippets for local demos
- Add a compact diff view for browser-local scenario drafts
- Add a reduced-motion and focus-visible accessibility pass
- Add browser-local light/dark theme controls to all demo UIs
- Add high-contrast screenshot checks for visual assets
- Add mobile viewport screenshots to the visual asset manifest
- Add compact visual asset diff summaries for screenshot refreshes
- Add visual asset refresh troubleshooting notes
- Add per-asset captions for screenshot galleries
- Add a README command quick-reference
- Add a compact README glossary for core gates
- Add a README maintainer workflow checklist
- Add a compact README demo path map
- Add README command output expectations
- Add a compact README troubleshooting pointer
- Add a compact README screenshot reviewer checklist
- Add a compact README command decision tree
- Add a compact README evidence legend
- Add a compact README contributor route map
- Add a compact README production-upgrade pointer
- Add a compact README release-evidence FAQ
- Add compact per-project risk badges
- Add a compact README operational runbook index
- Add a compact README evidence freshness checklist
- Add a compact README reviewer handoff checklist
- Add compact per-project architecture cards to the README
- Add shareable demo-state reset presets
- Add a compact README demo recording checklist pointer
- Add a compact README launch-channel checklist pointer
- Add a compact README contribution safety summary pointer
- Add a compact README release artifact attachment pointer
- Add a compact README optional-environment evidence pointer
- Add a compact README connector roadmap pointer
- Add a compact README eval regression report pointer
- Add a compact README storage adapter evidence pointer
- Add a compact README red-team eval expansion pointer
- Add a compact README OpenTelemetry backend pointer
- Add a compact README Docker runtime evidence pointer
- Add a compact README dependency surface evidence pointer
- Add a compact README API contract evidence pointer
- Add a compact README error hygiene evidence pointer
- Add a compact README model gateway safety evidence pointer

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
enhancement, eval
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
security, eval
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
Add a compact README PR triage evidence pointer
```

Labels:

```text
documentation, security, good first issue
```

Body:

```text
Add a compact README pointer that tells contributors where PR triage materials live and which public-contribution review boundaries must be preserved before approving workflows, running contributor code, or merging.

Acceptance criteria:

- Link to PR Review Security, PR Review Runbook, Maintainer PR Checklist, Development Issue Solutions, and the public PR triage row in the Evidence Matrix.
- Cover PR review checks: `python -B scripts/dev.py pr-triage`, `python -B scripts/dev.py pr-policy`, `python -B scripts/dev.py safety`, and `python -B scripts/dev.py quality`.
- Keep the pointer compact and local-first; do not require external accounts, paid APIs, private files, or secrets.
- Make clear that public PRs are treated as untrusted input, changed files and diffs are reviewed before running contributor code, and high-risk workflow, dependency, model gateway, safety, eval, binary, network, shell, or environment changes require extra scrutiny.
- python -B scripts/dev.py assets still passes.
- python -B scripts/dev.py pr-policy still passes.
- python -B scripts/dev.py quality still passes.
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

- Do not create issues that require secret values, token values, private files, or account access.
- Do not create issues that weaken permission checks, approval gates, evals, traces, or public safety scans.
- Keep local-first behavior intact unless an issue explicitly adds an optional production adapter.
- Every issue should include acceptance criteria and at least one verification command.
