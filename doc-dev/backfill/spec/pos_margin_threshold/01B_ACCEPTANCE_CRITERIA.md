# Acceptance Criteria — pos_margin_threshold

**Module:** `pos_margin_threshold`
**Ref:** `01A_FUNCTIONAL_SPEC.md`
**Last Updated:** 2026-07-31
**Status:** Backfill retroaktif

---

## AC-01 — Perhitungan margin & harga minimum

**AC-01-01** — ref `BR-01` `[HASIL-BACA]`
Given kategori produk punya `margin_sale = 20%` dan produk baru dibuat di kategori itu tanpa
override manual
When produk disimpan
Then `product.margin_sale` template maupun variant otomatis terisi `20%` (compute dari kategori).

**AC-01-02** — ref `BR-01` `[HASIL-BACA]`
Given produk sudah punya `margin_sale` ter-set (baik dari kategori atau manual)
When user mengedit `margin_sale` langsung di form produk
Then nilai manual tersimpan (`store=True`) dan TIDAK kembali ke nilai kategori sampai salah satu
dependency compute (`categ_id.margin_sale`) berubah lagi.

**AC-01-03** — ref `BR-02` `[HASIL-BACA]`
Given `standard_price = 100`, `margin_sale = 20`
When `minimum_sale_price` dihitung
Then `minimum_sale_price = 120` (100 * 1.20).

**AC-01-04** — ref `BR-02` `[HASIL-BACA]`
Given user mengedit `minimum_sale_price` langsung menjadi `150` (dengan `standard_price = 100`)
When field disimpan
Then `margin_sale` otomatis ter-inverse jadi `50` ((150/100 - 1) * 100).

**AC-01-05** — ref `BR-02` `[HASIL-BACA]`
Given `standard_price = 0`
When user set `minimum_sale_price` manual
Then `_inverse_minimum_sale_price` set `margin_sale = 0.0` (guard pembagian nol eksplisit di kode).

**AC-01-06** — ref `BR-01` `[PERLU-KEPUTUSAN]` — **DIREVISI setelah eksekusi nyata (F-01), lihat `FINDINGS.md`**
Given produk TEMPLATE punya 2 variant (A, B)
When user set `variant_A.margin_sale = 20`, lalu set `variant_B.margin_sale = 50`
Then (TERKONFIRMASI via `tests/test_margin_sale.py::test_margin_sale_inverse_writes_to_shared_template_not_per_variant`,
Docker, 2026-07-31) `variant_A.margin_sale` IKUT berubah jadi `50` juga (inverse menulis ke
`product_tmpl_id` yang shared) — precondition "margin A ≠ margin B" yang diasumsikan hipotesis
AWAL finding ini TERBUKTI TIDAK PERNAH BISA TERCAPAI. Konsekuensinya, `minimum_sale_price_with_tax`
(BR-03) yang didelegasikan dari template TIDAK bisa inkonsistensi seperti diduga awal — bukan
karena delegasinya aman, tapi karena precondition-nya mustahil.

---

## AC-02 — Blocking transaction POS

**AC-02-01** — ref `BR-04` `[HASIL-BACA]`
Given `blocking_transaction_pos = True`, order POS punya baris dengan `unit_price < minimum_sale_price_with_tax`
When kasir klik bayar
Then `ErrorPopup` muncul ("Please check !"), proses `pay()` dihentikan (`return` sebelum
`super().pay()`), kasir TIDAK bisa lanjut ke pembayaran.

**AC-02-02** — ref `BR-04` `[HASIL-BACA]`
Given `blocking_transaction_pos = False` (default), order POS punya baris di bawah minimum
When kasir klik bayar
Then `ConfirmPopup` muncul; kalau kasir pilih "Confirm" proses bayar lanjut (`super().pay()`), kalau
"Cancel" proses bayar dibatalkan (`return`).

**AC-02-03** — ref `BR-04` `[HASIL-BACA]`
Given semua baris order harganya di atas/sama dengan minimum
When kasir klik bayar
Then tidak ada popup sama sekali, langsung lanjut `super().pay()`.

---

## AC-03 — Wizard assign margin massal

**AC-03-01** — ref `BR-06` `[HASIL-BACA]`
Given user membuka wizard dari list view **Product Template**, pilih 3 produk, isi `margin = 15`
When klik "Assign"
Then ketiga `product_template_ids.margin_sale` di-set jadi `15`, wizard tertutup (`return True`).

**AC-03-02** — ref `BR-06` `[HASIL-BACA]`
Given user membuka wizard dari list view **Product Variants** (bukan Template)
When wizard terbuka
Then field yang tampil `product_ids` (bukan `product_template_ids`) — dikontrol
`is_product` compute berdasar `active_model` di context.

---

## AC-04 — Koeksistensi dengan `sale_margin_threshold` (cross-module)

**AC-04-01** — ref `BR-05` `[PERLU-KEPUTUSAN]`
Given HANYA `pos_margin_threshold` terinstall (TANPA `sale_margin_threshold`)
When admin membuka Settings
Then tidak ada UI sama sekali untuk `blocking_transaction_order` — field ada di database tapi
"mati" secara fungsional. Lihat **F-02**.

**AC-04-02** — ref `BR-07` `[PERLU-KEPUTUSAN]` — **TERKONFIRMASI eksekusi nyata, Docker 2026-07-31**
Given KEDUA modul (`pos_margin_threshold` + `sale_margin_threshold`) terinstall bersamaan
When Odoo membangun registry model `wizard.margin.product`
Then `create()` berhasil TANPA error (dugaan awal ini benar) — TAPI `__mro__` kelas final HANYA
berisi kelas `WizardMarginProduct` dari `sale_margin_threshold` (modul yang diinstall lebih
belakangan); kelas `pos_margin_threshold` SEPENUHNYA TIDAK MUNCUL di `__mro__`, bukan "digabung"
seperti dugaan awal. Aman SAAT INI karena kedua kelas identik. Lihat **F-03** (direvisi).
