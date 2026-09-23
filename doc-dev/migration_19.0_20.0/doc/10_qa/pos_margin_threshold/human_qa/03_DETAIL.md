# Detail Test — pos_margin_threshold

**Level:** Detail — varian/edge-case, fitur sekunder, kombinasi kondisi yang jarang dipakai tapi
tetap valid.
**Estimasi waktu:** ~15 menit.
**Sumber:** S-12..S-18 di `../10_BUSINESS_FLOW_MIGRATION.md`.

## Wizard "Assign Margin" — tombol Cancel

```
1. Buka wizard "Assign Margin" (lihat 02_MAIN_FLOW.md), isi angka margin.
2. Klik "Cancel" (bukan "Assign").
3. Pastikan TIDAK ADA produk manapun yang margin-nya berubah.
```

## Produk Combo di POS — styling baris child

```
1. Pastikan ada produk combo yang tersedia di POS (kalau belum ada, buat: 1 produk tipe "Combo"
   dengan 2+ pilihan produk).
2. Di POS, tambahkan produk combo tsb ke keranjang, pilih salah satu opsi combo-nya.
3. Pastikan baris produk PILIHAN COMBO (bukan baris combo induknya) tampil dengan indentasi/garis
   di sisi kiri (border kiri), berbeda dari baris produk biasa.
   CATATAN: ini styling yang BARU AKTIF pertama kali di versi ini (sebelumnya tidak pernah tampil
   karena bug lama) — kalau kamu TIDAK melihat garis/indentasi ini sama sekali, laporkan sebagai
   temuan (lihat FINDINGS.md MF-34).
```

## Form Kategori — posisi field Margin

```
1. Buka Inventory > Configuration > Product Categories > buka kategori apa saja.
2. Pastikan field "Margin" muncul SEBELUM field "Costing Method".
```

## Konsistensi lain (regresi — pastikan TIDAK berubah)

```
1. Buka Settings > General Settings, cari pengaturan terkait "Blocking transaction order" — pastikan
   field ini TIDAK muncul di halaman settings modul ini sendiri (field itu hanya relevan kalau modul
   "sale_margin_threshold" juga terinstall).
2. Kalau kedua modul margin (pos_margin_threshold + sale_margin_threshold) terinstall bersamaan,
   pastikan wizard "Assign Margin" tetap bisa dibuka dan dipakai tanpa error (model gabungan).
```

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-09-23 | Docker 20.0 QA (throwaway `..._step10` untuk combo) | AI (Step 10) | Sebagian Pass, 1 Pending | Wizard Cancel: belum ada bukti otomatis maupun manual (Pending, risiko rendah). Combo styling: KONTRAK DATA backend dikonfirmasi benar via ORM langsung (order+line combo dibuat nyata, relasi tersimpan benar) TAPI tampilan visual garis/indentasi itu sendiri BELUM dikonfirmasi (browser blocked). Form Kategori & item regresi lain: dikonfirmasi via RPC/Desk Review. **Rekomendasi: langkah "Produk Combo" WAJIB dijalankan manusia sebelum rilis besar** — ini genuinely belum pernah dilihat siapapun secara visual di versi ini. |
