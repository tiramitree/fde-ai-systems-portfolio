-- Local production-mode grants for the Project 1 PostgreSQL runtime path.
-- The app role is deliberately not the migration/table owner, so row-level
-- security remains meaningful during live local verification.

grant connect on database fde_portfolio to fde_app;
grant usage on schema public to fde_app;
grant select, insert, update, delete on all tables in schema public to fde_app;
grant usage, select on all sequences in schema public to fde_app;

alter default privileges in schema public
  grant select, insert, update, delete on tables to fde_app;

alter default privileges in schema public
  grant usage, select on sequences to fde_app;
