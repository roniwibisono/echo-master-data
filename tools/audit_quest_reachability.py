"""Structural audit: playable targets, drops, travel and prerequisite links."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = ['quest_list.json', 'quest_concordium.json', 'quest_arcanum.json',
         'quest_iron.json', 'quest_meridian.json', 'quest_omnicorp.json',
         'quest_shard.json', 'quest_legion.json', 'quest_events.json',
         'quest_mysteries.json', 'quest_neutral.json']


def audit():
    nodes = json.loads((ROOT / 'world_map_v4.json').read_text())['nodes']
    monsters = json.loads((ROOT / 'monster_master.json').read_text())['monsters']
    ids = {n['id'] for n in nodes}
    spawned = {s['monster_id'] for n in nodes if not n['is_safe_zone']
               for s in n['monster_spawns'] if s['spawn_weight'] > 0}
    live = [m for m in monsters if m['monster_id'] in spawned]
    codes = {m['code'] for m in live}
    drops = {d['itemId'] for m in live for d in m.get('drop_item', []) if d.get('chance', 0) > 0}
    drops.update(r['node_id'] for n in nodes for r in n.get('resource_nodes', []))
    quests = [(f, q) for f in FILES for q in json.loads((ROOT / f).read_text())['quests'] if q.get('id')]
    quest_ids = {q['id'] for _, q in quests}
    errors = []
    counts = {}
    for f, q in quests:
        for o in q.get('objectives', []):
            kind = o['type']
            counts[kind] = counts.get(kind, 0) + 1
            target = o['target']
            reason = None
            if kind == 'kill' and target not in spawned and target not in codes and o.get('target_code') not in codes:
                reason = 'kill target has no non-safe positive-weight spawn'
            elif kind == 'travel' and target not in ids:
                reason = 'travel destination does not exist'
            elif kind == 'collect' and target not in drops:
                reason = 'collect target has no field drop or resource source'
            elif kind not in {'kill', 'travel', 'collect', 'interact', 'action', 'level'}:
                reason = 'objective event is not emitted by the game'
            if reason:
                errors.append({'file': f, 'quest': q['id'], 'target': target, 'reason': reason})
        for prerequisite in q.get('requirements', {}).get('required_quests', []):
            if prerequisite not in quest_ids:
                errors.append({'file': f, 'quest': q['id'], 'target': prerequisite, 'reason': 'missing prerequisite'})
    return {'quests': len(quests), 'objectives': counts, 'errors': errors,
            'limitations': ['Interaction fallback and content activation must also be verified in the client; this is not a full gameplay simulation.']}


if __name__ == '__main__':
    report = audit()
    (ROOT / 'quest_reachability_audit.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    raise SystemExit(bool(report['errors']))
