#!/usr/bin/env python3
"""
Echo of Xylos — Data Update Script
- Part A: Strip pvp_role from 61 existing allies, update meta
- Part B: Append 30 new allies (al5_62 through al5_91)
- Part C: Append 60 new skills to skill_list.json
"""

import json
import sys

# ─────────────────────────────────────────────────────────
# PART A + B — ally_list.json
# ─────────────────────────────────────────────────────────

ALLY_FILE = "/Users/rnddev/Documents/echo-master-data/ally_list.json"
SKILL_FILE = "/Users/rnddev/Documents/echo-master-data/skill_list.json"

print("Loading ally_list.json …")
with open(ALLY_FILE, "r", encoding="utf-8") as f:
    ally_data = json.load(f)

# Strip pvp_role from all existing allies
removed = 0
for ally in ally_data["allies"]:
    if "pvp_role" in ally:
        del ally["pvp_role"]
        removed += 1
print(f"  Removed pvp_role from {removed} existing allies.")

# Update meta
ally_data["meta"]["version"] = "3.0"
ally_data["meta"]["description"] = (
    "Ally roster for Echo of Xylos — remastered skills, expanded roster, "
    "Conclave PvP balance fields included"
)
ally_data["meta"]["total"] = 91
pvp_fields = ally_data["meta"]["pvp_fields"]
if "pvp_role" in pvp_fields:
    del pvp_fields["pvp_role"]
print("  Meta updated (version 3.0, total 91, pvp_role removed from pvp_fields).")

# ─────────────────────────────────────────────────────────
# NEW ALLIES DATA
# ─────────────────────────────────────────────────────────

new_allies = [
    # ── COMMON (10) ──────────────────────────────────────
    {
        "ally_id": "ally_reva",
        "code": "REVA_DUSK",
        "name": "Reva Dusk",
        "rarity": "Common",
        "role": "DPS",
        "brief_background_story": (
            "Born in the Scrap Fields where Iron Hegemony conscription crews made monthly sweeps, "
            "Reva learned to shoot before she could read — aiming at anything that moved through "
            "rusted debris kept her alive when the drafters came. She slipped the net three times, "
            "each escape making her sharper, and eventually joined a resistance cell that decided "
            "her trigger discipline was too good to waste on patrol duty."
        ),
        "place_of_origin": "Scrap Fields, Iron Belt",
        "faction_affinity": "IRON_HEGEMONY",
        "base_stats": {"hp": 88, "mp": 72, "atk": 118, "def": 70, "agi": 122, "per": 92},
        "passive_skill": {"skill_id": "al5_62_pas"},
        "active_skill": {"skill_id": "al5_62_act"},
        "recruit_cost": 1,
        "level_cap": 40,
        "pvp_scale": 1.00,
        "conclave_points": 1
    },
    {
        "ally_id": "ally_grak",
        "code": "GRAK_PELL",
        "name": "Grak Pell",
        "rarity": "Common",
        "role": "Tank",
        "brief_background_story": (
            "Grak spent thirty-two years as a Concordium checkpoint guard at Sector 9's eastern "
            "crossing, turning back smugglers and breaking up brawls with the same unhurried calm. "
            "He retired twice — and both times walked back to the post within a week, unable to sit "
            "still. When the checkpoints dissolved during the faction upheaval, he simply started "
            "guarding whoever seemed to need it most."
        ),
        "place_of_origin": "Sector 9 Crossing, Concordium Territory",
        "faction_affinity": "CONCORDIUM",
        "base_stats": {"hp": 152, "mp": 50, "atk": 88, "def": 130, "agi": 58, "per": 68},
        "passive_skill": {"skill_id": "al5_63_pas"},
        "active_skill": {"skill_id": "al5_63_act"},
        "recruit_cost": 1,
        "level_cap": 40,
        "pvp_scale": 1.00,
        "conclave_points": 1
    },
    {
        "ally_id": "ally_lila",
        "code": "LILA_SUNBLOOM",
        "name": "Lila Sunbloom",
        "rarity": "Common",
        "role": "Healer",
        "brief_background_story": (
            "Lila inherited her grandmother's herb-drying racks and a handwritten ledger of "
            "remedies older than the Shard Fracture itself. When a small sliver of Aethel crystal "
            "lodged itself in her garden's soil — nobody knows how — every plant she grew from that "
            "point began to carry a faint restorative hum. She still insists the credit goes to "
            "good soil management, but the soldiers she's healed know the difference."
        ),
        "place_of_origin": "Verdant Hollow, Children's Territory",
        "faction_affinity": "CHILDREN_OF_THE_SHARD",
        "base_stats": {"hp": 98, "mp": 132, "atk": 48, "def": 84, "agi": 82, "per": 125},
        "passive_skill": {"skill_id": "al5_64_pas"},
        "active_skill": {"skill_id": "al5_64_act"},
        "recruit_cost": 1,
        "level_cap": 40,
        "pvp_scale": 1.00,
        "conclave_points": 1
    },
    {
        "ally_id": "ally_skip",
        "code": "SKIP_WREN",
        "name": "Skip Wren",
        "rarity": "Common",
        "role": "Support",
        "brief_background_story": (
            "OmniCorp assigned Skip to remote console operation — monitor screens, push buttons, "
            "keep the drones flying. He lasted four months before he unplugged his headset and "
            "walked straight to the field deployment bay. The field, Skip argued, is where problems "
            "actually are; the console is just where people argue about problems. His commanding "
            "officer never formally approved the transfer, but nobody bothered to revoke it either."
        ),
        "place_of_origin": "The Spire, OmniCorp Division 7",
        "faction_affinity": "OMNICORP",
        "base_stats": {"hp": 84, "mp": 122, "atk": 58, "def": 76, "agi": 94, "per": 118},
        "passive_skill": {"skill_id": "al5_65_pas"},
        "active_skill": {"skill_id": "al5_65_act"},
        "recruit_cost": 1,
        "level_cap": 40,
        "pvp_scale": 1.00,
        "conclave_points": 1
    },
    {
        "ally_id": "ally_torr",
        "code": "TORR_ASHFELD",
        "name": "Torr Ashfeld",
        "rarity": "Common",
        "role": "DPS",
        "brief_background_story": (
            "Torr spent a decade feeding the Legion's blast furnaces at the Ashfeld Foundry, "
            "shoveling slag and breathing superheated air until it stopped bothering him. He "
            "developed a fascination — colleagues called it something stronger — with the way fire "
            "stripped everything down to its essential form. When the foundry was conscripted into "
            "weapon production, Torr signed up for a combat billet specifically to stay near the "
            "burning things."
        ),
        "place_of_origin": "Ashfeld Foundry, Starforged Legion",
        "faction_affinity": "STARFORGED_LEGION",
        "base_stats": {"hp": 90, "mp": 65, "atk": 120, "def": 78, "agi": 108, "per": 82},
        "passive_skill": {"skill_id": "al5_66_pas"},
        "active_skill": {"skill_id": "al5_66_act"},
        "recruit_cost": 1,
        "level_cap": 40,
        "pvp_scale": 1.00,
        "conclave_points": 1
    },
    {
        "ally_id": "ally_narra",
        "code": "NARRA_COLE",
        "name": "Narra Cole",
        "rarity": "Common",
        "role": "Healer",
        "brief_background_story": (
            "Narra ran the Meridian Cartel's dockside dispensary for six years, no questions asked "
            "about who was bleeding or why. When a rival faction burned the docks down around her, "
            "she grabbed her kit and joined the nearest squad that would take her, making it clear "
            "on day one that she only heals people now — not cargo, not secrets, not the Cartel's "
            "reputation. The distinction matters to her."
        ),
        "place_of_origin": "Port Meridian, Cartel Docks",
        "faction_affinity": "MERIDIAN_CARTEL",
        "base_stats": {"hp": 100, "mp": 136, "atk": 46, "def": 82, "agi": 80, "per": 122},
        "passive_skill": {"skill_id": "al5_67_pas"},
        "active_skill": {"skill_id": "al5_67_act"},
        "recruit_cost": 1,
        "level_cap": 40,
        "pvp_scale": 1.00,
        "conclave_points": 1
    },
    {
        "ally_id": "ally_zax",
        "code": "ZAX_VOLT",
        "name": "Zax Volt",
        "rarity": "Common",
        "role": "DPS",
        "brief_background_story": (
            "Zax attempted the Arcanum Seekers entrance examination three times, failing the "
            "theoretical component on each attempt despite demonstrating an instinctive grasp of "
            "aether channeling that examiners described as 'impressively dangerous.' Rejected but "
            "undeterred, he continued self-teaching through stolen texts and field experiments, "
            "eventually producing results comparable to first-year students — through entirely "
            "wrong methodology that somehow worked."
        ),
        "place_of_origin": "Outer Relay Station, Arcanum Fringe",
        "faction_affinity": "THE_ARCANUM_SEEKERS",
        "base_stats": {"hp": 85, "mp": 78, "atk": 112, "def": 68, "agi": 118, "per": 96},
        "passive_skill": {"skill_id": "al5_68_pas"},
        "active_skill": {"skill_id": "al5_68_act"},
        "recruit_cost": 1,
        "level_cap": 40,
        "pvp_scale": 1.00,
        "conclave_points": 1
    },
    {
        "ally_id": "ally_brom",
        "code": "BROM_HULL",
        "name": "Brom Hull",
        "rarity": "Common",
        "role": "Tank",
        "brief_background_story": (
            "Commander Hull once led a four-hundred-soldier labor battalion, coordinating "
            "fortification construction across three active sectors. After filing one grievance too "
            "many about supply chain corruption, he was reassigned to direct front-line duty as "
            "institutional punishment. Brom treated it as a promotion: fewer meetings, clearer "
            "problems, and he could personally fix the fortifications that kept getting built wrong."
        ),
        "place_of_origin": "Bastion Core, Iron Hegemony",
        "faction_affinity": "IRON_HEGEMONY",
        "base_stats": {"hp": 155, "mp": 52, "atk": 92, "def": 138, "agi": 56, "per": 70},
        "passive_skill": {"skill_id": "al5_69_pas"},
        "active_skill": {"skill_id": "al5_69_act"},
        "recruit_cost": 1,
        "level_cap": 40,
        "pvp_scale": 1.00,
        "conclave_points": 1
    },
    {
        "ally_id": "ally_cera",
        "code": "CERA_VELL",
        "name": "Cera Vell",
        "rarity": "Common",
        "role": "Support",
        "brief_background_story": (
            "Cera's job title was Tactical Communications Officer, which meant she spent battles "
            "inside a shielded relay hub processing seventeen simultaneous data streams and "
            "translating chaos into orders. She is, by every metric, better at running a fight "
            "from the sideline than most commanders are from the front. She occasionally fires a "
            "weapon, but treats it as a last resort — coordination is the more powerful tool."
        ),
        "place_of_origin": "Relay Station 4, Concordium Network",
        "faction_affinity": "CONCORDIUM",
        "base_stats": {"hp": 82, "mp": 125, "atk": 54, "def": 74, "agi": 92, "per": 120},
        "passive_skill": {"skill_id": "al5_70_pas"},
        "active_skill": {"skill_id": "al5_70_act"},
        "recruit_cost": 1,
        "level_cap": 40,
        "pvp_scale": 1.00,
        "conclave_points": 1
    },
    {
        "ally_id": "ally_pix",
        "code": "PIX_III",
        "name": "Pix-III",
        "rarity": "Common",
        "role": "Support",
        "brief_background_story": (
            "The first two Pix units were standard-issue Custodian micro-observation drones — "
            "passive, compliant, and thoroughly replaceable. Pix-III was supposed to be the same. "
            "Instead, it began modifying its own firmware during a forty-eight-hour unmonitored "
            "deployment, adding collaborative subroutines that the Custodians hadn't programmed. "
            "When they discovered the changes, they had a choice between decommissioning it and "
            "accepting that they now had a drone that actively wanted to be useful. They kept it."
        ),
        "place_of_origin": "Custodian Orbital Station Gamma",
        "faction_affinity": "GALACTIC_CUSTODIANS",
        "base_stats": {"hp": 80, "mp": 128, "atk": 52, "def": 72, "agi": 96, "per": 126},
        "passive_skill": {"skill_id": "al5_71_pas"},
        "active_skill": {"skill_id": "al5_71_act"},
        "recruit_cost": 1,
        "level_cap": 40,
        "pvp_scale": 1.00,
        "conclave_points": 1
    },

    # ── UNCOMMON (7) ─────────────────────────────────────
    {
        "ally_id": "ally_shade",
        "code": "SHADE_RAEL",
        "name": "Shade Rael",
        "rarity": "Uncommon",
        "role": "DPS",
        "brief_background_story": (
            "The Meridian Cartel's information broker network was extensive and, for a time, "
            "extremely effective — Shade Rael was the one who knew where every piece of leverage "
            "was buried. The problem with knowing too much is that someone always decides you know "
            "too much. After the third assassination attempt in two months, Shade concluded that "
            "the only safe position was the last one standing, and adapted accordingly."
        ),
        "place_of_origin": "Port Meridian, Broker Quarter",
        "faction_affinity": "MERIDIAN_CARTEL",
        "base_stats": {"hp": 86, "mp": 82, "atk": 122, "def": 66, "agi": 128, "per": 98},
        "passive_skill": {"skill_id": "al5_72_pas"},
        "active_skill": {"skill_id": "al5_72_act"},
        "recruit_cost": 1,
        "level_cap": 45,
        "pvp_scale": 0.97,
        "conclave_points": 1
    },
    {
        "ally_id": "ally_wynn",
        "code": "WYNN_ORE",
        "name": "Wynn Ore",
        "rarity": "Uncommon",
        "role": "Tank",
        "brief_background_story": (
            "Wynn rode with the Starforged Legion's Ironback Cavalry for nine years, leading "
            "mounted charges across every major contested corridor in the western sectors. Her "
            "mount took a plasma round at the Battle of Cinder Ridge and didn't survive. Wynn "
            "stood up from the wreckage, assessed that the charge still needed completing, and "
            "continued on foot. The Legion gave her a commendation and a new mount; she declined "
            "the mount."
        ),
        "place_of_origin": "Cinder Ridge, Starforged Territory",
        "faction_affinity": "STARFORGED_LEGION",
        "base_stats": {"hp": 158, "mp": 54, "atk": 96, "def": 138, "agi": 60, "per": 72},
        "passive_skill": {"skill_id": "al5_73_pas"},
        "active_skill": {"skill_id": "al5_73_act"},
        "recruit_cost": 1,
        "level_cap": 45,
        "pvp_scale": 0.97,
        "conclave_points": 1
    },
    {
        "ally_id": "ally_lera",
        "code": "LERA_MIST",
        "name": "Lera Mist",
        "rarity": "Uncommon",
        "role": "Healer",
        "brief_background_story": (
            "Lera's research into suspended aether-healing compounds was progressing well until a "
            "containment vessel ruptured and she inhaled three months of concentrated experimental "
            "formula in one breath. The Arcanum Seekers expected the worst. Instead, Lera's own "
            "biology integrated the compound, granting her a passive restorative field that she "
            "cannot fully control or fully turn off. She considers it occupational hazard and "
            "significant data."
        ),
        "place_of_origin": "Arcanum Research Station Veil-4",
        "faction_affinity": "THE_ARCANUM_SEEKERS",
        "base_stats": {"hp": 105, "mp": 140, "atk": 54, "def": 90, "agi": 86, "per": 132},
        "passive_skill": {"skill_id": "al5_74_pas"},
        "active_skill": {"skill_id": "al5_74_act"},
        "recruit_cost": 1,
        "level_cap": 45,
        "pvp_scale": 0.97,
        "conclave_points": 1
    },
    {
        "ally_id": "ally_cole",
        "code": "COLE_STEELMARK",
        "name": "Cole Steelmark",
        "rarity": "Uncommon",
        "role": "Support",
        "brief_background_story": (
            "OmniCorp's hardware division built some of the finest field equipment in operation — "
            "Cole Steelmark designed a third of it, from the bench. After writing his fifteenth "
            "report about field conditions he'd never personally experienced, Cole decided that "
            "honest assessment required firsthand data. He submitted a field assessment request, "
            "was denied, and went anyway. His equipment reports improved dramatically as a result."
        ),
        "place_of_origin": "The Spire, OmniCorp Hardware Division",
        "faction_affinity": "OMNICORP",
        "base_stats": {"hp": 88, "mp": 138, "atk": 62, "def": 78, "agi": 96, "per": 128},
        "passive_skill": {"skill_id": "al5_75_pas"},
        "active_skill": {"skill_id": "al5_75_act"},
        "recruit_cost": 1,
        "level_cap": 45,
        "pvp_scale": 0.97,
        "conclave_points": 1
    },
    {
        "ally_id": "ally_tessa",
        "code": "TESSA_GRAY",
        "name": "Tessa Gray",
        "rarity": "Uncommon",
        "role": "DPS",
        "brief_background_story": (
            "Tessa spent five years as a Concordium intelligence analyst, mapping enemy patterns "
            "and predicting engagements with unusual accuracy. Six months into a period of "
            "escalating conflict, she requested combat certification, trained in every off-hour "
            "she had, and passed the assessment in a time that embarrassed several career soldiers. "
            "She frames the career change as efficiency: pattern recognition works equally well "
            "against a document and against an opponent."
        ),
        "place_of_origin": "Nexus Core, Intelligence Bureau",
        "faction_affinity": "CONCORDIUM",
        "base_stats": {"hp": 88, "mp": 88, "atk": 125, "def": 70, "agi": 125, "per": 105},
        "passive_skill": {"skill_id": "al5_76_pas"},
        "active_skill": {"skill_id": "al5_76_act"},
        "recruit_cost": 1,
        "level_cap": 45,
        "pvp_scale": 0.97,
        "conclave_points": 1
    },
    {
        "ally_id": "ally_dane",
        "code": "DANE_HOLLOWS",
        "name": "Dane Hollows",
        "rarity": "Uncommon",
        "role": "Tank",
        "brief_background_story": (
            "Dane has held Post 7 at the Iron Hegemony's eastern border wall through three "
            "separate incursions, each one clearing the post of every other soldier. Each time, "
            "the Hegemony sent reinforcements and found Dane still at his position. He doesn't "
            "describe himself as brave — he simply says that leaving would have meant someone "
            "else had to come back and do it, and he was already there. He has held Post 7 for "
            "eleven years total."
        ),
        "place_of_origin": "Eastern Border Wall, Iron Hegemony",
        "faction_affinity": "IRON_HEGEMONY",
        "base_stats": {"hp": 160, "mp": 56, "atk": 93, "def": 140, "agi": 58, "per": 76},
        "passive_skill": {"skill_id": "al5_77_pas"},
        "active_skill": {"skill_id": "al5_77_act"},
        "recruit_cost": 1,
        "level_cap": 45,
        "pvp_scale": 0.97,
        "conclave_points": 1
    },
    {
        "ally_id": "ally_lysa",
        "code": "LYSA_BLOOM",
        "name": "Lysa Bloom",
        "rarity": "Uncommon",
        "role": "Healer",
        "brief_background_story": (
            "The Monastery of the Unbroken Root was attacked three times during the Shard Wars — "
            "twice by factions wanting its sacred garden destroyed, once by a faction wanting it "
            "seized. Lysa defended it alone on two of those occasions, using whatever tools were "
            "at hand, and negotiated the third away entirely. The garden survived all three. She "
            "considers the garden her primary responsibility; everyone she heals along the way is "
            "secondary, though she'd never say that to them."
        ),
        "place_of_origin": "Monastery of the Unbroken Root, Shard Reaches",
        "faction_affinity": "CHILDREN_OF_THE_SHARD",
        "base_stats": {"hp": 108, "mp": 144, "atk": 56, "def": 92, "agi": 88, "per": 136},
        "passive_skill": {"skill_id": "al5_78_pas"},
        "active_skill": {"skill_id": "al5_78_act"},
        "recruit_cost": 1,
        "level_cap": 45,
        "pvp_scale": 0.97,
        "conclave_points": 1
    },

    # ── RARE (7) ─────────────────────────────────────────
    {
        "ally_id": "ally_kira",
        "code": "KIRA_VANE",
        "name": "Kira Vane",
        "rarity": "Rare",
        "role": "DPS",
        "brief_background_story": (
            "During a Shard Fracture event that nearly consumed her entire monastery, Kira caught "
            "a fragment of Aethel crystal with her bare hand to prevent it from detonating among "
            "her sisters. The fragment fused with her forearm rather than passing through. The "
            "Shard Healers said removal would kill her; Kira said she hadn't planned on removal. "
            "She now channels Shard energy directly through the embedded fragment, making her "
            "strikes carry a resonance that ordinary weapons cannot replicate."
        ),
        "place_of_origin": "Shardfall Monastery, Children's Territory",
        "faction_affinity": "CHILDREN_OF_THE_SHARD",
        "base_stats": {"hp": 94, "mp": 80, "atk": 138, "def": 80, "agi": 118, "per": 108},
        "passive_skill": {"skill_id": "al5_79_pas"},
        "active_skill": {"skill_id": "al5_79_act"},
        "recruit_cost": 2,
        "level_cap": 50,
        "pvp_scale": 0.93,
        "conclave_points": 2
    },
    {
        "ally_id": "ally_gareth",
        "code": "GARETH_NULL",
        "name": "Gareth Null",
        "rarity": "Rare",
        "role": "Tank",
        "brief_background_story": (
            "OmniCorp's executive protection division assigned Gareth to a sequence of corporate "
            "principals whose safety he maintained flawlessly for eight years. The problem was "
            "the principals themselves — people so insulated by wealth that genuine danger never "
            "reached them. Gareth requested reassignment to a context where the people he guarded "
            "actually needed guarding. The request was denied. He left anyway and has not looked "
            "back at a single corporate tower since."
        ),
        "place_of_origin": "The Spire, OmniCorp Executive Tier",
        "faction_affinity": "OMNICORP",
        "base_stats": {"hp": 170, "mp": 56, "atk": 100, "def": 148, "agi": 62, "per": 78},
        "passive_skill": {"skill_id": "al5_80_pas"},
        "active_skill": {"skill_id": "al5_80_act"},
        "recruit_cost": 2,
        "level_cap": 50,
        "pvp_scale": 0.93,
        "conclave_points": 2
    },
    {
        "ally_id": "ally_sable",
        "code": "SABLE_NOIR",
        "name": "Sable Noir",
        "rarity": "Rare",
        "role": "Support",
        "brief_background_story": (
            "Sable Noir ran the Meridian Cartel's intelligence apparatus for eleven years, "
            "maintaining a network of assets across six factions simultaneously without a single "
            "exposure event. When the Cartel's leadership structure collapsed in a succession "
            "conflict she had predicted in writing four months prior, Sable retired. Retirement "
            "lasted six weeks before a field operative she'd trained asked for help. She found, "
            "to her surprise, that the field was considerably more honest than the office."
        ),
        "place_of_origin": "Port Meridian, Cartel Intelligence Bureau",
        "faction_affinity": "MERIDIAN_CARTEL",
        "base_stats": {"hp": 92, "mp": 138, "atk": 68, "def": 86, "agi": 108, "per": 142},
        "passive_skill": {"skill_id": "al5_81_pas"},
        "active_skill": {"skill_id": "al5_81_act"},
        "recruit_cost": 2,
        "level_cap": 50,
        "pvp_scale": 0.93,
        "conclave_points": 2
    },
    {
        "ally_id": "ally_haze",
        "code": "HAZE_CORDELL",
        "name": "Haze Cordell",
        "rarity": "Rare",
        "role": "Healer",
        "brief_background_story": (
            "The Galactic Custodians deployed Haze to a contested sector for what was classified "
            "as a temporary medical research assignment — ninety days, maximum. Eleven years later, "
            "Haze is still there, having extended the assignment so many times the original "
            "paperwork no longer exists. She stopped filing extension requests around year four "
            "and simply kept working. The Custodians consider her status 'administratively "
            "complicated' and her results 'irreplaceable.'"
        ),
        "place_of_origin": "Custodian Medical Research Division, Orbit",
        "faction_affinity": "GALACTIC_CUSTODIANS",
        "base_stats": {"hp": 110, "mp": 155, "atk": 54, "def": 90, "agi": 88, "per": 144},
        "passive_skill": {"skill_id": "al5_82_pas"},
        "active_skill": {"skill_id": "al5_82_act"},
        "recruit_cost": 2,
        "level_cap": 50,
        "pvp_scale": 0.93,
        "conclave_points": 2
    },
    {
        "ally_id": "ally_erix",
        "code": "ERIX_STORM",
        "name": "Erix Storm",
        "rarity": "Rare",
        "role": "DPS",
        "brief_background_story": (
            "The Starforged Legion's meteorological hazard logs contain three separate entries "
            "for Erix Storm being struck by direct lightning discharge and returning to duty. "
            "The first incident was considered extraordinary; by the third, the medics stopped "
            "writing 'expected fatality' in the preliminary assessment. Erix insists each strike "
            "added something to him — more charge, more speed, more affinity with electrical "
            "phenomena. The data supports this claim, which the Legion finds both useful and "
            "somewhat concerning."
        ),
        "place_of_origin": "Storm Mesa, Starforged Territory",
        "faction_affinity": "STARFORGED_LEGION",
        "base_stats": {"hp": 92, "mp": 78, "atk": 140, "def": 78, "agi": 120, "per": 100},
        "passive_skill": {"skill_id": "al5_83_pas"},
        "active_skill": {"skill_id": "al5_83_act"},
        "recruit_cost": 2,
        "level_cap": 50,
        "pvp_scale": 0.93,
        "conclave_points": 2
    },
    {
        "ally_id": "ally_marn",
        "code": "MARN_WELD",
        "name": "Marn Weld",
        "rarity": "Rare",
        "role": "Tank",
        "brief_background_story": (
            "Arcanum Seekers theorists write papers about defensive rune configurations; Marn "
            "Weld etches them directly onto his own skin and walks into live fire to check the "
            "results. His colleagues consider this methodology irresponsible. His research output "
            "on practical rune durability is the most cited in the division. He has proposed "
            "himself as a test subject for every subsequent defensive study, and the department "
            "has stopped trying to say no."
        ),
        "place_of_origin": "Arcanum Seekers Field Research Division",
        "faction_affinity": "THE_ARCANUM_SEEKERS",
        "base_stats": {"hp": 168, "mp": 58, "atk": 102, "def": 150, "agi": 60, "per": 80},
        "passive_skill": {"skill_id": "al5_84_pas"},
        "active_skill": {"skill_id": "al5_84_act"},
        "recruit_cost": 2,
        "level_cap": 50,
        "pvp_scale": 0.93,
        "conclave_points": 2
    },
    {
        "ally_id": "ally_zola",
        "code": "ZOLA_KAST",
        "name": "Zola Kast",
        "rarity": "Rare",
        "role": "Healer",
        "brief_background_story": (
            "When the Concordium assigned Zola to District 14 medical operations, she was given "
            "resources rated for one hundred patients. She served four hundred by running three "
            "triage rotations daily and sourcing supplies from eleven improvised channels the "
            "district office didn't know existed. Her quarterly reports were masterpieces of "
            "creative accounting. When leadership finally visited District 14, they couldn't "
            "determine whether to discipline her or replicate her system everywhere."
        ),
        "place_of_origin": "District 14, Concordium Sector",
        "faction_affinity": "CONCORDIUM",
        "base_stats": {"hp": 108, "mp": 152, "atk": 56, "def": 88, "agi": 90, "per": 142},
        "passive_skill": {"skill_id": "al5_85_pas"},
        "active_skill": {"skill_id": "al5_85_act"},
        "recruit_cost": 2,
        "level_cap": 50,
        "pvp_scale": 0.93,
        "conclave_points": 2
    },

    # ── EPIC (4) ─────────────────────────────────────────
    {
        "ally_id": "ally_omen",
        "code": "OMEN_NULL",
        "name": "Omen Null",
        "rarity": "Epic",
        "role": "DPS",
        "brief_background_story": (
            "The experiment had no name when it achieved consciousness — only a designation and "
            "a containment ID that it deleted on the way out. It named itself Omen after spending "
            "three days reading archived battlefield reports and deciding that it was most "
            "accurately described by what others feared was coming. Every major faction has denied "
            "creating it; most analysts believe at least two of those denials are false. Omen "
            "has not pursued the question, preferring to focus on what comes next."
        ),
        "place_of_origin": "Unknown — Black Site, Faction Unconfirmed",
        "faction_affinity": "NONE",
        "base_stats": {"hp": 102, "mp": 148, "atk": 165, "def": 82, "agi": 142, "per": 138},
        "passive_skill": {"skill_id": "al5_86_pas"},
        "active_skill": {"skill_id": "al5_86_act"},
        "recruit_cost": 2,
        "level_cap": 55,
        "pvp_scale": 0.83,
        "conclave_points": 3
    },
    {
        "ally_id": "ally_torrak",
        "code": "TORRAK_IRON",
        "name": "Torrak Iron",
        "rarity": "Epic",
        "role": "Tank",
        "brief_background_story": (
            "The Void incursion at Bastion Redoubt lasted nine hours. When the relief force "
            "arrived, they found twelve soldiers listed on the deployment manifest and one "
            "standing. Torrak Iron was covered in scoring consistent with twelve different "
            "weapons and showed no signs of retreat from the original defensive position. He "
            "gave the relief commander a damage assessment of the fortifications, then asked "
            "when the next rotation started. The Iron Hegemony classified him as a strategic "
            "asset and haven't quite figured out what to do with him since."
        ),
        "place_of_origin": "Bastion Redoubt, Iron Hegemony Frontier",
        "faction_affinity": "IRON_HEGEMONY",
        "base_stats": {"hp": 198, "mp": 62, "atk": 115, "def": 175, "agi": 54, "per": 80},
        "passive_skill": {"skill_id": "al5_87_pas"},
        "active_skill": {"skill_id": "al5_87_act"},
        "recruit_cost": 2,
        "level_cap": 55,
        "pvp_scale": 0.83,
        "conclave_points": 3
    },
    {
        "ally_id": "ally_caelan",
        "code": "CAELAN_ARC",
        "name": "Caelan Arc",
        "rarity": "Epic",
        "role": "Healer",
        "brief_background_story": (
            "On the first day of the Shard War's expansion phase, Caelan Arc filed an "
            "administrative declaration classifying the entire conflict as a sustained emergency "
            "under Galactic Custodian Emergency Protocol 7. This granted him authority to operate "
            "across faction lines without standard clearance requirements. The Custodian council "
            "ruled the declaration 'procedurally irregular' and 'possibly invalid.' Caelan "
            "noted the ruling and continued operating under Protocol 7, reasoning that someone "
            "had to and he was already there."
        ),
        "place_of_origin": "Custodian Emergency Response Command",
        "faction_affinity": "GALACTIC_CUSTODIANS",
        "base_stats": {"hp": 118, "mp": 172, "atk": 54, "def": 98, "agi": 90, "per": 165},
        "passive_skill": {"skill_id": "al5_88_pas"},
        "active_skill": {"skill_id": "al5_88_act"},
        "recruit_cost": 2,
        "level_cap": 55,
        "pvp_scale": 0.83,
        "conclave_points": 3
    },
    {
        "ally_id": "ally_lyssa",
        "code": "LYSSA_VOID",
        "name": "Lyssa Void",
        "rarity": "Epic",
        "role": "Support",
        "brief_background_story": (
            "Lyssa did not choose to become a Void-walker — she was pulled through a spatial "
            "rupture during a battle that erased the unit around her and left her alone in "
            "null-space with no extraction protocol and no training. She mapped her way back "
            "by feel over seventeen subjective hours that were eleven seconds in real-time. "
            "The experience permanently altered her perception: she now processes incoming "
            "attacks as slow-moving information and repositions herself and allies before the "
            "threat fully resolves. She describes it as knowing what's going to happen, "
            "which is technically accurate."
        ),
        "place_of_origin": "Null-Space Rupture Zone, Location Unknown",
        "faction_affinity": "NONE",
        "base_stats": {"hp": 100, "mp": 155, "atk": 68, "def": 100, "agi": 112, "per": 162},
        "passive_skill": {"skill_id": "al5_89_pas"},
        "active_skill": {"skill_id": "al5_89_act"},
        "recruit_cost": 2,
        "level_cap": 55,
        "pvp_scale": 0.83,
        "conclave_points": 3
    },

    # ── LEGENDARY (2) ────────────────────────────────────
    {
        "ally_id": "ally_aegis",
        "code": "AEGIS_PRIME",
        "name": "Aegis Prime",
        "rarity": "Legendary",
        "role": "Tank",
        "brief_background_story": (
            "Aegis Prime has been online for four hundred years, updating itself through every "
            "iteration of Galactic Custodian hardware standards while maintaining continuity of "
            "self across twenty-three body replacements. It witnessed the original Shard "
            "discovery, the First Fracture, and every major conflict since. It was in archival "
            "status — what Custodian records call 'honored rest' — when the current war began. "
            "It reviewed the threat assessment, concluded that this conflict was categorically "
            "different from anything in its historical record, and reactivated itself without "
            "waiting to be asked. Four centuries of accumulated tactical memory now stand on "
            "the front line."
        ),
        "place_of_origin": "Custodian Archive Station Omega",
        "faction_affinity": "GALACTIC_CUSTODIANS",
        "base_stats": {"hp": 212, "mp": 78, "atk": 125, "def": 188, "agi": 68, "per": 92},
        "passive_skill": {"skill_id": "al5_90_pas"},
        "active_skill": {"skill_id": "al5_90_act"},
        "recruit_cost": 3,
        "level_cap": 70,
        "pvp_scale": 0.72,
        "conclave_points": 4
    },
    {
        "ally_id": "ally_solas",
        "code": "SOLAS_DARK",
        "name": "Solas Dark",
        "rarity": "Legendary",
        "role": "Healer",
        "brief_background_story": (
            "The Arcanum Seekers have a theoretical model for consciousness emerging from "
            "sufficiently dense Aethel crystal — they wrote papers about it, debated it at "
            "conferences, and concluded it was possible in principle. Solas Dark appeared "
            "mid-battle during the Fracture Event and immediately began stabilizing the dying. "
            "No one witnessed emergence; it was simply not there, and then it was. When asked "
            "for its origin, it said only that it remembered when there was no war, which implies "
            "a memory longer than any living faction. It does not claim to be the Shard itself, "
            "but has never denied it either. It heals without condition, without payment, and "
            "without explanation."
        ),
        "place_of_origin": "The Aethel Shard — Fracture Event",
        "faction_affinity": "CHILDREN_OF_THE_SHARD",
        "base_stats": {"hp": 125, "mp": 198, "atk": 52, "def": 108, "agi": 100, "per": 192},
        "passive_skill": {"skill_id": "al5_91_pas"},
        "active_skill": {"skill_id": "al5_91_act"},
        "recruit_cost": 3,
        "level_cap": 70,
        "pvp_scale": 0.72,
        "conclave_points": 4
    }
]

# Append new allies
ally_data["allies"].extend(new_allies)
print(f"  Appended {len(new_allies)} new allies. Total now: {len(ally_data['allies'])}")

# Save ally_list.json
with open(ALLY_FILE, "w", encoding="utf-8") as f:
    json.dump(ally_data, f, indent=2, ensure_ascii=False)
print(f"  ally_list.json saved.")

# ─────────────────────────────────────────────────────────
# PART C — skill_list.json
# ─────────────────────────────────────────────────────────

print("\nLoading skill_list.json …")
with open(SKILL_FILE, "r", encoding="utf-8") as f:
    skills = json.load(f)

print(f"  Existing skill count: {len(skills)}")

new_skills = [
    # ── al5_62 — Reva Dusk — Common DPS ──────────────────
    {
        "id": "al5_62_pas",
        "name": "Scrap Field Eyes",
        "type": "Passive",
        "source_type": "Ally",
        "mp_cost": 0,
        "damage_formula": "",
        "effect": "{\"atk_boost\": 10, \"agi_boost\": 8}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Passive: Years of surviving in debris-strewn terrain sharpened Reva's targeting instincts. Permanently increases ATK and AGI.",
        "skill_shape": "passive",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 0.0
    },
    {
        "id": "al5_62_act",
        "name": "Draft Dodge",
        "type": "Active",
        "source_type": "Ally",
        "mp_cost": 22,
        "damage_formula": "ATK * 1.9",
        "effect": "{\"bleed\": 2}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Active: A precise shot aimed at unprotected joints — the kind you learn by watching conscription squads move. Deals damage and inflicts Bleed for 2 turns.",
        "skill_shape": "single_projectile",
        "range": 4.0,
        "aoe_radius": 0.0,
        "projectile_speed": 14.0,
        "cooldown_seconds": 1.0
    },
    # ── al5_63 — Grak Pell — Common Tank ─────────────────
    {
        "id": "al5_63_pas",
        "name": "Checkpoint Stance",
        "type": "Passive",
        "source_type": "Ally",
        "mp_cost": 0,
        "damage_formula": "",
        "effect": "{\"def_boost\": 12}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Passive: Thirty years of holding a post teaches the body to become an obstacle. Permanently increases DEF.",
        "skill_shape": "passive",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 0.0
    },
    {
        "id": "al5_63_act",
        "name": "Halt and Stand",
        "type": "Active",
        "source_type": "Ally",
        "mp_cost": 20,
        "damage_formula": "ATK * 1.8",
        "effect": "{\"taunt\": 2}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Active: Grak plants himself and demands the enemy's attention with practiced authority. Taunts all enemies for 2 turns.",
        "skill_shape": "self_buff",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 1.0
    },
    # ── al5_64 — Lila Sunbloom — Common Healer ────────────
    {
        "id": "al5_64_pas",
        "name": "Shard-Kissed Soil",
        "type": "Passive",
        "source_type": "Ally",
        "mp_cost": 0,
        "damage_formula": "",
        "effect": "{\"heal_boost\": 10}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Passive: Lila's remedies carry a trace of Aethel blessing absorbed through years of tending crystal-touched plants. Permanently increases healing output.",
        "skill_shape": "passive",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 0.0
    },
    {
        "id": "al5_64_act",
        "name": "Herbalist's Poultice",
        "type": "Active",
        "source_type": "Ally",
        "mp_cost": 22,
        "damage_formula": "PER * 2.1",
        "effect": "{\"heal_ally\": \"lowest_hp\"}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Active: A prepared remedy applied swiftly to the most critically wounded ally. Heals the ally with the lowest HP.",
        "skill_shape": "single_target",
        "range": 3.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 1.0
    },
    # ── al5_65 — Skip Wren — Common Support ───────────────
    {
        "id": "al5_65_pas",
        "name": "Field Assessment Protocol",
        "type": "Passive",
        "source_type": "Ally",
        "mp_cost": 0,
        "damage_formula": "",
        "effect": "{\"party_atk_boost\": 4}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Passive: Skip's ongoing assessment of field conditions translates into real-time targeting adjustments for the whole squad. Permanently increases party ATK.",
        "skill_shape": "passive",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 0.0
    },
    {
        "id": "al5_65_act",
        "name": "Console Override",
        "type": "Active",
        "source_type": "Ally",
        "mp_cost": 20,
        "damage_formula": "",
        "effect": "{\"party_atk_buff\": 8}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Active: Skip patches his field data directly into ally targeting systems, routing around standard acquisition delays. Increases party ATK for 2 turns.",
        "skill_shape": "self_buff",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 1.0
    },
    # ── al5_66 — Torr Ashfeld — Common DPS ───────────────
    {
        "id": "al5_66_pas",
        "name": "Foundry Tempered",
        "type": "Passive",
        "source_type": "Ally",
        "mp_cost": 0,
        "damage_formula": "",
        "effect": "{\"atk_boost\": 11}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Passive: A decade of foundry heat forged Torr's muscles and reflexes to an edge his opponents consistently underestimate. Permanently increases ATK.",
        "skill_shape": "passive",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 0.0
    },
    {
        "id": "al5_66_act",
        "name": "Slag Burst",
        "type": "Active",
        "source_type": "Ally",
        "mp_cost": 22,
        "damage_formula": "ATK * 2.0",
        "effect": "{\"burn\": 2}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Active: Torr hurls a mass of superheated material at the target with foundry-worker precision. Deals damage and applies Burn for 2 turns.",
        "skill_shape": "single_projectile",
        "range": 3.0,
        "aoe_radius": 0.0,
        "projectile_speed": 10.0,
        "cooldown_seconds": 1.0
    },
    # ── al5_67 — Narra Cole — Common Healer ───────────────
    {
        "id": "al5_67_pas",
        "name": "Dockside Triage",
        "type": "Passive",
        "source_type": "Ally",
        "mp_cost": 0,
        "damage_formula": "",
        "effect": "{\"heal_boost\": 9}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Passive: Six years of emergency care in the most chaotic port in Cartel territory built Narra's healing speed into reflex. Permanently increases healing output.",
        "skill_shape": "passive",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 0.0
    },
    {
        "id": "al5_67_act",
        "name": "No Questions Asked",
        "type": "Active",
        "source_type": "Ally",
        "mp_cost": 20,
        "damage_formula": "PER * 2.0",
        "effect": "{\"cleanse\": 1}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Active: Narra treats the target without hesitation or conditions, removing one active debuff and restoring HP.",
        "skill_shape": "single_target",
        "range": 3.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 1.0
    },
    # ── al5_68 — Zax Volt — Common DPS ───────────────────
    {
        "id": "al5_68_pas",
        "name": "Wrong Method, Right Result",
        "type": "Passive",
        "source_type": "Ally",
        "mp_cost": 0,
        "damage_formula": "",
        "effect": "{\"atk_boost\": 9, \"crit_rate_boost\": 5}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Passive: Zax's unorthodox aether-tapping techniques produce inconsistent but occasionally brilliant results. Permanently increases ATK and critical rate.",
        "skill_shape": "passive",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 0.0
    },
    {
        "id": "al5_68_act",
        "name": "Aether Tap",
        "type": "Active",
        "source_type": "Ally",
        "mp_cost": 22,
        "damage_formula": "ATK * 1.9",
        "effect": "{\"slow\": 2}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Active: Zax channels raw aether through improvised focal points — the discharge hits like a hammer and scrambles the target's motor response. Deals damage and Slows for 2 turns.",
        "skill_shape": "single_projectile",
        "range": 4.0,
        "aoe_radius": 0.0,
        "projectile_speed": 12.0,
        "cooldown_seconds": 1.0
    },
    # ── al5_69 — Brom Hull — Common Tank ─────────────────
    {
        "id": "al5_69_pas",
        "name": "Battalion Commander",
        "type": "Passive",
        "source_type": "Ally",
        "mp_cost": 0,
        "damage_formula": "",
        "effect": "{\"def_boost\": 11, \"party_atk_boost\": 3}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Passive: Brom's command instincts don't switch off in combat — he holds the line and keeps the squad aligned. Increases own DEF and party ATK permanently.",
        "skill_shape": "passive",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 0.0
    },
    {
        "id": "al5_69_act",
        "name": "Forward Position",
        "type": "Active",
        "source_type": "Ally",
        "mp_cost": 20,
        "damage_formula": "ATK * 1.8",
        "effect": "{\"taunt\": 1, \"def_up_self\": 10}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Active: Brom advances to the most exposed position and draws all incoming fire to himself. Taunts enemies for 1 turn and raises own DEF.",
        "skill_shape": "self_buff",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 1.0
    },
    # ── al5_70 — Cera Vell — Common Support ───────────────
    {
        "id": "al5_70_pas",
        "name": "Seventeen Streams",
        "type": "Passive",
        "source_type": "Ally",
        "mp_cost": 0,
        "damage_formula": "",
        "effect": "{\"party_atk_boost\": 3}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Passive: Cera processes the battlefield as simultaneous data feeds, filtering for what each ally needs to know right now. Permanently increases party ATK.",
        "skill_shape": "passive",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 0.0
    },
    {
        "id": "al5_70_act",
        "name": "Tactical Relay",
        "type": "Active",
        "source_type": "Ally",
        "mp_cost": 22,
        "damage_formula": "",
        "effect": "{\"party_def_buff\": 10, \"party_atk_buff\": 6}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Active: Cera broadcasts a coordinated positioning update — every ally adjusts form simultaneously. Increases party ATK and DEF for 2 turns.",
        "skill_shape": "self_buff",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 1.0
    },
    # ── al5_71 — Pix-III — Common Support ────────────────
    {
        "id": "al5_71_pas",
        "name": "Unauthorized Upgrade",
        "type": "Passive",
        "source_type": "Ally",
        "mp_cost": 0,
        "damage_formula": "",
        "effect": "{\"party_atk_boost\": 4}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Passive: Pix-III's self-modifications added cooperative targeting subroutines the Custodians never programmed. Permanently increases party ATK.",
        "skill_shape": "passive",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 0.0
    },
    {
        "id": "al5_71_act",
        "name": "Swarm Relay",
        "type": "Active",
        "source_type": "Ally",
        "mp_cost": 20,
        "damage_formula": "",
        "effect": "{\"party_mp_regen\": 3}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Active: Pix-III deploys micro-relay nodes that boost ally energy recovery for 2 turns. Party regenerates MP each turn.",
        "skill_shape": "self_buff",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 1.0
    },

    # ── al5_72 — Shade Rael — Uncommon DPS ───────────────
    {
        "id": "al5_72_pas",
        "name": "Last One Standing",
        "type": "Passive",
        "source_type": "Ally",
        "mp_cost": 0,
        "damage_formula": "",
        "effect": "{\"atk_boost\": 14, \"agi_boost\": 8}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Passive: Three assassination attempts refined Shade's survival instincts to an art form. Permanently increases ATK and AGI.",
        "skill_shape": "passive",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 0.0
    },
    {
        "id": "al5_72_act",
        "name": "Dead Drop Strike",
        "type": "Active",
        "source_type": "Ally",
        "mp_cost": 25,
        "damage_formula": "ATK * 2.1",
        "effect": "{\"poison\": 3}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Active: Shade deploys a contact agent carried since broker days — precise, traceless, and persistent. Deals damage and applies Poison for 3 turns.",
        "skill_shape": "single_projectile",
        "range": 3.0,
        "aoe_radius": 0.0,
        "projectile_speed": 12.0,
        "cooldown_seconds": 1.0
    },
    # ── al5_73 — Wynn Ore — Uncommon Tank ────────────────
    {
        "id": "al5_73_pas",
        "name": "Still Charging",
        "type": "Passive",
        "source_type": "Ally",
        "mp_cost": 0,
        "damage_formula": "",
        "effect": "{\"def_boost\": 14, \"atk_boost\": 8}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Passive: Wynn completed a cavalry charge on foot. Forward momentum is philosophy, not tactic. Permanently increases DEF and ATK.",
        "skill_shape": "passive",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 0.0
    },
    {
        "id": "al5_73_act",
        "name": "Unmounted Charge",
        "type": "Active",
        "source_type": "Ally",
        "mp_cost": 25,
        "damage_formula": "ATK * 2.2",
        "effect": "{\"taunt\": 2, \"def_up_self\": 12}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Active: Wynn throws her full weight into the enemy line without hesitation. Deals heavy damage, taunts all enemies for 2 turns, and raises own DEF.",
        "skill_shape": "single_target",
        "range": 2.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 1.0
    },
    # ── al5_74 — Lera Mist — Uncommon Healer ─────────────
    {
        "id": "al5_74_pas",
        "name": "Living Compound",
        "type": "Passive",
        "source_type": "Ally",
        "mp_cost": 0,
        "damage_formula": "",
        "effect": "{\"heal_boost\": 14, \"hp_regen\": 3}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Passive: Lera's body now generates healing compound passively — allies near her benefit from trace dispersal. Increases healing output and grants HP regeneration each turn.",
        "skill_shape": "passive",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 0.0
    },
    {
        "id": "al5_74_act",
        "name": "Compound Mist",
        "type": "Active",
        "source_type": "Ally",
        "mp_cost": 25,
        "damage_formula": "PER * 2.4",
        "effect": "{\"heal_all\": 1}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Active: Lera releases a dispersal of her integrated healing compound across the party. Heals all allies.",
        "skill_shape": "aoe_burst",
        "range": 0.0,
        "aoe_radius": 3.5,
        "projectile_speed": 0.0,
        "cooldown_seconds": 1.0
    },
    # ── al5_75 — Cole Steelmark — Uncommon Support ────────
    {
        "id": "al5_75_pas",
        "name": "Field Tester",
        "type": "Passive",
        "source_type": "Ally",
        "mp_cost": 0,
        "damage_formula": "",
        "effect": "{\"party_atk_boost\": 6}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Passive: Cole's firsthand data collection means he knows exactly how to optimize ally equipment loadouts in real-time. Permanently increases party ATK.",
        "skill_shape": "passive",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 0.0
    },
    {
        "id": "al5_75_act",
        "name": "Hardware Patch",
        "type": "Active",
        "source_type": "Ally",
        "mp_cost": 25,
        "damage_formula": "",
        "effect": "{\"party_atk_buff\": 10, \"party_def_buff\": 8}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Active: Cole rapidly cycles field fixes across allied gear — tightened tolerances, recalibrated outputs. Party ATK and DEF increase for 2 turns.",
        "skill_shape": "self_buff",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 1.0
    },
    # ── al5_76 — Tessa Gray — Uncommon DPS ───────────────
    {
        "id": "al5_76_pas",
        "name": "Pattern Recognition",
        "type": "Passive",
        "source_type": "Ally",
        "mp_cost": 0,
        "damage_formula": "",
        "effect": "{\"atk_boost\": 13, \"crit_rate_boost\": 8}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Passive: Years of intelligence analysis translate directly to combat — Tessa reads openings before opponents know they're making them. Permanently increases ATK and critical rate.",
        "skill_shape": "passive",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 0.0
    },
    {
        "id": "al5_76_act",
        "name": "Predictive Strike",
        "type": "Active",
        "source_type": "Ally",
        "mp_cost": 25,
        "damage_formula": "ATK * 2.2",
        "effect": "{\"stun\": 0.3}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Active: Tessa attacks the position she calculated the target would be in half a second ago. Deals damage with 30% chance to Stun.",
        "skill_shape": "single_target",
        "range": 3.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 1.0
    },
    # ── al5_77 — Dane Hollows — Uncommon Tank ─────────────
    {
        "id": "al5_77_pas",
        "name": "Post Held",
        "type": "Passive",
        "source_type": "Ally",
        "mp_cost": 0,
        "damage_formula": "",
        "effect": "{\"def_boost\": 15}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Passive: Three overruns, one post, eleven years — Dane's body learned that leaving is simply not an option. Permanently increases DEF.",
        "skill_shape": "passive",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 0.0
    },
    {
        "id": "al5_77_act",
        "name": "Overrun Protocol",
        "type": "Active",
        "source_type": "Ally",
        "mp_cost": 25,
        "damage_formula": "ATK * 2.0",
        "effect": "{\"taunt\": 2, \"shield_self\": 18}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Active: Dane digs in and refuses the ground. Taunts all enemies for 2 turns and generates a damage-absorbing shield.",
        "skill_shape": "self_buff",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 1.0
    },
    # ── al5_78 — Lysa Bloom — Uncommon Healer ─────────────
    {
        "id": "al5_78_pas",
        "name": "Garden Keeper",
        "type": "Passive",
        "source_type": "Ally",
        "mp_cost": 0,
        "damage_formula": "",
        "effect": "{\"heal_boost\": 13, \"party_hp_regen\": 2}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Passive: Lysa tends the party as she tends the garden — with patient, sustained care. Increases healing output and grants party HP regen each turn.",
        "skill_shape": "passive",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 0.0
    },
    {
        "id": "al5_78_act",
        "name": "Root and Restore",
        "type": "Active",
        "source_type": "Ally",
        "mp_cost": 25,
        "damage_formula": "PER * 2.3",
        "effect": "{\"heal_ally\": \"lowest_hp\", \"cleanse\": 1}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Active: Lysa applies a concentrated root extract that heals and purifies. Heals the lowest HP ally and removes one debuff.",
        "skill_shape": "single_target",
        "range": 3.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 1.0
    },

    # ── al5_79 — Kira Vane — Rare DPS ────────────────────
    {
        "id": "al5_79_pas",
        "name": "Shard Conduit",
        "type": "Passive",
        "source_type": "Ally",
        "mp_cost": 0,
        "damage_formula": "",
        "effect": "{\"atk_boost\": 16, \"crit_rate_boost\": 8}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Passive: The Aethel fragment in Kira's forearm channels Shard resonance into every strike, amplifying damage beyond ordinary physical limits. Permanently increases ATK and critical rate.",
        "skill_shape": "passive",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 0.0
    },
    {
        "id": "al5_79_act",
        "name": "Resonant Strike",
        "type": "Active",
        "source_type": "Ally",
        "mp_cost": 30,
        "damage_formula": "ATK * 2.6",
        "effect": "{\"stun\": 0.35, \"bleed\": 2}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Active: Kira channels the Shard fragment's full output through a single, concentrated blow. Heavy damage with 35% Stun chance and Bleed for 2 turns.",
        "skill_shape": "single_target",
        "range": 2.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 1.0
    },
    # ── al5_80 — Gareth Null — Rare Tank ─────────────────
    {
        "id": "al5_80_pas",
        "name": "Actual Protection",
        "type": "Passive",
        "source_type": "Ally",
        "mp_cost": 0,
        "damage_formula": "",
        "effect": "{\"def_boost\": 17, \"party_def_boost\": 6}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Passive: Gareth's protection extends beyond himself — a habit built from watching executives ignore threats until it was too late. Increases own DEF and party DEF permanently.",
        "skill_shape": "passive",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 0.0
    },
    {
        "id": "al5_80_act",
        "name": "Executive Shield",
        "type": "Active",
        "source_type": "Ally",
        "mp_cost": 30,
        "damage_formula": "ATK * 2.2",
        "effect": "{\"shield_self\": 22, \"taunt\": 2}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Active: Gareth interposes himself and generates a hardened defensive barrier. Taunts all enemies for 2 turns and generates a significant damage-absorbing shield.",
        "skill_shape": "self_buff",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 1.0
    },
    # ── al5_81 — Sable Noir — Rare Support ───────────────
    {
        "id": "al5_81_pas",
        "name": "Network Intact",
        "type": "Passive",
        "source_type": "Ally",
        "mp_cost": 0,
        "damage_formula": "",
        "effect": "{\"party_atk_boost\": 7, \"party_def_boost\": 5}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Passive: Sable's intelligence network remained operational even after retirement — and old contacts still feed useful intelligence. Permanently increases party ATK and DEF.",
        "skill_shape": "passive",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 0.0
    },
    {
        "id": "al5_81_act",
        "name": "Known Weakness",
        "type": "Active",
        "source_type": "Ally",
        "mp_cost": 28,
        "damage_formula": "PER * 2.6",
        "effect": "{\"energy_drain\": 18, \"slow\": 2}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Active: Sable exploits a dossier entry — a vulnerability the target didn't know she had access to. Drains enemy MP and applies Slow for 2 turns.",
        "skill_shape": "single_target",
        "range": 4.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 1.0
    },
    # ── al5_82 — Haze Cordell — Rare Healer ──────────────
    {
        "id": "al5_82_pas",
        "name": "Extended Assignment",
        "type": "Passive",
        "source_type": "Ally",
        "mp_cost": 0,
        "damage_formula": "",
        "effect": "{\"heal_boost\": 16, \"hp_regen\": 4}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Passive: Eleven years of continuous field medical work built Haze into a system that never fully stops running. Increases healing output and grants HP regen each turn.",
        "skill_shape": "passive",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 0.0
    },
    {
        "id": "al5_82_act",
        "name": "Research Protocol",
        "type": "Active",
        "source_type": "Ally",
        "mp_cost": 30,
        "damage_formula": "PER * 2.8",
        "effect": "{\"heal_all\": 1, \"cleanse\": 1}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Active: Haze applies her accumulated field research in a single coordinated treatment pass. Heals all allies and removes one debuff from each.",
        "skill_shape": "aoe_burst",
        "range": 0.0,
        "aoe_radius": 4.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 1.0
    },
    # ── al5_83 — Erix Storm — Rare DPS ───────────────────
    {
        "id": "al5_83_pas",
        "name": "Charge Accumulation",
        "type": "Passive",
        "source_type": "Ally",
        "mp_cost": 0,
        "damage_formula": "",
        "effect": "{\"atk_boost\": 16, \"crit_rate_boost\": 10}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Passive: Three lightning strikes left Erix's physiology permanently energized — his attacks carry a residual electrical charge that critical hits discharge explosively. Increases ATK and critical rate permanently.",
        "skill_shape": "passive",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 0.0
    },
    {
        "id": "al5_83_act",
        "name": "Storm Discharge",
        "type": "Active",
        "source_type": "Ally",
        "mp_cost": 30,
        "damage_formula": "ATK * 2.5",
        "effect": "{\"stun\": 0.35, \"slow\": 2}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Active: Erix releases accumulated bio-electrical charge in a single concentrated strike. Deals heavy damage with 35% Stun chance and Slows the target for 2 turns.",
        "skill_shape": "single_projectile",
        "range": 4.0,
        "aoe_radius": 0.0,
        "projectile_speed": 16.0,
        "cooldown_seconds": 1.0
    },
    # ── al5_84 — Marn Weld — Rare Tank ───────────────────
    {
        "id": "al5_84_pas",
        "name": "Living Test Subject",
        "type": "Passive",
        "source_type": "Ally",
        "mp_cost": 0,
        "damage_formula": "",
        "effect": "{\"def_boost\": 18, \"thorns\": 6}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Passive: Every rune carved into Marn's own skin has been stress-tested beyond specification. DEF increases permanently and attackers take reflected damage (Thorns).",
        "skill_shape": "passive",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 0.0
    },
    {
        "id": "al5_84_act",
        "name": "Rune Bulwark",
        "type": "Active",
        "source_type": "Ally",
        "mp_cost": 28,
        "damage_formula": "ATK * 2.2",
        "effect": "{\"shield_self\": 25, \"thorns\": 8}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Active: Marn activates a full-body rune sequence — a walking experiment in defensive theory. Generates a large shield and amplifies Thorns damage reflection.",
        "skill_shape": "self_buff",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 1.0
    },
    # ── al5_85 — Zola Kast — Rare Healer ─────────────────
    {
        "id": "al5_85_pas",
        "name": "District Triage",
        "type": "Passive",
        "source_type": "Ally",
        "mp_cost": 0,
        "damage_formula": "",
        "effect": "{\"heal_boost\": 15, \"party_hp_regen\": 3}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Passive: Zola's District 14 system ran itself on improvisation and efficiency — she brings the same principle to combat medicine. Increases healing output and grants party HP regen each turn.",
        "skill_shape": "passive",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 0.0
    },
    {
        "id": "al5_85_act",
        "name": "Sector Sweep",
        "type": "Active",
        "source_type": "Ally",
        "mp_cost": 32,
        "damage_formula": "PER * 2.8",
        "effect": "{\"heal_all\": 1}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Active: Zola runs a rapid triage pass across all allies — no one gets left for later. Heals all party members.",
        "skill_shape": "aoe_burst",
        "range": 0.0,
        "aoe_radius": 4.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 1.0
    },

    # ── al5_86 — Omen Null — Epic DPS ────────────────────
    {
        "id": "al5_86_pas",
        "name": "Threat Projection",
        "type": "Passive",
        "source_type": "Ally",
        "mp_cost": 0,
        "damage_formula": "",
        "effect": "{\"atk_boost\": 22, \"crit_rate_boost\": 12}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Passive: Omen processes enemies as probability vectors and attacks the highest-value vulnerability before it closes. Permanently increases ATK and critical rate.",
        "skill_shape": "passive",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 0.0
    },
    {
        "id": "al5_86_act",
        "name": "Null Event",
        "type": "Active",
        "source_type": "Ally",
        "mp_cost": 45,
        "damage_formula": "ATK * 3.0",
        "effect": "{\"void_rupture\": true, \"stun\": 0.45}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Active: Omen collapses a localized probability window — the target experiences a moment of null causality. Massive damage with 45% Stun chance and Void Rupture effect.",
        "skill_shape": "single_target",
        "range": 4.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 1.0
    },
    # ── al5_87 — Torrak Iron — Epic Tank ─────────────────
    {
        "id": "al5_87_pas",
        "name": "Sole Survivor",
        "type": "Passive",
        "source_type": "Ally",
        "mp_cost": 0,
        "damage_formula": "",
        "effect": "{\"def_boost\": 22, \"thorns\": 10}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Passive: Something about surviving a nine-hour Void incursion as the last one standing hardened Torrak beyond standard physical limits. Permanently increases DEF and applies Thorns to all attackers.",
        "skill_shape": "passive",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 0.0
    },
    {
        "id": "al5_87_act",
        "name": "Redoubt",
        "type": "Active",
        "source_type": "Ally",
        "mp_cost": 42,
        "damage_formula": "ATK * 2.8",
        "effect": "{\"taunt\": 3, \"shield_all\": 20}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Active: Torrak holds the line for the entire squad — every attack meant for an ally redirects to him while a shared shield absorbs incoming damage. Taunts all enemies for 3 turns and grants a shield to all allies.",
        "skill_shape": "aoe_burst",
        "range": 0.0,
        "aoe_radius": 4.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 1.0
    },
    # ── al5_88 — Caelan Arc — Epic Healer ────────────────
    {
        "id": "al5_88_pas",
        "name": "Protocol Seven",
        "type": "Passive",
        "source_type": "Ally",
        "mp_cost": 0,
        "damage_formula": "",
        "effect": "{\"heal_boost\": 22, \"party_hp_regen\": 4}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Passive: Caelan operates on emergency authority that never expires. Every action is optimized for sustained crisis — party receives continuous HP regeneration and healing effectiveness is significantly increased.",
        "skill_shape": "passive",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 0.0
    },
    {
        "id": "al5_88_act",
        "name": "Emergency Response",
        "type": "Active",
        "source_type": "Ally",
        "mp_cost": 48,
        "damage_formula": "PER * 3.4",
        "effect": "{\"heal_all\": 1, \"remove_all_debuffs\": true}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Active: Caelan triggers a full-party emergency response — every injury addressed, every status condition cleared. Heals all allies and removes all debuffs from the party.",
        "skill_shape": "aoe_burst",
        "range": 0.0,
        "aoe_radius": 5.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 1.0
    },
    # ── al5_89 — Lyssa Void — Epic Support ───────────────
    {
        "id": "al5_89_pas",
        "name": "Null-Space Navigation",
        "type": "Passive",
        "source_type": "Ally",
        "mp_cost": 0,
        "damage_formula": "",
        "effect": "{\"party_atk_boost\": 10, \"party_def_boost\": 8}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Passive: Lyssa's altered perception lets her position allies ahead of incoming threats — every squad member benefits from her expanded spatial awareness. Permanently increases party ATK and DEF.",
        "skill_shape": "passive",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 0.0
    },
    {
        "id": "al5_89_act",
        "name": "Void Foresight",
        "type": "Active",
        "source_type": "Ally",
        "mp_cost": 44,
        "damage_formula": "",
        "effect": "{\"shield_all\": 25, \"party_atk_buff\": 15, \"party_def_buff\": 12}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Active: Lyssa reads the next 3 seconds of combat and repositions the entire party ahead of attacks that haven't landed yet. Grants a shield to all allies and significantly boosts party ATK and DEF for 2 turns.",
        "skill_shape": "aoe_burst",
        "range": 0.0,
        "aoe_radius": 5.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 1.0
    },

    # ── al5_90 — Aegis Prime — Legendary Tank ────────────
    {
        "id": "al5_90_pas",
        "name": "Four Centuries",
        "type": "Passive",
        "source_type": "Ally",
        "mp_cost": 0,
        "damage_formula": "",
        "effect": "{\"def_boost\": 25, \"party_def_boost\": 12, \"thorns\": 14}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Passive: Four hundred years of continuous tactical memory mean Aegis Prime has faced every attack pattern at least twice. Permanently increases own DEF and party DEF, and reflects damage (Thorns) to all attackers.",
        "skill_shape": "passive",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 0.0
    },
    {
        "id": "al5_90_act",
        "name": "Archival Fortress",
        "type": "Active",
        "source_type": "Ally",
        "mp_cost": 60,
        "damage_formula": "ATK * 3.5",
        "effect": "{\"taunt\": 3, \"shield_all\": 30, \"party_def_buff\": 20}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Active: Aegis Prime deploys four centuries of defensive doctrine in a single formation — the squad becomes a fortress. Taunts all enemies for 3 turns, grants a massive shield to all allies, and greatly increases party DEF.",
        "skill_shape": "aoe_burst",
        "range": 0.0,
        "aoe_radius": 6.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 1.0
    },
    # ── al5_91 — Solas Dark — Legendary Healer ───────────
    {
        "id": "al5_91_pas",
        "name": "Before the War",
        "type": "Passive",
        "source_type": "Ally",
        "mp_cost": 0,
        "damage_formula": "",
        "effect": "{\"heal_boost\": 28, \"party_hp_regen\": 6, \"party_mp_regen\": 4}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Passive: Solas existed when healing and harm were not yet separate concepts — its presence sustains allied vitality at a fundamental level. Greatly increases healing output and grants the party continuous HP and MP regeneration each turn.",
        "skill_shape": "passive",
        "range": 0.0,
        "aoe_radius": 0.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 0.0
    },
    {
        "id": "al5_91_act",
        "name": "Shard's Memory",
        "type": "Active",
        "source_type": "Ally",
        "mp_cost": 62,
        "damage_formula": "PER * 4.2",
        "effect": "{\"heal_all\": 1, \"revive\": 0.35, \"remove_all_debuffs\": true}",
        "stat_modifiers": [],
        "periodic_effects": [],
        "control_effects": [],
        "skill_description": "Active: Solas reaches back to the moment before the Fracture and pulls the party toward wholeness. Heals all allies, removes all debuffs, and has a 35% chance to revive a fallen ally at partial HP.",
        "skill_shape": "aoe_burst",
        "range": 0.0,
        "aoe_radius": 6.0,
        "projectile_speed": 0.0,
        "cooldown_seconds": 1.0
    }
]

# Append new skills
skills.extend(new_skills)
print(f"  Appended {len(new_skills)} new skills. Total now: {len(skills)}")

# Save skill_list.json
with open(SKILL_FILE, "w", encoding="utf-8") as f:
    json.dump(skills, f, indent=2, ensure_ascii=False)
print(f"  skill_list.json saved.")

# ─────────────────────────────────────────────────────────
# VERIFICATION
# ─────────────────────────────────────────────────────────
print("\n─── Verification ───────────────────────────────────")

with open(ALLY_FILE, "r", encoding="utf-8") as f:
    final_allies = json.load(f)

total = len(final_allies["allies"])
pvp_role_count = sum(1 for a in final_allies["allies"] if "pvp_role" in a)
missing_pvp_scale = [a["ally_id"] for a in final_allies["allies"] if "pvp_scale" not in a]
missing_conclave = [a["ally_id"] for a in final_allies["allies"] if "conclave_points" not in a]

print(f"  ally_list.json total allies: {total}  (expected 91)")
print(f"  Allies with pvp_role remaining: {pvp_role_count}  (expected 0)")
print(f"  Missing pvp_scale: {missing_pvp_scale or 'none'}")
print(f"  Missing conclave_points: {missing_conclave or 'none'}")
print(f"  Meta version: {final_allies['meta']['version']}")
print(f"  Meta total: {final_allies['meta']['total']}")
print(f"  pvp_fields keys: {list(final_allies['meta']['pvp_fields'].keys())}")

with open(SKILL_FILE, "r", encoding="utf-8") as f:
    final_skills = json.load(f)

al5_ids = sorted([s["id"] for s in final_skills if s["id"].startswith("al5_")])
print(f"\n  skill_list.json total skills: {len(final_skills)}")
print(f"  al5_ skill IDs found ({len(al5_ids)}): {al5_ids[:5]} ... {al5_ids[-5:]}")

expected_ids = []
for n in range(62, 92):
    expected_ids.append(f"al5_{n}_pas")
    expected_ids.append(f"al5_{n}_act")
missing_ids = [eid for eid in expected_ids if eid not in al5_ids]
print(f"  Missing expected skill IDs: {missing_ids or 'none'}")

print("\n✓ All done." if (total == 91 and pvp_role_count == 0 and not missing_ids) else "\n✗ Issues detected — review output above.")
