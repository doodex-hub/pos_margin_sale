# Diff & Compatibility Analysis — pin_message

**Step:** 2 — Diff & Compatibility Analysis
**Versi:** 17.0 → 18.0
**Tanggal:** 2026-08-24
**Ref:** `01_intake/pin_message/01a_MIGRATION_INTAKE.md`, `01_intake/pin_message/01b_BASELINE_SPEC.md`, `migration-tool/knowledge/`

> **Batasan metodologis PENTING — baca sebelum §1:** dev sudah mengonfirmasi (Step 1) **tidak ada
> `native-target`/`native-target-enterprise`/`third-party-*` yang tersedia di disk** untuk project
> ini. Analisis di bawah TIDAK bisa memverifikasi langsung ke source code Odoo 18.0 core (`mail`
> module) — disusun dari (a) `migration-tool/knowledge/version-diffs/17-to-18.md` (item yang sudah
> tervalidasi project migrasi lain), dan (b) pengetahuan umum AI soal evolusi arsitektur `mail`/
> `discuss` module Odoo (TIDAK tervalidasi cross-check source resmi 18.0 — confidence LEBIH RENDAH
> dari entry knowledge base yang sudah dieksekusi nyata). **Setiap baris di §1 yang ditandai
> `[TIDAK TERVERIFIKASI]` WAJIB dicek ulang empiris di Step 6 (install Docker, G1) sebelum dianggap
> final** — jangan diperlakukan sebagai kepastian.

---

## 0. Knowledge Base Check

| Sumber | Sudah ada entry? | Lokasi |
|---|---|---|
| `version-diffs/17-to-18.md` | Ya | Dibaca penuh sesi ini — relevan §1 (tree→list, chatter div, Owl JS/template order, `useService("rpc")` dihapus), §1b (Owl Component API, JS module system) |
| `dependency-compat/mail/17-to-18.md` (atau nama serupa) | **Tidak ada** | Tidak ada entry dependency-compat khusus `mail`/`discuss` module dari project migrasi manapun sebelumnya — modul ini jadi yang PERTAMA di migration-tool yang menyentuh area ini secara signifikan |

## 0b. Gate Community vs Enterprise

- [x] Dicek `01a_MIGRATION_INTAKE.md` §2 — semua dependency (`web`, `base`, `mail`) Native Community, **tidak ada baris Enterprise**. Gate ini **N/A**, lanjut §1 tanpa `native-target-enterprise`.

## 0c. Gate Transitive Dependency

- [x] Tidak ada dependency yang akan dihapus dari `depends` modul ini (scope migrasi: port kode saja, `depends` tetap `web`/`base`/`mail`). Gate ini **N/A**.

---

## 1. Perubahan Native (Core/Enterprise)

| ID | File/simbol modul | Simbol native terkait | Status di target | Dampak | Sumber |
|---|---|---|---|---|---|
| DIFF-01 | `static/src/xml/pinnedMessages.xml` — `t-inherit="mail.Chatter"`, xpath `//div[hasclass('o-mail-Chatter-topbar')]` | Struktur QWeb template `mail.Chatter` (komponen inti) | **[TIDAK TERVERIFIKASI]** — kemungkinan berubah | **Tinggi** — kalau class `o-mail-Chatter-topbar` di-rename/struktur DOM berubah di 18.0, xpath ini gagal match saat load (`ParseError` di install/upgrade), fitur "Pinned Messages" section tidak akan pernah muncul | Pengetahuan umum AI (arsitektur `mail`/`discuss` OWL termasuk area yang sering direstruktur antar versi mayor) — **BUKAN** dari cross-check source 18.0 langsung |
| DIFF-02 | `static/src/xml/pinnedMessages.xml` — `t-inherit="mail.Message"`, xpath `//span[hasclass('o-mail-Message-author')]` | Struktur QWeb template `mail.Message` | **[TIDAK TERVERIFIKASI]** | **Tinggi** — sama pola risiko DIFF-01, kalau gagal match, tombol pin inline (`onMessagePin`) tidak akan pernah muncul di bubble message | Sama seperti DIFF-01 |
| DIFF-03 | `static/src/xml/message_card_list.xml` — `t-inherit="mail.MessageCardList"`, xpath `//button[contains(@class,'o-mail-MessageCard-jump')]` | Struktur QWeb template `mail.MessageCardList` | **[TIDAK TERVERIFIKASI]** | Sedang — kalau gagal match, cuma styling tombol "See" di section Pinned Messages yang terpengaruh (fitur inti pin/unpin tetap jalan) | Sama seperti DIFF-01 |
| DIFF-04 | `static/src/js/{message,chatter}.js` — `import { Message } from "@mail/core/common/message"`, `import { Chatter } from "@mail/core/web/chatter"` | Path modul JS `@mail/core/common/message`, `@mail/core/web/chatter` | **[TIDAK TERVERIFIKASI]** | **Tinggi** — kalau path/nama export pindah (riwayat historis `mail` module sering reorganisasi folder `static/src/`), `import` gagal resolve, SELURUH bundle JS `web.assets_backend` modul ini gagal load (bukan cuma fitur pin — App JS Odoo yang bundling bisa ikut gagal load kalau satu modul dalam bundle sama error saat resolve import, tergantung strategi bundling 18.0) | Pengetahuan umum AI — path import spesifik ini tidak bisa dipastikan tanpa lihat source 18.0 langsung |
| DIFF-05 | `static/src/js/pinMessage.js` — `import { messageActionsRegistry } from "@mail/core/common/message_actions"` | Registry `messageActionsRegistry`, path `@mail/core/common/message_actions` | **[TIDAK TERVERIFIKASI]** | Tinggi — kalau registry key/API `.add()` berubah, action tombol "pins" di menu aksi pesan hilang total | Sama seperti DIFF-04 |
| DIFF-06 | `static/src/js/message.js` — `this.messagePinService.getPinnedAt(id)`/`.pin()`/`.unpin()` (diakses langsung tanpa `useService` eksplisit di modul ini — mengandalkan core `Message` component sudah meng-inject property ini) | Property `messagePinService` pada instance `Message` component core | **[TIDAK TERVERIFIKASI]** | **Tinggi** — kalau core mengubah cara servicenya diakses (mis. jadi eksplisit `useService("messagePin")` di setiap component, bukan property otomatis), akses `this.messagePinService` di modul ini `undefined`, `onClickPin()` untuk pesan Discuss (`is_discussion=True`) crash `TypeError` | Pengetahuan umum AI, dikombinasi dengan pola `useService("rpc")` yang TERBUKTI dihapus sebagai auto-inject service di 18.0 (§1c knowledge base, dari `purchase_product_optional`) — pola perubahan serupa (service jadi eksplisit/fungsi biasa) punya preseden nyata di versi ini, memperkuat kecurigaan (bukan cuma spekulasi acak), TAPI tetap belum dikonfirmasi khusus untuk `messagePinService` |
| DIFF-07 | `static/src/js/{chatter,message}.js` — `useService("orm")` | Service `orm` | Kemungkinan besar **tetap ada** (service inti, bukan service spesifik-fitur seperti `rpc` yang dihapus) | Rendah | Pengetahuan umum AI — `orm` adalah service fundamental dipakai luas di seluruh Odoo webclient, jauh lebih stabil daripada `rpc` yang memang secara spesifik direstrukturisasi jadi fungsi biasa (lihat knowledge base §1c) |
| DIFF-08 | Seluruh modul — tidak ada `<tree>` XML view sama sekali (modul ini `data: []`, semua UI lewat QWeb JS template) | `<tree>`→`<list>` (Critical Migration Blocker versi lain) | **N/A** | — | Verifikasi statis langsung (baca seluruh file `static/src/xml/*.xml`) — dikonfirmasi tidak ada tag `<tree>` |
| DIFF-09 | Seluruh modul — sudah pakai `/** @odoo-module **/` + `import` ES6, `patch()` dari `@web/core/utils/patch`, tidak ada `odoo.define`, tidak ada `Component.extend()` | JS module system lama (dilarang di 17+) | **N/A — sudah compliant** | — | Verifikasi statis langsung — modul ini ditulis dengan pola modern sejak awal (17.0), tidak ada legacy pattern yang perlu di-rewrite |
| DIFF-10 | `static/src/js/{chatter,message}.js` — `t-on-click="..."` (pinnedMessages.xml), tidak ditemukan `t-att-on-click` | `t-att-on-click`→`t-on-click` | **N/A — sudah compliant** | — | Verifikasi statis langsung |
| DIFF-11 | `static/src/css/style.css` — selector class biasa, tidak ada SCSS (`/` divisi, `@import`), tidak ada inline script/CDN | CSP/SCSS stricter enforcement (§2 knowledge base, lower confidence) | **N/A — tidak berlaku** | — | Verifikasi statis langsung — file CSS ini murni selector + `rgba()`, tidak ada fitur SCSS yang disebut berisiko |
| DIFF-12 | `models/mail_message.py` — `toggle_pin()` di-loop per record, tidak ada `create()`/`onchange`/`_name_search`/`_check_recursion`/`search()` override | Berbagai API ORM yang berubah §1 (create multi, `_search_display_name`, `_has_cycle`, `search_fetch`) | **N/A — tidak berlaku** | — | Verifikasi statis langsung — sisi Python modul ini sangat minimal (1 field + 1 method sederhana), tidak menyentuh API manapun yang disebut berubah |

---

## 2. Kompatibilitas Dependency (OCA/Third-Party)

Tidak ada dependency OCA/third-party (dikonfirmasi Step 1, semua dependency Native Community `web`/`base`/`mail`). Tabel ini **N/A**.

---

## 3. Temuan Baru — Tulis ke Migration Records

- [x] **Kandidat entry baru untuk `migration-tool/knowledge/`** (kategori `dependency-compat/mail`) — belum ada entry `mail`/`discuss` module manapun di knowledge base saat ini, project ini yang pertama. **Setelah Step 6 (install + browser testing nyata) modul ini selesai, hasil verifikasi DIFF-01..DIFF-06 di atas (terverifikasi/terbantah) WAJIB dicatat ke `migration-tool/migration-records/pos-margin-sale_17.0_18.0/SUMMARY.md`** kategori `dependency-compat` — ini akan jadi referensi berharga untuk project migrasi Odoo manapun di masa depan yang menyentuh `mail`/`discuss`/chatter (area yang sering dipakai banyak modul custom).
- [ ] Belum ditulis ke `SUMMARY.md` saat ini — menunggu hasil verifikasi nyata Step 6, bukan spekulasi dari analisis statis ini (`migration-records` isinya temuan terverifikasi, bukan dugaan).

---

## 4. Ringkasan Risiko

| Item | Level risiko | Catatan |
|---|---|---|
| DIFF-01/02/03 (xpath ke class QWeb `mail.Chatter`/`mail.Message`/`mail.MessageCardList`) | **Tinggi** | Tidak terverifikasi, dampak kalau salah: fitur pin tidak muncul di UI sama sekali. Prioritas #1 dicek di Step 6 G1 (install) — kalau xpath tidak match, Odoo raise error saat load QWeb, akan ketahuan SEGERA (bukan silent) |
| DIFF-04/05 (import path JS `@mail/core/...`) | **Tinggi** | Tidak terverifikasi, dampak kalau salah: bundle JS gagal load total. Terdeteksi di Step 6 G1 lewat console browser/log server saat load asset |
| DIFF-06 (`this.messagePinService` implicit access) | **Tinggi** | Preseden serupa (`useService("rpc")` dihapus) memperkuat kecurigaan. Terdeteksi HANYA lewat eksekusi browser nyata (klik pin di pesan Discuss channel) — **review statis TIDAK akan menangkap ini** (sintaks tetap valid), harus checkpoint G2 (browser), bukan cuma G1 (install) |
| DIFF-07 (`useService("orm")`) | Rendah | Service inti stabil, risiko rendah |
| DIFF-08..DIFF-12 | N/A | Dikonfirmasi tidak berlaku dari verifikasi statis |
| **Modul ini secara keseluruhan** | **Tinggi** (dikonfirmasi ulang dari Step 1) | Rekomendasi kuat: modul ini dikerjakan Step 6 dengan checkpoint G1 **dan** G2 penuh (bukan cuma G1) — beberapa risiko di atas (DIFF-06 khususnya) tidak akan ketahuan dari install sukses saja |
