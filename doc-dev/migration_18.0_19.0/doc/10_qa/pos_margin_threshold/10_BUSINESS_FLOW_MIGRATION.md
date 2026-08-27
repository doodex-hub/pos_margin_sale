# Business Flow — Migrasi pos_margin_threshold

**Step:** 10 — QA Testing (gate)
**Ref:** `05_acceptance/pos_margin_threshold/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-08-27

> Port kode saja, tidak ada instance produksi — dijalankan sebagai install bersih (bukan clone data
> produksi), konsisten dengan Step 7 N/A.

**Mode eksekusi dipilih:** AI+tool eksternal — Playwright (Node.js, headless Chromium), bukan
Claude Browser MCP internal (gagal total di environment ini — Service Worker registration error,
`document.body.innerHTML` cuma 24 karakter, screenshot gagal "Browser pane is not displayed") dan
tidak ada Claude in Chrome terhubung. Script disimpan di scratchpad
(`playwright-qa/qa_step10.js`) — tidak dicommit ke repo (bukan bagian scaffold `playwright/`
permanen modul, dibuat khusus sesi ini). Server: Docker `docker-env/` (Mode G2-live, image
`odoo:19.0`, db `pos_margin_sale_migration_19_qa`, port `8079`).

Semua AC UI dalam-modul yang sudah tercover Tour test Step 9 (`AC-02-01/02`) **tidak diulang di
sini** sesuai prinsip "Step 10 bukan tempat default untuk regresi UI dalam-modul yang sudah dicover
tour".

---

### S-10-02: Wizard "Update margin sale" dari list Product Template
**Level:** Main Flow
**Precondition:** Ketiga modul terinstall bersamaan (`pos_margin_threshold`, `sale_margin_threshold`,
`pin_message`), minimal 1 produk ada (`Tips`).
**Mode eksekusi:** AI+tool eksternal (Playwright, `qa_step10.js` — skenario S-10-02)
**Steps:**
1. Buka Inventory > Products (list view), pilih 1 produk via checkbox.
2. Buka menu Actions (gear icon).
3. Konfirmasi entry "Update margin sale" muncul (bukan 2 entry duplikat dari kedua modul — lihat
   catatan cross-module di bawah).
4. Klik entry tersebut.
**Expected:** Wizard terbuka menampilkan field `product_template_ids` berlabel "Products", BUKAN
"Product variants".
**Actual:** Wizard terbuka, field berlabel "Products" berisi `[TIPS] Tips`, field Margin kosong
(0.00%). Tidak ada error console. Screenshot: `shot_08_wizard_from_template_list.png`.
**Status:** [x] Pass / [ ] Fail
**Provenance:** [DIKONFIRMASI]

**Catatan cross-module (bonus verifikasi AC-04-02 `sale_margin_threshold`):** hanya SATU entry
"Update margin sale" muncul di Actions menu, bukan dua — mengonfirmasi `_register_hook()`
`sale_margin_threshold` benar-benar mengosongkan `group_sale_margin_action` saat
`pos_margin_threshold` terinstall bersamaan (fix `MF-17`, `res.groups.user_ids`).

---

### S-10-03: Wizard "Update margin sale" dari list Product Variants
**Level:** Main Flow
**Precondition:** Sama seperti S-10-02. Fitur "Variants" (`product.group_product_variant`) harus
aktif di Inventory Settings — **CATATAN:** di database QA ini, fitur tersebut awalnya TIDAK aktif
(baru instalasi bersih), sehingga menu "Product Variants" tidak muncul sama sekali sampai diaktifkan
manual lewat Inventory > Configuration > Settings > centang "Variants" > Save. Ini setting Odoo
native, bukan sesuatu yang disentuh migrasi modul ini.
**Mode eksekusi:** AI+tool eksternal (Playwright, `qa_step10.js` — skenario S-10-03)
**Steps:**
1. Aktifkan fitur "Variants" (lihat Precondition).
2. Buka Inventory > Products > Product Variants.
3. Pilih 1 baris, buka Actions > "Update margin sale".
**Expected:** Wizard menampilkan field `product_ids` berlabel "Product variants" (BUKAN
"Products") — per `AC-03-02`.
**Actual:** Wizard terbuka, field berlabel "Product variants" berisi `[TIPS] Tips`. Screenshot:
`shot_11_wizard_from_variants_list.png`.
**Status:** [x] Pass / [ ] Fail
**Provenance:** [DIKONFIRMASI]

**Catatan gap tertutup:** `AC-03-02` sebelumnya berstatus gap carry-forward sejak project 17→18
(belum pernah dieksekusi otomatis) — sekarang genuinely dieksekusi live untuk pertama kalinya di
project ini.

---

### S-10-05: Wizard "Update margin sale" — tombol Cancel = tidak ada perubahan
**Level:** Detail
**Precondition:** Sama seperti S-10-02, produk `Tips` bermargin awal `0.00%`.
**Mode eksekusi:** AI+tool eksternal (Playwright, `qa_step10.js` — skenario S-10-05)
**Steps:**
1. Buka form produk `Tips`, catat nilai Margin (`0.00`).
2. Kembali ke list, pilih produk, buka wizard "Update margin sale".
3. Isi Margin dengan nilai baru (`37`), screenshot untuk bukti input benar-benar masuk ke field
   Margin (bukan field lain).
4. Klik "Cancel" (bukan "Assign").
5. Buka ulang form produk `Tips`, baca ulang nilai Margin.
**Expected:** Margin produk TIDAK berubah (tetap `0.00`) — sesuai `AC-03-03`.
**Actual:** Margin sebelum = `0.00`, wizard terisi `37` (dikonfirmasi visual di
`shot_14_wizard_margin_filled_before_cancel.png` — field Margin terisi `37`, bukan field Products),
margin sesudah Cancel = `0.00`. Tidak berubah.
**Status:** [x] Pass / [ ] Fail
**Provenance:** [DIKONFIRMASI]

---

## Skenario yang TIDAK dieksekusi (gap diterima, carry-forward)

- **AC-02-03** (tidak ada popup kalau semua line valid) dan **AC-02-04** (assert visual teks/warna
  warning orderline) — butuh sesi POS register penuh (buka sesi kasir, transaksi riil). Gap terbuka
  sejak project 17→18, risiko rendah diterima (positive-path payment-blocking sudah dibuktikan 2x
  lewat Tour test Step 9 di jalur negative-nya). **Tidak diprioritaskan project ini** sesuai verdict
  Step 9 — tidak dieskalasi ulang di sini.

## Ringkasan per Level

| Level | Skenario | Jumlah |
|---|---|---|
| Smoke | — | 0 |
| Main Flow | S-10-02, S-10-03 | 2 |
| Detail | S-10-05 | 1 |
| Negative | — | 0 |

## Rekap Provenance

| Provenance | Jumlah | Skenario |
|---|---|---|
| `[DIKONFIRMASI]` | 3 | S-10-02, S-10-03, S-10-05 |
| `[HASIL-BACA]` | 0 | — |
| `[PERLU-KEPUTUSAN]` | 0 | — |

## Loop-back

Tidak ada skenario Fail — tidak perlu loop-back ke Step 9.

## Verdict

- [x] ✅ Lulus — lanjut ke step 11
