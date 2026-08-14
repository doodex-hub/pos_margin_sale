# Functional Spec — pos_margin_threshold

**Module:** `pos_margin_threshold`
**Odoo Version:** 17.0
**Depends:** `base`, `point_of_sale`, `product`, `stock_account`
**Last Updated:** 2026-07-31
**Status:** Backfill retroaktif — dibaca dari kode existing, bukan requirement baru
**Provenance:** lihat `pos-margin-sale/CLAUDE.md` §Provenance Tag

---

## Ringkasan untuk Review — Perlu Konfirmasi User

1. `[PERLU-KEPUTUSAN]` **F-05** (lihat `FINDINGS.md`) — `action_confirm` di `sale_margin_threshold`
   (modul sibling) memecah batch-confirm multi-order Odoo core. Dicantumkan di sini karena
   ditemukan lewat cek wajib Step 01, walau lokasinya di modul lain.
2. `[PERLU-KEPUTUSAN]` **F-01** — `minimum_sale_price_with_tax` tidak didefinisikan ulang per-variant
   di `product.product`, delegasi otomatis dari `product.template` lewat `_inherits` Odoo core —
   berpotensi tidak konsisten untuk produk multi-variant dengan margin berbeda per variant.
3. `[PERLU-KEPUTUSAN]` **F-02** — field `blocking_transaction_order` dideklarasikan modul ini tapi
   tidak punya efek/UI sama sekali kecuali `sale_margin_threshold` juga terinstall.
4. `[PERLU-KEPUTUSAN]` **F-03** — model `wizard.margin.product` didefinisikan identik dan independen
   di modul ini DAN `sale_margin_threshold` (bukan lewat `_inherit`).
5. `[PERLU-KEPUTUSAN]` **F-04** — mekanisme dedup action "Update margin sale" antar modul (lewat
   `_register_hook` di `sale_margin_threshold`) memutasi membership group setiap registry reload.

---

## Latar Belakang & Tujuan

Modul ini menghitung dan menegakkan harga jual minimum + margin per produk khusus untuk transaksi
**Point of Sale** — memberi peringatan (atau memblokir pembayaran, sesuai konfigurasi) kalau kasir
menjual produk di bawah harga minimumnya. `[HASIL-BACA]`

---

## Scope

### Yang Termasuk (disimpulkan dari kode)

- Field `margin_sale` (%) di `product.category`, diwariskan otomatis ke `product.template`/
  `product.product` lewat compute, tapi bisa di-override manual per template/variant (compute
  `store=True, readonly=False`). `[HASIL-BACA]`
- Field `minimum_sale_price` = `standard_price * (1 + margin_sale/100)`, dan
  `minimum_sale_price_with_tax` = `minimum_sale_price * (1 + total_tax_amount/100)` — dihitung di
  level `product.template`. `[HASIL-BACA]`
- Wizard "Assign Margin" (`action_assign_margin`) untuk set margin massal ke banyak
  produk/template sekaligus dari list view. `[HASIL-BACA]`
- Setting "Blocking Transaction POS" (`blocking_transaction_pos`) — kalau aktif, kasir TIDAK BISA
  bayar order yang mengandung baris di bawah harga minimum (`ErrorPopup`, pembayaran dibatalkan).
  Kalau nonaktif, muncul `ConfirmPopup` (boleh lanjut/batal). `[HASIL-BACA]`
- Loader POS (`_loader_params_product_product`) menambahkan `minimum_sale_price` +
  `minimum_sale_price_with_tax` ke data produk yang dikirim ke frontend POS. `[HASIL-BACA]`
- Highlight visual: baris order POS yang harganya di bawah minimum ditandai merah + pesan peringatan
  di UI order (`orderline.xml`), dan field `list_price`/`lst_price` di form produk ditandai merah
  kalau di bawah `minimum_sale_price`. `[HASIL-BACA]`

### Yang Tidak Termasuk

- `controllers/controllers.py` ada di struktur folder tapi **seluruh isinya di-comment**
  (boilerplate scaffold Odoo default) — tidak ada route HTTP yang benar-benar terdaftar. `[HASIL-BACA]`
- Tidak ada validasi/blocking di level Sale Order — itu domain modul sibling
  `sale_margin_threshold`. `[HASIL-BACA]`

---

## User Stories (rekonstruksi)

> Ditulis dari sudut pandang kode, bukan wawancara user asli.

### US-01 — Kasir mendapat peringatan saat menjual di bawah harga minimum
Sebagai kasir POS, saat saya membayar order yang mengandung produk di bawah harga minimumnya, saya
melihat dialog peringatan (atau pembayaran diblokir total kalau admin mengaktifkan mode blocking).
`[HASIL-BACA]`

### US-02 — Admin mengatur margin per kategori tanpa membuka produk satu-satu
Sebagai admin, saya set `margin_sale` di level `product.category` supaya semua produk di kategori
itu otomatis punya harga minimum terhitung, tanpa perlu edit produk satu-satu. `[HASIL-BACA]`

### US-03 — Admin assign margin massal ke produk terpilih
Sebagai admin, dari list view Produk/Product Variants, saya pilih beberapa produk lalu jalankan
action "Update margin sale" untuk set margin yang sama ke semuanya sekaligus. `[HASIL-BACA]`

---

## Business Rules

> **Cek wajib tabrakan nama method Odoo core (Step 01):** `_loader_params_product_product` (pos.session)
> MEMANG method core, tapi dipanggil lewat `super()` dengan benar (extend, bukan replace) — aman,
> pattern override yang benar. Tidak ada method lain di modul ini yang bentrok nama dengan core.

### BR-01 — Margin sale diwariskan dari kategori, bisa dioverride di level template — TAPI TIDAK BISA divergen antar variant satu template
`margin_sale` di `product.template`/`product.product` = compute dari `categ_id.margin_sale`
(template) atau `product_tmpl_id.margin_sale` (variant), TAPI `store=True, readonly=False` — user
bisa menulis manual, dan Odoo hanya recompute ulang kalau dependency (`categ_id.margin_sale` dst)
berubah, bukan tiap kali dibaca. Jadi override manual "menang" sampai dependency-nya sendiri
di-trigger ulang. `[HASIL-BACA]`
**TERKONFIRMASI lewat eksekusi (F-01, lihat `FINDINGS.md`):** inverse `margin_sale` di
`ProductProduct` menulis balik ke `product_tmpl_id.margin_sale` (TEMPLATE, shared) — akibatnya
menulis margin di SATU variant otomatis mengubah margin SEMUA variant sibling-nya juga. Margin
TIDAK PERNAH bisa berbeda antar variant dalam satu template, walau field-nya terlihat "milik
variant sendiri". `[PERLU-KEPUTUSAN]`
**Lokasi kode:** `models/product.py:20-23` (template), `:64-67` (inverse variant), `:73-76` (compute variant)

### BR-02 — Minimum sale price = cost + margin
`minimum_sale_price = standard_price * (1 + margin_sale/100)`, computed+inverse (bisa diedit
manual, otomatis balik hitung `margin_sale` dari nilai yang diinput). `[HASIL-BACA]`
**Lokasi kode:** `models/product.py:31-34` (template), `:78-81` (variant)

### BR-03 — Minimum sale price termasuk pajak dihitung HANYA di level template (TERNYATA TIDAK MASALAH)
`minimum_sale_price_with_tax = minimum_sale_price * (1 + total_tax_amount/100)`. Field ini **tidak
didefinisikan ulang** di kelas `ProductProduct` — nilainya didapat lewat delegasi otomatis Odoo core
(`product.product` `_inherits` `product.template`), BUKAN dihitung dari `minimum_sale_price` milik
variant itu sendiri. **Dikonfirmasi lewat eksekusi (F-01) bahwa ini TIDAK menyebabkan inkonsistensi**
seperti diduga awal — karena `margin_sale` (BR-01) TIDAK PERNAH bisa berbeda antar variant satu
template, `minimum_sale_price` template dan variant SELALU sama juga, jadi delegasi
`minimum_sale_price_with_tax` ke template aman dalam praktik (bukan karena desainnya benar,
tapi karena precondition inkonsistensinya tidak pernah tercapai). `[HASIL-BACA]` — lihat **F-01**
di `FINDINGS.md` untuk kronologi lengkap.
**Lokasi kode:** `models/product.py:25-29` (satu-satunya definisi, di kelas `ProductTemplate`)

### BR-04 — Setting "Blocking Transaction POS" mengontrol perilaku saat bayar
`blocking_transaction_pos` (config_parameter `post_margin_sale.blocking_transaction_pos`) dibaca di
`pos.config.is_blocked_warning` (compute), lalu dikonsumsi JS (`pos_store`/patch `Order.pay`):
- **True** → tampilkan `ErrorPopup`, batalkan proses bayar total.
- **False** (default) → tampilkan `ConfirmPopup`, user bisa pilih lanjut/batal.
`[HASIL-BACA]`
**Lokasi kode:** `models/pos_config.py:10-16`, `static/src/store/models/models.js:54-79`

### BR-05 — Field `blocking_transaction_order` dideklarasikan tapi tidak dipakai modul ini sendiri
Modul ini juga punya field `blocking_transaction_order` (config_parameter
`post_margin_sale.blocking_transaction_order`) — TAPI tidak pernah ditampilkan di view settings
modul ini (`views/res_config_settings.xml` cuma expose `blocking_transaction_pos`), dan tidak ada
kode di modul ini yang `get_param` key tersebut. Field ini baru bermakna kalau
`sale_margin_threshold` (modul sibling) juga terinstall. `[PERLU-KEPUTUSAN]` — lihat **F-02**.
**Lokasi kode:** `models/res_config_settings.py:8`

### BR-06 — Wizard assign margin massal menimpa `margin_sale` produk terpilih
`wizard.margin.product.action_assing_margin()` (nama method typo "assing", bukan "assign" —
konsisten di semua lapisan, bukan bug fungsional) menulis field `margin` wizard ke SEMUA
produk/template yang dipilih user tanpa konfirmasi tambahan (langsung overwrite, tidak ada
undo/histori selain `tracking=True` di chatter). `[HASIL-BACA]`
**Lokasi kode:** `wizard/wizard_margin_product.py:23-31`

### BR-07 — Model wizard `wizard.margin.product` didefinisikan independen, identik dengan modul sibling
Modul ini mendefinisikan `_name = 'wizard.margin.product'` tanpa `_inherit` — model DENGAN NAMA
PERSIS SAMA juga didefinisikan independen (byte-identik) di `sale_margin_threshold`. Saat ini aman
karena field/method-nya sama persis, tapi rawan divergen di masa depan. `[PERLU-KEPUTUSAN]` — lihat
**F-03**.
**Lokasi kode:** `wizard/wizard_margin_product.py:4-6`
