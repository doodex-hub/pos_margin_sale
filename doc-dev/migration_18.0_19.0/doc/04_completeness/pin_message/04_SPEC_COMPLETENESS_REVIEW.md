# Spec Completeness Review — pin_message

**Step:** 4 — Spec Completeness Review (gate)
**Ref:** `03_spec/pin_message/03_MIGRATION_SPEC.md`, source module `pin_message`
**Tanggal:** 2026-08-26

---

## Tabel Cakupan

| Elemen source module | Ada di Migration Spec? | Status | Catatan |
|---|---|---|---|
| `models/mail_message.py` (`is_pinned`, `toggle_pin`, `_to_store`) | Ya — §2 tabel (`DIFF-01`), §2b Critical Blockers #2, Kompatibilitas Data Model | ✅ Covered | Perbaikan WAJIB (signature `_to_store`), prioritas tertinggi project |
| `controllers/` | N/A — modul ini tidak punya folder `controllers/` sama sekali | ✅ Covered (N/A) | — |
| `views/*.xml` (`ir.ui.view`) | N/A — modul ini tidak punya folder `views/` sama sekali, `data: []` di manifest | ✅ Covered (N/A) | Semua UI lewat Owl QWeb (`static/src/xml/`), bukan `ir.ui.view` |
| `security/` | N/A — tidak ada file security, memakai access rule native `mail.message` yang sudah ada | ✅ Covered (N/A) | Dikonfirmasi sejak Step 1 (`01a_MIGRATION_INTAKE.md`) |
| `data/` | N/A — tidak ada folder `data/` | ✅ Covered (N/A) | — |
| `report/` | N/A — tidak ada folder `report/` | ✅ Covered (N/A) | — |
| `wizard/` | N/A — tidak ada folder `wizard/` | ✅ Covered (N/A) | — |
| `static/src/css/style.css` | Tidak disebut eksplisit (murni kosmetik, tidak ada logic) | ✅ Covered (implisit) | Tidak ada dependency ke API Odoo apapun |
| `static/src/js/chatter.js` | Ya — §2 tabel (`DIFF-03`) | ✅ Covered | Tidak ada perubahan |
| `static/src/js/message.js` | Ya — §2 tabel (`DIFF-04`, `DIFF-05`) | ✅ Covered | Tidak ada perubahan wajib, `MF-09` tetap dead code aman |
| `static/src/js/pinMessage.js` | Ya — §2 tabel (`DIFF-02`), §2b Critical Blockers #3 | ✅ Covered | Perbaikan WAJIB (rewrite `messageActionsRegistry`), prioritas tertinggi project |
| `static/src/xml/pinnedMessages.xml` | Ya — §2 tabel (`DIFF-06`) | ✅ Covered | Tidak ada perubahan |
| `static/src/xml/message_card_list.xml` | Ya — §2 tabel (`DIFF-07`) | ✅ Covered | Tidak ada perubahan |
| `static/tests/tours/pin_message_tour.js` + `tests/test_pin_message_tour.py`, `tests/test_pin_message.py` | Tidak disebut eksplisit di spec | ✅ Covered (implisit) | Test existing jadi validator Step 6/9 — WAJIB dijalankan ulang setelah `DIFF-01`/`DIFF-02` diporting, kemungkinan besar akan gagal SEBELUM fix diterapkan (bukti langsung blocker) |
| `__manifest__.py` | Ya — §2 tabel, §2b Critical Blockers #1 | ✅ Covered | Bump version |

## Verdict

- [x] ✅ **Lulus** — semua elemen Covered, lanjut ke step 5.

**Catatan:** modul ini paling sederhana secara STRUKTUR (jumlah file paling sedikit, tidak ada
views/security/wizard/data/report/controllers) tapi berisiko PALING TINGGI secara FUNGSIONAL
(`DIFF-01`/`DIFF-02`, dua blocker install/runtime dengan blast radius melampaui modul sendiri).
Tidak ada elemen source yang terlewat dari spec — cakupan 100%, verdict lulus murni administratif;
risiko sesungguhnya ada di KEDALAMAN dua fix wajib itu, bukan di cakupan.
