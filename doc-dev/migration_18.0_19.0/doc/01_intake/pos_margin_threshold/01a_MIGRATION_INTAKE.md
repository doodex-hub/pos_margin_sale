# Migration Intake — pos_margin_threshold

**Step:** 1 — Intake & Scope
**Versi:** 18.0 → 19.0
**Tanggal:** 2026-08-26
**Status:** 🔄 Draft ditulis, gate BELUM ditutup — menunggu jawaban dev di §0 (folder referensi)

---

## 0. Folder Referensi — WAJIB Ditanyakan ke Dev SEKARANG

**Checklist:**

- [ ] `native-target` (Odoo 19.0 Community) — **belum dijawab dev.** Ditanya di akhir sesi bootstrap
  (2026-08-26), belum ada respons eksplisit. **BLOCKING gate Step 1 ini** sampai dijawab.
- [ ] `native-source` (Odoo 18.0 Community) — opsional, juga belum dijawab.
- [ ] `native-target-enterprise` — **WAJIB dijawab, bukan opsional lagi**: dependency map modul
  sibling `sale_margin_threshold` (lihat dokumen modul itu) mengonfirmasi ketergantungan RUNTIME
  (bukan manifest `depends`, cek `hasattr(self, 'is_rental_order')`) ke modul Rental — berlisensi
  Enterprise. `pos_margin_threshold` sendiri TIDAK menyentuh field/model Enterprise apapun secara
  langsung (dependency map §2 di bawah: `base`, `point_of_sale`, `product`, `stock_account`, semua
  Community) — tapi karena ketiga modul dikerjakan sebagai satu project/branch, `native-target-enterprise`
  tetap wajib tersedia sebelum Step 2 project ini dianggap selesai (Step 2 `sale_margin_threshold`
  butuh ini).
- [ ] `third-party-source`/`third-party-target` — tidak ada indikasi OCA/vendor dari scan manifest
  modul ini. Tetap wajib ditanya eksplisit (belum dijawab dev): dikonfirmasi tidak ada?

**Status:** belum bisa ditutup. Lihat pertanyaan konkret di ringkasan akhir sesi.

### 0a. Konfirmasi Branch/Versi `source-codebase` & `target-codebase`

- [x] Model **dual-branch** (bukan dual-clone) — dikonfirmasi dev di kickoff (2026-08-26): source =
  branch `migration/18.0` (read-only, dibaca lewat `git show`/`git diff`, tidak pernah di-checkout),
  target = branch `migration/19.0_target` (working branch, sudah checkout, sudah jadi HEAD saat ini).
- [x] Kedua branch bukan folder yang sama secara fisik — benar, satu repo git, dua branch, target
  branch yang aktif di working tree ini.
- [x] Versi Odoo semantik: **18.0 → 19.0** — dikonfirmasi eksplisit dev di kickoff ("Lakukan migrasi
  18 ke 19"), konsisten dengan `__manifest__.py` (`version: '18.0.1.0'`, dikonfirmasi §7 di bawah).

### 0b. Gate: Lengkapi Path Absolut di `.claude/settings.json`

`Environment eksekusi = Claude Code CLI` dan `.claude/settings.json` sudah ter-bootstrap (varian
Mode Git) — gate ini berlaku.

- [x] `ABS_PATH_MIGRATION_TOOL` — diisi `D:\Kuncoro\doodex\repo\migration-tool-project\migration-tool`
  (3 baris: `Edit` allow migration-records, `Edit` deny knowledge/, `Edit` deny templates/).
- [ ] `ABS_PATH_SOURCE_CODEBASE` — **N/A untuk project ini**, deviasi disengaja dari template standar:
  model dual-branch (§Adaptasi dual-branch `CLAUDE.md`) tidak punya folder `source-codebase` fisik
  terpisah sama sekali — source dibaca lewat `git show migration/18.0:<path>` di repo yang sama,
  tidak ada path filesystem lain yang perlu diproteksi lewat `Edit deny`. Baris
  `Edit(//{{ABS_PATH_SOURCE_CODEBASE}}/**)` di `settings.json` dihapus (bukan diisi placeholder
  kosong) — dicatat di sini supaya jelas ini keputusan sadar, bukan terlewat.
- [ ] `ABS_PATH_NATIVE_TARGET` / `ABS_PATH_NATIVE_TARGET_ENTERPRISE` / `ABS_PATH_NATIVE_SOURCE` —
  **belum bisa diisi**, menunggu jawaban dev di §0 di atas. Placeholder tetap literal
  `{{ABS_PATH_...}}` untuk sekarang (rule-nya inert, bukan salah — tapi harus diisi sebelum Step 2
  mulai).
- [ ] `ABS_PATH_THIRD_PARTY_SOURCE` / `ABS_PATH_THIRD_PARTY_TARGET` — belum dikonfirmasi dipakai atau
  tidak (§0). Kalau dev konfirmasi tidak ada dependency OCA, baris ini akan DIHAPUS (bukan dibiarkan
  placeholder).

**`.claude/settings.json` BELUM final** — akan diedit lagi begitu §0 terjawab.

---

## Ringkasan untuk Review — Perlu Konfirmasi User

1. **[BLOCKING]** Belum dijawab: apakah `native-target` (Odoo 19.0 Community) sudah ada di disk?
   Path-nya? Sama untuk `native-source` (18.0, opsional), `native-target-enterprise` (wajib
   dikonfirmasi karena `sale_margin_threshold` — modul sibling di project yang sama — punya
   ketergantungan runtime opsional ke modul Rental Enterprise), dan `third-party-*` (scan tidak
   menemukan indikasi OCA, tapi tetap wajib dikonfirmasi eksplisit, bukan diasumsikan dari scan
   kosong).
2. **Asumsi yang perlu dikonfirmasi:** modul ini tidak punya dependency Enterprise/OCA LANGSUNG
   sendiri (semua di `depends`: `base`, `point_of_sale`, `product`, `stock_account`, semua Native
   Community) — benar?
3. **File mati, dipertahankan mati (bukan bug baru, warisan 17.0→18.0, `MF-04` project sebelumnya):**
   `views/product_template_views.xml` ada di disk tapi TIDAK terdaftar di manifest `data:` — duplikat
   XML-ID (`product_template_inherit_pos_margin_threshold`) dengan record aktif di `views/products.xml`
   yang targetnya beda (`product.product_template_only_form_view` vs `product.product_template_form_view`).
   Harus tetap mati di 19.0 kecuali user eksplisit minta diaktifkan/dihapus.
4. **Quirk warisan yang harus tetap identik di 19.0 (bukan bug untuk diperbaiki):**
   - `MF-01`: `margin_sale` di `product.product` inverse-nya menulis balik ke `product_tmpl_id`
     (template bersama) — margin per-variant TIDAK PERNAH bisa berbeda dari template-nya, walau field
     itu ada di level variant.
   - `MF-02`: field `blocking_transaction_order` dideklarasikan di `res.config.settings` tapi TIDAK
     PERNAH dibaca modul ini sendiri — cuma berefek kalau `sale_margin_threshold` juga terinstall.
   - `MF-03`: model `wizard.margin.product` didefinisikan dengan `_name` (bukan `_inherit`) di modul
     INI dan di `sale_margin_threshold` secara byte-identik — kalau kedua modul terinstall bersamaan,
     class `sale_margin_threshold` yang SELALU menang di `__mro__` (dikonfirmasi empiris 2026-08-26,
     independen urutan install `-i`), class modul ini hilang total dari registry. Risiko: kalau salah
     satu wizard diubah sendirian tanpa sinkron ke yang lain, silent-override.
   - Typo `action_assing_margin` (bukan "assign") di method Python DAN nama field XML — harus
     dipertahankan identik (nama method direferensikan langsung oleh view).
5. **Prioritas riset Step 2 (arsitektur JS POS paling berisiko berubah lagi di 19.0):** seluruh
   integrasi JS/Owl modul ini adalah *patch* terhadap komponen inti `point_of_sale` yang SUDAH sekali
   pindah total struktur di migrasi 17→18 (`Order`/`Orderline`/`Product` → `PosOrder`/`PosOrderline`/
   `ProductProduct`, path baru, `Order.pay()` → `PosStore.pay()`, popup service dihapus,
   `_load_pos_data_fields` API baru, Owl props-shape strict validation, xpath `orderline.xml`
   descendant-selector). Area yang sama ini adalah kandidat pertama breaking change lagi di 19.0 —
   tidak bisa diasumsikan stabil dari fakta method-level API bertahan 17→18.
6. **Gap test yang masih terbuka dari project 17.0→18.0 (bukan blocker, tapi carry-forward, keputusan
   user diperlukan apakah ditutup di project ini atau tetap dilewati):** AC-02-03 (tidak ada popup
   sama sekali kalau tidak ada line di bawah minimum — belum pernah ditest otomatis) dan AC-02-04
   (assert teks/warna merah warning di orderline secara terpisah — belum pernah diassert eksplisit).
   Keduanya butuh sesi POS register penuh untuk ditest.

---

## 1. Modul & Scope

- **Modul yang dimigrasi:** `pos_margin_threshold` (satu dari tiga addon independen dalam project
  ini — lihat `CLAUDE.md` §Adaptasi multi-modul).
- **Deskripsi singkat:** menambahkan margin minimum penjualan (`margin_sale`) per kategori/produk,
  menghitung `minimum_sale_price`/`minimum_sale_price_with_tax`, dan mem-block/mengonfirmasi
  pembayaran di Point of Sale kalau harga jual di bawah minimum (blocking atau confirm, tergantung
  setting `blocking_transaction_pos`).
- **Saling depend dengan modul lain?** Tidak ada dependency Python/manifest formal ke
  `sale_margin_threshold`/`pin_message`. Interaksi RUNTIME dengan `sale_margin_threshold`: kolisi
  model `wizard.margin.product` (`_name` sama, lihat `MF-03`). Tidak ada interaksi dengan
  `pin_message` sama sekali.

## 2. Dependency Map (auto-scan)

| Dependency | Tipe | Versi tersedia di target? | Catatan |
|---|---|---|---|
| `base` | Native Community | Belum dicek (`native-target` belum di-connect) | — |
| `point_of_sale` | Native Community | Belum dicek | Integrasi terberat — patch JS/Owl, `_load_pos_data_fields`. Prioritas riset Step 2. |
| `product` | Native Community | Belum dicek | `product.category`/`product.template`/`product.product` inherit + XML inherit ke `product.product_template_form_view`/`product.product_template_only_form_view`/`product.product_variant_easy_edit_view` |
| `stock_account` | Native Community | Belum dicek | Hanya lewat XML `inherit_id="stock_account.view_category_property_form_stock"`, tidak ada `_inherit` Python |

**Tidak ada baris Enterprise di dependency map modul ini sendiri** — tapi lihat §0 di atas, project
ini (3 modul) tetap wajib `native-target-enterprise` karena `sale_margin_threshold`.

Dependency opsional yang dicek runtime (tidak di manifest):
- **`sale_margin_threshold`** (modul custom sibling, bukan Odoo native) — kolisi `_name` model
  `wizard.margin.product` (`MF-03`). Tidak dideklarasikan di `depends` manapun, MRO merge terjadi
  murni dari kesamaan `_name` Python.

## 2b. Struktur & Fitur Modul (auto-scan)

| Fitur | Ada di modul? | Lokasi/bukti | Fase step 6 relevan |
|---|---|---|---|
| Controllers (route custom) | ☐ Tidak (scaffold mati) | `controllers/controllers.py` — seluruh body di-comment, `controllers/__init__.py` tetap import (no-op) | D1 — kandidat N/A |
| Assets/CSS/JS custom | ☑ Ya | `assets.point_of_sale._assets_pos` → `static/src/**/*`; `assets.web.assets_tests` → `static/tests/tours/**/*` (manifest) | D2, E, F — WAJIB full treatment |
| Komponen Owl/JavaScript custom | ☑ Ya (patch, bukan komponen baru) | `patch(ProductProduct.prototype)`/`patch(PosOrderline.prototype)`/`patch(Orderline.props.line.shape)` (`static/src/store/models/models.js`), `patch(PosStore.prototype)` (`static/src/store/pos_store.js`) | E — prioritas tertinggi, area paling sering breaking antar versi POS |
| Field JSON / relasi berantai >2 level / dynamic model creation | ☐ Tidak | Semua field Float/Boolean langsung, tidak ada `self.env[var]` di manapun (grep bersih) | B2 — N/A |
| View pakai `attrs=`/`states=`/domain/context dinamis | ☐ Tidak (pakai syntax modern `invisible=`/`decoration-*=`, bukan `attrs=` legacy) | `views/products.xml`, `views/product_template_views.xml` (dead file) | C2 — kemungkinan N/A, verifikasi ulang syntax `invisible=`/`decoration-danger=` masih valid di 19.0 |

## 3. Sifat Migrasi

- [x] Port kode saja (tidak ada data produksi — instalasi baru di 19.0)
- [ ] Upgrade instance

## 4. Baseline Spec / Characterization Test (gate)

- [x] Tidak ada `FUNCTIONAL_SPEC.md` lama TERPISAH di `pos_margin_threshold` sendiri untuk siklus
  ini — sumber baseline untuk project 18.0→19.0 ini adalah
  `doc-dev/migration_17.0_18.0/doc/01_intake/pos_margin_threshold/01b_BASELINE_SPEC.md` (baseline
  18.0 hasil project migrasi SEBELUMNYA, sudah lulus 11 step + UAT) — diperlakukan persis seperti
  "spec lama": dibaca, di-cross-check ke kode 18.0 aktual (branch `migration/18.0`, identik dengan
  working tree saat ini), digabung dengan `FINDINGS.md` project itu untuk menangkap perubahan yang
  terjadi SELAMA migrasi 17→18 tapi belum tercermin di teks BSL lama. Hasil: `01b_BASELINE_SPEC.md`
  (dokumen ini, versi 18.0→19.0) — lihat dokumen terpisah.
- [x] `01b_BASELINE_SPEC.md` sudah diisi, termasuk "Ringkasan untuk Review" dan ID `BSL-NNN` per klaim.

### 4a. Dokumen Pelengkap Lain

- [x] Tidak ada dokumen pelengkap lain di luar kode + dokumentasi `doc-dev/migration_17.0_18.0/` —
  belum dikonfirmasi eksplisit ke dev (asumsi sementara, konsisten pola project sebelumnya yang juga
  tidak punya dokumen eksternal). **Perlu konfirmasi eksplisit dev** kalau ada PRD/manual/spec Excel
  di luar repo yang belum diketahui AI.

## 4b. Source Masih Aktif Dikembangkan?

- [x] Tidak — source (`migration/18.0`) dibekukan selama migrasi 19.0 berjalan (konsisten keputusan
  project 17.0→18.0 sebelumnya, belum dikonfirmasi ulang eksplisit oleh dev untuk project ini
  — lihat `[PERLU-KEPUTUSAN]` di `CLAUDE.md`).

## 5. Scope Boundary

- **Harus tetap identik pasca migrasi:** semua business rule di §4 `01b_BASELINE_SPEC.md`
  (`BSL-001`..dst), termasuk SEMUA quirk warisan (`MF-01`, `MF-02`, `MF-03`, `MF-04`, typo
  `action_assing_margin`) — tidak satupun diperbaiki tanpa persetujuan eksplisit user.
  Method-level API POS (`get_unit_display_price()`, dst) yang sudah terbukti stabil 17→18 tidak boleh
  diasumsikan otomatis stabil lagi 18→19 — wajib diverifikasi ulang ke `native-target` 19.0 nyata di
  Step 2.
- **Yang sengaja diubah/di-drop:** tidak ada usulan perubahan disengaja untuk migrasi ini. Kalau Step
  2/6 menemukan API 19.0 yang memang mengharuskan perubahan (bukan pilihan), itu dicatat sebagai
  `MF-NNN` baru di `FINDINGS.md`, bukan dianggap "scope boundary" awal.

## 6. Constraint

- Deadline: belum disebutkan dev.
- Owner tiap step: belum disebutkan dev (asumsi: dev yang sama seperti project 17.0→18.0, belum
  dikonfirmasi ulang).
