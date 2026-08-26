# Negative Test — pos_margin_threshold

**Level:** Negative — hal yang HARUS ditolak/tidak boleh terjadi.
**Sumber:** skenario S-02 di `../10_BUSINESS_FLOW_MIGRATION.md`.

## Skenario: Klik Cancel di wizard "Update margin sale" tidak boleh mengubah apapun

```
1. Buka Inventory > Products, tampilan List.
2. Centang beberapa produk.
3. Klik "Actions" > "Update margin sale".
4. Isi angka margin apapun di kolom "Margin".
5. Klik tombol "Cancel" (BUKAN "Assign").
6. Buka salah satu produk yang tadi dicentang.
```

**Yang HARUS terjadi:** margin produk TIDAK berubah sama sekali — angka yang sempat diisi di wizard dibuang begitu klik Cancel, tidak ada jejak di chatter produk.

**Tanda kalau ada yang salah:** margin produk berubah walau sudah klik Cancel (bukan Assign) — ini bug serius, laporkan segera.

## Skenario tambahan: multi-dialog

N/A — dikonfirmasi tidak ada aksi user manapun di modul ini yang bisa membuka lebih dari satu dialog/wizard sekaligus, jadi tidak ada skenario "dialog yang diabaikan" untuk ditulis di sini.

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-08-26 | Docker QA (`pos_margin_sale_migration_18_qa`, live server) | AI, real Chrome (Step 10) | Pass | Cancel menutup dialog bersih, tidak ada perubahan pada 2 produk yang dipilih |
