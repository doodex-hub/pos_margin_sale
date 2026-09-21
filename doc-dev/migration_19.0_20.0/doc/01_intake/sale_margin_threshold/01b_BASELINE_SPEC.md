# Baseline Spec — sale_margin_threshold

**Step:** 1 — Intake & Scope (pelengkap `01a_MIGRATION_INTAKE.md`)
**Tujuan:** dokumentasikan behavior as-is di 19.0 (branch `migration/19.0`, identik dengan working
tree `migration/20.0` saat ini — belum ada edit migrasi apapun).
**Tanggal:** 2026-09-21
**Sumber:** Direkonsiliasi dari `doc-dev/migration_18.0_19.0/doc/01_intake/sale_margin_threshold/01b_BASELINE_SPEC.md`
(baseline 18.0→19.0 dari project sebelumnya, dokumen ini memainkan peran "baseline spec dari
project migrasi sebelumnya" karena tidak ada `FUNCTIONAL_SPEC.md` lama yang ditemukan — lihat
`01a_MIGRATION_INTAKE.md` §4) + cross-check kode 19.0 aktual (branch `migration/19.0`, identik
`migration/20.0` saat ini) + `FINDINGS.md` (root `doc-dev/migration_19.0_20.0/doc/`, berisi
`MF-08`/`MF-20`/`MF-21`/`MF-23`/`MF-24` yang dibawa dari project 18.0→19.0) + **temuan baru sesi ini:
`doc-dev/backfill/FINDINGS.md` (`F-05`) — dokumen characterization test EKSEKUSI NYATA (Docker Odoo
17.0, 2026-07-31) yang sebelumnya TIDAK PERNAH direferensikan oleh baseline spec 17.0→18.0 maupun
18.0→19.0, walau berada di repo yang sama dan langsung relevan ke `BSL-009` di bawah.**

> Provenance merujuk ke tiga sumber: `(ref: 18-19/BSL-NNN)` (baseline langsung sebelumnya),
> `(ref: 17-18/MF-NNN)` (lewat rantai 18-19), dan `(ref: doc-dev/backfill/FINDINGS.md F-NN)` (characterization
> test tereksekusi, ditemukan baru sesi ini, terpisah dari rantai baseline spec manapun).

---

## Ringkasan untuk Review — Perlu Konfirmasi User

**Tally provenance:** 16 klaim `[MATCH]`, 1 `[GAP]`, 2 `[NO-SPEC]` (19 klaim total, `BSL-001`..`BSL-019`).

- **`[BSL-009]` `[GAP]` — koreksi mekanisme bug `MF-08` (singleton-assumption di `action_confirm`),
  BUKAN koreksi keputusan.** Baseline 17-18/18-19 mendeskripsikan bug ini sebagai "kesalahan
  validasi margin SENYAP untuk order ke-2 dst dalam batch confirm". Kode aktual + bukti eksekusi
  nyata di `doc-dev/backfill/FINDINGS.md` `F-05` (Docker Odoo 17.0, 2026-07-31, direproduksi 2×
  termasuk demo data `sale_stock` core Odoo sendiri ikut crash) menunjukkan ini BUKAN senyap —
  ini `ValueError: Expected singleton` yang men-CRASH `action_confirm()` total begitu dipanggil
  pada >1 `sale.order` sekaligus (batch confirm dari list view). **Keputusan dev 2026-08-27
  ("pertahankan, jangan diperbaiki") tetap berlaku tidak berubah** — hanya presisi deskripsi
  mekanismenya yang dikoreksi di sini, TIDAK perlu keputusan baru.
- **Dokumen pelengkap yang terlewat 2 siklus sebelumnya:** `doc-dev/backfill/` (spec + test +
  `FINDINGS.md` untuk ketiga modul termasuk `sale_margin_threshold`, dieksekusi nyata bukan cuma
  baca kode) ada di repo ini sejak sebelum project 17.0→18.0, tapi TIDAK PERNAH disebut di
  `01a_MIGRATION_INTAKE.md`/`01b_BASELINE_SPEC.md` manapun sebelumnya. Dipakai sebagai sumber
  tambahan di sini (khususnya `BSL-009`) — lihat `01a` §4a untuk detail & pertanyaan ke dev.
- `[BSL-011]` `[NO-SPEC]` (baru) — ditemukan bug singleton-assumption KEDUA (instance terpisah dari
  `BSL-009`/`MF-08`) di compute `_compute_is_rental_order_installed`: sudah ada `for record in
  self:`, tapi kondisi di dalam loop membaca `self.is_rental_order` (recordset PENUH), bukan
  `record.is_rental_order`. Berpotensi jadi titik gagal LEBIH DULU dari `BSL-009` kalau field
  `is_rental_order_installed_true` pernah di-compute untuk >1 `sale.order` di context LAIN (bukan
  cuma di dalam `action_confirm`). Belum pernah didokumentasikan di baseline/`FINDINGS.md` manapun.
- `[BSL-019]` `[NO-SPEC]` (baru) — `list_price`/`lst_price` di-`position="replace"` (bukan
  `position="attributes"`) di 3 titik view (form `product.template`, form
  `product_variant_easy_edit_view`), pola PERSIS `MF-24` yang sudah tercatat untuk modul sibling
  `pos_margin_threshold` — TAPI belum pernah dicatat untuk modul INI walau kode-nya sudah begini
  sejak awal. Kode aktif (yang menang setelah `BSL-013` overwrite XML-ID) kehilangan
  `options="{'currency_field': 'currency_id', 'field_digits': True}"` milik core.
  **Rekomendasi (di luar scope dua dokumen ini):** kalau dev setuju, tambahkan sebagai finding baru
  (`MF-28`/`MF-29`) ke `FINDINGS.md` — TIDAK saya lakukan sendiri karena task ini dibatasi hanya
  menulis `01a`/`01b`.
- `MF-20` (`security/groups.xml` `implied_ids` diisi kategori bukan grup) dan `MF-21`
  (`is_less_minimum_sale` tanpa `@api.depends`) dikonfirmasi ULANG masih persis sama di kode
  19.0/20.0 saat ini (`BSL-017`/`BSL-018` di bawah) — keduanya masih **terbuka**, belum ada
  keputusan dev, dibawa apa adanya.
- `MF-08` sudah ada keputusan eksplisit dev (dipertahankan, 2026-08-27) — **tidak perlu keputusan
  baru**, hanya perlu diperbarui pemahaman mekanismenya (lihat poin `BSL-009` di atas).
- **Dependency Enterprise Rental** (`sale_renting`, field `is_rental_order`) dikonfirmasi masih ada
  persis nama sama di `enterprise20` (`sale_renting/models/sale_order.py:95`) — tidak ada indikasi
  deprecation/rename di titik ini (verifikasi mendalam tetap domain Step 2).
- Kolisi `wizard.margin.product` dengan `pos_margin_threshold` (`MF-03`/`BSL-015`) — modul INI yang
  selalu menang MRO, tidak berubah dari siklus sebelumnya.

---

## 1. Tujuan Modul

Menegakkan margin minimum penjualan saat konfirmasi Sale Order. Kategori/template/variant produk
punya field `margin_sale` (persentase markup atas `standard_price`); saat `action_confirm()`
dipanggil, modul mengecek semua baris order — kalau ada yang di bawah `minimum_sale_price`, sistem
memblok (`ValidationError`, bilingual EN/FR generik, bukan mekanisme `.po` standar) atau membuka
wizard konfirmasi (`sale.confirmation.wizard`), tergantung setting `blocking_transaction_order`.
Rental order (modul Enterprise `sale_renting`) sepenuhnya dikecualikan dari pengecekan ini. Modul
juga menyediakan wizard bulk-assign margin (`wizard.margin.product`) yang identik strukturnya
dengan sibling module `pos_margin_threshold`.

## 2. Model & Tanggung Jawab

| Model | Tanggung Jawab |
|---|---|
| `product.category` (extend) | `margin_sale` — nilai default yang diwarisi template lewat compute. |
| `product.template` (extend) | `margin_sale`, `minimum_sale_price`, `minimum_sale_price_with_tax`, `module_pos_margin_threshold` (dedup UI kalau sibling terinstall). |
| `product.product` (extend) | Sama seperti template + `is_less_minimum_sale` (warning UI). |
| `sale.order` (extend) | Override `action_confirm()` — validasi margin, kecuali rental. |
| `sale.order.line` (extend) | Field `minimum_sale_price` (related), dipakai decoration view. |
| `sale.confirmation.wizard` (baru, `_name`) | Wizard konfirmasi override minimum price. |
| `wizard.margin.product` (baru, `_name` — kolisi dengan `pos_margin_threshold`) | Bulk-assign margin. |
| `res.config.settings` (extend) | Expose `blocking_transaction_order`. |

## 3. Field dengan Makna Bisnis

### `product.category`
- `margin_sale` (Float) — nilai markup default, diwarisi `product.template` lewat
  `_compute_margin_sale` (`@api.depends('categ_id.margin_sale')`).

### `product.template`
- `margin_sale` (Float, compute+store+readonly=False, `tracking=True`) — markup % di atas
  `standard_price`.
- `minimum_sale_price` (Float, compute `_compute_minimum_sale_price` + inverse
  `_inverse_minimum_sale_price`, store) — `standard_price * (1 + margin_sale/100)`. Inverse
  memungkinkan user mengedit harga minimum langsung, otomatis menghitung balik `margin_sale`.
- `minimum_sale_price_with_tax` (Float, compute, store) — `minimum_sale_price` + total persentase
  `taxes_id`.
- `module_pos_margin_threshold` (Boolean, compute, `@api.depends_context('uid')`, tidak stored) —
  `True` kalau `pos_margin_threshold` terinstall; drives `invisible=` untuk cegah field margin
  tampil dobel.

### `product.product`
- `margin_sale` (Float, compute+inverse+store) — inverse (`_set_product_margin_sale`) menulis
  balik ke `product_tmpl_id` (TEMPLATE bersama, bukan variant sendiri — lihat `doc-dev/backfill/FINDINGS.md`
  `F-01`, instance sibling module, pola identik di sini walau belum ada test eksekusi khusus modul
  ini untuk klaim ini).
- `minimum_sale_price` (Float, compute+inverse+store) — sama formula seperti template.
- `is_less_minimum_sale` (Boolean, compute `_compute_warning`, **tidak ada `@api.depends`** — lihat
  `BSL-018`) — `lst_price < minimum_sale_price`.

### `sale.order`
- `is_rental_order_installed_true` (Boolean, compute, tidak stored) — `True` HANYA kalau record
  punya attribute `is_rental_order` (modul Rental Enterprise terinstall) DAN nilainya truthy.

### `sale.order.line`
- `minimum_sale_price` (Float, `related='product_id.minimum_sale_price'`) — murni untuk decoration
  view, `column_invisible` di list.

### `sale.confirmation.wizard`
- `message` (Text, `translate=True`) — pesan peringatan bilingual yang ditampilkan ke user.

### `res.config.settings`
- `blocking_transaction_order` (Boolean → config_parameter `post_margin_sale.blocking_transaction_order`).

### `wizard.margin.product`
- `product_template_ids`/`product_ids` (Many2many, salah satu dipakai tergantung `active_model`),
  `is_product` (Boolean, compute), `margin` (Float).

## 4. Business Workflow / State Transition

### Konfirmasi Sale Order
- `[BSL-001]` `[MATCH]` (ref: 18-19/BSL-001) Kalau `is_rental_order_installed_true` → langsung
  `super().action_confirm()`, TIDAK ADA pengecekan margin sama sekali.
- `[BSL-002]` `[MATCH]` (ref: 18-19/BSL-002) Kalau bukan rental: `check_product_price()` mengumpulkan
  semua produk di `order_line` yang `price_unit < minimum_sale_price`. Kalau kosong → langsung
  `super().action_confirm()`.
- `[BSL-003]` `[MATCH]` (ref: 18-19/BSL-003) Kalau ada line melanggar DAN context `skip_check_price`
  tidak di-set: baca config `post_margin_sale.blocking_transaction_order`.
  - Blocking `True` → `raise ValidationError` (pesan bilingual, lihat `BSL-006`) — order TIDAK
    terkonfirmasi.
  - Blocking `False` → buat `sale.confirmation.wizard` (`message` = versi bilingual sesuai bahasa
    user), return `ir.actions.act_window` modal (`target='new'`) — order **belum** terkonfirmasi,
    menunggu keputusan user di wizard.
- `[BSL-004]` `[MATCH]` (ref: 18-19/BSL-004) Kalau context `skip_check_price=True` (dikirim wizard
  saat user memilih lanjut) → langsung `super().action_confirm()`, TIDAK mengecek ulang margin
  (mencegah rekursi tak berujung).

### Wizard konfirmasi
- `[BSL-005]` `[MATCH]` (ref: 18-19/BSL-005) `action_confirm()` wizard: browse `sale.order` dari
  `active_id`/`active_model` context (dinamis, dibaca via `self.env.context.get(...)`, lihat §7),
  panggil `.with_context(skip_check_price=True).action_confirm()` — order akhirnya terkonfirmasi.
  Tombol "Cancel" tidak melakukan apapun ke sale order (murni menutup dialog, `special="cancel"`).

## 5. Server-Side Logic dengan Side Effect

- `[BSL-006]` `[MATCH][DIWARISI-SOURCE]` (ref: 18-19/BSL-006) `detect_user_language()` — HANYA
  membedakan prefix `fr` (kembalikan `'French'`) vs SEMUA bahasa lain (`'Other'`) — bukan mekanisme
  `.po` translasi standar Odoo, generasi string manual bilingual EN/FR.
- `[BSL-007]` `[MATCH][RESOLVED — ref: 18-19/BSL-007, 17-18/MF-21]` **Mekanisme bilingual
  `action_confirm()` dikonfirmasi ULANG di kode 19.0/20.0 aktual saat ini (grep penuh, sesi ini):**
  baik cabang blocking maupun cabang wizard memilih `message`/`message_Fr` (string plain, dibuat
  manual) sesuai `detect_user_language()` — 0 match untuk `fr_FR`/`with_context(lang=` di seluruh
  modul. Fix lama ini tetap dipertahankan identik, tidak ada regresi antara 18.0→19.0.
- `[BSL-008]` `[MATCH]` (ref: 18-19/BSL-008) `module_pos_margin_threshold` compute murni drives
  `invisible=` view — tidak ada side effect lain.
- `[BSL-009]` `[GAP][DIWARISI-SOURCE][KEPUTUSAN SUDAH ADA — jangan diperbaiki]` (ref: 18-19/BSL-009,
  17-18/MF-06, `doc-dev/backfill/FINDINGS.md` F-05) `action_confirm()` membaca
  `self.is_rental_order_installed_true`/`self.order_line` (via `check_product_price()`) TANPA
  `for order in self:` — asumsi singleton.
  - **Spec lama (17-18/18-19):** "kalau Odoo core memanggil override ini untuk banyak order
    sekaligus (batch confirm), logic ini hanya akan mengevaluasi record PERTAMA di `self`" —
    dideskripsikan sebagai kegagalan validasi yang SENYAP (silent) untuk order ke-2 dst.
  - **Kode aktual + bukti eksekusi nyata (`doc-dev/backfill/FINDINGS.md` F-05, Docker Odoo 17.0,
    2026-07-31):** membaca field non-relasional (`Boolean`) pada recordset `sale.order` yang berisi
    LEBIH DARI SATU record langsung me-raise `ValueError: Expected singleton: sale.order(id1, id2,
    ...)` — BUKAN senyap, ini CRASH TOTAL untuk seluruh batch (bukan cuma order ke-2 dst).
    Direproduksi 2× secara independen: (1) test buatan sendiri
    (`tests/test_action_confirm.py::test_action_confirm_BATCH_MULTI_ORDER_F05`, masih ada di modul
    ini saat ini, dibuat lewat proses `doc-dev-backfill`); (2) TIDAK SENGAJA — demo data BAWAAN
    Odoo core sendiri (`sale_stock/data/sale_order_demo.xml`) memanggil `action_confirm()` pada 4
    order sekaligus dan crash dengan error identik saat modul ini diinstall.
  - **Dampak:** Tinggi, TERKONFIRMASI (bukan lagi hipotesis) — batch-confirm quotation (fitur
    native Odoo, dipakai bahkan oleh demo data resmi Odoo core) akan GAGAL TOTAL untuk SEMUA order
    yang dipilih, bukan cuma yang harganya bermasalah.
  - **Keputusan pemilik modul:** ✅ Sudah dijawab (2026-08-27, project 18.0→19.0): **dipertahankan,
    tidak diperbaiki**. Keputusan ini TIDAK berubah oleh koreksi deskripsi mekanisme di atas — hanya
    presisi cara bug ini bermanifestasi yang dikoreksi (crash, bukan senyap).
- `[BSL-010]` `[MATCH][DIWARISI-SOURCE]` (ref: 18-19/BSL-010, 17-18/MF-05) `ProductProduct._register_hook()`
  (dijalankan setiap registry rebuild, TIDAK hanya saat install): kalau `pos_margin_threshold`
  terinstall → mengosongkan membership `group_sale_margin_action` untuk SEMUA user
  (`group.user_ids = [(5, 0, 0)]`); kalau tidak → memberikan grup itu ke SEMUA user internal
  (`group.user_ids = [(6, 0, internal_users.ids)]`). Field API `user_ids` (bukan `users`, sudah
  rename mekanis `MF-17` dari project 18.0→19.0) — perilaku tidak berubah dari rename ini. Mutasi
  paksa, bukan kondisi deklaratif — perubahan manual admin ke membership grup ini bisa ter-reset
  diam-diam di reload registry berikutnya.
- `[BSL-011]` `[NO-SPEC]` (baru — instance singleton-assumption KEDUA, belum pernah didokumentasikan)
  `SaleOrder._compute_is_rental_order_installed()` sudah punya `for record in self:`, TAPI kondisi
  di dalam loop membaca `hasattr(self, 'is_rental_order') and self.is_rental_order` — memakai
  variabel `self` (recordset PENUH, bukan `record`, walau nama loop variable-nya `record`). Kalau
  method compute ini pernah dipanggil Odoo dengan `self` berisi >1 `sale.order` (mis. batch-confirm
  MEMICU compute field ini lebih dulu sebelum baris `action_confirm()` sendiri yang dibahas
  `BSL-009` sempat jalan), baris `self.is_rental_order` akan raise `ValueError: Expected singleton`
  DI SINI — bukan di `action_confirm()`. Externally observable symptom kemungkinan sama (crash
  `ValueError` saat batch-confirm, sudah tercakup `BSL-009`/`F-05`), tapi titik kegagalan
  sesungguhnya bisa jadi compute ini, bukan baris yang selama ini disebut di baseline lama. Tidak
  mengubah keputusan `MF-08` (tetap dipertahankan) — dicatat murni sebagai perincian baru dari baca
  kode langsung sesi ini.

## 6. Client-Side Behavior (Views, JS, Owl)

Tidak ada JS/Owl sama sekali (lihat `BSL-014`) — modul ini murni server-side + view XML.

- `[BSL-012]` `[MATCH]` (ref: 18-19/BSL-011) Form Sale Order: order line di bawah minimum diberi
  `decoration-danger`, KECUALI order adalah rental (`not parent.is_rental_order_installed_true`).
  `minimum_sale_price` ditambahkan sebagai `column_invisible` (dipakai decoration, tidak ditampilkan
  sebagai kolom terpisah). `is_rental_order_installed_true` ditambahkan `invisible="1"` sebelum
  `<sheet>` murni agar tersedia untuk ekspresi decoration.
- Form Product Template/Variant: field margin/minimum-price ditambahkan dengan guard
  `module_pos_margin_threshold` untuk mencegah field margin tampil dobel kalau kedua modul margin
  terinstall bersamaan; guard tambahan `product_variant_count > 1 and not is_product_variant` untuk
  produk multi-variant (lihat `BSL-019` untuk quirk terkait `position="replace"` di view yang sama).

## 7. Dependency Eksternal

### Eksplisit (manifest)
- `depends: ['base', 'product', 'sale', 'stock_account']`

### Implisit/Inferred
- **Rental (Enterprise, `is_rental_order`)** — via `hasattr()`, opsional/soft, dikecek per record di
  `_compute_is_rental_order_installed`. Dikonfirmasi masih ada persis nama field ini di
  `enterprise20/sale_renting/models/sale_order.py:95` (Odoo 20.0 Enterprise) — lihat `01a` §0/§2.
- `pos_margin_threshold` (custom sibling) — via `ir.module.module` lookup (`_register_hook()`,
  `_compute_module_pos_margin_threshold`) + kolisi `_name` `wizard.margin.product` (`BSL-015`).
- Pola akses context konsisten pakai `self.env.context.get(...)` di seluruh modul (wizard
  `sale_confirmation.py`, `wizard_margin_product.py`, `sale_order.py`) — TIDAK ADA lagi
  `self._context` (rename mekanis `MF-22` dari project 18.0→19.0, dikonfirmasi ulang bersih via
  grep sesi ini).

## 8. Quirk / Behavior Non-Obvious

- `[BSL-013]` `[MATCH][DIWARISI-SOURCE]` (ref: 18-19/BSL-012, FINDINGS.md MF-05, 17-18/MF-07)
  Manifest memuat KEDUA `views/product_template_views.xml` dan `views/products.xml`, dan KEDUANYA
  mendefinisikan XML-ID identik `product_template_inherit_sale_margin_threshold` dengan
  `inherit_id` BERBEDA (`product.product_template_only_form_view` vs
  `product.product_template_form_view`). Karena keduanya dimuat (urutan manifest `data:`:
  `product_template_views.xml` lalu `products.xml`), record yang dimuat KEDUA (`products.xml`)
  menimpa TOTAL record pertama — termasuk `inherit_id`-nya. Konsekuensi: kustomisasi yang dituju ke
  `product.product_template_only_form_view` tidak pernah benar-benar aktif; hanya kustomisasi ke
  `product.product_template_form_view` (via `products.xml`) yang jalan. Dikonfirmasi ulang di kode
  19.0/20.0 saat ini — struktur file identik dengan 18.0.
- `[BSL-014]` `[MATCH][DIWARISI-SOURCE]` (ref: 18-19/BSL-013, FINDINGS.md MF-06, 17-18/MF-08)
  Manifest deklarasikan `assets.sale_margin_threshold._assets_sale` → `static/src/**/*`, tapi
  folder `static/src/` TIDAK ADA di disk sama sekali (dikonfirmasi ulang `ls static/` sesi ini —
  hanya `static/description/*` untuk listing app). Glob kosong, tidak ada efek fungsional,
  prioritas Rendah.
- `[BSL-015]` `[MATCH][DIWARISI-SOURCE]` (ref: 18-19/BSL-014, FINDINGS.md MF-03, 17-18/MF-03)
  Kolisi `_name` `wizard.margin.product` dengan `pos_margin_threshold` — kedua modul mendefinisikan
  model ini byte-identik tanpa `_inherit`. Modul INI (`sale_margin_threshold`) yang selalu menang
  MRO (dikonfirmasi empiris project sebelumnya, independen urutan install). Detail lengkap di
  dokumen baseline `pos_margin_threshold`.
- `[BSL-016]` `[MATCH]` (ref: 18-19/BSL-015) `_compute_module_pos_margin_threshold` dideklarasikan
  dengan `@api.depends_context('uid')` walau compute-nya sendiri tidak benar-benar bergantung pada
  `uid` — nit efisiensi (cache invalidation per-user yang tidak perlu), dikonfirmasi TIDAK
  berdampak fungsional. Tidak perlu diperbaiki, murni catatan.
- `[BSL-017]` `[MATCH][DIWARISI-SOURCE]` (ref: FINDINGS.md MF-20, ditemukan Step 8 project
  18.0→19.0) `security/groups.xml` — `implied_ids` diisi `[(4, ref('base.module_category_hidden'))]`,
  tapi `res.groups.implied_ids` adalah Many2many ke `res.groups` (grup lain), sedangkan
  `base.module_category_hidden` adalah record `ir.module.category` (kategori) — kemungkinan besar
  salah tempel dari `category_id` (field yang benar-benar dipakai untuk menyembunyikan grup dari UI
  Settings). Dikonfirmasi ulang identik di kode 19.0/20.0 saat ini. **Masih terbuka, belum ada
  keputusan dev** (dibiarkan dulu per keputusan 2026-08-27, belum final).
- `[BSL-018]` `[MATCH][DIWARISI-SOURCE]` (ref: FINDINGS.md MF-21, ditemukan Step 8 project
  18.0→19.0) `product.product._compute_warning()` (`is_less_minimum_sale`) TIDAK didekorasi
  `@api.depends(...)` — ORM tidak tahu harus invalidasi/recompute field ini saat
  `lst_price`/`minimum_sale_price` berubah, nilai cache bisa basi dalam transaksi/request yang
  sama. Dikonfirmasi ulang identik di kode 19.0/20.0 saat ini (`models/product.py:82-84`). **Masih
  terbuka, belum ada keputusan dev.**
- `[BSL-019]` `[NO-SPEC]` (baru — pola identik `FINDINGS.md MF-24` sibling module, belum pernah
  dicatat untuk modul INI) `list_price`/`lst_price` di-`position="replace"` (bukan
  `position="attributes"`) di 3 titik: `views/product_template_views.xml` (target
  `product_template_only_form_view`, tidak pernah aktif — lihat `BSL-013`), `views/products.xml`
  (target `product_template_form_view`, YANG AKTIF), dan implisit untuk `lst_price` di form
  `product.product` (`product_variant_easy_edit_view`, lewat `views/products.xml`). Dicek langsung
  ke core `odoo20/addons/product/views/product_views.xml` (`product_template_form_view`, baris
  ~124-129): field `list_price` core di form itu punya
  `options="{'currency_field': 'currency_id', 'field_digits': True}"` — atribut ini HILANG TOTAL
  karena `position="replace"` modul ini hanya menulis ulang `decoration-danger`+`widget="monetary"`
  tanpa `options`. Konsekuensi: rounding digit (`field_digits`) dan resolusi mata uang eksplisit
  ikut hilang dari field ini di form yang aktif. Sama seperti `MF-24` (sibling), ini bukan gap
  migrasi (sudah begini sejak sebelum 19.0), tapi belum pernah tercatat untuk modul ini sampai
  sesi ini.
- Cruft non-fungsional yang ditemukan sesi ini (tidak butuh keputusan): `googleaeed8a7b9ec156e7.html`
  (Google site-verification, 1 baris) dan `LISEZMOI.md` (README bahasa Prancis) ada di root modul —
  tidak didaftarkan di manifest `data`/apapun, tidak dimuat Odoo, murni file tambahan di disk.
- `controllers/controllers.py` — seluruh isi di-comment, scaffold mati sejak awal (sama seperti
  sibling module).

---

## Cara Pakai

Sama seperti dokumen `01b_BASELINE_SPEC.md` project 18.0→19.0 — ID `BSL-NNN` di sini adalah
penomoran BARU khusus modul ini untuk project 19.0→20.0 (mulai dari `BSL-001`), dirujuk balik ke
`(ref: 18-19/BSL-NNN)`/`(ref: FINDINGS.md MF-NNN)`/`(ref: doc-dev/backfill/FINDINGS.md F-NN)` untuk
ketertelusuran ke dokumen/eksekusi sebelumnya.
