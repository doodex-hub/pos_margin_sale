# Main Flow Test — pin_message

**Level:** Main Flow — flow bisnis inti yang paling sering dipakai user/admin sehari-hari.
**Estimasi waktu:** ~10 menit.
**Sumber:** S-03, S-04, S-05 di `../10_BUSINESS_FLOW_MIGRATION.md`.

## Toggle pin via tombol inline (di dalam section Pinned Messages)

```
1. Buka Chatter record apapun, tulis 2-3 Log Note.
2. Pin salah satu pesan lewat action-menu "..." > "Pin".
3. Expand section "Pinned Messages".
4. Di dalam kartu pesan pinned, cari ikon pin kecil — amati warnanya UNGU/BIRU (text-primary,
   menandakan "sudah di-pin").
5. Klik ikon pin itu untuk UNPIN.
6. Amati: ikon berubah warna ABU-ABU (text-muted), pesan hilang dari section Pinned Messages, badge
   count berkurang.
```

## Toggle pin via action-menu "..." + tampilan ikon

```
1. Buka Chatter record lain, tulis 1 Log Note baru.
2. Klik ikon "..." di pesan tersebut.
3. Amati entry "Pin" muncul di menu, dengan ikon pin (BUKAN kotak kosong/placeholder).
4. Klik "Pin".
5. Amati section "Pinned Messages" muncul dengan badge "1".
```

## Badge count + collapse/expand

```
1. Pin 2-3 pesan berbeda di satu thread yang sama.
2. Amati badge di header section menampilkan angka yang BENAR (sesuai jumlah pesan yang di-pin).
3. Klik header untuk collapse — amati kartu-kartu hilang, badge tetap terlihat.
4. Klik header lagi untuk expand — amati kartu-kartu muncul kembali, sama seperti sebelum collapse.
```

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-09-23 | Docker 20.0 QA (`localhost:8078`) | AI (Step 9 Tour otomatis, bukan checklist manual ini) | Pass (tidak langsung, N=1 saja) | Badge N>1 dan re-collapse manual (langkah 3-4 bagian "Badge count") BELUM pernah diverifikasi terpisah oleh siapapun — checklist ini genuinely baru pertama kali ditulis. |
| | | | | |
