# Complete End-to-End Guide: PPP with RTKLIB, GAMP, and PRIDE PPP-AR

### For Your Research Project on Precise Point Positioning (PPP)

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

### Tool 2: RTKLIB-demo (enhanced version — `C:\Program Files\RTKLIB-demo`)

**What it is:** A community-improved fork of RTKLIB, optimized especially for
low-cost u-blox receivers. Same GUI apps, but with better algorithms for PPP.
The actual binary executables you run are in `C:\Program Files\RTKLIB\bin\`
(both RTKLIB and RTKLIB-demo install to the same bin folder).

---

### Tool 3: GAMP (the multi-constellation champion — `C:\Program Files (x86)\GAMP\GAMP`)

**What it is:** GNSS Analysis software for Multi-constellation and multi-frequency
Precise Positioning. Developed by Chinese researchers. It's a **command-line** tool
(no graphical interface). You edit a config file, run it, and get results.

**Why use it for your research?** It handles GPS + GLONASS + Galileo + BeiDou better
than basic RTKLIB and lets you easily switch which constellations to use.

**Executable:** `C:\Program Files (x86)\GAMP\GAMP\bin\Windows\gamp.exe`

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

## PART 5 — STEP-BY-STEP: Using GAMP

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
PPP with Ambiguity Resolution (PPP-AR). It uses special Phase Bias products
from Wuhan University that allow the software to resolve the integer ambiguities —
the "blurry photo" problem mentioned earlier — dramatically improving both
convergence time and accuracy.

PRIDE is a Linux/macOS shell script that calls a series of programs in sequence.
On Windows, you need **Windows Subsystem for Linux (WSL)** to run it.

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

# Build the software
make

# Install (copies executables to ~/.local/bin or /usr/local/bin)
# Check Makefile for install target:
make install
```

After compilation, you should have programs like: `lsq`, `tedit`, `spp`, `redig`, `arsig`
These are the processing pipeline stages that `pdp3` calls automatically.

---

### Step 3 — Run the Built-in Test Example

```bash
cd "/mnt/c/Program Files (x86)/PRIDE-PPPAR-master/example"

# Run the test script
bash test.sh
```

This will:

1. Download necessary products from the internet automatically
2. Process the included observation file `abmf0010.20o`
3. Output results to `results/`

If successful, compare your results folder with `results_ref/`.

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

### Step 5 — Download Files Automatically with pdp3

One of PRIDE's best features: it can **download all needed products automatically**
just by knowing your observation date!

```bash
# Run static PPP-AR with all products downloaded automatically
pdp3 -m S /path/to/your/abmf0010.20o
```

When this runs, pdp3 will:

1. Read the date from the observation file
2. Download the sp3, clk, erp, bias files from `ftps://bdspride.com/wum/`
3. Find the antenna correction file in the `table/` folder
4. Process and output results

**Results will be in:** a folder named `YYYY/DDD/` in your current directory.

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

For your research, run `pdp3` four times on the SAME observation file:

```bash
# Run 1: Float PPP, GPS only
pdp3 -m S -float -sys g ./data/2020/001/abmf0010.20o
mv 2020/001 ./results/float_GPS

# Run 2: PPP-AR, GPS only
pdp3 -m S -sys g ./data/2020/001/abmf0010.20o
mv 2020/001 ./results/PPPAR_GPS

# Run 3: PPP-AR, GPS + Galileo
pdp3 -m S -sys ge ./data/2020/001/abmf0010.20o
mv 2020/001 ./results/PPPAR_GE

# Run 4: PPP-AR, GPS + Galileo + BeiDou
pdp3 -m S -sys gec ./data/2020/001/abmf0010.20o
mv 2020/001 ./results/PPPAR_GEC
```

The `kin_YYYYDDD_abmf` output file in each folder contains your position time series.
Compare the convergence curves. You should see PPP-AR converge MUCH faster.

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

### Using RTKPLOT to Compare

RTKPLOT can read:

- RTKLIB/GAMP `.pos` files directly
- PRIDE `kin_` files (after renaming or minor format adjustment)

To compare convergence:

1. Open RTKPLOT
2. File → Open Solution → hold Ctrl and select multiple `.pos` files
3. View → Plot Type → Position → you'll see all runs overlaid
4. The plot Y-axis shows position error; X-axis shows time
5. Watch how quickly each scenario's error drops below ~10 cm

---

## PART 9 — Understanding Your Results (PPP Theory Summary)

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

| Task                                     | Best Tool                    |
| ---------------------------------------- | ---------------------------- |
| Learning PPP basics with GUI             | RTKLIB / RTKPOST             |
| Comparing broadcast vs. precise products | GAMP (easy config switching) |
| GPS-only vs. multi-GNSS comparison       | GAMP (`navsys` parameter)    |
| Fastest convergence / PPP-AR             | PRIDE PPP-AR                 |
| Visualizing results                      | RTKPLOT                      |
| Downloading IGS products                 | RTKGET (GUI)                 |
| Batch processing many stations           | GAMP or PRIDE                |

---

## PART 12 — Your Research Proposal: Recommended Experiments

Based on your discussion with your team, here are the concrete experiments to run:

### Experiment 1: Broadcast vs. Precise Products

- Tool: GAMP
- Settings: `posmode=7`, `navsys=1`, vary `sp3/clk` files
- Measure: Final position accuracy (RMS of last 2 hours of data)

### Experiment 2: GPS-only vs. Multi-GNSS

- Tool: GAMP
- Settings: Same precise products; vary `navsys=1` vs `navsys=45`
- Measure: Convergence time (time to reach 10 cm accuracy)

### Experiment 3: Error Correction Method Comparison

- Tool: GAMP
- Settings: Vary `ionoopt`: 2 (IF) vs 4 (UC12) vs 5 (with IONEX GIM)
- Measure: Position accuracy and convergence behavior

### Experiment 4: Session Length for Convergence

- Tool: RTKLIB or GAMP
- Settings: Process 24h data; take 1h, 2h, 4h, 8h, 24h subsets
- Measure: Accuracy as function of session length

### Experiment 5: Float PPP vs. PPP-AR

- Tool: PRIDE PPP-AR
- Settings: `-float` vs default (AR enabled)
- Measure: Convergence time, final accuracy, ambiguity fixing rate

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

_Guide prepared for PPP research project. Tools: RTKLIB demo5, GAMP v2, PRIDE PPP-AR v3.2_
_Data sources: IGS/CDDIS, Wuhan University (WUM), CODE, CAS_
