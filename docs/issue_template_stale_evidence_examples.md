# Issue Template Stale Evidence Examples

Use this page before editing `.github/ISSUE_TEMPLATE/*`, `docs/github_initial_issues.md`, or public issue bodies that ask contributors for evidence. Read it with `docs/github_initial_issues.md`, `docs/community_backlog.md`, `docs/post_publish_warning_examples.md`, and `docs/public_maintainer_status_update_examples.md`.

The core rule: current reproducible evidence, stale evidence, generated artifacts, private/account-level material, and roadmap scope are separate. Do not ask contributors for secrets, private screenshots, local machine details, or real customer data.

## Evidence Principles

- Ask for the smallest current public repro: command, route, file path, trace ID, or fictional seed-data reference.
- Treat old command output, old screenshots, old generated artifacts, and old GitHub UI state as stale until rerun or rechecked.
- Keep generated local artifacts such as `out/`, `otel_traces.json`, and `eval_summaries.csv` out of source unless a release process explicitly asks for them.
- Keep account-level GitHub settings, private screenshots, analytics, DMs, tokens, and local usernames out of issue templates.
- Keep issue evidence separate from roadmap acceptance. A report can be useful without becoming accepted scope.

## Stale Command Output

Use this when a template or seeded issue asks for command output.

Good:

```text
Paste the smallest current command output that reproduces the issue.

Preferred:

- command: `python -B scripts/dev.py <gate>`
- current commit or branch state if relevant
- short failure excerpt

Do not paste secrets, local usernames, private paths, or full logs with unrelated environment details.
```

Avoid:

- asking for any old output without a rerun date or current command
- requiring full terminal history
- treating a stale local failure as current repository evidence

## Stale Screenshots

Use this when a template asks for screenshots.

Good:

```text
Attach a screenshot only when it shows current public UI behavior and does not include private account data.

Safer alternatives:

- affected route or URL path
- current command output
- trace ID from a local demo run
- expected versus actual behavior in text
```

Avoid:

- asking for private GitHub settings screenshots
- asking for account analytics, DMs, profile pages, or local file browsers
- treating old screenshots as proof that the current branch still behaves that way

## Stale Labels Or Template Links

Use this when issue labels, template links, or seeded issue bodies drift.

Good:

```text
Report the current stale label or template link with:

- affected file: `.github/ISSUE_TEMPLATE/<file>` or `docs/github_initial_issues.md`
- expected label or link
- current stale label or link
- verification command: `python -B scripts/dev.py community-issues`
```

Avoid:

- asking contributors to edit labels directly on GitHub without matching source updates
- treating a label warning as proof of account-level setup
- hiding template drift by deleting a useful public issue

## Stale Generated Artifacts

Use this when a template asks for generated reports, replay artifacts, traces, or CSV outputs.

Good:

```text
Generated artifacts can be used as local evidence, but they should stay uncommitted unless a release process explicitly asks for them.

Useful report fields:

- command that generated the artifact
- relevant case ID, trace ID, or failure summary
- whether `python -B scripts/dev.py safety` still passes
```

Avoid:

- asking contributors to commit `out/`, `otel_traces.json`, or `eval_summaries.csv`
- treating generated artifacts as uploaded release assets
- copying local machine paths from generated files into public issues

## Private Or Account-Level Evidence Requests

Use this when a template asks for account settings, private files, credentials, screenshots, or paid-service access.

Good:

```text
Please do not share secrets, tokens, credentials, private screenshots, private files, local machine details, account analytics, DMs, or real customer data.

If the issue depends on account-level state, summarize the public symptom and link the relevant repository doc or command instead.
```

Avoid:

- asking for GitHub tokens, API keys, account screenshots, or private profile details
- requiring paid-service access for the default local demo path
- asking for real customer, employee, support, or production incident data

## Review Checklist

Before changing issue templates or seeded issue bodies:

```bash
python -B scripts/dev.py community-issues
python -B scripts/dev.py launch-assets
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

- The request asks for current reproducible evidence, not stale output.
- The request does not require private/account-level material.
- Generated artifacts are described as local evidence and stay ignored unless a release process explicitly asks for them.
- Roadmap acceptance stays separate from evidence collection.
- `docs/post_publish_warning_examples.md` is used before treating remote warning rows or manual account settings as current evidence.
- `docs/public_maintainer_status_update_examples.md` is used before turning issue-template evidence into public maintainer status wording.
- The template or seeded issue does not ask contributors for secrets, private screenshots, local machine details, real customer data, credentials, tokens, private files, account analytics, DMs, or paid-service access.
