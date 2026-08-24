# Findings — pos-margin-sale (migrasi 17.0 → 18.0, multi-module)

> **Cross-cutting, direkomendasikan (tidak kondisional)** — dokumen konsolidasi TUNGGAL untuk semua
> gap/bug/ambiguitas yang butuh keputusan manusia selama migrasi, untuk KETIGA modul
> (`pos_margin_threshold`, `sale_margin_threshold`, `pin_message`) — lihat adaptasi multi-modul di
> `CLAUDE.md` root. Diadaptasi dari `migration-tool/templates/FINDINGS.md`.

**Modul:** `pos_margin_threshold`, `sale_margin_threshold`, `pin_message` (satu file, prefix modul di
tiap judul finding)
**Migrasi:** 17.0 → 18.0
**Terakhir update:** 2026-08-24 (Step 6, Mode D — `pos_margin_threshold` POS data-model architecture
overhaul ditemukan+diperbaiki+diverifikasi tour test nyata; total 20 finding, 9 diwarisi backfill)

---

## Beda Peran dari Mekanisme Lain (jangan bingung/duplikat)

| Mekanisme | Kapan dipakai | Sifat |
|---|---|---|
| Format `ESCALATION` (`CLAUDE.md`) | Isu **blocking** — butuh keputusan user SEBELUM lanjut ke step/fase berikutnya | Sinkron, muncul di respons AI saat itu juga |
| Tag `[GAP]` di `01b_BASELINE_SPEC.md` (per modul) | Penyimpangan spec lama vs kode aktual, per-klaim `BSL-NNN` | Inline, granular per klaim |
| Section Gap di `04_SPEC_COMPLETENESS_REVIEW.md` / `08_CODE_REVIEW.md` (per modul) | Gap spesifik di titik gate itu | Inline, per dokumen |
| **`FINDINGS.md` (file ini)** | **Semua finding lintas step (1-11) DAN lintas modul yang butuh keputusan manusia** — satu tempat, direview batch | Living document, append-only |

**Aturan penomoran:** ID `MF-NNN` (Migration Finding) sequential lintas KETIGA modul (bukan reset
per modul), judul WAJIB diberi prefix modul: `MF-01 [pos_margin_threshold] — ...`.

**Catatan penting — modul ini juga pernah lewat `doc-dev/backfill`:** ketiga modul punya
`doc-dev/backfill/FINDINGS.md` (branch `backfill/17.0`) dengan ID `F-01`..`F-07` miliknya sendiri
(termasuk F-01/F-02 soal interaksi runtime `pos_margin_threshold` ⟷ `sale_margin_threshold`, dan
F-05 soal `sale_margin_threshold.action_confirm` memecah batch-confirm Odoo core). **Cek dulu file
itu sebelum mencatat finding baru** — kalau finding di migrasi ini sebenarnya pewarisan dari F-NNN
backfill, buat `MF-NNN` yang mereferensikan `F-NNN` aslinya secara eksplisit (tag
`[DIWARISI-SOURCE]`), jangan dicatat ulang dari nol.

---

## Ringkasan

| ID | Judul | Modul | Ditemukan di Step | Tag | Prioritas | Status |
|---|---|---|---|---|---|---|
| MF-01 | `margin_sale` per-variant tidak bisa divergen — inverse menulis ke template shared | pos_margin_threshold | 1 | `[DIWARISI-SOURCE]` `[PERLU-KEPUTUSAN]` | Sedang | Terbuka — belum ada keputusan pemilik modul |
| MF-02 | `blocking_transaction_order` dideklarasikan tapi tidak berefek sendirian | pos_margin_threshold | 1 | `[DIWARISI-SOURCE]` `[PERLU-KEPUTUSAN]` | Rendah | Terbuka |
| MF-03 | Model `wizard.margin.product`: kelas `pos_margin_threshold` hilang total dari MRO saat 2 modul terinstall | pos_margin_threshold + sale_margin_threshold | 1 | `[DIWARISI-SOURCE]` `[PERLU-KEPUTUSAN]` | Sedang | Terbuka |
| MF-04 | `views/product_template_views.xml` dead file, duplikat XML-ID dengan `views/products.xml` | pos_margin_threshold | 1 | `[DIWARISI-SOURCE]` | Rendah | Terbuka — baru ditemukan, belum ada di backfill |
| MF-05 | `_register_hook` memutasi membership `group_sale_margin_action` tiap registry reload | sale_margin_threshold (interaksi dgn pos_margin_threshold) | 1 | `[DIWARISI-SOURCE]` `[PERLU-KEPUTUSAN]` | Sedang | Terbuka |
| MF-06 | `action_confirm` override asumsi singleton — memecah batch-confirm Odoo core | sale_margin_threshold | 1 | `[DIWARISI-SOURCE]` `[PERLU-KEPUTUSAN]` | **Tinggi** | Terbuka |
| MF-07 | Duplikasi XML-ID `product_template_inherit_sale_margin_threshold` — KEDUA file dimuat, yang kedua menimpa total yang pertama | sale_margin_threshold | 1 | `[DIWARISI-SOURCE]` | Sedang | Terbuka — baru ditemukan, lebih serius dari MF-04 (di sini file aktif dimuat, bukan dead) |
| MF-08 | Manifest declare `assets._assets_sale` menunjuk folder `static/src/` yang tidak eksis | sale_margin_threshold | 1 | `[DIWARISI-SOURCE]` | Rendah | Terbuka — baru ditemukan |
| MF-09 | `onClickPin` JS menimpa total (bukan extend) patch core `discuss/message_pin` | pin_message | 1 | `[DIWARISI-SOURCE]` `[PERLU-KEPUTUSAN]` | Sedang | Terbuka |
| MF-10 | `console.log` debug tertinggal di `pinMessage.js` | pin_message | 1 | `[DIWARISI-SOURCE]` | Rendah | Terbuka |
| MF-11 | `Orderline.getDisplayData()` full-override (bukan extend `super()`) — pola risiko sama seperti MF-09 | pos_margin_threshold | 2 | `[DIWARISI-SOURCE]` `[PERLU-KEPUTUSAN]` | Sedang-Tinggi | Terbuka — baru ditemukan saat diff analysis |
| MF-12 | `chatter.js` import `@mail/core/web/chatter` — path SUDAH TIDAK ADA di 18.0 | pin_message | 6 | `[GAP-MIGRASI]` | Tinggi | ✅ **RESOLVED** (2026-08-24) — diperbaiki jadi `@mail/chatter/web_portal/chatter`, dikonfirmasi via G2 browser + cross-check source container `odoo:18.0` |
| MF-13 | `ConfirmPopup`/`ErrorPopup` (`@point_of_sale/app/utils/confirm_popup/*`, `@point_of_sale/app/errors/popups/*`) — komponen & service `popup` DIHAPUS TOTAL di 18.0 | pos_margin_threshold | 6 | `[GAP-MIGRASI]` | **Tinggi** | ✅ **RESOLVED** (2026-08-24) — diganti `dialog` service + `ConfirmationDialog`/`AlertDialog`/`ask()` dari `@web/core/confirmation_dialog/confirmation_dialog` + `@point_of_sale/app/store/make_awaitable_dialog`, dikonfirmasi cross-check source container `odoo:18.0` (pola dipakai core POS sendiri) |
| MF-14 | `message_card_list.xml` xpath `//button[...]` — elemen core berubah jadi `<a role="button">` di 18.0, tag selector tidak match | pin_message | 6 | `[GAP-MIGRASI]` | Sedang | ✅ **RESOLVED** (2026-08-24) — xpath diubah jadi `//a[...]`, dikonfirmasi cross-check source container |
| MF-15 | `@point_of_sale/app/store/models` — `Order`/`Orderline`/`Product` classes SUDAH TIDAK ADA (file kosong 0 byte); dipindah ke `@point_of_sale/app/models/*` dengan nama baru | pos_margin_threshold | 6 | `[GAP-MIGRASI]` | **Kritis** | ✅ **RESOLVED** — import diarahkan ke `ProductProduct`/`PosOrderline`/`PosOrder` di path baru |
| MF-16 | `Order.prototype.pay()` — tombol "Pay" TIDAK LAGI memanggilnya sama sekali; entry point pindah ke `PosStore.prototype.pay()` | pos_margin_threshold | 6 | `[GAP-MIGRASI]` | **Kritis** — fitur inti blocking-payment tidak akan pernah jalan tanpa fix ini | ✅ **RESOLVED** — logic blocking dipindah ke patch `PosStore.prototype.pay()` di `pos_store.js` |
| MF-17 | `PosStore.prototype._loadProductProduct()` — hook ini sudah tidak ada di 18.0, patch modul ini jadi dead code total | pos_margin_threshold | 6 | `[GAP-MIGRASI]` | Rendah (dead code, tidak crash) | ✅ **RESOLVED** — patch dihapus, tidak diperlukan lagi (fields.Float() core sudah default 0.0 aman) |
| MF-18 | `pos.session._loader_params_product_product()` — hook dihapus total, diganti `_load_pos_data_fields()` per-model (`product.product`) | pos_margin_threshold | 6 | `[GAP-MIGRASI]` | **Tinggi** — field custom modul tidak akan pernah sampai ke frontend POS tanpa fix ini | ✅ **RESOLVED** — override dipindah ke `ProductProduct._load_pos_data_fields()` di `models/product.py`, override lama di `pos_session.py` dihapus |
| MF-19 | Komponen Owl `Orderline` sekarang validasi ketat `props.line` (shape schema) — field custom yang ditambahkan `getDisplayData()` di-reject sebagai "unknown key" | pos_margin_threshold | 6 | `[GAP-MIGRASI]` | Tinggi (crash render kalau tidak diperbaiki) | ✅ **RESOLVED** — `Orderline.props.line.shape` di-patch untuk mendeklarasikan 3 key baru |
| MF-20 | `orderline.xml` xpath `/ul[hasclass('info-list')]` (direct child) — core 18.0 menambah `<div>` wrapper, xpath direct-child tidak match lagi | pos_margin_threshold | 6 | `[GAP-MIGRASI]` | Tinggi (crash render QWeb) | ✅ **RESOLVED** — xpath diubah jadi descendant (`//ul[...]`) |
| MF-21 | `Environment.lang` (18.0) validasi ketat — `UserError` kalau context `lang=fr_FR` tapi bahasa Prancis tidak diinstall di database | sale_margin_threshold | 6 | `[CATATAN-DEPLOYMENT]` | Sedang | ✅ Bukan bug kode — dikonfirmasi test pass 0 error setelah bahasa Prancis diinstall (`--load-language=fr_FR`). **Perlu dikonfirmasi ke dev:** environment production harus punya bahasa Prancis terinstall, atau `action_confirm()` bilingual EN/FR modul ini akan crash di 18.0 (TIDAK crash di 17.0 — lihat detail) |

---

## Detail

### MF-01 — `margin_sale` per-variant TIDAK BISA divergen — inverse menulis ke template (shared)
**Ditemukan di:** Step 1 (2026-08-24) — diwarisi dari `doc-dev/backfill/FINDINGS.md` **F-01** (branch `backfill/17.0`, terkonfirmasi eksekusi Docker 2026-07-31)
**Tag:** `[DIWARISI-SOURCE]` `[PERLU-KEPUTUSAN]`
**Ref:** `BSL-011` (`01_intake/pos_margin_threshold/01b_BASELINE_SPEC.md`), backfill `F-01`
**Lokasi:** `pos_margin_threshold/models/product.py` (`ProductProduct._set_product_margin_sale`, inverse method)
**Deskripsi:** Field `margin_sale` di `ProductProduct` punya inverse sendiri tapi menulis ke `product_tmpl_id` (template, shared semua variant) — margin TIDAK PERNAH bisa berbeda antar variant satu template, walau field-nya terlihat "milik variant sendiri". Detail lengkap: lihat backfill `F-01`.
**Dampak di 18.0:** Belum diketahui apakah mekanisme compute/inverse Odoo 18.0 berubah caranya bekerja — kalau tidak berubah (kemungkinan besar, ini API `fields.Float` dasar), quirk ini tetap identik. WAJIB dicek ulang di Step 2, jangan diasumsikan otomatis sama.
**Rekomendasi:** Sama seperti backfill — kalau margin per-variant genuinely diinginkan, perlu perubahan bisnis (di luar scope migrasi port-kode-saja). Kalau margin selalu dimaksudkan sama, field ini redundant.
**Keputusan pemilik modul:** *(kosong — diisi manusia, sama dengan status backfill F-01)*

---

### MF-02 — `blocking_transaction_order` dideklarasikan di `pos_margin_threshold` tapi tidak berefek sendirian
**Ditemukan di:** Step 1 (2026-08-24) — diwarisi dari `doc-dev/backfill/FINDINGS.md` **F-02**
**Tag:** `[DIWARISI-SOURCE]` `[PERLU-KEPUTUSAN]`
**Ref:** `BSL-012`, backfill `F-02`
**Lokasi:** `pos_margin_threshold/models/res_config_settings.py:8`
**Deskripsi:** Field dideklarasikan tapi tidak ditampilkan di view settings modul ini dan tidak dibaca kode modul ini — baru bermakna kalau `sale_margin_threshold` juga terinstall.
**Dampak di 18.0:** Rendah, murni dead weight kalau modul ini diinstall sendirian — tidak ada risiko teknis migrasi (field Boolean sederhana, tidak depend API yang berubah).
**Rekomendasi:** Sama seperti backfill — pertimbangkan pindahkan deklarasi ke `sale_margin_threshold` saja, ATAU dokumentasikan eksplisit alasan duplikasi. Di luar scope migrasi port-kode-saja kecuali disetujui eksplisit.
**Keputusan pemilik modul:** *(kosong)*

---

### MF-03 — Model `wizard.margin.product`: kelas `pos_margin_threshold` hilang total dari MRO saat 2 modul terinstall
**Ditemukan di:** Step 1 (2026-08-24) — diwarisi dari `doc-dev/backfill/FINDINGS.md` **F-03** (terkonfirmasi eksekusi Docker, `tests/test_cross_module.py`)
**Tag:** `[DIWARISI-SOURCE]` `[PERLU-KEPUTUSAN]`
**Ref:** `BSL-013`, backfill `F-03`
**Lokasi:** `pos_margin_threshold/wizard/wizard_margin_product.py:4-31`, `sale_margin_threshold/wizard/wizard_margin_product.py:4-31` (byte-identik)
**Deskripsi:** Kedua modul mendefinisikan `_name = 'wizard.margin.product'` tanpa `_inherit`. `__mro__` final hanya berisi kelas dari modul yang diinstall lebih belakangan — kelas modul lain hilang total, bukan digabung.
**Dampak di 18.0:** Sedang — aman selama kedua kelas byte-identik. Risiko utama BUKAN dari perubahan platform 18.0 (ini mekanisme registry model Odoo/Python, kemungkinan tidak berubah), tapi dari perubahan kode salah satu modul saja saat migrasi (mis. `pos_margin_threshold` di-migrasi duluan dengan penyesuaian kode, `sale_margin_threshold` belum) — silent-override bisa menyembunyikan perubahan yang belum lengkap.
**Rekomendasi:** Saat migrasi KEDUA modul, pastikan wizard di kedua modul diubah BERSAMAAN dan tetap byte-identik (atau eksplisit konsolidasi jadi `_inherit` dari satu ke lainnya — itu perubahan struktural, minta persetujuan eksplisit dulu karena berpotensi dianggap "refactor" yang dilarang `CLAUDE.md` §Forbidden Actions kecuali wajib untuk kompatibilitas 18.0).
**Keputusan pemilik modul:** *(kosong)*

---

### MF-04 — `views/product_template_views.xml` dead file, duplikat XML-ID dengan `views/products.xml`
**Ditemukan di:** Step 1 (2026-08-24) — **BARU**, tidak ada di `doc-dev/backfill/FINDINGS.md` (belum pernah tercatat sebelumnya)
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `BSL-014` (`01_intake/pos_margin_threshold/01b_BASELINE_SPEC.md`)
**Lokasi:** `pos_margin_threshold/views/product_template_views.xml` (seluruh file), vs `pos_margin_threshold/views/products.xml` (record `product_template_inherit_pos_margin_threshold`)
**Deskripsi:** `product_template_views.xml` tidak terdaftar di `data:` manifest — dead file, tidak pernah dimuat Odoo di 17.0. File ini mendefinisikan XML-ID yang **identik** (`product_template_inherit_pos_margin_threshold`) dengan yang didefinisikan `products.xml`, tapi dengan `inherit_id` target berbeda (`product.product_template_only_form_view` vs `product.product_template_form_view`) dan struktur visibility field yang sedikit berbeda (versi di `product_template_views.xml` tidak punya kondisi `invisible` untuk multi-variant, versi di `products.xml` punya).
**Dampak di 18.0:** Rendah selama tetap dead file. **Risiko kalau ditambahkan ke manifest tanpa disadari** (mis. saat migrasi seseorang "membersihkan" dan tidak sadar file ini sengaja tidak dimuat) — akan clash XML-ID langsung dengan `products.xml` saat modul di-install, kemungkinan besar error saat load data atau salah satu record menimpa yang lain tergantung urutan load.
**Rekomendasi:** Pertahankan sebagai dead file yang sama persis di 18.0 (JANGAN didaftarkan ke manifest sebagai bagian dari migrasi — itu perubahan fungsional yang butuh persetujuan eksplisit, di luar "port kode saja").
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### MF-05 — `_register_hook` memutasi membership `group_sale_margin_action` tiap registry reload
**Ditemukan di:** Step 1 (2026-08-24) — diwarisi dari `doc-dev/backfill/FINDINGS.md` **F-04** (terkonfirmasi eksekusi Docker, arah "kedua modul terinstall")
**Tag:** `[DIWARISI-SOURCE]` `[PERLU-KEPUTUSAN]`
**Ref:** `BSL-006` (`01_intake/sale_margin_threshold/01b_BASELINE_SPEC.md`), backfill `F-04`
**Lokasi:** `sale_margin_threshold/models/product.py:115-131` (`ProductProduct._register_hook`)
**Deskripsi:** Dipanggil Odoo TIAP registry dibangun ulang (bukan cuma install) — menghapus semua user dari `group_sale_margin_action` kalau `pos_margin_threshold` terinstall, atau menambah semua internal user kalau tidak. Mutasi state, bukan kondisi deklaratif.
**Dampak di 18.0:** Kalau admin manual ubah membership group ini saat `pos_margin_threshold` terinstall, kemungkinan ter-revert diam-diam di reload berikutnya. Mekanisme hook Odoo (`_register_hook`) sendiri tidak berubah antar versi mayor — risiko migrasi rendah untuk MEKANISME-nya, tapi perilakunya (mutasi silent) tetap harus dipertahankan identik.
**Rekomendasi:** Sama seperti backfill — pertimbangkan ganti ke kondisi deklaratif (domain/groups at-read-time). Di luar scope migrasi port-kode-saja kecuali disetujui eksplisit.
**Keputusan pemilik modul:** *(kosong)*

---

### MF-06 — `action_confirm` override asumsi singleton, memecah batch-confirm Odoo core
**Ditemukan di:** Step 1 (2026-08-24) — diwarisi dari `doc-dev/backfill/FINDINGS.md` **F-05** (prioritas Tinggi, dieksekusi 2× Docker — test sendiri + demo data core `sale_stock` ikut crash)
**Tag:** `[DIWARISI-SOURCE]` `[PERLU-KEPUTUSAN]`
**Prioritas:** **Tinggi**
**Ref:** `BSL-002` (`01_intake/sale_margin_threshold/01b_BASELINE_SPEC.md`), backfill `F-05`
**Lokasi:** `sale_margin_threshold/models/sale_order.py:19-27` (`SaleOrder.action_confirm`)
**Deskripsi:** `action_confirm()` membaca `self.is_rental_order_installed_true`/`self.order_line` sebagai singleton tanpa `for order in self:` — batch-confirm >1 sale order dari list view (didukung native Odoo core) crash `ValueError: Expected singleton`.
**Dampak di 18.0:** WAJIB dicek ulang di Step 2 — kalau mekanisme batch action list view Odoo 18.0 berubah caranya memanggil method aksi (mis. selalu iterasi eksplisit vs kirim recordset multi-id), gejala crash yang identik ini bisa muncul di titik berbeda atau malah "sembuh sendiri" secara tidak sengaja — bukan sesuatu yang boleh diasumsikan otomatis sama tanpa verifikasi.
**Rekomendasi:** Backfill merekomendasikan fix (`for order in self:` loop) tapi itu **memperbaiki bug** — di luar scope migrasi "port kode saja" kecuali pemilik modul menyetujui eksplisit sebagai perubahan yang disengaja (lihat `CLAUDE.md` §Forbidden Actions: "Memperbaiki bug yang sudah ada di 17.0" dilarang kecuali disetujui).
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### MF-07 — Duplikasi XML-ID `product_template_inherit_sale_margin_threshold` — kedua file dimuat, yang kedua menimpa total yang pertama
**Ditemukan di:** Step 1 (2026-08-24) — **BARU**, tidak ada di backfill
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `BSL-008` (`01_intake/sale_margin_threshold/01b_BASELINE_SPEC.md`)
**Lokasi:** `sale_margin_threshold/views/product_template_views.xml` (loaded pertama, `inherit_id=product.product_template_only_form_view`) vs `sale_margin_threshold/views/products.xml` (loaded kedua, `inherit_id=product.product_template_form_view`)
**Deskripsi:** Manifest memuat KEDUA file (beda dari kasus serupa `MF-04` di `pos_margin_threshold`, di mana salah satu file dead/tidak dimuat). Karena XML-ID sama persis dan berada di modul yang sama, record kedua (`products.xml`) menimpa SELURUH field record pertama saat load — termasuk `inherit_id` dan `arch`. Kustomisasi yang dimaksud untuk `product_template_only_form_view` tidak pernah benar-benar aktif.
**Dampak di 18.0:** Sedang — perilaku ini (satu dari dua kustomisasi silently discarded) harus dipertahankan identik. Risiko migrasi: kalau Odoo 18.0 mengubah urutan/cara load `data:` manifest (kemungkinan sangat kecil, ini mekanisme ORM dasar), efek "menimpa" ini bisa berubah jadi error alih-alih silent override.
**Rekomendasi:** Pertahankan seperti apa adanya di 18.0 (efek akhirnya, bukan mekanismenya, yang harus identik) — kecuali dev memutuskan ini genuinely bug yang ingin diperbaiki (beri XML-ID berbeda ke masing-masing), itu keputusan eksplisit di luar "port kode saja".
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### MF-08 — Manifest declare `assets._assets_sale` menunjuk folder `static/src/` yang tidak eksis
**Ditemukan di:** Step 1 (2026-08-24) — **BARU**
**Tag:** `[DIWARISI-SOURCE]`
**Prioritas:** Rendah
**Ref:** `BSL-009`
**Lokasi:** `sale_margin_threshold/__manifest__.py` (`assets.sale_margin_threshold._assets_sale`)
**Deskripsi:** Manifest mendeklarasikan glob asset ke `sale_margin_threshold/static/src/**/*`, tapi folder `static/src/` tidak ada sama sekali di modul ini. Tidak error (glob kosong), kemungkinan sisa boilerplate scaffold yang tidak dibersihkan.
**Dampak di 18.0:** Sangat rendah — tidak ada perilaku yang bergantung padanya.
**Rekomendasi:** Bisa dihapus sebagai bagian cleanup, TAPI itu perubahan (walau trivial) di luar "port kode saja" murni — cukup pertahankan apa adanya kecuali dev menyetujui pembersihan.
**Keputusan pemilik modul:** *(kosong)*

---

### MF-09 — `onClickPin` JS menimpa total (bukan extend) patch core `discuss/message_pin`
**Ditemukan di:** Step 1 (2026-08-24) — diwarisi dari `doc-dev/backfill/FINDINGS.md` **F-06**
**Tag:** `[DIWARISI-SOURCE]` `[PERLU-KEPUTUSAN]`
**Ref:** `BSL-002` (`01_intake/pin_message/01b_BASELINE_SPEC.md`), backfill `F-06`
**Lokasi:** `pin_message/static/src/js/message.js:11-27` (`Message.prototype.onClickPin`)
**Deskripsi:** Patch `onClickPin` MENIMPA TOTAL (tidak pernah panggil `super.onClickPin()`) method dengan nama sama di patch core `discuss/message_pin/common/message_patch.js`. Perilaku SAAT INI identik dengan core (dikonfirmasi baca source core saat backfill), tapi pola override total ini berisiko silent-diverge kalau core berubah.
**Dampak di 18.0:** **Risiko migrasi PALING TINGGI di modul `pin_message`** — kalau Odoo 18.0 mengubah behavior `onClickPin` di core (bukan cuma lokasi/nama file), full-override modul ini TIDAK akan otomatis ikut berubah karena tidak pernah delegasi ke `super()`. WAJIB dicek ulang line-by-line terhadap source core `message_patch.js` versi 18.0 di Step 2 — tidak cukup diasumsikan sama dari kecocokan di 17.0.
**Rekomendasi:** Backfill merekomendasikan ganti jadi `super.onClickPin()` untuk robustness — itu **perubahan struktural** (bukan cuma port), di luar scope "port kode saja" kecuali disetujui eksplisit sebagai bagian migrasi (bisa dipertimbangkan KHUSUS kalau Step 2 menemukan core 18.0 sudah berubah dan override total ini pasti pecah — di titik itu "mengikuti pola `super()`" jadi WAJIB demi kompatibilitas, bukan lagi opsional).
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### MF-10 — `console.log` debug tertinggal di `pinMessage.js`
**Ditemukan di:** Step 1 (2026-08-24) — diwarisi dari `doc-dev/backfill/FINDINGS.md` **F-07**
**Tag:** `[DIWARISI-SOURCE]`
**Prioritas:** Rendah
**Ref:** `BSL-005`
**Lokasi:** `pin_message/static/src/js/pinMessage.js:7`
**Deskripsi:** `console.log(component.message.type)` di baris pertama callback `condition` action registry — dieksekusi setiap kali action menu pesan di-render (berpotensi sangat sering di chatter aktif).
**Dampak di 18.0:** Sangat rendah — tidak ada risiko fungsional, cuma noise di browser console.
**Rekomendasi:** Bisa dihapus sebagai cleanup trivial, tapi tetap di luar "port kode saja" murni kecuali disetujui eksplisit.
**Keputusan pemilik modul:** *(kosong)*

---

### MF-11 — `Orderline.getDisplayData()` full-override (bukan extend `super()`)
**Ditemukan di:** Step 2 (2026-08-24) — **BARU**, ditemukan saat diff analysis, tidak ada di backfill
**Tag:** `[DIWARISI-SOURCE]` `[PERLU-KEPUTUSAN]`
**Ref:** `DIFF-07` (`02_diff/pos_margin_threshold/02_DIFF_ANALYSIS.md`)
**Lokasi:** `pos_margin_threshold/static/src/store/models/models.js:26-50` (patch `Orderline.prototype.getDisplayData`)
**Deskripsi:** Method ini di-patch dengan MEREPLIKASI SELURUH field data tampilan orderline core (bukan cuma menambah 3 field baru terkait margin) — tidak pernah memanggil `super.getDisplayData()`. Pola sama persis dengan `MF-09` (`pin_message`, `onClickPin`): aman selama core tidak berubah, tapi kalau versi 18.0 menambah field baru ke data tampilan orderline (concept baru apapun), field itu tidak akan pernah muncul karena override total ini tidak pernah delegasi ke core untuk field-field yang tidak modul ini definisikan ulang.
**Dampak di 18.0:** Sedang-Tinggi — silent, tidak crash, cuma field baru core (kalau ada) yang hilang dari tampilan orderline. Wajib dicek Step 2 lanjutan/Step 6: apakah `getDisplayData()` core 18.0 menambah field dibanding 17.0.
**Rekomendasi:** Idealnya diubah jadi extend (`return {...super.getDisplayData(), minimumSalePrice: ..., ...}`) untuk robustness — itu **perubahan struktural**, di luar "port kode saja" murni kecuali disetujui eksplisit ATAU terbukti wajib demi kompatibilitas (field core baru yang genuinely dibutuhkan hilang).
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### MF-12 — `chatter.js` import `@mail/core/web/chatter` path sudah tidak ada di 18.0 — RESOLVED
**Ditemukan di:** Step 6 Fase E (2026-08-24), lewat G2 browser nyata (Docker `odoo:18.0` + Claude Browser tool) — bukan analisis statis
**Tag:** `[GAP-MIGRASI]`
**Ref:** `DIFF-04` (`02_diff/pin_message/02_DIFF_ANALYSIS.md`), `06_implementation/pin_message/06c_IMPLEMENTATION_LOG.md` Fase E
**Lokasi:** `pin_message/static/src/js/chatter.js:4`
**Deskripsi:** Console browser menunjukkan `@mail/core/web/chatter` "needed but not defined" dan `@pin_message/js/chatter` gagal load karena dependency itu. Dikonfirmasi via `docker exec ... find` di container `odoo:18.0`: file benar-benar pindah ke `mail/static/src/chatter/web_portal/chatter.js`.
**Dampak:** Tanpa fix, SELURUH fitur pin_message (bukan cuma chatter) gagal load di browser — modul terpasang tapi non-fungsional total di sisi frontend.
**Status:** ✅ **RESOLVED 2026-08-24** — import diubah ke `@mail/chatter/web_portal/chatter`, dikonfirmasi tab browser baru tidak lagi menunjukkan error ini.
**Keputusan pemilik modul:** Tidak perlu — ini perbaikan wajib kompatibilitas (API lama dihapus total), bukan pilihan desain.

---

### MF-13 — `ConfirmPopup`/`ErrorPopup` (POS) dihapus total di 18.0 — RESOLVED
**Ditemukan di:** Step 6 Fase E (2026-08-24), lewat audit source proaktif (cross-check tiap import `pos_margin_threshold` ke source container `odoo:18.0`) — TIDAK lewat error konsol otomatis, karena jalur kode ini (`Order.pay()`) tidak tereksekusi cuma dari membuka POS
**Tag:** `[GAP-MIGRASI]`
**Prioritas:** **Tinggi**
**Ref:** `DIFF-04` (`02_diff/pos_margin_threshold/02_DIFF_ANALYSIS.md`), `06_implementation/pos_margin_threshold/06c_IMPLEMENTATION_LOG.md` Fase E
**Lokasi:** `pos_margin_threshold/static/src/store/models/models.js:4-5` (import), `:62,70` (pemakaian)
**Deskripsi:** `@point_of_sale/app/utils/confirm_popup/confirm_popup` dan `@point_of_sale/app/errors/popups/error_popup`, plus service `this.env.services.popup` itu sendiri, **dihapus total** di Odoo 18.0 — diganti mekanisme `dialog` service + `ConfirmationDialog`/`AlertDialog` (`@web/core/confirmation_dialog/confirmation_dialog`) + helper `ask()` (`@point_of_sale/app/store/make_awaitable_dialog`), dikonfirmasi ini pola yang dipakai core POS 18.0 sendiri (`pos_store.js`).
**Dampak:** Ini FITUR INTI modul (blocking/warning saat bayar produk di bawah minimum) — tanpa fix, `Order.pay()` akan crash (`popup` service undefined) SETIAP KALI kasir mencoba bayar order dengan produk di bawah minimum, walau modul "terinstall" sukses.
**Status:** ✅ **RESOLVED dan TERVERIFIKASI PENUH 2026-08-24** — diganti ke `ask(this.env.services.dialog, {...})` (cabang confirm) dan `this.env.services.dialog.add(AlertDialog, {...})` (cabang block), pesan title/body tidak diubah. Blocking logic-nya sendiri juga dipindah dari `Order.pay()` (sudah tidak ada, lihat `MF-16`) ke `PosStore.pay()`. **Dikonfirmasi lewat Tour test nyata (Mode D, Chrome asli di Docker)** — `tests/test_margin_threshold_tour.py::test_pos_margin_threshold_below_minimum_confirm_tour`: klik Pay dengan produk di bawah minimum → dialog "Price unit less than minimum price" benar-benar muncul dengan body yang benar → klik Confirm → lanjut ke Payment Screen → validasi pembayaran sukses. "tour succeeded", 0 failed/0 error.
**Keputusan pemilik modul:** Tidak perlu — perbaikan wajib kompatibilitas.

---

### MF-14 — `message_card_list.xml` xpath tag selector tidak match elemen core baru — RESOLVED
**Ditemukan di:** Step 6 Fase F (2026-08-24), lewat audit source proaktif (cross-check ke source container `odoo:18.0` setelah menemukan MF-12, sebagai due-diligence tambahan)
**Tag:** `[GAP-MIGRASI]`
**Ref:** `DIFF-03`, `06_implementation/pin_message/06c_IMPLEMENTATION_LOG.md` Fase F
**Lokasi:** `pin_message/static/src/xml/message_card_list.xml` (xpath expression)
**Deskripsi:** Xpath `//button[contains(@class, 'o-mail-MessageCard-jump')]` menarget tag `<button>` — tapi core `mail.MessageCardList` 18.0 mengubah elemen ini jadi `<a role="button" class="...">`. Xpath tag-selector `button` tidak akan pernah match tag `a`.
**Dampak:** Kustomisasi tombol "See" (mengganti label "Jump") tidak akan pernah aktif — bukan install-blocking (QWeb JS template tidak divalidasi saat install, cuma saat asset bundle compile/dipakai), silent-gagal.
**Status:** ✅ **RESOLVED 2026-08-24** — xpath diubah ke `//a[contains(@class, 'o-mail-MessageCard-jump')]`.
**Keputusan pemilik modul:** Tidak perlu — perbaikan wajib kompatibilitas (bukan perubahan tampilan yang disengaja).

---

### MF-15 — POS data-model architecture: `Order`/`Orderline`/`Product` classes dipindah total — RESOLVED
**Ditemukan di:** Step 6 Fase E (2026-08-24), lewat audit source proaktif (cross-check import path modul ini SATU PER SATU ke source container `odoo:18.0`, dipicu curiga setelah `MF-13`) — **bukan** dari error konsol otomatis, karena bug ini baru bermanifestasi saat asset bundle POS benar-benar di-render browser (tidak kelihatan dari install/G1, tidak kelihatan dari G2 awal yang cuma cek backend login)
**Tag:** `[GAP-MIGRASI]`
**Prioritas:** **Kritis**
**Ref:** `06_implementation/pos_margin_threshold/06c_IMPLEMENTATION_LOG.md` Fase E
**Lokasi:** `pos_margin_threshold/static/src/store/models/models.js:3` (import lama)
**Deskripsi:** `@point_of_sale/app/store/models` — path yang di-import modul ini untuk `Order`, `Orderline`, `Product` — **masih ada sebagai file, TAPI isinya kosong (0 byte)**, dikonfirmasi `ls -la` di container `odoo:18.0`. Odoo 18.0 memindahkan seluruh arsitektur data POS ke pola baru ("Base model" reactive record, `static/src/app/models/`), dengan nama kelas baru: `Order`→`PosOrder` (`@point_of_sale/app/models/pos_order`), `Orderline`→`PosOrderline` (`@point_of_sale/app/models/pos_order_line`), `Product`→`ProductProduct` (`@point_of_sale/app/models/product_product`). Import lama menghasilkan `undefined` untuk ketiga nama tersebut — `patch(Order.prototype, ...)` akan crash `TypeError: Cannot read properties of undefined (reading 'prototype')` begitu bundle JS modul ini benar-benar dievaluasi browser.
**Dampak:** Kritis — seluruh modul JS (bukan cuma fitur payment) gagal total begitu POS session dibuka, kalau tidak diperbaiki.
**Kabar baik yang mengurangi risiko:** method-level API (`get_unit_display_price()`, `get_orderlines()`, `get_full_product_name()`, dst) **byte-identik nama & signature-nya** di kelas baru — dikonfirmasi baca source `pos_order_line.js`/`pos_order.js` langsung. Migrasi jadi soal ganti nama kelas & path import, BUKAN menulis ulang logic dari nol.
**Status:** ✅ **RESOLVED dan TERVERIFIKASI** — import diperbaiki di `models.js`, dikonfirmasi install (G1) DAN Tour test interaktif (G2, `MF-13`) sama-sama pass.
**Keputusan pemilik modul:** Tidak perlu — perbaikan wajib kompatibilitas, API publik yang dipakai modul ini tidak berubah semantiknya.

---

### MF-16 — `Order.prototype.pay()` tidak lagi dipanggil tombol "Pay" — RESOLVED
**Ditemukan di:** Step 6 Fase E (2026-08-24), sambungan investigasi `MF-15` — dicek langsung "apa yang benar-benar dipanggil tombol Pay" di source `product_screen.xml`/`pos_store.js` container `odoo:18.0`
**Tag:** `[GAP-MIGRASI]`
**Prioritas:** **Kritis**
**Ref:** `06_implementation/pos_margin_threshold/06c_IMPLEMENTATION_LOG.md` Fase E
**Lokasi:** `pos_margin_threshold/static/src/store/models/models.js` (patch lama `Order.prototype.pay`), `pos_margin_threshold/static/src/store/pos_store.js` (lokasi baru)
**Deskripsi:** Di 17.0, tombol "Pay" memanggil `Order.prototype.pay()` langsung — modul ini menaruh cek blocking-payment di situ. Di 18.0, tombol "Pay" (`product_screen.xml`) memanggil `this.pos.pay()` yaitu `PosStore.prototype.pay()` — method BARU yang tidak pernah memanggil `Order`/`PosOrder.pay()` sama sekali (method itu bahkan tidak ada lagi di kelas order). `PosStore.pay()` langsung menangani cek lot/serial number lalu navigasi ke Payment Screen.
**Dampak:** Kritis — kalaupun `MF-15` (import) diperbaiki tapi patch tetap ditaruh di `Order.prototype`, method itu TIDAK PERNAH terpanggil oleh UI — fitur blocking-payment modul ini mati total secara silent (tidak ada error, cuma tidak pernah jalan).
**Status:** ✅ **RESOLVED dan TERVERIFIKASI** — logic blocking (cek orderline di bawah minimum, dialog confirm/alert) dipindah jadi patch `PosStore.prototype.pay()` di `pos_store.js`, memanggil `super.pay(...arguments)` di akhir supaya lot-check dan navigasi payment screen bawaan core tetap jalan. Dikonfirmasi Tour test nyata (lihat `MF-13`).
**Keputusan pemilik modul:** Tidak perlu — relokasi wajib mengikuti perubahan entry point core, behavior akhir identik 17.0.

---

### MF-17 — `PosStore.prototype._loadProductProduct()` hook sudah tidak ada — RESOLVED
**Ditemukan di:** Step 6 Fase E (2026-08-24), audit source proaktif lanjutan
**Tag:** `[GAP-MIGRASI]`
**Prioritas:** Rendah (dead code, tidak crash apapun)
**Lokasi:** `pos_margin_threshold/static/src/store/pos_store.js` (patch lama)
**Deskripsi:** `_loadProductProduct()` — method yang di-patch modul ini untuk fallback `minimum_sale_price`/`minimum_sale_price_with_tax` ke `0` kalau falsy — **tidak ada lagi** di `PosStore` 18.0 (arsitektur loading data pindah total ke pola `_load_pos_data_fields`, lihat `MF-18`). Patch ke method yang tidak ada di prototype tidak error (`patch()` cuma menambah method baru yang tidak pernah dipanggil siapapun) — jadi ini silent dead code, bukan crash.
**Dampak:** Rendah — fallback-nya juga sudah tidak relevan (field `fields.Float()` Odoo core selalu default `0.0`, bukan `null`/`undefined`, di hasil `read()`/`search_read()`).
**Status:** ✅ **RESOLVED** — patch dihapus dari `pos_store.js` (bukan diperbaiki, karena tujuannya sudah tidak relevan).
**Keputusan pemilik modul:** Tidak perlu — pembersihan dead code yang memang sudah tidak berfungsi apapun.

---

### MF-18 — `pos.session._loader_params_product_product()` diganti `_load_pos_data_fields()` — RESOLVED
**Ditemukan di:** Step 6 Fase E (2026-08-24), sambungan investigasi `MF-15`/`MF-17` — dicek `grep` hook lama di `pos_session.py`/`product.py` core container `odoo:18.0`
**Tag:** `[GAP-MIGRASI]`
**Prioritas:** **Tinggi**
**Ref:** `DIFF-05` (`02_diff/pos_margin_threshold/02_DIFF_ANALYSIS.md`)
**Lokasi:** `pos_margin_threshold/models/pos_session.py` (override lama, dihapus), `pos_margin_threshold/models/product.py` (lokasi baru)
**Deskripsi:** Mekanisme loading field custom ke frontend POS berubah total: dari `pos.session._loader_params_<model>()` (mutasi dict `params['search_params']['fields']`) jadi `<model>._load_pos_data_fields(self, config_id)` (`@api.model`, return list field, didefinisikan LANGSUNG di model yang datanya di-load — di sini `product.product`, bukan lagi di `pos.session`). Hook lama TIDAK ADA lagi di `pos.session`, jadi override modul ini jadi dead code (tidak pernah terpanggil) — konsisten pola `MF-17`.
**Dampak:** Tinggi — field `minimum_sale_price`/`minimum_sale_price_with_tax` TIDAK AKAN PERNAH terkirim ke frontend POS tanpa fix ini, silent (tidak ada error apapun, popup/highlight cuma tidak pernah ter-trigger karena data-nya kosong/default).
**Status:** ✅ **RESOLVED dan TERVERIFIKASI** — override lama di `pos_session.py` dihapus total (dengan catatan penjelasan di file), diganti override baru `ProductProduct._load_pos_data_fields()` di `models/product.py` (`super()._load_pos_data_fields(config_id)` + tambah 2 field). Dikonfirmasi Tour test nyata membuktikan data ini benar-benar sampai ke frontend (dialog below-minimum muncul dengan benar, artinya field ter-load dan ter-hitung).
**Keputusan pemilik modul:** Tidak perlu — relokasi wajib mengikuti API baru, field yang di-expose identik.

---

### MF-19 — Owl `Orderline` component validasi ketat `props.line` shape — RESOLVED
**Ditemukan di:** Step 6 Fase F (2026-08-24), lewat Tour test nyata (Mode D) — `OwlError: Invalid props for component 'Orderline': 'line' doesn't have the correct shape (unknown key 'minimumSalePrice', ...)`
**Tag:** `[GAP-MIGRASI]`
**Prioritas:** Tinggi (crash render kalau tidak diperbaiki — TIDAK terdeteksi G1, cuma dari render browser nyata)
**Lokasi:** `pos_margin_threshold/static/src/store/models/models.js` (patch `getDisplayData()`)
**Deskripsi:** Komponen Owl `Orderline` (`@point_of_sale/app/generic_components/orderline/orderline.js`) mendeklarasikan `static props = { line: { type: Object, shape: {...} } }` — Owl 18.0 validasi STRICT terhadap shape ini, key APAPUN yang tidak dideklarasikan di `shape` di-reject sebagai error fatal (bukan cuma warning). Field custom (`minimumSalePrice`, `minimumSalePriceWithTax`, `isLessMinimumSalePrice`) yang ditambahkan `getDisplayData()` modul ini tidak terdaftar di shape itu.
**Dampak:** Fatal — begitu ada orderline yang datanya lewat `getDisplayData()` yang sudah dimodifikasi, SELURUH component tree Owl di titik itu crash (`[Owl] Unhandled error. Destroying the root component`), order screen tidak bisa dipakai.
**Status:** ✅ **RESOLVED dan TERVERIFIKASI** — `patch(Orderline.props.line.shape, {minimumSalePrice: {type: String, optional: true}, minimumSalePriceWithTax: {...}, isLessMinimumSalePrice: {type: Boolean, optional: true}})` ditambahkan di `models.js`. Dikonfirmasi Tour test lanjut normal setelah fix ini.
**Keputusan pemilik modul:** Tidak perlu — perbaikan wajib kompatibilitas, bagian tak terpisahkan dari mengekspos field baru lewat `getDisplayData()`.

---

### MF-20 — `orderline.xml` xpath direct-child tidak match wrapper baru — RESOLVED
**Ditemukan di:** Step 6 Fase F (2026-08-24), lewat Tour test nyata — `Element '<xpath expr="...">' cannot be located in element tree`
**Tag:** `[GAP-MIGRASI]`
**Prioritas:** Tinggi (crash render QWeb — juga TIDAK terdeteksi G1)
**Lokasi:** `pos_margin_threshold/static/src/store/orderline.xml`
**Deskripsi:** Xpath `//li[contains(@class,'orderline')]/ul[hasclass('info-list')]/t[@t-slot='default']` mengasumsikan `<ul class="info-list">` adalah ANAK LANGSUNG dari `<li class="orderline">`. Core 18.0 menambah `<div class="d-flex flex-column w-100 gap-1">` sebagai wrapper di antaranya (dikonfirmasi baca `orderline.xml` core container) — xpath direct-child (`/ul`) tidak lagi match struktur baru.
**Dampak:** Fatal untuk bagian ini — highlight teks peringatan "harga di bawah minimum" tidak akan pernah muncul, DAN karena xpath gagal resolve total, seluruh `t-inherit` ini bisa gagal (`ParseError`/`OwlError` di titik itu).
**Status:** ✅ **RESOLVED dan TERVERIFIKASI** — xpath diubah ke descendant (`//ul[hasclass('info-list')]`, dua slash) supaya tetap match terlepas dari wrapper baru. Dikonfirmasi Tour test render bersih setelah fix.
**Keputusan pemilik modul:** Tidak perlu — perbaikan wajib kompatibilitas, tidak mengubah maksud/isi kustomisasi asli.

---

### MF-21 — `Environment.lang` (18.0) validasi ketat bahasa terinstall — CATATAN DEPLOYMENT
**Ditemukan di:** Step 6 (2026-08-24), lewat run test suite penuh (`--test-enable`) pertama kali di 18.0 — `sale_margin_threshold/tests/test_action_confirm.py::test_action_confirm_wizard_path_when_not_blocking` gagal `UserError: Invalid language code: fr_FR`
**Tag:** `[CATATAN-DEPLOYMENT]` (bukan `[GAP-MIGRASI]` — lihat alasan di Deskripsi)
**Prioritas:** Sedang
**Lokasi:** `sale_margin_threshold/models/sale_order.py:42` (`wizard.with_context(lang='fr_FR').write(...)`)
**Deskripsi:** Odoo 18.0 `Environment.lang` (`odoo/api.py`) sekarang me-raise `UserError` eksplisit kalau context `lang` bukan `en_US` DAN bukan bahasa yang benar-benar terinstall (`res.lang._get_data`). Test database sesi ini TIDAK punya bahasa Prancis terinstall (sama seperti environment test backfill 17.0 — dikonfirmasi `docker-compose.yml` 17.0 juga tidak install bahasa apapun secara eksplisit), tapi test yang SAMA PERSIS lolos 0 error di 17.0 dan baru gagal di 18.0 — **dikonfirmasi ini genuinely validasi BARU 18.0**, bukan config test yang berubah.
**Verifikasi:** Menambahkan `--load-language=fr_FR` ke command Docker membuat SEMUA 17 test (termasuk yang ini) pass `0 failed, 0 error(s)` — membuktikan ini BUKAN bug kode `sale_order.py`, teknik `with_context(lang=...).write(...)` untuk field bilingual tetap valid selama bahasa targetnya benar-benar terinstall.
**Dampak:** Kalau environment PRODUCTION modul ini nanti dijalankan TANPA bahasa Prancis terinstall, `action_confirm()` akan crash `UserError` setiap kali cabang `blocking_transaction_order=False` (wizard konfirmasi) dieksekusi — meng-crash alur core (confirm quotation), bukan cuma gagal senyap.
**Status:** ✅ Dikonfirmasi bukan bug kode — **butuh keputusan/konfirmasi dev**: pastikan bahasa Prancis terinstall di environment production sebelum go-live 18.0 (kemungkinan besar SUDAH terinstall kalau modul ini memang dipakai user berbahasa Prancis, tapi wajib dikonfirmasi eksplisit, jangan diasumsikan).
**Keputusan pemilik modul:** *(kosong — perlu konfirmasi eksplisit dev: bahasa Prancis terinstall di production?)*

---

## Cara Pakai

1. Update SETIAP KALI step manapun (1-11), modul manapun, menemukan gap/bug/ambiguitas yang butuh
   keputusan manusia — jangan tunggu akhir project.
2. Tag: `[PERLU-KEPUTUSAN]` / `[DIWARISI-SOURCE]` (termasuk pewarisan dari `doc-dev/backfill/F-NNN`)
   / `[GAP-MIGRASI]` (genuinely muncul karena perubahan platform 18.0).
3. Step 4 dan Step 8 (tiap modul) WAJIB baca file ini sebagai bagian gate.
4. Update status (bukan hapus) begitu keputusan diambil — tandai `✅ RESOLVED`/`✅ CONFIRMED` + tanggal
   + bukti.
