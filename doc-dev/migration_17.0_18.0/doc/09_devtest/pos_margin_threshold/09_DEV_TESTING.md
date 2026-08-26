# Dev Testing — pos_margin_threshold

**Step:** 9 — Dev Testing (gate)
**Ref:** `05_acceptance/pos_margin_threshold/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `05_acceptance/pos_margin_threshold/05b_TEST_PLAN_MIGRATION.md`, `01_intake/pos_margin_threshold/01b_BASELINE_SPEC.md`, `08_review/pos_margin_threshold/08_CODE_REVIEW.md`
**Tanggal:** 2026-08-26

---

## 9a. Audit Kesiapan Test

Audit dilakukan pakai script `ast`-based (bukan cuma `grep -c def test_`) langsung terhadap image `pos_margin_sale_migration_18-odoo:latest`, cek tiap method test punya `assert*`/`self.assert*` real (bukan stub docstring-only).

| AC | Deskripsi | File test | Status | Catatan |
|---|---|---|---|---|
| AC-01-01..05 | Margin/minimum-price compute & constraint | `tests/test_margin_sale.py` (9 method) | ✅ **Lengkap** | Semua 9 method punya assertion nyata (`assertEqual`/`assertTrue`/dst), tidak ada stub |
| AC-02-01 (blocking, `AlertDialog`) | `tests/test_margin_threshold_tour.py::test_pos_margin_threshold_below_minimum_blocked_tour` | ✅ **Lengkap — BARU ditulis Step 9** | Menutup gap yang ditandai Step 8; `start_pos_tour()` sendiri adalah assertion (raise kalau tour gagal) |
| AC-02-02 (confirm/proceed) | `tests/test_margin_threshold_tour.py::test_pos_margin_threshold_below_minimum_confirm_tour` | ✅ **Lengkap** | Sudah ada sejak Step 6 |
| AC-02-03 (tidak ada line di bawah minimum → tidak ada popup) | — | ❌ **Tidak ada** | Lihat catatan risiko di §Verdict |
| AC-02-04 (teks peringatan merah orderline) | — | ❌ **Tidak ada test eksplisit** | Render template (`MF-20`) sudah terbukti tidak crash lewat kedua Tour; teks/warna spesifik belum diasersi terpisah |
| AC-03-01/02 (wizard assign margin) | — | ❌ **Tidak ada** | Lihat catatan risiko di §Verdict — kode wizard 0 diff dari 17.0 |
| AC-04-01/02 (cross-module dgn `sale_margin_threshold`) | `tests/test_cross_module.py::test_wizard_margin_product_model_merged_when_both_installed` | ✅ **Lengkap** | Assertion nyata + logging `__mro__`; lihat juga `FINDINGS.md` `MF-03` (dikonfirmasi Step 9 independen dari urutan install) |

**Verdict audit:** Tidak ada AC prioritas tinggi (risiko migrasi 18.0) yang stub/tidak ada — dua item `❌` yang tersisa (AC-02-03/04 detail visual, AC-03-01/02 wizard) adalah risiko RENDAH untuk migrasi spesifik ini (kode wizard 0 baris berubah dari 17.0, dikonfirmasi `08_CODE_REVIEW.md` §A; AC-02-03 adalah kasus kontrol negatif dari logic yang sudah sama-sama diuji jalur positifnya oleh dua Tour test). Lanjut ke eksekusi tanpa eskalasi tambahan.

## Baseline

- Characterization test asli 17.0 (`test_margin_sale.py`, `test_cross_module.py`) — reused apa adanya di 18.0, 0 diff kode test.
- Applicability Check Fase E (Owl/JS) dari step 6: **Ya, applicable** — 2 Tour test wajib (confirm + blocked path), keduanya sekarang ada.

## Hasil Unit, Integration & Tour Test (target-codebase, run bersih `docker compose down -v`, 2026-08-26)

| AC | Unit | Integration | Tour (Owl/JS) | Pass/Fail | Catatan |
|---|---|---|---|---|---|
| AC-01-01..05 | `test_margin_sale.py` (9 test) | — | — | ✅ Pass | |
| AC-02-01 | — | — | `test_pos_margin_threshold_below_minimum_blocked_tour` | ✅ **Pass — "tour succeeded"** | Baru, ditulis Step 9 |
| AC-02-02 | — | — | `test_pos_margin_threshold_below_minimum_confirm_tour` | ✅ Pass — "tour succeeded" | |
| AC-04-01/02 | — | `test_cross_module.py` | — | ✅ Pass | `__mro__` dikonfirmasi ulang, lihat `MF-03` |

**Hasil run gabungan ketiga modul (fresh DB):** `0 failed, 1 error(s) of 22 tests` — 1 error tetap `MF-21` (`sale_margin_threshold`, tidak terkait modul ini). Tidak ada regresi dari penambahan 2 test baru (blocked tour + reverse-order MRO test milik `sale_margin_threshold`).

## Kontribusi ke Knowledge Base

- [ ] **Tidak ada temuan baru** untuk modul ini spesifik di Step 9 — temuan baru sesi ini (`MF-03` order-independence) tercatat di bawah modul `sale_margin_threshold`/cross-cutting.

## Verdict

- [x] ✅ **Semua AC prioritas Unit/Integration/Tour pass — lanjut ke step 10**
- **Gap terbuka yang diterima sebagai risiko rendah, dibawa ke Step 10 (bukan blocker Step 9):** AC-02-03 (kontrol negatif "tidak ada popup"), AC-02-04 (assert visual teks/warna), AC-03-01/02 (wizard UI) — direkomendasikan ditutup lewat klik manual/QA di Step 10 kalau ada waktu, tapi TIDAK menghalangi gate ini karena risiko migrasi spesifiknya sudah rendah (kode wizard byte-identik 17.0, jalur positif AC-02 sudah terbukti dua kali lewat Tour nyata).
