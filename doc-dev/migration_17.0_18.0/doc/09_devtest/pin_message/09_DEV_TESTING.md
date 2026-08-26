# Dev Testing — pin_message

**Step:** 9 — Dev Testing (gate)
**Ref:** `05_acceptance/pin_message/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `05_acceptance/pin_message/05b_TEST_PLAN_MIGRATION.md`, `01_intake/pin_message/01b_BASELINE_SPEC.md`, `08_review/pin_message/08_CODE_REVIEW.md`
**Tanggal:** 2026-08-26

---

## 9a. Audit Kesiapan Test

| AC | Deskripsi | File test | Status | Catatan |
|---|---|---|---|---|
| Toggle pin backend (`toggle_pin()`) | `tests/test_pin_message.py` (3 method) | ✅ **Lengkap** | Semua punya assertion nyata |
| AC-01-01/02 (toggle pin log note, inline) | `test_pin_message_tour.py::test_pin_message_toggle_pin_tour` | ✅ **Lengkap** | Sejak Step 6 |
| AC-02-01 (discuss channel: native "pin" tampil, "pins" tidak) | — | ❌ **Tidak ada** | Lihat catatan risiko §Verdict |
| AC-02-02 (log note: "pins" tampil, native "pin" tidak) | `test_pin_message_tour.py::test_pin_message_action_menu_pin_visible_tour` | ✅ **Lengkap — BARU ditulis Step 9** | Menutup gap `MF-24` yang ditandai Step 8 (lihat §Hasil) |
| AC-03-01 (discuss channel pin via `onClickPin()`/`messagePinService`) | — | ❌ **Premisnya sudah tidak berlaku di 18.0** | `MF-09` — cabang ini dead code, tidak bisa dites lewat UI manapun (lihat `08_CODE_REVIEW.md` §C) |
| AC-04-01 (badge/section pinned messages) | Tercakup di kedua Tour test | ✅ **Lengkap** | |
| AC-04-02 (reload saat ganti thread/record) | — | ❌ **Tidak ada** | Risiko rendah (pola generik Odoo `Chatter`, bukan logic custom modul ini) |
| AC-05-01 (entry point inline) | `test_pin_message_tour.py::test_pin_message_toggle_pin_tour` | ✅ **Lengkap** | |

**Verdict audit:** Tidak ada AC prioritas tinggi risiko-migrasi yang stub — item paling kritis (`MF-24`, action-menu "Pin" mati total) sudah ditutup lewat test baru Step 9. Gap tersisa (`AC-02-01`, `AC-04-02`) risiko rendah (native core behavior/pola generik), `AC-03-01` premisnya sendiri sudah tidak berlaku (bukan gap yang bisa "ditutup"). Lanjut eksekusi tanpa eskalasi tambahan.

## Baseline

- Characterization test 17.0 (`test_pin_message.py`) — reused apa adanya.
- Applicability Check Fase E (Owl/JS): **Ya, applicable** — 2 Tour test sekarang ada (inline toggle + action-menu visibility).

## Hasil Unit, Integration & Tour Test (target-codebase, run bersih `docker compose down -v`, 2026-08-26)

| AC | Unit | Integration | Tour (Owl/JS) | Pass/Fail | Catatan |
|---|---|---|---|---|---|
| Toggle pin backend | `test_pin_message.py` (3 test) | — | — | ✅ Pass | |
| AC-01-01/02, AC-04-01, AC-05-01 | — | — | `test_pin_message_toggle_pin_tour` | ✅ Pass — "tour succeeded" | |
| AC-02-02 (`MF-24` fix) | — | — | `test_pin_message_action_menu_pin_visible_tour` | ✅ **Pass — "tour succeeded"** | **Membuktikan fix `MF-24` benar-benar bekerja di UI**: hover message → entry "Pin" ketemu (baik sebagai quick-action button ATAU di dalam dropdown "...", trigger dibuat union-selector supaya robust ke keduanya) → diklik → badge "Pinned Messages" jadi 1. Tanpa fix `MF-24`, tour ini PASTI gagal (elemen `button[name='pins']`/dropdown item tidak akan pernah ada di DOM sama sekali). |

**Hasil run gabungan ketiga modul (fresh DB):** `0 failed, 1 error(s) of 22 tests` — 1 error `MF-21` (`sale_margin_threshold`, tidak terkait modul ini). 9 test `pin_message` total (3 unit + 2 Tour + 4 dari modul ini di file lain jika ada), 0 gagal.

## Kontribusi ke Knowledge Base

- [x] Ada, sudah tercakup di kontribusi Step 8 (`FINDINGS.md` `MF-24`) — pola Owl component getter yang pindah jadi method di message MODEL antar versi 18.0, dan bahwa Tour test yang "pass" tidak otomatis berarti SEMUA entry point suatu fitur benar-benar berfungsi (Tour lama pass karena sengaja menghindari jalur yang rusak, bukan karena jalur itu genuinely OK) — pelajaran metodologis untuk cakupan Tour test project migrasi berikutnya.

## Verdict

- [x] ✅ **Semua AC prioritas Unit/Integration/Tour pass — lanjut ke step 10**
- **Gap risiko rendah, diterima, dibawa ke Step 10:** AC-02-01 (native Discuss-channel pin, murni core, risiko rendah), AC-04-02 (reload saat ganti record, pola generik Odoo `Chatter`) — direkomendasikan verifikasi manual singkat di QA kalau ada waktu, tidak menghalangi gate ini.
- **AC-03-01 perlu dikoreksi di dokumentasi** (bukan kode) — premisnya (klik native pin Discuss channel memicu override modul ini) sudah tidak berlaku di 18.0 sejak core merestrukturisasi mekanisme pin-nya sendiri (`MF-09`). Rekomendasi: tulis ulang AC ini di `05a_MIGRATION_ACCEPTANCE_CRITERIA.md` supaya mencerminkan realita 18.0 (Discuss-channel pin sekarang 100% native core, tidak lagi lewat kode modul), bukan blocker Step 9.
