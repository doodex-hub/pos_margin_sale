# Negative Test — pin_message

**Level:** Negative — input salah, guard/keamanan, hal yang HARUS ditolak atau HARUS TIDAK muncul.
Direkomendasikan dijalankan minimal sekali sebelum rilis besar APAPUN.
**Estimasi waktu:** ~10 menit.
**Sumber:** S-10, S-11 di `../10_BUSINESS_FLOW_MIGRATION.md`.

## Entry "Pin" TIDAK BOLEH muncul untuk pesan sistem/notifikasi

```
1. Cari atau buat pesan yang BUKAN log note biasa, contoh:
   - Notifikasi sistem otomatis (mis. "Product created", muncul otomatis saat record dibuat).
   - Pesan tracking perubahan field (mis. ubah field apapun yang di-track di form, chatter akan
     menampilkan "Field X: Y → Z" sebagai changelog message).
2. Klik ikon "..." pada pesan tersebut.
3. Amati: entry "Pin" TIDAK BOLEH muncul di menu tersebut.
4. Amati juga: TIDAK ADA tombol pin inline apapun yang muncul di dekat pesan ini (kalaupun section
   Pinned Messages sedang expand).
```

## Fitur pin di Discuss channel (dead-code warisan, harus tetap tidak berdampak)

```
1. Buka Discuss (menu app "Discuss" di navbar atas).
2. Buka/mulai sebuah channel percakapan, kirim satu pesan.
3. Klik ikon "..." pada pesan itu di dalam Discuss.
4. Ini bukan skenario yang perlu "lolos" secara spesifik (perilaku ini dead-code sejak versi lama,
   sengaja dipertahankan apa adanya) — cukup pastikan TIDAK ADA crash/error console saat berinteraksi
   dengan pesan Discuss dari sisi manapun (chatter biasa vs Discuss channel tidak boleh saling
   mengganggu).
```

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-09-23 | Docker 20.0 QA (`localhost:8078`) | AI (Step 10, live via Playwright MCP) | **BLOCKED — tidak bisa dieksekusi** | Lihat `FINDINGS.md` MF-46. Guard logic dikonfirmasi tidak berubah dari 19.0 (Step 8 desk review), tapi jalur negatif ini belum pernah diverifikasi otomatis di step manapun (Step 9 hanya menguji jalur positif) — checklist di atas genuinely baru pertama kali ditulis. |
| | | | | |
