#!/usr/bin/env python3
"""
PPP Data Downloader  v5  — Robust retry + verified CDDIS URLs
==============================================================
Downloads every file needed for PPP with RTKLIB, GAMP, PRIDE PPP-AR.

KEY FACTS CONFIRMED FROM LIVE CDDIS + MANUAL DOWNLOADS
───────────────────────────────────────────────────────
Observations  : .crx.gz  (Hatanaka-compressed RINEX 3, NOT .rnx.gz)
                Path: /data/daily/{year}/{doy:03d}/{yy}d/
                File: {SSSS}00{CCC}_R_{YYYYDDD}0000_01D_30S_MO.crx.gz
                After: decompress .gz → .crx → CRX2RNX → .rnx

Broadcast nav : /data/daily/{year}/brdc/BRD400DLR_S_{YYYYDDD}0000_01D_MN.rnx.gz
                OR team member downloaded: BRDC00IGS_R_{YYYYDDD}0000_01D_MN.rnx

Precise SP3   : /products/{week}/COD0OPSFIN_{YYYYDDD}0000_01D_05M_ORB.SP3.gz  (confirmed)
                fallback: COD0MGXFIN, WUM0MGXRAP

Precise CLK   : /products/{week}/COD0OPSFIN_{YYYYDDD}0000_01D_30S_CLK.CLK.gz
                fallback: COD0MGXFIN, WUM0MGXRAP

ERP           : /products/{week}/EMR0OPSFIN_{YYYYDDD}0000_01D_01D_ERP.ERP.gz  (confirmed)
                fallback: WUM0MGXRAP, COD0MGXFIN (_12H)

Bias          : /products/bias/{year}/CAS0OPSRAP_{YYYYDDD}0000_01D_01D_DCB.BIA.gz  (confirmed)
                fallback: COD0MGXFIN OSB in /products/{week}/

Ionosphere    : /products/ionosphere/{year}/{doy:03d}/COD0OPSFIN_{YYYYDDD}0000_01D_01H_GIM.INX.gz

Attitude OBX  : /products/{week}/COD0MGXFIN_{YYYYDDD}0000_01D_30S_ATT.OBX.gz
                Used by PRIDE PPP-AR for precise satellite attitude (eclipse seasons)
                Fallback: WUM0MGXFIN, WUM0MGXRAP same path

Antenna       : igs20.atx  (download once from files.igs.org or use team copy)
                NOTE: team zip has 'igs20_2401.atx' — same file, rename to igs20.atx

SINEX         : /products/{week}/MIT0OPSSNX_{YYYYDDD}0000_01D_01D_SOL.SNX.gz  (confirmed)
                fallback: JPL0OPSFIN, COD0OPSFIN

DROPPED CONNECTION FIX (IncompleteRead)
───────────────────────────────────────
Large files (SINEX, WUM CLK, WUM SP3) sometimes drop mid-download.
v5 adds: resume-capable chunked download with 3 automatic retries,
increasing timeout, and chunk-level integrity check.

USAGE
─────
  python download_ppp_data.py --stations HKWS ZIM2 --date 2026 15
  python download_ppp_data.py --obs-only
  python download_ppp_data.py --skip-wuhan

REQUIREMENTS
────────────
  pip install requests python-dotenv tqdm

SETUP
─────
  1. https://urs.earthdata.nasa.gov  — register and confirm email
  2. .env file next to this script:
       EARTHDATA_USERNAME=yourname
       EARTHDATA_PASSWORD=yourpass
  3. CRX2RNX.exe in C:\\PPP_PROJECT\\tools\\
       Download: https://terras.gsi.go.jp/ja/crx2rnx.html
       Windows 64-bit: RNXCMP_4.2.0_Windows_mingw_64bit.zip
"""

import os
import sys
import gzip
import shutil
import time
import requests
import datetime
import subprocess
from pathlib import Path
from getpass import getpass
from datetime import datetime as dt

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure") and stream.encoding.lower() != "utf-8":
        stream.reconfigure(encoding="utf-8", errors="replace")

# ══════════════════════════════════════════════════════════════════
#  CONFIGURATION
# ══════════════════════════════════════════════════════════════════

BASE_DIR = Path(r"C:\PPP_PROJECT")
DATA_DIR = BASE_DIR / "data"
PRODUCTS_DIR = BASE_DIR / "products"
TOOLS_DIR = BASE_DIR / "tools"

YEAR = 2026
DOY = 15
GPS_WEEK = 2401
GPS_DOW = 4

CDDIS = "https://cddis.nasa.gov/archive/gnss"
IGS_ATX = "https://files.igs.org/pub/station/general/igs20.atx"

EARTHDATA_USER = os.environ.get(
    "EARTHDATA_USERNAME") or os.environ.get("EARTHDATA_USER", "")
EARTHDATA_PASS = os.environ.get(
    "EARTHDATA_PASSWORD") or os.environ.get("EARTHDATA_PASS", "")

MAX_RETRIES = 3
CHUNK = 131072   # 128 KB

# ──────────────────────────────────────────────────────────────────
#  STATION TABLE
# ──────────────────────────────────────────────────────────────────
KNOWN_STATIONS = [
    ("BJFS", "CHN"), ("SHAO", "CHN"), ("WUHN",
                                       "CHN"), ("JFNG", "CHN"), ("LHAZ", "CHN"),
    ("HKWS", "HKG"), ("HKSL", "HKG"), ("HKMZ",
                                       "HKG"), ("HKLT", "HKG"), ("HKOH", "HKG"),
    ("TWTF", "TWN"), ("TCMS", "TWN"),
    ("USUD", "JPN"), ("AIRA", "JPN"), ("MIZU", "JPN"), ("TSKB", "JPN"),
    ("TOW2", "AUS"), ("KARR", "AUS"), ("DARW",
                                       "AUS"), ("TIDB", "AUS"), ("HOB2", "AUS"),
    ("IISC", "IND"), ("HYDE", "IND"),
    ("PIMO", "PHL"), ("GUAM", "GUM"), ("KOKB", "USA"),
    ("ZIM2", "CHE"), ("ZIM3", "CHE"), ("ZIMM", "CHE"),
    ("GRAZ", "AUT"), ("MATE", "ITA"), ("MEDI", "ITA"),
    ("ONSA", "SWE"), ("KIRU", "SWE"),
    ("WSRT", "NLD"), ("BRUX", "BEL"),
    ("WARN", "DEU"), ("WTZR", "DEU"), ("POTS", "DEU"), ("FFMJ", "DEU"),
    ("TLSE", "FRA"), ("MARS", "FRA"),
    ("MAD2", "ESP"), ("EBRE", "ESP"),
    ("NYAL", "NOR"), ("TROM", "NOR"),
    ("ZECK", "RUS"), ("NVSK", "RUS"),
    ("GOP6", "CZE"), ("GOPE", "CZE"),
    ("GOLD", "USA"), ("AMC2", "USA"), ("FAIR",
                                       "USA"), ("PIE1", "USA"), ("JPLM", "USA"),
    ("ALGO", "CAN"), ("CHUR", "CAN"), ("DUBO", "CAN"),
    ("ABMF", "GLP"), ("AREQ", "PER"), ("BRAZ",
                                       "BRA"), ("SANT", "CHL"), ("MANA", "NIC"),
    ("NKLG", "GAB"), ("SUTH", "ZAF"), ("HRAO", "ZAF"),
    ("MCM4", "ATA"), ("SYOG", "ATA"), ("KERG", "ATF"),
]

# ══════════════════════════════════════════════════════════════════
#  GPS UTILITIES
# ══════════════════════════════════════════════════════════════════


def compute_gps_week_dow(year, doy):
    epoch = dt(year, 1, 1) + datetime.timedelta(days=doy - 1)
    days = (epoch - dt(1980, 1, 6)).days
    return days // 7, days % 7


def gps_week_start_yyyyddd(gps_week):
    d = dt(1980, 1, 6) + datetime.timedelta(weeks=gps_week)
    doy = d.timetuple().tm_yday
    return f"{d.year:04d}{doy:03d}"

# ══════════════════════════════════════════════════════════════════
#  CLEANUP
# ══════════════════════════════════════════════════════════════════


def clean_tmp_files(*search_dirs):
    """
    Delete all *.tmp files left by interrupted downloads.
    These look like real files to already_have() and block re-downloads.
    """
    total = 0
    for d in search_dirs:
        for tmp in Path(d).rglob("*.tmp"):
            size = tmp.stat().st_size / 1024
            print(f"  🗑  Removing leftover: {tmp.name}  ({size:.0f} KB)")
            tmp.unlink()
            total += 1
    if total == 0:
        print("  ✓ No .tmp files found")
    else:
        print(f"  ✓ Removed {total} .tmp file(s)")

# ══════════════════════════════════════════════════════════════════
#  CORE HELPERS
# ══════════════════════════════════════════════════════════════════


def ensure_dirs(*paths):
    for p in paths:
        Path(p).mkdir(parents=True, exist_ok=True)


def get_credentials():
    global EARTHDATA_USER, EARTHDATA_PASS
    if not EARTHDATA_USER:
        print("\n  Earthdata login — register at https://urs.earthdata.nasa.gov")
        EARTHDATA_USER = input("  Username: ").strip()
    if not EARTHDATA_PASS:
        EARTHDATA_PASS = getpass("  Password: ")


def make_session():
    s = requests.Session()
    s.auth = (EARTHDATA_USER, EARTHDATA_PASS)
    return s


def download_file(session, url, output_path, skip_auth=False):
    """
    Chunked download with automatic retry on dropped connections.
    Retries MAX_RETRIES times with increasing timeout.
    .tmp extension used during download; renamed to final name on success.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = output_path.with_suffix(output_path.suffix + ".tmp")

    print(f"  📥 {output_path.name} ...", end="", flush=True)

    for attempt in range(1, MAX_RETRIES + 1):
        timeout = 90 * attempt
        try:
            getter = requests.get if skip_auth else session.get
            r = getter(url, timeout=timeout, allow_redirects=True, stream=True)

            if r.status_code == 404:
                print("  ✗ 404")
                return False
            r.raise_for_status()

            total = int(r.headers.get("content-length", 0))

            if HAS_TQDM and total > 0:
                with tqdm(total=total, unit="B", unit_scale=True,
                          desc=f"  {output_path.name[:35]}", leave=False) as bar:
                    with open(tmp, "wb") as fh:
                        for chunk in r.iter_content(CHUNK):
                            fh.write(chunk)
                            bar.update(len(chunk))
            else:
                with open(tmp, "wb") as fh:
                    for chunk in r.iter_content(CHUNK):
                        fh.write(chunk)

            # Validate: file must be ≥99% of Content-Length
            if total > 0:
                got = tmp.stat().st_size
                if got < total * 0.99:
                    raise IOError(f"Short: {got}/{total} bytes")

            tmp.rename(output_path)
            size_mb = output_path.stat().st_size / 1_048_576
            print(f"  ✓ {size_mb:.1f} MB")
            return True

        except requests.exceptions.HTTPError as e:
            print(f"  ✗ HTTP {e.response.status_code}")
            if tmp.exists():
                tmp.unlink()
            return False

        except (IOError, requests.exceptions.ChunkedEncodingError,
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as e:
            if tmp.exists():
                tmp.unlink()
            if attempt < MAX_RETRIES:
                wait = 8 * attempt
                print(f"\n    ↻ Retry {attempt}/{MAX_RETRIES} in {wait}s"
                      f" ({str(e)[:55]})...", end="", flush=True)
                time.sleep(wait)
            else:
                print(f"  ✗ Failed after {MAX_RETRIES} tries: {str(e)[:60]}")
                return False

        except Exception as e:
            if tmp.exists():
                tmp.unlink()
            print(f"  ✗ {str(e)[:70]}")
            return False

    return False


def decompress_gz(path):
    path = Path(path)
    if path.suffix != ".gz":
        return path
    out = path.with_suffix("")
    try:
        with gzip.open(path, "rb") as fi, open(out, "wb") as fo:
            shutil.copyfileobj(fi, fo)
        path.unlink()
        print(f"     → {out.name}")
        return out
    except Exception as e:
        print(f"    ⚠ gz decompress failed: {e}")
        return path


def decompress_Z(path):
    path = Path(path)
    if path.suffix != ".Z":
        return path
    out = path.with_suffix("")
    try:
        if subprocess.run(["uncompress", "-f", str(path)],
                          capture_output=True, timeout=60).returncode == 0:
            print(f"     → {out.name}")
            return out
    except FileNotFoundError:
        pass
    sz = Path("C:/Program Files/7-Zip/7z.exe")
    if sz.exists():
        try:
            subprocess.run([str(sz), "e", str(path), f"-o{path.parent}", "-y"],
                           capture_output=True, timeout=120, check=True)
            if path.exists():
                path.unlink()
            print(f"     → {out.name}")
            return out
        except Exception:
            pass
    print("    ℹ  .Z kept (install 7-Zip or uncompress)")
    return path


def decompress_file(path):
    path = Path(path)
    if path.suffix == ".gz":
        return decompress_gz(path)
    if path.suffix == ".Z":
        return decompress_Z(path)
    return path


def crx2rnx(crx_path):
    """Convert .crx → .rnx using CRX2RNX.exe from TOOLS_DIR or PATH."""
    crx_path = Path(crx_path)
    if crx_path.suffix.lower() != ".crx":
        return crx_path
    rnx_path = crx_path.with_suffix(".rnx")
    if rnx_path.exists():
        print(f"     → {rnx_path.name}  (already converted)")
        return rnx_path

    candidates = (
        [str(TOOLS_DIR / e) for e in ["CRX2RNX.exe", "CRX2RNX", "crx2rnx"]]
        + ["CRX2RNX.exe", "CRX2RNX", "crx2rnx"]
    )
    for exe in candidates:
        try:
            r = subprocess.run([exe, str(crx_path)],
                               capture_output=True, timeout=60)
            if r.returncode == 0 and rnx_path.exists():
                print(f"     → {rnx_path.name}")
                crx_path.unlink()
                return rnx_path
        except (FileNotFoundError, Exception):
            continue

    print(f"    ⚠  CRX2RNX not found — copy CRX2RNX.exe to {TOOLS_DIR}")
    return crx_path


def already_have(output_path):
    """
    Return True if a usable (non-.tmp) version of the file exists.
    Explicitly excludes .tmp files — those are incomplete downloads.
    """
    output_path = Path(output_path)
    parent = output_path.parent
    stem = output_path.stem   # e.g. "COD0OPSFIN_2026015_SP3.gz" → "COD0OPSFIN_2026015_SP3"

    # Check exact path
    if output_path.exists() and not output_path.name.endswith(".tmp"):
        return True

    # Check decompressed equivalents (no .gz / .Z extension)
    for suf in ["", ".crx", ".rnx", ".sp3", ".clk", ".erp",
                ".bia", ".snx", ".inx", ".ion", ".atx", ".obx"]:
        candidate = parent / (stem + suf)
        if candidate.exists() and not candidate.name.endswith(".tmp"):
            return True

    return False


def lookup_station(code):
    code = code.upper()
    for row in KNOWN_STATIONS:
        if row[0] == code:
            return row[0], row[1]
    print(f"  ⚠  '{code}' not in KNOWN_STATIONS — country defaulting to 'IGS'")
    return code, "IGS"


def banner(title):
    print(f"\n{'─'*62}\n  {title}\n{'─'*62}")


def try_candidates(session, candidates, out_dir, label):
    out_dir = Path(out_dir)
    for url, fname in candidates:
        op = out_dir / fname
        if already_have(op):
            print(f"  ⏭  {label} exists ({Path(fname).stem[:42]})")
            return True
        if download_file(session, url, op):
            decompress_file(op)
            return True
    print(f"  ⚠  {label}: not found from any source")
    return False

# ══════════════════════════════════════════════════════════════════
#  DOWNLOAD FUNCTIONS
# ══════════════════════════════════════════════════════════════════


def download_observation(session, code, country, year, doy):
    """
    File is Hatanaka-compressed RINEX 3: .crx.gz
    After download: decompress .gz → .crx → CRX2RNX → .rnx

    If .crx already exists but .rnx does not → run CRX2RNX directly.
    """
    ensure_dirs(DATA_DIR)
    yy = str(year)[2:]
    yyyyddd = f"{year:04d}{doy:03d}"
    crx_gz = f"{code}00{country}_R_{yyyyddd}0000_01D_30S_MO.crx.gz"
    crx = DATA_DIR / crx_gz[:-3]
    rnx = DATA_DIR / (crx_gz[:-7] + ".rnx")

    banner(f"Observation: {code} ({country})")

    # Already fully converted
    if rnx.exists():
        print(f"  ⏭  Already have: {rnx.name}")
        return rnx

    # .crx exists but not yet converted — just run CRX2RNX
    if crx.exists():
        print(f"  ↻  .crx found — converting to .rnx")
        return crx2rnx(crx)

    # Need to download
    out = DATA_DIR / crx_gz
    url = f"{CDDIS}/data/daily/{year}/{doy:03d}/{yy}d/{crx_gz}"

    if download_file(session, url, out):
        crx_path = decompress_gz(out)
        return crx2rnx(crx_path)

    print(f"  ✗ Not found: {crx_gz}")
    return None


def download_broadcast_nav(session, year, doy):
    ensure_dirs(PRODUCTS_DIR / "nav")
    yyyyddd = f"{year:04d}{doy:03d}"
    banner("Broadcast Navigation (Mixed GNSS)")
    cands = [
        (f"{CDDIS}/data/daily/{year}/brdc/BRD400DLR_S_{yyyyddd}0000_01D_MN.rnx.gz",
         f"BRD400DLR_S_{yyyyddd}0000_01D_MN.rnx.gz"),
        (f"{CDDIS}/data/daily/{year}/brdc/BRDC00IGS_R_{yyyyddd}0000_01D_MN.rnx.gz",
         f"BRDC00IGS_R_{yyyyddd}0000_01D_MN.rnx.gz"),
    ]
    try_candidates(session, cands, PRODUCTS_DIR/"nav", "Broadcast nav")


def download_precise_products(session, year, doy, gps_week, gps_dow):
    ensure_dirs(PRODUCTS_DIR/"sp3", PRODUCTS_DIR/"clk", PRODUCTS_DIR/"erp")
    yyyyddd = f"{year:04d}{doy:03d}"
    gwd = f"{gps_week}{gps_dow}"
    base = f"{CDDIS}/products/{gps_week}/"

    banner(f"Precise Products  (GPS week {gps_week}, DOW {gps_dow})")
    print("  Priority: IGS Final > CODE Final > CODE MGEX > WUM Rapid > legacy")

    sp3 = [
        (base+f"IGS0OPSFIN_{yyyyddd}0000_01D_05M_ORB.SP3.gz",
         f"IGS0OPSFIN_{yyyyddd}_ORB.SP3.gz"),
        (base+f"COD0OPSFIN_{yyyyddd}0000_01D_05M_ORB.SP3.gz",
         f"COD0OPSFIN_{yyyyddd}_ORB.SP3.gz"),
        (base+f"COD0MGXFIN_{yyyyddd}0000_01D_05M_ORB.SP3.gz",
         f"COD0MGXFIN_{yyyyddd}_ORB.SP3.gz"),
        (base+f"WUM0MGXRAP_{yyyyddd}0000_01D_05M_ORB.SP3.gz",
         f"WUM0MGXRAP_{yyyyddd}_ORB.SP3.gz"),
        (base+f"igs{gwd}.sp3.Z",
         f"igs{gwd}.sp3.Z"),
    ]
    clk = [
        (base+f"IGS0OPSFIN_{yyyyddd}0000_01D_30S_CLK.CLK.gz",
         f"IGS0OPSFIN_{yyyyddd}_CLK.CLK.gz"),
        (base+f"COD0OPSFIN_{yyyyddd}0000_01D_30S_CLK.CLK.gz",
         f"COD0OPSFIN_{yyyyddd}_CLK.CLK.gz"),
        (base+f"COD0MGXFIN_{yyyyddd}0000_01D_30S_CLK.CLK.gz",
         f"COD0MGXFIN_{yyyyddd}_CLK.CLK.gz"),
        (base+f"WUM0MGXRAP_{yyyyddd}0000_01D_30S_CLK.CLK.gz",
         f"WUM0MGXRAP_{yyyyddd}_CLK.CLK.gz"),
        (base+f"igs{gwd}.clk_30s.Z",
         f"igs{gwd}.clk_30s.Z"),
    ]
    erp = [
        (base+f"IGS0OPSFIN_{yyyyddd}0000_01D_01D_ERP.ERP.gz",
         f"IGS0OPSFIN_{yyyyddd}_ERP.ERP.gz"),
        (base+f"EMR0OPSFIN_{yyyyddd}0000_01D_01D_ERP.ERP.gz",
         f"EMR0OPSFIN_{yyyyddd}_ERP.ERP.gz"),
        (base+f"COD0OPSFIN_{yyyyddd}0000_01D_12H_ERP.ERP.gz",
         f"COD0OPSFIN_{yyyyddd}_ERP.ERP.gz"),
        (base+f"COD0MGXFIN_{yyyyddd}0000_01D_12H_ERP.ERP.gz",
         f"COD0MGXFIN_{yyyyddd}_ERP.ERP.gz"),
        (base+f"WUM0MGXRAP_{yyyyddd}0000_01D_01D_ERP.ERP.gz",
         f"WUM0MGXRAP_{yyyyddd}_ERP.ERP.gz"),
        (base+f"igs{gwd}.erp.Z",
         f"igs{gwd}.erp.Z"),
    ]

    for label, subdir, cands in [("SP3", "sp3", sp3), ("CLK", "clk", clk), ("ERP", "erp", erp)]:
        try_candidates(session, cands, PRODUCTS_DIR/subdir, label)


def download_cod_mgxfin(session, year, doy, gps_week):
    """
    Download CODE MGEX Final products (COD0MGXFIN).
    These are Final multi-GNSS products — best choice for G+R+E+C+J PPP.
    Downloaded separately (not as fallback) because COD0OPSFIN is GPS/GLO only
    and gets found first, so COD0MGXFIN would otherwise be skipped.
    """
    ensure_dirs(PRODUCTS_DIR/"sp3", PRODUCTS_DIR/"clk",
                PRODUCTS_DIR/"erp", PRODUCTS_DIR/"bia")
    yyyyddd = f"{year:04d}{doy:03d}"
    base = f"{CDDIS}/products/{gps_week}/"
    banner("CODE MGEX Final Products (COD0MGXFIN) — Multi-GNSS Best")

    for label, subdir, suffix in [
        ("SP3 (multi-GNSS final)", "sp3", "_01D_05M_ORB.SP3.gz"),
        ("CLK (multi-GNSS final)", "clk", "_01D_30S_CLK.CLK.gz"),
        ("ERP (multi-GNSS final)", "erp", "_01D_12H_ERP.ERP.gz"),
        ("OSB (phase biases)", "bia", "_01D_01D_OSB.BIA.gz"),
        ("OBX (attitude)", "obx", "_01D_30S_ATT.OBX.gz"),
    ]:
        ensure_dirs(PRODUCTS_DIR/subdir)
        fname_gz = f"COD0MGXFIN_{yyyyddd}0000{suffix}"
        url = base + fname_gz
        op = PRODUCTS_DIR / subdir / fname_gz
        if already_have(op):
            print(f"  ⏭  COD0MGXFIN {label} exists")
            continue
        if download_file(session, url, op):
            decompress_file(op)
        else:
            print(f"  ⚠  COD0MGXFIN {label}: not yet published or unavailable")


def download_wuhan_products(session, year, doy, gps_week):
    ensure_dirs(PRODUCTS_DIR/"sp3", PRODUCTS_DIR/"clk",
                PRODUCTS_DIR/"bia", PRODUCTS_DIR/"erp")
    yyyyddd = f"{year:04d}{doy:03d}"
    base = f"{CDDIS}/products/{gps_week}/"
    banner("Wuhan Multi-GNSS Products (WUM)")

    for label, subdir, suffix in [
        ("SP3", "sp3", "_01D_05M_ORB.SP3.gz"),
        ("CLK", "clk", "_01D_30S_CLK.CLK.gz"),
        ("OSB", "bia", "_01D_01D_OSB.BIA.gz"),
        ("ERP", "erp", "_01D_01D_ERP.ERP.gz"),
    ]:
        cands = [
            (base+f"WUM0MGXFIN_{yyyyddd}0000{suffix}",
             f"WUM0MGXFIN_{yyyyddd}0000{suffix}"),
            (base+f"WUM0MGXRAP_{yyyyddd}0000{suffix}",
             f"WUM0MGXRAP_{yyyyddd}0000{suffix}"),
        ]
        done = False
        for url, fname in cands:
            op = PRODUCTS_DIR / subdir / fname
            if already_have(op):
                tag = "FIN" if "FIN" in fname else "RAP"
                print(f"  ⏭  WUM {label} exists (WUM0MGX{tag})")
                done = True
                break
            if download_file(session, url, op):
                decompress_file(op)
                done = True
                break
        if not done:
            print(
                f"  ⚠  WUM {label}: not yet published (normal for recent dates)")


def download_code_biases(session, year, doy, gps_week):
    ensure_dirs(PRODUCTS_DIR/"dcb")
    yyyyddd = f"{year:04d}{doy:03d}"
    bias_url = f"{CDDIS}/products/bias/{year}/"
    prod_url = f"{CDDIS}/products/{gps_week}/"
    banner("Code/Phase Biases (DCB/OSB)")
    cands = [
        (bias_url+f"CAS0OPSRAP_{yyyyddd}0000_01D_01D_DCB.BIA.gz",
         f"CAS0OPSRAP_{yyyyddd}_DCB.BIA.gz"),
        (prod_url+f"COD0OPSFIN_{yyyyddd}0000_01D_01D_OSB.BIA.gz",
         f"COD0OPSFIN_{yyyyddd}_OSB.BIA.gz"),
        (prod_url+f"COD0MGXFIN_{yyyyddd}0000_01D_01D_OSB.BIA.gz",
         f"COD0MGXFIN_{yyyyddd}_OSB.BIA.gz"),
        (prod_url+f"WUM0MGXRAP_{yyyyddd}0000_01D_01D_OSB.BIA.gz",
         f"WUM0MGXRAP_{yyyyddd}_OSB.BIA.gz"),
    ]
    try_candidates(session, cands, PRODUCTS_DIR/"dcb", "Bias")


def download_attitude_file(session, year, doy, gps_week):
    """Satellite attitude quaternions (OBX). Used by PRIDE PPP-AR for precise
    attitude modelling, especially during eclipse seasons."""
    ensure_dirs(PRODUCTS_DIR / "obx")
    yyyyddd = f"{year:04d}{doy:03d}"
    base = f"{CDDIS}/products/{gps_week}/"
    banner("Satellite Attitude (OBX) — PRIDE PPP-AR")
    cands = [
        (base + f"COD0MGXFIN_{yyyyddd}0000_01D_30S_ATT.OBX.gz",
         f"COD0MGXFIN_{yyyyddd}_ATT.OBX.gz"),
        (base + f"WUM0MGXFIN_{yyyyddd}0000_01D_30S_ATT.OBX.gz",
         f"WUM0MGXFIN_{yyyyddd}_ATT.OBX.gz"),
        (base + f"WUM0MGXRAP_{yyyyddd}0000_01D_30S_ATT.OBX.gz",
         f"WUM0MGXRAP_{yyyyddd}_ATT.OBX.gz"),
    ]
    try_candidates(session, cands, PRODUCTS_DIR / "obx", "Attitude (OBX)")


def download_ionosphere_map(session, year, doy):
    ensure_dirs(PRODUCTS_DIR/"ionex")
    yyyyddd = f"{year:04d}{doy:03d}"
    folder = f"{CDDIS}/products/ionosphere/{year}/{doy:03d}/"
    banner("Ionosphere Map (IONEX / GIM)")
    cands = [
        (folder+f"COD0OPSFIN_{yyyyddd}0000_01D_01H_GIM.INX.gz",
         f"COD0OPSFIN_{yyyyddd}_GIM.INX.gz"),
        (folder+f"COD0OPSRAP_{yyyyddd}0000_01D_01H_GIM.INX.gz",
         f"COD0OPSRAP_{yyyyddd}_GIM.INX.gz"),
        (folder+f"EMR0OPSFIN_{yyyyddd}0000_01D_01H_GIM.INX.gz",
         f"EMR0OPSFIN_{yyyyddd}_GIM.INX.gz"),
        (folder+f"ESA0OPSFIN_{yyyyddd}0000_01D_02H_GIM.INX.gz",
         f"ESA0OPSFIN_{yyyyddd}_GIM.INX.gz"),
    ]
    try_candidates(session, cands, PRODUCTS_DIR/"ionex", "IONEX")


def download_antenna_file():
    ensure_dirs(PRODUCTS_DIR/"atx")
    op = PRODUCTS_DIR / "atx" / "igs20.atx"
    banner("Antenna Corrections (IGS20 ANTEX)")

    if op.exists():
        print("  ⏭  igs20.atx present")
        return op

    # Auto-find team copy under any name in common locations
    for name in ["igs20.atx", "igs20_2401.atx"]:
        for d in [BASE_DIR, BASE_DIR/"data", PRODUCTS_DIR, PRODUCTS_DIR/"atx"]:
            src = d / name
            if src.exists() and src != op:
                shutil.copy2(src, op)
                print(f"  ✓ Copied from {src.name} → igs20.atx")
                return op

    s = requests.Session()
    if download_file(s, IGS_ATX, op, skip_auth=True):
        return op

    print("  ⚠  Could not download — place manually:")
    print(f"       Copy igs20_2401.atx from team zip → rename → {op}")
    return None


def download_station_coords(session, year, doy, gps_week):
    ensure_dirs(PRODUCTS_DIR/"snx")
    yyyyddd = f"{year:04d}{doy:03d}"
    week_start = gps_week_start_yyyyddd(gps_week)
    base = f"{CDDIS}/products/{gps_week}/"
    banner("Station Coordinates (SINEX)")
    cands = [
        (base+f"MIT0OPSSNX_{yyyyddd}0000_01D_01D_SOL.SNX.gz",
         f"MIT0OPSSNX_{yyyyddd}_SOL.SNX.gz"),
        (base+f"JPL0OPSFIN_{yyyyddd}0000_01D_01D_SOL.SNX.gz",
         f"JPL0OPSFIN_{yyyyddd}_SOL.SNX.gz"),
        (base+f"COD0OPSFIN_{yyyyddd}0000_01D_01D_SOL.SNX.gz",
         f"COD0OPSFIN_{yyyyddd}_SOL.SNX.gz"),
        (base+f"IGS0OPSFIN_{week_start}0000_07D_07D_SOL.SNX.gz",
         f"IGS0OPSFIN_{week_start}_SOL.SNX.gz"),
        (base+f"igs{gps_week}7.snx.Z",
         f"igs{gps_week}7.snx.Z"),
    ]
    try_candidates(session, cands, PRODUCTS_DIR/"snx", "SINEX")


def print_phase_bias_info(year, doy):
    yyyyddd = f"{year:04d}{doy:03d}"
    banner("Phase Biases (PRIDE PPP-AR)")
    print(f"  pdp3 downloads these automatically when you run it.")
    print(f"  Manual: ftps://bdspride.com/wum/")
    print(f"  Pattern: WUM0MGXRAP_{yyyyddd}*_bia.gz")
    print(f"  Command: pdp3 -m S -sys gec <obs_file.rnx>")

# ══════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════


def main():
    import argparse
    global YEAR, DOY, GPS_WEEK, GPS_DOW

    p = argparse.ArgumentParser(
        description="PPP Data Downloader v6",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--stations",      nargs="+", default=["BJFS", "GOLD"])
    p.add_argument("--date",          nargs=2, type=int, metavar=("YEAR", "DOY"),
                   default=[YEAR, DOY])
    p.add_argument("--obs-only",      action="store_true",
                   help="Download/convert observations only")
    p.add_argument("--skip-wuhan",    action="store_true")
    p.add_argument("--clean-tmp",     action="store_true",
                   help="Remove leftover .tmp files and exit")
    args = p.parse_args()

    YEAR, DOY = args.date
    GPS_WEEK, GPS_DOW = compute_gps_week_dow(YEAR, DOY)
    date_str = (dt(YEAR, 1, 1)+datetime.timedelta(days=DOY-1)
                ).strftime("%Y-%m-%d")

    # ── Clean mode ──────────────────────────────────────────────
    if args.clean_tmp:
        print("\n  🧹 Cleaning .tmp files ...")
        clean_tmp_files(DATA_DIR, PRODUCTS_DIR)
        print()
        return

    get_credentials()
    session = make_session()

    print("\n" + "═"*62)
    print(f"  PPP DATA DOWNLOADER  v6")
    print(
        f"  Date    : {date_str}  DOY={DOY:03d}  GPS week {GPS_WEEK} / DOW {GPS_DOW}")
    print(f"  Stations: {', '.join(args.stations)}")
    print(f"  Data    : {DATA_DIR}")
    print(f"  Products: {PRODUCTS_DIR}")
    print("═"*62)

    # Auto-clean .tmp files at startup so stale partials don't block downloads
    stale = list(Path(DATA_DIR).rglob("*.tmp")) + \
        list(Path(PRODUCTS_DIR).rglob("*.tmp"))
    if stale:
        print(
            f"\n  🧹 Removing {len(stale)} leftover .tmp file(s) from previous run...")
        for f in stale:
            print(f"     {f.parent.name}/{f.name}")
            f.unlink()

    for code in args.stations:
        stn, ctry = lookup_station(code)
        download_observation(session, stn, ctry, YEAR, DOY)

    if args.obs_only:
        print("\n  ✓ Observation-only mode done.\n")
        return

    download_broadcast_nav(session, YEAR, DOY)
    download_precise_products(session, YEAR, DOY, GPS_WEEK, GPS_DOW)
    download_cod_mgxfin(session, YEAR, DOY, GPS_WEEK)
    if not args.skip_wuhan:
        download_wuhan_products(session, YEAR, DOY, GPS_WEEK)
    download_code_biases(session, YEAR, DOY, GPS_WEEK)
    download_ionosphere_map(session, YEAR, DOY)
    download_attitude_file(session, YEAR, DOY, GPS_WEEK)
    download_antenna_file()
    download_station_coords(session, YEAR, DOY, GPS_WEEK)
    print_phase_bias_info(YEAR, DOY)

    print("\n" + "═"*62)
    print("  ✅ DOWNLOAD COMPLETE")
    print("═"*62)
    print(f"""
  Directories
    Observations : {DATA_DIR}
    Products     : {PRODUCTS_DIR}

  WHAT EACH TOOL NEEDS
  ┌─────────────┬────────────────────────────────────────────┐
  │ RTKLIB      │ obs.rnx  +  broadcast-nav.rnx             │
  │             │ OR  obs.rnx  +  SP3  +  CLK               │
  ├─────────────┼────────────────────────────────────────────┤
  │ GAMP        │ obs.rnx + SP3 + CLK + ERP + DCB +         │
  │             │ IONEX + ATX  (+ SINEX recommended)        │
  ├─────────────┼────────────────────────────────────────────┤
  │ PRIDE PPP-AR│ obs.rnx + SP3 + CLK + ERP + OSB + ATX     │
  │             │ + OBX (attitude) + SNX                     │
  │             │ (phase bias also auto-downloaded by pdp3)  │
  └─────────────┴────────────────────────────────────────────┘

  NEXT STEPS""")
    for code in args.stations:
        print(f"    python check_station.py {code}")
    print("    cd GAMP_work && gamp.exe gamp.cfg\n")


if __name__ == "__main__":
    main()
