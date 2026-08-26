# Detail Test — pos_margin_threshold

**Level:** Detail — varian/edge-case, fitur sekunder.
**Sumber:** N/A — modul ini tidak punya skenario ber-`Level: Detail` tersendiri di `../10_BUSINESS_FLOW_MIGRATION.md` sesi ini.

## Item yang direkomendasikan dicek manual kalau ada waktu (belum ada bukti test otomatis)

Bukan blocker rilis (risiko sudah dinilai rendah, lihat `08_review/08_CODE_REVIEW.md` §C dan `09_devtest/09_DEV_TESTING.md`), tapi baik ditutup sebelum rilis besar:

```
1. Buka POS, buka register, jual sebuah produk yang harganya SUDAH DI ATAS harga
   minimum (bukan di bawah). Klik Pay.
   -> Yang HARUS terjadi: tidak ada dialog peringatan apapun yang muncul,
      langsung lanjut ke layar pembayaran seperti biasa.
2. Di keranjang belanja POS, tambahkan produk dengan harga di bawah minimum
   (custom price via numpad). Lihat baris produk itu di keranjang.
   -> Yang HARUS terjadi: ada teks peringatan berwarna merah di baris produk itu
      (di bawah nama produk), menandakan harga di bawah minimum.
```

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| | | | | |
