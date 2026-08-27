# Detail Test — pos_margin_threshold

**Level:** Detail — varian/edge-case, fitur sekunder, kombinasi kondisi yang jarang dipakai tapi tetap valid.
**Estimasi waktu:** ~3 menit.
**Sumber:** skenario ber-`Level: Detail` di `../10_BUSINESS_FLOW_MIGRATION.md`.

## Wizard "Update margin sale" — Cancel tidak mengubah apapun

```
1. Buka form salah satu produk, catat nilai field "Margin" saat ini.
2. Kembali ke list Products, centang produk yang sama.
3. Actions > "Update margin sale".
4. Isi field Margin dengan angka BERBEDA dari nilai asli.
5. Klik "Cancel" (JANGAN klik "Assign").
6. Buka kembali form produk yang sama.
7. Cek: nilai Margin TIDAK berubah — masih sama seperti langkah 1.
```

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-08-27 | Docker `odoo:19.0`, db `pos_margin_sale_migration_19_qa` | AI (Playwright, `qa_step10.js`) | Pass | S-10-05 — margin sebelum/sesudah tetap 0.00% |
