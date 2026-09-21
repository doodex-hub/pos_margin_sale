# Baseline Spec — pos_margin_threshold

**Step:** 1 — Intake & Scope (pelengkap `01a_MIGRATION_INTAKE.md`)
**Tujuan:** dokumentasikan APA yang modul lakukan (behavior as-is) di 19.0 — bukan bagaimana
diimplementasikan. Sumber kebenaran: kode 19.0 yang berjalan di branch `migration/19.0` (identik
dengan working tree `migration/20.0` saat ini, belum ada perubahan kode apapun untuk migrasi ini).
**Tanggal:** 2026-09-21
**Sumber:** Direkonsiliasi dari `doc-dev/migration_18.0_19.0/doc/01_intake/pos_margin_threshold/01b_BASELINE_SPEC.md`
(baseline 19.0 hasil project migrasi 18.0→19.0 SEBELUMNYA, sudah lulus 10 dari 11 step — UAT sign-off
menunggu eksekusi manusia) + cross-check langsung ke kode 19.0 aktual (baca semua file modul:
`__manifest__.py`, `models/`, `wizard/`, `views/`, `static/src/`, `static/tests/`, `tests/`,
`security/`, `demo/`) + `doc-dev/migration_18.0_19.0/doc/FINDINGS.md` (menangkap perubahan yang
terjadi selama migrasi 18→19 tapi belum tercermin di teks BSL dokumen lama) + `FINDINGS.md` project
ini sendiri (`doc-dev/migration_19.0_20.0/doc/FINDINGS.md`, sudah membawa masuk `MF-08`/`20`/`21`/
`23`/`24` dari project sebelumnya).

> Ini **sumber kebenaran** untuk `05a_MIGRATION_ACCEPTANCE_CRITERIA.md` dan semua testing (step 9,
> 10, 11) — BUKAN `03_MIGRATION_SPEC.md`.
>
> **Provenance di dokumen ini merujuk ke DUA sumber lama sekaligus:** `BSL-NNN` dari
> `01b_BASELINE_SPEC.md` project 18.0→19.0 (ditandai `(ref: 18.0→19.0 BSL-NNN)`), dan `MF-NNN` dari
> `FINDINGS.md` (ditandai `(ref: FINDINGS.md MF-NNN)`, tanpa perlu bedakan versi project karena
> `FINDINGS.md` project ini sendiri sudah mengonsolidasi ID dari project sebelumnya) — supaya tidak
> ambigu dengan `BSL-NNN` baru yang dipakai di dokumen 19.0→20.0 ini sendiri (dimulai lagi dari 001).
> **Penting:** tag provenance (`[MATCH]`/`[GAP]`/`[NO-SPEC]`) di dokumen ini dinilai ulang terhadap
> dokumen 18.0→19.0 SEBAGAI "spec lama" — bukan sekadar disalin tag aslinya. Beberapa klaim yang di
> dokumen 18.0→19.0 sendiri berlabel `[NO-SPEC]` (karena saat itu belum ada dokumen manapun yang
> membahasnya) menjadi `[MATCH]` di sini, karena SEKARANG dokumen 18.0→19.0 itu sendiri berperan
> sebagai "spec lama" yang membahasnya dan cocok dengan kode aktual.

---

## Ringkasan untuk Review — Perlu Konfirmasi User

**Tally provenance:** 19 klaim `[MATCH]`, 1 `[GAP]`, 2 `[NO-SPEC]` (22 klaim `BSL-NNN` total).

- **[GAP]** `BSL-017` — `FINDINGS.md` `MF-24` (dibawa dari project 18.0→19.0) hanya mencatat SATU
  lokasi pola `position="replace"` yang menghapus atribut core (`views/products.xml` baris ~62,
  field `list_price` di view Product Template). Kode aktual menunjukkan pola YANG SAMA juga di
  baris ~95 (field `lst_price` di `product_variant_easy_edit_view_margin_sale`) — tidak pernah
  disebut di `MF-24`. Dampak sama seperti `MF-24` asli (atribut core `options`/`optional`/
  `decoration-muted` pada `lst_price` di view variant-easy-edit ikut hilang), belum pernah dicatat
  sebelumnya. **Bukan gap migrasi** (pre-existing sejak sebelum 19.0), tapi scope `MF-24` yang
  tercatat perlu diperluas — tidak diedit di sini (di luar wewenang dua dokumen intake ini), cuma
  diberi jejak audit lewat `BSL-017` supaya Step 8 code review project ini tidak melewatkannya.
- **[NO-SPEC, baru]** `BSL-012` — field `margin_sale` (`product.product`) didekorasi DUA mekanisme
  sekaligus: `inverse="_set_product_margin_sale"` (klasik, dipanggil saat `write()`) DAN
  `@api.onchange('margin_sale')` pada method yang SAMA (dipanggil interaktif di form, sebelum save).
  Tidak pernah didokumentasikan granular di baseline manapun sebelumnya (17.0→18.0 maupun
  18.0→19.0) — bukan kontradiksi terhadap klaim lama (efek akhir tetap sama: menulis balik ke
  template, `BSL-010`), cuma perincian mekanisme yang belum pernah ditulis. Perlu diperhatikan di
  Step 2/6: kalau 20.0 mengubah semantik `@api.onchange` pada field yang juga punya `inverse=`,
  ini titik rawan.
- **[NO-SPEC, baru]** `BSL-016` — `orderline.xml` (patch `Orderline`) membangun `t-attf-class` dengan
  MENGGABUNGKAN kondisi modul ini (`isLessMinimumSalePrice` → `text-danger`) dengan kondisi milik
  core sendiri (`comboParent` → border kiri combo) di ekspresi yang sama — bukan cuma menambah class
  `text-danger` secara independen seperti yang digambarkan baseline 18.0→19.0 lama (`BSL-014` versi
  lama fokus ke penambahan class saja, tidak merinci penggabungan dengan class combo). Berarti kalau
  20.0 mengubah/menambah kondisi class combo lagi, patch modul ini WAJIB ikut menyesuaikan pola
  gabungan ini, bukan cuma menambah class terpisah.
- **Gap test yang masih terbuka, dua kali carry-forward (17.0→18.0, lalu 18.0→19.0), MASIH belum
  ditutup** (`BSL-018`, `[MATCH]`, ref `18.0→19.0 BSL-015`): AC-02-03 (tidak ada popup sama sekali
  kalau semua line di atas minimum) dan AC-02-04 (assert teks/warna warning orderline secara
  terpisah) — dua Tour test yang ada (`..._confirm_tour`/`..._blocked_tour`, sudah dieksekusi nyata
  di iterasi sebelumnya) TIDAK menutup dua skenario ini. **Keputusan user diperlukan:** ditutup di
  project 19.0→20.0 ini, atau tetap dilewati (sudah dilewati dua kali)?
- Quirk warisan (`[DIWARISI-SOURCE]`, harus dipertahankan, SEMUA dikonfirmasi ulang cocok dengan kode
  19.0 aktual sesi ini): `BSL-010` (`MF-01` — margin per-variant `product.product` tidak pernah bisa
  divergen dari template), `BSL-020` (`MF-03` — kolisi `_name` `wizard.margin.product` dengan
  `sale_margin_threshold`, `sale_margin_threshold` selalu menang `__mro__`), `BSL-021` (`MF-02` —
  `blocking_transaction_order` dideklarasikan tapi tidak pernah dibaca modul ini), `BSL-022`
  (`MF-04` — `views/product_template_views.xml` dead file, duplikat XML-ID), `BSL-019` (`MF-23` —
  `_compute_warning`/`is_less_minimum_sale` di `product.product` tanpa `@api.depends`, risiko cache
  stale). Typo `action_assing_margin` (bukan "assign") tetap identik di method Python + XML.
- **Catatan lintas-modul (bukan klaim modul ini):** `FINDINGS.md` `MF-08` (action_confirm singleton
  assumption) ada di `FINDINGS.md` project ini, TAPI itu kode `sale_margin_threshold` (modul
  sibling), bukan `pos_margin_threshold` — disebut di sini supaya tidak salah kira sudah tercakup,
  tidak menghasilkan klaim `BSL-NNN` di dokumen ini.

---

## 1. Tujuan Modul

Menegakkan margin minimum penjualan di Point of Sale. Setiap kategori produk punya `margin_sale`
default (%); tiap produk/varian mewarisi ini (bisa di-override), dari situ dihitung
`minimum_sale_price` dan `minimum_sale_price_with_tax`. Saat kasir memproses pembayaran di POS,
sistem mengecek tiap baris order: kalau harga jual aktual di bawah harga minimum (termasuk pajak),
sistem menampilkan peringatan — baik hanya konfirmasi (kasir bisa lanjut) atau blocking total
(pembayaran tidak bisa diproses), tergantung setting `blocking_transaction_pos`. Modul juga
menyediakan wizard bulk-assign margin dari list view Product Template/Product Variant. Fungsi ini
tidak berubah sejak 17.0 — hanya mekanisme implementasi JS/Owl POS yang sudah berubah dua kali
(17→18, 18→19) mengikuti perubahan arsitektur frontend `point_of_sale`.

## 2. Model & Tanggung Jawab

| Model | Tanggung Jawab |
|---|---|
| `product.category` (extend) | Default `margin_sale` (%) yang diwarisi produk di kategori ini. |
| `product.template` (extend) | `margin_sale`/`minimum_sale_price`/`minimum_sale_price_with_tax` di level template; aksi bulk-assign margin. |
| `product.product` (extend) | Sama seperti template, tapi inverse `margin_sale`-nya menulis balik ke template (lihat `BSL-010`); `is_less_minimum_sale` untuk decoration UI; `_load_pos_data_fields` menambah field ke payload POS. |
| `pos.config` (extend) | Flag `is_blocked_warning`, dibaca dari config parameter, dikonsumsi JS POS. |
| `res.config.settings` (extend) | Expose `blocking_transaction_pos` (dipakai) dan `blocking_transaction_order` (dideklarasikan, tidak dipakai modul ini — lihat `BSL-021`). |
| `pos.session` (extend) | **Kosong** — file cuma berisi komentar dokumentasi yang menjelaskan penghapusan hook lama `_loader_params_product_product` (lihat `BSL-009`). |
| `wizard.margin.product` (baru, `_name`) | Wizard bulk-assign margin dari list Product Template/Variant. **Kolisi model dengan `sale_margin_threshold`** (lihat `BSL-020`). |

## 3. Field dengan Makna Bisnis

### `product.category`
- `margin_sale` (Float) — margin default (%) yang diwarisi semua produk di kategori ini.

### `product.template`
- `margin_sale` (Float, `tracking=True`, compute `_compute_margin_sale` + `store=True`,
  `readonly=False`) — default dari `categ_id.margin_sale` (`@api.depends('categ_id.margin_sale')`),
  bisa ditimpa manual per-template (persisten via mekanisme compute+store, tidak revert sampai
  dependency compute-nya sendiri berubah).
- `minimum_sale_price` (Float, compute `_compute_minimum_sale_price` + inverse
  `_inverse_minimum_sale_price` + `store=True`, `readonly=False`) — `standard_price * (1 +
  margin_sale/100)` (`@api.depends('margin_sale', 'standard_price')`).
- `minimum_sale_price_with_tax` (Float, compute `_compute_minimum_sale_price_with_tax` +
  `store=True`, **tanpa inverse**) — `minimum_sale_price * (1 + sum(taxes_id.amount)/100)`
  (`@api.depends('margin_sale', 'minimum_sale_price', 'taxes_id')`).
- `action_assign_margin()` — server action, buka wizard `wizard.margin.product` dengan
  `product_template_ids` pre-populated.

### `product.product`
- `margin_sale` (Float, `tracking=True`, compute `_compute_margin_sale` (dari
  `product_tmpl_id.margin_sale`) + inverse `_set_product_margin_sale` + `store=True`,
  `readonly=False`) — **inverse-nya menulis balik ke `product_tmpl_id`, BUKAN ke variant sendiri**
  (`BSL-010`). Method inverse yang sama JUGA didekorasi `@api.onchange('margin_sale')` — dipanggil
  dua jalur: `write()` (inverse klasik) dan onchange interaktif di form (`BSL-012`, baru
  didokumentasikan sesi ini).
- `minimum_sale_price` (Float, compute `_compute_minimum_sale_price` + inverse
  `_inverse_minimum_sale_price` + `store=True`, `readonly=False`) — dihitung independen dari
  `standard_price` variant sendiri, formula sama seperti template.
- `is_less_minimum_sale` (Boolean, compute `_compute_warning`, **tidak stored, TANPA
  `@api.depends`**) — `lst_price < minimum_sale_price`, dipakai untuk decoration merah di form.
  Ketiadaan `@api.depends` adalah `MF-23` (`FINDINGS.md`), lihat `BSL-019`.
- `action_assign_margin()` — server action, buka wizard `wizard.margin.product` dengan
  `product_ids` pre-populated (implementasi terpisah dari versi template, lihat `BSL-011`).
- `_load_pos_data_fields(config_id)` — override `@api.model`, tambah `minimum_sale_price`/
  `minimum_sale_price_with_tax` ke daftar field yang dikirim ke frontend POS (lihat `BSL-009`).

### `pos.config`
- `is_blocked_warning` (Boolean, compute `_compute_blocked_warning`, tidak stored) — dibaca dari
  `ir.config_parameter` `post_margin_sale.blocking_transaction_pos` (sudo).

### `res.config.settings`
- `blocking_transaction_pos` (Boolean → config_parameter `post_margin_sale.blocking_transaction_pos`)
  — di-expose di settings view (`views/res_config_settings.xml`), dikonsumsi `pos.config` + JS POS.
- `blocking_transaction_order` (Boolean → config_parameter
  `post_margin_sale.blocking_transaction_order`) — dideklarasikan, TIDAK di-expose di settings view
  modul ini, TIDAK dibaca kode modul ini (`BSL-021`).

### `wizard.margin.product`
- `product_template_ids` (Many2many `product.template`), `product_ids` (Many2many `product.product`)
  — salah satu terisi tergantung konteks (lihat `is_product`).
- `is_product` (Boolean, compute `_compute_product_model`) — `True` kalau
  `self.env.context.get('active_model') == 'product.template'`.
- `margin` (Float) — input margin baru yang di-bulk-assign.

## 4. Business Workflow / State Transition

### Bulk-assign margin (wizard)
- `[BSL-001]` `[MATCH]` (ref: 18.0→19.0 BSL-001) Dari list view Product Template ATAU Product
  Variant, action server (`product_template_margin_sale_action_server`/
  `product_product_margin_sale_action_server`, `views/products.xml`) memanggil
  `action_assign_margin()` (di masing-masing model), membuka `wizard.margin.product` dengan
  `product_template_ids`/`product_ids` pre-populated dari record yang dipilih (`(6,0,ids)`), target
  `new` (dialog modal).
- `[BSL-002]` `[MATCH]` (ref: 18.0→19.0 BSL-002) `is_product` compute dari `active_model` context —
  menentukan field mana (`product_template_ids` vs `product_ids`) yang ditampilkan (`invisible=`) di
  form wizard.
- `[BSL-003]` `[MATCH]` (ref: 18.0→19.0 BSL-003) Tombol "Assign" memanggil `action_assing_margin()`
  (typo dipertahankan) — menulis `margin` wizard ke `margin_sale` SETIAP record terpilih (loop
  `for product in self.product_template_ids/product_ids`), tanpa konfirmasi tambahan, tanpa syarat.
  Tombol "Cancel" (`special="cancel"`) tidak mengubah apapun.

### Payment-time enforcement (POS)
- `[BSL-004]` `[MATCH]` (ref: 18.0→19.0 BSL-004) Saat kasir klik tombol "Pay",
  `PosStore.prototype.pay()` (patch, `static/src/store/pos_store.js`) mengambil order aktif
  (`this.getOrder()`), lines-nya (`currentOrder.getOrderlines()`), lalu memfilter line yang
  `line.displayPriceUnit < line.getProduct().get_minimum_sale_price_with_tax()`. **Mekanisme API
  method sudah berubah dari versi 18.0→19.0 lama** (dulu `unit_display_price`/`get_order`/
  `get_orderlines`/`get_product` snake_case — lihat `FINDINGS.md` `MF-13` project 18.0→19.0, sudah
  di-porting jadi camelCase `getOrder()`/`getOrderlines()`/`getProduct()`/`displayPriceUnit` di kode
  yang berjalan sekarang) — business rule-nya (line mana yang dianggap "melanggar") tidak berubah.
- `[BSL-005]` `[MATCH]` (ref: 18.0→19.0 BSL-005) Kalau tidak ada line yang melanggar (`lines.length
  === 0`) → langsung `super.pay(...arguments)`, tidak ada dialog apapun.
- `[BSL-006]` `[MATCH]` (ref: 18.0→19.0 BSL-006) Kalau ada line melanggar DAN `config.is_blocked_warning
  === false` (default) → dialog konfirmasi ("Price unit less than minimum price" / "Some products
  are below the minimum price. Proceed to payment?") muncul via `ask(this.env.services.dialog, {...})`
  (`@point_of_sale/app/utils/make_awaitable_dialog`). User confirm → lanjut `super.pay(...)`. User
  decline → `return`, pembayaran dibatalkan, kasir tetap di ProductScreen.
- `[BSL-007]` `[MATCH]` (ref: 18.0→19.0 BSL-007) Kalau ada line melanggar DAN
  `config.is_blocked_warning === true` → `AlertDialog` muncul (`@web/core/confirmation_dialog/confirmation_dialog`,
  title sama "Price unit less than minimum price", body "Some products are below the minimum price.
  Please check !"), `return` TANPA opsi lanjut sama sekali — pembayaran diblokir total, tidak ada
  jalan proceed dari dialog ini (dialog hanya punya tombol "Ok" default, dismiss tidak melanjutkan
  ke payment screen).

## 5. Server-Side Logic dengan Side Effect

### `product.template` / `product.product`
- `[BSL-008]` `[MATCH]` (ref: 18.0→19.0 BSL-008) `minimum_sale_price` inverse
  (`_inverse_minimum_sale_price`, identik di kedua model): menghitung ulang `margin_sale` dari harga
  yang di-set manual (`((minimum_sale_price / standard_price) - 1) * 100`); guard eksplisit
  `standard_price == 0`/falsy → set `margin_sale = 0.0` (cegah div-by-zero).
- `[BSL-009]` `[MATCH]` (ref: 18.0→19.0 BSL-009 — catatan: di dokumen 18.0→19.0 klaim ini sendiri
  ditandai `[NO-SPEC]` karena saat itu baru perincian baru; untuk dokumen ini, dokumen 18.0→19.0
  itulah "spec lama"-nya, dan cocok dengan kode aktual → `[MATCH]`) `product.product._load_pos_data_fields()`
  (override `@api.model`) memanggil `super()` lalu menambahkan `['minimum_sale_price',
  'minimum_sale_price_with_tax']` ke daftar field yang dikirim ke frontend POS. Ini mekanisme
  PENGGANTI 18.0+ untuk apa yang dulu (17.0) jadi override
  `pos.session._loader_params_product_product` — `models/pos_session.py` tetap **kosong murni
  komentar dokumentasi** yang menjelaskan penghapusan ini secara eksplisit.
- `[BSL-010]` `[MATCH][DIWARISI-SOURCE]` (ref: 18.0→19.0 BSL-010; FINDINGS.md MF-01) `product.product`
  `margin_sale` inverse (`_set_product_margin_sale`) menulis balik
  `rec.product_tmpl_id.write({'margin_sale': rec.margin_sale})` — bukan ke variant itu sendiri.
  **Konsekuensi:** margin per-variant TIDAK PERNAH bisa divergen dari template; field yang
  "kelihatan" per-variant di UI sebenarnya selalu tersinkron paksa ke template. Dikonfirmasi ulang
  cocok dengan kode `models/product.py` aktual sesi ini.
- `[BSL-011]` `[MATCH]` (ref: 18.0→19.0 BSL-011 — sama seperti `BSL-009`, dokumen 18.0→19.0 sendiri
  menandainya `[NO-SPEC]` tapi untuk dokumen ini itu "spec lama" yang cocok → `[MATCH]`) Dua
  entry-point wizard (dari list Template vs list Variant) memanggil `action_assign_margin()` yang
  SAMA NAMANYA tapi didefinisikan terpisah di masing-masing model
  (`product.template.action_assign_margin` vs `product.product.action_assign_margin`) — bukan satu
  method di-share, dua implementasi paralel yang membedakan lewat context `active_model` yang
  di-set masing-masing `ir.actions.server`.
- `[BSL-012]` `[NO-SPEC]` (ref: —, baru — perincian mekanisme, bukan bug) `product.product.margin_sale`
  didekorasi `inverse="_set_product_margin_sale"` DAN method yang sama juga didekorasi
  `@api.onchange('margin_sale')`. Ini berarti method ini terpanggil di DUA jalur berbeda: (1) inverse
  klasik saat `write()`/save, (2) onchange interaktif di form client-side SEBELUM save (setiap kali
  user mengubah nilai `margin_sale` di form). Efek akhirnya (menulis ke `product_tmpl_id`) sama di
  kedua jalur, tapi jalur onchange berarti write-back ke template bisa terpicu SEBELUM record variant
  sendiri disimpan. Tidak pernah didokumentasikan di baseline 17.0→18.0 maupun 18.0→19.0.

### Wizard
- (Lihat `BSL-011` di atas — dipindahkan ke bagian `product.template`/`product.product` karena
  sifatnya method di model produk, bukan wizard itu sendiri; penomoran dipertahankan seperti
  dokumen lama untuk konsistensi topik "dual entry-point".)

## 6. Client-Side Behavior (Views, JS, Owl)

### Backend (form views)
- `[BSL-013]` `[MATCH]` (ref: 18.0→19.0 BSL-012) Form Product Template
  (`product_template_inherit_pos_margin_threshold`, inherit
  `product.product_template_form_view`): `list_price` di-`position="replace"` dengan versi
  `decoration-danger="list_price < minimum_sale_price"` (lihat catatan `MF-24`/`BSL-017` di bawah
  soal hilangnya atribut core); field `margin_sale`/`minimum_sale_price`/
  `minimum_sale_price_with_tax` ditambahkan sebelum `categ_id`, dengan `invisible="product_variant_count
  > 1 and not is_product_variant"` untuk produk multi-variant (agar tidak duplikat tampilan dengan
  view variant). File dead `views/product_template_views.xml` (inherit
  `product.product_template_only_form_view`) punya arch serupa tapi TIDAK dimuat (`BSL-022`).
- `[BSL-014]` `[MATCH]` (ref: 18.0→19.0 BSL-013) Form Product Category
  (`product_category_form_view_inherit_margin_sale`, inherit
  `stock_account.view_category_property_form_stock`): `margin_sale` ditambahkan sebelum
  `property_cost_method`.
- Form Product Variant Easy Edit (`product_variant_easy_edit_view_margin_sale`, inherit
  `product.product_variant_easy_edit_view`): `lst_price` di-`position="replace"` dengan
  `decoration-danger="is_less_minimum_sale"`; group `pricing` ditambah `margin_sale`/
  `minimum_sale_price`/`minimum_sale_price_with_tax` dengan `invisible=` yang sama persis dengan
  form Template (`product_variant_count > 1 and not is_product_variant`) — pada view ini
  `is_product_variant` selalu `True` (record `product.product` selalu representasi satu variant),
  jadi kondisi `invisible` ini secara praktis SELALU `False` (blok selalu tampil) — bukan bug yang
  berdampak, hanya kondisi yang tampak disalin dari view Template tanpa disesuaikan.

### Owl / JavaScript (patch terhadap komponen inti `point_of_sale`)
- `patch(ProductProduct.prototype)` (`static/src/store/models/models.js`) — dua getter baru:
  `get_minimum_sale_price()` (return `this.minimum_sale_price`) dan
  `get_minimum_sale_price_with_tax()` (return `this.minimum_sale_price_with_tax`). Ini pengganti
  mekanisme 17.0 (`_loader_params_product_product`, lihat `BSL-009`).
- `patch(PosOrderline.prototype)` (file sama) — `setUnitPrice(price)` (cuma memanggil
  `super.setUnitPrice(price)`, no-op tambahan — kandidat dead patch, perlu dicek ulang di Step 2/6
  apakah override kosong ini masih diperlukan di 20.0 atau residu dari migrasi 18→19); getter
  `minimumSalePriceWithTax` (format currency dari `get_minimum_sale_price_with_tax()`); getter
  `isLessMinimumSalePrice` (`this.displayPriceUnit < product.get_minimum_sale_price_with_tax()`).
  **Ini pengganti langsung untuk `Orderline.props.line.shape` (dihapus total di 19.0, dulu
  `FINDINGS.md` `MF-12`) dan `getDisplayData()` (dihapus total, dulu `MF-13`)** — komponen `Orderline`
  sekarang membaca getter ini langsung dari record model (`line.<getter>`), bukan lewat objek
  display-data terpisah.
- `patch(PosStore.prototype.pay())` — lihat §4 `BSL-004`..`BSL-007`.
- `[BSL-015]` `[MATCH]` (ref: 18.0→19.0 BSL-014 — catatan: mekanisme detail berubah, lihat `BSL-016`)
  `orderline.xml` (`t-inherit point_of_sale.Orderline`, `t-inherit-mode="extension"`): xpath ke
  `//li[contains(@class, 'orderline')]//ul[hasclass('info-list')]/t[@t-slot='default']` (descendant,
  bukan direct-child — mempertahankan fix `FINDINGS.md` 18.0→19.0 `MF-20`/`BSL-014` lama) `position="before"`,
  menambah `<li t-if="line.isLessMinimumSalePrice">` dengan teks peringatan + nilai
  `line.minimumSalePriceWithTax`.
- `[BSL-016]` `[NO-SPEC]` (ref: —, baru — perincian mekanisme) Class `text-danger` TIDAK ditambahkan
  independen — `orderline.xml` men-patch atribut `t-attf-class` di elemen `<li class="orderline">`
  dengan xpath `position="attributes"`, MENGGABUNGKAN kondisi milik modul ini
  (`{{ line.isLessMinimumSalePrice ? 'text-danger' : '' }}`) dengan kondisi milik core sendiri
  (`{{ line.comboParent ? 'border-start border-3 ms-4' : '' }}`) di satu ekspresi `t-attf-class` yang
  sama. Baseline 18.0→19.0 lama (`BSL-014` versi lama) hanya menyebut "tambah class text-danger",
  tidak merinci penggabungan dengan class combo core. Implikasi: kalau 20.0 mengubah/menambah kondisi
  class combo lagi di core, patch modul ini WAJIB menyesuaikan ekspresi gabungan ini (bukan cuma
  menambah satu class terpisah) — risiko tersembunyi untuk Step 2/6.
- `[BSL-017]` `[GAP]` **Spec lama:** `FINDINGS.md` `MF-24` (dibawa dari project 18.0→19.0) mencatat
  pola `position="replace"` yang menghapus atribut core HANYA di `views/products.xml` baris ~62-64
  (field `list_price`, view `product_template_inherit_pos_margin_threshold`). **Kode aktual:** pola
  identik JUGA ada di `views/products.xml` baris ~95-97 (field `lst_price`, view
  `product_variant_easy_edit_view_margin_sale`) — `<field name="lst_price" position="replace">`
  mengganti definisi core (`options`/`optional`/`decoration-muted` bawaan `lst_price`) dengan versi
  yang hanya punya `decoration-danger`/`widget`. Instance kedua ini tidak pernah tercatat di
  `FINDINGS.md` `MF-24` maupun baseline manapun sebelumnya. Dampak sama seperti `MF-24` asli — belum
  ada keputusan pemilik modul untuk memperbaiki keduanya (pre-existing, bukan gap migrasi 19→20),
  jadi harus dipertahankan identik seperti sekarang, TAPI jejak audit ini perlu dibawa ke Step 8 Code
  Review project ini supaya scope `MF-24` yang diverifikasi ulang tidak berhenti di satu lokasi saja.
- `[BSL-018]` `[MATCH]` (ref: 18.0→19.0 BSL-015) Gap test yang masih TERBUKA (belum ditutup DUA
  project migrasi sebelumnya, carry-forward lagi): AC-02-03 (tidak ada popup sama sekali kalau semua
  line di atas minimum — belum ada test otomatis) dan AC-02-04 (assert teks/warna warning orderline
  secara terpisah, bukan cuma "tidak crash"). Dua Tour test yang ADA sekarang
  (`pos_margin_threshold_below_minimum_confirm_tour`, `..._blocked_tour`, sudah dieksekusi nyata di
  iterasi migrasi sebelumnya, lihat `tests/test_margin_threshold_tour.py`) menutup AC-02-02 dan jalur
  blocking, TAPI BUKAN dua skenario gap ini. **Keputusan user diperlukan:** ditutup di project
  19.0→20.0 ini, atau tetap dilewati?
- `[BSL-019]` `[MATCH][DIWARISI-SOURCE]` (ref: FINDINGS.md MF-23) `product.product._compute_warning`
  (di belakang `is_less_minimum_sale`) TIDAK didekorasi `@api.depends(...)` — dikonfirmasi cocok
  dengan kode aktual sesi ini (`models/product.py` baris ~69-71). ORM tidak tahu harus
  invalidasi/recompute field ini saat `lst_price`/`minimum_sale_price` berubah, risiko cache stale
  (warna peringatan UI bisa tidak update sampai reload penuh). Sudah ada keputusan dev sebelumnya:
  "dibiarkan dulu" (2026-08-27, `FINDINGS.md` project 18.0→19.0) — belum diperbaiki, tetap terbuka.

## 7. Dependency Eksternal

### Eksplisit (manifest)
- `depends: ['base', 'point_of_sale', 'product', 'stock_account']` — dikonfirmasi keempatnya ada di
  `native-target` 20.0 (`odoo20`), lihat `01a_MIGRATION_INTAKE.md` §2.

### Implisit/Inferred
- `sale_margin_threshold` (custom, sibling) — kolisi `_name` `wizard.margin.product` (`BSL-020`).
- XML-ID target inherit: `stock_account.view_category_property_form_stock`,
  `product.product_template_form_view`, `product.product_template_only_form_view` (via dead file),
  `product.product_variant_easy_edit_view`.
- JS import path (semua internal `point_of_sale`, WAJIB diverifikasi ulang ke `native-target` 20.0 di
  Step 2 — area ini sudah dua kali breaking change 17→18 dan 18→19): `@point_of_sale/app/models/product_product`,
  `@point_of_sale/app/models/pos_order_line`, `@point_of_sale/app/services/pos_store`,
  `@point_of_sale/app/models/utils/currency` (`formatCurrency`),
  `@point_of_sale/app/utils/make_awaitable_dialog` (`ask`),
  `@web/core/confirmation_dialog/confirmation_dialog` (`AlertDialog`), `@web/core/l10n/translation`
  (`_t`), `@web/core/utils/patch` (`patch`).
- Test-tour util import path (sudah pindah sekali, 18→19, `FINDINGS.md` `MF-19` lama — WAJIB dicek
  ulang lagi untuk 20.0): `@point_of_sale/../tests/pos/tours/utils/chrome_util`,
  `.../product_screen_util`, `.../payment_screen_util`, `@point_of_sale/../tests/generic_helpers/dialog_util`.

## 8. Quirk / Behavior Non-Obvious

- `[BSL-020]` `[MATCH][DIWARISI-SOURCE][PERLU-KEPUTUSAN]` (ref: 18.0→19.0 BSL-016; FINDINGS.md MF-03)
  Model `wizard.margin.product` (`_name`, bukan `_inherit`) didefinisikan BYTE-IDENTIK di modul ini
  dan di `sale_margin_threshold`. Kalau keduanya terinstall, Odoo meng-*merge* jadi satu model, dan
  `__mro__` SELALU menghasilkan class `sale_margin_threshold` menang (dikonfirmasi empiris di dua
  project migrasi sebelumnya, dua urutan install, hasil identik). Class modul INI
  (`pos_margin_threshold`) hilang total dari registry, bukan cuma "kalah prioritas". Ada test
  cross-module (`tests/test_cross_module.py`) yang memverifikasi model gabungan tetap bisa
  `create()` tanpa error kalau `sale_margin_threshold` juga terinstall (skip kalau tidak). **Risiko:**
  kalau salah satu wizard diubah sendirian di 20.0 tanpa sinkron manual ke yang lain, perubahan itu
  silent.
- `[BSL-021]` `[MATCH][DIWARISI-SOURCE]` (ref: 18.0→19.0 BSL-017; FINDINGS.md MF-02)
  `blocking_transaction_order` dideklarasikan di `res.config.settings` modul ini tapi TIDAK PERNAH
  dibaca oleh kode modul ini sendiri — field ini hanya bermakna kalau `sale_margin_threshold` juga
  terinstall. Ada test yang mengonfirmasi field ini TIDAK muncul di view settings milik
  `pos_margin_threshold` sendiri (`tests/test_margin_sale.py`,
  `test_blocking_transaction_order_field_has_no_view_in_this_module`). Bukan bug, tapi field yang
  "kelihatan aktif" di UI settings modul ini padahal efeknya nol tanpa modul sibling.
- `[BSL-022]` `[MATCH][DIWARISI-SOURCE]` (ref: 18.0→19.0 BSL-018; FINDINGS.md MF-04)
  `views/product_template_views.xml` ada di disk (`inherit_id="product.product_template_only_form_view"`,
  XML-ID `product_template_inherit_pos_margin_threshold`), TIDAK terdaftar di manifest `data:` — dead
  file yang sengaja dipertahankan mati (mencegah duplikat XML-ID dengan record aktif di
  `views/products.xml`, yang target `inherit_id`-nya beda: `product.product_template_form_view`).
  Dikonfirmasi ulang cocok dengan `__manifest__.py` aktual sesi ini (`data:` tidak menyebut file ini
  sama sekali).
- Typo `action_assing_margin` (bukan "assign") — di method Python
  (`wizard/wizard_margin_product.py`) DAN di atribut `name=` XML
  (`wizard/wizard_margin_product.xml`) — harus tetap identik, view mereferensikan nama method secara
  literal (`BSL-003`).
- `controllers/controllers.py` — seluruh isi di-comment, scaffold mati sejak awal (bukan regresi
  migrasi manapun), `controllers/__init__.py` tetap `from . import controllers` (no-op, tidak
  error).
- `MF-24`/`BSL-017` (lihat §6 di atas) — bukan diulang di sini, sudah dijelaskan lengkap sebagai
  `[GAP]` di §6 Client-Side Behavior karena sifatnya spesifik view/XML.

---

## Cara Pakai

Lihat `migration-tool/templates/01b_BASELINE_SPEC.md` §Cara Pakai untuk aturan penomoran/provenance
lengkap. Ringkas: ID `BSL-NNN` di dokumen ini adalah penomoran BARU (mulai 001) khusus project
19.0→20.0 — TIDAK sama dengan `BSL-NNN` di dokumen 18.0→19.0 (dirujuk eksplisit sebagai
`(ref: 18.0→19.0 BSL-NNN)` di tiap klaim yang diwarisi), maupun `MF-NNN` di `FINDINGS.md` (dirujuk
`(ref: FINDINGS.md MF-NNN)`) — supaya tidak ambigu.
