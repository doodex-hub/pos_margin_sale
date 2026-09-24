# UAT Checklist — Migrasi `pin_message` (Odoo 19.0 → 20.0)

**Step:** 11 — UAT Sign-off (final)
**Ref:** `05_acceptance/pin_message/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`,
`10_qa/pin_message/10_BUSINESS_FLOW_MIGRATION.md`
**Tanggal disiapkan:** 2026-09-24
**Disiapkan oleh:** AI (migration copilot) — **belum dijalankan siapapun**

> **Kriteria sukses: Anda TIDAK merasakan bedanya dibanding Odoo 19.0**, kecuali dua hal yang memang
> disebabkan Odoo 20.0 sendiri dan dijelaskan di §"Perubahan yang Memang Disengaja" — **tolong baca
> bagian itu DULU**, karena salah satunya akan langsung Anda lihat di layar dan mudah disangka
> kerusakan padahal bukan.

> **Dokumen ini adalah skrip test untuk DIJALANKAN SENDIRI oleh Anda (PM/FA/User), bukan laporan
> hasil test AI.** Kolom **Actual** dan **Status** sengaja dikosongkan — AI tidak boleh mengisinya.

---

## Persiapan Sebelum UAT (Precondition & Data)

- [ ] Odoo **20.0** dengan modul **Discuss** dan **`pin_message`** sudah terinstall.
- [ ] Login pakai user **biasa (bukan Administrator)** — supaya hak akses standar ikut tervalidasi.
- [ ] Database UAT adalah **salinan/staging**, bukan produksi asli.
- [ ] Siapkan **2 kontak** di **Contacts**: `UAT Kontak A` dan `UAT Kontak B`.

> **Catatan lokasi fitur:** modul ini bekerja di **Chatter** — kotak riwayat pesan/catatan yang ada di
> bagian bawah form (Contacts, Sales Order, dll). **Bukan** di aplikasi Discuss/channel chat. Kalau
> Anda mencoba di channel Discuss dan tampilannya berbeda, itu wajar — panel "Pinned Messages" milik
> modul ini memang menempel di Chatter, bukan di channel.

### Data dummy yang perlu Anda buat

Buka **Contacts ▸ `UAT Kontak A`**, di Chatter tulis **3 log note** berikut (tombol *Log note*):

1. `UAT catatan pertama - ini yang akan di-pin`
2. `UAT catatan kedua - biarkan tidak di-pin`
3. `UAT catatan ketiga - untuk test pin kedua`

Lalu buka **`UAT Kontak B`** dan tulis 1 log note: `UAT catatan di kontak B`.

---

## Skenario Test (Test Script)

### T-01: Pin sebuah catatan lewat menu aksi pesan

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka **Contacts ▸ `UAT Kontak A`**, arahkan kursor ke catatan `UAT catatan pertama...` | Muncul deretan ikon aksi di pojok pesan | | [ ] Pass [ ] Fail |
| 2 | Klik tombol **"..."** (menu aksi lainnya) pada pesan itu | Menu aksi terbuka. **Akan terlihat DUA entri bernama "Pin"** — ini normal di Odoo 20.0, baca §Perubahan yang Memang Disengaja | | [ ] Pass [ ] Fail |
| 3 | Klik entri **"Pin" yang PALING ATAS** (entri milik modul ini) | Pesan ter-pin | | [ ] Pass [ ] Fail |
| 4 | Perhatikan bagian atas Chatter | Muncul bagian **"Pinned Messages"** dengan hitungan **1** | | [ ] Pass [ ] Fail |

### T-02: Buka daftar pesan yang di-pin & lompat ke pesannya

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Klik bagian **"Pinned Messages"** untuk membukanya | Daftar terbuka, isinya `UAT catatan pertama...` | | [ ] Pass [ ] Fail |
| 2 | Perhatikan apakah ada error/layar kosong saat membuka | Terbuka mulus, **tidak ada error, tidak ada bagian yang kosong/rusak** | | [ ] Pass [ ] Fail |
| 3 | Klik tombol untuk melompat ke pesan tersebut (mis. **"See"/"Jump"**) | Layar melompat ke pesan aslinya di Chatter | | [ ] Pass [ ] Fail |
| 4 | Klik lagi bagian "Pinned Messages" untuk menutup | Daftar menutup normal | | [ ] Pass [ ] Fail |

### T-03: Pin lewat tombol pin langsung (entry-point kedua)

> Modul ini punya **dua cara** untuk pin — lewat menu "..." (T-01) dan lewat tombol pin langsung.
> Keduanya sengaja dipertahankan.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Pada catatan `UAT catatan ketiga...`, cari **tombol pin langsung** (ikon berbentuk paku payung / pin) | Tombol terlihat | | [ ] Pass [ ] Fail |
| 2 | Klik tombol itu | Pesan ter-pin | | [ ] Pass [ ] Fail |
| 3 | Perhatikan hitungan di bagian "Pinned Messages" | Berubah jadi **2** | | [ ] Pass [ ] Fail |

### T-04: Unpin (lepas pin)

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Pada catatan `UAT catatan ketiga...` yang tadi di-pin, klik tombol pin-nya lagi (atau entri unpin di menu "...") | Pin terlepas | | [ ] Pass [ ] Fail |
| 2 | Perhatikan hitungan "Pinned Messages" | Kembali jadi **1** | | [ ] Pass [ ] Fail |
| 3 | Lepas pin catatan yang terakhir tersisa juga | Bagian **"Pinned Messages" hilang sepenuhnya** dari Chatter (karena sudah tidak ada yang di-pin) | | [ ] Pass [ ] Fail |

### T-05: Pin bertahan setelah halaman di-refresh

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Pin kembali `UAT catatan pertama...` | Hitungan "Pinned Messages" = 1 | | [ ] Pass [ ] Fail |
| 2 | Tekan **F5 / refresh browser**, buka lagi `UAT Kontak A` | Bagian "Pinned Messages" **masih ada** dengan hitungan **1**, isinya masih catatan yang sama | | [ ] Pass [ ] Fail |

### T-06: Pindah antar kontak — daftar pin harus ikut berganti `[PALING PENTING]`

> Ini skenario **paling rawan** di migrasi ini (komponen Chatter ditulis ulang total oleh Odoo 20.0).
> Tolong jalankan pelan-pelan dan perhatikan betul.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Pastikan `UAT Kontak A` punya 1 pesan ter-pin | "Pinned Messages" = 1 | | [ ] Pass [ ] Fail |
| 2 | **Tanpa refresh browser**, pindah ke **`UAT Kontak B`** (lewat daftar Contacts / tombol navigasi) | Form `UAT Kontak B` terbuka | | [ ] Pass [ ] Fail |
| 3 | Perhatikan Chatter `UAT Kontak B` | **TIDAK ada** bagian "Pinned Messages" (karena kontak B belum punya pesan ter-pin) — daftar milik kontak A **tidak boleh nyangkut** di sini | | [ ] Pass [ ] Fail |
| 4 | Pin catatan `UAT catatan di kontak B` | "Pinned Messages" muncul dengan hitungan **1** | | [ ] Pass [ ] Fail |
| 5 | **Tanpa refresh**, kembali ke **`UAT Kontak A`** | "Pinned Messages" tampil **1**, isinya catatan milik kontak A (bukan milik B) | | [ ] Pass [ ] Fail |
| 6 | Bolak-balik A → B → A sekali lagi | Setiap kali, daftar yang tampil **selalu milik kontak yang sedang dibuka** | | [ ] Pass [ ] Fail |

### T-07: Tampilan ikon

> Odoo 20.0 mengganti set ikon bawaannya. Ikon pin di modul ini ikut disesuaikan supaya tetap serasi.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Perhatikan ikon tombol pin dan ikon panah buka/tutup di bagian "Pinned Messages" | Ikon **tampil utuh** (bukan kotak kosong, bukan tanda tanya, bukan teks mentah) dan **serasi** dengan ikon Odoo lain di sekitarnya | | [ ] Pass [ ] Fail |
| 2 | Bandingkan dengan perasaan Anda memakai versi 19.0 | Terasa setara — tidak ada yang hilang atau terlihat rusak | | [ ] Pass [ ] Fail |

### T-08: Coba di jenis dokumen lain (opsional tapi disarankan)

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka satu **Sale Order** (atau dokumen lain yang biasa Anda pakai sehari-hari), tulis log note, lalu pin | Perilaku sama seperti di Contacts | | [ ] Pass [ ] Fail |

### T-09: Item yang TIDAK Bisa Dites Lewat Tampilan Biasa (Informasi, Bukan Kegagalan)

- **Kode lama yang sengaja dibiarkan** (`BSL-002`/`BSL-016`, penanda `is_discussion` dan satu
  referensi layanan yang tidak terpakai) — tidak punya tampilan, sengaja tidak dibersihkan supaya
  perilaku persis sama dengan 19.0.
- **Perbedaan penanganan error antara dua tombol pin** (`BSL-015`) — dua cara pin di T-01 dan T-03
  menangani kegagalan sedikit berbeda di balik layar. Sengaja dipertahankan; tidak terlihat pada
  pemakaian normal.
- **Cara data pin dikirim dari server ke layar** — ditulis ulang total karena Odoo 20.0 menghapus
  mekanisme lama. Kalau T-01 sampai T-06 berjalan benar, bagian ini otomatis terbukti bekerja.

---

## Perubahan yang Memang Disengaja (WAJIB dibaca sebelum menilai)

### 1. Akan ada DUA entri "Pin" di menu aksi pesan — ini BUKAN kerusakan

**Odoo 20.0 kini punya fitur pin/unpin pesannya SENDIRI**, yang tidak ada di versi 19.0 atau
sebelumnya. Fitur bawaan itu berjalan **berdampingan** dengan modul `pin_message` ini. Akibatnya, di
menu **"..."** sebuah pesan Anda akan melihat **dua entri bernama "Pin"** dengan ikon mirip.

- Entri **paling atas** adalah milik modul ini — **itu yang harus Anda pakai**, dan itu yang mengisi
  panel "Pinned Messages".
- Entri kedua adalah milik Odoo bawaan. Kalau diklik, pesan akan ter-pin menurut Odoo **tapi TIDAK
  muncul** di panel "Pinned Messages" modul ini — karena keduanya menyimpan datanya secara terpisah.

Ini temuan baru yang **tidak bisa terdeteksi dari proses migrasi biasa** (fitur bawaannya memang baru
ada di 20.0), sudah dicatat sebagai `MF-47` dan **masih menunggu keputusan Anda**:

> **Pertanyaan untuk Anda jawab saat UAT:** apakah dua entri "Pin" ini cukup mengganggu sehingga perlu
> ditindaklanjuti? Pilihannya nanti antara lain: biarkan saja, sembunyikan salah satu, atau
> pertimbangkan apakah modul custom ini masih dibutuhkan mengingat Odoo sudah punya fitur setara.
> **Keputusan ini di luar scope migrasi (migrasi ini murni port 1:1) — tapi jawaban Anda dibutuhkan
> untuk menentukan langkah berikutnya.** Tulis pendapat Anda di kolom Catatan sign-off.

### 2. Ikon berubah mengikuti Odoo 20.0

Odoo 20.0 mengganti set ikon bawaannya (FontAwesome → Odoo Icons). Ikon pin di modul ini disesuaikan
supaya tetap serasi dengan tampilan sekitarnya. Bentuknya bisa terlihat sedikit berbeda dari 19.0 —
yang penting **tetap terbaca sebagai "pin" dan tidak rusak** (lihat T-07).

---

## Sign-off per Kelompok Fitur

> Isi setelah menjalankan skenario di atas **dengan tangan sendiri**, bukan berdasarkan laporan AI.

| # | Kelompok fitur | Skenario tercakup | Status | Catatan |
|---|---|---|---|---|
| 1 | Pin & unpin pesan (dua entry-point) | T-01, T-03, T-04 | [ ] Pass [ ] Fail | |
| 2 | Panel "Pinned Messages": tampil, hitungan, buka/tutup, lompat ke pesan | T-02, T-05 | [ ] Pass [ ] Fail | |
| 3 | Pindah antar dokumen (paling rawan) | T-06 | [ ] Pass [ ] Fail | |
| 4 | Tampilan ikon | T-07 | [ ] Pass [ ] Fail | |
| 5 | Berlaku di dokumen lain | T-08 | [ ] Pass [ ] Fail [ ] N/A | |
| 6 | **Keputusan soal dua entri "Pin" (`MF-47`)** | §Perubahan poin 1 | [ ] Biarkan [ ] Tindaklanjuti | |

## Review Item Out-of-Scope

Stakeholder mengonfirmasi **sadar dan menerima** bahwa hal berikut sengaja TIDAK diubah:

- [ ] **Kode lama yang tidak terpakai dibiarkan** (`BSL-002`/`BSL-016`) — tidak dibersihkan, konsisten
      dengan keputusan project migrasi 18.0→19.0.
- [ ] **Dua entry-point pin dengan penanganan error berbeda** (`BSL-015`) — dipertahankan apa adanya.
- [ ] **Isi internal komponen Chatter tidak ditulis ulang** mengikuti gaya baru Odoo 20.0 — hanya
      disesuaikan seperlunya agar berfungsi. Tidak dirombak preventif.
- [ ] **Fitur pin bawaan Odoo 20.0 dibiarkan berjalan berdampingan** (`MF-47`) — migrasi ini murni
      port 1:1; penyesuaian apapun soal ini adalah pekerjaan terpisah, menunggu keputusan Anda.

## Prasyarat Sebelum Go-Live Produksi

- [ ] **Rehearsal upgrade sungguhan belum pernah dilakukan** — migrasi ini memakai asumsi **"port kode
      saja"**, sehingga Step 7 (Data Migration) sengaja tidak dikerjakan. **Kalau ternyata ada
      instance produksi berisi pesan-pesan yang sudah di-pin**, perlu dicek dulu apakah data pin lama
      terbawa dengan benar — ini WAJIB dijadwalkan dan asumsi awal harus dikoreksi.
- [ ] Backup database produksi sebelum upgrade nyata.
- [ ] README modul sudah direview, tidak menyebut versi Odoo lama/instruksi basi.
- [ ] **Keputusan `MF-47`** (dua entri "Pin") sudah diambil — minimal diputuskan "biarkan dulu" secara
      sadar, supaya tidak jadi keluhan user setelah go-live.

## Catatan Kondisi Saat Dokumen Ini Dibuat (transparansi)

- Step 9 (Dev Testing) dan Step 10 (QA Testing) **sudah lulus** untuk modul ini. Pin/unpin, panel
  "Pinned Messages", buka daftar, dan tombol lompat-ke-pesan semuanya diverifikasi — sebagian lewat
  tour test otomatis, sebagian lewat klik langsung di browser.
- **T-06 (pindah antar dokumen) sudah diverifikasi manual dan berhasil**, tapi **belum punya test
  otomatis** yang menjaganya. Ini skenario dengan risiko tertinggi di modul ini karena Odoo 20.0
  menulis ulang komponen Chatter secara arsitektural. **Tolong jalankan T-06 dengan ekstra teliti.**
- Sepanjang Step 8/9/10 **tidak ditemukan satupun bug modul yang tersisa** — semua masalah yang
  ditemukan sudah diperbaiki dan diverifikasi ulang.

## Sign-off

| Role | Nama | Tanggal | Tanda tangan |
|---|---|---|---|
| PM | | | |
| FA | | | |
| User | | | |

> Sengaja dikosongkan. Diisi hanya setelah stakeholder benar-benar menjalankan skenario T-01 dst.
> dengan tangan sendiri. AI tidak mengisi baris ini atas nama siapapun.
