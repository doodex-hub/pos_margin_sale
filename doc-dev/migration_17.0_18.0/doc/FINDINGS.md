# Findings — pos-margin-sale (migrasi 17.0 → 18.0, multi-module)

> **Cross-cutting, direkomendasikan (tidak kondisional)** — dokumen konsolidasi TUNGGAL untuk semua
> gap/bug/ambiguitas yang butuh keputusan manusia selama migrasi, untuk KETIGA modul
> (`pos_margin_threshold`, `sale_margin_threshold`, `pin_message`) — lihat adaptasi multi-modul di
> `CLAUDE.md` root. Diadaptasi dari `migration-tool/templates/FINDINGS.md`.

**Modul:** `pos_margin_threshold`, `sale_margin_threshold`, `pin_message` (satu file, prefix modul di
tiap judul finding)
**Migrasi:** 17.0 → 18.0
**Terakhir update:** 2026-08-24 (Step 1 `pos_margin_threshold` — 3 finding diwarisi dari backfill + 1 temuan baru)

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
| MF-01 | `margin_sale` per-variant tidak bisa divergen — inverse menulis ke template shared | pos_margin_threshold | 1 | `[DIWARISI-SOURCE]` `[PERLU-KEPUTUSAN]` | Sedang | Terbuka — belum ada keputusan pemilik modul |
| MF-02 | `blocking_transaction_order` dideklarasikan tapi tidak berefek sendirian | pos_margin_threshold | 1 | `[DIWARISI-SOURCE]` `[PERLU-KEPUTUSAN]` | Rendah | Terbuka |
| MF-03 | Model `wizard.margin.product`: kelas `pos_margin_threshold` hilang total dari MRO saat 2 modul terinstall | pos_margin_threshold + sale_margin_threshold | 1 | `[DIWARISI-SOURCE]` `[PERLU-KEPUTUSAN]` | Sedang | Terbuka |
| MF-04 | `views/product_template_views.xml` dead file, duplikat XML-ID dengan `views/products.xml` | pos_margin_threshold | 1 | `[DIWARISI-SOURCE]` | Rendah | Terbuka — baru ditemukan, belum ada di backfill |

---

## Detail

### MF-01 — `margin_sale` per-variant TIDAK BISA divergen — inverse menulis ke template (shared)
**Ditemukan di:** Step 1 (2026-08-24) — diwarisi dari `doc-dev/backfill/FINDINGS.md` **F-01** (branch `backfill/17.0`, terkonfirmasi eksekusi Docker 2026-07-31)
**Tag:** `[DIWARISI-SOURCE]` `[PERLU-KEPUTUSAN]`
**Ref:** `BSL-011` (`01_intake/pos_margin_threshold/01b_BASELINE_SPEC.md`), backfill `F-01`
**Lokasi:** `pos_margin_threshold/models/product.py` (`ProductProduct._set_product_margin_sale`, inverse method)
**Deskripsi:** Field `margin_sale` di `ProductProduct` punya inverse sendiri tapi menulis ke `product_tmpl_id` (template, shared semua variant) — margin TIDAK PERNAH bisa berbeda antar variant satu template, walau field-nya terlihat "milik variant sendiri". Detail lengkap: lihat backfill `F-01`.
**Dampak di 18.0:** Belum diketahui apakah mekanisme compute/inverse Odoo 18.0 berubah caranya bekerja — kalau tidak berubah (kemungkinan besar, ini API `fields.Float` dasar), quirk ini tetap identik. WAJIB dicek ulang di Step 2, jangan diasumsikan otomatis sama.
**Rekomendasi:** Sama seperti backfill — kalau margin per-variant genuinely diinginkan, perlu perubahan bisnis (di luar scope migrasi port-kode-saja). Kalau margin selalu dimaksudkan sama, field ini redundant.
**Keputusan pemilik modul:** *(kosong — diisi manusia, sama dengan status backfill F-01)*

---

### MF-02 — `blocking_transaction_order` dideklarasikan di `pos_margin_threshold` tapi tidak berefek sendirian
**Ditemukan di:** Step 1 (2026-08-24) — diwarisi dari `doc-dev/backfill/FINDINGS.md` **F-02**
**Tag:** `[DIWARISI-SOURCE]` `[PERLU-KEPUTUSAN]`
**Ref:** `BSL-012`, backfill `F-02`
**Lokasi:** `pos_margin_threshold/models/res_config_settings.py:8`
**Deskripsi:** Field dideklarasikan tapi tidak ditampilkan di view settings modul ini dan tidak dibaca kode modul ini — baru bermakna kalau `sale_margin_threshold` juga terinstall.
**Dampak di 18.0:** Rendah, murni dead weight kalau modul ini diinstall sendirian — tidak ada risiko teknis migrasi (field Boolean sederhana, tidak depend API yang berubah).
**Rekomendasi:** Sama seperti backfill — pertimbangkan pindahkan deklarasi ke `sale_margin_threshold` saja, ATAU dokumentasikan eksplisit alasan duplikasi. Di luar scope migrasi port-kode-saja kecuali disetujui eksplisit.
**Keputusan pemilik modul:** *(kosong)*

---

### MF-03 — Model `wizard.margin.product`: kelas `pos_margin_threshold` hilang total dari MRO saat 2 modul terinstall
**Ditemukan di:** Step 1 (2026-08-24) — diwarisi dari `doc-dev/backfill/FINDINGS.md` **F-03** (terkonfirmasi eksekusi Docker, `tests/test_cross_module.py`)
**Tag:** `[DIWARISI-SOURCE]` `[PERLU-KEPUTUSAN]`
**Ref:** `BSL-013`, backfill `F-03`
**Lokasi:** `pos_margin_threshold/wizard/wizard_margin_product.py:4-31`, `sale_margin_threshold/wizard/wizard_margin_product.py:4-31` (byte-identik)
**Deskripsi:** Kedua modul mendefinisikan `_name = 'wizard.margin.product'` tanpa `_inherit`. `__mro__` final hanya berisi kelas dari modul yang diinstall lebih belakangan — kelas modul lain hilang total, bukan digabung.
**Dampak di 18.0:** Sedang — aman selama kedua kelas byte-identik. Risiko utama BUKAN dari perubahan platform 18.0 (ini mekanisme registry model Odoo/Python, kemungkinan tidak berubah), tapi dari perubahan kode salah satu modul saja saat migrasi (mis. `pos_margin_threshold` di-migrasi duluan dengan penyesuaian kode, `sale_margin_threshold` belum) — silent-override bisa menyembunyikan perubahan yang belum lengkap.
**Rekomendasi:** Saat migrasi KEDUA modul, pastikan wizard di kedua modul diubah BERSAMAAN dan tetap byte-identik (atau eksplisit konsolidasi jadi `_inherit` dari satu ke lainnya — itu perubahan struktural, minta persetujuan eksplisit dulu karena berpotensi dianggap "refactor" yang dilarang `CLAUDE.md` §Forbidden Actions kecuali wajib untuk kompatibilitas 18.0).
**Keputusan pemilik modul:** *(kosong)*

---

### MF-04 — `views/product_template_views.xml` dead file, duplikat XML-ID dengan `views/products.xml`
**Ditemukan di:** Step 1 (2026-08-24) — **BARU**, tidak ada di `doc-dev/backfill/FINDINGS.md` (belum pernah tercatat sebelumnya)
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `BSL-014` (`01_intake/pos_margin_threshold/01b_BASELINE_SPEC.md`)
**Lokasi:** `pos_margin_threshold/views/product_template_views.xml` (seluruh file), vs `pos_margin_threshold/views/products.xml` (record `product_template_inherit_pos_margin_threshold`)
**Deskripsi:** `product_template_views.xml` tidak terdaftar di `data:` manifest — dead file, tidak pernah dimuat Odoo di 17.0. File ini mendefinisikan XML-ID yang **identik** (`product_template_inherit_pos_margin_threshold`) dengan yang didefinisikan `products.xml`, tapi dengan `inherit_id` target berbeda (`product.product_template_only_form_view` vs `product.product_template_form_view`) dan struktur visibility field yang sedikit berbeda (versi di `product_template_views.xml` tidak punya kondisi `invisible` untuk multi-variant, versi di `products.xml` punya).
**Dampak di 18.0:** Rendah selama tetap dead file. **Risiko kalau ditambahkan ke manifest tanpa disadari** (mis. saat migrasi seseorang "membersihkan" dan tidak sadar file ini sengaja tidak dimuat) — akan clash XML-ID langsung dengan `products.xml` saat modul di-install, kemungkinan besar error saat load data atau salah satu record menimpa yang lain tergantung urutan load.
**Rekomendasi:** Pertahankan sebagai dead file yang sama persis di 18.0 (JANGAN didaftarkan ke manifest sebagai bagian dari migrasi — itu perubahan fungsional yang butuh persetujuan eksplisit, di luar "port kode saja").
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

## Cara Pakai

1. Update SETIAP KALI step manapun (1-11), modul manapun, menemukan gap/bug/ambiguitas yang butuh
   keputusan manusia — jangan tunggu akhir project.
2. Tag: `[PERLU-KEPUTUSAN]` / `[DIWARISI-SOURCE]` (termasuk pewarisan dari `doc-dev/backfill/F-NNN`)
   / `[GAP-MIGRASI]` (genuinely muncul karena perubahan platform 18.0).
3. Step 4 dan Step 8 (tiap modul) WAJIB baca file ini sebagai bagian gate.
4. Update status (bukan hapus) begitu keputusan diambil — tandai `✅ RESOLVED`/`✅ CONFIRMED` + tanggal
   + bukti.
