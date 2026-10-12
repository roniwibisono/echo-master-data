#!/usr/bin/env python3
"""Build the memory catalog and training templates. --check does not write files."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NPC = 'npc_skill_artisan_ivara'
WEAPONS = ['Knuckle', 'Sword', 'Dagger', 'Spear', 'Polearm', 'Staff', 'Orb', 'Grimoire', 'Shield']

# Name, tier, weapon, damage formula, secondary mechanic, thematic material.
CATALOG = [
    ('Dark Punch', 1, 'Knuckle', 'atk * 1.25', 'weaken', 'void_parasite_egg'),
    ('Iron Jab', 1, 'Knuckle', 'atk * 1.15', 'cheap', 'scrap_metal'),
    ('Crescent Slash', 1, 'Sword', 'atk * 1.2', 'bleed', 'scorpion_stinger'),
    ('Needle Fang', 1, 'Dagger', 'atk * 1.3', 'pierce', 'scorpion_stinger'),
    ('Piercing Thrust', 1, 'Spear', 'atk * 1.2', 'pierce', 'scrap_metal'),
    ('Spark Bolt', 1, 'Staff', 'per * 1.35', 'strike', 'scrap_circuit'),
    ('Shield Pulse', 1, 'Shield', '0', 'shield', 'scrap_circuit'),
    ('Phantom Step', 2, 'Dagger', '0', 'evade', 'void_channeler_core'),
    ('Ember Knuckle', 2, 'Knuckle', 'atk * 1.4', 'burn', 'mat_storm_core'),
    ('Frost Lance', 2, 'Spear', 'atk * 1.5', 'slow', 'raw_aethel_fragment'),
    ('Thunder Arc', 2, 'Staff', 'per * 1.15', 'aoe', 'mat_storm_core'),
    ('Siphon Touch', 2, 'Orb', 'per * 1.45', 'drain', 'abyssal_reaver_claw'),
    ('Guardian Script', 2, 'Grimoire', '0', 'ally_shield', 'mutated_neural_core'),
    ('Venom Edge', 2, 'Sword', 'atk * 1.35', 'poison', 'toxic_spore_gland'),
    ('Gravity Break', 3, 'Knuckle', 'atk * 1.9', 'slow', 'void_core'),
    ('Moon Sever', 3, 'Sword', 'atk * 2.2', 'strike', 'drake_heart'),
    ('Chain Impale', 3, 'Polearm', 'atk * 0.7', 'multi', 'leviathan_scale'),
    ('Echo Mend', 3, 'Staff', '0', 'heal', 'ancient_scale'),
    ('Null Ward', 3, 'Grimoire', '0', 'ward', 'void_core'),
    ('Astral Rupture', 3, 'Orb', 'per * 1.6', 'aoe', 'drake_heart'),
]


def load(name):
    return json.loads((ROOT / name).read_text())


def effect(kind, value, duration=0):
    return {'type': kind, 'value': value, 'duration_turns': duration}


def contract():
    return {
        'schema_version': 1,
        'status': 'data_ready_runtime_pending',
        'source_type': 'Skill_Memory', 'item_type': 'SKILL_MEMORY',
        'base_slots_per_learner': 2, 'max_skill_level': 10,
        'weapon_families': WEAPONS,
        'weapon_matching': 'explicit_equipped_item_type_suffix_after_WEAPON_prefix_in_either_hand',
        'equipment_type_format': {'weapon': 'WEAPON_{SUBTYPE}', 'accessory': 'ACCESSORY_{SUBTYPE}'},
        'weapon_subtype_comparison': 'uppercase_exact_match; no implicit aliases',
        'slot_bonus_effect': 'increase_skill_memory_slots',
        'slot_bonus_sources': ['class_passive', 'race_passive', 'ally_passive', 'equipped_item_passive'],
        'memory_skills_can_grant_slots': False,
        'learner_key': ['player_id', 'learner_type', 'learner_id'],
        'client_storage_keys': {'learned': 'skill_memory_levels',
                                'equipped': 'equipped_memory_skill_ids',
                                'learning': 'quest_progress.definition_snapshot.skill_memory'},
        'persistent_state': {
            'learned_memories': 'map skill_id -> level (1..10)',
            'equipped_memories': 'ordered unique skill_ids, separate from class skills',
            'learning_attempts': 'map skill_id -> quest_id, attempt_id, status, objective_progress',
            'training_attempts': 'map skill_id -> from_level, to_level, quest_id, attempt_id, objective_progress',
        },
        'states': ['unlearned', 'learning', 'learned', 'training'],
        'item_use': {
            'transaction': ['validate_selected_owned_learner', 'reject_known_or_pending_skill',
                            'check_min_level', 'consume_exactly_one_item', 'create_learning_quest'],
            'atomic': True, 'idempotency_key': 'item_use_request_id',
            'quest_failure_rolls_back_consumption': True,
            'abandon_policy': 'pause_and_resume_same_attempt_without_refund',
            'quest_completion': 'unlock_level_1_for_bound_learner_only',
            'weapon_required_at_use': False,
        },
        'battle_rules': {
            'resolve': 'class_skills_plus_valid_equipped_memories_only',
            'enforce_weapon': 'at_equip_and_each_cast',
            'weapon_swap': 'keep_loadout_but_disable_incompatible_memory',
            'loadout_changes': 'out_of_combat_only',
            'party_rules': 'same_contract_independent_progress_per_member',
        },
        'progression': {
            'level_potency_multipliers': [round(1 + 0.06 * i, 2) for i in range(10)],
            'scale_only': ['damage_formula_result', 'periodic_effects.percent_atk.value',
                           'periodic_effects.heal_over_time.value', 'healing_amount', 'shield_amount'],
            'never_scale': ['mp_cost', 'cooldown_seconds', 'duration_turns', 'chance', 'hit_count',
                            'lifesteal_percent', 'defense_penetration_percent', 'stat_modifiers', 'slot_count'],
            'learning_template': {'id_pattern': 'q_mem_learn_{skill_slug}',
                                  'objectives': ['qualifying_victories_with_required_weapon', 'artisan_turn_in'],
                                  'victories_by_tier': [3, 5, 8]},
            'training_template': {'id_pattern': 'q_mem_train_{skill_slug}_{to_level}',
                                  'objectives': ['meaningful_skill_uses', 'qualifying_victories', 'artisan_turn_in'],
                                  'uses_formula': '5 * to_level * tier',
                                  'victories_formula': 'to_level + tier'},
            'event_identity': ['battle_id', 'action_id', 'learner_id', 'skill_id', 'attempt_id'],
            'eligibility': 'living_actor; non_dummy_non_pvp_enemy; enemy_level >= learner_level - 10',
            'meaningful_use': 'positive_damage_or_effective_heal_or_absorbed_shield_or_new_status',
            'deduplicate': 'one_use_per_action; one_victory_per_battle; never_reward_replayed_events',
            'training_preserves_current_level': True,
            'quests_authored_in': ['P2_learning', 'P4_training'],
        },
        'market': {'unused_item_tradable': True, 'bind_on_use': True,
                   'learned_skill_and_progress_tradable': False, 'crafted_item_stack_size': 20},
        'activation_requires': ['transactional_learning_handler', 'quest_templates',
                                'memory_loadout_resolver', 'weapon_family_tags', 'level_scaling'],
    }


def build():
    items = {x['id']: x for x in load('item_list.json')['items']}
    skills, memories, recipes, profiles = [], [], [], []
    for name, tier, weapon, formula, mechanic, material in CATALOG:
        slug = name.lower().replace(' ', '_')
        sid, iid, rid = 'sk_mem_' + slug, 'mem_' + slug, 'rcp_mem_' + slug
        minimum = [20, 40, 60][tier - 1]
        target = 'enemy'
        specials, periodic, modifiers = [], [], []
        details = f'Deals {formula} damage.'
        if mechanic in ('burn', 'bleed', 'poison'):
            periodic = [{'type': 'percent_atk', 'effect': mechanic, 'value': 20, 'scale': 0,
                         'duration_turns': 3, 'target': 'enemy', 'interval_turns': 1}]
            details += f' Inflicts {mechanic} for 3 turns (20% ATK per turn).'
        elif mechanic in ('weaken', 'slow'):
            stat = 'atk' if mechanic == 'weaken' else 'agi'
            modifiers = [{'stat': stat, 'value': -15, 'type': 'percent',
                          'duration_turns': 2, 'target': 'enemy', 'condition': ''}]
            details += f' Reduces enemy {stat.upper()} by 15% for 2 turns.'
        elif mechanic == 'pierce':
            specials = [effect('defense_penetration_percent', 20)]
            details += ' Ignores 20% DEF.'
        elif mechanic == 'drain':
            specials = [effect('lifesteal_percent', 20)]
            details += ' Restores HP equal to 20% of damage dealt.'
        elif mechanic == 'multi':
            specials = [dict(effect('multi_hit', 3), hits=3)]
            details = 'Three strikes, each dealing 70% ATK damage.'
        elif mechanic == 'aoe':
            target = 'all_enemy'
            details += ' Hits all enemies.'
        elif mechanic in ('shield', 'ally_shield', 'heal', 'ward', 'evade'):
            target = 'ally' if mechanic in ('ally_shield', 'heal') else 'self'
            if mechanic == 'shield':
                specials = [effect('shield_percent', 12)]
                details = 'Grants the caster a shield equal to 12% maximum HP.'
            elif mechanic == 'ally_shield':
                specials = [effect('grant_shield_scale_perception', 2)]
                details = 'Grants one ally a shield equal to 200% caster PER.'
            elif mechanic == 'heal':
                specials = [effect('direct_heal_scaling_perception', 2)]
                periodic = [{'type': 'heal_over_time', 'value': 3, 'scale': 0,
                             'condition': 'max_hp_percent',
                             'duration_turns': 3, 'target': 'ally', 'interval_turns': 1}]
                details = 'Restores 200% caster PER HP and regenerates 3% target maximum HP for 3 turns.'
            elif mechanic == 'ward':
                specials = [effect('debuff_immunity', 1, 2)]
                details = 'The caster resists new debuffs for 2 turns; does not cleanse existing debuffs.'
            else:
                specials = [effect('evasion_chance', 15, 2)]
                details = 'Grants the caster 15% evasion for 2 turns.'
        description = f'{details} Requires {weapon}. Equip as a learned Skill Memory.'
        skill = {
            'id': sid, 'name': name, 'type': 'Active', 'source_type': 'Skill_Memory',
            'mp_cost': 8 if mechanic == 'cheap' else [18, 32, 50][tier - 1],
            'damage_formula': formula, 'effect': details, 'stat_modifiers': modifiers,
            'periodic_effects': periodic, 'control_effects': [], 'special_effects': specials,
            'usage_requirements': {'allowed_classes': [], 'min_level': minimum,
                                   'allowed_weapons': [weapon], 'allowed_races': []},
            'target_attack': 'none' if formula == '0' else target,
            'target_effect': target, 'skill_description': description,
            'skill_shape': 'circle_aoe' if target == 'all_enemy' else 'single_projectile',
            'range': 4.0 if weapon in ('Staff', 'Orb', 'Grimoire') else 1.5,
            'aoe_radius': 2.5 if target == 'all_enemy' else 0.0,
            'projectile_speed': 0.0, 'cooldown_seconds': [3.0, 5.0, 7.0][tier - 1],
            'skill_memory_profile_id': sid,
            'skill_memory_tier': tier,
        }
        ingredients = [{'item_id': 'memory_fragment_chip', 'quantity': 2 * tier},
                       {'item_id': ['scrap_circuit', 'raw_aethel_fragment', 'void_core'][tier - 1],
                        'quantity': tier + 1},
                       {'item_id': material, 'quantity': 2 * tier}]
        combined = {}
        for entry in ingredients:
            key = entry['item_id']
            combined[key] = combined.get(key, 0) + entry['quantity']
        ingredients = [{'item_id': key, 'quantity': value} for key, value in combined.items()]
        fee = [150, 600, 1800][tier - 1]
        floor = sum(items[x['item_id']]['sell_price'] * x['quantity'] for x in ingredients) + fee
        memory = {
            'id': iid, 'name': 'Skill Memory : ' + name,
            'description': f'Unbound memory of {name}. Use on a selected learner to begin training; completing the learning quest unlocks level 1. Requires learner level {minimum}. Unused memories can be traded.',
            'type': 'SKILL_MEMORY', 'rarity': ['UNCOMMON', 'RARE', 'EPIC'][tier - 1],
            'level_requirement': minimum, 'equipment_slots': [],
            'stats_bonus': dict.fromkeys(['atk', 'def', 'hp', 'mp', 'agi', 'per'], 0),
            'special_effects': [{'type': 'start_skill_memory_learning', 'value': 1, 'skill_id': sid,
                                 'weapon_family': weapon, 'learning_victories': [3, 5, 8][tier - 1]}],
            'buy_price': 0, 'sell_price': floor // 4, 'max_stack': 20,
            'icon_image': 'materials/memory_fragment_chip.png',
            'tradable': True, 'bind_on_use': True, 'skill_memory_profile_id': sid,
        }
        recipe = {'recipe_id': rid, 'recipe_name': 'Inscribe ' + name, 'category': 'SKILL_MEMORY',
                  'crafting_station': 'MEMORY_PRESS', 'required_level': minimum,
                  'crafting_time_seconds': [15, 30, 60][tier - 1], 'crafting_cost': fee,
                  'craftable_by_npcs': [NPC], 'result': {'item_id': iid, 'quantity': 1},
                  'ingredients': ingredients}
        profiles.append({'skill_id': sid, 'item_id': iid, 'recipe_id': rid, 'tier': tier,
                         'min_learner_level': minimum, 'weapon_family': weapon,
                         'max_level': 10, 'scalable_special_effects': [e['type'] for e in specials if e['type'] in
                         ('shield_percent', 'grant_shield_scale_perception', 'direct_heal_scaling_perception')],
                         'learning_quest_template': 'learning', 'training_quest_template': 'training'})
        skills.append(skill)
        memories.append(memory)
        recipes.append(recipe)
    npc = {'npc_id': NPC, 'name': 'Ivara', 'title': 'Skill Artisan', 'role': 'CRAFTER',
           'faction': 'NEUTRAL', 'dialogue_tree': 'dialog_skill_artisan_ivara',
           'location': 'Central Spire Bazaar', 'region_id': 'CENTRAL_SPIRE_BAZAAR',
           'description': 'A memory engraver who turns combat echoes into transferable skill memories.',
           'actions': ['open_crafting'], 'available_services': ['CRAFT'],
           'greeting': 'A memory is a beginning, not mastery. What will you make your own?'}
    def option(text, next_node, action=None):
        result = {'text': text, 'next': next_node}
        if action:
            result['action'] = action
        return result
    back = [option('Back.', 'greet')]
    dialog = {'dialog_id': 'dialog_skill_artisan_ivara', 'npc_id': NPC, 'start_node': 'greet', 'nodes': [
        {'id': 'greet', 'text': npc['greeting'], 'options': [
            option('Craft a Skill Memory.', 'craft', 'open_crafting'),
            option('How do I learn a memory?', 'learn'), option('How many can I equip?', 'slots'),
            option('Tell me about mastery training.', 'train'), option('Check my training progress.', 'progress'),
            option('Can I sell a memory?', 'trade'), option('Leave.', 'exit', 'exit')]},
        {'id': 'craft', 'text': 'Bring memory chips, a stabilizer, and the essence of the technique. Stronger inscriptions need rarer materials and a larger engraving fee.', 'options': back},
        {'id': 'learn', 'text': 'Choose yourself or a companion before using the memory. It is consumed to begin that learner\'s quest. Win real battles with the required weapon, then return to an artisan. Only completion unlocks the skill at level one.', 'options': back},
        {'id': 'slots', 'text': 'Each learner has two memory slots, separate from class techniques. Certain passives may add slots. You may learn many memories and change your selection outside battle. An incompatible weapon disables its technique.', 'options': back},
        {'id': 'train', 'text': 'Mastery grows from level one to ten. Each new level needs its own training quest: meaningful uses, worthy victories, and an artisan\'s review. Your current mastery remains usable while training.', 'options': back},
        {'id': 'progress', 'text': 'Learning and training records belong to the chosen learner. Paused lessons can resume; they do not return the consumed memory. Your quest journal will track the objectives once lessons are available.', 'options': back},
        {'id': 'trade', 'text': 'An unused inscription is unbound and may be sold on the market. Once used, the lesson and all mastery belong to that learner. They cannot be transferred or sold.', 'options': back},
        {'id': 'exit', 'text': 'Keep your hands steady and your memories sharper.', 'options': []},
    ]}
    training = []
    for profile in profiles:
        skill = next(s for s in skills if s['id'] == profile['skill_id'])
        for level in range(2, 11):
            tier = profile['tier']
            training.append({
                'id': f"q_mem_train_{skill['id'][7:]}_{level}",
                'skill_id': skill['id'], 'from_level': level - 1, 'to_level': level,
                'tier': tier, 'weapon_family': profile['weapon_family'],
                'required_uses': 5 * level * tier,
                'required_victories': level + tier,
                'quest_giver': NPC, 'region': 'CENTRAL_SPIRE_BAZAAR',
                'objectives': ['meaningful_skill_uses', 'qualifying_victories', 'artisan_turn_in'],
                'binding': 'learner_snapshot_only_not_public_quest_catalog',
            })
    return {'schema_version': 1, 'status': 'data_ready_runtime_pending', 'skills': skills,
            'training_quests': training,
            'items': memories, 'recipes': recipes, 'profiles': profiles, 'npc': npc, 'dialogue': dialog}


def merge(existing, incoming, key):
    incoming_by_id = {x[key]: x for x in incoming}
    result = [incoming_by_id.pop(x[key], x) for x in existing]
    return result + list(incoming_by_id.values())


def expected_files(pack):
    skills, items, recipes = load('skill_list.json'), load('item_list.json'), load('crafting_recipes.json')
    npcs, dialogs, world = load('npc_list.json'), load('dialog_tree_master.json'), load('world_map_v4.json')
    items['items'] = merge(items['items'], pack['items'], 'id')
    recipes['recipes'] = merge(recipes['recipes'], pack['recipes'], 'recipe_id')
    for group in dialogs:
        group['dialogues'] = [x for x in group['dialogues'] if x.get('dialog_id') != pack['dialogue']['dialog_id']]
    dialogs[0]['dialogues'].append(pack['dialogue'])
    # Maintain counters according to their existing meaning (generic vs quest dialogs).
    meta = dialogs[0].get('meta', {})
    if 'npc_dialog_count' in meta:
        old_count = len(load('dialog_tree_master.json')[0]['dialogues'])
        delta = len(dialogs[0]['dialogues']) - old_count
        meta['npc_dialog_count'] += delta
        meta['total_count'] += delta
    def place(obj):
        if isinstance(obj, dict):
            if obj.get('id') == 'CENTRAL_SPIRE_BAZAAR' and 'npc_ids' in obj:
                obj['npc_ids'] = list(dict.fromkeys(obj['npc_ids'] + [NPC]))
            for value in obj.values():
                place(value)
        elif isinstance(obj, list):
            for value in obj:
                place(value)
    place(world)
    return {'skill_memory_contract.json': contract(), 'skill_memory_pack.json': pack,
            'skill_list.json': merge(skills, pack['skills'], 'id'), 'item_list.json': items,
            'crafting_recipes.json': recipes, 'npc_list.json': merge(npcs, [pack['npc']], 'npc_id'),
            'dialog_tree_master.json': dialogs, 'world_map_v4.json': world}


def validate(pack, files):
    def require(condition, message):
        if not condition:
            raise ValueError(message)
    for name, entries, key in [
        ('skills', files['skill_list.json'], 'id'), ('items', files['item_list.json']['items'], 'id'),
        ('recipes', files['crafting_recipes.json']['recipes'], 'recipe_id'),
        ('npcs', files['npc_list.json'], 'npc_id'),
    ]:
        ids = [x[key] for x in entries]
        require(len(ids) == len(set(ids)), 'Duplicate ' + name + ' IDs')
    require(all(len(pack[key]) == 20 for key in ('skills', 'items', 'recipes', 'profiles')), 'Expected 20 complete memory sets')
    expected_training = {(p['skill_id'], level): p for p in pack['profiles'] for level in range(2, 11)}
    require(len(pack['training_quests']) == 180, 'Expected 180 training quests')
    require(len({q['id'] for q in pack['training_quests']}) == 180, 'Duplicate training IDs')
    for quest in pack['training_quests']:
        profile = expected_training.pop((quest['skill_id'], quest['to_level']), None)
        require(profile is not None, 'Invalid training level or skill')
        require(quest['from_level'] == quest['to_level'] - 1, 'Training must be sequential')
        require(quest['tier'] == profile['tier'] and
                quest['required_uses'] == 5 * quest['to_level'] * profile['tier'] and
                quest['required_victories'] == quest['to_level'] + profile['tier'], 'Training requirements mismatch')
    items = {x['id']: x for x in files['item_list.json']['items']}
    drops = {d['itemId'] for monster in load('monster_master.json')['monsters']
             for d in monster.get('drop_item', [])}
    skills = {x['id']: x for x in pack['skills']}
    recipes = {x['recipe_id']: x for x in pack['recipes']}
    for profile in pack['profiles']:
        skill, item, recipe = skills[profile['skill_id']], items[profile['item_id']], recipes[profile['recipe_id']]
        require(profile['weapon_family'] in WEAPONS, 'Unknown weapon')
        require(skill['skill_memory_tier'] == profile['tier'], 'Training tier mismatch')
        require(skill['usage_requirements']['allowed_weapons'] == [profile['weapon_family']], 'Weapon mismatch')
        require(item['special_effects'][0]['skill_id'] == skill['id'], 'Memory skill mismatch')
        require(item['special_effects'][0]['weapon_family'] == profile['weapon_family'], 'Learning weapon mismatch')
        require(item['special_effects'][0]['learning_victories'] == [3, 5, 8][profile['tier'] - 1], 'Learning objective mismatch')
        require(recipe['result'] == {'item_id': item['id'], 'quantity': 1}, 'Recipe output mismatch')
        require(recipe['craftable_by_npcs'] == [NPC], 'Wrong artisan')
        require(item['type'] == 'SKILL_MEMORY' and item['tradable'] and item['bind_on_use'], 'Unsafe item contract')
        require((ROOT / item['icon_image']).is_file(), 'Missing icon')
        require(profile['max_level'] == 10, 'Invalid mastery cap')
        price = recipe['crafting_cost']
        for ingredient in recipe['ingredients']:
            material = items[ingredient['item_id']]
            require(material['type'] == 'MATERIAL', 'Ingredient is not a material')
            require(material['id'] in drops, 'Material has no monster drop source')
            require(ingredient['quantity'] > 0, 'Invalid ingredient amount')
            require(material['level_requirement'] <= recipe['required_level'], 'Material above recipe level')
            price += material['sell_price'] * ingredient['quantity']
        require(0 <= item['sell_price'] < price, 'Vendor arbitrage')
    nodes = {x['id'] for x in pack['dialogue']['nodes']}
    require(len(nodes) == len(pack['dialogue']['nodes']), 'Duplicate dialog nodes')
    require(pack['dialogue']['start_node'] in nodes, 'Missing start node')
    for node in pack['dialogue']['nodes']:
        for opt in node['options']:
            require(opt['next'] in nodes, 'Broken dialog link')
            require(opt.get('action') in (None, 'open_crafting', 'exit'), 'Unimplemented dialog action')
    require(pack['npc']['dialogue_tree'] == pack['dialogue']['dialog_id'], 'NPC dialog mismatch')
    require(pack['dialogue']['npc_id'] == NPC, 'Dialog owner mismatch')
    bazaar = [x for x in files['world_map_v4.json']['nodes'] if x['id'] == 'CENTRAL_SPIRE_BAZAAR']
    require(len(bazaar) == 1 and bazaar[0]['npc_ids'].count(NPC) == 1, 'Artisan not placed once in Bazaar')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    pack = build()
    files = expected_files(pack)
    validate(pack, files)
    if args.check:
        for name, value in files.items():
            if not (ROOT / name).exists() or load(name) != value:
                raise SystemExit('Catalog needs regeneration: ' + name)
    else:
        for name, value in files.items():
            if not (ROOT / name).exists() or load(name) != value:
                (ROOT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
    print('PASS: 20 skills, 20 memories, 20 recipes, 20 profiles, 180 training templates, artisan dialogue; activation pending.')


if __name__ == '__main__':
    main()
