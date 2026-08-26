# UAT Checklist — Migrasi pos_margin_threshold

**Step:** 11 — UAT Sign-off (final)
**Ref:** `05_acceptance/pos_margin_threshold/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `10_qa/pos_margin_threshold/10_BUSINESS_FLOW_MIGRATION.md`
**Tanggal:** 2026-08-26

> Kriteria sukses: kasir/admin TIDAK merasakan bedanya menjual produk lewat POS dibanding sebelum migrasi ke Odoo 18, kecuali kalau memang ada perubahan yang disengaja (tidak ada untuk modul ini — port murni).
>
> **Dokumen ini draft test script — WAJIB dijalankan sendiri oleh user/stakeholder yang akan pakai modul ini sehari-hari** (misal: manajer toko, admin produk), bukan laporan hasil test AI/developer. Kolom **Actual** dan **Status** DIBIARKAN KOSONG di bawah ini — isi sendiri setelah benar-benar mencoba langkahnya, jangan disalin dari catatan Step 9/10 (yang dijalankan AI, tujuannya beda).

---

## Persiapan Sebelum UAT

- [ ] Modul `pos_margin_threshold` versi 18.0 sudah terinstall di database staging (BUKAN produksi asli).
- [ ] Login sebagai user dengan role **Kasir POS** (bukan cuma Administrator) untuk skenario T-01/T-02 — supaya UAT juga memvalidasi hak akses kasir standar. Login **Administrator** untuk T-03.
- [ ] Ada minimal 1 produk POS dengan `standard_price` (Cost) terisi, mis. **"Kopi Susu"**, Cost = Rp 10.000, dijual seharga Rp 15.000.
- [ ] Sesi POS (Point of Sale) sudah dikonfigurasi dan bisa dibuka normal.
- [ ] Menu Settings > Sales/Inventory bisa diakses untuk cek konfigurasi "Blocking Transaction POS".

## Skenario Test (Test Script)

### T-01: Jual produk dengan harga di bawah batas minimum — mode "boleh lanjut dengan konfirmasi"

**Data dummy yang perlu dientri:** Produk "Kopi Susu" (Cost Rp 10.000, margin 50% → minimum jual Rp 15.000). Di kasir, jual dengan harga custom Rp 12.000 (di bawah minimum).

**Precondition:** Setting "Blocking Transaction POS" di **TIDAK dicentang** (mode default — cek Settings > Point of Sale).

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka POS, buka kasir/register seperti biasa | Kasir terbuka normal, tidak ada error | | [ ] Pass [ ] Fail |
| 2 | Tambahkan "Kopi Susu" ke keranjang, ubah harga jadi Rp 12.000 lewat numpad | Produk masuk keranjang dengan harga Rp 12.000 | | [ ] Pass [ ] Fail |
| 3 | Klik tombol "Pay" (Bayar) | Muncul jendela peringatan "harga di bawah minimum, lanjutkan?" dengan pilihan lanjut/batal | | [ ] Pass [ ] Fail |
| 4 | Klik "Lanjut"/tombol konfirmasi | Kasir lanjut ke layar pembayaran seperti biasa, pembayaran bisa diselesaikan | | [ ] Pass [ ] Fail |

### T-02: Jual produk dengan harga di bawah batas minimum — mode "wajib diblokir"

**Data dummy yang perlu dientri:** Sama seperti T-01.

**Precondition:** Setting "Blocking Transaction POS" di Settings **DICENTANG**.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka POS, ulangi langkah tambah "Kopi Susu" seharga Rp 12.000 | Produk masuk keranjang | | [ ] Pass [ ] Fail |
| 2 | Klik "Pay" | Muncul jendela peringatan TANPA pilihan lanjut — cuma tombol "Ok"/tutup | | [ ] Pass [ ] Fail |
| 3 | Tutup jendela peringatan itu | Kasir TIDAK pindah ke layar pembayaran — tetap di keranjang belanja, transaksi benar-benar diblokir | | [ ] Pass [ ] Fail |

### T-03: Ubah margin banyak produk sekaligus (Administrator)

**Data dummy yang perlu dientri:** Pilih 2-3 produk apapun di menu Products.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka Inventory > Products, tampilan List, centang 2-3 produk | Produk terpilih, muncul badge "N selected" di atas | | [ ] Pass [ ] Fail |
| 2 | Klik "Actions" > "Update margin sale" | Jendela pop-up terbuka, daftar produk yang dipilih sudah terisi otomatis | | [ ] Pass [ ] Fail |
| 3 | Isi angka margin (mis. 25), klik "Assign" | Jendela tertutup, tidak ada error | | [ ] Pass [ ] Fail |
| 4 | Buka salah satu produk yang tadi dipilih | Kolom "Margin" = 25%, kolom "Minimum sale price" ikut ter-update sesuai rumus Cost × (1+Margin/100) | | [ ] Pass [ ] Fail |

### T-XX: Item yang TIDAK Bisa Dites Lewat Tampilan Biasa (Informasi, Bukan Kegagalan)

- Tidak ada — semua fitur modul ini reachable dari UI POS/backend biasa.

## Sign-off per Kelompok Fitur

| # | Kelompok fitur | Skenario tercakup | Status | Catatan |
|---|---|---|---|---|
| 1 | Penjualan POS dengan peringatan harga minimum | T-01, T-02 | [ ] Pass [ ] Fail | |
| 2 | Ubah margin massal (admin) | T-03 | [ ] Pass [ ] Fail | |

## Review Item Out-of-Scope

Stakeholder mengonfirmasi sadar & menerima:

- Bug lama 17.0 tetap dipertahankan apa adanya (bukan diperbaiki): margin per-variant tidak bisa berbeda dari template induk (`MF-01`); saat modul ini DAN `sale_margin_threshold` sama-sama terinstall, wizard "assign margin" yang benar-benar berjalan adalah versi `sale_margin_threshold` (`MF-03`) — perilaku identik dengan sebelum migrasi.

## Prasyarat Sebelum Go-Live Produksi

- [ ] Rehearsal upgrade sungguhan (kalau nanti ada data produksi asli untuk dimigrasikan — saat ini project bersifat port kode saja, tidak ada data produksi yang dimigrasikan, jadi item ini kemungkinan N/A, tapi tetap dicek eksplisit oleh stakeholder).
- [ ] Backup database produksi sebelum deploy versi 18.0.
- [ ] Item risiko rendah yang belum sempat dites AI (lihat `10_qa/pos_margin_threshold/10_BUSINESS_FLOW_MIGRATION.md` §Deferred) — direkomendasikan dicek sekalian saat UAT kalau ada waktu: (a) jual produk yang harganya SUDAH di atas minimum, pastikan TIDAK ada peringatan apapun; (b) lihat baris produk di bawah minimum di keranjang POS, pastikan ada teks peringatan berwarna merah.

## Sign-off

| Role | Nama | Tanggal | Tanda tangan |
|---|---|---|---|
| PM | | | |
| FA | | | |
| User | | | |

> Kosongkan sampai stakeholder benar-benar menjalankan skenario T-01 dst. dengan tangan sendiri dan menyetujui.
