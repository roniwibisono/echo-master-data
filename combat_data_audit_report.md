# Combat Data Audit - 2026-10-08

## Status

Audit dan koreksi master data selesai. Patch konten sudah diterapkan ke
Supabase project `fbntgtzimydjhuwedrjz`, setelah validasi transaksi dengan
rollback. Data skill lokal dan database cocok secara semantik, tidak termasuk
metadata database (`updated_at`, `sort_order`). Belum ada commit/push untuk
perubahan audit ini. Publikasi JSON ke Git/CDN masih diperlukan untuk client
yang membaca master data dari CDN.

Ini bukan jaminan bahwa seluruh mekanik skill sudah berfungsi sempurna di
client. Temuan engine yang tidak bisa diperbaiki hanya lewat JSON dicatat di
bawah. Repository game diperiksa tanpa mengubah kode atau perubahan lokalnya.

## Cakupan

| Pemeriksaan | Hasil |
| --- | --- |
| Class / skill / ally | 40 / 689 / 91 |
| Referensi skill class | 123 valid, seluruh Class_Tree bisa dipelajari |
| Referensi skill ally | 182 valid, tipe/source benar, MP terjangkau |
| Referensi race/genus | 74 valid |
| Skill unik yang direferensikan monster | 221 valid |
| Deskripsi kosong di Supabase | 399 menjadi 0 |
| Effect kosong di Supabase | 102 menjadi 0 |
| Perbedaan semantik skill JSON vs Supabase | 0 |

Ally diperiksa untuk ID/code unik, nama, role, rarity, story, origin, affinity,
enam base stat, level cap, recruit cost, pvp_scale, draft cost dan skill.
Tidak ada perubahan nilai atau format `ally_list.json`: roster valid, masalah
utamanya berada di definisi skill. Origin/story tetap teks naratif, bukan
foreign key map. Audit ini tidak membuktikan semua pernyataan lore dalam teks.

## Koreksi Data

- Dreadnought: `sk_dread_act_2` diganti dengan ID yang ada `sk_dread_act_3`;
  ultimate ikut ditautkan dan eligibility diperbaiki.
- Warlord: `sk_war_act_2` menjadi `sk_warlord_act_2`; skill ketiga dan ultimate
  yang sebelumnya tidak bisa dipelajari ikut ditautkan.
- Ravager: `sk_rav_pas` menjadi `sk_rav_pas_1`, minimum level diselaraskan.
- Dua skill Chronovore yang salah memakai source Class_Tree menjadi Race.
- Passive Dreadnought/Sentinel yang hanya berupa teks mendapat payload DEF.
- 41 passive monster yang salah bertipe Active dikoreksi berdasarkan slot
  monster, dengan payload defensif/sustain yang didukung engine.
- Spore Cloud aktif dipertahankan. Passive Wild Mushroom mendapat ID terpisah
  `spore_cloud_aura`, sehingga tidak ada satu skill dengan dua tipe berbeda.
- Target serangan monster tanpa target diperbaiki supaya tidak menyerang diri
  sendiri. Legacy effect/type, durasi, probability CC, formula kosong/list
  dan deskripsi kosong dinormalisasi tanpa mengganti format utama JSON.
- 14 skill memakai satuan persen yang salah untuk handler-nya: nilai seperti
  `0.2` menjadi `20` ketika handler membagi 100. Chance/factor yang memang
  memakai rasio tidak diubah.
- Heal Myste tidak lagi punya payload duplikat. Solas melakukan satu party
  heal 35% + cleanse; klaim revive dihapus karena payload bukan revival.
- Narra sebagai Healer kini punya heal PER * 1.5 selain cleanse.
- Channeler hanya meregenerasi MP 5%, tanpa HP regen/MP regen duplikat.
- Tujuh nama skill dan pengaturan tiga target Kythari yang sudah diperbaiki
  di Supabase dipertahankan dan dibawa kembali ke JSON.

Detail per field sebelum/sesudah ada di `combat_data_changes.json`:
686 record skill (termasuk satu baru), tiga class dan satu monster.
Skill monster placeholder yang sebelumnya kosong mendapat basic attack
ATK * 1.5; ini fallback playable, bukan redesign mekanik khas tiap monster.

## Balance

Perubahan konservatif menekan burst/MP yang menonjol, bukan meratakan rarity.
Cooldown tidak dijadikan satu-satunya pembatas karena model combat saat ini
tidak membaca `cooldown_seconds`.

| Skill | Sebelum | Sesudah |
| --- | --- | --- |
| Vael Black Tide | ATK * 2.5 x 3, AoE, 38 MP | ATK * 1.05 x 3, 45 MP |
| Tide Riptide | ATK * 1.5 x 2, 16 MP | ATK * 0.85 x 2, 18 MP |
| Serin Swarm Blitz | ATK * 1.2 x 3, 16 MP | ATK * 0.65 x 3, 18 MP |
| Desperado Coin Toss | Guaranteed crit, 10 MP | 25 MP |
| Axiom Sniper Protocol | 20 MP, ignore_def=1 | 32 MP, ignore_def=30% |
| Bioengineer Rage Injection | ATK +100% | ATK +40%, 2 turns |

Formula Hekaton multi-hit diratakan menjadi tiga hit yang masing-masing
`40 + (ATK * 0.65 / 3)`. Total raw damage tetap `120 + ATK * 0.65` sebelum
pembulatan; distribusi hit berubah agar formula valid dalam kolom TEXT.
PvP scale, draft budget, level cap, recruit cost dan base stat ally tidak
diubah. Balance final masih membutuhkan playtest PvE/PvP pada client nyata.

## Verifikasi

```bash
python3 audit_combat_data.py
python3 -m unittest discover -s tests -p 'test_combat_data_audit.py' -v
python3 verify_combat_supabase_seeds.py
python3 run_combat_runtime_audit.py --dart /path/to/dart
git -c core.whitespace=cr-at-eol diff --check
```

Harness menggunakan model dan engine Dart asli dari sibling `project-echo`,
bukan simulasi formula buatan ulang. 689 skill, 40 class dan 91 eksekusi ally
lolos tanpa exception, offensive attack tanpa damage, atau friendly damage
tak disengaja pada skenario uji. Enam regresi angka lolos: MP Channeler, heal
PER Lyra, regen Lyra, party heal Solas, damage cap Rex dan healing bonus Lyra.
Sepuluh unit test validator/importer juga lolos, termasuk data sengaja rusak
untuk skill hilang, salah tipe, heal duplikat, probability dan MP tidak valid.

689 row SQL lengkap cocok dengan JSON pada full seed, lima chunk dan bundle.
Importer menolak data kosong/formula list sebelum menulis ulang seed.
`validate_data.py` pada saat audit: 0 error, 7 warning lokasi farming quest
neutral, di luar koreksi combat ini. CRLF class_list dipertahankan.

Flutter SDK yang dikonfigurasi berada pada volume yang tidak tersedia;
uji UI/full Flutter tidak dijalankan. Uji pure Dart memakai SDK 3.11.0.

## Temuan Client

1. `lib/features/combat/engine/skill_library.dart:838`: resolver menyamakan
   `ally` dan `all_ally`, serta `enemy` dan `all_enemies`, terhadap seluruh
   peserta. Probe Myste membuktikan caster dan ally sama-sama ter-heal padahal
   hanya ally yang dipilih. Perlu resolver yang membedakan selected targets
   dan seluruh peserta, tanpa mengubah ID skill sebagai workaround.
2. `lib/features/combat/engine/ally_ai_service.dart:128`: klasifikasi heal
   berdasarkan substring ID/target. 19 active healer tidak dikenali, termasuk
   Lyra, Vera, Seraph, Narra dan Solas. Perlu klasifikasi payload healing.
3. `skill_library.dart:711`: applyPassives hanya memiliki konteks caster;
   stat/periodic aura party tidak didistribusikan ke party. Beberapa handler
   bersifat metadata/no-op, misalnya stat conversion atau utility crafting.
4. `lib/data/models/skill.dart:123`: cooldown/range/shape belum menjadi bagian
   model combat. Beberapa stat/condition juga tidak mempunyai semantik persis
   seperti teks desain (misalnya AGI percent dan damage_taken).

Harness mencatat 29 passive tanpa perubahan snapshot pada HP 45%. Ini bukan
29 bug yang terbukti: ada conditional yang tidak aktif, utility/noncombat,
metadata handler dan training dummy yang memang inert. Semua ID dan bukti
probe ada di `combat_runtime_validation.json`; jangan menganggap 0 exception
sebagai bukti semua efek sudah sesuai desain.

## Supabase dan Publikasi

Patch `supabase/seed/combat_audit_20261008.sql` sudah diterapkan: 685 UPDATE,
satu INSERT skill, satu UPDATE referensi passive monster. Tidak ada DDL,
perubahan save pemain, atau perubahan field monster lain. Verifikasi live
tercatat di `combat_supabase_validation.json`: nol skill link ally/monster
yang hilang atau salah tipe, nol effect/deskripsi kosong.

Full seed skill, lima chunk, monster seed terkait dan `apply_all.sql` sudah
sinkron. Jangan menjalankan bundle schema+seluruh domain sebagai content
update; gunakan delta khusus jika mengisi environment lain dengan baseline
yang sama. Perubahan lokal lain milik pengguna tidak di-revert atau dimasukkan
ke delta ini. JSON class/skill/monster tetap perlu dipublikasikan melalui Git
dan refresh cache master data game sebelum playtest.
