# Local Artifact Glossary

This glossary explains the repository's local data and evidence artifacts. It is local-only and uses checked-in fictional data. Do not add secrets, private paths, real customer data, external accounts, paid-service requirements, generated runtime files, or real incident details.

Use this page before changing seed fixtures, eval fixtures, runtime state, replay outputs, traces, audit logs, approvals, release evidence, or generated artifacts.

| Term | What It Means | Checked-In Or Generated | Paths And Patterns | Change Guidance |
| --- | --- | --- | --- | --- |
| Seed fixture | Fictional source data used to reset demos into a known state. | Checked in. | `secure-enterprise-knowledge-copilot/data/seed_documents.json`; `regulated-customer-operations-agent/data/seed_state.json`; `ai-reliability-incident-console/data/seed_state.json`. | Edit deliberately when adding fictional users, documents, cases, releases, incidents, runbooks, policies, or sellers. Run `python -B scripts/dev.py scenario-data`. |
| Runtime state | Mutable local state produced while a demo server runs. | Generated. | `*/data/runtime_state.json`; `*/data/runtime_state.tmp`. | Do not edit or commit as source data. Restart with reset state instead. |
| Eval fixture | Deterministic regression case definitions. | Checked in. | `secure-enterprise-knowledge-copilot/data/eval_cases.json`; `regulated-customer-operations-agent/data/eval_cases.json`; `ai-reliability-incident-console/data/eval_cases.json`. | Add one invariant per case and preserve unsafe failure counts at zero. Run `python -B scripts/dev.py evals` and `python -B scripts/dev.py claims`. |
| Eval run | Result of executing eval fixtures against local logic. | Generated. | `*/data/eval_runtime_state.json`; generated summaries printed by `python -B scripts/dev.py evals`; optional `eval_summaries.csv`. | Use as evidence, not source truth. Do not commit generated state unless a release artifact explicitly requires it and the diff is reviewed. |
| Trace-to-eval candidate | Review-only suggestion produced from local traces, audit events, approvals, and release decisions. | Generated. | `out/trace_eval_candidates.json`; `out/trace_eval_candidates.md`; source workflow: `docs/trace_to_eval_workflow.md`. | Use as a review queue, not a golden eval file. Promote only minimal, public-safe expected behavior into checked-in eval fixtures. |
| Replay artifact | Reproducible evidence package for the canonical demo run. | Instructions checked in, outputs generated. | Checked-in instructions: `docs/demo_replay_artifact.md`; generated outputs: `out/demo_replay_artifact.md`, `out/demo_replay_artifact.json`. | Regenerate with `python -B scripts/dev.py replay-artifact`; keep generated `out/` files ignored unless attaching release evidence externally. |
| Trace | Per-run technical record that links a response to retrieval, tool, approval, or release-decision evidence. | Generated runtime evidence. | API endpoints: `/api/traces`; local runtime state: `*/data/runtime_state.json`; OpenTelemetry export: `otel_traces.json`. | Inspect after a run, export for review, but do not treat generated trace ids as stable source data. |
| Audit | Structured event log for security, workflow, approval, and release-decision events. | Generated runtime evidence. | API endpoints: `/api/audit`; local runtime state: `*/data/runtime_state.json`. | Use to verify what happened after a run. Do not add real users, customer data, or external identifiers. |
| Approval | Project 2 governance queue record for blocked side effects that require supervisor action. | Generated from checked-in fictional state. | API endpoint: `/api/approvals`; Project 2 runtime state: `regulated-customer-operations-agent/data/runtime_state.json`; source logic: `regulated-customer-operations-agent/src/ops_agent/tools.py`. | Approval ids can reset between runs. Preserve the rule that investigators cannot directly execute side effects. |
| Release evidence | Project 3 data that explains whether an AI release should block rollout or stay monitor-only. | Seed evidence checked in; decisions generated at runtime. | Seed: `ai-reliability-incident-console/data/seed_state.json`; eval cases: `ai-reliability-incident-console/data/eval_cases.json`; generated decisions: `/api/triage`, `/api/traces`, `/api/audit`. | Unsafe canary incidents must stay linked to failed eval evidence and rollout-blocking remediation. |
| Generated artifact | File produced by a command rather than hand-authored source content. | Generated, sometimes tracked only as intentional release evidence. | `docs/demo_report.md`; `eval_summaries.csv`; `otel_traces.json`; `out/demo_replay_artifact.*`; `out/trace_eval_candidates.*`; `*/data/runtime_state.json`; `*/data/eval_runtime_state.json`. | Review generated diffs carefully and keep private paths, tokens, real customer data, and stale runtime evidence out of commits. |

## Safe Review Flow

Before committing data or evidence changes, run:

```powershell
git diff --check
python -B scripts/dev.py scenario-data
python -B scripts/dev.py evals
python -B scripts/dev.py claims
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

For public clone confidence, also run:

```powershell
python -B scripts/dev.py fresh-clone-local
```

Related docs:

- `docs/eval_authoring_guide.md`
- `docs/trace_to_eval_workflow.md`
- `docs/eval_gate_troubleshooting_examples.md`
- `docs/eval_csv_troubleshooting_examples.md`
- `docs/seed_data_extension_examples.md`
- `docs/trace_timeline_examples.md`
- `docs/demo_replay_artifact.md`
