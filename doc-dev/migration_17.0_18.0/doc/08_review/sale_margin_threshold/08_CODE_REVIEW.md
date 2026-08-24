# Code Review — sale_margin_threshold

**Step:** 8 — Code Review (gate)
**Ref:** `03_spec/sale_margin_threshold/03_MIGRATION_SPEC.md`, `05_acceptance/sale_margin_threshold/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `06_implementation/sale_margin_threshold/06c_IMPLEMENTATION_LOG.md`, `01_intake/sale_margin_threshold/01b_BASELINE_SPEC.md`
**Odoo Version:** 17.0 → 18.0
**Files reviewed:** semua file di `sale_margin_threshold/` — diff penuh `backfill/17.0` vs `HEAD`, plus seluruh `models/*.py`, `wizard/*.py`, `views/*.xml`, `security/*` (baca penuh)
**Tanggal:** 2026-08-24

---

## A. Issues (Lint, Konvensi Odoo, Business Logic, Security, Performance, Code Quality)

| ID | Severity | Kategori | File | Baris | Issue | Rekomendasi |
|---|---|---|---|---|---|---|
| — | — | — | — | — | Tidak ada issue baru ditemukan. | — |

**Catatan:** modul ini adalah port paling minimal dari ketiganya — hanya 2 baris berubah dari 17.0 (`__manifest__.py` version bump, `views/sale_order.xml` `<tree>`→`<list>` ×2). Seluruh `models/`, `wizard/`, `security/`, `demo/`, `controllers/`, sisa `views/` byte-identik. `sudo()` (1 pemakaian, baca `ir.config_parameter`), decorator, ACL — semua tidak berubah dari 17.0, tidak ada temuan baru. Dua quirk pre-existing dicatat untuk kelengkapan, TIDAK dianggap issue migrasi (unchanged dari 17.0, di luar scope "port apa adanya"): `models/product.py` — `_set_product_margin_sale` didekor `@api.onchange` padahal berfungsi sebagai inverse method (tidak lazim tapi berfungsi, warisan 17.0); `wizard/wizard_margin_product.py` — method `action_assing_margin` (typo "assing", konsisten dgn XML, tidak pernah diperbaiki karena bukan bug baru).

**Severity:** 🔴 Critical (bug/security/AC tidak cover — wajib fix) · 🟡 Warning (convention/performance — fix kalau memungkinkan) · 🔵 Info (saran, opsional)

## B. Gap Analysis — Implementasi vs Migration Spec

| Spec item (`DIFF-NNN`/Fase) | Implementasi | Status | Catatan |
|---|---|---|---|
| DIFF-01 (`<tree>`→`<list>`, `sale_order.xml`) | 2 xpath diubah | Implemented as specified | Install-blocking kalau tidak diperbaiki, dikonfirmasi |
| DIFF-02 (`action_confirm`, port as-is + `MF-06`) | Tidak berubah | Implemented as specified | Bug batch-confirm 17.0 dipertahankan sesuai aturan proyek |
| DIFF-03 (duplikasi XML-ID, port as-is) | Tidak berubah | Implemented as specified | Override behavior dipertahankan identik |
| DIFF-04 (`invisible=`, port as-is) | Tidak berubah | Implemented as specified | — |
| DIFF-05 (`res_config_settings.xml` xpath, verify) | Tidak berubah, diverifikasi valid | Implemented as specified, independently verified | `quotation_order_setting_container` dikonfirmasi masih ada di core 18.0 (bukan cuma "G1 tidak komplain") |
| DIFF-06 (xpath views `product`, verify) | Tidak berubah, diverifikasi valid | Implemented as specified, independently verified | Ketiga record ID (`product_template_form_view`, dst) dikonfirmasi ada di core 18.0 |
| DIFF-07 (`_register_hook`, port as-is, `MF-05`) | Tidak berubah | Implemented as specified | Mekanisme `_register_hook` core tidak berubah relevan |
| Wizard, test lama | Tidak berubah | Implemented as specified | — |

Tidak ada item "implemented differently" atau "not implemented" — spec-nya sempit dan dieksekusi persis seperti tertulis.

## C. Gap Analysis — Implementasi vs Acceptance Criteria

| AC ID | Behavior | Status | Catatan |
|---|---|---|---|
| AC-01-01 (blocking `ValidationError`) | — | ✅ **Terverifikasi** | `test_action_confirm_blocking_below_minimum`, pass di full run |
| AC-01-02 (wizard path, not blocking) | — | ✅ **Terverifikasi** | `test_action_confirm_wizard_path_when_not_blocking` — test yang sama juga yang menemukan `MF-21` |
| AC-01-03 (tidak ada isu → confirm langsung) | — | ✅ **Terverifikasi** | `test_action_confirm_normal_no_price_issue` |
| AC-01-04 (rental order → skip) | — | 🟡 **Belum diverifikasi, tidak bisa dites di environment ini** | Tidak ada modul rental (Enterprise-only) terinstall — environment Community tidak bisa menguji jalur ini sama sekali |
| AC-02-01 (batch-confirm crash dipertahankan, `MF-06`) | — | ✅ **Terverifikasi, 2 sumber independen** | `test_action_confirm_BATCH_MULTI_ORDER_F05` pass (`ValueError` tetap muncul) + korroborasi terpisah dari observasi demo data `sale_stock` di log G1 |
| AC-03-01 (wizard confirm → skip_check_price) | — | ✅ **Terverifikasi** | Inline di `test_action_confirm_wizard_path_when_not_blocking` |
| AC-03-02 (wizard cancel → no-op) | — | 🟡 **Belum diverifikasi** | Tidak ada test yang klik "Cancel"; risiko rendah (`special="cancel"` murni deklaratif form, tidak ada server call), tapi tidak ada assertion eksplisit |
| AC-04-01 (dedup group saat kedua modul terinstall) | — | ✅ **Terverifikasi, kondisional** | `test_cross_module.py` — `skipTest` kalau `pos_margin_threshold` tidak terinstall bersamaan; run G1/G2 terakhir memang meng-install ketiga modul sekaligus, jadi assertion ini benar-benar tereksekusi (bukan ter-skip) |
| AC-04-02 (MRO tergantung urutan install, arah reverse) | — | 🟡 **Belum diverifikasi untuk modul ini secara spesifik** | Test MRO/`__mro__` HANYA ada di `pos_margin_threshold/tests/test_cross_module.py` (install order `pos_margin_threshold,sale_margin_threshold`). Tidak ada test setara di `sale_margin_threshold/tests/` dengan urutan instalasi terbalik — AC ini butuh urutan spesifik untuk membuktikan MRO tergantung urutan install (bukan identitas modul), belum ada bukti dari sisi modul ini |
| AC-04-03 (`module_pos_margin_threshold` sembunyikan field UI) | — | 🟡 **Belum diverifikasi sama sekali** | Tidak ada test/tour yang assert field benar-benar tersembunyi di form yang dirender — murni compute Python trivial, tapi ACnya tentang UI visibility, belum ada bukti apapun |

**Kesimpulan C:** cakupan test cukup kuat untuk jalur inti (`AC-01-01..03`, `AC-02-01`, `AC-03-01`) — termasuk `MF-06` yang justru terkorroborasi dua sumber independen. Empat gap (`AC-01-04`, `AC-03-02`, `AC-04-02`, `AC-04-03`) genuinely tidak punya bukti test — `AC-01-04` tidak bisa dites sama sekali di environment ini (butuh Enterprise), tiga sisanya berisiko rendah secara teknis tapi tetap gap dokumentasi yang harus eksplisit, bukan diasumsikan aman.

## D. Cek Khusus Migrasi — P1 Fidelity

- [x] Tidak ada perubahan behavior yang tidak disengaja — hanya 2 baris berubah dari 17.0, keduanya wajib install-blocking, sisanya byte-identik (dikonfirmasi `git diff --stat` kosong untuk semua subpath lain).

**Cek tabrakan nama method dengan Odoo core (WAJIB, DUA ARAH):**
- [x] Sudah dicek (kedua arah), langsung terhadap source real `pos_margin_sale_migration_18-odoo:latest` — tidak ada tabrakan nama field/method modul ini terhadap core `sale`/`product`/`base`/`stock_account`. `action_confirm` adalah override legitimate (`super()` dipanggil), `_register_hook` ada di core pada model-model lain (tidak bentrok dengan `product.product`).

## E. Perubahan Tak Tertelusuri (di luar spec)

- [x] Tidak ada perubahan yang tidak tertelusuri ke spec.

## F. Kontribusi ke Knowledge Base

- [ ] **Ada, kandidat baru belum ditulis** — nuansa `MF-21` yang ditemukan Step 8: jejak kode (`fields.py`, 17.0 vs 18.0) menunjukkan mekanisme bilingual EN/FR modul ini (`with_context(lang='fr_FR').write(...)`) kemungkinan **sudah silently broken di 17.0 juga** kalau bahasa Prancis tidak pernah terinstall di database manapun (tulisan kedua akan jatuh ke key `en_US` yang sama, menimpa teks Inggris) — 18.0 mengubah kegagalan senyap ini jadi crash eksplisit, bukan memperkenalkan bug baru. Ini nuansa penting untuk keputusan dev soal `MF-21` (lihat §G) — direkomendasikan ditambahkan ke `FINDINGS.md` `MF-21` dan/atau `migration-records/.../SUMMARY.md`.

## G. Verdict

- Ringkasan Issues: 0 🔴 · 0 🟡 (kategori A) · 0 🔵 — 4 AC tanpa bukti test (§C) dan 1 catatan deployment (`MF-21`) dicatat sebagai gap terbuka/butuh keputusan dev, bukan bug kode.
- [x] ✅ **Lulus** — tidak ada 🔴, lanjut ke step 9

**Item yang butuh tindak lanjut sebelum UAT (bukan blocker Step 8):**
1. **`MF-21` — WAJIB dikonfirmasi ke dev sebelum go-live:** environment production harus punya bahasa Prancis (`fr_FR`) benar-benar terinstall, atau `action_confirm()` jalur wizard (non-blocking) akan crash `UserError` di 18.0. Rekomendasikan menambahkan nuansa "kemungkinan sudah silently broken di 17.0 tanpa Prancis terinstall" (temuan §F) ke percakapan konfirmasi ini — pertanyaannya bukan cuma "apakah Prancis terinstall" tapi juga "apakah fitur bilingual ini pernah benar-benar berfungsi di production 17.0".
2. Tulis test untuk AC-03-02 (klik Cancel di wizard) — trivial, risiko rendah, tapi mudah ditutup.
3. Tulis test MRO urutan instalasi terbalik (`-i sale_margin_threshold,pos_margin_threshold`) untuk melengkapi bukti AC-04-02 dari sisi modul ini.
4. AC-04-03 (UI field visibility) dan AC-01-04 (rental) — didokumentasikan sebagai gap yang genuinely tidak bisa/belum ditutup di environment ini; putuskan bersama dev apakah ini cukup penting untuk effort tambahan sebelum UAT atau diterima sebagai risiko rendah yang didokumentasikan.
