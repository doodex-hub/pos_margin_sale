# Smoke Test — pos_margin_threshold

**Level:** Smoke — flow paling kritis. Kalau salah satu langkah di sini gagal: STOP, jangan lanjut deploy/testing lain.
**Sumber:** N/A — modul ini tidak punya skenario ber-`Level: Smoke` tersendiri di `../10_BUSINESS_FLOW_MIGRATION.md`. Jalur paling kritis (POS terbuka, jual produk di bawah harga minimum, dialog peringatan muncul, pembayaran tetap bisa diselesaikan) sudah tercakup penuh oleh 2 Tour test otomatis yang jalan tiap kali test suite dijalankan (`pos_margin_threshold/static/tests/tours/margin_threshold_tour.js`) — kalau salah satu dari dua Tour ini gagal, test suite penuh langsung menunjukkan error, jadi tidak perlu langkah manual terpisah untuk level ini.

## Kalau tetap ingin cek manual cepat

1. Jalankan `docker compose up` di `docker-env/` (mode standar, `--test-enable`).
2. Cek baris terakhir log: harus ada `"tour succeeded"` dua kali untuk `pos_margin_threshold`, dan baris ringkasan `odoo.tests.result` harus `0 failed`.
3. Kalau tidak — itu tanda Smoke gagal, JANGAN lanjut deploy.

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-08-26 | Docker QA (`pos_margin_sale_migration_18_test`) | AI (Step 9/10) | Pass | Kedua Tour test "tour succeeded", 0 failed |
