# Implementation Log — pos_margin_threshold (19.0 → 20.0)

**Status:** 🔄 Sebagian — 3 fix install-blocking sudah diterapkan lebih awal dari urutan fase normal,
atas permintaan dev untuk keperluan review visual langsung (Docker 19.0 vs 20.0 berdampingan)
sebelum `MF-29` benar-benar final. Applicability Check penuh (Fase A→G) belum dijalankan formal.

**Tanggal:** 2026-09-22

---

## Perubahan yang sudah diterapkan

| Ref | Perubahan | File | Ref spec |
|---|---|---|---|
| `DIFF-01` | Rename `security/ir.model.access.csv` → `security/ir.access.csv`, reformat ke skema `operation`/`domain` | `security/ir.access.csv` (baru) | `03_MIGRATION_SPEC.md` §2a |
| `DIFF-02` | `ref="stock_account.view_category_property_form_stock"` → `ref="account.view_category_property_form"` | `views/products.xml` | `03_MIGRATION_SPEC.md` §2a |
| `DIFF-03`/`MF-29` | Ganti record `product_variant_easy_edit_view_margin_sale` (inherit view yang hilang) menjadi `product_product_tree_view_inherit_margin_sale` (inherit `product.product_product_tree_view`), tambah kolom `margin_sale`/`minimum_sale_price` (`optional="show"`) + `decoration-danger` di `lst_price` | `views/products.xml` | `03_MIGRATION_SPEC.md` §2a |
| — | Bump `version` → `20.0.1.0`, update `data:` entry nama file security | `__manifest__.py` | `03_MIGRATION_SPEC.md` §1 |

## Belum diterapkan (sengaja, menunggu keputusan/urutan normal)

- `DIFF-04` (options currency pada `list_price` di form Product Template) — menunggu konfirmasi
  ringan dev di gate Step 4, belum dieksekusi.
- `DIFF-05`/`MF-34` (`line.comboParent`) — ditunda, blocker `native-source` kosong.
- G1/G2 (install test, tour test) formal — baru dijalankan sebatas smoke-install manual via Docker
  untuk keperluan review visual, BUKAN full test suite Step 6/9 resmi.

## Catatan proses

Urutan eksekusi ini menyimpang dari disiplin fase normal (`06a_CODE_MIGRATION_PHASES.md`,
Applicability Check → A1→G2) — dev secara eksplisit meminta implementasi 3 fix install-blocking
LEBIH AWAL (sebelum Step 4/5 selesai) supaya bisa melihat perbandingan visual 19.0 vs 20.0 secara
langsung sebagai bagian proses mengambil keputusan `MF-29`. Setelah Step 4/5 selesai formal, Step 6
akan kembali menjalankan Applicability Check penuh untuk modul ini (kemungkinan besar akan
mengonfirmasi 3 fix di atas sudah benar dan tidak perlu diulang, tapi tetap wajib direview ulang
sebagai bagian gate, bukan diam-diam dianggap "selesai" dari eksekusi dini ini).
