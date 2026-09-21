# Findings — pos_margin_threshold / sale_margin_threshold / pin_message (migrasi 19.0 → 20.0)

> Cross-cutting, satu file untuk ketiga modul (lihat CLAUDE.md §"Adaptasi multi-modul"). Prefix
> judul finding dengan nama modul. Lihat `migration-tool/templates/FINDINGS.md` untuk beda peran
> file ini dari tag `[GAP]`/format `ESCALATION`, skema ID `MF-NNN`, dan cara pakai lengkap.

**Modul:** pos_margin_threshold, sale_margin_threshold, pin_message
**Migrasi:** 19.0 → 20.0
**Terakhir update:** 2026-09-21 (Step 1 — Intake & Baseline Spec, ketiga modul)

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
| MF-28 | [pin_message] **KRITIS** — native 20.0 `mail.message` TIDAK PUNYA `_to_store()` lagi (diganti `_store_message_fields()`/`Store.FieldList`) — override modul akan gagal total kalau di-port mekanis | Step 1, project 19.0→20.0 (2026-09-21) | `[GAP-MIGRASI]` | **Tertinggi** | 🔴 Terbuka — riset Step 2 WAJIB memprioritaskan ini sebelum fase manapun di Step 6 |

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
**Rekomendasi:** Step 2 (Diff Analysis) WAJIB menjadikan ini riset prioritas #1 untuk `pin_message` —
baca penuh pola `_store_message_fields()`/`Store.FieldList` di native 20.0 sebelum menulis
`03_MIGRATION_SPEC.md`. Jangan mulai Step 6 fase manapun untuk modul ini sebelum area ini selesai
diriset.
**Keputusan pemilik modul:** *(kosong — baru ditemukan, bukan keputusan user, tapi riset teknis Step 2)*

---

## Cara Pakai

Sama seperti `migration-tool/templates/FINDINGS.md` — lihat file itu untuk skema `MF-NNN`, kapan
pakai `[PERLU-KEPUTUSAN]`/`[DIWARISI-SOURCE]`/`[GAP-MIGRASI]`, dan kewajiban Step 4/Step 8 membaca
file ini sebagai bagian gate. `MF-25`..`MF-28` sudah dipakai (ditemukan Step 1, 2026-09-21) — ID
lanjutan finding BARU selanjutnya mulai dari `MF-29`.
