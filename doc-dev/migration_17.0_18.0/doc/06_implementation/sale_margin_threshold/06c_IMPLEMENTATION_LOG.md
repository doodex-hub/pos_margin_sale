# Implementation Log — sale_margin_threshold

**Step:** 6 — Code Migration
**Ref:** `03_spec/sale_margin_threshold/03_MIGRATION_SPEC.md`, `migration-tool/templates/06a_CODE_MIGRATION_PHASES.md`
**Tanggal:** 2026-08-24

---

## Applicability Check

| Fase | Relevan? | Bukti/alasan (dari `01a` §2b) |
|---|---|---|
| C1 | ☑ Ya | `views/` ada 4 file XML |
| B2 | ☐ Tidak | Tidak ada field JSON/relasi berantai/dynamic model |
| C2 | ☑ Ya | Ekspresi `invisible=` dinamis di `views/products.xml`/`product_template_views.xml` |
| D1 | ☐ Tidak | `controllers/controllers.py` dead scaffold |
| D2 | ☐ Tidak | `assets.sale_margin_threshold._assets_sale` declare folder yang TIDAK EKSIS (`MF-08`) — tidak ada asset nyata untuk dimigrasi |
| E | ☐ Tidak | Tidak ada JS sama sekali di modul ini |
| F | ☐ Tidak | Tidak ada template Owl |

---

## Tabel Ringkas Status Fase

| Fase | Status | Tanggal |
|---|---|---|
| A1 | ✅ | 2026-08-24 |
| A2 | ✅ **Perubahan kode nyata** — lihat entri di bawah | 2026-08-24 |
| G1 (setelah A2/A3) | ✅ Pass (install sukses, exit code 0) | 2026-08-24 |
| A3 | ✅ (ACL sudah lengkap sejak 17.0, 2 baris wizard) | 2026-08-24 |
| A4 | ✅ (struktur konsisten) | 2026-08-24 |
| A5 | ✅ (tidak ada API ORM yang berubah) | 2026-08-24 |
| B1 | ✅ (model sederhana, tidak ada perubahan) | 2026-08-24 |
| B2 | N/A — dikonfirmasi Applicability Check | — |
| C1 | ✅ (xpath lain — `res_config_settings.xml`, `products.xml`, dll — terkonfirmasi match lewat G1 sukses) | 2026-08-24 |
| C2 | ✅ (sudah sintaks modern) | 2026-08-24 |
| D1 | N/A | — |
| D2 | N/A — dikonfirmasi Applicability Check (`MF-08`, tidak ada asset nyata) | — |
| E | N/A — dikonfirmasi Applicability Check | — |
| F | N/A — dikonfirmasi Applicability Check | — |
| G2 (validasi akhir/runtime) | ⏳ Belum dijalankan — lihat `05b_TEST_PLAN_MIGRATION.md` (verifikasi visual `views/sale_order.xml`, re-run `test_action_confirm_BATCH_MULTI_ORDER_F05`) | — |

## Riwayat Percobaan G1 (Install Test)

| # | Dijalankan setelah fase | Mode | Hasil | Error (kalau fail) | Tanggal |
|---|---|---|---|---|---|
| 1 | A1+A2 (ketiga modul, satu instance) | C | ✅ **Pass** — exit code 0, `sale_margin_threshold` loaded di posisi 64/67 | Tidak ada error dari file modul ini. **TAPI** ada 1 warning non-fatal TERKONFIRMASI dari bug existing `MF-06` — lihat detail di bawah "Entri" [Fase A2] | 2026-08-24 |

---

## Entri

## [Fase A1] Manifest Bootstrap

- **Scope:** `__manifest__.py`
- **Aksi:** `version: '17.0.1.0'` → `'18.0.1.0'`
- **Risiko:** LOW
- **Status:** ✅ Selesai

## [Fase A2] XML Tree → List (Mekanis) — PERUBAHAN KODE NYATA

- **Scope:** `views/sale_order.xml`
- **Item spec (ref):** `03_MIGRATION_SPEC.md` §2b Critical Migration Blockers #2, `02_DIFF_ANALYSIS.md` DIFF-01
- **Aksi:**
  - `views/sale_order.xml` baris 15: xpath `//page[@name='order_lines']/field[@name='order_line']/tree` → `.../list`
  - `views/sale_order.xml` baris 20: xpath `//page[@name='order_lines']/field[@name='order_line']/tree/field[@name='price_unit']` → `.../list/field[@name='price_unit']`
  - Komentar HTML di baris 14 diupdate ("tree view" → "list view") untuk konsistensi dokumentasi inline
- **Secara eksplisit TIDAK dilakukan:** tidak ada perubahan field/decoration/logic lain di file ini — HANYA nama tag di xpath expression
- **Risiko:** LOW (fix mekanis, high-confidence dari knowledge base) — **TERBUKTI BENAR**, lihat hasil G1 di bawah
- **Status:** ✅ Selesai, **terverifikasi lewat G1 nyata** (install sukses — kalau xpath masih `/tree`, `ParseError` pasti muncul karena `sale.view_order_form` core 18.0 memang sudah pakai `<list>`)

## [Fase A3] Security Hardening

- **Scope:** `security/ir.model.access.csv`
- **Aksi:** Dicek — 2 baris ACL (`sale_confirmation_wizard`, `wizard_margin_product`) sudah ada sejak 17.0, keduanya TransientModel dengan ACL eksplisit (sudah comply dengan requirement 18.0 soal ACL wizard wajib).
- **Status:** ✅ Selesai (tidak ada perubahan diperlukan)

## [Fase A4] Skeleton & Folder Integrity

- **Status:** ✅ Selesai (tidak ada perubahan diperlukan)

## [Fase A5] Python API Compatibility

- **Scope:** `models/sale_order.py`, `models/product.py`, `wizard/*.py`
- **Aksi:** Dicek terhadap `knowledge/version-diffs/17-to-18.md` §1 — tidak ada API yang diketahui berubah dipakai modul ini.
- **Status:** ✅ Selesai (tidak ada perubahan diperlukan — TERMASUK `action_confirm()` yang punya bug `MF-06`, SENGAJA TIDAK diperbaiki, lihat di bawah)

## G1 — Install Test #1 (setelah A1+A2, ketiga modul sekaligus)

- **Command:** `docker compose -f docker-env/docker-compose.yml up` (image `odoo:18.0`)
- **Mode:** C
- **Hasil:** exit code 0, `sale_margin_threshold` loaded bersih di posisi 64/67.
- **TEMUAN PENTING — `MF-06` bereaksi ulang, TERKONFIRMASI IDENTIK dengan 17.0:** saat modul core `sale_stock` (dependency transitif, bukan dependency modul ini) mencoba load demo data-nya sendiri, ada panggilan `action_confirm()` batch ke 4 sale order sekaligus (`sale_stock/data/sale_order_demo.xml`). Ini memicu override `action_confirm` modul ini, yang crash `ValueError: Expected singleton: sale.order(21, 22, 23, 24)` — PERSIS bug yang didokumentasikan `MF-06`/backfill F-05. Odoo menangkap exception ini secara graceful ("Module sale_stock demo data failed to install, installed without demo data") — **instalasi TIDAK gagal total**, cuma demo data `sale_stock` yang di-skip.
- **Kesimpulan:** `MF-06` **terverifikasi bermanifestasi identik di 18.0** — bug dipertahankan tanpa perubahan behavior, sesuai `CLAUDE.md` §Source of Truth (bug existing tidak diperbaiki). Efek samping baru yang PERLU DICATAT: bug ini sekarang terbukti bisa mengganggu proses install modul CORE Odoo lain (`sale_stock`) kalau modul ini terinstall bersamaan — sebelumnya cuma diketahui lewat test buatan sendiri (backfill), sekarang terbukti nyata di alur install produksi biasa.
- **Rekomendasi/keputusan:** dicatat sebagai update ke `MF-06` (lihat `FINDINGS.md`) — dampak naik dari "test-only" ke "mempengaruhi instalasi modul core lain di environment yang sama". Tetap TIDAK diperbaiki tanpa persetujuan eksplisit (prinsip port-kode-saja).

## [Fase B1] Model Risiko Rendah

- **Scope:** `models/product.py`, `wizard/sale_confirmation.py`, `wizard/wizard_margin_product.py`
- **Status:** ✅ Selesai (tidak ada perubahan diperlukan)

## [Fase C1] View Sederhana

- **Scope:** `views/products.xml`, `views/product_template_views.xml`, `views/res_config_settings.xml`
- **Aksi:** Dicek — semua xpath lain (ke `product.product_template_form_view`, `product.product_template_only_form_view`, `product.product_variant_easy_edit_view`, `sale.res_config_settings_view_form`) terkonfirmasi MATCH lewat G1 sukses (install tidak gagal di titik manapun selain yang sudah dicatat di atas).
- **Status:** ✅ Selesai, terverifikasi G1

## [Fase C2] Semantik XML & UX

- **Status:** ✅ Selesai (sudah sintaks modern, tidak ada perubahan)

---

## Temuan di Luar Spec

- [x] Tidak ada temuan STRUKTUR baru — TAPI ada eskalasi dampak `MF-06` (lihat entri G1 di atas), dicatat balik ke `FINDINGS.md`.

## Kontribusi ke Knowledge Base

- [ ] Ada — kandidat `dependency-compat/sale/17-to-18.md`: konfirmasi `<tree>`→`<list>` di embedded `order_line` view `sale.view_order_form` genuinely install-blocking di 18.0 (dikonfirmasi eksekusi nyata, bukan cuma baca PR) — dicatat ke `migration-records/pos-margin-sale_17.0_18.0/SUMMARY.md`.
