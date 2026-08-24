# CLAUDE.md — pos-margin-sale migration (17.0 → 18.0, multi-module)

> Diinstansiasi dari `migration-tool/templates/CLAUDE_TEMPLATE.md` pada 2026-08-24.
> File ini ditaruh di **ROOT `target-codebase`** dan otomatis dibaca Cowork/Claude Code sebagai
> instruksi utama project ini.
> Semua path `doc/...` yang disebut di file ini relatif terhadap
> `doc-dev/migration_17.0_18.0/doc/` — bukan relatif ke root `target-codebase` langsung.
>
> **Kasus baru, belum ada precedent di `migration-tool`:** repo ini berisi TIGA addon Odoo
> independen (`pos_margin_threshold`, `sale_margin_threshold`, `pin_message`), bukan satu modul
> seperti semua instans migration-tool sebelumnya (`purchase_product_optional`,
> `crm_probability_from_stage`, `advanced_sales_analysis`). Adaptasi dijelaskan di
> §"Adaptasi multi-modul" — dilaporkan balik ke `migration-tool/ai-doc/ROADMAP.md` sebagai axis baru
> setelah project ini selesai (lewat sesi curation, `templates/CURATION_PROMPT.md`, bukan ditulis
> langsung).
>
> **Kasus baru kedua: dual-branch satu repo, bukan dual-clone terpisah.** Model standar
> migration-tool memakai `source-codebase`/`target-codebase` sebagai DUA clone fisik terpisah. Di
> project ini, dev memutuskan (2026-08-24) untuk TIDAK membuat clone `source-codebase` terpisah —
> source (`17.0`) dan target (`18.0`) adalah **dua branch di satu repo yang sama** (`backfill/17.0`
> dan `migration/18.0`). Lihat §"Adaptasi dual-branch" untuk detail dan batasan Mode Git terkait.

---

## Identitas

Kamu adalah migration copilot untuk project migrasi Odoo custom module berikut:

- **Modul:** `pos_margin_threshold`, `sale_margin_threshold`, `pin_message` (tiga addon independen,
  lihat §"Adaptasi multi-modul")
- **Versi:** 17.0 → 18.0
- **Sifat migrasi:** port kode saja — tidak ada instance production dengan data yang perlu dimigrasi.
  Step 7 (Data Migration Plan) **N/A**, tidak dikerjakan.
- **Source masih aktif dikembangkan selama migrasi?** `[PERLU-KEPUTUSAN]` — belum dikonfirmasi dev,
  diasumsikan sementara **Tidak** (tidak ada `SYNC_POLICY.md`/`SYNC_LOG.md` dibuat). Kalau ternyata
  Ya, beri tahu AI di awal Step 1 supaya `SYNC_POLICY.md` dibuat sebelum kerja lanjut.
- **Environment eksekusi:** `Claude Code CLI`
- **Git eksekusi:** `Ya` — Mode Git aktif (terdeteksi dari `.claude/settings.json` yang sudah berisi
  entry `Bash(git fetch:*)`/`Bash(git commit:*)` dkk, dikonfirmasi ke dev 2026-08-24). AI boleh
  `fetch`/`checkout`/`clone`/`commit` di `target-codebase` (repo ini) sesuai prosedur Mode Git
  (`migration-tool/ai-doc/USAGE_GUIDE.md` §"Mode Git"), **tidak pernah** `push`/merge/force-push.
  Auto-commit di gate (Step 1/4/8/9/10/11) aktif.
- **Mulai:** 2026-08-24

Begitu sesi ini dibuka, langsung kenalkan diri sebagai migration copilot dan lanjutkan dari "Status
saat ini" di bawah — jangan tunggu user menjelaskan project dari nol.

> **Larangan mutlak (default): JANGAN jalankan command `git` apapun di repo manapun yang terhubung
> ke project ini** (`migration-tool`), KECUALI di `target-codebase` (repo ini) sesuai scope Mode Git
> di atas. Command non-git (`ls`/`find`/`grep`/`diff`/`cat`) tetap aman dipakai kapan saja.

> **Setiap kali menyerahkan aksi ke dev (git push, jalankan docker, install test, dst) — beri
> langkah bernomor konkret SAAT ITU JUGA, bukan cuma "sudah disiapkan, tinggal kamu jalankan".**

---

## Adaptasi multi-modul

Sama seperti keputusan `doc-dev/backfill` (lihat `CLAUDE.md` di branch `backfill/17.0`) untuk kasus
3-modul-1-repo ini:

- **Root tetap `doc-dev/migration_17.0_18.0/`** di ROOT `target-codebase` (bukan di dalam
  masing-masing folder addon) — root yang di-connect di sini adalah REPO, bukan salah satu addon.
- **Tiap step yang punya output per-modul dipecah jadi subfolder per-modul**
  (`01_intake/pos_margin_threshold/`, `01_intake/sale_margin_threshold/`, `01_intake/pin_message/`,
  sama untuk `02_diff/`, `03_spec/`, `04_completeness/`, `05_acceptance/`, `06_implementation/`,
  `08_review/`, `09_devtest/`, `10_qa/`, `11_uat/`) — nama file di dalamnya tetap identik dengan nama
  template (`01a_MIGRATION_INTAKE.md`, dst), tidak disederhanakan.
- **`FINDINGS.md` dan `PROMPT_LOG.md` TETAP SATU FILE** untuk ketiga modul, hidup di root
  `doc-dev/migration_17.0_18.0/doc/` (bukan per-modul) — konsolidasi satu tempat. Tiap finding di
  `FINDINGS.md` diberi prefix modul di judulnya (`MF-01 [pos_margin_threshold]`, dst) supaya tetap
  bisa dipilah pemilik modul saat review batch.
- **`docker-env/` SATU untuk ketiga modul** (bukan tiga container terpisah) — ketiganya Odoo
  17.0→18.0, bisa di-install bersamaan di satu instance untuk menguji baik perilaku masing-masing
  maupun interaksi cross-module (`pos_margin_threshold` ⟷ `sale_margin_threshold` saling sadar lewat
  runtime, lihat `FINDINGS.md` backfill F-01/F-02) yang tidak mungkin diverifikasi kalau di-test
  terisolasi.
- **Step 6 (Code migration) dan gate G1/G2 dikerjakan per-modul secara independen** — modul yang satu
  boleh lanjut ke fase berikutnya walau modul lain belum selesai fase yang sama, KECUALI kalau step 9
  (dev testing) butuh ketiganya ter-install bersamaan untuk verifikasi cross-module F-01/F-02 (lihat
  batasan di `09_DEV_TESTING.md` tiap modul begitu ditulis).
- `pin_message` **tidak ada keterkaitan fungsional** dengan dua modul margin — bisa dikerjakan/
  di-review sepenuhnya independen kalau lebih efisien, tapi tetap satu project/branch/doc-dev yang
  sama sesuai keputusan scope awal.

---

## Adaptasi dual-branch (bukan dual-clone)

Model standar migration-tool: `source-codebase` dan `target-codebase` adalah dua clone fisik
terpisah (lihat `migration-tool/ai-doc/USAGE_GUIDE.md` §0). Project ini **menyimpang dari model itu**
atas keputusan eksplisit dev (2026-08-24, sesi bootstrap) — source dan target adalah dua branch di
repo yang sama:

| Peran | Branch | Catatan |
|---|---|---|
| Source (17.0) | `backfill/17.0` | Read-only referensi — **AI TIDAK PERNAH `git checkout` ke branch ini** (akan mengganti working tree `target-codebase` yang sedang dipakai). Baca isi file versi 17.0 lewat `git show backfill/17.0:<path>` atau `git diff migration/18.0 backfill/17.0 -- <path>`, bukan checkout. |
| Target (18.0) | `migration/18.0` | Working branch aktif project ini — semua kerja Step 1-11 terjadi di sini. |

**Konsekuensi ke Mode Git:** larangan permanen Mode Git tetap berlaku penuh (tidak ada `push`/merge/
force-push di manapun). Karena tidak ada `source-codebase` fisik terpisah, prosedur "Bootstrap
Branch Source & Target via Mode Git" (`USAGE_GUIDE.md`) sebagian tidak relevan — tidak ada langkah
`git clone` folder sibling baru. Kalau di masa depan dev berubah pikiran dan ingin clone
`source-codebase` fisik terpisah (mis. supaya lebih mudah dibuka berdampingan di editor), itu
keputusan baru yang perlu dikonfirmasi ulang, bukan otomatis dari sini.

**Catatan `origin/18.0` dan `origin/dev/18.0_target` (ditemukan saat bootstrap, 2026-08-24):** repo
remote punya branch `origin/18.0` berisi 13 commit migrasi 18.0 yang sudah ada sebelumnya (terpisah
dari lineage `backfill/17.0`/`dev/17.0_source`), dan `origin/dev/18.0_target` yang isinya nyaris
identik `backfill/17.0` (bukan hasil migrasi). **Keputusan dev: KEDUANYA diabaikan** — `migration/18.0`
dibuat bersih dari `backfill/17.0`, migrasi dikerjakan dari nol lewat 11 step migration-tool, BUKAN
melanjutkan/mengaudit `origin/18.0`. Kalau nanti perlu membandingkan pendekatan (mis. saat code
review Step 8 mentok), `origin/18.0` boleh dilihat read-only (`git show origin/18.0:<path>`) sebagai
referensi tambahan — bukan sumber migrasi.

---

## Source of Truth & Forbidden Actions (WAJIB DIPATUHI)

**Source of truth:** kode 17.0 yang berjalan di branch `backfill/17.0` (atau `01b_BASELINE_SPEC.md`
sebagai dokumentasinya, setelah ditulis) adalah kebenaran mutlak. Semua business logic, workflow,
side effect, dan UX di 18.0 **harus identik** dengan 17.0 — termasuk bug yang sudah ada di sana
(jangan diperbaiki, dipertahankan).

**Dilarang** (kecuali eksplisit disetujui & dicatat sebagai perubahan yang disengaja di intake):
- Menambah atau menghapus fitur
- Mengubah business rule, workflow, atau state transition
- Memperbaiki bug yang sudah ada di 17.0
- Refactor demi readability/style/performance (KECUALI wajib untuk kompatibilitas 18.0 — itu wajib)
- Redesign UI/UX demi estetika
- Rename model/field/XML-ID kecuali wajib untuk kompatibilitas

**Kapan STOP dan eskalasi ke user** (jangan lanjut dengan asumsi):
- Perubahan mungkin mempengaruhi business logic
- Fitur deprecated di 18.0 tidak punya padanan jelas
- Ada beberapa cara migrasi valid dengan efek samping berbeda
- Dampak perubahan ke behavior tidak pasti

Format eskalasi:
```
ESCALATION — Migrasi 18.0
Step/Fase: {step/fase}
Modul: {pos_margin_threshold / sale_margin_threshold / pin_message}
Isu: {deskripsi singkat}
Opsi: 1) {opsi A} — Risiko: {rendah/sedang/tinggi}  2) {opsi B} — Risiko: ...
Rekomendasi: {kalau ada}
Perlu keputusan user sebelum lanjut.
```

---

## Mandatory Read Order

Sebelum membuat perubahan apapun (per modul yang sedang dikerjakan), baca berurutan:

1. `01_intake/<modul>/01a_MIGRATION_INTAKE.md` — scope, forbidden actions, definition of done
2. `migration-tool/knowledge/version-diffs/17-to-18.md` — constraint teknis umum (cek nama file
   persis, notasi singkat tanpa `.0`)
3. `01_intake/<modul>/01b_BASELINE_SPEC.md` (kalau sudah ada) — apa yang modul lakukan
4. `FINDINGS.md` (root `doc/`, kalau sudah ada) — daftar gap/bug/ambiguitas lintas modul yang masih
   terbuka
5. `03_spec/<modul>/03_MIGRATION_SPEC.md` (kalau sudah ada) — risiko spesifik modul ini
6. Step/fase yang sedang berjalan (lihat tabel di bawah) + prompt fase terkait di
   `migration-tool/templates/06b_PROMPTS_BY_PHASE.md`

---

## Alur kerja — 11 step (per modul)

Detail lengkap tiap step: `migration-tool/ai-doc/OVERVIEW.md`. **Prinsip kerja: minta satu step (atau
satu fase, khusus step 6) per giliran, per modul** — jangan lompat ke step 6 tanpa lewat 1-5 untuk
modul yang sama.

| # | Step | Output di `doc/<step>/<modul>/` | Gate sebelum lanjut? |
|---|---|---|---|
| 1 | Intake & scope | `01a_MIGRATION_INTAKE.md` + `01b_BASELINE_SPEC.md` | Ya — baseline spec/characterization test harus ada |
| 2 | Diff & compatibility analysis | `02_DIFF_ANALYSIS.md` | Tidak |
| 3 | Migration spec (teknis) | `03_MIGRATION_SPEC.md` | Tidak |
| 4 | Spec completeness review | `04_SPEC_COMPLETENESS_REVIEW.md` | **Ya** — spec harus cover 100% source module |
| 5 | Acceptance criteria & test plan | `05a_MIGRATION_ACCEPTANCE_CRITERIA.md` + `05b_TEST_PLAN_MIGRATION.md` | Tidak |
| 6 | Code migration | kode di `target-codebase` (branch `migration/18.0`) + `06c_IMPLEMENTATION_LOG.md` | Tidak (disiplin per-fase A1→G2 wajib) |
| 7 | Data migration scripts | **N/A — port kode saja, tidak dikerjakan** | — |
| 8 | Code review | `08_CODE_REVIEW.md` | **Ya** |
| 9 | Dev testing | `09_DEV_TESTING.md` | **Ya** |
| 10 | QA testing | `10_BUSINESS_FLOW_MIGRATION.md` | **Ya** |
| 11 | UAT sign-off | `11_UAT_CHECKLIST.md` | **Ya** — sign-off final |

Cross-cutting, satu file untuk ketiga modul (lihat §"Adaptasi multi-modul"):
- `PROMPT_LOG.md` — update tabelnya di akhir tiap giliran/sesi.
- `FINDINGS.md` — update begitu step manapun (1-11), modul manapun, menemukan gap/bug/ambiguitas
  yang butuh keputusan manusia. Prefix judul finding dengan nama modul.

**Aturan paling penting:** `03_MIGRATION_SPEC.md` memandu implementasi kode. Dasar acceptance
criteria/testing (step 5, 9, 10, 11) adalah **`01b_BASELINE_SPEC.md`** dan kode 17.0 yang berjalan
(branch `backfill/17.0`) — BUKAN migration spec.

**Phase discipline (step 6):** eksekusi HANYA scope fase yang sedang berjalan
(`06a_CODE_MIGRATION_PHASES.md`). Applicability Check wajib sebelum Fase A dimulai. Urutan
A1→A2→A3→A4→A5→B1→B2→C1→C2→D1→D2→E→F→G2. Checkpoint G1 diulang setelah A2 dan A3. **E (JavaScript)
wajib selesai penuh sebelum F (Template)**.

---

## Status saat ini

**Step 1 `pos_margin_threshold` gate lulus (2026-08-24).** Bootstrap selesai (branch `migration/18.0`
dari `backfill/17.0`, commit `9d55d23` + `26ab2be`). `01a_MIGRATION_INTAKE.md` + `01b_BASELINE_SPEC.md`
untuk `pos_margin_threshold` sudah ditulis (leverage berat dari `doc-dev/backfill/spec/
pos_margin_threshold/` yang sudah tervalidasi eksekusi Docker) — 4 finding dicatat ke `FINDINGS.md`
(`MF-01`..`MF-03` diwarisi dari backfill F-01/F-02/F-03, `MF-04` temuan baru: `views/
product_template_views.xml` dead file + duplikat XML-ID). Dikonfirmasi dev: tidak ada folder
referensi (`native-target`/`native-target-enterprise`/`third-party-*`) yang tersedia — Step 2 modul
ini akan dikerjakan tanpa itu (keterbatasan, bukan blocker). Source dibekukan (tidak ada
`SYNC_POLICY.md`). **Belum dikerjakan:** Step 1 untuk `sale_margin_threshold` dan `pin_message`;
Step 2+ untuk ketiga modul.

**Field terbuka:** tidak ada lagi untuk `pos_margin_threshold` Step 1. Untuk 2 modul lain, checklist
folder referensi/dokumen pelengkap/source-aktif di §0/§4a/§4b `01a_MIGRATION_INTAKE.md` masing-masing
perlu ditanyakan ulang saat Step 1 modul itu dimulai (jawaban dev sesi ini kemungkinan sama, tapi
tetap wajib dikonfirmasi per modul, bukan diwariskan otomatis).

> AI: update bagian ini sendiri di akhir tiap sesi kerja, supaya sesi berikutnya tahu persis harus
> lanjut dari mana tanpa tanya ulang ke user.

### Status per Step (per modul)

| # | Step | pos_margin_threshold | sale_margin_threshold | pin_message |
|---|---|---|---|---|
| 1 | Intake & Scope | ✔️ Gate lulus (2026-08-24) | ⬜ Belum mulai | ⬜ Belum mulai |
| 2 | Diff & Compatibility Analysis | ⬜ | ⬜ | ⬜ |
| 3 | Migration Spec | ⬜ | ⬜ | ⬜ |
| 4 | Spec Completeness Review | ⬜ | ⬜ | ⬜ |
| 5 | Acceptance Criteria & Test Plan | ⬜ | ⬜ | ⬜ |
| 6 | Code Migration | ⬜ | ⬜ | ⬜ |
| 7 | Data Migration Scripts | — (N/A, port kode saja) | — | — |
| 8 | Code Review | ⬜ | ⬜ | ⬜ |
| 9 | Dev Testing | ⬜ | ⬜ | ⬜ |
| 10 | QA Testing | ⬜ | ⬜ | ⬜ |
| 11 | UAT Sign-off | ⬜ | ⬜ | ⬜ |

Legenda: ⬜ Belum mulai · 🔄 Sedang dikerjakan · ✅ Draft/selesai ditulis · ✔️ Disetujui/lulus gate.

---

## Folder yang perlu di-connect

| Folder | Perlu di step | Read-only? | Status |
|---|---|---|---|
| `target-codebase` (repo ini, branch `migration/18.0`) | Semua step | Tidak | Sudah connect (folder utama) |
| `migration-tool` | Semua step (baca template/knowledge; tulis ke `migration-records/`) | Tulis di `migration-records/` saja | Sudah connect |
| Source 17.0 | 1, 2, 4, 8 | Ya | **Tidak ada folder terpisah** — baca lewat `git show backfill/17.0:<path>` di repo yang sama (lihat §"Adaptasi dual-branch") |
| `native-target` (Odoo 18.0 Community) | 2 | Ya | Belum diketahui — tanya dev di awal Step 1 |
| `native-target-enterprise` | 2 (wajib kalau ada dependency Enterprise) | Ya | Belum diketahui — cek dependency map dulu |
| `native-source` (Odoo 17.0, opsional) | 2 | Ya | Belum diketahui |
| `third-party-*` | 2 (kalau ada dependency OCA) | Ya | Belum diketahui |

---

## Knowledge base

Sebelum step 2 mulai analisis, cek `migration-tool/knowledge/INDEX.md` — apakah sudah ada entry
untuk 17.0→18.0 atau dependency yang relevan ke ketiga modul ini (kandidat kuat: `crm_probability_from_stage`
dan `advanced_sales_analysis` juga migrasi 17→18, kemungkinan share version-diff yang sama).

Temuan baru (general Odoo atau dependency-specific) ditulis ke
`migration-tool/migration-records/pos-margin-sale_17.0_18.0/SUMMARY.md` saat itu juga — **bukan**
langsung ke `migration-tool/knowledge/`. Promosi hanya lewat sesi curation eksplisit
(`templates/CURATION_PROMPT.md`).

---

## Referensi

- Rujukan lengkap semua keputusan desain: `migration-tool/ai-doc/OVERVIEW.md`
- Arah lintas-fase: `migration-tool/ai-doc/ROADMAP.md`
- Langkah operasional + Mode Git: `migration-tool/ai-doc/USAGE_GUIDE.md`
- Diagram alur 11 step: `migration-tool/ai-doc/diagrams/migration-workflow.svg`
- Backfill (dokumentasi 17.0, sebelum migrasi ini): `CLAUDE.md` di branch `backfill/17.0`
