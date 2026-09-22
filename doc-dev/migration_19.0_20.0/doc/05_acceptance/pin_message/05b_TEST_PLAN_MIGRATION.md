# Test Plan (Migrasi) — pin_message

**Step:** 5 — Acceptance Criteria & Test Plan (satu paket dengan `05a_MIGRATION_ACCEPTANCE_CRITERIA.md`)
**Ref:** `05_acceptance/pin_message/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-09-22

---

## Konteks penting sebelum tabel — status test existing di modul ini

Modul ini punya suite test yang **sudah ada** (bukan perlu ditulis dari nol) dan sudah beberapa kali
dijalankan smoke-test manual di Docker 20.0 sesi ini:

- `tests/test_pin_message.py` (`TransactionCase`) — 3 method, isi genuinely berisi assertion (bukan
  stub, dikonfirmasi baca langsung): `test_toggle_pin_sets_true`, `test_toggle_pin_sets_false_when_already_pinned`,
  `test_toggle_pin_multi_record_safe`.
- `tests/test_pin_message_tour.py` (`HttpCase`) — 2 method, masing-masing menjalankan satu tour dari
  `static/tests/tours/pin_message_tour.js`: `test_pin_message_toggle_pin_tour` (tour
  `pin_message_toggle_pin_tour` — pin via tombol inline, **termasuk step expand section + cek card
  muncul**, lalu unpin) dan `test_pin_message_action_menu_pin_visible_tour` (tour
  `pin_message_action_menu_pin_visible_tour` — pin via action-menu "...").

**Temuan penting soal tour existing (relevan untuk `MF-36`):** tour `pin_message_toggle_pin_tour`
SUDAH punya step "expand the Pinned Messages section" + assertion "a message card is listed inside
the expanded section" (baris 43-52 `pin_message_tour.js`) — step ini sudah ada sejak migrasi
18.0→19.0 (`git log` menunjukkan step ini eksis sebelum commit branch-point `5876d01`), hanya
selector-nya yang diupdate sesi ini (`DIFF-04`). **Kalau tour ini benar-benar DIJALANKAN sebagai test
otomatis (`odoo-bin --test-tags`), harusnya sudah menangkap crash `MF-36`** (expand akan gagal karena
`MessageCardList` throw `TypeError` saat render, step tour akan timeout/fail). Namun `MF-36` justru
ditemukan lewat **smoke-test manual via browser di Docker**, bukan lewat menjalankan suite test
otomatis — mengindikasikan `test_pin_message_tour.py` **belum pernah benar-benar dieksekusi** untuk
pasangan 19.0→20.0 ini (konsisten status tabel `CLAUDE.md`: Step 9 masih ⬜ Belum mulai). Implikasi:
begitu Step 9 formal dimulai dan suite ini dijalankan sungguhan, `MF-36` (sudah RESOLVED di kode)
seharusnya lolos — tapi ini harus **dibuktikan dengan menjalankan test-nya**, bukan diasumsikan dari
fakta bahwa fix sudah diterapkan dan diverifikasi manual satu kali.

**Yang genuinely TIDAK tercakup tour existing manapun** (dikonfirmasi baca `pin_message_tour.js`
baris demi baris):
1. **Klik tombol "See"/jump** (`onClickJump`, AC-04-02) — tour berhenti setelah card muncul di
   section expanded, tidak pernah klik tombol "See" untuk memverifikasi scroll+highlight ke pesan
   asli.
2. **Thread-switch / ganti record** (AC-06-01, `MF-33` sisa risiko) — tidak ada tour yang membuka
   chatter di satu record, pin pesan, lalu pindah ke record LAIN untuk verifikasi refresh section.
   Ini dikonfirmasi eksplisit sebagai item terbuka di
   `06_implementation/pin_message/06c_IMPLEMENTATION_LOG.md` §"Belum diterapkan / masih terbuka".

Kedua gap ini adalah AC dengan risiko tertinggi di `05a` (AC-04-02, AC-06-01) — **rekomendasi step
9 di bawah bukan re-run test yang ada, tapi PERLUASAN tour existing** untuk menutup dua celah ini.

---

## Step 9 — Dev Testing

> Eksekusi: **otomatis/background** — `odoo-bin -i pin_message --test-enable --test-tags
> /pin_message --stop-after-init`. Termasuk tour Owl/JS (`HttpCase.start_tour`) karena Fase E (JS)
> applicable untuk modul ini.
>
> **Audit isi test disarankan** sebelum menganggap kolom di bawah sebagai "cakupan penuh" (lihat
> peringatan template `USAGE_GUIDE.md` §5) — untuk modul ini SUDAH dilakukan di atas: ketiga method
> `test_pin_message.py` dikonfirmasi berisi assertion nyata (bukan stub), kedua method
> `test_pin_message_tour.py` dikonfirmasi memanggil tour yang genuinely berisi step interaktif.

| AC | Deskripsi | Unit | Integration | Tour (Owl/JS) |
|---|---|---|---|---|
| AC-01-01, AC-01-02 | Toggle pin/unpin single record | `test_toggle_pin_sets_true`, `test_toggle_pin_sets_false_when_already_pinned` | — | — |
| AC-01-03 | Toggle pin multi-record safe (kontras `MF-08`) | `test_toggle_pin_multi_record_safe` | — | — |
| AC-01-04 | `is_pinned` muncul di payload store (`MF-28`) | — | Perlu ditambah: assertion langsung ke payload `_store_message_fields`/`Store` (bisa lewat `TransactionCase` + inspeksi `Store` object, BUKAN cuma lewat tour) — **belum ada test unit/integration eksplisit untuk ini**, hanya diverifikasi manual browser sesi ini | `pin_message_toggle_pin_tour` (implisit — badge count 1 muncul membuktikan field terkirim, tapi tidak eksplisit assert payload) |
| AC-02-01, AC-02-02, AC-02-03 | Dua entry-point pin (action-menu vs inline), dead code `is_discussion` | — | — | `pin_message_toggle_pin_tour` (inline), `pin_message_action_menu_pin_visible_tour` (action-menu). Cabang `is_discussion=True` (dead code, AC-02-01) TIDAK ditest — konsisten karena memang tidak pernah tereksekusi di praktik, dianggap cukup |
| AC-02-04, AC-02-05 | Visibility & render entry "Pin" (`MF-32`) | — | — | `pin_message_action_menu_pin_visible_tour` |
| AC-03-01, AC-03-02, AC-03-03 | Section Pinned Messages: visibility, badge, collapse/expand | — | — | `pin_message_toggle_pin_tour` (badge count, expand step) |
| AC-03-04 | Error handling `initialLoad()` gagal | — | **Tidak ada test** — perlu skenario `orm.searchRead` di-mock gagal untuk verifikasi try/catch silent; risiko rendah (perilaku non-obvious tapi tidak fungsional kritis), boleh ditunda ke Step 10 manual kalau effort tour terlalu tinggi | — |
| **AC-04-01** | Expand section TANPA crash (`MF-36`) — **RISIKO TERTINGGI** | — | — | `pin_message_toggle_pin_tour` (step "expand" + assertion card muncul) — **SUDAH ADA di kode tour, TAPI belum pernah dijalankan sungguhan untuk 20.0 (lihat catatan di atas) — WAJIB dijalankan sebagai bagian gate Step 9, jangan skip** |
| **AC-04-02** | Klik tombol "See"/jump (`onClickJump`) | — | — | **TIDAK ADA — perlu ditambahkan** ke `pin_message_toggle_pin_tour` (atau tour baru): step lanjutan setelah card muncul, klik `.o-mail-MessageCardList .card [tombol See]`, assert scroll/highlight terjadi ke pesan di thread utama |
| AC-05-01, AC-05-02, AC-05-03 | Ikon `push_pin`, state warna muted/primary (`DIFF-04`) | — | — | `pin_message_toggle_pin_tour` (selector `i[data-icon='push_pin'].text-muted`/`.text-primary` sudah jadi trigger step, implisit verifikasi visual lewat keberhasilan klik) |
| AC-05-04 | CSS kosmetik section pinned | — | — | Tidak ditest otomatis (murni visual) — cukup Step 10 manual/AI-interaktif |
| **AC-06-01** | Refresh section saat ganti thread (`MF-33` sisa risiko) — **RISIKO TERTINGGI, WAJIB SEBELUM GATE** | — | — | **TIDAK ADA — WAJIB ditambahkan** sebelum Step 6 fase E ditutup formal (syarat eksplisit `03_MIGRATION_SPEC.md` §1 butir 4/§2b). Skenario: buka chatter record A, pin 1 pesan, navigasi form ke record B (bukan reload), assert section Pinned Messages kosong/sesuai B, bukan sisa data A |

**Rekomendasi konkret Step 9 untuk pin_message (bernomor, untuk dev jalankan):**
1. Jalankan suite test yang SUDAH ADA dulu, sungguhan, di Docker 20.0:
   `odoo-bin -i pin_message --test-enable --test-tags /pin_message --stop-after-init` — ini akan
   jadi bukti pertama kali tour `pin_message_toggle_pin_tour` benar-benar dieksekusi otomatis untuk
   pasangan 19.0→20.0 (sejauh ini `MF-36` hanya diverifikasi manual). Kalau lolos, itu bukti kuat
   AC-04-01 genuinely fixed, bukan cuma "diverifikasi sekali secara manual".
2. Tambahkan step baru ke `pin_message_toggle_pin_tour` (atau tour terpisah) untuk klik tombol "See"
   (AC-04-02) — setelah step "a message card is listed inside the expanded section"
   (`pin_message_tour.js` baris 48-52), tambah step klik tombol jump + assertion highlight/scroll ke
   pesan asli.
3. Tulis tour BARU "pindah thread" (AC-06-01, `MF-33`) — buka chatter di record A (mis. partner A),
   log note + pin 1 pesan, navigasi ke record B via breadcrumb/search (BUKAN reload record A),
   assert `.o-mail-PinnedMessages` TIDAK ada (record B tidak punya pesan pinned) atau badge sesuai B.
   Tambahkan companion method `test_*` baru di `test_pin_message_tour.py`.
4. Setelah #2 dan #3 ditulis dan lolos, gate Step 6 fase E untuk modul ini baru bisa ditutup formal
   sesuai syarat `03_MIGRATION_SPEC.md`.

---

## Step 10 — QA Testing

> Satu mode per AC/skenario. AC yang sudah tercakup tour Step 9 (di atas) TIDAK diulang di sini
> kecuali untuk verifikasi visual murni yang tour tidak bisa nilai (warna, estetika).

| AC | Deskripsi | Manual | AI-interaktif | AI+tool eksternal (ref script) |
|---|---|---|---|---|
| AC-05-01..04 | Verifikasi visual ikon `push_pin` + warna state + styling card (bukan cuma "elemen ada", tapi "terlihat benar secara visual") | — | ✅ Claude in Chrome: buka chatter, pin/unpin, screenshot bandingkan ikon & warna ke referensi 19.0 | — |
| AC-04-01, AC-04-02 | Regression visual expand + jump (setelah tour Step 9 lolos) — cek sekali lagi via browser nyata sebagai sanity-check independen dari tour | ✅ dev/QA klik manual sebagai second-check sebelum gate Step 8/9 ditutup | — | — |
| AC-06-01 | Thread-switch — sanity-check visual TAMBAHAN setelah tour baru (Step 9 rekomendasi #3) lolos, uji minimal 2 record pasangan berbeda (mis. dua Product berbeda, atau Product → Sale Order) untuk variasi model | ✅ dev/QA klik manual | — | — |
| AC-02-01 (dead code `is_discussion`) | Pastikan tidak ada regresi ke pin native Discuss-channel akibat modul ini (§2b Risiko Integrasi `03_MIGRATION_SPEC.md`) | — | ✅ buka Discuss, pin/unpin pesan channel via action native `"pin"`/`"unpin"`, pastikan tidak collide dengan action "pins" modul ini | — |
| AC-03-04 | Error handling `initialLoad()` gagal (kalau tidak ditest otomatis di Step 9) | ✅ simulasi manual (matikan network sebentar di DevTools saat buka chatter) — opsional, risiko rendah | — | — |

---

## Step 11 — UAT

| Kelompok fitur | AC tercakup | UAT |
|---|---|---|
| Pin/unpin dasar (dua entry-point) | AC-01-01..04, AC-02-01..05 | Business user log note pada record apapun (partner/product/dsb), pin via kedua cara ("..." menu dan tombol inline), pastikan behavior identik ke 19.0 |
| Section Pinned Messages (visibility, badge, expand, jump) | AC-03-01..04, AC-04-01..02 | Business user pin beberapa pesan, expand section, klik "See" untuk lompat ke pesan asli — pastikan TIDAK ada crash/freeze (ini yang paling penting untuk sign-off, mengingat `MF-36` sempat crash total di area ini) |
| Ikon & tampilan visual | AC-05-01..04 | Business user bandingkan tampilan ikon pin (warna, bentuk) side-by-side dengan versi 19.0 kalau memungkinkan |
| Ganti thread/record | AC-06-01 | Business user buka chatter di satu record, pin pesan, pindah ke record lain, pastikan section Pinned Messages ikut berganti sesuai record aktif (bukan menampilkan data record sebelumnya) |
| Discuss-channel native (non-regression) | AC-02-01 (konteks) | Business user pastikan fitur pin bawaan Discuss-channel (bukan buatan modul ini) tetap berfungsi normal berdampingan |

---

## Ringkasan

| Step | Role | Tipe | Eksekusi | Jumlah AC |
|---|---|---|---|---|
| 9 | Developer | Unit/Integration/Tour (Owl/JS) | Otomatis/background — **2 tour baru wajib ditulis dulu (AC-04-02, AC-06-01) sebelum gate Step 6/9 dianggap tuntas** | 17 AC (05a) |
| 10 | QA | Manual/AI-interaktif | Fokus regresi visual + sanity-check independen area risiko tinggi | 5 baris skenario |
| 11 | PM/FA/User | UAT | Manual (selalu) — 5 kelompok fitur | Mencakup seluruh 17 AC |

---

## Flag non-blocking untuk perhatian dev (ringkas, sesuai instruksi Step 5)

1. **AC-04-02 (tombol jump/"See") dan AC-06-01 (thread-switch)** — dua AC berisiko tertinggi di
   modul ini (`MF-36` residual + `MF-33` residual), keduanya **belum ada test otomatis** meski
   fix kodenya sudah diterapkan dan diverifikasi manual sekali. Rekomendasi konkret di §Step 9 di
   atas (poin 2 & 3).
2. **AC-01-04** (`is_pinned` di payload store, `MF-28`) tidak punya assertion integrasi eksplisit
   yang membaca payload `Store` — hanya diverifikasi tidak langsung lewat tour (badge count muncul).
   Risiko rendah untuk regresi lanjutan (fix sudah mekanis & terverifikasi), tapi dicatat untuk
   kelengkapan.
3. **Tour `pin_message_toggle_pin_tour` sudah punya step expand yang relevan untuk `MF-36`**, tapi
   berdasarkan git history dan implementation log, tour ini kemungkinan **belum pernah benar-benar
   dieksekusi otomatis** untuk pasangan 19.0→20.0 — menjalankannya sungguhan adalah langkah pertama
   Step 9 yang paling murah dan paling penting untuk modul ini.
4. Tidak ada `BSL-NNN` yang gagal dipetakan ke AC manapun di `05a` — traceability penuh 17/17.
