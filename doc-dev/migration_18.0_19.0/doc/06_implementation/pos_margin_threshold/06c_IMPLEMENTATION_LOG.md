# Implementation Log — pos_margin_threshold

**Step:** 6 — Code Migration
**Ref:** `03_spec/pos_margin_threshold/03_MIGRATION_SPEC.md`, `migration-tool/templates/06a_CODE_MIGRATION_PHASES.md`
**Tanggal:** 2026-08-26

---

## Applicability Check

Sumber: `01a_MIGRATION_INTAKE.md` §2b.

| Fase | Relevan? | Bukti/alasan (dari `01a` §2b) |
|---|---|---|
| B2 (Model Kompleks) | ☐ Tidak | Tidak ada JSON/relasi berantai/dynamic model creation di `models/product.py` dkk |
| C2 (Semantik XML & UX) | ☐ Tidak | View pakai syntax modern `invisible=`/`decoration-*=` (bukan `attrs=` legacy), dikonfirmasi Step 4 seluruh `inherit_id` target stabil di 19.0 tanpa perubahan syntax |
| D1 (Controllers) | ☐ Tidak | `controllers/controllers.py` dead scaffold (semua di-comment), tidak disentuh |
| D2 (Assets & CSS Stabilization) | ☐ Tidak | Path asset `assets.point_of_sale._assets_pos`/`web.assets_tests` tidak berubah |
| E (JavaScript/Owl) | ☑ **Ya** | `static/src/store/{models/models.js,pos_store.js}` — area kerja utama (`DIFF-01/02/03/06/07/08/09`) |
| F (Upgrade Template) | ☐ Tidak | Step 2 mengonfirmasi `orderline.xml` (`DIFF-10`) tidak butuh perubahan syntax |

---

## Tabel Ringkas Status Fase

| Fase | Status | Tanggal |
|---|---|---|
| A1 | ✅ | 2026-08-26 |
| A2 | N/A — tidak ada `<tree>` tersisa (sudah `<list>` sejak 17→18, dikonfirmasi grep bersih) | 2026-08-26 |
| G1 (checkpoint Fase A) | ✅ **Pass** (2026-08-27) | 2026-08-27 |
| A3 | N/A — ACL wizard sudah ada sejak 17→18, tidak ada model baru di migrasi ini | 2026-08-26 |
| A4 | ✅ — struktur folder diverifikasi konsisten | 2026-08-26 |
| A5 | ✅ | 2026-08-26 |
| B1 | ✅ — model margin/minimum-price diverifikasi tidak butuh perubahan (Step 2/4) | 2026-08-26 |
| B2 | N/A — dikonfirmasi Applicability Check | — |
| C1 | ✅ — tidak ada perubahan, semua `inherit_id` target dikonfirmasi stabil (Step 4) | 2026-08-26 |
| C2 | N/A — dikonfirmasi Applicability Check | — |
| D1 | N/A — dikonfirmasi Applicability Check | — |
| D2 | N/A — dikonfirmasi Applicability Check | — |
| E | ✅ — logic `models.js`/`pos_store.js` divalidasi BENAR lewat Tour test (lihat G2) | 2026-08-26 |
| F | N/A — dikonfirmasi Applicability Check | — |
| G2 (validasi akhir/runtime) | ✅ **Pass (0 failed, 0 error dari 17 test, termasuk 2 Tour test browser asli), setelah 1 fix tambahan (test-tour util import path)** | 2026-08-27 |

## Riwayat Percobaan G1 (Install Test) + G2 (Tour test, Mode D)

Mode C (AI jalankan langsung), image `odoo:19.0` (sudah ada lokal).

| # | Dijalankan setelah fase | Mode | Hasil | Error (kalau fail) | Tanggal |
|---|---|---|---|---|---|
| 1 | A5 (install polos, bersama 2 modul lain) | C | ✅ Pass | — (2 fix ditemukan, tapi di `sale_margin_threshold`, tidak terkait modul ini — lihat log modul itu) | 2026-08-27 |
| 2 | E (`--test-enable`, Tour test) | C | ❌ **Fail 2** | Kedua Tour test (`test_pos_margin_threshold_below_minimum_confirm_tour`,
`test_pos_margin_threshold_below_minimum_blocked_tour`): "The ready `odoo.isTourReady(...)` code was
always falsy". **BUKAN bug di `models.js`/`pos_store.js`** (POS webclient terbukti load bersih di log
— banyak request sukses, Owl start normal) — root cause: `static/tests/tours/margin_threshold_tour.js`
mengimpor util test dari path LAMA (`@point_of_sale/../tests/tours/utils/{chrome_util,dialog_util,
product_screen_util,payment_screen_util}`) yang di 19.0 sudah PINDAH
(`chrome_util`/`product_screen_util`/`payment_screen_util` → `tests/pos/tours/utils/`; `dialog_util`
→ keluar dari `tours/` sepenuhnya, ke `tests/generic_helpers/`). Import gagal resolve → tour file
gagal load → `registry.category("web_tour.tours").add(...)` tidak pernah jalan → nama tour tidak
pernah terdaftar → `isTourReady` untuk nama itu tidak pernah true. **Ini area yang TIDAK dicek Step 2**
(fokus Step 2 ke kode produksi, bukan test-tour util import) — pelajaran baru: util test tour JUGA
ikut direstrukturisasi Odoo 19.0, bukan cuma kode produksi. | 2026-08-27 |
| 3 | E (setelah fix #2) | C | ✅ **Pass** | — 0 failed, 0 error dari 17 test `pos_margin_threshold`
(naik dari gagal total) — MEMBUKTIKAN getter pengganti (`displayPriceUnit`, dst) yang dipilih di
Fase E (lihat entri di bawah) benar SECARA SEMANTIK, bukan cuma benar sintaks; kedua Tour test
"tour succeeded" end-to-end (jual produk di bawah minimum → dialog muncul dengan teks benar →
confirm/block → hasil sesuai skenario). | 2026-08-27 |

---

## Entri

## [Fase A1] Manifest Bootstrap

- **Scope:** `pos_margin_threshold/__manifest__.py`
- **Aksi:** `version` `'18.0.1.0'` → `'19.0.1.0'`.
- **Secara eksplisit TIDAK dilakukan:** tidak ada perubahan `depends`/`data`/`assets` lain.
- **Risiko:** LOW
- **Status:** ✅ Selesai

## [Fase A2] XML Tree → List

N/A — tidak ada `<tree>` tersisa di modul ini (dikonfirmasi grep, sudah `<list>` sejak migrasi
17→18).

## [Fase A3] Security Hardening

N/A — `security/ir.model.access.csv` sudah mencakup `wizard.margin.product` sejak 17→18, tidak ada
model baru di migrasi 18→19 ini.

## [Fase A4] Skeleton & Folder Integrity

- **Aksi:** diverifikasi — struktur folder konsisten, tidak ada yang perlu diubah.
- **Risiko:** LOW
- **Status:** ✅ Selesai

## [Fase A5] Python API Compatibility

- **Scope:** `models/product.py`, `models/pos_config.py`, `models/pos_session.py`,
  `models/res_config_settings.py`, `wizard/wizard_margin_product.py`
- **Item spec (ref):** `03_MIGRATION_SPEC.md` §2 baris `_load_pos_data_fields` (`DIFF-05`).
- **Aksi:** diverifikasi — TIDAK ADA perubahan kode Python. `_load_pos_data_fields(self, config_id)`
  tetap berfungsi tanpa modifikasi walau core 19.0 me-rename parameter internal (`config_id`→`config`)
  dan mengubah tipenya (int→recordset) — override modul ini hanya meneruskan `config_id` ke `super()`
  tanpa dereference, jadi netral terhadap perubahan itu (dikonfirmasi Step 2/3). Nama parameter lokal
  SENGAJA dibiarkan `config_id` (bukan direname `config`) — mengubah nama parameter tanpa perlu
  fungsional dianggap di luar scope port minimal.
- **Risiko:** LOW
- **Status:** ✅ Selesai (tidak ada perubahan diperlukan)

## [Fase B1] Model Risiko Rendah

- **Scope:** semua model Python modul ini.
- **Aksi:** diverifikasi ulang — tidak ada perubahan.
- **Risiko:** LOW
- **Status:** ✅ Selesai

## [Fase B2] Model Kompleks

N/A — dikonfirmasi Applicability Check.

## [Fase C1] View Sederhana

- **Scope:** `views/products.xml`, `views/res_config_settings.xml`
- **Aksi:** diverifikasi ulang (bukan diubah) — keempat `inherit_id` target
  (`stock_account.view_category_property_form_stock`, `product.product_template_form_view`,
  `product.product_variant_easy_edit_view`, `point_of_sale.res_config_settings_view_form`) dan field
  anchor di dalamnya dikonfirmasi stabil di 19.0 (Step 4, `04_SPEC_COMPLETENESS_REVIEW.md`).
- **Secara eksplisit TIDAK dilakukan:** `views/product_template_views.xml` (dead file, `MF-04`) TETAP
  tidak dimuat — tidak diaktifkan, tidak dihapus.
- **Risiko:** LOW
- **Status:** ✅ Selesai (tidak ada perubahan kode diperlukan)

## [Fase C2] Semantik XML & Konsistensi UX

N/A — dikonfirmasi Applicability Check.

## [Fase D1] Controllers

N/A — dikonfirmasi Applicability Check.

## [Fase D2] Assets & CSS Stabilization

N/A — dikonfirmasi Applicability Check.

## [Fase E] JavaScript (Owl versi baru)

- **Scope:** `static/src/store/models/models.js`, `static/src/store/pos_store.js`
- **Item spec (ref):** `03_MIGRATION_SPEC.md` §2 baris `DIFF-01`/`02`/`03`/`06`/`07`/`08`/`09`, §2b
  Critical Blockers #2/#3, ref `FINDINGS.md` `MF-12`/`MF-13`.
- **Aksi:**
  - `models/models.js`:
    - Import `Orderline` (`@point_of_sale/app/generic_components/orderline/orderline`) DIHAPUS
      sepenuhnya — hanya dipakai untuk patch `props.line.shape` yang juga dihapus.
    - `patch(Orderline.props.line.shape, {...})` DIHAPUS TOTAL (`DIFF-06`) — mekanisme ini tidak ada
      lagi di 19.0.
    - `patch(PosOrderline.prototype, {...})`: `set_unit_price(price)` → `setUnitPrice(price)`
      (`DIFF-09`, passthrough murni, `super()` dipanggil dengan nama baru).
    - `getDisplayData()` override DIHAPUS (`DIFF-07`), diganti DUA getter baru langsung di
      `PosOrderline`: `get minimumSalePriceWithTax()` dan `get isLessMinimumSalePrice()` — nilai
      dihitung persis sama seperti sebelumnya (`formatCurrency(product.get_minimum_sale_price_with_tax(), this.currency)`
      dan `displayPriceUnit < product.get_minimum_sale_price_with_tax()`), cuma sumber
      `get_unit_display_price()` diganti getter core baru `displayPriceUnit` (dikonfirmasi Step 2:
      `displayPriceUnit` toggle `iface_tax_included`, semantik identik dengan
      `get_unit_display_price()` 18.0) dan `get_product()`→`getProduct()`.
    - `patch(ProductProduct.prototype, {get_minimum_sale_price, get_minimum_sale_price_with_tax})`
      TIDAK diubah — dua method custom modul ini sendiri, tidak terpengaruh rename core.
  - `pos_store.js`:
    - Import `PosStore`: `@point_of_sale/app/store/pos_store` → `@point_of_sale/app/services/pos_store`
      (`DIFF-02`).
    - Import `ask`: `@point_of_sale/app/store/make_awaitable_dialog` → `@point_of_sale/app/utils/make_awaitable_dialog`
      (`DIFF-03`).
    - Import `AlertDialog` (`@web/core/confirmation_dialog/confirmation_dialog`) TIDAK diubah
      (`DIFF-04`, path stabil).
    - Dalam `pay()`: `this.get_order()`→`this.getOrder()`, `.get_orderlines()`→`.getOrderlines()`,
      `line.get_unit_display_price()`→`line.displayPriceUnit` (getter, bukan lagi method call),
      `line.get_product()`→`line.getProduct()` (`DIFF-08`). Logic pengecekan margin, dialog
      confirm/alert, dan `super.pay(...)` TIDAK diubah sama sekali — cuma nama method/getter yang
      di-update.
- **Secara eksplisit TIDAK dilakukan:**
  - `minimumSalePrice` (tanpa tax) dari `getDisplayData()` lama SENGAJA TIDAK diporting jadi getter
    baru — dikonfirmasi tidak dipakai template manapun (`orderline.xml` cuma baca
    `isLessMinimumSalePrice`/`minimumSalePriceWithTax`), jadi tidak ada fungsi yang hilang.
  - `orderline.xml` TIDAK disentuh — dikonfirmasi Step 2 xpath tetap match tanpa perubahan
    (`DIFF-10`).
  - Tidak ada perubahan pada logic bisnis (kondisi blocking/confirm, threshold, dst) — HANYA nama
    method/getter yang diadaptasi ke API 19.0.
- **Risiko:** MEDIUM-HIGH (area yang sudah dua kali mengalami restrukturisasi besar berturut-turut,
  17→18 dan 18→19; getter pengganti `displayPriceUnit` dipilih berdasarkan analisis semantik Step 2).
- **Status:** ✅ Selesai — **divalidasi 2 Tour test browser asli, PASS** ("tour succeeded" untuk
  jalur confirm maupun blocked). Getter pengganti `displayPriceUnit`/`getProduct()`/`getOrder()`/
  `getOrderlines()` terbukti benar secara semantik, bukan cuma benar sintaks.

## [Fase E — tambahan] Perbaikan Test-Tour Util Import Path

- **Scope:** `static/tests/tours/margin_threshold_tour.js` (file test, bukan kode produksi — tetap
  bagian Step 6 karena test yang tidak bisa load = tidak ada bukti fitur berfungsi).
- **Item spec (ref):** TIDAK ADA di `03_MIGRATION_SPEC.md`/`02_DIFF_ANALYSIS.md` — **ditemukan lewat
  G2/Tour test (2026-08-27), bukan Step 2/3** (lihat "Riwayat Percobaan G1" #2, "Temuan di Luar
  Spec" di bawah).
- **Aksi:** 4 import statement diperbaiki:
  - `@point_of_sale/../tests/tours/utils/chrome_util` → `@point_of_sale/../tests/pos/tours/utils/chrome_util`
  - `@point_of_sale/../tests/tours/utils/dialog_util` → `@point_of_sale/../tests/generic_helpers/dialog_util`
    (pindah KELUAR dari `tours/`, bukan cuma nested lebih dalam)
  - `@point_of_sale/../tests/tours/utils/product_screen_util` → `@point_of_sale/../tests/pos/tours/utils/product_screen_util`
  - `@point_of_sale/../tests/tours/utils/payment_screen_util` → `@point_of_sale/../tests/pos/tours/utils/payment_screen_util`
  - Nama fungsi yang dipakai (`startPoS`, `endTour`, `confirm`, `is`, `bodyIs`, `isShown`,
    `addOrderline`, `clickPayButton`, `clickPaymentMethod`, `clickValidate`) dikonfirmasi TIDAK
    berubah nama/signature di 19.0 — HANYA lokasi file yang berubah.
- **Secara eksplisit TIDAK dilakukan:** isi tour steps (`Chrome.startPoS()`, dst) tidak diubah sama
  sekali — cuma baris import di paling atas file.
- **Risiko:** LOW (mekanis) — divalidasi langsung G2 PASS.
- **Status:** ✅ Selesai

## [Fase F] Upgrade Template

N/A — dikonfirmasi Applicability Check (Step 2 mengonfirmasi `orderline.xml` tidak butuh perubahan).

## [Fase G2] Validasi Akhir

✅ **Pass (2026-08-27)**, setelah fix test-tour util import path di atas — `docker compose up`
dengan `--test-enable --test-tags=/pos_margin_threshold` (dan dua modul lain sekaligus): **0 failed,
0 error dari 17 test**, termasuk kedua Tour test browser asli ("tour succeeded" untuk jalur confirm
maupun blocked). Kriteria minimal G2 terpenuhi: tidak ada warning server saat start, tidak ada error
console browser, `DIFF-06`/`07`/`08`/`09` (area paling berisiko project ini) terkonfirmasi valid di
runtime nyata.

---

## Temuan di Luar Spec (kalau ada)

- [x] **Ada** — `03_MIGRATION_SPEC.md`/`02_DIFF_ANALYSIS.md` tidak mencakup import test-tour util
  (`static/tests/tours/margin_threshold_tour.js`), karena Step 2 fokus ke kode produksi. Baru
  ketahuan lewat G2. Tidak perlu balik ke Step 3/4 (dampak kecil, mekanis, sudah divalidasi PASS) —
  dicatat di sini + `FINDINGS.md` (`MF-19`) untuk jejak lengkap.

## Kontribusi ke Knowledge Base

- [x] **Ada** — restrukturisasi path util test-tour `point_of_sale` (`tests/tours/utils/`→
  `tests/pos/tours/utils/` + `dialog_util` pindah ke `tests/generic_helpers/`) adalah temuan BARU,
  terpisah dari restrukturisasi kode produksi yang sudah dicatat Step 2. Relevan untuk modul CUSTOM
  APAPUN yang punya Tour test sendiri untuk `point_of_sale`. Dicatat ke
  `migration-records/pos-margin-sale_18.0_19.0/SUMMARY.md`.
