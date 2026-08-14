# Dev Testing — pin_message

**Step:** 04 — Developer Testing (backfill)
**Module:** `pin_message`
**Spec ref:** `doc-dev/backfill/spec/pin_message/01A_FUNCTIONAL_SPEC.md`
**Last Updated:** 2026-07-31

---

## 0. Environment eksekusi

**Mode C** (Claude Code CLI) — sama instance Docker gabungan 3-modul, lihat detail run lengkap di
`test/sale_margin_threshold/04A_DEV_TESTING.md` §0 (3 iterasi, hasil final `0 failed, 0 error(s) of
17 tests`). Modul ini TIDAK menyumbang FAIL/ERROR di iterasi manapun — 3 test Python-nya Pass
sejak run pertama.

**Limitasi eksplisit:** fitur inti modul ini JS/OWL-heavy (action registry, component patch,
section pinned messages) — TIDAK ada QUnit/Hoot yang dijalankan sesi ini (butuh Chrome headless,
Mode E, `docker-env/Dockerfile` tambahan — tidak di-setup karena fokus Step 04 diarahkan ke bug
Python berisiko tinggi dulu, F-05 di `sale_margin_threshold`). F-06/F-07 (temuan JS) TETAP
`[HASIL-BACA]`, belum diverifikasi eksekusi — kandidat Step 07 kalau Claude in Chrome/browser
tersedia untuk verifikasi visual sebagai gantinya.

---

## 1. Smoke Test

| # | Area/fitur | Happy path / edge case | Cara | Status |
|---|---|---|---|---|
| 1 | Toggle pin log note | `is_pinned` False→True→False | Mode C (Docker) | ✅ Pass |

---

## 2. Unit & Integration Test Specification

### 2a. Model — `mail.message.toggle_pin`

| # | Tipe | Condition | Expected | Actual | Provenance |
|---|---|---|---|---|---|
| TC-M-01 | Unit | toggle_pin pada pesan belum pinned | `is_pinned=True` | ✅ Pass | `[DIKONFIRMASI]` |
| TC-M-02 | Unit | toggle_pin pada pesan sudah pinned | `is_pinned=False` | ✅ Pass | `[DIKONFIRMASI]` |
| TC-M-03 | Unit | toggle_pin pada recordset 2 pesan sekaligus | keduanya ter-toggle benar (loop `for message in self`, aman) | ✅ Pass — kontras positif dengan bug F-05 (`sale_margin_threshold`) yang TIDAK loop | `[DIKONFIRMASI]` |

### 2b. JS/OWL (action registry, component patch) — TIDAK DIEKSEKUSI sesi ini

| # | Tipe | Condition | Expected | Status |
|---|---|---|---|---|
| TC-J-01 | Integration (QUnit/Hoot) | Action `"pins"` vs `"pin"` core tidak tumpang tindih | Sesuai AC-02-01/02 | ⬜ Desk-review saja (`[HASIL-BACA]`) |
| TC-J-02 | Integration (QUnit/Hoot) | `onClickPin` discussion branch identik core (F-06) | Sesuai AC-03-01 | ⬜ Desk-review saja (`[HASIL-BACA]`), dikonfirmasi via baca source, bukan eksekusi |

### 2c. Test Matrix Summary

| Area | Unit | Integration | Provenance |
|---|---|---|---|
| toggle_pin (Python) | ✓ (3 TC) | | `[DIKONFIRMASI]` |
| Action registry/component JS | | ⬜ belum (QUnit/Hoot) | `[HASIL-BACA]` |

### 2d. Ringkasan

- Unit: 3 TC — semua Pass. Total modul ini: 3 test case dari total 17 (gabungan repo).
- Integration JS: 0 dijalankan — dicatat sebagai limitasi eksplisit, BUKAN disamarkan "sudah
  dites". Kandidat Step 07 (AI-Browser/Tour) untuk verifikasi visual F-06/F-07 sebagai gantinya.

### 2e. Override/Collision Check terhadap Odoo Core (WAJIB)

| # | Method | Model/Component | Kelas/patch yang mendefinisikan | Override total Odoo core? | Provenance |
|---|---|---|---|---|---|
| 01 | `toggle_pin` | `mail.message` | Nama custom Python, tidak ada di core | ☑ Tidak (nama unik) | `[HASIL-BACA]` |
| 02 | **`onClickPin`** | `Message` (OWL component, JS) | Core (`discuss/message_pin/message_patch.js`) mem-patch method ini; modul ini JUGA mem-patch method sama TANPA `super.onClickPin()` | ☑ **Ya — override total di level JS**, TAPI dikonfirmasi baca source (bukan eksekusi QUnit) perilaku SAAT INI identik/benign | `[PERLU-KEPUTUSAN]` — F-06, belum diverifikasi via eksekusi QUnit/Hoot |
