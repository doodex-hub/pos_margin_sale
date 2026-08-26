# Negative Test — pin_message

**Level:** Negative — hal yang HARUS ditolak/tidak boleh terjadi.
**Sumber:** skenario S-02 di `../10_BUSINESS_FLOW_MIGRATION.md`.

## Skenario: Section "Pinned Messages" tidak boleh bocor antar-record

```
1. Buka record A (contoh: kontak "Acme Corporation"), Log note, pin pesannya
   lewat tombol pin di sebelah nama pengirim.
2. Pindah ke record B yang belum punya pesan/pin sama sekali (contoh: kontak lain).
```

**Yang HARUS terjadi:** record B TIDAK menampilkan section "Pinned Messages" apapun — harus benar-benar seolah tidak pernah ada pin di record itu. Kalau section itu muncul di record B (apalagi menampilkan pesan dari record A), itu bug serius — data record A bocor ke tampilan record B.

## Skenario tambahan: multi-dialog

N/A — dikonfirmasi tidak ada aksi user manapun di modul ini yang membuka lebih dari satu dialog/wizard sekaligus.

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-08-26 | Docker QA (`pos_margin_sale_migration_18_qa`, live server) | AI, real Chrome (Step 10) | Pass | Record B ("Azure Interior") tidak menampilkan section Pinned Messages sama sekali |
