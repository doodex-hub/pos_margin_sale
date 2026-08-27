# Implementation Log — sale_margin_threshold

**Step:** 6 — Code Migration
**Ref:** `03_spec/sale_margin_threshold/03_MIGRATION_SPEC.md`, `migration-tool/templates/06a_CODE_MIGRATION_PHASES.md`
**Tanggal:** 2026-08-26

---

## Applicability Check

Sumber: `01a_MIGRATION_INTAKE.md` §2b.

| Fase | Relevan? | Bukti/alasan (dari `01a` §2b) |
|---|---|---|
| B2 (Model Kompleks) | ☐ Tidak | Hanya dynamic model access (`self.env[active_model]`) di `wizard/sale_confirmation.py` — mekanisme stabil lintas versi, tidak spesifik ke 18→19, dikonfirmasi Step 2 tidak ada perubahan API terkait |
| C2 (Semantik XML & UX) | ☐ Tidak | Syntax modern `invisible=`, dikonfirmasi Step 4 semua `inherit_id` target stabil |
| D1 (Controllers) | ☐ Tidak | `controllers/controllers.py` dead scaffold |
| D2 (Assets & CSS Stabilization) | ☐ Tidak | Tidak ada asset JS/CSS aktual (`MF-06`) |
| E (JavaScript/Owl) | ☐ **Tidak** | Modul ini tidak punya JS/Owl sama sekali |
| F (Upgrade Template) | ☐ Tidak (otomatis N/A karena E juga N/A) | — |

---

## Tabel Ringkas Status Fase

| Fase | Status | Tanggal |
|---|---|---|
| A1 | ✅ | 2026-08-26 |
| A2 | N/A — tidak ada `<tree>` tersisa | 2026-08-26 |
| G1 (checkpoint Fase A) | ⏳ Belum dijalankan | — |
| A3 | N/A — ACL wizard sudah ada sejak 17→18 | 2026-08-26 |
| A4 | ✅ | 2026-08-26 |
| A5 | ✅ — tidak ada perubahan diperlukan (dikonfirmasi Step 2/3) | 2026-08-26 |
| B1 | ✅ | 2026-08-26 |
| B2 | N/A | — |
| C1 | ✅ — semua `inherit_id` target dikonfirmasi stabil (Step 4) | 2026-08-26 |
| C2 | N/A | — |
| D1 | N/A | — |
| D2 | N/A | — |
| E | N/A | — |
| F | N/A | — |
| G2 (validasi akhir/runtime) | ⏳ Menunggu G1 | — |

## Riwayat Percobaan G1 (Install Test)

**Belum dijalankan** — sama seperti dua modul lain, menunggu environment Docker 19.0.

| # | Dijalankan setelah fase | Mode | Hasil | Error (kalau fail) | Tanggal |
|---|---|---|---|---|---|
| 1 | A2 | — | ⏳ Belum dijalankan | — | — |

---

## Entri

## [Fase A1] Manifest Bootstrap

- **Scope:** `sale_margin_threshold/__manifest__.py`
- **Aksi:** `version` `'18.0.1.0'` → `'19.0.1.0'`.
- **Secara eksplisit TIDAK dilakukan:** tidak ada perubahan lain di manifest.
- **Risiko:** LOW
- **Status:** ✅ Selesai

## [Fase A2] XML Tree → List

N/A — tidak ada `<tree>` tersisa.

## [Fase A3] Security Hardening

N/A — ACL sudah lengkap sejak 17→18, tidak ada model baru.

## [Fase A4] Skeleton & Folder Integrity

- **Aksi:** diverifikasi — tidak ada yang perlu diubah.
- **Status:** ✅ Selesai

## [Fase A5] Python API Compatibility

- **Scope:** `models/sale_order.py`, `models/product.py`, `models/res_config_settings.py`,
  `wizard/sale_confirmation.py`, `wizard/wizard_margin_product.py`
- **Item spec (ref):** `03_MIGRATION_SPEC.md` §1 ("tidak ada perubahan kode wajib").
- **Aksi:** diverifikasi ulang — TIDAK ADA perubahan kode. Semua temuan Step 2
  (`ir.module.module` class rename, `_register_hook` pindah file internal, `action_confirm` batch
  semantics unchanged, `self._context` tetap valid) bersifat kosmetik/internal, tidak mempengaruhi
  cara modul ini menulis override.
- **Secara eksplisit TIDAK dilakukan:** `MF-08` (batch-confirm singleton bug) TIDAK diperbaiki —
  masih menunggu keputusan eksplisit user (belum dijawab), dipertahankan identik sesuai default
  "port kode saja".
- **Risiko:** LOW
- **Status:** ✅ Selesai (tidak ada perubahan diperlukan)

## [Fase B1] Model Risiko Rendah

- **Aksi:** diverifikasi ulang — tidak ada perubahan.
- **Status:** ✅ Selesai

## [Fase B2] Model Kompleks

N/A — dikonfirmasi Applicability Check.

## [Fase C1] View Sederhana

- **Scope:** `views/products.xml`, `views/product_template_views.xml`, `views/res_config_settings.xml`,
  `views/sale_order.xml`
- **Aksi:** diverifikasi ulang — kelima `inherit_id` target (`product.product_template_form_view`,
  `product.product_template_only_form_view`, `product.product_variant_easy_edit_view`,
  `sale.res_config_settings_view_form`, `sale.view_order_form`) dikonfirmasi stabil di 19.0 (Step 4).
- **Secara eksplisit TIDAK dilakukan:** `MF-05` (duplikat XML-ID, satu record menimpa yang lain)
  TIDAK diperbaiki — dikonfirmasi tetap ada identik di 19.0, menunggu klarifikasi user.
- **Risiko:** LOW
- **Status:** ✅ Selesai (tidak ada perubahan kode diperlukan)

## [Fase C2] Semantik XML & Konsistensi UX

N/A — dikonfirmasi Applicability Check.

## [Fase D1] Controllers

N/A — dikonfirmasi Applicability Check.

## [Fase D2] Assets & CSS Stabilization

N/A — dikonfirmasi Applicability Check.

## [Fase E] JavaScript (Owl versi baru)

N/A — dikonfirmasi Applicability Check (modul ini tidak punya JS/Owl sama sekali).

## [Fase F] Upgrade Template

N/A — otomatis N/A karena Fase E N/A.

## [Fase G2] Validasi Akhir

⏳ Belum dijalankan — menunggu G1 (install test) dan environment Docker 19.0.

---

## Temuan di Luar Spec (kalau ada)

- [x] Tidak ada.

## Kontribusi ke Knowledge Base

- [x] Tidak ada temuan baru dari implementasi modul ini — sesuai prediksi Step 2/3, tidak ada kode
  yang perlu diubah.
