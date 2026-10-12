import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import audit_mystery_data as audit

ROOT = Path(__file__).resolve().parents[1]
FILES = ['quest_mysteries.json', 'narrative/mystery_design.json', 'narrative/mystery_manifest.json',
    'world_map_v4.json', 'monster_master.json', 'npc_list.json', 'item_list.json', 'title_master.json',
    'dialog_quests.json', 'dialog_tree_master.json', 'skill_list.json', 'achievements.json',
    'narrative/mystery_achievements_pending.json', 'narrative/mystery_baseline.json']


class MysteryAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = {name: json.loads((ROOT / name).read_text()) for name in FILES}

    def setUp(self):
        self.data = copy.deepcopy(self.source)

    def errors(self):
        with patch.object(audit, 'load', side_effect=self.data.__getitem__):
            return audit.audit()['errors']

    def test_complete_pack(self):
        self.assertEqual([], self.errors())

    def test_deployment_status_uses_manifest(self):
        for applied in (False, True):
            self.data['narrative/mystery_manifest.json']['live_applied'] = applied
            with patch.object(audit, 'load', side_effect=self.data.__getitem__):
                self.assertEqual(applied, audit.audit()['live_applied'])

    def test_cycle(self):
        q = self.data['quest_mysteries.json']['quests']
        q[0]['requirements']['required_quests'] = [q[1]['id']]
        self.assertTrue(any('cycle' in e for e in self.errors()))

    def test_missing_local_clue_source(self):
        self.data['monster_master.json']['monsters'][-5]['drop_item'] = []
        self.assertTrue(any('guaranteed local source' in e for e in self.errors()))

    def test_missing_prop(self):
        self.data['world_map_v4.json']['nodes'][-5]['npc_ids'] = []
        self.assertTrue(any('inaccessible interaction' in e for e in self.errors()))

    def test_title_power_inflation(self):
        self.data['title_master.json']['titles'][-1]['stat_bonus'] = {'atk': 100}
        self.assertTrue(any('stacking title power' in e for e in self.errors()))

    def test_unimplemented_achievement_not_activated(self):
        self.data['narrative/mystery_manifest.json']['client_integration_verified'] = False
        self.data['achievements.json']['achievements'].append(self.data['narrative/mystery_achievements_pending.json']['achievements'][0])
        self.assertTrue(any('Unimplemented achievement activated' in e for e in self.errors()))

    def test_existing_user_record_preserved(self):
        self.data['item_list.json']['items'][0]['name'] = 'Unexpected rewrite'
        self.assertTrue(any('Pre-existing record changed' in e for e in self.errors()))

    def test_capstone_requires_all_arcs(self):
        self.data['quest_mysteries.json']['quests'][-1]['requirements']['required_quests'] = []
        self.assertTrue(any('Capstone does not require' in e for e in self.errors()))

    def test_route_reachability(self):
        self.data['world_map_v4.json']['routes'] = [r for r in self.data['world_map_v4.json']['routes'] if r['to'] != 'UNLISTED_WARD']
        self.assertTrue(any('unreachable' in e for e in self.errors()))


if __name__ == '__main__':
    unittest.main()
