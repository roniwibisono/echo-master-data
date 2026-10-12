# Equipment Type Contract

Weapon and accessory definitions use `WEAPON_{SUBTYPE}` and `ACCESSORY_{SUBTYPE}`.
Split after the first underscore; preserve the entire suffix. Compare uppercase
values. Never infer weapon family from item name, icon or item ID at runtime.

Examples: `WEAPON_SWORD`, `WEAPON_DAGGER`, `WEAPON_STAFF`, `WEAPON_SPEAR`,
`WEAPON_AXE`, `WEAPON_GREATSWORD`, `WEAPON_PISTOL`, `ACCESSORY_RING`,
`ACCESSORY_AMULET`, `ACCESSORY_BRACELET`, `ACCESSORY_BELT`, `ACCESSORY_PENDANT`.
Future content can explicitly use `WEAPON_KNUCKLE`, `WEAPON_ORB`, etc.
Subtypes match exactly; GREATSWORD is not silently treated as SWORD.

The migration changes 32 weapon and 59 accessory definitions, with five matching
relic definitions in the mystery manifest. It preserves IDs, stats, prices,
effects, icons and equipment slots. OFFHAND, armor and non-equipment types are
outside this migration; do not split TWO_HANDS or SKILL_MEMORY as generic types.

The client preserves the full serialized type and exposes category and subtype
separately. Category checks still accept legacy inventory types WEAPON/ACCESSORY.
For skill requirements, use the current master item definition's subtype rather
than an old persisted inventory copy. Bare legacy types have no known subtype.

Rebuild tools use explicit ID mappings, and unknown generic equipment fails
validation rather than receiving a guessed family. Historical audit/activation
snapshots remain unchanged. Future generators must emit typed equipment.

```sh
python3 tools/migrate_equipment_types.py
python3 tools/migrate_equipment_types.py --check
python3 -m unittest discover -s tools -p 'test_equipment_types.py'
```

Deploy the compatible client before publishing the new types to the CDN.
Older clients that compare type equality may otherwise stop recognizing gear.
