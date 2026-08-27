# Business Flow — Migrasi pin_message

**Step:** 10 — QA Testing (gate)
**Ref:** `05_acceptance/pin_message/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-08-27

> Port kode saja, tidak ada instance produksi — dijalankan sebagai install bersih, konsisten dengan
> Step 7 N/A.

**Mode eksekusi dipilih:** AI+tool eksternal — Playwright (Node.js, headless Chromium), bukan
Claude Browser MCP internal (gagal total di environment ini) dan tidak ada Claude in Chrome
terhubung. Script: scratchpad `playwright-qa/qa_step10.js` (tidak dicommit). Server: Docker
`docker-env/` (Mode G2-live, `odoo:19.0`, db `pos_margin_sale_migration_19_qa`, port `8079`).

Modul ini adalah risiko TERTINGGI di seluruh project (`MF-14`/`15`/`18`). AC paling kritis
(`AC-02-01/02`, `AC-04-02`) sudah tercover Tour test Step 9 dan **tidak diulang di sini**. Fokus
Step 10: 2 gap carry-forward yang memang direncanakan untuk step ini sejak Step 5/9 —
Discuss-channel native pin (dead code path modul ini tidak mengganggu) dan reload round-trip.

---

### S-10-01: Discuss-channel native pin — dead code modul ini tidak mengganggu
**Level:** Negative
**Precondition:** Channel `general` ada, user admin jadi member.
**Mode eksekusi:** AI+tool eksternal (Playwright, `qa_step10.js` — skenario S-10-01)
**Steps:**
1. Buka Discuss > channel `general`.
2. Kirim pesan baru.
3. Hover pesan, klik aksi pin native (via menu "Expand"/ikon pin bawaan `mail`).
4. Amati: tidak ada JS error, cabang `is_discussion` dead code di `onClickPin()` modul
   `pin_message` tidak pernah tereksekusi/mengganggu jalur native.
**Expected:** Pin native `mail` berfungsi penuh, tidak ada `pageerror`/console error yang berasal
dari `pinMessage.js` — per `AC-05-01`.
**Actual:** Pin berhasil diklik tanpa error pada 2 pesan berbeda (badge pin muncul di sebelah nama
"Administrator", screenshot `shot_04_discuss_after_pin_attempt.png`). Total console error selama
seluruh run (6 skenario): **0**.
**Status:** [x] Pass / [ ] Fail
**Provenance:** [DIKONFIRMASI]

---

### S-10-06: Reload round-trip — status pin tidak bocor antar thread
**Level:** Detail
**Precondition:** Ada 1+ pesan ter-pin di channel `general` (hasil S-10-01).
**Mode eksekusi:** AI+tool eksternal (Playwright, `qa_step10.js` — skenario S-10-06)
**Steps:**
1. Di channel `general`, catat jumlah ikon pin pada pesan yang baru di-pin.
2. Pindah ke channel lain (`Administrators`).
3. Kembali ke channel `general`.
4. Hitung ulang jumlah ikon pin pada pesan yang sama.
**Expected:** Jumlah ikon pin identik sebelum dan sesudah pindah-kembali thread — tidak ada state
`is_pinned` yang bocor/hilang/tercampur antar thread, per `AC-06-01`.
**Actual:** Ikon pin = 1 sebelum pindah, tetap 1 setelah kembali ke `general`. Screenshot:
`shot_16_discuss_other_channel.png`, `shot_17_discuss_back_to_general.png`.
**Status:** [x] Pass / [ ] Fail
**Provenance:** [DIKONFIRMASI]

**Catatan gap tertutup:** `AC-05-01` dan `AC-06-01` sebelumnya berstatus gap carry-forward sejak
project 17→18 (belum pernah dieksekusi otomatis) — keduanya sekarang genuinely dieksekusi live
untuk versi 19.0, memberi lapis verifikasi tambahan untuk modul risiko tertinggi di project ini
(total kini: Step 2 baca kode, Step 6 G2 Tour test, Step 8 code review, Step 10 QA interaktif — 4
lapis independen semua konsisten mengonfirmasi fix `MF-14`/`15`/`18` benar & tidak ada regresi baru).

## Ringkasan per Level

| Level | Skenario | Jumlah |
|---|---|---|
| Smoke | — | 0 |
| Main Flow | — | 0 |
| Detail | S-10-06 | 1 |
| Negative | S-10-01 | 1 |

## Rekap Provenance

| Provenance | Jumlah | Skenario |
|---|---|---|
| `[DIKONFIRMASI]` | 2 | S-10-01, S-10-06 |
| `[HASIL-BACA]` | 0 | — |
| `[PERLU-KEPUTUSAN]` | 0 | — |

## Loop-back

Tidak ada skenario Fail — tidak perlu loop-back ke Step 9.

## Verdict

- [x] ✅ Lulus — lanjut ke step 11
