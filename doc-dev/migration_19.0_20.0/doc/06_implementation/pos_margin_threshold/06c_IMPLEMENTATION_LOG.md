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
| `DIFF-04` | **Dikonfirmasi dev 2026-09-22 (lihat §4 spec, keputusan: terapkan)** — tambah `options="{'currency_field': 'currency_id', 'field_digits': True}"` ke field pengganti `list_price` (form Product Template), menyamai atribut baru native 20.0. Diverifikasi: tidak ada beda visual di data instance ini (single-currency), murni jaga-jaga kompatibilitas. | `views/products.xml` | `03_MIGRATION_SPEC.md` §2a/§4 |
| Visual parity `MF-29` | **Dikonfirmasi dev 2026-09-22** — tambah `decoration-danger="margin_sale &lt; 0.0"` pada kolom `margin_sale` + kolom baru `minimum_sale_price_with_tax` ("Incl. Tax") di list Product Variants, menyamai 2 elemen popup 19.0 (`product_variant_easy_edit_view_margin_sale`) yang belum ikut pindah ke kolom list saat `MF-29` dieksekusi. Field `minimum_sale_price_with_tax` baru ditambahkan ke `ProductProduct` (compute dari `margin_sale`/`minimum_sale_price`/`product_tmpl_id.taxes_id`, mirror pola `ProductTemplate` yang sudah ada). Diverifikasi live: margin negatif tampil merah, kolom Incl. Tax terisi benar. | `views/products.xml`, `models/product.py` (field+compute baru) | `FINDINGS.md` (lihat entri visual-parity `sale_margin_threshold`, berlaku sama untuk modul ini) |
| `DIFF-05`/`MF-34` | **Dikonfirmasi dev 2026-09-22 (keputusan: PERBAIKI, bukan pertahankan)** — `line.comboParent` → `line.combo_parent_id` di ekspresi `t-attf-class`. Cross-check ke native `odoo19`/`enterprise19` (setelah `native-source` diisi ulang) mengonfirmasi `comboParent` tidak pernah valid di versi manapun (typo sejak branch `17.0`, dikonfirmasi via `git show 17.0:...`) — field asli native adalah `combo_parent_id`. Komentar XML (bahasa Inggris) ditambahkan menjelaskan asal-usul rename. Styling combo-child (indent+border kiri) AKTIF untuk pertama kalinya di 20.0 — perubahan behavior yang terlihat, disetujui eksplisit dev. | `static/src/store/orderline.xml` | `FINDINGS.md` `MF-34` |
| — | Bump `version` → `20.0.1.0`, update `data:` entry nama file security | `__manifest__.py` | `03_MIGRATION_SPEC.md` §1 |
| `MF-40` | `ir.config_parameter.get_param()` dihapus total di native 20.0. `PosConfig._compute_blocked_warning()` crash runtime setiap kali dipanggil. Fix: `get_param`→`get_bool`. | `models/pos_config.py` | `FINDINGS.md` `MF-40` |
| `MF-41` | Xpath anchor `t[@t-slot='default']` tidak resolve (native rename ke `t-call-slot`) — template `Orderline` gagal kompilasi total. Setelah diperbaiki, ketahuan SEMUA 4 pemakaian `line` bare di file yang sama juga bug bare-identifier (pola `MF-33`) — diberi prefix `this.`. | `static/src/store/orderline.xml` | `FINDINGS.md` `MF-41` |
| `MF-42` (workaround, bukan fix modul) | Native 20.0 numpad tombol "Price" disabled untuk cashier role manager kalau `restrict_price_control=False` (logic terbalik dari help text field-nya sendiri, bug native). Workaround: set `restrict_price_control=True` di setup test. | `tests/test_margin_threshold_tour.py` | `FINDINGS.md` `MF-42` |
| `MF-44` | CSS class `.receipt-screen` (19.0) di-rename total jadi `.feedback-screen` di native 20.0 (`ReceiptScreen`→`FeedbackScreen`) — selector step terakhir tour tidak pernah match. Fix: update selector. | `static/tests/tours/margin_threshold_tour.js` | `FINDINGS.md` `MF-44` |
| `MF-43` (root cause final) | `setUpClass()` test membuat produk dengan compute chain (`margin_sale`→`minimum_sale_price`→`minimum_sale_price_with_tax`) tanpa flush — browser Chrome (thread/cursor terpisah) kadang membaca baris DB sebelum ter-flush, terbaca `0`. Fix: `env.flush_all()` setelah `create()`. | `tests/test_margin_threshold_tour.py` | `FINDINGS.md` `MF-43` (koreksi final) |

## Belum diterapkan (sengaja, menunggu keputusan/urutan normal)

- G1/G2 (install test, tour test) formal — baru dijalankan sebatas smoke-install manual via Docker
  untuk keperluan review visual, BUKAN full test suite Step 6/9 resmi.

## ✅ Step 9 Dev Testing — LOLOS BERSIH (2026-09-23)

`MF-43` (root cause final: kurang `env.flush_all()` di test setup) dan `MF-44` (rename CSS
`.receipt-screen`→`.feedback-screen`) sudah diperbaiki. Kedua tour
(`test_pos_margin_threshold_below_minimum_confirm_tour`,
`test_pos_margin_threshold_below_minimum_blocked_tour`) **lolos bersih 3 run berturut-turut**
(termasuk 1 run tanpa kode debug apapun, database fresh install). Modul ini sekarang tuntas Step 9.
Verifikasi visual live `MF-34` (combo product) sudah bisa dilakukan lewat tour yang sama (order
combo tidak eksplisit di test ini, tapi styling tidak lagi diblokir oleh kegagalan tour).

## Catatan proses

Urutan eksekusi ini menyimpang dari disiplin fase normal (`06a_CODE_MIGRATION_PHASES.md`,
Applicability Check → A1→G2) — dev secara eksplisit meminta implementasi 3 fix install-blocking
LEBIH AWAL (sebelum Step 4/5 selesai) supaya bisa melihat perbandingan visual 19.0 vs 20.0 secara
langsung sebagai bagian proses mengambil keputusan `MF-29`. Setelah Step 4/5 selesai formal, Step 6
akan kembali menjalankan Applicability Check penuh untuk modul ini (kemungkinan besar akan
mengonfirmasi 3 fix di atas sudah benar dan tidak perlu diulang, tapi tetap wajib direview ulang
sebagai bagian gate, bukan diam-diam dianggap "selesai" dari eksekusi dini ini).

**Catatan efek samping (visual parity, transparansi):** `ProductProduct._load_pos_data_fields()`
di file ini (baris ~111) sudah SEJAK 19.0 (`[DIWARISI-SOURCE]`, dikonfirmasi identik di
`git show migration/19.0:pos_margin_threshold/models/product.py`) mereferensikan
`'minimum_sale_price_with_tax'` sebagai field POS untuk `product.product` — padahal field itu
sebelumnya HANYA ada di `ProductTemplate`, tidak pernah didefinisikan di `ProductProduct` (baik di
19.0 maupun 20.0 sebelum perubahan sesi ini). Menambahkan field `minimum_sale_price_with_tax` ke
`ProductProduct` untuk keperluan visual parity (kolom Incl. Tax) SEBAGAI EFEK SAMPING membuat
referensi lama ini sekarang benar-benar valid (field-nya sekarang ada). Ini TIDAK diverifikasi lebih
lanjut apakah referensi lama itu sebelumnya silent-fail/crash di alur POS — di luar scope perubahan
kosmetik sesi ini, dicatat di sini murni untuk transparansi, bukan diklaim sebagai "bug POS
diperbaiki". Kalau nanti Step 9 (Dev Testing) POS menemukan perubahan perilaku terkait ini, cek
catatan ini dulu sebelum menganggapnya regresi baru.
