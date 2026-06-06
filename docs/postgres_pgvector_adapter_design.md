# PostgreSQL And pgvector Adapter Design

This design note describes how to replace the local JSON stores with PostgreSQL and pgvector without changing the core security principle of the repository:

> The model is not the security boundary. Permissions, side effects, audit, traces, and eval expectations stay in application code and database policy.

Related architecture decisions:

- [ADR 0002: The Model Is Not The Security Boundary](adr_0002_model_is_not_security_boundary.md)
- [ADR 0003: Eval State Isolated From Demo State](adr_0003_eval_state_isolated_from_demo_state.md)

## Goals

- Persist documents, cases, approvals, traces, audit events, eval runs, and generated artifacts in a production database.
- Add hybrid keyword/vector retrieval for the knowledge copilot.
- Enforce tenant and role access before retrieval results reach the model.
- Keep eval state isolated from live demo or production state.
- Make schema changes reviewable and reversible through migrations.
- Preserve local deterministic demos as the default path.

## Non-Goals

- Do not make PostgreSQL required for the zero-dependency demo.
- Do not move authorization checks into prompts.
- Do not let vector search bypass tenant, role, or document-level filters.
- Do not make eval runners write into production tables.

## Target Architecture

```text
HTTP/API layer
  -> application service
  -> authorization context
  -> repository interfaces
  -> PostgreSQL transaction
  -> row-level policies, indexes, audit triggers
  -> model gateway only after authorized evidence/actions are selected
```

Projects with persistent application state should use repository interfaces so local JSON stores and PostgreSQL adapters can coexist:

- `DocumentRepository`
- `TraceRepository`
- `AuditRepository`
- `EvalRepository`
- `CaseRepository`
- `ApprovalRepository`
- `ToolActionRepository`

Project 1 now has the first local version of this boundary in `secure-enterprise-knowledge-copilot/src/copilot/repositories.py`: application modules depend on `KnowledgeRepository` and `JsonKnowledgeRepository` while the local JSON mechanics stay in `storage.py`. It also has an optional production-path adapter contract in `secure-enterprise-knowledge-copilot/src/copilot/postgres_repositories.py`: `PostgresKnowledgeRepository` maps the same application-facing methods to tenant-scoped PostgreSQL tables for users, documents, chunks, traces, audit events, and eval runs. `COPILOT_REPOSITORY=postgres` switches `connect_repository()` to the Postgres session, `COPILOT_POSTGRES_DSN` supplies the deployment DSN, and `COPILOT_POSTGRES_POOL=1` opts into a dynamically loaded `psycopg_pool` lease when the deployment provides it. The default demo still uses `COPILOT_REPOSITORY=json` and does not require PostgreSQL.

Project 1 also now has a local deterministic embedding boundary in `secure-enterprise-knowledge-copilot/src/copilot/embeddings.py`. The `local-hashing-v1` model emits 1536-dimensional vectors so seed data, admin-ingested chunks, retrieval scoring, and the PostgreSQL adapter share one concrete vector contract. This is not the production embedding model; it is a dependency-free handoff point that can later be replaced by OpenAI, Voyage, bge-m3, or another approved embedding model without moving permission checks into prompts.

The PostgreSQL adapter also exposes `list_retrieval_candidates`, a SQL-backed candidate selection boundary. In the JSON runtime, retrieval uses `candidate_strategy=local_full_scan`. In the PostgreSQL runtime, retrieval uses `candidate_strategy=postgres_hybrid_sql_v1`: SQL first applies tenant and role filters, then merges `websearch_to_tsquery` keyword candidates with pgvector nearest-neighbor candidates before Python applies the shared final scoring, prompt-injection checks, source-span citations, traces, and audit behavior.

After candidate selection, `secure-enterprise-knowledge-copilot/src/copilot/reranking.py` applies `local-evidence-reranker-v1`. This deterministic boundary records query overlap, title overlap, source metadata, candidate keyword/vector scores, and security penalties. The current reranker is deliberately local and replaceable; a production reranker can be introduced later without moving tenant, role, or citation rules into SQL or prompts.

The application layer receives a typed user context:

```text
tenant_id
user_id
role
allowed_departments
request_id
```

The database session sets the same context with transaction-local settings before queries:

```sql
select set_config('app.tenant_slug', :tenant_slug, true);
select set_config('app.tenant_id', :tenant_id, true);
select set_config('app.user_id', :user_id, true);
select set_config('app.role', :role, true);
```

Application checks remain mandatory. Row-level security is an additional database enforcement layer.

## Core Schema

### Shared Identity And Audit

```sql
create table tenants (
  id uuid primary key,
  name text not null,
  created_at timestamptz not null default now()
);

create table users (
  id uuid primary key,
  tenant_id uuid not null references tenants(id),
  display_name text not null,
  role text not null check (role in ('employee', 'manager', 'engineer', 'investigator', 'supervisor')),
  department text,
  created_at timestamptz not null default now()
);

create table audit_events (
  id bigserial primary key,
  tenant_id uuid not null references tenants(id),
  actor_user_id uuid references users(id),
  event_type text not null,
  entity_type text,
  entity_id text,
  payload jsonb not null default '{}'::jsonb,
  request_id text,
  created_at timestamptz not null default now()
);

create index audit_events_tenant_created_idx on audit_events (tenant_id, created_at desc);
create index audit_events_payload_gin_idx on audit_events using gin (payload);
```

### Project 1: Knowledge Copilot

```sql
create extension if not exists vector;

create table documents (
  id uuid primary key,
  tenant_id uuid not null references tenants(id),
  external_doc_id text not null,
  title text not null,
  source_uri text,
  sensitivity text not null check (sensitivity in ('public', 'internal', 'confidential')),
  allowed_roles text[] not null default '{}',
  allowed_departments text[] not null default '{}',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (tenant_id, external_doc_id)
);

create table document_chunks (
  id uuid primary key,
  tenant_id uuid not null references tenants(id),
  document_id uuid not null references documents(id) on delete cascade,
  chunk_index integer not null,
  content text not null,
  content_tsv tsvector generated always as (to_tsvector('english', content)) stored,
  embedding vector(1536),
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique (document_id, chunk_index)
);

create index documents_tenant_sensitivity_idx on documents (tenant_id, sensitivity);
create index document_chunks_tenant_doc_idx on document_chunks (tenant_id, document_id);
create index document_chunks_tsv_idx on document_chunks using gin (content_tsv);
create index document_chunks_embedding_hnsw_idx
  on document_chunks using hnsw (embedding vector_cosine_ops);
```

Retrieval flow:

1. Resolve user context.
2. Apply tenant, role, department, and document sensitivity filters.
3. Run keyword and vector retrieval only across authorized rows.
4. Rerank merged candidates.
5. Remove suspicious retrieved instructions.
6. Generate answer only from authorized evidence.
7. Write trace and audit records in the same request scope.

Hybrid retrieval query shape:

```sql
with authorized_chunks as (
  select c.*, d.title, d.external_doc_id
  from document_chunks c
  join documents d on d.id = c.document_id
  where c.tenant_id = current_setting('app.tenant_id')::uuid
    and current_setting('app.role') = any(d.allowed_roles)
),
keyword_hits as (
  select id, ts_rank_cd(content_tsv, websearch_to_tsquery('english', :query)) as keyword_score, 0.0 as vector_score
  from authorized_chunks
  where content_tsv @@ websearch_to_tsquery('english', :query)
  order by keyword_score desc
  limit 50
),
vector_hits as (
  select id, 0.0 as keyword_score, 1 - (embedding <=> :query_embedding) as vector_score
  from authorized_chunks
  where embedding is not null
  order by embedding <=> :query_embedding
  limit 50
),
merged_hits as (
  select id, max(keyword_score) as keyword_score, max(vector_score) as vector_score
  from (
    select * from keyword_hits
    union all
    select * from vector_hits
  ) hits
  group by id
)
select authorized_chunks.*, keyword_score, vector_score
from authorized_chunks
join merged_hits using (id)
order by keyword_score * 0.65 + vector_score * 0.35 desc
limit :top_k;
```

The exact scoring formula can evolve, but the authorization CTE must stay before evidence assembly.

### Project 2: Governed Operations Agent

```sql
create table cases (
  id uuid primary key,
  tenant_id uuid not null references tenants(id),
  external_case_id text not null,
  status text not null,
  marketplace text not null,
  seller_id text,
  product_id text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (tenant_id, external_case_id)
);

create table tool_actions (
  id uuid primary key,
  tenant_id uuid not null references tenants(id),
  case_id uuid references cases(id),
  requested_by uuid not null references users(id),
  tool_name text not null,
  action_type text not null,
  idempotency_key text not null,
  payload jsonb not null,
  status text not null check (status in ('proposed', 'blocked', 'approved', 'executed', 'failed')),
  created_at timestamptz not null default now(),
  unique (tenant_id, idempotency_key)
);

create table approval_requests (
  id uuid primary key,
  tenant_id uuid not null references tenants(id),
  tool_action_id uuid not null references tool_actions(id),
  requested_by uuid not null references users(id),
  approved_by uuid references users(id),
  status text not null check (status in ('pending', 'approved', 'rejected', 'expired')),
  decision_reason text,
  created_at timestamptz not null default now(),
  decided_at timestamptz
);

create index cases_tenant_status_idx on cases (tenant_id, status);
create index tool_actions_tenant_case_idx on tool_actions (tenant_id, case_id, created_at desc);
create index approval_requests_pending_idx
  on approval_requests (tenant_id, created_at desc)
  where status = 'pending';
```

Side-effect flow:

1. Agent proposes or routes an action.
2. Application checks role and tool policy.
3. Safe internal actions may execute transactionally.
4. External side effects create `tool_actions` and `approval_requests`.
5. Supervisor approval executes the side effect through an idempotent worker.
6. Result, approval decision, and audit event are written transactionally.

## Row-Level Security

PostgreSQL row-level security policies restrict which rows are visible or mutable after `ENABLE ROW LEVEL SECURITY` is applied. The official PostgreSQL docs note that normal row access must be allowed by a row security policy once RLS is enabled.

Recommended baseline:

```sql
alter table documents enable row level security;
alter table document_chunks enable row level security;
alter table cases enable row level security;
alter table tool_actions enable row level security;
alter table approval_requests enable row level security;
alter table audit_events enable row level security;

create policy tenant_isolation_documents on documents
  using (tenant_id = current_setting('app.tenant_id')::uuid);

create policy tenant_isolation_chunks on document_chunks
  using (tenant_id = current_setting('app.tenant_id')::uuid);

create policy authorized_documents_select on documents
  for select using (
    tenant_id = current_setting('app.tenant_id')::uuid
    and current_setting('app.role') = any(allowed_roles)
  );

create policy supervisor_approval_select on approval_requests
  for select using (
    tenant_id = current_setting('app.tenant_id')::uuid
    and (
      requested_by = current_setting('app.user_id')::uuid
      or current_setting('app.role') = 'supervisor'
    )
  );
```

Operational rules:

- Use separate database roles for application runtime, migrations, and read-only analytics.
- The app role should not own protected tables.
- Do not use broad bypass roles for normal request handling.
- Set request context at the start of every transaction.
- Add tests that intentionally query cross-tenant and cross-role rows.

## Indexing Strategy

Use exact search first for small corpora because pgvector defaults to exact nearest-neighbor search and this gives perfect recall for early-stage datasets. Add approximate indexes when corpus size or latency requires them.

Recommended progression:

1. Small corpus: exact vector search plus GIN keyword index.
2. Medium corpus: HNSW vector index for low-latency semantic retrieval.
3. Large or highly filtered corpus: benchmark HNSW, IVFFlat, partitioning, and exact fallback under real tenant and role filters.
4. Always measure recall@k, permission leaks, latency p50/p95, and over-retrieval rate.

Indexes to benchmark:

```sql
create index document_chunks_embedding_hnsw_idx
  on document_chunks using hnsw (embedding vector_cosine_ops);

create index document_chunks_embedding_ivfflat_idx
  on document_chunks using ivfflat (embedding vector_cosine_ops) with (lists = 100);
```

Do not assume vector recall is acceptable because the query is fast. The retrieval evals should fail when authorized evidence is missed or unauthorized evidence is retrieved. The current local runtime exposes vector contribution in `retrieved[].score_breakdown.vector`; production SQL retrieval still needs the same metric discipline around actual pgvector queries.

## Migrations

Use versioned migrations with a tool such as Alembic, Flyway, or Sqitch.

This repository now includes the first reviewable production-path migration artifact:

- `infra/postgres/migrations/001_core.sql`
- `infra/postgres/migrations/002_project1_denied_evidence_count.sql`
- `python -B scripts/dev.py postgres-migrations`
- `infra/postgres/seeds/001_project1_demo.sql`
- `docker-compose.postgres.yml`
- `python -B scripts/dev.py postgres-compose`
- `python -B scripts/dev.py postgres-runtime`
- `python -B scripts/dev.py postgres-seed`

The migration check verifies that the artifact keeps the core industrialization invariants visible: pgvector extension setup, document and chunk tables, source hashes, hybrid retrieval indexes, tenant-scoped RLS, role-aware document and chunk policies, SQL-backed hybrid candidate selection, eval-state isolation, approval visibility rules, idempotent tool-action keys, the Project 1 adapter contract, and the `project1_denied_relevant_chunk_count` helper. The compose check verifies the optional digest-pinned pgvector service, init order, seed wiring, healthcheck, and local role separation. The runtime check verifies that `COPILOT_REPOSITORY=postgres`, `COPILOT_POSTGRES_DSN`, optional `COPILOT_POSTGRES_POOL`, reset behavior, and docs stay aligned. The seed check verifies that checked-in Project 1 demo SQL is generated from the fictional JSON seed data and does not drift. The seed SQL stores deterministic chunk vectors in `document_chunks.embedding`, embedding provenance in chunk metadata, and source-span metadata over parser normalized text, keeping the pgvector schema, adapter, citation output, and local seed artifact aligned before a production embedding service is introduced. None of these checks makes PostgreSQL required for the default local demo.

RLS hides unauthorized rows from the app role, which is correct for security but can remove useful audit evidence such as "this query had relevant denied evidence." `infra/postgres/migrations/002_project1_denied_evidence_count.sql` adds a security-definer function that returns only a count of denied but potentially relevant chunks for the current tenant and role. It does not return document IDs, titles, chunk text, or snippets. `PostgresKnowledgeRepository.count_potentially_blocked_chunks` calls this function so the application can preserve blocked-evidence audit semantics without weakening RLS.

For local production-mode database testing on a Docker-enabled machine:

```bash
python -B scripts/dev.py postgres-compose
docker compose -f docker-compose.postgres.yml up -d
export COPILOT_REPOSITORY=postgres
export COPILOT_POSTGRES_DSN=postgresql://fde_app:fde_app_demo_password@127.0.0.1:55432/fde_portfolio
python -B scripts/check_project1_postgres_runtime.py --live
```

The `fde_app` / `fde_app_demo_password` credentials are public local-only demo values for the compose stack. They exist to prove the app does not need the migrator/table-owner role; any non-local deployment must replace them with secret-managed credentials.

Migration phases:

1. Review and run `001_core.sql` in a PostgreSQL/pgvector environment.
2. Seed the Project 1 demo tenant, users, documents, and chunks with `infra/postgres/seeds/001_project1_demo.sql`.
3. Replace `local-hashing-v1` with a production embedding provider behind the existing embedding boundary.
4. Add SQL-backed keyword/vector candidate selection. Done for the Project 1 PostgreSQL path through `postgres_hybrid_sql_v1`.
5. Add a deterministic reranker boundary. Done for the shared retrieval path through `local-evidence-reranker-v1`.
6. Add production reranking, larger retrieval metrics, and a production embedding provider behind the existing boundaries.
7. Backfill cases, approvals, audit events, traces, and eval records for Projects 2 and 3 when those adapters are added.
8. Dual-write local and PostgreSQL adapters in a staging environment.
9. Compare read results and eval outcomes across both adapters.
10. Cut reads to PostgreSQL behind a feature flag.
11. Remove dual-write only after evals and replay checks are stable.

Rollback rules:

- Schema changes must be backward compatible until the next release.
- Data migrations must be idempotent.
- Long-running index builds use concurrent creation where supported.
- Any policy change gets a negative test for unauthorized access.

## Eval Isolation

Production, demo, and eval state must stay separate:

```text
production tenant: real workflow state
demo tenant: seeded demo data
eval tenant: disposable eval data
```

Eval runners should either:

- use a dedicated eval database, or
- create a temporary tenant and delete it after the run.

Required checks:

- Eval writes never modify production approvals or notices.
- Eval audit events are tagged as eval traffic.
- Eval replay can be repeated without changing live demo state.
- CI fails if eval tables contain uncommitted runtime artifacts.

## Observability

Persist these records:

- `traces`: request id, user id, route, retrieval ids, tool calls, latency, model mode.
- `audit_events`: security and workflow events.
- `eval_runs`: suite id, git sha, environment, metrics.
- `eval_cases`: case id, input, expected behavior, pass/fail, failure reason.

This keeps the technical review story inspectable: a reviewer can connect an answer or agent action to the exact retrieved chunks, policy checks, tool decisions, approval request, audit event, and eval case.

## Phased Implementation Plan

1. Extend the existing `KnowledgeRepository` boundary while keeping local JSON adapters. Done for Project 1.
2. Keep building the optional PostgreSQL adapter path behind the `COPILOT_REPOSITORY=postgres` switch. Done for the Project 1 documents, chunks, traces, audit, and eval repository session path.
3. Add migrations and seed scripts. Done for the Project 1 demo seed path.
4. Run `python -B scripts/check_project1_postgres_runtime.py --live` against the seeded `docker-compose.postgres.yml` database on port `55432`; the live probe checks Alice finance denial, Morgan finance access, SQL hybrid candidate retrieval, and denied-evidence count behavior.
5. Replace the local deterministic embedding provider with a production embedding provider behind the existing boundary.
6. Replace the deterministic reranker with a production reranker and add larger retrieval metrics behind the existing candidate boundary.
7. Port Project 2 cases, tool actions, approvals, traces, and audit state.
8. Add RLS tests, unauthorized retrieval tests, and cross-tenant side-effect tests.
9. Record live Docker Compose PostgreSQL evidence on a Docker-enabled machine.
10. Run `python -B scripts/dev.py verify`, `python -B scripts/dev.py replay`, and adapter-specific evals before promoting.

## Open Risks

- Filtered vector search can return fast but incomplete results if metadata filters and index behavior are not benchmarked together.
- RLS policies are easy to bypass accidentally if application traffic uses a table owner or overly privileged role.
- Dual-write migrations can create trace/audit inconsistencies unless idempotency keys are stable.
- Approval execution needs transactional outbox semantics in production so external side effects are not lost or duplicated.

## References

- PostgreSQL Row Security Policies: https://www.postgresql.org/docs/17/ddl-rowsecurity.html
- PostgreSQL CREATE POLICY: https://www.postgresql.org/docs/17/sql-createpolicy.html
- pgvector README: https://github.com/pgvector/pgvector/blob/master/README.md
