# Stale Release-Page Screenshot Examples

Use this page when GitHub release-page screenshots, latest-release screenshots, attachment screenshots, wrong-tag screenshots, or private account UI crops may no longer reflect the current repository state. Read it with `docs/github_release_page_troubleshooting_examples.md`, `docs/github_latest_release_troubleshooting_examples.md`, `docs/github_release_attachment_screenshot_checklist.md`, and `docs/post_publish_warning_examples.md`.

The core rule: release-page existence, latest-release selection, attachment state, screenshot evidence, and private account UI prove different things. Do not claim a release page is current until public evidence confirms it.

## Expected Evidence Split

Local release proof:

```bash
python -B scripts/dev.py replay-artifact
python -B scripts/dev.py launch-assets
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Public release proof after push:

```bash
python -B scripts/post_publish_check.py
python -B scripts/dev.py github-readiness
```

Screenshots are review aids. They can help explain a mismatch, but they do not replace the public release page, current attachment state, release notes, or generated replay artifacts.

Review old release-page screenshots, stale latest-release screenshots, missing attachment screenshots, wrong-tag screenshots, and private account UI crops as separate evidence surfaces.

## Old Release-Page Screenshots

Use this when a screenshot shows the release page from an earlier source state.

Symptom:

- The screenshot shows release text that no longer matches `docs/github_release_notes_v0.1.0.md`.
- The screenshot predates a README, eval, replay artifact, or release-note change.
- The screenshot is reused in a launch note as if it proves the current release.

Wrong fix:

- Claim the release page is current from the old screenshot.
- Edit source docs to match the screenshot.
- Keep an old screenshot in source as release evidence.

Safe fix:

```bash
git status --short --branch
python -B scripts/dev.py replay-artifact
python -B scripts/dev.py launch-assets
```

Use `docs/github_release_page_troubleshooting_examples.md` to compare tag, release notes, and attachment state. Keep the public claim manual until the current release page is visible and matches the intended source state.

## Stale Latest-Release Screenshots

Use this when a screenshot shows a latest-release page that may no longer be the selected latest release.

Symptom:

- The screenshot shows a release header, but not the latest-release selection or current tag.
- `/releases/latest` or `github-readiness` points somewhere else.
- A draft, prerelease, or newer release changed the public latest pointer.

Wrong fix:

- Treat a release-page screenshot as latest-release proof.
- Treat a latest-release screenshot as attachment freshness proof.
- Hide readiness warnings because an older screenshot looked correct.

Safe fix:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/check_github_readiness.py --strict
```

Use `docs/github_latest_release_troubleshooting_examples.md` before claiming latest-release freshness. The latest release is current only when the intended tag, latest pointer, public visibility, and attachment evidence agree.

## Missing Attachment Screenshots

Use this when a screenshot shows a release page without the expected replay artifacts.

Symptom:

- The screenshot shows the release page but no `demo_replay_artifact.md` or `demo_replay_artifact.json`.
- Local `out/` artifacts exist but are not attached or linked publicly.
- A launch note claims replay evidence even though the screenshot shows missing attachments.

Wrong fix:

- Commit ignored `out/` files to make the evidence visible.
- Claim attachments are current because local artifacts exist.
- Crop away the missing attachments area and reuse the screenshot.

Safe fix:

```bash
python -B scripts/dev.py replay-artifact
python -B scripts/dev.py safety
python -B scripts/dev.py github-readiness
```

Use `docs/github_release_attachment_screenshot_checklist.md` to review what the screenshot can and cannot prove. Keep attachment claims manual until public release evidence shows the expected files or reviewed links.

## Wrong-Tag Screenshots

Use this when a screenshot belongs to a tag other than the intended release.

Symptom:

- The screenshot URL, header, or tag differs from `v0.1.0`.
- The screenshot shows attachments from another release.
- The release notes or title match a different release candidate.

Wrong fix:

- Attach current artifacts to the easiest visible release page.
- Change checked-in release notes to match an accidental tag.
- Treat any visible release screenshot as proof of the intended release.

Safe fix:

```bash
git rev-parse HEAD
git ls-remote origin refs/heads/main
python -B scripts/dev.py github-readiness
```

Use `docs/github_release_page_troubleshooting_examples.md` and `docs/github_latest_release_troubleshooting_examples.md` to keep tag existence, release-page existence, and latest-release selection separate.

## Private Account UI Crops

Use this when a screenshot includes authenticated GitHub UI, account menus, notification panes, private repository lists, browser profile details, or collaborator/admin controls.

Symptom:

- The screenshot proves what the maintainer saw while signed in, not what public visitors can verify.
- The crop includes account-level UI, profile data, notifications, or private repository names.
- The screenshot is being considered for source docs or public launch material.

Wrong fix:

- Commit the authenticated screenshot as public evidence.
- Crop only the obvious account menu while leaving private UI clues.
- Treat maintainer-only draft visibility as public release evidence.

Safe fix:

```bash
python -B scripts/dev.py safety
python -B scripts/dev.py launch-assets
```

Prefer public release URLs, readiness output, or a redacted maintainer note kept outside git. If a screenshot must be retained for private review, keep it outside source and record only the neutral technical finding.

## Review Checklist

- `docs/github_release_page_troubleshooting_examples.md` remains the source for release-page drift.
- `docs/github_latest_release_troubleshooting_examples.md` remains the source for latest-release ambiguity.
- `docs/github_release_attachment_screenshot_checklist.md` remains the source for release attachment screenshot handling.
- `docs/post_publish_warning_examples.md` remains the source when local docs and remote public evidence disagree.
- Release-page existence, latest-release selection, attachment state, screenshot evidence, and private account UI stay separate.
- Old release-page screenshots, stale latest-release screenshots, missing attachment screenshots, wrong-tag screenshots, and private account UI crops are reviewed against current public evidence.
- Private account screenshots, account menus, notifications, private repository lists, local paths, browser profile details, and tokens are not committed.
- Do not claim a release page is current until public evidence confirms it.
- `python -B scripts/dev.py replay-artifact`, `python -B scripts/dev.py launch-assets`, `python -B scripts/dev.py safety`, and `python -B scripts/dev.py quality` pass after changing release-page screenshot wording.
