# Negative Test — pin_message

**Level:** Negative — input salah, guard/keamanan, hal yang HARUS ditolak atau HARUS TIDAK muncul. Direkomendasikan dijalankan minimal sekali sebelum rilis besar APAPUN, terlepas dari waktu — ini soal keamanan, bukan cuma fungsi.
**Estimasi waktu:** ~3 menit.
**Sumber:** skenario ber-`Level: Negative` di `../10_BUSINESS_FLOW_MIGRATION.md`.

## Discuss-channel native pin tidak terganggu modul ini (dead code aman)

```
1. Buka Discuss, masuk ke channel apapun.
2. Kirim pesan baru.
3. Hover pesan, buka menu aksi bawaan (native "mail", bukan chatter Pinned Messages modul ini).
4. Klik aksi pin native.
5. Cek: TIDAK ADA error muncul di halaman (buka DevTools Console kalau ragu — harus bersih, tidak
   ada baris merah).
6. Cek: pin native berfungsi normal (ikon pin muncul di pesan).
```

**Kenapa ini penting:** modul `pin_message` punya cabang kode `is_discussion` di `onClickPin()`
yang secara desain tidak pernah tereksekusi lewat jalur native ini (dead code, warisan sejak versi
sebelumnya) — skenario ini membuktikan dead code tersebut TIDAK ikut pecah/mengganggu jalur native
saat migrasi 19.0.

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-08-27 | Docker `odoo:19.0`, db `pos_margin_sale_migration_19_qa` | AI (Playwright, `qa_step10.js`) | Pass | S-10-01 — 0 console error di seluruh run 6 skenario |
