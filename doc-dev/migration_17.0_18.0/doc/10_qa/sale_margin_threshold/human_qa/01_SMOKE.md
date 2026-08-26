# Smoke Test — sale_margin_threshold

**Level:** Smoke — flow paling kritis. Kalau salah satu langkah di sini gagal: STOP, jangan lanjut deploy/testing lain.
**Sumber:** N/A — modul ini tidak punya skenario ber-`Level: Smoke` tersendiri. Jalur paling kritis (confirm sale order dengan harga di bawah minimum → wizard atau block muncul sesuai konfigurasi) sudah tercakup penuh oleh 4 test otomatis (`test_action_confirm.py`) yang jalan tiap kali test suite dijalankan.

## Kalau tetap ingin cek manual cepat

1. Jalankan `docker compose up` di `docker-env/` (mode standar, `--test-enable`).
2. Cek baris ringkasan `odoo.tests.result` di log — harus `0 failed`.
3. Kalau ada error dari `sale_margin_threshold.tests.test_action_confirm` — itu tanda Smoke gagal, JANGAN lanjut deploy.

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-08-26 | Docker QA (`pos_margin_sale_migration_18_test`) | AI (Step 9) | Pass | `0 failed, 0 error(s) of 22 tests` (setelah fix `MF-21`) |
