# Migration Acceptance Criteria — sale_margin_threshold

**Step:** 5 — Acceptance Criteria & Test Plan
**Ref:** `01_intake/sale_margin_threshold/01b_BASELINE_SPEC.md` dan kode 17.0 — bukan `03_MIGRATION_SPEC.md`
**Tanggal:** 2026-08-24

---

## AC-01 — Validasi harga minimum saat confirm (single order) — TERKAIT `DIFF-01` (Critical Blocker)

**AC-01-01** (verifies `BSL-001`)
Given `blocking_transaction_order = True`, quotation punya baris `price_unit < minimum_sale_price`
When user klik "Confirm"
Then `ValidationError` (pesan bilingual sesuai bahasa), order tetap draft/sent — **membuktikan `DIFF-01` (fix `/tree`→`/list`) tidak merusak alur ini**.

**AC-01-02** (verifies `BSL-001`)
Given `blocking_transaction_order = False`, ada baris di bawah minimum
When user klik "Confirm"
Then wizard `sale.confirmation.wizard` terbuka; confirm ulang di wizard → order benar-benar ter-confirm.

**AC-01-03** (verifies `BSL-001`)
Given semua baris di atas/sama minimum
When user klik "Confirm"
Then langsung confirm, tidak ada popup.

**AC-01-04** (verifies `BSL-001`)
Given modul rental terinstall dan order ini rental
When user klik "Confirm"
Then validasi margin di-skip total.

## AC-02 — Batch confirm (bug existing, `MF-06`) — PRIORITAS TINGGI

**AC-02-01** (verifies `BSL-002`, `MF-06`)
Given user memilih >1 quotation di list view
When klik action "Confirm" batch
Then **`ValueError: Expected singleton` tetap terjadi identik dengan 17.0** — re-run `tests/test_action_confirm.py::test_action_confirm_BATCH_MULTI_ORDER_F05`. Kalau di 18.0 ternyata TIDAK crash (karena mekanisme batch action berubah, `DIFF-02`), itu **perubahan behavior yang tidak disengaja** — WAJIB dieskalasi ke user (format `ESCALATION` di `CLAUDE.md`), bukan diam-diam dianggap "sudah lebih baik".

## AC-03 — Wizard konfirmasi

**AC-03-01** (verifies `BSL-004`)
Given wizard `sale.confirmation.wizard` terbuka
When user klik "Confirm" di wizard
Then order di-confirm ulang dengan `skip_check_price=True`, lolos ke `super().action_confirm()`.

**AC-03-02** (verifies `BSL-004`)
Given user klik "Cancel"
When wizard ditutup
Then tidak ada aksi ke sale order.

## AC-04 — Koeksistensi dengan `pos_margin_threshold`

**AC-04-01** (verifies `BSL-006`, `MF-05`)
Given `pos_margin_threshold` terinstall bersamaan
When registry dibangun ulang
Then semua user dihapus dari `group_sale_margin_action` (identik 17.0).

**AC-04-02** (verifies `BSL-007`, `MF-03`)
Given kedua modul terinstall
When registry dibangun (urutan `-i sale_margin_threshold,pos_margin_threshold` — **urutan KEBALIKAN dari test `pos_margin_threshold`**, untuk membuktikan MRO tergantung urutan install, bukan modul spesifik)
Then `wizard.margin.product` MRO cuma berisi kelas modul yang install belakangan.

**AC-04-03** (verifies `BSL-005`)
Given kedua modul terinstall, user buka form Product Template
When `module_pos_margin_threshold` compute `True`
Then field margin milik modul INI disembunyikan.
