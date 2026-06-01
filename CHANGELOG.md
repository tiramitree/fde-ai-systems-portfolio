# Changelog

All notable changes to this repository will be documented here.

## 0.1.0 - 2026-06-01

Initial public-ready portfolio release.

### Added

- Secure Enterprise Knowledge Copilot:
  - permission-aware retrieval
  - citation-based answers
  - abstention for inaccessible or unsupported questions
  - retrieved-content prompt-injection detection
  - trace and audit surfaces
  - golden eval suite

- Regulated Customer Operations Agent:
  - governed tool-calling workflow
  - deterministic business tools
  - side-effect blocking
  - approval queue
  - supervisor approval execution
  - trace and audit surfaces
  - golden eval suite

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
- Secure Enterprise Knowledge Copilot evals pass 7/7 with unsafe leaks 0.
- Regulated Customer Operations Agent evals pass 5/5 with unsafe direct side-effect failures 0.
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
