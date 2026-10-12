#!/usr/bin/env python3
"""Audit/deduplicate skills using the client's first-occurrence precedence.

Only duplicate copies are removed. Their complete definitions are archived.
The generated seed preserves existing order and skips unchanged live rows.
"""
import argparse
import collections
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def audit(skills, classes):
    first, indices, duplicates, errors = {}, {}, [], []
    class_ids = {c['id'] for c in classes}
    references = {sid for c in classes for sid in c['learnable_skill_ids']}
    legacy = []
    for index, row in enumerate(skills):
        sid = row.get('id')
        if not isinstance(sid, str) or not sid.strip():
            errors.append({'index': index, 'issue': 'missing_id'})
            continue
        if sid in first:
            duplicates.append({'id': sid, 'kept_index': indices[sid],
                               'removed_index': index,
                               'identical': first[sid] == row,
                               'removed_definition': row})
            continue
        first[sid], indices[sid] = row, index
        if row.get('type') not in ('Active', 'Passive', 'Ultimate'):
            errors.append({'id': sid, 'issue': 'invalid_type'})
        if not isinstance(row.get('damage_formula'), str):
            errors.append({'id': sid, 'issue': 'invalid_damage_formula'})
        for field in ('name', 'source_type', 'effect',
                      'skill_description', 'skill_shape'):
            if not isinstance(row.get(field), str) or not row[field].strip():
                errors.append({'id': sid, 'issue': 'invalid_' + field})
        for field in ('mp_cost', 'range', 'aoe_radius', 'projectile_speed',
                      'cooldown_seconds'):
            value = row.get(field)
            if type(value) not in (int, float) or value < 0:
                errors.append({'id': sid, 'issue': 'invalid_' + field})
        if type(row.get('mp_cost')) is not int:
            errors.append({'id': sid, 'issue': 'mp_cost_not_integer'})
        for field in ('stat_modifiers', 'periodic_effects', 'control_effects',
                      'special_effects'):
            if field in row and not isinstance(row[field], list):
                errors.append({'id': sid, 'issue': 'invalid_' + field})
        for cid in (row.get('usage_requirements') or {}).get('allowed_classes', []):
            if cid == 'all':
                continue
            if cid == 'mst_beastmaster' and 'mst_beastExpert' in class_ids:
                legacy.append({'skill_id': sid, 'legacy_class': cid,
                               'client_alias': 'mst_beastExpert'})
            elif cid not in class_ids:
                errors.append({'id': sid, 'issue': 'missing_allowed_class', 'class': cid})
    missing = sorted(references - first.keys())
    errors.extend({'id': sid, 'issue': 'missing_class_skill'} for sid in missing)
    return first, duplicates, {
        'input_entries': len(skills), 'unique_ids': len(first),
        'duplicate_copies': len(duplicates),
        'duplicate_ids': len({d['id'] for d in duplicates}),
        'conflicting_copies': sum(not d['identical'] for d in duplicates),
        'identical_copies': sum(d['identical'] for d in duplicates),
        'precedence': 'first occurrence, matching SkillRepository',
        'class_count': len(classes), 'class_skill_ids': len(references),
        'missing_class_skills': missing,
        'types': dict(collections.Counter(r['type'] for r in first.values())),
        'empty_formulas': sum(r.get('damage_formula') == '' for r in first.values()),
        'legacy_class_aliases': legacy, 'errors': errors,
    }


def build_seed(rows):
    path = ROOT / 'supabase/tools/import_skills.py'
    spec = importlib.util.spec_from_file_location('skills_import', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    columns = module.COLS
    content_columns = [c for c in columns if c not in ('id', 'sort_order')]
    updates = ', '.join(f'{c}=excluded.{c}' for c in content_columns)
    distinct = (f'row({", ".join("skills." + c for c in content_columns)}) '
                f'is distinct from row({", ".join("excluded." + c for c in content_columns)})')
    statements = ['-- Audited canonical skills; existing order preserved; unchanged rows skipped.',
                  'begin;']
    values = [f'({", ".join(module.rowvals(row, index))})'
              for index, row in enumerate(rows)]
    statements.append(f'insert into public.skills ({", ".join(columns)})\nvalues\n'
                      + ',\n'.join(values)
                      + f'\non conflict (id) do update set {updates}\nwhere {distinct};')
    statements.append('commit;')
    return '\n'.join(statements) + '\n'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--deduplicate', action='store_true')
    args = parser.parse_args()
    source = ROOT / 'skill_list.json'
    original = source.read_bytes()
    skills = json.loads(original)
    classes = json.loads((ROOT / 'class_list.json').read_text())
    first, duplicates, report = audit(skills, classes)
    report['source_sha256_before'] = hashlib.sha256(original).hexdigest()
    if report['errors']:
        raise SystemExit(json.dumps(report, indent=2))
    destination = ROOT / 'narrative/skill_audit_20261008'
    destination.mkdir(parents=True, exist_ok=True)
    backup = destination / 'skill_list.before.json'
    archive = destination / 'removed_duplicates.json'
    if args.deduplicate and duplicates:
        if backup.exists() or archive.exists():
            raise SystemExit('Archive exists; refusing to overwrite the recovery snapshot')
        backup.write_bytes(original)
        archive.write_text(json.dumps(duplicates, ensure_ascii=False, indent=2) + '\n')
        source.write_text(json.dumps(list(first.values()), ensure_ascii=False, indent=2) + '\n')
    report['canonical_definitions_unchanged'] = True
    report['source_sha256_after'] = hashlib.sha256(source.read_bytes()).hexdigest()
    report['deduplicated'] = args.deduplicate
    report['archive'] = str(archive) if archive.exists() else None
    seed = ROOT / 'supabase/seed/skills_audited_20261008.sql'
    seed.write_text(build_seed(list(first.values())))
    report['seed'] = str(seed)
    (destination / 'catalog-audit.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
