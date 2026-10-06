#!/usr/bin/env python3

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FILES = [
    "quest_concordium.json",
    "quest_arcanum.json",
    "quest_iron.json",
    "quest_meridian.json",
    "quest_omnicorp.json",
    "quest_shard.json",
    "quest_legion.json",
]


def load(name):
    with (ROOT / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def fail(message):
    raise AssertionError(message)


def main():
    world = load("world_map_v4.json")
    monster_data = load("monster_master.json")
    item_data = load("item_list.json")
    nodes = {node["id"]: node for node in world["nodes"]}
    monsters = {monster["monster_id"]: monster for monster in monster_data["monsters"]}
    item_ids = {item["id"] for item in item_data["items"]}
    baseline_rewards = None
    reports = []

    for filename in FILES:
        data = load(filename)
        quests = data.get("quests", [])
        if len(quests) != 100:
            fail(f"{filename}: expected 100 quests, got {len(quests)}")
        ids = [quest["id"] for quest in quests]
        if len(ids) != len(set(ids)):
            fail(f"{filename}: duplicate quest IDs")
        id_set = set(ids)
        levels = [quest["requirements"]["min_level"] for quest in quests]
        expected_levels = [1, 1, *range(2, 100)]
        if levels != expected_levels:
            fail(f"{filename}: invalid level coverage")

        rewards = [quest["rewards"] for quest in quests]
        reward_signature = [
            (reward["exp"], reward["currency"], reward["crd"], reward["rep"], reward["reputation"], tuple((item["item_id"], item["quantity"]) for item in reward["items"]))
            for reward in rewards
        ]
        if baseline_rewards is None:
            baseline_rewards = reward_signature
        elif reward_signature != baseline_rewards:
            fail(f"{filename}: reward curve differs from baseline")

        seen = set()
        current = quests[0]["id"]
        while current:
            if current in seen:
                fail(f"{filename}: chain cycle at {current}")
            seen.add(current)
            quest = quests[ids.index(current)]
            current = quest.get("quest_chain_next")
            if current and current not in id_set:
                fail(f"{filename}: missing chain target {current}")
        if len(seen) != 100:
            fail(f"{filename}: chain covers {len(seen)} of 100 quests")

        endgame = 0
        for quest in quests:
            region = quest["region"]
            if region not in nodes:
                fail(f'{filename}:{quest["id"]}: invalid region {region}')
            spawn_ids = {spawn["monster_id"] for spawn in nodes[region].get("monster_spawns", [])}
            for objective in quest["objectives"]:
                if objective["type"] != "kill":
                    fail(f'{filename}:{quest["id"]}: unsupported objective type {objective["type"]}')
                monster_id = objective["target"]
                if monster_id not in monsters:
                    fail(f'{filename}:{quest["id"]}: invalid monster {monster_id}')
                if monster_id not in spawn_ids:
                    fail(f'{filename}:{quest["id"]}: monster {monster_id} not in region {region}')
                if objective.get("target_code") != monsters[monster_id]["code"]:
                    fail(f'{filename}:{quest["id"]}: target code mismatch')
            for item in quest["rewards"]["items"]:
                if item["item_id"] not in item_ids:
                    fail(f'{filename}:{quest["id"]}: invalid reward item {item["item_id"]}')
            if quest["rewards"]["rep"] != quest["rewards"]["reputation"]:
                fail(f'{filename}:{quest["id"]}: reputation fields differ')
            level = quest["requirements"]["min_level"]
            if level >= 61:
                endgame += 1
                if quest["rewards"]["crd"] <= 0:
                    fail(f'{filename}:{quest["id"]}: endgame CRD must be positive')
        if endgame != 39:
            fail(f"{filename}: expected 39 endgame quests, got {endgame}")

        reports.append({
            "file": filename,
            "quests": len(quests),
            "endgame": endgame,
            "total_exp": sum(reward["exp"] for reward in rewards),
            "total_currency": sum(reward["currency"] for reward in rewards),
            "total_crd": sum(reward["crd"] for reward in rewards),
            "total_reputation": sum(reward["reputation"] for reward in rewards),
        })

    for report in reports:
        print(json.dumps(report, ensure_ascii=False))
    print("Faction quest validation passed")


if __name__ == "__main__":
    main()
