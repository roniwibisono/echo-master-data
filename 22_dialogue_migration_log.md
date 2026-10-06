# Dialogue Migration Log

| Original | Changed / Decision | Reason | Affected IDs | Compatibility impact | Migration required? |
|---|---|---|---|---|---|
| `npc_concordium_officer` used for text introducing Commander Lirien Vale | Create distinct Commander Vale record; preserve Officer Valen | First-person identity conflicts with roster's distinct name and security role | `dialog_fq_conc_001` onward pending production update | Avoids changing existing Officer Valen ID | Yes, alias and dialogue reassignment |
| Seven missing quest giver IDs | Canonical mappings documented in `02_npc_canonical_map.json` | Name evidence supports three aliases; Steele, Don Vercelli Mox, and Malakor require separate identities | faction quest dialogue IDs using those NPCs | Preserve old references as legacy aliases | Yes |
| Master metadata 254/279 vs actual 701 + 31 | Mark stale; regenerate only after dialogue migration | Counts don't match source files | `dialog_tree_master.json` | Flatten legacy blocks carefully | Yes |
| Multiple accept actions in each quest graph | Pilot convention: one final action after confirmation | Runtime idempotence is unverified | 701 quest dialogues | Retains same action name | Yes, after engine behavior review |
| `Great Fracture` | Leave unresolved | Source does not define event | Old Man Kael dialogue | No canon change | No |
| `Meridian Compact` | Flag as likely terminology error; no silent replacement | No evidence of historical organization | Concordium dialogue mentioning term | Avoids deleting possible lore | Author review before global edit |

## Applied in Current Workspace

- Added canonical roster entries for Commander Lirien Vale, Warlord Harkon Steele, Don Vercelli Mox, and Elder Malakor. Existing IDs are retained for those entries.
- Remapped High Seeker Elara Voss, Director Astra Vey, and Centurion Valka to roster IDs supported by exact name matches. The former quest-dialogue IDs remain recorded as legacy aliases in the canonical map.
- Reassigned only `fq_conc_001` from Officer Valen to Commander Vale based on its explicit self-introduction; kept Officer Valen as a separate character.
- Added dialogue-tree records for NPC roster tree IDs that previously had no master entry, preserving pre-existing service action strings and leaving extra NPC gameplay actions untouched.
- Rewrote the 100 Concordium offer flows and synchronized their displayed targets/counts with the quest JSON. Their gameplay objective/reward records did not change.
- Synchronized offer instructions for the remaining 598 faction quest dialogues to their current quest objectives and faction voice line.
- Reduced each of the 701 quest dialogue flows to one `accept_quest` action. Three reminder quests now funnel acceptance through one confirmation node.
- Flattened the legacy three-block master into the importer-supported single wrapper and recomputed metadata from 112 NPC trees plus 701 quest dialogues.
- Integrated 28 condition-free ambient/rumor conversations into the live NPC dialogue trees and generated Supabase dialog seeds. Five variants remain proposal-only because they require quest/world-state resolution.

After confirming the dialog chunk files were tracked and unmodified, regenerated `npcs_seed.sql`, `dialogs_seed.sql` plus seven chunks, `quests_seed.sql` plus five chunks, and `supabase/apply_all.sql` from current JSON.

The database rows represented by these seeds are 151 NPCs, 813 dialogues, and 719 unique quests. Existing live database counts (147/732/713) are an older verified baseline; they have not been updated in this session.

No Supabase schema migration was needed: existing `npcs`, `dialogs`, and `quests` tables already hold these records. The local Supabase stack could not start because Docker is unavailable, so SQL was not applied to a database in this session.
