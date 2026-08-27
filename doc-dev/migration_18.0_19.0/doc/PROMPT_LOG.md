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
| 1 — Intake & Baseline Spec | 5 | | "LANJUT" -> draft `01a`/`01b` ketiga modul + FINDINGS.md (MF-01..MF-11) -> dev jawab §0 bertahap (native-target/enterprise = `enterprise19.0` gabungan; native-source = `odoo18`; third-party = tidak ada) -> `.claude/settings.json` final -> **gate Step 1 LULUS ketiga modul (2026-08-26)**. |
| 2 — Diff & Compatibility Analysis | 1 | | Otomatis lanjut setelah gate Step 1 (prinsip "jalan terus") — 3 agent riset paralel cross-check `odoo18` vs `enterprise19.0` per modul. Hasil: 4 gap kritis baru (`MF-12`..`MF-15`), 2 di antaranya (`pin_message`) blast radius melampaui modul sendiri. `sale_margin_threshold` tidak ada blocker baru. |
| 3 — Migration Spec | 1 | | "LANJUT" — ditulis langsung dari temuan Step 2 (tanpa agent riset baru), 03_MIGRATION_SPEC.md ketiga modul. |
| 4 — Spec Completeness Review | 1 | | "LANJUT" — enumerasi tabel cakupan ketiga modul + verifikasi tambahan 7 view inherit_id target (belum dicek Step 2) langsung ke enterprise19.0. Semua stabil, gate lulus ketiganya. |
| 5 — Acceptance Criteria & Test Plan | 1 | | "LANJUT" — AC diturunkan dari BSL-NNN baseline spec (bukan migration spec), 05a+05b ketiga modul. pin_message dapat 1 requirement test baru (regression _to_store generik). |
| 6 — Code Migration (semua fase A-G2) | 4 | | "baik, lakukan" -> kode Fase A1-A5/B1/C1/E ketiga modul -> "buat saja, kamu jalankan docker" -> G1 install-test 3x percobaan (2 fix `sale_margin_threshold`: `groups_id`->`group_ids`, `users`->`user_ids`) -> G1 PASS -> G2 test-enable+Tour test (2 fix kritis: `pin_message` infinite recursion `Store.add()`, `pos_margin_threshold` test-tour util path) -> **G1+G2 PASS ketiga modul, 0 failed/0 error dari 22 test**. |
| 7 — Data Migration Scripts | | | — (N/A, port kode saja) |
| 8 — Code Review | | | |
| 9 — Dev Testing | | | |
| 10 — QA Testing | | | |
| 11 — UAT Sign-off | | | |
| **Total** | 14 | 0 | |

## Catatan Definisi

*(belum ada revisi kriteria)*

## Ringkasan Akhir Project (isi setelah step 11 selesai)

- Step dengan rasio Tool-fix tertinggi: ...
- Step yang paling "bersih": ...
- Tulis balik ringkasan project ini ke `migration-tool/ai-doc/ROADMAP.md` §5 begitu project ini selesai.
