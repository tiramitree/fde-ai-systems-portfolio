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

1. Confirm the README quality badge points to the real GitHub Actions workflow using `docs/github_actions_badge_verification_examples.md`.
2. Confirm GitHub Actions passes for the current remote `quality-gate` run.
3. Dry-run GitHub launch setup:

```powershell
python -B scripts/dev.py github-launch-setup
python -B scripts/dev.py github-maintenance
```

4. Regenerate current replay evidence, then after `gh auth login`, apply repository description, topics, merge policy, best-effort security settings, branch protection, the `v0.1.0` release, and the current replay artifact attachments:

```powershell
python -B scripts/dev.py replay-artifact
python -B scripts/maintain_github_state.py --apply
```

5. If the release page already existed before the apply path, review `docs/release_asset_upload_dry_run_examples.md` before replacing release assets manually:

```powershell
gh release upload v0.1.0 out/demo_replay_artifact.md out/demo_replay_artifact.json --repo tiramitree/fde-ai-systems-portfolio --clobber
```

6. Upload `docs/assets/github-preview.png` as the social preview and pin the repo on your profile.
7. Re-run:

```powershell
python -B scripts/dev.py github-readiness
```
