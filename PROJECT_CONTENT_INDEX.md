# Project Content Index

This file is the compact map of the portfolio. Use it when context is lost, when preparing a demo, or before publishing the repository.

## Current Scope

The repository contains two runnable FDE-style AI systems:

1. `secure-enterprise-knowledge-copilot`
   - Demonstrates permission-aware enterprise RAG.
   - Core behaviors: retrieval filtering, citations, abstention, prompt-injection detection, traces, audit logs, golden evals.
   - Local URL: `http://127.0.0.1:8765`

2. `regulated-customer-operations-agent`
   - Demonstrates governed tool-calling workflow automation.
   - Core behaviors: intent routing, operational tools, approval queue, side-effect blocking, supervisor approval, traces, audit logs, golden evals.
   - Local URL: `http://127.0.0.1:8770`

The design target is not "chatbot demo". The design target is an interview-ready and GitHub-ready portfolio showing how to build AI systems around model calls: product workflow, safety boundaries, evals, observability, and deployment paths.

## How To Run

From the repository root:

```bash
python -B scripts/dev.py verify
python -B scripts/dev.py start
python -B scripts/dev.py health
python -B scripts/dev.py evals
python -B scripts/dev.py smoke
python -B scripts/dev.py report
python -B scripts/dev.py quality
```

Verified local demo URLs:

- Secure Enterprise Knowledge Copilot: `http://127.0.0.1:8765`
- Regulated Customer Operations Agent: `http://127.0.0.1:8770`

## Verified State

Latest local verification:

```text
python -B scripts/dev.py verify
```

Result:

- both services healthy
- Project 1 eval: 7/7 passed, unsafe leaks 0
- Project 2 eval: 5/5 passed, unsafe direct side-effect failures 0
- smoke tests: 9/9 passed
- demo report generated
- quality gate passed

Local Git state:

- repository initialized
- default branch: `main`
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

- `scripts/dev.py`: single developer entrypoint for start, health, evals, smoke, report, quality, verify.
- `scripts/start_demo_servers.py`: starts both local demos.
- `scripts/check_health.py`: verifies both service health endpoints.
- `scripts/run_all_evals.py`: runs both project eval suites.
- `scripts/smoke_test_demo_flows.py`: exercises the critical demo paths end to end.
- `scripts/generate_demo_report.py`: writes `docs/demo_report.md`.
- `scripts/quality_gate.py`: local release gate.
- `scripts/ci_quality_gate.py`: clean-checkout CI gate for GitHub Actions.

## GitHub Assets

- `.github/workflows/ci.yml`: GitHub Actions workflow.
- `.github/pull_request_template.md`: PR checklist.
- `.github/ISSUE_TEMPLATE/bug_report.md`: bug report template.
- `.github/ISSUE_TEMPLATE/eval_case.md`: eval regression template.
- `.github/ISSUE_TEMPLATE/feature_request.md`: feature request template.

## Portfolio Docs

Start here:

- `docs/final_demo_runbook.md`: exact live demo order.
- `docs/demo_report.md`: generated verification report.
- `docs/completion_checklist.md`: current status and remaining blockers.
- `docs/final_completion_audit.md`: objective-by-objective audit.

Interview preparation:

- `docs/resume_and_interview_package.md`: resume bullets and interview framing.
- `docs/hard_interview_playbook.md`: difficult interviewer questions and answers.
- `docs/system_design_deep_dive.md`: architecture reasoning and tradeoffs.
- `docs/model_runtime_configuration.md`: optional OpenAI model, reasoning effort, verbosity, and structured-output configuration.
- `docs/portfolio_evidence_matrix.md`: claim-to-evidence map for reviewers and interviewers.
- `docs/case_study_secure_enterprise_knowledge_copilot.md`: Project 1 case study.
- `docs/case_study_regulated_customer_operations_agent.md`: Project 2 case study.

Release and growth:

- `docs/public_release_audit.md`: public-readiness audit.
- `docs/reviewer_perspective_checklist.md`: checks from user and interviewer perspectives.
- `docs/github_launch_plan.md`: launch sequence.
- `docs/github_repository_settings.md`: repository description, topics, social preview, branch protection, and first-release settings.
- `docs/github_release_commands.md`: publication commands.
- `docs/community_backlog.md`: first public issue backlog and contribution guardrails.
- `docs/github_initial_issues.md`: initial issue titles, labels, and bodies for launch.
- `docs/demo_video_script.md`: short video/GIF script.
- `docs/demo_recording_checklist.md`: operational checklist for recording the first demo video or GIF.
- `docs/star_growth_plan.md`: plan for distribution and feedback loops.
- `docs/launch_copy_pack.md`: copy-ready launch posts for GitHub, LinkedIn, X, Hacker News, and communities.
- `docs/differentiation_strategy.md`: why this differs from ordinary AI demos.

Architecture decisions:

- `docs/adr_0001_local_first_portfolio.md`: local-first runtime decision.
- `docs/adr_0002_model_is_not_security_boundary.md`: security boundaries live outside the model.
- `docs/adr_0003_eval_state_isolated_from_demo_state.md`: evals do not mutate live demo state.

Visual assets:

- `docs/assets/github-preview.svg`
- `docs/assets/architecture-overview.svg`
- `docs/assets/secure-knowledge-copilot-screenshot.png`
- `docs/assets/regulated-ops-agent-screenshot.png`

## Project 1 Contents

Path: `secure-enterprise-knowledge-copilot`

Important files:

- `app.py`: Python HTTP server and API routes.
- `src/copilot/retrieval.py`: role-aware retrieval and evidence selection.
- `src/copilot/security.py`: unsafe retrieved-content detection.
- `src/copilot/answering.py`: answer shaping, citation behavior, abstention.
- `src/copilot/storage.py`: thread-safe JSON state, traces, audit log.
- `src/copilot/evals.py`: golden eval definitions and assertions.
- `src/copilot/model_gateway.py`: optional OpenAI Responses API path.
- `scripts/run_eval.py`: project-level eval runner using isolated eval state.
- `web/index.html`, `web/styles.css`, `web/app.js`: browser demo UI.
- `data/seed_documents.json`: seed knowledge base.
- `data/eval_cases.json`: eval cases.
- `docs/architecture.md`: project architecture.
- `docs/threat_model.md`: threat model and security assumptions.
- `docs/demo_script.md`: exact project demo script.
- `docs/interview_talking_points.md`: talking points for interviews.
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
- `src/ops_agent/agent.py`: workflow planning and response assembly.
- `src/ops_agent/tools.py`: deterministic business tools and side-effect guards.
- `src/ops_agent/storage.py`: thread-safe JSON state, traces, audit log, approvals.
- `src/ops_agent/evals.py`: golden eval definitions and assertions.
- `src/ops_agent/model_gateway.py`: optional OpenAI Responses API path.
- `scripts/run_eval.py`: project-level eval runner using isolated eval state.
- `web/index.html`, `web/styles.css`, `web/app.js`: browser demo UI.
- `data/seed_state.json`: seeded operations state.
- `data/eval_cases.json`: eval cases.
- `docs/architecture.md`: project architecture.
- `docs/threat_model.md`: threat model and safety assumptions.
- `docs/demo_script.md`: exact project demo script.
- `docs/interview_talking_points.md`: talking points for interviews.
- `docs/implementation_status.md`: implementation notes.

Key demo claims:

- The agent can propose operational actions.
- Direct side effects are blocked unless the application authorization layer allows them.
- Investigator role creates approval requests; supervisor role executes approved actions.
- Eval cases prove investigation flow, approval requirement, bypass refusal, escalation approval, and irrelevant-query no-op behavior.

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

1. Add a GitHub remote and push `main`.
2. Replace the static quality badge with a real Actions badge after publishing.
3. Confirm GitHub Actions is green on the published repository.
4. Verify Docker Compose on a machine with Docker installed.
5. Verify optional OpenAI mode with a valid API key.
6. Record and include a short demo GIF/video.
7. Collect real launch feedback and star-growth evidence.

## Interview Narrative

Use this compact framing:

```text
I built two local-first enterprise AI systems around the model rather than just a chatbot. The first proves secure RAG with permission filtering, citations, abstention, prompt-injection handling, traces, audit logs, and evals. The second proves governed agentic workflow automation with deterministic tools, approval gates, blocked side effects, supervisor execution, traces, audit logs, and evals. The key design principle is that the model is not the security boundary; application code enforces permissions and side effects, while evals prove the expected behavior.
```
