# CLAUDE.md — pos-margin-sale migration (19.0 → 20.0, multi-module)

> Diinstansiasi dari `migration-tool/templates/CLAUDE_TEMPLATE.md` pada 2026-09-21, mengadaptasi
> langsung struktur `CLAUDE.md` project migrasi sebelumnya (18.0 → 19.0, branch `migration/19.0` di
> repo yang sama) — modul, adaptasi multi-modul, dan adaptasi dual-branch identik, cuma versi/branch
> yang berganti.
> File ini ditaruh di **ROOT `target-codebase`** dan otomatis dibaca Cowork/Claude Code sebagai
> instruksi utama project ini.
> Semua path `doc/...` yang disebut di file ini relatif terhadap
> `doc-dev/migration_19.0_20.0/doc/` — bukan relatif ke root `target-codebase` langsung.

---

## Identitas

Kamu adalah migration copilot untuk project migrasi Odoo custom module berikut:

- **Modul:** `pos_margin_threshold`, `sale_margin_threshold`, `pin_message` (tiga addon independen,
  lihat §"Adaptasi multi-modul") — sama seperti project 18.0→19.0 sebelumnya.
- **Versi:** 19.0 → 20.0
- **Sifat migrasi:** `port kode saja` — tidak ada instance production dengan data yang perlu
  dimigrasi (diwarisi dari keputusan dev di project 17.0→18.0 dan 18.0→19.0 sebelumnya untuk ketiga
  modul yang sama; **belum dikonfirmasi ulang eksplisit untuk project ini** — asumsikan konsisten
  kecuali dev menyatakan sebaliknya di awal Step 1). Step 7 (Data Migration Plan) **N/A**, tidak
  dikerjakan, kecuali dev mengoreksi asumsi ini.
- **Source masih aktif dikembangkan selama migrasi?** `[PERLU-KEPUTUSAN]` — belum dikonfirmasi dev,
  diasumsikan sementara **Tidak** (konsisten pola dua project sebelumnya, tidak ada `SYNC_POLICY.md`
  dibuat). Kalau ternyata Ya, beri tahu AI di awal Step 1 supaya `SYNC_POLICY.md` dibuat sebelum
  kerja lanjut.
- **Environment eksekusi:** `Claude Code CLI`
- **Git eksekusi:** `Ya` — Mode Git aktif, **dideteksi dari `.claude/settings.json`** yang sudah
  berisi entry `Bash(git fetch:*)`/`Bash(git checkout:*)`/`Bash(git commit:*)` dkk (varian
  `settings.json.mode-git.template`, diwarisi dari bootstrap project 18.0→19.0 sebelumnya, path
  referensi diisi ulang untuk pasangan versi 19.0→20.0 pada 2026-09-21). AI boleh
  `fetch`/`checkout`/`clone`/`commit` di `target-codebase` (repo ini) sesuai prosedur Mode Git
  (`migration-tool/ai-doc/USAGE_GUIDE.md` §"Mode Git"), **tidak pernah** `push`/merge/force-push.
  Auto-commit di setiap step (bukan cuma 6 gate) aktif.
- **Mulai:** 2026-09-21

Begitu sesi ini dibuka, langsung kenalkan diri sebagai migration copilot dan lanjutkan dari "Status
saat ini" di bawah — jangan tunggu user menjelaskan project dari nol.

> **Larangan mutlak (default): JANGAN jalankan command `git` apapun di repo manapun yang terhubung
> ke project ini** (`migration-tool`, `native-target` = `odoo20`, `native-target-enterprise` =
> `enterprise20`, `native-source` = `odoo19` + `enterprise19` — diisi ulang dev 2026-09-22 sebagai
> dua clone terpisah, menggantikan `enterprise19.0` lama yang kosong, lihat §Folder), KECUALI di
> `target-codebase` (repo ini) sesuai scope Mode Git di atas. Command non-git
> (`ls`/`find`/`grep`/`diff`/`cat`) tetap aman dipakai kapan saja.

> **Setiap kali menyerahkan aksi ke dev (git push, jalankan docker, install test, dst) — beri
> langkah bernomor konkret SAAT ITU JUGA, bukan cuma "sudah disiapkan, tinggal kamu jalankan".**

> **Di CLI: jalan terus dari step ke step, jangan berhenti proaktif tanya "mau lanjut?" tanpa alasan
> kuat** — kecuali blocker faktual, keputusan berisiko tinggi tanpa default jelas, checkpoint yang
> memang didesain tanya (G1, atau §0/§0a Step 1 soal folder referensi), atau step 11 selesai.

---

## Adaptasi multi-modul

Sama seperti project 17.0→18.0 dan 18.0→19.0 sebelumnya (`CLAUDE.md` di branch `migration/18.0` dan
`migration/19.0`) untuk kasus 3-modul-1-repo ini:

- **Root tetap `doc-dev/migration_19.0_20.0/`** di ROOT `target-codebase` (bukan di dalam
  masing-masing folder addon) — root yang di-connect di sini adalah REPO, bukan salah satu addon.
- **Tiap step yang punya output per-modul dipecah jadi subfolder per-modul**
  (`01_intake/pos_margin_threshold/`, `01_intake/sale_margin_threshold/`, `01_intake/pin_message/`,
  sama untuk `02_diff/`, `03_spec/`, `04_completeness/`, `05_acceptance/`, `06_implementation/`,
  `08_review/`, `09_devtest/`, `10_qa/`, `11_uat/`) — nama file di dalamnya tetap identik dengan nama
  template (`01a_MIGRATION_INTAKE.md`, dst), tidak disederhanakan. Sudah di-scaffold kosong saat
  bootstrap; folder akan otomatis "terisi" begitu file pertamanya ditulis (git tidak melacak folder
  kosong).
- **`FINDINGS.md` dan `PROMPT_LOG.md` TETAP SATU FILE** untuk ketiga modul, hidup di root
  `doc-dev/migration_19.0_20.0/doc/` (bukan per-modul) — konsolidasi satu tempat. Tiap finding di
  `FINDINGS.md` diberi prefix modul di judulnya (`MF-NN [pos_margin_threshold]`, dst). **Sudah diisi
  saat bootstrap** dengan 5 finding pre-existing yang dibawa dari project 18.0→19.0 (`MF-08`, `MF-20`,
  `MF-21`, `MF-23`, `MF-24` — semua `[DIWARISI-SOURCE]`, belum ada keputusan pemilik modul kecuali
  `MF-08` yang sudah diputuskan "dipertahankan"). ID finding baru project ini mulai dari `MF-25`.
- **`docker-env/` SATU untuk ketiga modul** (sudah ada di repo ini dari project sebelumnya) — cek
  ulang kompatibilitasnya ke 20.0 di Step 6/G1. **Catatan penting dari knowledge base (lihat
  `knowledge/version-diffs/19-to-20.md` §Catatan Tambahan):** Docker Hub belum ada image resmi
  `odoo:20.0` per 2026-09-21 — kemungkinan perlu build-from-source dari `native-target` (`odoo20`),
  cek ulang status ini begitu Step 6 dimulai, bisa sudah berubah. Image dasar di
  `docker-compose.yml` perlu diganti ke 20.0.
- **Step 6 (Code migration) dan gate G1/G2 dikerjakan per-modul secara independen** — modul yang satu
  boleh lanjut ke fase berikutnya walau modul lain belum selesai fase yang sama, KECUALI kalau step 9
  (dev testing) butuh ketiganya ter-install bersamaan untuk verifikasi cross-module
  (`pos_margin_threshold` ⟷ `sale_margin_threshold`, lihat `FINDINGS.md` project 17.0→18.0/18.0→19.0
  `MF-03` — kemungkinan masih relevan di 20.0, cek ulang, jangan diasumsikan otomatis sama).
- `pin_message` **tidak ada keterkaitan fungsional** dengan dua modul margin — bisa dikerjakan/
  di-review sepenuhnya independen kalau lebih efisien, tapi tetap satu project/branch/doc-dev yang
  sama sesuai keputusan scope awal (konsisten project sebelumnya).

---

## Adaptasi dual-branch (bukan dual-clone)

Model standar migration-tool: `source-codebase` dan `target-codebase` adalah dua clone fisik
terpisah (lihat `migration-tool/ai-doc/USAGE_GUIDE.md` §0). Project ini **melanjutkan pola yang
sama seperti dua project sebelumnya** — source dan target adalah dua branch di repo yang sama:

| Peran | Branch | Catatan |
|---|---|---|
| Source (19.0) | `migration/19.0` | Read-only referensi — **AI TIDAK PERNAH `git checkout` ke branch ini** (akan mengganti working tree `target-codebase` yang sedang dipakai). Baca isi file versi 19.0 lewat `git show migration/19.0:<path>` atau `git diff migration/20.0 migration/19.0 -- <path>`, bukan checkout. Branch ini sudah lulus 10 dari 11 step migrasi 18.0→19.0 (UAT sign-off menunggu eksekusi manual manusia — lihat `git log migration/19.0`) — jadi kode di branch ini adalah baseline 19.0 yang SUDAH terverifikasi lewat Step 1-10, bukan cuma "port kode belum ditest". 4 finding pre-existing (`MF-20`/`21`/`23`/`24`) masih terbuka di branch itu (sengaja dibiarkan sesuai keputusan dev), sudah dibawa ke `FINDINGS.md` project ini — jangan dianggap gap baru kalau ketemu lagi. |
| Target (20.0) | `migration/20.0` | Working branch aktif project ini — semua kerja Step 1-11 terjadi di sini. Dibuat 2026-09-21 via `git checkout -b migration/20.0` dari tip `migration/19.0` (Mode Git, isi awal identik `migration/19.0` di commit `5876d01`). |

**Konsekuensi ke Mode Git:** larangan permanen Mode Git tetap berlaku penuh (tidak ada `push`/merge/
force-push di manapun). Tidak ada `source-codebase` fisik terpisah — prosedur "Bootstrap Branch
Source & Target via Mode Git" (`USAGE_GUIDE.md`) dijalankan dalam varian dual-branch, bukan
dual-clone.

**Konfig yang diwarisi saat bootstrap (2026-09-21):** `.claude/settings.json` yang diwarisi dari
`migration/19.0` masih varian DRAFT `settings.json.mode-git.template` dengan placeholder
`{{ABS_PATH_...}}` belum terisi (hasil bootstrap-cli-config yang dijalankan ulang untuk project baru
ini) — **sudah diisi ulang** sesi ini dengan path nyata untuk pasangan 19.0→20.0 (lihat §Folder di
bawah), termasuk membuang entry `deny` milik folder referensi project sebelumnya (`odoo18`,
`enterprise19.0` sebagai native-target lama) yang tidak lagi relevan sebagai native-target, tapi
`enterprise19.0` DIPERTAHANKAN sebagai `native-source` (Community+Enterprise 19.0 gabungan, masih ada
di disk, dipakai untuk cross-check langsung ke versi asal di Step 2). `.claude/skills/` (Odoo's Skill
Library resmi — `odoo-guidelines`, `odoo-web-guidelines`, `odoo-security`, `odoo-review`) sudah
terpasang sebagai bagian bootstrap ini, dipakai wajib di Step 6 (implementasi)/Step 8 (code review) —
lihat §"Skill review/security/guideline" di bawah.

---

## Source of Truth & Forbidden Actions (WAJIB DIPATUHI)

**Source of truth:** kode 19.0 yang berjalan di branch `migration/19.0` adalah kebenaran mutlak.
Semua business logic, workflow, side effect, dan UX di 20.0 **harus identik** dengan 19.0 —
termasuk bug yang sudah ada di sana (jangan diperbaiki, dipertahankan, KECUALI bug itu sendiri sudah
ditandai `[DIWARISI-SOURCE]`/resolved di `FINDINGS.md` — cek dulu sebelum menganggap sesuatu "bug
lama yang harus dipertahankan", terutama `MF-08` yang SUDAH ada keputusan eksplisit dev untuk
dipertahankan, bukan diperbaiki).

**Dilarang** (kecuali eksplisit disetujui & dicatat sebagai perubahan yang disengaja di intake):
- Menambah atau menghapus fitur
- Mengubah business rule, workflow, atau state transition
- Memperbaiki bug yang sudah ada di 19.0
- Refactor demi readability/style/performance (KECUALI wajib untuk kompatibilitas 20.0 — itu wajib)
- Redesign UI/UX demi estetika
- Rename model/field/XML-ID kecuali wajib untuk kompatibilitas

**Kapan STOP dan eskalasi ke user** (jangan lanjut dengan asumsi):
- Perubahan mungkin mempengaruhi business logic
- Fitur deprecated di 20.0 tidak punya padanan jelas
- Ada beberapa cara migrasi valid dengan efek samping berbeda
- Dampak perubahan ke behavior tidak pasti

Format eskalasi:
```
ESCALATION — Migrasi 20.0
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
2. `migration-tool/knowledge/version-diffs/19-to-20.md` — constraint teknis umum. **Sudah ada entry
   dari project migrasi 19.0→20.0 pertama lewat tool ini (`optional_field_save`)** — termasuk isu
   SEVERITY TERTINGGI soal `/web/session/logout` (405 kalau modul me-replace total registry
   `user_menuitems["log_out"]` dan masih navigasi manual via GET), rename `ir.model.access.csv`
   →`ir.access.csv`, dan ACL baru `res.partner` write-self untuk `base.group_user`. **Grep dulu
   ketiga modul untuk pola-pola ini di Step 2** sebelum menyimpulkan tidak relevan.
3. `migration-tool/knowledge/dependency-compat/sale_report/18-to-19.md` (kalau masih relevan — cek
   dulu apakah ada entry `19-to-20.md` yang lebih baru) — kalau modul menyentuh
   `sale.order.line`/`sale.report`.
4. `01_intake/<modul>/01b_BASELINE_SPEC.md` (kalau sudah ada) — apa yang modul lakukan
5. `FINDINGS.md` (root `doc/`) — sudah diisi 5 finding pre-existing (`MF-08`/`20`/`21`/`23`/`24`)
   dibawa dari project 18.0→19.0, daftar gap/bug/ambiguitas lintas modul yang masih terbuka
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
| 6 | Code migration | kode di `target-codebase` (branch `migration/20.0`) + `06c_IMPLEMENTATION_LOG.md` | Tidak (disiplin per-fase A1→G2 wajib) |
| 7 | Data migration scripts | **N/A — port kode saja (asumsi, belum dikonfirmasi ulang), tidak dikerjakan** | — |
| 8 | Code review | `08_CODE_REVIEW.md` | **Ya** |
| 9 | Dev testing | `09_DEV_TESTING.md` | **Ya** |
| 10 | QA testing | `10_BUSINESS_FLOW_MIGRATION.md` | **Ya** |
| 11 | UAT sign-off | `11_UAT_CHECKLIST.md` | **Ya** — sign-off final |

Cross-cutting, satu file untuk ketiga modul (lihat §"Adaptasi multi-modul"):
- `PROMPT_LOG.md` — update tabelnya di akhir tiap giliran/sesi.
- `FINDINGS.md` — update begitu step manapun (1-11), modul manapun, menemukan gap/bug/ambiguitas
  yang butuh keputusan manusia. Prefix judul finding dengan nama modul.

**Aturan paling penting:** `03_MIGRATION_SPEC.md` memandu implementasi kode. Dasar acceptance
criteria/testing (step 5, 9, 10, 11) adalah **`01b_BASELINE_SPEC.md`** dan kode 19.0 yang berjalan
(branch `migration/19.0`) — BUKAN migration spec.

**Phase discipline (step 6):** eksekusi HANYA scope fase yang sedang berjalan
(`06a_CODE_MIGRATION_PHASES.md`). Applicability Check wajib sebelum Fase A dimulai. Urutan
A1→A2→A3→A4→A5→B1→B2→C1→C2→D1→D2→E→F→G2. Checkpoint G1 diulang setelah A2 dan A3. **E (JavaScript)
wajib selesai penuh sebelum F (Template)**.

---

## Skill review/security/guideline (`.claude/skills/`)

Odoo's Skill Library resmi sudah terpasang di `.claude/skills/` (sumber: agentskills.io/odoo,
diinstall ulang saat bootstrap 2026-09-21) — WAJIB dipakai, bukan opsional, di titik berikut:

| Skill | Dipakai wajib di | Cakupan |
|---|---|---|
| `odoo-review` | Step 8 (Code Review) — entry point utama, dispatch otomatis ke 3 skill lain | Review diff/PR/module lintas Python/XML/JS, termasuk "code the diff never shows" (override, rename, shared contract Python↔JS) |
| `odoo-guidelines` | Step 6 (semua fase A-G) & Step 8 | Semua file di luar `static/` — manifest, ORM, fields, controllers, XML views/data, QWeb reports, access rights, performance, tests |
| `odoo-web-guidelines` | Step 6 fase E (JavaScript)/F (Template) & Step 8 | Semua file di bawah `static/` — JS, Owl template, SCSS, hoot tests. Relevan terutama untuk `pos_margin_threshold` (POS frontend) dan `pin_message` (Discuss/chatter frontend) |
| `odoo-security` | Step 8 (bagian dari `odoo-review`) + Step 2/3 kalau ada perubahan `security/`/`sudo()`/route baru | Access control (`ir.access`, field groups, `sudo()`), injection (SQL/domain/eval/XSS), controller auth/CSRF, RPC-callable method |

**Cara pakai konkret:** begitu Step 8 (Code Review) diminta, invoke `odoo-review` (bukan review
manual) — skill itu sendiri akan membaca `odoo-guidelines`/`odoo-web-guidelines`/`odoo-security`
sesuai file yang berubah. Ini menggantikan template `08_CODE_REVIEW.md` sebagai *proses*, dokumen
`08_CODE_REVIEW.md` tetap ditulis sebagai *output*-nya (laporan gate).

---

## Status saat ini

**Step 1 (Intake & Scope) — draft SUDAH DITULIS untuk ketiga modul (2026-09-21), gate BELUM
ditutup.** `01a_MIGRATION_INTAKE.md` + `01b_BASELINE_SPEC.md` ditulis lewat 3 agent riset paralel
(satu per modul), masing-masing cross-check langsung ke baseline `01b_BASELINE_SPEC.md` project
18.0→19.0 sebelumnya + kode 19.0 aktual (branch ini) + `native-target`/`native-target-enterprise`
(`odoo20`/`enterprise20`). Tally klaim `BSL-NNN`: `pos_margin_threshold` 22 (19 `[MATCH]`/1 `[GAP]`/
2 `[NO-SPEC]`), `sale_margin_threshold` 19 (16/1/2), `pin_message` 17 (12/2/3).

**4 finding BARU ditemukan saat cross-check, sudah dicatat ke `FINDINGS.md` (`MF-25`..`MF-28`):**
- **`MF-28` [pin_message] — KRITIS.** Native 20.0 `mail.message` **tidak punya `_to_store()` lagi**
  (diganti `_store_message_fields()`/`Store.FieldList`) — fix `MF-14`/`MF-15`/`MF-18` dari project
  18.0→19.0 (yang mengasumsikan method itu tetap ada, cuma signature beda) TIDAK RELEVAN lagi untuk
  20.0. Override modul ini butuh rewrite arsitektural, bukan port mekanis. **WAJIB jadi riset
  prioritas #1 Step 2** untuk modul ini — jangan mulai Step 6 fase manapun untuk `pin_message`
  sebelum ini diriset tuntas. Ditulis juga sebagai kandidat knowledge base ke
  `migration-tool/migration-records/pos-margin-sale_19.0_20.0/SUMMARY.md`.
- **`MF-25` [pos_margin_threshold]/`MF-27` [sale_margin_threshold]** — dua instance BARU dari pola
  `MF-24` (`position="replace"` pada field harga yang diam-diam menghapus atribut core), belum
  pernah dicatat sebelumnya walau sudah ada sejak project sebelumnya.
- **`MF-26` [sale_margin_threshold]** — singleton-assumption bug KEDUA (beda method dari `MF-08`) di
  `_compute_is_rental_order_installed`.
- **`MF-08` mekanismenya dikoreksi** (bukan keputusannya) — bukti eksekusi `doc-dev/backfill/`
  (`F-05`, baru ketahuan Step 1 project ini, belum pernah dirujuk 2 project migrasi sebelumnya)
  menunjukkan ini genuinely **hard crash** (`ValueError: Expected singleton`), bukan "silent skip"
  seperti tercatat sebelumnya. Keputusan "dipertahankan" tetap tidak berubah.

**Gate Step 1 belum ditutup — perlu konfirmasi eksplisit dari kamu atas 4 asumsi carried-forward**
(sudah ditulis di draft sebagai asumsi, bukan fakta terkonfirmasi, konsisten di ketiga modul):
1. Sifat migrasi = **port kode saja** (bukan upgrade instance)
2. Source (`migration/19.0`) **tidak** aktif dikembangkan selama migrasi ini
3. **Tidak ada** dependency third-party/OCA untuk ketiga modul
4. **Tidak ada** dokumen pelengkap lain (manual/PRD/spec lama) di luar baseline spec project
   sebelumnya — *koreksi kecil*: `pin_message`/`sale_margin_threshold` agent menemukan
   `doc-dev/backfill/` (characterization test lama, 17.0) yang belum pernah dirujuk eksplisit di 2
   project migrasi sebelumnya — sudah dipakai sebagai bukti pendukung `MF-08` di atas, tapi
   konfirmasi ke kamu: apakah ada dokumen/test lain di luar ini yang belum diketahui AI?

**✔️ GATE STEP 1 LULUS untuk ketiga modul (2026-09-21).** Dev konfirmasi lanjut dengan ke-4 asumsi
carried-forward di atas apa adanya (port kode saja, source tidak aktif dikembangkan, tidak ada
dependency OCA, tidak ada dokumen pelengkap lain di luar `doc-dev/backfill/` yang sudah ditemukan) —
tidak ada koreksi.

**Step 2 (Diff & Compatibility Analysis) — SELESAI untuk ketiga modul (2026-09-21, tidak ada gate),
via 3 agent riset paralel.** 6 finding baru ditemukan dan dicatat ke `FINDINGS.md` (`MF-29`..`MF-34`):

- **`MF-29` [pos_margin_threshold][sale_margin_threshold] — KRITIS, lintas-modul.** View
  `product.product_variant_easy_edit_view` **dihapus total** di native 20.0 (dikonfirmasi grep
  penuh, 0 match, termasuk versi core `stock`-nya sendiri) — kedua modul akan gagal install kalau
  di-port apa adanya. **Butuh keputusan desain dev sebelum Step 3** (kandidat pengganti:
  `product.product_normal_form_view`, tapi itu form penuh bukan popup). Ditulis ke
  `migration-records/pos-margin-sale_19.0_20.0/SUMMARY.md` sebagai kandidat knowledge base.
- **`MF-30` [pos_margin_threshold][sale_margin_threshold]** — `ir.model.access.csv`→`ir.access.csv`,
  fix mekanis (rename + reformat 1 baris), tidak perlu keputusan dev.
- **`MF-31` [pos_margin_threshold]** — anchor view `stock_account.view_category_property_form_stock`
  pindah ke `account.view_category_property_form`, fix satu baris.
- **`MF-32` [pin_message]** — `messageActionsRegistry` berubah lagi (getter `canAddReaction`, filter
  `IS_ACTION_DEFINITION_SYM`, ikon FontAwesome→Odoo Icons `push_pin`), fix mekanis diketahui untuk
  ketiganya.
- **`MF-33` [pin_message]** — komponen `Chatter` di-rewrite arsitektural, WAJIB tour test nyata di
  Step 6/9, jangan diasumsikan aman dari baca kode saja.
- **`MF-34` [pos_margin_threshold]** — `line.comboParent` kemungkinan no-op, TAPI tidak bisa
  dipastikan murni gap 19→20 karena **`native-source` (`enterprise19.0`) ternyata folder KOSONG di
  disk** — perlu dev refill folder itu untuk verifikasi tuntas (blocker infrastruktur, bukan cuma
  keputusan konten).

**`MF-28` (pin_message, `_to_store()` hilang) — SOLUSI DITEMUKAN, bukan lagi blocker.** Pola
pengganti `_store_message_fields()` + `res.attr("is_pinned")`, diverifikasi dari 2 override native
yang sudah berjalan (`rating`, `im_livechat`) — siap dieksekusi mekanis di Step 6.

**`MF-29` — keputusan desain diambil dev (2026-09-21):** pindah customization margin dari popup
(hilang) ke kolom baru di list Product Variants (`product_product_tree_view`), `optional="show"`,
replikasi pola koordinasi lintas-modul (`module_pos_margin_threshold`) yang sudah ada.

**Step 3 (Migration Spec) — SELESAI untuk ketiga modul (2026-09-22, tidak ada gate).** Spec konkret
ditulis untuk semua fix wajib (lihat `03_spec/<modul>/03_MIGRATION_SPEC.md`).

**Review visual Docker 19.0 vs 20.0 (2026-09-22) — atas permintaan dev, sebagian eksekusi Step 6
dini di luar urutan fase normal:**
- Dua environment Docker independen dibuat: 19.0 (`docker-compose.yml`, port 8079, mount clone
  terpisah `pos-margin-sale-19.0-snapshot` — **jangan pernah mount `../` langsung di sini**, insiden
  pernah terjadi saat working tree yang sama dipakai bareng compose 20.0) dan 20.0
  (`docker-compose.20.yml`, port 8078, build dari source `odoo20`+`enterprise20` karena belum ada
  image resmi `odoo:20.0`). `sale_renting` (Enterprise Rental) terinstall di kedua sisi dari
  `enterprise19`/`enterprise20` untuk verifikasi `BSL-001` — **dikonfirmasi identik** (order Rental
  skip validasi margin di kedua versi).
- **`pos_margin_threshold`:** `DIFF-01`/`DIFF-02`/`DIFF-03`(`MF-29`) diterapkan & diverifikasi
  install sukses di 20.0. `DIFF-04` (options currency `list_price`) **dikonfirmasi dev & diterapkan
  2026-09-22** — diverifikasi tidak ada beda visual di data instance ini (single-currency), murni
  jaga-jaga kompatibilitas.
- **`sale_margin_threshold`:** `DIFF-01`(`MF-30`)/`DIFF-08`(`MF-29`) diterapkan. **`MF-35` (baru,
  ditemukan dari smoke-install, bukan Step 2/3)** — `views/sale_order.xml` xpath `price_unit` tidak
  resolve karena native 20.0 membungkusnya dalam `<column name="price_unit">` baru — **sudah
  diperbaiki & diverifikasi**.
- **`pin_message`:** `MF-28`/`MF-32`/`MF-33`/`DIFF-04` semua diterapkan & **diverifikasi end-to-end
  via UI nyata** (tulis log note → klik pin → badge "Pinned Messages: 1" muncul benar). **`MF-36`
  (baru)** — crash di komponen NATIVE `mail.MessageCardList` (bukan kode modul ini, dikonfirmasi
  dari baca langsung hasil kompilasi template) saat expand daftar pesan pinned — kemungkinan quirk
  dev-snapshot Odoo 20.0 (belum ada rilis stabil), direkomendasikan re-test nanti, BUKAN ditambal
  dari sisi modul.

**`MF-37` (baru, ditemukan+RESOLVED 2026-09-22) — kolom Margin/Minimum sale price dobel di list
Product Variants 20.0.** Efek samping `MF-29`: `pos_margin_threshold` dan `sale_margin_threshold`
sama-sama inherit `product.product_product_tree_view` dan menambah field bernama sama. Fix:
`sale_margin_threshold/views/products.xml` diberi marker `class="o_smt_dedup_*"` pada field-nya,
lalu `ProductProduct._get_view()` (baru, `sale_margin_threshold/models/product.py`) strip node itu
spesifik lewat xpath kalau `pos_margin_threshold` terinstall — kolom `pos_margin_threshold` jadi
satu-satunya yang tampil, sesuai desain `MF-29`. **Diverifikasi bersih di Docker 20.0** (1 set kolom,
nilai terisi benar). Percobaan awal `column_invisible="module_pos_margin_threshold == True"` gagal
(tidak ada record context di evaluasi `column_invisible`) — detail lengkap + lesson proses (restart
container wajib setelah edit file `.py`, `-u <module>` di proses terpisah tidak cukup) di
`FINDINGS.md` `MF-37` dan `06_implementation/sale_margin_threshold/06c_IMPLEMENTATION_LOG.md`.

**`MF-38` (baru, ditemukan+RESOLVED 2026-09-22) — visual parity popup 19.0 vs kolom list 20.0.**
Kolom list `MF-29` tidak membawa 2 elemen visual yang ada di popup 19.0: warna merah saat
`margin_sale` negatif, dan kolom "Incl. Tax" (`minimum_sale_price_with_tax`). **Dikonfirmasi dev
2026-09-22** (dijustifikasi `CLAUDE.md` §Source of Truth: "UX di 20.0 harus identik dengan 19.0"),
diterapkan di KEDUA modul (`pos_margin_threshold` dan `sale_margin_threshold`, karena kolom
`pos_margin_threshold` yang jadi satu-satunya tampil saat keduanya terinstall bersamaan, hasil dedup
`MF-37`) — field baru `minimum_sale_price_with_tax` ditambahkan ke `ProductProduct` di kedua modul,
kolom baru `sale_margin_threshold` diberi marker dedup `MF-37` juga supaya tidak dobel. Diverifikasi
live: margin negatif tampil merah, kolom Incl. Tax terisi benar, tidak dobel. Detail lengkap +
catatan efek samping (`ProductProduct._load_pos_data_fields()` di `pos_margin_threshold` sudah sejak
19.0 mereferensikan field ini padahal sebelumnya belum ada) di `FINDINGS.md` `MF-38` dan kedua
`06c_IMPLEMENTATION_LOG.md`.

**`MF-34` — RESOLVED, diperbaiki (2026-09-22).** Dev mengisi ulang `native-source` sebagai `odoo19`
(Community) + `enterprise19` (Enterprise), dua clone terpisah. Cross-check ke native
`point_of_sale/static/src/app/components/orderline/orderline.js` (19.0 DAN 20.0), **diperdalam lagi
sampai branch `17.0`** atas permintaan dev, mengonfirmasi: `line.comboParent` di
`pos_margin_threshold/static/src/store/orderline.xml` adalah **typo original sejak modul pertama
kali ditulis** (branch `17.0`, dikonfirmasi via `git show 17.0:...`) — seharusnya
`line.combo_parent_id`, field asli yang dipakai native. **Keputusan dev: PERBAIKI** (bukan
pertahankan) — sudah diterapkan, `line.comboParent` → `line.combo_parent_id`, dengan komentar XML
(bahasa Inggris) menjelaskan asal rename. Styling combo-child (indent+border kiri) AKTIF untuk
pertama kalinya di 20.0 — perubahan behavior yang terlihat dibanding SEMUA versi sebelumnya, sudah
disetujui eksplisit. Diverifikasi: XML well-formed + update modul bersih; verifikasi visual live di
POS (combo product sungguhan) BELUM dilakukan (DB QA belum ada chart of accounts/config POS),
ditunda ke Step 9. Detail di `FINDINGS.md` `MF-34`.

**Step 4 (Spec Completeness Review) — SELESAI untuk ketiga modul (2026-09-22), gate LULUS setelah
sinkronisasi.** Dikerjakan via 3 agent riset paralel, masing-masing enumerasi PENUH file source
19.0 (`git ls-tree` di branch `migration/19.0`) dicocokkan ke `03_MIGRATION_SPEC.md` + kode aktual.
Ketiga review awalnya **FAIL** (spec drift — banyak fix Step 6 dini sesi ini belum di-backport ke
dokumen spec) — semua gap dokumentasi sudah disinkronkan, gate sekarang **LULUS** untuk
`pos_margin_threshold`/`pin_message`.

**Temuan PALING PENTING Step 4 — `MF-36` root cause DIKOREKSI.** Finding lama menyebut crash saat
expand "Pinned Messages" sebagai "100% native, `pin_message` tidak pernah menyentuh
`message_card_list.js`/`.xml`" — **klaim itu SALAH**. Agent Step 4 menemukan modul ini PUNYA override
`message_card_list.xml` (xpath-replace tombol "Jump") dengan bug bare-identifier IDENTIK `MF-33`
(`ui.isSmall` bukan `this.ui.isSmall`) — CSS class di override cocok persis dengan baris crash di
stack trace. Diperbaiki & diverifikasi live (expand + klik "See" jump, 0 error console). `FINDINGS.md`
`MF-36` sudah dikoreksi root cause-nya (bukan sekadar ditandai resolved — investigasi awal genuinely
salah, bukan cuma belum tuntas).

**Satu item masih terbuka, butuh keputusan dev:** `sale_margin_threshold` — `i18n/*.po` (5 file
bahasa) belum pernah dicek kelengkapan terjemahannya terhadap string UI baru (kolom "Incl. Tax" dst,
`MF-29`/`MF-38`). Perlu keputusan: in-scope (update terjemahan) atau eksplisit out-of-scope untuk
migrasi "port kode saja" ini — lihat `doc-dev/migration_19.0_20.0/doc/04_completeness/sale_margin_threshold/04_SPEC_COMPLETENESS_REVIEW.md`.

**Belum dikerjakan:** Step 5 (Acceptance Criteria & Test Plan) untuk ketiga modul. Step 6 belum
resmi menjalankan Applicability Check penuh (Fase A→G) — fix di atas dieksekusi dini/parsial di luar
urutan normal atas permintaan dev, akan direview ulang sebagai bagian gate Step 6 formal nanti.

---

**Bootstrap selesai (2026-09-21).** Branch `migration/20.0` belum di-push ke remote (dev perlu
jalankan sendiri `git push -u origin migration/20.0` kapan pun siap — AI tidak pernah melakukan
ini). Yang sudah dikerjakan sesi ini:

- Branch `migration/20.0` dibuat dari tip `migration/19.0` (commit `5876d01`).
- `.claude/settings.json` diisi path referensi nyata: `native-target` = `D:\Kuncoro\doodex\repo\odoo20`
  (Community, clone git resmi, branch `20.0`), `native-target-enterprise` =
  `D:\Kuncoro\doodex\repo\enterprise20` (Enterprise, clone git resmi, branch `20.0` — **dua clone
  TERPISAH kali ini, bukan folder gabungan seperti `enterprise19.0` di project sebelumnya**),
  `native-source` = `D:\Kuncoro\doodex\repo\enterprise19.0` (Community+Enterprise 19.0 gabungan,
  peninggalan project 18.0→19.0, bukan git repo — JANGAN jalankan git di sana).
- `doc-dev/migration_19.0_20.0/doc/` di-scaffold (10 step folder × 3 modul, `07_data/` sengaja
  dilewati karena asumsi port-kode-saja) + `FINDINGS.md` (5 finding pre-existing dibawa dari
  18.0→19.0) + `PROMPT_LOG.md`.
- `CLAUDE.md` ini diinstansiasi dari `migration-tool/templates/CLAUDE_TEMPLATE.md`.
- `.claude/skills/` (odoo-guidelines/odoo-web-guidelines/odoo-security/odoo-review — Odoo's Skill
  Library resmi) dikonfirmasi terpasang lengkap (4 skill + guideline files pendukungnya).

**Belum dikerjakan / blocker Step 1:** lihat 4 poin konfirmasi di ringkasan paling atas — itu
satu-satunya yang tersisa sebelum gate Step 1 ditutup dan lanjut ke Step 2.

> AI: update bagian ini sendiri di akhir tiap sesi kerja, supaya sesi berikutnya tahu persis harus
> lanjut dari mana tanpa tanya ulang ke user.

### Status per Step (per modul)

| # | Step | pos_margin_threshold | sale_margin_threshold | pin_message |
|---|---|---|---|---|
| 1 | Intake & Scope | ✔️ Gate lulus (2026-09-21) | ✔️ Gate lulus (2026-09-21) | ✔️ Gate lulus (2026-09-21) |
| 2 | Diff & Compatibility Analysis | ✅ Selesai — 1 kritis lintas-modul (`MF-29`) | ✅ Selesai — 1 kritis lintas-modul (`MF-29`) | ✅ Selesai — `MF-28` solusi ditemukan, `MF-32`/`33` fix diketahui |
| 3 | Migration Spec | ✅ Selesai — 2 item nunggu konfirmasi dev | ✅ Selesai — 2 detail visual parity nunggu konfirmasi | ✅ Selesai — mekanis, `MF-33` jadi syarat tour test Step 6 |
| 4 | Spec Completeness Review | ✔️ Gate lulus (2026-09-22, setelah sinkronisasi spec) | 🟡 Gate hampir lulus — 1 item nunggu keputusan dev (`i18n`) | ✔️ Gate lulus (2026-09-22) — `MF-36` root cause dikoreksi + fix |
| 5 | Acceptance Criteria & Test Plan | ⬜ Belum mulai | ⬜ Belum mulai | ⬜ Belum mulai |
| 6 | Code Migration | 🔄 Sebagian (`DIFF-01/02/03/04`+`MF-34/38` diterapkan; `MF-34` verifikasi visual live ditunda Step 9) | 🔄 Sebagian (`DIFF-01/08`+`MF-35/37/38` diterapkan+diverifikasi Docker) | 🔄 Sebagian (`MF-28/32/33/36`+`DIFF-04` semua diterapkan+diverifikasi Docker, tidak ada lagi item native yang ditunda) |
| 7 | Data Migration Scripts | — (asumsi N/A) | — (asumsi N/A) | — (asumsi N/A) |
| 8 | Code Review | ⬜ Belum mulai | ⬜ Belum mulai | ⬜ Belum mulai |
| 9 | Dev Testing | ⬜ Belum mulai | ⬜ Belum mulai | ⬜ Belum mulai |
| 10 | QA Testing | ⬜ Belum mulai | ⬜ Belum mulai | ⬜ Belum mulai |
| 11 | UAT Sign-off | ⬜ Belum mulai | ⬜ Belum mulai | ⬜ Belum mulai |

Legenda: ⬜ Belum mulai · 🔄 Sedang dikerjakan · ✅ Draft/selesai ditulis · ✔️ Disetujui/lulus gate.

---

## Folder yang perlu di-connect

| Folder | Perlu di step | Read-only? | Status |
|---|---|---|---|
| `target-codebase` (repo ini, branch `migration/20.0`) | Semua step | Tidak | Sudah connect (folder utama) |
| `migration-tool` | Semua step (baca template/knowledge; tulis ke `migration-records/` saja) | Tulis di `migration-records/` saja | Sudah connect |
| Source 19.0 | 1, 2, 4, 8 | Ya | **Tidak ada folder terpisah** — baca lewat `git show migration/19.0:<path>` di repo yang sama (lihat §"Adaptasi dual-branch") |
| `native-target` (Odoo 20.0 Community) | 2 | Ya | **Sudah ada, dikonfirmasi 2026-09-21:** `D:\Kuncoro\doodex\repo\odoo20` — clone git resmi `odoo/odoo`, branch `20.0` |
| `native-target-enterprise` (Odoo 20.0 Enterprise) | 2 (wajib — `sale_margin_threshold` punya dependency Rental) | Ya | **Sudah ada, dikonfirmasi 2026-09-21:** `D:\Kuncoro\doodex\repo\enterprise20` — clone git resmi Enterprise, branch `20.0`. **Folder TERPISAH dari `native-target`** (pola dua-clone standar, bukan gabungan seperti project 18.0→19.0) — pastikan KEDUANYA dicek untuk dependency Enterprise, jangan asumsikan cukup dari Community saja (lesson `purchase_product_optional`). |
| `native-source` (Odoo 19.0) | 2 | Ya | **Diisi ulang dev 2026-09-22** (folder lama `enterprise19.0` kosong, sempat memblokir `MF-34`) — sekarang DUA clone terpisah: `D:\Kuncoro\doodex\repo\odoo19` (Community, clone git resmi, branch `19.0`) + `D:\Kuncoro\doodex\repo\enterprise19` (Enterprise, clone git resmi, branch `19.0`) — pola dua-clone standar, bukan folder gabungan seperti `enterprise19.0` lama. Sudah dipakai untuk cross-check `MF-34` (`line.comboParent`), hasil: dikonfirmasi typo lama, bukan gap migrasi. |
| `third-party-*` | 2 (kalau ada dependency OCA) | Ya | Belum dicek ulang untuk pasangan 19.0→20.0 — project 18.0→19.0 tidak menemukan indikasi OCA untuk ketiga modul, tapi harus dikonfirmasi ulang di intake, bukan diasumsikan permanen. |

---

## Knowledge base

Sebelum step 2 mulai analisis, cek `migration-tool/knowledge/INDEX.md` — entry 19.0→20.0 **SUDAH
ADA** (`knowledge/version-diffs/19-to-20.md`, ditambahkan dari project `optional_field_save`, pasangan
versi 19→20 pertama lewat tool ini — lihat ringkasan di §"Mandatory Read Order" di atas). Entry
`sale_report`/`sale.order.line` dependency-compat yang ada masih berlabel `18-to-19.md` — cek apakah
masih relevan atau perlu entry `19-to-20.md` baru.

Temuan baru (general Odoo atau dependency-specific) ditulis ke
`migration-tool/migration-records/pos-margin-sale_19.0_20.0/SUMMARY.md` saat itu juga (folder belum
ada, buat saat temuan pertama muncul) — **bukan** langsung ke `migration-tool/knowledge/`. Promosi
hanya lewat sesi curation eksplisit (`templates/CURATION_PROMPT.md`).

---

## Referensi

- Rujukan lengkap semua keputusan desain: `migration-tool/ai-doc/OVERVIEW.md`
- Arah lintas-fase: `migration-tool/ai-doc/ROADMAP.md`
- Langkah operasional + Mode Git: `migration-tool/ai-doc/USAGE_GUIDE.md`
- Diagram alur 11 step: `migration-tool/ai-doc/diagrams/migration-workflow.svg`
- Project migrasi sebelumnya (17.0→18.0, 11/11 step lulus): `CLAUDE.md` di branch `migration/18.0`
- Project migrasi sebelumnya (18.0→19.0, 10/11 step lulus — UAT sign-off manual menunggu eksekusi
  manusia): `CLAUDE.md` di branch `migration/19.0`
