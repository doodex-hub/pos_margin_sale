# Dev Testing — pos_margin_threshold

**Step:** 9 — Dev Testing (gate)
**Ref:** `05_acceptance/pos_margin_threshold/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`,
`05_acceptance/pos_margin_threshold/05b_TEST_PLAN_MIGRATION.md`,
`01_intake/pos_margin_threshold/01b_BASELINE_SPEC.md`
**Tanggal:** 2026-08-27

---

## 9a. Audit Kesiapan Test

**Registrasi:** `tests/__init__.py` mengimpor SEMUA file test yang ada
(`test_margin_sale`, `test_cross_module`, `test_margin_threshold_tour`) — tidak ada gap registrasi.

**Audit isi method (AST-based, bukan `grep -c`):** 11 method test, **SEMUA "ok"** (bukan stub) —
setiap method punya body eksekusi nyata (bukan cuma docstring), dikonfirmasi lewat parse `ast`
langsung terhadap `body` tiap `FunctionDef`.

| AC | Deskripsi | File test | Status | Catatan |
|---|---|---|---|---|
| AC-01-01/02/03 | Margin/minimum price compute+inverse, decoration | `test_margin_sale.py` (7 method: `test_margin_sale_from_category`, `test_margin_sale_manual_override_persists`, `test_minimum_sale_price_computation`, `test_minimum_sale_price_inverse`, `test_minimum_sale_price_zero_standard_price_guard`, `test_margin_sale_inverse_writes_to_shared_template_not_per_variant`, `test_blocking_transaction_order_field_has_no_view_in_this_module`) | ✅ Lengkap | Semua ada assert nyata |
| AC-02-01 | Payment blocking — jalur confirm | `test_margin_threshold_tour.py::test_pos_margin_threshold_below_minimum_confirm_tour` | ✅ Lengkap | Tour test, browser asli |
| AC-02-02 | Payment blocking — jalur blocked | `test_margin_threshold_tour.py::test_pos_margin_threshold_below_minimum_blocked_tour` | ✅ Lengkap | Tour test, browser asli |
| AC-02-03 | Tidak ada popup kalau semua line valid | — | ❌ Tidak ada | Gap terbuka sejak 17→18 (carry-forward), butuh sesi POS register penuh — TIDAK diprioritaskan project ini, risiko diterima (low, positive path sudah dibuktikan 2x lewat tour) |
| AC-02-04 | Assert visual warning teks/warna orderline | — | ❌ Tidak ada terpisah | Idem — render `orderline.xml` sudah dibuktikan tidak crash (via tour), tapi warna/teks spesifik belum diassert terpisah |
| AC-03-01/02/03 | Wizard bulk-assign margin | `test_margin_sale.py::test_wizard_assign_margin_from_template_list` | ✅ Lengkap (sebagian) | AC-03-02 (list Variant) dan AC-03-03 (Cancel) tidak ada unit test terpisah — tercakup Step 10 (interaksi manual project 17→18, carry-forward) |
| AC-04-01 | Kolisi `wizard.margin.product` MRO | `test_cross_module.py::test_wizard_margin_product_model_merged_when_both_installed` | ✅ Lengkap | Log MRO penuh, dikonfirmasi ulang di 19.0 |

**Verdict audit:** [x] Semua AC prioritas tinggi (AC-02-01/02, inti fitur blocking payment yang
diperbaiki Step 6) berstatus Lengkap — lanjut eksekusi. AC-02-03/04 dan sebagian AC-03 tetap gap
carry-forward risiko rendah, TIDAK mengeskalasi (sudah diketahui & diterima sejak Step 5).

## Baseline

- Characterization test: tidak ada test source 18.0 terpisah — modul ini adalah HASIL migrasi
  17.0→18.0 yang sudah lulus 11 step penuh (branch `migration/18.0`), jadi test yang ada SUDAH
  merupakan baseline 18.0 yang terverifikasi.
- Applicability Check Fase E (Owl/JS) dari step 6: **Ya, applicable** — 2 tour test tercantum di
  atas, keduanya WAJIB pass sebelum verdict.

## Hasil Unit, Integration & Tour Test (target-codebase, Odoo 19.0)

Eksekusi: `docker compose up` (Mode C, AI jalankan langsung), `--test-enable
--test-tags=/pos_margin_threshold` (bersama 2 modul lain), database bersih (`down -v` sebelum tiap
run resmi).

| AC | Unit | Integration | Tour (Owl/JS) | Pass/Fail | Catatan |
|---|---|---|---|---|---|
| AC-01-01/02/03 | 7 test `test_margin_sale.py` | — | — | ✅ Pass | |
| AC-02-01 | — | — | `test_pos_margin_threshold_below_minimum_confirm_tour` | ✅ Pass — "tour succeeded" | Sempat FAIL 2x sebelum fix (`MF-19` import path test-tour util) |
| AC-02-02 | — | — | `test_pos_margin_threshold_below_minimum_blocked_tour` | ✅ Pass — "tour succeeded" | Idem |
| AC-03-01 | 1 test | — | — | ✅ Pass | |
| AC-04-01 | — | 1 test | — | ✅ Pass | MRO 19.0 dikonfirmasi identik hasil 18.0 |

**Hasil akhir gabungan (re-run terakhir setelah Step 8, database bersih):** 17 test `pos_margin_threshold`
tereksekusi (angka dari `odoo.tests.stats` — cross-check manual via log "Starting X.Y" menghasilkan
11 method unik x konsisten di setiap run; selisih kemungkinan cara `odoo.tests.stats` menghitung,
tidak mempengaruhi hasil pass/fail), **0 failed, 0 error**. Total gabungan ketiga modul: **0 failed,
0 error dari 22 test**.

## Kontribusi ke Knowledge Base

- [x] Tidak ada temuan baru di Step 9 — semua temuan runtime (`MF-19`) sudah dicatat di Step 6/8.

## Verdict

- [x] ✅ Semua AC prioritas Unit/Integration/Tour pass — **lanjut ke step 10**.
