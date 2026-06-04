# Discussion To Issue Conversion Examples

Use this page when deciding whether a GitHub Discussion should become a scoped issue. Read it with `docs/github_discussions_launch_checklist.md`, `docs/public_roadmap_issue_comment_examples.md`, `docs/issue_triage_sla_wording_examples.md`, `docs/roadmap_duplicate_issue_handling_examples.md`, and `docs/launch_feedback_collection_examples.md`.

The core rule: discussion volume, untriaged ideas, private feedback, and accepted issue scope are different things. Do not create issues just to make activity visible.

## Conversion Principles

- Convert a discussion only when there is concrete repository work, a small expected change, and a local verification command.
- Keep setup questions in Q&A unless they expose a docs bug, command mismatch, or reproducible failure.
- Keep broad ideas in Discussions until scope, risk, and review path are narrow enough for `docs/public_roadmap_issue_comment_examples.md`.
- Keep private feedback outside git unless the technical issue can be summarized without names, accounts, screenshots, private files, or customer data.
- Close or leave low-signal discussions without converting them into issues for activity metrics.

## Setup Questions

Keep as Discussion:

```text
Answered in Q&A. The current quickstart and command output expectations cover this setup path, so there is no scoped repository change yet.
```

Convert to issue only when the question exposes a concrete docs or command gap:

```text
Converting this to a scoped docs issue because the setup question points to a missing command expectation.

Accepted issue scope:

- update the affected setup or troubleshooting section
- keep local-first behavior unchanged
- verify with `python -B scripts/dev.py assets` and `python -B scripts/dev.py safety`
```

Avoid converting every setup question. A factual answer is not automatically a roadmap item or a support SLA.

## Broad Ideas

Keep as Discussion:

```text
This is useful future direction, but it is still too broad for an issue. Please keep the idea here until it names one affected route, one expected behavior, and one verification command.
```

Convert to issue only after the idea becomes a narrow repository improvement:

```text
Converting this to an issue because the proposal has one reviewable scope: add a docs-only connector boundary note without changing runtime behavior.

The issue should stay separate from broader connector roadmap work and must not promise external account access, paid-service setup, or delivery dates.
```

Use `docs/public_roadmap_issue_comment_examples.md` before accepting the converted issue as roadmap scope.

Use `docs/roadmap_duplicate_issue_handling_examples.md` before opening a new issue that may duplicate or overlap existing roadmap scope.

## Reproducible Bugs

Convert to issue when the discussion includes public, reproducible details:

```text
Converting this to a bug issue because the discussion now includes:

- affected command or file
- expected behavior
- actual behavior
- minimal public repro using fictional or repository data
- local verification command
```

Keep as Discussion or ask for narrowing when the report is missing a public repro:

```text
This may be a bug, but it is not ready for an issue yet. Please remove private paths, account details, screenshots, and customer data, then share the smallest public command or file path that reproduces the behavior.
```

Do not ask for secrets, local usernames, private files, private screenshots, production logs, or real customer data.

## Private Feedback

Keep private:

```text
Thanks for the private note. I will not copy the message, account details, screenshots, or identity into the repository.
```

Create a public issue only when the technical problem can be fully neutralized:

```text
Opening a neutral public issue based on a private report. The issue describes only the repository behavior, uses fictional/public data, and removes names, accounts, screenshots, private paths, and message text.
```

Use `docs/launch_feedback_collection_examples.md` and `docs/contributor_attribution_examples.md` before turning any private feedback into public evidence or credit.

## Low-Signal Discussions

Keep as Discussion, close, lock, hide, or redirect:

```text
Closing this discussion because it is not specific enough to become a repository issue. A useful follow-up should name the affected file, command, route, or workflow, the smallest expected change, and the local command that would prove it.
```

Do not convert low-signal discussions into issues for visibility, momentum, or launch optics. Empty activity makes the project harder to trust and harder to maintain.

## Review Checklist

Before converting a discussion into an issue:

```bash
python -B scripts/dev.py community-issues
python -B scripts/dev.py pr-policy
python -B scripts/dev.py launch-assets
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

- The discussion has a concrete repository problem or narrow improvement.
- The issue can name one affected file, command, route, or workflow.
- The issue body avoids secrets, tokens, private account data, private screenshots, private paths, and real customer data.
- The issue acceptance criteria include a local verification command.
- The conversion does not imply support SLAs, production support, delivery dates, private-account access, or guaranteed roadmap acceptance.
- Discussion feedback, issue scope, PR review, launch evidence, and private feedback stay separate.
- Duplicate or overlapping discussion-to-issue paths are reviewed with `docs/roadmap_duplicate_issue_handling_examples.md`.
