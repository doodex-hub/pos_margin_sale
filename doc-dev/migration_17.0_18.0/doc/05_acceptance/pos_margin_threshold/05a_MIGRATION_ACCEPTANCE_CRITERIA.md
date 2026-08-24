# Migration Acceptance Criteria — pos_margin_threshold

**Step:** 5 — Acceptance Criteria & Test Plan
**Ref:** `01_intake/pos_margin_threshold/01b_BASELINE_SPEC.md` dan kode 17.0 yang berjalan — bukan `03_MIGRATION_SPEC.md`
**Tanggal:** 2026-08-24

> Diturunkan langsung dari `01b_BASELINE_SPEC.md`. Kesetaraan diukur terhadap 17.0, bukan terhadap rencana migrasi Step 3.

---

## AC-01 — Perhitungan margin & harga minimum

**AC-01-01** (verifies `BSL-001`)
Given kategori produk punya `margin_sale = 20%` dan produk baru dibuat di kategori itu tanpa override manual
When produk disimpan
Then `margin_sale` template maupun variant otomatis terisi `20%` di 18.0 (identik 17.0).

**AC-01-02** (verifies `BSL-001`)
Given produk sudah punya `margin_sale` manual
When dependency compute (`categ_id.margin_sale`) TIDAK berubah
Then nilai manual tetap tersimpan, tidak kembali ke nilai kategori (identik 17.0).

**AC-01-03** (verifies `BSL-004`)
Given `standard_price = 100`, `margin_sale = 20`
When `minimum_sale_price` dihitung
Then `= 120` (identik formula 17.0).

**AC-01-04** (verifies `BSL-004`)
Given `standard_price = 0`
When user set `minimum_sale_price` manual
Then `margin_sale` di-set `0.0` (guard div-by-zero tetap ada, identik 17.0).

**AC-01-05 — TERKAIT RISIKO TINGGI `03_MIGRATION_SPEC.md`** (verifies `BSL-011`, `MF-01`)
Given produk template punya 2 variant (A, B)
When `variant_A.margin_sale` di-set beda dari `variant_B.margin_sale`
Then **kedua variant tetap berakhir dengan nilai SAMA** (quirk existing, `product_tmpl_id` shared — HARUS identik dengan 17.0, JANGAN diperbaiki). Re-run test `tests/test_margin_sale.py::test_margin_sale_inverse_writes_to_shared_template_not_per_variant` sebagai bukti.

## AC-02 — Blocking transaction POS — TERKAIT RISIKO TINGGI (`DIFF-05` loader, `DIFF-02/03/04` JS store)

**AC-02-01** (verifies `BSL-003`)
Given `blocking_transaction_pos = True`, order POS ada baris `unit_price < minimum_sale_price_with_tax`
When kasir klik bayar
Then `ErrorPopup` muncul, pembayaran diblokir total — **ini membuktikan `DIFF-05` (loader field) DAN `DIFF-02/04` (import JS) sama-sama berfungsi**, bukan cuma install sukses.

**AC-02-02** (verifies `BSL-003`)
Given `blocking_transaction_pos = False` (default), ada baris di bawah minimum
When kasir klik bayar
Then `ConfirmPopup` muncul, kasir bisa pilih lanjut/batal.

**AC-02-03** (verifies `BSL-003`)
Given semua baris di atas/sama minimum
When kasir klik bayar
Then tidak ada popup, langsung lanjut.

**AC-02-04 — TERKAIT `MF-11`/`DIFF-07`** (verifies `BSL-007`)
Given tampilan orderline di POS
When baris di bawah minimum
Then teks merah + pesan peringatan tetap muncul (`getDisplayData()` full-override tetap menghasilkan field yang sama seperti 17.0 — kalau core 18.0 menambah field baru ke tampilan orderline yang seharusnya muncul tapi tidak, itu manifestasi `MF-11`, dicatat sebagai temuan baru bukan kegagalan AC ini).

## AC-03 — Wizard assign margin massal

**AC-03-01** (verifies `BSL-002`)
Given wizard dibuka dari list view Product Template, pilih 3 produk, isi margin
When klik tombol "Assign" (`action_assing_margin`, nama typo dipertahankan)
Then ketiga margin ter-update.

**AC-03-02** (verifies `BSL-002`)
Given wizard dibuka dari list view Product Variants
When wizard terbuka
Then field `product_ids` yang tampil (bukan `product_template_ids`).

## AC-04 — Koeksistensi cross-module (`pos_margin_threshold` + `sale_margin_threshold`)

**AC-04-01** (verifies `BSL-012`, `MF-02`)
Given HANYA modul ini terinstall
When admin buka Settings
Then tidak ada UI untuk `blocking_transaction_order` (identik 17.0).

**AC-04-02 — TERKAIT `MF-03`** (verifies `BSL-013`)
Given KEDUA modul terinstall
When registry dibangun ulang
Then `wizard.margin.product` MRO cuma berisi kelas dari modul yang install belakangan (identik 17.0) — **WAJIB dites dengan urutan install SAMA seperti backfill** (`-i pos_margin_threshold,sale_margin_threshold`) supaya hasil MRO comparable.
