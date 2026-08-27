# Test Plan (Migrasi) — pin_message

**Step:** 5 — Acceptance Criteria & Test Plan
**Ref:** `05_acceptance/pin_message/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-08-26

---

## Step 9 — Dev Testing

Test existing: `tests/test_pin_message.py` (server-side `toggle_pin`), `tests/test_pin_message_tour.py`
+ `static/tests/tours/pin_message_tour.js` (2 tour: toggle pin inline, action-menu pin visible).
**Kedua tour SANGAT PENTING untuk project ini** — `pin_message_action_menu_pin_visible_tour`
SPESIFIK dibuat di project 17→18 untuk membuktikan fix `MF-24` (pendahulu konseptual `MF-15` di
project ini). Tour ini HARUS dijalankan ulang segera setelah `DIFF-01`/`DIFF-02` diporting, dan
diperkirakan akan GAGAL/crash browser kalau dijalankan SEBELUM fix (bukti langsung blocker).

| AC | Deskripsi | Unit | Integration | Tour (Owl/JS) |
|---|---|---|---|---|
| AC-01-01 | `toggle_pin()` server-side, multi-record | `test_pin_message.py` | — | — |
| AC-02-01/02/03 | Action-menu "Pin" muncul + berfungsi | — | — | `pin_message_tour.js` — `pin_message_action_menu_pin_visible_tour` (existing, WAJIB re-run pasca `DIFF-02`) |
| AC-03-01 | Tombol pin inline | — | — | `pin_message_tour.js` — `pin_message_toggle_pin_tour` (existing) |
| AC-04-01 | Section Pinned Messages | — | — | Tercakup implisit di kedua tour di atas |
| AC-04-02 | `_to_store()` tidak error untuk pesan apapun | — | *(belum ada test spesifik "chatter generic tidak crash" — WAJIB ditambah di Step 9 sebagai regression test eksplisit untuk `DIFF-01`, bukan cuma diasumsikan dari tour pin yang PASS)* | — |
| AC-05-01 | Discuss-channel native pin, dead code aman | — | *(belum ada — gap terbuka sejak 17→18, jalur Discuss channel belum pernah punya Tour test sendiri)* | — |
| AC-06-01 | Reload round-trip | — | *(dikonfirmasi Step 10 project 17→18 via interaksi manual, belum ada test otomatis)* | — |

**Tambahan WAJIB Step 9 project ini:** buat/perluas test yang secara eksplisit memuat chatter untuk
model APAPUN (bukan cuma model yang biasa dipakai tour pin) dan mengonfirmasi tidak ada `TypeError`
dari `_to_store()` — ini satu-satunya cara membuktikan fix `MF-14` benar-benar menutup blast radius
penuhnya (tour pin yang PASS saja tidak cukup untuk membuktikan chatter model LAIN juga aman).

## Step 10 — QA Testing

| AC | Deskripsi | Manual | AI-interaktif | AI+tool eksternal |
|---|---|---|---|---|
| AC-05-01 | Discuss-channel native pin/unpin | — | ✅ (pola sama seperti Step 10 project 17→18 — verifikasi interaktif pertama untuk jalur ini) | — |
| AC-06-01 | Reload round-trip A→B→A | — | ✅ | — |
| AC-02-01/02, AC-04-02 | Sanity check tambahan: buka BEBERAPA chatter berbeda (partner, produk, dst — bukan cuma yang biasa dites) di browser nyata | — | ✅ (verifikasi tambahan blast radius `MF-14`, di luar cakupan tour otomatis) | — |

## Step 11 — UAT

| Kelompok fitur | AC tercakup | UAT |
|---|---|---|
| Pin/unpin pesan | AC-01-01, AC-02-01/02/03, AC-03-01, AC-04-01 | Skenario: tulis log note, pin lewat tombol ATAU menu titik tiga, lihat muncul di "Pinned Messages", unpin |
| Chatter umum tidak rusak | AC-04-02 | Skenario sanity check: buka chatter di halaman APAPUN (partner, invoice, dst), pastikan tetap normal |

## Ringkasan

| Step | Role | Tipe | Eksekusi | Jumlah AC |
|---|---|---|---|---|
| 9 | Developer | Unit/Integration/Tour (Owl/JS) | Otomatis/background, WAJIB re-run + WAJIB tambah test baru untuk `AC-04-02` | 5 dari 10 AC punya test existing, 1 AC butuh test baru |
| 10 | QA | AI-interaktif | Termasuk sanity-check blast-radius tambahan yang di luar cakupan tour biasa | 3 area |
| 11 | PM/FA/User | UAT | Manual (selalu), termasuk sanity check chatter umum | 2 kelompok fitur |
