# Human QA Checklists — pin_message

**Sumber:** diturunkan dari skenario S-01..S-11 di `../10_BUSINESS_FLOW_MIGRATION.md`, dikelompokkan
per `Level`. Kalau skenario/level di file itu berubah, regenerate 4 file di folder ini juga.

**Konteks penting:** eksekusi live AI (Playwright) untuk Step 10 modul ini terblokir total sesi ini
(lihat `../10_BUSINESS_FLOW_MIGRATION.md` §0 dan `FINDINGS.md` `MF-46`) — checklist di bawah ini
BELUM pernah genuinely dijalankan manusia/AI end-to-end sejak migrasi 20.0. Sangat direkomendasikan
dijalankan MANUAL minimal sekali (terutama `01_SMOKE.md` + `04_NEGATIVE.md`) sebelum Step 11.

| File | Isi | Kapan dipakai |
|---|---|---|
| `01_SMOKE.md` | Flow paling kritis saja | Re-cek super cepat sebelum deploy/hotfix — kalau ini gagal, STOP, jangan lanjut apapun |
| `02_MAIN_FLOW.md` | Flow bisnis inti sehari-hari (toggle pin, badge, action-menu) | QA rutin, atau setelah deploy fitur baru yang menyentuh Chatter |
| `03_DETAIL.md` | Varian/edge-case: ganti thread (`AC-06-01`, PALING PENTING untuk dites manual), tombol "See"/jump, error-swallow, styling | QA menyeluruh sebelum rilis besar — **WAJIB dijalankan minimal sekali** karena ini area yang belum pernah terbukti otomatis sama sekali |
| `04_NEGATIVE.md` | Guard visibility jalur negatif (pesan yang HARUS TIDAK bisa di-pin) | Direkomendasikan sebelum rilis besar APAPUN |

Angka prefix (01-04) = urutan prioritas kalau waktu terbatas — bukan urutan wajib berurutan.

**Kombinasi yang disarankan:**
- Deploy/hotfix kecil, waktu sangat terbatas → `01_SMOKE.md` saja
- Deploy rutin, waktu cukup → `01_SMOKE.md` + `02_MAIN_FLOW.md`
- Rilis besar / sebelum UAT (step 11) → **keempat file**, dengan perhatian KHUSUS ke `03_DETAIL.md`
  butir "Ganti Thread" (`AC-06-01`) — ini satu-satunya area berisiko tinggi yang genuinely belum
  pernah dibuktikan lolos oleh siapapun/apapun (bukan AI, bukan tour otomatis) sejak migrasi 20.0
  dimulai.
