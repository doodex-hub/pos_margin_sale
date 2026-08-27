# Main Flow Test — pos_margin_threshold

**Level:** Main Flow — flow bisnis inti yang paling sering dipakai user/admin sehari-hari.
**Estimasi waktu:** ~5 menit.
**Sumber:** skenario ber-`Level: Main Flow` di `../10_BUSINESS_FLOW_MIGRATION.md`.

## Update margin dari list Product Template

```
1. Buka menu Inventory > Products.
2. Centang checkbox di salah satu baris produk.
3. Klik tombol "Actions" (ikon gear) di atas list.
4. Klik "Update margin sale".
5. Cek: field yang muncul berlabel "Products" (bukan "Product variants").
6. Isi nilai Margin, klik "Assign".
7. Buka kembali produk tadi — pastikan Margin sudah ter-update sesuai isian.
```

## Update margin dari list Product Variants

```
1. Aktifkan dulu fitur "Variants" kalau belum aktif: Inventory > Configuration > Settings >
   centang "Variants" > Save.
2. Buka Inventory > Products > Product Variants.
3. Centang checkbox salah satu baris.
4. Klik "Actions" > "Update margin sale".
5. Cek: field yang muncul berlabel "Product variants" (bukan "Products").
6. Isi nilai Margin, klik "Assign" — atau "Cancel" untuk membatalkan.
```

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-08-27 | Docker `odoo:19.0`, db `pos_margin_sale_migration_19_qa` | AI (Playwright, `qa_step10.js`) | Pass | S-10-02 & S-10-03 — lihat `10_BUSINESS_FLOW_MIGRATION.md` |
