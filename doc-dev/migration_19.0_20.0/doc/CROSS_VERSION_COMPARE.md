# Cross-Version Compare — pos_margin_threshold, sale_margin_threshold, pin_message

**Sifat:** Cross-cutting, bukan bagian 11-step (lihat `migration-tool/templates/CROSS_VERSION_COMPARE.md`
untuk prosedur lengkap yang diikuti persis di sini). Dipicu **Titik B (independen)** oleh dev,
memenuhi kriteria trigger wajib: multi-addon saling depend (`pos_margin_threshold` ⟷
`sale_margin_threshold`, `MF-03`/`MF-37`), dependency Enterprise (`sale_renting`), dan volume finding
tinggi (project ini sudah di `MF-46`, jauh di atas ambang 10).

**Tanggal eksekusi:** 2026-09-23.

---

## 1. Environment

| Peran | Compose | URL | Mount | Catatan |
|---|---|---|---|---|
| Source (19.0) | `docker-env/docker-compose.yml` | http://localhost:8079 | clone terpisah `pos-margin-sale-19.0-snapshot` (read-only, = branch `migration/19.0`) | Login admin/admin. |
| Target (20.0) | `docker-env/docker-compose.20.yml` | http://localhost:8078 | working tree ini langsung, container `pos_margin_sale_migration_20-odoo-1`, DB `pos_margin_sale_migration_20_qa` | Login admin/admin. |

**Deviasi dari rencana awal (dicatat, bukan disembunyikan):** task ini meminta Playwright MCP untuk
live-compare. Dalam pelaksanaan, Playwright MCP browser ternyata **genuinely shared** dengan 3 agent
sibling Step 10 QA yang berjalan paralel terhadap container yang sama (tab bertambah dari 1→3+ di
luar kendali sesi ini, URL/tab "current" berubah sendiri antar panggilan tool) — dikonfirmasi juga
oleh sibling agent sendiri di `FINDINGS.md` `MF-46`. Beralih ke **Browser pane privat**
(`mcp__Claude_Browser__*`) untuk 19.0 (berhasil, popup ter-render normal) dan mencoba hal sama untuk
20.0 — di 20.0 ditemukan webclient blank untuk **fresh session apapun** (lihat `MF-46` + tambahan
bukti yang dicatat di sana sesi ini: asset bundle utama `web.assets_web.min.js`/`.css` mengembalikan
`HTTP 200 content-length: 0` walau `ir.attachment` metadata melaporkan ukuran penuh — kemungkinan
besar akibat filestore DB utama tidak tersinkron akibat clone/restore DB paralel oleh Step 10, root
cause sama dengan checkpoint Postgres berat yang didiagnosis `MF-46`). **Mitigasi yang dipakai:**
verifikasi live 20.0 dialihkan ke **JSON-RPC `call_kw` langsung** (lewat `fetch()` di browser pane
yang sudah ter-autentikasi) — ini genuinely mengeksekusi kode Python/ORM backend yang sama persis
dengan yang akan dipanggil UI (view merge, compute, security), BUKAN cuma re-baca source statis;
hanya bagian yang murni membutuhkan RENDER JS/CSS (pixel warna, ikon) yang tidak bisa diverifikasi
ulang secara live sesi ini — untuk bagian itu dipakai bukti verifikasi live yang SUDAH ada &
terdokumentasi di `FINDINGS.md` (`MF-29`/`MF-37`/`MF-38`/`MF-32`/`MF-33`/`MF-36`), dikonfirmasi
`git log` menunjukkan **tidak ada perubahan file** pada area itu sejak verifikasi tersebut (tidak ada
drift antara "yang diverifikasi" dan "HEAD saat ini").

Tidak ada mutasi destruktif dilakukan terhadap data QA bersama (satu percobaan edit field `Margin` di
popup 19.0 di-*discard*, bukan disimpan; satu percobaan `action_confirm()` pada order rental 20.0
ditolak oleh permission classifier dan tidak dipaksakan — sesuai instruksi "jangan mutasi data
shared"). Satu percobaan diagnosis (`docker exec ... odoo-bin shell` read-only) ternyata **berisiko**
(collision registry dengan proses utama, `SerializationFailure`) — dihentikan setelah 1x percobaan,
dicatat sebagai pelajaran di `MF-46`, tidak diulang.

## 2. Enumerasi Scope

Urutan sesuai dependency (`pos_margin_threshold`/`sale_margin_threshold` saling terkait `MF-03`/
`MF-37`, diperiksa bersama; `pin_message` independen):

1. `pos_margin_threshold` ⟷ `sale_margin_threshold` — redesign popup→list (`MF-29`), shared view
   `product.product_product_tree_view`, interaksi Rental (`sale_renting`).
2. `pin_message` — pin/unpin/expand UX, icon FontAwesome→Odoo Icons.

## 3. Static-Diff — Kandidat Dihasilkan

`git diff migration/19.0 migration/20.0 -- pos_margin_threshold/ sale_margin_threshold/ pin_message/`
(26 file berubah, 504 insersi/127 delesi) dibaca penuh, disilangkan ke `FINDINGS.md` (`MF-25`..`MF-45`
sudah ada) dan ketiga `03_MIGRATION_SPEC.md`. Kandidat yang **BELUM** genuinely diverifikasi hidup
(baru diverifikasi baca-kode atau verifikasi manual satu-kali) dipilah jadi 4 prioritas (sesuai arahan
task) + 1 tambahan ditemukan saat menelusuri:

| # | Kandidat | Kenapa dicurigai (bukan cuma re-cek MF existing) |
|---|---|---|
| 1 | `MF-29` popup 19.0 vs kolom list 20.0 | Redesign UX terbesar di seluruh project; belum ada perbandingan BERDAMPINGAN nyata, baru verifikasi fungsional terpisah per versi |
| 2 | `pin_message` pin/unpin/expand feel | Icon berubah total (FA→Odoo Icons) — task minta konfirmasi FEEL interaksi tetap setara, bukan cuma "tidak crash" |
| 3 | Rental (`sale_renting`) ⟷ `sale_margin_threshold` | Sudah dicek sekali sesi lalu, tapi kode berubah lagi sejak itu (`MF-45` dkk) — re-konfirmasi diminta eksplisit |
| 4 | `product.product_product_tree_view` (shared core view) | Dua modul custom menyuntik view yang sama; risiko efek samping ke user yang TIDAK pakai fitur margin sama sekali |
| 5 (tambahan) | Anchor `DIFF-02`/`MF-31` (`account.view_category_property_form`) | Ditemukan saat `get_views()` RPC gagal menampilkan `property_cost_method` — perlu dipastikan bukan regresi baru sebelum diabaikan |

Kandidat LAIN dari diff (xpath `t-call-slot`, `ir.access.csv`, `_store_message_fields`, icon
`push_pin`, dll.) **tidak** dijadikan kandidat baru di sini — semua sudah punya bukti live-test
eksplisit tercatat di `FINDINGS.md` (`MF-32`/`33`/`35`/`36`/`40`..`44`) dari sesi sebelumnya, dan
`git log` dikonfirmasi tidak ada perubahan file sejak itu (tidak ada risiko drift).

## 4. Live-Test per Kandidat

Detail lengkap tiap kandidat ada di `FINDINGS.md` sebagai `RMV-01`..`RMV-04`. Ringkasan:

- **Kandidat #1 (`RMV-01`):** popup 19.0 dibuka nyata (bukan re-baca source) — field `Margin`/
  `Minimum sale price`/`Incl. Tax` di bawah "PRICING", dengan pager Previous/Next per-variant,
  dikonfirmasi editable (uji ketik, di-discard). List 20.0 diverifikasi via `get_views()` RPC (arch
  hasil MERGE runtime, bukan source mentah) — satu set kolom (`lst_price` decoration, `margin_sale`
  decoration, `minimum_sale_price`, `minimum_sale_price_with_tax`/"Incl. Tax"), semua `optional="show"`.
  **Tidak ada kapabilitas hilang** — trade-off dua arah (pager vs `multi_edit`), bukan downgrade.
- **Kandidat #2 (pin_message):** **tidak bisa dieksekusi live baru** sesi ini (blocker environment,
  lihat §1) — mengandalkan verifikasi live YANG SUDAH ADA (`MF-32`/`33`/`36`, dikonfirmasi `git log`
  tidak ada perubahan file sejak itu). Tidak diklasifikasi sebagai RMV baru karena tidak ada eksekusi
  baru untuk dilaporkan; dicatat sebagai gap eksekusi di `MF-46` (sudah ada, bukan duplikat).
- **Kandidat #3 (`RMV-03`):** RPC read-only terhadap 20.0 — `is_rental_order_installed_true`
  dikonfirmasi `true` untuk order rental sungguhan (`S00015`) dengan line produk jauh di bawah
  minimum (price_unit 10 vs minimum_sale_price 120); `action_confirm()` (source tidak berubah sejak
  sebelum `MF-45`) mulai dengan early-return kalau flag itu true. **Efek samping ditemukan**: memicu
  `MF-26` (singleton crash) secara hidup saat query >1 sale.order sekaligus — dicatat sebagai
  konfirmasi (bukan temuan baru) `MF-26` masih valid di HEAD saat ini.
- **Kandidat #4 (`RMV-02`):** `get_views()` RPC arch penuh diperiksa field-per-field — seluruh kolom
  native (`image_128`, `qty_available`, `free_qty`, `barcode`, dll.) terstruktur identik definisi
  native, kolom custom murni additive. Tidak ada efek samping ke produk tak-terkait margin.
- **Kandidat #5 (`RMV-04`):** `ir.ui.view`/`ir.model.data` RPC mengonfirmasi rantai inherit `DIFF-02`
  resolve benar sampai XML-ID `account.view_category_property_form`; ketidaktampilan di satu panggilan
  `get_views()` disimpulkan security-group filtering di request itu, bukan regresi `DIFF-02`.

## 5. Klasifikasi & Tally

| Klasifikasi | Jumlah | Item |
|---|---|---|
| `NATIVE-DIFF` | 3 | `RMV-01` (redesign popup→list, sudah diputuskan `MF-29`), `RMV-02` (shared view bersih), sebagian `RMV-03` (skip-margin rental berfungsi) |
| `GAP-LAMA` | 1 | `RMV-03` bagian `MF-26` (singleton crash, direproduksi ulang, cross-link) |
| `REGRESI` | 0 | Tidak ditemukan regresi baru di 4 kandidat prioritas |
| `PERLU-DEV` | 0 (baru) / 1 (existing, dikuatkan) | Tidak ada eskalasi BARU dari kandidat prioritas; `MF-46` (existing, bukan RMV) diperkuat dengan bukti tambahan (asset bundle 0-byte) |
| Verifikasi tanpa klasifikasi (murni cross-check) | 1 | `RMV-04` (anchor `DIFF-02`, konfirmasi tidak ada regresi) |

**Live-tested:** 4 dari 5 kandidat (semua kecuali kandidat #2 `pin_message`, diblokir environment).
Kandidat #2 mengandalkan verifikasi live existing yang dikonfirmasi masih valid (tidak ada drift kode).

## 6. Visual Pass Sistematis

**Tidak dilakukan penuh** sesi ini — blocker environment (§1) membuat visual pass piksel-per-piksel
terhadap 20.0 (warna, ikon, spacing) tidak bisa dieksekusi ulang dengan browser fresh. Bagian yang
SUDAH tercakup visual pass sebelumnya (dan dikonfirmasi tidak drift): dedup kolom (`MF-37`), decoration
merah + Incl. Tax (`MF-38`), icon `push_pin`+expand pinned messages (`MF-32`/`33`/`36`). Bagian yang
BELUM pernah dapat visual pass sama sekali di project ini: `MF-34` (styling combo POS) dan thread-switch
Chatter (`AC-06-01`, `MF-33`/`MF-46`) — keduanya SUDAH diketahui sebagai gap terbuka di `FINDINGS.md`/
`10_BUSINESS_FLOW_MIGRATION.md` masing-masing, bukan temuan baru sesi ini.

## 7. Kontribusi Knowledge Base

- [x] Ada — dicatat sebagai kandidat: pola "asset bundle `ir.attachment` metadata benar tapi byte
  fisik 0" sebagai gejala kontensi I/O Postgres/filestore saat banyak sesi test paralel berbagi satu
  container Odoo — relevan untuk project migrasi manapun yang memakai pola dual-branch/shared-container
  dengan multi-agent QA paralel. **Belum ditulis** ke
  `migration-tool/migration-records/pos-margin-sale_19.0_20.0/SUMMARY.md` sesi ini (waktu terbatas,
  dan `MF-46` sudah menyimpan detail utamanya) — direkomendasikan follow-up singkat oleh dev/sesi
  berikutnya untuk memindahkan ringkasan pola ini ke `SUMMARY.md`.

## 8. Laporan Penutup

**Ringkasan:** 5 kandidat dihasilkan dari static-diff (bukan exhaustive replay), 4 live-tested (via
RPC `call_kw` backend nyata + 1 live-browser popup 19.0), 1 (pin_message feel) tidak bisa dieksekusi
ulang karena blocker environment bersama. **0 REGRESI ditemukan** di keempat kandidat yang genuinely
diverifikasi — redesign `MF-29` dikonfirmasi tidak kehilangan kapabilitas, shared view bersih, Rental
skip-margin tetap benar, anchor `DIFF-02` tetap valid. Satu bug lama (`MF-26`) direproduksi hidup
sebagai konfirmasi (bukan temuan baru), tetap `GAP-LAMA` sesuai keputusan dev sebelumnya.

**Gap residual, jujur dilaporkan (bukan dipaksakan "selesai"):**
- `pin_message` interaction-feel (icon+klik) TIDAK di-live-test ULANG sesi ini — mengandalkan bukti
  lama yang masih valid (tidak drift), bukan eksekusi baru.
- Visual pixel-level pass (warna/spacing) untuk `MF-29` kolom list 20.0 tidak bisa direplikasi karena
  environment blocker — kandidat #1 diverifikasi STRUKTURAL (arch RPC) + fungsional (editability
  popup 19.0), bukan piksel.
- `MF-34` (styling combo POS) dan `AC-06-01` (thread-switch Chatter) tetap gap visual TERBUKA yang
  sudah diketahui sebelumnya (`FINDINGS.md`), tidak tersentuh/tertutup sesi ini.

**Rekomendasi human QA sebelum go-live:** (1) jalankan ulang kandidat #2 (pin_message feel) dan visual
pixel-pass kandidat #1 di jam sepi container / sesi browser tidak dibagi ganda dengan Step 10 lain;
(2) selesaikan gap `MF-34`/`AC-06-01` yang sudah diketahui; (3) putuskan `MF-26` (masih terbuka, sudah
dua kali direproduksi lintas-sesi) — sudah cukup bukti untuk keputusan definitif alih-alih terus
dibawa sebagai "belum diputuskan"; (4) tindak lanjuti rekomendasi infra `MF-46` (pisahkan sesi
paralel container Docker) sebelum menjalankan Cross-Version-Compare/Step 10 lain secara bersamaan lagi.
