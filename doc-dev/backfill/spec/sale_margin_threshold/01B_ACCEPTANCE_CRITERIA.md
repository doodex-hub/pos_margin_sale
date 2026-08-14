# Acceptance Criteria — sale_margin_threshold

**Module:** `sale_margin_threshold`
**Ref:** `01A_FUNCTIONAL_SPEC.md`
**Last Updated:** 2026-07-31
**Status:** Backfill retroaktif

---

## AC-01 — Validasi harga minimum saat confirm (single order)

**AC-01-01** — ref `BR-01` `[HASIL-BACA]`
Given `blocking_transaction_order = True`, quotation punya 1 baris dengan `price_unit < minimum_sale_price`
When user klik "Confirm"
Then `ValidationError` di-raise, pesan bilingual sesuai bahasa user, order TETAP status draft/sent
(tidak pernah confirmed).

**AC-01-02** — ref `BR-01` `[HASIL-BACA]`
Given `blocking_transaction_order = False`, quotation punya baris di bawah minimum
When user klik "Confirm"
Then wizard `sale.confirmation.wizard` terbuka dengan pesan sesuai bahasa; kalau user klik "Confirm"
di wizard, order benar-benar ter-confirm (`skip_check_price=True` di panggilan kedua).

**AC-01-03** — ref `BR-01` `[HASIL-BACA]`
Given semua baris quotation harganya di atas/sama dengan minimum
When user klik "Confirm"
Then langsung `super().action_confirm()`, tidak ada popup/wizard apapun.

**AC-01-04** — ref `BR-01` `[HASIL-BACA]`
Given modul rental (`sale_renting` atau serupa) terinstall dan order ini `is_rental_order = True`
When user klik "Confirm"
Then validasi margin DI-SKIP TOTAL, langsung `super().action_confirm()`, terlepas dari harga baris
apapun.

---

## AC-02 — Batch confirm (multi-record) — BUG

**AC-02-01** — ref `BR-02` `[PERLU-KEPUTUSAN]` — **TERKONFIRMASI GANDA lewat eksekusi nyata, Docker 2026-07-31**
Given user memilih LEBIH DARI SATU quotation di list view (mis. 2 sale order draft)
When user klik action "Confirm" dari list view (batch action, didukung Odoo core secara native)
Then Python `ValueError: Expected singleton: sale.order(id1, id2)` BENAR-BENAR di-raise saat baris
`self.is_rental_order_installed_true` dieksekusi — batch confirm GAGAL TOTAL untuk semua order yang
dipilih, bukan cuma yang bermasalah. Dikonfirmasi 2 kali independen: (1) test
`tests/test_action_confirm.py::test_action_confirm_BATCH_MULTI_ORDER_F05`; (2) demo data BAWAAN
Odoo core (`sale_stock`) ikut crash dengan error identik saat modul ini terinstall. Lihat **F-05**,
prioritas Tinggi.

---

## AC-03 — Wizard konfirmasi

**AC-03-01** — ref `BR-04` `[HASIL-BACA]`
Given wizard `sale.confirmation.wizard` terbuka dari context `active_model=sale.order`,
`active_ids=[id_order]`
When user klik "Confirm" di wizard
Then order yang sama di-confirm ulang dengan `skip_check_price=True`, kali ini benar-benar lolos ke
`super().action_confirm()`.

**AC-03-02** — ref `BR-04` `[HASIL-BACA]`
Given user klik "Cancel" di wizard (`special="cancel"`)
When wizard ditutup
Then TIDAK ADA aksi apapun ke sale order — order tetap draft/sent, tidak pernah confirm.

---

## AC-04 — Koeksistensi dengan `pos_margin_threshold` (cross-module)

**AC-04-01** — ref `BR-05` `[PERLU-KEPUTUSAN]` — **TERKONFIRMASI eksekusi nyata, Docker 2026-07-31**
Given `pos_margin_threshold` TERINSTALL bersamaan dengan modul ini
When registry Odoo di-build ulang (install/upgrade/restart worker)
Then SEMUA user dihapus dari `group_sale_margin_action` (dikonfirmasi: `group.users.ids == []` di
database test setelah kedua modul terinstall) — action "Update margin sale" milik modul INI (yang
di-gate group ini) jadi tidak terlihat siapapun di menu Product. Lihat **F-04**.

**AC-04-02** — ref `BR-05` `[PERLU-KEPUTUSAN]`
Given admin SECARA MANUAL menambahkan seorang user ke `group_sale_margin_action` saat
`pos_margin_threshold` masih terinstall
When registry Odoo reload berikutnya terjadi (restart worker, install modul lain, dst — BUKAN aksi
user yang disengaja)
Then (dugaan `[HASIL-BACA]`, belum diverifikasi eksekusi nyata) perubahan manual admin
KEMUNGKINAN BESAR terhapus lagi oleh `_register_hook` tanpa notifikasi apapun. Perlu keputusan
pemilik modul apakah ini perilaku yang diinginkan.

**AC-04-03** — ref `BR-06` `[HASIL-BACA]`
Given kedua modul terinstall, user membuka form Product Template
When field `module_pos_margin_threshold` compute jadi `True`
Then field `margin_sale`/`minimum_sale_price` milik VIEW modul ini (`sale_margin_threshold`)
disembunyikan (`invisible`) — hanya versi dari `pos_margin_threshold` yang tampil, mencegah field
dobel.
