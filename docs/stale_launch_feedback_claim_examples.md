# Stale Launch Feedback Claim Examples

Use this page before reusing old launch-feedback notes in public copy, maintainer updates, issue replies, release notes, or growth summaries. Read it with `docs/launch_feedback_collection_examples.md`, `docs/public_maintainer_status_update_examples.md`, `docs/post_publish_warning_examples.md`, and `docs/star_growth_plan.md`.

The core rule: current public feedback, stale feedback, private feedback, analytics, launch copy, and roadmap scope prove different things. Do not claim star growth, user adoption, production readiness, or private support from stale or private feedback.

## Expected Evidence Split

Local launch-facing proof:

```bash
python -B scripts/dev.py launch-assets
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Public repository proof:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/post_publish_check.py
```

Feedback can suggest where the repository is confusing, useful, or worth improving. Feedback does not replace current repository checks, current public URLs, issue triage, or release evidence.

## Stale Stars Or Forks

Use this when an old screenshot, old readiness output, or old maintainer note lists star and fork counts that may have changed.

Safe wording:

```text
At the time of the prior launch note, the repository had visible public traction. Current star and fork counts should be read from GitHub or `python -B scripts/dev.py github-readiness`.
```

Avoid:

- claiming the old count as current
- describing one old count as star-growth success
- using stars or forks as proof of deployment quality

Review with:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/dev.py launch-assets
```

Keep dated count notes separate from current public metrics. If the count matters, rerun the readiness check and name the observation date.

## Stale Public Comments

Use this when a launch thread, GitHub issue, discussion, or community comment was useful but no longer reflects the current repository.

Safe wording:

```text
Earlier launch feedback pointed out setup confusion. The repository has since added a clearer run path and the current docs should be checked directly.
```

Avoid:

- quoting old comments as current endorsements
- treating an old bug report as proof the bug still exists
- using comments from one channel as accepted roadmap scope

Review with:

```bash
python -B scripts/dev.py community-issues
python -B scripts/dev.py launch-assets
python -B scripts/dev.py safety
```

If the comment led to a fix, link the current issue, PR, or doc. Do not preserve stale comment screenshots as source evidence.

## Private Feedback Summaries

Use this when private feedback helped identify a technical gap, but the original message is not public.

Safe wording:

```text
Private feedback surfaced a setup edge case. The public follow-up is tracked as a neutral repository issue without names, handles, screenshots, account details, or message text.
```

Avoid:

- turning private praise into public proof of adoption
- committing private DMs, emails, handles, avatars, company names, or screenshots
- implying private support or private access is available

Review with:

```bash
python -B scripts/dev.py safety
python -B scripts/dev.py community-issues
python -B scripts/dev.py quality
```

Private feedback can guide backlog triage. It should not become source-visible evidence unless it is rewritten as a neutral, public, non-identifying technical issue.

## Analytics Screenshots

Use this when launch analytics, traffic dashboards, social impressions, or referrer screenshots are older than the current launch note.

Safe wording:

```text
Private analytics informed the next launch channel to try. Current public repository evidence remains the GitHub page, published docs, issues, and readiness output.
```

Avoid:

- committing analytics screenshots
- claiming adoption, conversion, or current reach from old dashboards
- mixing private analytics with release, eval, or runtime evidence

Review with:

```bash
python -B scripts/dev.py launch-assets
python -B scripts/dev.py safety
```

Analytics are account-level planning notes. Keep them outside git unless they are replaced with a public, redacted, technical summary that does not identify private people or accounts.

## Launch-Post Reposts

Use this when a launch post was reposted, linked, bookmarked, or quoted by another channel.

Safe wording:

```text
The launch post was reshared publicly. Treat that as distribution context only; repository usefulness still comes from runnable demos, docs, evals, traces, and current public checks.
```

Avoid:

- presenting reposts as validation that the systems are complete
- treating repost volume as accepted roadmap scope
- copying account sidebars, notification panels, private analytics, or private profile details

Review with:

```bash
python -B scripts/dev.py launch-assets
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Reposts can help decide what to explain next. They do not prove runtime correctness, GitHub setup, release freshness, or production readiness.

## Review Checklist

- Current public feedback is checked through `docs/launch_feedback_collection_examples.md`.
- Public maintainer updates are checked through `docs/public_maintainer_status_update_examples.md`.
- Post-publish warning rows are checked through `docs/post_publish_warning_examples.md`.
- Star-growth wording stays aligned with `docs/star_growth_plan.md`.
- Current public feedback, stale feedback, private feedback, analytics, launch copy, and roadmap scope stay separate.
- Old stars, forks, comments, reposts, and screenshots are not described as current unless they are rechecked.
- Private messages and analytics are not committed as source evidence.
- Stale feedback is not used to claim star growth, user adoption, production readiness, or private support.
- `python -B scripts/dev.py launch-assets`, `python -B scripts/dev.py safety`, and `python -B scripts/dev.py quality` pass after changing launch-feedback wording.
