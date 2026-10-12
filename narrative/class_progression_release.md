# Class trials release — 8 October 2026

The migration and dated delta seed were deployed to live Supabase **Echo Of Xylos** (`fbntgtzimydjhuwedrjz`) at 10:52–10:54 WIB on 8 October 2026, following the user's explicit deployment request. Recorded remote migration version is `20261008035249`; the local migration filename is aligned with it. All 519 upserted rows match the prepared seed, references resolve, 28 trials and proof items are present, and existing monster rows retain their original digest. The anonymous REST API returns all 88 classes with their descriptions and activation flags. A snapshot of affected pre-existing master rows is saved in the app QA directory; no player rows were modified.

Evidence: [live deployment](/Users/rnddev/Documents/project-echo/docs/qa/2026-10-08-class-progression/live-deployment.json), [REST check](/Users/rnddev/Documents/project-echo/docs/qa/2026-10-08-class-progression/live-rest-validation.json), [master-row snapshot](/Users/rnddev/Documents/project-echo/docs/qa/2026-10-08-class-progression/live-master-before.json). Git/CDN publication remains pending. The installed simulator app contains the matching release pack and can be used for trainer-flow acceptance now.

1. Review `narrative/class_progression_validation.json` and the 28 trials in `quest_list.json`, their `dialog_quests.json` nodes and proof items. Level gates are Base 5, Advance 20, Expert 40 and Master 60. Runtime app code uses the same thresholds.
2. For another existing environment, apply only `supabase/migrations/20261008035249_class_trial_progression.sql` after existing quests/items/skills/monsters/npcs/dialogs schemas. It creates the public-read classes table with RLS, SELECT-only anon/authenticated grants and the quests `auto_accept` field. Do not rerun historical destructive schema files against production. Take the usual database backup and review the target environment before deployment. This migration is already applied to Echo Of Xylos live.
3. Apply `supabase/seed/class_progression_20261008.sql` in one transaction. This delta upserts 88 classes, 28 proof items, 28 trainers, 31 quests (28 trials and 3 corrected tutorials), 29 dialogs and 315 unique class skill definitions. It fills only absent monster definitions; it does not change existing enemy balance. Four retired quest definitions/dialogs are removed; player rows, saved histories and inventory are not deleted or migrated.
4. Export existing catalogues with their existing `supabase/tools/export_*.py` tools; classes use the new `export_classes.py`, mapping `is_active` back to integer `isActive` and preserving description. Quest import/export now round-trips `auto_accept`. Inspect the diff before publication. Existing migrations or backend player schemas are not changed by an export.
5. Publish reviewed JSON files through the project's normal master-data/CDN process. **`world_map_v4.json` is JSON-owned**; publish the updated capital NPC placements directly, because there is no Supabase world-map table/exporter. Also publish `class_list.json`, `npc_list.json`, `item_list.json`, `skill_list.json`, `quest_list.json`, `dialog_quests.json` and `dialog_tree_master.json` from this release. Retired pointers in faction quest files have been removed where present. Refresh the normal content tag/cache according to project practice.
6. Ship the matching app release, which contains `assets/data/class_progression_pack.json`. Test with an unassigned Level 4/5 account and existing Base/Advance/Expert/Master accounts. Verify return/restart, repeat report taps, missing proof recovery and Axiom links to Profile. Keep legacy class history intact.

## Regenerate and check locally

From project-echo: `python3 tools/build_class_progression.py` authors the narrative and rebuilds identical client/master packs. From this repo: `python3 validate_class_progression.py` and `python3 supabase/tools/build_class_progression_seed.py` validate and generate SQL. These scripts do not connect to Supabase.

SQL verification uses PostgreSQL through PGlite; no service keys are needed. Example (replace roots if necessary):

```sh
npm install --prefix /tmp/echo-class-pg @electric-sql/pglite
cp supabase/tools/verify_class_progression.mjs /tmp/echo-class-pg/verify.mjs
node /tmp/echo-class-pg/verify.mjs "$PWD" /tmp/class-progression-sql-validation.json
```

The verifier applies prerequisites to a fresh local database, executes the delta twice, checks references, export parity, anonymous read/write policy and preservation of unrelated items/existing monster stats. This verifies SQL in PostgreSQL; it is not evidence that migration/seed has been deployed to the remote Supabase project.

No global seed/apply_all regeneration was performed: the dated delta is the reviewed entry point. Secrets should use existing environment configuration and are not included in these files.
