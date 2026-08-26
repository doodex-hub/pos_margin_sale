# Detail Test — sale_margin_threshold

**Level:** Detail — varian/edge-case, fitur sekunder.
**Sumber:** skenario S-01, S-02 di `../10_BUSINESS_FLOW_MIGRATION.md`.

## Skenario 1: Field "Margin" tidak dobel saat modul POS margin juga terinstall

```
1. Pastikan modul "pos_margin_threshold" JUGA terinstall (bukan cuma modul ini).
2. Buka form produk apapun.
3. Cari label "Margin" dan "Minimum sale price" di form.
```

**Yang HARUS terjadi:** label ini muncul TEPAT SATU KALI, bukan dua kali (tidak ada baris/field yang dobel dari kedua modul).

## Skenario 2: Konfirmasi order rental — TIDAK BISA DICEK

Modul rental adalah fitur Odoo Enterprise. Kalau perusahaan Anda MEMAKAI Odoo Enterprise dengan modul Rental aktif, cek manual: buat rental order, confirm — modul ini HARUS SKIP validasi harga minimum sama sekali untuk rental order (biarkan core Odoo yang menangani). Kalau tidak memakai Enterprise/Rental, skenario ini tidak relevan untuk instalasi Anda.

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-08-26 | Docker QA (`pos_margin_sale_migration_18_qa`, live server, ketiga modul terinstall) | AI, real Chrome (Step 10) | Pass (Skenario 1) | Dikonfirmasi via inspeksi DOM: hanya 1 label "Margin", 1 label "Minimum sale price" |
