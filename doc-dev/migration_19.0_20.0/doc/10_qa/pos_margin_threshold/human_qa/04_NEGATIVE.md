# Negative Test — pos_margin_threshold

**Level:** Negative — input salah, guard/keamanan, hal yang HARUS ditolak atau HARUS TIDAK muncul.
Direkomendasikan dijalankan minimal sekali sebelum rilis besar APAPUN, terlepas dari waktu.

**PERINGATAN KHUSUS FILE INI:** 2 dari 3 flow di bawah **BELUM PERNAH diverifikasi live oleh siapapun**
(AI maupun manusia) sesi migrasi ini — bukan karena diketahui bermasalah, tapi karena AI terhambat
masalah teknis (browser automation gagal total sesi ini, lihat `FINDINGS.md MF-46`) DAN belum ada
keputusan dev final soal salah satunya (lihat Flow 2). **Ini adalah prioritas TERTINGGI untuk
dijalankan manusia**, bukan sekadar formalitas.

**Estimasi waktu:** ~10 menit.
**Sumber:** S-19, S-20, S-21 di `../10_BUSINESS_FLOW_MIGRATION.md`.

## Flow 1 — Batalkan pembayaran (klik "Decline"/tutup dialog, bukan konfirmasi) [BELUM PERNAH DIVERIFIKASI]

```
1. Di POS, tambahkan produk yang harganya di bawah minimum ke keranjang.
2. Klik "Pay" -> dialog peringatan muncul.
3. JANGAN klik tombol konfirmasi/lanjut — klik tombol TUTUP/batal/silang dialog, atau klik di luar
   dialog (dismiss).
4. Pastikan: kasir TETAP di layar produk (ProductScreen), TIDAK lanjut ke layar pembayaran.
5. Pastikan produk yang tadi ditambahkan MASIH ADA di keranjang (tidak hilang/ke-reset).
6. Coba klik "Pay" lagi -> pastikan dialog yang SAMA muncul lagi normal (tidak error/stuck).
```

## Flow 2 — Pastikan TIDAK ADA dialog sama sekali kalau semua harga sudah di atas minimum [BELUM PERNAH DIVERIFIKASI — juga BELUM ADA KEPUTUSAN DEV, lihat catatan]

```
1. Di POS, tambahkan HANYA produk yang harganya SUDAH di atas minimum masing-masing (semua baris
   aman, tidak ada satupun di bawah minimum).
2. Klik "Pay".
3. Pastikan TIDAK ADA dialog/popup apapun yang muncul (termasuk tidak ada yang muncul sekilas lalu
   hilang sendiri).
4. Lanjutkan ke pembayaran seperti biasa.
```

**Catatan untuk flow ini:** perilaku ini sudah "dianggap benar secara desain" oleh 3 tim migrasi
berturut-turut tanpa pernah benar-benar dites/diputuskan secara sadar. Kalau kamu menjalankan ini dan
menemukan dialog TETAP muncul padahal semua harga aman — ini kemungkinan besar bug nyata, laporkan
segera (bukan sekadar catatan proses).

## Flow 3 — Tidak ada dialog ganda dari satu aksi (sudah dikonfirmasi aman, cek ulang kalau ada perubahan)

```
1. Klik "Pay" dengan kondisi apapun (di atas/di bawah minimum, mode blocking on/off).
2. Pastikan HANYA SATU dialog yang muncul dalam satu waktu (tidak pernah dua dialog bertumpuk).
```

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-09-23 | Docker 20.0 QA | AI (Step 10) | **Flow 1 & 2: Pending, TIDAK dijalankan** (blocker teknis + Flow 2 juga menunggu keputusan dev — lihat `10_BUSINESS_FLOW_MIGRATION.md` S-19/S-20 untuk detail ESCALATION). Flow 3: Pass (dikonfirmasi via baca kode, struktur if/else tunggal). | **Flow 1 dan 2 WAJIB dijalankan manusia** sebelum rilis besar — jangan andalkan baris "Pass" manapun di dokumen lain untuk item ini, keduanya genuinely belum pernah dilihat siapapun bekerja di versi 20.0 ini. |
