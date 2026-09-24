# UAT Checklist — Migrasi `pos_margin_threshold` (Odoo 19.0 → 20.0)

**Step:** 11 — UAT Sign-off (final)
**Ref:** `05_acceptance/pos_margin_threshold/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`,
`10_qa/pos_margin_threshold/10_BUSINESS_FLOW_MIGRATION.md`
**Tanggal disiapkan:** 2026-09-24
**Disiapkan oleh:** AI (migration copilot) — **belum dijalankan siapapun**

> **Kriteria sukses: Anda TIDAK merasakan bedanya dibanding Odoo 19.0.** Modul ini dimigrasi dengan
> prinsip "port kode saja" — tidak ada fitur baru, tidak ada perubahan aturan bisnis. Kalau saat
> menjalankan skenario di bawah Anda merasa ada yang "beda dari biasanya", itu justru temuan penting,
> tolong tulis di kolom Actual.

> **Dokumen ini adalah skrip test untuk DIJALANKAN SENDIRI oleh Anda (PM/FA/User), bukan laporan
> hasil test AI.** Kolom **Actual** dan **Status** sengaja dikosongkan — AI tidak boleh mengisinya.
> Step 9 (Dev Testing) dan Step 10 (QA Testing) sudah dijalankan secara teknis dan lulus; UAT baru
> bermakna kalau yang menjalankan adalah orang yang memakai sistem ini sehari-hari, karena Anda bisa
> menangkap hal yang lolos dari mata teknis.

---

## Persiapan Sebelum UAT (Precondition & Data)

- [ ] Odoo **20.0** dengan modul **Point of Sale** dan **`pos_margin_threshold`** sudah terinstall
      dan bisa dibuka.
- [ ] **Kalau `sale_margin_threshold` juga dipakai di produksi, install KEDUANYA bersamaan** di
      environment UAT ini. Dua modul itu sama-sama menambah kolom ke layar yang sama, dan salah satu
      skenario di bawah (T-02) memang menguji bahwa kolomnya tidak tampil dobel.
- [ ] Login pakai user **dengan role kasir/manager POS biasa**, bukan Administrator — supaya hak akses
      standar ikut tervalidasi. Untuk langkah yang butuh ubah Settings, boleh login Administrator,
      tapi catat di kolom Actual kalau Anda harus ganti user.
- [ ] Database UAT adalah **salinan/staging**, bukan produksi asli.
- [ ] Sudah ada **1 Point of Sale** yang bisa dibuka (Register/Session), dengan minimal 1 metode
      pembayaran (mis. Cash atau Bank).
- [ ] Sudah ada **1 kategori produk** kosong yang boleh dipakai bebas untuk test.

### Data dummy yang perlu Anda siapkan lebih dulu

Buat lewat menu **Point of Sale ▸ Products ▸ Products** (atau Inventory ▸ Products):

| Nama produk | Cost / Harga Beli | Margin | Sales Price | Catatan |
|---|---|---|---|---|
| `UAT Kopi Murah` | 10.000 | 50 | **5.000** | sengaja DI BAWAH minimum |
| `UAT Kopi Normal` | 10.000 | 50 | **50.000** | sengaja DI ATAS minimum |
| `UAT Kopi Rugi` | 10.000 | **-10** | 8.000 | margin negatif, untuk cek warna merah |

Ketiganya harus dicentang **"Available in POS"**.

> Dengan Cost 10.000 dan Margin 50, sistem menghitung **Minimum sale price = 15.000**. Jadi
> `UAT Kopi Murah` (5.000) ada di bawah minimum, `UAT Kopi Normal` (50.000) di atas minimum.

---

## Skenario Test (Test Script)

### T-01: Margin dari kategori otomatis menurun ke produk

**Data dummy:** kategori produk test Anda, dan 1 produk baru.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka **Inventory ▸ Configuration ▸ Product Categories**, pilih kategori test Anda, isi field **Margin** = `30`, Save | Field Margin tersimpan `30` | | [ ] Pass [ ] Fail |
| 2 | Buat produk baru `UAT Cek Kategori`, set **Product Category** ke kategori tadi, isi **Cost** = `20.000` | Field **Margin** pada produk otomatis terisi `30` | | [ ] Pass [ ] Fail |
| 3 | Lihat field **Minimum sale price** pada produk itu | Terisi `26.000` (= 20.000 + 30%) | | [ ] Pass [ ] Fail |
| 4 | Ubah **Margin** produk itu jadi `40` secara manual, Save | **Minimum sale price** berubah jadi `28.000`; margin kategori TIDAK ikut berubah | | [ ] Pass [ ] Fail |

### T-02: Kolom margin di daftar "Product Variants"

> Ini bagian yang **paling berubah tampilannya** dibanding 19.0 — lihat catatan di §"Perubahan yang
> Memang Disengaja" di bawah sebelum menilai Pass/Fail.

**Data dummy:** ketiga produk UAT di atas.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka **Inventory ▸ Products ▸ Products**, buka `UAT Kopi Murah`, klik tombol/smart-button **Variants** | Muncul daftar (list) Product Variants | | [ ] Pass [ ] Fail |
| 2 | Perhatikan kolom-kolom yang tampil | Ada kolom **Margin**, **Minimum sale price**, dan **Incl. Tax** | | [ ] Pass [ ] Fail |
| 3 | Hitung ada berapa kolom "Margin" dan berapa kolom "Minimum sale price" | **Masing-masing HANYA SATU**, tidak dobel | | [ ] Pass [ ] Fail |
| 4 | Lihat baris `UAT Kopi Rugi` (margin `-10`) | Angka **Margin** dan **Sales Price**-nya tampil **MERAH** | | [ ] Pass [ ] Fail |
| 5 | Lihat baris `UAT Kopi Normal` (margin positif, harga di atas minimum) | Angkanya tampil **normal/hitam**, tidak merah | | [ ] Pass [ ] Fail |
| 6 | Klik langsung pada sel **Margin** salah satu baris dan ubah angkanya, lalu Save | Nilai bisa diedit langsung dari daftar, dan **Minimum sale price** ikut menyesuaikan | | [ ] Pass [ ] Fail |

### T-03: POS — jual di bawah minimum, lalu LANJUTKAN pembayaran

**Data dummy:** `UAT Kopi Murah` (harga 5.000, minimum 15.000).

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka **Point of Sale**, buka Register/Session | Masuk ke layar kasir | | [ ] Pass [ ] Fail |
| 2 | Klik produk `UAT Kopi Murah` sehingga masuk ke keranjang | Baris pesanan muncul | | [ ] Pass [ ] Fail |
| 3 | Perhatikan baris pesanan itu | Baris tampil **MERAH**, dengan tulisan peringatan bahwa harga di bawah minimum, **berikut angka minimumnya** | | [ ] Pass [ ] Fail |
| 4 | Klik tombol **Payment / Pay** | Muncul dialog berjudul kira-kira *"Price unit less than minimum price"* yang menanyakan apakah mau lanjut | | [ ] Pass [ ] Fail |
| 5 | Klik tombol konfirmasi (**Ok**) | Berpindah ke layar pembayaran | | [ ] Pass [ ] Fail |
| 6 | Selesaikan pembayaran seperti transaksi biasa | Transaksi selesai normal, struk/layar akhir muncul | | [ ] Pass [ ] Fail |

### T-04: POS — jual di bawah minimum, lalu BATALKAN di dialog

> Ini jalur yang **paling penting** dicek manual: satu-satunya cara kasir membatalkan.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Di layar kasir, tambahkan `UAT Kopi Murah` ke keranjang | Baris pesanan muncul (merah) | | [ ] Pass [ ] Fail |
| 2 | Klik **Payment / Pay** | Dialog peringatan muncul | | [ ] Pass [ ] Fail |
| 3 | Klik tombol **batal/Discard** (BUKAN Ok) | Dialog tertutup | | [ ] Pass [ ] Fail |
| 4 | Perhatikan layar sekarang | Masih di **layar produk/kasir**, TIDAK pindah ke layar pembayaran | | [ ] Pass [ ] Fail |
| 5 | Perhatikan keranjang | Isi keranjang **masih utuh** — barang tidak hilang, jumlah dan harga tidak berubah | | [ ] Pass [ ] Fail |
| 6 | Klik **Payment / Pay** lagi, lalu **Ok** | Bisa lanjut normal — artinya pembatalan tadi tidak merusak apa-apa | | [ ] Pass [ ] Fail |

### T-05: POS — mode "blokir total" (transaksi tidak boleh lanjut)

**Perlu ubah Settings** (boleh login Administrator untuk langkah 1).

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka **Point of Sale ▸ Configuration ▸ Settings**, bagian **Interface**, centang **"Blocking Transaction POS"**, Save | Setting tersimpan | | [ ] Pass [ ] Fail |
| 2 | Tutup lalu buka ulang layar kasir POS (refresh session) | Layar kasir terbuka | | [ ] Pass [ ] Fail |
| 3 | Tambahkan `UAT Kopi Murah`, klik **Payment / Pay** | Muncul dialog peringatan yang **hanya punya tombol Ok** (tidak menawarkan lanjut/batal) | | [ ] Pass [ ] Fail |
| 4 | Klik **Ok** | Kembali ke layar kasir, **TIDAK bisa lanjut ke pembayaran sama sekali** | | [ ] Pass [ ] Fail |
| 5 | **Kembalikan setting**: hilangkan centang "Blocking Transaction POS", Save | Setting kembali seperti semula | | [ ] Pass [ ] Fail |

### T-06: POS — transaksi normal TIDAK boleh diganggu peringatan apapun

> Ini menguji bahwa modul tidak "cerewet" pada transaksi yang wajar.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Di layar kasir, pastikan keranjang kosong, lalu tambahkan **hanya** `UAT Kopi Normal` | Baris pesanan muncul, **tidak merah**, tidak ada tulisan peringatan | | [ ] Pass [ ] Fail |
| 2 | Klik **Payment / Pay** | **Langsung** ke layar pembayaran — TIDAK ada dialog apapun, bahkan tidak ada yang berkedip sekejap | | [ ] Pass [ ] Fail |
| 3 | Selesaikan pembayaran | Transaksi selesai normal | | [ ] Pass [ ] Fail |

### T-07: POS — keranjang campur (ada yang di bawah minimum, ada yang tidak)

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Di layar kasir, tambahkan `UAT Kopi Normal` DAN `UAT Kopi Murah` ke keranjang yang sama | Dua baris pesanan muncul | | [ ] Pass [ ] Fail |
| 2 | Perhatikan kedua baris | **Hanya** baris `UAT Kopi Murah` yang merah + ada peringatan; baris `UAT Kopi Normal` normal | | [ ] Pass [ ] Fail |
| 3 | Klik **Payment / Pay** | Dialog peringatan tetap muncul (karena ada satu baris di bawah minimum) | | [ ] Pass [ ] Fail |

### T-08: Ubah margin banyak produk sekaligus (wizard)

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka daftar **Products**, centang `UAT Kopi Murah` dan `UAT Kopi Normal` | Dua produk tercentang | | [ ] Pass [ ] Fail |
| 2 | Buka menu **Actions / ⚙️**, pilih aksi terkait **Update margin sale** | Muncul jendela isian margin | | [ ] Pass [ ] Fail |
| 3 | Isi margin = `25`, konfirmasi | Kedua produk ter-update Margin = `25` | | [ ] Pass [ ] Fail |
| 4 | Cek **Minimum sale price** kedua produk | Ikut berubah jadi `12.500` (= 10.000 + 25%) | | [ ] Pass [ ] Fail |

### T-09: Field margin di form Produk dan Kategori

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka salah satu produk UAT, lihat area harga | Field **Margin**, **Minimum sale price**, dan harga jual tampil rapi, tidak tumpang tindih / terpotong | | [ ] Pass [ ] Fail |
| 2 | Buka **Product Categories**, buka satu kategori | Field **Margin** tampil di form kategori, di posisi yang wajar | | [ ] Pass [ ] Fail |

### T-10: POS — produk paket/combo (kalau Anda memakai fitur combo)

> **Lewati skenario ini kalau bisnis Anda tidak memakai produk combo di POS.**

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Siapkan 1 produk combo POS berisi 2 komponen, lalu tambahkan ke keranjang di layar kasir | Baris induk combo + baris komponennya muncul | | [ ] Pass [ ] Fail |
| 2 | Perhatikan tampilan baris komponen | Baris komponen tampil **menjorok ke dalam dengan garis di kiri** (menandakan bagian dari combo) | | [ ] Pass [ ] Fail |

### T-11: Item yang TIDAK Bisa Dites Lewat Tampilan Biasa (Informasi, Bukan Kegagalan)

Jangan mencari-cari hal berikut di layar — memang tidak terlihat, dan itu normal:

- **Pemuatan data margin ke layar kasir POS** (`AC-08`) — proses di balik layar saat POS dibuka.
  Kalau T-03 sampai T-07 berjalan benar, bagian ini otomatis terbukti bekerja.
- **File view lama yang sengaja tidak dipakai** dan **file kosong `pos_session.py`** (`AC-10`) —
  peninggalan versi lama yang sengaja **dipertahankan apa adanya** supaya tidak mengubah perilaku.
  Tidak punya tampilan sama sekali.
- **Field "Blocking Transaction Order"** — didefinisikan di modul ini tapi **tidak punya tampilan di
  modul ini** (tampilannya ada di `sale_margin_threshold`). Ini quirk lama yang sengaja dipertahankan,
  bukan kerusakan.
- **Penamaan internal `action_assing_margin`** (salah ketik "assing", seharusnya "assign") — sengaja
  **TIDAK diperbaiki** supaya tidak mengubah apapun di luar dugaan. Tidak terlihat oleh user.

---

## Perubahan yang Memang Disengaja (WAJIB dibaca sebelum menilai T-02)

Di Odoo 19.0, margin/minimum sale price diubah lewat **popup "edit cepat"** yang muncul saat membuka
varian produk. **Popup itu DIHAPUS oleh Odoo 20.0 sendiri** (bukan oleh kami) — tidak ada lagi di
versi ini, apapun yang kami lakukan.

Penggantinya, sesuai keputusan yang sudah disetujui: field-field itu dipindah menjadi **kolom di
daftar Product Variants**, yang tetap bisa diedit langsung dan bisa mengedit banyak baris sekaligus.
Warna merah untuk margin negatif dan kolom "Incl. Tax" juga ikut dibawa supaya setara popup lama.

**Jadi kalau di T-02 Anda merasa "kok beda dari 19.0" — itu memang disengaja dan sudah disetujui.**
Yang perlu Anda nilai adalah: **apakah Anda tetap bisa melakukan pekerjaan yang dulu Anda lakukan
lewat popup itu?** Kalau ada yang dulu bisa dan sekarang tidak bisa, itu temuan penting — tolong tulis
di kolom Actual T-02.

---

## Sign-off per Kelompok Fitur

> Isi setelah menjalankan skenario di atas **dengan tangan sendiri**, bukan berdasarkan laporan AI.

| # | Kelompok fitur | Skenario tercakup | Status | Catatan |
|---|---|---|---|---|
| 1 | Perhitungan margin & minimum sale price | T-01, T-09 | [ ] Pass [ ] Fail | |
| 2 | Kolom margin di daftar Product Variants (pengganti popup) | T-02 | [ ] Pass [ ] Fail | |
| 3 | Peringatan & dialog di POS | T-03, T-04, T-05, T-06, T-07 | [ ] Pass [ ] Fail | |
| 4 | Ubah margin massal (wizard) | T-08 | [ ] Pass [ ] Fail | |
| 5 | Tampilan produk combo di POS | T-10 | [ ] Pass [ ] Fail [ ] N/A | |

## Review Item Out-of-Scope

Stakeholder mengonfirmasi **sadar dan menerima** bahwa hal berikut sengaja TIDAK diubah di migrasi ini
(semua sudah diputuskan sebelumnya, dibawa apa adanya dari versi 19.0):

- [ ] Beberapa **bug/keanehan lama dipertahankan identik** — tidak diperbaiki, supaya perilaku persis
      sama dengan 19.0: margin varian tidak bisa berbeda dari produk induknya (`MF-01`); field
      "Blocking Transaction Order" tanpa tampilan di modul ini (`MF-02`); tabrakan nama internal
      wizard dengan `sale_margin_threshold` (`MF-03`); file view lama yang tidak dipakai (`MF-04`);
      warna peringatan yang bisa telat menyegarkan sampai halaman di-refresh (`MF-23`); pola
      `position="replace"` pada field harga (`MF-24`/`MF-25`); salah ketik `action_assing_margin`.
- [ ] **Terjemahan (i18n) tidak diupdate** untuk teks baru — teks baru akan tampil dalam bahasa
      Inggris. Konsisten dengan prinsip "port kode saja" (`MF-39`).
- [ ] **Odoo 20.0 punya perilaku barunya sendiri** yang tidak bisa kami ubah: popup edit-cepat varian
      dihapus (lihat §Perubahan yang Memang Disengaja).

## Prasyarat Sebelum Go-Live Produksi

- [ ] **Rehearsal upgrade sungguhan belum pernah dilakukan** — migrasi ini dikerjakan dengan asumsi
      **"port kode saja"** (tidak ada data produksi yang perlu dimigrasi), sehingga Step 7 (Data
      Migration) sengaja tidak dikerjakan. **Kalau ternyata ada instance produksi berisi data yang
      akan di-upgrade, ini WAJIB dijadwalkan dulu** (clone data produksi → jalankan upgrade nyata →
      spot-check) dan asumsi awal harus dikoreksi. Jangan dianggap beres otomatis karena Step 9/10
      lulus di environment Docker.
- [ ] Backup database produksi sebelum upgrade nyata.
- [ ] README modul sudah direview, tidak menyebut versi Odoo lama/instruksi basi.
- [ ] **Pastikan run test otomatis memasang `pos_margin_threshold` DAN `sale_margin_threshold`
      bersamaan.** Test yang menjaga "kolom tidak dobel" akan **ter-skip diam-diam** kalau hanya satu
      modul yang terinstall (lihat `FINDINGS.md` `MF-37`).

## Catatan Kondisi Saat Dokumen Ini Dibuat (transparansi)

- Step 9 (Dev Testing) dan Step 10 (QA Testing) **sudah lulus** untuk modul ini. Semua dialog POS,
  kolom list, dedup kolom, dan peringatan orderline sudah diverifikasi — sebagian lewat test otomatis,
  sebagian lewat eksekusi live di browser.
- **Dua hal berikut baru diverifikasi manual sekali, belum ada test otomatisnya:** jalur batal di
  dialog POS (T-04) dan tampilan combo POS (T-10). Keduanya terbukti benar saat dicoba, tapi tidak ada
  yang menjaga kalau nanti ada perubahan kode. **Karena itu T-04 dan T-10 layak Anda jalankan dengan
  ekstra teliti.**

## Sign-off

| Role | Nama | Tanggal | Tanda tangan |
|---|---|---|---|
| PM | | | |
| FA | | | |
| User | | | |

> Sengaja dikosongkan. Diisi hanya setelah stakeholder benar-benar menjalankan skenario T-01 dst.
> dengan tangan sendiri. AI tidak mengisi baris ini atas nama siapapun.
