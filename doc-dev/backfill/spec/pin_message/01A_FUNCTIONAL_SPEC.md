# Functional Spec — pin_message

**Module:** `pin_message`
**Odoo Version:** 17.0
**Depends:** `web`, `base`, `mail`
**Last Updated:** 2026-07-31
**Status:** Backfill retroaktif — dibaca dari kode existing, bukan requirement baru
**Provenance:** lihat `pos-margin-sale/CLAUDE.md` §Provenance Tag

> **Catatan scope:** modul ini TIDAK terkait fungsional dengan `pos_margin_threshold`/
> `sale_margin_threshold` — produk berbeda (fitur pin chatter) yang kebetulan di-bundle di repo yang
> sama. Lihat `pos-margin-sale/CLAUDE.md` §Identitas.

---

## Ringkasan untuk Review — Perlu Konfirmasi User

1. `[PERLU-KEPUTUSAN]` **F-06** — `onClickPin()` di `message.js` MENIMPA TOTAL (bukan extend lewat
   `super()`) patch core Odoo `discuss/message_pin` untuk `Message.prototype.onClickPin` — saat ini
   perilakunya kebetulan identik (dikonfirmasi baca source core), tapi berisiko silent-diverge kalau
   core berubah di versi Odoo mendatang.
2. `[PERLU-KEPUTUSAN]` **F-07** — `console.log(component.message.type)` tertinggal di kode produksi
   (`pinMessage.js`), dieksekusi setiap kali action registry menge-render tombol aksi pesan.

---

## Latar Belakang & Tujuan

Modul ini menambahkan kemampuan "pin" (menyematkan) pesan/log note penting di chatter — supaya
pesan penting tidak hilang di antara banyak pesan lain. `[HASIL-BACA]`

---

## Scope

### Yang Termasuk (disimpulkan dari kode)

- Field `is_pinned` di `mail.message` (baru, bukan bawaan core untuk model ini — core Odoo 17 punya
  fitur pin TAPI itu khusus untuk `discuss.channel` messages lewat mekanisme berbeda, field
  `pinned_at` yang tidak disentuh modul ini). `[HASIL-BACA]`
- Method `toggle_pin()` — flip `is_pinned`, kirim notifikasi realtime lewat `bus.bus` supaya UI
  update tanpa refresh. `[HASIL-BACA]`
- Action tombol "Pin" (key registry `"pins"`) khusus untuk pesan chatter TIPE LOG NOTE (bukan
  discussion/notification) — beririsan konsep dengan action native core `"pin"` (key berbeda,
  scope BERBEDA: core untuk `discuss.channel`, modul ini untuk chatter biasa — dikonfirmasi TIDAK
  tumpang tindih, lihat AC-02). `[HASIL-BACA]`
- Section "Pinned Messages" collapsible di atas chatter, menampilkan semua pesan `is_pinned=True`
  thread yang sedang dibuka. `[HASIL-BACA]`
- Tombol pin langsung di setiap bubble message chatter (ikon thumb-tack), toggle on-click.
  `[HASIL-BACA]`

### Yang Tidak Termasuk

- Tidak menyentuh mekanisme pin NATIVE Odoo untuk `discuss.channel` (`pinned_at`,
  `discuss.channel.set_message_pin`) — modul ini murni menambah fitur SERUPA untuk chatter model
  APAPUN (`res.partner`, `sale.order`, dst — chatter generik), bukan discuss channel.
  `[HASIL-BACA]`
- Tidak ada UI/setting untuk membatasi siapa yang boleh pin — semua user dengan akses tulis
  `mail.message` (yang berarti hampir semua internal user) bisa toggle pin pesan siapapun.
  `[HASIL-BACA]`

---

## User Stories (rekonstruksi)

### US-01 — User pin log note penting di chatter record apapun
Sebagai user, saya klik ikon pin di sebuah log note chatter (mis. di form Sale Order/Partner), pesan
itu masuk ke section "Pinned Messages" yang selalu terlihat di atas chatter. `[HASIL-BACA]`

### US-02 — User melihat jumlah pesan yang di-pin tanpa expand
Sebagai user, saya lihat badge angka jumlah pesan pinned di header section, tanpa perlu expand dulu.
`[HASIL-BACA]`

---

## Business Rules

> **Cek wajib tabrakan nama method Odoo core (Step 01):** `toggle_pin` (nama custom, tidak bentrok
> core). TAPI di sisi **JS**, `Message.prototype.onClickPin` (patch di `message.js`) BENTROK NAMA
> dengan patch core `odoo/addons/mail/static/src/discuss/message_pin/common/message_patch.js` yang
> JUGA mem-patch method dengan nama sama pada component yang sama. Override modul ini TIDAK
> memanggil `super.onClickPin()` — full replace, bukan extend. Dikonfirmasi (baca source core)
> perilaku SAAT INI identik/benign, tapi tetap tercatat sebagai pola berisiko. Lihat **F-06**.

### BR-01 — Toggle pin per pesan, broadcast realtime
`toggle_pin()` di-loop per record (`for message in self:`, aman untuk multi-record), flip boolean,
kirim `bus.bus._sendone` per pesan dengan payload `{id, is_pinned}`. `[HASIL-BACA]`
**Lokasi kode:** `models/mail_message.py:9-20`

### BR-02 — Dua jalur pin berbeda tergantung tipe pesan
`onClickPin()` (patch `message.js`) bercabang berdasar `this.message.is_discussion`:
- **True** (pesan discuss channel) → delegasi ke `messagePinService` core (`.pin()`/`.unpin()`,
  yang menampilkan dialog konfirmasi native core) — REIMPLEMENTASI manual logic yang SAMA dengan
  core, bukan panggil `super()`. `[PERLU-KEPUTUSAN]` — lihat **F-06**.
- **False** (log note/chatter) → RPC custom `mail.message.toggle_pin` (method BR-01), langsung
  tanpa dialog konfirmasi.
`[HASIL-BACA]`
**Lokasi kode:** `static/src/js/message.js:11-26`

### BR-03 — Action tombol pin di message actions menu, hanya untuk pesan non-discussion
Registry key `"pins"` — kondisi tampil: `canAddReaction` True, DAN pesan bukan discussion/
user_notification/auto_comment/notification, DAN tidak punya `subtype_description` (bukan
changelog-type message). `[HASIL-BACA]`
**Lokasi kode:** `static/src/js/pinMessage.js:5-26`

### BR-04 — Section Pinned Messages di-load sekali saat chatter mount/ganti thread
`initialLoad()` dipanggil di `onMounted` dan `onWillUpdateProps` (kalau `threadId`/`threadModel`
berubah) — fetch `mail.message` dengan domain `is_pinned=True` + `model`/`res_id` thread yang
sedang dibuka, lalu tandai `is_pinned` di message object lokal yang sudah ter-load. `[HASIL-BACA]`
**Lokasi kode:** `static/src/js/chatter.js:30-50`
