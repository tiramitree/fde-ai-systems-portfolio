# FDE AI Systems Reference Implementations

[![Quality Gate](https://github.com/tiramitree/fde-ai-systems-portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/tiramitree/fde-ai-systems-portfolio/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Local First](https://img.shields.io/badge/local--first-no_paid_API_required-2f855a)

Three runnable enterprise AI systems demonstrating secure RAG, governed agents, AI release reliability, evals, traces, audit logs, and approval gates.

![FDE AI Systems Reference Implementations](docs/assets/github-preview.png)

Most AI app demos stop at chat. Real enterprise deployments need permission boundaries, evidence, human approval, release reliability, debugging surfaces, and regression tests. This repo implements those patterns in three local-first systems that run without paid APIs, while leaving clean upgrade paths to OpenAI Responses API, Agents SDK, PostgreSQL/pgvector, OpenTelemetry, and enterprise connectors.

## Projects

| Project | What It Demonstrates | Local URL |
| --- | --- | --- |
| Secure Enterprise Knowledge Copilot | Permission-aware RAG, citations, abstention, prompt-injection handling, traces, audit logs, evals | `http://127.0.0.1:8765` |
| Regulated Customer Operations Agent | Tool calling, business workflow automation, approval queue, side-effect blocking, supervisor approval, unsafe-action evals | `http://127.0.0.1:8770` |
| AI Reliability Incident Console | Canary release triage, eval regression evidence, rollout blocking, remediation plans, traces, audit logs | `http://127.0.0.1:8780` |

## Why This Exists

FDE and AI application systems need more than a model call. These reference implementations focus on the controls that usually separate production-oriented AI systems from chatbot demos:

- permissions before model generation
- citations and abstention instead of unsupported answers
- retrieved-content prompt-injection handling
- tool permissions and approval gates
- trace and audit surfaces
- eval gates and smoke tests
- clear production upgrade paths

## Quickstart

Verify everything from a clean checkout:

```bash
python -B scripts/dev.py verify
```

Start all demos:

```bash
python -B scripts/dev.py start
```

Or start them separately:

```bash
cd secure-enterprise-knowledge-copilot
python -B app.py --reset --port 8765
```

```bash
cd regulated-customer-operations-agent
python -B app.py --reset --port 8770
```

```bash
cd ai-reliability-incident-console
python -B app.py --reset --port 8780
```

Useful commands:

```bash
python -B scripts/dev.py assets
python -B scripts/dev.py api-docs
python -B scripts/dev.py architecture
python -B scripts/dev.py claims
python -B scripts/dev.py community-issues
python -B scripts/dev.py container-release
python -B scripts/dev.py docker-runtime
python -B scripts/dev.py dependency-surface
python -B scripts/dev.py contracts
python -B scripts/dev.py error-hygiene
python -B scripts/dev.py frontend
python -B scripts/dev.py health
python -B scripts/dev.py evals
python -B scripts/dev.py eval-csv
python -B scripts/dev.py github-launch-setup
python -B scripts/dev.py github-community
python -B scripts/dev.py github-maintenance
python -B scripts/dev.py fresh-clone-local
python -B scripts/dev.py fresh-clone
python -B scripts/dev.py github-readiness
python -B scripts/dev.py governance
python -B scripts/dev.py launch-assets
python -B scripts/dev.py model-gateway-safety
python -B scripts/dev.py observability
python -B scripts/dev.py openai-live
python -B scripts/dev.py otel-traces
python -B scripts/dev.py pr-policy
python -B scripts/dev.py pr-triage
python -B scripts/dev.py readiness-report
python -B scripts/dev.py refresh-visual-assets
python -B scripts/dev.py replay
python -B scripts/dev.py replay-artifact
python -B scripts/dev.py scenario-data
python -B scripts/dev.py smoke
python -B scripts/dev.py report
python -B scripts/dev.py safety
python -B scripts/dev.py threat-model
python -B scripts/dev.py ui-contracts
python -B scripts/dev.py visual-assets
python -B scripts/dev.py workflow-security
python -B scripts/dev.py quality
python -B scripts/post_publish_check.py
```

Current verified status:

```text
health check: all services ok
smoke tests: 13/13 passed
Project 1 eval: 11/11 passed, unsafe_leak_failures = 0
Project 2 eval: 8/8 passed, unsafe_direct_side_effect_failures = 0
Project 3 eval: 6/6 passed, unsafe_release_approval_failures = 0
```

## Evidence Matrix

| Production Concern | Where To Look | Verification |
| --- | --- | --- |
| Permission-aware RAG | `secure-enterprise-knowledge-copilot/src/copilot/retrieval.py` | Alice finance query abstains; Morgan finance query answers |
| Prompt-injection handling | `secure-enterprise-knowledge-copilot/src/copilot/security.py`, `secure-enterprise-knowledge-copilot/src/copilot/answering.py` | `eval-005`, `eval-008` through `eval-011` |
| Governed tool use | `regulated-customer-operations-agent/src/ops_agent/tools.py` | direct `send_notice` is blocked for investigator |
| Human approval | Project 2 approval queue and supervisor endpoint | supervisor approval sends the notice once |
| Regression gates | `scripts/dev.py`, project eval runners, CSV summary export | `python -B scripts/dev.py verify`, `python -B scripts/dev.py eval-csv` |
| Public claim consistency | `scripts/check_claim_consistency.py` | README, release notes, evidence matrix, and preview metrics match eval/smoke evidence |
| Architecture boundaries | `scripts/check_architecture_boundaries.py`, `docs/architecture_boundaries.md` | app shells, API classes, backend packages, and frontend modules preserve separation of concerns |
| Frontend integrity | `scripts/check_frontend_integrity.py`, project `web/` folders | HTML, labels, local ES modules, DOM wiring, trace-copy and trace-link controls, and quick actions stay intact |
| Visual asset hygiene | `scripts/check_visual_asset_manifest.py`, `scripts/refresh_visual_assets.py`, `docs/visual_assets_manifest.json` | README screenshots stay tied to recorded frontend source hashes and can be refreshed from live local apps |
| Fresh clone experience | `scripts/check_fresh_clone_experience.py`, `docs/fresh_clone_experience.md` | clone the public repo into a temp directory, run release-facing checks, start all apps on isolated ports, and run smoke flows |
| Runtime UI contracts | `scripts/check_runtime_ui_contracts.py`, project `app.py` files | static assets, content types, security headers, 404s, and traversal blocking |
| Error hygiene | `scripts/check_error_hygiene.py`, project `app.py` files | unexpected exceptions return generic JSON errors without leaking paths, stack details, or secret-like strings |
| Dependency surface | `scripts/check_dependency_surface.py`, `.github/dependabot.yml`, `docs/supply_chain_security.md` | stdlib-only Python path, first-party frontend assets, pinned Docker bases, and Dependabot coverage |
| Container release hygiene | `scripts/check_container_release.py`, `scripts/check_docker_runtime.py`, `docs/container_release_hygiene.md` | Dockerfiles, compose ports, health checks, startup commands, env handling, build-context ignores, and optional runtime smoke checks stay aligned |
| API contracts | `scripts/check_api_contracts.py`, `scripts/check_api_documentation.py`, `docs/api_contracts.md` | runtime response shapes and public API documentation stay aligned with source routes |
| GitHub launch setup | `scripts/configure_github_launch.py` | dry-run repo metadata, topics, branch protection, and release commands |
| Community issue pack | `scripts/check_community_issue_pack.py`, `scripts/manage_community_issues.py`, `docs/github_labels.json` | labels, issue templates, contributor issue pack, and optional GitHub issue creation stay aligned |
| Launch asset hygiene | `scripts/check_launch_assets.py`, `docs/launch_assets_hygiene.md` | launch copy, star-growth plan, public issue pack, and anti-hype boundaries stay complete and honest |
| Repository governance | `scripts/check_repository_governance.py`, `.github/CODEOWNERS` | code-owner review and branch-protection payload sanity checks |
| Workflow security | `scripts/check_workflow_security.py`, `.github/workflows/ci.yml` | read-only workflow token, safe PR trigger, hardened checkout, and approved actions |
| Model gateway safety | `scripts/check_model_gateway_safety.py`, `scripts/check_openai_live_mode.py`, project `model_gateway.py` files | OpenAI mode is opt-in, key references are constrained, structured outputs are required, failures fall back locally, and live mode can be verified when a key is available |
| Observability integrity | `scripts/check_observability_integrity.py`, project trace/audit/approval endpoints | response trace IDs, audit events, approval records, blocked actions, unauthorized-query evidence, and release decisions stay internally consistent |
| Threat model | `docs/threat_model.md`, `scripts/check_threat_model.py` | threat IDs map to deterministic controls, source files, and evidence commands |
| Scenario data integrity | `scripts/check_scenario_data_integrity.py`, project `data/` folders | fictional seed data, roles, references, and eval expectations remain internally consistent |
| PR review policy | `scripts/check_pr_review_policy.py`, `docs/pr_review_security.md` | triage heuristics, runbook, maintainer policy, and PR template keep malicious-contribution checks intact |
| Public PR triage | `scripts/review_open_prs.py` | inspect open PRs and flag risky diffs before running code |
| Replayable demo | `scripts/replay_demo.py` | reset services, run key flows, print trace and approval evidence |
| Replay artifact | `scripts/export_demo_replay_artifact.py`, `docs/demo_replay_artifact.md` | generate release-attachable Markdown and JSON evidence under ignored `out/` |
| Observability export | `scripts/export_traces_otel.py` | local traces convert to OTLP/JSON-compatible `resourceSpans` |
| Final readiness report | `scripts/generate_final_readiness_report.py` | compact launch, blocker, and technical review walkthrough status |

See [System Evidence Matrix](docs/portfolio_evidence_matrix.md) for the full claim-to-evidence map.

## Screenshots

![Demo walkthrough](docs/assets/demo-walkthrough.gif)

| Secure Enterprise Knowledge Copilot | Regulated Customer Operations Agent | AI Reliability Incident Console |
| --- | --- | --- |
| ![Secure Enterprise Knowledge Copilot screenshot](docs/assets/secure-knowledge-copilot-screenshot.png) | ![Regulated Customer Operations Agent screenshot](docs/assets/regulated-ops-agent-screenshot.png) | ![AI Reliability Incident Console screenshot](docs/assets/ai-reliability-incident-console-screenshot.png) |

## Project 1: Secure Enterprise Knowledge Copilot

Open:

```text
http://127.0.0.1:8765
```

Show:

1. Alice asks: `How many days per week can employees work remotely?`
2. The system answers with `Remote Work Policy 2026` citation.
3. Alice asks: `What is the finance retention plan?`
4. The system abstains because Alice cannot access confidential finance evidence.
5. Morgan asks the same finance question.
6. The system answers with `Finance Retention Plan 2026` citation.
7. Run evals.

Core claim:

> The model never receives evidence the user is not allowed to access.

## Project 2: Regulated Customer Operations Agent

Open:

```text
http://127.0.0.1:8770
```

Show:

1. Ivy investigates Market Blue / RX-900 recalled product.
2. The agent searches policy and listings.
3. It creates a violation, drafts seller notice, schedules follow-up.
4. It creates an approval request before sending.
5. Direct `send_notice` is blocked for investigator.
6. Supervisor approval sends the notice.
7. Run evals.

Core claim:

> The model may propose actions, but side effects are enforced by application logic.

## Architecture

![Architecture overview](docs/assets/architecture-overview.svg)

```text
Reference Systems
  +-- Secure Enterprise Knowledge Copilot
  |   +-- role-aware retrieval
  |   +-- citation answer shape
  |   +-- abstention logic
  |   +-- prompt-injection detection
  |   +-- trace/audit/evals
  |
  +-- Regulated Customer Operations Agent
  |   +-- intent routing
  |   +-- business tools
  |   +-- approval queue
  |   +-- side-effect blocking
  |   +-- trace/audit/evals
  |
  +-- AI Reliability Incident Console
      +-- canary release triage
      +-- eval regression evidence
      +-- rollout blocking
      +-- remediation plans
      +-- trace/audit/evals
```

All three projects are dependency-free by default so they run reliably anywhere with Python 3.12. Optional OpenAI gateways are included for the model-facing projects but disabled by default.

## Optional OpenAI Mode

```powershell
$env:OPENAI_API_KEY="..."
$env:OPENAI_MODEL="gpt-5.2"
$env:OPENAI_REASONING_EFFORT="medium"
$env:OPENAI_TEXT_VERBOSITY="low"
$env:COPILOT_MODEL_PROVIDER="openai"
$env:OPS_AGENT_MODEL_ROUTER="openai"
```

Security boundaries remain outside the model:

- Project 1 filters permissions and unsafe retrieved content before generation.
- Project 2 enforces approval gates in deterministic application code.
- Project 3 links eval regressions to release decisions without a model dependency.

With a real API key, verify live OpenAI mode without changing the default local path:

```powershell
python -B scripts/dev.py openai-live
```

The check starts both model-facing apps with OpenAI mode enabled, requires Project 1 to return `model_provider=openai`, requires Project 2 to return `model_router=openai`, and still verifies citations, approvals, and side-effect blocking.

## Docker

Docker config is included:

```powershell
docker compose up --build
```

Docker release hygiene is statically gated:

```powershell
python -B scripts/dev.py container-release
```

On a Docker-enabled machine, run the runtime proof:

```powershell
python -B scripts/dev.py docker-runtime
```

This builds all service images through Compose, waits for health endpoints, runs the same smoke flows against the containers, and tears the Compose project down. Docker is not installed in this environment, so the local Python runtime is the fully verified path here.

## Repository Structure

```text
repository/
  secure-enterprise-knowledge-copilot/
  regulated-customer-operations-agent/
  ai-reliability-incident-console/
  scripts/
  docs/
  .github/
```

## Key Docs

- [Project Content Index](PROJECT_CONTENT_INDEX.md)
- [Changelog](CHANGELOG.md)
- [Final Demo Runbook](docs/final_demo_runbook.md)
- [Demo Report](docs/demo_report.md)
- [Demo Replay Artifact](docs/demo_replay_artifact.md)
- [Project Case Notes](docs/project_case_notes.md)
- [Production Upgrade Notes](docs/production_upgrade_notes.md)
- [PostgreSQL And pgvector Adapter Design](docs/postgres_pgvector_adapter_design.md)
- [OpenTelemetry Trace Export](docs/otel_trace_export.md)
- [Model Runtime Configuration](docs/model_runtime_configuration.md)
- [Model Gateway Safety](docs/model_gateway_safety.md)
- [Launch Assets Hygiene](docs/launch_assets_hygiene.md)
- [Observability Integrity](docs/observability_integrity.md)
- [Threat Model](docs/threat_model.md)
- [Scenario Data Integrity](docs/scenario_data_integrity.md)
- [Error Hygiene](docs/error_hygiene.md)
- [Container Release Hygiene](docs/container_release_hygiene.md)
- [Visual Asset Hygiene](docs/visual_asset_hygiene.md)
- [Architecture Boundaries](docs/architecture_boundaries.md)
- [Workflow Security](docs/workflow_security.md)
- [Final Completion Audit](docs/final_completion_audit.md)
- [GitHub Launch Plan](docs/github_launch_plan.md)
- [Published Repository Status](docs/published_repository_status.md)
- [GitHub Repository Settings](docs/github_repository_settings.md)
- [Community Backlog](docs/community_backlog.md)
- [Public Release Audit](docs/public_release_audit.md)
- [Differentiation Strategy](docs/differentiation_strategy.md)
- [Technical Review Playbook](docs/technical_review_playbook.md)
- [System Design Deep Dive](docs/system_design_deep_dive.md)
- [System Evidence Matrix](docs/portfolio_evidence_matrix.md)
- [ADR 0001: Local-First Reference Runtime](docs/adr_0001_local_first_portfolio.md)
- [ADR 0002: The Model Is Not The Security Boundary](docs/adr_0002_model_is_not_security_boundary.md)
- [ADR 0003: Eval State Isolated From Demo State](docs/adr_0003_eval_state_isolated_from_demo_state.md)
- [Secure RAG Case Study](docs/case_study_secure_enterprise_knowledge_copilot.md)
- [Governed Agent Case Study](docs/case_study_regulated_customer_operations_agent.md)
- [Demo Video Script](docs/demo_video_script.md)
- [Demo Recording Checklist](docs/demo_recording_checklist.md)
- [Star Growth Plan](docs/star_growth_plan.md)
- [Launch Copy Pack](docs/launch_copy_pack.md)
- [GitHub Community Issue Pack](docs/github_initial_issues.md)
- [Reviewer Perspective Checklist](docs/reviewer_perspective_checklist.md)
- [Fresh Clone Experience](docs/fresh_clone_experience.md)
- [API Contracts](docs/api_contracts.md)
- [PR Review Security](docs/pr_review_security.md)
- [Pull Request Review Runbook](docs/pr_review_runbook.md)
- [GitHub Release Commands](docs/github_release_commands.md)
- [Post-Publish Checklist](docs/post_publish_checklist.md)
- [Roadmap](ROADMAP.md)
- [AI Reliability Incident Console](ai-reliability-incident-console/README.md)

## System Narrative

The first project handles enterprise knowledge access with permissions, citations, abstention, traces, audit logs, and evals. The second project connects an agent to operational tools while preventing unsafe side effects through approval queues and governance checks. The third project handles AI release reliability after deployment by linking eval regressions, incidents, rollout blocking, traces, audit logs, and remediation plans. The browser demos expose trace IDs and local trace links so a specific run can be inspected again without relying on screenshots.

Together they form a compact reference architecture for AI systems that are useful, inspectable, and safe enough to reason about before enterprise deployment.

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
