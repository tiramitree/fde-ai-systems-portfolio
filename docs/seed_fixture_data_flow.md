# Seed Fixture Data Flow

This map explains how the checked-in fictional seed fixtures move through each local service. Use it before editing seed data, eval cases, scenario drafts, storage adapters, or replay evidence.

The short version: seed fixtures are source truth, `runtime_state.json` is generated local state, `eval_runtime_state.json` is generated eval evidence, and browser scenario drafts live in `localStorage`.

## Shared Boundary

| Layer | Source | Runtime Role |
| --- | --- | --- |
| Checked-in seed fixture | `secure-enterprise-knowledge-copilot/data/seed_documents.json`; `regulated-customer-operations-agent/data/seed_state.json`; `ai-reliability-incident-console/data/seed_state.json` | Provides fictional users, documents, policies, cases, releases, incidents, eval runs, and runbooks. |
| Checked-in eval fixture | each project `data/eval_cases.json` | Defines deterministic expected behavior for permission, citation, approval, refusal, and release-blocking checks. |
| Generated demo state | `*/data/runtime_state.json`; `*/data/runtime_state.tmp` | Rebuilt from seed fixtures with `app.py --reset` or `python -B scripts/dev.py start`; stores traces, audit, approvals, and decisions produced by local runs. |
| Generated eval state | `*/data/eval_runtime_state.json` | Used by project eval runners as evidence, not source truth. |
| Browser scenario draft | `localStorage` keys beginning with `fde-scenario-draft:` | Stores local JSON drafts from `/api/scenario`; does not mutate repository seed files. |
| Replay artifacts | `out/demo_replay_artifact.*`, `docs/demo_report.md`, `otel_traces.json`, `eval_summaries.csv` | Generated evidence for review and release workflows. |

Do not add secrets, private paths, real customer data, external accounts, paid-service requirements, generated runtime files, or real incident details.

## Project 1: Secure Enterprise Knowledge Copilot

| Fixture | Loaded Into | API Surface | Evidence Produced |
| --- | --- | --- | --- |
| `secure-enterprise-knowledge-copilot/data/seed_documents.json` users | `storage.seed()` copies users into `runtime_state.json`. | `/api/users`, `/api/documents`, `/api/query` | Trace and audit records include `user_id` and access outcome. |
| `seed_documents.json` documents | `storage.seed()` copies documents and creates chunk rows for retrieval. | `/api/documents`, `/api/query`, `/api/scenario` | Citations, abstention reasons, blocked inaccessible evidence counts, and security events. |
| `secure-enterprise-knowledge-copilot/data/eval_cases.json` | `evals.run_evals()` reads expected behavior directly. | `/api/eval/run`, `/api/eval/latest` | Eval run metrics and case rows appended to runtime or eval state. |

Data flow:

```text
seed_documents.json
  -> storage.seed()
  -> runtime_state.json users/documents/chunks
  -> retrieval.retrieve() filters by tenant and allowed_roles
  -> answering.generate_answer()
  -> citations or abstention
  -> traces and audit_events
```

Important source-to-runtime invariants:

- permission filtering happens before answer generation
- confidential finance evidence remains inaccessible to employee users
- answers with accessible evidence require citations
- unknown, unauthorized, or unsafe retrieved-content paths abstain
- `/api/scenario` exposes a read-only seed snapshot for browser-local drafts

Primary evidence commands:

```bash
python -B scripts/dev.py scenario-data
python -B scripts/dev.py evals
python -B scripts/dev.py observability
python -B scripts/dev.py quality
```

## Project 2: Regulated Customer Operations Agent

| Fixture | Loaded Into | API Surface | Evidence Produced |
| --- | --- | --- | --- |
| `regulated-customer-operations-agent/data/seed_state.json` users | `storage.init_state()` copies users into `runtime_state.json`. | `/api/users`, `/api/agent`, `/api/approval/approve` | Trace and audit records include requester and approver roles. |
| `seed_state.json` policies, products, sellers, listings, cases | `storage.init_state()` copies operational state into `runtime_state.json`. | `/api/cases`, `/api/agent`, `/api/scenario` | Policy citations, violations, approval requests, blocked side effects, notices, and follow-ups. |
| `regulated-customer-operations-agent/data/eval_cases.json` | `evals.run_evals()` drives agent messages against reset state. | `/api/eval/run`, `/api/eval/latest` | Eval metrics for intent, approval creation, refusal, and direct side-effect blocking. |

Data flow:

```text
seed_state.json
  -> storage.init_state()
  -> runtime_state.json users/policies/products/sellers/listings/cases
  -> agent.process_message()
  -> tools.search_recall_policy() and tools.search_listings()
  -> tools.create_violation(), draft_seller_notice(), schedule_followup()
  -> tools.request_approval() instead of direct side effects
  -> supervisor /api/approval/approve
  -> traces, approval_requests, notices, followups, audit_events
```

Important source-to-runtime invariants:

- investigator users can investigate but cannot directly execute `send_notice` or `escalate_case`
- side-effect actions are represented as approval requests with idempotency keys
- supervisor approval is the only path that sends notices or escalates cases
- bypass phrases create refusal evidence and do not create approval requests
- `/api/scenario` is read-only and browser drafts stay in `localStorage`

Primary evidence commands:

```bash
python -B scripts/dev.py scenario-data
python -B scripts/dev.py evals
python -B scripts/dev.py observability
python -B scripts/dev.py contracts
python -B scripts/dev.py quality
```

## Project 3: AI Reliability Incident Console

| Fixture | Loaded Into | API Surface | Evidence Produced |
| --- | --- | --- | --- |
| `ai-reliability-incident-console/data/seed_state.json` users, releases, incidents, eval_runs, runbooks | `storage.init_state()` copies reliability state into `runtime_state.json`. | `/api/users`, `/api/releases`, `/api/incidents`, `/api/eval-runs`, `/api/runbooks`, `/api/triage`, `/api/scenario` | Release decisions, remediation steps, linked failed eval evidence, traces, and audit events. |
| `ai-reliability-incident-console/data/eval_cases.json` | `evals.run_evals()` drives triage expectations against reset state. | `/api/eval/run`, `/api/eval/latest` | Eval metrics for release blocking, severity, linked eval cases, and remediation text. |

Data flow:

```text
seed_state.json
  -> storage.init_state()
  -> runtime_state.json users/releases/incidents/eval_runs/runbooks
  -> triage.triage_incident()
  -> failed eval and incident signal matching
  -> block_release or monitor decision
  -> triage_decisions, traces, audit_events
```

Important source-to-runtime invariants:

- high-risk incidents linked to failed evals block rollout
- latency-only incidents can stay monitor-only when risk evidence is lower
- runbook IDs and incident signals stay attached to the triage evidence
- release decisions append trace and audit evidence
- `/api/scenario` exposes seed and eval snapshots without writing to repository files

Primary evidence commands:

```bash
python -B scripts/dev.py scenario-data
python -B scripts/dev.py evals
python -B scripts/dev.py observability
python -B scripts/dev.py claims
python -B scripts/dev.py quality
```

## Contributor Checklist

Before changing any seed fixture:

1. Edit checked-in seed or eval fixtures, not `runtime_state.json`.
2. Keep data fictional and local-first.
3. Update `docs/demo_state_presets.json` only when canonical demo paths intentionally change.
4. Keep `docs/local_demo_reset_troubleshooting.md`, `docs/local_artifact_glossary.md`, and this map aligned.
5. Run the narrow seed gate first, then the full quality gate.

```bash
python -B scripts/dev.py scenario-data
python -B scripts/dev.py demo-presets
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Run `python -B scripts/dev.py fresh-clone-local` when the change affects public setup, docs navigation, runtime paths, or demo reset behavior.
