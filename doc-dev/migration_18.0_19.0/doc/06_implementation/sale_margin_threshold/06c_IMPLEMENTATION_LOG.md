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
| G1 (checkpoint Fase A) | ✅ **Pass** (setelah 2 fix baru, lihat "Riwayat Percobaan G1") | 2026-08-27 |
| A3 | N/A — ACL wizard sudah ada sejak 17→18 | 2026-08-26 |
| A4 | ✅ | 2026-08-26 |
| A5 | ✅ — **2 fix baru ditemukan lewat G1** (`groups_id`→`group_ids`, `users`→`user_ids`), lihat entri di bawah | 2026-08-27 |
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

Mode C (AI jalankan langsung, Claude Code CLI, `docker compose up`), image `odoo:19.0` (sudah ada
lokal, tidak perlu build dari `native-target`). Dua percobaan GAGAL menemukan gap baru yang tidak
ketahuan di Step 2 (fokus Step 2 sepenuhnya JS/Python `point_of_sale`/`mail`, tidak menyentuh
`ir.actions.server`/`res.groups` core `base`) — percobaan ketiga PASS bersih.

| # | Dijalankan setelah fase | Mode | Hasil | Error (kalau fail) | Tanggal |
|---|---|---|---|---|---|
| 1 | A5 (ketiga modul) | C | ❌ Fail | `ValueError: Invalid field 'groups_id' in 'ir.actions.server'` — parsing `sale_margin_threshold/views/products.xml:70`. Core 19.0 rename `groups_id`→`group_ids` di `ir.actions.server`/`ir.actions.act_window` (`odoo/addons/base/models/ir_actions.py`), dikonfirmasi bukan quirk 18.0 (18.0 juga pakai `groups_id`, jadi ini genuinely rename 19.0). | 2026-08-27 |
| 2 | A5 (ketiga modul, setelah fix #1) | C | ❌ Fail | `AttributeError: 'res.groups' object has no attribute 'users'` di `sale_margin_threshold/models/product.py:128` (`_register_hook`). Core 19.0 rename `res.groups.users`→`user_ids` (`odoo/addons/base/models/res_groups.py`), relation table sama (`res_groups_users_rel`). | 2026-08-27 |
| 3 | A5 (ketiga modul, setelah fix #1+#2) | C | ✅ **Pass** | — semua 68 modul (termasuk ketiga modul target) load bersih, "Registry loaded in 33.878s", tidak ada error/warning. | 2026-08-27 |

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
  `wizard/sale_confirmation.py`, `wizard/wizard_margin_product.py`, `tests/test_cross_module.py`
- **Item spec (ref):** `03_MIGRATION_SPEC.md` §1 ("tidak ada perubahan kode wajib") — **KOREKSI:
  spec ini TERBUKTI TIDAK LENGKAP, ditemukan lewat G1 percobaan #2 (bukan Step 2/3)**, lihat
  "Temuan di Luar Spec" di bawah.
- **Aksi:**
  - `models/product.py:128,130,131` (`_register_hook`): `group.users` → `group.user_ids` (2 lokasi),
    `self.env.ref('base.group_user').users` → `.user_ids` — core 19.0 me-rename field
    `res.groups.users` jadi `user_ids` (`odoo/addons/base/models/res_groups.py`, relation table SAMA:
    `res_groups_users_rel`).
  - `tests/test_cross_module.py:31,33` (`group.users.ids` → `group.user_ids.ids`, 2 lokasi) —
    supaya test tetap valid terhadap field baru, LOGIC assertion tidak diubah.
- **Secara eksplisit TIDAK dilakukan:** `MF-08` (batch-confirm singleton bug) TIDAK diperbaiki —
  masih menunggu keputusan eksplisit user, dipertahankan identik sesuai default "port kode saja".
  Semua temuan Step 2 lain (`ir.module.module` class rename, `_register_hook` pindah file internal,
  `action_confirm` batch semantics unchanged, `self._context` tetap valid) dikonfirmasi memang tidak
  butuh perubahan — TIDAK disentuh.
- **Risiko:** LOW (perbaikan mekanis, sudah divalidasi G1 percobaan #3 — PASS)
- **Status:** ✅ Selesai

## [Fase B1] Model Risiko Rendah

- **Aksi:** diverifikasi ulang — tidak ada perubahan.
- **Status:** ✅ Selesai

## [Fase B2] Model Kompleks

N/A — dikonfirmasi Applicability Check.

## [Fase C1] View Sederhana

- **Scope:** `views/products.xml`, `views/product_template_views.xml`, `views/res_config_settings.xml`,
  `views/sale_order.xml`
- **Aksi:**
  - `inherit_id` target: kelima target (`product.product_template_form_view`,
    `product.product_template_only_form_view`, `product.product_variant_easy_edit_view`,
    `sale.res_config_settings_view_form`, `sale.view_order_form`) dikonfirmasi stabil di 19.0
    (Step 4) — tidak diubah.
  - `views/products.xml:74,85` (`product_template_margin_sale_action_server`,
    `product_product_margin_sale_action_server`, dua record `ir.actions.server`): field
    `groups_id` → `group_ids` — **ditemukan lewat G1 percobaan #1 (bukan Step 2/4)**, core 19.0
    me-rename field ini (`odoo/addons/base/models/ir_actions.py`). NILAI (`eval="[(4,
    ref('group_sale_margin_action'))]"`) TIDAK diubah, cuma nama field.
- **Secara eksplisit TIDAK dilakukan:** `MF-05` (duplikat XML-ID, satu record menimpa yang lain)
  TIDAK diperbaiki — dikonfirmasi tetap ada identik di 19.0, menunggu klarifikasi user.
- **Risiko:** LOW (mekanis, divalidasi G1 percobaan #3 — PASS)
- **Status:** ✅ Selesai

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

- [x] **Ada** — `03_MIGRATION_SPEC.md` menyatakan "tidak ada perubahan kode wajib", tapi G1
  menemukan 2 gap yang TIDAK terdeteksi Step 2/3/4: `ir.actions.server.groups_id`→`group_ids` dan
  `res.groups.users`→`user_ids`. Keduanya di model `base` core (bukan `point_of_sale`/`mail`/`sale`
  yang jadi fokus riset Step 2) — Step 2 tidak mencakup diff `base`/`ir.actions`/`res.groups` secara
  spesifik untuk modul ini. **Tidak perlu balik ke Step 3/4 untuk update spec** (dampaknya kecil,
  fix mekanis, sudah divalidasi langsung lewat G1 PASS) — tapi dicatat di sini + `FINDINGS.md`
  (`MF-16`, `MF-17`) supaya jejak lengkap, konsisten prinsip "faktual, bukan diam-diam diperbaiki".

## Kontribusi ke Knowledge Base

- [x] **Ada** — `res.groups.users`→`user_ids` (baru, belum tercatat) dan konfirmasi ketiga
  `ir.actions.server.groups_id`→`group_ids` (sudah ada di knowledge base, dikonfirmasi kena lagi).
  Dicatat ke `migration-records/pos-margin-sale_18.0_19.0/SUMMARY.md` §"Temuan kandidat Step 6/G1".
