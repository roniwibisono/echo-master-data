begin;
alter table public.skills add column if not exists skill_memory_tier integer;
alter table public.skills add constraint skills_memory_tier_range
  check (skill_memory_tier is null or skill_memory_tier between 1 and 3);

-- Learner-bound templates are not public quest instances.
create table public.skill_memory_catalog (
  id text primary key,
  schema_version integer not null check (schema_version > 0),
  runtime_ready boolean not null default false,
  payload jsonb not null check (jsonb_typeof(payload) = 'object'),
  updated_at timestamptz not null default now()
);
alter table public.skill_memory_catalog enable row level security;
revoke all on public.skill_memory_catalog from anon, authenticated;
grant select on public.skill_memory_catalog to anon, authenticated;
grant all on public.skill_memory_catalog to service_role;
create policy skill_memory_catalog_read on public.skill_memory_catalog
  for select to anon, authenticated using (true);
create trigger skill_memory_catalog_touch before update on public.skill_memory_catalog
  for each row execute function public.touch_updated_at();
commit;
