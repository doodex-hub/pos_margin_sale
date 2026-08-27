# Business Flow — Migrasi sale_margin_threshold

**Step:** 10 — QA Testing (gate)
**Ref:** `05_acceptance/sale_margin_threshold/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-08-27

> Port kode saja, tidak ada instance produksi — dijalankan sebagai install bersih, konsisten dengan
> Step 7 N/A.

**Mode eksekusi dipilih:** AI+tool eksternal — Playwright (Node.js, headless Chromium), bukan
Claude Browser MCP internal (gagal total di environment ini) dan tidak ada Claude in Chrome
terhubung. Script: scratchpad `playwright-qa/qa_step10.js` (tidak dicommit). Server: Docker
`docker-env/` (Mode G2-live, `odoo:19.0`, db `pos_margin_sale_migration_19_qa`, port `8079`).

Modul ini tidak punya JS/Owl (N/A Tour test) — semua AC backend sudah tercover unit/integration
test Step 9. Fokus Step 10 di sini: verifikasi UI yang HANYA bisa diamati lewat browser (dedup
field, dedup action menu lintas modul).

---

### S-10-04: Field margin TIDAK duplikat di form Product (kedua modul margin terinstall)
**Level:** Main Flow
**Precondition:** `pos_margin_threshold` DAN `sale_margin_threshold` terinstall bersamaan.
**Mode eksekusi:** AI+tool eksternal (Playwright, `qa_step10.js` — skenario S-10-04)
**Steps:**
1. Buka form produk apapun (Inventory > Products > buka satu produk).
2. Hitung berapa kali label field margin (`margin_sale`) muncul di form.
**Expected:** Field Margin muncul HANYA SATU KALI (per `AC-02-02`) — bukti nyata `product_view`
inherit dari kedua modul tidak saling duplikat elemen di DOM akhir.
**Actual:** 1 elemen field margin ditemukan di form produk `Tips` (Margin `0.00%`, Minimum sale
price `$0.00`). Screenshot: `shot_12_product_form.png`.
**Status:** [x] Pass / [ ] Fail
**Provenance:** [DIKONFIRMASI]

**Catatan gap tertutup:** `AC-02-02` sebelumnya belum pernah dieksekusi otomatis di project ini
(hanya "dikonfirmasi Step 10 project 17→18" secara historis) — sekarang genuinely dieksekusi live
ulang untuk versi 19.0.

---

### S-10-02/S-10-03 (lihat detail penuh di `10_qa/pos_margin_threshold/10_BUSINESS_FLOW_MIGRATION.md`) — dedup Actions menu
**Level:** Main Flow
**Precondition:** Sama seperti di atas.
**Mode eksekusi:** AI+tool eksternal (Playwright, `qa_step10.js` — skenario S-10-02)
**Steps:** Buka Actions menu dari list Product Template dengan 1 produk terpilih.
**Expected:** Hanya SATU entry "Update margin sale" muncul (bukan dua, satu per modul) — per
`AC-04-02`: `_register_hook()` `sale_margin_threshold` mengosongkan `group_sale_margin_action`
(fix `MF-17`, `res.groups.user_ids`) saat `pos_margin_threshold` terinstall, sehingga action milik
`sale_margin_threshold` tidak muncul di menu — yang tersisa cuma action `pos_margin_threshold`.
**Actual:** Hanya 1 entry "Update margin sale" muncul di dropdown Actions (screenshot:
`shot_07_actions_menu_open.png`), wizard yang terbuka menampilkan field label "Products"/"Product
variants" sesuai konteks list — perilaku wizard byte-identik `pos_margin_threshold` (`AC-03-01`,
lihat dokumen modul itu untuk detail penuh kedua skenario).
**Status:** [x] Pass / [ ] Fail
**Provenance:** [DIKONFIRMASI]

---

## Skenario yang TIDAK dieksekusi (N/A/gap diterima, carry-forward)

- **AC-01-01** (rental exemption) — **N/A permanen**, environment test ini Community-only, tidak
  ada Enterprise (`sale_renting`) terinstall. Sudah dicatat sebagai N/A sejak Step 9.
- **AC-01-05** (bilingual FR tanpa `fr_FR`) — sudah divalidasi lewat run manual `--load-language=fr_FR`
  di project 17→18 sebelumnya (`MF-21` resolved), kode tidak diubah sejak itu — risiko rendah,
  tidak diulang di project ini.
- **AC-04-03** (batch-confirm singleton bug, `MF-08`) — sudah PENUH dibuktikan via unit test Step 9
  (`test_action_confirm_BATCH_MULTI_ORDER_F05`, membuktikan bug MASIH ADA sesuai keputusan user
  "biarkan dulu, pastikan tercatat di finding"). Tidak perlu diulang manual di Step 10 — behavior
  bug ini tidak punya komponen UI/browser yang unit test tidak bisa jangkau.

## Ringkasan per Level

| Level | Skenario | Jumlah |
|---|---|---|
| Smoke | — | 0 |
| Main Flow | S-10-04, S-10-02/03 (dedup Actions) | 2 |
| Detail | — | 0 |
| Negative | — | 0 |

## Rekap Provenance

| Provenance | Jumlah | Skenario |
|---|---|---|
| `[DIKONFIRMASI]` | 2 | S-10-04, S-10-02/03 |
| `[HASIL-BACA]` | 0 | — |
| `[PERLU-KEPUTUSAN]` | 0 | — |

## Loop-back

Tidak ada skenario Fail — tidak perlu loop-back ke Step 9.

## Verdict

- [x] ✅ Lulus — lanjut ke step 11
