# Spec Completeness Review — sale_margin_threshold

**Step:** 4 — Spec Completeness Review (gate)
**Ref:** `03_spec/sale_margin_threshold/03_MIGRATION_SPEC.md`, source module `sale_margin_threshold`
**Tanggal:** 2026-08-26

---

## Tabel Cakupan

| Elemen source module | Ada di Migration Spec? | Status | Catatan |
|---|---|---|---|
| `models/sale_order.py` (`action_confirm`, `SaleOrderLine`) | Ya — §2 tabel (`DIFF-01`, `DIFF-03`) | ✅ Covered | Tidak ada perubahan wajib; `MF-08` tetap butuh keputusan user, terpisah dari migrasi versi |
| `models/product.py` (`_register_hook`, margin fields) | Ya — §2 tabel (`DIFF-06`) | ✅ Covered | Tidak ada perubahan |
| `models/res_config_settings.py` | Ya — §2 tabel (`DIFF-07`) | ✅ Covered | Tidak ada perubahan |
| `controllers/controllers.py` | Ya — §2b Controller & Route | ✅ Covered | Dead scaffold |
| `wizard/sale_confirmation.py` + `.xml` | Tidak eksplisit disebut baris terpisah, tapi `self.env[active_model]` (dynamic model access) sudah dicek di intake — tidak ada perubahan API | ✅ Covered (implisit) | Mekanisme `self.env[var]` stabil lintas versi, tidak spesifik ke 18→19 |
| `wizard/wizard_margin_product.py` + `.xml` | Ya — §2b Risiko Integrasi (`MF-03`) | ✅ Covered | |
| `views/products.xml` (inherit `product.product_template_form_view`, `product.product_variant_easy_edit_view`) | **Baru diverifikasi saat Step 4 ini** | ✅ Covered | Dicek langsung ke `enterprise19.0` — kedua XML-ID + field anchor (`list_price`, `lst_price`, group `pricing`) masih ada (sama seperti verifikasi untuk `pos_margin_threshold`, target identik) |
| `views/product_template_views.xml` (inherit `product.product_template_only_form_view`, DIMUAT bersamaan `products.xml` — `MF-05`) | **Baru diverifikasi saat Step 4 ini** | ✅ Covered | XML-ID `product.product_template_only_form_view` dikonfirmasi MASIH ADA di 19.0 — `MF-05` (satu record menimpa yang lain) tetap ada persis sama seperti di 18.0, tidak berubah oleh migrasi versi |
| `views/res_config_settings.xml` (inherit `sale.res_config_settings_view_form`, xpath block `quotation_order_setting_container`) | **Baru diverifikasi saat Step 4 ini** | ✅ Covered | XML-ID dan nama block dikonfirmasi masih ada persis sama di 19.0 |
| `views/sale_order.xml` (inherit `sale.view_order_form`, xpath `//form/sheet`, `//page[@name='order_lines']/field[@name='order_line']/list`, field `price_unit`) | **Baru diverifikasi saat Step 4 ini** | ✅ Covered | `sale.view_order_form` ada, page `order_lines`/field `order_line`/field `price_unit` semua dikonfirmasi masih ada dengan nama sama di `sale/views/sale_order_views.xml` 19.0 |
| `security/groups.xml`, `security/ir.model.access.csv` | Tidak disebut eksplisit | ✅ Covered (implisit) | Tidak ada model baru/dihapus yang butuh access rule baru |
| `demo/demo.xml` | Tidak disebut | ✅ Covered (implisit) | Tidak terpengaruh |
| `tests/test_action_confirm.py`, `tests/test_cross_module.py` | Tidak disebut eksplisit di spec | ✅ Covered (implisit) | Test existing tetap jadi validator — dijalankan ulang di Step 9, tidak butuh perubahan sendiri karena tidak ada perubahan kode produksi |
| `__manifest__.py` | Ya — §2b Critical Blockers #1 | ✅ Covered | Bump version |

## Verdict

- [x] ✅ **Lulus** — semua elemen Covered, lanjut ke step 5.

**Catatan tambahan hasil review ini:** empat view inherit target (`views/products.xml`,
`views/product_template_views.xml`, `views/res_config_settings.xml`, `views/sale_order.xml`) belum
diverifikasi eksplisit di Step 2 — dilakukan di sini, semuanya STABIL di 19.0. `MF-05` (duplikat
XML-ID, satu record menimpa yang lain) dikonfirmasi TETAP ADA persis sama, bukan hilang/berubah
karena migrasi versi — jadi keputusan user soal `MF-05` (klarifikasi target mana yang benar) masih
sama urgensinya seperti sebelum Step 2/3/4, tidak berubah oleh temuan Step 4 ini.
