#!/usr/bin/env python3
"""Attach condition-free ambient and rumor conversations to NPC dialogue trees."""

import json
import re
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def load(name):
    return json.loads((ROOT/name).read_text(encoding="utf-8"))
def save(name,data):
    (ROOT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def main():
    npc_list=load("npc_list.json")
    npc_by_id={npc["npc_id"]:npc for npc in npc_list}
    wrappers=load("dialog_tree_master.json")
    dialogues=[item for wrapper in wrappers for item in wrapper.get("dialogues",[])]
    tree_by_id={tree["dialog_id"]:tree for tree in dialogues}
    refs=Counter(npc.get("dialogue_tree") for npc in npc_list if npc.get("dialogue_tree"))
    ambient=load("18_ambient_dialogue.json")["conversations"]
    rumors=load("19_rumor_system.json")["rumors"]
    additions={}
    skipped=[]

    for entry in ambient:
        if entry.get("conditions"):
            skipped.append(entry["id"])
            continue
        additions.setdefault(entry["npc_id"],[]).append(("ambient",entry))
    for rumor in rumors:
        if rumor.get("condition"):
            skipped.append(rumor["id"])
            continue
        additions.setdefault(rumor["source_npc"],[]).append(("rumor",rumor))

    for npc_id,items in additions.items():
        npc=npc_by_id.get(npc_id)
        if not npc:
            skipped.extend(entry["id"] for _,entry in items)
            continue
        current_id=npc.get("dialogue_tree")
        source=tree_by_id.get(current_id)
        if source and refs[current_id]>1:
            suffix=re.sub(r"[^a-z0-9]+","_",npc_id.lower()).strip("_")
            new_id=f"dialog_world_{suffix}"
            if new_id not in tree_by_id:
                source= json.loads(json.dumps(source))
                source["dialog_id"]=new_id
                source["npc_id"]=npc_id
                dialogues.append(source)
                tree_by_id[new_id]=source
            else:
                source=tree_by_id[new_id]
            npc["dialogue_tree"]=new_id
            refs[current_id]-=1
            refs[new_id]+=1
        elif not source:
            current_id=f"dialog_world_{re.sub(r'[^a-z0-9]+','_',npc_id.lower()).strip('_')}"
            source={"dialog_id":current_id,"npc_id":npc_id,"start_node":"greet","nodes":[
                {"id":"greet","text":npc.get("greeting") or f"{npc.get('name', 'The local')} looks up from the work in front of them.","options":[{"text":"How are things nearby?","next":"greet","action":""}]}
            ]}
            dialogues.append(source)
            tree_by_id[current_id]=source
            npc["dialogue_tree"]=current_id
            refs[current_id]+=1
        start=next((node for node in source.get("nodes",[]) if node.get("id")==source.get("start_node")),None)
        if not start:
            skipped.extend(entry["id"] for _,entry in items)
            continue
        existing_nodes={node.get("id") for node in source.get("nodes",[])}
        for index,(kind,entry) in enumerate(items,1):
            node_id=entry["id"]
            if node_id in existing_nodes:
                continue
            choice="Any word from around here?" if kind=="rumor" else "How are the locals holding up?"
            if any(option.get("text")==choice for option in start.get("options",[])):
                choice=f"{choice[:-1]} ({index})?"
            start.setdefault("options",[]).append({"text":choice,"next":node_id,"action":""})
            source.setdefault("nodes",[]).append({"id":node_id,"text":entry["text"],"options":[
                {"text":"I'll remember that.","next":source["start_node"],"action":""}]})
            existing_nodes.add(node_id)

    master=[{"meta":{"version":"2.1","description":"NPC dialogue trees with integrated ambient and rumor conversations; quest dialogues remain in dialog_quests.json.","quest_dialog_count":len(load("dialog_quests.json")["dialogues"]),"npc_dialog_count":len(dialogues),"total_count":len(dialogues)+len(load("dialog_quests.json")["dialogues"])},"dialogues":dialogues}]
    save("npc_list.json",npc_list)
    save("dialog_tree_master.json",master)
    save("23_updated_npc_list.json",npc_list)
    save("25_updated_dialog_tree_master.json",master)
    print(f"Integrated {sum(len(v) for v in additions.values())-len(skipped)} ambient/rumor lines; skipped {len(skipped)} condition-gated entries: {', '.join(skipped)}")
    print(f"NPC master trees: {len(dialogues)}")

if __name__=="__main__": main()
