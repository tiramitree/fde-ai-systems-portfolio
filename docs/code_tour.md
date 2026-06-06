# Contributor Code Tour

This tour maps the repository from local HTTP entry points to backend boundaries, state, evals, and frontend modules. It is source-linked and local-first: no generated runtime files, external accounts, paid services, secrets, or private paths are required.

Use this page with `docs/architecture_boundaries.md` for the boundary contract and `docs/api_contracts.md` for route-level response shapes.

## Shared Boundary Map

| Boundary | Source | Owns | Does Not Own |
| --- | --- | --- | --- |
| HTTP and static shell | project `app.py` | Local HTTP routing, static files, JSON parsing, security headers, generic JSON errors, reset-state startup. | Domain decisions, permission policy, side effects, eval assertions, frontend rendering. |
| API layer | `src/<package>/api.py` | UI-facing use cases, route dispatch, response shape assembly, `ApiError` status mapping. | Low-level storage mutation details, frontend DOM behavior, direct sibling-project imports. |
| Domain/service logic | `answering.py`, `retrieval.py`, `security.py`, `agent.py`, `tools.py`, `triage.py`, optional `model_gateway.py` | Permission filtering, evidence shaping, deterministic workflow decisions, tool governance, release-blocking logic, optional model calls behind local fallback. | Raw HTTP parsing, static files, generated artifacts. |
| Repository and state support | `repositories.py`, `postgres_repositories.py`, `storage.py`, `evals.py`, `data/*.json`, project `scripts/run_eval.py` | Application-facing repository interfaces, local JSON adapter details, production-path PostgreSQL adapter contract, fictional seed data, traces, audit logs, approvals, eval runs, regression assertions. | Browser layout, prompts as authorization boundaries, or direct external persistence calls from domain modules. |
| Frontend boundary | project `web/index.html`, `web/styles.css`, `web/js/*.js` | Local ES-module UI, HTTP client calls, rendering, trace links, clipboard actions, scenario draft editing, theme state. | Backend policy, authorization, side-effect execution. |

The same shape appears in all three projects so a contributor can learn one flow and apply it across the portfolio.

Shared observability scripts:

- `scripts/export_traces_otel.py`: converts persisted local trace records into OTLP/JSON `resourceSpans`, writes `otel_traces.json`, and can optionally POST the same payload to an OTLP/HTTP traces endpoint.
- `scripts/check_otel_collector_handoff.py`: verifies the optional collector handoff path with a local in-process collector stub, including endpoint construction, content type, user agent, header precedence, and payload shape.

## Project 1: Secure Enterprise Knowledge Copilot

Primary path:

```text
secure-enterprise-knowledge-copilot/app.py
  -> src/copilot/api.py: CopilotApi
  -> src/copilot/repositories.py
  -> src/copilot/postgres_repositories.py
  -> src/copilot/source_parsing.py
  -> src/copilot/embeddings.py
  -> src/copilot/retrieval.py
  -> src/copilot/retrieval_scoring.py
  -> src/copilot/reranking.py
  -> src/copilot/security.py
  -> src/copilot/answering.py
  -> src/copilot/model_gateway.py
  -> src/copilot/chunking.py
  -> src/copilot/storage.py
  -> src/copilot/evals.py
  -> web/js/*.js
```

Key files:

- `secure-enterprise-knowledge-copilot/app.py`: stdlib HTTP server and static shell. It imports only `copilot.api` and `copilot.storage` from the backend package.
- `secure-enterprise-knowledge-copilot/src/copilot/api.py`: `CopilotApi` maps browser/API requests to users, visible documents, query handling, traces, audit, scenario snapshots, and eval runs.
- `secure-enterprise-knowledge-copilot/src/copilot/repositories.py`: `KnowledgeRepository`, `JsonKnowledgeRepository`, `PostgresRepositorySession`, and `connect_repository` define the application-facing storage adapter boundary used by API, retrieval, answering, ingestion, and eval logic; `COPILOT_REPOSITORY=postgres`, `COPILOT_POSTGRES_DSN`, and optional `COPILOT_POSTGRES_POOL` keep the production data-plane path opt-in.
- `secure-enterprise-knowledge-copilot/src/copilot/source_parsing.py`: parser boundary for admin-ingested plain text, Markdown, CSV, HTML, and JSON sources. It returns normalized searchable text plus parser metadata and warnings so ingestion can audit the data-plane step without mixing parser rules into authorization logic.
- `secure-enterprise-knowledge-copilot/src/copilot/embeddings.py`: local deterministic embedding boundary for seed and ingestion chunks. It gives the pgvector path a concrete vector payload and retrieval profile today while staying replaceable by a production embedding model later.
- `secure-enterprise-knowledge-copilot/src/copilot/retrieval.py`: asks the repository for retrieval candidates, applies shared scoring and security checks, and asks for `count_potentially_blocked_chunks` so JSON can count denied local evidence directly while PostgreSQL can preserve RLS and use `project1_denied_relevant_chunk_count` without exposing unauthorized content.
- `secure-enterprise-knowledge-copilot/src/copilot/postgres_repositories.py`: optional production-path `PostgresKnowledgeRepository` contract over the PostgreSQL/pgvector schema. It keeps tenant context, document/chunk writes, traces, audit events, eval runs, denied-evidence counts, and SQL-backed keyword/vector candidate selection behind the same repository shape without making PostgreSQL required for the local demo.
- `secure-enterprise-knowledge-copilot/src/copilot/retrieval_scoring.py`: local hybrid retrieval scoring profile with lexical, title, phrase, semantic-family, and vector components. It makes retrieval quality inspectable now and leaves a clean handoff point for later production embedding and reranker work.
- `secure-enterprise-knowledge-copilot/src/copilot/reranking.py`: deterministic evidence reranker boundary after first-stage retrieval. It records feature-level rerank evidence today and gives a clean replacement point for a production reranker later.
- `secure-enterprise-knowledge-copilot/src/copilot/security.py`: prompt-injection detection and evidence sanitization.
- `secure-enterprise-knowledge-copilot/src/copilot/answering.py`: answer, citation, confidence, missing-evidence, and abstention behavior.
- `secure-enterprise-knowledge-copilot/src/copilot/chunking.py`: shared deterministic text chunking used by JSON seeding and admin ingestion after parser normalization; `chunk_text_with_spans` records source spans over normalized text so citations and traces can point back to exact chunk ranges.
- `secure-enterprise-knowledge-copilot/src/copilot/model_gateway.py`: optional OpenAI structured-output path with local fallback as the default.
- `secure-enterprise-knowledge-copilot/src/copilot/storage.py`: local JSON state mechanics and seed/reset support; application modules should go through `repositories.py`.
- `secure-enterprise-knowledge-copilot/src/copilot/evals.py`: retrieval, citation, abstention, and leak-prevention regression cases.
- `secure-enterprise-knowledge-copilot/web/js/api.js`: browser HTTP client.
- `secure-enterprise-knowledge-copilot/web/js/app.js`: screen orchestration.
- `secure-enterprise-knowledge-copilot/web/js/renderers.js`: response, document, trace, and audit rendering.
- `secure-enterprise-knowledge-copilot/web/js/scenarioEditor.js`: browser-local scenario draft and diff controls.
- `secure-enterprise-knowledge-copilot/web/js/traceLinks.js`: trace deep links and keyboard navigation.

Safe change paths:

- Permission or evidence behavior: update `retrieval.py`, `security.py`, `answering.py`, repository methods when persistence behavior changes, seed/eval cases, and `docs/api_contracts.md` when response shape changes.
- Optional model behavior: keep `model_gateway.py` opt-in, preserve local fallback, and run `python -B scripts/dev.py model-gateway-safety`.
- UI behavior: keep `web/js/api.js` as the only fetch helper and run frontend and UI contract gates.

## Project 2: Regulated Customer Operations Agent

Primary path:

```text
regulated-customer-operations-agent/app.py
  -> src/ops_agent/api.py: OpsAgentApi
  -> src/ops_agent/agent.py
  -> src/ops_agent/tools.py
  -> src/ops_agent/model_gateway.py
  -> src/ops_agent/storage.py
  -> src/ops_agent/evals.py
  -> web/js/*.js
```

Key files:

- `regulated-customer-operations-agent/app.py`: HTTP/static shell that delegates application behavior to `OpsAgentApi`.
- `regulated-customer-operations-agent/src/ops_agent/api.py`: `OpsAgentApi` maps requests to case lookup, agent messages, approval execution, trace/audit views, scenario snapshots, and eval runs.
- `regulated-customer-operations-agent/src/ops_agent/agent.py`: intent classification and workflow orchestration.
- `regulated-customer-operations-agent/src/ops_agent/tools.py`: deterministic tools, side-effect blocking, approval requests, idempotency, notice send, escalation, and supervisor approval.
- `regulated-customer-operations-agent/src/ops_agent/model_gateway.py`: optional model routing with deterministic fallback.
- `regulated-customer-operations-agent/src/ops_agent/storage.py`: JSON state, users, cases, listings, approvals, traces, and audit events.
- `regulated-customer-operations-agent/src/ops_agent/evals.py`: approval, bypass-refusal, escalation, and side-effect regression cases.
- `regulated-customer-operations-agent/web/js/api.js`: browser HTTP client.
- `regulated-customer-operations-agent/web/js/app.js`: case workspace orchestration.
- `regulated-customer-operations-agent/web/js/renderers.js`: tool call, approval, blocked-action, trace, and audit rendering.
- `regulated-customer-operations-agent/web/js/scenarioEditor.js`: browser-local scenario draft and diff controls.
- `regulated-customer-operations-agent/web/js/traceLinks.js`: trace deep links and keyboard navigation.

Safe change paths:

- Tool or governance behavior: update `agent.py`, `tools.py`, seed/eval cases, API contracts, and smoke/eval expectations together.
- New side-effect connector: keep execution behind approval, idempotency, audit, and trace boundaries; do not execute directly from model text.
- UI behavior: keep side-effect status inspectable through approvals, blocked actions, and audit traces.

## Project 3: AI Reliability Incident Console

Primary path:

```text
ai-reliability-incident-console/app.py
  -> src/reliability_console/api.py: ReliabilityApi
  -> src/reliability_console/triage.py
  -> src/reliability_console/storage.py
  -> src/reliability_console/evals.py
  -> web/js/*.js
```

Key files:

- `ai-reliability-incident-console/app.py`: HTTP/static shell that delegates release triage and state views to `ReliabilityApi`.
- `ai-reliability-incident-console/src/reliability_console/api.py`: `ReliabilityApi` maps requests to releases, incidents, runbooks, eval runs, triage, traces, audit, scenario snapshots, and eval execution.
- `ai-reliability-incident-console/src/reliability_console/triage.py`: deterministic release-blocking decisions from incident severity, failed eval evidence, runbooks, and remediation steps.
- `ai-reliability-incident-console/src/reliability_console/storage.py`: JSON state, releases, incidents, eval runs, runbooks, traces, and audit events.
- `ai-reliability-incident-console/src/reliability_console/evals.py`: release-blocking, monitor-only, linked-evidence, and audit-trace regression cases.
- `ai-reliability-incident-console/web/js/api.js`: browser HTTP client.
- `ai-reliability-incident-console/web/js/app.js`: incident triage screen orchestration.
- `ai-reliability-incident-console/web/js/renderers.js`: release, incident, decision, eval, trace, and audit rendering.
- `ai-reliability-incident-console/web/js/scenarioEditor.js`: browser-local scenario draft and diff controls.
- `ai-reliability-incident-console/web/js/traceLinks.js`: trace deep links and keyboard navigation.

Safe change paths:

- Release decision behavior: update `triage.py`, seed/eval cases, runbook evidence, API contracts, and eval expectations together.
- New reliability signal: keep it visible in traces/audit and linked to eval or runbook evidence.
- UI behavior: keep release-blocking decisions inspectable without requiring screenshots.

## Common Frontend Modules

Each project keeps first-party browser code under its own `web/` directory:

- `web/js/api.js`: one small `fetch` wrapper for local API calls.
- `web/js/dom.js`: DOM lookup and safe text/element helpers.
- `web/js/renderers.js`: pure rendering helpers for response panels, evidence, traces, audit, approvals, or release decisions.
- `web/js/app.js`: event binding, default scenarios, API calls, and screen-level orchestration.
- `web/js/clipboard.js`: copy controls for trace IDs, trace links, and scenario drafts.
- `web/js/scenarioEditor.js`: browser-local draft editing and local diff display; it does not write repository files.
- `web/js/theme.js`: browser-local light/dark theme preference.
- `web/js/traceLinks.js`: local hash links and keyboard movement across trace records.

Frontend modules must import only local JavaScript files inside the same project `web/` boundary.

## Contributor Change Checklist

Use the smallest checklist that matches the change:

| Change Type | Files To Inspect | Evidence Commands |
| --- | --- | --- |
| Backend route or response shape | project `app.py`, `src/<package>/api.py`, `docs/api_contracts.md`, `scripts/check_api_contracts.py` | `python -B scripts/dev.py api-docs`, `python -B scripts/dev.py contracts`, `python -B scripts/dev.py quality` |
| Domain policy or side-effect behavior | domain module, `repositories.py`, `storage.py`, `evals.py`, `data/*.json`, threat/model docs if relevant | `python -B scripts/dev.py architecture`, `python -B scripts/dev.py evals`, `python -B scripts/dev.py smoke`, `python -B scripts/dev.py quality` |
| Frontend UI or client behavior | project `web/` folder, `docs/frontend_integrity.md`, `docs/runtime_ui_contracts.md` | `python -B scripts/dev.py frontend`, `python -B scripts/dev.py ui-contracts`, `python -B scripts/dev.py quality` |
| Scenario or seed data | `data/*.json`, `infra/postgres/seeds/*.sql`, `docs/demo_state_presets.json`, scenario/eval docs | `python -B scripts/dev.py scenario-data`, `python -B scripts/dev.py postgres-seed`, `python -B scripts/dev.py demo-presets`, `python -B scripts/dev.py quality` |
| Architecture boundary | `app.py`, `src/`, `web/js/`, `docs/architecture_boundaries.md` | `python -B scripts/dev.py architecture`, `python -B scripts/dev.py quality` |
| Public repo or contributor docs | README, `PROJECT_CONTENT_INDEX.md`, `.github/`, growth and review docs | `python -B scripts/dev.py community-issues`, `python -B scripts/dev.py safety`, `python -B scripts/dev.py quality` |

Before opening or merging a PR, run `python -B scripts/dev.py safety` and check `git diff --check`. Public documentation should stay fictional, local-first, and free of secrets or private machine paths.
