# Main Flow Test — pin_message

**Level:** Main Flow — flow bisnis inti sehari-hari.
**Estimasi waktu:** ~3 menit.
**Sumber:** skenario S-01 di `../10_BUSINESS_FLOW_MIGRATION.md`.

## Skenario: Pin/unpin pesan Discuss channel

```
1. Buka Discuss, buka channel apapun (contoh: #general).
2. Kirim pesan baru di channel itu.
3. Arahkan mouse ke pesan yang baru dikirim (hover) sampai muncul ikon-ikon aksi
   di kanan atas pesan.
4. Klik ikon titik tiga ("..."), lalu klik "Pin" di menu yang muncul.
5. Sebuah jendela konfirmasi muncul ("You sure want this message pinned...") —
   klik "Yeah, pin it!".
6. Klik ikon thumbtack (pin) di header channel untuk buka panel "PINNED MESSAGES".
7. Cek pesan tadi muncul di panel itu.
8. Klik ikon silang (X) pada pesan di panel itu untuk unpin — konfirmasi
   "Yes, remove it please".
```

**Yang HARUS terjadi:** menu "..." hanya berisi SATU entry "Pin" (bukan dua — pastikan tidak ada entry dobel/aneh dari modul custom). Dialog konfirmasi muncul dan berfungsi untuk pin MAUPUN unpin. Panel "PINNED MESSAGES" menampilkan/menghilangkan pesan dengan benar.

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-08-26 | Docker QA (`pos_margin_sale_migration_18_qa`, live server) | AI, real Chrome (Step 10) | Pass | Menu "..." hanya 1 entry "Pin" (tidak dobel), pin & unpin berfungsi penuh via dialog native |
