# Release Note Refresh Checklist

Use this page when release notes, GitHub release-page text, replay artifacts, or post-publish evidence change. Read it with `docs/github_release_notes_v0.1.0.md`, `docs/github_release_commands.md`, `docs/release_asset_upload_dry_run_examples.md`, `docs/release_note_changelog_drift_examples.md`, `docs/github_release_page_troubleshooting_examples.md`, `docs/github_latest_release_troubleshooting_examples.md`, and `docs/post_publish_checklist.md`.

The core rule: checked-in release notes, generated replay artifacts, GitHub release-page text, and post-publish evidence prove different things. Do not claim release notes are current until public release evidence confirms it.

## Expected Evidence Split

Checked-in release note source:

```bash
git diff -- docs/github_release_notes_v0.1.0.md
python -B scripts/dev.py launch-assets
```

Generated replay artifact proof:

```bash
python -B scripts/dev.py replay-artifact
git status --ignored --short eval_summaries.csv otel_traces.json out
```

Local release-safety proof:

```bash
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Remote publication proof after push and release maintenance:

```bash
python -B scripts/dev.py fresh-clone
python -B scripts/post_publish_check.py
python -B scripts/dev.py github-readiness
```

`docs/github_release_notes_v0.1.0.md` is the source text for the intended release. The GitHub release page becomes evidence only after the page exists, the public text matches the checked-in notes, and current replay artifacts are attached or linked.

## Refresh Order

1. Review the current release claim in `docs/github_release_notes_v0.1.0.md`.
2. Regenerate local replay artifacts with `python -B scripts/dev.py replay-artifact` if eval, smoke, trace, API, screenshot, or release evidence changed.
3. Compare upload planning with `docs/release_asset_upload_dry_run_examples.md`.
4. Run local gates before changing public wording.
5. Push intentionally, refresh or recreate the GitHub release page through `docs/github_release_commands.md`, then run post-publish checks.
6. Keep release-page and latest-release claims manual until `docs/github_latest_release_troubleshooting_examples.md` and `docs/post_publish_checklist.md` agree with public evidence.

Use `docs/release_note_changelog_drift_examples.md` before summarizing drift across release notes, changelog summaries, release page text, or post-publish evidence.

## Stale Release Notes

Symptom:

- `docs/github_release_notes_v0.1.0.md` mentions old eval, smoke, API contract, or quality results.
- README release wording was updated, but the checked-in release notes still describe a previous evidence set.
- A maintainer wants to refresh the GitHub release page without reviewing the tracked notes file.

Wrong fix:

- Edit the GitHub release page first and leave checked-in notes stale.
- Copy old PASS counts into new release text without rerunning gates.
- Describe ignored `out/` artifacts as if they were source-controlled release notes.

Safe fix:

```bash
python -B scripts/dev.py claims
python -B scripts/dev.py launch-assets
git diff -- docs/github_release_notes_v0.1.0.md
```

Update checked-in notes first. If evidence counts changed, rerun the proof commands that produce those counts before refreshing public release text.

## Stale GitHub Release-Page Text

Symptom:

- The public release page exists, but its body does not match `docs/github_release_notes_v0.1.0.md`.
- `post_publish_check.py` proves files are reachable, but the release page still shows older wording.
- GitHub latest release points to the intended tag, but the page body still describes old local evidence.

Wrong fix:

- Claim release-page freshness from local README or raw file reachability.
- Hand-edit the release page without updating the tracked notes file.
- Treat a visible release page as proof that the release text is current.

Safe fix:

```bash
python -B scripts/dev.py github-maintenance
python -B scripts/dev.py github-readiness
python -B scripts/check_github_readiness.py --strict
```

Use `docs/github_release_commands.md` as the source of truth for the intended tag and notes file. Keep release-page freshness manual until the public page text matches the reviewed checked-in notes.

## Replay Artifact Drift

Symptom:

- `out/demo_replay_artifact.md` or `out/demo_replay_artifact.json` exists, but source docs or demo behavior changed afterward.
- Release notes mention replay evidence, but the local artifacts were not regenerated from the current commit.
- GitHub release attachments exist, but they may come from another commit or an older local run.

Wrong fix:

- Hand-edit generated replay artifacts to match desired release text.
- Commit ignored `out/` files as ordinary documentation.
- Reuse old attachments because filenames still match.

Safe fix:

```bash
git rev-parse HEAD
python -B scripts/dev.py replay-artifact
python -B scripts/dev.py quality
```

Generated artifacts stay under ignored `out/`. Use `docs/release_asset_upload_dry_run_examples.md` before treating local replay output as upload-ready release evidence.

## Post-Publish Evidence Mismatch

Symptom:

- Local `main` is ahead of `origin/main`, but release notes or README already describe public release evidence.
- `fresh-clone-local` passes while `fresh-clone`, `post_publish_check.py`, or `github-readiness` still sees stale remote content.
- GitHub latest-release, release-page text, and checked-in notes disagree.

Wrong fix:

- Lower post-publish expectations to match stale remote state.
- Claim release notes are current from local quality output alone.
- Hide `[WARN]` or `[MANUAL]` rows instead of tracking them as account-level follow-up.

Safe fix:

```bash
git status --short --branch
git ls-remote origin refs/heads/main
python -B scripts/dev.py fresh-clone
python -B scripts/post_publish_check.py
python -B scripts/dev.py github-readiness
```

Use `docs/post_publish_checklist.md` after push. Use `docs/github_latest_release_troubleshooting_examples.md` when the latest-release pointer, draft state, prerelease state, or release attachment freshness is ambiguous.

## Review Checklist

- `docs/github_release_notes_v0.1.0.md` is the reviewed source of release-page text.
- `docs/github_release_commands.md` still points to the intended tag and notes file.
- `python -B scripts/dev.py replay-artifact` regenerated current local replay evidence when release-facing evidence changed.
- `docs/release_asset_upload_dry_run_examples.md` was used before treating generated artifacts as upload inputs.
- `python -B scripts/dev.py launch-assets`, `python -B scripts/dev.py safety`, and `python -B scripts/dev.py quality` passed after release-facing wording changed.
- `python -B scripts/post_publish_check.py` and `python -B scripts/dev.py github-readiness` are used after push before public release freshness is claimed.
- Checked-in release notes, generated replay artifacts, GitHub release-page text, and post-publish evidence remain separate.
- Release notes, changelog summaries, release page text, and remote evidence stay separate when summarized through `docs/release_note_changelog_drift_examples.md`.
- Public docs do not claim release notes are current until public release evidence confirms the intended tag, page text, and current replay attachments.
