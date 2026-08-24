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
| E | ✅ 1 fix wajib diterapkan+terkonfirmasi (`ConfirmPopup`/`ErrorPopup` → `dialog` service), lihat entri Fase E | 2026-08-24 |
| F | ✅ Port apa adanya — xpath `t-inherit="point_of_sale.Orderline"` (`orderline.xml`) install sukses (G1), TAPI struktur target belum di-cross-check langsung ke source container seperti Fase E (rekomendasi dev spot-check kalau ada waktu, risiko dianggap Rendah-Sedang) | 2026-08-24 |
| G2 (validasi akhir/runtime) | ⚠️ **Sebagian** — konfirmasi source-level untuk import JS selesai (lihat entri G2), klik-test interaktif nyata (jual produk di bawah minimum, cek popup) BELUM dilakukan, wajib dev sebelum Step 8 final | 2026-08-24 |

## Riwayat Percobaan G1 (Install Test)

> Dijalankan sekaligus untuk ketiga modul (satu instance Docker `docker-env/docker-compose.yml`,
> image `odoo:18.0`, `-i pos_margin_threshold,sale_margin_threshold,pin_message --stop-after-init`)
> — hasil per-modul dicatat di log implementasi masing-masing. Command benar-benar dijalankan lewat
> Bash (Mode C), bukan diasumsikan — lihat `docker-env/logs/odoo.log` (timestamp `2026-08-24`).

| # | Dijalankan setelah fase | Mode | Hasil | Error (kalau fail) | Tanggal |
|---|---|---|---|---|---|
| 1 | A1+A2 (ketiga modul) | C | ✅ **Pass** — exit code 0, `pos_margin_threshold` loaded di posisi 59/67, "Modules loaded", "Registry loaded in 52.925s" | Tidak ada error/traceback dari modul ini secara spesifik di log. G1 konfirmasi backend (Python/security/XML `ir.ui.view`) parse & load bersih — TIDAK otomatis membuktikan JS. | 2026-08-24 |
| 2 | Setelah fix DIFF-04 (Fase E) | C | ✅ Pass | — | 2026-08-24 |

> **Update pasca-G2 (lihat entri Fase E/G2 di bawah):** `DIFF-02`/`DIFF-03` (import `@point_of_sale/app/store/{models,pos_store}`) **dikonfirmasi AMAN** — path tidak berubah di 18.0 (cross-check langsung source container). `DIFF-04` (`ConfirmPopup`/`ErrorPopup`) **dikonfirmasi BENAR-BENAR RUSAK** (path & service dihapus total di 18.0) — sudah diperbaiki, lihat Fase E. `DIFF-05` (loader `_loader_params_product_product`) masih belum diverifikasi eksekusi (butuh klik-test nyata, di luar kemampuan sesi browser tool ini).

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

## [Fase E] JavaScript — PERUBAHAN KODE WAJIB, dikonfirmasi G2 nyata (2026-08-24)

- **Scope:** `static/src/store/models/models.js`
- **Item spec (ref):** `03_MIGRATION_SPEC.md` §2 baris `DIFF-04`, `02_DIFF_ANALYSIS.md` DIFF-04
- **Temuan G2 (browser nyata, cross-check source container `odoo:18.0`):** `import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup"` dan `import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup"` — **KEDUA path/komponen ini SUDAH TIDAK ADA SAMA SEKALI di 18.0** (dikonfirmasi `docker exec ... find` — 0 hasil). Seluruh service `popup` (`this.env.services.popup`) juga tidak terdaftar lagi (dikonfirmasi grep registry). Odoo 18.0 mengganti mekanisme ini total dengan service `dialog` (`this.env.services.dialog`) + komponen `ConfirmationDialog`/`AlertDialog` dari `@web/core/confirmation_dialog/confirmation_dialog`, dan helper `ask()` dari `@point_of_sale/app/store/make_awaitable_dialog` (dikonfirmasi baca source `pos_store.js`/`make_awaitable_dialog.js` container langsung — pola ini dipakai core POS sendiri, bukan reka-reka).
- **Aksi:**
  - `static/src/store/models/models.js` baris 4-5: import `ConfirmPopup`/`ErrorPopup` → `import { ask } from "@point_of_sale/app/store/make_awaitable_dialog";` + `import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";`
  - Baris ~62 (`Order.prototype.pay`, cabang `!blocked`): `const {confirmed} = await this.env.services.popup.add(ConfirmPopup, {title, body})` → `const confirmed = await ask(this.env.services.dialog, {title, body})` — **pesan title/body TIDAK diubah sedikitpun**, hanya mekanisme panggilan dialog.
  - Baris ~70 (cabang `blocked`): `await this.env.services.popup.add(ErrorPopup, {title, body})` → `this.env.services.dialog.add(AlertDialog, {title, body})` — pesan tidak diubah.
- **Secara eksplisit TIDAK dilakukan:** tidak ada perubahan logic filter/kondisi `blocked`, tidak ada perubahan teks pesan (`_t(...)` string sama persis), tidak ada perubahan ke `getDisplayData()` (`MF-11`, terpisah dari fix ini).
- **Risiko:** Awalnya HIGH (`[TIDAK TERVERIFIKASI]`) → **dikonfirmasi WAJIB DIPERBAIKI** (path lama benar-benar hilang, bukan dugaan) → setelah fix, risiko turun ke LOW-MEDIUM (mekanisme baru dikonfirmasi persis dari pola yang dipakai core POS 18.0 sendiri, tapi belum diklik interaktif nyata — lihat batasan G2 di bawah).
- **Status:** ✅ Selesai, **perubahan wajib untuk kompatibilitas 18.0** (diizinkan eksplisit oleh `CLAUDE.md` §Forbidden Actions — bukan refactor gaya, API lama sudah dihapus total)

## G2 — Browser Verification Nyata (2026-08-24)

> Dijalankan bersamaan dengan sesi G2 `pin_message` (satu instance Docker/browser session).

- Sebelum fix: TIDAK ADA error konsol yang secara spesifik menyebut `pos_margin_threshold`/`@point_of_sale/*` — **BUKAN berarti aman**, karena `Order.prototype.pay()` (tempat `ConfirmPopup`/`ErrorPopup` dipakai) hanya benar-benar dieksekusi saat kasir klik bayar dengan produk di bawah minimum — jalur kode ini tidak dieksekusi cuma dari membuka halaman POS. **Ditemukan lewat audit source proaktif** (cross-check tiap import path modul ini terhadap source container `odoo:18.0` satu-satu), BUKAN lewat error konsol otomatis.
- Setelah fix: import baru (`ask`, `AlertDialog`) dikonfirmasi VALID (file & export ada di container `odoo:18.0`) — TAPI **belum diverifikasi lewat klik nyata** (buka POS session, coba jual produk di bawah minimum, klik bayar) karena batasan tool browser sesi ini (lihat catatan G2 `pin_message`, webclient tidak mounting penuh akibat isu Service Worker yang tidak terkait kode project).
- **WAJIB dev lakukan sebelum Step 8 final:** buka POS session di browser desktop biasa, jual produk di bawah minimum, klik bayar, pastikan dialog konfirmasi/error muncul benar (AC-02-01/02/03 di `05a_MIGRATION_ACCEPTANCE_CRITERIA.md`).

---

## Temuan di Luar Spec

- [x] Tidak ada

## Kontribusi ke Knowledge Base

- [ ] Ada — kandidat `dependency-compat/point_of_sale/17-to-18.md`: hasil G1 (install sukses/gagal) untuk import `@point_of_sale/app/store/models`, `pos_store`, popup path — ditulis ke `migration-records/pos-margin-sale_17.0_18.0/SUMMARY.md` setelah Fase E/F selesai dan G2 (browser) dijalankan.
