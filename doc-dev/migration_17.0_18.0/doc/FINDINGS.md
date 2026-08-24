# Findings — pos-margin-sale (migrasi 17.0 → 18.0, multi-module)

> **Cross-cutting, direkomendasikan (tidak kondisional)** — dokumen konsolidasi TUNGGAL untuk semua
> gap/bug/ambiguitas yang butuh keputusan manusia selama migrasi, untuk KETIGA modul
> (`pos_margin_threshold`, `sale_margin_threshold`, `pin_message`) — lihat adaptasi multi-modul di
> `CLAUDE.md` root. Diadaptasi dari `migration-tool/templates/FINDINGS.md`.

**Modul:** `pos_margin_threshold`, `sale_margin_threshold`, `pin_message` (satu file, prefix modul di
tiap judul finding)
**Migrasi:** 17.0 → 18.0
**Terakhir update:** 2026-08-24 (bootstrap, belum ada finding)

---

## Beda Peran dari Mekanisme Lain (jangan bingung/duplikat)

| Mekanisme | Kapan dipakai | Sifat |
|---|---|---|
| Format `ESCALATION` (`CLAUDE.md`) | Isu **blocking** — butuh keputusan user SEBELUM lanjut ke step/fase berikutnya | Sinkron, muncul di respons AI saat itu juga |
| Tag `[GAP]` di `01b_BASELINE_SPEC.md` (per modul) | Penyimpangan spec lama vs kode aktual, per-klaim `BSL-NNN` | Inline, granular per klaim |
| Section Gap di `04_SPEC_COMPLETENESS_REVIEW.md` / `08_CODE_REVIEW.md` (per modul) | Gap spesifik di titik gate itu | Inline, per dokumen |
| **`FINDINGS.md` (file ini)** | **Semua finding lintas step (1-11) DAN lintas modul yang butuh keputusan manusia** — satu tempat, direview batch | Living document, append-only |

**Aturan penomoran:** ID `MF-NNN` (Migration Finding) sequential lintas KETIGA modul (bukan reset
per modul), judul WAJIB diberi prefix modul: `MF-01 [pos_margin_threshold] — ...`.

**Catatan penting — modul ini juga pernah lewat `doc-dev/backfill`:** ketiga modul punya
`doc-dev/backfill/FINDINGS.md` (branch `backfill/17.0`) dengan ID `F-01`..`F-07` miliknya sendiri
(termasuk F-01/F-02 soal interaksi runtime `pos_margin_threshold` ⟷ `sale_margin_threshold`, dan
F-05 soal `sale_margin_threshold.action_confirm` memecah batch-confirm Odoo core). **Cek dulu file
itu sebelum mencatat finding baru** — kalau finding di migrasi ini sebenarnya pewarisan dari F-NNN
backfill, buat `MF-NNN` yang mereferensikan `F-NNN` aslinya secara eksplisit (tag
`[DIWARISI-SOURCE]`), jangan dicatat ulang dari nol.

---

## Ringkasan

| ID | Judul | Modul | Ditemukan di Step | Tag | Prioritas | Status |
|---|---|---|---|---|---|---|
| MF-01 | | | | | | |

---

## Detail

*(belum ada finding — diisi begitu step manapun, modul manapun, menemukan gap/bug/ambiguitas yang
butuh keputusan manusia. Format satu entry, lihat `migration-tool/templates/FINDINGS.md` §Detail
untuk template lengkap per-field.)*

---

## Cara Pakai

1. Update SETIAP KALI step manapun (1-11), modul manapun, menemukan gap/bug/ambiguitas yang butuh
   keputusan manusia — jangan tunggu akhir project.
2. Tag: `[PERLU-KEPUTUSAN]` / `[DIWARISI-SOURCE]` (termasuk pewarisan dari `doc-dev/backfill/F-NNN`)
   / `[GAP-MIGRASI]` (genuinely muncul karena perubahan platform 18.0).
3. Step 4 dan Step 8 (tiap modul) WAJIB baca file ini sebagai bagian gate.
4. Update status (bukan hapus) begitu keputusan diambil — tandai `✅ RESOLVED`/`✅ CONFIRMED` + tanggal
   + bukti.
