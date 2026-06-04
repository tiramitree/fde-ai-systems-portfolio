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
- GitHub API rate-limit troubleshooting examples are published: `docs/github_api_rate_limit_troubleshooting_examples.md`.
- raw README is reachable.
- GitHub Actions workflow is reachable.
- key documentation files are published.
- the authenticated GitHub maintenance troubleshooting examples are published.
- the GitHub public PR API fallback troubleshooting examples are published: `docs/github_public_pr_api_fallback_troubleshooting_examples.md`.
- the GitHub repository settings screenshot checklist is published: `docs/github_repository_settings_screenshot_checklist.md`.
- the public roadmap issue comment examples are published: `docs/public_roadmap_issue_comment_examples.md`.
- the roadmap duplicate issue handling examples are published: `docs/roadmap_duplicate_issue_handling_examples.md`.
- the contributor attribution examples are published: `docs/contributor_attribution_examples.md`.
- the issue triage SLA wording examples are published: `docs/issue_triage_sla_wording_examples.md`.
- the discussion-to-issue conversion examples are published: `docs/discussion_to_issue_conversion_examples.md`.
- the GitHub Discussions launch checklist is published: `docs/github_discussions_launch_checklist.md`.
- the Dependabot and secret-scanning verification examples are published: `docs/dependabot_secret_scanning_verification_examples.md`.
- the GitHub repository metadata troubleshooting examples are published.
- the public maintainer status update examples are published: `docs/public_maintainer_status_update_examples.md`.
- the observability integrity script and documentation are published.
- the threat model script and documentation are published.
- the PR review policy script and documentation are published.
- the fresh clone script and documentation are published.
- the API documentation script and documentation are published.
- the demo replay artifact script and documentation are published.
- the release attachment verification examples are published.
- the release asset upload dry-run examples are published: `docs/release_asset_upload_dry_run_examples.md`.
- the release note refresh checklist is published: `docs/release_note_refresh_checklist.md`.
- the release note changelog drift examples are published: `docs/release_note_changelog_drift_examples.md`.
- the GitHub release attachment screenshot checklist is published: `docs/github_release_attachment_screenshot_checklist.md`.
- the GitHub release page troubleshooting examples are published.
- the GitHub latest release troubleshooting examples are published.
- the branch protection verification examples are published.
- the social preview verification examples are published.
- the profile pin verification examples are published.
- the post-publish warning examples are published.
- the GitHub Actions warning examples are published.
- the GitHub Actions badge verification examples are published: `docs/github_actions_badge_verification_examples.md`.
- the container release hygiene script and documentation are published.
- the visual asset manifest script, documentation, manifest, and desktop/mobile screenshot assets are published.
- the launch asset hygiene script and documentation are published.
- the launch feedback collection examples are published: `docs/launch_feedback_collection_examples.md`.

## Manual GitHub Checks

After the automated check passes:

1. Confirm the README renders correctly.
2. Confirm screenshots render.
3. Confirm the `quality-gate` workflow completes successfully.
4. Confirm the README quality badge points to the real GitHub Actions workflow using `docs/github_actions_badge_verification_examples.md`.
5. Apply repository description, topics, and available security settings from `docs/github_repository_settings.md`, then compare warning rows with `docs/github_repository_metadata_troubleshooting_examples.md`, screenshot handling with `docs/github_repository_settings_screenshot_checklist.md`, and Dependabot/secret-scanning evidence with `docs/dependabot_secret_scanning_verification_examples.md` before claiming repository settings are current.
6. Enable branch protection on `main` using `docs/github_branch_protection.json`.
7. Compare branch protection state with `docs/branch_protection_verification_examples.md` before claiming the remote policy is active.
8. Add repository social preview using `docs/assets/github-preview.png`, then compare the result with `docs/social_preview_verification_examples.md` before claiming social preview setup.
9. Create a GitHub release page for `v0.1.0`.
10. Pin the repository on the GitHub profile, then compare the visible account-profile state with `docs/profile_pin_verification_examples.md` before claiming profile pin setup.
11. Run `python -B scripts/dev.py fresh-clone` after the push is visible. Use `python -B scripts/dev.py fresh-clone-local` before pushing when validating local-only commits.
12. Compare warning rows with `docs/post_publish_warning_examples.md` before claiming published evidence.
13. Compare Actions warnings with `docs/github_actions_warning_examples.md` and README badge evidence with `docs/github_actions_badge_verification_examples.md` before claiming the remote workflow is green.
14. Run `python -B scripts/dev.py replay-artifact` before attaching release evidence.
15. Compare release notes with `docs/release_note_refresh_checklist.md` before claiming checked-in notes, GitHub release-page text, replay artifacts, or post-publish evidence are current.
16. Compare release notes, changelog summaries, release page text, and remote evidence with `docs/release_note_changelog_drift_examples.md` before claiming changelog freshness.
17. Compare release-page state with `docs/github_release_page_troubleshooting_examples.md` and `docs/github_latest_release_troubleshooting_examples.md` before claiming the release page or latest release is current.
18. Compare release attachments with `docs/release_attachment_verification_examples.md`, release upload plans with `docs/release_asset_upload_dry_run_examples.md`, and release attachment screenshots with `docs/github_release_attachment_screenshot_checklist.md` before claiming the release page is current.
19. Run `python -B scripts/dev.py container-release` before claiming Docker packaging is release-clean.
20. Run `python -B scripts/dev.py docker-runtime` on a Docker-enabled machine before claiming Docker runtime verification.
21. Run `python -B scripts/dev.py openai-live` with a real API key before claiming OpenAI live-mode verification.
22. Run `python -B scripts/dev.py visual-asset-diff` and `python -B scripts/dev.py visual-assets` after refreshing desktop or mobile demo screenshots.
23. Run `python -B scripts/dev.py launch-assets` before publishing launch copy or growth posts.
24. Compare public comments, private-message summaries, analytics notes, stars, and forks with `docs/launch_feedback_collection_examples.md` before claiming launch feedback or star-growth evidence.
25. Run `python -B scripts/dev.py github-community` to dry-run label sync and optional community issue creation before changing public issue state.
26. Compare label warnings with `docs/github_label_troubleshooting_examples.md` before applying label sync or creating public roadmap issues.
27. Compare GitHub Discussions setup, categories, pinned starter topics, moderation rules, and launch-feedback boundaries with `docs/github_discussions_launch_checklist.md` before claiming Discussions are launch-ready.
28. Compare discussion-to-issue conversions with `docs/discussion_to_issue_conversion_examples.md` before turning Q&A, ideas, private feedback, or low-signal discussions into public issue scope.
29. Compare duplicate or overlapping roadmap issues with `docs/roadmap_duplicate_issue_handling_examples.md` before closing, merging, splitting, or redirecting public issue scope.
30. Compare public maintainer updates with `docs/public_maintainer_status_update_examples.md` before summarizing local progress, pushed code, remote warnings, manual account setup, launch feedback, or roadmap scope.
31. Compare authenticated maintenance output with `docs/github_authenticated_maintenance_troubleshooting_examples.md` before claiming account-level maintenance has been applied.

## Optional Backlog Seeding

Use `docs/github_initial_issues.md` only when you are ready to run the repository as an active public project. Creating those issues is useful for community planning, but it intentionally changes the readiness signal from "no open issues" to "open roadmap work exists." Every issue should map to real engineering work and include acceptance criteria. Validate the pack with `python -B scripts/dev.py community-issues` first.
