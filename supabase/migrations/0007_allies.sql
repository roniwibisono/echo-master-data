-- ═══════════════════════════════════════════════════════════════════════
--  Master-data migration 0007 — ALLIES
--  ally_list.json (91 allies, 0 dup ids/codes) → public.allies. Scalars as
--  columns; base_stats as JSONB. passive_skill/active_skill are just
--  {"skill_id": "..."} wrappers → flattened to passive_skill_id /
--  active_skill_id text columns (queryable, joinable to public.skills);
--  export_allies.py re-wraps them. Run after 0001 (and 0005 for the skills FK
--  targets, though no hard FK is enforced so order is flexible).
-- ═══════════════════════════════════════════════════════════════════════

create table if not exists public.allies (
  ally_id                 text primary key,
  code                    text not null unique,
  name                    text not null,
  rarity                  text,
  role                    text,
  brief_background_story   text,
  place_of_origin         text,
  faction_affinity        text,
  base_stats              jsonb not null default '{}'::jsonb,
  passive_skill_id        text,
  active_skill_id         text,
  recruit_cost            int,
  level_cap               int,
  pvp_scale               numeric,
  conclave_points         int,
  sort_order              int not null default 0,
  updated_at              timestamptz not null default now()
);

create index if not exists allies_rarity_idx  on public.allies (rarity);
create index if not exists allies_role_idx    on public.allies (role);
create index if not exists allies_faction_idx on public.allies (faction_affinity);

drop trigger if exists allies_touch on public.allies;
create trigger allies_touch before update on public.allies
  for each row execute function public.touch_updated_at();

drop trigger if exists allies_bump_version on public.allies;
create trigger allies_bump_version after insert or update or delete on public.allies
  for each statement execute function public.bump_content_version('allies');

alter table public.allies enable row level security;
drop policy if exists allies_public_read on public.allies;
create policy allies_public_read on public.allies for select using (true);
