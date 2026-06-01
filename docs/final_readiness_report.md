# Final Readiness Report

This file is the compact launch and interview status report for the portfolio.
Regenerate it with `python -B scripts/dev.py readiness-report` after meaningful publication or evidence changes.

## Executive Status

- Overall status: ready for technical review with manual launch blockers.
- The portfolio has two runnable enterprise AI systems with evals, traces, approval gates, API contracts, and public docs.
- The repository is suitable for interview walkthroughs after the commands below pass.
- Do not claim full launch completion until the manual/account and environment blockers are closed.

## Local Git Checks

Before publishing or interviewing from a fresh checkout:

```bash
git status --short
git rev-parse --abbrev-ref HEAD
git log -1 --oneline
```

Expected result: empty status output, branch `main`, and a latest commit that matches the pushed repository.

## Commands To Prove The Project

Run these from the repository root before sending the project to an interviewer or reviewer:

```bash
python -B scripts/dev.py verify
python -B scripts/dev.py replay
python -B scripts/dev.py eval-csv
python -B scripts/dev.py otel-traces
python -B scripts/dev.py github-readiness
python -B scripts/post_publish_check.py
```

Use strict GitHub readiness only when account-level setup is expected to be complete:

```bash
python -B scripts/check_github_readiness.py --strict
```

## GitHub Readiness

| Check | Status | Detail |
| --- | --- | --- |
| origin points to GitHub | PASS | https://github.com/tiramitree/fde-ai-systems-portfolio.git |
| GitHub repository metadata reachable | PASS | https://github.com/tiramitree/fde-ai-systems-portfolio |
| repository description set | WARN | missing |
| repository topics set | WARN | missing: agentic-workflows, ai-agents, ai-safety, enterprise-ai, forward-deployed-engineering, human-in-the-loop, llm-evals, openai, python, rag, responses-api, tool-calling |
| license detected as MIT | PASS | mit |
| default branch is main | PASS | main |
| stars observed at generation | PASS | 3 |
| forks observed at generation | PASS | 1 |
| main GitHub Actions run passed at generation | PASS | https://github.com/tiramitree/fde-ai-systems-portfolio/actions/runs/26768470906 |
| no open issues | PASS | 0 |
| no open PRs awaiting review | PASS | 0 |
| tag v0.1.0 exists | PASS | ok |
| GitHub release page exists for v0.1.0 | WARN | missing |
| social preview configured | MANUAL | GitHub does not expose a simple unauthenticated check; use docs/github_repository_settings.md |
| profile repository pin configured | MANUAL | Requires account profile settings |

## Remaining Blockers

- repository description set: missing
- repository topics set: missing: agentic-workflows, ai-agents, ai-safety, enterprise-ai, forward-deployed-engineering, human-in-the-loop, llm-evals, openai, python, rag, responses-api, tool-calling
- GitHub release page exists for v0.1.0: missing
- social preview configured: GitHub does not expose a simple unauthenticated check; use docs/github_repository_settings.md
- profile repository pin configured: Requires account profile settings
- Docker Compose runtime: not verified on this machine because Docker is not installed.
- Optional OpenAI live mode: not verified without a valid API key.
- Star growth: cannot be claimed as achieved until real launch feedback accumulates.

## Interview Walkthrough Order

1. Start with the README and evidence matrix to frame the two-system portfolio.
2. Run `python -B scripts/dev.py replay` to show the end-to-end demo path without relying on browser state.
3. Open Project 1 and show permission-aware retrieval, citations, abstention, and prompt-injection handling.
4. Open Project 2 and show investigation, approval queue, supervisor approval, trace, and audit log evidence.
5. Show `scripts/check_api_contracts.py`, eval files, and the safety scan to prove this is not only a UI demo.
6. Explain the upgrade path: OpenAI runtime adapters, PostgreSQL/pgvector design, OpenTelemetry export, Docker packaging, and approval governance.

## Quality Bar

- If `verify` fails, fix the failing local behavior before changing docs.
- If `github-readiness --strict` fails only on manual/account settings, do not call the launch complete.
- If an external PR appears, follow `docs/maintainer_review_policy.md` before merging.
- If generated runtime files appear in Git status, investigate `.gitignore` and the safety scan before publishing.
