# QA Testing — pos_margin_threshold

**Step:** 07 — QA Testing (backfill, TANPA UAT)
**Ref:** `doc-dev/backfill/spec/pos_margin_threshold/01A_FUNCTIONAL_SPEC.md`, `01B_ACCEPTANCE_CRITERIA.md`, `test/pos_margin_threshold/03B_TEST_PLAN.md`
**Tanggal:** 2026-07-31

---

## 1. Area yang Harus Dicakup

- [x] Margin per-variant tidak bisa divergen (F-01, revisi)
- [x] Blocking transaction POS (popup Error/Confirm saat bayar)
- [x] Wizard assign margin massal
- [x] Koeksistensi model wizard dengan `sale_margin_threshold` (F-03)

Tidak ada kasus "lebih dari satu dialog/wizard dari satu aksi" di modul ini (cek wajib
`USAGE_GUIDE.md` §"Skenario wajib Step 07") — `Order.pay()` hanya menampilkan SATU popup
(`ErrorPopup` ATAU `ConfirmPopup`, mutually exclusive berdasar setting), tidak pernah dua sekaligus.

---

## 2. Format Skenario

Sama seperti `doc-dev-backfill/templates/test/07_QA_TESTING.md` §2.

---

## 3. Skenario

### S-01: Margin tidak bisa divergen antar variant (F-01)
**Precondition:** Template dengan 2 variant.
**Mode eksekusi:** Mode C (Docker) — Unit test.
**Steps:** Set `variant_a.margin_sale=20`, cek `variant_b`; lalu set `variant_b.margin_sale=50`,
cek `variant_a`.
**Expected:** Kedua variant SELALU sama (inverse menulis ke template shared).
**Actual:** Terkonfirmasi — `variant_a.margin_sale=50.0 variant_b.margin_sale=50.0
template.margin_sale=50.0` di akhir test.
**Status:** ✅ Pass
**Provenance:** `[PERLU-KEPUTUSAN]` — lihat F-01 (direvisi total dari hipotesis awal).

### S-02: Blocking transaction POS — DESK-REVIEW (keterbatasan browser, lihat §4)
**Precondition:** Server Odoo G2 hidup, POS session dibuka, produk di bawah harga minimum di
order.
**Mode eksekusi:** AI-in-the-loop browser — **DICOBA, GAGAL** (detail identik dengan
`test/sale_margin_threshold/07_QA_TESTING.md` S-02 — sesi browser berhenti merespons klik/keyboard
setelah beberapa langkah navigasi awal, pada kedua mekanisme browser yang dicoba).
**Expected:** `blocking_transaction_pos=True` → `ErrorPopup`, pembayaran diblokir total.
`blocking_transaction_pos=False` → `ConfirmPopup`, user bisa lanjut/batal.
**Actual:** Tidak dieksekusi via browser. Logic ini (`static/src/store/models/models.js:54-79`)
sudah dibaca detail di Step 01 (`BR-04`) — desk-review kode JS, BUKAN test otomatis (POS frontend
JS tidak ada di scope `TransactionCase` Python, dan QUnit/Hoot tidak di-setup sesi ini).
**Status:** ⬜ Tidak dieksekusi (limitasi lingkungan)
**Provenance:** `[HASIL-BACA]`

### S-03: Wizard assign margin massal
**Precondition:** 3 produk template di kategori.
**Mode eksekusi:** Mode C (Docker) — Unit test.
**Steps:** Buka wizard dari context `active_model=product.template`, isi margin, klik Assign.
**Expected:** Ketiga produk ter-update.
**Actual:** Pass (`tests/test_margin_sale.py::test_wizard_assign_margin_from_template_list`).
**Status:** ✅ Pass
**Provenance:** `[DIKONFIRMASI]`

### S-04: Koeksistensi model wizard 2 modul (F-03)
**Precondition:** Kedua modul terinstall.
**Mode eksekusi:** Mode C (Docker) — Unit test + introspeksi `__mro__`.
**Expected:** `create()` sukses; perlu cek kelas mana yang benar-benar aktif.
**Actual:** `create()` sukses, TAPI `__mro__` HANYA berisi kelas `sale_margin_threshold` — kelas
modul ini hilang total dari class yang benar-benar jalan.
**Status:** ✅ Pass (test) — tapi hasilnya sendiri adalah **temuan** (F-03, lihat `FINDINGS.md`)
**Provenance:** `[PERLU-KEPUTUSAN]`

---

## 4. Status Sub-file & Rekap Eksekusi

| File | Isi | Status | Dieksekusi? | Mode |
|---|---|---|---|---|
| §3 di file ini | Skenario umum | ✅ Selesai | Ya (S-01, S-03, S-04); S-02 gagal | Mode C (Unit test) + AI-Browser (gagal) |
| `07B_QA_AI_BROWSER.md` | — | N/A | Tidak dibuat | Sama seperti `sale_margin_threshold/07_QA_TESTING.md` §4 — 2 mekanisme browser dicoba, keduanya gagal sebelum menghasilkan satu skenario lengkap |

**Keterbatasan eksekusi:** S-02 (popup blocking POS) murni JS/OWL — TIDAK ada padanan Python-level
untuk membuktikan seperti F-05 (yang bisa "disamakan" ke Unit test karena action_confirm murni
Python). Tetap `[HASIL-BACA]`, kandidat kuat untuk Tour/QUnit di sesi mendatang.

---

## 5. Rekap Findings

| Tag | Jumlah |
|---|---|
| `[PERLU-KEPUTUSAN]` | 3 (F-01, F-02, F-03 — semua terkait/melibatkan modul ini) |
| `[DIKONFIRMASI]` | beberapa AC dasar |
| `[HASIL-BACA]` (tanpa masalah) | sisanya (termasuk S-02, murni belum tereksekusi) |

**Verdict:** Backfill selesai sampai Step 07. Tidak ada sign-off.

---

## 6. Bug / Perlu Perbaikan

| Ditemukan di | Scenario | Ringkasan masalah | Status perbaikan |
|---|---|---|---|
| §3 | S-01 | F-01: margin_sale tidak bisa berbeda antar variant walau field terlihat per-variant | ☐ Belum |
| §3 | S-04 | F-03: kelas modul ini hilang dari `__mro__` saat 2 modul terinstall | ☐ Belum |

---

## 7. Slot Metode Masa Depan

- Tour headless (Mode E) untuk S-02 — sama seperti dicatat di `sale_margin_threshold/07_QA_TESTING.md` §7.
