# Post-Publish Checklist

Run this after creating the GitHub repository and pushing `main`.

## Commands

```powershell
git remote add origin https://github.com/tiramitree/fde-ai-systems-portfolio.git
git push -u origin main
python -B scripts/post_publish_check.py
```

## Required Evidence

The post-publish check must prove:

- `origin` points to GitHub.
- local branch is `main`.
- tracked worktree is clean.
- remote `main` branch exists.
- GitHub repository page is reachable.
- raw README is reachable.
- GitHub Actions workflow is reachable.
- key documentation files are published.

## Manual GitHub Checks

After the automated check passes:

1. Confirm the README renders correctly.
2. Confirm screenshots render.
3. Confirm the `quality-gate` workflow completes successfully.
4. Replace the static README quality badge with the real GitHub Actions badge.
5. Apply repository topics from `docs/github_repository_settings.md`.
6. Add repository social preview.
7. Create issues from `docs/github_initial_issues.md`.
8. Create release `v0.1.0`.
9. Pin the repository on the GitHub profile.

