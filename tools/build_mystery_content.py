#!/usr/bin/env python3
"""Materialize the authored mystery pack and append only its new master records."""

from collections import defaultdict
from copy import deepcopy
import json
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'narrative/mystery_manifest.json'


def load(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8'))


def save(name, value):
    (ROOT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def append_unique(rows, additions, key):
    ids = {row[key] for row in rows if key in row}
    for row in additions:
        if row[key] in ids:
            raise ValueError(f'Refusing to replace existing {key}: {row[key]}')
        ids.add(row[key])
    rows.extend(additions)


def option(text, nxt, action=''):
    return {'text': text, 'next': nxt, 'action': action}


def node(nid, text, options):
    return {'id': nid, 'text': text, 'options': options}


def item(iid, name, description, icon, level=1, stats=None, clue=False):
    return {
        'id': iid, 'name': name, 'description': description,
        'type': 'ACCESSORY' if stats else 'QUEST',
        'rarity': 'EPIC' if stats else ('UNCOMMON' if clue else 'RARE'),
        'level_requirement': level if stats else 1,
        'equipment_slots': ['ACCESSORY_1', 'ACCESSORY_2'] if stats else [],
        'stats_bonus': {s: (stats or {}).get(s, 0) for s in ('hp', 'mp', 'atk', 'def', 'agi', 'per')},
        'special_effects': [], 'buy_price': 0, 'sell_price': 0,
        'max_stack': 99 if clue else 1, 'icon_image': icon,
    }


def npc(nid, name, title, region, dialogue, description, personality, greeting, prop=False):
    return {
        'npc_id': nid, 'name': name, 'title': title,
        'role': 'TERMINAL' if prop else 'QUEST_GIVER', 'faction': 'NEUTRAL',
        'dialogue_tree': dialogue, 'shop_inventory': None,
        'location': region['name'], 'region_id': region['id'],
        'description': description, 'personality': personality, 'greeting': greeting,
        'available_services': ['INFO'] if prop else ['QUEST', 'INFO'],
        'actions': [] if prop else ['take_quest'],
        'quest_category': 'mystery', 'reward_currency': 'CRD',
    }


def main():
    if MANIFEST.exists():
        raise SystemExit('Pack already materialized. Edit scoped records explicitly; do not replay this append-only builder.')
    authored = load('narrative/mystery_catalogue.json')
    world = load('world_map_v4.json')
    monsters = load('monster_master.json')
    items = load('item_list.json')
    npcs = load('npc_list.json')
    generic = load('dialog_tree_master.json')
    quest_dialogs = load('dialog_quests.json')
    titles = load('title_master.json')
    biome = load('biome_monster_mapping.json')
    nodes = {n['id']: n for n in world['nodes']}
    templates = {m['monster_id']: m for m in monsters['monsters']}
    layout = {n['id']: n for n in world['node_map']['layout_nodes']}
    added = {k: [] for k in ('quests', 'npcs', 'items', 'monsters', 'regions', 'dialogs', 'titles', 'pending_achievements')}
    design = []
    finals = [f"mq_{a['id']}_{a['quests'][-1]['slug']}" for a in authored['arcs']]

    for arc_index, arc in enumerate(authored['arcs']):
        parent = nodes[arc['parent_region']]
        rid = arc['region_id']
        region = deepcopy(parent)
        region.update({
            'id': rid, 'name': arc['region_name'], 'node_type': parent['node_type'],
            'level_range': arc['level_range'], 'faction_owner': 'NONE',
            'is_safe_zone': False, 'is_pvp_enabled': False,
            'available_actions': ['hunt', 'travel'],
            'monster_spawns': [{'monster_id': arc['monster_id'], 'spawn_weight': 100}],
            'resource_nodes': [], 'world_events': [],
            'relative_layout': {'west': parent['id']},
            'world_position': {'x': parent['world_position']['x'] + 0.35, 'y': parent['world_position']['y'] + 0.25},
            'map_position': {**parent['map_position'], 'local_x': 75, 'local_y': 75},
        })
        prop_ids = [f"npc_mystery_{arc['id']}_clue_{i + 1}" for i in range(2)]
        region['npc_ids'] = [arc['npc_id']] + prop_ids
        added['regions'].append(region)
        clue_ids = [f"mq_clue_{arc['id']}_{i + 1}" for i in range(2)]
        for i, name in enumerate(arc['clue_items']):
            added['items'].append(item(clue_ids[i], name,
                f"Recovered at {arc['region_name']}. {arc['site']} A field record, not an established answer to Xylos's ancient mysteries.", arc['icon'], clue=True))
        monster = deepcopy(templates[arc['template_id']])
        monster.update({
            'monster_id': arc['monster_id'], 'code': arc['monster_code'], 'name': arc['monster_name'],
            'spawn_monster_id': rid, 'spawn_location': [rid],
            'ai_pattern': {'behavior': 'standard_rotation'},
            'drop_item': [{'itemId': cid, 'chance': 1.0} for cid in clue_ids], 'special_reward': [],
        })
        added['monsters'].append(monster)
        gid = f"dialog_mystery_{arc['id']}_greet"
        added['npcs'].append(npc(arc['npc_id'], arc['npc_name'], arc['npc_title'], region, gid,
            arc['motivation'], arc['personality'], arc['voice']))
        greeting = {'dialog_id': gid, 'npc_id': arc['npc_id'], 'start_node': 'greet', 'nodes': [
            node('greet', f"{arc['voice']} {arc['site']}", [
                option('What did you notice here?', 'observation'),
                option('Why ask an outsider?', 'motive'), option('I will look around first.', 'exit', 'exit')]),
            node('observation', arc['quests'][0]['clues'][0], [option('Tell me more.', 'greet'), option('I will examine it.', 'exit', 'exit')]),
            node('motive', arc['motivation'], [option('What did you notice?', 'observation'), option('I will think about it.', 'exit', 'exit')]),
            node('exit', 'The evidence remains available when you return.', []),
        ]}
        added['dialogs'].append(greeting)
        for i, pid in enumerate(prop_ids):
            did = f'dialog_{pid}'
            observation = arc['site'] if i == 0 else arc['quests'][1]['clues'][i]
            added['npcs'].append(npc(pid, arc['props'][i], 'Field Evidence', region, did,
                observation, 'environmental_record', observation, prop=True))
            added['dialogs'].append({'dialog_id': did, 'npc_id': pid, 'start_node': 'greet', 'nodes': [
                node('greet', observation, [option('Examine the mark.', 'detail'), option('Compare its placement.', 'placement'), option('Step away.', 'exit', 'exit')]),
                node('detail', arc['quests'][1]['clues'][i], [option('Look at its setting.', 'placement'), option('Step away.', 'exit', 'exit')]),
                node('placement', arc['site'], [option('Look again.', 'greet'), option('Step away.', 'exit', 'exit')]), node('exit', 'The record is left in place.', [])]})

        for stage, source in enumerate(arc['quests']):
            qid = f"mq_{arc['id']}_{source['slug']}"
            reward_id = f"mq_relic_{arc['id']}_{source['slug']}"
            title_id = f"mq_title_{arc['id']}_{source['slug']}"
            prior = [] if stage == 0 else [f"mq_{arc['id']}_{arc['quests'][stage - 1]['slug']}"]
            if arc_index == 4 and stage == 4:
                prior += finals[:4]
            objectives = []
            def objective(typ, target, text, code=None):
                row = {'type': typ, 'target': target, 'count': 1, 'description': text}
                if code:
                    row['target_code'] = code
                objectives.append(row)
            if source['mode'].startswith('collect'):
                which = 0 if source['mode'] == 'collect_first' else 1
                objective('collect', clue_ids[which], f"Recover the {arc['clue_items'][which]} from {arc['monster_name']} in {arc['region_name']}.")
            elif source['mode'] == 'combat':
                objective('kill', arc['monster_id'], f"Stop the dangerous {arc['monster_name']} in {arc['region_name']}.", arc['monster_code'])
                objective('travel', rid, f"Inspect the now-safe evidence area in {arc['region_name']}.")
            for pid, name in zip(prop_ids, arc['props']):
                objective('interact', pid, f"Examine {name} and compare its evidence.")
            objective('interact', arc['npc_id'], f"Discuss your finding with {arc['npc_name']} in {arc['region_name']}.")
            choices = [{'id': f'choice_{i + 1}', 'label': c[0], 'cost': c[1], 'visible_consequence': c[2],
                        'flag': f'{qid}.choice_{i + 1}', 'npc_response': f"If we choose that: {c[2]} The cost is clear: {c[1]}."}
                       for i, c in enumerate(source['choices'])]
            discovery = {'type': 'item_acquired', 'item_id': clue_ids[0], 'region_id': rid} if stage == 0 else {
                'type': 'quest_completed', 'quest_id': prior[0], 'region_id': rid}
            requirement = {
                'min_level': source['level'], 'reputation_required': 0, 'required_quests': prior,
                'required_items': [], 'party_required': False, 'raid_size': 1,
                'mystery': {'schema_version': 1, 'pack_id': authored['meta']['pack_id'],
                    'release_status': 'client_integration_required', 'discovery': discovery,
                    'hide_until_discovered': True, 'hide_waypoints_until_discovered': True,
                    'decision_required': True, 'decision_group': qid, 'choice_ids': [c['id'] for c in choices],
                    'enforce_real_interactions': True, 'evidence_prop_ids': prop_ids},
            }
            quest = {'id': qid, 'title': source['title'], 'type': source['kind'],
                'rank': 'B' if source['level'] <= 10 else ('A' if source['level'] < 40 else 'S'),
                'faction': 'NEUTRAL', 'region': rid, 'description': source['premise'],
                'quest_giver': {'npc_id': arc['npc_id'], 'name': arc['npc_name'], 'location': arc['region_name']},
                'requirements': requirement, 'objectives': objectives,
                'rewards': {'exp': source['level'] * 30, 'currency': 0, 'crd': source['level'] * 10,
                    'reputation': 15 if stage < 4 else 40, 'items': [{'item_id': reward_id, 'quantity': 1}]},
                'repeatable': False, 'daily': False,
                'quest_chain_next': f"mq_{arc['id']}_{arc['quests'][stage + 1]['slug']}" if stage < 4 else None}
            added['quests'].append(quest)
            reward = item(reward_id, source['reward'], source['reward_lore'], arc['icon'], source['level'], source.get('accessory_stats'))
            if arc_index == 4 and stage == 4:
                reward['rarity'] = 'LEGENDARY'
            added['items'].append(reward)
            rarity = 'LEGENDARY' if arc_index == 4 and stage == 4 else ('EPIC' if stage == 4 else 'RARE')
            added['titles'].append({'id': title_id, 'name': source['title_reward'], 'description': source['reward_lore'],
                'rarity': rarity, 'tier': 5 if rarity == 'LEGENDARY' else (4 if rarity == 'EPIC' else 3),
                'unlock': {'type': 'quest_completed', 'quest_id': qid}, 'stat_bonus': {}})
            added['pending_achievements'].append({'id': f'mq_achievement_{arc["id"]}_{source["slug"]}',
                'name': source['title'], 'description': f"Complete {source['title']} and preserve a witnessed finding.",
                'category': 'quests', 'metric': f'mystery_completed.{qid}', 'operator': 'gte', 'threshold': 1,
                'tier': 'gold' if stage == 4 else 'silver', 'reward_title': title_id, 'reward_rubies': 0,
                'hidden': True, 'sort_order': len(added['pending_achievements'])})
            dialog_id = f'dialog_{qid}'
            acceptance = f"Keep these points separate: {' '.join(o['description'] for o in objectives)}"
            tree_nodes = [node('greeting', source['opening'], [
                option('Show me what the evidence actually says.', 'evidence'),
                option('Who pays the cost of our decision?', 'decision'),
                option('I need more time.', 'exit', 'exit')]),
                node('evidence', ' '.join(source['clues']), [option('What are our options?', 'decision'), option('I will investigate.', 'accept'), option('I will return later.', 'exit', 'exit')]),
                node('decision', source['premise'], [option(c['label'], c['id']) for c in choices] + [option('I will not decide yet.', 'exit', 'exit')])]
            tree_nodes += [node(c['id'], c['npc_response'], [option('I will verify the evidence first.', 'accept'), option('I need more time.', 'exit', 'exit')]) for c in choices]
            tree_nodes += [node('accept', acceptance, [option('Begin this investigation.', 'exit', 'accept_quest'), option('Not yet.', 'exit', 'exit')]),
                          node('exit', 'You may return without losing your place in the investigation.', [])]
            added['dialogs'].append({'dialog_id': dialog_id, 'quest_id': qid, 'npc_id': arc['npc_id'], 'start_node': 'greeting', 'nodes': tree_nodes})
            design.append({'quest_id': qid, 'arc_id': arc['id'], 'kind': source['kind'],
                'era': arc['era'], 'faction_context': arc['faction_context'], 'npc_motivation': arc['motivation'],
                'discovery': discovery, 'breadcrumbs': source['clues'], 'answer': source['answer'],
                'decision_choices': choices, 'choice_persistence': 'pending_client_integration',
                'dialog_state_lines': {'available': source['opening'], 'active': arc['voice'],
                    'ready': source['answer'], 'completed': source['completion']},
                'consequence_application': 'personal_save_flags_and_npc_state_not_global_map_mutation',
                'consequence_activation': 'on_turn_in_only_after_valid_evidence_and_one_choice',
                'title_id': title_id, 'achievement_id': added['pending_achievements'][-1]['id'],
                'retry_rule': 'No fail-on-wrong-answer, timed window, permanent lockout, or consumed clue. Offer escalating hints after retries.',
                'spoiler_policy': 'No journal entry before discovery; details appear only after finding the first clue.'})

        # Register each annex in both route systems used by the current map data.
        append_unique(world['nodes'], [region], 'id')
        world['routes'].append({'from': parent['id'], 'to': rid, 'route_type': 'secondary',
            'min_level': arc['level_range'][0], 'travel_time': 30, 'danger_level': 1})
        edge = {'from': parent['id'], 'to': rid, 'type': 'trade', 'bidirectional': True, 'label': f"Field path to {arc['region_name']}"}
        world['edges'].append(edge)
        world['node_map']['visual_edges'].append({k: edge[k] for k in ('from', 'to', 'type')})
        anchor = layout[parent['id']]
        world['node_map']['layout_nodes'].append({'id': rid, 'label': region['name'],
            'x': anchor['x'] + 32, 'y': anchor['y'] - 28, 'icon': 'minor', 'faction': 'NEUTRAL'})

    # Validate all append collisions before replacing any canonical file.
    append_unique(npcs, added['npcs'], 'npc_id')
    append_unique(items['items'], added['items'], 'id')
    append_unique(monsters['monsters'], added['monsters'], 'monster_id')
    append_unique(titles['titles'], added['titles'], 'id')
    append_unique(quest_dialogs['dialogues'], [d for d in added['dialogs'] if d.get('quest_id')], 'dialog_id')
    master_dialogs = [d for block in generic for d in block.get('dialogues', [])]
    generic_add = [d for d in added['dialogs'] if not d.get('quest_id')]
    append_unique(master_dialogs, generic_add, 'dialog_id')
    generic.append({'dialogues': generic_add})
    weights = defaultdict(lambda: defaultdict(float))
    for n in world['nodes']:
        primary = n.get('biome', {}).get('primary')
        if primary:
            for spawn in n.get('monster_spawns', []):
                weights[primary][spawn['monster_id']] += spawn['spawn_weight']
    for mapping in biome['mappings']:
        aggregate = weights.get(mapping['biome_primary'], {})
        mids = sorted(aggregate)
        total = sum(aggregate.values())
        mapping.update({'monster_ids': mids, 'spawn_weights': [aggregate[mid] / total for mid in mids]})

    saves = {'quest_mysteries.json': {'meta': authored['meta'], 'quests': added['quests']},
        'world_map_v4.json': world, 'npc_list.json': npcs, 'item_list.json': items,
        'monster_master.json': monsters, 'title_master.json': titles,
        'dialog_tree_master.json': generic, 'dialog_quests.json': quest_dialogs,
        'biome_monster_mapping.json': biome,
        'narrative/mystery_design.json': {'meta': authored['meta'], 'quests': design},
        'narrative/mystery_achievements_pending.json': {'meta': {'release_status': 'pending_client_metric_bridge',
            'required_hook': 'On successful one-time mystery turn-in, set mystery_completed.<quest_id> to 1; backfill from completedQuestIds.',
            'instructions': 'Do not merge into achievements.json or seed until the metric producer and save backfill have tests.'},
            'achievements': added['pending_achievements']}}
    collections = {'item_list.json': ('items', 'id'), 'monster_master.json': ('monsters', 'monster_id'),
        'npc_list.json': (None, 'npc_id'), 'title_master.json': ('titles', 'id'),
        'dialog_quests.json': ('dialogues', 'dialog_id'), 'world_map_v4.json': ('nodes', 'id')}
    baseline = {}
    for name, (collection, key) in collections.items():
        original = load(name)
        rows = original[collection] if collection else original
        baseline[name] = {'collection': collection, 'key': key, 'hashes': {
            str(row[key]): hashlib.sha256(json.dumps(row, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
            for row in rows}}
    baseline_path = ROOT / 'narrative/mystery_baseline.json'
    if baseline_path.exists():
        raise ValueError('Refusing to replace an existing content baseline')
    save('narrative/mystery_baseline.json', baseline)
    for name, value in saves.items():
        save(name, value)
    save('narrative/mystery_manifest.json', {
        'pack_id': authored['meta']['pack_id'], 'created_on': authored['meta']['authored_on'],
        'ids': {key: [row['dialog_id' if key == 'dialogs' else 'npc_id' if key == 'npcs' else 'monster_id' if key == 'monsters' else 'id'] for row in rows]
                for key, rows in added.items()},
        'records': added,
        'modified_files': list(saves), 'live_applied': False, 'git_pushed': False,
        'client_modified': False,
    })
    print(json.dumps({k: len(v) for k, v in added.items()}))


if __name__ == '__main__':
    main()
