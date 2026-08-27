# Spec Completeness Review — pos_margin_threshold

**Step:** 4 — Spec Completeness Review (gate)
**Ref:** `03_spec/pos_margin_threshold/03_MIGRATION_SPEC.md`, source module `pos_margin_threshold`
**Tanggal:** 2026-08-26

> Tujuan: pastikan `03_MIGRATION_SPEC.md` mencakup 100% elemen source module — bukan review
> kualitas kode (itu step 8).

---

## Tabel Cakupan

| Elemen source module | Ada di Migration Spec? | Status | Catatan |
|---|---|---|---|
| `models/product.py` | Ya — §2 tabel, §2b Kompatibilitas Data Model | ✅ Covered | Tidak ada perubahan wajib kecuali rename kosmetik param `_load_pos_data_fields` |
| `models/pos_config.py` | Ya — §2b Kompatibilitas Data Model ("semua tetap identik struktur field") | ✅ Covered | Tidak ada perubahan |
| `models/pos_session.py` | Ya — sudah kosong (dokumentasi murni) sejak 17→18, tidak disentuh | ✅ Covered | N/A, tidak ada logic |
| `models/res_config_settings.py` | Ya — §2b | ✅ Covered | Tidak ada perubahan |
| `controllers/controllers.py` | Ya — §2b Controller & Route | ✅ Covered | Dead scaffold, tidak disentuh |
| `wizard/wizard_margin_product.py` + `.xml` | Ya — §2b Risiko Integrasi (kolisi `MF-03`) | ✅ Covered | Python murni, tidak ada perubahan API yang mempengaruhi |
| `views/products.xml` (inherit `stock_account.view_category_property_form_stock`, `product.product_template_form_view`, `product.product_variant_easy_edit_view`) | **Baru diverifikasi saat Step 4 ini** (tidak eksplisit di Step 2/3) | ✅ Covered | Dicek langsung ke `enterprise19.0`: ketiga XML-ID target MASIH ADA, field anchor (`property_cost_method`, `list_price`, `categ_id`, `lst_price`, group `pricing`) semua masih ada dengan nama sama. Tidak ada perubahan wajib. |
| `views/product_template_views.xml` (dead file) | Ya — §Scope "Di Luar Scope" (`MF-04`, tetap mati) | ✅ Covered | Tidak dimuat, tidak perlu dicek terhadap 19.0 |
| `views/res_config_settings.xml` (inherit `point_of_sale.res_config_settings_view_form`) | **Baru diverifikasi saat Step 4 ini** | ✅ Covered | XML-ID dan block `id="pos_interface_section"` dikonfirmasi masih ada di 19.0 |
| `security/ir.model.access.csv` | Tidak eksplisit disebut, tapi tidak ada model baru/dihapus | ✅ Covered (implisit) | Tidak ada perubahan model yang membutuhkan access rule baru |
| `demo/demo.xml` | Tidak disebut | ✅ Covered (implisit) | Data demo, tidak terpengaruh perubahan API |
| `static/src/store/models/models.js` | Ya — §2 tabel (`DIFF-01`, `06`, `07`, `08`, `09`) | ✅ Covered | Area kerja utama Step 6 |
| `static/src/store/pos_store.js` | Ya — §2 tabel (`DIFF-02`, `03`, `08`) | ✅ Covered | |
| `static/src/store/orderline.xml` | Ya — §2 tabel (`DIFF-10`) | ✅ Covered | Tidak ada perubahan |
| `static/tests/tours/margin_threshold_tour.js` + `tests/test_margin_threshold_tour.py` | Tidak disebut eksplisit di spec (spec fokus ke kode produksi) | ✅ Covered (implisit) | Test existing akan otomatis jadi validator porting Step 6/9 — tidak butuh perubahan spec sendiri, tapi WAJIB dijalankan ulang setelah `DIFF-06`/`07`/`08`/`09` diporting |
| `tests/test_margin_sale.py`, `tests/test_cross_module.py` | Sama seperti di atas | ✅ Covered (implisit) | |
| `__manifest__.py` | Ya — §2 tabel, §2b Critical Blockers #1 | ✅ Covered | Bump version |

## Verdict

- [x] ✅ **Lulus** — semua elemen Covered, lanjut ke step 5.

**Catatan tambahan hasil review ini:** verifikasi view XML inherit target terhadap `native-target`
19.0 (`stock_account.view_category_property_form_stock`, `product.product_template_form_view`,
`product.product_variant_easy_edit_view`, `point_of_sale.res_config_settings_view_form`, plus field
anchor di dalamnya) **belum dilakukan di Step 2** (fokus Step 2 sepenuhnya ke JS/Python) — dilakukan
di sini sebagai bagian gate Step 4, dan semuanya dikonfirmasi STABIL, tidak ada perubahan wajib.
Tidak ada gap baru yang perlu balik ke Step 2/3.
