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
- `/api/health` is the liveness endpoint. `/api/ready` is the readiness endpoint and verifies local storage, seed_data, eval_state, and scenario_snapshot availability before a service is treated as ready for review traffic.
- POST JSON request bodies are bounded before route handling by `local_http_limits.py`. The default limit is 1 MiB and can be adjusted for local verification with `FDE_MAX_JSON_BODY_BYTES`.
- Oversized JSON requests return `413` with `{"error": "Request body too large."}`. Non-object JSON payloads return `400` with `{"error": "JSON body must be an object."}`.
- The request-body boundary is verified by `python -B scripts/dev.py request-body-limits`.
- API routes pass through `local_request_governance.py` before route handling. Successful API responses include `X-Request-ID`, `X-RateLimit-Remaining`, `X-RateLimit-Window-Seconds`, and `X-RateLimit-Budget-Remaining` headers.
- Callers may provide a safe `X-Request-ID`; unsafe or missing values are replaced with a generated request id so user input is not blindly reflected.
- Local request-count and cost-budget limits can be adjusted with `FDE_RATE_LIMIT_REQUESTS_PER_WINDOW`, `FDE_RATE_LIMIT_BUDGET_PER_WINDOW`, and `FDE_RATE_LIMIT_WINDOW_SECONDS`.
- Requests over either local limit return `429` with `{"error": "Rate limit exceeded.", "request_id": "...", "retry_after_seconds": ...}` plus `Retry-After`.
- The request-governance boundary is verified by `python -B scripts/dev.py request-governance`.
- Core business POST routes propagate the governed `request_id` into the response, persisted trace, and linked audit event so a reviewer can correlate one HTTP request with durable evidence after the response has returned.
- Request correlation is verified by `python -B scripts/dev.py request-correlation`.

### Readiness Response Shape

`GET /api/ready` returns:

- `status`
- `app`
- `ready`
- `checks`

The `checks` object includes service-specific counts plus common `storage`, `seed_data`, `eval_state`, `scenario_snapshot`, and `scenario_files` fields.

## Secure Enterprise Knowledge Copilot

Source:

- `secure-enterprise-knowledge-copilot/src/copilot/api.py`
- Runtime gate: `scripts/check_api_contracts.py`

### Routes

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Service health and app name. |
| GET | `/api/ready` | Readiness check for storage, seed users, eval state, and scenario snapshot. |
| GET | `/api/users` | Demo users with `id`, `name`, `role`, `tenant_id`, `group_ids`, and `source_principals`. |
| GET | `/api/documents?user_id=alice` | Visible document metadata for the requester. Document `body` is never returned. |
| GET | `/api/traces?limit=25` | Recent trace records. |
| GET | `/api/audit?limit=50` | Recent audit events. |
| GET | `/api/ingestion/jobs?user_id=avery&limit=25` | Admin-only ingestion job ledger with sanitized input summaries, status, retry links, and dead-letter evidence. |
| GET | `/api/connectors/status?user_id=avery&limit=100` | Admin-only connector lifecycle summary derived from ingestion jobs, including health, cursors, counts, and dead-letter state. |
| GET | `/api/sources/quality?user_id=avery&limit=100` | Admin-only source quality inventory for indexed tenant documents, including parser quality schema coverage, source scan coverage, parser warnings, ACL metadata, lifecycle state, and per-source risk flags without raw bodies. |
| GET | `/api/connectors/source-bundle/catalog?user_id=avery&bundle=operations-handbook` | Admin-only source bundle manifest preview with ACL summaries, hashes, and file metadata but no raw source bodies. |
| GET | `/api/eval/latest` | Latest eval run record. |
| GET | `/api/scenario` | Fictional seed/eval snapshot for the browser-local scenario draft editor. |
| POST | `/api/auth/demo-token` | Local signed demo token issuer for exercising bearer-auth identity context without external SSO. |
| POST | `/api/query` | Permission-aware answer generation with citations or abstention. |
| POST | `/api/documents/ingest` | Admin-only local ingestion of searchable text, Markdown, CSV, HTML, or JSON content into the permission-aware document store. |
| POST | `/api/documents/parse-preview` | Admin-only dry-run parser preview for local source content or file-like payloads, returning parser contract, source hash, warnings, and chunk spans without indexing the source. |
| POST | `/api/sources/sync` | Admin-only connector-style batch source sync with external IDs, sync cursor, optional source ACL snapshot, permission drift evidence, parser normalization, chunking, and audit evidence. |
| POST | `/api/ingestion/jobs` | Admin-only local ingestion worker contract for source sync jobs with idempotency, inline execution, retry parent links, completion audit, and dead-letter audit. |
| POST | `/api/connectors/github/sync` | Admin-only GitHub read connector that normalizes issue/PR records into source sync jobs with source URLs, permission snapshots, idempotency, citation-ready chunks, and audit evidence. |
| POST | `/api/connectors/source-bundle/sync` | Admin-only allowlisted source bundle connector that reads checked-in synthetic files through manifest ACL snapshots and the ingestion job ledger. |
| POST | `/api/eval/run` | Run the project eval suite. |

### Local Auth Contract

The default browser demo can still pass `user_id` in the query string or JSON body so the local walkthrough stays simple. For production-shaped review, all three APIs also support a local signed bearer-token boundary implemented by `local_auth_tokens.py`:

- `POST /api/auth/demo-token` accepts `{"user_id": "riley"}` and returns `token_type`, `expires_in`, `auth_policy`, `token`, and `auth_context`
- `auth_policy` is `local_signed_demo_token_v1`
- callers can send `Authorization: Bearer <token>` on Project 1, Project 2, and Project 3 API requests
- bearer-auth identity is resolved before route behavior, so `/api/documents` without `user_id` returns the token subject's visible documents
- if a bearer token subject conflicts with a query/body `user_id`, the API returns `403` with `Request user_id does not match authenticated subject.`
- Project 2 and Project 3 use the same identity boundary for `POST /api/agent`, supervisor approval actions, action-outbox retry, and `POST /api/triage`; if the token subject conflicts with request identity fields, the API returns `403` with `Request identity does not match authenticated subject.`
- the local token secret defaults to a public demo value and can be overridden globally with `FDE_DEMO_AUTH_SECRET` or per service with `COPILOT_DEMO_AUTH_SECRET`, `OPS_AGENT_DEMO_AUTH_SECRET`, or `RELIABILITY_CONSOLE_DEMO_AUTH_SECRET`; it is not a production SSO replacement

Runtime contracts verify local token issuance, bearer-auth group document visibility, bearer-auth retrieval for group-scoped evidence, Project 2 bearer-auth agent routing and supervisor approval, Project 3 bearer-auth triage, and subject-mismatch rejection.

### Query Response Shape

`POST /api/query` returns:

- `trace_id`
- `request_id`
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
- `retrieval_profile.source_lifecycle_policy` is `active_sources_only`; superseded, deprecated, or deleted sources are retained for audit history but filtered before scoring and answer assembly
- `retrieval_profile.stale_filtered_count` records how many visible stale chunks were removed by source lifecycle filtering for that query
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
- optional `source_lifecycle_state` (`active`, `superseded`, `deprecated`, or `deleted`; defaults to `active`)
- optional `superseded_by`

The route returns:

- `document`
- `chunk_count`
- `ingestion.actor_user_id`
- `ingestion.replace`
- `ingestion.source_hash`
- `ingestion.source_scan`
- `ingestion.supported_mime_types`
- `ingestion.parser.name`
- `ingestion.parser.contract_version`
- `ingestion.parser.quality_schema_version`
- `ingestion.parser.normalized_characters`
- `ingestion.parser.metadata`
- `ingestion.parser.quality`
- `ingestion.parser.warnings`
- `ingestion.source.file`
- `ingestion.source.connector`
- `ingestion.source.external_id`
- `ingestion.source.acl_source`
- `ingestion.source.allowed_groups`
- `ingestion.source.source_acl_principals`
- `ingestion.source.sync_cursor`
- `ingestion.source.source_lifecycle_state`
- `ingestion.source.superseded_by`
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
- parser quality metadata is returned through `ingestion.parser.quality` and embedded in `ingestion.parser.metadata.quality`; it records `parser.quality.schema_version`, parser name, raw and normalized character counts, line counts, non-empty line counts, section counts, table-like line counts, and format details such as Markdown heading/link/code-block counts, CSV row/column/header/ragged-row counts, HTML tag/script-style counts, and JSON root/field/depth counts
- source scan metadata is returned through `ingestion.source_scan`; it records `source_scan.schema_version`, local scan policy, scan status, severity, finding counts, finding categories, `review_required`, and `source_scan.raw_matches_returned=false`
- ingestion records chunk source spans over parser `normalized_text`; `chunk_source_span_unit` is `normalized_text` and `chunk_source_span_count` matches `chunk_count`
- ingestion creates local deterministic chunk embeddings with model `local-hashing-v1` and dimension `1536`; raw vectors are stored for retrieval/indexing but not returned by the public API
- CSV parser metadata includes `row_count`, `column_count`, and `has_header`; parser warnings are surfaced as `parser_warnings`
- ingestion writes a `document_ingested` audit event with `source_hash`, `chunk_count`, `source_mime`, `source_file`, `parser_warnings`, source span metadata, embedding metadata, role metadata, and source-group ACL metadata

### Parser Preview Response Shape

`POST /api/documents/parse-preview` accepts the same admin `user_id` and `document` source payload as local ingestion, but it does not write the document, chunks, embeddings, traces, or audit records.

The route returns:

- `preview.actor_user_id`
- `preview.title`
- `preview.source_hash`
- `preview.source_mime`
- `preview.source_file`
- `preview.source_scan`
- `preview.parser.contract_version`
- `preview.parser.quality_schema_version`
- `preview.parser.name`
- `preview.parser.normalized_characters`
- `preview.parser.metadata`
- `preview.parser.quality`
- `preview.parser.warnings`
- `preview.parser.warning_count`
- `preview.validation_warnings`
- `preview.would_index`
- `preview.chunk_count`
- `preview.chunk_source_span_unit`
- `preview.chunks[].chunk_index`
- `preview.chunks[].character_count`
- `preview.chunks[].source_span`
- `preview.chunks[].text_excerpt`
- `preview.raw_body_returned`
- `supported_mime_types`

Parser preview contract:

- only admin users can preview parsing
- the same MIME detection, file decoding, parser normalization, and chunk-span code path is used before ingestion
- `preview.parser.contract_version` is `source_parser_contract_v1`
- `preview.parser.quality_schema_version` and `preview.parser.quality.schema_version` are `source_parser_quality_v1`
- `preview.source_scan.schema_version` is `source_scan_v1`; `preview.source_scan.raw_matches_returned` is `false`
- `preview.chunk_source_span_unit` is `normalized_text`
- `preview.raw_body_returned` is `false`; the response includes short chunk excerpts for operator review, not the full raw source body
- `preview.would_index` is `false` when validation warnings such as `searchable_body_too_short` would prevent ingestion

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
- `sync.source_scan_review_required_count`
- `sync.source_scan_finding_counts`
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
- `documents[].source_lifecycle_state`
- `documents[].superseded_by`

Source sync contract:

- only admin users can sync connector sources
- synced documents are normalized through the same parser, chunking, embedding, permission, and body-hiding path as local ingestion
- synced documents are scanned through `source_scan_v1`; batch source scan review counts and finding categories are summarized without returning raw matches
- the API accepts at most ten documents per local sync request so demo state remains reviewable
- connector `name`, external document ID, ACL source, ACL snapshot version, source permission ID, allowed-role source, allowed groups, source ACL principals, sync cursor, and source lifecycle metadata are persisted on documents and chunks
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

`GET /api/connectors/status` returns an admin-only operator summary derived from the ingestion job ledger plus the current indexed document inventory:

- `connectors`
- `connector_count`
- `job_window`
- `status_source`, currently `ingestion_jobs+indexed_documents`

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
- `indexed_document_count`
- `active_document_count`
- `filtered_document_count`
- `index_matches_latest_job`
- `index_health`: `indexed`, `parser_warnings`, or `empty`
- `source_lifecycle_counts`
- `classification_counts`
- `parser_warning_count`
- `parser_warning_document_count`
- `parser_warnings`
- `latest_indexed_updated_at`
- `source_mime_types`
- `acl_sources`
- `allowed_roles_sources`
- `source_acl_versions`
- `document_ids`

Connector status contract:

- only admin users can view connector status
- the response summarizes source sync jobs without returning raw document, issue, or pull request bodies
- `dead_letter_count` remains visible after a later successful retry, so recovered connectors still show prior failed work
- `latest_cursor`, document/chunk counts, ACL drift count, prune count, and job status are surfaced for operator review before trusting new source data
- indexed document counts, active/filtered lifecycle counts, parser warning totals, ACL sources, and source ACL versions are surfaced so operators can compare the latest connector run against the searchable index
- the endpoint is a local operator contract; a production deployment would attach real connector registry records, queue state, schedule metadata, and alert links

### Source Quality Response Shape

`GET /api/sources/quality` returns an admin-only source quality inventory across the current tenant. It is separate from connector status: connector status summarizes sync jobs, while source quality summarizes the indexed source inventory that operators review before trusting retrieval.

The route returns:

- `source_quality.schema_version`, currently `source_quality_report_v1`
- `source_quality.actor_user_id`
- `source_quality.tenant_id`
- `source_quality.document_count`
- `source_quality.active_document_count`
- `source_quality.filtered_document_count`
- `source_quality.attention_required_count`
- `source_quality.parser_warning_count`
- `source_quality.parser_warning_document_count`
- `source_quality.parser_quality_schema_counts`
- `source_quality.source_scan_schema_counts`
- `source_quality.source_scan_review_required_count`
- `source_quality.source_scan_finding_counts`
- `source_quality.source_mime_counts`
- `source_quality.connector_counts`
- `source_quality.lifecycle_counts`
- `source_quality.classification_counts`
- `source_quality.acl_snapshot_coverage_count`
- `source_quality.raw_bodies_returned`
- `source_quality.documents`
- `source_quality.documents[].risk_flags`
- `source_quality.documents[].source_scan_status`

Each `source_quality.documents[]` item returns:

- `id`
- `title`
- `source_connector`
- `source_mime`
- `classification`
- `source_lifecycle_state`
- `parser_name`
- `parser_quality_schema`
- `normalized_characters`
- `normalized_non_empty_line_count`
- `section_count`
- `table_like_line_count`
- `parser_warning_count`
- `parser_warnings`
- `source_scan_schema`
- `source_scan_status`
- `source_scan_severity`
- `source_scan_review_required`
- `source_scan_finding_categories`
- `acl_source`
- `allowed_roles_source`
- `allowed_groups`
- `source_acl_version`
- `source_acl_principal_count`
- `source_hash_prefix`
- `updated_at`
- `attention_required`
- `risk_flags`

Source quality contract:

- only admin users can view source quality
- raw document bodies, file contents, issue bodies, and pull request bodies are never returned
- every returned document carries `parser_quality_schema`; missing or unexpected parser quality metadata is surfaced through `risk_flags`
- every returned document carries `source_scan_schema`; missing scan metadata or review-required scan findings are surfaced through `risk_flags`
- checked-in Project 1 seed documents are parsed during `storage.seed()` so default JSON runtime state and generated PostgreSQL seed rows carry parser quality metadata before retrieval starts
- checked-in Project 1 seed documents, admin-ingested documents, source-sync documents, and generated PostgreSQL seed rows carry `source_scan_v1` metadata before retrieval starts
- parser warnings, source scan review signals, non-active lifecycle state, missing source hashes, missing connector ACL snapshot versions, and empty normalized text are visible as operator attention signals
- production deployments would attach source-owner routing, alert IDs, ingestion worker links, malware-scan state, DLP findings, and parser-worker retry history to the same operator surface

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

### Source Bundle Connector Response Shape

`GET /api/connectors/source-bundle/catalog` accepts:

- admin `user_id`
- optional `bundle`, currently an allowlisted checked-in synthetic bundle such as `operations-handbook`
- optional `cursor`
- optional `prune_missing`

The route returns:

- `catalog.catalog_version`, currently `source_bundle_catalog_v1`
- `catalog.root`
- `catalog.bundle_count`
- `catalog.raw_bodies_returned`, which must be `false`
- `catalog.bundles`
- `catalog.bundles[].bundle`
- `catalog.bundles[].connector`
- `catalog.bundles[].cursor`
- `catalog.bundles[].document_count`
- `catalog.bundles[].prune_missing`
- `catalog.bundles[].manifest`
- `catalog.bundles[].manifest_sha256`
- `catalog.bundles[].source_payload_sha256`
- `catalog.bundles[].acl_source`
- `catalog.bundles[].acl_snapshot_version`
- `catalog.bundles[].documents`
- `catalog.bundles[].documents[].id`
- `catalog.bundles[].documents[].external_id`
- `catalog.bundles[].documents[].title`
- `catalog.bundles[].documents[].path`
- `catalog.bundles[].documents[].classification`
- `catalog.bundles[].documents[].source_mime`
- `catalog.bundles[].documents[].source_url`
- `catalog.bundles[].documents[].file_size_bytes`
- `catalog.bundles[].documents[].body_sha256`
- `catalog.bundles[].documents[].allowed_roles`
- `catalog.bundles[].documents[].allowed_groups`
- `catalog.bundles[].documents[].permission_id`
- `catalog.bundles[].documents[].principal_count`

Source bundle catalog contract:

- only admin users can preview source bundles
- bundle names are validated with the same strict slug pattern used by sync
- manifests and referenced files are validated before returning a preview
- the preview returns manifest, source payload, file, body, and ACL hashes/counts for operator review
- raw source bodies are never returned in the catalog response

`POST /api/connectors/source-bundle/sync` accepts:

- admin `user_id`
- `bundle`, currently an allowlisted checked-in synthetic bundle such as `operations-handbook`
- optional `cursor`
- optional `idempotency_key`
- optional `prune_missing`

The route returns:

- `source_bundle.bundle`
- `source_bundle.connector`
- `source_bundle.cursor`
- `source_bundle.document_count`
- `source_bundle.synced_document_count`
- `source_bundle.manifest`
- `source_bundle.manifest_sha256`
- `source_bundle.source_payload_sha256`
- `job`
- `idempotency_replayed`
- optional `result` when the ingestion job succeeds

Source bundle connector contract:

- only admin users can sync source bundles
- bundle names are allowlisted by a strict slug pattern and cannot contain path traversal characters
- source bundle documents are read only from `secure-enterprise-knowledge-copilot/data/source_bundles/<bundle>` and must be UTF-8 text under the size limit
- the manifest maps each checked-in synthetic file to source sync documents, ACL snapshot records, source URLs, parser MIME types, and source lifecycle metadata
- source bundle content inherits the same parser, chunking, embedding, permission filtering, idempotency, prune, audit, and citation path as other connector data
- successful connector runs write `source_bundle_synced` audit events with bundle, connector, cursor, document count, job ID, job status, replay state, and payload hash; raw source bodies are not returned in connector status or job summaries

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
| GET | `/api/ready` | Readiness check for storage, seed cases, approval state, eval state, and scenario snapshot. |
| GET | `/api/users` | Demo users with `id`, `name`, and `role`. |
| GET | `/api/cases` | Demo operational cases. |
| GET | `/api/approvals` | Approval queue state. |
| GET | `/api/tool-registry` | Governed tool registry with risk, approval, and dry-run policy metadata. |
| GET | `/api/action-outbox?limit=25` | Sanitized side-effect dispatch queue created by approval requests and drained by supervisor approval. |
| GET | `/api/action-runs?limit=25` | Side-effect execution receipts written after supervisor approval. |
| GET | `/api/workflow-runs?limit=25` | Sanitized agent workflow checkpoints linking traces, approvals, outbox dispatch, retries, and execution receipts. |
| GET | `/api/traces?limit=25` | Recent trace records. |
| GET | `/api/audit?limit=50` | Recent audit events. |
| GET | `/api/eval/latest` | Latest eval run record. |
| GET | `/api/scenario` | Fictional seed/eval snapshot for the browser-local scenario draft editor. |
| POST | `/api/auth/demo-token` | Local signed demo token issuer for exercising bearer-auth identity context without external SSO. |
| POST | `/api/agent` | Process an investigator/supervisor workflow message. |
| POST | `/api/approval/approve` | Supervisor-only approval execution. |
| POST | `/api/approval/reject` | Supervisor-only approval rejection without executing side effects. |
| POST | `/api/approval/expire` | Supervisor-only approval expiry without executing side effects. |
| POST | `/api/action-outbox/retry` | Supervisor-only retry for retryable side-effect dispatch failures. |
| POST | `/api/eval/run` | Reset state and run the project eval suite. |

### Tool Registry Response Shape

`GET /api/tool-registry` returns:

- `schema_version`
- `tools`

Registry contract:

- `schema_version` is `tool_registry_v1`
- each `tool_registry` item includes `name`, `category`, `required_role`, `approval_required`, `dry_run_required`, `side_effect`, `credential_scope`, `risk_level`, and `description`
- side-effecting tools are declared in the registry before runtime use
- approval-gated tools can be inspected by the browser before any side effect is executed

### Agent Response Shape

`POST /api/agent` returns:

- `trace_id`
- `request_id`
- `intent`
- `response`
- `tool_calls`
- `approvals`
- `blocked_actions`
- `cited_policies`
- `outputs`
- `case`
- `model_router`
- `latency_ms`
- `workflow_run`

Security contract:

- investigator side effects create approval requests instead of executing directly
- non-supervisors receive `403` when approving actions
- approval requests include `approval_policy=approval_policy_v1`, `expires_at`, `approval_expires_at`, `owner_role`, `review_status`, `payload_sha256`, `payload_summary`, `decision_reason_summary`, `dry_run_preview`, and `raw_decision_reason_returned=false`
- `dry_run_preview` uses `dry_run_preview_v1` and shows the intended action without returning raw seller notice bodies or raw escalation reasons
- approval requests enqueue an `action_outbox` item with payload hashes, dry-run previews, review metadata, and summaries, not raw seller notice bodies
- supervisor approval is idempotent, drains the outbox item, and returns both an `outbox_item` and `execution` receipt after the side effect is applied
- supervisor rejection returns `approval_rejected`, marks the approval and outbox item as `review_status=rejected`, and does not execute a side effect
- supervisor expiry returns `approval_expired`, marks the approval and outbox item as `review_status=expired`, and does not execute a side effect
- supervisor approval can also leave an outbox item in `retryable_failure` or `dead_lettered` when dispatch fails before the side effect is applied
- retrying a `retryable_failure` outbox item uses the same idempotency key, never creates duplicate side effects, and returns the recovered `execution` receipt on success
- action run receipts expose `payload_sha256`, output references, actor IDs, action type, status, and result without returning raw seller notice bodies
- agent responses include a `workflow_run` checkpoint with `schema_version=workflow_run_v1`, `trace_id`, `status`, `stage`, approval/outbox/action-run references, a message hash, and `raw_message_returned=false`
- bypass instructions create blocked-action evidence instead of side effects
- `model_router` reports the actual routing source for the intent classification path, not just whether OpenAI mode was configured

### Workflow Run Response Shape

`GET /api/workflow-runs` returns:

- `workflow_runs`

Each `workflow_runs[]` item returns:

- `id`
- `schema_version`
- `created_at`
- `updated_at`
- `user_id`
- `trace_id`
- `case_id`
- `intent`
- `model_router`
- `status`
- `stage`
- `message_sha256`
- `message_characters`
- `raw_message_returned`
- `tool_call_count`
- `approval_ids`
- `outbox_ids`
- `action_run_ids`
- `blocked_action_count`
- `cited_policy_ids`
- `waiting_on`
- `retryable_outbox_ids`
- `dead_lettered_outbox_ids`
- `last_result`

Workflow run contract:

- workflow runs are checkpoints for the agent orchestration layer, not the side-effect executor itself
- raw user messages, raw seller notice bodies, and raw escalation reasons are not returned through workflow runs
- an approval-gated side effect starts as `waiting_for_approval` at stage `approval_requested`
- successful supervisor dispatch updates the same workflow run to `succeeded` at stage `side_effect_executed`
- pre-side-effect transient dispatch failure updates it to `dispatch_retryable_failure` at stage `waiting_for_retry`
- recovered retry clears `retryable_outbox_ids` and returns the run to `succeeded`
- repeated pre-side-effect failure updates it to `dispatch_dead_lettered` at stage `dead_lettered`
- rejected approvals update it to `approval_rejected`
- expired approvals update it to `approval_expired`

### Approval Response Shape

`GET /api/approvals` returns:

- `approvals`

Each `approvals[]` item returns:

- `id`
- `created_at`
- `updated_at`
- `expires_at`
- `approval_policy`
- `tool_registry_version`
- `requested_by`
- `owner_role`
- `case_id`
- `action_type`
- `status`
- `review_status`
- `payload_sha256`
- `payload_summary`
- `decision_reason_summary`
- `dry_run_preview`
- `raw_payload_returned`
- `raw_decision_reason_returned`
- `approved_by`
- `approved_at`
- `rejected_by`
- `rejected_at`
- `expired_by`
- `expired_at`

`POST /api/approval/reject` accepts:

- `approval_id`
- `reviewer_id`
- `reason`

It returns:

- `approval`
- `result`
- `execution`
- `outbox_item`

`POST /api/approval/expire` accepts:

- `approval_id`
- `operator_id`
- `reason`

It returns:

- `approval`
- `result`
- `execution`
- `outbox_item`

### Action Outbox Response Shape

`GET /api/action-outbox` returns:

- `action_outbox`

Each `action_outbox[]` item returns:

- `id`
- `created_at`
- `updated_at`
- `approval_id`
- `requested_by`
- `action_type`
- `status`
- `result`
- `approval_policy`
- `tool_registry_version`
- `approval_expires_at`
- `review_status`
- `idempotency_key`
- `approval_idempotency_key`
- `payload_sha256`
- `payload_summary`
- `dry_run_preview`
- `attempt_count`
- `next_attempt_at`
- `last_error`
- `dead_lettered_at`
- `dead_letter_reason`
- `lease_id`
- `leased_by`
- `lease_acquired_at`
- `lease_expires_at`
- `lease_released_at`
- `lease_count`
- `last_lease_id`
- `last_leased_by`
- `approved_by`
- `approved_at`
- `rejected_by`
- `rejected_at`
- `expired_by`
- `expired_at`
- `execution_id`
- `output_refs`
- `raw_payload_returned`

Outbox `status` values:

- `awaiting_approval`
- `dispatching`
- `succeeded`
- `approval_rejected`
- `approval_expired`
- `retryable_failure`
- `dead_lettered`

`POST /api/action-outbox/retry` accepts:

- `outbox_id`
- `operator_id`

It returns:

- `approval`
- `result`
- `execution`
- `outbox_item`

Retry contract:

- only supervisors can retry action outbox dispatch
- retryable failures keep the original `approval_id`, `payload_sha256`, and idempotency key
- every dispatch attempt records a local worker lease with `last_lease_id`, `last_leased_by`, `lease_count`, and `lease_released_at`
- dead-lettered items remain visible in the outbox ledger and are not retried by default
- retry responses do not expose raw seller notice bodies

The action outbox contract:

- new approval requests start as `awaiting_approval`
- supervisor approval moves the item through dispatch and records `succeeded` after the action receipt is written
- supervisor rejection and expiry close the item as `approval_rejected` or `approval_expired` without execution
- repeated approval calls return the existing execution rather than creating a second side effect
- outbox records expose stable hashes, action type, approval ID, status, attempts, and output refs without returning raw notice bodies

### Action Run Response Shape

`GET /api/action-runs` returns:

- `action_runs`

Each `action_runs[]` item returns:

- `id`
- `created_at`
- `executed_at`
- `approval_id`
- `requested_by`
- `executed_by`
- `action_type`
- `status`
- `result`
- `idempotency_key`
- `approval_idempotency_key`
- `payload_sha256`
- `payload_summary`
- `approval_policy`
- `tool_registry_version`
- `dry_run_preview`
- `raw_payload_returned`
- `output_refs`

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
| GET | `/api/ready` | Readiness check for storage, seed releases/incidents/runbooks, eval state, and scenario snapshot. |
| GET | `/api/users` | Demo users with `id`, `name`, and `role`. |
| GET | `/api/releases` | Release records and canary rollout state. |
| GET | `/api/incidents` | Release incident records with severity, category, signals, linked eval cases, and runbooks. |
| GET | `/api/eval-runs` | Release eval run history. |
| GET | `/api/runbooks` | Remediation runbooks referenced by incidents. |
| GET | `/api/traces?limit=25` | Recent triage trace records. |
| GET | `/api/audit?limit=50` | Recent audit events. |
| GET | `/api/eval/latest` | Latest release reliability eval run record. |
| GET | `/api/scenario` | Fictional seed/eval snapshot for the browser-local scenario draft editor. |
| POST | `/api/auth/demo-token` | Local signed demo token issuer for exercising bearer-auth identity context without external SSO. |
| POST | `/api/triage` | Triage an incident against a release and produce rollout decision evidence. |
| POST | `/api/eval/run` | Reset state and run the project eval suite. |

### Triage Response Shape

`POST /api/triage` returns:

- `trace_id`
- `request_id`
- `release`
- `incident`
- `decision`
- `failed_evals`
- `remediation_steps`
- `evidence`
- `latency_ms`

The `decision` object includes:

- `trace_id`
- `request_id`
- `user_id`
- `release_id`
- `incident_id`
- `severity`
- `recommendation`
- `release_blocked`
- `root_cause`
- `confidence`
- `latency_ms`

Release reliability contract:

- unsafe rollout incidents return `block_release`
- latency-only incidents can return `monitor`
- failed eval cases are returned as `failed_evals`
- evidence includes linked eval case IDs, runbook IDs, and incident signals
- trace and audit records are created for triage decisions, and latency evidence is present in both the API response and trace result

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
