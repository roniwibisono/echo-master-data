-- ═══════════════════════════════════════════════════════════════════════
--  Migration 0014 — ANTI-CHEAT (Phase 4): server-side plausibility flagging
--  player_stats writes are owner-scoped but a hacked client could inflate them.
--  A BEFORE UPDATE trigger compares the delta since the last sync against the
--  live game_settings `anticheat.*` per-hour/per-day thresholds and, if a jump
--  is implausible, records a stat_flags row and marks the player row `flagged`.
--  Policy: FLAG, don't block (never breaks a legit bursty sync). Leaderboards
--  exclude flagged players. Thresholds default to 0 (= disabled) so this is
--  opt-in — ops enable it live by setting anticheat.* in game_settings.
--  Runs after 0011 (player_stats) + 0010 (game_settings). Sticky: a player
--  cannot clear their own flag (trigger ORs with the old value, ignoring the
--  client-supplied column).
-- ═══════════════════════════════════════════════════════════════════════

alter table public.player_stats
  add column if not exists flagged boolean not null default false;

create table if not exists public.stat_flags (
  id                  bigserial primary key,
  player_id           text not null,
  metric              text not null,
  delta               numeric not null,
  elapsed_hours       numeric not null,
  threshold_per_hour  numeric not null,
  note                text,
  created_at          timestamptz not null default now()
);
create index if not exists stat_flags_player_idx on public.stat_flags (player_id, created_at desc);

-- admin/service-role only — RLS on, NO public policy.
alter table public.stat_flags enable row level security;

create or replace function public.setting_num(p_key text)
returns numeric language sql stable as $$
  select coalesce((value #>> '{}')::numeric, 0)
  from public.game_settings where key = p_key;
$$;

create or replace function public.flag_implausible_stats()
returns trigger language plpgsql as $$
declare
  elapsed_h numeric := greatest(extract(epoch from (now() - old.updated_at)) / 3600.0, 0.0001);
  elapsed_d numeric := greatest(extract(epoch from (now() - old.updated_at)) / 86400.0, 0.0001);
  violated  boolean := false;
  thr       numeric;
  d         numeric;
begin
  -- helper: flag when delta exceeds BOTH the rate window AND one full period
  -- (avoids twitchy false-positives on tiny debounce windows).
  thr := public.setting_num('anticheat.max_exp_per_hour');
  if thr > 0 then
    d := coalesce((new.counters->>'total_exp_earned')::numeric,0)
       - coalesce((old.counters->>'total_exp_earned')::numeric,0);
    if d > thr * elapsed_h and d > thr then
      insert into public.stat_flags(player_id, metric, delta, elapsed_hours, threshold_per_hour, note)
      values (new.player_id, 'total_exp_earned', d, elapsed_h, thr, 'exp/hour exceeded');
      violated := true;
    end if;
  end if;

  thr := public.setting_num('anticheat.max_credits_per_hour');
  if thr > 0 then
    d := coalesce((new.counters->>'credits_earned_total')::numeric,0)
       - coalesce((old.counters->>'credits_earned_total')::numeric,0);
    if d > thr * elapsed_h and d > thr then
      insert into public.stat_flags(player_id, metric, delta, elapsed_hours, threshold_per_hour, note)
      values (new.player_id, 'credits_earned_total', d, elapsed_h, thr, 'credits/hour exceeded');
      violated := true;
    end if;
  end if;

  thr := public.setting_num('anticheat.max_levelups_per_day');
  if thr > 0 then
    d := coalesce((new.counters->>'levelups')::numeric,0)
       - coalesce((old.counters->>'levelups')::numeric,0);
    if d > thr * elapsed_d and d > thr then
      insert into public.stat_flags(player_id, metric, delta, elapsed_hours, threshold_per_hour, note)
      values (new.player_id, 'levelups', d, elapsed_d, thr, 'levelups/day exceeded');
      violated := true;
    end if;
  end if;

  -- sticky + client-tamper-proof: recompute from old, ignore client value.
  new.flagged := coalesce(old.flagged, false) or violated;
  return new;
end $$;

drop trigger if exists player_stats_anticheat on public.player_stats;
create trigger player_stats_anticheat before update on public.player_stats
  for each row execute function public.flag_implausible_stats();

-- ── Leaderboards exclude flagged players ──────────────────────────────────
create or replace function public.leaderboard_top(
  p_metric text, p_faction text default null, p_limit int default 100)
returns table (rank bigint, player_id text, username text, faction_code text, level int, value numeric)
language sql stable as $$
  select
    row_number() over (order by coalesce((counters->>p_metric)::numeric, 0) desc, updated_at asc) as rank,
    player_id, username, faction_code, level,
    coalesce((counters->>p_metric)::numeric, 0) as value
  from public.player_stats
  where (p_faction is null or faction_code = p_faction) and not flagged
  order by value desc, updated_at asc
  limit greatest(1, least(p_limit, 500));
$$;

create or replace function public.leaderboard_rank(
  p_metric text, p_player text, p_faction text default null)
returns bigint language sql stable as $$
  select count(*) + 1
  from public.player_stats
  where (p_faction is null or faction_code = p_faction) and not flagged
    and coalesce((counters->>p_metric)::numeric, 0) >
        coalesce((select (counters->>p_metric)::numeric from public.player_stats where player_id = p_player), 0);
$$;

grant execute on function public.leaderboard_top(text, text, int) to anon, authenticated;
grant execute on function public.leaderboard_rank(text, text, text) to anon, authenticated;
grant execute on function public.setting_num(text) to anon, authenticated;
