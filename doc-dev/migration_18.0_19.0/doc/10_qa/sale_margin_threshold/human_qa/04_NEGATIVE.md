# Negative Test — sale_margin_threshold

**Level:** Negative — input salah, guard/keamanan, hal yang HARUS ditolak atau HARUS TIDAK muncul.
**Estimasi waktu:** N/A.
**Sumber:** skenario ber-`Level: Negative` di `../10_BUSINESS_FLOW_MIGRATION.md`.

N/A — modul ini tidak punya skenario ber-Level Negative di `10_BUSINESS_FLOW_MIGRATION.md`. Jalur
negative konfirmasi order (`AC-01-02`, `ValidationError` saat blocking aktif) sudah dicover penuh
oleh unit test otomatis Step 9 (`test_action_confirm_blocking_below_minimum`).

**Catatan bug yang SENGAJA dipertahankan (bukan gap Negative baru):** `MF-08` (batch-confirm
singleton bug) — dipertahankan identik sesuai keputusan user, dibuktikan lewat
`test_action_confirm_BATCH_MULTI_ORDER_F05` (Step 9). Ini BUKAN item checklist manual di sini
karena tidak ada komponen UI/browser yang unit test tidak bisa jangkau.

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| | | | | |
