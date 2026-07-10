# Master-data → Supabase migration

Goal: stop hand-maintaining large JSON files. Edit master data in Supabase
(dashboard/SQL, with constraints for validation), then **publish the same JSON
back to the CDN** so the Flutter client stays completely unchanged (it still
reads `quest_*.json` etc. via its cache-then-CDN loader). This is the low-risk
"edit in DB → export to CDN" hybrid.

## Apply everything (one paste)

`apply_all.sql` concatenates every schema migration + full seed in order —
but it's ~15 MB now, so it's for **psql/CLI only** (see Operational notes); it
exceeds the dashboard editor cap. In the dashboard, run each `migrations/000X.sql`
then the domain's chunked seed files. Regenerate apply_all with
`bash supabase/build_apply_all.sh`.

Alternatives: run each `migrations/000X.sql` then `seed/*.sql` individually, or
drop the migrations into your `supabase/migrations/` pipeline and `supabase db
push`. (DDL needs the service role / DB password / a linked CLI — the app's
anon key cannot create tables.)

## Pilot: Quests (8 files → 1 table)

`quest_list / arcanum / concordium / iron / legion / meridian / omnicorp /
shard / neutral / events` (713 quests) unify into `public.quests`. Nested
structures stay as **JSONB** (`quest_giver`, `requirements`, `objectives`,
`rewards`) so the `QuestTemplate` model is unchanged. `source_file` +
`sort_order` let the export tool rebuild the original files 1:1 (round-trip
verified: 713 quests, 0 value diffs).

### One-time setup
1. In the Supabase SQL editor, run **`migrations/0001_quests.sql`** (table +
   RLS public-read + content-version trigger).
2. Load the 713 quests. The full `seed/quests_seed.sql` (~1.5 MB) exceeds the
   SQL Editor's query-size cap, so **use the chunk files**: run
   `seed/quests_seed_part01.sql` … `part05.sql` in order (each ~300 KB). The
   single `quests_seed.sql` is fine for `psql`/CLI (no size limit).
   Regenerate all of them from the JSON with:
   `python3 supabase/tools/import_quests.py`

### Editing workflow (from now on)
1. Edit quests in the Supabase dashboard / SQL.
2. Publish back to the CDN:
   ```bash
   export SUPABASE_URL="https://<ref>.supabase.co"
   export SUPABASE_SERVICE_KEY="<service_role_key>"
   python3 supabase/tools/export_quests.py
   git add quest_*.json && git commit -m "content: quest edits" && git push
   ```
3. Bump the app's CDN refresh tag (`main.dart` → `refreshIfTagChanged('cdn-…')`)
   so every client re-pulls once on next launch.

`public.master_content_version` (domain `quests`) auto-increments on every
change — hook it into the app's `checkVersion` later if you move to querying
Supabase directly instead of the CDN.

## Shops (`shop_inventory.json` → 2 normalised tables)

42 shops / 372 stocked items → `public.shops` + `public.shop_items` (see
`migrations/0002_shops.sql`). Unlike quests, shops are **normalised** so per-item
`stock` / `price_modifier` / `refresh_time` are editable row-by-row. Setup: run
`0002_shops.sql` then `seed/shops_seed.sql` (regenerate via
`tools/import_shops.py`). Publish edits back with `tools/export_shops.py`
(re-nests rows into the exact `{meta, shops:[{categories:[{items}]}]}` file).
Round-trip verified: 42 shops, 372 items, 0 diffs.

## Raid events (`raid_boss_event.json` → `raid_events`)

Timed raid-boss definitions (currently 3) → `public.raid_events`
(`migrations/0003_raid_events.sql`). Scalars as columns; nested
`entry_requirements` / `spawn_monster_id` / `phases` / `clear_rewards` as JSONB.
Setup: run `0003` then `seed/raid_events_seed.sql` (regen via
`tools/import_raids.py`); publish with `tools/export_raids.py`. Round-trip
verified: 3 events, 0 diffs. `quest_events.json` is empty (0 quests) — already
round-tripped by the quests migration, no separate table yet.

## Items (`item_list.json` → `items`)

1146 entries → `public.items` (`migrations/0004_items.sql`). Scalars as columns;
`equipment_slots` / `stats_bonus` / `special_effects` as JSONB. Source file has
**37 duplicate ids** (20 identical, 17 with conflicting prices) — the client
builds its id→item map **last-wins**, so the seed keeps the last occurrence
(→ 1102 unique rows, matching runtime). `tools/import_items.py` prints the 17
conflicts to review + fix in the DB. Seed is chunked (`items_seed_part01..08.sql`,
~150 rows each) for the editor size cap; full `items_seed.sql` for psql. Publish
with `tools/export_items.py`. Round-trip vs runtime: 1102 items, 0 diffs.

## Skills (`skill_list.json` → `skills`)

688 skills (0 duplicate ids) → `public.skills` (`migrations/0005_skills.sql`).
Scalars as columns (`"range"` is quoted — reserved); the effect arrays +
`usage_requirements` as JSONB; `effect` is the legacy free-form blob kept
verbatim. Optional fields (`special_effects`, `usage_requirements`,
`target_attack`, `target_effect`, `arc_angle_degrees`) are NULL when absent and
omitted on export. Seed chunked (`skills_seed_part01..05.sql`). Tools:
`import_skills.py` / `export_skills.py`. Round-trip: 688 skills, 0 semantic diffs.

## Monsters (`monster_master.json` → `monsters`)

187 monsters (0 dup ids/codes) → `public.monsters` (`migrations/0006_monsters.sql`).
Scalars as columns; the list/dict fields (element, spawn_location, base_stats,
scaling, resistances, weaknesses, status_immunity, ai_pattern, skill_set,
drop_item, special_reward) as JSONB, with a **GIN index on `drop_item`** so
"which monster drops item X" is fast. Seed chunked (`monsters_seed_part01..03.sql`).
Tools: `import_monsters.py` / `export_monsters.py`. Round-trip: 187, 0 diffs.

## Allies (`ally_list.json` → `allies`)

91 allies (0 dup ids/codes) → `public.allies` (`migrations/0007_allies.sql`).
Scalars as columns; `base_stats` as JSONB. The `passive_skill`/`active_skill`
`{skill_id}` wrappers are flattened to `passive_skill_id` / `active_skill_id`
text columns (joinable to `public.skills`); `export_allies.py` re-wraps them.
Seed fits one file (`allies_seed.sql`, ~114 KB). Round-trip: 91 allies, 0 diffs.

## NPCs (`npc_list.json` → `npcs`)

147 NPCs (0 dup ids) → `public.npcs` (`migrations/0008_npcs.sql`). Scalars as
columns; `available_services` / `actions` as JSONB; 7 optional text fields are
NULL-when-absent, omitted on export. Seed fits one paste (`npcs_seed.sql`,
~208 KB). Tools: `import_npcs.py` / `export_npcs.py`. Round-trip: 147, 0 diffs.
**`npc_additions.json` is NOT migrated** — the client only adds additions whose
id isn't already in npc_list, and all 28 addition ids overlap it, so it adds
zero NPCs at runtime (15 of the overlaps *differ* — intended patches the client
silently ignores; worth cleaning up separately).

## Dialogs (`dialog_tree_master.json` + `dialog_quests.json` → `dialogs`)

732 dialogs (31 generic/NPC + 701 quest; `dialog_id` globally unique, 0 dups/
overlap) → `public.dialogs` (`migrations/0009_dialogs.sql`). The `nodes`
conversation tree is JSONB; `source_file` + `sort_order` round-trip to the two
files. `getDialogForQuest` maps to a `quest_id` index. Seed chunked
(`dialogs_seed_part01..07.sql`). Tools: `import_dialogs.py` / `export_dialogs.py`
(dialog_tree_master exports as a single `{dialogues:[…]}` wrapper — the client
flattens it; the empty wrapper + a doc `meta` block are dropped). Round-trip:
732 dialogs, 0 semantic diffs. **Migration roadmap complete.**

## Operational notes
- **JSONB reorders keys.** A round-trip through a `jsonb` column normalises key
  order + whitespace, so `export_*.py` output is *semantically identical* but
  textually reordered vs the original hand-formatted files (verified: quests
  713 rows, 0 semantic diffs). The client reads by key name, so this is
  harmless — the exported file becomes the new canonical CDN format the first
  time you publish a real edit.
- **`apply_all.sql`** (schema + full seeds) is ~7 MB → for **psql/CLI only**;
  it exceeds the dashboard SQL-editor cap. In the dashboard, run the per-file
  migrations + the chunked seeds.

## Roadmap (same pattern, one domain at a time)
Recommended order by maintenance pain / relational value:
`quests` (done) → `shops` (done) → `raid_events` (done) → `items` (done) →
`skills` (done) → `monsters` (done) → `allies` (done) → `npcs` (done) → `dialogs` (done). ALL DONE ✅

Keep as static JSON (small, structural): `xylos_factions`, `master_race`,
`class_list`, `biome_taxonomy`, `title_master`, `biome_*_mapping`, world-map
topology. Keep binary assets (`images/ sprites/ icons/ monsters/`) on the CDN.

> `shop_update.json` is unused — not migrated; safe to delete in a cleanup pass.
