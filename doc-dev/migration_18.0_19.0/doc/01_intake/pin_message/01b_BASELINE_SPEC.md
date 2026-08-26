# Baseline Spec — pin_message

**Step:** 1 — Intake & Scope (pelengkap `01a_MIGRATION_INTAKE.md`)
**Tujuan:** dokumentasikan behavior as-is di 18.0 (branch `migration/18.0`, identik dengan working
tree `migration/19.0_target` saat ini).
**Tanggal:** 2026-08-26
**Sumber:** Direkonsiliasi dari `doc-dev/migration_17.0_18.0/doc/01_intake/pin_message/01b_BASELINE_SPEC.md`
+ cross-check kode 18.0 aktual (baca penuh tiap file JS/Python) + `doc-dev/migration_17.0_18.0/doc/FINDINGS.md`.

> Provenance merujuk ke dua generasi dokumen: `(ref: 17-18/BSL-NNN)` dan `(ref: 17-18/MF-NNN)`.

---

## Ringkasan untuk Review — Perlu Konfirmasi User

**Tally provenance:** 6 klaim `[MATCH]`, 0 `[GAP]`, 3 `[NO-SPEC]` (2 perincian baru + 1 bug terbuka).

- `[BSL-002]` `[DIWARISI-SOURCE]` (ref: 17-18/MF-09) — cabang `is_discussion === true` di
  `onClickPin()` adalah dead code sejak 18.0 (native Discuss-channel pin lewat mekanisme lain),
  dikonfirmasi harmless. Pertahankan as-is.
- `[BSL-009]` `[DIWARISI-SOURCE][PERLU-KEPUTUSAN]` (ref: 17-18/MF-10) — `console.log(component.message.type)`
  di `pinMessage.js:7`, jalan tiap render action-menu pesan MANAPUN di seluruh sistem (bukan cuma
  pesan yang bisa di-pin). **Masih terbuka, belum diperbaiki dari project sebelumnya.** Perlu
  keputusan user: bersihkan di project ini, atau tetap dipertahankan?
- **Fix-fix dari migrasi 17→18 (MF-12, MF-14, MF-22, MF-23, MF-24) semua dikonfirmasi ULANG masih
  ada persis di kode saat ini** — lihat §5/§8. Ini bukan hal baru, tapi konfirmasi eksplisit bahwa
  baseline 18.0 project ini memang sudah dalam kondisi ter-fix, bukan regresi diam-diam.
- **Area risiko tertinggi:** seluruh modul adalah patch/`t-inherit` terhadap komponen Owl inti
  `mail`/`discuss` (`Chatter`, `Message`, `MessageCardList`) + satu override Python
  `mail.message._to_store()`. Kelima titik integrasi yang PERNAH rusak di migrasi 17→18 (path
  import, xpath selector, service/method relocation) adalah PERSIS jenis perubahan yang bisa terjadi
  lagi di 19.0 — wajib diverifikasi ulang ke `native-target` 19.0 nyata di Step 2, tidak bisa
  diasumsikan stabil dari riwayat migrasi sebelumnya.

---

## 1. Tujuan Modul

Menambahkan kemampuan "pin" pesan/log-note di chatter Odoo — independen dari mekanisme pin native
Discuss-channel. User bisa menandai pesan penting (via tombol inline per-pesan ATAU entry di
action-menu "..." pesan) supaya muncul di section collapsible "Pinned Messages" di bagian atas
chatter, dengan badge jumlah. Toggle pin/unpin sinkron realtime lewat bus.

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

- `[BSL-001]` `[MATCH]` (ref: 17-18/BSL-001) `toggle_pin()` — method di `mail.message`, dipanggil
  lewat RPC dari DUA entry-point client berbeda (lihat `BSL-006`). Loop `for message in self:` (aman
  multi-record), flip `is_pinned`, broadcast per-message via
  `bus.bus._sendone(f'{self._name},{message.id}', 'mail.message/pin_changed', {...})` untuk sinkron
  realtime UI. Return `True`.
- `[BSL-002]` `[MATCH][DIWARISI-SOURCE]` (ref: 17-18/BSL-002, 17-18/MF-09) `onClickPin()`
  (`message.js`) bercabang berdasarkan `this.message.is_discussion`:
  - `True` (pesan Discuss-channel) → delegasi ke `this.messagePinService` (service implisit, tidak
    diimpor eksplisit di modul ini). **Dead code sejak 18.0** — native Discuss-channel pin sekarang
    berjalan lewat mekanisme lain, method ini tidak pernah benar-benar terpanggil untuk jalur ini.
    Dikonfirmasi harmless (tidak ada fitur hilang untuk end-user).
  - `False` (chatter/log-note biasa) → RPC `orm.call("mail.message", "toggle_pin", [[id]])`, lalu
    flip `is_pinned` lokal di props, wrapped try/catch.
- `[BSL-003]` `[MATCH]` (ref: 17-18/BSL-002) `onMessagePin()` (`message.js`) — entry-point KEDUA,
  TANPA percabangan `is_discussion` sama sekali, selalu RPC + flip lokal. Dipanggil dari tombol pin
  inline (lihat `BSL-006`).
- `[BSL-004]` `[MATCH]` (ref: 17-18/BSL-003) Action-menu "Pin" (`messageActionsRegistry.add("pins",
  ...)`, sequence 15) hanya muncul kalau: `canAddReaction` true (lihat `BSL-010`), pesan BUKAN
  discussion DAN bukan tipe `user_notification`/`auto_comment`/`notification`, DAN
  `subtype_description` kosong (bukan changelog message). `onClick` memanggil `onClickPin()`
  (`BSL-002`).

## 5. Server-Side Logic dengan Side Effect

- `[BSL-005]` `[MATCH]` (ref: 17-18/BSL-001) `toggle_pin()` tidak punya side effect lain di luar bus
  broadcast (§4).
- `[BSL-006]` `[MATCH][RESOLVED — ref: 17-18/MF-22, 17-18/MF-23]` **`_to_store()` override
  dikonfirmasi ulang di kode aktual:** `super()._to_store(store, **kwargs)` dipanggil dulu (extend,
  bukan replace), lalu `store.add(message, {'is_pinned': message.is_pinned})` per message. Ini
  mekanisme PENGGANTI 18.0 untuk apa yang dulu (17.0) jadi full-override `Chatter.load()` dengan
  parameter field-list custom (mekanisme lama itu sudah dihapus total, dikonfirmasi tidak ada
  `load()` override di `chatter.js` manapun — hanya `setup()`/`initialLoad()`/getter/`togglePinnedMessages()`).

## 6. Client-Side Behavior (Views, JS, Owl)

### `chatter.js` (patch `Chatter.prototype`)
- `[BSL-007]` `[MATCH][RESOLVED — ref: 17-18/MF-12, 17-18/MF-22]` `setup()`: `super.setup()` +
  inject `orm`/`notification`, tambah `state.showPinnedMessages=false`, `onMounted`+`onWillUpdateProps`
  hook memanggil `initialLoad()`. Import path `Chatter` dikonfirmasi
  `@mail/chatter/web_portal/chatter` (fix `MF-12` masih ada, path lama `@mail/core/web/chatter` tidak
  dipakai lagi).
- `[BSL-008]` `[MATCH]` (ref: 17-18/BSL-007) `initialLoad()`: panggil `this.load(state.thread,
  ["messages"])` (method inti, TIDAK di-override), lalu `orm.searchRead` terpisah untuk
  `mail.message` ber-`is_pinned=True` sesuai thread, urut `date DESC`, stamp ke in-memory messages.
  Getter `pinnedMessages` filter dari situ; `togglePinnedMessages()` flip state collapse/expand.
  `Chatter.components` diperluas dengan `MessageCardList`.

### `message.js` (patch `Message.prototype`)
- Lihat `BSL-002`/`BSL-003` di §4.

### `pinMessage.js` (registrasi action-menu)
- `[BSL-009]` `[NO-SPEC][DIWARISI-SOURCE][PERLU-KEPUTUSAN — ref: 17-18/MF-10]`
  `console.log(component.message.type)` di baris 7 `condition` callback — dieksekusi SETIAP kali
  action-menu di-render untuk pesan MANAPUN (bukan cuma yang lolos kondisi pin). Debug leftover,
  **masih terbuka/belum diperbaiki** sejak project 17→18. Perlu keputusan eksplisit user.
- `[BSL-010]` `[MATCH][RESOLVED — ref: 17-18/MF-24]` `condition` callback: `if
  (!component.message.canAddReaction(component.props.thread)) return false` — dikonfirmasi memanggil
  `canAddReaction` sebagai METHOD di `component.message` (model), bukan sebagai getter di
  `component` (component). Ini bentuk yang SUDAH BENAR (fix `MF-24`); versi lama yang salah
  (`component.canAddReaction`, selalu `undefined`, membuat entry menu "Pin" tidak pernah render sama
  sekali) TIDAK ada di kode saat ini.

### Template QWeb
- `[BSL-011]` `[MATCH]` (ref: 17-18/BSL-007) `pinnedMessages.xml`: dua `t-inherit` — (a) ke
  `mail.Chatter`, xpath `o-mail-Chatter-topbar` position `after`, insert section collapsible +
  badge + `<MessageCardList messages="pinnedMessages" .../>`; (b) ke `mail.Message`, xpath
  `o-mail-Message-author` position `after`, insert tombol pin/unpin inline (guard `t-if` menghindari
  tipe `notification`/discussion/`mail.activity.thread`), memanggil `onMessagePin(props.message.id)`
  (`BSL-003`).
- `[BSL-012]` `[MATCH][RESOLVED — ref: 17-18/MF-14]` `message_card_list.xml`: `t-inherit` ke
  `mail.MessageCardList`, xpath `//a[contains(@class,'o-mail-MessageCard-jump')]` (dikonfirmasi
  selector `//a[...]`, BUKAN `//button[...]` yang lama — core 18.0 sudah pakai elemen `<a
  role="button">`), position `replace`, ganti jadi tombol custom "See" via `onClickJump(message)`.

### CSS
- `style.css` — styling kosmetik murni (background translucent merah-coklat untuk card pinned), tidak
  ada logic.

## 7. Dependency Eksternal

### Eksplisit (manifest)
- `depends: ['web', 'base', 'mail']`

### Implisit/Inferred
- Lihat `01a_MIGRATION_INTAKE.md` §2 — seluruh import `@mail/...`/`@web/...` dan `this.messagePinService`
  implisit (§8).

## 8. Quirk / Behavior Non-Obvious

- `[BSL-013]` `[MATCH][DIWARISI-SOURCE]` (ref: 17-18/BSL-006) Dua entry-point UI pin
  (`pinMessage.js` action-menu → `onClickPin` vs tombol inline `pinnedMessages.xml` →
  `onMessagePin`) berujung ke RPC server yang SAMA (`toggle_pin`), tapi lewat dua method client
  berbeda dengan percabangan `is_discussion` yang berbeda pula (`onClickPin` bercabang, `onMessagePin`
  tidak). Behaviorally konsisten hari ini, bukan bug — tapi kalau salah satu diubah tanpa
  menyesuaikan yang lain, bisa divergen diam-diam.
- `[BSL-014]` `[MATCH][DIWARISI-SOURCE]` (ref: 17-18/MF-09) `this.messagePinService` dipakai di cabang
  dead-code `onClickPin()` TANPA pernah diimpor/dideklarasikan — hanya ada karena `mail` core sendiri
  menyuntikkan service ini ke `Message`. Dependency implisit paling rapuh di modul ini: kalau
  mekanisme injeksi ini hilang/berubah nama di 19.0, baris ini akan error SAAT DIPANGGIL — tapi
  karena cabang ini dead code (tidak pernah benar-benar dieksekusi di 18.0/19.0), errornya kemungkinan
  tidak akan pernah muncul di praktik, HANYA relevan kalau native Discuss-pin behavior berubah lagi
  dan membuat cabang ini hidup kembali.

---

## Cara Pakai

Sama seperti dokumen `pos_margin_threshold`/`sale_margin_threshold` — `BSL-NNN` di sini penomoran
baru khusus modul ini untuk project 18.0→19.0.
