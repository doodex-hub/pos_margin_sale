# Human QA Checklists — pos_margin_threshold

**Sumber:** diturunkan dari skenario S-XX di `../10_BUSINESS_FLOW_MIGRATION.md`, dikelompokkan per `Level`. Kalau skenario/level di file itu berubah, regenerate 4 file di folder ini juga.

Tiap file berisi HANYA skenario dari satu `Level`, format bahasa manusia, langkah bernomor siap-jalan.

| File | Isi | Kapan dipakai |
|---|---|---|
| `01_SMOKE.md` | Flow paling kritis saja | Re-cek super cepat sebelum deploy/hotfix |
| `02_MAIN_FLOW.md` | Flow bisnis inti sehari-hari | QA rutin, atau setelah deploy fitur baru |
| `03_DETAIL.md` | Varian/edge-case | QA menyeluruh sebelum rilis besar |
| `04_NEGATIVE.md` | Guard/keamanan, hal yang HARUS ditolak | Direkomendasikan sebelum rilis besar apapun |

**Catatan modul ini:** Smoke dan jalur POS below-minimum (confirm/blocking) sudah tercakup lewat 2 Tour test otomatis yang jalan tiap `--test-enable` (`pos_margin_threshold/static/tests/tours/margin_threshold_tour.js`) — tidak diulang manual di sini kecuali Tour test-nya sendiri dicurigai gagal.
