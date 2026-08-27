# Implementation Log — pin_message

**Step:** 6 — Code Migration
**Ref:** `03_spec/pin_message/03_MIGRATION_SPEC.md`, `migration-tool/templates/06a_CODE_MIGRATION_PHASES.md`
**Tanggal:** 2026-08-26

---

## Applicability Check

Sumber: `01a_MIGRATION_INTAKE.md` §2b.

| Fase | Relevan? | Bukti/alasan (dari `01a` §2b) |
|---|---|---|
| B2 (Model Kompleks) | ☐ Tidak | Hanya satu field `Boolean` (`is_pinned`) di `mail.message`, tidak ada JSON/relasi berantai/dynamic model creation |
| C2 (Semantik XML & UX) | ☐ Tidak | Modul ini tidak punya `ir.ui.view`/`views/*.xml` sama sekali (`data: []` di manifest) |
| D1 (Controllers) | ☐ Tidak | Tidak ada folder `controllers/` |
| D2 (Assets & CSS Stabilization) | ☐ Tidak | Path asset (`static/src/{css,js,xml}/*`) tidak berubah sama sekali, `style.css` tidak disentuh |
| E (JavaScript/Owl) | ☑ **Ya** | `static/src/js/{chatter,message,pinMessage}.js` — patch Owl components, area kerja utama (`DIFF-02`) |
| F (Upgrade Template) | ☐ Tidak | Step 2 mengonfirmasi kedua template QWeb (`pinnedMessages.xml`, `message_card_list.xml`) TIDAK butuh perubahan syntax — xpath anchor tetap stabil di 19.0 |

---

## Tabel Ringkas Status Fase

| Fase | Status | Tanggal |
|---|---|---|
| A1 | ✅ | 2026-08-26 |
| A2 | N/A — tidak ada `ir.ui.view`/XML view sama sekali | 2026-08-26 |
| G1 (checkpoint Fase A) | ✅ **Pass** (2026-08-27) | 2026-08-27 |
| A3 | N/A — tidak ada wizard/TransientModel di modul ini | 2026-08-26 |
| A4 | ✅ — struktur folder tidak berubah, tidak ada yang perlu dinormalisasi | 2026-08-26 |
| A5 | ✅ — **1 fix KRITIS ditemukan lewat G2/Tour test** (`_to_store` infinite recursion), lihat entri | 2026-08-27 |
| B1 | ✅ — `is_pinned`/`toggle_pin()` diverifikasi tidak butuh perubahan | 2026-08-26 |
| B2 | N/A — dikonfirmasi Applicability Check | — |
| C1 | N/A — tidak ada view sama sekali | 2026-08-26 |
| C2 | N/A — dikonfirmasi Applicability Check | — |
| D1 | N/A — dikonfirmasi Applicability Check | — |
| D2 | N/A — dikonfirmasi Applicability Check | — |
| E | ✅ | 2026-08-26 |
| F | N/A — dikonfirmasi Applicability Check | — |
| G2 (validasi akhir/runtime) | ✅ **Pass (0 failed, 0 error dari 9 test, termasuk 2 Tour test browser asli)** | 2026-08-27 |

## Riwayat Percobaan G1 (Install Test) + G2 (Tour test, Mode D)

Mode C (AI jalankan langsung, `docker compose up`), image `odoo:19.0` (sudah ada lokal).

| # | Dijalankan setelah fase | Mode | Hasil | Error (kalau fail) | Tanggal |
|---|---|---|---|---|---|
| 1 | A5 (install polos) | C | ✅ Pass | — (bersama `pos_margin_threshold`/`sale_margin_threshold`, lihat log project itu untuk 2 fix `sale_margin_threshold` yang tidak terkait modul ini) | 2026-08-27 |
| 2 | E (`--test-enable`, Tour test) | C | ❌ **Fail 1, Error 1** | `test_pin_message_action_menu_pin_visible_tour`: "The ready `odoo.isTourReady(...)` code was always falsy". Root cause SEBENARNYA baru ketahuan dari traceback HTTP terpisah di log yang sama: **infinite recursion** — `models/mail_message.py`'s `_to_store()` override memanggil `store.add(message, {'is_pinned': ...})`, dan di 19.0 `Store.add()` TIDAK PUNYA jalur pintas untuk dict-of-values (beda dari 18.0) — setiap panggilan `store.add(record, ...)` SELALU re-entry ke `_to_store()`, jadi baris ini rekursi diri sendiri tanpa akhir sampai `RecursionError`, mematahkan loading HALAMAN APAPUN yang membuka chatter (bukan cuma fitur pin) — persis skenario blast-radius yang sudah diperingatkan di `MF-14`/`02_DIFF_ANALYSIS.md`, cuma fix pertama (Step 6 awal, cuma menambah parameter `fields`) BELUM cukup. | 2026-08-27 |
| 3 | A5 (setelah fix #2) | C | ✅ **Pass** | — 0 failed, 0 error dari 9 test `pin_message` (naik dari gagal total, waktu eksekusi turun dari 122s ke 4.22s — bukti recursion loop sebelumnya benar-benar makan waktu, bukan cuma error kosmetik) | 2026-08-27 |

---

## Entri

## [Fase A1] Manifest Bootstrap

- **Scope:** `pin_message/__manifest__.py`
- **Item spec (ref):** `03_MIGRATION_SPEC.md` §2 baris `__manifest__.py`
- **Aksi:**
  - `__manifest__.py`: `version` `'18.0.1.0'` → `'19.0.1.0'`.
- **Secara eksplisit TIDAK dilakukan:** tidak ada perubahan `depends`/`data`/`assets` lain — semuanya
  tetap identik.
- **Risiko:** LOW
- **Status:** ✅ Selesai

## [Fase A2] XML Tree → List

N/A — dikonfirmasi Applicability Check (tidak ada `ir.ui.view`/`views/*.xml` sama sekali di modul
ini, `data: []`).

## [Fase A3] Security Hardening

N/A — dikonfirmasi Applicability Check (tidak ada wizard/`TransientModel`; `mail.message` sudah
punya ACL native yang tidak disentuh modul ini).

## [Fase A4] Skeleton & Folder Integrity

- **Scope:** struktur folder modul secara keseluruhan.
- **Aksi:** diverifikasi — struktur (`models/`, `static/src/{css,js,xml}/`, `static/tests/`,
  `tests/`) konsisten, semua `__init__.py` sudah benar, tidak ada folder yang hilang.
- **Secara eksplisit TIDAK dilakukan:** tidak ada perubahan struktur.
- **Risiko:** LOW
- **Status:** ✅ Selesai

## [Fase A5] Python API Compatibility

- **Scope:** `models/mail_message.py`
- **Item spec (ref):** `03_MIGRATION_SPEC.md` §2 baris `_to_store`, §2b Critical Blocker #2, ref
  `FINDINGS.md` `MF-14`, `02_DIFF_ANALYSIS.md` `DIFF-01`.
- **Aksi:**
  - `models/mail_message.py`: signature `_to_store(self, store, /, **kwargs)` diubah jadi
    `_to_store(self, store, fields, /, **kwargs)` — tambah parameter positional `fields` sesuai
    signature 19.0 core, diteruskan apa adanya ke `super()._to_store(store, fields, **kwargs)`.
  - **Fix KEDUA, ditemukan lewat G2/Tour test (2026-08-27), TIDAK ketahuan Step 2/3 maupun review
    manual pertama:** baris `for message in self: store.add(message, {'is_pinned':
    message.is_pinned})` diganti `store.add_records_fields(self, ['is_pinned'])`. Root cause:
    `Store.add()` 18.0 punya jalur pintas kalau argumen kedua adalah dict nilai konkret (langsung ke
    `add_model_values`, TIDAK re-entry `_to_store()`); `Store.add()` 19.0 TIDAK punya jalur pintas
    itu — argumen kedua SELALU diperlakukan sebagai daftar field untuk di-fetch lewat `_to_store()`,
    jadi `store.add(message, {...})` dari DALAM `_to_store()` sendiri selalu re-entry ke
    `_to_store()` lagi → infinite recursion (`RecursionError`) begitu modul ini terinstall dan
    chatter APAPUN dibuka. `add_records_fields()` adalah API 19.0 yang didesain eksplisit untuk
    kasus ini (dipakai core sendiri di `mail_message.py`/`discuss_channel.py`) — tidak re-entry
    `_to_store()`.
- **Secara eksplisit TIDAK dilakukan:** tidak ada perubahan pada `toggle_pin()`, `is_pinned` field,
  atau NILAI yang dikirim ke frontend — behavior akhir (field `is_pinned` sampai ke client) identik,
  hanya MEKANISME pengirimannya yang diperbaiki dua kali.
- **Risiko:** Fix pertama LOW tapi TIDAK CUKUP (baru ketahuan dari eksekusi nyata, bukan baca kode) —
  ini bukti langsung kenapa G1 install-test SENDIRIAN tidak cukup untuk area `_to_store`/chatter,
  harus sampai G2/Tour test yang benar-benar membuka halaman dengan chatter.
- **Status:** ✅ Selesai — **divalidasi G2, PASS** (0 failed/0 error, 9 test `pin_message`, termasuk
  2 Tour test browser asli)

## [Fase B1] Model Risiko Rendah

- **Scope:** `models/mail_message.py` (`is_pinned`, `toggle_pin()`)
- **Aksi:** diverifikasi ulang (bukan diubah) — `toggle_pin()` sudah aman multi-record (`for message
  in self:`), tidak ada dependency compute yang perlu dilengkapi, tidak ada perubahan API ORM yang
  mempengaruhi kedua elemen ini (dikonfirmasi Step 2).
- **Secara eksplisit TIDAK dilakukan:** tidak ada perubahan kode.
- **Risiko:** LOW
- **Status:** ✅ Selesai

## [Fase B2] Model Kompleks

N/A — dikonfirmasi Applicability Check.

## [Fase C1] View Sederhana

N/A — tidak ada `ir.ui.view` sama sekali di modul ini.

## [Fase C2] Semantik XML & Konsistensi UX

N/A — dikonfirmasi Applicability Check.

## [Fase D1] Controllers

N/A — dikonfirmasi Applicability Check.

## [Fase D2] Assets & CSS Stabilization

N/A — dikonfirmasi Applicability Check.

## [Fase E] JavaScript (Owl versi baru)

- **Scope:** `static/src/js/pinMessage.js`
- **Item spec (ref):** `03_MIGRATION_SPEC.md` §2 baris `pinMessage.js`, §2b Critical Blocker #3, ref
  `FINDINGS.md` `MF-15`, `02_DIFF_ANALYSIS.md` `DIFF-02`.
- **Aksi:**
  - `pinMessage.js`: entry `messageActionsRegistry.add("pins", {...})` di-rewrite mengikuti pola
    native 19.0 (`mail/static/src/discuss/message_pin/common/message_actions.js`, dikonfirmasi
    langsung dari source):
    - `condition: (component) => {...}` → `condition: ({ message, thread }) => {...}` — semua akses
      `component.message.*` diganti `message.*`, `component.props.thread` diganti `thread` langsung
      (parameter kedua destructure).
    - `title: _t("Pin")` → `name: _t("Pin")` — rename key sesuai shape 19.0, NILAI tidak berubah.
    - `onClick: (component) => component.onClickPin()` → `onSelected: ({ owner }) =>
      owner.onClickPin()` — rename key, dan `owner` (bukan `component`) yang membawa referensi
      instance component `Message` asli (dikonfirmasi dari `Action.get params()` 19.0: `owner` =
      component yang mendaftarkan action lewat `useMessageActions()`) — pemanggilan
      `onClickPin()` di component TETAP SAMA, cuma cara mengaksesnya yang berubah.
    - `console.log(component.message.type)` dipertahankan APA ADANYA (bukan dihapus — `MF-10` masih
      status "belum ada keputusan eksplisit dari user"), hanya diadaptasi jadi
      `console.log(message.type)` mengikuti destructure baru.
    - Logic `isNote`/`isNotChangeLog` TIDAK diubah sama sekali — hanya sumber variabel
      (`component.message.X` → `message.X`).
- **Secara eksplisit TIDAK dilakukan:**
  - `chatter.js` dan `message.js` TIDAK disentuh — dikonfirmasi Step 2 tidak butuh perubahan
    (`DIFF-03`, `DIFF-04`, `DIFF-05`).
  - `MF-10` (`console.log` leftover) TIDAK dihapus — bukan bagian dari 3 perbaikan wajib yang
    disepakati, masih menunggu keputusan eksplisit user terpisah.
  - `icon: "fa-thumb-tack"` TIDAK diubah jadi `"fa fa-thumb-tack"` walau native 19.0 & 18.0
    konsisten pakai prefix `fa `. Ini quirk kosmetik yang SUDAH ADA sejak sebelum migrasi 19.0
    (bukan sesuatu yang 19.0 rusak), di luar scope 3 perbaikan wajib yang disepakati — dicatat di
    sini supaya tidak dianggap terlewat, bukan diperbaiki diam-diam.
- **Risiko:** MEDIUM (perubahan JS di area yang sebelumnya sudah pernah crash — `MF-24` di project
  17→18 — historically fragile).
- **Status:** ✅ Selesai — **divalidasi Tour test `pin_message_action_menu_pin_visible_tour`, PASS**
  (setelah fix `_to_store` di Fase A5 di atas juga diperbaiki — kegagalan pertama tour ini disebabkan
  crash `_to_store`, bukan bug di `pinMessage.js` sendiri; setelah kedua fix, `condition`/`onSelected`
  rewrite di file ini terbukti benar tanpa perubahan lanjutan).

## [Fase F] Upgrade Template

N/A — dikonfirmasi Applicability Check (Step 2 sudah memverifikasi kedua template QWeb tidak butuh
perubahan sama sekali).

## [Fase G2] Validasi Akhir

✅ **Pass (2026-08-27)** — `docker compose up` dengan `--test-enable --test-tags=/pin_message` (dan
dua modul lain sekaligus): **0 failed, 0 error dari 9 test**, termasuk kedua Tour test browser asli
(`pin_message_toggle_pin_tour`, `pin_message_action_menu_pin_visible_tour`, keduanya "tour
succeeded"). Kriteria minimal G2 terpenuhi: tidak ada warning server saat start, tidak ada error
console browser, `DIFF-01`/`DIFF-02` terkonfirmasi valid di runtime nyata (bukan cuma baca kode).

---

## Temuan di Luar Spec (kalau ada)

- [x] **Ada** — fix pertama untuk `_to_store` (Step 6 awal, cuma tambah parameter `fields`) TERNYATA
  TIDAK CUKUP, baru ketahuan lewat Tour test (G2), bukan dari baca kode/spec. Root cause sebenarnya
  (mekanisme `Store.add()` 19.0 tidak punya jalur pintas dict-value seperti 18.0) TIDAK tercakup di
  `03_MIGRATION_SPEC.md`/`02_DIFF_ANALYSIS.md` — Step 2 mengidentifikasi signature `_to_store`
  berubah, tapi tidak menganalisis PERILAKU `Store.add()` sendiri saat dipanggil dari dalam
  `_to_store()`. Tidak perlu balik ke Step 3/4 (dampak kecil, sudah divalidasi G2 PASS) — dicatat di
  sini + `FINDINGS.md` (`MF-18`) untuk jejak lengkap.

## Kontribusi ke Knowledge Base

- [x] **Ada** — `Store.add()`/`add_records_fields()` 19.0 (mekanisme baru untuk menambah field value
  dari dalam `_to_store()` tanpa infinite recursion) adalah temuan BARU, lebih dalam dari yang sudah
  dicatat Step 2 (yang cuma soal signature). Dicatat ke
  `migration-records/pos-margin-sale_18.0_19.0/SUMMARY.md`.
