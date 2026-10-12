#!/usr/bin/env python3
"""Exercise actual client JSON parsers and combat core without altering the client."""

import argparse
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dart', default='dart')
    parser.add_argument('--game-root', type=Path, default=ROOT.parent / 'project-echo')
    args = parser.parse_args()
    game = args.game_root
    def source(name):
        return (game / name).read_text(encoding='utf-8')
    region_source = source('lib/data/repositories/region_repository.dart')
    regions = region_source[region_source.index('class WorldRegion {'):region_source.index('/// Monster data')]
    title_source = source('lib/data/repositories/title_repository.dart')
    title_model = title_source[title_source.index('class TitleData {'):title_source.index('  bool isUnlocked(')] + '}\n'
    with tempfile.TemporaryDirectory(prefix='xylos-mystery-runtime-') as temp:
        folder = Path(temp)
        for filename, content in {
            'quest.dart': source('lib/data/models/quest_data.dart'),
            'dialog.dart': source('lib/data/models/dialog_data.dart'),
            'npc.dart': source('lib/data/models/npc_data.dart'),
            'item.dart': source('lib/data/models/crafting_data.dart'),
            'achievement.dart': source('lib/data/models/achievement.dart'),
            'region.dart': regions, 'title.dart': title_model,
        }.items():
            (folder / filename).write_text(content)
        harness = folder / 'parser_test.dart'
        harness.write_text("""import 'dart:convert';
import 'dart:io';
import 'quest.dart';
import 'dialog.dart';
import 'npc.dart';
import 'item.dart';
import 'achievement.dart';
import 'region.dart';
import 'title.dart';
void main(List<String> args) {
  final root = args.first;
  final manifest = jsonDecode(File('$root/narrative/mystery_manifest.json').readAsStringSync()) as Map<String, dynamic>;
  final rows = manifest['records'] as Map<String, dynamic>;
  final errors = <String>[];
  final counts = <String, int>{};
  for (final r in rows['quests']) {
    final q = QuestTemplate.fromJson(Map<String, dynamic>.from(r));
    final p = PlayerQuestProgress(questId: q.id);
    p.initProgress(q.objectives.length);
    if (p.isComplete(q.objectives)) errors.add('${q.id}: empty progress already complete');
    for (var i = 0; i < q.objectives.length; i++) { p.objectiveProgress[i] = q.objectives[i].count; }
    if (!p.isComplete(q.objectives)) errors.add('${q.id}: full progress not complete');
    if (!PlayerQuestProgress.fromJson(p.toJson()).isComplete(q.objectives)) errors.add('${q.id}: serialization drift');
    counts['quests'] = (counts['quests'] ?? 0) + 1;
  }
  for (final r in rows['npcs']) { NpcData.fromJson(Map<String, dynamic>.from(r)); }
  for (final r in rows['items']) { final i = ItemInfo.fromJson(Map<String, dynamic>.from(r)); if (i.type == 'ACCESSORY' && !i.isEquippable) errors.add('${i.id}: not equippable'); }
  for (final r in rows['regions']) { WorldRegion.fromJson(Map<String, dynamic>.from(r)); }
  for (final r in rows['dialogs']) { final d = DialogTree.fromJson(Map<String, dynamic>.from(r)); if (!d.nodes.containsKey(d.startNode)) errors.add('${d.dialogId}: missing start'); }
  for (final r in rows['titles']) { final t = TitleData.fromJson(Map<String, dynamic>.from(r)); if (t.statBonus.isNotEmpty) errors.add('${t.id}: unplanned stacking stats'); }
  final achievementKey = rows.containsKey('achievements') ? 'achievements' : 'pending_achievements';
  for (final r in rows[achievementKey]) { final a = Achievement.fromJson(Map<String, dynamic>.from(r)); if (a.satisfiedBy(0) || !a.satisfiedBy(1)) errors.add('${a.id}: threshold'); }
  for (final k in ['npcs', 'items', 'regions', 'dialogs', 'titles', achievementKey]) { counts[k] = (rows[k] as List).length; }
  final report = {'parser_counts': counts, 'errors': errors, 'limitations': ['JSON parser smoke tests only; discovery, choice persistence, ordered interactions, UI, and achievement metric production are not implemented or tested. Title factory is extracted verbatim; its player-dependent unlock evaluator is not executed.']};
  File('$root/narrative/mystery_runtime_validation.json').writeAsStringSync('${const JsonEncoder.withIndent('  ').convert(report)}\\n');
  print('${counts['quests']} quests and all supporting records parsed: ${errors.length} errors');
  if (errors.isNotEmpty) exitCode = 1;
}
""")
        subprocess.run([args.dart, str(harness), str(ROOT)], check=True)
        # Reuse the existing combat harness against only this pack's monsters.
        manifest = json.loads((ROOT / 'narrative/mystery_manifest.json').read_text())
        (folder / 'monster_master.json').write_text(json.dumps({'monsters': manifest['records']['monsters']}))
        (folder / 'skill_list.json').write_bytes((ROOT / 'skill_list.json').read_bytes())
        start = region_source.index('class MonsterTemplate {')
        end = region_source.index('\n}\n', start) + 3
        (folder / 'monster_template.dart').write_text(region_source[start:end])
        (folder / 'monster_runtime_audit.dart').write_bytes((ROOT / 'tools/monster_runtime_audit.dart').read_bytes())
        config = folder / 'package_config.json'
        config.write_text(json.dumps({'configVersion': 2, 'packages': [{
            'name': 'echo_of_xylos', 'rootUri': game.resolve().as_uri() + '/', 'packageUri': 'lib/', 'languageVersion': '3.11'}]}))
        subprocess.run([args.dart, f'--packages={config}', str(folder / 'monster_runtime_audit.dart'), str(folder)], check=True)
        (ROOT / 'narrative/mystery_combat_validation.json').write_bytes((folder / 'monster_runtime_validation.json').read_bytes())


if __name__ == '__main__':
    main()
