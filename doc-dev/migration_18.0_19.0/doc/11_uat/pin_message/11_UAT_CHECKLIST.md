# UAT Checklist — Migrasi pin_message

**Step:** 11 — UAT Sign-off (final)
**Ref:** `05_acceptance/pin_message/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`,
`10_qa/pin_message/10_BUSINESS_FLOW_MIGRATION.md`
**Tanggal:** 2026-08-27

> Kriteria sukses: user TIDAK merasakan bedanya dibanding versi 18.0. Modul ini sempat berisiko
> TINGGI selama migrasi (server sempat error setiap chatter dibuka sama sekali, sudah diperbaiki
> dan diverifikasi 4 lapis independen) — UAT di sini jadi lapis verifikasi terakhir sebelum
> go-live.
>
> **Dokumen ini test script untuk DIJALANKAN SENDIRI oleh business user/stakeholder** — kolom
> Actual/Status di bawah SENGAJA dikosongkan.

---

## Persiapan Sebelum UAT (Precondition & Data)

- [ ] Modul `pin_message` versi 19.0 sudah terinstall di environment staging.
- [ ] Login sebagai user biasa (bukan cuma Administrator).
- [ ] Ada minimal 1 record apapun yang punya chatter (log note) — contoh: buka record Contact
  (`res.partner`) apapun, atau Sales Order apapun.
- [ ] **Sanity check paling penting sebelum lanjut ke skenario di bawah:** buka chatter di
  BEBERAPA jenis halaman berbeda (Contact, Sales Order, Discuss) — pastikan SEMUA bisa dibuka
  normal tanpa error/loading macet. Kalau ada satu saja yang error/macet, STOP, laporkan ke tim
  teknis sebelum lanjut (ini indikasi masalah serius yang mempengaruhi seluruh sistem, bukan cuma
  fitur pin).

## Skenario Test (Test Script)

### T-01: Pin pesan lewat menu titik tiga (action-menu)

**Data dummy yang perlu dientri:** ketik pesan log "Test UAT pin message" di chatter record Contact
apapun.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka record Contact, tulis pesan "Test UAT pin message" di kotak log note, kirim | Pesan muncul di chatter | | [ ] Pass [ ] Fail |
| 2 | Arahkan mouse ke pesan tadi, klik ikon titik tiga (menu aksi) | Menu muncul, ada opsi "Pin" | | [ ] Pass [ ] Fail |
| 3 | Klik "Pin" | Pesan ter-pin (ikon pin/jarum muncul di pesan), badge "Pinned Messages" bertambah | | [ ] Pass [ ] Fail |

### T-02: Pin pesan lewat tombol pin langsung (inline)

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Kirim pesan log baru | Pesan muncul di chatter | | [ ] Pass [ ] Fail |
| 2 | Hover pesan, klik ikon jarum pin langsung (bukan lewat menu titik tiga) | Pesan langsung ter-pin, ikon berubah warna | | [ ] Pass [ ] Fail |
| 3 | Klik lagi ikon yang sama | Pesan ter-unpin, ikon kembali normal | | [ ] Pass [ ] Fail |

### T-03: Lihat daftar pesan yang di-pin

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Pin 2 pesan berbeda di record yang sama | Kedua pesan ter-pin | | [ ] Pass [ ] Fail |
| 2 | Klik badge/section "Pinned Messages" di chatter | Panel terbuka menampilkan kedua pesan, urut dari yang terbaru | | [ ] Pass [ ] Fail |

### T-04: Pin pesan di Discuss (chat internal), bukan cuma chatter record

**Data dummy yang perlu dientri:** kirim pesan "Test UAT Discuss pin" di channel Discuss apapun.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka Discuss, kirim pesan "Test UAT Discuss pin" di channel apapun | Pesan terkirim | | [ ] Pass [ ] Fail |
| 2 | Pin pesan tersebut (hover > menu, atau tombol pin) | Pesan ter-pin, tidak ada error muncul | | [ ] Pass [ ] Fail |
| 3 | Pindah ke channel lain lalu kembali lagi | Status pin pesan tadi masih sama (tidak hilang/berubah) | | [ ] Pass [ ] Fail |

## Sign-off per Kelompok Fitur

| # | Kelompok fitur | Skenario tercakup | Status | Catatan |
|---|---|---|---|---|
| 1 | Chatter bisa dibuka di semua jenis halaman (sanity check) | Precondition | [ ] Pass [ ] Fail | **Paling kritis — kalau Fail, STOP dan eskalasi** |
| 2 | Pin via menu aksi | T-01 | [ ] Pass [ ] Fail | |
| 3 | Pin via tombol inline | T-02 | [ ] Pass [ ] Fail | |
| 4 | Daftar Pinned Messages | T-03 | [ ] Pass [ ] Fail | |
| 5 | Pin di Discuss + reload round-trip | T-04 | [ ] Pass [ ] Fail | |

## Review Item Out-of-Scope

Tidak ada item out-of-scope untuk modul ini — migrasi murni port kode + perbaikan bug kompatibilitas
19.0 (fix `_to_store()` dan `messageActionsRegistry`, keduanya WAJIB agar modul jalan sama sekali di
19.0, bukan perubahan fitur/behavior yang disengaja).

## Prasyarat Sebelum Go-Live Produksi

- [ ] Rehearsal upgrade sungguhan — **belum dilakukan di project ini** (Step 7 N/A, port kode
  saja). WAJIB dilakukan terpisah kalau modul ini akan dipasang di atas database produksi 18.0
  yang sudah berisi data nyata (terutama karena modul ini pernah berisiko mematahkan chatter
  APAPUN — pastikan rehearsal mencakup pembukaan chatter di berbagai jenis halaman produksi nyata,
  bukan cuma data dummy staging).
- [ ] Backup database produksi sebelum upgrade nyata.

## Sign-off

| Role | Nama | Tanggal | Tanda tangan |
|---|---|---|---|
| PM | | | |
| FA | | | |
| User | | | |

> Kosongkan sampai stakeholder benar-benar menjalankan skenario T-01 dst. dengan tangan sendiri dan
> menyetujui.
