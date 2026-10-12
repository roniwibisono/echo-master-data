-- Item/shop audit: part 6/7. Run in order.
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

insert into public.shops (id, name, faction, buy_currency, description, sort_order) values ('shop_meridian_capital', 'Cartel Trading Post', NULL, NULL, NULL, 26) on conflict (id) do nothing;

insert into public.shops (id, name, faction, buy_currency, description, sort_order) values ('shop_omnicorp_capital', 'OmniCorp Supply Division', NULL, NULL, NULL, 27) on conflict (id) do nothing;

insert into public.shops (id, name, faction, buy_currency, description, sort_order) values ('shop_shard_capital', 'Shard Sanctum Supplies', NULL, NULL, NULL, 28) on conflict (id) do nothing;

insert into public.shops (id, name, faction, buy_currency, description, sort_order) values ('shop_legion_capital', 'Legion Quartermaster Depot', NULL, NULL, NULL, 29) on conflict (id) do nothing;

insert into public.shops (id, name, faction, buy_currency, description, sort_order) values ('shop_crossroad_basic', 'Nexus Crossroads Supplies', NULL, NULL, NULL, 30) on conflict (id) do nothing;

insert into public.shops (id, name, faction, buy_currency, description, sort_order) values ('shop_bazaar_advanced', 'Central Spire Bazaar', NULL, NULL, NULL, 31) on conflict (id) do nothing;

insert into public.shops (id, name, faction, buy_currency, description, sort_order) values ('shop_orbital_elite', 'Orbital Neutral Hub Exchange', NULL, NULL, NULL, 32) on conflict (id) do nothing;

insert into public.shops (id, name, faction, buy_currency, description, sort_order) values ('shop_crossroad_blacksmith', 'Crossroads Forge', NULL, NULL, NULL, 33) on conflict (id) do nothing;

insert into public.shops (id, name, faction, buy_currency, description, sort_order) values ('shop_abyssal_smith', 'Abyssal Forge', NULL, NULL, NULL, 37) on conflict (id) do nothing;

insert into public.shops (id, name, faction, buy_currency, description, sort_order) values ('shop_nexus_elara', 'Elara''s General Supplies — Pax Nexus', 'NEUTRAL', 'CRD', 'General consumables and survival gear. All prices in CRD.', 38) on conflict (id) do nothing;

create temporary table desired_shop_items on commit drop as
select * from jsonb_to_recordset('[{"shop_id":"shop_meridian_capital","category":"consumables","item_id":"con_small_mp_cell","stock":30,"refresh_time":300,"price_modifier":1.0,"sort_order":0},{"shop_id":"shop_meridian_capital","category":"general","item_id":"con_small_hp_cell","stock":50,"refresh_time":300,"price_modifier":1.0,"sort_order":1},{"shop_id":"shop_meridian_capital","category":"general","item_id":"con_nutrient_ration","stock":40,"refresh_time":300,"price_modifier":1.0,"sort_order":2},{"shop_id":"shop_meridian_capital","category":"general","item_id":"con_minor_stim_pack","stock":35,"refresh_time":300,"price_modifier":1.0,"sort_order":3},{"shop_id":"shop_meridian_capital","category":"general","item_id":"scrap_metal","stock":30,"refresh_time":300,"price_modifier":1.0,"sort_order":4},{"shop_id":"shop_omnicorp_capital","category":"general","item_id":"con_small_hp_cell","stock":50,"refresh_time":300,"price_modifier":1.0,"sort_order":0},{"shop_id":"shop_omnicorp_capital","category":"general","item_id":"con_small_mp_cell","stock":50,"refresh_time":300,"price_modifier":1.0,"sort_order":1},{"shop_id":"shop_omnicorp_capital","category":"general","item_id":"con_minor_stim_pack","stock":35,"refresh_time":300,"price_modifier":1.0,"sort_order":2},{"shop_id":"shop_shard_capital","category":"consumables","item_id":"con_small_mp_cell","stock":30,"refresh_time":300,"price_modifier":1.0,"sort_order":0},{"shop_id":"shop_shard_capital","category":"general","item_id":"con_small_hp_cell","stock":50,"refresh_time":300,"price_modifier":1.0,"sort_order":1},{"shop_id":"shop_shard_capital","category":"general","item_id":"con_nutrient_ration","stock":35,"refresh_time":300,"price_modifier":1.0,"sort_order":2},{"shop_id":"shop_shard_capital","category":"general","item_id":"shardroot_vine","stock":20,"refresh_time":300,"price_modifier":1.0,"sort_order":3},{"shop_id":"shop_legion_capital","category":"consumables","item_id":"con_small_mp_cell","stock":30,"refresh_time":300,"price_modifier":1.0,"sort_order":0},{"shop_id":"shop_legion_capital","category":"general","item_id":"con_small_hp_cell","stock":50,"refresh_time":300,"price_modifier":1.0,"sort_order":1},{"shop_id":"shop_legion_capital","category":"general","item_id":"con_repair_patch","stock":30,"refresh_time":300,"price_modifier":1.0,"sort_order":2},{"shop_id":"shop_legion_capital","category":"general","item_id":"scrap_metal","stock":25,"refresh_time":300,"price_modifier":1.0,"sort_order":3},{"shop_id":"shop_crossroad_basic","category":"general","item_id":"con_small_hp_cell","stock":50,"refresh_time":300,"price_modifier":1.0,"sort_order":0},{"shop_id":"shop_crossroad_basic","category":"general","item_id":"con_small_mp_cell","stock":50,"refresh_time":300,"price_modifier":1.0,"sort_order":1},{"shop_id":"shop_crossroad_basic","category":"general","item_id":"con_nutrient_ration","stock":30,"refresh_time":300,"price_modifier":1.0,"sort_order":2},{"shop_id":"shop_crossroad_basic","category":"general","item_id":"scrap_metal","stock":30,"refresh_time":300,"price_modifier":1.0,"sort_order":3},{"shop_id":"shop_bazaar_advanced","category":"general","item_id":"con_medium_hp_cell","stock":30,"refresh_time":300,"price_modifier":1.0,"sort_order":0},{"shop_id":"shop_bazaar_advanced","category":"general","item_id":"con_medium_mp_cell","stock":30,"refresh_time":300,"price_modifier":1.0,"sort_order":1},{"shop_id":"shop_bazaar_advanced","category":"general","item_id":"con_repair_patch","stock":25,"refresh_time":300,"price_modifier":1.0,"sort_order":2},{"shop_id":"shop_bazaar_advanced","category":"general","item_id":"con_minor_stim_pack","stock":25,"refresh_time":300,"price_modifier":1.0,"sort_order":3},{"shop_id":"shop_bazaar_advanced","category":"general","item_id":"con_large_energy_cell","stock":15,"refresh_time":1800,"price_modifier":1.0,"sort_order":4},{"shop_id":"shop_orbital_elite","category":"general","item_id":"con_elite_recovery_pack","stock":20,"refresh_time":600,"price_modifier":1.0,"sort_order":0},{"shop_id":"shop_orbital_elite","category":"general","item_id":"con_medium_hp_cell","stock":40,"refresh_time":300,"price_modifier":1.0,"sort_order":1},{"shop_id":"shop_orbital_elite","category":"general","item_id":"con_medium_mp_cell","stock":40,"refresh_time":300,"price_modifier":1.0,"sort_order":2},{"shop_id":"shop_orbital_elite","category":"general","item_id":"void_fragment","stock":10,"refresh_time":600,"price_modifier":1.0,"sort_order":3},{"shop_id":"shop_orbital_elite","category":"general","item_id":"titan_core","stock":5,"refresh_time":1200,"price_modifier":1.0,"sort_order":4},{"shop_id":"shop_crossroad_blacksmith","category":"weapons_basic","item_id":"wpn_apprentice_staff","stock":5,"refresh_time":86400,"price_modifier":1.0,"sort_order":0},{"shop_id":"shop_crossroad_blacksmith","category":"weapons_basic","item_id":"wpn_hunter_dagger","stock":5,"refresh_time":86400,"price_modifier":1.0,"sort_order":1},{"shop_id":"shop_crossroad_blacksmith","category":"weapons_basic","item_id":"wpn_iron_sword","stock":5,"refresh_time":86400,"price_modifier":1.0,"sort_order":2},{"shop_id":"shop_crossroad_blacksmith","category":"weapons_basic","item_id":"wpn_rusty_sword","stock":5,"refresh_time":86400,"price_modifier":1.0,"sort_order":3},{"shop_id":"shop_crossroad_blacksmith","category":"weapons_basic","item_id":"wpn_scrap_axe","stock":5,"refresh_time":86400,"price_modifier":1.0,"sort_order":4},{"shop_id":"shop_crossroad_blacksmith","category":"weapons_basic","item_id":"wpn_training_spear","stock":5,"refresh_time":86400,"price_modifier":1.0,"sort_order":5},{"shop_id":"shop_crossroad_blacksmith","category":"armor_basic","item_id":"arm_iron_plate","stock":5,"refresh_time":86400,"price_modifier":1.0,"sort_order":6},{"shop_id":"shop_crossroad_blacksmith","category":"armor_basic","item_id":"arm_leather_tunic","stock":5,"refresh_time":86400,"price_modifier":1.0,"sort_order":7},{"shop_id":"shop_crossroad_blacksmith","category":"armor_basic","item_id":"armor_cloth_robes","stock":5,"refresh_time":86400,"price_modifier":1.0,"sort_order":8},{"shop_id":"shop_crossroad_blacksmith","category":"armor_basic","item_id":"armor_guard_chainmail","stock":5,"refresh_time":86400,"price_modifier":1.0,"sort_order":9},{"shop_id":"shop_crossroad_blacksmith","category":"armor_basic","item_id":"armor_leather_vest","stock":5,"refresh_time":86400,"price_modifier":1.0,"sort_order":10},{"shop_id":"shop_crossroad_blacksmith","category":"forge_materials","item_id":"mat_iron_ore","stock":20,"refresh_time":3600,"price_modifier":1.0,"sort_order":11},{"shop_id":"shop_crossroad_blacksmith","category":"forge_materials","item_id":"leather_strip","stock":20,"refresh_time":3600,"price_modifier":1.0,"sort_order":12},{"shop_id":"shop_crossroad_blacksmith","category":"forge_materials","item_id":"wood_plank","stock":20,"refresh_time":3600,"price_modifier":1.0,"sort_order":13},{"shop_id":"shop_crossroad_blacksmith","category":"forge_materials","item_id":"scrap_metal","stock":20,"refresh_time":3600,"price_modifier":1.0,"sort_order":14},{"shop_id":"shop_crossroad_blacksmith","category":"forge_materials","item_id":"mat_iron_ingot","stock":10,"refresh_time":3600,"price_modifier":1.0,"sort_order":15},{"shop_id":"shop_abyssal_smith","category":"void_weapons","item_id":"wpn_t045_weapon1","stock":2,"refresh_time":86400,"price_modifier":2.0,"sort_order":0},{"shop_id":"shop_abyssal_smith","category":"void_weapons","item_id":"wpn_t025_weapon1","stock":3,"refresh_time":86400,"price_modifier":1.6,"sort_order":1},{"shop_id":"shop_abyssal_smith","category":"void_armor","item_id":"arm_t045_armor","stock":2,"refresh_time":86400,"price_modifier":2.0,"sort_order":2},{"shop_id":"shop_abyssal_smith","category":"void_armor","item_id":"arm_iron_plate","stock":3,"refresh_time":86400,"price_modifier":1.5,"sort_order":3},{"shop_id":"shop_abyssal_smith","category":"void_materials","item_id":"void_crystal_shard","stock":5,"refresh_time":86400,"price_modifier":1.0,"sort_order":4},{"shop_id":"shop_abyssal_smith","category":"void_materials","item_id":"raw_aethel_fragment","stock":3,"refresh_time":86400,"price_modifier":1.0,"sort_order":5},{"shop_id":"shop_abyssal_smith","category":"void_materials","item_id":"crs_resonance_crystal","stock":4,"refresh_time":3600,"price_modifier":1.0,"sort_order":6},{"shop_id":"shop_abyssal_smith","category":"void_materials","item_id":"void_fragment","stock":3,"refresh_time":86400,"price_modifier":1.0,"sort_order":7},{"shop_id":"shop_abyssal_smith","category":"consumables","item_id":"con_small_hp_cell","stock":10,"refresh_time":300,"price_modifier":1.5,"sort_order":8},{"shop_id":"shop_abyssal_smith","category":"consumables","item_id":"con_small_mp_cell","stock":10,"refresh_time":300,"price_modifier":1.5,"sort_order":9},{"shop_id":"shop_nexus_elara","category":"consumables","item_id":"con_small_hp_cell","stock":-1,"refresh_time":0,"price_modifier":1.2,"sort_order":0},{"shop_id":"shop_nexus_elara","category":"consumables","item_id":"con_medium_hp_cell","stock":-1,"refresh_time":0,"price_modifier":1.2,"sort_order":1},{"shop_id":"shop_nexus_elara","category":"consumables","item_id":"con_small_mp_cell","stock":-1,"refresh_time":0,"price_modifier":1.2,"sort_order":2},{"shop_id":"shop_nexus_elara","category":"consumables","item_id":"con_medium_mp_cell","stock":-1,"refresh_time":0,"price_modifier":1.2,"sort_order":3},{"shop_id":"shop_nexus_elara","category":"consumables","item_id":"con_nutrient_ration","stock":-1,"refresh_time":0,"price_modifier":1.0,"sort_order":4},{"shop_id":"shop_nexus_elara","category":"consumables","item_id":"con_antidote","stock":-1,"refresh_time":0,"price_modifier":1.0,"sort_order":5},{"shop_id":"shop_nexus_elara","category":"consumables","item_id":"con_small_energy_cell","stock":20,"refresh_time":600,"price_modifier":1.0,"sort_order":6},{"shop_id":"shop_nexus_elara","category":"consumables","item_id":"con_field_recovery_pack","stock":15,"refresh_time":600,"price_modifier":1.0,"sort_order":7}]'::jsonb)
as x(shop_id text, category text, item_id text, stock int, refresh_time int, price_modifier numeric, sort_order int);

delete from public.shop_items s where s.shop_id in ('shop_meridian_capital','shop_omnicorp_capital','shop_shard_capital','shop_legion_capital','shop_crossroad_basic','shop_bazaar_advanced','shop_orbital_elite','shop_crossroad_blacksmith','shop_abyssal_smith','shop_nexus_elara')
and not exists (select 1 from desired_shop_items d where (d.shop_id,d.category,d.item_id)=(s.shop_id,s.category,s.item_id));

insert into public.shop_items (shop_id,category,item_id,stock,refresh_time,price_modifier,sort_order)
select shop_id,category,item_id,stock,refresh_time,price_modifier,sort_order from desired_shop_items
on conflict (shop_id,category,item_id) do update set stock=excluded.stock,refresh_time=excluded.refresh_time,price_modifier=excluded.price_modifier,sort_order=excluded.sort_order;

do $$
begin
  if exists (select 1 from public.shop_items s join item_aliases a on a.old_id=s.item_id
             where s.shop_id in (select distinct shop_id from desired_shop_items)) then
    raise exception 'Retired item IDs still stocked';
  end if;
  if exists (select 1 from desired_shop_items d left join public.items i on i.id=d.item_id where i.id is null or coalesce(i.buy_price,0)<=0) then
    raise exception 'Missing/unpriced item in shop inventory';
  end if;
end $$;

select count(*) as updated_shop_listings from desired_shop_items;

commit;
