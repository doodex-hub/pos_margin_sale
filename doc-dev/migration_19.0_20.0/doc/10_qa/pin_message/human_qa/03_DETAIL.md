# Detail Test — pin_message

**Level:** Detail — varian/edge-case, fitur sekunder, kombinasi kondisi yang jarang dipakai tapi
tetap valid.
**Estimasi waktu:** ~15 menit.
**Sumber:** S-06, S-07, S-08, S-09 di `../10_BUSINESS_FLOW_MIGRATION.md`.

> **PALING PENTING DI FILE INI: "Ganti Thread" di bawah.** Ini satu-satunya skenario yang berulang
> kali ditandai risiko tinggi oleh Step 8 (Code Review) dan Step 9 (Dev Testing), dan **genuinely
> belum pernah dibuktikan lolos oleh siapapun/apapun** (bukan tour otomatis, bukan AI Step 10 — lihat
> `FINDINGS.md` MF-46 untuk alasan AI gagal mencobanya). Kalau kamu hanya punya waktu untuk SATU
> checklist Detail, jalankan ini.

## Ganti Thread (refresh Pinned Messages saat pindah record)

```
1. Buka Chatter di record A (mis. Contact "Azure Interior") — pastikan ada ≥1 pesan pinned di sana
   (pin salah satu Log Note kalau belum ada). Catat badge count-nya.
2. TANPA menutup tab/reload halaman, navigasi ke record B (Contact LAIN, mis. lewat breadcrumb/list
   Contacts, klik contact berbeda) sehingga Chatter yang sama kini menampilkan thread B.
3. Amati section "Pinned Messages" di record B:
   - Kalau record B TIDAK punya pesan pinned: section harus TIDAK MUNCUL SAMA SEKALI (bukan
     menampilkan sisa data dari record A).
   - Kalau record B PUNYA pesan pinned: badge count harus sesuai jumlah pinned di record B (bukan
     jumlah dari record A).
4. Kembali navigasi ke record A (tanpa reload) — pastikan section balik menampilkan data record A
   yang benar (bukan data B yang "nyangkut").
5. Ulangi langkah 1-4 beberapa kali berturut-turut (ganti-ganti thread dengan cepat) untuk
   memastikan tidak ada race condition/data basi yang muncul sesekali.
```

**Kalau langkah 3/4 gagal (data dari thread lama masih terlihat di thread baru):** ini konfirmasi bug
nyata terkait `MF-33`/`AC-06-01` — laporkan ke tim dev SEGERA sebagai temuan baru, jangan anggap
"known issue", karena belum pernah ada keputusan eksplisit menerima risiko ini.

## Tombol "See"/jump ke pesan asli

```
1. Pin satu pesan di tengah-tengah percakapan panjang (scroll dulu chatter sampai ada banyak pesan,
   pin salah satu yang berada di TENGAH, bukan yang paling atas).
2. Expand section "Pinned Messages".
3. Klik tombol "See" pada kartu pesan tersebut.
4. Amati: halaman scroll otomatis ke pesan ASLINYA di daftar pesan utama (bukan di section pinned),
   dan pesan itu ter-highlight sesaat (biasanya background berkedip/berubah warna).
```

## Simulasi error load pinned messages (opsional, butuh DevTools)

```
1. Buka DevTools > tab Network > cari request bernama mirip "search_read" atau set throttling ke
   "Offline" sesaat sebelum membuka Chatter.
2. Buka Chatter record dengan pesan pinned.
3. Amati: Chatter TETAP render normal (pesan biasa tetap muncul), tidak ada popup error ke user,
   TAPI Console (F12) mencatat "Error loading pinned messages: ...".
4. Nyalakan kembali koneksi network, reload halaman — pastikan kembali normal.
```

## Styling visual card Pinned Messages

```
1. Expand section "Pinned Messages" dengan ≥1 kartu.
2. Amati background kartu berwarna merah-coklat transparan (bukan putih polos, bukan ada border
   tebal/shadow mencolok).
```

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-09-23 | Docker 20.0 QA (`localhost:8078`) | AI (Step 10, live via Playwright MCP) | **BLOCKED — tidak bisa dieksekusi** | Browser Playwright shared antar sibling agent + webclient Odoo blank di semua tab (bukan spesifik ke sesi ini) — lihat `FINDINGS.md` MF-46 untuk bukti teknis lengkap (STOP-rule ditegakkan setelah ≥6 percobaan). "Ganti Thread" BELUM PERNAH dibuktikan lolos oleh siapapun sejak migrasi 20.0 dimulai — checklist di atas genuinely baru pertama kali ditulis, prioritas tertinggi untuk dijalankan manual. |
| | | | | |
