# Acceptance Criteria — pin_message

**Module:** `pin_message`
**Ref:** `01A_FUNCTIONAL_SPEC.md`
**Last Updated:** 2026-07-31
**Status:** Backfill retroaktif

---

## AC-01 — Toggle pin log note

**AC-01-01** — ref `BR-01` `[HASIL-BACA]`
Given sebuah log note (bukan discussion) di chatter Sale Order, `is_pinned = False`
When user klik ikon pin di pesan itu
Then RPC `toggle_pin` dipanggil, `is_pinned` jadi `True`, pesan langsung muncul di section "Pinned
Messages" (via realtime bus, tanpa perlu refresh halaman).

**AC-01-02** — ref `BR-01` `[HASIL-BACA]`
Given pesan sudah `is_pinned = True`
When user klik ikon pin lagi
Then `is_pinned` jadi `False`, pesan hilang dari section "Pinned Messages".

---

## AC-02 — Tidak ada duplikasi tombol pin discuss vs chatter

**AC-02-01** — ref `BR-03` `[HASIL-BACA]`
Given pesan ada di thread `discuss.channel` (percakapan Discuss, bukan chatter record)
When message actions menu dirender
Then action native core `"pin"` (sequence 65) tampil; action custom modul ini `"pins"` TIDAK
tampil (`isNote` di kondisinya jadi `False` karena `is_discussion=True`) — tidak ada duplikat.

**AC-02-02** — ref `BR-03` `[HASIL-BACA]`
Given pesan adalah log note di chatter record biasa (`sale.order`, `res.partner`, dst)
When message actions menu dirender
Then action custom `"pins"` tampil; action native core `"pin"` TIDAK tampil (`thread.model !==
'discuss.channel'` di kondisi core).

---

## AC-03 — Pin pesan discussion (jalur delegasi ke core)

**AC-03-01** — ref `BR-02` `[PERLU-KEPUTUSAN]`
Given pesan ada di `discuss.channel`, belum pinned
When user memicu `onClickPin()` (lewat action `"pin"` core, bukan `"pins"` modul ini — lihat AC-02-01)
Then (SEKARANG, dikonfirmasi identik dengan implementasi core) `messagePinService.pin()` dipanggil,
dialog konfirmasi "You sure want this message pinned..." muncul — TAPI method yang benar-benar
dieksekusi adalah override modul ini (menimpa core), bukan core langsung. Lihat **F-06** — perlu
keputusan pemilik modul apakah override ini sebaiknya diubah jadi `super.onClickPin()` untuk
robustness ke depan (tidak mengubah perilaku SAAT INI).

---

## AC-04 — Section Pinned Messages

**AC-04-01** — ref `BR-04` `[HASIL-BACA]`
Given thread punya 3 pesan `is_pinned=True`
When chatter di-mount
Then badge collapsed menunjukkan angka `3`; expand menampilkan `MessageCardList` ketiga pesan,
diurutkan `date DESC`.

**AC-04-02** — ref `BR-04` `[HASIL-BACA]`
Given user pindah dari record A ke record B (ganti `threadId`/`threadModel`, mis. navigasi antar
Sale Order)
When props chatter berubah
Then `initialLoad()` dipanggil ulang, pinned messages di-refresh sesuai thread B (bukan sisa
data thread A).
