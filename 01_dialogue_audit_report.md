# Dialogue Audit Report

Audit snapshot generated from current workspace files.

## Dataset

- NPC roster: 147 records.
- Quest dialogue: 701 records (698 faction quest and 3 other quest dialogs).
- Current quest JSON records: 712.
- Master dialogue trees: 31 across 3 legacy blocks; block sizes [0, 24, 7].
- Master metadata currently declares 254 quest and 279 total trees; this is stale against source files.

## Confirmed Structural Findings

- 7 quest dialogs reference missing NPC IDs across 7 unique IDs: npc_centurion_valka (99), npc_commander_vale (80), npc_director_vey (98), npc_don_mox (98), npc_elder_malakor (99), npc_high_seeker_voss (90), npc_warlord_steele (99).
- 85 NPCs point to a tree absent from the master.
- 701 quest dialogues contain multiple `accept_quest` actions; repository import code persists strings but does not establish idempotence.
- 6 non-terminal broken `next` references identified by direct graph inspection. The three `msq_lv*_reminder` references to `exit` have no declared terminal node.
- No duplicate quest dialog IDs, node IDs, or empty node texts were found in the current quest dialogue source.
- The master uses a legacy three-block array. Normalization must preserve all 31 existing NPC trees and compute metadata from the flattened result.

## Identity Decisions

- **Commander Lirien Vale vs Officer Valen:** keep distinct. Quest 001 contains explicit self-identification as Commander Lirien Vale, while roster defines Officer Valen. Create/retain distinct commander identity; reassign the erroneous first 20 dialogue references instead of renaming Officer Valen.
- **High Seeker Elara Voss:** map legacy `npc_high_seeker_voss` to `npc_arcanum_scholar` because the dialogue's full name matches the roster's Scholar Elara identity. Preserve the old ID as an alias.
- **Warlord Harkon Steele:** no roster match; create a separate NPC.
- **Don Vercelli Mox vs Revan “Ghost” Mox:** do not merge; distinct given names and no evidence of alias/kinship. Keep separate pending author confirmation.
- **Director Astra Vey:** map legacy `npc_director_vey` to roster `npc_omnicorp_class_trainer` based on exact full-name match; preserve legacy ID.
- **Elder Malakor:** no roster match; create a separate NPC.
- **Centurion Valka:** map legacy `npc_centurion_valka` to roster `npc_legion_class_trainer` based on exact name match; preserve legacy ID.

## Lore Classification

- Great Severance: established Aethelgardian Siphon overload catastrophe.
- Great Schism: later political split of Concordium leadership.
- Great Fracture: `CANON_REVIEW_REQUIRED`; only found as Old Man Kael wording in roster and not defined by the supplied canon.
- Meridian Cartel is the canonical faction name in faction data. “Meridian Compact” is not proven to be a historical predecessor; classify as a likely writing inconsistency and retain for author review before global replacement.
- Aethel Shard consciousness and any present-day deliberate intent are unresolved; dialogue may state them as belief or hypothesis only.

## Priorities

- **P0:** missing explicit `exit` targets in three level reminder dialogues; verify app terminal behavior before production migration.
- **P1:** seven missing quest giver identities, stale master metadata, and 85 NPC tree references.
- **P2:** repeated faction lore and quest acceptance actions; absent player-state responses.
- **P3:** individual voice variation and ambient civilian reactions.

## Limits

No dialogue runtime implementation was found in tracked app source; current import tooling stores JSON. State-aware conditions and flags therefore remain a proposal, not production fields. Great Fracture, Mox identity relationship, and the Meridian Compact label remain unresolved rather than invented.
