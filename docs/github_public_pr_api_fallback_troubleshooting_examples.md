# GitHub Public PR API Fallback Troubleshooting Examples

Use this page when public PR triage falls back from the GitHub API to the public pulls page. Read it with `docs/pr_review_runbook.md`, `docs/pr_review_security.md`, `docs/post_publish_warning_examples.md`, `docs/github_api_rate_limit_troubleshooting_examples.md`, `docs/maintainer_review_policy.md`, and `docs/command_output_troubleshooting_map.md`.

The core rule: public page visibility, API file-level triage, and strict review confidence prove different things. Do not claim no risky PRs until API or authenticated evidence confirms it.

## Expected Evidence Split

Public visibility evidence:

```bash
python -B scripts/dev.py pr-triage
```

File-level PR triage evidence:

```bash
python -B scripts/review_open_prs.py --strict
python -B scripts/dev.py pr-policy
```

Merge-readiness evidence:

```bash
python -B scripts/dev.py governance
python -B scripts/dev.py workflow-security
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

The public HTML fallback can show whether visible open PRs exist. It cannot inspect changed files, omitted patches, secrets, workflow edits, dependency changes, or high-impact paths. Use API-backed or authenticated evidence before approving workflows, running contributor code, closing as safe, or merging.

## Unauthenticated API Limits

Symptom:

- `python -B scripts/dev.py pr-triage` says the GitHub API was unavailable or rate-limited.
- Local gates still pass.
- The public pulls page is reachable.

Wrong fix:

- Treat API rate limits as local code failure.
- Claim file-level triage passed from local quality.
- Add token values or private account instructions to public docs.

Safe fix:

```bash
python -B scripts/dev.py pr-triage
python -B scripts/dev.py pr-policy
```

Use `docs/github_api_rate_limit_troubleshooting_examples.md` for broader API uncertainty. Authenticate in a maintainer environment before approving workflows or merging when file-level triage could not run.

## Public Pulls Page Fallback

Symptom:

- API PR listing fails.
- The script prints `Open PRs: 0`.
- The script also says the HTML fallback found no open PRs.

Wrong fix:

- Claim the API inspected every PR file.
- Treat public pulls page visibility as proof that review policy is complete.
- Remove strict review steps from the runbook.

Safe fix:

```bash
python -B scripts/dev.py pr-triage
python -B scripts/dev.py github-maintenance
```

Record the result as public visibility evidence only. If any workflow approval, merge, close, or contributor-code execution is being considered, rerun with API access or authenticated GitHub CLI first.

## Missing File-Level Triage

Symptom:

- The public pulls page shows one or more open PR numbers.
- `review_open_prs.py` cannot fetch `/pulls/{number}/files`.
- The script cannot report changed files, additions, deletions, findings, or required merge gates.

Wrong fix:

- Run contributor code to discover what changed.
- Assume visible PR numbers are low risk.
- Merge or close based only on title or author.

Safe fix:

```bash
python -B scripts/review_open_prs.py --strict
python -B scripts/dev.py pr-policy
python -B scripts/dev.py safety
```

Read the diff through the GitHub UI or an authenticated API path before running code. Follow `docs/pr_review_runbook.md` and `docs/maintainer_review_policy.md` when file-level triage is incomplete.

## Strict-Mode Review

Symptom:

- Non-strict `pr-triage` exits successfully.
- A release or merge review asks whether public PR state is safe enough.
- API fallback, omitted patches, or high-risk findings are possible.

Wrong fix:

- Treat non-strict success as merge approval.
- Skip strict mode because local quality passed.
- Claim no risky PRs without API-backed file evidence.

Safe fix:

```bash
python -B scripts/review_open_prs.py --strict
python -B scripts/dev.py pr-policy
python -B scripts/dev.py quality
```

Strict mode is the safer review boundary when high-risk findings should block automation. It still does not replace human diff review for public contributions.

## Stale No-Open-PR State

Symptom:

- `pr-triage` recently printed `Open PRs: 0`.
- A new public PR arrives after that command ran.
- README or release notes still reference an older no-open-PR state.

Wrong fix:

- Reuse an old no-open-PR line as current evidence.
- Claim the repository has no pending PR work without rerunning triage.
- Treat GitHub Actions green as proof that no external PRs exist.

Safe fix:

```bash
python -B scripts/dev.py pr-triage
python -B scripts/dev.py github-readiness
```

Use fresh command output for PR-state claims. Keep no-open-PR wording timestamped or conservative unless it was just checked against the current public repository state.

## Review Checklist

- `python -B scripts/dev.py pr-triage` is run before approving workflows, running contributor code, or merging.
- API fallback output is recorded as public visibility evidence only.
- API-backed file-level triage is required before claiming no risky PRs.
- `python -B scripts/review_open_prs.py --strict` is used when high-risk findings should block review automation.
- `docs/pr_review_runbook.md` and `docs/maintainer_review_policy.md` remain the merge bar.
- `docs/github_api_rate_limit_troubleshooting_examples.md` is used for broader API uncertainty.
- `python -B scripts/dev.py pr-policy` passes after changing PR review docs or scripts.
- Public docs do not claim no risky PRs until API or authenticated evidence confirms it.
