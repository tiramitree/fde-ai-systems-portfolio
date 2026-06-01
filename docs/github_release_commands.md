# GitHub Release Commands

Suggested repository name:

```text
fde-ai-systems-portfolio
```

Before publishing:

```powershell
cd <repo-root>
python -B scripts/dev.py verify
git status --short
```

Initialize and publish:

```powershell
git init
git status --short
git add .
git commit -m "Initial open-source FDE AI systems portfolio"
git branch -M main
git remote add origin https://github.com/<your-user>/fde-ai-systems-portfolio.git
git push -u origin main
```

If you are publishing from the current local workspace, the repository is already initialized and committed on `main`. Use only:

```powershell
git remote add origin https://github.com/<your-user>/fde-ai-systems-portfolio.git
git push -u origin main
```

After publishing:

1. Replace the static quality badge with the real GitHub Actions badge.
2. Confirm GitHub Actions passes.
3. Add repo topics from `docs/github_launch_plan.md`.
4. Pin the repo on your profile.
5. Add screenshots or GIF if available.
