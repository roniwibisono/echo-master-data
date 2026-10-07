#!/usr/bin/env python3
"""Build a content-only skill delta against an audited live Supabase snapshot."""

import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def sql_string(value):
    return "'" + value.replace("'", "''") + "'"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    args = parser.parse_args()
    skills = json.loads((ROOT / "skill_list.json").read_text(encoding="utf-8"))
    baseline = {row["id"]: row for row in json.loads(args.baseline.read_text(encoding="utf-8"))}
    spec = importlib.util.spec_from_file_location("skill_import", ROOT / "supabase/tools/import_skills.py")
    importer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(importer)
    lines = ["-- Content-only combat audit delta, 2026-10-08.",
             "-- Skills were compared with the live catalogue before building this file.",
             "-- Existing ally templates, player saves and unrelated monster fields are untouched.",
             "begin;"]
    inserts = updates = 0
    for order, row in enumerate(skills):
        values = importer.rowvals(row, order)
        if row["id"] not in baseline:
            assignments = ', '.join(f'{col}=excluded.{col}' for col in importer.COLS if col != 'id')
            lines.append(f"insert into public.skills ({', '.join(importer.COLS)})\n"
                         f"values ({', '.join(values)})\non conflict (id) do update set {assignments};")
            inserts += 1
            continue
        assignments = []
        for column, value in zip(importer.COLS, values):
            key = column.strip('"')
            if key in ("id", "sort_order"):
                continue
            normalized = row.get(key)
            if key in importer.JSONB_REQ:
                normalized = normalized or []
            if baseline[row["id"]].get(key) != normalized:
                assignments.append(f"{column}={value}")
        if assignments:
            lines.append(f"update public.skills set {', '.join(assignments)} where id={sql_string(row['id'])};")
            updates += 1
    lines.extend([
        "update public.monsters set skill_set = jsonb_set(skill_set, '{passive_skills,0,skill_id}', '\"spore_cloud_aura\"'::jsonb)\n"
        "where monster_id=5004 and skill_set #>> '{passive_skills,0,skill_id}' = 'spore_cloud';",
        "do $combat_audit$\nbegin\n"
        "  if exists (select 1 from public.skills where nullif(btrim(skill_description), '') is null) then\n"
        "    raise exception 'Combat audit: skill descriptions are still empty';\n  end if;\n"
        "  if not exists (select 1 from public.skills where id='spore_cloud_aura' and type='Passive') then\n"
        "    raise exception 'Combat audit: missing Spore Cloud passive';\n  end if;\n"
        "  if not exists (select 1 from public.monsters where monster_id=5004 and skill_set #>> '{passive_skills,0,skill_id}'='spore_cloud_aura') then\n"
        "    raise exception 'Combat audit: Wild Mushroom passive reference not updated';\n  end if;\n"
        "  if exists (select 1 from public.allies a left join public.skills p on p.id=a.passive_skill_id\n"
        "    left join public.skills s on s.id=a.active_skill_id\n"
        "    where p.id is null or s.id is null or p.type <> 'Passive' or s.type <> 'Active') then\n"
        "    raise exception 'Combat audit: invalid ally skill references';\n  end if;\n"
        "end;\n$combat_audit$;", "commit;", "",
    ])
    patch = ROOT / "supabase/seed/combat_audit_20261008.sql"
    patch.write_text("\n".join(lines), encoding="utf-8")
    changes = json.loads((ROOT / "combat_data_changes.json").read_text(encoding="utf-8"))["changes"]
    record = next(row for row in changes if row["domain"] == "monsters" and row["id"] == 5004)
    field = record["fields"]["skill_set"]
    before = sql_string(json.dumps(field["before"], ensure_ascii=False)) + "::jsonb"
    after = sql_string(json.dumps(field["after"], ensure_ascii=False)) + "::jsonb"
    for name in ["monsters_seed.sql", "monsters_seed_part01.sql"]:
        path = ROOT / "supabase/seed" / name
        text = path.read_text(encoding="utf-8")
        if before in text:
            if text.count(before) != 1:
                raise ValueError(f"{name}: ambiguous monster skill payload")
            path.write_text(text.replace(before, after), encoding="utf-8")
        elif after not in text:
            raise ValueError(f"{name}: neither previous nor updated monster payload found")
    print(f"Wrote {patch.name}: {updates} skill updates, {inserts} insert, one scoped monster reference fix.")


if __name__ == "__main__":
    main()
