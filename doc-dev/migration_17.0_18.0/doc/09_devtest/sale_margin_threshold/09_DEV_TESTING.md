# Dev Testing — sale_margin_threshold

**Step:** 9 — Dev Testing (gate)
**Ref:** `05_acceptance/sale_margin_threshold/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `05_acceptance/sale_margin_threshold/05b_TEST_PLAN_MIGRATION.md`, `01_intake/sale_margin_threshold/01b_BASELINE_SPEC.md`, `08_review/sale_margin_threshold/08_CODE_REVIEW.md`
**Tanggal:** 2026-08-26

---

## 9a. Audit Kesiapan Test

| AC | Deskripsi | File test | Status | Catatan |
|---|---|---|---|---|
| AC-01-01 (blocking `ValidationError`) | `test_action_confirm.py::test_action_confirm_blocking_below_minimum` | ✅ **Lengkap** | |
| AC-01-02 (wizard path, not blocking) | `test_action_confirm.py::test_action_confirm_wizard_path_when_not_blocking` | ✅ **Lengkap** | Test yang sama menemukan `MF-21` |
| AC-01-03 (tidak ada isu → confirm langsung) | `test_action_confirm.py::test_action_confirm_normal_no_price_issue` | ✅ **Lengkap** | |
| AC-01-04 (rental order → skip) | — | ❌ **Tidak bisa dites di environment ini** | Butuh modul rental (Enterprise-only), tidak tersedia — lihat `08_CODE_REVIEW.md` §C |
| AC-02-01 (batch-confirm crash dipertahankan, `MF-06`) | `test_action_confirm.py::test_action_confirm_BATCH_MULTI_ORDER_F05` | ✅ **Lengkap** | 2 sumber independen (test + observasi demo data) |
| AC-03-01 (wizard confirm → skip_check_price) | Inline di `test_action_confirm_wizard_path_when_not_blocking` | ✅ **Lengkap** | |
| AC-03-02 (wizard cancel → no-op) | — | ❌ **Tidak ada** | Risiko rendah (`special="cancel"` murni deklaratif form) |
| AC-04-01 (dedup group saat kedua modul terinstall) | `test_cross_module.py::test_group_sale_margin_action_emptied_when_pos_margin_installed` | ✅ **Lengkap** | |
| AC-04-02 (MRO tergantung urutan install) | `test_cross_module.py::test_wizard_margin_product_model_merged_when_both_installed` | ✅ **Ditutup Step 9 — TAPI premis AC salah, lihat catatan** | Ditulis Step 9, dites empiris DUA urutan install (`-i pos_margin_threshold,sale_margin_threshold` dan dibalik `-i sale_margin_threshold,pos_margin_threshold`) — hasil MRO **identik di kedua urutan**. Premis AC-04-02 asli ("tergantung urutan install") **TIDAK TERBUKTI** — yang benar: `sale_margin_threshold` SELALU menang MRO, independen urutan `-i`. Lihat `FINDINGS.md` `MF-03` untuk detail dan bukti mentah. **Rekomendasi: `05a_MIGRATION_ACCEPTANCE_CRITERIA.md` AC-04-02 perlu dikoreksi teksnya** (bukan blocker gate ini). |
| AC-04-03 (`module_pos_margin_threshold` sembunyikan field UI) | — | ❌ **Tidak ada** | Murni compute Python trivial + `invisible=` view, tidak ada Tour/browser test |

**Verdict audit:** Tidak ada AC prioritas tinggi risiko-migrasi yang stub/tidak ada. Empat gap (`AC-01-04`, `AC-03-02`, `AC-04-03`, dan koreksi premis `AC-04-02`) berisiko rendah/tidak bisa ditutup di environment ini — didokumentasikan eksplisit, bukan diasumsikan aman. Lanjut eksekusi tanpa eskalasi tambahan.

## Baseline

- Characterization test 17.0 (`test_action_confirm.py`, `test_cross_module.py`) — reused apa adanya, 2 baris kode modul berubah (bukan test).
- Applicability Check Fase E (Owl/JS): **Tidak, N/A** — modul ini tidak punya JS/Owl sama sekali, cuma backend `models`/`wizard`/`views`. Tidak ada Tour test yang relevan/diperlukan.

## Hasil Unit, Integration & Tour Test (target-codebase, run bersih `docker compose down -v`, 2026-08-26)

| AC | Unit | Integration | Tour | Pass/Fail | Catatan |
|---|---|---|---|---|---|
| AC-01-01..03, AC-02-01, AC-03-01 | `test_action_confirm.py` (4 test) | — | N/A | ✅ Pass | |
| AC-04-01, AC-04-02 | — | `test_cross_module.py` (2 test) | N/A | ✅ Pass | `AC-04-02` — lihat catatan premis di §9a |

**Reverse-order verification (one-off, di luar `docker-compose.yml` standar):** `docker compose run --rm ... -i sale_margin_threshold,pos_margin_threshold ... --test-tags /pos_margin_threshold:TestCrossModuleWizardMargin,/sale_margin_threshold:TestCrossModuleGroupDedup` terhadap database test terpisah (`pos_margin_sale_migration_18_reverse_test`, dihapus setelah dicek) — `0 failed, 0 error(s) of 3 tests`, `__mro__` byte-identik dengan urutan standar. Bukti: `docker-env/logs/odoo_reverse.log` (lokal, tidak dicommit — `docker-env/logs/` di-gitignore).

**Hasil run gabungan ketiga modul (fresh DB, urutan standar):** `0 failed, 1 error(s) of 22 tests` — 1 error `MF-21` (lihat baris berikutnya, WAJIB dikonfirmasi ke dev sebelum go-live, bukan bug kode).

## `MF-21` — status akhir sebelum lanjut

Tetap `[CATATAN-DEPLOYMENT]`, bukan bug — **WAJIB dikonfirmasi ke dev sebelum Step 10/11:** apakah bahasa Prancis (`fr_FR`) benar-benar terinstall di environment production. Nuansa tambahan dari Step 8: kemungkinan mekanisme bilingual ini sudah silently broken di 17.0 kalau Prancis tidak pernah terinstall (lihat `08_CODE_REVIEW.md` §F, `FINDINGS.md` `MF-21`) — pertanyaan konfirmasi ke dev bukan cuma "apakah terinstall" tapi juga "apakah fitur ini pernah benar-benar berfungsi di 17.0 production".

## Kontribusi ke Knowledge Base

- [ ] **Ada** — temuan `MF-03` Step 9 (MRO Odoo untuk model `_name` sama tanpa `_inherit` TIDAK ditentukan urutan CLI `-i`, kontra-intuitif dibanding asumsi awal) layak masuk `migration-records/.../SUMMARY.md` sebagai pola umum Odoo (bukan spesifik migrasi 17→18) — dicek dulu, kandidat baru.

## Verdict

- [x] ✅ **Semua AC prioritas Unit/Integration pass — lanjut ke step 10**
- **Item wajib sebelum Step 10/11 (bukan blocker Step 9):** konfirmasi `MF-21` ke dev (bahasa Prancis production).
- **Gap risiko rendah, diterima, dibawa ke Step 10:** AC-01-04 (rental, tidak bisa dites di environment ini sama sekali), AC-03-02 (wizard cancel), AC-04-03 (UI field visibility) — direkomendasikan ditutup manual di QA kalau memungkinkan, tidak menghalangi gate ini.
- **Dokumentasi perlu dikoreksi (bukan kode):** `05a_MIGRATION_ACCEPTANCE_CRITERIA.md` AC-04-02 — premis "tergantung urutan install" salah, ganti jadi "MRO selalu memenangkan `sale_margin_threshold`, independen urutan install" (lihat `FINDINGS.md` `MF-03`).
