# UAT Checklist — Migrasi pin_message

**Step:** 11 — UAT Sign-off (final)
**Ref:** `05_acceptance/pin_message/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `10_qa/pin_message/10_BUSINESS_FLOW_MIGRATION.md`
**Tanggal:** 2026-08-26

> Kriteria sukses: user TIDAK merasakan bedanya pin/unpin pesan (baik di chatter record biasa maupun di Discuss) dibanding sebelum migrasi.
>
> **PENYIMPANGAN DARI PRAKTIK STANDAR (dicatat eksplisit, bukan disembunyikan):** dokumen ini awalnya dirancang sebagai test script yang WAJIB dijalankan tangan sendiri oleh user/stakeholder. **User (kuncoro@doodex.net) secara eksplisit memutuskan (chat, 2026-08-26): "UAT dianggap selesai, percaya AI test"** — yaitu menerima bukti pengujian AI dari Step 9 (Tour test otomatis) dan Step 10 (interaksi Chrome asli) sebagai pengganti eksekusi manual T-01 dst. Kolom Actual/Status di bawah diisi AI, MENGUTIP sumber bukti Step 9/10 yang sudah ada (bukan klik ulang), sesuai instruksi eksplisit tersebut.

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
| 1 | Buka kontak, klik "Log note", tulis pesan, kirim | Pesan muncul di riwayat chatter | Tour test otomatis `test_pin_message_toggle_pin_tour` (Step 9, Chrome asli headless) — sukses | [x] Pass [ ] Fail |
| 2 | Arahkan mouse ke pesan itu, klik ikon pin (thumbtack) di sebelah nama pengirim | Pesan langsung ter-pin, badge "Pinned Messages" muncul dengan angka 1, TANPA perlu refresh halaman | Tour mengonfirmasi badge "Pinned Messages" muncul dengan angka 1 setelah klik tombol inline | [x] Pass [ ] Fail |
| 3 | Klik ikon pin yang sama lagi | Pesan ter-unpin, section "Pinned Messages" hilang/kembali kosong | Tour mengonfirmasi section hilang total setelah unpin | [x] Pass [ ] Fail |

### T-02: Pin/unpin log note lewat menu aksi ("...")

**Data dummy yang perlu dientri:** Sama seperti T-01, atau pesan baru di record yang sama.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Tulis log note baru, arahkan mouse ke pesan, klik ikon titik-tiga ("...") | Muncul menu berisi opsi "Pin" (custom, khusus modul ini) | Tour test otomatis `test_pin_message_action_menu_pin_visible_tour` (Step 9) — dibuat khusus membuktikan fix bug `MF-24` (entry ini sempat mati total di 18.0, sudah diperbaiki) | [x] Pass [ ] Fail |
| 2 | Klik "Pin" di menu itu | Pesan ter-pin, badge "Pinned Messages" bertambah | Tour mengonfirmasi badge jadi 1 setelah klik entry ini | [x] Pass [ ] Fail |

### T-03: Pin/unpin pesan di Discuss channel

**Data dummy yang perlu dientri:** Buka Discuss, channel apapun (mis. #general). Kirim pesan: "Meeting jam 2 siang di ruang rapat A".

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Kirim pesan di channel, arahkan mouse ke pesan, klik "..." | Menu HANYA berisi "Pin" (native Odoo) — pastikan TIDAK ada entry pin lain yang aneh/dobel | Step 10 (S-01, Chrome asli): menu "..." dikonfirmasi hanya berisi Pin, Mark as Unread, Create Thread, Edit, Delete, Copy Link — tidak ada entry dobel | [x] Pass [ ] Fail |
| 2 | Klik "Pin" | Muncul jendela konfirmasi, klik "Yeah, pin it!" | Step 10: dialog "Pin It" muncul dan berfungsi | [x] Pass [ ] Fail |
| 3 | Klik ikon thumbtack di header channel (buka panel "Pinned Messages") | Pesan tadi muncul di panel | Step 10: panel "PINNED MESSAGES" menampilkan pesan dengan benar | [x] Pass [ ] Fail |
| 4 | Klik ikon silang (X) pada pesan di panel itu, konfirmasi hapus | Pesan hilang dari panel, panel kembali kosong | Step 10: dialog "Unpin Message" muncul dan berfungsi, panel kembali ke "This channel doesn't have any pinned messages." | [x] Pass [ ] Fail |

### T-04: Ganti record — pastikan data pin tidak "bocor" ke record lain

**Data dummy yang perlu dientri:** Butuh 2 kontak berbeda — kontak A (yang sudah dipakai T-01, punya pesan pinned) dan kontak B (kontak lain, belum pernah ada pesan).

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Dari kontak A (masih ada pesan pinned), pindah ke kontak B | Kontak B TIDAK menampilkan section "Pinned Messages" apapun | Step 10 (S-02, Chrome asli): "Acme Corporation" → "Azure Interior" — record B menampilkan "The conversation is empty.", tidak ada section apapun | [x] Pass [ ] Fail |
| 2 | Kembali ke kontak A | Badge "Pinned Messages" di kontak A masih benar seperti semula | Step 10: kembali ke "Acme Corporation" — badge "Pinned Messages 1" masih benar | [x] Pass [ ] Fail |

### T-XX: Item yang TIDAK Bisa Dites Lewat Tampilan Biasa (Informasi, Bukan Kegagalan)

- Tidak ada — semua fitur modul ini reachable dari chatter/Discuss biasa.

## Sign-off per Kelompok Fitur

| # | Kelompok fitur | Skenario tercakup | Status | Catatan |
|---|---|---|---|---|
| 1 | Pin/unpin log note (dua entry point) | T-01, T-02 | [x] Pass [ ] Fail | Berdasar Tour test otomatis Step 9 |
| 2 | Pin/unpin Discuss channel | T-03 | [x] Pass [ ] Fail | Berdasar interaksi Chrome asli Step 10 |
| 3 | Konsistensi antar-record | T-04 | [x] Pass [ ] Fail | Berdasar interaksi Chrome asli Step 10 |

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
| User | kuncoro@doodex.net | 2026-08-26 | Disetujui via chat: "UAT dianggap selesai, percaya AI test" — bukan eksekusi tangan sendiri T-01 dst., melainkan penerimaan eksplisit atas bukti Step 9 (Tour test otomatis)/Step 10 (interaksi Chrome asli AI) sebagai pengganti. |

**Verdict:** ✅ Lulus — disetujui atas dasar keputusan eksplisit user di atas.
