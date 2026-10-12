#!/usr/bin/env python3
"""Apply the reviewed item consolidation and generate a small Supabase delta.

Run once from the repository root. --check validates the resulting catalog.
SQL only changes master data; legacy item definitions remain for saved bags.
"""

import argparse
import copy
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'item_audit_20261008.json'
SQL = ROOT / 'supabase/seed/item_shop_cleanup_20261008.sql'

ALIASES = {
    'cns_health_potion_small': 'con_small_hp_cell',
    'potion_minor_healing': 'con_small_hp_cell',
    'minor_health_potion': 'con_small_hp_cell',
    'basic_hp_potion': 'con_small_hp_cell',
    'itm_minor_hp_potion': 'con_small_hp_cell',
    'cns_mana_potion_small': 'con_small_mp_cell',
    'potion_minor_mana': 'con_small_mp_cell',
    'itm_minor_mp_potion': 'con_small_mp_cell',
    'advanced_hp_potion': 'con_medium_hp_cell',
    'itm_hp_potion': 'con_medium_hp_cell',
    'itm_mp_potion': 'con_medium_mp_cell',
    'itm_greater_hp_potion': 'con_large_hp_cell',
    'itm_greater_mp_potion': 'con_large_mp_cell',
    'itm_full_heal_potion': 'con_full_recovery_pack',
    'con_revive_shard': 'itm_revive_shard',
    'storm_core': 'mat_storm_core',
    'iron_ore': 'mat_iron_ore',
    'crs_paradox_crystal': 'paradox_crystal',
    'scarab_shell': 'bio_scarab_shell',
    # Undefined IDs previously stocked by the four Pax Nexus shops.
    'potion_medium_healing': 'con_medium_hp_cell',
    'potion_medium_mana': 'con_medium_mp_cell',
    'potion_major_healing': 'con_large_hp_cell',
    'ration_field': 'con_nutrient_ration',
    'antidote_basic': 'con_antidote',
    'grenade_frag': 'con_scramble_grenade',
    'smoke_bomb': 'con_minor_stim_pack',
    'stim_combat': 'con_combat_stimulant',
    'armor_patch_basic': 'con_repair_patch',
    'repair_kit_field': 'con_repair_patch',
    'aethel_dust': 'mat_aethel_dust',
    'resonant_shard': 'crs_resonant_shard',
    'revival_shard': 'itm_revive_shard',
    'cleanse_vial': 'con_antidote',
    'mp_cell_small': 'con_small_mp_cell',
    'mp_cell_large': 'con_large_mp_cell',
    'mat_metal': 'scrap_metal',
}

SCALARS = ['id', 'name', 'type', 'rarity', 'level_requirement', 'buy_price',
           'sell_price', 'sell_value', 'max_stack', 'icon_image', 'description']
JSONB = ['equipment_slots', 'stats_bonus', 'special_effects']
COLS = SCALARS + JSONB + ['sort_order']
ACTIVE_FILES = [
    'shop_inventory.json', 'monster_master.json', 'crafting_recipes.json',
    'upgrade_recipes.json', 'biome_item_mapping.json', 'dungeon_db.json',
    'raid_boss_event.json', 'world_map.json', 'world_map_v4.json',
    'ally_list.json', 'npc_list.json', 'dialog_quests.json',
    'dialog_tree_master.json', 'achievements.json', 'game_settings.json',
] + [p.name for p in sorted(ROOT.glob('quest_*.json'))]


def load(name):
    return json.loads((ROOT / name).read_text())


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def replace_refs(value):
    if isinstance(value, str):
        return ALIASES.get(value, value)
    if isinstance(value, list):
        return [replace_refs(v) for v in value]
    if isinstance(value, dict):
        result = {}
        for key, val in value.items():
            key = ALIASES.get(key, key)
            val = replace_refs(val)
            if key in result:
                if isinstance(val, (int, float)) and isinstance(result[key], (int, float)):
                    result[key] += val
                elif result[key] != val:
                    raise ValueError(f'Conflicting merged reference: {key}')
            else:
                result[key] = val
        return result
    return value


def new_item(item_id, name, description, effects, price, level=1,
             rarity='COMMON', stack=99, icon=None, item_type='CONSUMABLE'):
    return {
        'id': item_id, 'name': name, 'description': description,
        'type': item_type, 'rarity': rarity, 'level_requirement': level,
        'equipment_slots': [], 'stats_bonus': {},
        'special_effects': [{'effect_id': k, 'value': v} for k, v in effects],
        'buy_price': price, 'sell_price': price // 4, 'max_stack': stack,
        'icon_image': icon,
    }


def additions():
    return [
        new_item('con_small_energy_cell', 'Small Energy Cell',
                 'A portable Aethel battery. Restores 25 exploration energy; excess energy is stored as overcharge.',
                 [('restore_energy', 25)], 80,
                 icon='icons/items/consumables/con_small_mp_cell.png'),
        new_item('con_large_energy_cell', 'Large Energy Cell',
                 'A high-capacity Aethel battery. Restores 60 exploration energy; excess energy is stored as overcharge.',
                 [('restore_energy', 60)], 210, 15, 'UNCOMMON', 50,
                 'icons/items/consumables/large_mp_cell.png'),
        new_item('con_field_recovery_pack', 'Field Recovery Pack',
                 'A dual-chamber field med-kit. Restores 120 HP and 60 MP in one use.',
                 [('restore_hp', 120), ('restore_mp', 60)], 100, 5, 'UNCOMMON', 50,
                 'icons/items/consumables/elite_recovery_pack.png'),
        new_item('con_full_recovery_pack', 'Full Recovery Pack',
                 'A premium nanomedical resupply kit. Restores 100% of maximum HP and MP. Does not revive defeated allies.',
                 [('restore_hp_percent', 100), ('restore_mp_percent', 100)],
                 5500, 40, 'EPIC', 10, 'icons/items/consumables/elite_recovery_pack.png'),
        new_item('cns_clean_water', 'Sterile Water',
                 'Purified field water used to assemble medical cells and nutrient supplies.',
                 [], 4, icon='icons/items/consumables/con_nutrient_ration.png',
                 item_type='MATERIAL', stack=999),
    ]


def stock(item_id, quantity=20, refresh=600):
    return {'item_id': item_id, 'stock': quantity, 'refresh_time': refresh,
            'price_modifier': 1.0}


def update_shops(data, by_id):
    extra = {
        'shop_general_01': [('consumables', stock('con_small_energy_cell')),
                            ('misc_materials', stock('cns_clean_water', 50, 300))],
        'shop_tech_01': [('consumables', stock('con_small_energy_cell', 15))],
        'shop_wasteland_01': [('survival_consumables', stock('con_small_energy_cell', 15)),
                              ('survival_consumables', stock('con_field_recovery_pack', 10))],
        'shop_medic_01': [('medical', stock('con_field_recovery_pack')),
                         ('medical_supplies', stock('itm_revival_elixir', 15, 1800)),
                         ('medical_supplies', stock('itm_phoenix_core', 5, 3600))],
        'shop_nexus_elara': [('consumables', stock('con_small_energy_cell')),
                            ('consumables', stock('con_field_recovery_pack', 15))],
        'shop_nexus_grath': [('consumables', stock('con_defense_tonic', 15))],
        'shop_nexus_mira_medical': [('consumables', stock('con_field_recovery_pack')),
                                   ('consumables', stock('itm_revival_elixir', 15, 1800)),
                                   ('consumables', stock('itm_phoenix_core', 5, 3600))],
        'shop_bazaar_advanced': [('general', stock('con_large_energy_cell', 15, 1800))],
        'shop_currency_omnicorp': [('omnicorp_consumables', stock('con_large_energy_cell', 15, 1800))],
        'shop_orbital_exchange': [('orbital_consumables', stock('con_full_recovery_pack', 5, 3600))],
        'shop_currency_custodian': [('rare_consumables', stock('con_full_recovery_pack', 5, 3600))],
    }
    removed = []
    for shop in data['shops']:
        for cat in shop['categories']:
            if cat['category'] == 'potions':
                cat['category'] = 'medical_cells'
        for category, row in extra.get(shop['id'], []):
            cat = next((c for c in shop['categories'] if c['category'] == category), None)
            if cat is None:
                cat = {'category': category, 'items': []}
                shop['categories'].append(cat)
            cat['items'].append(row)
        # Keep the first listing's stock rather than adding together alias stock.
        seen = set()
        for cat in shop['categories']:
            rows = []
            for row in cat['items']:
                item_id = row['item_id']
                if item_id in seen:
                    removed.append({'shop_id': shop['id'], 'item_id': item_id, 'reason': 'duplicate_listing'})
                    continue
                if (by_id[item_id].get('buy_price') or 0) <= 0:
                    removed.append({'shop_id': shop['id'], 'item_id': item_id, 'reason': 'loot_only_no_buy_price'})
                    continue
                seen.add(item_id)
                rows.append(row)
            cat['items'] = rows
        shop['categories'] = [c for c in shop['categories'] if c['items']]
    return removed


def quote(value):
    if value is None:
        return 'NULL'
    if isinstance(value, (int, float)):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def json_sql(value):
    return quote(json.dumps(value, ensure_ascii=False, separators=(',', ':'))) + '::jsonb'


def generate_sql(changed_items, shops, aliases):
    columns = ', '.join(COLS)
    updates = ', '.join(f'{c}=excluded.{c}' for c in COLS if c != 'id')
    lines = [
        '-- Item/shop audit 2026-10-08. Full transaction for psql; SQL Editor: use numbered parts.',
        '-- Transactional and repeatable. Master data only; no player saves are modified.',
        '-- Legacy IDs remain as compatible definitions, but are no longer stocked/rewarded.',
        'begin;',
        'create temporary table item_aliases (old_id text primary key, new_id text not null) on commit drop;',
        'insert into item_aliases values\n' + ',\n'.join(f'({quote(k)},{quote(v)})' for k, v in aliases.items()) + ';',
    ]
    for item in changed_items:
        vals = [quote(item.get(c)) for c in SCALARS]
        vals += [json_sql(item.get(c) or ({} if c == 'stats_bonus' else [])) for c in JSONB]
        vals.append(str(item['sort_order']))
        lines.append(f'insert into public.items ({columns}) values ({", ".join(vals)})\non conflict (id) do update set {updates};')
    item_statements = lines[6:].copy()
    legacy_cols = ', '.join('a.old_id' if c == 'id' else
                            "'Legacy ID for ' || a.new_id || '. ' || coalesce(i.description, '')" if c == 'description' else
                            '100000 + row_number() over (order by a.old_id)' if c == 'sort_order' else
                            'i.' + c for c in COLS)
    lines.append(f'insert into public.items ({columns})\nselect {legacy_cols}\nfrom item_aliases a join public.items i on i.id=a.new_id\non conflict (id) do update set {updates};')
    lines.append('''create or replace function pg_temp.replace_item_refs(value jsonb, aliases jsonb)
returns jsonb language plpgsql immutable as $$
declare kind text := jsonb_typeof(value); result jsonb; entry record; new_key text; new_value jsonb;
begin
  if kind = 'string' then
    return coalesce(aliases -> (value #>> '{}'), value);
  elsif kind = 'array' then
    select coalesce(jsonb_agg(pg_temp.replace_item_refs(v, aliases) order by ord), '[]'::jsonb)
    into result from jsonb_array_elements(value) with ordinality as x(v, ord);
    return result;
  elsif kind = 'object' then
    result := '{}'::jsonb;
    for entry in select key, val from jsonb_each(value) as x(key, val) loop
      new_key := coalesce(aliases ->> entry.key, entry.key);
      new_value := pg_temp.replace_item_refs(entry.val, aliases);
      if result ? new_key and result -> new_key is distinct from new_value then
        if jsonb_typeof(result -> new_key) = 'number' and jsonb_typeof(new_value) = 'number' then
          new_value := to_jsonb((result ->> new_key)::numeric + (new_value #>> '{}')::numeric);
        else
          raise exception 'Conflicting merged item reference: %', new_key;
        end if;
      elsif result ? new_key and jsonb_typeof(new_value) = 'number' then
        new_value := to_jsonb((result ->> new_key)::numeric + (new_value #>> '{}')::numeric);
      end if;
      result := result || jsonb_build_object(new_key, new_value);
    end loop;
    return result;
  end if;
  return value;
end $$;

-- Patch exact IDs in JSON only, preserving live quest/combat balancing.
do $$
declare aliases jsonb; col record;
begin
  select jsonb_object_agg(old_id, new_id) into aliases from item_aliases;
  for col in select table_name, column_name from information_schema.columns
    where table_schema='public' and data_type='jsonb'
    and table_name in ('quests','monsters','raid_events','allies','npcs','dialogs','skills','game_settings')
  loop
    execute format('update public.%I set %I=pg_temp.replace_item_refs(%I,$1) where %I is distinct from pg_temp.replace_item_refs(%I,$1)',
                   col.table_name, col.column_name, col.column_name, col.column_name, col.column_name)
    using aliases;
  end loop;
end $$;
''')
    reference_statements = lines[-2:].copy()
    shop_statements = shop_sql(shops)
    lines.extend(shop_statements)
    lines.append('commit;')
    SQL.write_text('\n\n'.join(lines) + '\n')
    parts = []
    batch = []
    for statement in item_statements:
        if batch and sum(len(s.encode()) for s in batch) + len(statement.encode()) > 24000:
            parts.append(batch)
            batch = []
        batch.append(statement)
    if batch:
        parts.append(batch)
    alias_setup = lines[4:6]
    parts.append(alias_setup + reference_statements)
    for n in range(0, len(shops), 10):
        parts.append(alias_setup + shop_sql(shops[n:n + 10]))
    for old in SQL.parent.glob(SQL.stem + '_part*.sql'):
        old.unlink()
    for n, statements in enumerate(parts, 1):
        content = f'-- Item/shop audit: part {n}/{len(parts)}. Run in order.\nbegin;\n\n' + '\n\n'.join(statements) + '\n\ncommit;\n'
        assert len(content.encode()) < 32000, 'SQL Editor part is too large'
        SQL.with_name(f'{SQL.stem}_part{n:02d}.sql').write_text(content)
    generate_verification(aliases)


def generate_verification(aliases):
    expected = [
        {'id': i['id'], 'effects': i['special_effects']} for i in additions()
    ]
    for item in load('item_list.json')['items']:
        if item['id'] in {'con_medium_hp_cell', 'con_medium_mp_cell',
                          'con_large_hp_cell', 'con_large_mp_cell',
                          'con_full_hp_cell', 'con_full_mp_cell'}:
            expected.append({'id': item['id'], 'effects': item['special_effects']})
    query = '''-- Read-only verification after ALL seven editor parts. Every issues count must be zero.
with aliases(old_id,new_id) as (values
''' + ',\n'.join(f'({quote(k)},{quote(v)})' for k, v in aliases.items()) + '''
), expected as (
  select * from jsonb_to_recordset(''' + json_sql(expected) + ''') as x(id text,effects jsonb)
), master_refs as (
  select to_jsonb(q)::text as data from public.quests q
  union all select to_jsonb(m)::text from public.monsters m
  union all select to_jsonb(r)::text from public.raid_events r
)
select 'retired_shop_references' as check_name, count(*) as issues
from public.shop_items s join aliases a on a.old_id=s.item_id
union all
select 'missing_or_unpriced_shop_items',count(*)
from public.shop_items s left join public.items i on i.id=s.item_id
where i.id is null or coalesce(i.buy_price,0)<=0
union all
select 'duplicate_shop_items',count(*)
from (select shop_id,item_id from public.shop_items group by shop_id,item_id having count(*)>1) d
union all
select 'missing_or_incorrect_recovery_items',count(*)
from expected e left join public.items i on i.id=e.id
where i.id is null or i.special_effects is distinct from e.effects
union all
select 'missing_or_incorrect_legacy_definitions',count(*)
from aliases a left join public.items old on old.id=a.old_id
left join public.items current on current.id=a.new_id
where old.id is null or current.id is null or old.name is distinct from current.name
or old.special_effects is distinct from current.special_effects
union all
select 'retired_quest_monster_raid_references',count(*)
from master_refs r where exists (
  select 1 from aliases a where position('"' || a.old_id || '"' in r.data)>0
);
'''
    SQL.with_name(SQL.stem + '_verify.sql').write_text(query)


def shop_sql(shops):
    lines = []
    rows = []
    for si, shop in shops:
        shop_cols = ['id', 'name', 'faction', 'buy_currency', 'description', 'sort_order']
        values = [quote(shop.get(c)) for c in shop_cols[:-1]] + [str(si)]
        lines.append(f'insert into public.shops ({", ".join(shop_cols)}) values ({", ".join(values)}) on conflict (id) do nothing;')
        order = 0
        for cat in shop['categories']:
            for row in cat['items']:
                rows.append({'shop_id': shop['id'], 'category': cat['category'], **row, 'sort_order': order})
                order += 1
    lines += [
        'create temporary table desired_shop_items on commit drop as\nselect * from jsonb_to_recordset(' + json_sql(rows) + ')\nas x(shop_id text, category text, item_id text, stock int, refresh_time int, price_modifier numeric, sort_order int);',
        'delete from public.shop_items s where s.shop_id in (' + ','.join(quote(s['id']) for _, s in shops) + ')\nand not exists (select 1 from desired_shop_items d where (d.shop_id,d.category,d.item_id)=(s.shop_id,s.category,s.item_id));',
        'insert into public.shop_items (shop_id,category,item_id,stock,refresh_time,price_modifier,sort_order)\nselect shop_id,category,item_id,stock,refresh_time,price_modifier,sort_order from desired_shop_items\non conflict (shop_id,category,item_id) do update set stock=excluded.stock,refresh_time=excluded.refresh_time,price_modifier=excluded.price_modifier,sort_order=excluded.sort_order;',
        '''do $$
begin
  if exists (select 1 from public.shop_items s join item_aliases a on a.old_id=s.item_id
             where s.shop_id in (select distinct shop_id from desired_shop_items)) then
    raise exception 'Retired item IDs still stocked';
  end if;
  if exists (select 1 from desired_shop_items d left join public.items i on i.id=d.item_id where i.id is null or coalesce(i.buy_price,0)<=0) then
    raise exception 'Missing/unpriced item in shop inventory';
  end if;
end $$;''',
        'select count(*) as updated_shop_listings from desired_shop_items;',
    ]
    return lines


def check():
    data = load('item_list.json')
    items = data['items']
    by_id = {i['id']: i for i in items}
    assert len(items) == len(by_id), 'Duplicate master IDs'
    assert not (set(by_id) & ALIASES.keys()), 'Retired IDs in master'
    for shop in load('shop_inventory.json')['shops']:
        seen = set()
        for cat in shop['categories']:
            for row in cat['items']:
                item_id = row['item_id']
                assert item_id in by_id, f'Undefined shop item {item_id}'
                assert item_id not in seen, f'Duplicate shop item {shop["id"]}/{item_id}'
                assert by_id[item_id].get('buy_price', 0) > 0, f'Unpriced shop item {item_id}'
                seen.add(item_id)
    for filename in ACTIVE_FILES:
        obj = load(filename)
        assert replace_refs(obj) == obj, f'Retired reference in {filename}'
    for recipe in load('crafting_recipes.json')['recipes']:
        for ref in [recipe['result'], *recipe['ingredients']]:
            assert ref['item_id'] in by_id, f'Undefined recipe item {recipe["recipe_id"]}/{ref["item_id"]}'
    supported = {'restore_hp', 'restore_mp', 'restore_hp_percent', 'restore_mp_percent', 'restore_energy'}
    for item in additions():
        assert all(e['effect_id'] in supported and e['value'] > 0 for e in item['special_effects'])
    print(f'PASS: {len(items)} unique items; shops, crafting and retired references valid.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--sql-only', action='store_true', help='Regenerate SQL from the saved audit and current shops')
    args = parser.parse_args()
    if args.check:
        check()
        return
    if args.sql_only:
        check()
        report = load(REPORT.name)
        shop_ids = set(report['changed_shops'])
        shops = [(n, s) for n, s in enumerate(load('shop_inventory.json')['shops']) if s['id'] in shop_ids]
        changed = {i['id']: i for i in report['updated_items']}
        for n, item in enumerate(load('item_list.json')['items']):
            if item['id'] in set(ALIASES.values()):
                changed[item['id']] = dict(item, sort_order=n)
        generate_sql(list(changed.values()), shops, ALIASES)
        print(f'Regenerated {SQL.name}: {SQL.stat().st_size} bytes.')
        return
    if REPORT.exists():
        raise SystemExit('Consolidation already applied; use --check. Keep the original delta/report.')
    original = load('item_list.json')
    original_by_id = {i['id']: i for i in original['items']}
    duplicate_counts = Counter(i['id'] for i in original['items'])
    original_files = {name: load(name) for name in ACTIVE_FILES}
    # Preserve the effective runtime definition (last-write-wins) of repeated IDs.
    last = {i['id']: n for n, i in enumerate(original['items'])}
    items = [copy.deepcopy(i) for n, i in enumerate(original['items'])
             if n == last[i['id']] and i['id'] not in ALIASES]
    items.extend(additions())
    by_id = {i['id']: i for i in items}
    for item_id, amount in [('con_medium_hp_cell', 200), ('con_medium_mp_cell', 120),
                            ('con_large_hp_cell', 500), ('con_large_mp_cell', 300)]:
        item = by_id[item_id]
        stat = 'hp' if '_hp_' in item_id else 'mp'
        item['special_effects'] = [{'effect_id': 'restore_' + stat, 'value': amount}]
        item['description'] = f'A medical energy cell that restores {amount} {stat.upper()}.'
    for item_id, stat in [('con_full_hp_cell', 'hp'), ('con_full_mp_cell', 'mp')]:
        by_id[item_id]['special_effects'] = [{'effect_id': f'restore_{stat}_percent', 'value': 100}]
    for item_id, name, desc in [
        ('itm_revival_elixir', 'Emergency Revival Injector', 'A nanomedical injector. Revives a defeated ally with 30% HP.'),
        ('itm_phoenix_core', 'Phoenix Reboot Core', 'An Aethel-powered resuscitation core. Revives a defeated ally with full HP and MP.'),
        ('crs_core_fragment', 'Concentrated Aethel Core Fragment', 'A high-grade reactor fragment with concentrated Aethel energy. Distinct from ordinary core fragments.'),
        ('bio_shard_essence', 'Mutated Shard Bio-Essence', 'A biological extract from shard-mutated organisms, distinct from altar-distilled Shard Essence.'),
        ('art_prima_materia', 'Refined Aethel Essence', 'A rare refined Aethel catalyst. Distinct from mythic Prima Materia used for endgame upgrades.'),
        ('boots_scout_boots', 'Reinforced Scout Boots', 'Reinforced patrol boots with improved protection and perception.'),
    ]:
        by_id[item_id].update(name=name, description=desc)
    by_id['con_nutrient_ration']['description'] = 'A standard field ration. Restores 20 HP; does not restore exploration energy.'
    for item_id in ['wpn_t005_weapon1', 'wpn2_t005_weapon2', 'hlm_t005_helmet',
                    'arm_t005_armor', 'glv_t005_glove', 'trs_t005_trouser',
                    'bts_t005_boots', 'acc1_t005_accessory1', 'acc2_t005_accessory2']:
        by_id[item_id]['name'] = 'Reinforced ' + by_id[item_id]['name']
    updated = {name: replace_refs(value) for name, value in original_files.items()}
    removed_listings = update_shops(updated['shop_inventory.json'], by_id)
    for recipe in updated['crafting_recipes.json']['recipes']:
        result_id = recipe['result']['item_id']
        old_id = next(r for r in original_files['crafting_recipes.json']['recipes'] if r['recipe_id'] == recipe['recipe_id'])['result']['item_id']
        if result_id != old_id or result_id in ['itm_revival_elixir', 'itm_phoenix_core']:
            recipe['recipe_name'] = 'Assemble ' + by_id[result_id]['name']
            recipe['description'] = by_id[result_id]['description']
            recipe['required_level'] = max(recipe.get('required_level', 1), by_id[result_id]['level_requirement'])
    # Stable recipe IDs are retained for any crafting jobs already in progress.
    updated['crafting_recipes.json']['recipes'].extend([
        {'recipe_id': 'rec_small_energy_cell', 'recipe_name': 'Recharge Small Energy Cell',
         'category': 'CONSUMABLE', 'required_level': 1, 'crafting_time_seconds': 10, 'crafting_cost': 15,
         'ingredients': [{'item_id': 'machine_parts', 'quantity': 1}, {'item_id': 'mat_aethel_dust', 'quantity': 1}],
         'result': {'item_id': 'con_small_energy_cell', 'quantity': 1}},
        {'recipe_id': 'rec_field_recovery_pack', 'recipe_name': 'Assemble Field Recovery Pack',
         'category': 'CONSUMABLE', 'required_level': 5, 'crafting_time_seconds': 15, 'crafting_cost': 20,
         'ingredients': [{'item_id': 'con_small_hp_cell', 'quantity': 2}, {'item_id': 'con_small_mp_cell', 'quantity': 2}],
         'result': {'item_id': 'con_field_recovery_pack', 'quantity': 1}},
    ])
    changed_files = [name for name, value in updated.items() if value != original_files[name]]
    changed_items = [dict(item, sort_order=n) for n, item in enumerate(items)
                     if item != original_by_id.get(item['id']) or item['id'] in set(ALIASES.values())]
    shops = [(n, s) for n, s in enumerate(updated['shop_inventory.json']['shops'])
             if s != original_files['shop_inventory.json']['shops'][n]]
    report = {
        'date': '2026-10-08', 'before_raw_count': len(original['items']),
        'before_unique_count': len(original_by_id), 'after_count': len(items),
        'removed_duplicate_rows': sum(v - 1 for v in duplicate_counts.values()),
        'duplicate_ids_kept_last': {k: v for k, v in duplicate_counts.items() if v > 1},
        'retired_existing_ids': {k: v for k, v in ALIASES.items() if k in original_by_id},
        'undefined_ids_replaced': {k: v for k, v in ALIASES.items() if k not in original_by_id},
        'new_items': additions(), 'updated_items': changed_items,
        'changed_reference_files': changed_files,
        'changed_shops': [s['id'] for _, s in shops], 'removed_shop_listings': removed_listings,
        'notes': [
            'Small HP/MP cells retain 50 HP / 30 MP. Medium cells now restore 200 HP / 120 MP; large cells 500 HP / 300 MP.',
            'Original canonical prices and stock limits are retained. Distinct material grades and gear tiers are renamed, not merged.',
            'Herbs, bandages, faction rations, buff tiers and loot crates have distinct costs/provenance/effects and are retained.',
            'Revival uses the itm_* IDs explicitly recognized by the client ally screen. Stable crafting recipe IDs are retained.',
            'Legacy Supabase rows use canonical definitions for saved inventories. They are not new shop or quest supplies.',
            'Crafting, biome and dungeon files are CDN/local data; redeploy those JSON files along with the item catalog.',
            'Existing cleanse, grenade, HoT and some utility consumables need client support beyond recovery-only combat. No new unsupported effects are added.',
        ],
    }
    # Validate the whole transformation before any data files are written.
    for shop in updated['shop_inventory.json']['shops']:
        for cat in shop['categories']:
            assert all(row['item_id'] in by_id for row in cat['items'])
    for recipe in updated['crafting_recipes.json']['recipes']:
        for ref in [recipe['result'], *recipe['ingredients']]:
            assert ref['item_id'] in by_id, f'Undefined recipe item: {ref["item_id"]}'
    for name in changed_files:
        save(ROOT / name, updated[name])
    save(ROOT / 'item_list.json', {**original, 'items': items})
    save(REPORT, report)
    generate_sql(changed_items, shops, ALIASES)
    check()
    print(f'Applied: {len(report["retired_existing_ids"])} merged IDs; {len(additions())} additions; {len(shops)} shops. SQL: {SQL.stat().st_size} bytes.')


if __name__ == '__main__':
    main()
