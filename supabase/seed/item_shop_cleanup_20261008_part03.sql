-- Item/shop audit: part 3/7. Run in order.
begin;

create temporary table item_aliases (old_id text primary key, new_id text not null) on commit drop;

insert into item_aliases values
('cns_health_potion_small','con_small_hp_cell'),
('potion_minor_healing','con_small_hp_cell'),
('minor_health_potion','con_small_hp_cell'),
('basic_hp_potion','con_small_hp_cell'),
('itm_minor_hp_potion','con_small_hp_cell'),
('cns_mana_potion_small','con_small_mp_cell'),
('potion_minor_mana','con_small_mp_cell'),
('itm_minor_mp_potion','con_small_mp_cell'),
('advanced_hp_potion','con_medium_hp_cell'),
('itm_hp_potion','con_medium_hp_cell'),
('itm_mp_potion','con_medium_mp_cell'),
('itm_greater_hp_potion','con_large_hp_cell'),
('itm_greater_mp_potion','con_large_mp_cell'),
('itm_full_heal_potion','con_full_recovery_pack'),
('con_revive_shard','itm_revive_shard'),
('storm_core','mat_storm_core'),
('iron_ore','mat_iron_ore'),
('crs_paradox_crystal','paradox_crystal'),
('scarab_shell','bio_scarab_shell'),
('potion_medium_healing','con_medium_hp_cell'),
('potion_medium_mana','con_medium_mp_cell'),
('potion_major_healing','con_large_hp_cell'),
('ration_field','con_nutrient_ration'),
('antidote_basic','con_antidote'),
('grenade_frag','con_scramble_grenade'),
('smoke_bomb','con_minor_stim_pack'),
('stim_combat','con_combat_stimulant'),
('armor_patch_basic','con_repair_patch'),
('repair_kit_field','con_repair_patch'),
('aethel_dust','mat_aethel_dust'),
('resonant_shard','crs_resonant_shard'),
('revival_shard','itm_revive_shard'),
('cleanse_vial','con_antidote'),
('mp_cell_small','con_small_mp_cell'),
('mp_cell_large','con_large_mp_cell'),
('mat_metal','scrap_metal');

insert into public.items (id, name, type, rarity, level_requirement, buy_price, sell_price, sell_value, max_stack, icon_image, description, equipment_slots, stats_bonus, special_effects, sort_order)
select a.old_id, i.name, i.type, i.rarity, i.level_requirement, i.buy_price, i.sell_price, i.sell_value, i.max_stack, i.icon_image, 'Legacy ID for ' || a.new_id || '. ' || coalesce(i.description, ''), i.equipment_slots, i.stats_bonus, i.special_effects, 100000 + row_number() over (order by a.old_id)
from item_aliases a join public.items i on i.id=a.new_id
on conflict (id) do update set name=excluded.name, type=excluded.type, rarity=excluded.rarity, level_requirement=excluded.level_requirement, buy_price=excluded.buy_price, sell_price=excluded.sell_price, sell_value=excluded.sell_value, max_stack=excluded.max_stack, icon_image=excluded.icon_image, description=excluded.description, equipment_slots=excluded.equipment_slots, stats_bonus=excluded.stats_bonus, special_effects=excluded.special_effects, sort_order=excluded.sort_order;

create or replace function pg_temp.replace_item_refs(value jsonb, aliases jsonb)
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


commit;
