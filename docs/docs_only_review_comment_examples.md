# Docs-Only Review Comment Examples

Use this page when a documentation-only pull request needs a clear maintainer reply. Read it with `docs/docs_only_pr_review_examples.md`, `docs/pr_review_security.md`, `docs/first_pull_request_checklist.md`, and `docs/public_roadmap_issue_comment_examples.md`.

These examples are templates, not automatic decisions. Read the diff before posting a review, keep the response tied to the current repository state, and do not run contributor commands until the changed files are understood.

## Review Principles

- Keep comments specific to the changed files and evidence commands.
- Do not approve broader public claims unless a local doc, test, or gate proves them.
- Do not ask for secrets, private paths, external accounts, paid-service requirements, generated runtime files, or real customer data.
- Prefer narrow follow-up requests over broad rewrites when the contribution is useful.
- Close or ignore unsafe or low-signal changes that would weaken the repository.

## Approve

Use this when a docs-only PR is narrow, linked, and verified.

```text
Thanks for the focused docs update. I checked the changed docs against the current repository state, and the claim stays grounded in the existing local workflow.

Verified:

- README.md / PROJECT_CONTENT_INDEX.md links point to real files.
- No generated runtime files, private paths, external accounts, paid-service requirements, or real customer data were added.
- `python -B scripts/dev.py community-issues`, `python -B scripts/dev.py assets`, and `python -B scripts/dev.py safety` pass for the docs route.

Approved.
```

Use this decision only after the commands in `docs/docs_only_pr_review_examples.md` match the changed route. If the PR changes launch copy, issue labels, or evidence claims, include the matching launch, claims, or quality gate in the review note.

## Request Changes: Missing Link Or Evidence

Use this when the contribution is useful but not yet connected to the public navigation or evidence path.

```text
This looks useful, but it needs one small follow-up before merge.

Please connect the new wording to the public evidence path:

- link the new doc from README.md or PROJECT_CONTENT_INDEX.md, or explain why it should remain internal to the docs folder
- point the claim to the existing local evidence command or source doc
- keep the wording narrow enough that `python -B scripts/dev.py community-issues`, `python -B scripts/dev.py assets`, and `python -B scripts/dev.py safety` can prove it

Once that is updated, I can re-run the docs route and review again.
```

Do not request a large rewrite if a link, command reference, or claim adjustment is enough.

## Request Changes: Claim Is Too Broad

Use this when the PR turns a local reference workflow into an unsupported production or launch claim.

```text
I cannot approve this wording yet because it broadens the public claim beyond the evidence in this repository.

Please revise the claim so it is backed by a local source such as:

- docs/portfolio_evidence_matrix.md
- docs/demo_report.md
- docs/api_contracts.md
- docs/pr_review_security.md
- a passing `python -B scripts/dev.py claims`, `python -B scripts/dev.py pr-policy`, or `python -B scripts/dev.py quality` run

The docs should describe what the current local system proves, not imply runtime evidence, account-level setup, or production readiness that has not been verified.
```

Use `docs/pr_review_security.md` when the broad claim also touches workflow permissions, model behavior, dependency posture, or contributor safety.

## Close As Unsafe

Use this when a docs-only PR asks maintainers or users to expose sensitive information, run unknown commands, or weaken safety gates.

```text
Closing this because the change is unsafe for a public repository.

The docs must not ask maintainers or contributors to provide secrets, private paths, account credentials, external accounts, paid-service requirements, generated runtime files, or real customer data. They also must not weaken local safety, permission, eval, workflow, or PR-review gates.

Do not run contributor commands from this PR. If the idea is still useful, open a new narrow PR that keeps all verification local, documented, and safe.
```

Close-as-unsafe is appropriate even if the file extension is only `.md`. Documentation can still create credential pressure, phishing pressure, unsafe shell execution, or misleading release evidence.

## Close As Low Signal

Use this when a docs-only PR is broad activity noise, unrelated rewriting, or unsupported promotional copy.

```text
Closing this because it does not create a reviewable improvement for the repository.

Useful docs changes should be tied to a concrete issue, source file, local workflow, or evidence command. This PR mostly rewrites existing material or adds unsupported claims without improving setup, review, safety, troubleshooting, or contributor flow.

A better follow-up would be a small docs change that names the specific problem, updates the smallest relevant file, and includes the targeted `python -B scripts/dev.py ...` command used to verify it.
```

Use request-changes instead of close-as-low-signal when the contributor has a specific useful idea but missed the repo's link or evidence pattern.

Use `docs/public_roadmap_issue_comment_examples.md` when the same contribution also needs an issue-level reply about accepted scope, backlog ideas, implementation promises, or low-signal activity.

## Reviewer Checklist Before Posting

Before posting one of these comments:

```bash
git diff --stat
git diff -- README.md PROJECT_CONTENT_INDEX.md docs/ .github/
git diff --check
python -B scripts/dev.py community-issues
python -B scripts/dev.py assets
python -B scripts/dev.py pr-policy
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Use the narrowest useful set for small PRs, then run `python -B scripts/dev.py quality` before merge-facing approval. If a command fails, use `docs/command_output_troubleshooting_map.md` to find the first local fix instead of weakening the gate.

## Comment Selection Map

| Outcome | Use When | Do Not Use When |
| --- | --- | --- |
| approve | The diff is narrow, linked, and locally verified. | Claims are broader than evidence or safety checks were skipped. |
| request-changes | The idea is useful but needs links, commands, or narrower claims. | The PR asks for secrets, private files, unsafe commands, or access. |
| close-as-unsafe | The PR introduces unsafe instructions, generated runtime files, private paths, external accounts, paid-service requirements, or real customer data. | The issue is only missing navigation or wording polish. |
| close-as-low-signal | The PR is broad rewriting, unsupported hype, or unrelated activity. | A small concrete edit would make it useful and safe. |

Record only repository-safe evidence in public review comments. Do not paste environment dumps, API keys, local usernames, machine paths, customer names, or generated runtime traces.
