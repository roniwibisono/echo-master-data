# Dialogue Schema Documentation

Production files use `dialog_quests.json` as `{ dialogues: [...] }`. Each quest dialogue contains `dialog_id`, `quest_id`, `npc_id`, `start_node`, and `nodes`. Nodes use `id`, `text`, and `options`; options use `text`, `next`, and optional `action`. NPC trees live in the segmented `dialog_tree_master.json` array. NPC records reference them through `dialogue_tree`.

Observed production actions include `accept_quest` and `exit` in quest flows; master trees also use service actions such as `open_shop` and `currency_exchange`. No runtime implementation proving action idempotence or conditional state evaluation was found in this repository. Current import tooling stores node JSON without interpreting graph behavior.

Compatibility rule: preserve existing IDs and service action strings. Keep state-aware conditions in a separate proposal until a runtime consumer is confirmed. An `exit` with no target node is presently ambiguous; for migrated pilot dialogues prefer an explicit terminal node and document that the app's close behavior must be confirmed.
