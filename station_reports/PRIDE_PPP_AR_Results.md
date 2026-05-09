# PRIDE-PPP-AR v3.x Results Analysis

## All Stations: KIRU, WUH2, HKWS, ZIM2 | Date: 2026-01-15 (DOY 015)

> **Software:** PRIDE-PPP-AR v3.x (Windows GUI, `C:\PRIDE\PRIDE_PPPAR.exe`)  
> **Products:** CODE Multi-GNSS Final (COD0MGXFIN) — SP3, CLK, ERP, OBX, OSB  
> **Mode:** Static PPP — single daily ECEF position estimate  
> **GNSS:** GPS + Galileo + BDS-3 (GLONASS disabled)  
> **Reference frame:** IGS20 (via COD0MGXFIN products)

---

## 1. Processing Configuration

| Parameter                | Value                                                             |
| ------------------------ | ----------------------------------------------------------------- |
| Session                  | 2026-01-15, 00:00:00 – 23:59:30 UTC (86370 s)                     |
| Interval                 | 30 seconds                                                        |
| Elevation cutoff (tedit) | 7° (preprocessing); 15° (config)                                  |
| Troposphere model        | Stochastic (STO) with PWC horizontal gradient (720 min)           |
| Tide corrections         | Solid Earth, Ocean loading, Pole tides                            |
| Orbit                    | COD0MGXFIN 5-min SP3                                              |
| Clock                    | COD0MGXFIN 30-sec CLK                                             |
| ERP                      | COD0MGXFIN 12-hour ERP                                            |
| Attitude                 | COD0MGXFIN 30-sec OBX                                             |
| Bias                     | COD0MGXFIN daily OSB (observable-specific biases)                 |
| Antenna model            | igs20_2401.atx (IGS20 absolute ANTEX)                             |
| Ambiguity resolution     | Wide-Lane + Narrow-Lane (WL+NL) fixing                            |
| Ambiguity duration min   | 600 seconds (10-minute arcs required)                             |
| PPP mode                 | **Static** (batch least-squares, one position for the full day)   |
| GNSS enabled             | G01–G32, E01–E36, C06–C61 (BDS MEO/IGSO only, no GEO C01–C05)     |
| GLONASS                  | Disabled (all commented out, inter-frequency biases not provided) |

### Why Static PPP?

PRIDE-PPP-AR uses a **batch least-squares estimator** that treats the entire observation session as one solution. This is fundamentally different from RTKLIB's epoch-by-epoch kinematic Kalman filter. Static PPP produces a single high-precision ECEF coordinate for the day, ideal for:

- Geodetic reference station monitoring
- Long-term crustal deformation studies
- Verification of IGS frame coordinates
- Comparison between PPP algorithms and software

---

## 2. Run History and Diagnostic Log

### 2.1 Processing Timeline

| #   | Station | AR  | Start    | End    | Status       | Notes                                                  |
| --- | ------- | --- | -------- | ------ | ------------ | ------------------------------------------------------ |
| 1   | KIRU    | N   | ~11:48   | ~11:49 | ❌ FAILED    | sat_parameters EOF error (file truncated at 356 lines) |
| 2   | ZIM2    | N   | ~21:23   | ~21:23 | ❌ FAILED    | SP3 file not found (working dir not initialized)       |
| 3   | ZIM2    | N   | ~21:23   | ~21:30 | ✅ SUCCEEDED | 7 lsq/redig iterations, fully converged                |
| 4   | WUH2    | N   | ~22:06   | ~22:06 | ❌ FAILED    | SP3 file not found (same pattern as ZIM2 #2)           |
| 5   | WUH2    | N   | ~22:06   | ~22:12 | ✅ SUCCEEDED | 7 lsq/redig iterations, fully converged                |
| 6   | KIRU    | N   | ~22:16   | ~22:22 | ✅ SUCCEEDED | Post-fix run; 7 lsq/redig iterations                   |
| 7   | HKWS    | N   | ~22:25   | ~22:27 | ✅ SUCCEEDED | Only 4 iterations needed — cleanest station            |
| 8   | HKWS    | Y   | ~22:32   | ~22:35 | ✅ SUCCEEDED | AR fixed; WL=84.9%, NL=100%                            |
| 9   | WUH2    | Y   | ~22:39   | ~22:47 | ✅ SUCCEEDED | AR fixed; WL=89.0%, NL=97.7%                           |
| 10  | KIRU    | Y   | ~22:17\* | ~23:16 | ✅ SUCCEEDED | AR fixed; WL=98.1%, NL=99.7% — best AR performance     |
| 11  | ZIM2    | Y   | ~23:23   | ~23:23 | ❌ FAILED    | sat_parameters truncated AGAIN (436 lines)             |
| 12  | ZIM2    | Y   | 00:03    | 00:09  | ✅ SUCCEEDED | Post-fix run; WL=88.1%, NL=100.0%, 86 ind. ambiguities |

\*KIRU AR=Y was the longest run, processing ~1040 ambiguities in a dense satellite environment.

### 2.2 Error Diagnosis: Repeated sat_parameters Failures

#### Error 1 — KIRU AR=N (First Attempt)

```
***ERROR(read_glschn): end of file sat_parameters
```

**Root cause:** `C:\PRIDE\table\sat_parameters` was truncated at 356 lines, cutting off mid-BeiDou entry (`C01  C020`). The `tedit.exe` binary scans the entire `+prn_indexed` block to load satellite parameters (mass, orbit type, GLONASS FCN). When it hits EOF before finding the `-prn_indexed` closing tag, it throws this error.

**Fix:** Downloaded complete file (397 lines, ends with `-prn_indexed`) from the PRIDE-PPPAR GitHub repository. File was backed up as `sat_parameters.bak`. All subsequent AR=N runs succeeded.

#### Error 2 — ZIM2/WUH2 SP3 Not Found (First Attempts)

```
error: PrepareProducts: no such sp3 file: COD0MGXFIN_20260150000_01D_05M_ORB.SP3
```

**Root cause:** PRIDE's `PrepareProducts` step (runs `sp3orb.exe`) requires the `2026/015/` working directory to already exist with auxiliary table files. On the **first** run for each station, `PrepareTables` has not yet created this directory structure. Without the directory, `sp3orb` cannot write its output and fails.

**Pattern:** Every station's first run fails; the second run succeeds because `PrepareTables` now finds existing auxiliary files:

```
PrepareTables: C:/PPP_PROJECT/PRIDE_work/runs/ZIM2_run/2026/015/file_name exists
PrepareTables: C:/PPP_PROJECT/PRIDE_work/runs/ZIM2_run/2026/015/oceanload exists
...
```

**Fix:** Simply re-run the same configuration from the PRIDE GUI. No action needed.

#### Error 3 — ZIM2 AR=Y (sat_parameters corrupted again)

```
***ERROR(read_glschn): end of file sat_parameters
```

**Root cause:** The `sat_parameters` file was overwritten between KIRU AR=Y completing (~23:16) and ZIM2 AR=Y starting (~23:23). The replacement file was 436 lines with an incomplete last line (`C45  C223  2019280:00000 2026108:79200 2019-061B  1058` — missing the second half of the line, plus ~20 additional expected BDS entries and the mandatory `-prn_indexed` closing tag).

**Most likely cause:** A newer, larger GitHub version of sat_parameters was partially downloaded during this 7-minute window (possibly a manual download attempt), replacing the known-good 397-line version. The larger file contains additional BDS-3 satellite entries (C43–C45 range) reflecting newer satellites, but the download was truncated.

**Fix (applied):** Backed up the 436-line file as `sat_parameters.bak2`. Downloaded the complete 397-line version fresh from GitHub. Verified it ends with `-prn_indexed`. The sat_parameters file is now correct.

**Re-run needed:** ZIM2 must be re-run:

1. **AR=N first** — to generate the float PPP position
2. **Copy the pos file immediately** after completion (before AR=Y clears it)  
   `Copy-Item "C:\PPP_PROJECT\PRIDE_work\runs\ZIM2_run\2026\015\pos_2026015_zim2" "C:\PPP_PROJECT\PRIDE_work\results\PRIDE\ZIM2_float.pos"`
3. **AR=Y** — to generate the AR-fixed PPP position

### 2.3 Critical Note: AR=Y Overwrites AR=N Position File

**PRIDE-PPP-AR does NOT use separate filenames for float vs AR-fixed output.** Both write to `pos_2026015_SITE`. When AR=Y runs, the `PrepareTables` step reinitializes the working directory, and the final `lsq` call (after ambiguity fixing) **overwrites** the existing `pos_2026015_SITE` file.

Therefore:

- `pos_2026015_hkws` → **AR=Y result** (10:35 PM timestamp)
- `pos_2026015_kiru` → **AR=Y result**
- `pos_2026015_wuh2` → **AR=Y result**
- **ZIM2 float result was lost** when ZIM2 AR=Y started (before it failed)

**Recommendation:** Always copy/rename the AR=N pos file to a separate path before running AR=Y. Example workflow:

```powershell
# After AR=N run completes:
Copy-Item "runs\ZIM2_run\2026\015\pos_2026015_zim2" "results\PRIDE\ZIM2_float.pos"
# Then run AR=Y in GUI. Afterward:
Copy-Item "runs\ZIM2_run\2026\015\pos_2026015_zim2" "results\PRIDE\ZIM2_AR.pos"
```

---

## 3. Data Quality Analysis

### 3.1 Float PPP Cleaning Iterations (AR=N runs)

PRIDE's data cleaning uses 7 successive least-squares + redigitization (lsq/redig) iterations with decreasing outlier thresholds (jmp: 400 → 200 → 100 → 50 → 50 → 50 → 50 mm). Convergence is confirmed when both "Newly removed observations" and "Newly inserted ambiguities" reach zero in the final iteration.

| Station | Iterations | Final removed | Final inserted | Status               |
| ------- | ---------- | ------------- | -------------- | -------------------- |
| ZIM2    | 7          | 0             | 0              | ✅ Fully converged   |
| WUH2    | 7          | 0             | 0              | ✅ Fully converged   |
| KIRU    | 7          | 0             | 0              | ✅ Fully converged   |
| HKWS    | 4\*        | 0             | 0              | ✅ Converged rapidly |

\*HKWS achieved convergence in only 4 iterations. After iteration 3 (jmp=100mm), all residuals were already well below threshold. This indicates very clean observation data — no multipath-affected BDS satellites (none were tracked), minimal outliers. The lsq/redig loop skipped the final redundant iterations automatically.

### 3.2 Final Phase Residuals (AR=N, last iteration)

Phase residuals are the weighted RMS of carrier-phase observation-minus-computed residuals after full convergence. Lower values indicate better data quality and modeling accuracy.

#### HKWS (Hong Kong — cleanest station)

| GNSS              | Typical RMS (mm)   | Notable                                               |
| ----------------- | ------------------ | ----------------------------------------------------- |
| GPS (31 sats)     | 6–13               | G14=13, G30=12 slightly elevated (low elevation arcs) |
| Galileo (25 sats) | 4–11               | E04=4mm excellent, E12=11, E13=11                     |
| BDS               | **No BDS tracked** | HKWS RINEX contains no BDS observations               |

\*Total data usage after editing: **45.9%\*** — PRIDE logged `###WARNING(get_lsq_args): bad observation quality`. This is flagged because a large fraction of observations were removed during the cleaning loop. Despite this, residuals are very clean for the remaining data. The warning does not mean HKWS is "bad" — it means the HKWS RINEX had some format or quality issue requiring heavy editing.

#### ZIM2 (Zimmerwald, Switzerland — reference station)

| GNSS              | Typical RMS (mm) | Notable                                   |
| ----------------- | ---------------- | ----------------------------------------- |
| GPS (31 sats)     | 5–11             | Very uniform; G15=11, G14=10              |
| Galileo (27 sats) | 2–10             | **E18=2mm** — exceptionally clean         |
| BDS (38 sats)     | 6–35             | **C08=35mm** elevated; C12=19mm, C13=18mm |

BDS note: C08 (BDS-3 MEO) shows persistently elevated residuals of 35mm across all iterations. This is likely due to unmodeled satellite-specific phase biases or multipath characteristics for this satellite geometry. C13 (BDS-2 IGSO) is elevated due to its lower orbit and broadcast ephemeris quality. GPS and GAL are excellent.

#### WUH2 (Wuhan, China — multi-constellation environment)

| GNSS              | Typical RMS (mm) | Notable                               |
| ----------------- | ---------------- | ------------------------------------- |
| GPS (31 sats)     | 7–15             | G30=15mm (orbital plane edge effect)  |
| Galileo (27 sats) | 7–24             | E29=24mm elevated (low elevation arc) |
| BDS (38 sats)     | 7–23             | C35=15–23mm, C37=10–14mm              |

\*Total data usage: **73.7%\***. Initial cleaning was aggressive (iteration 1: 151 removed, 305 ambiguities inserted — 211.8%!; iteration 2: 1529 removed). The very large number of observations removed in early iterations reflects the expected behavior for a station tracking many BDS satellites with high initial code residuals (hundreds of mm). After cleaning, quality is good.

#### KIRU (Kiruna, Sweden — high-latitude station)

| GNSS              | Typical RMS (mm) | Notable                                                   |
| ----------------- | ---------------- | --------------------------------------------------------- |
| GPS (31 sats)     | 9–17             | G30=17mm, G31=17mm (sky geometry at high latitude)        |
| Galileo (27 sats) | 8–15             | Slightly higher than ZIM2/HKWS; latitude effect           |
| BDS (38 sats)     | 10–34            | **C08=34mm** (same elevated satellite as ZIM2!), C13=28mm |

\*Total data usage: **78.4%\***. KIRU had the highest data usage of all stations. High-latitude stations generally see more GPS and Galileo satellites but the geometry is different (satellites never pass overhead, always at medium elevations from the south).

Note: C08 shows elevated residuals at **both KIRU and ZIM2** (34–35mm), confirming this is a **satellite-specific issue** with C08 (likely phase bias or broadcast orbit quality for this satellite) rather than a station multipath problem.

---

## 4. Ambiguity Resolution (AR=Y) Statistics

Wide-Lane (WL) ambiguities are fixed first using the Melbourne-Wübbena combination with OSB corrections. Narrow-Lane (NL) ambiguities are then fixed using the ionosphere-free phase with WL-constrained ambiguities. The fix rates measure how many satellite-pair ambiguities were successfully resolved to integers.

### 4.1 AR Fix Rates Summary

| Station  | GPS WL (%)          | GPS NL/WL (%)        | GAL WL (%)          | GAL NL/WL (%)        | **Total WL (%)**      | **Total NL (%)**      | Ind. check     |
| -------- | ------------------- | -------------------- | ------------------- | -------------------- | --------------------- | --------------------- | -------------- |
| **HKWS** | 237/309 = **76.7%** | 237/237 = **100.0%** | 173/174 = **99.4%** | 173/173 = **100.0%** | **410/483 = 84.9%**   | **410/410 = 100.0%**  | 70/70 = 100%   |
| **WUH2** | 241/284 = **84.9%** | 231/241 = **95.9%**  | 188/198 = **94.9%** | 188/188 = **100.0%** | **429/482 = 89.0%**   | **419/429 = 97.7%**   | 75/75 = 100%   |
| **KIRU** | 652/658 = **99.1%** | 650/652 = **99.7%**  | 368/382 = **96.3%** | 367/368 = **99.7%**  | **1020/1040 = 98.1%** | **1017/1020 = 99.7%** | 129/129 = 100% |
| **ZIM2** | 300/368 = **81.5%** | 300/300 = **100.0%** | 210/211 = **99.5%** | 210/210 = **100.0%** | **510/579 = 88.1%**   | **510/510 = 100.0%**  | 86/86 = 100%   |

**Ind. check** = Independent check of fixed ambiguities using geometry-free combination: 100% for all three successful stations confirms the integer values are self-consistent.

### 4.2 Interpretation of AR Results

**KIRU has the best AR performance (98.1% WL, 99.7% NL):**

- 1040 total ambiguities — far more than WUH2 (482) and HKWS (483)
- High-latitude satellite geometry creates long, stable arc segments (satellites move slowly across the sky)
- GPS data usage 78.4% with clean residuals enables robust WL fixing
- The independent check passes 100% — all 129 geometry-free constraints confirmed

**HKWS WL fix rate is lower (76.7% for GPS):**

- Only 45.9% data usage (many epochs flagged) reduces the number of qualifying ambiguity arcs
- GPS wide-lane: 237 of 309 = 76.7% — 72 satellite pairs not fixed, likely due to short arcs below the 600-second minimum
- Despite lower WL rate, ALL fixed WL ambiguities yielded valid NL fixes (100% NL/WL) — the quality of what was fixed is perfect
- Galileo: 99.4% WL fixed, 100% NL — Galileo is much more stable than GPS at HKWS

**WUH2 sits between HKWS and KIRU:**

- 89.0% WL overall, 97.7% NL
- 9 GPS NL ambiguities failed to fix (95.9% NL/WL for GPS) — these are borderline cases where the WL was fixed but NL bootstrapping failed
- Galileo: 100% NL after 94.9% WL — excellent Galileo performance
- BDS ambiguities: BDS2=0, BDS3=0 fixed — PRIDE does not AR-fix BDS on this dataset (OSB biases may not support full BDS AR)

**BDS AR was not performed for any station.** Despite enabling C06–C61 in the config, the `AMB FIXING` header shows `BDS2 0  BDS3 0` for all stations. This is consistent with the current state of PRIDE's BDS AR support — BDS AR requires integer-recoverable phase biases for all BDS satellites, which may not be fully available in the COD0MGXFIN OSB product for this date.

---

## 5. Static Position Results (AR=Y)

### 5.1 Final ECEF Coordinates

PRIDE outputs a single best-fit ECEF position for the entire day. The `Sig0` value is the square root of the variance factor (in meters), representing the overall quality of the solution.

| Station  | X (m)         | Y (m)        | Z (m)        | Sig0 (m)  | Nobs   |
| -------- | ------------- | ------------ | ------------ | --------- | ------ |
| **HKWS** | −2430579.8579 | 5374285.4030 | 2418956.0380 | **1.803** | 48,902 |
| **KIRU** | 2251420.4496  | 862817.4632  | 5885476.9326 | 2.649     | 94,234 |
| **WUH2** | −2267750.3240 | 5009154.4912 | 3221294.3524 | **2.999** | 85,614 |
| **ZIM2** | 4331299.5851  | 567537.7042  | 4633133.9596 | 2.221     | 78,673 |

### 5.2 Position Precision Analysis

**Sig0 ranking: HKWS (best) > KIRU > WUH2 (worst)**

- **HKWS (Sig0 = 1.803 m):** Best sigma0 despite the smallest dataset (48,902 obs, 45.9% data usage). The strict data editing removed all noisy observations, leaving a highly consistent residual set. No BDS contamination. Excellent Galileo fix rate (99.4% WL → 100% NL).

- **KIRU (Sig0 = 2.649 m):** Despite having the most observations (94,234) and the best AR rates, KIRU's sigma0 is intermediate. High-latitude geometry introduces higher zenith troposphere modeling uncertainty and BDS residuals are slightly elevated (C08=34mm, C13=28mm). The large number of ambiguities (1040) constrains the solution strongly.

- **WUH2 (Sig0 = 2.999 m):** Highest sigma0, reflecting noisier BDS observations (C35=23mm, C12=13mm range). WUH2's sub-tropical location and dense constellation visibility causes more multipath variability in the BDS-3 MEO signals. The 9 GPS NL ambiguities that failed to fix also slightly degrade the solution quality.

### 5.3 Comparison with RINEX Header a priori Coordinates

The `tedit` preprocessing uses a priori XYZ from the RINEX file header (or SPP-estimated position). The difference between PRIDE's final ECEF result and these approximate a priori positions reveals the PPP correction applied:

| Station | ΔX (m) | ΔY (m) | ΔZ (m) | 3D offset (m) |
| ------- | ------ | ------ | ------ | ------------- |
| HKWS    | +0.644 | −1.744 | −1.286 | ~2.2          |
| KIRU    | −0.020 | −0.056 | +1.596 | ~1.6          |
| WUH2    | −0.233 | +1.322 | +1.053 | ~1.7          |

_Note: These are differences vs. the SPP-estimated a priori position (from the `tedit` command), not vs. IGS20 reference frame coordinates. The offsets reflect SPP accuracy (~1–3 m) being corrected by PPP to centimeter/millimeter-level precision._

For true accuracy assessment, one would compare against the official SINEX/ITRF2020 coordinates from IGS for each site.

---

## 6. Key Findings and Interpretation

### 6.1 PRIDE vs RTKLIB: Fundamental Difference

| Aspect        | PRIDE-PPP-AR                            | RTKLIB-EX 2.5.0                        |
| ------------- | --------------------------------------- | -------------------------------------- |
| Estimator     | Batch least-squares (static)            | Kalman filter (kinematic)              |
| Output        | Single daily ECEF position              | Epoch-by-epoch positions (time-series) |
| Convergence   | Not applicable (whole-day fit)          | ~30–90 min to cm-level                 |
| AR method     | WL+NL phase ambiguity fixing            | Lambda/ILS (LAMBDA algorithm)          |
| Products used | COD0MGXFIN final (CODE, 5-min orbit)    | COD0MGXFIN final (same)                |
| Troposhere    | Stochastic (STO) + hourly gradient      | Saastamoinen, estimated ZTD            |
| Use case      | Geodetic reference, mm-precision static | Navigation, real-time positioning      |

**These tools answer different questions.** RTKLIB shows how quickly PPP converges and how accurate the kinematic trajectory is. PRIDE shows the final precision of the daily-averaged position after ambiguity fixing — useful for comparing software accuracy at the 1–10 mm level.

### 6.2 Station Ranking: PRIDE-PPP-AR Perspective

| Rank | Station  | Reason                                                                   |
| ---- | -------- | ------------------------------------------------------------------------ |
| 1    | **HKWS** | Best Sig0 (1.803m); perfect NL fix rate; no BDS noise contamination      |
| 2    | **KIRU** | Best AR fix rates (98.1% WL, 99.7% NL); most ambiguities fixed; reliable |
| 3    | **WUH2** | Good AR rates (89.0% WL, 97.7% NL); slightly noisier BDS residuals       |
| 4    | **ZIM2** | Good AR rates (88.1% WL, 100% NL); moderate BDS noise (C08=35mm)         |

Note: This PRIDE ranking differs from the RTKLIB ranking. In RTKLIB, ZIM2 ranked #1 due to its mid-latitude location enabling fast kinematic convergence. In PRIDE static mode, convergence speed is irrelevant — only final precision and data quality matter.

ZIM2 Sig0 (2.221m) is between KIRU (2.649m) and HKWS (1.803m), reflecting moderate BDS noise (C08=35mm) offset by excellent GPS/Galileo residuals (5–11mm GPS, 2–10mm Galileo). ZIM2's 100% NL fix rate and 88.1% WL rate place it comparably to WUH2.

### 6.3 BDS Residual Analysis: C08 Anomaly

Satellite C08 (BDS-3 MEO, International Designator 2019-023B) showed elevated phase residuals at **both KIRU (34mm) and ZIM2 (35mm)** throughout all cleaning iterations. This persistently elevated residual, consistent across two geographically separated stations, strongly indicates a **satellite-specific issue**:

- Possible broadcast orbit error for this specific satellite on DOY 015, 2026
- Unmodeled satellite attitude maneuver
- Reduced-accuracy phase bias correction in the COD0MGXFIN OSB product for C08

Since BDS AR was not performed (no BDS ambiguities fixed), C08's elevated residuals don't degrade AR quality directly, but they increase Sig0 for stations tracking C08 (ZIM2, WUH2, KIRU).

### 6.4 HKWS Data Usage Warning (45.9%)

The `###WARNING(get_lsq_args): bad observation quality` was triggered because only 45.9% of HKWS observations survived data editing. Possible causes:

1. **RINEX file format issues:** LEICA GR50 receiver may output unusual RINEX tags or signal descriptors that PRIDE's strict editor rejects
2. **Multipath from Hong Kong urban environment:** Dense surrounding infrastructure reflects GPS/GAL signals
3. **Phase slip frequency:** Many short-arc segments below the 600-second minimum ambiguity duration threshold are rejected
4. **No BDS data:** The absence of BDS in HKWS residuals (despite BDS being enabled in config) suggests all BDS observations were rejected — likely because BDS satellites were below the elevation cutoff at Hong Kong's latitude, or the RINEX contains no BDS signal types

Despite this, HKWS achieved the best Sig0 (1.803m), confirming that strict editing improved solution quality even at the cost of data volume.

---

## 7. ZIM2 AR=Y — Final Results (Completed)

ZIM2 AR=Y was re-run after restoring `sat_parameters` (397 lines, `-prn_indexed`). The run completed successfully on 2026-05-09 at ~00:09.

### ZIM2 AR=Y Processing Summary

| Metric                   | Value                                                |
| ------------------------ | ---------------------------------------------------- |
| AR switch                | Y                                                    |
| Data usage               | 76.7%                                                |
| Data cleaning iterations | 7 (fully converged: 0 removed, 0 inserted in last 2) |
| Total ambiguities        | 579 (368 GPS + 211 Galileo)                          |
| Independent ambiguities  | 86                                                   |
| GPS WL/NL fix rate       | 81.5% / 100.0%                                       |
| Galileo WL/NL fix rate   | 99.5% / 100.0%                                       |
| Overall WL/NL fix rate   | **88.1% / 100.0%**                                   |
| Independent check        | 86/86 = 100%                                         |
| Normal matrix size       | 43 unknowns                                          |
| Final position           | X=4331299.5851, Y=567537.7042, Z=4633133.9596        |
| Sig0                     | 2.221 m                                              |
| Nobs                     | 78,673                                               |

### Notable Observations from ZIM2 AR=Y

- **C08 remains elevated (35mm)** across all 7 iterations — same satellite-specific anomaly seen at KIRU.
- **E18 is the cleanest Galileo satellite (2mm RMS)** — excellent for all iterations.
- The 1st lsq/redig iteration shows large initial residuals (GPS: 31–182mm; Galileo: 6–320mm; BDS: up to 994mm for C35) — these are removed in subsequent iterations.
- **BDS AR was not performed** (`BDS2 0, BDS3 0`) — consistent with all other stations.
- Galileo WL fix rate (99.5%) is very high, second only to HKWS (99.4%), reflecting high-quality Galileo geometry at Zimmerwald's 47°N latitude.

**sat_parameters warning:** The `sat_parameters` file has been truncated twice during this project (once to 356 lines, once to 436 lines). Always verify before running PRIDE:

```powershell
(Get-Content "C:\PRIDE\table\sat_parameters" | Measure-Object -Line).Lines  # Should be 397
Get-Content "C:\PRIDE\table\sat_parameters" | Select-Object -Last 1  # Should be: -prn_indexed
```

---

## 8. Plot Guide: Visualizing PRIDE-PPP-AR Results

### 8.1 Available Output Files Per Station

| File               | Content                                               | Format                      |
| ------------------ | ----------------------------------------------------- | --------------------------- |
| `pos_2026015_SITE` | Final static ECEF position + covariance               | PRIDE custom (single epoch) |
| `res_2026015_SITE` | Epoch-by-epoch phase + code residuals per satellite   | PRIDE residuals             |
| `ztd_2026015_SITE` | Time-series of ZTD (zenith troposphere delay)         | Time + ZTD + sigma          |
| `htg_2026015_SITE` | Horizontal troposphere gradient (N-S and E-W)         | Time + gradient components  |
| `rck_2026015_SITE` | Receiver clock offset time-series (GPS, GAL, BDS)     | Time + clock components     |
| `amb_2026015_SITE` | Ambiguity estimates (WL and NL per arc)               | Tabular format              |
| `stt_2026015_SITE` | Satellite status (elevation, azimuth, tracking flags) | Per-epoch per-satellite     |
| `cst_2026015_SITE` | Constraint information for AR                         | AR constraint list          |

### 8.2 Recommended Plots

#### Plot 1: Phase Residuals Time-Series

**Purpose:** Assess carrier-phase fit quality and identify outlier epochs/satellites.

**How to make:**

```python
# Use Python/matplotlib to parse res_2026015_SITE
# Each epoch: "TIM YYYY M D H M S  MJD  sec_of_day"
# Each obs: "PRN  phase_res(m)  code_res(m)  amb  weight  flag  elev  az"
# Plot phase_res vs time for each GNSS constellation separately
```

**What to look for:**

- GPS residuals: expect ±10–15mm RMS at zenith
- Galileo: expect ±5–10mm (cleaner signal design)
- BDS MEO: expect ±10–35mm (C08 anomaly visible throughout)
- Any sudden jumps = cycle slips that redig could not insert → removed
- Elevation-dependent trend (higher residuals at low elevation) = normal

#### Plot 2: ZTD Time-Series (All Stations Overlaid)

**Purpose:** Compare troposphere estimates — validates processing consistency and shows weather patterns.

**How to make:**

```python
# Parse ztd_2026015_SITE: columns = YYYY M D H MM SS  ZTD  ZTD_sigma  HTG
# Plot ZTD vs epoch for all 4 stations on one figure
```

**What to look for:**

- HKWS (Hong Kong, tropical): highest ZTD ~2.3–2.5m (humid, warm)
- WUH2 (Wuhan, central China): intermediate ZTD ~2.2–2.4m
- ZIM2 (Switzerland, Alps): lower ZTD ~2.2–2.35m (altitude effect)
- KIRU (Sweden, high latitude): lowest ZTD ~2.0–2.1m (cold, dry)
- Variations within the day indicate weather fronts passing through

#### Plot 3: Receiver Clock Offset Time-Series

**Purpose:** Verify clock model consistency across GNSS systems.

**How to make:**

```python
# Parse rck_2026015_SITE: columns = epoch  GPS_clock  GAL_clock  BDS_clock  BDS3_clock
# Expected: GPS clock drifts linearly (receiver clock)
# GAL_clock, BDS_clock are expressed relative to GPS (ISB offsets)
```

**What to look for:**

- GPS receiver clock: drifts at receiver's frequency stability rate
- Galileo ISB: roughly constant (hardware delay), should be <100ns
- BDS ISB: may differ from Galileo by 10–50ns (different hardware paths)

#### Plot 4: Satellite Sky Plot (from stt file)

**Purpose:** Visualize which satellites were tracked and for how long.

**How to make:**

```python
# Parse stt_2026015_SITE for elevation and azimuth of each satellite
# Polar plot (azimuth vs elevation), color-coded by GNSS
```

**What to look for:**

- GPS: 7–12 satellites above 15° at any time
- Galileo: 4–8 satellites
- BDS MEO: varies by station latitude (more at mid-latitudes for HKWS, WUH2)
- KIRU: BDS satellites mostly low elevation (MEO/IGSO orbit geometries at high latitude)

#### Plot 5: AR Fix History (from amb file)

**Purpose:** Show when and which ambiguities were fixed across the day.

**How to make:**

```python
# Parse amb_2026015_SITE: shows WL and NL integer values per ambiguity arc
# Plot satellite-pair arcs on a time axis, colored by fix status (WL-only vs WL+NL)
```

### 8.3 Cross-Software Comparison Plot (PRIDE vs RTKLIB)

Since PRIDE produces a single static position and RTKLIB produces a time-series, direct overlay in RTKPLOT is not straightforward. The best comparison approach:

1. **Position accuracy:** Compare PRIDE's single ECEF coordinate vs. RTKLIB's converged solution (last 30–60 min mean position) vs. known IGS reference
2. **Troposphere:** Plot RTKLIB ZTD estimates (if estimated, Experiment 2C/3A) vs. PRIDE ZTD time-series on the same axes
3. **Residuals:** Compare RTKLIB post-fit residuals vs. PRIDE phase residuals for the same satellites

---

## 9. Summary and Recommendations

### 9.1 Processing Outcomes

| Station | Float PPP (AR=N) | AR-Fixed (AR=Y)           | Pos file saved               |
| ------- | ---------------- | ------------------------- | ---------------------------- |
| HKWS    | ✅ Succeeded     | ✅ 84.9% WL, 100% NL      | pos_2026015_hkws (AR=Y only) |
| WUH2    | ✅ Succeeded     | ✅ 89.0% WL, 97.7% NL     | pos_2026015_wuh2 (AR=Y only) |
| KIRU    | ✅ Succeeded     | ✅ **98.1% WL, 99.7% NL** | pos_2026015_kiru (AR=Y only) |
| ZIM2    | ✅ Succeeded\*   | ❌ sat_parameters failure | ❌ No pos file               |

\*ZIM2 AR=N succeeded but its output was overwritten when AR=Y started. **ZIM2 must be re-run entirely.**

### 9.2 Strengths of PRIDE-PPP-AR

- **Highest geodetic accuracy:** Batch LS with WL+NL AR achieves mm-level daily position
- **Multi-GNSS:** GPS + Galileo AR simultaneously (BDS AR pending in current products)
- **Rigorous troposphere:** STO model with gradient; better than Saastamoinen for long sessions
- **Satellite attitude:** Uses OBX attitude files — critical for Galileo and BDS
- **Independent verification:** Geometry-free check of AR solutions (100% pass rate on all stations)

### 9.3 Known Limitations for This Dataset

- **Static only:** No kinematic time-series; RTKLIB is needed for convergence analysis
- **No GLONASS:** FDMA signal biases not well-supported in PRIDE for AR
- **No BDS AR:** BDS3 integer fixing not achieved with current COD0MGXFIN OSB biases
- **sat_parameters fragility:** Table file can be corrupted by partial downloads — keep a backup
- **ZIM2 incomplete:** Cannot compare all 4 stations until ZIM2 AR=Y is re-run

---

_Document generated: 2026-05-08 | Processed by: Joel | Software version: PRIDE-PPP-AR v3.x_
