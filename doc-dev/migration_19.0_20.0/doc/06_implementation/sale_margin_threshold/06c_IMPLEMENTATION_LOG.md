# Implementation Log — sale_margin_threshold (19.0 → 20.0)

**Status:** 🔄 Sebagian — 2 fix install-blocking sudah diterapkan lebih awal dari urutan fase normal,
atas permintaan dev untuk keperluan review visual langsung (Docker 19.0 vs 20.0 berdampingan)
sebelum `MF-29` benar-benar final. Applicability Check penuh (Fase A→G) belum dijalankan formal.

**Tanggal:** 2026-09-22

---

## Perubahan yang sudah diterapkan

| Ref | Perubahan | File | Ref spec |
|---|---|---|---|
| `DIFF-01`/`MF-30` | Rename `security/ir.model.access.csv` → `security/ir.access.csv`, reformat ke skema `operation`/`domain` (2 baris: `sale.confirmation.wizard`, `wizard.margin.product`) | `security/ir.access.csv` (baru) | `03_MIGRATION_SPEC.md` §2b |
| `DIFF-08`/`MF-29` | Ganti record `product_variant_easy_edit_view_margin_sale` menjadi `product_product_tree_view_margin_sale` (inherit `product.product_product_tree_view`), tambah kolom `margin_sale`/`minimum_sale_price` (`optional="show"`, `invisible="module_pos_margin_threshold == True"`) + `decoration-danger` di `lst_price` (tidak dikondisikan) | `views/products.xml` | `03_MIGRATION_SPEC.md` §2b |
| — | Bump `version` → `20.0.1.0`, update `data:` entry nama file security | `__manifest__.py` | `03_MIGRATION_SPEC.md` §1 |

## Belum diterapkan (sengaja)

- Dua item flagged (`minimum_sale_price_with_tax`, `decoration-danger` di field `margin_sale`
  sendiri) — di luar scope literal keputusan dev `MF-29`, menunggu keputusan tambahan kalau dev
  ingin full visual parity dengan popup 19.0.
- `MF-08`/`MF-20`/`MF-21`/`MF-26`/`MF-27` — semua dipertahankan identik, tidak disentuh (sesuai
  scope spec).

## Catatan proses

Sama seperti `pos_margin_threshold` (lihat `06_implementation/pos_margin_threshold/06c_IMPLEMENTATION_LOG.md`
§"Catatan proses") — eksekusi dini atas permintaan dev untuk review visual, bukan urutan fase normal.
Applicability Check penuh akan dijalankan ulang saat Step 6 resmi dimulai.
