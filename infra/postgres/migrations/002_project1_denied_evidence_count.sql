-- 002_project1_denied_evidence_count.sql
-- Security-definer helper for counting denied but potentially relevant Project 1 evidence.
-- It returns only a count and never returns document titles, chunk bodies, or identifiers.

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
    and not (current_setting('app.role') = any(d.allowed_roles))
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
