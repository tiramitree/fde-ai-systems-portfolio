# Contributor Attribution Examples

Use this page when crediting useful public contributions, triaging attribution requests, or summarizing feedback that led to a repository change. Read it with `docs/maintainer_review_policy.md`, `docs/docs_only_pr_review_examples.md`, `docs/public_roadmap_issue_comment_examples.md`, and `docs/launch_feedback_collection_examples.md`.

The core rule: useful public contribution, private feedback, launch feedback, and low-signal activity prove different things. Keep attribution tied to public GitHub activity or explicitly permissioned public credit; do not include private messages, account details, emails, or analytics screenshots.

## Attribution Principles

- Credit concrete repository improvements, not activity volume.
- Link public GitHub issues, pull requests, commits, or discussions when they are the source of the contribution.
- Keep names and handles out of source docs unless the credit is already public or explicitly permissioned.
- Summarize private feedback as a neutral technical problem before creating public work.
- Do not add contributor credits to make the repository look busier.
- Do not accept attribution requests that ask for collaborator access, external-account access, private identity details, or unverifiable claims.

## Useful Docs PR Credit

Scenario:

```text
A contributor opens a docs-only PR that fixes a confusing setup step and links the change to a public issue.
```

Good attribution:

```text
Thanks for the docs fix in PR #<number>. It clarifies the setup path and keeps the verification command tied to the current docs.
```

Use when:

- the PR is public
- the diff is narrow
- the changed claim is backed by a local command or repository file
- `docs/docs_only_pr_review_examples.md` still approves the docs-only route

Avoid:

- copying the contributor's email, profile bio, private message, employer, or account screenshot
- adding a permanent README credit for a tiny wording fix
- crediting the PR before it passes review and gates

## Useful Bug Report Credit

Scenario:

```text
A public issue reports that a command in README.md is stale or confusing.
```

Good attribution:

```text
Thanks for the report in issue #<number>. The fix updates the command path and adds a regression check so the docs stay aligned.
```

Use when:

- the issue is public
- the report names a concrete file, command, or behavior
- the maintainer can reproduce or verify the gap
- the follow-up issue or PR keeps private data out of source docs

Avoid:

- crediting vague comments that do not identify a repository improvement
- copying private reproduction data into the issue
- treating a bug report as a promise that a broader roadmap item is accepted

## Eval-Case Addition Credit

Scenario:

```text
A contributor proposes a new eval case that catches a prompt-injection, authorization, approval-bypass, or release-risk gap.
```

Good attribution:

```text
Thanks for the eval-case proposal in issue #<number>. The merged case strengthens the safety gate without weakening local-first behavior.
```

Use when:

- the eval case uses fictional seed data
- the case preserves unsafe leak, unsafe direct side-effect, and unsafe release approval failure expectations
- the PR does not add secrets, paid APIs, private data, or generated runtime artifacts
- `python -B scripts/dev.py quality` passes after the change

Avoid:

- crediting a security report by exposing exploit details before the fix is reviewed
- adding real customer, company, account, or incident details to seed data
- accepting attribution for a case that weakens expected failures to make tests pass

## Useful PR Credit

Scenario:

```text
A contributor opens a small PR that completes an accepted issue and passes review.
```

Good attribution:

```text
Closed by PR #<number>. Thanks for keeping the implementation within the accepted scope and preserving the safety gates.
```

Use when:

- the PR maps to an accepted issue or documented backlog item
- the diff has no hidden side effects
- local and CI gates pass
- the credit stays in the issue or PR thread unless a release note explicitly needs a public mention

Avoid:

- adding credits before the PR is reviewed
- giving credit for unrelated refactors bundled into the PR
- using attribution to bypass the merge bar in `docs/maintainer_review_policy.md`

## Private Feedback Credit

Scenario:

```text
A private message identifies a real setup problem, and the sender asks for public credit.
```

Good attribution:

```text
Thanks to the reporter who flagged this setup gap privately and approved public credit. The public issue describes only the technical fix.
```

Use when:

- the sender explicitly permits public credit
- the public text excludes message quotes, emails, handles, avatars, employer details, account screenshots, and private context
- the credited change is linked to a public issue or PR with a neutral technical description

Avoid:

- committing private messages, account analytics, screenshots, or personal account details
- naming a private reporter without explicit permission
- using private praise as public evidence of adoption or star-growth success

## Rejected Low-Signal Attribution Requests

Scenario:

```text
Someone asks for credit after opening vague issues, noisy docs rewrites, unrelated comments, or activity-only PRs.
```

Good response:

```text
Closing this attribution request because it is not tied to a concrete repository improvement.

Public credit should point to a useful issue, PR, eval case, docs fix, or bug report. This request does not currently identify a verified change that improves setup, safety, release evidence, contributor flow, or demo behavior.
```

Use when:

- the request is about visibility rather than a useful change
- the request pressures maintainers to merge low-signal work
- the request asks for private identity details, profile promotion, collaborator access, or external-account actions

Avoid:

- adding credits to keep issue activity high
- accepting broad attribution claims without a public repository artifact
- rewarding spam, phishing-like links, generated artifacts, or unsafe requests

## Review Checklist

Before adding public attribution:

```bash
python -B scripts/dev.py community-issues
python -B scripts/dev.py pr-policy
python -B scripts/dev.py launch-assets
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

- The credited work maps to a public issue, PR, commit, discussion, or explicitly permissioned public credit.
- The credit does not include private messages, account details, emails, analytics screenshots, private local paths, secrets, or customer data.
- Attribution is not used to imply adoption, production readiness, roadmap acceptance, support guarantees, or star-growth success.
- Low-signal activity, unsafe requests, and unverifiable claims are closed or ignored using `docs/maintainer_review_policy.md`.
- Docs-only credits are reviewed with `docs/docs_only_pr_review_examples.md`.
- Public issue replies are reviewed with `docs/public_roadmap_issue_comment_examples.md`.
- Private or launch-channel feedback is summarized through `docs/launch_feedback_collection_examples.md` before it becomes source content.
