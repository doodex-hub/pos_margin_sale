# Smoke Test — sale_margin_threshold

**Level:** Smoke — flow paling kritis. Kalau salah satu langkah di sini gagal: STOP, jangan lanjut
deploy/testing lain, balik ke step 9 atau eskalasi ke tim dev.
**Estimasi waktu:** ~3 menit.
**Sumber:** S-01 di `../10_BUSINESS_FLOW_MIGRATION.md`.

```
1. Buka http://<host QA 20.0>/web/login (mis. http://localhost:8078/web/login).
2. Login dengan user admin (mis. admin/admin).
3. Pastikan halaman utama (menu Sales/Inventory/dst) benar-benar tampil — bukan halaman putih
   kosong. Kalau blank, tunggu 10 detik lalu refresh sekali; kalau tetap blank, ini BUKAN masalah
   sale_margin_threshold -- cek FINDINGS.md MF-46 dulu (kemungkinan asset cache server perlu
   di-regenerate oleh dev/ops) sebelum melapor sebagai bug modul ini.
4. Buka menu Sales > Orders. Pastikan list order tampil tanpa error.
5. Buka menu Inventory > Products > Product Variants pada produk apa saja yang punya >1 varian.
   Pastikan list tampil tanpa error (loading spinner tidak stuck, tidak ada popup error merah).
```

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-09-23 | Docker 20.0, `pos_margin_sale_migration_20_qa`, port 8078 | AI (Claude Code, Step 10) | Fail (render) | Login server-side sukses (session valid), tapi webclient blank total di 2 browser engine berbeda -- root cause `FINDINGS.md` MF-46 (asset bundle corruption akibat beban gabungan Step 10 paralel), bukan bug modul. Perlu diulang manusia/AI di sesi tidak-paralel. |
