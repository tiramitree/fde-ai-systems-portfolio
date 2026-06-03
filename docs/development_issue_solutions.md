# Development Issue Solutions

Use this file before adding new code or touching GitHub settings. It records recurring problems, the current decision, and the safest next action.

## Current Open Items

| Item | Status | Resolution |
| --- | --- | --- |
| GitHub CLI authentication | Open | `gh` is installed but not authenticated. Account-level actions such as repository metadata, branch protection, release creation, PR comments, and PR closure require `gh auth login` or another authenticated GitHub path. |
| Repository metadata and topics | Open | Run `python -B scripts/configure_github_launch.py --apply` after GitHub CLI authentication, then rerun `python -B scripts/dev.py github-readiness`. |
| Main branch protection | Open | Apply `docs/github_branch_protection.json` through `python -B scripts/configure_github_launch.py --apply` after GitHub CLI authentication. |
| GitHub release page for `v0.1.0` | Open | Create with `python -B scripts/configure_github_launch.py --apply` after authentication. The tag already exists. |
| Social preview and profile pin | Manual | Use `docs/assets/github-preview.png` for the social preview and pin the repository from GitHub account settings. |
| PR #12 Python Docker major bump | Do not merge | The PR changes `ai-reliability-incident-console/Dockerfile` from the pinned Python 3.12 baseline to Python 3.14 and fails `python -B scripts/dev.py container-release`. Keep it unmerged unless the repository intentionally performs a coordinated runtime baseline upgrade. |

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

## Pull Request Decisions

### Docker Runtime Major Bumps

Current policy:

- The local demo baseline is Python 3.12 slim, digest-pinned.
- Dependabot ignores Python Docker semver-major updates.
- `scripts/review_open_prs.py` flags Dockerfile Python major baseline changes as `HIGH`.
- `scripts/check_container_release.py` rejects a service Dockerfile that does not use the expected pinned Python 3.12 prefix.

Accept a runtime major bump only as a coordinated release-policy project:

1. Update all service Dockerfiles together.
2. Update `scripts/check_container_release.py`.
3. Update `docs/container_release_hygiene.md` and `docs/supply_chain_security.md`.
4. Run local `python -B scripts/dev.py quality`.
5. Run Docker runtime verification on a Docker-enabled machine.
6. Confirm GitHub Actions is green.

### PR Review Minimum Bar

Before merging any PR:

```bash
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
python -B scripts/dev.py pr-triage
```

Expected current state:

- `fresh-clone` passes from GitHub origin.
- `post_publish_check.py` passes.
- `github-readiness` has no hard failures once Actions status has propagated, but still reports manual/account blockers until GitHub metadata, topics, branch protection, release page, social preview, and profile pin are complete.
- `pr-triage` flags PR #12 as high risk until it is closed or replaced by a coordinated runtime-baseline update.
