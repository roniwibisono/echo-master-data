#!/usr/bin/env python3
"""Ensure generated skill SQL exactly represents the audited source rows."""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    spec = importlib.util.spec_from_file_location("skill_import", ROOT / "supabase/tools/import_skills.py")
    importer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(importer)
    skills = json.loads((ROOT / "skill_list.json").read_text(encoding="utf-8"))
    seed_dir = ROOT / "supabase/seed"
    full = (seed_dir / "skills_seed.sql").read_text(encoding="utf-8")
    chunks = list(sorted(seed_dir.glob("skills_seed_part*.sql")))
    chunk_text = "\n".join(path.read_text(encoding="utf-8") for path in chunks)
    bundle = (ROOT / "supabase/apply_all.sql").read_text(encoding="utf-8")
    for order, skill in enumerate(skills):
        expected = f"values ({', '.join(importer.rowvals(skill, order))})\n"
        for label, text in [("full", full), ("chunks", chunk_text), ("bundle", bundle)]:
            if text.count(expected) != 1:
                raise ValueError(f"{label}: skill {skill['id']} row missing, different, or duplicated")
    for name in ["monsters_seed.sql", "monsters_seed_part01.sql"]:
        text = (seed_dir / name).read_text(encoding="utf-8")
        if '"passive_skills": [{"skill_id": "spore_cloud_aura"}]' not in text:
            raise ValueError(f"{name}: missing canonical Wild Mushroom passive")
    print(f"{len(skills)} complete SQL skill rows verified in full seed, {len(chunks)} chunks, and apply_all.sql.")


if __name__ == "__main__":
    main()
