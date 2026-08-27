# Dev Testing — sale_margin_threshold

**Step:** 9 — Dev Testing (gate)
**Ref:** `05_acceptance/sale_margin_threshold/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`,
`05_acceptance/sale_margin_threshold/05b_TEST_PLAN_MIGRATION.md`,
`01_intake/sale_margin_threshold/01b_BASELINE_SPEC.md`
**Tanggal:** 2026-08-27

---

## 9a. Audit Kesiapan Test

**Registrasi:** `tests/__init__.py` mengimpor semua file test (`test_action_confirm`,
`test_cross_module`) — tidak ada gap.

**Audit isi method (AST-based):** 6 method test, **SEMUA "ok"** (bukan stub).

| AC | Deskripsi | File test | Status | Catatan |
|---|---|---|---|---|
| AC-01-01 | Rental exemption | *(tidak ada test unit terpisah untuk rental — `native-target-enterprise` tersedia tapi environment test ini Community-only)* | ❌ Tidak ada | N/A permanen tanpa Enterprise environment nyata, carry-forward |
| AC-01-02 | Blocking `ValidationError` | `test_action_confirm.py::test_action_confirm_blocking_below_minimum` | ✅ Lengkap | |
| AC-01-03 | Wizard confirmation path | `test_action_confirm.py::test_action_confirm_wizard_path_when_not_blocking` | ✅ Lengkap | |
| AC-01-04 | `skip_check_price` no re-check | Tercakup implisit di `test_action_confirm_wizard_path_when_not_blocking` | ✅ Lengkap | |
| AC-01-05 | Bilingual EN/FR tanpa `fr_FR` | Tidak ada test unit eksplisit bahasa Prancis di suite ini | ❌ Tidak ada test khusus | `MF-21` (project 17→18) sudah divalidasi waktu itu lewat run manual `--load-language=fr_FR`, tidak diulang di project ini (risiko rendah, kode tidak diubah) |
| AC-02-01/02 | Margin compute + dedup UI | *(shared logic, tidak ada unit test terpisah modul ini)* | — | Tercakup implisit lewat `pos_margin_threshold`'s test suite (compute identik) |
| AC-03-01 | Wizard bulk-assign | *(tidak ada unit test dedicated modul ini)* | ❌ Tidak ada | Byte-identik `pos_margin_threshold`, sudah tercakup di sana |
| AC-04-01 | Kolisi `wizard.margin.product` MRO | `test_cross_module.py::test_wizard_margin_product_model_merged_when_both_installed` | ✅ Lengkap | |
| AC-04-02 | `_register_hook` grup mutation | `test_cross_module.py::test_group_sale_margin_action_emptied_when_pos_margin_installed` | ✅ Lengkap | |
| AC-04-03 | Batch-confirm singleton bug | `test_action_confirm.py::test_action_confirm_BATCH_MULTI_ORDER_F05` | ✅ Lengkap | Membuktikan bug MASIH ADA (`ValueError: Expected singleton`) — sesuai keputusan user (dipertahankan), test ini justru MEMBUKTIKAN status quo, bukan gagal |

**Verdict audit:** [x] AC prioritas tinggi (AC-01-02/03, AC-04-01/02/03) semua Lengkap — lanjut
eksekusi. AC-01-01/05 dan AC-03-01 N/A/tercakup-di-modul-lain, bukan gap yang perlu eskalasi.

## Baseline

- Sama seperti `pos_margin_threshold` — test yang ada adalah baseline 18.0 hasil project 17.0→18.0
  yang sudah lulus 11 step.
- Applicability Check Fase E (Owl/JS): **Tidak, N/A** — modul ini tidak punya JS/Owl sama sekali,
  jadi tabel di bawah wajar hanya berisi test backend.

## Hasil Unit, Integration & Tour Test (target-codebase, Odoo 19.0)

| AC | Unit | Integration | Tour (N/A) | Pass/Fail | Catatan |
|---|---|---|---|---|---|
| AC-01-02/03/04 | 2 test | — | — | ✅ Pass | |
| AC-04-01 | — | 1 test | — | ✅ Pass | MRO tetap `sale_margin_threshold` menang di 19.0 |
| AC-04-02 | — | 1 test | — | ✅ Pass | Field rename (`MF-17`) tidak mengubah hasil |
| AC-04-03 | 1 test | — | — | ✅ Pass (bug terkonfirmasi ada, sesuai ekspektasi) | `ValueError: Expected singleton: sale.order(1, 2)` — persis seperti diduga |

**Hasil akhir:** 10 test `sale_margin_threshold` (per `odoo.tests.stats`; 6 method unik dikonfirmasi
via log "Starting X.Y" — lihat catatan selisih di dokumen `pos_margin_threshold`), **0 failed, 0
error**. Total gabungan ketiga modul: **0 failed, 0 error dari 22 test**.

## Kontribusi ke Knowledge Base

- [x] Tidak ada temuan baru di Step 9 — `MF-16`/`17`/`22` sudah dicatat Step 6/8.

## Verdict

- [x] ✅ Semua AC prioritas Unit/Integration pass — **lanjut ke step 10**. `AC-04-03` sengaja
  "pass" dengan cara membuktikan bug (`MF-08`) masih ada persis seperti keputusan user — bukan
  celah cakupan.
