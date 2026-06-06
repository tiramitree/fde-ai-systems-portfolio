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
| GET | `/api/users` | Demo users with `id`, `name`, `role`, `tenant_id`, `group_ids`, and `source_principals`. |
| GET | `/api/documents?user_id=alice` | Visible document metadata for the requester. Document `body` is never returned. |
| GET | `/api/traces?limit=25` | Recent trace records. |
| GET | `/api/audit?limit=50` | Recent audit events. |
| GET | `/api/ingestion/jobs?user_id=avery&limit=25` | Admin-only ingestion job ledger with sanitized input summaries, status, retry links, and dead-letter evidence. |
| GET | `/api/connectors/status?user_id=avery&limit=100` | Admin-only connector lifecycle summary derived from ingestion jobs, including health, cursors, counts, and dead-letter state. |
| GET | `/api/eval/latest` | Latest eval run record. |
| GET | `/api/scenario` | Fictional seed/eval snapshot for the browser-local scenario draft editor. |
| POST | `/api/query` | Permission-aware answer generation with citations or abstention. |
| POST | `/api/documents/ingest` | Admin-only local ingestion of searchable text, Markdown, CSV, HTML, or JSON content into the permission-aware document store. |
| POST | `/api/sources/sync` | Admin-only connector-style batch source sync with external IDs, sync cursor, optional source ACL snapshot, permission drift evidence, parser normalization, chunking, and audit evidence. |
| POST | `/api/ingestion/jobs` | Admin-only local ingestion worker contract for source sync jobs with idempotency, inline execution, retry parent links, completion audit, and dead-letter audit. |
| POST | `/api/connectors/github/sync` | Admin-only GitHub read connector that normalizes issue/PR records into source sync jobs with source URLs, permission snapshots, idempotency, citation-ready chunks, and audit evidence. |
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
- `retrieval_profile`
- `permission_blocked_count`
- `latency_ms`

Security contract:

- unauthorized evidence is filtered before answer generation
- retrieved prompt-injection markers become security events
- unsupported or inaccessible questions abstain
- inaccessible document bodies are not returned in `/api/documents`
- document body is never returned

Retrieval contract:

- `retrieval_profile.name` is `local-hybrid-v1` in the local runtime
- `retrieval_profile.score_components` lists `bm25_like`, `title`, `phrase`, `semantic_family`, and `vector`
- `retrieval_profile.candidate_strategy` is `local_full_scan` for the default JSON runtime and `postgres_hybrid_sql_v1` for the PostgreSQL/pgvector runtime
- `retrieval_profile.candidate_source_count` records how many retrieval candidates were returned by the storage/search layer before final scoring
- `retrieval_profile.reranker` is `local-evidence-reranker-v1` for the default deterministic reranker boundary
- `retrieval_profile.rerank_features` lists the deterministic rerank features used before answer assembly
- `retrieval_profile.embedding_model` is `local-hashing-v1` and `retrieval_profile.embedding_dimensions` is `1536` for the local deterministic embedding boundary
- `retrieval_profile.permission_filter` is `tenant_identity_before_scoring`
- permission filtering uses tenant, role, and source-group identity before scoring; `allowed_roles` remains the coarse-grained fallback while `allowed_groups` and `source_acl_principals` demonstrate the source ACL migration path
- `citations[].source_span` and `retrieved[].source_span` expose the cited chunk range over parser `normalized_text`
- `citations[].evidence_excerpt` is the accessible sentence-level support used for answer assembly
- `citations[].evidence_spans` contains sentence-level evidence records; each record has `text` plus `evidence_spans[].source_span` over parser `normalized_text`
- `source_span.text_unit` is `normalized_text`; `source_span.start_line`, `source_span.end_line`, `source_span.start_char`, and `source_span.end_char` are integer offsets into parser-normalized source text
- `retrieved[].score_breakdown` exposes lexical, title, phrase, semantic, vector, matched-term, and semantic-family evidence for review
- `retrieved[].rerank_score` and `retrieved[].rerank_breakdown` expose the staged reranker decision separately from first-stage retrieval scoring
- `retrieved[].embedding_model` and `retrieved[].embedding_dimensions` expose embedding provenance, while raw embedding vectors are not returned
- evals assert expected retrieved document IDs and citation span coverage before answer generation changes are trusted

### Document Ingestion Response Shape

`POST /api/documents/ingest` accepts an admin `user_id`, a `document` object, and optional `replace`.

The document object supports:

- `title`
- `body` or `content`
- optional `document.file.filename`
- optional `document.file.content_base64`
- optional `document.file.mime_type`
- `classification`
- `allowed_roles`
- optional `allowed_groups`
- optional `source_acl_principals`
- `source_url`
- `source_mime`
- `version`
- `updated_at`
- `source_connector`
- `external_id`
- `acl_source`
- `sync_cursor`

The route returns:

- `document`
- `chunk_count`
- `ingestion.actor_user_id`
- `ingestion.replace`
- `ingestion.source_hash`
- `ingestion.supported_mime_types`
- `ingestion.parser.name`
- `ingestion.parser.normalized_characters`
- `ingestion.parser.metadata`
- `ingestion.parser.warnings`
- `ingestion.source.file`
- `ingestion.source.connector`
- `ingestion.source.external_id`
- `ingestion.source.acl_source`
- `ingestion.source.allowed_groups`
- `ingestion.source.source_acl_principals`
- `ingestion.source.sync_cursor`
- `ingestion.chunk_source_span_unit`
- `ingestion.chunk_source_span_count`
- `ingestion.embedding.model`
- `ingestion.embedding.dimensions`
- `ingestion.embedding.chunk_embedding_count`

Ingestion contract:

- only admin users can ingest documents
- admins can ingest only into their own tenant
- confidential documents cannot include the `employee` role
- duplicate document IDs require `replace`
- the raw document body is never returned
- file-like ingestion accepts UTF-8 text files through `document.file.content_base64`; returned public metadata includes `source_file.file_name`, `source_file.file_size_bytes`, `source_file.file_content_encoding`, and inferred MIME provenance without returning file contents
- ingestion normalizes supported source formats through parser versions such as `plain-text-v1`, `markdown-v1`, `csv-v1`, `html-v1`, and `json-v1`
- ingestion records chunk source spans over parser `normalized_text`; `chunk_source_span_unit` is `normalized_text` and `chunk_source_span_count` matches `chunk_count`
- ingestion creates local deterministic chunk embeddings with model `local-hashing-v1` and dimension `1536`; raw vectors are stored for retrieval/indexing but not returned by the public API
- CSV parser metadata includes `row_count`, `column_count`, and `has_header`; parser warnings are surfaced as `parser_warnings`
- ingestion writes a `document_ingested` audit event with `source_hash`, `chunk_count`, `source_mime`, `source_file`, `parser_warnings`, source span metadata, embedding metadata, role metadata, and source-group ACL metadata

### Source Sync Response Shape

`POST /api/sources/sync` accepts an admin `user_id`, a `connector` object, a non-empty `documents` list, and optional `replace`.
It also accepts optional boolean `prune_missing`, which should be used only for full connector snapshots.

The connector object supports:

- `name`
- `cursor`
- `acl_source`
- optional `acl_snapshot.version`
- optional `acl_snapshot.documents`

Each synced document supports the same fields as local ingestion plus:

- `id`
- `external_id`
- connector-derived `source_url` when one is not provided

The route returns:

- `sync.actor_user_id`
- `sync.connector`
- `sync.cursor`
- `sync.acl_source`
- `sync.acl_snapshot_version`
- `sync.acl_drift_count`
- `sync.acl_drift_doc_ids`
- `sync.prune_missing`
- `sync.pruned_count`
- `sync.pruned_doc_ids`
- `sync.document_count`
- `sync.chunk_count`
- `sync.replaced_count`
- `sync.parser_warnings`
- `documents`
- `documents[].source_connector`
- `documents[].external_id`
- `documents[].acl_source`
- `documents[].sync_cursor`
- `documents[].allowed_roles_source`
- `documents[].allowed_groups`
- `documents[].source_acl_principals`
- `documents[].source_acl_version`
- `documents[].source_acl_permission_id`
- `documents[].source_acl_principal_count`

Source sync contract:

- only admin users can sync connector sources
- synced documents are normalized through the same parser, chunking, embedding, permission, and body-hiding path as local ingestion
- the API accepts at most ten documents per local sync request so demo state remains reviewable
- connector `name`, external document ID, ACL source, ACL snapshot version, source permission ID, allowed-role source, allowed groups, source ACL principals, and sync cursor are persisted on documents and chunks
- when `connector.acl_snapshot` is present, each synced document must have a matching ACL record; missing ACL records fail closed before searchable chunks are written
- source ACL roles override document payload roles, source ACL groups are carried into the same permission filter, and classification validation still prevents confidential documents from being widened to employee access
- resyncs compare previous and current roles and return `acl_role_drift` plus batch `acl_drift_count` / `acl_drift_doc_ids`
- when `prune_missing` is `true`, documents already indexed for the same tenant and connector but absent from the current synced document IDs are removed from the searchable document/chunk store
- prune is opt-in so partial connector syncs do not accidentally remove still-valid source records
- prune results are returned as `pruned_count` and `pruned_doc_ids`, and the completed sync audit event records the same fields
- sync writes `document_ingested` events for each document and a `source_sync_completed` audit event for the batch, including permission drift evidence
- this route is a connector contract and sample data-plane demonstration; real external connectors, background queues, retries, and malware scanning remain production upgrade work

### Ingestion Job Response Shape

`POST /api/ingestion/jobs` accepts:

- admin `user_id`
- `type`, currently `source_sync`
- required `idempotency_key`
- optional `retry_of_job_id`
- `payload`, which is the source sync request body

The local worker executes inline so the repository stays dependency-free, but it records production-style job lifecycle evidence:

- `job.id`
- `job.type`
- `job.status`: `queued`, `running`, `succeeded`, or `dead_lettered`
- `job.idempotency_key`
- `job.retry_of_job_id`
- `job.attempts`
- `job.payload_sha256`
- `job.input`
- `job.input.documents[].body_sha256`
- `job.result`
- `job.error`
- `idempotency_replayed`
- optional `result` when the source sync succeeds
- source sync job summaries include `prune_missing`, `pruned_count`, and `pruned_doc_ids` when pruning is enabled

Ingestion job contract:

- only admin users can submit or list ingestion jobs
- repeated `idempotency_key` values return the existing job with `idempotency_replayed` instead of executing the source sync again
- job input summaries include document IDs, titles, classifications, source MIME types, body character counts, and `body_sha256`, but never raw document bodies
- source sync validation failures become `dead_lettered` jobs with a sanitized error object instead of silently losing the failed work
- retry jobs must reference a previous `dead_lettered` job through `retry_of_job_id`; the retry supplies a fresh payload and idempotency key
- prune metadata is summarized in job results without exposing raw document bodies
- successful jobs write `ingestion_job_completed` audit events
- failed worker validation writes `ingestion_job_dead_lettered` audit events

### Connector Status Response Shape

`GET /api/connectors/status` returns an admin-only operator summary derived from the ingestion job ledger:

- `connectors`
- `connector_count`
- `job_window`
- `status_source`, currently `ingestion_jobs`

Each `connectors[]` item returns:

- `connector`
- `health`: `healthy`, `running`, `needs_attention`, `recovered`, or `unknown`
- `latest_job_id`
- `latest_job_status`
- `latest_job_type`
- `latest_cursor`
- `latest_updated_at`
- `document_count`
- `chunk_count`
- `acl_drift_count`
- `pruned_count`
- `success_count`
- `dead_letter_count`
- `job_count`
- `last_error_status`
- `last_error_retryable`

Connector status contract:

- only admin users can view connector status
- the response summarizes source sync jobs without returning raw document, issue, or pull request bodies
- `dead_letter_count` remains visible after a later successful retry, so recovered connectors still show prior failed work
- `latest_cursor`, document/chunk counts, ACL drift count, prune count, and job status are surfaced for operator review before trusting new source data
- the endpoint is a local operator contract; a production deployment would attach real connector registry records, queue state, schedule metadata, and alert links

### GitHub Connector Response Shape

`POST /api/connectors/github/sync` accepts:

- admin `user_id`
- `owner`
- `repo`
- `cursor`
- `mode`: `fixture` for deterministic local review or `live` for the GitHub REST API adapter
- optional `idempotency_key`
- fixture `records` containing issue or pull request fields such as `kind`, `number`, `title`, `body`, `state`, `html_url`, `updated_at`, `labels`, `user.login`, and `allowed_roles`

The route returns:

- `github.owner`
- `github.repo`
- `github.mode`
- `github.cursor`
- `github.record_count`
- `github.source_payload_sha256`
- `github.api_reference`
- `job`
- `idempotency_replayed`
- optional `result` when the ingestion job succeeds

GitHub connector contract:

- only admin users can sync GitHub repositories
- fixture mode is used by CI so contract checks do not depend on network access or GitHub rate limits
- live mode uses the GitHub REST issues and pull requests APIs and can use `GITHUB_CONNECTOR_TOKEN` or `GITHUB_TOKEN` for a scoped read token; token values are never returned, stored, or written to audit details
- issue and pull request records become source sync documents with `source_connector` set to `github`, source URLs pointing to GitHub issue/PR pages, and external IDs like `github:owner/repo:issue:number`
- `allowed_roles` are converted into a connector ACL snapshot so the normal fail-closed source ACL and permission filtering path still applies
- the connector submits a source sync ingestion job, so GitHub content inherits `idempotency_key` replay, sanitized job input summaries, `body_sha256`, completion audit, dead-letter behavior, and citation-ready chunks
- successful connector runs write `github_connector_synced` audit events with owner, repo, mode, cursor, record count, job ID, job status, and replay state, but never raw issue or pull request bodies

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
