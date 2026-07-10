#!/usr/bin/env python3
"""Author the game_settings catalog -> emit game_settings.json (CDN canonical)
+ seed SQL. This domain is NEW (no pre-existing CDN file), so this tool IS the
authoring source of truth. Run:  python3 supabase/tools/import_game_settings.py

Each row: key, category, value (CURRENT in-code value so enabling the system is
behaviour-neutral), default (production intent), type, min, max, hot_reloadable,
description. Fixing dev-inflated multipliers = later step (flip value->default).
"""
import json, os
os.chdir('/Users/rnddev/Documents/echo-master-data')

ROWS = []
def S(key, cat, value, default, vtype, mn=None, mx=None, desc='', hot=True, cver=None):
    ROWS.append(dict(key=key, category=cat, value=value, default_value=default,
                     value_type=vtype, min_value=mn, max_value=mx,
                     hot_reloadable=hot, requires_client_version=cver,
                     enabled=True, description=desc, sort_order=len(ROWS)))

# ── MULTIPLIERS (game_config.dart) — value=CURRENT (dev-inflated), default=prod
S('exp.global_multiplier',      'multiplier', 13.0, 1.0, 'double', 0.1, 100, 'Global EXP multiplier on ALL exp gains. Currently dev-inflated (13); production default 1.0.')
S('credit.global_multiplier',   'multiplier', 1.0, 1.0, 'double', 0.1, 100, 'Global credit (CRD) multiplier.')
S('drop.rate_multiplier',       'multiplier', 1.0, 1.0, 'double', 0.0, 10,  'Global loot drop-rate multiplier (2.0 = double drops).')
S('exp.multi_enemy_bonus',      'multiplier', 10.3, 1.3, 'double', 1.0, 50, 'EXP bonus vs multiple enemies. Dev-inflated (10.3); prod 1.3.')
S('exp.elite_bonus',            'multiplier', 10.6, 1.6, 'double', 1.0, 50, 'EXP bonus vs elite/boss. Dev-inflated (10.6); prod 1.6.')
S('exp.idle_multiplier',        'multiplier', 105.0, 1.0, 'double', 0.1, 500,'Idle/AFK EXP-per-minute multiplier. Dev-inflated (105); prod 1.0.')
S('credit.idle_multiplier',     'multiplier', 1.0, 1.0, 'double', 0.1, 200, 'Idle credit-per-minute multiplier.')
S('quest.exp_multiplier',       'multiplier', 10.0, 1.0, 'double', 0.1, 100, 'Quest EXP reward multiplier (stacks with exp.global). Dev-inflated (10); prod 1.0.')
S('quest.credit_multiplier',    'multiplier', 1.0, 1.0, 'double', 0.1, 100, 'Quest credit reward multiplier.')
S('crafting.time_multiplier',   'multiplier', 1.0, 1.0, 'double', 0.1, 10,  'Crafting time multiplier (0.5 = twice as fast).')
S('crafting.cost_multiplier',   'multiplier', 1.0, 1.0, 'double', 0.1, 10,  'Crafting cost multiplier.')

# ── PROGRESSION (careful — affects existing players)
S('progression.max_player_level',    'progression', 100, 100, 'int', 1, 999, 'Hard level cap.', hot=False)
S('progression.xp_curve_linear',     'progression', 350, 350, 'int', 1, 100000, 'Linear coefficient A in XP curve A*L + B*L^2.', hot=False)
S('progression.xp_curve_quad',       'progression', 50, 50, 'int', 0, 100000, 'Quadratic coefficient B in XP curve A*L + B*L^2.', hot=False)
S('progression.start_exp_to_next',   'progression', 500, 400, 'int', 1, 100000, 'Initial expToNextLevel at creation. NOTE: 500 is inconsistent with formula (=400); default fixes it.', hot=False)
S('progression.stat_points_per_level',      'progression', 3, 3, 'int', 0, 100, 'Stat points granted per level-up (level <= 60).')
S('progression.stat_points_per_level_60',   'progression', 2, 2, 'int', 0, 100, 'Stat points per level-up when level > 60.')
S('progression.hp_per_stat_point',   'progression', 10, 10, 'int', 1, 1000, 'Max HP gained per allocated HP stat point.')
S('progression.mp_per_stat_point',   'progression', 5, 5, 'int', 1, 1000, 'Max MP gained per allocated MP stat point.')
S('progression.promote_level_advance','progression', 30, 30, 'int', 1, 999, 'Level gate: base -> advance class promotion.', hot=False)
S('progression.promote_level_master', 'progression', 60, 60, 'int', 1, 999, 'Level gate: advance -> master class promotion.', hot=False)
S('progression.respec_cost_base',    'progression', 500, 500, 'int', 0, 1000000, 'Base credit cost to respec stats (x level).')
S('progression.respec_cost_scale',   'progression', 0.5, 0.5, 'double', 0, 100, 'Respec cost growth per prior respec.')

# ── STARTING STATE
S('start.credits',          'starting', 100, 100, 'int', 0, 10000000, 'Starting universal credits (CRD).')
S('start.faction_currency', 'starting', 1000, 1000, 'int', 0, 10000000, 'Starting faction currency.')
S('start.rubies',           'starting', 0, 0, 'int', 0, 10000000, 'Starting premium currency (rubies).')
S('start.energy',           'starting', 100, 100, 'int', 0, 100000, 'Starting explore energy.')
S('start.max_energy',       'starting', 100, 100, 'int', 1, 100000, 'Starting max energy capacity.')
S('start.level',            'starting', 1, 1, 'int', 1, 999, 'Starting player level.', hot=False)
S('start.power_rating',     'starting', 10, 10, 'int', 0, 1000000, 'Starting power rating (matchmaking seed).')

# ── ENERGY / EXPLORE
S('energy.max',                    'energy', 100, 100, 'int', 1, 100000, 'Max energy capacity.')
S('energy.regen_minutes_per_point','energy', 3, 3, 'int', 1, 1440, 'Minutes to regenerate 1 energy.')
S('energy.cost_per_explore',       'energy', 1, 1, 'int', 0, 1000, 'Base energy cost per explore action (regions may override).')
S('explore.daily_soft_cap',        'energy', 20, 20, 'int', 0, 100000, 'Explores per day before diminishing returns.')
S('explore.diminishing_multiplier','energy', 0.5, 0.5, 'double', 0, 1, 'Reward multiplier once past the daily soft cap.')
S('explore.teleport_cost',         'energy', 100, 100, 'int', 0, 1000000, 'Faction-currency cost of a map teleport.')

# ── IDLE / AFK
S('idle.exp_per_min',            'idle', 1.5, 1.5, 'double', 0, 100000, 'Base idle EXP per minute (before idle multiplier).')
S('idle.currency_per_min',       'idle', 50, 50, 'int', 0, 1000000, 'Base idle faction-currency per minute.')
S('idle.cap_minutes',            'idle', 480, 480, 'int', 0, 100000, 'Max idle minutes accumulated (8h).')
S('idle.item_drop_threshold_min','idle', 60, 60, 'int', 0, 100000, 'Idle minutes per random item drop.')
S('afk.encounter_min_sec',       'idle', 4, 4, 'int', 1, 600, 'AFK-hunt: min seconds between encounters.')
S('afk.encounter_max_sec',       'idle', 8, 8, 'int', 1, 600, 'AFK-hunt: max seconds between encounters.')
S('afk.power_save_sec',          'idle', 120, 120, 'int', 5, 3600, 'AFK-hunt: idle seconds before power-save mode.')
S('afk.defeat_hp_restore_pct',   'idle', 0.30, 0.30, 'double', 0, 1, 'AFK-hunt: fraction of max HP restored on defeat.')

# ── ECONOMY / TRADE
S('economy.foreign_trade_tax_pct',     'economy', 8.0, 8.0, 'double', 0, 100, 'Tax % buying/selling outside home faction.')
S('economy.currency_exchange_tax_pct', 'economy', 5.0, 5.0, 'double', 0, 100, 'Tax % at currency-exchange NPCs.')
S('crafting.delivery_fee',             'economy', 1000, 1000, 'int', 0, 10000000, 'Faction-currency fee to deliver crafted items to inbox.')
S('economy.bank_max_slots',            'economy', 50, 50, 'int', 1, 100000, 'Bank storage slot limit.')
S('economy.rest_base_cost',            'economy', 50, 50, 'int', 0, 1000000, 'Inn rest base cost (full HP/MP restore).')
S('economy.revive_per_ally',           'economy', 30, 30, 'int', 0, 1000000, 'Inn surcharge per defeated ally revived.')
S('economy.wounded_treat_fee',         'economy', 10, 10, 'int', 0, 1000000, 'Inn surcharge per wounded ally treated.')

# ── COMBAT (client-side; tuning only — see anti-cheat)
S('combat.hit_base',            'combat', 85, 85, 'int', 0, 100, 'Base hit chance %.')
S('combat.hit_floor',           'combat', 60, 60, 'int', 0, 100, 'Minimum hit chance % (clamp).')
S('combat.hit_ceil',            'combat', 99, 99, 'int', 0, 100, 'Maximum hit chance % (clamp).')
S('combat.dodge_coef',          'combat', 0.15, 0.15, 'double', 0, 10, 'Dodge % per (DEF_AGI - ATK_PER) delta.')
S('combat.dodge_ceil',          'combat', 35, 35, 'int', 0, 100, 'Max dodge %.')
S('combat.crit_base',           'combat', 5.0, 5.0, 'double', 0, 100, 'Base critical-hit %.')
S('combat.crit_delta_coef',     'combat', 0.1, 0.1, 'double', 0, 10, 'Crit % per AGI delta.')
S('combat.crit_ceil',           'combat', 40, 40, 'int', 0, 100, 'Max crit %.')
S('combat.crit_damage_mult',    'combat', 1.5, 1.5, 'double', 1, 100, 'Critical damage multiplier.')
S('combat.block_coef',          'combat', 0.05, 0.05, 'double', 0, 10, 'Block % per DEF.')
S('combat.block_damage_reduction','combat', 0.6, 0.6, 'double', 0, 1, 'Damage multiplier when blocked (0.6 = -40%).')
S('combat.block_ceil_normal',   'combat', 25, 25, 'int', 0, 100, 'Max block % when not defending.')
S('combat.block_ceil_defend',   'combat', 35, 35, 'int', 0, 100, 'Max block % when defending.')
S('combat.def_mitigation_k',    'combat', 100, 100, 'int', 1, 100000, 'K in DEF mitigation 100/(K+DEF).')
S('combat.high_mp_threshold',   'combat', 0.80, 0.80, 'double', 0, 1, 'MP fraction that triggers high-MP damage boost.')
S('combat.turn_order_randomness','combat', 20, 20, 'int', 0, 1000, 'Random 0..N added to AGI for turn order.')
S('combat.last_stand_enabled',  'combat', True, True, 'bool', None, None, 'Prevent one lethal hit (survive at 1 HP) per battle.')

# ── RAID / SIEGE
S('raid.recommended_power_per_level','raid', 320, 320, 'int', 1, 100000, 'Recommended player power = minLevel * this.')
S('siege.reinforce_duration_min','siege', 15, 15, 'int', 1, 100000, 'Reinforce decree duration (min).')
S('siege.reinforce_cooldown_min','siege', 30, 30, 'int', 0, 100000, 'Reinforce decree cooldown (min).')
S('siege.reinforce_cost',        'siege', 500, 500, 'int', 0, 10000000, 'Reinforce decree treasury cost.')
S('siege.surge_duration_min',    'siege', 10, 10, 'int', 1, 100000, 'Surge decree duration (min).')
S('siege.surge_cooldown_min',    'siege', 30, 30, 'int', 0, 100000, 'Surge decree cooldown (min).')
S('siege.surge_cost',            'siege', 600, 600, 'int', 0, 10000000, 'Surge decree treasury cost.')
S('siege.treasury_shield_duration_min','siege', 2880, 2880, 'int', 1, 1000000, 'Treasury Shield duration (min, 48h).')
S('siege.treasury_shield_cost',  'siege', 1000, 1000, 'int', 0, 10000000, 'Treasury Shield treasury cost.')
S('siege.lockdown_duration_min', 'siege', 10, 10, 'int', 1, 100000, 'Lockdown decree duration (min).')
S('siege.lockdown_cooldown_min', 'siege', 45, 45, 'int', 0, 100000, 'Lockdown decree cooldown (min).')
S('siege.lockdown_cost',         'siege', 800, 800, 'int', 0, 10000000, 'Lockdown decree treasury cost.')
S('siege.deploy_supply_duration_min','siege', 1, 1, 'int', 1, 100000, 'Deploy Supply decree duration (min).')
S('siege.deploy_supply_cooldown_min','siege', 20, 20, 'int', 0, 100000, 'Deploy Supply decree cooldown (min).')
S('siege.deploy_supply_cost',    'siege', 400, 400, 'int', 0, 10000000, 'Deploy Supply decree treasury cost.')

# ── CONCLAVE PvP (core timing + VP + skills)
S('conclave.duel.vp_target',      'conclave', 100, 100, 'int', 1, 100000, 'Duel: VP to win.')
S('conclave.duel.duration_sec',   'conclave', 240, 240, 'int', 10, 100000, 'Duel: match length (s).')
S('conclave.duel.sudden_death_sec','conclave', 60, 60, 'int', 0, 100000, 'Duel: sudden-death timer (s).')
S('conclave.duel.skill1_mp',      'conclave', 30, 30, 'int', 0, 10000, 'Duel skill 1 MP cost.')
S('conclave.duel.skill1_cd_sec',  'conclave', 8, 8, 'int', 0, 10000, 'Duel skill 1 cooldown (s).')
S('conclave.duel.skill1_vp',      'conclave', 6, 6, 'int', 0, 10000, 'Duel skill 1 VP reward.')
S('conclave.duel.skill2_mp',      'conclave', 80, 80, 'int', 0, 10000, 'Duel skill 2 MP cost.')
S('conclave.duel.skill2_cd_sec',  'conclave', 15, 15, 'int', 0, 10000, 'Duel skill 2 cooldown (s).')
S('conclave.duel.skill2_vp',      'conclave', 10, 10, 'int', 0, 10000, 'Duel skill 2 VP reward.')
S('conclave.duel.attack_vp',      'conclave', 3, 3, 'int', 0, 10000, 'Duel basic-attack VP reward.')
S('conclave.duel.kill_bonus_vp',  'conclave', 20, 20, 'int', 0, 10000, 'Duel KO bonus VP.')
S('conclave.duel.mp_regen_per_sec','conclave', 2, 2, 'int', 0, 10000, 'Duel MP regen per second.')
S('conclave.match.vp_target',     'conclave', 150, 150, 'int', 1, 100000, '4v4 Match: VP to win.')
S('conclave.match.duration_sec',  'conclave', 480, 480, 'int', 10, 100000, '4v4 Match: length (s).')
S('conclave.match.node_capture_ticks','conclave', 15, 15, 'int', 1, 100000, '4v4 Match: ticks to capture a node.')
S('conclave.match.node_capture_vp','conclave', 15, 15, 'int', 0, 100000, '4v4 Match: VP per node capture.')
S('conclave.prep_duration_sec',   'conclave', 30, 30, 'int', 0, 100000, 'Conclave prep/ready-up timer (s).')
S('conclave.max_slots',           'conclave', 3, 3, 'int', 1, 20, 'Conclave team ally slots.')

# ── FACTION WAR & BUFFS
S('faction.war_max_duration_days','faction', 14, 14, 'int', 1, 3650, 'Faction war auto-expires after N days.')
S('faction.war_cooldown_days',    'faction', 3, 3, 'int', 0, 3650, 'Cooldown between wars (days).')
S('faction.war_declare_cost',     'faction', 5000, 5000, 'int', 0, 100000000, 'Treasury cost to declare war.')
S('faction.min_vote_level',       'faction', 10, 10, 'int', 1, 999, 'Min player level to vote in faction affairs.')
S('faction.buff_atk_pct',         'faction', 5, 5, 'int', 0, 1000, 'War Cry: ATK % buff.')
S('faction.buff_atk_cost',        'faction', 2000, 2000, 'int', 0, 100000000, 'War Cry treasury cost.')
S('faction.buff_atk_duration_h',  'faction', 24, 24, 'int', 1, 100000, 'War Cry duration (h).')
S('faction.buff_def_pct',         'faction', 5, 5, 'int', 0, 1000, 'Iron Wall: DEF % buff.')
S('faction.buff_def_cost',        'faction', 2000, 2000, 'int', 0, 100000000, 'Iron Wall treasury cost.')
S('faction.buff_def_duration_h',  'faction', 24, 24, 'int', 1, 100000, 'Iron Wall duration (h).')
S('faction.buff_exp_pct',         'faction', 10, 10, 'int', 0, 1000, 'Knowledge Drive: EXP % buff.')
S('faction.buff_exp_cost',        'faction', 3000, 3000, 'int', 0, 100000000, 'Knowledge Drive treasury cost.')
S('faction.buff_exp_duration_h',  'faction', 48, 48, 'int', 1, 100000, 'Knowledge Drive duration (h).')
S('faction.buff_loot_pct',        'faction', 15, 15, 'int', 0, 1000, 'Fortune Tide: LOOT % buff.')
S('faction.buff_loot_cost',       'faction', 3500, 3500, 'int', 0, 100000000, 'Fortune Tide treasury cost.')
S('faction.buff_loot_duration_h', 'faction', 24, 24, 'int', 1, 100000, 'Fortune Tide duration (h).')
S('faction.buff_craft_pct',       'faction', 20, 20, 'int', 0, 1000, 'Artisan Rush: CRAFT time -% buff.')
S('faction.buff_craft_cost',      'faction', 2500, 2500, 'int', 0, 100000000, 'Artisan Rush treasury cost.')
S('faction.buff_craft_duration_h','faction', 24, 24, 'int', 1, 100000, 'Artisan Rush duration (h).')
S('faction.buff_regen_pct',       'faction', 25, 25, 'int', 0, 1000, 'Vitality Surge: REGEN % buff.')
S('faction.buff_regen_cost',      'faction', 2000, 2000, 'int', 0, 100000000, 'Vitality Surge treasury cost.')
S('faction.buff_regen_duration_h','faction', 24, 24, 'int', 1, 100000, 'Vitality Surge duration (h).')

# ── SOCIAL / SYSTEM
S('social.max_party_size',        'social', 3, 3, 'int', 1, 20, 'Max party/ally slots.')
S('system.api_timeout_sec',       'system', 15, 15, 'int', 1, 300, 'Network API request timeout (s).')
S('system.data_sync_timeout_short_sec','system', 5, 5, 'int', 1, 300, 'Short data-sync timeout (s).')
S('system.data_sync_timeout_long_sec', 'system', 10, 10, 'int', 1, 300, 'Long data-sync timeout (s).')
S('system.remote_data_timeout_sec','system', 15, 15, 'int', 1, 300, 'Remote asset/data load timeout (s).')
S('combat.battle_speed_base_ms',  'system', 1800, 1800, 'int', 100, 10000, 'Battle turn delay at 1x (2x/4x derive from this).')

# ── FEATURE FLAGS (kill switches for incident response)
S('feature.enable_raids',    'feature', True, True, 'bool', None, None, 'Master switch: raid content.')
S('feature.enable_conclave', 'feature', True, True, 'bool', None, None, 'Master switch: Conclave PvP.')
S('feature.enable_siege',    'feature', True, True, 'bool', None, None, 'Master switch: siege/faction war.')
S('feature.enable_trading',  'feature', True, True, 'bool', None, None, 'Master switch: trading/market.')
S('feature.enable_crafting', 'feature', True, True, 'bool', None, None, 'Master switch: crafting.')
S('feature.enable_idle',     'feature', True, True, 'bool', None, None, 'Master switch: idle/AFK rewards.')
S('feature.enable_explore',  'feature', True, True, 'bool', None, None, 'Master switch: explore.')

# ── LIVE-OPS (maintenance, client gating, MOTD, events)
S('liveops.maintenance_mode',   'liveops', False, False, 'bool', None, None, 'Lock logins + show maintenance banner.')
S('liveops.maintenance_message','liveops', '', '', 'string', None, None, 'Maintenance banner text.')
S('liveops.maintenance_ends_at','liveops', '', '', 'string', None, None, 'ISO time maintenance ends (empty = unknown).')
S('liveops.min_client_version', 'liveops', '1.0.0', '1.0.0', 'string', None, None, 'Minimum allowed client version.')
S('liveops.force_update',       'liveops', False, False, 'bool', None, None, 'Force clients below min version to update.')
S('liveops.recommended_version','liveops', '1.0.0', '1.0.0', 'string', None, None, 'Recommended client version.')
S('liveops.motd_text',          'liveops', '', '', 'string', None, None, 'Server announcement / message of the day.')
S('liveops.motd_severity',      'liveops', 'info', 'info', 'string', None, None, 'MOTD severity: info|warning|critical.')
S('liveops.motd_expires_at',    'liveops', '', '', 'string', None, None, 'ISO time MOTD expires (empty = never).')
S('liveops.active_event_id',    'liveops', '', '', 'string', None, None, 'Active timed-event id (empty = none).')
S('liveops.event_starts_at',    'liveops', '', '', 'string', None, None, 'ISO event start.')
S('liveops.event_ends_at',      'liveops', '', '', 'string', None, None, 'ISO event end.')

# ── NEW-PLAYER / CATCH-UP & SEASON
S('catchup.below_level',   'season', 0, 0, 'int', 0, 999, 'Grant catch-up bonus to players below this level (0 = off).')
S('catchup.multiplier',    'season', 1.0, 1.0, 'double', 1, 100, 'EXP multiplier applied under catchup.below_level.')
S('season.id',             'season', '', '', 'string', None, None, 'Current season id (empty = none).')
S('season.starts_at',      'season', '', '', 'string', None, None, 'ISO season start.')
S('season.ends_at',        'season', '', '', 'string', None, None, 'ISO season end.')

# ── ANTI-CHEAT sanity caps (server-side validation; 0 = disabled)
S('anticheat.max_exp_per_hour',     'anticheat', 0, 0, 'int', 0, 1000000000, 'Max EXP/hour before flagging (0 = disabled).')
S('anticheat.max_credits_per_hour', 'anticheat', 0, 0, 'int', 0, 1000000000, 'Max credits/hour before flagging (0 = disabled).')
S('anticheat.max_levelups_per_day', 'anticheat', 0, 0, 'int', 0, 100000, 'Max level-ups/day before flagging (0 = disabled).')

# ── emit game_settings.json (CDN canonical, list of full objects)
json.dump({'meta': {'domain': 'game_settings', 'count': len(ROWS)}, 'settings': ROWS},
          open('game_settings.json', 'w'), indent=2, ensure_ascii=False)

# ── emit seed SQL
COLS = ['key','category','value','default_value','value_type','min_value','max_value',
        'hot_reloadable','requires_client_version','enabled','description','sort_order']
def s(v): return 'NULL' if v is None else "'" + str(v).replace("'", "''") + "'"
def jb(v): return "'" + json.dumps(v).replace("'", "''") + "'::jsonb"
def num(v): return 'NULL' if v is None else str(v)
def boolean(v): return 'true' if v else 'false'

def sqlval(r, c):
    if c in ('value', 'default_value'): return jb(r[c])
    if c in ('min_value', 'max_value'): return num(r[c])
    if c in ('hot_reloadable', 'enabled'): return boolean(r[c])
    if c == 'sort_order': return str(r[c])
    return s(r[c])

collist = ', '.join(f'"{c}"' if c == 'value' else c for c in COLS)
upd = ', '.join(f'{c}=excluded.{c}' for c in COLS if c != 'key')
lines = ['-- AUTO-GENERATED by import_game_settings.py — %d settings.' % len(ROWS), 'begin;']
for r in ROWS:
    vals = ', '.join(sqlval(r, c) for c in COLS)
    lines.append(f'insert into public.game_settings ({collist})\nvalues ({vals})\n'
                 f'on conflict (key) do update set {upd};')
lines.append('commit;')
open('supabase/seed/game_settings_seed.sql', 'w').write('\n'.join(lines) + '\n')

# sanity: keys unique, value within [min,max] for numerics
keys = [r['key'] for r in ROWS]
assert len(keys) == len(set(keys)), 'DUPLICATE KEYS: ' + str([k for k in keys if keys.count(k) > 1])
oob = [r['key'] for r in ROWS if r['value_type'] in ('int','double') and isinstance(r['value'],(int,float))
       and ((r['min_value'] is not None and r['value'] < r['min_value']) or
            (r['max_value'] is not None and r['value'] > r['max_value']))]
print(f'WROTE game_settings.json + game_settings_seed.sql ({len(ROWS)} settings, {len(set(r["category"] for r in ROWS))} categories)')
print('out-of-range values:', oob or 'none')
