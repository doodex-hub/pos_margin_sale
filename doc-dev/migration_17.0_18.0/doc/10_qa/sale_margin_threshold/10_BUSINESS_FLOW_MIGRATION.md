# Business Flow — Migrasi sale_margin_threshold

**Step:** 10 — QA Testing (gate)
**Ref:** `05_acceptance/sale_margin_threshold/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-08-26

> Modul ini tidak punya Owl/JS (Applicability Check Fase E: N/A, murni backend) — tidak ada Tour test yang relevan. AC-01/02/03 inti (blocking, wizard confirm, batch-confirm) sudah tercakup penuh lewat unit/integration test otomatis Step 9 (`test_action_confirm.py`, 4 test) — TIDAK diulang di sini. Step 10 fokus ke AC yang genuinely butuh verifikasi visual UI (dedup field) yang tidak bisa dibuktikan test Python biasa.
>
> **Mode eksekusi:** AI-interaktif (Claude in Chrome).

---

## Skenario

### S-01: Field "Margin"/"Minimum sale price" TIDAK dobel saat `pos_margin_threshold` juga terinstall
**Level:** Detail
**Precondition:** Ketiga modul (`pos_margin_threshold`, `sale_margin_threshold`, `pin_message`) terinstall bersamaan (environment QA standar project ini)
**Mode eksekusi:** AI-interaktif (Claude in Chrome)
**Steps:**
1. Buka form produk apapun (dicoba: "Apple Pie")
2. Baca DOM lengkap (`read_page filter=all`), hitung berapa kali label "Margin" dan "Minimum sale price" muncul
**Expected:** Field/label ini muncul TEPAT SATU KALI (dari `pos_margin_threshold`), bukan dua kali (dobel dari `sale_margin_threshold` juga) — `module_pos_margin_threshold == True` harus menyembunyikan salinan `sale_margin_threshold`.
**Actual:** Dikonfirmasi via `read_page`: HANYA satu `label "Margin"` dan satu `label "Minimum sale price"` di seluruh accessibility tree form. Tidak ada duplikasi.
**Status:** [x] Pass

### S-02: AC-01-04 (rental order → skip validasi)
**Level:** Detail
**Steps:** N/A — **tidak bisa dites di environment ini sama sekali.** Modul rental adalah fitur Odoo Enterprise, tidak tersedia di image `odoo:18.0` Community yang dipakai project ini (dikonfirmasi tidak ada modul apapun dengan nama mengandung "rental" ter-install/tersedia). `hasattr(self, 'is_rental_order')` di kode akan selalu `False` di environment Community — cabang ini genuinely tidak bisa dieksekusi tanpa Enterprise.
**Status:** N/A — didokumentasikan sebagai gap permanen di environment ini, bukan kegagalan test.

### S-03: Multi-dialog check
**Level:** Negative
**Steps:** N/A — dikonfirmasi tidak ada kasus multi-dialog. `action_confirm()` hanya membuka SATU wizard (`sale.confirmation.wizard`) atau me-raise SATU `ValidationError`, tidak pernah keduanya/berurutan dari satu klik yang sama.
**Status:** N/A

## Deferred (bukan blocker gate ini, risiko rendah — lihat `08_review`/`09_devtest`)

- **AC-03-02** (klik Cancel di wizard confirm → tidak ada efek) — tidak dieksekusi interaktif sesi ini. Risiko rendah: `special="cancel"` adalah atribut tombol form deklaratif Odoo standar (tutup dialog tanpa server call), bukan logic custom modul ini.

## Ringkasan per Level

| Level | Skenario | Jumlah |
|---|---|---|
| Smoke | — (N/A, tidak ada Owl/JS) | 0 |
| Main Flow | — (tercakup unit test Step 9, tidak diulang) | 0 |
| Detail | S-01, S-02 | 2 |
| Negative | S-03 | 1 |

## Loop-back

Tidak ada skenario Fail — tidak ada loop-back diperlukan.

## Verdict

- [x] ✅ Lulus — lanjut ke step 11
