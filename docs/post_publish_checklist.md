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
- the observability integrity script and documentation are published.
- the threat model script and documentation are published.

## Manual GitHub Checks

After the automated check passes:

1. Confirm the README renders correctly.
2. Confirm screenshots render.
3. Confirm the `quality-gate` workflow completes successfully.
4. Confirm the README quality badge points to the real GitHub Actions workflow.
5. Apply repository description and topics from `docs/github_repository_settings.md`.
6. Enable branch protection on `main` using `docs/github_branch_protection.json`.
7. Add repository social preview using `docs/assets/github-preview.png`.
8. Create a GitHub release page for `v0.1.0`.
9. Pin the repository on the GitHub profile.

## Optional Backlog Seeding

Use `docs/github_initial_issues.md` only when you are ready to run the repository as an active public project. Creating those issues is useful for community planning, but it intentionally changes the readiness signal from "no open issues" to "open roadmap work exists."
