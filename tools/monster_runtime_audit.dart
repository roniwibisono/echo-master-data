import 'dart:convert';
import 'dart:io';
import 'dart:math';
import 'monster_template.dart';
import 'package:echo_of_xylos/data/models/skill.dart';
import 'package:echo_of_xylos/features/combat/engine/combat_engine.dart';
import 'package:echo_of_xylos/features/combat/engine/skill_library.dart';
import 'package:echo_of_xylos/features/combat/models/combatant.dart';

Combatant monsterActor(MonsterTemplate m, String id) {
  final s = m.baseStats;
  return Combatant(
    id: id,
    name: m.name,
    isPlayer: false,
    monsterId: m.monsterId,
    monsterCode: m.code,
    level: m.level,
    maxHp: s['hp']!,
    currentHp: (s['hp']! * 0.7).round(),
    maxMp: s['mp']!,
    currentMp: s['mp']!,
    atk: s['atk']!,
    def: s['def']!,
    agi: s['agi']!,
    per: s['per']!,
    skillIds: m.allSkillIds,
  )..aiBehavior = m.aiBehavior;
}

Combatant targetActor(String id) => Combatant(
  id: id,
  name: id,
  isPlayer: true,
  level: 60,
  currentHp: 1000000,
  maxHp: 1000000,
  currentMp: 300,
  maxMp: 300,
  atk: 100,
  def: 80,
  agi: 60,
  per: 100,
);

void main(List<String> args) {
  final root = args[0];
  final raw =
      jsonDecode(File('$root/monster_master.json').readAsStringSync()) as Map;
  final skillRows =
      jsonDecode(File('$root/skill_list.json').readAsStringSync()) as List;
  final skills = {
    for (final row in skillRows)
      row['id'] as String: Skill.fromJson(Map<String, dynamic>.from(row)),
  };
  final errors = <String>[];
  var parsed = 0, basics = 0, casts = 0;
  final observations = <Map<String, Object>>[];
  for (final row in raw['monsters'] as List) {
    try {
      final m = MonsterTemplate.fromJson(Map<String, dynamic>.from(row));
      parsed++;
      for (final sid in m.activeSkillIds) {
        final skill = skills[sid]!;
        final actor = monsterActor(m, 'monster');
        final partner = monsterActor(m, 'partner');
        final foes = [targetActor('player1'), targetActor('player2')];
        final engine = CombatEngine(Random(400));
        SkillLibrary.applyPassives(
          combatant: actor,
          passiveSkills: m.passiveSkillIds.map((id) => skills[id]!).toList(),
          engine: engine,
        );
        actor.statusEffects.add(
          ActiveStatusEffect(
            id: 'audit_unevadable',
            name: 'Audit',
            type: 'buff',
            category: 'unevadable',
            remainingTurns: 99,
          ),
        );
        if (actor.currentMp < skill.mpCost) {
          errors.add('${m.code}: unaffordable $sid');
          continue;
        }
        final selected = switch (SkillLibrary.primaryTargetKind(skill)) {
          SkillTargetKind.selfCast => [actor],
          SkillTargetKind.allySingle => [partner],
          SkillTargetKind.allyAll => [actor, partner],
          SkillTargetKind.enemySingle => [foes.first],
          SkillTargetKind.enemyAll => foes,
        };
        final hpBefore = actor.currentHp;
        final partnerHp = partner.currentHp;
        actor.currentMp -= skill.mpCost;
        final result = SkillLibrary.executeSkill(
          skill: skill,
          source: actor,
          targets: selected,
          allCombatants: [actor, partner, ...foes],
          engine: engine,
        );
        casts++;
        final intentionalCost = skill.specialEffects.any(
          (e) => ['self_hp_loss_percent', 'set_hp_to_value'].contains(e.type),
        );
        if ((actor.currentHp < hpBefore && !intentionalCost) ||
            partner.currentHp < partnerHp) {
          errors.add('${m.code}: $sid caused unexpected friendly damage');
        }
        final offensive =
            !['0', '', '-'].contains(skill.damageFormula.toString()) &&
            !['none', 'self'].contains(skill.targetAttack.toLowerCase());
        if (offensive && result.totalDamage <= 0)
          errors.add('${m.code}: $sid caused zero offensive damage');
        engine.processStatusTurnStart(actor);
        observations.add({
          'monster': m.code,
          'skill': sid,
          'damage': result.totalDamage,
          'healing': result.totalHealing,
          'remaining_mp': actor.currentMp,
        });
      }
      final actor = monsterActor(m, 'basic');
      actor.statusEffects.add(
        ActiveStatusEffect(
          id: 'audit_unevadable',
          name: 'Audit',
          type: 'buff',
          category: 'unevadable',
          remainingTurns: 99,
        ),
      );
      CombatEngine(
        Random(401),
      ).resolveAttack(attacker: actor, defender: targetActor('basic_target'));
      basics++;
    } catch (e) {
      errors.add('${row['code']}: $e');
    }
  }
  final report = {
    'monsters_parsed': parsed,
    'basic_attacks': basics,
    'active_skill_executions': casts,
    'errors': errors,
    'observations': observations,
    'limitations': [
      'MonsterTemplate is extracted verbatim from the actual game source.',
      'AI decisions, raid phase transitions, UI and complete resistance/scaling semantics are not exercised.',
    ],
  };
  File('$root/monster_runtime_validation.json').writeAsStringSync(
    '${const JsonEncoder.withIndent('  ').convert(report)}\n',
  );
  stdout.writeln(
    '$parsed monsters, $basics basic attacks, $casts skill executions: ${errors.length} errors',
  );
  for (final error in errors.take(20)) {
    stdout.writeln(error);
  }
  if (errors.isNotEmpty) exitCode = 1;
}
