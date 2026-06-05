# Branch Protection Verification Examples

Use this page when checking whether `main` branch protection is actually active on GitHub. Read it with `docs/github_repository_settings.md`, `docs/github_branch_protection.json`, `docs/stale_branch_protection_screenshot_examples.md`, `docs/published_repository_status.md`, and `docs/post_publish_checklist.md`.

The core rule: `docs/github_branch_protection.json` is the desired policy payload. It is not proof that GitHub has applied that policy. Keep branch-protection wording manual until `python -B scripts/dev.py github-readiness` or account-level evidence confirms the remote state.

## Expected Protection Shape

The tracked payload should require:

- `quality-gate` status checks
- up-to-date branches before merge
- admin enforcement
- at least one approving review
- stale review dismissal
- code-owner reviews
- last-push approval
- conversation resolution
- no force pushes
- no branch deletion

Local static validation:

```bash
python -B scripts/dev.py governance
```

Remote readiness validation:

```bash
python -B scripts/dev.py github-readiness
```

Use strict mode only when account-level launch setup is expected to be complete:

```bash
python -B scripts/check_github_readiness.py --strict
```

## Missing Protection

Symptom:

- `github-readiness` prints `[WARN] main branch protection enabled: not protected`.
- `docs/published_repository_status.md` still lists branch protection under manual work.
- GitHub lets direct pushes or merges happen without the expected checks.

Wrong fix:

- Edit README wording to claim the remote policy is already active.
- Treat `docs/github_branch_protection.json` as remote proof.
- Remove the warning from readiness output.

Safe fix:

```bash
python -B scripts/dev.py governance
python -B scripts/dev.py github-maintenance
python -B scripts/dev.py github-readiness
```

After authentication, apply the account-level setup:

```bash
python -B scripts/maintain_github_state.py --apply --skip-release
```

Only claim protection after GitHub readiness or direct account evidence confirms it.

Use `docs/stale_branch_protection_screenshot_examples.md` before treating old branch-rule screenshots, wrong branch names, API warning rows, inherited organization policy screenshots, or private account UI crops as current branch-protection evidence.

## Stale Payloads

Symptom:

- `docs/github_branch_protection.json` changed, but `github-readiness` still reports the old remote state.
- `docs/github_repository_settings.md` describes one policy while the JSON payload describes another.
- CODEOWNERS coverage changes without a matching governance check.

Wrong fix:

- Update only the prose docs.
- Bypass `python -B scripts/dev.py governance` because the remote warning is manual.

Safe fix:

```bash
python -B scripts/dev.py governance
python -B scripts/dev.py pr-policy
python -B scripts/dev.py workflow-security
```

Treat payload changes as repository policy changes. Review `docs/github_branch_protection.json`, `.github/CODEOWNERS`, `.github/pull_request_template.md`, and `.github/dependabot.yml` together.

## API Warning Rows

Symptom:

- `github-readiness` reports `[WARN]` for branch protection, API rate limits, pending Actions, metadata, release page, social preview, or profile pin.
- The command exits successfully without `--strict`.
- A reviewer is unsure whether the warning blocks a local docs change.

Wrong fix:

- Treat all warnings as failures for every local docs edit.
- Treat all warnings as proof that setup is complete.
- Hide warning rows from public release notes.

Safe fix:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/dev.py safety
```

In non-strict mode, warnings identify account-level or remote-freshness follow-up. In strict mode, warnings become blockers for launch-complete claims.

## Manual Account Settings

Symptom:

- `github-readiness` returns `[MANUAL] social preview configured` or `[MANUAL] profile repository pin configured`.
- Branch protection is still listed with metadata, topics, release page, social preview, or profile pin work.
- A launch note says GitHub setup is complete even though manual rows remain.

Wrong fix:

- Claim full GitHub readiness from local quality output.
- Mark manual account settings done in docs before applying them.

Safe fix:

```bash
python -B scripts/dev.py github-maintenance
python -B scripts/dev.py github-readiness
```

Keep the wording specific: local governance is validated; remote account settings remain manual until applied and checked.

## Post-Publish Mismatch

Symptom:

- Local docs mention branch protection examples, but the pushed branch does not contain the page.
- `python -B scripts/post_publish_check.py` fails for a required published file.
- The remote `main` branch is behind local `HEAD`.

Wrong fix:

- Use local `fresh-clone-local` as proof that GitHub has the page.
- Remove the new page from post-publish checks.

Safe fix:

```bash
python -B scripts/dev.py fresh-clone-local
python -B scripts/dev.py fresh-clone
python -B scripts/post_publish_check.py
python -B scripts/dev.py github-readiness
```

Before push, local-only checks prove the source tree is ready. After push, remote checks prove GitHub has the files and account-level state.

## Review Checklist

- `python -B scripts/dev.py governance` passes for the tracked policy payload.
- `docs/stale_branch_protection_screenshot_examples.md` is used before stale branch-protection screenshots become a public claim.
- `python -B scripts/dev.py github-readiness` has no hard failures in non-strict mode.
- Branch-protection claims stay manual until remote evidence confirms them.
- `docs/github_branch_protection.json` stays aligned with `docs/github_repository_settings.md`.
- CODEOWNERS and PR review policy are reviewed with branch-protection changes.
- Post-publish checks prove this page is present on GitHub after a push.
