# GitHub Release Page Troubleshooting Examples

Use this page when release page evidence, release notes, tags, or replay attachments drift. Read it with `docs/github_latest_release_troubleshooting_examples.md`, `docs/github_release_commands.md`, `docs/github_release_notes_v0.1.0.md`, `docs/release_note_refresh_checklist.md`, `docs/release_note_changelog_drift_examples.md`, `docs/release_attachment_verification_examples.md`, `docs/release_asset_upload_dry_run_examples.md`, `docs/github_release_attachment_screenshot_checklist.md`, `docs/post_publish_checklist.md`, and `docs/command_output_troubleshooting_map.md`.

The core rule: local replay-artifact evidence and published release page evidence prove different things. Do not claim the release page is current until the tag, release notes, and current replay attachments are visible on GitHub.

## Expected Release Evidence

Local proof before push or release maintenance:

```bash
python -B scripts/dev.py replay-artifact
python -B scripts/dev.py launch-assets
python -B scripts/dev.py quality
```

Remote proof after push and release maintenance:

```bash
python -B scripts/dev.py fresh-clone
python -B scripts/post_publish_check.py
python -B scripts/dev.py github-readiness
```

Dry-run the authenticated release command before account-level mutation:

```bash
python -B scripts/dev.py github-maintenance
```

Apply release setup only after `gh auth login` and command review:

```bash
python -B scripts/maintain_github_state.py --apply
```

## Missing Release Page

Symptom:

- `github-readiness` reports `GitHub release page exists for v0.1.0` as `[WARN]`.
- The tag exists, but the latest release endpoint returns `404`.
- Local release notes and replay artifacts exist, but the GitHub release page is still account-level follow-up.

Wrong fix:

- Claim release page evidence from local `quality` output.
- Remove the readiness warning.
- Commit generated `out/` files as a substitute for the GitHub release page.

Safe fix:

```bash
python -B scripts/dev.py replay-artifact
python -B scripts/dev.py github-maintenance
python -B scripts/dev.py github-readiness
```

Keep the release page claim manual until authenticated maintenance or the GitHub UI confirms the page and attachments.

## Wrong Tag

Symptom:

- The release page or command targets a tag other than `v0.1.0`.
- `docs/github_release_notes_v0.1.0.md` is reviewed, but a different tag is selected.
- Replay artifacts were generated from a local commit that is not the pushed release commit.

Wrong fix:

- Attach current local artifacts to a mismatched tag.
- Rename the release notes file without updating the release command.
- Claim the release page is current because a tag exists.

Safe fix:

```bash
git status --short --branch
git rev-parse HEAD
git ls-remote origin refs/heads/main
python -B scripts/dev.py replay-artifact
python -B scripts/dev.py github-readiness
```

Use `docs/github_release_commands.md` and `docs/github_release_notes_v0.1.0.md` as the source of truth for the intended tag and release notes.

## Stale Release Notes

Symptom:

- `docs/github_release_notes_v0.1.0.md` describes outdated eval, smoke, or API contract evidence.
- Local `quality` now proves a different evidence count or gate shape.
- The release page notes do not match the current checked-in release notes.

Wrong fix:

- Edit the GitHub release page by hand without updating checked-in notes.
- Reuse old release notes because the old release already looked acceptable.
- Claim current release evidence without rerunning local gates.

Safe fix:

```bash
python -B scripts/dev.py quality
python -B scripts/dev.py replay-artifact
python -B scripts/dev.py launch-assets
```

Update checked-in release notes first, review `docs/release_note_refresh_checklist.md`, then refresh the release page through the reviewed maintenance path or GitHub UI.

## Missing Replay Attachments

Symptom:

- The release page exists, but `out/demo_replay_artifact.md` or `out/demo_replay_artifact.json` is missing from attachments or linked evidence.
- `python -B scripts/dev.py replay-artifact` has not been run for the current source state.
- A release note claims replay evidence, but no current artifacts are available to attach.

Wrong fix:

- Upload stale artifacts from another checkout.
- Hand-edit trace IDs, timestamps, ports, or PASS rows.
- Commit ignored `out/` artifacts as ordinary source content.

Safe fix:

```bash
python -B scripts/dev.py replay-artifact
git status --short --branch
python -B scripts/dev.py safety
```

Attach the regenerated files externally. Keep `out/` ignored unless a release process explicitly asks for reviewed source-visible evidence.

## Latest-Release Mismatch

Symptom:

- `github-readiness` checks `/releases/latest`, but another release is marked latest.
- `v0.1.0` exists, yet the latest release endpoint points to a different tag.
- Public docs mention the intended release while GitHub shows a different latest release.

Wrong fix:

- Treat any release page as proof that `v0.1.0` is current.
- Change README claims before the latest release state is verified.
- Hide the warning instead of correcting release metadata.

Safe fix:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/dev.py github-maintenance
```

Keep public wording tied to evidence: the release page is current only after the intended tag is the latest release and current replay artifacts are attached or linked.

Use `docs/github_latest_release_troubleshooting_examples.md` when the release page exists but the latest-release pointer, draft/prerelease state, or attachment freshness is still ambiguous. Use `docs/release_asset_upload_dry_run_examples.md` before treating an upload plan as applied release state. Use `docs/github_release_attachment_screenshot_checklist.md` before treating release-page screenshots as attachment evidence.

Use `docs/release_note_changelog_drift_examples.md` before treating changelog-style summaries as release-page evidence.

## Review Checklist

- `docs/github_release_notes_v0.1.0.md` matches the current release claim.
- `docs/release_note_refresh_checklist.md` was used before claiming the release notes, public release page text, or post-publish evidence are current.
- `docs/release_note_changelog_drift_examples.md` was used before reconciling release notes, changelog summaries, release page text, or remote evidence.
- `docs/github_release_commands.md` points to the intended tag and notes file.
- `python -B scripts/dev.py replay-artifact` regenerated the expected `out/` files.
- `out/demo_replay_artifact.md` and `out/demo_replay_artifact.json` are not committed as ordinary source files.
- Release attachment screenshots are compared with `docs/github_release_attachment_screenshot_checklist.md`.
- `python -B scripts/dev.py launch-assets` passes before release-facing wording changes.
- `python -B scripts/dev.py github-readiness` has no hard failures after the release page is updated.
- Public docs do not claim the release page is current until remote checks and attachment review pass.
