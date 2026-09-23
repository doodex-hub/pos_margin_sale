# Dev Testing — pos_margin_threshold

**Step:** 9 — Dev Testing (gate)
**Ref:** `05_acceptance/pos_margin_threshold/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`,
`05_acceptance/pos_margin_threshold/05b_TEST_PLAN_MIGRATION.md`, characterization baseline
(`01_intake/pos_margin_threshold/01b_BASELINE_SPEC.md`)
**Tanggal:** 2026-09-23

---

> Eksekusi dijalankan lewat `docker compose -f docker-compose.20.yml exec` langsung dari environment
> Docker 20.0 Step 6 (bukan `run-test.sh`, yang belum diinstansiasi untuk project ini) — command
> `--test-tags=/pos_margin_threshold` dipastikan tidak ter-mangle MSYS (dijalankan lewat
> `docker compose exec` sisi server, bukan argumen `odoo-bin` lokal langsung dari Git Bash Windows).
> Sanity-check manual: jumlah baris `Starting <Class>.<method>` di log dicocokkan ke 11 method test
> yang genuinely ada (lihat §9a) — bukan cuma baris ringkasan akhir.

## 9a. Audit Kesiapan Test — WAJIB sebelum eksekusi

**1. Registrasi (`tests/__init__.py`):** ketiga file test di `tests/` SEMUA ter-import
(`test_margin_sale`, `test_cross_module`, `test_margin_threshold_tour`) — tidak ada file test yang
luput dari test runner.

**2. Audit isi tiap method (AST-based, bukan cuma nama method)** — dijalankan dengan script identik
template ini (`ast.parse` per file, deteksi `body` method yang cuma 1 `Expr` docstring tanpa
statement lain = stub) terhadap ketiga file `tests/test_*.py`. **Hasil: 11/11 method = "ok" (bukan
stub)** — semua method test punya `assert*`/logika verifikasi nyata, tidak ada satupun yang cuma
docstring:

| File | Method | Status |
|---|---|---|
| test_margin_sale.py | test_margin_sale_from_category | Lengkap |
| test_margin_sale.py | test_margin_sale_manual_override_persists | Lengkap |
| test_margin_sale.py | test_minimum_sale_price_computation | Lengkap |
| test_margin_sale.py | test_minimum_sale_price_inverse | Lengkap |
| test_margin_sale.py | test_minimum_sale_price_zero_standard_price_guard | Lengkap |
| test_margin_sale.py | test_margin_sale_inverse_writes_to_shared_template_not_per_variant | Lengkap |
| test_margin_sale.py | test_wizard_assign_margin_from_template_list | Lengkap |
| test_margin_sale.py | test_blocking_transaction_order_field_has_no_view_in_this_module | Lengkap |
| test_cross_module.py | test_wizard_margin_product_model_merged_when_both_installed | Lengkap (skip kalau `sale_margin_threshold` tidak terinstall) |
| test_margin_threshold_tour.py | test_pos_margin_threshold_below_minimum_confirm_tour | Lengkap (Tour, real Chrome) |
| test_margin_threshold_tour.py | test_pos_margin_threshold_below_minimum_blocked_tour | Lengkap (Tour, real Chrome) |

**3. Cross-reference ke `05a_MIGRATION_ACCEPTANCE_CRITERIA.md` (37 AC leaf)** — per AC, bukan per
file:

| AC | Deskripsi singkat | File test | Status | Catatan |
|---|---|---|---|---|
| AC-01-01 | margin_sale diwarisi dari kategori | test_margin_sale.py::test_margin_sale_from_category | Lengkap | |
| AC-01-02 | override manual persisten | test_margin_sale.py::test_margin_sale_manual_override_persists | Lengkap | |
| AC-01-03 | minimum_sale_price = standard_price*(1+margin/100) | test_margin_sale.py::test_minimum_sale_price_computation | Lengkap | |
| AC-01-04 | inverse minimum_sale_price → margin_sale | test_margin_sale.py::test_minimum_sale_price_inverse | Lengkap | |
| AC-01-05 | guard div-by-zero | test_margin_sale.py::test_minimum_sale_price_zero_standard_price_guard | Lengkap | |
| AC-01-06 | margin_sale shared antar variant (quirk `MF-01`) | test_margin_sale.py::test_margin_sale_inverse_writes_to_shared_template_not_per_variant | Lengkap | `[DIWARISI-SOURCE]` |
| AC-01-07 | absensi recompute `is_less_minimum_sale` (quirk `MF-23`) | — | **Tidak ada** | Rekomendasi 05a: smoke/AST-check bahwa `@api.depends` masih tidak ada — belum ditulis |
| AC-01-08 | jalur onchange `_set_product_margin_sale` (`BSL-012`) | — | **Tidak ada** | Gap test baru, risiko migrasi rendah (Python tidak berubah) |
| AC-02-01 | wizard dialog dari list Product Template | — | **Tidak ada** | UI-only, tidak diautomasi |
| AC-02-02 | wizard dialog dari list Product Variant | — | **Tidak ada** | UI-only, tidak diautomasi |
| AC-02-03 | `action_assing_margin()` (typo dipertahankan) | test_margin_sale.py::test_wizard_assign_margin_from_template_list | Lengkap | |
| AC-02-04 | tombol Cancel wizard | — | **Tidak ada** | Low risk (native `special="cancel"`) |
| AC-03-01 | semua line di atas minimum → tidak ada dialog | — | **Tidak ada** | Sama substansi `BSL-018`/AC-03-05 |
| AC-03-02 | dialog konfirmasi + lanjut payment | test_margin_threshold_tour.py::test_pos_margin_threshold_below_minimum_confirm_tour | Lengkap | Tour, real Chrome, PASS (lihat §Hasil) |
| AC-03-03 | jalur DECLINE dialog konfirmasi | — | **Tidak ada** | Gap test baru, belum ditutup sesi ini |
| AC-03-04 | AlertDialog blocking mode | test_margin_threshold_tour.py::test_pos_margin_threshold_below_minimum_blocked_tour | Lengkap | Tour, real Chrome, PASS |
| AC-03-05 | `BSL-018`, nol dialog sama sekali | — | **Tidak ada** | Carry-forward 3x (17→18, 18→19, 19→20), belum ada keputusan dev |
| AC-04-01 | warning `<li>` + teks harga | — | **Tidak ada** (langsung) | Tidak diverifikasi eksplisit di tour (tidak ada assertion isi/posisi node); tour hanya melewati alur pembayaran |
| AC-04-02 | `[RISIKO TINGGI]` class `text-danger` gabungan dengan combo | — | **Tidak ada** | Regression check `BSL-016` murni dari baca kode/code review, bukan test otomatis |
| AC-04-03 | `BSL-018`, teks+warna terpisah | — | **Tidak ada** | Carry-forward 3x, sama seperti AC-03-05 |
| AC-05-01 | `[RISIKO TINGGI]` styling combo-child aktif (`MF-34`) | — | **Tidak ada** | Fix di level kode sudah diterapkan+diverifikasi well-formed, TAPI belum ada tour dengan combo product sungguhan |
| AC-06-01 | `[RISIKO]` `list_price` replace (`MF-24`/`DIFF-04`) | — | **Tidak ada** | Diverifikasi manual visual di Docker (Step 6), bukan test otomatis |
| AC-06-02 | `[RISIKO]` anchor `margin_sale` category form (`MF-31`) | — | **Tidak ada** | Diverifikasi manual install sukses, bukan test otomatis |
| AC-06-03 | (moot — popup dihapus `MF-29`) | — | N/A | Dokumentasi kelengkapan saja, tidak perlu pass/fail independen |
| AC-07-01 | `[RISIKO TINGGI]` kolom margin_sale/minimum_sale_price tampil | — | **Tidak ada** | Hanya diverifikasi manual sekali via Docker |
| AC-07-02 | `[RISIKO TINGGI]` decoration-danger `lst_price` via `position="attributes"` | — | **Tidak ada** | idem |
| AC-07-03 | `[RISIKO TINGGI]` kolom Incl. Tax + decoration margin negatif | — | **Tidak ada** | idem (`MF-38`) |
| AC-07-04 | `[RISIKO TINGGI]` dedup cross-module (`MF-37`) | — | **Tidak ada** | Diverifikasi manual sekali via Docker, direkomendasikan Step 8 jadi `TransactionCase` baru — belum ditulis |
| AC-08-01 | `_load_pos_data_fields` payload | — | **Tidak ada** (langsung) | Diverifikasi tidak langsung — tour PASS mensyaratkan payload ini benar (dipakai AC-04), tapi tidak ada assertion field-level eksplisit |
| AC-08-02 | getter `get_minimum_sale_price*()` frontend | — | **Tidak ada** (langsung) | Sama, tereksersis tidak langsung lewat tour |
| AC-08-03 | `[DIWARISI-SOURCE]` dead patch `setUnitPrice` | — | **Tidak ada** | Informational, risiko nol |
| AC-09-01 | `__mro__` `wizard.margin.product` gabungan | test_cross_module.py::test_wizard_margin_product_model_merged_when_both_installed | Lengkap | Database run final ternyata sudah punya `sale_margin_threshold` terinstall bersamaan — genuinely tereksekusi (bukan skip), lihat §Hasil |
| AC-09-02 | `blocking_transaction_order` tidak di view sendiri | test_margin_sale.py::test_blocking_transaction_order_field_has_no_view_in_this_module | Lengkap | |
| AC-09-03 | = AC-07-04 (dedup) | — | **Tidak ada** | idem AC-07-04 |
| AC-10-01 | dead file tidak terdaftar di manifest | — | **Tidak ada** | Informational, dicek Step 8 code review, tidak perlu test otomatis |
| AC-10-02 | `pos_session.py` tetap kosong | — | **Tidak ada** | Informational, regression-guard |
| AC-10-03 | `controllers.py` tidak disentuh | — | **Tidak ada** | Informational, risiko nol |

**Tally:** 37 AC leaf — **11 Lengkap** (0 Stub) · **1 N/A/moot** (AC-06-03) · **25 Tidak ada test
otomatis** (sebagian besar berstatus "diverifikasi manual via Docker" atau "informational/regresi
via code review", bukan genuinely belum diperiksa sama sekali — lihat kolom Catatan per baris).

**Verdict audit (sebelum eksekusi):**
- [x] Ada AC prioritas tinggi berstatus Tidak ada test otomatis (AC-04-02, AC-05-01, AC-06-01/02,
  AC-07-01..04, AC-09-03) — **di-flag secara eksplisit di sini**, bukan didiamkan. Namun ini BUKAN
  temuan baru sesi ini: Step 8 Code Review (`08_review/pos_margin_threshold/08_CODE_REVIEW.md`,
  gate LULUS, 0 🔴) sudah meninjau seluruh daftar ini dan mencatatnya sebagai rekomendasi
  non-blocking dibawa ke Step 9/10 (bukan syarat gate Step 8), dengan detail per item identik yang
  tercantum di tabel di atas (dedup cross-module, combo tour, `BSL-018` carry-forward, decline path).
  Step 9 ini **tidak membuka ulang keputusan itu secara sepihak** — gap-nya dibawa apa adanya ke
  Verdict di bawah dengan rekomendasi eksplisit untuk Step 10, bukan opsi (a)/(b) template (implementasi
  sekarang/prioritaskan sebagian) karena itu sudah diputuskan di Step 8.

## Baseline

- Characterization test / test asli source module: 8 method di `tests/test_margin_sale.py` berasal
  dari proses backfill (`doc-dev/backfill/`, characterization test 17.0, lihat `01a_MIGRATION_INTAKE.md`
  §4/§4a) yang sudah diadaptasi & di-carry-forward konsisten sejak project 17.0→18.0. Semua 8 method
  ini PASS terhadap kode 20.0 saat ini (lihat §Hasil) — tidak ada regresi terhadap baseline 19.0 yang
  berjalan.
- Applicability Check Fase E (Owl/JS) dari Step 6: **Ya, applicable** — modul ini punya
  `static/src/store/orderline.xml` (Owl template patch) dan `static/tests/tours/margin_threshold_tour.js`.
  2 Tour test (`..._confirm_tour`, `..._blocked_tour`) sudah ada dan wajib jadi bagian run resmi step
  ini (bukan cuma test backend) — lihat §Hasil untuk hasil run real Chrome terbaru.

## Hasil Unit, Integration & Tour Test (target-codebase)

Run resmi final sesi ini: `docker compose -f docker-compose.20.yml exec -T odoo` menjalankan
`odoo-bin -d pos_margin_sale_migration_20_qa_v7 -u pos_margin_threshold --test-enable
--test-tags=/pos_margin_threshold --stop-after-init`, log `/var/log/odoo/step9_final_pmt.log` di
container. `-u` sengaja disertakan (bukan cuma `-i`/tanpa flag) supaya dipastikan kode yang dites
adalah persis commit ter-`git status`-clean saat ini (`db3b73c`), bukan sisa state Docker lama — ini
memicu asset rebuild penuh (Owl/JS), dikonfirmasi dari log (`Pregenerating assets bundles` muncul).

| AC | Unit | Integration | Tour (Owl/JS) | Pass/Fail | Catatan |
|---|---|---|---|---|---|
| AC-01-01..06 | 6 test TransactionCase | — | — | **PASS** | 0 failed, 0 error |
| AC-02-03 | 1 test TransactionCase | — | — | **PASS** | |
| AC-09-01 | — | 1 test TransactionCase | — | **PASS** | Database `_qa_v7` ternyata SUDAH punya `sale_margin_threshold` terinstall bersamaan (dikonfirmasi dari log: `module: ['pos_margin_threshold, sale_margin_threshold']`) — test genuinely jalan (bukan skip), `__mro__` dikonfirmasi `sale_margin_threshold.WizardMarginProduct` menang seperti spesifikasi |
| AC-09-02 | 1 test TransactionCase | — | — | **PASS** | |
| AC-03-02, AC-04 (indirect), AC-08 (indirect) | — | — | `test_pos_margin_threshold_below_minimum_confirm_tour` | **PASS** | Real headless Chrome, `HttpCase.start_tour()` |
| AC-03-04 | — | — | `test_pos_margin_threshold_below_minimum_blocked_tour` | **PASS** | Real headless Chrome |

**Hasil run akhir (2026-09-23, log lengkap `docker-env/logs20/step9_final_pmt.log` di container
`/var/log/odoo/step9_final_pmt.log`):**

```
odoo.tests.stats: pos_margin_threshold: 17 tests 42.40s 6382 queries
odoo.tests.result: 0 failed, 0 error(s) of 11 tests when loading database 'pos_margin_sale_migration_20_qa_v7'
odoo.service.server: 11 post-tests in 325.63s, 6916 queries
```

Sanity-check jumlah baris `Starting <Class>.<method>` di log = **9** (8 `TestMarginSale` + 1
`TestCrossModuleWizardMargin`) + **2** baris `Starting TestMarginThresholdTour...` = **11**, cocok
persis dengan 11 method test yang teridentifikasi di §9a (bukan false-pass 0-test seperti lesson
`crm_probability_from_stage`). Kedua tour eksplisit tercatat **`SUCCEEDED`** di log (bukan cuma
"tidak timeout"):
```
╔════════════════════════════════════════════════════════════════╗
║ TOUR pos_margin_threshold_below_minimum_blocked_tour SUCCEEDED  ║
╚════════════════════════════════════════════════════════════════╝
╔════════════════════════════════════════════════════════════════╗
║ TOUR pos_margin_threshold_below_minimum_confirm_tour SUCCEEDED  ║
╚════════════════════════════════════════════════════════════════╝
```
Run ini dijalankan dengan `-u pos_margin_threshold` (asset rebuild penuh dikonfirmasi dari log
`Pregenerating assets bundles`) — memastikan kode yang dites adalah persis commit `db3b73c`
(working tree bersih, `git status` dicek sebelum run), bukan sisa state Docker sebelumnya.

## Kontribusi ke Knowledge Base

- [x] Ada — dicatat ke `FINDINGS.md` sesi ini (`MF-40`..`MF-45`), belum dipromosikan ke
  `migration-tool/knowledge/` (menunggu sesi curation terpisah). Kandidat SUMMARY.md
  (`migration-tool/migration-records/pos-margin-sale_19.0_20.0/SUMMARY.md`) — item paling bernilai
  general (bukan spesifik modul ini): (1) `ir.config_parameter.get_param/set_param` dihapus total di
  native 20.0 (`MF-40`), (2) Owl slot xpath `t-slot`→`t-call-slot` rename (`MF-41`), (3) lesson metodologi
  — compute `store=True` yang dibuat di `setUpClass()` `HttpCase`/Tour WAJIB `env.flush_all()` sebelum
  Chrome membaca (`MF-43`, awalnya salah didiagnosis sebagai "transient race condition", diralat), (4)
  CSS `ReceiptScreen`→`FeedbackScreen` rename (`MF-44`).

## Verdict

- [x] ✅ **Lulus — lanjut ke Step 10.** Semua 11 test otomatis yang ada (8 `TransactionCase` + 1
  cross-module + 2 Tour real Chrome) PASS bersih (0 failed, 0 error), termasuk kedua fitur inti
  risiko-migrasi-medium modul ini (dialog konfirmasi & blocking POS payment, `AC-03-02`/`AC-03-04`)
  dan verifikasi cross-module `AC-09-01` yang genuinely tereksekusi (bukan skip). Tidak ada AC
  prioritas Unit/Integration yang gagal.
- **Disclosure eksplisit (opsi (c) template — bukan silent-pass):** sejumlah AC **risiko migrasi
  tinggi** (`AC-04-02`, `AC-05-01`, `AC-06-01/02`, seluruh `AC-07`, `AC-09-03`) TIDAK punya test
  otomatis — status "Tidak ada", bukan "Stub" (tidak ada kode test yang ditulis lalu gagal diam-diam,
  memang belum ditulis). Ini bukan temuan baru: Step 8 Code Review sudah meninjau seluruh daftar ini
  dan eksplisit mencatatnya sebagai rekomendasi non-blocking (gate Step 8 LULUS, 0 🔴). Step 9 ini
  tidak membuka ulang keputusan itu secara sepihak — gate Step 9 dinyatakan lulus dengan gap-gap ini
  dibawa terbuka dan eksplisit ke Step 10 (lihat catatan di bawah), sesuai §Catatan.

**Catatan honest (tidak menghalangi gate, dibawa eksplisit ke Step 10 — konsisten Step 8 Code
Review):**
1. AC-07 (kolom list `MF-29`/`MF-37`/`MF-38`, seluruh grup **risiko migrasi tinggi**) — nol cakupan
   test otomatis, hanya diverifikasi manual sekali via Docker. Rekomendasi: prioritas tinggi Step 10
   review visual + pertimbangkan `TransactionCase` dedup (`AC-07-04`) sebelum UAT.
2. `BSL-018` (AC-03-05/AC-04-03) — carry-forward TIGA project migrasi berturut-turut (17→18, 18→19,
   19→20) tanpa keputusan dev eksplisit. Direkomendasikan **jangan di-carry-forward keempat kalinya**
   secara diam-diam — butuh keputusan sadar sebelum/selama Step 10.
3. AC-05-01 (`MF-34`, styling combo-child, **risiko migrasi tinggi**, PERTAMA KALI aktif di 20.0) —
   fix kode sudah diterapkan & well-formed, tapi belum ada Tour test dengan combo product sungguhan.
   Verifikasi visual live BELUM dilakukan sama sekali (bukan cuma "belum otomatis") — prioritas
   tertinggi Step 10.
4. AC-03-03 (jalur decline dialog konfirmasi POS) — belum pernah di-tour-test, satu-satunya jalur
   yang benar-benar membatalkan pembayaran.
5. Semua catatan di atas SUDAH direview & diterima sebagai rekomendasi non-blocking oleh Step 8 Code
   Review (`08_review/pos_margin_threshold/08_CODE_REVIEW.md`, gate lulus 2026-09-23) — Step 9 ini
   tidak menambah gap baru di area tersebut, hanya mengkonfirmasi ulang statusnya lewat audit AC formal
   dan run test real final.
