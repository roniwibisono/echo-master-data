#!/usr/bin/env python3
"""Emit only verified achievement rows and mystery release metadata updates."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / 'narrative/mystery_manifest.json').read_text())
    if not manifest.get('client_integration_verified') or not manifest.get('achievements_activated'):
        raise ValueError('Client metric bridge must be verified first')
    source = (ROOT / 'supabase/seed/achievements_seed.sql').read_text()
    ids = set(manifest['ids']['achievements'])
    rows = []
    for match in re.finditer(r"^insert into public\.achievements [^\n]+\nvalues \('([^']+)'[^\n]+\non conflict [^\n]+;", source, re.MULTILINE):
        if match.group(1) in ids:
            rows.append(match.group())
    if len(rows) != len(ids) or len(ids) != 25:
        raise ValueError('Expected exactly 25 scoped achievements')
    quote = lambda value: "'" + value.replace("'", "''") + "'"
    quest_ids = ', '.join(map(quote, manifest['ids']['quests']))
    achievement_ids = ', '.join(map(quote, manifest['ids']['achievements']))
    lines = ['-- Verified mystery client activation: 25 achievements + 25 quest status fields.',
             '-- No player saves, schema changes, or unrelated content updates.', 'begin;']
    lines += rows
    lines += [f"update public.quests set requirements=jsonb_set(requirements, '{{mystery,release_status}}', '\"client_playable_pending_release\"'::jsonb, false) where id in ({quest_ids});",
              'do $mystery_activation$', 'begin',
              f" if (select count(*) from public.quests where id in ({quest_ids}) and requirements->'mystery'->>'release_status'='client_playable_pending_release') <> 25 then raise exception 'Mystery metadata missing'; end if;",
              f" if (select count(*) from public.achievements where id in ({achievement_ids})) <> 25 then raise exception 'Mystery achievements missing'; end if;",
              f" if exists (select 1 from public.achievements a left join public.quests q on q.id=replace(a.metric, 'mystery_completed.', '') where a.id in ({achievement_ids}) and (q.id is null or a.reward_rubies<>0 or not a.hidden or a.threshold<>1)) then raise exception 'Invalid mystery achievement'; end if;",
              'end;', '$mystery_activation$;', 'commit;', '']
    (ROOT / 'supabase/seed/mystery_activation_20261008.sql').write_text('\n'.join(lines))
    print('Prepared 25 achievement upserts and 25 scoped quest metadata updates.')


if __name__ == '__main__':
    main()
