# Dev Testing — pos_margin_threshold

**Step:** 04 — Developer Testing (backfill)
**Module:** `pos_margin_threshold`
**Spec ref:** `doc-dev/backfill/spec/pos_margin_threshold/01A_FUNCTIONAL_SPEC.md`
**Last Updated:** 2026-07-31

---

## 0. Environment eksekusi

**Mode C** (Claude Code CLI, AI jalankan+pantau sendiri) — `docker-env/docker-compose.yml`
(instantiate dari `doc-dev-backfill/templates/docker-compose.yml.template`, adaptasi multi-modul:
SATU instance Odoo 17 + Postgres 15 untuk ketiga addon repo ini sekaligus). Dijalankan via
`docker compose up` (Bash background), di-poll `docker-env/logs/odoo.log` langsung, `docker compose
down` setelah selesai — TIDAK ada langkah manual dev sama sekali di modul ini.

**3 iterasi run** (2026-07-31) — 2 iterasi pertama menemukan bug DI TEST YANG SAYA TULIS SENDIRI
(bukan di kode modul), diperbaiki, iterasi ke-3 hasil final `0 failed, 0 error(s) of 17 tests`
(gabungan ketiga modul repo ini, lihat §"Ringkasan lintas-modul" di `test/sale_margin_threshold/04A_DEV_TESTING.md`
untuk detail run gabungan). Riwayat 2 bug test yang diperbaiki:
1. `test_wizard_margin_product_model_merged_when_both_installed` — `TypeError: argument of type
   'NoneType' is not iterable` di introspeksi `__mro__` sendiri (bukan bug modul) — fix: null-safe
   check.
2. `test_minimum_sale_price_with_tax_multivariant_delegation` (nama awal) — precondition-nya
   sendiri gagal tercapai 2× berturut, MENGUNGKAP temuan F-01 yang sebenarnya (lihat §2 di bawah,
   dan `FINDINGS.md` F-01 untuk kronologi lengkap) — test ditulis ulang total jadi
   `test_margin_sale_inverse_writes_to_shared_template_not_per_variant`.

---

## 1. Smoke Test (happy path)

| # | Area/fitur | Happy path / edge case | Cara | Status |
|---|---|---|---|---|
| 1 | Margin dari kategori | Produk baru di kategori bermargin → `margin_sale` template terisi otomatis | Mode C (Docker) | ✅ Pass |
| 2 | Blocking transaction POS | Guard `standard_price=0` tidak crash saat `_inverse_minimum_sale_price` | Mode C (Docker) | ✅ Pass |

---

## 2. Unit & Integration Test Specification

### 2a. Model Fields — `product.py` (`ProductTemplate`/`ProductProduct`)

| # | Tipe | Condition | Expected | Actual (Docker) | Provenance |
|---|---|---|---|---|---|
| TC-F-01 | Unit | margin_sale template baru dari kategori | = categ.margin_sale | ✅ Pass | `[DIKONFIRMASI]` |
| TC-F-02 | Unit | override manual margin_sale template | tetap nilai manual, tidak reset | ✅ Pass | `[DIKONFIRMASI]` |
| TC-F-03 | Unit | minimum_sale_price = cost*(1+margin) | 100*1.2=120 | ✅ Pass | `[DIKONFIRMASI]` |
| TC-F-04 | Unit | inverse minimum_sale_price→margin | 150 & cost 100 → margin 50 | ✅ Pass | `[DIKONFIRMASI]` |
| TC-F-05 | Unit | guard standard_price=0 | margin_sale=0.0, no ZeroDivisionError | ✅ Pass | `[DIKONFIRMASI]` |
| **TC-F-06** | **Unit** | **set margin_sale di 1 variant (template 2 variant)** | **variant SIBLING ikut berubah (F-01)** | **✅ Pass — F-01 terkonfirmasi** | `[PERLU-KEPUTUSAN]` |
| TC-F-07 | Unit | field `blocking_transaction_order` tanpa view sendiri | tidak muncul di `arch_db` view settings modul ini | ✅ Pass — F-02 terkonfirmasi | `[PERLU-KEPUTUSAN]` |

### 2b. Wizard Assign Margin

| # | Tipe | Condition | Expected | Actual | Provenance |
|---|---|---|---|---|---|
| TC-W-01 | Unit | assign margin dari list Product Template | `margin_sale` ter-set sesuai wizard | ✅ Pass | `[DIKONFIRMASI]` |

### 2c. Cross-module (F-03)

| # | Tipe | Condition | Expected | Actual | Provenance |
|---|---|---|---|---|---|
| TC-X-01 | Integration (install test, 2 modul) | `wizard.margin.product` dibaca `__mro__` saat `sale_margin_threshold` juga terinstall | `create()` sukses; **`__mro__` HANYA berisi kelas `sale_margin_threshold`** | ✅ Pass — F-03 terkonfirmasi (lebih presisi dari hipotesis awal) | `[PERLU-KEPUTUSAN]` |

### 2d. Test Matrix Summary

| Area | Unit | Integration | Provenance |
|---|---|---|---|
| Margin/harga minimum | ✓ (6 TC) | | `[DIKONFIRMASI]`/`[PERLU-KEPUTUSAN]` (TC-F-06) |
| Wizard | ✓ (1 TC) | | `[DIKONFIRMASI]` |
| Cross-module wizard model | | ✓ (1 TC) | `[PERLU-KEPUTUSAN]` |

### 2e. Ringkasan

- Unit: 7 TC — semua Pass setelah 2 iterasi perbaikan test.
- Integration (cross-module): 1 TC — Pass, hasil MENGKONFIRMASI F-03 dengan detail lebih tajam.
- Total modul ini: **9 test case**, `odoo.tests.stats` mencatat sebagai bagian dari total 17 test
  (gabungan 3 modul repo ini) — `0 failed, 0 error(s)` di run final.

### 2f. Override/Collision Check terhadap Odoo Core (WAJIB)

| # | Method | Model | Kelas yang mendefinisikan (`__mro__`) | Override total Odoo core? | Provenance |
|---|---|---|---|---|---|
| 01 | `_loader_params_product_product` | `pos.session` | `PosSession` (modul ini) → `super()` ke core | ☐ Ya / ☑ Tidak (extend via `super()`, aman) | `[HASIL-BACA]` |
| 02 | `action_assign_margin` | `product.template`/`product.product` | Nama custom, tidak ada di core | ☑ Tidak (nama unik) | `[HASIL-BACA]` |
| 03 | `wizard.margin.product` (SELURUH MODEL, bukan cuma method) | `wizard.margin.product` | **Kelas modul ini HILANG dari `__mro__` saat `sale_margin_threshold` juga terinstall** | ☑ **Ya — override total ANTAR MODUL SENDIRI** (bukan vs Odoo core, tapi pola identik) | `[PERLU-KEPUTUSAN]` — F-03 |
