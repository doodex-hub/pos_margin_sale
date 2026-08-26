# Migration Intake — pin_message

**Step:** 1 — Intake & Scope
**Versi:** 18.0 → 19.0
**Tanggal:** 2026-08-26
**Status:** 🔄 Draft ditulis, gate BELUM ditutup — menunggu jawaban dev di §0 (folder referensi,
konsisten dengan dua modul lain di project ini)

---

## 0. Folder Referensi — WAJIB Ditanyakan ke Dev SEKARANG

- [ ] `native-target` (Odoo 19.0 Community) — belum dijawab dev. Blocking gate Step 1 project ini.
- [ ] `native-source` (18.0 Community) — opsional, belum dijawab.
- [ ] `native-target-enterprise` — dependency map modul ini sendiri (§2 di bawah: `web`, `base`,
  `mail`, semua Community) TIDAK menemukan indikasi Enterprise. Tetap wajib ditanya eksplisit
  (aturan §0 template, silence ≠ tidak ada) — belum dijawab. Modul sibling `sale_margin_threshold`
  yang membuat `native-target-enterprise` wajib untuk PROJECT ini secara keseluruhan (lihat dokumen
  modul itu), tapi modul `pin_message` sendiri tidak butuh itu.
- [ ] `third-party-source`/`third-party-target` — tidak ada indikasi OCA. Belum dikonfirmasi
  eksplisit ke dev.

**Status:** belum bisa ditutup.

### 0a. Konfirmasi Branch/Versi

- [x] Sama seperti modul lain — dual-branch, 18.0→19.0 dikonfirmasi dev.

### 0b. Gate: Path Absolut `.claude/settings.json`

Sama seperti modul lain — satu `.claude/settings.json` untuk seluruh repo. Lihat status di dokumen
`pos_margin_threshold`.

---

## Ringkasan untuk Review — Perlu Konfirmasi User

1. **[BLOCKING]** Sama seperti modul lain: `native-target` belum dijawab.
2. **Modul ini paling kecil dari ketiganya** (1 model file, 3 file JS patch, 2 template QWeb patch,
   1 CSS) tapi **arsitekturnya paling rapuh** — HAMPIR SEMUA logic-nya adalah patch terhadap komponen
   Owl inti `mail`/`discuss`, area yang historis paling sering berubah struktural antar versi major
   Odoo (persis seperti yang terjadi di migrasi 17→18: `Chatter.load()` override rusak total,
   `messagePinService` implisit, method `canAddReaction` pindah dari getter component ke method
   model). Prioritas riset Step 2 tertinggi di seluruh project ini.
3. **Bug/gap warisan yang harus dipertahankan (bukan diperbaiki tanpa izin):**
   - `MF-09`: cabang `is_discussion === true` di `onClickPin()` (`message.js`) adalah dead code sejak
     18.0 (Discuss-channel pin sekarang lewat mekanisme native, tidak lewat method ini) — dikonfirmasi
     harmless (tidak ada fitur hilang), tapi kodenya tetap ada. Pertahankan as-is kecuali user minta
     dibersihkan.
4. **Satu bug KECIL yang MASIH TERBUKA (belum diperbaiki dari project sebelumnya, bukan sesuatu yang
   baru ditemukan sekarang):** `MF-10` — `console.log(component.message.type)` di `pinMessage.js`
   baris 7, jalan setiap kali action-menu pesan di-render (setiap hover/klik pesan di chatter manapun
   di seluruh sistem). Debug leftover, tidak fungsional tapi noise console browser tiap user.
   **Perlu keputusan user:** dibersihkan sebagai bagian project ini, atau tetap dipertahankan
   (konsisten prinsip "port kode saja, jangan perbaiki bug lama tanpa izin")?
5. **Tidak ada dependency Enterprise/OCA sama sekali** untuk modul ini — hanya Community
   (`web`, `base`, `mail`).

---

## 1. Modul & Scope

- **Modul:** `pin_message`.
- **Deskripsi:** menambahkan kemampuan "pin" pesan/log-note di chatter (terpisah dari mekanisme pin
  native Discuss-channel) — badge jumlah pesan ter-pin, section collapsible "Pinned Messages", dua
  entry-point UI (tombol inline per-pesan + entry action-menu "Pin") yang keduanya memanggil RPC
  server `toggle_pin` yang sama.
- **Saling depend dengan modul lain?** Tidak ada keterkaitan fungsional dengan
  `pos_margin_threshold`/`sale_margin_threshold` sama sekali (dikonfirmasi `CLAUDE.md` §Adaptasi
  multi-modul) — bisa dikerjakan/direview independen kapan saja.

## 2. Dependency Map (auto-scan)

| Dependency | Tipe | Versi tersedia di target? | Catatan |
|---|---|---|---|
| `web` | Native Community | Belum dicek | — |
| `base` | Native Community | Belum dicek | — |
| `mail` | Native Community | Belum dicek | **Prioritas riset Step 2 tertinggi** — seluruh integrasi JS/Owl modul ini adalah patch terhadap komponen `mail` core |

**Tidak ada Enterprise/OCA di dependency map modul ini.**

Dependency implisit/inferred (import JS, tidak ada di manifest sama sekali karena manifest hanya
mendeklarasikan path asset, bukan dependency modul Python — ini normal untuk cara Odoo asset
bundling bekerja, bukan gap):
- `@mail/chatter/web_portal/chatter` (`Chatter`), `@mail/core/common/message` (`Message`),
  `@mail/core/common/message_card_list` (`MessageCardList`), `@mail/core/common/message_actions`
  (`messageActionsRegistry`), `@web/core/utils/{hooks,patch}`, `@web/core/l10n/translation`,
  `@odoo/owl`.
- **`this.messagePinService`** (`message.js`) — dipakai TANPA pernah diimpor/dideklarasikan di modul
  ini — hanya ada karena `mail` core sendiri menyuntikkan service ini ke komponen `Message`. Dependency
  implisit yang paling rapuh: kalau mekanisme injeksi ini berubah nama/hilang di 19.0, cabang kode
  ini (dead code, `MF-09`) akan error saat dipanggil — walau saat ini tidak pernah benar-benar
  dipanggil (native Discuss pin tidak lewat jalur ini).

## 2b. Struktur & Fitur Modul (auto-scan)

| Fitur | Ada di modul? | Lokasi/bukti | Fase step 6 relevan |
|---|---|---|---|
| Controllers (route custom) | ☐ Tidak | Tidak ada folder `controllers/` sama sekali | D1 — N/A |
| Assets/CSS/JS custom | ☑ Ya | `static/src/{css,js,xml}/*`, terdaftar penuh di `assets.web.assets_backend` + `web.assets_tests` (tour) | D2, E, F — WAJIB full treatment |
| Komponen Owl/JavaScript custom | ☑ Ya (patch + `t-inherit`, TIDAK ADA komponen baru) | `patch(Chatter.prototype)` (`chatter.js`), `patch(Message.prototype)` (`message.js`), `messageActionsRegistry.add()` (`pinMessage.js`), dua `t-inherit` (`pinnedMessages.xml` ke `mail.Chatter`+`mail.Message`, `message_card_list.xml` ke `mail.MessageCardList`) | E — prioritas TERTINGGI di seluruh project, area paling rapuh |
| Field JSON / relasi berantai >2 level / dynamic model creation | ☐ Tidak | Hanya `is_pinned` (Boolean) di `mail.message` | B2 — N/A |
| View pakai `attrs=`/`states=`/domain/context dinamis | ☐ N/A — tidak ada `ir.ui.view`/`views/*.xml` sama sekali | `data: []` di manifest; semua UI lewat Owl QWeb `t-inherit`, bukan `ir.ui.view` | C2 — N/A murni |

## 3. Sifat Migrasi

- [x] Port kode saja
- [ ] Upgrade instance

## 4. Baseline Spec / Characterization Test (gate)

- [x] Sumber: `doc-dev/migration_17.0_18.0/doc/01_intake/pin_message/01b_BASELINE_SPEC.md` (baseline
  18.0 project sebelumnya) + cross-check kode aktual + `FINDINGS.md` project itu. Hasil:
  `01b_BASELINE_SPEC.md` (dokumen ini).
- [x] `01b_BASELINE_SPEC.md` sudah diisi.

### 4a. Dokumen Pelengkap Lain

- [x] Belum dikonfirmasi eksplisit — asumsi "tidak ada", konsisten pola project sebelumnya.

## 4b. Source Masih Aktif Dikembangkan?

- [x] Tidak (asumsi, belum dikonfirmasi ulang eksplisit).

## 5. Scope Boundary

- **Harus tetap identik:** semua `BSL-NNN` di `01b_BASELINE_SPEC.md`, termasuk `MF-09` (dead code
  dipertahankan) — KECUALI `MF-10` (`console.log` leftover) yang butuh keputusan eksplisit user
  (lihat §Ringkasan poin 4).
- **Yang sengaja diubah:** tidak ada yang diusulkan di titik ini.

## 6. Constraint

- Deadline: belum disebutkan.
- Owner: belum disebutkan.
