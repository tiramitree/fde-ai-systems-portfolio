# Post-Publish Warning Examples

Use this page when post-publish checks or GitHub readiness checks produce warnings. Read it with `docs/post_publish_checklist.md`, `docs/published_repository_status.md`, `docs/github_release_commands.md`, `docs/github_latest_release_troubleshooting_examples.md`, `docs/github_authenticated_maintenance_troubleshooting_examples.md`, `docs/github_public_pr_api_fallback_troubleshooting_examples.md`, `docs/github_api_rate_limit_troubleshooting_examples.md`, `docs/github_repository_metadata_troubleshooting_examples.md`, `docs/github_repository_settings_screenshot_checklist.md`, `docs/social_preview_verification_examples.md`, `docs/profile_pin_verification_examples.md`, `docs/github_actions_warning_examples.md`, and `docs/command_output_troubleshooting_map.md`.

The core rule: local quality evidence and remote GitHub evidence prove different things. Do not claim published evidence until the remote checks pass, and do not treat GitHub warning rows as local code failures unless strict launch verification is required.

## Expected Evidence Split

Local proof before push:

```bash
python -B scripts/dev.py quality
python -B scripts/dev.py fresh-clone-local
```

Remote proof after push:

```bash
python -B scripts/dev.py fresh-clone
python -B scripts/post_publish_check.py
python -B scripts/dev.py github-readiness
```

Use `python -B scripts/check_github_readiness.py --strict` only when account-level setup is expected to be finished and manual warning rows should block the release claim.

## Remote File Lag

Symptom:

- Local `main` is ahead of `origin/main`.
- `fresh-clone-local` passes but `fresh-clone` or `post_publish_check.py` still reads older remote files.
- A newly linked doc is present locally but missing on GitHub.

Wrong fix:

- Treat local clone proof as remote publication proof.
- Remove the new file from post-publish checks.
- Claim the public branch has the new docs before push.

Safe fix:

```bash
git status --short --branch
git rev-parse HEAD
git ls-remote origin refs/heads/main
python -B scripts/dev.py fresh-clone-local
```

After the push is intentionally visible:

```bash
python -B scripts/dev.py fresh-clone
python -B scripts/post_publish_check.py
```

## Raw README Failures

Symptom:

- `post_publish_check.py` fails on raw README reachability.
- The GitHub page is reachable, but raw content returns a transient error or stale content.
- A README link appears locally but the raw remote branch has not caught up.

Wrong fix:

- Weaken README links to make the check pass.
- Treat a raw README failure as proof that local docs are wrong.

Safe fix:

```bash
python -B scripts/post_publish_check.py
python -B scripts/dev.py fresh-clone
```

If the failure repeats after the pushed branch is visible, inspect the exact raw URL and file path named by the check. Keep README claims conservative until the raw file is reachable.

## GitHub Actions Pending State

Symptom:

- `github-readiness` reports a pending `quality-gate`.
- The local `quality` command passed.
- GitHub Actions has not finished processing the latest pushed commit.

Wrong fix:

- Mark GitHub Actions as green because local quality passed.
- Delete the readiness row or lower the expected check name.

Safe fix:

```bash
python -B scripts/dev.py quality
python -B scripts/dev.py github-readiness
```

If the latest pushed commit is still pending, wait for Actions and rerun readiness. Local quality is useful evidence, but it is not a replacement for the remote workflow result.

## Readiness Warning Rows

Symptom:

- `github-readiness` exits with `0 failure(s)` but reports `[WARN]` rows for metadata, topics, branch protection, release page state, or API rate limits.
- A reviewer asks whether the local docs change is blocked.

Wrong fix:

- Treat every warning as a code failure.
- Treat every warning as completed account setup.
- Hide the warning in status docs.

Safe fix:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/dev.py launch-assets
```

Non-strict warnings mean account-level or remote-freshness follow-up. Use `docs/github_latest_release_troubleshooting_examples.md` for latest-release state, tag selection, draft/prerelease confusion, and artifact drift. Use `docs/github_authenticated_maintenance_troubleshooting_examples.md` for dry-run versus apply, account permissions, branch protection or release side effects, and PR maintenance safeguards. Use `docs/github_api_rate_limit_troubleshooting_examples.md` for API rate limits, transient failures, stale cached status, pending Actions lookups, and strict-mode review. Use `docs/github_repository_metadata_troubleshooting_examples.md` for description, topics, URL, stale public status, and unauthenticated maintenance warnings. Strict warnings block claims that GitHub setup is finished.

## Manual Account Settings

Symptom:

- `github-readiness` prints `[MANUAL] social preview configured`.
- `github-readiness` prints `[MANUAL] profile repository pin configured`.
- Repository metadata, topics, branch protection, or release page work remains listed under manual follow-up.

Wrong fix:

- Claim full GitHub setup from local checks.
- Mark manual rows done before using the GitHub UI or authenticated maintenance path.

Safe fix:

```bash
python -B scripts/dev.py github-maintenance
python -B scripts/dev.py github-readiness
```

Use `docs/github_repository_settings.md` for the expected account settings, `docs/github_repository_settings_screenshot_checklist.md` before retaining or sharing settings screenshots, `docs/social_preview_verification_examples.md` before treating social preview image checks as account-level setup evidence, and `docs/profile_pin_verification_examples.md` before treating profile-page state as complete. Keep manual rows visible until the account action is done and rechecked.

## Review Checklist

- Local `quality` and `fresh-clone-local` passed before push-facing work.
- Remote `fresh-clone` and `post_publish_check.py` passed after push.
- GitHub readiness has no hard failures.
- `[WARN]` and `[MANUAL]` rows are described as follow-up unless strict verification is required.
- Public docs do not claim remote files, release page state, branch protection, social preview, profile pin, or launch feedback before matching evidence exists.
