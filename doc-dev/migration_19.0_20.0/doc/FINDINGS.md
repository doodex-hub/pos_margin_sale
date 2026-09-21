# Findings — pos_margin_threshold / sale_margin_threshold / pin_message (migrasi 19.0 → 20.0)

> Cross-cutting, satu file untuk ketiga modul (lihat CLAUDE.md §"Adaptasi multi-modul"). Prefix
> judul finding dengan nama modul. Lihat `migration-tool/templates/FINDINGS.md` untuk beda peran
> file ini dari tag `[GAP]`/format `ESCALATION`, skema ID `MF-NNN`, dan cara pakai lengkap.

**Modul:** pos_margin_threshold, sale_margin_threshold, pin_message
**Migrasi:** 19.0 → 20.0
**Terakhir update:** 2026-09-21

---

## Ringkasan

| ID | Judul | Ditemukan di Step | Tag | Prioritas | Status |
|---|---|---|---|---|---|
| MF-20 | [sale_margin_threshold] `security/groups.xml` `implied_ids` diisi kategori bukan grup | Dibawa dari project 18.0→19.0, Step 8 | `[DIWARISI-SOURCE]` | Sedang | 🔵 Terbuka — belum ada keputusan user |
| MF-21 | [sale_margin_threshold] `_compute_warning` (`is_less_minimum_sale`) tanpa `@api.depends` | Dibawa dari project 18.0→19.0, Step 8 | `[DIWARISI-SOURCE]` | Sedang | 🔵 Terbuka — belum ada keputusan user |
| MF-23 | [pos_margin_threshold] `_compute_warning` (`is_less_minimum_sale`), instance terpisah dari MF-21 | Dibawa dari project 18.0→19.0, Step 8 | `[DIWARISI-SOURCE]` | Sedang | 🔵 Terbuka — belum ada keputusan user |
| MF-24 | [pos_margin_threshold] `list_price` di-`position="replace"` bukan `attributes`, diam-diam menghapus atribut core | Dibawa dari project 18.0→19.0, Step 8 | `[DIWARISI-SOURCE]` | Sedang | 🔵 Terbuka — belum ada keputusan user |
| MF-08 | [sale_margin_threshold] `action_confirm()` singleton-assumption, pecah di batch-confirm | Dibawa dari project 17.0→18.0, dikonfirmasi tetap ada di 18.0→19.0 | `[DIWARISI-SOURCE]` | Tinggi | 🔵 Terbuka — **[KEPUTUSAN USER 2026-08-27, project 18.0→19.0]: dipertahankan**, jangan diperbaiki tanpa keputusan baru |

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
**Keputusan pemilik modul:** *(kosong — belum diputuskan, dibawa dari project sebelumnya)*

### MF-08 — `action_confirm()` singleton-assumption pecah di batch-confirm
**Ditemukan di:** project 17.0→18.0, dikonfirmasi ulang project 18.0→19.0 (blast radius sama, tidak
lebih parah)
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `FINDINGS.md` project 18.0→19.0
**Lokasi:** `sale_margin_threshold` — override `action_confirm()`.
**Keputusan pemilik modul:** **Dipertahankan** (keputusan user 2026-08-27, project 18.0→19.0: "biarkan
dulu, pastikan tercatat di finding"). Jangan diperbaiki di project ini tanpa keputusan baru eksplisit.

---

## Cara Pakai

Sama seperti `migration-tool/templates/FINDINGS.md` — lihat file itu untuk skema `MF-NNN`, kapan
pakai `[PERLU-KEPUTUSAN]`/`[DIWARISI-SOURCE]`/`[GAP-MIGRASI]`, dan kewajiban Step 4/Step 8 membaca
file ini sebagai bagian gate. ID lanjutan finding BARU di project ini mulai dari `MF-25` (supaya
tidak bertabrakan dengan ID yang dibawa dari project 18.0→19.0 di atas).
