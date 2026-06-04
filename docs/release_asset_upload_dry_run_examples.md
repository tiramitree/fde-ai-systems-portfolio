# Release Asset Upload Dry-Run Examples

Use this page when planning or reviewing release asset uploads. Read it with `docs/release_attachment_verification_examples.md`, `docs/release_asset_checksum_mismatch_examples.md`, `docs/github_release_commands.md`, `docs/release_note_refresh_checklist.md`, `docs/github_release_page_troubleshooting_examples.md`, `docs/github_release_attachment_screenshot_checklist.md`, and `docs/post_publish_checklist.md`.

The core rule: dry-run plans, generated replay artifacts, source-controlled docs, and published GitHub release state prove different things. Do not claim release assets were uploaded until public release evidence confirms it.

## Expected Evidence Split

Local artifact proof:

```bash
python -B scripts/dev.py replay-artifact
git status --short --branch
```

Local release-safety proof:

```bash
python -B scripts/dev.py launch-assets
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Remote release proof after push and release maintenance:

```bash
python -B scripts/dev.py fresh-clone
python -B scripts/post_publish_check.py
python -B scripts/dev.py github-readiness
```

Authenticated maintenance dry-run:

```bash
python -B scripts/dev.py github-maintenance
```

`python -B scripts/dev.py github-maintenance` prints the release setup plan. It does not prove the release page exists, and it does not upload `out/demo_replay_artifact.md` or `out/demo_replay_artifact.json`.

Use `docs/release_asset_checksum_mismatch_examples.md` before treating local hashes, changed generated artifact hashes, public attachment hashes, or screenshot-visible attachments as uploaded release evidence.

## Missing Replay Artifacts

Symptom:

- `out/demo_replay_artifact.md` or `out/demo_replay_artifact.json` is missing.
- A maintainer drafts upload commands before regenerating release evidence.
- The release page exists, but there is no current local artifact pair to attach.

Wrong fix:

- Upload old artifacts from another checkout.
- Commit hand-written replay files under `docs/`.
- Remove `out/` from `.gitignore` to make the files easier to find.

Safe fix:

```bash
python -B scripts/dev.py replay-artifact
git status --short --branch
```

Keep the generated files under `out/`. They are upload inputs, not source docs.

## Stale Local Artifacts

Symptom:

- `out/demo_replay_artifact.*` exists, but source files changed after it was generated.
- The JSON artifact has old trace IDs, ports, timestamps, or evidence counts.
- A dry-run command lists files that do not match the current release commit.

Wrong fix:

- Edit trace IDs, timestamps, ports, or PASS rows by hand.
- Trust existing artifact filenames without regenerating them.
- Treat local `quality` output as proof that the artifact pair is current.

Safe fix:

```bash
git status --short --branch
git rev-parse HEAD
python -B scripts/dev.py replay-artifact
python -B scripts/dev.py quality
```

Regenerate immediately before upload planning. If the branch is intentionally ahead of `origin/main`, keep release-page claims manual until the push and remote checks finish.

## Wrong Release Tag

Symptom:

- The upload plan targets a tag other than `v0.1.0`.
- The release page exists, but it is not the intended release from `docs/github_release_commands.md`.
- The local HEAD does not match the pushed commit used for the release.

Wrong fix:

- Attach current artifacts to whatever release page is easiest to reach.
- Change checked-in release notes to match an accidental tag.
- Claim upload completion because a release page with attachments exists.

Safe fix:

```bash
git rev-parse HEAD
git ls-remote origin refs/heads/main
python -B scripts/dev.py github-readiness
```

Use `docs/github_release_commands.md` as the source of truth for the intended tag and release notes. Use `docs/release_note_refresh_checklist.md` before changing release-page text to match a generated artifact. Keep the upload plan tied to `v0.1.0` unless a reviewed release process changes the target.

## GitHub Release Page Not Found

Symptom:

- `github-readiness` reports the release page as missing.
- `python -B scripts/dev.py github-maintenance` prints a release setup command, but it has not been applied.
- A reviewer asks whether assets can be uploaded before the release exists.

Wrong fix:

- Treat the dry-run plan as a created release.
- Upload artifacts to an unrelated release.
- Commit `out/` files as a substitute for public release assets.

Safe fix:

```bash
python -B scripts/dev.py github-maintenance
python -B scripts/dev.py github-readiness
```

After authenticated release creation is intentionally applied and visible, review the asset upload command before running it:

```bash
gh release upload v0.1.0 out/demo_replay_artifact.md out/demo_replay_artifact.json --repo tiramitree/fde-ai-systems-portfolio
```

Use `--clobber` only when intentionally replacing stale release assets after regenerating and reviewing the current artifact pair.

## Generated out/ Handling

Symptom:

- `out/demo_replay_artifact.md` or `out/demo_replay_artifact.json` appears in `git status --short`.
- A PR includes generated replay artifacts as source files.
- A release checklist asks whether generated artifacts should be committed.

Wrong fix:

- Add generated `out/` files to git as ordinary docs.
- Paste generated JSON into release notes.
- Hide generated-file drift by weakening safety or launch checks.

Safe fix:

```bash
git status --short --branch
git diff --stat
git diff --check
```

Generated replay artifacts should stay ignored and be uploaded externally to the GitHub release page. If a release process explicitly asks for source-visible evidence, document that exception before committing anything generated.

## Review Checklist

- `python -B scripts/dev.py replay-artifact` regenerated `out/demo_replay_artifact.md` and `out/demo_replay_artifact.json`.
- `python -B scripts/dev.py launch-assets`, `python -B scripts/dev.py safety`, and `python -B scripts/dev.py quality` passed after release-facing wording changed.
- The upload plan targets `v0.1.0` from `docs/github_release_commands.md`.
- Checked-in release notes and release-page text are reviewed with `docs/release_note_refresh_checklist.md`.
- The release page exists before upload commands are treated as actionable.
- Dry-run output is not described as an applied GitHub release state.
- Checksum mismatches are reviewed with `docs/release_asset_checksum_mismatch_examples.md` before upload plans are treated as current release evidence.
- `out/` files remain ignored and are not committed as ordinary source content.
- `docs/github_release_attachment_screenshot_checklist.md` is used before screenshots become release evidence.
