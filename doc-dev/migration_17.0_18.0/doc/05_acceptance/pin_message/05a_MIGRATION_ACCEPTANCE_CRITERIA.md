# Migration Acceptance Criteria — pin_message

**Step:** 5 — Acceptance Criteria & Test Plan
**Ref:** `01_intake/pin_message/01b_BASELINE_SPEC.md` dan kode 17.0 — bukan `03_MIGRATION_SPEC.md`
**Tanggal:** 2026-08-24

---

## AC-01 — Toggle pin log note

**AC-01-01** (verifies `BSL-001`)
Given log note (bukan discussion) di chatter, `is_pinned = False`
When user klik ikon pin
Then RPC `toggle_pin` dipanggil, `is_pinned = True`, pesan muncul di section "Pinned Messages" realtime tanpa refresh.

**AC-01-02** (verifies `BSL-001`)
Given `is_pinned = True`
When user klik pin lagi
Then `is_pinned = False`, hilang dari section.

## AC-02 — Tidak ada duplikasi tombol pin discuss vs chatter — TERKAIT `DIFF-01/02/03`

**AC-02-01** (verifies `BSL-003`)
Given pesan di thread `discuss.channel`
When message actions menu dirender
Then action native `"pin"` tampil, action custom `"pins"` TIDAK tampil — **membuktikan xpath `DIFF-01/02` tidak merusak kondisi `is_discussion`**.

**AC-02-02** (verifies `BSL-003`)
Given pesan log note di chatter biasa
When menu dirender
Then action `"pins"` tampil, `"pin"` native tidak.

## AC-03 — Pin pesan Discuss channel (jalur delegasi core) — RISIKO TERTINGGI `DIFF-06`

**AC-03-01 — WAJIB dites eksplisit, TIDAK BOLEH diasumsikan dari AC-01/02** (verifies `BSL-002`, `MF-09`)
Given pesan di `discuss.channel`, belum pinned
When user klik pin (lewat action native `"pin"`, memicu `onClickPin()` override modul ini)
Then dialog konfirmasi core muncul, pin berhasil — **kalau `TypeError: this.messagePinService is undefined` muncul, ini KONFIRMASI `DIFF-06` (`MF-09` bermanifestasi nyata di 18.0) — WAJIB dieskalasi ke user sebelum lanjut, bukan diam-diam dibiarkan gagal.**

## AC-04 — Section Pinned Messages

**AC-04-01** (verifies `BSL-007`)
Given thread punya 3 pesan `is_pinned=True`
When chatter mount
Then badge `3`, expand tampilkan `MessageCardList` diurutkan `date DESC`.

**AC-04-02** (verifies `BSL-007`)
Given user pindah record A→B
When props chatter berubah (`threadId`/`threadModel`)
Then `initialLoad()` refresh sesuai thread B.

## AC-05 — Entry point kedua (tombol pin inline di bubble message)

**AC-05-01** (verifies `BSL-006`)
Given pesan log note (non-discussion)
When user klik tombol pin inline (bukan lewat action menu)
Then `toggle_pin` RPC terpanggil sama seperti AC-01-01 (dua entry point, satu jalur logic efektif — hasil akhir harus identik).
