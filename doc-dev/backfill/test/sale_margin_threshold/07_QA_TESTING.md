# QA Testing — sale_margin_threshold

**Step:** 07 — QA Testing (backfill, TANPA UAT)
**Ref:** `doc-dev/backfill/spec/sale_margin_threshold/01A_FUNCTIONAL_SPEC.md`, `01B_ACCEPTANCE_CRITERIA.md`, `test/sale_margin_threshold/03B_TEST_PLAN.md`
**Tanggal:** 2026-07-31

---

## 1. Area yang Harus Dicakup

- [x] Validasi harga minimum saat confirm quotation (blocking vs wizard vs normal)
- [x] **Batch confirm multi-order (F-05)** — cek wajib "hanya satu dialog/wizard disentuh" TIDAK
  relevan di sini (bukan kasus dialog ganda), tapi ini kandidat skenario wajib versi lain: "aksi
  batch dari list view" yang perlu dicek eksplisit karena berpotensi merusak fitur native Odoo.
- [x] Dedup action "Update margin sale" antar modul (F-04)
- [ ] Rental order skip (AC-01-04) — TIDAK bisa diuji, `sale_renting`/modul rental tidak terinstall
  di environment ini (lihat §4 keterbatasan)

---

## 2. Format Skenario

Sama seperti `doc-dev-backfill/templates/test/07_QA_TESTING.md` §2.

---

## 3. Skenario

### S-01: Batch-confirm 2+ quotation dari list view (F-05)
**Precondition:** 2 quotation berstatus draft (`S00002`, `S00003`, hasil demo data `sale_stock` yang
sempat gagal sebagian — lihat §4), pilih via checkbox di list view "Quotations".
**Mode eksekusi:** Mode C (Docker) — **Unit test langsung** (`TransactionCase`), BUKAN klik UI asli.
**Steps:**
1. `order_1, order_2 = ` 2 sale.order draft dengan produk & harga di atas minimum.
2. Panggil `(order_1 + order_2).action_confirm()` langsung (mensimulasikan efek klik "Confirm"
   batch dari list view — Odoo menerjemahkan aksi UI itu jadi panggilan method persis ini pada
   recordset multi-record).
**Expected:** Berdasar kode, harus `ValueError: Expected singleton`.
**Actual:** **`ValueError: Expected singleton: sale.order(25, 26)` — PERSIS seperti diduga.**
Ditemukan LAGI (independen) sebagai kegagalan demo data `sale_stock` core sendiri saat instalasi
modul (`sale.order(21, 22, 23, 24)`).
**Status:** ✅ Pass (temuan bug F-05 TERKONFIRMASI, bukan "Pass" dalam arti "modul bekerja benar" —
ini test yang MEMBUKTIKAN bug-nya nyata)
**Provenance:** `[PERLU-KEPUTUSAN]` — lihat `FINDINGS.md` F-05.

### S-02: Verifikasi UI batch-confirm — DESK-REVIEW (keterbatasan lingkungan, lihat §4)
**Precondition:** Server Odoo G2 hidup (`docker-env`, mode server tetap hidup), login admin/admin.
**Mode eksekusi:** AI-in-the-loop browser (Claude in Chrome) — **DICOBA, GAGAL**, lihat §4.
**Steps direncanakan:** buka Quotations list, pilih 2 baris draft (S00002, S00003), klik "Confirm",
amati pesan error yang muncul ke user.
**Expected:** Error `ValueError`/traceback Odoo (atau notifikasi merah) muncul ke user, batch gagal
total untuk KEDUA order.
**Actual:** Tidak bisa dieksekusi — interaksi klik/keyboard berhenti terdaftar sama sekali di
tab browser (Chrome asli via `mcp__claude-in-chrome`) setelah beberapa navigasi awal berhasil
(login berhasil, navigasi ke Sales Orders/Quotations via URL berhasil) — screenshot tetap render
normal, tapi klik pada tombol/link/checkbox APAPUN di halaman SPA Odoo (New, row link, checkbox,
search box) tidak lagi memicu efek apapun, termasuk setelah reload halaman. `mcp__Claude_Browser`
(pane virtual) GAGAL LEBIH AWAL dengan pesan eksplisit "the Browser pane is not displayed" —
sama seperti root cause yang sudah terdokumentasi di `doc-dev-backfill/ai-doc/USAGE_GUIDE.md`
§Mode E untuk sesi CLI.
**Status:** ⬜ Tidak dieksekusi (limitasi lingkungan, BUKAN "Fail")
**Provenance:** `[HASIL-BACA]` untuk expected outcome — TIDAK diklaim "sudah dites via browser".

### S-03: Dedup action "Update margin sale" (F-04) — via Unit test
**Precondition:** Kedua modul (`pos_margin_threshold` + `sale_margin_threshold`) terinstall.
**Mode eksekusi:** Mode C (Docker) — Unit test.
**Steps:** Baca `group_sale_margin_action.users` setelah registry dibangun dengan kedua modul.
**Expected:** Kosong (tidak ada user).
**Actual:** `group_sale_margin_action.users=[]` — sesuai dugaan.
**Status:** ✅ Pass
**Provenance:** `[PERLU-KEPUTUSAN]` (mekanismenya fragile meski hasilnya sesuai dugaan) — lihat F-04.

### S-04: Validasi harga minimum single-order (blocking & wizard) — via Unit test
**Precondition:** 1 quotation, 1 baris produk di bawah minimum.
**Mode eksekusi:** Mode C (Docker) — Unit test (`TransactionCase`).
**Steps:** `action_confirm()` dengan `blocking_transaction_order` True lalu False (2 order
terpisah).
**Expected:** True → `ValidationError`; False → wizard, lalu confirm sukses setelah
`skip_check_price=True`.
**Actual:** Sesuai expected, keduanya Pass (`tests/test_action_confirm.py`).
**Status:** ✅ Pass
**Provenance:** `[DIKONFIRMASI]`

---

## 4. Status Sub-file & Rekap Eksekusi

| File | Isi | Status | Dieksekusi? | Mode |
|---|---|---|---|---|
| §3 di file ini | Skenario umum | ✅ Selesai | Ya (S-01, S-03, S-04 via Unit test; S-02 gagal) | Mode C (Unit test) + AI-Browser (gagal) |
| `07B_QA_AI_BROWSER.md` | — | N/A | Tidak dibuat | Lihat alasan di bawah |

**Kenapa `07B_QA_AI_BROWSER.md` TIDAK dibuat:** template mengasumsikan verifikasi browser BERHASIL
dijalankan (isinya laporan hasil). Sesi ini mencoba 2 mekanisme browser berbeda
(`mcp__Claude_Browser` dan `mcp__claude-in-chrome`) — keduanya gagal karena alasan berbeda (lihat
S-02) sebelum sempat menghasilkan satu skenario browser yang benar-benar selesai. Membuat file
kosong/placeholder melanggar prinsip `dev-workflow`/`doc-dev-backfill` "jangan buat file untuk
metode yang belum benar-benar dipakai" — limitasi ini dicatat di sini dan `FINDINGS.md` saja.

**Keterbatasan eksekusi (WAJIB diisi):**
1. Rental order skip (AC-01-04) — modul rental (`sale_renting` dst) tidak terinstall di image
   `odoo:17.0` community yang dipakai, TIDAK bisa diuji eksekusi nyata. Tetap `[HASIL-BACA]`.
2. Verifikasi visual browser (S-02) — GAGAL total lewat 2 mekanisme berbeda (lihat detail S-02).
   **Bukti pengganti yang dipakai:** Step 04 Unit test (`TransactionCase`) langsung memanggil
   method yang SAMA yang dipanggil UI saat user klik "Confirm" — untuk kasus batch-confirm,
   ini SECARA TEKNIS SAMA PERSIS dengan apa yang terjadi saat user pilih multi-row + klik Confirm
   (Odoo web client menerjemahkan klik itu jadi RPC `call_kw` yang memanggil `action_confirm()`
   pada recordset yang sama) — jadi walau bukan verifikasi visual, ini BUKAN desk-review lemah,
   tapi eksekusi kode PRODUKSI yang identik dengan jalur UI.

---

## 5. Rekap Findings

| Tag | Jumlah |
|---|---|
| `[PERLU-KEPUTUSAN]` | 3 (F-03, F-04, F-05 — semua terkait/melibatkan modul ini) |
| `[DIKONFIRMASI]` | beberapa AC dasar (lihat `01B_ACCEPTANCE_CRITERIA.md`) |
| `[HASIL-BACA]` (tanpa masalah) | sisanya |

**Verdict:** Backfill dokumentasi selesai sampai Step 07. **Tidak ada sign-off.** F-05 (Tinggi)
adalah temuan paling penting sesi ini — WAJIB direview pemilik modul sebelum modul ini dipakai di
alur kerja yang melibatkan batch-confirm quotation.

---

## 6. Bug / Perlu Perbaikan

| Ditemukan di | Scenario | Ringkasan masalah | Status perbaikan |
|---|---|---|---|
| §3 | S-01 | F-05: batch-confirm >1 sale.order crash `ValueError: Expected singleton` | ☐ Belum |
| §3 | S-03 | F-04: mekanisme dedup group fragile (mutasi state, bisa revert perubahan manual) | ☐ Belum |

---

## 7. Slot Metode Masa Depan

- `07C_QA_PLAYWRIGHT.md`/Tour headless — kandidat kalau `docker-env/Dockerfile` dengan Chrome
  (resep `USAGE_GUIDE.md` §Mode E) di-setup di sesi berikutnya, khususnya untuk verifikasi visual
  S-02 yang gagal di sesi ini.
