# Dialogue State Requirements

## Current Capability

The repository stores node graphs and action strings in JSON and imports them to `public.dialogs` as JSONB. NPC records store a `dialogue_tree` ID. No tracked runtime code was found that evaluates quest completion conditions, player flags, relationship tiers, or conditional node visibility. State-aware fields are therefore not added to production dialogue JSON.

## Minimum Runtime Contract

The dialogue runtime needs a read-only context containing active/completed quest IDs, faction reputation, region unlocks, class, and persistent player flags. It must evaluate dialogue conditions before showing a node or option and commit `set_flags` once per player interaction. Quest acceptance must be idempotent by `(player_id, quest_id)` or execute only after one explicit confirmation action.

## Proposed Condition Vocabulary

- `quest_state:<quest_id>=AVAILABLE|ACCEPTED|IN_PROGRESS|READY_TO_TURN_IN|COMPLETED`
- `quest_completed:<quest_id>`
- `flag:<flag_id>`
- `reputation:<faction_code>>=<integer>`
- `region_seen:<region_id>`
- `class:<class_id>`

## Memory and Relationship

Prefer event-derived facts over a free-form relationship score. Quest outcomes set durable flags such as `FLAG_HELPED_CONCORDIUM_GARDENS`; repeated successful interactions can derive a subtle trust tier. Do not expose a numeric relationship level unless the UI already supports it.

## Migration Safety

Keep production files on v1 fields until the runtime ships. The v2 schema is a proposal. Unsupported fields must not silently reach the importer because the app currently imports whole node JSON but may ignore unknown conditions.

## State Progression

Use `AVAILABLE`, `ACCEPTED`, `IN_PROGRESS`, `OBJECTIVE_PARTIAL`, `READY_TO_TURN_IN`, `COMPLETED`, `POST_COMPLETION`, `FAILED`, and `OPTIONAL_REVISIT` only where the quest state machine exposes them. Completion text should be served by the runtime after reward/turn-in, not shown at initial acceptance.
