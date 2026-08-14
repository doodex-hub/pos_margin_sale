# Test Plan — pin_message

**Module:** `pin_message`
**Ref:** `doc-dev/backfill/spec/pin_message/01B_ACCEPTANCE_CRITERIA.md`
**Taxonomy:** vocab Odoo intrinsik (`TransactionCase`/`HttpCase`/QUnit-Hoot/Tour)
**Dibuat oleh:** BACKFILL (Step 03B)
**Last Updated:** 2026-07-31

---

## Step 04 — Developer Testing (backfill)

| AC | Deskripsi singkat | Unit | Integration | API |
|---|---|---|---|---|
| AC-01-01 | toggle_pin True + bus notify | ✓ | | |
| AC-01-02 | toggle_pin False | ✓ | | |
| AC-02-01/02 | tidak ada duplikasi action pin (JS registry) | | ✓ (QUnit/Hoot, kondisional) | |
| AC-03-01 | onClickPin discussion branch identik core (F-06) | | ✓ (QUnit/Hoot, kondisional) | |
| AC-04-01/02 | pinned messages section load/refresh | | ✓ (QUnit/Hoot, kondisional) | |

**Ringkasan:** 2 AC → Unit Python (`TransactionCase`, `toggle_pin`). Sisanya murni JS/OWL
(action registry, component patch) — QUnit/Hoot BUTUH Chrome headless (Mode E, `USAGE_GUIDE.md`
§Mode E) yang belum pasti tersedia; kalau gagal setup, di-desk-review + dicatat sebagai limitasi
di `04A_DEV_TESTING.md`, JANGAN dipaksa lolos. API: N/A (tidak ada controller sama sekali di
modul ini).

---

## Step 07 — QA Testing

| AC | Deskripsi singkat | AI-interaktif (07 §3) | AI-Browser/Tour (07B) |
|---|---|---|---|
| AC-01-01/02 | toggle pin dari chatter UI | ✓ | ✓ |
| AC-02-01/02 | tidak ada tombol pin dobel | ✓ | ✓ |
| AC-04-01/02 | section pinned messages | ✓ | ✓ |

**Ringkasan:** Semua AC punya komponen UI — AI-Browser/Tour jadi verifikasi utama, bukan cuma
tambahan, karena modul ini JS-heavy (mirip profil `purchase_product_optional` di
`doc-dev-backfill/ai-doc/ROADMAP.md` §3.1).

---

## Ringkasan Keseluruhan

| Step | Tipe | Jumlah AC |
|---|---|---|
| 04 | Unit | 2 |
| 04 | Integration (QUnit/Hoot, kondisional) | 5 |
| 04 | API | N/A |
| 07 | AI-interaktif | 3 |
| 07 | AI-Browser/Tour | 3 |
