#!/usr/bin/env python3
"""Validate class trees, skills, ally templates and their external references."""

import argparse
import ast
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
STAT_KEYS = {"hp", "mp", "atk", "def", "agi", "per", "agility", "perception"}
FORMULA_NAMES = {
    "atk", "def", "agi", "agility", "per", "perception", "hp", "mp",
    "max_hp", "maxhp", "current_hp", "damage_taken_last_turn", "basedamage",
}
PVP = {"Common": (1.0, 1), "Uncommon": (0.97, 1), "Rare": (0.93, 2),
       "Epic": (0.83, 3), "Legendary": (0.72, 4)}


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def formula_value(formula, stats=None):
    """Evaluate only the arithmetic accepted by the game, without eval()."""
    values = dict.fromkeys(FORMULA_NAMES, 100)
    values.update({"max_hp": 500, "maxhp": 500, "current_hp": 300,
                   "damage_taken_last_turn": 80, "basedamage": 50})
    values.update(stats or {})
    expression = re.sub(r"\b[a-z_]+\b", lambda match: "stat_" + match[0], formula.lower())
    tree = ast.parse(expression, mode="eval")

    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.Name) and node.id.removeprefix("stat_") in values:
            return values[node.id.removeprefix("stat_")]
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            return visit(node.operand) * (-1 if isinstance(node.op, ast.USub) else 1)
        if isinstance(node, ast.BinOp):
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div) and right:
                return left / right
        raise ValueError("unsupported formula syntax or zero denominator")

    return visit(tree)


def audit():
    classes, skills, roster = load("class_list.json"), load("skill_list.json"), load("ally_list.json")
    allies = roster["allies"]
    errors, warnings = [], []
    by_skill = {x["id"]: x for x in skills}
    by_class = {x["id"]: x for x in classes}
    class_refs = set()

    def error(owner, message):
        errors.append(f"{owner}: {message}")

    def number(owner, value, minimum=0, integer=False):
        if type(value) not in (int, float) or not math.isfinite(value) or value < minimum or (integer and type(value) is not int):
            error(owner, f"invalid numeric value {value!r}")

    for label, rows, key in [("class", classes, "id"), ("skill", skills, "id"),
                             ("ally", allies, "ally_id"), ("ally code", allies, "code")]:
        for identifier, count in Counter(x.get(key) for x in rows).items():
            if not identifier or count > 1:
                error(label, f"missing or duplicate {key}: {identifier!r}")

    for cls in classes:
        cid, parent = cls["id"], cls.get("parent_id")
        tier = cls.get("tier")
        expected = {"Base": None, "Advance": "Base", "Master": "Advance"}.get(tier, "invalid")
        if expected == "invalid" or (expected is None and parent is not None) or (expected is not None and by_class.get(parent, {}).get("tier") != expected):
            error(cid, "invalid tier/parent path")
        path, cursor = set(), cls
        while cursor:
            if cursor["id"] in path:
                error(cid, "class inheritance cycle")
                break
            path.add(cursor["id"])
            cursor = by_class.get(cursor.get("parent_id"))
        for stat, value in cls.get("base_stats_bonus", {}).items():
            if stat not in STAT_KEYS or type(value) is not int:
                error(cid, f"invalid stat bonus {stat}: {value!r}")
        refs = cls.get("learnable_skill_ids", [])
        if len(refs) != len(set(refs)):
            error(cid, "duplicate learnable skill")
        if not any(by_skill.get(sid, {}).get("type") == "Passive" for sid in refs):
            error(cid, "class has no passive skill")
        if not any(by_skill.get(sid, {}).get("type") == "Active" for sid in refs):
            error(cid, "class has no active skill")
        for sid in refs:
            class_refs.add(sid)
            skill = by_skill.get(sid)
            if not skill:
                error(cid, f"missing skill {sid}")
            elif skill.get("source_type") != "Class_Tree" or cid not in skill.get("usage_requirements", {}).get("allowed_classes", []):
                error(cid, f"skill {sid} has wrong class eligibility")

    for skill in skills:
        sid, typ = skill["id"], skill.get("type")
        if typ not in ("Active", "Passive"):
            error(sid, "invalid skill type")
        for key in ["name", "effect", "skill_description", "source_type", "skill_shape", "target_attack", "target_effect"]:
            if not isinstance(skill.get(key), str) or not skill[key].strip():
                error(sid, f"empty/missing {key}")
        for key in ["mp_cost", "range", "aoe_radius", "projectile_speed", "cooldown_seconds"]:
            number(f"{sid}.{key}", skill.get(key), integer=key == "mp_cost")
        formula = skill.get("damage_formula")
        if not isinstance(formula, str) or not formula.strip():
            error(sid, "formula must be a nonempty SQL-compatible string")
        else:
            try:
                if not math.isfinite(formula_value(formula)) or formula_value(formula) < 0:
                    error(sid, "invalid formula result")
            except (ValueError, SyntaxError, TypeError):
                error(sid, f"invalid formula {formula!r}")
        if typ == "Passive" and (skill.get("mp_cost") != 0 or skill.get("cooldown_seconds") != 0 or formula not in ("0", "")):
            error(sid, "passive has cost/cooldown/damage")
        if typ == "Passive" and skill.get("control_effects"):
            warnings.append(f"{sid}: passive control_effects are ignored by applyPassives")
        for key in ["stat_modifiers", "periodic_effects", "control_effects", "special_effects"]:
            effects = skill.get(key, [])
            if not isinstance(effects, list):
                error(sid, f"{key} is not a list")
                continue
            if len({json.dumps(x, sort_keys=True) for x in effects}) != len(effects):
                error(sid, f"duplicate {key} payload")
            for effect in effects:
                if not effect.get("type"):
                    error(sid, f"{key} missing canonical type")
                number(f"{sid}.{key}.duration", effect.get("duration_turns", 0), integer=True)
                if key == "control_effects":
                    chance = effect.get("chance", 1)
                    number(f"{sid}.{key}.chance", chance)
                    if isinstance(chance, (float, int)) and chance > 1:
                        error(sid, "control chance exceeds 1")
                if key in ("periodic_effects", "stat_modifiers"):
                    number(f"{sid}.{key}.value", effect.get("value", 0), minimum=-100000)
                if typ == "Active" and key in ("control_effects", "stat_modifiers", "periodic_effects") and effect.get("duration_turns", 0) <= 0:
                    error(sid, f"active {key} duration must be positive")
        req = skill.get("usage_requirements", {})
        for cid in req.get("allowed_classes", []):
            if cid.lower() != "all" and cid not in by_class:
                error(sid, f"unknown allowed class {cid}")
        if skill.get("source_type") == "Class_Tree" and sid not in class_refs:
            error(sid, "class skill cannot be learned from any class")
        if formula == "0" and sid != "dummy_protocol" and not any(skill.get(k) for k in ["stat_modifiers", "periodic_effects", "control_effects", "special_effects"]):
            error(sid, "skill has no executable payload")

    if roster.get("meta", {}).get("total") != len(allies):
        error("ally meta", "total differs from roster count")
    known_factions = {npc.get("faction") for npc in load("npc_list.json")} | {"NEUTRAL"}
    for ally in allies:
        aid = ally["ally_id"]
        for key in ["name", "code", "role", "rarity", "brief_background_story", "place_of_origin", "faction_affinity"]:
            if not isinstance(ally.get(key), str) or not ally[key].strip():
                error(aid, f"empty {key}")
        if ally.get("role") not in {"DPS", "Tank", "Healer", "Support"}:
            error(aid, "unknown combat role")
        if ally.get("role") == "Healer":
            active = by_skill.get(ally.get("active_skill", {}).get("skill_id"), {})
            healing_types = {"direct_heal_scaling_perception", "aoe_heal_party", "heal_all_allies", "dual_target_heal"}
            if not any(effect.get("type") in healing_types for effect in active.get("special_effects", [])):
                error(aid, "Healer active skill has no healing payload")
        if ally.get("faction_affinity") not in known_factions:
            warnings.append(f"{aid}: affinity {ally.get('faction_affinity')} has no NPC faction match")
        for stat in ["hp", "mp", "atk", "def", "agi", "per"]:
            number(f"{aid}.{stat}", ally.get("base_stats", {}).get(stat), minimum=1, integer=True)
        for key in ["level_cap", "recruit_cost", "conclave_points"]:
            number(f"{aid}.{key}", ally.get(key), minimum=1, integer=True)
        expected = PVP.get(ally.get("rarity"))
        if not expected or (ally.get("pvp_scale"), ally.get("conclave_points")) != expected:
            error(aid, "rarity/PvP scale/draft cost mismatch")
        for slot, typ in [("passive_skill", "Passive"), ("active_skill", "Active")]:
            sid = ally.get(slot, {}).get("skill_id")
            skill = by_skill.get(sid)
            if not skill:
                error(aid, f"missing {slot}: {sid}")
            elif skill.get("source_type") != "Ally" or skill.get("type") != typ:
                error(aid, f"{slot} has wrong type/source")
            elif skill["mp_cost"] > ally["base_stats"]["mp"]:
                error(aid, f"{slot} unaffordable at recruitment")
            elif skill.get("usage_requirements", {}).get("allowed_classes") or skill.get("usage_requirements", {}).get("allowed_races"):
                error(aid, f"{slot} restricted to player race/class")

    external = defaultdict(set)
    for monster in load("monster_master.json")["monsters"]:
        for slot, typ in [("passive_skills", "Passive"), ("active_skills", "Active")]:
            for ref in monster.get("skill_set", {}).get(slot, []):
                sid = ref["skill_id"]
                external[sid].add(typ)
                if sid not in by_skill or by_skill[sid].get("type") != typ:
                    error(monster["monster_id"], f"{slot}: missing or wrong-type skill {sid}")
    race_refs = []

    def race_skills(value):
        if isinstance(value, dict):
            for slot, typ in [("passive_skill", "Passive"), ("active_skill", "Active")]:
                if slot in value:
                    sid = value[slot].get("skill_id")
                    race_refs.append(sid)
                    if sid not in by_skill or by_skill[sid].get("type") != typ:
                        error(value.get("code", "race/genus"), f"invalid {slot}: {sid}")
            for child in value.values():
                race_skills(child)
        elif isinstance(value, list):
            for child in value:
                race_skills(child)

    race_skills(load("master_race.json"))
    return {"classes": len(classes), "skills": len(skills), "allies": len(allies),
            "class_skill_links": sum(len(c["learnable_skill_ids"]) for c in classes),
            "ally_skill_links": len(allies) * 2,
            "race_genus_skill_links": len(race_refs),
            "monster_skill_ids": len(external), "errors": errors, "warnings": warnings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", default="combat_data_validation.json")
    args = parser.parse_args()
    result = audit()
    (ROOT / args.report).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{result['classes']} classes, {result['skills']} skills, {result['allies']} allies: "
          f"{len(result['errors'])} errors, {len(result['warnings'])} warnings")
    for message in result["errors"][:25]:
        print("ERROR", message)
    sys.exit(bool(result["errors"]))


if __name__ == "__main__":
    main()
