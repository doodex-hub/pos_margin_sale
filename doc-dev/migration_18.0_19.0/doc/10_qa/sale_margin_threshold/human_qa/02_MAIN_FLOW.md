# Main Flow Test — sale_margin_threshold

**Level:** Main Flow — flow bisnis inti yang paling sering dipakai user/admin sehari-hari.
**Estimasi waktu:** ~3 menit.
**Sumber:** skenario ber-`Level: Main Flow` di `../10_BUSINESS_FLOW_MIGRATION.md`.

## Field Margin tidak duplikat di form produk

```
1. Pastikan pos_margin_threshold DAN sale_margin_threshold terinstall bersamaan.
2. Buka Inventory > Products, buka salah satu produk.
3. Cari field "Margin" di tab General Information.
4. Cek: field "Margin" HANYA muncul SATU KALI, tidak dobel.
```

## Actions menu "Update margin sale" tidak duplikat

```
1. Buka Inventory > Products (list view), centang salah satu produk.
2. Klik "Actions".
3. Cek: hanya SATU entry "Update margin sale" yang muncul (bukan dua).
4. Klik entry tersebut — wizard yang terbuka sama seperti prosedur di
   `10_qa/pos_margin_threshold/human_qa/02_MAIN_FLOW.md`.
```

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-08-27 | Docker `odoo:19.0`, db `pos_margin_sale_migration_19_qa` | AI (Playwright, `qa_step10.js`) | Pass | S-10-04 & S-10-02/03 — lihat `10_BUSINESS_FLOW_MIGRATION.md` |
