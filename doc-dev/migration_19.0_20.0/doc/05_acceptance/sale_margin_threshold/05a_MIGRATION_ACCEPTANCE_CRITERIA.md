# Migration Acceptance Criteria — sale_margin_threshold

**Step:** 5 — Acceptance Criteria & Test Plan
**Ref:** `01_intake/sale_margin_threshold/01b_BASELINE_SPEC.md` dan kode 19.0 yang berjalan (branch
`migration/19.0`) — **bukan** `03_spec/sale_margin_threshold/03_MIGRATION_SPEC.md`
**Tanggal:** 2026-09-22

> Format Given/When/Then, diturunkan dari `01b_BASELINE_SPEC.md` (dokumentasi behavior modul asli).
> `03_MIGRATION_SPEC.md` dipakai sebagai referensi area berisiko tinggi (§2b Risk Analysis) dan
> untuk detail teknis spesifikasi record baru, tapi bukan sumber kebenaran perilaku — kesetaraan
> diukur terhadap 19.0, bukan terhadap rencana migrasi.
>
> **Traceability wajib:** tiap AC menyebut `BSL-NNN` mana (dari `01b_BASELINE_SPEC.md`) yang
> diverifikasi. Beberapa AC di bawah TIDAK bisa dipetakan ke `BSL-NNN` manapun karena
> `01b_BASELINE_SPEC.md` §3 ("Field dengan Makna Bisnis") dan sebagian §6 mendeskripsikan behavior
> dalam prosa tanpa memberi tag `BSL-NNN` — ini ditandai eksplisit `[BASELINE-GAP]` di AC terkait
> dan didaftar ulang di §"Catatan Gap Traceability" di akhir dokumen, BUKAN diam-diam dianggap
> tertelusuri. AC untuk perilaku yang genuinely BARU di 20.0 (kolom list pengganti popup, `MF-29`)
> ditandai eksplisit sebagai **PERUBAHAN DISENGAJA & DISETUJUI** sesuai keputusan dev
> (`FINDINGS.md` `MF-29`/`MF-37`/`MF-38`), bukan pelanggaran "identik dengan 19.0".
>
> **Penanda risiko tinggi:** AC yang menyentuh area migrasi berisiko (`MF-29` penggantian view list,
> `MF-37` mekanisme dedup, `MF-38` paritas visual, `MF-35` fix xpath `sale_order.xml`) diberi label
> **[HIGH-RISK — Step 9/10 extra scrutiny]**.

---

## AC-01 — Kalkulasi Margin & Minimum Sale Price (`product.category` / `product.template` / `product.product`)

**AC-01-01** (verifies §3 `product.category` — `[BASELINE-GAP]`, tidak ada `BSL-NNN`)
Given kategori produk punya `margin_sale = 20.0`
When produk baru dibuat dengan `categ_id` mengarah ke kategori itu (dan `margin_sale` template belum
di-override manual)
Then `product.template.margin_sale` mewarisi `20.0` dari kategori lewat `_compute_margin_sale`
(`@api.depends('categ_id.margin_sale')`) — identik dengan 19.0.

**AC-01-02** (verifies §3 `product.template` — `[BASELINE-GAP]`, tidak ada `BSL-NNN`)
Given `product.template` dengan `standard_price = 100.0` dan `margin_sale = 20.0`
When `minimum_sale_price` dihitung ulang (`_compute_minimum_sale_price`)
Then `minimum_sale_price = 120.0` (`standard_price * (1 + margin_sale/100)`) — identik dengan 19.0.
Test eksisting `test_action_confirm.py::test_action_confirm_blocking_below_minimum` sudah meng-assert
nilai ini (`self.assertEqual(product.minimum_sale_price, 120.0)`).

**AC-01-03** (verifies §3 `product.template` — `[BASELINE-GAP]`, tidak ada `BSL-NNN`)
Given `product.template` dengan `standard_price = 100.0`
When user mengedit `minimum_sale_price` langsung jadi `150.0` (memicu `_inverse_minimum_sale_price`)
Then `margin_sale` otomatis terhitung balik jadi `50.0` — identik dengan 19.0.

**AC-01-04** (verifies §3 `product.product` + ref `doc-dev/backfill/FINDINGS.md` `F-01`)
Given dua variant (`product.product`) berbagi `product_tmpl_id` yang sama
When `margin_sale` salah satu variant diedit (memicu inverse `_set_product_margin_sale`)
Then perubahan ditulis ke `product_tmpl_id` (TEMPLATE bersama), sehingga margin variant LAIN yang
berbagi template yang sama ikut berubah — `margin_sale` per-variant TIDAK BISA divergen. Ini
behavior asli 19.0 (bukan bug migrasi), harus identik, bukan diperbaiki jadi "per-variant murni".

**AC-01-05** (verifies §3 `product.product` — `[BASELINE-GAP]`, tidak ada `BSL-NNN`; **[HIGH-RISK —
Step 9/10 extra scrutiny]**, terkait `MF-38`)
Given `minimum_sale_price = 120.0` dan `taxes_id` dengan total persentase pajak `10%`
When `minimum_sale_price_with_tax` dihitung
Then hasilnya `minimum_sale_price` + total persentase pajak (`132.0` pada contoh ini) — field ini
sudah ada sejak 19.0 di baseline compute, TAPI baru punya representasi visual (kolom "Incl. Tax") di
20.0 lewat `MF-38` (lihat AC-04-03). AC ini memverifikasi computed value-nya sendiri tetap benar,
independen dari lokasi tampilnya di UI.

**AC-01-06** (verifies `BSL-018`/`MF-21`)
Given `product.product` dengan `lst_price < minimum_sale_price`
When `_compute_warning()` (`is_less_minimum_sale`) dievaluasi SETELAH `lst_price` atau
`minimum_sale_price` berubah DALAM transaksi/request yang sama, TANPA trigger recompute eksplisit
lain
Then nilai `is_less_minimum_sale` bisa tetap STALE (cache lama) karena method ini **TIDAK** punya
`@api.depends(...)` — bug ini harus direproduksi IDENTIK, **JANGAN** ditambahkan `@api.depends` tanpa
keputusan dev baru (`MF-21` masih 🔵 terbuka, belum ada keputusan "perbaiki").

---

## AC-02 — Konfirmasi Sale Order & Validasi Margin

**AC-02-01** (verifies `BSL-001`)
Given `sale.order` adalah rental order (`is_rental_order_installed_true = True`, butuh
`native-target-enterprise`/`sale_renting` terinstall)
When `action_confirm()` dipanggil
Then langsung `super().action_confirm()` TANPA pengecekan margin sama sekali — order rental
SEPENUHNYA dikecualikan, identik dengan 19.0.

**AC-02-02** (verifies `BSL-002`)
Given `sale.order` bukan rental, semua `order_line.price_unit >= minimum_sale_price`
When `action_confirm()` dipanggil
Then `check_product_price()` mengembalikan set kosong, order langsung `super().action_confirm()`
tanpa blocking/wizard — identik dengan 19.0. Sudah tercakup
`test_action_confirm.py::test_action_confirm_normal_no_price_issue`.

**AC-02-03** (verifies `BSL-003`, cabang blocking)
Given `post_margin_sale.blocking_transaction_order = True` DAN ada minimal satu `order_line` dengan
`price_unit < minimum_sale_price`, DAN context `skip_check_price` tidak di-set
When `action_confirm()` dipanggil
Then `ValidationError` di-raise (pesan bilingual, lihat AC-02-07), `order.state` tetap `'draft'` —
identik dengan 19.0. Sudah tercakup
`test_action_confirm.py::test_action_confirm_blocking_below_minimum`.

**AC-02-04** (verifies `BSL-003`, cabang wizard)
Given `post_margin_sale.blocking_transaction_order = False` DAN ada minimal satu `order_line` di
bawah minimum
When `action_confirm()` dipanggil
Then dikembalikan `ir.actions.act_window` modal (`target='new'`) mengarah ke
`sale.confirmation.wizard` dengan `message` terisi, `order.state` TETAP `'draft'` (belum confirm) —
identik dengan 19.0. Sudah tercakup
`test_action_confirm.py::test_action_confirm_wizard_path_when_not_blocking`.

**AC-02-05** (verifies `BSL-004`)
Given `action_confirm()` dipanggil dengan context `skip_check_price=True` (dikirim wizard)
When method dieksekusi
Then LANGSUNG `super().action_confirm()` tanpa mengecek ulang margin sama sekali (mencegah rekursi
tak berujung antara wizard dan `action_confirm()`) — identik dengan 19.0.

**AC-02-06** (verifies `BSL-005`)
Given `sale.confirmation.wizard` dibuka dari alur `AC-02-04` (context `active_id`/`active_model`
mengarah ke order yang benar)
When user klik tombol confirm wizard (`action_confirm()` wizard, memanggil
`.with_context(skip_check_price=True).action_confirm()` pada order)
Then `order.state` berubah jadi `'sale'` — order akhirnya terkonfirmasi. Tombol "Cancel"
(`special="cancel"`) TIDAK melakukan apapun ke sale order, murni menutup dialog — identik dengan
19.0. Sudah tercakup (jalur confirm)
`test_action_confirm.py::test_action_confirm_wizard_path_when_not_blocking`; jalur Cancel BELUM ada
test eksplisit (flag, lihat §Catatan Gap Traceability).

**AC-02-07** (verifies `BSL-006`, `BSL-007`)
Given user dengan bahasa UI berprefix `fr` (mis. `fr_FR`, `fr_BE`) vs user dengan bahasa lain (mis.
`en_US`, `id_ID`)
When `ValidationError`/`message` wizard dibuat
Then `detect_user_language()` HANYA membedakan dua kelompok — prefix `fr` → string versi Prancis
(`message_Fr`), SEMUA bahasa lain (termasuk `id_ID`) → string versi Inggris (`message`) — ini BUKAN
mekanisme `.po` translasi standar Odoo (dikonfirmasi ulang 0 match `with_context(lang=`/`fr_FR` file
`.po` di seluruh modul), string dibuat manual bilingual. Harus identik dengan 19.0, TIDAK dikonversi
ke mekanisme `.po` standar tanpa keputusan dev baru.

**AC-02-08** (verifies `BSL-012`; **[HIGH-RISK — Step 9/10 extra scrutiny]**, terkait fix `MF-35`)
Given form Sale Order menampilkan `order_line` di list (dalam `<page name="order_lines">`)
When salah satu line punya `price_unit < minimum_sale_price` DAN order BUKAN rental
(`not parent.is_rental_order_installed_true`)
Then line itu diberi `decoration-danger` (baris merah) di list; field `minimum_sale_price`
tersedia sebagai `column_invisible` (dipakai ekspresi decoration, tidak tampil sebagai kolom
sendiri); untuk order RENTAL, decoration ini TIDAK aktif sama sekali — identik dengan 19.0. AC ini
secara khusus memverifikasi list `order_line` masih resolve dengan benar setelah fix `MF-35`
(native 20.0 membungkus `price_unit` dalam `<column name="price_unit">` baru, xpath lama sempat
install-blocking sebelum diperbaiki) — pastikan xpath baru tidak mengubah PERILAKU decoration ini,
hanya jalur resolve-nya.

---

## AC-03 — Bug Warisan yang WAJIB Direproduksi Identik (bukan diperbaiki)

**AC-03-01** (verifies `BSL-009`/`MF-08`; **[HIGH-RISK — regresi kritis kalau berubah tanpa
sengaja]**)
Given ≥2 `sale.order` (bukan rental, tidak melanggar margin) dipilih sekaligus dari list view (batch
confirm — fitur native Odoo, termasuk dipicu oleh demo data `sale_stock` core sendiri)
When `action_confirm()` dipanggil pada recordset berisi >1 order (`self` tidak di-loop di baris
`self.is_rental_order_installed_true`/`self.order_line` dalam `check_product_price()`)
Then `ValueError: Expected singleton: sale.order(id1, id2, ...)` di-raise — **CRASH TOTAL** untuk
SELURUH batch (bukan cuma order ke-2 dst, bukan silent skip) — ini bug `[DIWARISI-SOURCE]` yang
**keputusan dev-nya sudah final: dipertahankan** (2026-08-27). Perilaku ini WAJIB tetap crash dengan
cara yang SAMA di 20.0 — kalau native `action_confirm()` batching berubah sehingga bug ini
"tidak sengaja hilang", itu HARUS dilaporkan sebagai regresi behavior yang butuh keputusan dev baru,
BUKAN dianggap perbaikan yang diinginkan. Sudah tercakup
`test_action_confirm.py::test_action_confirm_BATCH_MULTI_ORDER_F05` (assertion eksplisit menuntut
`ValueError` benar-benar ter-raise).

**AC-03-02** (verifies `BSL-011`/`MF-26`)
Given `_compute_is_rental_order_installed()` dipanggil Odoo pada recordset `sale.order` berisi >1
record (skenario trigger konkret BELUM dipastikan di baseline — lihat `FINDINGS.md` `MF-26`:
"dampak belum diukur skenario trigger konkretnya")
When compute berjalan dan mengevaluasi `hasattr(self, 'is_rental_order') and self.is_rental_order`
(memakai `self` PENUH, bukan `record`, walau loop variable-nya bernama `record`)
Then `ValueError: Expected singleton` berpotensi ter-raise DI SINI (bukan di `action_confirm()`
seperti `AC-03-01`) — symptom externally observable kemungkinan SAMA (crash batch-confirm), tapi
titik kegagalan sesungguhnya berbeda. **[BASELINE-GAP sebagian]** — baseline spec sendiri belum
memastikan skenario trigger konkret di luar `action_confirm()` (Rental compute bisa dipanggil compute
engine di context lain). AC ini deskriptif (dokumentasi bug), BUKAN prasyarat test otomatis wajib —
kalau Step 9 menemukan skenario trigger nyata (mis. lewat `_compute` dipanggil batch dari import/
onchange), tambahkan test baru dan update `FINDINGS.md` `MF-26` dengan bukti eksekusi (pola sama
`MF-08`/`F-05`).

**AC-03-03** (verifies `BSL-017`/`MF-20`)
Given `security/groups.xml` — `group_sale_margin_action.implied_ids` diisi
`[(4, ref('base.module_category_hidden'))]` (kategori, BUKAN grup — kemungkinan salah tempel dari
`category_id`)
When modul di-install/upgrade di 20.0
Then `implied_ids` tetap berisi referensi salah-tipe ini apa adanya (kemungkinan besar silent
no-op/inert di ORM Many2many-ke-`res.groups`) — TIDAK diperbaiki jadi `category_id` tanpa keputusan
dev baru eksplisit. `MF-20` masih 🔵 terbuka.

---

## AC-04 — Kolom List "Product Variants" (Pengganti Popup, `MF-29`/`MF-37`/`MF-38`)

> Seluruh AC di grup ini adalah **PERUBAHAN DISENGAJA & DISETUJUI** (keputusan dev 2026-09-21/22,
> `FINDINGS.md` `MF-29`/`MF-37`/`MF-38`) — popup `product.product_variant_easy_edit_view` yang jadi
> anchor `BSL-019` DIHAPUS TOTAL di native 20.0 (bukan sesuatu yang bisa dipertahankan identik), jadi
> AC berikut memverifikasi bahwa PENGGANTI-nya (kolom list) mencapai paritas fungsional/visual dengan
> popup lama, sesuai spesifikasi eksplisit `03_MIGRATION_SPEC.md` §2b, BUKAN mengukur "identik byte
> demi byte dengan 19.0" (yang secara teknis tidak mungkin, view lama sudah tidak ada).

**AC-04-01** (verifies `BSL-019` sebagai anchor kontras + keputusan dev `MF-29`; **[HIGH-RISK —
Step 9/10 extra scrutiny]**)
Given produk dengan variant >1 (`product_variant_count > 1`), `pos_margin_threshold` TIDAK
terinstall
When user membuka list "Product Variants" (smart button "N Variants" dari Product Template)
Then kolom `margin_sale` dan `minimum_sale_price` (record `product_product_tree_view_margin_sale`,
inherit `product.product_product_tree_view`) tampil dengan `optional="show"` (langsung tampil tanpa
toggle manual, SETARA popup lama yang selalu tampil tanpa toggle — `optional="hide"` akan jadi
downgrade visibilitas dibanding 19.0) dan bisa diedit inline (list sudah `editable="bottom"`/
`multi_edit="1"` di native 20.0) — setara fungsional dengan popup 19.0, bukan downgrade.

**AC-04-02** (verifies `BSL-008` sebagai pola dedup yang sudah ada + `MF-37`; **[HIGH-RISK — Step
9/10 extra scrutiny, mekanisme dedup rawan regresi diam-diam]**)
Given `pos_margin_threshold` JUGA terinstall (sibling module, punya record inherit terpisah ke
`product.product_product_tree_view` untuk view yang sama)
When list "Product Variants" dibuka
Then HANYA SATU set kolom margin/minimum-price yang tampil (milik `pos_margin_threshold`) — kolom
milik `sale_margin_threshold` DIHAPUS dari arch lewat override `ProductProduct._get_view()` yang
men-strip node bermarker `class="o_smt_dedup_margin"`/`o_smt_dedup_min_price"` (bukan `invisible=`/
`column_invisible=` biasa — keduanya TERBUKTI GAGAL di 20.0 karena `column_invisible` tanpa record
context, `MF-37`). Ini pola `BSL-008` (`module_pos_margin_threshold` drives visibility murni tanpa
side effect lain) diperluas ke mekanisme baru — TIDAK boleh muncul dobel (2 set kolom), TIDAK boleh
crash `EvalError`.

**AC-04-03** (verifies keputusan dev `MF-38`, paritas visual popup 19.0 vs list 20.0; **[HIGH-RISK —
Step 9/10 extra scrutiny]**)
Given produk dengan `margin_sale < 0.0` (margin negatif) di list "Product Variants"
When list dirender
Then field `margin_sale` mendapat `decoration-danger` (tampil merah) — elemen visual ini ADA di
popup 19.0 tapi TIDAK otomatis terbawa saat `MF-29` migrasi ke kolom list (baru ditambahkan lewat
`MF-38` atas persetujuan eksplisit dev, dijustifikasi `CLAUDE.md` §Source of Truth "UX di 20.0 harus
identik dengan 19.0"). Kolom "Incl. Tax" (`minimum_sale_price_with_tax`, lihat `AC-01-05`) juga harus
tampil di list yang sama, dengan marker dedup `MF-37` (tidak dobel saat kedua modul terinstall
bersamaan, sama seperti `AC-04-02`).

**AC-04-04** (verifies `BSL-018`/`MF-21` dalam konteks BARU — kolom list)
Given `lst_price < minimum_sale_price` untuk sebuah variant di list "Product Variants"
When list dirender (field `lst_price` mendapat `decoration-danger` via `is_less_minimum_sale`,
`position="attributes"` — BUKAN `position="replace"`, lihat kontras `AC-07-04`)
Then decoration merah tampil BENAR pada baris itu — TAPI tetap rawan bug stale-cache `MF-21`
(`AC-01-06`) kalau `is_less_minimum_sale` dibaca sebelum recompute terjadi (mis. langsung setelah
edit inline `lst_price` di baris lain pada list yang sama, sebelum reload). Verifikasi Step 9/10
HARUS eksplisit mencoba skenario edit-lalu-baca-cepat ini, bukan cuma reload penuh (yang akan selalu
menyembunyikan bug stale-cache).

**AC-04-05** (verifies §3 `product.product` compute+inverse — `[BASELINE-GAP]`, tidak ada
`BSL-NNN`, jalur input BARU dibanding popup lama)
Given list "Product Variants" dalam mode `multi_edit`
When user mengedit `margin_sale`/`minimum_sale_price` langsung di sel list (bukan lewat popup lagi)
dan menyimpan
Then nilai tersimpan benar ke `product.product`/`product_tmpl_id` sesuai formula compute+inverse
yang SAMA seperti `AC-01-02`/`AC-01-03`/`AC-01-04` (logic field-nya sendiri tidak berubah, hanya
jalur UI input yang baru) — wajib diverifikasi Step 9 karena ini jalur input yang belum pernah ada
di 19.0.

---

## AC-05 — Wizard Bulk-Assign Margin & Interaksi Lintas-Modul

**AC-05-01** (verifies `BSL-015`)
Given KEDUA `pos_margin_threshold` dan `sale_margin_threshold` terinstall (independen urutan
install)
When model `wizard.margin.product` di-resolve (dua modul mendefinisikan model ini byte-identik tanpa
`_inherit`, kolisi `_name`)
Then `sale_margin_threshold` SELALU menang MRO (empiris, independen urutan install) — identik dengan
19.0. Sudah tercakup
`test_cross_module.py::test_wizard_margin_product_model_merged_when_both_installed`.

**AC-05-02** (verifies `BSL-010`)
Given `ProductProduct._register_hook()` dijalankan (setiap registry rebuild, TIDAK hanya saat
install)
When `pos_margin_threshold` terinstall → `group_sale_margin_action.user_ids` di-set KOSONG untuk
SEMUA user (`[(5, 0, 0)]`); kalau TIDAK terinstall → grup itu diberikan ke SEMUA user internal
(`[(6, 0, internal_users.ids)]`)
Then perilaku mutasi paksa ini (bukan kondisi deklaratif) identik dengan 19.0 — perubahan manual
admin ke membership grup bisa ter-reset diam-diam di reload registry berikutnya, ini WAJIB tetap
begitu. Sudah tercakup
`test_cross_module.py::test_group_sale_margin_action_emptied_when_pos_margin_installed` (arah "kedua
modul terinstall"); arah "hanya modul ini terinstall" BELUM ada test eksplisit (flag, lihat
§Catatan Gap Traceability).

---

## AC-06 — Config Settings

**AC-06-01** (verifies §3 `res.config.settings` — `[BASELINE-GAP]`, tidak ada `BSL-NNN`)
Given `res.config.settings` field `blocking_transaction_order` diubah user via UI Settings
When settings disimpan
Then nilai ditulis ke `config_parameter` `post_margin_sale.blocking_transaction_order` dan
langsung mempengaruhi cabang mana yang diambil `action_confirm()` (`AC-02-03` vs `AC-02-04`) — sudah
tervalidasi TIDAK LANGSUNG lewat kedua test itu (yang men-set param langsung via
`ir.config_parameter`), tapi jalur UI Settings → param belum diverifikasi eksplisit.

---

## AC-07 — Quirk Non-Fungsional yang Harus Tetap Diam (Regression Guard)

**AC-07-01** (verifies `BSL-013`)
Given manifest memuat KEDUA `views/product_template_views.xml` dan `views/products.xml`, keduanya
mendefinisikan XML-ID identik `product_template_inherit_sale_margin_threshold` dengan `inherit_id`
berbeda
When kedua file dimuat (urutan manifest: `product_template_views.xml` lalu `products.xml`)
Then record dari `products.xml` (dimuat kedua) menimpa TOTAL record pertama — kustomisasi yang
dituju ke `product.product_template_only_form_view` TIDAK PERNAH aktif, hanya kustomisasi ke
`product.product_template_form_view` yang jalan. Perilaku (termasuk kerugiannya) harus identik
dengan 19.0 — TIDAK di-refactor jadi dua XML-ID terpisah tanpa keputusan dev baru.

**AC-07-02** (verifies `BSL-014`)
Given manifest deklarasikan `assets.sale_margin_threshold._assets_sale` → `static/src/**/*`
When assets di-build
Then glob tetap KOSONG (folder `static/src/` tidak ada di disk) — tidak ada efek fungsional, tidak
perlu diperbaiki (murni cruft, prioritas Rendah, identik dengan 19.0).

**AC-07-03** (verifies `BSL-016`)
Given `_compute_module_pos_margin_threshold` dideklarasikan `@api.depends_context('uid')`
When compute dipanggil
Then invalidasi cache per-user tetap terjadi walau compute-nya sendiri tidak bergantung `uid` — nit
efisiensi, TIDAK berdampak fungsional, tidak perlu diperbaiki tanpa keputusan dev baru.

**AC-07-04** (verifies `BSL-019`/`MF-27`; kontras eksplisit dengan `AC-04-01`/`AC-04-02`)
Given form `product.template` AKTIF (`product_template_form_view`, via `products.xml`) dan form
`product.product` (via `views/products.xml`, sebelum `MF-29` retarget)
When field `list_price`/`lst_price` di-xpath dengan `position="replace"` (BUKAN
`position="attributes"`) untuk menambah `decoration-danger`
Then atribut native `options="{'currency_field': 'currency_id', 'field_digits': True}"` HILANG TOTAL
dari field itu di form yang aktif — bug ini `[DIWARISI-SOURCE]`, harus TETAP ada (rounding
digit/resolusi mata uang eksplisit tetap hilang), TIDAK diperbaiki tanpa keputusan dev baru
(`MF-27` masih 🔵 terbuka). **Beda dengan `AC-04-01`/`AC-04-02`** — record BARU
`product_product_tree_view_margin_sale` SENGAJA memakai `position="attributes"` untuk MENGHINDARI
mengulang anti-pattern ini di kode baru (keputusan teknis eksplisit di `03_MIGRATION_SPEC.md` §2b
poin 3.1) — jangan disamaratakan sebagai "harus konsisten pakai `replace`" di kedua lokasi.

---

## Catatan Gap Traceability (non-blocking, untuk Step 1/4 revisit kalau perlu)

`01b_BASELINE_SPEC.md` memberi tag `BSL-NNN` HANYA untuk klaim di §4 (Business Workflow), §5
(Server-Side Logic), sebagian §6 (Client-Side — hanya form Sale Order, `BSL-012`), §7 (Dependency,
tidak ditag terpisah), dan §8 (Quirk). §3 ("Field dengan Makna Bisnis" — formula
`margin_sale`/`minimum_sale_price`/`minimum_sale_price_with_tax`/`is_less_minimum_sale` sebagai
computed value, di luar bug `BSL-018`-nya sendiri) dan sebagian §6 (paragraf "Form Product
Template/Variant" — guard `module_pos_margin_threshold`, `position="replace"` yang jadi anchor
`BSL-019`, tapi behavior visibility guard-nya sendiri) ditulis sebagai PROSA tanpa `BSL-NNN`. AC-01,
AC-04-05, dan AC-06-01 di atas ditandai `[BASELINE-GAP]` karena ini — direkomendasikan menambah
`BSL-020`..`BSL-02x` ke `01b_BASELINE_SPEC.md` retroaktif (Step 1 revisit, non-blocking, tidak perlu
membuka ulang gate) supaya traceability penuh untuk field-field inti modul ini yang justru paling
sering diuji (`test_action_confirm.py` sudah meng-assert `minimum_sale_price == 120.0` tanpa
BSL-NNN eksplisit untuk itu).

Dua AC (`AC-02-06` jalur Cancel, `AC-05-02` arah "hanya modul ini terinstall") tertelusuri BSL-NNN
tapi BELUM punya test otomatis eksisting — dicatat di `05b_TEST_PLAN_MIGRATION.md` sebagai gap Step
9.

`AC-03-02` (`MF-26`) sengaja ditulis deskriptif/kondisional karena baseline spec sendiri mengakui
belum memastikan skenario trigger konkret — bukan kegagalan traceability, tapi ketidakpastian
domain yang sudah dicatat eksplisit di `FINDINGS.md`.
