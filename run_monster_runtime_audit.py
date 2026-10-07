#!/usr/bin/env python3
"""Run the unchanged real MonsterTemplate parser plus the real Dart combat core."""

import argparse
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dart", default="dart")
    parser.add_argument("--game-root", type=Path, default=ROOT.parent / "project-echo")
    args = parser.parse_args()
    source = (args.game_root / "lib/data/repositories/region_repository.dart").read_text(encoding="utf-8")
    # This standalone class has no Flutter dependencies. Keep its exact body;
    # importing the entire repository would pull in Flutter and network loaders.
    start = source.index("class MonsterTemplate {")
    end = source.index("\n}\n", start) + 3
    model = source[start:end]
    with tempfile.TemporaryDirectory(prefix="xylos-monster-audit-") as temp:
        folder = Path(temp)
        (folder / "monster_template.dart").write_text(model, encoding="utf-8")
        harness = folder / "monster_runtime_audit.dart"
        harness.write_text((ROOT / "tools/monster_runtime_audit.dart").read_text(encoding="utf-8"), encoding="utf-8")
        config = folder / "package_config.json"
        config.write_text(json.dumps({"configVersion": 2, "packages": [{
            "name": "echo_of_xylos", "rootUri": args.game_root.resolve().as_uri() + "/",
            "packageUri": "lib/", "languageVersion": "3.11",
        }]}), encoding="utf-8")
        result = subprocess.run([args.dart, f"--packages={config}", str(harness), str(ROOT)])
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
