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
| MF-28 | [pin_message] native 20.0 `mail.message` tidak punya `_to_store()` lagi — **solusi mekanis SUDAH DITEMUKAN Step 2** (`res.attr("is_pinned")` via `_store_message_fields()`, pola native `rating`/`im_livechat`) | Step 1, riset selesai Step 2 (2026-09-21) | `[GAP-MIGRASI]` | Tinggi | 🟡 Solusi ditemukan — siap diimplementasi Step 6, belum ada keputusan/eksekusi |
| MF-29 | [pos_margin_threshold][sale_margin_threshold] **KRITIS, install-blocking, dampak lintas-modul** — view `product.product_variant_easy_edit_view` DIHAPUS TOTAL di native 20.0, tidak ada pengganti senama | Step 2, project 19.0→20.0 (2026-09-21) | `[GAP-MIGRASI]` | **Tertinggi** | 🔴 Terbuka — butuh keputusan desain dev sebelum Step 3, bukan port mekanis |
| MF-30 | [pos_margin_threshold][sale_margin_threshold] `ir.model.access.csv`→`ir.access.csv` — model lama dihapus total, kedua modul akan gagal install kalau tidak direname+reformat | Step 2, project 19.0→20.0 (2026-09-21) | `[GAP-MIGRASI]` | Tinggi | 🟡 Fix mekanis diketahui — rename file + reformat 1 baris ke skema `operation`/`domain` |
| MF-31 | [pos_margin_threshold] Anchor inherit `stock_account.view_category_property_form_stock` pindah jadi `account.view_category_property_form` | Step 2, project 19.0→20.0 (2026-09-21) | `[GAP-MIGRASI]` | Sedang | 🟡 Fix mekanis diketahui — ganti `ref=` satu baris, field target tidak berubah |
| MF-32 | [pin_message] `messageActionsRegistry` berubah lagi di 20.0 — 3 breaking point konkret (getter `canAddReaction`, filter `IS_ACTION_DEFINITION_SYM`, FontAwesome→Odoo Icons `push_pin`) | Step 2, project 19.0→20.0 (2026-09-21) | `[GAP-MIGRASI]` | Tinggi | 🟡 Fix mekanis diketahui untuk ketiganya — lihat `02_DIFF_ANALYSIS.md` |
| MF-33 | [pin_message] Komponen `Chatter` di-rewrite arsitektural (Owl signals) + pindah path modul — patch modul ini secara statis masih valid tapi behavior re-trigger saat ganti thread BELUM bisa dipastikan dari baca kode saja | Step 2, project 19.0→20.0 (2026-09-21) | `[GAP-MIGRASI]` | Sedang | 🔴 Terbuka — WAJIB diverifikasi via tour test nyata di Step 6/9, jangan diasumsikan aman |
| MF-34 | [pos_margin_threshold] `line.comboParent` (styling combo di `orderline.xml`) kemungkinan sudah jadi no-op — TIDAK bisa dipastikan murni gap 19→20 karena `native-source` (`enterprise19.0`) ternyata folder KOSONG di disk | Step 2, project 19.0→20.0 (2026-09-21) | `[PERLU-KEPUTUSAN]` | Rendah | 🔵 Terbuka — blocker infrastruktur (native-source kosong), bukan cuma keputusan konten |

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
**Rekomendasi:** siap dieksekusi mekanis di Step 6, tidak perlu eskalasi lagi untuk bagian `_to_store()`
ini. Sisa risiko `pin_message` sekarang pindah ke `MF-32` (registry) dan `MF-33` (arsitektur Chatter).
**Keputusan pemilik modul:** *(tidak perlu keputusan — solusi teknis, tinggal dieksekusi Step 6)*

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
**Rekomendasi:** WAJIB diputuskan sebelum Step 3 menulis migration spec untuk bagian ini di kedua
modul — apakah customization margin dipindah ke form penuh, atau didesain ulang cara lain. Ditulis
juga sebagai kandidat knowledge base ke
`migration-tool/migration-records/pos-margin-sale_19.0_20.0/SUMMARY.md` karena kemungkinan besar
relevan untuk modul migrasi Odoo LAIN yang juga customize popup easy-edit produk.
**Keputusan pemilik modul:** *(kosong — butuh keputusan desain, bukan cuma konfirmasi)*

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
**Rekomendasi:** fix mekanis untuk ketiganya, gunakan `registerMessageAction()` helper native alih-alih
`.add()` langsung. Test tour lama (`pin_message_tour.js`) juga pakai selector
`.fa-thumb-tack`/`.fa-ellipsis-v` yang akan gagal match — perlu diupdate juga.
**Keputusan pemilik modul:** *(tidak perlu keputusan — fix mekanis, tapi WAJIB dikerjakan bareng
`MF-28` supaya action pin genuinely muncul)*

### MF-33 — Arsitektur `Chatter` di-rewrite, risiko re-trigger saat ganti thread
**Ditemukan di:** Step 2, `pin_message`
**Tag:** `[GAP-MIGRASI]`
**Ref:** `02_diff/pin_message/02_DIFF_ANALYSIS.md`
**Lokasi:** `pin_message/static/src/js/chatter.js` (patch `onWillUpdateProps`).
**Deskripsi:** komponen native `Chatter` dipindah dari `@mail/chatter/web_portal/chatter` ke
`@mail/chatter/web_portal_project/chatter` DAN di-rewrite pakai pola Owl signals/`propComputed`/
`useOnChange` — patch modul ini masih valid secara sintaks, tapi apakah logic re-trigger-nya
(berbasis `onWillUpdateProps`) masih genuinely jalan terhadap mekanisme deteksi ganti-thread yang
BARU tidak bisa dipastikan dari baca kode statis saja.
**Dampak:** kalau tidak jalan, kemungkinan chatter tidak update saat pindah dokumen/thread — perlu
dibuktikan lewat eksekusi nyata, bukan dianggap aman.
**Rekomendasi:** WAJIB ada tour test "pindah thread" eksplisit di Step 6/9 — jangan tutup finding ini
hanya dari review kode.
**Keputusan pemilik modul:** *(kosong — perlu bukti eksekusi Step 6/9, bukan keputusan dev)*

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

---

## Cara Pakai

Sama seperti `migration-tool/templates/FINDINGS.md` — lihat file itu untuk skema `MF-NNN`, kapan
pakai `[PERLU-KEPUTUSAN]`/`[DIWARISI-SOURCE]`/`[GAP-MIGRASI]`, dan kewajiban Step 4/Step 8 membaca
file ini sebagai bagian gate. `MF-25`..`MF-34` sudah dipakai (`MF-25`..`MF-28` Step 1, `MF-29`..`MF-34`
Step 2, 2026-09-21) — ID lanjutan finding BARU selanjutnya mulai dari `MF-35`.
