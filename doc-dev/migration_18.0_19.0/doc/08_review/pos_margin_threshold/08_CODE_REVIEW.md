# Code Review — pos_margin_threshold

**Step:** 8 — Code Review (gate)
**Ref:** `03_spec/pos_margin_threshold/03_MIGRATION_SPEC.md`,
`05_acceptance/pos_margin_threshold/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`,
`06_implementation/pos_margin_threshold/06c_IMPLEMENTATION_LOG.md`,
`01_intake/pos_margin_threshold/01b_BASELINE_SPEC.md`
**Odoo Version:** 19.0
**Files reviewed:** seluruh modul (`models/`, `wizard/`, `views/`, `static/src/store/`,
`static/tests/`, `tests/`, `__manifest__.py`) — perhatian khusus ke 4 file yang disentuh Step 6
(`models/models.js`, `pos_store.js`, `margin_threshold_tour.js`, `__manifest__.py`) + 1 file
diperbaiki di Step 8 sendiri (`wizard/wizard_margin_product.py`, `MF-22`).
**Tanggal:** 2026-08-27

---

## A. Issues (Lint, Konvensi Odoo, Business Logic, Security, Performance, Code Quality)

| ID | Severity | Kategori | File | Baris | Issue | Rekomendasi |
|---|---|---|---|---|---|---|
| W-1 | 🟡 Warning | Version Compliance | `wizard/wizard_margin_product.py` | 16, 24 | `self._context` — deprecated eksplisit di core 19.0 (`@api.deprecated`) | **Diperbaiki (`MF-22`)** — jadi `self.env.context` |
| W-2 | 🟡 Warning | Business Logic | `models/product.py` | 62, 69-71 | `_compute_warning` (`is_less_minimum_sale`) tanpa `@api.depends` — risiko cache stale | Dicatat `MF-23`, butuh keputusan user (pre-existing, di luar scope port) |
| W-3 | 🟡 Warning | Convention/Business Logic | `views/products.xml` | 62-64 | `list_price` di-`position="replace"`, menghapus `options`/`optional`/`decoration-muted` core | Dicatat `MF-24`, butuh keputusan user (pre-existing) |
| I-1 | 🔵 Info | Code Quality | `views/product_template_views.xml` | — | Dead file, tidak dimuat manifest (`MF-04`, sudah tercatat) | Tidak ada aksi baru |
| I-2 | 🔵 Info | Code Quality | `static/src/store/models/models.js` | 25-28 | `setUnitPrice` patch no-op (cuma `super()`) | Sengaja dipertahankan — hasil rename mekanis `DIFF-09`, bukan dead code baru |
| I-3 | 🔵 Info | Code Quality | `static/src/store/models/models.js` | 15-17 | `get_minimum_sale_price()` (tanpa tax) tidak pernah dipanggil | Pre-existing dead code, tidak diubah (di luar scope) |
| I-4 | 🔵 Info | Convention | `static/src/store/models/models.js` | 14-21 | `get_minimum_sale_price*` snake_case vs getter baru camelCase | Stilistik, tidak wajib diseragamkan (bukan override core, jadi tidak wajib rename) |
| I-5 | 🔵 Info | Convention | `models/pos_config.py`, `models/res_config_settings.py` | — | Import `_`/`api` tidak dipakai | Pre-existing, tidak diubah |
| I-6 | 🔵 Info | Security | `security/ir.model.access.csv` | — | Wizard margin terbuka untuk semua `base.group_user` | Pre-existing (sama sejak 18.0), bukan regresi migrasi |
| I-7 | 🔵 Info | Convention | `models/pos_config.py`, `res_config_settings.py` | — | Config parameter key `post_margin_sale.*` (bukan `pos_margin_sale.*`, kemungkinan typo lama) | Pre-existing, dipakai konsisten di semua tempat termasuk test — TIDAK diubah (bukan bug fungsional) |

**Severity:** 🔴 Critical (bug/security/AC tidak cover — wajib fix) · 🟡 Warning (convention/performance — fix kalau memungkinkan) · 🔵 Info (saran, opsional)

**Tidak ada 🔴 Critical.**

## B. Gap Analysis — Implementasi vs Migration Spec

| Spec item (`DIFF-NNN`/Fase) | Implementasi | Status | Catatan |
|---|---|---|---|
| `DIFF-01`/`02`/`03` (import path pindah) | `models.js`/`pos_store.js` | ✅ Covered | Diverifikasi cocok persis dengan struktur 19.0 nyata |
| `DIFF-06` (`props.line.shape` dihapus) | Patch dihapus total | ✅ Covered | |
| `DIFF-07` (`getDisplayData()` dihapus) | Diganti 2 getter (`minimumSalePriceWithTax`, `isLessMinimumSalePrice`) | ✅ Covered | Reviewer independen mengonfirmasi kedua getter konsisten satu sama lain dan dengan pengecekan di `pos_store.js` |
| `DIFF-08` (rename method core) | `getOrder`/`getOrderlines`/`getProduct`/`displayPriceUnit` | ✅ Covered | `displayPriceUnit` dikonfirmasi setara `get_unit_display_price()` 18.0 (toggle `iface_tax_included` sama) |
| `DIFF-09` (`set_unit_price`→`setUnitPrice`) | Selesai | ✅ Covered | |
| `DIFF-05` (`_load_pos_data_fields` param) | Tidak diubah (sesuai spec) | ✅ Covered | |
| `DIFF-10` (`orderline.xml`) | Tidak diubah | ✅ Covered | |
| *(di luar spec awal)* `margin_threshold_tour.js` import path | Diperbaiki (`MF-19`) | ✅ Covered | Ditemukan G2, bukan spec awal — spec TIDAK perlu diupdate (dampak kecil, sudah divalidasi) |
| *(di luar spec awal)* `wizard_margin_product.py` `self._context` | Diperbaiki (`MF-22`) | ✅ Covered | Ditemukan Step 8 |

## C. Gap Analysis — Implementasi vs Acceptance Criteria

| AC ID | Behavior | Status | Catatan |
|---|---|---|---|
| AC-01-01/02/03 | Margin/minimum price compute, decoration | ✅ Pass | Unit test `test_margin_sale.py`, tidak berubah |
| AC-02-01 | Payment blocking — jalur confirm | ✅ Pass | Tour test "tour succeeded" (G2) |
| AC-02-02 | Payment blocking — jalur blocked | ✅ Pass | Tour test "tour succeeded" (G2) |
| AC-02-03 | Tidak ada popup kalau semua line valid | ⚠️ Belum ada test | Gap terbuka sejak 17→18, carry-forward, bukan blocker gate |
| AC-02-04 | Assert visual warning teks/warna | ⚠️ Belum ada test terpisah | Idem |
| AC-03-01/02/03 | Wizard bulk-assign margin | ✅ Pass (implisit) | Kode Python tidak berubah kecuali `MF-22`, behavior identik |
| AC-04-01 | Kolisi `wizard.margin.product` MRO | ✅ Pass | `test_cross_module.py`, tidak terpengaruh migrasi |

## D. Cek Khusus Migrasi — P1 Fidelity

- [x] Tidak ada perubahan behavior yang tidak disengaja — semua deviasi dari source (`migration/18.0`)
  adalah adaptasi API teknis (rename/pindah path) yang diverifikasi setara secara semantik
  (dikonfirmasi reviewer independen untuk `displayPriceUnit`, getter margin), PLUS satu perbaikan
  `self._context`→`self.env.context` (`MF-22`, mekanis, tanpa perubahan behavior).

**Cek tabrakan nama method dengan Odoo core (DUA ARAH):**
- [x] Sudah dicek (kedua arah) — agent review mengonfirmasi TIDAK ADA tabrakan nama antara field/
  method modul ini (`margin_sale`, `minimum_sale_price*`, `is_blocked_warning`,
  `blocking_transaction_*`, `action_assign_margin`, `get_minimum_sale_price*`,
  `minimumSalePriceWithTax`, `isLessMinimumSalePrice`) dengan definisi BARU di core 19.0 pada model
  yang sama (`product.category/template/product`, `pos.config`, `res.config.settings`) — dicek
  langsung terhadap `enterprise19.0`.

## E. Perubahan Tak Tertelusuri (di luar spec)

- [x] Ada — dua item ditemukan lewat eksekusi (G2)/review (Step 8), bukan dari Step 2/3 awal:
  `margin_threshold_tour.js` import path (`MF-19`), `wizard_margin_product.py` `self._context`
  (`MF-22`). Keduanya sudah diperbaiki + divalidasi, dicatat lengkap di `FINDINGS.md`. Tidak perlu
  balik ke Step 3/4 — dampak kecil, mekanis, sudah dibuktikan tidak merusak apapun.

## F. Kontribusi ke Knowledge Base

- [x] Tidak ada temuan baru DI STEP INI yang belum tercatat — semua (`MF-19`, `MF-22`) sudah masuk
  `migration-records/pos-margin-sale_18.0_19.0/SUMMARY.md` dari Step 6. `MF-23`/`MF-24` (pre-existing,
  bukan soal versi Odoo) tidak relevan untuk knowledge base lintas-project.

## G. Verdict

- Ringkasan Issues: 0 🔴 · 3 🟡 (1 sudah diperbaiki `MF-22`, 2 tercatat `MF-23`/`MF-24` untuk
  keputusan user, bukan blocker) · 7 🔵
- [x] ✅ **Lulus** — tidak ada 🔴, lanjut ke step 9.

**Catatan:** `MF-23` (missing `@api.depends`) dan `MF-24` (`list_price` position=replace) adalah bug
PRE-EXISTING (bukan disebabkan migrasi 19.0) yang ditemukan lewat review menyeluruh — tidak
menghalangi gate ini (di luar scope port), tapi perlu keputusan user sebelum project ditutup.
