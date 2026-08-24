# Test Plan (Migrasi) — pos_margin_threshold

**Step:** 5 — Acceptance Criteria & Test Plan
**Ref:** `05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-08-24

---

## Step 9 — Dev Testing

> Fase E (JavaScript) applicable (lihat `01a_MIGRATION_INTAKE.md` §2b) — tour test WAJIB untuk AC-02 (blocking/confirm popup di POS), tidak cukup unit test backend saja karena risiko utama modul ini (`DIFF-02..05`) murni di sisi frontend/loader.

| AC | Deskripsi | Unit | Integration | Tour (Owl/JS) |
|---|---|---|---|---|
| AC-01-01..04 | Perhitungan margin/harga minimum | `tests/test_margin_sale.py` (ada) | — | — |
| AC-01-05 | Margin per-variant shared (`MF-01`) | `tests/test_margin_sale.py::test_margin_sale_inverse_writes_to_shared_template_not_per_variant` (ada, dari backfill) | — | — |
| AC-02-02 | Confirm popup POS (`blocking_transaction_pos=False`, jalur `ask()`) | — | — | ✅ **SUDAH DITULIS DAN PASS** — `static/tests/tours/margin_threshold_tour.js` + `tests/test_margin_threshold_tour.py` (Step 6, Mode D, Chrome asli). "tour succeeded", terverifikasi menemukan+memperbaiki `MF-13/15/16/17/18/19/20` |
| AC-02-01, AC-02-03..04 | Blocking popup POS (`blocking_transaction_pos=True`, jalur `AlertDialog`) + kombinasi lain | — | — | Belum ditulis — kandidat lanjutan Step 9 (bukan blocker Step 8, mekanisme dialog-nya sudah terverifikasi identik lewat AC-02-02) |
| AC-03-01..02 | Wizard assign margin | — | Bisa lewat `TransactionCase` biasa (buka wizard via `env['wizard.margin.product'].create(...)`, tidak butuh browser) | — |
| AC-04-01..02 | Cross-module | `tests/test_cross_module.py` (ada) — **WAJIB kedua modul terinstall bersamaan**, lihat `CLAUDE.md` §Adaptasi multi-modul | — | — |

## Step 10 — QA Testing

| AC | Deskripsi | Manual | AI-interaktif | AI+tool eksternal |
|---|---|---|---|---|
| AC-02-01..03 | Popup blocking/confirm POS | Manual (kalau tour Step 9 belum cover semua kombinasi setting) | Kalau tour belum ada saat QA jalan | — |
| AC-01/03/04 | Margin/wizard/cross-module | — (sudah cukup dari Step 9 otomatis) | — | — |

## Step 11 — UAT

| Kelompok fitur | AC tercakup | UAT |
|---|---|---|
| Margin & harga minimum | AC-01-01..05 | Manual, business user set margin kategori, cek harga minimum ter-hitung benar |
| Blocking POS | AC-02-01..04 | Manual, kasir sungguhan coba jual produk di bawah minimum, konfirmasi popup sesuai setting |
| Wizard assign margin | AC-03-01..02 | Manual |

## Ringkasan

| Step | Role | Tipe | Eksekusi | Jumlah AC |
|---|---|---|---|---|
| 9 | Developer | Unit/Integration/Tour | Otomatis — **1 tour test baru wajib ditulis** (AC-02) | 11 |
| 10 | QA | Manual/AI-interaktif | Campuran, fokus AC-02 kalau tour belum lengkap | 3-4 |
| 11 | PM/FA/User | UAT | Manual | 3 kelompok |
