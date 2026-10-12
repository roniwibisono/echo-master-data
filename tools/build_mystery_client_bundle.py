#!/usr/bin/env python3
"""Export only the mystery pack as a versioned Flutter release asset."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--client', type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'narrative/mystery_manifest.json').read_text())
    records = manifest['records']
    world = json.loads((ROOT / 'world_map_v4.json').read_text())
    region_ids = set(manifest['ids']['regions'])
    files = {
        'quest_mysteries.json': {'quests': records['quests']},
        'narrative/mystery_design.json': json.loads((ROOT / 'narrative/mystery_design.json').read_text()),
    }
    overlays = {}

    def rows(file, path, key, values):
        overlays.setdefault(file, []).append({'path': path, 'key': key, 'rows': values})

    for file, collection, key in [('item_list.json', 'items', 'id'),
                                  ('monster_master.json', 'monsters', 'monster_id'),
                                  ('title_master.json', 'titles', 'id')]:
        rows(file, [collection], [key], records[collection])
    rows('npc_list.json', [], ['npc_id'], records['npcs'])
    rows('dialog_quests.json', ['dialogues'], ['dialog_id'], [d for d in records['dialogs'] if d.get('quest_id')])
    rows('dialog_tree_master.json', [0, 'dialogues'], ['dialog_id'], [d for d in records['dialogs'] if not d.get('quest_id')])
    rows('achievements.json', ['achievements'], ['id'],
         records.get('achievements', records.get('pending_achievements', [])))
    rows('world_map_v4.json', ['nodes'], ['id'], records['regions'])
    for collection in ['routes', 'edges']:
        rows('world_map_v4.json', [collection], ['from', 'to'],
             [r for r in world[collection] if r['from'] in region_ids or r['to'] in region_ids])
    rows('world_map_v4.json', ['node_map', 'layout_nodes'], ['id'],
         [r for r in world['node_map']['layout_nodes'] if r['id'] in region_ids])
    rows('world_map_v4.json', ['node_map', 'visual_edges'], ['from', 'to'],
         [r for r in world['node_map']['visual_edges'] if r['from'] in region_ids or r['to'] in region_ids])
    bundle = {'pack_id': manifest['pack_id'], 'version': 1, 'files': files, 'overlays': overlays}
    target = args.client / 'assets/data/mystery_pack.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + '\n')
    print(f'Exported scoped mystery bundle to {target}')


if __name__ == '__main__':
    main()
