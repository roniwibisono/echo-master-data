#!/usr/bin/env python3
"""Keep quest offer dialogue aligned with authoritative quest objectives."""

import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
FACTION_LINES={
 "CONCORDIUM":"Log the result accurately; a cleared route is useful only if the next crew can hold it.",
 "THE_ARCANUM_SEEKERS":"Record what you observe after the encounter. A result without context is only another rumor.",
 "IRON_HEGEMONY":"Hold the line and report the condition of the route when the work is done.",
 "MERIDIAN_CARTEL":"The contract pays for a verified result. Keep the route in mind; that's where the real value sits.",
 "OMNICORP":"Record the deliverable and any deviation from projection. Close the operation cleanly.",
 "CHILDREN_OF_THE_SHARD":"Do what must be done, then notice what the living place does in the silence afterward.",
 "STARFORGED_LEGION":"Complete the task as assigned and report who stood beside you when the line held.",
}
FILES=["quest_concordium.json","quest_arcanum.json","quest_iron.json","quest_meridian.json","quest_omnicorp.json","quest_shard.json","quest_legion.json"]

def read(name): return json.loads((ROOT/name).read_text(encoding="utf-8"))
def main():
    quests={q["id"]:q for filename in FILES for q in read(filename)["quests"]}
    data=read("dialog_quests.json")
    changed=0
    for dialog in data["dialogues"]:
        quest=quests.get(dialog.get("quest_id"))
        if not quest or dialog["quest_id"].startswith("fq_conc_"):
            continue
        node=next((n for n in dialog.get("nodes",[]) if n.get("id")=="accept"),None)
        if not node: continue
        objectives=[]
        for objective in quest.get("objectives",[]):
            verb={"kill":"Defeat","collect":"Collect","speak":"Speak with","interact":"Use"}.get(objective.get("type"),"Complete")
            target=objective.get("target_code") or objective.get("target")
            objectives.append(f"{verb} {objective.get('count',1)} {target}")
        region=quest.get("region","").replace("_"," ").title()
        faction=quest.get("faction","")
        voice=FACTION_LINES.get(faction,"Complete the task and bring back a clear account of what happened.")
        node["text"]=f"{quest.get('title','Assignment')}. In {region}: {'; '.join(objectives)}. {voice}"
        changed+=1
    (ROOT/"dialog_quests.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (ROOT/"24_updated_dialog_quests.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Synchronized acceptance instructions for {changed} non-Concordium faction quests")

if __name__=="__main__": main()
