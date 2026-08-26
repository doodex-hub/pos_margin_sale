# Human QA Checklists — sale_margin_threshold

**Sumber:** diturunkan dari skenario S-XX di `../10_BUSINESS_FLOW_MIGRATION.md`, dikelompokkan per `Level`. Kalau skenario/level di file itu berubah, regenerate 4 file di folder ini juga.

Tiap file berisi HANYA skenario dari satu `Level`, format bahasa manusia, langkah bernomor siap-jalan.

| File | Isi | Kapan dipakai |
|---|---|---|
| `01_SMOKE.md` | Flow paling kritis saja | Re-cek super cepat sebelum deploy/hotfix |
| `02_MAIN_FLOW.md` | Flow bisnis inti sehari-hari | QA rutin, atau setelah deploy fitur baru |
| `03_DETAIL.md` | Varian/edge-case | QA menyeluruh sebelum rilis besar |
| `04_NEGATIVE.md` | Guard/keamanan, hal yang HARUS ditolak | Direkomendasikan sebelum rilis besar apapun |

**Catatan modul ini:** modul ini tidak punya UI/JS sama sekali (murni backend) — sebagian besar flow inti (confirm order dengan harga di bawah minimum, blocking, batch-confirm) sudah tercakup lewat unit/integration test otomatis (`sale_margin_threshold/tests/test_action_confirm.py`), bukan sesuatu yang bisa "diklik" manual secara terpisah — cukup pastikan test suite `--test-enable` pass.
