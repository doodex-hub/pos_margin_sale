# Test Plan — pos_margin_threshold

**Module:** `pos_margin_threshold`
**Ref:** `doc-dev/backfill/spec/pos_margin_threshold/01B_ACCEPTANCE_CRITERIA.md`
**Taxonomy:** vocab Odoo intrinsik (`TransactionCase`/`HttpCase`/`Tour`) — `cicd/test_design/odoo-testing-taxonomy.md` tidak disentuh (opsional, lihat `USAGE_GUIDE.md` §0)
**Dibuat oleh:** BACKFILL (Step 03B)
**Last Updated:** 2026-07-31

---

## Step 04 — Developer Testing (backfill)

| AC | Deskripsi singkat | Unit | Integration | API |
|---|---|---|---|---|
| AC-01-01 | margin_sale compute dari kategori | ✓ | | |
| AC-01-02 | override manual margin_sale tidak ke-reset | ✓ | | |
| AC-01-03 | minimum_sale_price = cost*(1+margin) | ✓ | | |
| AC-01-04 | inverse minimum_sale_price → margin_sale | ✓ | | |
| AC-01-05 | guard standard_price=0 | ✓ | | |
| AC-01-06 | `minimum_sale_price_with_tax` multi-variant (F-01) | ✓ | | |
| AC-02-01/02/03 | blocking transaction POS (JS, `Order.pay`) | | ✓ (Tour) | |
| AC-03-01/02 | wizard assign margin massal | ✓ | | |
| AC-04-01 | `blocking_transaction_order` tanpa UI sendirian (F-02) | ✓ | | |
| AC-04-02 | koeksistensi model wizard 2 modul (F-03) | | ✓ (install test) | |

**Ringkasan:** 8 AC → Unit (`TransactionCase`), 2 AC → Integration (Tour headless + install-test
kedua modul bersamaan). API: N/A (controller modul ini inert, tidak ada route aktif).

---

## Step 07 — QA Testing

| AC | Deskripsi singkat | AI-interaktif (07 §3) | AI-Browser/Tour (07B) |
|---|---|---|---|
| AC-02-01 | blocking payment saat harga < minimum | ✓ | ✓ |
| AC-02-02 | confirm popup saat tidak blocking | ✓ | ✓ |
| AC-03-01 | wizard assign margin dari list view | ✓ | |
| AC-04-02 | kedua modul margin terinstall bersamaan, tidak crash | ✓ | |

**Ringkasan:** Semua AC lewat AI-interaktif/desk-review (§3) sebagai default; skenario POS payment
(AC-02) butuh Tour headless (Mode E, lihat `USAGE_GUIDE.md`) karena melibatkan popup OWL POS.

---

## Ringkasan Keseluruhan

| Step | Tipe | Jumlah AC |
|---|---|---|
| 04 | Unit | 8 |
| 04 | Integration | 2 |
| 04 | API | N/A |
| 07 | AI-interaktif | 4 |
| 07 | AI-Browser/Tour | 2 (subset POS UI) |
