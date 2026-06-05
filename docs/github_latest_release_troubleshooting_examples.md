# GitHub Latest Release Troubleshooting Examples

Use this page when GitHub latest-release state is unclear. Read it with `docs/github_release_page_troubleshooting_examples.md`, `docs/stale_release_page_screenshot_examples.md`, `docs/github_release_commands.md`, `docs/release_note_refresh_checklist.md`, `docs/release_note_changelog_drift_examples.md`, `docs/release_attachment_verification_examples.md`, `docs/github_release_attachment_screenshot_checklist.md`, `docs/post_publish_checklist.md`, `docs/post_publish_warning_examples.md`, and `docs/command_output_troubleshooting_map.md`.

The core rule: tag existence, release-page existence, and latest-release selection prove different things. Do not claim the latest release is current until GitHub readiness or direct release-page evidence confirms it.

## Expected Evidence Split

Local release evidence:

```bash
python -B scripts/dev.py replay-artifact
python -B scripts/dev.py launch-assets
python -B scripts/dev.py quality
```

Remote release evidence:

```bash
python -B scripts/dev.py fresh-clone
python -B scripts/post_publish_check.py
python -B scripts/dev.py github-readiness
```

Maintenance planning:

```bash
python -B scripts/dev.py github-maintenance
```

Local evidence proves the release artifacts can be regenerated. Remote evidence proves GitHub can see the intended public repository, release page, latest-release state, and current attachment review path.

## Missing Latest Release

Symptom:

- The tag `v0.1.0` exists.
- `github-readiness` reports `GitHub release page exists for v0.1.0` as `[WARN]`.
- The latest-release API endpoint returns `404` or no visible release.

Wrong fix:

- Claim a latest release from the tag alone.
- Commit generated `out/` artifacts as a substitute for a release page.
- Remove release-page readiness checks.

Safe fix:

```bash
python -B scripts/dev.py replay-artifact
python -B scripts/dev.py github-maintenance
python -B scripts/dev.py github-readiness
```

Create or refresh the release through the authenticated maintenance path or GitHub UI. Keep the latest-release claim manual until GitHub shows a visible latest release for the intended tag.

## Wrong Latest Tag

Symptom:

- A release page exists, but `/releases/latest` points to a tag other than `v0.1.0`.
- README or release notes mention `v0.1.0`.
- Local replay artifacts were generated for the current source state.

Wrong fix:

- Treat any visible release as proof that `v0.1.0` is latest.
- Change local docs to match an accidental latest tag.
- Attach current artifacts to an unintended tag.

Safe fix:

```bash
git rev-parse HEAD
git ls-remote origin refs/heads/main
python -B scripts/dev.py github-readiness
python -B scripts/dev.py github-maintenance
```

Use `docs/github_release_commands.md` as the source of truth for the intended tag. Do not claim latest-release freshness until the GitHub latest-release state points to the intended release.

## Draft Or Prerelease Confusion

Symptom:

- A release exists in GitHub UI, but it is draft, prerelease, or not selected as latest.
- Public checks still report the latest release as missing or stale.
- The release notes are visible to maintainers but not to public visitors.

Wrong fix:

- Claim the release is public from maintainer-only draft visibility.
- Mark prerelease evidence as the stable public release without saying so.
- Weaken readiness checks to accept any release object.

Safe fix:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/check_github_readiness.py --strict
```

Use strict readiness when release setup is expected to be finished. Keep public wording tied to the public latest release, not maintainer-only draft state.

## Stale Release Page

Symptom:

- The latest release page exists, but release notes do not match `docs/github_release_notes_v0.1.0.md`.
- The public page points to older evidence after local docs changed.
- `post_publish_check.py` proves files are reachable, but not that the release page was refreshed.

Wrong fix:

- Edit GitHub release notes by hand without updating checked-in notes.
- Claim latest release evidence from local README text.
- Treat raw README reachability as release-page freshness.

Safe fix:

```bash
python -B scripts/dev.py quality
python -B scripts/dev.py replay-artifact
python -B scripts/dev.py github-readiness
```

Update checked-in release notes first, then review `docs/release_note_refresh_checklist.md` and refresh the GitHub release page through reviewed maintenance or the UI. Keep stale-page wording manual until the public page matches the intended notes.

## Attached Artifact Drift

Symptom:

- The latest release exists, but attached or linked replay artifacts are missing, stale, or from another commit.
- `out/demo_replay_artifact.md` and `out/demo_replay_artifact.json` were regenerated locally.
- The release page still shows older evidence.

Wrong fix:

- Hand-edit generated replay artifacts.
- Upload artifacts from another checkout.
- Commit ignored `out/` files as ordinary source content.

Safe fix:

```bash
python -B scripts/dev.py replay-artifact
python -B scripts/dev.py safety
python -B scripts/dev.py github-readiness
```

Use `docs/release_attachment_verification_examples.md` and `docs/github_release_attachment_screenshot_checklist.md` to review attachment evidence. Attach or link the regenerated files externally, and keep `out/` ignored unless a release process explicitly asks for reviewed source-visible evidence.

Use `docs/release_note_changelog_drift_examples.md` before treating changelog freshness as latest-release evidence.

Use `docs/stale_release_page_screenshot_examples.md` before treating stale latest-release screenshots, wrong-tag screenshots, or private account UI crops as current latest-release evidence.

## Review Checklist

- `docs/github_release_commands.md` still points to the intended tag.
- `docs/github_release_notes_v0.1.0.md` matches the release claim.
- `docs/release_note_refresh_checklist.md` was used before treating checked-in notes or GitHub release-page text as current.
- `docs/release_note_changelog_drift_examples.md` was used before claiming changelog freshness or release-summary freshness.
- `python -B scripts/dev.py replay-artifact` regenerates current local attachment evidence.
- `python -B scripts/dev.py launch-assets` passes after release-facing wording changes.
- `python -B scripts/dev.py github-readiness` has no hard failures when the GitHub API is reachable.
- `python -B scripts/check_github_readiness.py --strict` is used when latest-release setup is expected to be complete.
- Tag existence, release-page existence, and latest-release selection are reviewed separately.
- Stale latest-release screenshots are reviewed with `docs/stale_release_page_screenshot_examples.md`.
- Latest-release attachment screenshots are compared with `docs/github_release_attachment_screenshot_checklist.md`.
- Public docs do not claim the latest release is current until GitHub readiness or direct release-page evidence confirms it.
