# Baseline Spec — pos_margin_threshold

**Step:** 1 — Intake & Scope (pelengkap `01a_MIGRATION_INTAKE.md`)
**Tujuan:** dokumentasikan APA yang modul lakukan (behavior as-is) di 17.0 — bukti tertulis dari source of truth (kode 17.0 yang berjalan, branch `backfill/17.0`).
**Tanggal:** 2026-08-24
**Sumber:** Direkonsiliasi dari `doc-dev/backfill/spec/pos_margin_threshold/01A_FUNCTIONAL_SPEC.md` + `01B_ACCEPTANCE_CRITERIA.md` (branch `backfill/17.0`, 2026-07-31, sudah lewat eksekusi test Docker) + cross-check langsung ke kode aktual sesi ini (2026-08-24, tidak ada penyimpangan ditemukan)

> Ini **sumber kebenaran** untuk `05a_MIGRATION_ACCEPTANCE_CRITERIA.md` dan semua testing (step 9, 10, 11) — BUKAN `03_MIGRATION_SPEC.md`.

---

## Ringkasan untuk Review — Perlu Konfirmasi User

**Tally provenance:** 13 klaim `[MATCH]` (semua terverifikasi eksekusi Docker oleh project backfill, 2026-07-31), 3 klaim `[NO-SPEC]` (ditemukan baca kode langsung sesi ini, belum pernah dicek dokumen manapun).

1. `[BSL-011]` `[PERLU-KEPUTUSAN]` `[DIWARISI-SOURCE]` — `margin_sale` per-variant **tidak pernah bisa berbeda** antar variant satu template (inverse selalu menulis ke template, shared). Diwarisi dari `MF-01`/backfill `F-01`. Harus dipertahankan identik — **kecuali** Step 2 menemukan mekanisme compute/inverse Odoo 18.0 berubah cara kerjanya (butuh dicek ulang, jangan diasumsikan otomatis sama).
2. `[BSL-012]` `[PERLU-KEPUTUSAN]` `[DIWARISI-SOURCE]` — field `blocking_transaction_order` dideklarasikan modul ini tapi tidak berefek apapun sendirian (baru bermakna kalau `sale_margin_threshold` juga terinstall). Diwarisi dari `MF-02`/backfill `F-02`.
3. `[BSL-013]` `[PERLU-KEPUTUSAN]` `[DIWARISI-SOURCE]` — model `wizard.margin.product` didefinisikan `_name` ganda (bukan `_inherit`) identik dengan `sale_margin_threshold`; kalau keduanya terinstall, kelas Python `pos_margin_threshold` **hilang total** dari MRO (bukan digabung). Diwarisi dari `MF-03`/backfill `F-03`. **Risiko migrasi:** urutan resolusi MRO Python tidak berubah antar versi Odoo (ini murni mekanisme Python, bukan Odoo API) — risiko utamanya justru kalau salah satu modul (pos atau sale) berubah kode wizard-nya saat migrasi tapi yang lain tidak, silent-override tetap terjadi seperti di 17.0.
4. `[BSL-014]` **`[NO-SPEC]` `[DIWARISI-SOURCE]` — TEMUAN BARU sesi ini, bukan dari backfill:** `views/product_template_views.xml` tidak terdaftar di `data:` manifest, dan mendefinisikan XML-ID (`product_template_inherit_pos_margin_threshold`) yang **identik** dengan `views/products.xml` (isi & `inherit_id` target berbeda). File ini dead code di 17.0 sekarang — dicatat sebagai `MF-04` di `FINDINGS.md`. Harus tetap dead code yang sama di 18.0 (jangan didaftarkan ke manifest tanpa persetujuan eksplisit — kalau didaftarkan apa adanya, akan clash XML-ID dengan `products.xml`).
5. `[BSL-002]` `[MATCH]` (ref: BR-06, AC-03-01/02) — method wizard bernama `action_assing_margin` (**typo "assing", bukan "assign"**) dipakai konsisten di Python model dan XML view (`name="action_assing_margin"`). Ini BUKAN bug fungsional (cuma penamaan) — **wajib dipertahankan ejaan yang sama persis di 18.0**, karena mengubahnya ("memperbaiki" jadi "assign") akan memutus rujukan `name=` di `wizard_margin_product.xml`.
6. Business rule inti lain (BR-01..BR-07 asli) semuanya `[MATCH]` — sudah diverifikasi eksekusi test Docker oleh backfill, tidak diulang di sini satu-satu (lihat §4/5/6/8 di bawah untuk detail per klaim).

---

## 1. Tujuan Modul

Modul ini menghitung dan menegakkan harga jual minimum + margin per produk khusus untuk transaksi **Point of Sale** — memberi peringatan (atau memblokir pembayaran, sesuai konfigurasi) kalau kasir menjual produk di bawah harga minimumnya. Margin diwariskan dari kategori produk (bisa di-override per produk/variant), dan sistem menampilkan indikator visual (warna merah) di berbagai tempat kalau harga jual berada di bawah minimum yang dihitung.

## 2. Model & Tanggung Jawab

| Model | Tanggung Jawab |
|---|---|
| `product.category` (extend) | Menyimpan `margin_sale` default yang diwariskan ke semua produk di kategori itu |
| `product.template` (extend) | Compute margin dari kategori (bisa override manual), compute harga minimum (+ pajak), action assign margin massal |
| `product.product` (extend) | Compute margin dari template (bisa override manual — TAPI inverse-nya menulis balik ke template, lihat `[BSL-011]`), flag `is_less_minimum_sale` |
| `pos.config` (extend) | Compute `is_blocked_warning` dari config parameter, dikonsumsi JS POS |
| `res.config.settings` (extend, transient) | Expose 2 config parameter: `blocking_transaction_pos` (dipakai modul ini) dan `blocking_transaction_order` (TIDAK dipakai modul ini, lihat `[BSL-012]`) |
| `pos.session` (extend) | Menambahkan 2 field (`minimum_sale_price`, `minimum_sale_price_with_tax`) ke payload data produk yang dikirim ke frontend POS |
| `wizard.margin.product` (baru, `_name` — bukan `_inherit`) | Wizard set margin massal ke banyak produk/template sekaligus dari list view |

## 3. Field dengan Makna Bisnis

### `product.category`
- `margin_sale` (Float) — persentase margin default untuk kategori ini, diwariskan ke semua produk di kategori (tanpa override manual).

### `product.template`
- `margin_sale` (Float, `tracking=True`, compute+store, override manual diizinkan) — persentase margin.
- `minimum_sale_price` (Float, compute+inverse+store) — `standard_price * (1 + margin_sale/100)`.
- `minimum_sale_price_with_tax` (Float, compute+store, **tanpa inverse**) — `minimum_sale_price * (1 + total_tax_amount/100)`.

### `product.product`
- `margin_sale` (Float, `tracking=True`, compute+inverse+store) — sama seperti template, tapi inverse-nya menulis balik ke `product_tmpl_id` (lihat `[BSL-011]`).
- `minimum_sale_price` (Float, compute+inverse+store) — dihitung ulang independen dari `standard_price` variant sendiri (formulanya sama dengan template, tapi `standard_price` per-variant BISA beda kalau ada Landed Cost/tracking harga per-variant — di luar scope modul ini untuk diverifikasi lebih jauh).
- `minimum_sale_price_with_tax` — **TIDAK didefinisikan ulang di kelas ini**, didapat lewat delegasi Odoo core (`product.product` `_inherits` `product.template`).
- `is_less_minimum_sale` (Boolean, compute, tidak `store`) — `lst_price < minimum_sale_price`.

### `pos.config`
- `is_blocked_warning` (Boolean, compute, tidak `store`) — dari `ir.config_parameter` `post_margin_sale.blocking_transaction_pos`.

### `res.config.settings`
- `blocking_transaction_order` (Boolean → `post_margin_sale.blocking_transaction_order`).
- `blocking_transaction_pos` (Boolean → `post_margin_sale.blocking_transaction_pos`).

### `wizard.margin.product`
- `product_template_ids` (Many2many `product.template`), `product_ids` (Many2many `product.product`), `is_product` (Boolean, compute dari `context.active_model`), `margin` (Float, input user).

## 4. Business Workflow / State Transition

### Perhitungan & pewarisan margin
- `[BSL-001]` `[MATCH]` (ref: BR-01, AC-01-01, AC-01-02) Margin produk (template maupun variant) otomatis terisi dari `categ_id.margin_sale` via compute (`@api.depends('categ_id.margin_sale')`). User bisa override manual langsung di form produk — nilai manual tersimpan (`store=True`) dan TIDAK kembali ke nilai kategori sampai dependency compute-nya sendiri berubah lagi (bukan re-sync otomatis tiap dibaca).

### Wizard assign margin massal
- `[BSL-002]` `[MATCH]` (ref: BR-06, AC-03-01, AC-03-02) Dari list view Product Template ATAU Product Variants, user pilih banyak produk sekaligus, buka wizard "Update margin sale" (action server, binding ke `model_product_template`/`model_product_product`), isi satu nilai margin, klik tombol "Assign" (method `action_assing_margin` — **typo, lihat "Ringkasan" poin 5**) → SEMUA produk terpilih langsung ditimpa nilai margin yang sama, tanpa konfirmasi tambahan (selain `tracking=True` di chatter). Field yang ditampilkan (`product_template_ids` vs `product_ids`) dikontrol `is_product` compute dari `context.active_model`.

### Blocking/warning saat pembayaran POS
- `[BSL-003]` `[MATCH]` (ref: BR-04, AC-02-01, AC-02-02, AC-02-03) Saat kasir klik bayar (`Order.pay()` di-patch): cek semua orderline, filter yang `unit_price < minimum_sale_price_with_tax`. Kalau ada baris yang kena filter:
  - `blocking_transaction_pos = True` → `ErrorPopup` ("Please check !"), pembayaran **dihentikan total** (return sebelum `super().pay()`).
  - `blocking_transaction_pos = False` (default) → `ConfirmPopup`, kasir pilih lanjut (`super().pay()`) atau batal (`return`).
  - Tidak ada baris yang kena filter → langsung `super().pay()`, tidak ada popup.

## 5. Server-Side Logic dengan Side Effect

### `product.template`
- `[BSL-004]` `[MATCH]` (ref: BR-02, AC-01-03, AC-01-04, AC-01-05) `minimum_sale_price = standard_price * (1 + margin_sale/100)` (compute), dan inverse: edit `minimum_sale_price` manual → `margin_sale` di-hitung-balik `((minimum_sale_price/standard_price) - 1) * 100`. Guard eksplisit: kalau `standard_price = 0`, inverse set `margin_sale = 0.0` (hindari div-by-zero).
- `[BSL-005]` `[MATCH]` (ref: BR-03) `minimum_sale_price_with_tax = minimum_sale_price * (1 + total_tax_amount/100)` — **satu-satunya definisi ada di kelas `ProductTemplate`**, `ProductProduct` tidak mendefinisikan ulang, nilainya didapat lewat delegasi otomatis Odoo core (`_inherits`). Ini aman dalam praktik BUKAN karena desainnya sengaja begitu, tapi karena `[BSL-011]` membuat precondition "margin beda antar variant" tidak pernah tercapai — lihat detail di §8.

### `product.product`
- `[BSL-004]` (lanjutan, variant) `minimum_sale_price`/inverse dihitung ulang independen di level variant dengan formula identik (`standard_price` milik variant sendiri).

### `pos.session`
- `[BSL-006]` `[NO-SPEC]` (ref: 01A_FUNCTIONAL_SPEC.md §Scope "Yang Termasuk" bullet 5 — disebut naratif, tidak diberi BR-ID di dokumen asal) `_loader_params_product_product` (extend via `super()`, pattern override yang benar — bukan replace method core) menambahkan `minimum_sale_price` dan `minimum_sale_price_with_tax` ke daftar field yang dikirim ke frontend POS.

## 6. Client-Side Behavior (Views, JS, Owl)

### Backend (form/list view produk)
- `[BSL-007]` `[MATCH]` (ref: BR-04) `models.js`: patch `Product.prototype` menambah `get_minimum_sale_price()`/`get_minimum_sale_price_with_tax()`; patch `Orderline.prototype.getDisplayData()` menambah field `minimumSalePrice`/`minimumSalePriceWithTax`/`isLessMinimumSalePrice` ke data tampilan; patch `Order.prototype.pay()` — logika blocking/confirm (lihat `[BSL-003]`).
- `[BSL-008]` `[NO-SPEC]` (ditemukan baca kode langsung, tidak disebut di dokumen manapun sebelumnya) `pos_store.js`: patch `PosStore.prototype._loadProductProduct()` — memberi default `0` ke `minimum_sale_price`/`minimum_sale_price_with_tax` kalau field itu falsy (`product.minimum_sale_price = product.minimum_sale_price || 0`) sebelum memanggil `super()`. Fallback ini mencegah `undefined`/`null` dipakai di kalkulasi JS (`get_unit_display_price() < ...`) yang bisa menghasilkan `NaN`/comparison salah.
- `[BSL-009]` `[MATCH]` (ref: 01A_FUNCTIONAL_SPEC.md §Scope "Yang Termasuk" bullet 6, "Highlight visual") `orderline.xml` (t-inherit `point_of_sale.Orderline`): baris order yang `isLessMinimumSalePrice` ditandai class `text-danger` + pesan peringatan ("*The price of this product is less than minimum sale price ...") ditambahkan sebelum slot default.
- `[BSL-010]` `[MATCH]` (ref: 01A_FUNCTIONAL_SPEC.md §Scope bullet 6) Form/list view produk: `list_price` (template) dan `lst_price` (variant easy-edit) diberi `decoration-danger` kalau di bawah `minimum_sale_price`/`is_less_minimum_sale`. Field `margin_sale`/`minimum_sale_price`/`minimum_sale_price_with_tax` ditambahkan ke form kategori (`stock_account.view_category_property_form_stock`), form template (`product.product_template_form_view`, dan salinan berbeda di `product.product_template_only_form_view` — lihat `[BSL-014]`), dan easy-edit variant (`product.product_variant_easy_edit_view`) — dengan visibility conditional (`invisible="product_variant_count > 1 and not is_product_variant"`) supaya field harga tidak dobel tampil untuk produk multi-variant di beberapa tempat.

## 7. Dependency Eksternal

### Eksplisit (manifest)
`depends: ['base', 'point_of_sale', 'product', 'stock_account']` — semua Native Community, tidak ada Enterprise/OCA (lihat `01a_MIGRATION_INTAKE.md` §2, masih perlu konfirmasi eksplisit dev di §0).

### Implisit/Inferred
- `stock_account.view_category_property_form_stock` (XML-ID inherit target) — dependency implisit ke struktur view spesifik modul `stock_account`, bukan cuma dependency modul secara umum. Kalau XML-ID ini berubah/dihapus di 18.0, inherit akan gagal — WAJIB dicek di Step 2.
- `product.product_template_form_view`, `product.product_template_only_form_view`, `product.product_variant_easy_edit_view` — sama, dependency implisit ke XML-ID spesifik core `product`, rawan berubah antar versi Odoo.
- `point_of_sale.Orderline` (t-inherit QWeb), `@point_of_sale/app/store/models` (`Orderline`/`Product`/`Order` JS export), `@point_of_sale/app/store/pos_store` (`PosStore` JS export), `@point_of_sale/app/utils/confirm_popup/confirm_popup`, `@point_of_sale/app/errors/popups/error_popup` — semua ini titik integrasi JS yang **paling rawan breaking change 17→18** (arsitektur frontend POS Odoo mengalami refactor signifikan antar versi mayor secara historis) — prioritas utama Step 2.

## 8. Quirk / Behavior Non-Obvious

- `[BSL-011]` `[MATCH]` `[DIWARISI-SOURCE]` (ref: BR-01, BR-03, AC-01-06, **backfill F-01** — dieksekusi 3× via Docker test `test_margin_sale_inverse_writes_to_shared_template_not_per_variant`) `margin_sale` pada `ProductProduct` PUNYA inverse sendiri (`_set_product_margin_sale`, terlihat seperti field independen per-variant), TAPI inverse itu menulis ke `product_tmpl_id.write({'margin_sale': ...})` — ke TEMPLATE yang di-share SEMUA variant sibling. Karena compute semua variant `@api.depends('product_tmpl_id.margin_sale')`, mengubah margin SATU variant otomatis mengubah margin SEMUA variant lain di template yang sama ("last write wins" untuk seluruh grup, bukan per-variant). **Konsekuensi:** `minimum_sale_price_with_tax` (yang cuma didefinisikan di level template, `[BSL-005]`) tidak bisa inkonsisten antar variant — bukan karena delegasinya "didesain aman", tapi karena precondition "margin beda antar variant" tidak pernah bisa tercapai sejak awal.
- `[BSL-012]` `[MATCH]` `[DIWARISI-SOURCE]` (ref: BR-05, AC-04-01, **backfill F-02**) `blocking_transaction_order` dideklarasikan modul ini (`models/res_config_settings.py:8`) tapi tidak pernah ditampilkan di `views/res_config_settings.xml` modul ini (cuma expose `blocking_transaction_pos`) dan tidak dibaca kode manapun di modul ini. Field ini baru "hidup" kalau `sale_margin_threshold` juga terinstall.
- `[BSL-013]` `[MATCH]` `[DIWARISI-SOURCE]` (ref: BR-07, AC-04-02, **backfill F-03** — dieksekusi via `tests/test_cross_module.py`) `wizard.margin.product` didefinisikan `_name` (bukan `_inherit`) identik-byte dengan `sale_margin_threshold`. Kalau KEDUA modul terinstall, `__mro__` final HANYA berisi kelas dari modul yang diinstall **lebih belakangan** — kelas `pos_margin_threshold` untuk model ini hilang total dari MRO (bukan digabung seperti dugaan naif). Aman selama kedua kelas byte-identik; kalau salah satu modul diubah independen di masa depan, perubahan itu silent-diabaikan selama modul lain terinstall duluan.
- `[BSL-014]` `[NO-SPEC]` `[DIWARISI-SOURCE]` **(temuan baru sesi ini, belum pernah tercatat backfill)** `views/product_template_views.xml` **tidak ada** di `data:` manifest — dead file, tidak pernah dimuat Odoo. File ini mendefinisikan XML-ID `product_template_inherit_pos_margin_threshold` yang **identik** dengan yang didefinisikan `views/products.xml` (target `inherit_id` beda: `product.product_template_only_form_view` vs `product.product_template_form_view`). Kalau file ini suatu saat ditambahkan ke `data:` tanpa mengganti nama ID, akan clash langsung dengan `products.xml`. Dicatat sebagai `MF-04`.
- `[BSL-002]` (lihat juga "Ringkasan" poin 5) `[MATCH]` `[DIWARISI-SOURCE]` Method `action_assing_margin` — nama method (bukan "assign") konsisten di model Python DAN atribut `name=` tombol XML (`wizard_margin_product.xml:22`). Bukan bug fungsional, tapi WAJIB dipertahankan ejaan identik di 18.0.
- `[BSL-015]` `[NO-SPEC]` `[DIWARISI-SOURCE]` `controllers/controllers.py` — seluruh isi file (boilerplate scaffold default Odoo) di-comment total, tidak ada route HTTP terdaftar. Dead file, bukan bug — cukup dipertahankan sebagai file kosong/comment yang sama.

---

## Cara Pakai

ID `BSL-NNN` di dokumen ini lanjut nomor dari 001 (khusus modul `pos_margin_threshold` — penomoran TIDAK dibagi lintas 3 modul, beda dengan `FINDINGS.md` yang pakai `MF-NNN` lintas modul). Rujukan silang ke `MF-NNN` (root `doc/FINDINGS.md`) dan `F-NNN` (backfill) dicatat eksplisit di tiap klaim yang mewarisi finding lama — lihat §8.
