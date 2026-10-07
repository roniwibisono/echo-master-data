-- Content-only monster audit, 2026-10-08. No schema or player-save changes.
-- Includes only fields recorded by this audit, preserving other content edits.
begin;
update public.monsters set spawn_location='["NEXUS_CORE"]'::jsonb where monster_id=9999;
update public.monsters set ai_pattern='{"phase_1": {"hp_threshold": 1, "behavior": "rotational_aoe", "skills": ["inferno_breath", "wing_cyclone"]}, "phase_2": {"hp_threshold": 0.6, "behavior": "summon_minions", "skills": ["meteor_dive", "inferno_breath"], "atk_bonus": 0.2}, "phase_3": {"hp_threshold": 0.25, "behavior": "berserk", "skills": ["apocalypse_flare"], "atk_bonus": 0.5, "agi_bonus": 0.3}, "behavior": "standard_rotation"}'::jsonb where monster_id=4001;
update public.monsters set ai_pattern='{"phase_1": {"hp_threshold": 1, "behavior": "single_target_burst", "skills": ["void_lance", "shadow_bind"]}, "phase_2": {"hp_threshold": 0.7, "behavior": "aoe_control", "skills": ["abyssal_wave"], "def_bonus": 0.3}, "phase_3": {"hp_threshold": 0.35, "behavior": "collapse_burst", "skills": ["black_hole_collapse"], "atk_bonus": 0.6, "agi_bonus": 0.4}, "behavior": "aggressive_single_target"}'::jsonb where monster_id=4002;
update public.monsters set spawn_location='["ETERNAL_GATE", "PRIMA_MATERIA_FORGE"]'::jsonb where monster_id=4003;
update public.monsters set spawn_location='["AETHEL_STORM_RIDGE"]'::jsonb where monster_id=4004;
update public.monsters set spawn_location='["AETHEL_GARDENS"]'::jsonb where monster_id=5001;
update public.monsters set spawn_location='["CORAL_WETLANDS"]'::jsonb where monster_id=5002;
update public.monsters set spawn_location='["SCRAP_FIELD"]'::jsonb where monster_id=5003;
update public.monsters set spawn_location='["CRYSTAL_SLOPE"]'::jsonb where monster_id=5004;
update public.monsters set spawn_location='["AETHEL_GARDENS"]'::jsonb where monster_id=50010;
update public.monsters set spawn_location='["AETHEL_GARDENS"]'::jsonb where monster_id=5006;
update public.monsters set spawn_location='["AETHEL_GARDENS", "GLOWVINE_FOREST"]'::jsonb where monster_id=5007;
update public.monsters set spawn_location='["CRYSTAL_SLOPE"]'::jsonb where monster_id=5008;
update public.monsters set spawn_location='["SCRAP_FIELD"]'::jsonb where monster_id=50012;
update public.monsters set spawn_location='["BROKEN_CIVIL_QUARTER"]'::jsonb where monster_id=5101;
update public.monsters set spawn_location='["BROKEN_CIVIL_QUARTER"]'::jsonb where monster_id=5105;
update public.monsters set spawn_location='["BROKEN_CIVIL_QUARTER"]'::jsonb where monster_id=5106;
update public.monsters set spawn_location='["CRYSTAL_SLOPE"]'::jsonb where monster_id=5009;
update public.monsters set spawn_location='["CORAL_WETLANDS"]'::jsonb where monster_id=50013;
update public.monsters set spawn_location='["SMUGGLER_JUNGLE", "SHARDROOT_SWAMP"]'::jsonb where monster_id=5110;
update public.monsters set spawn_location='["SMUGGLER_JUNGLE", "SHARDROOT_SWAMP"]'::jsonb where monster_id=5111;
update public.monsters set spawn_location='["SMUGGLER_JUNGLE"]'::jsonb where monster_id=5112;
update public.monsters set spawn_location='["SHARDROOT_SWAMP"]'::jsonb where monster_id=5120;
update public.monsters set spawn_location='["SHARDROOT_SWAMP"]'::jsonb where monster_id=5121;
update public.monsters set spawn_location='["SHARDROOT_SWAMP"]'::jsonb where monster_id=5122;
update public.monsters set spawn_location='["SCORCHED_BADLANDS"]'::jsonb where monster_id=5130;
update public.monsters set spawn_location='["CRADLE_EXPANSE", "SUNKEN_AETHEL_RUIN", "HEARTWOOD_ALTAR", "BORDER_SKIRMISH_RING", "TITAN_GRAVEYARD"]'::jsonb where monster_id=5200;
update public.monsters set ai_pattern='{"phase_1": {"hp_threshold": 1, "behavior": "aoe_pressure", "skills": ["slime_wave", "gel_smash"]}, "phase_2": {"hp_threshold": 0.4, "behavior": "split_spawn", "skills": ["mini_slime_spawn"], "atk_bonus": 0.2}, "behavior": "aggressive_swarm"}'::jsonb where monster_id=50014;
update public.monsters set ai_pattern='{"phase_1": {"hp_threshold": 1, "behavior": "aggressive_single_target", "skills": ["feral_bite", "tail_whip"]}, "phase_2": {"hp_threshold": 0.4, "behavior": "frenzy", "skills": ["berserk_rush"], "atk_bonus": 0.3, "agi_bonus": 0.2}, "behavior": "aggressive_single_target"}'::jsonb, spawn_location='["FRACTURED_GLASS_VALLEY"]'::jsonb where monster_id=5102;
update public.monsters set ai_pattern='{"phase_1": {"hp_threshold": 1, "behavior": "ranged_pressure", "skills": ["shock_blast", "overcharge"]}, "phase_2": {"hp_threshold": 0.35, "behavior": "overload", "skills": ["electric_surge"], "atk_bonus": 0.25}, "behavior": "ranged_basic"}'::jsonb, spawn_location='["SCRAP_FIELD"]'::jsonb where monster_id=5103;
update public.monsters set ai_pattern='{"phase_1": {"hp_threshold": 1, "behavior": "hit_and_run", "skills": ["sting_thrust", "sand_dash"]}, "phase_2": {"hp_threshold": 0.4, "behavior": "venom_frenzy", "skills": ["venom_burst"], "atk_bonus": 0.3, "agi_bonus": 0.25}, "behavior": "hit_and_run"}'::jsonb where monster_id=5104;
update public.monsters set spawn_location='["SCRAP_FIELD"]'::jsonb where monster_id=5010;
update public.monsters set spawn_location='["SCRAP_FIELD"]'::jsonb where monster_id=5011;
update public.monsters set spawn_location='["CRADLE_OUTER_RING"]'::jsonb where monster_id=5115;
update public.monsters set spawn_location='["INNER_CRADLE_EXCLUSION", "SUNKEN_AETHEL_RUIN"]'::jsonb where monster_id=5201;
update public.monsters set spawn_location='["CORAL_WETLANDS"]'::jsonb where monster_id=5012;
update public.monsters set spawn_location='["CORAL_WETLANDS"]'::jsonb where monster_id=5013;
update public.monsters set spawn_location='["HIGHLAND_PLATEAU"]'::jsonb where monster_id=5014;
update public.monsters set spawn_location='["HIGHLAND_PLATEAU"]'::jsonb where monster_id=5015;
update public.monsters set spawn_location='["HIGHLAND_PLATEAU"]'::jsonb where monster_id=5016;
update public.monsters set spawn_location='["GLOWVINE_FOREST"]'::jsonb where monster_id=5017;
update public.monsters set spawn_location='["GLOWVINE_FOREST"]'::jsonb where monster_id=5018;
update public.monsters set spawn_location='["DUNE_OUTSKIRTS"]'::jsonb where monster_id=5019;
update public.monsters set spawn_location='["DUNE_OUTSKIRTS"]'::jsonb where monster_id=5020;
update public.monsters set spawn_location='["CRADLE_OUTER_RING"]'::jsonb where monster_id=5116;
update public.monsters set spawn_location='["FRACTURED_GLASS_VALLEY"]'::jsonb where monster_id=5117;
update public.monsters set spawn_location='["FRACTURED_GLASS_VALLEY"]'::jsonb where monster_id=5118;
update public.monsters set spawn_location='["IRON_RAVINE"]'::jsonb where monster_id=5123;
update public.monsters set spawn_location='["SMUGGLER_JUNGLE"]'::jsonb where monster_id=5124;
update public.monsters set spawn_location='["INNER_CRADLE_EXCLUSION", "SUNKEN_AETHEL_RUIN"]'::jsonb where monster_id=5202;
update public.monsters set spawn_location='["INNER_CRADLE_EXCLUSION"]'::jsonb where monster_id=5203;
update public.monsters set spawn_location='["TITAN_ASSEMBLY_YARD", "HEARTWOOD_ALTAR", "BLOOD_IRON_BASIN"]'::jsonb where monster_id=5204;
update public.monsters set spawn_location='["SUNKEN_AETHEL_RUIN", "SHARD_PULSE_PEAK", "HEARTWOOD_ALTAR", "TITAN_GRAVEYARD"]'::jsonb where monster_id=5205;
update public.monsters set spawn_location='["AETHEL_STORM_BELT", "SHARD_PULSE_PEAK", "SKYBRIDGE_REACTOR", "AETHEL_STORM_RIDGE"]'::jsonb where monster_id=5206;
update public.monsters set spawn_location='["CRADLE_EXPANSE", "TITAN_GRAVEYARD", "SHATTERED_HEART", "SEVERANCE_FAULTLINE", "AETHEL_SIPHON_CORE", "PRIMA_MATERIA_FORGE", "VOID_ECHO_CHASM"]'::jsonb where monster_id=5222;
update public.monsters set ai_pattern='{"phase_1": {"hp_threshold": 1, "behavior": "territorial_guardian", "skills": ["crystal_slam", "shard_barrage"]}, "phase_2": {"hp_threshold": 0.55, "behavior": "aoe_pressure", "skills": ["crystal_spike_field"], "def_bonus": 0.25}, "phase_3": {"hp_threshold": 0.25, "behavior": "berserk", "skills": ["tyrant_crystal_cataclysm"], "atk_bonus": 0.4}, "behavior": "territorial_guardian"}'::jsonb, spawn_location='["crystal_depths"]'::jsonb where monster_id=4101;
update public.monsters set spawn_location='["VOID_ECHO_CHASM", "VOID_RIFT_CROSSROADS"]'::jsonb where monster_id=5301;
update public.monsters set spawn_location='["GLOWVINE_FOREST"]'::jsonb where monster_id=5021;
update public.monsters set spawn_location='["GLOWVINE_FOREST"]'::jsonb where monster_id=5022;
update public.monsters set spawn_location='["BROKEN_CIVIL_QUARTER"]'::jsonb where monster_id=5023;
update public.monsters set spawn_location='["CRYSTAL_SLOPE"]'::jsonb where monster_id=5024;
update public.monsters set spawn_location='["DUNE_OUTSKIRTS"]'::jsonb where monster_id=5025;
update public.monsters set spawn_location='["AETHEL_GARDENS"]'::jsonb where monster_id=5031;
update public.monsters set spawn_location='["BROKEN_CIVIL_QUARTER"]'::jsonb where monster_id=5032;
update public.monsters set spawn_location='["CRYSTAL_SLOPE"]'::jsonb where monster_id=5033;
update public.monsters set spawn_location='["SCRAP_FIELD"]'::jsonb where monster_id=5034;
update public.monsters set spawn_location='["SHARDROOT_SWAMP"]'::jsonb where monster_id=5035;
update public.monsters set spawn_location='["AETHEL_GARDENS"]'::jsonb where monster_id=5041;
update public.monsters set spawn_location='["BROKEN_CIVIL_QUARTER"]'::jsonb where monster_id=5042;
update public.monsters set spawn_location='["AETHEL_GARDENS"]'::jsonb where monster_id=5043;
update public.monsters set spawn_location='["CRYSTAL_SLOPE"]'::jsonb where monster_id=5044;
update public.monsters set spawn_location='["DUNE_OUTSKIRTS", "SCORCHED_BADLANDS"]'::jsonb where monster_id=5045;
update public.monsters set spawn_location='["GLOWVINE_FOREST"]'::jsonb where monster_id=5046;
update public.monsters set ai_pattern='{"behavior": "aggressive_hunter"}'::jsonb, drop_item='[{"itemId": "overheated_reactor_part", "chance": 0.4}, {"itemId": "hydraulic_piston_fragment", "chance": 0.35}, {"itemId": "power_regulator_core", "chance": 0.2}]'::jsonb where monster_id=926;
update public.monsters set spawn_location='["CRADLE_EXPANSE", "AETHEL_SIPHON_CORE", "HIDDEN_AETHELGARDIAN_CITY"]'::jsonb where monster_id=5223;
update public.monsters set spawn_location='["CRADLE_EXPANSE", "BLOOD_IRON_BASIN", "SEVERANCE_FAULTLINE", "PRIMA_MATERIA_FORGE", "HIDDEN_AETHELGARDIAN_CITY"]'::jsonb where monster_id=5224;
update public.monsters set spawn_location='["CRADLE_EXPANSE", "VOID_RIFT_CROSSROADS", "SEVERANCE_FAULTLINE", "AETHEL_SIPHON_CORE", "PRIMA_MATERIA_FORGE", "HIDDEN_AETHELGARDIAN_CITY", "VOID_ECHO_CHASM"]'::jsonb where monster_id=5225;
update public.monsters set spawn_location='["CRADLE_EXPANSE", "VOID_RIFT_CROSSROADS", "SHATTERED_HEART", "SEVERANCE_FAULTLINE", "AETHEL_SIPHON_CORE", "PRIMA_MATERIA_FORGE", "HIDDEN_AETHELGARDIAN_CITY", "VOID_ECHO_CHASM"]'::jsonb where monster_id=5226;
update public.monsters set spawn_location='["SHATTERED_HEART"]'::jsonb where monster_id=50056;
insert into public.monsters (monster_id, code, name, rank, level, race_code, spawn_monster_id, critical_rate, critical_damage, exp_reward, currency_reward, crd_reward, guild_point, reputation_point, hunting_point, element, spawn_location, base_stats, scaling, resistances, weaknesses, status_immunity, ai_pattern, skill_set, drop_item, special_reward, sort_order)
values (6001, 'CRYSTAL_DEPTHS_SENTRY', 'Crystal Depths Sentry', 'normal', 40, 'CRYSTALLINE', 'dungeon', 0.08, 1.5, 1800, 800, 5, 10, 20, 10, '["earth", "arcane"]'::jsonb, '["crystal_depths"]'::jsonb, '{"hp": 7200, "mp": 450, "atk": 420, "def": 400, "agi": 40, "per": 55}'::jsonb, '{"basic_attack": 1.2, "skill_scaling_bonus": 0.3}'::jsonb, '["earth"]'::jsonb, '["electric"]'::jsonb, '["bleed"]'::jsonb, '{"behavior": "defensive_guard"}'::jsonb, '{"passive_skills": [{"skill_id": "crystal_armor"}], "active_skills": [{"skill_id": "crystal_puncture"}]}'::jsonb, '[{"itemId": "refined_crystal_shard", "chance": 0.5}]'::jsonb, '[]'::jsonb, 187)
on conflict (monster_id) do update set code=excluded.code, name=excluded.name, rank=excluded.rank, level=excluded.level, race_code=excluded.race_code, spawn_monster_id=excluded.spawn_monster_id, critical_rate=excluded.critical_rate, critical_damage=excluded.critical_damage, exp_reward=excluded.exp_reward, currency_reward=excluded.currency_reward, crd_reward=excluded.crd_reward, guild_point=excluded.guild_point, reputation_point=excluded.reputation_point, hunting_point=excluded.hunting_point, element=excluded.element, spawn_location=excluded.spawn_location, base_stats=excluded.base_stats, scaling=excluded.scaling, resistances=excluded.resistances, weaknesses=excluded.weaknesses, status_immunity=excluded.status_immunity, ai_pattern=excluded.ai_pattern, skill_set=excluded.skill_set, drop_item=excluded.drop_item, special_reward=excluded.special_reward, sort_order=excluded.sort_order;
insert into public.monsters (monster_id, code, name, rank, level, race_code, spawn_monster_id, critical_rate, critical_damage, exp_reward, currency_reward, crd_reward, guild_point, reputation_point, hunting_point, element, spawn_location, base_stats, scaling, resistances, weaknesses, status_immunity, ai_pattern, skill_set, drop_item, special_reward, sort_order)
values (6002, 'CRYSTAL_DEPTHS_SKITTER', 'Crystal Depths Skitter', 'normal', 42, 'CRYSTALLINE', 'dungeon', 0.08, 1.5, 2000, 900, 5, 10, 20, 10, '["earth", "arcane"]'::jsonb, '["crystal_depths"]'::jsonb, '{"hp": 5400, "mp": 320, "atk": 480, "def": 280, "agi": 65, "per": 45}'::jsonb, '{"basic_attack": 1.2, "skill_scaling_bonus": 0.3}'::jsonb, '["earth"]'::jsonb, '["electric"]'::jsonb, '["bleed"]'::jsonb, '{"behavior": "skirmisher"}'::jsonb, '{"passive_skills": [{"skill_id": "crystal_carapace"}], "active_skills": [{"skill_id": "shard_spike"}]}'::jsonb, '[{"itemId": "refined_crystal_shard", "chance": 0.5}]'::jsonb, '[]'::jsonb, 188)
on conflict (monster_id) do update set code=excluded.code, name=excluded.name, rank=excluded.rank, level=excluded.level, race_code=excluded.race_code, spawn_monster_id=excluded.spawn_monster_id, critical_rate=excluded.critical_rate, critical_damage=excluded.critical_damage, exp_reward=excluded.exp_reward, currency_reward=excluded.currency_reward, crd_reward=excluded.crd_reward, guild_point=excluded.guild_point, reputation_point=excluded.reputation_point, hunting_point=excluded.hunting_point, element=excluded.element, spawn_location=excluded.spawn_location, base_stats=excluded.base_stats, scaling=excluded.scaling, resistances=excluded.resistances, weaknesses=excluded.weaknesses, status_immunity=excluded.status_immunity, ai_pattern=excluded.ai_pattern, skill_set=excluded.skill_set, drop_item=excluded.drop_item, special_reward=excluded.special_reward, sort_order=excluded.sort_order;
do $monster_audit$
begin
 if (select count(*) from public.monsters where monster_id in (9999,4001,4002,4003,4004,5001,5002,5003,5004,50010,5006,5007,5008,50012,5101,5105,5106,5009,50013,5110,5111,5112,5120,5121,5122,5130,5200,50014,5102,5103,5104,5010,5011,5115,5201,5012,5013,5014,5015,5016,5017,5018,5019,5020,5116,5117,5118,5123,5124,5202,5203,5204,5205,5206,5222,4101,5301,5021,5022,5023,5024,5025,5031,5032,5033,5034,5035,5041,5042,5043,5044,5045,5046,926,5223,5224,5225,5226,50056,6001,6002)) <> 81 then
  raise exception 'Monster audit: target records missing'; end if;
 if exists (select 1 from public.monsters m cross join lateral jsonb_array_elements(m.drop_item || m.special_reward) d
  left join public.items i on i.id=d->>'itemId' where i.id is null) then
  raise exception 'Monster audit: undefined reward item'; end if;
 if exists (select 1 from public.monsters m cross join lateral jsonb_array_elements(m.skill_set->'active_skills') r
  left join public.skills s on s.id=r->>'skill_id' where s.id is null or s.type<>'Active') then
  raise exception 'Monster audit: invalid active skill'; end if;
 if exists (select 1 from public.monsters m cross join lateral jsonb_array_elements(m.skill_set->'passive_skills') r
  left join public.skills s on s.id=r->>'skill_id' where s.id is null or s.type<>'Passive') then
  raise exception 'Monster audit: invalid passive skill'; end if;
end;
$monster_audit$;
commit;

-- Verification: all three columns below must be zero.
select
 (select count(*) from public.monsters m cross join lateral jsonb_array_elements(m.drop_item || m.special_reward) d
  left join public.items i on i.id=d->>'itemId' where i.id is null) as undefined_items,
 (select count(*) from public.monsters m cross join lateral jsonb_array_elements(m.skill_set->'active_skills') r
  left join public.skills s on s.id=r->>'skill_id' where s.id is null or s.type<>'Active') as invalid_active_skills,
 (select count(*) from public.monsters m cross join lateral jsonb_array_elements(m.skill_set->'passive_skills') r
  left join public.skills s on s.id=r->>'skill_id' where s.id is null or s.type<>'Passive') as invalid_passive_skills;
