# Migration Intake — sale_margin_threshold

**Step:** 1 — Intake & Scope
**Versi:** 18.0 → 19.0
**Tanggal:** 2026-08-26
**Status:** 🔄 Draft ditulis, native-target/enterprise RESOLVED, menunggu jawaban dev soal
third-party/OCA sebelum gate ditutup penuh

---

## 0. Folder Referensi — WAJIB Ditanyakan ke Dev SEKARANG

**Checklist:**

- [x] `native-target` (Odoo 19.0 Community) — **dikonfirmasi dev 2026-08-26:**
  `D:\Kuncoro\doodex\repo\enterprise19.0`.
- [ ] `native-source` (Odoo 18.0 Community) — opsional, belum dijawab.
- [x] **`native-target-enterprise` — RESOLVED, folder gabungan dengan `native-target`.**
  Dikonfirmasi via `ls` (2026-08-26): `enterprise19.0` adalah struktur repo Odoo penuh dengan
  Community DAN Enterprise tergabung di `odoo/addons/` yang sama (bukan Enterprise-addons-only,
  bukan git repo). **Sanity check awal (bukan Step 2 penuh):** `sale_renting` ADA di
  `odoo/addons/sale_renting/`, dan `is_rental_order` dikonfirmasi masih ada persis nama itu di
  `sale_renting/models/sale_order.py` (19.0) — field yang dicek `hasattr()` oleh modul ini
  (`models/sale_order.py:14`) MASIH ADA di 19.0. Ini bukan verifikasi lengkap (belum cek signature/
  behavior detail), cuma konfirmasi awal field-nya tidak hilang/rename — detail lengkap tetap
  domain Step 2.
- [ ] `third-party-source`/`third-party-target` — tidak ada indikasi OCA/vendor dari scan manifest.
  Belum dikonfirmasi eksplisit ke dev.

**Status:** sisa satu item non-blocking (third-party) sebelum gate ditutup penuh.

### 0a. Konfirmasi Branch/Versi

- [x] Sama seperti modul lain di project ini — dual-branch: source `migration/18.0` (read-only),
  target `migration/19.0_target` (aktif). Versi 18.0→19.0 dikonfirmasi eksplisit dev.

### 0b. Gate: Path Absolut `.claude/settings.json`

Sama seperti modul lain — lihat `01a_MIGRATION_INTAKE.md` `pos_margin_threshold` §0b untuk status
identik (satu `.claude/settings.json` untuk seluruh repo/project, bukan per-modul).
`ABS_PATH_NATIVE_TARGET_ENTERPRISE` **KHUSUSNYA relevan untuk modul ini** — belum bisa diisi sampai
dev menjawab §0.

---

## Ringkasan untuk Review — Perlu Konfirmasi User

1. **[RESOLVED]** `native-target`/`native-target-enterprise` = `D:\Kuncoro\doodex\repo\enterprise19.0`
   (folder gabungan). Sanity check awal: `is_rental_order` masih ada di `sale_renting` 19.0.
2. **Konfirmasi tidak ada `sale.order.line.tax_id`:** dicek langsung (grep penuh Python/XML/JS) —
   modul ini TIDAK menyentuh field `tax_id` pada `sale.order.line` sama sekali (yang ada cuma
   `product.template.taxes_id`, field berbeda, tidak terdampak rename 19.0). Jadi breaking-change
   `sale.order.line.tax_id`→`tax_ids` yang dicatat di `migration-tool/knowledge/version-diffs/18-to-19.md`
   **DIKONFIRMASI TIDAK RELEVAN** untuk modul ini — dicatat balik ke `FINDINGS.md` §Kandidat dari
   knowledge base.
3. **Bug warisan berprioritas TINGGI yang harus dipertahankan (bukan diperbaiki tanpa izin), tapi
   perlu keputusan user apakah tetap dipertahankan atau ini kesempatan baik untuk memperbaikinya:**
   `MF-06` — `action_confirm()` mengasumsikan `self` singleton (baca `self.is_rental_order_installed_true`/
   `self.order_line` tanpa `for order in self:`) — akan salah kalau Odoo core memanggil override ini
   dalam mode batch (multi-record) confirm. Ini bug lama (warisan sejak sebelum migrasi 17→18),
   ditandai prioritas **Tinggi** dan masih **terbuka** di `FINDINGS.md` project sebelumnya — belum
   pernah diperbaiki. **Perlu keputusan eksplisit:** pertahankan identik (risiko: masih bisa salah
   kalau core 19.0 memanggil batch-confirm) atau perbaiki sebagai bagian scope migrasi ini (butuh
   persetujuan eksplisit, dicatat sebagai perubahan disengaja)?
4. **Dua bug/gap lain warisan, prioritas Sedang, harus dipertahankan identik kecuali user putuskan
   lain:**
   - `MF-05`: `ProductProduct._register_hook()` memutasi membership grup `group_sale_margin_action`
     SETIAP registry rebuild (bukan cuma saat install) — kalau admin mengubah membership grup ini
     manual, bisa ter-reset diam-diam di reload berikutnya.
   - `MF-07`: dua file (`views/product_template_views.xml` DAN `views/products.xml`) sama-sama
     terdaftar di manifest `data:` dan sama-sama mendefinisikan XML-ID
     `product_template_inherit_sale_margin_threshold` — yang dimuat KEDUA (`products.xml`) menimpa
     total record pertama (termasuk `inherit_id`-nya), jadi kustomisasi yang dituju ke
     `product.product_template_only_form_view` tidak pernah benar-benar aktif. **Ini LEBIH serius
     dari `MF-04` modul sibling** (di sana file duplikatnya memang sengaja tidak dimuat; di sini
     KEDUA dimuat, salah satu diam-diam kalah).
   - `MF-08`: manifest deklarasikan `assets.sale_margin_threshold._assets_sale` menunjuk
     `static/src/**/*`, tapi folder itu TIDAK ADA di disk — glob kosong, tidak error, tapi cruft.
5. **Kolisi model `wizard.margin.product` dengan `pos_margin_threshold` (`MF-03`):** modul INI yang
   SELALU menang MRO (dikonfirmasi empiris, independen urutan install) — lihat detail lengkap di
   dokumen `pos_margin_threshold`. Risiko sama: silent-override kalau salah satu diubah sendirian.
6. **`MF-21` (bilingual EN/FR) sudah RESOLVED** sebelum baseline ini ditulis — dikonfirmasi ulang di
   kode aktual (§8 di bawah), tidak perlu keputusan baru, hanya harus dipertahankan.

---

## 1. Modul & Scope

- **Modul:** `sale_margin_threshold`.
- **Deskripsi:** menegakkan margin minimum di alur konfirmasi Sale Order (`action_confirm`) — kalau
  ada baris order dengan harga di bawah `minimum_sale_price`, sistem memblok konfirmasi
  (`ValidationError`) atau meminta konfirmasi via wizard, tergantung setting
  `blocking_transaction_order`. Rental order (Enterprise) sepenuhnya dikecualikan. Modul juga
  menyediakan wizard bulk-assign margin yang identik strukturnya dengan `pos_margin_threshold`.
- **Saling depend dengan modul lain?** Tidak ada dependency Python/manifest formal. Interaksi
  RUNTIME: kolisi `_name` `wizard.margin.product` dengan `pos_margin_threshold` (`MF-03`,
  `sale_margin_threshold` menang), `_register_hook()` dan `module_pos_margin_threshold` compute
  keduanya mengecek `ir.module.module` untuk tahu apakah `pos_margin_threshold` terinstall (murni
  introspeksi, bukan dependency formal).

## 2. Dependency Map (auto-scan)

| Dependency | Tipe | Versi tersedia di target? | Catatan |
|---|---|---|---|
| `base` | Native Community | Belum dicek | — |
| `product` | Native Community | Belum dicek | — |
| `sale` | Native Community | Belum dicek | **Prioritas riset Step 2** — `action_confirm()` override, model paling mungkin berubah struktural |
| `stock_account` | Native Community | Belum dicek | Sama seperti modul sibling — cuma lewat XML inherit |

**Dependency Enterprise (implisit, runtime, bukan `depends` formal):** Modul Rental
(`is_rental_order`, family `sale_renting`/`sale_temporal`) — dicek via `hasattr()`, TIDAK
mewajibkan instalasi, tapi behavior beda tergantung ada/tidaknya. **Lihat §0 — ini alasan
`native-target-enterprise` wajib untuk modul ini.**

Dependency opsional yang dicek runtime (tidak di manifest):
- **`pos_margin_threshold`** (custom sibling) — dicek via `ir.module.module` di dua tempat
  (`_register_hook()`, `_compute_module_pos_margin_threshold`), plus kolisi `_name`
  `wizard.margin.product` (lihat §8 baseline spec).

## 2b. Struktur & Fitur Modul (auto-scan)

| Fitur | Ada di modul? | Lokasi/bukti | Fase step 6 relevan |
|---|---|---|---|
| Controllers (route custom) | ☐ Tidak (scaffold mati) | `controllers/controllers.py` — semua di-comment | D1 — kandidat N/A |
| Assets/CSS/JS custom | ☐ Tidak (secara FUNGSIONAL) | Manifest deklarasikan `assets.sale_margin_threshold._assets_sale` → `static/src/**/*`, tapi folder `static/src/` **tidak ada di disk** (`MF-08`) — glob kosong, tidak ada file JS/CSS aktual sama sekali | D2, E, F — N/A murni (tidak ada yang perlu diporting) |
| Komponen Owl/JavaScript custom | ☐ Tidak | Tidak ada file `.js` di modul ini sama sekali | E, F — N/A |
| Field JSON / relasi berantai >2 level / dynamic model creation | ☑ Ya (dynamic model access, bukan JSON/deep-chain) | `wizard/sale_confirmation.py`: `self.env[active_model].browse(active_id)` — `active_model` dari context, resolusi dinamis saat runtime (nilai aktual selalu `'sale.order'` tapi ditulis generik) | B2 — perlu dicek konsep `self.env[var]` masih valid identik di 19.0 (kemungkinan besar ya, API dasar ini stabil lintas versi, tapi verifikasi tetap wajib) |
| View pakai `attrs=`/`states=`/domain/context dinamis | ☐ Tidak (syntax modern `invisible=`/`decoration-*=`) | `views/sale_order.xml`, `views/products.xml` | C2 — kemungkinan N/A, verifikasi syntax masih valid 19.0 |

## 3. Sifat Migrasi

- [x] Port kode saja
- [ ] Upgrade instance

## 4. Baseline Spec / Characterization Test (gate)

- [x] Sumber: `doc-dev/migration_17.0_18.0/doc/01_intake/sale_margin_threshold/01b_BASELINE_SPEC.md`
  (baseline 18.0 dari project sebelumnya) + cross-check kode aktual + `FINDINGS.md`/`05a`/`10_qa`
  project itu. Hasil: `01b_BASELINE_SPEC.md` (dokumen ini, versi 18.0→19.0).
- [x] `01b_BASELINE_SPEC.md` sudah diisi dengan ID `BSL-NNN` + provenance + "Ringkasan untuk Review".

### 4a. Dokumen Pelengkap Lain

- [x] Belum dikonfirmasi eksplisit ke dev — asumsi sementara "tidak ada", konsisten pola project
  sebelumnya. **Perlu konfirmasi eksplisit.**

## 4b. Source Masih Aktif Dikembangkan?

- [x] Tidak (asumsi, belum dikonfirmasi ulang eksplisit untuk project ini — sama seperti modul lain).

## 5. Scope Boundary

- **Harus tetap identik:** semua `BSL-NNN` di `01b_BASELINE_SPEC.md`, termasuk seluruh quirk warisan
  (`MF-03`, `MF-05`, `MF-06`, `MF-07`, `MF-08`) KECUALI user eksplisit memutuskan memperbaiki salah
  satu (lihat poin 3 §Ringkasan di atas — `MF-06` khususnya butuh keputusan eksplisit, bukan
  diasumsikan "pertahankan" secara default karena prioritasnya Tinggi).
- **Yang sengaja diubah:** tidak ada yang diusulkan di titik ini. `MF-21` (bilingual) SUDAH diperbaiki
  di siklus sebelumnya (disetujui eksplisit dev 2026-08-26 sebelum project ini dimulai) — fix itu
  dipertahankan apa adanya, bukan dianggap "baru" untuk project ini.

## 6. Constraint

- Deadline: belum disebutkan.
- Owner: belum disebutkan.
