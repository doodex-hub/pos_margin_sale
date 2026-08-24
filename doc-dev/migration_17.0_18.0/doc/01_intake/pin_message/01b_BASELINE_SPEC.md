# Baseline Spec — pin_message

**Step:** 1 — Intake & Scope (pelengkap `01a_MIGRATION_INTAKE.md`)
**Tujuan:** dokumentasikan behavior as-is modul ini di 17.0.
**Tanggal:** 2026-08-24
**Sumber:** Direkonsiliasi dari `doc-dev/backfill/spec/pin_message/01A_FUNCTIONAL_SPEC.md` + `01B_ACCEPTANCE_CRITERIA.md` (2026-07-31) + cross-check kode aktual sesi ini (tidak ada penyimpangan — satu-satunya commit setelah backfill spec, `313cef5`, cuma ubah path gambar banner)

---

## Ringkasan untuk Review — Perlu Konfirmasi User

**Tally:** 7 klaim `[MATCH]`, 1 klaim `[NO-SPEC]` (detail tambahan ditemukan sesi ini).

1. `[BSL-002]` `[PERLU-KEPUTUSAN]` `[DIWARISI-SOURCE]` — patch JS `Message.prototype.onClickPin` MENIMPA TOTAL (bukan extend via `super()`) patch core `discuss/message_pin`. Diwarisi `MF-09`/backfill `F-06`. **Risiko migrasi PALING TINGGI di modul ini** — kalau core Odoo 18.0 mengubah behavior `onClickPin` (bukan cuma lokasi file), override total ini tidak akan otomatis mengikuti perubahan itu.
2. `[BSL-005]` `[PERLU-KEPUTUSAN]` `[DIWARISI-SOURCE]` — `console.log(component.message.type)` debug tertinggal di `pinMessage.js`, dieksekusi tiap render action menu pesan. Diwarisi `MF-10`/backfill `F-07`.
3. Sisanya (`BSL-001`, `BSL-003`, `BSL-004`, `BSL-006`, `BSL-007`) `[MATCH]`, sudah cocok dengan kode aktual.

---

## 1. Tujuan Modul

Modul ini menambahkan kemampuan pin (menyematkan) pesan/log note penting di chatter model APAPUN (Sale Order, Partner, dst — chatter generik, bukan Discuss channel) — pesan yang di-pin selalu terlihat di section "Pinned Messages" collapsible di atas chatter, terpisah dari mekanisme pin native Odoo untuk `discuss.channel`.

## 2. Model & Tanggung Jawab

| Model | Tanggung Jawab |
|---|---|
| `mail.message` (extend) | Field `is_pinned` + method `toggle_pin()` (broadcast realtime via `bus.bus`) |

Tidak ada model/wizard baru — seluruh UI lewat patch komponen Owl JS milik `mail`, bukan `ir.ui.view`.

## 3. Field dengan Makna Bisnis

### `mail.message`
- `is_pinned` (Boolean, `default=False`, `index=True`) — status pin pesan, berlaku untuk chatter model apapun (bukan Discuss channel).

## 4. Business Workflow / State Transition

- `[BSL-001]` `[MATCH]` (ref: BR-01, AC-01-01, AC-01-02) `toggle_pin()` — flip `is_pinned`, broadcast `bus.bus._sendone` per pesan (`{id, is_pinned}`) supaya UI update realtime tanpa refresh. Method di-loop per record (`for message in self:`), aman untuk multi-record.
- `[BSL-002]` `[MATCH]` `[PERLU-KEPUTUSAN]` `[DIWARISI-SOURCE]` (ref: BR-02, AC-03-01, **backfill F-06**) `onClickPin()` (patch `Message.prototype`, `static/src/js/message.js`) bercabang berdasar `message.is_discussion`:
  - **True** (pesan Discuss channel) → delegasi ke `messagePinService.pin()`/`.unpin()` (menampilkan dialog konfirmasi native core) — TAPI ini REIMPLEMENTASI manual logic yang sama dengan core `message_patch.js`, method-nya MENIMPA TOTAL (tidak pernah panggil `super.onClickPin()`).
  - **False** (log note/chatter biasa) → RPC `mail.message.toggle_pin` langsung, tanpa dialog konfirmasi.
- `[BSL-003]` `[MATCH]` (ref: BR-03, AC-02-01, AC-02-02) Action tombol "pins" (registry `messageActionsRegistry`, sequence 15) tampil HANYA untuk pesan non-discussion, bukan `user_notification`/`auto_comment`/`notification`, dan tidak punya `subtype_description` (bukan changelog). Native action `"pin"` (sequence 65, punya core) dan action `"pins"` modul ini TIDAK PERNAH tampil bersamaan pada pesan yang sama (domain kondisinya saling eksklusif: discuss channel vs bukan).

## 5. Server-Side Logic dengan Side Effect

- `[BSL-004]` `[MATCH]` (ref: BR-01) `toggle_pin()` — lihat `[BSL-001]`, tidak ada side effect lain selain broadcast bus.

## 6. Client-Side Behavior (Views, JS, Owl)

- `[BSL-005]` `[MATCH]` `[PERLU-KEPUTUSAN]` `[DIWARISI-SOURCE]` (ref: **backfill F-07**) `console.log(component.message.type)` di baris pertama `condition` callback `pinMessage.js` — dieksekusi SETIAP KALI action registry menge-render tombol aksi pesan (berpotensi banyak sekali panggilan di chatter dengan banyak pesan). Debug leftover, bukan bug fungsional.
- `[BSL-006]` `[NO-SPEC]` (detail tambahan, ditemukan baca kode langsung — backfill spec menyebut naratif "tombol pin langsung di bubble message" tapi tidak merinci ini jalur KEDUA yang terpisah dari action registry) `pinnedMessages.xml` me-render tombol pin tambahan langsung di sebelah nama author pesan (`t-inherit="mail.Message"`), memanggil `onMessagePin(props.message.id)` — method TERPISAH dari `onClickPin()`, TIDAK punya percabangan `is_discussion` (selalu langsung RPC `toggle_pin`, tanpa dialog konfirmasi). **Behavior akhir tetap konsisten** karena kondisi tampil tombol ini (`!props.message.is_discussion` dkk, baris 37 XML) sudah membatasi cuma untuk domain non-discussion yang sama dengan action registry `"pins"` — jadi dua entry point UI, satu jalur logic efektif.
- `[BSL-007]` `[MATCH]` (ref: BR-04, AC-04-01, AC-04-02) `Chatter.initialLoad()` (patch `onMounted` + `onWillUpdateProps` saat `threadId`/`threadModel` berubah) — fetch `mail.message` dengan domain `is_pinned=True` + thread yang sedang dibuka, tandai `is_pinned` di message object lokal yang sudah ter-load di state thread. Section "Pinned Messages" (`pinnedMessages.xml`) tampilkan badge jumlah (kalau collapsed) atau `MessageCardList` (kalau expanded), diurutkan `date DESC`.

## 7. Dependency Eksternal

### Eksplisit (manifest)
`depends: ['web', 'base', 'mail']` — semua Native Community.

### Implisit/Inferred — INI YANG PALING BERISIKO DI PROJECT INI
- `@mail/core/common/message` (`Message` class/component)
- `@mail/core/web/chatter` (`Chatter` class/component)
- `@mail/core/common/message_card_list` (`MessageCardList` component)
- `@mail/core/common/message_actions` (`messageActionsRegistry`)
- `this.messagePinService` (service internal `mail` module untuk pin Discuss channel, dipanggil tanpa `depends`/import eksplisit — diakses via `this` di context Owl component, hanya ada karena `Message` component core sudah inject service ini)
- Selector CSS/QWeb xpath: `o-mail-Chatter-topbar`, `o-mail-Message-author`, `o-mail-MessageCard-jump` — kelas CSS/struktur DOM spesifik yang bisa berubah nama/struktur di refactor UI.

**Semua titik di atas adalah import path/nama export/struktur DOM dari MODUL INTI `mail` Odoo** — historically salah satu area yang paling sering direstruktur signifikan antar versi mayor (arsitektur OWL Discuss/Chatter). **Prioritas riset #1 Step 2**, termasuk baca `migration-tool/knowledge/version-diffs/17-to-18.md` untuk area `mail`/`discuss` secara spesifik kalau sudah ada entrinya.

## 8. Quirk / Behavior Non-Obvious

- `[BSL-002]` (lihat §4) — full-override `onClickPin`, `MF-09`.
- `[BSL-005]` (lihat §6) — `console.log` debug leftover, `MF-10`.
- `[BSL-006]` (lihat §6) — dua entry point UI untuk pin, satu jalur logic efektif — bukan bug, dicatat supaya Step 6 tahu ada 2 tempat yang perlu dipastikan tetap konsisten kalau salah satu diubah.
- Tidak ada `security/ir.model.access.csv` di modul ini — dikonfirmasi bukan gap (field+method ditambahkan ke model yang sudah py punya access rule dari core `mail`).

---

## Cara Pakai

ID `BSL-NNN` modul ini independen (mulai dari 001).
