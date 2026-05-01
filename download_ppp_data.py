#!/usr/bin/env python3
"""
🌐 Complete PPP Data Downloader  (FIXED)
=========================================
Download ALL products needed for PPP processing:
  1. RTKLIB/RTKPOST (broadcast or precise ephemeris)
  2. GAMP            (precise products via config file)
  3. PRIDE PPP-AR    (with phase biases for fastest convergence)
  4. RTKLIB-demo     (same as RTKLIB, enhanced algorithms)

FIXES vs original
─────────────────
 1. Observation subdirectory   : always  {yy}d  (e.g. 26d) — not "24d/24o"
 2. Broadcast nav subdirectory : always  brdc   (not 24p / {yy}m)
 3. Broadcast nav filename     : BRD400DLR_S_{YYYYDDD}0000_01D_MN.rnx.gz
                                 (prefix BRD4, source DLR, type S)
 4. IGS SP3 interval           : 15M → 05M (long-name files use 05M on CDDIS)
 5. WUM SP3 filename           : _01D_orb.sp3.gz → _05M_ORB.SP3.gz
 6. WUM CLK filename           : _01D_clk.clk.gz → _30S_CLK.CLK.gz
 7. WUM URL base               : products/mgex/  → products/{gps_week}/
 8. Bias filename/path         : CAS0MGXRAP_…_DCB.BSX.gz
                                 → CAS0OPSRAP_…_DCB.BIA.gz  (products/bias/{year}/)
    Also adds COD0MGXFIN OSB as second fallback
 9. Ionosphere path            : products/ionex/ → products/ionosphere/
10. Ionosphere filename        : IGS0OPSFIN_…_ION.ION.gz
                                 → COD0OPSFIN_…_GIM.INX.gz  (COD = CODE, best avail)
    Also adds COD0OPSRAP as rapid fallback
11. SINEX URL                  : literal "YYYYDDD" placeholder fixed to real date
    Also adds correct weekly SINEX name IGS0OPSFIN_{week_start_YYYYDDD}0000…
12. ERP legacy name            : igs{week}7.erp.Z → igs{week}{dow}.erp.Z
13. Station country lookup     : expanded table for HKWS (HKG), ZIM2 (CHE), etc.

USAGE
─────
    python download_ppp_data.py
    python download_ppp_data.py --stations HKWS ZIM2
    python download_ppp_data.py --stations BJFS GOLD --date 2026 015
    python download_ppp_data.py --obs-only
    python download_ppp_data.py --no-decompress
    python download_ppp_data.py --skip-wuhan

REQUIREMENTS
────────────
    pip install requests python-dotenv tqdm

SETUP
─────
    1. Register at https://urs.earthdata.nasa.gov
    2. Create .env file (or export env vars):
           EARTHDATA_USERNAME=your_username
           EARTHDATA_PASSWORD=your_password
"""

import os
import sys
import gzip
import shutil
import requests
import datetime
import hashlib
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

# Fix Unicode output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ==============================================================================
#  CONFIGURATION
# ==============================================================================

BASE_DIR = Path(r"C:\PPP_PROJECT")
DATA_DIR = BASE_DIR / "data"
PRODUCTS_DIR = BASE_DIR / "products"

# Default date: 2026-01-15  (GPS week 2401, day-of-week 4 = Thursday)
YEAR = 2026
DOY = 15
GPS_WEEK = 2401
GPS_DOW = 4        # 0=Sunday … 6=Saturday

# Derived strings (recalculated in main() when --date is used)
YY = str(YEAR)[2:]
DOY_STR = f"{DOY:03d}"
YYYYDDD = f"{YEAR:04d}{DOY:03d}"

CDDIS_BASE = "https://cddis.nasa.gov/archive/gnss"
IGS_FTP = "https://files.igs.org/pub/station/general"

# Credentials loaded from .env or environment
EARTHDATA_USER = (os.environ.get("EARTHDATA_USERNAME", "")
                  or os.environ.get("EARTHDATA_USER", ""))
EARTHDATA_PASS = (os.environ.get("EARTHDATA_PASSWORD", "")
                  or os.environ.get("EARTHDATA_PASS", ""))

# ---------------------------------------------------------------------------
#  Station lookup table  (code → country-code used in RINEX long filenames)
#  Extend this list as needed.
# ---------------------------------------------------------------------------
KNOWN_STATIONS = [
    # Asia-Pacific
    ("BJFS", "CHN", "Beijing Fangshan, China"),
    ("SHAO", "CHN", "Shanghai Sheshan, China"),
    ("WUHN", "CHN", "Wuhan, China"),
    ("HKWS", "HKG", "Hong Kong Wong Shek"),
    ("HKSL", "HKG", "Hong Kong Siu Lang Shui"),
    ("HKMZ", "HKG", "Hong Kong Ma Zi Po"),
    ("TWTF", "TWN", "Taoyuan, Taiwan"),
    ("USUD", "JPN", "Usuda, Japan"),
    ("AIRA", "JPN", "Aira, Japan"),
    ("TOW2", "AUS", "Townsville, Australia"),
    ("KARR", "AUS", "Karratha, Australia"),
    ("DARW", "AUS", "Darwin, Australia"),
    ("IISC", "IND", "Bangalore, India"),
    # Europe
    ("ZIM2", "CHE", "Zimmerwald, Switzerland"),
    ("ZIMM", "CHE", "Zimmerwald, Switzerland"),
    ("GRAZ", "AUT", "Graz, Austria"),
    ("MATE", "ITA", "Matera, Italy"),
    ("ONSA", "SWE", "Onsala, Sweden"),
    ("WSRT", "NLD", "Westerbork, Netherlands"),
    ("BRUX", "BEL", "Brussels, Belgium"),
    ("WARN", "DEU", "Warnemuende, Germany"),
    ("WTZR", "DEU", "Wettzell, Germany"),
    ("TLSE", "FRA", "Toulouse, France"),
    ("MAD2", "ESP", "Madrid, Spain"),
    ("NYAL", "NOR", "Ny-Ålesund, Norway"),
    ("KIRU", "SWE", "Kiruna, Sweden"),
    # Americas
    ("GOLD", "USA", "Goldstone, California"),
    ("AMC2", "USA", "Colorado Springs"),
    ("ALGO", "CAN", "Algonquin, Canada"),
    ("CHUR", "CAN", "Churchill, Canada"),
    ("ABMF", "PYF", "Guadeloupe, France"),   # actually FLK? use IGS code
    ("AREQ", "PER", "Arequipa, Peru"),
    ("BRAZ", "BRA", "Brasilia, Brazil"),
    ("SANT", "CHL", "Santiago, Chile"),
    ("MANA", "NIC", "Managua, Nicaragua"),
    # Africa
    ("NKLG", "GAB", "Libreville, Gabon"),
    ("SUTH", "ZAF", "Sutherland, South Africa"),
    ("HRAO", "ZAF", "Hartebeesthoek, South Africa"),
    # Other
    ("JFNG", "CHN", "Jiufeng, China"),
    ("PIMO", "PHL", "Quezon City, Philippines"),
    ("GUAM", "GUM", "Guam"),
    ("KOKB", "USA", "Kokee Park, Hawaii"),
    ("FAIR", "USA", "Fairbanks, Alaska"),
    ("MCM4", "ATA", "McMurdo, Antarctica"),
]


# ==============================================================================
#  GPS WEEK CALCULATOR
# ==============================================================================

def compute_gps_week_dow(year: int, doy: int):
    """Return (gps_week, day_of_week) for a given year + day-of-year."""
    epoch = dt(year, 1, 1) + datetime.timedelta(days=doy - 1)
    gps_epoch = dt(1980, 1, 6)
    total_days = (epoch - gps_epoch).days
    return total_days // 7, total_days % 7


def gps_week_start_yyyyddd(gps_week: int) -> str:
    """Return YYYYDDD string for Sunday (start) of a GPS week."""
    gps_epoch = dt(1980, 1, 6)
    week_start = gps_epoch + datetime.timedelta(weeks=gps_week)
    doy = week_start.timetuple().tm_yday
    return f"{week_start.year:04d}{doy:03d}"


# ==============================================================================
#  HELPER FUNCTIONS
# ==============================================================================

def ensure_dirs(*paths):
    for p in paths:
        Path(p).mkdir(parents=True, exist_ok=True)


def get_credentials():
    global EARTHDATA_USER, EARTHDATA_PASS
    if not EARTHDATA_USER:
        print("\n🔐 Earthdata Login Required (https://urs.earthdata.nasa.gov)")
        EARTHDATA_USER = input("  Username: ").strip()
    if not EARTHDATA_PASS:
        EARTHDATA_PASS = getpass("  Password: ")


def make_session():
    s = requests.Session()
    s.auth = (EARTHDATA_USER, EARTHDATA_PASS)
    return s


def download_file(session, url, output_path, skip_auth=False):
    """Download *url* to *output_path*. Returns True on success."""
    try:
        print(f"  📥 {Path(url).name} ...", end="", flush=True)

        if skip_auth:
            response = requests.get(url, timeout=60, stream=True)
        else:
            response = session.get(url, timeout=60,
                                   allow_redirects=True, stream=True)

        if response.status_code == 404:
            print(" ✗ (404 Not Found)")
            return False

        response.raise_for_status()

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        total = int(response.headers.get("content-length", 0))
        tmp = output_path.with_suffix(output_path.suffix + ".tmp")

        if HAS_TQDM and total > 0:
            with tqdm(total=total, unit="B", unit_scale=True,
                      desc=f"     {output_path.name}", leave=False) as bar:
                with open(tmp, "wb") as fh:
                    for chunk in response.iter_content(32768):
                        fh.write(chunk)
                        bar.update(len(chunk))
        else:
            with open(tmp, "wb") as fh:
                for chunk in response.iter_content(32768):
                    fh.write(chunk)

        tmp.rename(output_path)
        size_mb = output_path.stat().st_size / 1024 / 1024
        print(f" ✓ ({size_mb:.1f} MB)")
        return True

    except requests.exceptions.HTTPError as e:
        print(f" ✗ (HTTP {e.response.status_code})")
        return False
    except Exception as e:
        print(f" ✗ ({str(e)[:60]})")
        return False


def decompress_file(filepath):
    """Decompress .gz or .Z file in-place. Returns path to decompressed file."""
    filepath = Path(filepath)

    if filepath.suffix == ".gz":
        output_path = filepath.with_suffix("")
        try:
            with gzip.open(filepath, "rb") as f_in, \
                    open(output_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
            filepath.unlink()
            print(f"    ✓ Decompressed → {output_path.name}")
            return output_path
        except Exception as e:
            print(f"    ⚠️  Decompression failed: {e}")
            return filepath

    elif filepath.suffix == ".Z":
        output_path = filepath.with_suffix("")

        # Unix uncompress
        try:
            result = subprocess.run(
                ["uncompress", "-f", str(filepath)],
                capture_output=True, timeout=60
            )
            if result.returncode == 0:
                print(f"    ✓ Decompressed → {output_path.name}")
                return output_path
        except FileNotFoundError:
            pass

        # Windows 7-Zip
        seven_zip = Path("C:/Program Files/7-Zip/7z.exe")
        if seven_zip.exists():
            try:
                subprocess.run(
                    [str(seven_zip), "e", str(filepath),
                     f"-o{filepath.parent}", "-y"],
                    capture_output=True, timeout=60, check=True
                )
                filepath.unlink()
                print(f"    ✓ Decompressed (7z) → {output_path.name}")
                return output_path
            except Exception:
                pass

        print(f"    ℹ️  .Z file kept compressed (install 7-Zip or uncompress)")
        return filepath

    return filepath


def verify_checksum(filepath, expected_md5):
    """Verify file MD5 checksum."""
    if not expected_md5:
        return True
    try:
        md5 = hashlib.md5()
        with open(filepath, "rb") as fh:
            for chunk in iter(lambda: fh.read(8192), b""):
                md5.update(chunk)
        if md5.hexdigest().lower() == expected_md5.lower():
            print("    ✓ MD5 verified")
            return True
        else:
            print("    ⚠️  MD5 mismatch")
            return False
    except Exception as e:
        print(f"    (MD5 check skipped: {e})")
        return True


def lookup_station(code: str) -> tuple:
    """Return (code, country, desc) — falls back to IGS if unknown."""
    code_upper = code.upper()
    for s in KNOWN_STATIONS:
        if s[0].upper() == code_upper:
            return s
    print(f"  ⚠️  Unknown station {code_upper} — defaulting country to IGS")
    return (code_upper, "IGS", f"IGS Station {code_upper}")


# ==============================================================================
#  DOWNLOAD FUNCTIONS
# ==============================================================================

# ── 1. OBSERVATION FILES ──────────────────────────────────────────────────────

def download_observation(session, station_code, country_code, year, doy):
    """
    Download RINEX 3 mixed-GNSS observation file.

    FIX: subdir is always  {yy}d  (e.g. "26d") — not "24d" or "24o".
    CDDIS stores obs under:
        /archive/gnss/data/daily/{year}/{doy:03d}/{yy}d/
    """
    ensure_dirs(DATA_DIR)

    yy = str(year)[2:]
    yyddd = f"{year:04d}{doy:03d}"
    subdir = f"{yy}d"                          # FIX 1: was "24d","24o","{yy}d"

    print(f"\n📡 Observation: {station_code} ({country_code})")

    filename = f"{station_code}00{country_code}_R_{yyddd}0000_01D_30S_MO.rnx.gz"
    url = f"{CDDIS_BASE}/data/daily/{year}/{doy:03d}/{subdir}/{filename}"
    output_path = DATA_DIR / filename

    if output_path.exists():
        print(f"  ⏭️  Already exists: {filename}")
        return output_path
    if output_path.with_suffix("").exists():
        print(
            f"  ⏭️  Already decompressed: {output_path.with_suffix('').name}")
        return output_path.with_suffix("")

    if download_file(session, url, output_path):
        return decompress_file(output_path)

    print(f"  ❌ File not found for {station_code}")
    return None


# ── 2. BROADCAST NAVIGATION ───────────────────────────────────────────────────

def download_broadcast_nav(session, year, doy):
    """
    Download mixed broadcast navigation file.

    FIX 2: subdir is  brdc  (not "24p" or "{yy}m").
    FIX 3: filename prefix is BRD4, source code DLR, stream type S.
            BRD400DLR_S_{YYYYDDD}0000_01D_MN.rnx.gz
    """
    ensure_dirs(PRODUCTS_DIR / "nav")

    yyddd = f"{year:04d}{doy:03d}"

    print(f"\n📡 Broadcast Navigation (Mixed GNSS)")

    # Primary: new long-name mixed nav from DLR  (in /brdc/ subfolder)
    # Fallback: legacy per-year mixed nav file
    candidates = [
        (
            f"{CDDIS_BASE}/data/daily/{year}/brdc/"
            f"BRD400DLR_S_{yyddd}0000_01D_MN.rnx.gz",   # FIX 2+3
            f"BRD400DLR_S_{yyddd}0000_01D_MN.rnx.gz",
        ),
    ]

    for url, fname in candidates:
        output_path = PRODUCTS_DIR / "nav" / fname
        if output_path.exists():
            print(f"  ⏭️  Already exists: {fname}")
            return output_path
        if output_path.with_suffix("").exists():
            return output_path.with_suffix("")
        if download_file(session, url, output_path):
            return decompress_file(output_path)

    print("  ⚠️  Broadcast nav not found from any source")
    return None


# ── 3. PRECISE PRODUCTS (IGS final) ───────────────────────────────────────────

def download_precise_products(session, year, doy, gps_week, gps_dow):
    """
    Download IGS final precise orbits, clocks, and ERP.

    FIX 4: SP3 long-name uses 05M interval (not 15M).
    FIX 12: ERP legacy uses igs{week}{dow}.erp.Z  (dow per-day, not always "7").
    """
    ensure_dirs(PRODUCTS_DIR / "sp3",
                PRODUCTS_DIR / "clk",
                PRODUCTS_DIR / "erp")

    yyddd = f"{year:04d}{doy:03d}"
    gwd = f"{gps_week}{gps_dow}"

    print(f"\n🎯 Precise Products (IGS Final)")
    print(f"   GPS Week {gps_week}, Day-of-week {gps_dow}")

    products = {
        "sp3": [
            (
                f"{CDDIS_BASE}/products/{gps_week}/"
                # FIX 4: 05M not 15M
                f"IGS0OPSFIN_{yyddd}0000_01D_05M_ORB.SP3.gz",
                f"IGS0OPSFIN_{yyddd}_ORB.SP3.gz",
            ),
            (
                f"{CDDIS_BASE}/products/{gps_week}/igs{gwd}.sp3.Z",
                f"igs{gwd}.sp3.Z",
            ),
        ],
        "clk": [
            (
                f"{CDDIS_BASE}/products/{gps_week}/"
                f"IGS0OPSFIN_{yyddd}0000_01D_30S_CLK.CLK.gz",
                f"IGS0OPSFIN_{yyddd}_CLK.CLK.gz",
            ),
            (
                f"{CDDIS_BASE}/products/{gps_week}/igs{gwd}.clk_30s.Z",
                f"igs{gwd}.clk_30s.Z",
            ),
        ],
        "erp": [
            (
                f"{CDDIS_BASE}/products/{gps_week}/"
                f"IGS0OPSFIN_{yyddd}0000_01D_01D_ERP.ERP.gz",
                f"IGS0OPSFIN_{yyddd}_ERP.ERP.gz",
            ),
            (
                f"{CDDIS_BASE}/products/{gps_week}/igs{gwd}.erp.Z",  # FIX 12
                f"igs{gwd}.erp.Z",
            ),
        ],
    }

    for prod_type, candidates in products.items():
        out_dir = PRODUCTS_DIR / prod_type
        downloaded = False
        for url, fname in candidates:
            output_path = out_dir / fname
            decompressed = output_path.with_suffix("")   # strip .gz / .Z
            if output_path.exists() or decompressed.exists():
                print(f"  ⏭️  {prod_type.upper()} exists")
                downloaded = True
                break
            if download_file(session, url, output_path):
                decompress_file(output_path)
                downloaded = True
                break
        if not downloaded:
            print(f"  ⚠️  {prod_type.upper()} not found from any source")


# ── 4. WUHAN MULTI-GNSS PRODUCTS ─────────────────────────────────────────────

def download_wuhan_products(session, year, doy, gps_week):
    """
    Download Wuhan University multi-GNSS products.

    FIX 5: SP3 suffix is _05M_ORB.SP3.gz  (not _01D_orb.sp3.gz)
    FIX 6: CLK suffix is _30S_CLK.CLK.gz  (not _01D_clk.clk.gz)
    FIX 7: URL base is products/{gps_week}/ (not products/mgex/{gps_week}/)
    Also downloads OSB bias file while we are here.
    """
    ensure_dirs(PRODUCTS_DIR / "sp3",
                PRODUCTS_DIR / "clk",
                PRODUCTS_DIR / "bia")

    yyddd = f"{year:04d}{doy:03d}"
    url_base = f"{CDDIS_BASE}/products/{gps_week}/"   # FIX 7

    print(f"\n🌏 Wuhan Products (Multi-GNSS, WUM)")

    wum_products = [
        # (suffix,                   local-subdir)
        ("_05M_ORB.SP3.gz",  "sp3"),   # FIX 5
        ("_30S_CLK.CLK.gz",  "clk"),   # FIX 6
        ("_01D_OSB.BIA.gz",  "bia"),
        ("_01D_ERP.ERP.gz",  "erp"),
    ]

    for suffix, out_subdir in wum_products:
        fname = f"WUM0MGXFIN_{yyddd}0000{suffix}"
        url = url_base + fname
        output_path = PRODUCTS_DIR / out_subdir / fname

        if output_path.exists() or output_path.with_suffix("").exists():
            print(f"  ⏭️  WUM {out_subdir.upper()} exists")
            continue
        if download_file(session, url, output_path):
            decompress_file(output_path)


# ── 5. CODE / PHASE BIASES ────────────────────────────────────────────────────

def download_code_biases(session, year, doy):
    """
    Download code/phase bias files.

    FIX 8: Correct filenames visible on CDDIS /archive/gnss/products/bias/{year}/:
            CAS0OPSRAP_{YYYYDDD}0000_01D_01D_DCB.BIA.gz   (rapid, CAS)
            COD0MGXFIN_{YYYYDDD}0000_01D_01D_OSB.BIA.gz   (final, CODE)
    Old wrong names: CAS0MGXRAP_…_DCB.BSX.gz, CAS0MGXFIN_…_OSB.BIA.gz
    """
    ensure_dirs(PRODUCTS_DIR / "dcb")

    yyddd = f"{year:04d}{doy:03d}"

    print(f"\n📊 Code/Phase Biases (OSB)")

    bias_base = f"{CDDIS_BASE}/products/bias/{year}/"   # FIX 8 path

    candidates = [
        (
            bias_base + f"CAS0OPSRAP_{yyddd}0000_01D_01D_DCB.BIA.gz",
            f"CAS0OPSRAP_{yyddd}_DCB.BIA.gz",
        ),
        (
            bias_base + f"COD0MGXFIN_{yyddd}0000_01D_01D_OSB.BIA.gz",
            f"COD0MGXFIN_{yyddd}_OSB.BIA.gz",
        ),
        (
            bias_base + f"CAS0MGXRAP_{yyddd}0000_01D_01D_OSB.BIA.gz",
            f"CAS0MGXRAP_{yyddd}_OSB.BIA.gz",
        ),
    ]

    for url, fname in candidates:
        output_path = PRODUCTS_DIR / "dcb" / fname
        if output_path.exists() or output_path.with_suffix("").exists():
            print(f"  ⏭️  Bias file exists ({fname})")
            return
        if download_file(session, url, output_path):
            decompress_file(output_path)
            return

    print("  ⚠️  No bias file found from any source")


# ── 6. IONOSPHERE MAP ─────────────────────────────────────────────────────────

def download_ionosphere_map(session, year, doy):
    """
    Download global ionosphere map (IONEX / GIM).

    FIX 9:  Path is products/ionosphere/{year}/{doy:03d}/  (not products/ionex/)
    FIX 10: Correct filenames visible on CDDIS:
              COD0OPSFIN_{YYYYDDD}0000_01D_01H_GIM.INX.gz  (final, CODE)
              COD0OPSRAP_{YYYYDDD}0000_01D_01H_GIM.INX.gz  (rapid, CODE)
              ESA0OPSFIN_{YYYYDDD}0000_01D_02H_GIM.INX.gz  (final, ESA)
    Old wrong: IGS0OPSFIN_…_ION.ION.gz, igsg…i.Z from ionex/ folder
    """
    ensure_dirs(PRODUCTS_DIR / "ionex")

    yyddd = f"{year:04d}{doy:03d}"
    folder = f"{CDDIS_BASE}/products/ionosphere/{year}/{doy:03d}/"   # FIX 9

    print(f"\n🌐 Ionosphere Map (IONEX)")

    candidates = [
        (
            folder + f"COD0OPSFIN_{yyddd}0000_01D_01H_GIM.INX.gz",   # FIX 10
            f"COD0OPSFIN_{yyddd}_GIM.INX.gz",
        ),
        (
            folder + f"COD0OPSRAP_{yyddd}0000_01D_01H_GIM.INX.gz",
            f"COD0OPSRAP_{yyddd}_GIM.INX.gz",
        ),
        (
            folder + f"ESA0OPSFIN_{yyddd}0000_01D_02H_GIM.INX.gz",
            f"ESA0OPSFIN_{yyddd}_GIM.INX.gz",
        ),
        (
            folder + f"EMR0OPSFIN_{yyddd}0000_01D_01H_GIM.INX.gz",
            f"EMR0OPSFIN_{yyddd}_GIM.INX.gz",
        ),
    ]

    for url, fname in candidates:
        output_path = PRODUCTS_DIR / "ionex" / fname
        if output_path.exists() or output_path.with_suffix("").exists():
            print(f"  ⏭️  IONEX exists ({fname})")
            return
        if download_file(session, url, output_path):
            decompress_file(output_path)
            return

    print("  ⚠️  IONEX not found from any source")


# ── 7. ANTENNA FILE ───────────────────────────────────────────────────────────

def download_antenna_file():
    """Download IGS20 antenna corrections (static — only needed once)."""
    ensure_dirs(PRODUCTS_DIR / "atx")

    output_path = PRODUCTS_DIR / "atx" / "igs20.atx"

    print(f"\n📡 Antenna Corrections (IGS20)")

    if output_path.exists():
        print("  ⏭️  igs20.atx exists")
        return output_path

    url = f"{IGS_FTP}/igs20.atx"
    session = requests.Session()   # public — no auth needed
    if download_file(session, url, output_path, skip_auth=True):
        return output_path

    return None


# ── 8. STATION COORDINATES (SINEX) ───────────────────────────────────────────

def download_station_coords(session, gps_week, gps_dow):
    """
    Download IGS weekly station coordinates (SINEX).

    FIX 11a: Replace literal "YYYYDDD" placeholder with actual week-start date.
    FIX 11b: SINEX covers 7 days — use Sunday (start) of the GPS week.
             Long-name: IGS0OPSFIN_{week_start}0000_07D_07D_SOL.SNX.gz
             Short-name: igs{week}{dow_of_last_day}7.snx.Z  (traditionally week's Thu = dow 4
             but the file is identified by the last day of the week = 6, so igs{week}7.snx.Z)
    """
    ensure_dirs(PRODUCTS_DIR / "snx")

    week_start_yyddd = gps_week_start_yyyyddd(gps_week)   # FIX 11a

    print(f"\n📍 Station Coordinates (SINEX)")

    candidates = [
        (
            f"{CDDIS_BASE}/products/{gps_week}/"
            f"IGS0OPSFIN_{week_start_yyddd}0000_07D_07D_SOL.SNX.gz",  # FIX 11b
            f"IGS0OPSFIN_{week_start_yyddd}_SOL.SNX.gz",
        ),
        (
            f"{CDDIS_BASE}/products/{gps_week}/igs{gps_week}7.snx.Z",
            f"igs{gps_week}7.snx.Z",
        ),
    ]

    for url, fname in candidates:
        output_path = PRODUCTS_DIR / "snx" / fname
        if output_path.exists() or output_path.with_suffix("").exists():
            print(f"  ⏭️  SNX exists ({fname})")
            return
        if download_file(session, url, output_path):
            decompress_file(output_path)
            return

    print("  ⚠️  SINEX coords not found from any source")


# ── 9. PHASE BIASES (PRIDE PPP-AR) ───────────────────────────────────────────

def download_phase_biases(year, doy):
    """Print info for PRIDE PPP-AR phase biases (auto-downloaded by pdp3)."""
    ensure_dirs(PRODUCTS_DIR / "bia")

    yyddd = f"{year:04d}{doy:03d}"

    print(f"\n⚡ Phase Biases (PRIDE PPP-AR)")
    print(f"  Auto-downloaded by: pdp3 -m S -sys gec <obs_file>")
    print(f"  Manual source:      ftps://bdspride.com/wum/")
    print(f"  Filename pattern:   WUM0MGXRAP_{yyddd}*_bia.gz")


# ==============================================================================
#  MAIN
# ==============================================================================

def main():
    import argparse

    global YEAR, DOY, YYYYDDD, YY, DOY_STR, GPS_WEEK, GPS_DOW

    parser = argparse.ArgumentParser(
        description="PPP Data Downloader — downloads all files needed for "
                    "RTKLIB, GAMP, PRIDE PPP-AR processing.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--stations", nargs="+", default=["BJFS", "GOLD"],
        help="Station codes (e.g. --stations HKWS ZIM2 GOLD)",
    )
    parser.add_argument(
        "--date", nargs=2, type=int, metavar=("YEAR", "DOY"),
        default=[YEAR, DOY],
        help="Date as YEAR DOY (e.g. --date 2026 015)",
    )
    parser.add_argument(
        "--obs-only", action="store_true",
        help="Download observation files only (skip products)",
    )
    parser.add_argument(
        "--no-decompress", action="store_true",
        help="Keep .gz/.Z files compressed (skip decompression)",
    )
    parser.add_argument(
        "--skip-wuhan", action="store_true",
        help="Skip Wuhan multi-GNSS products (use IGS GPS-only)",
    )

    args = parser.parse_args()

    # Update globals from CLI args
    YEAR, DOY = args.date[0], args.date[1]
    DOY_STR = f"{DOY:03d}"
    YYYYDDD = f"{YEAR:04d}{DOY:03d}"
    YY = str(YEAR)[2:]
    GPS_WEEK, GPS_DOW = compute_gps_week_dow(YEAR, DOY)

    date_obj = dt(YEAR, 1, 1) + datetime.timedelta(days=DOY - 1)

    get_credentials()
    session = make_session()

    print("\n" + "=" * 80)
    print(f"  🌐 PPP DATA DOWNLOADER  (fixed)")
    print(f"     Date    : {date_obj.strftime('%Y-%m-%d')}  (DOY {DOY})"
          f"  GPS Week {GPS_WEEK} / Day {GPS_DOW}")
    print(f"     Stations: {', '.join(args.stations)}")
    print(f"     Data    : {DATA_DIR}")
    print(f"     Products: {PRODUCTS_DIR}")
    print("=" * 80)

    # ── Observation files ─────────────────────────────────────────────────────
    for code in args.stations:
        sta = lookup_station(code)
        download_observation(session, sta[0], sta[1], YEAR, DOY)

    if args.obs_only:
        print("\n✓ Observation-only mode complete.\n")
        return

    # ── Products ──────────────────────────────────────────────────────────────
    download_broadcast_nav(session, YEAR, DOY)
    download_precise_products(session, YEAR, DOY, GPS_WEEK, GPS_DOW)
    if not args.skip_wuhan:
        download_wuhan_products(session, YEAR, DOY, GPS_WEEK)
    download_code_biases(session, YEAR, DOY)
    download_ionosphere_map(session, YEAR, DOY)
    download_antenna_file()
    download_station_coords(session, GPS_WEEK, GPS_DOW)
    download_phase_biases(YEAR, DOY)

    print("\n" + "=" * 80)
    print("✅ DOWNLOAD COMPLETE")
    print("=" * 80)
    print(f"\n📁 Observation data : {DATA_DIR}")
    print(f"📁 Products         : {PRODUCTS_DIR}")
    print(f"\nNext steps:")
    for code in args.stations:
        print(f"  python check_station.py {code}")
    print(f"  cd GAMP_work && gamp.exe gamp.cfg")
    print()


if __name__ == "__main__":
    main()
