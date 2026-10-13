"""Repair unsupported neutral objectives using existing field encounters."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Preserve objective positions/counts so accepted quests retain earned progress.
RULES = {
    'QUEST_NEUTRAL_STORY_001': {1: ('kill', 'FERAL_SCAVENGER', 'BROKEN_CIVIL_QUARTER')},
    'QUEST_NEUTRAL_STORY_002': {0: ('travel', 'BLACK_DOCK_MARKET', None), 1: ('collect', 'contraband_core', 'BLACK_DOCK_MARKET'), 2: ('kill', 'BLACK_DOCK_ENFORCER', 'BLACK_DOCK_MARKET')},
    'QUEST_NEUTRAL_STORY_003': {0: ('travel', 'TITAN_ASSEMBLY_YARD', None), 1: ('kill', 'TITAN_ASSEMBLY_SENTINEL', 'TITAN_ASSEMBLY_YARD'), 2: ('kill', 'TITAN_PROTO_CORE', 'TITAN_ASSEMBLY_YARD')},
    'QUEST_NEUTRAL_SIDE_001': {0: ('travel', 'BROKEN_CIVIL_QUARTER', None)},
    'QUEST_NEUTRAL_SIDE_002': {0: ('travel', 'SECURE_MINING_GRID', None), 1: ('collect', 'refined_scrap', 'SECURE_MINING_GRID')},
    'QUEST_NEUTRAL_DAILY_001': {0: ('kill', 'SCRAPFIELD_ENFORCER', 'SCRAP_FIELD')},
    'QUEST_NEUTRAL_DAILY_003': {0: ('travel', 'EXTRACTION_ZONE_DELTA', None)},
    'QUEST_NEUTRAL_AMA_001': {0: ('travel', 'FORGE_CANYON_DEPTHS', None), 1: ('kill', 'WARPATH_SCOUT', 'FORGE_CANYON_DEPTHS'), 2: ('kill', 'WARPATH_CHAMPION', 'FORGE_CANYON_DEPTHS'), 3: ('collect', 'rare_emblem', 'FORGE_CANYON_DEPTHS')},
    'QUEST_NEUTRAL_AMA_002': {0: ('travel', 'SKYBRIDGE_REACTOR', None), 1: ('kill', 'TITAN_ASSEMBLY_SENTINEL', 'SKYBRIDGE_REACTOR')},
    'QUEST_NEUTRAL_SPECIAL_001': {0: ('kill', 'WARPATH_SCOUT', 'BORDER_SKIRMISH_RING'), 3: ('kill', 'BLACK_DOCK_ASSASSIN', 'BLACK_DOCK_MARKET')},
}


def build():
    path = ROOT / 'quest_neutral.json'
    data = json.loads(path.read_text())
    monsters = json.loads((ROOT / 'monster_master.json').read_text())['monsters']
    by_code = {m['code']: m for m in monsters}
    nodes = json.loads((ROOT / 'world_map_v4.json').read_text())['nodes']
    names = {n['id']: n['name'] for n in nodes}
    items = json.loads((ROOT / 'item_list.json').read_text())['items']
    item_names = {i['id']: i['name'] for i in items}
    patches = {}
    for q in data['quests']:
        if q.get('id') not in RULES:
            continue
        changes = {}
        for index, (kind, target, region) in RULES[q['id']].items():
            count = q['objectives'][index]['count']
            obj = {'type': kind, 'target': target, 'count': count}
            if kind == 'kill':
                obj['target'] = by_code[target]['monster_id']
                obj['target_code'] = target
                obj['description'] = f"Defeat {{count}} {by_code[target]['name']} in {names[region]}."
            elif kind == 'collect':
                obj['description'] = f"Recover {{count}} {item_names.get(target, target.replace('_', ' ').title())} in {names[region]}."
            else:
                obj['description'] = f"Travel to {names[target]}."
            if region:
                obj['location'] = region
            q['objectives'][index] = obj
            changes[str(index)] = obj
        patches[q['id']] = {'objectives': changes}
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    pack = {'version': 1, 'repairs': patches}
    (ROOT / 'quest_reachability_pack.json').write_text(json.dumps(pack, indent=2) + '\n')
    sql = ['-- Scoped objective repair; rewards and unrelated content are unchanged.', 'begin;']
    for quest_id, patch in patches.items():
        expression = 'objectives'
        for index, objective in patch['objectives'].items():
            value = json.dumps(objective).replace("'", "''")
            expression = f"jsonb_set({expression}, '{{{index}}}', '{value}'::jsonb, false)"
        sql.append(f"update public.quests set objectives = {expression} where id = '{quest_id}';")
    sql.append('commit;')
    (ROOT / 'supabase/seed/quest_reachability_patch.sql').write_text('\n'.join(sql) + '\n')


if __name__ == '__main__':
    build()
