# Migration Spec (Teknis) — sale_margin_threshold

**Step:** 3 — Migration Spec
**Versi:** 17.0 → 18.0
**Ref:** `02_diff/sale_margin_threshold/02_DIFF_ANALYSIS.md`
**Tanggal:** 2026-08-24

> Dokumen ini memandu implementasi Step 6. Dasar testing tetap `01b_BASELINE_SPEC.md`, bukan dokumen ini.

---

## 1. Ringkasan Strategi

Modul ini didominasi SATU Critical Migration Blocker konkret (`DIFF-01`, `<tree>`→`<list>`) yang sudah bisa langsung ditulis fix-nya (bukan `[TIDAK TERVERIFIKASI]` seperti kebanyakan temuan Step 2 project ini). Sisanya sebagian besar port langsung — tidak ada Owl/JS component di modul ini sama sekali (`MF-08`: asset key declare folder yang tidak eksis, jadi murni tidak ada kerja JS). Fokus Fase A (install blocker) di Step 6: fix `DIFF-01`, verifikasi 2 xpath lain yang `[TIDAK TERVERIFIKASI]` (`DIFF-05` settings block, `DIFF-06` XML-ID product view).

## 2. Strategi per File/Simbol (ringkasan umum)

| File/simbol | Ref `DIFF-NNN` | Strategi migrasi | Risiko | Ref `BSL-NNN` |
|---|---|---|---|---|
| `views/sale_order.xml` (2 xpath ke `.../tree` dan `.../tree/field[...]`) | DIFF-01 | Ganti literal `/tree` → `/list` di kedua xpath expression | Rendah (fix mekanis persis, sudah dikonfirmasi high-confidence) | `[BSL-007]` (decoration harga di bawah minimum) |
| `models/sale_order.py` — `action_confirm()` | DIFF-02 | Port apa adanya (TIDAK memperbaiki bug singleton `MF-06`) — hanya port, tidak ada perubahan logic | Sedang — bug existing harus tetap identik, verifikasi ulang di Step 9 dengan test yang sama | `[BSL-001]`, `[BSL-002]` |
| `views/product_template_views.xml` + `views/products.xml` (duplikasi XML-ID) | DIFF-03 | Port apa adanya — JANGAN diberi XML-ID berbeda/dihapus salah satu (itu memperbaiki `MF-07`, di luar scope port-kode-saja) | Rendah (mekanisme ORM stabil) | `[BSL-008]` |
| `views/products.xml`, `views/product_template_views.xml` (ekspresi `invisible=`) | DIFF-04 | Port apa adanya, sudah sintaks modern | N/A | `[BSL-010]` |
| `views/res_config_settings.xml` (xpath `block[@name='quotation_order_setting_container']`) | DIFF-05 | Port apa adanya dulu, coba install — kalau `ParseError`, cari nama block baru di form Settings Sales 18.0 (butuh `native-target` ATAU baca error message + inspect DOM Settings 18.0 langsung di instance test) | Sedang — install-blocking kalau salah, tapi errornya eksplisit (ParseError), gampang dideteksi G1 | — |
| `views/products.xml`, `views/product_template_views.xml` (inherit_id `product.*`) | DIFF-06 | Port apa adanya dulu, sama seperti DIFF-05 | Sedang | `[BSL-005]`, `[BSL-010]` |
| `security/groups.xml`, `_register_hook()` | DIFF-07, `MF-05` | Port apa adanya | Rendah | `[BSL-006]` |
| `__manifest__.py` | — | Update `version: '17.0.1.0'` → `'18.0.1.0'` (WAJIB, konvensi versi manifest Odoo) | Rendah | — |

## 2b. Risk Analysis Terstruktur

### Critical Migration Blockers
*(Mencegah instalasi di 18.0)*

| # | Isu | Lokasi | Rujukan knowledge base |
|---|---|---|---|
| 1 | Manifest version harus `18.0.x` | `__manifest__.py:17` (`version: '17.0.1.0'`) | `knowledge/version-diffs/17-to-18.md` (konvensi umum) |
| 2 | **`<tree>`→`<list>` di 2 xpath** — `views/sale_order.xml` baris 15 & 20 | `views/sale_order.xml` | `knowledge/version-diffs/17-to-18.md` §1, DIFF-01 — **HIGH CONFIDENCE, PR resmi odoo/odoo#159909** |
| 3 | (potensial) xpath `block[@name='quotation_order_setting_container']` gagal match | `views/res_config_settings.xml` | DIFF-05, `[TIDAK TERVERIFIKASI]` — verifikasi G1 |
| 4 | (potensial) xpath inherit ke `product.product_template_form_view`/`product.product_template_only_form_view`/`product.product_variant_easy_edit_view` gagal match | `views/products.xml`, `views/product_template_views.xml` | DIFF-06, `[TIDAK TERVERIFIKASI]` — verifikasi G1 |

**Priority:** HIGH — item #1 dan #2 WAJIB diperbaiki sebelum G1 pertama kali dijalankan (item #2 dijamin gagal kalau tidak diperbaiki, berdasar knowledge base high-confidence). Item #3/#4 baru terlihat SAAT G1 dijalankan (kalau gagal, `ParseError` akan eksplisit sebut xpath mana yang tidak match).

### OWL Widget yang Butuh Rewrite/Review

Tidak ada — modul ini tidak punya Owl/JS component (`MF-08`, asset key declare folder kosong).

### Controller & Route

Tidak ada — `controllers/controllers.py` seluruh isi di-comment (dead scaffold, dipertahankan apa adanya).

### Assets & Dependency

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | `assets.sale_margin_threshold._assets_sale` menunjuk folder yang tidak eksis (`MF-08`) | `__manifest__.py` | Rendah — port apa adanya, JANGAN dihapus (itu "membersihkan", di luar scope) |

### Kompatibilitas Data Model

Tidak ada perubahan struktur data model yang diketahui — field `margin_sale`/`minimum_sale_price`/`minimum_sale_price_with_tax`/`blocking_transaction_order` semuanya field custom modul ini sendiri, bukan field core yang direname.

### Risiko Integrasi

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | Interaksi runtime dengan `pos_margin_threshold` (`MF-03` wizard MRO, `MF-05` register hook) — WAJIB kedua modul diinstall bersamaan saat testing Step 9/10 untuk verifikasi cross-module | `wizard/wizard_margin_product.py`, `models/product.py` | Sedang — lihat `CLAUDE.md` §Adaptasi multi-modul soal batasan testing cross-module |
| 2 | `hasattr(self, 'is_rental_order')` — deteksi modul rental opsional | `models/sale_order.py:14` | Rendah, tapi kalau ada modul rental terinstall di environment test, WAJIB dicek behavior skip-nya tetap sama |

### Urutan Prioritas Testing

1. Install & startup — fix `DIFF-01` dulu, baru coba install (G1)
2. Kalau G1 gagal di xpath lain (`DIFF-05`/`DIFF-06`) — baca pesan `ParseError`, sesuaikan
3. Core user flow: confirm quotation single-order (blocking + wizard confirm), lihat `[BSL-001]`
4. Batch-confirm crash (`MF-06`) — re-run `test_action_confirm_BATCH_MULTI_ORDER_F05`, pastikan behavior identik (masih crash dengan cara yang sama)
5. Cross-module: install bersama `pos_margin_threshold`, verifikasi `MF-03`/`MF-05`

### View List (dulu Tree) Checklist

| # | Apa | Di mana | Perubahan |
|---|---|---|---|
| 1 | Inline tree di form (embedded order_line list) | `views/sale_order.xml` xpath `.../field[@name='order_line']/tree` (2 tempat) | `<tree>` (dalam xpath expression) → `<list>` |

### Estimasi Effort

| Area | Effort | Catatan |
|---|---|---|
| Fix `DIFF-01` (`/tree`→`/list`) | Sangat rendah (2 baris) | Mekanis, high-confidence |
| Manifest version bump | Sangat rendah | Mekanis |
| Verifikasi xpath lain (G1) | Rendah-Sedang | Tergantung hasil install pertama |
| Python (`action_confirm`, dll) | Sangat rendah | Port langsung, tidak ada API yang diketahui berubah |

## 3. Data Migration

N/A — port kode saja, tidak ada data produksi (Step 7 tidak dikerjakan).

## 4. Scope

### Termasuk
- Fix `DIFF-01` (`<tree>`→`<list>`) — **wajib untuk kompatibilitas 18.0**, bukan opsional.
- Bump `version` manifest ke `18.0.1.0`.
- Port seluruh business logic apa adanya, termasuk semua bug/quirk existing (`MF-03`, `MF-05`, `MF-06`, `MF-07`, `MF-08`).

### Di Luar Scope (sengaja, disetujui di intake)
- Memperbaiki `MF-06` (batch-confirm crash) — tetap dipertahankan sebagai bug identik.
- Konsolidasi wizard `MF-03` — di luar "port kode saja".
- Membersihkan `MF-07` (duplikasi XML-ID) atau `MF-08` (asset key tidak eksis) — dipertahankan apa adanya.
