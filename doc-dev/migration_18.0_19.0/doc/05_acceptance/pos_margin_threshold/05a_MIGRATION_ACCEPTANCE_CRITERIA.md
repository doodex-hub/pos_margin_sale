# Migration Acceptance Criteria — pos_margin_threshold

**Step:** 5 — Acceptance Criteria & Test Plan
**Ref:** `01_intake/pos_margin_threshold/01b_BASELINE_SPEC.md` dan kode 18.0 yang berjalan (branch
`migration/18.0`) — **bukan** `03_spec/pos_margin_threshold/03_MIGRATION_SPEC.md`
**Tanggal:** 2026-08-26

---

## AC-01 — Margin & Minimum Sale Price (compute/inverse)

**AC-01-01** (verifies `BSL-008`, `BSL-010`)
Given produk dengan `standard_price > 0` dan `margin_sale` tertentu
When `minimum_sale_price` di-compute
Then hasilnya `standard_price * (1 + margin_sale/100)`, identik dengan 18.0 — termasuk kasus
`standard_price == 0` (guard: `margin_sale` di-set `0.0`, tidak division-by-zero).

**AC-01-02** (verifies `BSL-010`)
Given `margin_sale` diubah manual di level `product.product` (variant)
When perubahan disimpan
Then `product_tmpl_id.margin_sale` (template) ikut berubah — **BUKAN bug yang diperbaiki**, ini
`MF-01`, harus identik dengan 18.0 (margin per-variant tidak pernah divergen dari template).

**AC-01-03** (verifies `BSL-012`)
Given produk dengan `list_price`/`lst_price` di bawah `minimum_sale_price(_with_tax)`
When form Product Template/Variant dibuka
Then field harga diberi `decoration-danger` (merah) — identik dengan 18.0.

## AC-02 — Payment-Time Enforcement (POS)

**AC-02-01** (verifies `BSL-006`) — **prioritas tinggi, area `MF-12`/`MF-13`**
Given kasir menjual produk dengan harga di bawah `minimum_sale_price_with_tax`, DAN
`blocking_transaction_pos = False` (default)
When kasir klik "Pay"
Then dialog konfirmasi muncul ("Some products are below the minimum price. Proceed to payment?");
konfirmasi → lanjut ke pembayaran; tolak → tetap di ProductScreen, TIDAK ada baris yang berubah.

**AC-02-02** (verifies `BSL-007`) — **prioritas tinggi, area `MF-12`/`MF-13`**
Given kasir menjual produk di bawah minimum DAN `blocking_transaction_pos = True`
When kasir klik "Pay"
Then `AlertDialog` muncul ("Some products are below the minimum price. Please check !"), TIDAK ADA
opsi lanjut — pembayaran diblokir total.

**AC-02-03** (verifies `BSL-005`)
Given SEMUA baris order di atas/sama dengan minimum
When kasir klik "Pay"
Then TIDAK ADA dialog apapun, langsung lanjut proses pembayaran. *(Gap test terbuka sejak 17→18,
belum pernah ditest otomatis — lihat `BSL-015`.)*

**AC-02-04** (verifies `BSL-014`)
Given orderline dengan harga di bawah minimum
When orderline dirender di layar POS
Then baris diberi class `text-danger` + teks peringatan `"*The price of this product is less than
minimum sale price {{minimumSalePriceWithTax}}"`. *(Belum pernah diassert eksplisit terpisah dari
"tidak crash" — lihat `BSL-015`.)*

## AC-03 — Wizard Bulk-Assign Margin

**AC-03-01** (verifies `BSL-001`, `BSL-002`, `BSL-003`)
Given user memilih 1+ produk di list view Product Template, klik action "Update margin sale"
When wizard terbuka, isi margin, klik "Assign"
Then `margin_sale` SEMUA produk terpilih ter-update ke nilai baru; wizard menampilkan field
`product_template_ids` (bukan `product_ids`).

**AC-03-02** (verifies `BSL-002`)
Given user membuka wizard yang sama dari list view **Product Variants** (bukan Template)
When wizard terbuka
Then field yang ditampilkan adalah `product_ids` (label "Product variants"), BUKAN
`product_template_ids` — dikonfirmasi Step 10 project 17→18 (screenshot: label "Product variants").

**AC-03-03** (verifies `BSL-003`)
Given wizard terbuka dengan margin ter-isi
When user klik "Cancel"
Then TIDAK ADA perubahan pada produk manapun.

## AC-04 — Interaksi Cross-Module (kolisi `wizard.margin.product`)

**AC-04-01** (verifies `BSL-016`, ref `FINDINGS.md` `MF-03`)
Given `pos_margin_threshold` DAN `sale_margin_threshold` terinstall bersamaan
When registry model `wizard.margin.product` dibangun
Then `__mro__` HANYA berisi class `sale_margin_threshold` — dikonfirmasi INDEPENDEN urutan install
(`-i pos_margin_threshold,sale_margin_threshold` atau kebalikannya, hasil identik). Ini bukan bug
baru migrasi, harus tetap identik.

---

**Ringkasan traceability:** 11 AC, mencakup `BSL-001` s.d. `BSL-018` (baseline spec) kecuali
`BSL-009`/`BSL-011` (perincian internal `_load_pos_data_fields`/dual wizard entry-point, tidak
punya user-facing behavior terpisah untuk diverifikasi) dan `BSL-017`/`BSL-018` (quirk warisan
`MF-02`/`MF-04`, tidak ada acceptance test yang bermakna untuk "field yang sengaja tidak dipakai"/
"file yang sengaja mati" — cukup diverifikasi via code review Step 8, bukan test runtime).
