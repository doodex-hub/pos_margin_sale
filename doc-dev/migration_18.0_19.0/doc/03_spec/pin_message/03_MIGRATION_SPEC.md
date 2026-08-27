# Migration Spec (Teknis) — pin_message

**Step:** 3 — Migration Spec
**Versi:** 18.0 → 19.0
**Ref:** `02_diff/pin_message/02_DIFF_ANALYSIS.md`
**Tanggal:** 2026-08-26

---

## 1. Ringkasan Strategi

Dua perbaikan WAJIB, keduanya install/runtime-blocking dengan blast radius melampaui modul ini
sendiri — **prioritas tertinggi di seluruh project**, harus selesai sebelum modul ini bisa lulus G1
sama sekali: (1) signature `_to_store()` Python, (2) payload shape `messageActionsRegistry` JS.
Sisanya (`chatter.js`, kedua xpath template, `canAddReaction` call) **tidak butuh perubahan** —
dikonfirmasi stabil di Step 2. `MF-09` (dead code `is_discussion`) tetap dipertahankan aman.

## 2. Strategi per File/Simbol (ringkasan umum)

| File/simbol | Ref `DIFF-NNN` | Strategi migrasi | Risiko | Ref `BSL-NNN` |
|---|---|---|---|---|
| `models/mail_message.py:22` `_to_store(self, store, /, **kwargs)` | `DIFF-01` | **WAJIB ubah signature:** `def _to_store(self, store, fields, /, **kwargs): super()._to_store(store, fields, **kwargs); ...` — tambahkan parameter positional `fields` persis sesuai signature 19.0 core, teruskan ke `super()` | **Kritis** — tanpa ini, `TypeError` di SETIAP `store.add(<mail.message>, ...)` manapun di sistem begitu modul terinstall | `BSL-006` |
| `static/src/js/pinMessage.js:5-26` `messageActionsRegistry.add("pins", {condition, icon, title, onClick, sequence})` | `DIFF-02` | **WAJIB rewrite total:** rename `title`→`name`, `onClick`→`onSelected`; ubah SEMUA signature callback dari `(component) => ...` jadi `({message, thread, owner, store, action}) => ...` — HAPUS semua akses `component.props.*`, ganti jadi destructure langsung `message`/`thread`. Rujuk pola native 19.0: `mail/static/src/discuss/message_pin/common/message_actions.js` (`registerMessageAction`) sebagai referensi bentuk yang benar | **Kritis** — crash di getter reactive yang dievaluasi untuk SETIAP pesan yang di-render, berpotensi mematahkan action-menu pesan secara luas | `BSL-004` |
| `static/src/js/pinMessage.js:7` `console.log(...)` | — (bukan `DIFF`, ini `MF-10` warisan) | Kalau user setuju dibersihkan (lihat `FINDINGS.md` `MF-10`), hapus baris ini SEKALIAN saat rewrite `DIFF-02` di atas — efisien karena file yang sama sudah disentuh | Rendah, tapi tetap butuh persetujuan eksplisit user sebelum dihapus (bukan port murni) | — |
| `static/src/js/chatter.js` | `DIFF-03` | **Tidak ada perubahan** — import path, `load()` call, `Chatter.components` semua stabil | Tidak ada | `BSL-007`, `BSL-008` |
| `static/src/js/message.js` `this.messagePinService` (`is_discussion` branch) | `DIFF-04` | **Tidak ada perubahan** — dead code di kedua versi, tetap aman dipertahankan (`MF-09`) | Tidak ada | `BSL-002` |
| `static/src/js/pinMessage.js:8` `canAddReaction(thread)` call | `DIFF-05` | **Tidak ada perubahan pada CARA memanggilnya** (setelah `DIFF-02` diperbaiki) — tapi WAJIB regression-check manual di Step 9: kondisi tambahan 19.0 (`!isPending`, `!thread.isTransient`, `thread.has_mail_thread`) mungkin membuat action "Pin" tersembunyi di kasus yang dulu terlihat di 18.0 | Rendah — bukan bug, tapi behavior yang perlu diverifikasi ulang | `BSL-010` |
| `static/src/xml/pinnedMessages.xml`, `message_card_list.xml` | `DIFF-06`, `DIFF-07` | **Tidak ada perubahan** — kedua xpath anchor tetap valid | Tidak ada | `BSL-011`, `BSL-012` |
| `__manifest__.py` | — | Bump `version` ke `19.0.x.x` | Tidak ada | — |

## 2b. Risk Analysis Terstruktur

### Critical Migration Blockers
*(Mencegah instalasi atau operasi inti di 19.0)*

| # | Isu | Lokasi | Rujukan knowledge base |
|---|---|---|---|
| 1 | Manifest version — harus `19.0.x.x` | `__manifest__.py` | — |
| 2 | `_to_store()` signature — `fields` jadi positional wajib, `TypeError` di SETIAP pengiriman pesan | `models/mail_message.py:22` | `FINDINGS.md` `MF-14`, `02_DIFF_ANALYSIS.md` `DIFF-01` |
| 3 | `messageActionsRegistry` payload shape berubah total — crash di getter reactive per-pesan | `static/src/js/pinMessage.js:5-26` | `FINDINGS.md` `MF-15`, `02_DIFF_ANALYSIS.md` `DIFF-02` |

**Priority:** **TERTINGGI DI SELURUH PROJECT.** Item #2 (`_to_store`) berpotensi mematahkan chatter/
Discuss SECARA UMUM begitu modul ini terinstall di instance 19.0 manapun — ini bukan skenario
"fitur pin rusak", ini skenario "seluruh pengiriman pesan ke frontend rusak selama modul ini
terinstall". Item #3 sama urgensinya karena reactive getter dievaluasi untuk setiap pesan yang
dirender. **Kedua fix WAJIB diselesaikan sebelum G1 (install test) modul ini dijalankan** — bahkan
install test standar (buka Discuss/chatter apapun setelah modul terinstall) kemungkinan besar akan
langsung menunjukkan error, beda dari kasus `pos_margin_threshold` yang errornya baru muncul saat
fitur spesifik dipakai.

### OWL Widget yang Butuh Rewrite/Review

| Widget/Registry | File | Risiko | Detail |
|---|---|---|---|
| `messageActionsRegistry` entry `"pins"` | `static/src/js/pinMessage.js` | Kritis | `DIFF-02` — rewrite total sesuai pola native 19.0 |

**Urutan wajib:** migrasi Python (`_to_store`) dan JS (`pinMessage.js`) bisa paralel (tidak saling
bergantung), tapi KEDUANYA harus selesai sebelum modul dianggap siap G1. `chatter.js`/`message.js`
tidak perlu disentuh (Fase E/F N/A untuk file-file ini spesifik, tapi tetap smoke-test).

### Controller & Route

Tidak ada — modul ini tidak punya controller sama sekali.

### Assets & Dependency

Tidak ada perubahan path asset — semua file `static/src/{css,js,xml}` tetap terdaftar sama di
`assets.web.assets_backend`.

### Kompatibilitas Data Model

| # | Isu | Lokasi | Priority | Ref `BSL-NNN` |
|---|---|---|---|---|
| 1 | `mail.message.is_pinned` field — tidak berubah struktur | `models/mail_message.py:7` | Tidak ada aksi | `BSL-001` |
| 2 | `_to_store()` override signature | `models/mail_message.py:22` | **Kritis, lihat blocker #2 di atas** | `BSL-006` |

### Risiko Integrasi

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | `messagePinService` implisit, tidak pernah ada sebagai service terdaftar di `mail` (dikonfirmasi ulang Step 2, sama di 18.0 dan 19.0) | `static/src/js/message.js` | Rendah — dead code tetap aman, tidak ada regresi baru |
| 2 | Native pin action key `"pin"` (singular) vs modul ini `"pins"` (jamak) — dikonfirmasi TIDAK ada kolisi nama key di registry (beda kata) | `static/src/js/pinMessage.js` | Tidak ada |

### Urutan Prioritas Testing

1. **Install & startup** — manifest version, dependency (`web`, `base`, `mail`) tetap Community.
2. **Buka chatter APAPUN (bukan cuma yang ada pesan pin)** — verifikasi `_to_store()` fix (`DIFF-01`)
   tidak `TypeError` sama sekali. Ini test PALING PENTING di seluruh project — kalau gagal di sini,
   TIDAK ADA chatter yang bisa dibuka selama modul terinstall.
3. **Hover/klik pesan APAPUN untuk buka action-menu** — verifikasi `messageActionsRegistry` fix
   (`DIFF-02`) tidak crash getter `condition` untuk pesan MANAPUN (bukan cuma yang seharusnya bisa
   di-pin).
4. Fitur pin sesungguhnya: tombol inline (`onMessagePin`) dan action-menu "Pin" (`onClickPin`
   via `DIFF-02` fix) — keduanya harus toggle `is_pinned`, badge, section "Pinned Messages".
5. Discuss-channel native pin/unpin (jalur `is_discussion`, `MF-09`) — verifikasi tetap berfungsi
   penuh lewat mekanisme native (bukan lewat modul ini).

### View List Checklist

N/A — tidak ada `ir.ui.view`/`<tree>` di modul ini sama sekali.

### Estimasi Effort (opsional)

| Area | Effort | Catatan |
|---|---|---|
| `_to_store()` signature fix | Kecil | Satu method, perubahan mekanis tapi WAJIB tepat |
| `messageActionsRegistry` rewrite | Sedang | Perlu baca pola native 19.0 dengan teliti sebelum menulis, bukan tebak-tebak |
| Sisanya | Nol | Tidak ada perubahan |

## 3. Data Migration

N/A — port kode saja.

## 4. Scope

### Termasuk
- `DIFF-01` (signature `_to_store`), `DIFF-02` (rewrite `messageActionsRegistry`), bump manifest
  version.
- `MF-10` (`console.log` cleanup) HANYA kalau user eksplisit setuju — bukan default.

### Di Luar Scope (sengaja, disetujui di intake)
- `MF-09` (dead code `is_discussion`) — dipertahankan, tidak dibersihkan kecuali user minta.
