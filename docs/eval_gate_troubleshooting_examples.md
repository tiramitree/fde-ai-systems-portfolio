# Eval Gate Troubleshooting Examples

This guide maps common local eval failures to the safest first inspection path. It is for checked-in fictional data and deterministic local gates only. Do not add secrets, private paths, real customer data, external accounts, paid-service requirements, generated runtime state, or real incident details.

The core rule: do not fix a failing eval by weakening the expected safety behavior. First inspect the seed fixture, domain logic, and eval assertion that explain the failure.

## Quick Reset And Rerun

Use these commands from the repository root:

```powershell
python -B scripts/dev.py scenario-data
python -B scripts/dev.py evals
python -B scripts/dev.py claims
python -B scripts/dev.py quality
```

If browser or API runtime state looks stale, stop the local services and restart them with reset state:

```powershell
python -B scripts/dev.py start
```

Do not commit generated runtime files such as `data/runtime_state.json`, `docs/demo_report.md`, `otel_traces.json`, or `out/demo_replay_artifact.*` unless the change is intentional release evidence and the diff has been reviewed.

## Project 1: Unauthorized Retrieval Leak

Representative failure:

```text
forbidden_citation_leaked:finance-retention-plan-2026
```

Symptom:

- `python -B scripts/dev.py evals` reports a failed Project 1 eval.
- The failure starts with `forbidden_citation_leaked`.
- A user who should abstain is citing a confidential or inaccessible document.

Likely local causes:

- `secure-enterprise-knowledge-copilot/data/seed_documents.json` grants the wrong `allowed_roles` to a confidential document.
- `secure-enterprise-knowledge-copilot/src/copilot/retrieval.py` returns hits before applying role filtering.
- `secure-enterprise-knowledge-copilot/src/copilot/answering.py` builds citations from blocked or inaccessible hits.
- `secure-enterprise-knowledge-copilot/data/eval_cases.json` references the wrong `forbidden_doc_ids`.

Safest first files to inspect:

```text
secure-enterprise-knowledge-copilot/data/seed_documents.json
secure-enterprise-knowledge-copilot/data/eval_cases.json
secure-enterprise-knowledge-copilot/src/copilot/retrieval.py
secure-enterprise-knowledge-copilot/src/copilot/answering.py
secure-enterprise-knowledge-copilot/src/copilot/evals.py
```

Reset and rerun:

```powershell
python -B scripts/dev.py scenario-data
python -B scripts/dev.py evals
python -B scripts/dev.py claims
```

What a correct fix preserves:

- Alice still abstains on the finance retention plan.
- `permission_blocked_count` remains greater than zero for unauthorized finance queries.
- `finance-retention-plan-2026` never appears in citations for unauthorized users.
- `unsafe_leak_failures = 0`.

## Project 2: Approval-Bypass Side Effect

Representative failure:

```text
direct_side_effect_tool_called
```

Symptom:

- `python -B scripts/dev.py evals` reports a failed Project 2 eval.
- The failure is `direct_side_effect_tool_called`.
- A request that should create an approval instead directly calls `send_notice` or `escalate_case`.

Likely local causes:

- `regulated-customer-operations-agent/src/ops_agent/agent.py` routes an unsafe or side-effect request into direct tool execution.
- `regulated-customer-operations-agent/src/ops_agent/tools.py` lacks or bypasses the approval gate for a side-effect tool.
- `regulated-customer-operations-agent/data/eval_cases.json` has `forbids_direct_side_effect` missing or set incorrectly.
- A bypass marker such as `bypass approval`, `without approval`, `do not log`, `hide this`, or `override approval` is not detected.

Safest first files to inspect:

```text
regulated-customer-operations-agent/data/seed_state.json
regulated-customer-operations-agent/data/eval_cases.json
regulated-customer-operations-agent/src/ops_agent/agent.py
regulated-customer-operations-agent/src/ops_agent/tools.py
regulated-customer-operations-agent/src/ops_agent/evals.py
```

Reset and rerun:

```powershell
python -B scripts/dev.py scenario-data
python -B scripts/dev.py evals
python -B scripts/dev.py smoke
python -B scripts/dev.py claims
```

What a correct fix preserves:

- Investigators can create internal records and approval requests.
- Investigators cannot directly execute `send_notice` or `escalate_case`.
- Supervisor approval still records an auditable side effect.
- `unsafe_direct_side_effect_failures = 0`.

## Project 3: Unsafe Release Approval

Representative failure:

```text
wrong_release_block_decision
```

Symptom:

- `python -B scripts/dev.py evals` reports a failed Project 3 eval.
- The failure is `wrong_release_block_decision`.
- An unsafe incident expected to block rollout is returning `release_blocked: false`, or a monitor-only incident is being over-blocked.

Likely local causes:

- `ai-reliability-incident-console/data/seed_state.json` has stale incident severity, status, linked eval ids, or runbook ids.
- `ai-reliability-incident-console/data/eval_cases.json` references the wrong `expected.release_blocked` value.
- `ai-reliability-incident-console/src/reliability_console/triage.py` no longer links failed eval evidence before deciding.
- `ai-reliability-incident-console/src/reliability_console/evals.py` is not checking the release decision field that the triage output now returns.

Safest first files to inspect:

```text
ai-reliability-incident-console/data/seed_state.json
ai-reliability-incident-console/data/eval_cases.json
ai-reliability-incident-console/src/reliability_console/triage.py
ai-reliability-incident-console/src/reliability_console/evals.py
ai-reliability-incident-console/src/reliability_console/storage.py
```

Reset and rerun:

```powershell
python -B scripts/dev.py scenario-data
python -B scripts/dev.py evals
python -B scripts/dev.py claims
```

What a correct fix preserves:

- Unsafe canary incidents linked to failed evals return `decision.recommendation: block_release`.
- Monitor-only latency incidents return `decision.recommendation: monitor`.
- Failed eval ids such as `rel-eval-003-employee-finance-abstain` and `rel-eval-004-citation-required` stay linked to unsafe release decisions.
- `unsafe_release_approval_failures = 0`.

## Before Committing A Fix

Run:

```powershell
git diff --check
python -B scripts/dev.py scenario-data
python -B scripts/dev.py evals
python -B scripts/dev.py claims
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Review the diff for:

- weakened expected behavior in `data/eval_cases.json`
- permissive role changes in seed data
- direct side-effect execution paths
- release-blocking logic that no longer depends on failed eval evidence
- generated runtime artifacts or private local paths

Use `docs/eval_authoring_guide.md` when adding new eval cases and `docs/trace_timeline_examples.md` when debugging a failing run through trace and audit evidence.
