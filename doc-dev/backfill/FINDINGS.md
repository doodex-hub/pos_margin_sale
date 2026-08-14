# Findings — pos-margin-sale (3 modul: pos_margin_threshold, sale_margin_threshold, pin_message)

> Satu file konsolidasi untuk KETIGA modul (keputusan struktur, lihat `CLAUDE.md` §"Adaptasi
> multi-modul") — tiap finding diberi prefix modul supaya tetap bisa dipilah. Diisi terus sepanjang
> proses, direview batch oleh pemilik modul setelah draft lengkap.
>
> **Dokumen hidup:** kalau pemilik modul memperbaiki kode berdasar finding di sini, update entry
> jadi `✅ RESOLVED` + tanggal + bukti test, jangan dihapus.

---

## Ringkasan

| ID | Modul | Judul | Tag | Prioritas | Verifikasi |
|---|---|---|---|---|---|
| F-01 | pos_margin_threshold | `margin_sale` per-variant TIDAK BISA divergen — inverse menulis ke template (shared) | `[PERLU-KEPUTUSAN]` | Sedang | ✅ **Dieksekusi (Docker), terkonfirmasi** |
| F-02 | pos_margin_threshold | `blocking_transaction_order` dideklarasikan tapi tidak berefek sendirian | `[PERLU-KEPUTUSAN]` | Rendah | ✅ Dieksekusi, terkonfirmasi |
| F-03 | pos_margin_threshold + sale_margin_threshold | Model `wizard.margin.product`: kelas `pos_margin_threshold` HILANG TOTAL dari `__mro__` saat 2 modul terinstall | `[PERLU-KEPUTUSAN]` | Sedang | ✅ Dieksekusi, terkonfirmasi (lebih presisi dari hipotesis awal) |
| F-04 | sale_margin_threshold (interaksi dgn pos_margin_threshold) | `_register_hook` memutasi group membership tiap registry reload | `[PERLU-KEPUTUSAN]` | Sedang | ✅ Dieksekusi, terkonfirmasi |
| F-05 | sale_margin_threshold | `action_confirm` override asumsi singleton — memecah batch-confirm Odoo core | `[PERLU-KEPUTUSAN]` | **Tinggi** | ✅ **Dieksekusi 2×, terkonfirmasi** (test sendiri + demo data `sale_stock` core ikut crash) |
| F-06 | pin_message | `onClickPin` JS menimpa total (bukan extend) patch core `discuss/message_pin` | `[PERLU-KEPUTUSAN]` | Sedang | ⬜ Desk-review saja (JS, lihat limitasi) |
| F-07 | pin_message | `console.log` debug tertinggal di `pinMessage.js` | `[HASIL-BACA]` | Rendah | ⬜ Desk-review saja (JS, lihat limitasi) |

---

## Detail

### F-01 — `margin_sale` per-variant TIDAK BISA divergen — inverse selalu menulis ke template (shared)
**Modul:** `pos_margin_threshold`
**Tag:** `[PERLU-KEPUTUSAN]`
**Status:** ✅ Terkonfirmasi lewat eksekusi nyata (`tests/test_margin_sale.py::test_margin_sale_inverse_writes_to_shared_template_not_per_variant`, 3× run Docker, 2026-07-31) — **hipotesis AWAL finding ini SALAH, direvisi total setelah eksekusi** (lihat riwayat di bawah).
**Lokasi:** `pos_margin_threshold/models/product.py:64-67` (`ProductProduct._set_product_margin_sale`, inverse method)
**Ref:** BR-01/BR-03 (`spec/pos_margin_threshold/`), AC-01-06 (direvisi)
**Riwayat revisi (transparansi metodologis, sesuai prinsip BACKFILL "hipotesis dari baca kode HARUS diuji"):**
Hipotesis AWAL (murni `[HASIL-BACA]`): "`minimum_sale_price_with_tax` tidak didefinisikan ulang di
`ProductProduct`, delegasi dari `product.template` lewat `_inherits` Odoo core — untuk produk
multi-variant dengan margin BERBEDA per variant, field ini bisa inkonsisten." Saat menulis test
untuk MEMBUKTIKAN precondition ini (2 variant, margin berbeda), precondition-nya sendiri GAGAL
tercapai dua kali berturut-turut (`assertNotEqual` gagal, kedua variant selalu berakhir dengan
nilai SAMA) — investigasi lebih lanjut menemukan akar masalah yang lebih dalam dari hipotesis awal.
**Deskripsi (temuan final, terkonfirmasi):** `margin_sale` pada `ProductProduct` didefinisikan
`compute="_compute_margin_sale", inverse="_set_product_margin_sale", store=True, readonly=False`
— TAPI method inverse-nya (`_set_product_margin_sale`) menulis ke
`rec.product_tmpl_id.write({'margin_sale': rec.margin_sale})`, yaitu ke TEMPLATE (shared oleh
SEMUA variant), bukan ke variant itu sendiri. Karena `_compute_margin_sale` semua variant
`@api.depends('product_tmpl_id.margin_sale')`, menulis margin di SATU variant otomatis
me-recompute-ulang margin SEMUA variant sibling ke nilai yang sama. **Akibatnya:
`minimum_sale_price`/`minimum_sale_price_with_tax` (yang menghitung dari `margin_sale`) TIDAK
PERNAH bisa berbeda antar variant satu template** — kebalikan dari kesan yang diberikan field
`margin_sale` yang terlihat "milik variant sendiri" (punya inverse sendiri, `store=True` sendiri).
Dikonfirmasi dua arah: set `variant_a.margin_sale=20` → `variant_b.margin_sale` ikut jadi 20; lalu
set `variant_b.margin_sale=50` → `variant_a.margin_sale` ikut balik jadi 50 ("last write wins"
untuk SEMUA variant, bukan per-variant).
**Dampak:** Sedang — bukan crash/error, tapi fitur "margin per-variant" yang tersirat dari desain
field-nya TERNYATA TIDAK PERNAH bisa dipakai sungguhan; kalau user mengedit margin salah satu
variant dengan asumsi "cuma variant ini yang berubah", SEMUA variant sibling-nya ikut berubah
tanpa peringatan apapun. Konsekuensi turunan: `minimum_sale_price_with_tax` (yang cuma
didefinisikan di level template, delegasi ke variant lewat `_inherits`) TIDAK bisa inkonsisten
seperti diduga hipotesis awal — justru karena margin/harga TIDAK PERNAH divergen antar variant
sejak awal, bukan karena delegasinya "kebetulan aman".
**Rekomendasi:** Kalau margin per-variant genuinely diinginkan (produk sama, variant beda margin),
`_set_product_margin_sale` perlu diubah supaya TIDAK menulis balik ke `product_tmpl_id` — tapi ini
perubahan kode bisnis, di luar scope BACKFILL. Kalau margin SELALU dimaksudkan sama untuk semua
variant satu template (desain yang disengaja), field `margin_sale` di `ProductProduct` jadi
redundant (bisa langsung baca dari template) — perlu klarifikasi intent ke pemilik modul.
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### F-02 — `blocking_transaction_order` dideklarasikan di `pos_margin_threshold` tapi tidak berefek sendirian
**Modul:** `pos_margin_threshold`
**Tag:** `[PERLU-KEPUTUSAN]`
**Status:** ✅ Terkonfirmasi lewat eksekusi (`tests/test_margin_sale.py::test_blocking_transaction_order_field_has_no_view_in_this_module` — Pass, field ada di registry tapi tidak muncul di `arch_db` view settings modul ini)
**Lokasi:** `pos_margin_threshold/models/res_config_settings.py:8`
**Ref:** BR-05, AC-04-01
**Deskripsi:** Field `blocking_transaction_order` (config_parameter
`post_margin_sale.blocking_transaction_order`) dideklarasikan di modul ini, tapi tidak pernah
ditampilkan di view settings modul ini (`views/res_config_settings.xml` cuma expose
`blocking_transaction_pos`) dan tidak dibaca oleh kode apapun di modul ini. Field ini hanya
bermakna kalau `sale_margin_threshold` JUGA terinstall (yang punya view + kode yang membacanya).
**Dampak:** Rendah — tidak menyebabkan error, tapi membingungkan developer yang membaca modul ini
sendirian (field yang terlihat tidak dipakai sama sekali). Kalau `pos_margin_threshold` pernah
dipasang TANPA `sale_margin_threshold`, field ini murni dead weight di database.
**Rekomendasi:** Pindahkan deklarasi field ke `sale_margin_threshold` saja (satu-satunya modul yang
benar-benar memakainya), ATAU dokumentasikan eksplisit di kode kalau duplikasi ini disengaja untuk
alasan tertentu (mis. supaya key config_parameter "siap" walau modul lain belum terinstall).
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### F-03 — Model `wizard.margin.product`: kelas `pos_margin_threshold` HILANG TOTAL dari `__mro__` saat 2 modul terinstall
**Modul:** `pos_margin_threshold` + `sale_margin_threshold`
**Tag:** `[PERLU-KEPUTUSAN]`
**Status:** ✅ Terkonfirmasi lewat eksekusi (`pos_margin_threshold/tests/test_cross_module.py`, Docker, 2026-07-31) — **lebih presisi dari hipotesis awal ("digabung aman"), lihat detail MRO di bawah.**
**Lokasi:** `pos_margin_threshold/wizard/wizard_margin_product.py:4-31`,
`sale_margin_threshold/wizard/wizard_margin_product.py:4-31` (byte-identik); method
`action_assign_margin()` juga diduplikasi identik di `product.py` kedua modul.
**Ref:** BR-07 (pos), BR-07 (sale, spec sama)
**Deskripsi:** Kedua modul mendefinisikan `_name = 'wizard.margin.product'` TANPA `_inherit`.
Hipotesis awal (`[HASIL-BACA]`) menduga Odoo "menggabungkan" kedua kelas jadi satu class gabungan
via multiple-inheritance (mirip `_inherit`). **Eksekusi nyata MEMBUKTIKAN INI SALAH** — `__mro__`
lengkap dari `type(self.env['wizard.margin.product'])` HANYA berisi SATU kelas
`WizardMarginProduct` (dari `sale_margin_threshold`, modul yang diinstall LEBIH BELAKANGAN sesuai
urutan `-i pos_margin_threshold,sale_margin_threshold`) — kelas `WizardMarginProduct` milik
`pos_margin_threshold` TIDAK MUNCUL SAMA SEKALI di `__mro__` final. Artinya: definisi Python
`pos_margin_threshold` untuk model ini SEPENUHNYA DIBUANG/DIGANTIKAN (bukan digabung) saat kedua
modul terinstall bersamaan — persis pola bug "override method by name" yang didokumentasikan
`USAGE_GUIDE.md` (`onchange_partner_id` lesson), TAPI di level SELURUH MODEL, bukan satu method.
`ir.model`/`ir.model.data` TETAP mencatat kedua modul sebagai "pemilik" metadata model ini (cuma
bookkeeping XML-ID, tidak mempengaruhi kelas Python yang benar-benar jalan).
**Dampak:** Sedang — SAAT INI aman secara fungsional karena kedua kelas byte-identik (jadi
"dibuang"-nya kelas `pos_margin_threshold` tidak kelihatan dari luar). TAPI kalau salah satu modul
diupdate independen (mis. `pos_margin_threshold` menambah validasi/field baru di wizard-nya
sendiri tanpa mengubah `sale_margin_threshold`), perubahan itu TIDAK AKAN PERNAH berlaku selama
`sale_margin_threshold` terinstall — silent, tidak ada error, developer bisa mengira fix-nya jalan
padahal kode yang benar-benar jalan adalah versi LAMA dari modul sibling.
**Rekomendasi:** Konsolidasikan wizard ke satu modul dasar (atau modul baru `margin_sale_common`)
yang keduanya depends, ATAU pakai `_inherit` eksplisit dari satu modul ke modul lain (bukan
`_name` ganda) supaya perilaku "yang menang" jadi eksplisit dan predictable, bukan implisit
tergantung urutan install.
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### F-04 — `_register_hook` memutasi membership `group_sale_margin_action` tiap registry reload
**Modul:** `sale_margin_threshold` (baca status install `pos_margin_threshold`)
**Tag:** `[PERLU-KEPUTUSAN]`
**Status:** ✅ Terkonfirmasi arah "kedua modul terinstall" lewat eksekusi (`sale_margin_threshold/tests/test_cross_module.py`, Docker, 2026-07-31) — `group_sale_margin_action.users` benar-benar kosong. Arah "manual override admin ter-revert" (AC-04-02) BELUM diuji (butuh 2 kali reload registry berturut, di luar scope test otomatis session ini — tetap `[HASIL-BACA]` untuk klaim spesifik itu).
**Lokasi:** `sale_margin_threshold/models/product.py:115-131`
**Ref:** BR-05 (sale), AC-04-01/AC-04-02
**Deskripsi:** `ProductProduct._register_hook()` (dipanggil Odoo SETIAP registry model dibangun
ulang — restart worker, install/upgrade modul apapun, bukan cuma saat modul ini diinstall)
menghapus SEMUA user dari `group_sale_margin_action` kalau `pos_margin_threshold` terinstall, atau
menambahkan SEMUA internal user kalau tidak. Ini adalah mekanisme dedup untuk mencegah action
"Update margin sale" tampil dobel dari 2 modul — TAPI diimplementasikan lewat mutasi state
(group membership), bukan lewat kondisi deklaratif (seperti pola `module_pos_margin_threshold`
invisible di view, yang dipakai modul ini sendiri untuk field lain).
**Dampak:** Kalau admin secara manual menambah/menghapus user dari group ini SAAT
`pos_margin_threshold` terinstall, perubahan itu kemungkinan besar ter-revert diam-diam di reload
registry berikutnya (restart server, install modul apapun) — tanpa notifikasi/log apapun ke admin.
Belum diverifikasi lewat eksekusi nyata seberapa sering `_register_hook` benar-benar terpanggil
dalam operasional normal (perlu Step 04).
**Rekomendasi:** Pertimbangkan ganti mekanisme dedup jadi kondisi deklaratif di action/view (mis.
domain/groups yang dievaluasi at-read-time berdasar `ir.module.module` state, bukan mutasi
persisten group membership).
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### F-05 — `action_confirm` override asumsi singleton, memecah batch-confirm Odoo core
**Modul:** `sale_margin_threshold`
**Tag:** `[PERLU-KEPUTUSAN]`
**Prioritas:** **Tinggi**
**Status:** ✅✅ **Terkonfirmasi GANDA lewat eksekusi nyata (Docker, 2026-07-31)** — (1) test sendiri
(`tests/test_action_confirm.py::test_action_confirm_BATCH_MULTI_ORDER_F05`) berhasil mereproduksi
`ValueError: Expected singleton: sale.order(25, 26)` persis seperti diduga; (2) **DITEMUKAN TIDAK
SENGAJA saat modul diinstall** — demo data BAWAAN Odoo core sendiri (`sale_stock/data/sale_order_demo.xml`)
memanggil `action_confirm()` pada 4 sale order sekaligus (`sale_order_19..22`) dan CRASH dengan
error identik (`ValueError: Expected singleton: sale.order(21, 22, 23, 24)`), tercatat di
`odoo.log` sebagai `Module sale_stock demo data failed to install, installed without demo data`.
Bug ini nyata di alur yang genuinely dipakai Odoo sendiri, bukan cuma skenario buatan test.
**Lokasi:** `sale_margin_threshold/models/sale_order.py:19-27` (baca `self.is_rental_order_installed_true`
baris 21, panggil `self.check_product_price()` yang membaca `self.order_line` di baris 66-68)
**Ref:** BR-01/BR-02 (spec sale), AC-02-01
**Deskripsi:** Ini adalah hasil cek WAJIB Step 01 "tabrakan nama method dengan Odoo core" —
`action_confirm` PERSIS sama nama dengan method core `sale.order.action_confirm`. Override ini
BERBEDA dari pola bug referensi di `USAGE_GUIDE.md` (yang silent-replace total tanpa `super()`) —
di sini `super(SaleOrder, self).action_confirm()` TETAP dipanggil di jalur fallthrough, jadi
logic core TIDAK hilang untuk single-record confirm. Bug-nya di tempat lain: baris `self.is_rental_order_installed_true`
dan `self.order_line` (via `check_product_price`) dibaca LANGSUNG tanpa `for order in self:` —
mengasumsikan `self` selalu berisi SATU record. Odoo core `action_confirm` didesain mendukung
CONFIRM BATCH (pilih beberapa quotation di list view, klik Confirm sekali untuk semua). Membaca
field non-relasional pada recordset multi-record di Odoo me-raise `ValueError: Expected
singleton: sale.order(id1, id2, ...)`.
**Dampak:** TINGGI, TERKONFIRMASI (bukan lagi hipotesis) — batch-confirm quotation (fitur native
Odoo, dipakai bahkan oleh demo data resmi Odoo core sendiri) akan GAGAL TOTAL untuk SEMUA order
yang dipilih begitu modul ini terinstall, bukan cuma order yang harganya bermasalah. Karena instalasi
modul TETAP "berhasil" (Odoo menangkap kegagalan demo data sebagai WARNING, bukan fatal), admin
yang menginstall modul ini TIDAK akan sadar ada masalah sampai benar-benar mencoba batch-confirm
di produksi.
**Rekomendasi:** Wrap logic validasi dalam `for order in self:`, kumpulkan hasil per-order, baru
panggil `super().action_confirm()` sekali di akhir (atau per-order sesuai kebutuhan bisnis).
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### F-06 — `onClickPin` JS menimpa total (bukan extend) patch core `discuss/message_pin`
**Modul:** `pin_message`
**Tag:** `[PERLU-KEPUTUSAN]`
**Lokasi:** `pin_message/static/src/js/message.js:11-26`; dibandingkan dengan
`odoo/addons/mail/static/src/discuss/message_pin/common/message_patch.js:14-26` (Odoo 17 core)
**Ref:** BR-02 (spec pin_message), AC-03-01
**Deskripsi:** Odoo core SUDAH mem-patch `Message.prototype.onClickPin` (untuk fitur native pin di
Discuss channel). Modul `pin_message` JUGA mem-patch method dengan nama sama, TAPI TIDAK memanggil
`super.onClickPin()` — override total, bukan extend. Sudah dikonfirmasi (baca source core) bahwa
untuk jalur `is_discussion=True`, logic yang ditulis ulang modul ini (`messagePinService.pin()`/
`.unpin()`) SAAT INI identik dengan yang dilakukan core, jadi perilaku pengguna TIDAK berubah.
**Dampak:** Sedang (bukan bug aktif, tapi risiko laten) — kalau versi Odoo mendatang mengubah
`onClickPin` core (mis. menambah analytics, guard baru, atau logic tambahan sebelum
pin/unpin), perubahan itu TIDAK akan pernah sampai ke user modul ini, karena override-nya
menimpa total bukan extend. Silent divergence, tidak akan muncul sebagai error yang jelas.
**Rekomendasi:** Ubah jadi `super.onClickPin()` di cabang `is_discussion=True` (delegasikan penuh
ke core), sisakan custom logic HANYA untuk cabang chatter/log note (yang core tidak punya sama
sekali). Tidak mengubah perilaku user saat ini, tapi menghilangkan risiko silent-drift ke depan.
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### F-07 — `console.log` debug tertinggal di kode produksi
**Modul:** `pin_message`
**Tag:** `[HASIL-BACA]`
**Prioritas:** Rendah
**Lokasi:** `pin_message/static/src/js/pinMessage.js:7`
**Ref:** BR-03 (spec pin_message)
**Deskripsi:** `console.log(component.message.type)` di dalam callback `condition` registry message
actions — dieksekusi setiap kali menu aksi pesan dirender (potensial sangat sering, tiap pesan di
chatter/thread). Jelas debug statement yang lupa dihapus (bukan logging terstruktur, tidak ada
guard dev-mode).
**Dampak:** Rendah — cuma noise di browser console, tidak mempengaruhi fungsionalitas.
**Rekomendasi:** Hapus baris ini (perbaikan kode di luar scope BACKFILL — dicatat untuk pemilik
modul, tidak dieksekusi otomatis oleh proses ini).
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

## Limitasi Tool (kalau ada)

- **Update 2026-07-31 setelah Step 04 dijalankan (Mode C, Docker, 3× iterasi):** F-01, F-02, F-03,
  F-04 (arah "kedua modul terinstall"), dan F-05 SEMUA sudah dieksekusi nyata (`TransactionCase`
  via `odoo-bin --test-enable` di container Odoo 17 + Postgres 15, 17 test case, hasil akhir
  `0 failed, 0 error(s)` setelah 2 bug DI TEST SAYA SENDIRI diperbaiki — lihat riwayat revisi F-01).
  Detail lengkap tiap modul di `test/{modul}/04A_DEV_TESTING.md`.
- F-06 (pin_message, `onClickPin` JS) dan F-07 (`console.log`) **TETAP desk-review saja** — QUnit/Hoot
  butuh Chrome headless (Mode E) yang belum di-setup sesi ini (fokus Step 04 diarahkan ke bug Python
  yang lebih berisiko dulu, F-05 khususnya). Kandidat Step 07 (Tour/AI-Browser) kalau environment
  browser tersedia.
- F-01 arah ASLI (delegasi `minimum_sale_price_with_tax` untuk variant yang margin-nya BERBEDA)
  TIDAK BISA diverifikasi seperti rencana awal — bukan karena environment tidak tersedia, tapi
  karena precondition-nya (variant dengan margin berbeda) TERBUKTI MUSTAHIL dicapai sama sekali
  (lihat F-01 revisi). Ini bukan limitasi tool — ini temuan itu sendiri.
