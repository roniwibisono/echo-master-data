# Dialogue Overhaul Status

## Narrative Improvements Delivered

1. Separated Commander Lirien Vale from Officer Valen using the explicit self-identification in the source dialogue.
2. Reconciled seven faction quest-giver IDs: three exact roster matches, four distinct/retained identities.
3. Added a canon glossary that separates established facts, faction interpretations, and unresolved terminology.
4. Added faction voice guidance for the seven playable factions, Custodians, AMA, and civilian roles.
5. Added profiles for major recurring NPCs and documented character-level voice needs.
6. Rewrote the complete 100-quest Concordium offer arc while retaining quest IDs and gameplay objective data.
7. Kept Great Severance and Great Schism as separate events and flagged Great Fracture for canon review.
8. Added 24 ambient conversations grounded in local work, routes, research, and community concerns; 22 condition-free conversations are active in NPC dialogue trees.
9. Added 14 rumors with source, region, and truth-status notes; 11 condition-free rumors are active in NPC dialogue trees.
10. Documented relationship and world-state dialogue as a future runtime capability instead of adding unsupported conditions; five condition-gated variants remain inactive.

## Technical Fixes Delivered

1. Added missing canonical NPC roster records for Commander Vale, Warlord Steele, Don Vercelli Mox, and Elder Malakor.
2. Mapped High Seeker Elara, Director Astra Vey, and Centurion Valka to roster IDs supported by name evidence; retained legacy aliases.
3. Preserved all 701 dialogue IDs and quest IDs.
4. Reduced every quest dialogue to exactly one `accept_quest` action.
5. Added a single confirmation step to three reminder quest flows that previously offered acceptance on multiple branches.
6. Synchronized current quest objective instructions for 598 non-Concordium faction offers; the Concordium pilot is sourced directly from each quest's objective records.
7. Added missing NPC dialogue tree entries while preserving the 31 existing master trees; cloned shared trees before adding NPC-specific world dialogue to prevent cross-NPC leakage.
8. Flattened the legacy master wrappers into the importer-supported wrapper and recomputed counts to 112 NPC trees plus 701 quest dialogs.
9. Added `validate_dialogues.py` and generated a current validation report.
10. Added structured JSON for ambient conversations, rumors, canonical identities, NPC profiles, and the proposed v2 schema.

## Remaining Risks and Work

1. The six non-Concordium faction arcs still contain repeated authored lore blocks; the validator reports these rather than replacing them with another mass paraphrase.
2. Concordium's 100-quest pilot still has repeated passages inherited from the source that need a line-by-line narrative pass.
3. Quest-state, relationship memory, and five conditional ambient/rumor lines cannot run until the game runtime evaluates conditions and flags.
4. Auto-added NPC master trees provide a functional fallback greeting/description, not bespoke character conversations.
5. Shared master tree IDs remain assigned to multiple NPCs for generic services; world-dialogue recipients have been split where needed.
6. The client runtime's handling of UI actions that point to absent nodes is undocumented; existing behavior is preserved and classified as action-terminal.
7. The AMA/NPC alias fields are documented in JSON, but the current SQL importer does not persist arbitrary NPC fields such as `legacy_aliases`.
8. Supabase seed SQL has been regenerated from JSON. It has not been applied to the remote database; the local stack could not start because Docker is unavailable.
9. “Meridian Compact” remains unverified as a historical organization or a naming error.
10. “Great Fracture” remains `CANON_REVIEW_REQUIRED` until an author decides whether it is a separate event, local term, or mistake.

## Validation Snapshot

- Dialogue validator: 0 structural errors, 58 warnings (generic shared NPC trees and repeated paragraphs).
- Faction quest validator: passes all seven 100-quest faction files with matching rewards and complete chains.
- General data validator: 0 errors; 7 warnings for neutral hub quests whose collection items are farmed elsewhere.
- JSON parsing and `git diff --check`: passed.
- Generated Supabase seed ID and chunk verification is implemented in `verify_supabase_seeds.py`.
- Current seeds: 151 NPCs, 813 dialogues, 719 quests; refreshed domain SQL is ready to apply. Remote Supabase was not modified.

This status is a completed Concordium pilot and data foundation, not a claim that every faction's full dialogue rewrite has reached final narrative acceptance.
