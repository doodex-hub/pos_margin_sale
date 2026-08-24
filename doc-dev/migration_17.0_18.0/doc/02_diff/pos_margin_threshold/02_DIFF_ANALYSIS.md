# Diff & Compatibility Analysis — pos_margin_threshold

**Step:** 2 — Diff & Compatibility Analysis
**Versi:** 17.0 → 18.0
**Tanggal:** 2026-08-24
**Ref:** `01_intake/pos_margin_threshold/01a_MIGRATION_INTAKE.md`, `01_intake/pos_margin_threshold/01b_BASELINE_SPEC.md`, `migration-tool/knowledge/`

> Batasan metodologis sama seperti 2 modul lain — tidak ada `native-target` tersedia. Tidak ada entry `dependency-compat/point_of_sale` di knowledge base saat ini (modul ini jadi yang pertama menyentuh area POS frontend).

---

## 0. Knowledge Base Check

| Sumber | Sudah ada entry? | Lokasi |
|---|---|---|
| `version-diffs/17-to-18.md` | Ya | §1 relevan: tidak ada `<tree>` di modul ini (dicek, N/A); §1c (`useService("rpc")` dihapus) relevan sebagai POLA WASPADA walau modul ini tidak pakai `useService` sama sekali |
| `dependency-compat/point_of_sale` | **Tidak ada** | Modul pertama migration-tool yang menyentuh `point_of_sale` frontend secara signifikan |

## 0b. Gate Community vs Enterprise
- [x] Semua dependency (`base`/`point_of_sale`/`product`/`stock_account`) Community. N/A.

## 0c. Gate Transitive Dependency
- [x] Tidak ada dependency dihapus. N/A.

---

## 1. Perubahan Native (Core/Enterprise)

| ID | File/simbol modul | Simbol native terkait | Status di target | Dampak | Sumber |
|---|---|---|---|---|---|
| DIFF-01 | Seluruh `views/*.xml` — tidak ada tag `<tree>` sama sekali (semua inherit ke form view) | `<tree>`→`<list>` | **N/A — tidak berlaku** | — | Verifikasi statis langsung (dicek `grep -r tree` di seluruh modul, 0 match) |
| DIFF-02 | `static/src/store/models/models.js` — `import { Orderline, Product, Order } from "@point_of_sale/app/store/models"` | Path modul `@point_of_sale/app/store/models`, class `Orderline`/`Product`/`Order` | **[TIDAK TERVERIFIKASI]** | **Tinggi** — arsitektur frontend POS Odoo historically mengalami restrukturisasi cukup sering antar versi mayor (termasuk kemungkinan pemecahan file/rename class). Kalau path/nama export ini berubah, `patch()` gagal total, SELURUH kustomisasi POS modul ini (highlight harga, blocking pembayaran) tidak aktif — POS tetap jalan normal (tidak crash total kemungkinan besar, tergantung apakah import error mematikan seluruh bundle atau cuma modul ini), tapi fitur modul hilang silent kalau errornya cuma warning console | Pengetahuan umum AI mengenai riwayat arsitektur POS Odoo — **BUKAN** dari cross-check source 18.0 langsung |
| DIFF-03 | `static/src/store/pos_store.js` — `import { PosStore } from "@point_of_sale/app/store/pos_store"` | Path modul `@point_of_sale/app/store/pos_store`, class `PosStore` | **[TIDAK TERVERIFIKASI]** | Tinggi — sama pola risiko DIFF-02. Method yang di-patch (`_loadProductProduct`) sendiri juga perlu dicek apakah masih ada nama/signature yang sama | Sama seperti DIFF-02 |
| DIFF-04 | `static/src/store/models/models.js` — `import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup"`, `import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup"` | Path/komponen popup POS | **[TIDAK TERVERIFIKASI]** | Tinggi — popup adalah UI dasar POS, kemungkinan lebih stabil dari model data (DIFF-02/03), tapi tetap dua path terpisah yang keduanya harus tetap valid | Pengetahuan umum AI |
| DIFF-05 | `models/pos_session.py` — override `_loader_params_product_product()` (extend via `super()`, pattern override benar) | Method `pos.session._loader_params_product_product` | **[TIDAK TERVERIFIKASI]** | Sedang-Tinggi — mekanisme loader data POS (bagaimana field dikirim dari server ke frontend) adalah salah satu area yang historically berubah antar versi POS Odoo (mis. shift ke pola data loading berbeda). Kalau method ini di-rename/dihapus, field `minimum_sale_price`/`minimum_sale_price_with_tax` tidak akan pernah sampai ke frontend — fitur blocking/highlight harga diam-diam tidak berfungsi (data selalu `undefined`→fallback 0 dari `[BSL-008]`, jadi TIDAK ADA baris yang pernah dianggap "di bawah minimum") | Pengetahuan umum AI — bagian dari arsitektur "loader" POS yang historically berevolusi |
| DIFF-06 | `views/products.xml`, `views/product_template_views.xml` — `inherit_id="product.product_template_form_view"`/`product.product_template_only_form_view"`/`product.product_variant_easy_edit_view"`, `stock_account.view_category_property_form_stock` | XML-ID view core `product`/`stock_account` | **[TIDAK TERVERIFIKASI]** | Sedang — XML-ID lama, historically stabil, tapi belum dikonfirmasi 18.0 | Pengetahuan umum AI |
| DIFF-07 | `static/src/store/models/models.js` — `getDisplayData()` override (patch `Orderline.prototype`), memanggil banyak method core (`get_full_product_name`, `getPriceString`, `get_quantity_str`, dst) lewat `super()`-style call pattern? **Perlu dicek:** apakah `getDisplayData()` di modul ini SEPENUHNYA REPLACE (bukan extend `super.getDisplayData()`) — dibaca ulang dari kode: **YA, method ini full-override, tidak memanggil `super.getDisplayData()`** — pola SAMA seperti `MF-09` di `pin_message` (override total, bukan extend) | Method `Orderline.prototype.getDisplayData` core | Method ini sendiri me-replikasi SEMUA field data tampilan core (bukan cuma nambah field baru) — kalau core menambah field baru di versi 18.0 (concept baru di data tampilan orderline), field itu TIDAK akan ikut muncul karena override total ini tidak pernah delegasi ke core | **Sedang-Tinggi, TEMUAN BARU sesi ini** (belum tercatat di baseline spec/backfill sebagai quirk eksplisit — cuma disebut sebagai "patch Orderline.prototype" tanpa menyoroti bahwa ini override total, bukan extend). Pola risiko sama seperti `MF-09` pin_message: aman kalau core tidak berubah, tapi silently kehilangan field baru core kalau core memang menambah sesuatu di 18.0 | Verifikasi statis langsung kode `models.js:26-50` |
| DIFF-08 | Python: tidak ada `create()`/`_name_search`/`_check_recursion`/`search()` override, tidak ada `user_has_groups` | API ORM §1 | **N/A** | — | Verifikasi statis |
| DIFF-09 | JS: sudah `/** @odoo-module **/` + `import` ES6 + `patch()`, tidak ada `odoo.define`/`Component.extend()` | JS module system lama | **N/A — sudah compliant** | — | Verifikasi statis |

---

## 2. Kompatibilitas Dependency (OCA/Third-Party)

N/A.

---

## 3. Temuan Baru — Tulis ke Migration Records

- [x] **DIFF-07 adalah finding baru** (`getDisplayData()` full-override) — belum tercatat di `FINDINGS.md`. **Ditambahkan sekarang sebagai `MF-11`** (lihat `FINDINGS.md`), karena ini genuinely gap/pola-berisiko yang butuh keputusan/perhatian pemilik modul, bukan cuma catatan teknis diff biasa.
- [x] DIFF-02/03/04/05 (semua import path & override method POS) — kandidat kuat `dependency-compat/point_of_sale/17-to-18.md`, ditulis ke `migration-records/` setelah verifikasi instalasi nyata Step 6.

---

## 4. Ringkasan Risiko

| Item | Level risiko | Catatan |
|---|---|---|
| DIFF-02/03/04 (import path POS store/popup) | **Tinggi** | Tidak terverifikasi, area arsitektur POS yang historically berubah. Prioritas #1 Step 6 G1 |
| DIFF-05 (loader `_loader_params_product_product`) | **Tinggi** | Kalau gagal, fitur silently mati (bukan crash) — WAJIB verifikasi G2 (test end-to-end: jual produk di bawah minimum, cek popup/block benar-benar muncul), G1 install sukses TIDAK CUKUP membuktikan ini jalan |
| DIFF-07 (`getDisplayData()` full-override, `MF-11` baru) | Sedang-Tinggi | Sama pola `MF-09` pin_message — aman kalau core tidak nambah field baru, tapi tidak akan ketahuan dari testing manapun kecuali core 18.0 memang menambah field yang "hilang" ini |
| DIFF-06 | Sedang | XML-ID historically stabil |
| DIFF-01, DIFF-08, DIFF-09 | N/A | Tidak berlaku |
| **Modul ini secara keseluruhan** | **Tinggi** | Konsisten dengan urutan prioritas di `CLAUDE.md` (setelah `pin_message`, sebelum `sale_margin_threshold` dari sisi jumlah unknown, tapi `sale_margin_threshold` py 1 item install-blocking konkret jadi urgensi imediatnya lebih tinggi) |
