# Release Asset Checksum Mismatch Examples

Use this page when generated replay artifacts, release attachment hashes, local manifests, screenshots, or public GitHub release evidence disagree. Read it with `docs/release_attachment_verification_examples.md`, `docs/release_asset_upload_dry_run_examples.md`, `docs/github_release_attachment_screenshot_checklist.md`, and `docs/post_publish_warning_examples.md`.

The core rule: generated local artifacts, source-controlled docs, uploaded release attachments, screenshots, checksums, and post-publish evidence prove different things. Do not claim release assets are current until public evidence confirms them.

## Expected Evidence Split

Regenerate local release evidence:

```bash
python -B scripts/dev.py replay-artifact
git status --short --branch
```

Review local release-facing claims:

```bash
python -B scripts/dev.py launch-assets
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Review public release evidence after push:

```bash
python -B scripts/post_publish_check.py
python -B scripts/dev.py github-readiness
```

Optional checksum capture on Windows:

```powershell
Get-FileHash out/demo_replay_artifact.md -Algorithm SHA256
Get-FileHash out/demo_replay_artifact.json -Algorithm SHA256
```

Keep checksum notes tied to the release tag, commit SHA, artifact filenames, and observation time. A checksum by itself does not prove that the public release page has the matching attachment.

## Stale Local Replay Artifacts

Use this when local `out/demo_replay_artifact.*` files exist but were generated before the current source change.

Symptom:

- `out/demo_replay_artifact.md` or `out/demo_replay_artifact.json` exists from an earlier run.
- The source branch, release notes, or demo evidence changed after the artifact was generated.
- The old artifact hash no longer represents the current release candidate.

Wrong fix:

- Reuse the old checksum because the filename is unchanged.
- Edit trace IDs, timestamps, ports, PASS rows, or JSON fields by hand.
- Commit generated `out/` files as ordinary source docs.

Safe fix:

```bash
git status --short --branch
python -B scripts/dev.py replay-artifact
python -B scripts/dev.py quality
```

Recalculate hashes only after regeneration. Treat changed hashes as normal generated evidence churn unless the current source state was expected to be identical.

## Changed Generated Artifact Hashes

Use this when the regenerated Markdown or JSON artifact has a different hash from a previous maintainer note.

Symptom:

- The regenerated artifact hash differs from the old local hash note.
- The artifact body changed because trace IDs, timestamps, ports, or eval run IDs were regenerated.
- The release upload plan still references the older hash.

Wrong fix:

- Modify generated files to match an old checksum.
- Weaken the release claim so the mismatch is ignored.
- Treat hash drift as a source-code failure without reviewing the regenerated artifact.

Safe fix:

```bash
python -B scripts/dev.py replay-artifact
python -B scripts/dev.py launch-assets
python -B scripts/dev.py safety
```

Compare the artifact names, command output, and expected replay checks. If the regenerated artifact is valid, update the release upload note or attachment plan to the new checksum.

## Missing Public Attachments

Use this when local hashes exist but the public GitHub release page does not show matching attachments.

Symptom:

- Local `Get-FileHash` output exists for both replay artifacts.
- `github-readiness` or manual release review reports missing attachments.
- A screenshot shows the release page without the expected artifact files.

Wrong fix:

- Claim assets are current because local hashes were captured.
- Paste local hashes into README as a substitute for public attachment evidence.
- Commit generated replay artifacts to bypass release upload work.

Safe fix:

```bash
python -B scripts/dev.py replay-artifact
python -B scripts/dev.py github-readiness
python -B scripts/post_publish_check.py
```

Use `docs/release_asset_upload_dry_run_examples.md` before upload planning. Keep release-page claims manual until the public page shows the expected attachments or reviewed links.

## Wrong Release Tag Checksums

Use this when a checksum note or screenshot belongs to a tag other than the intended release.

Symptom:

- The checksum note mentions a tag other than `v0.1.0`.
- A screenshot shows attachments on a different release page.
- The release page exists, but it points to a different commit than the reviewed branch.

Wrong fix:

- Attach current artifacts to whichever release page is easiest to reach.
- Change checked-in release notes to match an accidental tag.
- Treat an attachment hash from the wrong tag as proof for the intended release.

Safe fix:

```bash
git rev-parse HEAD
git ls-remote origin refs/heads/main
python -B scripts/dev.py github-readiness
```

Use `docs/github_release_commands.md` as the intended tag source. Recompute hashes after confirming the reviewed commit and release tag are aligned.

## Post-Publish Checksum Drift

Use this when remote files are reachable but public release attachment evidence still looks stale.

Symptom:

- `post_publish_check.py` proves source files are reachable on GitHub.
- The release page attachment hash, screenshot, or maintainer note still reflects an older artifact.
- Local `fresh-clone-local` passes while remote release evidence is pending.

Wrong fix:

- Treat raw README reachability as attachment checksum proof.
- Delete the release attachment requirement from public checks.
- Claim release assets are current while the public release page still shows older files.

Safe fix:

```bash
python -B scripts/dev.py fresh-clone
python -B scripts/post_publish_check.py
python -B scripts/dev.py github-readiness
```

If local commits are intentionally ahead of `origin/main`, use `fresh-clone-local` for local proof only. Keep checksum and attachment freshness manual until the branch is pushed and public release evidence is rechecked.

## Review Checklist

- `docs/release_attachment_verification_examples.md` remains the source for attachment troubleshooting.
- `docs/release_asset_upload_dry_run_examples.md` remains the source for upload-plan boundaries.
- `docs/github_release_attachment_screenshot_checklist.md` remains the source for screenshot evidence boundaries.
- `docs/post_publish_warning_examples.md` remains the source for remote freshness and warning rows.
- Generated local artifacts, source-controlled docs, uploaded release attachments, screenshots, checksums, and post-publish evidence stay separate.
- Checksums are tied to the release tag, commit SHA, artifact filename, and observation time.
- Changed generated artifact hashes are reviewed instead of hand-edited.
- Public release claims stay manual until the intended release page shows the current attachments or reviewed links.
- Generated `out/` files remain ignored unless a reviewed release process explicitly asks for source-visible evidence.
- `python -B scripts/dev.py replay-artifact`, `python -B scripts/dev.py launch-assets`, `python -B scripts/dev.py safety`, and `python -B scripts/dev.py quality` pass after changing checksum or release-asset wording.
