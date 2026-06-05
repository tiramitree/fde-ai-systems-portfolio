# GitHub Repository Metadata Troubleshooting Examples

Use this page when `github-readiness` reports repository metadata warnings, or when public launch docs mention repository description, topics, repository URL state, or Discussions setup. Read it with `docs/github_repository_settings.md`, `docs/published_repository_status.md`, `docs/post_publish_checklist.md`, `docs/post_publish_warning_examples.md`, `docs/stale_repository_topics_evidence_examples.md`, `docs/github_discussions_launch_checklist.md`, and `docs/command_output_troubleshooting_map.md`.

The core rule: local launch docs and GitHub account-level repository metadata prove different things. Do not claim metadata is current until GitHub readiness or authenticated maintenance confirms it.

## Expected Evidence Split

Local expected settings:

```bash
python -B scripts/dev.py launch-assets
python -B scripts/dev.py safety
```

These commands prove that release-facing docs stay conservative and point to the expected metadata settings.

Remote metadata proof:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/dev.py github-maintenance
```

`github-readiness` reports the public remote state. `github-maintenance` shows the authenticated maintenance plan, and only an applied authenticated path can change account-level repository metadata.

Use `docs/github_discussions_launch_checklist.md` before treating GitHub Discussions setup, categories, pinned starter topics, or moderation rules as account-level launch evidence.

## Missing Description

Symptom:

- `github-readiness` prints `[WARN] repository description set: missing`.
- `docs/github_repository_settings.md` contains the expected description.
- README copy still refers to the repository as if it is ready to share.

Wrong fix:

- Claim the repository description is set because the expected value is documented.
- Remove the warning row from status docs.
- Edit launch copy around the warning instead of applying the GitHub setting.

Safe fix:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/dev.py github-maintenance
```

Apply the description through the authenticated GitHub UI or maintenance path, then rerun readiness. Keep public wording manual until the remote state reports the expected description.

## Missing Topics

Symptom:

- `github-readiness` prints `[WARN] repository topics set: missing: ...`.
- `docs/github_repository_settings.md` lists the expected topics.
- Local launch checks pass.

Wrong fix:

- Treat local topic documentation as proof that GitHub topics are configured.
- Delete topics from the expected list to avoid a warning.
- Claim discoverability work is complete before the topics are visible on GitHub.

Safe fix:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/dev.py github-maintenance
```

Apply the full topic set from `docs/github_repository_settings.md`. If GitHub rejects a topic, keep the warning visible and update the expected set only when the repository positioning has intentionally changed.

Use `docs/stale_repository_topics_evidence_examples.md` before treating old topic screenshots, wrong topic slugs, unauthenticated API warning rows, cached repository cards, or private account UI crops as current repository-topic evidence.

## Wrong Repository URL

Symptom:

- `github-readiness` or `post_publish_check.py` checks the wrong owner/repository.
- `git remote -v` points to a fork, old test repo, or private URL.
- Raw README checks fail even though the current local repository is healthy.

Wrong fix:

- Change docs to match the accidental remote.
- Claim the public repository is ready because a different repository is reachable.

Safe fix:

```bash
git remote -v
python -B scripts/dev.py github-readiness
python -B scripts/post_publish_check.py
```

Set `origin` to the intended public repository before treating remote checks as launch evidence. Use `docs/published_repository_status.md` to keep local, remote, and public-status claims aligned.

## Stale Public Status

Symptom:

- Local `main` is ahead of `origin/main`.
- `docs/published_repository_status.md` or README links mention recently added docs.
- `post_publish_check.py` still reads older remote files.

Wrong fix:

- Claim remote metadata or published docs from local-only commits.
- Run only local gates and skip remote freshness checks after a push.

Safe fix:

```bash
git status --short --branch
git rev-parse HEAD
git ls-remote origin refs/heads/main
python -B scripts/dev.py fresh-clone
python -B scripts/post_publish_check.py
python -B scripts/dev.py github-readiness
```

Use `fresh-clone-local` for local-only commits and `fresh-clone` only after the intended push is visible. Keep remote metadata claims conservative until the public branch and GitHub API agree.

## Unauthenticated Maintenance Output

Symptom:

- `python -B scripts/dev.py github-maintenance` prints a dry-run plan.
- `gh auth status` is not authenticated or cannot access the repository settings.
- Metadata warnings remain after local docs change.

Wrong fix:

- Treat the dry-run command list as applied setup.
- Add token values or account instructions to public docs.
- Weaken `github-readiness` so unauthenticated environments look complete.

Safe fix:

```bash
python -B scripts/dev.py github-maintenance
python -B scripts/dev.py github-readiness
```

Dry-run output is planning evidence, not remote metadata evidence. Apply account-level changes only through an authenticated maintainer path, then rerun readiness without adding secrets, account tokens, or private setup details to public files.

## Review Checklist

- `docs/github_repository_settings.md` remains the source of truth for expected description and topics.
- `docs/stale_repository_topics_evidence_examples.md` is used before stale topic evidence becomes a public metadata claim.
- `python -B scripts/dev.py github-readiness` has no hard failures in non-strict mode.
- `[WARN] repository description set` and `[WARN] repository topics set` remain follow-up until the remote state confirms them.
- `python -B scripts/dev.py github-maintenance` is treated as dry-run planning unless explicitly applied by an authenticated maintainer.
- `python -B scripts/dev.py launch-assets` passes after release-facing wording changes.
- `python -B scripts/dev.py safety` passes before committing public GitHub setup docs.
- `python -B scripts/dev.py quality` passes before merging repository-readiness wording changes.
- Public docs do not claim repository metadata is current from local launch docs alone.
