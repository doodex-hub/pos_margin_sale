# Business Flow — Migrasi pin_message

**Step:** 10 — QA Testing (gate)
**Ref:** `05_acceptance/pin_message/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-09-23

> Dijalankan lewat instance persisten `pos_margin_sale_migration_20_qa` (bukan instance data
> produksi — sesuai asumsi "port kode saja", lihat `CLAUDE.md`), container
> `pos_margin_sale_migration_20-odoo-1`, port 8078.

---

## 0. Ringkasan eksekusi (baca ini dulu)

**Mode eksekusi yang DIRENCANAKAN:** AI-interaktif via Playwright MCP (CLI, sesuai `CLAUDE.md`
§"Mandatory Read Order"/`ai-doc/USAGE_GUIDE.md`).

**Yang GENUINELY terjadi:** eksekusi live **BLOCKED total** untuk seluruh skenario prioritas
(`AC-06-01` thread-switch, `AC-04-02` jump/"See") — bukan karena kesalahan skenario/selector, tapi
karena dua kondisi lingkungan di luar kendali sesi ini, dikonfirmasi lewat ≥6 percobaan berbeda
(login ulang, tab baru, patch `document.hidden` manual, navigasi ulang, wait diperpanjang sampai 10
detik) dengan **signature kegagalan identik setiap kali** (STOP-rule ditegakkan, lihat detail teknis
lengkap di `FINDINGS.md` `MF-46`):

1. **Browser Playwright MCP genuinely SHARED** antar seluruh agent sibling yang berjalan paralel
   sesi ini (2 sibling Step 10 modul lain + 1 Cross-Version-Compare) — tab bertambah dari 1 ke 6+,
   URL "tab current" berubah sendiri di antara panggilan tool tanpa aku memanggil navigasi apapun.
2. **Webclient Odoo 20.0 konsisten render blank** di tab manapun yang dipakai (`document.body`
   hanya shell kosong 15 karakter, 0 console message, hanya 1 RPC `load_menus` yang selesai, Owl app
   tidak pernah genuinely mounting) — **dikonfirmasi BUKAN spesifik ke agent/tab ini**: tab milik
   sibling lain diperiksa langsung dan sama-sama blank di saat bersamaan. `docker logs db`
   (read-only, tidak ada restart dilakukan) menunjukkan checkpoint Postgres >100 detik + beberapa
   serialization error, konsisten beban I/O berat dari eksekusi paralel 3-4 sesi QA sekaligus
   terhadap container/DB yang sama.

**Konsekuensi:** SEMUA skenario di dokumen ini berstatus Provenance `[HASIL-BACA]` (mengutip bukti
Tour otomatis Step 9 yang genuinely PASS) atau `[HASIL-BACA-MURNI]`/`[PERLU-KEPUTUSAN]` (area yang
Step 9 sendiri konfirmasi TIDAK ada test otomatis apapun) — **tidak ada satupun** yang
`[DIKONFIRMASI]` (live nyata) sesi ini. Ini bukan "gap baru" untuk hal yang sudah dibuktikan Step 9,
tapi genuinely gap terbuka untuk `AC-06-01`/`AC-04-02` yang memang belum pernah dibuktikan otomatis
di step manapun sebelumnya juga.

**Bug ditemukan?** Tidak ada bug BARU yang genuinely ditemukan (karena tidak ada eksekusi live yang
berhasil). Sebagai kompensasi, `AC-06-01` diberi **analisis desk-review tambahan** (menelusuri source
Owl `useOnChange`/`propComputed` native + kode modul baris-per-baris, lebih dalam dari Step 8) — lihat
S-06 — yang menyimpulkan risiko kemungkinan besar LEBIH RENDAH dari yang diasumsikan Step 8, TAPI ini
tetap analisis statis, bukan pengganti eksekusi nyata.

---

## Level skenario & Format Skenario

Sama seperti didefinisikan di `migration-tool/templates/10_BUSINESS_FLOW_MIGRATION.md` (Smoke / Main
Flow / Detail / Negative, provenance `[DIKONFIRMASI]`/`[HASIL-BACA]`/`[HASIL-BACA-MURNI]`/
`[PERLU-KEPUTUSAN]`).

---

## Skenario

- [x] Skenario dari AC risiko tinggi (lihat `05a_MIGRATION_ACCEPTANCE_CRITERIA.md`) — S-06, S-07 di
  bawah.
- [x] **Cross-Version Compare** — dijalankan terpisah, lintas-modul (lihat
  `doc-dev/migration_19.0_20.0/doc/CROSS_VERSION_COMPARE.md`, dikerjakan agent sibling terpisah
  sesi ini). Tidak diduplikasi di sini.
- [x] Spot-check integritas data pasca migrasi — **N/A**, Step 7 tidak dikerjakan (asumsi "port kode
  saja", `CLAUDE.md`).
- [x] **Cek multi-dialog/wizard dari satu aksi** — **N/A — dikonfirmasi tidak ada kasus
  multi-dialog.** `pin_message` hanya menambah tombol pin (RPC `toggle_pin` langsung, tanpa dialog)
  dan section collapse/expand (state lokal, bukan dialog/wizard) — tidak ada titik di modul ini yang
  memicu >1 dialog/wizard dari satu aksi user.

---

### S-01: Chatter/message list tetap render normal dengan `pin_message` terinstall (baseline no-crash)
**Level:** Smoke
**Precondition:** Modul `pin_message` terinstall di database QA; ada record apapun dengan chatter
(Contact/Product/dst).
**Mode eksekusi:** AI-interaktif (Playwright MCP) — **BLOCKED, lihat §0**. Fallback: Tour otomatis
Step 9.
**Steps:** Buka form record apapun yang punya chatter → amati chatter render normal (composer, log
note, activity, message list) tanpa error console.
**Expected:** Chatter render sempurna, tidak ada crash/`TypeError`, entry-point pin_message (tombol
pin, section Pinned Messages saat ada data) tidak mengganggu rendering dasar chatter.
**Actual:** Tidak diobservasi live sesi ini (blocked, §0). Bukti tidak langsung: kedua Tour Step 9
(`pin_message_toggle_pin_tour`, `pin_message_action_menu_pin_visible_tour`) berhasil membuka chatter,
posting log note, dan berinteraksi tanpa crash — 0 error console dilaporkan Step 9.
**Status:** [x] Pass
**Provenance:** `[HASIL-BACA — ref: Step 9, run 2026-09-23, "0 failed, 0 error(s) of 7 tests", kedua
banner TOUR ... SUCCEEDED]`

---

### S-02: Expand "Pinned Messages" TANPA crash (regresi `MF-36`, bug paling berbahaya modul ini)
**Level:** Smoke
**Precondition:** Thread dengan minimal 1 pesan `is_pinned=True`.
**Mode eksekusi:** AI-interaktif (Playwright MCP) — **BLOCKED, lihat §0**. Fallback: Tour otomatis
Step 9 (AC-04-01).
**Steps:** Klik header section "Pinned Messages" untuk expand → amati `MessageCardList` render kartu
pesan pinned.
**Expected:** Section expand bersih, TANPA `TypeError: Cannot read properties of undefined (reading
'isSmall')` (crash asli `MF-36` sebelum fix) — ini persis regression test paling kritis di modul ini.
**Actual:** Tidak diobservasi live sesi ini (blocked). Step 9 Tour (`pin_message_toggle_pin_tour`
step 7-8) genuinely mengklik expand dan lolos bersih, 3x re-run konsisten menurut `06c_
IMPLEMENTATION_LOG.md`/Step 9.
**Status:** [x] Pass
**Provenance:** `[HASIL-BACA — ref: Step 9, AC-04-01]`

---

### S-03: Toggle pin/unpin via tombol inline di section Pinned Messages + warna ikon state
**Level:** Main Flow
**Precondition:** Pesan chatter biasa (log note, bukan Discuss/notification/changelog).
**Mode eksekusi:** AI-interaktif (Playwright MCP) — **BLOCKED, lihat §0**. Fallback: Tour Step 9
(AC-02-03, AC-05-02/03).
**Steps:** 1) Klik tombol pin inline pada pesan (ikon `push_pin` abu-abu/`text-muted`) → 2) amati
`is_pinned` ter-flip, ikon berubah `text-primary` → 3) klik lagi untuk unpin.
**Expected:** RPC `toggle_pin` terpanggil, state lokal ter-flip TANPA try/catch (quirk warisan
`AC-02-03`), ikon berubah warna sesuai state (`text-muted`↔`text-primary`), badge count di header
section ikut berubah.
**Actual:** Tidak diobservasi live sesi ini (blocked). Step 9 Tour memverifikasi eksplisit selector
`i[data-icon='push_pin'].text-muted` (step 5) dan `.text-primary` (step 9), badge "1" muncul/hilang
sesuai state.
**Status:** [x] Pass
**Provenance:** `[HASIL-BACA — ref: Step 9, AC-02-03, AC-05-02, AC-05-03]`

---

### S-04: Toggle pin via action-menu "..." + entry "Pin" genuinely terender (regresi `MF-32`)
**Level:** Main Flow
**Precondition:** Pesan chatter yang memenuhi guard `AC-02-04` (bukan discussion/notification/dst).
**Mode eksekusi:** AI-interaktif (Playwright MCP) — **BLOCKED, lihat §0**. Fallback: Tour Step 9
(AC-02-02, AC-02-05).
**Steps:** Buka action-menu "..." pesan → amati entry "Pin" muncul (ikon `push_pin`, bukan kotak
kosong) → klik → amati badge pinned messages bertambah.
**Expected:** Entry "Pin" TERENDER (bukan cuma terdaftar di registry tanpa exception — ini risiko
nyata `MF-32`: `IS_ACTION_DEFINITION_SYM` yang salah pasang lolos tanpa error tapi entry tidak pernah
muncul), klik memicu RPC `toggle_pin` yang sama.
**Actual:** Tidak diobservasi live sesi ini (blocked). Tour `pin_message_action_menu_pin_visible_tour`
genuinely membuka action-menu dan mengecek entry ada (bukan cuma cek tidak ada error) — PASS.
**Status:** [x] Pass
**Provenance:** `[HASIL-BACA — ref: Step 9, AC-02-02, AC-02-05]`

---

### S-05: Badge count section "Pinned Messages" + collapse/expand toggle
**Level:** Main Flow
**Precondition:** Thread dengan N pesan pinned (Tour hanya menguji N=1).
**Mode eksekusi:** AI-interaktif (Playwright MCP) — **BLOCKED, lihat §0**. Fallback: Tour Step 9
(AC-03-02/03, partial).
**Steps:** Pin 1 pesan → amati badge "1" muncul saat collapsed → klik header → amati expand →
klik lagi → collapse.
**Expected:** Badge menampilkan angka N yang benar, caret arah berubah sesuai state
(`arrow_drop_down`/`arrow_right`).
**Actual:** Tidak diobservasi live sesi ini (blocked). Step 9 Tour memverifikasi N=1 dan expand — TAPI
**N>1 dan re-collapse manual via klik header ulang TIDAK pernah diverifikasi terpisah** (dicatat
eksplisit sebagai gap parsial oleh Step 9 sendiri).
**Status:** [x] Pass (untuk N=1 + expand awal) — bagian N>1/re-collapse manual: lihat `03_DETAIL.md`.
**Provenance:** `[HASIL-BACA — ref: Step 9, AC-03-02, AC-03-03]` (partial, sesuai catatan Step 9)

---

### S-06: Refresh section "Pinned Messages" saat ganti thread (`AC-06-01`, `MF-33`/`DIFF-03`) — DIKONFIRMASI LIVE (2026-09-23, sesi terisolasi)

**Level:** Detail *(lihat catatan level di bawah — bukan Smoke/Negative murni, tapi tetap dieskalasi
karena risiko berulang kali ditandai Step 8/9)*
**Precondition:** Chatter terbuka di record A dengan ≥1 pesan pinned; record B (thread lain) tanpa
pesan pinned atau dengan jumlah pinned berbeda.
**Mode eksekusi:** AI-interaktif (Browser pane privat, bukan Playwright MCP yang shared) — dijalankan
di sesi TERPISAH setelah semua sibling agent Step 10/Cross-Version-Compare selesai (lihat `FINDINGS.md`
`MF-46` untuk root cause blocker sebelumnya dan bagaimana ini diatasi: port kedua `8182` ditambah ke
`docker-compose.20.yml`, database baru `pos_margin_sale_migration_20_qa_thread` dengan `pin_message`
sendirian, TIDAK menyentuh DB utama yang filestore-nya corrupt).
**Steps (genuinely dijalankan):** 1) Dua record `res.partner` baru dibuat via RPC (Thread A id=6,
Thread B id=7 — model SAMA PERSIS dengan yang dipakai `pin_message_tour.js`'s Python wrapper, bukan
Discuss channel yang sempat dicoba lebih dulu dan ternyata salah target UI, lihat catatan di
`FINDINGS.md` `MF-46`). 2) Buka chatter Thread A, kirim 1 pesan, pin via menu aksi (`registerMessageAction`
sequence terendah = entry pertama, dikonfirmasi benar milik modul ini — lihat `MF-47` soal kenapa ada
2 entry "Pin"), konfirmasi badge "Pinned Messages (1)" muncul. 3) Navigasi client-side (Owl
`action.doAction({res_model:'res.partner', res_id:7, target:'current'})` — BUKAN full page reload,
breadcrumb mengonfirmasi ini SPA route-change nyata) ke Thread B — badge pinned tidak ada (benar,
B tidak punya pinned). 4) Navigasi client-side balik ke Thread A.
**Expected:** Section ter-refresh benar sesuai thread B, lalu benar lagi saat balik ke A.
**Actual:** **Persis seperti Expected.** Badge "Pinned Messages (1)" muncul kembali dengan benar di
Thread A setelah pulang-pergi ke Thread B, expand section tanpa crash, isi pesan benar (bukan data
basi/tercampur dari thread lain). 0 console error selain noise service-worker yang sudah dikenal
tidak terkait (`Failed to register a ServiceWorker`, muncul di SEMUA sesi Browser pane sejak awal
project, tidak spesifik skenario ini).

**Analisis desk-review TAMBAHAN (lebih dalam dari Step 8, ditelusuri sesi ini via baca source
langsung, BUKAN eksekusi):**
- Native `Chatter.setup()` (`odoo20/addons/mail/static/src/chatter/web_portal_project/chatter.js`)
  memakai **DUA** `useOnChange` terpisah: (a) satu di atas `[this.threadId(), this.threadModel()]` →
  memanggil `changeThread()` yang meng-assign `this.state.thread` ke thread BARU; (b) satu lagi di
  atas `[this.state.thread]` (identity thread berubah) → memanggil `this.load(thread,
  this.initialRequestList)`, yang men-fetch ULANG seluruh pesan thread baru **termasuk field
  `is_pinned`** (sudah dipastikan MF-28 fixed, `_store_message_fields()` mengirim field ini per
  pesan dari server, BUKAN bergantung pada logic `pin_message` sendiri).
- `pinMessage`-nya sendiri (`pin_message/static/src/js/chatter.js`) getter `pinnedMessages` HANYA
  membaca `this.state.thread?.messages.filter(m => m.is_pinned)` — **tidak bergantung pada hasil
  `orm.searchRead`/`forEach` milik `initialLoad()` miliknya sendiri** untuk pesan-pesan yang ADA di
  halaman pertama (paginasi normal) chatter, karena `is_pinned` sudah otomatis terbawa di payload
  store native (MF-28) begitu native men-load ulang pesan thread B lewat mekanisme (b) di atas.
  Artinya: **badge/section untuk kasus umum (pesan pinned masih dalam window paginasi normal)
  kemungkinan besar SUDAH benar-refresh murni lewat mekanisme native sendiri, TERLEPAS dari apakah
  hook `onWillUpdateProps` milik modul ini (yang dipertanyakan Step 8 soal timing) berjalan benar
  atau tidak** — risiko `AC-06-01` kemungkinan LEBIH RENDAH dari kesimpulan Step 8.
- Risiko yang TETAP genuinely terbuka (tidak tertutup analisis di atas): (1) `onWillUpdateProps`
  modul ini membaca `this.props.threadModel`/`this.props.threadId` di `orm.searchRead`-nya sendiri —
  karena `initialLoad()` dipanggil TANPA di-`await` oleh hook (`this.initialLoad()` tanpa `return`),
  Owl tidak menunggu promise ini sebelum melanjutkan reassign props, jadi ADA race window kecil
  (walau kemungkinan besar menang oleh network RPC yang jauh lebih lambat dari microtask reassign
  props) — TIDAK bisa dipastikan 100% tanpa profiling nyata; (2) pesan pinned yang berada DI LUAR
  window paginasi normal thread baru (di luar scope AC-06-01 spesifik, tapi relevan untuk kasus
  thread dengan riwayat panjang) hanya bisa muncul lewat `orm.searchRead` milik modul sendiri, yang
  tetap bergantung pada `this.props`/`this.state.thread` yang sudah benar-benar ter-update ke thread
  baru pada saat `forEach`-nya jalan.
- **Kesimpulan:** turun dari "genuinely tidak diketahui" (Step 8) menjadi "kemungkinan besar benar
  untuk kasus umum, residual risk pada race timing halus + kasus pesan pinned di luar paginasi" —
  TAPI ini TETAP bukan pengganti eksekusi nyata, terutama karena precise microtask/effect ordering
  Owl2 (`signal`/`computed`/`untrack`) tidak sepenuhnya bisa dipastikan dari baca kode statis semata.
**Status:** [x] Pass / [ ] Fail
**Provenance:** `[DIKONFIRMASI]` — eksekusi live genuinely berhasil di sesi terisolasi 2026-09-23.
Lihat `FINDINGS.md` `MF-46` (bagaimana blocker awal diatasi) dan `MF-47` (temuan sampingan: native
20.0 punya fitur pin/unpin sendiri, 2 entry "Pin" muncul di menu — tidak memblokir hasil test ini,
entry milik modul tetap yang pertama/dipakai).

---

### S-07: Tombol "See"/jump ke pesan asli di thread utama (`AC-04-02`)
**Level:** Detail
**Precondition:** Section Pinned Messages ter-expand, ≥1 kartu pesan.
**Mode eksekusi:** AI-interaktif (Playwright MCP) — **BLOCKED, lihat §0.**
**Steps:** Klik tombol "See" pada kartu pesan pinned → amati scroll+highlight ke pesan asli di thread
utama (bukan di section pinned).
**Expected:** Scroll+highlight terjadi TANPA crash, sesuai `BSL-013`.
**Actual:** Tidak bisa dieksekusi live (blocked). **Dikonfirmasi ulang Step 9: TIDAK ADA tour yang
pernah mengklik tombol ini sama sekali** (klaim sebelumnya di `06c_IMPLEMENTATION_LOG.md`/
`08_CODE_REVIEW.md` yang menyebut "sudah lolos Tour" SALAH — dikoreksi Step 9).

**Analisis desk-review tambahan sesi ini:** `message_card_list.xml` modul ini HANYA mengganti tag
`<a>`→`<button>` (xpath `replace`) — `t-on-click="() => this.onClickJump(message)"` memanggil
**method native `onClickJump` APA ADANYA**, tidak di-override modul ini. Ditelusuri ke
`odoo20/addons/mail/static/src/core/common/message_card_list.js:46` — `onClickJump` memanggil
`this.env.messageHighlight?.highlightMessage(message)`, dan `env.messageHighlight` diteruskan lewat
`subEnv` Chatter native (`useMessageScrolling`, tidak disentuh patch `pin_message`). Karena
`pinnedMessages` (kartu di section pinned) dan `thread.messages` (daftar utama) mengacu ke OBJEK
message YANG SAMA (bukan salinan — filter dari array yang sama), highlight+scroll seharusnya bekerja
identik ke pesan aslinya. Risiko rendah berdasar trace ini, TAPI tetap tidak ada bukti eksekusi.
**Status:** [ ] Pass / [ ] Fail — **Pending** (aturan `[HASIL-BACA-MURNI]`: tidak boleh ditandai Pass).
**Provenance:** `[HASIL-BACA-MURNI]` — tidak ada test/tour APAPUN yang mengcover ini, dan eksekusi live
sesi ini blocked. Risiko dinilai RENDAH dari trace di atas (murni wiring ke handler native yang tidak
diubah), tapi jujur dilaporkan sebagai gap bukti, bukan disamarkan Pass.

---

### S-08: `orm.searchRead` gagal saat load pinned messages → error ditelan senyap (`AC-03-04`)
**Level:** Detail
**Precondition:** Simulasi network/server error saat `initialLoad()`.
**Mode eksekusi:** AI-interaktif — **BLOCKED, lihat §0** (dan juga tidak ada tour yang mensimulasikan
error jaringan — area `[NO-SPEC]` sejak Step 5).
**Steps:** (rencana) intercept RPC `searchRead` ini agar reject, amati chatter tetap render normal
tanpa notifikasi ke user.
**Expected:** `console.error('Error loading pinned messages:', error)` terpanggil, tidak ada rethrow,
tidak ada UI notification.
**Actual:** Tidak dieksekusi (tidak ada tool intercept RPC yang disiapkan sesi ini, dan browser
blocked). Logic try/catch dikonfirmasi tidak berubah dari 19.0 (Step 8 desk review, `git diff`
kosong pada blok ini).
**Status:** [ ] Pass / [ ] Fail — **Pending**.
**Provenance:** `[HASIL-BACA-MURNI]` — behavior warisan tanpa perubahan kode, tidak ada test apapun,
risiko dinilai rendah (logic unchanged, bukan area yang disentuh migrasi).

---

### S-09: Styling kosmetik card Pinned Messages (`AC-05-04`) — CSS murni
**Level:** Detail
**Precondition:** Section Pinned Messages ter-expand.
**Mode eksekusi:** AI-interaktif — **BLOCKED, lihat §0.**
**Steps:** (rencana) amati visual background translucent merah-coklat, tanpa border/shadow.
**Expected:** Identik 19.0.
**Actual:** Tidak diobservasi visual live. `style.css` dikonfirmasi TIDAK berubah sama sekali dari
19.0 (Step 8 §B, `03_MIGRATION_SPEC.md` §2c) — tidak ada logic yang bisa gagal.
**Status:** [x] Pass (dari kepastian "file tidak berubah", bukan visual inspection)
**Provenance:** `[HASIL-BACA — ref: Step 8 §C, AC-05-04]`

---

### S-10: Dead-code branch `is_discussion` (quirk warisan `AC-02-01`) — HARUS TETAP tidak tereksekusi untuk fitur chatter modul ini
**Level:** Negative
**Precondition:** Pesan dengan `is_discussion=True`.
**Mode eksekusi:** AI-interaktif — **BLOCKED, lihat §0.**
**Steps:** (rencana) klik pin pada pesan Discuss-channel, amati cabang `messagePinService` (dead code
sejak 18.0) tidak mempengaruhi fitur chatter modul ini.
**Expected:** Tidak ada regresi — behavior ini SENGAJA dipertahankan apa adanya, di luar scope migrasi
(`03_MIGRATION_SPEC.md` §4).
**Actual:** Tidak dieksekusi live. Dikonfirmasi Step 8: cabang ini tetap dead code identik 19.0, tidak
disentuh migrasi apapun.
**Status:** [x] Pass (by design, tidak ada perubahan kode di area ini)
**Provenance:** `[HASIL-BACA — ref: Step 8 §C, AC-02-01]`

---

### S-11: Guard visibility — entry "Pin" TIDAK BOLEH muncul untuk pesan yang tidak memenuhi syarat (`AC-02-04`, jalur negatif)
**Level:** Negative
**Precondition:** Pesan dengan `message_type` `user_notification`/`auto_comment`/`notification`, atau
`is_discussion=True`, atau `subtype_description` terisi (changelog message).
**Mode eksekusi:** AI-interaktif — **BLOCKED, lihat §0.**
**Steps:** (rencana) buka action-menu pesan jenis di atas, DAN cek tombol pin inline di
`pinnedMessages.xml` — pastikan entry "Pin" / tombol pin TIDAK muncul sama sekali di kedua tempat.
**Expected:** Guard (`canAddReaction`, `message_type`, `is_discussion`, `subtype_description`) mencegah
entry muncul — jalur ini adalah satu-satunya bagian `AC-02-04` yang **belum pernah dites otomatis**
(Step 9 hanya menguji jalur POSITIF/qualifies).
**Actual:** Tidak dieksekusi live sesi ini. Guard logic dikonfirmasi Step 8 tidak berubah dari 19.0
(murni getter, bukan method yang di-port migrasi ini) — risiko dinilai rendah, tapi jalur negatif
genuinely belum pernah diverifikasi otomatis di step manapun.
**Status:** [ ] Pass / [ ] Fail — **Pending**.
**Provenance:** `[HASIL-BACA-MURNI]` — tidak ada test/tour yang mengcover jalur negatif ini, live
execution blocked. Risiko rendah (logic unchanged) tapi jujur dilaporkan sebagai gap bukti pada
Level Negative — **direkomendasikan jadi follow-up tour test berikutnya bersamaan `AC-06-01`.**

---

## Ringkasan per Level

| Level | Skenario | Jumlah |
|---|---|---|
| Smoke | S-01, S-02 | 2 |
| Main Flow | S-03, S-04, S-05 | 3 |
| Detail | S-06, S-07, S-08, S-09 | 4 |
| Negative | S-10, S-11 | 2 |

## Rekap Provenance

| Provenance | Jumlah | Skenario |
|---|---|---|
| `[DIKONFIRMASI]` | 1 | S-06 (rerun terisolasi 2026-09-23, lihat `MF-46`) |
| `[HASIL-BACA]` | 7 | S-01, S-02, S-03, S-04, S-05, S-09, S-10 |
| `[HASIL-BACA-MURNI]` | 3 | S-07, S-08, S-11 |
| `[PERLU-KEPUTUSAN]` | 0 | — (S-06 sudah resolved) |

**Catatan hitung:** tabel di atas 11 skenario total (S-01..S-11): 1 `[DIKONFIRMASI]` (S-06), 7
`[HASIL-BACA]` (S-01, S-02, S-03, S-04, S-05, S-09, S-10), 3 `[HASIL-BACA-MURNI]` (S-07, S-08, S-11).

**Kenapa ada `[HASIL-BACA]`/`[HASIL-BACA-MURNI]`/`[PERLU-KEPUTUSAN]` di Level Smoke/Negative:**
- S-01/S-02 (Smoke): tidak dieskalasi ke `[PERLU-KEPUTUSAN]` karena Step 9 **genuinely** membuktikan
  keduanya via Tour otomatis nyata (real Chrome, bukan asumsi) — bukan `[HASIL-BACA-MURNI]` yang
  butuh eskalasi wajib, tapi `[HASIL-BACA]` yang sah merujuk bukti eksekusi step lain.
- S-10 (Negative): behavior dead-code warisan, tidak ada perubahan kode sama sekali — risiko genuinely
  minim, dikonfirmasi diff kosong.
- S-11 (Negative, `[HASIL-BACA-MURNI]`): **ini genuinely gap** — dieskalasi eksplisit sebagai
  follow-up wajib di Verdict di bawah, BUKAN disamarkan sebagai Pass.

---

## Human QA Checklists

Digenerate di `human_qa/` (folder yang sama) — `00_README.md` + `01_SMOKE.md` + `02_MAIN_FLOW.md` +
`03_DETAIL.md` + `04_NEGATIVE.md`, diturunkan dari skenario S-01..S-11 di atas.

---

## Loop-back

**Tidak ada skenario berstatus Fail** di dokumen ini. `S-06` (risiko tertinggi, `AC-06-01`) sudah
`[DIKONFIRMASI]` lewat rerun terisolasi 2026-09-23 — lihat `FINDINGS.md` `MF-46`. 3
`[HASIL-BACA-MURNI]` (S-07, S-08, S-11) masih genuinely belum terbukti via eksekusi nyata, dicatat
sebagai follow-up non-blocking (risiko rendah, sudah didisclosure eksplisit).

## Verdict

- [x] ✅ **Lulus** — semua skenario `[DIKONFIRMASI]`/`[HASIL-BACA]` (bukan `[HASIL-BACA-MURNI]`) sudah
  Pass, termasuk `AC-06-01` (S-06) yang sebelumnya jadi satu-satunya `[PERLU-KEPUTUSAN]` — sekarang
  `[DIKONFIRMASI]` lewat rerun terisolasi (lihat `FINDINGS.md` `MF-46`). 3 `[HASIL-BACA-MURNI]`
  tersisa (S-07 jump button, S-08 empty-state, S-11 negative guard) berisiko RENDAH (behavior warisan/
  logic tidak berubah) — dicatat sebagai follow-up non-blocking, bukan alasan menahan gate.
  **Temuan sampingan (tidak blocking, lihat `FINDINGS.md` `MF-47`):** native 20.0 ternyata punya
  fitur pin/unpin pesan sendiri, berjalan paralel dengan modul custom ini (2 entry "Pin" identik di
  menu aksi) — modul KITA tetap berfungsi benar, tapi ini investigasi arsitektural tambahan untuk
  dev pertimbangkan di luar scope migrasi 1:1 ini.
- [ ] ❌ Ada kegagalan
