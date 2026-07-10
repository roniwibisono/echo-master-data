#!/usr/bin/env python3
"""Publish items from Supabase back to item_list.json (CDN).
    export SUPABASE_URL=... SUPABASE_SERVICE_KEY=...  (or SUPABASE_ANON_KEY)
    python3 supabase/tools/export_items.py
"""
import json, os, sys, urllib.request

ORDER = ['id','name','description','type','rarity','level_requirement',
         'equipment_slots','stats_bonus','special_effects','buy_price',
         'sell_price','sell_value','max_stack','icon_image']

def fetch(base, key, offset):
    req = urllib.request.Request(
        f'{base}/rest/v1/items?select=*&order=sort_order.asc&limit=1000&offset={offset}',
        headers={'apikey': key, 'Authorization': f'Bearer {key}', 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def main():
    try:
        base = os.environ['SUPABASE_URL'].rstrip('/')
        key = os.environ.get('SUPABASE_SERVICE_KEY') or os.environ['SUPABASE_ANON_KEY']
    except KeyError as e:
        sys.exit(f'Missing env var: {e}.')
    rows, off = [], 0
    while True:  # paginate (>1000 rows)
        batch = fetch(base, key, off)
        rows += batch
        if len(batch) < 1000:
            break
        off += 1000
    out = []
    for r in rows:
        it = {}
        for k in ORDER:
            v = r.get(k)
            if v is None and k in ('sell_value',):
                continue  # omit optional field when absent
            it[k] = v
        out.append(it)
    root = os.getcwd()
    path = os.path.join(root, 'item_list.json')
    wrapper = {}
    if os.path.exists(path):
        ex = json.load(open(path))
        if isinstance(ex, dict):
            wrapper = {k: v for k, v in ex.items() if k != 'items'}
    wrapper['items'] = out
    json.dump(wrapper, open(path, 'w'), indent=2, ensure_ascii=False)
    print(f'Exported {len(out)} items -> item_list.json')

if __name__ == '__main__':
    main()
