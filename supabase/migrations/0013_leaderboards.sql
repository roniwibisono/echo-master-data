-- ═══════════════════════════════════════════════════════════════════════
--  Migration 0013 — LEADERBOARDS (Phase 3)
--  RPC functions that rank players by any PlayerStats metric out of
--  public.player_stats. PostgREST can't ORDER BY a JSONB expression directly,
--  so these SQL functions expose ranked results (callable via supabase.rpc()).
--  p_metric is used only as a JSONB *value* key (->>), never as an identifier,
--  so there is no SQL-injection surface; the hot metrics have expression
--  indexes (see 0011) so those sorts are fast. Run after 0011.
-- ═══════════════════════════════════════════════════════════════════════

-- Top N players by a metric, optionally scoped to a faction.
create or replace function public.leaderboard_top(
  p_metric  text,
  p_faction text default null,
  p_limit   int  default 100
)
returns table (
  rank         bigint,
  player_id    text,
  username     text,
  faction_code text,
  level        int,
  value        numeric
)
language sql stable as $$
  select
    row_number() over (order by coalesce((counters->>p_metric)::numeric, 0) desc, updated_at asc) as rank,
    player_id, username, faction_code, level,
    coalesce((counters->>p_metric)::numeric, 0) as value
  from public.player_stats
  where (p_faction is null or faction_code = p_faction)
  order by value desc, updated_at asc
  limit greatest(1, least(p_limit, 500));
$$;

-- A single player's rank for a metric (1-based), optionally within a faction.
create or replace function public.leaderboard_rank(
  p_metric  text,
  p_player  text,
  p_faction text default null
)
returns bigint
language sql stable as $$
  select count(*) + 1
  from public.player_stats
  where (p_faction is null or faction_code = p_faction)
    and coalesce((counters->>p_metric)::numeric, 0) >
        coalesce((
          select (counters->>p_metric)::numeric
          from public.player_stats where player_id = p_player
        ), 0);
$$;

grant execute on function public.leaderboard_top(text, text, int) to anon, authenticated;
grant execute on function public.leaderboard_rank(text, text, text) to anon, authenticated;
