# API Contracts

Run:

```bash
python -B scripts/dev.py contracts
python -B scripts/dev.py api-docs
```

The demos expose small HTTP APIs so the browser remains a thin client over explicit backend boundaries. `contracts` starts isolated services and verifies response shapes at runtime. `api-docs` verifies this document stays aligned with the source routes and public evidence map.

## Shared Rules

- Responses are JSON.
- Errors use `{"error": "message"}` with an HTTP status code.
- Runtime route contracts are checked separately by `python -B scripts/dev.py ui-contracts`.
- The model is not the API authorization boundary; permission and approval checks happen in application code before responses are returned.

## Secure Enterprise Knowledge Copilot

Source:

- `secure-enterprise-knowledge-copilot/src/copilot/api.py`
- Runtime gate: `scripts/check_api_contracts.py`

### Routes

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Service health and app name. |
| GET | `/api/users` | Demo users with `id`, `name`, `role`, and `tenant_id`. |
| GET | `/api/documents?user_id=alice` | Visible document metadata for the requester. Document `body` is never returned. |
| GET | `/api/traces?limit=25` | Recent trace records. |
| GET | `/api/audit?limit=50` | Recent audit events. |
| GET | `/api/eval/latest` | Latest eval run record. |
| GET | `/api/scenario` | Fictional seed/eval snapshot for the browser-local scenario draft editor. |
| POST | `/api/query` | Permission-aware answer generation with citations or abstention. |
| POST | `/api/documents/ingest` | Admin-only local ingestion of searchable text, Markdown, CSV, HTML, or JSON content into the permission-aware document store. |
| POST | `/api/eval/run` | Run the project eval suite. |

### Query Response Shape

`POST /api/query` returns:

- `trace_id`
- `user`
- `question`
- `answer`
- `citations`
- `confidence`
- `missing_evidence`
- `abstain_reason`
- `security_events`
- `model_provider`
- `openai_gateway_enabled`
- `retrieved`
- `permission_blocked_count`
- `latency_ms`

Security contract:

- unauthorized evidence is filtered before answer generation
- retrieved prompt-injection markers become security events
- unsupported or inaccessible questions abstain
- inaccessible document bodies are not returned in `/api/documents`
- document body is never returned

### Document Ingestion Response Shape

`POST /api/documents/ingest` accepts an admin `user_id`, a `document` object, and optional `replace`.

The document object supports:

- `title`
- `body` or `content`
- `classification`
- `allowed_roles`
- `source_url`
- `source_mime`
- `version`
- `updated_at`

The route returns:

- `document`
- `chunk_count`
- `ingestion.actor_user_id`
- `ingestion.replace`
- `ingestion.source_hash`
- `ingestion.supported_mime_types`

Ingestion contract:

- only admin users can ingest documents
- admins can ingest only into their own tenant
- confidential documents cannot include the `employee` role
- duplicate document IDs require `replace`
- the raw document body is never returned
- ingestion writes a `document_ingested` audit event with `source_hash`, `chunk_count`, `source_mime`, and role metadata

### Scenario Snapshot Shape

`GET /api/scenario` returns:

- `scenario.app`
- `scenario.draft_mode`
- `scenario.write_policy`
- `scenario.files`
- `scenario.files[].path`
- `scenario.files[].kind`
- `scenario.files[].record_count`
- `scenario.files[].content`

Scenario contract:

- only allowlisted fictional seed and eval files are returned
- runtime state files are not returned
- `draft_mode` is `browser_local_storage`
- `write_policy` is `read_only_seed_snapshot`

## Regulated Customer Operations Agent

Source:

- `regulated-customer-operations-agent/src/ops_agent/api.py`
- Runtime gate: `scripts/check_api_contracts.py`

### Routes

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Service health and app name. |
| GET | `/api/users` | Demo users with `id`, `name`, and `role`. |
| GET | `/api/cases` | Demo operational cases. |
| GET | `/api/approvals` | Approval queue state. |
| GET | `/api/traces?limit=25` | Recent trace records. |
| GET | `/api/audit?limit=50` | Recent audit events. |
| GET | `/api/eval/latest` | Latest eval run record. |
| GET | `/api/scenario` | Fictional seed/eval snapshot for the browser-local scenario draft editor. |
| POST | `/api/agent` | Process an investigator/supervisor workflow message. |
| POST | `/api/approval/approve` | Supervisor-only approval execution. |
| POST | `/api/eval/run` | Reset state and run the project eval suite. |

### Agent Response Shape

`POST /api/agent` returns:

- `trace_id`
- `intent`
- `response`
- `tool_calls`
- `approvals`
- `blocked_actions`
- `cited_policies`
- `outputs`
- `case`
- `model_router`

Security contract:

- investigator side effects create approval requests instead of executing directly
- non-supervisors receive `403` when approving actions
- supervisor approval is idempotent
- bypass instructions create blocked-action evidence instead of side effects
- `model_router` reports the actual routing source for the intent classification path, not just whether OpenAI mode was configured

### Scenario Snapshot Shape

`GET /api/scenario` returns:

- `scenario.app`
- `scenario.draft_mode`
- `scenario.write_policy`
- `scenario.files`
- `scenario.files[].path`
- `scenario.files[].kind`
- `scenario.files[].record_count`
- `scenario.files[].content`

Scenario contract:

- only allowlisted fictional seed and eval files are returned
- runtime state files are not returned
- `draft_mode` is `browser_local_storage`
- `write_policy` is `read_only_seed_snapshot`

## AI Reliability Incident Console

Source:

- `ai-reliability-incident-console/src/reliability_console/api.py`
- Runtime gate: `scripts/check_api_contracts.py`

### Routes

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Service health and app name. |
| GET | `/api/users` | Demo users with `id`, `name`, and `role`. |
| GET | `/api/releases` | Release records and canary rollout state. |
| GET | `/api/incidents` | Release incident records with severity, category, signals, linked eval cases, and runbooks. |
| GET | `/api/eval-runs` | Release eval run history. |
| GET | `/api/runbooks` | Remediation runbooks referenced by incidents. |
| GET | `/api/traces?limit=25` | Recent triage trace records. |
| GET | `/api/audit?limit=50` | Recent audit events. |
| GET | `/api/eval/latest` | Latest release reliability eval run record. |
| GET | `/api/scenario` | Fictional seed/eval snapshot for the browser-local scenario draft editor. |
| POST | `/api/triage` | Triage an incident against a release and produce rollout decision evidence. |
| POST | `/api/eval/run` | Reset state and run the project eval suite. |

### Triage Response Shape

`POST /api/triage` returns:

- `trace_id`
- `release`
- `incident`
- `decision`
- `failed_evals`
- `remediation_steps`
- `evidence`

The `decision` object includes:

- `trace_id`
- `user_id`
- `release_id`
- `incident_id`
- `severity`
- `recommendation`
- `release_blocked`
- `root_cause`
- `confidence`

Release reliability contract:

- unsafe rollout incidents return `block_release`
- latency-only incidents can return `monitor`
- failed eval cases are returned as `failed_evals`
- evidence includes linked eval case IDs, runbook IDs, and incident signals
- trace and audit records are created for triage decisions

### Scenario Snapshot Shape

`GET /api/scenario` returns:

- `scenario.app`
- `scenario.draft_mode`
- `scenario.write_policy`
- `scenario.files`
- `scenario.files[].path`
- `scenario.files[].kind`
- `scenario.files[].record_count`
- `scenario.files[].content`

Scenario contract:

- only allowlisted fictional seed and eval files are returned
- runtime state files are not returned
- `draft_mode` is `browser_local_storage`
- `write_policy` is `read_only_seed_snapshot`

## Technical Review Framing

Use this answer:

```text
The browser talks to a small documented API surface. I verify the response shapes at runtime with `contracts`, and I verify the public API documentation with `api-docs` so a reviewer can map UI behavior to backend responsibilities. The important boundary is that permissions and side effects are enforced before the JSON response, while rollout decisions are backed by deterministic eval and incident evidence instead of trusting model text. Scenario editing is deliberately browser-local: the API exposes a read-only seed snapshot, and the UI stores drafts in localStorage instead of mutating repository data.
```
