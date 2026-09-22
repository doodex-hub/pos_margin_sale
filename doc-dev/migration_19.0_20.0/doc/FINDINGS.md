# Findings — pos_margin_threshold / sale_margin_threshold / pin_message (migrasi 19.0 → 20.0)

> Cross-cutting, satu file untuk ketiga modul (lihat CLAUDE.md §"Adaptasi multi-modul"). Prefix
> judul finding dengan nama modul. Lihat `migration-tool/templates/FINDINGS.md` untuk beda peran
> file ini dari tag `[GAP]`/format `ESCALATION`, skema ID `MF-NNN`, dan cara pakai lengkap.

**Modul:** pos_margin_threshold, sale_margin_threshold, pin_message
**Migrasi:** 19.0 → 20.0
**Terakhir update:** 2026-09-21 (Step 2 — Diff & Compatibility Analysis, ketiga modul)

---

## Ringkasan

| ID | Judul | Ditemukan di Step | Tag | Prioritas | Status |
|---|---|---|---|---|---|
| MF-20 | [sale_margin_threshold] `security/groups.xml` `implied_ids` diisi kategori bukan grup | Dibawa dari project 18.0→19.0, Step 8 | `[DIWARISI-SOURCE]` | Sedang | 🔵 Terbuka — belum ada keputusan user |
| MF-21 | [sale_margin_threshold] `_compute_warning` (`is_less_minimum_sale`) tanpa `@api.depends` | Dibawa dari project 18.0→19.0, Step 8 | `[DIWARISI-SOURCE]` | Sedang | 🔵 Terbuka — belum ada keputusan user |
| MF-23 | [pos_margin_threshold] `_compute_warning` (`is_less_minimum_sale`), instance terpisah dari MF-21 | Dibawa dari project 18.0→19.0, Step 8 | `[DIWARISI-SOURCE]` | Sedang | 🔵 Terbuka — belum ada keputusan user |
| MF-24 | [pos_margin_threshold] `list_price` di-`position="replace"` bukan `attributes`, diam-diam menghapus atribut core (§Detail: ada instance KEDUA baru ditemukan Step 1) | Dibawa dari project 18.0→19.0, Step 8 | `[DIWARISI-SOURCE]` | Sedang | 🔵 Terbuka — belum ada keputusan user |
| MF-08 | [sale_margin_threshold] `action_confirm()` singleton-assumption — **mekanisme dikoreksi Step 1: hard crash, bukan silent skip** | Dibawa dari project 17.0→18.0, dikonfirmasi tetap ada di 18.0→19.0, mekanisme dikoreksi Step 1 project ini | `[DIWARISI-SOURCE]` | Tinggi | 🔵 Terbuka — **[KEPUTUSAN USER 2026-08-27, project 18.0→19.0]: dipertahankan**, jangan diperbaiki tanpa keputusan baru |
| MF-25 | [pos_margin_threshold] Instance KEDUA `position="replace"` (pola sama `MF-24`) di `lst_price`, `product_variant_easy_edit_view_margin_sale` — belum pernah dicatat | Step 1, project 19.0→20.0 (2026-09-21) | `[DIWARISI-SOURCE]` | Sedang | 🔵 Terbuka — baru ditemukan, belum ada keputusan user |
| MF-26 | [sale_margin_threshold] Singleton-assumption bug KEDUA (beda method dari `MF-08`) di `_compute_is_rental_order_installed` | Step 1, project 19.0→20.0 (2026-09-21) | `[DIWARISI-SOURCE]` | Sedang | 🔵 Terbuka — baru ditemukan, belum ada keputusan user |
| MF-27 | [sale_margin_threshold] `position="replace"` pada `list_price`/`lst_price` (pola sama `MF-24`/`MF-25`, modul berbeda) — belum pernah dicatat | Step 1, project 19.0→20.0 (2026-09-21) | `[DIWARISI-SOURCE]` | Sedang | 🔵 Terbuka — baru ditemukan, belum ada keputusan user |
| MF-28 | [pin_message] native 20.0 `mail.message` tidak punya `_to_store()` lagi — diganti `_store_message_fields()`/`res.attr("is_pinned")` | Step 1, solusi Step 2, **diterapkan & diverifikasi 2026-09-22** | `[GAP-MIGRASI]` | Tinggi | ✅ RESOLVED — `is_pinned` dikonfirmasi tersimpan+toggle benar via UI nyata |
| MF-29 | [pos_margin_threshold][sale_margin_threshold] view `product.product_variant_easy_edit_view` DIHAPUS TOTAL di native 20.0 — **keputusan desain SUDAH DIAMBIL dev**: pindah ke kolom baru di `product_product_tree_view` (list Product Variants, native 20.0 sudah `editable="bottom"`/`multi_edit="1"`) | Step 2, project 19.0→20.0 (2026-09-21) | `[GAP-MIGRASI]` | Tinggi | 🟡 Keputusan diambil (2026-09-21) — siap dieksekusi Step 3/6, plus item review visual Step 10 |
| MF-30 | [pos_margin_threshold][sale_margin_threshold] `ir.model.access.csv`→`ir.access.csv` — model lama dihapus total, kedua modul akan gagal install kalau tidak direname+reformat | Step 2, project 19.0→20.0 (2026-09-21) | `[GAP-MIGRASI]` | Tinggi | 🟡 Fix mekanis diketahui — rename file + reformat 1 baris ke skema `operation`/`domain` |
| MF-31 | [pos_margin_threshold] Anchor inherit `stock_account.view_category_property_form_stock` pindah jadi `account.view_category_property_form` | Step 2, project 19.0→20.0 (2026-09-21) | `[GAP-MIGRASI]` | Sedang | 🟡 Fix mekanis diketahui — ganti `ref=` satu baris, field target tidak berubah |
| MF-32 | [pin_message] `messageActionsRegistry` berubah lagi di 20.0 — 3 breaking point (getter `canAddReaction`, filter `IS_ACTION_DEFINITION_SYM`, FontAwesome→Odoo Icons `push_pin`) | Step 2, **diterapkan & diverifikasi 2026-09-22** | `[GAP-MIGRASI]` | Tinggi | ✅ RESOLVED — action "Pin" dikonfirmasi muncul+berfungsi via UI nyata (badge count benar) |
| MF-33 | [pin_message] Crash `Chatter`/`Message` di 20.0 — 3 lapis bug (import path lama, bare identifier tidak auto-resolve ke `this.xxx` di node `t-inherit-mode="extension"`, dan salah ketik `--` di komentar XML) — **SEMUA DIPERBAIKI & DIVERIFIKASI** (2026-09-22) | Step 2 (risiko teoretis), 3 crash nyata ditemukan+diperbaiki via smoke-test Docker 2026-09-22 | `[GAP-MIGRASI]` | Tinggi | ✅ RESOLVED — diverifikasi bersih di browser (0 error console terkait modul) |
| MF-34 | [pos_margin_threshold] `line.comboParent` (styling combo di `orderline.xml`) kemungkinan sudah jadi no-op — TIDAK bisa dipastikan murni gap 19→20 karena `native-source` (`enterprise19.0`) ternyata folder KOSONG di disk | Step 2, project 19.0→20.0 (2026-09-21) | `[PERLU-KEPUTUSAN]` | Rendah | 🔵 Terbuka — blocker infrastruktur (native-source kosong), bukan cuma keputusan konten |
| MF-35 | [sale_margin_threshold] `price_unit` di list `sale.order` dibungkus `<column name="price_unit">` baru di native 20.0 (sengaja — komentar native eksplisit sebut modul seperti `sale_margin`) — xpath lama tidak resolve, install-blocking. Tidak ketahuan di Step 2/3 (file `views/sale_order.xml` tidak eksplisit dicek), baru ketemu dari smoke-install Docker nyata | Ditemukan dari smoke-install Docker 20.0, 2026-09-22 (di luar Step 2/3 formal) | `[GAP-MIGRASI]` | Tinggi | ✅ RESOLVED (2026-09-22) — xpath diupdate, install sukses dikonfirmasi |
| MF-36 | [pin_message] Crash di komponen **native** `mail.MessageCardList` (BUKAN kode modul ini) saat expand section "Pinned Messages" — `ctx['ui'].isSmall` tidak resolve ke `ctx['this'].ui.isSmall` untuk baris pertama setelah `t-foreach` masuk scope, padahal baris kedua di file yang sama resolve benar. Toggle pin sendiri (badge count) SUDAH terbukti berfungsi — ini murni soal expand-view | Ditemukan smoke-test Docker 20.0, 2026-09-22, saat verifikasi `MF-28`/`MF-32` | `[GAP-MIGRASI]` | Sedang | 🔴 Terbuka — kemungkinan bug/quirk native Odoo 20.0 dev-snapshot, di luar kendali modul ini |

---

## Detail

### MF-20 — `security/groups.xml` implied_ids salah tipe
**Ditemukan di:** Step 8, project 18.0→19.0 (2026-08-27) — dibawa masuk mentah ke project ini, belum
diverifikasi ulang terhadap 20.0.
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `08_CODE_REVIEW.md` (project 18.0→19.0, `doc-dev/migration_18.0_19.0/doc/08_review/`)
**Lokasi:** `sale_margin_threshold/security/groups.xml` — `implied_ids` diisi ID kategori, bukan ID
grup (kemungkinan salah tempel `category_id`).
**Deskripsi:** pre-existing sejak sebelum migrasi 19.0, bukan gap baru akibat migrasi. Harus
dipertahankan identik di 20.0 kecuali user memutuskan sebaliknya di project ini.
**Dampak:** belum diukur — kemungkinan `implied_ids` jadi inert/silent no-op.
**Keputusan pemilik modul:** *(kosong — belum diputuskan, dibawa dari project sebelumnya)*

### MF-21 — `_compute_warning` (`sale_margin_threshold`) tanpa `@api.depends`
**Ditemukan di:** Step 8, project 18.0→19.0 (2026-08-27)
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `08_CODE_REVIEW.md` (project 18.0→19.0)
**Lokasi:** `sale_margin_threshold` — method `_compute_warning` (`is_less_minimum_sale`) tidak
punya `@api.depends`, sehingga tidak auto-recompute saat field dependency berubah.
**Deskripsi:** pre-existing, instance terpisah dari `MF-23` di modul lain.
**Keputusan pemilik modul:** *(kosong — belum diputuskan, dibawa dari project sebelumnya)*

### MF-23 — `_compute_warning` (`pos_margin_threshold`) tanpa `@api.depends`
**Ditemukan di:** Step 8, project 18.0→19.0 (2026-08-27)
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `08_CODE_REVIEW.md` (project 18.0→19.0)
**Lokasi:** `pos_margin_threshold` — method `_compute_warning` (`is_less_minimum_sale`), instance
terpisah (duplikat pola) dari `MF-21`.
**Keputusan pemilik modul:** *(kosong — belum diputuskan, dibawa dari project sebelumnya)*

### MF-24 — `list_price` view `position="replace"` menghapus atribut core diam-diam
**Ditemukan di:** Step 8, project 18.0→19.0 (2026-08-27)
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `08_CODE_REVIEW.md` (project 18.0→19.0)
**Lokasi:** `pos_margin_threshold` — xpath ke field `list_price` pakai `position="replace"`, bukan
`position="attributes"`, sehingga menghapus atribut native (`options`/`optional`/
`decoration-muted`) tanpa disengaja.
**Dampak:** rawan pecah lebih parah lagi kalau native 20.0 menambah atribut baru ke elemen yang
sama — WAJIB dicek ulang di Step 2 (diff), bukan cuma dibawa asumsi aman.
**Update Step 1 (2026-09-21):** ada instance KEDUA pola yang sama, belum pernah dicatat sebelumnya —
lihat `MF-25`.
**Keputusan pemilik modul:** *(kosong — belum diputuskan, dibawa dari project sebelumnya)*

### MF-08 — `action_confirm()` singleton-assumption pecah di batch-confirm
**Ditemukan di:** project 17.0→18.0, dikonfirmasi ulang project 18.0→19.0 (blast radius sama, tidak
lebih parah), **mekanisme dikoreksi Step 1 project ini (2026-09-21)**
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `FINDINGS.md` project 18.0→19.0; `doc-dev/backfill/` (`F-05`, characterization test
17.0, dieksekusi live 2026-07-31 — sumber pelengkap yang belum pernah dirujuk eksplisit di dua
project migrasi sebelumnya) dan `sale_margin_threshold/tests/test_action_confirm.py` (masih ada di
repo, dikonfirmasi masih PASS/FAIL sesuai deskripsi baru di bawah)
**Lokasi:** `sale_margin_threshold` — override `action_confirm()`.
**Deskripsi (dikoreksi):** dokumentasi lama menyebut ini "silent validation skip" saat batch-confirm.
Bukti eksekusi nyata (backfill `F-05` + test yang masih ada di repo) menunjukkan ini genuinely
**hard crash** — `ValueError: Expected singleton` — bukan skip diam-diam. Blast radius juga lebih
luas dari perkiraan sebelumnya: memecahkan demo data `sale_stock` milik Odoo sendiri, bukan cuma
skenario custom.
**Keputusan pemilik modul:** **Dipertahankan** (keputusan user 2026-08-27, project 18.0→19.0: "biarkan
dulu, pastikan tercatat di finding"). Deskripsi mekanisme dikoreksi di atas, keputusan itu sendiri
TIDAK berubah — jangan diperbaiki di project ini tanpa keputusan baru eksplisit.

### MF-25 — `lst_price` view `position="replace"` di variant easy-edit (instance kedua `MF-24`)
**Ditemukan di:** Step 1, project 19.0→20.0 (2026-09-21)
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** pola identik `MF-24`, modul sama (`pos_margin_threshold`)
**Lokasi:** `pos_margin_threshold` — xpath ke field `lst_price` di
`product_variant_easy_edit_view_margin_sale`, pakai `position="replace"` bukan
`position="attributes"`.
**Deskripsi:** ditemukan saat menulis `01b_BASELINE_SPEC.md` Step 1 project ini — sudah ada sejak
project migrasi sebelumnya tapi belum pernah dicatat di `FINDINGS.md` manapun.
**Dampak:** sama seperti `MF-24` — menghapus atribut native diam-diam, rawan pecah lebih parah kalau
native 20.0 menambah atribut baru ke elemen yang sama.
**Keputusan pemilik modul:** *(kosong — baru ditemukan)*

### MF-26 — Singleton-assumption kedua di `_compute_is_rental_order_installed`
**Ditemukan di:** Step 1, project 19.0→20.0 (2026-09-21)
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** *(baru, tidak ada rujukan project sebelumnya)*
**Lokasi:** `sale_margin_threshold` — method `_compute_is_rental_order_installed`.
**Deskripsi:** pola bug yang sama dengan `MF-08` (asumsi singleton di method yang bisa dipanggil
batch) tapi di method berbeda — ditemukan saat cross-check baseline spec ke kode aktual.
**Dampak:** belum diukur skenario trigger konkretnya — perlu tes eksplisit di Step 5/9 kalau
diputuskan relevan.
**Keputusan pemilik modul:** *(kosong — baru ditemukan)*

### MF-27 — `list_price`/`lst_price` view `position="replace"` di `sale_margin_threshold`
**Ditemukan di:** Step 1, project 19.0→20.0 (2026-09-21)
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** pola identik `MF-24`/`MF-25`, modul berbeda (`sale_margin_threshold`)
**Lokasi:** `sale_margin_threshold` — xpath ke `list_price`/`lst_price`, pakai `position="replace"`.
**Deskripsi:** pola anti-pattern yang sama muncul independen di modul ini, belum pernah dicatat
sebelumnya walau sudah ada sejak project migrasi sebelumnya.
**Keputusan pemilik modul:** *(kosong — baru ditemukan)*

### MF-28 — `mail.message._to_store()` DIHAPUS TOTAL di native 20.0 (KRITIS)
**Ditemukan di:** Step 1, project 19.0→20.0 (2026-09-21), saat cross-check baseline spec `pin_message`
ke `native-target` (`odoo20/addons/mail/models/mail_message.py`)
**Tag:** `[GAP-MIGRASI]`
**Ref:** `knowledge/version-diffs/19-to-20.md` (belum ada entry ini — kandidat promosi, lihat
`migration-records/pos-margin-sale_19.0_20.0/SUMMARY.md`); `MF-14`/`MF-15`/`MF-18` (project
18.0→19.0) — fix `_to_store()` yang dilakukan di project itu (tambah parameter `fields`, lalu
`store.add_records_fields()`) sekarang jadi TIDAK RELEVAN karena method-nya sendiri hilang di 20.0.
**Lokasi:** `pin_message/models/mail_message.py` — override `_to_store()`.
**Deskripsi:** Odoo 20.0 core mengganti pola `_to_store()` dengan `_store_message_fields()` +
`Store.FieldList` (pola serializer field-list, bukan override method monolitik). Override modul ini
TIDAK BISA di-port mekanis (ganti signature saja) — perlu rewrite arsitektural mengikuti pola native
20.0 yang baru.
**Dampak:** **Tertinggi di seluruh project.** Kalau tidak diperbaiki, chatter/Discuss APAPUN yang
memuat pesan (bukan cuma fitur pin) berisiko pecah total begitu modul ini terinstall — sama seperti
blast radius `MF-14`/`MF-18` di migrasi sebelumnya, tapi sekarang akar masalahnya method hilang
total, bukan cuma signature berubah.
**Update Step 2 (2026-09-21) — SOLUSI DITEMUKAN:** native 20.0 punya pola pengganti
`_store_message_fields(self, res: Store.FieldList, **kwargs)` (`odoo20/addons/mail/tools/discuss.py`).
Ditemukan DUA modul native yang sudah pakai pola ini untuk kasus identik (tambah satu field boolean
ke store pesan): `odoo20/addons/rating/models/mail_message.py` dan
`odoo20/addons/im_livechat/models/mail_message.py`. Rewrite konkret untuk `pin_message`:
```python
def _store_message_fields(self, res, **kwargs):
    super()._store_message_fields(res, **kwargs)
    res.attr("is_pinned")
```
Ini LEBIH SEDERHANA dari pola `store.add_records_fields()` yang dipakai di 19.0 — bukan tebakan,
diverifikasi langsung dari 2 override native yang sudah berjalan. Detail lengkap:
`02_diff/pin_message/02_DIFF_ANALYSIS.md`.
**✅ RESOLVED 2026-09-22:** rewrite diterapkan persis seperti di atas
(`pin_message/models/mail_message.py`), modul di-update di Docker 20.0, dan **diverifikasi via UI
nyata** — tulis log note → klik tombol pin → `is_pinned` tersimpan dan section "Pinned Messages"
muncul dengan badge count benar. `store.py`/`_store_message_fields` genuinely mengirim field ini
ke frontend.
**Keputusan pemilik modul:** *(tidak perlu keputusan — solusi teknis, sudah diterapkan &
diverifikasi)*

### MF-29 — `product.product_variant_easy_edit_view` dihapus total di native 20.0 (KRITIS, lintas-modul)
**Ditemukan di:** Step 2, project 19.0→20.0 (2026-09-21), kedua agent `pos_margin_threshold` DAN
`sale_margin_threshold` menemukan ini secara independen — dikonsolidasikan di sini karena sama-sama
inherit view yang sama.
**Tag:** `[GAP-MIGRASI]`
**Ref:** `02_diff/pos_margin_threshold/02_DIFF_ANALYSIS.md` (`DIFF-03`),
`02_diff/sale_margin_threshold/02_DIFF_ANALYSIS.md` (`DIFF-08`); terkait `MF-25` (instance kedua
`position="replace"` yang justru hidup di view yang sekarang hilang ini).
**Lokasi:** kedua modul punya record XML yang `inherit_id`-nya menyasar
`product.product_variant_easy_edit_view` — dikonfirmasi TIDAK ADA di `odoo20` maupun `enterprise20`
(grep case-insensitive "easy_edit"/"easy.edit" di seluruh `.py`/`.xml`/`.js`, 0 match, termasuk
`stock_variant_easy_edit_view` milik core sendiri yang inherit view yang sama — juga dihapus, bukan
diretarget).
**Dampak:** kedua modul akan GAGAL INSTALL total di 20.0 kalau record ini diport apa adanya
(`inherit_id` tidak resolve). Kandidat pengganti terdekat: `product.product_normal_form_view` (form
penuh, bukan popup ringan) — TAPI ini keputusan desain, bukan port 1:1.
**Ditulis juga sebagai kandidat knowledge base ke**
`migration-tool/migration-records/pos-margin-sale_19.0_20.0/SUMMARY.md` karena kemungkinan besar
relevan untuk modul migrasi Odoo LAIN yang juga customize popup easy-edit produk.

**Update — Riset lanjutan & keputusan dev (2026-09-21):** dicek langsung ke
`odoo20/addons/product/views/product_views.xml:424-498` — Odoo 20.0 TIDAK sekadar menghapus popup,
tapi menggantinya: list "Product Variants" (`product_product_tree_view`, action yang sama,
`res_model=product.product`) sekarang `editable="bottom"` + `multi_edit="1"` (edit inline langsung
di list, bisa multi-select). Field `margin_sale`/`minimum_sale_price`/`is_less_minimum_sale` semuanya
sudah didefinisikan di model `product.product` (bukan field baru) — bisa langsung jadi kolom baru di
list yang sama.

**Keputusan dev (2026-09-21):**
1. **Setuju** pindah ke pendekatan kolom-di-list (bukan pindah ke form penuh) — **dicatat untuk
   review visual di Step 10** (bandingkan tampilan 19.0 popup vs 20.0 kolom list berdampingan, bukan
   cuma verifikasi fungsional).
2. Kolom `margin_sale`/`minimum_sale_price` pakai **`optional="show"`** (langsung tampil, sama
   seperti popup lama yang selalu tampil tanpa toggle — `optional="hide"` akan jadi downgrade
   visibilitas dibanding behavior 19.0).
3. Koordinasi lintas-modul (`MF-03`, sembunyikan field margin kalau `pos_margin_threshold` juga
   terinstall): pakai `invisible="module_pos_margin_threshold == True"` — pola yang SAMA PERSIS
   sudah dipakai (dan terbukti jalan) di `sale_margin_threshold/views/product_template_views.xml:13-20`
   untuk form produk penuh, tinggal direplikasi ke kolom list, bukan pola baru.

**Rekomendasi Step 3:** migration spec kedua modul menulis penggantian record
`product_variant_easy_edit_view_margin_sale` (inherit view yang sudah tidak ada) menjadi record baru
yang inherit `product.product_product_tree_view`, menambah kolom sesuai 3 poin keputusan di atas.
**Keputusan pemilik modul:** ✅ Diputuskan (2026-09-21) — lihat detail di atas.

### MF-30 — `ir.model.access.csv` → `ir.access.csv` (dua modul)
**Ditemukan di:** Step 2, `pos_margin_threshold` (`DIFF-01`) dan `sale_margin_threshold` (`DIFF-01`)
**Tag:** `[GAP-MIGRASI]`
**Ref:** `knowledge/version-diffs/19-to-20.md` (sudah ada entry general soal ini dari project
`optional_field_save`) — dikonfirmasi ulang di sini spesifik untuk kedua modul, termasuk bukti
langsung dari `odoo/tools/convert.py` bahwa nama model target ditentukan dari NAMA FILE, jadi file
lama akan mencoba `env['ir.model.access']` yang sudah tidak ada — tidak ada compat shim.
**Lokasi:** `pos_margin_threshold/security/ir.model.access.csv`,
`sale_margin_threshold/security/ir.model.access.csv`.
**Dampak:** install gagal total kalau tidak direname.
**Rekomendasi:** fix mekanis — rename file jadi `ir.access.csv`, reformat kolom `perm_read/write/create/unlink`
jadi satu kolom `operation` (kombinasi huruf `crud`) + kolom `domain` kosong. Bisa dieksekusi Step 6
tanpa perlu keputusan dev tambahan.
**Keputusan pemilik modul:** *(tidak perlu keputusan — fix mekanis)*

### MF-31 — Anchor `stock_account.view_category_property_form_stock` pindah
**Ditemukan di:** Step 2, `pos_margin_threshold` (`DIFF-02`)
**Tag:** `[GAP-MIGRASI]`
**Ref:** `02_diff/pos_margin_threshold/02_DIFF_ANALYSIS.md`
**Lokasi:** `pos_margin_threshold` — view yang inherit `stock_account.view_category_property_form_stock`.
**Deskripsi:** ID XML lama sudah tidak ada, penggantinya `account.view_category_property_form`
(`account/views/product_view.xml:116`) — field target (`property_cost_method`) tidak berubah.
**Rekomendasi:** fix mekanis — ganti `ref=` satu baris.
**Keputusan pemilik modul:** *(tidak perlu keputusan — fix mekanis)*

### MF-32 — `messageActionsRegistry` berubah lagi di 20.0 (3 breaking point)
**Ditemukan di:** Step 2, `pin_message`
**Tag:** `[GAP-MIGRASI]`
**Ref:** `02_diff/pin_message/02_DIFF_ANALYSIS.md`
**Lokasi:** `pin_message/static/src/js/pinMessage.js`.
**Deskripsi:** tiga breaking point konkret ditemukan: (1) `message.canAddReaction(thread)` jadi
getter tanpa argumen; (2) native sekarang memfilter entry registry lewat symbol privat
`IS_ACTION_DEFINITION_SYM` yang hanya terpasang lewat helper `registerMessageAction()` — panggilan
`messageActionsRegistry.add()` langsung akan DIAM-DIAM terfilter (tidak error, action cuma tidak
pernah muncul); (3) FontAwesome dihapus total dari template `mail` (0 match `fa fa-`), diganti Odoo
Icons — ikon pengganti yang benar sudah dikonfirmasi: `"push_pin"`.
**Dampak:** tanpa fix, action pin kemungkinan tidak muncul sama sekali di UI (silent, bukan crash) —
lebih berbahaya dari error karena tidak kelihatan saat testing sekilas.
**✅ RESOLVED 2026-09-22:** ketiga fix diterapkan (`registerMessageAction`, getter `canAddReaction`
tanpa parameter, icon `push_pin`) di `pinMessage.js`, plus `DIFF-04` (icon FA→`oi` di
`pinnedMessages.xml`, selector tour test di `pin_message_tour.js`). **Diverifikasi via UI nyata** —
tombol pin inline (`pinnedMessages.xml`) diklik, badge "Pinned Messages: 1" muncul benar.
**Keputusan pemilik modul:** *(tidak perlu keputusan — fix mekanis, sudah diterapkan &
diverifikasi bareng `MF-28`)*

### MF-33 — Arsitektur `Chatter` di-rewrite — CRASH NYATA dikonfirmasi (bukan cuma risiko re-trigger)
**Ditemukan di:** Step 2 (risiko teoretis), **dikonfirmasi crash nyata 2026-09-22** via smoke-test
manual Docker 20.0 (port 8078) — dicoba buka form Product baru DAN form Rental Order baru, keduanya
crash identik.
**Tag:** `[GAP-MIGRASI]`
**Ref:** `02_diff/pin_message/02_DIFF_ANALYSIS.md`; console browser (2026-09-22):
```
[error] The following modules are needed by other modules but have not been defined...: {0: @mail/chatter/web_portal/chatter}
[error] ...unmet dependencies...: {0: @pin_message/js/chatter}
[error] TypeError: Cannot read properties of undefined (reading 'length')
    at Chatter.template_mail_Chatter ...
```
**Lokasi:** `pin_message/static/src/js/chatter.js:4` —
`import { Chatter } from "@mail/chatter/web_portal/chatter";`
**Deskripsi:** path lama `@mail/chatter/web_portal/chatter` **TIDAK ADA SAMA SEKALI** di asset bundle
20.0 (dipindah ke `@mail/chatter/web_portal_project/chatter`, sudah diketahui sejak Step 2). Karena
modul JS ini gagal di-resolve, `patch(Chatter.prototype, ...)` di file ini patch ke `undefined` —
begitu komponen native `Chatter` benar-benar coba render (template mencoba akses properti pesan
pinned), terjadi `TypeError: Cannot read properties of undefined (reading 'length')`.
**Dampak (lebih parah dari perkiraan Step 2):** ini BUKAN cuma soal "chatter tidak update saat ganti
thread" — ini crash yang terjadi di **SETIAP render form apapun yang punya widget chatter**
(dikonfirmasi: form Product baru, form Sale/Rental Order baru — kemungkinan besar SEMUA form
standar Odoo, karena chatter ada di hampir semua business document). Untungnya non-fatal untuk
sisa form (Owl error boundary menahan crash di komponen Chatter saja, field lain di form tetap
berfungsi — dikonfirmasi `action_confirm()` Sale Order tetap jalan normal via RPC meski chatter
error terus muncul), tapi UX chatter/message panel genuinely rusak total di 20.0 selama file ini
belum diperbaiki.
**✅ RESOLVED 2026-09-22 — 3 bug lapis ditemukan dan diperbaiki semua, diverifikasi bersih:**

1. **Import path** (`chatter.js:4`) — diubah jadi
   `import { Chatter } from "@mail/chatter/web_portal_project/chatter";`. Diverifikasi via console
   browser: warning "module not defined"/unmet-dependency `@pin_message/js/chatter` hilang, asset
   bundle regenerate (hash `eb0cd74`→`65c0b38`).
2. **Bare identifier tidak auto-resolve ke `this.xxx` di node hasil `t-inherit-mode="extension"`**
   (root cause sebenarnya, ditemukan via `odoo.__WOWL_DEBUG__.root.__owl__.app.templates` — baca
   source function template hasil kompilasi langsung dari browser, bandingkan ke pola native yang
   SELALU eksplisit `this.xxx`):
   - `pinnedMessages.xml` (`mail.Chatter` extension): `pinnedMessages`/`state`/
     `togglePinnedMessages` dikompilasi jadi `ctx['pinnedMessages']` (lookup context biasa,
     `undefined`) bukan `ctx['this'].pinnedMessages` — diperbaiki jadi `this.pinnedMessages`/
     `this.state`/`this.togglePinnedMessages` di semua 6 titik pemakaian.
   - `pinnedMessages.xml` (`mail.Message` extension): pola identik untuk `props` — diperbaiki jadi
     `this.props.message...` di semua titik.
3. **Bug ketikan sendiri saat menulis komentar penjelasan fix #2** — komentar XML sempat memuat
   `--` (double-hyphen) yang tidak valid dalam XML comment, sempat merusak SELURUH asset bundle
   webclient (`Missing template: "web.WebClient"`) untuk seluruh database sampai diperbaiki (ganti
   ke tanda baca tanpa `--`). Pelajaran: hindari `--`/em-dash-style separator di komentar XML Odoo.

**Verifikasi akhir (browser tab baru, console bersih dari cache lama):** buka form Product (chatter)
— 0 error console selain `Service worker registration failed` (tidak terkait, gagal karena
localhost tanpa HTTPS, bukan bug modul). Scroll ke panel chatter — render sempurna, log message
("Product created", dst) tampil normal, tombol Send message/Log note/Activity berfungsi.
**Rekomendasi tersisa:** tour test "pindah thread" (rekomendasi asli finding ini) tetap disarankan
sebagai bagian Step 9 formal untuk verifikasi otomatis, meski verifikasi manual di atas sudah
cukup meyakinkan untuk menutup risiko utama finding ini.
**Keputusan pemilik modul:** *(tidak perlu keputusan — ketiga fix mekanis, sudah diterapkan dan
diverifikasi bersih via browser nyata)*

### MF-35 — `price_unit` dibungkus `<column>` baru di list `sale.order` native 20.0
**Ditemukan di:** smoke-install Docker 20.0 nyata (2026-09-22), BUKAN Step 2/3 formal — file
`views/sale_order.xml` tidak eksplisit masuk cakupan agent riset Step 2/3 untuk modul ini (celah
proses, dicatat supaya tidak terulang: Step 2 berikutnya harus eksplisit cek SEMUA file `views/*.xml`
satu per satu, bukan cuma yang "kelihatan berisiko" dari nama file).
**Tag:** `[GAP-MIGRASI]`
**Ref:** `odoo20/addons/sale/views/sale_order_views.xml:832-845` — komentar native persis:
*"price_unit is wrapped in a column so inheriting modules (e.g. sale_margin) can add fields to it
via position="inside" instead of replacing the price_unit field node."*
**Lokasi:** `sale_margin_threshold/views/sale_order.xml`, record `view_order_form_inherit_sale`.
**Deskripsi:** xpath lama `//page[@name='order_lines']/field[@name='order_line']/list/field[@name='price_unit']`
tidak resolve lagi karena `price_unit` sekarang anak dari `<column name="price_unit">` baru di dalam
`<list name="sol_list">`. Install gagal total (`ParseError`) sampai diperbaiki.
**Fix diterapkan (2026-09-22):** xpath diupdate jadi
`//page[@name='order_lines']/field[@name='order_line']/list[@name='sol_list']/column[@name='price_unit']/field[@name='price_unit']`
— dikonfirmasi resolve, install sukses (`SELECT state FROM ir_module_module` → `installed`, smoke-test
Docker 20.0 port 8078).
**Keputusan pemilik modul:** *(tidak perlu keputusan — fix mekanis, sudah diterapkan & diverifikasi)*

### MF-34 — `line.comboParent` kemungkinan no-op, blocker infrastruktur `native-source`
**Ditemukan di:** Step 2, `pos_margin_threshold`
**Tag:** `[PERLU-KEPUTUSAN]`
**Ref:** `02_diff/pos_margin_threshold/02_DIFF_ANALYSIS.md` (`DIFF-05`)
**Lokasi:** `pos_margin_threshold/static/src/xml/orderline.xml` — `line.comboParent` di ekspresi
`t-attf-class`.
**Deskripsi:** `comboParent` tidak match getter produksi manapun di 20.0 (cuma muncul sebagai nama
opsi test-helper) — styling combo-highlight kemungkinan sudah jadi no-op. **TIDAK bisa dipastikan
murni gap 19.0→20.0** karena `native-source` (`D:\Kuncoro\doodex\repo\enterprise19.0`, dikonfirmasi
di CLAUDE.md sebagai referensi 19.0) ternyata **folder KOSONG** di disk saat agent mengecek — tidak
bisa cross-check langsung ke kode 19.0 asli.
**Dampak:** rendah (styling saja, bukan fungsional), tapi finding ini butuh `native-source` terisi
ulang untuk verifikasi tuntas.
**Rekomendasi:** infrastruktur — minta dev refill `enterprise19.0` (re-extract/re-copy), atau
konfirmasi apakah folder itu memang sengaja dikosongkan. Setelah terisi, cross-check ulang baru bisa
menutup finding ini dengan pasti.
**Keputusan pemilik modul:** *(kosong — perlu tindakan infrastruktur dev dulu, bukan keputusan
konten)*

### MF-36 — Crash native `mail.MessageCardList` saat expand "Pinned Messages" (bukan bug modul ini)
**Ditemukan di:** smoke-test Docker 20.0, 2026-09-22, saat verifikasi end-to-end `MF-28`/`MF-32`
(toggle pin sendiri SUDAH terbukti berfungsi — badge count "Pinned Messages: 1" muncul benar begitu
pesan di-pin; crash ini baru terjadi saat mengklik header section untuk EXPAND daftar pesannya).
**Tag:** `[GAP-MIGRASI]`
**Ref:** console browser + `odoo.__WOWL_DEBUG__.root.__owl__.app.templates['mail.MessageCardList'].toString()`
(teknik debug yang sama dipakai `MF-33`):
```
TypeError: Cannot read properties of undefined (reading 'isSmall')
    at MessageCardList.template_mail_MessageCardList ...
```
Source kompilasi (dikonfirmasi 100% NATIVE, `pin_message` tidak pernah menyentuh
`message_card_list.js`/`.xml`):
```
5:const [k_block2, v_block2, l_block2, c_block2] = prepareList(ctx['this'].props.messages);;
...
11:let attr2 = {'opacity-100 py-1 px-2':ctx['ui'].isSmall};        // CRASH -- ctx['ui'] undefined
...
14:  let attr3 = {'fs-5':ctx['this'].ui.isSmall};                  // baris SERUPA, resolve BENAR
```
**Lokasi:** `odoo20/addons/mail/static/src/core/common/message_card_list.xml` (baris ~8, badge
"Jump") — file native, tidak dimodifikasi modul manapun.
**Deskripsi:** dua ekspresi `this.ui.isSmall` yang HAMPIR IDENTIK di file native yang sama
dikompilasi BERBEDA — satu (baris pertama setelah `t-foreach` masuk scope baru) jadi
`ctx['ui'].isSmall` (lookup context polos, `undefined`, CRASH), satu lagi (di dalam blok `t-if`
bersarang tepat setelahnya) jadi `ctx['this'].ui.isSmall` (benar). Ini BUKAN pola bug yang sama
dengan `MF-33` (yang ada di kode `pin_message` sendiri) — ini genuinely di kode native yang tidak
pernah disentuh modul manapun, kemungkinan besar quirk/bug compiler Owl (kombinasi
`useProps`/Owl 3 compatibility layer, lihat referensi `owl3_compatibility_layer.js` di stack trace)
pada snapshot dev 20.0 yang dipakai (`odoo20`, belum ada rilis resmi `odoo:20.0` di Docker Hub per
`knowledge/version-diffs/19-to-20.md`).
**Dampak:** fitur INTI (pin/unpin, badge count) tetap berfungsi penuh. Yang crash HANYA saat user
klik expand section "Pinned Messages" untuk melihat daftar pesannya — `MessageCardList` dipakai
modul ini apa adanya (`t-if="this.state.showPinnedMessages"` lalu render komponen native), tidak
ada workaround sisi modul yang jelas tanpa mengubah/patch file native (di luar scope migrasi
mekanis, dan berisiko besar men-patch komponen inti Discuss yang dipakai luas).
**Rekomendasi:** (1) uji ulang begitu image resmi `odoo:20.0` (rilis stabil, bukan dev-snapshot)
tersedia — kemungkinan bug ini sudah diperbaiki upstream sebelum rilis final; (2) kalau masih
terjadi di rilis stabil, ini keputusan/eskalasi terpisah untuk dev — apakah cukup laporkan sebagai
bug ke Odoo, atau perlu workaround sisi modul (mis. render list pesan pinned sendiri tanpa
`MessageCardList`, mengubah UI dari desain asli). **Jangan coba modifikasi file native
`message_card_list.xml`/`.js` untuk "fix" ini** — itu di luar scope perbaikan modul migrasi.
**Keputusan pemilik modul:** *(kosong — butuh keputusan setelah re-test di rilis 20.0 stabil, bukan
sesuatu yang bisa diputuskan sekarang dari dev-snapshot)*

---

## Cara Pakai

Sama seperti `migration-tool/templates/FINDINGS.md` — lihat file itu untuk skema `MF-NNN`, kapan
pakai `[PERLU-KEPUTUSAN]`/`[DIWARISI-SOURCE]`/`[GAP-MIGRASI]`, dan kewajiban Step 4/Step 8 membaca
file ini sebagai bagian gate. `MF-25`..`MF-36` sudah dipakai (`MF-25`..`MF-28` Step 1, `MF-29`..`MF-34`
Step 2, `MF-35`/`MF-36` smoke-test Docker 2026-09-22) — ID lanjutan finding BARU selanjutnya mulai dari
`MF-37`.
