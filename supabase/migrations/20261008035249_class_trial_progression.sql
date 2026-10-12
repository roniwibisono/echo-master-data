-- Four-tier class definitions. Existing player history is not migrated or reset.
-- Apply after 0001_quests.sql, then class_progression_20261008.sql.
begin;
alter table public.quests add column if not exists auto_accept boolean not null default false;
create table if not exists public.classes (
  id text primary key,
  name text not null,
  tier text not null check (tier in ('Base','Advance','Expert','Master')),
  parent_id text references public.classes(id) deferrable initially deferred,
  description text not null default '',
  is_active smallint not null default 1 check (is_active in (0,1)),
  base_stats_bonus jsonb not null default '{}'::jsonb,
  learnable_skill_ids jsonb not null default '[]'::jsonb,
  sort_order integer not null default 0,
  updated_at timestamptz not null default now()
);
create index if not exists classes_parent_idx on public.classes(parent_id);
drop trigger if exists classes_touch on public.classes;
create trigger classes_touch before update on public.classes
  for each row execute function public.touch_updated_at();
drop trigger if exists classes_bump_version on public.classes;
create trigger classes_bump_version after insert or update or delete on public.classes
  for each statement execute function public.bump_content_version('classes');
alter table public.classes enable row level security;
drop policy if exists classes_public_read on public.classes;
create policy classes_public_read on public.classes for select to anon, authenticated using (true);
revoke all on public.classes from anon, authenticated;
grant select on public.classes to anon, authenticated;
commit;
