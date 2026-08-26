# Detail Test — pos_margin_threshold

**Level:** Detail — varian/edge-case, fitur sekunder.
**Sumber:** skenario S-04 di `../10_BUSINESS_FLOW_MIGRATION.md`.

## Skenario: Wizard "Update margin sale" dibuka dari Product Variants (bukan Product Template)

```
1. Buka Inventory > Products > Product Variants (BUKAN menu "Products" biasa).
2. Centang checkbox satu variant produk.
3. Klik "Actions" > "Update margin sale".
4. Baca label field yang menampilkan produk terpilih di jendela wizard.
```

**Yang HARUS terjadi:** label field itu harus **"Product variants"**, BUKAN "Products" — wizard ini punya dua tampilan berbeda tergantung dari mana dia dibuka (list Produk biasa vs list Variant), dan harus konsisten menampilkan field yang benar sesuai konteksnya.

## Item lain yang direkomendasikan dicek manual kalau ada waktu (belum ada bukti test otomatis)

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
| 2026-08-26 | Docker QA (`pos_margin_sale_migration_18_qa2`, live server) | AI, real Chrome (Step 11 prep) | Pass (skenario Product Variants) | Label "Product variants" muncul benar dengan tag "[CONS_0001] Whiteboard Pen" |
