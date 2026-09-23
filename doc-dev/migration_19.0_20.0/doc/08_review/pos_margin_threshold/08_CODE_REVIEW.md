# Code Review — pos_margin_threshold

**Step:** 8 — Code Review (gate)
**Ref:** `03_spec/pos_margin_threshold/03_MIGRATION_SPEC.md`, `05_acceptance/pos_margin_threshold/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `06_implementation/pos_margin_threshold/06c_IMPLEMENTATION_LOG.md`, `01_intake/pos_margin_threshold/01b_BASELINE_SPEC.md`
**Odoo Version:** 19.0 → 20.0
**Files reviewed:** full `git diff migration/19.0 migration/20.0 -- pos_margin_threshold/` (9 files: `__manifest__.py`, `models/pos_config.py`, `models/product.py`, `security/ir.access.csv` (new)/`security/ir.model.access.csv` (removed), `static/src/store/orderline.xml`, `static/tests/tours/margin_threshold_tour.js`, `tests/test_margin_threshold_tour.py`, `views/products.xml`) plus every unchanged file the diff/manifest loads or depends on (`models/pos_session.py`, `wizard/wizard_margin_product.py`/`.xml`, `controllers/controllers.py`, `security/groups.xml` n/a — module has none, `demo/demo.xml`, `tests/test_margin_sale.py`, `tests/test_cross_module.py`, `views/res_config_settings.xml`) cross-checked against `D:\Kuncoro\doodex\repo\odoo20` and `D:\Kuncoro\doodex\repo\enterprise20` (target), `D:\Kuncoro\doodex\repo\odoo19`/`enterprise19` (source-side confirmation where relevant).
**Tanggal:** 2026-09-23

> §A (skill `odoo-review` dispatch + business-logic pass) dilakukan di pass review terpisah sebelum
> dokumen ini ditulis — hasilnya digabung verbatim di bawah, tidak diulang. §B/§C/§D/§E/§F/§G ditulis
> baru untuk gate ini, termasuk Desk Review penuh per AC (§C) dan cek tabrakan nama 3-arah (§D).

---

## A. Issues (Lint, Konvensi Odoo, Business Logic, Security, Performance, Code Quality)

**Status skill `odoo-review` (WAJIB diisi, sebelum isi tabel Issues di bawah):**
- [x] Terinstall & sudah dijalankan — hasil temuan digabung ke tabel Issues di bawah
- [ ] BELUM terinstall

> Guidelines dibaca: `odoo-guidelines` (security.md, xml.md, fields.md, orm.md, manifest.md, tests.md,
> python.md, stable.md), `odoo-web-guidelines` (javascript.md), `odoo-security` (SKILL.md, full
> checklist — sudo/SQL/domain/eval/route/RPC, tidak ada hit baru di luar `ir.config_parameter.sudo()`
> pre-existing yang sudah stabil sejak 19.0). Native-API cross-check (arsitektur/behavior yang
> berubah antar versi, bukan cuma gaya kode) sudah dilakukan terhadap `odoo20`/`enterprise20` untuk
> setiap API yang dipakai diff maupun file yang tidak disentuh tapi load-bearing — semuanya resolve
> bersih (lihat "Verified clean" di bawah), tidak menghasilkan issue baru di luar dua yang tercatat.

| ID | Severity | Kategori | File | Baris | Issue | Rekomendasi |
|---|---|---|---|---|---|---|
| ISS-01 | 🟡 Warning | Tests (odoo-guidelines tests.md) | `tests/test_margin_sale.py`, `tests/test_cross_module.py`, `static/tests/tours/margin_threshold_tour.js` | — (absensi) | Redesign kolom list `MF-29`/`MF-37`/`MF-38` (kolom baru `margin_sale`/`minimum_sale_price`/`minimum_sale_price_with_tax` di `product.product_product_tree_view`, `decoration-danger`, kontrak dedup lintas-modul dengan `sale_margin_threshold._get_view()`) **tidak punya test otomatis sama sekali** — hanya diverifikasi manual sekali di Docker (`FINDINGS.md` `MF-37`/`MF-38`). Regresi (view berubah lagi, dedup patah, kolom dobel muncul lagi) akan lolos CI diam-diam. | Tambah `TransactionCase` di `test_cross_module.py` yang assert `arch_db`/`fields_get` dari `product.product_product_tree_view` (via `_get_view()`) menunjukkan TEPAT satu set kolom margin/tax saat kedua modul terinstall. |
| ISS-02 | 🔵 Info | Dokumentasi (`FINDINGS.md`) | `FINDINGS.md` `MF-25` | — | `MF-25` sempat tercatat "🔵 Terbuka — belum ada keputusan user" padahal record `product_variant_easy_edit_view_margin_sale` yang jadi lokasinya sudah dihapus total oleh rewrite `MF-29`. Status jadi stale/menyesatkan untuk pembaca Step 9-11 berikutnya. | **Sudah diperbaiki sebagai bagian review ini** — lihat `FINDINGS.md` `MF-25` (ditandai ✅ RESOLVED/moot, 2026-09-23), tidak perlu aksi lanjutan. |
| ISS-03 | 🔵 Info | Dokumentasi (`05a_MIGRATION_ACCEPTANCE_CRITERIA.md`) | `wizard/wizard_margin_product.py` `_compute_product_model` vs `05a` AC-02-01/AC-02-02 | `wizard/wizard_margin_product.py:15-21` | Nilai boolean `is_product` yang dituliskan di AC-02-01/AC-02-02 (`05a`) terbalik dari kode aktual: kode men-set `is_product = True` untuk `active_model == 'product.template'` (bukan `False` seperti tertulis di AC-02-01). Perilaku yang KELIHATAN ke user tetap benar (field `product_template_ids` tetap tampil untuk konteks template — lihat Desk Review §C AC-02-01/02) karena view memakai `invisible="not is_product"`/`invisible="is_product"` yang konsisten dengan penamaan boolean kode, jadi ini murni typo deskripsi AC, BUKAN bug kode — kode ini byte-identik dengan `migration/19.0` (`git diff` kosong), jadi di luar scope P1 fidelity migrasi ini. | Perbaiki teks AC-02-01/AC-02-02 di `05a_MIGRATION_ACCEPTANCE_CRITERIA.md` (tukar nilai `is_product` yang dikutip) di sesi revisi berikutnya — tidak blocking gate ini. |

**Severity:** 🔴 Critical (bug/security/AC tidak cover — wajib fix) · 🟡 Warning (convention/performance — fix kalau memungkinkan) · 🔵 Info (saran, opsional)

### Verified clean (native-API cross-check, tidak menghasilkan issue baru)
Dikonfirmasi ulang saat menulis dokumen ini (menambah, bukan mengulang, cakupan pass sebelumnya):
`security/ir.access.csv` format/kolom cocok skema 20.0; `views/products.xml` ketiga record (`product_category_form_view_inherit_margin_sale`, `product_template_inherit_pos_margin_threshold`, `product_product_tree_view_inherit_margin_sale`) — semua anchor/xpath resolve, atribut `options`/`optional`/`column_invisible` dipakai benar sesuai konvensi `<list>` 20.0; `orderline.xml` — `t-call-slot`/`this.line.*` sudah benar, tidak ada bare identifier tersisa; `wizard/wizard_margin_product.py`/`.xml`, `controllers/controllers.py`, `models/pos_session.py` — byte-identik 19.0, tidak ada aksi dibutuhkan; `__manifest__.py` — `data`/`assets`/`depends` semua resolve di `odoo20`.

## B. Gap Analysis — Implementasi vs Migration Spec

| Spec item (`DIFF-NNN`/Fase) | Implementasi | Status | Catatan |
|---|---|---|---|
| `DIFF-01` (`ir.model.access.csv`→`ir.access.csv`) | `security/ir.access.csv` ditulis persis skema §2a (header `id,name,model_id,group_id/id,operation,domain`, baris `crud`) | ✅ Selesai | Dikonfirmasi file lama dihapus (`git diff` menunjukkan `-2` baris di `ir.model.access.csv`, `+2` di `ir.access.csv`), manifest `data:` diupdate |
| `DIFF-02` (anchor kategori) | `ref="account.view_category_property_form"` di `product_category_form_view_inherit_margin_sale` | ✅ Selesai | Sesuai literal §2a |
| `DIFF-03`/`MF-29` (kolom list pengganti popup) | Record `product_variant_easy_edit_view_margin_sale` dihapus, `product_product_tree_view_inherit_margin_sale` ditulis inherit `product.product_product_tree_view`, `lst_price` pakai `position="attributes"` (bukan `replace`) | ✅ Selesai | Cocok literal §2a persis, termasuk `is_less_minimum_sale column_invisible="True"` |
| `DIFF-04`/`MF-24` (options currency `list_price`) | `options="{'currency_field': 'currency_id', 'field_digits': True}"` ditambahkan ke field pengganti, `position="replace"` TIDAK diubah | ✅ Selesai | Sesuai keputusan dev "jaga-jaga kompatibilitas", bug `MF-24` sengaja dipertahankan |
| `DIFF-05`/`MF-34` (`combo_parent_id`) | `line.comboParent` → `line.combo_parent_id`, komentar XML ditambahkan | ✅ Selesai | Diperluas jadi juga fix `MF-41` (bare identifier `this.line.*`, `t-call-slot`) di file yang sama |
| `MF-38` (visual parity: field `minimum_sale_price_with_tax` di `ProductProduct` + 2 kolom list) | Field+compute baru di `models/product.py` `ProductProduct`; kolom `margin_sale` (`decoration-danger`) + `minimum_sale_price_with_tax` ("Incl. Tax") di `product_product_tree_view_inherit_margin_sale` | ✅ Selesai | Cocok §2 tabel baris `MF-38`; verifikasi live sudah dicatat di `FINDINGS.md` |
| `DIFF-06`..`DIFF-07`, `DIFF-09`..`DIFF-10` (tidak ada tindakan) | Tidak ada perubahan di file terkait (`pos_store.js`, import path, `_load_pos_data_fields` signature, `setUnitPrice` patch) | ✅ Selesai (no-op sesuai spec) | Dikonfirmasi `git diff` tidak menyentuh file-file ini kecuali `_load_pos_data_fields` (tambah 2 field ke `params`, konsisten §2 baris `DIFF-09` "tidak ada perubahan wajib") |
| `DIFF-08` (xpath `t-slot`) | **Spec awal salah** ("tidak ada tindakan") — implementasi AKTUAL memperbaiki `t[@t-slot='default']` → `t[@t-call-slot='default']` (`MF-41`) | ⚠️ Spec ternyata perlu update, implementasi SUDAH benar | `03_MIGRATION_SPEC.md` §2 baris `DIFF-08` belum diupdate untuk mencerminkan `MF-41` (dokumen spec masih bilang "tidak perlu tindakan") — rekomendasi: sinkronkan `03_MIGRATION_SPEC.md` §2 baris `DIFF-08` mengutip `MF-41` seperti sudah dilakukan di §1 untuk item lain, murni housekeeping dokumentasi, TIDAK ada gap kode |
| `MF-40`, `MF-41`, `MF-42`, `MF-43`, `MF-44` (ditemukan Step 9, di luar `03_MIGRATION_SPEC.md` asli) | Semua diterapkan (`get_bool`/`set_bool`, `this.line.*`+`t-call-slot`, workaround test `restrict_price_control`, `env.flush_all()`, selector `.feedback-screen`) | ✅ Selesai | Wajar tidak ada di spec asli (ditemukan setelah spec ditulis, dari eksekusi test sungguhan) — dicatat lengkap di `06c_IMPLEMENTATION_LOG.md`/`FINDINGS.md`, tidak perlu retrofit ke `03_MIGRATION_SPEC.md` (dokumen itu memandu implementasi sebelum eksekusi, bukan log post-hoc) |
| Bump `version` → `20.0.1.0` | `__manifest__.py` `version: "20.0.1.0"` | ✅ Selesai | — |

Tidak ada item `03_MIGRATION_SPEC.md` yang belum diimplementasikan. Satu catatan housekeeping non-blocking (`DIFF-08` deskripsi spec vs `MF-41`).

## C. Gap Analysis — Implementasi vs Acceptance Criteria

> Desk Review per AC (37 total). Grup yang murni regresi Python tanpa perubahan kode ditelusuri
> singkat (kode dikonfirmasi identik ke `migration/19.0`); grup berisiko migrasi ditelusuri penuh ke
> baris kode aktual.

| AC ID | Behavior | Status | Jejak Nalar (Desk Review) | Catatan |
|---|---|---|---|---|
| AC-01-01..03 | Margin compute dari kategori, override manual persisten, formula `minimum_sale_price` | Match | `models/product.py` `ProductTemplate._compute_margin_sale`/`_compute_minimum_sale_price` — `git diff migration/19.0` tidak menyentuh method-method ini (hanya `ProductProduct` yang dapat field baru). Logic dibaca identik ke deskripsi AC. | Regresi murni, test existing sudah cover |
| AC-01-04/05 | Inverse `minimum_sale_price`→`margin_sale`, guard div-zero | Match | `_inverse_minimum_sale_price` (baik `ProductTemplate` maupun `ProductProduct`) — guard `if rec.standard_price: ... else: rec.margin_sale = 0.0` persis sesuai AC, tidak berubah dari 19.0 | — |
| AC-01-06 | Margin variant selalu ikut template (quirk `MF-01`) | Match | `ProductProduct._set_product_margin_sale` (`@api.onchange`) menulis ke `product_tmpl_id`, dan `_compute_margin_sale` variant `@api.depends('categ_id.margin_sale', 'product_tmpl_id.margin_sale')` — mekanisme sharing sama, dipertahankan identik | Quirk warisan, sengaja tidak diperbaiki |
| AC-01-07 | `is_less_minimum_sale` boleh stale (no `@api.depends`) | Match | `ProductProduct._compute_warning` tidak punya decorator `@api.depends` — dikonfirmasi baris kode, absensi ini genuinely dipertahankan (tidak ditambahkan diam-diam saat migrasi) | Test absensi belum ada (dicatat AC itu sendiri sebagai gap, bukan temuan baru review ini) |
| AC-01-08 | `_set_product_margin_sale` terpanggil via onchange sebelum save | Match (kode) | `@api.onchange('margin_sale')` di atas `_set_product_margin_sale` — mekanisme onchange memang ada di kode, cuma belum ada test yang mensimulasikan form onchange (gap test, bukan gap kode) | Tidak ada perubahan migrasi di sini |
| AC-02-01 | Wizard dari list Product Template, `product_template_ids` tampil | Match (perilaku), lihat `ISS-03` | `action_assign_margin()` (`ProductTemplate`) create wizard dgn `product_template_ids`; `_compute_product_model` set `is_product=True` untuk `active_model=='product.template'`; view `invisible="not is_product"` pada `product_template_ids` → tampil. Field yang tampil ke user SESUAI AC's "Then" clause. Nilai `is_product` yang dikutip AC (`False`) terbalik dari kode aktual (`True`) — murni typo deskripsi AC (`ISS-03`), kode byte-identik 19.0 | — |
| AC-02-02 | Wizard dari list Product Variant, `product_ids` tampil | Match (perilaku), lihat `ISS-03` | Sama seperti AC-02-01, `action_assign_margin()` versi `ProductProduct` (method terpisah, sesuai AC "dua method paralel") | — |
| AC-02-03 | `action_assing_margin()` (typo dipertahankan) tulis `margin_sale` semua produk terpilih | Match | `wizard_margin_product.py:23` — nama method masih `action_assing_margin`, loop `product_template_ids`/`product_ids` sesuai `active_model`, tidak ada kondisi tambahan | Byte-identik 19.0 |
| AC-02-04 | Cancel — tidak ada perubahan | Match | `wizard_margin_product.xml:23` — `<button string="Cancel" special="cancel".../>`, native `special="cancel"` menutup dialog tanpa memanggil method apapun | Behavior native, test belum ada (gap AC sendiri, bukan gap kode) |
| AC-03-01..02/04 | Dialog confirm/blocking saat Pay | Match | `pos_config.py` `_compute_blocked_warning` (fix `MF-40`, `get_bool`) — logic if/else dipertahankan identik, hanya API call yang berubah. `pos_store.js` (patch `pay()`) tidak disentuh diff, dikonfirmasi tidak berubah dari 19.0. Tour existing (`..._confirm_tour`/`..._blocked_tour`) LOLOS BERSIH per `06c_IMPLEMENTATION_LOG.md` Step 9 | Diverifikasi via eksekusi nyata (bukan cuma baca kode), sesuai catatan risiko §2b poin 5 |
| AC-03-03 | Decline dialog — batal, tetap ProductScreen | Gap test (bukan gap kode) | Kode `pos_store.js` (tidak dalam diff) memanggil `Dialog.confirm()`/pola serupa — tidak ada test yang mengklik tombol decline; risiko rendah karena ini behavior komponen `Dialog` native, bukan logic modul | Sudah ditandai di `05a` sebagai gap, bukan temuan baru |
| AC-03-05 | Tidak ada dialog sama sekali di atas minimum | Gap test, carry-forward 3x | Logic `_compute_blocked_warning`/filter margin di `pos_store.js` secara struktural TIDAK memunculkan dialog kalau tidak ada line di bawah minimum (tidak ada jalur kode yang memanggil `Dialog` tanpa kondisi ini) — behaviorally masuk akal Match, tapi **belum ada test otomatis eksplisit**, ini `BSL-018` yang sudah dilewati DUA kali sebelumnya | **Direkomendasikan ke `FINDINGS.md`/eskalasi user sebelum Step 9 final ditutup — lihat §G** |
| AC-04-01 | Warning `<li>` disisipkan sebelum slot default | Match | `orderline.xml` xpath `position="before"` pada `t[@t-call-slot='default']` di dalam `ul.info-list` — descendant xpath dipertahankan (`MF-20` fix lama tetap ada) | Diverifikasi juga oleh tour Step 9 |
| AC-04-02 | Class gabungan `text-danger` + combo | Match | `t-attf-class` satu ekspresi gabungan `this.line.combo_parent_id ? '...' : ''` + `this.line.isLessMinimumSalePrice ? 'text-danger' : ''` — persis satu atribut, sesuai AC | `BSL-016` regression-check terpenuhi |
| AC-04-03 | Teks+warna warning ter-assert terpisah | Gap test, carry-forward 3x | Sama `AC-03-05` — kode sudah render benar (dikonfirmasi tour lolos), assertion granular belum ada | Sama rekomendasi §G |
| AC-05-01 | Combo-child styling aktif via `combo_parent_id` | Match (kode), visual live belum 100% dikonfirmasi kombo produk sungguhan | `orderline.xml` `this.line.combo_parent_id` — fix `MF-34`/`MF-41` diterapkan benar, XML well-formed, module update bersih. Tour Step 9 lolos TAPI test existing tidak eksplisit membuat skenario combo product (`FINDINGS.md MF-34` mencatat ini terbuka) | Risiko migrasi tinggi ditandai `05a` — **rekomendasi tour baru Step 9/10, lihat §G** |
| AC-06-01 | `list_price` replace + field baru sebelum `categ_id` | Match | `product_template_inherit_pos_margin_threshold`: `categ_id position="before"` berisi blok `margin_sale` DAN blok `minimum_sale_price`/`minimum_sale_price_with_tax`, keduanya dengan `invisible="product_variant_count > 1 and not is_product_variant"` — persis AC | `list_price` tetap `position="replace"` (bug `MF-24` dipertahankan by design) |
| AC-06-02 | `margin_sale` sebelum `property_cost_method`, anchor baru | Match | `product_category_form_view_inherit_margin_sale` `inherit_id="account.view_category_property_form"`, xpath `property_cost_method position="before"` | Sesuai `DIFF-02` |
| AC-06-03 | (dokumentasi popup lama, tidak berlaku 20.0) | N/A (by design) | View target sudah tidak ada, tidak ada record 20.0 untuk dinilai — sesuai `05a` sendiri yang menandai ini "bukan AC yang perlu lulus/gagal independen" | — |
| AC-07-01 | Kolom `margin_sale`/`minimum_sale_price` `optional="show"` | Match | `product_product_tree_view_inherit_margin_sale` — kedua field eksplisit `optional="show"` | — |
| AC-07-02 | `lst_price` decoration via `attributes` (bukan `replace`) | Match | Node pertama xpath: `<field name="lst_price" position="attributes"><attribute name="decoration-danger">is_less_minimum_sale</attribute></field>` — dikonfirmasi bukan `replace`, atribut native (`options`/`optional` pada `lst_price`) tetap utuh | Ini yang membuat `MF-25` moot (`ISS-02`) |
| AC-07-03 | `margin_sale` merah saat negatif + kolom Incl. Tax terisi | Match | `<field name="margin_sale" optional="show" widget="float" decoration-danger="margin_sale &lt; 0.0"/>` + `<field name="minimum_sale_price_with_tax" string="Incl. Tax" optional="show" .../>`, backing field+compute baru di `ProductProduct` (`MF-38`) | Diverifikasi live per `FINDINGS.md` |
| AC-07-04/AC-09-03 | Kolom tidak dobel dengan `sale_margin_threshold` | Match (per verifikasi manual), belum ada test otomatis | Dedup dilakukan di SISI `sale_margin_threshold` (`_get_view()` + marker `o_smt_dedup_*`) — kolom modul INI (`pos_margin_threshold`) tidak diberi marker apapun sehingga otomatis jadi satu-satunya yang tampil, sesuai desain `MF-29`/`MF-37`. Tidak ada kode di modul ini sendiri yang perlu berubah untuk dedup — tanggung jawab sepenuhnya di `sale_margin_threshold` | **Test otomatis lintas-modul masih kosong — sama isu dengan `ISS-01`, lihat §G** |
| AC-08-01/02 | `_load_pos_data_fields` kirim 2 field baru, getter frontend | Match | `models/product.py` `ProductProduct._load_pos_data_fields`: `super()` dipanggil dulu, lalu `params += ['minimum_sale_price', 'minimum_sale_price_with_tax']` — urutan super-then-extend benar. Getter JS (`models.js`, tidak dalam diff) tidak diverifikasi ulang baris-per-baris sesi ini (unchanged, load-bearing, sudah dikonfirmasi resolve di pass review sebelumnya) | `MF-43` (nilai 0 di frontend) sudah RESOLVED sebagai bug test-flush, bukan bug field ini |
| AC-08-03 | `setUnitPrice` dead patch dipertahankan | Match | `models.js` tidak disentuh diff — dikonfirmasi via `03_MIGRATION_SPEC.md` §2 `DIFF-10` "tidak ada tindakan" | — |
| AC-09-01 | `wizard.margin.product` MRO merge, `sale_margin_threshold` menang | Match (per test existing) | Struktur `_name` sama di kedua modul (Python `_inherit`-less `TransientModel`, jadi MRO/registry merge tergantung urutan load `depends`) — tidak ada perubahan kode migrasi yang mempengaruhi ini; test `test_cross_module.py::test_wizard_margin_product_model_merged_when_both_installed` sudah ada | Perlu dijalankan dgn kedua modul terinstall (dicatat CLAUDE.md, sudah bagian rencana Step 9/10) |
| AC-09-02 | `blocking_transaction_order` tidak muncul di view modul ini | Match | `views/res_config_settings.xml` tidak dalam diff (byte-identik 19.0), field itu memang cuma dideklarasikan di `sale_margin_threshold`'s config settings, tidak direferensikan modul ini | — |
| AC-10-01 | `views/product_template_views.xml` tidak di manifest | Match | `__manifest__.py` `data:` list hanya berisi `security/ir.access.csv`, `views/res_config_settings.xml`, `views/products.xml`, `wizard/wizard_margin_product.xml` — file dead tidak ada di sana | Dikonfirmasi baca langsung manifest |
| AC-10-02 | `pos_session.py` tetap kosong/komentar | Match | Isi file hanya docstring/komentar, tidak ada class/override — dikonfirmasi baca langsung | — |
| AC-10-03 | `controllers.py` tidak disentuh | Match | Seluruh isi file di-comment, `__init__.py` masih no-op import | — |

**Ringkasan §C:** 0 Gap kode ditemukan (37/37 AC behaviorally Match atau N/A-by-design). 6 AC menandai gap TEST (bukan gap kode) — konsisten `05a` sendiri, tidak ada yang baru ditemukan review ini di luar yang sudah dicatat, kecuali `ISS-03` (kesalahan kutipan nilai boolean di teks AC-02-01/02, bukan gap perilaku).

## D. Cek Khusus Migrasi — P1 Fidelity

- [x] Tidak ada perubahan behavior yang tidak disengaja — semua deviasi dari source (branch `migration/19.0`) sudah eksplisit tercatat & disetujui (`MF-29`, `MF-34`/`MF-41`, `MF-38`, `DIFF-04`/`MF-24` retensi sengaja, `MF-40` efek samping API wajib) — lihat §B/§C di atas untuk jejak masing-masing.
- [ ] Ada — daftar & keputusan: —

**Cek tabrakan nama method dengan Odoo core (WAJIB, DUA ARAH):**

**Arah 1 (method sama nama, model sama, risiko override-silent-tanpa-`super()`):** Modul mendefinisikan
method baru berikut pada model yang di-`_inherit`: `product.category` (tidak ada method baru selain
field), `product.template`/`product.product` (`_compute_margin_sale`, `_compute_minimum_sale_price`,
`_compute_minimum_sale_price_with_tax`, `_inverse_minimum_sale_price`, `action_assign_margin`,
`_set_product_margin_sale`, `_compute_warning`), `pos.config` (`_compute_blocked_warning`). Digrep
penuh nama-nama ini terhadap `D:\Kuncoro\doodex\repo\odoo20\addons\product`,
`...\odoo20\addons\point_of_sale`, `...\odoo20\odoo\addons\base`, dan seluruh
`D:\Kuncoro\doodex\repo\enterprise20` — satu-satunya match (`_compute_warning`) ada di
`odoo/addons/base/models/ir_actions.py` (model `ir.actions.server`, tidak terkait) dan tiga wizard HR
Enterprise (`hr_appraisal`/`l10n_eg_hr_payroll`/`l10n_pk_hr_payroll`, model berbeda total) — **tidak
ada collision pada model yang sama**. Aman.

**Arah 2 (field baru native 20.0 dengan nama sama, yang tidak ada di 19.0):** Field yang
DIDEFINISIKAN modul per model: `product.category` (`margin_sale`), `product.template` (`margin_sale`,
`minimum_sale_price`, `minimum_sale_price_with_tax`), `product.product` (`margin_sale`,
`minimum_sale_price`, `minimum_sale_price_with_tax`, `is_less_minimum_sale`), `pos.config`
(`is_blocked_warning`). Digrep kelima nama field ini ke seluruh `odoo20/addons/product`,
`odoo20/addons/point_of_sale`, dan `enterprise20` — **0 match di luar definisi modul ini sendiri**.
Tidak ada field baru native 20.0 yang bentrok nama.

**Arah 3:** N/A — modul ini tidak melakukan replace-total item registry UI JS (tidak ada pola
`registry.category(...).remove()/add()` di codebase-nya).

- [x] Sudah dicek (ketiga arah) — tidak ada tabrakan nama method/field dengan core/Enterprise, dan
  tidak ada item registry UI replace-total yang callback-nya menyimpang dari kontrak native TARGET
- [ ] Ada tabrakan/penyimpangan ditemukan

## E. Perubahan Tak Tertelusuri (di luar spec)

- [ ] Tidak ada perubahan yang tidak tertelusuri ke spec
- [x] Ada — daftar & keputusan: `MF-40`..`MF-44` (5 fix) ditemukan & diterapkan di Step 9 (Dev
  Testing), SETELAH `03_MIGRATION_SPEC.md` (Step 3) selesai ditulis — bukan celah proses Step 8, tapi
  urutan eksekusi non-normal yang sudah dicatat & disetujui dev sejak awal sesi (`CLAUDE.md`
  "Status saat ini", `06c_IMPLEMENTATION_LOG.md` §"Catatan proses"). Semua 5 fix punya jejak lengkap
  di `FINDINGS.md` dan `06c_IMPLEMENTATION_LOG.md` — tertelusuri ke gap migrasi konkret (API
  dihapus/di-rename di native 20.0, atau bug test fixture), bukan perubahan business-logic
  diskresioner. Tidak ada tindakan lanjutan dibutuhkan selain housekeeping `DIFF-08` di §B.

## F. Kontribusi ke Knowledge Base

- [ ] Tidak ada temuan baru yang perlu dicatat
- [x] Ada — dicatat ke `migration-tool/migration-records/pos-margin-sale_19.0_20.0/SUMMARY.md`
  (kandidat, belum ditulis ulang di sesi ini — sudah ada kandidat `MF-28`/`MF-29` dari Step 1/2):
  - **CAND — `ir.config_parameter.get_param()`/`set_param()` dihapus total di 20.0** (`MF-40`) —
    general Odoo 20.0, bukan spesifik modul ini, relevan untuk migrasi LAIN manapun yang memakai
    `config_parameter=` pada `Boolean` field. Belum ada di `knowledge/version-diffs/19-to-20.md`
    per pengecekan Step 1 — kandidat kuat untuk promosi.
  - **CAND — CSS class `.receipt-screen`→`.feedback-screen` (`ReceiptScreen`→`FeedbackScreen`)** di
    `point_of_sale` 20.0 (`MF-44`) — general untuk modul migrasi POS manapun yang punya tour test
    menyentuh layar setelah validasi pembayaran.
  - **CAND — `t[@t-slot='default']`→`t[@t-call-slot='default']`** rename Owl slot syntax di
    `point_of_sale` 20.0 (`MF-41` bagian pertama) — general untuk modul POS manapun yang xpath ke
    slot Owl.
  - **CAND — lesson proses:** field compute `store=True` yang di-`create()`/`write()` di
    `setUpClass()` `HttpCase`/Tour test WAJIB `env.flush_all()` sebelum request HTTP dari
    Chrome/browser tour membaca nilainya (`MF-43` koreksi final) — lesson metodologi testing, bukan
    API Odoo spesifik, tapi relevan lintas-project migrasi manapun yang pakai Tour test.

## G. Verdict

- Ringkasan Issues: 0 🔴 · 1 🟡 (`ISS-01`) · 2 🔵 (`ISS-02`, `ISS-03`)
- [x] ✅ Lulus — tidak ada 🔴, lanjut ke step 9 (lanjutan — modul ini sudah lolos Step 9 dev-testing
  per `06c_IMPLEMENTATION_LOG.md`, jadi verdict ini juga membuka jalan ke Step 10 QA Testing)
- [ ] ❌ Ditolak

**Issue 🔴 yang wajib difix sebelum lanjut:** Tidak ada.

**Rekomendasi non-blocking dibawa ke Step 9/10 (bukan syarat gate ini, tapi jangan hilang dari radar):**
1. `ISS-01`/AC-07-04 — tambah `TransactionCase` test dedup kolom lintas-modul (`test_cross_module.py`).
2. AC-05-01 (`MF-34`) — tour test baru dengan combo product sungguhan (`available_in_pos` + combo
   config), verifikasi visual live belum pernah dilakukan.
3. AC-03-03/AC-04-03 (gap test baru, bukan carry-forward) dan AC-03-05/AC-04-03 (`BSL-018`,
   carry-forward TIGA project migrasi berturut-turut) — direkomendasikan eskalasi eksplisit ke dev
   sebelum Step 9 project ini benar-benar ditutup formal, supaya `BSL-018` tidak ter-carry-forward
   keempat kalinya secara diam-diam (sesuai flag `05a_MIGRATION_ACCEPTANCE_CRITERIA.md` §Ringkasan
   Cakupan sendiri).
4. `DIFF-08` di `03_MIGRATION_SPEC.md` §2 — update housekeeping teks (masih bilang "tidak ada
   tindakan", padahal `MF-41` menemukan & memperbaiki 2 bug nyata di xpath yang sama).
5. `ISS-03` — perbaiki nilai boolean `is_product` yang dikutip di AC-02-01/AC-02-02
   (`05a_MIGRATION_ACCEPTANCE_CRITERIA.md`) di sesi revisi baseline berikutnya.
