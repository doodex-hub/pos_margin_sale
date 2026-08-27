# Migration Acceptance Criteria — pin_message

**Step:** 5 — Acceptance Criteria & Test Plan
**Ref:** `01_intake/pin_message/01b_BASELINE_SPEC.md` dan kode 18.0 yang berjalan
**Tanggal:** 2026-08-26

---

## AC-01 — Toggle Pin (server-side)

**AC-01-01** (verifies `BSL-001`, `BSL-005`)
Given satu atau lebih pesan chatter (log note)
When `toggle_pin()` dipanggil (multi-record)
Then `is_pinned` FLIP untuk SETIAP pesan di recordset, broadcast bus per-message — tidak ada side
effect lain.

## AC-02 — Pin via Action-Menu (`pinMessage.js`) — **area kritis `MF-15`**

**AC-02-01** (verifies `BSL-004`, `BSL-010`)
Given pesan log note (bukan discussion, bukan `user_notification`/`auto_comment`/`notification`,
bukan changelog)
When hover pesan, buka action-menu "..."
Then entry "Pin" MUNCUL (sequence 15), dengan label benar dan ikon `fa-thumb-tack`. **Setelah fix
`DIFF-02` (`MF-15`)** — sebelum fix, ini akan CRASH (getter `condition` throw), bukan cuma
"entry tidak muncul".

**AC-02-02** (verifies `BSL-004`)
Given entry "Pin" muncul di action-menu
When user klik entry tersebut
Then `toggle_pin()` terpanggil via `onClickPin()`, pesan ter-toggle pin, badge "Pinned Messages"
ter-update. **Setelah fix `DIFF-02`** — `onClick` diganti `onSelected`, harus benar-benar terpanggil.

**AC-02-03** (verifies `BSL-004`, negative)
Given pesan tipe `user_notification`/`auto_comment`/`notification`, atau changelog message
When action-menu dibuka
Then entry "Pin" TIDAK MUNCUL.

## AC-03 — Pin via Tombol Inline (`pinnedMessages.xml`)

**AC-03-01** (verifies `BSL-003`, `BSL-011`)
Given pesan log note ditampilkan di chatter
When user klik tombol pin inline (ikon `fa-thumb-tack`/`fa-thumb-tack-o`)
Then `onMessagePin()` terpanggil, `toggle_pin()` RPC, ikon toggle warna (primary saat pinned).

## AC-04 — Section "Pinned Messages"

**AC-04-01** (verifies `BSL-008`)
Given ada 1+ pesan ter-pin di thread
When chatter dimuat (mount atau ganti thread)
Then `initialLoad()` fetch pesan ber-`is_pinned=True` untuk thread ini, badge menampilkan jumlah,
section collapsible menampilkan `MessageCardList` (urut `date DESC`) saat di-expand.

**AC-04-02** (verifies `BSL-006`) — **area kritis `MF-14`**
Given pesan APAPUN (bukan cuma yang pinned) di-load ke chatter
When `mail.message._to_store()` dipanggil (via `store.add()`)
Then TIDAK ADA error — field `is_pinned` ikut terkirim ke frontend untuk semua pesan. **Setelah fix
`DIFF-01`** — sebelum fix, `TypeError` di titik ini akan mematahkan LOADING CHATTER APAPUN, bukan
cuma section pinned messages.

## AC-05 — Discuss-Channel Native Pin (jalur terpisah, dead code modul ini)

**AC-05-01** (verifies `BSL-002`, `BSL-013`)
Given pesan di Discuss channel
When user pin/unpin via mekanisme native (bukan lewat modul ini)
Then pin/unpin berfungsi penuh lewat native `mail`, TIDAK terganggu oleh cabang `is_discussion` di
`onClickPin()` modul ini (dead code, tidak pernah tercapai — dikonfirmasi ulang Step 2, sama di
18.0 dan 19.0).

## AC-06 — Reload Round-Trip

**AC-06-01** (verifies `BSL-008`)
Given user pindah dari thread A ke thread B lalu kembali ke A
When chatter reload
Then tidak ada state bocor — status pin tiap pesan tetap akurat sesuai server, tidak tercampur
antar thread.

---

**Ringkasan traceability:** 10 AC, mencakup semua `BSL-001` s.d. `BSL-014`. `AC-02-01`/`02` dan
`AC-04-02` adalah AC PALING KRITIS di seluruh project — keduanya secara langsung memverifikasi fix
`MF-14`/`MF-15` yang, kalau gagal, akan menunjukkan kegagalan JAUH LEBIH LUAS dari fitur pin itu
sendiri (chatter/action-menu pesan APAPUN).
