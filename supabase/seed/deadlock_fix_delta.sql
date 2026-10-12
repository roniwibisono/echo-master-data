-- Deadlock quest data delta. Generated from local JSON after neutral quest fix.
-- Run in Supabase SQL Editor instead of the full seed files.
begin;

-- 1) Neutral quest objectives/rewards changed by the deadlock fix.
update public.quests
set objectives = '[{"type": "travel", "target": "BLACK_DOCK_MARKET", "count": 1, "description": "Investigate the suspected arms route at Black Dock Market"}, {"type": "kill", "target": "BLACK_DOCK_SMUGGLER", "count": 5, "description": "Neutralize {count} rogue arms dealers near the contested border"}, {"type": "collect", "target": "illegal_weapon_cache", "count": 3, "description": "Recover 3 illegal weapon caches"}, {"type": "interact", "target": "NPC_NEXUS_QUESTGIVER_ARBITER", "count": 1, "description": "Return evidence to Arbiter Lorn Kael (Arbiter Lorn Kael at Pax Nexus — The Conclave Hall)"}]'::jsonb,
    rewards = '{"exp": 800, "currency": 0, "crd": 350, "reputation": 30, "items": [{"item_id": "custodian_badge_bronze", "quantity": 1}]}'::jsonb
where id = 'QUEST_NEUTRAL_STORY_001';

update public.quests
set objectives = '[{"type": "travel", "target": "BLACK_DOCK_MARKET", "count": 1, "description": "Infiltrate the suspected smuggling hub in the conflict zone"}, {"type": "collect", "target": "intel_drive", "count": 4, "description": "Gather {count} intelligence fragments without alerting guards"}, {"type": "kill", "target": "BLACK_DOCK_ASSASSIN", "count": 8, "description": "Eliminate {count} shadow enforcers who spot you during extraction"}, {"type": "interact", "target": "NPC_NEXUS_QUESTGIVER_COMMANDER", "count": 1, "description": "Deliver intelligence to Commander Holt (Commander Sera Holt at Pax Nexus — The Sentinel Outpost)"}]'::jsonb,
    rewards = '{"exp": 2000, "currency": 0, "crd": 800, "reputation": 60, "items": [{"item_id": "custodian_badge_silver", "quantity": 1}, {"item_id": "sentinel_comm_device", "quantity": 1}]}'::jsonb
where id = 'QUEST_NEUTRAL_STORY_002';

update public.quests
set objectives = '[{"type": "travel", "target": "BORDER_SKIRMISH_RING", "count": 1, "description": "Breach the rogue Custodian''s hidden fortress"}, {"type": "collect", "target": "precursor_weapon_cache", "count": 6, "description": "Recover {count} planet-killer weapon component caches"}, {"type": "kill", "target": "WARPATH_CHAMPION", "count": 1, "description": "Defeat the rogue Custodian Commander — a former Guardian-class Dreadnought captain"}, {"type": "interact", "target": "NPC_NEXUS_DIPLOMAT_VAEL", "count": 1, "description": "Return to Ambassador Vael with proof of neutralization (Ambassador Vael Drosian at Pax Nexus — The Diplomat''s Quarter)"}]'::jsonb,
    rewards = '{"exp": 8000, "currency": 0, "crd": 3500, "reputation": 200, "items": [{"item_id": "custodian_badge_gold", "quantity": 1}, {"item_id": "pact_keeper_insignia", "quantity": 1}, {"item_id": "sentinel_elite_armor_chest", "quantity": 1}]}'::jsonb
where id = 'QUEST_NEUTRAL_STORY_003';

update public.quests
set objectives = '[{"type": "travel", "target": "BROKEN_CIVIL_QUARTER", "count": 1, "description": "Travel to the Mid-Zone Skirmish Area node on the world map"}, {"type": "collect", "target": "salvaged_supply_crate", "count": 5, "description": "Collect 5x salvaged_supply_crate from the skirmish area drops"}, {"type": "kill", "target": "FERAL_SCAVENGER", "count": 10, "description": "Defeat 10x FERAL_SCAVENGER at the Mid-Zone Skirmish Area"}, {"type": "interact", "target": "NPC_NEXUS_MERCHANT_ELARA", "count": 1, "description": "Return to Elara Voss at Pax Nexus — The Common Market (Nexus Core) (Elara Voss at Pax Nexus — The Common Market)"}]'::jsonb,
    rewards = '{"exp": 500, "currency": 0, "crd": 200, "reputation": 15, "items": [{"item_id": "con_large_hp_cell", "quantity": 5}]}'::jsonb
where id = 'QUEST_NEUTRAL_SIDE_001';

update public.quests
set objectives = '[{"type": "travel", "target": "SECURE_MINING_GRID", "count": 1, "description": "Reach the hidden archive vault in the deep-tier region"}, {"type": "collect", "target": "archive_location_data", "count": 3, "description": "Recover {count} archive reader data fragments to locate the lost page"}, {"type": "kill", "target": "GRID_DEFENDER", "count": 4, "description": "Defeat {count} automatons guarding the vault"}, {"type": "collect", "target": "archive_scroll", "count": 1, "description": "Retrieve the lost archive page"}, {"type": "interact", "target": "NPC_NEXUS_INFO_CHRONICLER", "count": 1, "description": "Return the page to The Chronicler (The Chronicler at Pax Nexus — The Archive Spire)"}]'::jsonb,
    rewards = '{"exp": 1800, "currency": 0, "crd": 700, "reputation": 50, "items": [{"item_id": "mat_quantum_lens", "quantity": 1}, {"item_id": "ancient_data_slate", "quantity": 1}]}'::jsonb
where id = 'QUEST_NEUTRAL_SIDE_002';

update public.quests
set objectives = '[{"type": "kill", "target": "WARPATH_SCOUT", "count": 15, "description": "Eliminate {count} border raiders threatening the neutral zone"}, {"type": "travel", "target": "NEXUS_CORE", "count": 1, "description": "Return to report to Arbiter Lorn Kael (Travel to: Nexus Core)"}]'::jsonb,
    rewards = '{"exp": 300, "currency": 0, "crd": 120, "reputation": 10, "items": []}'::jsonb
where id = 'QUEST_NEUTRAL_DAILY_001';

update public.quests
set objectives = '[{"type": "travel", "target": "EXTRACTION_ZONE_DELTA", "count": 1, "description": "Reach the delivery point in the high-danger region"}, {"type": "kill", "target": "DELTA_ASSAULT_DRONE", "count": 6, "description": "Eliminate {count} interceptors who ambush you during delivery"}, {"type": "interact", "target": "npc_shady_smuggler", "count": 1, "description": "Complete the delivery with Ghost''s contact"}]'::jsonb,
    rewards = '{"exp": 600, "currency": 0, "crd": 280, "reputation": 0, "items": [{"item_id": "smugglers_cache", "quantity": 1}]}'::jsonb
where id = 'QUEST_NEUTRAL_DAILY_003';

update public.quests
set objectives = '[{"type": "travel", "target": "SECURE_MINING_GRID", "count": 1, "description": "Locate the underground counterfeit forge in the conflict zone"}, {"type": "kill", "target": "GRID_SENTINEL_DRONE", "count": 3, "description": "Disable {count} counterfeit CRD press control units"}, {"type": "kill", "target": "GRID_DEFENDER", "count": 10, "description": "Eliminate {count} forge guards protecting the operation"}, {"type": "collect", "target": "counterfeit_crd_sample", "count": 5, "description": "Recover 5 counterfeit CRD samples for forensic analysis"}, {"type": "interact", "target": "NPC_NEXUS_BANKER_AMA7", "count": 1, "description": "Submit samples to NEXON AMA-7 for analysis (NEXON AMA-7 at Pax Nexus — The AMA Exchange Hub)"}]'::jsonb,
    rewards = '{"exp": 3000, "currency": 0, "crd": 1500, "reputation": 100, "items": [{"item_id": "ama_certification_token", "quantity": 1}]}'::jsonb
where id = 'QUEST_NEUTRAL_AMA_001';

update public.quests
set objectives = '[{"type": "travel", "target": "BORDER_SKIRMISH_RING", "count": 1, "description": "Escort the AMA stabilization convoy to the crisis faction capital"}, {"type": "kill", "target": "BLACK_DOCK_SMUGGLER", "count": 20, "description": "Eliminate {count} speculator squads attacking the convoy"}, {"type": "interact", "target": "NPC_NEXUS_BANKER_AMA7", "count": 1, "description": "Deliver the stabilization package to the AMA terminal at the capital"}]'::jsonb,
    rewards = '{"exp": 15000, "currency": 0, "crd": 6000, "reputation": 400, "items": [{"item_id": "ama_master_seal", "quantity": 1}, {"item_id": "custodian_legendary_weapon_box", "quantity": 1}]}'::jsonb
where id = 'QUEST_NEUTRAL_AMA_002';

update public.quests
set objectives = '[{"type": "kill", "target": "BLACK_DOCK_ASSASSIN", "count": 12, "description": "Neutralize {count} summit disruptors before the delegates arrive"}, {"type": "travel", "target": "NEXUS_CORE", "count": 1, "description": "Escort Delegate A safely to the summit hall"}, {"type": "interact", "target": "NPC_NEXUS_DIPLOMAT_VAEL", "count": 1, "description": "Escort Delegate B safely to the summit hall"}, {"type": "kill", "target": "BLACK_DOCK_ASSASSIN", "count": 3, "description": "Defeat {count} elite assassins sent to disrupt the summit"}]'::jsonb,
    rewards = '{"exp": 2500, "currency": 400, "crd": 600, "reputation": 120, "items": [{"item_id": "diplomat_signet_ring", "quantity": 1}], "_reward_note": "currency=400 dibayar dalam mata uang faction player. crd=600 dari Custodian. Dual reward."}'::jsonb
where id = 'QUEST_NEUTRAL_SPECIAL_001';

-- 2) New/previously missing items referenced by those quests and rewards.
insert into public.items (id, name, type, rarity, level_requirement, buy_price, sell_price, sell_value, max_stack, icon_image, description, equipment_slots, stats_bonus, special_effects, sort_order)
values ('illegal_weapon_cache', 'Illegal Weapon Cache', 'QUEST', 'QUEST', 1, 0, 0, NULL, 99, '', 'A sealed crate of illicit weapons recovered from conflict-zone smugglers.', '[]'::jsonb, '{"hp": 0, "mp": 0, "atk": 0, "def": 0, "agi": 0, "per": 0}'::jsonb, '[]'::jsonb, 1145)
on conflict (id) do update set name=excluded.name, type=excluded.type, rarity=excluded.rarity, level_requirement=excluded.level_requirement, buy_price=excluded.buy_price, sell_price=excluded.sell_price, sell_value=excluded.sell_value, max_stack=excluded.max_stack, icon_image=excluded.icon_image, description=excluded.description, equipment_slots=excluded.equipment_slots, stats_bonus=excluded.stats_bonus, special_effects=excluded.special_effects, sort_order=excluded.sort_order;

insert into public.items (id, name, type, rarity, level_requirement, buy_price, sell_price, sell_value, max_stack, icon_image, description, equipment_slots, stats_bonus, special_effects, sort_order)
values ('counterfeit_crd_sample', 'Counterfeit CRD Sample', 'QUEST', 'QUEST', 1, 0, 0, NULL, 99, '', 'A forged Credent sample tagged for AMA forensic analysis.', '[]'::jsonb, '{"hp": 0, "mp": 0, "atk": 0, "def": 0, "agi": 0, "per": 0}'::jsonb, '[]'::jsonb, 1146)
on conflict (id) do update set name=excluded.name, type=excluded.type, rarity=excluded.rarity, level_requirement=excluded.level_requirement, buy_price=excluded.buy_price, sell_price=excluded.sell_price, sell_value=excluded.sell_value, max_stack=excluded.max_stack, icon_image=excluded.icon_image, description=excluded.description, equipment_slots=excluded.equipment_slots, stats_bonus=excluded.stats_bonus, special_effects=excluded.special_effects, sort_order=excluded.sort_order;

insert into public.items (id, name, type, rarity, level_requirement, buy_price, sell_price, sell_value, max_stack, icon_image, description, equipment_slots, stats_bonus, special_effects, sort_order)
values ('custodian_badge_bronze', 'Custodian Badge Bronze', 'QUEST', 'QUEST', 1, 0, 0, NULL, 99, '', 'A bronze service badge awarded by the Galactic Custodians.', '[]'::jsonb, '{"hp": 0, "mp": 0, "atk": 0, "def": 0, "agi": 0, "per": 0}'::jsonb, '[]'::jsonb, 1147)
on conflict (id) do update set name=excluded.name, type=excluded.type, rarity=excluded.rarity, level_requirement=excluded.level_requirement, buy_price=excluded.buy_price, sell_price=excluded.sell_price, sell_value=excluded.sell_value, max_stack=excluded.max_stack, icon_image=excluded.icon_image, description=excluded.description, equipment_slots=excluded.equipment_slots, stats_bonus=excluded.stats_bonus, special_effects=excluded.special_effects, sort_order=excluded.sort_order;

insert into public.items (id, name, type, rarity, level_requirement, buy_price, sell_price, sell_value, max_stack, icon_image, description, equipment_slots, stats_bonus, special_effects, sort_order)
values ('custodian_badge_silver', 'Custodian Badge Silver', 'QUEST', 'QUEST', 1, 0, 0, NULL, 99, '', 'A silver service badge awarded by the Galactic Custodians.', '[]'::jsonb, '{"hp": 0, "mp": 0, "atk": 0, "def": 0, "agi": 0, "per": 0}'::jsonb, '[]'::jsonb, 1148)
on conflict (id) do update set name=excluded.name, type=excluded.type, rarity=excluded.rarity, level_requirement=excluded.level_requirement, buy_price=excluded.buy_price, sell_price=excluded.sell_price, sell_value=excluded.sell_value, max_stack=excluded.max_stack, icon_image=excluded.icon_image, description=excluded.description, equipment_slots=excluded.equipment_slots, stats_bonus=excluded.stats_bonus, special_effects=excluded.special_effects, sort_order=excluded.sort_order;

insert into public.items (id, name, type, rarity, level_requirement, buy_price, sell_price, sell_value, max_stack, icon_image, description, equipment_slots, stats_bonus, special_effects, sort_order)
values ('custodian_badge_gold', 'Custodian Badge Gold', 'QUEST', 'QUEST', 1, 0, 0, NULL, 99, '', 'A gold service badge awarded by the Galactic Custodians.', '[]'::jsonb, '{"hp": 0, "mp": 0, "atk": 0, "def": 0, "agi": 0, "per": 0}'::jsonb, '[]'::jsonb, 1149)
on conflict (id) do update set name=excluded.name, type=excluded.type, rarity=excluded.rarity, level_requirement=excluded.level_requirement, buy_price=excluded.buy_price, sell_price=excluded.sell_price, sell_value=excluded.sell_value, max_stack=excluded.max_stack, icon_image=excluded.icon_image, description=excluded.description, equipment_slots=excluded.equipment_slots, stats_bonus=excluded.stats_bonus, special_effects=excluded.special_effects, sort_order=excluded.sort_order;

insert into public.items (id, name, type, rarity, level_requirement, buy_price, sell_price, sell_value, max_stack, icon_image, description, equipment_slots, stats_bonus, special_effects, sort_order)
values ('sentinel_comm_device', 'Sentinel Comm Device', 'QUEST', 'QUEST', 1, 0, 0, NULL, 99, '', 'A secure Custodian communications device keyed to Sentinel operations.', '[]'::jsonb, '{"hp": 0, "mp": 0, "atk": 0, "def": 0, "agi": 0, "per": 0}'::jsonb, '[]'::jsonb, 1150)
on conflict (id) do update set name=excluded.name, type=excluded.type, rarity=excluded.rarity, level_requirement=excluded.level_requirement, buy_price=excluded.buy_price, sell_price=excluded.sell_price, sell_value=excluded.sell_value, max_stack=excluded.max_stack, icon_image=excluded.icon_image, description=excluded.description, equipment_slots=excluded.equipment_slots, stats_bonus=excluded.stats_bonus, special_effects=excluded.special_effects, sort_order=excluded.sort_order;

insert into public.items (id, name, type, rarity, level_requirement, buy_price, sell_price, sell_value, max_stack, icon_image, description, equipment_slots, stats_bonus, special_effects, sort_order)
values ('pact_keeper_insignia', 'Pact Keeper Insignia', 'QUEST', 'QUEST', 1, 0, 0, NULL, 99, '', 'An insignia marking service in defense of inter-faction peace.', '[]'::jsonb, '{"hp": 0, "mp": 0, "atk": 0, "def": 0, "agi": 0, "per": 0}'::jsonb, '[]'::jsonb, 1151)
on conflict (id) do update set name=excluded.name, type=excluded.type, rarity=excluded.rarity, level_requirement=excluded.level_requirement, buy_price=excluded.buy_price, sell_price=excluded.sell_price, sell_value=excluded.sell_value, max_stack=excluded.max_stack, icon_image=excluded.icon_image, description=excluded.description, equipment_slots=excluded.equipment_slots, stats_bonus=excluded.stats_bonus, special_effects=excluded.special_effects, sort_order=excluded.sort_order;

insert into public.items (id, name, type, rarity, level_requirement, buy_price, sell_price, sell_value, max_stack, icon_image, description, equipment_slots, stats_bonus, special_effects, sort_order)
values ('sentinel_elite_armor_chest', 'Sentinel Elite Armor Chest', 'CONSUMABLE', 'EPIC', 1, 0, 0, NULL, 99, '', 'A sealed equipment cache containing elite Sentinel armor components.', '[]'::jsonb, '{"hp": 0, "mp": 0, "atk": 0, "def": 0, "agi": 0, "per": 0}'::jsonb, '[]'::jsonb, 1152)
on conflict (id) do update set name=excluded.name, type=excluded.type, rarity=excluded.rarity, level_requirement=excluded.level_requirement, buy_price=excluded.buy_price, sell_price=excluded.sell_price, sell_value=excluded.sell_value, max_stack=excluded.max_stack, icon_image=excluded.icon_image, description=excluded.description, equipment_slots=excluded.equipment_slots, stats_bonus=excluded.stats_bonus, special_effects=excluded.special_effects, sort_order=excluded.sort_order;

insert into public.items (id, name, type, rarity, level_requirement, buy_price, sell_price, sell_value, max_stack, icon_image, description, equipment_slots, stats_bonus, special_effects, sort_order)
values ('ama_certification_token', 'AMA Certification Token', 'QUEST', 'QUEST', 1, 0, 0, NULL, 99, '', 'A token certifying direct service to the Aegis Monetary Authority.', '[]'::jsonb, '{"hp": 0, "mp": 0, "atk": 0, "def": 0, "agi": 0, "per": 0}'::jsonb, '[]'::jsonb, 1153)
on conflict (id) do update set name=excluded.name, type=excluded.type, rarity=excluded.rarity, level_requirement=excluded.level_requirement, buy_price=excluded.buy_price, sell_price=excluded.sell_price, sell_value=excluded.sell_value, max_stack=excluded.max_stack, icon_image=excluded.icon_image, description=excluded.description, equipment_slots=excluded.equipment_slots, stats_bonus=excluded.stats_bonus, special_effects=excluded.special_effects, sort_order=excluded.sort_order;

insert into public.items (id, name, type, rarity, level_requirement, buy_price, sell_price, sell_value, max_stack, icon_image, description, equipment_slots, stats_bonus, special_effects, sort_order)
values ('ama_master_seal', 'AMA Master Seal', 'QUEST', 'QUEST', 1, 0, 0, NULL, 99, '', 'A high-grade seal issued for resolving a severe market stability crisis.', '[]'::jsonb, '{"hp": 0, "mp": 0, "atk": 0, "def": 0, "agi": 0, "per": 0}'::jsonb, '[]'::jsonb, 1154)
on conflict (id) do update set name=excluded.name, type=excluded.type, rarity=excluded.rarity, level_requirement=excluded.level_requirement, buy_price=excluded.buy_price, sell_price=excluded.sell_price, sell_value=excluded.sell_value, max_stack=excluded.max_stack, icon_image=excluded.icon_image, description=excluded.description, equipment_slots=excluded.equipment_slots, stats_bonus=excluded.stats_bonus, special_effects=excluded.special_effects, sort_order=excluded.sort_order;

insert into public.items (id, name, type, rarity, level_requirement, buy_price, sell_price, sell_value, max_stack, icon_image, description, equipment_slots, stats_bonus, special_effects, sort_order)
values ('custodian_legendary_weapon_box', 'Custodian Legendary Weapon Box', 'CONSUMABLE', 'LEGENDARY', 1, 0, 0, NULL, 99, '', 'A sealed Custodian cache containing a legendary-grade weapon reward.', '[]'::jsonb, '{"hp": 0, "mp": 0, "atk": 0, "def": 0, "agi": 0, "per": 0}'::jsonb, '[]'::jsonb, 1155)
on conflict (id) do update set name=excluded.name, type=excluded.type, rarity=excluded.rarity, level_requirement=excluded.level_requirement, buy_price=excluded.buy_price, sell_price=excluded.sell_price, sell_value=excluded.sell_value, max_stack=excluded.max_stack, icon_image=excluded.icon_image, description=excluded.description, equipment_slots=excluded.equipment_slots, stats_bonus=excluded.stats_bonus, special_effects=excluded.special_effects, sort_order=excluded.sort_order;

insert into public.items (id, name, type, rarity, level_requirement, buy_price, sell_price, sell_value, max_stack, icon_image, description, equipment_slots, stats_bonus, special_effects, sort_order)
values ('diplomat_signet_ring', 'Diplomat Signet Ring', 'QUEST', 'QUEST', 1, 0, 0, NULL, 99, '', 'A ceremonial signet awarded for protecting a cross-faction summit.', '[]'::jsonb, '{"hp": 0, "mp": 0, "atk": 0, "def": 0, "agi": 0, "per": 0}'::jsonb, '[]'::jsonb, 1156)
on conflict (id) do update set name=excluded.name, type=excluded.type, rarity=excluded.rarity, level_requirement=excluded.level_requirement, buy_price=excluded.buy_price, sell_price=excluded.sell_price, sell_value=excluded.sell_value, max_stack=excluded.max_stack, icon_image=excluded.icon_image, description=excluded.description, equipment_slots=excluded.equipment_slots, stats_bonus=excluded.stats_bonus, special_effects=excluded.special_effects, sort_order=excluded.sort_order;

insert into public.items (id, name, type, rarity, level_requirement, buy_price, sell_price, sell_value, max_stack, icon_image, description, equipment_slots, stats_bonus, special_effects, sort_order)
values ('brainwave_reader', 'Brainwave Reader', 'MATERIAL', 'UNCOMMON', 1, 120, 30, NULL, 99, 'materials/brainwave_reader.png', 'A compact device for recording volatile psionic waveforms.', '[]'::jsonb, '{"hp": 0, "mp": 0, "atk": 0, "def": 0, "agi": 0, "per": 0}'::jsonb, '[]'::jsonb, 1157)
on conflict (id) do update set name=excluded.name, type=excluded.type, rarity=excluded.rarity, level_requirement=excluded.level_requirement, buy_price=excluded.buy_price, sell_price=excluded.sell_price, sell_value=excluded.sell_value, max_stack=excluded.max_stack, icon_image=excluded.icon_image, description=excluded.description, equipment_slots=excluded.equipment_slots, stats_bonus=excluded.stats_bonus, special_effects=excluded.special_effects, sort_order=excluded.sort_order;

-- 3) Monster drop tables needed for the fixed collect objectives.
update public.monsters set drop_item = '[{"itemId": "mutant_claw", "chance": 0.6}, {"itemId": "salvaged_supply_crate", "chance": 0.35}]'::jsonb
where monster_id = 5105; -- FERAL_SCAVENGER

update public.monsters set drop_item = '[{"itemId": "metal_shard", "chance": 1}, {"itemId": "salvaged_alloy_fragment", "chance": 0.35}]'::jsonb
where monster_id = 50017; -- SCRAP_HOUND_FERAL

update public.monsters set drop_item = '[{"itemId": "contraband_core", "chance": 0.4}, {"itemId": "illegal_weapon_cache", "chance": 0.35}, {"itemId": "refined_scrap", "chance": 1}]'::jsonb
where monster_id = 5150; -- BLACK_DOCK_SMUGGLER

update public.monsters set drop_item = '[{"itemId": "rare_emblem", "chance": 0.4}, {"itemId": "intel_drive", "chance": 0.45}, {"itemId": "mutant_claw", "chance": 0.4}]'::jsonb
where monster_id = 5151; -- BLACK_DOCK_ASSASSIN

update public.monsters set drop_item = '[{"itemId": "sensor_chip", "chance": 1}, {"itemId": "circuit_fragment", "chance": 0.4}, {"itemId": "counterfeit_crd_sample", "chance": 0.35}]'::jsonb
where monster_id = 5165; -- GRID_SENTINEL_DRONE

update public.monsters set drop_item = '[{"itemId": "refined_scrap", "chance": 1}, {"itemId": "archive_location_data", "chance": 0.45}, {"itemId": "archive_scroll", "chance": 0.25}, {"itemId": "counterfeit_crd_sample", "chance": 0.45}]'::jsonb
where monster_id = 5166; -- GRID_DEFENDER

update public.monsters set drop_item = '[{"itemId": "rare_emblem", "chance": 0.7}, {"itemId": "precursor_weapon_cache", "chance": 0.45}]'::jsonb
where monster_id = 5182; -- WARPATH_CHAMPION

commit;
