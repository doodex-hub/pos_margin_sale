# Findings — pos-margin-sale (migrasi 17.0 → 18.0, multi-module)

> **Cross-cutting, direkomendasikan (tidak kondisional)** — dokumen konsolidasi TUNGGAL untuk semua
> gap/bug/ambiguitas yang butuh keputusan manusia selama migrasi, untuk KETIGA modul
> (`pos_margin_threshold`, `sale_margin_threshold`, `pin_message`) — lihat adaptasi multi-modul di
> `CLAUDE.md` root. Diadaptasi dari `migration-tool/templates/FINDINGS.md`.

**Modul:** `pos_margin_threshold`, `sale_margin_threshold`, `pin_message` (satu file, prefix modul di
tiap judul finding)
**Migrasi:** 17.0 → 18.0
**Terakhir update:** 2026-08-26 (Step 9 lanjutan — `MF-21` di-RESOLVE dengan fix kode atas keputusan
dev eksplisit [Prancis tidak boleh jadi syarat deployment], `sale_order.py` tidak lagi punya
dependency ke `fr_FR`; total 24 finding, 9 diwarisi backfill)

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
| MF-03 | Model `wizard.margin.product`: kelas `pos_margin_threshold` hilang total dari MRO saat 2 modul terinstall — dikonfirmasi Step 9 SELALU begitu, independen urutan install | pos_margin_threshold + sale_margin_threshold | 1 | `[DIWARISI-SOURCE]` `[PERLU-KEPUTUSAN]` | Sedang | Terbuka — risiko tetap ada (lihat rekomendasi), tapi mekanisme sudah dikonfirmasi empiris (Step 9) |
| MF-04 | `views/product_template_views.xml` dead file, duplikat XML-ID dengan `views/products.xml` | pos_margin_threshold | 1 | `[DIWARISI-SOURCE]` | Rendah | Terbuka — baru ditemukan, belum ada di backfill |
| MF-05 | `_register_hook` memutasi membership `group_sale_margin_action` tiap registry reload | sale_margin_threshold (interaksi dgn pos_margin_threshold) | 1 | `[DIWARISI-SOURCE]` `[PERLU-KEPUTUSAN]` | Sedang | Terbuka |
| MF-06 | `action_confirm` override asumsi singleton — memecah batch-confirm Odoo core | sale_margin_threshold | 1 | `[DIWARISI-SOURCE]` `[PERLU-KEPUTUSAN]` | **Tinggi** | Terbuka |
| MF-07 | Duplikasi XML-ID `product_template_inherit_sale_margin_threshold` — KEDUA file dimuat, yang kedua menimpa total yang pertama | sale_margin_threshold | 1 | `[DIWARISI-SOURCE]` | Sedang | Terbuka — baru ditemukan, lebih serius dari MF-04 (di sini file aktif dimuat, bukan dead) |
| MF-08 | Manifest declare `assets._assets_sale` menunjuk folder `static/src/` yang tidak eksis | sale_margin_threshold | 1 | `[DIWARISI-SOURCE]` | Rendah | Terbuka — baru ditemukan |
| MF-09 | `onClickPin` JS menimpa total (bukan extend) patch core `discuss/message_pin` | pin_message | 1 | `[DIWARISI-SOURCE]` | Sedang | ✅ **CONFIRMED** (Step 8, 2026-08-24) — dicek langsung terhadap source 17.0/18.0: cabang `is_discussion` jadi dead code di 18.0 tapi TIDAK ADA kehilangan fitur (Discuss pin tetap jalan penuh lewat mekanisme native 18.0). Dibiarkan apa adanya. |
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
| MF-21 | `Environment.lang` (18.0) validasi ketat — `UserError` kalau context `lang=fr_FR` tapi bahasa Prancis tidak diinstall di database | sale_margin_threshold | 6 | `[GAP-MIGRASI]` | Sedang | ✅ **RESOLVED** (2026-08-26) — dev memutuskan tidak boleh mensyaratkan Prancis terinstall; kode diperbaiki (hapus `.with_context(lang='fr_FR')`, pilih string langsung seperti pola cabang blocking). Dikonfirmasi `0 failed, 0 error(s) of 22 tests` TANPA bahasa Prancis terinstall sama sekali |
| MF-22 | `pin_message/chatter.js` — `load()` full-override memanggil `this.threadService.fetchData(thread, requestList, options)`, service+signature ini sudah tidak ada di 18.0 | pin_message | 6 | `[GAP-MIGRASI]` | **Tinggi** — crash total begitu chatter mount | ✅ **RESOLVED** — override dihapus (extend, bukan replace), terkonfirmasi Tour test nyata "tour succeeded" |
| MF-23 | `is_pinned` tidak lagi bisa "diminta" lewat field-list custom di `Chatter.load()` — field kustom ke frontend mail sekarang lewat `mail.message._to_store()` (per-model, seperti pola POS `_load_pos_data_fields`, `MF-18`) | pin_message | 6 | `[GAP-MIGRASI]` | Tinggi (silent, field tidak pernah sampai ke frontend tanpa fix) | ✅ **RESOLVED** — `mail.message._to_store()` di-extend, tambah `store.add(message, {'is_pinned': ...})`, terkonfirmasi Tour test |
| MF-24 | `pinMessage.js` — `component.canAddReaction` (getter component 17.0) dipindah jadi method `message.canAddReaction(thread)` di 18.0 — `condition` action "pins" selalu `false`, entry menu Pin tidak pernah render | pin_message | 8 | `[GAP-MIGRASI]` | **Tinggi** (silent, action-menu "Pin" tidak pernah muncul, sejak awal migrasi tanpa disadari) | ✅ **RESOLVED** — `condition` diubah jadi `component.message.canAddReaction(component.props.thread)`, terkonfirmasi re-run test suite penuh (kedua Tour test tetap "tour succeeded") |

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

**Update Step 9 (2026-08-26) — dicek empiris DUA urutan install, hipotesis "tergantung urutan `-i`" TERBUKTI SALAH:**
Dites langsung: (1) urutan compose standar `-i pos_margin_threshold,sale_margin_threshold,pin_message`, dan (2) urutan dibalik total lewat `docker compose run` satu-off dengan `-i sale_margin_threshold,pos_margin_threshold` (database test terpisah `pos_margin_sale_migration_18_reverse_test`, dihapus setelah dicek). **Hasil KEDUA kali identik** — `__mro__` `wizard.margin.product` SELALU berisi `sale_margin_threshold.wizard.wizard_margin_product.WizardMarginProduct`, TIDAK PERNAH `pos_margin_threshold`-nya, terlepas dari urutan `-i` di command line. Ini artinya urutan literal argumen `-i` BUKAN faktor penentu — MRO Odoo untuk model dengan `_name` sama tanpa `_inherit` ditentukan mekanisme lain (kemungkinan urutan topological load graph berdasar `depends`/nama modul, bukan urutan CLI) yang secara konsisten memenangkan `sale_margin_threshold`. **`05a_MIGRATION_ACCEPTANCE_CRITERIA.md` AC-04-02 (kedua modul) perlu dikoreksi** — premisnya ("MRO tergantung urutan install, buktikan lewat urutan terbalik") tidak berlaku; yang benar adalah "MRO SELALU memenangkan `sale_margin_threshold`, independen dari urutan install" — risiko tetap sama (silent-override kalau salah satu modul saja diubah), cuma penjelasan mekanismenya yang perlu diperbaiki di dokumentasi.
**Bukti mentah:** log `odoo.tests.result` kedua run — urutan standar (`docker-env/logs/odoo.log`, baris ~18403/18635, run 2026-08-26 02:06) dan urutan dibalik (`docker-env/logs/odoo_reverse.log`, run 2026-08-26 02:08) — `__mro__` string kedua run byte-identik.

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
**Tag:** `[DIWARISI-SOURCE]` `[PERLU-KEPUTUSAN]` → **lihat update Step 8 di bawah, sudah dikonfirmasi teknis**
**Ref:** `BSL-002` (`01_intake/pin_message/01b_BASELINE_SPEC.md`), backfill `F-06`
**Lokasi:** `pin_message/static/src/js/message.js:11-27` (`Message.prototype.onClickPin`)
**Deskripsi:** Patch `onClickPin` MENIMPA TOTAL (tidak pernah panggil `super.onClickPin()`) method dengan nama sama di patch core `discuss/message_pin/common/message_patch.js`. Perilaku SAAT INI identik dengan core (dikonfirmasi baca source core saat backfill), tapi pola override total ini berisiko silent-diverge kalau core berubah.
**Dampak di 18.0 (perkiraan awal, Step 1):** **Risiko migrasi PALING TINGGI di modul `pin_message`** — kalau Odoo 18.0 mengubah behavior `onClickPin` di core (bukan cuma lokasi/nama file), full-override modul ini TIDAK akan otomatis ikut berubah karena tidak pernah delegasi ke `super()`. WAJIB dicek ulang line-by-line terhadap source core `message_patch.js` versi 18.0 di Step 2 — tidak cukup diasumsikan sama dari kecocokan di 17.0.
**Rekomendasi (Step 1):** Backfill merekomendasikan ganti jadi `super.onClickPin()` untuk robustness — itu **perubahan struktural** (bukan cuma port), di luar scope "port kode saja" kecuali disetujui eksplisit sebagai bagian migrasi.

**Update Step 8 (2026-08-24) — dicek langsung terhadap source 18.0, DIKONFIRMASI HARMLESS, bukan lagi `[PERLU-KEPUTUSAN]` murni:**
Dicek `docker run --rm odoo:17.0`/`odoo:18.0` grep langsung `mail/static/src/discuss/message_pin/`:
- **17.0:** `messagePinService` yang dipakai method ini (`this.messagePinService`) BUKAN sesuatu yang `pin_message` definisikan sendiri — itu service Odoo CORE 17.0 asli (`registry.category("services").add("discuss.message.pin", messagePinService)`), di-inject ke `Message` component oleh core-nya sendiri lewat `message_patch.js` (`useState(useService("discuss.message.pin"))`), dan core 17.0 SENDIRI juga punya `onClickPin()` dengan logika identik (branch `is_discussion`, panggil `getPinnedAt`/`pin`/`unpin`). Jadi cabang `is_discussion` di modul ini bukan business logic custom — itu DUPLIKASI method core 17.0 apa adanya (kemungkinan besar supaya bisa gabung dengan cabang `else` custom log-note dalam satu method, karena Owl patch tidak trivial untuk "sisipkan di tengah" tanpa override total).
- **18.0:** grep `messagePinService` di seluruh addon `mail` 18.0 = 0 match — service ini dihapus total. Core 18.0 juga tidak lagi memanggil `onClickPin()` untuk aksi native pin di Discuss channel (grep `onClickPin` di addon `mail` 18.0 = 0 match) — native pin action sekarang panggil `message.pin()` langsung di message MODEL (`discuss/message_pin/common/message_model_patch.js`), yang membuka `MessageConfirmDialog` lalu ORM `discuss.channel.set_message_pin`.
- **Kesimpulan:** cabang `is_discussion` di `onClickPin()` milik modul ini jadi **dead code yang provably tidak bisa dieksekusi lagi** di 18.0 (tidak ada UI element manapun yang memanggilnya) — TAPI ini BUKAN kehilangan fitur, karena Discuss channel pinning tetap berfungsi penuh lewat mekanisme native 18.0 (`message.pin()`), yang MENGGANTIKAN peran core 17.0 yang tadinya diduplikasi modul ini. End-user experience pin/unpin di Discuss channel **tidak berubah** — cuma jalur kode yang mengeksekusinya sekarang 100% core, bukan lagi (duplikat) modul ini.
- **Keputusan:** kode dead branch ini **DIBIARKAN apa adanya** (tidak dihapus) — menghapusnya adalah cleanup di luar scope "port kode saja" yang tidak diminta, dan membiarkannya tidak officialy punya efek samping (tidak pernah terpanggil). Tidak perlu keputusan `[PERLU-KEPUTUSAN]` lebih lanjut dari dev — sudah confirmed secara teknis, bukan lagi ambiguitas.
**Keputusan pemilik modul:** ✅ **CONFIRMED (Step 8, 2026-08-24)** — tidak ada dampak behavior; dead code dibiarkan, tidak perlu persetujuan tambahan.

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

### MF-21 — `Environment.lang` (18.0) validasi ketat bahasa terinstall — RESOLVED (fix kode, bukan lagi catatan deployment)
**Ditemukan di:** Step 6 (2026-08-24), lewat run test suite penuh (`--test-enable`) pertama kali di 18.0 — `sale_margin_threshold/tests/test_action_confirm.py::test_action_confirm_wizard_path_when_not_blocking` gagal `UserError: Invalid language code: fr_FR`
**Tag:** `[GAP-MIGRASI]` (direklasifikasi dari `[CATATAN-DEPLOYMENT]` — lihat keputusan dev di bawah)
**Prioritas:** Sedang
**Lokasi:** `sale_margin_threshold/models/sale_order.py:41-43` (dulu: `wizard.create(...)` + `wizard.with_context(lang='fr_FR').write(...)`)
**Deskripsi (akar masalah):** Odoo 18.0 `Environment.lang` (`odoo/api.py`) sekarang me-raise `UserError` eksplisit kalau context `lang` bukan `en_US` DAN bukan bahasa yang benar-benar terinstall (`res.lang._get_data`) — validasi BARU di 18.0, tidak ada di 17.0. Kode asli menulis pesan wizard translatable field (`message = fields.Text(translate=True)`) DUA kali — sekali normal (Inggris), sekali lagi dipaksa `.with_context(lang='fr_FR')` untuk menyimpan versi Prancis lewat mekanisme translated-field Odoo, yang WAJIB `fr_FR` benar-benar terdaftar sebagai `res.lang`.
**Keputusan dev (2026-08-26):** bahasa Prancis di environment production **tidak bisa dijamin selalu terinstall** ("fr bisa terinstall bisa tidak") — modul TIDAK BOLEH mensyaratkan itu. Diputuskan: **perbaiki kode**, bukan menambah syarat deployment.
**Fix:** Cabang lain di file yang sama (`blocking_transaction_order=True`, baris 33-37) sudah menyelesaikan masalah identik ("pilih teks Inggris atau Prancis tergantung bahasa user") TANPA translated-field sama sekali — cukup `if user_language == 'French': pakai message_Fr else: pakai message` (string plain, `user_language` dari `detect_user_language()` yang membaca `self.env.context.get('lang')`). Idiom yang SAMA diterapkan ke cabang wizard: `wizard_message = message_Fr if user_language == 'French' else message`, lalu SATU `wizard.create({'message': wizard_message})` — dua-kali-tulis dan `.with_context(lang='fr_FR')` dihapus total. Tidak ada lagi referensi `fr_FR` di manapun di modul ini.
**Kenapa ini aman/tidak melanggar aturan "port apa adanya":** perubahan ini secara eksplisit diminta+disetujui user (bukan AI unilateral "memperbaiki bug lama") sebagai respons terhadap constraint deployment baru ("fr bisa ada bisa tidak"). Behavior YANG TERLIHAT USER tidak berubah sama sekali (user Prancis tetap lihat teks Prancis, user lain tetap lihat Inggris) — cuma MEKANISME internalnya yang diganti dari "translated-field storage" (butuh `res.lang` terinstall) jadi "pilih string langsung" (tidak butuh apa-apa), pola yang sudah ada persis sama di baris 33-37 file yang sama.
**Verifikasi:** Re-run test suite penuh TANPA `--load-language=fr_FR` sama sekali (docker-compose standar, tidak pernah install bahasa apapun) — **`0 failed, 0 error(s) of 22 tests`** (turun dari "1 error" sebelumnya). Semua 4 Tour test tetap "tour succeeded", tidak ada regresi.
**Status:** ✅ **RESOLVED** — bukan lagi item yang perlu dikonfirmasi ke dev sebelum go-live; modul sekarang berfungsi identik terlepas apakah Prancis terinstall atau tidak.
**Keputusan pemilik modul:** ✅ Dev memilih fix kode (2026-08-26) — lihat "Keputusan dev" di atas.

---

### MF-22 — `pin_message/chatter.js` `load()` full-override memanggil service yang sudah tidak ada — RESOLVED
**Ditemukan di:** Step 6 (2026-08-24), lewat Tour test nyata (Mode D) — `TypeError: Cannot read properties of undefined (reading 'fetchData')` tepat setelah klik "Log note"
**Tag:** `[GAP-MIGRASI]`
**Prioritas:** **Tinggi** — crash total begitu chatter mount (bukan cuma fitur pin, SELURUH chatter modul manapun yang render lewat `initialLoad()` modul ini)
**Lokasi:** `pin_message/static/src/js/chatter.js` (method `load()`)
**Deskripsi:** Sama pola dengan `MF-15`/`MF-19`/`MF-20` (`pos_margin_threshold`) — modul ini FULL-OVERRIDE `Chatter.prototype.load(thread, requestList)` (bukan extend) untuk menyisipkan `messageFields: ['is_pinned']` sebagai argumen ke-3 (`options`) ke `this.threadService.fetchData(thread, requestList, options)`. Di 18.0: (1) tidak ada lagi property `this.threadService` pada Chatter (dikonfirmasi baca source `chatter.js`/`thread_model_patch.js` container — `fetchData` sekarang milik objek `thread` itu sendiri, dipanggil `thread.fetchData(requestList)`), (2) `fetchData()` cuma menerima SATU argumen (`requestList`, daftar KATEGORI data seperti "messages"/"activities" — bukan daftar NAMA FIELD custom).
**Dampak:** Fatal — `this.threadService` selalu `undefined`, method crash SETIAP KALI chatter mount pertama kali (`onMounted → initialLoad → load`), sebelum user sempat berinteraksi apapun.
**Status:** ✅ **RESOLVED dan TERVERIFIKASI** — override `load()` dihapus total (modul ini tidak perlu override `load()` sama sekali lagi, lihat `MF-23` untuk mekanisme pengganti field custom). Dikonfirmasi Tour test `pin_message_toggle_pin_tour` — "tour succeeded".
**Keputusan pemilik modul:** Tidak perlu — perbaikan wajib kompatibilitas (API lama dihapus total).

---

### MF-23 — Field custom (`is_pinned`) butuh `mail.message._to_store()`, bukan lagi field-list di `Chatter.load()` — RESOLVED
**Ditemukan di:** Step 6 (2026-08-24), sambungan investigasi `MF-22` — dicek `_to_store()` di source `mail_message.py` container untuk cari mekanisme pengganti
**Tag:** `[GAP-MIGRASI]`
**Prioritas:** Tinggi (silent — field tidak pernah sampai ke frontend, tidak ada error, fitur cuma "tidak bekerja")
**Lokasi:** `pin_message/models/mail_message.py` (method baru `_to_store()`)
**Deskripsi:** Pola SAMA seperti `MF-18` (POS `_load_pos_data_fields`) tapi di area `mail`: field custom yang perlu dikirim ke frontend sekarang WAJIB didaftarkan lewat override `_to_store(self, store, /, **kwargs)` per-model (di sini `mail.message`), memanggil `store.add(message, {field: value})` — BUKAN lagi lewat parameter field-list di sisi client (`Chatter.load()`, sudah dihapus di `MF-22`). Tanpa fix ini, `is_pinned` tidak akan pernah muncul di data message yang dikirim ke JS, walau field-nya ada di database.
**Dampak:** Sebelum fix ini digabung dengan `MF-22`, section "Pinned Messages" akan selalu kosong (badge count `0`) walau ada pesan yang `is_pinned=True` di database — silent, tidak ada error apapun.
**Status:** ✅ **RESOLVED dan TERVERIFIKASI** — `mail.message._to_store()` di-extend (`super()._to_store(store, **kwargs)` lalu `store.add(message, {'is_pinned': message.is_pinned})` per message). Dikonfirmasi Tour test: badge muncul benar dengan angka 1 setelah pin, section menampilkan pesan yang benar, badge kembali kosong setelah unpin.
**Keputusan pemilik modul:** Tidak perlu — perbaikan wajib kompatibilitas, field yang di-expose sama persis dengan 17.0.

---

### MF-24 — `pinMessage.js`: `component.canAddReaction` getter dipindah jadi method `message.canAddReaction(thread)` — action "pins" selalu `false` — RESOLVED
**Ditemukan di:** Step 8 (2026-08-24), Code Review — ditemukan dari pembacaan kode langsung (bukan dari Tour test, yang tidak pernah menyentuh jalur ini sejak awal ditulis lewat tombol inline `pinnedMessages.xml`, bukan action-menu)
**Tag:** `[GAP-MIGRASI]`
**Prioritas:** **Tinggi** — silent, tidak ada error, entry menu "Pin" (action registry `messageActionsRegistry`) tidak PERNAH muncul untuk pesan manapun, di kondisi manapun, sejak awal migrasi
**Lokasi:** `pin_message/static/src/js/pinMessage.js:8` (callback `condition` di `messageActionsRegistry.add("pins", ...)`)
**Deskripsi:** Kode (diwarisi apa adanya dari 17.0) memanggil `component.canAddReaction` sebagai property/getter langsung di Owl component `Message`. Dikonfirmasi baca source core langsung (`docker run --rm pos_margin_sale_migration_18-odoo:latest`): di 17.0 `canAddReaction` memang getter di `Message` component (`core/common/message.js`); di 18.0 getter ini DIHAPUS dari component, dipindah jadi METHOD di message MODEL: `message.canAddReaction(thread)` (`core/common/message_model.js:450`) — core sendiri memanggilnya lewat `component.props.message.canAddReaction(component.props.thread)` (`core/common/message_actions.js:53`, entry registry "add-reaction" milik core). Karena `component.canAddReaction` (property langsung di component) selalu `undefined` di 18.0, `!component.canAddReaction` selalu `true` → `condition` SELALU return `false`.
**Dampak:** Entry menu "Pin" (ikon thumbtack di action bar pesan, sequence 15) tidak pernah render untuk pesan manapun — tapi tour test yang sudah ada (`pin_message_toggle_pin_tour`) tidak pernah menangkap ini karena tour tsb sengaja pakai tombol inline (`pinnedMessages.xml`, method `onMessagePin()`, jalur terpisah yang tidak lewat registry ini) — dipilih saat penulisan tour justru karena action-menu button "tidak pernah ketemu/timeout" (lihat `06c_IMPLEMENTATION_LOG.md` `pin_message` Fase E/F), yang saat itu disangka flakiness timing Tour, padahal akar masalahnya tombolnya memang tidak pernah dirender sama sekali oleh aplikasi, di context manapun.
**Status:** ✅ **RESOLVED dan TERVERIFIKASI** — `condition` diubah jadi `component.message.canAddReaction(component.props.thread)` (mengikuti persis idiom core sendiri; `component.message` adalah getter yang sudah ada dan tetap valid di 18.0, `return this.props.message`). Re-run test suite penuh setelah fix: kedua Tour test (`pos_margin_threshold`, `pin_message`) tetap "tour succeeded", `0 failed, 1 error(s) of 19 tests` (1 error tetap `MF-21`, tidak terkait).
**Keputusan pemilik modul:** Tidak perlu — perbaikan wajib kompatibilitas (API getter→method core), bukan perubahan behavior yang disengaja.

---

## Cara Pakai

1. Update SETIAP KALI step manapun (1-11), modul manapun, menemukan gap/bug/ambiguitas yang butuh
   keputusan manusia — jangan tunggu akhir project.
2. Tag: `[PERLU-KEPUTUSAN]` / `[DIWARISI-SOURCE]` (termasuk pewarisan dari `doc-dev/backfill/F-NNN`)
   / `[GAP-MIGRASI]` (genuinely muncul karena perubahan platform 18.0).
3. Step 4 dan Step 8 (tiap modul) WAJIB baca file ini sebagai bagian gate.
4. Update status (bukan hapus) begitu keputusan diambil — tandai `✅ RESOLVED`/`✅ CONFIRMED` + tanggal
   + bukti.
