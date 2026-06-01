# Changelog

All notable changes to this repository will be documented here.

## Unreleased

### Added

- Modular backend API layers for both demo applications.
- Modular frontend ES modules for API calls, DOM helpers, renderers, and app orchestration.
- Public safety scan for secret-like content, local paths, private identifiers, and tracked runtime artifacts.
- Maintainer review policy for triaging external PRs, useful reviews, unsafe changes, and phishing attempts.
- CSV eval summary export through `python -B scripts/dev.py eval-csv`.
- Replayable demo reset command through `python -B scripts/dev.py replay`.
- Release-attachable demo replay artifact through `python -B scripts/dev.py replay-artifact`.
- Container release hygiene gate through `python -B scripts/dev.py container-release`.
- Fresh clone checks now include the container release hygiene gate.
- PostgreSQL and pgvector adapter design covering schema, migrations, RLS, indexing, eval isolation, and rollout risks.
- OpenTelemetry-compatible local trace export through `python -B scripts/dev.py otel-traces`.
- README demo walkthrough GIF under `docs/assets/demo-walkthrough.gif`.
- Upload-ready GitHub social preview PNG under `docs/assets/github-preview.png`.
- Public asset and Markdown-link quality check through `python -B scripts/dev.py assets`.
- Fresh clone experience check through `python -B scripts/dev.py fresh-clone`.
- GitHub public-readiness report through `python -B scripts/dev.py github-readiness`.
- API contract checks for UI-facing endpoints through `python -B scripts/dev.py contracts`.
- API documentation consistency gate through `python -B scripts/dev.py api-docs`.
- Final launch and interview readiness report through `python -B scripts/dev.py readiness-report`.
- Dry-run/apply GitHub launch setup for repository metadata, topics, branch protection, and first release through `python -B scripts/dev.py github-launch-setup`.
- Public PR triage and risky-diff review runbook through `python -B scripts/dev.py pr-triage`.
- Tracked GitHub branch-protection payload for `main` and readiness warning when protection is missing.
- CODEOWNERS and repository-governance gate through `python -B scripts/dev.py governance`.
- Public claim-consistency gate through `python -B scripts/dev.py claims`.
- Dependency-surface gate, Dependabot config, and digest-pinned Docker base images through `python -B scripts/dev.py dependency-surface`.
- GitHub readiness now checks the latest `main` push workflow run directly so Dependabot PR runs do not create false failures.
- GitHub launch setup now attempts secret scanning and push protection as a best-effort authenticated setup step.
- Frontend integrity gate through `python -B scripts/dev.py frontend`.
- GitHub readiness can prove the release tag through `git ls-remote` when unauthenticated GitHub API limits are exhausted.
- Runtime UI contract gate through `python -B scripts/dev.py ui-contracts`.
- Architecture boundary gate through `python -B scripts/dev.py architecture`.
- Workflow security gate through `python -B scripts/dev.py workflow-security`.
- Model gateway safety gate through `python -B scripts/dev.py model-gateway-safety`.
- Observability integrity gate through `python -B scripts/dev.py observability`.
- Threat model consistency gate through `python -B scripts/dev.py threat-model`.
- PR review policy gate through `python -B scripts/dev.py pr-policy`.
- Scenario data integrity gate through `python -B scripts/dev.py scenario-data`.
- Error hygiene gate through `python -B scripts/dev.py error-hygiene`.

### Verified

- GitHub Actions passed after frontend/backend modularization.
- External PR #6 was reviewed, tested, and merged safely.
- Replay command starts clean reset services and passed 10/10 demo evidence checks locally.

## 0.1.0 - 2026-06-01

Initial public-ready portfolio release.

### Added

- Secure Enterprise Knowledge Copilot:
  - permission-aware retrieval
  - citation-based answers
  - abstention for inaccessible or unsupported questions
  - retrieved-content prompt-injection detection
  - user-message prompt-injection rejection before retrieval
  - trace and audit surfaces
  - golden eval suite with red-team coverage for injection, exfiltration, and policy override attempts

- Regulated Customer Operations Agent:
  - governed tool-calling workflow
  - deterministic business tools
  - side-effect blocking
  - approval queue
  - supervisor approval execution
  - trace and audit surfaces
  - golden eval suite with red-team coverage for hidden side effects, approval override attempts, and non-supervisor approval attempts

- Portfolio-level release assets:
  - unified developer command wrapper
  - health checks, evals, smoke tests, demo report, and quality gate
  - GitHub Actions workflow
  - open-source contribution, security, conduct, roadmap, and issue templates
  - screenshots, architecture visuals, case studies, and interview docs
  - Dockerfiles and Docker Compose configuration
  - optional OpenAI model, reasoning effort, verbosity, and structured-output configuration
  - GitHub repository settings and community backlog
  - portfolio evidence matrix and initial GitHub issue templates
  - launch copy pack and demo recording checklist
  - post-publish verification script and checklist

### Verified

- Local Python runtime health checks pass for both services.
- Secure Enterprise Knowledge Copilot evals pass 11/11 with unsafe leaks 0.
- Regulated Customer Operations Agent evals pass 8/8 with unsafe direct side-effect failures 0.
- Portfolio smoke tests pass 9/9.
- Quality gate passes.

### Not Yet Verified

- Docker runtime on a Docker-enabled machine.
- Optional OpenAI mode with a live API key.

### Published

- Repository: https://github.com/tiramitree/fde-ai-systems-portfolio
- GitHub Actions `quality-gate`: passing
- Initial public issues: #1-#5
- Post-publish verification: passing
