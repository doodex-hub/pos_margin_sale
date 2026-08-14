# Test Plan — sale_margin_threshold

**Module:** `sale_margin_threshold`
**Ref:** `doc-dev/backfill/spec/sale_margin_threshold/01B_ACCEPTANCE_CRITERIA.md`
**Taxonomy:** vocab Odoo intrinsik (`TransactionCase`/`HttpCase`/`Tour`)
**Dibuat oleh:** BACKFILL (Step 03B)
**Last Updated:** 2026-07-31

---

## Step 04 — Developer Testing (backfill)

| AC | Deskripsi singkat | Unit | Integration | API |
|---|---|---|---|---|
| AC-01-01 | blocking total saat confirm di bawah minimum | ✓ | | |
| AC-01-02 | wizard konfirmasi saat tidak blocking | ✓ | | |
| AC-01-03 | confirm normal tanpa masalah harga | ✓ | | |
| AC-01-04 | skip validasi untuk rental order | ✓ | | |
| **AC-02-01** | **batch-confirm multi order (F-05, PRIORITAS)** | **✓** | | |
| AC-03-01/02 | wizard confirm/cancel | ✓ | | |
| AC-04-01 | group dedup saat pos_margin_threshold terinstall (F-04) | | ✓ (install test) | |
| AC-04-02 | manual group override ter-revert (F-04) | | ✓ (install test) | |
| AC-04-03 | field invisible di view saat 2 modul terinstall | | ✓ (view test) | |

**Ringkasan:** 6 AC → Unit, 3 AC → Integration (butuh 2 modul terinstall bersamaan + registry
reload untuk F-04). API: N/A (controller inert).

**AC-02-01 adalah test case PALING PENTING sesi ini** — langsung memverifikasi/merefute F-05
(prioritas Tinggi di `FINDINGS.md`). Tulis TC eksplisit: buat 2+ `sale.order` draft, panggil
`(order1 + order2).action_confirm()` dari `TransactionCase`, assert apakah `ValueError: Expected
singleton` benar-benar ter-raise.

---

## Step 07 — QA Testing

| AC | Deskripsi singkat | AI-interaktif (07 §3) | AI-Browser/Tour (07B) |
|---|---|---|---|
| AC-01-01 | blocking confirm dari UI | ✓ | ✓ |
| AC-01-02 | wizard confirm dari UI | ✓ | ✓ |
| AC-02-01 | batch confirm dari list view (F-05) | ✓ | ✓ |
| AC-04-01 | action tidak dobel saat 2 modul terinstall | ✓ | |

**Ringkasan:** AC-02-01 diulang di Step 07 (Tour, klik multi-select di list view) karena Step 04
Unit test memanggil Python langsung — Tour membuktikan reproduksi lewat UI beneran (list view
batch action), bukan cuma lewat kode.

---

## Ringkasan Keseluruhan

| Step | Tipe | Jumlah AC |
|---|---|---|
| 04 | Unit | 6 |
| 04 | Integration | 3 |
| 04 | API | N/A |
| 07 | AI-interaktif | 4 |
| 07 | AI-Browser/Tour | 3 |
