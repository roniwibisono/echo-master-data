# Mystery Pack Integration

## Status

Integrasi playable sudah diterapkan di `/Users/rnddev/Documents/project-echo`.
Database project `fbntgtzimydjhuwedrjz` menyimpan permanen 145 record paket:
35 item, 5 monster, 15 NPC/objek, 25 quest, 40 dialog, dan 25 achievement.
Seluruh 145 record cocok dengan field seed pada query verifikasi terpisah.
Tidak ada perubahan schema, RLS, atau player saves melalui deployment SQL.
**Client baru belum dipublikasikan dan perubahan belum di-push ke Git.**

## Kontrak Client

- QuestRepository memuat `quest_mysteries.json`; parser mengenali `requirements.mystery`.
- `assets/data/mystery_pack.json` membawa quest/design dan overlay tambahan untuk item,
  monster, NPC, dialog, title, achievement, region, route, dan layout. Loader memakai
  paket ini tanpa menunggu publikasi CDN; record di luar scope paket tidak diganti.
- Root tersembunyi sampai bukti pertama ditemukan di region yang sesuai. Discovery
  tersimpan di quest progress dan tetap ada setelah abandon. Follow-up memerlukan
  completion sebelumnya; capstone memerlukan finale keempat arc lain.
- Acceptance merekonsiliasi clue yang sudah dimiliki. Clue tidak dikonsumsi saat turn-in.
- Kill/collect tidak otomatis menyelesaikan pemeriksaan prop. Interaksi NPC/terminal
  dan kunjungan region nyata dicatat; keputusan dan turn-in harus dilakukan di region quest.
- Dialog memakai briefing, active, ready, completed, petunjuk, tiga pilihan, dan biaya
  naratif dari design. Pilihan boleh direvisi sebelum completion. Konsekuensi tersimpan
  untuk player tersebut, bukan mutasi map global.
- `decision_id` dan `decision_at` tersimpan pada PlayerQuestProgress. Journal lokal
  menyimpan snapshot player dan completion bersama, kemudian memulihkan keduanya
  setelah restart sebelum cloud snapshot dikirim. Lock lokal mencegah reward ganda
  dari dua QuestState pada sesi yang sama; ini bukan transaksi lintas perangkat.
- Counter scalar `mystery_completed.<quest_id>` membuka hidden achievement; completed
  save lama direkonsiliasi secara idempotent. Title diberikan dari quest completion,
  bukan item yang dapat dipindahkan. Title tersembunyi sebelum discovery.
- NPC NEUTRAL dapat diakses ketujuh faction. Lima annex punya return route biasa;
  route tidak dikunci oleh discovery agar tidak terjadi loop akses clue.

## Verifikasi Dan Uji Manual

Lihat `mystery_client_validation.json` untuk hasil tes client terakhir, dan
`mystery_supabase_validation.json` untuk hasil database. Panduan langkah pertama
tersedia di client: `docs/qa/mystery-20261008/README.md`.

1. Dengan player level minimal 7, masuk dari BROKEN_CIVIL_QUARTER ke UNLISTED_WARD.
2. Kalahkan monster lokal sampai mendapat Carbon Census Slip. Quest pertama harus
   tersembunyi sebelum clue dan muncul setelah clue; keluar/masuk game untuk mengecek save.
3. Bicara dengan Edda Fen, pilih Investigate, periksa kedua objek petunjuk, lalu kembali.
4. Pilih satu keputusan, baca konsekuensi/biaya, Confirm Finding, kemudian Seal Record.
5. Pastikan relic, CRD, title, dan achievement didapat sekali. Reload lalu buka sealed
   record untuk membaca pilihan; abandon quest aktif harus mempertahankan discovery.
6. Lanjutkan lima quest pada setiap arc; capstone level 75 tidak boleh tersedia hanya
   karena arc kelima selesai.

## Deployment

Seed delta utama `supabase/seed/mystery_content_20261008.sql` sudah di-commit.
Aktivasi tambahan `supabase/seed/mystery_activation_20261008.sql` juga sudah di-commit:
25 achievement dan metadata release pada 25 quest. Tidak perlu seed manual lagi.
**Jangan replay apply_all.sql sebagai update content.**

Source achievement aktif adalah `narrative/mystery_achievements.json`.
File `_pending.json` tetap disimpan sebagai arsip rancangan, bukan seed aktif.
Importer achievement kini membaca tambahan aktif sehingga regenerasi tidak menghapusnya.

Untuk revisi data, jalankan `tools/build_mystery_client_bundle.py --client
/Users/rnddev/Documents/project-echo`, audit seed dan tes client, lalu publish client
melalui pipeline game. Publikasi master JSON/CDN tetap disarankan agar katalog remote
konsisten, tetapi client baru sudah membawa delta yang diperlukan.

## Batasan

Art khusus belum tersedia: ikon memakai asset valid placeholder dan petunjuk lingkungan
berupa teks objek. Tidak ada perubahan adegan global untuk ending personal. Konflik
save simultan lintas perangkat mengikuti mekanisme cloud save game yang sudah ada;
tes lokal tidak membuktikan jaminan exactly-once global/server.
