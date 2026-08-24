# Migration Spec (Teknis) — pos_margin_threshold

**Step:** 3 — Migration Spec
**Versi:** 17.0 → 18.0
**Ref:** `02_diff/pos_margin_threshold/02_DIFF_ANALYSIS.md`
**Tanggal:** 2026-08-24

---

## 1. Ringkasan Strategi

Sisi Python + XML view modul ini relatif aman (tidak ada `<tree>`, tidak ada API ORM yang diketahui berubah). Risiko utama seluruhnya di sisi JS POS store (`models.js`, `pos_store.js`) — semua `[TIDAK TERVERIFIKASI]` karena tidak ada `native-target`. Strategi: port apa adanya dulu, jalankan G1 (install) — kalau sukses, lanjut G2 (browser, test jual produk di bawah minimum) untuk menangkap silent failure yang tidak kelihatan dari install sukses saja (khususnya `DIFF-05`, loader field POS).

## 2. Strategi per File/Simbol

| File/simbol | Ref `DIFF-NNN` | Strategi migrasi | Risiko | Ref `BSL-NNN` |
|---|---|---|---|---|
| `static/src/store/models/models.js` — import `Orderline, Product, Order` | DIFF-02 | Port apa adanya dulu, cek error console saat load POS (G2) | Tinggi, `[TIDAK TERVERIFIKASI]` | `[BSL-007]` |
| `static/src/store/pos_store.js` — import `PosStore` | DIFF-03 | Port apa adanya dulu | Tinggi | `[BSL-008]` |
| `static/src/store/models/models.js` — import `ConfirmPopup`/`ErrorPopup` | DIFF-04 | Port apa adanya dulu | Tinggi | `[BSL-003]` |
| `models/pos_session.py` — `_loader_params_product_product` | DIFF-05 | Port apa adanya, WAJIB verifikasi G2 (bukan cukup G1) — test end-to-end jual produk di bawah minimum, pastikan field benar-benar sampai ke frontend | Tinggi, silent-failure kalau salah | `[BSL-006]` |
| `views/*.xml` (inherit ke `product`/`stock_account`) | DIFF-06 | Port apa adanya, cek G1 | Sedang | `[BSL-010]` |
| `static/src/store/models/models.js` — `getDisplayData()` full-override | DIFF-07, `MF-11` | Port apa adanya (JANGAN diubah jadi extend `super()` kecuali G2 membuktikan field core baru genuinely hilang) | Sedang-Tinggi | `[BSL-007]` |
| `__manifest__.py` | — | Bump `version` → `18.0.1.0` | Rendah | — |

## 2b. Risk Analysis Terstruktur

### Critical Migration Blockers

| # | Isu | Lokasi | Rujukan knowledge base |
|---|---|---|---|
| 1 | Manifest version → `18.0.x` | `__manifest__.py:17` | Konvensi umum |
| 2 | (potensial) import path `@point_of_sale/app/store/models`/`@point_of_sale/app/store/pos_store`/popup path gagal resolve | `static/src/store/*.js` | DIFF-02/03/04, `[TIDAK TERVERIFIKASI]` — **tidak ada fix konkret yang bisa ditulis sekarang**, WAJIB verifikasi G1 dulu |

**Priority:** HIGH untuk item #2 — kalau bundle JS gagal load total karena import error, SELURUH modul (bukan cuma fitur margin) berpotensi tidak berfungsi di POS. Jalankan G1 SEDINI mungkin di Step 6 untuk modul ini, jangan ditunda.

### OWL Widget yang Butuh Rewrite/Review

| Widget | File | Risiko | Detail |
|---|---|---|---|
| Patch `Product`/`Orderline`/`Order` prototype (bukan komponen baru — `patch()` ke class core) | `static/src/store/models/models.js` | Tinggi | Bukan komponen Owl baru, tapi tetap tergantung class core `Orderline`/`Product`/`Order` masih ada dengan nama sama |
| Patch `PosStore` prototype | `static/src/store/pos_store.js` | Tinggi | Sama, tergantung class `PosStore` masih ada |

**Urutan wajib Step 6:** karena TIDAK ada template QWeb Owl kustom di modul ini (semua patch ke `.js` murni, prototype JS, bukan `t-inherit` XML template) — Fase E (JavaScript) relevan penuh, Fase F (Template) **N/A** untuk modul ini (beda dari `pin_message` yang punya keduanya).

### Controller & Route

Tidak ada — dead scaffold, dipertahankan.

### Assets & Dependency

Tidak ada isu — `assets.point_of_sale._assets_pos` menunjuk folder yang benar-benar eksis dan berisi file.

### Kompatibilitas Data Model

Tidak ada perubahan struktur data model core yang diketahui terkait modul ini.

### Risiko Integrasi

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | Interaksi runtime dengan `sale_margin_threshold` (`MF-01` per-variant margin shared, `MF-03` wizard MRO) — install bersamaan wajib untuk verifikasi Step 9/10 | `models/product.py`, `wizard/wizard_margin_product.py` | Sedang |

### Urutan Prioritas Testing

1. Install (G1) — prioritas verifikasi import JS tidak gagal
2. Buka POS session, pastikan tidak ada error console saat load (G2 awal)
3. Test end-to-end: jual produk di bawah minimum, pastikan warning/block muncul sesuai setting (`[BSL-003]`) — ini yang membuktikan `DIFF-05` (loader field) benar-benar jalan
4. Wizard assign margin massal (`[BSL-002]`)
5. Cross-module dengan `sale_margin_threshold`

### View List (dulu Tree) Checklist

Tidak berlaku — tidak ada `<tree>` di modul ini.

### Estimasi Effort

| Area | Effort | Catatan |
|---|---|---|
| Manifest version bump | Sangat rendah | Mekanis |
| JS POS store (verifikasi + kemungkinan penyesuaian import) | **Tidak bisa diestimasi sebelum G1** | Tergantung sepenuhnya hasil install nyata — bisa 0 perubahan (kalau semua path masih valid) atau signifikan (kalau arsitektur POS 18.0 berubah struktur) |
| Views | Rendah | Port langsung, verifikasi G1 |

## 3. Data Migration

N/A — port kode saja.

## 4. Scope

### Termasuk
- Bump `version` manifest.
- Port seluruh JS/Python/view apa adanya.
- Penyesuaian import path JS **HANYA kalau terbukti wajib dari hasil G1/G2** (bukan spekulasi) — ini termasuk kategori "wajib untuk kompatibilitas 18.0" yang diizinkan `CLAUDE.md`, bukan refactor bebas.

### Di Luar Scope
- Mengubah `getDisplayData()` (`MF-11`) jadi extend `super()` — kecuali G2 membuktikan field core baru hilang.
- Memperbaiki `MF-01`/`MF-02`/`MF-03`/`MF-04`.
