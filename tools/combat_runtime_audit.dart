// Run through run_combat_runtime_audit.py to resolve the actual game sources.
import 'dart:convert';
import 'dart:io';
import 'dart:math';
import 'package:echo_of_xylos/data/models/skill.dart';
import 'package:echo_of_xylos/data/models/character_class.dart';
import 'package:echo_of_xylos/features/combat/engine/combat_engine.dart';
import 'package:echo_of_xylos/features/combat/engine/skill_library.dart';
import 'package:echo_of_xylos/features/combat/engine/effects/effect_registry.dart';
import 'package:echo_of_xylos/features/combat/engine/effects/effect_handler.dart';
import 'package:echo_of_xylos/features/combat/models/combatant.dart';

Combatant actor(String id, bool player, {Map<String, dynamic>? stats}) {
  final hp = stats?['hp'] as int? ?? 1000;
  final mp = stats?['mp'] as int? ?? 250;
  return Combatant(
    id: id,
    name: id,
    isPlayer: player,
    level: 60,
    currentHp: (hp * 0.45).round(),
    maxHp: hp,
    currentMp: mp,
    maxMp: mp,
    atk: stats?['atk'] as int? ?? 100,
    def: stats?['def'] as int? ?? 80,
    agi: stats?['agi'] as int? ?? 60,
    per: stats?['per'] as int? ?? 110,
  );
}

Map<String, Object> snapshot(Combatant c) => {
  'hp': c.currentHp,
  'maxHp': c.maxHp,
  'mp': c.currentMp,
  'shield': c.shield,
  'atk': c.effectiveAtk,
  'def': c.effectiveDef,
  'agi': c.effectiveAgi,
  'crit': c.effectiveCritBonus,
  'statuses': c.statusEffects.length,
};

List<Combatant> targets(
  Skill skill,
  List<Combatant> team,
  List<Combatant> foes,
) {
  return switch (SkillLibrary.primaryTargetKind(skill)) {
    SkillTargetKind.selfCast => [team.first],
    SkillTargetKind.allySingle => [team.last],
    SkillTargetKind.allyAll => team,
    SkillTargetKind.enemySingle => [foes.first],
    SkillTargetKind.enemyAll => foes,
  };
}

void main(List<String> args) {
  final root = args[0];
  final skills =
      (jsonDecode(File('$root/skill_list.json').readAsStringSync()) as List)
          .map((row) => Skill.fromJson(Map<String, dynamic>.from(row)))
          .toList();
  final classes =
      (jsonDecode(File('$root/class_list.json').readAsStringSync()) as List)
          .map((row) => CharacterClass.fromJson(Map<String, dynamic>.from(row)))
          .toList();
  final roster =
      jsonDecode(File('$root/ally_list.json').readAsStringSync()) as Map;
  final lookup = {for (final skill in skills) skill.id: skill};
  final errors = <String>[];
  final warnings = <String>[];
  final observations = <Map<String, Object>>[];
  final regressionChecks = <String>[];
  final semanticFindings = <Map<String, Object>>[];
  initEffectHandlers();
  final registry = EffectHandlerRegistry.instance;
  for (final skill in skills) {
    try {
      final team = [actor('caster', true), actor('partner', true)];
      final foes = [
        actor('enemy1', false),
        actor('enemy2', false),
        actor('enemy3', false),
      ];
      final caster = team.first;
      caster.lastDamageTaken = 60;
      caster.statusEffects.add(
        ActiveStatusEffect(
          id: 'audit_hit',
          name: 'Audit',
          type: 'buff',
          category: 'unevadable',
          remainingTurns: 99,
        ),
      );
      final engine = CombatEngine(Random(1701));
      final before = snapshot(caster);
      final friendlyHp = {for (final c in team) c.id: c.currentHp};
      SkillExecResult? result;
      if (skill.type == 'Passive') {
        SkillLibrary.applyPassives(
          combatant: caster,
          passiveSkills: [skill],
          engine: engine,
        );
      } else {
        result = SkillLibrary.executeSkill(
          skill: skill,
          source: caster,
          targets: targets(skill, team, foes),
          allCombatants: [...team, ...foes],
          engine: engine,
        );
      }
      for (final effect in skill.specialEffects) {
        if (!registry.hasHandler(effect.type.toLowerCase()) &&
            !registry.isNoOp(effect.type.toLowerCase())) {
          warnings.add('${skill.id}: unregistered ${effect.type}');
        }
      }
      if (skill.type == 'Passive' &&
          jsonEncode(before) == jsonEncode(snapshot(caster))) {
        warnings.add(
          '${skill.id}: passive has no observable application at 45% HP',
        );
      }
      final intentionalSelfCost = skill.specialEffects.any(
        (e) => ['self_hp_loss_percent', 'set_hp_to_value'].contains(e.type),
      );
      for (final ally in team) {
        if (ally.currentHp < friendlyHp[ally.id]! &&
            !(ally == caster && intentionalSelfCost)) {
          errors.add('${skill.id}: damaged friendly ${ally.id}');
        }
      }
      final offensive =
          skill.type == 'Active' &&
          skill.targetAttack.toLowerCase() != 'none' &&
          skill.targetAttack.toLowerCase() != 'self' &&
          !['0', '', '-'].contains(skill.damageFormula.toString());
      if (offensive && (result?.totalDamage ?? 0) <= 0) {
        errors.add('${skill.id}: offensive formula dealt zero damage');
      }
      observations.add({
        'id': skill.id,
        'damage': result?.totalDamage ?? 0,
        'healing': result?.totalHealing ?? 0,
        'after': snapshot(caster),
      });
    } catch (e) {
      errors.add('${skill.id}: runtime exception $e');
    }
  }
  for (final cls in classes) {
    for (final id in cls.learnableSkillIds) {
      if (!lookup.containsKey(id))
        errors.add('${cls.id}: skill $id failed model lookup');
    }
  }
  for (final raw in roster['allies'] as List) {
    final stats = Map<String, dynamic>.from(raw['base_stats'] as Map);
    final passive = lookup[raw['passive_skill']['skill_id']];
    final active = lookup[raw['active_skill']['skill_id']];
    if (passive == null || active == null) {
      errors.add('${raw['ally_id']}: missing runtime skill');
      continue;
    }
    try {
      final team = [
        actor(raw['ally_id'], true, stats: stats),
        actor('partner', true),
      ];
      final foes = [actor('enemy1', false), actor('enemy2', false)];
      final engine = CombatEngine(Random(700));
      SkillLibrary.applyPassives(
        combatant: team.first,
        passiveSkills: [passive],
        engine: engine,
      );
      if (team.first.currentMp < active.mpCost)
        errors.add('${raw['ally_id']}: cannot afford active after passives');
      team.first.currentMp -= active.mpCost;
      SkillLibrary.executeSkill(
        skill: active,
        source: team.first,
        targets: targets(active, team, foes),
        allCombatants: [...team, ...foes],
        engine: engine,
      );
      engine.processStatusTurnStart(team.first);
    } catch (e) {
      errors.add('${raw['ally_id']}: roster execution exception $e');
    }
  }
  void check(String label, bool passed) {
    if (passed) {
      regressionChecks.add(label);
    } else {
      errors.add('Regression failed: $label');
    }
  }

  // Numeric regression checks exercise the handlers, not a duplicate formula
  // evaluator. Use wounded allies so healing cannot hide behind max-HP clamping.
  final regenCaster = actor('regen', true);
  regenCaster.currentMp = 100;
  final regenHp = regenCaster.currentHp;
  final regenEngine = CombatEngine(Random(9));
  SkillLibrary.applyPassives(
    combatant: regenCaster,
    passiveSkills: [lookup['sk_channeler_pas']!],
    engine: regenEngine,
  );
  regenEngine.processStatusTurnStart(regenCaster);
  check(
    'Channeler restores exactly 5% MP without unintended HP regeneration',
    regenCaster.currentMp == 113 && regenCaster.currentHp == regenHp,
  );

  final healer = actor('healer', true);
  final healPartner = actor('heal_partner', true);
  final healFoe = actor('heal_enemy', false);
  final healEngine = CombatEngine(Random(10));
  SkillLibrary.executeSkill(
    skill: lookup['al_lyra_act']!,
    source: healer,
    targets: [healer, healPartner],
    allCombatants: [healer, healPartner, healFoe],
    engine: healEngine,
  );
  check(
    'Lyra party heal uses PER * 2 rather than 2% maximum HP',
    healer.currentHp == 670 &&
        healPartner.currentHp == 670 &&
        healFoe.currentHp == 450,
  );
  healEngine.processStatusTurnStart(healer);
  check('Lyra regeneration restores 4% maximum HP', healer.currentHp == 710);

  final solas = actor('solas', true);
  final solasPartner = actor('solas_partner', true);
  SkillLibrary.executeSkill(
    skill: lookup['al5_91_act']!,
    source: solas,
    targets: [solas, solasPartner],
    allCombatants: [solas, solasPartner],
    engine: CombatEngine(Random(11)),
  );
  check(
    'Solas applies one 35% party heal rather than duplicate 15% + 35% heals',
    solas.currentHp == 800 && solasPartner.currentHp == 800,
  );

  final rex = actor('rex', true);
  SkillLibrary.applyPassives(
    combatant: rex,
    passiveSkills: [lookup['al_rex_pas']!],
    engine: CombatEngine(Random(12)),
  );
  check(
    'Rex damage-cap handler receives 20% rather than 0.2%',
    rex.statusEffects.any(
      (s) =>
          s.category == 'damage_cap' &&
          (s.periodicScale - 0.2).abs() < 0.000001,
    ),
  );
  final lyra = actor('lyra', true);
  SkillLibrary.applyPassives(
    combatant: lyra,
    passiveSkills: [lookup['al_lyra_pas']!],
    engine: CombatEngine(Random(13)),
  );
  check(
    'Lyra healing amplifier handler receives 20% rather than 0.2%',
    lyra.statusEffects.any(
      (s) =>
          s.id.endsWith('_heal_bonus') &&
          (s.periodicScale - 0.2).abs() < 0.000001,
    ),
  );

  // Retain evidence for client behavior that a JSON-only correction cannot
  // safely repair without changing skill identities or player targeting.
  final singleCaster = actor('single_caster', true);
  final singlePartner = actor('single_partner', true);
  SkillLibrary.executeSkill(
    skill: lookup['al4_57_act']!,
    source: singleCaster,
    targets: [singlePartner],
    allCombatants: [singleCaster, singlePartner],
    engine: CombatEngine(Random(14)),
  );
  semanticFindings.add({
    'id': 'ally_single_target_resolution',
    'skill': 'al4_57_act',
    'selected': singlePartner.id,
    'healed': [
      for (final c in [singleCaster, singlePartner])
        if (c.currentHp > 450) c.id,
    ],
    'note': 'The current effect resolver broadens ally to the entire party.',
  });
  final report = {
    'skills': skills.length,
    'classes': classes.length,
    'allies': (roster['allies'] as List).length,
    'errors': errors,
    'warnings': warnings.toSet().toList(),
    'observations': observations,
    'regression_checks': regressionChecks,
    'client_semantic_findings': semanticFindings,
  };
  File('$root/combat_runtime_validation.json').writeAsStringSync(
    '${const JsonEncoder.withIndent('  ').convert(report)}\n',
  );
  stdout.writeln(
    '${skills.length} skills + ${classes.length} classes + ${(roster['allies'] as List).length} ally executions: '
    '${errors.length} errors, ${regressionChecks.length} regression checks, ${warnings.toSet().length} runtime observations',
  );
  for (final error in errors.take(30)) {
    stdout.writeln('ERROR $error');
  }
  if (errors.isNotEmpty) exitCode = 1;
}
