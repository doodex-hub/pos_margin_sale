# Migration Acceptance Criteria — sale_margin_threshold

**Step:** 5 — Acceptance Criteria & Test Plan
**Ref:** `01_intake/sale_margin_threshold/01b_BASELINE_SPEC.md` dan kode 18.0 yang berjalan
**Tanggal:** 2026-08-26

---

## AC-01 — Konfirmasi Sale Order (blocking/wizard)

**AC-01-01** (verifies `BSL-001`)
Given Sale Order rental (`is_rental_order_installed_true = True`)
When `action_confirm()` dipanggil
Then order langsung terkonfirmasi TANPA pengecekan margin sama sekali.

**AC-01-02** (verifies `BSL-002`, `BSL-003`)
Given Sale Order non-rental dengan line di bawah `minimum_sale_price`, DAN
`blocking_transaction_order = True`
When `action_confirm()` dipanggil
Then `ValidationError` di-raise dengan pesan bilingual sesuai bahasa user (`detect_user_language()`)
— order TIDAK terkonfirmasi.

**AC-01-03** (verifies `BSL-002`)
Given kondisi sama, tapi `blocking_transaction_order = False` (default)
When `action_confirm()` dipanggil
Then `sale.confirmation.wizard` dibuka (modal `target='new'`), order BELUM terkonfirmasi.

**AC-01-04** (verifies `BSL-004`)
Given wizard konfirmasi terbuka
When user klik tombol confirm di wizard
Then order terkonfirmasi via `with_context(skip_check_price=True).action_confirm()` — TIDAK ada
loop rekursi/pengecekan margin ulang.

**AC-01-05** (verifies `BSL-006`, MF-21 RESOLVED)
Given user berbahasa Prancis (`lang` prefix `fr`)
When pesan margin (blocking atau wizard) ditampilkan
Then teks bilingual Prancis muncul — TANPA butuh `fr_FR` genuinely terinstall sebagai `res.lang`
(fix `MF-21`, harus dipertahankan — grep `fr_FR` di kode = 0 match).

## AC-02 — Margin & Minimum Sale Price (identik pola `pos_margin_threshold`)

**AC-02-01** (verifies §3 Model — sama seperti `pos_margin_threshold` `AC-01-01`)
Given produk dengan `standard_price`/`margin_sale`
When `minimum_sale_price` di-compute
Then hasil identik formula `pos_margin_threshold` — kedua modul mendefinisikan field yang sama
secara independen (bukan shared code), harus tetap konsisten satu sama lain.

**AC-02-02** (verifies `BSL-008` deduplikasi UI)
Given `pos_margin_threshold` DAN `sale_margin_threshold` terinstall bersamaan
When form Product Template/Variant dibuka
Then field margin HANYA muncul SATU KALI (tidak duplikat) — dikonfirmasi Step 10 project 17→18 lewat
inspeksi DOM langsung.

## AC-03 — Wizard Bulk-Assign Margin (byte-identik `pos_margin_threshold`)

**AC-03-01** (verifies §4 Model — sama seperti `pos_margin_threshold` AC-03-01/02/03)
Given user membuka wizard "Update margin sale" dari list Template/Variant
When isi margin, klik Assign/Cancel
Then behavior identik dengan `pos_margin_threshold` (kedua modul wizard byte-identik kecuali
`MF-03` MRO collision — lihat AC-04 di bawah).

## AC-04 — Interaksi Cross-Module

**AC-04-01** (verifies `BSL-014`, ref `FINDINGS.md` `MF-03`)
Given `pos_margin_threshold` DAN `sale_margin_threshold` terinstall bersamaan
When registry model `wizard.margin.product` dibangun
Then `__mro__` HANYA berisi class `sale_margin_threshold` (modul INI menang) — dikonfirmasi
independen urutan install. Test: `tests/test_cross_module.py::test_wizard_margin_product_model_merged_when_both_installed`.

**AC-04-02** (verifies `BSL-010`, ref `FINDINGS.md` `MF-05`, `MF-07`)
Given `pos_margin_threshold` terinstall
When `_register_hook()` dijalankan (setiap registry rebuild)
Then grup `group_sale_margin_action` dikosongkan dari semua user — server action "Update margin
sale" tidak muncul di menu Actions. Kalau `pos_margin_threshold` TIDAK terinstall, grup diberikan ke
semua user internal.

**AC-04-03** (batch-confirm, ref `FINDINGS.md` `MF-08` — `[PERLU-KEPUTUSAN]`)
Given user melakukan batch-confirm 2+ Sale Order sekaligus (bulk action dari list view)
When `action_confirm()` dipanggil untuk recordset multi-record
Then **behavior SAAT INI (bug, harus dipertahankan identik KECUALI user putuskan diperbaiki)**:
hanya record PERTAMA di `self` yang benar-benar dicek/dipengaruhi logic margin (karena kode tidak
`for order in self:`) — dikonfirmasi Step 2: blast radius bug ini SAMA di 19.0 seperti 18.0, core
tidak pernah membatasi `action_confirm` ke singleton di versi manapun.

---

**Ringkasan traceability:** 11 AC, mencakup semua `BSL-NNN` §4/§5/§8 kecuali `BSL-005`
(`module_pos_margin_threshold` murni internal compute flag, sudah tercakup implisit di `AC-02-02`),
`BSL-011` (efisiensi `@api.depends_context`, tidak ada behavior user-facing untuk diverifikasi),
`BSL-012`/`BSL-013` (dead/cruft file, cukup code review Step 8, bukan test runtime).
