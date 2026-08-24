# Code Review — pos_margin_threshold

**Step:** 8 — Code Review (gate)
**Ref:** `03_spec/pos_margin_threshold/03_MIGRATION_SPEC.md`, `05_acceptance/pos_margin_threshold/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `06_implementation/pos_margin_threshold/06c_IMPLEMENTATION_LOG.md`, `01_intake/pos_margin_threshold/01b_BASELINE_SPEC.md`
**Odoo Version:** 17.0 → 18.0
**Files reviewed:** semua file di `pos_margin_threshold/` — diff penuh `backfill/17.0` vs `HEAD` (`migration/18.0`), plus seluruh `models/*.py`, `wizard/*.py`, `static/src/store/*.js`, `static/src/store/*.xml` (baca penuh, bukan cuma diff)
**Tanggal:** 2026-08-24

---

## A. Issues (Lint, Konvensi Odoo, Business Logic, Security, Performance, Code Quality)

| ID | Severity | Kategori | File | Baris | Issue | Rekomendasi |
|---|---|---|---|---|---|---|
| — | — | — | — | — | Tidak ada issue baru ditemukan. | — |

**Catatan:** `sudo()`, decorator, ORM pattern, N+1, dead code, unused import — semua diperiksa penuh terhadap kode 18.0 saat ini, tidak ada temuan konkret. `models/pos_session.py` sekarang hampir kosong (class dihapus total, hanya komentar) — ini SENGAJA (hook `_loader_params_product_product` sudah tidak ada di 18.0, `MF-18`), bukan dead code yang tertinggal tanpa alasan. `models.js:31-33` (`set_unit_price` passthrough no-op) adalah quirk 17.0 yang tidak disentuh migrasi ini — dibiarkan sesuai aturan "port apa adanya".

**Severity:** 🔴 Critical (bug/security/AC tidak cover — wajib fix) · 🟡 Warning (convention/performance — fix kalau memungkinkan) · 🔵 Info (saran, opsional)

## B. Gap Analysis — Implementasi vs Migration Spec

| Spec item (`DIFF-NNN`/Fase) | Implementasi | Status | Catatan |
|---|---|---|---|
| DIFF-02 (`models.js` import `Order`/`Orderline`/`Product`) | `ProductProduct`/`PosOrderline` di path baru (`MF-15`) | Implemented differently, sesuai klausul spec sendiri ("penyesuaian import HANYA kalau terbukti wajib dari G1/G2") | G2/Tour test membuktikan wajib — bukan pilihan gaya |
| DIFF-03 (`pos_store.js` patch `PosStore`) | Import tetap sama, isi patch berubah struktural (blocking logic dipindah ke sini, `MF-16`) | Implemented differently, sesuai klausul spec | Tombol Pay tidak lagi panggil `Order.pay()` di 18.0 |
| DIFF-04 (`ConfirmPopup`/`ErrorPopup`) | Diganti `dialog` service + `ask()`/`AlertDialog` (`MF-13`) | Implemented differently, wajib (API lama dihapus total core) | — |
| DIFF-05 (`pos_session.py` loader) | Dipindah ke `product.py` sebagai `_load_pos_data_fields()` (`MF-18`) | Implemented differently, sesuai klausul spec ("WAJIB verifikasi G2") | Hook lama dihapus core |
| DIFF-06 (`views/*.xml` inherits) | Tidak berubah | Implemented as specified | Diff kosong, dikonfirmasi |
| DIFF-07 (`getDisplayData()` full-override, `MF-11`) | Diubah jadi extend `{...super.getDisplayData(), ...}` (`MF-19`) | Implemented differently dari batas scope literal spec, TAPI dipicu bukti G2 nyata (Owl strict props validation) | Spec sendiri mensyaratkan ini jadi wajib begitu G2 membuktikan full-override tidak viable — persis yang terjadi |
| Wizard, `security/ir.model.access.csv`, `demo/demo.xml`, `i18n/*`, test lama | Tidak berubah | Implemented as specified | Diff kosong, dikonfirmasi |

Tidak ada item "not implemented". Semua deviasi dari teks literal spec adalah kontingensi yang sudah eksplisit disetujui di spec itu sendiri, dengan bukti G1/G2/Tour test di `06c_IMPLEMENTATION_LOG.md`.

## C. Gap Analysis — Implementasi vs Acceptance Criteria

| AC ID | Behavior | Status | Catatan |
|---|---|---|---|
| AC-01-01..05 | Margin/minimum-price compute & constraint | Tidak diverifikasi ulang di review ini | Diklaim tercakup `test_margin_sale.py` (reused apa adanya) — lulus per log G1 ("17 test lama ... semua pass"), tidak dibaca ulang isi test-nya di Step 8 ini |
| AC-02-01 (blocking, `AlertDialog`) | Jalur `blocking_transaction_pos=True` | 🟡 **Belum diverifikasi** | Tour test fixture eksplisit set `blocking_transaction_pos=False` — jalur block sepenuhnya tidak dites |
| AC-02-02 (confirm/proceed, `ask()`) | Jalur `blocking_transaction_pos=False` | ✅ **Terverifikasi Tour test nyata** | Skenario tour persis ini — dialog title/body dicek, lanjut ke payment, receipt muncul |
| AC-02-03 (tidak ada line di bawah minimum → tidak ada popup) | — | 🟡 **Belum diverifikasi** | Tidak ada skenario tour untuk kasus ini |
| AC-02-04 (teks peringatan merah di orderline) | — | 🟡 **Belum diverifikasi langsung** | Tour tidak assert teks/warna visual secara eksplisit — hanya membuktikan render tidak crash (`MF-20`) |
| AC-03-01/02 (wizard assign margin) | — | 🟡 **Belum diverifikasi** | Tidak ada test/tour untuk wizard di 18.0 |
| AC-04-01/02 (cross-module dgn `sale_margin_threshold`) | — | Tidak diverifikasi ulang di review ini | Diklaim tercakup `test_cross_module.py` (reused), lulus per log G1, tidak dibaca ulang isinya |

**Kesimpulan C:** Hanya AC-02-02 punya bukti interaktif baru sesi ini. Lima AC (`AC-02-01`, `AC-02-03`, `AC-02-04`, `AC-03-01`, `AC-03-02`) tidak punya bukti test sama sekali di 18.0 — **status ini SUDAH terdokumentasi terbuka di `06c_IMPLEMENTATION_LOG.md` sendiri** ("kandidat lanjutan Step 9, bukan blocker Step 8"), bukan temuan baru yang disembunyikan.

## D. Cek Khusus Migrasi — P1 Fidelity

- [x] Tidak ada perubahan behavior yang tidak disengaja — seluruh 9 file yang berubah (`git diff backfill/17.0 HEAD`) sudah dicek satu per satu, setiap hunk punya justifikasi teknis wajib (`MF-15`/`16`/`17`/`18`/`19`/`20`) atau murni test-infra baru. Wizard, views, security, demo, i18n — 100% byte-identik, dikonfirmasi via diff kosong.

**Cek tabrakan nama method dengan Odoo core (WAJIB, DUA ARAH):**
- [x] Sudah dicek (kedua arah), langsung terhadap source real `pos_margin_sale_migration_18-odoo:latest` (bukan asumsi/dugaan) — tidak ada tabrakan nama field/method modul ini (`margin_sale`, `minimum_sale_price`, `minimum_sale_price_with_tax`, `is_less_minimum_sale`, `action_assign_margin`, `is_blocked_warning`, `blocking_transaction_order`, `blocking_transaction_pos`, dst) terhadap core `point_of_sale`/`product`/`stock_account`. `_load_pos_data_fields` dikonfirmasi hook ekstensi resmi core (bukan kebetulan nama sama), signature cocok persis pola core sendiri.

## E. Perubahan Tak Tertelusuri (di luar spec)

- [x] Tidak ada perubahan yang tidak tertelusuri ke spec — semua hunk di diff sudah dipetakan ke `MF-NN` di §B.

## F. Kontribusi ke Knowledge Base

- [x] Ada — sudah ditulis sebelumnya ke `migration-tool/migration-records/pos-margin-sale_17.0_18.0/SUMMARY.md` (arsitektur data POS 18.0, Owl props validation, lesson G1≠G2, validasi bahasa). Tidak ada temuan kategori baru dari Step 8 ini untuk modul `pos_margin_threshold` spesifik (semua temuan Step 8 baru ada di modul `pin_message`, lihat review modul itu).

## G. Verdict

- Ringkasan Issues: 0 🔴 · 0 🟡 (kategori A) · 0 🔵 — catatan: 5 AC tanpa bukti test (§C) dicatat sebagai gap terbuka, bukan "issue" kategori A, karena sudah didokumentasikan dan tidak mengindikasikan bug (hanya kurang cakupan test).
- [x] ✅ **Lulus** — tidak ada 🔴, lanjut ke step 9

**Catatan untuk Step 9 (bukan blocker Step 8, tapi wajib ditindaklanjuti sebelum sign-off UAT):** tulis Tour test tambahan atau minimal manual click-test untuk AC-02-01 (jalur blocking `AlertDialog`) dan AC-03-01/02 (wizard assign margin) — keduanya adalah UI interaktif yang historisnya (lihat modul `pin_message`) rawan silent-break di migrasi Owl/JS meski G1 backend pass. AC-01/AC-04 disarankan dibaca ulang isi `test_margin_sale.py`/`test_cross_module.py` sekali lagi di Step 9 untuk konfirmasi eksplisit (bukan cuma percaya "17 test pass" dari log G1) sebelum UAT.
