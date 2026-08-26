# Diff & Compatibility Analysis — sale_margin_threshold

**Step:** 2 — Diff & Compatibility Analysis
**Versi:** 18.0 → 19.0
**Tanggal:** 2026-08-26
**Ref:** `01_intake/sale_margin_threshold/01a_MIGRATION_INTAKE.md`, `migration-tool/knowledge/`

---

## 0. Knowledge Base Check

| Sumber | Sudah ada entry? | Lokasi |
|---|---|---|
| `version-diffs/18-to-19.md` | Ya — dibaca penuh, cross-check §1 (`res.groups` rename, `self._context`→`self.env.context`) terhadap kode modul: TIDAK relevan (modul tidak sentuh `category_id`/`groups_id`) | `migration-tool/knowledge/version-diffs/18-to-19.md` |
| `dependency-compat/sale_report/18-to-19.md` | Ya, `tax_id`→`tax_ids` sudah dicatat, **dikonfirmasi ulang independen di Step 2 ini** (§1 di bawah) | `migration-tool/knowledge/dependency-compat/sale_report/18-to-19.md` |
| `dependency-compat/sale_renting/18-to-19.md` atau `ir_module/18-to-19.md` | Tidak ada — kandidat baru | — |

## 0b. Gate Community vs Enterprise

Dependency map `01a_MIGRATION_INTAKE.md` §2: `base`, `product`, `sale`, `stock_account` — Community.
**Tapi ada dependency Enterprise implisit** (`is_rental_order`, modul Rental `sale_renting`) — gate ini
WAJIB.

- [x] Dicek langsung ke `native-target` PERAN Enterprise (`enterprise19.0/odoo/addons/sale_renting/`)
  — modul masih ada, TIDAK dihapus/direname, field `is_rental_order` masih ada dengan nama+semantik
  yang sama (compute+store+editable Boolean, `@api.depends('order_line.is_rental')`).
- [x] `native-source` Community-only (`odoo18`) dikonfirmasi TIDAK punya `sale_renting` sama sekali
  (Rental adalah Enterprise-only) — sisi 18.0 Enterprise dari field ini tidak bisa diverifikasi
  langsung dari tree yang tersedia (tidak ada `native-source-enterprise`), tapi tidak ada indikasi
  perubahan dari sisi 19.0 yang dicek.

## 0c. Gate Transitive Dependency

Tidak ada `depends` yang diusulkan dihapus untuk modul ini — N/A.

---

## 1. Perubahan Native (Core/Enterprise)

| ID | File/simbol modul | Simbol native terkait | Status di target | Dampak | Sumber |
|---|---|---|---|---|---|
| DIFF-01 | `models/sale_order.py` override `action_confirm()` | `sale.order.action_confirm()` (`sale/models/sale_order.py`) | **Tidak berubah** — signature sama, semantik batch (multi-record, `self.write()`/`self.filtered()` batched) IDENTIK di 18.0 dan 19.0. Docstring `_prepare_confirmation_values` tetap eksplisit "self can contain multiple records" di kedua versi | **Konfirmasi penting untuk `MF-08`:** bug singleton-assumption modul ini punya blast radius yang SAMA di 19.0 seperti di 18.0 — tidak lebih buruk, tidak lebih baik. Core tidak pernah membatasi diri ke singleton di versi manapun | Analisis baru |
| DIFF-02 | (tidak disentuh modul, tapi di method yang sama yang di-override) | Blok `message_subscribe` di `action_confirm()` 18.0 (baris ~1153-1157) | **Dihapus total** di 19.0 (grep penuh: 0 match `message_subscribe` di `sale_order.py` 19.0, ada 3 di 18.0) | Rendah untuk modul ini (tidak pernah dipakai/disentuh modul), tapi perubahan behavior core yang nyata — partner tidak lagi otomatis di-subscribe ke message follower saat order dikonfirmasi | Analisis baru |
| DIFF-03 | `models/sale_order.py:24` `self._context.get('skip_check_price')` | Konvensi `self._context` vs `self.env.context` | **Tidak breaking** — `self._context` tetap berfungsi sebagai alias backward-compatible di 19.0, TAPI core sendiri sudah pindah ke `self.env.context.copy()` di `action_confirm()` (dikonfirmasi langsung). Bukan gap fungsional, cuma kandidat cleanup kosmetik | Rendah — tidak wajib diubah | Analisis baru + `knowledge/version-diffs/18-to-19.md` §1 |
| DIFF-04 | `models/sale_order.py` (tidak langsung disentuh, tapi field yang di-`related`-kan `sale.order.line.minimum_sale_price`) | `sale.order.line.product_id` (domain berubah dari string statis ke lambda dinamis, `check_company=True` ditambah) | **Tidak berubah untuk tujuan modul** — nama field/comodel/relasi identik, `related='product_id.minimum_sale_price'` tetap berfungsi tanpa modifikasi | Rendah | Analisis baru |
| DIFF-05 | (dikonfirmasi TIDAK dipakai modul, tapi rename core nyata) | `sale.order.line.tax_id` → `tax_ids` | **RENAME dikonfirmasi ulang independen** — field `tax_id` (18.0, `sale_order_line.py:159`) tidak ada sama sekali di 19.0, diganti `tax_ids` (`sale_order_line.py:162`, compute method juga di-rename `_compute_tax_id`→`_compute_tax_ids`) | **Tidak berdampak ke modul ini** — grep penuh modul: 0 referensi ke `tax_id`/`tax_ids` (`MF-11` di `FINDINGS.md`, sudah CONFIRMED N/A sebelumnya, sekarang dikonfirmasi ganda dari sisi core) | Analisis baru + knowledge base |
| DIFF-06 | `models/product.py` (`_register_hook`, cek `ir.module.module`) | `ir.module.module` (Python class `Module`→`IrModuleModule`, `_register_hook()` dipindah `odoo/models.py`→`odoo/orm/models.py`) | **Rename class Python + pindah file core (internal), TIDAK berdampak** — `_name = 'ir.module.module'` (technical name yang dipakai `search()`) tidak berubah; `_register_hook()` signature/semantik (zero-arg, dipanggil sekali setelah registry build) identik, cuma lokasi definisi berpindah sebagai bagian refactor ORM 19.0 (`odoo/models.py`→package, isi asli ke `odoo/orm/models.py`) | Tidak ada — override modul tetap valid tanpa perubahan | Analisis baru |
| DIFF-07 | `models/res_config_settings.py` `blocking_transaction_order` | `res.config.settings` + `config_parameter=` kwarg (`base/models/res_config.py`) | **Tidak berubah** — mekanisme binding `config_parameter` generik (kwarg arbitrary di-`setattr` oleh `Field` base class) identik di 18.0/19.0 | Tidak ada | Analisis baru |

## 2. Kompatibilitas Dependency (OCA/Third-Party)

Tidak ada — dikonfirmasi dev tidak ada dependency OCA/third-party.

## 3. Temuan Baru — Kandidat Migration Records

- [ ] **Tidak ada temuan general baru yang cukup signifikan untuk `SUMMARY.md` dari modul ini** — semua
  temuan di §1 bersifat konfirmasi (rename kosmetik tanpa dampak, atau konfirmasi ulang independen
  yang sudah tercatat). Satu-satunya hal yang berpotensi masuk kandidat: `_register_hook()`
  dipindah dari `odoo/models.py` ke `odoo/orm/models.py` sebagai bagian refactor ORM 19.0 (relevan
  untuk modul APAPUN yang override `_register_hook`) — TAPI ini murni lokasi definisi core, tidak
  mempengaruhi cara modul manapun menulis override-nya (`super()._register_hook()` tetap bekerja
  identik). Diputuskan TIDAK dicatat sebagai kandidat terpisah — cukup dirujuk dari
  `pos-margin-sale_18.0_19.0/SUMMARY.md` kalau relevan di masa depan.

## 4. Ringkasan Risiko

| Item | Level risiko | Catatan |
|---|---|---|
| `MF-08` (batch-confirm singleton bug) | **Tinggi (sudah diketahui sejak Step 1, BUKAN gap baru dari Step 2)** | Dikonfirmasi Step 2: blast radius SAMA di 19.0 seperti 18.0 — keputusan user (perbaiki atau pertahankan) masih berlaku sama, tidak ada urgensi baru dari migrasi versi |
| `DIFF-02` (message_subscribe dihapus dari core) | Rendah | Tidak disentuh modul, murni informasi — kalau ada ekspektasi bisnis "partner otomatis follow order saat dikonfirmasi", itu sekarang hilang dari CORE (bukan dari modul ini), di luar scope migrasi modul ini |
| `DIFF-05` (`tax_id`→`tax_ids`) | Tidak ada | Dikonfirmasi ganda tidak relevan |
| Sisanya (`DIFF-01`, `03`, `04`, `06`, `07`) | Tidak ada / Rendah | Rename kosmetik atau perpindahan internal core, tidak butuh perubahan kode modul |

**Kesimpulan Step 2 modul ini:** TIDAK ADA blocker teknis baru yang ditemukan dari migrasi versi
untuk `sale_margin_threshold` — modul ini jauh lebih "tenang" dibanding `pos_margin_threshold` untuk
migrasi 18→19 ini (konsisten dengan pola project 17→18 sebelumnya, di mana modul ini juga cuma
berubah 2 baris). Satu-satunya risiko terbuka adalah `MF-08`, yang sudah ada SEBELUM migrasi ini
dimulai dan butuh keputusan user, bukan hasil temuan Step 2.
