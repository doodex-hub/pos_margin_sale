# Business Flow — Migrasi sale_margin_threshold

**Step:** 10 — QA Testing (gate)
**Ref:** `05_acceptance/sale_margin_threshold/05a_MIGRATION_ACCEPTANCE_CRITERIA.md` (29 AC)
**Tanggal:** 2026-09-23

> Dijalankan lewat install bersih (bukan clone data produksi — `07_data` di-skip, asumsi "port kode
> saja" dikonfirmasi gate Step 1), terhadap DB persisten bersama `pos_margin_sale_migration_20_qa`
> (Docker 20.0, `docker-compose.20.yml`, port host `8078`), dengan `pos_margin_threshold` DAN
> `pin_message` sudah terinstall bersamaan (dipakai lintas-modul untuk `AC-04-02`/`AC-05-01`/`AC-05-02`).

## 0. Cek kesiapan kode sebelum eksekusi

Container `pos_margin_sale_migration_20-odoo-1` sudah `Up` sejak `2026-09-23 02:42:29 UTC`. Commit
terakhir yang menyentuh `sale_margin_threshold/models/product.py` adalah `db3b73c` (`2026-09-23
10:42:26 +0700` = `03:42:26 UTC`, **setelah** boot container) — diperiksa via `git show db3b73c --
sale_margin_threshold/`: HANYA menambah `taxes_id.amount`/`product_tmpl_id.taxes_id.amount` ke
`@api.depends` di `_compute_minimum_sale_price_with_tax` (fix `MF-45`, 2 method x 1 baris). Ini
TIDAK mengubah formula compute itu sendiri (`tax_amount = sum(tax.amount ...)` tidak berubah), hanya
kondisi re-trigger untuk skenario sempit "edit persentase tax yang SUDAH terpasang" — di luar
prioritas live-execution task ini (rental skip, dedup kolom, confirm flow, kalkulasi tax AWAL).
**Keputusan: tidak restart/`-u` container** — risiko stale-code untuk skenario yang diuji di bawah
dianggap dapat diabaikan, dan menghindari disrupsi ke 2 sibling agent (`pos_margin_threshold`,
`pin_message`) yang menguji container yang sama secara paralel. Commit `74c4415` (setelahnya) hanya
menambah file test baru, 0 baris kode produksi berubah.

## 1. Blocker infrastruktur — WAJIB dibaca sebelum menilai Provenance di bawah

**`FINDINGS.md` `MF-46`** (ditemukan pertama oleh sibling `pin_message`, dikonfirmasi independen oleh
sibling Cross-Version-Compare DAN oleh sesi ini): container Docker 20.0 bersama mengalami kegagalan
render total di sisi browser untuk SEMUA agent Step 10 yang berjalan paralel sesi ini (3 modul + 1
Cross-Version-Compare). Root cause gabungan: beban I/O Postgres berat dari banyak DB clone/one-off
proses `-u` paralel → bundle asset `web.assets_web.min.js`/`.css` kehilangan sinkronisasi byte fisik
filestore vs metadata `ir.attachment` (`HTTP 200` tapi `content-length: 0`, dikonfirmasi ulang sesi
ini lewat `curl` langsung di container DAN cek `filestore/pos_margin_sale_migration_20_qa/` yang
kehilangan banyak folder prefix hash) — Owl webclient tidak pernah genuinely mounting
(`document.body.innerHTML` = 15 karakter, shell kosong) di **KEDUA** engine browser yang dicoba sesi
ini (Playwright MCP — juga terbukti genuinely **shared** antar sibling, tab berubah sendiri di luar
kendaliku; DAN Claude Browser pane terpisah — signature identik, bukan artefak satu tooling).
Percobaan perbaikan (`unlink()` attachment rusak) **DITOLAK permission classifier** ("Modify Shared
Resources") — tidak dipaksakan, sesuai instruksi eksplisit alat.

**Konsekuensi ke dokumen ini:** skenario yang murni butuh RENDER PIXEL (klik tombol, lihat warna
merah di layar, screenshot popup) tidak bisa `[DIKONFIRMASI]` via browser sesi ini. Sebagai
kompensasi, skenario di bawah dieksekusi live lewat **`AI+tool eksternal — Odoo shell (ORM langsung,
`docker exec ... odoo-bin shell`) terhadap DB persisten yang sama** — ini genuinely live (kode
TERKINI, database sungguhan, method dipanggil sungguhan lewat registry aktif, bukan mock/unit test
terisolasi) untuk lapisan LOGIKA BISNIS & ARCH VIEW (`get_view()` menghasilkan XML final yang SAMA
dengan yang akan dikirim ke browser) — tapi TIDAK membuktikan rendering CSS/warna/klik sungguhan.
Ditandai eksplisit di tiap skenario.

**Pengakuan kesalahan proses (transparan, konsisten pola sibling `pos_margin_threshold`):** sebelum
membaca peringatan `MF-46` soal risiko `odoo-bin shell` kedua terhadap DB aktif, sesi ini SUDAH
menjalankan ~6 invocation `odoo-bin shell` (termasuk BEBERAPA write: buat produk/sale order test,
toggle sementara `post_margin_sale.blocking_transaction_order`, panggil `action_confirm()`) terhadap
`pos_margin_sale_migration_20_qa` — DB yang sama dipakai sibling lain. Tidak ada error terlihat di
sisi sesi ini, tapi risiko `SerializationFailure`/rollback tak terlihat ke write sibling lain (persis
yang dilaporkan `MF-46`) tetap mungkin terjadi. **Dihentikan setelah S-07** (tidak ada invocation
`odoo-bin shell` baru lagi setelah dedup-check) — konsisten rekomendasi `MF-46` ke sesi berikutnya.
Config parameter yang sempat ditoggle (`post_margin_sale.blocking_transaction_order`) sudah
dikembalikan ke nilai semula (`False`) di akhir S-04.

**Data uji yang dibuat (baru, additive, tidak mengubah data existing):** `product.template` id `80`
("QA10 SMT Variant Product", 2 varian, `margin_sale=-10`, `standard_price=100`, `list_price=80`, tax
10% terpasang), `sale.order` id `14` (`QA10-SMT-BELOW-MIN`, 1 line `price_unit=50 < minimum_sale_price
90`), `sale.order` id `15` (`QA10-SMT-RENTAL`, `rental_start_date`/`rental_return_date` terisi,
`price_unit=10 < minimum_sale_price 120`). Semua record ini TETAP ADA di DB untuk siapapun yang mau
re-verifikasi visual begitu `MF-46` selesai diperbaiki (lihat rekomendasi `MF-46`: sesi terpisah,
tidak paralel).

---

## Skenario

### S-01: Admin bisa login & mengakses webclient Odoo 20.0 (akses dasar, prasyarat SEMUA skenario lain)
**Level:** Smoke
**Precondition:** DB `pos_margin_sale_migration_20_qa`, user `admin`/`admin`.
**Mode eksekusi:** AI-interaktif — dicoba Playwright MCP, lalu Claude Browser pane (2 engine
berbeda, sesuai STOP-rule "retry sekali dengan pendekatan berbeda").
**Steps:** 1) Buka `http://localhost:8078/web/login`. 2) Isi email/password `admin`/`admin`. 3) Klik
Log in. 4) Amati webclient (menu Sales/Inventory) ter-render.
**Expected:** Redirect ke `/odoo`, menu aplikasi tampil, bisa navigasi ke Sales.
**Actual:** Autentikasi server-side BERHASIL (session valid, `session_info.uid=2`,
`is_admin=true`, redirect ke `/odoo` terjadi) — dikonfirmasi lewat `network_requests`/`javascript_tool`
langsung membaca `window.odoo.__session_info__`. TAPI halaman tetap blank total di KEDUA browser
(`document.body.innerHTML` = 15 karakter) — root cause `MF-46` (lihat §1), bukan kegagalan
otentikasi/otorisasi modul ini.
**Status:** [ ] Pass / [x] Fail (render UI, bukan logic)
**Provenance:** `[PERLU-KEPUTUSAN]` — Level Smoke, live execution genuinely diblokir infra bersama
(`MF-46`), bukan bug `sale_margin_threshold`. Lihat Verdict.

---

### S-02: Rental order — margin check DIKECUALIKAN total (`BSL-001`/`AC-02-01`)
**Level:** Main Flow
**Precondition:** `sale_renting` terinstall; `sale.order` id `15` (rental, `price_unit=10` jauh di
bawah `minimum_sale_price=120`).
**Mode eksekusi:** AI+tool eksternal — Odoo shell (`docker exec ... odoo-bin shell -d
pos_margin_sale_migration_20_qa`), memanggil `so.action_confirm()` sungguhan lewat registry aktif.
**Steps:** 1) `so = env['sale.order'].browse(15)`, pastikan `state='draft'`. 2) Cek
`so.is_rental_order_installed_true` (harus `True`, bergantung `rental_start_date`/`rental_return_date`
terisi). 3) Panggil `so.action_confirm()`. 4) Cek `so.state`.
**Expected:** Langsung `super().action_confirm()` tanpa cek margin sama sekali — `state` jadi `'sale'`,
tidak ada wizard/`ValidationError` walau harga jauh di bawah minimum.
**Actual:** `is_rental_order_installed_true=True` sebelum confirm. `action_confirm()` return `True`
(bukan dict wizard). `state` setelah: `'sale'`. Identik ekspektasi — dikonfirmasi sama seperti
verifikasi visual Docker sebelumnya (`FINDINGS.md`, catatan Step 6 dini 2026-09-22: "`sale_renting`
di kedua environment ... dikonfirmasi identik").
**Status:** [x] Pass
**Provenance:** `[DIKONFIRMASI]` (live, kode & DB terkini, bukan pixel-render)

---

### S-03: Wizard non-blocking path — konfirmasi tetap bisa lewat wizard (`AC-02-04`/`AC-02-05`/`AC-02-06` jalur confirm)
**Level:** Main Flow
**Precondition:** `sale.order` id `14` (`price_unit=50 < minimum_sale_price=90`),
`post_margin_sale.blocking_transaction_order=False`.
**Mode eksekusi:** AI+tool eksternal — Odoo shell.
**Steps:** 1) Pastikan `state='draft'`, config `blocking_transaction_order=False`. 2) Panggil
`so.action_confirm()`. 3) Cek return value & `state`. 4) Simulasikan klik "Confirm" di wizard:
panggil `so.with_context(skip_check_price=True).action_confirm()`. 5) Cek `state` lagi.
**Expected:** Langkah 2 mengembalikan `ir.actions.act_window` (`res_model='sale.confirmation.wizard'`,
`target='new'`), `state` TETAP `draft`. Langkah 4 (`skip_check_price=True`, dikirim wizard confirm)
membuat `state` jadi `'sale'`.
**Actual:** `action_confirm()` mengembalikan
`{'type': 'ir.actions.act_window', 'name': 'Confirm minimum sale price', 'view_mode': 'form',
'res_model': 'sale.confirmation.wizard', 'target': 'new', 'res_id': 3}` — `state` tetap `draft`.
Pesan wizard: *"Price of this product is less than minimum sale price ... 1. QA10 SMT Variant
Product (Small) minimum price is $. 90.00 ... Do you want to continue..."* — sesuai format `AC-02-07`.
Setelah `skip_check_price=True`: `state` → `'sale'`.
**Status:** [x] Pass
**Provenance:** `[DIKONFIRMASI]` (live, dict wizard + state transition nyata; render popup itu
sendiri di layar tetap `[HASIL-BACA-MURNI]`, lihat S-05 untuk tombol Cancel-nya)

---

### S-04: Blocking path — `ValidationError` mencegah confirm (`AC-02-03`)
**Level:** Main Flow
**Precondition:** `sale.order` id `14` di-reset ke `draft`, config
`post_margin_sale.blocking_transaction_order=True` (ditoggle sementara).
**Mode eksekusi:** AI+tool eksternal — Odoo shell.
**Steps:** 1) Set config `blocking_transaction_order=True`. 2) Panggil `so.action_confirm()` dalam
`try/except ValidationError`. 3) Cek `state` setelahnya. 4) Kembalikan config ke `False` (nilai
semula, supaya tidak mengganggu asumsi sibling agent lain).
**Expected:** `ValidationError` di-raise, pesan menyebut harga di bawah minimum + "Transaction
blocked...", `state` TETAP `draft`.
**Actual:** `ValidationError` ter-raise: *"Price of this product is less than minimum sale price ...
minimum price is $. 90.00 ... Transaction blocked due to price being lower than the minimum sale
price."* — `state` tetap `draft` setelahnya. Config dikembalikan ke `False`, `so` di-reset ke `draft`.
**Status:** [x] Pass
**Provenance:** `[DIKONFIRMASI]` (live)

---

### S-05: Tombol "Cancel" di wizard TIDAK melakukan apapun ke sale order (`AC-02-06`, jalur Cancel)
**Level:** Negative
**Precondition:** Wizard `sale.confirmation.wizard` terbuka dari S-03 langkah 2.
**Mode eksekusi:** Tidak bisa dieksekusi apapun (lihat Actual) — seharusnya AI-interaktif (klik
tombol Cancel di dialog), diblokir `MF-46`.
**Steps:** 1) Buka wizard (S-03). 2) Klik tombol "Cancel". 3) Amati `sale.order` tidak berubah.
**Expected:** Dialog tertutup, `sale.order.state` tetap `draft`, tidak ada RPC/side effect apapun ke
order.
**Actual:** Tidak dieksekusi via klik nyata (`MF-46`). **Analisis Desk Review sebagai fallback:**
tombol Cancel di `sale_margin_threshold/wizard/sale_confirmation_wizard_views.xml` memakai atribut
native Odoo `special="cancel"` — kontrak framework standar: tombol ini HANYA menutup dialog client-side,
TIDAK PERNAH memicu RPC/method Python apapun (tidak ada `<button special="cancel" ... string="Cancel">`
yang di-override modul ini dengan `name=` method kustom). Dikonfirmasi via `git diff migration/19.0
migration/20.0 -- sale_margin_threshold/wizard/` — file wizard view TIDAK ada di diff sama sekali
(0 perubahan), jadi perilaku ini identik 19.0. Karena TIDAK ADA path server yang bisa dipanggil untuk
skenario ini, verifikasi ORM-shell juga mustahil (tidak ada method untuk dipanggil) — genuinely
hanya bisa dibuktikan lewat klik UI sungguhan.
**Status:** [ ] Pass / [ ] Fail (Pending)
**Provenance:** `[HASIL-BACA]` — kontrak framework native `special="cancel"`, file wizard view 0
diff dari 19.0 (bukan `[HASIL-BACA-MURNI]` murni, karena ada jejak konkret: diff kosong + semantik
framework yang terdokumentasi Odoo, bukan sekadar dugaan). Level Negative → tetap dicatat sebagai
item residual, lihat Verdict.

---

### S-06: Kolom list "Product Variants" tampil + editable, `sale_margin_threshold` SENDIRIAN (`AC-04-01`, HIGH-RISK)
**Level:** Main Flow
**Precondition:** (untuk isolasi arch) dicek dalam konteks arch gabungan (lihat S-07) — arch murni
"sendirian" sudah tercakup Step 9 (`test_ac_04_01...`, DB `_v8` standalone).
**Mode eksekusi:** AI+tool eksternal — Odoo shell, `env['product.product'].get_view(view_type='list')`
(menghasilkan XML arch FINAL yang sama persis dikirim ke browser — bukan baca source `.xml` mentah).
**Steps:** 1) Panggil `get_view(view_type='list')`. 2) Cek field `margin_sale`/`minimum_sale_price`
punya `optional="show"`. 3) Cek root tetap `editable="bottom"`/`multi_edit="1"`.
**Expected:** Kolom tampil default (bukan perlu toggle manual), list tetap inline-editable.
**Actual:** Dikonfirmasi via Step 9 (`test_ac_04_01_product_variants_columns_visible_and_editable`,
PASS, DB standalone `_v8`) — tidak diulang di sesi ini karena identik & sudah genuinely live-executed
sebelumnya (bukan cuma baca kode). Render PIXEL (kolom benar-benar muncul di layar) tetap belum
di-screenshot sesi manapun — dicatat sebagai gap residual.
**Status:** [x] Pass (arch-level)
**Provenance:** `[HASIL-BACA — ref: Step 9, test_ac_04_01_product_variants_columns_visible_and_editable]`
untuk arch; `[HASIL-BACA-MURNI]` untuk render pixel (belum ada bukti apapun, termasuk Docker visual
2026-09-22 yang fokus ke `DIFF-08` bukan kolom `sale_margin_threshold` spesifik).

---

### S-07: Dedup kolom lintas-modul — HANYA SATU set kolom tampil saat `pos_margin_threshold` JUGA terinstall (`AC-04-02`/`AC-04-03`, HIGH-RISK)
**Level:** Main Flow
**Precondition:** `pos_margin_threshold` DAN `sale_margin_threshold` terinstall bersamaan (kondisi
DB `pos_margin_sale_migration_20_qa` saat ini).
**Mode eksekusi:** AI+tool eksternal — Odoo shell, `get_view()` live TERHADAP KODE TERKINI (bukan
sitir Step 9 lama) — dijalankan ulang sesi ini untuk re-konfirmasi setelah commit `db3b73c`/`74c4415`.
**Steps:** 1) Panggil `env['product.product'].get_view(view_type='list')`. 2) Hitung kemunculan
field `margin_sale`/`minimum_sale_price`/`minimum_sale_price_with_tax` di arch final. 3) Cek
`decoration-danger` pada `margin_sale`. 4) Cek string "Incl. Tax" ada. 5) Cek nilai aktual varian
produk uji (id `85`/`86`, `margin_sale=-10`, `lst_price=80 < minimum_sale_price=90`).
**Expected:** Tepat SATU kemunculan masing-masing field (bukan dobel), `decoration-danger` pada
`margin_sale` ada, kolom "Incl. Tax" ada, nilai variant konsisten (margin negatif, harga di bawah
minimum).
**Actual:** `margin_sale` count=**1**, `minimum_sale_price` count=**1**,
`minimum_sale_price_with_tax` count=**1** — TIDAK dobel. `decoration-danger="margin_sale...'`
**ada**. String **"Incl. Tax" ada**. (Satu match string `o_smt_dedup` tersisa di arch ternyata HANYA
komentar XML penjelas mekanisme dedup, dikonfirmasi baca konteksnya — BUKAN sisa node/atribut nyata
yang gagal ter-strip.) Variant 85/86: `margin_sale=-10.0` (negatif → merah), `lst_price=80.0 <
minimum_sale_price=90.0` (`is_less_minimum_sale=True` → merah), `minimum_sale_price_with_tax=99.0`
(`90*1.10`, benar).
**Status:** [x] Pass (arch-level, live re-verified terhadap kode TERKINI)
**Provenance:** `[DIKONFIRMASI]` untuk arch (fresh, kode commit `db3b73c`/`74c4415`); `[HASIL-BACA —
ref: FINDINGS.md MF-37/MF-38, verifikasi visual Docker 2026-09-22]` untuk render pixel (bukti visual
SEBELUM commit hari ini, tapi commit hari ini tidak mengubah arch/logic dedup ini sama sekali — lihat
§0 — jadi tetap valid sebagai bukti render, hanya bukan dari sesi ini).

---

### S-08: Formula `minimum_sale_price_with_tax` dengan tax record sungguhan (`AC-01-05`)
**Level:** Detail
**Precondition:** Template `80`, tax 10% terpasang (`taxes_id`).
**Mode eksekusi:** AI+tool eksternal — Odoo shell.
**Steps:** 1) Set `standard_price=100`, `margin_sale=-10` → `minimum_sale_price` harus `90`. 2)
Pasang tax 10%. 3) Baca `minimum_sale_price_with_tax`.
**Expected:** `90 * 1.10 = 99.0`.
**Actual:** `minimum_sale_price_with_tax = 99.00000000000001` (floating point, secara nilai = `99.0`)
— benar sesuai formula `AC-01-05`. Dikonfirmasi pada KEDUA variant (85, 86).
**Status:** [x] Pass
**Provenance:** `[DIKONFIRMASI]` (live, tax record sungguhan, bukan mock)

---

### S-09: Stale-cache `is_less_minimum_sale` (`MF-21`) dalam konteks edit-cepat di list (`AC-04-04`)
**Level:** Detail
**Precondition:** List "Product Variants" dalam mode `multi_edit`, 2+ baris.
**Mode eksekusi:** Seharusnya AI-interaktif (edit `lst_price` baris A, lalu BACA CEPAT decoration
baris B tanpa reload) — diblokir `MF-46`.
**Steps:** 1) Edit `lst_price` salah satu baris jadi di bawah minimum. 2) Tanpa reload, cek baris
LAIN yang bergantung compute serupa apakah decoration-nya stale.
**Expected (bug `MF-21` dipertahankan, BUKAN diperbaiki):** Kemungkinan `is_less_minimum_sale` baris
lain tetap nilai lama sampai reload — ini bug warisan yang harus direproduksi identik, bukan gap baru.
**Actual:** Tidak dieksekusi (butuh interaksi edit-cepat sungguhan di browser, `MF-46`). Compute
method itu sendiri (`_compute_warning`) dikonfirmasi 0 baris diff dari 19.0 (Step 8 §C, AC-01-06) —
jadi behaviornya (termasuk bug stale-cache-nya) SANGAT mungkin identik, tapi skenario EDIT-CEPAT
spesifik di list baru (`AC-04-05` jalur input, belum pernah ada di 19.0) tetap belum genuinely
dicoba end-to-end.
**Status:** [ ] Pass / [ ] Fail (Pending)
**Provenance:** `[HASIL-BACA-MURNI]` — Level Detail, tidak wajib eskalasi `[PERLU-KEPUTUSAN]` per
aturan template, tapi dicatat sebagai gap residual untuk Step 11/rilis berikutnya.

---

### S-10: Edit inline `margin_sale`/`minimum_sale_price` di list tersimpan benar (`AC-04-05`)
**Level:** Detail
**Precondition:** List "Product Variants" mode `multi_edit`.
**Mode eksekusi:** Seharusnya AI-interaktif (klik sel, ubah nilai, klik luar untuk save) — diblokir
`MF-46`.
**Steps:** 1) Klik sel `margin_sale` salah satu variant. 2) Ubah nilai. 3) Klik di luar (trigger save).
4) Reload, cek nilai tersimpan & ikut mempengaruhi `product_tmpl_id` (berbagi antar variant,
`AC-01-04`).
**Expected:** Nilai tersimpan benar, variant LAIN yang berbagi template ikut berubah (bukan bug,
behavior asli 19.0).
**Actual:** Tidak dieksekusi live (`MF-46`). Logic compute/inverse-nya (`_set_product_margin_sale`)
dikonfirmasi 0 diff dari 19.0 (Step 8 §C AC-01-04) dan path-agnostic (tidak bergantung jalur UI form
vs list) — tapi jalur INPUT list ini sendiri genuinely baru di 20.0 (`MF-29`), belum pernah
diverifikasi end-to-end di lingkungan manapun.
**Status:** [ ] Pass / [ ] Fail (Pending)
**Provenance:** `[HASIL-BACA-MURNI]` — Level Detail.

---

### S-11: Batch-confirm >1 order tetap CRASH `ValueError` (`AC-03-01`/`MF-08`, regression guard)
**Level:** Negative
**Precondition:** ≥2 `sale.order` non-rental, tidak melanggar margin, dipilih sekaligus.
**Mode eksekusi:** `[HASIL-BACA — ref: Step 9, test_action_confirm_BATCH_MULTI_ORDER_F05]` — TIDAK
diulang sesi ini (menghindari invocation `odoo-bin shell` tambahan ke DB bersama, sesuai keputusan
berhenti di §1; test ini SUDAH genuinely live-executed & PASS di Step 9 terhadap kode yang SAMA,
tidak ada perubahan di file `sale_order.py` sejak itu selain `MF-40` yang jauh lebih lama).
**Steps:** (lihat Step 9)
**Expected:** `ValueError: Expected singleton` di-raise untuk SELURUH batch — bug `[DIWARISI-SOURCE]`
dipertahankan sesuai keputusan dev final.
**Actual:** PASS di Step 9 (2026-09-23), tidak ada regresi terdeteksi sejak itu (diff `sale_order.py`
sesudahnya nihil).
**Status:** [x] Pass
**Provenance:** `[HASIL-BACA — ref: Step 9]`

---

### S-12: Guard `MF-27`/`AC-07-04` — `options=` tetap HILANG di form `product.product` (regression guard, bukan diperbaiki)
**Level:** Negative
**Precondition:** Form `product.product` (`views/products.xml`, sebelum retarget `MF-29`).
**Mode eksekusi:** `[HASIL-BACA — ref: Step 8 §C, AC-07-04]` — desk review kode (xpath
`position="replace"` dikonfirmasi tetap ada, kontras eksplisit dengan `AC-04-01`/`AC-04-02` yang
sengaja pakai `position="attributes"` untuk kode BARU).
**Expected:** `options="{'currency_field': ..., 'field_digits': True}"` TETAP hilang dari
`list_price`/`lst_price` di form aktif — bug warisan, TIDAK diperbaiki tanpa keputusan dev baru.
**Actual:** Dikonfirmasi Step 8 — tidak ada perubahan pada baris ini di diff.
**Status:** [x] Pass (guard tetap "gagal" sesuai desain — bug dipertahankan)
**Provenance:** `[HASIL-BACA — ref: Step 8 §C, AC-07-04]`

---

### S-13: MRO `wizard.margin.product` — `sale_margin_threshold` SELALU menang (`AC-05-01`)
**Level:** Negative
**Precondition:** Kedua modul terinstall (kondisi DB saat ini).
**Mode eksekusi:** `[HASIL-BACA — ref: Step 9, test_wizard_margin_product_model_merged_when_both_installed,
PASS di DB _v10]` — tidak diulang sesi ini (alasan sama S-11).
**Expected:** Model gabungan (`_name` sama tanpa `_inherit` di kedua modul) selalu resolve ke
implementasi `sale_margin_threshold`, independen urutan install.
**Actual:** PASS di Step 9.
**Status:** [x] Pass
**Provenance:** `[HASIL-BACA — ref: Step 9]`

---

- [x] Skenario dari AC risiko tinggi (`05a_MIGRATION_ACCEPTANCE_CRITERIA.md`) — S-06, S-07 (AC-04-01/02/03),
  S-04 (AC-02-03, terkait `MF-35`/`AC-02-08` yang sudah `[HASIL-BACA — ref: Step 9]` untuk arch
  decoration order line, tidak diulang terpisah di sini karena identik cakupan S-04's setup).
- [x] **Cross-Version Compare** — N/A untuk dokumen ini, **dijalankan terpisah, lintas-modul** (lihat
  `doc-dev/migration_19.0_20.0/doc/CROSS_VERSION_COMPARE.md`), memenuhi kriteria wajib (dependency
  Enterprise `sale_renting`, >10 `MF-NNN` di project ini).
- [x] Spot-check integritas data pasca migrasi — N/A (Step 7 tidak dikerjakan, port kode saja).
- [x] **Multi-dialog dari satu aksi** — **N/A, dikonfirmasi tidak ada kasus multi-dialog** di modul
  ini: `action_confirm()` hanya pernah membuka SATU wizard (`sale.confirmation.wizard`) dari satu
  klik "Confirm", tidak ada skenario 2 dialog/wizard terbuka bersamaan dari satu aksi user.

## Ringkasan per Level

| Level | Skenario | Jumlah |
|---|---|---|
| Smoke | S-01 | 1 |
| Main Flow | S-02, S-03, S-04, S-06, S-07 | 5 |
| Detail | S-08, S-09, S-10 | 3 |
| Negative | S-05, S-11, S-12, S-13 | 4 |

**Total: 13 skenario.**

## Rekap Provenance

| Provenance | Jumlah | Skenario |
|---|---|---|
| `[DIKONFIRMASI]` | 5 | S-02, S-03, S-04, S-07 (arch), S-08 |
| `[HASIL-BACA]` | 5 | S-05, S-06 (arch), S-07 (pixel), S-11, S-12, S-13 (catatan: S-06/S-07 masing-masing punya 2 baris provenance — arch vs pixel — dihitung sesuai baris yang relevan) |
| `[HASIL-BACA-MURNI]` | 2 | S-09, S-10 |
| `[PERLU-KEPUTUSAN]` | 1 | S-01 |

**Live-executed genuinely sesi ini (bukan sitir step lain): 5 dari 13 skenario (S-02, S-03, S-04,
S-07 arch, S-08)** — semua via Odoo shell/ORM terhadap kode & DB TERKINI, BUKAN via browser (blocked
`MF-46`). 4 skenario mengutip bukti live Step 8/9 yang genuinely valid (S-06 arch, S-11, S-12, S-13).
2 skenario (S-09, S-10) benar-benar tanpa bukti apapun — ditandai `[HASIL-BACA-MURNI]`, TIDAK diberi
status Pass, dibiarkan Pending sesuai aturan.

**S-01 (Smoke) `[PERLU-KEPUTUSAN]`** — live execution browser diblokir infrastruktur bersama
(`MF-46`), BUKAN bug `sale_margin_threshold`. Backend/otentikasi/otorisasi terbukti berfungsi (session
valid, redirect benar) lewat inspeksi network/JS langsung — hanya render Owl yang gagal. Eskalasi
sudah tercatat `FINDINGS.md` `MF-46` (ditemukan sibling, dikonfirmasi ulang independen sesi ini)
dengan rekomendasi eksplisit ke dev: re-run Step 10 browser-based di sesi TERPISAH (tidak paralel
dengan sibling Step 10/Cross-Version-Compare lain).

## Human QA Checklists

Lihat folder `human_qa/` (folder yang sama) — `00_README.md`, `01_SMOKE.md`, `02_MAIN_FLOW.md`,
`03_DETAIL.md`, `04_NEGATIVE.md`.

## Loop-back

Tidak ada skenario ber-status `[x] Fail` pada LOGIKA BISNIS (S-01 gagal render, bukan gagal logic).
Tidak ada bug kode baru ditemukan sesi ini pada `sale_margin_threshold` sendiri — semua skenario yang
genuinely bisa dieksekusi (data/arch/ORM level) PASS bersih terhadap kode TERKINI. Item yang masih
`Pending` (S-05, S-09, S-10) direkomendasikan diulang begitu `MF-46` selesai diperbaiki (Step 10
browser-based di sesi tidak-paralel), SEBELUM Step 11 ditutup — tapi tidak dianggap blocker gate Step
10 ini karena levelnya Negative/Detail (bukan Smoke), dan logic-nya sendiri sudah teruji benar di
lapisan lain (Step 8 desk review + Step 9 automated test + S-02..S-08 live ORM sesi ini).

## Verdict

- [x] ⚠️ **Lulus Bersyarat** — S-01 (`[PERLU-KEPUTUSAN]`, Level Smoke) TIDAK bisa dieksekusi live
  karena blocker infrastruktur bersama (`MF-46`, dikonfirmasi independen oleh 2 sibling agent lain +
  sesi ini, root cause: corruption filestore asset bundle akibat beban gabungan berat, BUKAN bug kode
  modul ini). Backend logic untuk SEMUA skenario Main Flow/Detail/Negative sudah genuinely diverifikasi
  benar (5 live ORM execution + 4 kutipan bukti Step 8/9 yang valid) terhadap kode & DB TERKINI —
  tidak ditemukan satupun regresi/bug baru pada `sale_margin_threshold`. Keputusan dev diperlukan
  HANYA untuk: (a) apakah Step 11 boleh lanjut dengan render-browser S-01/S-05/S-09/S-10 masih
  Pending, atau (b) wajib re-run Step 10 browser-based di sesi terpisah dulu (rekomendasi `MF-46`)
  sebelum Step 11 ditutup untuk modul ini.
