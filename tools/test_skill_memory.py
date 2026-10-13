import copy
import unittest

import build_skill_memory as builder


class SkillMemoryDataTest(unittest.TestCase):
    def setUp(self):
        self.pack = builder.build()
        self.files = builder.expected_files(self.pack)

    def test_valid_pack(self):
        builder.validate(self.pack, self.files)
    def test_dummy_only_costs_one_potion_and_no_currency(self):
        recipe = next(r for r in self.pack['recipes'] if r['recipe_id'] == 'rcp_mem_dummy_skill')
        self.assertEqual(recipe['ingredients'], [{'item_id': 'con_small_hp_cell', 'quantity': 1}])
        self.assertEqual(recipe['crafting_cost'], 0)
        self.assertEqual(recipe['craftable_by_npcs'], [builder.NPC])

    def test_required_weapon_families_are_craftable(self):
        equipment = {i['id']: i for i in self.pack['training_equipment']}
        families = {i['type'] for i in equipment.values()}
        self.assertEqual(families, {'WEAPON_KNUCKLE', 'WEAPON_ORB', 'WEAPON_GRIMOIRE', 'WEAPON_POLEARM', 'WEAPON_SHIELD'})
        self.assertEqual(len(self.pack['equipment_recipes']), 5)
        for recipe in self.pack['equipment_recipes']:
            self.assertIn(recipe['result']['item_id'], equipment)
            self.assertEqual(recipe['craftable_by_npcs'], ['npc_master_blacksmith'])

    def test_all_sequential_training_steps(self):
        quests = self.pack['training_quests']
        self.assertEqual(len(quests), 189)
        for profile in self.pack['profiles']:
            steps = [q for q in quests if q['skill_id'] == profile['skill_id']]
            self.assertEqual([q['to_level'] for q in steps], list(range(2, 11)))
            for q in steps:
                self.assertEqual(q['from_level'], q['to_level'] - 1)
                dummy = profile['skill_id'] == 'sk_mem_dummy_skill'
                self.assertEqual(q['required_uses'], 1 if dummy else 5 * q['to_level'] * profile['tier'])
                self.assertEqual(q['required_victories'], 1 if dummy else q['to_level'] + profile['tier'])

    def test_training_cannot_skip_levels(self):
        self.pack['training_quests'][0]['from_level'] = 0
        with self.assertRaisesRegex(ValueError, 'sequential'):
            builder.validate(self.pack, self.files)

    def test_training_cannot_lower_objectives(self):
        self.pack['training_quests'][0]['required_uses'] = 0
        with self.assertRaisesRegex(ValueError, 'requirements'):
            builder.validate(self.pack, self.files)

    def test_regeneration_is_not_twenty_percent_hp(self):
        heal = next(s for s in self.pack['skills'] if s['name'] == 'Echo Mend')
        self.assertEqual(heal['periodic_effects'][0]['value'], 3)
        self.assertEqual(heal['periodic_effects'][0]['scale'], 0)

    def test_dot_uses_caster_attack(self):
        dots = [s for s in self.pack['skills'] if s['name'] in ('Crescent Slash', 'Venom Edge', 'Ember Knuckle')]
        for skill in dots:
            self.assertEqual(skill['periodic_effects'][0]['type'], 'percent_atk')
            self.assertEqual(skill['periodic_effects'][0]['scale'], 0)

    def test_duplicate_skill_rejected(self):
        self.files['skill_list.json'].append(copy.deepcopy(self.files['skill_list.json'][0]))
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            builder.validate(self.pack, self.files)

    def test_broken_weapon_rejected(self):
        self.pack['profiles'][0]['weapon_family'] = 'Unknown'
        with self.assertRaisesRegex(ValueError, 'weapon'):
            builder.validate(self.pack, self.files)

    def test_broken_memory_link_rejected(self):
        self.pack['items'][0]['special_effects'][0]['skill_id'] = 'missing'
        with self.assertRaisesRegex(ValueError, 'mismatch'):
            builder.validate(self.pack, self.files)

    def test_missing_ingredient_rejected(self):
        self.pack['recipes'][0]['ingredients'][0]['item_id'] = 'missing'
        with self.assertRaises(KeyError):
            builder.validate(self.pack, self.files)

    def test_vendor_arbitrage_rejected(self):
        self.pack['items'][0]['sell_price'] = 10000000
        with self.assertRaisesRegex(ValueError, 'arbitrage'):
            builder.validate(self.pack, self.files)

    def test_unimplemented_dialog_action_rejected(self):
        self.pack['dialogue']['nodes'][0]['options'][0]['action'] = 'start_training'
        with self.assertRaisesRegex(ValueError, 'Unimplemented'):
            builder.validate(self.pack, self.files)

    def test_slot_and_mastery_contract(self):
        contract = builder.contract()
        self.assertEqual(contract['base_slots_per_learner'], 2)
        self.assertEqual(contract['max_skill_level'], 10)
        self.assertEqual(contract['progression']['level_potency_multipliers'][-1], 1.54)
        self.assertFalse(contract['memory_skills_can_grant_slots'])

    def test_merge_preserves_non_pack_data(self):
        record = {'id': 'legacy', 'custom_field': 'untouched'}
        self.assertEqual(builder.merge([record], self.pack['skills'], 'id')[0], record)


if __name__ == '__main__':
    unittest.main()
