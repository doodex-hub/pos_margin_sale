# Migration Intake — sale_margin_threshold

**Step:** 1 — Intake & Scope
**Versi:** 17.0 → 18.0
**Tanggal:** 2026-08-24
**Status:** ✔️ Gate lulus (2026-08-24) — checklist §0/§0a/§4a/§4b sama seperti `pos_margin_threshold`, dev sudah konfirmasi jawaban berlaku untuk seluruh project ini (lihat catatan di tiap sub-section)

---

## 0. Folder Referensi

- [x] `native-target`/`native-source`/`native-target-enterprise`/`third-party-*` — **dikonfirmasi dev (sesi 2026-08-24, saat Step 1 `pos_margin_threshold`): tidak ada satupun tersedia di disk, dan tidak ada dependency Enterprise/OCA.** Berlaku sama untuk modul ini (dependency `base`, `product`, `sale`, `stock_account` — semuanya Community, konsisten). Step 2 modul ini juga akan dikerjakan tanpa akses native core.

### 0a. Konfirmasi Branch/Versi

- [x] Sama seperti `pos_margin_threshold` — source `backfill/17.0`, target `migration/18.0`, versi 17.0→18.0, dual-branch (bukan dual-clone). Lihat `CLAUDE.md` §Adaptasi dual-branch.

### 0b. Gate Path Absolut `.claude/settings.json`

- [x] Sama seperti dicatat di `01_intake/pos_margin_threshold/01a_MIGRATION_INTAKE.md` §0b — tidak ada placeholder `{{ABS_PATH_...}}` di file ini, tidak ada proteksi teknis ke folder read-only.

---

## Ringkasan untuk Review — Perlu Konfirmasi User

1. **Sama seperti `pos_margin_threshold`, modul ini punya dokumentasi backfill lengkap** (`doc-dev/backfill/spec/sale_margin_threshold/01A_FUNCTIONAL_SPEC.md` + `01B_ACCEPTANCE_CRITERIA.md`, branch `backfill/17.0`, 2026-07-31, tervalidasi eksekusi Docker) — dipakai sebagai dasar `01b_BASELINE_SPEC.md`. Kode tidak berubah sejak dokumen itu ditulis (`git log -- sale_margin_threshold` — commit terakhir cuma menambah test files).
2. **[GAP] BARU ditemukan sesi ini — LEBIH SERIUS dari temuan serupa di `pos_margin_threshold` (`MF-04`):** `views/product_template_views.xml` **DAN** `views/products.xml` KEDUANYA terdaftar di `data:` manifest (beda dari `pos_margin_threshold`, di mana salah satunya dead/tidak terdaftar) — dan KEDUANYA mendefinisikan XML-ID yang **sama persis** (`product_template_inherit_sale_margin_threshold`) dengan `inherit_id` target berbeda. Karena keduanya benar-benar dimuat Odoo (bukan dead file), efeknya: record kedua yang di-load (`products.xml`, urutan manifest setelah `product_template_views.xml`) **menimpa seluruh field record pertama** — termasuk `inherit_id`-nya. Akibatnya kustomisasi yang ditujukan untuk `product.product_template_only_form_view` (dari `product_template_views.xml`) **tidak pernah benar-benar aktif**, walau filenya "termuat" di manifest. Dicatat sebagai `MF-07` di `FINDINGS.md`.
3. **3 finding backfill relevan modul ini diwarisi:** `MF-03` (wizard MRO collision, sudah tercatat dari sisi `pos_margin_threshold`, modul ini co-owner), `MF-05` (baru: `_register_hook` memutasi group membership, dari backfill F-04), `MF-06` (baru: `action_confirm` memecah batch-confirm Odoo core — **prioritas TINGGI**, dari backfill F-05).
4. **`MF-06` (batch-confirm crash) butuh perhatian ekstra di Step 2/3** — ini bug existing yang HARUS dipertahankan identik per aturan `CLAUDE.md` (jangan diperbaiki), TAPI kalau Odoo 18.0 mengubah cara `action_confirm` dipanggil dari list view (mis. batching berbeda), gejala krusial ini bisa muncul beda caranya, bukan hilang sendiri. Perlu dicek eksplisit di Step 2 apakah mekanisme batch action dari list view core berubah.
5. Sifat migrasi: port kode saja (sama seperti keseluruhan project).

---

## 1. Modul & Scope

- Modul yang dimigrasi: `sale_margin_threshold`
- Deskripsi singkat: menegakkan aturan harga jual minimum + margin untuk **Sale Order** — memblokir atau meminta konfirmasi tambahan saat user confirm quotation yang mengandung baris di bawah harga minimum produk.
- Depend ke modul sibling: **Tidak lewat manifest**, tapi ada interaksi runtime sama seperti `pos_margin_threshold` (lihat `MF-03`, `MF-05`) — model `wizard.margin.product` duplikat `_name`, dan `_register_hook` membaca status install `pos_margin_threshold`.

## 2. Dependency Map (auto-scan)

| Dependency | Tipe | Versi tersedia di target? | Catatan |
|---|---|---|---|
| `base` | Native Community | Ya | |
| `product` | Native Community | Ya | |
| `sale` | Native Community | Ya | **Prioritas Step 2** — `action_confirm` di-override, area sale order form/logic yang paling mungkin berubah struktur di 18.0 |
| `stock_account` | Native Community | Ya | Sama seperti `pos_margin_threshold`, dipakai untuk view kategori produk |

Tidak ada indikasi Enterprise/OCA dari auto-scan (dikonfirmasi eksplisit dev, lihat §0).

**Dependency implisit/opsional dicek runtime:** `hasattr(self, 'is_rental_order')` di `models/sale_order.py:14` — cek apakah modul rental (`sale_renting` atau serupa) terinstall, TIDAK dideklarasikan di `depends:` manifest (disengaja, supaya modul ini tidak mewajibkan install rental). **Wajib dicek Step 2:** apakah field `is_rental_order` masih bernama sama di modul rental Odoo 18.0.

## 2b. Struktur & Fitur Modul (auto-scan)

| Fitur | Ada di modul? | Lokasi/bukti | Fase step 6 relevan |
|---|---|---|---|
| Controllers (route custom) | ☐ Tidak (dead scaffold, sama seperti `pos_margin_threshold`) | `controllers/controllers.py` — seluruh isi di-comment | D1 — N/A |
| Assets/CSS/JS custom | ☐ Tidak ditemukan file JS aktual, TAPI `assets.sale_margin_threshold._assets_sale` dideklarasikan di manifest tanpa ada `static/src/` sama sekali di struktur folder | D2, E, F — kemungkinan N/A, **wajib dicek Step 2/6 apakah key assets kosong ini valid di 18.0 atau perlu dihapus** (bukan "fitur hilang", tapi manifest declare folder yang tidak eksis) |
| Komponen Owl/JavaScript custom | ☐ Tidak ada | — | E, F — N/A |
| Field JSON/relasi berantai/dynamic model | ☐ Tidak | | B2 — N/A |
| View pakai ekspresi dinamis (`invisible=`) | ☑ Ya | `views/products.xml`, `views/product_template_views.xml`, `views/sale_order.xml` — sintaks ekspresi langsung (Odoo 17 baru), bukan `attrs=` lama | C2 — relevan tapi migrasi minimal (lihat catatan sama di `pos_margin_threshold`) |

**Catatan tambahan hasil baca langsung:**
- `assets.sale_margin_threshold._assets_sale` di manifest menunjuk ke `sale_margin_threshold/static/src/**/*` — **folder `static/src/` TIDAK ADA** di struktur file modul ini (beda dari `pos_margin_threshold` yang benar-benar punya JS). Ini bukan dead code brutal (tidak error, glob kosong cuma tidak match apapun) tapi berpotensi jejak development yang belum selesai/dibersihkan. Dicatat sebagai `MF-08` di `FINDINGS.md`.
- Duplikasi XML-ID `product_template_inherit_sale_margin_threshold` — lihat "Ringkasan" poin 2, `MF-07`.

## 3. Sifat Migrasi

- [x] Port kode saja
- [ ] Upgrade instance

## 4. Baseline Spec / Characterization Test (gate)

- [x] `FUNCTIONAL_SPEC.md` lama: `doc-dev/backfill/spec/sale_margin_threshold/01A_FUNCTIONAL_SPEC.md` + `01B_ACCEPTANCE_CRITERIA.md` — proses sama seperti `pos_margin_threshold` (cross-check ke kode aktual, semua BR-01..BR-06 cocok, `[MATCH]`).
- [x] `01b_BASELINE_SPEC.md` sudah diisi.

### 4a. Dokumen Pelengkap Lain
- [x] Dikonfirmasi tidak ada (sama jawaban dev seperti `pos_margin_threshold`).

## 4b. Source Masih Aktif Dikembangkan?
- [x] Tidak — dikonfirmasi dev, berlaku sama untuk seluruh project.

## 5. Scope Boundary

- Tetap identik: seluruh BR-01..BR-06, termasuk bug batch-confirm (`MF-06`) dan quirk dedup group (`MF-05`) — TIDAK diperbaiki sebagai bagian migrasi.
- Diubah/di-drop: belum ada — kalau Step 2/3 menemukan API `action_confirm`/rental detection WAJIB berubah demi kompatibilitas 18.0, dicatat di `03_MIGRATION_SPEC.md` sebagai keputusan teknis, bukan perubahan scope.

## 6. Constraint

- Deadline: **[BELUM DIJAWAB]**
- Owner: **[BELUM DIJAWAB]**
