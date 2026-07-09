#!/usr/bin/env python3
"""
validate_data.py — Master-data consistency guard for Echo of Xylos.

Prevents the class of bug where a quest can never progress because the item it
asks the player to collect cannot drop in the quest's own region, or where a
region's spawn table is polluted with monsters that belong to other regions.

Run before committing any change to world_map_v4.json / monster_master.json /
quest_*.json:

    python3 validate_data.py

Exit code:
    0  -> no ERRORS (warnings may still be printed)
    1  -> at least one ERROR (a quest is unfinishable / broken data)

Note on quest regions
----------------------
Quest `collect` progress is NOT region-gated at runtime: the game fires the
collect event whenever the item enters the inventory, anywhere. So a quest is
only truly *unfinishable* when its target item has NO source in the entire game
(no monster drops it and it is not a resource node in any region). "Item farmed
elsewhere, turned in at a safe-zone hub" is a valid design, so a region mismatch
is a WARNING, not an error.

Checks
------
ERROR   A `collect` target item that has NO source anywhere — no monster drops
        it and no region lists it as a resource node. Such a quest can never be
        completed. (Distinct from the fq_shard_006 "Swamp Remembers" bug, which
        was obtainable-but-near-impossible: the sole dropper had a tiny spawn
        weight and the region was flooded with wrong-region monsters. That class
        is caught by the spawn-pollution WARN below plus manual weight review.)
WARN    A `collect` target item is obtainable in the game but NOT in the quest's
        own region (player must farm it elsewhere first).
WARN    A region's spawn table references a monster whose `spawn_location` does
        not include that region (spawn pollution / wrong-region monster).
"""
import json
import glob
import sys
from collections import defaultdict


def norm(s):
    return str(s).upper().strip().replace(' ', '_')


def load(path):
    with open(path) as f:
        return json.load(f)


def collect_nodes(obj, key, out):
    if isinstance(obj, dict):
        if key in obj and obj.get('id'):
            out.append(obj)
        for v in obj.values():
            collect_nodes(v, key, out)
    elif isinstance(obj, list):
        for v in obj:
            collect_nodes(v, key, out)


def collect_quests(obj, out):
    if isinstance(obj, dict):
        if 'objectives' in obj and isinstance(obj['objectives'], list):
            out.append(obj)
        for v in obj.values():
            collect_quests(v, out)
    elif isinstance(obj, list):
        for v in obj:
            collect_quests(v, out)


def main():
    wm = load('world_map_v4.json')
    monsters = load('monster_master.json')['monsters']
    by_id = {m['monster_id']: m for m in monsters}

    # monster_id -> normalized spawn_location set
    monster_locs = {
        m['monster_id']: {norm(l) for l in (m.get('spawn_location') or [])}
        for m in monsters
    }
    # item -> monster ids that drop it
    item_droppers = defaultdict(set)
    for m in monsters:
        for d in (m.get('drop_item') or []):
            item_droppers[norm(d['itemId'])].add(m['monster_id'])
    # every item that appears as a resource node anywhere (gatherable in-game)
    all_resource_items = set()

    # region -> spawn ids / resource nodes / keys
    region_nodes = []
    collect_nodes(wm, 'monster_spawns', region_nodes)
    region_spawn = {}
    region_keys = {}
    region_res = defaultdict(set)
    for r in region_nodes:
        rid = r['id']
        region_spawn[norm(rid)] = [s['monster_id'] for s in r['monster_spawns']]
        region_keys[norm(rid)] = {norm(rid), norm(r.get('name', ''))}
        for n in (r.get('resource_nodes') or []):
            region_res[norm(rid)].add(norm(n.get('node_id', '')))
            all_resource_items.add(norm(n.get('node_id', '')))

    errors, warns = [], []

    # WARN: spawn pollution
    for r in region_nodes:
        keys = {norm(r['id']), norm(r.get('name', ''))}
        for s in r['monster_spawns']:
            mid = s['monster_id']
            if mid not in by_id:
                warns.append(f"[{r['id']}] spawn references missing monster_id {mid}")
                continue
            locs = monster_locs.get(mid, set())
            if locs and not (keys & locs):
                warns.append(
                    f"[{r['id']}] spawn {mid} ({by_id[mid]['code']}) is tagged to "
                    f"{'/'.join(sorted(locs))}, not this region")

    # ERROR: unobtainable collect items
    quests = []
    for qf in glob.glob('quest_*.json'):
        qq = []
        collect_quests(load(qf), qq)
        for q in qq:
            quests.append((qf, q))

    for qf, q in quests:
        region = norm(q.get('region', ''))
        for ob in q['objectives']:
            if ob.get('type') != 'collect':
                continue
            item = norm(ob.get('target', ''))
            droppers = item_droppers.get(item, set())
            exists_anywhere = bool(droppers) or item in all_resource_items
            if not exists_anywhere:
                # Truly unfinishable — the item has no source in the whole game.
                errors.append(
                    f"[{qf}:{q.get('id')}] '{ob.get('target')}' x{ob.get('count')} "
                    f"(region {q.get('region')}) has NO source anywhere — quest "
                    f"can never be completed")
                continue
            # Obtainable somewhere; is it obtainable in the quest's own region?
            in_region = bool(set(region_spawn.get(region, [])) & droppers) \
                or item in region_res.get(region, set())
            if not in_region:
                where = sorted({by_id[mid]['code'] for mid in droppers})
                warns.append(
                    f"[{qf}:{q.get('id')}] region {q.get('region')} needs "
                    f"'{ob.get('target')}' but it is farmed elsewhere "
                    f"({'drops from ' + ', '.join(where[:3]) if where else 'resource node'})")

    for w in warns:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"\n{len(warns)} warning(s), {len(errors)} error(s)")
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
