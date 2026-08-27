# Detail Test — pin_message

**Level:** Detail — varian/edge-case, fitur sekunder, kombinasi kondisi yang jarang dipakai tapi tetap valid.
**Estimasi waktu:** ~3 menit.
**Sumber:** skenario ber-`Level: Detail` di `../10_BUSINESS_FLOW_MIGRATION.md`.

## Reload round-trip — status pin tidak bocor antar thread

```
1. Buka Discuss, masuk ke channel apapun (misal "general").
2. Kirim pesan baru, pin pesan tersebut (hover > menu > Pin, atau tombol pin inline).
3. Catat: pesan menampilkan ikon pin.
4. Pindah ke channel/thread LAIN.
5. Kembali lagi ke channel semula.
6. Cek: pesan yang tadi di-pin MASIH menampilkan ikon pin (tidak hilang, tidak berubah).
```

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-08-27 | Docker `odoo:19.0`, db `pos_margin_sale_migration_19_qa` | AI (Playwright, `qa_step10.js`) | Pass | S-10-06 — ikon pin tetap 1 sebelum/sesudah pindah thread |
