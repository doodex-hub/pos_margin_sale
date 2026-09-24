# Catatan Tindak Lanjut — Migrasi `pos-margin-sale` 19.0 → 20.0

**Dibuat:** 2026-09-24
**Status migrasi:** ⏸️ **DIJEDA SEMENTARA di titik ini** atas keputusan dev.
**Posisi:** Step 1–10 ✔️ lulus untuk ketiga modul; Step 11 (UAT) checklist sudah siap tapi **belum
dijalankan siapapun**.

> **Tujuan dokumen ini:** mengumpulkan hal-hal yang sengaja diangkat ke permukaan selama migrasi,
> supaya kalau nanti dilanjutkan/diperbaiki, **fixing-nya tepat sasaran** — bukan mulai dari
> menebak-nebak lagi. Tiap item di bawah menyebut **file/lokasi konkret**, **kenapa dibiarkan**, dan
> **apa yang dibutuhkan untuk menutupnya**.
>
> Ini BUKAN daftar bug migrasi. Step 8/9/10 tidak meninggalkan satupun gap kode yang belum
> ditangani. Yang ada di sini adalah: 1 keputusan produk yang menunggu dev, 1 pertanyaan UX ke user,
> dan 3 lubang coverage test.

---

## 1. `MF-47` — Native 20.0 punya fitur pin sendiri, jalan berdampingan dengan modul kita

**Jenis:** keputusan produk — **menunggu dev**, bukan bug.
**Dampak ke user:** langsung terlihat. Di menu aksi pesan ("...") muncul **DUA entri bernama "Pin"**
dengan ikon mirip.

### Kenapa ini terjadi

Odoo 20.0 menambahkan fitur pin/unpin pesannya sendiri — tidak ada di 19.0 atau versi manapun
sebelumnya. Jadi **tidak mungkin terdeteksi oleh proses diff/port biasa** (Step 2, Step 8, bahkan
Cross-Version Compare) — semuanya bertanya "apakah kode KITA masih benar", bukan "apakah NATIVE
sekarang punya fitur yang tumpang tindih".

### Bukti konkret (untuk dipakai saat fixing)

| Sisi | Lokasi |
|---|---|
| Native field | `odoo20/addons/mail/models/mail_message.py` baris 283 — `pinned_at = fields.Datetime('Pinned', ...)` |
| Native action | `odoo20/addons/mail/static/src/core/public_web/message_actions_patch.js` — `registerMessageAction("pin", {...})` + `"unpin"`, `sequence: 70` |
| Modul kita | `pin_message/static/src/js/pinMessage.js` — `registerMessageAction("pins", {...})`, `sequence: 15` |

**Dua sistem yang sepenuhnya terpisah:** native pakai field `pinned_at`, modul kita pakai `is_pinned`.
Beda field, beda method (`messagePin()` native vs `onClickPin()` kita). Yang menyamakan tampilannya
cuma kebetulan: sama-sama ikon `push_pin` dan label "Pin".

### Perilaku saat ini

Karena `sequence` kita (15) lebih kecil dari native (70), **entri kita tampil lebih dulu**. Jadi
selama user mengklik entri pertama, fungsi modul berjalan benar. Tapi kalau user mengklik entri
kedua, pesan ter-set `pinned_at` **tanpa muncul** di panel "Pinned Messages" custom — karena panel itu
hanya membaca `is_pinned`.

### Yang dibutuhkan untuk menutup

1. **Keputusan dev/user** dulu — ada di checklist UAT `pin_message` sebagai pertanyaan eksplisit.
   Opsi yang masuk akal:
   - (a) **biarkan** — terima dua entri, cukup dokumentasikan ke user mana yang dipakai;
   - (b) **sembunyikan salah satu** — paling murah: sembunyikan action native supaya hanya punya kita
     yang tampil, atau sebaliknya;
   - (c) **pertimbangkan pensiunkan modul custom ini** — native tampaknya punya kapabilitas setara;
     ini keputusan besar, di luar scope migrasi.
2. **Investigasi yang BELUM dilakukan** (kerjakan sebelum memilih (b)/(c)): apakah native 20.0 juga
   punya **UI daftar "pinned messages" sendiri** selain entri menu? Kalau ya, duplikasinya lebih luas
   dari yang terlihat sekarang, dan opsi (c) jadi lebih menarik.

> **Catatan scope:** migrasi ini mandatnya port 1:1, jadi tidak ada yang diubah soal ini. Apapun
> keputusannya = pekerjaan terpisah.

---

## 2. Popup "edit cepat" varian hilang — diganti kolom list (`MF-29`)

**Jenis:** pertanyaan paritas UX — **menunggu konfirmasi user lewat UAT**.
**Modul terdampak:** `pos_margin_threshold` DAN `sale_margin_threshold`.

### Kenapa ini terjadi

View `product.product_variant_easy_edit_view` **dihapus total oleh native 20.0** (dikonfirmasi grep
penuh, 0 match). Bukan keputusan kami, dan tidak bisa dikembalikan. Kedua modul akan gagal install
kalau di-port apa adanya.

### Yang sudah dikerjakan

Keputusan desain dev (2026-09-21): pindahkan customization margin ke **kolom baru di list Product
Variants** (`product.product_product_tree_view`), `optional="show"`. Sudah diterapkan, plus dua
penyesuaian supaya setara popup lama:

- **`MF-37`** — dedup kolom lintas-modul, supaya tidak dobel saat kedua modul terinstall.
- **`MF-38`** — paritas visual: warna merah untuk margin negatif + kolom "Incl. Tax", yang ada di
  popup 19.0 tapi belum terbawa ke kolom.

Semuanya sudah diverifikasi visual live di 20.0.

### Yang masih perlu dijawab user

Pertanyaannya **bukan** "apakah tampilannya sama" — jelas beda, dan itu disengaja. Yang perlu dijawab:

> **Apakah user tetap bisa melakukan pekerjaan yang dulu dilakukan lewat popup itu?**

Kalau ada yang dulu bisa dan sekarang tidak, itu gap nyata yang perlu ditambal. Sudah ditulis sebagai
instruksi eksplisit di checklist UAT kedua modul margin (skenario T-02 / T-05).

---

## 3. Tiga skenario berisiko tinggi yang baru terverifikasi MANUAL — belum ada test otomatis

**Jenis:** lubang coverage test — **bukan gap kode**. Ketiganya sudah dibuktikan **benar** saat
dicoba langsung, tapi tidak ada yang menjaga kalau nanti ada perubahan kode.

| # | Skenario | Modul | Kenapa berisiko | Bukti yang ada sekarang |
|---|---|---|---|---|
| 3a | **Jalur batal dialog POS** — klik "Discard" di dialog margin | `pos_margin_threshold` | Satu-satunya jalur yang membatalkan pembayaran | Diklik live 2026-09-23 + positive control (Pay lagi → Ok → lanjut). Lihat `10_qa/pos_margin_threshold/...` S-19 |
| 3b | **Jalur Cancel wizard** konfirmasi Sale Order | `sale_margin_threshold` | Satu-satunya jalur membatalkan konfirmasi order | Dinilai benar dari baca kode; **belum pernah diklik sungguhan**. Lihat `05a` AC-02-06 |
| 3c | **Pindah antar dokumen** (thread switch) — panel "Pinned Messages" harus ikut berganti | `pin_message` | Komponen `Chatter` **ditulis ulang arsitektural** oleh native 20.0 (`MF-33`) | Diklik live 2026-09-23, bolak-balik A→B→A, bersih. Lihat `10_qa/pin_message/...` S-06 |

### Yang dibutuhkan untuk menutup

Tulis **3 tour test** — dikerjakan sebagai **Step 9 addendum**, bukan diselipkan ke Step 10 lagi.

Polanya sudah terbukti murah: `BSL-018` ditutup dengan dua tour dalam satu sesi. Contoh yang bisa
dicontek langsung ada di `pos_margin_threshold/static/tests/tours/margin_threshold_tour.js`
(`..._no_dialog_above_minimum_tour` dan `..._orderline_warning_tour`).

**Pelajaran teknis dari menulis test `BSL-018` — pakai ini supaya tidak mengulang jebakan yang sama**
(detail penuh di `FINDINGS.md` `MF-48`):

1. **Jangan hardcode nominal** yang bergantung pajak. `'taxes_id': []` di fixture **tidak** menghapus
   pajak default 15% milik fixture akuntansi, dan mengubah `taxes_id` setelah `create()` di dalam
   `setUpClass` meninggalkan stored `minimum_sale_price_with_tax` tidak konsisten. (Compute modulnya
   sendiri sehat — sudah diverifikasi recompute benar di transaksi ORM biasa.) Assert **invarian**,
   bukan angka ajaib.
2. **`.orderline.selected` di POS 20.0 berwarna sama dengan `.text-danger`.** Jangan bandingkan warna
   terhadap orderline yang sedang terpilih — pilih dulu baris yang mau dibandingkan.
3. **Jangan pilih elemen pembanding dengan `li.orderline:not(.text-danger)`** — POS merender orderline
   di lebih dari satu tempat, `querySelector` bisa mengembalikan line dari render root lain.
   Identifikasi baris lewat **nama produk**.
4. Untuk "tidak boleh ada dialog sama sekali": assert layar akhir saja **tidak cukup** — dialog yang
   muncul lalu tertutup di frame yang sama tetap lolos. Pakai `MutationObserver` yang dipasang
   sebelum aksi.

---

## Item terbuka lain (lebih kecil, tapi jangan hilang)

### 4. Test dedup `MF-37` ter-skip diam-diam di run single-module

**Bukan** gap coverage — test-nya **ada dan lolos**:
`sale_margin_threshold/tests/test_high_risk_ac.py::test_ac_04_02_product_variants_columns_dedup_contract`.

Masalahnya: test itu memanggil `self.skipTest()` kalau `pos_margin_threshold` tidak terinstall. Jadi
di run test satu-addon yang biasa, ia **ter-skip tanpa sinyal kegagalan apapun** — coverage-nya ada di
repo tapi tidak pernah dieksekusi.

**Yang dibutuhkan:** pastikan konfigurasi CI memasang **kedua modul margin bersamaan**. Bukan menulis
test baru.

### 5. Rehearsal upgrade sungguhan belum pernah dilakukan

Migrasi ini memakai asumsi **"port kode saja"** — dikonfirmasi dev di gate Step 1, jadi Step 7 (Data
Migration) sengaja tidak dikerjakan sama sekali.

**Kalau ternyata ada instance produksi berisi data yang akan di-upgrade**, asumsi itu harus dikoreksi
dan rehearsal wajib dijadwalkan (clone data produksi → jalankan upgrade nyata → spot-check).
**Jangan dianggap beres otomatis karena Step 9/10 lulus** — semua verifikasi dilakukan di environment
Docker yang dibangun dari nol, bukan dari data nyata.

Khusus `pin_message`: kalau ada pesan yang sudah di-pin di produksi, perlu dicek apakah data
`is_pinned` lama terbawa benar.

### 6. Branch sudah di-push ✅ SELESAI

**Dev sudah menjalankan `git push -u origin migration/20.0` sendiri pada 2026-09-24.** Dikonfirmasi:
`origin/migration/20.0` = commit `1c7d420`, **0 ahead / 0 behind** — seluruh pekerjaan migrasi
(Step 1-10 + checklist Step 11 + catatan ini) sudah ada di remote. Tidak ada aksi tersisa untuk item
ini.

---

## Ringkasan: apa yang perlu diputuskan vs apa yang perlu dikerjakan

| # | Item | Perlu apa | Siapa |
|---|---|---|---|
| 1 | `MF-47` dua entri "Pin" | **Keputusan** (+ 1 investigasi kecil dulu) | dev/user |
| 2 | Popup → kolom list | **Konfirmasi paritas kerja** lewat UAT | user |
| 3 | 3 test regresi (decline POS, Cancel wizard, thread switch) | **Kerjakan** — Step 9 addendum | dev |
| 4 | CI pasang kedua modul margin | **Konfigurasi**, bukan coding | dev |
| 5 | Rehearsal upgrade | **Jadwalkan** kalau ada data produksi | dev/PM |
| 6 | ~~Push branch~~ | ✅ **SELESAI** 2026-09-24 (`origin/migration/20.0` = `1c7d420`, sinkron penuh) | — |

Tidak satupun dari ini memblokir apa yang sudah selesai. Step 1–10 lulus bersih untuk ketiga modul,
dan tidak ada gap kode migrasi yang tersisa.
