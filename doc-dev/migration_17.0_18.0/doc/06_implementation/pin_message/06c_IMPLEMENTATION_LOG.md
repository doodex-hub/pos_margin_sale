# Implementation Log — pin_message

**Step:** 6 — Code Migration
**Ref:** `03_spec/pin_message/03_MIGRATION_SPEC.md`, `migration-tool/templates/06a_CODE_MIGRATION_PHASES.md`
**Tanggal:** 2026-08-24

---

## Applicability Check

| Fase | Relevan? | Bukti/alasan (dari `01a` §2b) |
|---|---|---|
| C1 | ☐ Tidak | Tidak ada `ir.ui.view`/`views/` sama sekali (`data: []` manifest) — semua UI lewat template Owl QWeb JS |
| B2 | ☐ Tidak | Tidak ada field JSON/relasi berantai |
| C2 | ☐ Tidak | Tidak ada `ir.ui.view` dengan `invisible=`/`attrs=` (kondisi visibility di modul ini ada, tapi di template Owl `t-if`, bukan `ir.ui.view` — beda kategori dari C2 yang spesifik `attrs=`/`domain=`/`context=` view backend) |
| D1 | ☐ Tidak | Tidak ada controller sama sekali (bahkan tidak ada scaffold dead) |
| D2 | ☑ Ya | `assets.web.assets_backend` — CSS + 3 file JS + 2 file XML QWeb, semuanya nyata |
| E | ☑ Ya | `static/src/js/{chatter,message,pinMessage}.js` — patch prototype + registry |
| F | ☑ Ya | `static/src/xml/{pinnedMessages,message_card_list}.xml` — `t-inherit` template |

---

## Tabel Ringkas Status Fase

| Fase | Status | Tanggal |
|---|---|---|
| A1 | ✅ | 2026-08-24 |
| A2 | ✅ (N/A — tidak ada `<tree>`, tidak ada `ir.ui.view` sama sekali) | 2026-08-24 |
| G1 (setelah A2/A3) | ✅ Pass (install sukses, exit code 0) | 2026-08-24 |
| A3 | N/A — tidak ada `security/` folder, modul cuma extend `mail.message` yang sudah py ACL dari core `mail` (dikonfirmasi Step 1) | 2026-08-24 |
| A4 | ✅ (struktur konsisten) | 2026-08-24 |
| A5 | ✅ (tidak ada API ORM yang berubah — `toggle_pin()` sederhana) | 2026-08-24 |
| B1 | ✅ (model sederhana) | 2026-08-24 |
| B2 | N/A | — |
| C1 | N/A | — |
| C2 | N/A | — |
| D1 | N/A | — |
| D2 | ✅ (asset key valid, semua file eksis — dikonfirmasi Step 1, beda dari `sale_margin_threshold` yang folder-nya kosong) | 2026-08-24 |
| E | ✅ **SELESAI PENUH, TERVERIFIKASI TOUR TEST NYATA** — 2 fix wajib ditemukan+diperbaiki (`MF-12`, `MF-22`), lihat entri Fase E | 2026-08-24 |
| F | ✅ **SELESAI PENUH, TERVERIFIKASI TOUR TEST NYATA** — 1 fix wajib (`MF-14`) + 1 fix Python terkait (`MF-23`), lihat entri Fase F | 2026-08-24 |
| G2 (validasi akhir/runtime) | ✅ **Tour test pin/unpin log note PASS** ("tour succeeded", lihat entri Tour Test) — ⚠️ **jalur pin pesan Discuss channel (`messagePinService`, risiko tertinggi `MF-09`) BELUM ada Tour test terpisah**, masih perlu dev/Step 9 | 2026-08-24 |

## Riwayat Percobaan G1 (Install Test)

| # | Dijalankan setelah fase | Mode | Hasil | Error (kalau fail) | Tanggal |
|---|---|---|---|---|---|
| 1 | A1+A2 (ketiga modul, satu instance) | C | ✅ **Pass** — exit code 0, `pin_message` loaded di posisi 29/67 (modul PERTAMA dari ketiganya yang di-load, karena dependency-nya paling ringan) | Tidak ada error/traceback dari modul ini. 1 warning non-fatal (label collision `is_pinned`/`pinned_at`) — **dikonfirmasi SUDAH ADA JUGA di log 17.0 lama** (`docker-env/logs/odoo.log` baris 17-18, tanggal 2026-07-31), bukan regresi baru. | 2026-08-24 |

> **Batasan penting hasil G1 ini, WAJIB dibaca sebelum menganggap Fase E/F "aman":** `-i ... --stop-after-init`
> menjalankan install SERVER-SIDE (Python, `ir.model`, security) — TIDAK meng-compile/memvalidasi
> asset bundle frontend (`web.assets_backend`) yang berisi seluruh JS + `t-inherit` QWeb template
> modul ini. Odoo baru compile bundle itu saat ada request browser yang memintanya (buka backend
> UI apapun). **Install sukses TIDAK membuktikan `DIFF-01..06` (xpath match, import resolve,
> `messagePinService` akses) beneran valid** — cuma membuktikan tidak ada error Python-level saat
> registrasi asset key di manifest. G2 (buka browser, buka chatter, coba pin pesan) tetap **mutlak
> wajib**, bukan opsional/formalitas, untuk modul ini secara khusus.

---

## Entri

## [Fase A1] Manifest Bootstrap

- **Scope:** `__manifest__.py`
- **Aksi:** `version: '17.0.1.0'` → `'18.0.1.0'`
- **Risiko:** LOW
- **Status:** ✅ Selesai

## [Fase A2] XML Tree → List

N/A — dikonfirmasi Applicability Check, tidak ada `<tree>`/`ir.ui.view` sama sekali di modul ini.

## [Fase A3] Security Hardening

N/A — dikonfirmasi Step 1 (`01a_MIGRATION_INTAKE.md` "Ringkasan" poin 5): modul ini cuma extend `mail.message` (field + method), tidak butuh ACL baru — access control mail.message sudah ditangani core `mail`.

## [Fase A4] Skeleton & Folder Integrity

- **Status:** ✅ Selesai (tidak ada perubahan diperlukan)

## [Fase A5] Python API Compatibility

- **Scope:** `models/mail_message.py`
- **Aksi:** Dicek — `toggle_pin()` tidak pakai API yang diketahui berubah (bukan `create()`, bukan `_name_search`, dll).
- **Status:** ✅ Selesai (tidak ada perubahan diperlukan)

## G1 — Install Test #1 (setelah A1+A2, ketiga modul sekaligus)

- **Command:** `docker compose -f docker-env/docker-compose.yml up` (image `odoo:18.0`)
- **Mode:** C
- **Hasil:** exit code 0, `pin_message` loaded bersih di posisi 29/67, tidak ada error Python/manifest.
- **TIDAK terverifikasi oleh percobaan ini** (konfirmasi kemudian: BENAR sinyal ini penting — `MF-22` baru ketahuan dari Tour test, bukan dari G1 manapun): DIFF-01..06 semua masih `[TIDAK TERVERIFIKASI]` di titik ini.

## [Fase B1] Model Risiko Rendah

- **Scope:** `models/mail_message.py`
- **Status:** ✅ Selesai (tidak ada perubahan diperlukan)

## [Fase E] JavaScript (Owl) — 2 fix wajib, ditemukan+diperbaiki+diverifikasi Tour test nyata

### E.1 — `MF-12`: `chatter.js` import path `@mail/core/web/chatter` sudah tidak ada
- **Temuan:** Console browser: `modules needed but not defined ... @mail/core/web/chatter`. Dikonfirmasi `docker exec ... find` — file pindah ke `@mail/chatter/web_portal/chatter`.
- **Aksi:** import diperbaiki ke path baru.

### E.2 — `MF-22`: `chatter.js` `load()` full-override memanggil service yang sudah tidak ada
- **Temuan (baru ketahuan SETELAH E.1 diperbaiki, lewat Tour test nyata — bukan G1/console statis):** `TypeError: Cannot read properties of undefined (reading 'fetchData')` tepat setelah klik "Log note". Modul ini FULL-OVERRIDE `Chatter.prototype.load(thread, requestList)` untuk menyisipkan `messageFields: ['is_pinned']` via `this.threadService.fetchData(thread, requestList, options)`. Di 18.0: `this.threadService` tidak ada lagi (dikonfirmasi baca `chatter.js`/`thread_model_patch.js` container) — `fetchData` sekarang milik `thread` itu sendiri (`thread.fetchData(requestList)`, SATU argumen saja, tidak ada lagi customisasi field via parameter).
- **Aksi:** Method `load()` **DIHAPUS TOTAL** dari patch (bukan diperbaiki — modul ini tidak perlu override `load()` sama sekali lagi). `initialLoad()` tetap memanggil `this.load(...)` tapi ini sekarang jatuh ke `super.load()` (core) yang benar. Field custom `is_pinned` dipindah ke mekanisme baru — lihat `MF-23` di Fase A5 (Python).
- **Secara eksplisit TIDAK dilakukan:** tidak mengubah `this.messagePinService` (message.js, `MF-09`) — tidak pernah bermanifestasi jadi error di Tour test ini (Tour ini menguji jalur log note, bukan jalur Discuss channel yang memakai `messagePinService`).
- **Status:** ✅ Selesai, **terverifikasi Tour test nyata** — lihat entri Tour Test di bawah.

## [Fase A5, revisi] `MF-23`: field custom butuh `mail.message._to_store()`, bukan lagi field-list JS
- **Scope:** `models/mail_message.py`
- **Temuan:** Setelah `MF-22` diperbaiki (hapus `load()` override), `is_pinned` TIDAK PERNAH sampai ke data message di frontend (section Pinned Messages selalu kosong, badge 0) — karena mekanisme lama (field-list custom di `Chatter.load()`) yang biasa membawa field ini sudah dihapus, dan tidak ada penggantinya. Dikonfirmasi baca `mail_message.py` core — field custom ke frontend sekarang HARUS lewat override `_to_store(self, store, /, **kwargs)` per-model (pola sama seperti POS `_load_pos_data_fields`, `MF-18`).
- **Aksi:** `models/mail_message.py` — tambah method baru: `super()._to_store(store, **kwargs)` lalu `for message in self: store.add(message, {'is_pinned': message.is_pinned})`.
- **Status:** ✅ Selesai, **terverifikasi Tour test nyata** — badge muncul benar dengan angka 1 setelah pin.

## [Fase F] Upgrade Template — 1 fix wajib, ditemukan+diperbaiki+diverifikasi Tour test nyata

### F.1 — `MF-14`: `message_card_list.xml` xpath tag selector `button`→`a`
- **Temuan:** Core `mail.MessageCardList` mengubah elemen "Jump" dari `<button>` (17.0) jadi `<a role="button">` (18.0) — xpath tag-selector lama (`//button[...]`) tidak match.
- **Aksi:** xpath diubah ke `//a[contains(@class, 'o-mail-MessageCard-jump')]`.
- **Dicek juga (TIDAK diubah, terkonfirmasi masih valid):** `pinnedMessages.xml` — kelas `o-mail-Chatter-topbar`/`o-mail-Message-author` dikonfirmasi MASIH ADA persis sama di 18.0.
- **Status:** ✅ Selesai, **terverifikasi Tour test nyata** — section Pinned Messages expand dengan benar, menampilkan message card.

## [Fase E/F — Tour Test] Verifikasi interaktif nyata (Mode D)

- **File:** `static/tests/tours/pin_message_tour.js` (tour `pin_message_toggle_pin_tour`) + `tests/test_pin_message_tour.py` (companion `HttpCase`, target `res.partner`).
- **Manifest:** ditambah key `web.assets_tests: ['pin_message/static/tests/tours/**/*']`.
- **Alur yang benar-benar dieksekusi Chrome asli:** buka form `res.partner` → klik "Log note" → tulis catatan → submit → catatan muncul di chatter → klik tombol pin inline (icon thumbtack, dari `pinnedMessages.xml`) → **badge "Pinned Messages" muncul dengan angka 1** → klik header untuk expand → **message card muncul di dalam section** → klik tombol pin lagi (unpin) → **section Pinned Messages hilang total** (tidak ada lagi pesan pinned).
- **3 iterasi debugging nyata (dicatat supaya tidak terulang):**
  1. `TypeError: Cannot read properties of undefined (reading 'fetchData')` → `MF-22` (di atas).
  2. Klik tombol aksi pesan (`.o-mail-Message-actions button[name='pins']`) tidak pernah ketemu/timeout → **beralih ke tombol inline** (`pinnedMessages.xml`'s thumbtack button, next to author name) yang TIDAK butuh hover — lebih robust untuk Tour test.
  3. Klik `.o-mail-PinnedMessages` (container besar) untuk expand kadang tidak konsisten toggle-nya → **diperbaiki jadi klik `.o-mail-PinnedMessages .cursor-pointer`** (header spesifik yang punya `t-on-click`, bukan container luar) — lebih presisi, hasilnya stabil.
- **Hasil akhir:** `tour succeeded`, dikonfirmasi di database bersih (`docker compose down -v` sebelum run terakhir) — **0 failed, 1 error(s) of 19 tests** (1 error itu `MF-21`, `sale_margin_threshold`, tidak terkait modul ini).
- **BELUM ada Tour test untuk jalur Discuss channel** (`messagePinService`, `MF-09`, risiko tertinggi project ini) — kandidat lanjutan Step 9, bukan blocker Step 8 (jalur log note yang paling umum dipakai sudah terverifikasi penuh).

---

## Temuan di Luar Spec

- [x] Tidak ada temuan struktur baru di luar `MF-22`/`MF-23` (sudah dicatat resmi di `FINDINGS.md`).

## Kontribusi ke Knowledge Base

- [x] Ada, sudah ditulis — `migration-tool/migration-records/pos-margin-sale_17.0_18.0/SUMMARY.md`, mencakup: chatter/message data-loading mechanism 17.0→18.0 (`Chatter.load()` field-list → `_to_store()` per-model), xpath `button`→`a` di `MessageCardList`, dan chatter import path relocation (`MF-12`).
