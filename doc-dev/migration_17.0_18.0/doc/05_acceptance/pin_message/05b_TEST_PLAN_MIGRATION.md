# Test Plan (Migrasi) — pin_message

**Step:** 5 — Acceptance Criteria & Test Plan
**Ref:** `05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-08-24

---

## Step 9 — Dev Testing

> Fase E (JavaScript) applicable, Fase F (Template) applicable — modul ini py komponen Owl + template `t-inherit`. **Tour test WAJIB untuk AC-02/AC-03** (risiko tertinggi project ini, tidak bisa dibuktikan lewat unit test Python backend saja — `messagePinService` cuma dipanggil dari klik browser nyata).

| AC | Deskripsi | Unit | Integration | Tour (Owl/JS) |
|---|---|---|---|---|
| AC-01-01..02 | Toggle pin log note | `tests/test_pin_message.py` (ada, cek dulu isinya genuinely test RPC atau cuma model-level) | Bisa via `TransactionCase` (panggil `toggle_pin()` langsung) | Opsional (cukup Integration) |
| AC-02-01..02 | Tidak ada duplikasi tombol | — | — | **WAJIB baru** — kondisi `is_discussion` cuma bisa diverifikasi lewat render UI nyata |
| AC-03-01 | Pin pesan Discuss (risiko `messagePinService`) | — | — | **WAJIB baru, PRIORITAS TERTINGGI** — satu-satunya cara menangkap `DIFF-06` sebelum production |
| AC-04-01..02 | Section Pinned Messages | — | — | **WAJIB baru** — render chatter + navigasi antar record |
| AC-05-01 | Entry point kedua (tombol inline) | — | — | Bisa digabung ke tour AC-01 |

## Step 10 — QA Testing

| AC | Deskripsi | Manual | AI-interaktif | AI+tool eksternal |
|---|---|---|---|---|
| AC-03-01 | Pin Discuss channel | Manual, WAJIB dicoba manual minimal sekali walau ada tour — ini risiko tertinggi | Kalau tour Step 9 belum lengkap | — |
| AC-01/02/04/05 | Sisanya | — (cukup dari tour Step 9) | Kalau tour belum lengkap saat QA jalan | — |

## Step 11 — UAT

| Kelompok fitur | AC tercakup | UAT |
|---|---|---|
| Pin/unpin log note | AC-01, AC-05 | Manual |
| Pin pesan Discuss | AC-03 | Manual — **PENTING**, minta user benar-benar coba di percakapan Discuss sungguhan |
| Section Pinned Messages | AC-04 | Manual |

## Ringkasan

| Step | Role | Tipe | Eksekusi | Jumlah AC |
|---|---|---|---|---|
| 9 | Developer | Unit/Integration/Tour | **3 tour test baru wajib ditulis** (AC-02, AC-03, AC-04) | 8 |
| 10 | QA | Manual | Fokus AC-03 (risiko tertinggi) | 8 |
| 11 | PM/FA/User | UAT | Manual | 3 kelompok |
