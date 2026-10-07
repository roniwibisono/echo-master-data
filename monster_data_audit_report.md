# Monster Master Audit - 2026-10-08

## Status

Audit mencakup 187 monster awal, parser game, skill, item, map aktif,
biome mapping, dungeon dan raid. Katalog setelah koreksi: **189 monster**.
Validasi referensi/nilai: **0 error, 68 warning**. Tidak ada claim bahwa semua
monster sudah reachable atau semua field combat sudah berfungsi di client.
Audit awal menemukan 31 error referensi dan 170 warning; baseline lengkap
tersimpan di `monster_data_validation_before.json`.
Pemeriksaan tambahan terhadap quest menemukan **8 target kill tanpa definisi**.
Jumlah 0 error di atas hanya untuk record monster dan referensi world/biome/
dungeon/raid, bukan seluruh quest. Temuan quest belum dikoreksi.

Perubahan hanya memperbaiki referensi, label lokasi dan AI fallback yang
terverifikasi, serta mengisi dua template dungeon yang memang direferensikan.
Stat, level, rank, scaling, crit dan reward numerik monster lama tidak diubah.
Perubahan lokal lain yang sudah ada tidak dibatalkan. Tidak ada commit/push.

## Hasil Pemeriksaan

| Bagian | Hasil |
| --- | --- |
| Monster | 189 ID/code unik |
| Skill aktif / passive | 305 / 201 referensi valid dan tipe benar |
| Skill fase boss | 25 referensi valid, termasuk skill yang dipakai ulang |
| Drop dan special reward | 352 referensi item valid |
| World spawn | 234 referensi valid, cocok dengan lokasi monster |
| Dungeon / raid | 3 / 8 referensi monster valid |
| Mapping biome | 44 mapping, 219 referensi monster valid |
| Numeric | Stat/scaling/reward finite, integer sesuai parser, crit/chance 0-1 |

Race monster merupakan taxonomy monster tersendiri (52 kode), bukan foreign
key ke playable race; tidak dihapus karena tidak ada di `master_race.json`.
Elemen/resistance tetap sesuai sumber: client belum memakai semua field ini.
Chance drop adalah roll independen per item; total chance satu tabel tidak
harus 100%. Bobot spawn world adalah bobot relatif; hanya bobot biome yang
dituliskan sebagai probability dan harus berjumlah 1.

## Perbaikan

- Ashen Drake: referensi fase `flame_prison` yang tidak ada diganti dengan
  `inferno_breath` yang sudah terpasang. Threshold fase ketiga disamakan
  menjadi 0.25 sesuai `raid_dragon_nest`, bukan 0.30.
- Tujuh boss berpola fase mendapat `ai_pattern.behavior` eksplisit yang
  dikenali AI client. Detail fase lama tetap dipertahankan, bukan dihapus.
- Siege Reaper: behavior yang belum dikenali menjadi `aggressive_hunter`.
  Drop yang tidak terdefinisi diganti tanpa mengubah chance: plasma emitter
  -> `overheated_reactor_part` (0.40), hydraulic frame ->
  `hydraulic_piston_fragment` (0.35), reactor core -> `power_regulator_core`
  (0.20). Semua material sesuai tier awal monster level 12.
- 74 monster lama mendapat lokasi canonical tanpa alias duplikat/label lama
  ketika destination map/dungeon-nya dapat diverifikasi. Lokasi dummy
  termasuk dalam jumlah tersebut dan mengikuti region raid, `NEXUS_CORE`.
- Mapping biome disusun dari spawn table `world_map_v4.json`, termasuk bobot
  agregat yang dinormalisasi. 21 ID hilang (25 kemunculan) tidak lagi dirujuk.
  Biome/capital tanpa spawn tidak diberi monster secara sembarang; mapping
  kosong berarti tidak ada spawn. 13 mapping tambahan menutup biome aktif.
- Dungeon Crystal Depths sudah merujuk ID 6001 dan 6002, tetapi definisinya
  tidak ada di source maupun Supabase. Dua template ditambahkan pada ID itu,
  memakai skill/item yang sudah tersedia. Tidak ada ID dungeon yang diganti.

| ID | Monster | Level / HP / MP | ATK / DEF / AGI / PER |
| --- | --- | --- | --- |
| 6001 | Crystal Depths Sentry | 40 / 7200 / 450 | 420 / 400 / 40 / 55 |
| 6002 | Crystal Depths Skitter | 42 / 5400 / 320 | 480 / 280 / 65 / 45 |

Sentry memakai Crystal Armor + Crystal Puncture; Skitter memakai Crystal
Carapace + Shard Spike. Keduanya hanya ditempatkan pada `crystal_depths`,
bukan dimasukkan ke spawn world. Stat lebih rendah daripada boss level 45;
reward CRD dibatasi 5 per monster. Tuning wave/party memerlukan playtest.
Art CDN untuk dua code baru belum dibuat/diverifikasi.

Detail sebelum/sesudah ada di `monster_audit_20261008_changes.json`:
79 monster lama berubah pada field terpilih, dan dua record baru.

## Temuan Tersisa

1. **8 target kill quest netral tidak punya definisi monster.** Dari 711 link,
   703 cocok dengan ID atau code monster, dan seluruh target yang dikenal
   memiliki encounter aktif. Target yang hilang adalah `ROGUE_ARMS_DEALER`,
   `SHADOW_ENFORCER`, `ROGUE_CUSTODIAN_COMMANDER`, `BORDER_RAIDER`,
   `FORGE_GUARD_ELITE`, `ECONOMIC_SPECULATOR_SQUAD`, `SUMMIT_DISRUPTOR`, dan
   `ASSASSIN_ELITE`. Tidak ada alias target ini yang ditemukan di kode game.
   Perlu definisi + encounter atau redesign objective; mengganti commander
   Custodian menjadi guard faction lain bisa merusak cerita. Detail quest ID
   ada di `monster_quest_validation.json`. Tidak ada edit pada quest netral.
2. **38 lokasi legacy belum berada di map/dungeon aktif.** Contoh: Dungeon A,
   Dessert of Nadir, Veldt Savannah, Infested Flesh Pits dan Collapsed Assembly
   Yard. Monster terkait juga tidak dirujuk encounter world/dungeon/raid yang
   diaudit. Mereka dipertahankan sebagai template, tidak dipindahkan ke map
   baru tanpa desain encounter. Data rinci dan daftar template ada pada
   `monster_data_validation.json`. Ini bukan bukti tidak dipakai sistem lain.
3. **30 spawn monster normal berada di luar level_range region.** Contoh:
   Aethel Wisp level 7 di starter 1-5, serta Aethel Void Channeler level 40 di
   Aethel Siphon Core 70-90. Monster dipakai lintas region, jadi mengubah satu
   level global akan memengaruhi banyak encounter. Perlu keputusan tentang
   range rekomendasi, varian monster atau scaling per region. Tidak ada rebalance
   global/teleport spawn yang dilakukan sebagai koreksi otomatis.

## Batasan Client

- [Parser AI](/Users/rnddev/Documents/project-echo/lib/data/repositories/region_repository.dart:293) hanya
  mengambil satu behavior dari `ai_pattern`. Phase 2/3, HP threshold dan bonus
  stat dalam monster JSON tidak diteruskan ke MonsterTemplate. Menambahkan
  behavior membantu fallback, tetapi tidak mengaktifkan transisi fase.
- [LootService](/Users/rnddev/Documents/project-echo/lib/core/services/loot_service.dart:56) memakai `drop_item`,
  bukan `special_reward`. Parser menyimpan special_reward, tetapi tidak ada
  consumer distribusinya yang ditemukan. Jangan menganggap token/blueprint
  special sudah bisa diperoleh dari kill hanya karena item ID valid.
- [Factory enemy](/Users/rnddev/Documents/project-echo/lib/features/explore/pages/explore_page_v4.dart:3373)
  hanya meneruskan stat/skill. Crit/scaling template tidak diteruskan; element,
  resistance, weakness dan immunity dari monster juga tidak masuk model ringan.
  Menyetel nilai JSON saja tidak cukup untuk mengaktifkan mekanik tersebut.
- Masalah resolver target dan aura passive dari audit skill sebelumnya tetap
  berlaku. Tidak ada perubahan kode game pada audit ini.

## Uji dan Publikasi

```bash
python3 audit_monster_data.py
python3 audit_monster_data.py --check-quests
python3 -m unittest discover -s tests -p 'test_*data_audit.py' -v
python3 run_monster_runtime_audit.py --dart /path/to/dart
python3 verify_monster_supabase_seeds.py
python3 audit_combat_data.py
python3 validate_data.py
```

18 unit test (8 monster + 10 combat) lolos. Harness menggunakan body
MonsterTemplate asli yang diekstrak tanpa perubahan dari repository game,
serta model skill dan engine combat asli. 189 parser, 189 basic attack dan
305 eksekusi active skill pada stat monster nyata lolos tanpa exception,
MP tak terjangkau atau friendly damage yang tidak disengaja. Ini smoke test,
bukan pengujian lengkap AI/raid phase, UI, balance atau setiap semantik efek.
Full Flutter/UI tidak diuji karena SDK yang dikonfigurasi belum tersedia.
Flag `--check-quests` sengaja mengembalikan exit 1 selama delapan target
quest yang hilang belum ditangani; validasi record monster sendiri exit 0.

Full monster seed, tiga chunk dan `apply_all.sql` telah diregenerasi.
Importer sekarang menolak error audit sebelum mengganti seed. Jumlah
warning tidak menjadi alasan menghapus template legacy secara otomatis.

Patch khusus `supabase/seed/monster_audit_20261008.sql` berisi 79 field-scoped
UPDATE dan dua INSERT/upsert. Patch lolos validasi transaksi Supabase dengan
integrity assertions, lalu **ROLLBACK**. **Belum diterapkan permanen**:
database setelah rollback masih 187 monster, tanpa 6001/6002, dan tiga drop
Siege Reaper masih tidak terdefinisi. Tidak ada perubahan schema/save pemain.
Status dicatat dalam `monster_supabase_validation.json`.

Untuk database yang sudah berjalan, jalankan delta khusus tersebut lalu cek
tiga kolom verification semuanya nol. Tidak perlu menjalankan bundle seluruh
domain sebagai content update. Biome mapping tetap file CDN, sehingga
`monster_master.json` dan `biome_monster_mapping.json` perlu dipublikasikan ke
Git/CDN dan cache game di-refresh. Delta audit item terpisah tetap mengikuti
urutan/instruksi audit item; patch monster ini tidak menggantikannya.
