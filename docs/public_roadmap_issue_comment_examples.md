# Public Roadmap Issue Comment Examples

Use this page when replying to public roadmap issues, contributor proposals, or issue-to-PR handoff questions. Read it with `docs/github_initial_issues.md`, `docs/community_backlog.md`, `docs/issue_to_pr_handoff_flow.md`, `docs/docs_only_review_comment_examples.md`, `docs/contributor_attribution_examples.md`, and `docs/maintainer_review_policy.md`.

The core rule: accepted scope, backlog ideas, implementation promises, and low-signal activity are different things. Keep public issue comments factual, narrow, and reversible; do not promise delivery dates, external-account access, private data, or guaranteed roadmap acceptance.

## Comment Principles

- Tie every reply to the current issue title, acceptance criteria, or repository guardrail.
- Keep accepted scope separate from broader backlog ideas.
- Avoid delivery dates, roadmap guarantees, private maintainer context, and external account requirements.
- Redirect unsafe requests without asking contributors to provide secrets, credentials, private files, real customer data, or local machine details.
- Link useful pull requests only after the PR is narrow enough to review through `docs/issue_to_pr_handoff_flow.md`.

## Accept Scoped Roadmap Issue

Use this when the proposal matches the current roadmap, has narrow acceptance criteria, and does not require unsafe access.

```text
Thanks, this fits the current roadmap scope.

Accepted scope for this issue:

- <one concrete outcome>
- <the smallest docs/frontend/backend/eval/release route that should change>
- <the local verification command that should prove it>

Please keep the first PR narrow and use docs/issue_to_pr_handoff_flow.md before opening it. Broader follow-up ideas can stay in docs/community_backlog.md until they are ready for a separate issue.
```

Before posting, confirm the issue still matches `docs/github_initial_issues.md` or `docs/community_backlog.md`.

## Narrow Oversized Request

Use this when the idea is useful but combines too many systems, requires a broad rewrite, or mixes current work with future backlog ideas.

```text
This is useful, but the issue needs to be smaller before it is reviewable.

Please narrow it to one route:

- docs-only wording and links
- one frontend interaction
- one backend/API boundary
- one eval or seed-data change
- one release or GitHub-maintenance checklist

The first issue should not promise the full backlog item. A good next version names the one file group to change, the safety boundary it preserves, and the `python -B scripts/dev.py ...` command that should pass.
```

Use request-changes language from `docs/docs_only_review_comment_examples.md` if the oversized request already arrived as a PR.

## Close Low-Signal Activity

Use this when the issue is not tied to a concrete repository improvement.

```text
Closing this because it is not specific enough to become a useful roadmap issue.

Public issues should name a concrete problem, a small expected change, and a local verification path. This issue does not currently improve setup, review, safety, troubleshooting, contributor flow, release evidence, or demo behavior.

A better follow-up would be a new issue that points to the relevant file, describes the current gap, and includes a focused acceptance checklist.
```

Do not turn broad activity into public roadmap work just to keep the issue list busy.

## Redirect Unsafe Requests

Use this when an issue asks for secrets, credentials, private data, unsafe commands, external account access, paid-service requirements, or weakened gates.

```text
Closing this because the requested path is unsafe for a public repository.

This project does not ask maintainers or contributors for secrets, tokens, private files, account credentials, local machine details, paid-service access, generated runtime files, or real customer data. It also does not weaken permission checks, approval gates, traces, audit logs, evals, workflow security, or PR-review gates to make an issue easier to complete.

If the underlying idea is still useful, open a new issue that keeps verification local, uses fictional seed data, and preserves the existing safety gates.
```

Follow `docs/maintainer_review_policy.md` for unsafe or phishing-like activity, even when the request is written politely.

## Link Useful PR

Use this when a contributor has opened a PR that appears to address the issue.

```text
Thanks, linking this issue to PR #<number> for review.

Before merge, the PR still needs to stay within this issue's accepted scope:

- no unrelated cleanup
- no generated runtime artifacts as source
- no private paths, secrets, account data, or real customer data
- route-specific verification plus `python -B scripts/dev.py safety`

I will review the diff against the issue acceptance criteria and the merge bar before treating the issue as complete.
```

Do not mark the issue done until the PR is reviewed, merged, and verified through the relevant local gate.

Use `docs/contributor_attribution_examples.md` before adding public credit in issue comments. Credit useful public work without copying private identity details or turning low-signal activity into a roadmap signal.

## Review Checklist

Before posting a public roadmap issue comment:

```bash
python -B scripts/dev.py community-issues
python -B scripts/dev.py pr-policy
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

- The comment separates accepted scope, backlog ideas, implementation promises, and low-signal activity.
- The comment does not promise delivery dates, external-account access, private data, or guaranteed roadmap acceptance.
- The issue can be completed through a narrow route from `docs/issue_to_pr_handoff_flow.md`.
- Unsafe requests are closed or redirected without asking for secrets, credentials, private files, or real customer data.
- Useful PR links stay conditional until the diff and checks are reviewed.
