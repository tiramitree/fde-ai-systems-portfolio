# Public Maintainer Status Update Examples

Use this page when publishing a maintainer update in an issue, discussion, release note, launch thread, or repository status note. Read it with `docs/published_repository_status.md`, `docs/post_publish_checklist.md`, `docs/post_publish_warning_examples.md`, `docs/issue_template_stale_evidence_examples.md`, `docs/github_authenticated_maintenance_troubleshooting_examples.md`, and `docs/launch_feedback_collection_examples.md`.

The core rule: local quality, pushed code, remote GitHub evidence, account-level/manual setup, and roadmap promises are separate. Do not imply delivery dates, production support, private access, or completed setup before evidence exists.

## Expected Evidence Split

Local progress:

```bash
git status --short --branch
python -B scripts/dev.py quality
python -B scripts/dev.py fresh-clone-local
```

Pushed-code and remote evidence:

```bash
git ls-remote origin refs/heads/main
python -B scripts/dev.py fresh-clone
python -B scripts/post_publish_check.py
python -B scripts/dev.py github-readiness
```

Account-level setup:

```bash
python -B scripts/dev.py github-maintenance
python -B scripts/maintain_github_state.py --apply
python -B scripts/dev.py github-readiness
```

A public update should name which evidence exists now and which evidence is still pending.

## Local-Only Progress

Use this when a change is committed locally but not yet pushed:

```text
Local update: the repository source has a new maintainer-facing doc and the local gates pass.

Current proof:

- local branch is ahead of origin
- `python -B scripts/dev.py quality` passed locally
- `python -B scripts/dev.py fresh-clone-local` passed locally

This is not remote publication evidence yet. I will treat public GitHub state as pending until the branch is pushed and post-publish checks pass.
```

Avoid:

- saying the public repository already has the change
- claiming the release page, README badge, profile pin, or branch protection reflects the local commit
- describing local quality as production support

## Pushed-But-Pending Checks

Use this after push while GitHub Actions, raw files, or readiness checks are still catching up:

```text
Pushed update: the change is on the public branch, but remote verification is still pending.

Pending evidence:

- GitHub Actions result for the pushed commit
- raw README and required published-file reachability
- `python -B scripts/dev.py github-readiness`

Until those checks finish, I will describe the change as pushed, not fully verified on GitHub.
```

Avoid:

- treating pending Actions as green
- hiding `[WARN]` rows
- using local `quality` output as a substitute for remote GitHub evidence

## Remote Warning Or Manual Items

Use this when local and remote checks pass but account-level setup remains manual:

```text
Remote checks are healthy for source-visible files. Remaining items are account-level follow-up:

- repository metadata, topics, or branch protection
- social preview or profile pin setup
- release page, latest-release state, or attachment freshness
- optional Discussions setup

These are manual or authenticated-maintenance items, not local code failures.
```

Avoid:

- marking manual rows complete before GitHub UI or authenticated maintenance evidence confirms them
- committing account screenshots, private UI, token values, or profile details
- implying account-level setup is complete from a dry-run plan

## Accepted Roadmap Items Without Dates

Use this when acknowledging scoped work without promising delivery:

```text
Accepted as scoped roadmap work.

Current scope:

- one concrete repository improvement
- one affected file group or route
- one local verification command

This acceptance does not promise a delivery date, production support, private access, or broader roadmap commitment.
```

Avoid:

- promising timelines
- turning a useful idea into a broad support commitment
- implying a private implementation path or external account access

## Blocked Optional Environments

Use this when Docker runtime, OpenAI live mode, GitHub account settings, or another optional environment cannot be verified in the current environment:

```text
Optional-environment update: the default local path remains verified, but this optional check is not complete in the current environment.

Verified now:

- source-visible docs and local gates
- deterministic local demo path

Still pending:

- the optional environment command on a machine/account that can run it
- follow-up readiness evidence after that command passes
```

Avoid:

- making optional Docker, OpenAI, or authenticated GitHub paths required for the default demo
- claiming optional verification from static config alone
- asking contributors for credentials, tokens, private files, or paid-service access

## Review Checklist

- The update names whether evidence is local-only, pushed, remote-verified, account-level/manual, or roadmap scope.
- The update references `docs/published_repository_status.md` only for current, reviewable repository facts.
- The update uses `docs/post_publish_warning_examples.md` before explaining `[WARN]` or `[MANUAL]` rows.
- The update uses `docs/issue_template_stale_evidence_examples.md` before treating issue-template evidence requests, stale command output, screenshots, generated artifacts, or account-level material as public proof.
- The update uses `docs/github_authenticated_maintenance_troubleshooting_examples.md` before claiming account-level setup or maintenance has been applied.
- The update uses `docs/launch_feedback_collection_examples.md` before treating feedback, stars, forks, comments, or analytics as public evidence.
- The update does not imply delivery dates, production support, private access, or completed setup before evidence exists.
- The update does not expose secrets, token values, private screenshots, private account details, real customer data, or local machine details.
- `python -B scripts/dev.py launch-assets`, `python -B scripts/dev.py safety`, and `python -B scripts/dev.py quality` pass after changing status-update wording.
