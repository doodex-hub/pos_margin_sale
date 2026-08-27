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
| G1 (checkpoint Fase A) | ⏳ Belum dijalankan — lihat "Riwayat Percobaan G1" | — |
| A3 | N/A — ACL wizard sudah ada sejak 17→18, tidak ada model baru di migrasi ini | 2026-08-26 |
| A4 | ✅ — struktur folder diverifikasi konsisten | 2026-08-26 |
| A5 | ✅ | 2026-08-26 |
| B1 | ✅ — model margin/minimum-price diverifikasi tidak butuh perubahan (Step 2/4) | 2026-08-26 |
| B2 | N/A — dikonfirmasi Applicability Check | — |
| C1 | ✅ — tidak ada perubahan, semua `inherit_id` target dikonfirmasi stabil (Step 4) | 2026-08-26 |
| C2 | N/A — dikonfirmasi Applicability Check | — |
| D1 | N/A — dikonfirmasi Applicability Check | — |
| D2 | N/A — dikonfirmasi Applicability Check | — |
| E | ✅ | 2026-08-26 |
| F | N/A — dikonfirmasi Applicability Check | — |
| G2 (validasi akhir/runtime) | ⏳ Menunggu G1 | — |

## Riwayat Percobaan G1 (Install Test)

**Belum dijalankan** — sama seperti `pin_message`, menunggu environment Docker 19.0 dan keputusan
dev soal mode eksekusi + sumber image.

| # | Dijalankan setelah fase | Mode | Hasil | Error (kalau fail) | Tanggal |
|---|---|---|---|---|---|
| 1 | A2 | — | ⏳ Belum dijalankan | — | — |

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
  17→18 dan 18→19; getter pengganti `displayPriceUnit` dipilih berdasarkan analisis semantik Step 2,
  BELUM divalidasi runtime) — **belum divalidasi runtime** (G1/G2, khususnya kedua Tour test
  `margin_threshold_tour.js`, belum jalan).
- **Status:** ✅ Selesai (kode) — ⚠️ Perlu validasi G1/G2 + Tour test re-run (prioritas tinggi,
  ini fitur inti modul)

## [Fase F] Upgrade Template

N/A — dikonfirmasi Applicability Check (Step 2 mengonfirmasi `orderline.xml` tidak butuh perubahan).

## [Fase G2] Validasi Akhir

⏳ Belum dijalankan — menunggu G1 (install test) dan environment Docker 19.0.

---

## Temuan di Luar Spec (kalau ada)

- [x] Tidak ada — semua perubahan kode persis mengikuti `03_MIGRATION_SPEC.md`.

## Kontribusi ke Knowledge Base

- [x] Tidak ada temuan baru — pola porting `getDisplayData()`→getter langsung (dengan getter
  pengganti `get_unit_display_price()`→`displayPriceUnit`) sudah cukup terekam di
  `migration-records/pos-margin-sale_18.0_19.0/SUMMARY.md` dari Step 2; kalau G1/G2 menemukan getter
  pengganti ini SALAH secara semantik (baru bisa dipastikan lewat runtime), akan diupdate sebagai
  entri baru saat itu.
