#!/usr/bin/env python3
"""Publish skills from Supabase back to skill_list.json (top-level list).
    export SUPABASE_URL=... SUPABASE_SERVICE_KEY=...  (or SUPABASE_ANON_KEY)
    python3 supabase/tools/export_skills.py
"""
import json, os, sys, urllib.request

# canonical field order; OPTIONAL fields are omitted when NULL to match source
ORDER = ['id','name','type','source_type','mp_cost','damage_formula','effect',
         'stat_modifiers','periodic_effects','control_effects','special_effects',
         'usage_requirements','target_attack','target_effect','skill_description',
         'skill_shape','range','aoe_radius','projectile_speed','cooldown_seconds',
         'arc_angle_degrees']
OPTIONAL = {'special_effects','usage_requirements','target_attack','target_effect','arc_angle_degrees'}
FLOATS = {'range','aoe_radius','projectile_speed','cooldown_seconds','arc_angle_degrees'}

def main():
    try:
        base = os.environ['SUPABASE_URL'].rstrip('/')
        key = os.environ.get('SUPABASE_SERVICE_KEY') or os.environ['SUPABASE_ANON_KEY']
    except KeyError as e:
        sys.exit(f'Missing env var: {e}.')
    req = urllib.request.Request(
        f'{base}/rest/v1/skills?select=*&order=sort_order.asc&limit=2000',
        headers={'apikey': key, 'Authorization': f'Bearer {key}', 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        rows = json.loads(r.read())
    out = []
    for row in rows:
        sk = {}
        for k in ORDER:
            v = row.get(k)
            if k in OPTIONAL and v is None:
                continue  # omit absent optional field
            if k in FLOATS and v is not None:
                v = float(v)
            sk[k] = v
        out.append(sk)
    path = os.path.join(os.getcwd(), 'skill_list.json')
    json.dump(out, open(path, 'w'), indent=2, ensure_ascii=False)
    print(f'Exported {len(out)} skills -> skill_list.json')

if __name__ == '__main__':
    main()
