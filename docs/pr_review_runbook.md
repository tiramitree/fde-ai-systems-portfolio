# Pull Request Review Runbook

Use this before approving external PR workflows, running contributor code, or merging a public contribution.

For recurring PR, GitHub, and local-environment problems, also check `docs/development_issue_solutions.md` and `docs/github_authenticated_maintenance_troubleshooting_examples.md` before changing code.

## Fast Path

```bash
python -B scripts/dev.py github-maintenance
python -B scripts/dev.py pr-triage
python -B scripts/dev.py governance
python -B scripts/dev.py workflow-security
python -B scripts/dev.py safety
python -B scripts/dev.py verify
```

For one PR:

```bash
python -B scripts/review_open_prs.py --pr 6
```

Use strict mode when you want automation to fail on high-risk findings:

```bash
python -B scripts/review_open_prs.py --strict
```

If unauthenticated GitHub API rate limits are hit, the script falls back to the public pulls page to detect whether any open PRs are visible. Authenticate with `gh auth login` before reviewing or merging if the API cannot provide full file-level triage.

Authenticated repository maintenance is dry-run by default:

```bash
python -B scripts/maintain_github_state.py
```

After `gh auth login`, close guarded Dependabot Docker runtime-baseline PRs only through the exact matching rule:

```bash
python -B scripts/maintain_github_state.py --apply --skip-launch --close-runtime-bump-prs
```

## Review Order

1. Read the PR title, author, changed files, and automated triage findings.
2. Read the diff before running code.
3. Treat workflow changes, safety-gate changes, dependency changes, shell commands, environment access, outbound network calls, and binary files as high scrutiny.
4. Treat Docker runtime baseline bumps as coordinated release-policy work, not as routine dependency updates.
5. Run local safety and verify gates only after the diff review is clean.
6. Merge only if the change strengthens a public repository claim, closes a real issue, or improves reliability without weakening governance.

## Close Or Ignore

Close, ignore, or mark spam when a PR:

- asks for secrets, tokens, local files, account credentials, or collaborator access
- weakens permission checks, approval gates, traces, audit logs, evals, or public safety scans
- adds hidden network calls, install scripts, binaries, or obfuscated code
- changes CI to hide failures or bypass quality gates
- changes the pinned Python container runtime baseline without updating release policy, docs, and verification evidence
- is unrelated to the repository purpose

## Merge Bar

Before merge:

- `python -B scripts/dev.py pr-triage` has no unresolved high-risk finding.
- `python -B scripts/dev.py governance` passes.
- `python -B scripts/dev.py workflow-security` passes.
- `python -B scripts/dev.py safety` passes.
- `python -B scripts/dev.py verify` passes.
- GitHub Actions is green.
- The diff is narrow and explainable in technical review terms.
