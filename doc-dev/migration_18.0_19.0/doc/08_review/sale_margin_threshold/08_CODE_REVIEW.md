# Code Review — sale_margin_threshold

**Step:** 8 — Code Review (gate)
**Ref:** `03_spec/sale_margin_threshold/03_MIGRATION_SPEC.md`,
`05_acceptance/sale_margin_threshold/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`,
`06_implementation/sale_margin_threshold/06c_IMPLEMENTATION_LOG.md`,
`01_intake/sale_margin_threshold/01b_BASELINE_SPEC.md`
**Odoo Version:** 19.0
**Files reviewed:** seluruh modul — perhatian khusus ke 3 file Step 6 (`views/products.xml`,
`models/product.py`, `tests/test_cross_module.py`) + 2 file diperbaiki Step 8 sendiri
(`models/sale_order.py`, `wizard/sale_confirmation.py`, `wizard/wizard_margin_product.py` — `MF-22`).
**Tanggal:** 2026-08-27

---

## A. Issues (Lint, Konvensi Odoo, Business Logic, Security, Performance, Code Quality)

| ID | Severity | Kategori | File | Baris | Issue | Rekomendasi |
|---|---|---|---|---|---|---|
| C-1 | 🔴 Critical (pre-existing, DIWARISI-SOURCE, keputusan sudah diambil) | Business Logic | `models/sale_order.py` | 19-21 | `action_confirm()` asumsi singleton, pecah di batch-confirm (`MF-08`) | **Keputusan user (2026-08-27): dipertahankan** — tidak diperbaiki, dicatat resmi |
| W-1 | 🟡 Warning | Version Compliance | `models/sale_order.py`, `wizard/sale_confirmation.py`, `wizard/wizard_margin_product.py` | berbagai | `self._context` — deprecated eksplisit di core 19.0 | **Diperbaiki (`MF-22`)** — jadi `self.env.context`, 4 lokasi |
| W-2 | 🟡 Warning | Business Logic | `models/product.py` | 82-84 | `_compute_warning` (`is_less_minimum_sale`) tanpa `@api.depends` | Dicatat `MF-21`, butuh keputusan user (pre-existing) |
| W-3 | 🟡 Warning | Convention/Business Logic | `security/groups.xml` | 5 | `implied_ids` diisi `base.module_category_hidden` (kategori, bukan grup) — kemungkinan salah tempel `category_id` | Dicatat `MF-20`, butuh keputusan user (pre-existing) |
| I-1 | 🔵 Info | Code Quality | `models/product.py` | 73, 77-80 | `margin_sale` punya `inverse` DAN `@api.onchange` — redundan tapi harmless | Pre-existing, tidak diubah |
| I-2 | 🔵 Info | Convention | `models/product.py` | 115-131 | `_register_hook` di-`@api.model` walau core tidak — tidak error, stilistik | Pre-existing, tidak diubah |
| I-3 | 🔵 Info | Convention (sudah tercatat `MF-06`) | `wizard/wizard_margin_product.py` | 23 | Typo `action_assing_margin` | Dipertahankan (nama method direferensikan view, harus identik) |
| I-4 | 🔵 Info (sudah tercatat `MF-05`) | Convention | `views/product_template_views.xml`+`products.xml` | — | Duplikat XML-ID, satu menimpa yang lain | Tidak ada aksi baru |
| I-5 | 🔵 Info (sudah tercatat `MF-06` sale) | Code Quality | `__manifest__.py` | — | Asset bundle menunjuk folder yang tidak ada | Tidak ada aksi baru |

**Tidak ada 🔴 Critical BARU** — `C-1` adalah temuan LAMA (`MF-08`) yang sudah punya keputusan
eksplisit user (dipertahankan), bukan blocker gate baru.

## B. Gap Analysis — Implementasi vs Migration Spec

| Spec item (`DIFF-NNN`/Fase) | Implementasi | Status | Catatan |
|---|---|---|---|
| `DIFF-05` (`groups_id`→`group_ids`) | `views/products.xml:74,85` | ✅ Covered | Diverifikasi lengkap — grep whole-module nihil sisa `groups_id` lama |
| — (`res.groups.users`→`user_ids`, ditemukan G1 bukan spec awal) | `models/product.py`, `tests/test_cross_module.py` | ✅ Covered (`MF-17`) | Grep whole-module nihil sisa `.users` |
| *(di luar spec awal)* `self._context` deprecated | 4 lokasi | ✅ Covered (`MF-22`) | Ditemukan Step 8 lewat review `pos_margin_threshold`, diterapkan konsisten ke modul ini juga |
| Sisanya (`DIFF-01`/`02`/`03`/`04`/`06`/`07`) | Tidak ada perubahan (sesuai spec) | ✅ Covered | |

## C. Gap Analysis — Implementasi vs Acceptance Criteria

| AC ID | Behavior | Status | Catatan |
|---|---|---|---|
| AC-01-01/02/03/04 | `action_confirm` (rental, blocking, wizard, skip_check_price) | ✅ Pass | Test existing, tidak berubah logic |
| AC-01-05 | Bilingual EN/FR tanpa `fr_FR` | ✅ Pass | `MF-21` (project 17→18) tetap resolved |
| AC-02-01/02 | Margin compute + dedup UI | ✅ Pass (implisit) | |
| AC-03-01 | Wizard bulk-assign | ✅ Pass | |
| AC-04-01 | Kolisi `wizard.margin.product` MRO | ✅ Pass | `test_cross_module.py` — MRO tetap `sale_margin_threshold` menang, dikonfirmasi ulang di G2 |
| AC-04-02 | `_register_hook` grup mutation | ✅ Pass | Field rename (`MF-17`) tidak mengubah logic |
| AC-04-03 | Batch-confirm singleton bug | ⚠️ Dipertahankan (keputusan user) | Bukan gate blocker — `MF-08` |

## D. Cek Khusus Migrasi — P1 Fidelity

- [x] Tidak ada perubahan behavior yang tidak disengaja — semua perubahan adalah rename field
  mekanis (`group_ids`, `user_ids`, `self.env.context`) yang tidak mengubah nilai/logic apapun.
  `MF-08` (batch-confirm) sengaja TIDAK diperbaiki sesuai keputusan eksplisit user.

**Cek tabrakan nama method dengan Odoo core (DUA ARAH):**
- [x] Sudah dicek (kedua arah) — dikonfirmasi TIDAK ADA tabrakan nama BARU antara field/method modul
  ini dengan definisi core 19.0 pada model yang sama. `action_confirm` DIKONFIRMASI sebagai override
  core yang disengaja (bukan kolisi tak terduga) — kontrak core (`for order in self:`, multi-record)
  tidak berubah 18.0→19.0, jadi `MF-08` bukan hasil perubahan platform, murni bug lama yang
  dipertahankan.

## E. Perubahan Tak Tertelusuri (di luar spec)

- [x] Ada — `self._context`→`self.env.context` (`MF-22`) ditemukan lewat review Step 8 modul
  sibling (`pos_margin_threshold`), diterapkan juga ke modul ini untuk konsistensi (wizard
  byte-identik, `MF-03`). Tidak perlu balik ke Step 3/4 — mekanis, sudah divalidasi tidak merusak
  apapun (lihat re-run test G2 setelah Step 8).

## F. Kontribusi ke Knowledge Base

- [x] Tidak ada temuan baru soal versi Odoo yang belum tercatat — `MF-16`/`17`/`22` sudah di
  `migration-records/pos-margin-sale_18.0_19.0/SUMMARY.md`. `MF-20`/`21` (pre-existing, bukan soal
  versi) tidak relevan untuk knowledge base lintas-project.

## G. Verdict

- Ringkasan Issues: 0 🔴 baru (`C-1`/`MF-08` sudah ada keputusan) · 3 🟡 (1 diperbaiki `MF-22`, 2
  tercatat `MF-20`/`21` untuk keputusan user) · 5 🔵
- [x] ✅ **Lulus** — tidak ada 🔴 baru, lanjut ke step 9.
