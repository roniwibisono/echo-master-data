# Skill Memory

## Artisan Scope and Dummy Skill (2026-10-13)

Update: learned Dummy Skill upgrades consume one Small HP Cell per level
directly from Battle Skill Setup, with confirmation and no battle objectives or
CRD cost. Old test-training templates remain for compatibility; `dummy_upgrade`
is now the preferred path. Initial learning still requires a single PvE victory
and Ivara turn-in. Battle Skill Setup configures Memory slots only; class skills
are unchanged. Potion consumption and mastery increment commit atomically.

Ivara offers only explicitly assigned `SKILL_MEMORY` recipes. Generic `ALL`
recipes are excluded and the Upgrade/Shop service selector is hidden. Five
supporting weapon recipes have moved to `npc_master_blacksmith`.

`Dummy Skill` (`sk_mem_dummy_skill`, `mem_dummy_skill`, `rcp_mem_dummy_skill`)
is an additional QA technique: craft from one `con_small_hp_cell` (Small HP Cell /
HP potion), zero CRD, one-second craft. It deals 10% ATK, costs zero MP, and accepts
any weapon. Learn it with one PvE win; each mastery step requires one effective
use, one PvE win, and Ivara's turn-in. Low-level PvE qualifies ONLY for this
explicitly marked test skill. PvP, training-dummy enemies, ineffective casts,
and replayed events remain excluded. Normal Memory objectives are unchanged.
There are now 21 Memory skills/items/recipes and 189 upgrade templates.

Status: learning, loadout, training and mastery runtime implemented and tested in
the client; compatible iOS Simulator build is the requested release target.
Hosted catalog and co-op migrations are applied. Public store distribution is
not part of this release. Earlier phase sections below are implementation history.

## P0: Contract

`skill_memory_contract.json` is the normative versioned contract. Each player or
party member owns independent learning attempts, learned levels and memory loadout.
Two base memory slots are separate from class skills. Only eligible non-memory
passives can increase capacity; memory skills cannot grant their own slots.

Using one item must atomically consume it and create the selected learner's quest.
Reject duplicate learning and replayed requests before inventory changes. A failed
quest creation rolls everything back. Abandoning pauses the same quest without a
refund. Completion unlocks level 1. Learning many skills does not equip them all.

Weapon family is the explicit `WEAPON_` type suffix, never inferred from item names.
Match the required family in either equipped hand; recheck at equip and cast time.
Changing to an incompatible weapon keeps the loadout but disables the skill.
Loadout changes are out of combat only. Legacy class skills remain unaffected.

Mastery caps at level 10. Potency rises by 6% of level-1 potency per level, reaching
154% at level 10. Do not multiply durations, proc rates, penetration, lifesteal,
debuff strengths, hit counts, MP costs or slots. Profiles specify scalable special
effects. Percent-ATK DoTs scale their value; percentage regeneration scales its value.
Rounding occurs only after calculating the final amount.

Learning quests require 3/5/8 qualifying weapon victories by tier, then artisan
turn-in. They never require casting the not-yet-learned skill. Each upgrade requires
its own training quest; the current level remains available while training. Record
actor, action, battle and attempt identities to prevent replay or party attribution
errors. Only meaningful effects count, excluding dummies and PvP.

Unused crafted items are tradable. Consuming one binds the lesson, not a tradable
trained item. Learned skills and progression cannot be transferred or listed.

## P1: Catalog

20 new skills, 20 Skill Memory items and 20 recipes are merged into the existing
canonical files. `skill_memory_pack.json` also contains cross-linked progression
profiles and the Ivara artisan dialog. Tier I/II/III require learner/crafting levels
20/40/60, with increasing ingredient quantities, fees and production times.

Ivara is a CRAFTER at Central Spire Bazaar. Only this artisan may craft the pack.
All materials and the placeholder memory-chip icon reuse existing master assets.
Item type SKILL_MEMORY deliberately avoids the legacy consumable handler; the
dedicated P2 inventory action now selects the learner and creates a lesson. Dialog
training branches are informational; no nonexistent training handler is called.

Some weapon families do not yet exist in the equipment catalog. The family list
is a contract for P3, not a claim that every listed weapon is currently obtainable.
Learning quests are created as learner-bound definition snapshots when a memory
is consumed, not free-to-accept catalog quests. Mastery quests are still templates.

## P2: Local Learning Runtime

One journal atomically persists item consumption and the new learning quest.
Repeated request IDs return the original lesson; different requests for the same
learner/skill are rejected. Legacy consumable and battle item paths still reject
memories. Saved `skill_memory_levels` maps on player and allies hold learned levels
without adding skills to the legacy learned/class battle resolver before P3.

Quest IDs include learner identity. Pausing through Abandon keeps the lesson,
progress and receipt; Resume appears in the available list without another memory.
Only victories from the Explore PvE result path count. The learner must survive,
have the exact weapon subtype and fight an enemy no more than ten levels below
their level. Battle receipts prevent repeat credit. Returning to Ivara after the
victories requires a real interaction in Central Spire Bazaar; generic quest events
and auto-completed soft objectives cannot bypass the lesson.

Learning completion journals the Lv1 unlock with quest completion, including ally
state when appropriate. Revisioned lesson snapshots reject stale progress saves.
The item repository now pages through Supabase `items` as the canonical database
source, after the legacy `game_items` merge; published manifest definitions retain
priority. Inventory also resolves DB-only items rather than requiring a CDN entry.
Raid/PvP progression and Lv2-Lv10 training are outside P2. New Skill Memory items,
skills, recipes and Ivara have not yet been seeded/published to the live database.

## P3: Local Loadout and Battle Runtime

Each learner persists `equipped_memory_skill_ids` separately from class loadouts.
Two base slots plus eligible class/race/ally/equipment passive bonuses determine
capacity. Duplicate passive IDs count once; Memory skills cannot grant capacity.
Conditional, active and non-equipment effects are excluded. Missing data never
silently authorizes a memory. Each learned memory remains in the ability archive
whether equipped or not, without being mislabeled as an equipment grant.

The Profile Skills tab and party Skills detail expose learner-bound loadouts.
Mutations are journaled, limited to known learned skills and blocked during battle.
Weapon swaps retain saved slots but disable incompatible skills. Losing bonus
capacity disables trailing slots without deleting the saved selection. Existing
class skill resolution is retained; only valid equipped memories join battle lists.

Combatants carry explicit weapon families and authorized Memory IDs. ACT commit,
resolution and the shared SkillLibrary recheck before spending MP or applying
effects. Actor render snapshots preserve this context. Unsupported/old contexts
fail closed for memories, without changing legacy class skill behavior.

Co-op member metadata uses optional `memory_context` and ACT client protocol 2.
The additive `raid_skill_memory_context` migration preserves old rows and RLS,
requires string arrays, bounds payload size and enforces that Memory IDs occur in
the submitted skill list. A Memory raid requires protocol-2 participants. Clients
fall back to protocol 1 on an unupgraded server only when no memory is requested.
Participant stats/context retain the existing client/host authority; this does
not constitute server-side proof of learning or a new anti-cheat boundary.

The migration has been replayed on a disposable synthetic PostgreSQL instance;
it has NOT been applied to the hosted database. Publish the data and migrations
with the compatible client before enabling Memory content. Catalog coverage still
needs explicit weapons for Knuckle/Orb/Grimoire/Polearm and a compatible Shield tag;
legacy OFFHAND remains unchanged and is not guessed from item names.

## P4: Local Training Foundation

The pack now contains 180 learner-bound upgrade templates, nine per skill. They
are not added to the public quest catalog. Skills carry an explicit
`skill_memory_tier`; the client fails closed when that metadata is missing rather
than guessing the tier from a name or level requirement.

`SkillMemoryService.startTraining` binds the next level to an owned learner. It
does not consume another memory or change the usable level. Paused attempts must
resume rather than create another quest. Request replay returns the same quest.
Meaningful-use receipts are bound to the attempt, battle and action; victories
have their own objective and receipt list. Empty/no-effect, wrong-weapon, dead,
weak-enemy and ineligible combat receipts are ignored. Actual shield absorption,
not shield grants, is the intended event input.

Ivara requires both objectives before reviewing training. Turn-in compares the
learner's current level with the attempt's original level and atomically saves
the next level plus quest completion. Replays cannot raise the level again.
Player and ally progress remain independent; skill levels cannot exceed ten.

The internal `recordTrainingUse` API is tested but is NOT yet called by combat.
Do not expose a Train action or publish these memories until structured combat
outcomes (including shield attribution), potency scaling, and UI integration are
ready. Receipt inputs retain existing client authority; they are not a new
server-side anti-cheat guarantee. No live database or CDN publication was made
for this training foundation during its initial implementation.

## Hosted Data Publication (2026-10-12)

The `skill_memory_catalog` migration and generated scoped seed have now been
applied to Echo Of Xylos (`fbntgtzimydjhuwedrjz`). Twenty Memory items are in
`public.items`, twenty skills (including explicit tier) are in `public.skills`,
and Ivara and the dialogue are in `public.npcs` and `public.dialogs`.
`public.skill_memory_catalog` stores the complete pack, including twenty recipes,
profiles, trading/binding metadata, the contract, and 180 training templates.
The table has RLS and read-only client grants; only privileged writers may seed it.

No training templates were inserted into `public.quests`, no player progression
was modified, and unrelated master rows were checked inside the seed transaction.
The seed and permissions were also rehearsed locally before hosted execution.
The pack's `runtime_ready=false` is rollout metadata, NOT a feature gate enforced
by old clients. Publishing data does not build or release the Flutter client.
Recipes still use the client's existing CDN path; the new catalog needs a client
consumer before it can replace that path. Full training remains unimplemented.
The co-op Memory migration in the client checkout was not applied in this data
publication. Earlier sections describing unpublished data reflect the pre-release
implementation stages; this section is the current publication record.

## Remaining Priority

- P2 local implementation: done; live data publication remains a release step.
- P3 local implementation: done; deploy co-op migration and audit weapon coverage.
- P4 data/service: done locally; wire structured combat receipts, level scaling
  and training UI before enabling upgrades.
- P5: enforce unused-item market eligibility server-side.
- P6: learner list, equip/training UI, migrations and end-to-end regression tests.

Publishing must respect content activation. Do not mark runtime capability ready
until those handlers exist. JSON metadata is not a substitute for runtime gating.

## Simulator Runtime Activation (2026-10-12)

This section supersedes the historical pending flags above. Training can be
started/resumed from the player's or party member's Memory panel. Qualifying
Explore PvE actions are recorded as structured outcomes (never log parsing),
deduplicated and capped to the remaining objective, then committed once at battle
exit. PvP/dummy encounters do not grant training progress. Worthy victories and
Ivara's review remain independent objectives. Class skills are unchanged.

Combatants carry mastery through player/ally/war/raid/siege/Conclave builders and
raid snapshots. Context protocol 2 includes integer levels 1..10; old Memory
contexts remain level-one compatible but cannot host protocol-2 contexts.
Potency is `1 + 0.06 * (level - 1)`: damage formulas, authored ATK DoT, Echo Mend's
direct/periodic healing, and Memory shields scale. Proc chances, debuff magnitude,
duration, MP, cooldown and hit count are unchanged. Shields credit training only
on actual absorption. Refreshing a live ward does not grant another use.

Five explicit equipment families now have obtainable artisan recipes:
Knuckle, Orb, Grimoire, Polearm, Shield. Existing equipment is not reclassified.
The client reads the scoped Supabase pack once per startup, caches it for offline
reuse, and merges only Memory content; Ivara's placement and generic dialogue do
not depend on a fresh CDN cache. Existing activation overrides retain priority.

The hosted pack now has `runtime_ready=true`, twenty memories/skills/recipes,
five weapons and recipes, and 180 learner-bound templates. This metadata means
the compatible client implements the runtime; it does not update installed apps.
Validation: 91 focused Flutter regressions, 16 master-data/seed tests, disposable
PostgreSQL validation of both co-op migrations, and iOS Simulator debug builds.
No real player was granted test items or mastery for validation.

Unused Memory items follow the existing inventory/trading system; consuming one
removes it and persists a learner-bound quest, not a transferable inventory
object. This feature does not replace the existing client-authoritative inventory
and market with a new server-authoritative anti-cheat protocol. Store rollout and
that broader server hardening require separate release work; zero bugs are not
guaranteed by these tests.

## Rebuild and Validate

```sh
python3 tools/build_skill_memory.py
python3 tools/build_skill_memory.py --check
python3 -m unittest discover -s tools -p 'test_skill_memory.py'
python3 validate_data.py
```

Client regression coverage includes `test/skill_memory_learning_test.dart`,
`test/crafting/canonical_item_loading_test.dart`, and
`test/ui/skill_memory_learner_picker_test.dart` in the game checkout.

P3 coverage adds `test/skill_memory_loadout_test.dart` and
`test/ui/skill_memory_loadout_panel_test.dart`. The client checkout's
`tools/skill_memory_schema_rehearsal.py` validates the additive co-op migration
without touching a hosted project or player records.

P4 foundation coverage adds `test/skill_memory_training_test.dart` (eight tests),
including failed saves, replay protection, sequential upgrades, eligibility,
pause/resume and independent ally mastery. The data suite covers all 180 templates.

The builder uses structured JSON merges, preserves non-pack records and is
idempotent. `--check` verifies files without writing. No backups or caches belong
in the published pack.
