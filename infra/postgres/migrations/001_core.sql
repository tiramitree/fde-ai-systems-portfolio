-- 001_core.sql
-- Production-path schema for the FDE AI systems portfolio.
-- This migration is an auditable adapter artifact; the default local demos stay JSON-backed.

create extension if not exists vector;

create table if not exists tenants (
  id uuid primary key,
  slug text not null unique,
  name text not null,
  created_at timestamptz not null default now()
);

create table if not exists users (
  id uuid primary key,
  tenant_id uuid not null references tenants(id),
  external_user_id text not null,
  display_name text not null,
  role text not null check (role in ('employee', 'manager', 'admin', 'engineer', 'investigator', 'supervisor', 'pm')),
  department text,
  created_at timestamptz not null default now(),
  unique (tenant_id, external_user_id)
);

create table if not exists documents (
  id uuid primary key,
  tenant_id uuid not null references tenants(id),
  external_doc_id text not null,
  title text not null,
  source_uri text,
  source_mime text,
  source_hash text not null,
  sensitivity text not null check (sensitivity in ('public', 'internal', 'confidential')),
  allowed_roles text[] not null default '{}',
  allowed_departments text[] not null default '{}',
  version text not null,
  updated_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  unique (tenant_id, external_doc_id, source_hash)
);

create table if not exists document_chunks (
  id uuid primary key,
  tenant_id uuid not null references tenants(id),
  document_id uuid not null references documents(id) on delete cascade,
  chunk_index integer not null check (chunk_index >= 0),
  content text not null,
  content_tsv tsvector generated always as (to_tsvector('english', content)) stored,
  embedding vector(1536),
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique (document_id, chunk_index)
);

create table if not exists traces (
  id uuid primary key,
  tenant_id uuid not null references tenants(id),
  user_id uuid references users(id),
  request_id text not null,
  route text not null,
  model_mode text not null default 'local',
  payload jsonb not null default '{}'::jsonb,
  latency_ms integer,
  created_at timestamptz not null default now(),
  unique (tenant_id, request_id)
);

create table if not exists audit_events (
  id bigserial primary key,
  tenant_id uuid not null references tenants(id),
  actor_user_id uuid references users(id),
  trace_id uuid references traces(id),
  event_type text not null,
  entity_type text,
  entity_id text,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists eval_runs (
  id uuid primary key,
  tenant_id uuid not null references tenants(id),
  suite_id text not null,
  git_sha text,
  environment text not null check (environment in ('local', 'ci', 'staging', 'production')),
  metrics jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists eval_cases (
  id uuid primary key,
  tenant_id uuid not null references tenants(id),
  eval_run_id uuid not null references eval_runs(id) on delete cascade,
  case_id text not null,
  input jsonb not null,
  expected jsonb not null,
  outcome jsonb not null default '{}'::jsonb,
  passed boolean not null,
  trace_id uuid references traces(id),
  created_at timestamptz not null default now(),
  unique (eval_run_id, case_id)
);

create table if not exists cases (
  id uuid primary key,
  tenant_id uuid not null references tenants(id),
  external_case_id text not null,
  status text not null,
  marketplace text,
  metadata jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  unique (tenant_id, external_case_id)
);

create table if not exists tool_actions (
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

create table if not exists approval_requests (
  id uuid primary key,
  tenant_id uuid not null references tenants(id),
  tool_action_id uuid not null references tool_actions(id),
  requested_by uuid not null references users(id),
  approved_by uuid references users(id),
  status text not null check (status in ('pending', 'approved', 'rejected', 'expired')),
  decision_reason text,
  decided_at timestamptz,
  created_at timestamptz not null default now()
);

create index if not exists users_tenant_role_idx on users (tenant_id, role);
create index if not exists documents_tenant_sensitivity_idx on documents (tenant_id, sensitivity);
create index if not exists documents_source_hash_idx on documents (tenant_id, source_hash);
create index if not exists document_chunks_tenant_doc_idx on document_chunks (tenant_id, document_id);
create index if not exists document_chunks_tsv_idx on document_chunks using gin (content_tsv);
create index if not exists document_chunks_embedding_hnsw_idx
  on document_chunks using hnsw (embedding vector_cosine_ops);
create index if not exists traces_tenant_created_idx on traces (tenant_id, created_at desc);
create index if not exists audit_events_tenant_created_idx on audit_events (tenant_id, created_at desc);
create index if not exists audit_events_payload_gin_idx on audit_events using gin (payload);
create index if not exists eval_runs_tenant_created_idx on eval_runs (tenant_id, created_at desc);
create index if not exists cases_tenant_status_idx on cases (tenant_id, status);
create index if not exists tool_actions_tenant_case_idx on tool_actions (tenant_id, case_id, created_at desc);
create index if not exists approval_requests_pending_idx
  on approval_requests (tenant_id, created_at desc)
  where status = 'pending';

alter table tenants enable row level security;
alter table users enable row level security;
alter table documents enable row level security;
alter table document_chunks enable row level security;
alter table traces enable row level security;
alter table audit_events enable row level security;
alter table eval_runs enable row level security;
alter table eval_cases enable row level security;
alter table cases enable row level security;
alter table tool_actions enable row level security;
alter table approval_requests enable row level security;

create policy tenant_isolation_users on users
  using (tenant_id = current_setting('app.tenant_id')::uuid)
  with check (tenant_id = current_setting('app.tenant_id')::uuid);

create policy authorized_documents_select on documents
  for select using (
    tenant_id = current_setting('app.tenant_id')::uuid
    and current_setting('app.role') = any(allowed_roles)
  );

create policy tenant_document_writes on documents
  for all using (tenant_id = current_setting('app.tenant_id')::uuid)
  with check (tenant_id = current_setting('app.tenant_id')::uuid);

create policy authorized_chunks_select on document_chunks
  for select using (
    tenant_id = current_setting('app.tenant_id')::uuid
    and exists (
      select 1
      from documents d
      where d.id = document_chunks.document_id
        and d.tenant_id = document_chunks.tenant_id
        and current_setting('app.role') = any(d.allowed_roles)
    )
  );

create policy tenant_chunk_writes on document_chunks
  for all using (tenant_id = current_setting('app.tenant_id')::uuid)
  with check (tenant_id = current_setting('app.tenant_id')::uuid);

create policy tenant_traces on traces
  for all using (tenant_id = current_setting('app.tenant_id')::uuid)
  with check (tenant_id = current_setting('app.tenant_id')::uuid);

create policy tenant_audit_events on audit_events
  for all using (tenant_id = current_setting('app.tenant_id')::uuid)
  with check (tenant_id = current_setting('app.tenant_id')::uuid);

create policy eval_state_isolation_runs on eval_runs
  for all using (
    tenant_id = current_setting('app.tenant_id')::uuid
    and current_setting('app.environment', true) in ('local', 'ci', 'staging')
  )
  with check (
    tenant_id = current_setting('app.tenant_id')::uuid
    and current_setting('app.environment', true) in ('local', 'ci', 'staging')
  );

create policy eval_state_isolation_cases on eval_cases
  for all using (
    tenant_id = current_setting('app.tenant_id')::uuid
    and current_setting('app.environment', true) in ('local', 'ci', 'staging')
  )
  with check (
    tenant_id = current_setting('app.tenant_id')::uuid
    and current_setting('app.environment', true) in ('local', 'ci', 'staging')
  );

create policy tenant_cases on cases
  for all using (tenant_id = current_setting('app.tenant_id')::uuid)
  with check (tenant_id = current_setting('app.tenant_id')::uuid);

create policy tenant_tool_actions on tool_actions
  for all using (tenant_id = current_setting('app.tenant_id')::uuid)
  with check (tenant_id = current_setting('app.tenant_id')::uuid);

create policy supervisor_approval_select on approval_requests
  for select using (
    tenant_id = current_setting('app.tenant_id')::uuid
    and (
      requested_by = current_setting('app.user_id')::uuid
      or current_setting('app.role') = 'supervisor'
    )
  );

create policy supervisor_approval_writes on approval_requests
  for all using (tenant_id = current_setting('app.tenant_id')::uuid)
  with check (tenant_id = current_setting('app.tenant_id')::uuid);
