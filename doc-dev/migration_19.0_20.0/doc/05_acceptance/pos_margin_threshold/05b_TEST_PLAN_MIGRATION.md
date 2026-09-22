# Test Plan (Migrasi) — pos_margin_threshold

**Step:** 5 — Acceptance Criteria & Test Plan (satu paket dengan `05a_MIGRATION_ACCEPTANCE_CRITERIA.md`)
**Ref:** `05_acceptance/pos_margin_threshold/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-09-22

> Modul ini SUDAH punya test assets nyata: `tests/test_margin_threshold_tour.py`,
> `tests/test_margin_sale.py`, `tests/test_cross_module.py` (Python, dijalankan via
> `--test-enable --test-tags`), dan tour `static/tests/tours/margin_threshold_tour.js` (2 tour: `..._confirm_tour`,
> `..._blocked_tour`). Kolom "Unit"/"Integration"/"Tour" di bawah MERUJUK test yang sudah ada ini
> kalau AC sudah tercakup — tidak mengasumsikan test baru harus ditulis dari nol kecuali eksplisit
> ditandai "BARU" di kolom Catatan.

---

## Step 9 — Dev Testing

> Eksekusi: **otomatis/background** — `odoo-bin -i pos_margin_threshold --test-enable --test-tags
> /pos_margin_threshold --stop-after-init`. Tour test (Owl/JS) dijalankan lewat `HttpCase.start_tour()`
> di dalam `TestPointOfSaleHttpCommon` (real Chrome headless) — sudah applicable untuk modul ini (Fase
> E/F migrasi murni verifikasi, tidak ada kode JS/template berubah kecuali `MF-34`).
>
> **Audit isi test (bukan cuma nama method) direkomendasikan** sebelum Step 9 dieksekusi penuh — lihat
> peringatan template `05b` soal `totp_enhancement` (108/129 method ternyata stub). Spot-check cepat
> sesi ini: SELURUH method test di `test_margin_sale.py`/`test_cross_module.py`/`test_margin_threshold_tour.py`
> punya isi assertion nyata (bukan `pass`/docstring kosong) — dikonfirmasi baca langsung file penuh,
> bukan `grep -c "def test_"`. Tidak ada stub ditemukan di ketiga file ini.

| AC | Deskripsi | Unit | Integration | Tour (Owl/JS) |
|---|---|---|---|---|
| AC-01-01 | margin_sale template baru = margin_sale kategori | — | `test_margin_sale.py::test_margin_sale_from_category` (ADA) | — |
| AC-01-02 | Override manual margin_sale persisten | — | `test_margin_sale.py::test_margin_sale_manual_override_persists` (ADA) | — |
| AC-01-03 | minimum_sale_price = standard_price*(1+margin/100) | — | `test_margin_sale.py::test_minimum_sale_price_computation` (ADA) | — |
| AC-01-04 | Inverse minimum_sale_price manual → margin_sale | — | `test_margin_sale.py::test_minimum_sale_price_inverse` (ADA) | — |
| AC-01-05 | Guard standard_price=0 | — | `test_margin_sale.py::test_minimum_sale_price_zero_standard_price_guard` (ADA) | — |
| AC-01-06 | Inverse product.product menulis ke template, bukan per-variant (`MF-01`) | — | `test_margin_sale.py::test_margin_sale_inverse_writes_to_shared_template_not_per_variant` (ADA) | — |
| AC-01-07 | `is_less_minimum_sale` tanpa `@api.depends` tetap TIDAK ditambahkan (`MF-23`) | BARU — cukup assert `_compute_warning` masih tanpa `@api.depends` via inspeksi `models.Model._fields['is_less_minimum_sale'].compute` atau baca source (AST) | — | — |
| AC-01-08 | Dual-path inverse/onchange `margin_sale` (`BSL-012`) | BARU — simulasikan `onchange()` (`product.onchange(values, ['margin_sale'], {...})`) terpisah dari `write()` langsung, assert `product_tmpl_id.margin_sale` ikut berubah lewat jalur onchange | — | — |
| AC-02-01 | Wizard dari list Template pre-populated `product_template_ids` | — | BARU — `wizard.margin.product.with_context(active_model='product.template').create(...)`, assert `is_product == False` | — |
| AC-02-02 | Wizard dari list Variant pre-populated `product_ids` | — | BARU — sama pola AC-02-01, context `active_model='product.product'`, assert `is_product == True` | — |
| AC-02-03 | Tombol Assign menulis margin ke semua record terpilih | — | `test_margin_sale.py::test_wizard_assign_margin_from_template_list` (ADA) | — |
| AC-02-04 | Tombol Cancel tidak mengubah apapun | — | BARU — kecil, low-risk (native `special="cancel"`), boleh ditunda ke Step 10 AI-interaktif kalau Step 9 mau tetap ramping | — |
| AC-03-01 | Tidak ada line melanggar → langsung pay(), tanpa dialog | — | — | BARU — belum ada tour untuk jalur "semua line aman" (lihat juga AC-03-05, kaitan `BSL-018`) |
| AC-03-02 | Dialog konfirmasi muncul, confirm → lanjut payment | — | — | `margin_threshold_tour.js::pos_margin_threshold_below_minimum_confirm_tour` (ADA), dieksekusi via `test_margin_threshold_tour.py::test_pos_margin_threshold_below_minimum_confirm_tour` |
| AC-03-03 | Dialog konfirmasi, DECLINE → pembayaran batal, tetap ProductScreen | — | — | BARU — tour existing hanya `Dialog.confirm()`, tidak pernah test jalur decline (`Dialog` util kemungkinan sudah punya helper cancel/dismiss — cek `dialog_util` sebelum menulis tour baru) |
| AC-03-04 | AlertDialog blocking total, tidak ada jalan proceed | — | — | `margin_threshold_tour.js::pos_margin_threshold_below_minimum_blocked_tour` (ADA), dieksekusi via `test_pos_margin_threshold_below_minimum_blocked_tour` |
| AC-03-05 | Semua line aman → NOL dialog sama sekali (`BSL-018`, carry-forward 2x) | — | — | BELUM ADA — **keputusan dev diperlukan dulu** (lihat §"Item Menunggu Keputusan Dev" di bawah) sebelum menulis tour baru |
| AC-04-01 | Warning text+minimumSalePriceWithTax muncul di orderline | — | — | Tercakup implisit lewat `..._confirm_tour`/`..._blocked_tour` (orderline ditambah sebelum Pay diklik) TAPI tour TIDAK assert konten/warna warning-nya sendiri secara eksplisit — lihat AC-04-03 |
| AC-04-02 | `t-attf-class` gabungan text-danger + combo core | — | — | Tercakup TIDAK LANGSUNG (tidak crash di tour existing) — tidak ada assertion eksplisit atas class gabungan ini |
| AC-04-03 | Assert teks/warna warning orderline TERPISAH (`BSL-018`, carry-forward 2x) | — | — | BELUM ADA — sama status dengan AC-03-05, satu keputusan dev menutup keduanya sekaligus (§"Item Menunggu Keputusan Dev") |
| AC-05-01 | `combo_parent_id` styling combo-child AKTIF (`MF-34`, RISIKO TINGGI) | — | — | **BARU, WAJIB** — perlu data setup combo product (`available_in_pos` + `pos.combo`/`combo.line` config) yang belum ada di fixture test manapun saat ini. Tour baru harus: (1) buat combo product test, (2) jual di POS, (3) assert class `border-start border-3 ms-4` muncul pada `<li>` orderline combo-child. Prioritas TINGGI — ini satu-satunya AC dengan behavior baru yang disetujui dev tapi belum diverifikasi visual sama sekali. |
| AC-06-01 | Form Product Template — list_price replace + options currency (`DIFF-04`) | BARU — assert `arch_db` view mengandung `options` baru, ATAU baca view resolved via `fields_view_get`/`get_view` | — | Opsional tambahan visual via AI-interaktif Step 10 (lihat Step 10) |
| AC-06-02 | Form Product Category — anchor `account.view_category_property_form` (`DIFF-02`) | BARU — assert `env.ref('pos_margin_threshold.product_category_form_view_inherit_margin_sale').inherit_id.xml_id == 'account.view_category_property_form'` | — | — |
| AC-06-03 | (informational, popup lama — sudah tidak berlaku, lihat AC-07) | — | — | — |
| AC-07-01 | Kolom margin_sale/minimum_sale_price `optional="show"` di list Product Variants | — | BARU — assert via `get_view()`/arch resolved bahwa field muncul dengan `optional="show"` | Direkomendasikan JUGA tour/AI-interaktif Step 10 untuk verifikasi visual asli (lihat Step 10) |
| AC-07-02 | `lst_price` decoration-danger via `position="attributes"` (bukan replace) | — | BARU — assert node XML record baru (`product_product_tree_view_inherit_margin_sale`) pakai `position="attributes"`, DAN atribut native (`options`, `optional`) pada `lst_price` masih ada di arch resolved (regression guard MF-24/25 tidak terulang di lokasi baru) | — |
| AC-07-03 | Margin negatif merah + kolom Incl. Tax (`MF-38`) | — | BARU — assert `ProductProduct.minimum_sale_price_with_tax` field ada & compute benar (mirror test `test_minimum_sale_price_computation` tapi untuk `ProductProduct` + tax) | Direkomendasikan AI-interaktif Step 10 untuk verifikasi warna (assertion warna sulit murni lewat ORM test) |
| AC-07-04 / AC-09-03 | Kolom tidak dobel saat `sale_margin_threshold` juga terinstall (`MF-37`, RISIKO TINGGI cross-module) | — | BARU — perlu environment dengan KEDUA modul terinstall (lihat `CLAUDE.md` §Adaptasi multi-modul, syarat step 9 lintas-modul); assert `get_view()` list Product Variants hanya punya 1 node `margin_sale`/1 node `minimum_sale_price` | Direkomendasikan JUGA verifikasi visual (sudah pernah dilakukan manual sekali via Docker saat `MF-37` RESOLVED, belum diotomasi) |
| AC-08-01 | `_load_pos_data_fields` menambah 2 field ke payload POS | — | BARU — assert `env['product.product']._load_pos_data_fields(config_id)` mengandung `'minimum_sale_price'`/`'minimum_sale_price_with_tax'` | — |
| AC-08-02 | Getter `get_minimum_sale_price()`/`get_minimum_sale_price_with_tax()` | — | — | Tercakup implisit lewat tour existing (dipakai `isLessMinimumSalePrice`/`minimumSalePriceWithTax` di runtime) — tidak ada unit test JS terpisah, dianggap cukup (getter trivial, 1-baris passthrough) |
| AC-08-03 | `setUnitPrice` dead patch tetap no-op | — | — | Tidak perlu test baru — risiko nol, cukup code-review Step 8 |
| AC-09-01 | Wizard model merge, `sale_margin_threshold` menang `__mro__` | — | `test_cross_module.py::test_wizard_margin_product_model_merged_when_both_installed` (ADA, TAPI **skip kalau `sale_margin_threshold` tidak terinstall** — WAJIB dijalankan di environment kedua modul bersamaan) | — |
| AC-09-02 | `blocking_transaction_order` tidak muncul di view modul ini | — | `test_margin_sale.py::test_blocking_transaction_order_field_has_no_view_in_this_module` (ADA) | — |
| AC-10-01 | Dead file `product_template_views.xml` tidak di manifest | — | BARU (trivial) — assert file tidak ada di `__manifest__.py` `data` list, ATAU cukup code-review Step 8 (tidak wajib test otomatis) | — |
| AC-10-02 | `pos_session.py` tetap kosong-komentar | — | Tidak perlu test — `git diff migration/19.0` kosong (`03_MIGRATION_SPEC.md` §2c), cukup regression-guard code review | — |
| AC-10-03 | `controllers.py` tidak disentuh | — | Tidak perlu test — sama seperti AC-10-02 | — |

---

## Step 10 — QA Testing

> **Prinsip:** kalau AC sudah tercakup tour Step 9, TIDAK diulang manual di sini kecuali untuk
> verifikasi VISUAL murni yang sulit di-assert via tour selector (warna, layout berdampingan) — sesuai
> catatan template §Step 10.

| AC | Deskripsi | Manual | AI-interaktif | AI+tool eksternal (ref script) |
|---|---|---|---|---|
| AC-05-01 | Combo-child styling live (`MF-34`) | Direkomendasikan JUGA manual sekali oleh dev (selain tour Step 9) — style visual (indentasi/border) lebih cepat divalidasi mata manusia daripada lewat selector CSS class doang | — | — |
| AC-06-01/AC-06-02 | Review visual form Product Template/Category (anchor pindah, options currency baru) | — | AI-interaktif (Claude in Chrome) — buka form, screenshot, bandingkan posisi field & currency formatting vs 19.0 | — |
| AC-07-01/02/03 | **Review visual Step 10 kolom Product Variants vs popup 19.0 (SYARAT EKSPLISIT dari keputusan dev `MF-29`)** | Direkomendasikan dev/QA manusia untuk sign-off final (dev secara eksplisit minta perbandingan visual popup-vs-kolom sebagai bagian keputusan desain, bukan cuma smoke functional) | AI-interaktif — buka Docker 19.0 (port 8079) dan 20.0 (port 8078) berdampingan, screenshot list Product Variants, bandingkan kolom Margin/Minimum sale/Incl.Tax dan warna decoration | — |
| AC-07-04 / AC-09-03 | Kolom tidak dobel, kedua modul terinstall | — | AI-interaktif — sudah pernah dilakukan manual sekali (`MF-37` RESOLVED), ulangi setelah kode final Step 6 utk regresi | — |
| AC-03-01/AC-03-05, AC-04-03 | Item `BSL-018` (kalau diputuskan ditutup) | — | AI-interaktif ATAU tunggu Tour Step 9 kalau diputuskan ditulis sebagai tour — **jangan duplikasi di dua tempat**, pilih satu setelah keputusan dev | — |
| Lainnya (AC-01/02/08/09/10) | Regresi backend murni, sudah cukup di Step 9 | Tidak perlu | Tidak perlu | Tidak perlu |

**Tidak ada AC yang butuh AI+tool eksternal (Playwright dkk)** — semua skenario tercakup mekanisme
tour Odoo native (`HttpCase.start_tour`) atau AI-interaktif ad-hoc; tidak ada kebutuhan lintas-sistem/
browser-matrix/load-test untuk modul ini.

---

## Step 11 — UAT

| Kelompok fitur | AC tercakup | UAT |
|---|---|---|
| Margin & minimum sale price computation | AC-01-01..08 | Business user isi/override margin di form produk, verifikasi minimum sale price terhitung benar dan tidak "lompat" saat pindah kategori |
| Bulk-assign margin wizard | AC-02-01..04 | Business user pilih beberapa produk dari list Template/Variant, jalankan wizard, verifikasi margin ter-update sesuai input |
| POS payment enforcement | AC-03-01..05, AC-04-01..03 | Kasir jual produk di bawah minimum, verifikasi dialog konfirmasi/blocking sesuai setting toko (dua skenario: warning-only vs blocking) |
| Combo-child styling (BARU aktif di 20.0) | AC-05-01 | Kasir jual combo product, verifikasi tampilan baris combo-child (indentasi/border) — **beri tahu user ini TAMPILAN BARU dibanding 19.0**, bukan regresi kalau terlihat beda dari yang mereka ingat |
| Product Variants list (pengganti popup) | AC-06-03, AC-07-01..04 | Business user yang biasa pakai popup easy-edit di 19.0 diminta coba alur BARU (kolom di list) — **wajib feedback eksplisit** karena ini perubahan UX yang disetujui, bukan port identik; verifikasi juga saat modul sibling `sale_margin_threshold` aktif bersamaan |
| Cross-module wizard | AC-09-01..02 | Kalau `sale_margin_threshold` juga di-UAT bersamaan, verifikasi wizard tetap berfungsi walau model di-share dua modul |

> Skrip UAT detail (`11_UAT_CHECKLIST.md`) ditulis di Step 11, bukan di sini — tabel ini hanya
> pemetaan cakupan.

---

## Item Menunggu Keputusan Dev (blocker test plan, bukan blocker Step 5 ini)

Dua item berikut ADALAH bagian dari `01b_BASELINE_SPEC.md BSL-018`, sudah di-carry-forward TANPA
keputusan dua kali (project 17.0→18.0, 18.0→19.0). AC-03-05 dan AC-04-03 di `05a` sengaja ditulis
supaya keduanya TIDAK hilang dari radar lagi, tapi test plan ini TIDAK bisa menugaskan "Unit/
Integration/Tour" definitif untuk keduanya sampai ada keputusan:

1. **Ditutup di project 19.0→20.0 ini** → tulis 1 tour baru (skenario "semua line aman, klik Pay,
   assert NOL dialog") + perkuat assertion tour existing (`..._confirm_tour`) untuk assert teks/warna
   warning orderline secara eksplisit (bukan cuma "tidak crash").
2. **Tetap dilewati (carry-forward ketiga kalinya)** → cukup dicatat eksplisit di `06c_IMPLEMENTATION_LOG.md`
   Step 6 dan `FINDINGS.md`, tanpa test baru.

Tidak diputuskan sepihak di dokumen Step 5 ini (di luar wewenang step ini) — direkomendasikan
eskalasi ke dev SEBELUM Step 9 dieksekusi, memakai format `ESCALATION` di `CLAUDE.md` kalau belum ada
jawaban.

---

## Ringkasan

| Step | Role | Tipe | Eksekusi | Jumlah AC |
|---|---|---|---|---|
| 9 | Developer | Unit/Integration/Tour (Owl/JS) | Otomatis/background (semua, termasuk tour) | 37 (28 sudah/segera bisa Unit+Integration tercakup; 5 AC butuh Tour BARU: AC-03-01, AC-03-03, AC-03-05*, AC-04-03*, AC-05-01) |
| 10 | QA | Manual/AI-interaktif/AI+tool eksternal | Campuran, pilih per skenario | 8 baris (fokus review visual AC-05/06/07 sesuai syarat eksplisit `MF-29`/`MF-34`) |
| 11 | PM/FA/User | UAT | Manual (selalu) | 6 kelompok fitur |

`*` = menunggu keputusan dev (`BSL-018`), lihat §"Item Menunggu Keputusan Dev" di atas.
