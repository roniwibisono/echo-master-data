#!/usr/bin/env python3
"""Publish allies from Supabase back to ally_list.json ({meta, allies:[...]}).
    export SUPABASE_URL=... SUPABASE_SERVICE_KEY=...  (or SUPABASE_ANON_KEY)
    python3 supabase/tools/export_allies.py
"""
import json, os, sys, urllib.request

# canonical field order (passive/active re-wrapped as {skill_id})
ORDER = ['ally_id','code','name','rarity','role','brief_background_story',
         'place_of_origin','faction_affinity','base_stats','passive_skill',
         'active_skill','recruit_cost','level_cap','pvp_scale','conclave_points']

def main():
    try:
        base = os.environ['SUPABASE_URL'].rstrip('/')
        key = os.environ.get('SUPABASE_SERVICE_KEY') or os.environ['SUPABASE_ANON_KEY']
    except KeyError as e:
        sys.exit(f'Missing env var: {e}.')
    req = urllib.request.Request(
        f'{base}/rest/v1/allies?select=*&order=sort_order.asc&limit=500',
        headers={'apikey': key, 'Authorization': f'Bearer {key}', 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        rows = json.loads(r.read())
    out = []
    for row in rows:
        a = {}
        for k in ORDER:
            if k == 'passive_skill':
                a[k] = {'skill_id': row.get('passive_skill_id')}
            elif k == 'active_skill':
                a[k] = {'skill_id': row.get('active_skill_id')}
            elif k == 'pvp_scale':
                a[k] = float(row['pvp_scale']) if row.get('pvp_scale') is not None else None
            else:
                a[k] = row.get(k)
        out.append(a)
    path = os.path.join(os.getcwd(), 'ally_list.json')
    wrapper = {}
    if os.path.exists(path):
        ex = json.load(open(path))
        if isinstance(ex, dict):
            wrapper = {k: v for k, v in ex.items() if k != 'allies'}
    wrapper['allies'] = out
    json.dump(wrapper, open(path, 'w'), indent=2, ensure_ascii=False)
    print(f'Exported {len(out)} allies -> ally_list.json')

if __name__ == '__main__':
    main()
