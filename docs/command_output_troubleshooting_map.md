# Command Output Troubleshooting Map

This map helps contributors turn local command output into a safe next step. It uses only local commands and checked-in fictional data. Do not add secrets, private paths, real customer data, external accounts, paid-service requirements, generated runtime files, or real incident details when extending it.

Use `docs/development_issue_solutions.md` for recurring environment-specific notes and `docs/local_artifact_glossary.md` when a failure involves seed, runtime, eval, replay, trace, audit, approval, release evidence, or generated artifacts.

| Command | Success Signal | Common Failure Symptom | Safest First Files To Inspect | Next Command To Run |
| --- | --- | --- | --- | --- |
| `python -B scripts/dev.py verify` | Ends with `Quality gate passed.` after starting or reusing local services. | Service health/readiness refuses connection, a nested quality section fails, or a port is already in use. | `scripts/ci_quality_gate.py`; `scripts/quality_gate.py`; `scripts/start_demo_servers.py`; changed project `app.py` files. | Run the failing narrower gate from the output, then `python -B scripts/dev.py quality`. |
| `python -B scripts/dev.py quality` | Ends with `Quality gate passed.` after architecture, safety, UI, API, smoke, eval, replay, claim, and container checks. | Output stops under a section header such as `scenario-data`, `ui-contracts`, `contracts`, `smoke`, `evals`, or `claims`. | `scripts/quality_gate.py`; the failing `scripts/check_*.py` file; the files named in the failure message. | Run the named section directly, such as `python -B scripts/dev.py scenario-data`, then rerun `python -B scripts/dev.py quality`. |
| `python -B scripts/dev.py fresh-clone-local` | Ends with `Fresh clone experience check passed.` and `Smoke tests: 13/13 passed`. | A clean clone cannot start services, a public asset is missing, or smoke fails on isolated ports. | `scripts/check_fresh_clone_experience.py`; `README.md`; `PROJECT_CONTENT_INDEX.md`; `.gitignore`; recently changed setup, asset, or runtime files. | Fix clone-path assumptions, run `python -B scripts/dev.py safety`, then rerun `python -B scripts/dev.py fresh-clone-local`. |
| `python -B scripts/dev.py runtime-state-isolation` | Ends with `Runtime state isolation checks: ... passed`. | A service writes traces into canonical demo state, ignores `--state-path`, or the isolated state file is missing expected keys. | Project `app.py` files; project `storage.py` files; `scripts/check_runtime_state_isolation.py`; `docs/adr_0004_verification_runtime_state_isolation.md`. | Fix startup/storage routing, run `python -B scripts/dev.py runtime-state-isolation`, then rerun `python -B scripts/dev.py quality`. |
| `python -B scripts/dev.py runtime-latency-budget` | Ends with `Runtime latency budget checks: ... passed`. | A response misses `latency_ms`, trace records do not carry matching latency evidence, or a core local request exceeds the local budget. | Project response builders; project trace writers; `scripts/check_runtime_latency_budget.py`; `docs/api_contracts.md`; `docs/observability_integrity.md`. | Fix the response or trace instrumentation, run `python -B scripts/dev.py runtime-latency-budget`, then rerun `python -B scripts/dev.py quality`. |
| `python -B scripts/dev.py safety` | Prints `Public safety scan passed.` | The scan reports a private path, token marker, generated runtime state, local profile path, or disallowed public file content. | `scripts/public_safety_scan.py`; `git diff`; the exact file named in the safety failure. | Remove or replace unsafe text, run `git diff --check`, then rerun `python -B scripts/dev.py safety`. |
| `python -B scripts/dev.py community-issues` | Prints `Community issue pack check passed: labels, templates, issue pack, and references are aligned.` | Unknown label, unknown dev command, duplicate issue title, missing acceptance criteria, or a completed issue still appears in the active backlog. | `docs/github_initial_issues.md`; `docs/github_labels.json`; `docs/community_backlog.md`; `docs/star_growth_plan.md`; `scripts/check_community_issue_pack.py`. | Fix the issue pack or backlog entry, then rerun `python -B scripts/dev.py community-issues` and `python -B scripts/dev.py safety`. |

## Review Rules

- Fix the failing behavior or documentation drift; do not hide a failure by weakening the check.
- Treat generated files under `out/demo_replay_artifact.*`, `*/data/runtime_state.json`, `*/data/eval_runtime_state.json`, `otel_traces.json`, and `eval_summaries.csv` as local evidence unless a release process explicitly asks for them.
- For public-facing docs or setup changes, finish with `python -B scripts/dev.py fresh-clone-local`.
- For any commit that may be shared, finish with `python -B scripts/dev.py quality`.

Related docs:

- `docs/development_issue_solutions.md`
- `docs/fresh_clone_experience.md`
- `docs/local_artifact_glossary.md`
- `docs/eval_gate_troubleshooting_examples.md`
- `docs/pr_review_runbook.md`
