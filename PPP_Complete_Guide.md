# Complete End-to-End Guide: PPP with RTKLIB, GAMP, and PRIDE PPP-AR

---

## PART 0 — What is PPP? (Read This First)

### The Big Picture (Layman Explanation)

Your GPS phone is accurate to about 3–5 meters. That's fine for navigation. But scientists,
engineers, and surveyors need centimeter or even millimeter accuracy. That's where **PPP
(Precise Point Positioning)** comes in.

Think of it this way:

> A regular GPS receiver asks the satellite: "Where am I?"
> The satellite replies with an approximate answer.
>
> PPP is like getting a second opinion from _very precise satellite tracking stations_
> on the ground that constantly monitor and correct every satellite's orbit and clock
> to millimeter precision — then using those corrections to solve your position accurately.

PPP can achieve **2–5 cm accuracy** after some time — and that's without needing a
nearby reference station, unlike RTK (Real-Time Kinematic).

---

### Why Does PPP Take Time to Converge?

This is one of your research questions. Here's the honest explanation:

When PPP starts, it doesn't know exactly how many full wavelengths of radio signal are
between you and each satellite. The carrier phase measurement is like reading a ruler but
not knowing how many complete meters the tape has already scrolled — you only see the
fractional end. Figuring out these "ambiguity" integers takes time as the filter collects
enough observations from enough satellites from enough angles.

Typical convergence time:

- GPS-only: **20–40 minutes**
- GPS + Galileo + BeiDou: **8–12 minutes** (why your research compares these!)
- PPP-AR (Ambiguity Resolution): **2–5 minutes** (PRIDE's specialty)

---

### Your Research Questions — Mapped to What You'll Do

| Research Question            | What You'll Compare                    | Tool           |
| ---------------------------- | -------------------------------------- | -------------- |
| Error correction methods     | Broadcast vs Precise products          | GAMP or RTKLIB |
| GPS-only vs Multi-GNSS       | `navsys=1` vs `navsys=45` in GAMP      | GAMP           |
| Broadcast vs IGS products    | `.17p` nav file vs `.sp3`+`.clk` files | GAMP           |
| Convergence time             | Plot position error over first 60 min  | RTKPLOT        |
| PPP-AR (fastest convergence) | Ambiguity-fixed vs float PPP           | PRIDE PPP-AR   |

---

## PART 1 — The Three Tools Explained

### Tool 1: RTKLIB (the "classic" — your `C:\Program Files\RTKLIB`)

**What it is:** The original open-source GNSS toolkit. Like a Swiss Army knife for GNSS.
It has a graphical interface and can process stored data files (post-processing).

**Key programs inside `C:\Program Files\RTKLIB\bin\`:**

- `rtkpost.exe` — Post-process GNSS data (the main one you'll use for PPP)
- `rtkplot.exe` — Plot/visualize your position results
- `rtkconv.exe` — Convert raw receiver files to RINEX format
- `rtkget.exe` — Download IGS products from the internet

---

### Tool 2: RTKLIB-EX 2.5.0 (enhanced version — `C:\Program Files\RTKLIB_EX_2.5.0`)

**What it is:** RTKLIB-EX (formerly called "demo5") is a community-improved fork of RTKLIB,
developed by rtklibexplorer. Same GUI apps as stock RTKLIB, but with better PPP algorithms.
**Already installed:** executables are in `C:\Program Files\RTKLIB_EX_2.5.0\`
(rtkpost.exe, rtkplot.exe, rtkconv.exe, rnx2rtkp.exe, etc. — Help → About shows "RTKLIB-EX 2.5.0").

---

### Tool 3: GAMP (the multi-constellation champion — `C:\Program Files (x86)\GAMP\GAMP`)

**What it is:** GNSS Analysis software for Multi-constellation and multi-frequency
Precise Positioning. Developed by Chinese researchers (Feng Zhou et al.). It's a
**command-line** tool — you edit a config file, run it, get results. No GUI.

**Why use it for your research?** It handles GPS + GLONASS + Galileo + BeiDou better
than basic RTKLIB and lets you easily switch which constellations to use via a single
`navsys` setting. It also supports the uncombined dual-frequency (UC) model which is
considered more mathematically flexible than the classic ionosphere-free (IF) combination.

**Executable:** `C:\Program Files (x86)\GAMP\GAMP\bin\Windows\gamp.exe`

**GAMP output CANNOT be opened directly in rtkplot** — GAMP's `.pos` file uses
ECEF XYZ coordinates (X=-2364338m, Y=4870287m, Z=-3360810m), while rtkplot expects
lat/lon/height. rtkplot will load the file but show nothing. **Use the provided
scripts** in `C:\PPP_PROJECT\scripts\` to plot or convert:

#### What is GOOD? (You may have heard "GAMP and GOOD")

**GOOD** (GNSS Observations and prODucts downloading tool) is a **companion software**
developed by the same research group as GAMP. While GAMP _processes_ GNSS data,
GOOD _automates the downloading_ of observation files and precise products
from CDDIS, IGN, Wuhan, and other servers.

**Do you need GOOD?** No — you already have all your data downloaded. The
`download_ppp_data.py` script in your project does the same job. GOOD is useful
if you're doing batch processing of many days/stations. It's a separate executable
and is **not included** in the GAMP folder in your workspace.

---

### Tool 4: PRIDE PPP-AR (the precision champion — `C:\Program Files (x86)\PRIDE-PPPAR-master`)

**What it is:** PPP with **Ambiguity Resolution** — meaning it can fix the integer
ambiguities we mentioned, achieving the fastest convergence and highest accuracy.
Developed by Wuhan University, China. Also command-line.

**Why this is special:** Regular PPP leaves the ambiguities as floating-point estimates.
PRIDE PPP-AR resolves them to their true integer values, like suddenly snapping a blurry
photo into perfect focus. This cuts convergence to 2–5 minutes.

---

## PART 2 — File Types You'll Work With

Before downloading anything, you MUST understand what each file does. This is critical.

### A. The Observation File (.rnx / .xxo) — YOUR RAW DATA

**What it is:** The actual GNSS measurements recorded by a ground receiver.
Think of it as the "raw recording" of every satellite signal received, second by second.

**Format:** RINEX (Receiver INdependent EXchange format) — a universal text format.

**File naming example:** `cut02440.17o`

- `cut0` = station name (4 chars)
- `244` = day of year (244 = September 1)
- `0` = session (0 = full day)
- `.17o` = year 2017, observation file

**Where to get it:**

- IGS data archive: https://cddis.nasa.gov/archive/gnss/data/daily/
- MGEX (Multi-GNSS Experiment): https://cddis.nasa.gov/archive/gnss/data/daily/YYYY/DDD/
- Navigation: Data > Daily > YYYY > DDD > YYo/

**Effect if missing:** YOU CANNOT DO ANYTHING. This is your input data.
Every analysis starts with this file.

---

### B. Navigation/Broadcast Ephemeris (.17p / .rnx nav / brdmDDD0.YYp)

**What it is:** The satellite "announcement" of its own orbit and clock. Each satellite
broadcasts this signal — like a satellite saying "I am at X,Y,Z coordinates at time T."
It's rough — accurate to ~1–3 meters for orbit, ~2–7 nanoseconds for clock.

**File naming:** `brdm2440.17p`

- `brdm` = broadcast mixed (all constellations)
- `244` = day of year
- `0` = session
- `.17p` = year 2017, mixed navigation file

Older GPS-only: `brdc2440.17n` (.17n = GPS nav file)

**Where to get it:**

- https://cddis.nasa.gov/archive/gnss/data/daily/YYYY/DDD/YYp/ (mixed, all GNSS)
- https://cddis.nasa.gov/archive/gnss/data/daily/YYYY/DDD/YYn/ (GPS only)

**Effect if missing:** PPP cannot run at all. Without knowing roughly where satellites
are, no positioning is possible.

**Comparison value for your research:** "Broadcast-only PPP" uses ONLY this file for
orbit/clock — giving meter-level accuracy. Compare against precise products below.

---

### C. Precise Satellite Orbit File (.sp3)

**What it is:** Satellite positions computed **after the fact** by IGS analysis centers,
using hundreds of ground tracking stations worldwide. Accurate to **~2–3 cm**.
Compare to broadcast: the difference is like a rough hand-drawn map vs. a GPS-mapped
survey.

**File naming:** `wum19644.sp3`

- `wum` = Wuhan University analysis center code
- `1964` = GPS week
- `4` = day of week (0=Sunday, 4=Thursday)
- `.sp3` = Standard Product 3 format

**Other analysis center codes:**

- `igs` = IGS combined (most accurate, but 2 weeks delayed)
- `com` = CODE (Switzerland)
- `gbm` = GFZ (Germany)
- `grm` = CNES (France)
- `wum` = Wuhan University

**Where to get it:**

- IGS Final (most precise, ~2-week delay): https://cddis.nasa.gov/archive/gnss/products/WWWW/
- IGS Rapid (~2-day delay): same folder, `igsrWWWWD.sp3`
- MGEX (multi-GNSS): https://cddis.nasa.gov/archive/gnss/products/mgex/WWWW/
  - `WUM0MGXFIN_YYYY...` for Wuhan final
  - `WUM0MGXRAP_YYYY...` for Wuhan rapid (for PRIDE PPP-AR)

**Effect if missing or using broadcast instead:**
Orbit error: ~1–3 meters (broadcast) vs ~2–3 cm (precise)
This is HUGE — it directly drives your position error.

---

### D. Precise Satellite Clock File (.clk)

**What it is:** Satellite clock corrections computed to nanosecond precision.
Your GPS receiver's position depends on knowing EXACTLY when each signal was sent.
Even 1 nanosecond of clock error = 30 cm of position error!
Broadcast clock: ~2–7 ns error. Precise clock: ~0.03–0.1 ns error.

**File naming:** `wum19644.clk` (same naming convention as .sp3)

**Where to get it:** Same location and same centers as the .sp3 file.
You must always download the .clk file that MATCHES the .sp3 file (same center, same day).

**Effect if missing:** PPP fails completely. Without precise clocks, there's no PPP
— only broadcast/SPP (Standard Point Positioning).

---

### E. Earth Rotation Parameters (.erp)

**What it is:** Tiny corrections for how the Earth wobbles on its axis
(polar motion) and how Earth's rotation rate varies slightly day to day.
Think of it as accounting for the fact that "North Pole" drifts slightly.

**File naming:** `igs19647.erp`

- `igs` = IGS combined
- `1964` = GPS week
- `7` = this file covers a 7-day period

**Where to get it:** https://cddis.nasa.gov/archive/gnss/products/WWWW/

**Effect if missing:** GAMP and PRIDE will fail to run (required input).
Positional errors of a few centimeters without it.

---

### F. Differential Code Biases (.DCB / .BSX)

**What it is:** Every receiver and every satellite has tiny timing differences
between different signal frequencies. These are called "code biases."
For example, GPS L1 P-code and L2 P-code have a slight offset of a few nanoseconds.
Without correcting for this, your position wanders by 0.5–2 meters.

**File types:**

- `.DCB` files (older format):
  - `P1C11709.DCB` — GPS P1-C1 bias (receivers using C/A vs P-code)
  - `P1P21709.DCB` — GPS P1-P2 inter-frequency bias
  - `P2C21709.DCB` — GPS P2-C2 bias
  - Naming: `P1P2YYMM.DCB` where YY=year, MM=month
- `.BSX` files (newer BIAS-SINEX format, for multi-GNSS):
  - `CAS0MGXRAP_20172440000_01D_01D_DCB.BSX`
  - Used for GPS+GLONASS+Galileo+BeiDou corrections

**Where to get DCB files:**

- CODE DCB: https://cddis.nasa.gov/archive/gnss/products/bias/YYYY/
  - Files like `CAS0MGXRAP_YYYYDDD0000_01D_01D_DCB.BSX`
  - Or older: https://cddis.nasa.gov/archive/gnss/products/bias/YYYY/
- CAS (Chinese Academy of Sciences): ftp://igs.gnsswhu.cn/pub/gnss/products/mgex/dcb/

**Effect if missing:** For single-frequency PPP: position error of ~0.5–2 m.
For dual-frequency (ionosphere-free combination), impact is smaller but still present.
GAMP will warn or fail depending on the ionosphere correction mode selected.

---

### G. Ionosphere Map (IONEX / .YYI) — Optional but Important

**What it is:** The ionosphere is a layer of the atmosphere (80–1000 km altitude)
filled with charged particles that slow down GPS signals. This delay varies with
location, time of day, and solar activity. It can cause errors of 1–50 meters on
a single-frequency receiver. A Global Ionosphere Map (GIM) is a grid of these delays.

**File naming:** `CODG2440.17I`

- `COD` = CODE analysis center
- `G` = global
- `244` = day of year
- `0` = session
- `.17I` = year 2017, ionosphere IONEX file

**Where to get it:** https://cddis.nasa.gov/archive/gnss/products/ionex/YYYY/DDD/

- Files like `codgDDD0.YYi.Z` (CODE GIM)
- Or `igsgDDD0.YYi.Z` (IGS combined)

**Effect if missing:**

- Dual-frequency PPP: not needed (ionosphere cancels out mathematically — this is the beauty of using two frequencies!)
- Single-frequency PPP: HUGE effect. Without it, error up to 10–50 meters.
- For your research: compare "with GIM" vs "without GIM" for single-frequency analysis.

---

### H. Antenna Phase Center Corrections (ATX — .atx)

**What it is:** The GPS signal doesn't arrive at the exact center of the antenna.
It arrives at a point that varies with satellite elevation angle. This file provides
the correction — like accounting for the fact that you're measuring to the brim of a
cup, not its center.

**File naming:** `igs14.atx` (now `igs20_2317.atx`)

**Where to get it:**

- https://files.igs.org/pub/station/general/igs14.atx (older)
- https://files.igs.org/pub/station/general/igs20.atx (current, for post-2022 work)
- PRIDE uses: `igs14_2247.atx` or `igs20_2317.atx` — already in `C:\Program Files (x86)\PRIDE-PPPAR-master\table\`

**Effect if missing:** Position errors of 1–3 cm, especially in height.

---

### I. Ocean Tide Loading (BLQ — .blq)

**What it is:** Ocean tides cause the ground to deform by up to 10 cm (near coasts)
due to the weight of tidal water. This file tells the software how much the ground
moves at your station due to the ocean.

**File naming:** `ocnload.blq`

**Where to get it (compute it online):**

- http://holt.oso.chalmers.se/loading/ (use FES2004 or GOT00.2 model)
- Enter your station coordinates → download the .blq file

**Effect if missing:** Vertical position errors up to 5–10 cm (near coasts), 1–2 cm inland.

---

### J. Station Coordinates (SNX — .snx / .crd)

**What it is:** The known "truth" coordinates of the station, in ITRF (International
Terrestrial Reference Frame). Used as the reference to compute your position error.

**File naming:** `igs1964.snx` (SINEX format)

**Where to get it:**

- IGS weekly SINEX: https://cddis.nasa.gov/archive/gnss/products/WWWW/igsWWWWD.snx.Z
- Or use `site.crd` in GAMP (a simple coordinate file)

**Effect if missing:** You can still run PPP, but you have no "truth" to compare
your results against. Required if you want to evaluate accuracy.

---

### K. Phase Bias Products (OSB/FCB) — For PPP-AR only

**What it is:** For PRIDE PPP-AR, you need Observable-Specific Biases (OSB)
or Fractional Cycle Biases (FCB). These are the tiny phase offsets that must be
corrected before ambiguity resolution becomes possible. Think of them as the key
that "unlocks" the ability to fix ambiguities to integers.

**File naming:** `WUM0MGXRAP_YYYYDDDHHSS_01D_01D_OSB.BIA`

**Where to get it:**

- Wuhan University FTP: `ftps://bdspride.com/wum/` (PRIDE's primary product server)
- PDOP3 script (supplied with PRIDE) downloads these automatically.

**Effect if missing:** PPP-AR falls back to "float PPP" (lower accuracy, slower convergence).

---

## PART 3 — Quick Reference: Files Summary Table

| File                  | Extension   | What It Does            | Accuracy Impact    | Where to Download |
| --------------------- | ----------- | ----------------------- | ------------------ | ----------------- |
| Observation           | .xxo / .rnx | Your data               | N/A (required)     | IGS CDDIS / MGEX  |
| Broadcast nav         | .xxp / .xxn | Rough sat orbit+clock   | ±1–3 m             | IGS CDDIS         |
| Precise orbit         | .sp3        | Precise sat position    | ±2–3 cm            | IGS CDDIS / MGEX  |
| Precise clock         | .clk        | Precise sat time        | ±0.03 ns           | IGS CDDIS / MGEX  |
| Earth rotation        | .erp        | Earth wobble correction | ±2–3 cm            | IGS CDDIS         |
| Code bias             | .DCB / .BSX | Signal timing offsets   | ±0.5–2 m           | CODE / CAS        |
| Ionosphere map        | .YYI        | Atmospheric delay map   | ±1–50 m (1-freq)   | IGS CDDIS         |
| Antenna corrections   | .atx        | Antenna phase center    | ±1–3 cm            | IGS FTP           |
| Ocean tide            | .blq        | Ground deformation      | ±5–10 cm (coastal) | Chalmers online   |
| Station coordinates   | .snx / .crd | Reference truth         | N/A (for checking) | IGS CDDIS         |
| Phase biases (PPP-AR) | .BIA / .bia | Ambiguity fixing        | Enables AR         | Wuhan Univ. FTP   |

---

## PART 4 — Setting Up Your Folder Structure

Before running anything, organize your files like this:

```
C:\PPP_PROJECT\
    data\               ← Your observation files (.rnx / .17o)
    nav\                ← Broadcast navigation files (.17p)
    products\
        sp3\            ← Precise orbit files (.sp3)
        clk\            ← Precise clock files (.clk)
        erp\            ← Earth rotation parameter files (.erp)
        dcb\            ← Code bias files (.DCB or .BSX)
        ion\            ← Ionosphere map files (.17I or .23I)
    tables\
        igs20.atx       ← Antenna corrections
        ocnload.blq     ← Ocean tide loading
        igs_snx.snx     ← Station coordinates
    GAMP_work\          ← Where GAMP config and results go
    PRIDE_work\         ← Where PRIDE config and results go
    RTKLIB_work\        ← Where RTKLIB config and results go
    results\            ← Your final output files for comparison
```

---

## PART 5 — GAMP (Legacy / Optional Reference)

> **Team note:** For your research experiments, use **RTKLIB** (Part 6) and **PRIDE PPP-AR** (Part 7).
> GAMP is documented here for reference only. It has been validated on our dataset (2614 epochs,
> GPS-only IF12 PPP) but has several quirks that make it harder to use than RTKLIB or PRIDE.
>
> **Known GAMP limitations in this project:**
>
> - Requires RINEX-2 obs (`.26o`) — RINEX-3/4 files have compatibility issues
> - Requires RINEX-2 broadcast nav (`brdm*.p`) — RINEX-3/4 nav causes `toc` errors
> - Requires 3 consecutive days of SP3/CLK (day−1, day0, day+1) — GAMP extends its time window ±2.5h past midnight
> - Requires the old `igs14.atx` — `igs20.atx` fails silently
> - File naming is rigid: `<ac><week><dow>.sp3` only (e.g., `cod24014.sp3`)
> - **GAMP pos columns 11–13 (dE, dN, dU) are errors vs `site.crd`** — you must have the correct reference coordinates in `site.crd` for these to be meaningful
> - Does NOT converge within a single 24-hour session on our test data (ENU oscillates for the full day before settling)
>
> Use the wizard if you must run GAMP: `python scripts/run_gamp.py`

### What GAMP Does (Layman Summary)

GAMP is like a very smart calculator. You feed it:

1. Your raw GPS/GNSS observations
2. Satellite orbit and clock corrections
3. Error correction files

And it outputs your precise position at each second of the day, along with
troposphere delays, ambiguities, and residuals.

---

### Step 1 — Get the Example Running First

The easiest way to learn GAMP is to run the included example before using your own data.
All example files are at: `C:\Program Files (x86)\GAMP\GAMP\Examples\2017244\`

**Step 1a: Copy the example to a working folder**

Open Command Prompt (press Win+R, type `cmd`, press Enter), then:

```cmd
mkdir C:\PPP_PROJECT\GAMP_work
xcopy "C:\Program Files (x86)\GAMP\GAMP\Examples\2017244\*" C:\PPP_PROJECT\GAMP_work\ /E /I
copy "C:\Program Files (x86)\GAMP\GAMP\bin\Windows\gamp.exe" C:\PPP_PROJECT\GAMP_work\
```

**Step 1b: Edit the config file**

Open `C:\PPP_PROJECT\GAMP_work\gamp.cfg` in Notepad.

Change the observation folder path (line 4) to point to your working folder:

```
obs file/folder     = 1   %(0:file  1:folder)
                    = C:\PPP_PROJECT\GAMP_work
```

Also change the product file paths. Find lines starting with:

```
sp3 file            = ...
clk file            = ...
```

And update them to point to where you actually copied the files.

**Step 1c: Run GAMP**

In Command Prompt:

```cmd
cd C:\PPP_PROJECT\GAMP_work
gamp.exe gamp.cfg
```

You'll see output lines scrolling. GAMP processes each epoch (each second) of data.
When it finishes, look in the `result\` subfolder.

---

### Step 2 — Understanding the GAMP Config File (gamp.cfg)

Let's go through every important setting:

**LINE: `posmode = 6`**

- What it means: Processing mode
- `0` = SPP (Standard Point Positioning — rough, like your phone GPS)
- `6` = PPP Kinematic (the receiver is moving, or treated as moving — slower convergence)
- `7` = PPP Static (the receiver is stationary — FASTER convergence, more accurate)
- **For your research:** Start with `7` (static) to study convergence properly

**LINE: `navsys = 1`**

- What it means: Which satellite constellations to use
- `1` = GPS only
- `5` = GPS + GLONASS
- `8` = Galileo only
- `33` = GPS + BeiDou (1 + 32)
- `45` = GPS + GLONASS + Galileo + BeiDou (1+4+8+32)
- **For your research:** Run with `1` then `45` and compare convergence time!

**LINE: `ionoopt = 4`**

- What it means: How to handle ionosphere errors
- `0` = Ignore it (bad!)
- `1` = Use broadcast model (rough, built into nav file)
- `2` = Ionosphere-Free combination (IF12) — mathematically cancels ionosphere using two frequencies. Standard PPP approach!
- `4` = UC12 — Uncombined dual-frequency. Estimates ionosphere as an extra unknown. More powerful.
- `5` = Use IONEX GIM file (external map)
- **For your research:** Use `2` (IF) and `4` (UC) and compare results

**LINE: `tropopt = 3`**

- What it means: How to handle troposphere (lower atmosphere) delay
- `1` = Saastamoinen model only (rough formula based on temperature/pressure)
- `3` = Estimate ZTD (Zenith Troposphere Delay) — most accurate for PPP
- **Use `3` for all your PPP runs**

**LINE: `sp3 file = ...`**

- The precise orbit file. Location of your .sp3 file.
- If empty or pointing to wrong file, GAMP falls back to broadcast — huge accuracy loss.

**LINE: `clk file = ...`**

- The precise clock file. MUST match the sp3 file (same analysis center, same day).

---

### Step 3 — Download Files for Your Own Date

Let's say you want to process data from **2024, day 100** (April 9, 2024).
GPS week for 2024/100 = GPS week 2310, day 2 (Tuesday).

**3a: Download observation data**

Option A — Use an IGS station (free, globally distributed):

1. Go to: https://cddis.nasa.gov/archive/gnss/data/daily/2024/100/24o/
2. Look for a station near your area of interest
3. Download a file like `abmf1000.24o.gz`
4. Unzip it (use 7-Zip or run `gzip -d abmf1000.24o.gz` in cmd)

Option B — Download from MGEX (for multi-GNSS data, RECOMMENDED for your research):

1. Go to: https://cddis.nasa.gov/archive/gnss/data/daily/2024/100/24o/
   OR for RINEX 3 (multi-GNSS): https://cddis.nasa.gov/archive/gnss/data/daily/2024/100/24d/
2. Download MGEX observation files with names like `AREG00PER_R_20241000000_01D_30S_MO.rnx.gz`
   - `_MO` = mixed observation (multi-GNSS)

**Note:** You need a free CDDIS account. Register at: https://urs.earthdata.nasa.gov/

**3b: Download broadcast navigation file**

Go to: https://cddis.nasa.gov/archive/gnss/data/daily/2024/100/24p/
Download: `BRDM00DLR_S_20241000000_01D_MN.rnx.gz` (the mixed constellation nav file)
Unzip it.

**3c: Download precise orbit and clock files**

Go to: https://cddis.nasa.gov/archive/gnss/products/2310/
(Replace 2310 with the GPS week for your date)

Download:

- `igs23102.sp3.Z` — IGS precise orbits
- `igs23102.clk.Z` — IGS precise clocks
- `igs23102.erp.Z` — Earth rotation parameters

Unzip all (`.Z` files need `uncompress` or 7-Zip).

For multi-GNSS products (needed for BeiDou/Galileo): https://cddis.nasa.gov/archive/gnss/products/mgex/2310/
Download:

- `WUM0MGXFIN_2024100...sp3.gz` — Wuhan University final multi-GNSS orbit
- `WUM0MGXFIN_2024100...clk.gz` — Wuhan University final multi-GNSS clock
- `CAS0MGXRAP_2024100...DCB.BSX.gz` — CAS code biases for multi-GNSS

**3d: Download ionosphere file (if needed)**

Go to: https://cddis.nasa.gov/archive/gnss/products/ionex/2024/100/
Download: `codg1000.24i.Z` (CODE GIM)
Unzip it.

---

### Step 4 — Edit the GAMP Config for Your Own Data

Here is a complete template you can copy into your `gamp.cfg` file.
**Replace all paths with your actual paths.**

```
# GAMP config for PPP experiment - GPS only, static, precise products

obs file/folder     = 1
                    = C:\PPP_PROJECT\data

start_time          = 0    2024/04/09  00:00:00.0
end_time            = 0    2024/04/09  23:59:30.0

posmode             = 7                     # 7=PPP static
soltype             = 0                     # 0=forward
navsys              = 1                     # 1=GPS only (change to 45 for multi-GNSS)

minelev             = 7.0
inpfrq              = 2                     # 2=dual frequency

ionoopt             = 2                     # 2=IF (ionosphere-free)
tropopt             = 3                     # estimate ZTD
tropmf              = 1                     # GMF mapping function
tidecorr            = 7

outdir              = C:\PPP_PROJECT\results

# Precise products
sp3 file            = C:\PPP_PROJECT\products\sp3\igs23102.sp3
clk file            = C:\PPP_PROJECT\products\clk\igs23102.clk
erp file            = C:\PPP_PROJECT\products\erp\igs23102.erp

# DCB corrections
dcb p1c1 file       = C:\PPP_PROJECT\products\dcb\P1C12404.DCB
dcb p1p2 file       = C:\PPP_PROJECT\products\dcb\P1P22404.DCB

# Antenna corrections
atx file            = C:\PPP_PROJECT\tables\igs14.atx

# Ocean tide loading
blq file            = C:\PPP_PROJECT\tables\ocnload.blq

# Station coordinates (for accuracy check)
snx file            = C:\PPP_PROJECT\tables\igs23107.snx
```

---

### Step 5 — Run GAMP for Your Research Scenarios

**Scenario 1: GPS-only PPP with broadcast ephemeris**

```cfg
navsys    = 1     # GPS only
ionoopt   = 1     # broadcast ionosphere model
# Comment out sp3 file and clk file lines (or leave empty)
```

**Scenario 2: GPS-only PPP with precise products**

```cfg
navsys    = 1     # GPS only
ionoopt   = 2     # ionosphere-free combination
sp3 file  = C:\PPP_PROJECT\products\sp3\igs23102.sp3
clk file  = C:\PPP_PROJECT\products\clk\igs23102.clk
```

**Scenario 3: Multi-GNSS PPP (GPS+Galileo+BeiDou)**

```cfg
navsys    = 41    # GPS(1) + Galileo(8) + BeiDou(32) = 41
ionoopt   = 4     # UC12 (uncombined dual-freq, better for multi-GNSS)
sp3 file  = C:\PPP_PROJECT\products\sp3\WUM0MGXFIN_...sp3
clk file  = C:\PPP_PROJECT\products\clk\WUM0MGXFIN_...clk
```

Run each scenario:

```cmd
cd C:\PPP_PROJECT\GAMP_work
gamp.exe gamp.cfg
```

---

### Step 6 — Understanding GAMP Output Files

Look inside `C:\PPP_PROJECT\results\` after GAMP runs.

Key output files (named like `stationname_YYYYday_GAMP.xxx`):

- `*.pos` — Position results: columns are time, lat, lon, height, errors, etc.
- `*.dtrp` — Troposphere delay estimates over time
- `*.ippp` — PPP iteration information
- `*.debug` — Detailed processing log (good for troubleshooting)
- `*.elev` — Satellite elevation angles over time
- `*.pdop` — PDOP (position dilution of precision) — lower is better

**The `.pos` file columns:**

```
Year Month Day Hour Min Sec  Lat(deg) Lon(deg) Height(m)  Easting-err Northing-err Height-err  PDOP
```

---

## PART 6 — STEP-BY-STEP: Using RTKLIB / RTKPOST for PPP

### What RTKPOST Does

RTKPOST is the graphical (Windows GUI) post-processing tool. You load your observation
file, navigation file, and product files through a visual interface, then click
"Execute" to run the processing.

---

### Step 1 — Open RTKPOST

Double-click: `C:\Program Files\RTKLIB\bin\rtkpost.exe`

You should see a window with file inputs and processing options.

---

### Step 2 — Load Your Input Files

In RTKPOST, you will see these input fields at the top:

**RINEX OBS (Rover):** Click the `...` button → select your observation file (`.rnx` or `.17o`)
This is your raw data — the receiver's observations.

**RINEX NAV/CLK:** Click `...` → select your navigation file (`.17p` or `.rnx nav`)

**SP3 / CLK:** Click the `+` button next to "SP3/CLK" → add your `.sp3` file, then add `.clk` file

**Base Station:** Leave EMPTY for PPP (PPP needs no base station — this is its advantage!)

**Output File:** Choose where to save results → e.g., `C:\PPP_PROJECT\results\output.pos`

---

### Step 3 — Configure PPP Options (the most important step)

Click the **"Options"** button. A dialog opens with several tabs.

#### Tab: "Setting 1"

**Positioning Mode:** Change to `PPP-Static` (or `PPP-Kinematic` for moving receiver)

- Static = receiver doesn't move. Much faster convergence. Use for your research.

**Frequencies:** Select `L1+L2` (dual frequency)

- This enables the Ionosphere-Free combination, eliminating most ionosphere error.

**Filter Type:** `Forward` (start from beginning of file, process forward in time)

**Elevation Mask:** `15 deg` (ignore satellites below 15° elevation — they have more error)

**Satellite Ephemeris:**

- `Broadcast` = use the .17p file only (rough)
- `Precise` = use .sp3 + .clk files (centimeter accuracy)
- **For your comparison: run once with each setting!**

**Satellite System:**

- Tick GPS, Galileo, BDS boxes to enable multi-GNSS
- **For your comparison: run GPS-only first, then add systems**

#### Tab: "Setting 2"

**Integer Ambiguity Res (GPS):**

- `Off` = "Float PPP" — slower convergence, less accurate
- `Continuous` or `Fix-and-Hold` = tries to fix ambiguities (better)
- For this RTKLIB version, PPP-AR works only with special bias products.

#### Tab: "Positions"

If you know your station's true coordinates (from IGS), enter them here under "Base Station."
Check "Use Average of Single Solution" to automatically estimate the position.

#### Tab: "Files"

**Satellite/Receiver Antenna PCO/PCV:** Click `...` → select `igs14.atx`
(CRITICAL: without this, your height will have a systematic centimeter-level error)

---

### Step 4 — Run RTKPOST

Click **"Execute"** at the bottom right.

You'll see a progress bar and a log window scrolling. Processing a full day of data
at 30-second intervals takes about 30 seconds to 2 minutes on a modern PC.

When done, you'll see "done" in the log.

---

### Step 5 — View Results in RTKPLOT

Open `C:\Program Files\RTKLIB\bin\rtkplot.exe`

Go to File → Open Solution → select your `.pos` output file.

**What to look at:**

1. **Ground Track:** shows your position over time (should be a single dot for static)
2. **Position:** Top/East/North plots show position error vs. time
   - Watch how the error SHRINKS over the first 20–40 minutes — THIS IS CONVERGENCE!
   - Save a screenshot: right-click the plot → Save Image
3. **Number of Satellites:** should stay ≥ 5 for reliable PPP
4. **Status:** Green = fixed (AR), Yellow = float — green is better

**For your convergence analysis:**

- Count the time from the start until the position error drops below 10 cm (horizontal)
- That's your "convergence time" — the key metric for your research

---

### Step 6 — Research Comparison Runs

Run RTKPOST **four times** with these settings, saving each output separately:

| Run | Mode       | Ephemeris | Systems     | Output filename   |
| --- | ---------- | --------- | ----------- | ----------------- |
| 1   | PPP-Static | Broadcast | GPS only    | broadcast_GPS.pos |
| 2   | PPP-Static | Precise   | GPS only    | precise_GPS.pos   |
| 3   | PPP-Static | Precise   | GPS+GAL     | precise_GE.pos    |
| 4   | PPP-Static | Precise   | GPS+GAL+BDS | precise_GEC.pos   |

Then open all four `.pos` files in RTKPLOT at once (File → Open Solution → select multiple)
to overlay the convergence curves.

---

## PART 7 — STEP-BY-STEP: Using PRIDE PPP-AR

### What PRIDE Does Differently

PRIDE PPP-AR is the most sophisticated of the three tools. Its specialty is
PPP with Ambiguity Resolution (PPP-AR). It uses special Phase Bias (OSB/FCB) products
from Wuhan University that allow the software to resolve the integer ambiguities —
the "blurry photo" problem mentioned earlier — dramatically improving both
convergence time and accuracy.

PRIDE is a Linux/macOS pipeline. On Windows, you need **Windows Subsystem for Linux (WSL)**.

> **Current status (as of May 2026):** PRIDE source is at
> `C:\Program Files (x86)\PRIDE-PPPAR-master\src\` but has **not yet been compiled**.
> The GUI launcher (`gui\pride_pppar_winGUI.exe`) exists but the core processing binary
> (`pdp3` → `lsq`, `tedit`, `arsig`, etc.) needs to be built in WSL first.
> Follow Steps 1–3 below before attempting any runs.

**Why PRIDE is worth the WSL setup effort:**

| Feature               | RTKLIB    | GAMP      | PRIDE PPP-AR |
| --------------------- | --------- | --------- | ------------ |
| Float PPP             | ✅        | ✅        | ✅           |
| PPP-AR                | Limited   | ❌        | ✅ **Best**  |
| Multi-GNSS            | ✅        | ✅        | ✅           |
| Auto product download | ❌        | ❌        | ✅ **Auto**  |
| Convergence time      | 20–40 min | 20–40 min | **2–10 min** |
| Windows native        | ✅ GUI    | ✅        | WSL only     |

---

### Step 1 — Install WSL (Windows Subsystem for Linux)

PRIDE PPP-AR runs in a Linux environment. On Windows, you need WSL.

1. Open **PowerShell as Administrator** (Start → search "PowerShell" → right-click → "Run as Administrator")
2. Type:
   ```powershell
   wsl --install
   ```
3. Restart your computer when prompted
4. After restart, Ubuntu opens automatically. Create a username and password.
5. You now have a Linux terminal inside Windows.

**Verify WSL is working:**

```powershell
# In PowerShell — should print the Ubuntu version
wsl -- lsb_release -a
```

**Verify you can see the PRIDE source from WSL:**

```bash
# In WSL terminal
ls "/mnt/c/Program Files (x86)/PRIDE-PPPAR-master/src/"
# Should list: Makefile arsig/ lib/ lsq/ mhm/ orbit/ otl/ redig/ spp/ tedit/ utils/
```

---

### Step 2 — Compile PRIDE PPP-AR

In the Ubuntu (WSL) terminal:

```bash
# Install required tools
sudo apt-get update
sudo apt-get install -y build-essential gfortran cmake

# Navigate to the PRIDE source folder
# Note: Windows C: drive is at /mnt/c/ in WSL
cd "/mnt/c/Program Files (x86)/PRIDE-PPPAR-master/src"

# Build the software (takes ~2 minutes)
make

# The binaries are placed in ../bin/ automatically
ls ../bin/
# Should list: lsq  tedit  spp  redig  arsig  mhm  otl  pdp3  ...
```

**Verify the build worked:**

```bash
# Run the test example
cd "/mnt/c/Program Files (x86)/PRIDE-PPPAR-master/example"
bash test.sh
# Should produce files like kin_2020001_abmf in the results/ folder
```

**Add pdp3 to your WSL PATH (do once):**

```bash
echo 'export PATH="/mnt/c/Program Files (x86)/PRIDE-PPPAR-master/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
pdp3 --help   # Should print usage
```

After compilation, the pipeline stages `lsq`, `tedit`, `spp`, `redig`, `arsig`
are all called automatically by `pdp3` — you never invoke them directly.

---

### Step 3 — Run the Built-in Test Example

```bash
cd "/mnt/c/Program Files (x86)/PRIDE-PPPAR-master/example"

# Run the test script (auto-downloads products, processes abmf0010.20o)
bash test.sh
```

This will:

1. Download necessary products from the internet automatically (needs internet in WSL)
2. Process the included observation file `abmf0010.20o` (ABMF station, Guadeloupe, 2020-001)
3. Output results to `results/`

If successful, compare your results folder with `results_ref/`:

```bash
# These should be nearly identical (within a few mm)
diff results/ results_ref/
```

> **Troubleshooting:** If the test fails to download products, PRIDE's auto-download uses
> IGN FTP, Wuhan FTP, and bdspride FTPS. Check your WSL has internet access:
>
> ```bash
> curl -I https://cddis.nasa.gov  # Should return HTTP 200 or 302
> ```
>
> If blocked, manually place products (see Step 6 product structure) and re-run with `bash test.sh --offline`.

---

### Step 4 — The `pdp3` Command (PRIDE's Main Entry Point)

`pdp3` is the main script. Here is its syntax:

```bash
pdp3 [options] <observation_file.rnx>
```

**Key options:**

| Option      | Meaning                             | Example                    |
| ----------- | ----------------------------------- | -------------------------- |
| (no option) | Kinematic PPP-AR                    | `pdp3 myfile.rnx`          |
| `-m S`      | Static PPP-AR                       | `pdp3 -m S myfile.rnx`     |
| `-m F`      | Static PPP, output troposphere      | `pdp3 -m F myfile.rnx`     |
| `-sys g`    | GPS only                            | `pdp3 -sys g myfile.rnx`   |
| `-sys gec`  | GPS + Galileo + BeiDou              | `pdp3 -sys gec myfile.rnx` |
| `-z P`      | Use LAMBDA for ambiguity resolution | `pdp3 -z P myfile.rnx`     |
| `-float`    | Float PPP only (no AR)              | `pdp3 -float myfile.rnx`   |

---

### Step 5 — Does pdp3 auto-download products?

**YES — pdp3 downloads all needed products automatically** by reading the date from your observation file. This is one of PRIDE's best features.

```bash
# Run static PPP-AR — pdp3 downloads everything it needs
pdp3 -m S /path/to/your/abmf0010.20o
```

When this runs, pdp3 will:

1. Read the date from the observation file
2. Check its local product cache at `{working_dir}/{year}/product/common/`
3. If products are missing, **download from**: IGN FTP (week ≥ 2290), Wuhan FTP, or bdspride.com FTPS
4. Process and output results into the current working directory

**For our research data (2026-01-15, GPS week 2401 ≥ 2290):**
Auto-download works perfectly — no manual steps needed.

**For the PRIDE test cases (2020–2023, GPS week < 2290):**
pdp3 skips IGN for old dates and may fail to download automatically.
Use `scripts/download_test_products.sh` to pre-place files (see PRIDE Test Setup below).

**To skip download and use only locally cached products:**

```bash
pdp3 -m S -offline /path/to/obs.rnx
```

---

### Step 6 — Products Directory Structure (PRIDE auto-creates this)

When pdp3 downloads products, it creates:

```
./2024/100/
    WUM0MGXRAP_2024100...sp3      ← precise orbit
    WUM0MGXRAP_2024100...clk      ← precise clock
    WUM0MGXRAP_2024100...bia      ← phase biases (key for PPP-AR!)
    WUM0MGXRAP_2024100...erp      ← earth rotation
    config_abmf                    ← processing config
    kin_2024100_abmf               ← kinematic position output
    ztd_2024100                    ← troposphere output
    res_2024100                    ← residuals
    log_2024100_abmf               ← log file
```

---

### Step 7 — The Config File for PRIDE

PRIDE uses `config_template` in the `table/` folder. When `pdp3` runs, it creates
a `config_stationname` file. You can edit this to change settings.

Key settings in that file:

```
## Satellite product
Product directory = Default       ← auto-downloads here
Satellite orbit   = Default       ← auto-selects from downloaded
...

## Data processing strategies
ZTD model         = PWC/STO       ← troposphere estimation
Tides             = SOLID/OCEAN/POLE  ← tide corrections on

## Ambiguity fixing options
Ambiguity duration = 600          ← min 600 seconds before trying to fix
Cutoff elevation   = 15           ← min 15 degrees elevation for AR
```

---

### Step 8 — PRIDE Research Comparison Runs

For your research, run `pdp3` four times on the SAME observation file.
Work from your PPP_PROJECT directory in WSL:

```bash
# In WSL — navigate to your work folder
cd /mnt/c/PPP_PROJECT
mkdir -p PRIDE_work && cd PRIDE_work

# Your obs file is at (RINEX-3 works natively with PRIDE):
OBS="/mnt/c/PPP_PROJECT/data/ZIM200CHE_R_20260150000_01D_30S_MO.rnx"

# Run 1: Float PPP, GPS only (no ambiguity resolution)
pdp3 -m S -float -sys G $OBS
mv 2026/015 ./float_GPS

# Run 2: PPP-AR, GPS only
pdp3 -m S -sys G $OBS
mv 2026/015 ./PPPAR_GPS

# Run 3: PPP-AR, GPS + Galileo
pdp3 -m S -sys GE $OBS
mv 2026/015 ./PPPAR_GE

# Run 4: PPP-AR, GPS + Galileo + BeiDou (best convergence expected)
pdp3 -m S -sys GEC $OBS
mv 2026/015 ./PPPAR_GEC
```

**What to look at after each run:**

- `kin_20260150000_ZIM2` → per-epoch position time series (main result)
- `pos_20260150000_ZIM2` → final static position estimate + formal uncertainty
- `log_20260150000_ZIM2` → processing log (check for errors)

Compare the convergence curves. You should see PPP-AR converge significantly faster than
float, and multi-GNSS faster than GPS-only.

---

### Step 9 — Plotting PRIDE Results

PRIDE comes with Python plotting scripts in `scripts/`:

```bash
cd "/mnt/c/Program Files (x86)/PRIDE-PPPAR-master/scripts"

# Plot kinematic position results
python plotkin.py ../results/PPPAR_GPS/kin_2020001_abmf

# Plot troposphere
python plotztd.py ../results/PPPAR_GPS/ztd_2020001
```

Make sure you have Python and matplotlib:

```bash
sudo apt install python3-matplotlib python3-numpy
```

---

## PART 8 — Visualizing and Comparing All Results

<div style="background: #e3f2fd; border-left: 5px solid #1976d2; padding: 10px 16px; margin: 8px 0; border-radius: 4px">

### ⚠️ Important: Format Compatibility

| Tool      | Output file       | rtkplot can open?             | How to visualize                                                                 |
| --------- | ----------------- | ----------------------------- | -------------------------------------------------------------------------------- |
| RTKLIB    | `.pos`            | ✅ Yes, directly              | File → Open Solution                                                             |
| RTKLIB-EX | `.pos`            | ✅ Yes, directly              | File → Open Solution                                                             |
| GAMP      | `.pos`            | ❌ No — ECEF XYZ format       | Use `scripts/plot_gamp_enu.py` or `scripts/gamp2rtkplot.py` to convert first     |
| PRIDE     | `kin_*` / `pos_*` | ⚠️ Partial — needs conversion | Use `scripts/plot_pride_enu.py --convert-only kin_file`, then open `.rtklib.pos` |

</div>

---

### Visualizing GAMP Results

All scripts are in `C:\PPP_PROJECT\scripts\`. Run from `C:\PPP_PROJECT\`.

#### Step 0: Use run_gamp.py (recommended — handles everything)

Instead of manually copying files and editing configs, use the wizard:

```cmd
cd C:\PPP_PROJECT
python scripts/run_gamp.py
```

The wizard:

1. Lists your obs files from `data/`
2. Shows 4 scenario choices (A–D) with descriptions
3. Auto-matches products for the obs file date from `products/`
4. Creates an isolated run folder: `GAMP_work/runs/<station>_<scenario>_<timestamp>/`
5. Copies all files, generates `run.cfg`, runs GAMP
6. Tells you exactly which `plot_gamp_enu.py` command to use on the result

**All runs are preserved** in `GAMP_work/runs/` — each run is self-contained.

#### Option A: Python plot (primary method)

```cmd
cd C:\PPP_PROJECT

rem Single file — ENU convergence:
python scripts/plot_gamp_enu.py GAMP_work/result/cut02440.17o.pos

rem Additional plots (white legend, for reports):
python scripts/plot_gamp_enu.py --scatter GAMP_work/result/cut02440.17o.pos
python scripts/plot_gamp_enu.py --d3      GAMP_work/result/cut02440.17o.pos

rem All plots at once:
python scripts/plot_gamp_enu.py --all --no-show GAMP_work/result/cut02440.17o.pos

rem Overlay GPS-only vs multi-GNSS for convergence comparison:
python scripts/plot_gamp_enu.py --compare GAMP_work/result/cut02440.17o.pos GAMP_work/results_reference/result_GRCE_kin_DF_noGIM_wum/cut02440.17o.pos

rem Summary bar chart across all scenarios:
python scripts/plot_gamp_enu.py --summary GAMP_work/result/scen_A.pos GAMP_work/result/scen_B.pos GAMP_work/result/scen_C.pos
```

Outputs saved next to the `.pos` file:

| Flag        | Output file         | Content                                           |
| ----------- | ------------------- | ------------------------------------------------- |
| (default)   | `*.pos.png`         | ENU error time series                             |
| `--scatter` | `*.pos.scatter.png` | E vs N horizontal scatter + RMS circle            |
| `--d3`      | `*.pos.3d.png`      | 3D error + horizontal error over time             |
| `--summary` | `*/summary_bar.png` | Convergence time + RMS bar chart across scenarios |
| `--all`     | all above           | Everything at once                                |
| (always)    | `*.pos.stats`       | Text statistics summary                           |

#### Option B: Convert to rtkplot format, then open in rtkplot

```cmd
cd C:\PPP_PROJECT

rem Convert single file:
python scripts/gamp2rtkplot.py GAMP_work/result/cut02440.17o.pos

rem Convert all .pos files in a folder:
python scripts/gamp2rtkplot.py GAMP_work/result/

rem Convert and auto-open in rtkplot:
python scripts/gamp2rtkplot.py --open GAMP_work/result/cut02440.17o.pos
```

This creates `*.rtklib.pos` files. In rtkplot:

1. File → Open Solution 1 → select the `.rtklib.pos` file
2. Plot Type → **"Position"**
3. E/N/U errors will be displayed as sdn/sde/sdu columns

#### Option C: MATLAB (original GAMP tool)

The GAMP distribution includes MATLAB plotting scripts in:
`C:\Program Files (x86)\GAMP\GAMP\Tools\MatPlot\`

If you have MATLAB:

```matlab
% In MATLAB:
cd('C:\PPP_PROJECT\GAMP_work')
addpath('C:\Program Files (x86)\GAMP\GAMP\Tools\MatPlot')
Plot_PPP_result('result/cut02440.17o')   % without .pos extension
```

This produces plots identical to the reference JPGs in `results_reference\*\plot\jpg\`.
For most purposes the Python script (Option A) is equivalent and doesn't require MATLAB.

---

### Visualizing PRIDE PPP-AR Results

PRIDE produces these output files after running `pdp3`:

| File                  | Content                              | Use for                            |
| --------------------- | ------------------------------------ | ---------------------------------- |
| `kin_YYYYDDD_station` | Per-epoch position (lat/lon/ECEF)    | **Main result** — convergence plot |
| `pos_YYYYDDD_station` | Final static position + uncertainty  | Final accuracy figure              |
| `ztd_YYYYDDD_station` | Zenith troposphere delay time series | Troposphere analysis               |
| `res_YYYYDDD_station` | Post-fit residuals per satellite     | Outlier/quality check              |
| `rck_YYYYDDD_station` | Receiver clock estimates             | Clock analysis                     |
| `amb_YYYYDDD_station` | Ambiguity parameters                 | AR success check                   |

#### Plot PRIDE kin\_ convergence:

```cmd
rem From Windows CMD (run from C:\PPP_PROJECT):
cd C:\PPP_PROJECT
python scripts\plot_pride_enu.py PRIDE_work\kin_20260150000_hkws

rem Additional plots:
python scripts\plot_pride_enu.py --scatter  PRIDE_work\kin_20260150000_hkws
python scripts\plot_pride_enu.py --nsat     PRIDE_work\kin_20260150000_hkws

rem All plots at once:
python scripts\plot_pride_enu.py --all --no-show  PRIDE_work\kin_20260150000_hkws

rem Or from WSL:
python /mnt/c/PPP_PROJECT/scripts/plot_pride_enu.py  kin_20260150000_hkws

rem Compare float vs AR fixed:
python scripts\plot_pride_enu.py --compare kin_20260150000_hkws_float kin_20260150000_hkws_fixed

rem Summary bar chart across scenarios:
python scripts\plot_pride_enu.py --summary kin_float kin_fixed kin_gec

rem Print static result (final accuracy):
python scripts\plot_pride_enu.py --pos  pos_20260150000_hkws

rem Convert to rtkplot format only:
python scripts\plot_pride_enu.py --convert-only  kin_20260150000_hkws
```

Available plot flags for PRIDE:

| Flag             | Output                | Content                                |
| ---------------- | --------------------- | -------------------------------------- |
| (default)        | `kin_*.png`           | ENU error time series                  |
| `--scatter`      | `kin_*.scatter.png`   | E vs N horizontal scatter + RMS circle |
| `--nsat`         | `kin_*.nsat_pdop.png` | N satellites tracked + PDOP over time  |
| `--summary`      | `*/summary_bar.png`   | Convergence time + RMS bar chart       |
| `--all`          | all above             | Everything at once                     |
| `--convert-only` | `kin_*.rtklib.pos`    | rtkplot-compatible file (no plot)      |

The script automatically computes ENU errors vs. the known ITRF2020 coordinates
for HKWS and ZIM2 (already built into the script). For other stations, add them
to the `KNOWN_REF` dict in `scripts/plot_pride_enu.py`.

#### Open PRIDE result in rtkplot:

After running `--convert-only` (or any plot command which also auto-converts):

1. Open `C:\Program Files\RTKLIB\bin\rtkplot.exe`
2. File → Open Solution 1 → select `kin_*.rtklib.pos`
3. Plot Type → **"Position"** — shows E/N/U errors vs time
4. Overlay GAMP and PRIDE by also opening the GAMP `.rtklib.pos` as Solution 2

---

### RTKLIB / RTKLIB-EX — Already Native rtkplot Format

RTKLIB and RTKLIB-EX `.pos` output is already in rtkplot's native format:

1. Open `C:\Program Files\RTKLIB\bin\rtkplot.exe`
2. File → Open Solution 1 (or drag-and-drop the `.pos` file)
3. Plot Type → **"Position"** — immediate ENU convergence display
4. File → Open Solution 2 for comparison overlay

For the reference position: Edit → Options → set known lat/lon/height:

- HKWS: Lat 22.272200° Lon 114.161400° Height 72.0 m
- ZIM2: Lat 46.877200° Lon 7.465200° Height 956.0 m

---

## PART 9 — Understanding Your Results: Convergence and Verification

### What "Convergence" Means on a Graph

When you open your position file in RTKPLOT, you'll see position vs. time:

```
Error
(m)
5 |*
4 | **
3 |   ***
2 |      ****
1 |           *****
0.2|                **************
   |___________________________|___> Time
   t=0                         t=30min
```

The slow decay from ~5 meters down to ~20 cm takes 20–40 minutes for GPS-only PPP.
That's convergence time. After convergence, the position settles to its final accuracy.

---

### How to Verify Your PPP Results

You need a **reference ("true") position** to compute the error. For IGS stations
like ZIM2 and HKWS, highly accurate coordinates are published weekly in SINEX files.

**Method 1 — Compare to SINEX/IGS reference (most rigorous)**

The SINEX file downloaded by `download_gamp_data.py` contains the IGS-computed
coordinates for that exact day:

```bash
# From the SINEX file MIT0OPSSNX_2026015_SOL.SNX, ZIM2 2026/015:
# X = 4331299.7091  Y = 567537.7486  Z = 4633133.8374  (ITRF2020)
```

These are the authoritative reference coordinates. If your PPP estimate matches
these to within 5–10 cm, you have good float PPP. Within 2–3 cm = excellent.

> ⚠️ **Important:** The GAMP `site.crd` file in the run wizard uses the coordinates
> from the `KNOWN_REFS` dictionary in `scripts/run_gamp.py`. The ZIM2 entry was initially
> set to an old ITRF2020 epoch value that differs from the 2026 SINEX by ~18 m in Y
> (wrong longitude). This means GAMP's reported dE/dN/dU in the `.pos` file do NOT
> reflect the true error. Always verify against the SINEX reference independently.

**Method 2 — Check if the solution converged (visual)**

1. Plot ENU error vs time using `python scripts/plot_gamp_enu.py` (GAMP) or
   `python scripts/plot_pride_enu.py` (PRIDE)
2. Look for the position to stabilize — flat line after ~30 min
3. If the East/North/Up is still trending or oscillating after 2 hours, convergence failed

**Definition of convergence used in this project:**

- Horizontal error (2D: √(E²+N²)) < 10 cm AND
- Vertical error |U| < 20 cm AND
- Both maintained for at least 10 consecutive minutes

**Method 3 — Compare the ECEF estimate to the SINEX ECEF reference**

For PRIDE, after running `pdp3 -m S`, read the `pos_YYYYDDD_station` file:

```
# pos file format: STA  X(m)  Y(m)  Z(m)  sX  sY  sZ
```

Subtract the SINEX reference to get dX, dY, dZ. Convert to dE/dN/dU using the
local rotation matrix at the station latitude/longitude.

**ZIM2 reference coordinates (2026/015, SINEX ITRF2020):**

| Parameter | Value          |
| --------- | -------------- |
| X         | 4331299.7091 m |
| Y         | 567537.7486 m  |
| Z         | 4633133.8374 m |
| Latitude  | 46.8771° N     |
| Longitude | 7.4650° E      |
| Height    | 956.4 m        |

**HKWS reference coordinates (2026/015):**

Extract from SINEX or use the IGS published value:

- Latitude ≈ 22.2722° N, Longitude ≈ 114.1614° E, Height ≈ 72.0 m

---

### Is >24h Convergence Normal for GAMP?

For our test run (ZIM2, GPS-only, Scenario B), the ENU plot shows the solution
continuously drifting for the full 24-hour day before approaching the reference:

```
dE at  0h:  +2.1 m   (just started, very wrong)
dE at  8h:  -1.6 m   (large residual East bias persists)
dE at 16h:  -1.2 m   (still 1.2 m off)
dE at 24h:  ~0.0 m   (finally near reference at end of day)
```

This is **not typical PPP convergence** — it's a sign of a systematic issue:

- **Likely cause:** Missing DCB (Differential Code Bias) files. GAMP warned
  `P1-P2 DCB file NOT found` and `P1-C1 DCB file NOT found`. Without DCBs,
  systematic biases remain unmodelled, causing slow drift especially in East.
- The 2017 BSX DCB file in `GAMP_work/` is outdated for 2026 data.
  Getting 2026 DCB files from CDDIS (`CAS0MGXRAP_2026015_...DCB.BSX`) would likely fix this.

**For comparison:** RTKLIB with proper DCB/bias products and PRIDE PPP-AR should
achieve convergence within 20–40 min (float) or 5–15 min (PPP-AR).

### Why Multi-GNSS Converges Faster

More satellites from more directions = better geometry = ambiguities are solved faster.
GPS alone: ~8–10 satellites visible.
GPS + Galileo + BeiDou: ~25–30 satellites visible!
More observations mean the filter has more equations to solve those unknowns faster.

### Why Precise Products Are Better Than Broadcast

|                | Broadcast | IGS Rapid | IGS Final | PRIDE (WUM)  |
| -------------- | --------- | --------- | --------- | ------------ |
| Orbit accuracy | ~1–3 m    | ~5 cm     | ~2 cm     | ~2–3 cm      |
| Clock accuracy | ~2–7 ns   | ~0.1 ns   | ~0.03 ns  | ~0.03 ns     |
| PPP accuracy   | ~1–5 m    | ~5–10 cm  | ~2–5 cm   | ~1–3 cm (AR) |
| Availability   | Real-time | ~2 days   | ~2 weeks  | ~2 days      |

### The Key Trade-off

- **Broadcast** = available immediately, good for real-time apps, low accuracy
- **Rapid** = 2-day delay, centimeter-level accuracy
- **Final** = 2-week delay, best accuracy possible
- **PPP-AR** = uses special biases to fix ambiguities, best convergence

---

## PART 10 — Common Problems and Solutions

**Problem: GAMP exits immediately without processing**

- Check: Is the observation file path in `gamp.cfg` correct?
- Check: Does the observation file exist and is it unzipped?
- Check: Do the sp3 and clk filenames match what's in the config?

**Problem: GAMP processes but the position jumps around wildly**

- Check: Are you using matching sp3+clk files (same analysis center, same day)?
- Try: Lower the `minelev` value to 5 degrees
- Try: Switch `ionoopt` from 4 (UC12) to 2 (IF12)

**Problem: RTKPOST shows "no solution" or "Q=0"**

- Check: Is the observation file in RINEX format? (use RTKCONV to convert if it's in u-blox binary)
- Check: Is the sp3 file covering the right time period?
- Check: Did you select "PPP-Static" mode (not "Single" or "Kinematic")?

**Problem: PRIDE pdp3 won't download products ("connection refused")**

- Try: `pdp3 -offline -m S myfile.rnx` (use cached/pre-downloaded products)
- Or manually download products from: https://cddis.nasa.gov/archive/gnss/products/mgex/

**Problem: RINEX file won't open / "unrecognized format"**

- Use RTKCONV to convert it
- Check the RINEX version (RTKLIB handles v2.x and v3.x, PRIDE handles v2 and v3)

---

## PART 11 — Summary: Which Tool for Which Task?

| Task                                     | Best Tool                         | Notes                                           |
| ---------------------------------------- | --------------------------------- | ----------------------------------------------- |
| Learning PPP basics with GUI             | **RTKLIB / RTKPOST**              | Windows GUI, no setup needed                    |
| Comparing broadcast vs. precise products | **RTKLIB** or PRIDE               | Easy mode switching in RTKPOST                  |
| GPS-only vs. multi-GNSS comparison       | **RTKLIB** or **PRIDE**           | Both support multi-GNSS                         |
| Float PPP, best accuracy (no AR)         | **RTKLIB** or **PRIDE -float**    |                                                 |
| PPP with Ambiguity Resolution            | **PRIDE PPP-AR**                  | Best convergence, needs WSL                     |
| Visualizing / comparing results          | **RTKPLOT**                       | Native RTKLIB format                            |
| Downloading IGS products                 | `download_gamp_data.py` or RTKGET | Script supports batch download                  |
| Checking result accuracy                 | Compare to SINEX reference        | ITRF2020 from MIT0OPSSNX\_\*.SNX                |
| GAMP (GPS-only IF12 PPP)                 | `python scripts/run_gamp.py`      | Works but needs DCB fix for convergence; legacy |

**Recommended workflow for your research:**

1. Run RTKLIB (RTKPOST) first — GUI, quick, good enough for broadcast vs. precise comparison
2. Run PRIDE PPP-AR — for PPP-AR vs float and multi-GNSS comparison
3. Plot everything in RTKPLOT — overlay the `.pos` files for visual comparison

---

## PART 12 — Your Research Proposal: Recommended Experiments

Based on your discussion with your team, here are the concrete experiments to run:

### Experiment 1: Broadcast vs. Precise Products

- **Tool:** RTKLIB (RTKPOST)
- **Obs file:** `ZIM200CHE_R_20260150000_01D_30S_MO.rnx` or `zim20150.26o`
- **Run A:** Positioning Mode=PPP-Static, Ephemeris=Broadcast (`brdm0150.26p` only)
- **Run B:** Positioning Mode=PPP-Static, Ephemeris=Precise (SP3 + CLK from `products/`)
- **Measure:** RMS of position error in last 2 hours; time to reach 10 cm horizontal
- **Expected:** Broadcast ~1–5 m; Precise ~5–15 cm

### Experiment 2: GPS-only vs. Multi-GNSS

- **Tool:** RTKLIB (RTKPOST) or PRIDE PPP-AR
- **Settings:** Same precise products; vary satellite systems
  - RTKLIB: Options → Setting 1 → Satellite System: [GPS only] vs [GPS+GAL+BDS]
  - PRIDE: `pdp3 -m S -sys G` vs `pdp3 -m S -sys GEC`
- **Measure:** Convergence time (minutes to reach 10 cm horizontal)
- **Expected:** GPS-only ~25–40 min; GPS+GAL+BDS ~8–15 min

### Experiment 3: Float PPP vs. PPP-AR

- **Tool:** PRIDE PPP-AR
- **Run A:** `pdp3 -m S -float -sys GEC obs.rnx` (float only, no ambiguity resolution)
- **Run B:** `pdp3 -m S -sys GEC obs.rnx` (PPP-AR enabled)
- **Measure:** Convergence time, final RMS, fraction of epochs with fixed ambiguities
- **Expected:** Float ~15–25 min; PPP-AR ~3–8 min

### Experiment 4: Error Correction Method

- **Tool:** RTKLIB or PRIDE
- **Vary:** Whether to use ionosphere-free combination (IF) vs uncombined + ionosphere model
  - RTKLIB: Options → Setting 1 → Ionosphere Correction → [Broadcast] vs [None (dual-freq IF)]
  - PRIDE: `-sys G -float` (uses UC PPP) vs RTKLIB IF12
- **Measure:** Position accuracy and convergence at different corrections

### Experiment 5: Session Length Effect on Convergence

- **Tool:** RTKLIB (easy with partial file processing) or PRIDE
- **Settings:** Process the same 24h file but with different end times: 1h, 2h, 4h, 8h, 24h
  - RTKLIB: Options → Setting 1 → Time Start/End to cut the session
- **Measure:** Final accuracy as a function of observation session length
- **Expected:** After 1h, still not fully converged; after 4–8h, approaching cm-level

---

## APPENDIX A — File Calendar: GPS Week to Date

| Date       | Day of Year | GPS Week | Day of Week |
| ---------- | ----------- | -------- | ----------- |
| 2024 Jan 1 | 001         | 2295     | 1           |
| 2024 Apr 9 | 100         | 2310     | 2           |
| 2024 Jun 1 | 153         | 2317     | 6           |
| 2024 Sep 1 | 245         | 2329     | 0           |

Use the online converter: https://www.ngs.noaa.gov/NCAT/ or
https://www.gnsscalendar.com/

---

## APPENDIX B — Complete Download Checklist for One Day of Processing

Replace YYYY=2024, DDD=100, WWWW=2310, WD=2 with your actual dates.

```
[ ] Observation file:    cddis.nasa.gov/archive/gnss/data/daily/YYYY/DDD/YYo/
[ ] Mixed nav file:      cddis.nasa.gov/archive/gnss/data/daily/YYYY/DDD/YYp/
[ ] IGS SP3:             cddis.nasa.gov/archive/gnss/products/WWWW/igsWWWWWD.sp3.Z
[ ] IGS CLK:             cddis.nasa.gov/archive/gnss/products/WWWW/igsWWWWWD.clk.Z
[ ] IGS ERP:             cddis.nasa.gov/archive/gnss/products/WWWW/igsWWWW7.erp.Z
[ ] MGEX SP3 (WUM):      cddis.nasa.gov/archive/gnss/products/mgex/WWWW/WUM0MGXFIN_...sp3.gz
[ ] MGEX CLK (WUM):      cddis.nasa.gov/archive/gnss/products/mgex/WWWW/WUM0MGXFIN_...clk.gz
[ ] DCB (CAS):           cddis.nasa.gov/archive/gnss/products/bias/YYYY/CAS0MGXRAP_...DCB.BSX.gz
[ ] GIM (CODE):          cddis.nasa.gov/archive/gnss/products/ionex/YYYY/DDD/codgDDD0.YYi.Z
[ ] ATX:                 files.igs.org/pub/station/general/igs14.atx  (download once, reuse)
[ ] SNX:                 cddis.nasa.gov/archive/gnss/products/WWWW/igsWWWW7.snx.Z
```

---

_Guide prepared for PPP research project. Tools: RTKLIB stock 2.4.3, RTKLIB-EX 2.5.0, GAMP v2, PRIDE PPP-AR v3.2_
_Data sources: IGS/CDDIS, Wuhan University (WUM), CODE, CAS_

---

<div style="border-left: 5px solid #e53e3e; background: #fff5f5; padding: 1px 20px; margin: 10px 0">

## PART 13 — Product File Naming Conventions 🔴

> This section explains what every part of a product filename means and why you have
> multiple files that appear to do the same thing.

### Why Are There Multiple SP3/CLK Files?

After running the download script you ended up with **3 SP3 files** and **3 CLK files**.
This is normal and intentional — they come from different analysis centers and cover
different satellite systems. Here is exactly what each one is:

| File (SP3)                               | Size   | Center             | Systems Covered      | Delay    | Use for                       |
| ---------------------------------------- | ------ | ------------------ | -------------------- | -------- | ----------------------------- |
| `COD0OPSFIN_2026015_ORB.SP3`             | 1.4 MB | CODE (Switzerland) | GPS + GLONASS only   | ~2 weeks | GPS/GLONASS PPP               |
| `COD0MGXFIN_20260150000_01D_05M_ORB.SP3` | 2.1 MB | CODE MGEX          | GPS+GLO+GAL+BDS+QZSS | ~2 weeks | **Multi-GNSS PPP (Best)**     |
| `WUM0MGXRAP_20260150000_01D_05M_ORB.SP3` | 1.9 MB | Wuhan Univ.        | GPS+GLO+GAL+BDS+QZSS | ~2 days  | Multi-GNSS when FIN not ready |

| File (CLK)                               | Size  | Systems              | Quality                                |
| ---------------------------------------- | ----- | -------------------- | -------------------------------------- |
| `IGS0OPSFIN_2026015_CLK.CLK`             | 12 MB | GPS + GLONASS        | IGS combined, highest GPS/GLO accuracy |
| `COD0MGXFIN_20260150000_01D_30S_CLK.CLK` | 35 MB | GPS+GLO+GAL+BDS+QZSS | Best for multi-GNSS                    |
| `WUM0MGXRAP_20260150000_01D_30S_CLK.CLK` | 19 MB | GPS+GLO+GAL+BDS+QZSS | Rapid, good fallback                   |

### Decoding the Filename Format

Every modern IGS RINEX 3 product file follows this pattern:

```
COD0MGXFIN_20260150000_01D_05M_ORB.SP3
│   │   │     │        │    │    │    └── Extension: SP3 (orbit), CLK (clock), ERP, BIA, OBX, INX
│   │   │     │        │    │    └── Content code: ORB=orbit, CLK=clock, ATT=attitude
│   │   │     │        │    └── Sample interval: 05M=5 minutes, 30S=30 seconds, 01D=1 day, 12H=12 hour
│   │   │     │        └── Duration: 01D=1 day
│   │   │     └── Start epoch: YYYY=2026, DDD=015, HH=00, mm=00, ss=00
│   │   └── Solution type: FIN=Final (best), RAP=Rapid, ULT=Ultra-rapid
│   └── Data source: MGX=Multi-GNSS, OPS=IGS Operations
└── Analysis center: COD=CODE, WUM=Wuhan, IGS=Combined, EMR=NRCan, CAS=Chinese Acad.
```

### What FIN / RAP / ULT Mean

| Code     | Full Name   | Published                  | Orbit Accuracy | Clock Accuracy |
| -------- | ----------- | -------------------------- | -------------- | -------------- |
| **FIN**  | Final       | ~2 weeks after observation | ~2–3 cm        | ~0.02–0.03 ns  |
| **RAP**  | Rapid       | ~2 days after observation  | ~2.5 cm        | ~0.03 ns       |
| **ULT**  | Ultra-rapid | 90 min after observation   | ~5 cm          | ~0.15 ns       |
| _(none)_ | Broadcast   | Real-time                  | ~100 cm        | ~2–7 ns        |

**For your research (2026-01-15 analysis today, May 2026):** You have Final products.
This is the **best available quality** — equivalent to surveying-grade data.

### Does "Fallback 3" Mean Inferior Data? — NO!

In the download script, the numbering (Priority 1, Fallback 3) refers only to the
**order the script tries them**, not the quality of the data.

- **`IGS0OPSFIN`** — Tries first. But it covers GPS+GLONASS ONLY.
- **`COD0OPSFIN`** — Tries second. Also GPS+GLONASS only.
- **`COD0MGXFIN`** — Was labeled "Fallback 3" in the table. But for **multi-GNSS PPP
  (GPS + Galileo + BeiDou + QZSS)**, `COD0MGXFIN` is actually the **BEST product**
  because it is the only Final product that includes all 5 constellations.

The script stopped at `COD0OPSFIN` for the GPS/GLONASS products. `COD0MGXFIN` was
separately downloaded from your team member's zip and is now in `products/sp3/` and
`products/clk/`.

### ATX Files — Which One to Use

| File                       | Size                                  | Validity                        |
| -------------------------- | ------------------------------------- | ------------------------------- |
| `igs20.atx` (52.7 MB)      | Downloaded fresh from `files.igs.org` | Current, covers all IGS20 epoch |
| `igs20_2401.atx` (48.6 MB) | Team's copy from GPS week 2401        | Slightly older version          |

**Use `igs20.atx`** (the larger one) for all processing. `igs20_2401.atx` can be kept
as a backup but is not needed. These are NOT the same file — `igs20.atx` is always
the most current release; `igs20_2401.atx` was the version released during GPS week 2401.

</div>

---

<div style="border-left: 5px solid #e53e3e; background: #fff5f5; padding: 1px 20px; margin: 10px 0">

## PART 14 — Your Complete 2026-01-15 File Inventory 🔴

> Do you need to rerun the download script? **No** — you have everything needed for
> all four tools. This table shows exactly what you have and what each file is for.

### Observation Files (`C:\PPP_PROJECT\data\`)

| File                                     | Size    | Description                                          |
| ---------------------------------------- | ------- | ---------------------------------------------------- |
| `HKWS00HKG_R_20260150000_01D_30S_MO.rnx` | 22.3 MB | HKWS station, Hong Kong, 30-second sampling, 24h     |
| `ZIM200CHE_R_20260150000_01D_30S_MO.rnx` | 35.7 MB | ZIM2 station, Zimmerwald Switzerland, 30-second, 24h |

### Product Files (`C:\PPP_PROJECT\products\`)

**`products/sp3/` — Precise Satellite Orbits**

| File                                     | Size   | Systems       | Use With                              |
| ---------------------------------------- | ------ | ------------- | ------------------------------------- |
| `COD0OPSFIN_2026015_ORB.SP3`             | 1.4 MB | GPS + GLONASS | RTKLIB GPS/GLO comparison runs        |
| `COD0MGXFIN_20260150000_01D_05M_ORB.SP3` | 2.1 MB | G+R+E+C+J     | GAMP multi-GNSS, RTKLIB-EX multi-GNSS |
| `WUM0MGXRAP_20260150000_01D_05M_ORB.SP3` | 1.9 MB | G+R+E+C+J     | PRIDE PPP-AR (pdp3 auto-places this)  |

**`products/clk/` — Precise Satellite Clocks**

| File                                     | Size    | Systems       | Use With                                       |
| ---------------------------------------- | ------- | ------------- | ---------------------------------------------- |
| `IGS0OPSFIN_2026015_CLK.CLK`             | 12.0 MB | GPS + GLONASS | RTKLIB GPS/GLO runs (pair with COD0OPSFIN SP3) |
| `COD0MGXFIN_20260150000_01D_30S_CLK.CLK` | 35.3 MB | G+R+E+C+J     | **GAMP multi-GNSS (pair with COD0MGXFIN SP3)** |
| `WUM0MGXRAP_20260150000_01D_30S_CLK.CLK` | 19.0 MB | G+R+E+C+J     | PRIDE PPP-AR, RTKLIB-EX multi-GNSS fallback    |

<div style="background: #fffde7; border-left: 5px solid #f9a825; padding: 10px 16px; margin: 8px 0; border-radius: 4px">
💡 <strong>SP3 and CLK must always come from the SAME analysis center!</strong>
Mixing COD0OPSFIN SP3 with WUM CLK causes centimeter-level inconsistencies because
each center uses its own reference frame and clock datum. Always pair:
COD0OPSFIN SP3 + IGS0OPSFIN CLK, OR COD0MGXFIN SP3 + COD0MGXFIN CLK, OR WUM SP3 + WUM CLK.
</div>

**`products/erp/` — Earth Rotation Parameters**

| File                                     | Bytes | Use With                                  |
| ---------------------------------------- | ----- | ----------------------------------------- |
| `COD0MGXFIN_20260150000_01D_12H_ERP.ERP` | 1,631 | **GAMP** (most complete, covers all GNSS) |
| `EMR0OPSFIN_2026015_ERP.ERP`             | 340   | RTKLIB GPS/GLO runs                       |
| `WUM0MGXRAP_20260150000_01D_01D_ERP.ERP` | 468   | **PRIDE PPP-AR** (pdp3 uses WUM products) |

<div style="background: #fffde7; border-left: 5px solid #f9a825; padding: 10px 16px; margin: 8px 0; border-radius: 4px">
💡 <strong>ERP files are tiny text files (~300–1600 bytes)</strong> — the small size is normal.
They contain only a table of Earth Orientation Parameter values (X/Y polar motion, UT1-UTC)
for each day of the week. The actual values fit in one page of text.
</div>

**`products/bia/` — Phase/Code Biases**

| File                                     | Size   | Type                           | Use With                                      |
| ---------------------------------------- | ------ | ------------------------------ | --------------------------------------------- |
| `WUM0MGXRAP_20260150000_01D_01D_OSB.BIA` | 536 KB | Observable-Specific Bias (OSB) | **PRIDE PPP-AR** — phase biases needed for AR |
| `COD0MGXFIN_20260150000_01D_01D_OSB.BIA` | 749 KB | Observable-Specific Bias (OSB) | Alternative OSB for GAMP UC12 mode            |

**`products/dcb/`**

| File                         | Size   | Type                   | Use With                                      |
| ---------------------------- | ------ | ---------------------- | --------------------------------------------- |
| `CAS0OPSRAP_2026015_DCB.BIA` | 614 KB | Differential Code Bias | **GAMP** — required for ionosphere correction |

**`products/ionex/`**

| File                         | Size    | Use With                           |
| ---------------------------- | ------- | ---------------------------------- |
| `COD0OPSFIN_2026015_GIM.INX` | 1.62 MB | GAMP ionoopt=5, RTKLIB single-freq |

**`products/atx/`**

| File             | Size    | Use With                                         |
| ---------------- | ------- | ------------------------------------------------ |
| `igs20.atx`      | 52.7 MB | **ALL TOOLS** — antenna phase center corrections |
| `igs20_2401.atx` | 48.6 MB | Backup (not needed, team copy)                   |

**`products/obx/`**

| File                                     | Size    | Use With                                          |
| ---------------------------------------- | ------- | ------------------------------------------------- |
| `COD0MGXFIN_20260150000_01D_30S_ATT.OBX` | 35.0 MB | **PRIDE PPP-AR** — satellite attitude quaternions |

**`products/nav/`**

| File                                 | Size    | Use With                              |
| ------------------------------------ | ------- | ------------------------------------- |
| `BRD400DLR_S_20260150000_01D_MN.rnx` | 12.0 MB | **All tools** — primary broadcast nav |
| `BRDC00IGS_R_20260150000_01D_MN.rnx` | 12.0 MB | Backup (equivalent to BRD400DLR)      |

**`products/snx/`**

| File                         | Size    | Use With                                             |
| ---------------------------- | ------- | ---------------------------------------------------- |
| `MIT0OPSSNX_2026015_SOL.SNX` | 29.1 MB | GAMP + reference coordinates for accuracy evaluation |

</div>

---

<div style="border-left: 5px solid #e53e3e; background: #fff5f5; padding: 1px 20px; margin: 10px 0">

## PART 15 — STEP-BY-STEP: RTKLIB-EX 2.5.0 (formerly "demo5") 🔴

### What Is RTKLIB-EX and How Is It Different from RTKLIB?

**RTKLIB-EX** (previously named "demo5") is a community-maintained enhanced version of RTKLIB
developed by rtklibexplorer. It has the same GUI applications (rtkpost, rtkplot, rtkconv, etc.)
but with significantly improved algorithms especially for:

- PPP with ambiguity resolution (better than stock RTKLIB)
- Improved carrier-phase processing
- Better cycle-slip detection
- Improved multi-constellation support

**Already installed** at: `C:\Program Files\RTKLIB_EX_2.5.0\`
Executables: rtkpost.exe, rtkplot.exe, rtkconv.exe, rnx2rtkp.exe, convbin.exe, crx2rnx.exe, rtkget.exe, etc.
Also includes: `igs20_2353.atx` (antenna calibration file), `manual_demo5.pdf`, sample config files.

<div style="background: #e8f5e9; border-left: 5px solid #4caf50; padding: 10px 16px; margin: 8px 0; border-radius: 4px">
✅ <strong>No download needed.</strong> RTKLIB-EX 2.5.0 is already extracted and ready.
To verify: Help → About in rtkpost.exe shows "RTKLIB-EX 2.5.0".
Note: <code>C:\Program Files\RTKLIB-demo</code> contains <em>source code only</em> and can be deleted.
</div>

### Step 1 — Open RTKLIB-EX rtkpost

Double-click: `C:\Program Files\RTKLIB_EX_2.5.0\rtkpost.exe`

The window looks identical to stock RTKLIB but the Options dialog has additional
settings that are not available in stock RTKLIB.

### Step 3 — Load Input Files

In the RTKLIB-EX rtkpost window:

**RINEX OBS (Rover):**

```
C:\PPP_PROJECT\data\HKWS00HKG_R_20260150000_01D_30S_MO.rnx
```

(or ZIM2 for the second station)

**RINEX NAV/CLK:** (broadcast nav — used only for SPP fallback, not for PPP with precise products)

```
C:\PPP_PROJECT\products\nav\BRD400DLR_S_20260150000_01D_MN.rnx
```

**SP3/CLK** — Click the `+` button to add files. Add BOTH the SP3 and CLK:

```
C:\PPP_PROJECT\products\sp3\COD0MGXFIN_20260150000_01D_05M_ORB.SP3
C:\PPP_PROJECT\products\clk\COD0MGXFIN_20260150000_01D_30S_CLK.CLK
```

**Output File:**

```
C:\PPP_PROJECT\results\HKWS_RTKLIBEX_multiGNSS.pos
```

### Step 4 — Configure Options (RTKLIB-EX-specific settings)

Click **Options**:

#### Tab: Setting 1

| Parameter           | Value                        | Why                                               |
| ------------------- | ---------------------------- | ------------------------------------------------- |
| Positioning Mode    | `PPP-Static`                 | Static station, fastest convergence               |
| Frequencies         | `L1+L2`                      | Dual-frequency to eliminate ionosphere            |
| Filter Type         | `Forward`                    | Standard forward Kalman filter                    |
| Elevation Mask      | `10 deg`                     | RTKLIB-EX handles low-elevation better than stock |
| Satellite Ephemeris | `Precise`                    | Use the SP3+CLK files loaded above                |
| Satellite System    | Tick GPS ✓ GLO ✓ GAL ✓ BDS ✓ | Enable all constellations                         |

#### Tab: Setting 2 (RTKLIB-EX extra options)

| Parameter                   | Value    | Why                                               |
| --------------------------- | -------- | ------------------------------------------------- |
| Integer Ambiguity Res (GPS) | `PPP-AR` | **Key RTKLIB-EX feature** — fixes GPS ambiguities |
| Min Fix Count               | `10`     | Must track ≥10 epochs before attempting fix       |
| Min Hold Count              | `10`     | Must hold fix for ≥10 epochs                      |

#### Tab: Files

| Field                          | File                                                                 |
| ------------------------------ | -------------------------------------------------------------------- |
| Satellite/Rcvr Antenna PCO/PCV | `C:\PPP_PROJECT\products\atx\igs20.atx`                              |
| Earth Rotation Parameters      | `C:\PPP_PROJECT\products\erp\COD0MGXFIN_20260150000_01D_12H_ERP.ERP` |
| Ionosphere (IONEX)             | `C:\PPP_PROJECT\products\ionex\COD0OPSFIN_2026015_GIM.INX`           |
| DCB                            | `C:\PPP_PROJECT\products\dcb\CAS0OPSRAP_2026015_DCB.BIA`             |

### Step 5 — Run and View Results

1. Click **Execute** (bottom right)
2. Processing takes 1–3 minutes for 24h of 30-second data
3. Open rtkplot.exe → File → Open Solution → select your `.pos` output file
4. View → Plot Type → Position — watch convergence

### Step 6 — Research Comparison Runs for RTKLIB-EX

Run four times saving separate outputs:

| Run | Mode          | SP3+CLK                 | GNSS        | navsys setting | Output                        |
| --- | ------------- | ----------------------- | ----------- | -------------- | ----------------------------- |
| 1   | PPP-Static    | COD0OPSFIN + IGS0OPSFIN | GPS only    | GPS ✓          | `HKWS_RTKLIBEX_GPS.pos`       |
| 2   | PPP-Static    | COD0MGXFIN + COD0MGXFIN | GPS+GAL     | GPS✓ GAL✓      | `HKWS_RTKLIBEX_GE.pos`        |
| 3   | PPP-Static    | COD0MGXFIN + COD0MGXFIN | GPS+GAL+BDS | GPS✓ GAL✓ BDS✓ | `HKWS_RTKLIBEX_GEC.pos`       |
| 4   | PPP-Kinematic | COD0MGXFIN + COD0MGXFIN | GPS+GAL+BDS | GPS✓ GAL✓ BDS✓ | `HKWS_RTKLIBEX_kinematic.pos` |

</div>

---

<div style="border-left: 5px solid #e53e3e; background: #fff5f5; padding: 1px 20px; margin: 10px 0">

## PART 16 — Complete File Requirements Per Tool (With Reasons) 🔴

> This is the master reference. For each tool, every file is listed with its
> required/recommended/optional status AND the specific filename from your
> `C:\PPP_PROJECT\products\` folder.

---

### Tool 1: RTKLIB (rtkpost.exe) — `C:\Program Files\RTKLIB\bin\`

| File Type             | Status               | Your Specific File                                                                                      | Why Needed                                                        |
| --------------------- | -------------------- | ------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| Observation (.rnx)    | **REQUIRED**         | `data\HKWS00HKG_R_20260150000_01D_30S_MO.rnx`                                                           | Your raw measurements                                             |
| Broadcast Nav (.rnx)  | **REQUIRED**         | `products\nav\BRD400DLR_S_20260150000_01D_MN.rnx`                                                       | Needed even with precise products for initial orbit approximation |
| Precise Orbit (.sp3)  | **REQUIRED for PPP** | `products\sp3\COD0OPSFIN_2026015_ORB.SP3` (GPS/GLO) OR `products\sp3\WUM0MGXRAP_*_ORB.SP3` (multi-GNSS) | Replaces broadcast orbit; 100× more accurate                      |
| Precise Clock (.clk)  | **REQUIRED for PPP** | `products\clk\IGS0OPSFIN_2026015_CLK.CLK` (GPS/GLO) OR `products\clk\WUM0MGXRAP_*_CLK.CLK` (multi-GNSS) | Must match SP3 center; eliminates ~30 cm/ns clock errors          |
| Antenna ATX (.atx)    | **REQUIRED**         | `products\atx\igs20.atx`                                                                                | Without this, height error ~2–5 cm systematic                     |
| Earth Rotation (.erp) | RECOMMENDED          | `products\erp\EMR0OPSFIN_2026015_ERP.ERP`                                                               | RTKLIB reads via Files tab; corrects Earth orientation            |
| IONEX (.inx)          | RECOMMENDED          | `products\ionex\COD0OPSFIN_2026015_GIM.INX`                                                             | Critical for single-frequency; improves dual-freq convergence     |
| DCB (.bia)            | RECOMMENDED          | `products\dcb\CAS0OPSRAP_2026015_DCB.BIA`                                                               | Reduces code bias errors 0.5–2 m                                  |
| SINEX (.snx)          | Optional             | `products\snx\MIT0OPSSNX_2026015_SOL.SNX`                                                               | RTKLIB doesn't use SNX directly; use for external verification    |

**How RTKLIB receives product files:**

- SP3+CLK: via the `+` button in the main window
- ATX, ERP, IONEX, DCB: via Options → Files tab (separate fields for each)
- Nav: second input field in main window

---

### Tool 2: RTKLIB-EX 2.5.0 — `C:\Program Files\RTKLIB_EX_2.5.0\rtkpost.exe`

Same file types as RTKLIB, but with better SP3+CLK combination for multi-GNSS:

| File Type          | Status       | Your Specific File                                    | Difference from RTKLIB                                          |
| ------------------ | ------------ | ----------------------------------------------------- | --------------------------------------------------------------- |
| Observation (.rnx) | **REQUIRED** | Same as RTKLIB                                        | Same                                                            |
| Broadcast Nav      | **REQUIRED** | Same as RTKLIB                                        | Same                                                            |
| SP3                | **REQUIRED** | `products\sp3\COD0MGXFIN_20260150000_01D_05M_ORB.SP3` | **Use COD0MGXFIN** — RTKLIB-EX PPP-AR needs multi-GNSS products |
| CLK                | **REQUIRED** | `products\clk\COD0MGXFIN_20260150000_01D_30S_CLK.CLK` | **Use COD0MGXFIN** — must match SP3 center                      |
| ATX                | **REQUIRED** | `products\atx\igs20.atx`                              | Same                                                            |
| ERP                | RECOMMENDED  | `products\erp\COD0MGXFIN_20260150000_01D_12H_ERP.ERP` | **Use COD0MGXFIN ERP** to match orbit center                    |
| IONEX              | RECOMMENDED  | `products\ionex\COD0OPSFIN_2026015_GIM.INX`           | Same                                                            |
| DCB                | RECOMMENDED  | `products\dcb\CAS0OPSRAP_2026015_DCB.BIA`             | Same                                                            |

---

### Tool 3: GAMP — `C:\Program Files (x86)\GAMP\GAMP\bin\Windows\gamp.exe`

<div style="background: #fffde7; border-left: 5px solid #f9a825; padding: 10px 16px; margin: 8px 0; border-radius: 4px">
💡 <strong>GAMP's critical difference:</strong> ALL product files must be in the SAME FOLDER as
the observation file. GAMP auto-detects them by file extension and naming pattern.
There is no separate file-path configuration for each product — GAMP scans the folder.
Create a dedicated working folder like <code>C:\PPP_PROJECT\GAMP_work\2026015\</code>
and copy all needed files there.
</div>

| File Type            | Status            | Your Specific File                       | Config Parameter                     |
| -------------------- | ----------------- | ---------------------------------------- | ------------------------------------ |
| Observation (.rnx)   | **REQUIRED**      | `HKWS00HKG_R_20260150000_01D_30S_MO.rnx` | `obs file/folder`                    |
| Broadcast Nav (.rnx) | **REQUIRED**      | `BRD400DLR_S_20260150000_01D_MN.rnx`     | Auto-detected by .rnx extension      |
| SP3                  | **REQUIRED**      | `COD0MGXFIN_20260150000_01D_05M_ORB.SP3` | Auto-detected by .SP3 extension      |
| CLK                  | **REQUIRED**      | `COD0MGXFIN_20260150000_01D_30S_CLK.CLK` | Auto-detected by .CLK extension      |
| ERP                  | **REQUIRED**      | `COD0MGXFIN_20260150000_01D_12H_ERP.ERP` | Auto-detected by .ERP extension      |
| DCB/OSB              | **REQUIRED**      | `CAS0OPSRAP_20260150000_01D_01D_DCB.BIA` | Auto-detected by .BIA/.BSX extension |
| IONEX                | Req. if ionoopt=5 | `COD0OPSFIN_2026015_GIM.INX`             | Auto-detected by .INX/.I extension   |
| ATX                  | **REQUIRED**      | `igs20.atx`                              | Auto-detected by .atx extension      |
| SINEX (.snx)         | RECOMMENDED       | `MIT0OPSSNX_2026015_SOL.SNX`             | Auto-detected by .SNX extension      |
| Ocean Loading        | Optional          | `ocnload.blq`                            | Auto-detected (only if present)      |

**GAMP Config Parameters for Multi-GNSS PPP Static:**

```ini
obs file/folder = 1
               = C:\PPP_PROJECT\GAMP_work\2026015
posmode        = 7          # 7=PPP static (6=kinematic)
navsys         = 45         # 1+4+8+32 = GPS+GLONASS+Galileo+BDS (45 = all)
ionoopt        = 4          # 4=UC12 (uncombined dual-freq, best for multi-GNSS)
tropopt        = 3          # 3=ZTD estimation (estimate troposphere)
tidecorr       = 7          # 7=all tides (solid+ocean+pole)
outdir         = result
```

<div style="background: #fffde7; border-left: 5px solid #f9a825; padding: 10px 16px; margin: 8px 0; border-radius: 4px">
💡 <strong>GAMP navsys bit flags explained:</strong><br>
<code>navsys = 1</code> → GPS only<br>
<code>navsys = 5</code> → GPS(1) + GLONASS(4) = 5<br>
<code>navsys = 13</code> → GPS(1) + GLONASS(4) + Galileo(8) = 13<br>
<code>navsys = 45</code> → GPS(1) + GLONASS(4) + Galileo(8) + BDS(32) = 45<br>
<code>navsys = 61</code> → GPS(1)+GLONASS(4)+Galileo(8)+QZSS(16)+BDS(32) = 61
</div>

---

### Tool 4: PRIDE PPP-AR — `C:\Program Files (x86)\PRIDE-PPPAR-master\`

PRIDE auto-downloads WUM products when you run pdp3. For 2026-01-15 (GPS week 2401,
which is ≥ 2290), pdp3 will successfully download from multiple servers including IGN.
You can also pre-place products to avoid any download failures.

| File Type          | Status              | Specific File                            | How PRIDE Gets It                     |
| ------------------ | ------------------- | ---------------------------------------- | ------------------------------------- |
| Observation (.rnx) | **REQUIRED**        | `HKWS00HKG_R_20260150000_01D_30S_MO.rnx` | You specify on command line           |
| SP3                | **REQUIRED**        | `WUM0MGXRAP_20260150000_01D_05M_ORB.SP3` | pdp3 auto-downloads OR pre-place      |
| CLK                | **REQUIRED**        | `WUM0MGXRAP_20260150000_01D_30S_CLK.CLK` | pdp3 auto-downloads OR pre-place      |
| OSB (Phase Bias)   | **REQUIRED for AR** | `WUM0MGXRAP_20260150000_01D_01D_OSB.BIA` | pdp3 auto-downloads (key for PPP-AR!) |
| ERP                | **REQUIRED**        | `WUM0MGXRAP_20260150000_01D_01D_ERP.ERP` | pdp3 auto-downloads                   |
| ATX                | **REQUIRED**        | `igs20_2317.atx` in `table/`             | Already in PRIDE's table/ directory   |
| OBX (Attitude)     | RECOMMENDED         | `COD0MGXFIN_20260150000_01D_30S_ATT.OBX` | Must pre-place in product dir         |
| SINEX (.snx)       | Optional            | `MIT0OPSSNX_2026015_SOL.SNX`             | For a priori coordinates              |
| Nav (.rnx)         | Auto                | `BRDC00IGS_R_*_MN.rnx`                   | pdp3 downloads automatically          |
| sat_parameters     | Auto                | (from ftp://gnsswhu.cn)                  | pdp3 downloads from table server      |

<div style="background: #fffde7; border-left: 5px solid #f9a825; padding: 10px 16px; margin: 8px 0; border-radius: 4px">
💡 <strong>Why does PRIDE use WUM products while other tools use CODE products?</strong><br>
PRIDE PPP-AR is developed by Wuhan University, and its ambiguity resolution algorithm
uses Wuhan's specific Observable-Specific Bias (OSB) products. The SP3/CLK and OSB MUST
come from the same analysis center's calibration system. Using CODE SP3 with WUM OSB
would give inconsistent phase bias corrections. PRIDE + WUM products = consistent system.
</div>

**Pre-placing products for PRIDE (if pdp3 download fails):**

```bash
# From WSL — PRIDE looks for products in <working_dir>/<year>/product/common/
mkdir -p "/mnt/c/PPP_PROJECT/PRIDE_work/2026/015/product/common"
cp /mnt/c/PPP_PROJECT/products/sp3/WUM0MGXRAP_20260150000_01D_05M_ORB.SP3 \
   "/mnt/c/PPP_PROJECT/PRIDE_work/2026/015/product/common/"
cp /mnt/c/PPP_PROJECT/products/clk/WUM0MGXRAP_20260150000_01D_30S_CLK.CLK \
   "/mnt/c/PPP_PROJECT/PRIDE_work/2026/015/product/common/"
cp /mnt/c/PPP_PROJECT/products/erp/WUM0MGXRAP_20260150000_01D_01D_ERP.ERP \
   "/mnt/c/PPP_PROJECT/PRIDE_work/2026/015/product/common/"
cp /mnt/c/PPP_PROJECT/products/bia/WUM0MGXRAP_20260150000_01D_01D_OSB.BIA \
   "/mnt/c/PPP_PROJECT/PRIDE_work/2026/015/product/common/"
```

</div>

---

<div style="border-left: 5px solid #e53e3e; background: #fff5f5; padding: 1px 20px; margin: 10px 0">

## PART 17 — Which File to Use for Each Research Question 🔴

> This table maps every research experiment to the exact files, tool settings, and
> expected output location. Use this as your run checklist.

### Research Question 1: Broadcast vs. Precise Products

**Goal:** How much does position accuracy improve when using precise SP3+CLK vs. broadcast nav?

| Run                     | Tool | SP3/CLK                         | ionoopt | navsys | Output                  | Expected Accuracy |
| ----------------------- | ---- | ------------------------------- | ------- | ------ | ----------------------- | ----------------- |
| A: Broadcast only       | GAMP | None (leave out)                | 2=IF12  | 1=GPS  | `broadcast_GPS.pos`     | **2–5 m** RMS     |
| B: Precise (GPS)        | GAMP | COD0OPSFIN SP3 + IGS0OPSFIN CLK | 2=IF12  | 1=GPS  | `precise_GPS.pos`       | **5–15 cm** RMS   |
| C: Precise (multi-GNSS) | GAMP | COD0MGXFIN SP3+CLK              | 4=UC12  | 45=all | `precise_multiGNSS.pos` | **2–5 cm** RMS    |

**Specific GAMP config changes for Broadcast-only:**

```ini
posmode = 7          # PPP static
navsys  = 1          # GPS only
ionoopt = 2          # IF12 (broadcast ionosphere cancels automatically)
# Remove SP3 and CLK from working folder
```

---

### Research Question 2: GPS-only vs. Multi-GNSS

**Goal:** Does adding Galileo/BeiDou reduce convergence time?

| Run             | Tool | navsys                     | SP3+CLK                 | Convergence Time       |
| --------------- | ---- | -------------------------- | ----------------------- | ---------------------- |
| GPS only        | GAMP | 1                          | COD0OPSFIN + IGS0OPSFIN | **20–35 min** to 10 cm |
| GPS + Galileo   | GAMP | 13 (1+4+8→ actually 1+8=9) | COD0MGXFIN + COD0MGXFIN | **12–20 min** to 10 cm |
| GPS + GAL + BDS | GAMP | 45                         | COD0MGXFIN + COD0MGXFIN | **8–15 min** to 10 cm  |

<div style="background: #fffde7; border-left: 5px solid #f9a825; padding: 10px 16px; margin: 8px 0; border-radius: 4px">
💡 <strong>GAMP navsys for GPS+Galileo only = 9 (1+8)</strong>, not 13.
GLONASS=4, so GPS+GLONASS+Galileo = 13. For GPS+Galileo without GLONASS = 9.
For your comparison, running GPS+GAL (9) separately from GPS+GAL+BDS (45) is
more informative for showing Galileo's specific contribution.
</div>

---

### Research Question 3: Float PPP vs. PPP-AR

**Goal:** How much faster does PRIDE PPP-AR converge compared to float PPP?

| Run       | Tool      | Command                           | AR On? | Expected Convergence |
| --------- | --------- | --------------------------------- | ------ | -------------------- |
| Float PPP | PRIDE     | `pdp3 -m S -float -sys gec <obs>` | No     | 20–40 min to 5 cm    |
| PPP-AR    | PRIDE     | `pdp3 -m S -sys gec <obs>`        | Yes    | **2–8 min** to 5 cm  |
| Float PPP | RTKLIB    | PPP-Static, Ambiguity=Off         | No     | 20–40 min            |
| PPP-AR    | RTKLIB-EX | PPP-Static, Ambiguity=PPP-AR      | Yes    | 5–15 min             |

**Files for PRIDE runs:** WUM0MGXRAP SP3 + CLK + OSB + ERP (auto-downloaded by pdp3)

---

### Research Question 4: Station Comparison — HKWS vs. ZIM2

**Goal:** Compare tropical/coastal (HK) vs. mid-latitude/inland (Switzerland) performance.

Run the SAME experiment on BOTH stations:

```bash
# PRIDE: ZIM2
pdp3 -m S -sys gec --config /tmp/pride_config.cfg \
  /mnt/c/PPP_PROJECT/data/ZIM200CHE_R_20260150000_01D_30S_MO.rnx

# PRIDE: HKWS
pdp3 -m S -sys gec --config /tmp/pride_config.cfg \
  /mnt/c/PPP_PROJECT/data/HKWS00HKG_R_20260150000_01D_30S_MO.rnx
```

Expected: ZIM2 (inland, mid-latitude, 5-constellation receiver) converges faster and
achieves lower tropospheric delay uncertainty than HKWS (coastal, tropical, higher humidity).

---

### Research Question 5: Tool Comparison — All Four Tools, Same Data

**Goal:** Compare accuracy and convergence across RTKLIB, RTKLIB-EX, GAMP, PRIDE.

Use identical settings (GPS+GAL+BDS, dual-freq, static, same SP3+CLK) on the same
observation file. Run these commands/configs:

| Tool      | Files to Use                    | Mode                 | Expected Final Accuracy |
| --------- | ------------------------------- | -------------------- | ----------------------- |
| RTKLIB    | WUM SP3+CLK, igs20.atx, CAS DCB | PPP-Static           | 5–15 cm (float)         |
| RTKLIB-EX | COD0MGXFIN SP3+CLK, igs20.atx   | PPP-Static + AR      | 2–8 cm                  |
| GAMP      | COD0MGXFIN SP3+CLK+ERP, CAS DCB | navsys=45, ionoopt=4 | 2–5 cm                  |
| PRIDE     | WUM SP3+CLK+OSB (auto)          | pdp3 -m S -sys gec   | **1–3 cm** (PPP-AR)     |

</div>

---

<div style="border-left: 5px solid #e53e3e; background: #fff5f5; padding: 1px 20px; margin: 10px 0">

## PART 18 — PRIDE PPP-AR: Complete Windows/WSL Setup and Running Real Data 🔴

> This replaces PART 7 with the working procedure verified on your system.
> PART 7 above shows the general approach; this section shows the ACTUAL commands
> that work on your Windows + WSL setup.

### Your PRIDE Setup (Already Done)

| Component      | Location                                             | Status                |
| -------------- | ---------------------------------------------------- | --------------------- |
| Source code    | `C:\Program Files (x86)\PRIDE-PPPAR-master\`         | Compiled ✅           |
| Binaries       | `C:\Program Files (x86)\PRIDE-PPPAR-master\bin\`     | Built ✅              |
| Table files    | `C:\Program Files (x86)\PRIDE-PPPAR-master\table\`   | Present ✅            |
| `pdp3` wrapper | `C:\Program Files (x86)\PRIDE-PPPAR-master\bin\pdp3` | Created ✅            |
| WSL path alias | `/tmp/pride` → PRIDE root                            | Created per run ✅    |
| Config fix     | `/tmp/pride_config_test.cfg`                         | Created by test.sh ✅ |

### Why test.sh Still Fails (and How to Fix It)

The current test.sh output shows:

- ✅ Config found: `/tmp/pride_config_test.cfg`
- ✅ Table directory: `/tmp/pride/table`
- ✅ Executables all found
- ✅ Broadcast nav downloads (BRDC00IGS_R files)
- ❌ WUM SP3/CLK download fails via FTP — **"unexpected end of file"** from gunzip

**Root cause:** The PRIDE test data uses dates in 2020–2023 (GPS weeks 2086–2243).
In `pdp3.sh`, the IGN FTP fallback is **hardcoded to only work for GPS week ≥ 2290**.
So for test dates, only the Wuhan FTP is tried — which either times out or returns
a partial file. The partial `.gz` file then fails the `gunzip` step with the error:

```
gzip: WUM0MGXRAP_20200010000_01D_05M_ORB.SP3.gz: unexpected end of file
  FAILED: SP3
```

**Fix: Use `scripts/download_test_products.sh` to pre-download BEFORE running test.sh:**

```bash
# In WSL — pre-download with 3-source fallback and gz integrity check:
bash /mnt/c/PPP_PROJECT/scripts/download_test_products.sh

# Then run the official test:
cd "/mnt/c/Program Files (x86)/PRIDE-PPPAR-master/example"
bash test.sh
```

`download_test_products.sh` improvements over the naive approach:

1. **Three-source fallback**: IGN FTP → Wuhan MGEX → Wuhan phasebias
2. **gz integrity check**: `gunzip -t` validates the file before decompressing — no more corrupt partial-file failures
3. **Clean retry**: deletes partial file before each retry (avoids corrupt+append)
4. Files cached in `<example>/<year>/product/common/` — test.sh uses cached files

### Running PRIDE on Your Real Data (2026-01-15, HKWS and ZIM2)

For GPS week 2401 (2026-01-15), the IGN FTP fallback IS enabled (2401 ≥ 2290).
pdp3 should auto-download successfully without needing pre-downloads.

**Step 1: Create a PRIDE working directory**

```bash
# In WSL:
mkdir -p /mnt/c/PPP_PROJECT/PRIDE_work
cd /mnt/c/PPP_PROJECT/PRIDE_work
```

**Step 2: Create a config file pointing to your table directory**

```bash
cat > /tmp/pride_config.cfg << 'EOF'
## PRIDE PPP-AR configuration for HKWS/ZIM2 2026-01-15
## Modified from config_template

## Table directory
Table directory = /mnt/c/Program Files (x86)/PRIDE-PPPAR-master/table

## Satellite product
Product directory = Default

## Processing options
ZTD model         = STO
Tides             = SOLID OCEAN POLE
EOF
```

**Alternative: Use the symlink approach to avoid spaces in path:**

```bash
# Create symlink to avoid "Program Files (x86)" path issues
ln -sfn "/mnt/c/Program Files (x86)/PRIDE-PPPAR-master" /tmp/pride

# Create config using symlink path
cat > /tmp/pride_config.cfg << 'EOF'
Table directory = /tmp/pride/table
Product directory = Default
ZTD model         = STO
Tides             = SOLID OCEAN POLE
EOF
```

**Step 3: Set PATH and run pdp3**

```bash
export PATH="/tmp/pride/bin:/tmp/pride/scripts:$PATH"

# Static PPP-AR, GPS + Galileo + BeiDou
cd /mnt/c/PPP_PROJECT/PRIDE_work
pdp3 -m S -sys gec --config /tmp/pride_config.cfg \
  /mnt/c/PPP_PROJECT/data/HKWS00HKG_R_20260150000_01D_30S_MO.rnx
```

**Step 4: Check output**

PRIDE creates a folder `2026/015/` in your current directory:

```
PRIDE_work/
  2026/015/
    product/common/          ← downloaded WUM products
    kin_2026015_hkws         ← kinematic position time series
    ztd_2026015              ← tropospheric delay estimates
    res_2026015              ← observation residuals
    flt_2026015_hkws         ← Kalman filter states
    log_2026015_hkws         ← processing log
    config_hkws              ← used configuration
```

**Reading the kin\_ output file:**

```
# Columns: MJD, SOD, X(m), Y(m), Z(m), SigX, SigY, SigZ, NumSat, PDOP, Fix
58863.0  0.0  -2414262.123  5386840.456  2404337.789  0.012  0.014  0.023  12  1.8  1
```

- Column 11 (Fix): `1` = ambiguity fixed (PPP-AR), `0` = float

**Step 5: Run all four scenarios for comparison**

```bash
# Run 1: Float PPP, GPS only
pdp3 -m S -float -sys g --config /tmp/pride_config.cfg \
  /mnt/c/PPP_PROJECT/data/HKWS00HKG_R_20260150000_01D_30S_MO.rnx
mv 2026/015 results/HKWS_float_GPS

# Run 2: PPP-AR, GPS only
pdp3 -m S -sys g --config /tmp/pride_config.cfg \
  /mnt/c/PPP_PROJECT/data/HKWS00HKG_R_20260150000_01D_30S_MO.rnx
mv 2026/015 results/HKWS_AR_GPS

# Run 3: PPP-AR, GPS+Galileo+BDS
pdp3 -m S -sys gec --config /tmp/pride_config.cfg \
  /mnt/c/PPP_PROJECT/data/HKWS00HKG_R_20260150000_01D_30S_MO.rnx
mv 2026/015 results/HKWS_AR_GEC

# Run 4: Same for ZIM2
pdp3 -m S -sys gec --config /tmp/pride_config.cfg \
  /mnt/c/PPP_PROJECT/data/ZIM200CHE_R_20260150000_01D_30S_MO.rnx
mv 2026/015 results/ZIM2_AR_GEC
```

### Setting Up GAMP for 2026-01-15 — Complete Research Analysis

#### Step 1: Prepare the Working Folder (one time)

GAMP requires all input files in a single folder. Run this once in PowerShell:

```powershell
# Create working folder
New-Item -ItemType Directory -Force "C:\PPP_PROJECT\GAMP_work\2026015"

# Copy observation files
Copy-Item "C:\PPP_PROJECT\data\HKWS00HKG_R_20260150000_01D_30S_MO.rnx" "C:\PPP_PROJECT\GAMP_work\2026015\"
Copy-Item "C:\PPP_PROJECT\data\ZIM200CHE_R_20260150000_01D_30S_MO.rnx"  "C:\PPP_PROJECT\GAMP_work\2026015\"

# Navigation (broadcast)
Copy-Item "C:\PPP_PROJECT\products\nav\BRD400DLR_S_20260150000_01D_MN.rnx" "C:\PPP_PROJECT\GAMP_work\2026015\"

# SP3 orbit files (GPS/GLO only AND multi-GNSS — you'll switch between them)
Copy-Item "C:\PPP_PROJECT\products\sp3\COD0OPSFIN_2026015_ORB.SP3"                "C:\PPP_PROJECT\GAMP_work\2026015\"
Copy-Item "C:\PPP_PROJECT\products\sp3\COD0MGXFIN_20260150000_01D_05M_ORB.SP3"    "C:\PPP_PROJECT\GAMP_work\2026015\"

# CLK clock files (GPS/GLO only AND multi-GNSS)
Copy-Item "C:\PPP_PROJECT\products\clk\IGS0OPSFIN_2026015_CLK.CLK"                "C:\PPP_PROJECT\GAMP_work\2026015\"
Copy-Item "C:\PPP_PROJECT\products\clk\COD0MGXFIN_20260150000_01D_30S_CLK.CLK"    "C:\PPP_PROJECT\GAMP_work\2026015\"

# ERP, DCB, IONEX, ATX, SNX
Copy-Item "C:\PPP_PROJECT\products\erp\COD0MGXFIN_20260150000_01D_12H_ERP.ERP"    "C:\PPP_PROJECT\GAMP_work\2026015\"
Copy-Item "C:\PPP_PROJECT\products\dcb\CAS0OPSRAP_2026015_DCB.BIA"                "C:\PPP_PROJECT\GAMP_work\2026015\"
Copy-Item "C:\PPP_PROJECT\products\ionex\COD0OPSFIN_2026015_GIM.INX"              "C:\PPP_PROJECT\GAMP_work\2026015\"
Copy-Item "C:\PPP_PROJECT\products\atx\igs20.atx"                                 "C:\PPP_PROJECT\GAMP_work\2026015\"
Copy-Item "C:\PPP_PROJECT\products\snx\MIT0OPSSNX_2026015_SOL.SNX"                "C:\PPP_PROJECT\GAMP_work\2026015\"
```

Create the results folder too:

```cmd
mkdir C:\PPP_PROJECT\GAMP_work\2026015\result
```

---

#### Step 2: Run Scenario A — GPS-only, Broadcast Ephemeris (Baseline)

**Purpose:** This is your baseline "no precise products" run. Shows what accuracy
you get with just the broadcast navigation message — what your phone essentially does
but in post-processing. Expected horizontal accuracy: 1–3 m.

**Why these settings?**

- `navsys = 1` → GPS only (broadcast nav only has GPS info in .rnx mixed nav, GLONASS possible too but let's isolate GPS)
- `ionoopt = 1` → Use Klobuchar broadcast model (single-freq equivalent, no precise IONEX needed)
- No `sp3 file` or `clk file` → forces GAMP to use broadcast ephemeris

Create `C:\PPP_PROJECT\GAMP_work\2026015\gamp_A_broadcast.cfg`:

```ini
# Scenario A: GPS-only, Broadcast products (baseline comparison)
obs file/folder = 1
               = C:\PPP_PROJECT\GAMP_work\2026015

start_time      = 0    2026/01/15  00:00:00.0
end_time        = 0    2026/01/15  23:59:30.0
posmode         = 7               # PPP static
soltype         = 0               # forward filter
navsys          = 1               # GPS only
inpfrq          = 2               # dual frequency
ionoopt         = 1               # broadcast Klobuchar model
tropopt         = 3               # estimate ZTD
tropmf          = 1               # GMF mapping function
tidecorr        = 7               # solid+ocean+pole tides
minelev         = 7.0

outdir          = result
output          = 21
     pos        = 1
     debug      = 1
     pdop        = 1
     elev        = 1
     dtrp        = 1

# Broadcast navigation
nav file        = C:\PPP_PROJECT\GAMP_work\2026015\BRD400DLR_S_20260150000_01D_MN.rnx

# No sp3/clk = uses broadcast ephemeris
atx file        = C:\PPP_PROJECT\GAMP_work\2026015\igs20.atx
snx file        = C:\PPP_PROJECT\GAMP_work\2026015\MIT0OPSSNX_2026015_SOL.SNX
```

```cmd
"C:\Program Files (x86)\GAMP\GAMP\bin\Windows\gamp.exe" "C:\PPP_PROJECT\GAMP_work\2026015\gamp_A_broadcast.cfg"
```

Result files will appear in `C:\PPP_PROJECT\GAMP_work\2026015\result\`
Output: `HKWS00HKG*.pos` and `ZIM200CHE*.pos`

---

#### Step 3: Run Scenario B — GPS-only, Precise Products, IF model

**Purpose:** Classic GPS PPP. Shows the improvement from using precise sp3+clk
over broadcast. The ionosphere-free (IF) combination on two frequencies cancels
~99.9% of ionosphere delay mathematically. Expected convergence: 20–40 min to cm-level.

**Why these settings?**

- `navsys = 1` → GPS only (COD0OPSFIN SP3 is GPS/GLONASS, but we focus on GPS)
- `ionoopt = 2` → Ionosphere-free L1/L2 combination (IF12) — the classic PPP approach
- `sp3 file` = COD0OPSFIN (GPS+GLO precise orbits, ~2cm accuracy)
- `clk file` = IGS0OPSFIN (IGS combined clock, best for GPS)
- SP3 and CLK **must come from the same analysis center pair** — COD0OPSFIN + IGS0OPSFIN is the standard IGS pair

Create `C:\PPP_PROJECT\GAMP_work\2026015\gamp_B_GPS_IF.cfg`:

```ini
# Scenario B: GPS-only, Precise products, Ionosphere-Free (IF12)
obs file/folder = 1
               = C:\PPP_PROJECT\GAMP_work\2026015

start_time      = 0    2026/01/15  00:00:00.0
end_time        = 0    2026/01/15  23:59:30.0
posmode         = 7               # PPP static
soltype         = 0               # forward filter
navsys          = 1               # GPS only
inpfrq          = 2               # dual frequency
ionoopt         = 2               # IF12 ionosphere-free combination
tropopt         = 3               # estimate ZTD
tropmf          = 1               # GMF mapping function
tidecorr        = 7               # solid+ocean+pole tides
minelev         = 7.0

outdir          = result
output          = 21
     pos        = 1
     debug      = 1
     pdop        = 1
     elev        = 1
     dtrp        = 1

nav file        = C:\PPP_PROJECT\GAMP_work\2026015\BRD400DLR_S_20260150000_01D_MN.rnx
sp3 file        = C:\PPP_PROJECT\GAMP_work\2026015\COD0OPSFIN_2026015_ORB.SP3
clk file        = C:\PPP_PROJECT\GAMP_work\2026015\IGS0OPSFIN_2026015_CLK.CLK
erp file        = C:\PPP_PROJECT\GAMP_work\2026015\COD0MGXFIN_20260150000_01D_12H_ERP.ERP
dcb p1c1 file   = C:\PPP_PROJECT\GAMP_work\2026015\CAS0OPSRAP_2026015_DCB.BIA
atx file        = C:\PPP_PROJECT\GAMP_work\2026015\igs20.atx
snx file        = C:\PPP_PROJECT\GAMP_work\2026015\MIT0OPSSNX_2026015_SOL.SNX
```

```cmd
"C:\Program Files (x86)\GAMP\GAMP\bin\Windows\gamp.exe" "C:\PPP_PROJECT\GAMP_work\2026015\gamp_B_GPS_IF.cfg"
```

---

#### Step 4: Run Scenario C — Multi-GNSS (G+R+E+C), Uncombined (UC12)

**Purpose:** The "best GAMP can do" run. Using GPS + GLONASS + Galileo + BeiDou
with the uncombined dual-frequency model. More satellites → faster convergence,
better geometry. UC12 treats ionosphere as an unknown rather than cancelling it,
which preserves more signal information and improves accuracy for multi-GNSS.

**Why these settings?**

- `navsys = 45` → GPS(1) + GLONASS(4) + Galileo(8) + BeiDou(32) = 45
  (This is the maximum — Galileo and BeiDou require MGEX products)
- `ionoopt = 4` → Uncombined dual-frequency (UC12). Each satellite's ionosphere
  is estimated as an extra unknown. This is preferred for multi-GNSS because
  different constellations use different frequencies and the classic IF12 combination
  coefficients are constellation-specific
- `sp3 file` = COD0MGXFIN (CODE multi-GNSS final — highest quality MGEX orbits)
- `clk file` = COD0MGXFIN (same center — they MUST match)
- DCB file is critical here: tells GAMP the code bias differences between signal
  types for each satellite, essential for BeiDou and Galileo

Create `C:\PPP_PROJECT\GAMP_work\2026015\gamp_C_multiGNSS_UC.cfg`:

```ini
# Scenario C: Multi-GNSS (G+R+E+C), Uncombined dual-frequency (UC12)
# This is the highest-accuracy GAMP configuration
obs file/folder = 1
               = C:\PPP_PROJECT\GAMP_work\2026015

start_time      = 0    2026/01/15  00:00:00.0
end_time        = 0    2026/01/15  23:59:30.0
posmode         = 7               # PPP static
soltype         = 0               # forward filter
navsys          = 45              # GPS+GLONASS+Galileo+BeiDou (1+4+8+32)
inpfrq          = 2               # dual frequency
ionoopt         = 4               # UC12 uncombined — estimates ionosphere per sat
ionopnoise      = 1               # ionosphere random walk noise
ionconstraint   = 0               # no ionosphere constraint (let it float)
tropopt         = 3               # estimate ZTD
tropmf          = 1               # GMF mapping function
tidecorr        = 7               # solid+ocean+pole tides
minelev         = 7.0

outdir          = result
output          = 21
     pos        = 1
     debug      = 1
     pdop        = 1
     elev        = 1
     dtrp        = 1

nav file        = C:\PPP_PROJECT\GAMP_work\2026015\BRD400DLR_S_20260150000_01D_MN.rnx
sp3 file        = C:\PPP_PROJECT\GAMP_work\2026015\COD0MGXFIN_20260150000_01D_05M_ORB.SP3
clk file        = C:\PPP_PROJECT\GAMP_work\2026015\COD0MGXFIN_20260150000_01D_30S_CLK.CLK
erp file        = C:\PPP_PROJECT\GAMP_work\2026015\COD0MGXFIN_20260150000_01D_12H_ERP.ERP
dcb p1c1 file   = C:\PPP_PROJECT\GAMP_work\2026015\CAS0OPSRAP_2026015_DCB.BIA
atx file        = C:\PPP_PROJECT\GAMP_work\2026015\igs20.atx
snx file        = C:\PPP_PROJECT\GAMP_work\2026015\MIT0OPSSNX_2026015_SOL.SNX
```

```cmd
"C:\Program Files (x86)\GAMP\GAMP\bin\Windows\gamp.exe" "C:\PPP_PROJECT\GAMP_work\2026015\gamp_C_multiGNSS_UC.cfg"
```

---

#### Step 5: Run Scenario D — Multi-GNSS with IONEX GIM

**Purpose:** Tests whether using an external ionosphere map (GIM = Global Ionosphere
Map) improves results compared to estimating ionosphere per-satellite. In UC12 with
external GIM, the ionosphere is constrained by the GIM prediction, which can speed up
convergence especially in single-epoch or short-session processing.

**Why these settings?**

- `ionoopt = 5` → Use IONEX GIM file as ionosphere constraint
- `ionfile` → Points to the COD GIM file (CODE's global ionosphere map, 1-degree resolution, updated every 2 hours)
- Compared to Scenario C: determines whether the external ionosphere map actually helps

Create `C:\PPP_PROJECT\GAMP_work\2026015\gamp_D_multiGNSS_GIM.cfg`:

```ini
# Scenario D: Multi-GNSS with IONEX GIM constraint
obs file/folder = 1
               = C:\PPP_PROJECT\GAMP_work\2026015

start_time      = 0    2026/01/15  00:00:00.0
end_time        = 0    2026/01/15  23:59:30.0
posmode         = 7
soltype         = 0
navsys          = 45              # GPS+GLONASS+Galileo+BeiDou
inpfrq          = 2
ionoopt         = 5               # use external IONEX GIM
tropopt         = 3
tropmf          = 1
tidecorr        = 7
minelev         = 7.0

outdir          = result
output          = 21
     pos        = 1
     debug      = 1
     pdop        = 1
     elev        = 1
     dtrp        = 1

nav file        = C:\PPP_PROJECT\GAMP_work\2026015\BRD400DLR_S_20260150000_01D_MN.rnx
sp3 file        = C:\PPP_PROJECT\GAMP_work\2026015\COD0MGXFIN_20260150000_01D_05M_ORB.SP3
clk file        = C:\PPP_PROJECT\GAMP_work\2026015\COD0MGXFIN_20260150000_01D_30S_CLK.CLK
erp file        = C:\PPP_PROJECT\GAMP_work\2026015\COD0MGXFIN_20260150000_01D_12H_ERP.ERP
dcb p1c1 file   = C:\PPP_PROJECT\GAMP_work\2026015\CAS0OPSRAP_2026015_DCB.BIA
ion file        = C:\PPP_PROJECT\GAMP_work\2026015\COD0OPSFIN_2026015_GIM.INX
atx file        = C:\PPP_PROJECT\GAMP_work\2026015\igs20.atx
snx file        = C:\PPP_PROJECT\GAMP_work\2026015\MIT0OPSSNX_2026015_SOL.SNX
```

```cmd
"C:\Program Files (x86)\GAMP\GAMP\bin\Windows\gamp.exe" "C:\PPP_PROJECT\GAMP_work\2026015\gamp_D_multiGNSS_GIM.cfg"
```

---

#### Step 6: Repeat Scenarios B and C for ZIM2

To compare HKWS (Hong Kong, low-latitude, higher ionosphere activity) vs ZIM2
(Switzerland, mid-latitude, calmer ionosphere), just change the observation folder
to a folder containing **only ZIM2 data**, or temporarily rename/move files.

**Simplest approach:** Copy the entire working folder for each station:

```cmd
mkdir C:\PPP_PROJECT\GAMP_work\2026015_ZIM2
# Copy all product files from 2026015 to 2026015_ZIM2
xcopy "C:\PPP_PROJECT\GAMP_work\2026015\*" "C:\PPP_PROJECT\GAMP_work\2026015_ZIM2\" /E /I
# Remove HKWS observation from the ZIM2 folder
del "C:\PPP_PROJECT\GAMP_work\2026015_ZIM2\HKWS00HKG_R_20260150000_01D_30S_MO.rnx"
```

Then update the `obs file/folder` path in each `.cfg` file to point to `2026015_ZIM2`
and the `outdir` to `result_ZIM2`. Run the same scenarios for both stations.

---

#### Step 7: View Results in rtkplot

**Yes — GAMP .pos files open directly in rtkplot.exe.**

1. Open `C:\Program Files\RTKLIB\bin\rtkplot.exe`
2. Menu: **File → Open Solution 1** (or drag-and-drop the `.pos` file)
3. Navigate to: `C:\PPP_PROJECT\GAMP_work\2026015\result\`
4. Select e.g. `HKWS00HKG_R_20260150000_01D_30S_MO.pos`
5. In the "Plot Type" dropdown (top-left), choose:
   - **"Gnd Trk"** → ground track map
   - **"Position"** → E/N/U error vs time (most useful for convergence analysis)
   - **"Velocity"** → for kinematic only
   - **"Residual"** → satellite residuals
6. For convergence comparison: Plot type = **"Position"**, click **"ORI"** button to
   set the reference origin to your known coordinates. The SNX file provides these
   but you can also manually enter from ITRF2020:
   - HKWS: 3396803.066 E, 5513394.978 N, 2499393.701 U (ECEF XYZ)
   - ZIM2: 4331297.344, 567555.639, 4633133.920 (ECEF XYZ)

**To overlay multiple runs** (e.g., GPS-only vs Multi-GNSS):

- File → Open Solution 1 → (first .pos file, shown in red)
- File → Open Solution 2 → (second .pos file, shown in green)
- This gives a direct visual comparison of convergence speed

**What to look for:**

- How long until the E/N/U position error drops below 10 cm? (convergence time)
- What is the final accuracy after convergence? (steady-state RMS)
- Is multi-GNSS noticeably faster to converge than GPS-only?

---

#### Quick Run Summary (all 4 scenarios, both stations)

| Config file                | navsys    | ionoopt       | Products                | Station   | Research Question         |
| -------------------------- | --------- | ------------- | ----------------------- | --------- | ------------------------- |
| `gamp_A_broadcast.cfg`     | 1 (G)     | 1 (Klobuchar) | Broadcast only          | HKWS+ZIM2 | RQ1: Broadcast vs Precise |
| `gamp_B_GPS_IF.cfg`        | 1 (G)     | 2 (IF12)      | COD0OPSFIN + IGS0OPSFIN | HKWS+ZIM2 | RQ1+RQ2 baseline          |
| `gamp_C_multiGNSS_UC.cfg`  | 45 (GREC) | 4 (UC12)      | COD0MGXFIN + COD0MGXFIN | HKWS+ZIM2 | RQ2: multi-GNSS           |
| `gamp_D_multiGNSS_GIM.cfg` | 45 (GREC) | 5 (GIM)       | COD0MGXFIN + GIM        | HKWS+ZIM2 | RQ3: ionosphere model     |

Run them in sequence:

```cmd
set GAMP="C:\Program Files (x86)\GAMP\GAMP\bin\Windows\gamp.exe"
set WD=C:\PPP_PROJECT\GAMP_work\2026015

%GAMP% "%WD%\gamp_A_broadcast.cfg"
%GAMP% "%WD%\gamp_B_GPS_IF.cfg"
%GAMP% "%WD%\gamp_C_multiGNSS_UC.cfg"
%GAMP% "%WD%\gamp_D_multiGNSS_GIM.cfg"
```

Each run takes ~1–5 minutes. Results go to `result\` subfolder.
Then visualize with the Python scripts (GAMP .pos is **not** readable directly by rtkplot):

```cmd
cd C:\PPP_PROJECT\GAMP_work
python scripts/plot_gamp_enu.py --no-show result/HKWS00HKG_R_20260150000_01D_30S_MO.pos
python scripts/gamp2rtkplot.py --open result/HKWS00HKG_R_20260150000_01D_30S_MO.pos
```

---

<div style="border-left: 5px solid #e53e3e; background: #fff5f5; padding: 1px 20px; margin: 10px 0">

## PART 19 — Expected Results Reference 🔴

> Use these numbers to verify your results are reasonable. Values significantly
> outside these ranges suggest a configuration error.

### Station Reference Coordinates (ITRF2020)

These are the IGS ITRF2020 coordinates for your stations (use for accuracy evaluation):

**HKWS (Hong Kong):**

- Latitude: ~22.3° N
- Longitude: ~114.1° E
- Height: ~71 m (ellipsoidal)
- Multi-GNSS: GPS + GLONASS + Galileo + BeiDou
- Expected visible satellites: 12–18 (multi-GNSS), 8–12 (GPS only)

**ZIM2 (Zimmerwald, Switzerland):**

- Latitude: ~46.9° N
- Longitude: ~7.5° E
- Height: ~956 m (ellipsoidal)
- Multi-GNSS: GPS + GLONASS + Galileo
- Expected visible satellites: 10–16 (multi-GNSS), 6–10 (GPS only)

<div style="background: #fffde7; border-left: 5px solid #f9a825; padding: 10px 16px; margin: 8px 0; border-radius: a4px">
💡 <strong>Getting exact reference coordinates:</strong> Extract from the SNX file:<br>
<code>grep "HKWS\|ZIM2" C:\PPP_PROJECT\products\snx\MIT0OPSSNX_2026015_SOL.SNX</code><br>
Or from IGS station page: https://network.igs.org/
</div>

### Expected Accuracy by Tool and Mode

| Tool          | Mode                  | GNSS        | Convergence | Final 3D RMS | Notes                   |
| ------------- | --------------------- | ----------- | ----------- | ------------ | ----------------------- |
| **RTKLIB**    | PPP-Static, Broadcast | GPS         | N/A (SPP)   | 1–5 m        | Broadcast only, no PPP  |
| **RTKLIB**    | PPP-Static, Precise   | GPS         | 25–40 min   | 5–15 cm      | Float PPP               |
| **RTKLIB**    | PPP-Static, Precise   | GPS+GAL+BDS | 15–25 min   | 3–10 cm      | Float multi-GNSS        |
| **RTKLIB-EX** | PPP-Static + AR       | GPS         | 15–25 min   | 3–8 cm       | Ambiguity resolution    |
| **RTKLIB-EX** | PPP-Static + AR       | GPS+GAL+BDS | 8–15 min    | 1–5 cm       | Best RTKLIB-EX result   |
| **GAMP**      | PPP-Static, IF        | GPS         | 20–35 min   | 5–12 cm      | ionoopt=2 (IF12)        |
| **GAMP**      | PPP-Static, UC12      | GPS+GAL+BDS | 8–15 min    | 2–6 cm       | ionoopt=4 (best)        |
| **PRIDE**     | PPP-AR (float)        | GPS         | 20–35 min   | 5–15 cm      | `-float` flag           |
| **PRIDE**     | PPP-AR (fixed)        | GPS         | 5–15 min    | **1–4 cm**   | Integer fixed           |
| **PRIDE**     | PPP-AR (fixed)        | GPS+GAL+BDS | **2–8 min** | **1–3 cm**   | **Best result overall** |

### Understanding Your GAMP Output File

GAMP creates `result/<stationname>.pos` with these columns:

```
%GPST         X(m)         Y(m)         Z(m)  Q  Ns  sdN(m) sdE(m) sdU(m) ...
2026/01/15 00:00:00.000  -2414262.xxx  5386840.xxx  2404337.xxx  2  12  0.31  0.28  0.55 ...
```

- **Q=5** → SPP (broadcast)
- **Q=2** → Float PPP
- **Q=1** → Fixed PPP (not produced by GAMP — PRIDE produces this)
- **sdN, sdE, sdU** → formal uncertainties. As convergence progresses, these shrink.

### Understanding Your RTKLIB .pos Output File

```
%  GPST          latitude(deg) longitude(deg) height(m)   Q  ns   sdn(m)    sde(m)    sdu(m) ...
2026/01/15 00:00:00.000   22.29xxxx   114.1xxxx   71.xxx   5   8   2.3456    1.2345    3.4567 ...
```

- **Q=5** → SPP (single point, broadcast)
- **Q=2** → DGPS (differential — not relevant for PPP)
- **Q=5 persisting** → PPP not converging — check that SP3+CLK are loaded correctly

### Understanding PRIDE kin\_ Output

```
%  MJD           SOD      x-ECEF(m)      y-ECEF(m)      z-ECEF(m)  Sig_x  Sig_y  Sig_z  Ns  PDOP  Fix
2026/01/15  0.000  -2414262.xxx  5386840.xxx  2404337.xxx  0.312  0.281  0.553  12  1.8   0
2026/01/15  30.000 -2414262.xxx  5386840.xxx  2404337.xxx  0.045  0.039  0.089  12  1.7   1
```

- **Fix=0** → Float phase (still converging)
- **Fix=1** → Ambiguity fixed! Watch the σ values drop sharply when Fix becomes 1.
- Convergence = when Fix stays 1 for 5+ consecutive epochs

### What to Plot in Your Report

1. **Position error vs. time** — shows convergence curve (tool comparison)
2. **σ (sigma) vs. time** — formal uncertainty, shows when tool "thinks" it converged
3. **Ambiguity fix rate** — fraction of epochs with Fix=1 (PRIDE only)
4. **PDOP vs. time** — satellite geometry (explains spikes in error)
5. **Residuals histogram** — should be normally distributed; outliers show multipath

### GAMP vs. PRIDE Final Accuracy Comparison Table (Typical for your stations)

| Metric               | GAMP (navsys=45)  | PRIDE PPP-AR   | Winner |
| -------------------- | ----------------- | -------------- | ------ |
| 3D RMS after 1 hour  | 3–8 cm            | 1–4 cm         | PRIDE  |
| 3D RMS after 6 hours | 2–4 cm            | 1–2 cm         | PRIDE  |
| Convergence time     | 10–20 min         | 2–8 min        | PRIDE  |
| Ease of setup        | Easy (one folder) | Moderate (WSL) | GAMP   |
| Multi-GNSS support   | Excellent         | Excellent      | Tie    |
| Troposphere output   | Yes               | Yes            | Tie    |
| Ambiguity resolution | No                | Yes            | PRIDE  |

</div>

---

<div style="border-left: 5px solid #e53e3e; background: #fff5f5; padding: 1px 20px; margin: 10px 0">

## APPENDIX C — Quick Command Reference 🔴

### GAMP — Recommended Workflow (Wizard)

```cmd
cd C:\PPP_PROJECT
python scripts/run_gamp.py
```

The wizard guides you through:

- Selecting obs file from `data/`
- Choosing scenario A/B/C/D with descriptions
- Auto-matching products from `products/` for the correct date
- Creating an isolated run folder: `GAMP_work/runs/<station>_<scenario>_<timestamp>/`
- Running GAMP and reporting results

Each run is **self-contained and preserved** in its own folder.

### GAMP — Manual Run (if needed)

```cmd
set GAMP="C:\Program Files (x86)\GAMP\GAMP\bin\Windows\gamp.exe"
set WD=C:\PPP_PROJECT\GAMP_work\2026015

%GAMP% "%WD%\gamp_A_broadcast.cfg"
%GAMP% "%WD%\gamp_B_GPS_IF.cfg"
%GAMP% "%WD%\gamp_C_multiGNSS_UC.cfg"
%GAMP% "%WD%\gamp_D_multiGNSS_GIM.cfg"
```

### GAMP — Visualize Results

```cmd
cd C:\PPP_PROJECT

rem ENU convergence (default):
python scripts/plot_gamp_enu.py GAMP_work/runs/<run>/result/<station>.pos

rem All plot types at once (for report):
python scripts/plot_gamp_enu.py --all --no-show GAMP_work/runs/<run>/result/<station>.pos

rem Scenario comparison bar chart:
python scripts/plot_gamp_enu.py --summary --no-show ^
  GAMP_work/runs/HKWS_A_*/result/*.pos ^
  GAMP_work/runs/HKWS_C_*/result/*.pos

rem Convert to rtkplot format:
python scripts/gamp2rtkplot.py GAMP_work/runs/<run>/result/<station>.pos
python scripts/gamp2rtkplot.py --open GAMP_work/result/HKWS00HKG_R_20260150000_01D_30S_MO.pos

rem --- Option C: MATLAB (if available) ---
rem cd to GAMP_work, then in MATLAB:
rem   addpath('C:\Program Files (x86)\GAMP\GAMP\Tools\MatPlot')
rem   Plot_PPP_result('result/HKWS00HKG_R_20260150000_01D_30S_MO')
```

### GAMP — rtkplot after conversion

```
Open: C:\Program Files\RTKLIB\bin\rtkplot.exe
  File → Open Solution 1 → result\HKWS00HKG_R_20260150000_01D_30S_MO.pos.rtklib.pos
  Plot Type: "Position"   (shows ENU errors in sdn/sde/sdu)
  For comparison: File → Open Solution 2 → ZIM2 or reference file
```

### RTKLIB rtkpost (Windows GUI — no command line needed)

Just double-click `C:\Program Files\RTKLIB\bin\rtkpost.exe`

### RTKLIB-EX rtkpost (Windows GUI)

Double-click `C:\Program Files\RTKLIB_EX_2.5.0\rtkpost.exe`

### PRIDE PPP-AR (WSL terminal)

```bash
# One-time setup per WSL session:
ln -sfn "/mnt/c/Program Files (x86)/PRIDE-PPPAR-master" /tmp/pride
export PATH="/tmp/pride/bin:/tmp/pride/scripts:$PATH"

# Create config:
cat > /tmp/pride_config.cfg << 'EOF'
Table directory = /tmp/pride/table
Product directory = Default
ZTD model = STO
Tides = SOLID OCEAN POLE
EOF

# Run for HKWS (static, multi-GNSS, PPP-AR):
cd /mnt/c/PPP_PROJECT/PRIDE_work
pdp3 -m S -sys gec --config /tmp/pride_config.cfg \
  /mnt/c/PPP_PROJECT/data/HKWS00HKG_R_20260150000_01D_30S_MO.rnx

# Run for ZIM2:
pdp3 -m S -sys gec --config /tmp/pride_config.cfg \
  /mnt/c/PPP_PROJECT/data/ZIM200CHE_R_20260150000_01D_30S_MO.rnx

# Float PPP (no AR) for comparison:
pdp3 -m S -float -sys gec --config /tmp/pride_config.cfg \
  /mnt/c/PPP_PROJECT/data/HKWS00HKG_R_20260150000_01D_30S_MO.rnx
```

### PRIDE — Visualize Results

PRIDE's `kin_` files contain lat/lon/height per epoch. Use the Python script to plot and convert:

```bash
# From WSL (run from the directory where kin_ files are created, e.g. PRIDE_work):
cd /mnt/c/PPP_PROJECT/PRIDE_work

# Plot single kin_ file (ENU convergence):
python /mnt/c/PPP_PROJECT/scripts/plot_pride_enu.py  kin_20260150000_hkws

# Compare float vs AR fixed:
python /mnt/c/PPP_PROJECT/scripts/plot_pride_enu.py --compare \
  kin_20260150000_hkws_float  kin_20260150000_hkws

# Print static pos_ result (final position + accuracy):
python /mnt/c/PPP_PROJECT/scripts/plot_pride_enu.py --pos  pos_20260150000_hkws

# Convert to rtkplot format (creates kin_20260150000_hkws.rtklib.pos):
python /mnt/c/PPP_PROJECT/scripts/plot_pride_enu.py --convert-only  kin_20260150000_hkws
```

```cmd
rem From Windows CMD:
cd C:\PPP_PROJECT\PRIDE_work
python C:\PPP_PROJECT\scripts\plot_pride_enu.py  kin_20260150000_hkws

rem Then open in rtkplot:
rem   File → Open Solution 1 → kin_20260150000_hkws.rtklib.pos
rem   Plot Type → "Position"
```

### Python Download Script

```cmd
cd C:\PPP_PROJECT
# Multi-GNSS products for Jan 15, 2026
python download_ppp_data.py --stations HKWS ZIM2 --date 2026 15
# Observations only
python download_ppp_data.py --stations HKWS ZIM2 --date 2026 15 --obs-only
```

### PRIDE Test (run download_test_products.sh first!)

```bash
# In WSL:
cd "/mnt/c/Program Files (x86)/PRIDE-PPPAR-master/example"
bash download_test_products.sh    # pre-download products (run once)
bash test.sh                      # should now complete all 6 tests
```

</div>
