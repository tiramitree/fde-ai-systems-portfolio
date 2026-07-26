-- 003_project1_group_acl.sql
-- Adds production-path group ACL context for Project 1 source permission sync.

alter table users add column if not exists group_ids text[] not null default '{}';

create index if not exists users_tenant_group_ids_idx on users using gin (group_ids);

drop policy if exists authorized_documents_select on documents;
create policy authorized_documents_select on documents
  for select using (
    tenant_id = current_setting('app.tenant_id')::uuid
    and (
      current_setting('app.role') = any(allowed_roles)
      or exists (
        select 1
        from jsonb_array_elements_text(coalesce(metadata->'allowed_groups', '[]'::jsonb)) as allowed(group_id)
        where allowed.group_id = any(
          coalesce(string_to_array(nullif(current_setting('app.group_ids', true), ''), ','), array[]::text[])
        )
      )
    )
  );

drop policy if exists authorized_chunks_select on document_chunks;
create policy authorized_chunks_select on document_chunks
  for select using (
    tenant_id = current_setting('app.tenant_id')::uuid
    and exists (
      select 1
      from documents d
      where d.id = document_chunks.document_id
        and d.tenant_id = document_chunks.tenant_id
        and (
          current_setting('app.role') = any(d.allowed_roles)
          or exists (
            select 1
            from jsonb_array_elements_text(coalesce(d.metadata->'allowed_groups', '[]'::jsonb)) as allowed(group_id)
            where allowed.group_id = any(
              coalesce(string_to_array(nullif(current_setting('app.group_ids', true), ''), ','), array[]::text[])
            )
          )
        )
    )
  );

create or replace function project1_denied_relevant_chunk_count(query_terms text[])
returns integer
language sql
security definer
set search_path = public
as $$
  select count(*)::integer
  from document_chunks c
  join documents d on d.id = c.document_id
  where c.tenant_id = current_setting('app.tenant_id')::uuid
    and not (
      current_setting('app.role') = any(d.allowed_roles)
      or exists (
        select 1
        from jsonb_array_elements_text(coalesce(d.metadata->'allowed_groups', '[]'::jsonb)) as allowed(group_id)
        where allowed.group_id = any(
          coalesce(string_to_array(nullif(current_setting('app.group_ids', true), ''), ','), array[]::text[])
        )
      )
    )
    and exists (
      select 1
      from unnest(query_terms) as term
      where length(term) > 1
        and position(
          lower(term) in lower(coalesce(d.title, '') || ' ' || coalesce(c.content, ''))
        ) > 0
    );
$$;

revoke all on function project1_denied_relevant_chunk_count(text[]) from public;
