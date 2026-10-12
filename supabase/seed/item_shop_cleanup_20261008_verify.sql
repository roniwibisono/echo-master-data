-- Read-only verification after ALL seven editor parts. Every issues count must be zero.
with aliases(old_id,new_id) as (values
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
('mat_metal','scrap_metal')
), expected as (
  select * from jsonb_to_recordset('[{"id":"con_small_energy_cell","effects":[{"effect_id":"restore_energy","value":25}]},{"id":"con_large_energy_cell","effects":[{"effect_id":"restore_energy","value":60}]},{"id":"con_field_recovery_pack","effects":[{"effect_id":"restore_hp","value":120},{"effect_id":"restore_mp","value":60}]},{"id":"con_full_recovery_pack","effects":[{"effect_id":"restore_hp_percent","value":100},{"effect_id":"restore_mp_percent","value":100}]},{"id":"cns_clean_water","effects":[]},{"id":"con_medium_hp_cell","effects":[{"effect_id":"restore_hp","value":200}]},{"id":"con_medium_mp_cell","effects":[{"effect_id":"restore_mp","value":120}]},{"id":"con_large_hp_cell","effects":[{"effect_id":"restore_hp","value":500}]},{"id":"con_large_mp_cell","effects":[{"effect_id":"restore_mp","value":300}]},{"id":"con_full_hp_cell","effects":[{"effect_id":"restore_hp_percent","value":100}]},{"id":"con_full_mp_cell","effects":[{"effect_id":"restore_mp_percent","value":100}]}]'::jsonb) as x(id text,effects jsonb)
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
