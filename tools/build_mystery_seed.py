#!/usr/bin/env python3
"""Build a scoped, content-only seed; never seed pending achievements or player data."""

import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from audit_mystery_data import audit


def importer(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f'supabase/tools/{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    manifest_path = ROOT / 'narrative/mystery_manifest.json'
    manifest = json.loads(manifest_path.read_text())
    keys = {'dialogs': 'dialog_id', 'npcs': 'npc_id', 'monsters': 'monster_id'}
    manifest['ids'] = {k: [r[keys.get(k, 'id')] for r in rows] for k, rows in manifest['records'].items()}
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')
    errors = audit()['errors']
    if errors:
        raise ValueError(errors)
    data = manifest['records']
    im, mm, nm, qm, dm = [importer(n) for n in ['import_items', 'import_monsters', 'import_npcs', 'import_quests', 'import_dialogs']]
    def load(name):
        return json.loads((ROOT / name).read_text())
    lines = ['-- Xylos Unwritten Witness: 35 items, 5 monsters, 15 NPCs, 25 quests, 40 dialogs.',
        ('-- Content applied to Supabase. Client integration is still required before feature release.'
         if manifest.get('live_applied') else
         '-- Prepared content only. NOT applied. Client integration is required before publishing.'),
        '-- No schema, player-save, achievement, title-table, or world-map DML.', 'begin;']
    counts = {}
    def insert(table, columns, values, key):
        assignments = ', '.join(f'{c}=excluded.{c}' for c in columns if c != key)
        lines.append(f"insert into public.{table} ({', '.join(columns)})\nvalues ({', '.join(values)})\n"
                     f'on conflict ({key}) do update set {assignments};')
        counts[table] = counts.get(table, 0) + 1
    item_order = {r['id']: i for i, r in enumerate(load('item_list.json')['items'])}
    for r in data['items']:
        values = [im.i(r.get(c)) if isinstance(r.get(c), int) and not isinstance(r.get(c), bool) else im.s(r.get(c)) for c in im.SCALARS]
        values += [im.jb(r.get(c) if r.get(c) is not None else ({} if c == 'stats_bonus' else [])) for c in im.JSONB]
        insert('items', im.COLS, values + [str(item_order[r['id']])], 'id')
    monster_order = {r['monster_id']: i for i, r in enumerate(load('monster_master.json')['monsters'])}
    for r in data['monsters']:
        insert('monsters', mm.COLS, mm.rowvals(r, monster_order[r['monster_id']]), 'monster_id')
    npc_order = {r['npc_id']: i for i, r in enumerate(load('npc_list.json'))}
    for r in data['npcs']:
        insert('npcs', nm.COLS, [nm.s(r.get(c)) for c in nm.TEXT] + [nm.jb(r.get(c)) for c in nm.JSONB] + [str(npc_order[r['npc_id']])], 'npc_id')
    for i, r in enumerate(data['quests']):
        values = [qm.s(r.get(c)) for c in qm.COLS[:7]]
        values += [qm.jb(r.get(c)) for c in qm.COLS[7:11]]
        values += [qm.b(r.get('repeatable')), qm.b(r.get('daily')), qm.s(r.get('quest_chain_next')),
                   qm.b(r.get('popup')), qm.s(r.get('popup_trigger')), qm.i(r.get('popup_level')),
                   qm.s(r.get('popup_prerequisite')), qm.s('quest_mysteries.json'), str(i)]
        insert('quests', qm.COLS, values, 'id')
    dialog_order = {r['dialog_id']: i for i, r in enumerate([r for b in load('dialog_tree_master.json') for r in b.get('dialogues', [])] + load('dialog_quests.json')['dialogues'])}
    for r in data['dialogs']:
        source = 'dialog_quests.json' if r.get('quest_id') else 'dialog_tree_master.json'
        values = [dm.s(r.get(c)) for c in dm.COLS[:4]] + [dm.jb(r['nodes']), dm.s(source), str(dialog_order[r['dialog_id']])]
        insert('dialogs', dm.COLS, values, 'dialog_id')
    ids = ','.join(str(mid) for mid in manifest['ids']['monsters'])
    qids = ','.join(qm.s(qid) for qid in manifest['ids']['quests'])
    lines += ['do $mystery_pack$', 'begin',
        f" if (select count(*) from public.quests where id in ({qids})) <> 25 then raise exception 'Mystery quests missing'; end if;",
        f" if exists (select 1 from public.monsters m cross join lateral jsonb_array_elements(m.drop_item) d left join public.items i on i.id=d->>'itemId' where m.monster_id in ({ids}) and i.id is null) then raise exception 'Mystery clue item missing'; end if;",
        f" if exists (select 1 from public.monsters m cross join lateral jsonb_array_elements(m.skill_set->'active_skills') r left join public.skills s on s.id=r->>'skill_id' where m.monster_id in ({ids}) and (s.id is null or s.type<>'Active')) then raise exception 'Mystery active skill invalid'; end if;",
        f" if exists (select 1 from public.monsters m cross join lateral jsonb_array_elements(m.skill_set->'passive_skills') r left join public.skills s on s.id=r->>'skill_id' where m.monster_id in ({ids}) and (s.id is null or s.type<>'Passive')) then raise exception 'Mystery passive skill invalid'; end if;",
        f" if exists (select 1 from public.quests q left join public.npcs n on n.npc_id=q.quest_giver->>'npc_id' where q.id in ({qids}) and n.npc_id is null) then raise exception 'Mystery giver missing'; end if;",
        f" if exists (select 1 from public.quests q cross join lateral jsonb_array_elements(q.rewards->'items') r left join public.items i on i.id=r->>'item_id' where q.id in ({qids}) and i.id is null) then raise exception 'Mystery reward missing'; end if;",
        'end;', '$mystery_pack$;', 'commit;', '']
    (ROOT / 'supabase/seed/mystery_content_20261008.sql').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps(counts))


if __name__ == '__main__':
    main()
