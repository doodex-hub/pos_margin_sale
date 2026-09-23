# Dev Testing — sale_margin_threshold

**Step:** 9 — Dev Testing (gate)
**Ref:** `05_acceptance/sale_margin_threshold/05a_MIGRATION_ACCEPTANCE_CRITERIA.md` (29 AC),
`05_acceptance/sale_margin_threshold/05b_TEST_PLAN_MIGRATION.md`, `01_intake/sale_margin_threshold/01b_BASELINE_SPEC.md`
**Tanggal:** 2026-09-23
**DB dipakai run final ini:** `pos_margin_sale_migration_20_qa_v8` (fresh, port `8130`, Docker 20.0
`docker-compose.20.yml` — DB `_v7`/port lain sedang dipakai agent sibling untuk `pos_margin_threshold`
secara paralel, sengaja dipisah supaya tidak bentrok)

---

## 9a. Audit Kesiapan Test

**Langkah 1 — registrasi:** `tests/__init__.py` meng-import KEDUA file
(`test_action_confirm`, `test_cross_module`) — tidak ada file test yang luput ter-load.

**Langkah 2 — klasifikasi AST tiap method** (dijalankan di dalam container, `python3` lokal Windows
tidak tersedia):

```
tests/test_action_confirm.py test_action_confirm_blocking_below_minimum          ok
tests/test_action_confirm.py test_action_confirm_wizard_path_when_not_blocking   ok
tests/test_action_confirm.py test_action_confirm_normal_no_price_issue           ok
tests/test_action_confirm.py test_action_confirm_BATCH_MULTI_ORDER_F05           ok
tests/test_cross_module.py   test_group_sale_margin_action_emptied_when_pos_margin_installed   ok
tests/test_cross_module.py   test_wizard_margin_product_model_merged_when_both_installed       ok
```

Tidak ada method dengan `body` berupa satu `Expr` docstring saja — **0 dari 6 method adalah stub**.
Dibaca manual juga (bukan cuma AST) untuk memastikan assert-nya genuinely menguji behavior, bukan
tautologi — semua 6 punya `assertEqual`/`assertRaises`/`assertTrue`/`assertFalse` yang mengikat ke
nilai/exception spesifik.

**Langkah 3 — cross-reference ke 29 AC (`05a_MIGRATION_ACCEPTANCE_CRITERIA.md`):**

| AC | Deskripsi singkat | File/method test | Status | Catatan |
|---|---|---|---|---|
| AC-01-01 | `product.category.margin_sale` diwarisi ke template | — | ❌ Tidak ada (tidak langsung) | Hanya diverifikasi TIDAK LANGSUNG lewat efek turunannya di AC-01-02 (nilai `minimum_sale_price` yang benar mengasumsikan inheritance jalan); tidak ada assert khusus `product.template.margin_sale == 20.0` sebelum dipakai. |
| AC-01-02 | `minimum_sale_price = standard_price*(1+margin_sale/100)` | `test_action_confirm_blocking_below_minimum` (assert `120.0`) | ✅ Lengkap | |
| AC-01-03 | Inverse `minimum_sale_price` → `margin_sale` | — | ❌ Tidak ada | |
| AC-01-04 | Edit `margin_sale` per-variant menulis ke template bersama | — | ❌ Tidak ada | |
| AC-01-05 | `minimum_sale_price_with_tax` formula (**[HIGH-RISK]**, `MF-38`/`MF-45`) | — | ❌ Tidak ada | Field ini baru dapat fix `@api.depends` di `MF-45` (Step 8) — TIDAK ada unit test Python yang meng-assert nilai aritmetika pajaknya (`120*1.10=132.0`), padahal ini murni backend/testable tanpa browser. Hanya diverifikasi visual manual di Docker (`MF-38`: "kolom Incl. Tax terisi benar"). |
| AC-01-06 | Stale-cache `is_less_minimum_sale` (`MF-21`, bug dipertahankan) | — | ❌ Tidak ada | Deskriptif/dokumentasi bug warisan, bukan prasyarat wajib test baru. |
| AC-02-01 | Rental order skip validasi margin (`BSL-001`) | — | ❌ Tidak ada (di modul ini) | Diverifikasi manual visual Docker (`sale_renting` di kedua environment, "dikonfirmasi identik") — bukan test Python otomatis di sini (butuh Enterprise `sale_renting`, di luar test suite modul). |
| AC-02-02 | Confirm langsung kalau semua harga OK (`BSL-002`) | `test_action_confirm_normal_no_price_issue` | ✅ Lengkap | |
| AC-02-03 | Blocking cabang `ValidationError` (`BSL-003`) | `test_action_confirm_blocking_below_minimum` | ✅ Lengkap | |
| AC-02-04 | Wizard cabang non-blocking (`BSL-003`) | `test_action_confirm_wizard_path_when_not_blocking` | ✅ Lengkap | |
| AC-02-05 | `skip_check_price` context mencegah rekursi (`BSL-004`) | `test_action_confirm_wizard_path_when_not_blocking` (indirect) | ⚠️ Lengkap-tidak langsung | Tervalidasi lewat efek sampingnya (wizard confirm berhasil), tidak ada assert eksplisit context flag itu sendiri. |
| AC-02-06 | Wizard confirm → state `sale`; Cancel → no-op (`BSL-005`) | `test_action_confirm_wizard_path_when_not_blocking` (jalur confirm saja) | ⚠️ Sebagian | Jalur Cancel **BELUM ada test** — sudah di-flag di 05a §Catatan Gap Traceability sejak Step 5, non-blocking, bukan temuan baru. |
| AC-02-07 | Pesan bilingual `fr`/lainnya (`BSL-006`/`007`) | — | ❌ Tidak ada | |
| AC-02-08 | Decoration merah `order_line` list, fix xpath `MF-35` (**[HIGH-RISK]**) | — | ❌ Tidak ada (view-level) | Modul ini tidak punya Tour/HttpCase (backend-only, dikonfirmasi Applicability Check Fase E = N/A). View decoration hanya diverifikasi manual smoke-install Docker (`MF-35`: "sudah diperbaiki & diverifikasi"), belum ada regression test otomatis. |
| AC-03-01 | Batch confirm crash `ValueError` (`BSL-009`/`MF-08`, **[HIGH-RISK — regresi kritis]**) | `test_action_confirm_BATCH_MULTI_ORDER_F05` | ✅ Lengkap | AC prioritas tertinggi di modul ini — tercakup penuh & PASS. |
| AC-03-02 | `_compute_is_rental_order_installed` singleton (`MF-26`) | — | N/A (deskriptif) | AC sendiri menyatakan ini dokumentasi bug, bukan prasyarat test wajib. |
| AC-03-03 | `implied_ids` salah tipe di `groups.xml` (`MF-20`) | — | N/A (tidak perlu test) | Prioritas rendah, dipertahankan apa adanya. |
| AC-04-01 | Kolom list Product Variants `optional="show"` + editable (**[HIGH-RISK]**, `MF-29`) | — | ❌ Tidak ada (view-level) | |
| AC-04-02 | Dedup kolom lewat `_get_view()` (**[HIGH-RISK]**, `MF-37`) | — | ❌ Tidak ada | Sudah di-flag Step 5 sebagai "baru diverifikasi manual sekali via Docker, belum ada regression test otomatis" — bukan temuan baru, tapi masih terbuka. |
| AC-04-03 | Paritas visual (merah margin negatif + kolom Incl. Tax) (**[HIGH-RISK]**, `MF-38`) | — | ❌ Tidak ada | Diverifikasi manual live Docker sesi sebelumnya, belum otomatis. |
| AC-04-04 | Decoration merah `lst_price` + skenario stale-cache | — | ❌ Tidak ada | |
| AC-04-05 | Edit inline `margin_sale`/`minimum_sale_price` di list tersimpan benar | — | ❌ Tidak ada | |
| AC-05-01 | MRO `wizard.margin.product` menang `sale_margin_threshold` (`BSL-015`) | `test_wizard_margin_product_model_merged_when_both_installed` | ✅ Lengkap (test ada, real) — **SKIPPED di run DB ini** | DB `_v8` hanya install `sale_margin_threshold` sendirian (sesuai instruksi task), jadi `skipTest()` otomatis terpicu (`pos_margin_threshold tidak terinstall`) — bukan gagal, memang butuh DB gabungan untuk genuinely jalan. |
| AC-05-02 | `_register_hook()` mutasi `group_sale_margin_action.user_ids` (`BSL-010`) | `test_group_sale_margin_action_emptied_when_pos_margin_installed` | ✅ Lengkap (test ada, real) — **SKIPPED di run DB ini** | Sama seperti di atas, arah "hanya modul ini terinstall" juga belum ada test terpisah (sudah di-flag Step 5). |
| AC-06-01 | UI Settings → `config_parameter` (`res.config.settings`) | — | ❌ Tidak ada (jalur UI) | Tervalidasi tidak langsung lewat 2 test yang men-set param langsung; jalur UI Settings sendiri belum, sudah di-flag Step 5. |
| AC-07-01 | XML-ID dobel saling timpa (`BSL-013`) | — | N/A (quirk dipertahankan) | |
| AC-07-02 | Glob assets kosong (`BSL-014`) | — | N/A (cruft tanpa efek) | |
| AC-07-03 | `depends_context('uid')` nit efisiensi (`BSL-016`) | — | N/A (nit) | |
| AC-07-04 | `position="replace"` hilangkan `options=` (`BSL-019`/`MF-27`) | — | N/A (dipertahankan, kontras `AC-04-01`) | |

**Tally:** 6 method test — **6 Lengkap, 0 Stub, 0 Tidak valid**. Dari 29 AC: **8 Lengkap (assert
langsung PASS)**, **2 Lengkap-tapi-skip-di-run-ini** (AC-05-01/02, butuh DB gabungan), **1
Lengkap-tidak-langsung** (AC-02-05), **1 sebagian** (AC-02-06, jalur Cancel kosong), **~13 Tidak ada
test eksplisit**, **7 N/A** (deskriptif/quirk yang memang tidak perlu test per keputusan dev).

**Verdict audit (sebelum eksekusi final):** Beberapa AC **[HIGH-RISK]** (`AC-01-05`, `AC-02-08`,
`AC-04-01`, `AC-04-02`, `AC-04-03`) **tidak** berstatus Lengkap secara otomatis — lihat eskalasi di
bagian Verdict di bawah, bukan diam-diam dianggap tercakup.

---

## Baseline

- Characterization test / test asli source module: `tests/test_action_confirm.py` dan
  `tests/test_cross_module.py` adalah hasil backfill (`doc-dev/backfill/`, komentar header
  "BACKFILL (doc-dev-backfill) — test baru ditambahkan retroaktif, tidak mengubah kode bisnis"),
  bukan test asli 19.0 (modul asli tidak punya folder `tests/` bawaan) — dikonfirmasi sesuai Step 1
  §4/§4a dan gate Step 1 (asumsi "tidak ada dokumen pelengkap lain di luar `doc-dev/backfill/`" sudah
  dikonfirmasi dev). Hasil run terhadap logic yang sama sudah konsisten pass di 19.0 (baseline) dan
  20.0 (setelah `MF-40` fix) — tidak ada regresi behavior antar versi pada test yang ada.
- Applicability Check Fase E (Owl/JS) dari Step 6: **Tidak, N/A** — `sale_margin_threshold` murni
  backend (tidak ada file `.js`/Owl, `AC-07-02` mengonfirmasi `static/src/` bahkan tidak ada di
  disk). Konsekuensinya tabel di bawah cuma backend Python — ini bukan celah cakupan tour, tapi tetap
  meninggalkan gap nyata untuk AC **view-level** (list/form XML) yang tidak tercakup Tour maupun unit
  test arch-inspection (lihat Verdict).

## Hasil Unit, Integration & Tour Test (target-codebase)

Run final (2026-09-23, DB baru `pos_margin_sale_migration_20_qa_v8`, port 8130):
```
docker compose -f docker-compose.20.yml exec -T odoo bash -lc \
  "python3 /odoo20/odoo-bin -d pos_margin_sale_migration_20_qa_v8 --db_host=db --db_user=odoo \
   --db_password=odoo --addons-path=/odoo20/addons,/enterprise20,/mnt/extra-addons \
   -i sale_margin_threshold --http-port=8130 --test-enable --test-tags=/sale_margin_threshold \
   --stop-after-init --log-level=info --logfile=/var/log/odoo/step9_final_smt.log"
```
Log hasil (`docker-env/logs20/step9_final_smt.log` di container):
```
odoo.tests.stats: sale_margin_threshold: 10 tests 0.44s 507 queries
odoo.tests.stats: web: 6 tests 0.01s 14 queries
odoo.tests.result: 0 failed, 0 error(s) of 8 tests when loading database 'pos_margin_sale_migration_20_qa_v8'
```
(8 "Starting ..." log line: 4 `test_action_confirm` + 2 `test_cross_module` [keduanya `skipped`,
bukan fail] + 2 test JS unit generik `web.tests.test_js` yang tidak terkait modul ini — total baris
summary Odoo sendiri menghitung 8 test post-install; angka "10 tests" di baris `stats` sedikit beda
konvensi hitung internal Odoo, bukan indikasi ada test tersembunyi yang gagal — tidak ada baris
`FAIL`/`ERROR` di log manapun.)

| AC | Unit | Integration | Tour | Pass/Fail | Catatan |
|---|---|---|---|---|---|
| AC-01-02 | ✅ | — | N/A | ✅ Pass | `minimum_sale_price == 120.0` |
| AC-02-02 | ✅ | — | N/A | ✅ Pass | |
| AC-02-03 | ✅ | ✅ | N/A | ✅ Pass | `ValidationError` + state tetap `draft` |
| AC-02-04 | ✅ | ✅ | N/A | ✅ Pass | wizard `act_window` + state `draft` |
| AC-02-05 | ✅ (indirect) | — | N/A | ✅ Pass (indirect) | |
| AC-02-06 (jalur confirm) | ✅ | ✅ | N/A | ✅ Pass | jalur Cancel: gap, lihat 9a |
| AC-03-01 | ✅ | ✅ | N/A | ✅ Pass | `ValueError: Expected singleton` ter-raise, HIGH-RISK, PASS bersih |
| AC-05-01 | ⚠️ skipped (DB standalone) | — | N/A | ⚠️ Skipped (bukan fail) | perlu DB gabungan kedua modul untuk genuinely jalan |
| AC-05-02 | ⚠️ skipped (DB standalone) | — | N/A | ⚠️ Skipped (bukan fail) | idem |
| AC-01-01/03/04/05/06, AC-02-01/07/08, AC-03-02/03, AC-04-01..05, AC-06-01, AC-07-01..04 | — | — | N/A | Tidak ada test otomatis / N/A | lihat detail per-AC di §9a |

**0 failed, 0 error** untuk seluruh test yang genuinely dieksekusi — tidak ada regresi dari `MF-40`
(sudah RESOLVED) atau `MF-45` (fix Step 8 sudah aktif, compute `minimum_sale_price_with_tax` tidak
error saat load meski belum ada unit test khusus nilai pajaknya).

## Kontribusi ke Knowledge Base

- [x] Tidak ada temuan baru yang perlu dicatat — run final ini murni re-konfirmasi state yang sudah
  didokumentasikan (`MF-40`, `MF-45`), tidak menemukan bug/behavior Odoo baru yang belum tertangkap
  Step 2-8.

## Verdict

**Backend/Python: ✅ bersih.** 0 failed/0 error pada seluruh test yang genuinely dieksekusi; AC
prioritas tertinggi modul ini (`AC-03-01`, regresi kritis batch-confirm `MF-08`) PASS penuh. `MF-40`
(config_parameter API) dan `MF-45` (`@api.depends` pajak) tetap resolved, tidak ada regresi.

**⚠️ ESCALATION — tidak ditutup sebagai ✅ tanpa syarat, mengikuti instruksi audit 9a:**
```
ESCALATION — Migrasi 20.0
Step/Fase: 9 (Dev Testing, gate)
Modul: sale_margin_threshold
Isu: 5 AC berlabel [HIGH-RISK — Step 9/10 extra scrutiny] TIDAK punya test otomatis:
     AC-01-05 (formula minimum_sale_price_with_tax, backend murni — MUDAH ditest, belum ada),
     AC-02-08 (decoration order_line list, fix MF-35), AC-04-01/02/03 (kolom list Product
     Variants: visibility, dedup MF-37, paritas visual MF-38). Modul ini backend-only (tidak
     ada Tour/HttpCase infrastruktur), jadi AC view-level ini hanya pernah diverifikasi manual
     via Docker sesi sebelumnya (MF-35/37/38 log), bukan regression test yang akan
     menangkap regresi diam-diam ke depannya.
Opsi: 1) Tulis unit test tambahan sekarang (arch-inspection get_view() untuk AC-04-01/02/03 +
     assert aritmetika pajak untuk AC-01-05 — keduanya feasible tanpa browser/Tour) sebelum
     menutup gate — Risiko keterlambatan: rendah-sedang.
     2) Lanjut ke Step 10 (QA/Business Flow) dengan gap ini didisclosure eksplisit di sana,
     karena Step 10 memang didesain untuk verifikasi UI/business-flow manual (AC-nya sendiri
     ditandai "Step 9/10", bukan cuma "Step 9") — Risiko: regresi UI baru bisa lolos tanpa
     terdeteksi otomatis di masa depan (siklus migrasi berikutnya).
     3) Disclosure + lanjut TANPA test tambahan, terima risiko permanen (konsisten pola MF-37
     yang sudah diterima Step 5 sebagai gap non-blocking) — Risiko: sedang.
Rekomendasi: Opsi 2 (lanjut ke Step 10 dengan gap didisclosure) — konsisten dengan label AC-nya
sendiri ("Step 9/10"), dan gap AC-04-02 (MF-37) sudah pre-accepted sejak Step 5. TAPI AC-01-05
direkomendasikan kuat ditambah unit test murah (Opsi 1 parsial) karena murni Python/backend,
tidak butuh Tour — biaya rendah, high-value untuk BSL formula inti.
Perlu keputusan user sebelum lanjut.
```

- [ ] ✅ Semua AC prioritas Unit/Integration pass tanpa syarat — lanjut ke step 10
- [x] ⚠️ Pass bersyarat: 0 failed/0 error pada semua test yang ADA, tapi 5 AC HIGH-RISK
  view/formula-level belum tercakup test otomatis (lihat eskalasi di atas) — user diminta memilih
  opsi sebelum gate dianggap final closed.
