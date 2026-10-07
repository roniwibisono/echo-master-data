#!/usr/bin/env python3
"""Audit monster records and the active world/biome/dungeon/raid references."""

import argparse
from collections import Counter
import json
import math
from pathlib import Path
import re

from validate_data import collect_quests

ROOT = Path(__file__).resolve().parent
RANKS = {"normal", "elite", "hero", "leader", "boss", "area_boss", "raid_boss", "dungeon_boss", "summon"}
STATS = {"hp", "mp", "atk", "def", "agi", "per"}
REWARDS = {"exp_reward", "currency_reward", "crd_reward", "guild_point", "reputation_point", "hunting_point"}


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def norm(value):
    return str(value).upper().strip().replace(" ", "_")


def audit_quest_targets():
    monsters = load("monster_master.json")["monsters"]
    by_target = {norm(m["code"]): m for m in monsters}
    by_target.update({str(m["monster_id"]): m for m in monsters})
    reachable = {s["monster_id"] for n in load("world_map_v4.json")["nodes"]
                 for s in n.get("monster_spawns", [])}
    for raid in load("raid_boss_event.json")["raids"]:
        reachable.update([raid["boss_monster_id"]] + raid.get("spawn_monster_id", []))
    for dungeon in load("dungeon_db.json")["dungeons"]:
        reachable.update([dungeon["boss_monster_id"]] + [m["monster_id"] for m in dungeon.get("monsters", [])])
    errors, warnings, count = [], [], 0
    for path in sorted(ROOT.glob("quest_*.json")):
        quests = []
        collect_quests(load(path.name), quests)
        for quest in quests:
            for objective in quest["objectives"]:
                if objective.get("type") not in ("kill", "defeat", "hunt"):
                    continue
                count += 1
                target = objective.get("target")
                monster = by_target.get(norm(target))
                record = {"source": path.name, "quest_id": quest.get("id"), "target": target}
                if monster is None:
                    errors.append({**record, "message": "No monster definition for quest kill target"})
                elif monster["monster_id"] not in reachable:
                    warnings.append({**record, "message": "No active world/dungeon/raid encounter found"})
    return {"kill_objective_links": count, "resolved_links": count - len(errors),
            "errors": errors, "warnings": warnings}


def audit(game_root=None):
    monsters = load("monster_master.json")["monsters"]
    skills = {s["id"]: s for s in load("skill_list.json")}
    items = {i["id"] for i in load("item_list.json")["items"]}
    nodes = {n["id"]: n for n in load("world_map_v4.json")["nodes"]}
    dungeons, raids = load("dungeon_db.json")["dungeons"], load("raid_boss_event.json")["raids"]
    by_id = {m["monster_id"]: m for m in monsters}
    aliases = {norm(value): n["id"] for n in nodes.values() for value in (n["id"], n["name"])}
    for d in dungeons:
        for value in (d["dungeon_id"], d["name"]):
            aliases[norm(value)] = d["dungeon_id"]
    errors, warnings = [], []
    counts = Counter()

    def issue(out, owner, field, message):
        out.append({"owner": owner, "field": field, "message": message})

    def number(owner, field, value, minimum=0, maximum=None, integer=False):
        valid = type(value) in (int, float) and math.isfinite(value) and value >= minimum
        valid = valid and (maximum is None or value <= maximum) and (not integer or type(value) is int)
        if not valid:
            issue(errors, owner, field, f"Invalid numeric value: {value!r}")

    for key in ("monster_id", "code"):
        for value, count in Counter(m.get(key) for m in monsters).items():
            if not value or count > 1:
                issue(errors, "catalogue", key, f"Missing or duplicate identifier: {value!r}")
    referenced = set()
    supported = None
    if game_root:
        path = Path(game_root) / "lib/features/combat/engine/monster_ai_service.dart"
        if path.exists():
            supported = set(re.findall(r"case '([^']+)':", path.read_text(encoding="utf-8")))

    for m in monsters:
        owner = m["code"]
        number(owner, "monster_id", m.get("monster_id"), 1, integer=True)
        number(owner, "level", m.get("level"), 1, integer=True)
        for field in ("code", "name", "race_code", "spawn_monster_id"):
            if not isinstance(m.get(field), str) or not m[field].strip():
                issue(errors, owner, field, "Required text is empty")
        if m.get("rank") not in RANKS:
            issue(errors, owner, "rank", "Unknown rank")
        if set(m.get("base_stats", {})) != STATS:
            issue(errors, owner, "base_stats", "Expected exactly six canonical stat keys")
        for stat in STATS:
            number(owner, f"base_stats.{stat}", m.get("base_stats", {}).get(stat), 1 if stat == "hp" else 0, integer=True)
        for field in REWARDS:
            number(owner, field, m.get(field), integer=True)
        number(owner, "critical_rate", m.get("critical_rate"), maximum=1)
        number(owner, "critical_damage", m.get("critical_damage"), 1)
        number(owner, "scaling.basic_attack", m.get("scaling", {}).get("basic_attack"), 0.01)
        number(owner, "scaling.skill_scaling_bonus", m.get("scaling", {}).get("skill_scaling_bonus"))
        for field in ("element", "resistances", "weaknesses", "status_immunity", "spawn_location"):
            values = m.get(field)
            if not isinstance(values, list) or any(not isinstance(v, str) or not v.strip() for v in values):
                issue(errors, owner, field, "Expected a list of nonempty strings")
            elif len(values) != len(set(values)):
                issue(errors, owner, field, "Duplicate entries")
        for value in set(m.get("resistances", [])) & set(m.get("weaknesses", [])):
            issue(errors, owner, "weaknesses", f"Both resistance and weakness: {value}")
        active = set()
        for slot, typ in (("active_skills", "Active"), ("passive_skills", "Passive")):
            refs = m.get("skill_set", {}).get(slot, [])
            ids = [r.get("skill_id") for r in refs]
            if len(ids) != len(set(ids)):
                issue(errors, owner, slot, "Duplicate skill reference")
            for sid in ids:
                counts[slot] += 1
                if sid not in skills or skills[sid].get("type") != typ:
                    issue(errors, owner, slot, f"Missing or wrong-type skill: {sid}")
                elif typ == "Active":
                    active.add(sid)
                    if skills[sid]["mp_cost"] > m["base_stats"]["mp"]:
                        issue(errors, owner, slot, f"Cannot afford {sid} at full MP")
        pattern = m.get("ai_pattern", {})
        behavior = pattern.get("behavior", pattern.get("phase_1", {}).get("behavior", "basic_attack_loop"))
        if supported is not None and behavior not in supported:
            issue(warnings, owner, "ai_pattern.behavior", f"Client uses generic fallback for {behavior}")
        phases = sorted((p, v) for p, v in pattern.items() if p.startswith("phase_") and isinstance(v, dict))
        previous = 1.01
        for phase, payload in [("main", pattern)] + phases:
            for sid in payload.get("skills", []):
                counts["phase_skill_links"] += 1
                if sid not in active:
                    issue(errors, owner, f"ai_pattern.{phase}.skills", f"Not an equipped active skill: {sid}")
            if phase != "main":
                threshold = payload.get("hp_threshold")
                number(owner, f"{phase}.hp_threshold", threshold, maximum=1)
                if isinstance(threshold, (int, float)):
                    if threshold >= previous:
                        issue(errors, owner, phase, "HP thresholds must strictly descend")
                    previous = threshold
                for key, value in payload.items():
                    if key.endswith("_bonus"):
                        number(owner, f"{phase}.{key}", value)
        for field in ("drop_item", "special_reward"):
            drops = m.get(field, [])
            drop_ids = [d.get("itemId") for d in drops]
            if len(drop_ids) != len(set(drop_ids)):
                issue(errors, owner, field, "Duplicate item drop within one table")
            for d in drops:
                counts["drop_links"] += 1
                if d.get("itemId") not in items:
                    issue(errors, owner, field, f"Undefined item: {d.get('itemId')}")
                number(owner, f"{field}.chance", d.get("chance"), maximum=1)
                low, high = d.get("min_qty", 1), d.get("max_qty", 1)
                number(owner, f"{field}.min_qty", low, 1, integer=True)
                number(owner, f"{field}.max_qty", high, low, integer=True)
        for loc in m.get("spawn_location", []):
            canonical = aliases.get(norm(loc))
            if canonical and loc != canonical:
                issue(warnings, owner, "spawn_location", f"Noncanonical alias: {loc} -> {canonical}")
            elif not canonical and m["rank"] != "summon":
                issue(warnings, owner, "spawn_location", f"Legacy location not present in active world/dungeons: {loc}")

    for node in nodes.values():
        for spawn in node.get("monster_spawns", []):
            mid = spawn.get("monster_id")
            counts["world_spawn_links"] += 1
            referenced.add(mid)
            number(node["id"], "spawn_weight", spawn.get("spawn_weight"), 0.000001)
            if mid not in by_id:
                issue(errors, node["id"], "monster_spawns", f"Undefined monster: {mid}")
                continue
            monster = by_id[mid]
            if node["id"] not in {aliases.get(norm(loc)) for loc in monster["spawn_location"]}:
                issue(errors, node["id"], "monster_spawns", f"{monster['code']} is tagged to another region")
            low, high = node.get("level_range", [1, 100])
            if monster["rank"] == "normal" and not low <= monster["level"] <= high:
                issue(warnings, node["id"], "level_range", f"{monster['code']} level {monster['level']} outside {low}-{high}")
    for kind, rows, key in (("dungeon", dungeons, "dungeon_id"), ("raid", raids, "raid_id")):
        for encounter in rows:
            mid_list = [encounter["boss_monster_id"]]
            mid_list += [x["monster_id"] for x in encounter.get("monsters", [])]
            mid_list += encounter.get("spawn_monster_id", [])
            for mid in mid_list:
                counts[f"{kind}_monster_links"] += 1
                referenced.add(mid)
                if mid not in by_id:
                    issue(errors, encounter[key], "monster_id", f"Undefined monster: {mid}")
            boss = by_id.get(encounter["boss_monster_id"])
            if kind == "raid" and boss:
                for phase in encounter.get("phases", []):
                    mp = boss["ai_pattern"].get(f"phase_{phase['phase']}")
                    if mp and mp.get("hp_threshold") != phase.get("hp_threshold"):
                        issue(warnings, boss["code"], "hp_threshold", f"Monster phase {phase['phase']} differs from {encounter[key]}")
            for drop in encounter.get("clear_rewards", {}).get("loot_table", []):
                if drop.get("item_id") not in items:
                    issue(errors, encounter[key], "loot_table", f"Undefined item: {drop.get('item_id')}")
    mappings = load("biome_monster_mapping.json")["mappings"]
    biome_ids = [row["biome_primary"] for row in mappings]
    if len(biome_ids) != len(set(biome_ids)):
        issue(errors, "biome mapping", "biome_primary", "Duplicate biome mapping")
    for row in mappings:
        ids, weights = row["monster_ids"], row["spawn_weights"]
        if len(ids) != len(weights) or len(ids) != len(set(ids)):
            issue(errors, row["biome_primary"], "monster_ids", "Duplicate IDs or weight count mismatch")
        if weights and not math.isclose(sum(weights), 1, abs_tol=1e-9):
            issue(errors, row["biome_primary"], "spawn_weights", "Probabilities must sum to one")
        for weight in weights:
            number(row["biome_primary"], "spawn_weights", weight, 0.000001, 1)
        for mid in ids:
            counts["biome_monster_links"] += 1
            if mid not in by_id:
                issue(errors, row["biome_primary"], "monster_ids", f"Undefined monster: {mid}")
        eligible = {s["monster_id"] for n in nodes.values()
                    if n.get("biome", {}).get("primary") == row["biome_primary"]
                    for s in n.get("monster_spawns", [])}
        if eligible and set(ids) != eligible:
            issue(warnings, row["biome_primary"], "monster_ids", "Biome mapping disagrees with active world spawn tables")
    unused = [{"monster_id": m["monster_id"], "code": m["code"], "rank": m["rank"]}
              for m in monsters if m["monster_id"] not in referenced and m["rank"] != "summon"]
    return {"monsters": len(monsters), "ranks": dict(Counter(m["rank"] for m in monsters)),
            "counts": dict(counts), "unreferenced_encounter_templates": unused,
            "errors": errors, "warnings": warnings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=ROOT.parent / "project-echo")
    parser.add_argument("--report", default="monster_data_validation.json")
    parser.add_argument("--check-quests", action="store_true", help="Also report unresolved quest kill targets")
    args = parser.parse_args()
    result = audit(args.game_root)
    quest_report = audit_quest_targets() if args.check_quests else None
    if quest_report is not None:
        result["quest_references"] = quest_report
        (ROOT / "monster_quest_validation.json").write_text(json.dumps(quest_report, indent=2) + "\n", encoding="utf-8")
    (ROOT / args.report).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{result['monsters']} monsters: {len(result['errors'])} errors, {len(result['warnings'])} warnings")
    for item in result["errors"][:30]:
        print("ERROR", item)
    if quest_report is not None:
        print(f"Quest kill targets: {quest_report['resolved_links']}/{quest_report['kill_objective_links']} resolved; {len(quest_report['errors'])} errors")
        for item in quest_report["errors"]:
            print("QUEST ERROR", item)
    raise SystemExit(bool(result["errors"] or (quest_report and quest_report["errors"])))


if __name__ == "__main__":
    main()
