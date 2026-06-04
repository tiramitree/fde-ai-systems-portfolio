# GitHub API Rate-Limit Troubleshooting Examples

Use this page when `github-readiness`, `post_publish_check.py`, or PR triage reports a GitHub API rate limit, transient API failure, pending Actions lookup, stale cached status, or strict-mode review question. Read it with `docs/published_repository_status.md`, `docs/post_publish_checklist.md`, `docs/post_publish_warning_examples.md`, `docs/github_public_pr_api_fallback_troubleshooting_examples.md`, `docs/github_actions_warning_examples.md`, `docs/github_repository_metadata_troubleshooting_examples.md`, and `docs/command_output_troubleshooting_map.md`.

The core rule: GitHub API availability and local project quality prove different things. Do not claim remote readiness until the readiness command can verify the current repository state.

## Expected Evidence Split

Local quality proof:

```bash
python -B scripts/dev.py quality
python -B scripts/dev.py fresh-clone-local
```

Remote readiness proof:

```bash
python -B scripts/dev.py fresh-clone
python -B scripts/post_publish_check.py
python -B scripts/dev.py github-readiness
```

Strict remote review:

```bash
python -B scripts/check_github_readiness.py --strict
```

Use strict mode only when account-level setup and remote evidence are expected to be complete.

## Unauthenticated Rate Limits

Symptom:

- `github-readiness` reports a GitHub API rate limit.
- `pr-triage` falls back to public HTML or cannot inspect PR files.
- Local `quality` and `fresh-clone-local` still pass.

Wrong fix:

- Treat the rate limit as a code regression.
- Claim remote readiness because local quality passed.
- Add tokens, account identifiers, or private auth instructions to public docs.

Safe fix:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/dev.py pr-triage
```

Wait, rerun, or use an authenticated maintainer environment. Keep API rate-limit rows visible as remote-evidence uncertainty until the command can inspect the current repository state.

## Transient GitHub API Failures

Symptom:

- GitHub repository pages are reachable in a browser.
- API calls return a transient unavailable, timeout, or unexpected response.
- `post_publish_check.py` or raw file checks may still pass.

Wrong fix:

- Rewrite local docs to hide the warning.
- Treat a transient API failure as proof that the public repository is broken.
- Skip the readiness rerun before claiming launch state.

Safe fix:

```bash
python -B scripts/post_publish_check.py
python -B scripts/dev.py github-readiness
python -B scripts/dev.py launch-assets
```

Separate raw-file reachability from GitHub API metadata. Public launch claims should wait for the API-backed readiness command to verify the current repository state.

## Pending Actions Lookups

Symptom:

- The latest pushed commit exists on `origin/main`.
- `github-readiness` cannot yet find a completed `quality-gate`.
- The Actions page shows pending, queued, or no current run.

Wrong fix:

- Claim GitHub Actions is green from local quality.
- Change the workflow only to force activity.
- Lower workflow permissions or checks to silence readiness warnings.

Safe fix:

```bash
git ls-remote origin refs/heads/main
python -B scripts/dev.py workflow-security
python -B scripts/dev.py github-readiness
```

Use `docs/github_actions_warning_examples.md` for workflow-specific follow-up. Local quality is prerequisite evidence, not remote Actions evidence.

## Stale Cached Status

Symptom:

- README badge, GitHub UI, API output, and raw files disagree for a short period after a push.
- Local `main` has commits that are not yet visible on `origin/main`.
- `fresh-clone-local` passes but remote checks still read older content.

Wrong fix:

- Claim the remote repository has the latest local docs before push or propagation.
- Remove required files from post-publish checks.
- Treat a stale badge as stronger evidence than commit-targeted readiness output.

Safe fix:

```bash
git status --short --branch
git rev-parse HEAD
git ls-remote origin refs/heads/main
python -B scripts/dev.py fresh-clone
python -B scripts/post_publish_check.py
python -B scripts/dev.py github-readiness
```

Use local checks for local commits and remote checks only after the intended push is visible. Keep status wording conservative until remote clone, raw files, and API readiness agree.

## Strict-Mode Review

Symptom:

- Non-strict `github-readiness` has `0 failure(s)` plus warning/manual rows.
- A release review asks whether warning rows should block launch claims.
- Account-level setup, metadata, release page, social preview, or profile pin is expected to be complete.

Wrong fix:

- Treat all warnings as harmless after strict launch setup is expected.
- Treat all warnings as code failures when they are only account-level follow-up.
- Claim launch completion without rerunning strict readiness.

Safe fix:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/check_github_readiness.py --strict
python -B scripts/dev.py github-maintenance
```

Use strict mode to decide whether warning/manual rows block a release claim. Use the maintenance dry-run as planning evidence only until an authenticated maintainer applies the account-level changes.

## Review Checklist

- Local quality is proved with `python -B scripts/dev.py quality` and `python -B scripts/dev.py fresh-clone-local`.
- Remote readiness is proved only after `python -B scripts/dev.py fresh-clone`, `python -B scripts/post_publish_check.py`, and `python -B scripts/dev.py github-readiness` can inspect the intended public state.
- API rate limits and transient GitHub failures are documented as remote-evidence uncertainty, not local code quality.
- Pending Actions rows are checked against `docs/github_actions_warning_examples.md`.
- Metadata warning rows are checked against `docs/github_repository_metadata_troubleshooting_examples.md`.
- `python -B scripts/dev.py launch-assets` passes after release-facing wording changes.
- `python -B scripts/dev.py safety` passes before committing public GitHub setup docs.
- Public docs do not claim remote readiness from local quality or cached GitHub UI state alone.
