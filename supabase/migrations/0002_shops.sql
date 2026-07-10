-- ═══════════════════════════════════════════════════════════════════════
--  Master-data migration 0002 — SHOPS
--  Moves shop_inventory.json (42 shops, 372 stocked items across 72 category
--  labels) into Supabase. Unlike quests (JSONB blob), shops are NORMALISED
--  into shops + shop_items so per-item stock / price can be tuned row-by-row
--  (the actual maintenance pain). export_shops.py re-nests rows into the exact
--  {meta, shops:[{categories:[{items}]}]} JSON the client reads (unchanged).
--  Run after 0001; requires the master_content_version helper from 0001.
-- ═══════════════════════════════════════════════════════════════════════

create table if not exists public.shops (
  id            text primary key,
  name          text not null,
  faction       text,
  buy_currency  text,
  description   text,
  sort_order    int not null default 0,
  updated_at    timestamptz not null default now()
);

create table if not exists public.shop_items (
  id             bigint generated always as identity primary key,
  shop_id        text not null references public.shops(id) on delete cascade,
  category       text not null,
  item_id        text not null,
  stock          int not null default 0,
  refresh_time   int not null default 0,
  price_modifier numeric not null default 1.0,
  sort_order     int not null default 0,
  updated_at     timestamptz not null default now(),
  unique (shop_id, category, item_id)
);

create index if not exists shop_items_shop_idx on public.shop_items (shop_id, sort_order);
create index if not exists shop_items_item_idx on public.shop_items (item_id);

-- touch updated_at (reuses touch_updated_at() from 0001)
drop trigger if exists shops_touch on public.shops;
create trigger shops_touch before update on public.shops
  for each row execute function public.touch_updated_at();
drop trigger if exists shop_items_touch on public.shop_items;
create trigger shop_items_touch before update on public.shop_items
  for each row execute function public.touch_updated_at();

-- bump the 'shops' content version on any change (reuses bump_content_version)
drop trigger if exists shops_bump_version on public.shops;
create trigger shops_bump_version after insert or update or delete on public.shops
  for each statement execute function public.bump_content_version('shops');
drop trigger if exists shop_items_bump_version on public.shop_items;
create trigger shop_items_bump_version after insert or update or delete on public.shop_items
  for each statement execute function public.bump_content_version('shops');

-- RLS: public read-only; writes only via service role.
alter table public.shops enable row level security;
drop policy if exists shops_public_read on public.shops;
create policy shops_public_read on public.shops for select using (true);

alter table public.shop_items enable row level security;
drop policy if exists shop_items_public_read on public.shop_items;
create policy shop_items_public_read on public.shop_items for select using (true);
