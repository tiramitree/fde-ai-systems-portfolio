-- Local production-mode role setup for docker-compose.postgres.yml.
-- These are public demo credentials for local verification only.

do $$
begin
  if not exists (select 1 from pg_roles where rolname = 'fde_app') then
    create role fde_app login password 'fde_app_demo_password';
  else
    alter role fde_app with login password 'fde_app_demo_password';
  end if;
end
$$;

alter role fde_app set row_security = on;
