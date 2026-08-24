# Prompt Log — pos-margin-sale (17.0 → 18.0, multi-module)

**Tujuan:** data empiris untuk `migration-tool/ai-doc/ROADMAP.md` Fase 5 (Otomasi Bertahap) —
mengukur seberapa sering user harus prompt untuk flow normal migrasi vs prompt tool-fix, per step.
Satu file untuk ketiga modul (`pos_margin_threshold`, `sale_margin_threshold`, `pin_message`) —
kolom modul ditambahkan di tabel supaya tetap bisa dipilah.

**Cross-cutting** — hidup di root `doc/`, bukan di satu folder step.

---

## Klasifikasi (WAJIB konsisten)

- **Normal** — prompt yang menjalankan/melanjutkan salah satu dari 11 step, atau review/verifikasi
  konten migrasi modul ini.
- **Tool-fix** — prompt yang hasilnya perubahan ke `migration-tool/templates/`, `migration-tool/ai-doc/`,
  atau proses SOP itu sendiri.
- **Tidak dihitung** — orientasi murni, basa-basi non-actionable.
- Satu prompt user = satu unit hitung. Kalau menghasilkan KEDUA jenis, hitung sebagai Tool-fix.

## Log per Step

| Step | Modul | # Prompt Normal | # Prompt Tool-fix | Catatan |
|---|---|---|---|---|
| 0 — Bootstrap | (semua) | 5 | 0 | Scope 3-modul + sifat migrasi + keputusan dual-branch (bukan dual-clone) + keputusan mengabaikan `origin/18.0` — semua lewat AskUserQuestion, tidak ada perubahan ke `migration-tool/templates` itu sendiri |
| 1 — Intake & Baseline Spec | pos_margin_threshold | 1 | 0 | Satu prompt ("lanjut") menghasilkan `01a_MIGRATION_INTAKE.md` + `01b_BASELINE_SPEC.md` draft lengkap + 4 finding (`MF-01..04`) ke `FINDINGS.md` — sebagian besar leverage dokumen backfill (`01A_FUNCTIONAL_SPEC.md`/`01B_ACCEPTANCE_CRITERIA.md`) yang sudah tervalidasi eksekusi, bukan ditulis dari nol |
| 2 — Diff & Compatibility Analysis | | | | |
| 3 — Migration Spec | | | | |
| 4 — Spec Completeness Review | | | | |
| 5 — Acceptance Criteria & Test Plan | | | | |
| 6 — Code Migration (semua fase A-G2) | | | | |
| 7 — Data Migration Scripts | | | | N/A — port kode saja |
| 8 — Code Review | | | | |
| 9 — Dev Testing | | | | |
| 10 — QA Testing | | | | |
| 11 — UAT Sign-off | | | | |
| **Total** | | 5 | 0 | |

## Catatan Definisi

*(belum ada revisi kriteria)*

## Ringkasan Akhir Project (isi setelah step 11 selesai, ketiga modul)

- Step dengan rasio Tool-fix tertinggi: ...
- Step yang paling "bersih": ...
- Tulis balik ke `migration-tool/ai-doc/ROADMAP.md` §5 setelah project ini selesai — termasuk catatan
  baru soal axis "3-modul-1-repo" dan "dual-branch bukan dual-clone" untuk project migrasi berikutnya
  yang mirip.
