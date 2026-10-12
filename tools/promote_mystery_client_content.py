#!/usr/bin/env python3
"""Promote tested mystery definitions; this does not publish or modify live DB."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(name):
    return json.loads((ROOT / name).read_text())


def write(name, data):
    (ROOT / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def main():
    validation = read('narrative/mystery_client_validation.json')
    if validation['status'] != 'passed' or validation['complete_quest_flow_count'] != 25:
        raise ValueError('Client completion/metric bridge has not been verified')
    manifest = read('narrative/mystery_manifest.json')
    pending = read('narrative/mystery_achievements_pending.json')
    canonical = read('achievements.json')
    added_ids = {a['id'] for a in pending['achievements']}
    existing = [a for a in canonical['achievements'] if a['id'] not in added_ids]
    start = max((a['sort_order'] for a in existing), default=-1) + 1
    added = [dict(a, sort_order=start + i) for i, a in enumerate(pending['achievements'])]
    write('narrative/mystery_achievements.json', {
        'meta': {'pack_id': manifest['pack_id'], 'activation': 'verified_client_metric_bridge', 'count': len(added)},
        'achievements': added,
    })
    canonical['achievements'] = existing + added
    canonical['meta']['count'] = len(canonical['achievements'])
    write('achievements.json', canonical)
    quests = read('quest_mysteries.json')
    for q in quests['quests']:
        q['requirements']['mystery']['release_status'] = 'client_playable_pending_release'
    write('quest_mysteries.json', quests)
    for name in ['narrative/mystery_catalogue.json', 'narrative/mystery_design.json']:
        data = read(name)
        data['meta']['release_status'] = 'client_playable_pending_release'
        if name.endswith('mystery_design.json'):
            for q in data['quests']:
                q['choice_persistence'] = 'player_quest_progress.decision_id'
        write(name, data)
    manifest['records']['quests'] = quests['quests']
    manifest['records'].pop('pending_achievements', None)
    manifest['ids'].pop('pending_achievements', None)
    manifest['records']['achievements'] = added
    manifest['ids']['achievements'] = [a['id'] for a in added]
    manifest.update(client_modified=True, client_integration_verified=True,
                    achievements_activated=True, client_released=False)
    write('narrative/mystery_manifest.json', manifest)
    print('Promoted 25 tested quests and 25 achievements; no database or Git publication performed.')


if __name__ == '__main__':
    main()
