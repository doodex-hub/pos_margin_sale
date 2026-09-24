# Business Flow — Migrasi pos_margin_threshold

**Step:** 10 — QA Testing (gate)
**Ref:** `05_acceptance/pos_margin_threshold/05a_MIGRATION_ACCEPTANCE_CRITERIA.md` (37 AC),
`08_review/pos_margin_threshold/08_CODE_REVIEW.md` (gate lulus, 2026-09-23),
`09_devtest/pos_margin_threshold/09_DEV_TESTING.md` (gate lulus, 2026-09-23)
**Tanggal:** 2026-09-23

> Dijalankan lewat instance Docker 20.0 (`docker-env/docker-compose.20.yml`, container
> `pos_margin_sale_migration_20-odoo-1`, port 8078) — install bersih (bukan upgrade dari data
> produksi), konsisten asumsi Step 1 "port kode saja". Environment eksekusi live: **Playwright MCP
> (CLI)** sesuai mandat template ini, BUKAN Claude Browser MCP internal.

## Ringkasan Eksekutif (baca ini dulu)

Sesi ini berjalan **paralel dengan 2 agent sibling Step 10 lain** (`sale_margin_threshold`,
`pin_message`) + 1 agent Cross-Version-Compare, semuanya memakai **satu instance Playwright MCP dan
satu container Docker 20.0 yang SAMA**. Ini menghasilkan blocker infrastruktur nyata yang sudah
dicatat lintas-modul di `FINDINGS.md` `MF-46` (ditemukan pertama oleh agent `pin_message`, direplikasi
independen sesi ini SEBELUM membaca `MF-46`, lihat addendum yang ditambahkan ke `MF-46` sesi ini):
webclient Odoo 20.0 gagal total mounting DOM (`document.body` kosong, 0 console message) di
Playwright MCP yang shared, terlepas dari database/URL/tab yang dipakai — **bukan bug kode modul
manapun**, murni kontensi Playwright+Postgres akibat 3-4 sesi Step 10 paralel.

**Strategi mitigasi yang dipakai sesi ini** (bukan sekadar menyerah ke Desk Review): dibuat database
QA **throwaway sendiri** (`pos_margin_sale_migration_20_qa_step10`, hanya `pos_margin_threshold`
ter-install, dibuat via one-off `-i` — tidak mengganggu database utama yang dipakai sibling), lalu
verifikasi prioritas tinggi (AC-07 kolom list, dedup lintas-modul, kontrak data backend combo `MF-34`)
dieksekusi via **RPC/ORM langsung** (`get_view()`, `create()` order/line sungguhan, baca field
compute nyata) terhadap registry Odoo 20.0 yang benar-benar hidup — **genuinely dieksekusi, bukan baca
kode**, walau tanpa konfirmasi visual piksel (CSS/warna) karena rendering browser blocked total. Ini
ditandai `[DIKONFIRMASI]` dengan disclosure eksplisit "via RPC/ORM, bukan render visual" di tiap
skenario terkait — bukan disamarkan sebagai visual-confirmed.

**2 item TIDAK bisa ditutup sama sekali sesi ini** (murni interaksi Owl/Dialog frontend, tidak ada
jalur RPC-proxy): S-19 (jalur decline dialog POS, `AC-03-03`) dan sebagian S-13 (rendering CSS combo
`MF-34`, bagian visual saja — kontrak data backend-nya SUDAH dikonfirmasi). Keduanya dieskalasi
`[PERLU-KEPUTUSAN]`, bukan dipaksa "Pass". S-20 (`BSL-018`, carry-forward TIGA kali) juga dieskalasi
eksplisit — ini BUKAN blocker environment, murni keputusan desain yang ditunda 3x berturut-turut.


> **ADDENDUM (2026-09-23, sesi rerun TERISOLASI — mengubah verdict sebagian):** S-19 (`AC-03-03`,
> jalur decline dialog POS) **SUDAH dieksekusi live dan LULUS** di sesi terpisah, jadi item ini TIDAK
> lagi `[PERLU-KEPUTUSAN]` — lihat S-19 di bawah untuk bukti lengkap (termasuk positive control).
> **UPDATE 2026-09-24:** S-13 dan S-20 JUGA sudah ditutup. S-13 diverifikasi visual live (combo
> product nyata) dan S-20 (`BSL-018`) ditutup lewat DUA tour test otomatis baru yang lolos bersih.
> **Tidak ada lagi item `[PERLU-KEPUTUSAN]` di dokumen ini — verdict naik jadi ✅ Lulus.**
> **Root cause `MF-46` juga akhirnya ditemukan** dan mengoreksi diagnosis di paragraf-paragraf di atas:
> penyebabnya BUKAN kontensi Postgres/paralelisme (itu gejala bersamaan yang kebetulan ada), melainkan
> **browser tool tertentu** — pada sesi rerun ini, server+database yang SAMA PERSIS merender webclient
> 20.0 dengan sempurna di Playwright MCP (`bodyLen` 27635, `odoo.isReady=true`) di saat yang sama
> Browser pane bawaan tetap `bodyLen: 15`. Lihat `FINDINGS.md` `MF-46 (lanjutan 2)`.

**Verdict: ✅ Lulus** (per 2026-09-24, naik dari "Lulus Bersyarat" setelah ketiga item ditutup) —
lihat §Verdict untuk rinciannya.

---

## Checklist wajib (sebelum skenario)

- [x] Skenario dari AC risiko tinggi — S-09, S-10, S-11 (`AC-07`/`AC-09-03`), S-13 (`AC-05-01`/`MF-34`),
  S-19 (`AC-03-03`) mencakup semua AC bertanda `[RISIKO MIGRASI TINGGI]` di `05a`.
- [x] **Cross-Version Compare** — dijalankan **terpisah, lintas-modul**, sudah ada dokumennya:
  `doc-dev/migration_19.0_20.0/doc/CROSS_VERSION_COMPARE.md` (`RMV-01`/`RMV-02`/`RMV-04` relevan
  langsung untuk `pos_margin_threshold` — dikutip di S-09/S-10/S-14 di bawah, tidak diulang dari nol).
  Tidak didup likasi di sesi ini.
- [x] Spot-check integritas data pasca migrasi — **N/A**, Step 7 (Data Migration) tidak dijalankan
  (asumsi "port kode saja" dikonfirmasi gate Step 1, 2026-09-21, tidak dikoreksi sejak itu).
- [x] **Skenario multi-dialog dari satu aksi** — **N/A, dikonfirmasi tidak ada kasus** (lihat S-21):
  dialog confirm (`AC-03-02`) dan dialog blocked (`AC-03-04`) adalah dua PATH YANG SALING EKSKLUSIF
  (dipilih oleh `is_blocked_warning`, satu config boolean — tidak pernah keduanya render dari satu
  klik "Pay" yang sama), dan wizard "Assign Margin" adalah aksi berdiri sendiri (tidak pernah dipicu
  bersamaan dialog lain). Dikonfirmasi via baca kode `pos_store.js` (patch `pay()`, if/else tunggal)
  + `wizard_margin_product.py` (tidak ada wizard bersarang) — lihat S-21 untuk detail.

## Human QA Checklists

Digenerate di `human_qa/` (folder yang sama) — 4 file (`01_SMOKE.md`..`04_NEGATIVE.md` + `00_README.md`),
diturunkan dari skenario `Level` di bawah.

---

## Skenario

### S-01: POS — flow pembayaran inti end-to-end (dialog konfirmasi below-minimum)
**Level:** Smoke
**Precondition:** POS config dengan produk below-minimum, `is_blocked_warning=False` (default)
**Mode eksekusi:** AI-interaktif (Playwright MCP) — **gagal, lihat Actual** → fallback ke Step 9
**Steps:** Buka sesi POS → tambah produk below-minimum ke order → klik "Pay" → dialog konfirmasi
muncul → klik confirm → lanjut payment screen → selesaikan pembayaran → layar receipt
**Expected:** Seluruh alur selesai tanpa crash; dialog "Price unit less than minimum price" muncul
tepat sebelum payment screen.
**Actual:** Live execution diblokir total sesi ini (`MF-46`, lihat Ringkasan Eksekutif) — TIDAK
dicoba ulang berkali-kali (STOP-rule, signature identik 3x percobaan berbeda). Fallback: Step 9
(`09_DEV_TESTING.md`) menjalankan tour REAL Chrome (`test_pos_margin_threshold_below_minimum_confirm_tour`)
2026-09-23 dan tercatat **SUCCEEDED** end-to-end (log: `TOUR ... SUCCEEDED`), mencakup PERSIS alur ini.
**Status:** [x] Pass (berdasar bukti Step 9)
**Provenance:** `[HASIL-BACA — ref: Step 9, tour test_pos_margin_threshold_below_minimum_confirm_tour, SUCCEEDED]`

### S-02: Modul terinstall bersih, form Product/Category backend terbuka tanpa error
**Level:** Smoke
**Precondition:** `pos_margin_threshold` ter-install di database 20.0
**Mode eksekusi:** AI-interaktif — gagal render, fallback RPC + Step 8/9
**Steps:** Buka form Product Template, form Product Category, list Product Variants
**Expected:** Ketiga view terbuka tanpa traceback, field custom modul tampil.
**Actual:** Dikonfirmasi via `product.product.get_view()`/`product.category` arch RPC (lihat S-09,
S-14) — arch resolve bersih, tidak ada exception. Step 9: 8/8 test `TransactionCase` di
`test_margin_sale.py` PASS (0 error), yang secara implisit membuktikan model+field valid dan installable.
**Status:** [x] Pass
**Provenance:** `[HASIL-BACA — ref: Step 8 §C AC-06-01/02, Step 9 unit tests PASS]` + RPC S-09/S-14

### S-03: Margin diwarisi dari kategori ke produk baru
**Level:** Main Flow
**Precondition:** Kategori dengan `margin_sale=20.0`
**Mode eksekusi:** N/A (regresi murni, tidak ada perubahan kode Python di area ini)
**Steps:** Buat produk baru di kategori tsb tanpa override manual → cek `margin_sale`
**Expected:** `margin_sale` produk = `20.0`
**Actual:** `tests/test_margin_sale.py::test_margin_sale_from_category` PASS (Step 9, 2026-09-23).
Dikonfirmasi ulang via RPC sesi ini (produk throwaway "QA Step10 Product Above Minimum" dibuat di
kategori `margin_sale=20.0` tanpa override → `margin_sale` produk = `20.0`, `minimum_sale_price=12.0`
= `10.0*(1+20/100)`, cocok formula).
**Status:** [x] Pass
**Provenance:** `[HASIL-BACA — ref: Step 9, test_margin_sale_from_category]`

### S-04: Override manual margin persisten (tidak revert ke kategori)
**Level:** Main Flow
**Mode eksekusi:** N/A (regresi)
**Expected:** `margin_sale` yang di-override manual tetap nilai baru setelah flush/invalidate.
**Actual:** `test_margin_sale_manual_override_persists` PASS (Step 9).
**Status:** [x] Pass
**Provenance:** `[HASIL-BACA — ref: Step 9]`

### S-05: Formula minimum_sale_price + guard div-by-zero
**Level:** Main Flow
**Mode eksekusi:** RPC (dikonfirmasi ulang sesi ini)
**Expected:** `minimum_sale_price = standard_price * (1 + margin_sale/100)`; `standard_price=0` → `margin_sale=0` (bukan error/inf) saat inverse dari `minimum_sale_price`.
**Actual:** `test_minimum_sale_price_computation`/`test_minimum_sale_price_inverse`/
`test_minimum_sale_price_zero_standard_price_guard` semua PASS (Step 9). Dikonfirmasi ulang RPC sesi
ini dengan 3 produk throwaway: `standard_price=10, margin=20 → min=12`; `standard_price=10, margin=50
→ min=15`; `standard_price=100, margin=-10 → min=90` (formula konsisten untuk margin negatif juga).
**Status:** [x] Pass
**Provenance:** `[HASIL-BACA — ref: Step 9]` + RPC korroboratif

### S-06: Wizard "Assign Margin" dari list Template & list Variant
**Level:** Main Flow
**Precondition:** User di list Product Template / Product Variant, 1+ record dipilih
**Mode eksekusi:** AI-interaktif — gagal render, fallback Desk Review
**Steps:** Jalankan action server "Assign Margin" dari kedua entry point → isi margin → klik "Assign"
**Expected:** Wizard `wizard.margin.product` terbuka dengan field yang sesuai konteks
(`product_template_ids` vs `product_ids`); klik Assign menulis `margin_sale` semua record terpilih.
**Actual:** Tidak bisa live-klik sesi ini (`MF-46`). Desk Review Step 8 (`AC-02-01/02/03`): kode
`action_assign_margin()` (dua method paralel) + `_compute_product_model` dikonfirmasi Match, byte-identik
19.0. Catatan `ISS-03` (Step 8): nilai `is_product` yang dikutip di `05a` AC-02-01/02 terbalik dari kode
aktual — ini typo DESKRIPSI AC, bukan bug; behavior yang terlihat user tetap benar (dikonfirmasi jejak
nalar Step 8). Test existing `test_wizard_assign_margin_from_template_list` PASS (Step 9).
**Status:** [x] Pass
**Provenance:** `[HASIL-BACA — ref: Step 8 §C AC-02-01/02/03, Step 9]`

### S-07: Dialog konfirmasi POS saat line di bawah minimum (mode non-blocking)
**Level:** Main Flow
**Mode eksekusi:** AI-interaktif — gagal render (sama seperti S-01), fallback Step 9
**Expected:** Dialog "Price unit less than minimum price" (confirm/cancel) muncul saat klik Pay.
**Actual:** Tour `test_pos_margin_threshold_below_minimum_confirm_tour` **SUCCEEDED** (Step 9, real
Chrome, 2026-09-23) — mencakup PERSIS skenario ini (`AC-03-02`).
**Status:** [x] Pass
**Provenance:** `[HASIL-BACA — ref: Step 9, tour SUCCEEDED]`

### S-08: Dialog blocking POS saat `blocking_transaction_pos=True`
**Level:** Main Flow
**Mode eksekusi:** AI-interaktif — gagal render, fallback Step 9
**Expected:** `AlertDialog` (hanya tombol "Ok") muncul, dismiss TIDAK lanjut ke payment.
**Actual:** Tour `test_pos_margin_threshold_below_minimum_blocked_tour` **SUCCEEDED** (Step 9, real
Chrome, `AC-03-04`).
**Status:** [x] Pass
**Provenance:** `[HASIL-BACA — ref: Step 9, tour SUCCEEDED]`

### S-09: List Product Variants — kolom Margin/Minimum sale price/Incl. Tax + decoration `[RISIKO TINGGI]`
**Level:** Main Flow
**Precondition:** Database dengan `pos_margin_threshold` DAN `sale_margin_threshold` ter-install
(`pos_margin_sale_migration_20_qa`, database QA utama)
**Mode eksekusi:** AI-interaktif (Playwright) — **gagal render (MF-46)** → **fallback: RPC/ORM
langsung terhadap registry Odoo 20.0 HIDUP** (bukan Desk Review kode statis)
**Steps (via RPC, method `product.product.get_view(view_type='list')` + baca field produk nyata):**
1. Ambil arch view `product.product` list (`get_view()`, hasil MERGE lengkap seperti yang dikirim ke
   client asli)
2. Cek field `lst_price`/`margin_sale`/`minimum_sale_price`/`minimum_sale_price_with_tax` ada di arch
3. Cek atribut `decoration-danger` pada `lst_price` dan `margin_sale`
4. Baca field aktual beberapa produk nyata di database (bukan produk buatan sendiri) untuk konfirmasi
   nilai compute + kondisi decoration genuinely benar untuk data riil
**Expected:** Kolom `margin_sale`/`minimum_sale_price` `optional="show"` tanpa toggle manual;
`lst_price` `decoration-danger="is_less_minimum_sale"`; `margin_sale` `decoration-danger="margin_sale &lt; 0.0"`;
kolom "Incl. Tax" (`minimum_sale_price_with_tax`) ada & terisi benar.
**Actual (dieksekusi 2026-09-23, `docker exec ... odoo-bin shell -d pos_margin_sale_migration_20_qa`,
READ-ONLY, tanpa `env.cr.commit()`):**
```
ARCH_COUNTS margin=1 min_price=1 tax=1
LST_PRICE_DECORATION is_less_minimum_sale
MARGIN_DECORATION margin_sale < 0.0
```
Baca produk nyata di database (bukan data buatan): produk id 85/86 ("QA10 SMT Variant Product")
`margin_sale=-10.0`, `is_less_minimum_sale=True`, `minimum_sale_price_with_tax=99.00` (=`90*1.1`,
benar) — decoration merah AKAN genuinely ter-trigger untuk baris ini kalau dirender. Produk id 4
("Test Rental Margin QA 20") `is_less_minimum_sale=False` — decoration TIDAK ter-trigger, juga benar
(kontrol negatif). **Disclosure jujur:** ini MEMBUKTIKAN struktur arch + kebenaran nilai compute yang
akan dipakai kondisi decoration, dieksekusi via RPC/ORM NYATA (bukan baca kode) — TAPI TIDAK
membuktikan warna merah genuinely tampil di layar (rendering CSS/browser blocked total, `MF-46`).
Dikorroborasi independen oleh Cross-Version-Compare (`RMV-01`/`RMV-02`, `CROSS_VERSION_COMPARE.md`)
yang menemukan arch identik via jalur RPC terpisah.
**Status:** [x] Pass (untuk bagian struktur+data yang genuinely diverifikasi; lihat disclosure)
**Provenance:** `[DIKONFIRMASI — via RPC/ORM live execution, BUKAN render visual browser; lihat MF-46]`

### S-10: Dedup kolom lintas-modul — kedua modul margin terinstall bersamaan `[RISIKO TINGGI]`
**Level:** Main Flow
**Precondition:** `pos_margin_threshold` DAN `sale_margin_threshold` ter-install (`MF-37`)
**Mode eksekusi:** RPC (sama seperti S-09)
**Steps:** Sama seperti S-09, hitung berapa kali `margin_sale`/`minimum_sale_price`/
`minimum_sale_price_with_tax` muncul di arch merge.
**Expected:** TEPAT satu set kolom (bukan dobel).
**Actual:** `ARCH_COUNTS margin=1 min_price=1 tax=1` — TEPAT satu set, dedup `MF-37` berfungsi di HEAD
saat ini. Dikonfirmasi juga oleh `sale_margin_threshold` sisi lain (marker `o_smt_dedup_*` stripped),
dan oleh Cross-Version-Compare (`RMV-01`, arch RPC independen, hasil sama).
**Status:** [x] Pass
**Provenance:** `[DIKONFIRMASI — via RPC/ORM live execution]`, dikorroborasi `RMV-01`/`CROSS_VERSION_COMPARE.md`

### S-11: Kolom list tetap tampil benar saat `pos_margin_threshold` SENDIRIAN (tanpa `sale_margin_threshold`) `[RISIKO TINGGI]`
**Level:** Main Flow
**Precondition:** Database THROWAWAY baru (`pos_margin_sale_migration_20_qa_step10`), hanya
`pos_margin_threshold` ter-install (dikonfirmasi `sale_margin_threshold`/`pin_message` `state=uninstalled`)
— dibuat khusus sesi ini via one-off `-i pos_margin_threshold --stop-after-init`, TIDAK menyentuh
database utama, supaya tidak mengganggu sibling agent yang sedang QA `sale_margin_threshold`.
**Mode eksekusi:** RPC/ORM langsung di database throwaway
**Steps:** Sama seperti S-09/S-10, di database yang HANYA punya modul ini.
**Expected:** Kolom modul ini tetap tampil satu set (logic dedup ada di SISI `sale_margin_threshold`,
jadi tidak relevan di sini — modul ini tidak boleh ikut hilang/berubah hanya karena modul lain absen).
**Actual:** `STANDALONE_ARCH_COUNTS margin=1 min_price=1 tax=1`, `INSTALLED_MODULES_STANDALONE
['pos_margin_threshold']` — kolom tampil benar, tidak terpengaruh keberadaan/ketiadaan
`sale_margin_threshold`. Data produk throwaway juga dikonfirmasi benar (lihat S-05).
**Status:** [x] Pass
**Provenance:** `[DIKONFIRMASI — via RPC/ORM live execution, database throwaway terisolasi]`

### S-12: Wizard "Assign Margin" — tombol Cancel tidak mengubah apapun
**Level:** Detail
**Mode eksekusi:** N/A (behavior native `special="cancel"`)
**Expected:** Tidak ada `margin_sale` record manapun berubah.
**Actual:** Tidak ada test otomatis (gap diketahui, dicatat `05a`/Step 8 sebagai low-risk, native
button behavior, bukan logic modul). Tidak dicoba live sesi ini (di luar prioritas, dan `MF-46` akan
memblokirnya juga).
**Status:** [ ] Pass / [ ] Fail — **Pending**
**Provenance:** `[HASIL-BACA-MURNI]` — tidak ada eksekusi live maupun test otomatis. Risiko dinilai
rendah (native framework behavior, `special="cancel"` tidak pernah memanggil method modul apapun,
dikonfirmasi baca `wizard_margin_product.xml`). **Level Detail (bukan Smoke/Negative), sehingga TIDAK
wajib dieskalasi `[PERLU-KEPUTUSAN]`** per aturan provenance — dicatat rekomendasi non-blocking untuk
ditutup test-nya di sesi Step 9 berikutnya.

### S-13: Styling combo-child aktif di orderline POS (`MF-34`, AKTIF pertama kali di 20.0) `[RISIKO TINGGI]`
**Level:** Detail
**Precondition:** Order POS dengan produk combo (`product.combo` + template `type='combo'`)
**Mode eksekusi:** AI-interaktif (Playwright, untuk visual) — **gagal render (MF-46)** → fallback:
**kontrak data backend via ORM** (database throwaway) + Desk Review Step 8 untuk template JS
**Steps (ORM, database throwaway):**
1. Buat produk combo (`QA Step10 Combo Parent` + `QA Step10 Combo Choice A/B`), buka sesi POS
2. Buat `pos.order` nyata dengan 1 line combo-parent + 1 `pos.order.line` child dengan
   `combo_parent_id` di-set ke id line parent
3. Baca kembali `child_line.combo_parent_id` dan cocokkan ke id parent
**Expected:** Backend menyimpan relasi `combo_parent_id` dengan benar (prasyarat SEBELUM frontend bisa
merender class `border-start border-3 ms-4`); frontend `orderline.xml`
(`this.line.combo_parent_id ? '...' : ''`) sudah dikonfirmasi Match/byte-benar di Step 8.
**Actual:** `CHILD_LINE combo_parent_id= 1 expected_parent= 1 MATCH= True` — kontrak data backend
dikonfirmasi BENAR via eksekusi ORM nyata (bukan baca kode), sesi ini, database throwaway. **Bagian
visual (CSS border-left genuinely tampil di layar POS) TIDAK bisa dikonfirmasi** — blocker rendering
sama seperti S-09 (`MF-46`). Ini adalah bukti BARU (belum pernah ada sebelumnya — Step 9 mencatat
"verifikasi visual live BELUM dilakukan sama sekali") yang MENAIKKAN keyakinan tapi TIDAK
menggantikan kebutuhan tour test visual nyata.
**Status:** [ ] Pass / [ ] Fail — **Pending** (bagian data: lulus; bagian visual: belum terverifikasi)
**Provenance:** `[HASIL-BACA]` untuk keseluruhan skenario (backend `[DIKONFIRMASI]` + frontend code
Match Step 8, tapi TIDAK ADA tour/klik visual apapun yang membuktikan CSS benar-benar render) —
**direkomendasikan kuat jadi prioritas tour test baru Step 9 sebelum Step 11**, konsisten rekomendasi
Step 8/9 sebelumnya. Risiko dinilai SEDANG (bukan tinggi) mengingat kontrak data + kode frontend
sudah dua-duanya dikonfirmasi benar secara independen, hanya langkah render piksel terakhir yang
belum tertutup.


**ADDENDUM — VERIFIKASI VISUAL LIVE (2026-09-23, Playwright, DB `..._qa_decline` port 8182):
`[DIKONFIRMASI]`/Pass, DENGAN satu koreksi penting atas klaim dampak `MF-34`.**

**Setup nyata:** dibuat lewat RPC produk combo sungguhan — `MF34 Combo Menu`
(`product.template` `type='combo'`, `available_in_pos=True`) dengan 2 `product.combo`
(`MF34 Main` -> `MF34 Burger`, `MF34 Drinks` -> `MF34 Drink`). Combo diklik di POS nyata sehingga POS
membuat line parent + 2 line child ber-`combo_parent_id`.

**Hasil render (bagian visual yang selama ini kosong — sekarang tertutup):** kedua orderline child
ter-render dengan `class="orderline border-start orderline-combo fst-italic ms-4 ... border-3"`,
`border-left-width: 3px solid rgb(222,226,230)`, `margin-left: 24px`; line parent TIDAK ter-indent
(`border-left-width: 0px`, `margin-left: 0px`). Jadi styling combo-child (indent + garis kiri +
italic) **genuinely tampil di layar** — lihat screenshot `mf34-combo-visual.png`.

**KOREKSI atas klaim `MF-34` ("styling combo AKTIF untuk pertama kalinya di 20.0, perubahan behavior
yang terlihat dibanding SEMUA versi sebelumnya"):** klaim itu **TIDAK BENAR**, dan judul skenario ini
("AKTIF pertama kali di 20.0") ikut terkoreksi. Diverifikasi dengan eksperimen langsung di DOM +
baca source native:
1. **Native 20.0 sendiri sudah memberi `border-start` dan `orderline-combo fst-italic ms-4`** untuk
   setiap line ber-`combo_parent_id` — `odoo20/addons/point_of_sale/static/src/app/components/
   orderline/orderline.js` getter `lineContainerClasses` baris 53-54.
2. **Native 19.0 JUGA sudah memberikannya** (`odoo19/.../orderline.js` baris 61-62, isi praktis
   identik). Jadi indent + garis kiri sudah tampil di 19.0 TERLEPAS dari typo `line.comboParent` —
   typo itu tidak pernah menghilangkan styling, karena yang merender adalah native, bukan modul ini.
3. **Kontribusi unik modul (`border-3`) terbukti no-op secara visual.** Diuji langsung: menghapus
   `border-3` dari elemen -> `border-left-width` TETAP `3px`; menghapus `border-start` (milik native)
   juga -> baru jadi `0px`/`none`. Jadi yang benar-benar menghasilkan garis adalah class NATIVE,
   sedangkan `border-start`/`ms-4` dari modul duplikat dan `border-3` tidak mengubah lebar apapun.
**Implikasi (positif untuk mandat migrasi):** tidak ada perubahan behavior visual 19.0 -> 20.0 di
jalur ini — parity terjaga, dan "perubahan behavior yang terlihat" yang sempat disetujui dev di
`MF-34` sebenarnya tidak pernah terjadi. Tidak ada aksi kode yang diperlukan.
**Catatan penting — override modul TIDAK mati/dead code.** Atribut `t-attf-class` yang sama juga
membawa `this.line.isLessMinimumSalePrice ? 'text-danger' : ''`, dan bagian ITU terbukti hidup di
layar yang sama: line `MF-Decline Test Product` ter-render `text-danger` (merah) berikut baris
peringatan `*The price of this product is less than minimum sale price $ 15.00`. Jadi fix `MF-41`
(`this.line` + anchor `t-call-slot`) memang benar dan perlu; yang redundan HANYA bagian combo-nya.
**Status (diperbarui):** [x] Pass — bagian data (`combo_parent_id`) DAN bagian visual keduanya
terverifikasi.
**Provenance (diperbarui):** `[DIKONFIRMASI]` — eksekusi live Playwright dengan combo product
sungguhan, 2026-09-23.

### S-14: Field `margin_sale` di form Product Category — posisi anchor baru
**Level:** Detail
**Mode eksekusi:** RPC (arch mentah)
**Expected:** `margin_sale` muncul sebelum `property_cost_method`, inherit dari
`account.view_category_property_form` (anchor lama `stock_account.view_category_property_form_stock`
sudah tidak ada di 20.0).
**Actual:** Dikonfirmasi Step 8 (Match) + dikorroborasi independen oleh Cross-Version-Compare
(`RMV-04`): `ir.ui.view.read()` arch mentah mengonfirmasi `inherit_id` tepat ke
`account.view_category_property_form`, xpath `property_cost_method position="before"` resolve.
**Status:** [x] Pass
**Provenance:** `[HASIL-BACA — ref: Step 8 §C AC-06-02]`, dikorroborasi `RMV-04`

### S-15: Data produk (`minimum_sale_price`/`minimum_sale_price_with_tax`) terkirim ke frontend POS
**Level:** Detail
**Mode eksekusi:** N/A (indirect, terbukti lewat tour PASS)
**Expected:** `_load_pos_data_fields` mengirim 2 field baru; getter frontend membacanya benar.
**Actual:** Tour `..._confirm_tour`/`..._blocked_tour` PASS (Step 9) — keduanya BERGANTUNG pada nilai
ini benar-benar terkirim & terbaca frontend (dialog memakai `line.minimumSalePriceWithTax`), jadi PASS
tour = bukti tidak langsung yang kuat. Step 8: kode `super()`-then-extend dikonfirmasi Match.
**Status:** [x] Pass
**Provenance:** `[HASIL-BACA — ref: Step 8 §C AC-08-01/02, Step 9 tour PASS (indirect)]`

### S-16: `wizard.margin.product` MRO merge — `sale_margin_threshold` menang
**Level:** Detail
**Mode eksekusi:** N/A (test existing sudah genuinely jalan, bukan skip)
**Expected:** Model gabungan resolve tanpa error, `sale_margin_threshold` yang menang.
**Actual:** `test_wizard_margin_product_model_merged_when_both_installed` PASS di Step 9 — dikonfirmasi
GENUINELY tereksekusi (bukan skip) karena database `_qa_v7` waktu itu sudah punya kedua modul.
**Status:** [x] Pass
**Provenance:** `[HASIL-BACA — ref: Step 9, test genuinely executed (not skipped)]`

### S-17: Quirk yang wajib dipertahankan — absensi recompute (`AC-01-07`) & jalur onchange (`AC-01-08`)
**Level:** Detail
**Mode eksekusi:** N/A (regression-guard, bukan business flow user-facing)
**Expected:** `_compute_warning` TIDAK punya `@api.depends` (quirk sengaja dipertahankan);
`@api.onchange('margin_sale')` tetap ada di atas `_set_product_margin_sale`.
**Actual:** Dikonfirmasi Step 8 (Match, baca baris kode langsung) — keduanya masih seperti seharusnya,
tidak diam-diam "diperbaiki" saat migrasi.
**Status:** [x] Pass
**Provenance:** `[HASIL-BACA — ref: Step 8 §C AC-01-07/08]`

### S-18: Dead code/quirk lain wajib identik (`AC-10-01/02/03`)
**Level:** Detail
**Mode eksekusi:** N/A
**Expected:** `views/product_template_views.xml` tidak di manifest; `pos_session.py` tetap
kosong/komentar; `controllers.py` tidak disentuh.
**Actual:** Dikonfirmasi Step 8 (Match, baca manifest/file langsung).
**Status:** [x] Pass
**Provenance:** `[HASIL-BACA — ref: Step 8 §C AC-10-01/02/03]`

### S-19: POS — user DECLINE dialog konfirmasi (bukan confirm) `[RISIKO — jalur satu-satunya yang membatalkan pembayaran]`
**Level:** Negative
**Precondition:** Dialog konfirmasi below-minimum muncul (sama seperti S-07)
**Mode eksekusi:** AI-interaktif (Playwright) — **DIEKSEKUSI LIVE & BERHASIL (2026-09-23, sesi rerun
terisolasi)**, menggantikan status `[PERLU-KEPUTUSAN]` sebelumnya.
**Steps (yang BENAR-BENAR dijalankan):** Environment terisolasi (port `8182`, database
`pos_margin_sale_migration_20_qa_decline`, `pos_margin_threshold` sendirian, proses `odoo-bin` kedua
— tidak menyentuh DB utama). Produk `MF-Decline Test Product` (`list_price` 1.00,
`minimum_sale_price_with_tax` 15.00, jadi genuinely below-minimum), POS config `MF-Decline Shop`,
`ir.config_parameter` `post_margin_sale.blocking_transaction_pos` TIDAK di-set (dikonfirmasi 0 row di
DB) sehingga `is_blocked_warning=False` -> jalur dialog konfirmasi (BUKAN jalur `AlertDialog` blocked).
Login POS -> Open Register -> klik produk -> klik "Payment" -> dialog muncul -> klik **"Discard"**
(tombol decline, `button.btn-secondary`), BUKAN "Ok".
**Expected:** `return` bersih, tidak lanjut ke payment, tidak ada crash.
**Actual:** **PASS, semua assert terpenuhi:**
1. Dialog muncul persis seperti kode `pos_store.js`: title `"Price unit less than minimum price"`,
   body `"Some products are below the minimum price. Proceed to payment?"`, tombol `Ok` / `Discard`.
2. Setelah klik "Discard": `dialogOpen=false`, `onProductScreen=true`, `onPaymentScreen=false`,
   URL tetap `/pos/ui/1/product/<uuid>` (TIDAK berpindah ke `/payment/`).
3. **Tidak ada data hilang** — orderline tetap utuh (`1 x MF-Decline Test Product, $ 1.00`),
   berikut teks peringatan modul `"*The price of this product is less than minimum sale price
   $ 15.00"` (bukti tambahan: override `orderline.xml` modul ini juga render benar live di 20.0).
4. **Tidak ada side effect server** — `select * from pos_order` = **0 row** setelah decline.
5. **0 console error** (`browser_console_messages level=error` -> 0).
6. **Positive control (penting — membedakan "decline bekerja" dari "tombol Pay rusak"):** klik
   "Payment" LAGI lalu klik **"Ok"** -> URL BERPINDAH ke `/pos/ui/1/payment/<uuid>` (PaymentScreen).
   Jadi jalur confirm terbukti masih berfungsi, membuktikan bahwa berhentinya alur pada langkah 2
   memang disebabkan oleh decline, bukan oleh tombol/flow yang rusak.
**Status:** [x] Pass
**Provenance:** `[DIKONFIRMASI]` — eksekusi live Playwright, 2026-09-23 (rerun terisolasi pasca
`MF-46`; lihat `FINDINGS.md` `MF-46 (lanjutan 2)` untuk root cause tooling yang akhirnya ditemukan).
**Catatan gap yang TETAP terbuka:** jalur ini masih **belum punya test otomatis** (tour) — verifikasi
di atas manual-interaktif, jadi tidak menjaga regresi masa depan. Rekomendasi Opsi 3 di ESCALATION
lama (tulis tour test decline) tetap relevan sebagai follow-up, tapi TIDAK lagi memblokir Step 10.

### S-20: POS — TIDAK ADA dialog sama sekali saat semua line di atas minimum (`BSL-018`) — **DITUTUP**
**Level:** Negative
**Precondition:** Order dengan SEMUA line di atas `minimum_sale_price_with_tax` masing-masing
**Mode eksekusi:** **Tour test otomatis BARU** (`pos_margin_threshold_no_dialog_above_minimum_tour`,
real Chrome, `--test-enable`) — dev memilih Opsi 1 dari ESCALATION lama (tulis test, jangan
carry-forward keempat kalinya), dieksekusi 2026-09-23/24.
**Expected:** Nol dialog/popup apapun, termasuk tidak ada flash/render sekilas.
**Actual:** **PASS.** Tour menjual produk di harga 50 (di atas minimum, dijaga prakondisi Python
`5 < minimum < 50`), klik "Pay", lalu meng-assert tiga hal: (1) langsung sampai di
`.pos-content .payment-screen`; (2) `body:not(:has(.modal))` saat itu; (3) **tidak ada node `.modal`
yang PERNAH disisipkan** selama proses — dipantau `MutationObserver` yang dipasang SEBELUM klik Pay.
Poin (3) yang membuat AC ini genuinely tertutup: assert "payment screen tampil" saja tidak cukup,
karena dialog yang muncul lalu tertutup di frame yang sama tetap akan lolos, padahal AC-nya eksplisit
menyebut "termasuk tidak ada flash/render sekilas".
**Hasil run:** `0 failed, 0 error(s) of 4 tests` — keempat tour `pos_margin_threshold` (2 lama +
2 baru) lolos bersih di database `pos_margin_sale_migration_20_bsl018`.
**Status:** [x] Pass
**Provenance:** `[DIKONFIRMASI]` — test otomatis, bukan klik manual, jadi juga menjaga regresi ke depan.
**⚠️ Versi sebelumnya belum punya ini:** branch `migration/19.0` dan `migration/18.0` TIDAK punya
tour maupun method test ini; 18.0/19.0 tetap tanpa coverage otomatis untuk perilaku ini. Jangan
diasumsikan ikut tertutup — harus di-backport eksplisit kalau diinginkan di sana. Lihat `FINDINGS.md`
`MF-48`.
**Bagian kedua `BSL-018` ikut ditutup di sini:** "assert teks/warna warning orderline secara
terpisah" (bukan sekadar menyimpulkan "tidak crash" dari tour dialog) sekarang punya tour sendiri,
`pos_margin_threshold_orderline_warning_tour` — assert teks warning, nominalnya, warna merah yang
benar-benar ter-render (bukan cuma ada class `text-danger`), plus line kontrol di atas minimum yang
TIDAK boleh ditandai. Juga Pass di run yang sama.

### S-21: Cek multi-dialog dari satu aksi — N/A, dikonfirmasi tidak ada kasus
**Level:** Negative
**Mode eksekusi:** N/A (analisis struktur kode)
**Expected/Actual:** Dialog confirm (`AC-03-02`) dan dialog blocked (`AC-03-04`) dipilih oleh SATU
config boolean (`is_blocked_warning`) di dalam SATU blok if/else pada `pos_store.js` `pay()` — tidak
pernah keduanya dievaluasi/dirender dari satu klik yang sama. Wizard "Assign Margin" adalah action
server berdiri sendiri, tidak pernah dipicu bersamaan dialog lain (dikonfirmasi baca
`wizard_margin_product.py`/`.xml`, tidak ada wizard bersarang atau `context` yang membuka dialog
kedua). **Modul ini tidak punya kasus ">1 dialog dari satu aksi user"** — checklist wajib di atas
sudah ditandai N/A berdasar analisis ini.
**Status:** [x] Pass (N/A secara struktural)
**Provenance:** `[HASIL-BACA]`

---

## Ringkasan per Level

| Level | Skenario | Jumlah |
|---|---|---|
| Smoke | S-01, S-02 | 2 |
| Main Flow | S-03, S-04, S-05, S-06, S-07, S-08, S-09, S-10, S-11 | 9 |
| Detail | S-12, S-13, S-14, S-15, S-16, S-17, S-18 | 7 |
| Negative | S-19, S-20, S-21 | 3 |
| **Total** | | **21** |

## Rekap Provenance

| Provenance | Jumlah | Skenario |
|---|---|---|
| `[DIKONFIRMASI]` (RPC/ORM live execution, disclosed non-visual) | 3 | S-09, S-10, S-11 |
| `[DIKONFIRMASI]` (UI live execution penuh, Playwright, rerun terisolasi 2026-09-23) | 2 | S-19, S-13 (bagian visual — lihat ADDENDUM) |
| `[DIKONFIRMASI]` (tour test otomatis BARU, `BSL-018`, 2026-09-23/24) | 1 | S-20 |
| `[HASIL-BACA]` (ref Step 8/9, sebagian dikorroborasi RPC/RMV) | 14 | S-01, S-02, S-03, S-04, S-05, S-06, S-07, S-08, S-14, S-15, S-16, S-17, S-18, S-21 |
| `[HASIL-BACA-MURNI]` | 1 | S-12 (Pending, Level Detail, risiko rendah, tidak wajib eskalasi) |
| `[PERLU-KEPUTUSAN]` | 0 | — (S-20 ditutup lewat tour test baru; tidak ada item tersisa) |

**Catatan transparansi (diperbarui 2026-09-24):** S-19 dan S-13 ditandai Pass `[DIKONFIRMASI]` lewat
eksekusi live UI Playwright di environment terisolasi (S-19 termasuk positive control). **S-20
(`BSL-018`) juga SUDAH ditutup** — bukan lewat klik manual, tapi lewat DUA tour test otomatis baru,
sehingga sekaligus menjaga regresi ke depan. Tidak ada lagi skenario `[PERLU-KEPUTUSAN]` di dokumen ini. S-12 (`[HASIL-BACA-MURNI]`, Level Detail) sengaja dibiarkan
Pending sesuai aturan, TIDAK dieskalasi `[PERLU-KEPUTUSAN]` karena risikonya rendah dan levelnya bukan
Smoke/Negative.

## Loop-back

Tidak ada skenario berstatus Fail (semua yang dievaluasi = Pass), dan **tidak ada lagi skenario
Pending `[PERLU-KEPUTUSAN]`** setelah `BSL-018` ditutup 2026-09-24. Tidak perlu balik ke Step 9 untuk
fix kode — tidak ada bug modul yang ditemukan, baik di sesi Step 10 asli, di rerun terisolasi, maupun
saat menulis test `BSL-018`.

## Verdict

- [x] ✅ **Lulus** — 3 item yang semula bersyarat semuanya sudah ditutup dengan bukti eksekusi nyata:
  1. ~~**S-19 (`AC-03-03`, decline dialog)**~~ — **SELESAI 2026-09-23.** Dieksekusi live penuh
     (Playwright, environment terisolasi), termasuk positive control yang membuktikan alur berhenti
     karena decline, bukan karena tombol rusak. `[DIKONFIRMASI]`/Pass.
  2. ~~**S-20 (`AC-03-05`/`BSL-018`, nol dialog)**~~ — **SELESAI 2026-09-24.** Dev memilih Opsi 1
     (tulis test, jangan carry-forward keempat kalinya). DUA tour otomatis baru ditulis dan lolos
     (`0 failed, 0 error(s) of 4 tests`). Berbeda dari dua item lain, penutupan ini **juga menjaga
     regresi ke depan**, bukan cuma membuktikan sekali. Lihat `FINDINGS.md` `MF-48`.
  3. ~~**S-13 (`AC-05-01`, styling combo `MF-34`)**~~ — **SELESAI 2026-09-23.** Diverifikasi visual
     live dengan combo product sungguhan. Sekaligus MENGOREKSI klaim dampak `MF-34`: styling combo
     ternyata sudah disediakan NATIVE sejak 19.0, jadi fix ini TIDAK mengubah behavior user — parity
     justru terjaga. Lihat ADDENDUM S-13 dan `FINDINGS.md` `MF-34` §KOREKSI.

  **Tidak ada gap kode BARU yang ditemukan sepanjang Step 10** — yang ditutup adalah gap BUKTI dan
  gap COVERAGE, bukan cacat modul. 37 dari 37 AC kini tertutup `[DIKONFIRMASI]`/`[HASIL-BACA]` dengan
  bukti solid (test otomatis PASS, eksekusi live UI/RPC/ORM, atau Desk Review Step 8 yang sudah lulus
  gate).
- [ ] ❌ Ada kegagalan

**Sisa residual yang layak ditindaklanjuti (TIDAK blocking Step 11, bukan `[PERLU-KEPUTUSAN]`):**
**jalur decline POS (S-19)** genuinely belum punya test otomatis — terverifikasi manual saja, jadi
tidak ada yang menjaga regresinya. Pola `BSL-018` menunjukkan menutup gap seperti ini murah;
direkomendasikan sebagai Step 9 addendum, bukan diselipkan lagi ke Step 10.

**KOREKSI (2026-09-24):** versi sebelumnya paragraf ini juga menyebut dedup kolom `MF-37` "masih
terverifikasi manual saja" — **itu SALAH**. `MF-37` SUDAH punya test otomatis sejak Step 9:
`sale_margin_threshold/tests/test_high_risk_ac.py::test_ac_04_02_product_variants_columns_dedup_contract`,
yang meng-assert node bermarker `o_smt_dedup_*` sudah ter-strip dari arch final DAN tersisa tepat satu
kolom `margin_sale`/`minimum_sale_price`/`minimum_sale_price_with_tax`. Dijalankan 2026-09-24 di
database dengan KEDUA modul terinstall (`pos_margin_sale_migration_20_qa_dedup`): **lolos, dan
genuinely dieksekusi — bukan ter-skip** (13/13 test `sale_margin_threshold` pass di sana).

**Caveat nyata yang tersisa (jauh lebih kecil dari klaim yang dikoreksi):** test itu memanggil
`self.skipTest()` kalau `pos_margin_threshold` TIDAK terinstall. Di run test single-module yang biasa
(hanya `sale_margin_threshold`) ia **diam-diam ter-skip** tanpa sinyal kegagalan apapun. Jadi supaya
dedup `MF-37` benar-benar terjaga di CI, run test WAJIB menyertakan kedua modul terinstall bersamaan —
kalau tidak, coverage-nya ada di repo tapi tidak pernah dieksekusi.

**Langkah konkret berikutnya untuk dev:**
1. Lanjut ke **Step 11 (UAT Sign-off)** — Step 10 modul ini sudah lulus tanpa syarat.
2. Opsional sebelum rilis: jadwalkan Step 9 addendum untuk test regresi jalur decline POS, dan
   pastikan run CI menyertakan kedua modul margin bersamaan (lihat caveat `MF-37` di atas).
3. ~~`git push -u origin migration/20.0`~~ — **SUDAH dijalankan dev 2026-09-24**; `origin/migration/20.0`
   sinkron penuh dengan lokal (commit `1c7d420`). Tidak ada aksi tersisa.
