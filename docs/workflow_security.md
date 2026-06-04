# Workflow Security

Public repositories receive untrusted pull requests. The CI workflow is intentionally small and least-privileged so external code can be checked without giving it write credentials or repository secrets.

Run the workflow security gate with:

```bash
python -B scripts/dev.py workflow-security
```

Use `docs/github_actions_warning_examples.md` when GitHub Actions or `github-readiness` reports pending, missing, skipped, stale, or fork-permission workflow states.

## CI Contract

The GitHub Actions workflow keeps these rules:

- use `pull_request`, not `pull_request_target`
- declare `permissions: contents: read`
- set `actions/checkout` `persist-credentials: false`
- use only approved first-party GitHub actions
- use only approved action major refs for those actions
- do not reference `secrets.*`
- do not authenticate `gh` inside CI
- do not push from CI
- do not download scripts and pipe them into a shell
- do not use encoded or expression-executing PowerShell commands

The workflow may run contributor code through the project quality gate, but it does so with a read-only token and no secrets.

## Why This Matters

The repository is meant to be public and reviewable. If a public PR changes workflow privileges, adds hidden dependency installation, or exfiltrates secrets, a green CI badge would become misleading. The workflow security gate makes those changes visible before merge.

The gate complements:

- `python -B scripts/dev.py pr-triage` for remote PR diff triage
- `python -B scripts/dev.py governance` for CODEOWNERS and branch-protection payload checks
- `python -B scripts/dev.py safety` for public content and secret-like artifact scanning
- `python -B scripts/dev.py verify` for runtime, eval, smoke, and quality evidence

## Maintainer Rule

External PR workflow runs should be approved only after reading the diff. Any PR that changes `.github/workflows/`, `scripts/dev.py`, `scripts/quality_gate.py`, `scripts/ci_quality_gate.py`, safety scans, launch asset checks, dependency policy, or model/security boundaries requires high scrutiny even if the automated check is green.
