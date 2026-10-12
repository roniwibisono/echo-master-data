#!/usr/bin/env python3

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

FACTIONS = {
    "quest_concordium.json": {
        "prefix": "fq_conc_",
        "faction": "CONCORDIUM",
        "regions": ["AETHEL_GARDENS", "BROKEN_CIVIL_QUARTER", "CRADLE_OUTER_RING", "INNER_CRADLE_EXCLUSION"],
    },
    "quest_arcanum.json": {
        "prefix": "fq_arc_",
        "faction": "THE_ARCANUM_SEEKERS",
        "regions": ["CRYSTAL_SLOPE", "FRACTURED_GLASS_VALLEY", "RESONANCE_CAVERNS", "SHARD_PULSE_PEAK"],
    },
    "quest_iron.json": {
        "prefix": "fq_iron_",
        "faction": "IRON_HEGEMONY",
        "regions": ["SCRAP_FIELD", "IRON_RAVINE", "WAR_MACHINE_GRAVEYARD", "TITAN_ASSEMBLY_YARD"],
    },
    "quest_meridian.json": {
        "prefix": "fq_merid_",
        "faction": "MERIDIAN_CARTEL",
        "regions": ["CORAL_WETLANDS", "SMUGGLER_JUNGLE", "BLACK_DOCK_MARKET", "SUNKEN_AETHEL_RUIN"],
    },
    "quest_omnicorp.json": {
        "prefix": "fq_omni_",
        "faction": "OMNICORP",
        "regions": ["HIGHLAND_PLATEAU", "EXTRACTION_ZONE_DELTA", "SECURE_MINING_GRID", "SKYBRIDGE_REACTOR"],
    },
    "quest_shard.json": {
        "prefix": "fq_shard_",
        "faction": "CHILDREN_OF_THE_SHARD",
        "regions": ["GLOWVINE_FOREST", "SHARDROOT_SWAMP", "FRAGMENT_SHRINE", "HEARTWOOD_ALTAR"],
    },
    "quest_legion.json": {
        "prefix": "fq_star_",
        "faction": "STARFORGED_LEGION",
        "regions": ["DUNE_OUTSKIRTS", "SCORCHED_BADLANDS", "MESA_WARPATH", "FORGE_CANYON_DEPTHS"],
    },
}

SHARED_REGIONS = {
    range(41, 51): ["CRADLE_EXPANSE", "BLOOD_IRON_BASIN", "VOID_RIFT_CROSSROADS"],
    range(51, 61): ["AETHEL_STORM_RIDGE", "VOID_ECHO_CHASM", "HIDDEN_AETHELGARDIAN_CITY"],
    range(61, 71): ["TITAN_GRAVEYARD", "SHATTERED_HEART", "SEVERANCE_FAULTLINE"],
    range(71, 81): ["ETERNAL_GATE", "PRIMA_MATERIA_FORGE", "AETHEL_SIPHON_CORE"],
    range(81, 100): ["ETERNAL_GATE", "SEVERANCE_FAULTLINE", "PRIMA_MATERIA_FORGE"],
}

REWARD_ITEMS = {
    range(1, 21): ("cns_health_potion_small", 2),
    range(21, 41): ("advanced_hp_potion", 2),
    range(41, 61): ("con_large_hp_cell", 2),
    range(61, 81): ("itm_greater_hp_potion", 2),
    range(81, 100): ("itm_phoenix_core", 1),
}

FACTION_VOICE = {
    "CONCORDIUM": "Concordium command marks this threat as a danger to civil order",
    "THE_ARCANUM_SEEKERS": "Arcanum readings identify this target as a source of unstable aethel resonance",
    "IRON_HEGEMONY": "Hegemony command demands a decisive field operation",
    "MERIDIAN_CARTEL": "Cartel intelligence identifies a profitable threat-removal contract",
    "OMNICORP": "OmniCorp analytics classify this target as an unacceptable operational liability",
    "CHILDREN_OF_THE_SHARD": "The Shard's resonance warns that this creature disrupts the living balance",
    "STARFORGED_LEGION": "Legion command designates this target a test of discipline and battlefield resolve",
}

STORY_ARCS = {
    "CONCORDIUM": [
        ("Garden Mandate", "secure the first settlement routes and protect the civic population"),
        ("Broken Charter", "recover order in the abandoned civil quarter without abandoning Concordium law"),
        ("Cradle Authority", "hold the outer Cradle while rival powers contest Prima Materia"),
        ("Severance Inquiry", "verify evidence of the Great Severance before issuing planetary orders"),
        ("Stewardship of the Siphon", "keep the Aethel Siphon stable while negotiating who may govern Xylos"),
    ],
    "THE_ARCANUM_SEEKERS": [
        ("Field Specimens", "collect controlled observations of Xylos life and Aethel exposure"),
        ("Glass Archive", "trace crystal formations toward sealed Aethelgardian records"),
        ("Resonance Protocol", "measure dangerous pulses without letting the Hegemony seize the instruments"),
        ("Severance Proof", "test whether the Great Severance was an accident or a deliberate intervention"),
        ("Prima Materia Thesis", "reach the Forge and Siphon data needed to understand the planet's energy cycle"),
    ],
    "IRON_HEGEMONY": [
        ("Supply Discipline", "secure salvage and enforce Bastion's field command"),
        ("Ravine Doctrine", "clear Iron Ravine defenses and prepare the heavy advance"),
        ("Graveyard Recovery", "claim usable war machines before rival scavengers strip them"),
        ("Titan Muster", "assemble a force capable of holding the contested Cradle"),
        ("Armistice by Force", "control the approaches to the Forge and compel a durable planetary order"),
    ],
    "MERIDIAN_CARTEL": [
        ("Opening Contract", "protect Meridian's routes and make every expedition pay its debts"),
        ("Jungle Ledger", "map the smugglers who move goods beyond official tariffs"),
        ("Black Dock Accounts", "break a rival network and secure its names, cargo, and leverage"),
        ("Sunken Clauses", "recover Aethel-era assets before governments can claim them"),
        ("Market for a World", "control the supply lines around the Forge and bargain over the Siphon's future"),
    ],
    "OMNICORP": [
        ("Asset Survey", "classify the plateau's deposits and protect company equipment"),
        ("Delta Extraction", "keep the extraction corridor productive despite local resistance"),
        ("Grid Security", "restore the secure mining grid and contain unauthorized access"),
        ("Skybridge Control", "bring the reactor route under corporate operating authority"),
        ("Exclusive Future", "secure the Prima Materia chain and prevent Xylos from closing its export window"),
    ],
    "CHILDREN_OF_THE_SHARD": [
        ("Rite of Calming", "quiet the wounded life around the Shard without mistaking violence for healing"),
        ("Rootwater Cleansing", "purge the corruption spreading through the living wetlands"),
        ("Fragment Vigil", "guard the shrine fragments from those who would turn them into instruments"),
        ("Great Purification", "prepare the faithful for the promised end of industrial harvesting"),
        ("Voice of the Shard", "reach the source of the Aethel pulse and decide what must be sacrificed"),
    ],
    "STARFORGED_LEGION": [
        ("A Place in the Sand", "prove the newcomers can defend their camp and earn a place on Xylos"),
        ("Badland Oath", "secure water and passage through the scorched approaches"),
        ("Warpath Standard", "win the Mesa route through discipline and protect the Legion's people"),
        ("Canyon Claim", "take defensible ground without breaking the Legion's code of honor"),
        ("Home Earned", "hold the Eternal Gate and forge an honorable settlement amid the planetary crisis"),
    ],
}

TITLE_SEEDS = [
    "First Watch", "Broken Signal", "Ashes on the Route", "Quiet Perimeter", "A Debt Repaid",
    "The Missing Patrol", "Measure of Resolve", "A Narrow Passage", "Unclaimed Ground", "Before the Next Dawn",
    "Witness at the Ridge", "Supply Line", "The Last Warning", "A Question of Trust", "Outer Ring Report",
    "No Safe Shortcut", "Aethel Aftershock", "The Unquiet Machine", "Terms of Passage", "Report to Command",
]

LORE_TERMS = {
    "aethel": "Aethel", "prima materia": "Prima Materia", "great severance": "Great Severance",
    "xylos": "Xylos", "concordium law": "Concordium law", "outer cradle": "Outer Cradle",
    "the shard": "the Shard", "eternal gate": "Eternal Gate", "aethel siphon": "Aethel Siphon",
}

def preserve_lore_case(text):
    for source, target in LORE_TERMS.items():
        text = text.replace(source, target)
        text = text.replace(source.capitalize(), target)
    return text

FACTION_METADATA = {
    "CONCORDIUM": ("NEXUS_CORE", "AETHEL_GARDENS", "The old guard founded by Xylos's first explorers. It seeks planetary stability, regulated Prima Materia, and renewed unity under Nexus."),
    "THE_ARCANUM_SEEKERS": ("OBSERVATORY_SPIRE", "CRYSTAL_SLOPE", "A Concordium splinter devoted to unrestricted knowledge of Aethel energy, Aethelgardian vaults, and sentient evolution."),
    "IRON_HEGEMONY": ("BASTION_CORE", "SCRAP_FIELD", "The military-industrial power of Bastion pursues order through strength and control of every Prima Materia site."),
    "MERIDIAN_CARTEL": ("PORT_MERIDIAN", "CORAL_WETLANDS", "A network of former diplomats and merchants seeking influence through trade, intelligence, and economic dependence."),
    "OMNICORP": ("THE_SPIRE", "HIGHLAND_PLATEAU", "An off-world corporation treating Xylos as a resource asset and seeking a proprietary Prima Materia supply chain."),
    "CHILDREN_OF_THE_SHARD": ("SANCTUM", "GLOWVINE_FOREST", "A faith devoted to the Aethel Shard that seeks to end technological harvesting through the Great Purification."),
    "STARFORGED_LEGION": ("FORTRESS_KAELEN", "DUNE_OUTSKIRTS", "A displaced warrior people seeking a defensible home through courage, discipline, and honorable alliances."),
}


def load(name):
    with (ROOT / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def save(name, data):
    with (ROOT / name).open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def tier_rank(level):
    if level <= 10:
        return "D"
    if level <= 20:
        return "C"
    if level <= 30:
        return "B"
    if level <= 40:
        return "A"
    if level <= 98:
        return "S"
    return "S+"


def rewards(level):
    if level <= 10:
        exp = 75 + (level - 1) * 30
        currency = 50 + (level - 1) * 15
        crd = 0
        reputation = 20 + level * 5
    elif level <= 20:
        exp = 350 + (level - 11) * 50
        currency = 200 + (level - 11) * 25
        crd = 0
        reputation = 75 + (level - 11) * 10
    elif level <= 30:
        exp = 700 + (level - 21) * 65
        currency = 400 + (level - 21) * 40
        crd = 0
        reputation = 175 + (level - 21) * 15
    elif level <= 40:
        exp = 1500 + (level - 31) * 165
        currency = 800 + (level - 31) * 130
        crd = 0
        reputation = 325 + (level - 31) * 20
    elif level <= 60:
        exp = 3000 + (level - 41) * 160
        currency = 2000 + (level - 41) * 75
        crd = 300 + (level - 41) * 10
        reputation = 550 + (level - 41) * 25
    elif level <= 80:
        exp = 6200 + (level - 61) * 200
        currency = 3500 + (level - 61) * 75
        crd = 500 + (level - 61) * 8
        reputation = 1050 + (level - 61) * 30
    elif level <= 98:
        exp = 10200 + (level - 81) * 330
        currency = 5000 + (level - 81) * 55
        crd = 660 + (level - 81) * 8
        reputation = 1650 + (level - 81) * 35
    else:
        exp = 30000
        currency = 10000
        crd = 2000
        reputation = 2500

    item_id, quantity = next(value for levels, value in REWARD_ITEMS.items() if level in levels)
    return {
        "exp": exp,
        "currency": currency,
        "crd": crd,
        "rep": reputation,
        "reputation": reputation,
        "items": [{"item_id": item_id, "quantity": quantity}],
    }


def region_and_monster(level, faction_regions, nodes, monsters):
    if level <= 40:
        region_options = [
            region for region in faction_regions
            if nodes[region]["level_range"][0] <= level
        ]
    else:
        shared = next(values for levels, values in SHARED_REGIONS.items() if level in levels)
        region_options = [
            region for region in shared
            if nodes[region]["level_range"][0] <= level
        ]

    candidates = []
    for region in region_options:
        spawn_ids = []
        for spawn in nodes[region].get("monster_spawns", []):
            monster_id = spawn.get("monster_id")
            if monster_id not in spawn_ids:
                spawn_ids.append(monster_id)
        for monster_id in spawn_ids:
            monster = monsters.get(monster_id)
            if monster and monster_id != 9999 and monster["level"] <= level + 5:
                candidates.append((region, monster))

    if not candidates and level > 1:
        # Some authored map regions have no low-level spawns; fall back to the
        # nearest eligible entry while still enforcing the quest-level ceiling.
        for node in nodes.values():
            if node.get("level_range", [0, 999])[0] > level + 5 or node.get("level_range", [0, 999])[1] < level - 5:
                continue
            for spawn in node.get("monster_spawns", []):
                monster = monsters.get(spawn.get("monster_id"))
                if monster and monster["level"] <= level + 5:
                    candidates.append((node["id"], monster))
    if not candidates:
        raise ValueError(f"No valid monster available at level {level}")
    return min(
        candidates,
        key=lambda pair: (abs(pair[1]["level"] - level), -pair[1]["level"]),
    )


def quest_content(faction, title, region, monster_name, count, level, arc_title, arc_goal, npc_name):
    voice = FACTION_VOICE[faction]
    region_name = region.replace("_", " ").title()
    arc_goal = preserve_lore_case(arc_goal.capitalize())
    description = (
        f"{arc_title}: {arc_goal}. {voice}. In {region_name}, "
        f"defeat {monster_name} (x{count}) to secure the next piece of the operation."
    )
    dialog = [
        {"speaker": npc_name, "text": f"{arc_title} is active. {arc_goal}."},
        {"speaker": npc_name, "text": f"Proceed to {region_name}; neutralize {monster_name} (x{count}) and keep the site usable."},
        {"speaker": npc_name, "text": f"{title}: this result will shape how our faction responds to Xylos."},
    ]
    return description, dialog


def make_missing(template, quest_id, title):
    quest = copy.deepcopy(template)
    quest["id"] = quest_id
    quest["title"] = title
    quest["description"] = f"A new operational window has opened. Complete {title.lower()} to keep the faction campaign moving toward the shared endgame front."
    return quest


def ensure_hundred(quests, config):
    by_id = {quest["id"]: quest for quest in quests}
    if len(quests) == 99:
        missing_number = next(number for number in range(1, 101) if f'{config["prefix"]}{number:03d}' not in by_id)
        previous_id = f'{config["prefix"]}{missing_number - 1:03d}'
        next_id = f'{config["prefix"]}{missing_number + 1:03d}'
        template = by_id.get(previous_id) or by_id.get(next_id) or quests[0]
        title = "Operational Continuity" if missing_number < 80 else "Endgame Convergence"
        by_id[f'{config["prefix"]}{missing_number:03d}'] = make_missing(template, f'{config["prefix"]}{missing_number:03d}', title)
    ordered = sorted(by_id.values(), key=lambda quest: int(quest["id"].rsplit("_", 1)[1]))
    if len(ordered) != 100:
        raise ValueError(f'{config["faction"]} must have 100 quests, got {len(ordered)}')
    return ordered


def main():
    world = load("world_map_v4.json")
    monster_data = load("monster_master.json")
    npc_data = load("npc_list.json")
    nodes = {node["id"]: node for node in world["nodes"]}
    monsters = {monster["monster_id"]: monster for monster in monster_data["monsters"]}
    npcs = {npc["npc_id"]: npc for npc in npc_data}

    # Keep master spawn records aligned with the regions that actually list them.
    for node in world["nodes"]:
        for spawn in node.get("monster_spawns", []):
            monster = monsters.get(spawn.get("monster_id"))
            if monster and node["id"] not in monster.setdefault("spawn_location", []):
                monster["spawn_location"].append(node["id"])
    save("monster_master.json", monster_data)

    faction_data = load("xylos_factions.json")
    for faction in faction_data["factions"]:
        metadata = FACTION_METADATA.get(faction["faction_code"])
        if metadata:
            faction["capital_region"], faction["starting_region"], faction["summary"] = metadata
    save("xylos_factions.json", faction_data)

    for filename, config in FACTIONS.items():
        data = load(filename)
        quests = ensure_hundred(data["quests"], config)
        cumulative_reputation = 0

        for index, quest in enumerate(quests):
            level = 1 if index < 2 else index
            arc_index = min(4, max(0, (level - 1) // 20))
            if level >= 41:
                arc_index = min(4, 2 + (level - 41) // 20)
            region, monster = region_and_monster(level, config["regions"], nodes, monsters)
            arc_title, arc_goal = STORY_ARCS[config["faction"]][arc_index]
            title = f"{arc_title}: {TITLE_SEEDS[index % len(TITLE_SEEDS)]} {index // len(TITLE_SEEDS) + 1:02d}"
            quest["title"] = title
            rank = tier_rank(level)
            boss = monster.get("rank") in {"area_boss", "leader", "raid_boss"}
            count = 1 if boss else min(12, 3 + level // 10)
            previous_id = quests[index - 1]["id"] if index > 0 else None
            next_id = quests[index + 1]["id"] if index + 1 < len(quests) else None

            quest["rank"] = rank
            quest["faction"] = config["faction"]
            quest["region"] = region
            quest["type"] = "boss" if boss else ("story" if index % 5 == 0 else "hunt")
            giver = quest.get("quest_giver", {})
            master_npc = npcs.get(giver.get("npc_id"))
            npc_name = master_npc["name"] if master_npc else giver.get("name", "Faction Handler")
            description, dialog_nodes = quest_content(
                config["faction"], title, region, monster["name"], count, level,
                arc_title, arc_goal, npc_name,
            )
            quest["description"] = description
            if master_npc:
                giver["name"] = master_npc["name"]
            giver["location"] = region
            quest["quest_giver"] = giver
            quest["requirements"] = {
                "min_level": level,
                "reputation_required": 0 if index < 2 else int(cumulative_reputation * 0.55),
                "required_quests": [previous_id] if previous_id else [],
                "required_items": [],
                "party_required": boss and level >= 75,
                "raid_size": 4 if boss and level >= 75 else 1,
            }
            quest["objectives"] = [
                {
                    "objective_id": "primary_target",
                    "type": "kill",
                    "target": monster["monster_id"],
                    "target_code": monster["code"],
                    "count": count,
                    "description": f'Defeat {monster["name"]} (x{count}).',
                }
            ]
            quest["rewards"] = rewards(level)
            quest["repeatable"] = False
            quest["daily"] = False
            quest["quest_chain_next"] = next_id
            quest["dialog_nodes"] = dialog_nodes
            cumulative_reputation += quest["rewards"]["reputation"]

        data["schema_version"] = 2
        data["progression"] = {
            "quest_count": 100,
            "level_range": [1, 99],
            "reward_curve": "faction_equal_v2",
            "endgame_start_level": 61,
        }
        data["quests"] = quests
        save(filename, data)
        print(f"Updated {filename}: {len(quests)} quests")

    # Give the neutral collection quests real item definitions and drop sources.
    items_data = load("item_list.json")
    item_ids = {item["id"] for item in items_data["items"]}
    for item_id, name, description in [
        ("ILLEGAL_WEAPON_CACHE", "Illegal Weapon Cache", "A sealed cache of illicit arms seized for a Custodian investigation."),
        ("COUNTERFEIT_CRD_SAMPLE", "Counterfeit CRD Sample", "A forged Credent sample flagged by the Aegis Monetary Authority."),
    ]:
        if item_id not in item_ids:
            items_data["items"].append({
                "id": item_id, "name": name, "description": description, "type": "QUEST",
                "rarity": "QUEST", "level_requirement": 1, "equipment_slots": [],
                "stats_bonus": {"atk": 0, "def": 0, "hp": 0, "mp": 0, "agi": 0, "per": 0},
                "special_effects": [], "buy_price": 0, "sell_price": 0, "max_stack": 99, "icon_image": "",
            })
    save("item_list.json", items_data)

    drop_sources = {
        5105: [("salvaged_supply_crate", 0.45), ("ILLEGAL_WEAPON_CACHE", 0.25)],
        5136: [("salvaged_alloy_fragment", 0.5)],
        5150: [("ILLEGAL_WEAPON_CACHE", 0.35)],
        5166: [("archive_scroll", 0.35)],
        5167: [("COUNTERFEIT_CRD_SAMPLE", 0.4)],
    }
    for monster_id, drops in drop_sources.items():
        for item_id, chance in drops:
            if not any(drop["itemId"] == item_id for drop in monsters[monster_id].get("drop_item", [])):
                monsters[monster_id].setdefault("drop_item", []).append({"itemId": item_id, "chance": chance})
    save("monster_master.json", monster_data)


if __name__ == "__main__":
    main()
