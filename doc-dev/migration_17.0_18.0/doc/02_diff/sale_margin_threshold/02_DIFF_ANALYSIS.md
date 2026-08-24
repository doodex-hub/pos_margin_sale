# Diff & Compatibility Analysis — sale_margin_threshold

**Step:** 2 — Diff & Compatibility Analysis
**Versi:** 17.0 → 18.0
**Tanggal:** 2026-08-24
**Ref:** `01_intake/sale_margin_threshold/01a_MIGRATION_INTAKE.md`, `01_intake/sale_margin_threshold/01b_BASELINE_SPEC.md`, `migration-tool/knowledge/`

> Batasan metodologis sama seperti `pin_message` — tidak ada `native-target` tersedia (dikonfirmasi Step 1). Beda dengan `pin_message`, sebagian besar temuan modul ini berasal dari item **High Confidence** knowledge base (sumber PR resmi Odoo, bukan dugaan AI) karena modul ini pakai `ir.ui.view`/XML biasa (bukan Owl JS custom) — area yang sudah lebih terpetakan di `17-to-18.md`.

---

## 0. Knowledge Base Check

| Sumber | Sudah ada entry? | Lokasi |
|---|---|---|
| `version-diffs/17-to-18.md` | Ya | §1 — item `<tree>`→`<list>` (Critical Blocker) **langsung berlaku ke modul ini**, lihat DIFF-01 |
| `dependency-compat/sale_report` (project `advanced_sales_analysis`) | Ya, tapi tidak langsung relevan | Soal `sale.report`, modul ini tidak menyentuh `sale.report` |

## 0b. Gate Community vs Enterprise
- [x] Tidak ada dependency Enterprise (`base`/`product`/`sale`/`stock_account`, semua Community). N/A.

## 0c. Gate Transitive Dependency
- [x] Tidak ada dependency yang dihapus. N/A.

---

## 1. Perubahan Native (Core/Enterprise)

| ID | File/simbol modul | Simbol native terkait | Status di target | Dampak | Sumber |
|---|---|---|---|---|---|
| DIFF-01 | `views/sale_order.xml` — 2 xpath: `//page[@name='order_lines']/field[@name='order_line']/tree` (position `inside`), dan `.../tree/field[@name='price_unit']` (position `attributes`) | Embedded list view order_line di `sale.view_order_form` — elemen `<tree>` | **Dihapus/Rename** — `<tree>` diganti `<list>` di 18.0, XML-ID yang MENGANDUNG kata "tree" tetap dipertahankan (tidak relevan di sini, ini soal TAG elemen, bukan XML-ID) | **Kritis — install-blocking.** Kalau `sale.view_order_form` core 18.0 mengganti elemen order_line jadi `<list>`, KEDUA xpath ini gagal match saat parsing (`ParseError`), modul **gagal install total**, bukan cuma gagal sebagian fitur | **High Confidence** — `migration-tool/knowledge/version-diffs/17-to-18.md` §1, dikonfirmasi via PR resmi [odoo/odoo#159909](https://github.com/odoo/odoo/pull/159909) DAN dry-run langsung project lain (bukan spekulasi) |
| DIFF-02 | `models/sale_order.py` — override `action_confirm()` (nama method core) | `sale.order.action_confirm()` | Perlu dicek: apakah cara Odoo 18.0 memanggil `action_confirm` dari batch action list view berubah | **Terkait `MF-06`** — kalau mekanisme batch-call berubah, bug existing (crash singleton) bisa bermanifestasi beda, BUKAN otomatis hilang/sama | **[TIDAK TERVERIFIKASI]** — tidak ada `native-target` untuk cek langsung. Pengetahuan umum AI: mekanisme `action_confirm` dari list view (`ir.actions.server`/binding button) secara arsitektural stabil lintas versi Odoo (bukan area yang diketahui direstruktur), confidence SEDANG bahwa BEHAVIOR crash yang sama tetap terjadi identik — tapi tetap wajib diverifikasi eksekusi nyata Step 6/9 (re-run test yang sama: `test_action_confirm_BATCH_MULTI_ORDER_F05`), jangan diasumsikan dari analisis ini saja |
| DIFF-03 | `views/product_template_views.xml` + `views/products.xml` — duplikasi XML-ID `product_template_inherit_sale_margin_threshold` (`MF-07`) | Mekanisme load `data:` manifest ORM (urutan sekuensial, XML-ID sama = update record yang sama) | Tidak berubah — ini mekanisme ORM dasar (load data files), bukan API yang didokumentasikan berubah di `17-to-18.md` manapun | Rendah risiko migrasi (mekanismenya stabil) — TAPI efek quirk `MF-07` (satu kustomisasi silently discarded) tetap harus dipertahankan identik, bukan "diperbaiki" sebagai bagian migrasi | Pengetahuan umum AI — load data XML urutan sekuensial adalah perilaku ORM yang sangat stabil, tidak ada indikasi perubahan di knowledge base manapun |
| DIFF-04 | `views/products.xml`, `views/product_template_views.xml` — `invisible="module_pos_margin_threshold == True or product_variant_count > 1 and not is_product_variant"` (ekspresi Python langsung, bukan `attrs={}`) | Sintaks `invisible=`/`attrs=` view | Sudah pakai sintaks modern (ekspresi langsung) — **tidak** pakai `attrs={...}` gaya sangat lama | **N/A — sudah compliant.** Field yang dipakai di ekspresi ini (`module_pos_margin_threshold`, `product_variant_count`, `is_product_variant`) otomatis dianggap invisible field oleh 18.0 (PR #137031) — field yang sudah dideklarasikan eksplisit `invisible="1"` di XML (mis. `<field name="module_pos_margin_threshold" invisible="1"/>`) TETAP valid, cuma jadi sedikit redundant (bukan breaking) | High Confidence — `17-to-18.md` §1 |
| DIFF-05 | `views/res_config_settings.xml` — `inherit_id="sale.res_config_settings_view_form"`, xpath `//block[@name='quotation_order_setting_container']` | Struktur `res.config.settings` form Sales core | **[TIDAK TERVERIFIKASI]** | Sedang — kalau nama block/struktur setting Sales berubah, setting "Blocking Transaction Order" tidak akan muncul di halaman Settings (silent, bukan error install — `position="inside"` di xpath yang tidak ketemu biasanya `ParseError` juga sebenarnya, jadi tetap install-blocking kalau xpath gagal match) | Pengetahuan umum AI — halaman Settings Sales relatif jarang berubah struktur block besar-besaran, confidence sedang bahwa ini stabil, tapi belum dikonfirmasi |
| DIFF-06 | `views/products.xml`, `views/product_template_views.xml` — `inherit_id="product.product_template_form_view"` vs `product.product_template_only_form_view`, `product.product_variant_easy_edit_view` | XML-ID view core `product` module | **[TIDAK TERVERIFIKASI]** | Sedang — sama seperti `pos_margin_threshold` DIFF setara, XML-ID spesifik core yang jadi target inherit | Pengetahuan umum AI — XML-ID ini sudah ada sejak versi lama Odoo, historically stabil, tapi tidak ada konfirmasi eksplisit 18.0 |
| DIFF-07 | `security/groups.xml` — `implied_ids` ref `base.module_category_hidden` | XML-ID `base.module_category_hidden` | Kemungkinan besar stabil (kategori modul tersembunyi adalah konsep dasar `base`) | Rendah | Pengetahuan umum AI |
| DIFF-08 | Python: `_register_hook()`, tidak ada `create()`/`_name_search`/`_check_recursion`/`search()` override; `hasattr(self, 'is_rental_order')` bukan `user_has_groups` | API ORM §1 knowledge base | **N/A — tidak berlaku** | — | Verifikasi statis langsung |
| DIFF-09 | Tidak ada Owl/JS component sama sekali di modul ini (`assets` manifest declare folder yang tidak eksis, `MF-08`) | Owl JS/Template migration order, `useService` | **N/A — tidak berlaku** | — | Verifikasi statis langsung |

---

## 2. Kompatibilitas Dependency (OCA/Third-Party)

N/A — tidak ada dependency OCA/third-party.

---

## 3. Temuan Baru — Tulis ke Migration Records

- [x] **DIFF-01 (`<tree>`→`<list>` di xpath embedded order_line) adalah kandidat kuat entry baru** `dependency-compat/sale/17-to-18.md` — pola ini (modul yang inherit ke `sale.view_order_form` dan xpath ke sub-list order_line) kemungkinan besar berlaku untuk BANYAK modul custom lain yang extend Sale Order form, bukan cuma modul ini. Dicatat sebagai kandidat, ditulis ke `migration-tool/migration-records/pos-margin-sale_17.0_18.0/SUMMARY.md` setelah dikonfirmasi lewat instalasi nyata Step 6 (kategori `dependency-compat`).
- [ ] Belum ditulis ke `SUMMARY.md` — menunggu konfirmasi instalasi nyata.

---

## 4. Ringkasan Risiko

| Item | Level risiko | Catatan |
|---|---|---|
| DIFF-01 (`<tree>`→`<list>` order_line xpath) | **Kritis** | Install-blocking, HIGH CONFIDENCE dari PR resmi — ini WAJIB diperbaiki di Step 3/6 (ganti `/tree`→`/list` di kedua xpath), bukan opsional. Prioritas #1 mutlak modul ini |
| DIFF-02 (batch-confirm bug, `MF-06`) | Sedang-Tinggi | Bug existing harus dipertahankan, tapi manifestasinya perlu diverifikasi ulang eksekusi nyata (test sudah ada dari backfill, tinggal re-run pasca migrasi) |
| DIFF-05 (xpath settings Sales) | Sedang | Tidak terverifikasi, potensi install-blocking kalau xpath gagal match — cek di G1 |
| DIFF-03, DIFF-06, DIFF-07 | Rendah-Sedang | Mekanisme stabil/XML-ID lama, risiko lebih rendah dari DIFF-01/02/05 |
| DIFF-04, DIFF-08, DIFF-09 | N/A | Dikonfirmasi tidak berlaku |
| **Modul ini secara keseluruhan** | **Tinggi**, didominasi SATU item kritis konkret (DIFF-01) | Beda karakter dari `pin_message` (banyak unknown tersebar) — modul ini py risikonya lebih TERKONSENTRASI dan sudah punya fix yang jelas (ganti tag), tapi tetap install-blocking kalau terlewat |
