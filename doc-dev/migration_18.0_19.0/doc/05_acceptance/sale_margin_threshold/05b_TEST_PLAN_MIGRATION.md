# Test Plan (Migrasi) — sale_margin_threshold

**Step:** 5 — Acceptance Criteria & Test Plan
**Ref:** `05_acceptance/sale_margin_threshold/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-08-26

---

## Step 9 — Dev Testing

Tidak ada JS/Owl di modul ini (`MF-06`) — Fase E/F Step 6 N/A, tidak ada Tour test yang relevan.
Test existing: `tests/test_action_confirm.py`, `tests/test_cross_module.py`. Karena Step 3 tidak
menemukan perubahan kode wajib, test ini diharapkan PASS tanpa modifikasi setelah bump versi
manifest saja — kalau ada yang gagal pasca Step 6, itu sinyal regresi tak terduga (bukan hasil yang
diantisipasi).

| AC | Deskripsi | Unit | Integration | Tour (Owl/JS) |
|---|---|---|---|---|
| AC-01-01/02/03/04 | `action_confirm` (rental exempt, blocking, wizard, skip_check_price) | `test_action_confirm.py` | — | N/A |
| AC-01-05 | Bilingual EN/FR tanpa `fr_FR` | `test_action_confirm.py` (kalau ada kasus bahasa — cek isi test, jangan asumsikan dari nama) | — | N/A |
| AC-02-01/02 | Margin compute + dedup UI | *(shared logic dengan `pos_margin_threshold`, tidak ada unit test terpisah di modul ini)* | — | N/A |
| AC-03-01 | Wizard bulk-assign | *(tidak ada unit test dedicated — sama seperti `pos_margin_threshold`)* | — | N/A |
| AC-04-01 | Kolisi `wizard.margin.product` MRO | `test_cross_module.py` | — | N/A |
| AC-04-02 | `_register_hook` grup mutation | *(cek isi `test_cross_module.py` — mungkin sudah tercakup, verifikasi Step 9)* | — | N/A |
| AC-04-03 | Batch-confirm singleton bug | *(belum ada test — kalau user putuskan memperbaiki `MF-08` di Step 6, WAJIB tambah test batch-confirm baru di Step 9)* | — | N/A |

## Step 10 — QA Testing

| AC | Deskripsi | Manual | AI-interaktif | AI+tool eksternal |
|---|---|---|---|---|
| AC-01-02/03 | Konfirmasi order dengan margin di bawah minimum (blocking & wizard) | — | ✅ | — |
| AC-02-02 | Dedup field margin saat kedua modul terinstall | — | ✅ (inspeksi DOM, pola sama seperti project 17→18) | — |
| AC-01-04 rental exemption | *(N/A permanen tanpa Enterprise environment — kecuali `native-target-enterprise` `enterprise19.0` dipakai untuk setup test environment nyata, bukan cuma referensi baca kode)* | — | — | — |

## Step 11 — UAT

| Kelompok fitur | AC tercakup | UAT |
|---|---|---|
| Konfirmasi order dengan margin | AC-01-01/02/03/04/05 | Skenario: buat quotation dengan harga rendah, coba konfirmasi, lihat blokir/wizard |
| Wizard bulk-assign | AC-03-01 | Sama seperti `pos_margin_threshold` |

## Ringkasan

| Step | Role | Tipe | Eksekusi | Jumlah AC |
|---|---|---|---|---|
| 9 | Developer | Unit/Integration | Otomatis/background — diharapkan PASS tanpa modifikasi | 7 AC, sebagian besar sudah punya test existing |
| 10 | QA | AI-interaktif | 2 AC; AC-01-04 (rental) tetap N/A tanpa Enterprise environment nyata | 3 AC dipertimbangkan |
| 11 | PM/FA/User | UAT | Manual (selalu) | 2 kelompok fitur |
