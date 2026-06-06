# Architecture Boundaries

This repository is designed to look simple during a demo while keeping the implementation boundaries inspectable.

The architecture boundary gate is:

```bash
python -B scripts/dev.py architecture
```

It checks that the three applications preserve the same separation of concerns that would be expected in a production service.

## Boundary Contract

Each project keeps four layers separate:

| Layer | Files | Contract |
| --- | --- | --- |
| HTTP and static shell | project `app.py` | Owns local HTTP routing, static file serving, JSON parsing, and response headers. It delegates application behavior to the API class. |
| API layer | `src/<package>/api.py` | Owns UI-facing use cases and response shapes. It is the backend boundary used by `app.py`. |
| Domain layer | `answering.py`, `retrieval.py`, `security.py`, `agent.py`, `tools.py` | Owns permission checks, evidence shaping, workflow decisions, deterministic tools, and approval gates. |
| Repository and state support | `repositories.py`, `storage.py`, `evals.py`, seed data | Owns application-facing storage interfaces, local deterministic state adapters, traces, audit logs, and regression evidence. |

The frontend stays in each project's `web/` directory and imports only local JavaScript modules from the same web boundary.

## What The Gate Prevents

The gate fails if:

- `app.py` starts importing domain modules directly instead of going through the API layer.
- backend modules import the sibling project's package.
- backend modules import frontend assets, docs, scripts, or `app.py`.
- non-API backend modules import the API layer.
- Project 1 application modules bypass `repositories.py` and import `storage.py` directly for JSON state.
- `storage.py` imports higher-level package modules instead of lower utility helpers such as chunking or time utilities.
- frontend JavaScript imports external modules, missing modules, non-JS modules, or files outside its `web/` boundary.
- required public symbols such as `CopilotApi`, `OpsAgentApi`, `generate_answer`, `process_message`, `request_approval`, and eval runners disappear.

## Technical Review Framing

The point is not to claim this local repository is a full production microservice platform. The point is to show production instincts:

- the browser is a thin client over stable API contracts
- local HTTP code is replaceable by FastAPI or another framework without rewriting domain logic
- local JSON storage is replaceable by PostgreSQL adapters behind repository interfaces
- permissions and side effects live in deterministic backend modules, not in prompts
- eval and smoke gates prove critical behavior after refactors
- public PRs cannot quietly collapse the architecture into a hard-to-review script

In a production upgrade, the same boundaries would map cleanly to service routers, dependency injection, persistent storage adapters, hosted observability, and authenticated enterprise connectors.
