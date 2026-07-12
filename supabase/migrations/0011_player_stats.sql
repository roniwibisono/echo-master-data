-- ═══════════════════════════════════════════════════════════════════════
--  Migration 0011 — PLAYER STATS (Phase 1: cloud mirror for leaderboards)
--  Player accomplishment stats already ride inside player_saves.profile JSON.
--  These tables are the QUERYABLE mirror the client upserts (debounced) so
--  leaderboards/achievements can rank + aggregate server-side.
--    • player_stats      — hot scalar counters (JSONB) + expression indexes
--    • player_stat_maps  — full breakdown maps (kills_by_monster, …), slower sync
--    • stat_events       — append-only event log (audit + anti-cheat + feeds)
--  player_id == auth.uid() (owner-scoped writes). Run after 0001.
-- ═══════════════════════════════════════════════════════════════════════

-- ── Aggregate counters (leaderboard-queryable) ────────────────────────────
create table if not exists public.player_stats (
  player_id     text primary key,
  faction_code  text,
  username      text,
  level         int not null default 1,
  power_rating  int not null default 0,
  counters      jsonb not null default '{}'::jsonb,  -- StatKeys -> num
  firsts        jsonb not null default '{}'::jsonb,   -- milestone timestamps
  updated_at    timestamptz not null default now()
);
create index if not exists player_stats_faction_idx on public.player_stats (faction_code);
-- Expression indexes for the hot leaderboard metrics (ORDER BY <metric> DESC).
create index if not exists ps_monsters_killed_idx
  on public.player_stats (((counters->>'monsters_killed')::bigint) desc);
create index if not exists ps_total_damage_idx
  on public.player_stats (((counters->>'total_damage_dealt')::bigint) desc);
create index if not exists ps_battles_won_idx
  on public.player_stats (((counters->>'battles_won')::bigint) desc);
create index if not exists ps_quests_completed_idx
  on public.player_stats (((counters->>'quests_completed')::bigint) desc);
create index if not exists ps_crafts_idx
  on public.player_stats (((counters->>'crafts_completed')::bigint) desc);
create index if not exists ps_pvp_wins_idx
  on public.player_stats (((counters->>'pvp_duels_won')::bigint) desc);
create index if not exists ps_max_level_idx
  on public.player_stats (((counters->>'max_level_reached')::bigint) desc);

drop trigger if exists player_stats_touch on public.player_stats;
create trigger player_stats_touch before update on public.player_stats
  for each row execute function public.touch_updated_at();

-- ── Full breakdown maps (bestiary / collection completeness) ───────────────
create table if not exists public.player_stat_maps (
  player_id   text primary key,
  breakdowns  jsonb not null default '{}'::jsonb,  -- group -> {key: count}
  updated_at  timestamptz not null default now()
);
drop trigger if exists player_stat_maps_touch on public.player_stat_maps;
create trigger player_stat_maps_touch before update on public.player_stat_maps
  for each row execute function public.touch_updated_at();

-- ── Append-only event log (audit / anti-cheat replay / activity feed) ──────
create table if not exists public.stat_events (
  id          bigserial primary key,
  player_id   text not null,
  type        text not null,
  amount      numeric not null default 0,
  meta        jsonb,
  created_at  timestamptz not null default now()
);
create index if not exists stat_events_player_idx
  on public.stat_events (player_id, created_at desc);

-- ── RLS: public READ (leaderboards), owner-only WRITE (player_id = auth uid) ─
alter table public.player_stats enable row level security;
drop policy if exists player_stats_public_read on public.player_stats;
create policy player_stats_public_read on public.player_stats for select using (true);
drop policy if exists player_stats_owner_write on public.player_stats;
create policy player_stats_owner_write on public.player_stats
  for all using (auth.uid()::text = player_id) with check (auth.uid()::text = player_id);

alter table public.player_stat_maps enable row level security;
drop policy if exists player_stat_maps_public_read on public.player_stat_maps;
create policy player_stat_maps_public_read on public.player_stat_maps for select using (true);
drop policy if exists player_stat_maps_owner_write on public.player_stat_maps;
create policy player_stat_maps_owner_write on public.player_stat_maps
  for all using (auth.uid()::text = player_id) with check (auth.uid()::text = player_id);

-- stat_events: owner can insert + read own; NOT public-read.
alter table public.stat_events enable row level security;
drop policy if exists stat_events_owner_insert on public.stat_events;
create policy stat_events_owner_insert on public.stat_events
  for insert with check (auth.uid()::text = player_id);
drop policy if exists stat_events_owner_read on public.stat_events;
create policy stat_events_owner_read on public.stat_events
  for select using (auth.uid()::text = player_id);

-- NOTE: writes are owner-scoped but NOT yet plausibility-validated — server-side
-- delta/anti-cheat checks (game_settings anticheat.* thresholds) land in Phase 4.
