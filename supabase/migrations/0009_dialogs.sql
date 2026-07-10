-- ═══════════════════════════════════════════════════════════════════════
--  Master-data migration 0009 — DIALOGS  (final domain)
--  dialog_tree_master.json (31 generic/NPC dialogs) + dialog_quests.json
--  (701 quest dialogs) → public.dialogs. 732 total, dialog_id globally unique
--  (0 dups, 0 cross-file overlap). The `nodes` conversation tree is JSONB.
--  `source_file` + `sort_order` round-trip to the two files; the client
--  flattens both, so dialog_tree_master exports as a single {dialogues:[…]}
--  wrapper (the empty wrapper + a doc `meta` block are dropped — cosmetic).
--  Run after 0001.
-- ═══════════════════════════════════════════════════════════════════════

create table if not exists public.dialogs (
  dialog_id    text primary key,
  quest_id     text,                       -- only on quest dialogs
  npc_id       text,
  start_node   text,
  nodes        jsonb not null default '[]'::jsonb,
  source_file  text,
  sort_order   int not null default 0,
  updated_at   timestamptz not null default now()
);

create index if not exists dialogs_quest_idx  on public.dialogs (quest_id);
create index if not exists dialogs_npc_idx     on public.dialogs (npc_id);
create index if not exists dialogs_source_idx  on public.dialogs (source_file, sort_order);

drop trigger if exists dialogs_touch on public.dialogs;
create trigger dialogs_touch before update on public.dialogs
  for each row execute function public.touch_updated_at();

drop trigger if exists dialogs_bump_version on public.dialogs;
create trigger dialogs_bump_version after insert or update or delete on public.dialogs
  for each statement execute function public.bump_content_version('dialogs');

alter table public.dialogs enable row level security;
drop policy if exists dialogs_public_read on public.dialogs;
create policy dialogs_public_read on public.dialogs for select using (true);
