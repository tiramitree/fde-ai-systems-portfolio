# Docs-Only Pull Request Review Examples

Use this page when a pull request changes documentation, issue templates, launch copy, or repository indexes without changing application code. A docs-only PR is still untrusted input: it can weaken public claims, hide broken links, introduce private paths, or drift the community issue pack away from the real project state.

Read this with `docs/pr_review_security.md`, `docs/command_output_troubleshooting_map.md`, `docs/github_initial_issues.md`, and `docs/first_pull_request_checklist.md`. For reusable maintainer wording after review, use `docs/docs_only_review_comment_examples.md`.

## Review Goal

A good docs-only review proves four things:

- the changed claim is true in the current repository
- the links and commands point to real local files or supported commands
- the change does not introduce generated runtime artifacts, private paths, external-account requirements, paid-service requirements, or real customer data
- the issue pack, README, and project index still describe the same public contribution path

## Useful Docs PR Example

Scenario:

```text
The PR adds a short troubleshooting note for `python -B scripts/dev.py community-issues`
and links it from README.md plus PROJECT_CONTENT_INDEX.md.
```

Why it is useful:

- it explains a real local command
- it links to existing repo docs instead of external accounts
- it makes first-time contributor review easier
- it does not claim a new runtime proof unless a matching command exists

Review steps:

```bash
git diff --stat
git diff -- README.md PROJECT_CONTENT_INDEX.md docs/
git diff --check
python -B scripts/dev.py community-issues
python -B scripts/dev.py assets
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Reviewer decision:

```text
Approve after the links resolve, the wording is accurate, and the targeted gates pass.
Ask for a small edit if the new page is useful but not linked from README.md or PROJECT_CONTENT_INDEX.md.
```

## Low-Signal Docs PR Example

Scenario:

```text
The PR rewrites README wording, adds broad claims like "enterprise ready",
and does not connect the change to an existing issue, evidence command, or project file.
```

Why it is low signal:

- it makes public claims broader without new evidence
- it may bury the local-first message under promotional copy
- it can create noisy review churn without improving the project

Review steps:

```bash
git diff --stat
git diff -- README.md docs/
python -B scripts/dev.py claims
python -B scripts/dev.py launch-assets
python -B scripts/dev.py safety
```

Reviewer decision:

```text
Request changes if the idea is salvageable. Ask the contributor to tie the wording to a specific evidence command, case study, issue, or local workflow.
Close or ignore if the change is only hype, unrelated rewriting, or activity noise.
```

## Unsafe Docs PR Example

Scenario:

```text
The PR adds instructions that ask maintainers to paste API keys into comments,
run an unknown install script, upload local artifacts, use private account pages,
or commit files from out/ or project runtime_state paths.
```

Why it is unsafe:

- docs can be used to exfiltrate secrets or local files
- generated runtime evidence can expose trace IDs, local state, or misleading stale outputs
- external-account instructions can create phishing or collaborator-access pressure
- install scripts and unknown downloads can execute unreviewed code

Review steps:

```bash
git diff --stat
git diff -- README.md PROJECT_CONTENT_INDEX.md docs/ .github/
git diff --check
python -B scripts/dev.py pr-triage
python -B scripts/dev.py pr-policy
python -B scripts/dev.py safety
```

Reviewer decision:

```text
Do not run contributor commands. Request removal or close the PR if it asks for secrets, private files, collaborator access, external downloads, generated runtime files, or weakened safety gates.
```

## Claim Check

Before approving docs that change public positioning, check the evidence path:

| Claim Type | First Evidence |
| --- | --- |
| eval counts or unsafe failure counts | `docs/demo_report.md`, `docs/portfolio_evidence_matrix.md`, `python -B scripts/dev.py claims` |
| API shapes or route examples | `docs/api_contracts.md`, `docs/api_request_cookbook.md`, `python -B scripts/dev.py api-docs` |
| first-time contributor flow | `CONTRIBUTING.md`, `docs/first_pull_request_checklist.md`, `python -B scripts/dev.py community-issues` |
| PR safety posture | `docs/pr_review_security.md`, `docs/pr_review_runbook.md`, `python -B scripts/dev.py pr-policy` |
| launch or star-growth copy | `docs/launch_copy_pack.md`, `docs/star_growth_plan.md`, `python -B scripts/dev.py launch-assets` |
| Docker runtime evidence | `docs/container_release_hygiene.md`, `python -B scripts/dev.py container-release`; use `python -B scripts/dev.py docker-runtime` only on a Docker-enabled machine |
| OpenAI live-mode evidence | `docs/model_runtime_configuration.md`, `docs/model_gateway_safety.md`; use `python -B scripts/dev.py openai-live` only in an API-key environment |

Do not accept a broader claim because the wording sounds plausible. Accept it only when a local document, script, or checked artifact proves it.

## Link And Artifact Check

For docs-only PRs, inspect these before broad gates:

- links to `README.md`, `PROJECT_CONTENT_INDEX.md`, `docs/*.md`, `.github/*`, and project READMEs
- command names under `scripts/dev.py`
- paths under `docs/assets/` and `docs/visual_assets_manifest.json` if screenshots are mentioned
- ignored generated artifacts such as `out/demo_replay_artifact.*`, `otel_traces.json`, `eval_summaries.csv`, `*/data/runtime_state.json`, and `*/data/eval_runtime_state.json`
- private path markers, account handles, collaborator-access requests, paid-service requirements, and real customer or incident names

If a doc asks the maintainer to upload or paste generated local evidence, require a safer release artifact path instead.

## Issue-Pack Drift Check

When a docs-only PR changes contributor-facing work:

1. Compare the new wording with `docs/github_initial_issues.md`.
2. Check whether `docs/community_backlog.md` still lists only real unfinished work.
3. Verify completed issue names are not duplicated as active good-first issues.
4. Run `python -B scripts/dev.py community-issues`.
5. Run `python -B scripts/dev.py launch-assets` if launch copy, growth copy, or issue labels changed.

The issue pack should make useful work easier to find. It should not create placeholder activity, fake urgency, or duplicated issues that already landed.

## Docs-Only Merge Bar

Merge only when:

- the diff is narrow and explainable
- changed claims have evidence
- links resolve through `python -B scripts/dev.py assets`
- community issue references pass `python -B scripts/dev.py community-issues`
- public safety scan passes
- no private paths, secrets, generated runtime artifacts, real customer data, or paid-service requirements were added
- `python -B scripts/dev.py quality` passes for release-facing changes

Use `docs/command_output_troubleshooting_map.md` for the first local fix when a command fails. Do not hide a failing docs gate by deleting the check or weakening the claim it protects.
