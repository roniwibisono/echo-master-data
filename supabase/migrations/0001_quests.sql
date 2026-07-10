-- ═══════════════════════════════════════════════════════════════════════
--  Master-data migration 0001 — QUESTS
--  Unifies the 8 quest_*.json files into a single Supabase table so quests
--  can be edited in the dashboard/SQL instead of hand-maintained JSON.
--  The nested structures stay as JSONB (the Flutter model is unchanged) so
--  this is a low-risk lift. `source_file` + `sort_order` let the export tool
--  regenerate the exact original JSON files for the CDN (client untouched).
--  Run once in the Supabase SQL editor, then load supabase/seed/quests_seed.sql.
-- ═══════════════════════════════════════════════════════════════════════

-- ── Content version registry (for cache-busting / checkVersion) ──────────
create table if not exists public.master_content_version (
  domain      text primary key,
  version     bigint not null default 1,
  updated_at  timestamptz not null default now()
);

create or replace function public.bump_content_version()
  returns trigger language plpgsql as $$
begin
  insert into public.master_content_version(domain, version, updated_at)
  values (tg_argv[0], 1, now())
  on conflict (domain)
    do update set version = master_content_version.version + 1,
                  updated_at = now();
  return null;
end $$;

-- ── Quests ───────────────────────────────────────────────────────────────
create table if not exists public.quests (
  id                  text primary key,
  title               text not null,
  type                text,
  rank                text,
  faction             text not null,
  region              text,
  description         text,
  -- nested structures kept as JSONB (matches the Flutter QuestTemplate model)
  quest_giver         jsonb not null default '{}'::jsonb,
  requirements        jsonb not null default '{}'::jsonb,
  objectives          jsonb not null default '[]'::jsonb,
  rewards             jsonb not null default '{}'::jsonb,
  repeatable          boolean not null default false,
  daily               boolean not null default false,
  quest_chain_next    text,
  -- popup / tutorial metadata (only on a handful of msq_* quests)
  popup               boolean not null default false,
  popup_trigger       text,
  popup_level         int,
  popup_prerequisite  text,
  -- round-trip bookkeeping so export can rebuild the original CDN files 1:1
  source_file         text,
  sort_order          int not null default 0,
  updated_at          timestamptz not null default now()
);

create index if not exists quests_faction_idx on public.quests (faction);
create index if not exists quests_type_idx    on public.quests (type);
create index if not exists quests_source_idx  on public.quests (source_file, sort_order);
-- query quests by required prerequisite quest, etc. (JSONB GIN)
create index if not exists quests_requirements_gin on public.quests using gin (requirements);

-- touch updated_at on every write
create or replace function public.touch_updated_at()
  returns trigger language plpgsql as $$
begin new.updated_at := now(); return new; end $$;

drop trigger if exists quests_touch on public.quests;
create trigger quests_touch before update on public.quests
  for each row execute function public.touch_updated_at();

-- bump the 'quests' content version on any change (per statement = one bump/batch)
drop trigger if exists quests_bump_version on public.quests;
create trigger quests_bump_version after insert or update or delete on public.quests
  for each statement execute function public.bump_content_version('quests');

-- ── RLS: master data is public read-only; writes only via service role ───
alter table public.quests enable row level security;
drop policy if exists quests_public_read on public.quests;
create policy quests_public_read on public.quests for select using (true);

alter table public.master_content_version enable row level security;
drop policy if exists mcv_public_read on public.master_content_version;
create policy mcv_public_read on public.master_content_version for select using (true);
