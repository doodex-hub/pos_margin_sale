# Detail Test — sale_margin_threshold

**Level:** Detail — varian/edge-case, fitur sekunder, kombinasi kondisi yang jarang dipakai tapi
tetap valid.
**Estimasi waktu:** ~10 menit.
**Sumber:** S-08, S-09, S-10 di `../10_BUSINESS_FLOW_MIGRATION.md`.

## Flow 1 — "Incl. Tax" dengan pajak sungguhan (S-08)

```
1. Buat/pakai produk dengan Cost = 100, Margin Sale = -10 (Minimum Sale Price jadi 90).
2. Pasang Customer Tax 10% pada produk itu.
3. Cek kolom "Incl. Tax" di list Product Variants.
```
**Expected:** Nilai = 99.00 (90 x 1.10).

## Flow 2 — Stale-cache saat edit cepat di list (S-09, BUG WARISAN -- JANGAN DIPERBAIKI)

```
1. Buka list Product Variants (multi_edit), pastikan ada 2+ baris.
2. Edit "Sales Price" salah satu baris jadi di bawah "Minimum Sale Price"-nya SENDIRI.
3. TANPA reload/refresh halaman, cek kolom warna merah (highlight "Sales Price" di bawah minimum)
   pada baris LAIN yang tidak diedit.
```
**Expected (edge-case, bukan bug baru):** Kemungkinan baris lain TIDAK ikut update warnanya sampai
halaman di-reload -- ini bug warisan `MF-21` yang harus tetap ada, JANGAN dilaporkan sebagai bug baru
atau diminta diperbaiki tanpa persetujuan eksplisit dev.

## Flow 3 — Edit inline margin/minimum price tersimpan benar (S-10)

```
1. Buka list Product Variants (multi_edit) untuk produk dengan >1 varian berbagi Product Template
   yang sama.
2. Klik langsung sel "Margin Sale" salah satu varian, ubah nilainya, klik di luar sel untuk save.
3. Reload halaman.
4. Cek: nilai baru tersimpan? Varian LAIN yang berbagi Product Template yang sama ikut berubah
   nilainya juga?
```
**Expected:** Nilai tersimpan benar. Varian lain IKUT berubah (margin_sale disimpan di level
Template, bukan per-variant murni) -- ini behavior asli, bukan bug.

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-09-23 | Docker 20.0, `pos_margin_sale_migration_20_qa` | AI (Claude Code, Step 10) | Flow 1: Pass (via ORM langsung). Flow 2 & 3: Pending -- belum dijalankan | Flow 2/3 butuh interaksi klik/edit UI sungguhan yang tidak bisa dilakukan sesi ini (blocker infrastruktur `FINDINGS.md` MF-46) -- perlu dijalankan manusia atau AI sesi berikutnya begitu environment normal. |
