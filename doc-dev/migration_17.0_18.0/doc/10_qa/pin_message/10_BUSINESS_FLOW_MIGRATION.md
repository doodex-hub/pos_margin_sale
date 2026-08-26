# Business Flow — Migrasi pin_message

**Step:** 10 — QA Testing (gate)
**Ref:** `05_acceptance/pin_message/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-08-26

> AC-01-01/02 (toggle pin log note, jalur inline) dan AC-02-02 (action-menu "Pin" visibility, fix `MF-24`) sudah tercakup penuh lewat 2 Tour test otomatis Step 9 — TIDAK diulang di sini. Step 10 fokus ke AC yang benar-benar belum ada bukti test apapun sebelum sesi ini: Discuss-channel native pin (AC-02-01) dan reload saat ganti record (AC-04-02) — keduanya butuh interaksi lintas-halaman yang lebih natural lewat browser nyata daripada Tour test scripted.
>
> **Mode eksekusi:** AI-interaktif (Claude in Chrome, real Chrome — dikonfirmasi bekerja normal, TIDAK kena limitasi Service Worker yang membatasi Browser pane bawaan sesi ini).

---

## Skenario

### S-01: Pin/unpin pesan Discuss channel lewat aksi native "Pin"
**Level:** Main Flow
**Precondition:** Login admin, channel `#general` ada pesan
**Mode eksekusi:** AI-interaktif (Claude in Chrome)
**Steps:**
1. Buka Discuss → channel `#general`, kirim pesan baru
2. Hover pesan → klik menu "..." (three-dot)
3. **Cek: apakah entry "pins" (custom modul ini) ikut muncul di menu ini?**
4. Klik "Pin" → confirm "Yeah, pin it!" di dialog
5. Buka panel "PINNED MESSAGES" (ikon thumbtack di header channel), cek pesan muncul
6. Klik X pada pesan pinned → confirm "Yes, remove it please" untuk unpin
**Expected:** Menu "..." HANYA berisi SATU entry "Pin" (native core) — entry custom `pins` milik modul ini TIDAK muncul (karena `condition` di `pinMessage.js` sengaja mem-filter `is_discussion` messages). Dialog konfirmasi native muncul, pin berhasil, pesan muncul di panel "PINNED MESSAGES". Unpin juga berhasil, panel kembali kosong.
**Actual:** Persis sesuai expected. Menu "..." hanya berisi: Pin, Mark as Unread, Create Thread, Edit, Delete, Copy Link — tidak ada entry duplikat dari modul. Dialog "Pin It" ("You sure want this message pinned to #general forever and ever?") muncul dan berfungsi. Panel "PINNED MESSAGES" menampilkan pesan dengan benar. Dialog "Unpin Message" muncul dan berfungsi, panel kembali ke "This channel doesn't have any pinned messages."
**Status:** [x] Pass — ini bukti langsung pertama untuk `MF-09` (sebelumnya cuma dikonfirmasi lewat baca kode, sekarang dikonfirmasi lewat interaksi nyata: Discuss-channel pinning berfungsi 100% via mekanisme native 18.0, modul ini tidak mengganggu maupun diperlukan)

### S-02: Section "Pinned Messages" (chatter) reset benar saat pindah record
**Level:** Negative
**Precondition:** Login admin, minimal 2 record `res.partner` (dicoba: "Acme Corporation", "Azure Interior")
**Mode eksekusi:** AI-interaktif (Claude in Chrome)
**Steps:**
1. Buka "Acme Corporation" (record A) → Log note → pin lewat tombol inline
2. Cek badge "Pinned Messages 1" muncul di record A
3. Navigasi ke "Azure Interior" (record B, tidak punya pesan/pin apapun)
4. Cek: apakah section "Pinned Messages" bocor dari record A / muncul salah?
5. Kembali ke record A (tombol Previous)
6. Cek: apakah badge "Pinned Messages 1" masih benar (tidak hilang/rusak)?
**Expected:** Record B TIDAK menampilkan section "Pinned Messages" apapun (tidak ada state bocor dari record A). Record A, setelah kembali, tetap menampilkan badge "Pinned Messages 1" dengan benar.
**Actual:** Persis sesuai expected. Record B: "The conversation is empty.", tidak ada section Pinned Messages sama sekali. Record A (setelah kembali): "Pinned Messages 1" masih benar, pesan yang sama masih ada di dalamnya.
**Status:** [x] Pass

### S-03: Multi-dialog check
**Level:** Negative
**Steps:** N/A — dikonfirmasi tidak ada kasus multi-dialog dari SATU aksi user. Klik "Pin" (native, S-01) memicu SATU dialog konfirmasi ("Pin It"); klik tombol inline pin (jalur log note, tercakup Tour test Step 9) TIDAK memicu dialog sama sekali (langsung toggle). Tidak ada skenario di modul ini yang membuka >1 dialog/wizard sekaligus.
**Status:** N/A

## Ringkasan per Level

| Level | Skenario | Jumlah |
|---|---|---|
| Smoke | — (tercakup Tour test Step 9, tidak diulang) | 0 |
| Main Flow | S-01 | 1 |
| Detail | — | 0 |
| Negative | S-02, S-03 | 2 |

## Loop-back

Tidak ada skenario Fail — tidak ada loop-back diperlukan.

## Verdict

- [x] ✅ Lulus — lanjut ke step 11
