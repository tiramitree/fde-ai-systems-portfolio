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
git commit -m "Initial open-source FDE AI systems reference"
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
3. Dry-run GitHub launch setup:

```powershell
python -B scripts/dev.py github-launch-setup
python -B scripts/dev.py github-maintenance
```

4. After `gh auth login`, apply repository description, topics, merge policy, best-effort security settings, branch protection, and the `v0.1.0` release:

```powershell
python -B scripts/maintain_github_state.py --apply
```

5. Upload `docs/assets/github-preview.png` as the social preview and pin the repo on your profile.
6. Re-run:

```powershell
python -B scripts/dev.py github-readiness
```
