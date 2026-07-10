-- ═══════════════════════════════════════════════════════════════════════
--  Master-data migration 0006 — MONSTERS
--  monster_master.json (187 monsters, 0 duplicate ids/codes) → public.monsters.
--  Scalars as columns; the many list/dict fields (element, spawn_location,
--  base_stats, scaling, resistances, weaknesses, status_immunity, ai_pattern,
--  skill_set, drop_item, special_reward) as JSONB. GIN index on drop_item so
--  "which monster drops item X" is a fast query (used by the loot/spawn audits).
--  Run after 0001.
-- ═══════════════════════════════════════════════════════════════════════

create table if not exists public.monsters (
  monster_id        int primary key,
  code              text not null unique,
  name              text not null,
  rank              text,
  level             int,
  race_code         text,
  spawn_monster_id  text,
  critical_rate     numeric,
  critical_damage   numeric,
  exp_reward        int,
  currency_reward   int,
  crd_reward        int,
  guild_point       int,
  reputation_point  int,
  hunting_point     int,
  element           jsonb not null default '[]'::jsonb,
  spawn_location    jsonb not null default '[]'::jsonb,
  base_stats        jsonb not null default '{}'::jsonb,
  scaling           jsonb not null default '{}'::jsonb,
  resistances       jsonb not null default '[]'::jsonb,
  weaknesses        jsonb not null default '[]'::jsonb,
  status_immunity   jsonb not null default '[]'::jsonb,
  ai_pattern        jsonb not null default '{}'::jsonb,
  skill_set         jsonb not null default '{}'::jsonb,
  drop_item         jsonb not null default '[]'::jsonb,
  special_reward    jsonb not null default '[]'::jsonb,
  sort_order        int not null default 0,
  updated_at        timestamptz not null default now()
);

create index if not exists monsters_rank_idx on public.monsters (rank);
create index if not exists monsters_race_idx on public.monsters (race_code);
create index if not exists monsters_drop_gin on public.monsters using gin (drop_item);

drop trigger if exists monsters_touch on public.monsters;
create trigger monsters_touch before update on public.monsters
  for each row execute function public.touch_updated_at();

drop trigger if exists monsters_bump_version on public.monsters;
create trigger monsters_bump_version after insert or update or delete on public.monsters
  for each statement execute function public.bump_content_version('monsters');

alter table public.monsters enable row level security;
drop policy if exists monsters_public_read on public.monsters;
create policy monsters_public_read on public.monsters for select using (true);
