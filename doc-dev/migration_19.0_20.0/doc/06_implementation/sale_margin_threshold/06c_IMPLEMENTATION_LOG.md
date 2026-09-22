# Implementation Log — sale_margin_threshold (19.0 → 20.0)

**Status:** 🔄 Sebagian — beberapa fix install-blocking dan satu bug dedup kolom sudah diterapkan
lebih awal dari urutan fase normal, atas permintaan dev untuk keperluan review visual langsung
(Docker 19.0 vs 20.0 berdampingan) sebelum `MF-29` benar-benar final. Applicability Check penuh
(Fase A→G) belum dijalankan formal.

**Tanggal:** 2026-09-22

---

## Perubahan yang sudah diterapkan

| Ref | Perubahan | File | Ref spec |
|---|---|---|---|
| `DIFF-01`/`MF-30` | Rename `security/ir.model.access.csv` → `security/ir.access.csv`, reformat ke skema `operation`/`domain` (2 baris: `sale.confirmation.wizard`, `wizard.margin.product`) | `security/ir.access.csv` (baru) | `03_MIGRATION_SPEC.md` §2b |
| `DIFF-08`/`MF-29` | Ganti record `product_variant_easy_edit_view_margin_sale` menjadi `product_product_tree_view_margin_sale` (inherit `product.product_product_tree_view`), tambah kolom `margin_sale`/`minimum_sale_price` + `decoration-danger` di `lst_price` (tidak dikondisikan) | `views/products.xml` | `03_MIGRATION_SPEC.md` §2b |
| `MF-35` | Xpath `price_unit` di list `sale.order` tidak resolve — native 20.0 membungkusnya di `<column name="price_unit">` baru (sengaja, komentar native sebut modul seperti `sale_margin`); install-blocking, ditemukan dari smoke-install Docker nyata | `views/sale_order.xml` | `FINDINGS.md` `MF-35` |
| `MF-37` | Kolom `margin_sale`/`minimum_sale_price` DOBEL di list Product Variants 20.0 (efek samping `MF-29` — `pos_margin_threshold` inherit view native yang sama, field nama sama). Percobaan `column_invisible="module_pos_margin_threshold == True"` gagal (tidak ada record context di evaluasi `column_invisible`). Fix final: tambah marker `class="o_smt_dedup_margin"`/`class="o_smt_dedup_min_price"` di field ini, lalu strip via xpath di `ProductProduct._get_view()` kalau `pos_margin_threshold` terinstall — hanya kolom modul ini yang dihapus, kolom `pos_margin_threshold` jadi satu-satunya yang tampil (sesuai keputusan desain `MF-29`) | `views/products.xml` (marker) + `models/product.py` (`_get_view()` override, method baru) | `FINDINGS.md` `MF-37` |
| Visual parity `MF-29` | **Dikonfirmasi dev 2026-09-22 (keputusan: terapkan, dijustifikasi via review visual live 19.0 vs 20.0 di Docker)** — tambah `decoration-danger="margin_sale &lt; 0.0"` pada field `margin_sale`, tambah field+kolom baru `minimum_sale_price_with_tax` ("Incl. Tax", compute dari `margin_sale`/`minimum_sale_price`/`product_tmpl_id.taxes_id`, mirror pola `ProductTemplate` yang sudah ada) — menyamai 2 elemen popup 19.0 yang belum ikut pindah ke kolom list saat `MF-29` dieksekusi. Kolom baru ini JUGA diberi marker dedup (`class="o_smt_dedup_min_price_tax"`) dan ditambahkan ke xpath strip `_get_view()`, supaya tidak dobel lagi seperti `MF-37` saat `pos_margin_threshold` juga terinstall (yang JUGA mendapat kolom Incl. Tax yang sama, lihat `06_implementation/pos_margin_threshold/06c_IMPLEMENTATION_LOG.md`). Diverifikasi live: margin negatif tampil merah, kolom Incl. Tax terisi benar, tidak dobel. | `views/products.xml`, `models/product.py` (field+compute baru, xpath strip diperluas) | `FINDINGS.md` (lihat catatan visual-parity di bawah) |
| — | Bump `version` → `20.0.1.0`, update `data:` entry nama file security | `__manifest__.py` | `03_MIGRATION_SPEC.md` §1 |

## Belum diterapkan (sengaja)

- `MF-08`/`MF-20`/`MF-21`/`MF-26`/`MF-27` — semua dipertahankan identik, tidak disentuh (sesuai
  scope spec).

## Catatan proses

Sama seperti `pos_margin_threshold` (lihat `06_implementation/pos_margin_threshold/06c_IMPLEMENTATION_LOG.md`
§"Catatan proses") — eksekusi dini atas permintaan dev untuk review visual, bukan urutan fase normal.
Applicability Check penuh akan dijalankan ulang saat Step 6 resmi dimulai.

**Lesson `MF-37`:** setelah mengedit file Python model (bukan XML/aset), update modul via `-u
<module>` di proses `odoo-bin` terpisah TIDAK CUKUP untuk verifikasi via browser — proses web server
yang sebenarnya melayani request (container `odoo` long-running di `docker compose`) masih
menjalankan kode Python lama di memori sampai container itu sendiri di-restart
(`docker compose restart odoo`). Sempat menyebabkan false negative (fix terlihat belum jalan padahal
kodenya sudah benar) sampai root cause ini ketahuan.
