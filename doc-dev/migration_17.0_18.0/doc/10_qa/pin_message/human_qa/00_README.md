# Human QA Checklists — pin_message

**Sumber:** diturunkan dari skenario S-XX di `../10_BUSINESS_FLOW_MIGRATION.md`, dikelompokkan per `Level`. Kalau skenario/level di file itu berubah, regenerate 4 file di folder ini juga.

Tiap file berisi HANYA skenario dari satu `Level`, format bahasa manusia, langkah bernomor siap-jalan.

| File | Isi | Kapan dipakai |
|---|---|---|
| `01_SMOKE.md` | Flow paling kritis saja | Re-cek super cepat sebelum deploy/hotfix |
| `02_MAIN_FLOW.md` | Flow bisnis inti sehari-hari | QA rutin, atau setelah deploy fitur baru |
| `03_DETAIL.md` | Varian/edge-case | QA menyeluruh sebelum rilis besar |
| `04_NEGATIVE.md` | Guard/keamanan, hal yang HARUS ditolak | Direkomendasikan sebelum rilis besar apapun |

**Catatan modul ini:** toggle pin lewat log note (tombol inline DAN menu aksi "...") sudah tercakup lewat 2 Tour test otomatis (`pin_message/static/tests/tours/pin_message_tour.js`) — tidak diulang manual di sini. Folder ini fokus ke pin/unpin Discuss channel (lewat aksi native, bukan kode modul ini) dan perilaku ganti-record chatter.
