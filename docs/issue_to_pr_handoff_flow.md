# Issue To PR Handoff Flow

Use this page when a contributor wants to turn one approved public issue into a small, reviewable pull request. Read it with `docs/github_initial_issues.md`, `docs/first_pull_request_checklist.md`, `docs/public_roadmap_issue_comment_examples.md`, `docs/docs_only_review_comment_examples.md`, and `docs/pr_review_security.md`.

This flow is local-first. It does not require external accounts, paid APIs, generated runtime files, private paths, or real customer data. Public PRs are still untrusted input, so maintainers should read the diff before running contributor code.

## 1. Pick One Issue

Choose one active issue from `docs/github_initial_issues.md` or `docs/community_backlog.md`.

Good issue choices:

- have clear acceptance criteria
- name the expected docs, frontend, backend, eval, visual asset, Docker, or release route
- include at least one `python -B scripts/dev.py ...` verification command
- can be completed without broad rewrites or unrelated cleanup

Avoid:

- combining multiple issues in one pull request
- changing generated runtime files as source evidence
- adding external services to the default local path
- asking maintainers for secrets, private files, private account data, or local machine details

## 2. Create A Small Branch

Use a branch name that describes the issue and the route:

```bash
git status --short --branch
git switch -c docs/issue-to-pr-handoff
```

Examples:

| Route | Branch Name |
| --- | --- |
| Docs-only | `docs/release-attachment-examples` |
| Frontend | `frontend/trace-copy-state` |
| Backend/API | `api/typed-error-example` |
| Eval | `eval/retrieval-abstain-case` |
| Visual asset | `visual/mobile-screenshot-refresh` |
| Docker | `docker/runtime-failure-notes` |

Keep branch names descriptive and short. Do not include user names, organization names, tokens, ticket systems, or private project identifiers.

## 3. Keep The Diff Narrow

Start from the route table in `docs/first_pull_request_checklist.md`.

| Route | Typical Files | Targeted Gates |
| --- | --- | --- |
| Docs-only | `README.md`, `PROJECT_CONTENT_INDEX.md`, `docs/*.md`, `.github/ISSUE_TEMPLATE/*` | `python -B scripts/dev.py community-issues`; `python -B scripts/dev.py assets`; `python -B scripts/dev.py safety` |
| Frontend | project `web/index.html`, `web/styles.css`, `web/js/*.js` | `python -B scripts/dev.py frontend`; `python -B scripts/dev.py ui-contracts`; `python -B scripts/dev.py visual-assets` |
| Backend/API | project `app.py`, `src/<package>/api.py`, `docs/api_contracts.md` | `python -B scripts/dev.py api-docs`; `python -B scripts/dev.py contracts`; `python -B scripts/dev.py error-hygiene` |
| Domain logic | `retrieval.py`, `answering.py`, `agent.py`, `tools.py`, `triage.py`, `storage.py` | `python -B scripts/dev.py architecture`; `python -B scripts/dev.py evals`; `python -B scripts/dev.py smoke` |
| Seed/eval | project `data/*.json`, `docs/demo_state_presets.json`, seed/eval docs | `python -B scripts/dev.py scenario-data`; `python -B scripts/dev.py demo-presets`; `python -B scripts/dev.py claims` |
| Visual asset | `docs/assets/*`, `docs/visual_assets_manifest.json`, visual asset docs | `python -B scripts/dev.py visual-asset-diff`; `python -B scripts/dev.py visual-assets`; `python -B scripts/dev.py assets` |
| Docker docs/config | `docker-compose.yml`, `*/Dockerfile`, `*/.dockerignore`, Docker docs | `python -B scripts/dev.py container-release`; `python -B scripts/dev.py safety` |

If the change crosses routes, name every affected route in the PR body and run the targeted gates for each route.

## 4. Review Before Broad Gates

Before running the full local bar:

```bash
git diff --stat
git diff --check
git status --short --branch
```

Do not include these as source content:

- `*/data/runtime_state.json`
- `*/data/eval_runtime_state.json`
- `out/demo_replay_artifact.*`
- `otel_traces.json`
- `eval_summaries.csv`
- local browser storage exports
- Docker logs, collector logs, environment dumps, private paths, or real incident/customer data

If any generated file appears in the diff, either remove it or explain why a release process intentionally needs it.

## 5. Run The Local Bar

Run the route-specific gates first, then:

```bash
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Run this before publishing or requesting broad review when setup paths, public docs navigation, runtime paths, screenshots, or release-facing claims changed:

```bash
python -B scripts/dev.py fresh-clone-local
```

Do not hide a failing gate by deleting the check, weakening the claim, or moving evidence into ignored generated artifacts.

## 6. PR Body

Use a compact PR body:

```text
Summary:
- <what changed>
- <why this solves issue #N>

Route:
- <docs-only | frontend | backend/API | domain logic | seed/eval | visual asset | Docker docs/config>

Verification:
- `python -B scripts/dev.py ...`
- `python -B scripts/dev.py safety`
- `python -B scripts/dev.py quality`

Generated artifacts:
- None, or explain the intentional release artifact.

Follow-up:
- None, or name the remaining manual/environment-dependent action.
```

Keep the PR body factual. Do not claim Docker runtime, OpenAI live mode, GitHub release, branch protection, social preview, profile pin, or launch feedback unless the matching proof exists.

## 7. Maintainer Review Notes

Maintainers should:

- run `python -B scripts/dev.py pr-triage` for visible public PRs
- read the diff before running contributor code
- compare the PR with the issue acceptance criteria
- use `docs/public_roadmap_issue_comment_examples.md` before accepting, narrowing, closing, or linking public roadmap issue work
- run the route-specific gates and the merge bar from `docs/pr_review_security.md`
- use `docs/docs_only_review_comment_examples.md` for docs-only approve, request-changes, close-as-unsafe, or close-as-low-signal wording

Request changes when the PR is useful but missing links, evidence commands, or narrow wording. Close or ignore changes that ask for secrets, private files, unsafe commands, external account access, broad rewrites, generated runtime evidence, or weakened safety gates.

## Done Criteria

A clean issue-to-PR handoff has:

- one issue addressed
- one clear route
- narrow file changes
- no unsafe generated artifacts
- targeted gates passed
- `python -B scripts/dev.py safety` passed
- `python -B scripts/dev.py quality` passed
- reviewer notes tied to the issue acceptance criteria
