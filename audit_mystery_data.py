#!/usr/bin/env python3
"""Validate the additive mystery pack, its dependencies, and preserved records."""

from collections import Counter, defaultdict, deque
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8'))


def audit():
    quests = load('quest_mysteries.json')['quests']
    design = {q['quest_id']: q for q in load('narrative/mystery_design.json')['quests']}
    manifest = load('narrative/mystery_manifest.json')
    world = load('world_map_v4.json')
    nodes = {n['id']: n for n in world['nodes']}
    monsters = {m['monster_id']: m for m in load('monster_master.json')['monsters']}
    npcs = {n['npc_id']: n for n in load('npc_list.json')}
    items = {i['id']: i for i in load('item_list.json')['items']}
    titles = {t['id']: t for t in load('title_master.json')['titles']}
    dialogs = load('dialog_quests.json')['dialogues'] + [d for b in load('dialog_tree_master.json') for d in b.get('dialogues', [])]
    by_dialog = {d['dialog_id']: d for d in dialogs}
    by_quest = {q['id']: q for q in quests}
    skills = {s['id']: s for s in load('skill_list.json')}
    errors = []

    def check(test, message):
        if not test:
            errors.append(message)

    for name, rows, key in [('quest', quests, 'id'), ('npc', list(npcs.values()), 'npc_id'),
                           ('dialog', dialogs, 'dialog_id')]:
        for value, count in Counter(r[key] for r in rows).items():
            check(count == 1, f'{name}: duplicate {value}')
    check(len(quests) == 25, 'Expected 25 quests')
    check(set(by_quest) == set(design), 'Quest/design membership differs')
    graph = defaultdict(list)
    for route in world['routes']:
        graph[route['from']].append((route['to'], route['min_level']))
        graph[route['to']].append((route['from'], route['min_level']))

    def reachable(level):
        seen, queue = {'NEXUS_CORE'}, deque(['NEXUS_CORE'])
        while queue:
            for dest, required in graph[queue.popleft()]:
                if required <= level and dest not in seen:
                    seen.add(dest)
                    queue.append(dest)
        return seen

    for q in quests:
        qid, region = q['id'], nodes.get(q['region'])
        check(q['type'] in ('secret', 'mystery'), f'{qid}: unsupported pack kind')
        check(not q['repeatable'] and not q['daily'], f'{qid}: prestige must be one-time')
        check(q['faction'] == 'NEUTRAL', f'{qid}: not cross-faction')
        check(q['rewards']['currency'] == 0 and q['rewards']['crd'] > 0, f'{qid}: neutral currency rule')
        check(region is not None, f'{qid}: missing region')
        check(q['region'] in reachable(q['requirements']['min_level']), f'{qid}: region unreachable at required level')
        giver = npcs.get(q['quest_giver']['npc_id'])
        check(giver is not None and giver['region_id'] == q['region'] and giver['name'] == q['quest_giver']['name'], f'{qid}: inconsistent giver')
        rules = q['requirements']['mystery']
        expected_status = 'client_playable_pending_release' if manifest.get('client_integration_verified') else 'client_integration_required'
        check(rules['release_status'] == expected_status, f'{qid}: unsafe activation claim')
        check(rules['hide_until_discovered'] and rules['decision_required'], f'{qid}: missing mystery rules')
        checked_props = {o['target'] for o in q['objectives'] if o['type'] == 'interact' and o['target'] != q['quest_giver']['npc_id']}
        check(checked_props == set(rules['evidence_prop_ids']), f'{qid}: evidence rules do not match visible objectives')
        for prior in q['requirements']['required_quests']:
            check(prior in by_quest and prior != qid, f'{qid}: bad prerequisite {prior}')
            if prior in by_quest:
                check(by_quest[prior]['requirements']['min_level'] <= q['requirements']['min_level'], f'{qid}: prerequisite level exceeds quest')
        if q['quest_chain_next']:
            check(q['quest_chain_next'] in by_quest and qid in by_quest[q['quest_chain_next']]['requirements']['required_quests'], f'{qid}: broken next link')
        for objective in q['objectives']:
            typ, target = objective['type'], objective['target']
            check(objective['count'] == 1, f'{qid}: repetitive count or invalid count')
            check(typ in {'collect', 'kill', 'travel', 'interact'}, f'{qid}: unsupported objective {typ}')
            if typ == 'kill':
                m = monsters.get(target)
                check(m is not None and m['code'] == objective.get('target_code'), f'{qid}: invalid numeric/code kill link')
                check(region and target in {s['monster_id'] for s in region['monster_spawns']}, f'{qid}: kill not locally spawned')
            elif typ == 'collect':
                check(target in items, f'{qid}: undefined collect item')
                local = [monsters[s['monster_id']] for s in region['monster_spawns']] if region else []
                check(any(d['itemId'] == target and d['chance'] == 1 for m in local for d in m['drop_item']), f'{qid}: clue has no guaranteed local source')
            elif typ == 'interact':
                check(target in npcs and target in (region or {}).get('npc_ids', []), f'{qid}: inaccessible interaction {target}')
            elif typ == 'travel':
                check(target in nodes, f'{qid}: undefined travel target')
        for reward in q['rewards']['items']:
            check(reward['item_id'] in items and reward['quantity'] == 1, f'{qid}: reward undefined or duplicated')
        details = design[qid]
        check(len(details['breadcrumbs']) >= 3 and bool(details['answer']), f'{qid}: missing solvable breadcrumb chain')
        check(len(details['decision_choices']) == 3, f'{qid}: expected three decisions')
        check(all(c['cost'] and c['visible_consequence'] for c in details['decision_choices']), f'{qid}: costless or empty decision')
        title = titles.get(details['title_id'])
        check(title and title['unlock'] == {'type': 'quest_completed', 'quest_id': qid}, f'{qid}: invalid title unlock')
        check(title and title['stat_bonus'] == {}, f'{qid}: stacking title power inflation')

    def visit(qid, visiting, visited):
        if qid in visiting:
            errors.append(f'Prerequisite cycle: {qid}')
            return
        if qid in visited:
            return
        visiting.add(qid)
        for prior in by_quest[qid]['requirements']['required_quests']:
            if prior in by_quest:
                visit(prior, visiting, visited)
        visiting.remove(qid)
        visited.add(qid)
    visited = set()
    for qid in by_quest:
        visit(qid, set(), visited)
    capstone = by_quest['mq_armistice_unwritten_witness']
    check(len(capstone['requirements']['required_quests']) == 5, 'Capstone does not require all five arcs')

    for entry in manifest['records']['dialogs']:
        tree = by_dialog.get(entry['dialog_id'])
        check(tree == entry, f'Dialog drift: {entry["dialog_id"]}')
        if not tree:
            continue
        node_map = {n['id']: n for n in tree['nodes']}
        check(tree['start_node'] in node_map, f'{tree["dialog_id"]}: missing start')
        for n in tree['nodes']:
            check(bool(n['text'].strip()), f'{tree["dialog_id"]}: empty text')
            check(all(o['next'] in node_map for o in n['options']), f'{tree["dialog_id"]}: broken option')
        reached, queue = set(), [tree['start_node']]
        while queue:
            nid = queue.pop()
            if nid in reached or nid not in node_map:
                continue
            reached.add(nid)
            queue.extend(o['next'] for o in node_map[nid]['options'])
        check(reached == set(node_map), f'{tree["dialog_id"]}: unreachable node')
        can_exit = {'exit'}
        for _ in node_map:
            can_exit |= {nid for nid, n in node_map.items() if any(o['next'] in can_exit for o in n['options'])}
        check(can_exit == set(node_map), f'{tree["dialog_id"]}: dialog trap')
    for m in manifest['records']['monsters']:
        check(monsters[m['monster_id']] == m, f'Monster drift: {m["code"]}')
        for slot, expected in [('active_skills', 'Active'), ('passive_skills', 'Passive')]:
            for ref in m['skill_set'][slot]:
                skill = skills.get(ref['skill_id'])
                check(skill and skill['type'] == expected, f'{m["code"]}: wrong skill link')
                if expected == 'Active' and skill:
                    check(skill['mp_cost'] <= m['base_stats']['mp'], f'{m["code"]}: unaffordable skill')
    for i in manifest['records']['items']:
        check(items[i['id']] == i, f'Item drift: {i["id"]}')
        check((ROOT / i['icon_image']).is_file(), f'Item placeholder icon missing: {i["id"]}')
        check(i['sell_price'] == 0 and not i['special_effects'], f'{i["id"]}: farmable reward or unsupported proc')
    live_achievement_ids = {a['id'] for a in load('achievements.json')['achievements']}
    for a in load('narrative/mystery_achievements_pending.json')['achievements']:
        if manifest.get('achievements_activated'):
            check(manifest.get('client_integration_verified'), 'Unimplemented achievement activated: client bridge unverified')
            check(a['id'] in live_achievement_ids, f'Activated achievement missing: {a["id"]}')
        else:
            check(a['id'] not in live_achievement_ids, f'Unimplemented achievement activated: {a["id"]}')
        check(a['reward_title'] in titles and a['reward_rubies'] == 0 and a['hidden'], f'Invalid pending prestige achievement: {a["id"]}')

    preserved = 0
    for name, before in load('narrative/mystery_baseline.json').items():
        current = load(name)
        rows = current[before['collection']] if before['collection'] else current
        hashes = {str(row[before['key']]): hashlib.sha256(json.dumps(row, sort_keys=True, ensure_ascii=False).encode()).hexdigest() for row in rows}
        for rid, digest in before['hashes'].items():
            check(hashes.get(rid) == digest, f'Pre-existing record changed: {name}/{rid}')
            preserved += 1
    return {'counts': {k: len(v) for k, v in manifest['records'].items()}, 'preserved_records': preserved,
        'errors': errors, 'release_blockers': (['Client build publication'] if manifest.get('client_integration_verified') else ['Client quest/CDN registration', 'Discovery visibility and item-event reconciliation',
            'Real evidence interaction and ordered decision validation', 'Persisted choice/consequence dialogue states',
            'Achievement scalar metrics and old-save backfill']),
        'live_applied': manifest.get('live_applied', False),
        'client_modified': manifest.get('client_modified', False)}


if __name__ == '__main__':
    result = audit()
    (ROOT / 'narrative/mystery_validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(f"Mystery pack: {len(result['errors'])} data errors; {result['preserved_records']} existing records preserved.")
    for error in result['errors']:
        print(error)
    raise SystemExit(bool(result['errors']))
