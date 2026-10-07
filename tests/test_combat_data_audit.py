import copy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import mock_open, patch

import audit_combat_data as audit

ROOT = Path(__file__).resolve().parents[1]
FILES = ["class_list.json", "skill_list.json", "ally_list.json", "npc_list.json",
         "monster_master.json", "master_race.json"]


class CombatDataAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = {name: json.loads((ROOT / name).read_text(encoding="utf-8")) for name in FILES}

    def setUp(self):
        self.data = copy.deepcopy(self.source)

    def errors(self):
        with patch.object(audit, "load", side_effect=self.data.__getitem__):
            return audit.audit()["errors"]

    def test_current_catalogue_has_no_errors(self):
        self.assertEqual([], self.errors())

    def test_missing_class_skill_is_rejected(self):
        self.data["class_list.json"][0]["learnable_skill_ids"][0] = "missing_skill"
        self.assertTrue(any("missing skill missing_skill" in x for x in self.errors()))

    def test_wrong_ally_passive_type_is_rejected(self):
        ally = self.data["ally_list.json"]["allies"][0]
        ally["passive_skill"] = ally["active_skill"]
        self.assertTrue(any("passive_skill has wrong type/source" in x for x in self.errors()))

    def test_unaffordable_ally_active_is_rejected(self):
        ally = self.data["ally_list.json"]["allies"][0]
        active = next(s for s in self.data["skill_list.json"] if s["id"] == ally["active_skill"]["skill_id"])
        active["mp_cost"] = ally["base_stats"]["mp"] + 1
        self.assertTrue(any("unaffordable at recruitment" in x for x in self.errors()))

    def test_control_percentage_must_be_a_probability(self):
        skill = next(s for s in self.data["skill_list.json"] if s["control_effects"])
        skill["control_effects"][0]["chance"] = 20
        self.assertTrue(any("control chance exceeds 1" in x for x in self.errors()))

    def test_duplicate_heal_payload_is_rejected(self):
        skill = next(s for s in self.data["skill_list.json"] if s["id"] == "al4_57_act")
        skill["special_effects"].append(copy.deepcopy(skill["special_effects"][0]))
        self.assertTrue(any("duplicate special_effects" in x for x in self.errors()))

    def test_healer_requires_a_healing_payload(self):
        skill = next(s for s in self.data["skill_list.json"] if s["id"] == "al5_67_act")
        skill["special_effects"] = [{"type": "cleanse_debuff", "value": 1}]
        self.assertTrue(any("Healer active skill has no healing payload" in x for x in self.errors()))

    def test_formula_supports_def_and_multihit_average(self):
        self.assertEqual(170, audit.formula_value("ATK + DEF * 0.7"))
        self.assertAlmostEqual(185 / 3, audit.formula_value("40 + (ATK * 0.65 / 3)"))

    def test_formula_rejects_calls_and_division_by_zero(self):
        for formula in ["__import__('os')", "ATK / 0", "unknown_stat * 2"]:
            with self.subTest(formula=formula), self.assertRaises((ValueError, SyntaxError)):
                audit.formula_value(formula)

    def test_importer_rejects_bad_content_before_replacing_seeds(self):
        spec = importlib.util.spec_from_file_location("skill_import", ROOT / "supabase/tools/import_skills.py")
        importer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(importer)
        for field, value in [("skill_description", ""), ("effect", " "),
                             ("damage_formula", ["ATK", "ATK * 0.5"]),
                             ("mp_cost", 1.5), ("cooldown_seconds", float("nan"))]:
            skills = copy.deepcopy(self.data["skill_list.json"])
            skills[0][field] = value
            with self.subTest(field=field), patch.object(importer.json, "load", return_value=skills), \
                    patch("builtins.open", mock_open()) as files:
                with self.assertRaises(ValueError):
                    importer.main()
                self.assertEqual(1, files.call_count, "No seed files should be opened for writing")


if __name__ == "__main__":
    unittest.main()
