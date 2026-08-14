# Dev Testing — sale_margin_threshold

**Step:** 04 — Developer Testing (backfill)
**Module:** `sale_margin_threshold`
**Spec ref:** `doc-dev/backfill/spec/sale_margin_threshold/01A_FUNCTIONAL_SPEC.md`
**Last Updated:** 2026-07-31

---

## 0. Environment eksekusi

**Mode C** (Claude Code CLI). Sama instance Docker dengan `pos_margin_threshold`+`pin_message`
(lihat `docker-env/docker-compose.yml` di root repo — SATU Odoo+Postgres untuk ketiga addon,
`-i pos_margin_threshold,sale_margin_threshold,pin_message`). Ini adalah dokumen tempat hasil
RUN GABUNGAN dilaporkan lengkap (modul lain merujuk balik ke sini untuk detail run).

### Ringkasan lintas-modul (3 iterasi, 2026-07-31)

| Iterasi | Hasil | Catatan |
|---|---|---|
| 1 | `1 failed, 1 error(s) of 17 tests` | FAIL di TC F-01 pos_margin_threshold (precondition test salah), ERROR di TC F-03 pos_margin_threshold (`TypeError` di test sendiri). **Efek samping penting:** demo data core `sale_stock` GAGAL load karena F-05 (lihat §2 di bawah) — WARNING, bukan fatal. |
| 2 | `1 failed, 0 error(s) of 17 tests` | Bug TypeError F-03 fixed. FAIL F-01 masih ada dengan pesan berbeda (`150.0 == 150.0`) — mengarah ke akar masalah sebenarnya. |
| 3 | **`0 failed, 0 error(s) of 17 tests`** | F-01 test ditulis ulang sesuai temuan sebenarnya (margin tidak bisa divergen antar variant) — semua Pass. |

Perintah yang dijalankan AI sendiri (tanpa dev), persis:
```
cd pos-margin-sale/docker-env
docker compose up
```
lalu poll `logs/odoo.log` untuk baris `X failed, Y error(s) of Z tests`, dan `docker compose down`
(iterasi 2/3 pakai `down -v` dulu untuk db bersih) setelah selesai.

---

## 1. Smoke Test

| # | Area/fitur | Happy path / edge case | Cara | Status |
|---|---|---|---|---|
| 1 | Confirm quotation normal | Harga di atas minimum → langsung confirm | Mode C (Docker) | ✅ Pass |
| 2 | Confirm quotation di bawah minimum, blocking ON | `ValidationError`, order tetap draft | Mode C (Docker) | ✅ Pass |

---

## 2. Unit & Integration Test Specification

### 2a. `action_confirm` — validasi harga minimum (single order)

| # | Tipe | Condition | Expected | Actual | Provenance |
|---|---|---|---|---|---|
| TC-C-01 | Unit | blocking=True, harga < minimum | `ValidationError`, state tetap draft | ✅ Pass | `[DIKONFIRMASI]` |
| TC-C-02 | Unit | blocking=False, harga < minimum | wizard confirm dibuka, order belum confirm; setelah wizard confirm → state='sale' | ✅ Pass | `[DIKONFIRMASI]` |
| TC-C-03 | Unit | harga normal (di atas minimum) | langsung confirm, state='sale' | ✅ Pass | `[DIKONFIRMASI]` |

### 2b. `action_confirm` — BATCH MULTI-RECORD (F-05, PRIORITAS TINGGI)

| # | Tipe | Condition | Expected | Actual | Provenance |
|---|---|---|---|---|---|
| **TC-C-04** | **Unit** | **`(order_1 + order_2).action_confirm()`** | **`ValueError: Expected singleton`** | **✅ Pass — ValueError benar-benar ter-raise: `Expected singleton: sale.order(25, 26)` (run 3)** | `[PERLU-KEPUTUSAN]` |

**Bukti tambahan TIDAK DIRENCANAKAN (lebih kuat dari test buatan sendiri):** selama instalasi
modul (SEBELUM test manapun berjalan), Odoo memuat demo data BAWAAN core `sale_stock`
(`sale_stock/data/sale_order_demo.xml`) yang memanggil
```xml
<function model="sale.order" name="action_confirm" eval="[[ref('sale_order_19'), ref('sale_order_20'), ref('sale_order_21'), ref('sale_order_22')]]"/>
```
— 4 order sekaligus. Ini CRASH dengan `ValueError: Expected singleton: sale.order(21, 22, 23, 24)`,
tertangkap Odoo sebagai kegagalan non-fatal: `WARNING ... Module sale_stock demo data failed to
install, installed without demo data`. **Ini pembuktian independen KEDUA untuk F-05, dari jalur yang
genuinely dipakai Odoo sendiri** — bukan skenario buatan BACKFILL. Detail traceback lengkap ada di
`FINDINGS.md` F-05.

### 2c. Wizard konfirmasi

| # | Tipe | Condition | Expected | Actual | Provenance |
|---|---|---|---|---|---|
| TC-W-01 | Unit | wizard confirm dengan `skip_check_price=True` | order benar-benar confirm | ✅ Pass (tergabung TC-C-02) | `[DIKONFIRMASI]` |

### 2d. Cross-module (F-04)

| # | Tipe | Condition | Expected | Actual | Provenance |
|---|---|---|---|---|---|
| TC-X-02 | Integration (install test, 2 modul) | `pos_margin_threshold` juga terinstall → cek `group_sale_margin_action.users` | Kosong (`[]`) | ✅ Pass — F-04 terkonfirmasi arah ini | `[PERLU-KEPUTUSAN]` |

### 2e. Test Matrix Summary

| Area | Unit | Integration | Provenance |
|---|---|---|---|
| Validasi harga minimum (single) | ✓ (3 TC) | | `[DIKONFIRMASI]` |
| **Batch confirm (F-05)** | **✓ (1 TC)** | | `[PERLU-KEPUTUSAN]` Tinggi |
| Wizard | ✓ (1 TC) | | `[DIKONFIRMASI]` |
| Group dedup cross-module | | ✓ (1 TC) | `[PERLU-KEPUTUSAN]` |

### 2f. Ringkasan

- Unit: 5 TC — semua Pass.
- Total modul ini: 5 test case dari total 17 (gabungan repo). AC-04-02 (manual override group
  ter-revert di reload BERIKUTNYA) TIDAK diuji — butuh 2 siklus reload registry berturut, di luar
  scope test otomatis sesi ini, tetap `[HASIL-BACA]` (lihat `FINDINGS.md` F-04).

### 2g. Override/Collision Check terhadap Odoo Core (WAJIB)

| # | Method | Model | Kelas yang mendefinisikan (`__mro__`) | Override total Odoo core? | Provenance |
|---|---|---|---|---|---|
| 01 | **`action_confirm`** | `sale.order` | `SaleOrder` (modul ini) → `super()` dipanggil di fallthrough | ☐ Ya (core tertimpa TOTAL) / ☑ **Sebagian** — logic core TETAP jalan lewat `super()`, TAPI ada bug independen (asumsi singleton) yang merusak jalur batch | `[PERLU-KEPUTUSAN]` — **F-05, Tinggi, terkonfirmasi eksekusi** |
| 02 | `_register_hook` | `product.product` | `ProductProduct` (modul ini) → `super()._register_hook()` dipanggil di awal | ☑ Tidak (pakai hook resmi Odoo sesuai desain, extend bukan replace) | `[HASIL-BACA]` |
| 03 | `detect_user_language`, `check_product_price` | `sale.order` | Nama custom, tidak ada di core | ☑ Tidak | `[HASIL-BACA]` |
| 04 | `wizard.margin.product` (SELURUH MODEL) | `wizard.margin.product` | Kelas modul ini yang MENANG di `__mro__` (menimpa `pos_margin_threshold`) | ☑ **Ya, tapi terhadap modul SENDIRI (sibling), bukan Odoo core** | `[PERLU-KEPUTUSAN]` — F-03 |
