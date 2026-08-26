# Prompt Log — pos_margin_threshold / sale_margin_threshold / pin_message (18.0 → 19.0)

**Tujuan:** data empiris untuk `migration-tool/ai-doc/ROADMAP.md` §5 (Fase Otomasi Bertahap) —
mengukur seberapa sering user harus prompt untuk **flow normal** migrasi vs prompt **tool-fix**, per
step. Lihat `migration-tool/templates/PROMPT_LOG.md` untuk definisi klasifikasi lengkap.

**Cross-cutting, SATU FILE untuk ketiga modul** (sama seperti `FINDINGS.md` dan pola project
17.0→18.0 sebelumnya di repo ini) — bukan per-modul.

---

## Klasifikasi

- **Normal** — prompt yang menjalankan/melanjutkan salah satu dari 11 step, atau review/verifikasi
  konten migrasi.
- **Tool-fix** — prompt yang hasilnya perubahan ke `migration-tool/templates/`, `migration-tool/ai-doc/`,
  atau proses SOP itu sendiri.
- **Tidak dihitung** — orientasi murni, basa-basi non-actionable.
- Satu prompt user = satu unit hitung. Prompt yang menghasilkan KEDUA jenis dihitung sebagai
  **Tool-fix**.

## Log per Step

| Step | # Prompt Normal | # Prompt Tool-fix | Catatan |
|---|---|---|---|
| 0 — Bootstrap (sebelum step 1 resmi) | 1 | | Kickoff: "Lakukan migrasi 18 ke 19, branch target `migration/19.0_target`, source copy dari `migration/18.0`" — branch dibuat via Mode Git (dual-branch, bukan dual-clone, pola sama seperti project 17.0→18.0 di repo ini), `CLAUDE.md` + struktur `doc-dev/migration_18.0_19.0/doc/` diinstansiasi. |
| 1 — Intake & Baseline Spec | | | |
| 2 — Diff & Compatibility Analysis | | | |
| 3 — Migration Spec | | | |
| 4 — Spec Completeness Review | | | |
| 5 — Acceptance Criteria & Test Plan | | | |
| 6 — Code Migration (semua fase A-G2) | | | |
| 7 — Data Migration Scripts | | | — (N/A, port kode saja) |
| 8 — Code Review | | | |
| 9 — Dev Testing | | | |
| 10 — QA Testing | | | |
| 11 — UAT Sign-off | | | |
| **Total** | 1 | 0 | |

## Catatan Definisi

*(belum ada revisi kriteria)*

## Ringkasan Akhir Project (isi setelah step 11 selesai)

- Step dengan rasio Tool-fix tertinggi: ...
- Step yang paling "bersih": ...
- Tulis balik ringkasan project ini ke `migration-tool/ai-doc/ROADMAP.md` §5 begitu project ini selesai.
