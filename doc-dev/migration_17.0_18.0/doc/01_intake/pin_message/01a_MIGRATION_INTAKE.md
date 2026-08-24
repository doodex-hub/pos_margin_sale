# Migration Intake — pin_message

**Step:** 1 — Intake & Scope
**Versi:** 17.0 → 18.0
**Tanggal:** 2026-08-24
**Status:** ✔️ Gate lulus (2026-08-24) — checklist §0/§0a/§4a/§4b sama seperti 2 modul lain di project ini, dev sudah konfirmasi jawaban berlaku project-wide

---

## 0. Folder Referensi / 0a / 0b

- [x] Sama seperti `pos_margin_threshold`/`sale_margin_threshold` — tidak ada folder referensi (`native-*`/`third-party-*`) tersedia, tidak ada Enterprise/OCA (manifest cuma `web`, `base`, `mail` — semua Community), branch/versi sudah dikonfirmasi, tidak ada proteksi path teknis di `.claude/settings.json`.

---

## Ringkasan untuk Review — Perlu Konfirmasi User

1. **Modul ini TIDAK terkait fungsional dengan `pos_margin_threshold`/`sale_margin_threshold`** (dikonfirmasi dari `doc-dev/backfill/spec/pin_message/01A_FUNCTIONAL_SPEC.md` — produk berbeda, fitur pin chatter, kebetulan di-bundle repo yang sama). Bisa dikerjakan/direview independen sesuai `CLAUDE.md` §Adaptasi multi-modul.
2. Dokumentasi backfill lengkap tersedia (`01A_FUNCTIONAL_SPEC.md`+`01B_ACCEPTANCE_CRITERIA.md`, 2026-07-31, tervalidasi). Kode tidak berubah sejak itu — satu-satunya commit setelahnya (`313cef5 wrong banner`) cuma mengubah path gambar banner di manifest, bukan business logic.
3. **2 finding backfill diwarisi:** `MF-09` (dari F-06 — patch JS `onClickPin` MENIMPA TOTAL patch core `discuss/message_pin`, bukan extend via `super()`), `MF-10` (dari F-07 — `console.log` debug tertinggal di `pinMessage.js`, dieksekusi tiap render action menu).
4. **Modul ini paling berisiko untuk Step 2** dari ketiga modul — HAMPIR SELURUH logic-nya patch JS/OWL ke komponen inti `mail` module (`Message`, `Chatter`, `MessageCardList`, `messageActionsRegistry`) via `t-inherit`/`patch()`. Modul `mail`/`discuss` termasuk yang paling sering di-refactor signifikan antar versi mayor Odoo (arsitektur chatter/discuss OWL). **`MF-09` sendiri jadi lebih berisiko di 18.0** — kalau core `message_patch.js` berubah behavior `onClickPin` (bukan cuma nama, tapi behaviornya), full-override modul ini TIDAK akan otomatis ikut berubah (karena tidak pernah panggil `super()`), berpotensi silent-diverge dari core yang baru.
5. Tidak ada `security/ir.model.access.csv` di modul ini — dikonfirmasi BUKAN gap, karena modul cuma menambah field+method ke `mail.message` yang sudah py punya access rule dari core `mail`, tidak butuh rule baru.

---

## 1. Modul & Scope

- Modul: `pin_message` — menambahkan kemampuan "pin" (menyematkan) pesan/log note penting di chatter model apapun, supaya tidak hilang di antara banyak pesan lain.
- Tidak depend/berinteraksi dengan `pos_margin_threshold`/`sale_margin_threshold`.

## 2. Dependency Map (auto-scan)

| Dependency | Tipe | Versi tersedia di target? | Catatan |
|---|---|---|---|
| `web` | Native Community | Ya | |
| `base` | Native Community | Ya | |
| `mail` | Native Community | Ya | **Prioritas TERTINGGI Step 2** — modul ini patch banyak komponen inti `mail`/`discuss` (`Message`, `Chatter`, `MessageCardList`, `messageActionsRegistry`, `message_pin` service) — area paling rawan breaking change 17→18 dari ketiga modul project ini |

Tidak ada indikasi Enterprise/OCA (dikonfirmasi dev, berlaku project-wide).

## 2b. Struktur & Fitur Modul (auto-scan)

| Fitur | Ada di modul? | Lokasi/bukti | Fase step 6 relevan |
|---|---|---|---|
| Controllers | ☐ Tidak ada sama sekali (bahkan tidak ada file scaffold dead seperti 2 modul lain) | — | D1 — N/A |
| Assets/CSS/JS custom | ☑ Ya, PALING BANYAK dari ketiga modul | `static/src/js/{chatter,message,pinMessage}.js`, `static/src/xml/{pinnedMessages,message_card_list}.xml`, `static/src/css/style.css` — semua di `assets.web.assets_backend` | D2, E, F — **prioritas tertinggi, area paling kritis** |
| Komponen Owl/JS custom | ☑ Ya (patch + `t-inherit` template, bukan komponen baru) | `patch(Message.prototype, ...)`, `patch(Chatter.prototype, ...)`, `messageActionsRegistry.add(...)`, `t-inherit="mail.Chatter"`/`t-inherit="mail.Message"`/`t-inherit="mail.MessageCardList"` | E, F — **wajib cek versi terbaru `@mail/core/common/message`, `@mail/core/web/chatter`, `@mail/core/common/message_actions`, `@mail/core/common/message_card_list` di 18.0 — import path/nama export ini historically berubah antar versi Odoo mail module** |
| Field JSON/relasi berantai/dynamic model | ☐ Tidak | | B2 — N/A |
| View dinamis (`invisible=`/`attrs=`) | ☐ Tidak ada view XML sama sekali (`data: []` di manifest) — semua UI lewat template Owl (`t-inherit` QWeb JS component, bukan `ir.ui.view`) | | C2 — N/A (tapi lihat catatan Owl di atas, ranahnya beda) |

**Catatan tambahan hasil baca langsung:**
- Ada **DUA jalur pin terpisah** yang keduanya berujung ke RPC `toggle_pin` yang sama: (1) action registry `"pins"` (`pinMessage.js` → `onClickPin()`), dan (2) tombol pin inline di `pinnedMessages.xml` (langsung panggil `onMessagePin(id)` — method terpisah, TIDAK ada percabangan `is_discussion` seperti `onClickPin`, tapi kondisi tampil tombolnya di XML sudah membatasi cuma untuk non-discussion). Bukan bug (behavior akhirnya konsisten), tapi dua entry point terpisah untuk fungsi yang sama — dicatat sebagai detail baseline (`BSL-006` di `01b_BASELINE_SPEC.md`), tidak perlu jadi finding terpisah.
- Tidak ada `security/ir.model.access.csv` — dikonfirmasi bukan gap (lihat "Ringkasan" poin 5).

## 3. Sifat Migrasi

- [x] Port kode saja
- [ ] Upgrade instance

## 4. Baseline Spec (gate)

- [x] `FUNCTIONAL_SPEC.md` lama: `doc-dev/backfill/spec/pin_message/01A_FUNCTIONAL_SPEC.md` + `01B_ACCEPTANCE_CRITERIA.md` — semua BR-01..BR-04 `[MATCH]` setelah cross-check kode aktual.
- [x] `01b_BASELINE_SPEC.md` sudah diisi.

### 4a. Dokumen Pelengkap Lain
- [x] Dikonfirmasi tidak ada (jawaban dev berlaku project-wide).

## 4b. Source Aktif Dikembangkan?
- [x] Tidak (jawaban dev berlaku project-wide).

## 5. Scope Boundary

- Tetap identik: BR-01..BR-04, termasuk 2 quirk diwarisi (`MF-09`/`MF-10`).
- Diubah/di-drop: belum ada — TAPI beda dari 2 modul margin, modul ini punya kemungkinan CUKUP BESAR butuh perubahan teknis wajib di Step 6 (import path Owl/JS `mail` module kemungkinan berubah total di 18.0) — itu tetap "port kode", bukan perubahan scope, tapi perlu dicatat eksplisit di `03_MIGRATION_SPEC.md` sebagai risiko implementasi tertinggi project ini.

## 6. Constraint

- Deadline: **[BELUM DIJAWAB]**
- Owner: **[BELUM DIJAWAB]**
