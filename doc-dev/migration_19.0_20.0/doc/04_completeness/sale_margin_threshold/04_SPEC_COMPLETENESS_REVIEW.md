# Spec Completeness Review — sale_margin_threshold

**Step:** 4 — Spec Completeness Review (gate)
**Ref:** `03_spec/sale_margin_threshold/03_MIGRATION_SPEC.md`, source module `sale_margin_threshold` di
branch `migration/19.0` (`git ls-tree -r --name-only migration/19.0 -- sale_margin_threshold/`)
**Tanggal:** 2026-09-22

> Tujuan: pastikan `03_MIGRATION_SPEC.md` mencakup 100% elemen source module — bukan review kualitas
> kode (itu step 8). Setiap file/elemen dari source 19.0 dicek satu-satu terhadap spec, DAN
> terhadap kode aktual di working tree (`migration/20.0`) untuk menangkap spec-drift dari fix yang
> sudah diterapkan langsung ke kode (`MF-35`, `MF-37`, `MF-38`) tanpa disinkronkan balik ke dokumen
> spec.

---

## Tabel Cakupan

| Elemen source module | Ada di Migration Spec? | Status | Catatan |
|---|---|---|---|
| `__manifest__.py` (`version`, `data`) | Ya | ✅ Covered | §1 poin 1, §2 baris 1-3 |
| `__init__.py` (root) | Tidak eksplisit | ✅ Covered (implisit) | Import murni (`controllers`/`models`/`wizard`), byte-identik 19.0/20.0, tidak ada API versi terlibat |
| `controllers/__init__.py` | Tidak eksplisit | ✅ Covered (implisit) | Trivial, di bawah payung §2b "Controller & Route" |
| `controllers/controllers.py` | Ya | ✅ Covered | §2b "Controller & Route: Tidak ada — seluruhnya di-comment" |
| `demo/demo.xml` | Tidak | ❌ Gap (trivial) | Isi 100% ter-comment, byte-identik 19.0/20.0 (dikonfirmasi diff) — tidak ada risiko migrasi, tapi tidak pernah disebut eksplisit di spec manapun |
| `googleaeed8a7b9ec156e7.html` | Tidak | ❌ Gap (non-fungsional) | File verifikasi Google Site, tidak terkait logic modul, aman diabaikan |
| `i18n/ar_001.po`, `es.po`, `fr.po`, `id.po`, `pt.po` | Tidak | ❌ **Gap** | Tidak pernah disinggung di spec/finding manapun — string baru/berubah dari `DIFF-08`/`MF-29`/`MF-38` (kolom list "Incl. Tax", dst.) belum dicek kelengkapan terjemahannya. Lihat §Gap Baru di bawah. |
| `LICENSE` | Tidak | ❌ Gap (non-fungsional) | Static, tidak terkait migrasi |
| `LISEZMOI.md` | Tidak | ❌ Gap (non-fungsional) | Static readme, tidak terkait migrasi |
| `models/__init__.py` | Tidak eksplisit | ✅ Covered (implisit) | Trivial import, tidak berubah |
| `models/product.py` — `ProductCategory.margin_sale` | Tidak ada baris eksplisit | ✅ Covered (implisit, "sisanya murni port identik") | Field sederhana, tidak ada perubahan API versi yang relevan |
| `models/product.py` — `ProductTemplate` (semua field/compute/`action_assign_margin`) | Ya | ✅ Covered | §2 tabel baris `_register_hook()`/dst, §2b "Kompatibilitas Data Model" |
| `models/product.py` — `ProductProduct` field/compute existing (`margin_sale`, `minimum_sale_price`, `is_less_minimum_sale`, `_register_hook`) | Ya | ✅ Covered | §2 tabel, §2b |
| `models/product.py` — `ProductProduct._get_view()` (BARU di kode 20.0, mekanisme final fix `MF-37`) | **Tidak** di `03_MIGRATION_SPEC.md` | ❌ **Gap — spec drift** | Spec §2b "Risiko Integrasi" #2 menulis pendekatan dedup via `invisible="module_pos_margin_threshold == True"` pada field — pendekatan itu TERBUKTI GAGAL (`column_invisible` tanpa record context) dan diganti mekanisme Python (`_get_view()` override + marker `class="o_smt_dedup_*"`), didokumentasikan hanya di `FINDINGS.md` `MF-37`, tidak pernah disinkronkan balik ke `03_MIGRATION_SPEC.md`. Kode aktual sudah benar & terverifikasi Docker — ini murni gap dokumentasi, bukan gap kode. |
| `models/product.py` — `ProductProduct.minimum_sale_price_with_tax` (field baru, `MF-38`) | Ya | ✅ Covered | §2b bagian "Visual parity — DIKONFIRMASI DEV 2026-09-22, DITERAPKAN (`MF-38`)" |
| `models/res_config_settings.py` | Ya | ✅ Covered | §2 tabel (`DIFF-04`, tidak ada perubahan) |
| `models/sale_order.py` — `SaleOrder.action_confirm()` / `MF-08` | Ya | ✅ Covered | §2 tabel, §4 "Di Luar Scope" |
| `models/sale_order.py` — `_compute_is_rental_order_installed()` / `MF-26` | Ya | ✅ Covered | §2 tabel, §4 "Di Luar Scope" |
| `models/sale_order.py` — `SaleOrderLine.minimum_sale_price` (related field) | Tidak ada baris terpisah | ✅ Covered (implisit) | Field `related`, tidak ada API versi terlibat, di bawah payung umum "sale_order.py tidak berubah" |
| `security/groups.xml` (`implied_ids` / `MF-20`) | Ya | ✅ Covered | §2 tabel, §4 "Di Luar Scope" |
| `security/ir.model.access.csv` → `security/ir.access.csv` (`MF-30`/`DIFF-01`) | Ya | ✅ Covered | §2b spesifikasi persis (skema, isi CSV, entry manifest) — **dikonfirmasi cocok 100% dengan kode aktual** |
| `static/description/*` (banner, icon, assets `pos_17_step_*.png`, `index.html`) | Tidak | ❌ Gap (non-fungsional) | Aset marketing App Store, tidak terkait logic modul |
| `tests/__init__.py` | Tidak eksplisit | ✅ Covered (implisit) | Trivial import |
| `tests/test_action_confirm.py` | Ya | ✅ Covered | §2 tabel — "tidak ada perubahan kode wajib, tetap baseline eksekusi Step 9" |
| `tests/test_cross_module.py` | Ya | ✅ Covered | §2 tabel, sama seperti di atas |
| `views/product_template_views.xml` (`product_template_inherit_sale_margin_threshold`, inert `BSL-013`) | Ya | ✅ Covered | §2 tabel `DIFF-06` |
| `views/products.xml` — record `product_template_inherit_sale_margin_threshold` (inherit `product_template_form_view`) | Ya | ✅ Covered | §2 tabel `DIFF-05`, `MF-27` |
| `views/products.xml` — record `product_variant_easy_edit_view_margin_sale` → diganti `product_product_tree_view_margin_sale` | Ya | ✅ Covered | §2b spesifikasi persis (`DIFF-08`/`MF-29`) — **dikonfirmasi cocok dengan kode aktual**, termasuk 2 field visual-parity `MF-38` dan marker dedup `MF-37` |
| `views/products.xml` — 2 record `ir.actions.server` (`product_template_margin_sale_action_server`, `product_product_margin_sale_action_server`) | Tidak ada baris eksplisit | ✅ Covered (implisit) | `ref="model_product_template"`/`model_product_product"` masih resolve normal di 20.0, tidak ada rename model — di bawah payung "sisanya murni port identik" |
| `views/res_config_settings.xml` | Ya | ✅ Covered | §2 tabel `DIFF-10` |
| `views/sale_order.xml` (record `view_order_form_inherit_sale`) | **Tidak** — tidak pernah ada baris di §2 maupun §2b `03_MIGRATION_SPEC.md` | ❌ **Gap** | File ini TIDAK PERNAH masuk cakupan eksplisit Step 2/3 formal (dikonfirmasi juga oleh `FINDINGS.md` `MF-35` sendiri: *"file `views/sale_order.xml` tidak eksplisit masuk cakupan agent riset Step 2/3"*). Baru ketahuan lewat smoke-install Docker (2026-09-22, di luar Step 2/3), langsung diperbaiki (xpath `price_unit` dibungkus `<column>` baru) & diverifikasi install sukses. **Kode aktual sudah benar & terverifikasi**, tapi `03_MIGRATION_SPEC.md` tidak pernah diupdate untuk mencantumkan file ini — gap dokumentasi murni, bukan gap kode. |
| `wizard/sale_confirmation.py` | Ya | ✅ Covered | §2 tabel |
| `wizard/sale_confirmation.xml` | Ya (implisit, baris "wizard files") | ✅ Covered | §2 tabel |
| `wizard/wizard_margin_product.py` | Ya | ✅ Covered | §2 tabel, risiko integrasi #1 (`MF-03`/`BSL-015`) |
| `wizard/wizard_margin_product.xml` | Ya (implisit) | ✅ Covered | §2 tabel |

---

## Cross-check kode aktual vs spec (ringkasan)

Semua fix yang tercantum eksplisit di `03_MIGRATION_SPEC.md` (`DIFF-01`/`MF-30` rename security CSV,
`DIFF-08`/`MF-29` retarget view list Product Variants, visual parity `MF-38`) **dikonfirmasi cocok
persis** dengan kode aktual di working tree (`security/ir.access.csv`, `views/products.xml`,
`models/product.py`). Tidak ada penyimpangan dari apa yang tertulis di spec untuk ketiga item ini.

Dua penyimpangan ditemukan antara **dokumen spec** dan **kode aktual** (keduanya sudah diperbaiki di
kode, hanya dokumen yang belum disinkronkan):

1. **`views/sale_order.xml`** — spec tidak pernah membahas file ini sama sekali; fix `MF-35` (xpath
   `price_unit` dibungkus `<column>` baru di native 20.0) diterapkan langsung ke kode tanpa update
   balik ke `03_MIGRATION_SPEC.md`.
2. **`models/product.py` `ProductProduct._get_view()`** — mekanisme dedup kolom margin (`MF-37`)
   yang benar-benar dipakai di kode (override Python + marker `class`) berbeda dari yang tertulis di
   spec (`invisible="module_pos_margin_threshold == True"` pada field, yang sudah terbukti gagal).

Kedua kode sudah diverifikasi berjalan benar di Docker 20.0 (lihat `FINDINGS.md` `MF-35`/`MF-37` dan
`06_implementation/sale_margin_threshold/06c_IMPLEMENTATION_LOG.md`) — ini murni utang dokumentasi,
**bukan** blocker fungsional.

---

## Gap Baru (kandidat `MF-NN`, ID berikutnya mulai `MF-39` — cek ulang saat menulis finding formal)

1. **[sale_margin_threshold] `i18n/*.po` tidak pernah dicek kelengkapan terjemahannya terhadap
   string UI baru/berubah dari migrasi ini** (kolom list "Incl. Tax" dan label lain hasil
   `DIFF-08`/`MF-29`/`MF-38`). Tidak disebut di `01b_BASELINE_SPEC.md`, `02_DIFF_ANALYSIS.md`,
   `03_MIGRATION_SPEC.md`, maupun `FINDINGS.md` manapun. Risiko rendah (fallback ke source string
   Inggris kalau terjemahan hilang, bukan crash), tapi genuinely belum pernah dievaluasi — perlu
   keputusan dev apakah in-scope (`.po` perlu diupdate) atau eksplisit di-declare out-of-scope untuk
   migrasi "port kode saja" ini.
2. **[sale_margin_threshold] `03_MIGRATION_SPEC.md` perlu update retroaktif** untuk dua titik yang
   sudah diperbaiki di kode tapi belum tercatat di dokumen spec itu sendiri: (a) baris baru untuk
   `views/sale_order.xml` (`MF-35`), (b) revisi mekanisme dedup `MF-37` di §2b "Risiko Integrasi" #2
   (ganti dari rencana `invisible=` yang gagal, jadi deskripsi `_get_view()` override yang benar-benar
   dipakai). Ini murni pekerjaan dokumentasi (menyalin apa yang sudah ada di `FINDINGS.md`), tidak
   perlu riset baru.

Item non-fungsional (`LICENSE`, `LISEZMOI.md`, `googleaeed8a7b9ec156e7.html`, `static/description/*`,
`demo/demo.xml` yang inert) **tidak** direkomendasikan jadi `MF-NN` — tidak ada risiko migrasi nyata,
cukup dicatat di tabel cakupan di atas untuk kelengkapan Step 4.

---

## Verdict

- [ ] ✅ Lulus — semua elemen Covered, lanjut ke step 5
- [x] ❌ Ditolak — ada gap, balik ke step 2/3 untuk item berikut:
  1. **`views/sale_order.xml`** — tambahkan baris eksplisit di `03_MIGRATION_SPEC.md` §2/§2b
     merujuk `MF-35` (dokumentasi saja, kode & fix sudah benar+terverifikasi).
  2. **`models/product.py` `ProductProduct._get_view()` / dedup `MF-37`** — revisi §2b "Risiko
     Integrasi" #2 di `03_MIGRATION_SPEC.md` supaya sesuai mekanisme aktual yang dipakai (dokumentasi
     saja, kode & fix sudah benar+terverifikasi).
  3. **`i18n/*.po`** — perlu keputusan dev: in-scope (update terjemahan) atau eksplisit
     out-of-scope untuk migrasi port-kode-saja ini; belum ada keputusan tercatat di mana pun.

**Catatan:** kedua gap pertama TIDAK memblokir Step 6 lebih lanjut secara fungsional (kode sudah
benar & terverifikasi Docker) — ini murni supaya `03_MIGRATION_SPEC.md` benar-benar mencerminkan
implementasi final sebelum dipakai sebagai rujukan Step 8 (Code Review). Gap ke-3 (`i18n`) butuh
keputusan dev eksplisit sebelum ditutup. Rekomendasi: dev/AI update dokumen spec (item 1-2, cepat,
tidak perlu riset ulang) + minta keputusan dev soal item 3, lalu re-run Step 4 review singkat untuk
menutup gate secara resmi.

---

## Update pasca-review (2026-09-22)

Gap #1 (`views/sale_order.xml`) dan #2 (`ProductProduct._get_view()` / dedup `MF-37`) **sudah
disinkronkan** ke `03_MIGRATION_SPEC.md` (baris baru di §2 untuk `views/sale_order.xml`, revisi
"Risiko Integrasi" #2 di §2b) — murni update dokumentasi, tidak ada perubahan kode. Gap #3
(`i18n/*.po`) **DIPUTUSKAN dev 2026-09-22: out-of-scope**, tidak diupdate (dicatat sebagai `MF-39`,
`FINDINGS.md`). **Gate ini sekarang LULUS** — ketiga gap sudah ditutup (2 dokumentasi + 1 keputusan
dev eksplisit).
