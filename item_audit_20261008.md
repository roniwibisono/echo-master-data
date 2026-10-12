# Audit Item dan Shop - 8 Oktober 2026

Katalog berubah dari 1.148 entri (1.104 ID unik) menjadi 1.090 item unik.
Sebanyak 44 entri berulang dibuang dengan mempertahankan definisi terakhir,
sesuai perilaku client. Sebanyak 19 ID berbeda digabungkan dan 5 item ditambahkan.
Ada 33 shop yang berubah; seluruh 42 shop sekarang memiliki 370 listing valid.

## Item yang Digabungkan

| Keluarga lama | Item yang dipertahankan |
| --- | --- |
| Minor Health/Healing Potion, Basic Health Potion, Minor HP Potion | Small HP Cell (50 HP) |
| Minor Mana/MP Potion | Small MP Cell (30 MP) |
| Advanced Health Potion, HP Potion | Medium HP Cell (200 HP) |
| MP Potion | Medium MP Cell (120 MP) |
| Greater HP Potion | Large HP Cell (500 HP) |
| Greater MP Potion | Large MP Cell (300 MP) |
| Elixir of Restoration | Full Recovery Pack (100% HP dan MP) |
| Revive Shard (`con_revive_shard`) | Revival Shard (`itm_revive_shard`, 50% HP) |
| Storm Core (`storm_core`) | `mat_storm_core` |
| Iron Ore (`iron_ore`) | `mat_iron_ore` |
| Paradox Crystal (`crs_paradox_crystal`) | `paradox_crystal` |
| Scarab Shell (`scarab_shell`) | `bio_scarab_shell` |

Small HP/MP Cell tetap 50/30. Medium HP/MP Cell berubah dari 120/90 menjadi
200/120; Large HP/MP Cell berubah dari 300/250 menjadi 500/300. Harga cell
yang dipertahankan tidak berubah. Potion kecil dengan nilai 40/60/80 HP
distandardisasi ke 50 HP; potion 50 MP ke 30 MP. Full Recovery Pack berharga
5.500, level 40, menggantikan elixir lama dengan harga 1.500, level 30.

Material dengan grade berbeda tidak digabungkan: nama menjadi Concentrated
Aethel Core Fragment, Mutated Shard Bio-Essence, dan Refined Aethel Essence.
Prima Materia mythic untuk upgrade tetap terpisah. Gear tier level 5 yang punya
nama sama dengan level 1 diberi awalan Reinforced. Bandage, herb, ration,
buff berbagai tier, dan crate dipertahankan karena biaya, asal, atau efek berbeda.

## Item Baru

| Item | Fungsi | Harga / Level |
| --- | --- | --- |
| Small Energy Cell | +25 energi eksplorasi | 80 / 1 |
| Large Energy Cell | +60 energi eksplorasi | 210 / 15 |
| Field Recovery Pack | +120 HP dan +60 MP | 100 / 5 |
| Full Recovery Pack | 100% HP dan MP, tidak revive | 5.500 / 40 |
| Sterile Water | Bahan crafting cell yang sebelumnya belum terdefinisi | 4 / 1 |

Efek baru memakai handler yang sudah tersedia di client. Energy Cell mengikuti
aturan overcharge energi yang sudah ada. Ikon memakai aset item yang sudah
dirujuk katalog. Small Energy Cell dan Field Recovery Pack punya resep baru.

Revival Elixir menjadi Emergency Revival Injector dan Phoenix Core menjadi
Phoenix Reboot Core; ID `itm_*` tetap karena dikenali layar ally. Recipe ID lama
juga tetap agar referensi pekerjaan crafting tidak putus.

## Perubahan Shop

Semua 16 ID tidak terdefinisi di shop Pax Nexus diganti dengan item katalog.
Listing berulang setelah penggabungan tidak dijumlahkan stoknya. Tiga item
loot-only dengan buy_price nol tidak lagi dijual: core_fragment, drake_heart,
dan echo_memory_core_low. Bahan resep `mat_metal` yang tidak terdefinisi diganti
scrap_metal. Semua referensi aktif quest, drop, biome, dungeon, dan crafting
untuk ID yang digabungkan ikut diperbarui.

## Menjalankan SQL

Jalankan file berikut di SQL Editor secara berurutan; tiap file memiliki
transaksi sendiri dan berukuran di bawah 24 KB. Selesaikan seluruh bagian
sebelum menerbitkan JSON baru.

1. [Part 01: item](supabase/seed/item_shop_cleanup_20261008_part01.sql)
2. [Part 02: item](supabase/seed/item_shop_cleanup_20261008_part02.sql)
3. [Part 03: kompatibilitas dan referensi](supabase/seed/item_shop_cleanup_20261008_part03.sql)
4. [Part 04: shop](supabase/seed/item_shop_cleanup_20261008_part04.sql)
5. [Part 05: shop](supabase/seed/item_shop_cleanup_20261008_part05.sql)
6. [Part 06: shop](supabase/seed/item_shop_cleanup_20261008_part06.sql)
7. [Part 07: shop](supabase/seed/item_shop_cleanup_20261008_part07.sql)

Untuk koneksi langsung/psql, gunakan file lengkap
`supabase/seed/item_shop_cleanup_20261008.sql` sebagai satu transaksi.
Setelahnya jalankan `supabase/seed/item_shop_cleanup_20261008_verify.sql`;
semua jumlah masalah harus nol.

SQL mengubah master item, inventori 33 shop, dan referensi ID dalam kolom
JSONB master data. Referensi di database diubah berdasarkan ID tepat sehingga
balancing quest/combat lain tetap dipertahankan. Isi listing shop yang berubah
disamakan dengan JSON; listing tambahan pada shop tersebut ikut dihapus.

Definisi ID lama tetap disimpan di Supabase sebagai kompatibilitas inventori
pemain dan memakai efek item penggantinya. SQL ini tidak memigrasikan save
pemain atau menggabungkan stack di inventori mereka. ID lama tidak muncul
lagi sebagai stok atau referensi reward baru. Seed items/shops saja tidak
menghapus stok lama; gunakan delta ini untuk database yang sudah berjalan.

Crafting, biome, dungeon, dan master JSON perlu diterbitkan ke sumber data
client juga. Setelah bootstrap memakai apply_all.sql lama, jalankan delta ini.

## Verifikasi dan Batasan

Validasi katalog: tidak ada ID berulang, item shop hilang, bahan crafting hilang,
listing ganda per shop, atau referensi aktif ke ID yang digabungkan.
Validasi quest menghasilkan 0 error dan 7 warning lokasi farming lintas region.
SQL diuji di PostgreSQL lokal melalui PGlite 0.5.8: query lengkap, tujuh bagian,
pengulangan, kesesuaian definisi item/shop, dan referensi JSON bertingkat lulus.
Struktur tabel telah dicocokkan dengan Supabase live melalui query baca.

Efek lama seperti cleanse, grenade, heal-over-time, dan sebagian utility masih
memerlukan dukungan client di luar jalur recovery combat. Audit ini tidak
menambahkan efek yang belum tersedia atau mengubah engine client.

Mapping ID dan perubahan per item lengkap tersedia di `item_audit_20261008.json`.
