-- ═══════════════════════════════════════════════════════════════════════
--  Master-data migration 0008 — NPCS
--  npc_list.json (147 NPCs, 0 dup ids) → public.npcs. Scalars as columns;
--  available_services / actions as JSONB. Optional fields (personality,
--  shop_inventory, buy_currency, rest_currency, sell_note, quest_category,
--  reward_currency) are NULL when absent, omitted on export. Run after 0001.
--
--  NOTE: npc_additions.json is NOT migrated. The client only adds an addition
--  whose id is NOT already in npc_list, and all 28 addition ids overlap the
--  list — so npc_additions contributes ZERO NPCs at runtime (npc_list wins).
--  15 of those overlaps DIFFER from the list version (intended patches the
--  client silently ignores) — surface for cleanup; not migrated here.
-- ═══════════════════════════════════════════════════════════════════════

create table if not exists public.npcs (
  npc_id             text primary key,
  name               text not null,
  title              text,
  role               text,
  faction            text,
  location           text,
  region_id          text,
  description        text,
  personality        text,
  greeting           text,
  shop_inventory     text,
  dialogue_tree      text,
  buy_currency       text,
  rest_currency      text,
  sell_note          text,
  quest_category     text,
  reward_currency    text,
  available_services jsonb not null default '[]'::jsonb,
  actions            jsonb not null default '[]'::jsonb,
  sort_order         int not null default 0,
  updated_at         timestamptz not null default now()
);

create index if not exists npcs_role_idx    on public.npcs (role);
create index if not exists npcs_faction_idx on public.npcs (faction);
create index if not exists npcs_region_idx  on public.npcs (region_id);

drop trigger if exists npcs_touch on public.npcs;
create trigger npcs_touch before update on public.npcs
  for each row execute function public.touch_updated_at();

drop trigger if exists npcs_bump_version on public.npcs;
create trigger npcs_bump_version after insert or update or delete on public.npcs
  for each statement execute function public.bump_content_version('npcs');

alter table public.npcs enable row level security;
drop policy if exists npcs_public_read on public.npcs;
create policy npcs_public_read on public.npcs for select using (true);
