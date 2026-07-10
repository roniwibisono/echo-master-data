#!/usr/bin/env python3
"""Publish monsters from Supabase back to monster_master.json ({monsters:[...]}).
    export SUPABASE_URL=... SUPABASE_SERVICE_KEY=...  (or SUPABASE_ANON_KEY)
    python3 supabase/tools/export_monsters.py
"""
import json, os, sys, urllib.request

ORDER = ['monster_id','code','name','rank','level','race_code','element',
         'spawn_monster_id','spawn_location','base_stats','scaling','critical_rate',
         'critical_damage','resistances','weaknesses','status_immunity','ai_pattern',
         'skill_set','exp_reward','currency_reward','crd_reward','guild_point',
         'reputation_point','hunting_point','drop_item','special_reward']
NUM = {'critical_rate', 'critical_damage'}

def main():
    try:
        base = os.environ['SUPABASE_URL'].rstrip('/')
        key = os.environ.get('SUPABASE_SERVICE_KEY') or os.environ['SUPABASE_ANON_KEY']
    except KeyError as e:
        sys.exit(f'Missing env var: {e}.')
    req = urllib.request.Request(
        f'{base}/rest/v1/monsters?select=*&order=sort_order.asc&limit=2000',
        headers={'apikey': key, 'Authorization': f'Bearer {key}', 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        rows = json.loads(r.read())
    out = []
    for row in rows:
        m = {}
        for k in ORDER:
            v = row.get(k)
            if k in NUM and v is not None:
                fv = float(v)
                v = int(fv) if fv.is_integer() else fv
            m[k] = v
        out.append(m)
    path = os.path.join(os.getcwd(), 'monster_master.json')
    wrapper = {}
    if os.path.exists(path):
        ex = json.load(open(path))
        if isinstance(ex, dict):
            wrapper = {k: v for k, v in ex.items() if k != 'monsters'}
    wrapper['monsters'] = out
    json.dump(wrapper, open(path, 'w'), indent=2, ensure_ascii=False)
    print(f'Exported {len(out)} monsters -> monster_master.json')

if __name__ == '__main__':
    main()
