# Main Flow Test — sale_margin_threshold

**Level:** Main Flow — flow bisnis inti sehari-hari.
**Sumber:** N/A — modul ini tidak punya skenario ber-`Level: Main Flow` tersendiri di `../10_BUSINESS_FLOW_MIGRATION.md` sesi ini (sudah tercakup unit test otomatis, lihat `01_SMOKE.md`).

## Kalau tetap ingin cek manual — confirm quotation dengan harga di bawah minimum

```
1. Buka Sales, buat quotation baru untuk pelanggan apapun.
2. Tambahkan produk dengan harga jual di bawah "Minimum sale price" produk itu
   (bisa dicek di form produk).
3. Klik tombol "Confirm".
```

**Yang HARUS terjadi (tergantung setting "Blocking Transaction" di Settings > Sales):**
- Kalau setting blocking AKTIF: order TIDAK bisa dikonfirmasi, muncul pesan error yang jelas (bahasa Inggris atau Prancis tergantung bahasa user login).
- Kalau setting blocking TIDAK aktif: muncul jendela pop-up konfirmasi ("mau lanjut walau harga di bawah minimum?"), order baru berubah status "Sales Order" setelah wizard itu di-confirm.

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| | | | | |
