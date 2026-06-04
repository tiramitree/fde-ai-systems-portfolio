# Issue Triage SLA Wording Examples

Use this page when setting public response expectations for GitHub issues. Read it with `docs/maintainer_review_policy.md`, `docs/public_roadmap_issue_comment_examples.md`, `docs/github_discussions_launch_checklist.md`, `docs/discussion_to_issue_conversion_examples.md`, and `docs/launch_feedback_collection_examples.md`.

The core rule: issue triage expectations, support SLAs, delivery dates, private-account access, roadmap acceptance, and production support are different things. Keep issue replies factual, best-effort, and reversible.

## Wording Principles

- Say what will be reviewed next, not when it will be delivered.
- Tie follow-up to issue scope, repository guardrails, and local verification commands.
- Keep support questions, broad ideas, and private feedback out of issue promises.
- Avoid words that imply guaranteed response time, guaranteed fix time, private help, production support, or roadmap acceptance.
- Close or redirect unsafe requests without asking for secrets, credentials, private files, private account screenshots, or real customer data.

## First-Response Wording

Use this when a new issue is concrete enough to triage, but not yet accepted as work.

```text
Thanks for opening this. I will triage it against the current repository scope and safety guardrails.

For this to stay reviewable, please keep the issue focused on:

- the affected file, command, route, or workflow
- the smallest expected change
- the local verification command that should prove it

This is best-effort open-source triage, not a support SLA or delivery commitment.
```

Good fit:

- bug reports with a command or file path
- docs confusion tied to current repository text
- feature ideas that can be narrowed before acceptance

Avoid:

- promising a response window
- saying the issue will be fixed
- asking for private account access, credentials, screenshots, or customer data

## Accepted Follow-Up Wording

Use this when the issue is accepted as scoped repository work.

```text
Accepted as scoped follow-up.

The expected change is:

- <one concrete docs/frontend/backend/eval/release outcome>
- <the safety or evidence boundary it must preserve>
- <the command that should pass before this is treated as complete>

This acceptance does not promise a delivery date or broader roadmap commitment. A PR should stay within this scope and follow docs/issue_to_pr_handoff_flow.md.
```

Good fit:

- narrow docs fixes
- small UI or API changes
- eval additions with clear pass/fail expectations
- release or GitHub-maintenance checklist updates

Avoid:

- accepting a broad roadmap area as one issue
- treating issue acceptance as public support coverage
- marking work complete before the PR and gates pass

## Delayed-Response Wording

Use this when the issue is plausible but cannot be reviewed immediately.

```text
This is still visible, but it has not been reviewed deeply yet.

To keep expectations clear: the repository does not provide response-time guarantees. I will leave this open while it remains specific and safe. A useful next comment would narrow the issue to one affected file, one expected behavior, and one verification command.
```

Good fit:

- issue backlog is real but not urgent
- the request needs a smaller scope
- the maintainer wants to acknowledge the issue without promising time

Avoid:

- apologizing in a way that implies contractual support
- promising a date
- leaving vague issues open forever without narrowing or closure

## No-Guarantee Closure Wording

Use this when the issue is too vague, too broad, unsafe, private-account-dependent, or outside the repository scope.

```text
Closing this because it is not reviewable as a repository issue.

Public issues need a concrete repository problem, a narrow expected change, and a local verification path. This issue currently asks for broad support, private access, delivery guarantees, or work outside the project scope.

If there is a smaller technical problem, please open a new issue that uses fictional/public data, avoids secrets and private account details, and names the file or command that should change.
```

Good fit:

- broad support requests
- private-account debugging
- vague "please build this" requests
- requests that need secrets, private files, account screenshots, or production support

Avoid:

- asking for more private data in public
- turning unsafe requests into accepted roadmap work
- adding labels or comments that imply the project owes delivery

## Channel Routing

Use this quick routing table before replying:

| Incoming Content | Best Channel | Wording Boundary |
| --- | --- | --- |
| Reproducible bug with public details | Issue | Ask for smallest repro and local verification command. |
| Broad idea before scope is clear | Discussion or backlog note | Do not call it accepted roadmap work. |
| Narrow implementation tied to accepted issue | PR | Review with the PR gate before completion. |
| Setup question without a bug | Discussion Q&A | Answers are best-effort and not an SLA. |
| Private feedback or analytics | Outside git or neutral public summary | Do not quote private content or account details. |
| Security concern | SECURITY.md path | Do not ask for exploit details in public. |

## Review Checklist

Before posting issue triage wording:

```bash
python -B scripts/dev.py community-issues
python -B scripts/dev.py pr-policy
python -B scripts/dev.py launch-assets
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

- The reply separates issue triage expectations from support SLAs, delivery dates, private-account access, roadmap acceptance, and production support.
- The reply points to public files, local commands, or fictional/public data only.
- Unsafe requests are closed or redirected through `docs/maintainer_review_policy.md`.
- Accepted-scope comments stay aligned with `docs/public_roadmap_issue_comment_examples.md`.
- Discussion-style questions are routed with `docs/github_discussions_launch_checklist.md`.
- Discussion-to-issue conversions are reviewed with `docs/discussion_to_issue_conversion_examples.md` before they become public issue expectations.
- Private feedback and launch-channel feedback are summarized through `docs/launch_feedback_collection_examples.md` before they become source-visible issue content.
