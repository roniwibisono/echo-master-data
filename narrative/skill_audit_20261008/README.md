# Skill catalogue audit — 8 October 2026

Duplicate cleanup and live Supabase seeding are complete. `skill_list.json` now contains 881 unique IDs, down from 1,004 rows. The 123 removed copies comprise 122 conflicting copies and one identical copy. The first occurrence was retained for every ID, matching `SkillRepository`; the complete ordered canonical definitions are identical before and after cleanup. This changes neither authored combat values nor the currently resolved skill definitions.

Recovery files: [original source](skill_list.before.json), [removed copies and original indices](removed_duplicates.json), and [pre-deployment live catalogue](live-skills.before.json). Recover any removed definition by its archived ID/index; do not replace the current source blindly after later authoring edits.

All 315 skill IDs referenced by the 88 classes resolve. The canonical catalogue contains 518 Active, 315 Passive and 48 Ultimate skills. Three Beastmaster usage references retain the legacy `mst_beastmaster` identifier, recorded with the client's `mst_beastExpert` alias. The `all` usage sentinel is accepted. Empty damage formulas are supported as zero by the existing engine; all 88 such canonical formulas remain intact.

The import tool now accepts Ultimate and legitimate empty formulas, and supports `--validate-only` without replacing global seed files. Duplicate IDs continue to fail import validation. [Audit/generator](../../tools/audit_skills.py) archives removed definitions and prepares [the dated seed](../../supabase/seed/skills_audited_20261008.sql). No historical/global seed or apply_all regeneration was performed.

## Live deployment and PostgreSQL verification

The dated seed ran as one transaction against **Echo Of Xylos**, project `fbntgtzimydjhuwedrjz`, at approximately 13:11 WIB on 8 October 2026. Every one of the 881 live rows matches the canonical authored fields; no class skill reference is missing. The canonical rows were already present from the prior deployment, so the upsert skipped identical rows. The ordered digest including `updated_at` remains `b029c62dd51d3d84bfac75f55f4ec42a`, confirming no existing skill row changed. Existing sort order is preserved, and no player table is targeted. See [live evidence](live-deployment.json).

Local PostgreSQL verification checked 17,339 authored fields, idempotence, actual changed-field updates, preservation of existing order and unrelated rows. See [SQL validation](sql-validation.json). The public-read live catalogue was also compared before cleanup: all 881 canonical definitions matched. JSON/CDN publication remains pending; no Git push was issued.

## Runtime findings requiring separate implementation

The audit fixtures now include all 48 Ultimate skills that were previously excluded. All 881 unique skills were simulated: 566 Active/Ultimate and 315 Passive. Passive simulations and the raid passive regression passed. The audit suite as a whole failed, so this release does not certify every skill mechanic as functional.

- Handler coverage identified **40 effect types used by 60 skills** without registered support. These include summons/structures, counters, shields/interception variants, next-attack effects, stealth, cooldown operations and status propagation. This is a runtime implementation gap, not a missing Supabase row.
- Three simulated casts reduced the caster's HP: **Last Wall** (`sk_bulwark_ult`), **Two of You** (`sk_paradox_ult`) and **Herald the Dark** (`sk_abyssherald_act_1`). These should be investigated with deterministic targeting tests. Single-run HP observations depend on combat RNG and are not an exhaustive list of unsafe targeting combinations.
- Healing warnings were observed for Sanctuary and Organism.
- The current PvE skill picker filters `type == active`; Ultimate skills need an explicit castability/UI decision before being considered playable there. Their data type was preserved rather than silently converted to Active.

Details: [machine-readable runtime findings](runtime-findings.json) and [full execution log](runtime-audit.log). Battle engine/runtime files were not modified. Follow-up work should add the missing mechanics and their targeted regressions, then rerun the complete audit including Ultimates.
