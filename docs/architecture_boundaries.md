# Architecture Boundaries

This repository is designed to look simple during a demo while keeping the implementation boundaries inspectable.

The architecture boundary gate is:

```bash
python -B scripts/dev.py architecture
```

It checks that the two portfolio applications preserve the same separation of concerns that would be expected in a production service.

## Boundary Contract

Each project keeps four layers separate:

| Layer | Files | Contract |
| --- | --- | --- |
| HTTP and static shell | project `app.py` | Owns local HTTP routing, static file serving, JSON parsing, and response headers. It delegates application behavior to the API class. |
| API layer | `src/<package>/api.py` | Owns UI-facing use cases and response shapes. It is the backend boundary used by `app.py`. |
| Domain layer | `answering.py`, `retrieval.py`, `security.py`, `agent.py`, `tools.py` | Owns permission checks, evidence shaping, workflow decisions, deterministic tools, and approval gates. |
| State and eval support | `storage.py`, `evals.py`, seed data | Owns local deterministic state, traces, audit logs, and regression evidence. |

The frontend stays in each project's `web/` directory and imports only local JavaScript modules from the same web boundary.

## What The Gate Prevents

The gate fails if:

- `app.py` starts importing domain modules directly instead of going through the API layer.
- backend modules import the sibling project's package.
- backend modules import frontend assets, docs, scripts, or `app.py`.
- non-API backend modules import the API layer.
- `storage.py` imports higher-level package modules.
- frontend JavaScript imports external modules, missing modules, non-JS modules, or files outside its `web/` boundary.
- required public symbols such as `CopilotApi`, `OpsAgentApi`, `generate_answer`, `process_message`, `request_approval`, and eval runners disappear.

## Interview Framing

The point is not to claim this local portfolio is a full production microservice platform. The point is to show production instincts:

- the browser is a thin client over stable API contracts
- local HTTP code is replaceable by FastAPI or another framework without rewriting domain logic
- permissions and side effects live in deterministic backend modules, not in prompts
- eval and smoke gates prove critical behavior after refactors
- public PRs cannot quietly collapse the architecture into a hard-to-review script

In a production upgrade, the same boundaries would map cleanly to service routers, dependency injection, persistent storage adapters, hosted observability, and authenticated enterprise connectors.
