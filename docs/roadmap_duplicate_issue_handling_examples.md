# Roadmap Duplicate Issue Handling Examples

Use this page when a public roadmap issue duplicates, overlaps, or reopens existing public scope. Read it with `docs/public_roadmap_issue_comment_examples.md`, `docs/discussion_to_issue_conversion_examples.md`, `docs/issue_triage_sla_wording_examples.md`, and `docs/community_backlog.md`.

The core rule: duplicate reports, overlapping ideas, new evidence, accepted scope, and low-signal activity are separate. Do not close, merge, or relabel issues just to hide activity or inflate public momentum.

## Handling Principles

- Keep the oldest scoped issue as the canonical issue when the scope and evidence are the same.
- Preserve useful new evidence by linking or copying only the neutral technical summary, not private details.
- Split overlapping ideas when they require different files, routes, commands, or safety boundaries.
- Route discussion-style duplicates through `docs/discussion_to_issue_conversion_examples.md`.
- Use `docs/issue_triage_sla_wording_examples.md` so closure or merge wording does not imply delivery dates, support SLAs, private-account access, or production support.

## Exact Duplicates

Use this when two issues ask for the same repository change with no new evidence.

```text
Thanks, this duplicates the existing scoped issue: #<canonical-issue>.

I am closing this one so the work stays reviewable in a single place. The canonical issue already covers:

- <same expected change>
- <same affected file group or route>
- <same local verification command>

This closure is only duplicate cleanup. It is not a rejection of the idea and it does not change the accepted scope.
```

Avoid:

- closing without linking the canonical issue
- implying the duplicate was low quality when it was simply repeated
- using duplicate closure to make the issue list look cleaner

## Overlapping Roadmap Ideas

Use this when a new issue partly overlaps existing roadmap scope but includes a different useful idea.

```text
This overlaps #<canonical-issue>, but it also includes a separable follow-up.

I will keep #<canonical-issue> focused on:

- <current accepted scope>
- <current verification command>

The separable follow-up should become a new narrow issue only if it names one affected file group, one expected behavior, and one local verification command. Until then, it belongs in `docs/community_backlog.md` or a GitHub Discussion rather than this issue.
```

Avoid:

- expanding the canonical issue into a broad roadmap bucket
- promising the follow-up will ship
- treating an interesting overlap as accepted scope before it has a narrow verification path

## Duplicate Bugs With New Evidence

Use this when a duplicate bug report includes a new public repro, command output, or affected route.

```text
Thanks, this is a duplicate of #<canonical-issue>, but it includes useful new evidence.

I am closing this duplicate and linking the new evidence back to the canonical issue:

- affected command or route: `<command-or-route>`
- observed behavior: <short neutral summary>
- expected behavior: <short neutral summary>
- verification command: `python -B scripts/dev.py <gate>`

Please keep any follow-up evidence public, minimal, and free of secrets, private paths, account screenshots, or real customer data.
```

Avoid:

- copying private screenshots, account names, logs, tokens, local usernames, or customer data
- losing the new evidence just because the issue is a duplicate
- treating new evidence as proof that the bug is fixed

## Issue-Versus-Discussion Duplicates

Use this when an issue duplicates a GitHub Discussion, setup question, or broad idea.

```text
This duplicates an existing Discussion rather than a scoped issue.

I am closing the issue path for now because it does not yet name a concrete repository change. Please keep the conversation in the Discussion until it has:

- one affected file, command, route, or workflow
- one expected change
- one local verification command

When that exists, use `docs/discussion_to_issue_conversion_examples.md` before converting it into issue scope.
```

Avoid:

- converting discussion volume into issue activity
- calling a setup answer accepted roadmap work
- asking contributors for private account access, screenshots, credentials, or paid-service access

## Stale Duplicate References

Use this when an issue points to an old duplicate, a merged PR, or a stale checklist item.

```text
This duplicate reference is stale.

Current state:

- canonical issue or PR: #<current-reference>
- old duplicate reference: #<stale-reference>
- current verification command: `python -B scripts/dev.py <gate>`

I will update the reference and keep the issue open only if there is current, reviewable work left. If no scoped work remains, I will close it as stale duplicate cleanup without implying new roadmap commitment.
```

Avoid:

- reopening old duplicates only for visibility
- using stale references as launch or roadmap evidence
- marking stale duplicate cleanup as a new feature

## Review Checklist

Before closing, merging, splitting, or redirecting duplicate roadmap issues:

```bash
python -B scripts/dev.py community-issues
python -B scripts/dev.py pr-policy
python -B scripts/dev.py launch-assets
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

- The response keeps duplicate reports, overlapping ideas, new evidence, accepted scope, and low-signal activity separate.
- The canonical issue is linked before any duplicate is closed.
- Useful new public evidence is preserved without copying secrets, private paths, account screenshots, private messages, local machine details, or real customer data.
- Discussion-style duplicates are reviewed with `docs/discussion_to_issue_conversion_examples.md`.
- Public replies use `docs/issue_triage_sla_wording_examples.md` before implying response expectations.
- Backlog-only ideas stay in `docs/community_backlog.md` until they have one affected file group and one verification command.
- Duplicate cleanup is not used to hide activity, inflate activity, promise delivery dates, claim production support, or imply private-account access.
