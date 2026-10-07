#!/usr/bin/env python3
"""Apply the narrowly reviewed monster audit fixes and preserve other edits."""

import argparse
from collections import defaultdict
import copy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from audit_monster_data import load, norm


def save(name, value):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def dungeon_templates():
    # Reuse the existing crystal-family mechanics rather than adding new skills.
    template = copy.deepcopy(next(m for m in load("monster_master.json")["monsters"] if m["monster_id"] == 5033))
    templates = []
    for mid, code, name, level, stats, passive, active, behavior in [
        (6001, "CRYSTAL_DEPTHS_SENTRY", "Crystal Depths Sentry", 40,
         {"hp": 7200, "mp": 450, "atk": 420, "def": 400, "agi": 40, "per": 55},
         "crystal_armor", "crystal_puncture", "defensive_guard"),
        (6002, "CRYSTAL_DEPTHS_SKITTER", "Crystal Depths Skitter", 42,
         {"hp": 5400, "mp": 320, "atk": 480, "def": 280, "agi": 65, "per": 45},
         "crystal_carapace", "shard_spike", "skirmisher"),
    ]:
        monster = copy.deepcopy(template)
        monster.update(monster_id=mid, code=code, name=name, level=level,
                       spawn_monster_id="dungeon", spawn_location=["crystal_depths"],
                       base_stats=stats, ai_pattern={"behavior": behavior},
                       critical_rate=0.08, critical_damage=1.5,
                       scaling={"basic_attack": 1.2, "skill_scaling_bonus": 0.3},
                       skill_set={"passive_skills": [{"skill_id": passive}], "active_skills": [{"skill_id": active}]},
                       exp_reward=1800 if mid == 6001 else 2000,
                       currency_reward=800 if mid == 6001 else 900,
                       crd_reward=5, guild_point=10, reputation_point=20, hunting_point=10,
                       drop_item=[{"itemId": "refined_crystal_shard", "chance": 0.5}], special_reward=[])
        templates.append(monster)
    return templates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--add-dungeon-monsters", action="store_true")
    args = parser.parse_args()
    log_name = "monster_audit_20261008_changes.json"
    if (ROOT / log_name).exists():
        raise SystemExit("Audit already applied; do not overwrite its baseline/change log.")
    data, world, dungeon = load("monster_master.json"), load("world_map_v4.json"), load("dungeon_db.json")
    monsters = data["monsters"]
    old = {m["monster_id"]: copy.deepcopy(m) for m in monsters}
    nodes = world["nodes"]
    aliases = {norm(value): n["id"] for n in nodes for value in (n["id"], n["name"])}
    for d in dungeon["dungeons"]:
        for value in (d["dungeon_id"], d["name"]):
            aliases[norm(value)] = d["dungeon_id"]
    for monster in monsters:
        canonical = [aliases[norm(loc)] for loc in monster["spawn_location"] if norm(loc) in aliases]
        # A verified destination supersedes obsolete labels on the same record;
        # entirely unmapped legacy templates retain their original locations.
        if canonical:
            monster["spawn_location"] = list(dict.fromkeys(canonical))
        pattern = monster["ai_pattern"]
        if "phase_1" in pattern:
            default = pattern["phase_1"]["behavior"]
            pattern["behavior"] = {"rotational_aoe": "standard_rotation",
                                   "single_target_burst": "aggressive_single_target",
                                   "aoe_pressure": "aggressive_swarm",
                                   "ranged_pressure": "ranged_basic"}.get(default, default)
        if monster["monster_id"] == 4001:
            pattern["phase_2"]["skills"] = ["meteor_dive", "inferno_breath"]
            raid = next(r for r in load("raid_boss_event.json")["raids"] if r["boss_monster_id"] == 4001)
            pattern["phase_3"]["hp_threshold"] = raid["phases"][2]["hp_threshold"]
        if monster["monster_id"] == 926:
            pattern["behavior"] = "aggressive_hunter"
            replacements = {"siege_plasma_emitter": "overheated_reactor_part",
                            "reinforced_hydraulic_frame": "hydraulic_piston_fragment",
                            "high_density_reactor_core": "power_regulator_core"}
            for drop in monster["drop_item"]:
                drop["itemId"] = replacements.get(drop["itemId"], drop["itemId"])
        if monster["monster_id"] == 9999:
            monster["spawn_location"] = ["NEXUS_CORE"]
    if args.add_dungeon_monsters:
        monsters.extend(m for m in dungeon_templates() if m["monster_id"] not in old)
    mapping = load("biome_monster_mapping.json")
    previous_mapping = copy.deepcopy(mapping)
    weights_by_biome = defaultdict(lambda: defaultdict(float))
    for node in nodes:
        biome = node.get("biome", {}).get("primary")
        if biome:
            for spawn in node.get("monster_spawns", []):
                weights_by_biome[biome][spawn["monster_id"]] += spawn["spawn_weight"]
    present = {row["biome_primary"] for row in mapping["mappings"]}
    for biome in sorted(weights_by_biome.keys() - present):
        mapping["mappings"].append({"biome_primary": biome, "monster_ids": [], "spawn_weights": []})
    for row in mapping["mappings"]:
        weighted = weights_by_biome[row["biome_primary"]]
        row["monster_ids"] = sorted(weighted)
        total = sum(weighted.values())
        row["spawn_weights"] = [weighted[mid] / total for mid in row["monster_ids"]]
    changes = []
    for monster in monsters:
        before = old.get(monster["monster_id"], {})
        fields = {key: {"before": before.get(key), "after": monster.get(key)}
                  for key in before.keys() | monster.keys() if before.get(key) != monster.get(key)}
        if fields:
            changes.append({"monster_id": monster["monster_id"], "code": monster["code"], "new": not before, "fields": fields})
    save("monster_master.json", data)
    save("biome_monster_mapping.json", mapping)
    save(log_name, {"date": "2026-10-08", "changes": changes,
                    "biome_mapping": {"before": previous_mapping, "after": mapping}})
    print(f"Changed {len(changes)} monster records; {len(monsters)} total, {len(mapping['mappings'])} biome mappings.")


if __name__ == "__main__":
    main()
