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
| G1 (checkpoint Fase A) | ⏳ Belum dijalankan — lihat "Riwayat Percobaan G1" | — |
| A3 | N/A — tidak ada wizard/TransientModel di modul ini | 2026-08-26 |
| A4 | ✅ — struktur folder tidak berubah, tidak ada yang perlu dinormalisasi | 2026-08-26 |
| A5 | ✅ | 2026-08-26 |
| B1 | ✅ — `is_pinned`/`toggle_pin()` diverifikasi tidak butuh perubahan | 2026-08-26 |
| B2 | N/A — dikonfirmasi Applicability Check | — |
| C1 | N/A — tidak ada view sama sekali | 2026-08-26 |
| C2 | N/A — dikonfirmasi Applicability Check | — |
| D1 | N/A — dikonfirmasi Applicability Check | — |
| D2 | N/A — dikonfirmasi Applicability Check | — |
| E | ✅ | 2026-08-26 |
| F | N/A — dikonfirmasi Applicability Check | — |
| G2 (validasi akhir/runtime) | ⏳ Menunggu G1 | — |

## Riwayat Percobaan G1 (Install Test)

**Belum dijalankan** — environment Docker 19.0 (`docker-env/docker-compose.yml`) masih memakai image
18.0 dari project sebelumnya, belum di-bump ke 19.0. Perlu keputusan dev soal mode eksekusi
(A/B/C, lihat `06a_CODE_MIGRATION_PHASES.md` "Checkpoint G1") dan sumber image 19.0 (tidak ada image
Docker Hub publik `odoo:19.0` yang dikonfirmasi tersedia — kemungkinan perlu build image sendiri dari
`native-target` `enterprise19.0`, atau dev sudah punya sumber lain) sebelum G1 bisa dijalankan.

| # | Dijalankan setelah fase | Mode | Hasil | Error (kalau fail) | Tanggal |
|---|---|---|---|---|---|
| 1 | A2 | — | ⏳ Belum dijalankan | — | — |

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
    Komentar ditambah menjelaskan perubahan ini.
- **Secara eksplisit TIDAK dilakukan:** tidak ada perubahan pada `toggle_pin()`, `is_pinned` field,
  atau logic penambahan `is_pinned` ke `store` — hanya signature yang diubah, behavior identik.
  `fields` tidak pernah dibaca/dipakai langsung (modul ini selalu menambahkan `is_pinned` tanpa
  syarat, tidak bergantung pada daftar field yang diminta).
- **Risiko:** LOW (perubahan mekanis, sudah diverifikasi terhadap signature 19.0 asli di Step 2) —
  tapi **belum divalidasi runtime** (G1/G2 belum jalan).
- **Status:** ✅ Selesai (kode) — ⚠️ Perlu validasi G1/G2

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
  17→18 — historically fragile) — **belum divalidasi runtime** (G1/G2, khususnya Tour test
  `pin_message_action_menu_pin_visible_tour`, belum jalan).
- **Status:** ✅ Selesai (kode) — ⚠️ Perlu validasi G1/G2 + Tour test re-run

## [Fase F] Upgrade Template

N/A — dikonfirmasi Applicability Check (Step 2 sudah memverifikasi kedua template QWeb tidak butuh
perubahan sama sekali).

## [Fase G2] Validasi Akhir

⏳ Belum dijalankan — menunggu G1 (install test) dan environment Docker 19.0.

---

## Temuan di Luar Spec (kalau ada)

- [x] Tidak ada — semua perubahan kode persis mengikuti `03_MIGRATION_SPEC.md`, tidak ada yang
  ditemukan di luar rencana.

## Kontribusi ke Knowledge Base

- [x] Tidak ada temuan baru yang perlu dicatat di titik ini — temuan `mail` 18→19 (`_to_store`,
  `messageActionsRegistry`) sudah dicatat di Step 2 (`migration-records/pos-margin-sale_18.0_19.0/SUMMARY.md`).
  Kalau G1/G2 nanti menemukan sesuatu yang tidak terduga, akan ditambahkan sebagai entri baru.
