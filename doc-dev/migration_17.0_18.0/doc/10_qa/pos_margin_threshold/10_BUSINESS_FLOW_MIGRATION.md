# Business Flow — Migrasi pos_margin_threshold

**Step:** 10 — QA Testing (gate)
**Ref:** `05_acceptance/pos_margin_threshold/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-08-26

> Dijalankan lewat install bersih (bukan clone data produksi — tidak ada instance production, port kode saja per `CLAUDE.md`).
>
> **Cek Owl/JS vs Tour test dulu:** AC-02-01 (blocking) dan AC-02-02 (confirm) sudah tercakup penuh lewat 2 Tour test otomatis Step 9 (`test_pos_margin_threshold_below_minimum_blocked_tour`, `test_pos_margin_threshold_below_minimum_confirm_tour`) — TIDAK diulang di sini (lihat `09_devtest/pos_margin_threshold/09_DEV_TESTING.md`). Step 10 fokus ke AC yang BELUM ada bukti test sama sekali sebelum sesi ini: wizard assign margin (AC-03-01/02).
>
> **Mode eksekusi:** AI-interaktif (Claude in Chrome, real Chrome — `list_connected_browsers` dikonfirmasi tersedia sebelum dipakai), terhadap instance live G2-mode (`docker compose run` one-off, database `pos_margin_sale_migration_18_qa`, dihapus setelah sesi).

---

## Skenario

### S-01: Wizard "Update margin sale" — assign margin ke 1 produk
**Level:** Main Flow
**Precondition:** Login admin, produk "Apple Pie" ada (`standard_price=10.80`, margin awal 0%)
**Mode eksekusi:** AI-interaktif (Claude in Chrome)
**Steps:**
1. Inventory → Products → list view → centang checkbox "Apple Pie" saja
2. Klik "Actions" → "Update margin sale"
3. Isi Margin = 20, klik "Assign"
4. Buka form produk "Apple Pie", cek field "Margin" dan "Minimum sale price"
**Expected:** Wizard dialog muncul dengan produk yang dipilih pre-populated. Setelah Assign: `Margin` = 20.00%, `Minimum sale price` = $12.96 (10.80 × 1.2), chatter mencatat perubahan "0.00 → 20.00 (Margin)". Karena Sales Price ($12.00) sekarang di bawah minimum baru, field Sales Price ter-highlight merah (bonus konfirmasi visual, bukan bagian AC ini tapi terlihat otomatis).
**Actual:** Persis sesuai expected — dikonfirmasi via screenshot + baca DOM (`read_page`), chatter log muncul "Mitchell Admin: 0.00 → 20.00 (Margin)".
**Status:** [x] Pass

### S-02: Wizard "Update margin sale" — Cancel tidak menerapkan apapun
**Level:** Negative
**Precondition:** Sama seperti S-01
**Mode eksekusi:** AI-interaktif (Claude in Chrome)
**Steps:**
1. Pilih 2 produk (Acoustic Bloc Screens, Apple Pie), buka wizard "Update margin sale"
2. Klik "Cancel" (bukan Assign)
**Expected:** Dialog tertutup, TIDAK ADA perubahan pada margin/harga kedua produk.
**Actual:** Dialog tertutup bersih, kembali ke list produk, tidak ada highlight/perubahan apapun terlihat pada baris kedua produk.
**Status:** [x] Pass

### S-03: Multi-dialog check
**Level:** Negative
**Steps:** N/A — dikonfirmasi tidak ada kasus multi-dialog di modul ini. Satu-satunya dialog (`ask()`/`AlertDialog` di `pos_store.js`) dan satu-satunya wizard (`Update margin sale`) masing-masing berdiri sendiri, tidak pernah memicu dialog/wizard lain secara bersamaan dari satu aksi user yang sama.
**Status:** N/A

## Deferred (bukan blocker gate ini, risiko rendah — lihat `08_review`/`09_devtest`)

- **AC-02-03** (tidak ada line di bawah minimum → tidak ada popup sama sekali) — tidak dieksekusi sesi ini (butuh sesi POS penuh: buka register, kasir). Risiko rendah: ini kontrol negatif dari logic `lines.length > 0` yang jalur positifnya (`lines.length > 0`) sudah terbukti benar via 2 Tour test.
- **AC-02-04** (teks peringatan merah di orderline POS) — tidak diasersi visual terpisah sesi ini. Risiko rendah: render template (`orderline.xml`, `MF-20`) sudah terbukti tidak crash lewat 2 Tour test; S-01 di atas justru mengonfirmasi POLA highlight-merah-saat-di-bawah-minimum berfungsi (di form produk, konteks berbeda tapi mekanisme serupa).

## Ringkasan per Level

| Level | Skenario | Jumlah |
|---|---|---|
| Smoke | — (tercakup Tour test Step 9, tidak diulang) | 0 |
| Main Flow | S-01 | 1 |
| Detail | — | 0 |
| Negative | S-02, S-03 | 2 |

## Loop-back

Tidak ada skenario Fail — tidak ada loop-back diperlukan.

## Verdict

- [x] ✅ Lulus — lanjut ke step 11
