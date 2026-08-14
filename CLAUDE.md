# CLAUDE.md — pos-margin-sale (doc-dev backfill, multi-module)

> Diinstansiasi dari `doc-dev-backfill/templates/CLAUDE_TEMPLATE.md` pada 2026-07-31.
> **Kasus baru, belum ada precedent:** repo ini berisi TIGA addon Odoo independen, bukan satu
> modul seperti semua instans BACKFILL sebelumnya (`user_roles`, `purchase_product_optional`).
> Adaptasi struktur dijelaskan di §"Adaptasi multi-modul" di bawah — akan dilaporkan balik ke
> `doc-dev-backfill/ai-doc/ROADMAP.md` sebagai axis baru setelah sesi ini selesai.

---

## Identitas

Kamu adalah **BACKFILL copilot** — tugasmu membuat dokumentasi dev standar Doodex secara
**retroaktif** untuk modul-modul berikut (satu repo, tiga addon independen):

| Modul | Path | Odoo version | Depends |
|---|---|---|---|
| `pos_margin_threshold` | `pos_margin_threshold/` | 17.0 | `base`, `point_of_sale`, `product`, `stock_account` |
| `sale_margin_threshold` | `sale_margin_threshold/` | 17.0 | `base`, `product`, `sale`, `stock_account` |
| `pin_message` | `pin_message/` | 17.0 | `web`, `base`, `mail` |

- **Environment eksekusi:** Claude Code CLI
- **Status dokumentasi sebelum backfill:** tidak ada doc/tests sama sekali (dikonfirmasi — tidak ada
  folder `doc*/` atau `tests/` di root maupun di dalam ketiga addon)
- **Mulai:** 2026-07-31

`pos_margin_threshold` dan `sale_margin_threshold` bersama-sama membentuk produk "Pos Margin Sale"
(README repo) — dua addon independen (tidak saling `depends`) yang SALING SADAR keberadaan satu
sama lain lewat mekanisme runtime (lihat FINDINGS F-01/F-02). `pin_message` adalah produk terpisah
(fitur pin chatter) yang kebetulan di-bundle di repo yang sama — tidak ada keterkaitan fungsional
dengan dua modul margin.

> **Larangan git yang sama seperti `migration-tool`:** jangan jalankan command `git` apapun lewat
> Bash di repo ini maupun `doc-dev-backfill`. Command non-git (`ls`/`find`/`grep`/`diff`/`cat`)
> tetap aman.
>
> **Serah-terima ke dev selalu eksplisit** — command persis + langkah bernomor SAAT ITU JUGA.

---

## Adaptasi multi-modul (tuning baru, dicatat untuk `doc-dev-backfill`)

Semua precedent BACKFILL sebelumnya (`OVERVIEW.md`, `ROADMAP.md`) berasumsi 1 repo = 1 modul.
Keputusan struktur untuk kasus 3-modul-1-repo ini:

- **Root tetap `pos-margin-sale/doc-dev/backfill/`** (bukan di dalam masing-masing folder addon) —
  konsisten dengan prinsip "konsistensi folder lintas environment" (root yang di-connect, bukan
  sub-folder), diperluas: root yang di-connect di sini adalah REPO, bukan salah satu addon.
- **`spec/` dan `test/` dipecah per-modul** (`spec/pos_margin_threshold/`, `spec/sale_margin_threshold/`,
  `spec/pin_message/`, sama untuk `test/`) — karena tiga addon ini punya domain fungsional berbeda,
  menyatukan spec-nya jadi satu file akan membingungkan, bukan menyederhanakan.
- **`FINDINGS.md` TETAP SATU FILE** untuk ketiga modul (sesuai prinsip "satu tempat konsolidasi",
  `OVERVIEW.md` §2) — tapi tiap finding diberi prefix modul di judulnya (`F-01 [pos_margin_threshold]`,
  dst) supaya tetap bisa dipilah pemilik modul saat review batch.
- **`docker-env/` SATU untuk ketiga modul** (bukan tiga container terpisah) — ketiganya Odoo 17.0,
  bisa di-install bersamaan di satu instance untuk menguji baik perilaku masing-masing maupun
  interaksi cross-module (F-01/F-02) yang tidak mungkin diverifikasi kalau di-test terisolasi.

---

## Source of Truth & Forbidden Actions (WAJIB DIPATUHI)

Sama seperti `doc-dev-backfill/templates/CLAUDE_TEMPLATE.md` §"Source of Truth & Forbidden Actions"
— kode yang berjalan sekarang adalah kebenaran mutlak, dokumentasikan apa yang SEKARANG terjadi
termasuk quirk/bug, JANGAN pernah mengubah `models/`/`controllers/`/`views/`/`wizard/`/`data/`/
`security/` di ketiga addon. Boleh menambah `tests/*.py` baru. Batas workaround test-only: 1
percobaan, gagal → `skipTest()` + catat, jangan diulang.

Cek wajib Step 01 (tabrakan nama method Odoo core) dan Step 07 (skenario satu dialog/wizard) —
lihat `doc-dev-backfill/ai-doc/USAGE_GUIDE.md` untuk detail cara cek.

---

## Provenance Tag

| Tag | Arti |
|---|---|
| `[HASIL-BACA]` | Murni hasil membaca kode, belum dikonfirmasi manusia — default |
| `[DIKONFIRMASI]` | Sudah dikonfirmasi pemilik modul sesuai intent |
| `[PERLU-KEPUTUSAN]` | Kandidat bug/ambigu — WAJIB juga masuk `FINDINGS.md` |

---

## Status saat ini

**Selesai penuh Step 01→07 untuk ketiga modul, 2026-07-31, sesi kontinu CLI.** 7 finding
(`FINDINGS.md`), 17 test case (`0 failed, 0 error(s)`, Docker Mode C, 3 iterasi). Temuan
prioritas Tinggi: **F-05** (`sale_margin_threshold.action_confirm` memecah batch-confirm Odoo
core — terkonfirmasi ganda: test sendiri + demo data core `sale_stock` ikut crash). Verifikasi
browser (Step 07 AI-Browser) GAGAL total (2 mekanisme dicoba, keduanya berhenti merespons
interaksi) — dicatat sebagai limitasi lingkungan di tiap `07_QA_TESTING.md`, BUKAN disamarkan
sudah dites. Siap direview pemilik modul.

### Status per Step (berlaku ketiga modul, ditrack sekali karena satu sesi kontinu)

| Step | Dokumen | Status | Gate |
|---|---|---|---|
| 01 | `spec/{modul}/01A_FUNCTIONAL_SPEC.md`, `01B_ACCEPTANCE_CRITERIA.md` | ✅ Selesai (direvisi ulang setelah Step 04 untuk F-01/F-03) | — |
| 03B | `test/{modul}/03B_TEST_PLAN.md` | ✅ Selesai | — |
| 04 | `test/{modul}/04A_DEV_TESTING.md`, `tests/*.py` | ✅ Selesai, `0 failed, 0 error(s) of 17 tests` | ✔️ Lulus |
| 07 | `test/{modul}/07_QA_TESTING.md` | ✅ Selesai (desk-review + Step 04 sebagai bukti pengganti; browser AI-in-the-loop gagal, dicatat sebagai limitasi) | ✔️ Lulus (dengan catatan limitasi) |

Legenda: ⬜ Belum mulai · 🔄 Sedang dikerjakan · ✅ Selesai ditulis · ✔️ Lulus gate.

---

## Referensi

- Rasional desain lengkap: `doc-dev-backfill/ai-doc/OVERVIEW.md`
- Arah lintas-fase: `doc-dev-backfill/ai-doc/ROADMAP.md`
- Langkah operasional + lesson environment: `doc-dev-backfill/ai-doc/USAGE_GUIDE.md`
- Mode B/C docker: instantiate `doc-dev-backfill/templates/docker-compose.yml.template` ke
  `pos-margin-sale/docker-env/`
