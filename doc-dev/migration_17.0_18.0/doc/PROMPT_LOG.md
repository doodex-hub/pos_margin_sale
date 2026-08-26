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
| 9 — Dev Testing (lanjutan, fix `MF-21`) | sale_margin_threshold | 1 | 0 | Prompt ("fr bisa terinstall bisa tidak, sehingga tidak boleh mensyaratkan harus ada fr, kenapa membutuhkan fr, solusi bagaimana") — user menolak solusi "konfirmasi Prancis terinstall di production" yang direkomendasikan sejak Step 6, minta fix kode. Ditemukan cabang blocking (`sale_order.py:33-37`) sudah menyelesaikan masalah sama tanpa translated-field; pola sama diterapkan ke cabang wizard, hapus `.with_context(lang='fr_FR')` total. Re-verifikasi: `0 failed, 0 error(s) of 22 tests` TANPA bahasa Prancis terinstall sama sekali. `MF-21` RESOLVED, direklasifikasi dari `[CATATAN-DEPLOYMENT]` ke `[GAP-MIGRASI]` (selesai). Tidak ada tool-fix |
| 10 — QA Testing (gate) | pos_margin_threshold, sale_margin_threshold, pin_message | 1 | 0 | Prompt ("lanjuit") — QA interaktif via Claude in Chrome (Chrome asli, tidak kena limitasi Service Worker Browser pane bawaan) terhadap instance live G2-mode (`docker compose run` one-off). Menutup gap yang sebelumnya cuma "dikonfirmasi baca kode": wizard assign margin `pos_margin_threshold` (assign+cancel), dedup field label `sale_margin_threshold` (inspeksi DOM), Discuss-channel native pin/unpin `pin_message` (verifikasi interaktif pertama untuk `MF-09` — sebelumnya cuma baca source) + reload ganti record. Ketiga modul lulus gate. Menulis `10_BUSINESS_FLOW_MIGRATION.md` + folder `human_qa/` (4 file per modul) per template. Tidak ada tool-fix |
| 11 — UAT Sign-off | pos_margin_threshold, sale_margin_threshold, pin_message | 1 | 0 | Prompt ("lanjtu") — draft `11_UAT_CHECKLIST.md` per modul (bahasa awam, data dummy konkret, kolom Actual/Status/Sign-off sengaja dikosongkan sesuai template — UAT harus dijalankan tangan sendiri oleh user, bukan AI). Sambil menyiapkan draft, ditemukan+diperbaiki kesalahan pelabelan `AC-03-02` `pos_margin_threshold` dari Step 8-10 (yang dites sebelumnya adalah "klik Cancel", bukan AC-03-02 asli soal field `product_ids` vs `product_template_ids`) — diverifikasi ulang skenario yang benar via Chrome asli, dikonfirmasi Pass. Tidak ada tool-fix |
| 11 — UAT Sign-off (ditutup) | pos_margin_threshold, sale_margin_threshold, pin_message | 1 | 0 | Prompt ("UAT dianggap selesai, percaya AI test") — user eksplisit memutuskan menerima bukti Step 9/10 AI sebagai pengganti eksekusi tangan sendiri T-01 dst. Ketiga `11_UAT_CHECKLIST.md` diisi AI (Actual/Status/Sign-off) MENGUTIP sumber bukti Step 9/10 yang sudah ada — bukan klik ulang, bukan inisiatif sepihak, sesuai instruksi eksplisit. 1 langkah (`sale_margin_threshold` T-02.4, wizard Cancel) jujur ditandai belum ada bukti eksekusi apapun, bukan dipaksakan Pass. **Project migrasi 3 modul selesai, 11 step lulus semua.** Tidak ada tool-fix |
| 10 — QA Testing | | | | |
| 11 — UAT Sign-off | | | | |
| **Total** | | 13 | 0 | |

## Catatan Definisi

*(belum ada revisi kriteria)*

## Ringkasan Akhir Project (2026-08-26 — SELESAI, 13 prompt normal, 0 tool-fix)

- **Step dengan rasio Tool-fix tertinggi:** Tidak ada satupun — 0 tool-fix di seluruh project (13/13
  prompt normal). Semua temuan/perbaikan bersifat spesifik project ini, tidak ada yang jadi perubahan
  ke `migration-tool/templates`/`ai-doc` itu sendiri.
- **Step yang paling "bersih":** Step 1-5, 7 (N/A) — nol iterasi/koreksi. Step yang paling banyak
  iterasi/temuan real: Step 6 (Mode D, 7 percobaan sampai Tour test lolos, `MF-13..20`) dan Step 8
  (`MF-24`, bug nyata ditemukan+diperbaiki dalam review itu sendiri).
- **Lesson terbesar:** validasi lewat interaksi nyata (Tour test Odoo asli / Chrome asli) berulang
  kali menemukan breaking change yang TIDAK terdeteksi G1 (install test)/analisis statis/baca kode
  saja — pola berulang di ketiga modul (`MF-13..20` POS, `MF-22..24` pin_message). Kelas bug ini
  (Owl component API relocation, entry-point yang diam-diam tidak lagi terpanggil) hampir mustahil
  ketemu tanpa benar-benar mengeklik UI.
- **Penyimpangan proses yang perlu dicatat untuk ROADMAP:** Step 11 (UAT) ditutup atas keputusan
  eksplisit user yang menerima bukti Step 9/10 (AI) sebagai pengganti eksekusi tangan sendiri —
  bukan default proses, tapi valid sebagai keputusan pemilik project. Item yang genuinely tidak
  punya bukti eksekusi apapun (`sale_margin_threshold` T-02.4) tetap dicatat jujur, tidak dipaksakan
  Pass — pola ini (transparan soal apa yang benar-benar diverifikasi vs diasumsikan) layak jadi
  rekomendasi standar kalau situasi serupa terjadi lagi di project migrasi lain.
- Tulis balik ke `migration-tool/ai-doc/ROADMAP.md` §5 setelah project ini selesai — termasuk catatan
  baru soal axis "3-modul-1-repo", "dual-branch bukan dual-clone", dan "UAT ditutup via keputusan
  eksplisit stakeholder mengganti eksekusi tangan sendiri" untuk project migrasi berikutnya yang mirip.
