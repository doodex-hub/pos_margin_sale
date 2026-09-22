# Migration Acceptance Criteria — pin_message

**Step:** 5 — Acceptance Criteria & Test Plan
**Ref:** `01_intake/pin_message/01b_BASELINE_SPEC.md` dan kode 19.0 yang berjalan (branch
`migration/19.0`) — **bukan** `03_spec/pin_message/03_MIGRATION_SPEC.md`
**Tanggal:** 2026-09-22

> Format Given/When/Then, diturunkan dari `01b_BASELINE_SPEC.md` (dokumentasi behavior modul asli,
> 17 klaim `BSL-001`..`BSL-017`). `03_MIGRATION_SPEC.md` dipakai HANYA sebagai referensi area
> berisiko tinggi (§2b Risk Analysis, `FINDINGS.md` `MF-28`/`MF-32`/`MF-33`/`MF-36`) — kesetaraan
> diukur terhadap 19.0, bukan terhadap rencana migrasi.
>
> **Traceability:** tiap AC menyebut `BSL-NNN` yang diverifikasi. Semua 17 klaim baseline (BSL-001
> s/d BSL-017) tercakup di bawah — lihat §Ringkasan Traceability di akhir dokumen untuk peta lengkap
> dan satu gap traceability yang ditemukan (field `is_pinned` sendiri tidak punya BSL-NNN dedicated).

---

## AC-01 — Toggle pin/unpin & persistensi server-side (`mail.message.toggle_pin()`)

**AC-01-01** (verifies `BSL-001`, `BSL-006`)
Given sebuah `mail.message` (log note/comment) dengan `is_pinned=False`
When `toggle_pin()` dipanggil pada message tersebut (via RPC dari client manapun)
Then `is_pinned` menjadi `True`, `bus.bus._sendone(f'{self._name},{message.id}',
'mail.message/pin_changed', {'id': ..., 'is_pinned': True})` di-broadcast per-message, method
mengembalikan `True`, dan tidak ada side effect lain di luar broadcast bus tersebut (tidak menulis
field lain, tidak trigger workflow lain).

**AC-01-02** (verifies `BSL-001`)
Given sebuah `mail.message` dengan `is_pinned=True`
When `toggle_pin()` dipanggil
Then `is_pinned` menjadi `False` dan broadcast bus terkirim dengan `is_pinned: False`.

**AC-01-03** (verifies `BSL-001`)
Given dua atau lebih `mail.message` sekaligus dipanggil sebagai satu recordset (`batch.toggle_pin()`)
When method dieksekusi
Then setiap message di-flip secara independen (loop `for message in self:`) TANPA error
"Expected singleton" atau efek silang antar-record — aman untuk multi-record, kontras eksplisit
dengan bug `F-05`/`MF-08` (singleton-assumption crash) di modul `sale_margin_threshold`.

**AC-01-04** (verifies `BSL-007`) — **RISIKO TINGGI, WAJIB TEST** (ref `FINDINGS.md` `MF-28`,
`03_MIGRATION_SPEC.md` §2b Critical Blocker #2)
Given sebuah message dengan `is_pinned=True` di database
When payload store frontend untuk message tersebut dibentuk (mis. saat chatter memuat pesan, method
`_store_message_fields(self, res, **kwargs)` di 20.0)
Then field `is_pinned` genuinely muncul di payload yang dikirim ke client (via `res.attr("is_pinned")`
setelah `super()._store_message_fields(res, **kwargs)`), BUKAN cuma "tidak ada error" — kegagalan di
20.0 untuk area ini bersifat SENYAP (chatter tetap render normal tanpa field ini, tanpa exception),
jadi verifikasi harus eksplisit inspeksi payload/state Owl, bukan cuma observasi absennya error
console.

---

## AC-02 — Dua entry-point UI untuk trigger pin/unpin

**AC-02-01** (verifies `BSL-002`, `BSL-016`) — quirk warisan, PERTAHANKAN apa adanya
Given sebuah pesan dengan `is_discussion=True` (pesan Discuss-channel)
When user klik tombol pin lewat `onClickPin()` (`message.js`)
Then kode masuk cabang `this.messagePinService.getPinnedAt/unpin/pin` — **dead code sejak 18.0**,
service ini dipakai implisit tanpa import eksplisit di modul, dan cabang ini tidak pernah benar-benar
tereksekusi untuk fitur pin chatter modul ini (tidak ada fitur hilang untuk end-user). Perilaku ini
harus dipertahankan identik (bukan dibersihkan) — di luar scope migrasi ini per `03_MIGRATION_SPEC.md`
§4 "Di Luar Scope".

**AC-02-02** (verifies `BSL-002`)
Given sebuah pesan dengan `is_discussion=False` (chatter/log-note biasa)
When user klik tombol pin lewat `onClickPin()` (action-menu "...")
Then client memanggil RPC `orm.call("mail.message", "toggle_pin", [[id]])`, flip `is_pinned` lokal
di props setelah sukses, dan kegagalan RPC ditangani via try/catch (`console.error`, TIDAK dilempar
ulang ke UI) — behavior try/catch ini harus identik 19.0.

**AC-02-03** (verifies `BSL-003`, `BSL-015`)
Given sebuah pesan chatter biasa
When user klik tombol pin inline di `pinnedMessages.xml` lewat `onMessagePin()` (`message.js`)
Then client memanggil RPC `toggle_pin` yang SAMA, flip `is_pinned` lokal, TANPA percabangan
`is_discussion` DAN TANPA try/catch (beda eksplisit dari `onClickPin()`/AC-02-02 — divergensi ini
adalah quirk warisan yang harus dipertahankan, bukan disatukan/diperbaiki).

**AC-02-04** (verifies `BSL-004`, `BSL-012`)
Given berbagai jenis pesan di chatter (log note, `user_notification`, `auto_comment`,
`notification`, pesan Discuss, changelog message dengan `subtype_description` terisi)
When action-menu "..." pesan dibuka DAN tombol pin inline dievaluasi
Then entry "Pin" di action-menu HANYA muncul untuk pesan yang: `canAddReaction(thread)` true, BUKAN
discussion, `message_type` BUKAN salah satu dari `user_notification`/`auto_comment`/`notification`,
DAN `subtype_description` kosong — tombol pin inline (`pinnedMessages.xml`) memakai guard field yang
sama (`message_type`/`is_discussion`/`thread?.model !== 'mail.activity.thread'`); untuk pesan yang
tidak memenuhi syarat, kedua entry (action-menu dan tombol inline) TIDAK ditampilkan sama sekali.

**AC-02-05** (verifies `BSL-005`) — **RISIKO TINGGI, WAJIB TEST** (ref `FINDINGS.md` `MF-32`,
`03_MIGRATION_SPEC.md` §2b Critical Blocker #3)
Given entry "Pin" terdaftar di message action registry
When action-menu pesan yang memenuhi syarat AC-02-04 dibuka
Then entry "Pin" benar-benar TERENDER di UI (bukan cuma terdaftar tanpa error) — di 20.0, registrasi
lewat `registerMessageAction()` yang tidak dipasang Symbol `IS_ACTION_DEFINITION_SYM` yang benar akan
LOLOS tanpa exception tapi TIDAK PERNAH muncul di action-menu manapun. Verifikasi harus eksplisit
klik-buka action-menu dan cek entry ada, bukan cuma cek tidak ada `TypeError` dari getter
`canAddReaction`.

---

## AC-03 — Section "Pinned Messages": visibility, badge count, initial load

**AC-03-01** (verifies `BSL-008`, `BSL-009`, `BSL-011`)
Given sebuah thread (record chatter apapun) TANPA pesan pinned
When chatter dimuat (`onMounted`)
Then `initialLoad()` berjalan (`this.load(state.thread, ["messages"])` + `orm.searchRead` khusus
`is_pinned=True` di-scope `model=threadModel`+`res_id=threadId`, urut `date DESC`), section "Pinned
Messages" TIDAK ditampilkan (`t-if="pinnedMessages.length > 0"` false).

**AC-03-02** (verifies `BSL-009`, `BSL-011`)
Given sebuah thread dengan N pesan `is_pinned=True`
When chatter dimuat atau di-refresh
Then section "Pinned Messages" muncul (posisi `after` topbar chatter) dengan badge menampilkan angka
N yang benar, di state collapsed secara default (`state.showPinnedMessages=false`).

**AC-03-03** (verifies `BSL-009`)
Given section "Pinned Messages" dalam keadaan collapsed atau expanded
When user klik header section (`togglePinnedMessages()`)
Then state collapse/expand ter-toggle (caret berubah arah sesuai state — lihat AC-05 untuk detail
ikon).

**AC-03-04** (verifies `BSL-010`) — area `[NO-SPEC]`, baru terdokumentasi sesi ini
Given `orm.searchRead` untuk memuat pesan pinned GAGAL (mis. error jaringan/server)
When `initialLoad()` mencoba memuat pinned messages
Then error ditangkap via try/catch, `console.error('Error loading pinned messages:', error)`
dipanggil, TIDAK dilempar ulang — chatter tetap render normal (pesan biasa tetap muncul) tanpa
notifikasi visual ke user bahwa pinned messages gagal dimuat. Perilaku non-obvious ini harus
dipertahankan identik (bukan ditambah notifikasi baru — itu perubahan UX yang butuh persetujuan
eksplisit terpisah).

---

## AC-04 — Expand/collapse section + jump-to-message navigation

> **RISIKO TERTINGGI DI DOKUMEN INI.** Area ini adalah AC eksplisit untuk `MF-36`
> (`FINDINGS.md` — crash nyata saat expand "Pinned Messages" di 20.0, root cause bug bare-identifier
> `ui.isSmall` di `message_card_list.xml`, RESOLVED 2026-09-22 tapi HANYA diverifikasi manual via
> browser, belum via tour otomatis yang benar-benar mengeksekusi klik tombol "See"). **WAJIB jadi
> bagian eksekusi nyata Step 9/10, jangan dianggap selesai dari baca kode/log implementasi saja.**

**AC-04-01** (verifies `BSL-011`)
Given section "Pinned Messages" berisi minimal satu pesan pinned
When user klik header untuk expand section
Then section expand TANPA crash/exception apapun di console, menampilkan
`<MessageCardList messages="pinnedMessages" thread="state.thread" mode="'extended'"
showEmpty="false"/>` berisi satu card per pesan pinned. **Ini persis skenario yang pernah crash total
(`TypeError: Cannot read properties of undefined (reading 'isSmall')`) sebelum fix `MF-36` —
regression test paling kritis di dokumen ini.**

**AC-04-02** (verifies `BSL-013`)
Given section "Pinned Messages" ter-expand dengan minimal satu card pesan
When user klik tombol "See" custom (`onClickJump(message)`, pengganti tombol "Jump" native lewat
xpath `replace` di `message_card_list.xml`)
Then tampilan scroll dan highlight ke pesan asli di thread utama chatter (bukan di section pinned),
TANPA crash. Tombol ini adalah hasil `position="replace"` terhadap
`//a[contains(@class,'o-mail-MessageCard-jump')]` native (selector `<a>`, bukan `<button>` — fix
warisan sejak generasi 17→18, dikonfirmasi ulang masih berlaku di 20.0).

**Catatan traceability:** tidak ada `BSL-NNN` khusus yang mendeskripsikan hasil visual "scroll +
highlight" tombol jump secara presisi (baseline hanya menyebut "tombol custom 'See'" di `BSL-013`) —
ini bukan gap kritis (behavior tombol jump/scroll adalah bawaan `mail.MessageCardList` native, modul
ini hanya mengganti elemen `<a>`→`<button>`), tapi dicatat untuk kelengkapan.

---

## AC-05 — Ikon & state visual (FontAwesome → Odoo Icons, `DIFF-04`)

**AC-05-01** (verifies `BSL-017`)
Given entry "Pin" di action-menu pesan yang memenuhi syarat AC-02-04
When action-menu dibuka
Then ikon entry tampil sebagai `push_pin` (Odoo Icons, `<i class="oi" data-icon="push_pin">` di
20.0) — TIDAK boleh tampil kotak kosong/placeholder. Ini perubahan bentuk render (FontAwesome →
Odoo Icons, `DIFF-04`) TANPA perubahan business rule — outcome visual (ikon pin terlihat) harus
identik ke 19.0 meski implementasi berbeda.

**AC-05-02** (verifies `BSL-017`)
Given tombol pin inline di `pinnedMessages.xml`, state pesan BELUM pinned
When tombol dirender
Then ikon tampil dengan warna muted/`text-muted` (state "belum di-pin").

**AC-05-03** (verifies `BSL-017`)
Given tombol pin inline, state pesan SUDAH pinned
When tombol dirender
Then ikon tampil dengan warna primary/`text-primary` (state "sudah di-pin") — kontras visual dari
AC-05-02 harus tetap jelas terlihat sama seperti 19.0.

**AC-05-04** (verifies `BSL-014`)
Given section "Pinned Messages" atau card di dalamnya
When dirender
Then styling kosmetik (`.o-mail-PinnedMessages .card`/`.card-body`, background translucent
merah-coklat `rgba(165,42,42,0.1)`, tanpa border/shadow) identik 19.0 — murni CSS, tidak ada logic
yang bisa gagal, tapi tetap dicek visual sebagai bagian regresi tampilan.

---

## AC-06 — Refresh section "Pinned Messages" saat ganti thread (patch `Chatter`)

> **RISIKO TINGGI, BELUM PERNAH DIBUKTIKAN LEWAT TOUR OTOMATIS.** Area ini adalah AC eksplisit
> untuk risiko `MF-33`/`DIFF-03` yang **masih outstanding** menurut
> `06_implementation/pin_message/06c_IMPLEMENTATION_LOG.md` §"Belum diterapkan / masih terbuka":
> *"Tour test 'pindah thread' untuk MF-33 ... verifikasi manual sudah dilakukan tapi tour test
> otomatis formal belum ditulis."* `03_MIGRATION_SPEC.md` §2b sendiri menyatakan ini sebagai syarat
> WAJIB sebelum fase E (Step 6) modul ini ditutup — **belum terpenuhi**, lihat §Test Plan (05b)
> untuk rekomendasi konkret.

**AC-06-01** (verifies `BSL-008`, `BSL-009`)
Given chatter terbuka di record A dengan satu atau lebih pesan pinned
When user berpindah ke record B (record lain, BUKAN reload record A yang sama) lewat form view,
sehingga `threadId`/`threadModel` berubah
Then `onWillUpdateProps` hook modul ini ter-trigger, memanggil ulang `initialLoad()`, dan section
"Pinned Messages" ter-refresh sesuai thread B: KOSONG kalau B tidak punya pesan pinned (bukan
menampilkan sisa data pesan pinned dari thread A), atau menampilkan badge count yang benar sesuai
jumlah pesan pinned B kalau ada.

**Catatan risiko (bukan bagian AC, konteks untuk penguji):** native 20.0
(`@mail/chatter/web_portal_project/chatter.js`) sekarang punya mekanisme reload otomatis sendiri
lewat `useOnChange` berbasis signal, TIDAK lagi mengandalkan `onWillUpdateProps` mentah seperti yang
dipakai modul ini. Ada kemungkinan hook modul ini tidak lagi ter-trigger dengan timing yang benar
terhadap thread baru — kalau demikian, dampaknya SPESIFIK ke AC-06-01 (pesan lain di chatter tetap
refresh normal lewat mekanisme native, HANYA section Pinned Messages yang stale/tidak ikut refresh)
dan bersifat silent (tidak ada error). `03_MIGRATION_SPEC.md` §1 butir 4 eksplisit menyatakan ini
"TIDAK bisa dipastikan dari baca kode statis" — **hanya eksekusi nyata (tour multi-thread) yang bisa
menjawab.**

---

## Ringkasan Traceability

| `BSL-NNN` | AC yang memverifikasi |
|---|---|
| BSL-001 | AC-01-01, AC-01-02, AC-01-03 |
| BSL-002 | AC-02-01, AC-02-02 |
| BSL-003 | AC-02-03 |
| BSL-004 | AC-02-04 |
| BSL-005 | AC-02-05 |
| BSL-006 | AC-01-01 |
| BSL-007 | AC-01-04 |
| BSL-008 | AC-03-01, AC-06-01 |
| BSL-009 | AC-03-01, AC-03-02, AC-03-03, AC-06-01 |
| BSL-010 | AC-03-04 |
| BSL-011 | AC-03-01, AC-03-02, AC-04-01 |
| BSL-012 | AC-02-04 |
| BSL-013 | AC-04-02 |
| BSL-014 | AC-05-04 |
| BSL-015 | AC-02-03 |
| BSL-016 | AC-02-01 |
| BSL-017 | AC-05-01, AC-05-02, AC-05-03 |

**Cakupan:** 17/17 klaim `BSL-NNN` tercakup minimal satu AC. Tidak ada AC yang tidak bisa dipetakan
ke `BSL-NNN` manapun.

**Gap traceability yang ditemukan (dilaporkan, bukan diperbaiki di dokumen ini):**
- Field `is_pinned` sendiri (`Boolean`, `default=False`, `index=True`, §3 `01b_BASELINE_SPEC.md`)
  tidak punya `BSL-NNN` dedicated — hanya disebut sebagai bagian deskripsi model di §2/§3, dirujuk
  implisit lewat `BSL-007` (yang membahas *pengiriman* field ke store, bukan *definisi* field itu
  sendiri). AC-01-04 memakai `BSL-007` sebagai rujukan terdekat, tapi klaim spesifik "field ini
  `index=True`" tidak punya AC tersendiri karena tidak ada BSL-NNN yang mengklaimnya secara eksplisit
  sebagai behavior yang harus diverifikasi (index adalah detail performa, bukan behavior yang
  teramati user) — dianggap cukup diverifikasi tidak langsung lewat AC-01-01..04, tidak
  dieskalasi balik ke Step 1.
- **AC-04-02** (tombol jump/"See") dan **AC-06-01** (thread-switch) adalah dua AC dengan risiko
  tertinggi di dokumen ini (`MF-36`, `MF-33`) yang verifikasinya SAH terhadap `BSL-013`/`BSL-008`/
  `BSL-009` tapi **belum pernah dibuktikan via test otomatis** — lihat `05b_TEST_PLAN_MIGRATION.md`
  untuk rekomendasi konkret menutup gap ini di Step 9.
