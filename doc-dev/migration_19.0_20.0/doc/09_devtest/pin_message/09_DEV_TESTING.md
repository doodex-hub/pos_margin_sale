# Dev Testing — pin_message

**Step:** 9 — Dev Testing (gate)
**Ref:** `05_acceptance/pin_message/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `05_acceptance/pin_message/05b_TEST_PLAN_MIGRATION.md`, characterization baseline (`01_intake/pin_message/01b_BASELINE_SPEC.md`)
**Tanggal:** 2026-09-23

---

> **Eksekusi:** dijalankan langsung via `docker compose -f docker-compose.20.yml exec` (stack
> `pos_margin_sale_migration_20`, container sudah up dari sesi sebelumnya) dengan `MSYS_NO_PATHCONV=1`
> di-prefix manual (bukan lewat `run-test.sh` — wrapper itu belum di-instansiasi di project ini;
> command mentah dipakai SADAR risiko MSYS path-mangling dan hasil disanity-check manual di bawah,
> bukan cuma dipercaya dari exit code).
> **Database KHUSUS untuk run ini:** `pos_margin_sale_migration_20_qa_v9` (fresh, dibuat sesi ini) —
> port `8140`, dipilih sengaja beda dari `pos_margin_sale_migration_20_qa` (Mode G2 server yang masih
> jalan di port 8078) dan dari db/port yang dipakai agent sibling untuk `pos_margin_threshold`
> (`_qa_v7`) dan `sale_margin_threshold` (`_qa_v8`) di container Docker yang SAMA, supaya ketiganya
> tidak bentrok.

## 9a. Audit Kesiapan Test — WAJIB sebelum eksekusi

**1. Registrasi (`tests/__init__.py`):** mengimpor KEDUA file test yang ada
(`test_pin_message`, `test_pin_message_tour`) — tidak ada file test yang tidak ter-load.

**2. Isi tiap method (AST stub-detection, `ast.parse` per method `test_*`, dijalankan nyata sesi ini
terhadap `pin_message/tests/test_*.py`):**

```
tests\test_pin_message.py test_toggle_pin_sets_true ok
tests\test_pin_message.py test_toggle_pin_sets_false_when_already_pinned ok
tests\test_pin_message.py test_toggle_pin_multi_record_safe ok
tests\test_pin_message_tour.py test_pin_message_toggle_pin_tour ok
tests\test_pin_message_tour.py test_pin_message_action_menu_pin_visible_tour ok
```

Kelima method **bukan stub** (semua punya body eksekusi nyata: assert langsung untuk 3 method Python,
`self.start_tour(...)` untuk 2 method tour). Tidak ada file hoot/JS unit test terpisah di bawah
`pin_message/static/tests/` — yang ada hanya `static/tests/tours/pin_message_tour.js` (definisi
langkah tour, dikonsumsi oleh `test_pin_message_tour.py`, bukan test Python/hoot berdiri sendiri).

**3. Cross-reference ke `05a_MIGRATION_ACCEPTANCE_CRITERIA.md`** (20 AC sub-item ditemukan di dokumen
— `AC-01-01..04`, `AC-02-01..05`, `AC-03-01..04`, `AC-04-01..02`, `AC-05-01..04`, `AC-06-01`; dekat
dengan "21 AC" yang disebut ringkasan project, selisih kecil tidak signifikan untuk audit ini):

| AC | Deskripsi singkat | File test | Status | Catatan |
|---|---|---|---|---|
| AC-01-01 | `toggle_pin()` False→True + broadcast bus | `test_pin_message.py::test_toggle_pin_sets_true` | ✅ Lengkap | Assert langsung `is_pinned` True setelah toggle. |
| AC-01-02 | `toggle_pin()` True→False | `test_pin_message.py::test_toggle_pin_sets_false_when_already_pinned` | ✅ Lengkap | Assert langsung. |
| AC-01-03 | Multi-record safe (`for message in self`) | `test_pin_message.py::test_toggle_pin_multi_record_safe` | ✅ Lengkap | Eksplisit kontras `MF-08`/`F-05`. |
| AC-01-04 ⚠️**RISIKO TINGGI** | `is_pinned` genuinely muncul di payload `_store_message_fields()` | — (tidak ada test langsung) | ⚠️ **Tidak ada assert langsung** | Tidak ada test yang membuka payload store secara eksplisit. Tour (`toggle_pin_tour`) hanya memverifikasi flip state LOKAL di client (optimistic update `onMessagePin`, bukan hasil `_store_message_fields()` dari fresh load) — badge count berasal dari `orm.searchRead` terpisah, BUKAN dari store field ini. Klaim "Match" di `08_CODE_REVIEW.md` berbasis desk-review kode (`res.attr()` dikonfirmasi baris-per-baris ke native), bukan bukti eksekusi. **Gap nyata, honestly flagged** — beda kategori risiko dari `AC-06-01` (di sini logic sudah diverifikasi statis sangat teliti + tidak ada indikasi gagal, hanya belum ada assert Tour eksplisit; `AC-06-01` di bawah belum ada tour SAMA SEKALI). |
| AC-02-01 | Dead-code branch `is_discussion` (quirk warisan) | — | N/A (disengaja) | Di luar scope migrasi (`03_MIGRATION_SPEC.md` §4), tidak butuh test baru. |
| AC-02-02 | RPC `toggle_pin` via action-menu "..." | `pin_message_action_menu_pin_visible_tour` | ✅ Lengkap (Tour) | Badge "1" muncul setelah klik entry action-menu. |
| AC-02-03 | RPC `toggle_pin` via tombol inline | `pin_message_toggle_pin_tour` | ✅ Lengkap (Tour) | Klik tombol inline → badge muncul → unpin. |
| AC-02-04 | Guard visibility (`message_type`/`is_discussion`/`subtype_description`) | Kedua tour (implisit, hanya jalur "qualifies") | ⚠️ Sebagian | Hanya jalur POSITIF (log note biasa) yang teruji. Jalur NEGATIF (`user_notification`/`auto_comment`/`notification`/`is_discussion=True`/`subtype_description` terisi — tombol TIDAK muncul) tidak pernah dieksekusi test manapun. Risiko rendah (guard adalah getter murni, tidak berubah dari 19.0), tidak ditandai "RISIKO TINGGI" di `05a`. |
| AC-02-05 ⚠️**RISIKO TINGGI** | Entry "Pin" genuinely TERENDER di action-menu | `pin_message_action_menu_pin_visible_tour` | ✅ Lengkap (Tour) | Tour klik buka action-menu, cek entry ada — bukan cuma cek tidak ada error. |
| AC-03-01 | Section hidden saat 0 pesan pinned | — | ⚠️ Tidak ada | Kedua tour selalu memulai dengan mem-pin sesuatu; skenario "thread kosong pinned" tidak pernah diuji eksplisit (implisit benar di state AWAL sebelum step pin pertama, tapi tidak ada assertion eksplisit atas itu). |
| AC-03-02 | Badge count N benar | `pin_message_toggle_pin_tour` (badge "1") | ✅ Lengkap (partial) | Hanya N=1 diverifikasi, bukan N>1. |
| AC-03-03 | Toggle collapse/expand via header | `pin_message_toggle_pin_tour` (step 7-8) | ✅ Lengkap (partial) | Expand diverifikasi (card muncul); re-collapse manual via header klik ulang tidak diverifikasi terpisah (section akhirnya hilang total via unpin, jalur kode beda). |
| AC-03-04 | `orm.searchRead` gagal → error ditelan senyap | — | ⚠️ Tidak ada | Tidak ada test yang mensimulasikan network/server error saat `initialLoad()`. |
| AC-04-01 ⚠️**RISIKO TERTINGGI (`MF-36`)** | Expand section TANPA crash | `pin_message_toggle_pin_tour` (step 7-8) | ✅ **Lengkap (Tour)** | **Regression test paling kritis di dokumen ini — PASSED.** Ini persis skenario yang dulu crash `TypeError: ...isSmall`. |
| AC-04-02 | Tombol "See"/jump ke pesan asli | — | ⚠️ **Tidak ada** | **Tidak ada tour yang benar-benar klik tombol "See".** Baik `06c_IMPLEMENTATION_LOG.md` maupun `08_CODE_REVIEW.md` menyebut ini "sudah lolos Tour", tapi membaca ulang `pin_message_tour.js` baris-per-baris: TIDAK ADA step yang men-trigger `.o-mail-MessageCard-jump`/tombol "See" di kedua tour. Klaim sebelumnya tidak akurat — dicatat sebagai temuan Step 9 ini, bukan cuma "belum dites", verifikasi hanya manual (browser) sesuai `06c`. |
| AC-05-01 | Ikon `push_pin` di action-menu (bukan kotak kosong) | `pin_message_action_menu_pin_visible_tour` | ⚠️ Sebagian | Tour memverifikasi entry "Pin" fungsional (badge jadi 1), tapi trigger selector-nya tidak secara spesifik mengunci `data-icon='push_pin'` pada entry action-menu itu sendiri (hanya `more_vert` untuk overflow icon). Icon name sendiri sudah dikonfirmasi benar via desk-review `08_CODE_REVIEW.md` `DIFF-04`. |
| AC-05-02 | Ikon inline `text-muted` (belum pin) | `pin_message_toggle_pin_tour` (step 5) | ✅ Lengkap (Tour) | Selector eksplisit `i[data-icon='push_pin'].text-muted`. |
| AC-05-03 | Ikon inline `text-primary` (sudah pin) | `pin_message_toggle_pin_tour` (step 9) | ✅ Lengkap (Tour) | Selector eksplisit `i[data-icon='push_pin'].text-primary`. |
| AC-05-04 | Styling kosmetik card (CSS) | — | ⚠️ Tidak ada | Murni CSS, tidak ada regresi logic mungkin — diterima sebagai risiko rendah (`08_CODE_REVIEW.md`). |
| AC-06-01 ⚠️**RISIKO TINGGI (`MF-33`, belum ada tour)** | Refresh section saat ganti thread | — | ❌ **Tidak ada** | **Dikonfirmasi ulang: benar-benar tidak ada tour untuk skenario ini.** Sudah diketahui sejak Step 8 (`08_CODE_REVIEW.md` I-01, "lulus dengan syarat"), bukan temuan baru — hanya diverifikasi manual satu kali. |

**Verdict audit (sebelum eksekusi):**
- [x] AC prioritas tinggi `AC-02-05` dan `AC-04-01` → Lengkap, siap eksekusi.
- [ ] **`AC-01-04` dan `AC-06-01` (dua AC berlabel RISIKO TINGGI/TERTINGGI di `05a`) TIDAK punya assert
  otomatis langsung** — dieskalasi di §Verdict di bawah, bukan diam-diam dianggap tercakup. Keduanya
  tetap dieksekusi ke Step 9 run (bukan diblokir total) karena: (a) `AC-01-04` sudah punya jejak
  desk-review sangat teliti (baris kode dikonfirmasi ke 2 pola native referensi) dan tidak ada indikasi
  gagal, (b) `AC-06-01` sudah diketahui & disetujui dev/Step 8 sebagai "lulus dengan syarat, tour
  wajib jadi prioritas Step 9/10" — bukan gap yang baru ditemukan sesi ini, sudah eksplisit
  direncanakan untuk ditindaklanjuti, bukan diabaikan.

## Baseline

- Characterization test / test asli source module: `pin_message/tests/test_pin_message.py` di branch
  `migration/19.0` — sama persis (3 method, semua sudah ada sejak backfill 18.0→19.0, dikonfirmasi
  `git diff migration/19.0 migration/20.0 -- pin_message/tests/` kosong untuk file ini). Tidak ada
  characterization test tambahan di luar `source-codebase` untuk modul ini (`doc-dev/backfill/`
  dikonfirmasi Step 1 hanya relevan untuk `sale_margin_threshold`/`MF-08`, bukan `pin_message`).
- Applicability Check Fase E (Owl/JS) dari Step 6: **Ya, applicable** (`pin_message` adalah patch
  Chatter/Message frontend) — 2 tour wajib ada, keduanya ADA dan keduanya PASS (lihat run di bawah).

## Hasil Unit, Integration & Tour Test (target-codebase)

**Run resmi Step 9 (2026-09-23), fresh database `pos_margin_sale_migration_20_qa_v9`, port `8140`,
container `pos_margin_sale_migration_20-odoo-1` (Docker 20.0, real headless Chrome, `--test-enable`,
`--test-tags=/pin_message`):**

```
odoo.tests.stats: pin_message: 9 tests 21.55s 877 queries
odoo.tests.stats: web: 6 tests 0.01s 14 queries
odoo.tests.result: 0 failed, 0 error(s) of 7 tests when loading database 'pos_margin_sale_migration_20_qa_v9'
```

(7 test dihitung ke summary utama: 3 unit `TestPinMessage` + 2 tour `TestPinMessageTour` + 2 test
`web.tests.test_js` bawaan framework yang auto-register, bukan milik modul ini. Sanity-check
anti-false-pass: log memuat baris `Starting TestPinMessage.test_toggle_pin_multi_record_safe`,
`Starting TestPinMessageTour.test_pin_message_action_menu_pin_visible_tour` dst — 5 baris `Starting`
untuk 5 method modul ini, cocok jumlahnya, DAN dua banner eksplisit `TOUR ... SUCCEEDED` untuk kedua
tour — bukan MSYS tag-mangling false-pass 0/0/0.)

| AC | Unit | Integration | Tour (Owl/JS) | Pass/Fail | Catatan |
|---|---|---|---|---|---|
| AC-01-01/02/03 | ✅ pass | — | — | ✅ Pass | 3 method Python, semua pass. |
| AC-01-04 | — | — | ⚠️ tidak diassert langsung | N/A (tidak diuji) | Lihat §9a — gap dicatat, tidak memblokir run. |
| AC-02-01 | — | — | — | N/A | Dead code, di luar scope test. |
| AC-02-02/03 | — | — | ✅ pass | ✅ Pass | Kedua entry-point RPC berfungsi. |
| AC-02-04 | — | — | ⚠️ partial | ✅ Pass (jalur positif saja) | Jalur negatif guard tidak teruji. |
| AC-02-05 | — | — | ✅ pass | ✅ Pass | Entry "Pin" genuinely terender. |
| AC-03-01/04 | — | — | ⚠️ tidak diuji | N/A (tidak diuji) | — |
| AC-03-02/03 | — | — | ✅ pass (partial) | ✅ Pass | N=1 & expand saja. |
| AC-04-01 (`MF-36`) | — | — | ✅ **pass** | ✅ **Pass** | Regression test paling kritis — expand section TANPA crash, dikonfirmasi bersih. |
| AC-04-02 | — | — | ❌ tidak ada tour | N/A (tidak diuji) | Tombol "See"/jump tidak pernah diklik test manapun — koreksi klaim lama. |
| AC-05-01 | — | — | ⚠️ partial | ✅ Pass (fungsional, bukan icon-specific) | — |
| AC-05-02/03 | — | — | ✅ pass | ✅ Pass | Warna ikon state eksplisit diverifikasi. |
| AC-05-04 | — | — | — | N/A (tidak diuji) | CSS murni, risiko rendah. |
| AC-06-01 (`MF-33`) | — | — | ❌ tidak ada tour | ❌ **Belum diverifikasi otomatis** | Gap tertua & paling penting yang tersisa — lihat Verdict. |

## Kontribusi ke Knowledge Base

- [x] Tidak ada temuan baru yang perlu dicatat ke `migration-records/pos-margin-sale_19.0_20.0/SUMMARY.md`
  — run ini adalah re-konfirmasi (`0 failed, 0 error`) atas fix yang sudah diketahui (`MF-28`/`MF-32`/
  `MF-33`/`MF-36`), bukan perilaku Odoo baru yang belum tertangkap Step 2. Satu catatan proses (bukan
  kandidat knowledge base, murni klarifikasi dokumentasi internal project ini): klaim "AC-04-02 sudah
  lolos Tour" di `06c_IMPLEMENTATION_LOG.md`/`08_CODE_REVIEW.md` **tidak akurat** — tour yang ada
  memverifikasi expand (`AC-04-01`) tapi TIDAK memverifikasi klik tombol "See" (`AC-04-02`). Perbaikan
  dokumentasi ini cukup dicatat di sini, tidak perlu entry `SUMMARY.md` terpisah karena bukan temuan
  perilaku Odoo, melainkan koreksi akurasi klaim testing internal.

## Verdict

- [x] ✅ **Lulus dengan syarat eksplisit — lanjut ke Step 10**, dengan catatan berikut WAJIB
  ditindaklanjuti (bukan diam-diam dianggap selesai):

**Hasil run:** `0 failed, 0 error(s) of 7 tests` — bersih, genuinely dieksekusi (bukan false-pass
MSYS), termasuk kedua Tour (`pin_message_toggle_pin_tour`, `pin_message_action_menu_pin_visible_tour`)
yang keduanya PASS bersih dengan banner `TOUR ... SUCCEEDED`, mencakup skenario regresi paling kritis
di dokumen ini (`AC-04-01`/`MF-36` — expand "Pinned Messages" tanpa crash). `pin_message` tetap
satu-satunya dari ketiga modul dengan Tour coverage otomatis genuinely lolos sebelum Step 9 formal ini.

**Gap yang TERBUKA, dua tingkat prioritas berbeda:**

1. **`AC-06-01` (thread-switch refresh, `MF-33`/`DIFF-03`) — prioritas tertinggi, follow-up
   sebelum modul ini dianggap benar-benar tuntas.** Tidak ada tour otomatis sama sekali untuk skenario
   ganti thread dalam satu instance Chatter yang sama. `08_CODE_REVIEW.md` (Step 8) sudah mengonfirmasi
   independen bahwa risiko timing `useOnChange` (native) vs `onWillUpdateProps` (modul ini) genuinely
   masih terbuka di kode native 20.0 aktual — bukan sekadar kekhawatiran lama yang basi. Verifikasi
   manual informal sudah dilakukan sekali, tapi bukan pengganti tour otomatis. **Rekomendasi konkret:**
   tulis tour baru (`pin_message_thread_switch_tour`) sebelum Step 10 — buka chatter record A dengan
   pesan pinned, navigasi ke record B, assert badge/section ter-refresh sesuai B (kosong atau count
   benar), sebelum modul ini disebut selesai secara genuine.
2. **`AC-01-04` (store payload `is_pinned`) dan `AC-04-02` (tombol jump "See") — prioritas sedang,
   temuan Step 9 ini sendiri (bukan cuma warisan Step 8).** Keduanya diklaim "sudah teruji" di dokumen
   sebelumnya, tapi audit AST + baca ulang tour baris-per-baris sesi ini menunjukkan tidak ada assert
   otomatis untuk keduanya. Risiko lebih rendah dari `AC-06-01` (logic sudah diverifikasi statis
   teliti, tidak ada indikasi kegagalan), tapi tetap gap bukti eksekusi yang jujur harus dicatat,
   bukan diwariskan sebagai "selesai" ke Step 10/11.

Tidak ada AC yang GAGAL (semua yang teruji, pass) — verdict "lulus dengan syarat" murni karena
cakupan test, bukan karena ada kegagalan aktual.
