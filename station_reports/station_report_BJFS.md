# IGS / MGEX Station Report: **BJFS**

Generated: 2026-05-01 01:04 UTC  
Status files date: **2026-01-15 (DOY 015)**  (GPS Week 2401, Day 5)

---

## 1. Data Availability

| Status file | Result |
|-------------|--------|
| `26015_status.txt` (RINEX v2) | ✅ Data found |
| `26015_V3status.txt` (MGEX v3) | ❌ Station listed — no data submitted |

## 2. Station Identity

| Field | Value |
|-------|-------|
| 4-char ID | `BJFS` |
| Full RINEX3 ID | `BJFS00???` |
| Marker name | 21601M001 |
| DOMES number | M |
| Type | `X` — M = Multi-constellation, G = GPS-only |
| Receiver | `NETR9        TRM5990` |
| Antenna | `.00     SCIS BJFS` |

> **Receiver:** ⚠️ Check manufacturer specs for geodetic suitability
> **Antenna:** Verify `.00     SCIS BJFS` exists in `igs20.atx`. Missing entry → systematic 1–3 cm height error.

## 3. Data Quality Metrics (RINEX v2 QC)

| Metric | Value | Grade | What it means for PPP |
|--------|-------|-------|------------------------|
| Delivery delay | 10h 0m | ⚠️ Late | Late data misses rapid products window |
| Observations | 24,325 / 24,593 | 99% | ✅ Full day |
| Points deleted | 268 | — | Removed by QC (multipath / noise) |
| L1 Multipath (MP1) | 0.37 m | ✅ Good | Signal bouncing off surroundings |
| L2 Multipath (MP2) | 0.25 m | ✅ Good | L2 frequency environment |
| Cycle slips | 7 | ✅ Clean | Phase breaks — too many = noisy PPP |
| Quality flag | V=1 (Good) | ✅ | Minor issues, still fully usable for PPP |

## 4. Constellation / Signal Coverage

> **Why this matters:** More constellations = more satellites = better geometry = faster PPP convergence.
> GPS-only: ~8–12 sats. GPS+Galileo+BeiDou: ~30–40 sats visible simultaneously.

| System | Code | Available | PPP Contribution |
|--------|------|-----------|-----------------|
| GPS (USA) | `G` | ✅ YES | Essential — core of all PPP processing |
| GLONASS (Russia) | `R` | ✅ YES | Adds geometry; needs GLONASS-specific products |
| Galileo (EU) | `E` | — no | Reduces convergence 30–40%; excellent clock stability |
| BeiDou (China) | `C` | — no | Adds 10–15 satellites in Asia; key for multi-GNSS studies |
| QZSS (Japan) | `J` | — no | Supplements GPS in Japan / Asia-Pacific region |
| SBAS | `S` | — no | SBAS — not used in PPP (navigation augmentation only) |
| NavIC (India) | `I` | — no | NavIC — regional (India); rarely in PPP products yet |

> ⚠️  **Why is the file small?**
> This station tracks only GPS + GLONASS.
> A full multi-GNSS station (G+R+E+C) has ~30–40 satellites → ~40 MB/day uncompressed.
> A GPS+GLONASS station has ~15–20 satellites → **~12–18 MB/day** — roughly half the size.
> For larger multi-GNSS files, choose a station with Galileo (E) and BeiDou (C) coverage.

## 5. File Names and Download URLs

### RINEX v3 observation file
```
BJFS00???_R_20260150000_01D_30S_MO.rnx.gz
```
URL: `https://cddis.nasa.gov/archive/gnss/data/daily/2026/015/26d/BJFS00???_R_20260150000_01D_30S_MO.rnx.gz`

### RINEX v2 observation file (alternative / fallback)
```
bjfs0150.26o.gz
```
URL: `https://cddis.nasa.gov/archive/gnss/data/daily/2026/015/26o/bjfs0150.26o.gz`

### MD5 Checksum — verify after download
```bash
md5sum BJFS00???_R_20260150000_01D_30S_MO.rnx.gz
# Expected: 4ab92c3a5eb78dd457035d4f672af460
```

## 6. PPP Suitability Assessment

### → GOOD — suitable for PPP, ready to use

**Strengths:**
- ✅ GPS tracking confirmed
- ✅ GLONASS: adds geometry diversity
- ✅ 99% data completeness — full day available
- ✅ Low multipath (0.31 m) — clean signal environment
- ✅ Low cycle slips (7) — clean carrier phase
- ✅ Data quality flag V=1 (Good)

**Issues / Cautions:**
- ⚠️  No Galileo — convergence will be slower (GPS-only ~20–40 min)

## 7. Files Required Per Tool

| Tool | Mode | Required Files | Expected Accuracy |
|------|------|----------------|-------------------|
| **RTKLib** | Broadcast PPP | `.rnx obs` + `.rnx nav` | ~1–3 m |
| **RTKLib** | Precise PPP | obs + nav + `.SP3` + `.CLK` + `igs20.atx` | ~5–10 cm |
| **DEMO5** | PPP-AR | Same as RTKLib precise + `.BIA` (OSB) | ~1–3 cm |
| **GAMP** | Multi-GNSS PPP | obs + nav + `.SP3` + `.CLK` + `.ERP` + `.BSX/.DCB` + `igs20.atx` + `.blq` | ~2–5 cm |
| **PRIDE PPP-AR** | PPP-AR | obs only (pdp3 auto-downloads rest) | ~1–3 cm |

> **DEMO5 location:** See Part 10 of the PPP Complete Guide for running both RTKLib
> and DEMO5 from the same `Program Files` folder.

## 8. Quick-Start Processing Commands

### A) RTKLib — broadcast only (simplest, lowest accuracy)
```
RTKPOST settings:
  Rover:      BJFS00???_R_20260150000_01D_30S_MO.rnx
  Nav:        BRDM00DLR_R_20260150000_01D_MN.rnx
  Mode:       PPP-Static
  Ephemeris:  Broadcast
  Expected:   ~1–3 m accuracy
```

### B) RTKLib / DEMO5 — precise PPP
```
RTKPOST settings:
  Rover:      BJFS00???_R_20260150000_01D_30S_MO.rnx
  Nav:        BRDM00DLR_R_20260150000_01D_MN.rnx
  SP3:        IGS0OPSFIN_20260150000_01D_15M_ORB.SP3
  CLK:        IGS0OPSFIN_20260150000_01D_30S_CLK.CLK
  ATX:        igs20.atx
  Mode:       PPP-Static | Ephemeris: Precise
  Expected:   ~2–5 cm after 20–40 min convergence
```

### C) GAMP — full multi-GNSS PPP
```ini
# gamp.cfg key settings:
posmode   = 7          # PPP-Static
navsys    = 45         # GPS+GLO+GAL+BDS (use 1 for GPS-only)
ionoopt   = 4          # UC12 uncombined
tropopt   = 3          # estimate ZTD
# obs: BJFS00???_R_20260150000_01D_30S_MO.rnx
# sp3: WUM0MGXFIN_20260150000_01D_15M_ORB.SP3
# clk: WUM0MGXFIN_20260150000_01D_30S_CLK.CLK
# erp: IGS0OPSFIN_20260150000_01D_01D_ERP.ERP
# dcb: CAS0MGXRAP_20260150000_01D_01D_OSB.BIA
```

### D) PRIDE PPP-AR — highest accuracy
```bash
# Copy your obs file to working directory, then:
pdp3 -m S -sys gec BJFS00???_R_20260150000_01D_30S_MO.rnx
# pdp3 auto-downloads SP3, CLK, BIA, ERP from Wuhan server
# Expected: ~1–3 cm, ambiguity fixed within 5–15 min
```

---
_Report for station BJFS — generated by check_station.py_