#!/usr/bin/env python3
"""Publish npcs from Supabase back to npc_list.json (top-level list).
    export SUPABASE_URL=... SUPABASE_SERVICE_KEY=...  (or SUPABASE_ANON_KEY)
    python3 supabase/tools/export_npcs.py
"""
import json, os, sys, urllib.request

ORDER = ['npc_id','name','title','role','faction','location','region_id','description',
         'personality','greeting','available_services','actions','shop_inventory',
         'dialogue_tree','buy_currency','rest_currency','sell_note','quest_category',
         'reward_currency']
OPTIONAL = {'personality','shop_inventory','buy_currency','rest_currency','sell_note',
            'quest_category','reward_currency'}

def main():
    try:
        base = os.environ['SUPABASE_URL'].rstrip('/')
        key = os.environ.get('SUPABASE_SERVICE_KEY') or os.environ['SUPABASE_ANON_KEY']
    except KeyError as e:
        sys.exit(f'Missing env var: {e}.')
    req = urllib.request.Request(
        f'{base}/rest/v1/npcs?select=*&order=sort_order.asc&limit=1000',
        headers={'apikey': key, 'Authorization': f'Bearer {key}', 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        rows = json.loads(r.read())
    out = []
    for row in rows:
        n = {}
        for k in ORDER:
            v = row.get(k)
            if k in OPTIONAL and v is None:
                continue
            n[k] = v
        out.append(n)
    path = os.path.join(os.getcwd(), 'npc_list.json')
    json.dump(out, open(path, 'w'), indent=2, ensure_ascii=False)
    print(f'Exported {len(out)} npcs -> npc_list.json')

if __name__ == '__main__':
    main()
