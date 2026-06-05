# GitHub Actions Badge Verification Examples

Use this page when checking the README quality badge, GitHub Actions page, or `github-readiness` output. Read it with `.github/workflows/ci.yml`, `docs/github_actions_warning_examples.md`, `docs/stale_github_actions_badge_cache_examples.md`, `docs/post_publish_checklist.md`, `docs/post_publish_warning_examples.md`, `docs/workflow_security.md`, and `docs/command_output_troubleshooting_map.md`.

The core rule: local quality output, remote workflow status, skipped workflows, and README badge rendering prove different things. Do not claim a green workflow badge until the current remote `quality-gate` run is public and current.

## Expected Evidence Split

Local workflow safety evidence:

```bash
python -B scripts/dev.py workflow-security
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Remote workflow evidence:

```bash
python -B scripts/dev.py github-readiness
```

Published badge evidence after push:

```bash
python -B scripts/dev.py fresh-clone
```

The README badge URL should point to the tracked workflow file:

```text
https://github.com/tiramitree/fde-ai-systems-portfolio/actions/workflows/ci.yml/badge.svg
```

The badge link should point to the same workflow page:

```text
https://github.com/tiramitree/fde-ai-systems-portfolio/actions/workflows/ci.yml
```

## Missing Badge

Symptom:

- README has no `Quality Gate` badge.
- The workflow exists at `.github/workflows/ci.yml`.
- `github-readiness` can still find the latest `quality-gate` run.

Wrong fix:

- Add a static green image or success text.
- Link the badge to an unrelated workflow or repository.
- Claim badge evidence before the pushed README is visible.

Safe fix:

```bash
python -B scripts/dev.py workflow-security
python -B scripts/dev.py github-readiness
```

Add or restore the badge only when it points to `.github/workflows/ci.yml` in this repository. Keep the public claim tied to the current remote run, not the local badge markup.

## Stale Badge

Symptom:

- README badge renders an older state than the latest pushed commit.
- The Actions page and `github-readiness` disagree.
- A reviewer sees a green badge while readiness reports a pending or missing current run.

Wrong fix:

- Trust the rendered badge over the current commit check.
- Replace the badge with a static success claim.
- Remove `github-readiness` because the badge looks good.

Safe fix:

```bash
git rev-parse HEAD
git ls-remote origin refs/heads/main
python -B scripts/dev.py github-readiness
```

Use `github-readiness` for exact remote commit evidence. Treat badge rendering as presentation only until the badge, Actions page, and readiness output agree.

Use `docs/stale_github_actions_badge_cache_examples.md` before treating old badge images, wrong workflow badge URLs, skipped workflow badges, fork-PR badge confusion, or private account UI crops as current workflow evidence.

## Wrong Workflow Badge

Symptom:

- The README badge points to a workflow other than `ci.yml`.
- The badge label says `Quality Gate`, but the URL targets another workflow file, branch, or repository.
- The linked Actions page does not show the `quality-gate` workflow.

Wrong fix:

- Rename the workflow just to match a badge.
- Point the badge at a different public repository with a passing workflow.
- Hide the mismatch in launch copy.

Safe fix:

```bash
python -B scripts/dev.py workflow-security
python -B scripts/dev.py github-readiness
```

Use `.github/workflows/ci.yml` as the source of truth. The README badge URL and link should both target that workflow file.

## Skipped Workflow Badge

Symptom:

- The badge is visible, but the workflow run for the current remote commit was skipped or not triggered.
- The workflow still declares `push`, `pull_request`, and `workflow_dispatch`.
- `github-readiness` cannot find a successful current `quality-gate`.

Wrong fix:

- Claim a green badge from a previous run.
- Add secrets, write tokens, or `pull_request_target` to force richer CI behavior.
- Weaken the workflow-security gate.

Safe fix:

```bash
python -B scripts/dev.py workflow-security
python -B scripts/dev.py github-readiness
```

If the run is blocked by repository-level Actions settings, keep the badge claim manual until the account-level setting and current run are verified.

## Fork-PR Badge Confusion

Symptom:

- A fork PR has a failing, pending, or permission-limited workflow.
- The main README badge still reflects the default branch.
- A contributor assumes the badge proves their fork PR is safe to merge.

Wrong fix:

- Approve an external PR because the default-branch badge is green.
- Give public PR workflows secrets or write permissions.
- Treat the badge as a substitute for PR diff review.

Safe fix:

```bash
python -B scripts/dev.py pr-triage
python -B scripts/dev.py pr-policy
python -B scripts/dev.py workflow-security
```

The default-branch badge is not PR review evidence. Public PRs remain untrusted input until the diff, workflow changes, dependency changes, and relevant gates are reviewed.

## Review Checklist

- README keeps the `Quality Gate` badge pointed at `.github/workflows/ci.yml`.
- `.github/workflows/ci.yml` keeps the workflow name `quality-gate`.
- `.github/workflows/ci.yml` keeps `push`, `pull_request`, and `workflow_dispatch`.
- Workflow permissions remain `contents: read`.
- Checkout keeps `persist-credentials: false`.
- `python -B scripts/dev.py workflow-security` passes before changing badge or workflow wording.
- `python -B scripts/dev.py github-readiness` is used for current remote workflow evidence after push.
- `python -B scripts/dev.py quality` remains local prerequisite evidence, not remote badge evidence.
- Public docs do not claim a green workflow badge until the current remote `quality-gate` run is public and current.
- `docs/stale_github_actions_badge_cache_examples.md` is used before stale badge cache evidence becomes a public workflow claim.
