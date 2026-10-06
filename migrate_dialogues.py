#!/usr/bin/env python3
"""Apply evidence-backed dialogue identity and safety migration."""

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))

def save(name, data):
    (ROOT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def make_npc(npc_id, name, title, role, faction, location, region, description, personality, greeting, tree):
    return {"npc_id":npc_id,"name":name,"title":title,"role":role,"faction":faction,
            "dialogue_tree":tree,"shop_inventory":None,"location":location,"region_id":region,
            "description":description,"personality":personality,"greeting":greeting,
            "available_services":["QUEST"],"actions":[],"legacy_aliases":[]}

NEW_NPCS = [
    make_npc("npc_commander_vale","Commander Lirien Vale","Concordium Field Commander","QUEST_GIVER","CONCORDIUM","Aethel Gardens","AETHEL_GARDENS","Field commander responsible for Concordium operations across the Gardens and Cradle. She weighs operational success against the people who pay for it.","direct_strategic","The route report first. Then tell me what you saw.","dialog_lirien_vale_main"),
    make_npc("npc_warlord_steele","Warlord Harkon Steele","Iron Hegemony Warlord","QUEST_GIVER","IRON_HEGEMONY","Bastion Core","BASTION_CORE","Hegemony warlord overseeing field operations and the recovery of strategic industrial ground.","hard_practical","State your readiness. I have a line to hold.","dialog_harkon_steele_main"),
    make_npc("npc_don_mox","Don Vercelli Mox","Meridian Cartel Don","QUEST_GIVER","MERIDIAN_CARTEL","Port Meridian","PORT_MERIDIAN","Cartel leader whose influence rests on routes, favors, and information as much as cargo.","social_calculating","Sit. We can decide whether this is business after we hear the whole story.","dialog_don_vercelli_mox_main"),
    make_npc("npc_elder_malakor","Elder Malakor","Shard Elder","QUEST_GIVER","CHILDREN_OF_THE_SHARD","Sanctum","SANCTUM","Senior voice among the Children of the Shard. His interpretation of the Shard is a religious belief, not established fact.","solemn_grieving","Listen before you answer. The forest has been trying to tell us something.","dialog_elder_malakor_main"),
]

NPC_ALIASES = {
    "npc_high_seeker_voss":"npc_arcanum_scholar",
    "npc_director_vey":"npc_omnicorp_class_trainer",
    "npc_centurion_valka":"npc_legion_class_trainer",
}

QUEST_NARRATIVE = {
    1:("The first dispatch is a perimeter report, not a victory speech. The Garden crews need a corridor they can cross twice.","Vale has learned to ask what the field changed, not only whether the order was obeyed."),
    2:("The sentries are back on the line, but nobody calls the route safe after one clean pass.","Valen records every open path because he has watched small omissions close them again."),
    3:("The next report links the local threat to a wider failure in the old settlement grid.","A scout's observations are now part of the operational record, not a footnote."),
    4:("A cleared site still has to support the people sent to occupy it.","Vael counts tools, water, and names; the last column is the one he rereads."),
    5:("The response is becoming a routine, and routine is where an unchecked assumption hides.","Hale wants a clean containment result. Vale asks what the result costs after the report is filed."),
    6:("An old marker places this disturbance beside infrastructure built before Nexus had a name.","Rian trusts a footprint more than a faction's version of the map."),
    7:("Local crews have started changing their shifts around the hazard.","The Guard Captain calls that adaptation. The workers call it losing half a night's sleep."),
    8:("The evidence points inward, toward systems no present faction fully understands.","Valen will certify the route; he will not certify a theory."),
    9:("The field pattern repeats, but the surviving records do not agree on why.","Vale is willing to carry uncertainty into the briefing. She will not let anyone disguise it as proof."),
    10:("One more secured sector gives the displaced crews somewhere to return to.","For the people who live here, a stable door matters more than a grand claim about the Cradle."),
    11:("The operation now affects who can move supplies through the district.","Vael knows every delayed crate has a person waiting at the other end of the manifest."),
    12:("A recovered trace suggests the disturbance is connected to damaged Aethel infrastructure.","The record says what was measured. It does not say the Siphon caused this event."),
    13:("Rival claims are beginning to follow the same route as the field reports.","Hale prefers a sealed perimeter; Vale knows a sealed perimeter can become a political border."),
    14:("The old civil quarter offers evidence, but not a single account of its past.","Rian marks what she can see and leaves the missing years blank."),
    15:("The crew can hold the next position only if the approach stays usable.","The captain has stopped promising that a route will be quiet. Now he promises to be there."),
    16:("Aethel readings rise near the Cradle, though the instruments disagree on the scale.","Nobody gets to call a disputed reading a warning from the Shard."),
    17:("The briefing includes a civilian report that was absent from yesterday's official summary.","Vale asked for the witness to be named. It cost her an hour with the review board."),
    18:("The next archive fragment may clarify the timeline, but its provenance is uncertain.","An old record can be useful without being honest."),
    19:("The line is holding through cooperation between crews that do not share a flag.","Valen dislikes the unofficial arrangement. He dislikes losing people more."),
    20:("The Outer Ring remains contested; securing it is a continuing responsibility, not a finished map.","Vale will report the limits of Concordium control as clearly as its gains."),
}

def quest_story(quest, original, giver_name, ordinal):
    level=quest.get("requirements",{}).get("min_level",1)
    group=min(20,max(1,((level-1)//5)+1))
    beat, personal=QUEST_NARRATIVE[group]
    old_nodes={node.get("id"):node for node in original.get("nodes",[])}
    old_greeting=old_nodes.get("greeting",{}).get("text","").strip()
    old_lore=old_nodes.get("lore",{}).get("text","").strip()
    region=quest.get("region","").replace("_"," ").title()
    objective_lines=[]
    for objective in quest.get("objectives",[]):
        target=objective.get("target_code") or objective.get("target")
        objective_lines.append(f"{objective.get('type','Complete').capitalize()} {target} x{objective.get('count',1)}")
    objective_text="; ".join(objective_lines) or "Complete the assigned operation"
    # Retain authored scene-specific opening when it is not merely the old menu text.
    if not old_greeting or old_greeting in {"Tell me more.","Quest available."}:
        old_greeting=f"{giver_name} checks the latest field sheet. {beat}"
    if len(old_greeting)>900:
        old_greeting=old_greeting[:897].rsplit(" ",1)[0]+"..."
    if not old_lore or len(old_lore)<35:
        old_lore=f"{beat} {personal}"
    if len(old_lore)>900:
        old_lore=old_lore[:897].rsplit(" ",1)[0]+"..."
    title=quest.get("title","this operation")
    lore_text=old_lore if old_lore.endswith(personal) else old_lore+" "+personal
    return {
      "dialog_id":original.get("dialog_id",f"dialog_{quest['id']}"),"quest_id":quest["id"],"npc_id":original.get("npc_id"),"start_node":"greeting",
      "nodes":[
        {"id":"greeting","text":old_greeting,"options":[
          {"text":"What changed since the last report?","next":"lore","action":""},
          {"text":"I'll take the assignment.","next":"accept","action":""},
          {"text":"Not yet.","next":"exit","action":"exit"}]},
        {"id":"lore","text":lore_text,"options":[
          {"text":"Put me on the line.","next":"accept","action":""},
          {"text":"Back to the report.","next":"greeting","action":""}]},
        {"id":"accept","text":f"{giver_name}: {beat} In {region}, {objective_text}. {personal}","options":[
          {"text":"Confirm assignment: {title}".format(title=title),"next":"exit","action":"accept_quest"},
          {"text":"I'll decide later.","next":"exit","action":"exit"}]},
        {"id":"exit","text":"The briefing ends; the field report stays open.","options":[]},
      ]}

def generic_tree(npc):
    tree_id=npc.get("dialogue_tree")
    if not tree_id: return None
    name=npc.get("name","Local contact")
    greeting=npc.get("greeting") or f"{name} looks up from the work in front of them."
    about=npc.get("description") or f"{name} has little to add until the next shift."
    return {"dialog_id":tree_id,"npc_id":npc["npc_id"],"start_node":"greet","nodes":[
      {"id":"greet","text":greeting,"options":[{"text":"What's happening around here?","next":"local","action":""},{"text":"I'll leave you to it.","next":"exit","action":"exit"}]},
      {"id":"local","text":about,"options":[{"text":"Thanks for the word.","next":"exit","action":"exit"}]},
      {"id":"exit","text":"The conversation pauses.","options":[]}]}

def main():
    npc_list=load("npc_list.json")
    npc_by_id={npc["npc_id"]:npc for npc in npc_list}
    for legacy_id,canonical_id in NPC_ALIASES.items():
        canonical=npc_by_id.get(canonical_id)
        if canonical:
            aliases=canonical.setdefault("legacy_aliases",[])
            if legacy_id not in aliases:
                aliases.append(legacy_id)
    for npc in NEW_NPCS:
        if npc["npc_id"] not in npc_by_id:
            npc_list.append(npc)
            npc_by_id[npc["npc_id"]]=npc

    quest_data=load("dialog_quests.json")
    quest_dialogues=quest_data["dialogues"]
    original_by_quest={d.get("quest_id"):d for d in quest_dialogues}
    for dialogue in quest_dialogues:
        qid=dialogue.get("quest_id","")
        if dialogue.get("npc_id") in NPC_ALIASES:
            old=dialogue["npc_id"]
            dialogue["npc_id"]=NPC_ALIASES[old]
        if qid=="fq_conc_001":
            dialogue["npc_id"]="npc_commander_vale"
        # Exactly one acceptance action, after the player has reached confirmation.
        for node in dialogue.get("nodes",[]):
            for option in node.get("options",[]):
                if option.get("action")=="accept_quest":
                    option["action"]=""
        accept_node=next((node for node in dialogue.get("nodes",[]) if node.get("id")=="accept"),None)
        if accept_node:
            accept_option=next((op for op in accept_node.get("options",[]) if op.get("next") in {"exit",None}),None)
            if accept_option:
                accept_option["action"]="accept_quest"
        else:
            # Legacy reminder flows offered acceptance from two nodes. Funnel
            # both choices through one confirmation action to avoid double-fire.
            nodes=dialogue.get("nodes",[])
            node_ids={node.get("id") for node in nodes}
            for node in nodes:
                for option in node.get("options",[]):
                    if "accept quest" in option.get("text","").lower():
                        option["next"]="confirm_accept"
            if "confirm_accept" not in node_ids:
                nodes.append({"id":"confirm_accept","text":"Confirm that you are ready to take this assignment.","options":[
                    {"text":"Confirm acceptance","next":"exit","action":"accept_quest"},
                    {"text":"Return to the briefing","next":dialogue.get("start_node","start"),"action":""}]})
            else:
                confirm=next(node for node in nodes if node.get("id")=="confirm_accept")
                confirm_option=next((op for op in confirm.get("options",[]) if op.get("text")=="Confirm acceptance"),None)
                if confirm_option:
                    confirm_option["action"]="accept_quest"

    # Make the pilot match current objective data and resolve its direct identity conflict.
    quest_data_by_id={q["id"]:q for q in load("quest_concordium.json")["quests"]}
    pilot=[]
    for qid,quest in quest_data_by_id.items():
        old=original_by_quest.get(qid,{"dialog_id":f"dialog_{qid}","quest_id":qid,"npc_id":"npc_concordium_officer","nodes":[]})
        if qid=="fq_conc_001": old["npc_id"]="npc_commander_vale"
        pilot.append(quest_story(quest,old,npc_by_id[old["npc_id"]]["name"],int(qid[-3:])))
    pilot.sort(key=lambda item:int(item["quest_id"].rsplit("_",1)[1]))
    by_qid={d.get("quest_id"):d for d in quest_dialogues}
    by_qid.update({d["quest_id"]:d for d in pilot})
    quest_data["dialogues"]=[by_qid[d.get("quest_id")] for d in quest_dialogues]

    # Keep all generic tree IDs functional. Existing tree content is preserved.
    master=load("dialog_tree_master.json")
    existing=[d for block in master for d in block.get("dialogues",[])]
    existing_by_id={d.get("dialog_id"):d for d in existing if d.get("dialog_id")}
    for npc in npc_list:
        tree_id=npc.get("dialogue_tree")
        if tree_id and tree_id not in existing_by_id:
            tree=generic_tree(npc)
            if tree:
                existing.append(tree)
                existing_by_id[tree_id]=tree
    # New canonical NPCs receive matching entry-point trees.
    for npc in NEW_NPCS:
        if npc["dialogue_tree"] not in existing_by_id:
            tree=generic_tree(npc)
            if tree:
                existing.append(tree)
                existing_by_id[npc["dialogue_tree"]]=tree
    metadata={"version":"2.0","description":"Synchronized NPC dialogue trees; quest dialogues are stored in dialog_quests.json.","quest_dialog_count":len(quest_data["dialogues"]),"npc_dialog_count":len(existing),"total_count":len(existing)+len(quest_data["dialogues"])}

    # Keep quest giver IDs/names in gameplay quest records aligned to dialogue identity.
    q_giver_map={d["quest_id"]:d["npc_id"] for d in quest_data["dialogues"] if d.get("quest_id")}
    for filename in ["quest_concordium.json","quest_arcanum.json","quest_iron.json","quest_meridian.json","quest_omnicorp.json","quest_shard.json","quest_legion.json","quest_neutral.json"]:
        data=load(filename)
        changed=False
        for quest in data.get("quests",[]):
            npc_id=q_giver_map.get(quest.get("id"))
            if npc_id and npc_id in npc_by_id and quest.get("quest_giver"):
                quest["quest_giver"]["npc_id"]=npc_id
                quest["quest_giver"]["name"]=npc_by_id[npc_id]["name"]
                changed=True
        if changed: save(filename,data)

    save("npc_list.json",npc_list)
    save("dialog_quests.json",quest_data)
    save("dialog_tree_master.json",[{"meta":metadata,"dialogues":existing}])
    save("23_updated_npc_list.json",npc_list)
    save("24_updated_dialog_quests.json",quest_data)
    save("25_updated_dialog_tree_master.json",[{"meta":metadata,"dialogues":existing}])
    save("09_concordium_dialogue_rewrite.json",{"status":"pilot","dialogues":pilot,"notes":"Pilot content copied into dialog_quests.json. Gameplay quest IDs/objectives/rewards remain authoritative; state-aware completion/post-completion is not enabled without runtime support."})
    print(f"Migrated {len(quest_dialogues)} quest dialogues; rewrote Concordium pilot ({len(pilot)}); NPC roster {len(npc_list)}; master trees {len(existing)}")

if __name__=="__main__":
    main()
