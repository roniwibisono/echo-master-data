#!/usr/bin/env python3
"""Explicit equipment subtype migration; --check makes no changes."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPLICIT = {
    'wpn_iron_sword': 'WEAPON_SWORD',
    'wpn_void_blade': 'WEAPON_SWORD',
    'wpn_bronze_dagger': 'WEAPON_DAGGER',
    'wpn_steel_broadsword': 'WEAPON_SWORD',
    'wpn_apprentice_staff': 'WEAPON_STAFF',
    'wpn_rusty_sword': 'WEAPON_SWORD',
    'wpn_hunter_dagger': 'WEAPON_DAGGER',
    'wpn_training_spear': 'WEAPON_SPEAR',
    'wpn_scrap_axe': 'WEAPON_AXE',
    'forge_master_greatsword': 'WEAPON_GREATSWORD',
    'rusted_plasma_pistol': 'WEAPON_PISTOL',
    'acc_ring_of_vitality': 'ACCESSORY_RING',
    'acc_hunters_amulet': 'ACCESSORY_AMULET',
    'ring_minor_focus': 'ACCESSORY_RING',
    'ring_hunter_band': 'ACCESSORY_RING',
    'amulet_aethel_fragment': 'ACCESSORY_AMULET',
    'belt_adventurer_belt': 'ACCESSORY_BELT',
    'acc_dummy_bracelet': 'ACCESSORY_BRACELET',
    'ring_of_destruct': 'ACCESSORY_RING',
    'ring_of_destruct_r': 'ACCESSORY_RING',
    'expanse_conqueror_ring': 'ACCESSORY_RING',
    'blessing_ring': 'ACCESSORY_RING',
    'blessing_bracelet': 'ACCESSORY_BRACELET',
    'mq_relic_unlisted_right_to_remain': 'ACCESSORY_RING',
    'mq_relic_muster_warning_not_oath': 'ACCESSORY_BRACELET',
    'mq_relic_zero_port_without_lie': 'ACCESSORY_RING',
    'mq_relic_quiet_silence_kept': 'ACCESSORY_PENDANT',
    'mq_relic_armistice_unwritten_witness': 'ACCESSORY_RING',
}
for level in [1] + list(range(5, 101, 5)):
    EXPLICIT[f'wpn_t{level:03}_weapon1'] = 'WEAPON_SWORD'
    EXPLICIT[f'acc1_t{level:03}_accessory1'] = 'ACCESSORY_RING'
    EXPLICIT[f'acc2_t{level:03}_accessory2'] = 'ACCESSORY_AMULET'


def migrate(data):
    count = 0
    if isinstance(data, dict):
        item_id = data.get('id')
        old = data.get('type')
        if old in ('WEAPON', 'ACCESSORY'):
            if item_id not in EXPLICIT:
                raise ValueError(f'Unclassified equipment: {item_id}')
            new = EXPLICIT[item_id]
            if new.split('_', 1)[0] != old:
                raise ValueError(f'Category mismatch: {item_id}')
            data['type'] = new
            count += 1
        elif item_id in EXPLICIT and old is not None and old != EXPLICIT[item_id]:
            raise ValueError(f'Unexpected type for {item_id}: {old}')
        for value in data.values():
            count += migrate(value)
    elif isinstance(data, list):
        for value in data:
            count += migrate(value)
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    total = 0
    # Leave historical audit reports and activation snapshots untouched.
    for name in ('item_list.json', 'narrative/mystery_manifest.json'):
        path = ROOT / name
        data = json.loads(path.read_text())
        count = migrate(data)
        if count and args.check:
            raise SystemExit(f'{name}: {count} items need migration')
        if count:
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
        total += count
    print(f'PASS: {len(EXPLICIT)} explicit equipment mappings; {total} records updated.')


if __name__ == '__main__':
    main()
