#!/usr/bin/env python3
"""Apply the reviewed 2026-10-08 combat catalogue corrections once."""

from collections import defaultdict
import copy
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def save(name, data):
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if name == "class_list.json":
        text = text.replace("\n", "\r\n")
    (ROOT / name).write_bytes(text.encode("utf-8"))


def modifier(stat, value, target="self", duration=0):
    return {"stat": stat, "value": value, "type": "percent", "duration_turns": duration,
            "target": target, "condition": "-"}


def periodic(kind, value, duration=99, target="self", condition=None, scale=0):
    result = {"type": kind, "value": value, "scale": scale,
              "duration_turns": duration, "target": target}
    if condition:
        result["condition"] = condition
    return result


def special(kind, value, duration=0, **extra):
    return {"type": kind, "value": value, "duration_turns": duration, **extra}


def n(value):
    return f"{value:g}"


def payload_description(skill):
    """Render legacy JSON effect blobs from the authoritative structured fields."""
    parts = []
    formula = skill["damage_formula"]
    if formula != "0" and skill["target_attack"] != "none":
        area = "all enemies" if "all" in skill["target_attack"] or "aoe" in skill["target_attack"] else "an enemy"
        parts.append(f"Deal {formula} damage to {area}")
    for effect in skill.get("stat_modifiers", []):
        stat, value = effect["stat"], effect["value"]
        if stat == "damage_taken":
            stat, value = "def", -value
        target = effect.get("target", "self").replace("all_ally", "all allies").replace("all_enemies", "all enemies")
        duration = f" for {effect['duration_turns']} turns" if skill["type"] == "Active" else ""
        suffix = "%" if effect["type"] == "percent" and stat not in ("agi", "per", "accuracy", "crit_rate") else ""
        parts.append(f"{target.capitalize()}: {n(value):s}{suffix} {stat.upper()}{duration}")
    for effect in skill.get("periodic_effects", []):
        target, kind = effect.get("target", "self"), effect["type"]
        value, scale = effect.get("value", 0), effect.get("scale", 0)
        amount = n(value) if value else n(scale * 100)
        percent = effect.get("condition") in ("max_hp_percent", "max_mp_percent") or (kind == "heal_over_time" and value > 0 and scale == 0)
        parts.append(f"{kind.replace('_', ' ').capitalize()} on {target}: {amount}{'%' if percent or scale else ''} per turn")
    for effect in skill.get("control_effects", []):
        chance = effect.get("chance", 1) * 100
        parts.append(f"{n(chance)}% chance to {effect['type']} {effect.get('target', 'enemy')} for {effect['duration_turns']} turns")
    for effect in skill.get("special_effects", []):
        kind, value = effect["type"], effect.get("value", 0)
        if kind == "direct_heal_scaling_perception":
            parts.append(f"Heal the selected ally for PER * {n(value)} HP")
        elif kind in ("aoe_heal_party", "aoe_damage_and_heal"):
            amount = f"PER * {n(value)} HP" if value <= 5 else f"{n(value)}% of each ally's maximum HP"
            parts.append(f"Heal all living allies for {amount}")
        elif kind == "healing_bonus_percent":
            parts.append(f"Increase healing power by {n(value)}%")
        elif kind == "party_shield":
            parts.append(f"Grant all living allies a shield of {n(value)} HP")
        elif kind in ("shield_flat", "shield_percent"):
            parts.append(f"Grant a shield of {n(value)}{'% maximum HP' if kind == 'shield_percent' else ' HP'}")
        elif kind in ("cleanse_debuff", "remove_debuff"):
            parts.append("Remove one debuff from the selected allies")
        elif kind == "cleanse_all_debuffs":
            parts.append("Remove all debuffs from the selected allies")
        elif kind == "damage_reflect":
            parts.append(f"Reflect {n(value)}% of damage received")
        elif kind == "armor_break":
            parts.append(f"Ignore {n(value)}% of enemy DEF for this attack")
        elif kind in ("multi_hit", "random_multi_target"):
            parts.append(f"Strike {effect.get('hits', value)} times")
        else:
            parts.append(f"{kind.replace('_', ' ').capitalize()}: {value}")
    return ". ".join(parts) + "."


def finalize():
    """Reconcile reviewed database edits and refresh the detailed change log."""
    skills = load("skill_list.json")
    by_id = {skill["id"]: skill for skill in skills}
    live_names = {
        "al5_67_act": "Dockside Absolution", "al5_68_pas": "Jury-Rigged Surge",
        "al5_73_pas": "Unfinished Charge", "al5_80_pas": "Corporate Bulwark",
        "al5_88_pas": "Seventh Protocol", "al5_90_pas": "Centuries of Aegis",
        "al5_91_pas": "Prewar Benediction",
    }
    for sid, name in live_names.items():
        by_id[sid]["name"] = name
    narra = by_id["al5_67_act"]
    narra.update(special_effects=[special("direct_heal_scaling_perception", 1.5), special("cleanse_debuff", 1)],
                 effect="Heal an ally for PER * 1.5 HP and remove one debuff.")
    narra["skill_description"] = narra["effect"]
    kythari = by_id["rc_kyt_act"]
    kythari.update(target_attack="random_enemies", skill_shape="multi_projectile")
    for effect in kythari["special_effects"]:
        if effect["type"] == "multi_target_limit":
            effect["hits"] = 3
    for skill in skills:
        for effect in skill.get("stat_modifiers", []):
            if effect.get("duration_turns", 0) < 0:
                effect["duration_turns"] = 0
        if skill["source_type"] == "Monster" and skill["skill_description"].endswith("a basic monster ability."):
            skill["skill_description"] = skill["effect"]
    # Give ignored passive CC payloads conservative, supported defensive effects.
    passive_fallbacks = {
        "storm_aura": ("damage_reflect", 10, "Reflect 10% of damage received."),
        "sk_mon_pas_venom_blood": ("status_immunity", "poison", "Immune to Poison effects."),
        "sk_mon_pas_storm_skin": ("status_immunity", "stun", "Immune to Stun effects."),
    }
    for sid, (kind, value, text) in passive_fallbacks.items():
        by_id[sid].update(control_effects=[], special_effects=[special(kind, value, 99)],
                         effect=text, skill_description=text)
    axiom = by_id["al2_axiom_act"]
    axiom["effect"] = "Deal ATK * 3.0 damage to one enemy, ignoring 30% of its DEF. Gain Unevadable for 1 turn after the attack."
    axiom["skill_description"] = axiom["effect"]
    by_id["dummy_protocol"].update(effect="An inert training protocol.", skill_description="An inert training protocol.")
    log = load("combat_data_changes.json")
    reasons = {entry["id"]: entry.get("reasons", []) for entry in log["changes"]}
    for sid in live_names:
        reasons.setdefault(sid, []).append("Preserve the already-applied Supabase name correction")
    reasons.setdefault("al5_67_act", []).append("Give the Healer role an actual healing payload, alongside its cleanse")
    reasons.setdefault("rc_kyt_act", []).append("Preserve the already-applied Supabase three-target routing correction")
    for sid in passive_fallbacks:
        reasons.setdefault(sid, []).append("Replace ignored passive CC with a supported defensive effect")
    changes = []
    for domain, filename, key, rows in [
        ("skills", "skill_list.json", "id", skills),
        ("classes", "class_list.json", "id", load("class_list.json")),
        ("allies", "ally_list.json", "ally_id", load("ally_list.json")["allies"]),
    ]:
        baseline = json.loads(subprocess.check_output(["git", "show", f"HEAD:{filename}"], cwd=ROOT))
        if isinstance(baseline, dict):
            baseline = baseline["allies"]
        old_by_id = {row[key]: row for row in baseline}
        for row in rows:
            before = old_by_id.get(row[key], {})
            fields = {field: {"before": before.get(field), "after": row.get(field)}
                      for field in before.keys() | row.keys() if before.get(field) != row.get(field)}
            if fields:
                changes.append({"domain": domain, "id": row[key], "reasons": list(dict.fromkeys(reasons.get(row[key], []))), "fields": fields})
    changes.extend(entry for entry in log["changes"] if entry["domain"] == "monsters")
    save("skill_list.json", skills)
    save("class_list.json", load("class_list.json"))
    # This roster was validated without changing its authored values/format.
    ally_path = ROOT / "ally_list.json"
    ally_path.write_bytes(ally_path.read_bytes().rstrip(b"\n"))
    save("combat_data_changes.json", {"date": "2026-10-08", "changes": changes})
    print(f"Finalized {len(changes)} changed records, preserving reviewed live edits.")


def main():
    log_path = ROOT / "combat_data_changes.json"
    if log_path.exists():
        raise SystemExit("Audit changes already applied. Review/remove the change log before re-authoring.")
    skills, classes, roster, monsters = load("skill_list.json"), load("class_list.json"), load("ally_list.json"), load("monster_master.json")
    originals = {"skills": copy.deepcopy(skills), "classes": copy.deepcopy(classes),
                 "allies": copy.deepcopy(roster["allies"]), "monsters": copy.deepcopy(monsters["monsters"])}
    by_id = {x["id"]: x for x in skills}
    by_class = {x["id"]: x for x in classes}
    reasons = {}

    def change(sid, reason, **updates):
        by_id[sid].update(updates)
        reasons.setdefault(sid, []).append(reason)

    replacements = {"sk_dread_act_2": "sk_dread_act_3", "sk_war_act_2": "sk_warlord_act_2", "sk_rav_pas": "sk_rav_pas_1"}
    for cls in classes:
        cls["learnable_skill_ids"] = [replacements.get(sid, sid) for sid in cls["learnable_skill_ids"]]
    by_class["mst_dreadnought"]["learnable_skill_ids"].append("sk_dread_ult")
    by_class["mst_warlord"]["learnable_skill_ids"].extend(["sk_warlord_act_3", "sk_warlord_ult"])
    by_id["sk_dread_ult"]["usage_requirements"]["allowed_classes"] = ["mst_dreadnought"]
    by_id["sk_rav_pas_1"]["usage_requirements"]["min_level"] = 40
    for sid in ["sk_chrono_act_3", "sk_chrono_ult"]:
        change(sid, "Chronovore eligibility identifies this as a racial skill", source_type="Race")

    # Use supported stat payloads; stat_conversion has no consumer in this client.
    change("sk_dread_pas", "Replace inert conversion with a supported tank passive",
           stat_modifiers=[modifier("def", 10)], effect="Increases the user's DEF by 10%.")
    change("sk_sent_pas", "Encode the previously text-only defensive passive",
           stat_modifiers=[modifier("def", 15)], effect="Increases the user's DEF by 15%.")
    change("sk_dread_act_1", "Remove simultaneous penalty falsely advertised as a delayed effect",
           stat_modifiers=[modifier("def", 50, duration=1)], mp_cost=35,
           effect="Increase the user's DEF by 50% for 1 turn.")
    change("sk_dread_ult", "Active HP stat modifiers have no engine consumer",
           stat_modifiers=[modifier("def", 40, duration=3)],
           special_effects=[special("shield_percent", 20, 3, target="self")],
           effect="Increase DEF by 40% and grant a shield equal to 20% of maximum HP for 3 turns.")
    change("sk_channeler_pas", "Remove unintended HP regeneration from an MP-only passive",
           periodic_effects=[periodic("mp_regen", 5, condition="max_mp_percent")], special_effects=[],
           effect="Recover 5% of maximum MP at the start of each turn.")
    change("sk_sky_pas", "Passive control_effects are not executed",
           control_effects=[], special_effects=[special("status_immunity", "root", 99)],
           effect="Immune to Root effects.")
    change("rc_num_pas", "Passive burn immunity requires a special handler",
           control_effects=[], special_effects=[special("status_immunity", "burn", 99)])
    change("metal_frame", "Passive poison immunity requires a special handler",
           control_effects=[], special_effects=[special("status_immunity", "poison", 99)],
           effect="Immune to Poison effects.")

    # MP costs, not metadata-only cooldowns, bound the strongest repeatable attacks.
    for sid, updates in {
        "sk_desp_act_2": {"mp_cost": 25, "cooldown_seconds": 3.5},
        "al_vael_act": {"damage_formula": "ATK * 1.05", "mp_cost": 45,
                        "effect": "Strike every enemy three times for ATK * 1.05 damage per hit and reduce their AGI by 30 for 2 turns."},
        "al2_tide_act": {"damage_formula": "ATK * 0.85", "mp_cost": 18,
                         "effect": "Strike one enemy twice for ATK * 0.85 damage per hit and reduce their AGI by 20 for 2 turns."},
        "al_serin_act": {"damage_formula": "ATK * 0.65", "mp_cost": 18,
                        "effect": "Deliver three strikes to random enemies for ATK * 0.65 damage each. Enemies hit lose 10 AGI for 2 turns."},
        "al2_axiom_act": {"mp_cost": 32},
        "sk_bioengineer_act_1": {"stat_modifiers": [modifier("atk", 40, "ally", 2)],
                                "effect": "Grant allies +40% ATK and Berserk for 2 turns."},
    }.items():
        change(sid, "Conservative MP/burst balance correction", **updates)

    change("al2_axiom_act", "ignore_def uses percentage units, not a boolean",
           special_effects=[special("ignore_def", 30), special("unevadable", 1, 1)],
           effect="Deal ATK * 3.0 damage to one enemy, ignoring 30% of its DEF. This attack cannot miss.")
    # Averaging the three hit formulas keeps total base damage while round-tripping
    # through public.skills.damage_formula (TEXT) and its existing exporter.
    change("rc_hek_act", "List formula was stringified into invalid SQL-exported arithmetic",
           damage_formula="40 + (ATK * 0.65 / 3)",
           effect="Strike one enemy three times. Each hit deals 40 + (ATK * 0.65 / 3) damage.")
    change("al4_57_act", "Remove duplicate heal; retain the intended Epic single heal",
           special_effects=[special("direct_heal_scaling_perception", 2.5)],
           effect="Heal the selected ally for PER * 2.5 HP.")
    change("al5_91_act", "Revive was implemented as a second party heal, not revival",
           special_effects=[special("aoe_heal_party", 35), special("cleanse_all_debuffs", 1)],
           effect="Restore 35% of maximum HP to all living allies and remove all their debuffs.")

    percent_types = {"bonus_damage_on_debuffed", "healing_bonus_percent", "bonus_damage_per_burn_stack",
                     "magic_penetration_percent", "redirect_party_damage", "conditional_damage_reduction",
                     "self_emergency_heal", "lifesteal_on_kill", "party_heal_amplify",
                     "splash_damage_all_enemies", "single_hit_damage_cap", "evasion_chance"}
    for skill in skills:
        for effect in skill.get("special_effects", []):
            if effect.get("type") in percent_types and isinstance(effect.get("value"), (int, float)) and 0 < effect["value"] < 1:
                effect["value"] = round(effect["value"] * 100, 6)
                reasons.setdefault(skill["id"], []).append("Correct fraction-to-percent units for the registered handler")
    for effect in by_id["al_grimm_pas"]["special_effects"]:
        if effect["type"] == "retaliate_on_hit_below_hp":
            effect["condition"] = "0.5"

    # Monster role membership is authoritative; the late imported records were
    # all stamped Active, including armor/regeneration passives.
    memberships = defaultdict(set)
    for monster in monsters["monsters"]:
        for slot in ["passive_skills", "active_skills"]:
            for ref in monster.get("skill_set", {}).get(slot, []):
                memberships[ref["skill_id"]].add(slot)
    passive_groups = {
        "def": "rust_armor chitin_shell fortified_frame bark_fortress hard_shell mud_body crystal_hide crystal_armor void_skin ember_skin crystal_carapace horned_guard crystal_skin parasite_shell venom_skin decay_skin",
        "atk": "void_resonance battle_instinct aethel_overflow pack_leader aethel_resonance aethel_glow shamanic_growth scavenger_greed mutagen_absorption spore_aura rot_aura",
        "agi": "light_drift nimble_feet",
        "accuracy": "sensor_matrix",
    }
    for stat, ids in passive_groups.items():
        for sid in ids.split():
            change(sid, "Restore monster passive role and executable payload",
                   type="Passive", damage_formula="0", mp_cost=0,
                   stat_modifiers=[modifier(stat, 10)], periodic_effects=[], control_effects=[],
                   special_effects=[], effect=f"Increases the user's {stat.upper()} by 10{'%' if stat in ('atk', 'def') else ''}.",
                   target_attack="none", target_effect="self", skill_shape="passive", cooldown_seconds=0.0)
    for sid in "minor_regeneration root_regeneration mutant_regeneration tumor_regeneration".split():
        change(sid, "Restore monster HP regeneration passive", type="Passive", damage_formula="0", mp_cost=0,
               periodic_effects=[periodic("heal_over_time", 3, condition="max_hp_percent")],
               effect="Recover 3% of maximum HP at the start of each turn.", target_attack="none", target_effect="self",
               skill_shape="passive", cooldown_seconds=0.0)
    for sid in "mana_echo energy_core_minor neural_absorption".split():
        change(sid, "Restore monster MP regeneration passive", type="Passive", damage_formula="0", mp_cost=0,
               periodic_effects=[periodic("mp_regen", 3, condition="max_mp_percent")],
               effect="Recover 3% of maximum MP at the start of each turn.", target_attack="none", target_effect="self",
               skill_shape="passive", cooldown_seconds=0.0)
    for sid in "pain_conversion blood_siphon".split():
        change(sid, "Replace inert passive import with explicit sustain", type="Passive", damage_formula="0", mp_cost=0,
               periodic_effects=[periodic("heal_over_time", 2, condition="max_hp_percent")],
               effect="Recover 2% of maximum HP at the start of each turn.", target_attack="none", target_effect="self",
               skill_shape="passive", cooldown_seconds=0.0)
    for sid in "venom_glands venom_sac".split():
        change(sid, "Restore passive venom defense", type="Passive", damage_formula="0", mp_cost=0,
               special_effects=[special("status_immunity", "poison", 99)],
               effect="Immune to Poison effects.", target_attack="none", target_effect="self",
               skill_shape="passive", cooldown_seconds=0.0)

    # Spore Cloud is used as both an active and a passive. Split only the passive
    # reference, preserving the active ID and all existing monster edits.
    aura = copy.deepcopy(by_id["spore_cloud"])
    aura.update(id="spore_cloud_aura", name="Spore Cloud Aura", type="Passive", damage_formula="0", mp_cost=0,
                stat_modifiers=[modifier("def", 8)], periodic_effects=[], control_effects=[], special_effects=[],
                effect="A protective spore veil increases the user's DEF by 8%.", skill_description="",
                target_attack="none", target_effect="self", skill_shape="passive", range=0.0, aoe_radius=0.0,
                projectile_speed=0.0, cooldown_seconds=0.0)
    skills.append(aura)
    for monster in monsters["monsters"]:
        for ref in monster.get("skill_set", {}).get("passive_skills", []):
            if ref["skill_id"] == "spore_cloud":
                ref["skill_id"] = "spore_cloud_aura"

    for skill in skills:
        sid = skill["id"]
        if not skill.get("damage_formula"):
            skill["damage_formula"] = "0"
        for key in ["control_effects", "periodic_effects", "special_effects"]:
            for effect in skill.get(key, []):
                if not effect.get("type") and effect.get("effect"):
                    effect["type"] = effect["effect"]
                if key == "control_effects" and effect.get("chance", 1) > 1:
                    effect["chance"] /= 100
                if skill["type"] == "Active" and key in ("control_effects", "periodic_effects") and effect.get("duration_turns", 0) <= 0:
                    effect["duration_turns"] = 1
        for effect in skill.get("stat_modifiers", []):
            if skill["type"] == "Passive" and effect.get("duration_turns", 0) < 0:
                effect["duration_turns"] = 0
            if skill["type"] == "Active" and effect.get("duration_turns", 0) <= 0:
                effect["duration_turns"] = 1
        if skill["type"] == "Passive":
            skill["target_attack"], skill["target_effect"] = "none", "self"
        else:
            for key in ["target_attack", "target_effect"]:
                skill[key] = (skill.get(key) or "enemy").lower().replace(" ", "_")
        if not skill.get("effect"):
            if sid == "dummy_protocol":
                skill["effect"] = "Training target protocol. Its encounter behavior is managed by the training battle."
            else:
                skill["target_attack"] = "enemy"
                skill["target_effect"] = "enemy"
                skill["skill_shape"] = "single_projectile"
                skill["range"], skill["projectile_speed"] = 1.5, 8.0
                skill["cooldown_seconds"] = 2.0
                skill["effect"] = "Deal ATK * 1.5 damage to one enemy."
                skill["skill_description"] = skill["effect"]
        if skill["source_type"] == "Ally" and skill["effect"].startswith("{"):
            skill["effect"] = payload_description(skill)
        if not skill.get("skill_description", "").strip() or skill["source_type"] == "Ally" or sid in reasons or sid == "dummy_protocol":
            skill["skill_description"] = skill["effect"]

    # Preserve recruitment costs, caps, rarity, draft cost and all ally stats.
    roster["meta"]["total"] = len(roster["allies"])
    changes = []
    for domain, key, rows in [("skills", "id", skills), ("classes", "id", classes),
                              ("allies", "ally_id", roster["allies"]), ("monsters", "monster_id", monsters["monsters"])]:
        old_by_id = {x[key]: x for x in originals[domain]}
        for row in rows:
            before = old_by_id.get(row[key], {})
            fields = {field: {"before": before.get(field), "after": row.get(field)}
                      for field in before.keys() | row.keys() if before.get(field) != row.get(field)}
            if fields:
                changes.append({"domain": domain, "id": row[key], "reasons": reasons.get(row[key], []), "fields": fields})
    save("skill_list.json", skills)
    save("class_list.json", classes)
    save("ally_list.json", roster)
    save("monster_master.json", monsters)
    save("combat_data_changes.json", {"date": "2026-10-08", "changes": changes})
    print(f"Updated {len(changes)} records; catalogue now has {len(skills)} skills.")


if __name__ == "__main__":
    if "--finalize" in sys.argv:
        finalize()
    else:
        main()
