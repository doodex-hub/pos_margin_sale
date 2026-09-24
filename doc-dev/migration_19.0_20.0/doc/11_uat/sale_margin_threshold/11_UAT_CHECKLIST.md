# UAT Checklist — Migrasi `sale_margin_threshold` (Odoo 19.0 → 20.0)

**Step:** 11 — UAT Sign-off (final)
**Ref:** `05_acceptance/sale_margin_threshold/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`,
`10_qa/sale_margin_threshold/10_BUSINESS_FLOW_MIGRATION.md`
**Tanggal disiapkan:** 2026-09-24
**Disiapkan oleh:** AI (migration copilot) — **belum dijalankan siapapun**

> **Kriteria sukses: Anda TIDAK merasakan bedanya dibanding Odoo 19.0.** Modul ini dimigrasi dengan
> prinsip "port kode saja" — tidak ada fitur baru, tidak ada perubahan aturan bisnis. Kalau saat
> menjalankan skenario di bawah Anda merasa ada yang "beda dari biasanya", itu justru temuan penting,
> tolong tulis di kolom Actual.

> **Dokumen ini adalah skrip test untuk DIJALANKAN SENDIRI oleh Anda (PM/FA/User), bukan laporan
> hasil test AI.** Kolom **Actual** dan **Status** sengaja dikosongkan — AI tidak boleh mengisinya.

---

## Persiapan Sebelum UAT (Precondition & Data)

- [ ] Odoo **20.0** dengan modul **Sales** dan **`sale_margin_threshold`** sudah terinstall.
- [ ] **Kalau `pos_margin_threshold` juga dipakai di produksi, install KEDUANYA bersamaan** di
      environment UAT ini — skenario T-05 memang menguji bahwa kolom tidak tampil dobel.
- [ ] Login pakai user **dengan role Sales biasa**, bukan Administrator — supaya hak akses standar
      ikut tervalidasi. Untuk langkah yang mengubah Settings, boleh Administrator; catat di kolom
      Actual kalau Anda harus ganti user.
- [ ] Database UAT adalah **salinan/staging**, bukan produksi asli.
- [ ] Sudah ada **1 pelanggan** untuk dipakai di Sale Order (mis. `UAT Pelanggan Coba`).
- [ ] **Kalau bisnis Anda memakai fitur Rental** (modul `sale_renting` / Odoo Enterprise), pastikan
      modul itu juga terinstall — dibutuhkan untuk T-04. Kalau tidak dipakai, lewati T-04.

### Data dummy yang perlu Anda siapkan lebih dulu

| Nama produk | Cost / Harga Beli | Margin | Sales Price | Catatan |
|---|---|---|---|---|
| `UAT Jasa Murah` | 100.000 | 50 | **80.000** | sengaja DI BAWAH minimum |
| `UAT Jasa Normal` | 100.000 | 50 | **200.000** | sengaja DI ATAS minimum |
| `UAT Jasa Rugi` | 100.000 | **-10** | 80.000 | margin negatif, untuk cek warna merah di daftar |

> Dengan Cost 100.000 dan Margin 50, **Minimum sale price = 150.000**. Jadi `UAT Jasa Murah` (80.000)
> ada di bawah minimum, `UAT Jasa Normal` (200.000) di atas minimum.

---

## Skenario Test (Test Script)

### T-01: Konfirmasi Sale Order NORMAL (tidak boleh diganggu)

> Menguji bahwa modul tidak "cerewet" pada order yang wajar.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka **Sales ▸ Orders ▸ Quotations**, buat quotation baru untuk `UAT Pelanggan Coba` | Form quotation terbuka | | [ ] Pass [ ] Fail |
| 2 | Tambah 1 baris: `UAT Jasa Normal`, qty `1`, harga biarkan `200.000` | Baris masuk, tampil **normal (tidak merah)** | | [ ] Pass [ ] Fail |
| 3 | Klik **Confirm** | Order **langsung terkonfirmasi** jadi Sales Order — tidak ada peringatan, tidak ada popup apapun | | [ ] Pass [ ] Fail |

### T-02: Konfirmasi Sale Order di bawah minimum — mode NORMAL (boleh lanjut lewat konfirmasi)

**Pastikan dulu:** buka **Sales ▸ Configuration ▸ Settings**, pastikan **"Blocking Transaction
Order" TIDAK dicentang**, Save.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buat quotation baru untuk `UAT Pelanggan Coba` | Form terbuka | | [ ] Pass [ ] Fail |
| 2 | Tambah baris `UAT Jasa Murah`, qty `1`, harga `80.000` | Baris masuk | | [ ] Pass [ ] Fail |
| 3 | Perhatikan baris itu di daftar Order Lines | Baris tampil **MERAH** (menandakan harga di bawah minimum) | | [ ] Pass [ ] Fail |
| 4 | Klik **Confirm** | Muncul **jendela konfirmasi** berisi pesan peringatan harga di bawah minimum | | [ ] Pass [ ] Fail |
| 5 | Perhatikan status order di belakang jendela itu | Masih **Quotation/draft** — belum terkonfirmasi | | [ ] Pass [ ] Fail |
| 6 | Klik tombol **konfirmasi** di jendela tersebut | Jendela tertutup, order **berubah jadi Sales Order** (terkonfirmasi) | | [ ] Pass [ ] Fail |

### T-03: Konfirmasi di bawah minimum — tombol BATAL di jendela konfirmasi

> Jalur ini belum punya test otomatis — tolong dijalankan dengan teliti.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Ulangi T-02 langkah 1-4 sampai jendela konfirmasi muncul | Jendela konfirmasi tampil | | [ ] Pass [ ] Fail |
| 2 | Klik tombol **Cancel / batal** di jendela itu (BUKAN konfirmasi) | Jendela tertutup | | [ ] Pass [ ] Fail |
| 3 | Perhatikan status order | Tetap **Quotation/draft** — TIDAK terkonfirmasi | | [ ] Pass [ ] Fail |
| 4 | Perhatikan isi order | Baris pesanan **masih utuh**, harga dan qty tidak berubah | | [ ] Pass [ ] Fail |
| 5 | Klik **Confirm** lagi, lalu konfirmasi | Bisa lanjut normal — pembatalan tadi tidak merusak apa-apa | | [ ] Pass [ ] Fail |

### T-04: Order RENTAL dikecualikan total dari pengecekan margin

> **Lewati skenario ini kalau bisnis Anda tidak memakai fitur Rental.**

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buat order **Rental** untuk `UAT Pelanggan Coba`, isi tanggal mulai & tanggal kembali | Form rental terbuka | | [ ] Pass [ ] Fail |
| 2 | Tambah baris `UAT Jasa Murah` dengan harga jauh di bawah minimum (mis. `50.000`) | Baris masuk | | [ ] Pass [ ] Fail |
| 3 | Perhatikan warna baris | Baris **TIDAK merah** — pengecekan margin memang sengaja tidak berlaku untuk rental | | [ ] Pass [ ] Fail |
| 4 | Klik **Confirm** | Order **langsung terkonfirmasi**, TANPA peringatan/jendela konfirmasi apapun | | [ ] Pass [ ] Fail |

### T-05: Kolom margin di daftar "Product Variants"

> Bagian yang **paling berubah tampilannya** dibanding 19.0 — baca §"Perubahan yang Memang Disengaja"
> di bawah sebelum menilai Pass/Fail.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka **Inventory/Sales ▸ Products ▸ Products**, buka `UAT Jasa Murah`, klik smart-button **Variants** | Muncul daftar Product Variants | | [ ] Pass [ ] Fail |
| 2 | Perhatikan kolom yang tampil | Ada kolom **Margin**, **Minimum sale price**, dan **Incl. Tax** | | [ ] Pass [ ] Fail |
| 3 | Hitung ada berapa kolom "Margin" dan "Minimum sale price" | **Masing-masing HANYA SATU**, tidak dobel — termasuk kalau `pos_margin_threshold` juga terinstall | | [ ] Pass [ ] Fail |
| 4 | Lihat baris `UAT Jasa Rugi` (margin `-10`) | Angka **Margin** dan **Sales Price** tampil **MERAH** | | [ ] Pass [ ] Fail |
| 5 | Lihat baris `UAT Jasa Normal` | Angkanya **normal/hitam**, tidak merah | | [ ] Pass [ ] Fail |
| 6 | Klik sel **Margin** salah satu baris, ubah angkanya, Save | Bisa diedit langsung; **Minimum sale price** ikut menyesuaikan | | [ ] Pass [ ] Fail |

### T-06: Mode "blokir total" untuk Sale Order

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka **Sales ▸ Configuration ▸ Settings**, centang **"Blocking Transaction Order"**, Save | Setting tersimpan | | [ ] Pass [ ] Fail |
| 2 | Buat quotation baru berisi `UAT Jasa Murah` (80.000) | Baris masuk, tampil merah | | [ ] Pass [ ] Fail |
| 3 | Klik **Confirm** | Muncul **pesan error** yang menolak konfirmasi — BUKAN jendela konfirmasi yang bisa dilanjutkan | | [ ] Pass [ ] Fail |
| 4 | Tutup pesan error, perhatikan status order | Tetap **Quotation/draft**, tidak bisa dikonfirmasi sama sekali selama harga masih di bawah minimum | | [ ] Pass [ ] Fail |
| 5 | Ubah harga baris jadi `200.000`, klik **Confirm** | Order terkonfirmasi normal | | [ ] Pass [ ] Fail |
| 6 | **Kembalikan setting**: hilangkan centang "Blocking Transaction Order", Save | Setting kembali seperti semula | | [ ] Pass [ ] Fail |

### T-07: Pesan peringatan dalam Bahasa Prancis (hanya kalau relevan)

> **Lewati kalau tidak ada user berbahasa Prancis.** Modul ini punya penanganan bahasa khusus yang
> sengaja dipertahankan: **hanya membedakan Prancis vs selain-Prancis**.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Ubah bahasa user Anda ke **Français**, ulangi T-02 | Pesan peringatan tampil dalam **Bahasa Prancis** | | [ ] Pass [ ] Fail |
| 2 | Ubah bahasa user ke **Bahasa Indonesia**, ulangi T-02 | Pesan peringatan tampil dalam **Bahasa Inggris** (bukan Indonesia) — ini memang perilaku lama yang dipertahankan, bukan kerusakan | | [ ] Pass [ ] Fail |

### T-08: Ubah margin banyak produk sekaligus (wizard)

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka daftar **Products**, centang `UAT Jasa Murah` dan `UAT Jasa Normal` | Dua produk tercentang | | [ ] Pass [ ] Fail |
| 2 | Buka menu **Actions / ⚙️**, pilih aksi terkait **Update margin sale** | Muncul jendela isian margin | | [ ] Pass [ ] Fail |
| 3 | Isi margin = `25`, konfirmasi | Kedua produk ter-update Margin = `25`, **Minimum sale price** jadi `125.000` | | [ ] Pass [ ] Fail |

### T-09: Konfirmasi BANYAK order sekaligus (batch) — perilaku lama yang dipertahankan

> **Penting: skenario ini sengaja menguji sesuatu yang MEMANG BERMASALAH sejak versi lama**, dan
> keputusan yang sudah diambil adalah **dipertahankan apa adanya**, bukan diperbaiki di migrasi ini.
> Tujuan T-09 bukan mencari bug, tapi memastikan perilakunya **sama persis** seperti di 19.0.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buat **2 quotation** yang masing-masing berisi `UAT Jasa Murah` (di bawah minimum) | Dua quotation draft | | [ ] Pass [ ] Fail |
| 2 | Dari daftar Quotations, **centang keduanya**, lalu jalankan aksi Confirm massal | Terjadi **error** (bukan proses yang mulus) — ini perilaku lama yang memang diketahui dan sengaja dipertahankan | | [ ] Pass [ ] Fail |
| 3 | Catat: apakah error-nya terasa **sama** seperti di Odoo 19.0? | Sama, tidak lebih buruk | | [ ] Pass [ ] Fail |

> Kalau menurut Anda perilaku ini **mengganggu operasional sehari-hari**, tolong tulis di kolom
> Actual — itu bahan untuk keputusan perbaikan **terpisah** di luar migrasi ini.

### T-10: Item yang TIDAK Bisa Dites Lewat Tampilan Biasa (Informasi, Bukan Kegagalan)

- **Pengaturan hak akses grup (`security/groups.xml`)** — ada keanehan lama pada konfigurasi grup
  (`MF-20`) yang sengaja dibawa apa adanya. Tidak terlihat sebagai menu/tombol.
- **Tabrakan nama internal wizard** dengan `pos_margin_threshold` (`MF-03`/`BSL-010`) — dua modul
  mendefinisikan wizard bernama sama; sengaja dipertahankan. Efeknya hanya di balik layar.
- **Mekanisme internal penyembunyian kolom** saat kedua modul terinstall bersamaan — yang perlu Anda
  nilai cuma hasil akhirnya di T-05 langkah 3 (kolom tidak dobel).
- **Terjemahan file `.po`** tidak diupdate untuk teks baru (`MF-39`) — teks baru tampil dalam Bahasa
  Inggris. Disengaja.

---

## Perubahan yang Memang Disengaja (WAJIB dibaca sebelum menilai T-05)

Di Odoo 19.0, margin/minimum sale price diubah lewat **popup "edit cepat"** pada varian produk.
**Popup itu DIHAPUS oleh Odoo 20.0 sendiri** — bukan oleh kami, dan tidak bisa dikembalikan.

Penggantinya, sesuai keputusan yang sudah disetujui: field-field itu menjadi **kolom di daftar Product
Variants**, tetap bisa diedit langsung dan bisa mengedit banyak baris sekaligus. Warna merah untuk
margin negatif dan kolom "Incl. Tax" ikut dibawa supaya setara popup lama.

**Yang perlu Anda nilai di T-05: apakah Anda tetap bisa melakukan pekerjaan yang dulu Anda lakukan
lewat popup itu?** Kalau ada yang dulu bisa dan sekarang tidak, itu temuan penting — tulis di kolom
Actual.

---

## Sign-off per Kelompok Fitur

> Isi setelah menjalankan skenario di atas **dengan tangan sendiri**, bukan berdasarkan laporan AI.

| # | Kelompok fitur | Skenario tercakup | Status | Catatan |
|---|---|---|---|---|
| 1 | Konfirmasi Sale Order & validasi margin | T-01, T-02, T-03, T-06 | [ ] Pass [ ] Fail | |
| 2 | Pengecualian order Rental | T-04 | [ ] Pass [ ] Fail [ ] N/A | |
| 3 | Kolom margin di daftar Product Variants | T-05 | [ ] Pass [ ] Fail | |
| 4 | Pesan bilingual (Prancis vs lainnya) | T-07 | [ ] Pass [ ] Fail [ ] N/A | |
| 5 | Ubah margin massal (wizard) | T-08 | [ ] Pass [ ] Fail | |
| 6 | Perilaku lama yang dipertahankan (batch confirm) | T-09 | [ ] Pass [ ] Fail | |

## Review Item Out-of-Scope

Stakeholder mengonfirmasi **sadar dan menerima** bahwa hal berikut sengaja TIDAK diubah:

- [ ] **Error saat konfirmasi banyak order sekaligus** (`MF-08`) — sudah diputuskan 2026-08-27
      **dipertahankan**, tidak diperbaiki tanpa keputusan baru. Lihat T-09.
- [ ] **Keanehan konfigurasi grup** `security/groups.xml` (`MF-20`) — dibawa apa adanya.
- [ ] **Warna peringatan bisa telat menyegarkan** sampai halaman di-refresh (`MF-21`) — dibawa apa
      adanya.
- [ ] **Masalah serupa `MF-08` pada perhitungan status rental** (`MF-26`) — dibawa apa adanya.
- [ ] **Pola `position="replace"` pada field harga** di form (`MF-27`) — dibawa apa adanya.
- [ ] **Tabrakan XML-ID** `product_template_inherit_sale_margin_threshold` (`BSL-013`) — dibawa apa
      adanya.
- [ ] **Terjemahan (i18n) tidak diupdate** untuk teks baru (`MF-39`).
- [ ] **Pesan peringatan hanya bilingual Prancis/Inggris**, bukan mengikuti bahasa user (lihat T-07)
      — mekanisme lama, sengaja tidak dikonversi ke sistem terjemahan standar Odoo.

## Prasyarat Sebelum Go-Live Produksi

- [ ] **Rehearsal upgrade sungguhan belum pernah dilakukan** — migrasi ini memakai asumsi **"port kode
      saja"** (tidak ada data produksi yang perlu dimigrasi), sehingga Step 7 (Data Migration) sengaja
      tidak dikerjakan. **Kalau ternyata ada instance produksi berisi data**, ini WAJIB dijadwalkan
      dulu dan asumsi awal harus dikoreksi.
- [ ] Backup database produksi sebelum upgrade nyata.
- [ ] README modul sudah direview, tidak menyebut versi Odoo lama/instruksi basi.
- [ ] **Pastikan run test otomatis memasang `sale_margin_threshold` DAN `pos_margin_threshold`
      bersamaan.** Test yang menjaga "kolom tidak dobel" **ter-skip diam-diam** kalau hanya satu modul
      terinstall (lihat `FINDINGS.md` `MF-37`).

## Catatan Kondisi Saat Dokumen Ini Dibuat (transparansi)

- Step 9 (Dev Testing) dan Step 10 (QA Testing) **sudah lulus tanpa syarat** untuk modul ini. Logic
  backend (konfirmasi order, pengecualian rental, formula margin, perilaku batch yang dipertahankan)
  diverifikasi lewat 12 test otomatis; tampilan kolom daftar varian diverifikasi visual live.
- **Jalur "Cancel" di jendela konfirmasi (T-03) belum punya test otomatis** — sudah dinilai benar dari
  pembacaan kode, tapi belum pernah diklik sungguhan. **Tolong jalankan T-03 dengan ekstra teliti.**
- Beberapa skenario detail (edit cepat berturut-turut di daftar varian) juga belum pernah dieksekusi
  end-to-end; kalau Anda menemukan keanehan saat mengedit cepat di T-05 langkah 6, tolong catat.

## Sign-off

| Role | Nama | Tanggal | Tanda tangan |
|---|---|---|---|
| PM | | | |
| FA | | | |
| User | | | |

> Sengaja dikosongkan. Diisi hanya setelah stakeholder benar-benar menjalankan skenario T-01 dst.
> dengan tangan sendiri. AI tidak mengisi baris ini atas nama siapapun.
