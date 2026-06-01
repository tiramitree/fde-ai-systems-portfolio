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
python -B scripts/dev.py governance
python -B scripts/dev.py observability
python -B scripts/dev.py otel-traces
python -B scripts/dev.py pr-triage
python -B scripts/dev.py github-launch-setup
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
| GitHub repository metadata reachable | WARN | API rate-limited; authenticate with GH_TOKEN, GITHUB_TOKEN, or gh auth login |

## Remaining Blockers

- GitHub repository metadata reachable: API rate-limited; authenticate with GH_TOKEN, GITHUB_TOKEN, or gh auth login
- repository description, topics, branch protection, release page, social preview, and profile pin still require authenticated verification.
- rerun `python -B scripts/dev.py github-readiness` with `GH_TOKEN`, `GITHUB_TOKEN`, or `gh auth login` before claiming GitHub launch completion.
- Docker Compose runtime: not verified on this machine because Docker is not installed.
- Optional OpenAI live mode: not verified without a valid API key.
- Star growth: cannot be claimed as achieved until real launch feedback accumulates.

Repository description, topics, branch protection, and the first release can be applied after `gh auth login` with:

```bash
python -B scripts/configure_github_launch.py --apply
```

## Interview Walkthrough Order

1. Start with the README and evidence matrix to frame the two-system portfolio.
2. Run `python -B scripts/dev.py replay` to show the end-to-end demo path without relying on browser state.
3. Open Project 1 and show permission-aware retrieval, citations, abstention, and prompt-injection handling.
4. Open Project 2 and show investigation, approval queue, supervisor approval, trace, and audit log evidence.
5. Run `python -B scripts/dev.py observability` to prove response trace IDs, audit events, approvals, and blocked actions line up.
6. Show `scripts/check_api_contracts.py`, eval files, and the safety scan to prove this is not only a UI demo.
7. Explain the upgrade path: OpenAI runtime adapters, PostgreSQL/pgvector design, OpenTelemetry export, Docker packaging, and approval governance.

## Quality Bar

- If `verify` fails, fix the failing local behavior before changing docs.
- If `github-readiness --strict` fails only on manual/account settings, do not call the launch complete.
- If an external PR appears, follow `docs/maintainer_review_policy.md` before merging.
- If generated runtime files appear in Git status, investigate `.gitignore` and the safety scan before publishing.
