# Implementation Log — pos_margin_threshold

**Step:** 6 — Code Migration
**Ref:** `03_spec/pos_margin_threshold/03_MIGRATION_SPEC.md`, `migration-tool/templates/06a_CODE_MIGRATION_PHASES.md`
**Tanggal:** 2026-08-24

---

## Applicability Check

| Fase | Relevan? | Bukti/alasan (dari `01a` §2b) |
|---|---|---|
| C1 | ☑ Ya | Modul punya `views/` (3 file XML, inherit ke form produk/settings) |
| B2 | ☐ Tidak | Tidak ada field JSON/relasi berantai/dynamic model creation |
| C2 | ☑ Ya | `invisible="product_variant_count > 1 and not is_product_variant"` — ekspresi dinamis di `views/products.xml`/`product_template_views.xml` |
| D1 | ☐ Tidak | `controllers/controllers.py` seluruh isi di-comment, dead scaffold |
| D2 | ☑ Ya | `assets.point_of_sale._assets_pos` — JS/XML custom nyata |
| E | ☑ Ya | `static/src/store/{models/models,pos_store}.js` — patch prototype `Product`/`Orderline`/`Order`/`PosStore` |
| F | ☑ Ya | `static/src/store/orderline.xml` — `t-inherit="point_of_sale.Orderline"` (QWeb Owl template) |

---

## Tabel Ringkas Status Fase

| Fase | Status | Tanggal |
|---|---|---|
| A1 | ✅ | 2026-08-24 |
| A2 | ✅ (N/A — tidak ada `<tree>` di modul ini, dikonfirmasi Step 2 DIFF-01) | 2026-08-24 |
| G1 (setelah A2/A3) | ✅ Pass (lihat "Riwayat Percobaan G1") | 2026-08-24 |
| A3 | ✅ (sudah compliant — ACL wizard sudah ada sejak 17.0) | 2026-08-24 |
| A4 | ✅ (struktur folder konsisten, tidak ada perubahan diperlukan) | 2026-08-24 |
| A5 | ✅ (tidak ada `create()`/API ORM yang berubah, dikonfirmasi Step 2 DIFF-08) | 2026-08-24 |
| B1 | ✅ (model sederhana, tidak ada perubahan diperlukan) | 2026-08-24 |
| B2 | N/A — dikonfirmasi Applicability Check | — |
| C1 | ✅ (tidak ada perubahan diperlukan, tidak ada `<tree>`, xpath tidak diketahui berubah dari analisis statis) | 2026-08-24 |
| C2 | ✅ (ekspresi `invisible=` sudah sintaks modern, tidak ada perubahan diperlukan) | 2026-08-24 |
| D1 | N/A — dikonfirmasi Applicability Check | — |
| D2 | ✅ (asset key valid, folder eksis, tidak ada perubahan diperlukan) | 2026-08-24 |
| E | ✅ **SELESAI PENUH, TERVERIFIKASI TOUR TEST NYATA** — 4 fix wajib ditemukan+diperbaiki (`MF-13`, `MF-15`, `MF-16`, `MF-17`), lihat entri Fase E | 2026-08-24 |
| F | ✅ **SELESAI PENUH, TERVERIFIKASI TOUR TEST NYATA** — 2 fix wajib (`MF-19`, `MF-20`), lihat entri Fase F | 2026-08-24 |
| G2 (validasi akhir/runtime) | ✅ **SELESAI** — Tour test Mode D (Chrome asli, Docker) menjalankan alur penuh: buka POS → jual produk di bawah minimum → dialog muncul → confirm → bayar → sukses. "tour succeeded", 0 failed/0 error dari 18 test total. | 2026-08-24 |

## Riwayat Percobaan G1 (Install Test)

> Dijalankan sekaligus untuk ketiga modul (satu instance Docker `docker-env/docker-compose.yml`,
> image `odoo:18.0`, `-i pos_margin_threshold,sale_margin_threshold,pin_message --stop-after-init`)
> — hasil per-modul dicatat di log implementasi masing-masing. Command benar-benar dijalankan lewat
> Bash (Mode C), bukan diasumsikan — lihat `docker-env/logs/odoo.log` (timestamp `2026-08-24`).

| # | Dijalankan setelah fase | Mode | Hasil | Error (kalau fail) | Tanggal |
|---|---|---|---|---|---|
| 1 | A1+A2 (ketiga modul) | C | ✅ **Pass** — exit code 0, `pos_margin_threshold` loaded di posisi 59/67, "Modules loaded", "Registry loaded in 52.925s" | Tidak ada error/traceback dari modul ini secara spesifik di log. G1 konfirmasi backend (Python/security/XML `ir.ui.view`) parse & load bersih — TIDAK otomatis membuktikan JS. | 2026-08-24 |
| 2 | Setelah fix `MF-13` (dialog service) — SEBELUM `MF-15`/`MF-16` ditemukan | C | ✅ Pass (install) | Install tetap sukses (blocker install tetap N/A) — TAPI ini titik di mana kesimpulan "G1 pass = aman" terbukti keliru: `MF-15`/`MF-16` (arsitektur data model + entry point pay() pindah total) baru ketahuan belakangan dari Tour test, TIDAK dari G1 manapun | 2026-08-24 |
| 3 | Setelah fix `MF-15`/`MF-16`/`MF-17`/`MF-18` (rewrite arsitektur) | C | ✅ Pass (17 test lama, termasuk backend `pos_margin_threshold` 13 test) | Test lama (non-Tour) semua pass — belum mencakup Tour baru | 2026-08-24 |
| 4 | Tour test pertama ditulis, sebelum fix `MF-19` | C | ❌ Fail | `OwlError: Invalid props for component 'Orderline': ... unknown key 'minimumSalePrice'...` — Owl validasi strict shape | 2026-08-24 |
| 5 | Setelah fix `MF-19` (props shape) | C | ❌ Fail | `Error: Element '<xpath expr="...">' cannot be located in element tree` — `MF-20` (xpath direct-child) | 2026-08-24 |
| 6 | Setelah fix `MF-20` (xpath descendant) | C | ❌ Fail (tour timeout, BUKAN error kode) | Tour timeout di step "now in payment screen" — bukan bug modul, tapi tour test SAYA sendiri salah asumsi urutan step (`clickPayButton()` helper punya built-in wait yang konflik dengan dialog kita) | 2026-08-24 |
| 7 | Setelah fix urutan step Tour (`clickPayButton(false)` + wait manual) | C | ✅ **PASS PENUH** — "tour succeeded", **0 failed, 0 error(s) of 18 tests** | — | 2026-08-24 |

**Kesimpulan penting dari 7 percobaan di atas:** G1 (install, `-i ... --stop-after-init`) **TIDAK CUKUP** untuk modul dengan Owl/JS kompleks — percobaan #2 install sukses padahal ADA 2 bug kritis (`MF-15`/`MF-16`) yang bikin seluruh fitur JS modul ini crash/mati total begitu benar-benar dipakai. Baru ketahuan dari Tour test nyata (Mode D, percobaan #4-7). Ini validasi konkret kenapa disiplin G1≠G2≠review-statis (`USAGE_GUIDE.md`) penting — bukan formalitas.

---

## Entri

## [Fase A1] Manifest Bootstrap

- **Scope:** `__manifest__.py`
- **Item spec (ref):** `03_MIGRATION_SPEC.md` §2 baris terakhir
- **Aksi:**
  - `__manifest__.py`: `version: '17.0.1.0'` → `'18.0.1.0'`
- **Secara eksplisit TIDAK dilakukan:** tidak ada perubahan `depends`/`data`/`assets` — manifest tetap merepresentasikan modul penuh (P4)
- **Risiko:** LOW
- **Status:** ✅ Selesai

## [Fase A2] XML Tree → List (Mekanis)

N/A — dikonfirmasi Applicability Check tidak berlaku (tidak ada tag `<tree>` di modul ini sama sekali, dikonfirmasi Step 2 `02_DIFF_ANALYSIS.md` DIFF-01).

## [Fase A3] Security Hardening

- **Scope:** `security/ir.model.access.csv`
- **Aksi:** Dicek — ACL untuk `wizard.margin.product` (TransientModel) sudah ada sejak 17.0 (`access_wizard_margin_product`, `base.group_user`, full CRUD). Tidak perlu perubahan.
- **Secara eksplisit TIDAK dilakukan:** tidak ada penambahan/perubahan baris ACL
- **Risiko:** LOW
- **Status:** ✅ Selesai (sudah compliant tanpa perubahan)

## [Fase A4] Skeleton & Folder Integrity

- **Scope:** struktur folder keseluruhan
- **Aksi:** Dicek — struktur `models/`, `views/`, `controllers/`, `static/`, `security/`, `wizard/`, `demo/`, `i18n/`, `tests/` konsisten, semua `__init__.py` ada.
- **Status:** ✅ Selesai (tidak ada perubahan diperlukan)

## [Fase A5] Python API Compatibility

- **Scope:** `models/**/*.py`, `wizard/**/*.py`
- **Aksi:** Dicek terhadap `knowledge/version-diffs/17-to-18.md` §1 — tidak ada `user_has_groups`, `_name_search`, `_check_recursion`, override `search()`, atau `create()` single-record di modul ini. Semua compute/inverse pattern (`@api.depends`, `readonly=False` + `store=True`) tidak termasuk API yang diketahui berubah.
- **Status:** ✅ Selesai (tidak ada perubahan diperlukan)

## G1 — Install Test #1 (setelah A1+A2, ketiga modul sekaligus)

- **Command:** `docker compose -f docker-env/docker-compose.yml up` (image `odoo:18.0`, `-i pos_margin_threshold,sale_margin_threshold,pin_message --stop-after-init`)
- **Mode:** C (AI jalankan langsung via Bash, Claude Code CLI)
- **Hasil nyata (bukan dugaan):** exit code 0. `odoo.modules.loading: Loading module pos_margin_threshold (59/67)` tercatat bersih, tidak ada Traceback/ParseError yang menyebut file modul ini. Total "67 modules loaded in 44.66s". Registry loaded sukses.
- **Masih belum terverifikasi oleh G1 ini:** DIFF-02/03/04 (import JS `@point_of_sale/*`) — install command tidak memuat/compile asset bundle frontend, cuma backend. G2 (buka POS session browser nyata) wajib sebelum `DIFF-02..05` dianggap selesai.

## [Fase B1] Model Risiko Rendah

- **Scope:** `models/pos_config.py`, `models/res_config_settings.py`, `wizard/wizard_margin_product.py`
- **Aksi:** Dicek — semua model sederhana (compute dari config_parameter, wizard biasa), tidak ada perubahan API yang diketahui.
- **Status:** ✅ Selesai (tidak ada perubahan diperlukan)

## [Fase C1] View Sederhana

- **Scope:** `views/products.xml`, `views/product_template_views.xml`, `views/res_config_settings.xml`, `wizard/wizard_margin_product.xml`
- **Aksi:** Dicek — tidak ada `<tree>`, xpath target (`product.product_template_form_view`, dll) tidak berubah berdasar hasil G1 (install sukses = xpath match).
- **Status:** ✅ Selesai, terkonfirmasi lewat G1

## [Fase C2] Semantik XML & UX

- **Scope:** ekspresi `invisible=` di `views/products.xml`/`product_template_views.xml`
- **Aksi:** Dicek — sudah sintaks modern (ekspresi Python langsung), tidak ada `attrs={}` lama yang perlu dikonversi.
- **Status:** ✅ Selesai (tidak ada perubahan diperlukan)

## [Fase E] JavaScript — ARSITEKTUR DATA MODEL POS BERUBAH TOTAL, 4 fix wajib (2026-08-24)

> **Konteks penting:** fix pertama (`MF-13`, dialog service) SEMPAT dianggap "selesai" berdasar audit source statis + G1 install pass. **Ini keliru** — baru ketahuan setelah benar-benar menjalankan Tour test (Mode D) bahwa ada 3 lapis masalah LAIN yang lebih dalam, semuanya berasal dari SATU root cause: Odoo 18.0 memindahkan seluruh arsitektur data POS (`Order`/`Orderline`/`Product` class lama) ke pola baru ("Base model" reactive record, `static/src/app/models/`). Ditulis di sini SESUAI URUTAN ditemukan (bukan dirapikan seolah sudah tahu dari awal), supaya lesson-nya jelas.

### E.1 — `MF-13`: `ConfirmPopup`/`ErrorPopup` → `dialog` service
- **Temuan:** `@point_of_sale/app/utils/confirm_popup/confirm_popup` dan `@point_of_sale/app/errors/popups/error_popup` sudah tidak ada di 18.0, begitu juga service `this.env.services.popup`. Diganti service `dialog` + `ConfirmationDialog`/`AlertDialog` (`@web/core/confirmation_dialog/confirmation_dialog`) + helper `ask()` (`@point_of_sale/app/store/make_awaitable_dialog`) — dikonfirmasi ini pola yang dipakai core POS sendiri (`pos_store.js`).
- **Aksi:** import diganti, pemanggilan `this.env.services.popup.add(...)` → `ask(this.env.services.dialog, {...})` (cabang confirm) / `this.env.services.dialog.add(AlertDialog, {...})` (cabang block). Pesan title/body TIDAK diubah.

### E.2 — `MF-15`: `Order`/`Orderline`/`Product` class dipindah total
- **Temuan:** `@point_of_sale/app/store/models` (path lama) masih ada sebagai FILE tapi isinya KOSONG (0 byte, dikonfirmasi `ls -la` container). Class baru: `PosOrder` (`@point_of_sale/app/models/pos_order`), `PosOrderline` (`@point_of_sale/app/models/pos_order_line`), `ProductProduct` (`@point_of_sale/app/models/product_product`). Method-level API (`get_unit_display_price()`, `get_orderlines()`, dst) byte-identik nama/signature-nya — dikonfirmasi baca source langsung.
- **Aksi:** `static/src/store/models/models.js` — import diarahkan ke path/nama baru. `patch(Product.prototype,...)` → `patch(ProductProduct.prototype,...)`. `patch(Orderline.prototype,...)` → `patch(PosOrderline.prototype,...)`.

### E.3 — `MF-16`: `Order.prototype.pay()` tidak lagi dipanggil tombol "Pay"
- **Temuan:** tombol "Pay" (`product_screen.xml`) memanggil `this.pos.pay()` = `PosStore.prototype.pay()` LANGSUNG — method itu TIDAK PERNAH memanggil `PosOrder.pay()` (method itu bahkan tidak ada lagi di kelas order). Dikonfirmasi baca `product_screen.xml`/`pos_store.js` container.
- **Aksi:** blok `patch(Order.prototype, {async pay(){...}})` **DIHAPUS** dari `models.js`. Logic blocking (filter orderline di bawah minimum + dialog) dipindah jadi `patch(PosStore.prototype, {async pay(){...; return super.pay(...arguments);}})` di `pos_store.js` — dipanggil TEPAT SEBELUM logic lot/serial-check bawaan core (via `super.pay()`), supaya urutan validasi tetap masuk akal (margin check duluan, baru lot check, baru navigasi Payment Screen).

### E.4 — `MF-17`: `PosStore.prototype._loadProductProduct()` sudah tidak ada
- **Temuan:** hook ini (dipatch untuk fallback `minimum_sale_price`→`0` kalau falsy) tidak ada lagi di `PosStore` 18.0 — patch modul ini jadi dead code (tidak error, cuma tidak pernah terpanggil).
- **Aksi:** patch **DIHAPUS** dari `pos_store.js` (bukan diperbaiki — tujuannya sudah tidak relevan, `fields.Float()` core selalu default `0.0`).

### E.5 — `MF-18`: `pos.session._loader_params_product_product()` → `_load_pos_data_fields()`
- **Temuan:** mekanisme loading field custom ke frontend berubah dari `pos.session._loader_params_<model>()` jadi `<model>._load_pos_data_fields(config_id)` (`@api.model`, per-model). Hook lama TIDAK ADA lagi di `pos.session` — override modul ini jadi dead code juga.
- **Aksi:** `models/pos_session.py` — override lama **DIHAPUS** (diganti komentar penjelasan, file tetap ada sesuai P1 Full Module Fidelity, tapi TIDAK ada override berbahaya yang bisa `AttributeError` kalau hook lama dipanggil lagi). `models/product.py` — ditambah `ProductProduct._load_pos_data_fields()` (`super()._load_pos_data_fields(config_id)` + append 2 field custom).

- **Secara eksplisit TIDAK dilakukan (seluruh Fase E):** tidak ada perubahan logic bisnis (kondisi `blocked`, formula margin, dst), tidak ada perubahan teks pesan. Semua perubahan murni relokasi API mengikuti perpindahan core, bukan refactor gaya.
- **Risiko:** Kritis → RESOLVED, **terverifikasi Tour test nyata** (lihat entri G2/Tour di bawah).
- **Status:** ✅ Selesai, **seluruhnya perubahan wajib untuk kompatibilitas 18.0** (`CLAUDE.md` §Forbidden Actions mengizinkan eksplisit — API lama dihapus total, bukan pilihan gaya).

## [Fase F] Upgrade Template — 2 fix wajib, ditemukan lewat Tour test (2026-08-24)

> Dijalankan SETELAH Fase E selesai penuh (urutan wajib). Kedua bug di sini **TIDAK terdeteksi G1**, hanya dari benar-benar merender komponen di Chrome (Mode D).

### F.1 — `MF-19`: Owl `Orderline` component validasi strict `props.line` shape
- **Temuan:** `OwlError: Invalid props for component 'Orderline': 'line' doesn't have the correct shape (unknown key 'minimumSalePrice', ...)`. Komponen `Orderline` (`@point_of_sale/app/generic_components/orderline/orderline.js`) sekarang mendeklarasikan `static props = {line: {shape: {...}}}` dan Owl 18.0 me-reject key yang tidak terdaftar di `shape` sebagai error fatal.
- **Aksi (models.js):**
  - Sekaligus resolusi `MF-11` (full-override risiko lama): `getDisplayData()` diubah dari full-override jadi **extend** — `return {...super.getDisplayData(), minimumSalePrice: ..., minimumSalePriceWithTax: ..., isLessMinimumSalePrice: ...}`. Ini juga otomatis benar terhadap perubahan field lain di core (`packLotLines` bukan `pack_lot_lines`, `taxGroupLabels` baru, dst) yang TIDAK PERNAH akan kita tahu semua kalau tetap full-override.
  - `this.product` → `this.get_product()` (getter properti lama sudah tidak ada, method baru).
  - `this.env.utils.formatCurrency(...)` → import `formatCurrency` langsung dari `@point_of_sale/app/models/utils/currency` (Base model record TIDAK punya `this.env` — dikonfirmasi core sendiri tidak pernah pakai `this.env` di file model manapun).
  - `patch(Orderline.props.line.shape, {minimumSalePrice: {type: String, optional: true}, minimumSalePriceWithTax: {...}, isLessMinimumSalePrice: {type: Boolean, optional: true}})` ditambahkan.

### F.2 — `MF-20`: `orderline.xml` xpath direct-child tidak match wrapper baru
- **Temuan:** `Error: Element '<xpath expr="//li[...]/ul[...]/t[...]">' cannot be located in element tree`. Core 18.0 menambah `<div class="d-flex flex-column w-100 gap-1">` di antara `<li class="orderline">` dan `<ul class="info-list">` — xpath direct-child (`/ul`) tidak lagi match.
- **Aksi:** `static/src/store/orderline.xml` — xpath diubah dari `/ul[hasclass('info-list')]` jadi `//ul[hasclass('info-list')]` (descendant, bukan direct-child). Isi kustomisasi (pesan peringatan) TIDAK diubah.
- **Secara eksplisit TIDAK dilakukan:** tidak menyentuh `<attribute name="t-attf-class">` di xpath pertama (styling `comboParent`/`isLessMinimumSalePrice` di `<li>` root) — itu quirk pre-existing (replace bukan merge terhadap `t-attf-class` core), di luar scope fix ini, dicatat sebagai catatan minor bukan finding baru (tidak crash, cuma styling combo item berpotensi kurang tepat — sudah ada risiko yang sama sejak 17.0).
- **Status:** ✅ Selesai, **seluruh Fase F terverifikasi Tour test nyata**.

## [Fase E/F — Tour Test] Verifikasi interaktif nyata (Mode D)

- **File:** `static/tests/tours/margin_threshold_tour.js` (tour `pos_margin_threshold_below_minimum_confirm_tour`) + `tests/test_margin_threshold_tour.py` (companion `HttpCase`, inherit `TestPointOfSaleHttpCommon`).
- **Manifest:** ditambah key `web.assets_tests: ['pos_margin_threshold/static/tests/tours/**/*']`.
- **Setup:** produk `standard_price=10`, `margin_sale=50` → `minimum_sale_price=15`; jual di harga `5` (di bawah minimum); `blocking_transaction_pos=False` (jalur `ask()`/`ConfirmationDialog`, bukan `AlertDialog`).
- **Alur yang benar-benar dieksekusi Chrome asli:** buka POS → buka register → tambah produk dengan harga custom via numpad → klik Pay → **dialog "Price unit less than minimum price" benar-benar muncul dengan body yang benar** → klik Confirm → **benar-benar lanjut ke Payment Screen** → pilih metode bayar → validate → **receipt screen muncul (pembayaran sukses)**.
- **3 lesson penulisan Tour yang ditemukan sendiri (dicatat supaya tidak terulang):**
  1. `ProductScreen.clickPayButton()` punya built-in wait-for-payment-screen — kalau ada dialog di antaranya (seperti kasus kita), WAJIB panggil `clickPayButton(false)` dan tulis wait manual sendiri SETELAH dialog di-confirm.
  2. Owl props validation (`MF-19`) adalah kelas error yang TIDAK akan pernah ketahuan dari G1/install — hanya dari render nyata.
  3. Xpath direct-child vs descendant (`MF-20`) juga kelas error yang sama — QWeb JS template (beda dari `ir.ui.view`) tidak divalidasi saat install.
- **Hasil akhir:** `tour succeeded`, **0 failed, 0 error(s) of 18 tests**.
- **Kontribusi ke `05b_TEST_PLAN_MIGRATION.md`:** tour AC-02-01/02/03 yang sebelumnya "wajib ditulis" — **1 dari 3 sudah ditulis dan pass** (jalur `!blocked`/`ask()`). Jalur `blocked`/`AlertDialog` (AC-02-01) dan wizard assign margin (AC-03) masih belum punya Tour — kandidat lanjutan Step 9, bukan blocker Step 8.

---

## Temuan di Luar Spec

- [x] Tidak ada

## Kontribusi ke Knowledge Base

- [x] **Ada, dan SUDAH terverifikasi eksekusi nyata (bukan cuma baca kode)** — kandidat kuat `dependency-compat/point_of_sale/17-to-18.md`, mencakup:
  1. `@point_of_sale/app/store/models` kosong total di 18.0, class pindah ke `@point_of_sale/app/models/{pos_order,pos_order_line,product_product}.js` dengan nama `PosOrder`/`PosOrderline`/`ProductProduct` — method-level API tetap byte-identik.
  2. `Order.pay()` tidak lagi entry point tombol Pay — pindah ke `PosStore.pay()`.
  3. `_loader_params_product_product` (pos.session) → `_load_pos_data_fields` (per-model, `@api.model`).
  4. `ConfirmPopup`/`ErrorPopup`/service `popup` dihapus total → `dialog` service + `ConfirmationDialog`/`AlertDialog`/`ask()`.
  5. Owl `Orderline` component validasi strict `props.line` shape — extend field custom WAJIB lewat `patch(Orderline.props.line.shape, {...})`.
  6. `orderline.xml` core menambah wrapper `<div>` antara `<li class="orderline">` dan `<ul class="info-list">` — xpath lama harus descendant (`//`), bukan direct-child (`/`).
  - Ditulis ke `migration-records/pos-margin-sale_17.0_18.0/SUMMARY.md` — lihat file itu untuk detail lengkap siap-promosi ke `knowledge/`.
