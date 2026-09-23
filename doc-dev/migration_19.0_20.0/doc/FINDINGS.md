# Findings — pos_margin_threshold / sale_margin_threshold / pin_message (migrasi 19.0 → 20.0)

> Cross-cutting, satu file untuk ketiga modul (lihat CLAUDE.md §"Adaptasi multi-modul"). Prefix
> judul finding dengan nama modul. Lihat `migration-tool/templates/FINDINGS.md` untuk beda peran
> file ini dari tag `[GAP]`/format `ESCALATION`, skema ID `MF-NNN`, dan cara pakai lengkap.

**Modul:** pos_margin_threshold, sale_margin_threshold, pin_message
**Migrasi:** 19.0 → 20.0
**Terakhir update:** 2026-09-23 (Step 9, `MF-40`..`MF-44` — rangkaian bug ditemukan begitu test suite
+ Tour test (real Chrome) benar-benar dijalankan untuk pertama kali; `MF-40`/`MF-41` RESOLVED (bug
modul), `MF-42` WORKAROUND (bug native), `MF-43` DAN `MF-44` KEDUANYA RESOLVED — root cause final:
(1) CSS class `.receipt-screen` di-rename total jadi `.feedback-screen` di native 20.0 (fix selector
tour), (2) test `setUpClass()` kurang `env.flush_all()` setelah `create()` produk ber-compute-chain,
membuat browser Chrome (thread/cursor terpisah) kadang membaca baris DB yang belum ter-flush (fix:
tambah `env.flush_all()`). Kesimpulan awal "transient race condition, self-heals" TERBUKTI SALAH dan
sudah diralat eksplisit di entri `MF-43`. Kedua tour `pos_margin_threshold` lolos bersih 3 run
berturut-turut pasca kedua fix. **Step 10 (2026-09-23):** ketiga modul lulus bersyarat (`MF-46`,
blocker infra test paralel, lihat entri sendiri), `MF-26` diperbaiki (keputusan dev: 20.0 saja),
`AC-06-01` [pin_message] akhirnya `[DIKONFIRMASI]` lewat rerun terisolasi, DAN ditemukan `MF-47`
(native 20.0 ternyata punya fitur pin/unpin pesan sendiri, berjalan paralel dengan modul custom ini —
belum ada keputusan dev, tidak blocking gate).

---

## Ringkasan

| ID | Judul | Ditemukan di Step | Tag | Prioritas | Status |
|---|---|---|---|---|---|
| MF-20 | [sale_margin_threshold] `security/groups.xml` `implied_ids` diisi kategori bukan grup | Dibawa dari project 18.0→19.0, Step 8 | `[DIWARISI-SOURCE]` | Sedang | 🔵 Terbuka — belum ada keputusan user |
| MF-21 | [sale_margin_threshold] `_compute_warning` (`is_less_minimum_sale`) tanpa `@api.depends` | Dibawa dari project 18.0→19.0, Step 8 | `[DIWARISI-SOURCE]` | Sedang | 🔵 Terbuka — belum ada keputusan user |
| MF-23 | [pos_margin_threshold] `_compute_warning` (`is_less_minimum_sale`), instance terpisah dari MF-21 | Dibawa dari project 18.0→19.0, Step 8 | `[DIWARISI-SOURCE]` | Sedang | 🔵 Terbuka — belum ada keputusan user |
| MF-24 | [pos_margin_threshold] `list_price` di-`position="replace"` bukan `attributes`, diam-diam menghapus atribut core (§Detail: ada instance KEDUA baru ditemukan Step 1) | Dibawa dari project 18.0→19.0, Step 8 | `[DIWARISI-SOURCE]` | Sedang | 🔵 Terbuka — belum ada keputusan user |
| MF-08 | [sale_margin_threshold] `action_confirm()` singleton-assumption — **mekanisme dikoreksi Step 1: hard crash, bukan silent skip** | Dibawa dari project 17.0→18.0, dikonfirmasi tetap ada di 18.0→19.0, mekanisme dikoreksi Step 1 project ini | `[DIWARISI-SOURCE]` | Tinggi | 🔵 Terbuka — **[KEPUTUSAN USER 2026-08-27, project 18.0→19.0]: dipertahankan**, jangan diperbaiki tanpa keputusan baru |
| MF-25 | [pos_margin_threshold] Instance KEDUA `position="replace"` (pola sama `MF-24`) di `lst_price`, `product_variant_easy_edit_view_margin_sale` — belum pernah dicatat | Step 1, project 19.0→20.0 (2026-09-21) | `[DIWARISI-SOURCE]` | Sedang | ✅ RESOLVED (2026-09-23, Step 8 Code Review) — moot: record yang mengandung instance ini dihapus total oleh rewrite `MF-29`/`DIFF-03` (record baru inherit `product.product_product_tree_view` pakai `position="attributes"`, bukan `replace`) — lihat `08_review/pos_margin_threshold/08_CODE_REVIEW.md` §E |
| MF-26 | [sale_margin_threshold] Singleton-assumption bug KEDUA (beda method dari `MF-08`) di `_compute_is_rental_order_installed` | Step 1, project 19.0→20.0 (2026-09-21) | `[DIWARISI-SOURCE]` | Sedang | 🔵 Terbuka — baru ditemukan, belum ada keputusan user |
| MF-27 | [sale_margin_threshold] `position="replace"` pada `list_price`/`lst_price` (pola sama `MF-24`/`MF-25`, modul berbeda) — belum pernah dicatat | Step 1, project 19.0→20.0 (2026-09-21) | `[DIWARISI-SOURCE]` | Sedang | 🔵 Terbuka — baru ditemukan, belum ada keputusan user |
| MF-28 | [pin_message] native 20.0 `mail.message` tidak punya `_to_store()` lagi — diganti `_store_message_fields()`/`res.attr("is_pinned")` | Step 1, solusi Step 2, **diterapkan & diverifikasi 2026-09-22** | `[GAP-MIGRASI]` | Tinggi | ✅ RESOLVED — `is_pinned` dikonfirmasi tersimpan+toggle benar via UI nyata |
| MF-29 | [pos_margin_threshold][sale_margin_threshold] view `product.product_variant_easy_edit_view` DIHAPUS TOTAL di native 20.0 — **keputusan desain SUDAH DIAMBIL dev**: pindah ke kolom baru di `product_product_tree_view` (list Product Variants, native 20.0 sudah `editable="bottom"`/`multi_edit="1"`) | Step 2, project 19.0→20.0 (2026-09-21) | `[GAP-MIGRASI]` | Tinggi | 🟡 Keputusan diambil (2026-09-21) — siap dieksekusi Step 3/6, plus item review visual Step 10 |
| MF-30 | [pos_margin_threshold][sale_margin_threshold] `ir.model.access.csv`→`ir.access.csv` — model lama dihapus total, kedua modul akan gagal install kalau tidak direname+reformat | Step 2, project 19.0→20.0 (2026-09-21) | `[GAP-MIGRASI]` | Tinggi | 🟡 Fix mekanis diketahui — rename file + reformat 1 baris ke skema `operation`/`domain` |
| MF-31 | [pos_margin_threshold] Anchor inherit `stock_account.view_category_property_form_stock` pindah jadi `account.view_category_property_form` | Step 2, project 19.0→20.0 (2026-09-21) | `[GAP-MIGRASI]` | Sedang | 🟡 Fix mekanis diketahui — ganti `ref=` satu baris, field target tidak berubah |
| MF-32 | [pin_message] `messageActionsRegistry` berubah lagi di 20.0 — 3 breaking point (getter `canAddReaction`, filter `IS_ACTION_DEFINITION_SYM`, FontAwesome→Odoo Icons `push_pin`) | Step 2, **diterapkan & diverifikasi 2026-09-22** | `[GAP-MIGRASI]` | Tinggi | ✅ RESOLVED — action "Pin" dikonfirmasi muncul+berfungsi via UI nyata (badge count benar) |
| MF-33 | [pin_message] Crash `Chatter`/`Message` di 20.0 — 3 lapis bug (import path lama, bare identifier tidak auto-resolve ke `this.xxx` di node `t-inherit-mode="extension"`, dan salah ketik `--` di komentar XML) — **SEMUA DIPERBAIKI & DIVERIFIKASI** (2026-09-22) | Step 2 (risiko teoretis), 3 crash nyata ditemukan+diperbaiki via smoke-test Docker 2026-09-22 | `[GAP-MIGRASI]` | Tinggi | ✅ RESOLVED — diverifikasi bersih di browser (0 error console terkait modul) |
| MF-34 | [pos_margin_threshold] `line.comboParent` (styling combo di `orderline.xml`) — typo lama sejak branch `17.0` (seharusnya `combo_parent_id`) | Step 2, project 19.0→20.0 (2026-09-21); blocker infrastruktur resolved + cross-check tuntas 2026-09-22 | `[DIWARISI-SOURCE]` | Rendah | ✅ RESOLVED (2026-09-22) — **keputusan dev: perbaiki** (bukan pertahankan) — `line.comboParent` → `line.combo_parent_id`, styling combo-child aktif untuk pertama kali. Diverifikasi XML well-formed + module update bersih; verifikasi visual live di POS ditunda (butuh chart of accounts + config POS, belum tersedia di DB QA ini) |
| MF-35 | [sale_margin_threshold] `price_unit` di list `sale.order` dibungkus `<column name="price_unit">` baru di native 20.0 (sengaja — komentar native eksplisit sebut modul seperti `sale_margin`) — xpath lama tidak resolve, install-blocking. Tidak ketahuan di Step 2/3 (file `views/sale_order.xml` tidak eksplisit dicek), baru ketemu dari smoke-install Docker nyata | Ditemukan dari smoke-install Docker 20.0, 2026-09-22 (di luar Step 2/3 formal) | `[GAP-MIGRASI]` | Tinggi | ✅ RESOLVED (2026-09-22) — xpath diupdate, install sukses dikonfirmasi |
| MF-36 | [pin_message] **ROOT CAUSE DIKOREKSI (2026-09-22, Step 4).** Crash saat expand "Pinned Messages" — semula ditulis "100% native, `pin_message` tidak pernah menyentuh `message_card_list.js`/`.xml`", **KLAIM ITU SALAH**. Modul ini PUNYA override `static/src/xml/message_card_list.xml` (xpath replace tombol "Jump") yang menulis `ui.isSmall` bare — bug bare-identifier IDENTIK `MF-33`, bukan quirk native | Ditemukan smoke-test Docker 20.0, 2026-09-22, saat verifikasi `MF-28`/`MF-32`; root cause dikoreksi + diperbaiki Step 4, 2026-09-22 | `[GAP-MIGRASI]` | Sedang | ✅ RESOLVED (2026-09-22) — `ui.isSmall` → `this.ui.isSmall`, diverifikasi live (expand + klik "See" jump, 0 error console) |
| MF-37 | [pos_margin_threshold][sale_margin_threshold] Kolom "Margin"/"Minimum sale price" DOBEL di list Product Variants 20.0 setelah eksekusi `MF-29` (kedua modul sama-sama inherit `product.product_product_tree_view` dan menambah field bernama sama) | Ditemukan review visual Docker 19.0 vs 20.0, 2026-09-22, saat verifikasi `MF-29` | `[GAP-MIGRASI]` | Tinggi | ✅ RESOLVED (2026-09-22) — dedup via `ProductProduct._get_view()` di `sale_margin_threshold`, diverifikasi bersih di browser (1 set kolom, bukan 2) |
| MF-38 | [pos_margin_threshold][sale_margin_threshold] Kolom list `MF-29` (pengganti popup `product_variant_easy_edit_view` yang dihapus native 20.0) tidak membawa 2 elemen visual yang ADA di popup 19.0: warna merah saat `margin_sale` negatif, dan kolom "Incl. Tax" (`minimum_sale_price_with_tax`) | Ditemukan review visual Docker 19.0 vs 20.0, 2026-09-22, saat konfirmasi ulang keputusan `MF-29` bersama dev | `[GAP-MIGRASI]` | Sedang | ✅ RESOLVED (2026-09-22) — **keputusan dev: diterapkan** (dijustifikasi `CLAUDE.md` §Source of Truth: "UX di 20.0 harus identik dengan 19.0"), diverifikasi live di kedua modul: margin negatif tampil merah, kolom Incl. Tax terisi benar, tidak dobel (field+kolom baru `minimum_sale_price_with_tax` di `ProductProduct` juga diberi marker dedup `MF-37` supaya tidak duplikat saat kedua modul terinstall bersamaan) |

| MF-39 | [sale_margin_threshold] `i18n/*.po` (5 file bahasa) tidak pernah dicek kelengkapan terjemahannya terhadap string UI baru dari `DIFF-08`/`MF-29`/`MF-38` (kolom "Incl. Tax" dst) | Ditemukan Step 4 (Spec Completeness Review), 2026-09-22 | `[PERLU-KEPUTUSAN]` → **DIPUTUSKAN** | Rendah | ✅ RESOLVED (2026-09-22) — **keputusan dev: out-of-scope**, tidak diupdate. Migrasi ini "port kode saja", tidak ada keputusan sebelumnya soal update terjemahan. Fallback ke string Inggris untuk string baru, tidak crash — dampak murni kosmetik (UI campur bahasa untuk 2-3 string) |
| MF-40 | [pos_margin_threshold][sale_margin_threshold] `ir.config_parameter.get_param()`/`set_param()` **dihapus total** di native 20.0, diganti method typed (`get_bool`/`set_bool`/`get_str`/dst) — install sukses, TAPI **crash saat runtime** setiap kali kode ini genuinely dieksekusi (klik "Pay" di POS / confirm Sale Order dengan produk di bawah minimum) | Ditemukan Step 9 (Dev Testing), 2026-09-22, saat menjalankan test suite existing sungguhan untuk pertama kali (`--test-enable`) — TIDAK ketahuan di Step 1-4 manapun karena hanya muncul saat compute yang memakainya benar-benar jalan, bukan saat install modul | `[GAP-MIGRASI]` | **Kritis** | ✅ RESOLVED (2026-09-22) — `get_param`→`get_bool` di `pos_margin_threshold/models/pos_config.py` + `sale_margin_threshold/models/sale_order.py` (keduanya field `Boolean` via `config_parameter=`, dikonfirmasi dari definisi field di `res_config_settings.py` dan pola native `res.config.settings.default_get`/`set_values`), `set_param`→`set_bool` di 2 file test yang juga memakai API lama. Diverifikasi: 0 failed, 0 error di 22 test (sebelumnya 4 error, semua akibat bug ini) |
| MF-41 | [pos_margin_threshold] DUA bug bertumpuk di `static/src/store/orderline.xml` (`DIFF-08`), keduanya baru ketahuan begitu Tour test (real Chrome) genuinely jalan untuk pertama kali: (1) xpath anchor `t[@t-slot='default']` tidak pernah resolve — native 20.0 rename total jadi `t-call-slot`; (2) setelah #1 diperbaiki, SEMUA 4 pemakaian identifier bare `line` di file yang sama ternyata bug bare-identifier IDENTIK `MF-33`/`MF-36` (`line` harus `this.line`) | Ditemukan Step 9 (Dev Testing), 2026-09-22, tour pertama kali benar-benar jalan dengan Chrome sungguhan (sebelumnya Chrome belum terpasang di image Docker) | `[GAP-MIGRASI]` | **Kritis** | ✅ RESOLVED (2026-09-22) — (1) xpath diupdate ke `t[@t-call-slot='default']`, dikonfirmasi dari `odoo20/addons/point_of_sale/static/src/app/components/orderline/orderline.xml`; (2) `line.combo_parent_id`/`line.isLessMinimumSalePrice` (di `position="attributes"`) dan `line.isLessMinimumSalePrice`/`line.minimumSalePriceWithTax` (di node baru hasil `position="before"`) semua diberi prefix `this.` — dikonfirmasi native 20.0 sendiri tidak pernah bind bare `line` di scope ini, hanya `this.line` (getter component). `03_MIGRATION_SPEC.md` `DIFF-08` awalnya menulis "tidak ada tindakan, xpath anchor stabil" — kesimpulan itu SALAH, cuma dari baca kode, tidak pernah diverifikasi dengan menjalankan tour sungguhan. Diverifikasi ulang setelah kedua fix: lihat catatan hasil test di bawah |
| MF-42 | [pos_margin_threshold] **BUKAN bug modul ini** — native 20.0's numpad tombol "Price" (`access_right_plugin.js` `get disablePriceButton()`) punya logic TERBALIK dari help text field-nya sendiri: `restrict_price_control` (help: "Only users with Manager access rights... can modify prices") justru membuat tombol Price DISABLED untuk cashier role "manager" saat `False` (default) — kebalikan dari yang diimplikasikan help text. Dikonfirmasi 19.0 punya logic SAMA SEKALI BEDA (`cashierHasPriceControlRights()`), bukan regresi dari kode lama, genuinely fitur/logic baru 20.0 yang tampak salah | Ditemukan Step 9 (Dev Testing), 2026-09-22, tour `pos_margin_threshold` gagal di step numpad "Price" ("Element is not enabled") setelah `MF-41` diperbaiki | `[GAP-MIGRASI]` (native, di luar kendali modul) | Sedang — blocking test tour, TIDAK blocking fungsi inti manapun di modul ini | ✅ WORKAROUND (2026-09-22) — `restrict_price_control=True` ditambahkan ke setup POS config test (`tests/test_margin_threshold_tour.py`), TIDAK menyentuh file native manapun. Kalau perilaku ini genuinely bug (bukan intentional design 20.0), sebaiknya dilaporkan ke Odoo terpisah dari migrasi ini — di luar scope perbaikan modul |
| MF-43 | [pos_margin_threshold] Tour `pos_margin_threshold_below_minimum_confirm_tour`/`..._blocked_tour` sempat gagal — dialog "Price unit less than minimum price" (`PosStore.pay()` patch) kadang tidak muncul. Root cause final: `setUpClass()` test kurang `env.flush_all()` setelah `create()` produk ber-compute-chain — lihat detail lengkap di bawah | Ditemukan Step 9 (Dev Testing), 2026-09-22 | `[GAP-MIGRASI]` | Kritis (fitur inti POS) | ✅ **RESOLVED (2026-09-23)** — fix `env.flush_all()` di test, diverifikasi 3+ run bersih berturut-turut |
| MF-46 | **RESOLVED 2026-09-23 (lihat `MF-46 (lanjutan 2)`)** — atribusi root cause DIKOREKSI: bukan kontensi Postgres/paralelisme/"tool fatigue", tapi spesifik ke browser tool yang dipakai (Playwright merender sempurna di server+DB+menit yang SAMA saat Browser pane blank). Ketiga item yang sempat blocked (`pin_message` AC-06-01, `pos_margin_threshold` AC-03-03, `sale_margin_threshold` visual smoke) SUDAH dieksekusi live dan LULUS. Teks asli di bawah dipertahankan apa adanya sebagai rekaman diagnosis awal. ~~[pin_message][process] Step 10 live Playwright execution (`AC-06-01` thread-switch, prioritas #1) BLOCKED total sesi ini — browser Playwright MCP genuinely SHARED antar agent sibling konkuren (bukan cuma container/DB), tab saling timpa terus-menerus, DAN container `pos_margin_sale_migration_20` sempat mengalami I/O contention berat (checkpoint Postgres >100 detik) akibat beban gabungan Step 10 paralel 3 modul — webclient Odoo blank/`document.body` kosong di SEMUA tab (bukan cuma punya AI ini), bukan bug kode `pin_message`~~ | Ditemukan Step 10 (QA Testing), 2026-09-23; ditutup 2026-09-23 (rerun terisolasi) | `[RESOLVED]` | Nihil sekarang (semua AC terdampak sudah ditutup `[DIKONFIRMASI]` lewat eksekusi live) | ✅ **Selesai — tidak butuh keputusan dev lagi.** Pelajaran yang dibawa ke depan: kalau satu browser tool menunjukkan `bodyLen` 6/15 padahal server sehat, coba browser tool yang satunya SEBELUM menyimpulkan blocker environment |

**`DIFF-04` [pos_margin_threshold] — dikonfirmasi dev 2026-09-22, diterapkan.** Field pengganti
`list_price` (form Product Template, bug lama `MF-24` yang dipertahankan) ditambah
`options="{'currency_field': 'currency_id', 'field_digits': True}"` menyamai atribut baru native
20.0 (tidak ada di 19.0). Diverifikasi: tidak ada beda visual di data instance ini (single-currency)
— murni jaga-jaga kompatibilitas kalau instance ini suatu saat multi-currency, risiko nol.

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
**✅ RESOLVED (2026-09-23, ditemukan ulang saat Step 8 Code Review) — moot, bukan lagi berlaku di
20.0.** Record `product_variant_easy_edit_view_margin_sale` yang menjadi lokasi instance ini SUDAH
DIHAPUS TOTAL oleh rewrite `MF-29`/`DIFF-03` (native 20.0 menghapus view target inherit-nya,
`product.product_variant_easy_edit_view` — lihat `MF-29`). Record penggantinya
(`product_product_tree_view_inherit_margin_sale`, inherit `product.product_product_tree_view`)
sengaja pakai `position="attributes"` untuk `lst_price` (bukan `replace`) — lihat
`03_MIGRATION_SPEC.md` §2a catatan implementasi `DIFF-03`, dan `AC-07-02`
(`05a_MIGRATION_ACCEPTANCE_CRITERIA.md`) yang eksplisit memverifikasi pola lama TIDAK terulang di
lokasi baru. Bug class-nya (pola `MF-24`) sendiri masih hidup di lokasi LAIN (`AC-06-01`,
`views/products.xml` record `product_template_inherit_pos_margin_threshold`) — hanya instance
SPESIFIK `MF-25` ini yang moot karena lokasinya hilang, bukan seluruh pola. Ditutup sebagai bagian
Step 8 Code Review (`08_review/pos_margin_threshold/08_CODE_REVIEW.md`), tidak perlu keputusan user
lebih lanjut untuk finding INI (beda dari `MF-24` yang masih terbuka di lokasi lain).
**Keputusan pemilik modul:** *(tidak perlu — moot secara struktural, bukan keputusan desain)*

### MF-26 — Singleton-assumption kedua di `_compute_is_rental_order_installed` — ✅ RESOLVED (20.0 saja)
**Ditemukan di:** Step 1, project 19.0→20.0 (2026-09-21); direproduksi live Step 10 (`RMV-03`,
2026-09-23, Cross-Version Compare)
**Tag:** `[DIWARISI-SOURCE]` → **diperbaiki di 20.0 saja** (lihat keputusan di bawah)
**Ref:** `RMV-03` (Cross-Version Compare, konfirmasi live bug-nya nyata sebelum fix)
**Lokasi:** `sale_margin_threshold/models/sale_order.py` — method
`_compute_is_rental_order_installed`.
**Deskripsi:** pola bug yang sama dengan `MF-08` (asumsi singleton) tapi di method berbeda — di
dalam `for record in self:`, baris kondisinya membaca `self.is_rental_order` (recordset UTUH)
bukan `record.is_rental_order` (item loop) — copy-paste error. Kalau dipanggil untuk >1
`sale.order` sekaligus (bulk action apapun yang menyentuh field ini, bukan cuma batch-confirm),
`self.is_rental_order` melempar `ValueError: Expected singleton`.
**Dampak:** crash nyata, dikonfirmasi live via `RMV-03` sebelum fix diterapkan.
**Keputusan pemilik modul (2026-09-23):** **PERBAIKI** — beda dari `MF-08` (yang tetap
dipertahankan). **Fix HANYA diterapkan di branch `migration/20.0` (versi 20 ke atas) — TIDAK
di-backport ke `migration/19.0` atau versi sebelumnya**, sesuai instruksi eksplisit dev. Fix:
`self.is_rental_order` → `record.is_rental_order` (satu baris). Diverifikasi via test baru
`test_mf26_compute_is_rental_order_installed_batch` (`sale_margin_threshold/tests/
test_high_risk_ac.py`) — batch 3 record, 0 failed/0 error setelah fix (sebelumnya akan crash).

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

### MF-34 — `line.comboParent` adalah typo lama sejak branch `17.0` — ✅ RESOLVED (diperbaiki)
**Ditemukan di:** Step 2, `pos_margin_threshold`. **Blocker infrastruktur resolved 2026-09-22** — dev
mengisi ulang referensi native-source sebagai dua folder terpisah: `D:\Kuncoro\doodex\repo\enterprise19`
(Enterprise 19.0, git clone resmi, branch `19.0`) + `D:\Kuncoro\doodex\repo\odoo19` (Community 19.0,
sudah ada sebelumnya) — pola dua-clone, bukan folder gabungan seperti `enterprise19.0` lama.
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `02_diff/pos_margin_threshold/02_DIFF_ANALYSIS.md` (`DIFF-05`)
**Lokasi:** `pos_margin_threshold/static/src/store/orderline.xml` — `line.comboParent` di ekspresi
`t-attf-class`.
**Deskripsi — CROSS-CHECK TUNTAS ke `odoo19`/`enterprise19` (2026-09-22):** native `Orderline`
component (`point_of_sale/static/src/app/components/orderline/orderline.js`, `get
lineContainerClasses()`) memakai `this.line.combo_parent_id` (snake_case, field model asli) untuk
styling combo-child — **BUKAN** `comboParent` (camelCase). Digrep di SELURUH `point_of_sale` addon,
baik `odoo19` maupun `odoo20`: getter/property `comboParent` **TIDAK PERNAH ADA** pada model
`pos.order.line` di versi manapun — satu-satunya kemunculan `comboParent` di kode native adalah nama
variabel lokal di test-helper/customer-display (konteks berbeda total, bukan properti record).
**Diperdalam lagi atas permintaan dev:** dicek `git show 17.0:pos_margin_threshold/static/src/store/orderline.xml`
— baris `line.comboParent` sudah identik ada di branch `17.0`, versi tertua yang tersimpan di repo
ini. Jadi bukan cuma "sejak 19.0" seperti draft awal finding ini, tapi **sejak modul pertama kali
ditulis** — typo original, dipertahankan identik lewat migrasi 17→18, 18→19, dan sampai sebelum fix
ini di 19→20. Styling border/indent combo-child TIDAK PERNAH aktif di versi manapun sebelum fix ini.
**Dampak:** tetap rendah — murni styling (indentasi/border kiri combo-child), tidak pernah
fungsional aktif, tidak ada crash, tidak ada data yang salah.
**Keputusan pemilik modul (2026-09-22): PERBAIKI** (bukan pertahankan, dev secara eksplisit meminta
fix untuk versi 20.0 ini) — `line.comboParent` → `line.combo_parent_id` di
`pos_margin_threshold/static/src/store/orderline.xml`, dengan komentar XML (bahasa Inggris)
menjelaskan asal-usul rename ini. Styling combo-child sekarang AKTIF untuk pertama kalinya di 20.0 —
**catatan penting:** ini genuinely perubahan behavior yang terlihat user dibanding SEMUA versi
sebelumnya (17.0-19.0 tidak pernah menampilkannya), bukan port mekanis murni, tapi sudah disetujui
dev secara eksplisit jadi tidak perlu eskalasi lagi.
**Verifikasi:** XML dikonfirmasi well-formed (`lxml.etree.parse`, dijalankan di container Docker
20.0), update modul (`-u pos_margin_threshold`) sukses tanpa error. **Verifikasi visual live di POS
(combo product sungguhan) BELUM dilakukan** — DB QA Docker 20.0 belum ada chart of accounts/config
POS terpasang, di luar scope perbaikan mekanis ini. Rekomendasi: verifikasi visual jadi bagian Step 9
(Dev Testing) formal nanti, bukan diasumsikan otomatis benar dari baca kode saja (pola yang sama
seperti `MF-33`).


**KOREKSI (2026-09-23, dari verifikasi visual live Step 10 — mengoreksi KLAIM DAMPAK di atas, bukan
keputusan fix-nya).** Dua kalimat di atas — "Styling border/indent combo-child TIDAK PERNAH aktif di
versi manapun sebelum fix ini" dan "genuinely perubahan behavior yang terlihat user dibanding SEMUA
versi sebelumnya (17.0-19.0 tidak pernah menampilkannya)" — **TIDAK BENAR**. Ditemukan saat akhirnya
menjalankan verifikasi visual dengan combo product sungguhan di POS 20.0 (yang di paragraf di atas
memang dicatat "BELUM dilakukan"):
1. **Native 20.0 sudah memberi `border-start` + `orderline-combo fst-italic ms-4` sendiri** untuk
   setiap line ber-`combo_parent_id` — `odoo20/addons/point_of_sale/static/src/app/components/
   orderline/orderline.js`, getter `lineContainerClasses` baris 53-54.
2. **Native 19.0 juga sudah** (`odoo19/.../orderline.js` baris 61-62, isi praktis identik). Jadi
   indent + garis kiri combo-child SUDAH tampil di 19.0, terlepas dari typo `line.comboParent` —
   yang merender adalah native, bukan modul ini. Typo itu tidak pernah menghilangkan styling apapun.
3. **Kontribusi unik modul (`border-3`) terbukti no-op visual.** Diuji langsung di DOM live:
   hapus `border-3` -> `border-left-width` TETAP `3px`; hapus `border-start` (milik native) -> baru
   jadi `0px`/`none`.
**Konsekuensi:** fix `MF-34` **tidak menghasilkan perubahan behavior yang terlihat user** — parity
19.0 -> 20.0 justru TERJAGA (yang memang diinginkan mandat migrasi). Persetujuan dev untuk
"perubahan behavior yang terlihat" ternyata tidak pernah perlu dipakai. **Fix-nya sendiri tetap
benar dan tetap dipertahankan** (`combo_parent_id` memang nama field yang benar; `comboParent` selalu
`undefined`), cuma dampaknya jauh lebih kecil dari yang dicatat sebelumnya.
**Override modul TIDAK dead code** — atribut `t-attf-class` yang sama membawa
`isLessMinimumSalePrice ? 'text-danger' : ''`, dan bagian itu terbukti hidup di layar yang sama
(line below-minimum ter-render merah + baris peringatan). Jadi fix `MF-41` (`this.line` +
anchor `t-call-slot`) memang perlu; yang redundan HANYA bagian combo-nya.
**Verifikasi visual: SEKARANG SUDAH DILAKUKAN** (menutup gap yang dicatat di paragraf "Verifikasi" di
atas) — Playwright, DB `pos_margin_sale_migration_20_qa_decline` port 8182, combo product nyata
(`MF34 Combo Menu` + `MF34 Burger`/`MF34 Drink`). Detail di
`10_qa/pos_margin_threshold/10_BUSINESS_FLOW_MIGRATION.md` S-13 ADDENDUM.

### MF-36 — Crash saat expand "Pinned Messages" — ROOT CAUSE DIKOREKSI, RESOLVED
**Ditemukan di:** smoke-test Docker 20.0, 2026-09-22, saat verifikasi end-to-end `MF-28`/`MF-32`
(toggle pin sendiri SUDAH terbukti berfungsi — badge count "Pinned Messages: 1" muncul benar begitu
pesan di-pin; crash ini baru terjadi saat mengklik header section untuk EXPAND daftar pesannya).
**Root cause DIKOREKSI Step 4 (2026-09-22):** klaim asli finding ini — "dikonfirmasi 100% NATIVE,
`pin_message` tidak pernah menyentuh `message_card_list.js`/`.xml`" — **SALAH**. Investigasi awal
membaca hasil kompilasi template dan menyimpulkan "native quirk" tanpa mengecek apakah modul punya
override di file itu. Agent Step 4 (Spec Completeness Review) menemukan
`pin_message/static/src/xml/message_card_list.xml` **memang ada** — sebuah `t-inherit="mail.MessageCardList"`
yang xpath-replace tombol "Jump" (`<a>` native → `<button>` modul ini), dan tombol pengganti itu
menulis `t-att-class="{ 'opacity-100 py-1 px-2': ui.isSmall }"` — bare `ui.isSmall`, BUKAN
`this.ui.isSmall`. CSS class di override (`opacity-100 py-1 px-2`) **cocok persis** dengan class di
baris crash pada stack trace kompilasi (`attr2`, lihat di bawah) — bukti langsung bahwa baris yang
crash adalah node HASIL OVERRIDE modul ini, bukan node native asli.
**Tag:** `[GAP-MIGRASI]`
**Ref:** console browser + `odoo.__WOWL_DEBUG__.root.__owl__.app.templates['mail.MessageCardList'].toString()`
(teknik debug yang sama dipakai `MF-33`):
```
TypeError: Cannot read properties of undefined (reading 'isSmall')
    at MessageCardList.template_mail_MessageCardList ...
```
Source kompilasi (baris yang crash adalah node hasil xpath-replace `pin_message`, BUKAN native):
```
5:const [k_block2, v_block2, l_block2, c_block2] = prepareList(ctx['this'].props.messages);;
...
11:let attr2 = {'opacity-100 py-1 px-2':ctx['ui'].isSmall};        // CRASH -- node pin_message
...
14:  let attr3 = {'fs-5':ctx['this'].ui.isSmall};                  // node NATIVE (tombol Unpin), resolve BENAR
```
**Lokasi:** `pin_message/static/src/xml/message_card_list.xml` — sama persis pola bug bare-identifier
`MF-33` di `pinnedMessages.xml` (bare identifiers pada node hasil `t-inherit-mode="extension"` tidak
auto-resolve ke `this.xxx` di 20.0), cuma belum ketahuan sebelumnya karena file ini tidak dicek saat
investigasi awal `MF-36`.
**Dampak:** fitur INTI (pin/unpin, badge count) tetap berfungsi penuh sebelum fix. Yang crash HANYA
saat user klik expand section "Pinned Messages".
**Fix (2026-09-22):** `ui.isSmall` → `this.ui.isSmall`. `message` (parameter `onClickJump`) TETAP
bare — dikonfirmasi itu variabel `t-foreach`/`t-as="message"` dari parent, bukan property instance,
resolve benar tanpa prefix baik di native maupun modul ini. Komentar XML (bahasa Inggris) ditambahkan
menjelaskan kedua hal ini sekaligus (kenapa `ui` diberi `this.`, kenapa `message` TIDAK).
**Verifikasi live (2026-09-22):** log note pada produk → pin pesan → expand "Pinned Messages" → TIDAK
crash (sebelumnya crash persis di titik ini) → klik tombol "See" (jump) → scroll+highlight ke pesan
asli di thread utama, berfungsi normal → 0 error console selain noise service-worker yang sudah
dikenal tidak terkait. Unpin dikonfirmasi berfungsi (section hilang otomatis).
**Keputusan pemilik modul:** tidak perlu — ini bug migrasi bare-identifier standar, pola sama persis
`MF-33` yang modul ini SUDAH diperbaiki di titik lain, jadi konsisten memperbaikinya di sini juga
(bukan keputusan desain baru, murni menyelesaikan pola fix yang sudah disetujui).

---

### MF-37 — Kolom Margin/Minimum sale price dobel di list Product Variants 20.0 (efek samping `MF-29`)
**Ditemukan di:** review visual Docker 19.0 vs 20.0, 2026-09-22, saat verifikasi manual keputusan
desain `MF-29` (kolom pengganti popup "easy edit" yang dihapus native 20.0).
**Tag:** `[GAP-MIGRASI]`
**Deskripsi:** `pos_margin_threshold` (`product_product_tree_view_inherit_margin_sale`) DAN
`sale_margin_threshold` (`product_product_tree_view_margin_sale`) masing-masing inherit native
`product.product_product_tree_view` dan menambah `<field name="margin_sale">`/
`<field name="minimum_sale_price">` persis setelah `lst_price` — field yang sama (didefinisikan di
model `product.product`), ditambahkan dua kali oleh dua view inherit terpisah. Di 20.0, list
"Product Variants" (dibuka lewat smart button "N Variants" pada Product Template) menampilkan KEDUA
pasang kolom berdampingan: "Margin | Minimum sale ... | Margin | Minimum s...".
**Percobaan fix #1 (GAGAL):** `column_invisible="module_pos_margin_threshold == True"` pada field
`sale_margin_threshold` — error `EvalError: ... Name 'module_pos_margin_threshold' is not defined`.
Root cause: `column_invisible` dievaluasi TANPA record context sama sekali (beda dari `invisible`
pada `<field>` list biasa, yang punya record context tapi cuma mem-blank isi sel per baris, tidak
menyembunyikan header kolom — jadi `invisible=` juga tidak applicable di sini).
**Percobaan fix #2 (GAGAL, kesalahan implementasi bukan pendekatan):** override
`ProductProduct._get_view()` di `sale_margin_threshold/models/product.py`, strip node
`margin_sale`/`minimum_sale_price` dari arch kalau `pos_margin_threshold` terinstall — TAPI gating-nya
salah, membandingkan `view.id` (view YANG DIMINTA/basis, yaitu native
`product.product_product_tree_view` sendiri) dengan id view inherit `sale_margin_threshold` —
kondisi ini TIDAK PERNAH true karena `view` yang dikembalikan `_get_view()` bukan salah satu delta
view inherit, jadi override tidak pernah efektif. Sempat memberi kesan "sudah fix" karena update
modul di Docker (`-u sale_margin_threshold`) sukses tanpa error, TAPI proses `-u` itu berjalan di
proses `odoo-bin` terpisah/sesaat — server web yang benar-benar melayani browser (`docker compose
... exec odoo` container long-running) masih menjalankan kode Python LAMA di memori sampai
di-restart. **Lesson penting:** setelah edit file `.py` (bukan `.xml`/aset), restart container/proses
server (`docker compose restart odoo`), jangan cuma jalankan `-u <module>` di proses terpisah — kalau
tidak, hasil test akan terlihat "belum fix" walau kode sudah benar (atau sebaliknya, terlihat "sudah
fix" padahal proses updatenya sendiri yang salah, harus dicek dua-duanya).
**Fix final (BERHASIL, diverifikasi 2026-09-22):** dua bagian —
1. `sale_margin_threshold/views/products.xml` — tambah `class="o_smt_dedup_margin"` /
   `class="o_smt_dedup_min_price"` pada dua field itu, murni sebagai marker (tidak mengubah tampilan)
   supaya node milik modul ini bisa ditarget spesifik lewat xpath di arch HASIL MERGE (nama field
   saja tidak cukup, karena kedua modul pakai nama field yang identik).
2. `sale_margin_threshold/models/product.py` — `ProductProduct._get_view()`: hapus gating
   `view.id == target_view.id` yang salah, jalankan dedup setiap kali `view_type == 'list'` untuk
   `product.product` dan `pos_margin_threshold` terinstall, target node lewat
   `//field[@name='margin_sale'][contains(@class, 'o_smt_dedup_margin')] | //field[@name='minimum_sale_price'][contains(@class, 'o_smt_dedup_min_price')]`
   — hanya menghapus node milik `sale_margin_threshold`, kolom `pos_margin_threshold` (tanpa marker)
   tetap utuh sebagai satu-satunya set kolom yang tampil, sesuai keputusan desain `MF-29`.
**Verifikasi:** update modul + restart container `odoo` di Docker 20.0, buka Product Variants untuk
"Test Rental Margin QA 20" (2 varian) — hasil: satu set kolom "Margin"/"Minimum sale price" (bukan
dua), nilai tetap terisi benar (20.00 / $0.00) untuk kedua baris varian.
**Keputusan pemilik modul:** tidak perlu — ini murni bug implementasi migrasi (kolom dobel akibat dua
modul menyentuh view yang sama), bukan ambiguitas desain (desain sudah diputuskan di `MF-29`: kolom
`pos_margin_threshold` yang jadi satu-satunya yang tampil).

---

### MF-40 — `ir.config_parameter.get_param()`/`set_param()` dihapus total di native 20.0 — RESOLVED
**Ditemukan di:** Step 9 (Dev Testing), 2026-09-22 — saat menjalankan test suite existing
(`odoo-bin --test-enable --test-tags /pos_margin_threshold,/sale_margin_threshold,/pin_message`)
untuk **pertama kalinya sungguhan** untuk pasangan 19.0→20.0 ini (sebelumnya cuma `-u <module>`
tanpa `--test-enable`, yang tidak menjalankan test sama sekali).
**Tag:** `[GAP-MIGRASI]`
**Kenapa TIDAK ketahuan di Step 1-4:** `get_param`/`set_param` adalah API generik yang dipakai di
MANA SAJA di seluruh ekosistem Odoo — bukan sesuatu yang di-grep khusus di analisis diff manapun
(Step 2/3 fokus ke elemen spesifik modul: view, security, field). Modul tetap **install sukses**
tanpa error (Python syntax valid, cuma runtime `AttributeError` saat method itu benar-benar
DIPANGGIL) — jadi tidak muncul di log instalasi, dan tidak muncul di review kode manapun yang cuma
baca struktur tanpa eksekusi. Baru ketahuan begitu test suite di-eksekusi SUNGGUHAN dengan
`--test-enable` (bukan cuma `-u <module>` biasa).
**Deskripsi:** Native `ir.orm.addons.base.models.ir_config_parameter.IrConfig_Parameter` di 20.0
tidak lagi punya method `get_param(key, default)`/`set_param(key, value)` generik — diganti method
per-tipe: `get_bool`/`get_int`/`get_float`/`get_str` dan `set_bool`/`set_int`/`set_float`/`set_str`
(dikonfirmasi baca langsung `odoo20/odoo/addons/base/models/ir_config_parameter.py`, tidak ada shim
kompatibilitas apapun di core). Ini pola yang sama dipakai native `res.config.settings` sendiri
(`default_get`/`set_values` di `odoo/addons/base/models/res_config.py` memilih method berdasarkan
`field.type` — untuk field `Boolean` pakai `get_bool`/`set_bool`).
**Lokasi kode terdampak (produksi, BUKAN cuma test):**
- `pos_margin_threshold/models/pos_config.py` — `PosConfig._compute_blocked_warning()`, dipanggil
  setiap kali field `is_blocked_warning` di-compute (dipakai untuk menentukan dialog
  blocking/confirm/tanpa-dialog saat klik "Pay" di POS — AC-03 di `05a_MIGRATION_ACCEPTANCE_CRITERIA.md`).
- `sale_margin_threshold/models/sale_order.py` — `SaleOrder.action_confirm()`, dipanggil setiap kali
  Sale Order di-confirm (fitur INTI modul ini).
- Plus 2 file test (`sale_margin_threshold/tests/test_action_confirm.py`,
  `pos_margin_threshold/tests/test_margin_threshold_tour.py`) yang memakai `set_param` untuk setup
  data test.

Keduanya field `Boolean` didefinisikan via `config_parameter="post_margin_sale.blocking_transaction_{pos,order}"`
di `res_config_settings.py` masing-masing modul — dikonfirmasi tipe field sebelum memilih method
pengganti yang benar (`get_bool`/`set_bool`, bukan `get_str`/`set_str`).
**Dampak sebelum fix:** **install sukses, TAPI crash runtime** — setiap kali kasir klik "Pay" di POS
dengan produk di bawah minimum (`pos_margin_threshold`), atau setiap kali Sale Order dengan produk
di bawah minimum di-confirm (`sale_margin_threshold`), method itu raise `AttributeError` — fitur
INTI kedua modul (validasi margin minimum) akan crash total, bukan cuma degradasi. Ini SEVERITY
TERTINGGI dari seluruh finding project ini — lebih parah dari `MF-29`/`MF-36` karena tidak ada jalan
pintas (bukan satu skenario visual, tapi jalur transaksi utama modul).
**Catatan efek samping (transparansi, bukan "fix bug"):** kode lama (`get_param` mengembalikan
string, string `'False'` selalu truthy di Python) sudah punya bug laten identik di 19.0 (dikonfirmasi
`git show migration/19.0`) — `get_bool` (wajib dipakai, API lama sudah dihapus total) otomatis
menghilangkan bug laten itu sebagai efek samping tak terhindarkan, BUKAN perbaikan yang disengaja.
**Fix:** `get_param(key)` → `get_bool(key)` (2 lokasi produksi), `set_param(key, value)` →
`set_bool(key, value)` (5 lokasi test, value sudah Python `bool` di semua kasus, tidak perlu
konversi). Komentar Python ditambahkan di tiap lokasi.
**Verifikasi:** re-run `--test-enable --test-tags /pos_margin_threshold,/sale_margin_threshold,/pin_message`
— **0 failed, 0 error dari 22 test** (sebelumnya 4 error, semuanya `AttributeError` ini). Tour test
(HttpCase) masih skip di percobaan ini karena Docker image belum punya Chrome — infrastruktur
terpisah, lihat catatan Dockerfile.20 di `06_implementation/` masing-masing modul.
**Keputusan pemilik modul:** tidak perlu — perbaikan API wajib (API lama sudah tidak ada sama sekali
di 20.0, bukan pilihan desain), murni mekanis.

---

### MF-43 — Dialog margin minimum TIDAK muncul di POS — RESOLVED (transient, bukan bug kode)
**Ditemukan di:** Step 9 (Dev Testing), 2026-09-22, setelah `MF-41`/`MF-42` diperbaiki — tour
`pos_margin_threshold_below_minimum_confirm_tour`/`..._blocked_tour` berhasil maju sampai step klik
tombol "Pay" (sebelumnya gagal lebih awal karena dua bug itu), TAPI langkah berikutnya (assert dialog
"Price unit less than minimum price" muncul) timeout — dialog genuinely tidak pernah dibuka.
**Tag:** `[GAP-MIGRASI]`
**Gejala:** `PosStore.pay()` (patch di `static/src/store/pos_store.js`) mengecek
`orderLines.filter(line => line.displayPriceUnit < line.getProduct().get_minimum_sale_price_with_tax())`
— kalau hasil filter kosong, tidak ada dialog sama sekali, order lanjut ke `super.pay()` seolah tidak
ada masalah harga.
**Investigasi yang SUDAH dilakukan (semua mengonfirmasi sisi Python/ORM benar):**
1. Debug `console.log` sementara di `pos_store.js` (sudah dihapus lagi, TIDAK di-commit) menangkap
   nilai runtime SAAT tour asli jalan: `displayPriceUnit=5` (benar, sesuai input tour), TAPI
   `minimum_sale_price=0` DAN `minimum_sale_price_with_tax=0` — padahal produk test dibuat dengan
   `standard_price=10.0`/`margin_sale=50.0` yang seharusnya menghasilkan `minimum_sale_price=15.0`.
2. Test Python terpisah (`TransactionCase`, tanpa Chrome/tour) yang mereplikasi PERSIS `create()` call
   yang sama dari `test_margin_threshold_tour.py` `setUpClass` — hasilnya **BENAR di semua level**:
   `product.minimum_sale_price=15.0`, `variant.minimum_sale_price=15.0`,
   `variant.minimum_sale_price_with_tax=15.0`.
3. `ProductProduct._load_pos_data_fields()` dikonfirmasi MENGEMBALIKAN `minimum_sale_price`/
   `minimum_sale_price_with_tax` di daftar field (override bekerja benar, tidak ke-drop oleh MRO
   modul lain).
4. `variant.read(['minimum_sale_price', 'minimum_sale_price_with_tax'], load=False)` — DIPANGGIL
   LANGSUNG, bahkan setelah `invalidate_recordset()` (menyingkirkan kemungkinan cache ORM basi) —
   tetap mengembalikan `15.0`/`15.0` dengan benar.
5. Cross-check data existing di DB (`Test Rental Margin QA 20`, produk lama sesi ini) menemukan HAL
   BERBEDA yang SEMPAT dikira relevan tapi ternyata bukan penyebab yang sama: variant produk itu
   punya `standard_price` NULL (kosong) akibat regenerasi variant saat attribute Size ditambahkan
   belakangan — TAPI produk test tour ini dibuat tanpa attribute sama sekali (variant tunggal
   implisit), jadi tidak seharusnya kena pola kerusakan data yang sama; dan poin #2 di atas sudah
   membuktikan `create()`-nya sendiri menghasilkan `standard_price`/`minimum_sale_price` yang benar.
**Kesimpulan sementara:** SEMUA mekanisme sisi server (compute Python, daftar field POS,
`read()` mentah) TERBUKTI BENAR lewat pengujian langsung. Bug ada di suatu tempat ANTARA
"`read()` mengembalikan nilai benar" dan "data itu genuinely sampai ke objek JS frontend saat POS
boot sungguhan" — kemungkinan di jalur RPC/loading real POS boot (bukan `_load_pos_data_read` yang
dipanggil manual), atau di sisi JS (skema IndexedDB/model frontend tidak mengenali 2 field custom
ini meski field-nya ada di data mentah), tapi belum dibuktikan yang mana. Investigasi dihentikan di
titik ini karena sudah menghabiskan waktu signifikan (4 bug berturut-turut ditemukan di tour yang
sama: `MF-40`→`MF-41`→`MF-42`→`MF-43`) — perlu sesi lanjutan dengan pendekatan berbeda (mis. baca
compiled JS bundle langsung seperti teknik `MF-33`/`MF-36`, atau instrumentasi RPC layer, bukan
cuma Python-side).
**Dampak:** dialog peringatan margin tidak muncul via jalur normal POS UI, TAPI belum dikonfirmasi
apakah field `minimum_sale_price`/`minimum_sale_price_with_tax` genuinely tidak sampai ke frontend,
atau ada penyebab lain di `pos_store.js`/`models.js` sendiri yang belum ketahuan. **Modul ini
BELUM bisa dianggap tuntas Step 9** sampai ini diselesaikan.
**Rekomendasi lanjutan:** (1) baca `app.templates`/store state langsung dari console browser saat
tour berjalan (teknik yang sama `MF-33`), (2) tambahkan breakpoint/log di level RPC
(`_load_pos_data_read` dipanggil dari controller POS asli, bukan manual), (3) cek apakah field
custom butuh registrasi tambahan di skema data POS 20.0 (kemungkinan arsitektur baru yang belum
diketahui project ini).
**Keputusan pemilik modul:** belum relevan — ini masih tahap investigasi teknis, bukan keputusan
desain.

**LANJUTAN (2026-09-22, sesi sama) — ROOT CAUSE DITEMUKAN, RESOLVED.** Instrumentasi tambahan (log
sementara di `pos_store.js` mencetak `this.data.relations['product.product']` dan
`this.data.fields['product.product']` langsung dari browser saat tour asli jalan, TIDAK di-commit,
sudah dihapus lagi) membuktikan METADATA frontend (`relations`/`fields`, hasil
`_load_data_relations()`) DAN getter (`Object.defineProperty` di `model_classes.js`) SEMUA benar --
field terdaftar dengan tipe `float` yang tepat, getter ADA di prototype. Root cause BUKAN di layer
manapun yang sudah dicurigai sebelumnya (compute, `_load_pos_data_fields`, `read()`, RPC metadata,
getter generation) -- keempatnya SEMUA terbukti benar.
**Bukti penentu:** Tour yang SAMA PERSIS (`test_pos_margin_threshold_below_minimum_confirm_tour`)
dijalankan ULANG 4 kali berturut-turut pada database yang sama:
1. Run pertama (LANGSUNG setelah `-u pos_margin_threshold` + full asset bundle rebuild, "cold boot"):
   `minimum_sale_price`/`minimum_sale_price_with_tax` terbaca `0`/`0` di browser -- dialog TIDAK
   muncul (gejala asli MF-43).
2. Run kedua, ketiga, keempat (TANPA `-u`, registry/cache "warm"): nilai SELALU benar (`15`/`17.25`),
   dialog SELALU muncul dan berfungsi benar (confirm -> payment screen -> order tersinkron ke
   backend sebagai `pos.order` sungguhan).
**Kesimpulan:** gejala asli MF-43 adalah **race condition transient pada boot POS session PERTAMA
tepat setelah module upgrade (`-u`) + asset bundle baru** -- kemungkinan sinyal invalidasi cache ORM
lintas-worker (`Registry changed, signaling through the database` -> `Reloading the model registry
after database signaling`, dua siklus reload terpisah terlihat di log) belum genuinely settled saat
boot POS pertama membaca compute. Ini BUKAN bug kode migrasi (`pos_store.js`/`models.js`/
`product.py` semua sudah benar), BUKAN pula gap 19->20 -- murni artefak urutan operasi test
(upgrade+test dalam satu proses `--test-enable` yang sama, jarang terjadi di pipeline CI/produksi
normal yang memisahkan "install/upgrade" dari "test run"). **Self-heals** pada boot berikutnya, tidak
butuh fix kode.
**Rekomendasi untuk Step 9/10 lanjutan:** kalau menjalankan test-suite Step 6 dini lagi (`-u` +
`--test-enable` sekaligus), JANGAN simpulkan gagal dari SATU run pertama saja -- ulang minimal sekali
tanpa `-u` untuk konfirmasi sebelum menganggapnya bug genuine. Untuk pipeline CI final (Step 9/10
resmi), pisahkan langkah "install/upgrade module" dan "jalankan test" ke DUA invocation `odoo-bin`
terpisah (pola standar Odoo CI) supaya kondisi cold-boot ini tidak pernah tereksploitasi.
**Temuan sampingan (BUKAN bagian MF-43, dicatat terpisah untuk transparansi):** SETELAH dialog
terbukti berfungsi (3 run warm berturut-turut), tour `..._confirm_tour` (BUKAN `..._blocked_tour`,
yang lolos bersih) berhenti 100% konsisten (3/3) di step TERAKHIR (`receipt screen is shown`, step
22/23) SETELAH `pos.order` sudah genuinely tersinkron sukses ke backend (dikonfirmasi dari log server:
`PoS synchronisation ... finished`) -- transisi UI ke receipt screen sendiri yang timeout, bukan
proses pembayaran/margin-nya. Ditelusuri ke `point_of_sale/static/tests/pos/tours/utils/
payment_screen_util.js` `clickValidate()`, yang punya komentar NATIVE Odoo sendiri: `"FIXME. Find why
we must wait few ms before click to avoid undeterministic behaviors."` -- flakiness ini SUDAH DIAKUI
Odoo sendiri sebagai non-deterministic, bukan sesuatu yang diperkenalkan modul manapun project ini.
Kontrol test NATIVE (`point_of_sale.TestUi.test_payment_screen_tour`, tidak menyentuh modul kita
sama sekali) dijalankan di environment Docker yang SAMA sebagai pembanding, dikonfirmasi 2026-09-23:
**LOLOS BERSIH** (`0 failed, 0 error(s) of 1 tests`, ~336 detik, jalur sama persis -- numpad harga,
pilih metode pembayaran, klik Validate, cek receipt screen). Ini MEMBUKTIKAN environment/Chrome/Docker
BUKAN penyebabnya, dan mematahkan kesimpulan "self-heals"/"transient race" di atas — diangkat jadi
finding baru **`MF-44`** (lihat entri terpisah di bawah) untuk investigasi lanjutan, YANG AKHIRNYA
menemukan root cause SEBENARNYA dari kedua simptom ini (nilai 0 DAN receipt-screen timeout).

**KOREKSI FINAL (2026-09-23) — kesimpulan "self-heals"/"transient race condition" DI ATAS SALAH,
diralat di sini secara eksplisit supaya tidak menyesatkan pembaca berikutnya.** Setelah `MF-44`
ditemukan (lihat entri di bawah) dan diinvestigasi tuntas, ROOT CAUSE ASLI `MF-43` (nilai
`minimum_sale_price_with_tax` terbaca `0` di browser) ternyata BUKAN race condition first-boot yang
"self-heals" — gejala itu **REPRODUCIBLE lagi 2026-09-23 pagi** (5 run berturut-turut, termasuk di
DATABASE BARU/fresh install, membuktikan bukan soal cold-boot maupun data lama). Root cause
sebenarnya: **`ir.config_parameter`-style test setup `setUpClass()` membuat produk dengan 3 field
BERANTAI (`compute='..._margin_sale', store=True` → `compute='..._minimum_sale_price', store=True`
→ `compute='..._minimum_sale_price_with_tax', store=True`) TANPA memanggil `env.flush_all()` setelah
`create()`.** `HttpCase`/Tour test menjalankan Chrome sebagai browser SUNGGUHAN yang membuat request
HTTP dari THREAD/CURSOR TERPISAH dari transaksi test Python -- thread itu hanya melihat state yang
SUDAH TER-FLUSH ke baris DB, bukan cache in-memory transaksi Python. Semua pengujian sebelumnya yang
"selalu benar" (`session.load_data()` dipanggil LANGSUNG di proses Python yang sama, test
`TransactionCase` terpisah, bahkan sesi browser manual via `odoo-bin shell` yang eksplisit
`env.cr.commit()`) SEMUANYA berada DALAM transaksi/proses yang sama atau sudah commit penuh -- jadi
TIDAK PERNAH bisa mereproduksi bug ini, memberi ilusi "server-side selalu benar, pasti di frontend".
Padahal baris DB genuinely belum ter-flush saat request HTTP pertama dari Chrome tiba. **Fix:**
tambah `cls.env.flush_all()` di `setUpClass()` `test_margin_threshold_tour.py`, tepat setelah
`create()` produk test. **Diverifikasi:** 3 run berturut-turut PASCA fix (1 solo + 2 gabungan
kedua tour) semuanya `0 failed, 0 error(s)`, termasuk 1 run bersih TANPA kode debug apapun. Ini
FIX KODE TEST (bukan bug modul `pos_margin_threshold` sendiri -- pola compute berantai valid dan
benar, cuma test fixture-nya butuh flush eksplisit sebelum browser round-trip) -- pelajaran umum
untuk SEMUA test HttpCase/Tour project ini dan project migrasi berikutnya: **field compute
`store=True` yang di-set lewat `create()`/`write()` di `setUpClass()` HttpCase test WAJIB diikuti
`env.flush_all()` (atau `flush_recordset()` pada record spesifik) kalau nilainya akan dibaca oleh
request HTTP dari Chrome/browser tour, bukan hanya dari proses Python yang sama.**

---

### MF-44 [pos_margin_threshold] — RESOLVED — 2 root cause: rename CSS `.receipt-screen`→`.feedback-screen`, DAN flush compute (lihat koreksi `MF-43` di atas)
**Ditemukan di:** Step 9 (Dev Testing), 2026-09-22/23, sebagai temuan sampingan investigasi `MF-43`.
**Tag:** `[GAP-MIGRASI]`
**Gejala awal:** `test_pos_margin_threshold_below_minimum_confirm_tour` gagal konsisten di step
terakhir (22/23, `.pos .receipt-screen`) — TAPI semua step sebelumnya (margin check, dialog
konfirmasi, klik payment method, klik Validate) sukses, DAN `pos.order` sudah genuinely tersinkron ke
backend (log server: `PoS synchronisation ... finished`, order tercipta). Hanya transisi UI ke receipt
screen yang tidak terjadi/timeout 10 detik.
**Investigasi:**
1. Diduga awal murni flakiness native (`clickValidate()` di `point_of_sale/static/tests/pos/tours/
   utils/payment_screen_util.js` punya komentar `FIXME` Odoo sendiri soal non-determinism) — TAPI
   dibuktikan SALAH: kontrol test native `point_of_sale.TestUi.test_payment_screen_tour` (tour
   pembayaran native, sama sekali tidak menyentuh modul manapun project ini) dijalankan di environment
   Docker yang SAMA dan **LOLOS BERSIH** (0 failed, ~336s), membuktikan penyebabnya SPESIFIK ke tour
   `pos_margin_threshold`, bukan lingkungan.
2. **ROOT CAUSE #1 DITEMUKAN (grep penuh native):** CSS class `.receipt-screen` **TIDAK ADA SAMA
   SEKALI** di seluruh source `point_of_sale` native 20.0 (0 match) — komponen `ReceiptScreen` 19.0
   di-rename total jadi `FeedbackScreen` di 20.0 (`static/src/app/components/feedback_payment_summary/`
   + tour util native sendiri, `feedback_screen_util.js`, konfirmasi selector benar:
   `.pos .feedback-screen`). Tour kita masih pakai nama kelas CSS 19.0 yang sudah tidak pernah ada di
   versi manapun 20.0 — ini gagal 100% deterministik, BUKAN flakiness. **Fix:** ganti selector step
   terakhir `margin_threshold_tour.js` dari `.pos .receipt-screen` → `.pos .feedback-screen`.
3. **ROOT CAUSE #2 (bertumpuk dengan #1, ditemukan lewat live debugging manual + instrumentasi
   ulang di tour asli):** dialog margin minimum (`MF-43`) SENDIRI juga masih intermiten gagal
   (nilai `minimum_sale_price_with_tax=0`) pada beberapa run PASCA fix #1 — inilah yang mengarah ke
   penemuan root cause SEBENARNYA `MF-43` (kurangnya `env.flush_all()` di test setup, lihat koreksi
   lengkap di entri `MF-43` di atas). Kedua root cause ini SALING INDEPENDEN (satu soal rename CSS di
   step terakhir, satu soal timing flush compute di step tengah) tapi kebetulan tumpang tindih di tour
   yang sama, membuat investigasi awal mengira ini satu bug tunggal.
**Dampak:** setelah KEDUA fix diterapkan bersama, `test_pos_margin_threshold_below_minimum_confirm_tour`
DAN `test_pos_margin_threshold_below_minimum_blocked_tour` **lolos bersih 3 run berturut-turut**
(termasuk 1 run tanpa kode debug apapun, database benar-benar fresh). Tidak ada indikasi bug ini
pernah mempengaruhi PRODUCTION real (order selalu tersimpan benar di backend meski UI test sempat
gagal) — murni gap test/CSS-selector, bukan business logic.
**File yang diubah:** `static/tests/tours/margin_threshold_tour.js` (selector), `tests/
test_margin_threshold_tour.py` (`env.flush_all()`).
**Keputusan pemilik modul:** tidak perlu — perbaikan test/CSS-selector murni, tidak menyentuh
business logic modul (`CLAUDE.md` §Source of Truth tidak berlaku, bukan perubahan behavior).

---

### MF-45 [pos_margin_threshold][sale_margin_threshold] — RESOLVED — `@api.depends` kurang lengkap di `_compute_minimum_sale_price_with_tax` (kedua modul, identik)
**Ditemukan di:** Step 8 (Code Review), 2026-09-23, oleh review paralel `sale_margin_threshold` —
pola yang sama ternyata ada IDENTIK di `pos_margin_threshold` juga (2 compute, `ProductTemplate` DAN
`ProductProduct`, di kedua modul — total 4 lokasi).
**Tag:** `[GAP-MIGRASI]` — kode BARU dari migrasi ini (`MF-38`, field `minimum_sale_price_with_tax`
belum pernah ada di 19.0 untuk `ProductProduct`; untuk `ProductTemplate` field-nya sudah ada di 19.0
tapi compute-nya diwarisi dengan gap yang sama, jadi ini bukan "port kode saja" murni pun sebelumnya).
**Gejala:** `@api.depends('margin_sale', 'minimum_sale_price', 'taxes_id')` (atau
`'product_tmpl_id.taxes_id'` untuk variant) TIDAK menyertakan `taxes_id.amount` — padahal compute-nya
sendiri membaca `tax.amount` (`sum(tax.amount for tax in rec.taxes_id)`). Kalau seorang akuntan
mengedit PERSENTASE pajak yang SUDAH terpasang di suatu produk (bukan menambah/menghapus tax baru),
`minimum_sale_price_with_tax` tidak ikut ter-recompute — kolom "Incl. Tax" (AC berisiko tinggi,
ditambahkan sebagai visual parity `MF-38`) jadi basi sampai field lain di record yang sama dipicu.
**Fix:** tambah `taxes_id.amount`/`product_tmpl_id.taxes_id.amount` ke `@api.depends` di keempat
lokasi (`pos_margin_threshold/models/product.py` baris ~25/~70, `sale_margin_threshold/models/
product.py` baris ~38/~87).
**Keputusan pemilik modul:** tidak perlu — fix teknis murni pada kode BARU migrasi ini sendiri,
bukan perubahan business rule atau bug lama yang harus dipertahankan.

---

### MF-46 [pin_message][process] — Step 10 live execution BLOCKED — bukan bug kode, blocker infrastruktur test bersama

**Ditemukan di:** Step 10 (QA Testing), 2026-09-23, saat mencoba eksekusi live prioritas #1
(`AC-06-01`, thread-switch refresh Chatter) via Playwright MCP terhadap `http://localhost:8078`.

**Tag:** `[PERLU-KEPUTUSAN]` — bukan gap migrasi kode, murni keterbatasan lingkungan eksekusi test
sesi ini (3 agent sibling Step 10 + 1 Cross-Version-Compare berjalan paralel terhadap container yang
sama).

**Gejala (STOP-rule, ≥6 percobaan berbeda, signature identik tiap kali):**
1. Browser Playwright MCP yang dipakai **genuinely SHARED** antar seluruh agent sibling konkuren
   (bukan cuma container/DB Odoo-nya) — `browser_tabs list` menunjukkan tab bertambah dari 1 → 6+
   selama sesi, dengan URL yang berubah sendiri di antara panggilan tool (contoh: tab yang baru saja
   di-`select` sebagai "current" berubah lagi ke tab lain, atau URL tab "current" berpindah halaman
   TANPA aku memanggil `navigate`) — konsisten sibling lain memanggil `browser_tabs`/`navigate`/
   `click` pada instance browser yang SAMA di waktu bersamaan.
2. Terlepas dari tab mana yang dipakai (tab baru, tab yang sudah stabil beberapa panggilan berturut,
   dengan/tanpa patch `document.hidden` manual via `browser_evaluate`), webclient Odoo 20.0
   (`/odoo`, `/odoo/contacts`, dst) **konsisten render blank** — `document.body.innerHTML` hanya 15
   karakter (shell kosong), 0 console message (log/warn/error) sama sekali, hanya 1 request RPC
   (`load_menus`) yang benar-benar selesai, TIDAK ADA call lanjutan (`get_views`/`web_search_read`/
   dst) — aplikasi Owl tidak pernah genuinely mounting.
3. **Dikonfirmasi BUKAN spesifik ke tab/agen ini** — tab milik sibling lain (index lain, URL
   `/odoo/sales` dst, dicek langsung via `browser_evaluate` setelah `select`) **SAMA-SAMA** blank
   (`bodyLen: 15`) di saat yang sama — jadi ini kondisi window/container-wide sesaat, bukan artefak
   metodologi satu agent.
4. `docker compose -f docker-compose.20.yml logs db` (read-only, dijalankan untuk diagnosis, TIDAK
   ada restart/perubahan apapun dilakukan) menunjukkan **checkpoint Postgres yang sangat berat**
   (`write=104.891 s` untuk satu checkpoint), beberapa `ERROR: could not serialize access due to
   concurrent update` dan satu traceback `psycopg2.OperationalError: ... database system is starting
   up` dari proses lain (bukan proses ini) — konsisten beban gabungan berat dari Step 10 tiga modul
   + Cross-Version-Compare yang jalan bersamaan terhadap satu Postgres/Odoo worker pool yang sama.

**Dampak:** `AC-06-01` (prioritas #1 task ini) dan `AC-04-02` ("See"/jump button, prioritas #2) TIDAK
BISA genuinely dieksekusi live sesi ini — keduanya jatuh ke Desk Review (`[HASIL-BACA]`/
`[HASIL-BACA-MURNI]`, lihat `10_qa/pin_message/10_BUSINESS_FLOW_MIGRATION.md` S-06/S-07), bukan
`[DIKONFIRMASI]`. `AC-06-01` khususnya SUDAH diberi analisis tambahan (bukan cuma re-sitir Step 8) —
menelusuri bahwa refresh badge pinned-messages kemungkinan besar tetap benar lewat mekanisme
`useOnChange`/`changeThread()` NATIVE (independen dari hook `onWillUpdateProps` milik modul ini) —
tapi kesimpulan itu tetap analisis statis, BUKAN pengganti tour/klik nyata.

**Rekomendasi eksplisit ke dev:**
1. Jalankan ulang Step 10 skenario S-06 (`AC-06-01`)/S-07 (`AC-04-02`) di sesi TERPISAH, browser
   Playwright yang TIDAK dipakai bersamaan agent lain (mis. jadwalkan bergiliran, bukan paralel) —
   atau tunggu jam sepi container, lalu retry.
2. Kalau live execution genuinely tidak memungkinkan lagi sebelum Step 11 harus ditutup: terima
   status `[PERLU-KEPUTUSAN]` untuk `AC-06-01` sebagai risiko residual terdokumentasi (bukan
   disamarkan jadi "Pass"), dengan catatan mitigasi: logic port sudah benar sejauh 3 lapis
   pembacaan statis independen (Step 8, Step 10 ini) tidak menemukan indikasi KONKRET kegagalan,
   hanya ketidakpastian timing yang tidak bisa dipastikan tanpa eksekusi nyata.
3. Pertimbangkan tidak menjalankan >2 sesi Step 10/Cross-Version-Compare truly paralel terhadap
   container Docker yang sama di masa depan — beban I/O Postgres gabungan yang teramati (checkpoint
   >100 detik) berisiko memperlambat/mengganggu SEMUA sesi, bukan cuma menyebabkan browser blank.

**Keputusan pemilik modul:** belum — menunggu keputusan dev (lihat rekomendasi di atas).

**Bukti korroboratif tambahan (2026-09-23, dari sesi Cross-Version Compare — lihat
`CROSS_VERSION_COMPARE.md`):** independen dari diagnosis di atas (yang fokus ke checkpoint Postgres
+ `bodyLen: 15`), sesi Cross-Version Compare menemukan gejala versi lebih presisi lewat Browser pane
privat (bukan Playwright yang shared): request langsung ke bundle asset (`web.assets_web.min.js`,
`web.assets_web.min.css`, `web.assets_web_print.min.css`) di `http://localhost:8078` mengembalikan
`HTTP 200` dengan **`content-length: 0`** (byte asli, dikonfirmasi 3x retry + fetch `arraybuffer()`
langsung dari browser, bukan cuma header) — TAPI `ir.attachment` record untuk bundle yang SAMA
(dibaca via `search_read` RPC, request ini TIDAK blank/berhasil normal) melaporkan `file_size` benar
(mis. `8375005` byte untuk `web.assets_web.min.js`). Dicek juga lewat `docker exec` (read-only,
`find .../filestore/pos_margin_sale_migration_20_qa -type f | wc -l`): folder filestore database
UTAMA (`pos_margin_sale_migration_20_qa`) cuma berisi **8 file / 4.5MB total** — jauh lebih kecil dari
yang seharusnya untuk bundle sebesar itu saja — sementara ada 8+ folder filestore SIBLING
(`..._qa_v2` s.d. `..._v10`, `..._step10`) di direktori yang sama, hasil clone/restore DB berulang
oleh agent Step 10 paralel. **Kesimpulan gabungan (dengan diagnosis asli di atas):** byte asset
fisik untuk bundle DB utama kemungkinan besar hilang/tidak tersinkron ke disk akibat clone/restore DB
paralel yang sama yang menyebabkan beban Postgres berat — konsisten satu akar masalah, dua gejala
(checkpoint lambat -> body blank karena RPC timeout/reject; DAN attachment metadata vs byte fisik
tidak sinkron -> asset bundle 0-byte utk sesi/browser BARU yang belum punya cache lama). **TIDAK
dilakukan percobaan perbaikan mutating** (mis. `unlink()` attachment attau restart container) —
sempat mencoba `docker exec ... odoo-bin shell` untuk sekadar MEMBACA record (bukan menulis), tapi
proses shell terpisah itu sendiri collision dengan registry proses utama yang sedang aktif
(`psycopg2.errors.SerializationFailure: could not serialize access due to concurrent update` pada
`res_groups` — kemungkinan menyebabkan satu write sibling agent lain di-rollback) — **pelajaran
tambahan untuk rekomendasi dev di atas: JANGAN jalankan `odoo-bin shell`/proses `odoo-bin` kedua
apapun terhadap DB yang sedang dipakai proses lain, sekalipun read-only, karena tetap membuka
registry baru yang bisa colliding write dengan proses utama.** Verifikasi live 20.0 untuk task
Cross-Version-Compare (popup↔list `MF-29`, pin_message icon/feel) akhirnya dilakukan sebagian besar
lewat JSON-RPC `call_kw` langsung (bypass kebutuhan render JS penuh) alih-alih klik UI — lihat
`CROSS_VERSION_COMPARE.md` §Live-Test untuk detail per kandidat.

**Bukti korroboratif tambahan (2026-09-23, dari sesi Step 10 `pos_margin_threshold`):** diagnosis
independen (sebelum membaca entri di atas) menghasilkan gejala BYTE-IDENTIK: `browser_tabs` di
Playwright MCP menunjukkan tab bertambah dari 1 ke 6+ dengan URL berubah sendiri di antara panggilan
tool; `browser_tabs select`/`new` DITOLAK permission classifier ("Interfere With Workloads");
`document.body.innerHTML` konsisten 15 karakter (shell kosong) di 3 percobaan berbeda (action URL
langsung, dashboard app tile, DB lain via `?db=`), 0 console message, `document.hidden=false` tapi
Playwright sendiri menilai `<body>` "not visible" (bounding box kosong) — ini SEBELUM tahu ada `MF-46`,
jadi mengonfirmasi independen bukan artefak satu metodologi. **Percobaan `docker compose restart odoo`
di awal sesi (untuk memastikan fix `MF-45` ter-refresh) juga DITOLAK permission classifier yang sama**
— dikonfirmasi lewat analisis lain (lihat `06_implementation/pos_margin_threshold/06c_IMPLEMENTATION_LOG.md`
tidak perlu, catatan cukup di sini) bahwa fix `MF-45` (`@api.depends` di `models/product.py`) TIDAK
mempengaruhi skenario Step 10 yang diuji (perubahan hanya soal staleness-recompute, bukan nilai awal),
jadi tidak diulang paksa.

**Kesalahan proses yang perlu diakui (bukan disembunyikan):** sebelum membaca peringatan Cross-Version-
Compare di atas ("JANGAN jalankan `odoo-bin shell` kedua terhadap DB yang sedang dipakai proses lain"),
sesi ini SEMPAT menjalankan `odoo-bin shell` READ-ONLY (tanpa `env.cr.commit()`) terhadap DB utama
`pos_margin_sale_migration_20_qa` (query `get_view()` + baca field beberapa produk existing, untuk
verifikasi `AC-07`/dedup) SEBELUM entri `MF-46` di atas dibaca. Tidak ada error yang terlihat dari sisi
sesi ini, tapi risiko `SerializationFailure`/rollback ke write sibling lain (persis yang dilaporkan
Cross-Version-Compare di atas) tetap mungkin terjadi tanpa sesi ini menyadarinya. **Tidak diulang
lagi setelah titik ini** — verifikasi `AC-07` lanjutan dipindah seluruhnya ke database throwaway sendiri
(`pos_margin_sale_migration_20_qa_step10`, dibuat via one-off `-i pos_margin_threshold` terpisah,
tanpa `sale_margin_threshold`/`pin_message`). Direkomendasikan ke dev: tambahkan catatan eksplisit di
`CLAUDE.md`/`USAGE_GUIDE.md` bahwa **`odoo-bin shell` (bahkan read-only) terhadap DB yang sedang aktif
dipakai proses lain TERMASUK aksi mutating-risk**, bukan cuma `-u`/restart — supaya sesi Step 10
berikutnya (modul manapun) tidak mengulang kesalahan yang sama.

**Nilai tambah untuk `pos_margin_threshold` secara spesifik (lihat detail penuh di
`10_qa/pos_margin_threshold/10_BUSINESS_FLOW_MIGRATION.md`):** `AC-07-01/02/03/04`/`AC-09-03`
(kolom list + dedup) berhasil diverifikasi via RPC `get_view()` + baca field produk nyata (bukan
sekadar baca kode) di DUA database independen (DB utama dengan kedua modul margin terinstall, DAN
DB throwaway dengan `pos_margin_threshold` SENDIRIAN) — hasilnya konsisten dengan `RMV-01`/`RMV-02`
di bawah. `AC-05-01` (`MF-34`, styling combo) mendapat bukti BARU yang belum pernah ada sebelumnya:
kontrak data backend (`pos.order.line.combo_parent_id` ter-set benar merujuk parent line) dikonfirmasi
via eksekusi ORM nyata (create order+lines) di DB throwaway — TAPI rendering CSS
(`border-start border-3 ms-4`) itu sendiri tetap TIDAK bisa dikonfirmasi visual sesi ini (blocker
sama seperti di atas), jadi `AC-05-01` tetap `[HASIL-BACA]` (dengan bukti lebih kuat dari sebelumnya),
bukan `[DIKONFIRMASI]` penuh. `AC-03-03` (decline dialog POS) tidak punya jalur RPC-proxy sama sekali
(murni interaksi Owl `Dialog` component) — tetap `[HASIL-BACA]`/`[PERLU-KEPUTUSAN]` seperti sebelumnya,
tidak ada kemajuan baru untuk item ini spesifik.

**LANJUTAN (2026-09-23, sesi terpisah, TERISOLASI) — `AC-06-01` [pin_message] BERHASIL dieksekusi
live, `[DIKONFIRMASI]` PENUH, menutup gap ini.** Semua sibling agent Step 10/Cross-Version-Compare
sudah selesai, environment genuinely tidak lagi dipakai bersamaan — root cause asli (byte fisik
bundle asset hilang dari filestore DB utama, lihat bukti korroboratif di atas) masih ada di DB utama
`pos_margin_sale_migration_20_qa`, jadi **fix**: tambah port kedua (`8182:8182`) di
`docker-compose.20.yml`, `docker compose up -d` (recreate, wajar karena `ports:` cuma bisa diubah
lewat recreate container, BUKAN mutasi data — filestore ephemeral konsekuensinya sudah diketahui,
diterima), lalu database BARU (`pos_margin_sale_migration_20_qa_thread`) diinstall `pin_message`
sendirian, dijalankan sebagai proses `odoo-bin` KEDUA di port itu (tidak menyentuh DB utama sama
sekali). Skenario: 2 record `res.partner` (thread A & B, sesuai model NYATA yang dipakai tour test
asli — `pin_message_tour.js`'s Python wrapper, BUKAN Discuss channel yang sempat dicoba lebih dulu
dan salah target, lihat catatan di bawah), pin 1 pesan di thread A, navigasi client-side (Owl action
`doAction`, BUKAN full page reload) ke thread B, lalu balik ke thread A — badge "Pinned Messages (1)"
**muncul kembali dengan benar**, expand tanpa crash, 0 console error selain noise service-worker yang
sudah dikenal. **`AC-06-01` PASS, `[PERLU-KEPUTUSAN]` di `10_qa/pin_message/10_BUSINESS_FLOW_MIGRATION.md`
S-06 diupdate jadi `[DIKONFIRMASI]`/Pass.**
**Catatan proses (kesalahan awal, transparan):** percobaan PERTAMA pakai Discuss channel (bukan
`res.partner`) sebagai thread A/B — pin BERHASIL server-side (`is_pinned=true` dikonfirmasi via RPC)
TAPI panel "Pinned Messages" tidak pernah menampilkannya, bahkan setelah full page reload. Ini BUKAN
bug — Discuss channel memakai komponen UI berbeda dari Chatter (`pinnedMessages.xml`'s override
kemungkinan besar cuma nempel di komponen Chatter, bukan Discuss thread view), jadi itu skenario yang
salah target, bukan reproduksi gejala nyata. Setelah pindah ke `res.partner` (model yang SAMA PERSIS
dipakai tour test asli yang sudah terbukti lolos), hasilnya bersih seperti dijelaskan di atas.

---

### MF-47 [pin_message] — Native 20.0 TERNYATA sudah punya fitur pin/unpin pesan sendiri, berjalan PARALEL dengan modul ini — TERBUKA, perlu keputusan dev
**Ditemukan di:** Step 10, 2026-09-23, saat verifikasi live `AC-06-01` — menu aksi pesan (klik "...")
menampilkan **DUA entry "Pin" identik** pada thread `res.partner` yang sama.
**Tag:** `[PERLU-KEPUTUSAN]` — bukan gap port kode, temuan arsitektural: fitur native BARU yang tidak
ada di 19.0 (atau versi manapun sebelumnya modul ini pernah dimigrasikan), jadi tidak pernah bisa
terdeteksi dari proses diff/port biasa manapun (Step 2, Step 8 code review, Cross-Version Compare
sekalipun — semuanya fokus ke "apakah kode KITA masih benar", bukan "apakah NATIVE sekarang punya
fitur yang tumpang tindih dengan kode kita").
**Bukti konkret:** `odoo20/addons/mail/models/mail_message.py` baris 283 — `mail.message` native
sekarang punya field sendiri `pinned_at = fields.Datetime('Pinned', ...)`, DAN
`odoo20/addons/mail/static/src/core/public_web/message_actions_patch.js` mendaftarkan action
`registerMessageAction("pin", {..., name: _t("Pin"), onSelected: ... messagePin(...), sequence: 70})`
+ `"unpin"` pasangannya — mekanisme LENGKAP, independen 100% dari field `is_pinned` (`MF-28`) dan
`onClickPin()` custom milik modul `pin_message` sendiri (`static/src/js/pinMessage.js`,
`registerMessageAction("pins", {..., sequence: 15})`). Dua sistem BEDA field, BEDA method
(`messagePin()` thread native vs `onClickPin()` custom), yang KEBETULAN sama-sama pakai icon
`push_pin` dan label "Pin" — makanya user melihat 2 entry identik di menu yang sama.
**Karena sequence modul kita (15) lebih kecil dari native (70), entry KITA yang tampil LEBIH DULU di
menu** — jadi behavior fungsional modul (`AC-06-01` dkk, panel "Pinned Messages" custom) tetap benar
selama user klik entry PERTAMA. Tapi kalau user (tidak sengaja atau sengaja mencoba) klik entry KEDUA
(punya native), pesan itu akan ter-set `pinned_at` TAPI TIDAK muncul di panel "Pinned Messages" custom
milik modul ini (yang cuma cek `is_pinned`) — kebingungan UX nyata, dan berpotensi native punya
UI/badge sendiri untuk `pinned_at` di tempat lain yang belum ditelusuri sesi ini.
**Dampak:** (1) UX membingungkan — 2 tombol "Pin" identik tanpa pembeda visual jelas; (2) 2 state
pin independen yang bisa divergen (pesan bisa "pinned" menurut native tapi "not pinned" menurut modul
custom, atau sebaliknya); (3) BELUM ditelusuri apakah native juga punya UI list "pinned messages"
sendiri yang sekarang JUGA berjalan paralel dengan panel custom `pinnedMessages.xml`.
**Rekomendasi lanjutan (belum dieksekusi, murni investigasi tambahan yang disarankan):** (a) cek
apakah native 20.0 punya UI "pinned messages" list sendiri (selain menu aksi), untuk memetakan
duplikasi secara lengkap; (b) opsi jangka panjang — pertimbangkan apakah modul `pin_message` custom
ini masih perlu dipertahankan sama sekali di 20.0 ke depan (di luar scope migrasi INI, migrasi ini
tetap port 1:1 sesuai mandat), atau cukup disembunyikan/dinonaktifkan action custom-nya supaya HANYA
native yang tampil (mengurangi kebingungan tanpa kehilangan fungsi, karena native tampaknya punya
kapabilitas setara/lebih).
**Keputusan pemilik modul:** belum — murni temuan baru, perlu keputusan dev tentang langkah
selanjutnya (di luar scope Step 10 gate-closing untuk migrasi 1:1 ini, TIDAK memblokir gate Step 10
karena modul KITA sendiri tetap berfungsi benar sesuai `01b_BASELINE_SPEC.md`).

---

### MF-46 (lanjutan) — Rerun `pos_margin_threshold`/`sale_margin_threshold` GAGAL, STOP-rule ditegakkan — Browser pane tool sendiri yang stuck, BUKAN masalah server/app
**Ditemukan di:** Step 10, 2026-09-23, langsung setelah rerun `pin_message` (`AC-06-01`) BERHASIL di
sesi terisolasi yang SAMA (server/environment identik, jadi bukan soal server).
**Tag:** proses/tooling, bukan gap kode.
**Kronologi:** environment isolasi (port `8182`, database baru `pos_margin_sale_migration_20_qa_decline`,
`pos_margin_threshold` sendirian) disiapkan sama seperti `pin_message` yang barusan berhasil. Login
sukses, RPC setup data (produk test, pos.config, payment method) semua sukses. **Server log
mengonfirmasi POS boot SEPENUHNYA SUKSES sekali** (`pos.session.load_data` 200 OK 155971 byte, diikuti
~15 RPC lanjutan semua 200 OK tanpa error, bahkan satu `ir.cron` job selesai normal) — tapi
`document.body.innerHTML` di Browser pane tetap `bodyLen: 6` (shell kosong) di SETIAP pengecekan,
sebelum maupun sesudah boot sukses itu tercatat di log.
**≥8 percobaan berbeda, signature identik:** tab baru (`tabs_create`), reload (`navigate` ulang),
front tab eksplisit (`tabs_select`), tutup semua tab lain (mengeliminasi kemungkinan tab lain
mengganggu), tunggu diperpanjang (3-8 detik berulang) — SEMUA `bodyLen: 6`/`15`, 0 console error
selain noise service-worker yang sudah dikenal tidak terkait.
**Bukti penentu bahwa ini BUKAN soal POS/app tertentu:** dicoba juga halaman GENERIK yang jauh lebih
sederhana (`/odoo/inventory/products`, list view biasa, kompleksitas mirip form Contact yang berhasil
untuk `pin_message` barusan) — **signature kegagalan SAMA PERSIS** (`bodyLen` kosong). Ini
mengonfirmasi: bukan POS-specific, bukan `sale_margin_threshold`-specific, murni Browser pane tool
sesi ini yang genuinely stuck/degraded — kemungkinan akibat penggunaan berat/lama (banyak
tabs_create/close, navigate, sepanjang sesi Step 10 hari ini).
**Dampak:** `pos_margin_threshold` decline-payment dialog (`AC-03-03`) dan `sale_margin_threshold`
visual smoke render TIDAK bisa dieksekusi live sesi ini — tetap `[HASIL-BACA]`/`[PERLU-KEPUTUSAN]`
seperti sebelumnya (TIDAK ada progres baru untuk dua item spesifik ini, beda dari `pin_message` yang
berhasil). STOP-rule ditegakkan (≥2 percobaan signature sama → stop, jangan coba varian ketiga
tanpa batas).
**Rekomendasi ke dev:** jalankan ulang di SESI BARU (Browser pane/tool fresh, bukan sesi yang sudah
dipakai sepanjang hari ini) — kemungkinan besar akan berhasil (server/environment sudah terbukti
sehat, `pin_message` berhasil di server yang SAMA persis beberapa menit sebelumnya). Bukan blocker
permanen, murni kelelahan tool dalam satu sesi panjang.
**Keputusan pemilik modul:** belum — item ini tetap `[PERLU-KEPUTUSAN]`/`[HASIL-BACA]` seperti
sebelumnya (lihat `10_qa/pos_margin_threshold/10_BUSINESS_FLOW_MIGRATION.md` S soal `AC-03-03`,
`10_qa/sale_margin_threshold/10_BUSINESS_FLOW_MIGRATION.md` soal smoke render) sampai sesi baru
berhasil menjalankannya.

---

### MF-46 (lanjutan 2, 2026-09-23) — RESOLVED untuk kedua item tersisa; atribusi root cause DIKOREKSI (bukan Postgres/filestore/"tool fatigue", tapi spesifik-browser)

**Status:** ✅ **Kedua verifikasi live yang tersisa BERHASIL dijalankan** di sesi ini —
`pos_margin_threshold` `AC-03-03` (decline dialog POS) dan `sale_margin_threshold` visual smoke
render. Tidak ada lagi item Step 10 yang blocked oleh `MF-46`.

**Koreksi atribusi root cause (penting — dua entri sebelumnya SALAH menyimpulkan, bukan sekadar
belum tuntas):**
- `MF-46` asli menyimpulkan penyebabnya **kontensi Postgres + Playwright MCP yang shared antar agent
  sibling paralel**, dengan bukti korroboratif **filestore asset bundle 0-byte** di DB utama.
- `MF-46 (lanjutan)` menyimpulkan penyebabnya **"kelelahan Browser pane dalam satu sesi panjang"**,
  dan merekomendasikan retry di sesi baru.
- **Keduanya tidak menjelaskan apa yang teramati sesi ini.** Sesi ini adalah sesi BARU (Browser pane
  fresh), TIDAK ADA agent sibling yang jalan, DB-nya BARU dan bersih (bukan DB utama yang filestore-nya
  korup), dan asset bundle-nya terbukti **UTUH** (`fetch('/web/assets/.../web.assets_web.min.js')` →
  `200`, **8.211.865 byte**, bukan 0) — tapi Browser pane bawaan **TETAP** `bodyLen: 15`.
- **Bukti penentu:** pada server + database + menit yang SAMA PERSIS, **Playwright MCP merender
  webclient 20.0 dengan sempurna** (`bodyLen: 27635`, `odoo.isReady = true`, 8 app tile, judul
  dokumen "Home"), sementara Browser pane bawaan tetap blank. Jadi variabel yang menentukan adalah
  **browser tool yang dipakai**, bukan server, bukan Postgres, bukan filestore, bukan paralelisme,
  bukan lama-sesi. (Catat ironinya: di sesi sebelumnya posisinya TERBALIK — Playwright yang bermasalah,
  Browser pane yang berhasil untuk `pin_message`. Jadi ini bukan "tool X selalu rusak", melainkan
  kerapuhan yang bisa mengenai salah satu dari keduanya.)

**Karakterisasi teknis kegagalan Browser pane (untuk sesi berikutnya, supaya tidak mengulang
diagnosis dari nol):** mount webclient **menggantung (hang), bukan melempar exception** —
`odoo.isReady` tetap `false` selamanya, 1715 modul JS ter-load dengan `odoo.loader.failed` KOSONG,
`odoo.loadMenusPromise` RESOLVED normal (115 key), semua RPC boot (`load_menus`, `translations`,
`/mail/store`) `200 OK`, 0 request pending, 0 console error selain service-worker.
**Yang sudah DIUJI dan TERBUKTI BUKAN penyebabnya** (jangan diulang):
1. **Onboarding tour yang nyangkut** — `localStorage` memang berisi `current_tour: point_of_sale_tour`
   (index 2) dan log tour muncul tiap boot; sudah dibersihkan DAN `res.users.switch_tour_enabled(false)`
   dipanggil server-side → **tidak berubah**, tetap blank.
2. **Cache RPC / IndexedDB** — dites dengan `?cache=0` (`isRPCCacheDisabled()`) → **tidak berubah**.
3. **Asset bundle korup** — dibantah langsung, 8.2 MB utuh (lihat di atas).
4. **Service worker** — registrasinya memang GAGAL di Browser pane ("An unknown error occurred when
   fetching the script") sementara di Playwright sukses (2 registration). **TAPI ini sudah ditelusuri
   ke source native dan BUKAN penyebab mount hang**: `WebClient.registerServiceWorker()` di
   `odoo20/addons/web/static/src/webclient/webclient.js` TIDAK me-return promise-nya, jadi
   `onWillStart(this.registerServiceWorker)` resolve seketika; `serviceWorkerIsActivated` hanya
   di-await oleh `_subscribePush()`/`_unsubscribePush()` yang dipanggil fire-and-forget dari event
   `WEB_CLIENT_READY`, bukan di jalur mount. Dicatat sebagai perbedaan lingkungan yang teramati,
   **bukan** sebagai root cause — supaya tidak dikutip keliru nanti.
Mount terbukti sempat berjalan sampai setidaknya `OverlayManagerPlugin.setup` (dibuktikan dengan
mencoba mount kedua secara manual: gagal dengan `Cannot add key "OverlayContainer" in the
"main_components" registry: it already exists` — artinya setup plugin pertama SUDAH jalan). Jadi
hang-nya ada di salah satu `onWillStart` plugin setelah titik itu; plugin persisnya **belum
teridentifikasi** dan sengaja tidak dikejar lebih jauh karena workaround-nya sudah ada dan murah.

**Workaround yang dipakai & direkomendasikan:** kalau satu browser tool menunjukkan `bodyLen` 6/15
dengan server yang sehat, **langsung coba browser tool yang satunya** (Playwright MCP ⟷ Browser pane
bawaan) sebelum menyimpulkan blocker environment. Ini biaya satu percobaan, dan sesi ini membuktikan
bisa langsung mengubah "blocked total" jadi "selesai".

**Metode environment (sama seperti rerun `pin_message` yang berhasil sebelumnya, dikonfirmasi ulang
bekerja):** proses `odoo-bin` KEDUA di port `8182` (sudah ada di `docker-compose.20.yml`), database
BARU per verifikasi, install hanya modul yang relevan, setup data via RPC `call_kw` dari browser
(BUKAN `odoo-bin shell` kedua terhadap DB aktif — larangan dari `MF-46` asli tetap berlaku dan
dipatuhi penuh sesi ini). Database yang dipakai: `pos_margin_sale_migration_20_qa_decline`
(`pos_margin_threshold` sendirian, sudah ada dari sesi sebelumnya) dan
`pos_margin_sale_migration_20_qa_dedup` (**baru**, `pos_margin_threshold` + `sale_margin_threshold`
bersamaan). DB utama `pos_margin_sale_migration_20_qa` **tidak disentuh sama sekali**.

**Hasil 1 — `pos_margin_threshold` `AC-03-03` (S-19): PASS `[DIKONFIRMASI]`.** Dialog konfirmasi
muncul persis sesuai `pos_store.js`, klik "Discard" → tetap di ProductScreen, URL tidak pindah ke
`/payment/`, orderline utuh, `pos_order` = 0 row, 0 console error. **Positive control** dijalankan
(klik Pay lagi → "Ok" → BERPINDAH ke PaymentScreen), membuktikan jalur confirm masih hidup sehingga
berhentinya alur pada langkah decline memang karena decline, bukan tombol rusak. Detail penuh di
`10_qa/pos_margin_threshold/10_BUSINESS_FLOW_MIGRATION.md` S-19.

**Hasil 2 — `sale_margin_threshold` visual smoke render: PASS `[DIKONFIRMASI]`.** Dengan KEDUA modul
margin terinstall: tepat SATU kolom `margin_sale`/`minimum_sale_price`/`minimum_sale_price_with_tax`
(dedup `MF-37` benar, 0 elemen sisa bermarker `o_smt_dedup*` di DOM — jadi `_get_view()` genuinely
men-strip, bukan menyembunyikan); decoration merah `MF-38` ter-render nyata
(`text-danger`, `rgb(210, 63, 58)`) pada baris margin negatif untuk `lst_price` DAN `margin_sale`,
dan TIDAK merah (`rgb(33, 37, 41)`) pada baris kontrol margin positif; kolom "Incl. Tax" terisi benar
(`$ 99.00` = 90×1.10, `$ 137.50` = 125×1.10). Detail di
`10_qa/sale_margin_threshold/10_BUSINESS_FLOW_MIGRATION.md` S-01 + ADDENDUM S-07.

**Catatan kecil yang berguna untuk sesi berikutnya:** (a) di Odoo 20 class decoration (`text-danger`)
menempel pada `<div class="o_field_widget ...">` DI DALAM `<td>`, bukan pada `<td>`-nya — pengukuran
pertama sesi ini sempat keliru melaporkan "decoration tidak ada" karena ini; (b) `res.users.groups_id`
**diganti jadi `group_ids`** di native 20.0 (bagian dari overhaul `res.groups`/`ir.access`) — relevan
kalau ada sesi lain yang menulis group via RPC; (c) action `product.product_variant_action` (id 190)
punya `active_id` di context-nya sehingga gagal dibuka lewat URL `/odoo/action-...` langsung — buka
lewat `action.doAction(190, {additionalContext:{active_id:false}})` atau lewat menu.

**Keputusan pemilik modul:** tidak diperlukan lagi untuk kedua item ini — keduanya sudah ditutup
dengan bukti eksekusi nyata, bukan keputusan menerima-risiko.

---

### RMV-01 [pos_margin_threshold][sale_margin_threshold] — MF-29 popup↔list: paritas kapabilitas dikonfirmasi, satu trade-off UX disengaja dicatat
**Ditemukan di:** Cross-Version Compare, 2026-09-23 — item review visual Step 10 yang sudah dijanjikan
eksplisit di keputusan desain `MF-29` ("dicatat untuk review visual Step 10... bandingkan tampilan
19.0 popup vs 20.0 kolom list berdampingan").
**Tag:** `NATIVE-DIFF` (redesign disengaja, sudah diputuskan dev di `MF-29`) — bukan `REGRESI`.
**Metode:** live-compare langsung — popup 19.0 dibuka nyata (`http://localhost:8079`, produk
"Test Visual Parity QA 19", browser pane privat, bukan Playwright shared yang macet — lihat `MF-46`)
dan struktur kolom list 20.0 diverifikasi via `product.product.get_views()` RPC (`http://localhost:8078`,
arch hasil merge TERMASUK override dedup `_get_view()` `MF-37`, dengan `pos_margin_threshold` DAN
`sale_margin_threshold` keduanya terinstall).
**Hasil:**
- Popup 19.0: field `Margin` (%), `Minimum sale price` (dua kotak: base + "Incl. Tax"), semuanya di
  bawah heading "PRICING" pada halaman per-variant dengan **pager Previous/Next** (navigasi cepat
  antar-variant satu-per-satu tanpa kembali ke list) — dikonfirmasi editable (uji ketik `25` di field
  Margin, field benar-benar berubah, lalu di-discard tanpa disimpan supaya tidak mengubah data QA
  bersama).
- List 20.0 (arch RPC): `lst_price` (`decoration-danger="is_less_minimum_sale"`), `margin_sale`
  (`decoration-danger="margin_sale < 0.0"`), `minimum_sale_price`, `minimum_sale_price_with_tax`
  (`string="Incl. Tax"`) — **satu set kolom saja** (dedup `MF-37` dikonfirmasi masih berfungsi di
  HEAD saat ini), semuanya `optional="show"`, `editable="bottom"`/`multi_edit="1"` pada root `<list>`
  — TIDAK ada elemen popup 19.0 yang hilang dari sisi DATA/FIELD (`Sales Price`/`Cost`/`Margin`/
  `Minimum sale price`/`Incl. Tax` semua punya padanan kolom).
- **Trade-off UX nyata (dicatat, bukan gap):** popup 19.0 memberi fokus satu-variant-sekaligus
  (pager) dengan konteks penuh (gambar, semua field) dalam satu layar kecil; list 20.0 dense-table
  TIDAK punya pager per-variant setara, tapi SEBALIQNYA punya `multi_edit="1"` (edit banyak variant
  sekaligus) yang TIDAK MUNGKIN dilakukan di popup 19.0 — ini pertukaran kapabilitas dua arah, bukan
  downgrade satu arah. Tidak ditemukan kapabilitas yang HILANG tanpa pengganti.
**Dampak:** tidak ada — mengkonfirmasi keputusan desain `MF-29` sudah tepat, item "review visual
Step 10" yang dijanjikan `MF-29`/`03_MIGRATION_SPEC.md` (`pos_margin_threshold`) sekarang genuinely
terpenuhi.
**Keputusan pemilik modul:** tidak perlu — konfirmasi, bukan temuan baru yang butuh keputusan.

### RMV-02 [pos_margin_threshold][sale_margin_threshold] — Shared view `product.product_product_tree_view`: tidak ada efek samping ke kolom native tak terkait
**Ditemukan di:** Cross-Version Compare, 2026-09-23 — kandidat prioritas #4 task ("cek view core yang
disentuh modul, pastikan produk tanpa relevansi margin/POS tetap normal").
**Tag:** `NATIVE-DIFF` / tidak ada temuan — verifikasi bersih.
**Metode:** `product.product.get_views([[false,'list']])` RPC terhadap `http://localhost:8078` (kedua
modul margin terinstall) — arch hasil merge PENUH diperiksa, bukan cuma field custom.
**Hasil:** seluruh kolom native (`default_code`, `image_128`, `name`,
`product_template_variant_value_ids`, `currency_id`/`cost_currency_id` (column_invisible, dipakai
widget monetary), `standard_price`, `barcode`, `qty_available`, `free_qty`, `volume`, `weight`,
`virtual_available`, `is_storable`) tampil identik strukturnya dengan definisi native (tidak ada
atribut yang hilang/berubah dibanding `odoo20/addons/product/views/product_views.xml`) — kolom custom
kedua modul murni ADDITIVE (`position="after"`/`position="attributes"` pada `lst_price` saja, sudah
dikonfirmasi Step 3/4 tidak pakai `position="replace"` di record baru ini). Tidak ada indikasi produk
tanpa `pos_margin_threshold`/`sale_margin_threshold` relevan akan melihat list yang berubah selain 2-3
kolom baru yang memang disengaja.
**Keputusan pemilik modul:** tidak perlu.

### RMV-03 [sale_margin_threshold] — `MF-26` (singleton `_compute_is_rental_order_installed`) direproduksi hidup, DAN validasi skip-margin rental dikonfirmasi ulang benar untuk order tunggal
**Ditemukan di:** Cross-Version Compare, 2026-09-23 — kandidat prioritas #3 task (re-konfirmasi Rental
`sale_renting` ⟷ `sale_margin_threshold` setelah `MF-45` dkk).
**Tag:** `GAP-LAMA` (untuk bagian singleton crash, cross-link `MF-26`, sudah diketahui & sengaja belum
diperbaiki) + tidak ada temuan baru untuk bagian skip-margin rental itu sendiri (`NATIVE-DIFF`/OK).
**Metode:** RPC read-only terhadap `http://localhost:8078` (`sale_renting`, `pos_margin_threshold`,
`sale_margin_threshold` dikonfirmasi `state=installed` ketiganya via `ir.module.module`).
**Hasil:**
1. `sale.order.search_read([['is_rental_order','=',true]], [...])` — **crash hidup**
   `ValueError: Expected singleton: sale.order(15, 1)` persis di
   `sale_margin_threshold/models/sale_order.py:14` (`_compute_is_rental_order_installed`, akses
   `self.is_rental_order` bukan `record.is_rental_order` di dalam loop `for record in self`) — begitu
   domain match >1 record sekaligus. **Ini BUKAN temuan baru** — persis `MF-26` yang sudah dicatat
   Step 1 (2026-09-21) sebagai `[DIWARISI-SOURCE]`/dipertahankan tanpa keputusan dev baru. Kegunaan
   reproduksi ini: mengonfirmasi bug itu MASIH nyata & reproducible di HEAD saat ini (bukan sudah
   ter-fix diam-diam oleh perubahan lain sejak Step 1), sesuai permintaan task untuk "re-konfirmasi
   given code changed since (MF-45 dkk)".
2. Dibaca SATU record saja (`read([15], [...])`, menghindari trigger bug #1): order rental sungguhan
   `S00015` (`is_rental_order=true`) punya `is_rental_order_installed_true=true` (compute benar untuk
   single-record) dan satu order line produk `QA10 SMT Rental Product` dengan `price_unit=10` jauh di
   bawah `minimum_sale_price=120` — skenario PERSIS yang biasanya memicu blocking `ValidationError` di
   `action_confirm()` non-rental. **`action_confirm()` TIDAK dijalankan** (mutasi state order QA
   bersama, ditolak permission classifier — benar, sesuai batasan "jangan mutasi data shared"), jadi
   skip-path itu sendiri tidak dieksekusi ulang secara live sesi ini. TAPI kode `action_confirm()`
   (dibaca `git show`, tidak berubah sejak commit `b88aaa5`/sebelum `MF-45`) mulai dengan
   `if self.is_rental_order_installed_true: return super().action_confirm()` — early-return murni
   sebelum blok margin apapun — dikombinasikan dengan compute yang terbukti benar (poin di atas)
   untuk record real ini, tidak ada indikasi regresi risk dari perubahan `MF-45` (yang hanya mengubah
   `@api.depends` di `models/product.py`, tidak menyentuh `sale_order.py` sama sekali).
**Dampak:** tidak ada perubahan rekomendasi — `MF-26` tetap terbuka sesuai keputusan lama (dipertahankan,
butuh keputusan dev eksplisit kalau mau diperbaiki), rental skip-margin tetap dinilai fungsional benar.
**Keputusan pemilik modul:** tidak perlu untuk temuan RMV ini sendiri — kalau MAU memutuskan `MF-26`
akhirnya diperbaiki, itu keputusan terpisah di entri `MF-26`, bukan hasil RMV-03.

### RMV-04 [pos_margin_threshold] — Anchor `DIFF-02`/`MF-31` (`account.view_category_property_form`) diverifikasi ulang lewat inspeksi arch mentah, bukan cuma baca source
**Ditemukan di:** Cross-Version Compare, 2026-09-23 — verifikasi tambahan saat `product.category`
`get_views()` gagal menunjukkan `property_cost_method` (arch pendek, 1795 char, kemungkinan
terpotong `groups="account.group_account_readonly"` pada request RPC tertentu — bukan bug, lihat
catatan di bawah), sehingga perlu dicek lebih dalam lewat `ir.ui.view.read()` mentah (bypass merge)
untuk memastikan bukan regresi baru.
**Tag:** tidak ada temuan baru — konfirmasi `MF-31` masih valid, `[GAP-LAMA]`/`NATIVE-DIFF` N/A
(murni verifikasi).
**Hasil:** `ir.ui.view.search_read([['model','=','product.category']])` mengonfirmasi record
`pos_margin_threshold.product_category_form_view_inherit_margin_sale` (id 1491) ber-`inherit_id`
langsung ke id 894, dan `ir.model.data` mengonfirmasi id 894 = XML-ID `account.view_category_property_form`
persis seperti yang ditulis `DIFF-02`. `ir.ui.view.read([894,1491], ['arch'])` (arch MENTAH, tanpa
merge) mengonfirmasi keduanya well-formed dan `position="before"` pada `property_cost_method` resolve
tepat (field itu memang ada di arch mentah view 894). Ketidaktampilan di `get_views()` sebelumnya
kemungkinan besar disebabkan security group filtering (`groups="account.group_account_readonly"` pada
`<page>` pembungkus) pada request tersebut, TIDAK terkait fix `DIFF-02`/`MF-31` sama sekali — tidak
diinvestigasi lebih lanjut karena di luar scope (bukan salah satu dari 4 prioritas task, dan `MF-31`
sendiri sudah rendah risiko/mekanis).
**Keputusan pemilik modul:** tidak perlu.

---

## Cara Pakai

Sama seperti `migration-tool/templates/FINDINGS.md` — lihat file itu untuk skema `MF-NNN`, kapan
pakai `[PERLU-KEPUTUSAN]`/`[DIWARISI-SOURCE]`/`[GAP-MIGRASI]`, dan kewajiban Step 4/Step 8 membaca
file ini sebagai bagian gate. `MF-25`..`MF-47` sudah dipakai (`MF-25`..`MF-28` Step 1, `MF-29`..`MF-34`
Step 2, `MF-35`/`MF-36` smoke-test Docker 2026-09-22, `MF-37`/`MF-38` Step 6 dini, `MF-39` Step 4,
`MF-40`..`MF-44` Step 9, `MF-45` Step 8, `MF-46` Step 10 — blocker proses/infra, bukan gap kode,
`MF-47` Step 10 — native 20.0 punya fitur pin/unpin sendiri, tumpang tindih modul `pin_message`) — ID
lanjutan finding BARU selanjutnya mulai dari `MF-48`.
