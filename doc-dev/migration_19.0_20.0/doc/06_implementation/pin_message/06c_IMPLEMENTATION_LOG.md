# Implementation Log — pin_message (19.0 → 20.0)

**Status:** 🔄 Hampir selesai — `MF-28`/`MF-32`/`MF-33`/`DIFF-04` semua diterapkan & diverifikasi
lebih awal dari urutan fase normal, atas permintaan dev untuk investigasi crash nyata yang ditemukan
saat review visual Docker 19.0 vs 20.0. Fitur pin/unpin end-to-end dikonfirmasi berfungsi via UI
nyata. Satu bug baru ditemukan (`MF-36`) di komponen NATIVE (bukan kode modul ini) saat expand
daftar pesan yang di-pin — di luar kendali modul, lihat `FINDINGS.md`.

**Tanggal:** 2026-09-22

---

## Perubahan yang sudah diterapkan

| Ref | Perubahan | File | Ref spec |
|---|---|---|---|
| — | Bump `version` → `20.0.1.0` (mekanis, syarat minimal install) | `__manifest__.py` | — |
| `MF-33` fix #1 | Import `Chatter` dari `@mail/chatter/web_portal/chatter` (hilang di 20.0) → `@mail/chatter/web_portal_project/chatter` | `static/src/js/chatter.js` | `FINDINGS.md` `MF-33` |
| `MF-33` fix #2 | Bare identifier (`pinnedMessages`/`state`/`togglePinnedMessages`/`props`) di node hasil `t-inherit-mode="extension"` tidak auto-resolve ke `this.xxx` di 20.0 — semua diberi prefix eksplisit `this.` (6 titik di `mail.Chatter` extension, 5 titik di `mail.Message` extension) | `static/src/xml/pinnedMessages.xml` | `FINDINGS.md` `MF-33` |
| `MF-28` | Rewrite `_to_store(store, fields, **kwargs)` → `_store_message_fields(res: Store.FieldList, **kwargs)` + `res.attr("is_pinned")`, pola native `rating`/`im_livechat` | `models/mail_message.py` | `03_MIGRATION_SPEC.md` §2b Blocker #2 |
| `MF-32` | Rewrite total: `messageActionsRegistry.add()` → `registerMessageAction()`, `canAddReaction(thread)` → getter `canAddReaction`, icon `"fa fa-thumb-tack"` → `"push_pin"` | `static/src/js/pinMessage.js` | `03_MIGRATION_SPEC.md` §2b Blocker #3 |
| `DIFF-04` | Icon FontAwesome → Odoo Icons: caret collapse (`arrow_drop_down`/`arrow_right`) + tombol pin inline (`push_pin`) | `static/src/xml/pinnedMessages.xml` | `03_MIGRATION_SPEC.md` §2b |
| `DIFF-04` | Update 3 selector tour test: `.fa-thumb-tack.*` → `i[data-icon='push_pin'].*`, `.fa-ellipsis-v` → `i[data-icon='more_vert']` | `static/tests/tours/pin_message_tour.js` | `03_MIGRATION_SPEC.md` §2b |

**Verifikasi end-to-end (browser nyata, bukan cuma baca kode):** tulis log note pada record Product
→ klik tombol pin inline → `is_pinned` tersimpan, section "Pinned Messages" muncul dengan badge
count "1" yang benar. Membuktikan `MF-28` (persistensi field) DAN `MF-32` (action/tombol genuinely
render & berfungsi) bekerja sama-sama, bukan cuma tidak error.

## Belum diterapkan / masih terbuka

- Tour test "pindah thread" untuk `MF-33` (rekomendasi asli finding, verifikasi manual sudah
  dilakukan tapi tour test otomatis formal belum ditulis).
- `MF-36` — crash di komponen native `mail.MessageCardList` saat expand section "Pinned Messages"
  (BUKAN bug modul ini, kemungkinan quirk dev-snapshot Odoo 20.0) — perlu re-test di rilis 20.0
  stabil, keputusan lanjutan ditunda sampai itu tersedia.

## Catatan proses — metodologi debug

Karena stack trace dari asset bundle terminifikasi tidak informatif, root cause `MF-33` fix #2
ditemukan dengan cara:
1. Buka `?debug=assets` untuk source map jelas (baris fungsi generated, bukan posisi bundle).
2. Akses `odoo.__WOWL_DEBUG__.root.__owl__.app.templates['mail.Chatter']` dari console browser —
   `app.templates` menyimpan fungsi JS hasil kompilasi QWeb per nama template, `.toString()`
   memberi source code lengkapnya.
3. Bandingkan baris yang crash (`ctx['pinnedMessages'].length`) dengan pola native di sekitarnya
   (`ctx['this'].attachments.length`) — beda prefix `ctx['this'].` inilah akar masalahnya.

Teknik ini (baca `app.templates[name].toString()` langsung dari browser) reusable untuk debug
crash QWeb serupa di project migrasi Odoo manapun — dicatat di sini supaya tidak perlu ditemukan
ulang dari nol.

**Insiden kecil selama proses:** komentar penjelasan yang ditambahkan untuk fix #2 sempat memuat
`--` (double-hyphen) di dalam XML comment — tidak valid, sempat merusak SELURUH asset bundle
webclient database ini (`Missing template: "web.WebClient"`) sampai diperbaiki (commit berikutnya).
Tidak ada database/data yang rusak permanen — murni asset bundle cache, pulih otomatis setelah
`-u pin_message` berikutnya.
