# Migration Spec (Teknis) — pin_message

**Step:** 3 — Migration Spec
**Versi:** 19.0 → 20.0
**Ref:** `02_diff/pin_message/02_DIFF_ANALYSIS.md`
**Tanggal:** 2026-09-22

> Dokumen ini memandu IMPLEMENTASI (step 6). Ini **bukan** dasar testing/acceptance criteria —
> itu datang dari `01b_BASELINE_SPEC.md` (step 1) dan kode 19.0 aktual (`migration/19.0`). Lihat
> step 5.

---

## 1. Ringkasan Strategi

Modul ini punya **tiga area WAJIB rewrite mekanis** (pola pengganti sudah dikonfirmasi konkret dari
kode native yang benar-benar jalan, bukan tebakan) dan **satu area yang HANYA butuh perubahan
import path — logic patch-nya sendiri TIDAK di-rewrite — tapi wajib verifikasi eksekusi nyata
sebelum ditutup**:

1. **`DIFF-01`** — `_to_store()` dihapus total dari `mail.message` core 20.0. Diganti
   `_store_message_fields(self, res: Store.FieldList, **kwargs)`. Rewrite mekanis, pola dikonfirmasi
   dari 2 override native (`rating`, `im_livechat`).
2. **`DIFF-02`** — `messageActionsRegistry.add()` langsung (bukan lewat helper) sekarang **di-filter
   keluar senyap** oleh mekanisme `IS_ACTION_DEFINITION_SYM`; `canAddReaction` berubah dari method
   jadi getter; FontAwesome dihapus dari icon action (`"fa fa-thumb-tack"` → `"push_pin"`). Rewrite
   mekanis, tiga fix dikonfirmasi dari ~15 action bawaan native yang sudah pakai pola ini.
3. **`DIFF-04`** — FontAwesome dihapus TOTAL dari seluruh template `mail` (0 match `fa fa-`/`class="fa
   `). Dua icon di `pinnedMessages.xml` (caret collapse/expand, tombol pin inline) dan dua selector
   CSS di tour test (`pin_message_tour.js`) harus diganti ke sistem Odoo Icons (`oi`/`data-icon`).
   Rewrite mekanis, nama icon pengganti (`push_pin`, `keyboard_arrow_down`/`chevron_right`,
   `more_vert`) sudah dikonfirmasi dari banyak contoh native.
4. **`DIFF-03`** — komponen native `Chatter` pindah path (`@mail/chatter/web_portal/chatter` →
   `@mail/chatter/web_portal_project/chatter`) DAN di-rewrite total secara internal (primitif Owl
   `signal`/`propComputed`/`useOnChange`, bukan lagi `useState`/props mentah + `onWillUpdateProps`
   manual). **Spec ini TIDAK mengusulkan rewrite logic patch (`chatter.js`) mengikuti primitif baru
   itu** — hanya perbaikan import path, logic `setup()`/`initialLoad()`/`onWillUpdateProps` modul ini
   dipertahankan apa adanya (konsisten rekomendasi `02_DIFF_ANALYSIS.md` §4: "tulis spec dengan
   asumsi path import diganti + logic dipertahankan apa adanya"). **INI BUKAN klaim "aman"** — native
   sekarang sudah punya mekanisme reload otomatisnya sendiri lewat `useOnChange` (lihat §2b, baris
   `DIFF-03` lanjutan, temuan baru sesi ini) yang duplikat sebagian dengan `initialLoad()` modul ini;
   apakah hook `onWillUpdateProps` modul ini MASIH ter-trigger dengan timing yang benar terhadap
   thread baru TIDAK bisa dipastikan dari baca kode statis. **Step 6 WAJIB menutup fase E modul ini
   dengan tour "ganti thread" nyata** (lihat §2b "Urutan Prioritas Testing" butir 6) sebelum dianggap
   selesai — kalau tour itu gagal, itu jadi keputusan/eskalasi terpisah di Step 6 (mis. migrasi ke
   `useOnChange` mengikuti pola native), bukan diasumsikan sekarang.

Sisanya (`DIFF-05` xpath anchor, `DIFF-06` `message.js`, `DIFF-07` business-rule fields) dikonfirmasi
**tidak berubah** — tidak butuh aksi. Manifest version dibump ke `20.0.1.0`.

## 2. Strategi per File/Simbol (ringkasan umum)

| File/simbol | Ref `DIFF-NNN` (02_DIFF_ANALYSIS §1) | Strategi migrasi | Risiko | Ref `BSL-NNN` |
|---|---|---|---|---|
| `models/mail_message.py:22-36` — override `_to_store()` | `DIFF-01` | **Rewrite total nama+signature+body**, lihat kode konkret §2b Critical Blockers #2 | Kritis (silent — `is_pinned` hilang dari payload tanpa error), TAPI mekanis | `BSL-007` |
| `static/src/js/pinMessage.js` (seluruh file, 27 baris) | `DIFF-02` | **Rewrite total**: `messageActionsRegistry.add()` → `registerMessageAction()`, `message.canAddReaction(thread)` → `message.canAddReaction` (getter, drop parameter `thread`), `icon: "fa fa-thumb-tack"` → `icon: "push_pin"`. Lihat kode konkret §2b Critical Blockers #3 | Kritis (silent — action "Pin" tidak pernah muncul), TAPI mekanis | `BSL-004`, `BSL-005`, `BSL-017` |
| `static/src/js/chatter.js:4` — `import { Chatter } from "@mail/chatter/web_portal/chatter"` | `DIFF-03` | **Ganti import path SAJA** → `@mail/chatter/web_portal_project/chatter`. Body `patch()` (`setup`/`initialLoad`/`onMounted`/`onWillUpdateProps`) **tidak diubah** | **Tertinggi, BUKAN mekanis** — wajib tour "ganti thread" sebelum ditutup (lihat §1 butir 4, §2b) | `BSL-008`, `BSL-009`, `BSL-010` |
| `static/src/xml/pinnedMessages.xml:12-13` (caret) dan `:40-45` (tombol pin inline) | `DIFF-04` | Ganti `<i class="fa ...">` → `<i class="oi" data-icon="...">`. Kode konkret §2b OWL Widget/Estimasi Effort | Tinggi (UI, fungsional tetap jalan tapi ikon bisa kotak kosong kalau tidak diganti) — mekanis | `BSL-011`, `BSL-017` |
| `static/tests/tours/pin_message_tour.js:35,55,101` — selector `.fa-thumb-tack.*`/`.fa-ellipsis-v` | `DIFF-04` | Update selector CSS ke `[data-icon="push_pin"]`/`[data-icon="more_vert"]` beserta class warna | Tinggi (test false-negative kalau tidak diupdate) — mekanis | — |
| `static/src/js/message.js` (seluruh file) | `DIFF-06` | **Tidak ada perubahan** — path import, `setup()`, getter `this.message`, `this.props.message.id` semua dikonfirmasi stabil | Tidak ada | `BSL-002`, `BSL-003`, `BSL-015`, `BSL-016` |
| `static/src/xml/message_card_list.xml` | `DIFF-05` | **Tidak ada perubahan** — xpath anchor `o-mail-MessageCard-jump` stabil | Tidak ada | `BSL-013` |
| `pinMessage.js` business-rule fields (`is_discussion`/`message_type`/`subtype_description`) | `DIFF-07` | **Tidak ada perubahan** — field-field ini stabil di `message_model.js` 20.0 | Rendah | `BSL-004` |
| `__manifest__.py:3` | — | Bump `'version': '19.0.1.0'` → `'20.0.1.0'` | Tidak ada | — |

## 2b. Risk Analysis Terstruktur (detail, per kategori)

### Critical Migration Blockers
*(Mencegah instalasi atau operasi inti di 20.0 — di sini bersifat SILENT, bukan crash instalasi;
lihat catatan di tiap baris)*

| # | Isu | Lokasi | Rujukan knowledge base |
|---|---|---|---|
| 1 | Manifest version — harus `20.0.x.x` | `__manifest__.py` | `knowledge/version-diffs/19-to-20.md` |
| 2 | `_to_store()` dihapus total dari core — override modul jadi method mati (tidak pernah dipanggil siapapun), `is_pinned` hilang total dari payload store TANPA error apapun (silent, bukan crash — beda dari 18→19 yang crash total) | `models/mail_message.py:22-36` | `FINDINGS.md` `MF-28`, `02_DIFF_ANALYSIS.md` `DIFF-01` |
| 3 | `messageActionsRegistry.add()` langsung di-filter keluar senyap oleh `IS_ACTION_DEFINITION_SYM` (hanya terpasang via `registerMessageAction()`) DAN `condition` callback akan `TypeError` (`canAddReaction` sekarang getter, bukan method) — dua kegagalan independen, keduanya wajib fix | `static/src/js/pinMessage.js:5-27` | `FINDINGS.md` `MF-32`, `02_DIFF_ANALYSIS.md` `DIFF-02` |

**Priority:** HIGH — perbaiki #2 dan #3 sebelum runtime testing apapun. Berbeda dari migrasi
18.0→19.0 (di mana kegagalan langsung `TypeError` pada instalasi/pemuatan chatter apapun), kegagalan
di 19.0→20.0 untuk modul ini **senyap** — install & chatter tetap jalan normal, fitur pin hilang
tanpa jejak error. Jangan andalkan "tidak ada error di console" sebagai bukti lulus.

**Kode konkret #2 — `models/mail_message.py`, rewrite penuh method (baris 22-36):**

```python
from odoo import models, fields, api
from odoo.addons.mail.tools.discuss import Store


class Message(models.Model):
    _inherit = 'mail.message'

    is_pinned = fields.Boolean(string='Pinned', default=False, index=True)

    def toggle_pin(self):
        for message in self:
            message.is_pinned = not message.is_pinned
            self.env['bus.bus']._sendone(
                f'{self._name},{message.id}',
                'mail.message/pin_changed',
                {
                    'id': message.id,
                    'is_pinned': message.is_pinned,
                }
            )
        return True

    def _store_message_fields(self, res: Store.FieldList, **kwargs):
        # 20.0: `_to_store(self, store, fields, **kwargs)` dihapus TOTAL dari core (0 match
        # `_to_store`/`to_store` di odoo20/addons/mail/models/mail_message.py) -- diganti pola
        # serializer field-list `_store_message_fields(self, res: Store.FieldList, **kwargs)`
        # (odoo20/addons/mail/models/mail_message.py:1177, tipe `Store.FieldList` didefinisikan
        # odoo20/addons/mail/tools/discuss.py:830-963). Pola rewrite ini PERSIS sama dengan dua
        # override native yang sudah jalan untuk kasus identik (tambah satu field ke store pesan
        # tanpa syarat): odoo20/addons/rating/models/mail_message.py:41-44 dan
        # odoo20/addons/im_livechat/models/mail_message.py:10-11.
        super()._store_message_fields(res, **kwargs)
        # `res.attr(field_name)` tanpa value/predicate/sudo custom cukup untuk field yang SELALU
        # dikirim tanpa syarat -- behavior-nya cuma append field_name ke list yang nanti dibatch
        # lewat _read_format() (discuss.py:860-868), sama seperti is_pinned di 19.0 lewat
        # store.add_records_fields(self, ['is_pinned']) tapi TANPA butuh API itu sama sekali.
        res.attr("is_pinned")
```

`toggle_pin()` **tidak berubah sama sekali** (`BSL-001`/`BSL-006`) — bagian yang di-rewrite murni
method serialisasi-ke-frontend.

**Kode konkret #3 — `static/src/js/pinMessage.js`, rewrite total (seluruh file):**

```js
/* @odoo-module */
import { _t } from "@web/core/l10n/translation";
import { registerMessageAction } from "@mail/core/common/message_actions";

registerMessageAction("pins", {
    condition: ({ message }) => {
        if (!message.canAddReaction) {
            return false;
        }

        const isNote = !message.is_discussion &&
                       message.message_type !== "user_notification" &&
                       message.message_type !== "auto_comment" &&
                       message.message_type !== "notification";

        const isNotChangeLog = !message.subtype_description ||
                              message.subtype_description === "";

        return isNote && isNotChangeLog;
    },
    // 20.0: FontAwesome dihapus total dari template `mail` (0 match "fa fa-"/'class="fa '　di
    // seluruh mail/static/src/**/*.xml/js) -- icon sekarang nama Odoo Icon polos, dirender lewat
    // <i class="oi" t-att-data-icon="..."/>. "push_pin" dikonfirmasi nama resmi untuk konsep pin
    // (dipakai native sendiri, message_model.js get notificationIcon() case "pin").
    icon: "push_pin",
    name: _t("Pin"),
    onSelected: ({ owner }) => owner.onClickPin(),
    sequence: 15,
});
```

Tiga perubahan dalam satu rewrite ini:
1. **Import & registrasi:** `messageActionsRegistry.add("pins", {...})` → `registerMessageAction("pins", {...})`
   (import dari `@mail/core/common/message_actions`, nama berbeda tapi path modul sama). Helper ini
   menempel Symbol privat `IS_ACTION_DEFINITION_SYM` (`action.js:23`) ke definisi — tanpa ini, entry
   LOLOS registrasi tanpa error tapi di-filter keluar sebelum dirender oleh `action.js:868-870`
   (`actionRegistry.getEntries().filter(([id, def]) => def?.[IS_ACTION_DEFINITION_SYM])`).
2. **Getter, bukan method:** `if (!message.canAddReaction(thread))` → `if (!message.canAddReaction)`.
   Native (`message_model.js:582-589`) sudah menjadikan ini getter yang meng-include cek `thread`
   secara internal (`this.thread?.can_react`, dst) — parameter `thread` di callback `condition`
   sudah tidak diperlukan lagi untuk pemanggilan ini (masih tersedia dari registry kalau modul butuh
   di masa depan, cukup di-drop dari destructure karena tidak dipakai di tempat lain pada file ini).
3. **Icon:** `"fa fa-thumb-tack"` → `"push_pin"` (lihat DIFF-02/DIFF-04, dikonfirmasi via
   `message_model.js:484-491` `get notificationIcon()` case `"pin"`).

**Catatan risiko baru (informasi, bukan blocker) — ditemukan sesi ini saat verifikasi native:**
`odoo20/addons/mail/static/src/core/public_web/message_actions_patch.js` sekarang mendaftarkan
action registry key **native** `"pin"`/`"unpin"` (singular, beda dari `"pins"` jamak milik modul
ini — **dikonfirmasi ulang TIDAK ada kolisi nama key**, konsisten temuan spec 18.0→19.0 sebelumnya),
memakai icon **SAMA** `"push_pin"`, tapi mekanismenya BEDA TOTAL — action native ini untuk pin level
Discuss-channel (`message.channel_id.messagePin()`/`messageUnpin()`, guard
`!owner.env.inMessagingMenu`, dst), bukan untuk pin chatter/log-note seperti modul ini. Fungsional
tidak konflik (kondisi visibility keduanya saling eksklusif berdasar `is_discussion`/`message_type`),
tapi dua action "Pin" dengan ikon identik bisa muncul berdampingan secara visual di pesan Discuss —
murni catatan UX untuk kewaspadaan review Step 9/10, bukan business-rule yang perlu diubah.

### OWL Widget yang Butuh Rewrite/Review

| Widget | File | Risiko | Detail |
|---|---|---|---|
| `messageActionsRegistry` entry `"pins"` (registry extension, bukan komponen Owl baru) | `static/src/js/pinMessage.js` | Kritis, mekanis | Lihat kode konkret Critical Blockers #3 di atas |
| `patch(Chatter.prototype, ...)` | `static/src/js/chatter.js` | **Tertinggi, BUKAN mekanis** | Hanya import path yang diganti (lihat §2b lanjutan "Detail `DIFF-03`" di bawah); logic patch dipertahankan; WAJIB tour ganti-thread sebelum G2 |
| `patch(Message.prototype, ...)` | `static/src/js/message.js` | Tidak ada | Dikonfirmasi stabil penuh — `DIFF-06` |

**Detail `DIFF-03` (Chatter) — perubahan yang DIUSULKAN vs yang TIDAK:**

- **Diusulkan (mekanis):** ganti baris impor saja —
  `import { Chatter } from "@mail/chatter/web_portal/chatter";` →
  `import { Chatter } from "@mail/chatter/web_portal_project/chatter";`
  (path lama 0 match di `odoo20`/`enterprise20`; path baru dikonfirmasi masuk bundle
  `web.assets_backend` yang sama lewat `mail/__manifest__.py`).
- **TIDAK diusulkan:** menulis ulang `setup()`/`initialLoad()`/`onWillUpdateProps` mengikuti primitif
  baru native (`signal`/`propComputed`/`useOnChange`). Business behavior (initial load pesan +
  pinned messages saat mount, refresh saat ganti thread) harus tetap identik ke 19.0 — mengubah
  mekanisme internal tanpa bukti kebutuhan adalah refactor di luar scope (dilarang `CLAUDE.md`
  §"Source of Truth & Forbidden Actions" kecuali wajib untuk kompatibilitas).
- **Temuan baru sesi ini (memperkuat, bukan menggantikan, `MF-33`):** dibaca langsung
  `odoo20/addons/mail/static/src/chatter/web_portal_project/chatter.js:47-65` — native SEKARANG
  sudah punya mekanisme reload otomatisnya sendiri: `useOnChange(() => [this.threadId(),
  this.threadModel()], (threadId, threadModel) => this.changeThread(...), {initialRun: false})`
  (mendeteksi ganti thread) DAN `useOnChange(() => [this.state.thread], (thread) => {
  ...this.load(thread, this.initialRequestList); }, {initialRun: false})` (auto-fetch pesan begitu
  `this.state.thread` berubah). Ini artinya **native sendiri sudah memuat ulang `messages` secara
  otomatis saat thread berganti** — method `initialLoad()` modul ini (yang memanggil
  `this.load(this.state.thread, ["messages"])` lalu `orm.searchRead` khusus `is_pinned`) jadi
  **sebagian redundan** dengan mekanisme native untuk bagian `messages`-nya, TAPI bagian
  `searchRead` pinned-messages tetap SATU-SATUNYA jalur yang mengisi `is_pinned` ke state lokal —
  kalau hook `onWillUpdateProps` modul ini tidak lagi ter-trigger benar (karena native tidak lagi
  mengandalkan hook itu, gantinya `useOnChange` berbasis signal), efeknya SPESIFIK: pesan lain
  ter-refresh normal (lewat mekanisme native), TAPI **Pinned Messages tidak ikut ter-refresh** saat
  pindah thread — silent, gampang terlewat kalau tour cuma menguji satu thread. Ini memperkuat,
  bukan mengganti, kesimpulan `MF-33`/`DIFF-03` bahwa hanya eksekusi nyata yang bisa memastikan.

### Controller & Route

| # | Isu | Lokasi | Priority |
|---|---|---|---|

Tidak ada — modul ini tidak punya folder `controllers/` sama sekali (dikonfirmasi
`01a_MIGRATION_INTAKE.md` §2b).

### Assets & Dependency

Tidak ada perubahan path asset — seluruh file `static/src/{css,js,xml}` dan
`static/tests/tours/**/*` tetap terdaftar sama persis di `assets.web.assets_backend`/
`web.assets_tests` (`__manifest__.py`). Dependency manifest (`web`, `base`, `mail`) tidak berubah,
tidak ada OCA/third-party.

### Kompatibilitas Data Model

| # | Isu | Lokasi | Priority | Ref `BSL-NNN` |
|---|---|---|---|---|
| 1 | `is_pinned` (Boolean, `default=False`, `index=True`) — tidak berubah struktur field sama sekali | `models/mail_message.py:7` | Tidak ada aksi | §3 `01b_BASELINE_SPEC.md` |
| 2 | Override serialisasi ke frontend (`_to_store()` → `_store_message_fields()`) | `models/mail_message.py:22-36` | **Kritis, lihat Critical Blockers #2** | `BSL-007` |

### Risiko Integrasi

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | `this.messagePinService` (cabang dead code `is_discussion`) — dikonfirmasi ULANG tetap tidak ada sebagai service terdaftar di `mail` 20.0 (`DIFF-06`, grep 0 match), aman dipertahankan as-is | `static/src/js/message.js` | Rendah — warisan (`BSL-016`) |
| 2 | Dua entry-point UI pin (`onClickPin` action-menu vs `onMessagePin` tombol inline) tetap divergen percabangan `is_discussion` dan error-handling — perilaku warisan, bukan bug baru migrasi ini | `static/src/js/message.js` | Tidak ada — dipertahankan (`BSL-015`) |
| 3 | Action registry native baru `"pin"`/`"unpin"` (`message_actions_patch.js`) pakai icon sama `"push_pin"` tapi mekanisme beda total (level Discuss-channel, bukan chatter/log-note) — tidak collide key, murni catatan kewaspadaan UX | `static/src/js/pinMessage.js` | Rendah — informasi baru sesi ini, lihat catatan di Critical Blockers #3 |

### Urutan Prioritas Testing

1. **Install & startup** — manifest version `20.0.1.0`, dependency (`web`/`base`/`mail` tetap
   Community).
2. **Buka chatter APAPUN (bukan cuma yang ada pesan pin)** — pastikan tidak ada error apapun
   (install/load), dan `is_pinned` benar-benar muncul di payload store (`_store_message_fields`
   fix, `DIFF-01`) — verifikasi lewat inspeksi state Owl/network, BUKAN cuma "tidak ada error di
   console" (kegagalan di sini SENYAP, beda dari 18→19).
3. **Hover/klik pesan APAPUN untuk buka action-menu** — verifikasi getter `canAddReaction`
   (`DIFF-02`) tidak `TypeError` UNTUK SEMUA pesan yang di-render, DAN entry "Pin" benar-benar
   RENDER di action-menu untuk pesan yang memenuhi syarat (bukan cuma tidak error — filter Symbol
   bisa lolos tanpa error tapi entry tetap tidak muncul).
4. **Cek visual icon** — tombol pin inline & entry action-menu "Pin" tampil sebagai ikon `push_pin`
   yang benar (bukan kotak kosong) di kedua state (pinned/unpinned) — verifikasi `DIFF-04`.
5. **Fitur pin sesungguhnya** — tombol inline (`onMessagePin`) dan action-menu "Pin" (`onClickPin`
   via `DIFF-02` fix) — keduanya harus toggle `is_pinned`, badge jumlah, section "Pinned Messages"
   collapse/expand.
6. **WAJIB — tour "ganti thread"** (belum ada di suite tour existing, harus ditambahkan Step 6/9):
   buka chatter di satu record (mis. invoice A), pin satu pesan, pindah ke record LAIN (invoice B,
   BUKAN reload record yang sama) lewat form view, verifikasi section "Pinned Messages" ter-refresh
   sesuai thread baru (kosong kalau B tidak punya pesan pinned, bukan menampilkan sisa data thread
   A). Lihat `DIFF-03`/`MF-33` — risiko silent, hanya kelihatan dari eksekusi nyata multi-thread.
7. **Discuss-channel native pin/unpin** (jalur `is_discussion` dead code DAN action registry native
   baru `"pin"`/`"unpin"`) — verifikasi tetap berfungsi penuh lewat mekanisme native, tidak
   terganggu modul ini (§2b Risiko Integrasi #3).
8. **Tour test lama** (`pin_message_toggle_pin_tour`, `pin_message_action_menu_pin_visible_tour`) —
   update selector dulu sesuai `DIFF-04`, baru dijalankan sebagai regression check otomatis.

### View List (dulu Tree) Checklist

N/A — modul ini tidak punya `ir.ui.view`/`views/*.xml` sama sekali (`data: []` di manifest, seluruh
UI lewat Owl QWeb `t-inherit`, dikonfirmasi `01a_MIGRATION_INTAKE.md` §2b).

### Estimasi Effort (opsional)

| Area | Effort | Catatan |
|---|---|---|
| `_store_message_fields()` rewrite | Kecil | Satu method, pola sudah terverifikasi lewat 2 contoh native kerja nyata |
| `messageActionsRegistry` rewrite (`pinMessage.js`) | Sedang | Tiga perubahan sekaligus (helper, getter, icon) dalam satu file kecil — perlu teliti, bukan tebak-tebak |
| `chatter.js` import path | Kecil (kode) / **Sedang-Tinggi (testing)** | Satu baris impor, tapi wajib tour ganti-thread BARU yang belum ada di suite existing |
| Icon FA→`oi` (`pinnedMessages.xml` + `pin_message_tour.js`) | Sedang | 2 file produksi (2 icon) + 1 file test (3 selector) — perlu cek visual manual Step 6/9, bukan cuma sintaks |
| Sisanya (`message.js`, `message_card_list.xml`, `DIFF-07` fields) | Nol | Dikonfirmasi stabil, tidak perlu disentuh |

## 3. Data Migration (ringkas — detail di step 7)

N/A — port kode saja (asumsi carry-forward, lihat `CLAUDE.md` §Identitas dan
`01a_MIGRATION_INTAKE.md` §3). `is_pinned` tidak berubah struktur field, tidak ada data existing yang
perlu ditransformasi.

## 4. Scope

### Termasuk
- `DIFF-01` — rewrite `_to_store()` → `_store_message_fields()` (kode konkret §2b).
- `DIFF-02` — rewrite total `pinMessage.js` (`registerMessageAction`, getter `canAddReaction`, icon
  `push_pin`) (kode konkret §2b).
- `DIFF-03` — ganti import path `chatter.js` ke `@mail/chatter/web_portal_project/chatter` SAJA;
  logic patch dipertahankan. Ditambah **tour "ganti thread" baru** sebagai syarat wajib penutupan
  fase E Step 6 untuk modul ini (belum ada di suite existing — bukan port, tapi test baru yang
  dibutuhkan untuk membuktikan port lama masih valid).
- `DIFF-04` — icon FontAwesome → Odoo Icons di `pinnedMessages.xml` (caret + tombol pin inline) dan
  update 3 selector di `pin_message_tour.js`.
- Bump `__manifest__.py` version ke `20.0.1.0`.

### Di Luar Scope (sengaja, disetujui di intake/step 2)
- `BSL-002`/`BSL-016` — dead code `is_discussion`/`this.messagePinService` — dipertahankan as-is,
  tidak dibersihkan (konsisten keputusan project 18.0→19.0, tidak ada permintaan baru untuk ini).
- `BSL-015` — dua entry-point UI (`onClickPin`/`onMessagePin`) yang divergen error-handling —
  dipertahankan as-is, bukan bug yang diperbaiki di migrasi ini.
- Rewrite logic internal `chatter.js` mengikuti primitif Owl baru native (`signal`/`propComputed`/
  `useOnChange`) — TIDAK dilakukan preventif. Hanya jadi in-scope kalau tour ganti-thread (§2b butir
  6 Urutan Prioritas Testing) di Step 6/9 MEMBUKTIKAN ada regresi nyata — keputusan itu dieskalasi
  terpisah saat itu terjadi, bukan diasumsikan sekarang.
- `message.js` (`DIFF-06`), `message_card_list.xml` (`DIFF-05`), business-rule fields `pinMessage.js`
  (`DIFF-07`) — dikonfirmasi stabil, tidak disentuh.
