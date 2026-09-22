# Migration Spec (Teknis) — pos_margin_threshold

**Step:** 3 — Migration Spec
**Versi:** 19.0 → 20.0
**Ref:** `02_diff/pos_margin_threshold/02_DIFF_ANALYSIS.md`
**Tanggal:** 2026-09-22

> Dokumen ini memandu IMPLEMENTASI (step 6). Ini **bukan** dasar testing/acceptance criteria —
> itu datang dari `01b_BASELINE_SPEC.md` dan kode 19.0 yang berjalan (branch `migration/19.0`).
> Lihat step 5.

---

## 1. Ringkasan Strategi

**Update retroaktif (Step 4, 2026-09-22):** klaim asli paragraf ini — "Python tidak butuh perubahan
apapun" — sudah TIDAK akurat lagi. `ProductProduct.minimum_sale_price_with_tax` (field baru, compute
dari `margin_sale`/`minimum_sale_price`/`product_tmpl_id.taxes_id`) DITAMBAHKAN ke `models/product.py`
sebagai bagian fix `MF-38` (visual parity, dikonfirmasi dev 2026-09-22) — field ini sebelumnya HANYA
ada di `ProductTemplate`, sekarang juga ada di `ProductProduct`. Juga, `static/src/store/orderline.xml`
(bukan Python, tapi bagian klaim "stabil" yang sama) diperbaiki untuk `MF-34` (`line.comboParent` →
`combo_parent_id`, keputusan dev: perbaiki, bukan pertahankan — lihat `FINDINGS.md` `MF-34`). Detail
kedua fix ada di §2 tabel di bawah. Sisanya (wizard, `_load_pos_data_fields`, JS lain) tetap identik
seperti klaim asli. Breaking change instalasi modul ini SELURUHNYA ada di lapisan **XML/security**,
tiga item install-blocking:

1. **`DIFF-01`** — `security/ir.model.access.csv` harus di-rename + reformat jadi
   `security/ir.access.csv` (model ORM `ir.model.access` dihapus total di 20.0). Mekanis.
2. **`DIFF-02`** — anchor `stock_account.view_category_property_form_stock` pindah jadi
   `account.view_category_property_form`. Ganti satu `ref=`, field target (`property_cost_method`)
   tidak berubah posisi. Mekanis.
3. **`DIFF-03`** (⟷ `MF-29`) — `product.product_variant_easy_edit_view` dihapus total, TIDAK ADA
   pengganti bernama sama. **Keputusan desain sudah diambil dev (2026-09-21, lihat `FINDINGS.md`
   `MF-29`):** ganti record `product_variant_easy_edit_view_margin_sale` (inherit view yang sudah
   hilang) menjadi record BARU yang inherit `product.product_product_tree_view` (list "Product
   Variants", native 20.0 sudah `editable="bottom"`/`multi_edit="1"`), menambah kolom
   `margin_sale`/`minimum_sale_price` (`optional="show"`) + `decoration-danger` pada kolom
   `lst_price` yang sudah ada, dikaitkan ke `is_less_minimum_sale`. Ini keputusan yang SUDAH
   DIPUTUSKAN — spec di bawah menulis bentuk konkretnya, bukan opsi alternatif.

Tambahan non-blocking yang direkomendasikan Step 2 (`DIFF-04`, terkait `MF-24`/`MF-25`): anchor
`list_price` di `product.product_template_form_view` berubah struktural di 20.0 (native menambah
`options="{'currency_field': 'currency_id', 'field_digits': True}"` yang tidak ada di 19.0) —
supaya field pengganti modul tidak REGRESI visual dari 19.0 (bug `MF-24` tetap dipertahankan
identik — `position="replace"` TIDAK diubah jadi `position="attributes"` — hanya field pengganti
ditambah `options` yang sama seperti versi native 20.0 yang baru). Ini dikategorikan "wajib untuk
kompatibilitas 20.0" (mencegah regresi akibat perubahan native), bukan perbaikan bug diskresioner —
tapi tetap ditandai untuk konfirmasi ringan di gate Step 4 (lihat §4 "Perlu Konfirmasi").

`DIFF-05` (`line.comboParent`, terkait `MF-34`) — **RESOLVED (2026-09-22).** `native-source` sudah
diisi ulang dev (`odoo19`+`enterprise19`, dua clone terpisah). Cross-check tuntas ke native
mengonfirmasi `line.comboParent` adalah typo original sejak branch `17.0` (bukan gap migrasi 19→20)
— field asli native adalah `combo_parent_id`. **Keputusan dev: perbaiki** (bukan pertahankan) —
`static/src/store/orderline.xml` diupdate, styling combo-child AKTIF untuk pertama kalinya di 20.0.
Detail lengkap di `FINDINGS.md` `MF-34`.

Manifest: bump `version` dari `19.0.1.0` → `20.0.1.0` (skema angka mayor mengikuti versi Odoo,
konsisten pola migrasi 18→19 sebelumnya), plus update path `security/ir.model.access.csv` →
`security/ir.access.csv` di `data:`.

## 2. Strategi per File/Simbol (ringkasan umum)

> Kolom "kondisi source"/"kondisi target" tidak diulang di sini — lihat `02_DIFF_ANALYSIS.md` §1.

| File/simbol | Ref `DIFF-NNN` (02_DIFF_ANALYSIS §1) | Strategi migrasi | Risiko | Ref `BSL-NNN` |
|---|---|---|---|---|
| `security/ir.model.access.csv` | `DIFF-01` | Rename file → `security/ir.access.csv`, reformat header & baris ke skema baru (lihat §2a). Update `__manifest__.py` `data:` list. | Kritis kalau tidak dikerjakan (install-blocking) — rendah setelah fix, murni mekanis | — |
| `views/products.xml` record `product_category_form_view_inherit_margin_sale`, `<field name="inherit_id">` | `DIFF-02` | Ganti `ref="stock_account.view_category_property_form_stock"` → `ref="account.view_category_property_form"`. Tidak ada perubahan lain — xpath `<field name="property_cost_method" position="before">` tetap match. | Kritis kalau tidak dikerjakan — rendah setelah fix | `BSL-014` |
| `views/products.xml` record `product_variant_easy_edit_view_margin_sale` (inherit `product.product_variant_easy_edit_view`, DIHAPUS di 20.0) | `DIFF-03` / `MF-29` | **Ganti total** — hapus record lama, tulis record baru inherit `product.product_product_tree_view`, tambah kolom `margin_sale`/`minimum_sale_price` (`optional="show"`) + `decoration-danger` di kolom `lst_price` existing. Lihat §2a untuk XML literal. | Kritis kalau tidak dikerjakan (install-blocking); Sedang setelah fix — kolom baru harus direview visual Step 10 (keputusan dev sudah mencatat ini eksplisit) | `BSL-017`/`MF-25` (view yang sama, konteks bug lama yang harus tetap dipertahankan pada field `lst_price`) |
| `views/products.xml` record `product_template_inherit_pos_margin_threshold`, `<field name="list_price" position="replace">` | `DIFF-04` | **RESOLVED (2026-09-22, dikonfirmasi dev di gate Step 4)** — `options="{'currency_field': 'currency_id', 'field_digits': True}"` ditambahkan ke field pengganti `list_price`, menyamai atribut baru native 20.0. `position="replace"` (akar `MF-24`) TIDAK diubah jadi `attributes` — bug lama tetap dipertahankan identik. Diverifikasi: tidak ada beda visual di data instance ini (single-currency), murni jaga-jaga kompatibilitas. | Sedang tanpa fix (regresi visual currency/presisi dari 19.0); rendah dengan fix — **RESOLVED** | `BSL-013`/`MF-24` |
| `static/src/store/orderline.xml` `line.comboParent` | `DIFF-05` / `MF-34` | **RESOLVED (2026-09-22)** — `line.comboParent` → `line.combo_parent_id` (typo original sejak branch `17.0`, dikonfirmasi via `git show`; field asli native). Keputusan dev: perbaiki. Komentar XML (bahasa Inggris) ditambahkan. Styling combo-child aktif pertama kali di 20.0. | Rendah (styling saja) — **RESOLVED**, diverifikasi XML well-formed + update modul bersih | `BSL-016` |
| `views/products.xml` record `product_product_tree_view_inherit_margin_sale` (kolom `margin_sale`/`minimum_sale_price`) + `models/product.py` `ProductProduct` | `MF-38` (baru, ditemukan Step 2 setelah `03_MIGRATION_SPEC.md` awal ditulis) | **RESOLVED (2026-09-22, dikonfirmasi dev)** — visual parity dengan popup 19.0 yang belum tercakup di keputusan `MF-29` awal: `decoration-danger="margin_sale &lt; 0.0"` ditambahkan ke field `margin_sale`, field BARU `minimum_sale_price_with_tax` ditambahkan ke `ProductProduct` (compute, mirror pola `ProductTemplate`) + kolom baru "Incl. Tax" di list. Diverifikasi live: margin negatif tampil merah, kolom Incl. Tax terisi benar, tidak dobel dengan kolom `sale_margin_threshold` (marker dedup `MF-37` diterapkan juga di sisi `sale_margin_threshold`). | Rendah (cosmetic, sesuai prinsip source-of-truth "UX 20.0 harus identik 19.0") — **RESOLVED** | — |
| `static/src/store/pos_store.js` `patch(PosStore.prototype.pay())` | `DIFF-06` | Tidak ada tindakan — guard baru `canPay()` di native tidak konflik dengan override modul. | Tidak ada | `BSL-004`..`BSL-007` |
| Semua import path JS (`@point_of_sale/...`, `@web/core/...`) | `DIFF-07` | Tidak ada tindakan — seluruh import path modul stabil, tidak direstrukturisasi di 20.0. | Tidak ada | — |
| `static/src/store/orderline.xml` xpath ke `//li[contains(@class,'orderline')]//ul[hasclass('info-list')]/t[@t-slot='default']` | `DIFF-08` | Tidak ada tindakan — struktur DOM target xpath tidak berubah, `t-att-class` native baru dan `t-attf-class` modul additive (tidak saling override). | Rendah, tidak perlu perubahan | `BSL-015` |
| `models/product.py` `_load_pos_data_fields(self, config_id)` | `DIFF-09` | Tidak ada tindakan wajib — signature tidak berubah dari 19.0. Opsional kosmetik: rename param lokal `config_id`→`config` (tidak wajib, boleh dilewati). | Tidak ada | `BSL-009` |
| `static/src/store/models/models.js` `patch(PosOrderline.prototype, {setUnitPrice(price){...}})` | `DIFF-10` | Tidak ada tindakan — method native tetap ada, patch kosong (`super()`-only) tetap valid. **Dipertahankan** (bukan dihapus) sesuai forbidden-actions `CLAUDE.md`, kecuali dev putuskan lain. | Tidak ada | — |
| `__manifest__.py` | — | Bump `version` → `20.0.1.0`; update `data:` list entry `security/ir.model.access.csv` → `security/ir.access.csv`. | Rendah — mekanis | — |

### 2a. Kode/XML Literal — Perubahan Wajib

**`DIFF-01` — `security/ir.access.csv` (file baru, menggantikan `security/ir.model.access.csv`):**

Rename fisik file, isi baru (header + satu baris data, dikonfirmasi format dari
`odoo20/addons/product/security/ir.access.csv` — kolom `model_id` diisi nama model teknis
langsung, BUKAN external-id `model_xxx`; `operation` gabungan huruf `crud` menggantikan 4 kolom
`perm_read/write/create/unlink` yang semuanya `1` di baris lama):

```csv
id,name,model_id,group_id/id,operation,domain
access_wizard_margin_product,pos_margin_threshold.wizard_margin_product,wizard.margin.product,base.group_user,crud,
```

`__manifest__.py` §`data`: ganti baris `'security/ir.model.access.csv',` menjadi
`'security/ir.access.csv',`.

**`DIFF-02` — `views/products.xml`, record `product_category_form_view_inherit_margin_sale`:**

Ganti baris:
```xml
<field name="inherit_id" ref="stock_account.view_category_property_form_stock"/>
```
menjadi:
```xml
<field name="inherit_id" ref="account.view_category_property_form"/>
```
Tidak ada perubahan lain di record ini — `<field name="property_cost_method" position="before">`
tetap match (dikonfirmasi ada di `odoo20/addons/account/views/product_view.xml:130`, di dalam
group `stock_properties`).

**`DIFF-03`/`MF-29` — `views/products.xml`, ganti record `product_variant_easy_edit_view_margin_sale`:**

Hapus record lama (baris ~90-121 di `views/products.xml` saat ini):
```xml
<record id="product_variant_easy_edit_view_margin_sale" model="ir.ui.view">
    <field name="name">product.variant.easy.edit.view.margin.sale</field>
    <field name="model">product.product</field>
    <field name="inherit_id" ref="product.product_variant_easy_edit_view"/>
    ...
</record>
```

Ganti dengan record baru, inherit `product.product_product_tree_view` (list "Product Variants",
`odoo20/addons/product/views/product_views.xml:424-498` — kolom `lst_price` sudah ada dengan
`optional="show" options="{'currency_field': 'currency_id'}" widget="monetary"`, TANPA
`decoration-*` apapun di native):

```xml
<record id="product_product_tree_view_inherit_margin_sale" model="ir.ui.view">
    <field name="name">product.product.tree.view.inherit.margin.sale</field>
    <field name="model">product.product</field>
    <field name="inherit_id" ref="product.product_product_tree_view"/>
    <field name="arch" type="xml">
        <field name="lst_price" position="attributes">
            <attribute name="decoration-danger">is_less_minimum_sale</attribute>
        </field>
        <field name="lst_price" position="after">
            <field name="margin_sale" optional="show" widget="float"/>
            <field name="minimum_sale_price" optional="show" widget="monetary"
                   options="{'currency_field': 'currency_id'}"/>
            <field name="is_less_minimum_sale" column_invisible="True"/>
        </field>
    </field>
</record>
```

Catatan implementasi:
- `position="attributes"` (bukan `replace`) dipakai untuk `lst_price` di sini — **berbeda dari
  pola `MF-24`/`MF-25`** yang dipertahankan di record lain. Ini BUKAN pola baru yang menyalahi
  aturan "port kode saja": record lama (`product_variant_easy_edit_view_margin_sale`) memang sudah
  hilang total, jadi ini record BARU, bukan migrasi record lama — dipilih `attributes` di sini
  karena kolom `lst_price` native 20.0 di `product_product_tree_view` sudah punya
  `options`/`optional` yang harus tetap ada (beda situasi dari `DIFF-04`/`MF-24` yang memang
  mempertahankan pola `replace` warisan lama pada view LAIN).
- `is_less_minimum_sale` wajib ditambahkan sebagai kolom (`column_invisible="True"`, BUKAN
  `invisible="1"` — atribut form tidak berlaku di elemen `<list>`) supaya field itu ke-load dan
  bisa dipakai ekspresi `decoration-danger`.
- `margin_sale`/`minimum_sale_price` **tidak diberi `invisible=`** — per keputusan dev `MF-29`
  poin 3, koordinasi lintas-modul (sembunyikan kolom kalau `pos_margin_threshold` juga terinstall)
  adalah tanggung jawab SISI `sale_margin_threshold` (modul itu yang menyembunyikan kolomnya
  sendiri kalau modul ini terinstall, pola sudah ada di
  `sale_margin_threshold/views/product_template_views.xml:13-20`) — bukan tanggung jawab spec ini.
  **Risiko sisa:** kalau kedua modul terinstall bersamaan DAN spec `sale_margin_threshold`
  belum/tidak menerapkan invisible itu dengan benar, kolom `margin_sale`/`minimum_sale_price` bisa
  dobel (dua field node dengan nama sama di satu `<list>`) — WAJIB diverifikasi silang di Step 9
  kalau kedua modul di-install bersamaan (lihat `CLAUDE.md` §"Adaptasi multi-modul" soal step 9
  butuh instalasi bersama untuk verifikasi cross-module).
- Nama `id`/`name` record mengikuti konvensi modul (`<record_purpose>_inherit_margin_sale` /
  `product.<x>.tree.view.inherit.margin.sale`), konsisten pola record lain di file yang sama
  (`product_category_form_view_inherit_margin_sale`).
- `pos_margin_threshold/i18n/fr.po` berisi string terjemahan yang merujuk nama view lama
  (`product.variant.easy.edit.view.margin.sale`) — tidak install-blocking (PO file tidak divalidasi
  saat load data), tapi akan jadi entry terjemahan basi (orphan) setelah rename ini. Bukan prioritas
  Step 6, bisa dibersihkan kapan saja (regenerasi POT) tanpa risiko fungsional.

**`DIFF-04`/`MF-24` (direkomendasikan, lihat §4 untuk status konfirmasi) — `views/products.xml`
record `product_template_inherit_pos_margin_threshold`:**

Ganti:
```xml
<field name="list_price" position="replace">
    <field name="list_price" decoration-danger="list_price &lt; minimum_sale_price" widget="monetary"/>
</field>
```
menjadi:
```xml
<field name="list_price" position="replace">
    <field name="list_price" decoration-danger="list_price &lt; minimum_sale_price" widget="monetary"
           options="{'currency_field': 'currency_id', 'field_digits': True}"/>
</field>
```
`position="replace"` itu sendiri (akar `MF-24`, dipertahankan sesuai keputusan dev sebelumnya)
**tidak diubah**.

## 2b. Risk Analysis Terstruktur (detail, per kategori)

### Critical Migration Blockers
*(Mencegah instalasi atau operasi inti di 20.0)*

| # | Isu | Lokasi | Rujukan knowledge base |
|---|---|---|---|
| 1 | Manifest version — harus `20.0.x.x` | `__manifest__.py:17` | `knowledge/version-diffs/19-to-20.md` |
| 2 | `security/ir.model.access.csv` memuat model `ir.model.access` yang sudah dihapus total — install akan gagal saat load data security | `security/ir.model.access.csv` | `knowledge/version-diffs/19-to-20.md`; `02_DIFF_ANALYSIS.md` `DIFF-01`; `FINDINGS.md` `MF-30` |
| 3 | `ref="stock_account.view_category_property_form_stock"` tidak resolve (XML-ID dihapus/dipindah) | `views/products.xml` record `product_category_form_view_inherit_margin_sale` | `02_DIFF_ANALYSIS.md` `DIFF-02`; `FINDINGS.md` `MF-31` |
| 4 | `ref="product.product_variant_easy_edit_view"` tidak resolve (view dihapus total) | `views/products.xml` record `product_variant_easy_edit_view_margin_sale` | `02_DIFF_ANALYSIS.md` `DIFF-03`; `FINDINGS.md` `MF-29` |

**Priority:** HIGH — perbaiki ketiganya (#2-#4) sebelum G1 (install test) Step 6 dijalankan; tanpa
ini modul GAGAL INSTALL total, bukan cuma satu fitur rusak.

### OWL Widget yang Butuh Rewrite/Review

| Widget | File | Risiko | Detail |
|---|---|---|---|
| — | — | Tidak ada | Tidak ada widget Owl yang butuh rewrite siklus ini (`DIFF-06`..`DIFF-10` semuanya "tidak ada tindakan") — pengecualian dari pola dua migrasi sebelumnya. |

**Urutan wajib tetap berlaku** (walau tidak ada perubahan JS kali ini): migrasi SEMUA JavaScript
dulu (tetap pakai syntax Owl lama di template), baru upgrade template ke syntax Owl baru terakhir.
Lihat `06a_CODE_MIGRATION_PHASES.md` Fase E & F — untuk modul ini, Fase E/F murni verifikasi
(tidak ada kode diubah), bukan dilewati.

### Controller & Route

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| — | Tidak ada — `controllers/controllers.py` tetap dead scaffold (seluruh isi di-comment), tidak disentuh. | `controllers/controllers.py` | — |

### Assets & Dependency

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | `depends: ['base', 'point_of_sale', 'product', 'stock_account']` — keempatnya dikonfirmasi ada di `native-target` 20.0, tidak ada perubahan dibutuhkan | `__manifest__.py` | — (tidak ada tindakan) |
| 2 | `assets` (`point_of_sale._assets_pos`, `web.assets_tests`) — key asset bundle tidak berubah di 20.0 | `__manifest__.py` | — (tidak ada tindakan, verifikasi ulang saat G1) |

### Kompatibilitas Data Model

| # | Isu | Lokasi | Priority | Ref `BSL-NNN` |
|---|---|---|---|---|
| — | Tidak ada perubahan model Python dibutuhkan — semua field/compute/inverse `product.category`/`product.template`/`product.product`/`pos.config`/`res.config.settings`/`wizard.margin.product` tetap identik struktur di 20.0. | `models/`, `wizard/` | — | `BSL-008`..`BSL-012` |

### Risiko Integrasi

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | Kolisi `wizard.margin.product` dengan `sale_margin_threshold` (`MF-03`/`BSL-020`) — murni struktur Python, tidak terkait migrasi versi, TIDAK berubah oleh migrasi ini | `wizard/wizard_margin_product.py` | Menengah — tidak perlu aksi Step 6, sudah diketahui sejak Step 1 |
| 2 | Kolom `margin_sale`/`minimum_sale_price` di `product_product_tree_view` berpotensi dobel kalau `sale_margin_threshold` diinstall bersamaan dan koordinasi `invisible=` di sisi modul itu tidak diterapkan benar (lihat §2a catatan `DIFF-03`) | `views/products.xml` (record baru) ⟷ `sale_margin_threshold/views/product_template_views.xml` | Tinggi — WAJIB diverifikasi Step 9 dengan kedua modul terinstall bersamaan |

### Urutan Prioritas Testing

1. Install & startup — manifest version `20.0.x.x`, `ir.access.csv` termuat tanpa error, kedua
   `ref=` (`account.view_category_property_form`, `product.product_product_tree_view`) resolve.
2. Buka list "Product Variants" (Inventory/Sales > Products > Product Variants) — verifikasi kolom
   `margin_sale`/`minimum_sale_price` muncul (`optional="show"`, harus tampil tanpa toggle manual)
   dan `lst_price` berwarna merah (`decoration-danger`) untuk baris `is_less_minimum_sale=True`.
3. Buka form Product Category — verifikasi field `margin_sale` tetap muncul sebelum
   `property_cost_method` (anchor `DIFF-02` baru).
4. Buka form Product Template — verifikasi `list_price` (dengan `options` baru `DIFF-04`) tampil
   currency-aware, presisi desimal konsisten dengan field `uom_id` companion di sebelahnya.
5. Core user flow POS — jual produk di bawah minimum, klik Pay, verifikasi dialog
   confirm/block sesuai `blocking_transaction_pos` (BSL-004..BSL-007) — regresi-check saja (tidak
   ada perubahan kode di jalur ini, tapi WAJIB dites nyata, bukan diasumsikan aman dari baca kode).
6. Wizard bulk-assign margin (dari list Product Template DAN Product Variant) — Python murni,
   risiko rendah, tetap perlu smoke-test manual.
7. Persistensi data — save perubahan `margin_sale` dari kolom list baru, verifikasi inverse
   `_set_product_margin_sale` tetap menulis balik ke `product_tmpl_id` (`BSL-010`, quirk warisan
   yang harus tetap identik).
8. **Kalau `sale_margin_threshold` juga terinstall di environment yang sama:** verifikasi list
   "Product Variants" tidak menampilkan kolom `margin_sale`/`minimum_sale_price` dobel (Risiko
   Integrasi #2 di atas).

### View List (dulu Tree) Checklist

| # | Apa | Di mana | Perubahan |
|---|---|---|---|
| 1 | Standalone list view | `views/*.xml` | N/A — tidak ada `<tree>` tersisa di modul ini (sudah `<list>` sejak migrasi 17→18, dikonfirmasi grep bersih); record baru `DIFF-03` langsung ditulis pakai `<list>` (native `product_product_tree_view` sudah `<list>`). |
| 2 | `view_mode` di action | `ir.actions.act_window` | N/A — modul ini tidak mendefinisikan action baru untuk list Product Variants (memakai action native yang sudah ada). |
| 3 | Inline tree di form | `<field><tree>...</tree></field>` | N/A — tidak ada. |

### Estimasi Effort (opsional)

| Area | Effort | Catatan |
|---|---|---|
| `DIFF-01` (`ir.access.csv`) | Kecil | Rename + reformat 1 baris, mekanis |
| `DIFF-02` (`ref=` anchor kategori) | Kecil | Ganti 1 baris |
| `DIFF-03`/`MF-29` (view kolom list baru) | Sedang | XML baru sudah konkret di §2a, tapi butuh review visual Step 10 (keputusan dev) + verifikasi cross-module Step 9 |
| `DIFF-04` (options currency pada `list_price`) | Sangat kecil | 1 atribut tambahan — **RESOLVED**, dikonfirmasi dev di gate Step 4 |
| `DIFF-05`/`MF-34` (`combo_parent_id`) | Kecil | 1 rename identifier + komentar — **RESOLVED**, native-source terisi ulang, dev putuskan perbaiki |
| `MF-38` (visual parity: field baru + 2 kolom list) | Kecil | Field compute baru + 2 atribut XML — **RESOLVED**, dikonfirmasi dev |
| Python (sisanya) | Nol | Tidak ada perubahan wajib lain |
| JS/Owl (sisanya) | Nol | Tidak ada perubahan wajib (`DIFF-06`..`DIFF-10`) |

## 2c. Elemen Tanpa Risiko (kelengkapan cakupan Step 4, 2026-09-22)

> Ditambahkan retroaktif setelah Step 4 (Spec Completeness Review) menemukan 10 file/elemen yang
> belum pernah masuk enumerasi eksplisit `02_DIFF_ANALYSIS.md`/`03_MIGRATION_SPEC.md`. Semua
> dicross-check independen terhadap `native-target` (`odoo20`) dan/atau `git diff migration/19.0` —
> tidak ada indikasi install-blocking atau regresi fungsional. Ditulis di sini murni untuk
> kelengkapan dokumentasi (100% coverage), bukan pekerjaan implementasi baru.

| Elemen | Verifikasi | Kesimpulan |
|---|---|---|
| `models/pos_session.py` | `git diff migration/19.0` kosong; isi hanya komentar sejarah (override lama sudah dihapus sejak migrasi 18.0) | No action needed |
| `views/products.xml` record `product_template_margin_sale_action_server`, `product_product_margin_sale_action_server` | `git diff migration/19.0` kosong; `ref="model_product_template"`/`model_product_product"` XML-ID inti stabil lintas versi | No action needed |
| `views/res_config_settings.xml` | `git diff migration/19.0` kosong; anchor `<block id="pos_interface_section">` dikonfirmasi masih ada di `odoo20/addons/point_of_sale/views/res_config_settings_views.xml:159` | No action needed |
| `wizard/wizard_margin_product.xml` | `git diff migration/19.0` kosong; view form mandiri, tanpa `inherit_id`/anchor eksternal | No action needed |
| `static/tests/tours/margin_threshold_tour.js` | `git diff migration/19.0` kosong; import path (`chrome_util`/`product_screen_util`/`payment_screen_util`/`dialog_util`) dikonfirmasi masih ada persis sama di `odoo20/addons/point_of_sale/static/tests/...` | No action needed |
| `tests/test_margin_threshold_tour.py` | `git diff migration/19.0` kosong; base class `TestPointOfSaleHttpCommon` dikonfirmasi masih ada di `odoo20/addons/point_of_sale/tests/test_frontend.py` | No action needed — tetap baseline eksekusi Step 9 |
| `tests/test_margin_sale.py`, `tests/test_cross_module.py` | `git diff migration/19.0` kosong; test ORM murni, tidak bergantung API versi-spesifik | No action needed — tetap baseline eksekusi Step 9 |
| `demo/demo.xml` | `git diff migration/19.0` kosong; seluruh isi XML comment (sisa scaffold, tidak pernah dipakai) | No action needed |
| `i18n/ar_001.po`, `i18n/es.po`, `i18n/id.po`, `i18n/pt.po` | `git diff migration/19.0` kosong untuk keempatnya; kemungkinan sama nasibnya dengan `fr.po` (orphan entry pasca rename `MF-29`, sudah dicatat non-blocking) | No action needed, konsisten catatan `fr.po` yang sudah ada |

## 3. Data Migration (ringkas — detail di step 7)

N/A — port kode saja, tidak ada data produksi (`01a_MIGRATION_INTAKE.md` §3, Gate Step 1 lulus
2026-09-21 dengan asumsi carried-forward ini dikonfirmasi dev). Step 7 tidak dikerjakan.

## 4. Scope

### Termasuk
- `DIFF-01` — rename + reformat `security/ir.model.access.csv` → `security/ir.access.csv`.
- `DIFF-02` — ganti `ref=` anchor view Product Category.
- `DIFF-03`/`MF-29` — ganti total record `product_variant_easy_edit_view_margin_sale` menjadi
  record baru inherit `product.product_product_tree_view` (XML literal di §2a).
- `__manifest__.py` — bump version `20.0.1.0`, update path data security.
- Review visual Step 10 untuk kolom baru (dicatat eksplisit di keputusan dev `MF-29`).
- Verifikasi cross-module Step 9 (kolom margin tidak dobel kalau `sale_margin_threshold` juga
  terinstall).

### Perlu Konfirmasi (belum final, bukan blocker instalasi)
- **`DIFF-04`** — **✅ DIKONFIRMASI DEV 2026-09-22, DITERAPKAN.** Tambah
  `options="{'currency_field': 'currency_id', 'field_digits': True}"` ke field pengganti
  `list_price` di form Product Template. Diverifikasi live (Docker 19.0 vs 20.0): tidak ada beda
  visual di data instance ini (single-currency) — diterapkan murni sebagai jaga-jaga kompatibilitas
  jangka panjang. Lihat `FINDINGS.md` §`DIFF-04` dan
  `06_implementation/pos_margin_threshold/06c_IMPLEMENTATION_LOG.md`.

### Di Luar Scope (sengaja, disetujui di intake/finding)
- `MF-01`/`BSL-010`, `MF-02`/`BSL-021`, `MF-03`/`BSL-020`, `MF-04`/`BSL-022`, `MF-23`/`BSL-019`,
  `MF-24`/`MF-25` (akar bug `position="replace"` itu sendiri — HANYA ditambal supaya tidak
  memburuk lewat `DIFF-04`, TIDAK diubah jadi `position="attributes"`), typo
  `action_assing_margin` — semua quirk warisan dipertahankan identik, tidak diperbaiki tanpa
  keputusan baru eksplisit dari user.
- `views/product_template_views.xml` (dead file) — tetap mati, tidak dimasukkan ke manifest.
- Gap test AC-02-03/AC-02-04 (`BSL-018`) — carry-forward dua project migrasi sebelumnya, belum ada
  keputusan user untuk project ini (lihat "Ringkasan untuk Review" `01a_MIGRATION_INTAKE.md` poin
  6) — bukan bagian dari migration spec teknis (itu wewenang Step 5 test plan), disebut di sini
  supaya Step 5 tidak menganggap ini otomatis di luar scope.
