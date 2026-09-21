# Migration Intake — pin_message

**Step:** 1 — Intake & Scope
**Versi:** 19.0 → 20.0
**Tanggal:** 2026-09-21
**Status:** ✔️ Gate LULUS (2026-09-21) — semua §0/§0a/§0b terpenuhi (diwarisi dari bootstrap project +
dikonfirmasi ulang sesi ini)

---

## 0. Folder Referensi — WAJIB Ditanyakan ke Dev SEKARANG

> Sudah dijawab eksplisit di bootstrap project (lihat `CLAUDE.md` §"Status saat ini" +
> §"Folder yang perlu di-connect", 2026-09-21) — dicatat di sini sebagai fakta yang sudah
> dikonfirmasi, bukan pertanyaan terbuka baru untuk modul ini.

- [x] `native-target` (Odoo 20.0 Community) — **dikonfirmasi 2026-09-21:**
  `D:\Kuncoro\doodex\repo\odoo20` (clone git resmi `odoo/odoo`, branch `20.0`). Dicek langsung sesi
  ini: `mail`, `base`, `web` semua ada (`odoo20/addons/mail`, `odoo20/addons/base`,
  `odoo20/addons/web`).
- [x] `native-source` (19.0, opsional) — **dikonfirmasi 2026-09-21:**
  `D:\Kuncoro\doodex\repo\enterprise19.0` (Community+Enterprise 19.0 gabungan, peninggalan project
  18.0→19.0, **bukan git repo** — tidak ada `.git/`, JANGAN jalankan git di sana). Untuk modul ini,
  source of truth utama tetap kode di branch `migration/19.0` repo ini sendiri (dual-branch, lihat
  §0a), bukan folder ini — folder ini dipakai sebagai referensi tambahan Step 2 kalau perlu
  cross-check struktur asli 19.0 di luar repo.
- [x] `native-target-enterprise` — **dikonfirmasi 2026-09-21:** `D:\Kuncoro\doodex\repo\enterprise20`
  (clone git resmi Enterprise, branch `20.0`, folder **TERPISAH** dari `native-target` kali ini —
  beda dari project 18.0→19.0 yang memakai folder gabungan). Modul `pin_message` sendiri **tidak
  butuh peran Enterprise ini** (lihat §2 — hanya depend ke `web`/`base`/`mail`, ketiganya Community,
  dan dikonfirmasi TIDAK ada di `enterprise20` sebagai modul terpisah — memang seharusnya begitu,
  Community-only), tapi folder-nya sudah tersedia untuk project secara keseluruhan
  (`sale_margin_threshold` yang membutuhkannya).
- [x] `third-party-source`/`third-party-target` (OCA/vendor) — **dikonfirmasi TIDAK ADA** (diwarisi
  dari dua project migrasi sebelumnya, 17.0→18.0 dan 18.0→19.0, keduanya tidak menemukan indikasi
  OCA untuk modul ini; dikonfirmasi ulang oleh dev di awal project ini per `CLAUDE.md`). Grep source
  `pin_message` sesi ini juga tidak menemukan import/dependency di luar `web`/`base`/`mail`.

**Status:** ✔️ **Gate Step 1 LULUS (2026-09-21).**

### 0a. Konfirmasi Branch/Versi

- [x] **Model dual-branch (bukan dual-clone) — sudah dikonfirmasi dev di bootstrap project, dicatat
  eksplisit di sini karena menyimpang dari default template (yang mengasumsikan dua clone fisik
  terpisah):**
  - Source (19.0) = branch `migration/19.0`, repo yang SAMA dengan target (`pos-margin-sale-migration-20`).
    Read-only — AI **tidak pernah** `git checkout` ke branch ini; baca isi file 19.0 lewat
    `git show migration/19.0:<path>` atau `git diff migration/20.0 migration/19.0 -- <path>` bila
    perlu. Branch ini sudah lulus 10 dari 11 step migrasi 18.0→19.0 (UAT sign-off menunggu eksekusi
    manual manusia) — jadi kode di branch ini adalah baseline 19.0 yang **sudah terverifikasi**
    lewat Step 1-10 project sebelumnya, bukan cuma "port belum ditest".
  - Target (20.0) = branch `migration/20.0`, working branch aktif project ini. Dibuat 2026-09-21 via
    `git checkout -b migration/20.0` dari tip `migration/19.0` (commit `5876d01`) — working tree saat
    ini **identik byte-for-byte** dengan `migration/19.0` (belum ada edit migrasi apapun).
  - Kedua branch bukan clone fisik terpisah — satu working directory, satu `.git/`, dibedakan lewat
    branch pointer. Konsekuensi: AI tidak bisa "buka dua folder" untuk membandingkan, harus pakai
    `git show`/`git diff` antar-branch di repo yang sama.
- [x] Versi Odoo semantik: **19.0 → 20.0**, dikonfirmasi eksplisit di `CLAUDE.md` §Identitas
  (bukan cuma dugaan dari nama branch).

### 0b. Gate: Path Absolut `.claude/settings.json`

Satu `.claude/settings.json` untuk seluruh repo (tiga modul) — **sudah dipenuhi saat bootstrap
project (2026-09-21)**, dikonfirmasi di `CLAUDE.md` §"Adaptasi dual-branch" (paragraf "Konfig yang
diwarisi saat bootstrap"): `ABS_PATH_NATIVE_TARGET`, `ABS_PATH_NATIVE_TARGET_ENTERPRISE` sudah diisi
path nyata untuk pasangan 19.0→20.0; entry `deny` milik folder referensi project 18.0→19.0 yang tidak
lagi relevan sebagai native-target sudah dibuang; `ABS_PATH_THIRD_PARTY_*` tidak ada baris-nya sama
sekali (dikonfirmasi tidak dipakai). Tidak ada placeholder `{{ABS_PATH_...}}` literal tersisa. Tidak
ada aksi tambahan dibutuhkan khusus untuk modul `pin_message` di gate ini.

---

## Ringkasan untuk Review — Perlu Konfirmasi User

1. **Tiga asumsi carry-forward BELUM dikonfirmasi ulang eksplisit oleh dev untuk project ini**
   (diwarisi apa adanya dari dua project migrasi sebelumnya, 17.0→18.0 dan 18.0→19.0, konsisten
   `CLAUDE.md` §Identitas): (a) **§3 Sifat migrasi = "Port kode saja"**, (b) **§4a Dokumen pelengkap
   lain = "tidak ada"**, (c) **§4b Source aktif dikembangkan = "Tidak"**. Ketiganya ditulis sebagai
   asumsi default di dokumen ini, bukan hasil konfirmasi baru — kalau dev punya info berbeda untuk
   project ini, beri tahu sebelum Step 2 mulai.
2. **Temuan preliminary paling penting sesi ini:** mekanisme `_to_store()` di
   `mail.message` — yang di-override modul ini (lihat `01b_BASELINE_SPEC.md` `BSL-007`) dan yang
   jadi salah satu dari DUA gap kritis (`MF-14`/`MF-18`) migrasi 18.0→19.0 sebelumnya — **sudah tidak
   ada sama sekali** di `odoo20/addons/mail/models/mail_message.py` (grep penuh: 0 match untuk
   `_to_store`/`to_store` di file itu). Sebagai gantinya, 20.0 memakai pola baru
   `_store_message_fields(self, res: Store.FieldList, ...)` dengan API `res.one()`/`res.many()`/
   `res.from_method()` (lihat `odoo20/addons/mail/tools/store_handler.py`,
   `odoo20/addons/mail/models/mail_message.py:1174` dst). Ini indikasi KUAT override modul ini butuh
   **rewrite arsitektural**, bukan cuma penyesuaian parameter seperti waktu 18.0→19.0 — **prioritas
   riset tertinggi Step 2**, jangan diasumsikan "sudah pernah diperbaiki sekali jadi cukup port
   ulang".
3. **`messageActionsRegistry`** (import `@mail/core/common/message_actions`) — lokasi file/import
   path dikonfirmasi masih ada persis sama di `odoo20/addons/mail/static/src/core/common/
   message_actions.js` (grep cepat sesi ini), TAPI payload/callback shape-nya **belum di-diff**
   (deep diff itu tugas Step 2). Jangan diasumsikan stabil hanya karena lokasi filenya tidak
   berubah — riwayat migrasi 18.0→19.0 modul ini justru membuktikan payload registry ini yang
   berubah total (`title`→`name`, `onClick`→`onSelected`, `component`→objek polos) meski path
   importnya tetap sama persis. Cek ulang mekanisme lengkap ini di Step 2, jangan cuma existence.
4. **Dua `[GAP]` ditemukan di `01b_BASELINE_SPEC.md`** saat cross-check baseline lama (18.0→19.0,
   ditulis SEBELUM fix `MF-14`/`MF-15`/`MF-18` landed) ke kode 19.0 aktual sekarang (SESUDAH fix):
   `BSL-005` (bentuk callback `messageActionsRegistry`) dan `BSL-007` (signature `_to_store()` +
   mekanisme `store.add_records_fields`). Kode aktual menang (sudah mencerminkan versi ter-fix),
   detail perbedaan tercatat di §8 dokumen itu — bukan regresi, murni baseline lama yang belum
   pernah diupdate pasca-fix.
5. **Tidak ada dependency Enterprise/OCA** untuk modul ini — hanya `web`/`base`/`mail`, ketiganya
   Community, dikonfirmasi masih ada di `native-target` (`odoo20`) dan dikonfirmasi TIDAK ada
   (dengan benar) sebagai modul terpisah di `native-target-enterprise` (`enterprise20`).
6. **Test/characterization test SUDAH ADA** di repo ini sendiri (`pin_message/tests/
   test_pin_message.py`, `test_pin_message_tour.py` + `static/tests/tours/pin_message_tour.js`,
   hasil proses `doc-dev-backfill` sebelumnya) — lokasi SAMA dengan `target-codebase`/branch
   `migration/19.0`. Tidak perlu tindakan tambahan §4, tapi ini aset executable berharga untuk
   Step 9/10 nanti (karakterisasi behavior sudah bisa dijalankan, bukan cuma baca kode statis).
7. Modul ini tetap dikonfirmasi sebagai **modul terkecil (jumlah file) tapi paling rapuh secara
   arsitektur** dari ketiga modul project (konsisten temuan dua project migrasi sebelumnya) — seluruh
   logic-nya adalah patch/`t-inherit` terhadap komponen Owl inti `mail` + satu override Python
   `mail.message._to_store()`, area yang historis paling sering berubah struktural antar versi major
   Odoo. Prioritas riset Step 2 tertinggi tetap berlaku untuk pasangan 19.0→20.0 ini.

---

## 1. Modul & Scope

- **Modul:** `pin_message`.
- **Deskripsi:** menambahkan kemampuan "pin" pesan/log-note di chatter (terpisah dari mekanisme pin
  native Discuss-channel) — badge jumlah pesan ter-pin, section collapsible "Pinned Messages", dua
  entry-point UI (tombol inline per-pesan + entry action-menu "Pin") yang keduanya memanggil RPC
  server `toggle_pin` yang sama. Behavior tidak berubah dari dua project migrasi sebelumnya
  (17.0→18.0, 18.0→19.0) — lihat `01b_BASELINE_SPEC.md`.
- **Saling depend dengan modul lain?** Tidak ada keterkaitan fungsional dengan
  `pos_margin_threshold`/`sale_margin_threshold` (dikonfirmasi `CLAUDE.md` §"Adaptasi multi-modul")
  — bisa dikerjakan/direview independen kapan saja.

## 2. Dependency Map (auto-scan)

| Dependency | Tipe (Native Community / Native Enterprise / OCA / Custom) | Versi tersedia di target? | Catatan |
|---|---|---|---|
| `web` | Native Community | ✅ Ada — `odoo20/addons/web` | Dependency manifest langsung |
| `base` | Native Community | ✅ Ada — `odoo20/addons/base` | Dependency manifest langsung |
| `mail` | Native Community | ✅ Ada — `odoo20/addons/mail` | **Prioritas riset Step 2 tertinggi** — seluruh integrasi JS/Owl + satu override Python modul ini adalah patch terhadap komponen `mail` core. Dikonfirmasi TIDAK ada sebagai modul terpisah di `enterprise20` (benar, Community-only). |

**Tidak ada Enterprise/OCA di dependency map modul ini** — dikonfirmasi ulang lewat pengecekan
langsung ke `enterprise20` (tidak ada folder `mail`/`base`/`web` di sana, sesuai ekspektasi
modul-modul Community-only).

Dependency implisit/inferred (import JS, tidak ada di manifest sama sekali karena manifest hanya
mendeklarasikan path asset, bukan dependency modul Python — normal untuk cara Odoo asset bundling
bekerja, bukan gap):
- `@mail/chatter/web_portal/chatter` (`Chatter`), `@mail/core/common/message` (`Message`),
  `@mail/core/common/message_card_list` (`MessageCardList`), `@mail/core/common/message_actions`
  (`messageActionsRegistry`), `@web/core/utils/{hooks,patch}`, `@web/core/l10n/translation`,
  `@odoo/owl`. Dikonfirmasi sesi ini: keempat path `@mail/...` di atas MASIH ADA persis sama di
  `odoo20/addons/mail` (existence-only check — lihat §2b untuk detail risiko payload/shape yang
  belum di-diff).
- **`this.messagePinService`** (`message.js`) — dipakai TANPA pernah diimpor/dideklarasikan di modul
  ini — hanya ada karena `mail` core sendiri menyuntikkan service ini ke komponen `Message`.
  Dependency implisit paling rapuh: kalau mekanisme injeksi ini berubah nama/hilang di 20.0, cabang
  kode ini (dead code, lihat `BSL-002`/warisan `MF-09`) akan error saat dipanggil — walau saat ini
  tidak pernah benar-benar dipanggil (native Discuss pin tidak lewat jalur ini). Belum dicek ulang
  keberadaannya secara spesifik di 20.0 sesi ini (di luar scope Step 1 — existence check dependency
  eksplisit/manifest saja, bukan tiap service implisit; catat untuk Step 2).

## 2b. Struktur & Fitur Modul (auto-scan)

| Fitur | Ada di modul? | Lokasi/bukti (kalau ada) | Fase step 6 yang jadi relevan |
|---|---|---|---|
| Controllers (route custom) | ☐ Tidak | Tidak ada folder `controllers/` sama sekali | D1 — N/A |
| Assets/CSS/JS custom | ☑ Ya | `static/src/{css,js,xml}/*`, terdaftar penuh di `assets.web.assets_backend` + `web.assets_tests` (tour) | D2, E, F — WAJIB full treatment |
| Komponen Owl/JavaScript custom | ☑ Ya (patch + `t-inherit`, TIDAK ADA komponen baru) | `patch(Chatter.prototype)` (`chatter.js`), `patch(Message.prototype)` (`message.js`), `messageActionsRegistry.add()` (`pinMessage.js`), dua `t-inherit` (`pinnedMessages.xml` ke `mail.Chatter`+`mail.Message`, `message_card_list.xml` ke `mail.MessageCardList`) | E — prioritas TERTINGGI di seluruh project, area paling rapuh |
| Field JSON, relasi berantai (>2 level), atau dynamic model creation (`self.env[var]`) | ☐ Tidak | Hanya `is_pinned` (Boolean) di `mail.message` | B2 — N/A |
| View pakai `attrs=`/`states=`/`domain=`/`context=` dinamis | ☐ N/A — tidak ada `ir.ui.view`/`views/*.xml` sama sekali | `data: []` di manifest; semua UI lewat Owl QWeb `t-inherit`, bukan `ir.ui.view` | C2 — N/A murni |

> **Catatan risiko tertinggi (flag eksplisit untuk Step 2, diperkuat dari lesson dua project migrasi
> sebelumnya):** dua titik integrasi berikut adalah tempat KEDUA gap kritis (`MF-14`/`MF-15`)
> migrasi 18.0→19.0 sebelumnya ditemukan, dan preliminary check sesi ini (§2, Ringkasan poin 2-3)
> sudah menunjukkan indikasi perubahan lagi di 20.0 — treat dengan kecurigaan ekstra, jangan
> diasumsikan "sudah pernah diperbaiki sekali jadi otomatis stabil":
> 1. **`pin_message/models/mail_message.py:22-36`** — override `_to_store()`. Mekanisme core yang
>    di-extend ini (`mail.message._to_store()` + `Store.add_records_fields()`) **kemungkinan besar
>    sudah tidak ada lagi** di 20.0 (lihat Ringkasan poin 2) — kandidat rewrite arsitektural, bukan
>    penyesuaian parameter.
> 2. **`pin_message/static/src/js/pinMessage.js:5-27`** — registrasi `messageActionsRegistry.add()`.
>    Lokasi/import path dikonfirmasi masih sama (§2), payload/callback shape belum di-diff — riwayat
>    migrasi sebelumnya modul ini adalah persis titik ini yang payload-nya berubah total.

Kalau semua kolom "Ada di modul?" terisi "Tidak", step 6 langsung menyatakan fase terkait N/A di
Applicability Check — **tidak berlaku untuk modul ini**, dua fase (D2/E/F) wajib full treatment.

## 3. Sifat Migrasi

- [x] Port kode saja (belum ada data produksi — instalasi baru di versi target)
- [ ] Upgrade instance

> **Flag Ringkasan poin 1:** ini asumsi carry-forward dari dua project migrasi sebelumnya
> (17.0→18.0, 18.0→19.0), **belum dikonfirmasi ulang eksplisit oleh dev untuk project 19.0→20.0
> ini** — konsisten `CLAUDE.md` §Identitas ("belum dikonfirmasi ulang eksplisit untuk project ini").
> Step 7 (Data Migration Plan) diasumsikan N/A berdasarkan ini.

## 4. Baseline Spec / Characterization Test (gate)

- [x] Cek dulu: apakah modul punya `FUNCTIONAL_SPEC.md` lama di `source-codebase`? **Tidak ada**
  (dikonfirmasi glob `pin_message/**/FUNCTIONAL_SPEC.md` — nihil, konsisten pola dua project
  migrasi sebelumnya yang juga tidak menemukan file ini untuk modul ini).
  - Karena TIDAK ADA `FUNCTIONAL_SPEC.md` bernama itu, tapi ADA dokumen setara-peran dari project
    migrasi sebelumnya — `doc-dev/migration_18.0_19.0/doc/01_intake/pin_message/01b_BASELINE_SPEC.md`
    (baseline spec 18.0→19.0) — dokumen itu diperlakukan sebagai **draft awal utama** untuk
    `01b_BASELINE_SPEC.md` project ini, PERSIS seperti proses yang digariskan template untuk modul
    yang punya `FUNCTIONAL_SPEC.md` lama: (1) baca sebagai draft, (2) cross-check tiap klaim `BSL-NNN`
    ke kode 19.0 aktual (branch `migration/19.0`) satu per satu, (3) cocok → salin/rangkum dengan
    rujukan `(ref: 18.0→19.0 BSL-NNN)`, (4) tidak cocok → kode menang, penyimpangan dicatat eksplisit
    di §8 dokumen itu (`[GAP]`, dua baris "Spec lama"/"Kode aktual").
  - Hasil cross-check: **2 penyimpangan `[GAP]` ditemukan** (`BSL-005`, `BSL-007` — lihat Ringkasan
    poin 4 dan `01b_BASELINE_SPEC.md` §4/§5) — keduanya adalah bukti bahwa fix `MF-14`/`MF-15`/`MF-18`
    dari migrasi 18.0→19.0 (ditemukan/diperbaiki SETELAH baseline 18.0→19.0 ditulis) sudah landed di
    kode aktual, tapi dokumen baseline lama itu sendiri belum pernah diupdate untuk mencerminkannya.
- [x] Test/characterization test lama — **ADA, dan lokasinya SAMA dengan `target-codebase`**
  (`pin_message/tests/test_pin_message.py`, `test_pin_message_tour.py`,
  `static/tests/tours/pin_message_tour.js`, hasil proses `doc-dev-backfill` yang dijalankan sebelum
  project migrasi 18.0→19.0). Tidak perlu tindakan tambahan gate ini.
- [x] `01b_BASELINE_SPEC.md` sudah diisi (baca kode source module langsung — model, field, workflow,
  side effect, client behavior), termasuk section "Ringkasan untuk Review" dan ID `BSL-NNN` di tiap
  klaim behavior.

### 4a. Dokumen Pelengkap Lain

- [x] **Belum dikonfirmasi eksplisit oleh dev untuk project ini** — ditulis sebagai asumsi
  carry-forward "tidak ada", konsisten pola dua project migrasi sebelumnya (keduanya juga tidak
  menemukan/mengonfirmasi dokumen pelengkap lain untuk modul ini). **Flag Ringkasan poin 1** — kalau
  dev punya info berbeda, sampaikan sebelum Step 2 mulai.

## 4b. Source Masih Aktif Dikembangkan?

- [x] Tidak (asumsi carry-forward dari dua project sebelumnya, **belum dikonfirmasi ulang eksplisit**
  untuk project ini — **flag Ringkasan poin 1**, konsisten `CLAUDE.md` §Identitas).

## 5. Scope Boundary

- **Harus tetap identik:** semua `BSL-NNN` di `01b_BASELINE_SPEC.md` yang bertag `[MATCH]`, termasuk
  dua quirk warisan (`BSL-002`, `BSL-016`, `BSL-017` — dead code `is_discussion`/`messagePinService`,
  dipertahankan as-is). Dua klaim `[GAP]` (`BSL-005`, `BSL-007`) — versi KODE AKTUAL (pasca-fix
  `MF-14`/`MF-15`/`MF-18`) adalah yang harus dipertahankan identik ke 20.0, BUKAN versi yang
  digambarkan baseline lama 18.0→19.0 (pra-fix).
- **Yang sengaja diubah:** tidak ada yang diusulkan di titik ini. Perubahan MEKANISME internal
  `_to_store()`/`messageActionsRegistry` yang mungkin dibutuhkan Step 6 untuk kompatibilitas 20.0
  (lihat §2b) bukan perubahan business rule — outcome/behavior end-user harus tetap identik.

## 6. Constraint

- Deadline: belum disebutkan.
- Owner: belum disebutkan.
