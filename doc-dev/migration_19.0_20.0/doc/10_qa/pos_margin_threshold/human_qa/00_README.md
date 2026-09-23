# Human QA Checklists — pos_margin_threshold

**Sumber:** diturunkan dari skenario S-XX di `../10_BUSINESS_FLOW_MIGRATION.md`, dikelompokkan per
`Level`. Kalau skenario/level di file itu berubah, regenerate 4 file di folder ini juga.

Tiap file berisi HANYA skenario dari satu `Level`, bahasa manusia (bukan jargon AC/BSL), langkah
bernomor siap-jalan.

| File | Isi | Kapan dipakai |
|---|---|---|
| `01_SMOKE.md` | Flow paling kritis saja (2 langkah) | Re-cek super cepat sebelum deploy/hotfix |
| `02_MAIN_FLOW.md` | Flow bisnis inti sehari-hari (9 langkah) | QA rutin, atau setelah deploy fitur baru |
| `03_DETAIL.md` | Varian/edge-case, fitur sekunder (7 langkah) | QA menyeluruh sebelum rilis besar |
| `04_NEGATIVE.md` | Guard/keamanan, hal yang HARUS ditolak/tidak muncul (3 langkah, 2 di antaranya BELUM lulus verifikasi — lihat catatan di file itu) | Wajib sebelum rilis besar APAPUN |

**Catatan penting untuk QA manusia yang menjalankan `04_NEGATIVE.md`:** 2 dari 3 item di file itu
BELUM pernah diverifikasi live sama sekali oleh AI (blocker infrastruktur test, `FINDINGS.md MF-46`)
— kalau kamu menjalankan ini secara manual dan menemukan hasil BEDA dari "Expected", ini KEMUNGKINAN
BESAR temuan baru genuine (bukan regresi yang sudah diketahui), tolong laporkan sebagai finding baru.

**Kombinasi yang disarankan:**
- Deploy/hotfix kecil, waktu sangat terbatas → `01_SMOKE.md` saja
- Deploy rutin, waktu cukup → `01_SMOKE.md` + `02_MAIN_FLOW.md`
- Rilis besar / sebelum UAT (step 11) → keempat file, **WAJIB termasuk `04_NEGATIVE.md`** (2 item di
  situ belum pernah dikonfirmasi manusia maupun AI)
- Kapan pun mengubah logic dialog/config POS margin → `04_NEGATIVE.md` terlepas dari kombinasi lain
