# Migration Spec (Teknis) — pos_margin_threshold

**Step:** 3 — Migration Spec
**Versi:** 18.0 → 19.0
**Ref:** `02_diff/pos_margin_threshold/02_DIFF_ANALYSIS.md`
**Tanggal:** 2026-08-26

> Dokumen ini memandu IMPLEMENTASI (step 6). Ini **bukan** dasar testing/acceptance criteria —
> itu datang dari `01b_BASELINE_SPEC.md`. Lihat step 5.

---

## 1. Ringkasan Strategi

Python (`models/`, `wizard/`) **tidak butuh perubahan apapun** kecuali rename kosmetik param
opsional (`DIFF-05`). Seluruh pekerjaan nyata ada di JS/Owl (`static/src/store/`) — 3 area:
(a) tiga import path yang pindah (mekanis, low-risk), (b) porting mekanisme
`getDisplayData()`/`props.line.shape` jadi getter langsung di record model (perlu rewrite, bukan
cuma rename), (c) rename massal method core snake_case→camelCase di `pos_store.js` yang di-`pay()`
override (mekanis tapi wajib teliti — satu method, `get_unit_display_price`, tidak punya pengganti
nama persis). `orderline.xml` dan dialog service **tidak butuh perubahan**. Manifest version bump
`18.0.x.x`→`19.0.1.0` (atau skema versi yang disepakati dev).

## 2. Strategi per File/Simbol (ringkasan umum)

| File/simbol | Ref `DIFF-NNN` | Strategi migrasi | Risiko | Ref `BSL-NNN` |
|---|---|---|---|---|
| `static/src/store/models/models.js:5` import `Orderline` | `DIFF-01` | Ganti path `@point_of_sale/app/generic_components/orderline/orderline` → `@point_of_sale/app/components/orderline/orderline` | Rendah — mekanis | — |
| `static/src/store/pos_store.js:2` import `PosStore` | `DIFF-02` | Ganti path `@point_of_sale/app/store/pos_store` → `@point_of_sale/app/services/pos_store` | Rendah — mekanis | — |
| `static/src/store/pos_store.js:6` import `ask` | `DIFF-03` | Ganti path `@point_of_sale/app/store/make_awaitable_dialog` → `@point_of_sale/app/utils/make_awaitable_dialog` | Rendah — mekanis | — |
| `models/product.py:103-107` `_load_pos_data_fields` | `DIFF-05` | Opsional: rename parameter lokal `config_id`→`config` demi kejelasan (tetap fungsional tanpa perubahan apapun) | Sangat rendah | `BSL-009` |
| `static/src/store/models/models.js:12-16` `patch(Orderline.props.line.shape, {...})` | `DIFF-06` | **HAPUS patch ini sepenuhnya** — mekanisme `.shape` tidak ada lagi di 19.0 | Kritis kalau tidak diporting | `BSL-014` |
| `static/src/store/models/models.js:35-43` `patch(PosOrderline.prototype, {getDisplayData(){...}})` | `DIFF-07` | **Ganti pola:** hapus patch `getDisplayData()`, tambahkan 2 getter baru langsung di `PosOrderline` (`get isLessMinimumSalePrice()`, `get minimumSalePriceWithTax()`) yang menghitung nilai langsung dari field record (`this.product_id.minimum_sale_price_with_tax`, `this.getUnitDisplayPrice()` — lihat baris berikutnya untuk nama method benar) | Kritis kalau tidak diporting — perlu verifikasi getter apa yang tersedia di `PosOrderlineAccounting` 19.0 sebelum menulis kode (Step 6, bukan diasumsikan sekarang) | `BSL-014` |
| `static/src/store/pos_store.js:12-15` `get_order`, `get_orderlines`, `get_unit_display_price`, `get_product` | `DIFF-08` | Rename ke `getOrder()`, `getOrderlines()`, `getProduct()`. Untuk `get_unit_display_price` — **cari pengganti di `PosOrderlineAccounting` 19.0** (`displayPriceUnit`/`currencyDisplayPriceUnit`, dikonfirmasi Step 2, TAPI belum diverifikasi mana yang tepat secara semantik — WAJIB baca source getter itu di Step 6 sebelum pakai, jangan tebak dari nama) | Tinggi — kalau salah pilih getter, validasi margin bisa salah angka (bukan cuma crash) | `BSL-006`, `BSL-007` |
| `static/src/store/models/models.js:30` `patch(PosOrderline.prototype, {set_unit_price(){super.set_unit_price(price)}})` | `DIFF-09` | Rename jadi `setUnitPrice(price) { super.setUnitPrice(price); }` — method ini murni passthrough, tidak ada logic tambahan, aman di-rename langsung | Rendah | — |
| `static/src/store/orderline.xml` | `DIFF-10` | **Tidak ada perubahan** — xpath descendant tetap match | Tidak ada | `BSL-014` |
| `__manifest__.py` | — | Bump `version` ke `19.0.x.x` | Tidak ada | — |

## 2b. Risk Analysis Terstruktur

### Critical Migration Blockers
*(Mencegah instalasi atau operasi inti di 19.0)*

| # | Isu | Lokasi | Rujukan knowledge base |
|---|---|---|---|
| 1 | Manifest version — harus `19.0.x.x` | `__manifest__.py:17` | — |
| 2 | `patch(Orderline.props.line.shape, {...})` — target `undefined`, akan throw saat load | `static/src/store/models/models.js:12-16` | `FINDINGS.md` `MF-12`, `02_DIFF_ANALYSIS.md` `DIFF-06` |
| 3 | `pay()` override memanggil method core yang sudah di-rename (`get_order`, `get_orderlines`, `get_product`) — akan `TypeError` saat kasir klik "Pay" | `static/src/store/pos_store.js:12-15` | `FINDINGS.md` `MF-13`, `02_DIFF_ANALYSIS.md` `DIFF-08` |

**Priority:** HIGH — perbaiki sebelum runtime testing apapun (G1 install test TIDAK akan menangkap
blocker #2/#3 karena Owl error/JS runtime error baru muncul saat komponen benar-benar dipakai, bukan
saat install — pelajaran persis yang sama seperti `MF-15`/`MF-16` di migrasi 17→18. G1 (install)
bisa PASS padahal fitur JS rusak total; wajib Tour test nyata untuk menangkap ini, lihat §Urutan
Prioritas Testing).

### OWL Widget yang Butuh Rewrite/Review

| Widget | File | Risiko | Detail |
|---|---|---|---|
| `Orderline` (patch props shape) | `static/src/store/models/models.js` | Kritis | `DIFF-06` — hapus patch, porting jadi getter di record |
| `PosOrderline` (patch `getDisplayData`) | `static/src/store/models/models.js` | Kritis | `DIFF-07` — ganti pola total, bukan rename |

**Urutan wajib:** migrasi SEMUA JavaScript dulu, baru sentuh template (`orderline.xml` — walau
tidak butuh perubahan struktural, tetap harus dites SETELAH JS selesai, bukan sebelum). Lihat
`06a_CODE_MIGRATION_PHASES.md` Fase E & F.

### Controller & Route

Tidak ada — `controllers/controllers.py` tetap dead scaffold, tidak disentuh (lihat `MF-` — bukan
finding, memang sengaja mati sejak awal).

### Assets & Dependency

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | 3 import path pindah (`DIFF-01`/`02`/`03`) | `static/src/store/{models/models.js,pos_store.js}` | Tinggi (mekanis, tapi wajib — modul tidak akan load tanpa ini) |

### Kompatibilitas Data Model

Tidak ada perubahan model Python yang dibutuhkan — `product.category`/`product.template`/
`product.product`/`pos.config`/`res.config.settings`/`wizard.margin.product` semua tetap identik
struktur field-nya. `_load_pos_data_fields` fungsional tanpa perubahan (`DIFF-05`).

### Risiko Integrasi

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | Kolisi `wizard.margin.product` dengan `sale_margin_threshold` (`MF-03`) — tidak terkait versi Odoo, murni struktur Python, TIDAK berubah oleh migrasi ini | `wizard/wizard_margin_product.py` | Menengah — sudah diketahui sejak Step 1, tidak perlu aksi baru di Step 6 kecuali user putuskan konsolidasi |

### Urutan Prioritas Testing

1. Install & startup — manifest version, dependency (`base`, `point_of_sale`, `product`,
   `stock_account`) masih Community di 19.0 (dikonfirmasi Step 2).
2. **Buka POS session** — memuat `ProductProduct`/`PosOrderline` (verifikasi 3 import path resolve,
   `DIFF-01`/`02`/`03`), render `Orderline` sekali dengan produk apapun (verifikasi `DIFF-06`
   fix — kalau masih crash di titik ini, patch `props.line.shape` belum benar-benar dihapus).
3. **Jual produk di bawah minimum, klik Pay** — jalur inti (`DIFF-08`/`09`) — Tour test WAJIB, bukan
   cuma baca kode (lesson 17→18: G1 install-test PASS tidak menjamin fitur JS jalan).
4. Verifikasi visual: warna merah/teks peringatan di orderline saat harga di bawah minimum
   (`DIFF-07` fix — getter baru harus benar-benar dibaca template).
5. Wizard bulk-assign margin (Python murni, risiko rendah, tapi tetap perlu smoke-test manual).

### View List Checklist

N/A — tidak ada `<tree>` tersisa di modul ini (sudah `<list>` sejak migrasi 17→18, dikonfirmasi
grep bersih).

### Estimasi Effort (opsional)

| Area | Effort | Catatan |
|---|---|---|
| Import path (3x) | Kecil | Mekanis |
| `getDisplayData()`/`props.line.shape` porting | Sedang-Besar | Butuh baca source getter `PosOrderlineAccounting` 19.0 langsung di Step 6, tidak bisa ditulis blind dari sini |
| Rename method core (`pay()` override) | Sedang | Terutama `get_unit_display_price` — perlu identifikasi getter pengganti yang benar |
| Python | Nol | Tidak ada perubahan wajib |

## 3. Data Migration

N/A — port kode saja, tidak ada data produksi.

## 4. Scope

### Termasuk
- Semua item §2 di atas (import path, porting getter, rename method, manifest version bump).

### Di Luar Scope (sengaja, disetujui di intake)
- `MF-01`/`MF-02`/`MF-03`/`MF-04` (quirk warisan) — dipertahankan identik, tidak diperbaiki, kecuali
  user memutuskan lain (lihat `FINDINGS.md`).
- `views/product_template_views.xml` (dead file) — tetap mati.
