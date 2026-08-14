# Functional Spec — sale_margin_threshold

**Module:** `sale_margin_threshold`
**Odoo Version:** 17.0
**Depends:** `base`, `product`, `sale`, `stock_account`
**Last Updated:** 2026-07-31
**Status:** Backfill retroaktif — dibaca dari kode existing, bukan requirement baru
**Provenance:** lihat `pos-margin-sale/CLAUDE.md` §Provenance Tag

---

## Ringkasan untuk Review — Perlu Konfirmasi User

1. `[PERLU-KEPUTUSAN]` **F-05 (PRIORITAS TINGGI)** — `action_confirm` di-override dengan asumsi
   `self` singleton (baca `self.is_rental_order_installed_true`, `self.order_line` langsung tanpa
   loop) — **memecahkan batch-confirm multi Sale Order Odoo core** (`ValueError: Expected
   singleton`). Ini hasil cek wajib Step 01 "tabrakan nama method dengan Odoo core".
2. `[PERLU-KEPUTUSAN]` **F-04** — `_register_hook` memutasi membership group `group_sale_margin_action`
   berdasar status install `pos_margin_threshold`, setiap registry reload — bisa membalikkan
   perubahan manual admin secara silent.
3. `[PERLU-KEPUTUSAN]` **F-03** — model `wizard.margin.product` didefinisikan identik dan independen
   di modul ini DAN `pos_margin_threshold`.
4. `[PERLU-KEPUTUSAN]` **F-05b** — field `module_pos_margin_threshold` pakai
   `@api.depends_context('uid')` padahal compute-nya tidak benar-benar bergantung `uid` (cuma nit
   efisiensi cache, bukan bug).

---

## Latar Belakang & Tujuan

Modul ini menegakkan aturan harga jual minimum + margin untuk **Sale Order** — memblokir atau
meminta konfirmasi tambahan saat user mencoba confirm quotation yang mengandung baris di bawah
harga minimum produk. `[HASIL-BACA]`

---

## Scope

### Yang Termasuk (disimpulkan dari kode)

- Field `margin_sale`, `minimum_sale_price`, `minimum_sale_price_with_tax` di
  `product.category`/`product.template`/`product.product` — **definisi identik** dengan
  `pos_margin_threshold` (lihat **F-01 pola serupa**, dan **F-03**). `[HASIL-BACA]`
- Override `sale.order.action_confirm()`: sebelum confirm, cek semua order line — kalau ada yang di
  bawah minimum, munculkan pesan (blocking total ATAU wizard konfirmasi tambahan, sesuai setting).
  `[HASIL-BACA]`
- Wizard konfirmasi (`sale.confirmation.wizard`) — muncul kalau setting TIDAK blocking, user bisa
  pilih lanjut confirm walau ada baris di bawah minimum. `[HASIL-BACA]`
- Setting "Blocking Transaction Order" (`blocking_transaction_order`), dan grup `group_sale_margin_action`
  yang mengontrol visibilitas action "Update margin sale" — otomatis dikosongkan/diisi berdasar
  status install `pos_margin_threshold` (lihat **F-04**). `[HASIL-BACA]`
- Pengecualian untuk **Rental Order** — kalau `sale.order` juga punya field `is_rental_order`
  (artinya modul `sale_renting`/rental terinstall) DAN order itu memang rental, validasi margin
  DI-SKIP TOTAL, langsung `super().action_confirm()`. `[HASIL-BACA]`
- Deteksi bahasa user (EN/FR) untuk pesan error — HANYA dua bahasa ini yang ditangani; bahasa lain
  fallback ke pesan Inggris. `[HASIL-BACA]`

### Yang Tidak Termasuk

- `controllers/controllers.py` — seluruh isinya di-comment, sama seperti `pos_margin_threshold`,
  tidak ada route aktif. `[HASIL-BACA]`
- Tidak ada integrasi apapun ke POS — itu domain modul sibling `pos_margin_threshold`. `[HASIL-BACA]`

---

## User Stories (rekonstruksi)

### US-01 — Sales confirm quotation dan mendapat peringatan harga di bawah minimum
Sebagai sales, saat saya confirm quotation yang mengandung produk di bawah harga minimumnya, saya
melihat pesan peringatan (blocking total, atau wizard konfirmasi kalau admin izinkan override).
`[HASIL-BACA]`

### US-02 — Rental order tidak terkena validasi margin
Sebagai sales yang mengelola rental order, proses confirm saya tidak terganggu validasi margin sama
sekali — modul ini secara eksplisit skip untuk rental order. `[HASIL-BACA]`

### US-03 — Admin tidak melihat action duplikat kalau pos_margin_threshold juga terinstall
Sebagai admin dengan kedua modul margin terinstall, saya hanya melihat SATU action "Update margin
sale" (bukan dua), sesuai desain dedup lewat `_register_hook`. `[HASIL-BACA]` — lihat **F-04** untuk
catatan risiko implementasinya.

---

## Business Rules

> **Cek wajib tabrakan nama method Odoo core (Step 01) — TEMUAN PENTING:** `action_confirm`
> (`sale.order`) BENTROK NAMA dengan method core Odoo (`sale.order.action_confirm`, tombol
> "Confirm" quotation). Override ini MEMANGGIL `super().action_confirm()` di jalur fallthrough
> (jadi TIDAK silent-replace total seperti pola bug di `USAGE_GUIDE.md`) — tapi punya bug class
> LAIN yang sama beratnya: asumsi `self` singleton. Lihat BR-01 dan **F-05**.
>
> `_register_hook` (`product.product`) JUGA bentrok nama dengan method lifecycle Odoo core
> (`models.BaseModel._register_hook`) — TAPI ini PAKAI SESUAI DESAIN (hook resmi Odoo untuk
> registrasi custom logic saat registry dibangun, wajib panggil `super()._register_hook()` di awal,
> yang memang dilakukan). Bukan bug, dicantumkan di sini supaya jelas sudah dicek, bukan terlewat.

### BR-01 — Validasi harga minimum dijalankan sebelum confirm, KECUALI rental order
`action_confirm()` di-override: skip total (langsung `super()`) kalau
`is_rental_order_installed_true` True. Selain itu, cek `check_product_price()` (baris dengan
`price_unit < minimum_sale_price`), lalu cabang sesuai `blocking_transaction_order`:
- **True** → `raise ValidationError` (blocking total, TIDAK ADA cara lanjut dari UI biasa).
- **False** → buka `sale.confirmation.wizard` (pesan bilingual EN/FR), user pilih confirm ulang
  dengan context `skip_check_price=True`.
`[HASIL-BACA]`
**Lokasi kode:** `models/sale_order.py:19-52`

### BR-02 — `action_confirm` override TIDAK menghandle multi-record (bug)
`self.is_rental_order_installed_true` (baris 21) dan `self.check_product_price()` → `self.order_line`
(baris 66-68) dibaca LANGSUNG tanpa `for order in self:` — Odoo core `action_confirm` didesain
mendukung confirm BANYAK sale order sekaligus dari list view (batch action). Membaca field pada
recordset multi-record akan `raise ValueError: Expected singleton`. `[PERLU-KEPUTUSAN]` — lihat
**F-05**, prioritas Tinggi.
**Lokasi kode:** `models/sale_order.py:19-27`

### BR-03 — Deteksi bahasa hanya EN/FR
`detect_user_language()` cuma bedakan "French" (prefix `fr`) vs "Other" (semua bahasa lain
diperlakukan sebagai English). Pesan error selalu ada versi EN + FR yang di-generate manual (bukan
lewat mekanisme translasi `.po` standar Odoo untuk string dinamis ini). `[HASIL-BACA]`
**Lokasi kode:** `models/sale_order.py:54-62`

### BR-04 — Wizard konfirmasi men-skip re-validasi lewat context flag
`sale.confirmation.wizard.action_confirm()` memanggil ulang
`sale.with_context(skip_check_price=True).action_confirm()` — ini MEMANGGIL LAGI method yang sama
(rekursif via context flag, bukan infinite loop karena `skip_check_price` membuat kondisi `if`
BR-01 jadi False lalu jatuh ke `return super().action_confirm()`). `[HASIL-BACA]`
**Lokasi kode:** `wizard/sale_confirmation.py:10-15`

### BR-05 — Dedup action "Update margin sale" lintas modul via mutasi group membership
`_register_hook()` (dipanggil Odoo tiap registry dibangun/reload, bukan cuma saat install) mengecek
apakah `pos_margin_threshold` terinstall:
- **Terinstall** → SEMUA user dihapus dari `group_sale_margin_action` (action jadi tak terlihat
  siapapun, karena `pos_margin_threshold` sudah punya action serupa tanpa group-gating).
- **Tidak terinstall** → SEMUA internal user (`base.group_user`) ditambahkan ke group (action
  terlihat semua orang, seperti tidak ada gating sama sekali).
`[PERLU-KEPUTUSAN]` — lihat **F-04**, mekanisme ini memutasi state group secara implisit setiap
reload, berpotensi membalikkan perubahan manual admin tanpa peringatan.
**Lokasi kode:** `models/product.py:115-131`

### BR-06 — Field cross-module `module_pos_margin_threshold` sebagai flag UI
Field compute ini murni untuk keperluan `invisible=` di view (`views/products.xml`,
`views/product_template_views.xml`) — menyembunyikan field margin_sale/minimum_sale_price milik
modul ini di form produk KALAU `pos_margin_threshold` juga terinstall (supaya field yang sama tidak
tampil dobel dari 2 modul). `[HASIL-BACA]`
**Lokasi kode:** `models/product.py:18-31`
