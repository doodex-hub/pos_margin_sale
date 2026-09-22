# Implementation Log — pin_message (19.0 → 20.0)

**Status:** 🔄 Sebagian — fix `Chatter`/`Message` (`MF-33`) sudah diterapkan lebih awal dari urutan
fase normal, atas permintaan dev untuk investigasi crash nyata yang ditemukan saat review visual
Docker 19.0 vs 20.0. `MF-28` (`_to_store`) dan `MF-32` (`messageActionsRegistry`) BELUM diterapkan.

**Tanggal:** 2026-09-22

---

## Perubahan yang sudah diterapkan

| Ref | Perubahan | File | Ref spec |
|---|---|---|---|
| — | Bump `version` → `20.0.1.0` (mekanis, syarat minimal install) | `__manifest__.py` | — |
| `MF-33` fix #1 | Import `Chatter` dari `@mail/chatter/web_portal/chatter` (hilang di 20.0) → `@mail/chatter/web_portal_project/chatter` | `static/src/js/chatter.js` | `FINDINGS.md` `MF-33` |
| `MF-33` fix #2 | Bare identifier (`pinnedMessages`/`state`/`togglePinnedMessages`/`props`) di node hasil `t-inherit-mode="extension"` tidak auto-resolve ke `this.xxx` di 20.0 — semua diberi prefix eksplisit `this.` (6 titik di `mail.Chatter` extension, 5 titik di `mail.Message` extension) | `static/src/xml/pinnedMessages.xml` | `FINDINGS.md` `MF-33` |

## Belum diterapkan (di luar scope investigasi ini)

- `MF-28`/`DIFF-01` — rewrite `_to_store()` → `_store_message_fields()` (`models/mail_message.py`) —
  solusi sudah konkret di `03_MIGRATION_SPEC.md`, belum dieksekusi.
- `MF-32`/`DIFF-02` — rewrite `messageActionsRegistry` (`static/src/js/pinMessage.js`) — solusi
  sudah konkret di `03_MIGRATION_SPEC.md`, belum dieksekusi.
- Update selector tour test (`static/tests/tours/`) untuk ikon FontAwesome→Odoo Icons.
- Tour test "pindah thread" untuk `MF-33` (rekomendasi asli finding, verifikasi manual sudah
  dilakukan tapi tour test otomatis formal belum ditulis).

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
