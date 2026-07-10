#!/usr/bin/env python3
"""Publish quests from Supabase back to the CDN JSON files.

The `public.quests` table is the source of truth; this regenerates the exact
quest_*.json files the Flutter client already reads (grouped by source_file,
in sort_order), so NO client change is needed. Run after editing quests in
Supabase, then commit + push the repo.

Usage (from repo root):
    export SUPABASE_URL="https://<ref>.supabase.co"
    export SUPABASE_SERVICE_KEY="<service_role_key>"   # or anon key (read is public)
    python3 supabase/tools/export_quests.py

Then: git add quest_*.json && git commit && git push   (and bump the app's
CDN refresh tag so clients pull the update).
"""
import json, os, sys, urllib.request

# quest field order for clean, stable output (matches the original files)
FIELD_ORDER = ['id', 'title', 'type', 'rank', 'faction', 'region', 'description',
               'quest_giver', 'requirements', 'objectives', 'rewards',
               'repeatable', 'daily', 'quest_chain_next']
POPUP_FIELDS = ['popup', 'popup_trigger', 'popup_level', 'popup_prerequisite']

def fetch_all():
    base = os.environ['SUPABASE_URL'].rstrip('/')
    key = os.environ.get('SUPABASE_SERVICE_KEY') or os.environ['SUPABASE_ANON_KEY']
    url = f'{base}/rest/v1/quests?select=*&order=source_file.asc,sort_order.asc'
    req = urllib.request.Request(url, headers={
        'apikey': key, 'Authorization': f'Bearer {key}',
        'Accept': 'application/json', 'Range-Unit': 'items', 'Range': '0-9999',
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def to_quest(row):
    q = {}
    for f in FIELD_ORDER:
        q[f] = row.get(f)
    # popup fields only when this is a popup quest (keeps non-popup quests clean)
    if row.get('popup'):
        for f in POPUP_FIELDS:
            q[f] = row.get(f)
    return q

def main():
    try:
        rows = fetch_all()
    except KeyError as e:
        sys.exit(f'Missing env var: {e}. Set SUPABASE_URL and SUPABASE_SERVICE_KEY.')
    by_file = {}
    for row in rows:
        by_file.setdefault(row.get('source_file') or 'quest_list.json', []).append(row)

    root = os.getcwd()
    for fname, rws in by_file.items():
        rws.sort(key=lambda r: r.get('sort_order', 0))
        quests = [to_quest(r) for r in rws]
        # preserve any non-quests top-level keys (_meta / meta) already in the file
        wrapper = {}
        path = os.path.join(root, fname)
        if os.path.exists(path):
            existing = json.load(open(path))
            if isinstance(existing, dict):
                wrapper = {k: v for k, v in existing.items() if k != 'quests'}
        wrapper['quests'] = quests
        json.dump(wrapper, open(path, 'w'), indent=2, ensure_ascii=False)
        print(f'  wrote {fname}  ({len(quests)} quests)')
    print(f'Exported {len(rows)} quests to {len(by_file)} files.')

if __name__ == '__main__':
    main()
