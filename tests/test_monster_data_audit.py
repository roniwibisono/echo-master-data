import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import audit_monster_data as audit

ROOT = Path(__file__).resolve().parents[1]
FILES = ["monster_master.json", "skill_list.json", "item_list.json", "world_map_v4.json",
         "dungeon_db.json", "raid_boss_event.json", "biome_monster_mapping.json"]


class MonsterAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = {name: json.loads((ROOT / name).read_text(encoding="utf-8")) for name in FILES}

    def setUp(self):
        self.data = copy.deepcopy(self.source)

    def errors(self):
        with patch.object(audit, "load", side_effect=self.data.__getitem__):
            return audit.audit()["errors"]

    def test_current_data(self):
        self.assertEqual([], self.errors())

    def test_missing_drop_is_detected(self):
        self.data["monster_master.json"]["monsters"][0]["drop_item"][0]["itemId"] = "missing_item"
        self.assertTrue(any("Undefined item: missing_item" in e["message"] for e in self.errors()))

    def test_phase_skill_must_be_equipped(self):
        self.data["monster_master.json"]["monsters"][0]["ai_pattern"]["phase_1"]["skills"] = ["missing_skill"]
        self.assertTrue(any("Not an equipped active skill" in e["message"] for e in self.errors()))

    def test_crit_probability_is_bounded(self):
        self.data["monster_master.json"]["monsters"][0]["critical_rate"] = 20
        self.assertTrue(any(e["field"] == "critical_rate" for e in self.errors()))

    def test_drop_chance_is_bounded(self):
        self.data["monster_master.json"]["monsters"][0]["drop_item"][0]["chance"] = 20
        self.assertTrue(any(e["field"] == "drop_item.chance" for e in self.errors()))

    def test_spawn_missing_monster_is_detected(self):
        self.data["world_map_v4.json"]["nodes"][1]["monster_spawns"][0]["monster_id"] = -9
        self.assertTrue(any("Undefined monster: -9" in e["message"] for e in self.errors()))

    def test_biome_weights_are_normalized(self):
        row = next(x for x in self.data["biome_monster_mapping.json"]["mappings"] if x["spawn_weights"])
        row["spawn_weights"][0] += 1
        self.assertTrue(any("Probabilities must sum to one" in e["message"] for e in self.errors()))

    def test_phase_thresholds_descend(self):
        self.data["monster_master.json"]["monsters"][0]["ai_pattern"]["phase_2"]["hp_threshold"] = 1
        self.assertTrue(any("HP thresholds must strictly descend" in e["message"] for e in self.errors()))


if __name__ == "__main__":
    unittest.main()
