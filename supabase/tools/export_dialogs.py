#!/usr/bin/env python3
"""Publish dialogs from Supabase back to the two CDN files.
  dialog_quests.json      -> {dialogues:[...quest dialogs...]}
  dialog_tree_master.json -> [{dialogues:[...generic dialogs...]}]  (client flattens)
    export SUPABASE_URL=... SUPABASE_SERVICE_KEY=...  (or SUPABASE_ANON_KEY)
    python3 supabase/tools/export_dialogs.py
"""
import json, os, sys, urllib.request

def to_dialog(row):
    d = {'dialog_id': row.get('dialog_id')}
    if row.get('quest_id') is not None:
        d['quest_id'] = row['quest_id']
    d['npc_id'] = row.get('npc_id')
    d['start_node'] = row.get('start_node')
    d['nodes'] = row.get('nodes') or []
    return d

def main():
    try:
        base = os.environ['SUPABASE_URL'].rstrip('/')
        key = os.environ.get('SUPABASE_SERVICE_KEY') or os.environ['SUPABASE_ANON_KEY']
    except KeyError as e:
        sys.exit(f'Missing env var: {e}.')
    rows, off = [], 0
    while True:
        req = urllib.request.Request(
            f'{base}/rest/v1/dialogs?select=*&order=source_file.asc,sort_order.asc&limit=1000&offset={off}',
            headers={'apikey': key, 'Authorization': f'Bearer {key}', 'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=30) as r:
            batch = json.loads(r.read())
        rows += batch
        if len(batch) < 1000:
            break
        off += 1000
    root = os.getcwd()
    groups = {}
    for row in rows:
        groups.setdefault(row.get('source_file') or 'dialog_quests.json', []).append(row)
    for fn, rws in groups.items():
        rws.sort(key=lambda r: r.get('sort_order', 0))
        dialogues = [to_dialog(r) for r in rws]
        path = os.path.join(root, fn)
        if fn == 'dialog_tree_master.json':
            payload = [{'dialogues': dialogues}]   # single wrapper; client flattens
        else:
            payload = {'dialogues': dialogues}
        json.dump(payload, open(path, 'w'), indent=2, ensure_ascii=False)
        print(f'  wrote {fn}  ({len(dialogues)} dialogs)')
    print(f'Exported {len(rows)} dialogs.')

if __name__ == '__main__':
    main()
