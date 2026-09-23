# Negative Test — sale_margin_threshold

**Level:** Negative — input salah, guard/keamanan, hal yang HARUS ditolak atau HARUS TIDAK muncul.
Direkomendasikan dijalankan minimal sekali sebelum rilis besar APAPUN.
**Estimasi waktu:** ~10 menit.
**Sumber:** S-05, S-11, S-12, S-13 di `../10_BUSINESS_FLOW_MIGRATION.md`.

## Flow 1 — Tombol "Cancel" di wizard tidak boleh berefek apapun (S-05)

```
1. Buat Sale Order dengan harga di bawah minimum (setting blocking OFF, lihat 02_MAIN_FLOW.md Flow
   2 langkah 1-4 untuk memunculkan wizard).
2. Klik tombol "Cancel" pada wizard (BUKAN "Confirm").
3. Cek status Sale Order.
```
**Expected:** Dialog tertutup, Sale Order TETAP "Quotation" (draft) -- tidak ada perubahan status,
tidak ada order line hilang/berubah, tidak ada error console.

## Flow 2 — Batch-confirm >1 order HARUS tetap crash (S-11, BUG WARISAN -- JANGAN DIPERBAIKI)

```
1. Buat 2+ Sale Order berbeda (bukan rental, harga tidak melanggar margin).
2. Di list view Sales Orders, pilih (centang) 2 order tsb sekaligus.
3. Klik aksi "Confirm" massal (batch action).
```
**Expected (bug warisan, sengaja dipertahankan -- keputusan dev final):** Muncul error teknis
("Expected singleton...") untuk SELURUH batch -- ini HARUS tetap terjadi. Kalau batch-confirm ini
malah BERHASIL tanpa error, itu JUSTRU regresi behavior yang harus dilaporkan ke dev (bukan dianggap
perbaikan yang diinginkan).

## Flow 3 — Field yang seharusnya tetap "rusak" (S-12, bug warisan `MF-27`)

```
1. Buka form Product Variant (bukan Product Template), lihat field "Sales Price"/list_price.
```
**Expected (bug warisan, JANGAN diperbaiki tanpa persetujuan dev):** Field ini kehilangan opsi
currency/digit formatting eksplisit dibanding field sejenis lainnya -- perilaku ini harus tetap ada,
konsisten 19.0.

## Flow 4 — Wizard "Assign Margin" tetap milik sale_margin_threshold saat 2 modul terinstall (S-13)

```
1. Pastikan pos_margin_threshold DAN sale_margin_threshold terinstall bersamaan.
2. Jalankan wizard "Assign Margin"/model wizard.margin.product dari kedua kemungkinan jalur akses
   (menu masing-masing modul kalau ada).
```
**Expected:** Perilaku wizard yang muncul konsisten dengan implementasi sale_margin_threshold
(bukan implementasi pos_margin_threshold yang tertimpa) -- independen urutan install modul.

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-09-23 | Docker 20.0, `pos_margin_sale_migration_20_qa` | AI (Claude Code, Step 10) | Flow 1: Pending. Flow 2-4: Pass (via kutipan test otomatis Step 9 + desk review Step 8, genuinely live sebelumnya) | Flow 1 butuh klik UI sungguhan, diblokir `FINDINGS.md` MF-46 -- desk review kode (tombol pakai `special="cancel"` native, 0 diff dari 19.0) menunjukkan risiko rendah, tapi belum genuinely diverifikasi klik. |
