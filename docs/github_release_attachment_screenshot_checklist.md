# GitHub Release Attachment Screenshot Checklist

Use this page when collecting or reviewing screenshots that show release replay artifacts attached to GitHub. Read it with `docs/release_attachment_verification_examples.md`, `docs/release_asset_upload_dry_run_examples.md`, `docs/release_asset_checksum_mismatch_examples.md`, `docs/github_release_page_troubleshooting_examples.md`, `docs/github_latest_release_troubleshooting_examples.md`, `docs/post_publish_checklist.md`, `docs/post_publish_warning_examples.md`, and `docs/command_output_troubleshooting_map.md`.

The core rule: generated local artifacts, release-page screenshots, and current public release evidence prove different things. Do not commit private account screenshots, generated `out/` files, or release-attachment claims without matching public evidence.

## Expected Evidence Split

Local replay artifact evidence:

```bash
python -B scripts/dev.py replay-artifact
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Public release evidence:

```bash
python -B scripts/post_publish_check.py
python -B scripts/dev.py github-readiness
```

Release screenshots are review aids. They help compare the visible GitHub release with the expected artifact names, tag, and latest-release state, but they do not replace the generated artifact command, the release page itself, or the post-publish checks.

## Replay Artifact Attachment Screenshots

Capture only when the current replay artifact files are attached or linked on the intended release.

Useful screenshot evidence:

- release tag `v0.1.0`
- attachment names `demo_replay_artifact.md` and `demo_replay_artifact.json`
- release title or notes close enough to compare with `docs/github_release_notes_v0.1.0.md`
- no account menu, private notifications, browser profile data, local paths, or tokens

Wrong use:

- treating a local `out/` folder screenshot as public release evidence
- committing generated `out/demo_replay_artifact.*` files as source content
- claiming attachments are current from a screenshot that does not show the release tag

Review with:

```bash
python -B scripts/dev.py replay-artifact
python -B scripts/dev.py github-readiness
```

Use `docs/release_attachment_verification_examples.md` before turning the screenshot into a release claim.

Use `docs/release_asset_checksum_mismatch_examples.md` before treating screenshot-visible attachments, filenames, local hashes, or changed generated artifact hashes as current release evidence.

## Missing Attachment Screenshots

Capture only when the release page is visible but expected replay artifact attachments are absent.

Useful screenshot evidence:

- release tag or release URL
- visible assets area, attachment area, or notes area showing the missing attachment context
- a dated maintainer note outside git if the screenshot includes account-level UI

Wrong use:

- weakening release docs because a screenshot shows missing attachments
- replacing missing public attachments with checked-in `out/` files
- claiming release evidence from local quality output alone

Review with:

```bash
python -B scripts/dev.py replay-artifact
python -B scripts/dev.py launch-assets
```

Keep the release attachment row manual until the regenerated artifacts are attached or linked on the public release page.

## Stale Attachment Screenshots

Capture only when the screenshot shows attachments that may belong to an older commit, old release notes, or an older replay run.

Useful screenshot evidence:

- release tag and visible attachment names
- release notes snippet that can be compared with `docs/github_release_notes_v0.1.0.md`
- current local `git rev-parse HEAD` recorded in a maintainer note outside git when comparing commit freshness

Wrong use:

- editing trace IDs, timestamps, ports, or PASS rows by hand
- reusing screenshots after `docs/github_release_notes_v0.1.0.md` or replay output changed
- claiming attachment freshness when only the filename is visible

Review with:

```bash
git status --short --branch
git rev-parse HEAD
python -B scripts/dev.py replay-artifact
python -B scripts/dev.py quality
```

If freshness is ambiguous, regenerate the artifacts and refresh the release attachment through the reviewed GitHub maintenance path or UI.

## Wrong Tag Screenshots

Capture only when a screenshot helps diagnose a release or attachment tied to the wrong tag.

Useful screenshot evidence:

- visible tag that differs from the intended `v0.1.0`
- release title or URL showing the mismatched release context
- attachment names only if the screenshot also shows which tag owns them

Wrong use:

- attaching current artifacts to an unintended tag
- changing checked-in release notes to match an accidental release page
- treating any visible attachment as proof that the intended release has current evidence

Review with:

```bash
git rev-parse HEAD
git ls-remote origin refs/heads/main
python -B scripts/dev.py github-readiness
python -B scripts/dev.py github-maintenance
```

Use `docs/github_release_commands.md` as the source of truth for the intended tag and release notes.

## Latest-Release Attachment Screenshots

Capture only when the latest-release selection and attachment state need to be reviewed together.

Useful screenshot evidence:

- visible latest-release marker, release URL, or release header
- intended `v0.1.0` tag
- current replay artifact attachment names or reviewed links
- no private account UI, collaborator lists, notification panes, or local filesystem details

Wrong use:

- treating latest-release visibility as proof that attachments are fresh
- treating attachment filenames as proof that the selected release is latest
- claiming latest-release state from maintainer-only draft visibility

Review with:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/check_github_readiness.py --strict
```

Use `docs/github_latest_release_troubleshooting_examples.md` when latest-release state, draft state, prerelease state, or attachment freshness is ambiguous.

## Screenshot Handling Rules

- Keep release screenshots outside git unless a release process explicitly asks for a reviewed, redacted artifact.
- Crop or redact browser chrome, account menus, notifications, private repository lists, local paths, and tokens.
- Prefer public release page screenshots over authenticated settings screenshots when public evidence can prove the claim.
- Pair every screenshot claim with the command or source doc that owns the relevant evidence boundary.
- Do not use screenshots to bypass `python -B scripts/dev.py replay-artifact`, `python -B scripts/post_publish_check.py`, or `python -B scripts/dev.py github-readiness`.

## Review Checklist

- `docs/release_attachment_verification_examples.md` remains the source for attachment troubleshooting.
- `docs/release_asset_upload_dry_run_examples.md` remains the source for upload-plan and generated-`out/` boundaries.
- `docs/release_asset_checksum_mismatch_examples.md` remains the source for checksum mismatch review.
- `docs/github_release_page_troubleshooting_examples.md` remains the source for release-page drift.
- `docs/github_latest_release_troubleshooting_examples.md` remains the source for latest-release ambiguity.
- `docs/post_publish_checklist.md` keeps release attachment review as a manual GitHub step.
- Public release claims are backed by public release evidence, not local `out/` screenshots.
- Private account screenshots, generated `out/` files, local paths, and tokens are not committed.
- `python -B scripts/dev.py replay-artifact`, `python -B scripts/dev.py launch-assets`, `python -B scripts/dev.py safety`, and `python -B scripts/dev.py quality` pass after changing release attachment wording.
