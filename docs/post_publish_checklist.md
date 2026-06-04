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
- the PR review policy script and documentation are published.
- the fresh clone script and documentation are published.
- the API documentation script and documentation are published.
- the demo replay artifact script and documentation are published.
- the release attachment verification examples are published.
- the container release hygiene script and documentation are published.
- the visual asset manifest script, documentation, manifest, and desktop/mobile screenshot assets are published.
- the launch asset hygiene script and documentation are published.

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
10. Run `python -B scripts/dev.py fresh-clone` after the push is visible. Use `python -B scripts/dev.py fresh-clone-local` before pushing when validating local-only commits.
11. Run `python -B scripts/dev.py replay-artifact` before attaching release evidence.
12. Compare release attachments with `docs/release_attachment_verification_examples.md` before claiming the release page is current.
13. Run `python -B scripts/dev.py container-release` before claiming Docker packaging is release-clean.
14. Run `python -B scripts/dev.py docker-runtime` on a Docker-enabled machine before claiming Docker runtime verification.
15. Run `python -B scripts/dev.py openai-live` with a real API key before claiming OpenAI live-mode verification.
16. Run `python -B scripts/dev.py visual-asset-diff` and `python -B scripts/dev.py visual-assets` after refreshing desktop or mobile demo screenshots.
17. Run `python -B scripts/dev.py launch-assets` before publishing launch copy or growth posts.
18. Run `python -B scripts/dev.py github-community` to dry-run label sync and optional community issue creation before changing public issue state.

## Optional Backlog Seeding

Use `docs/github_initial_issues.md` only when you are ready to run the repository as an active public project. Creating those issues is useful for community planning, but it intentionally changes the readiness signal from "no open issues" to "open roadmap work exists." Every issue should map to real engineering work and include acceptance criteria. Validate the pack with `python -B scripts/dev.py community-issues` first.
