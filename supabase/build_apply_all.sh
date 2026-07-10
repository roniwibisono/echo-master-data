#!/usr/bin/env bash
# Regenerate supabase/apply_all.sql from the individual migration + seed files.
cd "$(dirname "$0")"
OUT=apply_all.sql
{
  echo "-- apply_all.sql — run ONCE in the Supabase SQL editor (schema 0001→0003, then seeds)."
  for f in migrations/0001_quests.sql migrations/0002_shops.sql migrations/0003_raid_events.sql migrations/0004_items.sql migrations/0005_skills.sql migrations/0006_monsters.sql migrations/0007_allies.sql \
           seed/quests_seed.sql seed/shops_seed.sql seed/raid_events_seed.sql seed/items_seed.sql seed/skills_seed.sql seed/monsters_seed.sql seed/allies_seed.sql; do
    echo; echo "-- ─── $f ───"; echo; cat "$f"; echo
  done
} > "$OUT"
echo "wrote $OUT ($(wc -l < "$OUT") lines)"
