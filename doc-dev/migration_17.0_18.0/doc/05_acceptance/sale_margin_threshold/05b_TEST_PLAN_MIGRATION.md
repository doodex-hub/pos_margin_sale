# Test Plan (Migrasi) — sale_margin_threshold

**Step:** 5 — Acceptance Criteria & Test Plan
**Ref:** `05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-08-24

---

## Step 9 — Dev Testing

> Fase E/F **N/A** (tidak ada Owl/JS di modul ini) — semua test cukup Unit/Integration backend, tidak butuh tour.

| AC | Deskripsi | Unit | Integration | Tour |
|---|---|---|---|---|
| AC-01-01..04 | Validasi confirm single order | `tests/test_action_confirm.py` (ada) | — | N/A |
| AC-02-01 | Batch confirm crash (`MF-06`) | `tests/test_action_confirm.py::test_action_confirm_BATCH_MULTI_ORDER_F05` (ada) — **prioritas #1 re-run, konfirmasi crash identik** | — | N/A |
| AC-03-01..02 | Wizard konfirmasi | Bisa Unit (`TransactionCase`) | — | N/A |
| AC-04-01..03 | Cross-module | `tests/test_cross_module.py` (ada) — kedua modul terinstall bersama | — | N/A |

## Step 10 — QA Testing

| AC | Deskripsi | Manual | AI-interaktif | AI+tool eksternal |
|---|---|---|---|---|
| AC-01-01..02 | Blocking/wizard confirm (UI form) | Manual, verifikasi visual `views/sale_order.xml` (pasca fix `DIFF-01`) — decoration merah baris di bawah minimum benar-benar tampil | — | — |
| AC-02-01 | Batch confirm dari list view | Manual, coba klik "Confirm" batch beneran dari UI | — | — |

## Step 11 — UAT

| Kelompok fitur | AC tercakup | UAT |
|---|---|---|
| Validasi harga minimum saat confirm | AC-01-01..04 | Manual, sales user coba confirm quotation di bawah minimum |
| Batch confirm (dikonfirmasi tetap error, bukan fitur) | AC-02-01 | Manual — **PENTING dijelaskan ke UAT user bahwa ini bug existing yang disengaja dipertahankan**, bukan regresi migrasi |

## Ringkasan

| Step | Role | Tipe | Eksekusi | Jumlah AC |
|---|---|---|---|---|
| 9 | Developer | Unit/Integration | Otomatis, semua test sudah ada dari backfill, tinggal re-run | 10 |
| 10 | QA | Manual | Fokus verifikasi visual `views/sale_order.xml` pasca fix `DIFF-01` | 2 |
| 11 | PM/FA/User | UAT | Manual | 2 kelompok |
