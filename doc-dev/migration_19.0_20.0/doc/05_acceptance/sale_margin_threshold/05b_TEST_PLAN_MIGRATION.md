# Test Plan (Migrasi) — sale_margin_threshold

**Step:** 5 — Acceptance Criteria & Test Plan (satu paket dengan `05a_MIGRATION_ACCEPTANCE_CRITERIA.md`)
**Ref:** `05_acceptance/sale_margin_threshold/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-09-22

> Modul ini **tidak punya JS/Owl/frontend sama sekali** (`BSL-014`, `01b_BASELINE_SPEC.md` §6:
> "Tidak ada JS/Owl sama sekali... modul ini murni server-side + view XML") — kolom Tour (Owl/JS)
> di tabel Step 9 di bawah karena itu diisi "—" untuk semua AC modul ini. Satu-satunya interaksi
> lintas-modul yang relevan dengan frontend adalah `pos_margin_threshold` (POS, punya JS sendiri),
> yang test-nya hidup di suite `pos_margin_threshold`, bukan di sini — cross-check dedup visual
> (`AC-04-02`) tetap perlu verifikasi kombinasi kedua modul, tapi dari sisi Python/view-arch modul
> ini, bukan Tour JS baru.
>
> **Aset test eksisting yang sudah ada di repo (dipakai, bukan ditulis ulang dari nol):**
> - `sale_margin_threshold/tests/test_action_confirm.py` — 4 method test, dibuat lewat proses
>   `doc-dev-backfill` (17.0), mengacu `doc-dev/backfill/spec/sale_margin_threshold/01B_ACCEPTANCE_CRITERIA.md`
>   dan `doc-dev/backfill/FINDINGS.md` (`F-05` khususnya, jadi baseline eksekusi untuk `MF-08`).
> - `sale_margin_threshold/tests/test_cross_module.py` — 2 method test, interaksi dengan
>   `pos_margin_threshold` (dedup group `MF-03`/`BSL-010`, MRO `wizard.margin.product`/`BSL-015`).
> - Kedua file sudah diaudit isinya (bukan cuma nama method) — semua 6 method PUNYA assertion
>   genuine (bukan stub docstring seperti kasus `totp_enhancement` yang jadi peringatan template
>   ini), jadi tidak perlu audit ulang "9a — Audit Kesiapan Test" secara mendalam untuk file ini.
>   Tetap dijalankan ulang di Step 9 formal untuk konfirmasi PASS di 20.0 (bukan diasumsikan otomatis
>   lolos dari baca kode saja).

---

## Step 9 — Dev Testing

> Eksekusi: **otomatis/background** — `odoo-bin -i sale_margin_threshold --test-enable --test-tags
> /sale_margin_threshold --stop-after-init` (tambahkan `,/pos_margin_threshold` pada tag kalau
> menjalankan bareng untuk `AC-04-02`/`AC-05-*` — lihat catatan cross-module di bawah tabel). Murah
> diulang, tempat siklus test→fix→test terjadi.

| AC | Deskripsi | Unit | Integration | Tour (Owl/JS) |
|---|---|---|---|---|
| AC-01-01 | Kategori→template margin_sale inheritance | Baru — tambah assert `template.margin_sale` setelah create dari kategori | — | — |
| AC-01-02 | minimum_sale_price = standard_price*(1+margin/100) | ✅ Sudah ada (implisit, `test_action_confirm_blocking_below_minimum`) | — | — |
| AC-01-03 | Inverse minimum_sale_price → margin_sale | Baru — belum ada test eksplisit untuk arah inverse ini | — | — |
| AC-01-04 | margin_sale per-variant shared ke template (F-01) | Baru — port konsep dari `doc-dev/backfill/test/sale_margin_threshold` kalau ada, cross-check dulu | — | — |
| AC-01-05 | minimum_sale_price_with_tax compute | Baru — field ditambahkan sesi migrasi ini (`MF-38`), belum ada test compute-nya | — | — |
| AC-01-06 | is_less_minimum_sale stale-cache (MF-21, preserved) | Baru — assert TIDAK auto-update tanpa reload eksplisit (bukti bug tetap ada) | — | — |
| AC-02-01 | Rental order skip validasi total | — | Baru — butuh `sale_renting` (Enterprise) terinstall di test DB | — |
| AC-02-02 | check_product_price kosong → confirm langsung | ✅ Sudah ada (`test_action_confirm_normal_no_price_issue`) | — | — |
| AC-02-03 | Blocking=True → ValidationError | ✅ Sudah ada (`test_action_confirm_blocking_below_minimum`) | — | — |
| AC-02-04 | Blocking=False → wizard, order tetap draft | ✅ Sudah ada (`test_action_confirm_wizard_path_when_not_blocking`) | — | — |
| AC-02-05 | skip_check_price bypass, no re-check | Baru — assert tidak infinite-loop/tidak re-raise saat context di-set manual | — | — |
| AC-02-06 | Wizard confirm → state=sale; Cancel → no-op | ✅ Sudah ada (jalur confirm, sama test `AC-02-04`); Cancel — **Baru** | — | — |
| AC-02-07 | Bilingual EN/FR message content | Baru — assert isi string `message`/`message_Fr` sesuai `detect_user_language()`, minimal 2 kasus (`fr_FR`, `en_US`) | — | — |
| AC-02-08 | decoration-danger + column_invisible di form Sale Order | — | Baru — cek arch view via `get_view()`/`fields_view_get`, atau serahkan ke Step 10 visual (lihat catatan) | — |
| AC-03-01 | Batch-confirm crash (MF-08, HIGH-RISK) | ✅ Sudah ada (`test_action_confirm_BATCH_MULTI_ORDER_F05`) | — | — |
| AC-03-02 | Singleton bug kedua (MF-26) | — | Kondisional — hanya kalau Step 9 menemukan skenario trigger konkret (lihat `05a` AC-03-02) | — |
| AC-03-03 | groups.xml implied_ids salah tipe (MF-20, preserved) | Baru — assert `implied_ids` masih berisi `ir.module.category` id (bukti bug tetap ada) | — | — |
| AC-04-01 | Kolom list Product Variants muncul, optional=show, editable (MF-29, HIGH-RISK) | — | Baru — `get_view()` arch check (field ada, `optional="show"`) | — (visual editing → Step 10) |
| AC-04-02 | Dedup kolom saat kedua modul terinstall (MF-37, HIGH-RISK) | — | Baru — `get_view()` dengan `pos_margin_threshold` terinstall, assert HANYA 1 set field muncul di arch hasil `_get_view()` | — |
| AC-04-03 | Decoration merah margin negatif + kolom Incl.Tax (MF-38, HIGH-RISK) | Baru — assert compute value benar (paritas dengan AC-01-05); visual decoration → Step 10 | Baru — arch check `decoration-danger` attribute ada | — |
| AC-04-04 | Decoration lst_price di list baru + stale-cache MF-21 | — | Baru — kombinasikan dengan AC-01-06, edit-lalu-baca-cepat | — |
| AC-04-05 | Persistensi data via multi_edit inline | — | Baru — simulasikan write lewat `write()` batch (proxy untuk multi_edit UI), assert tersimpan benar | — (UI multi_edit asli → Step 10) |
| AC-05-01 | wizard.margin.product MRO, sale_margin_threshold menang | ✅ Sudah ada (`test_wizard_margin_product_model_merged_when_both_installed`) | — | — |
| AC-05-02 | _register_hook dedup group (dua arah) | ✅ Sudah ada arah "kedua terinstall" (`test_group_sale_margin_action_emptied_when_pos_margin_installed`); arah "hanya modul ini" — **Baru** | — | — |
| AC-06-01 | blocking_transaction_order config→param | Baru — assert `ir.config_parameter` value tercermin ke behavior `action_confirm()` (proxy, sudah implisit via AC-02-03/04) | — | — |
| AC-07-01 | XML-ID collision, record pertama inert (BSL-013) | — | Baru (opsional/rendah prioritas) — assert `product_template_inherit_sale_margin_threshold` resolve ke `products.xml` punya (inherit_id form aktif) | — |
| AC-07-02 | static assets glob kosong (BSL-014) | — | Tidak perlu test otomatis — verifikasi manual `ls static/src/` sudah cukup (dicatat di baseline) | — |
| AC-07-03 | depends_context('uid') inefisiensi (BSL-016) | — | Tidak perlu test otomatis — nit, tidak berdampak fungsional | — |
| AC-07-04 | position=replace di form lama, options hilang (MF-27, preserved) | — | Baru (opsional) — assert `options` TIDAK ada di arch `lst_price` form `product_template_form_view` (bukti bug tetap ada); kontras eksplisit dengan AC-04-01 yang HARUS punya `options` | — |

**Catatan cross-module (AC-04-02, AC-05-*):** DB test yang sama harus punya KEDUA
`pos_margin_threshold` dan `sale_margin_threshold` ter-install untuk assertion "hanya 1 set kolom
tampil"/"MRO menang" bermakna — jalankan test-tag gabungan
(`--test-tags /pos_margin_threshold,/sale_margin_threshold`) minimal sekali, di LUAR run per-modul
biasa, konsisten pola yang sudah dipakai `test_cross_module.py` (`skipTest` kalau modul sibling tidak
terinstall).

**Catatan arch-check (AC-02-08, AC-04-01/02/03/04, AC-07-01/04):** modul ini tidak punya Tour/HttpCase
existing untuk verifikasi visual — arch check via `env['product.product'].get_view(view_type='list')`
(atau `fields_view_get` tergantung API final 20.0, cek `odoo20/odoo/addons/base/models/ir_ui_view.py`
saat implementasi test) memverifikasi STRUKTUR view (field ada/tidak ada, atribut benar), TAPI TIDAK
memverifikasi rendering visual sungguhan (warna merah beneran tampil, dst) — itu tetap domain Step
10 (lihat di bawah). Jangan anggap arch-check lolos = visual parity `MF-38` terverifikasi penuh.

---

## Step 10 — QA Testing

> Eksekusi: pilih satu mode per AC/skenario. AC yang murni Python/logic (AC-01 s.d. AC-03, AC-05,
> AC-06, sebagian besar AC-07) SELESAI di Step 9 lewat unit/integration test — Step 10 untuk modul
> ini FOKUS ke AC yang punya komponen VISUAL/UI nyata (AC-02-08, seluruh AC-04) yang tidak bisa
> divalidasi penuh dari arch-check saja.

| AC | Deskripsi | Manual | AI-interaktif | AI+tool eksternal (ref script) |
|---|---|---|---|---|
| AC-02-08 | decoration-danger merah pada order line di bawah minimum (form Sale Order), skip untuk rental | — | ✅ AI-interaktif (browser) — buat SO dengan line di bawah minimum, screenshot baris merah; ulangi dengan rental order, screenshot TIDAK merah | — |
| AC-04-01 | Kolom margin_sale/minimum_sale_price di list Product Variants, editable inline | Sudah ada bukti historis (review visual Docker 19.0 vs 20.0, 2026-09-22, dicatat `MF-29`/CLAUDE.md "Status saat ini") — **direkomendasikan RE-VERIFIKASI formal Step 10** (bukan cuma warisi bukti informal sesi implementasi dini) | ✅ AI-interaktif (browser) — buka list, edit inline, screenshot | — |
| AC-04-02 | Dedup — hanya 1 set kolom saat kedua modul terinstall | Sudah ada bukti historis (`MF-37`, "1 set kolom, bukan 2", diverifikasi Docker) — **re-verifikasi formal Step 10 direkomendasikan** | ✅ AI-interaktif — install kedua modul, buka list, screenshot; bandingkan dengan hanya 1 modul terinstall | — |
| AC-04-03 | Decoration merah margin negatif + kolom Incl. Tax | Sudah ada bukti historis (`MF-38`, "margin negatif tampil merah, kolom Incl. Tax terisi benar") — **re-verifikasi formal Step 10 direkomendasikan** | ✅ AI-interaktif — set margin negatif, screenshot warna; cek nilai kolom Incl. Tax vs hitungan manual | — |
| AC-04-04 | Decoration lst_price + stale-cache MF-21 di list baru | — | ✅ AI-interaktif — edit lst_price satu variant lalu SEGERA (tanpa reload) cek variant lain di list yang sama, screenshot state stale kalau muncul | — |
| AC-04-05 | Persistensi data via multi_edit inline | — | ✅ AI-interaktif — multi-select 2+ variant, edit margin_sale bareng, screenshot hasil tersimpan | — |
| Perbandingan visual popup 19.0 vs list 20.0 (rekomendasi `MF-29`) | Side-by-side popup lama (Docker 19.0, port 8079) vs kolom list baru (Docker 20.0, port 8078) | ✅ Manual (dev/QA) — dua screenshot berdampingan, bukan otomatis | ✅ AI-interaktif bisa bantu ambil kedua screenshot | — |

**Catatan:** ketiga baris AC-04 sudah punya bukti verifikasi visual INFORMAL dari sesi implementasi
dini (di luar urutan Step normal, dicatat `CLAUDE.md` §"Review visual Docker 19.0 vs 20.0" dan
`FINDINGS.md` `MF-37`/`MF-38`) — tabel ini tetap mencantumkannya sebagai baris Step 10 FORMAL karena
bukti sesi implementasi bukan pengganti QA gate resmi (dijalankan dev implementasi sendiri, bukan
role QA terpisah, dan belum melalui checklist `10_BUSINESS_FLOW_MIGRATION.md` terstruktur).

---

## Step 11 — UAT

> Tool cuma generate skrip test-nya (`11_UAT_CHECKLIST.md`) — TIDAK PERNAH mengeksekusi atau mengisi
> Actual/Status/Sign-off. Selalu manual, business user asli.

| Kelompok fitur | AC tercakup | UAT |
|---|---|---|
| Kalkulasi margin & minimum sale price | AC-01-01..06 | Business user set margin di kategori/produk, verifikasi harga minimum terhitung benar (termasuk kolom Incl. Tax) |
| Konfirmasi Sale Order — validasi margin | AC-02-01..08 | Business user coba confirm SO dengan harga di bawah minimum (mode blocking DAN mode wizard), coba juga dengan rental order |
| Bug warisan (harus tetap ada, bukan regresi baru) | AC-03-01..03 | Business user coba batch-confirm >1 quotation dari list view — WAJIB gagal dengan error (bukan silent), konfirmasi ini "expected" bukan bug baru |
| Kolom Product Variants (pengganti popup) | AC-04-01..05 | Business user yang biasa pakai popup lama di 19.0 diminta bandingkan langsung workflow baru (kolom list) — feedback UX eksplisit, bukan cuma cek fungsional |
| Wizard bulk-assign margin | AC-05-01..02 | Business user jalankan bulk-assign margin ke banyak produk sekaligus |
| Config settings | AC-06-01 | Business user toggle "Blocking Transaction Order" di Settings, verifikasi efeknya konsisten |

---

## Ringkasan

| Step | Role | Tipe | Eksekusi | Jumlah AC |
|---|---|---|---|---|
| 9 | Developer | Unit/Integration (tidak ada Tour — modul tanpa JS/Owl) | Otomatis/background | 29 AC — 6 sudah punya test eksisting (AC-01-02, AC-02-02/03/04/06-jalur-confirm, AC-03-01, AC-05-01/02-arah1), 1 kondisional (AC-03-02), 2 sengaja tanpa test otomatis (AC-07-02/03, nit non-fungsional), sisanya (~20) perlu test baru |
| 10 | QA | AI-interaktif (dominan) + Manual (perbandingan popup vs list) | Campuran, fokus AC dengan komponen visual | 6 baris (AC-02-08, AC-04-01..05) — 3 di antaranya (AC-04-01/02/03) sudah punya bukti informal dari sesi implementasi, tetap wajib re-verifikasi formal |
| 11 | PM/FA/User | UAT | Manual (selalu) | 6 kelompok fitur mencakup seluruh 29 AC |
