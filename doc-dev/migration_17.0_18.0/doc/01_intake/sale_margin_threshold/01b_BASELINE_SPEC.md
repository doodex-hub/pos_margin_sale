# Baseline Spec — sale_margin_threshold

**Step:** 1 — Intake & Scope (pelengkap `01a_MIGRATION_INTAKE.md`)
**Tujuan:** dokumentasikan behavior as-is modul ini di 17.0.
**Tanggal:** 2026-08-24
**Sumber:** Direkonsiliasi dari `doc-dev/backfill/spec/sale_margin_threshold/01A_FUNCTIONAL_SPEC.md` + `01B_ACCEPTANCE_CRITERIA.md` (2026-07-31, tervalidasi eksekusi Docker) + cross-check kode aktual sesi ini (tidak ada penyimpangan)

---

## Ringkasan untuk Review — Perlu Konfirmasi User

**Tally:** 10 klaim `[MATCH]`, 2 klaim `[NO-SPEC]` (temuan baru sesi ini).

1. `[BSL-002]` `[PERLU-KEPUTUSAN]` `[DIWARISI-SOURCE]` **PRIORITAS TINGGI** — `action_confirm()` membaca `self.is_rental_order_installed_true`/`self.order_line` sebagai singleton, TIDAK mendukung batch-confirm multi-order dari list view (crash `ValueError: Expected singleton`). Diwarisi `MF-06`/backfill `F-05`. Bug existing, harus dipertahankan — TAPI wajib dicek ulang Step 2 apakah mekanisme batch action Odoo 18.0 memanggil `action_confirm` dengan cara berbeda (kalau ya, gejala crash yang sama bisa muncul di titik berbeda, bukan otomatis identik).
2. `[BSL-006]` `[PERLU-KEPUTUSAN]` `[DIWARISI-SOURCE]` — `_register_hook` memutasi membership `group_sale_margin_action` tiap registry reload berdasar status install `pos_margin_threshold`. Diwarisi `MF-05`/backfill `F-04`.
3. `[BSL-007]` `[PERLU-KEPUTUSAN]` `[DIWARISI-SOURCE]` — wizard `wizard.margin.product` duplikat `_name` dengan `pos_margin_threshold` (sama isu, lihat `MF-03`).
4. `[BSL-008]` **`[NO-SPEC]` `[DIWARISI-SOURCE]` TEMUAN BARU** — `views/product_template_views.xml` DAN `views/products.xml` KEDUANYA terdaftar manifest, KEDUANYA define XML-ID sama (`product_template_inherit_sale_margin_threshold`) — yang kedua (`products.xml`, urutan load setelahnya) menimpa total record pertama, termasuk `inherit_id`-nya. Kustomisasi untuk `product_template_only_form_view` **tidak pernah aktif** walau "termuat". Dicatat `MF-07`. **Lebih serius dari kasus serupa di `pos_margin_threshold`** (di sana filenya dead/tidak dimuat sama sekali; di sini dimuat tapi hasilnya silently discarded).
5. `[BSL-009]` `[NO-SPEC]` **TEMUAN BARU** — manifest mendeklarasikan `assets.sale_margin_threshold._assets_sale` menunjuk `static/src/**/*`, tapi folder `static/src/` **tidak eksis** di modul ini. Dicatat `MF-08`, prioritas rendah (tidak error, cuma glob kosong).
6. Business rule inti lain (BR-01, BR-03, BR-04, BR-06 versi backfill) `[MATCH]`, sudah diverifikasi eksekusi Docker.

---

## 1. Tujuan Modul

Modul ini menegakkan aturan harga jual minimum + margin untuk **Sale Order** — memblokir total (`ValidationError`) atau meminta konfirmasi tambahan lewat wizard saat user confirm quotation yang mengandung baris di bawah harga minimum produk, sesuai konfigurasi. Rental order dikecualikan total dari validasi ini.

## 2. Model & Tanggung Jawab

| Model | Tanggung Jawab |
|---|---|
| `product.category`/`product.template`/`product.product` (extend) | Sama seperti `pos_margin_threshold` (margin_sale, minimum_sale_price, minimum_sale_price_with_tax) + field flag `module_pos_margin_threshold` untuk UI dedup |
| `sale.order` (extend) | Override `action_confirm` — validasi harga minimum sebelum confirm, kecuali rental order |
| `sale.order.line` (extend) | Field `minimum_sale_price` (related ke `product_id.minimum_sale_price`), dipakai untuk decoration view |
| `sale.confirmation.wizard` (baru) | Wizard konfirmasi override harga minimum |
| `wizard.margin.product` (baru, `_name` — duplikat `pos_margin_threshold`) | Sama seperti modul sibling |
| `res.config.settings` (extend) | Expose `blocking_transaction_order` |

## 3. Field dengan Makna Bisnis

### `product.template` (tambahan dari `pos_margin_threshold`)
- `module_pos_margin_threshold` (Boolean, compute, `@api.depends_context('uid')`, tidak `store`) — `True` kalau `pos_margin_threshold` terinstall, dipakai murni untuk `invisible=` di view (sembunyikan field margin modul ini kalau modul sibling juga aktif, supaya tidak dobel tampil).

### `sale.order`
- `is_rental_order_installed_true` (Boolean, compute, tidak `store`) — `True` kalau atribut `is_rental_order` ada di record DAN bernilai `True` (deteksi modul rental terinstall + order ini memang rental).

### `sale.order.line`
- `minimum_sale_price` (Float, `related='product_id.minimum_sale_price'`).

### `sale.confirmation.wizard`
- `message` (Text, `translate=True`).

## 4. Business Workflow / State Transition

- `[BSL-001]` `[MATCH]` (ref: BR-01, AC-01-01, AC-01-02, AC-01-03, AC-01-04) `action_confirm()`: skip total (langsung `super()`) kalau rental order. Selain itu, cek semua order line via `check_product_price()` — kalau ada baris `price_unit < minimum_sale_price`:
  - `blocking_transaction_order = True` → `raise ValidationError` (pesan bilingual EN/FR sesuai `detect_user_language()`), order tetap draft/sent.
  - `blocking_transaction_order = False` (default) → buka `sale.confirmation.wizard` dengan pesan bilingual; user confirm ulang di wizard → `action_confirm` dipanggil LAGI dengan `context.skip_check_price=True` → kali ini lolos ke `super().action_confirm()`.
  - Tidak ada baris kena filter → langsung `super().action_confirm()`.
- `[BSL-002]` `[MATCH]` `[PERLU-KEPUTUSAN]` `[DIWARISI-SOURCE]` (ref: BR-02, AC-02-01, **backfill F-05**, dieksekusi 2× Docker — test sendiri + demo data core `sale_stock` ikut crash) — **BUG:** `action_confirm()` membaca `self.is_rental_order_installed_true`/`self.order_line` sebagai singleton (tanpa `for order in self:`), padahal Odoo core `action_confirm` didesain mendukung batch-confirm banyak order dari list view. Memilih >1 quotation lalu klik "Confirm" dari list view → `ValueError: Expected singleton` — batch confirm gagal total untuk SEMUA order yang dipilih.

## 5. Server-Side Logic dengan Side Effect

- `[BSL-003]` `[MATCH]` (ref: BR-03) `detect_user_language()` cuma bedakan prefix bahasa `fr` (French) vs semua lainnya (Other/English) — bukan mekanisme translasi `.po` standar, pesan bilingual di-generate manual dalam method.
- `[BSL-004]` `[MATCH]` (ref: BR-04, AC-03-01, AC-03-02) `sale.confirmation.wizard.action_confirm()` — tombol "Confirm" memanggil ulang `sale.with_context(skip_check_price=True).action_confirm()` (rekursi terkontrol, bukan infinite loop, karena flag context membuat kondisi `[BSL-001]` jadi False). Tombol "Cancel" (`special="cancel"`) tidak melakukan aksi apapun ke sale order.
- `[BSL-005]` `[MATCH]` (ref: BR-06, AC-04-03) `module_pos_margin_threshold` compute murni untuk `invisible=` di view — field margin/minimum_sale_price milik modul INI disembunyikan kalau `pos_margin_threshold` juga terinstall (mencegah field dobel tampil dari 2 modul).
- `[BSL-006]` `[MATCH]` `[PERLU-KEPUTUSAN]` `[DIWARISI-SOURCE]` (ref: BR-05, AC-04-01, AC-04-02, **backfill F-04**, dieksekusi Docker) `ProductProduct._register_hook()` (dipanggil Odoo TIAP registry dibangun ulang, bukan cuma saat install) — kalau `pos_margin_threshold` terinstall: SEMUA user dihapus dari `group_sale_margin_action` (action "Update margin sale" milik modul ini jadi tak terlihat siapapun). Kalau tidak: SEMUA internal user ditambahkan. Perubahan manual admin ke group ini kemungkinan besar ter-revert diam-diam di reload berikutnya (arah ini belum diverifikasi eksekusi langsung oleh backfill, tetap `[HASIL-BACA]`-setara `[NO-SPEC]` untuk klaim spesifik "override admin ter-revert").

## 6. Client-Side Behavior (Views, JS, Owl)

- `[BSL-007]` `[MATCH]` (ref: BR-05, `views/sale_order.xml`) Form Sale Order: baris order line dengan `price_unit` di bawah `minimum_sale_price` ditandai `decoration-danger`, KECUALI kalau order ini rental (`not parent.is_rental_order_installed_true`). Field `minimum_sale_price` ditambahkan ke tree order_line sebagai `column_invisible` (dipakai cuma untuk decoration, tidak ditampilkan sebagai kolom).
- `[BSL-008]` **`[NO-SPEC]` `[DIWARISI-SOURCE]` TEMUAN BARU** — `views/product_template_views.xml` (loaded pertama, target `inherit_id=product.product_template_only_form_view`) dan `views/products.xml` (loaded kedua, target `inherit_id=product.product_template_form_view`) mendefinisikan XML-ID **identik** `product_template_inherit_sale_margin_threshold`. Karena keduanya benar-benar ada di `data:` manifest (beda dari kasus dead-file `pos_margin_threshold`), Odoo memuat keduanya sebagai `<record id="...">` yang SAMA — record kedua (`products.xml`) menimpa SELURUH field record pertama (termasuk `inherit_id`, `arch`). **Efek nyata:** kustomisasi form yang ditujukan untuk `product_template_only_form_view` tidak pernah benar-benar diterapkan — yang benar-benar aktif cuma versi dari `products.xml` (target `product_template_form_view`). File `product_template_views.xml` secara teknis "dimuat" tapi hasilnya langsung ditimpa, bukan dead code murni seperti di `pos_margin_threshold` (`MF-04`), tapi efeknya serupa: satu dari dua kustomisasi yang dimaksud tidak pernah hidup.
- `[BSL-009]` `[NO-SPEC]` **TEMUAN BARU** — Manifest mendeklarasikan `assets.sale_margin_threshold._assets_sale: ['sale_margin_threshold/static/src/**/*']`, tapi folder `static/src/` **tidak ada** di modul ini sama sekali (tidak ada file JS/CSS/XML template POS). Kemungkinan sisa boilerplate scaffold Odoo yang tidak dibersihkan (module ini tidak butuh asset frontend, semua logic-nya server-side + view Backend biasa).
- `[BSL-010]` `[MATCH]` (ref: BR-06, AC-04-03) Form/easy-edit view produk: field margin disembunyikan kondisional berdasar `module_pos_margin_threshold` DAN `product_variant_count > 1` (multi-variant tanpa is_product_variant) — sama pola visibility seperti `pos_margin_threshold`.

## 7. Dependency Eksternal

### Eksplisit (manifest)
`depends: ['base', 'product', 'sale', 'stock_account']` — semua Native Community.

### Implisit/Inferred
- `hasattr(self, 'is_rental_order')` — deteksi runtime modul rental (`sale_renting` atau serupa), TIDAK di `depends:` (disengaja). **Wajib dicek Step 2** apakah nama field ini masih sama di modul rental 18.0.
- `product.product_template_form_view`, `product.product_template_only_form_view`, `product.product_variant_easy_edit_view`, `sale.view_order_form`, `sale.res_config_settings_view_form` — XML-ID spesifik core, rawan berubah antar versi.
- `base.module_category_hidden` (dipakai `security/groups.xml` untuk `group_sale_margin_action`).

## 8. Quirk / Behavior Non-Obvious

- `[BSL-002]` (lihat §4) — batch-confirm crash, prioritas TINGGI, `MF-06`.
- `[BSL-006]` (lihat §5) — dedup group membership via mutasi state, `MF-05`.
- `[BSL-007]` `[MATCH]` `[PERLU-KEPUTUSAN]` `[DIWARISI-SOURCE]` (ref: backfill F-03, `MF-03` — sama finding dengan `pos_margin_threshold`) Model `wizard.margin.product` didefinisikan `_name` (bukan `_inherit`) identik-byte dengan `pos_margin_threshold` — MRO final cuma berisi kelas dari modul yang diinstall lebih belakangan.
- `[BSL-008]` (lihat §6) — duplikasi XML-ID aktif, `MF-07`.
- `[BSL-011]` `[MATCH]` — `_compute_module_pos_margin_threshold` pakai `@api.depends_context('uid')` padahal compute-nya tidak benar-benar bergantung `uid` — nit efisiensi cache Odoo (invalidasi per-user tidak perlu), BUKAN bug (dikonfirmasi backfill F-05b, tidak diberi status `[PERLU-KEPUTUSAN]` karena tidak ada dampak fungsional). Dipertahankan apa adanya, tidak perlu dicatat sebagai finding terpisah.

---

## Cara Pakai

ID `BSL-NNN` modul ini independen dari `pos_margin_threshold` (mulai dari 001 lagi, tidak lanjut nomor). Rujukan ke `MF-NNN` (root `FINDINGS.md`) dan `F-NNN` (backfill) dicatat eksplisit di tiap klaim yang mewarisi finding lama.
