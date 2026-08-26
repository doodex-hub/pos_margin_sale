# Detail Test — pin_message

**Level:** Detail — varian/edge-case, fitur sekunder.
**Sumber:** N/A — modul ini tidak punya skenario ber-`Level: Detail` tersendiri di `../10_BUSINESS_FLOW_MIGRATION.md` sesi ini.

## Item lain yang berguna dicek sesekali

```
1. Buka record apapun yang punya chatter (contoh: kontak pelanggan), Log note,
   pin pesan itu.
2. Buka record LAIN yang belum pernah punya pesan/pin apapun.
3. Cek: section "Pinned Messages" TIDAK BOLEH muncul di record kedua ini
   (harus benar-benar kosong, bukan bocoran dari record pertama).
4. Kembali ke record pertama — badge "Pinned Messages" harus masih menunjukkan
   angka yang benar.
```

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-08-26 | Docker QA (`pos_margin_sale_migration_18_qa`, live server) | AI, real Chrome (Step 10) | Pass | "Acme Corporation" → "Azure Interior" → kembali: tidak ada state bocor, badge tetap benar |
