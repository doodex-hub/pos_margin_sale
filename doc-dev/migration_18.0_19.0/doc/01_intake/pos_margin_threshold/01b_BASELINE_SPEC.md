# Baseline Spec — pos_margin_threshold

**Step:** 1 — Intake & Scope (pelengkap `01a_MIGRATION_INTAKE.md`)
**Tujuan:** dokumentasikan APA yang modul lakukan (behavior as-is) di 18.0 — bukan bagaimana
diimplementasikan. Sumber kebenaran: kode 18.0 yang berjalan di branch `migration/18.0` (identik
dengan working tree `migration/19.0_target` saat ini, belum ada perubahan kode apapun).
**Tanggal:** 2026-08-26
**Sumber:** Direkonsiliasi dari `doc-dev/migration_17.0_18.0/doc/01_intake/pos_margin_threshold/01b_BASELINE_SPEC.md`
(baseline 18.0 hasil project migrasi 17.0→18.0 SEBELUMNYA, sudah lulus 11 step + UAT sign-off) +
cross-check langsung ke kode 18.0 aktual + `doc-dev/migration_17.0_18.0/doc/FINDINGS.md` (menangkap
perubahan yang terjadi selama migrasi 17→18 tapi belum tercermin di teks BSL dokumen lama).

> Ini **sumber kebenaran** untuk `05a_MIGRATION_ACCEPTANCE_CRITERIA.md` dan semua testing (step 9,
> 10, 11) — BUKAN `03_MIGRATION_SPEC.md`.
>
> **Provenance di dokumen ini merujuk ke DUA generasi dokumen lama sekaligus:** `BSL-NNN` dari
> `01b_BASELINE_SPEC.md` project 17.0→18.0 (ditandai `(ref: 17-18/BSL-NNN)`), dan `MF-NNN` dari
> `FINDINGS.md` project yang sama (ditandai `(ref: 17-18/MF-NNN)`) — supaya tidak ambigu dengan ID
> `BSL-NNN`/`MF-NNN` baru yang dipakai di dokumen 18.0→19.0 ini sendiri.

---

## Ringkasan untuk Review — Perlu Konfirmasi User

**Tally provenance:** 15 klaim `[MATCH]`, 0 `[GAP]`, 3 `[NO-SPEC]` (baru, ditemukan langsung dari
kode saat menyusun dokumen ini — bukan bug, cuma belum pernah dicatat granular sebelumnya).

- `[BSL-011]` `[DIWARISI-SOURCE]` — margin (`margin_sale`) di level *variant* (`product.product`)
  TIDAK PERNAH bisa berbeda dari template-nya — inverse-nya menulis balik ke `product_tmpl_id`. Field
  ada di level variant tapi secara desain selalu tersinkron ke template. Harus dipertahankan identik.
- `[BSL-012]` `[DIWARISI-SOURCE]` — `blocking_transaction_order` (di `res.config.settings`) ada tapi
  TIDAK dibaca modul ini sama sekali — cuma berefek kalau `sale_margin_threshold` juga terinstall.
  Bukan bug modul ini, harus dipertahankan.
- `[BSL-013]` `[DIWARISI-SOURCE]` `[PERLU-KEPUTUSAN]` — `wizard.margin.product` (`_name`, bukan
  `_inherit`) byte-identik dengan wizard `sale_margin_threshold`. Kalau kedua modul terinstall,
  `sale_margin_threshold` SELALU menang MRO (dikonfirmasi empiris 2026-08-26, independen urutan
  install) — class modul ini hilang total dari registry. Risiko silent-override kalau salah satu
  diubah sendirian.
- `[BSL-014]` `[DIWARISI-SOURCE]` — `views/product_template_views.xml` ada di disk, sengaja TIDAK
  didaftarkan di manifest `data:` (dead file), duplikat XML-ID dengan record aktif di
  `views/products.xml` yang target `inherit_id`-nya beda. Harus tetap mati.
- **Typo `action_assing_margin`** (method Python + nama field XML) — bukan `assign` — harus
  dipertahankan byte-identik karena view mereferensikan nama method ini langsung.
- **Area risiko tertinggi untuk Step 2/6 (19.0):** seluruh integrasi JS/Owl (`static/src/store/`)
  adalah *patch* terhadap arsitektur inti `point_of_sale` yang TERBUKTI berubah total sekali (17→18:
  rename kelas `Order/Orderline/Product`→`PosOrder/PosOrderline/ProductProduct`, `Order.pay()`
  dipindah jadi `PosStore.pay()`, popup service dihapus total, `_load_pos_data_fields` API baru, Owl
  props-shape validation ketat, xpath `orderline.xml` butuh descendant-selector). Tidak ada asumsi
  "method-level API sudah terbukti stabil 17→18, jadi otomatis stabil lagi 18→19" — wajib verifikasi
  ulang langsung ke `native-target` 19.0 di Step 2, bukan diwariskan dari kesimpulan migrasi
  sebelumnya.
- `[NO-SPEC]` baru (`BSL-016`/`017`/`018` di bawah) — 3 klaim yang genuinely belum pernah
  didokumentasikan granular sebelumnya (bukan gap/bug, cuma perincian baru dari baca kode langsung
  untuk dokumen ini): urutan resolusi `get_minimum_sale_price()`/`_with_tax()` getter POS, pola dual
  wizard entry-point (Template vs Variant list), dan `pos.session` yang sekarang jadi file kosong
  murni dokumentasi.

---

## 1. Tujuan Modul

Menegakkan margin minimum penjualan di Point of Sale. Setiap kategori produk punya `margin_sale`
default (%); tiap produk/varian mewarisi ini (bisa di-override), dari situ dihitung
`minimum_sale_price` dan `minimum_sale_price_with_tax`. Saat kasir memproses pembayaran di POS,
sistem mengecek tiap baris order: kalau harga jual aktual di bawah harga minimum (termasuk pajak),
sistem menampilkan peringatan — baik hanya konfirmasi (kasir bisa lanjut) atau blocking total
(pembayaran tidak bisa diproses), tergantung setting `blocking_transaction_pos`. Modul juga
menyediakan wizard bulk-assign margin dari list view Product Template/Product Variant.

## 2. Model & Tanggung Jawab

| Model | Tanggung Jawab |
|---|---|
| `product.category` (extend) | Default `margin_sale` (%) yang diwarisi produk di kategori ini. |
| `product.template` (extend) | `margin_sale`/`minimum_sale_price`/`minimum_sale_price_with_tax` di level template; aksi bulk-assign margin. |
| `product.product` (extend) | Sama seperti template, tapi inverse-nya menulis balik ke template (lihat `BSL-011`). |
| `pos.config` (extend) | Flag `is_blocked_warning`, dibaca dari config parameter, dikonsumsi JS POS. |
| `res.config.settings` (extend) | Expose `blocking_transaction_pos` (dipakai) dan `blocking_transaction_order` (dideklarasikan, tidak dipakai modul ini — lihat `BSL-012`). |
| `pos.session` (extend) | **Kosong** — sekarang cuma comment dokumentasi (lihat `BSL-009` di §5). |
| `wizard.margin.product` (baru, `_name`) | Wizard bulk-assign margin dari list Product Template/Variant. |

## 3. Field dengan Makna Bisnis

### `product.category`
- `margin_sale` (Float) — margin default (%) yang diwarisi semua produk di kategori ini.

### `product.template`
- `margin_sale` (Float, `tracking=True`, compute+store, readonly=False) — margin (%); default dari
  `categ_id.margin_sale`, bisa ditimpa manual per-template (persisten, tidak revert sampai dependency
  compute-nya berubah).
- `minimum_sale_price` (Float, compute+inverse+store) — `standard_price * (1 + margin_sale/100)`.
- `minimum_sale_price_with_tax` (Float, compute+store, **tanpa inverse**) — `minimum_sale_price * (1
  + sum(taxes_id.amount)/100)`.

### `product.product`
- `margin_sale`, `minimum_sale_price` — field yang sama, tapi computed independen dari
  `standard_price` variant sendiri; inverse `margin_sale` menulis balik ke `product_tmpl_id` (lihat
  `BSL-011`).
- `is_less_minimum_sale` (Boolean, compute, tidak stored) — `lst_price < minimum_sale_price`, dipakai
  untuk decoration merah di form.

### `pos.config`
- `is_blocked_warning` (Boolean, compute, tidak stored) — dibaca dari `ir.config_parameter`
  `post_margin_sale.blocking_transaction_pos` (sudo).

### `res.config.settings`
- `blocking_transaction_pos` (Boolean → config_parameter) — di-expose di settings view, dikonsumsi
  `pos.config` + JS.
- `blocking_transaction_order` (Boolean → config_parameter) — dideklarasikan, TIDAK di-expose di
  settings view modul ini, TIDAK dibaca kode modul ini (lihat `BSL-012`).

### `wizard.margin.product`
- `product_template_ids` (Many2many `product.template`), `product_ids` (Many2many `product.product`)
  — salah satu terisi tergantung konteks (lihat `is_product`).
- `is_product` (Boolean, compute) — `True` kalau dibuka dari context `active_model ==
  'product.template'`.
- `margin` (Float) — input margin baru yang di-bulk-assign.

## 4. Business Workflow / State Transition

### Bulk-assign margin (wizard)
- `[BSL-001]` `[MATCH]` (ref: 17-18/BSL-002) Dari list view Product Template ATAU Product Variant,
  action server memanggil `action_assign_margin()` (di masing-masing model), membuka
  `wizard.margin.product` dengan `product_template_ids`/`product_ids` pre-populated dari record yang
  dipilih (`(6,0,ids)`).
- `[BSL-002]` `[MATCH]` (ref: 17-18/BSL-002) `is_product` compute dari `active_model` context —
  menentukan field mana (`product_template_ids` vs `product_ids`) yang ditampilkan di form wizard.
- `[BSL-003]` `[MATCH]` (ref: 17-18/BSL-002) Tombol "Assign" memanggil `action_assing_margin()`
  (typo dipertahankan) — menulis `margin` wizard ke `margin_sale` SETIAP record terpilih, tanpa
  konfirmasi tambahan, tanpa syarat. Tombol "Cancel" tidak mengubah apapun.

### Payment-time enforcement (POS)
- `[BSL-004]` `[MATCH]` (ref: 17-18/BSL-003, 17-18/MF-13, 17-18/MF-15, 17-18/MF-16) Saat kasir klik
  tombol "Pay", `PosStore.prototype.pay()` (patch) mengecek SEMUA orderline order saat ini, memfilter
  yang `unit_display_price < minimum_sale_price_with_tax`.
- `[BSL-005]` `[MATCH]` (ref: 17-18/BSL-003) Kalau tidak ada line yang melanggar → langsung
  `super.pay(...)`, tidak ada dialog apapun.
- `[BSL-006]` `[MATCH]` (ref: 17-18/BSL-003, 17-18/MF-13) Kalau ada line melanggar DAN
  `config.is_blocked_warning === false` (default) → dialog konfirmasi ("Price unit less than minimum
  price" / "Some products are below the minimum price. Proceed to payment?") muncul via `ask()`
  (`@point_of_sale/app/store/make_awaitable_dialog`). User confirm → lanjut `super.pay(...)`. User
  decline → `return`, pembayaran dibatalkan, kasir tetap di ProductScreen.
- `[BSL-007]` `[MATCH]` (ref: 17-18/BSL-003, 17-18/MF-13) Kalau ada line melanggar DAN
  `config.is_blocked_warning === true` → `AlertDialog` muncul ("Price unit less than minimum price" /
  "Some products are below the minimum price. Please check !"), `return` TANPA opsi lanjut sama
  sekali — pembayaran diblokir total, tidak ada jalan proceed dari dialog ini.

## 5. Server-Side Logic dengan Side Effect

### `product.template` / `product.product`
- `[BSL-008]` `[MATCH]` (ref: 17-18/BSL-004) `minimum_sale_price` inverse: menghitung ulang
  `margin_sale` dari harga yang di-set manual; ada guard eksplisit `standard_price == 0` → set
  `margin_sale = 0.0` (cegah div-by-zero).
- `[BSL-009]` `[NO-SPEC]` (baru — perincian, bukan bug) `product.product._load_pos_data_fields()`
  (override `@api.model`) memanggil `super()` lalu menambahkan `['minimum_sale_price',
  'minimum_sale_price_with_tax']` ke daftar field yang dikirim ke frontend POS. Ini adalah mekanisme
  PENGGANTI 18.0 untuk apa yang dulu (17.0) jadi override `pos.session._loader_params_product_product`
  — file `models/pos_session.py` sekarang **kosong murni komentar dokumentasi** yang menjelaskan
  penghapusan ini secara eksplisit (ref: 17-18/MF-18).
- `[BSL-010]` `[MATCH][DIWARISI-SOURCE]` (ref: 17-18/BSL-011, 17-18/MF-01) `product.product`
  `margin_sale` inverse (`_set_product_margin_sale`) menulis balik `rec.product_tmpl_id.write({'margin_sale':
  rec.margin_sale})` — bukan ke variant itu sendiri. **Konsekuensi:** margin per-variant TIDAK PERNAH
  bisa divergen dari template; field yang "kelihatan" per-variant di UI sebenarnya selalu tersinkron
  paksa ke template.

### Wizard
- `[BSL-011]` `[NO-SPEC]` (baru — perincian) Dua entry-point wizard (dari list Template vs list
  Variant) memanggil `action_assign_margin()` yang SAMA NAMANYA tapi didefinisikan terpisah di masing-
  masing model (`product.template.action_assign_margin` vs `product.product.action_assign_margin`)
  — bukan satu method di-share, dua implementasi paralel yang membedakan lewat context
  `active_model` yang di-set masing-masing `ir.actions.server`.

## 6. Client-Side Behavior (Views, JS, Owl)

### Backend
- `[BSL-012]` `[MATCH]` (ref: 17-18/BSL-010) Form Product Template/Variant: `list_price`/`lst_price`
  diberi `decoration-danger` (merah) kalau di bawah minimum; field `margin_sale`/`minimum_sale_price`/
  `minimum_sale_price_with_tax` ditambahkan dengan `invisible=` guard untuk produk multi-variant (agar
  tidak duplikat tampilan).
- `[BSL-013]` `[MATCH]` (ref: 17-18/BSL-010) Form Product Category: `margin_sale` ditambahkan sebelum
  `property_cost_method` (inherit `stock_account.view_category_property_form_stock`).
- Komponen Owl (patch, bukan komponen baru): `patch(ProductProduct.prototype)` (getter
  `get_minimum_sale_price()`/`_with_tax()`), `patch(PosOrderline.prototype)` (`getDisplayData()`
  extend — sudah `super()`-aware, resolusi `17-18/MF-11`), `patch(Orderline.props.line.shape)`
  (deklarasi 3 prop key baru, fix `17-18/MF-19`), `patch(PosStore.prototype.pay())` (§4 di atas).
- `[BSL-014]` `[MATCH]` (ref: 17-18/BSL-009, 17-18/MF-20) `orderline.xml` (`t-inherit
  point_of_sale.Orderline`): tambah class `text-danger` + baris peringatan teks kalau
  `line.isLessMinimumSalePrice` — xpath descendant (`//ul[...]`), BUKAN direct-child, karena 18.0
  menambah `<div>` wrapper (fix `17-18/MF-20`).

### Test coverage (Tour)
- Dua Tour test ada: `pos_margin_threshold_below_minimum_confirm_tour` (jalur confirm, sampai
  receipt) dan `pos_margin_threshold_below_minimum_blocked_tour` (jalur blocking, `AlertDialog`
  menghentikan, tetap di ProductScreen).
- `[BSL-015]` `[NO-SPEC][DIWARISI-SOURCE]` (ref: 17-18/09_DEV_TESTING, 17-18/10_BUSINESS_FLOW) Gap
  test yang masih TERBUKA (belum ditutup project 17→18, carry-forward): AC-02-03 (tidak ada popup
  sama sekali kalau semua line di atas minimum — belum ada test otomatis) dan AC-02-04 (assert teks/
  warna warning orderline secara terpisah, bukan cuma "tidak crash"). Kedua butuh sesi POS register
  penuh. **Keputusan user diperlukan:** ditutup di project 18.0→19.0 ini, atau tetap dilewati?

## 7. Dependency Eksternal

### Eksplisit (manifest)
- `depends: ['base', 'point_of_sale', 'product', 'stock_account']`

### Implisit/Inferred
- `sale_margin_threshold` (custom, sibling) — kolisi `_name` `wizard.margin.product` (`BSL-013`
  di §Ringkasan / lihat §8).
- XML-ID target inherit: `stock_account.view_category_property_form_stock`,
  `product.product_template_form_view`, `product.product_template_only_form_view` (via dead file),
  `product.product_variant_easy_edit_view`.
- JS import path (semua internal `point_of_sale`, prioritas riset Step 2): path model POS
  (`@point_of_sale/app/models/...` di 18.0, WAJIB dicek ulang ke 19.0), `PosStore`
  (`@point_of_sale/app/store/pos_store`), dialog service (`@web/core/confirmation_dialog/confirmation_dialog`,
  `@point_of_sale/app/store/make_awaitable_dialog`).

## 8. Quirk / Behavior Non-Obvious

- `[BSL-016]` `[MATCH][DIWARISI-SOURCE][PERLU-KEPUTUSAN]` (ref: 17-18/BSL-013, 17-18/MF-03) Model
  `wizard.margin.product` (`_name`, bukan `_inherit`) didefinisikan BYTE-IDENTIK di modul ini dan di
  `sale_margin_threshold`. Kalau keduanya terinstall, Odoo meng-*merge* jadi satu model, dan
  `__mro__` SELALU menghasilkan class `sale_margin_threshold` — dikonfirmasi empiris 2026-08-26
  (project 17→18, Step 9): dites DUA urutan install (`-i pos_margin_threshold,sale_margin_threshold`
  dan kebalikannya), hasil identik di kedua kasus. Class modul INI (`pos_margin_threshold`) hilang
  total dari registry, bukan cuma "kalah prioritas". **Risiko:** kalau salah satu wizard diubah
  sendirian di 19.0 tanpa sinkron manual ke yang lain, perubahan itu silent — tidak error, tapi salah
  satu modul efektif tidak punya wizard sendiri lagi.
- `[BSL-017]` `[MATCH][DIWARISI-SOURCE]` (ref: 17-18/BSL-012, 17-18/MF-02) `blocking_transaction_order`
  dideklarasikan di `res.config.settings` modul ini tapi TIDAK PERNAH dibaca oleh kode modul ini
  sendiri — field ini hanya bermakna kalau `sale_margin_threshold` juga terinstall (field itu punya
  makna di modul sana). Bukan bug, tapi field yang "kelihatan aktif" di UI settings modul ini padahal
  efeknya nol tanpa modul sibling.
- `[BSL-018]` `[MATCH][DIWARISI-SOURCE]` (ref: 17-18/BSL-014, 17-18/MF-04) `views/product_template_views.xml`
  ada di disk (`inherit_id="product.product_template_only_form_view"`, XML-ID
  `product_template_inherit_pos_margin_threshold`), TIDAK terdaftar di manifest `data:` — dead file
  yang sengaja dipertahankan mati (mencegah duplikat XML-ID dengan `views/products.xml`). Kalau nanti
  seseorang menambah file ini ke `data:` tanpa rename ID, akan konflik.
- Typo `action_assing_margin` (bukan "assign") — di method Python (`wizard/wizard_margin_product.py`)
  DAN di atribut `name=` XML (`wizard/wizard_margin_product.xml`) — harus tetap identik, view
  mereferensikan nama method secara literal.
- `controllers/controllers.py` — seluruh isi di-comment, scaffold mati sejak awal (bukan regresi
  migrasi manapun), `controllers/__init__.py` tetap mengimpornya (no-op, tidak error).

---

## Cara Pakai

Lihat `migration-tool/templates/01b_BASELINE_SPEC.md` §Cara Pakai untuk aturan penomoran/provenance
lengkap. Ringkas: ID `BSL-NNN` di dokumen ini adalah penomoran BARU (mulai 001) khusus project
18.0→19.0 — TIDAK sama dengan `BSL-NNN` di dokumen 17.0→18.0 (dirujuk eksplisit sebagai
`(ref: 17-18/BSL-NNN)` di tiap klaim yang diwarisi, supaya tidak ambigu).
