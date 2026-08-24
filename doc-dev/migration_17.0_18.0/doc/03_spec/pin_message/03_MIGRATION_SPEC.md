# Migration Spec (Teknis) — pin_message

**Step:** 3 — Migration Spec
**Versi:** 17.0 → 18.0
**Ref:** `02_diff/pin_message/02_DIFF_ANALYSIS.md`
**Tanggal:** 2026-08-24

---

## 1. Ringkasan Strategi

Modul dengan risiko tertinggi di project ini — hampir seluruh logic patch JS/OWL ke komponen inti `mail`, dan SEMUA titik integrasi itu `[TIDAK TERVERIFIKASI]` (tidak ada fix konkret yang bisa ditulis di muka). Sisi Python (`mail_message.py`) sangat minimal dan aman. Strategi: port seluruh kode apa adanya, jalankan G1 (install — akan langsung ketahuan kalau xpath `t-inherit` gagal match), lalu G2 (browser, WAJIB — beberapa risiko seperti `messagePinService` cuma kelihatan dari eksekusi klik nyata).

## 2. Strategi per File/Simbol

| File/simbol | Ref `DIFF-NNN` | Strategi migrasi | Risiko | Ref `BSL-NNN` |
|---|---|---|---|---|
| `models/mail_message.py` | — | Port langsung, tidak ada API yang berubah | Rendah | `[BSL-001]` |
| `static/src/xml/pinnedMessages.xml` (`t-inherit="mail.Chatter"`, `t-inherit="mail.Message"`) | DIFF-01, DIFF-02 | Port apa adanya, G1 akan langsung gagal (`ParseError`) kalau xpath tidak match — baca pesan error untuk tahu struktur baru | Tinggi | `[BSL-007]`, `[BSL-009]` |
| `static/src/xml/message_card_list.xml` (`t-inherit="mail.MessageCardList"`) | DIFF-03 | Sama seperti di atas | Sedang | `[BSL-007]` |
| `static/src/js/{message,chatter}.js` (import `@mail/core/common/message`, `@mail/core/web/chatter`) | DIFF-04 | Port apa adanya, cek console error saat load (G1/G2) | Tinggi | `[BSL-002]`, `[BSL-007]` |
| `static/src/js/pinMessage.js` (import `messageActionsRegistry`) | DIFF-05 | Port apa adanya | Tinggi | `[BSL-003]` |
| `static/src/js/message.js` — `this.messagePinService` | DIFF-06 | Port apa adanya, **WAJIB test G2**: klik pin di pesan Discuss channel (`is_discussion=True`) — kalau `TypeError`, service ini perlu di-inject eksplisit lewat `useService` (perubahan struktural, minta persetujuan) | **Tertinggi di modul ini** — review statis tidak akan menangkap ini | `[BSL-002]` |
| `static/src/js/{chatter,message}.js` — `useService("orm")` | DIFF-07 | Port apa adanya | Rendah | — |
| `static/src/css/style.css` | DIFF-11 | Port apa adanya, verifikasi visual G2 (warna section pinned messages) | Rendah | — |
| `__manifest__.py` | — | Bump `version` → `18.0.1.0` | Rendah | — |

## 2b. Risk Analysis Terstruktur

### Critical Migration Blockers

| # | Isu | Lokasi | Rujukan knowledge base |
|---|---|---|---|
| 1 | Manifest version → `18.0.x` | `__manifest__.py` | Konvensi umum |
| 2 | (potensial) xpath `t-inherit` ke `mail.Chatter`/`mail.Message`/`mail.MessageCardList` gagal match | `static/src/xml/*.xml` | DIFF-01/02/03, `[TIDAK TERVERIFIKASI]` |
| 3 | (potensial) import path `@mail/core/*` gagal resolve | `static/src/js/*.js` | DIFF-04/05, `[TIDAK TERVERIFIKASI]` |

**Priority:** HIGH untuk #2/#3 — modul ini WAJIB jadi kandidat pertama dijalankan G1 di Step 6 antara ketiga modul (paling banyak unknown, paling penting cepat dapat sinyal nyata).

### OWL Widget yang Butuh Rewrite/Review

| Widget | File | Risiko | Detail |
|---|---|---|---|
| Patch `Message.prototype` | `static/src/js/message.js` | Tinggi | `onClickPin`/`onMessagePin`, termasuk akses implisit `this.messagePinService` (`MF-09`, DIFF-06) |
| Patch `Chatter.prototype` | `static/src/js/chatter.js` | Tinggi | `initialLoad`, `pinnedMessages` getter |
| `t-inherit` template (3 file XML) | `static/src/xml/*.xml` | Tinggi | Xpath ke class QWeb core |
| Action registry `messageActionsRegistry.add` | `static/src/js/pinMessage.js` | Tinggi | Termasuk `MF-10` (console.log leftover — port apa adanya, JANGAN dihapus sebagai "cleanup" di luar scope) |

**Urutan wajib Step 6 (Fase E sebelum F):** modul ini PUNYA template QWeb custom (`t-inherit`) — migrasi SEMUA JS dulu (Fase E: `message.js`, `chatter.js`, `pinMessage.js`), BARU sentuh template XML (Fase F: `pinnedMessages.xml`, `message_card_list.xml`). Kebalikannya berisiko `OwlError: Unknown QWeb directive` (lihat `knowledge/version-diffs/17-to-18.md` §1b).

### Controller & Route

Tidak ada.

### Assets & Dependency

Tidak ada isu — `assets.web.assets_backend` menunjuk file yang benar-benar eksis semua.

### Kompatibilitas Data Model

Field `is_pinned` di `mail.message` — tidak ada indikasi field ini bentrok/berubah struktur di core 18.0 (field custom modul ini sendiri).

### Risiko Integrasi

Tidak ada — modul ini independen, tidak berinteraksi dengan `pos_margin_threshold`/`sale_margin_threshold` (`CLAUDE.md` §Adaptasi multi-modul).

### Urutan Prioritas Testing

1. Install (G1) — prioritas TERTINGGI project ini untuk dijalankan lebih dulu, paling banyak unknown
2. Buka chatter record apapun, pastikan tidak ada error console saat mount
3. Toggle pin log note (non-discussion) — jalur RPC langsung, `[BSL-001]`/`[BSL-002]`
4. **Toggle pin pesan Discuss channel** — jalur `messagePinService`, WAJIB dites eksplisit (DIFF-06, risiko tertinggi silent-fail)
5. Verifikasi section "Pinned Messages" muncul & berfungsi (badge, expand, jump)

### View List (dulu Tree) Checklist

Tidak berlaku — tidak ada `<tree>`.

### Estimasi Effort

| Area | Effort | Catatan |
|---|---|---|
| Manifest version bump | Sangat rendah | Mekanis |
| XML template (`t-inherit`) | **Tidak bisa diestimasi sebelum G1** | Tergantung penuh hasil xpath matching nyata |
| JS (`message.js`/`chatter.js`/`pinMessage.js`) | **Tidak bisa diestimasi sebelum G1/G2** | Terutama `messagePinService` (DIFF-06) — berpotensi butuh perubahan struktural kalau service API berubah |

## 3. Data Migration

N/A — port kode saja.

## 4. Scope

### Termasuk
- Bump `version` manifest.
- Port seluruh JS/XML/Python apa adanya.
- Penyesuaian import/xpath/service access **HANYA kalau terbukti wajib dari G1/G2** — dicatat sebagai keputusan teknis di `06c_IMPLEMENTATION_LOG.md` Step 6, bukan diasumsikan sekarang.

### Di Luar Scope
- Mengubah `onClickPin` (`MF-09`) jadi extend `super()` — kecuali terbukti wajib.
- Menghapus `console.log` (`MF-10`) — dipertahankan apa adanya kecuali disetujui eksplisit.
