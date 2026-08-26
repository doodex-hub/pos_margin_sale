# Main Flow Test — pos_margin_threshold

**Level:** Main Flow — flow bisnis inti sehari-hari.
**Estimasi waktu:** ~3 menit.
**Sumber:** skenario S-01 di `../10_BUSINESS_FLOW_MIGRATION.md`.

## Skenario: Ubah margin banyak produk sekaligus lewat wizard

```
1. Buka Inventory > Products, ganti ke tampilan List (ikon list di pojok kanan atas).
2. Centang checkbox di sebelah kiri satu atau lebih produk yang mau diubah marginnya.
3. Klik tombol "Actions" di atas daftar, pilih "Update margin sale".
4. Sebuah jendela pop-up muncul dengan daftar produk yang tadi dipilih sudah terisi otomatis.
5. Isi angka di kolom "Margin" (contoh: 20 untuk margin 20%).
6. Klik tombol "Assign".
7. Buka salah satu produk yang tadi dipilih — cek kolom "Margin" sudah berubah sesuai
   angka yang diisi, dan kolom "Minimum sale price" ikut ter-update otomatis
   (rumus: Cost × (1 + Margin/100)).
8. Scroll ke bagian riwayat chatter di sisi kanan — harus ada catatan
   "... → [angka baru] (Margin)" mencatat siapa yang mengubah dan kapan.
```

**Yang HARUS terjadi:** wizard terbuka lancar tanpa error, margin ter-apply ke SEMUA produk yang dipilih, minimum sale price ikut terhitung ulang, perubahan tercatat di chatter.

**Tanda kalau ada yang salah:** wizard tidak terbuka / error saat klik "Assign" / margin tidak berubah setelah klik Assign / minimum sale price tidak ikut ter-update.

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-08-26 | Docker QA (`pos_margin_sale_migration_18_qa`, live server) | AI, real Chrome (Step 10) | Pass | Produk "Apple Pie": Margin 0→20%, Minimum sale price → $12.96, chatter mencatat perubahan |
