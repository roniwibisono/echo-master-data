# GM-02 authoring artifacts

9 Oktober 2026. Generated offline; **belum dieksekusi ke Supabase**.

4.835 unique activation entries, termasuk 340 JSON-domain extras. Existing class flags dipertahankan. `catalog-extras-bootstrap.sql` insert-only, tidak menimpa edit GM atau definition existing. Activation catalog adalah sidecar authoring; tidak mengganti database publication sebagai authority.

Generator: `/Users/rnddev/Documents/project-echo/tools/gm_content_catalog.py`.
Gunakan `--manifest <verified-envelope.json>` untuk review draft import dengan expected release/revision. Missing canonical IDs harus direkonsiliasi sebelum publish; template tidak menyisipkan definisi atau mengaktifkan ID tak dikenal.

Exporter master diperbarui agar flag/revision tidak hilang. Jangan menggunakan legacy seed definition terhadap live setelah editor GM diterapkan; cutover importer definition-draft adalah gate GM-06. Ekspor/CDN upload dan acceptance perangkat belum dijalankan. Kontrak lengkap: `/Users/rnddev/Documents/project-echo/docs/admin/gm-02-content-activation.md`.
