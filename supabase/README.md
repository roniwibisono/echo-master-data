# Master-data → Supabase migration

Goal: stop hand-maintaining large JSON files. Edit master data in Supabase
(dashboard/SQL, with constraints for validation), then **publish the same JSON
back to the CDN** so the Flutter client stays completely unchanged (it still
reads `quest_*.json` etc. via its cache-then-CDN loader). This is the low-risk
"edit in DB → export to CDN" hybrid.

## Apply everything (one paste)

Fastest path — open the **Supabase SQL editor** and run **`apply_all.sql`**
(schema `0001→0003` + all three seeds, in the correct order). Regenerate it
after any change with `bash supabase/build_apply_all.sh`.

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
`skills` (done) → `monsters` → `allies` → `npcs` → `dialogs`.

Keep as static JSON (small, structural): `xylos_factions`, `master_race`,
`class_list`, `biome_taxonomy`, `title_master`, `biome_*_mapping`, world-map
topology. Keep binary assets (`images/ sprites/ icons/ monsters/`) on the CDN.

> `shop_update.json` is unused — not migrated; safe to delete in a cleanup pass.
