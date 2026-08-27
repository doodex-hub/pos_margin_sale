# Migration Spec (Teknis) — sale_margin_threshold

**Step:** 3 — Migration Spec
**Versi:** 18.0 → 19.0
**Ref:** `02_diff/sale_margin_threshold/02_DIFF_ANALYSIS.md`
**Tanggal:** 2026-08-26

---

## 1. Ringkasan Strategi

**Tidak ada perubahan kode wajib untuk migrasi versi ini.** Step 2 tidak menemukan satu pun blocker
teknis baru — semua perubahan core (`action_confirm` batch semantics, `ir.module.module` class
rename, `_register_hook` pindah file, `self._context`→`self.env.context`) bersifat kosmetik/internal
dan tidak mempengaruhi cara modul ini di-`_inherit`/dipanggil. Satu-satunya pekerjaan wajib adalah
bump versi manifest. Risiko yang ada (`MF-08`, batch-confirm singleton bug) SUDAH ADA sebelum
migrasi ini, blast radius-nya dikonfirmasi TIDAK berubah oleh 19.0 — keputusan memperbaiki atau
tidak ada di tangan user, bukan keharusan teknis migrasi.

## 2. Strategi per File/Simbol (ringkasan umum)

| File/simbol | Ref `DIFF-NNN` | Strategi migrasi | Risiko | Ref `BSL-NNN` |
|---|---|---|---|---|
| `__manifest__.py` | — | Bump `version` ke `19.0.x.x` | Tidak ada | — |
| `models/sale_order.py` `action_confirm()` | `DIFF-01` | **Tidak ada perubahan wajib** — kecuali user memutuskan memperbaiki `MF-08` (tambah `for order in self:`), yang merupakan keputusan terpisah dari migrasi versi | Tergantung keputusan user | `BSL-009` |
| `models/sale_order.py:24` `self._context` | `DIFF-03` | Opsional: ganti jadi `self.env.context` demi konsistensi dengan konvensi core 19.0 — tidak wajib, `_context` tetap alias valid | Sangat rendah | — |
| `models/product.py` `_register_hook()` | `DIFF-06` | **Tidak ada perubahan** — signature/semantik tidak berubah | Tidak ada | `BSL-010` |
| `models/res_config_settings.py` | `DIFF-07` | **Tidak ada perubahan** | Tidak ada | — |

## 2b. Risk Analysis Terstruktur

### Critical Migration Blockers

| # | Isu | Lokasi | Rujukan knowledge base |
|---|---|---|---|
| 1 | Manifest version — harus `19.0.x.x` | `__manifest__.py:17` | — |

**Priority:** HIGH untuk item manifest (wajib, mekanis). Tidak ada blocker lain.

### OWL Widget yang Butuh Rewrite/Review

Tidak ada — modul ini tidak punya JS/Owl sama sekali (`MF-06`, `assets._assets_sale` menunjuk
folder yang tidak ada).

### Controller & Route

Tidak ada — `controllers/controllers.py` dead scaffold, tidak disentuh.

### Assets & Dependency

Tidak ada perubahan — tidak ada asset JS/CSS aktual di modul ini.

### Kompatibilitas Data Model

| # | Isu | Lokasi | Priority | Ref `BSL-NNN` |
|---|---|---|---|---|
| 1 | `sale.order.line.tax_id`→`tax_ids` — dikonfirmasi TIDAK dipakai modul (ganda: grep kode + verifikasi core rename nyata di Step 2) | N/A | Tidak ada aksi | `FINDINGS.md` `MF-11` |
| 2 | `product_id` domain di `sale.order.line` berubah jadi lambda dinamis + `check_company=True` | Core, tidak disentuh modul | Tidak ada — `related` field tetap berfungsi | — |

### Risiko Integrasi

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | Kolisi `wizard.margin.product` dengan `pos_margin_threshold` (`MF-03`) — modul ini yang menang MRO, tidak berubah oleh migrasi versi | `wizard/wizard_margin_product.py` | Menengah — sudah diketahui, tidak perlu aksi baru |
| 2 | Dependency Rental (`is_rental_order`) — dikonfirmasi field masih ada persis nama sama di `sale_renting` 19.0 Enterprise, semantik sama (compute+store+editable Boolean) | `models/sale_order.py:14` | Rendah — tidak perlu perubahan kode |

### Urutan Prioritas Testing

1. Install & startup — manifest version, dependency (`base`, `product`, `sale`, `stock_account`)
   tetap Community di 19.0.
2. Core flow: konfirmasi Sale Order dengan produk di bawah minimum — jalur blocking
   (`ValidationError`) dan jalur wizard konfirmasi, keduanya harus tetap identik behavior-nya.
3. Rental order exemption — kalau `native-target-enterprise` (`sale_renting`) tersedia di environment
   test, verifikasi order rental tetap skip validasi margin.
4. Wizard bulk-assign margin (byte-identik `pos_margin_threshold`, risiko rendah).

### View List Checklist

N/A — tidak ada `<tree>` tersisa (sudah `<list>` sejak 17→18).

### Estimasi Effort (opsional)

| Area | Effort | Catatan |
|---|---|---|
| Manifest version bump | Trivial | Satu baris |
| Sisanya | Nol | Tidak ada perubahan kode wajib |

## 3. Data Migration

N/A — port kode saja.

## 4. Scope

### Termasuk
- Bump versi manifest.

### Di Luar Scope (sengaja, disetujui di intake)
- `MF-03`, `MF-05`, `MF-06`, `MF-07`, `MF-08` (quirk/bug warisan) — dipertahankan identik kecuali
  user memutuskan lain (`MF-08` khususnya butuh keputusan eksplisit, lihat `FINDINGS.md`).
