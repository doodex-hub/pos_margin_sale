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

**Ringkasan cepat (2026-08-26):** Step 1-9 selesai ketiga modul (lihat detail Tour test di bawah).
Step 7 N/A. **Step 8 (Code Review) dan Step 9 (Dev Testing) LULUS GATE untuk ketiga modul** — lihat
ringkasan di bawah. **Belum dikerjakan: Step 10-11.**

**Step 9 — Dev Testing (gate, LULUS ketiganya, 2026-08-26):** menutup 3 gap yang ditandai Step 8 lewat
test baru (audit stub `ast`-based dulu — semua test lama TERKONFIRMASI real, tidak ada stub), lalu
re-run test suite penuh (`docker compose down -v` + up bersih).
- **`pos_margin_threshold`:** Tour baru `test_pos_margin_threshold_below_minimum_blocked_tour`
  (AC-02-01, jalur `blocking_transaction_pos=True`/`AlertDialog`) — **"tour succeeded"**.
- **`pin_message`:** Tour baru `test_pin_message_action_menu_pin_visible_tour` (AC-02-02) —
  **membuktikan fix `MF-24` (Step 8) benar-benar membuat entry menu "Pin" muncul di UI** (hover
  message → klik quick-action/dropdown "Pin" → badge jadi 1), bukan cuma test suite tidak error.
  **"tour succeeded".**
- **`sale_margin_threshold`:** test MRO baru di sisi modul ini sendiri (`AC-04-02`) — **dan dites
  EMPIRIS DUA urutan install** (`-i pos_margin_threshold,sale_margin_threshold` standar DAN dibalik
  `-i sale_margin_threshold,pos_margin_threshold`, database test terpisah). **Temuan penting:** premis
  asli `MF-03`/`AC-04-02` ("MRO tergantung urutan install") **TERBUKTI SALAH** — hasil MRO IDENTIK di
  kedua urutan, `sale_margin_threshold` SELALU menang, `pos_margin_threshold` SELALU hilang dari
  `__mro__`, independen urutan CLI. `05a_MIGRATION_ACCEPTANCE_CRITERIA.md` (`pos_margin_threshold` DAN
  `sale_margin_threshold`) sudah dikoreksi teksnya untuk mencerminkan mekanisme sebenarnya. Risiko
  `MF-03` (silent-override kalau salah satu modul diubah sendirian) tetap sama, cuma penjelasannya
  yang diperbaiki.
- **Hasil akhir gabungan (fresh DB, ketiga modul + 4 test baru, SEBELUM `MF-21` di-fix):**
  `0 failed, 1 error(s) of 22 tests` (naik dari 19 — 3 test baru berhasil ditambah tanpa regresi).
- **`pin_message` AC-03-01** (Discuss-channel native pin) juga dikoreksi di `05a` — premis lama
  ("memicu `onClickPin()` override modul") sudah tidak berlaku di 18.0 (`MF-09`, dead code tapi
  harmless, lihat Step 8), diganti jadi "lewat mekanisme native 18.0".

**`MF-21` — RESOLVED lewat fix kode (2026-08-26, lanjutan sesi Step 9 yang sama):** user menegaskan
bahasa Prancis di production **tidak bisa dijamin selalu terinstall** — modul tidak boleh
mensyaratkan itu. `sale_margin_threshold/models/sale_order.py` cabang wizard (baris 41-43) diperbaiki:
dulu double-write (`create()` + `.with_context(lang='fr_FR').write()`) yang butuh `fr_FR` genuinely
terinstall (validasi baru `Environment.lang` 18.0), sekarang SATU `create()` yang langsung pilih
`message_Fr`/`message` sesuai `user_language` terdeteksi — pola yang SUDAH ADA persis sama di cabang
blocking (baris 33-37) file yang sama, tidak pernah butuh translated-field/`with_context(lang=...)`.
Behavior yang terlihat user (pesan sesuai bahasa) tidak berubah, cuma mekanisme internal. Tidak ada
lagi referensi `fr_FR` di modul ini. **Re-verifikasi: `0 failed, 0 error(s) of 22 tests`, TANPA
`--load-language=fr_FR` sama sekali** — bersih total, semua 4 Tour test tetap "tour succeeded".
`docker-env/docker-compose.yml` komentarnya diperbarui (flag itu sekarang benar-benar tidak pernah
perlu dipasang lagi, bukan cuma "jarang").

**Step 8 — Code Review (gate, LULUS ketiganya, 2026-08-24):** dikerjakan lewat 3 agent paralel
(gather diff+gap-analysis+core-collision-check per modul, real `git diff backfill/17.0 HEAD`, cross-
check langsung terhadap source Odoo 17.0/18.0 di image `pos_margin_sale_migration_18-odoo:latest`),
lalu sintesis manual jadi `08_review/<modul>/08_CODE_REVIEW.md`.
- **`pos_margin_threshold`:** 0 issue baru, diff 100% terjustifikasi ke `MF-NN` yang sudah ada. Gap
  terbuka (bukan bug, cuma belum ada test): AC-02-01 (jalur blocking `AlertDialog`), AC-02-03/04,
  AC-03-01/02 (wizard) — sudah didokumentasikan sejak Step 6, ditegaskan lagi sebagai kandidat Step 9.
- **`sale_margin_threshold`:** 0 issue baru, diff cuma 2 baris dari 17.0 (version bump + `<tree>`→
  `<list>`). Nuansa baru soal `MF-21`: kemungkinan mekanisme bilingual EN/FR modul ini SUDAH silently
  broken di 17.0 kalau Prancis tidak pernah terinstall (18.0 mengubah silent-fail jadi crash eksplisit,
  bukan bug baru) — ditambahkan ke rekomendasi konfirmasi dev. Gap test terbuka: AC-01-04 (rental,
  tidak bisa dites di environment Community), AC-03-02, AC-04-02, AC-04-03.
- **`pin_message`:** **1 bug fungsional nyata ditemukan DAN DIPERBAIKI dalam review ini sendiri**
  (`MF-24`) — `pinMessage.js`'s `condition` action-menu "Pin" memanggil `component.canAddReaction`
  (getter 17.0 di component `Message`), yang di 18.0 dipindah jadi method di message MODEL
  (`message.canAddReaction(thread)`) — selalu `undefined` di 18.0, `condition` selalu `false`, entry
  menu "Pin" TIDAK PERNAH render, sejak awal migrasi, tanpa error apapun (Tour test lolos karena
  sengaja pakai tombol inline `pinnedMessages.xml`, bukan jalur ini). **Diperbaiki** (`component.message.canAddReaction(component.props.thread)`,
  idiom sama seperti core sendiri) **dan diverifikasi ulang** — re-run `docker compose down -v` +
  test suite penuh, kedua Tour test tetap "tour succeeded". Juga: `MF-09` (Discuss-channel
  `onClickPin`/`messagePinService`) dikonfirmasi **harmless** lewat cross-check source 17.0/18.0
  langsung — cabang ini jadi dead code di 18.0 tapi Discuss-channel pinning tetap berfungsi penuh
  lewat mekanisme native 18.0, tidak ada fitur hilang untuk end-user.
- **Tidak ada tabrakan nama method/field dengan Odoo core** di ketiga modul (dicek 2 arah, langsung
  terhadap source real, bukan asumsi).

**Milestone terbesar sesi ini — Mode D (Chrome asli di Docker) berhasil dipasang dan dipakai untuk
verifikasi interaktif nyata**, bukan cuma install test. `docker-env/Dockerfile` diinstansiasi
(`google-chrome-stable` + `websocket-client`), `docker-compose.yml` pakai `build: .` +
`shm_size: 2gb`. Ini menemukan `pos_margin_threshold` DAN `pin_message` punya masalah JAUH lebih
dalam dari perkiraan awal Step 2 — **G1 (install) PASS padahal fitur JS-nya rusak total** untuk
keduanya — baru ketahuan dari Tour test:

- **`pos_margin_threshold` — root cause:** Odoo 18.0 memindahkan SELURUH arsitektur data POS
  (`Order`/`Orderline`/`Product` → `PosOrder`/`PosOrderline`/`ProductProduct` di path baru,
  `@point_of_sale/app/store/models` jadi file KOSONG 0-byte). Method-level API tetap byte-identik
  (kabar baik), tapi class name/path/entry-point semua pindah. **6 finding kritis
  ditemukan+diperbaiki+diverifikasi** (`MF-13`, `MF-15`..`MF-20`, lihat `FINDINGS.md` detail lengkap):
  popup service dihapus, class model dipindah, `Order.pay()` tidak lagi dipanggil tombol Pay (pindah
  ke `PosStore.pay()`), loader field custom pindah API (`_load_pos_data_fields`), Owl `Orderline`
  component validasi strict props shape, xpath `orderline.xml` butuh descendant bukan direct-child.
  **Diverifikasi PENUH lewat Tour test nyata** (`pos_margin_threshold/static/tests/tours/margin_threshold_tour.js`
  + companion `.py`) — Chrome asli benar-benar klik: buka POS → jual produk di bawah minimum → dialog
  muncul dengan pesan benar → confirm → bayar → sukses.
- **`pin_message` — root cause:** mekanisme lama untuk membawa field custom (`is_pinned`) ke frontend
  lewat full-override `Chatter.load()` sudah tidak berfungsi (`this.threadService` dihapus di 18.0).
  **2 finding kritis ditemukan+diperbaiki+diverifikasi** (`MF-22`: `load()` override dihapus total,
  digantikan pola baru `MF-23`: Python `mail.message._to_store()` override), plus 2 fix sebelumnya
  yang sudah ada dari G2 (`MF-12` import path chatter, `MF-14` xpath `message_card_list.xml`).
  **Diverifikasi PENUH lewat Tour test nyata** (`pin_message/static/tests/tours/pin_message_tour.js`
  + companion `.py`) — Chrome asli benar-benar klik: tulis log note → pin lewat tombol inline →
  section Pinned Messages muncul dengan badge & message card → unpin → section hilang.
  **Jalur Discuss channel (`messagePinService`, `MF-09`/DIFF-06, risiko tertinggi project ini) BELUM
  ada Tour test** — kandidat lanjutan Step 9, bukan blocker Step 8 (jalur log note yang paling umum
  dipakai sudah terverifikasi penuh).
- **Hasil akhir gabungan (re-run bersih, `docker compose down -v`, ketiga modul + kedua Tour test
  sekaligus):** `tour succeeded` untuk `pos_margin_threshold` dan `pin_message`, **0 failed, 1
  error(s) of 19 tests** — 1 error itu `MF-21` (`sale_margin_threshold`), tidak terkait dua modul lain.
- **`sale_margin_threshold` `MF-21`:** Odoo 18.0 `Environment.lang` sekarang validasi ketat bahasa
  terinstall; modul ini pakai teknik bilingual EN/FR yang butuh bahasa Prancis genuinely terinstall
  di database (dikonfirmasi BUKAN bug kode, tapi butuh konfirmasi dev untuk environment production).
- **Lesson environment penting (jangan diulang):** `--load-language=fr_FR` di `docker-compose.yml`
  (dipasang sementara untuk verifikasi `MF-21`) sempat bocor jadi bahasa DEFAULT SELURUH SESI server
  (bukan cuma satu user), menyamar sebagai regresi Tour test `pos_margin_threshold` (modal "Open
  Register" ter-render Prancis, xpath teks tidak match). Root-cause via screenshot (`docker cp` dari
  container exited). **Fix permanen:** flag dihapus dari `docker-compose.yml` (lihat komentar di
  file itu, hanya dipasang manual sekali kalau `MF-21` perlu re-verifikasi), dan tour text-based
  dialog matcher diubah language-agnostic di kedua tour (`Dialog.confirm()` tanpa argumen teks).

**Kandidat knowledge base sudah ditulis:** `migration-tool/migration-records/pos-margin-sale_17.0_18.0/SUMMARY.md`
(ditulis sebelum `MF-22`/`MF-23` ditemukan — dev sudah commit manual sekali, mungkin perlu entry
tambahan untuk `MF-22`/`MF-23`, belum diminta eksplisit oleh dev).

**Belum dikerjakan:** Step 10 (QA Testing, gate) → 11 (UAT, gate) untuk ketiga modul. Tidak ada lagi
item wajib-konfirmasi-dev tersisa (`MF-21` sudah RESOLVED). Gap risiko rendah yang didokumentasikan
eksplisit (bukan blocker gate manapun, tapi disarankan ditutup manual kalau ada waktu di QA):
`pos_margin_threshold` AC-02-03/04 (kontrol negatif + assert visual), AC-03-01/02 (wizard UI, kode
0-diff dari 17.0); `sale_margin_threshold` AC-01-04 (rental, tidak bisa dites di environment
Community sama sekali), AC-03-02 (wizard cancel), AC-04-03 (UI field visibility); `pin_message`
AC-02-01 (native Discuss pin) dan AC-04-02 (reload ganti record).

> AI: update bagian ini sendiri di akhir tiap sesi kerja, supaya sesi berikutnya tahu persis harus
> lanjut dari mana tanpa tanya ulang ke user.

### Status per Step (per modul)

| # | Step | pos_margin_threshold | sale_margin_threshold | pin_message |
|---|---|---|---|---|
| 1 | Intake & Scope | ✔️ Gate lulus (2026-08-24) | ✔️ Gate lulus (2026-08-24) | ✔️ Gate lulus (2026-08-24) |
| 2 | Diff & Compatibility Analysis | ✅ Draft selesai (2026-08-24) | ✅ Draft selesai (2026-08-24) | ✅ Draft selesai (2026-08-24) |
| 3 | Migration Spec | ✅ Draft selesai (2026-08-24) | ✅ Draft selesai (2026-08-24) | ✅ Draft selesai (2026-08-24) |
| 4 | Spec Completeness Review | ✔️ Gate lulus (2026-08-24) | ✔️ Gate lulus (2026-08-24) | ✔️ Gate lulus (2026-08-24) |
| 5 | Acceptance Criteria & Test Plan | ✅ Draft selesai (2026-08-24) | ✅ Draft selesai (2026-08-24) | ✅ Draft selesai (2026-08-24) |
| 6 | Code Migration | ✅ Selesai, Tour test PASS | ✅ Selesai (G1/G2 + `MF-21` dikonfirmasi) | ✅ Selesai, Tour test PASS (jalur log note; Discuss channel belum) |
| 7 | Data Migration Scripts | — (N/A, port kode saja) | — | — |
| 8 | Code Review | ✔️ Gate lulus (2026-08-24) | ✔️ Gate lulus (2026-08-24) | ✔️ Gate lulus (2026-08-24) — 1 bug baru (`MF-24`) ditemukan+diperbaiki+diverifikasi dalam review |
| 9 | Dev Testing | ✔️ Gate lulus (2026-08-26) | ✔️ Gate lulus (2026-08-26) — `MF-03` dikonfirmasi order-independent | ✔️ Gate lulus (2026-08-26) — `MF-24` fix diverifikasi end-to-end di UI |
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
