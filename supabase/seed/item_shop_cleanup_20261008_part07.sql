-- Item/shop audit: part 7/7. Run in order.
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

insert into public.shops (id, name, faction, buy_currency, description, sort_order) values ('shop_nexus_grath', 'Grath''s Combat Outfitters — Pax Nexus', 'NEUTRAL', 'CRD', 'Combat equipment and weapons for all factions. Neutral pricing.', 39) on conflict (id) do nothing;

insert into public.shops (id, name, faction, buy_currency, description, sort_order) values ('shop_nexus_sable', 'Sable''s Rare Exchange — Pax Nexus', 'NEUTRAL', 'CRD', 'Rare materials and crafting components sourced from all seven territories.', 40) on conflict (id) do nothing;

insert into public.shops (id, name, faction, buy_currency, description, sort_order) values ('shop_nexus_mira_medical', 'Sister Mira''s Medical Station — Pax Nexus', 'NEUTRAL', 'CRD', 'Advanced healing supplies and medical equipment.', 41) on conflict (id) do nothing;

create temporary table desired_shop_items on commit drop as
select * from jsonb_to_recordset('[{"shop_id":"shop_nexus_grath","category":"consumables","item_id":"con_scramble_grenade","stock":20,"refresh_time":3600,"price_modifier":1.3,"sort_order":0},{"shop_id":"shop_nexus_grath","category":"consumables","item_id":"con_minor_stim_pack","stock":30,"refresh_time":3600,"price_modifier":1.1,"sort_order":1},{"shop_id":"shop_nexus_grath","category":"consumables","item_id":"con_combat_stimulant","stock":15,"refresh_time":3600,"price_modifier":1.4,"sort_order":2},{"shop_id":"shop_nexus_grath","category":"consumables","item_id":"con_repair_patch","stock":40,"refresh_time":3600,"price_modifier":1.0,"sort_order":3},{"shop_id":"shop_nexus_grath","category":"consumables","item_id":"con_defense_tonic","stock":15,"refresh_time":600,"price_modifier":1.0,"sort_order":4},{"shop_id":"shop_nexus_sable","category":"materials","item_id":"metal_shard","stock":50,"refresh_time":7200,"price_modifier":1.5,"sort_order":0},{"shop_id":"shop_nexus_sable","category":"materials","item_id":"refined_scrap","stock":30,"refresh_time":7200,"price_modifier":1.4,"sort_order":1},{"shop_id":"shop_nexus_sable","category":"materials","item_id":"mat_aethel_dust","stock":20,"refresh_time":7200,"price_modifier":1.6,"sort_order":2},{"shop_id":"shop_nexus_sable","category":"materials","item_id":"crs_resonant_shard","stock":15,"refresh_time":7200,"price_modifier":1.8,"sort_order":3},{"shop_id":"shop_nexus_sable","category":"materials","item_id":"void_fragment","stock":5,"refresh_time":28800,"price_modifier":2.5,"sort_order":4},{"shop_id":"shop_nexus_mira_medical","category":"consumables","item_id":"con_large_hp_cell","stock":-1,"refresh_time":0,"price_modifier":1.1,"sort_order":0},{"shop_id":"shop_nexus_mira_medical","category":"consumables","item_id":"itm_revive_shard","stock":10,"refresh_time":3600,"price_modifier":1.5,"sort_order":1},{"shop_id":"shop_nexus_mira_medical","category":"consumables","item_id":"con_antidote","stock":20,"refresh_time":3600,"price_modifier":1.2,"sort_order":2},{"shop_id":"shop_nexus_mira_medical","category":"consumables","item_id":"con_small_mp_cell","stock":-1,"refresh_time":0,"price_modifier":1.0,"sort_order":3},{"shop_id":"shop_nexus_mira_medical","category":"consumables","item_id":"con_large_mp_cell","stock":20,"refresh_time":3600,"price_modifier":1.3,"sort_order":4},{"shop_id":"shop_nexus_mira_medical","category":"consumables","item_id":"con_field_recovery_pack","stock":20,"refresh_time":600,"price_modifier":1.0,"sort_order":5},{"shop_id":"shop_nexus_mira_medical","category":"consumables","item_id":"itm_revival_elixir","stock":15,"refresh_time":1800,"price_modifier":1.0,"sort_order":6},{"shop_id":"shop_nexus_mira_medical","category":"consumables","item_id":"itm_phoenix_core","stock":5,"refresh_time":3600,"price_modifier":1.0,"sort_order":7}]'::jsonb)
as x(shop_id text, category text, item_id text, stock int, refresh_time int, price_modifier numeric, sort_order int);

delete from public.shop_items s where s.shop_id in ('shop_nexus_grath','shop_nexus_sable','shop_nexus_mira_medical')
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
