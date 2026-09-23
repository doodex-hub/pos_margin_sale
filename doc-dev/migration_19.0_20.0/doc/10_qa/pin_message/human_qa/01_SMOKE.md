# Smoke Test — pin_message

**Level:** Smoke — flow paling kritis. Kalau salah satu langkah di sini gagal: STOP, jangan lanjut
deploy/testing lain, balik ke Step 9 atau eskalasi ke tim dev.
**Estimasi waktu:** ~5 menit.
**Sumber:** S-01, S-02 di `../10_BUSINESS_FLOW_MIGRATION.md`.

```
1. Login sebagai admin, buka record apapun yang punya Chatter (mis. Contacts > pilih satu contact).
2. Amati Chatter render normal: tombol "Send message"/"Log note"/"Activity" muncul, tidak ada
   halaman blank atau error merah di layar.
3. Buka Developer Tools (F12) > tab Console — pastikan TIDAK ADA error merah terkait
   "pin_message"/"Chatter"/"isSmall" saat halaman dimuat.
4. Tulis satu Log Note apa saja (klik "Log note", ketik teks, klik "Log").
5. Klik ikon "..." (action-menu) di pesan yang baru dibuat > klik "Pin".
6. Amati section "Pinned Messages" muncul di atas daftar pesan, dengan badge angka "1".
7. Klik header section "Pinned Messages" untuk EXPAND.
8. Amati kartu pesan pinned muncul TANPA error/crash (halaman tidak blank, tidak ada popup error).
   Ini yang paling penting — bug lama (MF-36) pernah bikin expand ini CRASH TOTAL sebelum fix.
```

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-09-23 | Docker 20.0 QA (`localhost:8078`) | AI (Step 9 Tour otomatis, BUKAN checklist manual ini) | Pass (tidak langsung) | Tour `pin_message_toggle_pin_tour`/`..._action_menu_pin_visible_tour` mencakup langkah setara (log note → pin → expand), 0 error console — tapi checklist manual di atas belum pernah genuinely dijalankan kata-per-kata. Live AI Step 10 gagal total (browser shared blocked, lihat `FINDINGS.md` MF-46). |
| | | | | |
