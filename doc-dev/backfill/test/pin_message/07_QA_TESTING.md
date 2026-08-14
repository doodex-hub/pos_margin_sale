# QA Testing — pin_message

**Step:** 07 — QA Testing (backfill, TANPA UAT)
**Ref:** `doc-dev/backfill/spec/pin_message/01A_FUNCTIONAL_SPEC.md`, `01B_ACCEPTANCE_CRITERIA.md`, `test/pin_message/03B_TEST_PLAN.md`
**Tanggal:** 2026-07-31

---

## 1. Area yang Harus Dicakup

- [x] Toggle pin log note (Python, tereksekusi)
- [ ] Tidak ada duplikasi tombol pin discuss vs chatter (JS, desk-review saja)
- [ ] `onClickPin` discussion branch (F-06, desk-review saja)
- [ ] Section Pinned Messages (JS, desk-review saja)

---

## 2. Format Skenario

Sama seperti `doc-dev-backfill/templates/test/07_QA_TESTING.md` §2.

---

## 3. Skenario

### S-01: Toggle pin log note (Python)
**Precondition:** Partner dengan 1 log note.
**Mode eksekusi:** Mode C (Docker) — Unit test.
**Steps:** `message.toggle_pin()` dua kali berurutan.
**Expected:** `is_pinned` False→True→False, tanpa error, aman untuk multi-record.
**Actual:** Pass penuh (3 TC di `tests/test_pin_message.py`).
**Status:** ✅ Pass
**Provenance:** `[DIKONFIRMASI]`

### S-02: Verifikasi visual chatter (pin button, section Pinned Messages) — DESK-REVIEW
**Precondition:** Server Odoo G2 hidup, form Contact/Sale Order dibuka, ada beberapa log note.
**Mode eksekusi:** AI-in-the-loop browser — **DICOBA, GAGAL** (sama seperti modul lain di repo
ini — lihat detail lengkap di `test/sale_margin_threshold/07_QA_TESTING.md` S-02, root cause
identik: 2 mekanisme browser dicoba di sesi CLI ini, keduanya gagal sebelum sempat menyelesaikan
satu skenario).
**Expected:** Ikon pin muncul di tiap log note (bukan pesan discuss/notification); klik toggle
`is_pinned`; section "Pinned Messages" muncul di atas chatter dengan badge jumlah yang benar.
**Actual:** Tidak dieksekusi via browser.
**Status:** ⬜ Tidak dieksekusi (limitasi lingkungan)
**Provenance:** `[HASIL-BACA]`

### S-03: Tidak ada duplikasi action pin discuss vs chatter (F-06 terkait) — DESK-REVIEW KODE
**Precondition:** —
**Mode eksekusi:** Desk-review (baca source `pinMessage.js` vs
`odoo/addons/mail/static/src/discuss/message_pin/common/message_actions.js` core).
**Expected/Actual:** Kondisi registry key `"pins"` (modul ini, syarat `!is_discussion`) dan
`"pin"` (core, syarat `thread.model==='discuss.channel'`) SALING EKSKLUSIF — dikonfirmasi baca
kode langsung (bukan eksekusi), TIDAK ada overlap kondisi yang bisa membuat 2 tombol muncul
bersamaan.
**Status:** ✅ "Pass" desk-review (tinggi keyakinan, karena kondisinya sederhana & saling eksklusif
secara struktural — bukan runtime behavior yang butuh eksekusi untuk dipastikan)
**Provenance:** `[HASIL-BACA]`, tinggi keyakinan

---

## 4. Status Sub-file & Rekap Eksekusi

| File | Isi | Status | Dieksekusi? | Mode |
|---|---|---|---|---|
| §3 di file ini | Skenario umum | ✅ Selesai | Ya (S-01); S-02 gagal, S-03 desk-review kode | Mode C (Unit test) + AI-Browser (gagal) + desk-review |
| `07B_QA_AI_BROWSER.md` | — | N/A | Tidak dibuat | Sama alasan seperti 2 modul lain di repo ini |

**Keterbatasan eksekusi:** Modul ini PALING JS-heavy dari ketiga modul repo (mirip profil
`purchase_product_optional` di `ROADMAP.md` §3.1) — TAPI verifikasi visual browser gagal total
sesi ini. F-06/F-07 (temuan JS) TETAP `[HASIL-BACA]` murni, BUKAN `[DIKONFIRMASI]`, sampai ada
sesi mendatang dengan environment browser yang berfungsi (Tour/Mode E atau browser session baru).

---

## 5. Rekap Findings

| Tag | Jumlah |
|---|---|
| `[PERLU-KEPUTUSAN]` | 2 (F-06, F-07 — F-07 sebenarnya `[HASIL-BACA]` prioritas Rendah) |
| `[DIKONFIRMASI]` | S-01 (toggle_pin) |
| `[HASIL-BACA]` (tanpa masalah) | S-03 |

**Verdict:** Backfill selesai sampai Step 07. Tidak ada sign-off.

---

## 6. Bug / Perlu Perbaikan

| Ditemukan di | Scenario | Ringkasan masalah | Status perbaikan |
|---|---|---|---|
| Step 01 (baca kode) | — | F-06: `onClickPin` override total core, risiko silent-drift | ☐ Belum |
| Step 01 (baca kode) | — | F-07: `console.log` debug tertinggal | ☐ Belum |

---

## 7. Slot Metode Masa Depan

- Tour headless (Mode E) ATAU sesi browser baru — untuk verifikasi visual S-02 dan konfirmasi
  final F-06/F-07 yang saat ini masih murni `[HASIL-BACA]`.
