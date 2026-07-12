-- ═══════════════════════════════════════════════════════════════════════
--  Migration 0015 — SEASONAL LEADERBOARD SNAPSHOTS (Phase 4)
--  Non-destructive seasonal archive: live lifetime stats are never reset;
--  instead, at season rollover ops capture the current top-N per metric into
--  leaderboard_snapshots tagged with the season id (from game_settings
--  `season.id`). Clients can then show "past season" boards. Run after 0014.
-- ═══════════════════════════════════════════════════════════════════════

create table if not exists public.leaderboard_snapshots (
  id            bigserial primary key,
  season_id     text not null,
  metric        text not null,
  rank          int not null,
  player_id     text not null,
  username      text,
  faction_code  text,
  value         numeric not null,
  captured_at   timestamptz not null default now()
);
create index if not exists lbsnap_season_metric_idx
  on public.leaderboard_snapshots (season_id, metric, rank);

-- Public READ (show past-season boards); writes only via the SECURITY DEFINER
-- capture function below (no public write policy).
alter table public.leaderboard_snapshots enable row level security;
drop policy if exists lbsnap_public_read on public.leaderboard_snapshots;
create policy lbsnap_public_read on public.leaderboard_snapshots for select using (true);

-- Capture the current top-N for a metric into the archive under a season id.
-- SECURITY DEFINER so it can insert despite the no-public-write policy; NOT
-- granted to anon/authenticated → only the service role (ops) can run it at
-- season rollover. Returns the number of rows archived.
create or replace function public.snapshot_leaderboard(
  p_season text, p_metric text, p_top int default 100)
returns int
language plpgsql security definer as $$
declare n int;
begin
  delete from public.leaderboard_snapshots
   where season_id = p_season and metric = p_metric;  -- idempotent re-capture
  insert into public.leaderboard_snapshots
    (season_id, metric, rank, player_id, username, faction_code, value)
  select p_season, p_metric, t.rank, t.player_id, t.username, t.faction_code, t.value
  from public.leaderboard_top(p_metric, null, p_top) t;
  get diagnostics n = row_count;
  return n;
end $$;

-- Read a past-season board (public).
create or replace function public.season_leaderboard(
  p_season text, p_metric text, p_limit int default 100)
returns table (rank int, player_id text, username text, faction_code text, value numeric)
language sql stable as $$
  select rank, player_id, username, faction_code, value
  from public.leaderboard_snapshots
  where season_id = p_season and metric = p_metric
  order by rank asc
  limit greatest(1, least(p_limit, 500));
$$;

grant execute on function public.season_leaderboard(text, text, int) to anon, authenticated;
-- snapshot_leaderboard intentionally NOT granted to anon/authenticated (ops-only).
