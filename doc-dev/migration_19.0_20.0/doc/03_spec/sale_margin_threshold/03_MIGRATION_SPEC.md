# Migration Spec (Teknis) — sale_margin_threshold

**Step:** 3 — Migration Spec
**Versi:** 19.0 → 20.0
**Ref:** `02_diff/sale_margin_threshold/02_DIFF_ANALYSIS.md`, `FINDINGS.md` (`MF-08`, `MF-20`, `MF-21`, `MF-26`, `MF-27`, `MF-29`, `MF-30`)
**Tanggal:** 2026-09-22

> Dokumen ini memandu IMPLEMENTASI (step 6). Ini **bukan** dasar testing/acceptance criteria —
> itu datang dari `01b_BASELINE_SPEC.md` (step 1) dan kode 19.0 yang berjalan (branch
> `migration/19.0`). Lihat step 5.

---

## 1. Ringkasan Strategi

Berbeda dari migrasi 18.0→19.0 sebelumnya (yang tidak menemukan blocker teknis apapun untuk modul
ini), migrasi 19.0→20.0 ini punya **dua perubahan wajib install-blocking**:

1. **`DIFF-01`/`MF-30`** — rename mekanis `security/ir.model.access.csv` → `security/ir.access.csv`
   + reformat skema kolom (`perm_read/write/create/unlink` → `operation`+`domain`). Sempit, tidak
   butuh keputusan desain, bisa dieksekusi murni mekanis.
2. **`DIFF-08`/`MF-29`** — record `product_variant_easy_edit_view_margin_sale` (inherit
   `product.product_variant_easy_edit_view`, view yang **dihapus total** di native 20.0) harus
   diganti total dengan record baru yang inherit `product.product_product_tree_view` (list "Product
   Variants"), menambah kolom `margin_sale`/`minimum_sale_price` + `decoration-danger` pada
   `lst_price`. **Keputusan desain SUDAH DIAMBIL dev (2026-09-21, dicatat di `FINDINGS.md` `MF-29`)**
   — dokumen ini menuliskan spec konkret untuk arah itu, bukan mengevaluasi ulang alternatif lain
   (mis. retarget ke `product_normal_form_view`).

Sisanya murni port identik — tidak ada perubahan struktural di `sale`/`product`/`stock_account`
yang mempengaruhi cara modul ini di-`_inherit`/dipanggil (dikonfirmasi `DIFF-02`/`DIFF-03`/`DIFF-04`/
`DIFF-09`/`DIFF-10`). Empat bug/quirk `[DIWARISI-SOURCE]` (`MF-08`, `MF-20`, `MF-21`, `MF-26`,
`MF-27`) **dipertahankan identik, TIDAK diperbaiki** — lihat §4 "Di Luar Scope".

## 2. Strategi per File/Simbol (ringkasan umum)

| File/simbol | Ref `DIFF-NNN` | Strategi migrasi | Risiko | Ref `BSL-NNN` |
|---|---|---|---|---|
| `__manifest__.py` `version` | — | Bump ke `20.0.1.0` | Tidak ada | — |
| `__manifest__.py` `data` (nama file security) | `DIFF-01` | Ganti entry `'security/ir.model.access.csv'` → `'security/ir.access.csv'` | Rendah — lupa update manifest = file baru tidak termuat | — |
| `security/ir.model.access.csv` → `security/ir.access.csv` | `DIFF-01`/`MF-30` | Rename file + reformat skema kolom, lihat §2b poin 1 untuk isi persis | Rendah — mekanis, skema sudah dikonfirmasi dari `odoo20/odoo/addons/base/security/ir.access.csv` | — |
| `views/products.xml` record `product_variant_easy_edit_view_margin_sale` | `DIFF-08`/`MF-29` | **Ganti total** jadi record baru inherit `product.product_product_tree_view`, lihat §2b poin 2 untuk XML persis | Sedang — view baru, perlu verifikasi visual Step 10 (sudah dicatat di `MF-29`) | `BSL-019` |
| `views/products.xml` record `product_template_inherit_sale_margin_threshold` (`inherit_id="product.product_template_form_view"`) | `DIFF-05` | **Tidak ada perubahan** — view target masih ada, `position="replace"` pada `list_price` tetap dipertahankan apa adanya (quirk `MF-27`, bukan diperbaiki) | Tidak ada aksi (bug lama dipertahankan) | `BSL-019` |
| `views/product_template_views.xml` record `product_template_inherit_sale_margin_threshold` (`inherit_id="product.product_template_only_form_view"`) | `DIFF-06` | **Tidak ada perubahan** — tetap inert (kalah XML-ID vs `products.xml`, `BSL-013`), dipertahankan identik | Tidak ada aksi (bug lama dipertahankan) | `BSL-013` |
| `models/sale_order.py` override `action_confirm()` | `DIFF-02` | **Tidak ada perubahan** — `MF-08` dipertahankan (keputusan dev 2026-08-27) | Tidak ada aksi (bug lama dipertahankan) | `BSL-009` |
| `models/sale_order.py` `_compute_is_rental_order_installed` | `DIFF-03` | **Tidak ada perubahan** — `MF-26` dipertahankan, belum ada keputusan dev untuk fix | Tidak ada aksi (bug lama dipertahankan) | `BSL-011` |
| `models/product.py` `_register_hook()` | — | **Tidak ada perubahan** — `user_ids` (API 20.0) sudah dipakai sejak project 18.0→19.0 (`MF-17`), tidak ada rename baru | Tidak ada | `BSL-010` |
| `security/groups.xml` `implied_ids` | — | **Tidak ada perubahan** — `MF-20` dipertahankan, belum ada keputusan dev | Tidak ada aksi (bug lama dipertahankan) | `BSL-017` |
| `models/product.py` `_compute_warning` (`is_less_minimum_sale`) | — | **Tidak ada perubahan** — `MF-21` dipertahankan (tanpa `@api.depends`), belum ada keputusan dev | Tidak ada aksi (bug lama dipertahankan) | `BSL-018` |
| `models/res_config_settings.py` | `DIFF-04` | Tidak ada perubahan | Tidak ada | — |
| `views/res_config_settings.xml` | `DIFF-10` | Tidak ada perubahan (block anchor tidak berubah) | Tidak ada | — |
| `views/sale_order.xml` record `view_order_form_inherit_sale` | `MF-35` | **Update retroaktif (Step 4, 2026-09-22):** file ini TIDAK masuk cakupan eksplisit Step 2/3 formal — baru ketahuan install-blocking lewat smoke-install Docker (2026-09-22, di luar Step 2/3), langsung diperbaiki. Native 20.0 membungkus `price_unit` di `<column name="price_unit">` baru pada list `sale.order.line` (sengaja, komentar native menyebut modul seperti `sale_margin` sebagai target); xpath lama ke `price_unit` langsung tidak resolve. Fix: xpath diupdate mengikuti struktur `<column>` baru. Diverifikasi install sukses di Docker 20.0. | Kritis kalau tidak dikerjakan (install-blocking) — rendah setelah fix, murni mekanis, **RESOLVED** | — |
| `wizard/sale_confirmation.py`, `wizard/wizard_margin_product.py` | — | Tidak ada perubahan (pola `self.env.context.get(...)`/`self.env[active_model]` tetap valid 20.0) | Tidak ada | `BSL-005` |
| `tests/test_action_confirm.py`, `tests/test_cross_module.py` | — | Tidak ada perubahan kode wajib — tetap jadi baseline eksekusi Step 9 (lihat `01a_MIGRATION_INTAKE.md` §4, path `doc-dev/backfill/`) | Tidak ada | `BSL-009` |

## 2b. Risk Analysis Terstruktur (detail, per kategori)

> Analisis, bukan kode migrasi. Kode konkret di bawah ini adalah **spesifikasi untuk Step 6**
> (bukan dieksekusi di step ini) — ditulis literal karena kedua item (`DIFF-01`/`DIFF-08`) sudah
> punya arah teknis/desain yang pasti, tidak ada ambiguitas tersisa yang perlu dieksplorasi ulang
> saat implementasi.

### Critical Migration Blockers
*(Mencegah instalasi atau operasi inti di 20.0)*

| # | Isu | Lokasi | Rujukan knowledge base |
|---|---|---|---|
| 1 | Manifest version — harus `20.0.x.x` | `__manifest__.py:17` | `knowledge/version-diffs/19-to-20.md` |
| 2 | `ir.model.access.csv` → `ir.access.csv` — model Python lama (`ir.model.access`) tidak ada lagi di 20.0, nama model target di-load dari **nama file**, bukan isi. File lama akan mencoba `env['ir.model.access']` → gagal. **Install-blocking total.** | `security/ir.model.access.csv` | `knowledge/version-diffs/19-to-20.md`, `FINDINGS.md` `MF-30`, `02_DIFF_ANALYSIS.md` `DIFF-01` |
| 3 | `product.product_variant_easy_edit_view` dihapus total (termasuk versi core `stock`-nya sendiri) — `ir.ui.view` dengan `inherit_id` yang tidak resolve raise error saat load data XML. **Install-blocking total.** | `views/products.xml` record `product_variant_easy_edit_view_margin_sale` | `FINDINGS.md` `MF-29`, `02_DIFF_ANALYSIS.md` `DIFF-08` |

**Priority:** HIGH — perbaiki #2 dan #3 sebelum runtime testing apapun; tanpa keduanya modul tidak
akan install sama sekali di 20.0.

#### Spesifikasi #2 — `security/ir.access.csv` (isi persis)

Skema dikonfirmasi langsung dari `odoo20/odoo/addons/base/security/ir.access.csv` (header baris 1)
dan `odoo20/odoo/addons/base/models/ir_access.py` (field `model_id` = Many2one ke `ir.model`,
`operation` = Selection kombinasi huruf `c`/`r`/`u`/`d`, `domain` = Char, kolom kosong untuk baris
permission murni tanpa domain). Kolom `model_id` diisi **nama teknis model** (bukan external ID
`model_xxx` seperti skema lama) — konsisten dengan contoh native (`decimal.precision`, `ir.cron`,
dst di file yang sama).

**Hapus** `sale_margin_threshold/security/ir.model.access.csv`, **buat**
`sale_margin_threshold/security/ir.access.csv`:

```csv
id,name,model_id,group_id/id,operation,domain
access_sale_confirmation_wizard,sale_margin_threshold.sale_confirmation_wizard,sale.confirmation.wizard,base.group_user,crud,
access_wizard_margin_product,sale_margin_threshold.wizard_margin_product,wizard.margin.product,base.group_user,crud,
```

Catatan konversi: `perm_read=perm_write=perm_create=perm_unlink=1` (keempatnya `1` di file lama) →
`operation=crud` (semua 4 operasi, urutan huruf `c`/`r`/`u`/`d` mengikuti konvensi native), `domain`
dikosongkan (baris permission murni, bukan `ir.rule` gabungan). Kolom `name` (nilai
`sale_margin_threshold.sale_confirmation_wizard`/`sale_margin_threshold.wizard_margin_product`)
**tidak berubah** dari file lama.

`__manifest__.py` — ganti baris `data`:
```python
'data': [
    'security/groups.xml',
    'security/ir.access.csv',   # was: 'security/ir.model.access.csv'
    'views/product_template_views.xml',
    'views/products.xml',
    'views/res_config_settings.xml',
    'views/sale_order.xml',
    'wizard/sale_confirmation.xml',
    'wizard/wizard_margin_product.xml',
],
```

#### Spesifikasi #3 — Retarget `product_variant_easy_edit_view_margin_sale` (isi persis)

Konteks: form popup `product.product_variant_easy_edit_view` dihapus total di 20.0. Dev memutuskan
(`FINDINGS.md` `MF-29`, 2026-09-21) mengganti dengan kolom baru di list "Product Variants"
(`product.product_product_tree_view`, `odoo20/addons/product/views/product_views.xml:424-498`) —
list ini sudah `editable="bottom"`/`multi_edit="1"` di native 20.0, jadi field yang ditambahkan
langsung bisa diedit inline (setara fungsional dengan popup lama, bukan downgrade).

Field yang dibutuhkan (`margin_sale`, `minimum_sale_price`, `is_less_minimum_sale`,
`module_pos_margin_threshold`) semua sudah tersedia di `product.product` — `margin_sale`/
`minimum_sale_price`/`is_less_minimum_sale` didefinisikan langsung di `ProductProduct`
(`models/product.py:73-75`), `module_pos_margin_threshold` didefinisikan di `ProductTemplate`
tapi otomatis accessible di `product.product` lewat mekanisme `_inherits` (delegation) native Odoo
— pola yang SAMA sudah dipakai popup lama (`<field name="module_pos_margin_threshold"
invisible="1"/>` langsung di form `product.product`, tanpa masalah).

**Ganti total** record `product_variant_easy_edit_view_margin_sale` di `views/products.xml`
(baris ~36-68 saat ini) menjadi:

```xml
<record id="product_product_tree_view_margin_sale" model="ir.ui.view">
    <field name="name">product.product.list.margin.sale</field>
    <field name="model">product.product</field>
    <field name="inherit_id" ref="product.product_product_tree_view"/>
    <field name="arch" type="xml">
        <field name="lst_price" position="attributes">
            <attribute name="decoration-danger">is_less_minimum_sale</attribute>
        </field>
        <field name="lst_price" position="after">
            <field name="module_pos_margin_threshold" column_invisible="True"/>
            <field name="is_less_minimum_sale" column_invisible="True"/>
            <field name="margin_sale"
                   optional="show"
                   invisible="module_pos_margin_threshold == True"
                   widget="float"/>
            <field name="minimum_sale_price"
                   optional="show"
                   invisible="module_pos_margin_threshold == True"
                   widget="monetary"
                   options="{'currency_field': 'currency_id'}"/>
        </field>
    </field>
</record>
```

Keputusan teknis yang perlu dijelaskan (semua konsisten dengan `MF-29` §"Keputusan dev"):

1. **`position="attributes"` pada `lst_price`, BUKAN `position="replace"`.** Popup lama
   (`MF-25`/`MF-27` pattern) selalu memakai `position="replace"` untuk menambah decoration ke
   `lst_price`/`list_price`, yang diam-diam menghapus atribut core (`options`, dst) — ini SUDAH
   dicatat sebagai anti-pattern warisan yang harus DIPERTAHANKAN di lokasi lama (`MF-27`, view
   `product.product_template_form_view`, tidak diperbaiki di migrasi ini). **TAPI record ini adalah
   record BARU** (bukan port 1:1 dari kode lama — `product_product_tree_view` tidak pernah
   di-inherit modul ini sebelumnya), jadi tidak ada kewajiban "identik dengan 19.0" untuk cara
   penulisannya. `position="attributes"` mencapai efek visual yang sama (decoration merah pada
   harga di bawah minimum) TANPA menghapus `options="{'currency_field': 'currency_id'}"`/
   `widget="monetary"` milik `lst_price` core (`product_views.xml:461-466`) — menghindari
   mengulang anti-pattern `MF-24`/`25`/`27` di kode baru. Direkomendasikan, bukan port mekanis.
2. **`decoration-danger="is_less_minimum_sale"` TIDAK dikondisikan `module_pos_margin_threshold`.**
   Dikonfirmasi dari popup lama (`views/products.xml` baris 41-43 saat ini,
   `<field name="lst_price" position="replace"><field name="lst_price"
   decoration-danger="is_less_minimum_sale" .../></field>`) — decoration ini murni warning harga
   (`lst_price < minimum_sale_price`), TIDAK pernah dibungkus `invisible=`/kondisi apapun di popup
   lama, beda dari field `margin_sale`/`minimum_sale_price` yang memang disembunyikan kalau
   `pos_margin_threshold` terinstall (mencegah field ganda). Konsisten dengan instruksi task: field
   warning ini module-agnostic, kolom margin/minimum-price yang perlu di-dedup lintas modul.
3. **`invisible="module_pos_margin_threshold == True"`** (bukan `optional="hide"`) untuk
   `margin_sale`/`minimum_sale_price` — pola PERSIS yang sudah terbukti jalan di popup lama
   (`views/products.xml` baris 46/52 saat ini, form `product.product`) dan di
   `views/product_template_views.xml:13-14` (form `product.template`, walau record itu sendiri
   inert karena `BSL-013` — pola ekspresinya tetap valid, bukan syntax yang mati). Direplikasi
   langsung tanpa modifikasi ekspresi.
4. **`optional="show"`** (bukan `optional="hide"`) — keputusan dev eksplisit `MF-29` poin 2: popup
   lama selalu menampilkan kedua field tanpa toggle, `optional="hide"` akan jadi downgrade
   visibilitas dibanding behavior 19.0.
5. **`column_invisible="True"`** untuk `module_pos_margin_threshold`/`is_less_minimum_sale` (bukan
   `invisible="1"`) — kedua field ini hanya dipakai sebagai input ekspresi (`invisible=`/
   `decoration-danger=`) pada field lain, tidak boleh muncul sebagai kolom sendiri. Ini idiom list
   view 20.0 yang benar (dipakai native sendiri untuk `currency_id`/`cost_currency_id` di view yang
   sama, `product_views.xml:459-460`) — beda dari form view yang tetap pakai `invisible="1"`.
6. **`options="{'currency_field': 'currency_id'}"` pada `minimum_sale_price`** — disamakan dengan
   pola native `lst_price`/`standard_price` di view yang sama (baris 464/470), field `currency_id`
   sudah tersedia sebagai `column_invisible` di list ini (baris 459) sehingga widget monetary bisa
   resolve mata uang dengan benar, konsisten dengan cara core menampilkan field monetary lain di
   list yang sama (bukan devisiasi baru).

**Visual parity — ✅ DIKONFIRMASI DEV 2026-09-22, DITERAPKAN (`FINDINGS.md` `MF-38`):**
- **`minimum_sale_price_with_tax`** — ada di popup lama (kolom "Incl. Tax"). Field baru ditambahkan
  ke `ProductProduct` (compute dari `margin_sale`/`minimum_sale_price`/`product_tmpl_id.taxes_id`)
  + kolom baru di list, dengan marker dedup `MF-37` supaya tidak dobel saat `pos_margin_threshold`
  juga terinstall (modul itu mendapat kolom yang sama).
- **`decoration-danger="margin_sale < 0.0"`** pada field `margin_sale` sendiri — ditambahkan ke
  field yang sudah ada.
- Diverifikasi live (Docker 20.0): margin negatif tampil merah, kolom Incl. Tax terisi benar, tidak
  dobel. Lihat `06_implementation/sale_margin_threshold/06c_IMPLEMENTATION_LOG.md`.

**Review visual Step 10 (sudah dicatat `MF-29`):** bandingkan tampilan popup 19.0 vs kolom list
20.0 berdampingan — bukan cuma verifikasi fungsional (field muncul/tersimpan), termasuk cek kedua
poin flagged di atas kalau dev memutuskan menambahkannya nanti.

### OWL Widget yang Butuh Rewrite/Review

Tidak ada — modul ini tidak punya JS/Owl sama sekali (`BSL-014`, grep `.js` sesi Step 1: 0 file,
`static/src/` tidak ada di disk walau dideklarasikan di manifest `assets`).

### Controller & Route

Tidak ada — `controllers/controllers.py` seluruhnya di-comment (scaffold mati sejak awal, tidak
disentuh migrasi ini).

### Assets & Dependency

Tidak ada asset JS/CSS fungsional (`assets.sale_margin_threshold._assets_sale` menunjuk folder yang
tidak ada di disk, `BSL-014`, dipertahankan apa adanya — glob kosong, tidak ada efek).

### Kompatibilitas Data Model

| # | Isu | Lokasi | Priority | Ref `BSL-NNN` |
|---|---|---|---|---|
| 1 | `model_id`/`group_id` skema `ir.access` (Many2one ke `ir.model`, bukan lagi kombinasi `ir.model.access`) | `security/ir.access.csv` (baru) | Tinggi | — |
| 2 | Field `margin_sale`/`minimum_sale_price`/`is_less_minimum_sale` pada `product.product` — tidak berubah struktur, hanya dipakai di lokasi view baru | `models/product.py` (tidak diubah) | Tidak ada | BSL-018 |
| 3 | `stock_account`/`product`/`sale`/`base` dependency — semua tetap ada, tidak ada rename model yang mempengaruhi modul ini (`DIFF-02`/`DIFF-04`/`DIFF-09`/`DIFF-10`) | manifest `depends` | Tidak ada | — |

### Risiko Integrasi

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | Kolisi `wizard.margin.product` dengan `pos_margin_threshold` (`MF-03`/`BSL-015`) — modul ini menang MRO, tidak berubah oleh migrasi versi | `wizard/wizard_margin_product.py` | Rendah — sudah diketahui, tidak perlu aksi baru |
| 2 | Koordinasi `module_pos_margin_threshold` — kolom baru di list `product_product_tree_view` harus tetap konsisten dengan sibling module `pos_margin_threshold` (yang punya `MF-29` retarget serupa untuk view yang sama) — **kedua modul menambah record inherit `product.product_product_tree_view` yang BERBEDA XML-ID** (masing-masing modul punya record sendiri), tidak akan kolisi XML-ID seperti `BSL-013`, tapi kolom hasil gabungan (kalau kedua modul terinstall) dobel kalau tidak di-dedup (`MF-37`, ditemukan+diperbaiki 2026-09-22). **Update retroaktif (Step 4, 2026-09-22):** pendekatan `invisible="module_pos_margin_threshold == True"` yang tertulis semula di baris ini **TERBUKTI GAGAL** — `column_invisible`/`invisible` pada list view tidak punya record context saat dievaluasi (`EvalError: Name 'module_pos_margin_threshold' is not defined`), dan `invisible=` biasa cuma mem-blank isi sel per baris, tidak menyembunyikan header kolom. Mekanisme final yang benar-benar dipakai: override `ProductProduct._get_view()` (Python, `models/product.py`) yang strip node `margin_sale`/`minimum_sale_price`/`minimum_sale_price_with_tax` dari arch hasil merge — ditarget via marker `class="o_smt_dedup_*"` pada field di `views/products.xml` (karena field bernama sama muncul dari dua modul, nama field saja tidak cukup) — kalau `pos_margin_threshold` terdeteksi terinstall, kolom modul ini yang dihapus, kolom `pos_margin_threshold` yang jadi satu-satunya tampil. Diverifikasi visual live di Docker 20.0 (bukan cuma baca kode) — 1 set kolom, tidak dobel. | `views/products.xml` (marker `class`) + `models/product.py` (`_get_view()` override) — modul ini; `pos_margin_threshold` sisi lain tidak disentuh (kolomnya yang dipertahankan) | Sedang → **RESOLVED** — perilaku dedup sudah diverifikasi visual (`FINDINGS.md` `MF-37`/`MF-38`) |
| 3 | Dependency Rental (`is_rental_order`) — dikonfirmasi field masih ada persis nama sama di `enterprise20/sale_renting` | `models/sale_order.py:14` | Tidak ada — tidak berubah |

### Urutan Prioritas Testing

1. Install & startup — manifest version `20.0.x.x`, `security/ir.access.csv` termuat tanpa error
   (blocker #2), record view baru `product_product_tree_view_margin_sale` resolve tanpa error
   (blocker #3).
2. Core user flow — konfirmasi Sale Order dengan produk di bawah minimum: jalur blocking
   (`ValidationError`) dan jalur wizard konfirmasi (`sale.confirmation.wizard`), keduanya harus
   identik behavior dengan 19.0 (`BSL-001`..`BSL-005`).
3. Rental order exemption — order rental (`is_rental_order_installed_true=True`) tetap skip validasi
   margin sepenuhnya (`BSL-001`), butuh `native-target-enterprise` (`sale_renting`) terinstall di
   environment test.
4. List "Product Variants" — kolom `margin_sale`/`minimum_sale_price` tampil+editable inline
   (`multi_edit`), decoration merah pada `lst_price` muncul saat harga di bawah minimum, kolom margin
   tersembunyi otomatis kalau `pos_margin_threshold` juga terinstall (item risiko integrasi #2 di
   atas).
5. Wizard bulk-assign margin (`wizard.margin.product`, byte-identik `pos_margin_threshold`, risiko
   rendah, `BSL-015`).
6. Persistensi data — `margin_sale` (inverse ke `product_tmpl_id`), `minimum_sale_price`
   (compute+inverse+store) tetap tersimpan benar lewat edit inline di list baru (jalur input BARU
   dibanding popup lama, wajib diverifikasi Step 9 walau field/logic-nya sendiri tidak berubah).
7. Regresi bug warisan (`MF-08` batch-confirm crash, `MF-26` singleton compute) — **verifikasi tetap
   CRASH dengan cara yang sama** (bukan diperbaiki tanpa sengaja oleh perubahan native `action_confirm`
   batching, sudah dikonfirmasi `DIFF-02` tidak berubah, tapi bukti eksekusi tetap wajib Step 9 sesuai
   `doc-dev/backfill/` baseline).

### View List (dulu Tree) Checklist

| # | Apa | Di mana | Perubahan |
|---|---|---|---|
| 1 | Standalone list view | N/A | Modul ini tidak punya `<tree>`/`<list>` standalone sendiri — record baru §2b poin 3 adalah inherit ke list native (`product_product_tree_view`), bukan definisi list baru dari nol; sudah ditulis pakai `<field>` xpath (bukan `<tree>`/`<list>` root), tidak ada elemen `<tree>` tersisa di modul manapun. |
| 2 | `view_mode` di action | N/A | Modul ini tidak mendefinisikan `ir.actions.act_window` untuk list Product Variants (action native `product.product_variant_action` dipakai apa adanya, tidak disentuh). |
| 3 | Inline tree di form | N/A | Tidak ada `<field><tree>...</tree></field>` di modul ini (grep `<tree` seluruh `views/`/`wizard/`: 0 match selain yang sudah dikonfirmasi N/A di atas). |

### Estimasi Effort (opsional)

| Area | Effort | Catatan |
|---|---|---|
| Manifest version bump | Trivial | Satu baris |
| `security/ir.access.csv` (rename + reformat) | Kecil | 2 baris data, skema sudah dikonfirmasi persis dari native |
| Manifest `data` update nama file security | Trivial | Satu baris |
| Record baru `product_product_tree_view_margin_sale` | Sedang | XML baru (bukan port), perlu verifikasi visual Step 10 + kombinasi dua modul (risiko integrasi #2) |
| Hapus record lama `product_variant_easy_edit_view_margin_sale` | Trivial | Hapus blok, tidak ada dependensi lain ke XML-ID ini (grep sesi Step 2: 0 referensi dari file lain) |
| Sisanya (Python/model/wizard/security groups) | Nol | Tidak ada perubahan kode wajib |

## 3. Data Migration (ringkas — detail di step 7)

**N/A — port kode saja** (asumsi carried-forward, dikonfirmasi gate Step 1 lulus). Tidak ada field
yang berubah struktur secara data — `margin_sale`/`minimum_sale_price`/`is_less_minimum_sale` tetap
field yang sama di `product.product`/`product.template`, hanya lokasi UI-nya (view) yang pindah dari
popup ke kolom list. Tidak ada transformasi data lama yang dibutuhkan.

## 4. Scope

### Termasuk
- Bump `__manifest__.py` `version` ke `20.0.1.0`.
- Rename `security/ir.model.access.csv` → `security/ir.access.csv` + reformat skema kolom
  (`DIFF-01`/`MF-30`), update entry `data` di manifest.
- Ganti total record `product_variant_easy_edit_view_margin_sale` (`views/products.xml`) menjadi
  record baru `product_product_tree_view_margin_sale` inherit `product.product_product_tree_view`
  (`DIFF-08`/`MF-29`), sesuai spesifikasi §2b poin 3 (3 poin keputusan dev + 2 keputusan teknis
  tambahan `position="attributes"`/`column_invisible`).

### Di Luar Scope (sengaja, disetujui di intake/carried-forward)
- `MF-08` (batch-confirm singleton crash, `action_confirm()`) — **dipertahankan**, keputusan dev
  2026-08-27, tidak diperbaiki tanpa keputusan baru eksplisit.
- `MF-20` (`security/groups.xml` `implied_ids` salah tipe) — terbuka, belum ada keputusan dev,
  dibawa apa adanya.
- `MF-21` (`_compute_warning`/`is_less_minimum_sale` tanpa `@api.depends`) — terbuka, belum ada
  keputusan dev, dibawa apa adanya.
- `MF-26` (singleton-assumption kedua, `_compute_is_rental_order_installed`) — terbuka, belum ada
  keputusan dev, dibawa apa adanya.
- `MF-27` (`position="replace"` pada `list_price`/`lst_price` di view form yang SUDAH ADA sejak
  19.0 — `views/products.xml`/`views/product_template_views.xml`) — terbuka, belum ada keputusan
  dev, dibawa apa adanya. **Tidak sama dengan keputusan `position="attributes"` di record BARU
  `product_product_tree_view_margin_sale`** — lihat §2b poin 3.1 untuk penjelasan bedanya.
- `BSL-013` (kolisi XML-ID `product_template_inherit_sale_margin_threshold` antara
  `product_template_views.xml` dan `products.xml`, record pertama selalu inert) — dipertahankan
  identik, tidak diperbaiki.
- Dua item flagged §2b poin 3 (`minimum_sale_price_with_tax`, `decoration-danger="margin_sale <
  0.0"`) — **di luar scope literal keputusan dev `MF-29` saat ini**, ditulis sebagai kandidat kalau
  dev ingin paritas visual penuh dengan popup lama, bukan diasumsikan otomatis termasuk.
