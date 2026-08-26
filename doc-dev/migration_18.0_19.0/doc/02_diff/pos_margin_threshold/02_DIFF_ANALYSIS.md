# Diff & Compatibility Analysis — pos_margin_threshold

**Step:** 2 — Diff & Compatibility Analysis
**Versi:** 18.0 → 19.0
**Tanggal:** 2026-08-26
**Ref:** `01_intake/pos_margin_threshold/01a_MIGRATION_INTAKE.md`, `migration-tool/knowledge/`

---

## 0. Knowledge Base Check

| Sumber | Sudah ada entry? | Lokasi |
|---|---|---|
| `version-diffs/18-to-19.md` | Ya (riset umum, tidak spesifik `point_of_sale`) | `migration-tool/knowledge/version-diffs/18-to-19.md` |
| `dependency-compat/point_of_sale/18-to-19.md` | **Tidak ada** — modul ini yang menghasilkan riset pertama untuk `point_of_sale` 18→19 lewat tool ini | — (kandidat baru, lihat §3) |

## 0b. Gate Community vs Enterprise

Dependency map `01a_MIGRATION_INTAKE.md` §2: `base`, `point_of_sale`, `product`, `stock_account` —
**semua Native Community, tidak ada baris Enterprise**. Cukup `native-target` Community
(`enterprise19.0`, yang juga berisi Community di `odoo/addons/`) — tidak perlu cross-check
Enterprise untuk modul ini.

- [x] Dicek langsung ke `native-source` (`D:\Kuncoro\doodex\repo\odoo18`, `point_of_sale` di
  `addons/point_of_sale/`) DAN `native-target` (`D:\Kuncoro\doodex\repo\enterprise19.0`,
  `point_of_sale` di `odoo/addons/point_of_sale/`) — bukan diasumsikan.

## 0c. Gate Transitive Dependency

Tidak ada `depends` yang diusulkan dihapus untuk modul ini di titik ini — gate ini N/A untuk Step 2
kali ini.

---

## 1. Perubahan Native (Core/Enterprise)

| ID | File/simbol modul | Simbol native terkait | Status di target | Dampak | Sumber |
|---|---|---|---|---|---|
| DIFF-01 | `static/src/store/models/models.js:5` `import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline"` | `point_of_sale/static/src/app/generic_components/orderline/orderline.js` | **Dihapus/Rename path** — seluruh folder `generic_components/` di-rename jadi `components/` di 19.0 (semua subfolder ikut pindah: `product_card`, `numpad`, `popups/*`, dst). Path baru: `@point_of_sale/app/components/orderline/orderline` | **Tinggi** — import akan gagal resolve, modul tidak akan load sama sekali kalau path tidak diupdate | Analisis baru (agent Step 2) |
| DIFF-02 | `static/src/store/pos_store.js:2` `import { PosStore } from "@point_of_sale/app/store/pos_store"` | `point_of_sale/static/src/app/store/pos_store.js` | **Pindah** — file dipindah ke `app/services/pos_store.js`, base class berubah `Reactive`→`WithLazyGetterTrap`. `pay()` tetap ada, tetap jadi entry-point pembayaran, signature sama (tanpa argumen) | **Tinggi** — import gagal resolve tanpa path baru | Analisis baru |
| DIFF-03 | `static/src/store/pos_store.js:6` `import { ask } from "@point_of_sale/app/store/make_awaitable_dialog"` | `point_of_sale/static/src/app/store/make_awaitable_dialog.js` | **Pindah** — ke `app/utils/make_awaitable_dialog.js`. Isi fungsi `ask()` byte-identik, cuma lokasi file berubah | **Tinggi** — import gagal resolve tanpa path baru | Analisis baru |
| DIFF-04 | `static/src/store/pos_store.js:7` `import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog"` | `web/static/src/core/confirmation_dialog/confirmation_dialog.js` | **Tidak berubah** — path dan definisi class `ConfirmationDialog`/`AlertDialog` identik di 18.0 dan 19.0 | — | Analisis baru |
| DIFF-05 | `models/product.py:103-107` `_load_pos_data_fields(self, config_id)` (override `product.product`) | `point_of_sale/models/product.py` (18.0) → `point_of_sale/models/product_product.py` (19.0) | **Signature berubah** — parameter di-rename `config_id`→`config`, TIPE berubah dari `int` (id) jadi recordset `pos.config`. Override modul ini hanya meneruskan parameter ke `super()` tanpa dereference — **tetap berfungsi tanpa perubahan kode**, tapi nama variabel lokal jadi menyesatkan (`config_id` sebenarnya berisi record, bukan id) | Rendah (fungsional tetap jalan) — direkomendasikan rename param demi kejelasan, bukan wajib | Analisis baru |
| DIFF-06 | `static/src/store/models/models.js:12-16` `patch(Orderline.props.line.shape, {minimumSalePrice, minimumSalePriceWithTax, isLessMinimumSalePrice})` | `Orderline` component props (`app/generic_components/orderline/orderline.js` di 18.0) | **DIHAPUS TOTAL** — di 19.0, `Orderline.props.line` didefinisikan sebagai `Object` polos, TIDAK ADA `.shape` sama sekali. `line` sekarang adalah record `PosOrderline` LIVE, bukan objek display-data hasil `getDisplayData()`. `patch(Orderline.props.line.shape, {...})` akan **crash saat load** (`patch()` butuh target object, `.shape` adalah `undefined`) | **KRITIS — install/load-blocking** | Analisis baru |
| DIFF-07 | `static/src/store/models/models.js:35-43` `patch(PosOrderline.prototype, {getDisplayData() {...}})` | `PosOrderline.prototype.getDisplayData()` (18.0) | **DIHAPUS TOTAL** — method ini tidak ada lagi DI MANAPUN di addon 19.0 (grep penuh: 0 match). `Orderline` 19.0 membaca getter LANGSUNG dari record (`line.getQuantityStr()`, `line.currencyDisplayPrice`, dst), bukan dari objek hasil `getDisplayData()` | **KRITIS** — patch ini jadi no-op total di 19.0, `minimumSalePriceWithTax`/`isLessMinimumSalePrice` TIDAK PERNAH sampai ke component | Analisis baru |
| DIFF-08 | `static/src/store/pos_store.js:12-15` `this.get_order()`, `.get_orderlines()`, `line.get_unit_display_price()`, `.get_product()` | `PosStore`/`PosOrderline`/`ProductProduct` method names | **Rename massal snake_case→camelCase** di seluruh POS 19.0: `get_order`→`getOrder`, `get_orderlines`→`getOrderlines`, `get_product`→`getProduct`, `set_unit_price`→`setUnitPrice`. `get_unit_display_price` KHUSUSNYA tidak ada penggantinya dengan nama persis — fungsinya kini tersebar di getter `displayPriceUnit`/`currencyDisplayPriceUnit` pada base class baru `PosOrderlineAccounting` | **Tinggi — install/runtime-blocking** (`AttributeError`/`undefined is not a function` begitu `pay()` dipanggil) | Analisis baru |
| DIFF-09 | `static/src/store/models/models.js:20-26` `patch(ProductProduct.prototype, {get_minimum_sale_price(), get_minimum_sale_price_with_tax()})` dan `static/src/store/models/models.js:30` `patch(PosOrderline.prototype, {set_unit_price(price) {super.set_unit_price(price)}})` | `ProductProduct`/`PosOrderline` method naming convention | Method BARU yang didefinisikan modul ini sendiri (`get_minimum_sale_price`/`_with_tax`) tetap bisa dipakai dengan nama snake_case apapun (tidak override core) — **tidak masalah**. Tapi `set_unit_price` yang di-OVERRIDE (`super.set_unit_price`) targetnya sudah di-rename core jadi `setUnitPrice` — override snake_case ini jadi method BARU terpisah, bukan override sungguhan, dan `super.set_unit_price` akan error (method tidak ada di parent) | **Tinggi** | Analisis baru |
| DIFF-10 | `static/src/store/orderline.xml` xpath `//li[contains(@class,'orderline')]//ul[hasclass('info-list')]/t[@t-slot='default']` | Template `Orderline` (`orderline.xml`) | **Tidak berubah struktural** — `<ul class="info-list">` tetap descendant dari `<li class="orderline">` (di dalam wrapper `<div>` baru, sama pola seperti fix 17→18), `<t t-slot="default">` tetap child terakhir. Xpath descendant modul ini (bukan direct-child) TETAP MATCH tanpa perubahan | Rendah — perlu smoke-test kombinasi `class`+`t-att-class`+`t-attf-class` di elemen `<li>` (baru muncul kombinasi 3 arah di 19.0), tapi struktural aman | Analisis baru |

## 2. Kompatibilitas Dependency (OCA/Third-Party)

Tidak ada — dikonfirmasi dev tidak ada dependency OCA/third-party di project ini (lihat
`01a_MIGRATION_INTAKE.md` §0).

## 3. Temuan Baru — Kandidat Migration Records

- [x] **Ditulis ke `migration-tool/migration-records/pos-margin-sale_18.0_19.0/SUMMARY.md`** (kategori
  `dependency-compat`, `point_of_sale` 18→19) — lihat file itu untuk detail lengkap siap-curation.
  Ringkasan: `point_of_sale` JS mengalami restrukturisasi besar KEDUA kalinya berturut-turut
  (setelah 17→18): folder `generic_components/`→`components/`, `app/store/`→`app/services/`+
  `app/utils/`+`app/components/popups/`, rename massal method snake_case→camelCase, DAN
  penghapusan total mekanisme `Orderline.props.line.shape`/`getDisplayData()` (diganti getter
  langsung di record model). Ini pola breaking-change paling agresif yang ditemukan sejauh ini
  lintas project migrasi manapun via tool ini.

## 4. Ringkasan Risiko

| Item | Level risiko | Catatan |
|---|---|---|
| `DIFF-01`/`DIFF-02`/`DIFF-03` (import path pindah) | Tinggi | Mekanis — perbaikan pindah path 3 import statement, pola sama seperti fix `MF-12`/17→18 |
| `DIFF-06` (`Orderline.props.line.shape` dihapus) | **Kritis** | Modul akan **crash saat load** di 19.0 tanpa fix — bukan cuma silent-fail, ini blocker install/run total untuk fitur JS |
| `DIFF-07` (`getDisplayData()` dihapus) | **Kritis** | Fitur utama (highlight harga di bawah minimum di orderline POS) jadi **non-fungsional total** tanpa porting ke pola getter baru — TIDAK crash, tapi silent-fail (fitur hilang tanpa error) |
| `DIFF-08`/`DIFF-09` (rename method core) | Tinggi | `pay()` override akan **crash saat dipanggil** (`this.get_order is not a function` dkk) — blocking fitur inti (validasi margin saat bayar) |
| `DIFF-05` (`_load_pos_data_fields` signature) | Rendah | Tetap fungsional tanpa perubahan kode, cuma nama variabel menyesatkan |
| `DIFF-10` (xpath `orderline.xml`) | Rendah | Struktural tetap match, cuma perlu smoke-test kombinasi class attribute baru |

**Kesimpulan Step 2 modul ini:** SELURUH lapisan JS/Owl modul ini (`models.js`, `pos_store.js`) butuh
port substansial di Step 6 — bukan sekadar update path import, tapi porting `getDisplayData()`
menjadi getter langsung di `PosOrderline`, mengganti seluruh pemanggilan method snake_case jadi
camelCase, dan mencari pengganti `get_unit_display_price` di base class accounting baru. `orderline.xml`
dan dialog service relatif aman (cukup update path import). Prioritas Step 3 (migration spec):
`DIFF-06`/`DIFF-07`/`DIFF-08`/`DIFF-09` adalah blocker fungsional, harus diselesaikan sebelum modul
ini bisa lulus G1 (install test) di Step 6.
