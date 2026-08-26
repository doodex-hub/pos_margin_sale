# Diff & Compatibility Analysis — pin_message

**Step:** 2 — Diff & Compatibility Analysis
**Versi:** 18.0 → 19.0
**Tanggal:** 2026-08-26
**Ref:** `01_intake/pin_message/01a_MIGRATION_INTAKE.md`, `migration-tool/knowledge/`

---

## 0. Knowledge Base Check

| Sumber | Sudah ada entry? | Lokasi |
|---|---|---|
| `version-diffs/18-to-19.md` | Ya, tidak spesifik `mail` | `migration-tool/knowledge/version-diffs/18-to-19.md` |
| `dependency-compat/mail/18-to-19.md` | **Tidak ada** — modul ini yang menghasilkan riset pertama untuk `mail` 18→19 lewat tool ini | — (kandidat baru, lihat §3) |

## 0b. Gate Community vs Enterprise

Dependency map: `web`, `base`, `mail` — semua Community. Tidak perlu `native-target-enterprise`
untuk modul ini.

- [x] Dicek langsung ke `native-source` (`odoo18/addons/mail/`) DAN `native-target`
  (`enterprise19.0/odoo/addons/mail/`).

## 0c. Gate Transitive Dependency

N/A — tidak ada `depends` yang diusulkan dihapus.

---

## 1. Perubahan Native (Core/Enterprise)

| ID | File/simbol modul | Simbol native terkait | Status di target | Dampak | Sumber |
|---|---|---|---|---|---|
| DIFF-01 | `models/mail_message.py:22` `def _to_store(self, store, /, **kwargs): super()._to_store(store, **kwargs)` | `mail.message._to_store()` (`mail/models/mail_message.py`) | **SIGNATURE BERUBAH — breaking.** 18.0: `_to_store(self, store, /, *, fields=None, format_reply=True, msg_vals=None, for_current_user=False, add_followers=False, followers=None)` — `fields` keyword-only, opsional. 19.0: `_to_store(self, store, fields, *, format_reply=True, msg_vals=False, add_followers=False, followers=None)` — `fields` sekarang **positional wajib** (parameter ke-2), `for_current_user` **dihapus total** (diganti `store.target`). Override modul ini (`store, /, **kwargs`) TIDAK punya slot untuk argumen positional kedua | **KRITIS — crash total, blast radius luas.** Setiap `store.add(<mail.message>, ...)` di MANAPUN (chatter, Discuss, notifikasi apapun yang serialisasi pesan) memanggil `_to_store` secara positional (`records._to_store(self, fields, **kwargs)`, `mail/tools/discuss.py`). Override ini akan `TypeError: _to_store() takes 2 positional arguments but 3 were given` — bukan cuma fitur pin yang rusak, TAPI SELURUH mekanisme pengiriman pesan ke frontend | Analisis baru |
| DIFF-02 | `static/src/js/pinMessage.js:5-26` `messageActionsRegistry.add("pins", {condition, icon, title, onClick, sequence})` | `messageActionsRegistry`/`Action` class (`mail/static/src/core/common/message_actions.js`, `action.js`) | **RENAME + BEHAVIOR BERUBAH TOTAL — breaking.** Import path & `registry.category("mail.message/actions")` TIDAK berubah, TAPI shape definisi berubah total: `title`→`name`, `onClick`→`onSelected`. Argumen callback (`component` di 18.0 = instance komponen Owl asli) di 19.0 jadi objek POLOS `{action, store, owner, message, thread}` — **TIDAK ADA `.props` di objek ini** | **KRITIS.** `component.message.canAddReaction(component.props.thread)` di `condition` akan throw `TypeError: Cannot read properties of undefined (reading 'thread')` KARENA `component.props` sekarang `undefined` — ini jalan di getter reactive yang dievaluasi untuk SETIAP pesan yang di-render, untuk SEMUA action, bukan cuma "pins". `title`/`onClick` juga diam-diam diabaikan (19.0 baca `.name`/`.onSelected`) — bahkan kalau crash di atas diperbaiki, label tidak muncul dan klik tidak melakukan apapun | Analisis baru |
| DIFF-03 | `static/src/js/chatter.js` (`Chatter.load()`, import path) | `Chatter` component (`mail/static/src/chatter/web_portal/chatter.js`) | **Tidak berubah untuk modul ini.** Path file tidak pindah lagi. `load(thread, requestList)` tetap ada dengan signature sama yang dipakai modul (`this.load(this.state.thread, ["messages"])`) — internal core berubah jadi `async`/`fetchThreadData` (rename dari `fetchData`), tapi TIDAK observable dari cara modul memanggilnya | Tidak ada | Analisis baru |
| DIFF-04 | `static/src/js/message.js` (`this.messagePinService`, cabang `is_discussion`) | Mekanisme native Discuss-channel pin (`mail/static/src/discuss/message_pin/common/message_model_patch.js`) | **Tidak berubah — dikonfirmasi dead code di KEDUA versi**, bukan regresi baru. `messagePinService` TIDAK PERNAH ada sebagai service terdaftar di source `mail` manapun (grep penuh 18.0 DAN 19.0: 0 match) — native pin/unpin jalan lewat `patch(Message.prototype, {pin(), unpin()})` langsung di record model, bukan lewat service. Cabang `is_discussion` di `onClickPin()` modul ini sudah TIDAK PERNAH tercapai bahkan sebelum 19.0 (template pin inline dan `condition` action-menu keduanya sudah men-syarat `!is_discussion`) | Tidak ada (tetap dead code aman, konsisten `MF-09`) | Analisis baru |
| DIFF-05 | `static/src/js/pinMessage.js:8` `component.message.canAddReaction(component.props.thread)` | `Message.prototype.canAddReaction(thread)` (`mail/static/src/core/common/message_model.js`) | **Signature tidak berubah, internal behavior berubah.** 18.0: `return Boolean(!this.is_transient && this.thread?.can_react)`. 19.0: tambah kondisi `!this.isPending && !this.thread.isTransient && this.thread.has_mail_thread`. Method tetap ada di message MODEL (bukan pindah balik jadi getter component) dengan signature `canAddReaction(thread)` yang sama | Rendah — setelah `DIFF-02` diperbaiki, action "Pin" mungkin tersembunyi di lebih banyak kondisi dibanding 18.0 (pesan pending, thread tanpa `mail.thread` mixin) — perlu regression check manual, bukan hard break | Analisis baru |
| DIFF-06 | `static/src/xml/pinnedMessages.xml` xpath `o-mail-Chatter-topbar`, `o-mail-Message-author` | Template `Chatter`/`Message` | **Tidak berubah** — kedua CSS class anchor tetap ada di tag/posisi yang sama (`<div class="o-mail-Chatter-topbar">` dan `<span class="o-mail-Message-author">`) di 18.0 dan 19.0 | Tidak ada | Analisis baru |
| DIFF-07 | `static/src/xml/message_card_list.xml` xpath `o-mail-MessageCard-jump` | Template `MessageCardList` | **Tidak berubah** — tetap `<a role="button" class="o-mail-MessageCard-jump ...">` di kedua versi (fix `MF-14`/17→18 tetap valid, tidak berubah lagi jadi tag lain) | Tidak ada | Analisis baru |

## 2. Kompatibilitas Dependency (OCA/Third-Party)

Tidak ada.

## 3. Temuan Baru — Kandidat Migration Records

- [x] **Ditulis ke `migration-tool/migration-records/pos-margin-sale_18.0_19.0/SUMMARY.md`** (kategori
  `dependency-compat`, `mail` 18→19). Dua temuan sangat general: (1) `mail.message._to_store()`
  signature `fields` jadi positional wajib — akan mematahkan SETIAP modul yang override method ini
  dengan pola umum `def _to_store(self, store, /, **kwargs)`; (2) `messageActionsRegistry` payload
  shape berubah total (`title`→`name`, `onClick`→`onSelected`, argumen callback jadi objek polos
  tanpa `.props`) — akan mematahkan SETIAP modul yang menambahkan action-menu pesan custom dengan
  pola 18.0. Kedua pola ini SANGAT UMUM untuk modul custom yang menyentuh chatter/Discuss.

## 4. Ringkasan Risiko

| Item | Level risiko | Catatan |
|---|---|---|
| `DIFF-01` (`_to_store` signature) | **Kritis — blast radius terluas di seluruh project ini** | Bukan cuma fitur pin yang rusak — SEMUA pengiriman pesan ke frontend (chatter, Discuss, notifikasi) akan `TypeError` begitu modul ini terinstall di 19.0, sampai fix diterapkan |
| `DIFF-02` (`messageActionsRegistry` shape) | **Kritis** | Crash di getter reactive yang dievaluasi untuk SETIAP pesan — potensi mematahkan action-menu pesan secara luas, tidak terbatas ke action "pins" modul ini sendiri |
| `DIFF-05` (kondisi `canAddReaction` bertambah) | Rendah | Regression check manual setelah fix DIFF-02 |
| Sisanya (`DIFF-03`, `04`, `06`, `07`) | Tidak ada | Konfirmasi stabil |

**Kesimpulan Step 2 modul ini:** `pin_message` adalah modul dengan risiko TERTINGGI di seluruh project
18.0→19.0 ini — dua breaking change independen (`_to_store` dan `messageActionsRegistry`), keduanya
install/runtime-blocking dengan blast radius yang melampaui fitur modul ini sendiri (mempengaruhi
mekanisme inti pengiriman pesan dan action-menu pesan secara umum). Perbaikan konkret sudah
diidentifikasi (lihat `DIFF-01`/`DIFF-02` dan pola referensi native `discuss/message_pin/common/message_actions.js`
19.0) — ini jadi prioritas TERTINGGI Step 3 (migration spec) di seluruh project, harus diselesaikan
sebelum modul ini bisa lulus G1 (install test) sama sekali.
