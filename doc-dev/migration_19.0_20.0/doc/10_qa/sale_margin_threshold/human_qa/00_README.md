# Human QA Checklists — sale_margin_threshold

**Sumber:** diturunkan dari skenario S-XX di `../10_BUSINESS_FLOW_MIGRATION.md`, dikelompokkan per
`Level`. Kalau skenario/level di file itu berubah, regenerate 4 file di folder ini juga — jangan
diedit terpisah sampai tidak sinkron.

**Catatan penting per 2026-09-23:** beberapa skenario di `01_SMOKE.md`/`04_NEGATIVE.md`/
`03_DETAIL.md` di bawah BELUM sempat diverifikasi lewat klik browser sungguhan sesi Step 10 ini
(blocker infrastruktur `FINDINGS.md` MF-46 — container Docker QA bersama sempat gagal me-render
webclient sama sekali untuk semua agent yang menguji paralel). Langkah-langkah di bawah tetap valid
sebagai PANDUAN manual — jalankan langkah ini SENDIRI (dev/QA/PM) begitu environment normal kembali,
untuk menutup gap verifikasi yang tersisa.

| File | Isi | Kapan dipakai |
|---|---|---|
| `01_SMOKE.md` | Flow paling kritis saja | Re-cek super cepat sebelum deploy/hotfix — kalau ini gagal, STOP, jangan lanjut apapun |
| `02_MAIN_FLOW.md` | Flow bisnis inti sehari-hari | QA rutin dengan waktu terbatas, atau setelah deploy fitur baru yang menyentuh flow utama |
| `03_DETAIL.md` | Varian/edge-case, fitur sekunder | QA menyeluruh sebelum rilis besar, atau setelah bug report terkait edge-case |
| `04_NEGATIVE.md` | Guard/keamanan, hal yang HARUS ditolak | Direkomendasikan dijalankan minimal sekali sebelum rilis besar APAPUN |

Angka prefix (01-04) = urutan prioritas kalau waktu terbatas (Smoke dulu, baru Main Flow, dst) —
bukan urutan wajib dijalankan berurutan.

**Kombinasi yang disarankan:**
- Deploy/hotfix kecil, waktu sangat terbatas → `01_SMOKE.md` saja
- Deploy rutin, waktu cukup → `01_SMOKE.md` + `02_MAIN_FLOW.md`
- Rilis besar / sebelum UAT (step 11) → keempat file — **WAJIB untuk modul ini**, karena beberapa
  item Detail/Negative masih Pending (belum genuinely diverifikasi live) per catatan di atas
- Kapan pun ada perubahan yang menyentuh logic disable/policy `blocking_transaction_order` → jalankan
  `04_NEGATIVE.md` terlepas dari kombinasi lain yang dipilih
