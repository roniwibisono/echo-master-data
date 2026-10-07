#!/usr/bin/env python3
"""Verify generated monster SQL rows and that the audit log matches the source."""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    spec = importlib.util.spec_from_file_location("monster_import", ROOT / "supabase/tools/import_monsters.py")
    importer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(importer)
    monsters = json.loads((ROOT / "monster_master.json").read_text())["monsters"]
    chunks = sorted((ROOT / "supabase/seed").glob("monsters_seed_part*.sql"))
    files = {"full seed": (ROOT / "supabase/seed/monsters_seed.sql").read_text(),
             "chunks": "\n".join(p.read_text() for p in chunks),
             "bundle": (ROOT / "supabase/apply_all.sql").read_text()}
    for order, monster in enumerate(monsters):
        expected = "values (" + ", ".join(importer.rowvals(monster, order)) + ")"
        for label, text in files.items():
            if text.count(expected) != 1:
                raise ValueError(f"{monster['code']}: missing/duplicate/different row in {label}")
    changes = json.loads((ROOT / "monster_audit_20261008_changes.json").read_text())["changes"]
    by_id = {m["monster_id"]: m for m in monsters}
    for change in changes:
        if not change["new"] and not set(change["fields"]) <= {"spawn_location", "ai_pattern", "drop_item"}:
            raise ValueError("Audit unexpectedly changed existing monster stats/economy")
        for field, pair in change["fields"].items():
            if by_id[change["monster_id"]].get(field) != pair["after"]:
                raise ValueError(f"Audit log drift: {change['code']}.{field}")
    print(f"{len(monsters)} complete SQL rows verified in full seed, {len(chunks)} chunks and bundle; {len(changes)} audit records match source.")


if __name__ == "__main__":
    main()
