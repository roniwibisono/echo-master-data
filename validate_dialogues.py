#!/usr/bin/env python3
"""Validate quest and NPC dialogue references without assuming runtime behavior."""

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
QUEST_DIALOGS = ROOT / "dialog_quests.json"
MASTER = ROOT / "dialog_tree_master.json"
NPCS = ROOT / "npc_list.json"
QUEST_FILES = [
    "quest_concordium.json", "quest_arcanum.json", "quest_iron.json",
    "quest_meridian.json", "quest_omnicorp.json", "quest_shard.json",
    "quest_legion.json", "quest_neutral.json",
]
KNOWN_ACTIONS = {
    "accept_quest", "take_quest", "exit", "open_shop", "open_crafting", "rest", "rest_inn",
    "currency_exchange", "open_banking", "open_bank", "open_class_change", "open_bounty",
    "open_quest_board", "open_skill_training", "open_upgrade", "open_guide", "open_world_info", "open_lore",
}
ALLOWED_UI_TERMINALS = KNOWN_ACTIONS


def load(path):
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def main():
    errors, warnings = [], []
    quest_dialog_data = load(QUEST_DIALOGS)
    dialogues = quest_dialog_data.get("dialogues", [])
    npc_list = load(NPCS)
    npc_by_id = {npc.get("npc_id"): npc for npc in npc_list}
    quest_ids = {
        quest.get("id")
        for filename in QUEST_FILES
        for quest in load(ROOT / filename).get("quests", [])
    }
    quest_ids.update(q.get("id") for q in load(ROOT / "quest_list.json").get("quests", []) if q.get("id"))
    master_blocks = load(MASTER)
    master_dialogues = [dialogue for block in master_blocks for dialogue in block.get("dialogues", [])]
    master_by_id = {dialogue.get("dialog_id"): dialogue for dialogue in master_dialogues}

    dialog_counts = Counter(dialogue.get("dialog_id") for dialogue in dialogues)
    for dialog_id, count in dialog_counts.items():
        if not dialog_id or count > 1:
            errors.append(f"duplicate or empty quest dialog_id: {dialog_id!r} ({count})")

    npc_tree_counts = Counter(npc.get("dialogue_tree") for npc in npc_list if npc.get("dialogue_tree"))
    for tree_id, count in npc_tree_counts.items():
        if count > 1:
            warnings.append(f"dialogue_tree {tree_id} is shared by {count} NPCs")

    for npc in npc_list:
        tree_id = npc.get("dialogue_tree")
        if tree_id and tree_id not in master_by_id:
            warnings.append(f"NPC {npc.get('npc_id')} references missing master tree {tree_id}")

    all_actions = Counter()
    for dialogue in dialogues:
        dialog_id = dialogue.get("dialog_id", "<missing-id>")
        quest_id = dialogue.get("quest_id")
        npc_id = dialogue.get("npc_id")
        if npc_id not in npc_by_id:
            errors.append(f"{dialog_id}: missing NPC {npc_id}")
        if quest_id not in quest_ids:
            warnings.append(f"{dialog_id}: quest reference not present in current quest JSON: {quest_id}")
        nodes = dialogue.get("nodes", [])
        node_ids = [node.get("id") for node in nodes]
        node_map = {node.get("id"): node for node in nodes}
        if len(node_ids) != len(set(node_ids)):
            errors.append(f"{dialog_id}: duplicate node IDs")
        if dialogue.get("start_node") not in node_map:
            errors.append(f"{dialog_id}: missing start_node {dialogue.get('start_node')}")
        for node in nodes:
            if not str(node.get("text", "")).strip():
                errors.append(f"{dialog_id}/{node.get('id')}: empty text")
            for option in node.get("options", []):
                action = option.get("action", "")
                if action:
                    all_actions[action] += 1
                    if action not in KNOWN_ACTIONS:
                        warnings.append(f"{dialog_id}/{node.get('id')}: undocumented action {action}")
                target = option.get("next")
                if target and target not in node_map:
                    if action in ALLOWED_UI_TERMINALS:
                        continue
                    errors.append(f"{dialog_id}/{node.get('id')}: broken next={target!r}")
        reached, queue = set(), [dialogue.get("start_node")]
        while queue:
            node_id = queue.pop()
            if node_id in reached or node_id not in node_map:
                continue
            reached.add(node_id)
            queue.extend(option.get("next") for option in node_map[node_id].get("options", []) if option.get("next") in node_map)
        unreachable = set(node_map) - reached
        if unreachable:
            warnings.append(f"{dialog_id}: unreachable nodes {sorted(unreachable)}")
        accept_count = sum(option.get("action") == "accept_quest" for node in nodes for option in node.get("options", []))
        if accept_count > 1:
            warnings.append(f"{dialog_id}: {accept_count} accept_quest actions; runtime idempotence is unverified")
        for node in nodes:
            for option in node.get("options", []):
                if option.get("action") == "accept_quest" and option.get("next") in node_map:
                    continue
                if option.get("action") == "accept_quest" and option.get("next") not in node_map and option.get("action") not in ALLOWED_UI_TERMINALS:
                    warnings.append(f"{dialog_id}: accept action ends at undeclared node {option.get('next')!r}")

    master_ids=Counter(d.get("dialog_id") for d in master_dialogues)
    for dialog_id,count in master_ids.items():
        if not dialog_id or count>1:
            errors.append(f"duplicate or empty master dialog_id: {dialog_id!r} ({count})")
    for dialogue in master_dialogues:
        dialog_id=dialogue.get("dialog_id","<missing-id>")
        if dialogue.get("npc_id") not in npc_by_id:
            errors.append(f"master {dialog_id}: missing NPC {dialogue.get('npc_id')}")
        nodes=dialogue.get("nodes",[])
        node_map={node.get("id"):node for node in nodes}
        if dialogue.get("start_node") not in node_map:
            errors.append(f"master {dialog_id}: missing start_node {dialogue.get('start_node')}")
        for node in nodes:
            if not str(node.get("text","")).strip():
                errors.append(f"master {dialog_id}/{node.get('id')}: empty text")
            for option in node.get("options",[]):
                action=option.get("action","")
                if action and action not in KNOWN_ACTIONS:
                    warnings.append(f"master {dialog_id}/{node.get('id')}: undocumented action {action}")
                target=option.get("next")
                if target and target not in node_map and action not in ALLOWED_UI_TERMINALS:
                    errors.append(f"master {dialog_id}/{node.get('id')}: broken next={target!r}")
        reached,queue=set(),[dialogue.get("start_node")]
        while queue:
            node_id=queue.pop()
            if node_id in reached or node_id not in node_map: continue
            reached.add(node_id)
            queue.extend(op.get("next") for op in node_map[node_id].get("options",[]) if op.get("next") in node_map)
        unreachable=set(node_map)-reached
        if unreachable:
            warnings.append(f"master {dialog_id}: unreachable nodes {sorted(unreachable)}")

    meta = [block.get("meta") for block in master_blocks if block.get("meta")]
    if meta:
        declared = meta[0]
        quest_count = sum(d.get("quest_id") is not None for d in master_dialogues)
        total_count = len(master_dialogues) + len(dialogues)
        if declared.get("quest_dialog_count") != len(dialogues):
            warnings.append(f"master quest_dialog_count={declared.get('quest_dialog_count')} but dialog_quests has {len(dialogues)}")
        if declared.get("total_count") != total_count:
            warnings.append(f"master total_count={declared.get('total_count')} but flattened total is {total_count}")

    duplicates_text = defaultdict(list)
    for dialogue in dialogues:
        for node in dialogue.get("nodes", []):
            text = " ".join(str(node.get("text", "")).split())
            if len(text) > 50:
                duplicates_text[text].append(f"{dialogue.get('dialog_id')}/{node.get('id')}")
    repeated = [(text, refs) for text, refs in duplicates_text.items() if len(refs) >= 3]
    for text, refs in repeated:
        warnings.append(f"exact paragraph repeated {len(refs)} times: {text[:110]!r}")

    lines = ["# Dialogue Validation Report", "", f"Source quest dialogues: {len(dialogues)}", f"NPC records: {len(npc_list)}", f"Master NPC trees: {len(master_dialogues)}", f"Current quest IDs: {len(quest_ids)}", "", f"Errors: {len(errors)}", f"Warnings: {len(warnings)}", "", "## Errors", ""]
    lines.extend(f"- {entry}" for entry in errors or ["None"])
    lines.extend(["", "## Warnings", ""])
    lines.extend(f"- {entry}" for entry in warnings or ["None"])
    lines.extend(["", "## Actions", "", "```json", json.dumps(all_actions, indent=2), "```", ""])
    rendered="\n".join(lines)
    (ROOT / "dialogue_validation_report.md").write_text(rendered, encoding="utf-8")
    (ROOT / "21_dialogue_validation_report.md").write_text(rendered, encoding="utf-8")
    print(f"{len(errors)} error(s), {len(warnings)} warning(s); report: dialogue_validation_report.md")
    if errors:
        for error in errors:
            print(f"ERROR {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
