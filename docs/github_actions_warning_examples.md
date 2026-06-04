# GitHub Actions Warning Examples

Use this page when GitHub Actions or `github-readiness` reports a workflow warning. Read it with `.github/workflows/ci.yml`, `docs/workflow_security.md`, `docs/post_publish_checklist.md`, `docs/post_publish_warning_examples.md`, `docs/github_api_rate_limit_troubleshooting_examples.md`, and `docs/command_output_troubleshooting_map.md`.

The core rule: local quality evidence and remote GitHub Actions evidence prove different things. Do not claim a green workflow until the current remote `quality-gate` run passes for the pushed commit.

## Expected Actions Evidence

Local proof before push:

```bash
python -B scripts/dev.py workflow-security
python -B scripts/dev.py quality
python -B scripts/dev.py fresh-clone-local
```

Remote proof after push:

```bash
python -B scripts/dev.py fresh-clone
python -B scripts/post_publish_check.py
python -B scripts/dev.py github-readiness
```

Use strict readiness only when account-level setup and remote workflow evidence are expected to be complete:

```bash
python -B scripts/check_github_readiness.py --strict
```

## Pending Quality Gate

Symptom:

- `github-readiness` reports `quality-gate pending`.
- The latest pushed commit appears in GitHub Actions but has not completed.
- Local `quality` passed before the push.

Wrong fix:

- Mark the workflow green because local quality passed.
- Disable the readiness row or rename the expected check.
- Claim published workflow evidence before the remote run completes.

Safe fix:

```bash
python -B scripts/dev.py quality
python -B scripts/dev.py github-readiness
```

Wait for the current remote run to finish, then rerun readiness. Local quality is a prerequisite, not a substitute for the remote `quality-gate`.

## Missing Workflow Run

Symptom:

- `github-readiness` reports `quality-gate check run not found`.
- The remote `main` commit exists, but Actions has no matching run yet.
- The workflow file is reachable but GitHub has not associated a run with the commit.

Wrong fix:

- Change `.github/workflows/ci.yml` just to create activity.
- Treat the missing run as proof that local code is broken.
- Claim Actions is green based on an older commit.

Safe fix:

```bash
git ls-remote origin refs/heads/main
python -B scripts/dev.py workflow-security
python -B scripts/dev.py github-readiness
```

If the workflow remains missing after the pushed commit is visible, inspect the Actions page for repository-level workflow settings before changing code.

Use `docs/github_api_rate_limit_troubleshooting_examples.md` when the missing run might be API rate-limit, stale-cache, or transient GitHub availability rather than workflow configuration.

## Stale Badge

Symptom:

- The README badge or Actions page shows an older status than the latest pushed commit.
- `github-readiness` targets the exact current `origin/main` SHA.
- A reviewer sees a mismatch between the badge and readiness output.

Wrong fix:

- Trust the badge over the exact commit check.
- Replace the badge with a static success claim.
- Claim latest Actions evidence from a previous commit.

Safe fix:

```bash
git rev-parse HEAD
git ls-remote origin refs/heads/main
python -B scripts/dev.py github-readiness
```

Use the readiness check for current-commit evidence. Keep badge wording conservative until the badge and readiness agree.

## Skipped Workflow

Symptom:

- GitHub Actions shows the workflow as skipped or not triggered for a commit.
- The workflow file still contains the expected `push`, `pull_request`, and `workflow_dispatch` triggers.
- `github-readiness` does not find a successful `quality-gate` for the current remote commit.

Wrong fix:

- Broaden workflow permissions.
- Switch public PR handling to `pull_request_target`.
- Add secrets or authenticated GitHub commands to CI.

Safe fix:

```bash
python -B scripts/dev.py workflow-security
python -B scripts/dev.py governance
python -B scripts/dev.py github-readiness
```

Keep `.github/workflows/ci.yml` least-privileged. If repository-level Actions settings blocked the run, treat that as account-level setup rather than a code-quality result.

## Fork PR Permission Limits

Symptom:

- A public fork PR cannot access secrets or write credentials.
- Uploads, comments, or authenticated GitHub commands are unavailable from CI.
- The PR workflow still runs with `permissions: contents: read`.

Wrong fix:

- Add `secrets.*` to the workflow.
- Enable write tokens for external PRs.
- Use `pull_request_target` for untrusted contributor code.

Safe fix:

```bash
python -B scripts/dev.py workflow-security
python -B scripts/dev.py pr-policy
python -B scripts/dev.py pr-triage
```

The public PR workflow should stay least-privileged. Use maintainer-side review and authenticated maintenance commands outside CI for actions that need repository write access.

## Review Checklist

- `.github/workflows/ci.yml` still uses `pull_request`, `push`, and `workflow_dispatch`.
- Workflow permissions remain `contents: read`.
- Checkout keeps `persist-credentials: false`.
- The workflow does not reference `secrets.*`, run authenticated `gh`, or push from CI.
- `python -B scripts/dev.py workflow-security` passes before workflow-related changes are committed.
- `python -B scripts/dev.py github-readiness` is used for remote current-commit evidence after push.
- Public docs do not claim a green workflow until the current remote `quality-gate` run passes.
