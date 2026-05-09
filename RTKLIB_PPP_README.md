# RTKLIB PPP — Complete Step-by-Step Guide

---

## TABLE OF CONTENTS

1. [Your Datasets — What You Have](#1-your-datasets)
2. [Which Files to Use and Why](#2-which-files-to-use-and-why)
3. [Reference Coordinates (True Positions)](#3-reference-coordinates)
4. [The Difference: RTKLIB 2.4.3 vs RTKLIB-EX 2.5.0](#4-rtklib-versions)
5. [RTKPOST Main Window — Every Field Explained](#5-rtkpost-main-window)
6. [Options Dialog — Every Tab and Setting Explained](#6-options-dialog)
   - [Setting1 Tab](#setting1-tab)
   - [Setting2 Tab](#setting2-tab)
   - [Output Tab](#output-tab)
   - [Statistics Tab](#statistics-tab)
   - [Positions Tab](#positions-tab)
   - [Files Tab](#files-tab)
   - [Misc Tab](#misc-tab)
7. [RTKPLOT — Complete Validation Guide](#7-rtkplot-complete-validation-guide)
8. [Research Experiments — Manual Step-by-Step](#8-research-experiments-manual)
   - [Experiment 1: Broadcast vs Precise Products](#experiment-1-broadcast-vs-precise-products)
   - [Experiment 2: GPS-only vs Multi-GNSS](#experiment-2-gps-only-vs-multi-gnss)
   - [Experiment 3: Float PPP vs PPP-AR (RTKLIB-EX)](#experiment-3-float-ppp-vs-ppp-ar)
   - [Experiment 4: Ionosphere Correction Methods](#experiment-4-ionosphere-correction-methods)
   - [Experiment 5: Session Length Effect](#experiment-5-session-length-effect)
9. [Old_Data — Which Products to Use](#9-old_data-which-products-to-use)
10. [PRIDE PPP-AR — Using Your Local Data](#10-pride-ppp-ar-with-local-data)
11. [Automation Script: run_rtklib.py](#11-automation-script)
12. [Quick Reference Cheat Sheet](#12-quick-reference-cheat-sheet)
13. [Troubleshooting](#13-troubleshooting)

---

## 1. YOUR DATASETS

You have two datasets, both for the **same day: January 15, 2026 (Day of Year 015, GPS Week 2401)**.

### New_Data (START HERE)

Location: `C:\PPP_PROJECT\New_Data\`

**Observation files (your raw GNSS measurements):**

| File                                                          | Station | Location                | Why Interesting                                         |
| ------------------------------------------------------------- | ------- | ----------------------- | ------------------------------------------------------- |
| `New_Data/obs/RNXDATA/KIRU00SWE_R_20260150000_01D_30S_MO.rnx` | KIRU    | Kiruna, Sweden (67.9°N) | High-latitude — more ionosphere effects at polar region |
| `New_Data/obs/RNXDATA/WUH200CHN_R_20260150000_01D_30S_MO.rnx` | WUH2    | Wuhan, China (30.5°N)   | Mid-latitude — typical continental performance          |

Both also exist as `.obs` files — these are identical content, just different extension. Use `.rnx`.

**Filename decoded:** `KIRU00SWE_R_20260150000_01D_30S_MO.rnx`

- `KIRU` = Station name (4 chars, Kiruna)
- `00` = Monument number
- `SWE` = Country code (Sweden)
- `_R_` = Data source: R=Real-time, S=Streamed, U=Unknown
- `2026` = Year
- `015` = Day of year (Jan 15 = DOY 015)
- `0000` = Start time (00:00 UTC)
- `_01D_` = Duration: 1 Day
- `_30S_` = Sample rate: 30 Seconds
- `MO` = File type: Mixed Observation (all constellations)
- `.rnx` = RINEX format, version 3

**Navigation (broadcast ephemeris):**

| File                                              | Description                                   |
| ------------------------------------------------- | --------------------------------------------- |
| `New_Data/nav/BRDC00IGS_R_20260150000_01D_MN.rnx` | Mixed nav (all constellations) — **use this** |
| `New_Data/nav/BRDC00IGS_R_20260150000_01D_MN.nav` | Same content, different extension             |

**Precise products (in `New_Data/DATA_FINAL_ANT_EXTRA/`):**

| File                                     | Type         | Description                                             |
| ---------------------------------------- | ------------ | ------------------------------------------------------- |
| `COD0MGXFIN_20260150000_01D_05M_ORB.SP3` | SP3 orbit    | CODE multi-GNSS **final** orbit (5-min intervals)       |
| `COD0MGXFIN_20260150000_01D_30S_CLK.CLK` | CLK clock    | CODE multi-GNSS **final** clock (30-sec intervals)      |
| `COD0MGXFIN_20260150000_01D_01D_OSB.BIA` | OSB biases   | CODE observable-specific biases — **needed for PPP-AR** |
| `COD0MGXFIN_20260150000_01D_12H_ERP.ERP` | ERP          | Earth rotation parameters                               |
| `COD0MGXFIN_20260150000_01D_30S_ATT.OBX` | OBX attitude | Satellite attitude/yaw (used by PRIDE, not RTKLIB)      |
| `igs20_2401.atx`                         | ATX          | Antenna phase center corrections — **always load this** |

---

### Old_Data (Use After New_Data)

Location: `C:\PPP_PROJECT\Old_data\`

**Observation files:**

| File                                                   | Station | Location                         |
| ------------------------------------------------------ | ------- | -------------------------------- |
| `Old_data/data/ZIM200CHE_R_20260150000_01D_30S_MO.rnx` | ZIM2    | Zimmerwald, Switzerland (46.9°N) |
| `Old_data/data/HKWS00HKG_R_20260150000_01D_30S_MO.rnx` | HKWS    | Hong Kong, China (22.3°N)        |

**Products:** Multiple options available — see [Section 9](#9-old_data-which-products-to-use) for full guidance.

---

## 2. WHICH FILES TO USE AND WHY

### For New_Data (Experiments 1–5)

**For Experiment 1 (Broadcast vs Precise):**

| Run           | Ephemeris                                                                           | Files needed  |
| ------------- | ----------------------------------------------------------------------------------- | ------------- |
| Broadcast run | `New_Data/nav/BRDC00IGS_R_20260150000_01D_MN.rnx` only                              | Nav file only |
| Precise run   | `COD0MGXFIN_20260150000_01D_05M_ORB.SP3` + `COD0MGXFIN_20260150000_01D_30S_CLK.CLK` | SP3 + CLK     |

**For Experiments 2–5 (Multi-GNSS, PPP-AR, Ionosphere, Session Length):**

- Always use the SP3 + CLK + BIA files from `New_Data/DATA_FINAL_ANT_EXTRA/`
- Always load `igs20_2401.atx` in the Files tab

### Why COD0MGXFIN Is the Best Choice

`COD` = CODE (Center for Orbit Determination in Europe, ETH Zürich)
`MGX` = Multi-GNSS experiment — supports GPS + GLONASS + Galileo + BeiDou + QZSS
`FIN` = Final product (most accurate; ~2 week delay from observation date)

This gives you:

- Orbit accuracy: ~2–3 cm (vs ~1–3 m for broadcast)
- Clock accuracy: ~0.03 ns (vs ~2–7 ns for broadcast)
- Phase biases (OSB): needed for PPP-AR

### File Compatibility Note

The `.obs` and `.rnx` files are identical in content. Always use `.rnx` with RTKLIB for clarity.
RTKLIB handles RINEX 3 files — just make sure to load the mixed navigation `.rnx` file (not a GPS-only `.nav`).

---

## 3. REFERENCE COORDINATES

To evaluate your PPP accuracy, you need the "true" position of each station. These are
published by the IGS (International GNSS Service) in SINEX format.

The SINEX file for your dataset is: `Old_data/products/snx/MIT0OPSSNX_2026015_SOL.SNX`

### Station Coordinates (ITRF2020, Epoch 2026.0, DOY 015)

| Station  | Latitude   | Longitude   | Height (m) | ECEF X (m)   | ECEF Y (m)  | ECEF Z (m)   |
| -------- | ---------- | ----------- | ---------- | ------------ | ----------- | ------------ |
| **ZIM2** | 46.8771° N | 7.4650° E   | 956.4      | 4331299.7091 | 567537.7486 | 4633133.8374 |
| **HKWS** | 22.2722° N | 114.1614° E | 72.0       | -2430579.667 | 5374285.542 | 2418955.908  |
| **KIRU** | 67.8579° N | 20.9678° E  | 390.9      | 2287359.044  | 864704.133  | 5900842.040  |
| **WUH2** | 30.5317° N | 114.3570° E | 73.4       | -2267741.455 | 5009164.095 | 3221012.978  |

> **How to verify:** Open `MIT0OPSSNX_2026015_SOL.SNX` in a text editor.
> Find lines starting with ` KIRU` or ` ZIM2` in the SOLUTION/ESTIMATE block.
> The STAX/STAY/STAZ values are the ECEF coordinates. For KIRU and WUH2,
> also search the IGS site list or use the approximate values above.

### Convergence Criteria Used in This Research

A PPP solution is considered **converged** when ALL of the following are met:

- **East error** |dE| < 10 cm
- **North error** |dN| < 10 cm
- **2D horizontal error** (√(dE²+dN²)) < 10 cm
- **Vertical error** |dU| < 20 cm
- **All four criteria maintained** for at least 10 consecutive minutes

---

## 4. RTKLIB VERSIONS

You have two versions installed. Here is exactly how they differ for PPP:

### RTKLIB 2.4.3 (Standard Version)

**Location:** `C:\Program Files\RTKLIB\bin\`

- Key program: `rtkpost.exe`, `rtkplot.exe`
- PPP capability: Float PPP only (no real ambiguity resolution)
- Multi-GNSS: GPS + GLONASS + Galileo + BDS supported
- Phase bias input: NOT supported in main window
- Best for: Learning PPP basics, Experiment 1 (broadcast vs precise), Experiment 2 (multi-GNSS)

### RTKLIB-EX 2.5.0 ("demo5" version)

**Location:** `C:\Program Files\RTKLIB_EX_2.5.0\`  
(Help → About shows "RTKLIB-EX 2.5.0")

- Key program: `rtkpost.exe`, `rtkplot.exe`, `rnx2rtkp.exe`
- PPP capability: **Float PPP + PPP-AR** (with OSB/BIA files)
- Multi-GNSS: Better handling than 2.4.3
- Phase bias input: **YES** — the main window has BIA/BSX/FCB input slots
- Best for: All experiments, especially Experiment 3 (PPP-AR)

### Visual Difference in the GUI

In the RTKPOST main window, look at the "RINEX NAV/CLK..." label:

- **RTKLIB 2.4.3:** Label says `RINEX NAV/CLK, SP3 or RTCM` (fewer slots)
- **RTKLIB-EX 2.5.0:** Label says `RINEX NAV/CLK, SP3, BIA/BSX, FCB, IONEX, SBS/EMS or RTCM` — more input slots visible, enabling phase bias loading for PPP-AR

**Which to use:** For Experiments 1–2 and 4–5, either version works. For Experiment 3 (PPP-AR), use RTKLIB-EX 2.5.0. When in doubt, always use RTKLIB-EX 2.5.0 — it is strictly better.

---

## 5. RTKPOST MAIN WINDOW

Open RTKPOST-EX 2.5.0:

> Double-click `C:\Program Files\RTKLIB_EX_2.5.0\rtkpost.exe`

You will see the main window. Here is every field explained:

```
┌─────────────────────────────────────────────────────────────────┐
│ □ Time Start (GPST)  ?    □ Time End (GPST)   ?    □ Interval   Unit│
│ 2000/01/01  00:00:00      2000/01/01 00:00:00   0    s   24  H  │
│                                                                   │
│ RINEX OBS: Rover             ?                         ⊕  ▭  ... │
│ [____________________________________________________]        ▼  │
│                                                                   │
│ RINEX OBS: Base Station                                ⊕  ▭      │
│ [____________________________________________________]        ▼  │
│                                                                   │
│ RINEX NAV/CLK, SP3, BIA/BSX, FCB, IONEX, SBS/EMS or RTCM  □ □..│
│ [____________________________________________________]        ▼  │
│ [____________________________________________________]        ▼  │
│ ... (10 slots total)                                              │
│                                                                   │
│ Solution □ Dir                                                ... │
│ [____________________________________________________]        ▼  │
│                                                                   │
│  ▭  □                                                           ? │
│ [Plot] [View] [KML/GPX] [Options] [▶ Execute]         [Exit]     │
└─────────────────────────────────────────────────────────────────┘
```

### Time Start / Time End (top row)

**What they do:** Crop the observation file to a specific time window.

- **Checkbox unchecked (default):** Process the ENTIRE observation file (all 24 hours).
  Leave unchecked when you want the full-day result.
- **Checkbox checked + date/time filled in:** Process ONLY the time window you specify.
  This is essential for **Experiment 5 (Session Length)** where you process the same file
  for 1h, 2h, 4h, 8h, and 24h separately.

**Time format:** Year/Month/Day and HH:MM:SS in GPST (GPS Time).
GPST is ahead of UTC by 18 seconds as of 2026. However, for your data files that span 00:00:00 to 23:59:30,
just use 00:00:00 to the end time you want — RTKLIB handles the GPST offset internally.

**Interval / Unit:** If you want to process only every Nth epoch (e.g., every 60 seconds
instead of every 30 seconds), set this here. Leave at `0` to use the native file sample rate (30s).

---

### RINEX OBS: Rover

**What it is:** Your primary observation file — the actual GNSS measurements.

**How to set it:** Click the `...` button → navigate to your .rnx file → click Open.

**For New_Data experiments:**

- KIRU station: `C:\PPP_PROJECT\New_Data\obs\RNXDATA\KIRU00SWE_R_20260150000_01D_30S_MO.rnx`
- WUH2 station: `C:\PPP_PROJECT\New_Data\obs\RNXDATA\WUH200CHN_R_20260150000_01D_30S_MO.rnx`

**The `?` button:** Click this to see information about the loaded file (station name,
receiver type, antenna type, first/last epoch). Use this to verify you loaded the right file.

**The small icon `⊕`:** Allows you to add a second rover file (for multi-session stitching). Leave alone for now.

---

### RINEX OBS: Base Station

**What it is:** For PPP, this must be EMPTY.

**Why:** PPP stands for Precise Point Positioning — it is a standalone technique that does NOT
require a base station. This field is only used for RTK (Real-Time Kinematic) processing.
If you accidentally load a file here, PPP will not work correctly.

**Action:** Leave this field completely empty for all your PPP experiments.

---

### RINEX NAV/CLK, SP3, BIA/BSX, FCB, IONEX, SBS/EMS or RTCM (Multiple Slots)

This is the most important input section. It accepts up to 10 input product files.
Each row `...` opens a file picker. You can load multiple files into different rows.

**What goes in which row:**

| Slot   | File to load                           | When to load                                |
| ------ | -------------------------------------- | ------------------------------------------- |
| Row 1  | Navigation file (`.rnx` nav or `.17p`) | Always — this is the broadcast ephemeris    |
| Row 2  | SP3 orbit file (`.SP3`)                | For precise ephemeris runs                  |
| Row 3  | CLK clock file (`.CLK`)                | For precise ephemeris runs (must match SP3) |
| Row 4  | BIA/BSX/OSB file (`.BIA`)              | For PPP-AR in RTKLIB-EX 2.5.0               |
| Row 5  | IONEX file (`.INX` or `.YYI`)          | For ionosphere-constrained runs             |
| Others | Leave empty                            | —                                           |

> **Important:** RTKLIB auto-detects the file type from its content, not the extension.
> You can drag-and-drop files into the slots, or use the `...` picker.
> The small checkbox next to each row (`□`) enables/disables that specific file without removing it.

**For broadcast-only run:** Load ONLY the navigation file in Row 1. Leave all others empty.

**For precise PPP run:** Load nav in Row 1, SP3 in Row 2, CLK in Row 3.

**For PPP-AR run (RTKLIB-EX 2.5.0):** Load nav, SP3, CLK, then also the `.BIA` file.

---

### Solution Directory / File

**What it is:** Where RTKPOST saves the output `.pos` file.

**How to set it:** Click `...` → navigate to a folder → type an output filename.

**Recommended naming scheme:**

```
C:\PPP_PROJECT\RTKLIB_work\results\KIRU_EXP1_broadcast.pos
C:\PPP_PROJECT\RTKLIB_work\results\KIRU_EXP1_precise.pos
C:\PPP_PROJECT\RTKLIB_work\results\KIRU_EXP2_GPS.pos
C:\PPP_PROJECT\RTKLIB_work\results\KIRU_EXP2_GEC.pos
```

**The `□ Dir` checkbox:** When checked, the path is treated as a directory and RTKPOST
auto-names the output file based on the observation file name. When unchecked (default),
you provide the full output filename.

---

### Bottom Toolbar Buttons

**Plot...** — Open results in RTKPLOT immediately after processing. Shortcut.

**View...** — View the raw text of the output `.pos` file. Useful for debugging.

**KML/GPX...** — Export position to Google Earth KML or GPX format. Useful for visualizing
ground track in Google Earth, especially for kinematic data.

**Options...** — Open the options dialog (covered in detail in the next section).

**Execute ▶** — Start processing. All files must be loaded and options set before clicking this.

**Exit** — Close RTKPOST.

---

## 6. OPTIONS DIALOG

Click **Options...** in the main window. You will see a tabbed dialog with 7 tabs.
Here is a complete explanation of every setting relevant to your research.

---

### SETTING1 TAB

This is the most important tab. These settings define the fundamental processing strategy.

---

#### Positioning Mode

**Current value in screenshot:** `Kinematic`

**All options and their meanings:**

| Mode              | Code | What it does                                                                                                     | Use when                 |
| ----------------- | ---- | ---------------------------------------------------------------------------------------------------------------- | ------------------------ |
| Single            | 0    | Standard Point Positioning (SPP). No correction. Like a basic GPS phone. ~1–5 m accuracy.                        | Sanity check only        |
| DGPS/DGNSS        | 1    | Differential GPS — needs base station. Not PPP.                                                                  | Not for this research    |
| Kinematic         | 2    | RTK mode (moving receiver). Needs base station. Not PPP.                                                         | Not for this research    |
| Static            | 3    | RTK static mode. Needs base station. Not PPP.                                                                    | Not for this research    |
| Static-Start      | 4    | RTK that starts static then goes kinematic.                                                                      | Not for this research    |
| Moving-Base       | 5    | Base station is also moving.                                                                                     | Not for this research    |
| Fixed             | 6    | Fixed known position (for residual analysis).                                                                    | Not for this research    |
| **PPP-Kinematic** | 7    | PPP for a moving receiver. Slower convergence. Each position independent.                                        | Kinematic survey         |
| **PPP-Static**    | 8    | **USE THIS.** PPP for a stationary receiver. Filters accumulate over time → faster convergence, better accuracy. | **All your experiments** |
| PPP-Fixed         | 9    | PPP with a known position fixed. Used to estimate biases.                                                        | Advanced analysis        |

> **For all your research experiments:** Set to **PPP-Static**.
>
> PPP-Static treats the receiver as not moving. The Kalman filter accumulates
> all observations over time, improving accuracy as more data is processed.
> PPP-Kinematic would treat each epoch independently (or with a tight dynamic model),
> which prevents the accumulation benefit and gives worse convergence.

---

#### Frequencies

**Current value in screenshot:** `L1+L2+L3+L4`

**All options and their meanings:**

| Setting     | Meaning                                    | Effect                                                                         |
| ----------- | ------------------------------------------ | ------------------------------------------------------------------------------ |
| L1          | Single frequency (GPS L1 = 1575.42 MHz)    | Cannot form ionosphere-free combination. Needs external IONEX. 1–5 m accuracy. |
| L1+L2       | Dual frequency (GPS L1 + L2 = 1227.60 MHz) | **Ionosphere-free (IF) combination possible. ~5–15 cm accuracy.**              |
| L1+L2+L5    | Triple frequency (GPS L1+L2+L5)            | Best for ambiguity resolution in some methods                                  |
| L1+L2+L3+L4 | Quad frequency                             | Uses all available frequencies                                                 |

> **For your research:** Use **L1+L2** for the standard experiments. This enables the
> classic dual-frequency PPP (ionosphere-free combination).
>
> Why L1+L2 is the key: By combining L1 and L2 measurements mathematically
> (L1×f1² - L2×f2²)/(f1²-f2²), the ionosphere effect is almost completely
> eliminated. This is the **ionosphere-free (IF) combination** — the backbone of standard PPP.

---

#### Filter Type

**Current value in screenshot:** `Forward`

| Setting     | Meaning                                 | Effect                                                                            |
| ----------- | --------------------------------------- | --------------------------------------------------------------------------------- |
| **Forward** | Process from start to end in time order | Normal convergence from scratch — **use this**                                    |
| Backward    | Process from end to start               | Good for post-processing where you want best accuracy at the START of the session |
| Combined    | Forward + Backward, then merged         | Smoother results throughout, but 2× processing time                               |

> **For your research:** Use **Forward**. This is the standard PPP processing mode and
> is what all textbooks describe. It correctly shows the convergence behavior from scratch.
>
> **Note:** Combined mode would give artificially better results at the start of the session
> because it uses future data to help past epochs — this is not realistic for real-time use
> and would make Experiment 5 (session length) meaningless.

---

#### Elevation Mask (°) / SNR Mask

**Current value in screenshot:** `15` degrees

**Elevation Mask:** Satellites below this angle above the horizon are excluded.

| Value   | Effect                                                                                      |
| ------- | ------------------------------------------------------------------------------------------- |
| 5°      | Very low cut — includes noisy low-elevation satellites. More satellites but more multipath. |
| 10°     | Moderate                                                                                    |
| **15°** | **Standard PPP setting. Good balance. Use this.**                                           |
| 20°     | Conservative — excludes more satellites but only uses high-quality signals                  |
| 30°     | Very restrictive — few satellites, but very clean signals                                   |

**Why elevation matters:** Signals from satellites near the horizon travel through much
more atmosphere (ionosphere + troposphere), making them noisier and more affected by multipath
(signals bouncing off buildings/ground). Low-elevation satellites also contribute worse geometry.

**SNR Mask (`...` button):** Signal-to-Noise Ratio mask — exclude signals below a certain
SNR threshold. The `...` opens a per-frequency SNR table. Leave at defaults for now.

> **For all your experiments:** Keep elevation mask at **15°**.

---

#### Rec Dynamics / Earth Tides Correction

**Current values in screenshot:** `ON` / `OFF`

**Rec Dynamics (Receiver Dynamics):** Controls whether the Kalman filter has a velocity
and acceleration model for the receiver.

| Setting | Effect                                                                                                  |
| ------- | ------------------------------------------------------------------------------------------------------- |
| OFF     | Receiver is assumed perfectly stationary. Correct for PPP-Static with stationary antenna.               |
| **ON**  | Adds a dynamic model. For static processing, this helps when there are small unmodelled position jumps. |

> **Recommendation:** For your PPP-Static experiments with permanently mounted IGS antennas
> (KIRU, WUH2, ZIM2, HKWS), the receiver is truly stationary. Either ON or OFF is fine;
> **ON** is slightly safer as it handles any small position perturbations.

**Earth Tides Correction:**

| Setting | Effect                                                                       |
| ------- | ---------------------------------------------------------------------------- |
| **OFF** | No tidal correction. Simpler. ~cm level error in height.                     |
| ON      | Applies solid Earth tide model. Adds ~1–3 cm accuracy improvement in height. |

> For basic experiments, OFF is fine. For highest accuracy, turn ON.
> Your research focuses on convergence time, so tides have minor impact — leave **OFF**.

---

#### Ionosphere Correction

**Current value in screenshot:** `Broadcast`

This controls how the ionospheric delay is handled. This is a CRITICAL setting for Experiment 4.

| Setting          | Code | Meaning                                                          | Accuracy                          | Use case                               |
| ---------------- | ---- | ---------------------------------------------------------------- | --------------------------------- | -------------------------------------- |
| Off              | 0    | Ignore ionosphere completely                                     | Very poor (~10–50 m)              | Never use                              |
| **Broadcast**    | 1    | Use Klobuchar model (8 coefficients broadcast by GPS)            | ~50% correction (~2–5 m residual) | Single-frequency baseline              |
| **Iono-Free LC** | 3    | **Ionosphere-free combination.** L1/L2 used to cancel ionosphere | ~99% correction                   | **Standard PPP — use for Exp 1, 2, 3** |
| Est-STEC         | 4    | Estimate Slant TEC as parameter                                  | Best for UC-PPP                   | Advanced                               |
| IONEX-TEC        | 5    | Use external IONEX GIM file                                      | ~80–90% correction                | Single-freq with GIM                   |
| QZSS-BRDC        | 6    | QZSS regional ionosphere                                         | Japan region only                 | Specific                               |

> **CRITICAL UNDERSTANDING:**
>
> When you set **Frequencies = L1+L2** AND **Ionosphere Correction = Iono-Free LC**,
> RTKLIB automatically forms the ionosphere-free combination. This is standard PPP.
>
> When you set Ionosphere Correction = **Broadcast**, RTKLIB uses the Klobuchar model
> embedded in the navigation file. This is only valid for single-frequency GPS.
>
> **For Experiments 1, 2, 3, 5:** Use **Iono-Free LC** with **L1+L2** frequencies.
> **For Experiment 4 (Ionosphere methods comparison):**
>
> - Run A: Broadcast (single-frequency baseline)
> - Run B: Iono-Free LC (standard dual-frequency — labelled "Iono-Free LC" in the GUI)
> - Run C: IONEX-TEC with the `COD0OPSFIN_20260150000_01D_01H_GIM.INX` file

---

#### Troposphere Correction

**Current value in screenshot:** `Saastamoinen`

| Setting      | Meaning                                                                   | Effect                                                   |
| ------------ | ------------------------------------------------------------------------- | -------------------------------------------------------- |
| Off          | No tropospheric correction                                                | Huge error (~2–5 m in vertical)                          |
| Saas         | **Saastamoinen model** — formula using station height and elevation angle | ~90% correction, standard for PPP-Static                 |
| SBAS         | SBAS-broadcast troposphere                                                | Real-time only                                           |
| **Est-ZTD**  | **Estimate Zenith Tropospheric Delay (ZTD) as a filter parameter**        | **Best accuracy** — removes systematic tropospheric bias |
| Est-ZTD+Grad | Estimate ZTD + north-south gradient                                       | Best, but slower                                         |

> **Recommendation for your research:**
>
> - Use **Saastamoinen** to start (fast, stable)
> - For best accuracy in final results: **Est-ZTD**
>
> The troposphere is the lower atmosphere (0–50 km). It slows GPS signals, especially
> at low elevation angles. Saastamoinen is a formula; Est-ZTD actually estimates the
> delay as an unknown — more accurate but adds one more parameter the filter must solve.

---

#### Satellite Ephemeris/Clock

**Current value in screenshot:** `Broadcast`

This is the other key setting for **Experiment 1**.

| Setting       | What it uses                                       | Orbit accuracy | Clock accuracy        |
| ------------- | -------------------------------------------------- | -------------- | --------------------- |
| **Broadcast** | The navigation file (.rnx nav/.17p)                | ~1–3 m         | ~2–7 ns (= 0.6–2.1 m) |
| **Precise**   | The SP3 + CLK files you loaded                     | ~2–3 cm        | ~0.03 ns (= 9 mm)     |
| Brdc+SBAS     | Broadcast + SBAS corrections                       | ~0.5–1 m       | ~1 ns                 |
| Brdc+SSR-APC  | Broadcast + State Space Representation corrections | ~dm            | ~ns                   |

> **For Experiment 1:**
>
> - Run A: Set to **Broadcast** (and don't load SP3/CLK files)
> - Run B: Set to **Precise** (and load the SP3 + CLK files)
>
> This is the single most impactful setting difference — the accuracy gap is enormous:
> Broadcast ~1–5 m, Precise ~5–15 cm.
>
> **IMPORTANT:** When set to Precise, you MUST have both SP3 and CLK files loaded.
> If only SP3 is loaded without CLK, RTKLIB cannot do precise PPP.

---

#### Sat PCV / Rec PCV / PhWU / Rej Ecl / RAIM FDE / DBCorr (Checkboxes)

These appear in the bottom portion of Setting1.

| Checkbox    | Full Name                                | Effect                                                                                                                           |
| ----------- | ---------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| **Sat PCV** | Satellite Phase Center Variation         | Correct for the satellite antenna's non-uniform phase pattern. Requires ATX file in Files tab. **CHECK THIS** for best accuracy. |
| **Rec PCV** | Receiver Phase Center Variation          | Correct for the receiver antenna's non-uniform phase pattern. Requires ATX file. **CHECK THIS** for best accuracy.               |
| PhWU        | Phase Wind-Up                            | Correct for the rotation of the satellite causing a phase wind-up effect (~few cm). **Check this** for highest accuracy.         |
| Rej Ecl     | Reject Eclipsing Satellites              | Exclude satellites passing through Earth's shadow (their clocks behave erratically). Generally good to check.                    |
| RAIM FDE    | Receiver Autonomous Integrity Monitoring | Automatically detect and exclude bad satellites. Helpful but can cause gaps.                                                     |
| DBCorr      | Dead-Band Correction                     | Minor filter correction. Leave unchecked.                                                                                        |

> **For your research:**
>
> - **Always check Sat PCV and Rec PCV** when you have loaded the ATX antenna file.
>   Without these, your height will have a systematic error of 1–3 cm.
> - Check **PhWU** for best accuracy.
> - RAIM FDE is optional — uncheck if you see too many solution gaps.

---

#### Excluded Satellites (+PRN: Included)

A text field where you can manually exclude specific satellites by PRN number.
Example: `G03 R07` would exclude GPS satellite #3 and GLONASS satellite #7.
Use `+PRN` syntax to force-include a satellite that would otherwise be excluded.
Leave **empty** for normal processing.

---

#### Satellite Systems (GPS / GLONASS / Galileo / QZSS / BDS / NavIC / SBAS)

**This is the key setting for Experiment 2.**

| Checkbox    | System                       | Satellites                         | Frequencies      |
| ----------- | ---------------------------- | ---------------------------------- | ---------------- |
| **GPS**     | American GPS                 | ~32 active                         | L1, L2, L5       |
| **GLONASS** | Russian GLONASS              | ~24 active                         | G1, G2           |
| **Galileo** | European Galileo             | ~30 active                         | E1, E5a, E5b, E6 |
| **QZSS**    | Japanese QZSS                | 4 active (visible from East Asia)  | L1, L2, L5       |
| **BDS**     | Chinese BeiDou               | ~45 active                         | B1, B2, B3       |
| NavIC       | Indian NavIC                 | 7 active (visible from South Asia) | L5, S            |
| SBAS        | Satellite-Based Augmentation | WAAS/EGNOS                         | L1 only          |

**Currently shown in screenshot:** GPS, GLONASS, Galileo, QZSS, BDS all checked.

> **For Experiment 2 — GPS-only vs Multi-GNSS:**
>
> - Run A: Check **GPS only** (uncheck all others)
> - Run B: Check **GPS + Galileo + BDS** (the most impactful combination)
> - Run C (optional): Check all (GPS + GLONASS + Galileo + QZSS + BDS)
>
> **Why this matters:** GPS-only gives ~8–12 satellites. Adding Galileo+BDS gives ~25–35
> satellites. More satellites = better geometry = faster ambiguity convergence = better
> position. The convergence time improvement can be 2–3× faster with multi-GNSS.
>
> **Note:** GLONASS uses FDMA (different frequencies per satellite), which makes
> ambiguity resolution harder. In RTKLIB, GLONASS AR requires the HW bias calibration.
> For your experiments, GPS + Galileo + BDS is more straightforward than adding GLONASS.

---

### SETTING2 TAB

Controls ambiguity resolution (PPP-AR). This tab is crucial for Experiment 3.

---

#### Integer Ambiguity Res (GPS/GLO/BDS)

**Current values in screenshot:** `Contin` / `OFF` / `ON`

Three dropdowns — one each for GPS, GLONASS, and BDS ambiguity resolution.

| Setting        | Meaning                                                                                  |
| -------------- | ---------------------------------------------------------------------------------------- |
| **OFF**        | Float PPP — ambiguities treated as real numbers (float). Slower convergence but simpler. |
| **Continuous** | Try to fix ambiguities at every epoch. Best for PPP-AR with good bias products.          |
| Instantaneous  | Fix at each epoch independently (no temporal smoothing).                                 |
| Fix-and-Hold   | Fix ambiguities then hold them fixed (can be dangerous if wrong).                        |

> **For Float PPP:** Set all three to **OFF**
> **For PPP-AR (Experiment 3 in RTKLIB-EX 2.5.0):** Set GPS to **Continuous**, BDS to **ON** (as shown)
>
> **IMPORTANT:** PPP-AR in RTKLIB-EX 2.5.0 requires the OSB/BIA file loaded in the main window.
> Without the BIA file, setting to Continuous will try to fix ambiguities but will fail or
> give wrong fixes because the phase biases are unmodelled.

---

#### Ratio to Fix Ambiguity (Min/Nom/Max)

**Current values:** `3` / `3` / `3`

The ratio test determines if an ambiguity candidate is reliable enough to fix.
If the ratio of the best solution's residual to the second-best is ≥ threshold, it's fixed.

| Value   | Effect                                             |
| ------- | -------------------------------------------------- |
| 2.0     | Liberal — more fixes, more risk of wrong fix       |
| **3.0** | Standard (recommended) — good balance              |
| 5.0     | Conservative — fewer fixes, but more reliable      |
| 10.0    | Very conservative — only fixes when very confident |

Leave at **3** for standard processing.

---

#### GLO HW Bias

**Current value:** `0`

GLONASS hardware bias between GPS and GLONASS receivers. This is receiver-specific.
If you want GLONASS AR, you need to calibrate this for your receiver. Leave at **0** unless
you specifically know the hardware bias for your receiver.

---

#### Min Lock / Elevation (°) to Fix Amb

**Current values:** `0` / `15`

- **Min Lock count:** Minimum number of consecutive epochs a satellite must be tracked before
  trying to fix its ambiguity. `0` means fix immediately. A value of `20` means wait for 20
  consecutive seconds of tracking.
- **Elevation:** Only attempt to fix ambiguities for satellites above this elevation angle.
  15° is standard.

---

#### Min Fix / Elevation (°) to Hold Amb

**Current values:** `20` / `15`

After a fix is made, require at least 20 consecutive fixed epochs before switching to Hold mode.

---

#### Slip Threshs: Doppler (Hz) / Geom-Free (m)

**Current values:** `0.000` / `0.050`

These thresholds detect cycle slips (sudden jumps in the carrier phase signal).

- **Doppler threshold:** Detects large velocity jumps. `0` means disabled.
- **Geom-Free threshold:** 0.050 m (5 cm). If the geometry-free combination changes by more
  than 5 cm between epochs, a cycle slip is declared and the ambiguity is reset.

---

#### Max Age of Diff (s) / Outs to Reset Amb

**Current values:** `30.0` / `20`

- **Max Age of Diff:** Used for RTK (not PPP). Irrelevant for your work.
- **Outs to Reset Amb:** If a satellite is absent for more than 20 epochs, reset its ambiguity.
  Prevents using stale ambiguity estimates.

---

#### Outlier Threshold for Code/Phase (m)

**Current values:** `30.0` / `5.0`

If a code (pseudorange) residual exceeds 30 m, the measurement is rejected as an outlier.
If a phase residual exceeds 5 m (a very large threshold), it's rejected.
These are conservative defaults — leave them unless you have specific multipath issues.

---

#### # of Filter Iter / Sync Solution

**Current values:** `1` / `ON`

- **# of Filter Iter:** Number of Kalman filter iterations per epoch. 1 is standard.
- **Sync Solution:** Synchronize output to integer seconds. Keep ON.

---

#### Min Fix Sats / Min Hold Sats

**Current values:** `4` / `5`

- **Min Fix Sats:** Minimum number of fixed ambiguities required before outputting a fixed solution.
- **Min Hold Sats:** Minimum fixed satellites to maintain the hold status.

---

#### Max Pos Var for AR / AR Filter

**Current values:** `0.1000` / `ON`

- **Max Pos Var for AR:** If the position variance exceeds 0.1 m², don't attempt AR — the
  position uncertainty is too large for meaningful ambiguity fixing.
- **AR Filter:** Use additional filtering for AR. Keep ON.

---

### OUTPUT TAB

Controls what the output `.pos` file contains and how it is formatted.

---

#### Solution Format

**Current value:** `Lat/Lon/Height`

| Setting            | Output columns                                            | Best for                |
| ------------------ | --------------------------------------------------------- | ----------------------- |
| **Lat/Lon/Height** | Latitude, Longitude, Ellipsoidal Height (geodetic coords) | **Standard — use this** |
| ECEF-XYZ           | Earth-centered Earth-fixed X, Y, Z coordinates            | Needed for GAMP-style   |
| ENU                | East, North, Up errors (relative to a reference)          | If reference is pre-set |
| NMEA               | NMEA format sentences (like marine GPS)                   | Device integration only |

> Use **Lat/Lon/Height**. This is what RTKPLOT reads natively for ENU error plots.
> When you then open in RTKPLOT and set the reference coordinates, RTKPLOT converts
> to ENU errors automatically.

---

#### Output Header / Process Options / Vel

**Current values:** `ON` / `ON` / `OFF`

- **Output Header:** Writes a header block at the top of the .pos file describing the settings used.
  Keep **ON** — this is how you remember what settings were used for each run.
- **Process Options:** Includes the full processing options in the header. Keep **ON**.
- **Vel:** Output velocity estimates. **OFF** for static PPP.

---

#### Time Format / # of Decimals

**Current values:** `hh:mm:ss GPST` / `3`

- **Time Format:** `hh:mm:ss GPST` (time of day in GPS Time) is standard and readable.
  Alternative: `GPST week seconds` or `UTC`.
- **# of Decimals:** 3 means times are output to millisecond precision (30-second intervals
  need only 0 decimals, but 3 is fine).

---

#### Latitude Longitude Format / Field Separator

**Current values:** `ddd.dddddddddd` / (empty)

- **Lat/Lon Format:** `ddd.dddddddddd` = decimal degrees with 10 decimal places (nanodegree precision). Good.
- **Field Separator:** Space by default (empty field = space). You can set tab or comma if preferred.

---

#### Output Single if Sol Outage / Max Sol Std (m)

**Current values:** `OFF` / `0`

- **Output Single:** When PPP solution is unavailable (no convergence), output a Single Point
  Position instead. Keep **OFF** for pure PPP analysis — you want gaps, not bad positions.
- **Max Sol Std:** Maximum position standard deviation to output. 0 = no limit. Leave at 0.

---

#### Datum / Height

**Current values:** `WGS84` / `Ellipsoidal`

- **Datum:** WGS84 is the GPS reference frame. Keep this.
- **Height:** `Ellipsoidal` = height above the WGS84 ellipsoid (geometric surface).
  `Geodal` = height above mean sea level (requires a geoid model). Use **Ellipsoidal** since
  your reference coordinates are also ellipsoidal.

---

#### Solution for Static Mode

**Current value:** `All`

| Setting | Effect                                  |
| ------- | --------------------------------------- | ------------------------------ |
| All     | Output every epoch's position estimate  | Best for convergence analysis  |
| Single  | Output only one final averaged position | For final static survey result |

> Use **All** — you need the time series to study convergence behavior.

---

#### Output Solution Status / Output Debug Trace

**Current values:** `Residuals` / `OFF`

- **Solution Status:** Set to `Residuals` — this writes a `.stat` sidecar file with
  per-satellite residuals and solution quality statistics. VERY useful for RTKPLOT's
  residual analysis plots.
- **Debug Trace:** OFF for normal runs. Level 1–5 for detailed debugging (very slow, huge files).

---

### STATISTICS TAB

These are the Kalman filter noise parameters. They tell the filter how much to trust
different measurements and how quickly the state is expected to change.

---

#### Code/Phase Error Ratio L1/L2/L5/L6

**Current values:** `300.0` / `300.0` / `300.0` / `300.0`

The ratio of code (pseudorange) noise to phase noise. A ratio of 300 means the filter
trusts code observations 300× less than phase observations.

Why 300? Pseudorange accuracy ≈ 0.3–1 m; carrier phase accuracy ≈ 0.003 m → ratio ≈ 300.

Leave at **300.0** for standard PPP. Increasing this ratio (e.g., 1000) makes the filter
trust code less. Decreasing it (e.g., 100) trusts code more.

---

#### Carrier-Phase Error: a + b/sinEl (m)

**Current values:** `0.003` / `0.003`

Standard deviation of phase measurement noise: σ_phase = a + b/sin(elevation).

- `a` = 0.003 m = base noise of 3 mm
- `b` = 0.003 m = elevation-dependent term (at 90° = 3 mm, at 15° = 3+11.6 = ~12 mm)

This is the fundamental precision of your phase observations. 3 mm is a reasonable
value for a geodetic-grade antenna (which all your IGS stations use).

---

#### Process Noises (1-sigma/sqrt(s))

These define how quickly the Kalman filter states are expected to change.

| Parameter                      | Current Value       | Meaning                                                                                                          |
| ------------------------------ | ------------------- | ---------------------------------------------------------------------------------------------------------------- |
| **Receiver Accel Horiz**       | 3.00E+00 (3.0 m/s²) | How fast the receiver can accelerate horizontally. 3 m/s² = aggressive. For static PPP, this value can be lower. |
| **Receiver Accel Vertical**    | 1.00E+00 (1.0 m/s²) | Vertical acceleration. For static: low.                                                                          |
| **Carrier-Phase Bias**         | 1.00E-04            | How fast ambiguities drift. Small = treat as nearly constant. This is correct for PPP.                           |
| **Vertical Ionospheric Delay** | 1.00E-03            | How fast the ionospheric delay changes. 1 mm/s is reasonable.                                                    |
| **Zenith Tropospheric Delay**  | 1.00E-04            | How fast ZTD changes. 0.1 mm/s is typical.                                                                       |
| **Satellite Clock Stability**  | 5.00E-12            | Allan deviation of satellite clock. 5E-12 s/s is typical for modern GPS clocks.                                  |

> For PPP-Static with truly stationary receivers (IGS sites), you can lower the
> Receiver Accel values to 0.1 or 0.01 m/s², which can slightly improve convergence.
> For your experiments, leave at defaults.

---

### POSITIONS TAB

Sets the known reference position for accuracy evaluation.

---

#### Rover Position

**Current values:** Lat=-90, Lon=0, Ht=-6378137 (these are default "unknown" values)

- **Position Type dropdown:** How to interpret the position field
  - `Average of Single` — Automatically compute from single-point positioning
  - `RINEX Header` — Use the approximate position in the RINEX file header
  - `Lat/Lon/Height` — Manual entry
  - `ECEF-XYZ` — Manual ECEF entry
  - `POSFILE` — Read from a file

> For PPP, the rover position is what you are SOLVING FOR. Leave as default
> (the filter will estimate it from scratch). RTKPOST uses this only as the initial
> seed for PPP — the filter quickly moves away from it.

#### Rover Antenna Type / Delta-E/N/U

**Antenna Type:** Set to `*` (Auto) — RTKLIB reads the antenna type from the RINEX header
and looks it up in the ATX file automatically. This is the best setting.

**Delta-E/N/U:** Offset of the antenna above the reference mark (usually 0 for IGS sites).

---

#### Base Station Position

Leave these at defaults — PPP has no base station.

---

#### Station Position File

A `.pos` file containing known coordinates for multiple stations. RTKLIB reads this file
to set the reference position automatically based on the station name in the RINEX file.

**To use:** Create a text file with format:

```
%  STATION    LATITUDE(deg)   LONGITUDE(deg)  HEIGHT(m)
   KIRU       67.857900       20.967800       390.900
   WUH2       30.531700       114.357000       73.400
   ZIM2       46.877100        7.465000       956.400
   HKWS       22.272200      114.161400        72.000
```

Save as `C:\PPP_PROJECT\config\stations.pos` and load it here.

> This is very useful when processing multiple stations — RTKLIB automatically picks
> the correct reference for each station.

---

### FILES TAB

These auxiliary files improve accuracy.

---

#### Satellite/Receiver Antenna PCV File ANTEX/NGS PCV

**Load:** `C:\PPP_PROJECT\New_Data\DATA_FINAL_ANT_EXTRA\igs20_2401.atx`
(or for Old_Data: `C:\PPP_PROJECT\Old_data\products\atx\igs20_2401.atx`)

**What it does:** Contains phase center offset (PCO) and phase center variation (PCV) for
every satellite and every receiver antenna model. The antenna does not receive signals exactly
at its physical reference point — there are millimeter-to-centimeter offsets that vary
with elevation angle.

**Why critical:** Without this file, your height solution will have a systematic error of
1–3 cm. For highest accuracy, this file is mandatory.

**Two slots shown:** The first slot is for the satellite ATX; the second for the receiver ATX.
Load the same `igs20_2401.atx` file in BOTH slots — it contains both satellite and receiver corrections.

---

#### Geoid Data File

For converting ellipsoidal height to orthometric height (above mean sea level).
Leave **empty** for your research — you are comparing ellipsoidal heights, and your reference
coordinates are also ellipsoidal.

---

#### DCB Data File

Differential Code Biases. For GPS dual-frequency IF combination, this is NOT needed
(the IF combination cancels most code biases). For RTKLIB 2.5.0 with OSB/BIA files,
also not needed separately.

> Leave **empty** for your experiments (the BIA file in the main window covers this).

---

#### EOP Data File

Earth Orientation Parameters — similar to the ERP file. RTKLIB can read EOP format files.
For precise PPP, you can load `COD0MGXFIN_20260150000_01D_12H_ERP.ERP` here, or leave empty
(RTKLIB has built-in EOP prediction for the current era).

---

#### Ocean Tide Loading BLQ File

Corrections for ocean tidal loading deformation. For IGS stations, BLQ files are available from
`http://holt.oso.chalmers.se/loading/`. For your experiments, leave **empty** (the effect
is < 2 cm for inland stations, minor for your convergence study).

---

#### Ionosphere Data File

The IONEX GIM file. Only needed when Ionosphere Correction = IONEX-TEC (Experiment 4, Run C).

**Load:** `C:\PPP_PROJECT\Old_data\products\ionex\COD0OPSFIN_20260150000_01D_01H_GIM.INX`

---

### MISC TAB

Advanced settings, mostly for RTK and DGPS. Most are not relevant for PPP.

---

#### RINEX Opt (Rover) / RINEX Opt (Base)

Optional RINEX processing keywords. For example:

- `-SYS=G` — force use of GPS observations only from the file
- `-SYS=GEC` — use GPS, Galileo, BeiDou

> These can be left empty — the satellite system selection in Setting1 controls which
> constellations are processed. However, if you notice RTKLIB is loading GLONASS even
> when unchecked, adding `-SYS=GEC` here can help.

---

#### PPP Options

Special options string for PPP processing in RTKLIB-EX 2.5.0. The key option:

`-EPHTYPE=CLK13` — Use the 13-column CLK format (needed for some CLK files)

Leave **empty** for standard processing.

---

## 7. RTKPLOT — COMPLETE VALIDATION GUIDE

RTKPLOT is the visualization and analysis tool. Open it:

> `C:\Program Files\RTKLIB_EX_2.5.0\rtkplot.exe`

---

### Loading Your Results

**Method 1 — File menu:**

- `File → Open Solution 1` — load your first `.pos` file
- `File → Open Solution 2` — load a second `.pos` file to overlay for comparison
- For comparing multiple experiments simultaneously, open Solution 1, then Solution 2

**Method 2 — Drag and drop:**

- Drag the `.pos` file directly onto the RTKPLOT window

**Method 3 — From RTKPOST:**

- Click the `Plot...` button in RTKPOST after processing

---

### Setting the Reference Position (Critical Step)

Before any ENU error plot makes sense, you must tell RTKPLOT where the station really is.

1. In RTKPLOT: `Edit → Options` (or just click the gear icon)
2. In the Options dialog, find **"Reference Position"**
3. Enter the coordinates:
   - For KIRU: Lat=67.857900°, Lon=20.967800°, Ht=390.900 m
   - For WUH2: Lat=30.531700°, Lon=114.357000°, Ht=73.400 m
   - For ZIM2: Lat=46.877100°, Lon=7.465000°, Ht=956.400 m
   - For HKWS: Lat=22.272200°, Lon=114.161400°, Ht=72.000 m
4. Click OK

After setting the reference, the Position plot will show **ENU errors** relative to the true position.

---

### Plot Types — All Options Explained

Access via the **Plot Type** dropdown in the toolbar or `View → Plot Type`.

#### Ground Track

Shows the receiver's position trace on a map view (longitude vs latitude).

- For a stationary receiver, this should be a tight cluster of points.
- Early in processing: scattered (unconverged). Later: tight cluster.
- The center of the tight cluster should be the true position.
- **Use for:** Visually confirming convergence and checking for systematic offset.

---

#### Position (ENU Error vs. Time) ← MOST IMPORTANT FOR YOUR RESEARCH

Shows East, North, and Up errors as separate time series.

```
Error (m)
  5 |          E error
  4 |
  3 |             N error
  2 |                U error
  1 |
0.5 |
0.1 |___convergence_line________________________
    0          15min         30min          60min
```

This is the main plot you will use to:

1. Measure convergence time (when does error drop below 10 cm?)
2. Compare GPS-only vs Multi-GNSS convergence
3. Compare broadcast vs precise products accuracy
4. Identify systematic biases (if lines don't converge to zero)

**How to read it:**

- Y-axis: position error in meters (or centimeters after convergence)
- X-axis: time from start of processing
- Three colored lines: E (East), N (North), U (Up/Vertical)
- **Convergence = all three below your threshold (10 cm H, 20 cm V) and staying there**

**Overlay comparison:**

- Load Solution 1 (e.g., broadcast GPS only)
- Load Solution 2 (e.g., precise GPS only)
- RTKPLOT shows both in different colors simultaneously

---

#### Velocity

Shows estimated receiver velocity in E/N/U components.
For static receivers, this should be near zero. Large velocities indicate filter instability.

---

#### Acceleration

Shows estimated receiver acceleration. Should be near zero for static.

---

#### NSat / PDOP (Number of Satellites / Dilution of Precision)

**NSat:** How many satellites are being tracked and used per epoch.

- Important for understanding WHY GPS-only converges slower than multi-GNSS
- More satellites → lower PDOP → faster convergence

**PDOP (Position Dilution of Precision):** Geometric quality factor.

- PDOP < 2.0: Excellent geometry
- PDOP 2–5: Good
- PDOP > 5: Poor — expect large errors
- PDOP > 10: Dangerous — results unreliable

---

#### Residuals

Shows post-fit residuals for each satellite.
After loading a `.pos` file with residuals (Output Solution Status = Residuals), you can
see per-satellite phase and code residuals versus time.

**What to look for:**

- Large systematic residuals: unmodelled biases (bad antenna corrections, wrong DCB, etc.)
- Sudden jumps: cycle slips that weren't detected
- Correlated residuals: multipath or model error

**This view requires:** Output Solution Status = `Residuals` in Options → Output.

---

#### OBS (Observation Data)

Shows the raw observation data quality: SNR (signal strength), multipath, etc.
Only available if RTKPOST has output raw observation data (requires OBS output mode).

---

#### Sky Plot

Shows satellite positions in the sky (azimuth vs elevation) for each epoch.
Helps understand which satellites are contributing to your solution.

**How to read it:**

- Center = zenith (straight up)
- Outer ring = horizon (0° elevation)
- Each colored dot = a satellite at that moment
- Trajectory shows where each satellite moves during the session

---

#### DOP

Shows PDOP, HDOP (horizontal), VDOP (vertical), GDOP (geometric), and TDOP (time) vs time.
These dilution-of-precision values indicate the geometric quality of the satellite constellation.

---

#### SNR (Signal-to-Noise Ratio)

Signal strength of each satellite over time. Lower SNR = noisier observation.

- Good: > 40 dBHz
- Marginal: 30–40 dBHz
- Poor: < 30 dBHz

---

#### SNR/MP (Multipath)

Combined SNR and multipath analysis per satellite.

---

### RTKPLOT Options (Edit → Options)

These are the RTKPLOT display settings.

| Option                 | Effect                                             |
| ---------------------- | -------------------------------------------------- |
| **Reference Position** | Set the true coordinates for ENU error computation |
| **Plot Interval**      | Thin the displayed data for speed                  |
| **Max HDOP/PDOP**      | Filter out epochs with bad geometry                |
| **Quality Filter**     | Show only Fixed (Q=1), Float (Q=2), or All         |
| **Time Range**         | Display only a time window                         |
| **Scale**              | Set axis limits manually                           |
| **Show Statistics**    | Display RMS, mean error in the plot                |

**Quality Filter options:**

- **Q=1 (Fixed/Green):** PPP-AR fixed solution — best
- **Q=2 (Float/Yellow):** Float PPP — standard result
- **Q=3 (SBAS/Blue):** SBAS-corrected
- **Q=4 (DGPS/Blue):** Differential
- **Q=5 (Single/Red):** Single point — worst
- **All:** Show everything

---

### How to Measure Convergence Time in RTKPLOT

1. Open the `.pos` file
2. Select **Position** plot type
3. Set the reference coordinates (Edit → Options)
4. Look at the E and N traces
5. Find the first time where:
   - |E| < 0.10 m AND |N| < 0.10 m simultaneously
   - AND they stay there for at least 10 minutes
6. That time = convergence time. Subtract from the start epoch.
7. Note: RTKPLOT shows absolute values on Y — use **View → Statistics** to get exact RMS values

**Reading convergence time from plot:**

- Right-click on the plot → Mark the convergence point
- Or use `View → Statistics` which shows mean/RMS for the whole period or a selected window

---

### Saving Plots

- `File → Save Image` → saves PNG (for reports)
- `File → Save Text` → saves the plot data as text (for further analysis)
- `Edit → Copy to Clipboard` → copy plot image

---

## 8. RESEARCH EXPERIMENTS — MANUAL STEP-BY-STEP

### BEFORE ANY EXPERIMENT — One-Time Setup

**1. Create the output folder:**

```
mkdir C:\PPP_PROJECT\RTKLIB_work\results
mkdir C:\PPP_PROJECT\config
```

**2. Open RTKPOST-EX 2.5.0:**
`C:\Program Files\RTKLIB_EX_2.5.0\rtkpost.exe`

**3. Save a base configuration to reset from between experiments:**
Configure these base settings in Options, then click **Save** → `C:\PPP_PROJECT\config\base_ppp.conf`

| Tab        | Setting                          | Value                                                         |
| ---------- | -------------------------------- | ------------------------------------------------------------- |
| Setting1   | Positioning Mode                 | PPP Static                                                    |
| Setting1   | Frequencies                      | L1+L2                                                         |
| Setting1   | Filter Type                      | Forward                                                       |
| Setting1   | Elevation Mask                   | 15°                                                           |
| Setting1   | Rec Dynamics                     | ON                                                            |
| Setting1   | Earth Tides                      | OFF                                                           |
| Setting1   | Ionosphere Correction            | Iono-Free LC                                                  |
| Setting1   | Troposphere Correction           | Saastamoinen                                                  |
| Setting1   | Satellite Ephemeris/Clock        | Precise                                                       |
| Setting1   | Sat PCV                          | ✓ Checked                                                     |
| Setting1   | Rec PCV                          | ✓ Checked                                                     |
| Setting1   | PhWU                             | ✓ Checked                                                     |
| Setting1   | Rej Ecl                          | ☐ Unchecked                                                   |
| Setting1   | RAIM FDE                         | ☐ Unchecked                                                   |
| Setting1   | DBCorr                           | ☐ Unchecked                                                   |
| Setting2   | Integer Ambiguity Res (GPS)      | OFF                                                           |
| Setting2   | Integer Ambiguity Res (GLO)      | OFF                                                           |
| Setting2   | Integer Ambiguity Res (BDS)      | OFF                                                           |
| Setting2   | Ratio to Fix                     | 3 / 3 / 3                                                     |
| Setting2   | Min Lock / Elev to Fix           | 0 / 15°                                                       |
| Setting2   | Slip Threshs Geom-Free           | 0.050 m                                                       |
| Setting2   | Outlier Threshold Code/Phase     | 30.0 / 5.0 m                                                  |
| Setting2   | Min Fix Sats / Hold Sats         | 4 / 5                                                         |
| Setting2   | Max Pos Var for AR               | 0.1000                                                        |
| Setting2   | AR Filter                        | ON                                                            |
| Output     | Solution Format                  | Lat/Lon/Height                                                |
| Output     | Output Header                    | ON                                                            |
| Output     | Process Options                  | ON                                                            |
| Output     | Time Format                      | hh:mm:ss GPST                                                 |
| Output     | Lat/Lon Format                   | ddd.dddddddddd                                                |
| Output     | Datum / Height                   | WGS84 / Ellipsoidal                                           |
| Output     | Solution for Static Mode         | All                                                           |
| Output     | Output Solution Status           | Residuals                                                     |
| Output     | Debug Trace                      | OFF                                                           |
| Statistics | Code/Phase Error Ratio           | 300 / 300 / 300 / 300                                         |
| Statistics | Carrier-Phase Error a+b/sinEl    | 0.003 / 0.003                                                 |
| Statistics | Receiver Accel Horiz/Vert        | 3.0 / 1.0 m/s²                                                |
| Statistics | Carrier-Phase Bias               | 1.00E-04                                                      |
| Statistics | Vertical Iono Delay              | 1.00E-03                                                      |
| Statistics | Zenith Trop Delay                | 1.00E-04                                                      |
| Statistics | Satellite Clock Stability        | 5.00E-12                                                      |
| Positions  | Rover Position Type              | RINEX Header Position                                         |
| Positions  | Rover Antenna Type               | \* (Auto)                                                     |
| Positions  | Base Station                     | (leave empty)                                                 |
| Files      | Sat/Rec Antenna PCO (slot 1 & 2) | `C:\PPP_PROJECT\New_Data\DATA_FINAL_ANT_EXTRA\igs20_2401.atx` |
| Files      | Geoid / DCB / EOP / BLQ / Iono   | (leave empty for base)                                        |
| Misc       | Time Interp of Base Station Data | ON                                                            |
| Misc       | RINEX Opt (Rover)                | (empty)                                                       |
| Misc       | PPP Options                      | (empty)                                                       |

---

## EXPERIMENT 1 — Broadcast vs Precise Ephemeris

> **Research Question:** How much does using precise satellite orbits and clocks improve PPP accuracy?
>
> **What changes between runs:** Only "Satellite Ephemeris/Clock" and which product files are loaded.
> Everything else is identical so the comparison is fair.
>
> **Expected results:** Run 1A ~1–5 m final error | Run 1B ~5–15 cm final error

---

### RUN 1A — Broadcast Ephemeris (GPS-only)

#### Step 1 — RTKPOST Main Window: Load Files

| Field                    | Value                                                                        |
| ------------------------ | ---------------------------------------------------------------------------- |
| RINEX OBS (Rover)        | `C:\PPP_PROJECT\New_Data\obs\RNXDATA\KIRU00SWE_R_20260150000_01D_30S_MO.rnx` |
| RINEX OBS (Base Station) | **EMPTY** — PPP has no base station                                          |
| NAV/CLK Row 1            | `C:\PPP_PROJECT\New_Data\nav\BRDC00IGS_R_20260150000_01D_MN.rnx`             |
| NAV/CLK Row 2            | **EMPTY** — no SP3 for broadcast run                                         |
| NAV/CLK Row 3            | **EMPTY** — no CLK for broadcast run                                         |
| NAV/CLK Rows 4–10        | **EMPTY**                                                                    |
| Solution File            | `C:\PPP_PROJECT\RTKLIB_work\results\KIRU_EXP1A_broadcast.pos`                |
| Time Start               | ☐ Unchecked (process full day)                                               |
| Time End                 | ☐ Unchecked (process full day)                                               |
| Interval                 | 0 (use native 30 s file rate)                                                |

#### Step 2 — Options: Setting1 Tab

| Setting                       | Value            | Reason                                                                                |
| ----------------------------- | ---------------- | ------------------------------------------------------------------------------------- |
| Positioning Mode              | **PPP Static**   | Stationary receiver, accumulates filter over time                                     |
| Frequencies                   | **L1+L2**        | Dual frequency enables IF combination when in precise mode; here broadcast model used |
| Filter Type                   | **Forward**      | Process start→end; shows natural convergence                                          |
| Elevation Mask                | **15°**          | Standard; excludes noisy low-elevation signals                                        |
| Rec Dynamics                  | **ON**           | Handles small position perturbations                                                  |
| Earth Tides Correction        | **OFF**          | Minor effect; keep simple for this experiment                                         |
| Ionosphere Correction         | **Broadcast**    | Klobuchar model embedded in nav file — matches broadcast-only scenario                |
| Troposphere Correction        | **Saastamoinen** | Standard formula-based tropospheric correction                                        |
| **Satellite Ephemeris/Clock** | **Broadcast**    | ← KEY: uses the loaded nav file only, NO SP3/CLK                                      |
| Sat PCV                       | **☐ Unchecked**  | No ATX file loaded — leave off                                                        |
| Rec PCV                       | **☐ Unchecked**  | No ATX file loaded — leave off                                                        |
| PhWU                          | **☐ Unchecked**  | Leave off for broadcast baseline                                                      |
| Rej Ecl                       | **☐ Unchecked**  | Leave off                                                                             |
| RAIM FDE                      | **☐ Unchecked**  | Leave off                                                                             |
| DBCorr                        | **☐ Unchecked**  | Leave off                                                                             |
| Excluded Satellites           | (empty)          |                                                                                       |
| GPS                           | **✓ Checked**    |                                                                                       |
| GLONASS                       | **☐ Unchecked**  | GPS only for this experiment                                                          |
| Galileo                       | **☐ Unchecked**  |                                                                                       |
| QZSS                          | **☐ Unchecked**  |                                                                                       |
| BDS                           | **☐ Unchecked**  |                                                                                       |
| NavIC                         | **☐ Unchecked**  |                                                                                       |
| SBAS                          | **☐ Unchecked**  |                                                                                       |

#### Step 3 — Options: Setting2 Tab

| Setting                          | Value           | Reason                                      |
| -------------------------------- | --------------- | ------------------------------------------- |
| Integer Ambiguity Res (GPS)      | **OFF**         | Float PPP — no AR with broadcast products   |
| Integer Ambiguity Res (GLO)      | **OFF**         |                                             |
| Integer Ambiguity Res (BDS)      | **OFF**         |                                             |
| Ratio to Fix                     | 3 / 3 / 3       | (irrelevant when AR = OFF, keep at default) |
| GLO HW Bias                      | 0               | Default                                     |
| Min Lock / Elev to Fix Amb       | 0 / 15°         | Default                                     |
| Min Fix / Elev to Hold Amb       | 20 / 15°        | Default                                     |
| Slip Threshs Doppler / Geom-Free | 0.000 / 0.050   | Default                                     |
| Max Age of Diff / Outs to Reset  | 30.0 / 20       | Default                                     |
| Outlier Threshold Code / Phase   | 30.0 / 5.0 m    | Default                                     |
| # of Filter Iter                 | 1               | Default                                     |
| Min Fix Sats / Hold Sats         | 4 / 5           | Default                                     |
| Min Drop Sats                    | 10              | Default                                     |
| Max Pos Var for AR / AR Filter   | 0.1000 / ON     | Default                                     |
| Hold Amb Var / Gain              | 0.1000 / 0.0100 | Default                                     |

#### Step 4 — Options: Output Tab

| Setting                     | Value                                                        |
| --------------------------- | ------------------------------------------------------------ |
| Solution Format             | Lat/Lon/Height                                               |
| Output Header               | ON                                                           |
| Process Options             | ON                                                           |
| Vel                         | OFF                                                          |
| Time Format                 | hh:mm:ss GPST                                                |
| # of Decimals               | 3                                                            |
| Lat/Lon Format              | ddd.dddddddddd                                               |
| Field Separator             | (empty = space)                                              |
| Output Single if Sol Outage | OFF                                                          |
| Max Sol Std                 | 0                                                            |
| Datum                       | WGS84                                                        |
| Height                      | Ellipsoidal                                                  |
| Solution for Static Mode    | All                                                          |
| Output Solution Status      | **Residuals** (creates .stat file for RTKPLOT residual view) |
| Output Debug Trace          | OFF                                                          |

#### Step 5 — Options: Statistics Tab

Leave all values at defaults (as saved in `base_ppp.conf`).

| Setting                            | Value                 |
| ---------------------------------- | --------------------- |
| Code/Phase Error Ratio L1/L2/L5/L6 | 300 / 300 / 300 / 300 |
| Carrier-Phase Error a+b/sinEl      | 0.003 / 0.003         |
| Carrier-Phase Error Baseline       | 0.000                 |
| Carrier Phase Error SNR / max      | 0.000 / 52.000        |
| Doppler Freq Error                 | 1.000                 |
| Receiver Accel Horiz               | 3.00E+00              |
| Receiver Accel Vert                | 1.00E+00              |
| Carrier-Phase Bias                 | 1.00E-04              |
| Vertical Iono Delay                | 1.00E-03              |
| Zenith Trop Delay                  | 1.00E-04              |
| Satellite Clock Stability          | 5.00E-12              |

#### Step 6 — Options: Positions Tab

| Setting               | Value                    | Reason                                                                               |
| --------------------- | ------------------------ | ------------------------------------------------------------------------------------ |
| Rover Position Type   | RINEX Header Position    | Let RTKLIB read the approximate position from the obs file header as the filter seed |
| Rover Latitude        | (auto-filled from RINEX) |                                                                                      |
| Rover Longitude       | (auto-filled from RINEX) |                                                                                      |
| Rover Height          | (auto-filled from RINEX) |                                                                                      |
| Rover Antenna Type    | \* (Auto)                | Reads from RINEX header, looks up in ATX                                             |
| Rover Delta-E/N/U     | 0.0 / 0.0 / 0.0          | No ARP offset for IGS stations                                                       |
| Base Station          | (all empty)              | PPP has no base station                                                              |
| Station Position File | (empty)                  |                                                                                      |

#### Step 7 — Options: Files Tab

| Field                          | Value       | Reason                            |
| ------------------------------ | ----------- | --------------------------------- |
| Satellite Antenna PCO (slot 1) | **(empty)** | No ATX for broadcast-only run     |
| Receiver Antenna PCO (slot 2)  | **(empty)** | No ATX for broadcast-only run     |
| Geoid Data File                | (empty)     | Not needed                        |
| DCB Data File                  | (empty)     | Not needed for broadcast run      |
| EOP Data File                  | (empty)     |                                   |
| Ocean Tide BLQ File            | (empty)     |                                   |
| Ionosphere Data File           | (empty)     | Klobuchar is embedded in nav file |

#### Step 8 — Options: Misc Tab

| Setting                                 | Value   |
| --------------------------------------- | ------- |
| Time Interpolation of Base Station Data | ON      |
| SBAS Satellite Selection                | 0       |
| RINEX Opt (Rover)                       | (empty) |
| RINEX Opt (Base)                        | (empty) |
| PPP Options                             | (empty) |

#### Step 9 — Execute and Save Config

1. Click **OK** to close Options
2. Click **Execute ▶**
3. Watch the log — you should see epoch-by-epoch output
4. When done: **Options → Save → `C:\PPP_PROJECT\config\exp1A_broadcast.conf`**

**Output file produced:** `C:\PPP_PROJECT\RTKLIB_work\results\KIRU_EXP1A_broadcast.pos`

---

### RUN 1B — Precise Ephemeris (GPS-only)

#### Step 1 — RTKPOST Main Window: Load Files

| Field                    | Value                                                                                 |
| ------------------------ | ------------------------------------------------------------------------------------- |
| RINEX OBS (Rover)        | `C:\PPP_PROJECT\New_Data\obs\RNXDATA\KIRU00SWE_R_20260150000_01D_30S_MO.rnx`          |
| RINEX OBS (Base Station) | **EMPTY**                                                                             |
| NAV/CLK Row 1            | `C:\PPP_PROJECT\New_Data\nav\BRDC00IGS_R_20260150000_01D_MN.rnx`                      |
| NAV/CLK Row 2            | `C:\PPP_PROJECT\New_Data\DATA_FINAL_ANT_EXTRA\COD0MGXFIN_20260150000_01D_05M_ORB.SP3` |
| NAV/CLK Row 3            | `C:\PPP_PROJECT\New_Data\DATA_FINAL_ANT_EXTRA\COD0MGXFIN_20260150000_01D_30S_CLK.CLK` |
| NAV/CLK Rows 4–10        | EMPTY                                                                                 |
| Solution File            | `C:\PPP_PROJECT\RTKLIB_work\results\KIRU_EXP1B_precise.pos`                           |
| Time Start / End         | ☐ Unchecked (full day)                                                                |

#### Step 2 — Options: Setting1 Tab

| Setting                       | Value            | Reason                                                     |
| ----------------------------- | ---------------- | ---------------------------------------------------------- |
| Positioning Mode              | **PPP Static**   |                                                            |
| Frequencies                   | **L1+L2**        | Enables ionosphere-free (IF) combination                   |
| Filter Type                   | **Forward**      |                                                            |
| Elevation Mask                | **15°**          |                                                            |
| Rec Dynamics                  | **ON**           |                                                            |
| Earth Tides Correction        | **OFF**          |                                                            |
| Ionosphere Correction         | **Iono-Free LC** | ← KEY: mathematically cancels ionosphere using L1+L2       |
| Troposphere Correction        | **Saastamoinen** |                                                            |
| **Satellite Ephemeris/Clock** | **Precise**      | ← KEY: uses the SP3+CLK files you loaded                   |
| Sat PCV                       | **✓ Checked**    | ATX file loaded — apply satellite phase centre corrections |
| Rec PCV                       | **✓ Checked**    | ATX file loaded — apply receiver antenna corrections       |
| PhWU                          | **✓ Checked**    | Correct phase wind-up (~few cm)                            |
| Rej Ecl                       | **☐ Unchecked**  |                                                            |
| RAIM FDE                      | **☐ Unchecked**  |                                                            |
| DBCorr                        | **☐ Unchecked**  |                                                            |
| GPS                           | **✓ Checked**    |                                                            |
| GLONASS                       | **☐ Unchecked**  | GPS only — same as 1A for fair comparison                  |
| Galileo                       | **☐ Unchecked**  |                                                            |
| QZSS                          | **☐ Unchecked**  |                                                            |
| BDS                           | **☐ Unchecked**  |                                                            |

#### Step 3 — Options: Setting2 Tab

Same as Run 1A (all AR = OFF, all defaults). No change.

#### Step 4 — Options: Output Tab

Same as Run 1A. All defaults.

#### Step 5 — Options: Statistics Tab

Same as Run 1A. All defaults.

#### Step 6 — Options: Positions Tab

Same as Run 1A. Rover = RINEX Header Position, Base empty.

#### Step 7 — Options: Files Tab

| Field                          | Value                                                         | Reason                                           |
| ------------------------------ | ------------------------------------------------------------- | ------------------------------------------------ |
| Satellite Antenna PCO (slot 1) | `C:\PPP_PROJECT\New_Data\DATA_FINAL_ANT_EXTRA\igs20_2401.atx` | ← KEY: satellite phase centre corrections        |
| Receiver Antenna PCO (slot 2)  | `C:\PPP_PROJECT\New_Data\DATA_FINAL_ANT_EXTRA\igs20_2401.atx` | ← KEY: receiver antenna phase centre corrections |
| Geoid Data File                | (empty)                                                       |                                                  |
| DCB Data File                  | (empty)                                                       | IF combination removes most code biases          |
| EOP Data File                  | (empty)                                                       |                                                  |
| Ocean Tide BLQ File            | (empty)                                                       |                                                  |
| Ionosphere Data File           | (empty)                                                       | IF combination does not need IONEX               |

#### Step 8 — Options: Misc Tab

Same as Run 1A. All defaults.

#### Step 9 — Execute and Save Config

1. Click **OK**, then **Execute ▶**
2. **Options → Save → `C:\PPP_PROJECT\config\exp1B_precise.conf`**

**Output file produced:** `C:\PPP_PROJECT\RTKLIB_work\results\KIRU_EXP1B_precise.pos`

---

### EXPERIMENT 1 — Comparison in RTKPLOT

**Files to compare:**

| Solution   | File                       | Label         |
| ---------- | -------------------------- | ------------- |
| Solution 1 | `KIRU_EXP1A_broadcast.pos` | Broadcast GPS |
| Solution 2 | `KIRU_EXP1B_precise.pos`   | Precise GPS   |

**Steps in RTKPLOT:**

1. Open `C:\Program Files\RTKLIB_EX_2.5.0\rtkplot.exe`
2. `File → Open Solution 1` → select `KIRU_EXP1A_broadcast.pos`
3. `File → Open Solution 2` → select `KIRU_EXP1B_precise.pos`
4. `Edit → Options`:
   - **Receiver Position:** Lat/Lon/Height (deg/m)
   - Latitude: **67.857900**
   - Longitude: **20.967800**
   - Height: **390.900** m
   - Quality Filter: **All** (so you see all solution types)
5. Select Plot Type: **Position**
6. Observe:
   - Solution 1 (orange/red): settles ~1–5 m from zero — systematic broadcast error
   - Solution 2 (blue): converges toward zero within 20–40 min — this is PPP convergence
7. Switch to Plot Type: **NSat** → confirm both use the same number of GPS satellites
8. `View → Statistics` → note RMS values for both solutions
9. `File → Save Image` → save as `KIRU_EXP1_comparison.png`

**What to record in your report:**

| Metric                        | Run 1A (Broadcast) | Run 1B (Precise) |
| ----------------------------- | ------------------ | ---------------- |
| Final East error (m)          |                    |                  |
| Final North error (m)         |                    |                  |
| Final Up error (m)            |                    |                  |
| RMS Horizontal (last 2h)      |                    |                  |
| RMS Vertical (last 2h)        |                    |                  |
| Time to converge to < 10 cm H | — (may never)      | \_\_\_ min       |

**Repeat with WUH2:** Swap the obs file to `WUH200CHN_R_20260150000_01D_30S_MO.rnx`, change reference to Lat=30.531700 Lon=114.357000 Ht=73.400, save outputs as `WUH2_EXP1A_broadcast.pos` and `WUH2_EXP1B_precise.pos`.

---

## EXPERIMENT 2 — GPS-only vs Multi-GNSS

> **Research Question:** How does using more satellite constellations affect convergence time?
>
> **What changes between runs:** Only the "Satellite Systems" checkboxes. Every other setting is identical.
>
> **Expected results:** GPS-only ~25–40 min | GPS+GAL ~15–25 min | GPS+GAL+BDS ~8–20 min

All four runs use the same precise products. The only thing that changes is which satellite system checkboxes are ticked in Setting1.

---

### RUN 2A — GPS Only (Precise)

#### Step 1 — RTKPOST Main Window: Load Files

| Field                    | Value                                                                                 |
| ------------------------ | ------------------------------------------------------------------------------------- |
| RINEX OBS (Rover)        | `C:\PPP_PROJECT\New_Data\obs\RNXDATA\KIRU00SWE_R_20260150000_01D_30S_MO.rnx`          |
| RINEX OBS (Base Station) | EMPTY                                                                                 |
| NAV/CLK Row 1            | `C:\PPP_PROJECT\New_Data\nav\BRDC00IGS_R_20260150000_01D_MN.rnx`                      |
| NAV/CLK Row 2            | `C:\PPP_PROJECT\New_Data\DATA_FINAL_ANT_EXTRA\COD0MGXFIN_20260150000_01D_05M_ORB.SP3` |
| NAV/CLK Row 3            | `C:\PPP_PROJECT\New_Data\DATA_FINAL_ANT_EXTRA\COD0MGXFIN_20260150000_01D_30S_CLK.CLK` |
| NAV/CLK Rows 4–10        | EMPTY                                                                                 |
| Solution File            | `C:\PPP_PROJECT\RTKLIB_work\results\KIRU_EXP2A_GPS.pos`                               |
| Time Start / End         | ☐ Unchecked (full day)                                                                |

#### Steps 2–8 — Options Tabs

**Setting1 Tab:**

| Setting                   | Value           |
| ------------------------- | --------------- |
| Positioning Mode          | PPP Static      |
| Frequencies               | L1+L2           |
| Filter Type               | Forward         |
| Elevation Mask            | 15°             |
| Rec Dynamics              | ON              |
| Earth Tides               | OFF             |
| Ionosphere Correction     | Iono-Free LC    |
| Troposphere Correction    | Saastamoinen    |
| Satellite Ephemeris/Clock | Precise         |
| Sat PCV                   | ✓ Checked       |
| Rec PCV                   | ✓ Checked       |
| PhWU                      | ✓ Checked       |
| Rej Ecl                   | ☐ Unchecked     |
| RAIM FDE                  | ☐ Unchecked     |
| **GPS**                   | **✓ Checked**   |
| **GLONASS**               | **☐ Unchecked** |
| **Galileo**               | **☐ Unchecked** |
| **QZSS**                  | **☐ Unchecked** |
| **BDS**                   | **☐ Unchecked** |

**Setting2, Output, Statistics, Misc Tabs:** All defaults (same as base_ppp.conf).

**Positions Tab:** Rover = RINEX Header Position. Base = empty.

**Files Tab:**

| Field                          | Value                                                         |
| ------------------------------ | ------------------------------------------------------------- |
| Satellite Antenna PCO (slot 1) | `C:\PPP_PROJECT\New_Data\DATA_FINAL_ANT_EXTRA\igs20_2401.atx` |
| Receiver Antenna PCO (slot 2)  | `C:\PPP_PROJECT\New_Data\DATA_FINAL_ANT_EXTRA\igs20_2401.atx` |
| All others                     | (empty)                                                       |

**Execute → Save config:** `C:\PPP_PROJECT\config\exp2A_GPS.conf`

**Output:** `C:\PPP_PROJECT\RTKLIB_work\results\KIRU_EXP2A_GPS.pos`

---

### RUN 2B — GPS + Galileo

Settings are **identical to Run 2A** except the satellite systems:

**Setting1 — Satellite Systems only change:**

| System      | Value                 |
| ----------- | --------------------- |
| **GPS**     | **✓ Checked**         |
| **GLONASS** | **☐ Unchecked**       |
| **Galileo** | **✓ Checked** ← added |
| QZSS        | ☐ Unchecked           |
| BDS         | ☐ Unchecked           |

All other settings, all other tabs: identical to Run 2A.

**Output file:** `C:\PPP_PROJECT\RTKLIB_work\results\KIRU_EXP2B_GE.pos`
**Save config:** `C:\PPP_PROJECT\config\exp2B_GE.conf`

---

### RUN 2C — GPS + Galileo + BDS (Recommended)

**Setting1 — Satellite Systems only change:**

| System      | Value                 |
| ----------- | --------------------- |
| **GPS**     | **✓ Checked**         |
| GLONASS     | ☐ Unchecked           |
| **Galileo** | **✓ Checked**         |
| QZSS        | ☐ Unchecked           |
| **BDS**     | **✓ Checked** ← added |

All other settings identical to Run 2A.

**Output file:** `C:\PPP_PROJECT\RTKLIB_work\results\KIRU_EXP2C_GEC.pos`
**Save config:** `C:\PPP_PROJECT\config\exp2C_GEC.conf`

---

### RUN 2D — All Systems (GPS + GLONASS + Galileo + QZSS + BDS)

**Setting1 — Satellite Systems only change:**

| System      | Value                 |
| ----------- | --------------------- |
| **GPS**     | **✓ Checked**         |
| **GLONASS** | **✓ Checked** ← added |
| **Galileo** | **✓ Checked**         |
| **QZSS**    | **✓ Checked** ← added |
| **BDS**     | **✓ Checked**         |

All other settings identical to Run 2A.

**Output file:** `C:\PPP_PROJECT\RTKLIB_work\results\KIRU_EXP2D_GRCEQ.pos`
**Save config:** `C:\PPP_PROJECT\config\exp2D_GRCEQ.conf`

---

### EXPERIMENT 2 — Comparison in RTKPLOT

**Files to compare (open all in sequence):**

| RTKPLOT Slot | File                 | Label         |
| ------------ | -------------------- | ------------- |
| Solution 1   | `KIRU_EXP2A_GPS.pos` | GPS only      |
| Solution 2   | `KIRU_EXP2B_GE.pos`  | GPS + Galileo |

> RTKPLOT only supports 2 overlapping solutions at once. To compare all four, open pairs:
> (2A vs 2C), then (2B vs 2D), then note convergence times manually.

**Reference Position (same for all Exp 2 runs):**

- Latitude: **67.857900**
- Longitude: **20.967800**
- Height: **390.900** m

**In RTKPLOT:**

1. `Edit → Options` → set reference position above, Quality Filter = All
2. Plot Type: **Position** — observe convergence curves
3. Plot Type: **NSat** — directly see that GPS-only has ~8 satellites; GPS+GAL+BDS has ~25+
4. Plot Type: **DOP** — lower PDOP for multi-GNSS = better geometry
5. `View → Statistics` → record RMS and convergence time for each

**What to record:**

| Metric                 | 2A GPS | 2B G+E | 2C G+E+C | 2D All |
| ---------------------- | ------ | ------ | -------- | ------ |
| Avg satellites visible |        |        |          |        |
| Avg PDOP               |        |        |          |        |
| Convergence time (min) |        |        |          |        |
| Final East RMS (cm)    |        |        |          |        |
| Final North RMS (cm)   |        |        |          |        |
| Final Up RMS (cm)      |        |        |          |        |

---

## EXPERIMENT 3 — Float PPP vs PPP-AR

> **Research Question:** Does integer ambiguity resolution (PPP-AR) improve convergence time?
>
> **What changes:** Setting2 AR mode + loading the OSB.BIA file.
>
> **⚠️ Known Limitation — RTKLIB-EX 2.5.0 with IGS OSB products:**
> PPP-AR does **not** activate in RTKLIB-EX 2.5.0 when using COD or WUM OSB-format phase
> bias files. The AR ratio remains permanently at 0.0 (no fixing). This is because RTKLIB-EX
> requires FCB/IRC-format integer phase biases (historically from CNES/CLS), not the OSB
> nanosecond-format biases currently distributed by IGS analysis centres.
>
> **Result:** Runs 3A and 3B are identical in practice — both produce Q=6 float PPP, 100% of epochs.
>
> **Recommended approach:** Use **PRIDE-PPP-AR** for a genuine float vs fixed comparison.
> PRIDE natively supports COD OSB phase biases and delivers true Q=1 integer-fixed solutions.
> The RTKLIB steps below are still documented for completeness and reproducibility.

> **Tool required:** RTKLIB-EX 2.5.0 (RTKLIB 2.4.3 cannot load BIA files).
>
> **Expected results:** Float ~15–25 min | PPP-AR ~5–15 min

---

### RUN 3A — Float PPP (No Ambiguity Resolution)

#### Step 1 — RTKPOST Main Window: Load Files

| Field                    | Value                                                                                 |
| ------------------------ | ------------------------------------------------------------------------------------- |
| RINEX OBS (Rover)        | `C:\PPP_PROJECT\New_Data\obs\RNXDATA\KIRU00SWE_R_20260150000_01D_30S_MO.rnx`          |
| RINEX OBS (Base Station) | EMPTY                                                                                 |
| NAV/CLK Row 1            | `C:\PPP_PROJECT\New_Data\nav\BRDC00IGS_R_20260150000_01D_MN.rnx`                      |
| NAV/CLK Row 2            | `C:\PPP_PROJECT\New_Data\DATA_FINAL_ANT_EXTRA\COD0MGXFIN_20260150000_01D_05M_ORB.SP3` |
| NAV/CLK Row 3            | `C:\PPP_PROJECT\New_Data\DATA_FINAL_ANT_EXTRA\COD0MGXFIN_20260150000_01D_30S_CLK.CLK` |
| NAV/CLK Row 4            | **EMPTY** — no BIA file for float run                                                 |
| NAV/CLK Rows 5–10        | EMPTY                                                                                 |
| Solution File            | `C:\PPP_PROJECT\RTKLIB_work\results\KIRU_EXP3A_float.pos`                             |
| Time Start / End         | ☐ Unchecked                                                                           |

#### Setting1 Tab

| Setting                   | Value        |
| ------------------------- | ------------ |
| Positioning Mode          | PPP Static   |
| Frequencies               | L1+L2        |
| Filter Type               | Forward      |
| Elevation Mask            | 15°          |
| Rec Dynamics              | ON           |
| Earth Tides               | OFF          |
| Ionosphere Correction     | Iono-Free LC |
| Troposphere Correction    | Saastamoinen |
| Satellite Ephemeris/Clock | Precise      |
| Sat PCV                   | ✓ Checked    |
| Rec PCV                   | ✓ Checked    |
| PhWU                      | ✓ Checked    |
| GPS                       | ✓ Checked    |
| GLONASS                   | ☐ Unchecked  |
| Galileo                   | ✓ Checked    |
| QZSS                      | ☐ Unchecked  |
| BDS                       | ✓ Checked    |

#### Setting2 Tab — KEY DIFFERENCE FOR THIS RUN

| Setting                         | Value     | Reason                   |
| ------------------------------- | --------- | ------------------------ |
| **Integer Ambiguity Res (GPS)** | **OFF**   | ← No AR — float solution |
| **Integer Ambiguity Res (GLO)** | **OFF**   |                          |
| **Integer Ambiguity Res (BDS)** | **OFF**   |                          |
| Ratio to Fix                    | 3 / 3 / 3 | (irrelevant when OFF)    |
| All other Setting2 values       | defaults  |                          |

#### Output, Statistics, Positions, Misc Tabs

All defaults. Same as base_ppp.conf.

#### Files Tab

| Field                          | Value                                                         |
| ------------------------------ | ------------------------------------------------------------- |
| Satellite Antenna PCO (slot 1) | `C:\PPP_PROJECT\New_Data\DATA_FINAL_ANT_EXTRA\igs20_2401.atx` |
| Receiver Antenna PCO (slot 2)  | `C:\PPP_PROJECT\New_Data\DATA_FINAL_ANT_EXTRA\igs20_2401.atx` |
| All others                     | (empty)                                                       |

**Execute → Save config:** `C:\PPP_PROJECT\config\exp3A_float.conf`

**Output:** `C:\PPP_PROJECT\RTKLIB_work\results\KIRU_EXP3A_float.pos`

---

### RUN 3B — PPP-AR (Integer Ambiguity Resolution)

#### Step 1 — RTKPOST Main Window: Load Files

| Field                    | Value                                                                                           |
| ------------------------ | ----------------------------------------------------------------------------------------------- |
| RINEX OBS (Rover)        | `C:\PPP_PROJECT\New_Data\obs\RNXDATA\KIRU00SWE_R_20260150000_01D_30S_MO.rnx`                    |
| RINEX OBS (Base Station) | EMPTY                                                                                           |
| NAV/CLK Row 1            | `C:\PPP_PROJECT\New_Data\nav\BRDC00IGS_R_20260150000_01D_MN.rnx`                                |
| NAV/CLK Row 2            | `C:\PPP_PROJECT\New_Data\DATA_FINAL_ANT_EXTRA\COD0MGXFIN_20260150000_01D_05M_ORB.SP3`           |
| NAV/CLK Row 3            | `C:\PPP_PROJECT\New_Data\DATA_FINAL_ANT_EXTRA\COD0MGXFIN_20260150000_01D_30S_CLK.CLK`           |
| **NAV/CLK Row 4**        | **`C:\PPP_PROJECT\New_Data\DATA_FINAL_ANT_EXTRA\COD0MGXFIN_20260150000_01D_01D_OSB.BIA`** ← KEY |
| NAV/CLK Rows 5–10        | EMPTY                                                                                           |
| Solution File            | `C:\PPP_PROJECT\RTKLIB_work\results\KIRU_EXP3B_PPPAR.pos`                                       |
| Time Start / End         | ☐ Unchecked                                                                                     |

#### Setting1 Tab

Identical to Run 3A. No changes.

#### Setting2 Tab — KEY DIFFERENCE FOR THIS RUN

| Setting                          | Value           | Reason                                                 |
| -------------------------------- | --------------- | ------------------------------------------------------ |
| **Integer Ambiguity Res (GPS)**  | **Continuous**  | ← KEY: try to fix GPS ambiguities every epoch          |
| **Integer Ambiguity Res (GLO)**  | **OFF**         | GLONASS AR needs hardware bias calibration — leave off |
| **Integer Ambiguity Res (BDS)**  | **ON**          | Enable BDS ambiguity resolution                        |
| **Ratio to Fix Ambiguity (Min)** | **3**           | Minimum ratio for candidate acceptance                 |
| **Ratio to Fix Ambiguity (Nom)** | **3**           | Nominal ratio threshold                                |
| **Ratio to Fix Ambiguity (Max)** | **3**           | Maximum ratio threshold                                |
| GLO HW Bias                      | 0               | No GLONASS AR so this is irrelevant                    |
| Min Lock / Elev to Fix Amb       | 0 / 15°         | Start attempting fix immediately                       |
| Min Fix / Elev to Hold Amb       | 20 / 15°        | Hold fix after 20 consecutive fixed epochs             |
| Slip Threshs Geom-Free           | 0.050 m         | Reset ambiguity if GF combination jumps >5 cm          |
| Outlier Threshold Code / Phase   | 30.0 / 5.0      | Default                                                |
| Min Fix Sats / Hold Sats         | 4 / 5           | Need ≥4 fixed sats before reporting a fixed solution   |
| Max Pos Var for AR               | 0.1000 m²       | Don't attempt AR if position variance too large        |
| AR Filter                        | ON              | Additional AR quality filter                           |
| Hold Amb Var / Gain              | 0.1000 / 0.0100 | Default                                                |

#### Output, Statistics, Positions, Misc Tabs

All identical to Run 3A. No changes.

#### Files Tab

| Field                          | Value                                                         |
| ------------------------------ | ------------------------------------------------------------- |
| Satellite Antenna PCO (slot 1) | `C:\PPP_PROJECT\New_Data\DATA_FINAL_ANT_EXTRA\igs20_2401.atx` |
| Receiver Antenna PCO (slot 2)  | `C:\PPP_PROJECT\New_Data\DATA_FINAL_ANT_EXTRA\igs20_2401.atx` |
| All others                     | (empty)                                                       |

**Execute → Save config:** `C:\PPP_PROJECT\config\exp3B_PPPAR.conf`

**Output:** `C:\PPP_PROJECT\RTKLIB_work\results\KIRU_EXP3B_PPPAR.pos`

---

### EXPERIMENT 3 — Comparison in RTKPLOT

**Files to compare:**

| RTKPLOT Slot | File                   | Label     |
| ------------ | ---------------------- | --------- |
| Solution 1   | `KIRU_EXP3A_float.pos` | Float PPP |
| Solution 2   | `KIRU_EXP3B_PPPAR.pos` | PPP-AR    |

**Reference Position:**

- Latitude: **67.857900** | Longitude: **20.967800** | Height: **390.900** m

**Steps in RTKPLOT:**

1. Load both solutions
2. `Edit → Options` → set Reference Position, Quality Filter = **All**
3. Plot Type: **Position** — compare convergence curves
   - Float (Solution 1): all yellow (Q=2) points; slower convergence
   - PPP-AR (Solution 2): yellow early, switching to **green (Q=1 Fixed)** once AR resolves
4. Plot Type: **Ground Track** — fixed points (green) should be tighter cluster
5. `View → Statistics` → record RMS and time of first fixed epoch

**Solution quality colours to interpret:**

- 🟢 Green = Q=1 Fixed (AR resolved) — best quality
- 🟡 Yellow = Q=2 Float — converging but not fixed
- 🔴 Red = Q=5 Single — unconverged / no solution

**What to record:**

| Metric                        | 3A Float   | 3B PPP-AR  |
| ----------------------------- | ---------- | ---------- |
| Time to first Q=1 fix (min)   | N/A        | \_\_\_ min |
| % of epochs fixed (Q=1)       | 0%         | \_\_\_%    |
| Convergence time (< 10 cm H)  | \_\_\_ min | \_\_\_ min |
| Final East RMS, last 2h (cm)  |            |            |
| Final North RMS, last 2h (cm) |            |            |
| Final Up RMS, last 2h (cm)    |            |            |

---

## EXPERIMENT 4 — Ionosphere Correction Methods

> **Research Question:** How does the ionosphere correction method affect PPP accuracy?
>
> **What changes:** Frequencies (L1 vs L1+L2), Ionosphere Correction mode, which product files are loaded.
>
> **Expected results:** 4A (single-freq + Klobuchar) ~1–5 m | 4C (single-freq + GIM) ~0.5–2 m | 4B (dual-freq IF) ~5–15 cm

---

### RUN 4A — Single-Frequency, Klobuchar Ionosphere (Broadcast)

#### Step 1 — RTKPOST Main Window: Load Files

| Field                    | Value                                                                        |
| ------------------------ | ---------------------------------------------------------------------------- |
| RINEX OBS (Rover)        | `C:\PPP_PROJECT\New_Data\obs\RNXDATA\KIRU00SWE_R_20260150000_01D_30S_MO.rnx` |
| RINEX OBS (Base Station) | EMPTY                                                                        |
| NAV/CLK Row 1            | `C:\PPP_PROJECT\New_Data\nav\BRDC00IGS_R_20260150000_01D_MN.rnx`             |
| NAV/CLK Rows 2–10        | **EMPTY** — broadcast-only run, no SP3/CLK                                   |
| Solution File            | `C:\PPP_PROJECT\RTKLIB_work\results\KIRU_EXP4A_L1_Klobuchar.pos`             |
| Time Start / End         | ☐ Unchecked                                                                  |

#### Setting1 Tab

| Setting                       | Value         | Reason                                           |
| ----------------------------- | ------------- | ------------------------------------------------ |
| Positioning Mode              | PPP Static    |                                                  |
| **Frequencies**               | **L1**        | ← KEY: single-frequency only                     |
| Filter Type                   | Forward       |                                                  |
| Elevation Mask                | 15°           |                                                  |
| Rec Dynamics                  | ON            |                                                  |
| Earth Tides                   | OFF           |                                                  |
| **Ionosphere Correction**     | **Broadcast** | ← KEY: Klobuchar 8-parameter model from nav file |
| Troposphere Correction        | Saastamoinen  |                                                  |
| **Satellite Ephemeris/Clock** | **Broadcast** | Broadcast nav only; no SP3/CLK loaded            |
| Sat PCV                       | ☐ Unchecked   | No ATX for this run                              |
| Rec PCV                       | ☐ Unchecked   |                                                  |
| PhWU                          | ☐ Unchecked   |                                                  |
| GPS                           | ✓ Checked     |                                                  |
| GLONASS                       | ☐ Unchecked   |                                                  |
| Galileo                       | ☐ Unchecked   | GPS only for ionosphere comparison               |
| QZSS                          | ☐ Unchecked   |                                                  |
| BDS                           | ☐ Unchecked   |                                                  |

#### Setting2 Tab

All AR = OFF. All defaults.

#### Output Tab

All defaults (same as base_ppp.conf).

#### Statistics Tab

All defaults.

#### Positions Tab

Rover = RINEX Header Position. Base = empty.

#### Files Tab

| Field                          | Value                                                            |
| ------------------------------ | ---------------------------------------------------------------- |
| Satellite Antenna PCO (slot 1) | **(empty)**                                                      |
| Receiver Antenna PCO (slot 2)  | **(empty)**                                                      |
| Ionosphere Data File           | **(empty)** — Klobuchar is in the nav file, not a separate IONEX |
| All others                     | (empty)                                                          |

#### Misc Tab

All defaults.

**Execute → Save config:** `C:\PPP_PROJECT\config\exp4A_L1_Klobuchar.conf`

**Output:** `C:\PPP_PROJECT\RTKLIB_work\results\KIRU_EXP4A_L1_Klobuchar.pos`

---

### RUN 4B — Dual-Frequency, Ionosphere-Free (Standard PPP)

#### Step 1 — RTKPOST Main Window: Load Files

| Field                    | Value                                                                                 |
| ------------------------ | ------------------------------------------------------------------------------------- |
| RINEX OBS (Rover)        | `C:\PPP_PROJECT\New_Data\obs\RNXDATA\KIRU00SWE_R_20260150000_01D_30S_MO.rnx`          |
| RINEX OBS (Base Station) | EMPTY                                                                                 |
| NAV/CLK Row 1            | `C:\PPP_PROJECT\New_Data\nav\BRDC00IGS_R_20260150000_01D_MN.rnx`                      |
| NAV/CLK Row 2            | `C:\PPP_PROJECT\New_Data\DATA_FINAL_ANT_EXTRA\COD0MGXFIN_20260150000_01D_05M_ORB.SP3` |
| NAV/CLK Row 3            | `C:\PPP_PROJECT\New_Data\DATA_FINAL_ANT_EXTRA\COD0MGXFIN_20260150000_01D_30S_CLK.CLK` |
| NAV/CLK Rows 4–10        | EMPTY                                                                                 |
| Solution File            | `C:\PPP_PROJECT\RTKLIB_work\results\KIRU_EXP4B_L1L2_IF.pos`                           |
| Time Start / End         | ☐ Unchecked                                                                           |

#### Setting1 Tab

| Setting                   | Value            | Reason                                              |
| ------------------------- | ---------------- | --------------------------------------------------- |
| Positioning Mode          | PPP Static       |                                                     |
| **Frequencies**           | **L1+L2**        | ← KEY: dual frequency                               |
| Filter Type               | Forward          |                                                     |
| Elevation Mask            | 15°              |                                                     |
| Rec Dynamics              | ON               |                                                     |
| Earth Tides               | OFF              |                                                     |
| **Ionosphere Correction** | **Iono-Free LC** | ← KEY: IF combination eliminates ~99% of iono delay |
| Troposphere Correction    | Saastamoinen     |                                                     |
| Satellite Ephemeris/Clock | Precise          |                                                     |
| Sat PCV                   | ✓ Checked        |                                                     |
| Rec PCV                   | ✓ Checked        |                                                     |
| PhWU                      | ✓ Checked        |                                                     |
| GPS                       | ✓ Checked        |                                                     |
| GLONASS                   | ☐ Unchecked      | GPS only for fair ionosphere comparison             |
| Galileo                   | ✓ Checked        |                                                     |
| QZSS                      | ☐ Unchecked      |                                                     |
| BDS                       | ✓ Checked        |                                                     |

#### Setting2, Output, Statistics, Misc Tabs

All defaults.

#### Positions Tab

Rover = RINEX Header Position. Base = empty.

#### Files Tab

| Field                          | Value                                                         |
| ------------------------------ | ------------------------------------------------------------- |
| Satellite Antenna PCO (slot 1) | `C:\PPP_PROJECT\New_Data\DATA_FINAL_ANT_EXTRA\igs20_2401.atx` |
| Receiver Antenna PCO (slot 2)  | `C:\PPP_PROJECT\New_Data\DATA_FINAL_ANT_EXTRA\igs20_2401.atx` |
| Ionosphere Data File           | **(empty)** — IF combination needs no IONEX                   |
| All others                     | (empty)                                                       |

**Execute → Save config:** `C:\PPP_PROJECT\config\exp4B_L1L2_IF.conf`

**Output:** `C:\PPP_PROJECT\RTKLIB_work\results\KIRU_EXP4B_L1L2_IF.pos`

---

### RUN 4C — Single-Frequency, External IONEX GIM

#### Step 1 — RTKPOST Main Window: Load Files

| Field                    | Value                                                                        |
| ------------------------ | ---------------------------------------------------------------------------- |
| RINEX OBS (Rover)        | `C:\PPP_PROJECT\New_Data\obs\RNXDATA\KIRU00SWE_R_20260150000_01D_30S_MO.rnx` |
| RINEX OBS (Base Station) | EMPTY                                                                        |
| NAV/CLK Row 1            | `C:\PPP_PROJECT\New_Data\nav\BRDC00IGS_R_20260150000_01D_MN.rnx`             |
| NAV/CLK Rows 2–10        | **EMPTY** — broadcast-only, no SP3/CLK                                       |
| Solution File            | `C:\PPP_PROJECT\RTKLIB_work\results\KIRU_EXP4C_L1_IONEX.pos`                 |
| Time Start / End         | ☐ Unchecked                                                                  |

#### Setting1 Tab

| Setting                       | Value         | Reason                                                |
| ----------------------------- | ------------- | ----------------------------------------------------- |
| Positioning Mode              | PPP Static    |                                                       |
| **Frequencies**               | **L1**        | ← KEY: single frequency                               |
| Filter Type                   | Forward       |                                                       |
| Elevation Mask                | 15°           |                                                       |
| Rec Dynamics                  | ON            |                                                       |
| Earth Tides                   | OFF           |                                                       |
| **Ionosphere Correction**     | **IONEX-TEC** | ← KEY: uses the external GIM file loaded in Files tab |
| Troposphere Correction        | Saastamoinen  |                                                       |
| **Satellite Ephemeris/Clock** | **Broadcast** | Broadcast only                                        |
| Sat PCV                       | ☐ Unchecked   |                                                       |
| Rec PCV                       | ☐ Unchecked   |                                                       |
| PhWU                          | ☐ Unchecked   |                                                       |
| GPS                           | ✓ Checked     |                                                       |
| GLONASS                       | ☐ Unchecked   |                                                       |
| Galileo                       | ☐ Unchecked   |                                                       |
| QZSS                          | ☐ Unchecked   |                                                       |
| BDS                           | ☐ Unchecked   |                                                       |

#### Setting2, Output, Statistics, Misc Tabs

All defaults.

#### Positions Tab

Rover = RINEX Header Position. Base = empty.

#### Files Tab

| Field                          | Value                                                                               | Reason                       |
| ------------------------------ | ----------------------------------------------------------------------------------- | ---------------------------- |
| Satellite Antenna PCO (slot 1) | (empty)                                                                             |                              |
| Receiver Antenna PCO (slot 2)  | (empty)                                                                             |                              |
| Geoid Data File                | (empty)                                                                             |                              |
| DCB Data File                  | (empty)                                                                             |                              |
| EOP Data File                  | (empty)                                                                             |                              |
| Ocean Tide BLQ File            | (empty)                                                                             |                              |
| **Ionosphere Data File**       | **`C:\PPP_PROJECT\Old_data\products\ionex\COD0OPSFIN_20260150000_01D_01H_GIM.INX`** | ← KEY: the external GIM file |

> Note: This IONEX file is in Old_data/products/ionex/. It covers the same date (DOY 015, 2026) as your observation files.

**Execute → Save config:** `C:\PPP_PROJECT\config\exp4C_L1_IONEX.conf`

**Output:** `C:\PPP_PROJECT\RTKLIB_work\results\KIRU_EXP4C_L1_IONEX.pos`

---

### EXPERIMENT 4 — Comparison in RTKPLOT

**Files to compare (in pairs — RTKPLOT shows 2 at a time):**

| Pair   | Solution 1                    | Solution 2                | Purpose                              |
| ------ | ----------------------------- | ------------------------- | ------------------------------------ |
| Pair A | `KIRU_EXP4A_L1_Klobuchar.pos` | `KIRU_EXP4C_L1_IONEX.pos` | GIM improvement over Klobuchar       |
| Pair B | `KIRU_EXP4A_L1_Klobuchar.pos` | `KIRU_EXP4B_L1L2_IF.pos`  | Dual-freq advantage over single-freq |
| Pair C | `KIRU_EXP4C_L1_IONEX.pos`     | `KIRU_EXP4B_L1L2_IF.pos`  | GIM vs IF — is GIM good enough?      |

**Reference Position (all Exp 4 runs):**

- Latitude: **67.857900** | Longitude: **20.967800** | Height: **390.900** m

**Steps in RTKPLOT for each pair:**

1. Load both solutions
2. `Edit → Options` → set reference, Quality Filter = All
3. Plot Type: **Position** — the Y-axis scale will be very different between runs
   - 4A: Y-axis in metres; 4B: Y-axis in centimetres → you may need to manually adjust scale
4. `View → Statistics` → record RMS

**What to record:**

| Metric                 | 4A: L1 + Klobuchar | 4C: L1 + GIM | 4B: L1+L2 + IF   |
| ---------------------- | ------------------ | ------------ | ---------------- |
| East bias / RMS (m)    |                    |              |                  |
| North bias / RMS (m)   |                    |              |                  |
| Up bias / RMS (m)      |                    |              |                  |
| Converge to < 10 cm H? | No / Yes           | No / Yes     | Yes — \_\_\_ min |

---

## EXPERIMENT 5 — Session Length Effect on Convergence

> **Research Question:** How does the observation duration affect final position accuracy?
>
> **What changes:** Only the Time End setting. All other settings are identical.
>
> **Expected results:** 1h — not fully converged; 4h — approaching cm-level; 24h — fully converged

All five runs use **identical settings**. The only difference is the Time End cutoff in the main window.

### Common Settings for ALL Runs 5A–5E

**RTKPOST Main Window files (same for all):**

| Field                    | Value                                                                                 |
| ------------------------ | ------------------------------------------------------------------------------------- |
| RINEX OBS (Rover)        | `C:\PPP_PROJECT\New_Data\obs\RNXDATA\KIRU00SWE_R_20260150000_01D_30S_MO.rnx`          |
| RINEX OBS (Base Station) | EMPTY                                                                                 |
| NAV/CLK Row 1            | `C:\PPP_PROJECT\New_Data\nav\BRDC00IGS_R_20260150000_01D_MN.rnx`                      |
| NAV/CLK Row 2            | `C:\PPP_PROJECT\New_Data\DATA_FINAL_ANT_EXTRA\COD0MGXFIN_20260150000_01D_05M_ORB.SP3` |
| NAV/CLK Row 3            | `C:\PPP_PROJECT\New_Data\DATA_FINAL_ANT_EXTRA\COD0MGXFIN_20260150000_01D_30S_CLK.CLK` |
| NAV/CLK Rows 4–10        | EMPTY                                                                                 |

**All Options tabs (same for all 5A–5E):**

| Tab       | Setting                   | Value                 |
| --------- | ------------------------- | --------------------- |
| Setting1  | Positioning Mode          | PPP Static            |
| Setting1  | Frequencies               | L1+L2                 |
| Setting1  | Filter Type               | Forward               |
| Setting1  | Elevation Mask            | 15°                   |
| Setting1  | Rec Dynamics              | ON                    |
| Setting1  | Earth Tides               | OFF                   |
| Setting1  | Ionosphere Correction     | Iono-Free LC          |
| Setting1  | Troposphere Correction    | Saastamoinen          |
| Setting1  | Satellite Ephemeris/Clock | Precise               |
| Setting1  | Sat PCV                   | ✓                     |
| Setting1  | Rec PCV                   | ✓                     |
| Setting1  | PhWU                      | ✓                     |
| Setting1  | GPS                       | ✓                     |
| Setting1  | GLONASS                   | ☐                     |
| Setting1  | Galileo                   | ✓                     |
| Setting1  | QZSS                      | ☐                     |
| Setting1  | BDS                       | ✓                     |
| Setting2  | All AR                    | OFF                   |
| Output    | Solution for Static       | All                   |
| Output    | Output Solution Status    | Residuals             |
| Files     | ATX slot 1 & 2            | `igs20_2401.atx`      |
| Positions | Rover                     | RINEX Header Position |

**Reference for RTKPLOT:**

- Latitude: **67.857900** | Longitude: **20.967800** | Height: **390.900** m

---

### RUN 5A — 1-Hour Session

**Main Window — Time settings:**

| Field         | Value                                                  |
| ------------- | ------------------------------------------------------ |
| Time Start    | **✓ Checked** → 2026/01/15 → 00:00:00                  |
| Time End      | **✓ Checked** → 2026/01/15 → **01:00:00**              |
| Solution File | `C:\PPP_PROJECT\RTKLIB_work\results\KIRU_EXP5A_1h.pos` |

Click **Execute ▶**

---

### RUN 5B — 2-Hour Session

| Field         | Value                                                  |
| ------------- | ------------------------------------------------------ |
| Time Start    | ✓ Checked → 2026/01/15 → 00:00:00                      |
| Time End      | ✓ Checked → 2026/01/15 → **02:00:00**                  |
| Solution File | `C:\PPP_PROJECT\RTKLIB_work\results\KIRU_EXP5B_2h.pos` |

---

### RUN 5C — 4-Hour Session

| Field         | Value                                                  |
| ------------- | ------------------------------------------------------ |
| Time Start    | ✓ Checked → 2026/01/15 → 00:00:00                      |
| Time End      | ✓ Checked → 2026/01/15 → **04:00:00**                  |
| Solution File | `C:\PPP_PROJECT\RTKLIB_work\results\KIRU_EXP5C_4h.pos` |

---

### RUN 5D — 8-Hour Session

| Field         | Value                                                  |
| ------------- | ------------------------------------------------------ |
| Time Start    | ✓ Checked → 2026/01/15 → 00:00:00                      |
| Time End      | ✓ Checked → 2026/01/15 → **08:00:00**                  |
| Solution File | `C:\PPP_PROJECT\RTKLIB_work\results\KIRU_EXP5D_8h.pos` |

---

### RUN 5E — Full 24-Hour Session

| Field         | Value                                                   |
| ------------- | ------------------------------------------------------- |
| Time Start    | **☐ Unchecked** (full day)                              |
| Time End      | **☐ Unchecked** (full day)                              |
| Solution File | `C:\PPP_PROJECT\RTKLIB_work\results\KIRU_EXP5E_24h.pos` |

---

### EXPERIMENT 5 — Comparison in RTKPLOT

**Files produced (compare in sequential pairs or load all):**

| Run | File                 | Duration |
| --- | -------------------- | -------- |
| 5A  | `KIRU_EXP5A_1h.pos`  | 1 hour   |
| 5B  | `KIRU_EXP5B_2h.pos`  | 2 hours  |
| 5C  | `KIRU_EXP5C_4h.pos`  | 4 hours  |
| 5D  | `KIRU_EXP5D_8h.pos`  | 8 hours  |
| 5E  | `KIRU_EXP5E_24h.pos` | 24 hours |

**Reference Position (all Exp 5 runs):**

- Latitude: **67.857900** | Longitude: **20.967800** | Height: **390.900** m

**Steps in RTKPLOT:**

1. Load Solution 1 = `5A_1h.pos` and Solution 2 = `5E_24h.pos` first for the widest contrast
2. `Edit → Options` → set reference, Quality Filter = All
3. Plot Type: **Position** — observe where the 1h run ends vs where the 24h run is at the same time
4. For each .pos file individually: note the last-epoch ENU error from `View → Statistics`
5. Plot the "last-epoch error vs session length" in Excel/Python as a convergence curve

**What to record (use the last-epoch position from each run's `View → Statistics`):**

| Session | File | Last East (cm) | Last North (cm) | Last Up (cm) | Converged? |
| ------- | ---- | -------------- | --------------- | ------------ | ---------- |
| 1h      | 5A   |                |                 |              |            |
| 2h      | 5B   |                |                 |              |            |
| 4h      | 5C   |                |                 |              |            |
| 8h      | 5D   |                |                 |              |            |
| 24h     | 5E   |                |                 |              |            |

> **Tip:** In RTKPLOT, use `Edit → Options → Time` to set a custom time window so you can zoom into just the last few minutes of each run to read the final accuracy.

---

## 9. OLD_DATA — WHICH PRODUCTS TO USE

Your Old_Data has multiple product options. Here is the guidance:

**Stations:** ZIM2 (Switzerland) and HKWS (Hong Kong)
**Date:** Same as New_Data (DOY 015, January 15, 2026)

### Product Selection Guide

| Product Type      | File                                     | Use For                      | Notes                                       |
| ----------------- | ---------------------------------------- | ---------------------------- | ------------------------------------------- |
| **SP3 orbit**     | `COD0MGXFIN_20260150000_01D_05M_ORB.SP3` | **All precise PPP**          | Best: CODE multi-GNSS FINAL. 5-min orbit.   |
| SP3 orbit         | `IGS0OPSFIN_20260150000_01D_15M_ORB.SP3` | GPS-only PPP                 | GPS-only (no Galileo/BDS). 15-min interval. |
| SP3 orbit         | `IGS0OPSRAP_20260150000_01D_15M_ORB.SP3` | Testing rapid products       | Rapid (less accurate than FINAL)            |
| SP3 orbit         | `WUM0MGXRAP_20260150000_01D_05M_ORB.SP3` | Multi-GNSS rapid             | Wuhan University Rapid                      |
| **CLK clock**     | `COD0MGXFIN_20260150000_01D_30S_CLK.CLK` | **All precise PPP**          | Must match SP3: use COD SP3 with COD CLK    |
| CLK clock         | `IGS0OPSFIN_20260150000_01D_30S_CLK.CLK` | GPS-only with IGS SP3        |                                             |
| CLK clock         | `WUM0MGXRAP_20260150000_01D_30S_CLK.CLK` | With WUM SP3                 |                                             |
| **BIA biases**    | `COD0MGXFIN_20260150000_01D_01D_OSB.BIA` | **PPP-AR with COD products** | Use with COD SP3+CLK                        |
| BIA biases        | `WUM0MGXRAP_20260150000_01D_01D_OSB.BIA` | PPP-AR with WUM products     | Alternative                                 |
| **ATX**           | `igs20_2401.atx`                         | **All runs**                 | Same as New_Data. Use this version.         |
| ATX               | `igs20.atx`                              | Alternative                  | Older version, also fine                    |
| **Nav broadcast** | `BRDC00IGS_R_20260150000_01D_MN.rnx`     | **All runs**                 | In Old_data/products/nav/. Mixed, all GNSS. |
| Nav broadcast     | `brdm0150.26p`                           | RINEX-2 format               | For tools requiring RINEX-2                 |
| **IONEX**         | `COD0OPSFIN_20260150000_01D_01H_GIM.INX` | Ionosphere experiment        | 1-hour GIM                                  |
| DCB               | `CAS0OPSRAP_2026015_DCB.BIA`             | If needed                    | For legacy processing                       |
| **SNX reference** | `MIT0OPSSNX_2026015_SOL.SNX`             | Reference coordinates        | True position for accuracy                  |
| **ERP**           | `COD0MGXFIN_20260150000_01D_12H_ERP.ERP` | Optional                     | Earth rotation                              |

### Recommended Product Combinations for Old_Data

**For Experiments 1–5 with Old_Data (RECOMMENDED):**

```
SP3:  Old_data/products/sp3/COD0MGXFIN_20260150000_01D_05M_ORB.SP3
CLK:  Old_data/products/clk/COD0MGXFIN_20260150000_01D_30S_CLK.CLK
BIA:  Old_data/products/bia/COD0MGXFIN_20260150000_01D_01D_OSB.BIA
ATX:  Old_data/products/atx/igs20_2401.atx
NAV:  Old_data/products/nav/BRDC00IGS_R_20260150000_01D_MN.rnx
GIM:  Old_data/products/ionex/COD0OPSFIN_20260150000_01D_01H_GIM.INX
```

All from the same analysis center (CODE), same date → consistent and highest accuracy.

**IMPORTANT: Always match SP3+CLK+BIA from the SAME analysis center.**
Do NOT mix `COD` SP3 with `WUM` CLK — the reference frames and clock definitions differ.

### Reference Coordinates for Old_Data Stations

Use the SNX file: `Old_data/products/snx/MIT0OPSSNX_2026015_SOL.SNX`

| Station | Latitude     | Longitude     | Height (m) |
| ------- | ------------ | ------------- | ---------- |
| ZIM2    | 46.877100° N | 7.465000° E   | 956.400 m  |
| HKWS    | 22.272200° N | 114.161400° E | 72.000 m   |

---

## 10. PRIDE PPP-AR — GUI WALKTHROUGH & ALL EXPERIMENTS

PRIDE-PPP-AR v3.2.7 is used to reproduce all 5 experiments and to deliver genuine
PPP-AR results for Experiment 3 (which RTKLIB-EX 2.5.0 cannot achieve with OSB products).

**GUI executable:** `pride_pppar_winGUI.exe` — download from
[github.com/PrideLab/PRIDE-PPPAR/tree/master/gui](https://github.com/PrideLab/PRIDE-PPPAR/tree/master/gui)
Place it at `C:\PPP_PROJECT\PRIDE_work\pride_pppar_winGUI.exe` (no installer needed).

---

### Product Directory Setup

The GUI **Products tab** expects one `Product dir` with subdirectories. This is already
prepared at `C:\PPP_PROJECT\PRIDE_work\products\`:

```
PRIDE_work\products\
  sp3\  COD0MGXFIN_20260150000_01D_05M_ORB.SP3
  clk\  COD0MGXFIN_20260150000_01D_30S_CLK.CLK
  bia\  COD0MGXFIN_20260150000_01D_01D_OSB.BIA
  atx\  igs20_2401.atx
  erp\  COD0MGXFIN_20260150000_01D_12H_ERP.ERP
  obx\  COD0MGXFIN_20260150000_01D_30S_ATT.OBX
```

> **For Old_Data (ZIM2/HKWS):** `Old_data\products\` already has this structure — point
> Product dir directly to `C:/PPP_PROJECT/Old_data/products/`.

**Temp folder approach (recommended for reproducibility):**
For each run, create a folder under `PRIDE_work\runs\<STATION>_<EXP>\`, set `Rinex Dir`
and `Result Dir` to this folder. Copy the RINEX obs file into it. All input files and
output results will be co-located, mirroring what the RTKLIB script does automatically.

---

### GUI Options — Common Settings (All Experiments)

**General Tab**

| Setting                 | Value for our runs      | Notes                                                   |
| ----------------------- | ----------------------- | ------------------------------------------------------- |
| Session Time checkbox   | ☐ Unchecked             | Full 24h; check + set date/end for Exp 5 short sessions |
| Date                    | 2026/1/15               | DOY 015 of 2026                                         |
| Start / End             | 0:00:00 / 23:59:59      | Override end time for Exp 5                             |
| Interval (s)            | 30                      | Match RINEX sample rate                                 |
| Strict editing          | YES                     | Keep YES                                                |
| **Positioning mode**    | **Static**              | ← Change from default Kinematic                         |
| Satellite systems       | Per-experiment (below)  |                                                         |
| Excluded satellites     | C01 C02 C03 C04 C05     | Keep defaults                                           |
| Downweighted satellites | C01–C05 C18 C59–C61 J07 | Keep defaults                                           |

**Products Tab**

| Setting           | Value                                   |
| ----------------- | --------------------------------------- |
| Product dir       | `C:/PPP_PROJECT/PRIDE_work/products/`   |
| WCC products      | NO                                      |
| Satellite orbit   | Default (auto-finds SP3 in sp3/ subdir) |
| Satellite clock   | Default (auto-finds CLK in clk/ subdir) |
| ERP               | Default                                 |
| Quaternions ✓     | Default (auto-finds OBX in obx/ subdir) |
| Code/phase bias ✓ | Default (auto-finds BIA in bia/ subdir) |

**Atmosphere Tab**

| Setting                         | Value         |
| ------------------------------- | ------------- |
| 2nd-order ionosphere correction | NO            |
| Troposphere mapping function    | GMF           |
| ZTD model / interval            | STO / 60 min  |
| HTG model / interval            | PWC / 720 min |
| ZTD prior variance / noise (m)  | 0.20 / 0.0004 |
| HTG prior variance / noise (m)  | 0.005 / 0.002 |

**Station Tab**

| Setting               | Value                  |
| --------------------- | ---------------------- |
| Pseudorange noise (m) | 0.30                   |
| Phase noise (cycle)   | 0.01                   |
| Tides                 | ✓ SOLID ✓ OCEAN ✓ POLE |
| Observation cut-off   | 7°                     |
| σ-x / σ-y / σ-z (m)   | 10.00 / 10.00 / 10.00  |

---

### Per-Experiment PRIDE Configuration

#### EXPERIMENT 1B — Precise Float PPP (GPS only)

> PRIDE cannot reproduce 1A (no broadcast-only mode). 1B is the equivalent comparison.

**General Tab changes from defaults:**

| Setting                       | Value           |
| ----------------------------- | --------------- |
| Positioning mode              | Static          |
| GPS                           | ✓               |
| GLO / GAL / BDS2 / BDS3 / QZS | ☐ all unchecked |

**Ambiguity Tab:**

| Setting          | Value |
| ---------------- | ----- |
| Ambiguity fixing | NO    |

**Files:**

- Rinex Dir: `C:\PPP_PROJECT\PRIDE_work\runs\KIRU_PRIDE_1B\`
- Result Dir: same folder
- Load RINEX obs: `KIRU00SWE_R_20260150000_01D_30S_MO.rnx`

**Output:** `KIRU_PRIDE_EXP1B_GPS_float.kin`

---

#### EXPERIMENT 2A — GPS Only

| Setting          | Value    |
| ---------------- | -------- |
| Positioning mode | Static   |
| Satellite system | GPS only |
| Ambiguity fixing | NO       |

**Output:** `KIRU_PRIDE_EXP2A_GPS.kin`

---

#### EXPERIMENT 2B — GPS + Galileo

| Setting          | Value     |
| ---------------- | --------- |
| Positioning mode | Static    |
| Satellite system | GPS + GAL |
| Ambiguity fixing | NO        |

**Output:** `KIRU_PRIDE_EXP2B_GPS_GAL.kin`

---

#### EXPERIMENT 2C — GPS + Galileo + BDS

| Setting          | Value                   |
| ---------------- | ----------------------- |
| Positioning mode | Static                  |
| Satellite system | GPS + GAL + BDS2 + BDS3 |
| Ambiguity fixing | NO                      |

**Output:** `KIRU_PRIDE_EXP2C_GPS_GAL_BDS.kin`

---

#### EXPERIMENT 2D — All Constellations

| Setting          | Value                               |
| ---------------- | ----------------------------------- |
| Positioning mode | Static                              |
| Satellite system | GPS + GLO + GAL + BDS2 + BDS3 + QZS |
| Ambiguity fixing | NO                                  |

**Output:** `KIRU_PRIDE_EXP2D_ALL.kin`

---

#### EXPERIMENT 3A — Float PPP (PRIDE baseline)

| Setting          | Value                   |
| ---------------- | ----------------------- |
| Positioning mode | Static                  |
| Satellite system | GPS + GAL + BDS2 + BDS3 |
| Ambiguity fixing | **NO**                  |

**Output:** `KIRU_PRIDE_EXP3A_float.kin`

---

#### EXPERIMENT 3B — PPP-AR ← PRIMARY EXPERIMENT

> This is the critical run — demonstrating genuine AR that RTKLIB-EX cannot achieve.

| Setting          | Value                   |
| ---------------- | ----------------------- |
| Positioning mode | Static                  |
| Satellite system | GPS + GAL + BDS2 + BDS3 |
| Ambiguity fixing | **YES / Default**       |

**Ambiguity Tab (full settings):**

| Setting                    | Value                 |
| -------------------------- | --------------------- |
| Ambiguity fixing           | YES / Default         |
| Ambiguity cut-off          | 15°                   |
| Ambiguity duration         | 600 s                 |
| PCO on wide-lane           | Default               |
| Widelane round-off (cycle) | 0.20 / 0.15 / 1000.00 |
| Narrowlane round-off       | 0.15 / 0.15 / 1000.00 |
| Critical search            | 3 / 4 / 1.80 / 3.00   |

**Output:** `KIRU_PRIDE_EXP3B_PPPAR.kin`

**What to look for in results:**

- `pos_*.log` → check `Fixed: xx.x%` — should be >80% after convergence
- PRIDE Plot ENU tab → E/N traces should tighten significantly vs 3A after ~5–10 min
- U component: should stabilise ~2× faster than float

---

#### EXPERIMENT 4B — Dual-Frequency IF (PRIDE baseline)

> PRIDE always uses dual-frequency IF internally. 4A (Klobuchar) and 4C (GIM) have
> no direct equivalent — only 4B is reproduced for cross-software comparison.

| Setting          | Value                   |
| ---------------- | ----------------------- |
| Positioning mode | Static                  |
| Satellite system | GPS + GAL + BDS2 + BDS3 |
| Ambiguity fixing | NO                      |

**Output:** `KIRU_PRIDE_EXP4B_DF_float.kin`

---

#### EXPERIMENT 5A–5E — Session Length

For each sub-run, check ✓ the **Session Time** checkbox in General Tab and set:

| Run | End time | Output filename            |
| --- | -------- | -------------------------- |
| 5A  | 01:00:00 | `KIRU_PRIDE_EXP5A_1h.kin`  |
| 5B  | 02:00:00 | `KIRU_PRIDE_EXP5B_2h.kin`  |
| 5C  | 04:00:00 | `KIRU_PRIDE_EXP5C_4h.kin`  |
| 5D  | 08:00:00 | `KIRU_PRIDE_EXP5D_8h.kin`  |
| 5E  | 23:59:59 | `KIRU_PRIDE_EXP5E_24h.kin` |

All other settings: Static, GPS+GAL+BDS2+BDS3, Ambiguity = NO.

---

### Viewing Results in PRIDE Plot

PRIDE Plot launches from `Plot` menu in the main GUI window.

1. `File → Import kin file` → select `*.kin` from result folder
2. `File → Import res file` → select `*.res` (residuals — optional)
3. `File → Import ztd file` → select `*.ztd` (troposphere — optional)
4. Click **ENU** tab → E/N/U time series in **cm** relative to a priori position
5. Click **Nsats** tab → satellite count over time
6. `File → Save current figure` (`Ctrl+S`) → save as JPG to `RTKLIB_work\results\PRIDE\`

**Note:** PRIDE Plot axes are in **cm**; RTKPLOT axes are in **m**. Both show E/N/U relative
to the reference, so the shapes are directly comparable — just mind the scale.

---

### Comparing PRIDE Output in RTKPLOT

To load a PRIDE `.kin` file directly in RTKPLOT for overlay with RTKLIB results:

1. Locate `xyz2enu` utility (ships with PRIDE in the `scripts/` folder, or use WSL)
2. Convert:
   ```bash
   xyz2enu -r 67.857900 20.967800 390.900 KIRU_PRIDE_EXP3B_PPPAR.kin > KIRU_PRIDE_3B.pos
   ```
   (Use WUH coords `30.531700 114.357000 73.400` for WUH station)
3. Open the `.pos` file in RTKPLOT — it renders identically to a RTKLIB `.pos` file
4. Load RTKLIB 3A alongside for direct comparison: `File → Open Solution 2`

---

### PRIDE Figure Names — Save to `RTKLIB_work\results\PRIDE\`

| Figure                                | When to save                     |
| ------------------------------------- | -------------------------------- |
| `KIRU_PRIDE_EXP1_ENU.jpg`             | After Exp 1B run, PRIDE Plot ENU |
| `KIRU_PRIDE_EXP2_ENU.jpg`             | After Exp 2A–2D overlay          |
| `KIRU_PRIDE_EXP3_ENU_float_vs_AR.jpg` | PRIDE Plot with 3A and 3B loaded |
| `KIRU_PRIDE_EXP4_ENU.jpg`             | After Exp 4B run                 |
| `KIRU_PRIDE_EXP5_ENU.jpg`             | After all 5A–5E runs overlaid    |
| `WUH_PRIDE_EXP3_ENU_float_vs_AR.jpg`  | WUH equivalent for Exp 3         |
| _(repeat WUH pattern for all exps)_   |                                  |

---

## 11. AUTOMATION SCRIPT

The `scripts/run_rtklib.py` script automates the entire RTKLIB workflow.
Run it instead of manually configuring RTKPOST for each experiment:

```cmd
cd C:\PPP_PROJECT
python scripts\run_rtklib.py
```

See `scripts\run_rtklib.py` for full documentation. The script:

1. Asks which dataset (New_Data or Old_Data) and which station
2. Shows all 5 experiments with descriptions
3. Lets you choose single or all experiments
4. Generates `.conf` configuration files automatically
5. Runs `rnx2rtkp.exe` (command-line RTKLIB) for each configuration
6. Saves results to `RTKLIB_work/runs/<station>_EXP<N>_<timestamp>/`
7. Reports convergence time for each run

---

## 12. QUICK REFERENCE CHEAT SHEET

### Settings for Each Experiment

| Experiment     | Mode       | Frequency | Ephemeris     | Iono             | AR             | Systems     |
| -------------- | ---------- | --------- | ------------- | ---------------- | -------------- | ----------- |
| 1A Broadcast   | PPP-Static | L1+L2     | **Broadcast** | Broadcast        | Off            | GPS         |
| 1B Precise     | PPP-Static | L1+L2     | **Precise**   | Dual-Freq IF     | Off            | GPS         |
| 2A GPS-only    | PPP-Static | L1+L2     | Precise       | Dual-Freq IF     | Off            | **GPS**     |
| 2B GPS+GAL     | PPP-Static | L1+L2     | Precise       | Dual-Freq IF     | Off            | **GPS+GAL** |
| 2C GPS+GAL+BDS | PPP-Static | L1+L2     | Precise       | Dual-Freq IF     | Off            | **GEC**     |
| 3A Float PPP   | PPP-Static | L1+L2     | Precise       | Dual-Freq IF     | **Off**        | GEC         |
| 3B PPP-AR      | PPP-Static | L1+L2     | Precise + BIA | Dual-Freq IF     | **Continuous** | GEC         |
| 4A L1+Klob     | PPP-Static | **L1**    | Broadcast     | **Broadcast**    | Off            | GPS         |
| 4B L1L2+IF     | PPP-Static | **L1+L2** | Precise       | **Dual-Freq IF** | Off            | GEC         |
| 4C L1+IONEX    | PPP-Static | **L1**    | Precise       | **IONEX-TEC**    | Off            | GPS         |
| 5A–5E          | PPP-Static | L1+L2     | Precise       | Dual-Freq IF     | Off            | GEC         |

### Product Files (New_Data)

| Need       | File path                                                              |
| ---------- | ---------------------------------------------------------------------- |
| OBS (KIRU) | `New_Data/obs/RNXDATA/KIRU00SWE_R_20260150000_01D_30S_MO.rnx`          |
| OBS (WUH2) | `New_Data/obs/RNXDATA/WUH200CHN_R_20260150000_01D_30S_MO.rnx`          |
| NAV        | `New_Data/nav/BRDC00IGS_R_20260150000_01D_MN.rnx`                      |
| SP3        | `New_Data/DATA_FINAL_ANT_EXTRA/COD0MGXFIN_20260150000_01D_05M_ORB.SP3` |
| CLK        | `New_Data/DATA_FINAL_ANT_EXTRA/COD0MGXFIN_20260150000_01D_30S_CLK.CLK` |
| BIA        | `New_Data/DATA_FINAL_ANT_EXTRA/COD0MGXFIN_20260150000_01D_01D_OSB.BIA` |
| ATX        | `New_Data/DATA_FINAL_ANT_EXTRA/igs20_2401.atx`                         |

### RTKPLOT Quick Setup

1. Open solution file
2. Edit → Options → Reference Position (enter station coordinates)
3. Select "Position" plot type
4. Convergence line = 0.10 m horizontal threshold
5. File → Save Image for report figures
