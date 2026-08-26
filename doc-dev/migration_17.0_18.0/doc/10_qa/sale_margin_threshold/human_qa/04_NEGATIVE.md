# Negative Test — sale_margin_threshold

**Level:** Negative — hal yang HARUS ditolak/tidak boleh terjadi.
**Sumber:** N/A — modul ini tidak punya skenario ber-`Level: Negative` yang dieksekusi interaktif sesi ini (sudah tercakup unit test otomatis untuk kasus batch-confirm, lihat `01_SMOKE.md`).

## Kalau tetap ingin cek manual — klik Cancel di wizard confirm

```
1. Buat quotation dengan produk di bawah harga minimum, klik "Confirm".
2. Di jendela pop-up konfirmasi yang muncul, klik tombol "Cancel" (ikon silang atau tombol Cancel).
```

**Yang HARUS terjadi:** jendela tertutup, order TETAP di status "Quotation" (belum confirmed), tidak ada perubahan apapun ke order.

## Skenario tambahan: multi-dialog

N/A — dikonfirmasi tidak ada aksi user manapun di modul ini yang bisa membuka lebih dari satu dialog/wizard sekaligus.

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| | | | | |
