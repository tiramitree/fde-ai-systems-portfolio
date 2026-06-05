# Stale GitHub Actions Badge Cache Examples

Use this page when old badge images, wrong workflow badge URLs, skipped workflow badges, fork-PR badge confusion, or private account UI crops may no longer prove the current GitHub Actions state. Read it with `docs/github_actions_badge_verification_examples.md`, `docs/github_actions_warning_examples.md`, `docs/post_publish_warning_examples.md`, and `docs/post_publish_checklist.md`.

The core rule: local quality output, remote workflow runs, README badge URLs, cached badge images, fork PR context, account UI screenshots, and source docs prove different things. Do not claim the workflow badge is current until the current remote `quality-gate` run and badge evidence confirm it.

The stale evidence set includes old badge images, wrong workflow badge URLs, skipped workflow badges, fork-PR badge confusion, and private account UI crops.

## Expected Evidence Split

Local quality evidence:

```bash
python -B scripts/dev.py workflow-security
python -B scripts/dev.py quality
python -B scripts/dev.py fresh-clone-local
```

Remote workflow evidence after push:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/dev.py fresh-clone
python -B scripts/post_publish_check.py
```

Badge URL evidence:

```text
https://github.com/tiramitree/fde-ai-systems-portfolio/actions/workflows/ci.yml/badge.svg
https://github.com/tiramitree/fde-ai-systems-portfolio/actions/workflows/ci.yml
```

Use `docs/github_actions_badge_verification_examples.md` to verify the current README badge URL and linked workflow page. Keep workflow badge claims manual until the current remote run, Actions page, README badge URL, and rendered badge evidence agree.

## Old Badge Images

Symptom:

- A copied README screenshot shows a green `Quality Gate` badge.
- `github-readiness` reports a pending, missing, or stale current workflow run.
- The screenshot was taken before the latest push.

Wrong fix:

- Treat the old screenshot as current workflow evidence.
- Replace remote readiness output with the copied screenshot.
- Claim a green workflow badge from a cached image.

Safe fix:

```bash
git rev-parse HEAD
git ls-remote origin refs/heads/main
python -B scripts/dev.py github-readiness
```

Keep the screenshot as historical context only. A badge image is current evidence only when it matches the current remote commit and the current `quality-gate` run.

## Wrong Workflow Badge URLs

Symptom:

- The badge image URL points to another workflow file, branch, repository, or owner.
- The badge label says `Quality Gate`, but the linked Actions page does not show `.github/workflows/ci.yml`.
- The rendered badge is green while `github-readiness` checks a different workflow.

Wrong fix:

- Rename `.github/workflows/ci.yml` only to match the badge.
- Point the badge at another repository with a passing workflow.
- Hide the mismatch in launch copy or status docs.

Safe fix:

```bash
python -B scripts/dev.py workflow-security
python -B scripts/dev.py github-readiness
```

Use the tracked workflow file as the source of truth. The README badge image URL and link should both target `actions/workflows/ci.yml` for this repository.

## Skipped Workflow Badges

Symptom:

- The badge exists, but the current pushed commit has no completed `quality-gate` run.
- The workflow was skipped, disabled, pending, or blocked by repository-level Actions settings.
- A stale green badge remains visible from an older run.

Wrong fix:

- Claim the workflow badge is current because a previous run was green.
- Broaden CI permissions, add secrets, or use `pull_request_target` to force richer public PR behavior.
- Remove the stale badge warning from status docs.

Safe fix:

```bash
python -B scripts/dev.py workflow-security
python -B scripts/dev.py governance
python -B scripts/dev.py github-readiness
```

Keep `.github/workflows/ci.yml` least-privileged. Treat skipped or blocked workflow runs as remote/account-level evidence gaps until the current run completes.

## Fork-PR Badge Confusion

Symptom:

- A fork PR has a failed, pending, skipped, or permission-limited workflow.
- The default-branch README badge still appears green.
- A reviewer or contributor treats the default-branch badge as PR approval evidence.

Wrong fix:

- Approve a public PR because the default-branch badge is green.
- Give fork PR workflows write tokens or secrets.
- Skip file-level review because the README badge looks good.

Safe fix:

```bash
python -B scripts/dev.py pr-triage
python -B scripts/dev.py pr-policy
python -B scripts/dev.py workflow-security
```

Default-branch badge state and public PR review state are separate. Public PRs remain untrusted input until workflow changes, dependency changes, and diff-level risks are reviewed.

## Private Account UI Crops

Symptom:

- A private account screenshot shows Actions settings, notification badges, or workflow status.
- The crop includes account menus, profile details, private repository lists, browser profile data, or token-adjacent UI.
- The screenshot does not prove what a public reviewer can see.

Wrong fix:

- Commit private account screenshots as badge evidence.
- Use a private Actions settings crop as public workflow proof.
- Expose local paths, account names, browser profile details, or tokens in docs.

Safe fix:

```bash
python -B scripts/dev.py safety
python -B scripts/dev.py github-readiness
python -B scripts/dev.py launch-assets
```

Private account screenshots, account menus, notifications, private repository lists, local paths, browser profile details, and tokens are not committed. Use public workflow pages, current readiness output, and safe status wording instead.

## Review Checklist

- `docs/github_actions_badge_verification_examples.md` remains the source for current README badge URL and workflow evidence.
- Old badge images, wrong workflow badge URLs, skipped workflow badges, fork-PR badge confusion, and private account UI crops are not treated as current workflow evidence.
- Local quality output, remote workflow runs, README badge URLs, cached badge images, fork PR context, account UI screenshots, and source docs stay separate.
- Badge screenshots are review aids; they do not replace GitHub readiness output, the current Actions page, or the current remote `quality-gate` run.
- Private account screenshots, account menus, notifications, private repository lists, local paths, browser profile details, and tokens are not committed.
- `python -B scripts/dev.py workflow-security` passes before changing workflow or badge wording.
- `python -B scripts/dev.py github-readiness` remains the public/account-level follow-up command.
- `python -B scripts/dev.py launch-assets` passes before public launch copy references badge evidence.
- `python -B scripts/dev.py safety` passes before publishing docs.
- `python -B scripts/dev.py quality` passes before push-facing work.
- `python -B scripts/post_publish_check.py` is used only after the intended push is visible.
