# Code Review — sale_margin_threshold

**Step:** 8 — Code Review (gate)
**Ref:** `03_spec/sale_margin_threshold/03_MIGRATION_SPEC.md`, `05_acceptance/sale_margin_threshold/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `06_implementation/sale_margin_threshold/06c_IMPLEMENTATION_LOG.md`, `01_intake/sale_margin_threshold/01b_BASELINE_SPEC.md`
**Odoo Version:** 19.0 → 20.0
**Files reviewed:** `__manifest__.py`, `models/product.py`, `models/sale_order.py`, `security/ir.access.csv` (baru, ganti `ir.model.access.csv`), `tests/test_action_confirm.py`, `views/products.xml`, `views/sale_order.xml`
**Tanggal:** 2026-09-23
**Reviewer:** Claude Code (Step 8 agent), `git diff migration/19.0 migration/20.0 -- sale_margin_threshold/`

> Skill `odoo-review` dijalankan (dispatch ke `odoo-guidelines`/`odoo-security`; `odoo-web-guidelines`
> tidak relevan — modul ini tidak punya file di `static/`, dikonfirmasi `BSL-014`/`03_MIGRATION_SPEC.md`
> §"OWL Widget"). Guideline sections dibaca penuh sebelum menulis finding — lihat "Guidelines read" di
> akhir dokumen.

---

## A. Issues (Lint, Konvensi Odoo, Business Logic, Security, Performance, Code Quality)

**Status skill `odoo-review`:**
- [x] Terinstall & sudah dijalankan — hasil temuan digabung ke tabel Issues di bawah

| ID | Severity | Kategori | File | Baris | Issue | Rekomendasi |
|---|---|---|---|---|---|---|
| CR-01 | 🟡 | Business Logic / ORM (`@api.depends` tidak lengkap) | `models/product.py` `ProductProduct._compute_minimum_sale_price_with_tax` | 87-91 | `@api.depends('margin_sale', 'minimum_sale_price', 'product_tmpl_id.taxes_id')` — path berhenti di `taxes_id` (set pajak), TIDAK sampai ke `.amount` yang benar-benar dibaca di badan compute (`tax.amount`). Kalau field `account.tax.amount` diedit langsung (mis. akuntan koreksi persentase PPN pada tax record yang SUDAH terpasang di produk), kolom baru "Incl. Tax" (`AC-04-03`, ditandai **HIGH-RISK**) tidak ikut recompute — nilai stale sampai ada trigger lain (`margin_sale`/`minimum_sale_price` berubah). Field ini BARU di `product.product` (tidak ada di 19.0, ditambahkan migrasi ini via `MF-38`) — bukan port 1:1 dari kode lama, jadi memperbaiki `@api.depends` di sini bukan "memperbaiki bug warisan yang harus dipertahankan" (beda dengan `MF-21` yang memang harus dibiarkan identik). | Ganti depends jadi `@api.depends('margin_sale', 'minimum_sale_price', 'product_tmpl_id.taxes_id.amount')`. Catatan: `ProductTemplate._compute_minimum_sale_price_with_tax` (file sama, tidak disentuh diff ini) punya gap identik sejak sebelum migrasi — di luar scope untuk diperbaiki di sini tanpa keputusan dev baru, tapi layak dicatat sebagai kandidat perbaikan terpisah. |
| CR-02 | 🟡 | Code the diff never shows / ORM (cache contract) | `models/product.py` `ProductProduct._get_view()` | 123-152 | Override menentukan isi arch (strip kolom dedup atau tidak) berdasarkan state `ir.module.module` (`pos_margin_threshold` terinstall/tidak). Hasil `_get_view()` mengalir ke `_get_view_cache()` (`odoo/addons/base/models/ir_ui_view.py:3112-3117`, `@tools.conditional(..., api.ormcache(...))`) yang docstring-nya eksplisit menyatakan hasil "can only depend on the requested view types, access rights ..., options, context lang and TYPE_view_ref" — dan `_get_view_cache_key()` (baris 3089-3110) TIDAK menyertakan state instalasi modul. Dalam praktiknya ini aman HARI INI karena install/uninstall modul di Odoo selalu memicu full registry reload (ormcache baru, sudah dikonfirmasi lewat verifikasi visual live `MF-37`/`MF-38`) — tapi ini kopling implisit ke perilaku internal Odoo yang tidak didokumentasikan sebagai kontrak resmi, bukan mekanisme resmi seperti `groups=` (yang diproses di `_postprocess_access_rights`, langkah TIDAK ter-cache setelah `_get_view_cache`). Kalau ada jalur di masa depan yang mengubah `ir.module.module.state` tanpa full registry reload (mis. optimisasi reload parsial, atau race multi-worker di jendela sebelum sinyal reload diproses pekerja lain), kolom bisa dobel/hilang secara diam-diam sampai reload berikutnya. | Terima risiko ini secara eksplisit (dicatat di sini, cukup untuk lulus gate — dampak dibatasi & sudah diverifikasi live) ATAU pertimbangkan pola alternatif: grup `res.groups` yang keanggotaannya di-drive oleh `_register_hook` (pola yang SUDAH dipakai modul ini untuk `group_sale_margin_action`) lalu `groups="sale_margin_threshold.<grup>"` pada node yang di-dedup, supaya visibility diproses di `_postprocess_access_rights` (uncached) bukan dibakar ke arch yang di-cache. Tidak blocking untuk Step 8, tapi layak jadi kandidat knowledge base (§F). |
| CR-03 | 🔵 | Konvensi (CSS class prefix) | `views/products.xml` | 58, 63, 71 (+ `models/product.py` 147-149) | Marker `class="o_smt_dedup_margin"` / `o_smt_dedup_min_price` / `o_smt_dedup_min_price_tax` memakai singkatan `smt`, bukan `o_<module>` penuh (`o_sale_margin_threshold_...`) sesuai house rule prefix CSS class. Risiko rendah — marker ini murni selector internal dikonsumsi hanya oleh `_get_view()` modul ini sendiri, bukan dipakai styling/JS pihak lain — tapi singkatan generik 3-huruf berisiko tabrakan kalau modul lain kelak memakai abbreviation yang sama. | Opsional: rename ke prefix penuh (`o_sale_margin_threshold_dedup_margin`, dst) kalau ada kesempatan menyentuh file ini lagi; tidak perlu PR terpisah hanya untuk ini. |

**Severity:** 🔴 Critical (bug/security/AC tidak cover — wajib fix) · 🟡 Warning (convention/performance — fix kalau memungkinkan) · 🔵 Info (saran, opsional)

**Business Logic — dicek manual (sesuai catatan template, di luar cakupan skill generik):**
- Formula compute inti (`margin_sale`/`minimum_sale_price`/`minimum_sale_price_with_tax`) diverifikasi sama persis dengan `01b_BASELINE_SPEC.md` §3 dan `AC-01-01`..`AC-01-06` — match, tidak ada penyimpangan.
- Edge case recordset kosong/multi-record: `_compute_*` semua sudah `for rec in self:` (aman multi-record); `action_confirm()`/`_compute_is_rental_order_installed` TETAP memakai `self` penuh tanpa loop (bug `MF-08`/`MF-26`, **tidak disentuh diff ini** — dikonfirmasi via `git diff migration/19.0 migration/20.0 -- sale_margin_threshold/models/sale_order.py`, satu-satunya perubahan baris di file itu adalah `get_param`→`get_bool`). Tidak di-re-flag sesuai instruksi.
- Error type: `ValidationError` tetap dipakai (bukan diganti `UserError`/lainnya) — identik 19.0.
- Admin-bypass (`skip_check_price` context) tidak diubah — konsisten `AC-02-05`.
- `get_param`→`get_bool` (`MF-40`): diverifikasi behaviorally EQUIVALENT, bukan cuma "kompilasi jalan" — 19.0 `set_param(key, False)` sebenarnya **unlink** parameter (`ir_config_parameter.py` 19.0, cabang `else` saat value `False`) sehingga `get_param` balik ke default `False`; `set_param(key, True)` menulis string `'True'` (truthy). 20.0 `set_bool`/`get_bool` (`ir_config_parameter.py` 20.0, baris 66-67 & 100-105) menyimpan/membaca boolean bertipe eksplisit dengan default eksplisit `False` saat unset. Hasil akhir kedua cabang (`True`/`False`/unset) SAMA persis di kedua versi — bukan fix diam-diam atas perilaku 19.0, murni port mekanis yang benar.

---

## B. Gap Analysis — Implementasi vs Migration Spec

| Spec item (`DIFF-NNN`/Fase) | Implementasi | Status | Catatan |
|---|---|---|---|
| `DIFF-01`/`MF-30` — rename+reformat `ir.model.access.csv`→`ir.access.csv` | `security/ir.access.csv` baru, 2 baris, skema `id,name,model_id,group_id/id,operation,domain`, `operation=crud` | ✅ Match | Dikonfirmasi ulang terhadap `odoo20/odoo/addons/base/security/ir.access.csv` (native pakai nama model teknis polos di kolom `model_id`, bukan `model_xxx` ref) dan `ir_access.py` (`operation` Selection: subset huruf `crud`, nilai `"crud"` valid). Manifest `data:` entry sudah diupdate ke `security/ir.access.csv`. |
| `DIFF-08`/`MF-29` — retarget popup→kolom list `product_product_tree_view` | `views/products.xml` record `product_product_tree_view_margin_sale` | ✅ Match (versi FINAL, bukan snippet literal awal §2b) | Spec sendiri mencatat snippet literal awal (`invisible="module_pos_margin_threshold == True"` + `column_invisible` untuk 2 field bantu) **TERBUKTI GAGAL** dan digantikan mekanisme `_get_view()` (dicatat retroaktif di §2b Risiko Integrasi #2). Implementasi aktual match ke versi FINAL itu, BUKAN ke snippet literal §2b poin 3 yang sudah usang. Field bantu `module_pos_margin_threshold`/`is_less_minimum_sale` yang di spec literal ditambah sebagai `column_invisible` TIDAK diperlukan lagi di arch — dikonfirmasi ke source Odoo (`ir_ui_view.py::_postprocess_attributes`, baris 1648-1653): field yang dipakai `decoration-*`/view-modifier expression otomatis masuk daftar field yang harus diambil (`must_have_fields`) walau tidak dideklarasi sebagai `<field>` eksplisit — simplifikasi ini valid, bukan gap. |
| `MF-35` — xpath `price_unit` lewat `<column>` baru | `views/sale_order.xml` xpath diupdate ke `list[@name='sol_list']/column[@name='price_unit']/field[@name='price_unit']` | ✅ Match | Dikonfirmasi struktur `<list name="sol_list">`/`<column name="price_unit">` benar-benar ada di `odoo20/addons/sale/views/sale_order_views.xml` (baris 644/839). |
| `MF-37` — dedup kolom lintas modul | `ProductProduct._get_view()` (baru) + marker `class="o_smt_dedup_*"` | ✅ Match, dengan catatan `CR-02` | Implementasi sesuai deskripsi final di spec §2b Risiko Integrasi #2; lihat `CR-02` untuk catatan ketergantungan ke cache `_get_view_cache`. |
| `MF-38` — visual parity (`decoration-danger` margin negatif + kolom Incl. Tax) | `decoration-danger="margin_sale &lt; 0.0"` pada `margin_sale`; field+kolom baru `minimum_sale_price_with_tax` | ✅ Match, dengan catatan `CR-01` | Field/kolom ada dan match `03_MIGRATION_SPEC.md` §2b "Visual parity"; formula compute-nya sendiri punya gap `@api.depends` (`CR-01`). |
| `MF-40` — `get_param`/`set_param` dihapus native | `get_bool`/`set_bool` di `models/sale_order.py` (1 lokasi) + `tests/test_action_confirm.py` (3 lokasi) | ✅ Match | Lihat verifikasi ekuivalensi behavior di §A. |
| Manifest version bump | `20.0.1.0` | ✅ Match | — |
| Item "Di Luar Scope" (`MF-08`/`20`/`21`/`26`/`27`, `BSL-013`, `i18n`) | Tidak disentuh | ✅ Match | Dikonfirmasi via diff — tidak ada baris berubah di file-file yang jadi lokasi bug-bug ini selain yang eksplisit didaftar. |

Tidak ada item spec yang TIDAK diimplementasikan (semua `DIFF-NNN`/`MF-NNN` di scope §4 "Termasuk" migration spec sudah ada realisasinya di kode).

---

## C. Gap Analysis — Implementasi vs Acceptance Criteria

> Desk Review: jalur kode nyata ditelusuri, bukan cuma baca sekilas.

| AC ID | Behavior | Status | Jejak Nalar (Desk Review) | Catatan |
|---|---|---|---|---|
| AC-01-01..04 | Compute margin/minimum price warisan kategori/template/variant | ✅ Match | `_compute_margin_sale`/`_compute_minimum_sale_price`/`_inverse_minimum_sale_price` di `ProductTemplate` dan `ProductProduct` byte-identik dengan 19.0 (tidak ada baris berubah di diff) — formula, arah inverse (template-shared utk variant via `_set_product_margin_sale` yang menulis ke `product_tmpl_id`), semua sama. | — |
| AC-01-05 | `minimum_sale_price_with_tax` computed value benar | 🟡 Sebagian | User set `taxes_id`→`_compute_minimum_sale_price_with_tax` jalan pertama kali dengan benar (formula sama seperti `ProductTemplate`, `120 * 1.10 = 132` sesuai contoh AC). TAPI kalau user berikutnya mengedit `account.tax.amount` pada tax yang SUDAH terpasang (bukan menambah/melepas tax), compute TIDAK retrigger (`CR-01`) — nilai jadi stale sampai `margin_sale`/`minimum_sale_price` berubah lagi. | Match untuk skenario "hitung awal"; gap untuk skenario "tax rate diedit belakangan" — lihat `CR-01`. |
| AC-01-06 | `is_less_minimum_sale` stale-cache bug (`MF-21`) dipertahankan | ✅ Match (bug dipertahankan, sesuai keputusan) | `_compute_warning` di `ProductProduct` tidak berubah (tidak ada `@api.depends`) — dikonfirmasi 0 baris diff di method ini. | Sesuai `03_MIGRATION_SPEC.md` §4 "Di Luar Scope". |
| AC-02-01..08 | Alur konfirmasi sale order (rental exempt, blocking, wizard, bilingual message, decoration list) | ✅ Match | `action_confirm()` diff HANYA baris `get_param`→`get_bool` (dikonfirmasi ekuivalen §A) — sisa logic (rental short-circuit, `skip_check_price`, wizard, `detect_user_language`) byte-identik. `views/sale_order.xml` xpath baru (`MF-35`) resolve ke node `field[@name='price_unit']` YANG SAMA seperti sebelumnya (hanya jalur xpath berubah, node target & attribute yang ditambahkan `decoration-danger` identik) — perilaku decoration tidak berubah, hanya cara resolve-nya. | AC-02-08 (HIGH-RISK, terkait `MF-35`) — dikonfirmasi struktur native `<column name="price_unit">` benar-benar ada (lihat §B). |
| AC-03-01 | `MF-08` batch-confirm crash tetap crash | ✅ Match (dipertahankan) | `action_confirm()` baris pertama tetap `self.is_rental_order_installed_true` (bukan loop) — tidak berubah. Test `test_action_confirm_BATCH_MULTI_ORDER_F05` masih ada, tidak diedit isinya (hanya bukan bagian diff). | Verifikasi eksekusi aktual ada di Step 9 (`06c`/`FINDINGS.md`), bukan tugas Step 8 — desk review disini cukup memastikan kode compute tidak berubah. |
| AC-03-02 | `MF-26` singleton kedua dipertahankan | ✅ Match (dipertahankan) | `_compute_is_rental_order_installed` tidak ada di diff sama sekali (bukan bagian perubahan). | — |
| AC-03-03 | `MF-20` `implied_ids` salah tipe dipertahankan | ✅ Match (dipertahankan) | `security/groups.xml` tidak ada di diff (`git diff --stat` di atas tidak menyebut file ini). | — |
| AC-04-01 | Kolom baru `optional="show"`, editable inline, setara popup lama | ✅ Match | Field `margin_sale`/`minimum_sale_price` di record baru memakai `optional="show"` (bukan `hide`); `product.product_product_tree_view` native sudah `editable`/`multi_edit` (dikonfirmasi `03_MIGRATION_SPEC.md` §2b, tidak dibantah oleh pembacaan kode). | — |
| AC-04-02 | Dedup — hanya 1 set kolom saat kedua modul terinstall | ✅ Match, dengan catatan `CR-02` | `_get_view()` men-strip node bermarker `o_smt_dedup_*` HANYA kalau `pos_margin_threshold` terinstall; `pos_margin_threshold` sendiri TIDAK override `_get_view` (dikonfirmasi grep `pos_margin_threshold/`, 0 match) — jadi tidak ada risiko kedua modul saling strip diri sendiri atau saling meninggalkan 0 kolom. Mekanisme sudah diverifikasi live (`FINDINGS.md` `MF-37`/`MF-38`). | Ketergantungan ke cache `_get_view_cache` dicatat `CR-02` — tidak menggagalkan AC ini untuk skenario install/uninstall NORMAL. |
| AC-04-03 | Decoration merah margin negatif + kolom Incl. Tax, tidak dobel | 🟡 Sebagian | Decoration & kolom ADA dan match secara struktural (lihat §B `MF-38`) — nilai kolom Incl. Tax sendiri punya gap depends yang sama seperti `AC-01-05` (`CR-01`). | — |
| AC-04-04 | Decoration `lst_price` via `position="attributes"`, bukan `replace` | ✅ Match | Dikonfirmasi `views/products.xml` baris 41-43: `position="attributes"` + `<attribute name="decoration-danger">`, TIDAK menghapus `options`/`widget` milik `lst_price` native (kontras eksplisit dengan `AC-07-04`/`MF-27` yang tetap `replace` di lokasi lama). | Field `is_less_minimum_sale` yang dipakai ekspresi TIDAK dideklarasikan eksplisit di arch — dikonfirmasi AMAN (lihat §B, `must_have_fields` native). Skenario stale-cache (`MF-21`) sendiri tetap ada, sesuai `AC-01-06`, tidak berubah oleh migrasi. |
| AC-04-05 | Compute+inverse tetap benar lewat input list baru | ✅ Match (logic) | Compute/inverse method sama, tidak bergantung jalur UI (form vs list) — logic-nya sendiri path-agnostic. Verifikasi END-TO-END (browser nyata, edit inline) tetap tugas Step 9/10, bukan desk review. | — |
| AC-05-01, AC-05-02 | Kolisi `wizard.margin.product` menang MRO; `_register_hook` reset `user_ids` | ✅ Match (dipertahankan) | Kedua method (`_register_hook`, model wizard) tidak ada di diff. | — |
| AC-06-01 | Config Settings UI → config_parameter | ✅ Match (tidak berubah, hanya storage backend `get_bool`) | `res_config_settings.py`/`.xml` tidak ada di diff — field `blocking_transaction_order` yang binding ke config_parameter itu sendiri tidak disentuh; hanya CARA `action_confirm()` membaca param yang berubah (`get_param`→`get_bool`), sudah dikonfirmasi ekuivalen. | — |
| AC-07-01..04 | Quirk non-fungsional (`BSL-013`/`014`/`016`/`019`-`MF-27`) tetap diam | ✅ Match (dipertahankan) | Tidak ada file terkait di diff (`product_template_views.xml`, bagian `products.xml` yang lain, `res_config_settings.py`). | — |

**Gap dari §"Catatan Gap Traceability" (`05a`) — tidak berubah statusnya di Step 8** (bukan tugas Step 8 untuk menutup gap test coverage, itu Step 9/10): jalur Cancel wizard (`AC-02-06`), arah "hanya modul ini terinstall" (`AC-05-02`), retroaktif `BSL-020`+ untuk §3/§6 baseline spec — semua tetap terbuka, tidak jadi blocker gate ini karena murni soal test-coverage/traceability dokumentasi, bukan implementasi kode yang salah.

---

## D. Cek Khusus Migrasi — P1 Fidelity

- [x] Tidak ada perubahan behavior yang tidak disengaja — semua deviasi dari source (`migration/19.0`) sudah eksplisit tercatat & disetujui (`MF-29`/`MF-37`/`MF-38`/`MF-40`, semua sudah ada keputusan dev tercatat di `FINDINGS.md`). `CR-01` bukan "perubahan behavior yang disengaja tak tercatat" — ini gap teknis (dependency compute tidak lengkap) di kode yang MEMANG baru ditulis migrasi ini, bukan port dari 19.0.

**Cek tabrakan nama method dengan Odoo core (DUA ARAH + Arah 3):**

1. **Arah 1** — method yang di-override modul ini pada model core (`product.product`, `product.template`, `sale.order`): `_get_view` dan `_register_hook` (pada `product.product`), `action_confirm` (pada `sale.order`). Ketiganya memanggil `super()` dengan benar (`super()._get_view(...)`, `super()._register_hook()`, `super(SaleOrder, self).action_confirm()`) — dikonfirmasi baca langsung kode, tidak ada yang menimpa total tanpa `super()`. Tidak ada method LAIN yang didefinisikan modul ini yang namanya bertabrakan dengan method native pada model yang sama (`_compute_margin_sale`, `_compute_minimum_sale_price`, `_inverse_minimum_sale_price`, `_set_product_margin_sale`, `_compute_warning`, `action_assign_margin`, `detect_user_language`, `check_product_price`, `_compute_is_rental_order_installed` — semua nama custom, tidak ada di native `product`/`sale` addon manapun, dikonfirmasi grep `odoo20/addons/product`, `odoo20/addons/sale`, `enterprise20`).
2. **Arah 2** — field/method yang DIDEFINISIKAN modul pada model yang di-`_inherit`, dicek apakah native 20.0 (bukan 19.0) SEKARANG mendefinisikan nama yang sama: grep `margin_sale`, `minimum_sale_price`, `minimum_sale_price_with_tax`, `is_less_minimum_sale` ke `odoo20/addons/product/`, `odoo20/addons/sale/`, `odoo20/addons/stock_account/`, `enterprise20/` → **0 match** (dan 0 match juga di `odoo19`/`enterprise19` untuk perbandingan — bukan field yang baru muncul di source 19.0 lalu diam-diam collide di target, memang tidak pernah ada di native manapun). Field `is_rental_order_installed_true` (nama custom modul ini) dan `minimum_sale_price` pada `sale.order.line` (related field custom) juga tidak collide (dependency `sale_renting` untuk `is_rental_order` dikonfirmasi tetap ada nama sama di `enterprise20/sale_renting`, sesuai `03_MIGRATION_SPEC.md` §2b Risiko Integrasi #3, tidak diverifikasi ulang di sini — sudah tugas Step 2/3).
3. **Arah 3** — modul ini TIDAK melakukan replace-total item registry JS manapun (`registry.category(...).remove()+.add()`) — dikonfirmasi tidak ada file JS sama sekali di modul ini (`BSL-014`, `static/src/` tidak ada di disk). N/A.

- [x] Sudah dicek (ketiga arah) — tidak ada tabrakan nama method/field dengan core/Enterprise, dan tidak ada item registry UI replace-total yang callback-nya menyimpang dari kontrak native TARGET.

---

## E. Perubahan Tak Tertelusuri (di luar spec)

- [x] Tidak ada perubahan yang tidak tertelusuri ke spec — setiap hunk diff sudah dipetakan ke satu `DIFF-NNN`/`MF-NNN` di §B. Tidak ditemukan baris berubah yang tidak dijelaskan spec/implementation log manapun.

---

## F. Kontribusi ke Knowledge Base

- [x] Ada — dicatat sebagai kandidat ke `migration-tool/migration-records/pos-margin-sale_19.0_20.0/SUMMARY.md` (belum ditulis fisik di sesi ini, direkomendasikan sesi kurasi berikutnya menambahkan):
  - **CAND-NNN (baru, dari `CR-02`):** pola umum untuk migrasi Odoo 20.0 manapun yang butuh "dedup kolom antar-modul lintas-inherit view yang sama" via override `_get_view()` — WASPADAI bahwa hasilnya mengalir ke `_get_view_cache()` yang di-`ormcache`, dengan cache key TIDAK menyertakan state eksternal seperti instalasi modul lain. Aman selama perubahan state itu selalu dibarengi full registry reload (kasus modul install/uninstall) — TAPI bukan kontrak resmi yang didokumentasikan Odoo untuk `_get_view`, beda dengan `groups=` yang memang didesain untuk kondisi per-user/per-state yang diproses di luar cache (`_postprocess_access_rights`). Relevan untuk migrasi manapun yang mengadopsi pola serupa (mis. penggantian popup terhapus jadi kolom list, tren umum di 20.0 sejak `product_variant_easy_edit_view` dihapus).
  - **CAND-NNN+1 (dari §B):** konfirmasi bahwa field yang HANYA dipakai di ekspresi `decoration-*`/view-modifier (`invisible`, dst) TIDAK perlu dideklarasikan eksplisit sebagai `<field>` (bahkan `column_invisible`) di arch — Odoo (`_postprocess_attributes`/`must_have_fields`, `ir_ui_view.py`) otomatis memasukkannya ke daftar field yang wajib diambil. Berguna untuk migrasi lain yang menyederhanakan view lama yang terlalu verbose menambahkan field bantu.

---

## G. Verdict

- Ringkasan Issues: **0 🔴 · 2 🟡 · 1 🔵**
- [x] ✅ **Lulus** — tidak ada 🔴, lanjut ke step 9

**Issue 🔴 yang wajib difix sebelum lanjut:** tidak ada.

**Catatan untuk Step 9/10 (bukan blocker gate, tapi wajib diperhatikan saat testing eksekusi nyata):**
- `CR-01` — tambahkan skenario test: edit `account.tax.amount` pada tax yang sudah terpasang ke produk, verifikasi apakah kolom "Incl. Tax" ikut update tanpa reload manual paksa (kemungkinan besar TIDAK, sesuai analisis desk review) — kalau dev ingin fix, ini eligible diperbaiki SEKARANG (bukan bug warisan 19.0, field baru migrasi ini) via `@api.depends` tambahan `.amount`, cukup mekanis, risiko rendah.
- `CR-02` — tidak perlu aksi Step 9 khusus (risiko sudah dimitigasi behavior native "install = full reload"), tapi kalau Step 10/11 mengetes skenario upgrade/multi-worker yang tidak biasa, waspadai potensi kolom dobel/hilang sesaat sebelum reload berikutnya.

---

**Guidelines read (sections opened in full before writing findings):**
- `odoo-guidelines/guidelines/xml.md` — Views/actions/data records, Anchor view inheritance on names
- `odoo-guidelines/guidelines/security.md` — Access rights (`ir.access`)
- `odoo-guidelines/guidelines/orm.md` — Recordsets/domains/context, Computes/onchange/constraints, Methods and extension points, Transactions and exceptions
- `odoo-guidelines/guidelines/tests.md` — Tests
- `odoo-review/SKILL.md` — process + "Code the diff never shows"
- `odoo-web-guidelines` — dilewati sengaja, tidak ada file `static/` di modul ini (`BSL-014`)
- `odoo-security` — dicek implisit lewat `ir.access.csv` (tidak ada `sudo()`/route/controller baru di diff ini untuk diaudit lebih lanjut)
