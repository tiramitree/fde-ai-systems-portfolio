# Project Content Index

This file is the compact map of the repository. Use it when context is lost, when preparing a release review, or before publishing the repository.

## Current Scope

The repository contains three runnable FDE-style AI reference systems:

1. `secure-enterprise-knowledge-copilot`
   - Demonstrates permission-aware enterprise RAG.
   - Core behaviors: retrieval filtering, citations, abstention, prompt-injection detection, traces, audit logs, golden evals.
   - Local URL: `http://127.0.0.1:8765`

2. `regulated-customer-operations-agent`
   - Demonstrates governed tool-calling workflow automation.
   - Core behaviors: intent routing, operational tools, approval queue, side-effect blocking, supervisor approval, traces, audit logs, golden evals.
   - Local URL: `http://127.0.0.1:8770`

3. `ai-reliability-incident-console`
   - Demonstrates AI release reliability and eval regression triage.
   - Core behaviors: canary release incident triage, linked failed eval evidence, rollout blocking, remediation steps, traces, audit logs, golden evals.
   - Local URL: `http://127.0.0.1:8780`

The design target is not "chatbot demo". The design target is an operational reference repository showing how to build AI systems around model calls: product workflow, safety boundaries, evals, observability, and deployment paths.

## How To Run

From the repository root:

```bash
python -B scripts/dev.py verify
python -B scripts/dev.py start
python -B scripts/dev.py api-docs
python -B scripts/dev.py assets
python -B scripts/dev.py architecture
python -B scripts/dev.py claims
python -B scripts/dev.py community-issues
python -B scripts/dev.py container-release
python -B scripts/dev.py docker-runtime
python -B scripts/dev.py dependency-surface
python -B scripts/dev.py demo-presets
python -B scripts/dev.py contracts
python -B scripts/dev.py error-hygiene
python -B scripts/dev.py health
python -B scripts/dev.py evals
python -B scripts/dev.py eval-csv
python -B scripts/dev.py frontend
python -B scripts/dev.py fresh-clone-local
python -B scripts/dev.py fresh-clone
python -B scripts/dev.py github-community
python -B scripts/dev.py github-launch-setup
python -B scripts/dev.py github-maintenance
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
python -B scripts/dev.py visual-asset-diff
python -B scripts/dev.py workflow-security
python -B scripts/dev.py quality
```

Verified local demo URLs:

- Secure Enterprise Knowledge Copilot: `http://127.0.0.1:8765`
- Regulated Customer Operations Agent: `http://127.0.0.1:8770`
- AI Reliability Incident Console: `http://127.0.0.1:8780`

## Verified State

Latest local verification:

```text
python -B scripts/dev.py verify
```

Result:

- all services healthy
- Project 1 eval: 11/11 passed, unsafe leaks 0
- Project 2 eval: 8/8 passed, unsafe direct side-effect failures 0
- Project 3 eval: 6/6 passed, unsafe release approval failures 0
- smoke tests: 13/13 passed
- demo report generated
- quality gate passed

Local Git state:

- repository initialized
- default branch: `main`
- GitHub repository published at `https://github.com/tiramitree/fde-ai-systems-portfolio`
- GitHub Actions `quality-gate` passed after publication
- tracked worktree clean after `python -B scripts/dev.py verify`
- runtime state, logs, SQLite files, and Python caches are ignored

## Root Files

- `README.md`: public GitHub-facing landing page.
- `PROJECT_CONTENT_INDEX.md`: this file, the compact repo map.
- `CHANGELOG.md`: public release history and verification notes.
- `.gitattributes`: keeps text files LF-normalized across platforms.
- `docker-compose.yml`: Docker entrypoint for Docker-enabled machines.
- project-level `.dockerignore` files: keep runtime state, logs, caches, and local env files out of Docker build contexts.
- `.env.example`: optional OpenAI mode environment template.
- `LICENSE`: MIT license.
- `CONTRIBUTING.md`: contribution workflow.
- `SECURITY.md`: security reporting and boundary statement.
- `CODE_OF_CONDUCT.md`: community behavior policy.
- `ROADMAP.md`: near-term project direction.
- `.gitignore`: excludes runtime state, logs, caches, and local env files.

## Automation And Quality Scripts

- `scripts/dev.py`: single developer entrypoint for start, api-docs, architecture, assets, claims, community-issues, container-release, docker-runtime, dependency-surface, demo-presets, contracts, error-hygiene, health, evals, eval-csv, frontend, fresh-clone-local, fresh-clone, github-community, github-launch-setup, github-maintenance, github-readiness, governance, launch-assets, model-gateway-safety, observability, openai-live, otel-traces, pr-policy, pr-triage, readiness-report, refresh-visual-assets, replay, replay-artifact, scenario-data, smoke, report, safety, quality, threat-model, ui-contracts, visual-assets, visual-asset-diff, workflow-security, verify.
- `scripts/start_demo_servers.py`: starts all local demos.
- `scripts/check_architecture_boundaries.py`: verifies app shells, API classes, backend packages, and frontend modules preserve separation of concerns.
- `scripts/check_workflow_security.py`: verifies GitHub Actions keep safe PR triggers, read-only token permissions, hardened checkout, and approved actions.
- `scripts/check_model_gateway_safety.py`: verifies optional OpenAI gateways stay opt-in, key references remain constrained, structured outputs are required, and failures fall back locally.
- `scripts/check_openai_live_mode.py`: optionally proves live OpenAI mode with a real API key while preserving citations, approval requests, and side-effect blocking.
- `scripts/check_observability_integrity.py`: starts isolated services and verifies trace, audit, approval, blocked-action, unauthorized-query, and release-decision evidence stay consistent with demo outcomes.
- `scripts/check_threat_model.py`: verifies repository threat IDs map to deterministic controls, source files, supporting docs, and evidence commands.
- `scripts/check_scenario_data_integrity.py`: verifies fictional seed data, roles, cross-references, and eval expectations remain internally consistent for the local scenario draft surface.
- `scripts/check_demo_state_presets.py`: verifies shareable demo reset presets in `docs/demo_state_presets.json` still reference valid fictional seed and eval data.
- `scripts/check_error_hygiene.py`: verifies unexpected backend exceptions return generic JSON errors without leaking internals.
- `scripts/check_public_assets.py`: verifies local Markdown links and public image assets.
- `scripts/check_visual_asset_manifest.py`: verifies desktop and mobile demo screenshots match recorded asset hashes, dimensions, contrast samples, and frontend source hashes.
- `scripts/summarize_visual_asset_diff.py`: summarizes changed visual asset paths, dimensions, hash prefixes, source-hash changes, and contrast ratios without printing binary image contents.
- `scripts/refresh_visual_assets.py`: starts live local apps, captures desktop and mobile demo screenshots with a local browser, and rewrites the visual asset manifest.
- `scripts/check_claim_consistency.py`: verifies public metric claims match eval case counts, smoke checks, and generated demo report evidence.
- `scripts/check_container_release.py`: verifies Dockerfiles, Compose ports, health checks, startup commands, env handling, and build-context ignores stay aligned.
- `scripts/check_docker_runtime.py`: optionally builds the Compose stack, waits for container health, runs smoke flows, and tears the stack down on Docker-enabled machines.
- `scripts/check_frontend_integrity.py`: verifies project HTML, labels, local ES modules, DOM wiring, trace-copy controls, keyboard trace deep links, copyable scenario-draft controls, local draft diffs, and quick-action controls.
- `scripts/check_fresh_clone_experience.py`: clones the repository into a temporary directory, runs release-facing static checks, starts all demos on isolated ports, and runs health/smoke flows.
- `scripts/check_runtime_ui_contracts.py`: starts isolated services and verifies static UI routes, scenario editor modules, content types, security headers, 404s, and traversal blocking.
- `scripts/check_api_documentation.py`: verifies API source routes, public API contract documentation, README, index, and evidence matrix stay aligned.
- `scripts/check_dependency_surface.py`: verifies stdlib-only Python imports, first-party frontend assets, digest-pinned Docker bases, and Dependabot coverage.
- `scripts/check_api_contracts.py`: verifies stable response shapes for UI-facing API endpoints.
- `scripts/check_health.py`: verifies all service health endpoints.
- `scripts/configure_github_launch.py`: dry-runs or applies GitHub repo metadata, topics, merge policy, best-effort security settings, branch protection, and first-release setup through `gh`.
- `scripts/maintain_github_state.py`: dry-runs or applies authenticated GitHub repository maintenance and guarded Dependabot runtime-bump PR closure.
- `scripts/check_github_readiness.py`: reports public repository metadata, release, CI, issue, and PR readiness.
- `scripts/check_repository_governance.py`: validates CODEOWNERS, branch-protection payload, and PR-template safeguards.
- `scripts/check_launch_assets.py`: verifies launch copy, star-growth materials, initial issue pack, public-doc links, and anti-hype boundaries.
- `scripts/check_community_issue_pack.py`: verifies GitHub label manifest, issue templates, community issue pack, acceptance criteria, and verification commands.
- `scripts/manage_community_issues.py`: dry-runs or applies GitHub label sync and optional community issue creation through `gh`.
- `scripts/community_issue_pack.py`: shared parser for label and community issue automation.
- `scripts/generate_final_readiness_report.py`: writes the compact launch, blocker, and technical review walkthrough report.
- `scripts/check_pr_review_policy.py`: verifies malicious-contribution triage heuristics, runbook, maintainer policy, docs-only review examples, and PR template safeguards remain intact.
- `scripts/review_open_prs.py`: inspects open public PRs and flags risky diffs before running contributor code.
- `scripts/run_all_evals.py`: runs all project eval suites.
- `scripts/export_eval_csv.py`: exports repository eval summary rows to `eval_summaries.csv`.
- `scripts/export_traces_otel.py`: exports local trace records to an OTLP/JSON-compatible payload.
- `scripts/replay_demo.py`: starts clean reset demo services, runs the release validation path, and prints trace/approval evidence.
- `scripts/export_demo_replay_artifact.py`: writes release-attachable Markdown and JSON replay evidence under ignored `out/`.
- `scripts/smoke_test_demo_flows.py`: exercises the critical demo paths end to end.
- `scripts/generate_demo_report.py`: writes `docs/demo_report.md`.
- `scripts/public_safety_scan.py`: scans public files for secret-like tokens, personal identifiers, local paths, and tracked runtime artifacts.
- `scripts/quality_gate.py`: local release gate.
- `scripts/ci_quality_gate.py`: clean-checkout CI gate for GitHub Actions.
- `scripts/post_publish_check.py`: verifies remote GitHub publication after `main` is pushed.

## GitHub Assets

- `.github/workflows/ci.yml`: GitHub Actions workflow.
- `.github/CODEOWNERS`: code-owner review coverage for public contributions and safety-critical files.
- `.github/dependabot.yml`: weekly updates for GitHub Actions and Docker base images.
- `.github/pull_request_template.md`: PR checklist.
- `.github/ISSUE_TEMPLATE/bug_report.md`: bug report template.
- `.github/ISSUE_TEMPLATE/eval_case.md`: eval regression template.
- `.github/ISSUE_TEMPLATE/feature_request.md`: feature request template.

## Reference Docs

Start here:

- `docs/final_demo_runbook.md`: exact live demo order.
- `docs/development_issue_solutions.md`: recurring development, GitHub, PR, and publication issues with current resolutions.
- `docs/final_readiness_report.md`: compact launch, blocker, and release review status.
- `docs/demo_report.md`: generated verification report.
- `docs/demo_replay_artifact.md`: release-attachable replay evidence artifact instructions and review framing.
- `docs/completion_checklist.md`: current status and remaining blockers.
- `docs/final_completion_audit.md`: objective-by-objective audit.

Design Review Docs:

- `docs/project_case_notes.md`: project impact notes and review framing.
- `docs/technical_review_playbook.md`: difficult system-design questions and answers.
- `docs/system_design_deep_dive.md`: architecture reasoning and tradeoffs.
- `docs/postgres_pgvector_adapter_design.md`: PostgreSQL, pgvector, RLS, migrations, indexing, and eval-isolation adapter design.
- `docs/otel_trace_export.md`: local trace to OpenTelemetry-compatible JSON mapping and production collector path.
- `docs/model_runtime_configuration.md`: optional OpenAI model, reasoning effort, verbosity, and structured-output configuration.
- `docs/openai_live_mode_troubleshooting.md`: optional OpenAI live-mode setup, safe failure modes, rollback, and review guardrails.
- `docs/model_gateway_safety.md`: optional model gateway key-safety, fallback, and boundary contract.
- `docs/observability_integrity.md`: trace, audit, approval, refusal, and release-decision evidence contract for the critical demo flows.
- `docs/trace_timeline_examples.md`: copyable local timelines from request to trace, audit, approval, and release-decision evidence for the canonical flows.
- `docs/threat_model.md`: repository threat matrix, trust boundaries, control owners, evidence commands, and review framing.
- `docs/scenario_data_integrity.md`: fictional seed/eval data consistency and review framing.
- `docs/seed_fixture_data_flow.md`: source-to-runtime data-flow map for checked-in seed fixtures, runtime state, eval state, scenario drafts, traces, audit, approvals, and release decisions.
- `docs/local_artifact_glossary.md`: local glossary for seed, runtime, eval, replay, trace, audit, approval, release evidence, and generated artifacts.
- `docs/local_demo_reset_troubleshooting.md`: local reset troubleshooting for runtime state, eval runtime state, browser scenario drafts, and canonical demo presets.
- `docs/command_output_troubleshooting_map.md`: local troubleshooting map from common gate output to first files, narrower commands, and safe follow-up checks.
- `docs/readme_navigation_audit.md`: README-to-docs navigation audit for release-facing pointers, supporting docs, owner gates, and drift risks.
- `docs/readme_navigation_drift_examples.md`: examples for fixing stale README links, unsupported claims, missing source docs, and manual-evidence drift.
- `docs/eval_authoring_guide.md`: contributor workflow for adding retrieval, approval, refusal, release-blocking, and monitor-only eval cases safely.
- `docs/eval_gate_troubleshooting_examples.md`: local troubleshooting map for unsafe retrieval, direct side-effect, and release-blocking eval failures.
- `docs/seed_data_extension_examples.md`: copyable fictional seed extension examples for one knowledge document, one operations case, and one incident signal.
- `docs/error_hygiene.md`: generic error response contract for unexpected backend failures.
- `docs/container_release_hygiene.md`: Docker/Compose release hygiene gate and honest runtime-verification framing.
- `docs/docker_runtime_evidence_checklist.md`: Docker-enabled runtime evidence checklist, expected output, failure notes, and claim wording.
- `docs/visual_asset_hygiene.md`: desktop/mobile screenshot manifest, source-hash drift protection, refresh troubleshooting, and review framing.
- `docs/architecture_boundaries.md`: app/API/domain/frontend boundary contract and review framing.
- `docs/code_tour.md`: contributor map from HTTP shells to API classes, domain modules, storage, evals, and frontend modules.
- `docs/first_pull_request_checklist.md`: first local pull request checklist for clone, branch, diff review, route selection, targeted gates, quality checks, and PR handoff.
- `docs/docs_only_pr_review_examples.md`: examples for approving, requesting changes, or closing docs-only PRs without weakening public claims.
- `docs/readme_navigation_audit.md`: README navigation audit for release, contribution, review, optional environment, and technical evidence links.
- `docs/workflow_security.md`: GitHub Actions and external PR workflow security posture.
- `docs/supply_chain_security.md`: dependency posture, supply-chain gate, and dependency-addition policy.
- `docs/frontend_integrity.md`: frontend wiring, trace-copy, keyboard trace-link, copyable scenario-draft controls, local draft diffs, no-build local UI posture, and review framing.
- `docs/fresh_clone_experience.md`: public clone verification, isolated-port smoke proof, and review framing.
- `docs/runtime_ui_contracts.md`: running UI route contracts, local security headers, and static-serving boundary notes.
- `docs/api_contracts.md`: documented backend API surface, response-shape boundaries, and review framing.
- `docs/api_request_cookbook.md`: copyable local API requests for the canonical Project 1, Project 2, and Project 3 demo paths.
- `docs/api_error_examples.md`: copyable local requests for expected 403, 404, invalid JSON, and typed API error responses.
- `docs/openai_live_mode_troubleshooting.md`: local-only troubleshooting for optional API-key environments, safe fallback, and no-secret review rules.
- `docs/portfolio_evidence_matrix.md`: system claim-to-evidence map.
- `docs/case_study_secure_enterprise_knowledge_copilot.md`: Project 1 case study.
- `docs/case_study_regulated_customer_operations_agent.md`: Project 2 case study.

Release and growth:

- `docs/public_release_audit.md`: public-readiness audit.
- `docs/reviewer_perspective_checklist.md`: checks from user and reviewer perspectives.
- `docs/pr_review_security.md`: PR review policy gate and malicious-contribution review framing.
- `docs/docs_only_pr_review_examples.md`: docs-only PR review examples for useful docs, low-signal docs, unsafe docs, claim checks, link checks, generated artifact checks, and issue-pack drift.
- `docs/docs_only_review_comment_examples.md`: maintainer comment templates for approving, requesting changes, closing unsafe changes, or closing low-signal docs-only PRs.
- `docs/readme_navigation_drift_examples.md`: README navigation drift fix examples for docs-only reviews that touch public navigation or evidence wording.
- `docs/github_launch_plan.md`: launch sequence.
- `docs/published_repository_status.md`: current GitHub publication evidence and remaining manual release tasks.
- `docs/github_branch_protection.json`: branch-protection payload for `main`.
- `docs/github_repository_settings.md`: repository description, topics, social preview, branch protection, and first-release settings.
- `docs/github_release_commands.md`: publication commands.
- `docs/github_release_notes_v0.1.0.md`: release notes used by `scripts/configure_github_launch.py`.
- `docs/maintainer_review_policy.md`: policy for accepting useful reviews and ignoring unsafe or low-signal external activity.
- `docs/pr_review_runbook.md`: concrete PR review command sequence and merge bar.
- `docs/development_issue_solutions.md`: issue and solution log for recurring local, GitHub, PR, and publication problems.
- `docs/post_publish_checklist.md`: post-publish verification checklist.
- `docs/launch_assets_hygiene.md`: launch copy, star-growth, issue-pack, and anti-hype release gate.
- `docs/community_backlog.md`: first public issue backlog and contribution guardrails.
- `docs/github_initial_issues.md`: completed launch issues and current community issue pack with labels, acceptance criteria, and guardrails.
- `docs/github_labels.json`: GitHub label manifest used by community issue checks and optional `gh` sync.
- `docs/demo_video_script.md`: short video/GIF script.
- `docs/demo_recording_checklist.md`: operational checklist for recording the first demo video or GIF.
- `docs/star_growth_plan.md`: plan for distribution and feedback loops.
- `docs/launch_copy_pack.md`: copy-ready launch posts for GitHub, LinkedIn, X, Hacker News, and communities.
- `docs/differentiation_strategy.md`: why this differs from ordinary AI demos.
- `docs/assets/demo-walkthrough.gif`: README walkthrough animation for the core demo flows.
- `docs/assets/github-preview.png`: upload-ready GitHub social preview image.

Architecture decisions:

- `docs/adr_0001_local_first_portfolio.md`: local-first reference runtime decision.
- `docs/adr_0002_model_is_not_security_boundary.md`: security boundaries live outside the model.
- `docs/adr_0003_eval_state_isolated_from_demo_state.md`: evals do not mutate live demo state.

Visual assets:

- `docs/assets/github-preview.svg`
- `docs/assets/github-preview.png`
- `docs/assets/architecture-overview.svg`
- `docs/assets/secure-knowledge-copilot-screenshot.png`
- `docs/assets/secure-knowledge-copilot-mobile.png`
- `docs/assets/regulated-ops-agent-screenshot.png`
- `docs/assets/regulated-ops-agent-mobile.png`
- `docs/assets/ai-reliability-incident-console-screenshot.png`
- `docs/assets/ai-reliability-incident-console-mobile.png`

## Project 1 Contents

Path: `secure-enterprise-knowledge-copilot`

Important files:

- `app.py`: Python HTTP server and API routes.
- `src/copilot/api.py`: application API layer for HTTP-facing use cases.
- `src/copilot/retrieval.py`: role-aware retrieval and evidence selection.
- `src/copilot/security.py`: unsafe retrieved-content detection.
- `src/copilot/answering.py`: answer shaping, citation behavior, abstention.
- `src/copilot/storage.py`: thread-safe JSON state, traces, audit log.
- `src/copilot/evals.py`: golden eval definitions and assertions.
- `src/copilot/model_gateway.py`: optional OpenAI Responses API path.
- `scripts/run_eval.py`: project-level eval runner using isolated eval state.
- `web/index.html`, `web/styles.css`, `web/js/*`: modular browser demo UI split into API client, DOM helpers, clipboard helper, scenario draft helper, renderers, and app orchestration.
- `data/seed_documents.json`: seed knowledge base.
- `data/eval_cases.json`: eval cases.
- `docs/architecture.md`: project architecture.
- `docs/threat_model.md`: threat model and security assumptions.
- `docs/demo_script.md`: exact project demo script.
- `docs/technical_review_notes.md`: project review notes.
- `docs/implementation_status.md`: implementation notes.

Key demo claims:

- Users only retrieve evidence they are authorized to see.
- The model is never treated as the permission boundary.
- Unsupported or unsafe answers abstain instead of guessing.
- Eval cases prove normal answers, denied access, injection handling, and unknown-question abstention.

## Project 2 Contents

Path: `regulated-customer-operations-agent`

Important files:

- `app.py`: Python HTTP server and API routes.
- `src/ops_agent/api.py`: application API layer for HTTP-facing use cases.
- `src/ops_agent/agent.py`: workflow planning and response assembly.
- `src/ops_agent/tools.py`: deterministic business tools and side-effect guards.
- `src/ops_agent/storage.py`: thread-safe JSON state, traces, audit log, approvals.
- `src/ops_agent/evals.py`: golden eval definitions and assertions.
- `src/ops_agent/model_gateway.py`: optional OpenAI Responses API path.
- `scripts/run_eval.py`: project-level eval runner using isolated eval state.
- `web/index.html`, `web/styles.css`, `web/js/*`: modular browser demo UI split into API client, DOM helpers, clipboard helper, scenario draft helper, renderers, and app orchestration.
- `data/seed_state.json`: seeded operations state.
- `data/eval_cases.json`: eval cases.
- `docs/architecture.md`: project architecture.
- `docs/threat_model.md`: threat model and safety assumptions.
- `docs/demo_script.md`: exact project demo script.
- `docs/technical_review_notes.md`: project review notes.
- `docs/implementation_status.md`: implementation notes.

Key demo claims:

- The agent can propose operational actions.
- Direct side effects are blocked unless the application authorization layer allows them.
- Investigator role creates approval requests; supervisor role executes approved actions.
- Eval cases prove investigation flow, approval requirement, bypass refusal, escalation approval, and irrelevant-query no-op behavior.

## Project 3 Contents

Path: `ai-reliability-incident-console`

Important files:

- `app.py`: Python HTTP server and API routes.
- `src/reliability_console/api.py`: application API layer for HTTP-facing release reliability use cases.
- `src/reliability_console/triage.py`: deterministic incident triage and rollout-blocking logic.
- `src/reliability_console/storage.py`: thread-safe JSON state, traces, audit log, and triage decisions.
- `src/reliability_console/evals.py`: golden eval definitions and assertions.
- `scripts/run_eval.py`: project-level eval runner using reset local state.
- `web/index.html`, `web/styles.css`, `web/js/*`: modular browser demo UI split into API client, DOM helpers, clipboard helper, scenario draft helper, renderers, and app orchestration.
- `data/seed_state.json`: fictional release, incident, eval, and runbook data.
- `data/eval_cases.json`: eval cases.
- `docs/architecture.md`: project architecture.
- `docs/threat_model.md`: threat model and safety assumptions.
- `docs/demo_script.md`: exact project demo script.
- `docs/technical_review_notes.md`: project review notes.
- `docs/implementation_status.md`: implementation notes.

Key demo claims:

- High-risk incidents linked to failed evals block rollout.
- Latency-only incidents can stay monitor-only without weakening safety gates.
- Triage decisions produce trace and audit evidence.
- Eval cases prove unsafe rollout blocking and monitor-only behavior.

## Optional OpenAI Mode

Default mode is deterministic and local-first. Optional OpenAI integration exists but is disabled by default.

Environment controls:

```powershell
$env:OPENAI_API_KEY="..."
$env:OPENAI_MODEL="gpt-5.2"
$env:COPILOT_MODEL_PROVIDER="openai"
$env:OPS_AGENT_MODEL_ROUTER="openai"
```

Important boundary:

- OpenAI mode changes generation/routing behavior only.
- Permission checks, retrieved-content filtering, approval gates, audit logging, and eval expectations remain in application code.

## Remaining External Blockers

These are not local code blockers, but they should not be claimed as completed until verified:

1. Add repository description, topics, branch protection, and social preview in GitHub settings.
2. Create a GitHub release page for `v0.1.0`.
3. Run `python -B scripts/dev.py docker-runtime` on a Docker-enabled machine; the static container release hygiene gate is already included.
4. Verify optional OpenAI mode with a valid API key by running `python -B scripts/dev.py openai-live`.
5. Record an optional narrated demo video; the README GIF is already included.
6. Collect real launch feedback and star-growth evidence.

## System Narrative

Use this compact framing:

```text
Three local-first enterprise AI systems demonstrate controls around the model rather than only chatbot behavior. The first proves secure RAG with permission filtering, citations, abstention, prompt-injection handling, traces, audit logs, and evals. The second proves governed agentic workflow automation with deterministic tools, approval gates, blocked side effects, supervisor execution, traces, audit logs, and evals. The third proves AI release reliability with canary incident triage, linked eval regressions, rollout blocking, remediation plans, traces, audit logs, and evals. The key design principle is that the model is not the security boundary; application code enforces permissions, side effects, and rollout decisions, while evals prove the expected behavior.
```
