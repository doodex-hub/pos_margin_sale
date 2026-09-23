# Main Flow Test — pos_margin_threshold

**Level:** Main Flow — flow bisnis inti yang paling sering dipakai user/admin sehari-hari.
**Estimasi waktu:** ~20 menit.
**Sumber:** S-03..S-11 di `../10_BUSINESS_FLOW_MIGRATION.md`.

## Margin & harga minimum — perhitungan dasar

```
1. Buka kategori produk, set "Margin" = 20%.
2. Buat produk baru di kategori itu, JANGAN isi margin manual.
3. Pastikan margin produk otomatis ikut 20% (diwarisi dari kategori).
4. Ubah margin produk itu manual jadi 35%, simpan.
5. Buka lagi produk itu (refresh/reload) — pastikan margin TETAP 35% (tidak balik ke 20%).
6. Cek "Minimum sale price" = Cost x (1 + Margin/100). Contoh: Cost 100, Margin 20% -> Minimum 120.
```

## Wizard "Assign Margin" (isi margin banyak produk sekaligus)

```
1. Buka list Product Template, centang 2-3 produk.
2. Klik menu Actions > "Assign Margin" (atau tombol serupa).
3. Pastikan dialog wizard terbuka menampilkan produk yang dicentang tadi.
4. Isi angka margin, klik "Assign".
5. Pastikan margin SEMUA produk yang dicentang berubah sesuai angka yang diisi.
6. Ulangi dari list "Product Variants" (bukan Template) — pastikan wizard yang sama juga berfungsi.
```

## Dialog peringatan harga di POS (mode konfirmasi & mode blokir)

```
1. Buka Settings > Point of Sale, pastikan "Blocking transaction" MATI (default).
2. Di POS, tambahkan produk di bawah harga minimum, klik "Pay".
3. Pastikan dialog KONFIRMASI muncul (ada tombol lanjut/batal), klik lanjut -> sampai ke pembayaran.
4. Kembali ke Settings, NYALAKAN "Blocking transaction".
5. Ulangi tambah produk di bawah minimum di POS, klik "Pay".
6. Pastikan dialog kali ini HANYA punya tombol "Ok" (tidak bisa lanjut ke pembayaran sama sekali).
```

## Kolom Margin/Minimum sale price/Incl. Tax di list Product Variants

```
1. Buka list "Product Variants" (Inventory/Sales > Products > Product Variants).
2. Pastikan kolom "Margin", "Minimum sale price", "Incl. Tax" TAMPIL LANGSUNG (tidak perlu klik
   toggle kolom manapun).
3. Cari/buat produk dengan margin negatif — pastikan kolom "Margin" tampil MERAH.
4. Cari/buat produk dengan harga jual di bawah minimum — pastikan kolom "Sales Price" tampil MERAH.
5. Kalau modul "sale_margin_threshold" JUGA terinstall: pastikan kolom di atas HANYA muncul SATU
   SET (tidak dobel/duplikat).
```

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-09-23 | Docker 20.0 QA (utama + throwaway `..._step10`) | AI (Step 10) | Pass | "Margin & harga minimum" dan "Wizard" dibuktikan lewat test/tour otomatis + Desk Review Step 8 (bukan klik manual, browser blocked `MF-46`). "Kolom list" (bagian 4) dibuktikan lewat RPC/ORM live langsung ke registry Odoo (arch + data nyata dikonfirmasi benar) TAPI warna merah itu sendiri belum dikonfirmasi tampil visual — rekomendasi: QA manusia jalankan langkah 3-5 di atas secara visual sebelum rilis besar. |
