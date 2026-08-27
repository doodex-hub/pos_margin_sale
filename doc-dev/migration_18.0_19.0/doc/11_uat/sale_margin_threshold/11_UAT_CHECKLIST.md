# UAT Checklist — Migrasi sale_margin_threshold

**Step:** 11 — UAT Sign-off (final)
**Ref:** `05_acceptance/sale_margin_threshold/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`,
`10_qa/sale_margin_threshold/10_BUSINESS_FLOW_MIGRATION.md`
**Tanggal:** 2026-08-27

> Kriteria sukses: user TIDAK merasakan bedanya dibanding versi 18.0, kecuali item yang memang
> disepakati berubah — **satu pengecualian yang sudah disepakati eksplisit** (lihat "Review Item
> Out-of-Scope" di bawah): bug batch-confirm lama (`MF-08`) SENGAJA dipertahankan, bukan gap
> migrasi baru.
>
> **Dokumen ini test script untuk DIJALANKAN SENDIRI oleh business user/stakeholder** — kolom
> Actual/Status di bawah SENGAJA dikosongkan.

---

## Persiapan Sebelum UAT (Precondition & Data)

- [ ] Modul `sale_margin_threshold` versi 19.0 sudah terinstall di environment staging.
- [ ] Login sebagai user dengan akses Sales (Salesperson, bukan cuma Administrator).
- [ ] Minimal 1 produk dengan `Margin` terisi (contoh: produk "Kursi Kayu", Cost `Rp 100.000`,
  Margin `20%` → minimum sale price `Rp 120.000`).
- [ ] Setting "Block below minimum" (`blocking_transaction_order`) diketahui kondisinya (default:
  TIDAK dicentang → jalur wizard konfirmasi, bukan blocking keras).

## Skenario Test (Test Script)

### T-01: Konfirmasi Sales Order dengan harga di bawah minimum (mode wizard, default)

**Data dummy yang perlu dientri:** Sales Order baru, produk "Kursi Kayu", harga jual diubah jadi
`Rp 80.000` (di bawah minimum `Rp 120.000`).

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buat Sales Order baru, tambahkan produk "Kursi Kayu", ubah harga jadi `Rp 80.000` | Baris tersimpan | | [ ] Pass [ ] Fail |
| 2 | Klik "Confirm" | Muncul popup konfirmasi margin (bukan langsung terkonfirmasi) | | [ ] Pass [ ] Fail |
| 3 | Klik tombol konfirmasi di popup | Order berubah status jadi "Sales Order" (terkonfirmasi) | | [ ] Pass [ ] Fail |

### T-02: Konfirmasi Sales Order dengan mode blocking penuh (kalau setting diaktifkan)

**Precondition:** minta admin mengaktifkan `blocking_transaction_order` dulu.
**Data dummy yang perlu dientri:** sama seperti T-01.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buat Sales Order baru, harga di bawah minimum, klik "Confirm" | Muncul pesan error (bukan popup konfirmasi) | | [ ] Pass [ ] Fail |
| 2 | Perhatikan bahasa pesan error | Pesan sesuai bahasa akun login (Indonesia/Inggris/dst) | | [ ] Pass [ ] Fail |
| 3 | Cek status order | Order TETAP di status "Quotation", tidak terkonfirmasi | | [ ] Pass [ ] Fail |

### T-03: Assign margin massal dari menu Sales

**Data dummy yang perlu dientri:** pilih 2+ produk, Margin = `10`.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka Sales > Products, centang 2+ produk | Baris terpilih ter-highlight | | [ ] Pass [ ] Fail |
| 2 | Klik "Actions" > "Update margin sale", isi `10`, klik "Assign" | Margin SEMUA produk terpilih berubah jadi `10` | | [ ] Pass [ ] Fail |

### T-XX: Item yang TIDAK Bisa Dites Lewat Tampilan Biasa (Informasi, Bukan Kegagalan)

- **Sales Order tipe Rental** — butuh modul Enterprise `sale_renting` yang tidak tersedia di
  environment test/staging ini. Behavior yang diharapkan: order rental TIDAK pernah dicek margin
  sama sekali (`AC-01-01`). Kalau perusahaan memakai Rental, minta tim teknis verifikasi terpisah
  di environment yang punya modul tersebut.

## Sign-off per Kelompok Fitur

| # | Kelompok fitur | Skenario tercakup | Status | Catatan |
|---|---|---|---|---|
| 1 | Konfirmasi order — mode wizard | T-01 | [ ] Pass [ ] Fail | |
| 2 | Konfirmasi order — mode blocking | T-02 | [ ] Pass [ ] Fail | Opsional, hanya kalau perusahaan memakai setting ini |
| 3 | Assign margin massal | T-03 | [ ] Pass [ ] Fail | |

## Review Item Out-of-Scope

Stakeholder mengonfirmasi sadar & menerima item berikut sebagai **behavior lama yang SENGAJA
dipertahankan** (bukan bug baru migrasi 19.0), sesuai keputusan eksplisit saat project ini
berjalan:

- **Konfirmasi banyak Sales Order sekaligus (bulk-select > Confirm dari list view)** — kalau Anda
  mencoba mengonfirmasi 2+ order sekaligus lewat aksi massal, HANYA order PERTAMA di daftar yang
  benar-benar dicek marginnya; order lainnya bisa ikut terkonfirmasi tanpa pengecekan margin.
  **Ini bug warisan sejak versi sebelumnya (`FINDINGS.md` `MF-08`), keputusan dev: dipertahankan
  apa adanya, bukan diperbaiki di migrasi ini.** Kalau proses bisnis Anda mengandalkan
  bulk-confirm, konfirmasi order satu per satu sebagai workaround sampai ada keputusan perbaikan
  terpisah.

## Prasyarat Sebelum Go-Live Produksi

- [ ] Rehearsal upgrade sungguhan — **belum dilakukan di project ini** (Step 7 N/A, port kode
  saja). WAJIB dilakukan terpisah kalau modul ini akan dipasang di atas database produksi 18.0
  yang sudah berisi data nyata.
- [ ] Backup database produksi sebelum upgrade nyata.

## Sign-off

| Role | Nama | Tanggal | Tanda tangan |
|---|---|---|---|
| PM | | | |
| FA | | | |
| User | | | |

> Kosongkan sampai stakeholder benar-benar menjalankan skenario T-01 dst. dengan tangan sendiri dan
> menyetujui.
