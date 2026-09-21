# Migration Intake — sale_margin_threshold

**Step:** 1 — Intake & Scope
**Versi:** 19.0 → 20.0
**Tanggal:** 2026-09-21
**Status:** ✔️ Gate LULUS (2026-09-21) — semua §0/§0a/§0b sudah terjawab lewat bootstrap `CLAUDE.md`
project ini; lihat catatan koreksi di "Ringkasan untuk Review" untuk dua temuan baru yang perlu
dikonfirmasi ke dev walau gate ini sendiri tidak diblokir olehnya.

---

## 0. Folder Referensi — WAJIB Ditanyakan ke Dev SEKARANG

**Checklist (sudah terjawab lewat bootstrap project ini — lihat `CLAUDE.md` §"Folder yang perlu
di-connect" dan §"Status saat ini", dikonfirmasi 2026-09-21):**

- [x] `native-target` (Odoo 20.0 Community) — **`D:\Kuncoro\doodex\repo\odoo20`** (clone git resmi
  `odoo/odoo`, branch `20.0`). Dikonfirmasi ada: `base` di `odoo20/odoo/addons/base`, `product`/
  `sale`/`stock_account` di `odoo20/addons/`.
- [x] `native-source` (Odoo 19.0, opsional) — **tidak ada folder terpisah**, dibaca lewat
  `git show migration/19.0:<path>` di repo yang sama (lihat §"Adaptasi dual-branch" `CLAUDE.md`).
  Peninggalan `D:\Kuncoro\doodex\repo\enterprise19.0` (Community+Enterprise 19.0 gabungan, BUKAN
  git repo) tetap dipertahankan sebagai referensi cross-check langsung ke versi asal.
- [x] **`native-target-enterprise` — RESOLVED, dua clone TERPISAH kali ini (bukan gabungan seperti
  project 18.0→19.0 sebelumnya).** `D:\Kuncoro\doodex\repo\enterprise20` (clone git resmi
  Enterprise, branch `20.0`). **Sanity check awal sesi ini (bukan Step 2 penuh):** `sale_renting`
  ADA di `enterprise20/sale_renting/`, dan `is_rental_order` dikonfirmasi masih ada persis nama itu
  di `sale_renting/models/sale_order.py:95` (Odoo 20.0) — field yang dicek `hasattr()` oleh modul
  ini (`models/sale_order.py:14`) MASIH ADA di 20.0. Ini bukan verifikasi lengkap (belum cek
  signature/behavior detail perubahan `_compute_is_rental_order`), detail lengkap tetap domain
  Step 2.
- [x] `third-party-source`/`third-party-target` — **belum dikonfirmasi ULANG secara eksplisit oleh
  dev untuk pasangan 19.0→20.0 ini** (lihat `CLAUDE.md` §"Folder yang perlu di-connect": "Belum
  dicek ulang untuk pasangan 19.0→20.0 — project 18.0→19.0 tidak menemukan indikasi OCA... tapi
  harus dikonfirmasi ulang di intake, bukan diasumsikan permanen"). Grep langsung `depends`/import
  di `__manifest__.py` dan seluruh kode modul ini sesi ini: **tidak ada indikasi OCA/third-party
  apapun** (cuma `base`/`product`/`sale`/`stock_account`, semua native Odoo). Ini konsisten dengan
  asumsi carried-forward, TAPI tetap flagged di "Ringkasan untuk Review" sebagai belum dikonfirmasi
  dev secara eksplisit-baru (bukan cuma diwarisi).

**Status:** ✔️ **Gate Step 1 LULUS (2026-09-21)** — semua path terisi nyata, tidak ada placeholder
`{{...}}` tersisa.

### 0a. Konfirmasi Branch/Versi (WAJIB)

- [x] **Model dual-branch (BUKAN dual-clone) — deviasi eksplisit dari default template**, dilanjutkan
  identik dari dua project sebelumnya (17.0→18.0, 18.0→19.0) di repo yang sama:
  - **Source (19.0):** branch `migration/19.0` — read-only referensi. AI TIDAK PERNAH `git
    checkout` ke branch ini; baca isi file versi 19.0 lewat `git show migration/19.0:<path>` atau
    `git diff migration/20.0 migration/19.0 -- <path>`. Branch ini sudah lulus 10 dari 11 step
    migrasi 18.0→19.0 (UAT sign-off menunggu eksekusi manual manusia).
  - **Target (20.0):** branch `migration/20.0` — working branch aktif project ini, dibuat
    2026-09-21 via `git checkout -b migration/20.0` dari tip `migration/19.0` (commit `5876d01`).
    Working tree saat dokumen ini ditulis IDENTIK dengan `migration/19.0` (belum ada edit migrasi).
- [x] Versi Odoo semantik: **19.0 → 20.0**, dikonfirmasi eksplisit lewat `CLAUDE.md` §Identitas
  (diinstansiasi dari template project 18.0→19.0, path/versi diisi ulang 2026-09-21).

### 0b. Gate: Path Absolut `.claude/settings.json`

- [x] **Sudah dipenuhi saat bootstrap 2026-09-21** (lihat `CLAUDE.md` §"Adaptasi dual-branch" ¶
  "Konfig yang diwarisi saat bootstrap"): `ABS_PATH_NATIVE_TARGET` = `odoo20`,
  `ABS_PATH_NATIVE_TARGET_ENTERPRISE` = `enterprise20` (dua entry deny TERPISAH, bukan satu path
  gabungan seperti project 18.0→19.0), `ABS_PATH_SOURCE_CODEBASE`/`ABS_PATH_MIGRATION_TOOL` terisi
  path nyata. Entry deny milik folder referensi project sebelumnya (`odoo18`, `enterprise19.0`
  sebagai native-target lama) sudah dibuang saat bootstrap — `enterprise19.0` DIPERTAHANKAN hanya
  sebagai `native-source` (bukan native-target lagi). Tidak ada placeholder `{{ABS_PATH_...}}`
  literal tersisa di `.claude/settings.json`.

---

## Ringkasan untuk Review — Perlu Konfirmasi User

1. **Empat asumsi carried-forward dari project 18.0→19.0 (dan 17.0→18.0 sebelumnya), BELUM
   dikonfirmasi ulang eksplisit oleh dev untuk project 19.0→20.0 ini** (lihat `CLAUDE.md` §Identitas
   — semua ditandai `[PERLU-KEPUTUSAN]`/"belum dikonfirmasi ulang" di sana):
   - Sifat migrasi = "Port kode saja" (§3 di bawah).
   - Source (`migration/19.0`) tidak aktif dikembangkan selama migrasi ini berjalan (§4b).
   - Tidak ada dokumen pelengkap lain SELAIN baseline spec lama (§4a) — **lihat poin 2 di bawah,
     asumsi ini ternyata TIDAK sepenuhnya akurat, ada satu yang terlewat 2 siklus.**
   - Tidak ada dependency third-party/OCA (§0 di atas — grep sesi ini konsisten dengan asumsi ini,
     tapi belum ada konfirmasi eksplisit dev yang BARU untuk pasangan versi ini).
2. **KOREKSI atas asumsi §4a "tidak ada dokumen pelengkap lain":** ditemukan `doc-dev/backfill/`
   (folder ada di ROOT repo ini, sejajar `doc-dev/migration_17.0_18.0/` dkk) — berisi
   `spec/sale_margin_threshold/01A_FUNCTIONAL_SPEC.md`+`01B_ACCEPTANCE_CRITERIA.md`,
   `test/sale_margin_threshold/03B_TEST_PLAN.md`+`04A_DEV_TESTING.md`+`07_QA_TESTING.md`, dan
   `FINDINGS.md` konsolidasi (finding `F-01`..`F-07` lintas 3 modul, termasuk `F-05` untuk modul
   ini). Dokumen ini dihasilkan proses `doc-dev-backfill` DENGAN EKSEKUSI NYATA (Docker Odoo 17.0,
   2026-07-31 — 17 test case, `0 failed, 0 error(s)`), bukan cuma baca kode. **Dokumen ini TIDAK
   PERNAH direferensikan oleh `01a`/`01b` project 17.0→18.0 maupun 18.0→19.0 sebelumnya** — kedua
   project itu menulis §4a sebagai "belum dikonfirmasi eksplisit... asumsi sementara tidak ada"
   dan tidak pernah menemukan folder ini walau berada tepat di repo yang sama. Sudah dipakai
   sebagai sumber tambahan di `01b_BASELINE_SPEC.md` (`BSL-009`) sesi ini. **Perlu dikonfirmasi ke
   dev:** apakah dev sudah tahu folder ini, dan apakah isinya harus diperlakukan resmi sebagai
   "dokumen pelengkap" untuk seluruh sisa step project ini (bukan cuma ditemukan sekali lalu
   dilupakan lagi).
3. **`[BSL-009]` di `01b_BASELINE_SPEC.md` — koreksi deskripsi mekanisme bug `MF-08`, BUKAN
   keputusan baru.** Baseline lama (17-18/18-19) mendeskripsikan bug singleton-assumption
   `action_confirm()` sebagai "validasi margin SENYAP untuk order ke-2 dst saat batch confirm".
   Bukti eksekusi nyata (`doc-dev/backfill/FINDINGS.md` F-05) menunjukkan ini sebenarnya
   `ValueError: Expected singleton` — CRASH TOTAL, bukan senyap, termasuk memecahkan demo data
   `sale_stock` bawaan Odoo core sendiri. **Keputusan dev 2026-08-27 (dipertahankan, tidak
   diperbaiki) TIDAK berubah** oleh koreksi ini — cuma presisi mekanismenya, tidak perlu keputusan
   baru dari user.
4. **Dua temuan BARU yang belum pernah dicatat di `FINDINGS.md`/baseline spec manapun sebelumnya**
   (detail lengkap di `01b_BASELINE_SPEC.md` `BSL-011`/`BSL-019`):
   - Bug singleton-assumption KEDUA (instance terpisah dari `MF-08`) di compute
     `_compute_is_rental_order_installed` — membaca `self.is_rental_order` padahal sudah ada
     `for record in self:`.
   - `list_price`/`lst_price` di-`position="replace"` (menghapus atribut core `options`) — pola
     identik `MF-24` (sudah tercatat untuk sibling `pos_margin_threshold`) tapi belum pernah dicatat
     untuk modul INI.
   - **Tidak saya tambahkan ke `FINDINGS.md`** karena task ini dibatasi hanya menulis dua dokumen
     `01a`/`01b` — direkomendasikan ke dev untuk ditambahkan sebagai `MF-28`/`MF-29` kalau setuju.
5. **`MF-20`/`MF-21` masih terbuka**, dikonfirmasi ulang identik di kode 19.0/20.0 saat ini, belum
   ada keputusan dev sejak ditemukan Step 8 project 18.0→19.0.
6. **`MF-08` (lihat poin 3) sudah punya keputusan eksplisit** — dipertahankan, bukan pertanyaan
   terbuka baru.
7. **Kolisi `wizard.margin.product` dengan `pos_margin_threshold` (`MF-03`)** — modul INI yang
   selalu menang MRO, dikonfirmasi konsisten sepanjang 3 siklus migrasi, tidak berubah.

---

## 1. Modul & Scope

- **Modul:** `sale_margin_threshold`.
- **Deskripsi:** menegakkan margin minimum di alur konfirmasi Sale Order (`action_confirm`) — kalau
  ada baris order dengan harga di bawah `minimum_sale_price`, sistem memblok konfirmasi
  (`ValidationError`) atau meminta konfirmasi via wizard, tergantung setting
  `blocking_transaction_order`. Rental order (Enterprise) sepenuhnya dikecualikan. Modul juga
  menyediakan wizard bulk-assign margin yang identik strukturnya dengan `pos_margin_threshold`.
- **Saling depend dengan modul lain?** Tidak ada dependency Python/manifest formal ke
  `pos_margin_threshold`/`pin_message`. Interaksi RUNTIME: kolisi `_name` `wizard.margin.product`
  dengan `pos_margin_threshold` (`MF-03`, `sale_margin_threshold` menang), `_register_hook()` dan
  `_compute_module_pos_margin_threshold` keduanya mengecek `ir.module.module` untuk tahu apakah
  `pos_margin_threshold` terinstall (murni introspeksi, bukan dependency formal).

## 2. Dependency Map (auto-scan)

| Dependency | Tipe (Native Community / Native Enterprise / OCA / Custom) | Versi tersedia di target (20.0)? | Catatan |
|---|---|---|---|
| `base` | Native Community | **Ya** — `odoo20/odoo/addons/base` | Inti Odoo, praktis tidak mungkin hilang. Catatan knowledge base 19→20: `ir.model.access.csv`→`ir.access.csv` rename (`migration-tool/knowledge/version-diffs/19-to-20.md`) — modul ini punya `security/ir.model.access.csv`, **wajib dicek ulang Step 2** apakah nama file lama masih diterima atau harus dimigrasi ke skema baru. |
| `product` | Native Community | **Ya** — `odoo20/addons/product` | Model utama yang di-extend (`product.category`/`product.template`/`product.product`). Cek ulang Step 2: atribut core `list_price`/`lst_price` di form view (relevan ke `BSL-019`/quirk `position="replace"`). |
| `sale` | Native Community | **Ya** — `odoo20/addons/sale` | **Prioritas riset Step 2** — `action_confirm()` override, model paling mungkin berubah struktural antar versi. |
| `stock_account` | Native Community | **Ya** — `odoo20/addons/stock_account` | Sama seperti modul sibling — cuma lewat XML inherit (`view_category_property_form_stock` untuk `margin_sale` di kategori). |

**Dependency Enterprise (implisit, runtime, bukan `depends` formal):** Modul Rental
(`is_rental_order`, family `sale_renting`) — dicek via `hasattr()`, TIDAK mewajibkan instalasi,
tapi behavior beda tergantung ada/tidaknya. **Dikonfirmasi masih ada di `enterprise20`** (lihat §0
di atas) — `native-target-enterprise` wajib untuk modul ini, sudah di-connect terpisah dari
`native-target` (dua clone berbeda kali ini, lihat §0).

Dependency opsional yang dicek runtime (tidak di manifest):
- **`pos_margin_threshold`** (custom sibling) — dicek via `ir.module.module` di dua tempat
  (`_register_hook()`, `_compute_module_pos_margin_threshold`), plus kolisi `_name`
  `wizard.margin.product` (lihat `01b_BASELINE_SPEC.md` §8).

## 2b. Struktur & Fitur Modul (auto-scan)

| Fitur | Ada di modul? | Lokasi/bukti (dicek langsung sesi ini) | Fase step 6 yang jadi relevan |
|---|---|---|---|
| Controllers (route custom) | ☐ Tidak (scaffold mati) | `controllers/controllers.py` — semua di-comment | D1 — kandidat N/A |
| Assets/CSS/JS custom | ☐ Tidak (secara FUNGSIONAL) | Manifest deklarasikan `assets.sale_margin_threshold._assets_sale` → `static/src/**/*`, tapi `ls static/` sesi ini konfirmasi folder itu **tidak ada** — hanya `static/description/*` (listing app) | D2, E, F — N/A murni |
| Komponen Owl/JavaScript custom | ☐ Tidak | Grep `.js` di seluruh modul sesi ini: 0 file | E, F — N/A |
| Field JSON / relasi berantai >2 level / dynamic model creation | ☑ Ya (dynamic model access, bukan JSON/deep-chain) | `wizard/sale_confirmation.py`: `self.env[active_model].browse(active_id)` — `active_model` dari context, resolusi dinamis saat runtime (nilai aktual selalu `'sale.order'` tapi ditulis generik) | B2 — perlu dicek `self.env[var]` masih valid identik di 20.0 (API dasar stabil lintas versi, tapi verifikasi tetap wajib) |
| View pakai `attrs=`/`states=`/domain/context dinamis | ☐ Tidak (syntax modern `invisible=`/`decoration-*=`) | `views/sale_order.xml`, `views/products.xml`, `views/product_template_views.xml` — semua expression modern (`invisible="module_pos_margin_threshold == True or ..."`, `decoration-danger="..."`) | C2 — kemungkinan N/A, verifikasi syntax masih valid 20.0 |

Modul ini murni backend (model + wizard + view XML), tidak ada folder `static/src/` — footprint JS
nol, konsisten dengan dugaan awal task.

## 3. Sifat Migrasi

- [x] Port kode saja — **asumsi carried-forward dari project 17.0→18.0/18.0→19.0, BELUM
  dikonfirmasi ulang eksplisit oleh dev untuk project 19.0→20.0 ini** (lihat "Ringkasan untuk
  Review" poin 1). Diasumsikan konsisten kecuali dev menyatakan sebaliknya.
- [ ] Upgrade instance

## 4. Baseline Spec / Characterization Test (gate)

- [x] Tidak ada `FUNCTIONAL_SPEC.md` lama di dalam `sale_margin_threshold/` itu sendiri (dikonfirmasi
  konsisten dengan pola dua project sebelumnya) — **TAPI** ada `doc-dev/backfill/spec/sale_margin_threshold/01A_FUNCTIONAL_SPEC.md`
  di lokasi TERPISAH di repo yang sama (lihat "Ringkasan untuk Review" poin 2). Proses pengisian
  `01b_BASELINE_SPEC.md` sesi ini: (1) baca `doc-dev/migration_18.0_19.0/doc/01_intake/sale_margin_threshold/01b_BASELINE_SPEC.md`
  (baseline 18.0→19.0 project sebelumnya) sebagai draft awal — dokumen itu sendiri sudah
  memainkan peran "baseline spec dari project migrasi sebelumnya" (bukan `FUNCTIONAL_SPEC.md`
  generik); (2) cross-check tiap klaim ke kode 19.0/20.0 aktual satu per satu; (3) yang cocok
  disalin/dirangkum dengan tag `[MATCH]` + `(ref: 18-19/BSL-NNN)`; (4) satu klaim (`BSL-009`)
  TIDAK cocok persis (deskripsi mekanisme, bukan keputusan) — kode + bukti eksekusi `doc-dev/backfill`
  yang menang, dicatat eksplisit sebagai `[GAP]` di `01b` §5, bukan diam-diam "dikoreksi" tanpa
  jejak.
- [x] **Test/characterization test LAMA (WAJIB ditanyakan eksplisit, terpisah dari pertanyaan
  `FUNCTIONAL_SPEC.md` di atas):** **ADA, dan lokasinya BERBEDA dari path modul itu sendiri** —
  `doc-dev/backfill/test/sale_margin_threshold/` (`03B_TEST_PLAN.md`, `04A_DEV_TESTING.md`,
  `07_QA_TESTING.md`) + `doc-dev/backfill/FINDINGS.md` (`F-01`..`F-07`, `F-05` relevan langsung ke
  modul ini). **Dieksekusi NYATA** (Docker Odoo 17.0, 2026-07-31, `TransactionCase` via
  `odoo-bin --test-enable`, 17 test case lintas 3 modul, hasil `0 failed, 0 error(s)`) — bukan
  cuma baca kode statis. Test file hasilnya (`tests/test_action_confirm.py`,
  `tests/test_cross_module.py`) MASIH ADA di modul `sale_margin_threshold/tests/` saat ini (kode
  19.0/20.0), berisi komentar `# BACKFILL` yang mereferensikan
  `doc-dev/backfill/spec/sale_margin_threshold/01B_ACCEPTANCE_CRITERIA.md`. **Path lengkap ini
  WAJIB diteruskan ke Step 9** (`09_DEV_TESTING.md` §Baseline) — Step 9 TIDAK BOLEH menyimpulkan
  "tidak ada test dari proses sebelumnya" hanya dari struktur folder modul semata.
- [x] `01b_BASELINE_SPEC.md` sudah diisi dengan ID `BSL-001`..`BSL-019` + provenance (`[MATCH]`
  ×16, `[GAP]` ×1, `[NO-SPEC]` ×2) + "Ringkasan untuk Review".

### 4a. Dokumen Pelengkap Lain

- [x] **Belum dikonfirmasi eksplisit ke dev untuk project 19.0→20.0 ini** — asumsi carried-forward
  dari dua project sebelumnya adalah "tidak ada". **Asumsi ini TERNYATA TIDAK SEPENUHNYA AKURAT**
  (lihat "Ringkasan untuk Review" poin 2 dan §4 di atas): ditemukan `doc-dev/backfill/` yang belum
  pernah dicatat sebagai "dokumen pelengkap" oleh proses Step 1 manapun sebelumnya, walau sudah ada
  di repo sejak sebelum project 17.0→18.0. **Perlu konfirmasi eksplisit ke dev**: apakah dev sudah
  tahu soal folder ini, dan supaya tidak terlewat siklus keempat, apakah perlu direferensikan
  permanen (mis. ditambahkan ke `CLAUDE.md`/`FINDINGS.md`) — di luar scope dua dokumen yang ditulis
  sesi ini, hanya direkomendasikan.

## 4b. Source Masih Aktif Dikembangkan?

- [x] Tidak — **asumsi carried-forward dari dua project sebelumnya, BELUM dikonfirmasi ulang
  eksplisit untuk project ini** (lihat `CLAUDE.md` §Identitas: `[PERLU-KEPUTUSAN]`). Tidak ada
  `SYNC_POLICY.md` dibuat, konsisten dengan asumsi ini. Kalau dev menyatakan source aktif
  dikembangkan, `SYNC_POLICY.md` wajib dibuat sebelum kerja lanjut.

## 5. Scope Boundary

- **Harus tetap identik:** semua `BSL-NNN` di `01b_BASELINE_SPEC.md`, termasuk seluruh quirk
  warisan (`MF-03`, `MF-05`(=BSL-013)/`MF-06`(=BSL-014)/`MF-08`(=BSL-009)/`MF-20`(=BSL-017)/
  `MF-21`(=BSL-018)) DAN dua quirk baru yang ditemukan sesi ini (`BSL-011`, `BSL-019`) — belum ada
  yang diusulkan diperbaiki di titik ini, semua menunggu keputusan eksplisit user kalau ingin
  diperbaiki (bukan bagian scope "port kode saja").
- **Yang sengaja diubah:** tidak ada yang diusulkan di titik ini. `MF-08` (koreksi deskripsi
  mekanisme, bukan perilaku) BUKAN perubahan kode — murni koreksi dokumentasi. Fix-fix mekanis
  warisan migrasi 18.0→19.0 (`MF-16`/`MF-17`/`MF-18`/`MF-22`, rename field API core) sudah
  dipertahankan apa adanya di kode saat ini — bukan perubahan baru untuk project ini.

## 6. Constraint

- Deadline: belum disebutkan.
- Owner: belum disebutkan.
