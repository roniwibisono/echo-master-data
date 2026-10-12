# The Unwritten Witness

Paket narrative playable untuk Echo of Xylos, 2026-10-08. **25 quest: 10 secret, 15 mystery.** Lima rangkaian dapat dimulai terpisah; quest terakhir mengharuskan empat rangkaian lainnya selesai. Semua bisa diakses tujuh player faction, tanpa mengubah pihak yang dianggap benar oleh story utama. Integrasi client tersedia lokal; rilis publik belum dilakukan.

## Pengalaman Pemain

Pemain menemukan sesuatu yang tidak cocok: kursi yang masih diperbaiki di rumah kosong, bunyi lonceng yang kehilangan satu ketukan, tagihan barang yang tidak ada, bangku yang menghadap arah salah, atau kunci modern di ruang kuno. Petunjuk dapat dibaca di tempat, dibandingkan, lalu dibicarakan. Tidak ada jendela waktu sempit, jawaban salah yang mengunci quest selamanya, atau drop bukti 1%.

Kelima rangkaian disatukan oleh satu pertanyaan: **siapa yang berhak memperbaiki sebuah catatan ketika catatan itu sudah melukai seseorang?** Tidak ada dalang baru yang menguasai tujuh faction. Reveal tetap lokal, dapat diuji, dan tidak mengubah penyebab Great Severance.

## Rangkaian

1. **The Unlisted Ward, level 7-10.** Edda Fen membantu keluarga yang tidak tercatat. Misterinya memisahkan kehilangan identitas, relokasi, dan pilihan untuk tidak membuka alamat. Concordium dilihat melalui dampak rekonstruksi, bukan karikatur birokrasi jahat.
2. **The Hollow Muster, level 18-22.** Tovan Rell memperbaiki lonceng evakuasi. Roster kerja gabungan memperlihatkan bantuan praktis di antara kru Iron Hegemony dan Starforged Legion; bukan retcon aliansi resmi atau penggabungan faction.
3. **The Zero Berth, level 22-25.** Sella Quinn membongkar double billing. Pemain harus membedakan jasa penyimpanan yang sah dari tagihan duplikat, dan kriminal individual dari semua pedagang Meridian atau pegawai OmniCorp.
4. **The Quiet Resonator, level 32-40.** Iren Saye membandingkan rekaman Arcanum dengan ingatan Children of the Shard. Efek akustik dapat dibuktikan; kesadaran atau kehendak Shard tetap tidak dinyatakan sebagai fakta.
5. **The Unwritten Witness, level 65-75.** Maela Orr meninjau arsip bantuan modern di ruang kuno. Custodians dan AMA dinilai melalui batas mandat, ketelitian, keterlambatan bantuan, dan kesempatan mengajukan koreksi.

## Daftar Quest

| Quest | Level | Jenis | Title Eksklusif |
| --- | ---: | --- | --- |
| A Chair for Someone Missing | 7 | Secret | Finder of the Unlisted |
| The Number Beneath the Number | 7 | Mystery | Reader Beneath the Paint |
| An Obedient Lock | 8 | Mystery | Breaker of Empty Orders |
| The Route Kept Inside | 9 | Secret | Keeper of Private Roads |
| The Right to Remain Unlisted | 10 | Mystery | Witness Without Ownership |
| The Missing Fourth Beat | 18 | Secret | Hearer of the Missing Beat |
| Boots Facing Outward | 18 | Mystery | Reader of the Empty Line |
| What Keeps Taking the Cable | 19 | Mystery | Ender of Repeated Failure |
| The Shift Neither Banner Claimed | 20 | Secret | Keeper of the Shared Shift |
| A Warning Is Not an Oath | 22 | Mystery | Keeper of the Fourth Beat |
| The Weight of Nothing | 22 | Secret | Appraiser of Nothing |
| The Label Facing Inward | 22 | Mystery | Reader of Reversed Claims |
| The Fee at the Evidence Door | 23 | Mystery | Breaker of Circular Debt |
| Rent Inside Rent | 24 | Secret | Unfolder of Double Ledgers |
| A Port Without This Lie | 25 | Mystery | Auditor of the Unseen Margin |
| Cloth on a Singing Rib | 32 | Secret | Listener Before Believer |
| The Bench Facing the Wrong Way | 33 | Mystery | Reader of the Second Sound |
| One Test Without a Witnessed Monster | 34 | Mystery | Keeper of a Measured Boundary |
| The Same Pause Twice | 36 | Secret | Keeper of Honest Uncertainty |
| The Silence Worth Keeping | 40 | Mystery | Warden of the Unanswered |
| A Modern Lock on Ancient Stone | 65 | Secret | Divider of Borrowed Histories |
| A Burn Without a Verdict | 66 | Mystery | Witness Before Judge |
| Safe Enough to Make a Copy | 68 | Mystery | Keeper of the Second Copy |
| The Reserve That Wasn't a Ransom | 70 | Secret | Reader of the Withheld Line |
| The Unwritten Witness | 75 | Mystery | The Unwritten Witness |

## Prestige Dan Balance

- 25 title memakai unlock `quest_completed`, yang sudah didukung client. Semua `stat_bonus` title kosong karena client menjumlahkan bonus seluruh earned title, bukan hanya title yang ditampilkan.
- 25 relic hadiah: 20 koleksi `QUEST` dan lima accessory. Sepuluh item bukti terpisah membuat total item baru 35.
- Accessory finale: Ring of the Unlisted Ward (+20 HP, +1 PER), Bellwright's Wrist Loop (+40 HP, +3 DEF), Zero Berth Signet (+25 MP, +3 PER), Quiet Gallery Pendant (+40 MP, +4 PER), dan Signet of the Unwritten Witness (+100 HP, +50 MP, +6 PER).
- Finale terakhir memakai rarity LEGENDARY sebagai prestige penyelesaian semua rangkaian, bukan sebagai best-in-slot otomatis. Tidak ada ATK baru, passive proc rekaan, ruby reward, atau multiplier permanen.
- Reward quest netral memakai CRD, bukan mata uang faction. EXP = level x30, CRD = level x10; reputation 15, atau 40 untuk finale. Semua quest nonrepeatable/nondaily.
- Ketiga pilihan memperoleh prestige yang sama. Pemain tidak harus memilih respons yang paling menguntungkan statistik untuk memperoleh title.
- Title mengikuti quest completion, bukan kepemilikan item yang bisa diperdagangkan/dibuang. Binding, larangan discard, atau keunikan kepemilikan accessory tidak dijanjikan karena belum menjadi kontrak item yang diverifikasi.
- 25 hidden achievement aktif dalam `mystery_achievements.json` dan katalog gabungan. Hook completion scalar serta backfill client sudah diuji. File `_pending.json` adalah arsip rancangan, bukan source aktivasi.

## Data Pendukung

Lima NPC baru dan sepuluh objek petunjuk yang direpresentasikan dengan schema NPC/terminal yang ada. Lima annex map mempunyai jalur kembali yang dicerminkan oleh RegionRepository. Lima monster baru menyalin stats/skills dari template setingkat yang sudah diaudit; monster lama tidak diubah. Setiap monster lokal memberi dua bukti dengan chance 1.0 melalui `drop_item`, bukan `special_reward` yang belum mempunyai distribusi lengkap.

Petunjuk lingkungan sekarang direpresentasikan oleh teks objek. Kursi, kabel, stencil, dan ledger belum dibuat sebagai art/scene 3D. Ikon item sementara memakai bitmap `materials/rusted_plate.png` yang benar-benar ada; portrait dan sprite khusus belum dibuat. Rancangan visual final harus mengikuti vignette dalam catalogue.

`mystery_catalogue.json` adalah sumber tulisan; `mystery_design.json` menyimpan 75 keputusan, petunjuk, jawaban, state dialog, dan konsekuensi personal. Catatan waktu menggunakan era relatif yang sudah diketahui, bukan tanggal sejarah baru.

## Status

Discovery, interaksi prop, validasi keputusan, state dialog, title, achievement, dan penyimpanan completion/reward sudah diintegrasikan ke client lokal. Bundle additive membawa quest/design dan data pendukung tanpa menunggu CDN. Lihat `MYSTERY_INTEGRATION.md` untuk kontrak save dan batasan.

Seed khusus dan aktivasi achievement sudah di-commit permanen ke Supabase pada 2026-10-08: 35 item, 5 monster, 15 NPC/objek, 25 quest, 40 dialog, dan 25 achievement. Query terpisah memastikan semua 145 record cocok dengan seed. Dry-run rollback sebelumnya tetap dicatat sebagai riwayat pengujian. Belum ada push Git atau deployment client/CDN; tidak perlu seed manual lagi dan jangan jalankan `apply_all.sql` untuk update ini.

## Verifikasi

28 unit test master data lulus. Validator paket: 0 error baru, 2.212 record lama tidak berubah. Parser Dart client membaca 25 quest dan semua data pendukung; lima monster baru menjalankan lima basic attack dan delapan active skill tanpa error. Tes client mencakup penyelesaian seluruh 25 quest, discovery, reward sekali, title/achievement, recovery journal, dan dialog nyata pada tiga ukuran layar. Hasil terbaru tersimpan di `mystery_client_validation.json`.

Audit global tetap mempunyai temuan lama: delapan target kill yang belum terdefinisi di quest_neutral.json, 68 warning legacy/level monster, 61 warning dialog, dan tujuh warning farm-region. Paket ini tidak menggunakan delapan target tersebut dan tidak menambah warning region/item. Tes otomatis tidak menggantikan playtest balance dan penerimaan cerita oleh pemain.
