# Human QA Checklists — sale_margin_threshold

**Sumber:** diturunkan dari skenario S-XX di `../10_BUSINESS_FLOW_MIGRATION.md`, dikelompokkan per `Level`. Kalau skenario/level di file itu berubah, regenerate 4 file di folder ini juga — jangan diedit terpisah sampai tidak sinkron.

Tiap file berisi HANYA skenario dari satu `Level`, format bahasa manusia, langkah bernomor siap-jalan.

| File | Isi | Kapan dipakai |
|---|---|---|
| `01_SMOKE.md` | Flow paling kritis saja | Re-cek super cepat sebelum deploy/hotfix |
| `02_MAIN_FLOW.md` | Flow bisnis inti sehari-hari | QA rutin, atau setelah deploy fitur baru |
| `03_DETAIL.md` | Varian/edge-case, fitur sekunder | QA menyeluruh sebelum rilis besar |
| `04_NEGATIVE.md` | Guard/keamanan, hal yang HARUS ditolak | Direkomendasikan sebelum rilis besar APAPUN |

**Kombinasi yang disarankan:**
- Deploy/hotfix kecil, waktu sangat terbatas → `01_SMOKE.md` saja
- Deploy rutin, waktu cukup → `01_SMOKE.md` + `02_MAIN_FLOW.md`
- Rilis besar / sebelum UAT (step 11) → keempat file
