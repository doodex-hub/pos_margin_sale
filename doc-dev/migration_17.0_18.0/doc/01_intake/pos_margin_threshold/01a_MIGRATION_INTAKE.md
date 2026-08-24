# Migration Intake — pos_margin_threshold

**Step:** 1 — Intake & Scope
**Versi:** 17.0 → 18.0
**Tanggal:** 2026-08-24
**Status:** ✔️ Gate lulus (2026-08-24) — semua checklist §0/§0a/§4a/§4b dikonfirmasi dev

---

## 0. Folder Referensi — WAJIB Ditanyakan ke Dev SEKARANG

- [x] `native-target` (Community, clone `odoo/odoo` checkout 18.0) — **dikonfirmasi dev: belum ada di disk.** Step 2 (diff analysis) akan dikerjakan tanpa akses langsung ke source Odoo 18.0 core — mengandalkan pengetahuan umum + `migration-tool/knowledge/version-diffs/17-to-18.md`. Kurang presisi, dicatat sebagai keterbatasan Step 2, bukan blocker Step 1.
- [x] `native-source` (Community, checkout 17.0) — sama, tidak ada, tidak diminta (opsional).
- [x] `native-target-enterprise` — **dikonfirmasi dev: tidak ada dependency Enterprise** (konsisten dengan auto-scan manifest, semuanya Community).
- [x] `third-party-source`/`third-party-target` — **dikonfirmasi dev: tidak ada dependency OCA/vendor.**

### 0a. Konfirmasi Branch/Versi `source-codebase` & `target-codebase`

- [x] **Source:** branch `backfill/17.0`, repo yang sama (`target-codebase`) — dikonfirmasi dev di sesi bootstrap 2026-08-24 (bukan clone terpisah, lihat `CLAUDE.md` §Adaptasi dual-branch).
- [x] **Target:** branch `migration/18.0`, repo yang sama — dikonfirmasi dev, dibuat dari `backfill/17.0` (commit `9fb8905`).
- [x] Kedua branch BUKAN clone fisik terpisah (dual-branch, bukan dual-clone) — deviasi disengaja dari model standar, dikonfirmasi eksplisit.
- [x] Versi semantik: **17.0 → 18.0** — dikonfirmasi dev di sesi bootstrap (nama folder repo `pos-margin-sale-migration-18` awalnya cuma dugaan, sudah dikonfirmasi eksplisit lewat AskUserQuestion, bukan diasumsikan dari nama folder semata).

### 0b. Gate: Path Absolut di `.claude/settings.json`

`Environment eksekusi = Claude Code CLI` dan `.claude/settings.json` sudah ada (dibuat sebelum sesi ini, dibawa ke branch `migration/18.0` saat bootstrap). Isi saat ini:

```
"Bash(git rev-parse:*)", "Bash(git status:*)", "Bash(git fetch:*)", "Bash(git ls-remote:*)",
"Bash(git checkout:*)", "Bash(git clone:*)", "Bash(git pull:*)", "Bash(git commit:*)",
"Bash(git diff:*)", "Bash(git log:*)", "Bash(git branch:*)", "Edit(**)"
deny: "Bash(git push:*)", "Bash(git push --force:*)", "Bash(git rebase:*)", "Bash(git merge:*)",
"Bash(git reset --hard:*)", "Bash(git branch -D:*)", "Bash(gh pr create:*)"
```

**Tidak ada placeholder `{{ABS_PATH_...}}`** di file ini — varian yang ter-install adalah `settings.json.mode-git.template` versi sederhana (tanpa proteksi path Edit ke folder referensi eksternal), bukan varian yang membawa deny-list `native-*`/`third-party-*`/`migration-tool` per-path. **Konsekuensi:** kalau folder referensi (`native-target`, dll.) di §0 di atas nanti di-connect, TIDAK ADA proteksi otomatis dari `settings.json` yang mencegah AI menulis ke folder read-only itu — kedisiplinan "jangan edit folder read-only" murni bergantung pada instruksi `CLAUDE.md` (§Folder yang perlu di-connect, kolom "Read-only"), bukan enforcement teknis. Dicatat di sini supaya tidak diasumsikan ada proteksi teknis yang sebenarnya tidak ada. Kalau dev ingin proteksi teknis ditambahkan, itu permintaan terpisah (edit manual `.claude/settings.json`, bukan bagian gate Step 1 ini).

---

## Ringkasan untuk Review — Perlu Konfirmasi User

1. **Modul ini punya dokumentasi retroaktif lengkap dari project `doc-dev/backfill`** (branch `backfill/17.0`: `01A_FUNCTIONAL_SPEC.md`, `01B_ACCEPTANCE_CRITERIA.md`, plus test suite yang sudah dieksekusi via Docker 2026-07-31) — dipakai sebagai "FUNCTIONAL_SPEC.md lama" untuk mengisi `01b_BASELINE_SPEC.md` (lihat §4 di bawah), BUKAN ditulis ulang dari nol. Kode modul **tidak berubah** sejak dokumen itu ditulis (dicek lewat `git log -- pos_margin_threshold`, commit terakhir yang menyentuh modul ini sebelum sesi migrasi adalah penambahan test files, bukan perubahan business logic) — jadi tingkat kepercayaan dokumen ini terhadap kode saat ini tinggi.
2. **[GAP] BARU ditemukan sesi ini (belum tercatat di backfill):** `views/product_template_views.xml` **tidak terdaftar** di `data:` manifest, dan mendefinisikan XML-ID (`product_template_inherit_pos_margin_threshold`) yang **sama persis** dengan yang didefinisikan `views/products.xml` (isi & `inherit_id` target beda). File ini dead code — tidak pernah dimuat Odoo 17.0 sekarang. Dicatat sebagai `MF-04` di `FINDINGS.md`, tag `[DIWARISI-SOURCE]` — **wajib dipertahankan sebagai dead file yang sama di 18.0** (jangan "dibersihkan"/didaftarkan ke manifest), kecuali dev menyetujui eksplisit ini perubahan yang disengaja.
3. **3 finding backfill yang relevan modul ini (F-01, F-02, F-03) diwariskan ke `MF-01`/`MF-02`/`MF-03`** — semuanya `[PERLU-KEPUTUSAN]` di level backfill, **belum ada keputusan pemilik modul**. Untuk migrasi ini, defaultnya: dipertahankan identik (bug/quirk existing bukan tanggung jawab migrasi untuk diperbaiki), tapi WAJIB dicek ulang di Step 2 apakah mekanismenya (compute/inverse Odoo, MRO Python multi-module) berubah caranya bekerja di 18.0 — kalau platform 18.0 mengubah urutan resolusi MRO/compute secara berbeda, F-01/F-03 bisa berubah dari "quirk existing" jadi "gap migrasi baru" yang butuh keputusan berbeda.
4. **Sifat migrasi: port kode saja** (dikonfirmasi dev di bootstrap) — Step 7 N/A.
5. Field terbuka §0/§4a/§4b di bawah **belum dijawab dev** — gate Step 1 belum bisa ditutup sampai ini terisi.

---

## 1. Modul & Scope

- Modul yang dimigrasi: `pos_margin_threshold` (bagian dari project multi-modul 3-addon, lihat `CLAUDE.md` root — 2 modul lain: `sale_margin_threshold`, `pin_message`, dikerjakan sebagai intake terpisah)
- Deskripsi singkat fungsi modul: menghitung & menegakkan harga jual minimum + margin per produk khusus transaksi Point of Sale — memberi peringatan (atau memblokir pembayaran sesuai konfigurasi) kalau kasir menjual produk di bawah harga minimumnya.
- Apakah modul-modul ini saling depend satu sama lain: **Tidak lewat `depends:` manifest** (tidak ada `sale_margin_threshold`/`pin_message` di `depends:` modul ini) — TAPI ada interaksi RUNTIME implisit kalau `sale_margin_threshold` juga terinstall bersamaan (lihat MF-01/MF-03: nama model `wizard.margin.product` sama persis tanpa `_inherit`, dan `sale_margin_threshold._register_hook()` membaca status install modul ini). Interaksi ini terjadi di LUAR kontrol dependency graph Odoo — tidak akan terdeteksi cuma dari baca `__manifest__.py`.

## 2. Dependency Map (auto-scan)

| Dependency | Tipe (Native Community / Native Enterprise / OCA / Custom) | Versi tersedia di target? | Catatan |
|---|---|---|---|
| `base` | Native Community | Ya (core Odoo 18.0) | Belum dicek detail API — Step 2 |
| `point_of_sale` | Native Community | Ya (core Odoo 18.0) | **Prioritas cek Step 2** — modul ini paling banyak API POS JS yang dipatch (lihat §2b), area paling rawan breaking change 17→18 (arsitektur POS JS/Owl sering berubah signifikan antar versi) |
| `product` | Native Community | Ya (core Odoo 18.0) | |
| `stock_account` | Native Community | Ya (core Odoo 18.0) | Dipakai untuk `stock_account.view_category_property_form_stock` (inherit view kategori produk) |

Dependency opsional yang dicek runtime (mis. `'hr.employee' in self.env`) — tidak ditemukan pola seperti ini di modul ini dari pembacaan kode langsung.

**Tidak ada indikasi dependency Enterprise atau OCA dari auto-scan** — lihat §0 untuk pertanyaan konfirmasi eksplisit ke dev (scan kosong bukan jawaban final).

## 2b. Struktur & Fitur Modul (auto-scan)

| Fitur | Ada di modul? | Lokasi/bukti (kalau ada) | Fase step 6 yang jadi relevan |
|---|---|---|---|
| Controllers (route custom) | ☐ Tidak (dead scaffold) | `controllers/controllers.py` — seluruh isi di-comment, tidak ada route terdaftar | D1 — kemungkinan besar N/A, cukup dinyatakan sekali di Applicability Check |
| Assets/CSS/JS custom | ☑ Ya | `static/src/store/models/models.js`, `static/src/store/pos_store.js`, key `assets.point_of_sale._assets_pos` di manifest | D2, E, F — **relevan, prioritas tinggi** |
| Komponen Owl/JavaScript custom | ☑ Ya (patch, bukan komponen baru) | `models.js` (patch `Product`/`Orderline`/`Order` prototype), `pos_store.js` (patch `PosStore` prototype) — pola `patch()` dari `@web/core/utils/patch`, BUKAN komponen Owl baru (`Component extends`) | E, F — **relevan**, tapi fokus ke API POS store 17→18 (kemungkinan `models.js`/`pos_store.js` di-refactor jadi struktur data lain di 18.0, cek `migration-tool/knowledge/version-diffs/17-to-18.md`) |
| Field JSON, relasi berantai (>2 level), atau dynamic model creation (`self.env[var]`) | ☐ Tidak | Semua field di `models/product.py` relasi langsung (`categ_id`, `product_tmpl_id`), tidak ada `self.env[var]` dinamis | B2 — N/A |
| View pakai `attrs=`/`states=`/`domain=`/`context=` dinamis | ☑ Ya (`invisible=` dengan ekspresi Python string, bukan `attrs=` lama) | `views/products.xml`, `views/product_template_views.xml`: `invisible="product_variant_count &gt; 1 and not is_product_variant"` — **sudah pakai sintaks Odoo 17 baru (ekspresi langsung), bukan `attrs={...}` gaya lama** | C2 — relevan, tapi migrasi kemungkinan minimal karena sudah pakai sintaks yang API 18.0 juga pakai (perlu dikonfirmasi di Step 2, bukan diasumsikan aman) |

**Catatan tambahan hasil baca langsung (di luar kolom tabel):**
- `views/product_template_views.xml` **tidak ada di `data:` manifest** — dead file, duplikat XML-ID dengan `views/products.xml` (lihat "Ringkasan untuk Review" poin 2, `MF-04`).
- Wizard `wizard.margin.product` didefinisikan `_name` (bukan `_inherit`) identik di modul sibling `sale_margin_threshold` — relevan ke Step 2 kalau ada perubahan cara Odoo 18.0 resolve model registry dengan `_name` ganda (kemungkinan kecil berubah, tapi wajib dicek, bukan diasumsikan sama seperti 17.0 — lihat `MF-03`).

## 3. Sifat Migrasi

- [x] Port kode saja (belum ada data produksi — instalasi baru di versi target)
- [ ] Upgrade instance (ada data produksi — step 7 Data Migration Scripts wajib jalan)

## 4. Baseline Spec / Characterization Test (gate)

- [x] Cek dulu: apakah modul punya `FUNCTIONAL_SPEC.md` lama di `source-codebase`? **Ya** — `doc-dev/backfill/spec/pos_margin_threshold/01A_FUNCTIONAL_SPEC.md` + `01B_ACCEPTANCE_CRITERIA.md` (branch `backfill/17.0`, commit `9fb8905`, tanggal 2026-07-31). Ini bukan requirement doc asli (ditulis retroaktif dari kode oleh project BACKFILL sebelumnya), tapi levelnya setara — sudah lewat proses cross-check kode + eksekusi test Docker nyata, bukan cuma baca statis.
  - Proses yang dijalankan: (1) baca `01A_FUNCTIONAL_SPEC.md`/`01B_ACCEPTANCE_CRITERIA.md` sebagai draft awal, (2) cross-check tiap BR/AC ke kode aktual di `models/product.py`, `models/pos_config.py`, `models/res_config_settings.py`, `models/pos_session.py`, `wizard/wizard_margin_product.py`, `static/src/store/*.js`, `views/*.xml` — **semua klaim BR-01..BR-07 cocok persis dengan kode saat ini** (line-by-line, tidak ada penyimpangan ditemukan), (3) hasil disalin/dirangkum jadi `BSL-NNN` ber-tag `[MATCH]` di `01b_BASELINE_SPEC.md`, referensi ID asal `BR-NNN`/`AC-NN-NN`.
  - Satu penyimpangan ditemukan yang TIDAK tercakup dokumen lama sama sekali (bukan `[GAP]` — tidak ada klaim lama yang dibandingkan, murni temuan baru): `views/product_template_views.xml` dead/duplicate XML-ID (lihat poin 2 di atas).
- [x] `01b_BASELINE_SPEC.md` sudah diisi.

### 4a. Dokumen Pelengkap Lain

- [x] **Dikonfirmasi tidak ada dokumen pelengkap lain** (dev, 2026-08-24) — backfill spec + kode aktual cukup sebagai baseline.

## 4b. Source Masih Aktif Dikembangkan?

- [x] **Tidak** — dikonfirmasi dev (2026-08-24), source dibekukan selama migrasi berjalan. `SYNC_POLICY.md` tidak dibuat.

## 5. Scope Boundary

- Yang harus tetap identik pasca migrasi: seluruh business rule BR-01..BR-07 (lihat `01b_BASELINE_SPEC.md`), termasuk 3 quirk yang diwarisi (MF-01/MF-02/MF-03) dan typo method `action_assing_margin` (BUKAN "assign" — konsisten dipakai model+view, jangan "diperbaiki" jadi benar secara ejaan karena itu mengubah nama method yang dirujuk view).
- Yang sengaja diubah/di-drop selama migrasi: **belum ada** — kalau Step 2/3 menemukan sesuatu yang WAJIB berubah demi kompatibilitas API 18.0 (mis. struktur `pos_store.js` yang berubah total), itu dicatat sebagai keputusan migrasi teknis di `03_MIGRATION_SPEC.md`, bukan perubahan scope/fitur.

## 6. Constraint

- Deadline: **[BELUM DIJAWAB]**
- Owner tiap step (Dev/QA/PM/FA): **[BELUM DIJAWAB]**
