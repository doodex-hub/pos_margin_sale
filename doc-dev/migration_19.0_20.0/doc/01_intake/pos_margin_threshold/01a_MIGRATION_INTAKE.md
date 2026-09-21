# Migration Intake — pos_margin_threshold

**Step:** 1 — Intake & Scope
**Versi:** 19.0 → 20.0
**Tanggal:** 2026-09-21
**Status:** ✅ Draft Step 1 selesai ditulis (2026-09-21) — §0/§0a/§0b sudah terpenuhi (diwarisi dari
bootstrap project, diverifikasi ulang sesi ini); beberapa asumsi carried-forward (§3, §4a, §4b) masih
menunggu konfirmasi ULANG eksplisit dari dev — lihat "Ringkasan untuk Review" sebelum gate dianggap
✔️ LULUS penuh.

---

## 0. Folder Referensi — WAJIB Ditanyakan ke Dev SEKARANG

**Checklist — semua sudah dikonfirmasi/diisi sebelum sesi ini (bootstrap 2026-09-21, lihat `CLAUDE.md`
§"Status saat ini" & §"Folder yang perlu di-connect"), diverifikasi ulang sesi ini dengan `ls`/glob
langsung ke tiap folder (bukan cuma dipercaya dari catatan `CLAUDE.md`):**

- [x] `native-target` (Odoo 20.0 Community) — `D:\Kuncoro\doodex\repo\odoo20`, clone git resmi
  `odoo/odoo`, branch `20.0`. **Diverifikasi ulang sesi ini:** `base` ada di
  `odoo20/odoo/addons/base/__manifest__.py`; `point_of_sale`, `product`, `stock_account` ada di
  `odoo20/addons/<modul>/__manifest__.py` — keempat dependency modul ini (§2) dikonfirmasi tersedia.
- [x] `native-target-enterprise` (Odoo 20.0 Enterprise) — `D:\Kuncoro\doodex\repo\enterprise20`, clone
  git resmi Enterprise, branch `20.0`. **Folder TERPISAH dari `native-target`** (dua-clone standar,
  BUKAN folder gabungan seperti project 18.0→19.0 sebelumnya — perhatian khusus karena pola berubah
  antar project). **Diverifikasi ulang sesi ini:** struktur addons-only di root (`account_3way_match/`,
  `account_accountant/`, dst langsung di root, tidak ada `odoo/addons/`); TIDAK ada `point_of_sale`,
  `product`, `stock_account` di sini — konsisten, keempat dependency modul ini murni Native Community,
  tidak butuh apapun dari Enterprise secara langsung. Folder ini tetap wajib di-connect untuk project
  (bukan modul ini) karena `sale_margin_threshold` — modul sibling di project yang sama — punya
  dependency Rental Enterprise (lihat `CLAUDE.md` §Folder).
- [x] `native-source` (Odoo 19.0, opsional) — `D:\Kuncoro\doodex\repo\enterprise19.0`, peninggalan
  project 18.0→19.0 sebelumnya, Community+Enterprise 19.0 gabungan, **BUKAN git repo** (tidak ada
  `.git/`) — dipakai Step 2 untuk cross-check langsung ke versi asal, read-only, tidak pernah
  `git` apapun di sini.
- [ ] `third-party-source`/`third-party-target` (OCA/vendor) — **BELUM dikonfirmasi ulang eksplisit
  untuk pasangan 19.0→20.0 ini** (carried-forward dari dua project sebelumnya: "tidak ada"). Scan
  `__manifest__.py` modul ini (§2) tidak menemukan indikasi apapun (`depends` hanya `base`,
  `point_of_sale`, `product`, `stock_account`, semua Native Community) — tapi scan kosong bukan
  jawaban "tidak ada" per aturan §0. **Perlu konfirmasi eksplisit dev** — masuk "Ringkasan untuk
  Review" di bawah.

### 0a. Konfirmasi Branch/Versi `source-codebase` & `target-codebase`

- [x] Model **dual-branch** (bukan dual-clone), melanjutkan pola dua project sebelumnya — dikonfirmasi
  di `CLAUDE.md` §"Adaptasi dual-branch": source = branch `migration/19.0` (read-only, dibaca lewat
  `git show migration/19.0:<path>`/`git diff migration/20.0 migration/19.0 -- <path>`, **AI tidak
  pernah `git checkout` ke branch ini**), target = branch `migration/20.0` (working branch aktif,
  sudah jadi HEAD sesi ini).
- [x] Kedua branch bukan folder fisik yang sama — satu repo git, dua branch, `migration/20.0` yang
  aktif di working tree.
- [x] Versi Odoo semantik: **19.0 → 20.0** — dikonfirmasi eksplisit (task/kickoff sesi ini + konsisten
  `CLAUDE.md`), konsisten dengan `__manifest__.py` modul ini (`version: '19.0.1.0'`, dikonfirmasi §7 di
  bawah — angka mayor `19` cocok versi source, `.0.1.0` adalah versi modul, bukan versi Odoo).
- **Catatan penting (beda dari model standar template):** branch `migration/19.0` BUKAN cuma "source
  belum ditest" — branch itu sudah lulus 10 dari 11 step migrasi 18.0→19.0 (UAT sign-off manual masih
  menunggu eksekusi manusia, lihat `git log migration/19.0`). Artinya kode yang kita baca sebagai
  "19.0 source of truth" di seluruh dokumen ini SUDAH terverifikasi lewat Step 1-10 migrasi
  sebelumnya, bukan port kode mentah yang belum pernah direview.

### 0b. Gate: Lengkapi Path Absolut di `.claude/settings.json`

`Environment eksekusi = Claude Code CLI`, `.claude/settings.json` sudah ter-bootstrap (varian Mode
Git) — gate ini berlaku, dan **sudah terpenuhi**. Diverifikasi ulang sesi ini dengan membaca isi
`.claude/settings.json` langsung — tidak ada satupun placeholder `{{ABS_PATH_...}}` literal yang
tersisa:

- [x] `Edit(//D:/Kuncoro/doodex/repo/odoo20/**)` — deny, `native-target`.
- [x] `Edit(//D:/Kuncoro/doodex/repo/enterprise20/**)` — deny, `native-target-enterprise` (folder
  terpisah, sesuai §0 di atas).
- [x] `Edit(//D:/Kuncoro/doodex/repo/enterprise19.0/**)` — deny, `native-source`.
- [x] `Edit(//D:/Kuncoro/doodex/repo/migration-tool-project/migration-tool/knowledge/**)` dan
  `.../templates/**)` — deny, sesuai standar.
- [x] `Edit(//D:/Kuncoro/doodex/repo/migration-tool-project/migration-tool/migration-records/**)` —
  allow (satu-satunya folder tulis di `migration-tool`).
- Tidak ada baris `third-party-*` di `settings.json` — konsisten dengan status §0 di atas (belum
  dikonfirmasi ulang, tapi juga belum ada folder fisik yang perlu diproteksi).

**Gate §0b: TERPENUHI.**

---

## Ringkasan untuk Review — Perlu Konfirmasi User

1. **[CARRIED-FORWARD, belum dikonfirmasi ULANG untuk project ini]** Sifat migrasi = **"Port kode
   saja"** (§3 di bawah) — diwarisi dari keputusan dev di project 17.0→18.0 dan 18.0→19.0 untuk modul
   yang sama, **belum ditanya ulang eksplisit** untuk pasangan 19.0→20.0 ini. Diasumsikan tetap
   konsisten kecuali dev menyatakan sebaliknya.
2. **[CARRIED-FORWARD, belum dikonfirmasi ULANG]** Dokumen pelengkap lain (§4a) = **"tidak ada"** dan
   source masih aktif dikembangkan (§4b) = **"Tidak"** — keduanya asumsi warisan dari dua project
   sebelumnya, belum ditanya ulang eksplisit ke dev untuk siklus 19.0→20.0 ini.
3. **[BELUM DIKONFIRMASI]** Dependency `third-party-*`/OCA — scan `__manifest__.py` tidak menemukan
   indikasi apapun (§0), konsisten "tidak ada" dari dua project sebelumnya, tapi **belum ditanya ulang
   eksplisit** untuk pasangan versi ini (silence dari scan kosong ≠ jawaban).
4. **[GAP]** `FINDINGS.md` project 18.0→19.0 mencatat `MF-04`/`BSL-018` (lama): file
   `views/product_template_views.xml` dead (tidak di manifest `data:`), dan `MF-24`/`BSL-017` (baru,
   ditemukan sesi ini): pola `position="replace"` yang menghapus atribut core field
   `list_price`/`lst_price` **muncul DUA KALI** di `views/products.xml` (baris ~62 untuk `list_price`
   di view Product Template, DAN baris ~95 untuk `lst_price` di `product_variant_easy_edit_view` —
   `FINDINGS.md` `MF-24` cuma menyebut lokasi pertama). Detail lengkap: `01b_BASELINE_SPEC.md`
   `BSL-017`.
5. **[NO-SPEC, baru]** Field `margin_sale` di `product.product` didekorasi **dua mekanisme sekaligus**:
   `inverse="_set_product_margin_sale"` (dipanggil saat `write()`/save) DAN `@api.onchange('margin_sale')`
   pada method yang sama (dipanggil interaktif di form, sebelum save). Tidak pernah didokumentasikan
   granular di baseline manapun sebelumnya (18.0→19.0 maupun 17.0→18.0) — cuma perincian mekanisme
   baru dari baca kode langsung, bukan kontradiksi terhadap klaim lama (efek akhirnya tetap sama:
   menulis balik ke template). Detail: `01b_BASELINE_SPEC.md` `BSL-012`.
6. **Gap test yang masih terbuka (carry-forward dari DUA project migrasi sebelumnya, masih belum
   ditutup):** AC-02-03 (tidak ada popup sama sekali kalau semua line di atas minimum — belum ada
   Tour test yang mengasersi ini) dan AC-02-04 (assert teks/warna warning di orderline secara
   terpisah). Dua Tour test yang ADA (`..._confirm_tour`, `..._blocked_tour`) menutup AC-02-02 dan
   jalur blocking, tapi bukan dua gap ini. **Keputusan user diperlukan:** ditutup di project 19.0→20.0
   ini, atau tetap dilewati (sudah dilewati dua kali)?
7. Quirk warisan yang harus tetap identik (bukan bug untuk diperbaiki, sudah dikonfirmasi ulang cocok
   dengan kode 19.0 aktual sesi ini) — lihat `01b_BASELINE_SPEC.md` §8 untuk detail lengkap:
   `MF-01`/`BSL-010` (margin per-variant selalu tersinkron ke template), `MF-02`/`BSL-021`
   (`blocking_transaction_order` dideklarasikan tapi tidak dibaca modul ini), `MF-03`/`BSL-020`
   (kolisi `wizard.margin.product` dengan `sale_margin_threshold`), `MF-04`/`BSL-022` (dead file view),
   `MF-23`/`BSL-019` (compute `is_less_minimum_sale` tanpa `@api.depends`), typo
   `action_assing_margin`.

---

## 1. Modul & Scope

- **Modul yang dimigrasi:** `pos_margin_threshold` (satu dari tiga addon independen dalam project ini
  — lihat `CLAUDE.md` §"Adaptasi multi-modul").
- **Deskripsi singkat:** menambahkan margin minimum penjualan (`margin_sale`) per kategori/produk,
  menghitung `minimum_sale_price`/`minimum_sale_price_with_tax`, dan mem-block/mengonfirmasi
  pembayaran di Point of Sale kalau harga jual di bawah minimum (blocking atau confirm, tergantung
  setting `blocking_transaction_pos`). Menyediakan wizard bulk-assign margin dari list view Product
  Template/Product Variant.
- **Saling depend dengan modul lain?** Tidak ada dependency Python/manifest formal ke
  `sale_margin_threshold`/`pin_message`. Interaksi RUNTIME dengan `sale_margin_threshold`: kolisi
  model `wizard.margin.product` (`_name` sama, lihat `MF-03`/`BSL-020`). Tidak ada interaksi dengan
  `pin_message` sama sekali.

## 2. Dependency Map (auto-scan, diverifikasi ulang ke `native-target`/`native-target-enterprise` 20.0)

| Dependency | Tipe | Versi tersedia di target 20.0? | Catatan |
|---|---|---|---|
| `base` | Native Community | **Ya** — `odoo20/odoo/addons/base/__manifest__.py` | Inti framework, tidak pernah dihapus. |
| `point_of_sale` | Native Community | **Ya** — `odoo20/addons/point_of_sale/__manifest__.py` | Integrasi terberat modul ini — patch JS/Owl (`ProductProduct`, `PosOrderline`, `PosStore`), `_load_pos_data_fields`. Prioritas riset Step 2 — area ini SUDAH terbukti berubah total sekali (17→18) dan sekali lagi mekanismenya (18→19, lihat §8). |
| `product` | Native Community | **Ya** — `odoo20/addons/product/__manifest__.py` | `product.category`/`product.template`/`product.product` inherit + XML inherit ke `product.product_template_form_view`/`product.product_template_only_form_view`/`product.product_variant_easy_edit_view`. |
| `stock_account` | Native Community | **Ya** — `odoo20/addons/stock_account/__manifest__.py` | Hanya lewat XML `inherit_id="stock_account.view_category_property_form_stock"`, tidak ada `_inherit` Python. |

**Dicek juga di `native-target-enterprise` (`enterprise20`):** TIDAK ada satupun dari keempat modul di
atas di sana (struktur addons-only Enterprise dikonfirmasi via `ls` — `point_of_sale`/`product`/
`stock_account` tidak ada) — konsisten, keempat dependency modul ini murni Native Community, tidak ada
baris Enterprise di dependency map modul ini sendiri. Project ini (3 modul) tetap wajib
`native-target-enterprise` karena `sale_margin_threshold` (sibling, lihat `CLAUDE.md` §Folder), bukan
karena modul ini.

Dependency opsional yang dicek runtime (tidak di manifest):
- **`sale_margin_threshold`** (modul custom sibling, bukan Odoo native) — kolisi `_name` model
  `wizard.margin.product` (`MF-03`/`BSL-020`). Tidak dideklarasikan di `depends` manapun, merge model
  terjadi murni dari kesamaan `_name` Python saat registry dibangun.

## 2b. Struktur & Fitur Modul (auto-scan)

| Fitur | Ada di modul? | Lokasi/bukti | Fase step 6 relevan |
|---|---|---|---|
| Controllers (route custom) | ☐ Tidak (scaffold mati) | `controllers/controllers.py` — seluruh body di-comment; `controllers/__init__.py` tetap `from . import controllers` (no-op, tidak error) | D1 — kandidat N/A |
| Assets/CSS/JS custom | ☑ Ya | `assets['point_of_sale._assets_pos']` → `static/src/**/*`; `assets['web.assets_tests']` → `static/tests/tours/**/*` (`__manifest__.py`) | D2, E, F — WAJIB full treatment |
| Komponen Owl/JavaScript custom | ☑ Ya (patch, bukan komponen baru) | `patch(ProductProduct.prototype)`/`patch(PosOrderline.prototype)` (`static/src/store/models/models.js`), `patch(PosStore.prototype)` (`static/src/store/pos_store.js`), template inherit `orderline.xml` (`t-inherit point_of_sale.Orderline`) | E — prioritas tertinggi, area paling sering breaking antar versi POS (terbukti 2x: 17→18 rename kelas total, 18→19 hapus `Orderline.props.line.shape` + rename massal method) |
| Field JSON / relasi berantai >2 level / dynamic model creation | ☐ Tidak | Semua field Float/Boolean langsung (`margin_sale`, `minimum_sale_price`, `minimum_sale_price_with_tax`, `is_less_minimum_sale`, `is_blocked_warning`, `blocking_transaction_pos/order`), tidak ada `self.env[var]` di manapun (grep bersih) | B2 — N/A |
| View pakai `attrs=`/`states=`/domain/context dinamis | ☐ Tidak (pakai syntax modern `invisible=`/`decoration-*=`, bukan `attrs=` legacy) | `views/products.xml`, `views/product_template_views.xml` (dead file), `wizard/wizard_margin_product.xml` — semua pakai `invisible="<expr>"`/`decoration-danger="<expr>"` modern | C2 — kemungkinan N/A, tapi WAJIB verifikasi ulang syntax `invisible=`/`decoration-*=` masih valid identik di 20.0 (Step 2), termasuk ekspresi majemuk `product_variant_count > 1 and not is_product_variant` |

## 3. Sifat Migrasi

- [x] Port kode saja (tidak ada data produksi — instalasi baru di 20.0) — **[CARRIED-FORWARD]**
  diwarisi dari keputusan dev di project 17.0→18.0 dan 18.0→19.0 untuk modul yang sama, **belum
  dikonfirmasi ulang eksplisit untuk project ini**. Lihat "Ringkasan untuk Review" poin 1.
- [ ] Upgrade instance

## 4. Baseline Spec / Characterization Test (gate)

- [x] Tidak ada `FUNCTIONAL_SPEC.md` lama TERPISAH di `pos_margin_threshold` sendiri untuk siklus ini
  (pola sama dua project sebelumnya) — sumber baseline untuk project 19.0→20.0 ini adalah
  `doc-dev/migration_18.0_19.0/doc/01_intake/pos_margin_threshold/01b_BASELINE_SPEC.md` (baseline 19.0
  hasil project migrasi SEBELUMNYA, sudah lulus 10 dari 11 step, UAT sign-off menunggu eksekusi
  manusia) — diperlakukan persis seperti "spec lama": dibaca, di-cross-check ke kode 19.0 aktual
  (branch `migration/19.0`, identik dengan working tree `migration/20.0` saat ini sebelum ada
  perubahan kode apapun), digabung dengan `FINDINGS.md` (baik versi project 18.0→19.0 maupun versi
  yang sudah dibawa ke project ini) untuk menangkap perubahan/temuan yang terjadi SELAMA migrasi
  18→19 tapi belum tercermin di teks BSL lama itu sendiri. Hasil: `01b_BASELINE_SPEC.md` (dokumen ini,
  versi 19.0→20.0) — lihat dokumen terpisah.
- [x] **Test/characterization test LAMA — ADA, di lokasi YANG SAMA dengan `source-codebase`** (bukan
  di luar repo): `tests/test_margin_sale.py`, `tests/test_cross_module.py`,
  `tests/test_margin_threshold_tour.py` + `static/tests/tours/margin_threshold_tour.js` — hasil proses
  `doc-dev-backfill` yang dijalankan di iterasi migrasi sebelumnya (komentar header file merujuk
  `doc-dev/backfill/spec/pos_margin_threshold/01B_ACCEPTANCE_CRITERIA.md`). Test-test ini
  mengeksekusi terhadap kode 19.0 yang berjalan SEKARANG (branch `migration/19.0`), bukan cuma
  pembacaan statis — jadi baseline di `01b_BASELINE_SPEC.md` yang berkaitan dengan
  klaim-klaim ini punya bukti eksekusi (lebih kuat dari baca kode langsung).
- [x] `01b_BASELINE_SPEC.md` sudah diisi, termasuk "Ringkasan untuk Review" dan ID `BSL-NNN` per klaim.

### 4a. Dokumen Pelengkap Lain

- [x] **[CARRIED-FORWARD]** Tidak ada dokumen pelengkap lain di luar kode + dokumentasi
  `doc-dev/migration_17.0_18.0/` dan `doc-dev/migration_18.0_19.0/` — pola konsisten dari dua project
  sebelumnya (yang juga tidak menemukan dokumen eksternal). **Belum dikonfirmasi ulang eksplisit ke
  dev** untuk siklus 19.0→20.0 ini. Lihat "Ringkasan untuk Review" poin 2.

## 4b. Source Masih Aktif Dikembangkan?

- [x] **[CARRIED-FORWARD]** Tidak — asumsi bahwa `migration/19.0` dibekukan selama migrasi 20.0
  berjalan, konsisten keputusan dua project sebelumnya. **Belum dikonfirmasi ulang eksplisit oleh dev
  untuk project ini** — lihat `[PERLU-KEPUTUSAN]` di `CLAUDE.md` dan "Ringkasan untuk Review" poin 2.

## 5. Scope Boundary

- **Harus tetap identik pasca migrasi:** semua business rule di §4 `01b_BASELINE_SPEC.md`
  (`BSL-001`..dst), termasuk SEMUA quirk warisan (`MF-01`/`BSL-010`, `MF-02`/`BSL-021`,
  `MF-03`/`BSL-020`, `MF-04`/`BSL-022`, `MF-23`/`BSL-019`, typo `action_assing_margin`) — tidak
  satupun diperbaiki tanpa persetujuan eksplisit user. `MF-24` (view `list_price`/`lst_price`
  `position="replace"`) sudah ada keputusan dev sebelumnya ("dibiarkan dulu") — dipertahankan identik,
  termasuk instance KEDUA yang baru ditemukan sesi ini (`BSL-017`). Mekanisme JS POS (getter
  `get_minimum_sale_price()`/`get_minimum_sale_price_with_tax()`, `displayPriceUnit`,
  `getOrderlines()`, `getProduct()`) yang sudah terbukti stabil sejak migrasi 18→19 TIDAK boleh
  diasumsikan otomatis stabil lagi 19→20 — wajib diverifikasi ulang ke `native-target` 20.0 nyata di
  Step 2, konsisten pola dua project sebelumnya (area ini sudah dua kali breaking change).
- **Yang sengaja diubah/di-drop:** tidak ada usulan perubahan disengaja untuk migrasi ini. Kalau Step
  2/6 menemukan API 20.0 yang memang mengharuskan perubahan (bukan pilihan), itu dicatat sebagai
  `MF-NNN` baru (mulai `MF-25`, lihat `FINDINGS.md`) — bukan dianggap "scope boundary" awal.

## 6. Constraint

- Deadline: belum disebutkan dev.
- Owner tiap step: belum disebutkan dev (asumsi: dev yang sama seperti dua project sebelumnya, belum
  dikonfirmasi ulang).
