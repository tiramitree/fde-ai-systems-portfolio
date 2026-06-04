# GitHub Authenticated Maintenance Troubleshooting Examples

Use this page when authenticated GitHub maintenance is unclear. Read it with `docs/github_repository_settings.md`, `docs/post_publish_checklist.md`, `docs/post_publish_warning_examples.md`, `docs/public_maintainer_status_update_examples.md`, `docs/pr_review_runbook.md`, `docs/maintainer_review_policy.md`, and `docs/command_output_troubleshooting_map.md`.

The core rule: dry-run planning, authenticated account permissions, repository metadata changes, and PR maintenance prove different things. Do not claim remote maintenance applied until authenticated evidence confirms it.

## Expected Evidence Split

Local planning evidence:

```bash
python -B scripts/dev.py github-maintenance
python -B scripts/dev.py github-readiness
```

Authenticated apply path:

```bash
python -B scripts/maintain_github_state.py --apply
python -B scripts/dev.py github-readiness
python -B scripts/dev.py pr-triage
```

Safety review path:

```bash
python -B scripts/dev.py pr-policy
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

The default maintenance command prints a plan. It does not mutate GitHub. Apply commands need an authenticated maintainer account, the intended repository remote, and a follow-up readiness or PR-triage check.

## Missing gh Auth

Symptom:

- `python -B scripts/dev.py github-maintenance` prints a dry-run plan.
- `python -B scripts/maintain_github_state.py --apply` reports that GitHub CLI is not authenticated.
- GitHub readiness still shows metadata, branch protection, release page, social preview, or profile pin warnings.

Wrong fix:

- Add token values, account screenshots, or private auth instructions to public docs.
- Treat dry-run output as applied setup.
- Remove readiness warning rows so the repository looks complete.

Safe fix:

```bash
python -B scripts/dev.py github-maintenance
python -B scripts/dev.py github-readiness
```

Authenticate locally through a maintainer-controlled `gh auth login` flow when applying account-level work. Keep public docs free of token values, account identifiers, and private browser profile details.

## Wrong Account Or Repository

Symptom:

- `gh auth status` is authenticated, but the account cannot edit the intended repository.
- `git remote -v` points to a fork, stale test repository, or private remote.
- Maintenance output names a repository other than `tiramitree/fde-ai-systems-portfolio`.

Wrong fix:

- Apply settings to whichever repository the current remote names.
- Rewrite public docs to match an accidental fork.
- Ask contributors for collaborator access or account credentials.

Safe fix:

```bash
git remote -v
python -B scripts/dev.py github-maintenance
python -B scripts/dev.py github-readiness
```

Confirm the remote owner and repository before applying changes. Use `docs/github_repository_settings.md` as the source of truth for expected repository metadata and manual account settings.

## Dry-Run Versus Apply

Symptom:

- `python -B scripts/dev.py github-maintenance` lists commands for metadata, topics, branch protection, release setup, PR triage, and community labels.
- No command with `--apply` has been run.
- GitHub readiness still reports the same account-level warnings.

Wrong fix:

- Claim repository settings changed because the dry-run listed them.
- Use dry-run output as release or branch-protection evidence.
- Weaken `github-readiness` so planning output looks like remote proof.

Safe fix:

```bash
python -B scripts/dev.py github-maintenance
python -B scripts/maintain_github_state.py --apply
python -B scripts/dev.py github-readiness
```

Treat dry-run output as a reviewable plan. Treat `--apply` plus a fresh readiness check as the evidence path for remote repository settings.

Use `docs/public_maintainer_status_update_examples.md` before announcing that authenticated maintenance has been applied.

## Branch Protection Or Release Side Effects

Symptom:

- The maintainer wants metadata and topics, but not release creation.
- Branch protection should be applied without changing release state.
- The release page or latest-release state is still under manual review.

Wrong fix:

- Run the full apply path without considering release side effects.
- Claim release setup is complete from branch-protection evidence.
- Edit release docs to match an accidental remote side effect.

Safe fix:

```bash
python -B scripts/maintain_github_state.py --apply --skip-release
python -B scripts/dev.py github-readiness
```

Use the narrower authenticated path when release creation is not intended. Keep branch protection, release page, latest-release state, and release attachments as separate evidence rows.

## PR Maintenance Safeguards

Symptom:

- A public PR or Dependabot PR is open.
- The maintenance dry-run mentions guarded runtime-bump PR closure.
- The PR changes Dockerfiles, workflows, safety gates, or maintenance scripts.

Wrong fix:

- Close or merge PRs because a title looks familiar.
- Run contributor code before diff review.
- Apply broad PR cleanup without checking the exact guarded rule.

Safe fix:

```bash
python -B scripts/dev.py pr-triage
python -B scripts/review_open_prs.py --strict
python -B scripts/maintain_github_state.py --apply --skip-launch --close-runtime-bump-prs
```

Use `docs/pr_review_runbook.md` and `docs/maintainer_review_policy.md` before closing or merging public contributions. Guarded closure is only for exact Dependabot Docker runtime-baseline changes that match the scripted rule.

## Review Checklist

- `git remote -v` points to the intended public repository before apply.
- `python -B scripts/dev.py github-maintenance` is reviewed as dry-run planning.
- `python -B scripts/maintain_github_state.py --apply` is used only from an authenticated maintainer environment.
- `python -B scripts/dev.py github-readiness` is rerun after account-level changes.
- `python -B scripts/dev.py pr-triage` is rerun after PR-maintenance actions.
- `docs/github_repository_settings.md` remains the source of truth for expected metadata, branch protection, release, social preview, and profile pin setup.
- `docs/pr_review_runbook.md` and `docs/maintainer_review_policy.md` stay in force before any PR closure or merge.
- Public docs do not claim remote maintenance applied until authenticated evidence confirms it.
- Public maintainer updates separate dry-run planning, authenticated apply output, readiness evidence, and PR maintenance state.
