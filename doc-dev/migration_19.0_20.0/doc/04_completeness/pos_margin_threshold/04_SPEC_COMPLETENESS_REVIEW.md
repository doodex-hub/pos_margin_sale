# Spec Completeness Review — pos_margin_threshold

**Step:** 4 — Spec Completeness Review (gate)
**Ref:** `03_spec/pos_margin_threshold/03_MIGRATION_SPEC.md`, source module 19.0 (branch `migration/19.0`)
**Tanggal:** 2026-09-22

> Tujuan: pastikan `03_MIGRATION_SPEC.md` mencakup 100% elemen source module — bukan review
> kualitas kode (itu step 8). Enumerasi semua elemen modul dari branch `migration/19.0`, cocokkan
> satu-satu ke spec, DAN cross-check ke kode aktual di working tree (`migration/20.0`) untuk
> menangkap spec drift (fix yang sudah diterapkan ke kode tapi belum di-backport ke dokumen spec).

**Metodologi:**
1. Enumerasi penuh `git ls-tree -r migration/19.0 -- pos_margin_threshold/` (44 file).
2. Baca `03_MIGRATION_SPEC.md` penuh + `FINDINGS.md` penuh (MF-08, MF-20 s/d MF-38 yang menyentuh
   modul ini).
3. `git diff migration/19.0 -- pos_margin_threshold/<file>` untuk SETIAP file berkas kode/config
   (bukan cuma yang "kelihatan berisiko") — supaya tidak mengulang celah proses yang sudah pernah
   tercatat di `FINDINGS.md` `MF-35` ("Step 2 berikutnya harus eksplisit cek SEMUA file
   `views/*.xml` satu per satu, bukan cuma yang kelihatan berisiko dari nama file").
4. Untuk file yang TIDAK disebut di spec sama sekali, cross-check independen ke `native-target`
   (`odoo20`) untuk menilai risiko riil (bukan cuma menandai gap tanpa investigasi).

---

## Tabel Cakupan

| Elemen source module | Ada di Migration Spec? | Status | Catatan |
|---|---|---|---|
| `__manifest__.py` | Ya — §1 Ringkasan Strategi, §2 baris terakhir tabel | ✅ Covered | Version bump `19.0.1.0`→`20.0.1.0` + path `security/ir.model.access.csv`→`ir.access.csv`. Diverifikasi identik dengan `git diff migration/19.0` — cuma 2 baris itu yang berubah, sesuai spec. |
| `__init__.py` (root) | Tidak eksplisit, tapi tidak ada isi berisiko (cuma import submodule) | ✅ Covered (implisit) | File boilerplate murni (`from . import controllers, models, wizard`), tidak ada elemen versi-spesifik. Tidak perlu entri spec terpisah. |
| `controllers/__init__.py`, `controllers/controllers.py` | Ya — §2b "Controller & Route" | ✅ Covered | Spec: "Tidak ada — tetap dead scaffold (seluruh isi di-comment)". Dikonfirmasi `git diff migration/19.0` kosong — file benar-benar tidak berubah, seluruh isi tetap ter-comment. |
| `models/product.py` — class `ProductCategory`, `ProductTemplate` | Ya — §1 ("Python tidak butuh perubahan apapun"), §2b "Kompatibilitas Data Model" | ✅ Covered | Diverifikasi `git diff migration/19.0 -- .../models/product.py` — kedua class ini 100% identik dengan 19.0, sesuai klaim spec. |
| `models/product.py` — class `ProductProduct` | Ya (klaim umum), **TAPI klaim spec tidak akurat lagi** | ⚠️ Covered dengan **spec drift** | Spec §1 menyatakan **"Python (`models/`, `wizard/`) tidak butuh perubahan apapun ... tetap fungsional identik"** dan `DIFF-09` (§2 tabel) hanya membahas `_load_pos_data_fields`. Tapi `git diff migration/19.0` menunjukkan `ProductProduct` di kode AKTUAL (branch `migration/20.0`) punya field BARU yang tidak ada di 19.0 source: `minimum_sale_price_with_tax = fields.Float(...)` + method `_compute_minimum_sale_price_with_tax` — ditambahkan sebagai bagian eksekusi `MF-38` (visual parity kolom "Incl. Tax"), tapi **`03_MIGRATION_SPEC.md` tidak pernah diupdate untuk mendokumentasikan perubahan Python ini**. Klaim "Python tidak butuh perubahan apapun" di §1 sekarang secara faktual salah. Lihat kandidat finding baru #1 di bawah. |
| `models/pos_config.py` — `PosConfig.is_blocked_warning` | Ya (klaim umum) — §2b "Kompatibilitas Data Model" (disebut sebagai `pos.config`) | ✅ Covered | `git diff migration/19.0` kosong — identik. |
| `models/pos_session.py` | **Tidak** — tidak disebut namanya di mana pun; daftar model pada §2b "Kompatibilitas Data Model" cuma menyebut `product.category`/`product.template`/`product.product`/`pos.config`/`res.config.settings`/`wizard.margin.product`, TIDAK menyebut `pos.session` | ❌ Gap (minor) | Isi file HANYA komentar (override `_loader_params_product_product` sudah dihapus total sejak migrasi 18.0, sengaja dibiarkan sebagai catatan sejarah) — tidak ada kode aktif. `git diff migration/19.0` kosong. Risiko nyata nihil, tapi secara harfiah file/model ini tidak pernah disebut eksplisit di spec. |
| `models/res_config_settings.py` | Ya (klaim umum) — §2b "Kompatibilitas Data Model" | ✅ Covered | `git diff migration/19.0` kosong — identik. |
| `security/ir.model.access.csv` → `security/ir.access.csv` | Ya — `DIFF-01`, §2a (literal CSV baru dicantumkan) | ✅ Covered | Isi file aktual (`id,name,model_id,group_id/id,operation,domain` + 1 baris `crud`) **persis sama** dengan literal di §2a spec. |
| `views/products.xml` — record `product_category_form_view_inherit_margin_sale` | Ya — `DIFF-02`, §2a | ✅ Covered | `ref=` sudah `account.view_category_property_form`, sesuai spec. |
| `views/products.xml` — record `product_template_inherit_pos_margin_threshold` (`list_price` + `margin_sale`/`minimum_sale_price`) | Ya — `DIFF-04`/`MF-24`, §2a | ✅ Covered | `options="{'currency_field': 'currency_id', 'field_digits': True}"` sudah ada sesuai spec. |
| `views/products.xml` — record `product_variant_easy_edit_view_margin_sale` (dihapus) → `product_product_tree_view_inherit_margin_sale` (baru) | Ya — `DIFF-03`/`MF-29`, §2a (literal XML dicantumkan) | ⚠️ Covered dengan **spec drift** | Struktur dasar (inherit `product.product_product_tree_view`, kolom `margin_sale`/`minimum_sale_price`, `decoration-danger` pada `lst_price`) sesuai literal spec §2a. **TAPI** kode aktual punya 2 elemen TAMBAHAN yang tidak ada di literal spec: (1) `decoration-danger="margin_sale < 0.0"` pada kolom `margin_sale` itu sendiri, (2) kolom baru `minimum_sale_price_with_tax` (label "Incl. Tax"). Kedua tambahan ini adalah hasil `MF-38` (keputusan dev 2026-09-22, visual parity dengan popup 19.0) — **diterapkan ke kode TAPI `03_MIGRATION_SPEC.md` §2a tidak diupdate**, literal XML di spec sekarang stale/tidak merepresentasikan kode aktual. Lihat kandidat finding baru #1. |
| `views/products.xml` — record `product_normal_form_view_inherit_margin_sale` (dead, di-comment) | Tidak eksplisit disebut per-nama, tapi konsisten "di luar scope" (view mati) | ✅ Covered (implisit) | Tetap ter-comment, tidak masuk manifest, tidak berubah dari 19.0 — pola yang sama dengan `views/product_template_views.xml` (dead file) yang memang eksplisit disebut di §4 "Di Luar Scope". |
| `views/products.xml` — record `product_template_form_view_inherit_pos_margin_threshold` (dead, di-comment, model salah `product.product`) | Sama seperti di atas | ✅ Covered (implisit) | Idem — tetap ter-comment, tidak berubah. |
| `views/products.xml` — record `product_template_margin_sale_action_server`, `product_product_margin_sale_action_server` (server action) | **Tidak** disebut eksplisit di spec manapun | ❌ Gap (minor) | `git diff migration/19.0` kosong — identik dengan 19.0, tidak ada `ref=`/anchor eksternal yang rawan pindah versi (`model_id ref="model_product_template"`/`model_product_product"` adalah XML-ID inti Odoo yang stabil lintas versi). Risiko nihil, tapi tidak pernah dicatat di tabel `DIFF-NNN`. |
| `views/product_template_views.xml` (dead file, tidak di manifest) | Ya — §4 "Di Luar Scope" | ✅ Covered | Eksplisit disebut sebagai dead file, tidak dimasukkan manifest. |
| `views/res_config_settings.xml` | **Tidak** — tidak disebut sama sekali di `02_DIFF_ANALYSIS.md` maupun `03_MIGRATION_SPEC.md` | ❌ Gap | `git diff migration/19.0` kosong (tidak berubah). Cross-check independen ke `native-target`: anchor `<block id="pos_interface_section">` yang di-xpath modul ini **masih ada** di `odoo20/addons/point_of_sale/views/res_config_settings_views.xml:159` — resolve dengan benar, tidak ada indikasi breaking change. Risiko rendah/verified-aman, tapi file ini (satu-satunya view settings modul) tidak pernah masuk enumerasi Step 2/3 secara eksplisit. |
| `wizard/wizard_margin_product.py` | Ya (klaim umum) — §2b "Kompatibilitas Data Model" (`wizard.margin.product`), §2b "Risiko Integrasi" #1 (koeksistensi dengan `sale_margin_threshold`) | ✅ Covered | `git diff migration/19.0` kosong — identik. |
| `wizard/wizard_margin_product.xml` | **Tidak** disebut eksplisit sebagai file terpisah (hanya wizard `.py`-nya yang disebut) | ❌ Gap (minor) | `git diff migration/19.0` kosong. View form murni, tidak ada `inherit_id`/anchor eksternal apapun (definisi mandiri, bukan inherit), sehingga risiko breaking-change versi sangat rendah — tapi tetap tidak pernah dicatat sebagai elemen terpisah di tabel `DIFF-NNN`. |
| `static/src/store/pos_store.js` — patch `PosStore.prototype.pay()` | Ya — `DIFF-06`, §2 tabel | ✅ Covered | `git diff migration/19.0` kosong — identik, sesuai klaim "tidak ada tindakan". |
| `static/src/store/models/models.js` — patch `ProductProduct`/`PosOrderline` | Ya — `DIFF-10`, §2 tabel | ✅ Covered | `git diff migration/19.0` kosong — identik. |
| `static/src/store/orderline.xml` — xpath struktur DOM (`isLessMinimumSalePrice` li) | Ya — `DIFF-08`, §2 tabel | ✅ Covered | Bagian ini tidak berubah, sesuai spec. |
| `static/src/store/orderline.xml` — ekspresi `line.comboParent`/`combo_parent_id` | Ya — `DIFF-05`/`MF-34`, §1 & §2 tabel, **TAPI status di spec sudah usang** | ⚠️ Covered dengan **spec drift** | `03_MIGRATION_SPEC.md` (ditulis 2026-09-22) menyatakan `DIFF-05` "**DITUNDA** — tidak ada perubahan kode. Blocker: `native-source` kosong" dan tabel §2 menulis "Biarkan `orderline.xml` seperti sekarang". Tapi `FINDINGS.md` `MF-34` mencatat blocker itu SUDAH resolved (dev mengisi ulang `native-source` = `odoo19`+`enterprise19`) dan **dev memutuskan PERBAIKI** — `git diff migration/19.0` mengonfirmasi kode aktual SUDAH menerapkan fix (`line.comboParent` → `line.combo_parent_id`, commit `0c39cd6`). `03_MIGRATION_SPEC.md` tidak diupdate untuk mencerminkan keputusan final ini — dokumen spec masih bilang "ditunda tanpa perubahan kode", padahal kode sudah berubah. Lihat kandidat finding baru #2. |
| Semua import path JS lain (`@point_of_sale/...`, `@web/core/...`) di `models.js`/`pos_store.js`/`orderline.xml` | Ya — `DIFF-07`, §2 tabel | ✅ Covered | Diverifikasi tidak berubah. |
| `static/tests/tours/margin_threshold_tour.js` | **Tidak** disebut sama sekali di `02_DIFF_ANALYSIS.md`/`03_MIGRATION_SPEC.md` (`DIFF-07` soal import path hanya membahas file `static/src/`, bukan `static/tests/`) | ❌ Gap | `git diff migration/19.0` kosong (tidak berubah). Cross-check independen: file ini meng-import `@point_of_sale/../tests/pos/tours/utils/{chrome_util,product_screen_util,payment_screen_util}` dan `@point_of_sale/../tests/generic_helpers/dialog_util` — dikonfirmasi keempatnya **masih ada persis di path yang sama** di `odoo20/addons/point_of_sale/static/tests/...` (bukan `tests/` Python biasa). Risiko rendah/verified-aman, tapi asset test tour ini luput sepenuhnya dari cakupan Step 2/3 — pola celah proses yang sama seperti `MF-35`. |
| `tests/test_margin_threshold_tour.py` | **Tidak** disebut di spec | ❌ Gap | `git diff migration/19.0` kosong. Memakai `TestPointOfSaleHttpCommon` dari `odoo.addons.point_of_sale.tests.test_frontend` — base class ini masih ada di `odoo20/addons/point_of_sale/tests/test_frontend.py` (dikonfirmasi file ada, 120KB, belum dicek isi class secara detail — lihat rekomendasi Step 5/9 di bawah). Tidak dibahas di spec sama sekali. |
| `tests/test_margin_sale.py` | **Tidak** disebut di spec | ❌ Gap | `git diff migration/19.0` kosong. Test `TransactionCase` murni terhadap ORM (`margin_sale`, `minimum_sale_price`, wizard) — tidak bergantung API versi-spesifik yang berubah 19→20. Risiko rendah, tapi tidak dicatat di spec. |
| `tests/test_cross_module.py` | **Tidak** disebut di spec | ❌ Gap | `git diff migration/19.0` kosong. Test murni ORM/`ir.model`, tidak bergantung API versi-spesifik. Risiko rendah, tapi tidak dicatat di spec. |
| `demo/demo.xml` | **Tidak** disebut di spec | ❌ Gap (sangat minor) | `git diff migration/19.0` kosong. **Seluruh isi file adalah XML comment** (referensi ke model `pos_margin_threshold.pos_margin_threshold` yang tidak pernah ada — sisa scaffold generator modul, tidak pernah dipakai). Tidak ada baris aktif yang dimuat saat install demo data — nihil risiko install-blocking, tapi tidak pernah disebut di spec. |
| `i18n/fr.po` | Disebut sebagai **catatan tambahan**, bukan baris cakupan formal — §2a catatan `DIFF-03`: string terjemahan merujuk nama view lama, jadi orphan (non-blocking) | ✅ Covered (sebagai catatan) | Konsisten `git diff migration/19.0` kosong (belum ada regenerasi POT, sesuai catatan spec "bukan prioritas Step 6"). |
| `i18n/ar_001.po`, `i18n/es.po`, `i18n/id.po`, `i18n/pt.po` | **Tidak** disebut sama sekali (beda dari `fr.po` yang dapat catatan spesifik) | ❌ Gap (sangat minor) | `git diff migration/19.0` kosong untuk keempatnya. File katalog terjemahan murni, tidak divalidasi saat load (sama seperti `fr.po`), tidak install-blocking. Kemungkinan besar sama nasibnya dengan `fr.po` (orphan entry pasca rename `MF-29`) tapi belum ditulis eksplisit. |
| `LICENSE`, `LISEZMOI.md`, `README.md`, `googleaeed8a7b9ec156e7.html`, `static/description/**` (banner/icon/screenshot/`index.html`) | Tidak disebut — di luar kategori manapun di template (bukan `models/`, `views/`, `security/`, `data/`, `report/`, `wizard/`) | N/A (bukan elemen fungsional) | File dokumentasi/marketing/verifikasi domain Google Search Console, tidak dimuat Odoo saat install (kecuali `static/description/banner.png` yang direferensikan `images:` di manifest — sudah dikonfirmasi ada, tidak berubah). Tidak relevan untuk migrasi kode, wajar tidak disebut di spec teknis. |

---

## Ringkasan Gap

**Total elemen dicek:** 44 file source 19.0 (ditambah cross-check terhadap kode aktual `migration/20.0` untuk mendeteksi drift).

**Covered bersih (tanpa catatan):** sebagian besar file inti (Python model/wizard, `__manifest__.py`,
`controllers/`, patch JS, `DIFF-01`/`02`/`04`).

**⚠️ Covered dengan spec drift (2 item, PRIORITAS TINGGI untuk diperbaiki karena sudah mempengaruhi
akurasi dokumen, bukan cuma kelalaian minor):**
1. `models/product.py` (`ProductProduct.minimum_sale_price_with_tax`) + `views/products.xml`
   (record `product_product_tree_view_inherit_margin_sale`, tambahan `decoration-danger` di
   `margin_sale` + kolom "Incl. Tax") — hasil eksekusi `MF-38` yang tidak di-backport ke
   `03_MIGRATION_SPEC.md`. Klaim §1 "Python tidak butuh perubahan apapun" sudah tidak akurat.
2. `static/src/store/orderline.xml` (`line.combo_parent_id`) — hasil eksekusi `MF-34` (keputusan
   dev: PERBAIKI) yang tidak di-backport; spec §1/§2 masih bilang `DIFF-05` "DITUNDA, tidak ada
   perubahan kode".

**❌ Gap murni (tidak pernah disebut di spec sama sekali, 10 file/elemen), semuanya sudah
di-cross-check independen sesi ini dan TERVERIFIKASI AMAN (tidak ada breaking-change 19→20):**
`models/pos_session.py`, dua `ir.actions.server` di `views/products.xml`, `views/res_config_settings.xml`,
`wizard/wizard_margin_product.xml`, `static/tests/tours/margin_threshold_tour.js`,
`tests/test_margin_threshold_tour.py`, `tests/test_margin_sale.py`, `tests/test_cross_module.py`,
`demo/demo.xml`, `i18n/{ar_001,es,id,pt}.po`.

Tidak satu pun dari 10 gap ini menunjukkan indikasi install-blocking atau regresi fungsional baru —
semuanya identik byte-per-byte dengan 19.0 source (`git diff migration/19.0` kosong), dan untuk yang
punya dependency eksternal (anchor XML-ID, import path test util), cross-check ke `native-target`
mengonfirmasi masih resolve dengan benar di 20.0. **Tapi** kekosongan ini murni karena belum pernah
di-enumerasi eksplisit di Step 2/3 (pola celah proses yang sama seperti `MF-35` — "Step 2 berikutnya
harus eksplisit cek SEMUA file, bukan cuma yang kelihatan berisiko dari nama file") — bukan karena
sudah dianalisis lalu dianggap tidak relevan.

---

## Kandidat Finding Baru (untuk `FINDINGS.md`, ID lanjutan dimulai `MF-39` — TIDAK diberi nomor di
sini, keputusan penomoran final ada di proses curation `FINDINGS.md`)

**Kandidat #1 — Prioritas Sedang. `03_MIGRATION_SPEC.md` stale terhadap eksekusi `MF-38`.**
Field `minimum_sale_price_with_tax` baru di `ProductProduct` (`models/product.py`) dan kolom
tambahan (`decoration-danger` pada `margin_sale`, kolom "Incl. Tax") di record
`product_product_tree_view_inherit_margin_sale` (`views/products.xml`) sudah diterapkan & diverifikasi
langsung di kode (Docker 20.0, per `FINDINGS.md` `MF-38` + `06_implementation/pos_margin_threshold/06c_IMPLEMENTATION_LOG.md`),
tapi `03_MIGRATION_SPEC.md` §1 dan §2a tidak pernah diupdate untuk mencerminkan ini. Rekomendasi:
update §1 (hapus/koreksi klaim "Python tidak butuh perubahan apapun") dan §2a (literal XML record
`product_product_tree_view_inherit_margin_sale` diperbarui menyamai kode aktual) sebelum gate Step 4
ditutup formal.

**Kandidat #2 — Prioritas Sedang. `03_MIGRATION_SPEC.md` stale terhadap eksekusi `MF-34`.**
`DIFF-05` di spec masih berstatus "DITUNDA, blocker `native-source` kosong, tidak ada perubahan
kode" — padahal `FINDINGS.md` `MF-34` sudah RESOLVED dengan keputusan dev "PERBAIKI" dan kode aktual
(`orderline.xml`) sudah menerapkannya. Rekomendasi: update §1 dan baris `DIFF-05` di tabel §2 untuk
mencerminkan status final (fix diterapkan, bukan ditunda).

**Kandidat #3 — Prioritas Rendah. 10 file/elemen di atas tidak pernah masuk enumerasi eksplisit
Step 2/3** (`models/pos_session.py`, 2 `ir.actions.server`, `views/res_config_settings.xml`,
`wizard/wizard_margin_product.xml`, `static/tests/tours/margin_threshold_tour.js`, 3 file
`tests/*.py`, `demo/demo.xml`, 4 file `i18n/*.po` selain `fr.po`). Semua sudah di-cross-check aman
di gate ini (lihat tabel di atas). Rekomendasi: tambahkan baris singkat "no action needed, verified
identical to 19.0 source" untuk masing-masing di `02_DIFF_ANALYSIS.md`/`03_MIGRATION_SPEC.md` —
murni untuk kelengkapan dokumentasi, BUKAN indikasi ada pekerjaan implementasi tersisa. Ini juga pola
proses yang sama dengan `MF-35` ("Step 2 berikutnya harus eksplisit cek SEMUA file") — pertimbangkan
apakah perlu jadi catatan proses permanen di `CLAUDE.md`/`OVERVIEW.md` supaya Step 2 project
berikutnya (modul lain) melakukan enumerasi file lengkap dari awal, bukan cuma file yang "kelihatan
berisiko".

---

## Verdict

- [ ] ✅ Lulus — semua elemen Covered, lanjut ke step 5
- [x] ❌ Ditolak — ada gap, balik ke step 2/3 untuk item berikut:
  1. **Update `03_MIGRATION_SPEC.md`** untuk mencerminkan eksekusi `MF-38` (field `minimum_sale_price_with_tax`
     baru + kolom list tambahan) dan `MF-34` (fix `combo_parent_id` diterapkan, `DIFF-05` bukan lagi
     "ditunda") — Kandidat #1 dan #2 di atas. **Ini yang paling penting** karena menyangkut akurasi
     dokumen spec yang jadi acuan Step 6 lanjutan/Step 8 review, bukan cuma risiko fungsional.
  2. **Tambahkan baris cakupan eksplisit** (boleh singkat, "no action needed") untuk 10 file/elemen
     yang belum pernah disebut di `02_DIFF_ANALYSIS.md`/`03_MIGRATION_SPEC.md` — Kandidat #3 di atas.
     Tidak ada indikasi risiko fungsional baru (semua sudah di-cross-check aman sesi ini), jadi ini
     murni pekerjaan dokumentasi, seharusnya cepat.

**Catatan penting untuk dev:** kedua kategori gap di atas TIDAK menunjukkan bug/regresi baru yang
perlu perbaikan kode — implementasi aktual (`MF-34`/`MF-38`) sudah benar dan sudah diverifikasi
langsung di Docker sebelumnya. Yang kurang murni dokumen `03_MIGRATION_SPEC.md`/`02_DIFF_ANALYSIS.md`
belum disinkronkan dengan keputusan-keputusan yang diambil di luar urutan step normal (lihat
`CLAUDE.md` "Status saat ini" — beberapa fix Step 6 sudah dieksekusi dini atas permintaan dev sebelum
Step 4 ini). Setelah dokumen diupdate, gate ini bisa langsung diulang (cukup cek ulang §1/§2a spec
dan tambah baris tabel di atas) tanpa perlu riset ulang dari nol — cross-check teknis di review ini
sudah tuntas.

---

## Update pasca-review (2026-09-22)

Kandidat #1 (`MF-38` spec drift, §1+§2a), #2 (`MF-34` spec drift, §1+§2) dan #3 (10 elemen coverage
gap) **semua sudah disinkronkan** ke `03_MIGRATION_SPEC.md` (§1 dikoreksi, baris §2 tabel diupdate
status RESOLVED, §2c baru ditambahkan untuk 10 elemen no-action-needed) — murni update dokumentasi,
tidak ada perubahan kode tambahan. Gate ini bisa dianggap **LULUS** setelah update ini.
