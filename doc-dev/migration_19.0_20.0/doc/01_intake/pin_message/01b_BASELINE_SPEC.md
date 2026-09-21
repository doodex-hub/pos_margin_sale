# Baseline Spec — pin_message

**Step:** 1 — Intake & Scope (pelengkap `01a_MIGRATION_INTAKE.md`)
**Tujuan:** dokumentasikan APA yang modul lakukan (behavior as-is) di 19.0 (branch `migration/19.0`,
identik dengan working tree `migration/20.0` saat dokumen ini ditulis — belum ada edit migrasi).
**Tanggal:** 2026-09-21
**Sumber:** Direkonsiliasi dari baseline spec project migrasi sebelumnya
(`doc-dev/migration_18.0_19.0/doc/01_intake/pin_message/01b_BASELINE_SPEC.md`, 18.0→19.0) +
cross-check penuh ke kode 19.0 aktual (baca seluruh file Python/JS/XML modul) +
`doc-dev/migration_18.0_19.0/doc/FINDINGS.md` (khususnya `MF-09`, `MF-10`, `MF-14`, `MF-15`, `MF-18`,
`MF-25`..`MF-27`) + `doc-dev/migration_19.0_20.0/doc/FINDINGS.md` (dikonfirmasi tidak ada finding
`pin_message` yang masih terbuka dibawa ke project ini — lihat §Ringkasan).

> Dokumen lama (18.0→19.0) berperan sebagai baseline spec pengganti `FUNCTIONAL_SPEC.md` (modul ini
> tidak pernah punya file itu) — bukan sumber kebenaran, kode 19.0 aktual yang menang. Provenance
> merujuk ke `(ref: 18.0→19.0 BSL-NNN)`; kalau dokumen 18.0→19.0 sendiri mewarisi dari 17.0→18.0,
> rujukan gandanya (`17-18/BSL-NNN`, `17-18/MF-NNN`) tetap dipertahankan apa adanya di teks klaim
> supaya jejak audit lengkap sampai ke asal-usulnya.

---

## Provenance Tag

Tag yang dipakai di dokumen ini: `[MATCH]` (klaim baseline lama cocok dengan kode 19.0 aktual),
`[GAP]` (baseline lama menyimpang dari kode aktual — kode menang, penyimpangan dicatat dua baris),
`[NO-SPEC]` (topik tidak/tidak sepenuhnya dibahas dokumen manapun, murni dari baca kode). Lihat
`migration-tool/templates/01b_BASELINE_SPEC.md` untuk definisi lengkap.

---

## Ringkasan untuk Review — Perlu Konfirmasi User

**Tally provenance:** 12 klaim `[MATCH]`, 2 `[GAP]`, 3 `[NO-SPEC]` (total 17 klaim, `BSL-001`..`BSL-017`).

- **`[BSL-007]` `[GAP]` (ref: 18.0→19.0 BSL-006) — override `_to_store()`.** Baseline lama (ditulis
  2026-08-26, SEBELUM fix `MF-14`/`MF-18` migrasi 18.0→19.0 landed) mendeskripsikan signature
  `_to_store(self, store, **kwargs)` + `super()._to_store(store, **kwargs)` + loop
  `store.add(message, {'is_pinned': ...})` per message. **Kode aktual sekarang** (SESUDAH fix):
  `_to_store(self, store, fields, **kwargs)` + `super()._to_store(store, fields, **kwargs)` +
  `store.add_records_fields(self, ['is_pinned'])` (batched, tanpa loop manual). Kode aktual yang
  menang dan harus dipertahankan identik ke 20.0 — TAPI lihat `01a_MIGRATION_INTAKE.md` §2b: ada
  indikasi kuat mekanisme `_to_store()` ini sendiri sudah tidak ada lagi di native 20.0, jadi override
  ini kandidat rewrite besar di Step 2/6, bukan sekadar "port apa adanya".
- **`[BSL-005]` `[GAP]` (ref: 18.0→19.0 BSL-004, BSL-010) — bentuk callback `messageActionsRegistry`.**
  Baseline lama mendeskripsikan mekanisme era-18.0 (akses `component.message`/`component.props.thread`,
  penamaan callback tersirat `onClick`, "SUDAH BENAR" merujuk fix `MF-24` yang justru soal HAL LAIN
  — method vs getter). **Kode aktual sekarang** (SESUDAH fix `MF-15`): callback destructure langsung
  `({ message, thread })`/`({ owner })`, TIDAK ADA `.props` sama sekali, key registry `name`/
  `onSelected`. Kode aktual menang. Sama seperti `BSL-007` — perlu diverifikasi ulang penuh ke 20.0
  di Step 2, jangan diasumsikan stabil.
- **Dua area di atas adalah PERSIS dua gap kritis (`MF-14`/`_to_store`, `MF-15`/`messageActionsRegistry`)
  yang ditemukan migrasi 18.0→19.0 sebelumnya** — modul ini dikonfirmasi ulang sebagai yang paling
  rapuh di project, treat kedua pola registry/override ini dengan kecurigaan ekstra di Step 2 untuk
  pasangan 19.0→20.0 juga, jangan berasumsi "sudah pernah diperbaiki sekali jadi otomatis aman".
- `[BSL-002]`/`[BSL-016]`/`[BSL-017]` `[MATCH][DIWARISI-SOURCE]` — tiga quirk warisan (cabang
  `is_discussion` dead code, `this.messagePinService` implisit, dua entry-point UI yang rawan
  divergen) dikonfirmasi ULANG masih ada persis di kode 19.0 saat ini. Pertahankan as-is ke 20.0.
- `[BSL-010]`/`[BSL-012]`/`[BSL-017]` `[NO-SPEC]` — tiga detail yang baru pertama kali didokumentasikan
  di sini (error-handling `initialLoad()`, field guard `message_type`/`thread?.model` di
  `pinnedMessages.xml`, pilihan class ikon Font Awesome) — semuanya berasal dari fix pasca-baseline
  lama (`MF-25`/`MF-26`/`MF-27`, di-port dari `migration/18.0` commit `82e25af` SETELAH baseline lama
  ditulis). Tidak ada kontradiksi dengan dokumen manapun (topiknya memang belum pernah dibahas
  eksplisit), tapi tetap tandai risiko lebih tinggi karena belum pernah "dicek dua kali".
- **Dikonfirmasi:** `MF-10` (console.log leftover, dulu masih terbuka di baseline 18.0→19.0) sudah
  dibersihkan (keputusan user 2026-08-27, project 18.0→19.0) — TIDAK ada di kode 19.0 saat ini,
  TIDAK dikembalikan oleh fix `MF-25`..`MF-27` manapun. `MF-14`/`MF-15`/`MF-18` (dua gap kritis +
  satu gap turunan infinite-recursion) juga dikonfirmasi RESOLVED, tercermin di `BSL-005`/`BSL-007`
  di atas. Ketiganya juga dikonfirmasi TIDAK muncul sebagai finding terbuka di
  `doc-dev/migration_19.0_20.0/doc/FINDINGS.md` (hanya `MF-08`/`20`/`21`/`23`/`24` — milik
  `pos_margin_threshold`/`sale_margin_threshold`, tidak ada satupun untuk `pin_message` — dikonfirmasi
  eksplisit sesi ini) — bukan regresi diam-diam, murni kode yang sudah dalam kondisi ter-fix.

---

## 1. Tujuan Modul

Menambahkan kemampuan "pin" pesan/log-note di chatter Odoo — independen dari mekanisme pin native
Discuss-channel. User bisa menandai pesan penting (via tombol inline per-pesan ATAU entry di
action-menu "..." pesan) supaya muncul di section collapsible "Pinned Messages" di bagian atas
chatter, dengan badge jumlah. Toggle pin/unpin sinkron realtime lewat bus. Behavior ini identik sejak
generasi migrasi 17.0→18.0, dipertahankan tanpa perubahan lewat 18.0→19.0.

## 2. Model & Tanggung Jawab

| Model | Tanggung Jawab |
|---|---|
| `mail.message` (extend) | Field `is_pinned`, method `toggle_pin()`, override `_to_store()` untuk mengirim `is_pinned` ke frontend. |

Tidak ada model lain — modul ini hanya menyentuh satu model Python, sisanya murni client-side
(patch Owl + QWeb template).

## 3. Field dengan Makna Bisnis

### `mail.message`
- `is_pinned` (Boolean, `default=False`, `index=True`) — menandai pesan/log-note sebagai "pinned",
  independen dari pin native Discuss-channel.

## 4. Business Workflow / State Transition

- `[BSL-001]` `[MATCH]` (ref: 18.0→19.0 BSL-001) `toggle_pin()` — method di `mail.message`, dipanggil
  lewat RPC dari DUA entry-point client berbeda (lihat `BSL-016`). Loop `for message in self:` (aman
  multi-record — dikonfirmasi ulang lewat test `test_toggle_pin_multi_record_safe`), flip
  `is_pinned`, broadcast per-message via
  `bus.bus._sendone(f'{self._name},{message.id}', 'mail.message/pin_changed', {...})` untuk sinkron
  realtime UI. Return `True`.
- `[BSL-002]` `[MATCH][DIWARISI-SOURCE]` (ref: 18.0→19.0 BSL-002, 17-18/MF-09) `onClickPin()`
  (`message.js`) bercabang berdasarkan `this.message.is_discussion`:
  - `True` (pesan Discuss-channel) → delegasi ke `this.messagePinService` (service implisit, tidak
    diimpor eksplisit di modul ini): `getPinnedAt(id)`/`unpin(message)`/`pin(message)`. **Dead code
    sejak 18.0** — native Discuss-channel pin sekarang berjalan lewat mekanisme lain, method ini
    tidak pernah benar-benar terpanggil untuk jalur ini. Dikonfirmasi harmless (tidak ada fitur
    hilang untuk end-user), dikonfirmasi ULANG masih persis sama di kode 19.0 saat ini.
  - `False` (chatter/log-note biasa) → RPC `orm.call("mail.message", "toggle_pin", [[id]])`, lalu
    flip `is_pinned` lokal di props, wrapped try/catch (`console.error` kalau gagal, tidak
    dilempar ulang).
- `[BSL-003]` `[MATCH]` (ref: 18.0→19.0 BSL-003) `onMessagePin()` (`message.js`) — entry-point KEDUA,
  TANPA percabangan `is_discussion` sama sekali, selalu RPC + flip lokal (tanpa try/catch, beda dari
  `onClickPin()` — perbedaan ini sudah ada sejak baseline lama, bukan temuan baru).
- `[BSL-004]` `[MATCH]` (ref: 18.0→19.0 BSL-004) Business rule visibility entry "Pin" di action-menu
  (`messageActionsRegistry.add("pins", ...)`, sequence 15): hanya muncul kalau `canAddReaction(thread)`
  true (method di model `message`, lihat `BSL-005`), pesan BUKAN discussion DAN `message_type` bukan
  `user_notification`/`auto_comment`/`notification`, DAN `subtype_description` kosong (bukan
  changelog message). Business rule ini identik dengan baseline lama — hanya BENTUK
  callback/registrasinya yang berubah (lihat `BSL-005`).
- `[BSL-005]` `[GAP]` (ref: 18.0→19.0 BSL-004, BSL-010) **Bentuk callback registrasi
  `messageActionsRegistry`.**
  **Spec lama:** callback `condition` diakses via `component.message.canAddReaction(component.props.thread)`
  (component Owl asli, lewat `.props`); entry di registry disebut dipanggil oleh `onClick` (implisit
  dari deskripsi "`onClick` memanggil `onClickPin()`" — konsisten mekanisme pra-fix `MF-15`, 18.0-style).
  **Kode aktual:** `condition: ({ message, thread }) => { if (!message.canAddReaction(thread))
  return false; ... }` — destructure langsung objek `{message, thread}`, TIDAK ADA `.props` sama
  sekali; key registrasi `name: _t("Pin")` (bukan `title`) dan `onSelected: ({ owner }) =>
  owner.onClickPin()` (bukan `onClick`). Ini adalah bentuk PASCA-FIX `MF-15` (migrasi 18.0→19.0,
  Step 2/6) — baseline lama ditulis SEBELUM fix ini landed, jadi mendeskripsikan mekanisme yang
  sudah tidak berlaku. Outcome bisnis (kapan entry "Pin" muncul, apa yang terjadi saat diklik)
  identik — yang berubah murni bentuk integrasi ke registry core. **Wajib re-verifikasi penuh ke
  20.0 di Step 2** (lihat `01a_MIGRATION_INTAKE.md` §2b/Ringkasan) — riwayat migrasi sebelumnya
  membuktikan titik ini paling rawan berubah lagi.

## 5. Server-Side Logic dengan Side Effect

- `[BSL-006]` `[MATCH]` (ref: 18.0→19.0 BSL-005) `toggle_pin()` tidak punya side effect lain di luar
  bus broadcast (§4).
- `[BSL-007]` `[GAP]` (ref: 18.0→19.0 BSL-006) **Signature `_to_store()` + mekanisme penambahan
  field ke store.**
  **Spec lama:** `def _to_store(self, store, **kwargs)`; `super()._to_store(store, **kwargs)`
  dipanggil dulu (extend); lalu untuk tiap message: `store.add(message, {'is_pinned':
  message.is_pinned})` (raw dict nilai konkret, jalur pintas 18.0).
  **Kode aktual:** `def _to_store(self, store, fields, **kwargs)` (`fields` sekarang parameter
  positional wajib, bukan lagi keyword-only opsional); `super()._to_store(store, fields, **kwargs)`;
  lalu `store.add_records_fields(self, ['is_pinned'])` (dipanggil SEKALI untuk seluruh `self`, tidak
  loop manual per message, dan TIDAK memakai `store.add()` dengan dict nilai konkret — 19.0 core
  tidak punya jalur pintas itu lagi, akan infinite-recurse kalau dipakai dari dalam `_to_store()`
  sendiri, lihat riwayat `MF-14`/`MF-18`). Kode aktual (pasca-fix) yang harus dipertahankan identik
  ke 20.0 — TAPI lihat `01a_MIGRATION_INTAKE.md` §2b/Ringkasan poin 2: preliminary check native 20.0
  (`odoo20/addons/mail/models/mail_message.py`) menunjukkan method `_to_store()` itu sendiri
  kemungkinan besar sudah tidak ada lagi (diganti pola `_store_message_fields()`/`Store.FieldList`)
  — kandidat rewrite arsitektural di Step 2/6, bukan port apa adanya.

## 6. Client-Side Behavior (Views, JS, Owl)

### `chatter.js` (patch `Chatter.prototype`)
- `[BSL-008]` `[MATCH]` (ref: 18.0→19.0 BSL-007) `setup()`: `super.setup()` + inject
  `orm`/`notification`, tambah `state.showPinnedMessages=false`, `onMounted`+`onWillUpdateProps`
  hook (trigger ulang saat `threadId`/`threadModel` berubah) memanggil `initialLoad()`. Import path
  `Chatter` dikonfirmasi ULANG `@mail/chatter/web_portal/chatter` (fix `MF-12` warisan masih berlaku,
  path lama `@mail/core/web/chatter` tidak dipakai).
- `[BSL-009]` `[MATCH]` (ref: 18.0→19.0 BSL-008) `initialLoad()`: panggil `this.load(state.thread,
  ["messages"])` (method inti, TIDAK di-override), lalu `orm.searchRead` terpisah untuk
  `mail.message` ber-`is_pinned=True`, di-scope ke `model=threadModel`+`res_id=threadId`, urut
  `date DESC`, stamp ke in-memory messages yang sudah ada di `state.thread.messages`. Getter
  `pinnedMessages` filter dari situ; `togglePinnedMessages()` flip state collapse/expand.
  `Chatter.components` diperluas dengan `MessageCardList`.
- `[BSL-010]` `[NO-SPEC]` (ref: —) **Error handling `initialLoad()`.** Baseline lama tidak merinci
  perilaku kalau `orm.searchRead` gagal. Kode aktual: seluruh blok `searchRead`+stamping dibungkus
  `try/catch`; kalau gagal, `console.error('Error loading pinned messages:', error)` dipanggil,
  TIDAK dilempar ulang (chatter tetap render tanpa pinned messages termuat, tidak ada notifikasi
  visual ke user). Perilaku non-obvious, murni dari baca kode langsung — belum pernah didokumentasikan
  di generasi manapun sebelumnya.

### `message.js` (patch `Message.prototype`)
- Lihat `BSL-002`/`BSL-003` di §4.

### Template QWeb
- `[BSL-011]` `[MATCH]` (ref: 18.0→19.0 BSL-011, bagian `mail.Chatter`) `pinnedMessages.xml`:
  `t-inherit` ke `mail.Chatter`, xpath `o-mail-Chatter-topbar` position `after`, insert section
  collapsible (`t-if="pinnedMessages.length > 0"`) + header klik-toggle (caret + badge jumlah kalau
  collapsed) + `<MessageCardList messages="pinnedMessages" thread="state.thread" mode="'extended'"
  showEmpty="false"/>` saat expanded.
- `[BSL-012]` `[NO-SPEC]` (ref: 18.0→19.0 BSL-011 bagian `mail.Message`, topik umum saja — cross-ref
  `17-18/`→`MF-27`) **Field guard tombol pin inline.** Baseline lama hanya menyebut guard secara
  umum ("menghindari tipe notification/discussion/mail.activity.thread") tanpa merinci nama field
  JS yang dipakai. Kode aktual: `t-if="props.message.message_type !== 'notification' and
  props.message.message_type !== 'auto_comment' and props.message.message_type !==
  'user_notification' and !props.message.is_discussion and props.message.thread?.model !==
  'mail.activity.thread'"` (xpath `o-mail-Message-author` position `after`), memanggil
  `onMessagePin(props.message.id)` (`BSL-003`). Field `message_type`/`thread?.model` ini adalah hasil
  fix `MF-27` (di-port dari `migration/18.0` commit `82e25af`, SETELAH baseline lama ditulis) — versi
  sebelum fix memakai atribut `message.type`/`message.model` yang sudah mati sejak 18.0 (silent-fail,
  filter jenis-pesan tidak pernah benar-benar bekerja). Karena baseline lama tidak merinci nama field
  spesifik (bukan kontradiksi tekstual langsung), diklasifikasi `[NO-SPEC]` bukan `[GAP]` — tapi
  tetap high-risk untuk diverifikasi ulang di Step 2 (nama field mail lain juga rawan berubah antar
  versi major).
- `[BSL-013]` `[MATCH]` (ref: 18.0→19.0 BSL-012) `message_card_list.xml`: `t-inherit` ke
  `mail.MessageCardList`, xpath `//a[contains(@class,'o-mail-MessageCard-jump')]` (selector `//a[...]`,
  bukan `//button[...]` — fix warisan `MF-14`/generasi 17→18, dikonfirmasi ULANG masih berlaku),
  position `replace`, ganti jadi tombol custom "See" via `onClickJump(message)`.

### CSS
- `[BSL-014]` `[MATCH]` (ref: 18.0→19.0 §6 "CSS", prosa tanpa ID `BSL` eksplisit di dokumen lama)
  `style.css` — styling kosmetik murni (`.o-mail-PinnedMessages .card`/`.card-body`, background
  translucent merah-coklat `rgba(165,42,42,0.1)`, tanpa border/shadow), tidak ada logic.

## 7. Dependency Eksternal

### Eksplisit (manifest)
- `depends: ['web', 'base', 'mail']`

### Implisit/Inferred
- Lihat `01a_MIGRATION_INTAKE.md` §2 — seluruh import `@mail/...`/`@web/...` dan `this.messagePinService`
  implisit (§8 di bawah).

## 8. Quirk / Behavior Non-Obvious

- `[BSL-015]` `[MATCH][DIWARISI-SOURCE]` (ref: 18.0→19.0 BSL-013) Dua entry-point UI pin
  (`pinMessage.js` action-menu → `onClickPin` vs tombol inline `pinnedMessages.xml` →
  `onMessagePin`) berujung ke RPC server yang SAMA (`toggle_pin`), tapi lewat dua method client
  berbeda dengan percabangan `is_discussion` yang berbeda pula (`onClickPin` bercabang, `onMessagePin`
  tidak) DAN error-handling yang berbeda (`onClickPin` punya try/catch, `onMessagePin` tidak).
  Behaviorally konsisten hari ini, bukan bug — tapi kalau salah satu diubah tanpa menyesuaikan yang
  lain, bisa divergen diam-diam. Dikonfirmasi ULANG masih persis sama di kode 19.0 saat ini.
- `[BSL-016]` `[MATCH][DIWARISI-SOURCE]` (ref: 18.0→19.0 BSL-014) `this.messagePinService` dipakai di
  cabang dead-code `onClickPin()` TANPA pernah diimpor/dideklarasikan — hanya ada karena `mail` core
  sendiri menyuntikkan service ini ke `Message`. Dependency implisit paling rapuh di modul ini: kalau
  mekanisme injeksi ini hilang/berubah nama di 20.0, baris ini akan error SAAT DIPANGGIL — tapi
  karena cabang ini dead code (tidak pernah benar-benar dieksekusi), errornya kemungkinan tidak akan
  pernah muncul di praktik, HANYA relevan kalau native Discuss-pin behavior berubah lagi dan membuat
  cabang ini hidup kembali. Belum dicek ulang keberadaan service ini secara spesifik di 20.0 (di luar
  scope Step 1 — dependency implisit-non-manifest, lihat `01a_MIGRATION_INTAKE.md` §2).
- `[BSL-017]` `[NO-SPEC]` (ref: — ; cross-ref `MF-25`, `MF-26`) **Pilihan class ikon Font Awesome.**
  Tidak pernah dibahas di baseline lama sama sekali (topik baru). Kode aktual: action-menu memakai
  `icon: "fa fa-thumb-tack"` (prefix family wajib disertakan, konvensi Odoo 18.0+ — fix `MF-26`,
  tanpa prefix akan render kotak kosong); tombol inline memakai `fa-thumb-tack text-primary` (state
  pinned) / `fa-thumb-tack text-muted` (state belum-pinned, fix `MF-25` — Font Awesome 4.7 bawaan
  Odoo tidak punya varian outline `fa-thumb-tack-o`, sebelumnya render kotak kosong). Murni detail
  presentasi, tidak ada business logic — dicatat di sini karena sebelumnya genuinely tidak
  didokumentasikan di generasi manapun.

---

## Cara Pakai

`BSL-NNN` di dokumen ini penomoran baru khusus modul ini untuk project 19.0→20.0, dimulai dari 001
(tidak melanjutkan nomor dari dokumen 18.0→19.0). Tiap klaim yang carry-forward dari dokumen 18.0→19.0
merujuk balik lewat `(ref: 18.0→19.0 BSL-NNN)`; kalau dokumen itu sendiri mewarisi dari 17.0→18.0,
rujukan ganda (`17-18/BSL-NNN`, `17-18/MF-NNN`) dipertahankan di teks klaim untuk jejak audit penuh.
