# Diff & Compatibility Analysis — sale_margin_threshold

**Step:** 2 — Diff & Compatibility Analysis
**Versi:** 19.0 → 20.0
**Tanggal:** 2026-09-21
**Ref:** `01_intake/sale_margin_threshold/01a_MIGRATION_INTAKE.md`, `01_intake/sale_margin_threshold/01b_BASELINE_SPEC.md`, `migration-tool/knowledge/`, `FINDINGS.md` (`MF-08`, `MF-20`, `MF-21`, `MF-26`, `MF-27`)

---

## 0. Knowledge Base Check

| Sumber | Sudah ada entry? | Lokasi |
|---|---|---|
| `version-diffs/19-to-20.md` | Ya — dibaca penuh. Berisi 5 entry general (route `/web/session/logout` GET→POST, `logOutItem()` tidak lagi exported, `ir.model.access.csv`→`ir.access.csv`, ACL baru `res.partner` write-self, `ListRenderer.computeOptionalActiveFields()`). Semua di-cross-check ke modul ini di §1 di bawah. | `migration-tool/knowledge/version-diffs/19-to-20.md` |
| `dependency-compat/sale_renting/19-to-20.md` atau `dependency-compat/product/19-to-20.md` | **Tidak ada — dua kandidat baru signifikan ditemukan sesi ini** (lihat `DIFF-08` di bawah, view `product.product_variant_easy_edit_view` DIHAPUS TOTAL di 20.0). Direkomendasikan jadi entry `dependency-compat/product/19-to-20.md` baru. | — |
| `dependency-compat/sale_report/18-to-19.md` (dari project sebelumnya) | Ya, `tax_id`→`tax_ids` — dikonfirmasi ulang independen Step 2 18→19 sebelumnya, **tetap tidak relevan** ke modul ini (modul tidak sentuh `tax_id`/`tax_ids`) | `migration-tool/knowledge/dependency-compat/sale_report/18-to-19.md` |

## 0b. Gate Community vs Enterprise (WAJIB dicek sebelum §1 dimulai)

- [x] `01a_MIGRATION_INTAKE.md` §2 — ADA satu baris "Native Enterprise" (Rental, `is_rental_order`,
  family `sale_renting`).
- [x] **`native-target-enterprise` (`D:\Kuncoro\doodex\repo\enterprise20`) sudah dicek LANGSUNG sesi
  ini** (bukan diasumsikan dari Community) — `enterprise20/sale_renting/models/sale_order.py:95-97`
  dibaca penuh: field `is_rental_order` (Boolean, `compute="_compute_is_rental_order"`,
  `search="_search_is_rental_order"`) MASIH ADA persis nama sama di 20.0 Enterprise. Modul masih ada
  di lokasi yang sama (`enterprise20/sale_renting/`), tidak dihapus/dipindah ke Community.
- [x] `native-target` (Community, `D:\Kuncoro\doodex\repo\odoo20`) dicek terpisah untuk `sale`,
  `product`, `stock_account`, `base` (lihat §1).
- Kolom "Sumber" tabel §1 di bawah eksplisit menyebut `native-target` vs `native-target-enterprise`
  yang mana yang dicek per baris.

## 0c. Gate Transitive Dependency

Tidak ada `depends` yang diusulkan dihapus untuk modul ini — N/A. (`base`, `product`, `sale`,
`stock_account` semua tetap ada dan tetap didepend.)

## 0d. Gate Grep Menyeluruh — Rename di Knowledge Base

Entry `version-diffs/19-to-20.md` yang match dependency modul ini (`base`, `web` [transitif lewat
`sale`/`product` UI], `product`) — digrep PENUH ke `sale_margin_threshold/` (semua `.py`/`.xml`,
termasuk `tests/`):

- `session/logout`, `"log_out"`, `user_menuitems` — **0 match**. Modul ini tidak punya JS/Owl sama
  sekali (`static/src/` tidak ada di disk, `BSL-014`) — tidak relevan.
- `from "@web/webclient/user_menu/user_menu_items"`, `logOutItem` — **0 match** — sama alasan, tidak
  ada JS.
- `computeOptionalActiveFields` — **0 match** — tidak ada JS.
- `ir.model.access.csv` (nama file, bukan isi) — **1 match**, `security/ir.model.access.csv` sendiri
  (manifest `data` list) — **wajib migrasi format, lihat `DIFF-01`**.
- ACL `res.partner` write-self — tidak relevan, modul tidak sentuh `res.partner`.

Tidak ada rename dari `version-diffs/18-to-19.md` (project sebelumnya) yang perlu digrep ulang di
sini — semua sudah dikonfirmasi selesai/tidak relevan di `02_DIFF_ANALYSIS.md` project 18.0→19.0
(`tax_id`→`tax_ids`, `self._context`, `users`→`user_ids`, `groups_id`→`group_ids`) — dikonfirmasi
ULANG di kode 19.0/20.0 saat ini (identik, lihat `01b_BASELINE_SPEC.md` `BSL-010` §7): kode modul
sudah 100% pakai `self.env.context.get(...)` dan `group_ids`/`user_ids`, 0 sisa pola lama.

## 0e. Gate Silent-Regression per Tipe Override

- **(a) Python — `action_confirm()` override.** Return value native `action_confirm()` 20.0
  (`sale/models/sale_order.py:1619-1649`) adalah `True` (unconditional) — SAMA seperti yang
  diasumsikan modul (`return super().action_confirm()` tanpa memproses return value lebih lanjut).
  Native tetap **batched** secara struktural: `for order in self: ... self.write(...) ...
  self.with_context(...)._action_confirm() ... self.filtered(...).action_lock()` — sama filosofi
  "self bisa multi-record" seperti 18.0/19.0 (dikonfirmasi ulang `DIFF-02` di bawah, blast radius
  `MF-08` TIDAK berubah). Override modul ini sendiri (baris SEBELUM `super()` dipanggil) yang
  meng-copy logic lama TANPA loop (`self.is_rental_order_installed_true`, `self.check_product_price()`)
  — bug lama, tidak diperparah/diperbaiki oleh perubahan native.
- **(a) — entry point tidak langsung, compute `_compute_is_rental_order_installed`.** Dipanggil ORM
  standar (`compute=`), tidak ada perubahan jalur pemanggilan di native 20.0 yang relevan
  (`MF-26`, bug pre-existing, lihat `DIFF-03`).
- **(b) XML — inheritance view.** Dua pola dicek terpisah di §1: `<xpath>`/`position="replace"` ke
  `product.product_template_form_view` (`DIFF-05`/`06`, masih valid) DAN
  `product.product_variant_easy_edit_view` (`DIFF-08`, **view HILANG TOTAL** — lihat detail). Modul
  ini TIDAK punya pola `t-call`/`t-extend` tanpa `inherit_id` (grep `t-call`/`t-extend` di seluruh
  `views/`/`wizard/`: 0 match).
- **(c)/(d) Owl/JS, registry.** N/A — modul tidak punya JS/Owl sama sekali.

---

## 1. Perubahan Native (Core/Enterprise)

| ID | File/simbol modul | Simbol native terkait | Status di target | Dampak | Sumber |
|---|---|---|---|---|---|
| DIFF-01 | `security/ir.model.access.csv` (manifest `data`) | `base` — file `addons/base/security/ir.model.access.csv` (skema `id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink`) → digantikan `ir.access.csv` (model baru `ir.access`, `odoo/addons/base/models/ir_access.py:64-66`, skema `id,name,model_id,group_id/id,operation,domain`, dikonfirmasi langsung dari `odoo/addons/base/security/ir.access.csv` 20.0) | **Rename struktural, TIDAK ADA compat shim.** Dikonfirmasi langsung di loader (`odoo/tools/convert.py:739-740`, `convert_csv_import`): nama MODEL target diambil dari **nama file** (`filename.split('-')[0]`) — untuk file bernama `ir.model.access.csv`, loader akan mencoba `env['ir.model.access']`. Model Python `ir.model.access` (class `IrModelAccess`) **TIDAK ADA lagi** di 20.0 (digantikan total oleh `ir.access`/`IrAccess`) — `env['ir.model.access']` akan raise `KeyError`/model-not-found. **Install-blocking**, bukan cosmetic. | **Tinggi — WAJIB fix sebelum Step 6.** File harus di-rename ke `security/ir.access.csv` + kolom ditulis ulang: `perm_read,perm_write,perm_create,perm_unlink` (4 boolean terpisah) → `operation` (kode gabungan `crud`/`cr`/dst) + kolom `domain` (kosong untuk baris permission murni tanpa domain, karena `ir.access` MENGGABUNGKAN peran `ir.model.access`+`ir.rule`). Manifest `data` juga wajib diupdate nama file. | `native-target` (`odoo20/odoo/tools/convert.py`, `odoo/addons/base/models/ir_access.py`, `odoo/addons/base/security/ir.access.csv`) + `knowledge/version-diffs/19-to-20.md` |
| DIFF-02 | `models/sale_order.py` override `action_confirm()` | `sale.order.action_confirm()` (`odoo20/addons/sale/models/sale_order.py:1619-1649`) | **Tidak berubah secara struktural untuk tujuan blast-radius `MF-08`.** Native tetap memproses `self` sebagai recordset multi-record: `for order in self: ...` (cek error saja, per-record), lalu `self.write(...)`/`self.with_context(...)._action_confirm()`/`self.filtered(...)` (batched, bukan per-record). Return value `True` (unconditional) — sama seperti diasumsikan modul. | **Konfirmasi untuk `MF-08`:** blast radius bug singleton-assumption modul ini SAMA seperti di 18.0/19.0 — tidak lebih buruk, tidak lebih baik. Tidak ada perubahan native yang memperbesar/memperkecil dampak. | `native-target` (`odoo20/addons/sale/models/sale_order.py`) |
| DIFF-03 | `models/sale_order.py:12-17` `_compute_is_rental_order_installed` (`MF-26`) | Tidak ada simbol native yang berubah — ini murni bug internal modul (`self.is_rental_order` dibaca di dalam `for record in self:` yang seharusnya `record.is_rental_order`) | **N/A — bukan gap migrasi.** Dikonfirmasi ulang: pola compute standar (`compute=` kwarg field) tidak berubah caranya dipanggil ORM di 20.0. | Bug pre-existing (`MF-26`), tidak diperparah/diperbaiki migrasi versi — tetap dipertahankan `[DIWARISI-SOURCE]` sesuai `CLAUDE.md` §"Source of Truth". | Analisis baru (konfirmasi `MF-26` tidak berubah) |
| DIFF-04 | `models/res_config_settings.py` `blocking_transaction_order` (`config_parameter=`) | `res.config.settings` binding generik `config_parameter` kwarg (`base/models/res_config.py`) | **Tidak berubah** — mekanisme `Field(config_parameter=...)` generik, tidak versi-spesifik | Tidak ada | `native-target` (`odoo20/odoo/addons/base/models/res_config.py`) |
| DIFF-05 | `views/products.xml` record `product_template_inherit_sale_margin_threshold` — `inherit_id="product.product_template_form_view"`, `position="replace"` field `list_price` | `product.product_template_form_view` (`odoo20/addons/product/views/product_views.xml:35`) MASIH ADA, XML-ID tidak berubah | **Tidak berubah (view tetap ada)** — TAPI native 20.0 field `list_price` di view ini (baris ~127-129) punya `options="{'currency_field': 'currency_id', 'field_digits': True}"` yang HILANG karena `position="replace"` modul menulis ulang tanpa `options` (`BSL-019`/`MF-27`, dikonfirmasi ulang identik — quirk pre-existing, bukan gap baru). | Sedang — `MF-27` tetap terbuka, tidak diperparah versi 20.0 (native tetap punya `options` yang sama, cuma modul yang terus menghapusnya) | `native-target` (`odoo20/addons/product/views/product_views.xml:124-129`) |
| DIFF-06 | `views/product_template_views.xml` record `product_template_inherit_sale_margin_threshold` (XML-ID **identik** dengan `DIFF-05`, `inherit_id="product.product_template_only_form_view"`) | `product.product_template_only_form_view` — **dikonfirmasi MASIH ADA** di `odoo20/addons/product/views/product_template_views.xml` (grep XML-ID langsung, ditemukan) | **View target tetap ada, tapi record ini tetap KALAH** karena `BSL-013` (dua file manifest mendefinisikan XML-ID identik, `products.xml` dimuat setelah `product_template_views.xml` sehingga menimpa total) — quirk pre-existing, tidak berubah oleh migrasi 20.0 | Rendah — dikonfirmasi ulang tidak berubah, kustomisasi ke view ini tetap inert | `native-target` (`odoo20/addons/product/views/product_template_views.xml`) |
| **DIFF-07** | `security/groups.xml` `implied_ids` (`MF-20`) | `res.groups.implied_ids` (Many2many ke `res.groups`, `odoo20/odoo/addons/base/models/res_groups.py:75-78`) | **Field tidak berubah** (nama, tipe, semantik Many2many-ke-res.groups identik). `base.module_category_hidden` (record `ir.module.category`) juga masih ada. Bug lama (isi Many2many dengan record `ir.module.category`, bukan `res.groups`) tetap identik reproduksinya di 20.0 — kemungkinan besar akan raise error tipe relasi saat load data (perlu dicek eksekusi nyata di Step 6/G1, di luar scope statis Step 2) | Sedang — `MF-20` tetap terbuka, tidak berubah dari migrasi versi | `native-target` (`odoo20/odoo/addons/base/models/res_groups.py`) |
| **DIFF-08** | `views/products.xml` record `product_variant_easy_edit_view_margin_sale` — `inherit_id="product.product_variant_easy_edit_view"` | `product.product_variant_easy_edit_view` (Odoo 20.0 core) | **DIHAPUS TOTAL.** Dikonfirmasi via `git log -S"product_variant_easy_edit_view" -- addons/product/views/product_views.xml` di `native-target`: commit `30ec4bee8ae7b6d23ca28e140de72a95fd23ec5a` ("[IMP] product, *: simplify product variant management", task-5207510, closes odoo/odoo#244185) **menghapus record `product_variant_easy_edit_view` beserta SEMUA view yang inherit ke situ di seluruh core** (termasuk `stock.stock_variant_easy_edit_view` milik Odoo sendiri — dihapus, bukan di-retarget). Grep penuh `product_variant_easy_edit_view` di `odoo20/addons/**/*.xml` DAN `enterprise20/**/*.xml`: **0 match** di manapun. Peran form ini sekarang dipegang `product.product_normal_form_view` (`odoo20/addons/product/views/product_views.xml:512-518`, `mode="primary"`, `inherit_id="product.product_template_form_view"`) — struktur BEDA TOTAL (bukan lagi standalone dialog `<form>` sendiri, field `lst_price` sudah exposed native lengkap dengan `options="{'currency_field': 'currency_id', 'field_digits': True}"` di baris 556-558, tidak ada lagi `<group name="pricing">` yang jadi target `position="inside"` modul ini) | **KRITIS — install-blocking, BUKAN cosmetic.** `ir.ui.view` dengan `inherit_id` yang tidak resolve raise error saat load data XML (`ValueError`/`External ID not found`) — modul GAGAL INSTALL TOTAL di 20.0 kalau file ini di-port mekanis apa adanya. Field `is_less_minimum_sale` decoration (`decoration-danger="is_less_minimum_sale"` pada `lst_price`) dan guard `module_pos_margin_threshold` untuk sub-form variant HARUS di-rewrite menyasar `product_normal_form_view` (struktur XPath baru, bukan cuma ganti `inherit_id`) — **wajib jadi riset detail Step 3**, bukan port mekanis. | `native-target` (`odoo20/addons/product/views/product_views.xml`, git history) — **belum ada di `knowledge/version-diffs/19-to-20.md`, kandidat promosi kuat, lihat §3** |
| DIFF-09 | `depends: ['stock_account']` (manifest) | `stock_account` — dependency modul, TIDAK ada XML inherit langsung ke view kategori (`view_category_property_form_stock` yang disebut `01a_MIGRATION_INTAKE.md` §2 **TIDAK ditemukan** dipakai modul manapun setelah pengecekan file listing `views/` lengkap — kemungkinan catatan intake tidak akurat/hipotesis, bukan bukti langsung) | **Koreksi temuan intake:** grep XML-ID `view_category_property_form_stock`/`category_property_form` di seluruh `sale_margin_threshold/`: **0 match**. Dependency `stock_account` kemungkinan murni untuk ketersediaan field `standard_price` (Cost) yang dipakai `_compute_minimum_sale_price` — bukan dependency view. `stock_account` sendiri masih ada di `odoo20/addons/stock_account`, tidak dihapus. | Tidak ada — koreksi dokumentasi murni, tidak mempengaruhi migrasi | Analisis baru (koreksi `01a_MIGRATION_INTAKE.md` §2) |
| DIFF-10 | `res.config.settings` xpath `block[@name='quotation_order_setting_container']` (`views/res_config_settings.xml`) | `sale.res_config_settings_view_form` (`odoo20/addons/sale/wizard/res_config_settings_views.xml`) | **Tidak berubah** — block `quotation_order_setting_container` dikonfirmasi masih ada persis nama sama di 20.0 | Tidak ada | `native-target` (`odoo20/addons/sale/wizard/res_config_settings_views.xml`) |

## 2. Kompatibilitas Dependency (OCA/Third-Party)

Tidak ada — dikonfirmasi dev tidak ada dependency OCA/third-party untuk modul ini (lihat
`01a_MIGRATION_INTAKE.md` §0, gate Step 1 sudah lulus dengan asumsi ini dikonfirmasi dev).

## 3. Temuan Baru — Tulis ke Migration Records

- [x] **`DIFF-08` (view `product.product_variant_easy_edit_view` dihapus total) — kandidat KUAT untuk
  `SUMMARY.md` kategori `version-diff` DAN `dependency-compat/product/19-to-20.md`.** Ini general
  (bukan spesifik modul ini) — modul APAPUN yang inherit `product.product_variant_easy_edit_view`
  akan install-blocking di 20.0. Direkomendasikan promosi ke
  `migration-tool/knowledge/version-diffs/19-to-20.md` (entry general) setelah sesi curation
  terpisah — TIDAK dipromosikan langsung di sini, hanya dicatat sebagai kandidat kuat di
  `migration-records/pos-margin-sale_19.0_20.0/SUMMARY.md`.
- [x] **`DIFF-01` (`ir.model.access.csv`→`ir.access.csv`) — konfirmasi konkret dari entry
  `version-diffs/19-to-20.md` yang sudah ada** (entry itu sendiri menulis "belum diverifikasi
  eksplisit apakah nama file lama masih diterima" — **sesi ini MENJAWAB pertanyaan itu: TIDAK
  diterima**, dikonfirmasi lewat baca langsung `convert_csv_import` di `odoo/tools/convert.py`).
  Kandidat update entry `version-diffs/19-to-20.md` yang sudah ada (menghapus kalimat "belum
  diverifikasi", ganti dengan kesimpulan definitif) — dicatat di `SUMMARY.md` kategori `version-diff`.
- [x] `DIFF-09` — koreksi kecil ke `01a_MIGRATION_INTAKE.md` (bukan temuan versi, dicatat di sini
  untuk jejak, tidak perlu masuk `SUMMARY.md`).

## 4. Ringkasan Risiko

| Item | Level risiko | Catatan |
|---|---|---|
| `DIFF-08` — `product.product_variant_easy_edit_view` dihapus total | **Tinggi — install-blocking baru, BUKAN gap yang sudah diantisipasi Step 1** | Step 1 (`BSL-019`/`MF-27`) cuma menandai `position="replace"` kehilangan atribut — TIDAK menemukan bahwa seluruh VIEW TARGET-nya hilang. Wajib rewrite arsitektural (retarget ke `product_normal_form_view` + struktur XPath baru) sebelum Step 6 fase C (Views) modul ini dimulai. Rekomendasi: eskalasi ke dev sebelum Step 3 ditulis — ada beberapa cara valid untuk retarget (xpath ke grup mana di `product_normal_form_view`), bukan port mekanis satu-ke-satu. |
| `DIFF-01` — `ir.model.access.csv`→`ir.access.csv` | **Tinggi — install-blocking, mekanis tapi wajib** | Fix murah (rename file + rewrite kolom `operation`/`domain`), tapi WAJIB dilakukan, bukan opsional — tanpa ini modul tidak akan install sama sekali di 20.0. Isi baris modul ini murni permission (`perm_read=perm_write=perm_create=perm_unlink=1` untuk `base.group_user` di dua model wizard) — konversi ke `operation='crud'`, `domain=` kosong, straightforward. |
| `MF-08` (batch-confirm singleton bug) | **Tinggi (sudah diketahui sejak Step 1, dikonfirmasi ULANG Step 2 tidak berubah)** | `DIFF-02` mengonfirmasi blast radius sama seperti 18.0/19.0. Keputusan dev (dipertahankan) tetap berlaku, tidak ada urgensi baru dari migrasi versi ini. |
| `MF-26` (singleton bug kedua, `_compute_is_rental_order_installed`) | Sedang | `DIFF-03` — bug internal, tidak berubah oleh native 20.0. Masih terbuka, belum ada keputusan dev. |
| `MF-27`/`BSL-019` (`position="replace"` pada `list_price`, hilangkan `options`) | Sedang | `DIFF-05` — native tetap punya `options` yang sama, modul tetap menghapusnya. Tidak diperparah migrasi, tapi tetap terbuka. |
| `MF-20` (`implied_ids` diisi kategori bukan grup) | Sedang | `DIFF-07` — field native tidak berubah, bug reproduksi identik. Masih terbuka, belum ada keputusan dev. |
| Dependency Enterprise Rental (`is_rental_order`) | **Tidak ada — stabil** | Dikonfirmasi LANGSUNG ke `native-target-enterprise` (`enterprise20/sale_renting/models/sale_order.py:95-97`), bukan diasumsikan dari Community. Nama field, tipe (Boolean, compute+search), lokasi modul semua identik dengan 19.0. |
| `DIFF-06`/`BSL-013` (kolisi XML-ID `product_template_inherit_sale_margin_threshold`) | Rendah | Tidak berubah — kedua view target (`product_template_only_form_view` dan `product_template_form_view`) masih ada di 20.0, urutan menang/kalah identik. |
| `DIFF-10` (xpath `res.config.settings`) | Tidak ada | Target block tidak berubah. |

**Kesimpulan Step 2 modul ini:** Berbeda dari migrasi 18.0→19.0 sebelumnya (yang menyimpulkan modul
ini "tenang", 0 blocker baru), migrasi 19.0→20.0 ini menemukan **DUA blocker teknis install-blocking
BARU** yang harus diperbaiki sebelum Step 6: `DIFF-08` (view core `product_variant_easy_edit_view`
dihapus total — butuh rewrite arsitektural bagian variant-form) dan `DIFF-01`
(`ir.model.access.csv`→`ir.access.csv` — rename + rewrite kolom, mekanis tapi wajib). Empat finding
`[DIWARISI-SOURCE]` lama (`MF-08`, `MF-20`, `MF-26`, `MF-27`) dikonfirmasi ULANG tidak berubah/tidak
diperparah oleh migrasi versi ini — tetap menunggu keputusan dev yang sama seperti sebelumnya, bukan
blocker teknis Step 2.

**Confidence Step 3 lanjut mekanis vs eskalasi:**
- `DIFF-01` — **bisa mekanis**, langkah konversi jelas dan sempit (rename file, ganti 4 kolom boolean
  → `operation`+`domain`), tidak butuh keputusan desain.
- `DIFF-08` — **TIDAK bisa mekanis, wajib eskalasi/keputusan desain di Step 3** sebelum implementasi:
  struktur baru `product_normal_form_view` tidak punya `<group name="pricing">` yang sama, xpath
  target field `lst_price` juga sudah punya `options` native duplikat dengan yang modul coba tambah
  sendiri (potensi konflik `position="replace"` vs `position="attributes"` perlu diputuskan ulang,
  bukan sekadar ganti nilai `inherit_id`). Rekomendasi: `03_MIGRATION_SPEC.md` menuliskan draft
  approach (mis. `position="attributes"` ke `lst_price` yang sudah ada + xpath baru untuk blok
  margin/minimum-price ke grup terdekat di `product_normal_form_view`) dan kalau ada ambiguitas
  nyata, eskalasi ke dev pakai format `ESCALATION` di `CLAUDE.md`.
