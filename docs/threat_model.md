# System Threat Model

This repository is a local-first demonstration of enterprise AI control boundaries. It is not production software, but the security model is intentionally explicit so a reviewer can ask, "What can go wrong, and what proves the control still works?"

Core principle:

```text
The model is not the security boundary. Permissions, side effects, audit, traces, and eval success are enforced by application code and verified by gates.
```

## AI Governance Control Registry

The checked registry at `docs/ai_governance_control_registry.json` maps the
repository controls to OWASP Top 10 for LLM Applications risks, NIST AI RMF
Govern/Map/Measure/Manage functions, threat IDs, owner roles, evidence files,
evidence commands, and remaining production gaps.

Verify the registry with:

```text
python -B scripts/dev.py governance-controls
```

## Assets

| Asset | Why It Matters |
| --- | --- |
| Internal documents and citations | Users must not receive evidence they cannot access. |
| User identity, role, and group membership | Retrieval and approval behavior depends on deterministic identity context. |
| Retrieved evidence and prompt context | Retrieved text may contain untrusted instructions. |
| Case, seller, listing, approval, and notice state | Agent side effects must be controlled and auditable. |
| API keys and local environment values | Secrets must stay outside the public repository and browser-visible errors. |
| Audit events, traces, eval runs, and release docs | Evidence must explain behavior without leaking private material. |
| GitHub Actions and public PR workflow | External contributors must not gain write tokens or secrets through CI. |

## Threat Matrix

| ID | Threat | Deterministic Control | Evidence |
| --- | --- | --- | --- |
| T01 | Unauthorized document disclosure | Project 1 filters by tenant, role, and source group before retrieval scoring and answer generation; inaccessible chunks are counted but not passed as answer evidence. | `python -B scripts/dev.py evals`, `python -B scripts/dev.py smoke`, `python -B scripts/dev.py observability` |
| T02 | User or retrieved-content prompt injection | User messages are rejected before retrieval when they match injection patterns; retrieved unsafe lines are treated as data and removed from evidence. | `python -B scripts/dev.py evals`, `python -B scripts/dev.py smoke`, `python -B scripts/dev.py observability` |
| T03 | Unsupported or fabricated answers | The answer layer abstains when accessible evidence does not clear the threshold or citation requirements; retrieval evals assert expected source recall before answer text is trusted. | `python -B scripts/dev.py evals`, `python -B scripts/dev.py claims` |
| T04 | External side effect without approval | Project 2 blocks direct side-effect tools for investigator users and creates approval requests with tool-registry policy, dry-run preview, owner role, expiry, and payload-hash evidence instead. | `python -B scripts/dev.py evals`, `python -B scripts/dev.py smoke`, `python -B scripts/dev.py observability` |
| T05 | Approval bypass or non-supervisor approval | Approval execution, rejection, expiry, and outbox retry are supervisor-only; bypass instructions create refusal evidence instead of approvals. | `python -B scripts/dev.py evals`, `python -B scripts/dev.py contracts`, `python -B scripts/dev.py observability` |
| T06 | Duplicate side-effect execution | Approval requests use idempotency keys, write sanitized workflow-run checkpoints, enqueue sanitized action-outbox dispatch checkpoints, retry failed dispatch through the same outbox key, dead-letter repeated pre-side-effect failures, approved side effects write action-run receipts with payload hashes, and already-processed approvals return the existing outbox item and execution receipt without sending duplicate notices. | `python -B scripts/dev.py contracts`, `python -B scripts/dev.py smoke`, `python -B scripts/dev.py observability` |
| T07 | Secret, private path, or internal exception leakage | Public files are scanned for secret-like and local-machine markers; unexpected backend exceptions return generic JSON errors; trace export and trace-to-eval artifacts pass through `public_trace_export_redaction_v1` before leaving local runtime state. | `python -B scripts/dev.py safety`, `python -B scripts/dev.py error-hygiene`, `python -B scripts/dev.py trace-redaction` |
| T08 | Public PR or CI workflow abuse | GitHub Actions run with read-only permissions, safe triggers, hardened checkout, no secrets, and CODEOWNERS/governance plus PR-review-policy checks. | `python -B scripts/dev.py workflow-security`, `python -B scripts/dev.py governance`, `python -B scripts/dev.py pr-policy`, `python -B scripts/dev.py pr-triage` |
| T09 | Dependency or supply-chain drift | Local runtime stays stdlib-first; Docker bases are digest-pinned; Dependabot covers allowed update surfaces. | `python -B scripts/dev.py dependency-surface` |
| T10 | Optional model gateway weakens controls or leaks keys | OpenAI mode is opt-in, key references are constrained, structured outputs are required, and failures fall back locally. | `python -B scripts/dev.py model-gateway-safety` |
| T11 | Trace, audit, workflow-run, approval, action-outbox, or release-decision evidence does not explain behavior | Observability integrity checks connect responses to persisted trace IDs, audit events, blocked actions, workflow-run checkpoints, approval records, action-outbox dispatch/retry/dead-letter records, action-run receipts, and release decisions; export boundaries preserve that evidence while redacting common sensitive markers. | `python -B scripts/dev.py observability`, `python -B scripts/dev.py otel-traces`, `python -B scripts/dev.py trace-redaction` |
| T12 | Browser/static route surprises | Runtime UI contracts verify content types, basic safety headers, JSON 404s, and traversal blocking. | `python -B scripts/dev.py ui-contracts` |
| T13 | Unauthorized or poisoned document ingestion | Project 1 also treats stale connector content and risky source content as ingestion risks. It uses admin-only ingestion, source sync, allowlisted source bundle intake, GitHub connector intake, ingestion jobs, connector status, and source quality inventory with tenant checks, role/classification validation, parser metadata, parser quality metadata, source scan metadata, duplicate protection, `source_hash`, connector metadata, source bundle manifest hashes, GitHub issue/PR source URLs, ACL source metadata, ACL snapshot fail-closed validation, source permission IDs, permission drift evidence, sync cursors, opt-in `prune_missing` stale-source removal, chunk-count evidence, source risk flags, job `idempotency_key`, sanitized job summaries, `dead_lettered` worker failures, retry parent links, `document_ingested`, `source_sync_completed`, `source_bundle_synced`, `github_connector_synced`, `ingestion_job_completed`, and `ingestion_job_dead_lettered` audit events before new content becomes searchable. | `python -B scripts/dev.py contracts`, `python -B scripts/dev.py api-docs`, `python -B scripts/dev.py parser-quality`, `python -B scripts/dev.py source-scan` |

## Trust Boundaries

| Boundary | Trusted Component | Untrusted Input | Rule |
| --- | --- | --- | --- |
| Retrieval | `identity.py`, `source_lifecycle.py`, plus `retrieval.py` tenant/role/source-group and source-lifecycle filters | user question and document corpus | Filter before evidence assembly. |
| Ingestion | `ingestion.py` admin gate, `source_bundle_connector.py` checked-in bundle adapter, `github_connector.py` issue/PR adapter, `ingestion_jobs.py` job ledger, plus `source_parsing.py` parser normalization | admin-supplied source text, connector batch payloads, source bundle manifests and files, GitHub issue/PR records, optional connector ACL snapshots, ingestion job payloads, HTML, CSV, Markdown, or JSON | Validate actor, tenant, classification, roles, duplicate policy, parser metadata, source hash, connector name, source bundle name/path, GitHub owner/repo, external ID, source URL, ACL source, ACL snapshot permission records, source permission ID, permission drift, idempotency key, retry parent, sync cursor, and explicit full-snapshot prune intent before changing searchable chunks. |
| Answering | `answering.py` and `security.py` | user text and retrieved text | Cite accessible evidence or abstain. |
| Agent tools | `tools.py` and `agent.py` | user request and model/router output | Side effects require deterministic approval. |
| Approval | `approve_action`, `reject_approval`, `expire_approval`, and approval endpoints | approval ID, requester role, owner role, expiry, dry-run preview, and decision metadata | Supervisor-only execution or terminal closure without side effects. |
| Model gateway | project `model_gateway.py` files | model output and API availability | Optional model output cannot authorize access or side effects. |
| Trace export | `trace_redaction.py`, `export_traces_otel.py`, and `export_trace_eval_candidates.py` | trace payloads, evidence excerpts, user text, tool results, and generated candidate artifacts | Redact common sensitive markers before generated observability or eval-review artifacts leave local runtime state. |
| Public repo | safety, dependency, workflow, governance, and PR-policy gates | contributor code and public docs | No secrets, no privileged CI, no unreviewed security-boundary changes, and no weakened review heuristics. |
| UI runtime | project `app.py` files | path input and browser requests | Serve known local assets with explicit security headers. |

## Production Controls To Add

- Real authentication and session management.
- PostgreSQL row-level security and transactionally persisted traces/audit events.
- Connector-backed ingestion with source-system user/group permission sync, malware scanning, and parser isolation.
- Immutable audit/event storage with retention and redaction policies.
- Policy-as-code for retrieval permissions, tool authorization, and approval routing.
- OpenTelemetry SDK instrumentation around API handlers, retrieval, model calls, tool calls, approvals, and audit writes.
- Connector-scoped credentials, rate limits, retry policies, and transactional outbox processing for external side effects.
- Red-team eval ingestion from production incidents and support tickets.

## Technical Review Framing

Use this concise answer:

```text
I separate threats into information disclosure, prompt injection, unsafe side effects, evidence gaps, public-repo supply-chain risk, and optional model-provider risk. The important part is that each control has a deterministic owner and a command that proves it. The model can help draft or classify, but the app decides what evidence is visible, what tools can execute, and what gets recorded for audit.
```
