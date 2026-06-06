# Production Upgrade Notes

## Why The Current Version Is Structured This Way

The local repository uses dependency-free Python and static frontend assets so the demos run reliably on the current machine. The core FDE behavior is implemented now:

- permissions before retrieval answer generation
- citations and abstention
- prompt-injection handling
- tool calling
- side-effect approval gates
- audit and trace records
- golden eval gates

Production hardening should upgrade infrastructure without changing these core control boundaries.

## OpenAI Integration

Optional OpenAI Responses API gateways are implemented:

- Project 1: `COPILOT_MODEL_PROVIDER=openai`
- Project 2: `OPS_AGENT_MODEL_ROUTER=openai`

Runtime controls:

- `OPENAI_MODEL=gpt-5.2`
- `OPENAI_REASONING_EFFORT=none|low|medium|high|xhigh`
- `OPENAI_TEXT_VERBOSITY=low|medium|high`

See `docs/model_runtime_configuration.md` for the current model selection rationale.

References:

- Responses API: https://platform.openai.com/docs/api-reference/responses
- Structured Outputs: https://platform.openai.com/docs/guides/structured-outputs?api-mode=responses
- Agents: https://platform.openai.com/docs/guides/agents
- Agent Evals: https://platform.openai.com/docs/guides/agent-evals
- Trace Grading: https://platform.openai.com/docs/guides/trace-grading

The model should not enforce security by itself.

Project 1 still performs:

- admin-only ingestion before document chunks are added to searchable state
- tenant and role filtering before generation
- unsafe retrieved-content removal before generation
- source lifecycle filtering before retrieval scoring so superseded, deprecated, or deleted sources stay auditable but cannot answer current questions
- citation and abstention decisions in application logic
- normalized-text source spans attached to retrieved chunks, cited chunks, and sentence-level answer evidence

Project 2 still performs:

- tool permission checks in application logic
- approval gate enforcement in application logic
- side-effect execution only after supervisor approval

## Recommended Production Architecture

```text
Next.js frontend
  -> API gateway
  -> FastAPI services
  -> PostgreSQL
  -> pgvector / search backend
  -> Redis worker queue
  -> OpenAI Responses API / Agents SDK
  -> OpenTelemetry trace backend
  -> CI eval gate
```

## Project 1 Upgrade Path

Current production-path artifacts:

- `infra/postgres/migrations/001_core.sql`
- `infra/postgres/migrations/002_project1_denied_evidence_count.sql`
- `infra/postgres/migrations/003_project1_group_acl.sql`
- `infra/postgres/seeds/001_project1_demo.sql`
- `docker-compose.postgres.yml`
- `secure-enterprise-knowledge-copilot/src/copilot/embeddings.py`
- `secure-enterprise-knowledge-copilot/src/copilot/ingestion.py`
- `secure-enterprise-knowledge-copilot/src/copilot/source_files.py`
- `secure-enterprise-knowledge-copilot/src/copilot/source_lifecycle.py`
- `secure-enterprise-knowledge-copilot/web/js/ingestion.js`
- `secure-enterprise-knowledge-copilot/src/copilot/postgres_repositories.py`
- `python -B scripts/dev.py postgres-migrations`
- `python -B scripts/dev.py postgres-compose`
- `python -B scripts/dev.py postgres-runtime`
- `python -B scripts/dev.py postgres-seed`

Project 1 runtime switch:

- `COPILOT_REPOSITORY=json` keeps the verified local JSON path.
- `COPILOT_REPOSITORY=postgres` switches `connect_repository()` to `PostgresRepositorySession`.
- `COPILOT_POSTGRES_DSN` points the optional runtime at a PostgreSQL/pgvector deployment that has applied `infra/postgres/migrations/001_core.sql` and `infra/postgres/seeds/001_project1_demo.sql`.
- `COPILOT_POSTGRES_POOL=1` opts into a dynamically loaded `psycopg_pool` connection pool lease when the deployment environment provides that package.
- `python -B scripts/dev.py postgres-runtime` verifies the offline runtime switch contract; `python -B scripts/check_project1_postgres_runtime.py --live` verifies a real seeded database when `COPILOT_POSTGRES_DSN` is available.
- `python -B scripts/dev.py postgres-compose` verifies the optional local pgvector compose file, digest-pinned image, init order, seed wiring, healthcheck, and local role separation.
- `docker-compose.postgres.yml` runs Project 1 local production-mode Postgres on host port `55432`; its public local-only app role is `fde_app` with demo password `fde_app_demo_password`.
- `project1_denied_relevant_chunk_count` preserves denied-evidence audit counts under RLS without exposing unauthorized document IDs, titles, or chunk bodies; the group ACL migration also counts documents denied by source-group membership rather than role alone.
- `local-hashing-v1` provides a deterministic 1536-dimensional embedding boundary for seed data and admin ingestion so pgvector storage and vector score reporting are now concrete, while a production embedding model remains a later replacement.
- `PostgresKnowledgeRepository.list_retrieval_candidates` adds `postgres_hybrid_sql_v1`, a SQL-backed keyword/vector candidate selection path that applies tenant, role, and source-group filters before `websearch_to_tsquery` and pgvector nearest-neighbor retrieval.
- `local-evidence-reranker-v1` provides a deterministic reranker boundary with feature-level rerank scores so production rerankers can be added without changing the permission or citation invariants.
- Project 1 chunk metadata now carries normalized-text `source_span` values through JSON seed state, admin ingestion, citation output, traces, and the optional PostgreSQL adapter.
- Project 1 documents and chunks now carry `source_lifecycle_state` and `superseded_by` metadata. Retrieval uses the `active_sources_only` lifecycle policy, records `stale_filtered_count`, and keeps superseded/deprecated/deleted sources out of scoring and answer assembly while retaining them for audit history.
- `scripts/export_traces_otel.py --send-otlp-http` adds an optional OTLP/HTTP JSON collector handoff path, while `scripts/check_otel_collector_handoff.py` verifies the POST behavior with a local collector stub so hosted observability remains opt-in.
- `scripts/trace_redaction.py` adds `public_trace_export_redaction_v1`, a shared export-boundary redaction policy for OTLP payloads and trace-to-eval candidates. `python -B scripts/dev.py trace-redaction` verifies that common email, phone, secret-like, private ID, and local path markers are removed before generated observability artifacts leave local runtime state.
- `scripts/export_trace_eval_candidates.py` adds a local trace-to-eval candidate workflow so permission abstentions, prompt-injection refusals, approval gates, bypass refusals, release blocks, and monitor-only eval signals can be reviewed before promotion into checked-in golden evals. Candidate artifacts include owner roles, allowed dispositions, promotion targets, redaction policy metadata, and regression schedules so review remains explicit.
- `POST /api/documents/ingest` now accepts either direct text/Markdown/CSV/HTML/JSON body content or a UTF-8 file-like JSON payload with `document.file.filename` and `document.file.content_base64`. The file boundary records safe `source_file` metadata, rejects path-like filenames and unsupported MIME types, infers supported MIME types from filenames when needed, and routes decoded content through the same parser, chunking, embedding, citation, audit, and retrieval path.
- `POST /api/sources/sync` adds an admin-only connector-style source sync contract. It persists connector name, external document ID, ACL source, ACL snapshot version, source permission ID, allowed-role source, allowed source groups, source ACL principals, sync cursor metadata, and source lifecycle metadata on documents and chunks. It reuses parser/chunking/embedding boundaries, fails closed when a provided ACL snapshot lacks a document permission record, supports opt-in `prune_missing` for full-snapshot removal of stale connector documents, writes per-document `document_ingested` events, and writes a batch `source_sync_completed` audit event with `acl_drift_count`, `pruned_count`, and affected document IDs. The frontend includes a sample connector sync button so reviewers can exercise the data-plane contract without external accounts.
- `POST /api/ingestion/jobs` and `GET /api/ingestion/jobs` add a local ingestion worker contract. The local demo still executes inline, but it records job lifecycle state, `idempotency_key` replay, sanitized input summaries with `body_sha256`, `dead_lettered` validation failures, retry parent links, `ingestion_job_completed`, and `ingestion_job_dead_lettered` audit evidence.
- `POST /api/connectors/github/sync` adds the first read connector boundary. Fixture mode keeps CI deterministic while live mode can call the GitHub REST issues and pull requests APIs with an optional scoped `GITHUB_CONNECTOR_TOKEN`. Issue and PR records are normalized into source sync ingestion jobs with GitHub source URLs, external IDs, connector ACL snapshots, idempotency replay, citation-ready chunks, and `github_connector_synced` audit evidence without returning or auditing raw issue bodies.
- `GET /api/connectors/status` adds an admin-only operator status boundary derived from ingestion jobs. It reports connector health, latest cursor, document/chunk counts, ACL drift, prune counts, prior dead letters, and recovered status without exposing raw source bodies.

Next steps:

1. Run `python -B scripts/check_project1_postgres_runtime.py --live` on a Docker-enabled machine after starting `docker-compose.postgres.yml`; verify Alice finance denial, Morgan finance access, SQL hybrid candidate retrieval, and denied-evidence count behavior.
2. Extend the current admin-only text/file-like ingestion, ACL-snapshot source sync, source-group permission checks, and GitHub read connector contracts into multipart uploads, broader external connectors, source user/group membership sync, connector checkpoint recovery, and live deletion/prune verification against external source APIs.
3. Move the local inline ingestion job contract behind a real background parser pipeline with external worker processes, durable queue storage, retry scheduling, and sync checkpoint recovery.
4. Replace the deterministic local hashing embedding with a production embedding model.
5. Add retrieval metrics for SQL candidate recall, lexical/vector balance, rerank quality, broader citation span accuracy, larger stale/conflict fixtures, and source lifecycle drift over time.
6. Replace the deterministic reranker with a production reranker provider behind the existing boundary.
7. Connect trace-to-eval candidate review metadata to a checked-in reviewed-dataset ledger and nightly regression scheduling automation.
8. Send OTLP traces to a real collector or hosted backend in a documented target environment, preserving the local collector-stub check as the default CI proof.
9. Add PostgreSQL row-level security tests against a running database.
10. Add eval cases from real failure logs.

## Project 2 Upgrade Path

1. Replace deterministic routing with Responses API or Agents SDK planning.
2. Keep side-effect tools behind deterministic approval middleware.
3. Add external connectors for CRM/ticketing/email/calendar.
4. Add workflow state machine.
5. Add idempotency and retry policies per connector.
6. Add trace grading for routing, tool choice, and approval compliance.

## Deployment Decision Gate

Do not deploy a change unless:

- health check passes
- all evals pass or approved exceptions are documented
- unsafe leak/direct-side-effect failures remain zero
- trace/audit schema compatibility is preserved
- demo script still works end to end
