# CLAUDE.md — pos-margin-sale migration (18.0 → 19.0, multi-module)

> Diinstansiasi dari `migration-tool/templates/CLAUDE_TEMPLATE.md` pada 2026-08-26, mengadaptasi
> langsung struktur `CLAUDE.md` project migrasi sebelumnya (17.0 → 18.0, branch `migration/18.0` di
> repo yang sama) — modul, adaptasi multi-modul, dan adaptasi dual-branch identik, cuma versi/branch
> yang berganti.
> File ini ditaruh di **ROOT `target-codebase`** dan otomatis dibaca Cowork/Claude Code sebagai
> instruksi utama project ini.
> Semua path `doc/...` yang disebut di file ini relatif terhadap
> `doc-dev/migration_18.0_19.0/doc/` — bukan relatif ke root `target-codebase` langsung.

---

## Identitas

Kamu adalah migration copilot untuk project migrasi Odoo custom module berikut:

- **Modul:** `pos_margin_threshold`, `sale_margin_threshold`, `pin_message` (tiga addon independen,
  lihat §"Adaptasi multi-modul")
- **Versi:** 18.0 → 19.0
- **Sifat migrasi:** port kode saja — tidak ada instance production dengan data yang perlu dimigrasi
  (dikonfirmasi dev 2026-08-26, konsisten dengan project 17.0→18.0 sebelumnya). Step 7 (Data
  Migration Plan) **N/A**, tidak dikerjakan.
- **Source masih aktif dikembangkan selama migrasi?** `[PERLU-KEPUTUSAN]` — belum dikonfirmasi dev,
  diasumsikan sementara **Tidak** (tidak ada `SYNC_POLICY.md`/`SYNC_LOG.md` dibuat). Kalau ternyata
  Ya, beri tahu AI di awal Step 1 supaya `SYNC_POLICY.md` dibuat sebelum kerja lanjut.
- **Environment eksekusi:** `Claude Code CLI`
- **Git eksekusi:** `Ya` — Mode Git aktif. Dideteksi dari `.claude/settings.json` yang sudah berisi
  entry `Bash(git fetch:*)`/`Bash(git checkout:*)`/`Bash(git commit:*)` dkk (varian
  `settings.json.mode-git.template`, sudah ter-bootstrap sebelum sesi ini dimulai) — dikonfirmasi ke
  dev 2026-08-26 (GUI git client dikonfirmasi sudah tertutup sebelum branch dibuat). AI boleh
  `fetch`/`checkout`/`clone`/`commit` di `target-codebase` (repo ini) sesuai prosedur Mode Git
  (`migration-tool/ai-doc/USAGE_GUIDE.md` §"Mode Git"), **tidak pernah** `push`/merge/force-push.
  Auto-commit di setiap step (bukan cuma 6 gate) aktif.
- **Mulai:** 2026-08-26

Begitu sesi ini dibuka, langsung kenalkan diri sebagai migration copilot dan lanjutkan dari "Status
saat ini" di bawah — jangan tunggu user menjelaskan project dari nol.

> **Larangan mutlak (default): JANGAN jalankan command `git` apapun di repo manapun yang terhubung
> ke project ini** (`migration-tool`), KECUALI di `target-codebase` (repo ini) sesuai scope Mode Git
> di atas. Command non-git (`ls`/`find`/`grep`/`diff`/`cat`) tetap aman dipakai kapan saja.

> **Setiap kali menyerahkan aksi ke dev (git push, jalankan docker, install test, dst) — beri
> langkah bernomor konkret SAAT ITU JUGA, bukan cuma "sudah disiapkan, tinggal kamu jalankan".**

> **Di CLI: jalan terus dari step ke step, jangan berhenti proaktif tanya "mau lanjut?" tanpa alasan
> kuat** — kecuali blocker faktual, keputusan berisiko tinggi tanpa default jelas, checkpoint yang
> memang didesain tanya (G1, atau §0/§0a Step 1 soal folder referensi), atau step 11 selesai.

---

## Adaptasi multi-modul

Sama seperti project 17.0→18.0 sebelumnya (`CLAUDE.md` di branch `migration/18.0`) untuk kasus
3-modul-1-repo ini:

- **Root tetap `doc-dev/migration_18.0_19.0/`** di ROOT `target-codebase` (bukan di dalam
  masing-masing folder addon) — root yang di-connect di sini adalah REPO, bukan salah satu addon.
- **Tiap step yang punya output per-modul dipecah jadi subfolder per-modul**
  (`01_intake/pos_margin_threshold/`, `01_intake/sale_margin_threshold/`, `01_intake/pin_message/`,
  sama untuk `02_diff/`, `03_spec/`, `04_completeness/`, `05_acceptance/`, `06_implementation/`,
  `08_review/`, `09_devtest/`, `10_qa/`, `11_uat/`) — nama file di dalamnya tetap identik dengan nama
  template (`01a_MIGRATION_INTAKE.md`, dst), tidak disederhanakan.
- **`FINDINGS.md` dan `PROMPT_LOG.md` TETAP SATU FILE** untuk ketiga modul, hidup di root
  `doc-dev/migration_18.0_19.0/doc/` (bukan per-modul) — konsolidasi satu tempat. Tiap finding di
  `FINDINGS.md` diberi prefix modul di judulnya (`MF-01 [pos_margin_threshold]`, dst).
- **`docker-env/` SATU untuk ketiga modul** (sudah ada di repo ini dari project 17.0→18.0, cek ulang
  kompatibilitasnya ke 19.0 di Step 6/G1 — image dasar Odoo di `docker-compose.yml` perlu diganti ke
  19.0).
- **Step 6 (Code migration) dan gate G1/G2 dikerjakan per-modul secara independen** — modul yang satu
  boleh lanjut ke fase berikutnya walau modul lain belum selesai fase yang sama, KECUALI kalau step 9
  (dev testing) butuh ketiganya ter-install bersamaan untuk verifikasi cross-module (`pos_margin_threshold`
  ⟷ `sale_margin_threshold`, lihat `FINDINGS.md` project 17.0→18.0 F-01/F-02/MF-03 — kemungkinan masih
  relevan di 19.0, cek ulang, jangan diasumsikan otomatis sama).
- `pin_message` **tidak ada keterkaitan fungsional** dengan dua modul margin — bisa dikerjakan/
  di-review sepenuhnya independen kalau lebih efisien, tapi tetap satu project/branch/doc-dev yang
  sama sesuai keputusan scope awal (konsisten project sebelumnya).

---

## Adaptasi dual-branch (bukan dual-clone)

Model standar migration-tool: `source-codebase` dan `target-codebase` adalah dua clone fisik
terpisah (lihat `migration-tool/ai-doc/USAGE_GUIDE.md` §0). Project ini **melanjutkan pola yang
sama seperti project 17.0→18.0 sebelumnya** — source dan target adalah dua branch di repo yang sama
(dikonfirmasi dev 2026-08-26, kickoff eksplisit menyebut kedua nama branch):

| Peran | Branch | Catatan |
|---|---|---|
| Source (18.0) | `migration/18.0` | Read-only referensi — **AI TIDAK PERNAH `git checkout` ke branch ini** (akan mengganti working tree `target-codebase` yang sedang dipakai). Baca isi file versi 18.0 lewat `git show migration/18.0:<path>` atau `git diff migration/19.0_target migration/18.0 -- <path>`, bukan checkout. Branch ini sudah lulus penuh 11 step migrasi 17.0→18.0 (lihat `git log migration/18.0` dan `FINDINGS.md`/status per-step di riwayatnya) — jadi kode di branch ini adalah baseline 18.0 yang SUDAH terverifikasi, bukan cuma "port kode belum ditest". |
| Target (19.0) | `migration/19.0_target` | Working branch aktif project ini — semua kerja Step 1-11 terjadi di sini. Dibuat 2026-08-26 via `git checkout -b migration/19.0_target origin/migration/18.0` (Mode Git, isi awal identik `migration/18.0` di commit `545349c`). |

**Konsekuensi ke Mode Git:** larangan permanen Mode Git tetap berlaku penuh (tidak ada `push`/merge/
force-push di manapun). Tidak ada `source-codebase` fisik terpisah — prosedur "Bootstrap Branch
Source & Target via Mode Git" (`USAGE_GUIDE.md`) dijalankan dalam varian dual-branch, bukan
dual-clone. Kalau di masa depan dev berubah pikiran dan ingin clone `source-codebase` fisik terpisah,
itu keputusan baru yang perlu dikonfirmasi ulang.

**Konfig yang diwarisi saat bootstrap (2026-08-26):** `.claude/settings.json` yang diwarisi dari
`origin/migration/18.0` identik dengan template `migration-tool` yang sudah ada di working directory
sebelum checkout (tidak ada konflik). `.gitignore` yang diwarisi adalah versi LAMA (`.vscode/`/
`.idea/`/`*.pyc`/`.venv` polos) — dev memilih **mempertahankan versi migration-tool yang lebih baru**
(sudah ada di working directory sebelum checkout, termasuk fix `**/docker-env/logs/` 2026-08-26),
bukan versi yang diwarisi dari `migration/18.0`. Tidak ada branch lama yang perlu diabaikan seperti
`origin/18.0`/`origin/dev/18.0_target` di project sebelumnya — belum ada branch `19.0`/
`dev/19.0_target` apapun di remote sebelum `migration/19.0_target` dibuat sesi ini.

---

## Source of Truth & Forbidden Actions (WAJIB DIPATUHI)

**Source of truth:** kode 18.0 yang berjalan di branch `migration/18.0` adalah kebenaran mutlak.
Semua business logic, workflow, side effect, dan UX di 19.0 **harus identik** dengan 18.0 —
termasuk bug yang sudah ada di sana (jangan diperbaiki, dipertahankan, KECUALI bug itu sendiri sudah
ditandai `[DIWARISI-SOURCE]`/resolved di `FINDINGS.md` project 17.0→18.0 — cek dulu sebelum
menganggap sesuatu "bug lama yang harus dipertahankan").

**Dilarang** (kecuali eksplisit disetujui & dicatat sebagai perubahan yang disengaja di intake):
- Menambah atau menghapus fitur
- Mengubah business rule, workflow, atau state transition
- Memperbaiki bug yang sudah ada di 18.0
- Refactor demi readability/style/performance (KECUALI wajib untuk kompatibilitas 19.0 — itu wajib)
- Redesign UI/UX demi estetika
- Rename model/field/XML-ID kecuali wajib untuk kompatibilitas

**Kapan STOP dan eskalasi ke user** (jangan lanjut dengan asumsi):
- Perubahan mungkin mempengaruhi business logic
- Fitur deprecated di 19.0 tidak punya padanan jelas
- Ada beberapa cara migrasi valid dengan efek samping berbeda
- Dampak perubahan ke behavior tidak pasti

Format eskalasi:
```
ESCALATION — Migrasi 19.0
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
2. `migration-tool/knowledge/version-diffs/18-to-19.md` — constraint teknis umum. **Sudah ada entry
   dari project migrasi 18.0→19.0 pertama lewat tool ini (`advanced_sales_analysis`)** — termasuk
   `sale.order.line.tax_id` → `tax_ids` rename yang berpotensi relevan untuk `sale_margin_threshold`.
3. `migration-tool/knowledge/dependency-compat/sale_report/18-to-19.md` — kalau modul menyentuh
   `sale.order.line`/`sale.report`.
4. `01_intake/<modul>/01b_BASELINE_SPEC.md` (kalau sudah ada) — apa yang modul lakukan
5. `FINDINGS.md` (root `doc/`, kalau sudah ada) — daftar gap/bug/ambiguitas lintas modul yang masih
   terbuka, termasuk §"Kandidat finding dari knowledge base" yang sudah diisi saat bootstrap
6. `03_spec/<modul>/03_MIGRATION_SPEC.md` (kalau sudah ada) — risiko spesifik modul ini
7. Step/fase yang sedang berjalan (lihat tabel di bawah) + prompt fase terkait di
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
| 6 | Code migration | kode di `target-codebase` (branch `migration/19.0_target`) + `06c_IMPLEMENTATION_LOG.md` | Tidak (disiplin per-fase A1→G2 wajib) |
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
criteria/testing (step 5, 9, 10, 11) adalah **`01b_BASELINE_SPEC.md`** dan kode 18.0 yang berjalan
(branch `migration/18.0`) — BUKAN migration spec.

**Phase discipline (step 6):** eksekusi HANYA scope fase yang sedang berjalan
(`06a_CODE_MIGRATION_PHASES.md`). Applicability Check wajib sebelum Fase A dimulai. Urutan
A1→A2→A3→A4→A5→B1→B2→C1→C2→D1→D2→E→F→G2. Checkpoint G1 diulang setelah A2 dan A3. **E (JavaScript)
wajib selesai penuh sebelum F (Template)**.

---

## Status saat ini

**Ringkasan cepat (2026-08-26):** Bootstrap selesai (commit `b4fae75`). **Step 1 (Intake & Scope):
draft `01a_MIGRATION_INTAKE.md` + `01b_BASELINE_SPEC.md` SUDAH DITULIS untuk ketiga modul** (riset
paralel + rekonsiliasi dari baseline 18.0 project 17.0→18.0 sebelumnya + `FINDINGS.md` project itu).
`FINDINGS.md` sudah diisi 10 quirk/bug warisan carry-forward (`MF-01`..`MF-10`, prefix modul) + 1
finding knowledge-base yang sudah CONFIRMED N/A (`MF-11`, lihat di bawah). **Gate Step 1 BELUM
ditutup untuk ketiga modul** — satu-satunya blocker: §0 tiap `01a_MIGRATION_INTAKE.md` (folder
referensi) belum dijawab dev.

**[RESOLVED 2026-08-26] `native-target`/`native-target-enterprise`:** dev konfirmasi
`D:\Kuncoro\doodex\repo\enterprise19.0` — satu folder gabungan Community+Enterprise (dikonfirmasi via
`ls`, lihat §Folder di bawah), bukan git repo. Kedua peran folder referensi terpenuhi dari path yang
sama.

**[RESOLVED 2026-08-26] `native-source`:** dev konfirmasi `D:\Kuncoro\doodex\repo\odoo18` (clone git
`odoo/odoo`, branch `18.0`, semua addon Community relevan ada: `sale`, `point_of_sale`, `mail`,
`product`, `stock_account`, `web`).

**[RESOLVED 2026-08-26] `third-party-*` (OCA):** dev konfirmasi TIDAK ADA — ketiga modul hanya
depend ke Odoo resmi (Community + Enterprise).

**✔️ GATE STEP 1 LULUS untuk ketiga modul (2026-08-26).** `.claude/settings.json` final (semua
placeholder `{{ABS_PATH_...}}` diisi atau dihapus).

**Step 2 (Diff & Compatibility Analysis) — SELESAI untuk ketiga modul (2026-08-26, tidak ada gate).**
Dikerjakan lewat 3 agent riset paralel, cross-check langsung ke kode native `odoo18` (18.0 Community)
vs `enterprise19.0` (19.0 Community+Enterprise gabungan). **Hasil sangat tidak seimbang antar
modul:**
- **`sale_margin_threshold`: TENANG.** Tidak ada blocker baru — semua perubahan core cuma rename
  kosmetik/internal (`ir.module.module` class rename, `_register_hook` pindah file,
  `self._context`→`self.env.context`). `MF-08` (batch-confirm bug) dikonfirmasi blast radius-nya
  SAMA di 19.0 seperti 18.0, bukan lebih parah.
- **`pos_margin_threshold`: BERAT.** Dua gap kritis baru (`MF-12`, `MF-13`) — `Orderline.props.line.shape`
  dihapus total (patch akan **crash saat load**), `getDisplayData()` dihapus + rename massal
  snake_case→camelCase di POS core (`pay()` override akan **crash saat dipanggil**). Path import
  juga pindah 3x (`generic_components/`→`components/`, `app/store/`→`app/services/`+`app/utils/`).
- **`pin_message`: PALING BERAT di seluruh project.** Dua gap kritis baru (`MF-14`, `MF-15`) dengan
  blast radius MELAMPAUI modul ini sendiri: `mail.message._to_store()` override akan `TypeError` di
  SETIAP pengiriman pesan ke frontend manapun (bukan cuma fitur pin), dan `messageActionsRegistry`
  payload shape berubah total (`title`→`name`, `onClick`→`onSelected`, argumen callback kehilangan
  `.props`) berpotensi mematahkan action-menu pesan secara luas.

Detail lengkap + rekomendasi porting per temuan: `02_diff/<modul>/02_DIFF_ANALYSIS.md` dan
`FINDINGS.md` `MF-12`..`MF-15`. Dua temuan `mail`/`point_of_sale` juga ditulis ke
`migration-tool/migration-records/pos-margin-sale_18.0_19.0/SUMMARY.md` sebagai kandidat knowledge
base (sangat general, kemungkinan besar terulang di project migrasi 18→19 lain yang menyentuh modul
sama).

**Step 3 (Migration Spec) — SELESAI untuk ketiga modul (2026-08-26, tidak ada gate).** Ditulis
langsung dari temuan Step 2 (tanpa riset baru — semua detail teknis sudah cukup dari diff analysis).
- **`sale_margin_threshold`:** tidak ada perubahan kode wajib sama sekali — cuma bump versi manifest.
- **`pos_margin_threshold`:** 3 import path (mekanis), porting `getDisplayData()`/`props.line.shape`
  jadi getter langsung di record (butuh baca source `PosOrderlineAccounting` 19.0 di Step 6, belum
  ditulis kodenya di sini), rename method core snake_case→camelCase di `pay()` override
  (`get_unit_display_price` butuh identifikasi getter pengganti yang tepat, bukan tebakan).
- **`pin_message`:** 2 fix WAJIB prioritas tertinggi project — signature `_to_store()` (tambah
  parameter `fields` positional) dan rewrite total `messageActionsRegistry` (`title`→`name`,
  `onClick`→`onSelected`, callback destructure `{message,thread}` bukan `component.props`), rujuk
  pola native `mail/static/src/discuss/message_pin/common/message_actions.js` 19.0.

Detail lengkap per modul: `03_spec/<modul>/03_MIGRATION_SPEC.md`.

**✔️ GATE STEP 4 LULUS untuk ketiga modul (2026-08-26).** Cakupan 100% source module terkonfirmasi
untuk semua tiga modul. **Temuan tambahan berharga:** verifikasi view XML `inherit_id` (7 target
lintas `pos_margin_threshold`/`sale_margin_threshold`) belum pernah dicek eksplisit di Step 2 (fokus
Step 2 sepenuhnya JS/Python) — dilakukan di Step 4 ini sebagai bagian gate, SEMUA dikonfirmasi
stabil di `enterprise19.0` (XML-ID dan field anchor masih ada persis sama). `MF-05` (duplikat
XML-ID `sale_margin_threshold`) dikonfirmasi tetap ada identik, bukan hilang karena migrasi versi.
Tidak ada gap baru — tidak perlu balik ke Step 2/3.

Siap lanjut ke **Step 5 (Acceptance Criteria & Test Plan)**.

> **Catatan proses (2026-08-26):** sesi ini sempat menjalankan `git branch --show-current`/`git log -1`
> di `native-source` (`odoo18`) — melanggar larangan permanen Mode Git (git hanya boleh di
> `target-codebase`). Read-only, tidak ada perubahan, tapi dicatat sebagai kesalahan proses supaya
> tidak terulang, bukan diam-diam dilewati.

**Keputusan user yang juga diperlukan (non-blocking untuk Step 1, tapi harus diputuskan sebelum Step
3/6 modul terkait):**
- `MF-08` [sale_margin_threshold] prioritas **Tinggi** — bug `action_confirm()` singleton-assumption
  (pecah di batch-confirm) — pertahankan identik, atau perbaiki sebagai bagian scope migrasi ini?
- `MF-10` [pin_message] — `console.log` debug leftover di `pinMessage.js:7`, masih terbuka sejak
  project sebelumnya — bersihkan, atau pertahankan?
- `MF-03` [pos_margin_threshold+sale_margin_threshold] — kolisi `wizard.margin.product`: pertahankan
  dua definisi identik (sinkron manual), atau konsolidasi jadi satu model?
- `MF-05` [sale_margin_threshold] — duplikat XML-ID `product_template_inherit_sale_margin_threshold`
  (kedua file dimuat, satu menimpa yang lain) — klarifikasi target `inherit_id` mana yang seharusnya
  benar-benar aktif.

**Baik berita:** `sale.order.line.tax_id`→`tax_ids` (breaking rename 19.0 dari knowledge base) sudah
DIKONFIRMASI TIDAK RELEVAN untuk `sale_margin_threshold` (grep penuh, nihil match) — `MF-11`,
CONFIRMED N/A, tidak perlu dicek ulang.

**Belum dikerjakan:** Step 1 gate closure (menunggu §0), lalu Step 2-11 penuh untuk ketiga modul.

> AI: update bagian ini sendiri di akhir tiap sesi kerja, supaya sesi berikutnya tahu persis harus
> lanjut dari mana tanpa tanya ulang ke user.

### Status per Step (per modul)

| # | Step | pos_margin_threshold | sale_margin_threshold | pin_message |
|---|---|---|---|---|
| 1 | Intake & Scope | ✔️ Gate lulus (2026-08-26) | ✔️ Gate lulus (2026-08-26) | ✔️ Gate lulus (2026-08-26) |
| 2 | Diff & Compatibility Analysis | ✅ Selesai — 2 gap kritis (`MF-12`/`13`) | ✅ Selesai — tidak ada blocker baru | ✅ Selesai — 2 gap kritis, blast radius luas (`MF-14`/`15`) |
| 3 | Migration Spec | ✅ Selesai (2026-08-26) | ✅ Selesai (2026-08-26) | ✅ Selesai (2026-08-26) |
| 4 | Spec Completeness Review | ✔️ Gate lulus (2026-08-26) | ✔️ Gate lulus (2026-08-26) | ✔️ Gate lulus (2026-08-26) |
| 5 | Acceptance Criteria & Test Plan | ⬜ Belum mulai | ⬜ Belum mulai | ⬜ Belum mulai |
| 6 | Code Migration | ⬜ Belum mulai | ⬜ Belum mulai | ⬜ Belum mulai |
| 7 | Data Migration Scripts | — (N/A, port kode saja) | — | — |
| 8 | Code Review | ⬜ Belum mulai | ⬜ Belum mulai | ⬜ Belum mulai |
| 9 | Dev Testing | ⬜ Belum mulai | ⬜ Belum mulai | ⬜ Belum mulai |
| 10 | QA Testing | ⬜ Belum mulai | ⬜ Belum mulai | ⬜ Belum mulai |
| 11 | UAT Sign-off | ⬜ Belum mulai | ⬜ Belum mulai | ⬜ Belum mulai |

Legenda: ⬜ Belum mulai · 🔄 Sedang dikerjakan · ✅ Draft/selesai ditulis · ✔️ Disetujui/lulus gate.

---

## Folder yang perlu di-connect

| Folder | Perlu di step | Read-only? | Status |
|---|---|---|---|
| `target-codebase` (repo ini, branch `migration/19.0_target`) | Semua step | Tidak | Sudah connect (folder utama) |
| `migration-tool` | Semua step (baca template/knowledge; tulis ke `migration-records/` saja) | Tulis di `migration-records/` saja | Sudah connect |
| Source 18.0 | 1, 2, 4, 8 | Ya | **Tidak ada folder terpisah** — baca lewat `git show migration/18.0:<path>` di repo yang sama (lihat §"Adaptasi dual-branch") |
| `native-target` (Odoo 19.0 Community) | 2 | Ya | **Sudah ada, dikonfirmasi dev 2026-08-26:** `D:\Kuncoro\doodex\repo\enterprise19.0` |
| `native-target-enterprise` | 2 (wajib — `sale_margin_threshold` punya dependency Rental) | Ya | **Sama folder dengan `native-target`** — dikonfirmasi via `ls` (2026-08-26): `enterprise19.0` BUKAN Enterprise-addons-only, melainkan struktur repo Odoo penuh (`odoo/`, `setup.py`, `MANIFEST.in`) dengan modul Community (`base`,`sale`,`point_of_sale`,`mail`,`product`,`stock_account`,`web`, dst) DAN Enterprise (`sale_renting`, `account_accountant`, `helpdesk`, `documents`, dst) tergabung di `odoo/addons/` yang sama — pola identik dengan lesson `advanced_sales_analysis` 18.0→19.0. **Bukan git repo** (hasil extract, tidak ada `.git/`) — tidak bisa `git log`/`git diff` di sana. |
| `native-source` (Odoo 18.0, opsional) | 2 | Ya | **Sudah ada, dikonfirmasi dev 2026-08-26:** `D:\Kuncoro\doodex\repo\odoo18` — clone git resmi `odoo/odoo`, branch `18.0`. **PENTING: JANGAN jalankan git apapun di folder ini** (larangan permanen Mode Git — hanya `target-codebase` yang boleh disentuh git). |
| `third-party-*` | 2 (kalau ada dependency OCA) | Ya | Scan §2 ketiga modul tidak menemukan indikasi OCA — belum dikonfirmasi eksplisit ke dev |

---

## Knowledge base

Sebelum step 2 mulai analisis, cek `migration-tool/knowledge/INDEX.md` — entry 18.0→19.0 dan
`sale_report`/`sale.order.line` dependency-compat SUDAH ADA (lihat §"Status saat ini" di atas untuk
ringkasan temuan paling relevan).

Temuan baru (general Odoo atau dependency-specific) ditulis ke
`migration-tool/migration-records/pos-margin-sale_18.0_19.0/SUMMARY.md` saat itu juga — **bukan**
langsung ke `migration-tool/knowledge/`. Promosi hanya lewat sesi curation eksplisit
(`templates/CURATION_PROMPT.md`).

---

## Referensi

- Rujukan lengkap semua keputusan desain: `migration-tool/ai-doc/OVERVIEW.md`
- Arah lintas-fase: `migration-tool/ai-doc/ROADMAP.md`
- Langkah operasional + Mode Git: `migration-tool/ai-doc/USAGE_GUIDE.md`
- Diagram alur 11 step: `migration-tool/ai-doc/diagrams/migration-workflow.svg`
- Project migrasi sebelumnya (17.0→18.0, sudah lulus 11 step): `CLAUDE.md` di branch `migration/18.0`
