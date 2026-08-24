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
| E | ✅ **Port apa adanya, terverifikasi G1 tidak error saat load module** — TAPI risiko tertinggi (`DIFF-04/05/06`, `this.messagePinService`) BELUM terverifikasi penuh, itu ranah G2 | 2026-08-24 |
| F | ✅ **Port apa adanya, xpath `t-inherit` TIDAK terverifikasi oleh G1** (lihat catatan di bawah — QWeb JS template beda mekanisme validasi dari `ir.ui.view`) | 2026-08-24 |
| G2 (validasi akhir/runtime) | ⏳ **BELUM dijalankan — prioritas tertinggi project ini**, lihat `05b_TEST_PLAN_MIGRATION.md` (3 tour test wajib ditulis) | — |

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
- **TIDAK terverifikasi oleh percobaan ini** (lihat catatan batasan di atas): DIFF-01 (xpath `t-inherit="mail.Chatter"`), DIFF-02 (xpath `t-inherit="mail.Message"`), DIFF-03 (xpath `t-inherit="mail.MessageCardList"`), DIFF-04/05 (import `@mail/core/*`), DIFF-06 (`this.messagePinService`). Semua masih `[TIDAK TERVERIFIKASI]` sampai G2 dijalankan.

## [Fase B1] Model Risiko Rendah

- **Scope:** `models/mail_message.py`
- **Status:** ✅ Selesai (tidak ada perubahan diperlukan)

## [Fase E] JavaScript (Owl) — REVISI setelah G2 nyata (lihat di bawah)

- **Scope:** `static/src/js/{chatter,message,pinMessage}.js`
- **Item spec (ref):** `03_MIGRATION_SPEC.md` §2b "OWL Widget yang Butuh Rewrite/Review"
- **Aksi AWAL:** Port seluruh isi apa adanya. Dicek ulang: sudah `/** @odoo-module **/` + `import` ES6 + `patch()`, tidak ada `odoo.define`/`Component.extend()`.
- **Aksi KOREKSI (setelah G2 nyata, lihat entri "G2" di bawah):** `static/src/js/chatter.js` baris 4 — import `Chatter` diubah dari `@mail/core/web/chatter` (path 17.0, SUDAH TIDAK ADA di 18.0) → `@mail/chatter/web_portal/chatter` (path baru 18.0, dikonfirmasi baca source langsung di container `odoo:18.0`). Ini **wajib untuk kompatibilitas** (path lama benar-benar tidak eksis, bukan cuma dugaan) — bukan refactor gaya.
- **Secara eksplisit TIDAK dilakukan:** TIDAK mengubah `this.messagePinService` (message.js) — dicek G2, TIDAK ada error terkait ini muncul (lihat entri G2), jadi TIDAK diubah sama sekali (tetap apa adanya, `[BSL-002]`/`MF-09` tetap berlaku sebagai catatan risiko, tapi TIDAK bermanifestasi jadi error nyata di sesi verifikasi ini).
- **Risiko:** Diturunkan dari HIGH ke MEDIUM untuk import path (sudah diperbaiki+terverifikasi), TETAP MEDIUM untuk `messagePinService` (belum dites interaktif klik pin di pesan Discuss channel sungguhan — G2 sesi ini cuma sampai tahap "modul termuat tanpa error", belum sampai klik tombol nyata, lihat batasan di entri G2)
- **Status:** ✅ Selesai (1 fix wajib) + ⚠️ `messagePinService` masih perlu klik-test manual dev sebelum Step 8/9 final

## [Fase F] Upgrade Template — REVISI setelah G2 nyata

- **Scope:** `static/src/xml/{pinnedMessages,message_card_list}.xml`
- **Aksi AWAL:** Port seluruh isi apa adanya.
- **Aksi KOREKSI (setelah G2 nyata):** `static/src/xml/message_card_list.xml` — xpath matcher `//button[contains(@class, 'o-mail-MessageCard-jump')]` diubah jadi `//a[contains(@class, 'o-mail-MessageCard-jump')]`. **Alasan:** dikonfirmasi baca source `mail/static/src/core/common/message_card_list.xml` di container `odoo:18.0` — elemen core berubah dari `<button>` (17.0) jadi `<a role="button">` (18.0), xpath tag-selector lama tidak akan pernah match tag baru. Konten replacement (isi `<button>` custom di dalamnya) TIDAK diubah — cuma tag SELECTOR di xpath expression yang diperbaiki.
- **Dicek juga (TIDAK diubah, terkonfirmasi masih valid):** `pinnedMessages.xml` — kelas `o-mail-Chatter-topbar` (chatter/web/chatter.xml) dan `o-mail-Message-author` (core/common/message.xml) dikonfirmasi MASIH ADA persis sama di 18.0 (grep langsung source container) — xpath `t-inherit="mail.Chatter"`/`t-inherit="mail.Message"` di file ini TIDAK perlu diubah.
- **Risiko:** Diturunkan ke LOW-MEDIUM — kedua target xpath dikonfirmasi match (satu sudah benar dari awal, satu sudah diperbaiki).
- **Status:** ✅ Selesai, terverifikasi G2 (browser nyata, console bersih dari error terkait modul ini setelah fix)

## G2 — Browser Verification Nyata (2026-08-24)

> **Dijalankan sungguhan** lewat Claude Browser tool (Docker `odoo:18.0` mode G2, login admin,
> buka `/odoo`) — bukan simulasi/dugaan. Metodologi: baca console error browser, cross-reference ke
> source Odoo 18.0 SUNGGUHAN di dalam container (`docker exec ... grep/find`), bukan tebakan.

**Iterasi 1 (sebelum fix):** Console menunjukkan persis:
```
The following modules are needed by other modules but have not been defined... {0: @mail/core/web/chatter}
The following modules could not be loaded because they have unmet dependencies... {0: @pin_message/js/chatter}
```
Dikonfirmasi via `docker exec ... find .../mail/static/src -iname "*chatter*"` — path `core/web/chatter.js` SUDAH TIDAK ADA, file pindah ke `chatter/web_portal/chatter.js`. **Ini konfirmasi nyata `DIFF-04` (bukan lagi `[TIDAK TERVERIFIKASI]`).**

**Iterasi 2 (setelah fix chatter.js path):** Error `@mail/core/web/chatter`/`@pin_message/js/chatter` **hilang total** (dikonfirmasi tab browser baru, tanpa cache modul lama). Sisa error konsol: `"An unknown error occurred when fetching the script"` + `"Service worker registration failed"` — dikonfirmasi lewat cross-check TIDAK terkait modul manapun di project ini (error yang sama juga muncul di sesi awal SEBELUM pin_message bahkan diinstall, terkait `/bus/websocket_worker_bundle`, fitur inti Odoo websocket worker) — **kemungkinan besar limitasi environment tool browser tersandbox ini** (Service Worker registration sering gagal di browser context yang di-proxy), bukan bug kode project.

**Batasan sesi verifikasi ini (WAJIB dibaca sebelum Step 8/9):** karena keterbatasan di atas, webclient tidak pernah selesai mounting penuh (`document.body` tetap 0 children) — **interaksi klik nyata (toggle pin, buka Discuss, dst.) BELUM bisa dilakukan lewat tool ini.** Yang terverifikasi: (1) tidak ada JS module/import error tersisa dari kode project, (2) kedua xpath (`o-mail-Chatter-topbar`, `o-mail-Message-author`) dikonfirmasi valid dari BACA SOURCE LANGSUNG (bukan cuma "tidak error"). **Verifikasi interaktif (AC-01 s.d. AC-05 penuh, `05b_TEST_PLAN_MIGRATION.md`) tetap wajib dilakukan dev di browser desktop biasa sebelum Step 8 code review dianggap final** — terutama AC-03 (`messagePinService`, risiko tertinggi yang masih tersisa).

---

## Temuan di Luar Spec

- [x] Tidak ada

## Kontribusi ke Knowledge Base

- [ ] Ditunda — kandidat `dependency-compat/mail/17-to-18.md` (semua DIFF-01..06) baru bisa ditulis SETELAH G2 nyata membuktikan/membantah risiko-risiko ini. Menulis sekarang (dari G1 saja) akan salah — G1 tidak menyentuh area yang paling berisiko di modul ini.
