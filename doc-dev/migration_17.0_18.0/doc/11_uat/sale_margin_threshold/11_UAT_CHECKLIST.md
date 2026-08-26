# UAT Checklist — Migrasi sale_margin_threshold

**Step:** 11 — UAT Sign-off (final)
**Ref:** `05_acceptance/sale_margin_threshold/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `10_qa/sale_margin_threshold/10_BUSINESS_FLOW_MIGRATION.md`
**Tanggal:** 2026-08-26

> Kriteria sukses: sales admin TIDAK merasakan bedanya konfirmasi Sales Order/Quotation dibanding sebelum migrasi, kecuali item yang memang disepakati berubah.
>
> **PENTING sebelum mulai UAT — konfirmasi ke IT/dev:** apakah bahasa Prancis (`fr_FR`) perlu diinstall di environment ini? Modul ini SEBELUMNYA butuh itu untuk pesan bilingual, tapi sudah diperbaiki (2026-08-26) supaya TIDAK butuh lagi — kalau UAT dilakukan di environment yang masih versi kode LAMA (sebelum fix ini), gejalanya: konfirmasi quotation crash dengan pesan error bahasa Inggris teknis (`Invalid language code`). Kalau itu terjadi, laporkan ke dev, JANGAN dianggap gagal UAT sampai dikonfirmasi versi kode yang benar sudah dipakai.
>
> **Dokumen ini draft test script — WAJIB dijalankan sendiri oleh user/stakeholder** (misal: sales admin), bukan laporan AI. Kolom **Actual** dan **Status** DIBIARKAN KOSONG — isi sendiri.

---

## Persiapan Sebelum UAT

- [ ] Modul `sale_margin_threshold` versi 18.0 terinstall di database staging.
- [ ] Login sebagai user dengan role **Sales User** (bukan cuma Administrator) untuk T-01/T-02. Login **Administrator** untuk T-03.
- [ ] Ada produk dengan harga minimum jual sudah dikonfigurasi, mis. **"Meja Kantor"**, minimum jual Rp 1.000.000.
- [ ] Setidaknya 1 pelanggan (customer) dummy sudah ada untuk dipakai bikin quotation.

## Skenario Test (Test Script)

### T-01: Confirm quotation dengan harga di bawah minimum — mode "wajib diblokir"

**Data dummy yang perlu dientri:** Quotation baru untuk pelanggan apapun, produk "Meja Kantor" dengan harga jual diubah manual jadi Rp 800.000 (di bawah minimum Rp 1.000.000).

**Precondition:** Setting "Blocking Transaction Order" di Settings > Sales **DICENTANG**.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buat quotation baru, tambah "Meja Kantor" harga Rp 800.000 | Baris produk masuk quotation | | [ ] Pass [ ] Fail |
| 2 | Klik tombol "Confirm" | Muncul pesan error yang jelas (bukan technical/crash aneh), quotation TETAP status draft, tidak jadi Sales Order | | [ ] Pass [ ] Fail |

### T-02: Confirm quotation dengan harga di bawah minimum — mode "boleh lanjut dengan konfirmasi"

**Data dummy yang perlu dientri:** Sama seperti T-01.

**Precondition:** Setting "Blocking Transaction Order" **TIDAK dicentang**.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buat quotation baru, produk sama seperti T-01 | Baris produk masuk quotation | | [ ] Pass [ ] Fail |
| 2 | Klik "Confirm" | Muncul jendela pop-up konfirmasi bertanya apakah mau lanjut walau di bawah minimum | | [ ] Pass [ ] Fail |
| 3 | Klik "Confirm" di jendela pop-up itu | Quotation benar-benar berubah status jadi "Sales Order" | | [ ] Pass [ ] Fail |
| 4 | Ulangi langkah 1-2, tapi kali ini klik "Cancel" di jendela pop-up | Jendela tertutup, quotation TETAP draft, tidak ada perubahan apapun | | [ ] Pass [ ] Fail |

### T-03: Confirm banyak quotation sekaligus (Administrator) — perilaku existing, JANGAN dianggap bug

**Data dummy yang perlu dientri:** 2 atau lebih quotation baru, tidak perlu produk khusus.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Di list Quotations, centang 2 quotation atau lebih sekaligus | Terpilih beberapa baris | | [ ] Pass [ ] Fail |
| 2 | Klik action "Confirm" (batch) | **Muncul error teknis** ("Expected singleton" atau serupa) — INI PERILAKU YANG SUDAH ADA SEJAK SEBELUM MIGRASI, bukan bug baru. Kalau muncul error ini, itu justru TANDA BENAR (konsisten dengan versi lama). Kalau TIDAK ADA error sama sekali dan batch-confirm malah berhasil mulus, **laporkan ke dev** — itu perubahan perilaku yang tidak terduga. | | [ ] Pass [ ] Fail |

### T-XX: Item yang TIDAK Bisa Dites Lewat Tampilan Biasa (Informasi, Bukan Kegagalan)

- **Skip validasi untuk order rental** — hanya relevan kalau perusahaan memakai Odoo Enterprise dengan modul Rental aktif. Kalau tidak memakai Rental, skenario ini tidak berlaku untuk instalasi Anda dan boleh dilewati.

## Sign-off per Kelompok Fitur

| # | Kelompok fitur | Skenario tercakup | Status | Catatan |
|---|---|---|---|---|
| 1 | Confirm quotation dengan validasi harga minimum | T-01, T-02 | [ ] Pass [ ] Fail | |
| 2 | Batch confirm (perilaku existing) | T-03 | [ ] Pass [ ] Fail | |

## Review Item Out-of-Scope

Stakeholder mengonfirmasi sadar & menerima:

- Batch-confirm quotation lewat list view TETAP error (bug lama, `MF-06`, sengaja dipertahankan identik 17.0 — bukan diperbaiki saat migrasi).
- Saat modul ini DAN `pos_margin_threshold` sama-sama terinstall, field "Margin"/"Minimum sale price" pada form produk yang tampil adalah versi `pos_margin_threshold` (tidak dobel) — perilaku identik 17.0.

## Prasyarat Sebelum Go-Live Produksi

- [ ] Backup database produksi sebelum deploy versi 18.0.
- [ ] **Konfirmasi eksplisit:** environment production TIDAK perlu bahasa Prancis terinstall lagi (sudah diperbaiki via kode, bukan syarat deployment) — cukup pastikan versi kode yang dipakai sudah termasuk fix `MF-21` (2026-08-26).
- [ ] Item risiko rendah yang belum sempat dites AI (lihat `10_qa/sale_margin_threshold/10_BUSINESS_FLOW_MIGRATION.md` §Deferred): kalau perusahaan memakai modul Rental Enterprise, cek manual bahwa order rental TIDAK kena validasi harga minimum sama sekali.

## Sign-off

| Role | Nama | Tanggal | Tanda tangan |
|---|---|---|---|
| PM | | | |
| FA | | | |
| User | | | |

> Kosongkan sampai stakeholder benar-benar menjalankan skenario T-01 dst. dengan tangan sendiri dan menyetujui.
