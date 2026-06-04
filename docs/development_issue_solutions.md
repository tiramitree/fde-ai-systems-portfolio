# Development Issue Solutions

Use this file before adding new code or touching GitHub settings. It records recurring problems, the current decision, and the safest next action.

## Current Open Items

| Item | Status | Resolution |
| --- | --- | --- |
| GitHub CLI authentication | Open | `gh` is installed but not authenticated. Account-level actions such as repository metadata, branch protection, release creation, PR comments, and PR closure require `gh auth login` or another authenticated GitHub path. Use `python -B scripts/dev.py github-maintenance` for the dry-run plan. |
| Repository metadata and topics | Open | Run `python -B scripts/maintain_github_state.py --apply` after GitHub CLI authentication, then rerun `python -B scripts/dev.py github-readiness`. |
| Main branch protection | Open | Apply `docs/github_branch_protection.json` through `python -B scripts/maintain_github_state.py --apply` after GitHub CLI authentication. |
| GitHub release page for `v0.1.0` | Open | Create with `python -B scripts/maintain_github_state.py --apply` after authentication. The tag already exists. |
| Social preview and profile pin | Manual | Use `docs/assets/github-preview.png` for the social preview and pin the repository from GitHub account settings. |
| GitHub labels and community issues | Open | Validate locally with `python -B scripts/dev.py community-issues`, dry-run with `python -B scripts/dev.py github-community`, and sync labels after authentication with `python -B scripts/manage_community_issues.py --apply`. Create roadmap issues only when open roadmap work should be visible. |
| PR #12 Python Docker baseline bump | Closed, not merged | The PR changed `ai-reliability-incident-console/Dockerfile` from the pinned Python 3.12 baseline to Python 3.14 and failed `python -B scripts/dev.py container-release`. Future matching runtime-baseline Dependabot PRs can be closed after authentication with `python -B scripts/maintain_github_state.py --apply --skip-launch --close-runtime-bump-prs` unless the repository intentionally performs a coordinated runtime baseline upgrade. |

## Recurring Local Issues

### Git Index Lock On Windows

Symptom:

```text
warning: unable to unlink '.git/index.lock': Invalid argument
fatal: Unable to create '.git/index.lock': File exists.
```

Resolution:

1. Check that no Git process is running:

```powershell
Get-Process git -ErrorAction SilentlyContinue
```

2. If no Git process is running, remove only the lock file:

```powershell
Remove-Item -LiteralPath .git\index.lock -Force
```

Do not use `git reset --hard` for this problem.

### Fresh Clone Validation Under Local Sandboxes

Symptom:

```text
git clone failed to write .git/config
```

Resolution:

- Use `python -B scripts/dev.py fresh-clone-local` outside restricted sandbox execution when Git needs to create a clean clone.
- The script creates temporary clones under ignored `out/fresh-clone-tmp/`.
- Cleanup is hardened for read-only Git objects. If cleanup still fails, treat it as local environment cleanup work, not as a repository release failure, as long as the command reports `Fresh clone experience check passed.`

### GitHub API Rate Limits Or Status Propagation

Symptom:

```text
API rate limit exceeded
latest main GitHub Actions run passed: FAIL
```

Resolution:

1. `python -B scripts/dev.py github-readiness` first checks the exact current `origin/main` commit's `quality-gate` check run.
2. Wait briefly and rerun:

```bash
python -B scripts/dev.py github-readiness
```

3. If ordinary readiness reports a warning because the GitHub API is rate-limited or the current check is still pending, do not treat that as a project code failure.
4. If unauthenticated API limits continue, authenticate GitHub CLI and rerun readiness.
5. Use strict mode only for final account-level launch checks:

```bash
python -B scripts/check_github_readiness.py --strict
```

Do not change project code merely because a readiness read hit a temporary API limit.

### Browser-Based Visual Asset Refresh Failures

Symptom:

```text
No Chrome/Chromium/Edge executable found. Set FDE_BROWSER_BIN to refresh screenshots.
```

or:

```text
screenshot is suspiciously small
contrast sample check failed
source file changed since capture
```

Resolution:

1. Run browser discovery without refreshing assets:

```bash
python -B scripts/refresh_visual_assets.py --check-browser
```

2. If needed, set `FDE_BROWSER_BIN` for the current shell only. Do not commit local browser paths or profile directories.
3. Refresh screenshots and manifest together:

```bash
python -B scripts/dev.py refresh-visual-assets
python -B scripts/dev.py visual-asset-diff
python -B scripts/dev.py visual-assets
```

4. If dimensions mismatch, remember desktop assets are 1400x900 and mobile / narrow viewport assets are 500x844.
5. If contrast samples fail, inspect the screenshot first. Fix the UI when contrast actually regressed; move sample coordinates in `scripts/refresh_visual_assets.py` only when the UI is correct and the stable text region moved.
6. Run `python -B scripts/dev.py safety` before committing so temporary browser profiles, logs, local paths, and runtime files stay out of the public repository.

## Pull Request Decisions

### Docker Runtime Baseline Bumps

Current policy:

- The local demo baseline is Python 3.12 slim, digest-pinned.
- Dependabot ignores Python Docker semver-minor and semver-major updates.
- `scripts/review_open_prs.py` flags Dockerfile Python baseline changes away from the pinned 3.12 image as `HIGH`.
- `scripts/check_container_release.py` rejects a service Dockerfile that does not use the expected pinned Python 3.12 prefix.

Accept a runtime baseline bump only as a coordinated release-policy project:

1. Update all service Dockerfiles together.
2. Update `scripts/check_container_release.py`.
3. Update `docs/container_release_hygiene.md` and `docs/supply_chain_security.md`.
4. Run local `python -B scripts/dev.py quality`.
5. Run Docker runtime verification on a Docker-enabled machine.
6. Confirm GitHub Actions is green.

### PR Review Minimum Bar

Before merging any PR:

```bash
python -B scripts/dev.py github-maintenance
python -B scripts/dev.py github-community
python -B scripts/dev.py pr-triage
python -B scripts/dev.py governance
python -B scripts/dev.py workflow-security
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Also confirm:

- The diff is narrow and explainable.
- No personal paths, secrets, local state, or generated runtime artifacts are tracked.
- GitHub Actions is green.
- The contribution strengthens a public repository claim.

## Publication Checks

After a push:

```bash
python -B scripts/dev.py fresh-clone
python -B scripts/post_publish_check.py
python -B scripts/dev.py github-readiness
python -B scripts/dev.py github-maintenance
python -B scripts/dev.py github-community
python -B scripts/dev.py pr-triage
```

Expected current state:

- `fresh-clone` passes from GitHub origin.
- `post_publish_check.py` passes.
- `github-readiness` has no hard failures once Actions status has propagated, but still reports manual/account blockers until GitHub metadata, topics, branch protection, release page, social preview, and profile pin are complete.
- `pr-triage` currently reports 0 open PRs. Historical PR #12 remains high-risk if inspected directly by PR number.
