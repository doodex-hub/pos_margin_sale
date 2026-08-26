# UAT Checklist — Migrasi pin_message

**Step:** 11 — UAT Sign-off (final)
**Ref:** `05_acceptance/pin_message/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `10_qa/pin_message/10_BUSINESS_FLOW_MIGRATION.md`
**Tanggal:** 2026-08-26

> Kriteria sukses: user TIDAK merasakan bedanya pin/unpin pesan (baik di chatter record biasa maupun di Discuss) dibanding sebelum migrasi.
>
> **Dokumen ini draft test script — WAJIB dijalankan sendiri oleh user/stakeholder**, bukan laporan AI. Kolom **Actual** dan **Status** DIBIARKAN KOSONG — isi sendiri.

---

## Persiapan Sebelum UAT

- [ ] Modul `pin_message` versi 18.0 terinstall di database staging.
- [ ] Login sebagai user biasa (bukan cuma Administrator) untuk validasi hak akses standar.
- [ ] Ada minimal 1 record dengan chatter (kontak/customer apapun) dan 1 channel Discuss untuk dipakai testing.

## Skenario Test (Test Script)

### T-01: Pin/unpin log note lewat tombol inline

**Data dummy yang perlu dientri:** Buka kontak apapun (mis. pelanggan "PT Contoh Sejahtera"). Tulis log note dengan teks: "Follow up pembayaran invoice #123".

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka kontak, klik "Log note", tulis pesan, kirim | Pesan muncul di riwayat chatter | | [ ] Pass [ ] Fail |
| 2 | Arahkan mouse ke pesan itu, klik ikon pin (thumbtack) di sebelah nama pengirim | Pesan langsung ter-pin, badge "Pinned Messages" muncul dengan angka 1, TANPA perlu refresh halaman | | [ ] Pass [ ] Fail |
| 3 | Klik ikon pin yang sama lagi | Pesan ter-unpin, section "Pinned Messages" hilang/kembali kosong | | [ ] Pass [ ] Fail |

### T-02: Pin/unpin log note lewat menu aksi ("...")

**Data dummy yang perlu dientri:** Sama seperti T-01, atau pesan baru di record yang sama.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Tulis log note baru, arahkan mouse ke pesan, klik ikon titik-tiga ("...") | Muncul menu berisi opsi "Pin" (custom, khusus modul ini) | | [ ] Pass [ ] Fail |
| 2 | Klik "Pin" di menu itu | Pesan ter-pin, badge "Pinned Messages" bertambah | | [ ] Pass [ ] Fail |

### T-03: Pin/unpin pesan di Discuss channel

**Data dummy yang perlu dientri:** Buka Discuss, channel apapun (mis. #general). Kirim pesan: "Meeting jam 2 siang di ruang rapat A".

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Kirim pesan di channel, arahkan mouse ke pesan, klik "..." | Menu HANYA berisi "Pin" (native Odoo) — pastikan TIDAK ada entry pin lain yang aneh/dobel | | [ ] Pass [ ] Fail |
| 2 | Klik "Pin" | Muncul jendela konfirmasi, klik "Yeah, pin it!" | | [ ] Pass [ ] Fail |
| 3 | Klik ikon thumbtack di header channel (buka panel "Pinned Messages") | Pesan tadi muncul di panel | | [ ] Pass [ ] Fail |
| 4 | Klik ikon silang (X) pada pesan di panel itu, konfirmasi hapus | Pesan hilang dari panel, panel kembali kosong | | [ ] Pass [ ] Fail |

### T-04: Ganti record — pastikan data pin tidak "bocor" ke record lain

**Data dummy yang perlu dientri:** Butuh 2 kontak berbeda — kontak A (yang sudah dipakai T-01, punya pesan pinned) dan kontak B (kontak lain, belum pernah ada pesan).

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Dari kontak A (masih ada pesan pinned), pindah ke kontak B | Kontak B TIDAK menampilkan section "Pinned Messages" apapun | | [ ] Pass [ ] Fail |
| 2 | Kembali ke kontak A | Badge "Pinned Messages" di kontak A masih benar seperti semula | | [ ] Pass [ ] Fail |

### T-XX: Item yang TIDAK Bisa Dites Lewat Tampilan Biasa (Informasi, Bukan Kegagalan)

- Tidak ada — semua fitur modul ini reachable dari chatter/Discuss biasa.

## Sign-off per Kelompok Fitur

| # | Kelompok fitur | Skenario tercakup | Status | Catatan |
|---|---|---|---|---|
| 1 | Pin/unpin log note (dua entry point) | T-01, T-02 | [ ] Pass [ ] Fail | |
| 2 | Pin/unpin Discuss channel | T-03 | [ ] Pass [ ] Fail | |
| 3 | Konsistensi antar-record | T-04 | [ ] Pass [ ] Fail | |

## Review Item Out-of-Scope

Stakeholder mengonfirmasi sadar & menerima:

- `console.log` debug tertinggal di kode (tidak berdampak fungsional, cuma noise di console browser developer) — sengaja dipertahankan, bukan bug baru.
- Jalur klik pin dari Discuss channel sekarang 100% ditangani Odoo core (bukan lagi kode custom modul ini) — hasil akhir untuk pengguna tetap sama persis, cuma mekanisme internalnya berubah karena Odoo 18 merestrukturisasi fitur pin-nya sendiri.

## Prasyarat Sebelum Go-Live Produksi

- [ ] Backup database produksi sebelum deploy versi 18.0.

## Sign-off

| Role | Nama | Tanggal | Tanda tangan |
|---|---|---|---|
| PM | | | |
| FA | | | |
| User | | | |

> Kosongkan sampai stakeholder benar-benar menjalankan skenario T-01 dst. dengan tangan sendiri dan menyetujui.
