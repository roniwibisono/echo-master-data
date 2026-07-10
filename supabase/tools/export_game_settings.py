#!/usr/bin/env python3
"""Publish game settings from Supabase back to the CDN game_settings.json.
    export SUPABASE_URL=... SUPABASE_SERVICE_KEY=...   (or SUPABASE_ANON_KEY)
    python3 supabase/tools/export_game_settings.py
"""
import json, os, sys, urllib.request

COLS = ['key','category','value','default_value','value_type','min_value','max_value',
        'hot_reloadable','requires_client_version','enabled','description','sort_order']

def main():
    try:
        base = os.environ['SUPABASE_URL'].rstrip('/')
        key = os.environ.get('SUPABASE_SERVICE_KEY') or os.environ['SUPABASE_ANON_KEY']
    except KeyError as e:
        sys.exit(f'Missing env var: {e}.')
    req = urllib.request.Request(
        f'{base}/rest/v1/game_settings?select=*&order=sort_order.asc',
        headers={'apikey': key, 'Authorization': f'Bearer {key}', 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        rows = json.loads(r.read())
    rows.sort(key=lambda x: x.get('sort_order', 0))
    settings = [{c: row.get(c) for c in COLS} for row in rows]
    out = {'meta': {'domain': 'game_settings', 'count': len(settings)}, 'settings': settings}
    json.dump(out, open(os.path.join(os.getcwd(), 'game_settings.json'), 'w'),
              indent=2, ensure_ascii=False)
    print(f'Exported {len(settings)} settings -> game_settings.json')

if __name__ == '__main__':
    main()
