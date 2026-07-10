-- ═══════════════════════════════════════════════════════════════════════
--  Master-data migration 0003 — RAID EVENTS (live/timed content)
--  raid_boss_event.json (the timed raid boss definitions) → public.raid_events.
--  Scalars as columns; nested (entry_requirements / spawn_monster_id / phases /
--  clear_rewards) as JSONB, matching the RaidEvent model. export_raids.py
--  rebuilds {raids:[...]} for the CDN (client unchanged).
--  Run after 0001 (needs touch_updated_at + bump_content_version).
--
--  NOTE: quest_events.json currently holds 0 quests — it is already covered by
--  the quests migration (0001) which round-trips it as an empty file; no
--  separate table is needed until timed quest-events actually exist.
-- ═══════════════════════════════════════════════════════════════════════

create table if not exists public.raid_events (
  raid_id                 text primary key,
  name                    text not null,
  region                  text,
  min_level               int,
  recommended_party_size  int,
  max_player              int,
  spawn_time_ends         int,
  time_limit              int,
  boss_monster_id         int,
  raid_type               text,
  max_entry               int,
  entry_requirements      jsonb not null default '[]'::jsonb,
  spawn_monster_id        jsonb not null default '[]'::jsonb,
  phases                  jsonb not null default '[]'::jsonb,
  clear_rewards           jsonb not null default '{}'::jsonb,
  sort_order              int not null default 0,
  updated_at              timestamptz not null default now()
);

create index if not exists raid_events_region_idx on public.raid_events (region);

drop trigger if exists raid_events_touch on public.raid_events;
create trigger raid_events_touch before update on public.raid_events
  for each row execute function public.touch_updated_at();

drop trigger if exists raid_events_bump_version on public.raid_events;
create trigger raid_events_bump_version after insert or update or delete on public.raid_events
  for each statement execute function public.bump_content_version('raid_events');

alter table public.raid_events enable row level security;
drop policy if exists raid_events_public_read on public.raid_events;
create policy raid_events_public_read on public.raid_events for select using (true);
