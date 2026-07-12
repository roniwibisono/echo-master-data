-- ═══════════════════════════════════════════════════════════════════════
--  Migration 0012 — ACHIEVEMENTS (Phase 2)
--  Data-driven, tiered achievement DEFINITIONS (mirrors achievements.json on
--  the CDN; client reads the CDN copy, this table is the editable source) +
--  a per-player unlock table for cloud sync / achievement leaderboards.
--  Definitions reference a PlayerStats metric key + threshold. Run after 0001.
-- ═══════════════════════════════════════════════════════════════════════

create table if not exists public.achievements (
  id            text primary key,
  name          text not null,
  description   text,
  category      text not null,          -- combat|progression|quests|crafting|explore|economy|pvp
  metric        text not null,          -- StatKeys metric key
  operator      text not null default 'gte',
  threshold     numeric not null,
  tier          text not null,          -- bronze|silver|gold|…
  reward_title  text,                   -- optional title id granted on unlock
  reward_rubies int not null default 0,
  hidden        boolean not null default false,
  sort_order    int not null default 0,
  updated_at    timestamptz not null default now()
);
create index if not exists achievements_category_idx on public.achievements (category);
create index if not exists achievements_metric_idx on public.achievements (metric);

drop trigger if exists achievements_touch on public.achievements;
create trigger achievements_touch before update on public.achievements
  for each row execute function public.touch_updated_at();
drop trigger if exists achievements_bump_version on public.achievements;
create trigger achievements_bump_version after insert or update or delete on public.achievements
  for each statement execute function public.bump_content_version('achievements');

alter table public.achievements enable row level security;
drop policy if exists achievements_public_read on public.achievements;
create policy achievements_public_read on public.achievements for select using (true);

-- ── Per-player unlocks (cloud mirror / achievement leaderboards) ──────────
create table if not exists public.player_achievements (
  player_id       text not null,
  achievement_id  text not null,
  unlocked_at     timestamptz not null default now(),
  primary key (player_id, achievement_id)
);
create index if not exists pa_player_idx on public.player_achievements (player_id);
create index if not exists pa_achievement_idx on public.player_achievements (achievement_id);

alter table public.player_achievements enable row level security;
drop policy if exists player_achievements_public_read on public.player_achievements;
create policy player_achievements_public_read on public.player_achievements for select using (true);
drop policy if exists player_achievements_owner_write on public.player_achievements;
create policy player_achievements_owner_write on public.player_achievements
  for all using (auth.uid()::text = player_id) with check (auth.uid()::text = player_id);
