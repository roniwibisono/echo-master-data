#!/usr/bin/env python3
"""Publish raid events from Supabase back to raid_boss_event.json (CDN).
    export SUPABASE_URL=... SUPABASE_SERVICE_KEY=...
    python3 supabase/tools/export_raids.py
"""
import json, os, sys, urllib.request

ORDER = ['raid_id','name','region','min_level','recommended_party_size',
         'max_player','spawn_time_ends','time_limit','boss_monster_id',
         'raid_type','max_entry','entry_requirements','spawn_monster_id',
         'phases','clear_rewards']

def main():
    try:
        base = os.environ['SUPABASE_URL'].rstrip('/')
        key = os.environ.get('SUPABASE_SERVICE_KEY') or os.environ['SUPABASE_ANON_KEY']
    except KeyError as e:
        sys.exit(f'Missing env var: {e}.')
    req = urllib.request.Request(
        f'{base}/rest/v1/raid_events?select=*&order=sort_order.asc',
        headers={'apikey': key, 'Authorization': f'Bearer {key}', 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        rows = json.loads(r.read())
    raids = [{k: row.get(k) for k in ORDER} for row in rows]
    root = os.getcwd()
    path = os.path.join(root, 'raid_boss_event.json')
    wrapper = {}
    if os.path.exists(path):
        ex = json.load(open(path))
        if isinstance(ex, dict):
            wrapper = {k: v for k, v in ex.items() if k != 'raids'}
    wrapper['raids'] = raids
    json.dump(wrapper, open(path, 'w'), indent=2, ensure_ascii=False)
    print(f'Exported {len(raids)} raid events -> raid_boss_event.json')

if __name__ == '__main__':
    main()
