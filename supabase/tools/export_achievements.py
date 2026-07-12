#!/usr/bin/env python3
"""Publish achievement definitions from Supabase back to CDN achievements.json.
    export SUPABASE_URL=... SUPABASE_SERVICE_KEY=...  (or SUPABASE_ANON_KEY)
    python3 supabase/tools/export_achievements.py
"""
import json, os, sys, urllib.request

COLS = ['id','name','description','category','metric','operator','threshold','tier',
        'reward_title','reward_rubies','hidden','sort_order']

def main():
    try:
        base = os.environ['SUPABASE_URL'].rstrip('/')
        key = os.environ.get('SUPABASE_SERVICE_KEY') or os.environ['SUPABASE_ANON_KEY']
    except KeyError as e:
        sys.exit(f'Missing env var: {e}.')
    req = urllib.request.Request(
        f'{base}/rest/v1/achievements?select=*&order=sort_order.asc',
        headers={'apikey': key, 'Authorization': f'Bearer {key}', 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        rows = json.loads(r.read())
    rows.sort(key=lambda x: x.get('sort_order', 0))
    out = {'meta': {'domain': 'achievements', 'count': len(rows)},
           'achievements': [{c: row.get(c) for c in COLS} for row in rows]}
    json.dump(out, open(os.path.join(os.getcwd(), 'achievements.json'), 'w'),
              indent=2, ensure_ascii=False)
    print(f'Exported {len(rows)} achievements -> achievements.json')

if __name__ == '__main__':
    main()
