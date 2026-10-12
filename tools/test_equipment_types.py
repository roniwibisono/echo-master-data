import copy
import json
import unittest

import migrate_equipment_types as migration


class EquipmentTypesTest(unittest.TestCase):
    def test_each_explicit_mapping_changes_only_type(self):
        for item_id, new_type in migration.EXPLICIT.items():
            old = {'id': item_id, 'type': new_type.split('_', 1)[0],
                   'equipment_slots': ['MAIN_HAND'], 'stats_bonus': {'atk': 12},
                   'special_effects': [], 'buy_price': 100}
            record = copy.deepcopy(old)
            self.assertEqual(migration.migrate(record), 1)
            self.assertEqual(record['type'], new_type)
            record['type'] = old['type']
            self.assertEqual(record, old)

    def test_migration_is_idempotent(self):
        record = {'id': 'wpn_iron_sword', 'type': 'WEAPON'}
        migration.migrate(record)
        self.assertEqual(migration.migrate(record), 0)

    def test_unknown_equipment_is_not_guessed(self):
        with self.assertRaisesRegex(ValueError, 'Unclassified'):
            migration.migrate({'id': 'unknown', 'name': 'Sword', 'type': 'WEAPON'})

    def test_offhand_and_non_equipment_unchanged(self):
        for category in ('OFFHAND', 'MATERIAL', 'SKILL_MEMORY', 'QUEST'):
            record = {'id': 'other', 'type': category}
            self.assertEqual(migration.migrate(record), 0)
            self.assertEqual(record['type'], category)

    def test_canonical_catalog_has_no_generic_weapon_or_accessory(self):
        records = json.loads((migration.ROOT / 'item_list.json').read_text())['items']
        self.assertFalse(any(x['type'] in ('WEAPON', 'ACCESSORY') for x in records))
        lookup = {x['id']: x for x in records}
        for item_id, category in migration.EXPLICIT.items():
            self.assertEqual(lookup[item_id]['type'], category)


if __name__ == '__main__':
    unittest.main()
