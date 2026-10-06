# Concordium Dialogue QA Report

## Scope

- 100 faction quest dialogues, `fq_conc_001` through `fq_conc_100`.
- Existing quest IDs, objective data, reward values, requirements, and quest-chain order were retained.
- Quest offer dialogue uses the authoritative objective target and count from its quest JSON.
- `accept_quest` appears once per dialogue, after the player reaches the confirmation step.
- Concordium quest 001 now uses Commander Lirien Vale's distinct NPC ID; Officer Valen remains unchanged in the NPC roster.

## Structural Results

- All 100 dialog IDs remain unique and tied to their quest IDs.
- All four pilot nodes (`greeting`, `lore`, `accept`, `exit`) are reachable.
- Every player response targets an existing node or uses the existing `exit` action terminal.
- No new runtime-only state fields were added.

## Narrative Review

- Opening text preserves the existing scene and field context instead of replacing the whole chain with one faction slogan.
- Lore responses combine the existing authored context with a staged character stake, with limits around what the current evidence proves.
- The campaign distinguishes Vale's field command from Valen's security liaison role.
- Great Severance remains the ancient Aethelgardian catastrophe; Great Schism remains a later political split.
- The Aethel Shard is not asserted to have a confirmed mind or to issue verified commands.

## Remaining Pilot Risks

- The current runtime contract has no verified quest-state conditions, so accepted, ready-to-turn-in, completed, and post-completion responses cannot safely be served in this production graph yet.
- The pilot still contains repeated source lore passages in some levels. The global validator reports exact repeated paragraphs separately; those require another authored pass before the narrative system meets the complete task's no-repetition target.
- Character relationship progression is specified as a runtime requirement, not implemented as an unsupported production field.

## Status

Pilot structure and gameplay references pass automated validation. Narrative quality has improved but is not at final acceptance until remaining repeated passages and runtime-backed completion/memory states are resolved.
