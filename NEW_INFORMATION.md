# ⚡ PPP Project Setup - New Information & Status Files

## NEW (Updated May 2026)

### MGEX Status Files - Understanding Station Data Quality

Two status files provide complete information about every IGS/MGEX station:

| File               | Content            | Constellations                  |
| ------------------ | ------------------ | ------------------------------- |
| **26015.V2status** | GPS + GLONASS only | G, R (2 satellites systems)     |
| **26015.V3status** | Multi-GNSS full    | G, R, E, C, J, S, I (7 systems) |

**Why two files?**

- **V2** = Older RINEX v2 format (GPS + GLONASS), smaller files, fewer constellations
- **V3** = Modern RINEX v3 format (all constellations), larger files, richer data

---

### 🔍 Understanding Station Entries

Example from V2 status:

```
Mon. Full Mon. RNX  Dly  Dly                                              Mkr. Marker        Obs. Types
ID     ID      Ver. (H)  (M)  V    Receiver Type         Antenna Type     Name Number    Typ G R E C J S I
BJFS BJFS00CHN 3.04  56    43 9 SEPT POLARX5         TRM59800.99     SCIT BJFS 41813M013  M  X X
```

**Column Explanations:**

| Column        | Example      | Meaning                                           |
| ------------- | ------------ | ------------------------------------------------- |
| **Mon. ID**   | BJFS         | 4-letter station code                             |
| **Full ID**   | BJFS00CHN    | Full 9-char identifier (code + country)           |
| **RNX Ver**   | 3.04         | RINEX file version                                |
| **Dly (H)**   | 56           | Daily file count (hours submitted)                |
| **Dly (M)**   | 43           | Minute data samples                               |
| **V flag**    | 9            | Quality: 0=excellent, 1=good, 9=real-time         |
| **Receiver**  | SEPT POLARX5 | Receiver model (top-tier = Septentrio PolaRx5)    |
| **Antenna**   | TRM59800.99  | Antenna model (Trimble choke-ring = high quality) |
| **Obs Types** | X X          | Each X = constellation tracked (G R E C J S I)    |

---

### 📏 Why BJFS File Is Smaller Than Others

**BJFS (Beijing Fangshan):**

- **V2 File Only** — GPS + GLONASS (G, R)
- **Does NOT track** Galileo, BeiDou, QZSS, SBAS, NavIC (E, C, J, S, I all blank)
- **File size**: ~15 MB for 24h (only 2 constellations)

**GOLD (Goldstone, USA):**

- **V3 File** — GPS + GLONASS + Galileo (G, R, E)
- **Does NOT track** BeiDou (out of coverage in California)
- **File size**: ~25 MB for 24h (3 constellations)

**Why?** More satellites = more observations per epoch = larger file.

**For your research:**
| Task | Best Station |
|------|---|
| GPS-only baseline | BJFS or GOLD (both track GPS) |
| GPS vs GPS+GLO | Use BJFS (V2) |
| GPS vs GPS+Gal | Use GOLD (V3) |
| GPS vs GPS+GLO+Gal | Use GOLD (V3) |
| 4-constellation (GPS+GLO+Gal+BDS) | ❌ Can't use USA stations - need China station |

---

### ✅ Checking Your Downloaded Files

After downloading, verify file quality:

```bash
# 1. Check file size (should be 15-30 MB for 24h multi-GNSS)
ls -lh C:\PPP_PROJECT\data\BJFS*.rnx

# 2. Count epochs (should be ~2880 for 24h @ 30s sampling)
gunzip -c BJFS*.rnx.gz | grep "^> " | wc -l

# 3. Verify constellations in file
gunzip -c BJFS*.rnx.gz | grep "SYS / # / OBS TYPES"

# Expected output for BJFS:
# G  3 C1C L1C D1C
# R  3 C4A L4A D4A
# (Only GPS + GLONASS lines)

# Expected output for GOLD:
# G  3 C1C L1C D1C
# R  3 C4A L4A D4A
# E  3 C1X L1X D1X
# (GPS + GLONASS + Galileo)
```

---

### 🛠️ Tool-Specific Product Requirements

| Product          | RTKLIB            | GAMP           | PRIDE                        | DEMO5             |
| ---------------- | ----------------- | -------------- | ---------------------------- | ----------------- |
| Obs (.rnx)       | **✓ Required**    | **✓ Required** | **✓ Required**               | **✓ Required**    |
| Nav (.rnx nav)   | **✓ Required**    | **✓ Required** | auto-downloaded              | **✓ Required**    |
| SP3 orbit        | Optional          | Via config     | auto-downloaded              | Optional          |
| CLK clock        | Optional          | Via config     | auto-downloaded              | Optional          |
| ERP              | Optional          | Via config     | **✓ Required**               | Optional          |
| DCB/BSX          | Optional          | Via config     | auto-downloaded              | N/A               |
| Ionex            | Optional          | Via config     | N/A                          | N/A               |
| ATX antenna      | **✓ Recommended** | Via config     | **✓ Required**               | **✓ Recommended** |
| SNX coords       | Optional          | Via config     | auto-downloaded              | Optional          |
| BIA (phase bias) | N/A               | N/A            | **✓ Required (PPP-AR only)** | N/A               |

---

### 🎯 RTKLIB vs RTKLIB-demo

**Both use the same Windows executables in:** `C:\Program Files\RTKLIB\bin\`

| Feature         | RTKLIB                       | RTKLIB-demo                       |
| --------------- | ---------------------------- | --------------------------------- |
| **Source**      | Classic open-source          | Community-enhanced fork           |
| **Best For**    | Standard PPP, RTK, PPK       | Low-cost receivers, dual-freq PPP |
| **Receiver**    | Any GNSS                     | u-blox optimized                  |
| **Algorithm**   | Standard Kalman filter       | Improved ambiguity resolution     |
| **GUI Apps**    | `rtkpost.exe`, `rtkplot.exe` | Same binaries                     |
| **Run Command** | Double-click .exe            | Same                              |

**Bottom line:** Use RTKLIB demo5 source code but run the GUI apps from `bin\` folder.

---

### 🚀 Running RTKLIB in Two Ways

#### Option A: GUI Mode (Easiest - Recommended for Learning)

```cmd
# Double-click these executables
C:\Program Files\RTKLIB\bin\rtkpost.exe      # Processing engine
C:\Program Files\RTKLIB\bin\rtkplot.exe      # Plotting results
```

**Steps:**

1. Open RTKPOST
2. Select observation file
3. Select nav file
4. Click Options → PPP-Static
5. Click Execute
6. Open RTKPLOT and view results

#### Option B: Command-Line Mode (For Batch Processing)

```cmd
cd "C:\Program Files\RTKLIB\bin"

# PPP with broadcast ephemeris
rnx2rtkp -m 7 -sys 1 -ionoopt 2 -x 1000000 -o output.pos input.rnx brdc_nav.rnx

# PPP with precise products
rnx2rtkp -m 7 -sys 1 -ionoopt 2 -sp3 precise.sp3 -clk precise.clk -x 1000000 input.rnx nav.rnx
```

**Parameters:**

- `-m 7` = PPP static mode
- `-sys 1` = GPS only (change to 5 for GPS+GLONASS)
- `-ionoopt 2` = Ionosphere-Free combination
- `-sp3 file.sp3` = Precise orbit
- `-clk file.clk` = Precise clock
- `-x 1000000` = Output lat/lon coordinates (instead of XYZ)

---

### 📊 GAMP Settings for Your Research

Complete config for all 4 scenarios:

**Scenario 1: GPS-only + Broadcast**

```cfg
posmode    = 7          # Static
navsys     = 1          # GPS only
ionoopt    = 1          # Broadcast ionosphere
# Leave sp3/clk files empty or commented
```

**Expected:** 2-5 m accuracy, 40-60 min convergence

**Scenario 2: GPS-only + Precise**

```cfg
posmode    = 7
navsys     = 1
ionoopt    = 2          # Ionosphere-Free dual-freq
sp3 file   = path/to/igs_sp3.sp3
clk file   = path/to/igs_clk.clk
```

**Expected:** 2-5 cm accuracy, 20-30 min convergence

**Scenario 3: Multi-GNSS (GPS+Gal+BDS)**

```cfg
posmode    = 7
navsys     = 41         # GPS(1) + Galileo(8) + BeiDou(32)
ionoopt    = 4          # Uncombined dual-frequency
sp3 file   = path/to/wum_sp3.sp3     # Wuhan multi-GNSS
clk file   = path/to/wum_clk.clk
dcb p1p2   = path/to/CAS_DCB.BSX     # Multi-GNSS biases
```

**Expected:** 1-2 cm accuracy, 8-12 min convergence

**Scenario 4: PPP-AR (PRIDE)**

```bash
# CLI mode (no config needed)
pdp3 -m S observation.rnx            # Auto-downloads all products
pdp3 -m S -sys gec observation.rnx   # Multi-constellation
```

**Expected:** 0.5-1 cm accuracy, 2-5 min convergence (after AR)

---

### 📁 Complete Folder Structure (New)

Run this once to set up:

```bash
cd C:\PPP_PROJECT
python create_project_structure.bat
```

**Result:**

```
C:\PPP_PROJECT\
├── data\                          ← Download .rnx observation files here
├── products\
│   ├── status\                    ← Download 26015.V2status, 26015.V3status
│   ├── sp3\                       ← Precise orbits (.sp3)
│   ├── clk\                       ← Precise clocks (.clk)
│   ├── erp\                       ← Earth rotation parameters (.erp)
│   ├── dcb\                       ← Code biases (.DCB, .BSX)
│   ├── bia\                       ← Phase biases for PPP-AR (.BIA)
│   ├── ionex\                     ← Ionosphere maps (.rnx iono)
│   ├── atx\                       ← Antenna corrections (igs20.atx)
│   └── snx\                       ← Station coords (.snx)
├── GAMP_work\                     ← Copy gamp.cfg and run gamp.exe here
├── PRIDE_work\                    ← Run pdp3 commands here
├── RTKLIB_work\                   ← Output from rtkpost.exe
├── results\                       ← Final comparison analysis
├── station_reports\               ← Markdown reports from check_station.py
├── config\                        ← Configuration files
├── create_project_structure.bat   ← Run ONCE to create all folders
├── download_ppp_data.py           ← Download all products automatically
├── check_station.py               ← Check station data quality
└── scripts\                       ← Helper scripts
```

---

### 📥 How to Download Products

**Automatic (Recommended):**

```bash
cd C:\PPP_PROJECT

# Default (BJFS, GOLD, 2026-01-15)
python download_ppp_data.py

# Custom date
python download_ppp_data.py --date 2025 250

# Custom stations
python download_ppp_data.py --stations ABMF JFNG BJFS

# Download all products
python download_ppp_data.py --stations BJFS GOLD --date 2026 15

# Or specific products only
python download_ppp_data.py --obs-only  # Just observation files
```

**What it downloads:**

- ✓ Observation files (RINEX .rnx)
- ✓ Broadcast navigation (.rnx nav)
- ✓ IGS precise products (sp3, clk, erp)
- ✓ Wuhan multi-GNSS (better for GPS+Gal+BDS)
- ✓ Code biases (DCB, BSX)
- ✓ Ionosphere map (IONEX)
- ✓ Antenna file (igs20.atx)
- ✓ Station coordinates (SNX)

**Requires:**

```bash
pip install requests python-dotenv tqdm
```

**.env file (create in same folder):**

```
EARTHDATA_USERNAME=your_username
EARTHDATA_PASSWORD=your_password
```

Get free Earthdata account: https://urs.earthdata.nasa.gov/

---

### 🔍 Station Quality Checking

**Check your downloaded station:**

```bash
python check_station.py BJFS

# Output: markdown report with:
#   - Constellation support (V2 vs V3)
#   - Receiver/antenna quality
#   - File size and epoch count
#   - PPP suitability
#   - Convergence expectations
#   - Tool-specific recommendations
```

**Interpreting the report:**

| V Flag | Quality   | Status              |
| ------ | --------- | ------------------- |
| 0      | Excellent | ✅ Use for research |
| 1      | Good      | ✅ Use for research |
| 9      | Real-time | ✅ Use for research |
| 2-4    | Degraded  | ⚠️ Verify results   |

---

### 📊 Expected Results Table

For January 15, 2026 (BJFS static PPP):

| Tool   | Mode       | Ephemeris | Constellations | Convergence | Final Accuracy |
| ------ | ---------- | --------- | -------------- | ----------- | -------------- |
| RTKLIB | PPP-Static | Broadcast | GPS            | 45 min      | 2-5 m          |
| RTKLIB | PPP-Static | Precise   | GPS            | 25 min      | 2-5 cm         |
| GAMP   | PPP-Static | Broadcast | G              | 40 min      | 1-3 m          |
| GAMP   | PPP-Static | Precise   | G              | 20 min      | 1-3 cm         |
| GAMP   | PPP-Static | Precise   | G+R+E+C        | 8 min       | 0.5-1 cm       |
| PRIDE  | PPP-AR     | Precise   | G              | 3 min       | 0.5 cm (fixed) |
| PRIDE  | PPP-AR     | Precise   | G+R+E+C        | 2 min       | 0.3 cm (fixed) |

---

### ⚠️ Troubleshooting

**Problem:** Downloaded file is very small (~500 KB)

- **Reason:** Station only tracks 2 constellations (e.g., GPS+GLONASS only)
- **Solution:** Check V2 status file; use multi-constellation station like GOLD

**Problem:** GAMP exits immediately

- **Check:** Do sp3/clk files exist and are named correctly in config?
- **Check:** Is observation file path correct?
- **Check:** Do files cover the same date?

**Problem:** Convergence takes longer than expected

- **Check:** Is elevation mask set appropriately (7-15 degrees)?
- **Check:** Are you using broadcast nav instead of precise?
- **Hint:** Add more constellations (GPS+GLONASS faster than GPS-only)

**Problem:** Position jumps around after convergence

- **Reason:** Cycle slips on low-elevation satellites
- **Solution:** Increase elevation mask from 7° to 15°

---

## 🎓 Research Application

Use these tools and status files to answer your team's questions:

1. **Error correction impact** → Compare broadcast vs precise products in GAMP
2. **Multi-GNSS benefit** → Use GOLD with navsys=1 vs navsys=13 vs navsys=41
3. **Convergence analysis** → Plot position error vs time for each scenario
4. **Data quality check** → Use check_station.py to verify file completeness
5. **PPP-AR advantage** → Compare PRIDE float vs fixed solutions

---

_Updated: May 2026_
_Tools: RTKLIB, GAMP v2, PRIDE PPP-AR v3.2+_
_Data: IGS/MGEX/CDDIS + Wuhan University (WUM)_
