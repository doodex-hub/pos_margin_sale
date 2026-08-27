# Test Plan (Migrasi) — pos_margin_threshold

**Step:** 5 — Acceptance Criteria & Test Plan
**Ref:** `05_acceptance/pos_margin_threshold/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-08-26

---

## Step 9 — Dev Testing

Test existing (dari project 17.0→18.0, sudah lulus penuh sebagai baseline 18.0): `tests/test_margin_sale.py`,
`tests/test_cross_module.py`, `tests/test_margin_threshold_tour.py` +
`static/tests/tours/margin_threshold_tour.js`. Semua HARUS dijalankan ulang setelah Step 6 (porting
`DIFF-06`/`07`/`08`/`09`) — kemungkinan besar tour test akan GAGAL sebelum fix diterapkan (bukti
langsung blocker `MF-12`/`MF-13`), lalu harus PASS setelahnya.

| AC | Deskripsi | Unit | Integration | Tour (Owl/JS) |
|---|---|---|---|---|
| AC-01-01/02/03 | Margin/minimum price compute+inverse, decoration | `test_margin_sale.py` | — | — |
| AC-02-01 | Payment blocking — jalur confirm | — | — | `margin_threshold_tour.js` — `pos_margin_threshold_below_minimum_confirm_tour` (existing, WAJIB re-run pasca Step 6) |
| AC-02-02 | Payment blocking — jalur blocked | — | — | `margin_threshold_tour.js` — `pos_margin_threshold_below_minimum_blocked_tour` (existing, WAJIB re-run) |
| AC-02-03 | Tidak ada popup kalau semua line valid | — | *(belum ada — gap terbuka sejak 17→18)* | — |
| AC-02-04 | Assert visual warning teks/warna orderline | — | *(belum ada — gap terbuka sejak 17→18)* | — |
| AC-03-01/02/03 | Wizard bulk-assign margin | — | *(belum ada dedicated test — diverifikasi Step 10 lewat interaksi manual di project 17→18)* | — |
| AC-04-01 | Kolisi `wizard.margin.product` MRO | `test_cross_module.py` | — | — |

## Step 10 — QA Testing

| AC | Deskripsi | Manual | AI-interaktif | AI+tool eksternal |
|---|---|---|---|---|
| AC-03-01/02 | Wizard assign margin dari list Template/Variant | — | ✅ (pola sama seperti project 17→18 — Claude in Chrome, buka wizard dari kedua konteks, verifikasi field yang tampil + hasil assign) | — |
| AC-03-03 | Wizard Cancel tidak mengubah apapun | — | ✅ | — |
| AC-02-03/04 | Negative control (no popup) + assert visual warning | ✅ *(butuh sesi POS register penuh, belum pernah dieksekusi baik 17→18 maupun sekarang)* | — | — |

## Step 11 — UAT

| Kelompok fitur | AC tercakup | UAT |
|---|---|---|
| Margin & minimum price | AC-01-01/02/03 | Skenario bahasa awam: buat produk, isi margin, lihat harga minimum terhitung otomatis |
| Payment blocking | AC-02-01/02 | Skenario: jual produk murah di POS, lihat dialog konfirmasi/blokir |
| Wizard bulk-assign | AC-03-01/02/03 | Skenario: pilih beberapa produk, update margin sekaligus lewat wizard |

## Ringkasan

| Step | Role | Tipe | Eksekusi | Jumlah AC |
|---|---|---|---|---|
| 9 | Developer | Unit/Integration/Tour (Owl/JS) | Otomatis/background, WAJIB re-run pasca porting Step 6 | 7 dari 11 AC punya test otomatis existing |
| 10 | QA | Manual/AI-interaktif | Campuran | 5 AC (3 AI-interaktif, 2 manual butuh POS register) |
| 11 | PM/FA/User | UAT | Manual (selalu) | 3 kelompok fitur |
