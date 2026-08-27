# UAT Checklist — Migrasi pos_margin_threshold

**Step:** 11 — UAT Sign-off (final)
**Ref:** `05_acceptance/pos_margin_threshold/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`,
`10_qa/pos_margin_threshold/10_BUSINESS_FLOW_MIGRATION.md`
**Tanggal:** 2026-08-27

> Kriteria sukses: user TIDAK merasakan bedanya dibanding versi 18.0, kecuali item yang memang
> disepakati berubah (tidak ada — migrasi ini port kode saja, tidak ada perubahan fitur/behavior
> yang disengaja).
>
> **Dokumen ini test script untuk DIJALANKAN SENDIRI oleh business user/stakeholder** — kolom
> Actual/Status di bawah SENGAJA dikosongkan, bukan diisi AI/developer. AI (Claude Code) hanya
> menyiapkan langkah dan data dummy.

---

## Persiapan Sebelum UAT (Precondition & Data)

- [ ] Modul `pos_margin_threshold` versi 19.0 sudah terinstall di environment staging (bukan
  produksi asli).
- [ ] Login sebagai user dengan akses Point of Sale + Inventory (bukan cuma Administrator).
- [ ] Minimal 1 produk sudah ada, harga jual (`Sales Price`) dan biaya (`Cost`) diisi (contoh:
  produk "Kursi Kayu", Cost `Rp 100.000`, Sales Price `Rp 150.000`).
- [ ] Sesi kasir POS bisa dibuka (`Point of Sale > Sesi baru`).

## Skenario Test (Test Script)

### T-01: Atur margin minimum untuk satu produk

**Data dummy yang perlu dientri:** produk "Kursi Kayu", isi field `Margin` = `20` (persen).

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka Inventory > Products > "Kursi Kayu" | Form produk terbuka | | [ ] Pass [ ] Fail |
| 2 | Isi field "Margin" dengan `20` | Field "Minimum sale price" otomatis terhitung (`Cost x 1.20`) | | [ ] Pass [ ] Fail |
| 3 | Simpan | Perubahan tersimpan tanpa error | | [ ] Pass [ ] Fail |

### T-02: Assign margin massal ke banyak produk sekaligus (wizard)

**Data dummy yang perlu dientri:** pilih 2+ produk apapun di list, isi Margin = `15`.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka Inventory > Products (tampilan list), centang 2 produk atau lebih | Baris terpilih ter-highlight | | [ ] Pass [ ] Fail |
| 2 | Klik "Actions" > "Update margin sale" | Popup "Update margin sale" terbuka, menampilkan daftar produk yang dipilih | | [ ] Pass [ ] Fail |
| 3 | Isi Margin = `15`, klik "Assign" | Popup tertutup, SEMUA produk yang dipilih margin-nya berubah jadi `15` | | [ ] Pass [ ] Fail |
| 4 | Ulangi langkah 1-2, isi Margin = `99`, klik "Cancel" (bukan Assign) | Popup tertutup, margin produk TIDAK berubah (tetap `15`) | | [ ] Pass [ ] Fail |

### T-03: Jual produk di bawah harga minimum di kasir POS (mode konfirmasi)

**Precondition:** setting "Block below minimum" (`blocking_transaction_pos`) di kondisi default
(TIDAK dicentang).
**Data dummy yang perlu dientri:** di kasir, ubah harga jual produk "Kursi Kayu" jadi lebih rendah
dari minimum (misal `Rp 50.000`).

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka sesi kasir POS, tambahkan "Kursi Kayu" ke pesanan | Produk masuk keranjang | | [ ] Pass [ ] Fail |
| 2 | Ubah harga baris jadi `Rp 50.000` (di bawah minimum) | Baris pesanan berubah warna/ada peringatan harga di bawah minimum | | [ ] Pass [ ] Fail |
| 3 | Klik "Payment"/"Bayar" | Muncul dialog konfirmasi "Some products are below the minimum price. Proceed to payment?" | | [ ] Pass [ ] Fail |
| 4 | Klik "Batal"/tolak dialog | Tetap di layar produk, pesanan tidak lanjut ke pembayaran | | [ ] Pass [ ] Fail |
| 5 | Ulangi, kali ini klik "Konfirmasi"/setuju dialog | Lanjut ke layar pembayaran seperti biasa | | [ ] Pass [ ] Fail |

### T-XX: Item yang TIDAK Bisa Dites Lewat Tampilan Biasa (Informasi, Bukan Kegagalan)

- **Mode "Block below minimum" (blocking penuh, tanpa opsi lanjut)** — butuh setting tambahan
  (`blocking_transaction_pos = True`) yang tidak aktif secara default. Kalau perusahaan memakai mode
  ini, minta admin mengaktifkannya dulu sebelum UAT, lalu ulangi T-03 langkah 3 — hasil yang
  diharapkan berubah jadi dialog PERINGATAN TANPA tombol lanjut (pembayaran diblokir total).
- **Sesi kasir dengan SEMUA baris di atas/sama minimum** — behavior yang diharapkan: TIDAK ADA
  dialog apapun muncul, langsung ke pembayaran. Sudah divalidasi tim teknis (Step 9/10) lewat jalur
  Tour test otomatis untuk kasus below-minimum; kasus "semua valid" ini silakan dicoba sendiri saat
  UAT sebagai sanity check tambahan (bukan wajib, risiko rendah).

## Sign-off per Kelompok Fitur

| # | Kelompok fitur | Skenario tercakup | Status | Catatan |
|---|---|---|---|---|
| 1 | Margin & harga minimum per produk | T-01 | [ ] Pass [ ] Fail | |
| 2 | Assign margin massal | T-02 | [ ] Pass [ ] Fail | |
| 3 | Enforcement harga minimum di kasir POS | T-03 | [ ] Pass [ ] Fail | |

## Review Item Out-of-Scope

Tidak ada item out-of-scope untuk modul ini — migrasi murni port kode, tidak ada perubahan
fitur/behavior yang disengaja (lihat `03_MIGRATION_SPEC.md`).

## Prasyarat Sebelum Go-Live Produksi

- [ ] Rehearsal upgrade sungguhan (clone data produksi → jalankan urutan upgrade nyata →
  spot-check data) — **belum dilakukan di project ini** (Step 7 N/A karena tidak ada data produksi
  yang perlu dimigrasi, port kode saja). Kalau di masa depan modul ini dipasang di atas database
  produksi 18.0 yang sudah berisi data nyata, rehearsal upgrade tetap WAJIB dilakukan terpisah
  sebelum go-live — dokumen ini tidak menggantikannya.
- [ ] Backup database produksi sebelum upgrade nyata.

## Sign-off

| Role | Nama | Tanggal | Tanda tangan |
|---|---|---|---|
| PM | | | |
| FA | | | |
| User | | | |

> Kosongkan sampai stakeholder benar-benar menjalankan skenario T-01 dst. dengan tangan sendiri dan
> menyetujui.
