# Diff & Compatibility Analysis — pin_message

**Step:** 2 — Diff & Compatibility Analysis
**Versi:** 19.0 → 20.0
**Tanggal:** 2026-09-21
**Ref:** `01_intake/pin_message/01a_MIGRATION_INTAKE.md`, `01_intake/pin_message/01b_BASELINE_SPEC.md`,
`FINDINGS.md` `MF-28`, `migration-tool/knowledge/`

---

## 0. Knowledge Base Check

| Sumber | Sudah ada entry? | Lokasi |
|---|---|---|
| `version-diffs/19-to-20.md` | **Ya, TAPI tidak spesifik `mail`** — isinya `web` (logout 405, `ListRenderer`), `base` (`ir.access.csv`) dari project `optional_field_save`. Tidak ada satu baris pun soal `mail`/`_to_store`/`messageActionsRegistry`. | `migration-tool/knowledge/version-diffs/19-to-20.md` |
| `dependency-compat/mail/19-to-20.md` | **Tidak ada.** Entry yang ada baru `dependency-compat/mail/18-to-19.md` (pasangan versi SEBELUMNYA, dari project `pos-margin-sale` 18→19 — ini yang jadi baseline `_to_store`/`messageActionsRegistry` versi lama). Modul ini (`pin_message`, project 19.0→20.0) jadi riset **pertama** untuk `mail` di pasangan versi 19→20 lewat tool ini — kandidat kuat promosi ke `dependency-compat/mail/19-to-20.md` (lihat §3). | — (kandidat baru) |

## 0b. Gate Community vs Enterprise

- [x] `01a_MIGRATION_INTAKE.md` §2 — TIDAK ADA baris "Native Enterprise" di dependency map modul ini
  (`web`, `base`, `mail`, semua Community).
- [x] Karena tidak ada, `native-target-enterprise` (`enterprise20`) TIDAK wajib untuk gate ini secara
  substantif, tapi tetap dicek existence-nya sesi ini sebagai verifikasi silang (`grep -rn
  "_store_message_fields" enterprise20` — 4 match: `account_reports`, `ai_website`, `whatsapp`;
  TIDAK ADA satupun yang menyentuh `pin`/pesan chatter secara umum di luar contoh pola override yang
  memang sudah dipakai sebagai referensi §1). Dikonfirmasi ULANG: tidak ada modul `mail`/`base`/`web`
  terpisah di `enterprise20` (Community-only, sesuai `01a_MIGRATION_INTAKE.md`).
- **Sumber tiap baris DIFF-NNN di §1 di bawah:** semua dicek langsung ke `native-target`
  (`D:\Kuncoro\doodex\repo\odoo20\addons\mail`), dengan `enterprise20` sebagai cross-check tambahan
  untuk pola override `_store_message_fields()` (lihat DIFF-01).

## 0c. Gate Transitive Dependency

N/A — tidak ada `depends` yang diusulkan dihapus dari manifest modul ini (`web`, `base`, `mail` tetap
semua dipertahankan).

## 0d. Gate Grep Menyeluruh — Rename di Knowledge Base

Tidak ada entry knowledge base 19→20 spesifik `mail` yang bisa di-grep (§0 — belum ada sebelum sesi
ini). Sebagai gantinya, grep dilakukan terhadap SIMBOL YANG DITEMUKAN BARU sesi ini (bukan dari
knowledge base lama) ke **seluruh** source `pin_message` (`.py`, `.js`, `.xml`, termasuk
`tests/`/`static/tests/`) — bukan cuma file yang kelihatan relevan:

| Simbol/pola lama | Ditemukan di | Catatan |
|---|---|---|
| `_to_store(` | `models/mail_message.py:22,30` (definisi override + `super()` call) | Satu-satunya pemakaian, tidak ada di file lain modul ini |
| `message.canAddReaction(thread)` (dipanggil sebagai method) | `static/src/js/pinMessage.js:7` | Satu-satunya pemakaian |
| `icon: "fa fa-thumb-tack"` / `fa-thumb-tack` / `fa-caret-` | `static/src/js/pinMessage.js:23`, `static/src/xml/pinnedMessages.xml:13,41,43`, **`static/tests/tours/pin_message_tour.js:35,55`** | Dua kemunculan di file test tour (`.fa-thumb-tack.text-muted`/`.text-primary` sebagai CSS selector trigger) — **wajib ikut diperbaiki**, bukan cuma file produksi, sesuai pola gate ini (lihat juga `fa-ellipsis-v` di bawah) |
| `.fa-ellipsis-v` (selector overflow menu action) | `static/tests/tours/pin_message_tour.js:101` | Bukan dari kode modul sendiri (itu selector ke elemen NATIVE), tapi tour test ini akan gagal cocok elemen di 20.0 kalau overflow-menu native sudah pindah dari FontAwesome ke icon-font baru (dikonfirmasi §1 DIFF-04) |
| `messageActionsRegistry.add(` (bukan lewat helper resmi) | `static/src/js/pinMessage.js:5` | Lihat DIFF-02 — pola akses langsung ke registry (bukan lewat `registerMessageAction()`) berisiko silent-filtered di 20.0 |

Tidak ada kemunculan lain yang lolos dari grep di atas (dicek `models/`, `static/src/js/`,
`static/src/xml/`, `static/src/css/`, `tests/*.py`, `static/tests/tours/*.js` — daftar lengkap file
modul dari `01a_MIGRATION_INTAKE.md`/Glob sesi ini).

## 0e. Gate Silent-Regression per Tipe Override

Klasifikasi override modul ini ke 4 kategori gate, dieksekusi di §1 (baris DIFF-NNN merujuk balik ke
sini):

- **(a) Python — override method model:** `_to_store()` (`mail_message.py`) → **DIFF-01**. Bentuk
  return value method native tidak relevan di sini (tidak ada return value yang dipakai ulang), TAPI
  method-nya sendiri **tidak ada lagi** di target — kategori ekstrem dari checklist (a), bukan cuma
  signature.
- **(c) Owl/JS — `patch()` ke component native:** `patch(Chatter.prototype, ...)` (`chatter.js`),
  `patch(Message.prototype, ...)` (`message.js`) → **DIFF-03** (Chatter, RISIKO TINGGI — path import
  DAN internal architecture berubah) dan **DIFF-06** (Message, dikonfirmasi AMAN — path/internal
  method/lifecycle tidak berubah untuk yang dipakai modul ini).
- **(d) JS — ekstensi berbasis registry:** `messageActionsRegistry.add("pins", ...)` (`pinMessage.js`)
  → **DIFF-02**. Shape key (`name`/`onSelected`/`icon`/`sequence`) TIDAK berubah dari 19.0, TAPI ada
  DUA hal baru yang lolos dari cek shape-level naif: (1) `canAddReaction` berubah dari method jadi
  getter (lihat DIFF-02), (2) native TARGET sekarang mem-filter entry registry berdasarkan Symbol
  marker privat (`IS_ACTION_DEFINITION_SYM`) yang HANYA dipasang otomatis kalau registrasi lewat
  helper `registerMessageAction()` — modul ini akses `messageActionsRegistry.add()` LANGSUNG (pola
  19.0), yang di 20.0 akan LOLOS tanpa error TAPI entry-nya di-filter keluar sebelum dirender (silent,
  persis pola yang gate ini coba tangkap).
- **(b) XML inheritance:** lihat catatan "Dua pola ketergantungan ke native" di §1 tabel — modul ini
  murni pola pertama (`t-inherit`/xpath), tidak ada `t-call` standalone.

---

## 1. Perubahan Native (Core/Enterprise)

| ID | File/simbol modul | Simbol native terkait | Status di target | Dampak | Sumber |
|---|---|---|---|---|---|
| **DIFF-01** | `models/mail_message.py:22-36` `def _to_store(self, store, fields, **kwargs): super()._to_store(store, fields, **kwargs); store.add_records_fields(self, ['is_pinned'])` | `mail.message._to_store()` (harusnya di `odoo20/addons/mail/models/mail_message.py`) | **METHOD DIHAPUS TOTAL — rewrite arsitektural wajib, TAPI pola pengganti sudah dikonfirmasi konkret & mekanis.** Grep penuh `odoo20/addons/mail/models/mail_message.py`: 0 match untuk `_to_store`/`to_store`. Diganti `_store_message_fields(self, res: Store.FieldList, *, format_reply=True, chatter_fields=False, inbox_fields=False, followers=None)` (baris 1177 dst) — API serializer field-list (`Store.FieldList`, didefinisikan `odoo20/addons/mail/tools/discuss.py` baris 830-963), BUKAN lagi override method monolitik dengan objek `store` mentah. Native SUDAH memanggil field ini sendiri: `res.attr("pinned_at")` — **field pin NATIVE lain (Discuss-channel, tidak sama dengan `is_pinned` modul ini)** ada di `_store_message_fields`, jadi field boolean/datetime tambahan memang didaftarkan dengan `res.attr(...)`, bukan raw dict. **Pola pengganti yang PERSIS sama kebutuhannya sudah ada 2 contoh kerja native**: `odoo20/addons/rating/models/mail_message.py:41-44` dan `odoo20/addons/im_livechat/models/mail_message.py:10-11` — keduanya `def _store_message_fields(self, res: Store.FieldList, **kwargs): super()._store_message_fields(res, **kwargs); res.<something>(...)`. Untuk field boolean tunggal tanpa predicate/sudo seperti `is_pinned`, `Store.FieldList.attr(field_name)` (baris 860-868 `discuss.py`) sudah cukup — behaviornya: kalau `records is not None` dan tidak ada `value`/`predicate`/`sudo` custom, `attr()` cuma `append(field_name)` ke list field yang di-batch-read lewat `_read_format()` (mekanisme SAMA seperti `res.attr("subject")`/`res.attr("write_date")` yang dipakai native `_store_message_fields` sendiri). **Rewrite konkret yang disarankan:**<br>`from odoo.addons.mail.tools.discuss import Store`<br>`def _store_message_fields(self, res: Store.FieldList, **kwargs):`<br>`    super()._store_message_fields(res, **kwargs)`<br>`    res.attr("is_pinned")`<br>Ini MENGHILANGKAN kebutuhan `store.add_records_fields()` sama sekali (API itu juga terkait `_to_store`/`Store` versi 19.0 — belum dicek apakah `add_records_fields` masih ada di `discuss.py` 20.0 untuk use-case lain, TAPI untuk kasus modul ini tidak lagi relevan karena `res.attr()` sudah cukup). | **Tertinggi di seluruh project — TAPI mekanis** (lihat kesimpulan §4). Kalau tidak diperbaiki: `AttributeError`/`TypeError` saat modul di-load (override method yang sudah tidak ada di base class mana pun bukan error langsung di Python — override tetap terdaftar sebagai method BARU tanpa pernah dipanggil siapapun, KARENA native tidak lagi memanggil `_to_store` sama sekali di jalur manapun; `is_pinned` akan hilang total dari payload store, chatter/Discuss TETAP jalan tapi fitur pin senyap tidak pernah muncul — silent, bukan crash. Beda dari 18→19 yang crash total; 19→20 GAGAL SENYAP kalau tidak diperbaiki.) | Analisis baru sesi ini |
| **DIFF-02** | `static/src/js/pinMessage.js:1-27` (seluruh file: `messageActionsRegistry.add("pins", {condition, icon, name, onSelected, sequence})`) | `messageActionsRegistry`/`registerMessageAction()`/`Action` class (`odoo20/addons/mail/static/src/core/common/message_actions.js`, `action.js`) | **Shape key TIDAK berubah dari 19.0** (`name`/`onSelected`/`icon`/`sequence`/`condition` semua masih dipakai identik oleh ~15 action bawaan 20.0 — dicek langsung `message_actions.js` baris 41-222). **TIGA hal baru breaking, tidak kelihatan dari cek shape saja:**<br>**(1) `condition` callback — `message.canAddReaction(thread)` (method 19.0) → `message.canAddReaction` (GETTER, tanpa argumen) di 20.0.** Dikonfirmasi `odoo20/addons/mail/static/src/core/common/message_model.js:582-587`: `get canAddReaction() { return Boolean(!this.is_transient && !this.isPending && this.thread?.can_react && ...) }` — properti langsung, sudah include cek thread internal. Native sendiri sudah migrasi ke pola getter ini (`message_actions.js:49`: `condition: ({ message }) => message.canAddReaction`, TANPA `thread` dan TANPA tanda kurung panggil). Kode modul ini (`if (!message.canAddReaction(thread)) return false;`) akan **`TypeError: message.canAddReaction is not a function`** (boolean dipanggil sebagai fungsi) — crash di getter reactive yang dievaluasi untuk SETIAP pesan yang di-render, klasik pola `MF-15`/DIFF-02 18→19 terulang lagi dengan simbol berbeda.<br>**(2) Registrasi via `messageActionsRegistry.add()` LANGSUNG (bukan lewat helper `registerMessageAction()`) sekarang di-filter keluar secara SENYAP.** Native 20.0 membungkus setiap registrasi bawaan dengan `registerMessageAction(id, definition)` (`message_actions.js:37-39`): `messageActionsRegistry.add(id, Object.assign(definition, { [IS_ACTION_DEFINITION_SYM]: true }))` — menempel Symbol privat `IS_ACTION_DEFINITION_SYM` (`export const IS_ACTION_DEFINITION_SYM = Symbol("isActionDefinition")`, `action.js:23`). Consumer registry (`useAction`, dipakai `useMessageActions`) MEM-FILTER entry: `actionRegistry.getEntries().filter(([id, definition]) => definition?.[IS_ACTION_DEFINITION_SYM])` (`action.js:868-870`) — entry TANPA symbol ini **tidak pernah masuk daftar action yang di-render sama sekali**, tanpa error apapun (LOLOS install, LOLOS runtime tanpa exception, cuma action "Pin" TIDAK PERNAH muncul di action-menu). Modul ini masih akses `messageActionsRegistry.add("pins", {...})` langsung (pola 19.0, TIDAK lewat `registerMessageAction`) — TIDAK LULUS filter ini di 20.0.<br>**(3) Icon berubah sistem total: FontAwesome (`fa fa-*`) → Odoo Icons (`oi`, atribut `data-icon="<nama>"`).** Grep penuh `mail/static/src` 20.0 untuk `fa fa-`/`class="fa `: **0 match** — FontAwesome sepenuhnya dihapus dari template `mail`. `icon` di definisi action native sekarang nama Odoo Icon polos tanpa prefix (`icon: "add_reaction"`, `"reply"`, `"bookmark"`, `"delete"`, dst — lihat `message_actions.js` baris 41-222), dirender lewat `action_list.xml:129`: `<i class="oi" ... t-att-data-icon="this.action.icon"/>`. `icon: "fa fa-thumb-tack"` milik modul ini akan dirender sebagai `<i class="oi" data-icon="fa fa-thumb-tack">` — nama icon tidak dikenal font `oi`, kemungkinan besar kotak kosong/tidak tampil (persis pola historis `MF-25`/`MF-26`). **Nama icon pengganti yang benar sudah terkonfirmasi tersedia**: `odoo20/addons/mail/static/src/core/common/message_model.js:484-491` (`get notificationIcon()`) punya mapping `case "pin": return "push_pin";` — `"push_pin"` adalah nama Odoo Icon resmi untuk konsep "pin" di 20.0, dipakai native sendiri untuk kasus terkait. **Rewrite konkret disarankan:**<br>`import { registerMessageAction } from "@mail/core/common/message_actions";`<br>`registerMessageAction("pins", {`<br>`    condition: ({ message }) => { if (!message.canAddReaction) return false; ... },`<br>`    icon: "push_pin",`<br>`    name: _t("Pin"),`<br>`    onSelected: ({ owner }) => owner.onClickPin(),`<br>`    sequence: 15,`<br>`});` | **Kritis, TAPI mekanis** — tiga fix konkret di atas (getter, helper registrasi, nama icon) sudah dikonfirmasi lewat kode native yang benar-benar jalan (bukan tebakan) | Analisis baru sesi ini |
| **DIFF-03** | `static/src/js/chatter.js:1-65` (seluruh file: `patch(Chatter.prototype, {setup, initialLoad, ...})`, import `Chatter` dari `@mail/chatter/web_portal/chatter`) | `Chatter` component (harusnya `odoo20/addons/mail/static/src/chatter/web_portal/chatter.js`) | **RISIKO TERTINGGI BARU sesi ini, BUKAN mekanis — lihat §4 "Risiko yang TIDAK bisa dipastikan mekanis".** (1) **Path import pindah**: `@mail/chatter/web_portal/chatter` (19.0, dipakai modul ini) sudah TIDAK ADA di 20.0 — grep penuh `odoo20`+`enterprise20` untuk `@mail/chatter/web_portal` (tanpa `_project`): 0 match. Path baru dikonfirmasi `@mail/chatter/web_portal_project/chatter` (`odoo20/addons/mail/static/src/chatter/web_portal_project/chatter.js`), dan dikonfirmasi masuk bundle `web.assets_backend` yang sama (manifest `mail/__manifest__.py` baris 196/200: `'mail/static/src/core/web_portal_project/**/*'`, `'mail/static/src/**/web_portal_project/**/*'`) — ini production path, bukan file mati/eksperimen. (2) **Arsitektur internal `Chatter` dirombak total**, bukan cuma rename folder: 19.0 memakai `useState`/`this.state` (proxy Owl klasik) + lifecycle `onMounted`/`onWillUpdateProps` membaca `this.props.threadId` langsung. 20.0 memakai primitif baru (`signal`, `computed`, `proxy`, `propComputed`, `useOnChange` — impor dari `@odoo/owl` dan `@web/owl2/utils`): `this.threadId = propComputed("threadId", t.or([t.number(), t.literal(false)]).optional(false))` (bukan lagi `this.props.threadId` mentah untuk baca reaktif), deteksi ganti thread sekarang lewat `useOnChange(() => [this.threadId(), this.threadModel()], (threadId, threadModel) => this.changeThread(...), { initialRun: false })` (bukan lagi `onWillUpdateProps` manual). `this.state` native SEKARANG cuma berisi `jumpThreadPresent`/`thread` (`thread` ditandai `@deprecated use the this.thread signal instead`, tapi MASIH ADA & MASIH DIISI oleh `changeThread()`). Method `initialLoad()` TIDAK ADA sebagai nama di native manapun (native native pakai `_onMounted()`+`load()`) — nama method patch modul ini murni method BARU milik modul (aman, tidak collide), TAPI method `load(thread, requestList)` yang dipanggil dari dalamnya (`this.load(this.state.thread, ["messages"])`) dikonfirmasi MASIH ADA dengan signature sama (`async load(thread, requestList)`, `chatter.js` baris 147-154), jadi panggilan itu sendiri kemungkinan besar tetap valid. **Yang BELUM bisa dipastikan tanpa eksekusi nyata (browser/tour test)**: apakah `patch(Chatter.prototype, {setup() { super.setup(); ...; onMounted(...); onWillUpdateProps(...); }})` — yang menambah HOOK KEDUA `onWillUpdateProps` di atas hook native yang SUDAH TIDAK memakai `onWillUpdateProps` sama sekali (diganti `useOnChange`) — masih ter-trigger dengan urutan/timing yang sama seperti 19.0, atau apakah duplikasi logic reaktif (native pakai `useOnChange` momentum baru, modul masih pakai `onWillUpdateProps` gaya lama) menyebabkan race/`initialLoad()` terpanggil di waktu yang salah (sebelum `this.state.thread` sempat diisi ulang oleh `changeThread()`, atau dua kali). `Chatter.components = {...Chatter.components, MessageCardList}` (assignment ke static class field) dikonfirmasi tetap valid secara sintaks (native tetap punya `static components = {Thread, Composer}` sebagai class field biasa), risiko di sini rendah. | **Tertinggi — BUKAN mekanis, WAJIB verifikasi eksekusi nyata (Step 6/9) sebelum dianggap selesai, bukan tebakan.** Kalau `onWillUpdateProps` modul ini tidak lagi ter-trigger benar (karena native tidak lagi mengandalkan hook itu untuk deteksi ganti thread), efeknya SENYAP: pindah dari satu chatter record ke record lain (mis. ganti antar invoice/partner di form view) tidak akan me-refresh ulang daftar Pinned Messages — bug UX, bukan crash, gampang terlewat kalau test cuma menguji SATU thread/record (persis pola `MF-14`/`MF-15` — silent, ketahuan cuma dari eksekusi behavior nyata) | Analisis baru sesi ini |
| **DIFF-04** | `static/src/xml/pinnedMessages.xml:12-13` (caret icon `fa fa-fw`/`fa-caret-down`/`fa-caret-right`), `:43` (`fa-thumb-tack text-primary`/`text-muted`); juga `static/tests/tours/pin_message_tour.js:35,55,101` (selector CSS ke class FA yang sama) | Sistem icon `mail` (Odoo Icons `oi`/`data-icon`, native `odoo20/addons/mail/static/src/**/*.xml`) | **FontAwesome dihapus total dari template `mail` 20.0** (0 match `fa fa-`/`class="fa ` di seluruh `mail/static/src/**/*.xml` — dicek penuh sesi ini), diganti pola `<i class="oi" data-icon="<nama>"/>` konsisten di semua template native yang dicek (`chatter.xml` baris 33: `data-icon="search"`; `message_card_list.xml` baris 10: `data-icon="close_small"`). Untuk collapse/expand caret, native punya BANYAK contoh konsisten: `attachment_list.xml:195` `data-icon="keyboard_arrow_down"`, `message.xml:217` `data-icon="keyboard_arrow_right"`, `chat_window.xml:95`/`discuss_content.xml:27` `data-icon="chevron_right"`/`"chevron_forward"`. Untuk icon pin itu sendiri, `"push_pin"` sudah terkonfirmasi (lihat DIFF-02) sebagai nama resmi. **Rewrite konkret disarankan** untuk `pinnedMessages.xml`: caret → `<i class="oi" t-att-data-icon="state.showPinnedMessages ? 'keyboard_arrow_down' : 'chevron_right'"/>` (menggantikan `<i class="fa fa-fw" t-att-class="...">`); tombol pin inline → `<i class="oi" data-icon="push_pin" t-att-class="props.message.is_pinned ? 'text-primary' : 'text-muted'" role="img" .../>` (kelas Bootstrap `text-primary`/`text-muted` TETAP dipertahankan — itu bukan bagian sistem FA, cuma warna). Komentar lama di baris 40-42 (soal FA 4.7 tidak punya varian outline `fa-thumb-tack-o`) jadi TIDAK RELEVAN lagi di 20.0 — `oi` bukan FontAwesome, tidak punya masalah varian outline yang sama, TAPI perlu dicek ulang di Step 6 apakah `oi` punya 2 varian visual (solid/outline) untuk `push_pin` atau cukup dibedakan warna saja (yang sudah jadi pola modul ini). **Tour test** (`pin_message_tour.js`) memakai selector `button:has(.fa-thumb-tack.text-muted)`/`.text-primary` (baris 35, 55) dan `button:has(.fa-ellipsis-v)` (baris 101, selector ke tombol overflow-menu NATIVE, defaultnya `more_vert` per `action.js` baris 768: `icon: data?.icon ?? "more_vert"`) — SEMUA wajib diupdate ke selector `[data-icon="push_pin"]`/`[data-icon="more_vert"]` beserta pasangannya, atau tour akan gagal mencocokkan elemen (bukan bug modul, tapi test jadi false-negative/timeout) | **Tinggi (fungsional UI + false-negative test), tapi mekanis** — pola pengganti (`data-icon`) dan nama icon (`push_pin`, `more_vert`, `keyboard_arrow_down`/`chevron_right`) sudah dikonfirmasi lewat banyak contoh native yang identik kebutuhannya | Analisis baru sesi ini (temuan BARU, belum ada di `01a_MIGRATION_INTAKE.md`/`01b_BASELINE_SPEC.md` — flag untuk `FINDINGS.md`, lihat §3) |
| **DIFF-05** | `static/src/xml/pinnedMessages.xml:6,35`, `static/src/xml/message_card_list.xml:4` — xpath anchor `o-mail-Chatter-topbar`, `o-mail-Message-author`, `o-mail-MessageCard-jump` | Template `Chatter`/`Message`/`MessageCardList` (`chatter.xml` baris 7, `message.xml` baris 37, `message_card_list.xml` baris 8) | **Tidak berubah.** Ketiga CSS class anchor dikonfirmasi masih ada di tag & posisi struktural yang sama: `<div class="o-mail-Chatter-topbar ...">`, `<span ... class="o-mail-Message-author smaller">`, `<a role="button" class="o-mail-MessageCard-jump ...">`. Ketiga `t-inherit`/xpath modul ini tetap resolve tanpa perlu diubah. | Tidak ada | Analisis baru sesi ini |
| **DIFF-06** | `static/src/js/message.js:1-32` (`patch(Message.prototype, {setup, onClickPin, onMessagePin})`, import `Message` dari `@mail/core/common/message`) | `Message` component (`odoo20/addons/mail/static/src/core/common/message.js`) | **Tidak berubah untuk yang dipakai modul ini.** Path import stabil (file tetap di `core/common/message.js`, dikonfirmasi lewat Glob). `setup()` tetap ada sebagai method overridable (baris 84) dan `useService` tetap dipakai untuk pola sama. Getter `get message() { return this.props.message; }` (baris 346-347) dikonfirmasi TETAP ADA — `this.message.is_discussion` dan `this.props.message.id` (yang dipakai `onClickPin`/`onMessagePin`) tetap valid API. `this.messagePinService` tetap TIDAK ADA sebagai service terdaftar di `mail` 20.0 (grep `messagePinService`: 0 match di `mail/static/src`) — cabang dead code `is_discussion` (`BSL-002`/`BSL-016`) tetap aman, konsisten temuan 18→19 (`DIFF-04` dokumen lama). | Tidak ada — tapi tetap tandai dead code `is_discussion` sebagai warisan (lihat catatan `BSL-016`) | Analisis baru sesi ini |
| **DIFF-07** | `static/src/js/pinMessage.js:6-19` (business rule `condition`: `isNote`/`isNotChangeLog` berdasar `message.is_discussion`/`message.message_type`/`message.subtype_description`) | `Message` model fields (`message_model.js`) | **Field-field yang dibaca TIDAK berubah** — `is_discussion`, `message_type`, `subtype_description` dikonfirmasi masih ada sebagai field/getter di `message_model.js` 20.0 dengan semantik yang sama (dicek existence, bukan re-verifikasi value/logic penuh — di luar prioritas riset DIFF-01/02/03). Business rule visibility "Pin" (§4 `01b_BASELINE_SPEC.md` `BSL-004`) tidak perlu berubah setelah DIFF-02 diperbaiki. | Rendah | Analisis baru sesi ini |

> **Catatan "Dua pola ketergantungan ke native":** seluruh file `views/`/template modul ini
> (`pinnedMessages.xml`, `message_card_list.xml`) sudah dienumerasi lewat Glob §Ringkasan sesi ini —
> keduanya pola `t-inherit`+xpath (DIFF-05), tidak ada `t-call`/`t-extend` standalone terhadap layout
> native. Tidak ada gap gate ini untuk modul ini.

## 2. Kompatibilitas Dependency (OCA/Third-Party)

Tidak ada — modul ini tidak punya dependency OCA/third-party (dikonfirmasi ulang `01a_MIGRATION_INTAKE.md` §0/§2).

## 3. Temuan Baru — Tulis ke Migration Records

- [ ] **Kandidat `dependency-compat/mail/19-to-20.md` (BARU, belum ada file ini sama sekali).** Tulis
  ke `migration-tool/migration-records/pos-margin-sale_19.0_20.0/SUMMARY.md` (kategori
  `dependency-compat`, dependency `mail`, pasangan 19→20) — ringkasan 3 temuan independen: (1)
  `_to_store()` dihapus total, diganti `_store_message_fields()`/`Store.FieldList` (pola `res.attr()`
  dkk, DIFF-01); (2) `messageActionsRegistry` — `canAddReaction` method→getter, filter Symbol
  `IS_ACTION_DEFINITION_SYM` via `registerMessageAction()`, wajib pakai helper resmi bukan `.add()`
  langsung (DIFF-02); (3) FontAwesome dihapus TOTAL dari `mail`, diganti Odoo Icons `oi`/`data-icon`
  (DIFF-04) — SANGAT UMUM untuk modul custom apapun yang menyisipkan `<i class="fa ...">` ke template
  `mail`, dampaknya jauh melampaui modul ini sendiri.
- [ ] **Kandidat `FINDINGS.md` — MF-29 baru (severity Tinggi, bukan Kritis):** DIFF-04 (icon FA→oi,
  termasuk 2 selector tour test yang ikut rusak) BELUM tercatat di `01a_MIGRATION_INTAKE.md`/
  `01b_BASELINE_SPEC.md`/`FINDINGS.md` manapun sebelum sesi ini — murni ditemukan step 2. Tulis
  sebagai `MF-29` di `FINDINGS.md`, tag `[GAP-MIGRASI]`.
- [ ] **Kandidat `FINDINGS.md` — MF-30 baru (severity Tinggi, RISIKO BUKAN mekanis):** DIFF-03
  (arsitektur `Chatter` dirombak jadi primitif signal/`propComputed`/`useOnChange`, path pindah ke
  `web_portal_project`) — eskalasi eksplisit untuk Step 6/9: fix path import saja TIDAK CUKUP untuk
  memastikan `initialLoad()`/`onWillUpdateProps` modul ini masih ter-trigger benar: WAJIB
  diverifikasi lewat tour test nyata (ganti-ganti thread di form view, bukan cuma load sekali) sebelum
  dianggap selesai.
- [ ] Promosi ke `knowledge/` HANYA lewat sesi curation terpisah (`templates/CURATION_PROMPT.md`),
  tidak dilakukan di step ini.

## 4. Ringkasan Risiko

| Item | Level risiko | Catatan |
|---|---|---|
| `DIFF-01` (`_to_store` → `_store_message_fields`) | **Kritis (silent, bukan crash) — TAPI mekanis** | Rewrite konkret sudah dikonfirmasi lewat 2 contoh native kerja (`rating`, `im_livechat`) + API `Store.FieldList.attr()` yang dibaca penuh. Step 3 bisa langsung menulis spec final tanpa riset tambahan. |
| `DIFF-02` (`messageActionsRegistry` — getter, filter Symbol, icon) | **Kritis (silent, action "Pin" tidak pernah muncul) — TAPI mekanis** | Tiga fix konkret (getter `canAddReaction`, helper `registerMessageAction()`, icon `"push_pin"`) sudah dikonfirmasi lewat kode native yang benar-benar dipakai ~15 action bawaan. |
| `DIFF-03` (arsitektur `Chatter` — Owl signal/`propComputed`/`useOnChange`, path `web_portal_project`) | **Tertinggi — BUKAN mekanis, wajib verifikasi eksekusi nyata** | Path import & pemanggilan `load()` sudah dikonfirmasi tetap valid secara SINTAKS, tapi INTERAKSI patch (`onWillUpdateProps` gaya lama di atas mekanisme deteksi-ganti-thread yang sudah diganti `useOnChange`) tidak bisa dipastikan BENAR tanpa tour test nyata berganti-ganti thread. **Jangan tutup Step 6 fase E untuk modul ini sebelum tour ini lulus di 20.0 sungguhan — risiko silent-UX-bug, bukan install-blocking, gampang terlewat kalau test cuma pakai satu thread.** |
| `DIFF-04` (FontAwesome → Odoo Icons `oi`) | **Tinggi (UI + 2 tour selector rusak) — mekanis** | Pola & nama icon pengganti (`push_pin`, `keyboard_arrow_down`/`chevron_right`, `more_vert`) sudah dikonfirmasi konkret dari banyak contoh native. Wajib disertakan di scope Step 3 meski bukan bagian dari `MF-28` awal. |
| `DIFF-05`, `DIFF-06`, `DIFF-07` | Tidak ada/Rendah | Konfirmasi stabil — xpath anchor, `Message` component, business-rule fields semua tidak berubah untuk kebutuhan modul ini. |

**Kesimpulan Step 2 modul ini:** `MF-28` (temuan Step 1) TERBUKTI benar arahnya (`_to_store()` memang
hilang total) TAPI kekhawatirannya bisa DITURUNKAN — pola pengganti `_store_message_fields()` +
`Store.FieldList.attr()` sudah dikonfirmasi mekanis lewat dua contoh native kerja nyata, jadi Step 3
bisa langsung menulis spec final untuk area ini tanpa riset tambahan. **DUA temuan BARU sesi ini yang
JUSTRU lebih berisiko dari `MF-28` untuk Step 3/6:**
1. `DIFF-03` (rombakan arsitektur `Chatter`) — **satu-satunya area di modul ini yang TIDAK bisa
   dipastikan mekanis** hanya dari baca kode statis; wajib tour test nyata sebelum Step 6 fase E
   ditutup untuk modul ini.
2. `DIFF-02`+`DIFF-04` (registry filter Symbol + penghapusan total FontAwesome dari `mail`) — dua pola
   SANGAT UMUM yang akan mempengaruhi modul custom LAIN manapun yang menyentuh action-menu
   pesan/chatter, layak dipromosikan ke `dependency-compat/mail/19-to-20.md` di sesi curation
   berikutnya (§3), tidak cukup diselesaikan diam-diam hanya untuk modul ini.

**Rekomendasi ke Step 3:** tulis `03_MIGRATION_SPEC.md` untuk `DIFF-01`, `DIFF-02`, `DIFF-04` sebagai
perubahan MEKANIS (kode pengganti sudah ada di §1 tabel di atas, siap disalin/disesuaikan). Untuk
`DIFF-03`, tulis spec dengan asumsi "path import diganti + logic dipertahankan apa adanya", TAPI beri
flag eksplisit ke Step 6 bahwa fase E modul ini WAJIB menyertakan skenario tour "ganti thread"
(pindah antar record chatter, bukan cuma satu record statis) sebelum dianggap lulus — jangan
diasumsikan aman hanya karena tidak ada error saat install/load pertama.
