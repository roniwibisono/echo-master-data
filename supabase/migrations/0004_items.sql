-- ═══════════════════════════════════════════════════════════════════════
--  Master-data migration 0004 — ITEMS
--  item_list.json (1146 entries) → public.items. Scalars as columns;
--  equipment_slots / stats_bonus / special_effects as JSONB. Run after 0001.
--
--  DATA NOTE: the source file has 37 duplicate ids (20 identical, 17 with
--  conflicting prices, e.g. core_fragment @ buy 30/40/0). The Flutter client
--  builds its id→item map last-write-wins, so the seed keeps the LAST
--  occurrence of each id (matching runtime) → the table has one row per id
--  (~1109 unique). Review the 17 conflicts (import_items.py prints them) and
--  fix prices here — the primary key now prevents the duplicates recurring.
-- ═══════════════════════════════════════════════════════════════════════

create table if not exists public.items (
  id                 text primary key,
  name               text not null,
  type               text,
  rarity             text,
  level_requirement  int,
  buy_price          int,
  sell_price         int,
  sell_value         int,
  max_stack          int,
  icon_image         text,
  description        text,
  equipment_slots    jsonb not null default '[]'::jsonb,
  stats_bonus        jsonb not null default '{}'::jsonb,
  special_effects    jsonb not null default '[]'::jsonb,
  sort_order         int not null default 0,
  updated_at         timestamptz not null default now()
);

create index if not exists items_type_idx   on public.items (type);
create index if not exists items_rarity_idx on public.items (rarity);

drop trigger if exists items_touch on public.items;
create trigger items_touch before update on public.items
  for each row execute function public.touch_updated_at();

drop trigger if exists items_bump_version on public.items;
create trigger items_bump_version after insert or update or delete on public.items
  for each statement execute function public.bump_content_version('items');

alter table public.items enable row level security;
drop policy if exists items_public_read on public.items;
create policy items_public_read on public.items for select using (true);
