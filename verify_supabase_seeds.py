#!/usr/bin/env python3
"""Verify generated Supabase upsert SQL contains current JSON record IDs."""

import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SEED=ROOT/"supabase"/"seed"
QUEST_FILES=["quest_list.json","quest_arcanum.json","quest_concordium.json","quest_iron.json","quest_legion.json","quest_meridian.json","quest_omnicorp.json","quest_shard.json","quest_neutral.json","quest_events.json"]

def ids_from_sql(path):
    return re.findall(r"values \('((?:''|[^'])*)'",path.read_text(encoding="utf-8"),re.IGNORECASE)

def check(domain,expected,full_file,part_pattern):
    expected=list(dict.fromkeys(expected))
    full=ids_from_sql(SEED/full_file)
    chunks=sorted(SEED.glob(part_pattern))
    chunk_ids=[rid for part in chunks for rid in ids_from_sql(part)]
    errors=[]
    variants=[(full_file,full)]
    if chunks:
        variants.append(("chunks",chunk_ids))
    for label,actual in variants:
        if len(actual)!=len(set(actual)):
            errors.append(f"{domain}: duplicate IDs in {label}")
        missing=set(expected)-set(actual)
        extra=set(actual)-set(expected)
        if missing or extra:
            errors.append(f"{domain}: {label} mismatch; missing={len(missing)} extra={len(extra)}")
    print(f"{domain}: {len(expected)} IDs, {len(chunks)} chunk(s), {'FAIL' if errors else 'OK'}")
    return errors

def main():
    npcs=json.loads((ROOT/"npc_list.json").read_text(encoding="utf-8"))
    npc_ids=[npc["npc_id"] for npc in npcs]
    quest_dialogues=json.loads((ROOT/"dialog_quests.json").read_text(encoding="utf-8"))["dialogues"]
    dialog_ids=[dialog["dialog_id"] for dialog in quest_dialogues]
    wrappers=json.loads((ROOT/"dialog_tree_master.json").read_text(encoding="utf-8"))
    dialog_ids.extend(dialog["dialog_id"] for wrapper in wrappers for dialog in wrapper.get("dialogues",[]))
    quest_ids=[]
    for filename in QUEST_FILES:
        path=ROOT/filename
        if not path.exists(): continue
        data=json.loads(path.read_text(encoding="utf-8"))
        records=data.get("quests",data) if isinstance(data,dict) else data
        quest_ids.extend(q["id"] for q in records if isinstance(q,dict) and q.get("id"))
    errors=[]
    errors+=check("NPCs",npc_ids,"npcs_seed.sql","npcs_seed_part*.sql")
    errors+=check("Dialogs",dialog_ids,"dialogs_seed.sql","dialogs_seed_part*.sql")
    errors+=check("Quests",quest_ids,"quests_seed.sql","quests_seed_part*.sql")
    apply_all=(ROOT/"supabase"/"apply_all.sql").read_text(encoding="utf-8")
    for domain,records in [("NPCs",npc_ids),("Dialogs",dialog_ids),("Quests",list(dict.fromkeys(quest_ids)))]:
        absent=[record_id for record_id in records if f"'{record_id.replace(chr(39),chr(39)*2)}'" not in apply_all]
        if absent: errors.append(f"apply_all.sql: {domain} missing {len(absent)} source IDs")
    if errors:
        for error in errors: print(f"ERROR {error}")
        raise SystemExit(1)

if __name__=="__main__": main()
