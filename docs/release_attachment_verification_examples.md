# Release Attachment Verification Examples

Use this page when preparing or reviewing release evidence attachments. Read it with `docs/github_release_commands.md`, `docs/github_release_page_troubleshooting_examples.md`, `docs/post_publish_checklist.md`, `docs/command_output_troubleshooting_map.md`, and `docs/demo_replay_artifact.md`.

The core rule: release attachments are generated evidence, not source content. Regenerate them from the release commit, attach them to the release page or review notes, and keep `out/` ignored unless a release process explicitly asks for a reviewed source diff.

## Expected Attachment Set

Generate the local evidence package with:

```bash
python -B scripts/dev.py replay-artifact
```

The expected files are:

- `out/demo_replay_artifact.md`
- `out/demo_replay_artifact.json`

Before publishing or claiming the release page is current, run:

```bash
python -B scripts/dev.py launch-assets
python -B scripts/post_publish_check.py
python -B scripts/dev.py quality
```

Use `python -B scripts/dev.py fresh-clone-local` before push, and `python -B scripts/dev.py fresh-clone` after the pushed branch is visible.

## Missing Replay Artifacts

Symptom:

- `out/demo_replay_artifact.md` or `out/demo_replay_artifact.json` is missing.
- A release note says replay evidence is attached, but there is no local artifact to upload.

Wrong fix:

- Copy an old artifact from another checkout.
- Commit a hand-written replacement under `out/` or `docs/`.

Safe fix:

```bash
python -B scripts/dev.py replay-artifact
git status --short --branch
```

Attach the newly generated `out/` files externally. Do not commit them as source content.

## Stale Attachments

Symptom:

- The artifact was generated before the current release commit.
- The Markdown says replay checks passed, but the current branch has changed since generation.
- The JSON evidence count or labels do not match the current `docs/demo_replay_artifact.md` expectations.

Wrong fix:

- Reuse the stale file because it still has `PASS` rows.
- Edit trace IDs, timestamps, ports, or evidence rows by hand.

Safe fix:

```bash
git status --short --branch
python -B scripts/dev.py replay-artifact
python -B scripts/dev.py quality
```

If the regenerated artifact changes, treat that as normal runtime evidence churn. Upload the regenerated attachments, not the stale copies.

## Wrong Release Tag

Symptom:

- The release page is for a different tag than the commit being reviewed.
- The attached replay evidence came from a local commit that is not pushed.
- `python -B scripts/post_publish_check.py` proves the public branch is reachable, but not that the release page attachment is current.

Wrong fix:

- Claim the release page is ready from local quality output alone.
- Attach local evidence to a tag without checking that the tag points to the intended release commit.

Safe fix:

```bash
git status --short --branch
git rev-parse HEAD
git ls-remote origin refs/heads/main
python -B scripts/dev.py replay-artifact
python -B scripts/post_publish_check.py
```

Only claim the release page is current after the tag/page exists and the current replay artifacts are attached or linked.

## Generated out/ Handling

Symptom:

- `out/demo_replay_artifact.*` appears in a source diff.
- A PR adds copied release evidence instead of instructions or checked-in docs.
- A reviewer cannot tell whether a file is source content or generated local evidence.

Wrong fix:

- Remove `out/` from `.gitignore`.
- Commit local ports, timestamps, trace IDs, or generated replay payloads as ordinary docs.

Safe fix:

```bash
git diff --stat
git diff --check
git status --short --branch
```

Keep generated replay files out of commits unless a release process explicitly asks for source-visible evidence. If that exception is used, explain why the artifact is intentionally tracked and run `python -B scripts/dev.py safety`.

## Post-Publish Mismatch

Symptom:

- The local README or release docs mention files that are not visible on GitHub yet.
- `python -B scripts/post_publish_check.py` fails for a required published file.
- GitHub readiness shows manual or warning rows for release page state.

Wrong fix:

- Treat local `quality` as proof that remote release assets are published.
- Delete the post-publish check or weaken the release claim.

Safe fix:

```bash
python -B scripts/dev.py fresh-clone
python -B scripts/post_publish_check.py
python -B scripts/dev.py github-readiness
```

If the branch is intentionally ahead only locally, use `python -B scripts/dev.py fresh-clone-local` and keep the release-page wording manual until the push and post-publish checks pass.

## Review Checklist

- The branch is clean except for intentional source changes.
- `python -B scripts/dev.py replay-artifact` regenerated the two expected `out/` files.
- Attachments are uploaded externally or described as manual follow-up.
- `out/` files are not committed as ordinary source content.
- The release tag or page points to the intended commit.
- `python -B scripts/dev.py launch-assets` passed.
- `python -B scripts/post_publish_check.py` passed after push, or the release claim stays manual.
- `python -B scripts/dev.py quality` passed before publishing release-facing claims.
