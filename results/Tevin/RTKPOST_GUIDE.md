# Tevin — RTKPOST Step-by-Step Guide
## PPP Experiments: All 5 Experiments × 4 Stations

**Software:** RTKLIB-EX 2.5.0 (demo5 b34d) — `rtkpost.exe`  
**Project root:** `C:\Users\tevin\Desktop\GNSS - MASTA\SPRING SEM\4.SAT NAV DATA PROCESSING\TEAM PROJECT\SNDP-PROJECT\`  
**All paths below are relative to the project root.**

---

## Quick Reference: Input Files

### Station Observation Files (RINEX OBS)

| Station | Observation File |
|---------|----------------|
| HKWS | `Old_data\data\HKWS00HKG_R_20260150000_01D_30S_MO.rnx` |
| KIRU | `New_Data\obs\RNXDATA\KIRU00SWE_R_20260150000_01D_30S_MO.rnx` |
| WUH2 | `New_Data\obs\RNXDATA\WUH200CHN_R_20260150000_01D_30S_MO.rnx` |
| ZIM2 | `Old_data\data\ZIM200CHE_R_20260150000_01D_30S_MO.rnx` |

### Precise Products (used in all precise-ephemeris experiments)

| Slot | File | Full Path |
|------|------|-----------|
| NAV (slot 1) | `BRDC00IGS_R_20260150000_01D_MN.rnx` | `Old_data\products\nav\` |
| SP3 (slot 2) | `COD0MGXFIN_20260150000_01D_05M_ORB.SP3` | `Old_data\products\sp3\` |
| CLK (slot 3) | `COD0MGXFIN_20260150000_01D_30S_CLK.CLK` | `Old_data\products\clk\` |
| BIA (slot 4) | `COD0MGXFIN_20260150000_01D_01D_OSB.BIA` | `Old_data\products\bia\` |
| ATX | `igs20_2401.atx` | `Old_data\products\atx\` |
| IONEX | `COD0OPSFIN_20260150000_01D_01H_GIM.INX` | `Old_data\products\ionex\` |

### RTKPLOT Reference Coordinates (for validation after processing)

| Station | Latitude (°) | Longitude (°) | Height (m) |
|---------|-------------|--------------|------------|
| HKWS | 22.3024 | 114.1741 | 25.862 |
| KIRU | 67.8576 | 20.9680 | 393.665 |
| WUH2 | 30.5316 | 114.3571 | 71.492 |
| ZIM2 | 46.8771 | 7.4653 | 956.312 |

---

## General RTKPOST Procedure (applies to every run)

1. Open RTKLIB-EX RTKPOST
2. **Load config first:** Click `Options` → `Load` → browse to `results\tevin\configs\[exp_name].conf` → Open → **OK**
   - This sets all processing parameters automatically
3. **Set RINEX OBS (Rover):** First input field → browse to the station `.rnx` file
4. **Set NAV slots:** Click the `...` button beside each slot number and load the required files (or clear unused slots)
5. **Set output file:** Last output field → type the full output path:
   `results\tevin\[STATION]\[STATION]_[EXPCODE].pos`
6. **Set time range:** Leave both Time checkboxes unchecked for full day (EXP5E). For EXP5A–5D, check both and enter the times from the EXP5 table.
7. Click **Execute**

RTKPOST auto-generates three output files per run:
- `[output].pos` — position solutions
- `[output].pos.stat` — residuals and statistics
- `[output]_events.pos` — event log

---

## EXP1 — Broadcast vs Precise Ephemeris (GPS Only)

**Goal:** Show the accuracy improvement from precise orbital/clock products over broadcast.

---

### EXP1A — GPS Only, Broadcast Ephemeris, Klobuchar Iono

Run for: **HKWS, KIRU, WUH2, ZIM2**

| Setting | Value |
|---------|-------|
| Config file | `results\tevin\configs\exp1A_broadcast.conf` |
| RINEX OBS | Station `.rnx` (see table above) |
| NAV Slot 1 | `Old_data\products\nav\BRDC00IGS_R_20260150000_01D_MN.rnx` |
| NAV Slots 2–10 | **EMPTY** (clear all) |
| Files → Satellite ATX | **EMPTY** |
| Files → Receiver ATX | **EMPTY** |
| Files → IONEX | **EMPTY** |
| Output | `results\tevin\[STATION]\[STATION]_EXP1A_broadcast.pos` |
| Time range | Unchecked (full day) |

**Verify in Options → Settings1:**
- Positioning Mode: `PPP Static`
- Frequencies: `L1+L2`
- Satellite Ephemeris: `Broadcast`
- Ionosphere Correction: `Broadcast (Klobuchar)`
- Navigation Systems: GPS only
- posopt1 / posopt2 / posopt3: **OFF**

---

### EXP1B — GPS Only, Precise Ephemeris, Iono-Free LC

Run for: **HKWS, KIRU, WUH2, ZIM2**

| Setting | Value |
|---------|-------|
| Config file | `results\tevin\configs\exp1B_precise.conf` |
| RINEX OBS | Station `.rnx` |
| NAV Slot 1 | `Old_data\products\nav\BRDC00IGS_R_20260150000_01D_MN.rnx` |
| NAV Slot 2 | `Old_data\products\sp3\COD0MGXFIN_20260150000_01D_05M_ORB.SP3` |
| NAV Slot 3 | `Old_data\products\clk\COD0MGXFIN_20260150000_01D_30S_CLK.CLK` |
| NAV Slots 4–10 | **EMPTY** |
| Files → Satellite ATX | `Old_data\products\atx\igs20_2401.atx` |
| Files → Receiver ATX | `Old_data\products\atx\igs20_2401.atx` |
| Files → IONEX | **EMPTY** |
| Output | `results\tevin\[STATION]\[STATION]_EXP1B_precise.pos` |
| Time range | Unchecked (full day) |

**Verify in Options → Settings1:**
- Satellite Ephemeris: `Precise`
- Ionosphere Correction: `Dual-Freq (IF Combination)`
- posopt1 (Satellite PCV): **ON**
- posopt2 (Receiver PCV): **ON**
- posopt3 (Phase Wind-up): **ON**

---

## EXP2 — Multi-Constellation Comparison

**Goal:** Assess how adding Galileo, BDS, and GLONASS improves PPP accuracy and convergence.

All EXP2 runs use **Precise ephemeris**. Load NAV + SP3 + CLK + ATX for each (same as EXP1B). No BIA file.

---

### EXP2A — GPS Only (Precise baseline)

| Setting | Value |
|---------|-------|
| Config file | `results\tevin\configs\exp2A_GPS.conf` |
| Products | NAV slot 1 + SP3 slot 2 + CLK slot 3 + ATX |
| Output | `results\tevin\[STATION]\[STATION]_EXP2A_GPS.pos` |

Navigation Systems: **GPS only**

---

### EXP2B — GPS + Galileo

| Setting | Value |
|---------|-------|
| Config file | `results\tevin\configs\exp2B_GE.conf` |
| Products | NAV slot 1 + SP3 slot 2 + CLK slot 3 + ATX |
| Output | `results\tevin\[STATION]\[STATION]_EXP2B_GE.pos` |

Navigation Systems: **GPS + Galileo** (`navsys=9`)

---

### EXP2C — GPS + Galileo + BDS

| Setting | Value |
|---------|-------|
| Config file | `results\tevin\configs\exp2C_GEC.conf` |
| Products | NAV slot 1 + SP3 slot 2 + CLK slot 3 + ATX |
| Output | `results\tevin\[STATION]\[STATION]_EXP2C_GEC.pos` |

Navigation Systems: **GPS + Galileo + BDS** (`navsys=41`)

---

### EXP2D — All Constellations

| Setting | Value |
|---------|-------|
| Config file | `results\tevin\configs\exp2D_GRCEQ.conf` |
| Products | NAV slot 1 + SP3 slot 2 + CLK slot 3 + ATX |
| Output | `results\tevin\[STATION]\[STATION]_EXP2D_GRCEQ.pos` |

Navigation Systems: **GPS + GLONASS + Galileo + BDS + QZSS** (`navsys=61`)

---

## EXP3 — Float PPP vs PPP-AR

**Goal:** Compare standard float ambiguity PPP against attempted integer ambiguity resolution.

Both runs use GPS+GAL+BDS. EXP3B adds the BIA file in slot 4.

---

### EXP3A — Standard Float PPP

| Setting | Value |
|---------|-------|
| Config file | `results\tevin\configs\exp3A_float.conf` |
| NAV Slot 1 | `Old_data\products\nav\BRDC00IGS_R_20260150000_01D_MN.rnx` |
| NAV Slot 2 | `Old_data\products\sp3\COD0MGXFIN_20260150000_01D_05M_ORB.SP3` |
| NAV Slot 3 | `Old_data\products\clk\COD0MGXFIN_20260150000_01D_30S_CLK.CLK` |
| NAV Slots 4–10 | **EMPTY** |
| Files → ATX | `Old_data\products\atx\igs20_2401.atx` (both slots) |
| Output | `results\tevin\[STATION]\[STATION]_EXP3A_float.pos` |

Verify in Options → Amb Resolution: **OFF**

---

### EXP3B — PPP-AR Attempt

| Setting | Value |
|---------|-------|
| Config file | `results\tevin\configs\exp3B_PPPAR.conf` |
| NAV Slot 1 | `Old_data\products\nav\BRDC00IGS_R_20260150000_01D_MN.rnx` |
| NAV Slot 2 | `Old_data\products\sp3\COD0MGXFIN_20260150000_01D_05M_ORB.SP3` |
| NAV Slot 3 | `Old_data\products\clk\COD0MGXFIN_20260150000_01D_30S_CLK.CLK` |
| **NAV Slot 4** | **`Old_data\products\bia\COD0MGXFIN_20260150000_01D_01D_OSB.BIA`** |
| NAV Slots 5–10 | **EMPTY** |
| Files → ATX | `Old_data\products\atx\igs20_2401.atx` (both slots) |
| Output | `results\tevin\[STATION]\[STATION]_EXP3B_PPPAR.pos` |

Verify in Options → Amb Resolution: **Continuous**

> **Important — Expected Behaviour:** The AR ratio will remain at 0.0 for the entire run. RTKLIB-EX 2.5.0 requires FCB-format integer phase biases for PPP-AR. IGS CODE provides OSB-format biases (the `.BIA` file). These are incompatible, so AR never activates. The solution will be numerically identical to EXP3A. This is expected and should be documented as such in your analysis.

---

## EXP4 — Ionosphere Correction Methods

**Goal:** Compare three ionosphere handling strategies: Klobuchar model, IONEX TEC grid, and dual-frequency IF elimination.

---

### EXP4A — L1 Only, Broadcast + Klobuchar Model

| Setting | Value |
|---------|-------|
| Config file | `results\tevin\configs\exp4A_L1_Klobuchar.conf` |
| NAV Slot 1 | `Old_data\products\nav\BRDC00IGS_R_20260150000_01D_MN.rnx` |
| NAV Slots 2–10 | **EMPTY** |
| Files → ATX | **EMPTY** |
| Files → IONEX | **EMPTY** |
| Output | `results\tevin\[STATION]\[STATION]_EXP4A_L1_Klobuchar.pos` |

Verify: Frequencies = `L1`, Satellite Ephemeris = `Broadcast`, Ionosphere = `Broadcast (Klobuchar)`, posopt1/2/3 = **OFF**

---

### EXP4B — L1+L2 Iono-Free LC, Precise (Dual-Freq Baseline)

| Setting | Value |
|---------|-------|
| Config file | `results\tevin\configs\exp4B_L1L2_IF.conf` |
| NAV Slot 1 | `Old_data\products\nav\BRDC00IGS_R_20260150000_01D_MN.rnx` |
| NAV Slot 2 | `Old_data\products\sp3\COD0MGXFIN_20260150000_01D_05M_ORB.SP3` |
| NAV Slot 3 | `Old_data\products\clk\COD0MGXFIN_20260150000_01D_30S_CLK.CLK` |
| NAV Slots 4–10 | **EMPTY** |
| Files → ATX | `Old_data\products\atx\igs20_2401.atx` (both slots) |
| Files → IONEX | **EMPTY** |
| Output | `results\tevin\[STATION]\[STATION]_EXP4B_L1L2_IF.pos` |

Verify: Frequencies = `L1+L2`, Satellite Ephemeris = `Precise`, Ionosphere = `Dual-Freq (IF Combination)`, posopt1/2/3 = **ON**

---

### EXP4C — L1 Only, Broadcast + IONEX TEC Map

| Setting | Value |
|---------|-------|
| Config file | `results\tevin\configs\exp4C_L1_IONEX.conf` |
| NAV Slot 1 | `Old_data\products\nav\BRDC00IGS_R_20260150000_01D_MN.rnx` |
| NAV Slots 2–10 | **EMPTY** |
| Files → ATX | **EMPTY** |
| **Files → IONEX** | **`Old_data\products\ionex\COD0OPSFIN_20260150000_01D_01H_GIM.INX`** |
| Output | `results\tevin\[STATION]\[STATION]_EXP4C_L1_IONEX.pos` |

Verify: Frequencies = `L1`, Satellite Ephemeris = `Broadcast`, Ionosphere = `IONEX TEC`, posopt1/2/3 = **OFF**

> The IONEX path is already embedded in the conf file. When you load the config via Options → Load, the Files tab will auto-populate the IONEX field. Confirm it shows the correct `.INX` file before running.

---

## EXP5 — Convergence vs Session Length

**Goal:** Quantify how PPP accuracy and convergence time change with observation duration (1 h → 24 h).

**All five sub-experiments share the same config file:** `results\tevin\configs\exp5_sessions.conf`

Load the same products for every sub-experiment:
- NAV Slot 1: `Old_data\products\nav\BRDC00IGS_R_20260150000_01D_MN.rnx`
- NAV Slot 2: `Old_data\products\sp3\COD0MGXFIN_20260150000_01D_05M_ORB.SP3`
- NAV Slot 3: `Old_data\products\clk\COD0MGXFIN_20260150000_01D_30S_CLK.CLK`
- NAV Slots 4–10: **EMPTY**
- Files → ATX: `Old_data\products\atx\igs20_2401.atx` (both slots)

**The only change between sub-experiments is the Time End in the RTKPOST main window.**

| Sub-exp | Duration | Time Start (check the box) | Time End (check the box) |
|---------|----------|---------------------------|--------------------------|
| EXP5A | 1 h | `2026/01/15 00:00:00` | `2026/01/15 01:00:00` |
| EXP5B | 2 h | `2026/01/15 00:00:00` | `2026/01/15 02:00:00` |
| EXP5C | 4 h | `2026/01/15 00:00:00` | `2026/01/15 04:00:00` |
| EXP5D | 8 h | `2026/01/15 00:00:00` | `2026/01/15 08:00:00` |
| EXP5E | 24 h | **Uncheck Time Start** | **Uncheck Time End** |

For EXP5E, leave both time fields unchecked so RTKPOST uses the full 24-hour span from the RINEX file.

### Output file names

| Sub-exp | Output |
|---------|--------|
| EXP5A | `results\tevin\[STATION]\[STATION]_EXP5A_1h.pos` |
| EXP5B | `results\tevin\[STATION]\[STATION]_EXP5B_2h.pos` |
| EXP5C | `results\tevin\[STATION]\[STATION]_EXP5C_4h.pos` |
| EXP5D | `results\tevin\[STATION]\[STATION]_EXP5D_8h.pos` |
| EXP5E | `results\tevin\[STATION]\[STATION]_EXP5E_24h.pos` |

---

## Complete Run Count

| Experiment | Configs | Stations | Runs |
|------------|---------|----------|------|
| EXP1A | 1 | 4 | 4 |
| EXP1B | 1 | 4 | 4 |
| EXP2A | 1 | 4 | 4 |
| EXP2B | 1 | 4 | 4 |
| EXP2C | 1 | 4 | 4 |
| EXP2D | 1 | 4 | 4 |
| EXP3A | 1 | 4 | 4 |
| EXP3B | 1 | 4 | 4 |
| EXP4A | 1 | 4 | 4 |
| EXP4B | 1 | 4 | 4 |
| EXP4C | 1 | 4 | 4 |
| EXP5A–5E | 1 (same conf) | 4 | 20 |
| **Total** | **12 conf files** | **4 stations** | **60 runs** |

---

## Expected Output Folder Structure

After all 60 runs, `results\tevin\` should look like this:

```
results\tevin\
├── RTKPOST_GUIDE.md          ← this file
├── configs\
│   ├── exp1A_broadcast.conf
│   ├── exp1B_precise.conf
│   ├── exp2A_GPS.conf
│   ├── exp2B_GE.conf
│   ├── exp2C_GEC.conf
│   ├── exp2D_GRCEQ.conf
│   ├── exp3A_float.conf
│   ├── exp3B_PPPAR.conf
│   ├── exp4A_L1_Klobuchar.conf
│   ├── exp4B_L1L2_IF.conf
│   ├── exp4C_L1_IONEX.conf
│   └── exp5_sessions.conf
├── HKWS\
│   ├── HKWS_EXP1A_broadcast.pos  (+.stat, +_events.pos)
│   ├── HKWS_EXP1B_precise.pos
│   ├── HKWS_EXP2A_GPS.pos
│   ├── HKWS_EXP2B_GE.pos
│   ├── HKWS_EXP2C_GEC.pos
│   ├── HKWS_EXP2D_GRCEQ.pos
│   ├── HKWS_EXP3A_float.pos
│   ├── HKWS_EXP3B_PPPAR.pos
│   ├── HKWS_EXP4A_L1_Klobuchar.pos
│   ├── HKWS_EXP4B_L1L2_IF.pos
│   ├── HKWS_EXP4C_L1_IONEX.pos
│   ├── HKWS_EXP5A_1h.pos
│   ├── HKWS_EXP5B_2h.pos
│   ├── HKWS_EXP5C_4h.pos
│   ├── HKWS_EXP5D_8h.pos
│   └── HKWS_EXP5E_24h.pos
├── KIRU\                          (same 16 .pos files)
├── WUH2\                          (same 16 .pos files)
└── ZIM2\                          (same 16 .pos files)
```

---

## Validating Results with RTKPLOT

1. Open RTKLIB-EX RTKPLOT
2. **File → Open Solution 1** → load a `.pos` file
3. **Options → Solution Options** → Reference Position → enter the station coordinates from the table at the top of this guide
4. Switch to **ENU** view to see East/North/Up error time series
5. Switch to **Gnd Trk** view to see horizontal scatter around the true position

**Convergence criterion (per README):**  
The position is converged when `|E| < 0.10 m` AND `|N| < 0.10 m` AND `|U| < 0.20 m` hold continuously for at least 10 minutes. Record the epoch where this first occurs.

**For EXP5 analysis:** Load 5A through 5E in sequence and record the convergence time for each session length to see how accuracy improves with more data.

---

## Committing Results to GitHub

After all 60 runs are complete:

```powershell
# Stage all output files and configs
git add results\tevin\configs\
git add results\tevin\HKWS\
git add results\tevin\KIRU\
git add results\tevin\WUH2\
git add results\tevin\ZIM2\
git add results\tevin\RTKPOST_GUIDE.md

# Also commit the pending .gitignore change
git add .gitignore

# Commit
git commit -m "feat: add Tevin PPP results for all 5 experiments, 4 stations"

# Push
git push origin main
```

> **Note on Git LFS:** The project uses Git LFS for `.pos` and `.stat` files. Confirm the `.gitattributes` file already tracks `*.pos` and `*.pos.stat` via LFS before pushing — large solution files will fail to push otherwise.

---

*Guide generated for SNDP Team Project — DOY 015, 2026 (GPS Week 2401)*
