# Prompt Log — pos_margin_threshold / sale_margin_threshold / pin_message (19.0 → 20.0)

**Tujuan:** data empiris untuk `migration-tool/ai-doc/ROADMAP.md` §5 (Fase Otomasi) — mengukur
seberapa sering user harus prompt untuk flow normal migrasi vs prompt tool-fix, per step. Lihat
`migration-tool/templates/PROMPT_LOG.md` untuk definisi klasifikasi lengkap (Normal / Tool-fix /
Tidak dihitung).

**Cross-cutting, satu file untuk ketiga modul** (lihat CLAUDE.md §"Adaptasi multi-modul").

---

## Log per Step

| Step | # Prompt Normal | # Prompt Tool-fix | Catatan |
|---|---|---|---|
| 0 — Bootstrap (sebelum step 1 resmi) | 1 | 0 | Branch `migration/20.0` dibuat dari `migration/19.0`, `.claude/settings.json` diisi path referensi (`odoo20`, `enterprise20`, `enterprise19.0` sebagai native-source), `doc-dev/migration_19.0_20.0/doc/` dibuat, `CLAUDE.md` diinstansiasi dari template, `.claude/skills/` (odoo-guidelines/odoo-review/odoo-security/odoo-web-guidelines) dikonfirmasi terpasang. |
| 1 — Intake & Baseline Spec | 1 | 0 | Draft `01a_MIGRATION_INTAKE.md` + `01b_BASELINE_SPEC.md` ditulis untuk ketiga modul (3 agent paralel), cross-check ke baseline 18.0→19.0 + kode 19.0 aktual + native20/enterprise20. 4 finding baru (`MF-25`..`MF-28`, termasuk 1 kritis `MF-28` — `_to_store()` hilang di native 20.0) + koreksi mekanisme `MF-08` ditulis ke `FINDINGS.md`. Gate Step 1 BELUM ditutup — menunggu konfirmasi user atas asumsi carried-forward (sifat migrasi, source aktif dikembangkan, dependency OCA, dokumen pelengkap lain). |
| 2 — Diff & Compatibility Analysis | ? | ? | Belum di-backfill retroaktif (dikerjakan sesi sebelum compaction) — perlu sesi berikutnya mengisi dari transcript kalau data ini dibutuhkan untuk `ROADMAP.md` §5. |
| 3 — Migration Spec | ? | ? | Sama seperti di atas — belum di-backfill. |
| 4 — Spec Completeness Review | 1 | 1 | 1 prompt normal ("LANJUT step 4") memicu 3 agent riset paralel (satu per modul); 1 tool-fix diam-diam (bukan diminta user) — koreksi root cause `MF-36` (salah-diagnosis "100% native" sebelumnya, ternyata bug `pin_message` sendiri) ditemukan & diperbaiki sebagai bagian gate ini, bukan dari prompt tool-fix eksplisit user. |
| 5 — Acceptance Criteria & Test Plan | 1 | 0 | 1 prompt normal ("LANJUT step 4" yang lalu diikuti kelanjutan otomatis ke step 5 tanpa tanya ulang, sesuai prinsip "jalan terus") memicu 3 agent riset paralel (satu per modul), 87 AC total ditulis, tidak ada tool-fix. |
| 6 — Code Migration (semua fase A-G2) | | | |
| 7 — Data Migration Scripts | | | — (N/A, port kode saja) |
| 8 — Code Review | | | |
| 9 — Dev Testing | | | |
| 10 — QA Testing | | | |
| 11 — UAT Sign-off | | | |
| **Total** | 3+ | 1+ | Step 2/3 belum di-backfill (lihat catatan baris masing-masing) — total ini undercount sampai itu diisi. |

## Catatan Definisi

*(belum ada revisi kriteria di project ini)*

## Ringkasan Akhir Project (isi setelah step 11 selesai)

- Step dengan rasio Tool-fix tertinggi: ...
- Step yang paling "bersih": ...
- Tulis balik ringkasan project ini ke `migration-tool/ai-doc/ROADMAP.md` §5 begitu project ini
  selesai.
