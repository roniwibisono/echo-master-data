#!/usr/bin/env python3
"""Check every scoped SQL row against the full seed, chunks, and fresh-install bundle."""

from collections import Counter
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def main():
    delta = (ROOT / 'supabase/seed/mystery_content_20261008.sql').read_text()
    activation = (ROOT / 'supabase/seed/mystery_activation_20261008.sql').read_text()
    bundle = (ROOT / 'supabase/apply_all.sql').read_text()
    expected = {'items': 35, 'monsters': 5, 'npcs': 15, 'quests': 25, 'dialogs': 40, 'achievements': 25}
    counts = Counter()
    rows = re.findall(r'^insert into public\.(\w+) \([^\n]+\)\n(values \([^\n]+\))\n', delta + '\n' + activation, re.MULTILINE)
    for table, row in rows:
        if table not in expected:
            raise ValueError(f'Unexpected delta table: {table}')
        full = (ROOT / f'supabase/seed/{table}_seed.sql').read_text()
        chunks = sorted((ROOT / 'supabase/seed').glob(f'{table}_seed_part*.sql'))
        sources = {'full seed': full, 'bundle': bundle}
        if chunks:
            sources['chunks'] = '\n'.join(p.read_text() for p in chunks)
        for label, text in sources.items():
            if text.count(row) != 1:
                raise ValueError(f'{table}: row differs or is missing in {label}')
        counts[table] += 1
    if dict(counts) != expected:
        raise ValueError(f'Unexpected delta record counts: {dict(counts)}')
    if re.search(r'^(delete|alter|create|truncate|drop|update)\s', delta, re.MULTILINE | re.IGNORECASE):
        raise ValueError('Unexpected destructive or unrelated SQL operation')
    if re.search(r'^(delete|alter|create|truncate|drop)\s', activation, re.MULTILINE | re.IGNORECASE):
        raise ValueError('Unexpected destructive activation SQL operation')
    updates = re.findall(r'^update [^\n]+', activation, re.MULTILINE)
    if len(updates) != 1 or not updates[0].startswith('update public.quests set requirements=jsonb_set('):
        raise ValueError('Activation must only update scoped quest release metadata')
    print(f'{sum(counts.values())} scoped SQL records match full seeds, chunks, and bundle.')


if __name__ == '__main__':
    main()
