# Master-data → Supabase migration

Goal: stop hand-maintaining large JSON files. Edit master data in Supabase
(dashboard/SQL, with constraints for validation), then **publish the same JSON
back to the CDN** so the Flutter client stays completely unchanged (it still
reads `quest_*.json` etc. via its cache-then-CDN loader). This is the low-risk
"edit in DB → export to CDN" hybrid.

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
2. Run **`seed/quests_seed.sql`** to load the current 713 quests.
   Regenerate it any time from the JSON with:
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

## Roadmap (same pattern, one domain at a time)
Recommended order by maintenance pain / relational value:
`quests` (done) → `shop_inventory` → `raid_boss_event` / `quest_events`
(live/timed) → `items` → `skills` → `monsters` → `allies` → `npcs` → `dialogs`.

Keep as static JSON (small, structural): `xylos_factions`, `master_race`,
`class_list`, `biome_taxonomy`, `title_master`, `biome_*_mapping`, world-map
topology. Keep binary assets (`images/ sprites/ icons/ monsters/`) on the CDN.

> `shop_update.json` is unused — not migrated; safe to delete in a cleanup pass.
