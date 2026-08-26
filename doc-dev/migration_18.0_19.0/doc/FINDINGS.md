# Findings — pos_margin_threshold / sale_margin_threshold / pin_message (migrasi 18.0 → 19.0)

> **Cross-cutting, direkomendasikan (tidak kondisional)** — dokumen konsolidasi TUNGGAL untuk semua
> gap/bug/ambiguitas yang butuh keputusan manusia selama migrasi, supaya user tidak perlu buka
> `01b_BASELINE_SPEC.md`/`03_MIGRATION_SPEC.md`/`04_SPEC_COMPLETENESS_REVIEW.md`/`08_CODE_REVIEW.md`
> satu per satu untuk tahu apa yang masih terbuka. Hidup di root `doc/` (sejajar `PROMPT_LOG.md`) —
> bukan milik satu step tertentu. Lihat `migration-tool/templates/FINDINGS.md` untuk penjelasan
> lengkap beda peran dari `ESCALATION`/`[GAP]`/section Gap per-dokumen.

**Modul:** `pos_margin_threshold`, `sale_margin_threshold`, `pin_message` (tiga addon independen —
lihat §"Adaptasi multi-modul" di `CLAUDE.md`, sama seperti project migrasi 17.0→18.0 sebelumnya di
repo ini).
**Migrasi:** 18.0 → 19.0
**Terakhir update:** 2026-08-26 (bootstrap, belum ada finding baru — lihat §"Kandidat finding dari
knowledge base" di bawah untuk hal yang sudah diketahui dari project 18.0→19.0 lain lewat
`migration-tool` dan wajib dicek ulang di Step 2).

Prefix judul finding dengan nama modul (`MF-01 [sale_margin_threshold]`, dst) supaya tetap bisa
dipilah pemilik modul saat review batch (konsisten pola `FINDINGS.md` project 17.0→18.0 di
`migration/18.0`).

---

## Ringkasan

| ID | Judul | Ditemukan di Step | Tag | Prioritas | Status |
|---|---|---|---|---|---|
| MF-01 | | | | | |

---

## Kandidat finding dari knowledge base (WAJIB diverifikasi ulang di Step 2, jangan diasumsikan otomatis)

`migration-tool/knowledge/version-diffs/18-to-19.md` dan
`migration-tool/knowledge/dependency-compat/sale_report/18-to-19.md` sudah punya entry dari project
migrasi 18.0→19.0 pertama lewat tool ini (`advanced_sales_analysis`) — relevan untuk modul di project
ini:

- **`sale.order.line.tax_id` → `tax_ids` (rename, breaking, kolom DB ikut berubah).** Berpotensi
  relevan untuk `sale_margin_threshold` (baca/tulis field di `sale.order.line`) — WAJIB dicek langsung
  di Step 2 apakah modul ini menyentuh field ini (baca kode, jangan asumsikan dari nama field margin
  saja).
- Model `sale.report`/`sale.order.line` lain (`_select_additional_fields()`, `_group_by_sale()`)
  dikonfirmasi byte-stable 18.0↔19.0 di project itu — tidak otomatis berarti stable untuk cara modul
  ini pakai, cek ulang sesuai kode aktual.

Catat sebagai `MF-NNN` begini ditemukan berlaku/tidak berlaku untuk modul ini, jangan cuma dirujuk di
sini tanpa verdict.

---

## Detail

*(belum ada finding — diisi begitu Step 1 mulai menemukan gap)*

---

## Cara Pakai

1. **Update SETIAP KALI step manapun (1-11), modul manapun, menemukan gap/bug/ambiguitas yang butuh
   keputusan manusia** — jangan tunggu sampai akhir project.
2. ID `MF-NNN` sequential lintas ketiga modul (satu skema penomoran, prefix modul di judul).
3. Tag: `[PERLU-KEPUTUSAN]` / `[DIWARISI-SOURCE]` (bug/quirk yang sudah ada di 18.0, harus
   dipertahankan identik) / `[GAP-MIGRASI]` (genuinely muncul karena perubahan platform 19.0).
4. Step 4 dan Step 8 (per modul) WAJIB baca file ini sebagai bagian gate.
5. Update status (bukan hapus) begitu keputusan diambil/finding resolved — histori tetap terbaca.
