# Smoke Test — pos_margin_threshold

**Level:** Smoke — flow paling kritis. Kalau salah satu langkah di sini gagal: STOP, jangan lanjut
deploy/testing lain, balik ke step 9 atau eskalasi ke tim dev.
**Estimasi waktu:** ~5 menit.
**Sumber:** S-01, S-02 di `../10_BUSINESS_FLOW_MIGRATION.md`.

## Flow 1 — Pembayaran POS dengan produk di bawah harga minimum

```
1. Buka Point of Sale, mulai sesi kasir baru.
2. Tambahkan ke keranjang sebuah produk yang harganya SUDAH di-set di bawah "minimum sale price"-nya.
3. Klik tombol "Pay".
4. Pastikan muncul dialog peringatan "Price unit less than minimum price".
5. Klik tombol konfirmasi/lanjut pada dialog tsb.
6. Selesaikan pembayaran seperti biasa (pilih metode bayar, validasi).
7. Pastikan sampai ke layar struk (receipt) tanpa error/crash.
```

## Flow 2 — Form produk & kategori terbuka normal

```
1. Buka Inventory/Sales > Products > pilih produk apa saja > buka form-nya.
2. Pastikan form terbuka tanpa pesan error, dan field "Margin" / "Minimum sale price" terlihat.
3. Buka Inventory > Configuration > Product Categories > pilih kategori apa saja.
4. Pastikan field "Margin" terlihat di form kategori, form terbuka tanpa error.
5. Buka list "Product Variants" (lewat smart button "N Variants" di produk, atau menu Products >
   Product Variants).
6. Pastikan list terbuka, kolom "Margin", "Minimum sale price", dan "Incl. Tax" terlihat.
```

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-09-23 | Docker 20.0 QA (`pos_margin_sale_migration_20_qa`) | AI (Step 10, evidence tidak langsung — lihat S-01/S-02) | Pass | Flow 1 dibuktikan lewat Tour otomatis Step 9 (real Chrome, SUCCEEDED), BUKAN klik manual sesi ini (browser Playwright blocked, `MF-46`). Flow 2 dibuktikan lewat RPC `get_view()` (S-09/S-14), bukan klik manual. Rekomendasi: QA manusia tetap jalankan langkah di atas minimal sekali sebelum rilis besar untuk konfirmasi visual penuh. |
