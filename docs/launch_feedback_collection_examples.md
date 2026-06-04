# Launch Feedback Collection Examples

Use this page after sharing the public repository or launch copy. Read it with `docs/launch_copy_pack.md`, `docs/star_growth_plan.md`, `docs/published_repository_status.md`, `docs/post_publish_checklist.md`, `docs/post_publish_warning_examples.md`, and `docs/command_output_troubleshooting_map.md`.

The core rule: public feedback, private messages, analytics screenshots, and source evidence prove different things. Do not commit private DMs, account analytics, personal account details, or launch-feedback claims without matching evidence.

## Expected Evidence Split

Local release-facing evidence:

```bash
python -B scripts/dev.py launch-assets
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Public repository evidence:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/post_publish_check.py
```

Feedback evidence can inform backlog priorities, docs improvements, and launch copy. It does not prove production readiness, runtime verification, account-level setup, or star-growth success by itself.

## GitHub Stars And Forks

Use this when recording visible repository traction.

Useful evidence:

- `github-readiness` output showing current stars and forks
- public repository page showing star and fork counts
- dated release notes or maintainer notes that clearly say the counts were observed at that time

Wrong use:

- claiming star-growth success from one observed count
- treating stars or forks as deployment-quality proof
- editing source docs to inflate, imply, or guarantee future growth

Review with:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/dev.py launch-assets
```

Keep count-based wording dated and conservative. Prefer "observed" over "achieved" unless a documented launch goal explicitly defines the threshold and the evidence is fresh.

## Issue Feedback

Use this when public users open issues, suggest improvements, or report confusion.

Useful evidence:

- public issue URL
- issue title and labels
- affected docs, command, or project path
- maintainer triage note linking the feedback to a real improvement

Wrong use:

- creating low-signal issues for activity metrics
- copying private user details from an issue into docs
- treating vague feedback as an accepted roadmap without triage

Review with:

```bash
python -B scripts/dev.py community-issues
python -B scripts/dev.py safety
```

Convert useful public feedback into issues only when the work improves the repository. Keep issue bodies free of secrets, account access requests, private local paths, or real customer data.

## Launch-Post Comments

Use this when feedback arrives on LinkedIn, X / Twitter, Hacker News, Reddit, or another launch channel.

Useful evidence:

- public comment URL or public thread URL
- short maintainer summary of the technical point
- linked follow-up issue or doc change when the comment exposes a real gap
- source channel named without copying private profile details

Wrong use:

- committing screenshots of social accounts, notifications, or private profile sidebars
- presenting comments as endorsements without permission
- treating a high-comment thread as proof that the repo is complete

Review with:

```bash
python -B scripts/dev.py launch-assets
python -B scripts/dev.py safety
```

If a public comment identifies a bug, missing setup step, or unclear claim, fix the repository artifact first. A launch thread is feedback, not a source file.

## Private-Message Feedback

Use this only for internal triage. Private feedback can guide fixes, but the private message itself should not become repository content.

Useful evidence:

- a redacted maintainer note summarizing the technical issue
- a new public issue that removes names, accounts, emails, screenshots, and message text
- a local task note outside the repository when the feedback is not yet public

Wrong use:

- committing private DMs, emails, handles, avatars, company names, or screenshots
- asking contributors to share private account conversations
- using private praise as public proof of adoption

Review with:

```bash
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

When private feedback leads to a fix, describe the technical problem in neutral terms. Do not quote private messages unless the sender explicitly asks for public attribution and the attribution is reviewed.

## Analytics Screenshots

Use this only when reviewing launch reach or traffic privately. Analytics screenshots are account-level artifacts, not source content.

Useful evidence:

- redacted aggregate metric notes kept outside git
- a dated summary that avoids account IDs, IP data, referrers that identify private people, and paid-platform account details
- public GitHub metrics only when they are visible on the repository page or returned by the readiness command

Wrong use:

- committing account analytics screenshots
- claiming adoption, conversion, or star-growth success from private dashboards alone
- mixing analytics screenshots with release evidence such as evals, smoke tests, or GitHub Actions

Review with:

```bash
python -B scripts/dev.py launch-assets
python -B scripts/dev.py safety
```

Analytics can shape future launch posts and docs, but they do not replace public repository evidence or local quality gates.

## Review Checklist

- `docs/launch_copy_pack.md` remains the source for public launch copy.
- `docs/star_growth_plan.md` keeps stars as a byproduct of usefulness, not the product goal.
- `docs/published_repository_status.md` records only evidence that is current and reviewable.
- `docs/post_publish_checklist.md` keeps launch feedback separate from source verification.
- `docs/post_publish_warning_examples.md` is used before claiming launch feedback or star-growth evidence.
- Public feedback links are used only when the source is actually public.
- Private messages, account analytics, personal account details, and screenshots with private UI are not committed.
- `python -B scripts/dev.py launch-assets`, `python -B scripts/dev.py safety`, and `python -B scripts/dev.py quality` pass after changing launch-feedback wording.
