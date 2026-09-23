# Main Flow Test — sale_margin_threshold

**Level:** Main Flow — flow bisnis inti yang paling sering dipakai user/admin sehari-hari.
**Estimasi waktu:** ~15 menit.
**Sumber:** S-02, S-03, S-04, S-06, S-07 di `../10_BUSINESS_FLOW_MIGRATION.md`.

## Flow 1 — Rental order melewati cek margin sepenuhnya (S-02)

```
1. Pastikan modul Enterprise "sale_renting" terinstall.
2. Buat Sale Order baru, isi Rental Start/Return Date (menandakan order ini rental).
3. Tambah 1 order line dengan produk rentable, harga jual (price_unit) SENGAJA diisi jauh di bawah
   "Minimum sale price" produk tsb.
4. Klik "Confirm".
```
**Expected:** Order langsung terkonfirmasi (status "Sales Order") TANPA muncul wizard/pesan
peringatan margin apapun, walau harga jauh di bawah minimum.

## Flow 2 — Wizard non-blocking saat harga di bawah minimum (S-03)

```
1. Pastikan Settings > (pengaturan modul ini) "Blocking Transaction Order" TIDAK dicentang (off).
2. Buat Sale Order (bukan rental), tambah line dengan price_unit di bawah "Minimum sale price".
3. Klik "Confirm".
4. Amati popup "Confirm minimum sale price" muncul dengan pesan harga di bawah minimum.
5. Klik tombol "Confirm" pada popup tsb (BUKAN Cancel).
```
**Expected:** Langkah 3: order TIDAK langsung confirm, popup muncul, status order tetap "Quotation".
Langkah 5: order berubah jadi "Sales Order".

## Flow 3 — Blocking penuh saat setting diaktifkan (S-04)

```
1. Aktifkan Settings > "Blocking Transaction Order" (on).
2. Ulangi langkah 2-3 Flow 2 di atas.
```
**Expected:** Muncul pesan error (bukan popup konfirmasi) menyebut "Transaction blocked due to price
being lower than the minimum sale price", order TIDAK confirm, status tetap "Quotation".
**PENTING:** setelah selesai testing, kembalikan setting "Blocking Transaction Order" ke kondisi
semula (biasanya off), supaya tidak mengganggu test/pengguna lain di environment yang sama.

## Flow 4 — Kolom Margin/Minimum Sale Price di Product Variants (S-06/S-07)

```
1. Buka produk dengan >1 varian > smart button "N Variants".
2. Pastikan kolom "Margin Sale" dan "Minimum Sale Price" tampil TANPA perlu klik toggle kolom
   opsional (langsung terlihat).
3. Kalau modul "pos_margin_threshold" JUGA terinstall di environment yang sama: pastikan kolom ini
   HANYA MUNCUL SATU KALI (tidak dobel) -- kolom ini seharusnya milik pos_margin_threshold saat
   keduanya terinstall.
4. Cari/atur satu varian dengan margin negatif -- pastikan angka margin tampil MERAH.
5. Pastikan ada kolom tambahan "Incl. Tax" (harga minimum + pajak), terisi angka wajar.
```
**Expected:** Semua poin di atas benar, tidak ada kolom dobel, tidak ada error console.

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-09-23 | Docker 20.0, `pos_margin_sale_migration_20_qa` | AI (Claude Code, Step 10) | Pass (logic, via Odoo shell/ORM langsung -- bukan klik browser, lihat MF-46) | Flow 1-3: dikonfirmasi via pemanggilan `action_confirm()` langsung ke `sale.order` id 14/15 (data uji QA10 SMT). Flow 4: dikonfirmasi via `get_view()` langsung (arch akhir sama persis yang dikirim ke browser) -- tepat 1 set kolom, decoration merah ada, "Incl. Tax" ada. Render pixel di layar (warna, popup literal) belum di-screenshot -- tunggu MF-46 selesai untuk re-konfirmasi visual. |
