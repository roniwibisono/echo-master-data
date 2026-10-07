#!/usr/bin/env python3
"""Run the real pure-Dart combat engine without requiring the Flutter SDK."""

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
    if not (args.game_root / "lib/features/combat/engine/skill_library.dart").exists():
        parser.error("game source not found; pass --game-root")
    with tempfile.TemporaryDirectory(prefix="xylos-combat-audit-") as temp:
        config = Path(temp) / "package_config.json"
        config.write_text(json.dumps({"configVersion": 2, "packages": [{
            "name": "echo_of_xylos", "rootUri": args.game_root.resolve().as_uri() + "/",
            "packageUri": "lib/", "languageVersion": "3.11",
        }]}), encoding="utf-8")
        result = subprocess.run([args.dart, f"--packages={config}", str(ROOT / "tools/combat_runtime_audit.dart"), str(ROOT)])
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
