# Portfolio Evidence Matrix

Use this file when a reviewer, recruiter, or interviewer asks: "How do I know this is not just a chatbot demo?"

## Core Claims

| Claim | Evidence In Repo | Verification Command | Interview Framing |
| --- | --- | --- | --- |
| The portfolio runs locally without paid APIs. | `scripts/dev.py`, both `app.py` files, static `web/` folders | `python -B scripts/dev.py start` | Local-first keeps demos reliable and makes model-backed mode optional. |
| Both services are healthy. | `/api/health` routes in both projects | `python -B scripts/dev.py health` | Health checks make the demo and CI verifiable. |
| Project 1 enforces permissions before generation. | `secure-enterprise-knowledge-copilot/src/copilot/retrieval.py` | `python -B scripts/dev.py smoke` | The model never receives inaccessible evidence. |
| Project 1 abstains when evidence is missing or unauthorized. | `answering.py`, `evals.py`, `data/eval_cases.json` | `python -B scripts/dev.py evals` | Abstention is a product behavior, not a prompt-only instruction. |
| Project 1 handles prompt injection in retrieved content and user messages. | `security.py`, `answering.py`, eval cases `eval-005`, `eval-008` through `eval-011` | `python -B scripts/dev.py evals` | Retrieved text and user instructions are treated as untrusted input. |
| Project 2 blocks unsafe side effects. | `regulated-customer-operations-agent/src/ops_agent/tools.py` | `python -B scripts/dev.py smoke` | The model can suggest actions; application code controls execution. |
| Project 2 requires supervisor approval. | approval endpoint in `app.py`, tool guards in `tools.py` | `python -B scripts/dev.py smoke` | Approval gates are enforced outside the model. |
| Both projects have regression evals. | project `scripts/run_eval.py`, root `scripts/run_all_evals.py` | `python -B scripts/dev.py evals` | Evals protect the security and workflow invariants. |
| Demo flows are smoke-tested end to end. | `scripts/smoke_test_demo_flows.py` | `python -B scripts/dev.py smoke` | The demo path is tested like a user journey. |
| Demo replay evidence can be attached to releases. | `scripts/export_demo_replay_artifact.py`, `docs/demo_replay_artifact.md` | `python -B scripts/dev.py replay-artifact` | The live interview path produces ignored Markdown and JSON artifacts with trace, approval, and audit evidence. |
| Public release content is scanned. | `scripts/quality_gate.py` | `python -B scripts/dev.py quality` | The repository has a release gate, not just code. |
| Backend and frontend boundaries stay modular. | `scripts/check_architecture_boundaries.py`, `docs/architecture_boundaries.md` | `python -B scripts/dev.py architecture` | HTTP shells, API classes, domain logic, storage, evals, and frontend modules remain independently reviewable. |
| Frontend modules are wired to the expected UI. | `scripts/check_frontend_integrity.py`, project `web/` folders | `python -B scripts/dev.py frontend` | The demo UI is a thin, inspectable layer over backend APIs, with no build step or hidden bundle. |
| README screenshots do not silently drift from the UI source. | `docs/visual_assets_manifest.json`, `scripts/check_visual_asset_manifest.py`, `scripts/refresh_visual_assets.py`, `docs/visual_asset_hygiene.md` | `python -B scripts/dev.py visual-assets` | Visual assets are treated as release artifacts: screenshots can be refreshed from live apps, then hashes, dimensions, and frontend source hashes must line up. |
| Fresh clones work without hidden local state. | `scripts/check_fresh_clone_experience.py`, `docs/fresh_clone_experience.md` | `python -B scripts/dev.py fresh-clone` | The public repository is treated as the product surface: clone, static checks, isolated services, and smoke flows must work from a temp directory. |
| Running UI routes are served intentionally. | `scripts/check_runtime_ui_contracts.py`, both `app.py` files | `python -B scripts/dev.py ui-contracts` | The running demos serve local HTML/CSS/JS with stable content types, basic safety headers, JSON 404s, and traversal blocking. |
| API docs match source routes and runtime contracts. | `docs/api_contracts.md`, `scripts/check_api_documentation.py`, `scripts/check_api_contracts.py` | `python -B scripts/dev.py api-docs`, `python -B scripts/dev.py contracts` | A reviewer can map UI behavior to explicit backend endpoints and response-shape responsibilities. |
| Unexpected server errors do not leak internals. | `scripts/check_error_hygiene.py`, both `app.py` files | `python -B scripts/dev.py error-hygiene` | Raw exceptions, local paths, and secret-like markers are replaced by a generic browser-visible JSON error. |
| Dependency surface is intentional. | `scripts/check_dependency_surface.py`, `.github/dependabot.yml`, `docs/supply_chain_security.md` | `python -B scripts/dev.py dependency-surface` | The local path stays easy to audit: stdlib-only Python, first-party frontend assets, pinned Docker bases, and automated update monitoring. |
| Container release config is controlled. | `scripts/check_container_release.py`, `scripts/check_docker_runtime.py`, `docker-compose.yml`, project `.dockerignore` files, `docs/container_release_hygiene.md` | `python -B scripts/dev.py container-release`; Docker-enabled machines can run `python -B scripts/dev.py docker-runtime` | Docker packaging is treated as release-facing code: ports, health checks, commands, env defaults, ignored local state, and optional runtime smoke checks stay aligned. |
| GitHub Actions are safe for public PRs. | `.github/workflows/ci.yml`, `scripts/check_workflow_security.py`, `docs/workflow_security.md` | `python -B scripts/dev.py workflow-security` | External PR code runs with a read-only token, no secrets, safe triggers, hardened checkout, and approved actions. |
| Public PR review rules stay safety-focused. | `scripts/review_open_prs.py`, `scripts/check_pr_review_policy.py`, `docs/pr_review_security.md`, `.github/pull_request_template.md` | `python -B scripts/dev.py pr-policy` | Malicious or careless public contributions are treated as untrusted input before contributor code is executed. |
| Optional model gateways do not become security boundaries. | project `model_gateway.py` files, `.env.example`, `docs/model_gateway_safety.md` | `python -B scripts/dev.py model-gateway-safety` | OpenAI mode is opt-in, API keys stay outside the repo, structured outputs are enforced, and failures fall back to local behavior. |
| Trace, audit, and approval evidence is internally consistent. | `scripts/check_observability_integrity.py`, project trace/audit/approval endpoints, `docs/observability_integrity.md` | `python -B scripts/dev.py observability` | Critical demo responses can be explained after the fact by trace IDs, linked audit events, blocked-action records, and approval queue state. |
| Threats map to explicit controls. | `docs/threat_model.md`, project threat models, `scripts/check_threat_model.py` | `python -B scripts/dev.py threat-model` | Information disclosure, prompt injection, unsafe side effects, public PR abuse, dependency drift, model gateway risk, and UI route surprises each have deterministic controls and evidence commands. |
| Demo data stays fictional and internally consistent. | project `data/` folders, `scripts/check_scenario_data_integrity.py`, `docs/scenario_data_integrity.md` | `python -B scripts/dev.py scenario-data` | Roles, permissions, seed objects, and eval expectations remain aligned with the public demo story. |
| Optional OpenAI mode is configurable. | model gateway files, `.env.example`, `docs/model_runtime_configuration.md` | import check through `python -B scripts/dev.py verify` | Model choice, reasoning effort, and verbosity are runtime decisions. |
| The model is not the security boundary. | `docs/adr_0002_model_is_not_security_boundary.md` | doc review plus smoke/evals | This is the core enterprise deployment principle. |

## Current Verification Snapshot

```text
python -B scripts/dev.py verify
```

Current expected result:

- health check: both services ok
- Project 1 eval: 11/11 passed, unsafe leak failures 0
- Project 2 eval: 8/8 passed, unsafe direct side-effect failures 0
- smoke tests: 9/9 passed
- quality gate: passed

## Hard Interview Use

If challenged on depth, answer in this order:

1. State the invariant.
2. Name the application code that enforces it.
3. Name the eval or smoke flow that proves it.
4. State what would change in production without changing the invariant.

Example:

```text
For permission-aware RAG, the invariant is that unauthorized evidence never reaches the model. Retrieval filters documents by user role before answer generation, the Alice finance eval proves abstention, and the Morgan finance eval proves authorized access still works. In production I would replace JSON storage with PostgreSQL row-level security and vector retrieval, but the permission boundary would stay before model generation.
```
