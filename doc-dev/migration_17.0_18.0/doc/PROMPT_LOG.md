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
| 1 — Intake & Baseline Spec | sale_margin_threshold | 1 | 0 | Satu prompt ("comit saja dan lanjut") menghasilkan Step 1 lengkap modul ini + 4 finding baru (`MF-05..08`), termasuk 1 temuan `[PERLU-KEPUTUSAN]` prioritas Tinggi (`MF-06`, batch-confirm crash) |
| 1 — Intake & Baseline Spec | pin_message | 1 | 0 | Prompt ("kenapa harus berhenti, tidak lanjut saja") — feedback: lanjutkan tiap modul tanpa berhenti minta konfirmasi. Step 1 modul ini selesai + 2 finding (`MF-09..10`) dalam giliran yang sama tanpa jeda |
| 2 — Diff & Compatibility Analysis | pos_margin_threshold, sale_margin_threshold, pin_message | 1 | 0 | Satu prompt ("lanjut") menghasilkan Step 2 ketiga modul sekaligus (tanpa native-target — sebagian besar ditandai `[TIDAK TERVERIFIKASI]`) + 1 finding baru (`MF-11`). Temuan kritis: `sale_margin_threshold` DIFF-01 (`<tree>`→`<list>` install-blocking, high confidence dari knowledge base) |
| 3 — Migration Spec | pos_margin_threshold, sale_margin_threshold, pin_message | 1 | 0 | Sama prompt ("lanjut") lanjut tanpa jeda ke Step 3 ketiga modul — strategi per-file + Critical Migration Blockers + urutan testing, berdasar Step 1/2. Tidak ada tool-fix |
| 4 — Spec Completeness Review | pos_margin_threshold, sale_margin_threshold, pin_message | 1 | 0 | Prompt ("LANJUUT, kenapa sering berhenti...") — feedback: hanya berhenti di gate/keputusan asli. Step 4 menemukan gap nyata (folder `wizard/` hilang dari draft Step 3 di 2 modul), diperbaiki sebelum gate dinyatakan lulus |
| 5 — Acceptance Criteria & Test Plan | pos_margin_threshold, sale_margin_threshold, pin_message | 1 | 0 | Lanjut otomatis tanpa prompt baru (mengikuti feedback "jangan berhenti") — AC diturunkan dari BSL-NNN, test plan mengidentifikasi 4 tour test baru yang wajib ditulis (1 pos_margin_threshold, 3 pin_message) |
| 6 — Code Migration (semua fase A-G2) | pos_margin_threshold, sale_margin_threshold, pin_message | 1 | 0 | Prompt ("commit saja dulu" lalu "status apa?" lalu commit) — Fase A dikerjakan ketiganya + G1 Docker nyata (pass) + G2 browser nyata via Claude Browser tool + `docker exec` cross-check source 18.0. Menemukan & memperbaiki 3 breaking change nyata (MF-12/13/14) yang TIDAK mungkin ketemu dari analisis statis Step 2 saja — validasi kuat metodologi G1≠G2≠review statis |
| 6 — Code Migration, Mode D (Tour test) | pos_margin_threshold, sale_margin_threshold, pin_message | 1 | 0 | Prompt ("Ya, lanjut" ke setup Mode D) — pasang Chrome asli di Docker (`Dockerfile`), tulis Tour test `pos_margin_threshold`. Perjalanan 7 percobaan G1/Tour menemukan arsitektur data POS 18.0 berubah total (`MF-15..20`) yang TIDAK terdeteksi G1/browser-console sebelumnya — akhirnya "tour succeeded" penuh. Juga menemukan `MF-21` (validasi bahasa 18.0) dari `sale_margin_threshold`. Menulis `migration-records/pos-margin-sale_17.0_18.0/SUMMARY.md` (kandidat knowledge base baru). Tidak ada tool-fix ke `migration-tool/templates` itu sendiri (semua temuan spesifik project ini) |
| 6 — Code Migration, Mode D (Tour test `pin_message`) + doc catch-up | pin_message | 1 | 0 | Prompt ("Lanjutkan" setelah konfirmasi commit manual `SUMMARY.md`) — tulis Tour test `pin_message` (jalur log note, pin/unpin). Menemukan 2 finding kritis baru yang TIDAK terdeteksi G1/G2 statis sebelumnya (`MF-22`: `chatter.js load()` full-override butuh service yang sudah hilang; `MF-23`: field custom `is_pinned` butuh `mail.message._to_store()`, bukan lagi field-list JS) — pola sama seperti `_load_pos_data_fields` POS di `MF-18`. Juga root-cause regresi environment palsu di `pos_margin_threshold` (flag `--load-language=fr_FR` bocor jadi bahasa default sesi, bukan bug kode) via screenshot `docker cp`, diperbaiki permanen di `docker-compose.yml`. Hasil akhir gabungan: kedua Tour test (`pos_margin_threshold`, `pin_message`) "tour succeeded", 0 failed/1 error (19 test, 1 error = `MF-21` tidak terkait). Diikuti update dokumentasi (`FINDINGS.md`, kedua `06c_IMPLEMENTATION_LOG.md`, `CLAUDE.md` §Status). Tidak ada tool-fix ke `migration-tool/templates` |
| 2 — Diff & Compatibility Analysis | | | | |
| 3 — Migration Spec | | | | |
| 4 — Spec Completeness Review | | | | |
| 5 — Acceptance Criteria & Test Plan | | | | |
| 6 — Code Migration (semua fase A-G2) | | | | |
| 7 — Data Migration Scripts | | | | N/A — port kode saja |
| 8 — Code Review (gate) | pos_margin_threshold, sale_margin_threshold, pin_message | 1 | 0 | Prompt ("berhenti apa lagi?" — feedback: lanjut tanpa jeda ke Step 8) — 3 agent paralel gather diff+gap-analysis+core-collision-check per modul (git diff `backfill/17.0`→`HEAD`, cross-check langsung ke source real 17.0/18.0 di image `pos_margin_sale_migration_18-odoo:latest`), lalu sintesis manual jadi `08_CODE_REVIEW.md` per modul. Ketiga modul lulus gate. Menemukan+memperbaiki+memverifikasi 1 bug fungsional nyata yang lolos dari Tour test sebelumnya (`MF-24`, `pin_message` action-menu "Pin" silently dead karena `canAddReaction` getter→method di 18.0) — re-run test suite penuh mengonfirmasi tidak ada regresi. Juga mengonfirmasi `MF-09` (Discuss-channel `onClickPin`) harmless via cross-check source langsung, bukan lagi `[PERLU-KEPUTUSAN]` terbuka. Tidak ada tool-fix ke `migration-tool/templates` |
| 9 — Dev Testing (gate) | pos_margin_threshold, sale_margin_threshold, pin_message | 2 | 0 | Prompt ("apa status disisni" lalu "LANJUT") — audit stub test `ast`-based (semua test lama terkonfirmasi real, tidak ada stub), tulis 3 test baru menutup gap Step 8 (`pos_margin_threshold` Tour blocking path, `pin_message` Tour action-menu visibility untuk verifikasi `MF-24` end-to-end di UI, `sale_margin_threshold` test MRO sisi modul sendiri), lalu re-run test suite penuh (fresh DB) — 0 regresi, `0 failed, 1 error(s) of 22 tests`. Temuan tambahan: dites empiris MRO `wizard.margin.product` di DUA urutan install (`docker compose run` one-off) — premis asli `MF-03`/AC-04-02 ("tergantung urutan install") TERBUKTI SALAH, `sale_margin_threshold` selalu menang independen urutan; `05a_MIGRATION_ACCEPTANCE_CRITERIA.md` (2 modul) dikoreksi. Ketiga modul lulus gate. Tidak ada tool-fix |
| 10 — QA Testing | | | | |
| 11 — UAT Sign-off | | | | |
| **Total** | | 9 | 0 | |

## Catatan Definisi

*(belum ada revisi kriteria)*

## Ringkasan Akhir Project (isi setelah step 11 selesai, ketiga modul)

- Step dengan rasio Tool-fix tertinggi: ...
- Step yang paling "bersih": ...
- Tulis balik ke `migration-tool/ai-doc/ROADMAP.md` §5 setelah project ini selesai — termasuk catatan
  baru soal axis "3-modul-1-repo" dan "dual-branch bukan dual-clone" untuk project migrasi berikutnya
  yang mirip.
