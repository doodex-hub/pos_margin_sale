# Findings — pos_margin_threshold / sale_margin_threshold / pin_message (migrasi 18.0 → 19.0)

> **Cross-cutting, direkomendasikan (tidak kondisional)** — dokumen konsolidasi TUNGGAL untuk semua
> gap/bug/ambiguitas yang butuh keputusan manusia selama migrasi, supaya user tidak perlu buka
> `01b_BASELINE_SPEC.md`/`03_MIGRATION_SPEC.md`/`04_SPEC_COMPLETENESS_REVIEW.md`/`08_CODE_REVIEW.md`
> satu per satu untuk tahu apa yang masih terbuka. Hidup di root `doc/` (sejajar `PROMPT_LOG.md`) —
> bukan milik satu step tertentu. Lihat `migration-tool/templates/FINDINGS.md` untuk penjelasan
> lengkap beda peran dari `ESCALATION`/`[GAP]`/section Gap per-dokumen.

**Modul:** `pos_margin_threshold`, `sale_margin_threshold`, `pin_message` (tiga addon independen —
lihat §"Adaptasi multi-modul" di `CLAUDE.md`, sama seperti project migrasi 17.0→18.0 sebelumnya di
repo ini).
**Migrasi:** 18.0 → 19.0
**Terakhir update:** 2026-08-26 (Step 2 — Diff & Compatibility Analysis selesai untuk ketiga modul).
MF-01..MF-10 adalah quirk/bug WARISAN dari project migrasi 17.0→18.0 sebelumnya (ID baru, dokumen
self-contained) — lihat kolom "Ref asal" untuk ketertelusuran ke
`doc-dev/migration_17.0_18.0/doc/FINDINGS.md`. **MF-12..MF-15 adalah gap BARU yang genuinely muncul
dari perubahan platform 19.0** (ditemukan Step 2, `[GAP-MIGRASI]`) — dua di antaranya
(`MF-14`/`MF-15`, `pin_message`) install/runtime-blocking dengan blast radius melampaui modul itu
sendiri.

Prefix judul finding dengan nama modul (`MF-01 [sale_margin_threshold]`, dst) supaya tetap bisa
dipilah pemilik modul saat review batch (konsisten pola `FINDINGS.md` project 17.0→18.0 di
`migration/18.0`).

---

## Ringkasan

| ID | Judul | Ditemukan di Step | Tag | Prioritas | Status |
|---|---|---|---|---|---|
| MF-01 [pos_margin_threshold] | `margin_sale` per-variant tidak pernah bisa divergen dari template | 1 (carry-forward) | `[DIWARISI-SOURCE]` | Sedang | Open |
| MF-02 [pos_margin_threshold] | `blocking_transaction_order` dideklarasikan tapi tidak dibaca modul ini | 1 (carry-forward) | `[DIWARISI-SOURCE]` | Rendah | Open |
| MF-03 [pos_margin_threshold][sale_margin_threshold] | Kolisi `_name` `wizard.margin.product` — `sale_margin_threshold` selalu menang MRO | 1 (carry-forward) | `[DIWARISI-SOURCE][PERLU-KEPUTUSAN]` | Sedang | Open |
| MF-04 [pos_margin_threshold] | `views/product_template_views.xml` dead file, duplikat XML-ID | 1 (carry-forward) | `[DIWARISI-SOURCE]` | Rendah | Open |
| MF-05 [sale_margin_threshold] | Duplikat XML-ID `product_template_inherit_sale_margin_threshold`, KEDUA file dimuat, satu menimpa yang lain | 1 (carry-forward) | `[DIWARISI-SOURCE]` | Sedang | Open |
| MF-06 [sale_margin_threshold] | Manifest `assets._assets_sale` menunjuk folder `static/src/` yang tidak ada | 1 (carry-forward) | `[DIWARISI-SOURCE]` | Rendah | Open |
| MF-07 [sale_margin_threshold] | `_register_hook()` memutasi grup `group_sale_margin_action` setiap registry rebuild | 1 (carry-forward) | `[DIWARISI-SOURCE]` | Sedang | Open |
| MF-08 [sale_margin_threshold] | `action_confirm()` mengasumsikan `self` singleton — pecah di batch-confirm | 1 (carry-forward) | `[DIWARISI-SOURCE][PERLU-KEPUTUSAN]` | **Tinggi** | Open |
| MF-09 [pin_message] | Cabang `is_discussion` di `onClickPin()` dead code, dikonfirmasi harmless | 1 (carry-forward) | `[DIWARISI-SOURCE]` | Rendah | Open (accepted) |
| MF-10 [pin_message] | `console.log(component.message.type)` debug leftover di `pinMessage.js:7` | 1 (carry-forward) | `[DIWARISI-SOURCE][PERLU-KEPUTUSAN]` | Rendah | Open |
| MF-11 [sale_margin_threshold] | `sale.order.line.tax_id`→`tax_ids` (knowledge base 18→19) — dikonfirmasi TIDAK relevan | 1 | `[GAP-MIGRASI]` (verdict: N/A) | — | ✅ CONFIRMED N/A |
| MF-12 [pos_margin_threshold] | `Orderline.props.line.shape` dihapus total di 19.0 — patch akan crash saat load | 2 | `[GAP-MIGRASI]` | **Kritis** | Open |
| MF-13 [pos_margin_threshold] | `getDisplayData()` dihapus + rename massal snake_case→camelCase (`get_order`, `get_product`, dst) — `pay()` override akan crash saat dipanggil | 2 | `[GAP-MIGRASI]` | **Kritis** | Open |
| MF-14 [pin_message] | `mail.message._to_store()` — `fields` jadi positional wajib, override modul akan `TypeError` di SETIAP pengiriman pesan ke frontend | 2 | `[GAP-MIGRASI]` | **Kritis** | Open |
| MF-15 [pin_message] | `messageActionsRegistry` payload shape berubah total (`title`→`name`, `onClick`→`onSelected`, argumen jadi objek tanpa `.props`) | 2 | `[GAP-MIGRASI]` | **Kritis** | Open |
| MF-16 [sale_margin_threshold] | `ir.actions.server.groups_id`→`group_ids` — ditemukan lewat G1 (bukan Step 2), install-blocking | 6 (G1) | `[GAP-MIGRASI]` | Tinggi | ✅ RESOLVED (2026-08-27) |
| MF-17 [sale_margin_threshold] | `res.groups.users`→`user_ids` — ditemukan lewat G1 (bukan Step 2), install-blocking | 6 (G1) | `[GAP-MIGRASI]` | Tinggi | ✅ RESOLVED (2026-08-27) |

---

## Kandidat finding dari knowledge base (status setelah verifikasi Step 1)

`migration-tool/knowledge/version-diffs/18-to-19.md` dan
`migration-tool/knowledge/dependency-compat/sale_report/18-to-19.md` (dari project 18.0→19.0 pertama
lewat tool ini, `advanced_sales_analysis`):

- **`sale.order.line.tax_id` → `tax_ids` (rename, breaking).** **Diverifikasi di Step 1 (2026-08-26,
  research agent, grep penuh Python/XML/JS `sale_margin_threshold`): TIDAK ADA referensi sama sekali**
  ke `tax_id` pada `sale.order.line` di modul manapun di project ini. Satu-satunya `tax*` field yang
  disentuh adalah `product.template.taxes_id` (field berbeda, tidak terdampak rename ini). Lihat
  `MF-11` di tabel Ringkasan — dicatat CONFIRMED N/A, tidak perlu dicek ulang di Step 2 lagi kecuali
  kode berubah.
- Model `sale.report`/`sale.order.line` lain (`_select_additional_fields()`, `_group_by_sale()`)
  dikonfirmasi byte-stable 18.0↔19.0 di project `advanced_sales_analysis` — tidak dipakai modul
  manapun di project ini secara langsung, jadi tidak relevan di sini.

---

## Detail

### MF-01 [pos_margin_threshold] — `margin_sale` per-variant tidak pernah bisa divergen dari template
**Ditemukan di:** Step 1 (2026-08-26), carry-forward dari `doc-dev/migration_17.0_18.0/doc/FINDINGS.md` `MF-01`.
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `01b_BASELINE_SPEC.md` `pos_margin_threshold` `BSL-010`; asal `17-18/MF-01`.
**Lokasi:** `pos_margin_threshold/models/product.py` — inverse `margin_sale` di `product.product`.
**Deskripsi:** Inverse `margin_sale` di level variant menulis balik ke `product_tmpl_id` (template
bersama), bukan ke variant itu sendiri — field yang kelihatan per-variant di UI selalu tersinkron
paksa ke template.
**Dampak:** Tidak ada — ini desain yang sudah berjalan sejak 17.0, bukan gap migrasi.
**Rekomendasi:** Pertahankan identik di 19.0.
**Keputusan pemilik modul:** *(kosong — diisi manusia, kecuali user ingin memperbaikinya sekalian di
project ini)*

### MF-02 [pos_margin_threshold] — `blocking_transaction_order` dideklarasikan tapi tidak dibaca
**Ditemukan di:** Step 1 (2026-08-26), carry-forward `17-18/MF-02`.
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `01b_BASELINE_SPEC.md` `pos_margin_threshold` `BSL-017`.
**Lokasi:** `pos_margin_threshold/models/res_config_settings.py`.
**Deskripsi:** Field ada di `res.config.settings` modul ini tapi hanya bermakna kalau
`sale_margin_threshold` juga terinstall.
**Dampak:** Tidak ada — field "kelihatan aktif" di UI tapi efeknya nol tanpa modul sibling.
**Keputusan pemilik modul:** *(kosong)*

### MF-03 [pos_margin_threshold][sale_margin_threshold] — Kolisi `_name` `wizard.margin.product`
**Ditemukan di:** Step 1 (2026-08-26), carry-forward `17-18/MF-03`, dikonfirmasi empiris Step 9
project 17→18 (2026-08-26 sesi itu): dites DUA urutan install, hasil identik — `sale_margin_threshold`
SELALU menang MRO, independen urutan.
**Tag:** `[DIWARISI-SOURCE][PERLU-KEPUTUSAN]`
**Ref:** `01b_BASELINE_SPEC.md` `pos_margin_threshold` `BSL-016`, `sale_margin_threshold` `BSL-014`.
**Lokasi:** `pos_margin_threshold/wizard/wizard_margin_product.py`,
`sale_margin_threshold/wizard/wizard_margin_product.py`.
**Deskripsi:** Kedua modul mendefinisikan model `wizard.margin.product` dengan `_name` (bukan
`_inherit`), byte-identik. Kalau keduanya terinstall, class `pos_margin_threshold` hilang total dari
`__mro__`.
**Dampak:** Risiko silent-override kalau salah satu wizard diubah sendirian tanpa sinkron ke yang
lain — modul yang "kalah" MRO efektif kehilangan wizard-nya sendiri tanpa error apapun.
**Rekomendasi:** Pertahankan seperti sekarang (dua definisi identik, sinkron manual), atau
konsolidasi jadi satu model `_inherit` bersama — butuh keputusan eksplisit user, bukan keputusan AI
sepihak (mengubah struktur model termasuk larangan default "rename model kecuali wajib").
**Keputusan pemilik modul:** *(kosong)*

### MF-04 [pos_margin_threshold] — `views/product_template_views.xml` dead file, duplikat XML-ID
**Ditemukan di:** Step 1 (2026-08-26), carry-forward `17-18/MF-04`.
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `01b_BASELINE_SPEC.md` `pos_margin_threshold` `BSL-018`.
**Lokasi:** `pos_margin_threshold/views/product_template_views.xml` (tidak di manifest `data:`).
**Deskripsi:** File ada di disk, sengaja tidak dimuat, duplikat XML-ID dengan record aktif di
`views/products.xml` (target `inherit_id` beda).
**Dampak:** Tidak ada selama file ini tetap tidak dimuat.
**Keputusan pemilik modul:** *(kosong)*

### MF-05 [sale_margin_threshold] — Duplikat XML-ID, KEDUA file dimuat, satu menimpa yang lain
**Ditemukan di:** Step 1 (2026-08-26), carry-forward `17-18/MF-07`.
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `01b_BASELINE_SPEC.md` `sale_margin_threshold` `BSL-012`.
**Lokasi:** `sale_margin_threshold/views/product_template_views.xml` DAN `views/products.xml` —
keduanya di manifest `data:`, XML-ID sama `product_template_inherit_sale_margin_threshold`.
**Deskripsi:** Beda dari `MF-04` — di sini KEDUA file dimuat, record yang dimuat kedua (`products.xml`)
menimpa total record pertama termasuk `inherit_id`-nya, jadi kustomisasi ke
`product.product_template_only_form_view` tidak pernah aktif.
**Dampak:** Sedang — tidak ada error, tapi satu maksud kustomisasi silently tidak berfungsi.
**Rekomendasi:** Klarifikasi ke user apakah `product.product_template_only_form_view` memang
seharusnya tidak dikustomisasi (kalau ya, hapus file `product_template_views.xml` dari `data:`,
setara `MF-04`), atau memang harus aktif (kalau ya, ganti salah satu XML-ID).
**Keputusan pemilik modul:** *(kosong)*

### MF-06 [sale_margin_threshold] — Manifest asset menunjuk folder yang tidak ada
**Ditemukan di:** Step 1 (2026-08-26), carry-forward `17-18/MF-08`.
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `01b_BASELINE_SPEC.md` `sale_margin_threshold` `BSL-013`.
**Lokasi:** `sale_margin_threshold/__manifest__.py` (`assets.sale_margin_threshold._assets_sale`).
**Deskripsi:** Menunjuk `static/src/**/*`, folder itu tidak ada di disk — glob kosong, tidak error.
**Dampak:** Tidak ada, cruft murni.
**Rekomendasi:** Bisa dibersihkan (hapus baris manifest) sebagai housekeeping trivial, atau
dipertahankan — risiko sama-sama nol.
**Keputusan pemilik modul:** *(kosong)*

### MF-07 [sale_margin_threshold] — `_register_hook()` memutasi grup setiap registry rebuild
**Ditemukan di:** Step 1 (2026-08-26), carry-forward `17-18/MF-05`.
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `01b_BASELINE_SPEC.md` `sale_margin_threshold` `BSL-010`.
**Lokasi:** `sale_margin_threshold/models/product.py` (`ProductProduct._register_hook`).
**Deskripsi:** Setiap registry rebuild (bukan hanya install), membership `group_sale_margin_action`
di-reset paksa berdasarkan apakah `pos_margin_threshold` terinstall.
**Dampak:** Perubahan manual admin ke membership grup ini bisa ter-reset diam-diam.
**Keputusan pemilik modul:** *(kosong)*

### MF-08 [sale_margin_threshold] — `action_confirm()` mengasumsikan singleton, pecah di batch-confirm
**Ditemukan di:** Step 1 (2026-08-26), carry-forward `17-18/MF-06`, prioritas **Tinggi**, masih
terbuka sejak sebelum project 17→18.
**Tag:** `[DIWARISI-SOURCE][PERLU-KEPUTUSAN]`
**Ref:** `01b_BASELINE_SPEC.md` `sale_margin_threshold` `BSL-009`.
**Lokasi:** `sale_margin_threshold/models/sale_order.py` (`action_confirm`, baca `self.order_line`/
`self.is_rental_order_installed_true` tanpa `for order in self:`).
**Deskripsi:** Kalau Odoo core memanggil override ini untuk batch (multi-record) confirm, logic hanya
mengevaluasi record pertama di `self`.
**Dampak:** **Tinggi** — kesalahan validasi margin senyap untuk order ke-2 dst dalam satu batch
confirm, kalau skenario itu pernah terjadi di produksi.
**Rekomendasi:** Perbaiki (`for order in self:`) atau pertahankan identik — butuh keputusan eksplisit
user karena ini bug prioritas tinggi, bukan quirk kosmetik.
**Keputusan pemilik modul:** *(kosong — BLOCKING keputusan sebelum Step 3/6 modul ini)*

### MF-09 [pin_message] — Cabang `is_discussion` di `onClickPin()` dead code
**Ditemukan di:** Step 1 (2026-08-26), carry-forward `17-18/MF-09`, dikonfirmasi harmless Step 8
project 17→18.
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `01b_BASELINE_SPEC.md` `pin_message` `BSL-002`.
**Lokasi:** `pin_message/static/src/js/message.js` (`onClickPin`).
**Deskripsi:** Cabang ini didelegasikan ke `this.messagePinService` implisit, tidak pernah benar-
benar terpanggil di 18.0 (native Discuss pin lewat mekanisme lain).
**Dampak:** Tidak ada untuk end-user. Risiko laten: kalau mekanisme injeksi `messagePinService`
hilang di 19.0, baris ini akan error HANYA JIKA cabang ini pernah hidup kembali (saat ini tidak).
**Keputusan pemilik modul:** *(kosong — accepted, tidak butuh aksi)*

### MF-10 [pin_message] — `console.log` debug leftover
**Ditemukan di:** Step 1 (2026-08-26), carry-forward `17-18/MF-10`, **masih terbuka/belum diperbaiki**
sejak project 17→18.
**Tag:** `[DIWARISI-SOURCE][PERLU-KEPUTUSAN]`
**Ref:** `01b_BASELINE_SPEC.md` `pin_message` `BSL-009`.
**Lokasi:** `pin_message/static/src/js/pinMessage.js:7`.
**Deskripsi:** `console.log(component.message.type)` jalan setiap render action-menu pesan MANAPUN
di seluruh sistem (bukan hanya pesan yang lolos kondisi pin).
**Dampak:** Rendah — noise console browser, tidak fungsional.
**Rekomendasi:** Housekeeping trivial (hapus baris), atau pertahankan konsisten prinsip "jangan
perbaiki bug lama tanpa izin" — butuh keputusan eksplisit user karena walau kecil, ini tetap
perubahan kode di luar scope port.
**Keputusan pemilik modul:** *(kosong)*

### MF-11 [sale_margin_threshold] — `sale.order.line.tax_id`→`tax_ids` — dikonfirmasi N/A
**Ditemukan di:** Step 1 (2026-08-26).
**Tag:** `[GAP-MIGRASI]` (verdict setelah verifikasi: tidak berlaku)
**Ref:** `migration-tool/knowledge/version-diffs/18-to-19.md`.
**Lokasi:** N/A — dicek seluruh Python/XML/JS `sale_margin_threshold`, nihil match.
**Deskripsi:** Breaking rename Odoo 19.0 `sale.order.line.tax_id`→`tax_ids` yang dicatat di knowledge
base project migrasi 18→19 lain (`advanced_sales_analysis`) TIDAK relevan untuk modul ini — tidak
ada referensi ke field ini sama sekali.
**Dampak:** Tidak ada.
**Status:** ✅ CONFIRMED N/A (2026-08-26) — tidak perlu dicek ulang di Step 2 kecuali kode berubah.

### MF-16 [sale_margin_threshold] — `ir.actions.server.groups_id` → `group_ids`
**Ditemukan di:** Step 6, G1 percobaan #1 (2026-08-27) — **TIDAK ketahuan di Step 2/3/4** (riset Step
2 fokus ke `point_of_sale`/`mail`/`sale`, tidak mencakup `base`/`ir.actions` untuk modul ini).
**Tag:** `[GAP-MIGRASI]`
**Ref:** `06_implementation/sale_margin_threshold/06c_IMPLEMENTATION_LOG.md` Fase C1, "Riwayat
Percobaan G1" #1.
**Lokasi:** `sale_margin_threshold/views/products.xml:74,85` (`product_template_margin_sale_action_server`,
`product_product_margin_sale_action_server`).
**Deskripsi:** Core 19.0 me-rename field `ir.actions.server.groups_id` (dan `ir.actions.act_window.groups_id`)
jadi `group_ids` (`odoo/addons/base/models/ir_actions.py`). Menyebabkan `ValueError: Invalid field
'groups_id' in 'ir.actions.server'` — instalasi gagal total (`ParseError`).
**Dampak:** Kritis sebelum fix — install-blocking. Setelah fix: tidak ada dampak, nilai tidak berubah.
**Status:** ✅ RESOLVED (2026-08-27) — rename mekanis, divalidasi G1 percobaan #3 PASS.

### MF-17 [sale_margin_threshold] — `res.groups.users` → `user_ids`
**Ditemukan di:** Step 6, G1 percobaan #2 (2026-08-27) — TIDAK ketahuan di Step 2/3/4, sama alasannya
seperti `MF-16`.
**Tag:** `[GAP-MIGRASI]`
**Ref:** `06_implementation/sale_margin_threshold/06c_IMPLEMENTATION_LOG.md` Fase A5, "Riwayat
Percobaan G1" #2.
**Lokasi:** `sale_margin_threshold/models/product.py:128,130,131` (`_register_hook`),
`sale_margin_threshold/tests/test_cross_module.py:31,33`.
**Deskripsi:** Core 19.0 me-rename field `res.groups.users` jadi `user_ids` (relation table sama,
`res_groups_users_rel`) — `odoo/addons/base/models/res_groups.py`. Menyebabkan `AttributeError:
'res.groups' object has no attribute 'users'` — registry gagal dibangun, instalasi gagal total.
**Dampak:** Kritis sebelum fix. Setelah fix: tidak ada dampak, logic tidak berubah.
**Status:** ✅ RESOLVED (2026-08-27) — rename mekanis, divalidasi G1 percobaan #3 PASS.

### MF-12 [pos_margin_threshold] — `Orderline.props.line.shape` dihapus total di 19.0
**Ditemukan di:** Step 2 (2026-08-26), agent riset diff-analysis, cross-check langsung `odoo18` vs `enterprise19.0`.
**Tag:** `[GAP-MIGRASI]`
**Ref:** `02_diff/pos_margin_threshold/02_DIFF_ANALYSIS.md` `DIFF-06`.
**Lokasi:** `pos_margin_threshold/static/src/store/models/models.js:12-16`
(`patch(Orderline.props.line.shape, {...})`).
**Deskripsi:** Di 19.0, `Orderline.props.line` didefinisikan sebagai `Object` polos — tidak ada
`.shape` sama sekali (component sekarang menerima record model langsung, bukan objek display-data).
`patch()` terhadap `undefined` akan throw.
**Dampak:** **Kritis** — modul akan crash saat load fitur JS POS di 19.0, bukan cuma silent-fail.
**Rekomendasi:** Di Step 6, hapus patch ini; tambahkan getter (`isLessMinimumSalePrice`,
`minimumSalePriceWithTax`) langsung di `PosOrderline`/`PosOrderlineAccounting` sehingga template
`Orderline` 19.0 bisa membacanya lewat `line.<getter>`.
**Keputusan pemilik modul:** *(kosong — bukan pilihan opsional, harus diperbaiki agar modul bisa
jalan; keputusan yang perlu user adalah APAKAH pendekatan porting di atas disetujui saat Step 3/6)*

### MF-13 [pos_margin_threshold] — `getDisplayData()` dihapus + rename massal snake_case→camelCase
**Ditemukan di:** Step 2 (2026-08-26).
**Tag:** `[GAP-MIGRASI]`
**Ref:** `02_diff/pos_margin_threshold/02_DIFF_ANALYSIS.md` `DIFF-07`, `DIFF-08`, `DIFF-09`.
**Lokasi:** `pos_margin_threshold/static/src/store/models/models.js:35-43` (patch `getDisplayData()`),
`pos_margin_threshold/static/src/store/pos_store.js:12-15` (`get_order`, `get_orderlines`,
`get_unit_display_price`, `get_product`).
**Deskripsi:** `PosOrderline.prototype.getDisplayData()` tidak ada lagi di manapun di addon 19.0
(grep penuh: 0 match) — patch modul ini jadi no-op total. Terpisah, method core yang dipanggil
`pay()` override modul (`get_order`, `get_orderlines`, `get_product`) di-rename massal jadi
camelCase di 19.0; `get_unit_display_price` khususnya tidak punya pengganti nama persis (logic
pindah ke getter `displayPriceUnit`/`currencyDisplayPriceUnit` di base class baru
`PosOrderlineAccounting`).
**Dampak:** **Kritis** — fitur inti (highlight/blokir harga di bawah minimum saat bayar) akan
crash (`pay()` override) DAN fitur highlight visual jadi non-fungsional senyap (`getDisplayData()`).
**Rekomendasi:** Step 6 wajib porting: rename seluruh pemanggilan method core jadi camelCase, cari
pengganti `get_unit_display_price` di base class accounting baru, pindahkan logic `getDisplayData()`
jadi getter langsung di `PosOrderline`.
**Keputusan pemilik modul:** *(kosong)*

### MF-14 [pin_message] — `mail.message._to_store()` signature berubah, blast radius luas
**Ditemukan di:** Step 2 (2026-08-26).
**Tag:** `[GAP-MIGRASI]`
**Ref:** `02_diff/pin_message/02_DIFF_ANALYSIS.md` `DIFF-01`.
**Lokasi:** `pin_message/models/mail_message.py:22` (`def _to_store(self, store, /, **kwargs)`).
**Deskripsi:** Di 19.0, `_to_store()` core menambah parameter `fields` sebagai POSITIONAL WAJIB
(bukan lagi keyword-only opsional). Override modul ini (`store, /, **kwargs`, tidak ada slot untuk
argumen positional kedua) akan `TypeError` setiap kali `store.add(<mail.message>, ...)` dipanggil
DI MANAPUN di sistem (chatter, Discuss, notifikasi apapun) — bukan cuma jalur yang disentuh modul
ini sendiri.
**Dampak:** **Kritis, blast radius terluas di seluruh project** — bisa mematahkan pengiriman pesan
ke frontend secara umum, tidak terbatas ke fitur pin.
**Rekomendasi:** Step 6 wajib ubah signature jadi
`def _to_store(self, store, fields, /, **kwargs): super()._to_store(store, fields, **kwargs)`
(atau bentuk yang cocok persis dengan signature 19.0).
**Keputusan pemilik modul:** *(kosong — perbaikan ini wajib, bukan opsional, supaya modul bisa
terinstall sama sekali di 19.0)*

### MF-15 [pin_message] — `messageActionsRegistry` payload shape berubah total
**Ditemukan di:** Step 2 (2026-08-26).
**Tag:** `[GAP-MIGRASI]`
**Ref:** `02_diff/pin_message/02_DIFF_ANALYSIS.md` `DIFF-02`.
**Lokasi:** `pin_message/static/src/js/pinMessage.js:5-26`.
**Deskripsi:** 19.0 me-rename `title`→`name`, `onClick`→`onSelected`, dan mengubah argumen callback
dari instance component Owl asli jadi objek polos `{action, store, owner, message, thread}` — TIDAK
ADA `.props`. `condition` modul ini (`component.message.canAddReaction(component.props.thread)`)
akan throw karena `component.props` sekarang `undefined`, di getter reactive yang dievaluasi untuk
SETIAP pesan yang di-render (potensi mematahkan action-menu pesan secara luas).
**Dampak:** **Kritis.**
**Rekomendasi:** Step 6: rewrite sesuai pola native 19.0
(`mail/static/src/discuss/message_pin/common/message_actions.js` — `registerMessageAction`, key
`name`/`onSelected`, destructure `{message, thread}` bukan `component`).
**Keputusan pemilik modul:** *(kosong — wajib diperbaiki)*

---

## Cara Pakai

1. **Update SETIAP KALI step manapun (1-11), modul manapun, menemukan gap/bug/ambiguitas yang butuh
   keputusan manusia** — jangan tunggu sampai akhir project.
2. ID `MF-NNN` sequential lintas ketiga modul (satu skema penomoran, prefix modul di judul).
3. Tag: `[PERLU-KEPUTUSAN]` / `[DIWARISI-SOURCE]` (bug/quirk yang sudah ada di 18.0, harus
   dipertahankan identik) / `[GAP-MIGRASI]` (genuinely muncul karena perubahan platform 19.0).
4. Step 4 dan Step 8 (per modul) WAJIB baca file ini sebagai bagian gate.
5. Update status (bukan hapus) begitu keputusan diambil/finding resolved — histori tetap terbaca.
