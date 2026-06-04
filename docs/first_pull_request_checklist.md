# First Pull Request Checklist

Use this checklist for the first local pull request. It keeps the contribution path small, reviewable, and safe without requiring external accounts, paid APIs, private files, generated runtime state, or real customer data.

Read this with `CONTRIBUTING.md`, `docs/code_tour.md`, `docs/issue_to_pr_handoff_flow.md`, `docs/pr_review_security.md`, `docs/command_output_troubleshooting_map.md`, and `docs/local_demo_reset_troubleshooting.md`.

## 1. Start Clean

From a fresh checkout or a clean local branch:

```bash
git status --short --branch
python -B scripts/dev.py verify
git switch -c docs/describe-the-change
```

If `verify` fails before any local edits, inspect `docs/command_output_troubleshooting_map.md` first. Do not hide a failing gate by weakening checks, changing expected safety behavior, or committing generated runtime artifacts.

## 2. Pick The Smallest Route

| Change Route | Typical Files | Targeted Gates |
| --- | --- | --- |
| Docs-only | `README.md`, `PROJECT_CONTENT_INDEX.md`, `docs/*.md`, `.github/ISSUE_TEMPLATE/*` | `python -B scripts/dev.py community-issues`; `python -B scripts/dev.py assets`; `python -B scripts/dev.py safety` |
| Frontend | project `web/index.html`, `web/styles.css`, `web/js/*.js` | `python -B scripts/dev.py frontend`; `python -B scripts/dev.py ui-contracts`; `python -B scripts/dev.py visual-assets` |
| Backend/API | project `app.py`, `src/<package>/api.py`, `docs/api_contracts.md` | `python -B scripts/dev.py api-docs`; `python -B scripts/dev.py contracts`; `python -B scripts/dev.py error-hygiene` |
| Domain logic | `retrieval.py`, `answering.py`, `agent.py`, `tools.py`, `triage.py`, `storage.py` | `python -B scripts/dev.py architecture`; `python -B scripts/dev.py evals`; `python -B scripts/dev.py smoke` |
| Seed/eval | project `data/*.json`, `docs/demo_state_presets.json`, seed/eval docs | `python -B scripts/dev.py scenario-data`; `python -B scripts/dev.py demo-presets`; `python -B scripts/dev.py claims` |
| Visual-asset | `docs/assets/*`, `docs/visual_assets_manifest.json`, visual asset docs | `python -B scripts/dev.py visual-asset-diff`; `python -B scripts/dev.py visual-assets`; `python -B scripts/dev.py assets` |

If a change crosses routes, run the targeted gates for every affected route.

## 3. Review Your Diff Before Running Broad Gates

Check the diff yourself before running the full release gate:

```bash
git diff --stat
git diff --check
git status --short --branch
```

Do not commit these as source content:

- `*/data/runtime_state.json`
- `*/data/eval_runtime_state.json`
- `*/data/runtime_state.tmp`
- `out/demo_replay_artifact.*`
- `otel_traces.json`
- `eval_summaries.csv`
- local `localStorage` exports
- personal paths, tokens, private links, account credentials, or real incident/customer data

Use `docs/local_demo_reset_troubleshooting.md` if browser drafts, reset state, approval ids, trace ids, or eval outputs look stale.

## 4. Run The Full Local Bar

After targeted gates pass, run:

```bash
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Run the clean-clone proof when the change affects public setup, docs navigation, runtime paths, screenshots, reset behavior, or release-facing claims:

```bash
python -B scripts/dev.py fresh-clone-local
```

## 5. Prepare The PR Handoff

Before opening the PR:

```bash
git status --short --branch
git diff --stat
git log --oneline --decorate --max-count=5
```

In the PR body, include:

- what changed and why
- which route you used from the table above
- which commands passed
- whether generated artifacts were intentionally refreshed
- any remaining manual follow-up

## 6. Reviewer Safety Notes

Public PRs are untrusted input. Maintainers should read the diff before running contributor code, then use `docs/pr_review_security.md` and `docs/pr_review_runbook.md` for the merge bar.

Contributors should not ask maintainers for secrets, collaborator access, local files, account credentials, paid-service keys, or private environment details. A good first PR should be narrow, local-first, and easy to explain from the diff.
