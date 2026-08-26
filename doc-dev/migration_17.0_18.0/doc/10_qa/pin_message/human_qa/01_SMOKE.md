# Smoke Test — pin_message

**Level:** Smoke — flow paling kritis. Kalau salah satu langkah di sini gagal: STOP, jangan lanjut deploy/testing lain.
**Sumber:** N/A — modul ini tidak punya skenario ber-`Level: Smoke` tersendiri. Jalur paling kritis (pin/unpin pesan log note lewat tombol inline) sudah tercakup penuh oleh 2 Tour test otomatis (`pin_message/static/tests/tours/pin_message_tour.js`).

## Kalau tetap ingin cek manual cepat

1. Jalankan `docker compose up` di `docker-env/` (mode standar, `--test-enable`).
2. Cek log — harus ada `"tour succeeded"` dua kali untuk `pin_message`, dan ringkasan `0 failed`.
3. Kalau tidak — Smoke gagal, JANGAN lanjut deploy.

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-08-26 | Docker QA (`pos_margin_sale_migration_18_test`) | AI (Step 9) | Pass | Kedua Tour test "tour succeeded", 0 failed |
