# Release Note Changelog Drift Examples

Use this page when release notes, changelog-style summaries, GitHub release-page text, or post-publish evidence disagree. Read it with `docs/release_note_refresh_checklist.md`, `docs/github_release_page_troubleshooting_examples.md`, `docs/github_latest_release_troubleshooting_examples.md`, and `docs/post_publish_checklist.md`.

The core rule: release notes, changelog summaries, release page text, and remote evidence are different things. Do not claim changelog freshness until public evidence confirms it.

This page covers checked-in release notes drift, changelog-style summary drift, GitHub release-page drift, and post-publish evidence mismatch.

## Expected Evidence Split

Checked-in source:

```bash
git diff -- docs/github_release_notes_v0.1.0.md CHANGELOG.md README.md
python -B scripts/dev.py launch-assets
```

Local verification:

```bash
python -B scripts/dev.py replay-artifact
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Remote publication proof after push and release maintenance:

```bash
python -B scripts/dev.py fresh-clone
python -B scripts/post_publish_check.py
python -B scripts/dev.py github-readiness
```

Local notes and changelog-style summaries can describe intended release content. Remote evidence proves what public visitors can actually see.

## Checked-In Release Notes Drift

Symptom:

- `docs/github_release_notes_v0.1.0.md` mentions old smoke, eval, API contract, or replay evidence.
- README release wording was updated, but the checked-in release note source still describes an older state.
- The release note source omits a new release-facing doc or troubleshooting path.

Wrong fix:

- Edit GitHub release-page text first and leave the checked-in notes stale.
- Copy old PASS rows into the release note source without rerunning the matching gate.
- Treat ignored `out/` replay artifacts as if they were release note source files.

Safe fix:

```bash
python -B scripts/dev.py claims
python -B scripts/dev.py launch-assets
git diff -- docs/github_release_notes_v0.1.0.md
```

Refresh the checked-in note source first. If the evidence changed, rerun the command that proves the new count before copying it into release-facing text.

## Changelog-Style Summary Drift

Symptom:

- `CHANGELOG.md`, README release summaries, or launch copy describe a different feature set than `docs/github_release_notes_v0.1.0.md`.
- A compact summary says a capability is published, but post-publish evidence still sees the old remote branch.
- A changelog-style note compresses several changes into one claim and drops the required verification boundary.

Wrong fix:

- Make the changelog-style summary more confident than the evidence.
- Remove caveats about GitHub account-level actions, release attachments, branch protection, or latest-release state.
- Treat local `quality` output as proof that public release notes are fresh.

Safe fix:

```bash
git status --short --branch
python -B scripts/dev.py launch-assets
python -B scripts/dev.py safety
```

Keep summaries conservative. A changelog-style summary can say what changed in source, but it should not claim remote publication, latest-release freshness, or attachment freshness until those checks pass.

## GitHub Release-Page Drift

Symptom:

- The public GitHub release page exists, but its body differs from `docs/github_release_notes_v0.1.0.md`.
- The latest-release page points at the intended tag, but the page text still describes older local evidence.
- A maintainer updates release notes locally and forgets to refresh the public page.

Wrong fix:

- Claim the release page is current because raw README or raw release notes are reachable.
- Hand-edit the GitHub page without reviewing checked-in release notes.
- Treat any visible release page as proof that the latest release is fresh.

Safe fix:

```bash
python -B scripts/dev.py github-maintenance
python -B scripts/dev.py github-readiness
python -B scripts/check_github_readiness.py --strict
```

Use `docs/github_release_page_troubleshooting_examples.md` for page text drift and `docs/github_latest_release_troubleshooting_examples.md` for latest-release selection, draft state, prerelease state, or attachment freshness.

## Post-Publish Evidence Mismatch

Symptom:

- Local `main` is ahead of `origin/main`, but source docs already describe public release evidence.
- `fresh-clone-local` passes, while `fresh-clone`, `post_publish_check.py`, or `github-readiness` still sees stale remote files.
- Release notes, changelog-style summaries, latest-release state, and replay attachments disagree.

Wrong fix:

- Weaken post-publish checks to match stale remote content.
- Hide `[WARN]` or `[MANUAL]` rows instead of treating them as account-level follow-up.
- Claim changelog freshness from a local commit that has not been pushed.

Safe fix:

```bash
git status --short --branch
git ls-remote origin refs/heads/main
python -B scripts/dev.py fresh-clone
python -B scripts/post_publish_check.py
python -B scripts/dev.py github-readiness
```

Use `docs/post_publish_checklist.md` after push. Until remote checks confirm the current branch, keep changelog freshness and release-page freshness as intended source state, not public evidence.

## Review Checklist

- `docs/release_note_refresh_checklist.md` was used before changing checked-in release notes or release-facing summaries.
- `docs/github_release_page_troubleshooting_examples.md` was used before claiming GitHub release-page text is current.
- `docs/github_latest_release_troubleshooting_examples.md` was used before claiming latest-release freshness.
- `docs/post_publish_checklist.md` was used before claiming public remote evidence.
- `python -B scripts/dev.py replay-artifact` regenerated local replay evidence when release-facing evidence changed.
- `python -B scripts/dev.py launch-assets`, `python -B scripts/dev.py safety`, and `python -B scripts/dev.py quality` passed after release wording changed.
- Release notes, changelog summaries, release page text, and remote evidence remain separate.
- Public docs do not claim changelog freshness until public evidence confirms the current branch, intended tag, public page text, and current replay attachment path.
