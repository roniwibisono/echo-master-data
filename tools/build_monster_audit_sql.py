#!/usr/bin/env python3
"""Build only this audit's field changes, never unrelated local monster edits."""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def literal(value):
    return "'" + value.replace("'", "''") + "'"


def main():
    spec = importlib.util.spec_from_file_location("monster_import", ROOT / "supabase/tools/import_monsters.py")
    importer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(importer)
    log = json.loads((ROOT / "monster_audit_20261008_changes.json").read_text())
    monsters = json.loads((ROOT / "monster_master.json").read_text())["monsters"]
    by_id = {m["monster_id"]: (i, m) for i, m in enumerate(monsters)}
    lines = ["-- Content-only monster audit, 2026-10-08. No schema or player-save changes.",
             "-- Includes only fields recorded by this audit, preserving other content edits.", "begin;"]
    for change in log["changes"]:
        mid = change["monster_id"]
        if change["new"]:
            order, monster = by_id[mid]
            values = importer.rowvals(monster, order)
            assignments = ", ".join(f"{c}=excluded.{c}" for c in importer.COLS if c != "monster_id")
            lines.append(f"insert into public.monsters ({', '.join(importer.COLS)})\nvalues ({', '.join(values)})\n"
                         f"on conflict (monster_id) do update set {assignments};")
        else:
            assignments = []
            for column, pair in sorted(change["fields"].items()):
                if column not in importer.JSONB:
                    raise ValueError(f"Unexpected scalar update: {column}")
                assignments.append(f"{column}={literal(json.dumps(pair['after'], ensure_ascii=False))}::jsonb")
            lines.append(f"update public.monsters set {', '.join(assignments)} where monster_id={mid};")
    ids = ','.join(str(c['monster_id']) for c in log['changes'])
    lines += ["do $monster_audit$", "begin",
              f" if (select count(*) from public.monsters where monster_id in ({ids})) <> {len(log['changes'])} then",
              "  raise exception 'Monster audit: target records missing'; end if;",
              " if exists (select 1 from public.monsters m cross join lateral jsonb_array_elements(m.drop_item || m.special_reward) d",
              "  left join public.items i on i.id=d->>'itemId' where i.id is null) then",
              "  raise exception 'Monster audit: undefined reward item'; end if;",
              " if exists (select 1 from public.monsters m cross join lateral jsonb_array_elements(m.skill_set->'active_skills') r",
              "  left join public.skills s on s.id=r->>'skill_id' where s.id is null or s.type<>'Active') then",
              "  raise exception 'Monster audit: invalid active skill'; end if;",
              " if exists (select 1 from public.monsters m cross join lateral jsonb_array_elements(m.skill_set->'passive_skills') r",
              "  left join public.skills s on s.id=r->>'skill_id' where s.id is null or s.type<>'Passive') then",
              "  raise exception 'Monster audit: invalid passive skill'; end if;",
              "end;", "$monster_audit$;", "commit;", "", "-- Verification: all three columns below must be zero.",
              "select", " (select count(*) from public.monsters m cross join lateral jsonb_array_elements(m.drop_item || m.special_reward) d",
              "  left join public.items i on i.id=d->>'itemId' where i.id is null) as undefined_items,",
              " (select count(*) from public.monsters m cross join lateral jsonb_array_elements(m.skill_set->'active_skills') r",
              "  left join public.skills s on s.id=r->>'skill_id' where s.id is null or s.type<>'Active') as invalid_active_skills,",
              " (select count(*) from public.monsters m cross join lateral jsonb_array_elements(m.skill_set->'passive_skills') r",
              "  left join public.skills s on s.id=r->>'skill_id' where s.id is null or s.type<>'Passive') as invalid_passive_skills;", ""]
    path = ROOT / "supabase/seed/monster_audit_20261008.sql"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {path.name}: {len(log['changes'])} scoped monster changes.")


if __name__ == "__main__":
    main()
