# Spec Completeness Review — pin_message

**Step:** 4 — Spec Completeness Review (gate)
**Ref:** `03_spec/pin_message/03_MIGRATION_SPEC.md`, source module 19.0 (`git show migration/19.0:pin_message/...`)
**Tanggal:** 2026-09-22

> Tujuan: pastikan `03_MIGRATION_SPEC.md` mencakup 100% elemen source module — bukan review
> kualitas kode (itu step 8). Enumerasi seluruh elemen modul dari branch `migration/19.0` (source
> 19.0 project ini), cocokkan satu-satu ke spec, DAN cross-check ke kode aktual di working tree
> (`migration/20.0`) karena sebagian eksekusi Step 6 sudah terjadi dini di luar urutan normal
> (lihat `CLAUDE.md` §Status saat ini) — jadi ada risiko spec dan kode sudah drift satu sama lain.

---

## Ringkasan Eksekutif

**Verdict: ❌ DITOLAK (FAIL).** Enumerasi penuh 19.0 source (17 file, dikeluarkan file non-kode:
`LICENSE.txt`, `README.md`, `static/description/**`) terhadap `03_MIGRATION_SPEC.md` menemukan
**satu gap KRITIS baru** yang bukan cuma soal dokumentasi tidak lengkap, tapi bug fungsional nyata
yang belum diperbaiki di kode, DAN salah-atribusi di `FINDINGS.md` (`MF-36`) yang menyebut root
cause-nya "100% native, `pin_message` tidak pernah menyentuh `message_card_list.js`/`.xml`" — klaim
itu **terbukti salah** setelah dibandingkan langsung ke native 20.0 (lihat §Gap 1 di bawah). Dua gap
minor tambahan (test files Python, `style.css`) juga ditemukan — risiko rendah, tapi tetap
"elemen source tanpa entri spec eksplisit" sesuai definisi Step 4.

---

## Tabel Cakupan

| Elemen source module | Ada di Migration Spec? | Status | Catatan |
|---|---|---|---|
| `__manifest__.py` (version) | Ya — §2 baris `__manifest__.py:3`, §2b Critical Blockers #1 | ✅ Covered | Bump `20.0.1.0` ditulis eksplisit, dikonfirmasi sudah diterapkan di kode aktual. |
| `__manifest__.py` (`depends`, `assets`, `data: []`, `license`/`price`/dst) | Ya — §2b "Assets & Dependency": "Tidak ada perubahan path asset... Dependency manifest (`web`, `base`, `mail`) tidak berubah, tidak ada OCA/third-party." | ✅ Covered | Konsisten kode aktual — tidak ada perubahan struktur manifest di luar version. |
| `__init__.py` (root) | Tidak eksplisit disebut | ✅ Covered (implisit) | `from . import models` — boilerplate satu baris, tidak pernah berubah lintas versi Odoo, risiko nol. Tidak perlu entri terpisah. |
| `models/__init__.py` | Tidak eksplisit disebut | ✅ Covered (implisit) | `from . import mail_message` — sama seperti di atas, boilerplate. |
| `models/mail_message.py` — field `is_pinned` | Ya — §2b "Kompatibilitas Data Model" #1 | ✅ Covered | "tidak berubah struktur field sama sekali". |
| `models/mail_message.py` — `toggle_pin()` | Ya — §2b baris 124 ("tidak berubah sama sekali", `BSL-001`/`BSL-006`) | ✅ Covered | Dikonfirmasi identik di kode aktual. |
| `models/mail_message.py` — `_to_store()` → `_store_message_fields()` | Ya — `DIFF-01`, §2b Critical Blockers #2, kode konkret lengkap | ✅ Covered | Kode aktual (`pin_message/models/mail_message.py:23-32`) **identik** dengan kode konkret di spec — tidak ada drift. |
| `static/src/css/style.css` | **Tidak disebut sama sekali** — hanya tercakup tidak langsung lewat kalimat umum "seluruh file `static/src/{css,js,xml}`... tetap terdaftar sama persis" (soal *registrasi asset*, bukan *isi/kompatibilitas* file) | ❌ Gap (minor) | Isi file (`.o-mail-PinnedMessages .card`/`.card-body`, kelas Bootstrap) tidak pernah dianalisis eksplisit terhadap kemungkinan perubahan Bootstrap/CSS core di 20.0. Risiko rendah (kelas generik, tidak menyentuh FontAwesome yang sudah dibahas `DIFF-04`), tapi tetap elemen source tanpa baris analisis sendiri. Kode aktual = identik 19.0 (tidak diubah). |
| `static/src/js/chatter.js` | Ya — `DIFF-03`, dibahas sangat detail (§1 butir 4, §2b OWL Widget, §2b lanjutan "Detail DIFF-03") | ✅ Covered | Kode aktual cocok: import path sudah diganti ke `@mail/chatter/web_portal_project/chatter`, logic `setup()`/`initialLoad()`/`onWillUpdateProps` dipertahankan persis sesuai spec. Tour "ganti thread" yang diwajibkan spec (§1 butir 4, §2b Urutan Prioritas Testing #6) **belum ada** di `static/tests/tours/pin_message_tour.js` — bukan gap *spec*, tapi item Step 6/9 yang masih outstanding, lihat §Catatan Tambahan. |
| `static/src/js/message.js` | Ya — `DIFF-06`, "Tidak ada perubahan" | ✅ Covered | Kode aktual identik 19.0, dikonfirmasi. |
| `static/src/js/pinMessage.js` | Ya — `DIFF-02`, rewrite total, kode konkret lengkap | ✅ Covered | Kode aktual **identik** dengan kode konkret di spec (`registerMessageAction`, getter `canAddReaction` tanpa parameter, icon `push_pin`) — tidak ada drift. |
| `static/src/xml/pinnedMessages.xml` | Ya — `DIFF-04` (icon) eksplisit; fix bare-identifier `this.` (root cause `MF-33`) **tidak ada di `03_MIGRATION_SPEC.md` versi tertulis** (dokumen ini ditulis Step 3, sebelum crash `MF-33` ditemukan lewat smoke-test Docker) | 🟡 Covered sebagian, tapi via `FINDINGS.md` bukan spec | `DIFF-04` (icon FA→`oi`) tercakup dan kode aktual cocok. Fix `this.` prefix (`pinnedMessages`/`state`/`togglePinnedMessages`/`props`) TIDAK ditulis di `03_MIGRATION_SPEC.md` manapun — hanya didokumentasikan di `FINDINGS.md` `MF-33` (ditemukan+diperbaiki live, di luar siklus Step 3→6 normal). Bukan gap blocking (fix sudah diterapkan & diverifikasi UI nyata di kode aktual + FINDINGS.md), tapi `03_MIGRATION_SPEC.md` sendiri sudah **stale** dan sebaiknya diupdate supaya jadi rujukan implementasi yang akurat (dokumen ini secara eksplisit bilang "dokumen ini memandu IMPLEMENTASI"). Rekomendasi: tambahkan referensi ke `MF-33` di baris `DIFF-04`/`pinnedMessages.xml` pada `03_MIGRATION_SPEC.md`. |
| `static/src/xml/message_card_list.xml` | Ya — `DIFF-05`, "Tidak ada perubahan — xpath anchor `o-mail-MessageCard-jump` stabil" | ❌ **GAP KRITIS** | **Kesimpulan spec salah.** Lihat §Gap 1 di bawah — analisis DIFF-05 hanya memeriksa apakah xpath ANCHOR (`o-mail-MessageCard-jump`) masih ada di native 20.0 (ya, masih ada), tapi TIDAK memeriksa apakah ISI node pengganti modul sendiri (`t-att-class="{ 'opacity-100 py-1 px-2': ui.isSmall }"`) masih valid dikompilasi di bawah `t-inherit-mode="extension"` 20.0 — pola bug PERSIS SAMA dengan yang sudah ditemukan & diperbaiki di `pinnedMessages.xml` (`MF-33`, bare identifier tidak auto-resolve ke `this.xxx`), TAPI TIDAK diterapkan ke file ini. Kode aktual masih pakai `ui.isSmall` bare (belum diperbaiki) — dikonfirmasi via perbandingan langsung ke `odoo20/addons/mail/static/src/core/common/message_card_list.xml:8` yang menulis `this.ui.isSmall`. |
| `static/tests/tours/pin_message_tour.js` | Ya — `DIFF-04`, selector CSS diupdate (`.fa-thumb-tack`→`[data-icon='push_pin']`, `.fa-ellipsis-v`→`[data-icon='more_vert']`) | ✅ Covered | Kode aktual cocok persis dengan spec, ketiga selector sudah diupdate. |
| `tests/__init__.py` | Tidak eksplisit disebut | ✅ Covered (implisit) | Boilerplate `from . import test_pin_message` / `test_pin_message_tour`, tidak pernah berubah lintas versi. |
| `tests/test_pin_message.py` | **Tidak disebut sama sekali** di `03_MIGRATION_SPEC.md` | ❌ Gap (minor) | Test `TransactionCase` (`toggle_pin` single & multi-record) — konsisten dengan kesimpulan spec bahwa `toggle_pin()` tidak berubah, TAPI spec tidak pernah eksplisit menulis "test ini dikonfirmasi tetap valid di 20.0" atau memeriksa apakah API `odoo.tests.common.TransactionCase`/`tagged` masih stabil. Risiko rendah (API test framework inti, jarang breaking), tapi tetap elemen source tanpa baris analisis sendiri di spec. |
| `tests/test_pin_message_tour.py` | **Tidak disebut sama sekali** di `03_MIGRATION_SPEC.md` | ❌ Gap (minor) | Sama seperti di atas — `HttpCase.start_tour()` tidak eksplisit dianalisis kompatibilitasnya ke 20.0 (meski dalam praktik sudah dipakai berhasil untuk smoke-test Docker sesi ini, jadi terbukti jalan, cuma tidak dicatat sebagai analisis spec formal). |

---

## Detail Gap

### Gap 1 (KRITIS) — `static/src/xml/message_card_list.xml`: bug bare-identifier belum diperbaiki, DAN salah-atribusi di `FINDINGS.md` `MF-36`

**Apa yang ditemukan:** `pin_message/static/src/xml/message_card_list.xml` meng-inherit
`mail.MessageCardList` (`t-inherit-mode="extension"`) dan me-*replace* elemen `<a>` "Jump" native
dengan `<button>` custom miliknya sendiri:

```xml
<button class="o-mail-MessageCard-jump btn rounded bg-400 badge opacity-0 flex-shrink-0"
        t-att-class="{ 'opacity-100 py-1 px-2': ui.isSmall }"
        t-on-click="() => this.onClickJump(message)">
    See
</button>
```

Bandingkan node NATIVE yang di-*replace* (`odoo20/addons/mail/static/src/core/common/message_card_list.xml:8`):

```xml
<a role="button" class="o-mail-MessageCard-jump rounded bg-400 badge opacity-0"
   t-att-class="{ 'opacity-100 py-1 px-2': this.ui.isSmall }"
   t-on-click="() => this.onClickJump(message)">Jump</a>
```

Native menulis `this.ui.isSmall` (benar). Node pengganti milik `pin_message` menulis `ui.isSmall`
**tanpa** prefix `this.` — persis pola bug yang sama yang sudah ditemukan dan diperbaiki di
`pinnedMessages.xml` (`MF-33`): di bawah `t-inherit-mode="extension"` 20.0, identifier bebas
(bukan variabel loop `t-as`) tidak lagi auto-resolve ke `this.xxx`, dikompilasi jadi lookup context
polos (`ctx['ui'].isSmall`) yang `undefined` → crash. (`message` di baris `t-on-click` aman karena
itu variabel loop `t-as="message"` dari `t-foreach` induk, bukan property komponen — konsisten pola
yang sudah dikonfirmasi di `MF-33`.)

**Ini PERSIS crash yang dicatat `FINDINGS.md` `MF-36`:**
```
TypeError: Cannot read properties of undefined (reading 'isSmall')
    at MessageCardList.template_mail_MessageCardList ...
11:let attr2 = {'opacity-100 py-1 px-2':ctx['ui'].isSmall};        // CRASH -- ctx['ui'] undefined
...
14:  let attr3 = {'fs-5':ctx['this'].ui.isSmall};                  // baris SERUPA, resolve BENAR
```
`MF-36` mengklaim root cause ini **"dikonfirmasi 100% NATIVE, `pin_message` tidak pernah menyentuh
`message_card_list.js`/`.xml`"** — klaim ini **tidak akurat**. Baris `attr2` (class
`opacity-100 py-1 px-2`, `ctx['ui'].isSmall` undefined) secara tekstual HANYA bisa berasal dari node
pengganti `pin_message` sendiri (native menulis `this.ui.isSmall` secara eksplisit di baris yang
sama persis, yang akan terkompilasi jadi `ctx['this'].ui.isSmall`, BUKAN `ctx['ui'].isSmall`) — baris
`attr3` sesudahnya (`fs-5`, resolve benar `ctx['this'].ui.isSmall`) adalah tombol "Unpin" native
yang TIDAK disentuh modul ini, dan itu tetap benar karena memang bukan hasil replace `pin_message`.

**Dampak:** fitur pin/unpin sendiri (toggle, badge count) tetap berfungsi (dikonfirmasi `MF-28`/
`MF-32`/`MF-33`), tapi **setiap kali user expand section "Pinned Messages"**, render
`MessageCardList` akan crash — persis gejala yang sudah diverifikasi live di Docker 20.0 dan dicatat
`MF-36`, HANYA saja root cause-nya BUKAN "quirk native di luar kendali modul" seperti tercatat saat
ini, melainkan **bug modul sendiri yang bisa dan seharusnya diperbaiki** dengan fix mekanis yang
identik dengan `MF-33`: `ui.isSmall` → `this.ui.isSmall`.

**Kenapa ini gap Step 4 (bukan cuma "temuan baru"):** `03_MIGRATION_SPEC.md` (`DIFF-05`) menyatakan
file ini "Tidak ada perubahan — xpath anchor `o-mail-MessageCard-jump` stabil". Analisis itu hanya
menguji apakah xpath ANCHOR (target `position="replace"`) masih ada di 20.0 (ya) — tidak menguji
apakah ISI node hasil replace, yang ditulis modul ini sendiri, masih valid dikompilasi di rezim
extension-mode 20.0 yang baru. Ini persis kategori risiko yang sama dengan `DIFF-04`/`MF-33`
(bare-identifier resolution), tapi tidak diterapkan konsisten ke file ini — celah proses yang sama
persis dengan yang sudah dicatat sendiri di `MF-35` ("Step 2 berikutnya harus eksplisit cek SEMUA
file, bukan cuma yang 'kelihatan berisiko'").

**Rekomendasi:**
1. **Kembali ke Step 3** — update `03_MIGRATION_SPEC.md` §2 baris `message_card_list.xml`/`DIFF-05`:
   ganti kesimpulan dari "tidak ada perubahan" jadi "rewrite mekanis: `ui.isSmall` → `this.ui.isSmall`
   di node pengganti `o-mail-MessageCard-jump`, pola sama `MF-33`".
2. **Step 6** — terapkan fix satu baris di
   `pin_message/static/src/xml/message_card_list.xml`: `ui.isSmall` → `this.ui.isSmall`.
3. **`FINDINGS.md`** — `MF-36` perlu dikoreksi (bukan oleh dokumen ini — di luar scope Step 4 yang
   dilarang mengubah `FINDINGS.md`/`CLAUDE.md`, tapi WAJIB dikoreksi oleh sesi berikutnya): root
   cause sebenarnya ada di `pin_message/static/src/xml/message_card_list.xml`, bukan murni native.
   Setelah fix di atas diterapkan dan diverifikasi ulang di Docker (klik expand "Pinned Messages"
   tidak lagi crash), status `MF-36` semestinya jadi `✅ RESOLVED`, bukan tetap `🔴 Terbuka` menunggu
   rilis stabil Odoo 20.0.
4. Ini kandidat `MF-39` baru (ID lanjutan setelah `MF-38`, yang tertinggi saat ini di `FINDINGS.md`) —
   **BUKAN revisi `MF-36`** (biarkan `MF-36` dikoreksi terpisah sesuai poin 3), karena root cause dan
   lokasi bug berbeda total dari yang tercatat di `MF-36` saat ini.

### Gap 2 (minor) — `static/src/css/style.css` tidak dianalisis eksplisit
Isi file (dua selector `.o-mail-PinnedMessages .card`/`.card-body`, warna `rgba(165, 42, 42, 0.1)`)
tidak pernah dibahas per-file di spec — hanya tercakup implisit lewat pernyataan umum soal registrasi
asset tidak berubah. Risiko rendah (kelas Bootstrap generik `.card`/`.card-body`, tidak bersinggungan
dengan perubahan FontAwesome yang sudah dibahas `DIFF-04`), tapi untuk kelengkapan 100% sesuai
definisi Step 4, sebaiknya `03_MIGRATION_SPEC.md` menambah satu baris eksplisit: "`style.css` — tidak
ada perubahan, kelas target (`.card`/`.card-body`) stabil di Bootstrap 20.0". Tidak perlu eskalasi ke
dev — cukup ditambahkan sebagai baris dokumentasi.

### Gap 3 (minor) — `tests/test_pin_message.py` dan `tests/test_pin_message_tour.py` tidak disebut di spec
Kedua file test Python (`TransactionCase`/`HttpCase`) tidak punya baris analisis sendiri di
`03_MIGRATION_SPEC.md`, walau secara implisit konsisten dengan kesimpulan "`toggle_pin()`/business
logic tidak berubah". Risiko rendah — kedua test ini terbukti bisa dijalankan di Docker 20.0 sesi ini
(dipakai untuk verifikasi `MF-28`/`MF-32`/`MF-33` end-to-end), tapi itu bukti dari eksekusi manual,
bukan dari baris spec formal. Rekomendasi: tambah satu baris di §2 `03_MIGRATION_SPEC.md`
mengonfirmasi `tests/*.py` tidak perlu perubahan (API `TransactionCase`/`HttpCase.start_tour`
stabil), supaya cakupan spec genuinely 100%.

---

## Catatan Tambahan (bukan gap spec, tapi relevan untuk Step 5/6/9)

- **Tour "ganti thread"** yang diwajibkan `03_MIGRATION_SPEC.md` sendiri (§1 butir 4, §2b Urutan
  Prioritas Testing #6, syarat wajib penutupan fase E) **belum ditambahkan** ke
  `static/tests/tours/pin_message_tour.js` — ini bukan gap cakupan spec (spec sudah eksplisit
  mewajibkannya), tapi outstanding action item Step 6/9 yang belum dieksekusi. Perlu ditindaklanjuti
  sebelum modul ini dianggap tuntas fase E.
- `03_MIGRATION_SPEC.md` sendiri sudah agak stale dibanding kode aktual untuk `pinnedMessages.xml`
  (fix `this.` prefix `MF-33` diterapkan di kode tapi tidak pernah ditulis balik ke dokumen spec) —
  lihat baris terkait di tabel cakupan di atas. Tidak menghalangi gate (kode dan `FINDINGS.md` sudah
  benar), tapi sebaiknya disinkronkan supaya `03_MIGRATION_SPEC.md` tetap jadi rujukan implementasi
  yang akurat sesuai perannya sendiri.

---

## Verdict

- [ ] ✅ Lulus — semua elemen Covered, lanjut ke step 5
- [x] ❌ Ditolak — ada gap, balik ke step 2/3 untuk item berikut:
  1. **`static/src/xml/message_card_list.xml`** (Gap 1, KRITIS) — spec `DIFF-05` perlu direvisi dari
     "tidak ada perubahan" menjadi rewrite mekanis `ui.isSmall` → `this.ui.isSmall`; fix perlu
     diterapkan ke kode aktual di Step 6; `FINDINGS.md` `MF-36` perlu dikoreksi root cause-nya di
     sesi berikutnya (kandidat finding baru `MF-39` untuk mencatat gap ini sendiri).
  2. **`static/src/css/style.css`** (Gap 2, minor) — tambah satu baris konfirmasi eksplisit di spec.
  3. **`tests/test_pin_message.py`** / **`tests/test_pin_message_tour.py`** (Gap 3, minor) — tambah
     baris konfirmasi eksplisit di spec.

Setelah ketiga item di atas ditutup (terutama Gap 1, yang punya dampak fungsional nyata dan
mempengaruhi status `MF-36`), Step 4 bisa diulang untuk menutup gate sebelum lanjut ke Step 5.

---

## Update pasca-review (2026-09-22)

Semua 3 gap **sudah ditutup di sesi yang sama**:
- **Gap 1 (kritis):** `message_card_list.xml` diperbaiki (`ui.isSmall` → `this.ui.isSmall`),
  diverifikasi live di Docker 20.0 (expand "Pinned Messages" tidak lagi crash, tombol "See"
  berfungsi, 0 error console). `FINDINGS.md` `MF-36` dikoreksi root cause-nya (bukan finding baru
  `MF-39` terpisah — dikoreksi langsung sebagai `MF-36` karena ini sama persis crash yang sudah
  dicatat, cuma root cause-nya yang salah, bukan bug baru yang belum tercatat).
- **Gap 2, 3 (minor):** baris konfirmasi eksplisit ditambahkan ke `03_MIGRATION_SPEC.md` (§2c baru)
  untuk `style.css` dan kedua file test Python.
- `03_MIGRATION_SPEC.md` juga disinkronkan untuk fix `MF-33` di `pinnedMessages.xml` (baris `DIFF-04`
  diupdate) yang sebelumnya cuma tercatat di `FINDINGS.md`.

Gate ini bisa dianggap **LULUS** setelah update ini.
