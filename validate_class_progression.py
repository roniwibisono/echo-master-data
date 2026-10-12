#!/usr/bin/env python3
"""Validate the playable class trials against actual faction spawn catalogues."""
import json
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parent

def load(name):return json.loads((ROOT/name).read_text())

def main():
    pack=load('narrative/class_progression_pack.json')
    classes=load('class_list.json'); cmap={c['id']:c for c in classes}
    skills={s['id'] for s in load('skill_list.json')}
    items={i['id']:i for i in load('item_list.json')['items']}
    npcs={n['npc_id']:n for n in load('npc_list.json')}
    nodes={n['id']:n for n in load('world_map_v4.json')['nodes']}
    monsters={m['monster_id']:m for m in load('monster_master.json')['monsters']}
    dialogues={d['dialog_id']:d for d in load('dialog_quests.json')['dialogues']}
    trials=[q for q in load('quest_list.json')['quests'] if q.get('requirements',{}).get('class_promotion')]
    errors=[];matrix=[];tiers=['Base','Advance','Expert','Master'];levels=[5,20,40,60]
    def check(condition,message):
        if not condition: errors.append(message)
    check(len(trials)==28,'Expected 28 class trials')
    check(len(cmap)==len(classes)==88,'Expected 88 unique class definitions')
    for c in classes:
        check(c.get('isActive') in [0,1],c['id']+': invalid active flag')
        check(bool(c.get('description')),c['id']+': missing description')
        check(c['tier'] in tiers,c['id']+': unsupported tier')
        check(all(s in skills for s in c['learnable_skill_ids']),c['id']+': missing skill')
        if c['parent_id']:
            parent=cmap.get(c['parent_id'])
            check(parent is not None,c['id']+': missing parent')
            if parent:check(tiers.index(c['tier'])==tiers.index(parent['tier'])+1,c['id']+': skipped tier')
        if c['tier']!='Master':check(any(x['parent_id']==c['id'] for x in classes),c['id']+': dead-end branch')
    for q in trials:
        r=q['requirements']['class_promotion'];t=tiers.index(r['tier']);n=npcs.get(r['trainer_npc_id']);region=nodes.get(q['region']);capital=nodes.get(r['trainer_region'])
        check(q['requirements']['min_level']==levels[t],q['id']+': incorrect level gate')
        check(not q['repeatable'] and not q['daily'],q['id']+': repeatable proof')
        check(not q['requirements']['required_quests'] and not q['requirements']['required_items'],q['id']+': circular legacy prerequisites')
        check(not q['requirements']['party_required'],q['id']+': unsupported party gate')
        check(n and n['faction']==q['faction'],q['id']+': wrong faction trainer')
        check(capital and capital['faction_owner']==q['faction'],q['id']+': wrong trainer territory')
        check(n and n['region_id']==r['trainer_region'],q['id']+': unreachable trainer placement')
        check(n and n['dialogue_tree']=='dialog_'+q['id'],q['id']+': trainer dialogue pointer missing')
        check(capital and n['npc_id'] in capital['npc_ids'],q['id']+': trainer absent from map')
        check(capital and capital['level_range'][0]<=5,q['id']+': trainer capital inaccessible to novice')
        check(region and region['faction_owner']==q['faction'],q['id']+': wrong faction hunt')
        proof=items.get(r['proof_item_id'])
        check(proof and proof['type']=='QUEST_ITEM' and proof['sell_price']==0,q['id']+': invalid trial proof')
        check(q['rewards']['items']==[{'item_id':r['proof_item_id'],'quantity':1}],q['id']+': non-deterministic proof reward')
        d=dialogues.get('dialog_'+q['id'])
        check(d and d['npc_id']==n['npc_id'],q['id']+': missing matching dialogue')
        if d:check({x['id'] for x in d['nodes']}=={'offer','progress','report','certified'},q['id']+': missing dialogue phase')
        for o in q['objectives']:
            m=monsters.get(int(o['target']))
            check(o['type']=='kill' and o['count']>0,q['id']+': unsupported objective')
            check(m and m['code']==o['target_code'],q['id']+': mismatched monster identity')
            check(m and m['level']<=levels[t],q['id']+': hunt exceeds promotion level')
            check(region and any(s['monster_id']==o['target'] and s['spawn_weight']>0 for s in region['monster_spawns']),q['id']+': missing positive spawn')
            check(m and m['rank'] not in ['raid_boss','dungeon_boss'],q['id']+': requires external raid flow')
        matrix.append({'quest':q['id'],'tier':r['tier'],'level':levels[t],'faction':q['faction'],'trainer':n['name'],'trainer_region':capital['name'],'hunting_region':region['name'],'proof':proof['name'],'targets':[o['description'] for o in q['objectives']]})
    check(len({q['requirements']['class_promotion']['proof_item_id'] for q in trials})==28,'Proofs are shared across factions/tiers')
    for f in ROOT.glob('quest_*.json'):
        data=json.loads(f.read_text());qs=(data[0] if isinstance(data,list) else data).get('quests',[])
        for q in qs:
            if 'id' not in q: continue
            check(q['id'] not in pack['retired_quests'],f.name+': retired quest remains')
            check(q.get('quest_chain_next') not in pack['retired_quests'],q['id']+': retired chain link')
            check(not set(q.get('requirements',{}).get('required_quests',[])) & set(pack['retired_quests']),q['id']+': retired prerequisite')
    check(pack['classes']==classes,'Client class definitions differ from master')
    result={'errors':errors,'trials':len(trials),'classes_by_tier':dict(Counter(c['tier'] for c in classes)),'class_skill_ids':len({s for c in classes for s in c['learnable_skill_ids']}),'proofs':28,'new_mentors':21,'matrix':matrix}
    (ROOT/'narrative/class_progression_validation.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='matrix'}))
    if errors:raise SystemExit(1)

if __name__=='__main__':main()
