# Baseline Spec — sale_margin_threshold

**Step:** 1 — Intake & Scope (pelengkap `01a_MIGRATION_INTAKE.md`)
**Tujuan:** dokumentasikan behavior as-is di 18.0 (branch `migration/18.0`, identik dengan working
tree `migration/19.0_target` saat ini).
**Tanggal:** 2026-08-26
**Sumber:** Direkonsiliasi dari `doc-dev/migration_17.0_18.0/doc/01_intake/sale_margin_threshold/01b_BASELINE_SPEC.md`
+ cross-check kode 18.0 aktual + `doc-dev/migration_17.0_18.0/doc/FINDINGS.md` +
`05a_MIGRATION_ACCEPTANCE_CRITERIA.md`/`10_BUSINESS_FLOW_MIGRATION.md` project 17.0→18.0.

> Provenance merujuk ke dua generasi dokumen: `(ref: 17-18/BSL-NNN)` dan `(ref: 17-18/MF-NNN)`.

---

## Ringkasan untuk Review — Perlu Konfirmasi User

**Tally provenance:** 11 klaim `[MATCH]`, 0 `[GAP]`, 2 `[NO-SPEC]` (perincian baru, bukan bug).

- `[BSL-009]` `[DIWARISI-SOURCE]` `[PERLU-KEPUTUSAN — prioritas TINGGI]` — `action_confirm()`
  mengasumsikan `self` singleton, TIDAK ada `for order in self:`. Bug lama, masih terbuka, prioritas
  **Tinggi** di `FINDINGS.md` sebelumnya. Bisa salah kalau core Odoo memanggil override ini dalam
  mode batch confirm. **Butuh keputusan user:** pertahankan identik, atau perbaiki sebagai bagian
  scope migrasi ini?
- `[BSL-010]` `[DIWARISI-SOURCE]` — `_register_hook()` memutasi grup `group_sale_margin_action`
  setiap registry rebuild, bukan cuma saat install — override manual admin bisa ter-reset diam-diam.
- `[BSL-011]` `[DIWARISI-SOURCE]` — dua file view (`product_template_views.xml` DAN `products.xml`)
  SAMA-SAMA dimuat manifest, sama-sama definisikan XML-ID
  `product_template_inherit_sale_margin_threshold` — yang dimuat kedua menimpa total yang pertama.
  Lebih serius dari kasus sibling module (di sana file duplikatnya sengaja tidak dimuat sama sekali).
- `[BSL-012]` `[DIWARISI-SOURCE]` — `assets._assets_sale` menunjuk folder `static/src/` yang tidak
  ada di disk. Cruft, tidak error, prioritas Rendah.
- **Kolisi `wizard.margin.product` dengan `pos_margin_threshold` (`MF-03`):** modul INI yang selalu
  menang MRO — lihat detail di dokumen `pos_margin_threshold`.
- **`MF-21` (bilingual EN/FR `fr_FR` hard dependency) — SUDAH RESOLVED, dikonfirmasi ulang di kode
  aktual** (§5 di bawah): tidak ada lagi referensi `fr_FR`/`with_context(lang=...)` di manapun di
  modul ini (grep bersih). Fix ini harus dipertahankan apa adanya.
- **Dikonfirmasi TIDAK ada referensi `sale.order.line.tax_id`** di modul ini (grep penuh) — breaking
  change 19.0 (`tax_id`→`tax_ids`) yang dicatat di knowledge base **tidak relevan** untuk modul ini.
- **Dependency Enterprise implisit (Rental, `is_rental_order`)** — lihat `01a_MIGRATION_INTAKE.md`
  §0, `native-target-enterprise` wajib untuk verifikasi Step 2.

---

## 1. Tujuan Modul

Menegakkan margin minimum penjualan saat konfirmasi Sale Order. Kategori/produk punya `margin_sale`
(sama seperti `pos_margin_threshold`); saat `action_confirm()` dipanggil, modul mengecek semua baris
order — kalau ada yang di bawah `minimum_sale_price`, sistem memblok (`ValidationError`, bilingual
EN/FR) atau membuka wizard konfirmasi, tergantung setting `blocking_transaction_order`. Rental order
(modul Enterprise) sepenuhnya dikecualikan dari pengecekan ini.

## 2. Model & Tanggung Jawab

| Model | Tanggung Jawab |
|---|---|
| `product.category`/`product.template`/`product.product` (extend) | Sama seperti `pos_margin_threshold` — `margin_sale`, `minimum_sale_price`, `minimum_sale_price_with_tax` — plus flag `module_pos_margin_threshold` untuk dedup UI. |
| `sale.order` (extend) | Override `action_confirm()` — validasi margin, kecuali rental. |
| `sale.order.line` (extend) | Field `minimum_sale_price` (related), dipakai decoration view. |
| `sale.confirmation.wizard` (baru) | Wizard konfirmasi override minimum price. |
| `wizard.margin.product` (baru, `_name` — kolisi dengan `pos_margin_threshold`) | Bulk-assign margin, identik strukturnya dengan sibling module. |
| `res.config.settings` (extend) | Expose `blocking_transaction_order`. |

## 3. Field dengan Makna Bisnis

### `sale.order`
- `is_rental_order_installed_true` (Boolean, compute, tidak stored) — `True` HANYA kalau record punya
  attribute `is_rental_order` (modul Rental Enterprise terinstall) DAN nilainya truthy.

### `sale.order.line`
- `minimum_sale_price` (Float, `related='product_id.minimum_sale_price'`) — murni untuk decoration
  view, `column_invisible` di list (tidak ditampilkan sebagai kolom).

### `sale.confirmation.wizard`
- `message` (Text, `translate=True`) — pesan peringatan bilingual yang ditampilkan ke user.

### `res.config.settings`
- `blocking_transaction_order` (Boolean → config_parameter `post_margin_sale.blocking_transaction_order`).

### `product.template`
- `module_pos_margin_threshold` (Boolean, compute, `@api.depends_context('uid')`, tidak stored) —
  `True` kalau `pos_margin_threshold` terinstall; drives `invisible=` untuk cegah field margin
  tampil dobel.

## 4. Business Workflow / State Transition

### Konfirmasi Sale Order
- `[BSL-001]` `[MATCH]` (ref: 17-18/BSL-001) Kalau `is_rental_order_installed_true` → langsung
  `super().action_confirm()`, TIDAK ADA pengecekan margin sama sekali.
- `[BSL-002]` `[MATCH]` (ref: 17-18/BSL-001) Kalau bukan rental: `check_product_price()` mengumpulkan
  semua produk di `order_line` yang `price_unit < minimum_sale_price`. Kalau kosong → langsung
  `super().action_confirm()`.
- `[BSL-003]` `[MATCH]` (ref: 17-18/BSL-001) Kalau ada line melanggar DAN context
  `skip_check_price` tidak di-set: baca config `post_margin_sale.blocking_transaction_order`.
  - Blocking `True` → `raise ValidationError` (pesan bilingual, lihat `BSL-005`) — order TIDAK
    terkonfirmasi.
  - Blocking `False` → buat `sale.confirmation.wizard` (`message` = versi bilingual sesuai bahasa
    user), return `ir.actions.act_window` modal (`target='new'`) — order **belum** terkonfirmasi,
    menunggu keputusan user di wizard.
- `[BSL-004]` `[MATCH]` (ref: 17-18/BSL-004) Kalau context `skip_check_price=True` (dikirim wizard
  saat user memilih lanjut) → langsung `super().action_confirm()`, TIDAK mengecek ulang margin
  (mencegah rekursi tak berujung).

### Wizard konfirmasi
- `[BSL-005]` `[MATCH]` (ref: 17-18/BSL-004) `action_confirm()` wizard: browse `sale.order` dari
  `active_id`/`active_model` context (dinamis, lihat §2b `01a`), panggil
  `.with_context(skip_check_price=True).action_confirm()` — order akhirnya terkonfirmasi. Tombol
  "Cancel" tidak melakukan apapun ke sale order (murni menutup dialog).

## 5. Server-Side Logic dengan Side Effect

- `[BSL-006]` `[MATCH][DIWARISI-SOURCE]` (ref: 17-18/BSL-003) `detect_user_language()` — HANYA
  membedakan prefix `fr` (kembalikan `'French'`) vs SEMUA bahasa lain (`'Other'`) — bukan mekanisme
  `.po` translasi standar Odoo, generasi string manual bilingual EN/FR.
- `[BSL-007]` `[MATCH][RESOLVED — ref: 17-18/MF-21]` **Mekanisme bilingual `action_confirm()`
  dikonfirmasi ulang di kode aktual saat ini:** baik cabang blocking maupun cabang wizard memilih
  `message`/`message_Fr` (string plain, dibuat manual) sesuai `detect_user_language()` — TIDAK ADA
  lagi pola lama (double-write + `.with_context(lang='fr_FR')` yang mensyaratkan bahasa Prancis
  genuinely terinstall). Grep `fr_FR`/`with_context(lang=` di seluruh modul: **0 match**. Fix ini
  (disetujui eksplisit dev 2026-08-26, sebelum project 18.0→19.0 ini dimulai) harus dipertahankan
  identik — bukan perubahan baru untuk migrasi ini.
- `[BSL-008]` `[MATCH]` (ref: 17-18/BSL-005) `module_pos_margin_threshold` compute murni drives
  `invisible=` view — tidak ada side effect lain.
- `[BSL-009]` `[MATCH][DIWARISI-SOURCE][PERLU-KEPUTUSAN — prioritas Tinggi]` (ref: 17-18/BSL-002,
  17-18/MF-06) `action_confirm()` membaca `self.is_rental_order_installed_true`/`self.order_line`
  TANPA `for order in self:` — asumsi singleton. Kalau core Odoo memanggil override ini untuk banyak
  order sekaligus (batch confirm), logic ini hanya akan mengevaluasi record PERTAMA di `self`, bukan
  tiap order secara independen. Bug lama, masih terbuka dari project 17→18, prioritas **Tinggi**.
  **Perlu keputusan user eksplisit** (lihat §Ringkasan) — apakah dipertahankan identik (risiko sama
  berlanjut ke 19.0) atau diperbaiki di project ini (harus disetujui eksplisit dulu, dicatat sebagai
  perubahan disengaja, bukan "port kode saja" murni).
- `[BSL-010]` `[MATCH][DIWARISI-SOURCE]` (ref: 17-18/BSL-006, 17-18/MF-05) `ProductProduct._register_hook()`
  (dijalankan setiap registry rebuild, TIDAK hanya saat install): kalau `pos_margin_threshold`
  terinstall → mengosongkan membership `group_sale_margin_action` untuk SEMUA user; kalau tidak →
  memberikan grup itu ke SEMUA user internal. Ini mutasi paksa, bukan kondisi deklaratif — perubahan
  manual admin ke membership grup ini bisa ter-reset diam-diam di reload registry berikutnya.

## 6. Client-Side Behavior (Views, JS, Owl)

Tidak ada JS/Owl sama sekali (`[BSL-011]` di §8, `MF-08`) — modul ini murni server-side + view XML.

- `[BSL-011]` `[MATCH]` (ref: 17-18/BSL-007) Form Sale Order: order line di bawah minimum diberi
  `decoration-danger`, KECUALI order adalah rental (`not parent.is_rental_order_installed_true`).
  `minimum_sale_price` ditambahkan sebagai `column_invisible` (dipakai decoration, tidak ditampilkan
  sebagai kolom terpisah).
- Form Product Template/Variant: sama seperti `pos_margin_threshold`, ditambah guard
  `module_pos_margin_threshold` untuk mencegah field margin tampil dobel kalau kedua modul margin
  terinstall bersamaan.

## 7. Dependency Eksternal

### Eksplisit (manifest)
- `depends: ['base', 'product', 'sale', 'stock_account']`

### Implisit/Inferred
- **Rental (Enterprise, `is_rental_order`)** — via `hasattr()`, opsional/soft. Lihat `01a` §0.
- `pos_margin_threshold` (custom sibling) — via `ir.module.module` lookup (`_register_hook()`,
  `_compute_module_pos_margin_threshold`) + kolisi `_name` `wizard.margin.product`.

## 8. Quirk / Behavior Non-Obvious

- `[BSL-012]` `[MATCH][DIWARISI-SOURCE][PERLU-KEPUTUSAN]` (ref: 17-18/BSL-008, 17-18/MF-07) Manifest
  memuat KEDUA `views/product_template_views.xml` dan `views/products.xml`, dan KEDUANYA
  mendefinisikan XML-ID identik `product_template_inherit_sale_margin_threshold` dengan `inherit_id`
  BERBEDA. Karena keduanya dimuat (bukan salah satu dead file seperti kasus `pos_margin_threshold`),
  record yang dimuat KEDUA (`products.xml`, urutan sesuai manifest `data:`) menimpa TOTAL record
  pertama — termasuk `inherit_id`-nya. Konsekuensi: kustomisasi yang dituju ke
  `product.product_template_only_form_view` (via `product_template_views.xml`) tidak pernah benar-
  benar aktif; hanya kustomisasi ke `product.product_template_form_view` (via `products.xml`) yang
  jalan. **Ini lebih serius dari kasus dead-file sibling module** karena tidak ada error/warning
  apapun yang menandakan salah satu record hilang.
- `[BSL-013]` `[MATCH][DIWARISI-SOURCE]` (ref: 17-18/BSL-009) Manifest deklarasikan
  `assets.sale_margin_threshold._assets_sale` → `static/src/**/*`, tapi folder `static/src/` TIDAK
  ADA di disk sama sekali (hanya `static/description/*` untuk listing app). Glob kosong, tidak ada
  efek fungsional, prioritas Rendah.
- `[BSL-014]` `[MATCH][DIWARISI-SOURCE]` (ref: 17-18/BSL-011, 17-18/MF-03) Kolisi `wizard.margin.product`
  dengan `pos_margin_threshold` — lihat detail lengkap di dokumen baseline `pos_margin_threshold`
  §8 (`BSL-016` di sana). Modul INI yang selalu menang MRO.
- `[BSL-015]` `[NO-SPEC]` (baru — perincian) `_compute_module_pos_margin_threshold` dideklarasikan
  dengan `@api.depends_context('uid')` walau compute-nya sendiri tidak benar-benar bergantung pada
  `uid` — nit efisiensi (cache invalidation per-user yang tidak perlu), dikonfirmasi TIDAK berdampak
  fungsional (ref: 17-18/BSL-011 lama). Tidak perlu diperbaiki, murni catatan.
- `controllers/controllers.py` — sama seperti sibling module, seluruh isi di-comment, scaffold mati
  sejak awal.

---

## Cara Pakai

Sama seperti dokumen `pos_margin_threshold` — ID `BSL-NNN` di sini adalah penomoran baru khusus
modul ini untuk project 18.0→19.0, dirujuk balik ke `(ref: 17-18/BSL-NNN)`/`(ref: 17-18/MF-NNN)`
untuk ketertelusuran ke dokumen project sebelumnya.
