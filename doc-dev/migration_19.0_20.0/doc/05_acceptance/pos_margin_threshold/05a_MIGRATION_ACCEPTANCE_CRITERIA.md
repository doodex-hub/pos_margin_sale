# Migration Acceptance Criteria — pos_margin_threshold

**Step:** 5 — Acceptance Criteria & Test Plan
**Ref:** `01_intake/pos_margin_threshold/01b_BASELINE_SPEC.md` dan kode 19.0 yang berjalan (branch
`migration/19.0`) — **bukan** `03_spec/pos_margin_threshold/03_MIGRATION_SPEC.md`
**Tanggal:** 2026-09-22

> Format Given/When/Then, diturunkan dari `01b_BASELINE_SPEC.md` (dokumentasi behavior modul asli
> 19.0). `03_MIGRATION_SPEC.md` dipakai HANYA sebagai referensi area berisiko tinggi (ditandai
> **[RISIKO MIGRASI]** di tiap AC yang relevan) — bukan sumber kebenaran perilaku. Kesetaraan diukur
> terhadap kode 19.0 yang berjalan, bukan terhadap rencana migrasi.
>
> **Traceability:** tiap AC menyebut `BSL-NNN` yang diverifikasi. Beberapa AC di bawah TIDAK bisa
> dipetakan ke `BSL-NNN` bernomor — ini sengaja dibiarkan terlihat (bukan diakali dengan mengarang
> nomor) dan dikumpulkan di §"Catatan Kelengkapan Baseline" di bawah, karena itu tanda
> `01b_BASELINE_SPEC.md` sendiri belum 100% lengkap, bukan tanda AC ini tidak sah.
>
> **Penomoran AC di dokumen ini BARU** (didesain ulang untuk project 19.0→20.0 ini, dikelompokkan per
> area fitur sesuai kondisi baseline saat ini) — **bukan** kelanjutan penomoran `AC-NN-NN` yang
> disebut di docstring/komentar test yang sudah ada di repo (`tests/test_margin_sale.py`,
> `tests/test_margin_threshold_tour.py`, dll — rujukan itu berasal dari dokumen acceptance criteria
> project migrasi 18.0→19.0 SEBELUMNYA). Perilaku yang diverifikasi identik; hanya nomornya beda.
> Setiap AC yang sudah punya test existing menyebut eksplisit nomor AC lama + nama method test supaya
> tidak ambigu.

---

## Catatan Kelengkapan Baseline (temuan Step 5, bukan blocker)

`01b_BASELINE_SPEC.md` secara umum lengkap (22 klaim `BSL-NNN`), tapi ada beberapa celah yang
ditemukan saat menyusun AC di bawah — dicatat di sini, bukan didiamkan:

1. **§3 "Field dengan Makna Bisnis" (formula inti `minimum_sale_price = standard_price * (1 +
   margin_sale/100)` dan pewarisan `margin_sale` dari `categ_id`) tidak punya `BSL-NNN` sendiri.**
   Hanya sisi *inverse*-nya (set `minimum_sale_price` manual → recompute `margin_sale`) yang
   ter-tag `BSL-008`. Formula *forward*-nya (arah paling sering dipakai — inilah computation inti
   modul) cuma dijelaskan naratif di §3, tanpa ID. AC-01-01/01-02/01-03 di bawah tetap ditulis
   (perilaku ini SUDAH ditest nyata sejak dua project migrasi sebelumnya, lihat `tests/test_margin_sale.py`)
   tapi disitat ke "§3 (tanpa BSL-NNN)" — bukan diakali dengan nomor baru.
2. **Bullet "Form Product Variant Easy Edit" di §6 (antara `BSL-014` dan `BSL-015`) tidak punya tag
   `[BSL-NNN]`.** Ini justru bullet paling penting untuk AC-07 (kolom list pengganti popup yang
   dihapus `MF-29`) karena menjelaskan ISI popup lama (field apa saja yang tampil, decoration apa)
   yang harus disetarakan visualnya di UI pengganti. Disitat sebagai "§6 bullet tanpa BSL-NNN,
   antara BSL-014/BSL-015" di AC-06-03/AC-07.
3. **`BSL-012` (dual-path `inverse=`/`@api.onchange` pada `margin_sale` variant) baru
   didokumentasikan sesi Step 1 ini** — belum pernah ada test eksplisit yang membedakan jalur
   `write()` vs jalur onchange interaktif (test yang ada, `test_margin_sale_inverse_writes_to_shared_template_not_per_variant`,
   hanya menguji lewat `write()` langsung ke field, bukan lewat simulasi onchange form). AC-01-08
   menandai ini sebagai gap test yang genuinely baru, bukan carry-forward.
4. **AC-07 (kolom Product Variants pengganti popup, `MF-29`) dan sebagian AC-05 (`combo_parent_id`
   aktif, `MF-34`) TIDAK bisa disitat ke `BSL-NNN` manapun** karena keduanya representasi UI/behavior
   yang secara harfiah TIDAK ADA di 19.0 (popup lama dihapus total oleh native 20.0; styling combo
   tidak pernah aktif di versi manapun sebelum 20.0). Untuk kasus ini, "kesetaraan terhadap 19.0"
   diukur dari **maksud/isi** yang didokumentasikan (popup lama via bullet §6 tanpa ID di atas; typo
   `comboParent` vs `combo_parent_id` via `BSL-016`), bukan dari perilaku 19.0 yang identik piksel —
   sudah eksplisit disetujui dev sebagai perubahan yang disengaja (`MF-29`, `MF-34`), bukan gap
   tersembunyi.

Tidak ada dari empat poin di atas yang memblokir Step 5 (step ini tidak ada gate) — tapi #1 dan #2
sebaiknya diperbaiki di `01b_BASELINE_SPEC.md` kapan pun ada sesi revisi baseline (Step 4 sudah
lewat untuk modul ini), supaya AC berikutnya tidak perlu menyitir "tanpa BSL-NNN" lagi.

---

## AC-01 — Margin Sale & Minimum Sale Price Computation

Cakupan: `product.category`, `product.template`, `product.product`. Tidak ada perubahan kode Python
di area ini untuk migrasi 20.0 (`03_MIGRATION_SPEC.md` §2b "Kompatibilitas Data Model": *"Tidak ada
perubahan model Python dibutuhkan"*) — AC di grup ini murni regresi, bukan area berisiko migrasi.

**AC-01-01** (verifies §3 product.template, tanpa BSL-NNN — lihat Catatan Kelengkapan #1)
Given kategori produk dengan `margin_sale = 20.0`
When produk (template) baru dibuat di kategori tersebut, tanpa override manual
Then `margin_sale` produk = `20.0` (diwarisi dari kategori)
*Test existing: `tests/test_margin_sale.py::test_margin_sale_from_category` (AC lama: AC-01-01,
project 18.0→19.0 — perilaku sama, nomor tetap kebetulan sama).*

**AC-01-02** (verifies §3 product.template, tanpa BSL-NNN)
Given produk dengan `margin_sale` yang sudah diwarisi dari kategori (`20.0`)
When `margin_sale` ditimpa manual jadi `35.0` lalu di-flush/invalidate
Then nilai tetap `35.0` (tidak revert ke nilai kategori — compute+store persisten sampai dependency
`categ_id.margin_sale` sendiri berubah)
*Test existing: `test_margin_sale_manual_override_persists` (AC lama: AC-01-02).*

**AC-01-03** (verifies §3 product.template, tanpa BSL-NNN)
Given produk dengan `standard_price = 100.0`, `margin_sale = 20.0`
When `minimum_sale_price` dihitung (compute)
Then `minimum_sale_price = 120.0` (`standard_price * (1 + margin_sale/100)`)
*Test existing: `test_minimum_sale_price_computation` (AC lama: AC-01-03).*

**AC-01-04** (verifies `BSL-008`)
Given produk dengan `standard_price = 100.0`
When `minimum_sale_price` di-set manual jadi `150.0`
Then `margin_sale` ter-inverse jadi `50.0` (`((150/100) - 1) * 100`)
*Test existing: `test_minimum_sale_price_inverse` (AC lama: AC-01-04).*

**AC-01-05** (verifies `BSL-008` guard clause)
Given produk dengan `standard_price = 0.0`
When `minimum_sale_price` di-set manual jadi `999.0`
Then `margin_sale` = `0.0` (guard div-by-zero, bukan error/`inf`)
*Test existing: `test_minimum_sale_price_zero_standard_price_guard` (AC lama: AC-01-05).*

**AC-01-06** `[DIWARISI-SOURCE — pertahankan identik]` (verifies `BSL-010`, `FINDINGS.md MF-01`)
Given template dengan 2 variant (A, B) dari 1 attribute
When `margin_sale` variant A di-set manual jadi `20.0`
Then `product_tmpl_id.margin_sale` ikut jadi `20.0` DAN variant B (compute dari template yang sama)
ikut berubah jadi `20.0` — margin per-variant TIDAK PERNAH bisa divergen dari template (quirk warisan,
bukan bug baru, jangan diperbaiki tanpa keputusan baru)
*Test existing: `test_margin_sale_inverse_writes_to_shared_template_not_per_variant`.*

**AC-01-07** `[DIWARISI-SOURCE — pertahankan identik]` `[DIWARISI-SOURCE — MF-23, "dibiarkan"]`
(verifies `BSL-019`)
Given produk dengan `lst_price < minimum_sale_price` (kondisi `is_less_minimum_sale = True`)
When `lst_price` diubah lewat jalur yang TIDAK memicu recompute manual (mis. write langsung ke DB atau
compute lain yang tidak eksplisit invalidate `is_less_minimum_sale`)
Then `is_less_minimum_sale` BOLEH tetap menunjukkan nilai lama (stale) sampai reload penuh — ini
adalah quirk yang harus tetap ada (TIDAK ditambahkan `@api.depends`), keputusan dev 2026-08-27
(project 18.0→19.0) "dibiarkan dulu" masih berlaku, bukan regresi migrasi
*Belum ada test otomatis untuk memverifikasi ABSENSI recompute ini secara eksplisit — regression risk
kalau ada perubahan tidak sengaja di Step 6 yang "memperbaiki" ini. Rekomendasi Step 9: minimal smoke
test bahwa `@api.depends` masih tidak ada di source (grep/AST check), bukan perilaku runtime.*

**AC-01-08** `[GAP TEST BARU — belum pernah ditest]` (verifies `BSL-012`)
Given form produk (`product.product`) terbuka di UI, `margin_sale` field kosong
When user mengubah `margin_sale` di form (memicu `@api.onchange('margin_sale')`) SEBELUM record
di-save
Then `_set_product_margin_sale` terpanggil lewat jalur onchange (bukan cuma jalur `write()`/inverse
klasik) — write-back ke `product_tmpl_id` sudah bisa terjadi sebelum variant sendiri disimpan
*Belum ada test. `BSL-012` baru didokumentasikan Step 1 project ini (mekanisme granular, bukan
kontradiksi klaim lama) — test yang ada (`test_margin_sale_inverse_writes_to_shared_template_not_per_variant`)
hanya menguji lewat `write()` langsung, tidak mensimulasikan onchange form. Rendah risiko migrasi
(Python tidak berubah), tapi test coverage genuinely kosong untuk jalur ini — dicatat untuk Step 9,
bukan Step 6.*

---

## AC-02 — Bulk-Assign Margin Wizard (`wizard.margin.product`)

Tidak ada perubahan Python di area ini (`03_MIGRATION_SPEC.md` §2b). Risiko migrasi rendah, tapi
tetap perlu smoke-test manual per rekomendasi §2b urutan testing poin 6.

**AC-02-01** (verifies `BSL-001`, `BSL-002`)
Given user berada di list view Product Template, memilih 1+ record
When user menjalankan action server "Assign Margin" (`product_template_margin_sale_action_server`)
Then dialog modal `wizard.margin.product` terbuka dengan `product_template_ids` pre-populated dari
record terpilih; `is_product` = `False` (context `active_model = product.template`) sehingga field
`product_template_ids` yang ditampilkan, bukan `product_ids`

**AC-02-02** (verifies `BSL-001`, `BSL-002`, `BSL-011`)
Given user berada di list view Product Variant, memilih 1+ record
When user menjalankan action server "Assign Margin" (`product_product_margin_sale_action_server`)
Then dialog modal `wizard.margin.product` terbuka dengan `product_ids` pre-populated; `is_product` =
`True` sehingga field `product_ids` yang ditampilkan — implementasi `action_assign_margin()` terpisah
dari versi template (dua method paralel, bukan satu method di-share)

**AC-02-03** `[DIWARISI-SOURCE — typo `action_assing_margin` dipertahankan]` (verifies `BSL-003`)
Given wizard terbuka dengan `margin = 15.0`, 1+ produk terpilih
When user klik tombol "Assign" (memanggil `action_assing_margin()` — nama method TETAP typo, bukan
"assign")
Then `margin_sale` SETIAP record terpilih ditulis jadi `15.0`, tanpa konfirmasi tambahan, tanpa syarat
*Test existing: `test_wizard_assign_margin_from_template_list` (AC lama: AC-03-01).*

**AC-02-04** (verifies `BSL-003`)
Given wizard terbuka dengan `margin` diisi
When user klik tombol "Cancel" (`special="cancel"`)
Then tidak ada `margin_sale` record manapun yang berubah
*Belum ada test eksplisit untuk jalur Cancel — low risk (behavior native `special="cancel"`, bukan
logic modul), tapi belum diverifikasi otomatis.*

---

## AC-03 — POS Payment-Time Enforcement (dialog konfirmasi/blocking)

`PosStore.prototype.pay()` — API method sudah full camelCase sejak migrasi 18→19, TIDAK berubah lagi
di 20.0 (`03_MIGRATION_SPEC.md` `DIFF-06`: *"guard baru `canPay()` di native tidak konflik dengan
override modul"*). Risiko migrasi rendah untuk grup ini, tapi WAJIB tetap dites nyata (bukan
diasumsikan aman dari baca kode — eksplisit dicatat di §2b urutan testing poin 5).

**AC-03-01** (verifies `BSL-005`)
Given order dengan semua line di atas `minimum_sale_price_with_tax` masing-masing produk
When kasir klik "Pay"
Then langsung `super.pay(...)` — TIDAK ADA dialog apapun yang muncul

**AC-03-02** (verifies `BSL-004`, `BSL-006`)
Given order dengan 1+ line di bawah minimum, `config.is_blocked_warning = False` (default,
`blocking_transaction_pos` OFF)
When kasir klik "Pay"
Then dialog konfirmasi muncul (title "Price unit less than minimum price", body "Some products are
below the minimum price. Proceed to payment?")
And ketika user klik confirm → lanjut ke payment screen
*Test existing: tour `pos_margin_threshold_below_minimum_confirm_tour`
(`tests/test_margin_threshold_tour.py::test_pos_margin_threshold_below_minimum_confirm_tour`).*

**AC-03-03** `[GAP TEST — belum ditest]` (verifies `BSL-006`)
Given kondisi sama seperti AC-03-02 (dialog konfirmasi muncul)
When user klik DECLINE/dismiss dialog (bukan confirm)
Then `return` — pembayaran dibatalkan, kasir tetap di ProductScreen, TIDAK lanjut ke payment
*Tour yang ada (`..._confirm_tour`) hanya menguji jalur confirm (`Dialog.confirm()` selalu dipanggil)
— jalur decline TIDAK PERNAH ditest. Ini bukan carry-forward dari `BSL-018` (yang soal "tidak ada
popup sama sekali"/"assert warning terpisah") — ini gap BARU yang ditemukan saat menyusun AC ini,
belum pernah dicatat di `FINDINGS.md` manapun. Direkomendasikan ditutup di Step 9 project ini
(risiko rendah secara fungsional, tapi coverage genuinely kosong untuk satu-satunya jalur yang
benar-benar MEMBATALKAN pembayaran).*

**AC-03-04** (verifies `BSL-007`)
Given order dengan 1+ line di bawah minimum, `config.is_blocked_warning = True`
(`blocking_transaction_pos` ON)
When kasir klik "Pay"
Then `AlertDialog` muncul (title sama, body "Some products are below the minimum price. Please
check !"), HANYA tombol "Ok", dismiss TIDAK melanjutkan ke payment — pembayaran diblokir total
*Test existing: tour `pos_margin_threshold_below_minimum_blocked_tour`.*

**AC-03-05** `[GAP TEST — carry-forward 2x, belum ada keputusan dev]` (verifies `BSL-018`, bagian
"AC-02-03" lama)
Given order dengan SEMUA line di atas minimum masing-masing
When kasir klik "Pay"
Then TIDAK ADA dialog apapun (bukan cuma "tidak block" — benar-benar nol popup, termasuk tidak ada
flash/render sekilas)
*Belum ada test. Carry-forward dari `01b_BASELINE_SPEC.md BSL-018` (sudah dilewati DUA project
migrasi sebelumnya, 17.0→18.0 dan 18.0→19.0). **Keputusan dev masih diperlukan**: ditutup di Step 9
project ini, atau tetap dilewati untuk ketiga kalinya? Tidak diputuskan sepihak di sini — hanya
diwariskan sebagai AC eksplisit supaya Step 9 tidak melewatkannya tanpa sadar.*

---

## AC-04 — POS Orderline Warning Display (Owl/JS)

**AC-04-01** (verifies `BSL-015`)
Given order line dengan `line.isLessMinimumSalePrice = True`
When orderline dirender di ProductScreen
Then `<li>` warning teks + `line.minimumSalePriceWithTax` (format currency) muncul, disisipkan SEBELUM
slot `t-slot='default'` di dalam `ul.info-list` (xpath descendant, bukan direct-child — mempertahankan
fix lama `FINDINGS.md` MF-20)

**AC-04-02** `[RISIKO MIGRASI — perhatikan §6 BSL-016]` (verifies `BSL-016`)
Given order line dengan `line.isLessMinimumSalePrice = True`
When `t-attf-class` pada `<li class="orderline">` dievaluasi
Then class `text-danger` MUNCUL bersama (bukan menggantikan) kondisi combo core
(`line.combo_parent_id ? 'border-start border-3 ms-4' : ''` — lihat AC-05), keduanya dalam satu
ekspresi `t-attf-class` gabungan
*`03_MIGRATION_SPEC.md` `DIFF-08`: "tidak perlu tindakan" untuk migrasi 20.0 ini, TAPI baseline
eksplisit menandai (`BSL-016`) bahwa kalau native 20.0 kelak mengubah kondisi class combo lagi,
patch modul ini wajib menyesuaikan ekspresi GABUNGAN ini, bukan cuma menambah class terpisah — jadi
regression check di AC ini tetap bernilai tinggi walau tidak ada perubahan kode saat ini.*

**AC-04-03** `[GAP TEST — carry-forward 2x, belum ada keputusan dev]` (verifies `BSL-018`, bagian
"AC-02-04" lama)
Given order line di bawah minimum, warning tampil (AC-04-01)
When warning tersebut diperiksa
Then teks pesan DAN warna (`text-danger`) ter-assert SECARA TERPISAH (bukan cuma "tour tidak crash")
*Belum ada test. Sama seperti AC-03-05 — carry-forward `BSL-018`, keputusan dev masih diperlukan
apakah ditutup di project ini.*

---

## AC-05 — Combo-Child Styling (`MF-34`, AKTIF pertama kali di 20.0) `[RISIKO MIGRASI TINGGI]`

> Tidak bisa disitat ke `BSL-NNN` tunggal untuk perilaku "combo child bergaris kiri" itu sendiri —
> BSL-016 mendokumentasikan EKSPRESI-nya (§AC-04-02), tapi styling ini TIDAK PERNAH benar-benar aktif
> di 19.0 (maupun 17.0/18.0) karena typo `line.comboParent` (properti yang tidak pernah ada di model
> `pos.order.line` versi manapun). `MF-34` dikonfirmasi tuntas: sejak branch `17.0`. Dev secara
> eksplisit memutuskan MEMPERBAIKI (bukan mempertahankan typo) untuk 20.0 — jadi AC ini BUKAN
> "samakan dengan 19.0" seperti grup lain, melainkan "verifikasi perbaikan yang sudah disetujui dev
> bekerja seperti spesifikasi core, dan tidak mengubah apapun selain styling combo."

**AC-05-01** `[RISIKO MIGRASI TINGGI — belum diverifikasi visual live]`
Given `line.combo_parent_id` terisi (order line adalah bagian dari combo product) — field yang benar
digunakan setelah `MF-34` diperbaiki dari `line.comboParent` (typo, selalu `undefined`)
When orderline combo-child dirender
Then class `border-start border-3 ms-4` muncul pada `<li class="orderline">` line tersebut — styling
combo AKTIF untuk pertama kalinya di seluruh riwayat modul ini (17.0-19.0 tidak pernah menampilkannya)
*Status verifikasi per `FINDINGS.md MF-34`: XML well-formed + module update sukses SUDAH dikonfirmasi,
TAPI verifikasi visual live di POS dengan combo product sungguhan BELUM dilakukan (DB QA Docker 20.0
belum ada chart of accounts/config POS). **WAJIB jadi Tour test baru di Step 9** — tidak boleh
dianggap otomatis benar dari baca kode saja (pola yang sama seperti pesan `MF-33`/`MF-36` yang
sempat salah kalau cuma dibaca, bukan dijalankan). Tidak ada test existing untuk AC ini — perlu setup
data combo product (`available_in_pos` + combo config) yang belum ada di `tests/test_margin_threshold_tour.py`
saat ini.*

---

## AC-06 — Backend Product/Category Form Views

**AC-06-01** `[DIWARISI-SOURCE — MF-24, pertahankan pola `position="replace"`]` `[RISIKO MIGRASI —
DIFF-04]` (verifies `BSL-013`)
Given form Product Template dibuka
When field `list_price` dirender
Then field itu adalah versi HASIL REPLACE modul ini (`decoration-danger="list_price < minimum_sale_price"`,
`options="{'currency_field': 'currency_id', 'field_digits': True}"` — atribut currency BARU
ditambahkan `DIFF-04`, dikonfirmasi dev, supaya tidak regresi dari `options` baru native 20.0), BUKAN
versi native murni — field `margin_sale`/`minimum_sale_price`/`minimum_sale_price_with_tax` muncul
sebelum `categ_id`, `invisible` untuk produk multi-variant (`product_variant_count > 1 and not
is_product_variant`)
*Bug `MF-24` (atribut core `optional`/`decoration-muted` hilang akibat `position="replace"`) TETAP
ADA secara sengaja — `position` TIDAK diubah jadi `attributes`, sesuai keputusan dev "dipertahankan".
AC ini memverifikasi bug itu TIDAK diam-diam "diperbaiki" saat migrasi (regresi ke arah yang salah).*

**AC-06-02** `[RISIKO MIGRASI — DIFF-02/MF-31, anchor pindah]` (verifies `BSL-014`)
Given form Product Category dibuka
When field `margin_sale` dirender
Then muncul sebelum `property_cost_method`, di view yang sekarang inherit
`account.view_category_property_form` (anchor lama `stock_account.view_category_property_form_stock`
sudah tidak ada di 20.0)

**AC-06-03** `[GAP BASELINE — bullet §6 tanpa BSL-NNN, lihat Catatan Kelengkapan #2]` `[SUDAH TIDAK
BERLAKU di 20.0 — DIHAPUS oleh `MF-29`]`
Given (konteks 19.0) form Product Variant Easy Edit (popup ringan dari list Product Variants)
When popup dibuka
Then (di 19.0) `lst_price` tampil dengan `decoration-danger="is_less_minimum_sale"` (pola
`position="replace"`, ini instance `MF-25`), group `pricing` menampilkan `margin_sale`/
`minimum_sale_price`/`minimum_sale_price_with_tax`
*Di 20.0, view `product.product_variant_easy_edit_view` yang jadi target inherit-nya DIHAPUS TOTAL
oleh native (`MF-29`) — popup ini TIDAK ADA LAGI, digantikan kolom list (AC-07). AC ini didaftar
untuk dokumentasi kelengkapan SAJA (isi popup lama, jadi acuan visual-parity AC-07) — bukan AC yang
perlu lulus/gagal secara independen di 20.0. Catatan efek samping: karena view ini hilang, instance
`MF-25` (bug `position="replace"` di `lst_price` popup ini) ikut hilang secara STRUKTURAL (bukan
diperbaiki sengaja) — `MF-25` sebagai finding tetap dicatat "terbuka" di `FINDINGS.md` karena bug
class-nya (pola `MF-24`) masih hidup di AC-06-01, tapi lokasi spesifik `MF-25` sendiri sudah moot.*

---

## AC-07 — Product Variants List Columns (pengganti popup, `MF-29`/`DIFF-03`) `[RISIKO MIGRASI TINGGI]`

> Tidak bisa disitat `BSL-NNN` langsung (UI baru, tidak ada di 19.0) — kesetaraan diukur terhadap ISI
> popup lama (`AC-06-03` di atas, bullet §6 tanpa ID) + keputusan desain dev yang tercatat di
> `FINDINGS.md MF-29`. Wajib direview visual Step 10 (dicatat eksplisit sebagai syarat oleh dev saat
> keputusan diambil), bukan cuma smoke functional.

**AC-07-01** (verifies keputusan dev `MF-29` poin 2, ekuivalen `AC-06-03`)
Given list "Product Variants" (`product.product_product_tree_view`, dibuka lewat smart button "N
Variants" dari Product Template ATAU menu Inventory/Sales > Products > Product Variants)
When list dirender
Then kolom `margin_sale`/`minimum_sale_price` TAMPIL LANGSUNG (`optional="show"`, tanpa perlu toggle
manual) — menyamai popup lama yang selalu tampil tanpa opsi sembunyi

**AC-07-02** (verifies `AC-06-03`/instance `MF-25` lama, direplikasi sebagai `position="attributes"`
di record baru — lihat catatan implementasi `03_MIGRATION_SPEC.md` §2a)
Given baris produk dengan `is_less_minimum_sale = True`
When kolom `lst_price` dirender di list Product Variants
Then kolom itu berwarna merah (`decoration-danger`) — TAPI kali ini via `position="attributes"` (BUKAN
`replace`), sehingga atribut native (`options`/`optional`) TETAP UTUH, tidak mengulang bug `MF-24`/
`MF-25` di lokasi baru ini

**AC-07-03** `[RISIKO MIGRASI — MF-38, visual parity]`
Given baris produk dengan `margin_sale < 0.0`
When kolom `margin_sale` dirender
Then kolom berwarna merah (`decoration-danger="margin_sale < 0.0"`) — DAN kolom baru "Incl. Tax"
(`minimum_sale_price_with_tax`, field baru di `ProductProduct`, mirror pola `ProductTemplate`) tampil
terisi dengan nilai benar — menyamai 2 elemen visual popup lama yang sempat tertinggal di draft awal
`MF-29`

**AC-07-04** `[RISIKO MIGRASI TINGGI — cross-module, MF-37]` (verifies koordinasi lintas-modul, lihat
juga AC-09)
Given `sale_margin_threshold` JUGA terinstall di database yang sama
When list Product Variants dibuka
Then kolom `margin_sale`/`minimum_sale_price` HANYA muncul SATU SET (milik `pos_margin_threshold`) —
TIDAK dobel dengan kolom yang ditambahkan `sale_margin_threshold` ke view yang sama
*Sudah diverifikasi manual sekali via Docker (`MF-37` RESOLVED) — **belum ada test otomatis**
(unit/integration/tour) untuk regresi ini. WAJIB Step 9 dengan kedua modul terinstall bersamaan
(lihat `CLAUDE.md` §Adaptasi multi-modul).*

---

## AC-08 — POS Frontend Data Loading

**AC-08-01** (verifies `BSL-009`)
Given konfigurasi POS dibuka (`pos.config`)
When payload data produk dikirim ke frontend (`_load_pos_data_fields`)
Then field `minimum_sale_price` dan `minimum_sale_price_with_tax` termasuk di payload (ditambahkan
lewat override `@api.model`, memanggil `super()` dulu)

**AC-08-02** (verifies `BSL-009`, dipakai downstream oleh AC-04)
Given record produk sudah dimuat di frontend POS (`ProductProduct` patch)
When `get_minimum_sale_price()`/`get_minimum_sale_price_with_tax()` dipanggil
Then mengembalikan `this.minimum_sale_price`/`this.minimum_sale_price_with_tax` masing-masing —
pengganti mekanisme lama `_loader_params_product_product` (17.0)

**AC-08-03** `[DIWARISI-SOURCE — dead patch, pertahankan]` (verifies §6 catatan `setUnitPrice`,
`DIFF-10`)
Given `PosOrderline.prototype.setUnitPrice(price)` dipatch modul ini
When method dipanggil
Then perilaku identik native (`super.setUnitPrice(price)`, tidak ada efek tambahan) — patch kosong ini
DIPERTAHANKAN (tidak dihapus) sesuai larangan `CLAUDE.md` "jangan refactor demi readability", kecuali
dev putuskan lain secara eksplisit

---

## AC-09 — Cross-Module Coordination (`sale_margin_threshold`)

**AC-09-01** `[DIWARISI-SOURCE — pertahankan, `PERLU-KEPUTUSAN` lama sudah dianggap final]` (verifies
`BSL-020`, `FINDINGS.md MF-03`)
Given `pos_margin_threshold` DAN `sale_margin_threshold` sama-sama terinstall
When model `wizard.margin.product` (didefinisikan `_name` identik di kedua modul) di-resolve ORM
Then `__mro__` selalu menghasilkan class `sale_margin_threshold` yang menang (class
`pos_margin_threshold` hilang total dari registry, bukan cuma kalah prioritas) — model gabungan tetap
bisa `create()` tanpa error
*Test existing: `tests/test_cross_module.py::test_wizard_margin_product_model_merged_when_both_installed`
(skip kalau `sale_margin_threshold` tidak terinstall — WAJIB dijalankan dengan environment kedua modul
bersamaan di Step 9, lihat `CLAUDE.md` §Adaptasi multi-modul).*

**AC-09-02** `[DIWARISI-SOURCE — pertahankan]` (verifies `BSL-021`, `FINDINGS.md MF-02`)
Given view settings milik `pos_margin_threshold` sendiri
When arch view diperiksa
Then field `blocking_transaction_order` TIDAK muncul di view itu (field dideklarasikan di
`res.config.settings` tapi hanya bermakna kalau `sale_margin_threshold` juga terinstall — modul ini
sendiri tidak pernah membacanya)
*Test existing: `test_blocking_transaction_order_field_has_no_view_in_this_module` (AC lama: AC-04-01).*

**AC-09-03** — lihat AC-07-04 (kolom list tidak dobel) — didaftar ulang di sini sebagai bagian
"Cross-Module Coordination" supaya Step 9/10 tidak melewatkannya saat mencari AC per kategori
"cross-module", walau isinya sama.

---

## AC-10 — Quirk / Dead Code yang Wajib Dipertahankan Identik (regresi-only, prioritas rendah)

Grup ini murni "pastikan TIDAK diam-diam diperbaiki/dihapus selama migrasi" — bukan fitur aktif.

**AC-10-01** `[DIWARISI-SOURCE]` (verifies `BSL-022`, `FINDINGS.md MF-04`)
Given `__manifest__.py` `data:` list
When diperiksa
Then `views/product_template_views.xml` TIDAK terdaftar (dead file tetap sengaja tidak dimuat, mencegah
duplikat XML-ID dengan `views/products.xml`)

**AC-10-02** `[DIWARISI-SOURCE]` (verifies §8, `models/pos_session.py`)
Given `models/pos_session.py`
When isi file diperiksa
Then tetap kosong murni komentar dokumentasi (override lama `_loader_params_product_product` TIDAK
direintroduksi)
*`03_MIGRATION_SPEC.md` §2c mengonfirmasi `git diff migration/19.0` kosong untuk file ini — AC ini
murni regression-guard untuk Step 8/9, bukan area kerja.*

**AC-10-03** `[DIWARISI-SOURCE — informational, tidak perlu AC formal terpisah]`
`controllers/controllers.py` (seluruh isi di-comment sejak awal, `__init__.py` tetap `from . import
controllers` no-op) — tidak ada BSL-NNN, risiko nol, cukup dicek sekali saat Step 8 code review bahwa
file tidak disentuh, tidak perlu test otomatis.

---

## Ringkasan Cakupan

| Grup | Jumlah AC | Risiko Migrasi Tinggi | Gap Test Belum Tertutup |
|---|---|---|---|
| AC-01 Margin computation | 8 | Tidak | AC-01-07 (regresi absensi), AC-01-08 (baru) |
| AC-02 Wizard | 4 | Tidak | AC-02-04 (jalur Cancel) |
| AC-03 POS payment dialog | 5 | Tidak (kode stabil, tapi wajib dites nyata) | AC-03-03 (baru), AC-03-05 (`BSL-018`, carry-forward 2x) |
| AC-04 Orderline warning | 3 | Ya (AC-04-02, `BSL-016` ekspresi gabungan) | AC-04-03 (`BSL-018`, carry-forward 2x) |
| AC-05 Combo styling | 1 | **Ya, tinggi** (`MF-34`, behavior baru) | AC-05-01 (verifikasi visual live belum dilakukan) |
| AC-06 Backend forms | 3 | Ya (AC-06-01 `DIFF-04`, AC-06-02 `DIFF-02`) | Tidak |
| AC-07 List columns (`MF-29`) | 4 | **Ya, tinggi** (seluruh grup) | AC-07-04 (dedup cross-module, belum ada test otomatis) |
| AC-08 POS data loading | 3 | Tidak | Tidak |
| AC-09 Cross-module | 3 | Ya (AC-09-03/AC-07-04) | AC-07-04 (sama) |
| AC-10 Dead code/quirk | 3 | Tidak | Tidak (regresi-only) |

**Total:** 37 AC leaf. 6 AC menandai gap test yang genuinely belum tertutup (2 di antaranya,
AC-03-05/AC-04-03, adalah carry-forward `BSL-018` yang SUDAH dilewati dua project migrasi sebelumnya
— rekomendasi eksplisit: putuskan sekarang, jangan carry-forward ketiga kalinya tanpa keputusan
sadar).
