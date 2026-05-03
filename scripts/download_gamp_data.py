#!/usr/bin/env python3
"""
download_gamp_data.py  --  Download GNSS obs & products for GAMP PPP

Downloads from CDDIS (NASA) using your NASA Earthdata login.
Files are saved to:
    data/           <- observation file (RINEX 2, .{yy}o)
    products/nav/   <- broadcast navigation (RINEX 2 mixed, brdm{doy}0.{yy}p)
    products/sp3/   <- precise orbits
    products/clk/   <- precise clocks
    products/erp/   <- earth rotation
    products/ionex/ <- IONEX TEC maps
    products/dcb/   <- differential code biases

RINEX 2 vs RINEX 3
------------------
RINEX 3 was formalised in 2007 (3.03 in 2015) and became CDDIS primary ~2018.
However, CDDIS still provides RINEX 2 obs files in parallel /{YY}o/ folders
for most stations, even for 2026 dates.  This script downloads RINEX 2 obs
(*.{yy}o) because:
  - No Hatanaka decompression needed (no crx2rnx tool required)
  - No trailing-record stripping needed (GAMP bug only hits RINEX 3)
  - Short 4-char station name already matches GAMP auto-detection

Product naming changes by era:
  pre-2020 (GPS week < 2060):  cod{week}{dow}.sp3    <- already GAMP-native
  post-2020 (GPS week >= 2060): COD0MGXFIN_...SP3.gz  <- wizard renames these

REQUIREMENTS
    pip install requests
    NASA Earthdata account (free): https://urs.earthdata.nasa.gov/
    Add to ~/.netrc (recommended):
        machine urs.earthdata.nasa.gov login <user> password <pass>
    OR set env vars: CDDIS_USER and CDDIS_PASS

USAGE
    python scripts/download_gamp_data.py
    python scripts/download_gamp_data.py --year 2017 --doy 244 --station cut0
    python scripts/download_gamp_data.py --year 2026 --doy 15  --station hkws

EXAMPLE  (matches GAMP example dataset)
    python scripts/download_gamp_data.py --year 2017 --doy 244 --station cut0
    python scripts/run_gamp.py
    -> select cut02440.17o, scenario B or C
"""

import argparse
import gzip
import netrc
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import date, timedelta
from getpass import getpass
from pathlib import Path
from urllib.parse import urlparse

try:
    import requests
    from requests.auth import HTTPBasicAuth
except ImportError:
    print("ERROR: 'requests' not installed.\n  Run: pip install requests")
    sys.exit(1)

# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PROD_DIR = ROOT / "products"
CDDIS = "https://cddis.nasa.gov/archive"

# GPS week threshold: below = old RINEX 2 product names (already GAMP-native)
#                    above = new RINEX 3 long names (wizard renames for GAMP)
# Week 2060 ~ January 2020
R2_PRODUCT_WEEK_MAX = 2060

ANSI = sys.stdout.isatty()
GREEN = "\033[92m" if ANSI else ""
YELLOW = "\033[93m" if ANSI else ""
RED = "\033[91m" if ANSI else ""
DIM = "\033[2m" if ANSI else ""
BOLD = "\033[1m" if ANSI else ""
RESET = "\033[0m" if ANSI else ""

# Station 9-char hints for RINEX-3 obs fallback names.
# CDDIS RINEX-3 filenames require full site+domes country code (e.g. HKWS00HKG).
STATION_RINEX3_HINTS = {
    "HKWS": ["HKWS00HKG"],
    "ZIM2": ["ZIM200CHE"],
    "ZIMM": ["ZIMM00CHE"],
}


# ===========================================================================
# GPS calendar
# ===========================================================================

def gps_week_dow(year: int, doy: int):
    """Return (GPS_week, day_of_week) where 0=Sunday ... 6=Saturday."""
    GPS_EPOCH = date(1980, 1, 6)
    d = date(year, 1, 1) + timedelta(days=doy - 1)
    delta = (d - GPS_EPOCH).days
    return delta // 7, delta % 7


def get_adjacent_doy(year: int, doy: int, offset: int):
    """Return (year, doy) shifted by offset days with year rollover support."""
    d = date(year, 1, 1) + timedelta(days=doy - 1 + offset)
    return d.year, d.timetuple().tm_yday


# ===========================================================================
# Authentication
# ===========================================================================

def get_credentials():
    """Return (username, password) from .netrc, env vars, or interactive."""
    user = os.environ.get("CDDIS_USER") or os.environ.get("EARTHDATA_USER")
    pw = os.environ.get("CDDIS_PASS") or os.environ.get("EARTHDATA_PASS")
    if user and pw:
        print(f"  Using credentials from environment variables.")
        return user, pw
    try:
        n = netrc.netrc()
        auth = n.authenticators("urs.earthdata.nasa.gov")
        if auth:
            print(f"  Using credentials from ~/.netrc.")
            return auth[0], auth[2]
    except Exception:
        pass
    print(f"\n  {YELLOW}NASA Earthdata credentials required.{RESET}")
    print(f"  Register free at: https://urs.earthdata.nasa.gov/")
    print(f"  Tip: add to ~/.netrc:  "
          f"machine urs.earthdata.nasa.gov login <u> password <p>")
    user = input("  Username: ").strip()
    pw = getpass("  Password: ")
    return user, pw


class _EarthdataSession(requests.Session):
    """Session that reattaches auth when NASA URS redirect returns to CDDIS."""

    def rebuild_auth(self, prepared_request, response):
        headers = prepared_request.headers
        if "Authorization" in headers:
            orig = urlparse(response.request.url)
            redir = urlparse(prepared_request.url)
            # Drop auth only if leaving both the original host AND URS
            if (orig.hostname != redir.hostname
                    and "urs.earthdata.nasa.gov" not in redir.hostname):
                del headers["Authorization"]


def make_session(user: str, pw: str) -> requests.Session:
    s = _EarthdataSession()
    s.auth = HTTPBasicAuth(user, pw)
    return s


# ===========================================================================
# Decompression
# ===========================================================================

def _decompress_gz(src: Path) -> Path:
    out = src.with_suffix("")
    with gzip.open(src, "rb") as fin, open(out, "wb") as fout:
        shutil.copyfileobj(fin, fout)
    src.unlink()
    return out


def _decompress_Z(src: Path) -> Path:
    """Decompress .Z (LZW) using 7-Zip. Returns decompressed path or src."""
    out = src.with_suffix("")
    candidates = [
        r"C:\Program Files\7-Zip\7z.exe",
        r"C:\Program Files (x86)\7-Zip\7z.exe",
        "7z",
    ]
    for exe in candidates:
        try:
            ret = subprocess.run(
                [exe, "e", str(src), f"-o{src.parent}", "-y"],
                capture_output=True, text=True,
            )
            if ret.returncode == 0 and out.exists():
                src.unlink()
                return out
        except FileNotFoundError:
            continue
    print(f"  {YELLOW}  Cannot decompress {src.name} — 7-Zip not found.{RESET}")
    print(f"  {DIM}  Install from https://7-zip.org/ then rerun, or decompress manually.{RESET}")
    return src  # return .Z as-is


def decompress(src: Path) -> Path:
    """Decompress .gz or .Z file. Returns path to decompressed file."""
    if src.suffix == ".gz":
        result = _decompress_gz(src)
        print(f"    -> {result.name}")
        return result
    if src.suffix == ".Z":
        result = _decompress_Z(src)
        if result != src:
            print(f"    -> {result.name}")
        return result
    return src


# ===========================================================================
# HTTP download
# ===========================================================================

def _download_raw(session: requests.Session, url: str, dest: Path,
                  max_attempts: int = 6) -> bool:
    """Download URL to dest with retry.

    Returns True on success, False on 404/error after retries.
    """
    part = dest.with_name(dest.name + ".part")
    for attempt in range(1, max_attempts + 1):
        ok = False
        existing = part.stat().st_size if part.exists() else 0
        headers = {}
        mode = "ab" if existing else "wb"
        if existing:
            headers["Range"] = f"bytes={existing}-"
        try:
            with session.get(url, stream=True, timeout=90, headers=headers) as r:
                if r.status_code == 404:
                    return False

                if r.status_code not in (200, 206):
                    print(f"  {YELLOW}  HTTP {r.status_code}{RESET}: {url.split('/')[-1]}"
                          f" {DIM}(attempt {attempt}/{max_attempts}){RESET}")
                    continue

                # Server ignored our Range request: restart full download cleanly.
                if existing and r.status_code == 200:
                    existing = 0
                    mode = "wb"
                    part.unlink(missing_ok=True)

                expected_total = None
                if r.status_code == 206:
                    content_range = r.headers.get("Content-Range", "")
                    m = re.match(r"bytes\s+\d+-\d+/(\d+)", content_range)
                    if m:
                        expected_total = int(m.group(1))
                else:
                    content_length = r.headers.get("Content-Length")
                    if content_length:
                        expected_total = existing + int(content_length)

                dest.parent.mkdir(parents=True, exist_ok=True)
                with open(part, mode) as f:
                    for chunk in r.iter_content(chunk_size=131072):
                        if chunk:
                            f.write(chunk)

                actual_size = part.stat().st_size
                if expected_total is not None and actual_size < expected_total:
                    print(f"  {YELLOW}  incomplete transfer{RESET}: {dest.name}"
                          f" {DIM}({actual_size // 1024}/{expected_total // 1024} KB,"
                          f" attempt {attempt}/{max_attempts}){RESET}")
                    continue

                part.replace(dest)
                ok = True
                kb = dest.stat().st_size // 1024
                print(
                    f"  {GREEN}  downloaded{RESET}  {dest.name}  {DIM}({kb} KB){RESET}")
                return True

        except requests.exceptions.RequestException as exc:
            print(f"  {YELLOW}  transient download error{RESET}: {exc}"
                  f" {DIM}(attempt {attempt}/{max_attempts}){RESET}")

        if attempt < max_attempts:
            time.sleep(1.2 * attempt)

    return False


def try_urls(session: requests.Session, urls: list, dest_dir: Path,
             label: str, silent404: bool = False) -> Path | None:
    """Try each URL. Download + decompress first successful one.

    silent404: if True, suppress the 'not found' message (used when a
               caller will try a fallback URL set).
    """
    for url in urls:
        fname = url.split("/")[-1]
        compressed = dest_dir / fname
        if _download_raw(session, url, compressed):
            return decompress(compressed)
    if not silent404:
        print(
            f"  {YELLOW}  {label}: not found on CDDIS (tried {len(urls)} URLs){RESET}")
    return None


def _rnx3_station_candidates(station: str) -> list[str]:
    """Return likely 9-char station identifiers used in RINEX-3 filenames."""
    st4 = station.upper()[:4]
    cands = []
    # Known exact mappings first.
    cands.extend(STATION_RINEX3_HINTS.get(st4, []))
    # Generic fallbacks if specific code unknown.
    cands.extend([f"{st4}00XXX", f"{st4}00IGS", f"{st4}00000"])
    # Deduplicate while preserving order.
    uniq = []
    for c in cands:
        if c not in uniq:
            uniq.append(c)
    return uniq


# ===========================================================================
# Per-product download functions
# ===========================================================================

def download_obs(session, year: int, doy: int, station: str,
                 dest_dir: Path) -> Path | None:
    """Observation file.  Tries RINEX 2 first, falls back to RINEX 3.

    RINEX 2 ({site4}{doy}0.{yy}o):
      - Preferred for GAMP: no trailing-record stripping needed
      - Available for most stations even in 2026 (e.g. zim20150.26o.gz)
      - Some modern stations (e.g. HKWS) only provide RINEX 3 after ~2019

    RINEX 3 (site9_R_{year}{doy}...MO.rnx.gz / .crx.gz):
      - run_gamp.py wizard strips trailing records before passing to GAMP
      - crx (Hatanaka compressed) requires crx2rnx — NOT handled here;
        only .rnx.gz (already uncompressed RINEX) is tried.
    """
    yy = year % 100
    site = station.lower()[:4]

    # --- RINEX 2 ---
    base_r2 = f"{CDDIS}/gnss/data/daily/{year}/{doy:03d}/{yy:02d}o"
    fn_r2 = f"{site}{doy:03d}0.{yy:02d}o"
    result = try_urls(session, [
        f"{base_r2}/{fn_r2}.gz",
        f"{base_r2}/{fn_r2}.Z",
    ], dest_dir, f"obs RINEX 2 ({fn_r2})", silent404=True)
    if result:
        return result

    # --- RINEX 3 fallback (.rnx only — crx/Hatanaka not handled) ---
    print(f"  {DIM}  RINEX 2 not found — trying RINEX 3 (.rnx.gz) ...{RESET}")
    yy = year % 100
    base_candidates = [
        f"{CDDIS}/gnss/data/daily/{year}/{doy:03d}/rnx",
        f"{CDDIS}/gnss/data/daily/{year}/{doy:03d}/{yy:02d}o",
    ]
    urls = []
    for site9 in _rnx3_station_candidates(station):
        fn_r3 = f"{site9}_R_{year:04d}{doy:03d}0000_01D_30S_MO.rnx.gz"
        for base_r3 in base_candidates:
            urls.append(f"{base_r3}/{fn_r3}")

    result = try_urls(session, urls, dest_dir,
                      f"obs RINEX 3 ({station.upper()})")
    if result:
        print(
            f"  {DIM}  Note: RINEX 3 obs — wizard will strip trailing records for GAMP{RESET}")
    return result


def download_nav(session, year: int, doy: int, dest_dir: Path) -> Path | None:
    """Broadcast navigation with RINEX-2 and RINEX-3 fallbacks.

    Preferred target is mixed nav that run_gamp.py can rename to brdm{DOY}0.{YY}p.
    """
    yy = year % 100
    ddd = f"{doy:03d}"
    base_p = f"{CDDIS}/gnss/data/daily/{year}/{ddd}/{yy:02d}p"
    base_n = f"{CDDIS}/gnss/data/daily/{year}/{ddd}/{yy:02d}n"
    base_rnx = f"{CDDIS}/gnss/data/daily/{year}/{ddd}/rnx"
    base_brdc = f"{CDDIS}/gnss/data/daily/{year}/{ddd}/brdc"

    fn_r2 = f"brdm{ddd}0.{yy:02d}p"
    fn_r3_a = f"BRD400DLR_S_{year:04d}{ddd}0000_01D_MN.rnx.gz"
    fn_r3_b = f"BRDC00IGS_R_{year:04d}{ddd}0000_01D_MN.rnx.gz"

    urls = [
        f"{base_p}/{fn_r2}.gz",
        f"{base_p}/{fn_r2}.Z",
        f"{base_n}/{fn_r2}.gz",
        f"{base_n}/{fn_r2}.Z",
        f"{base_p}/{fn_r3_a}",
        f"{base_p}/{fn_r3_b}",
        f"{base_brdc}/{fn_r3_a}",
        f"{base_brdc}/{fn_r3_b}",
        f"{base_rnx}/{fn_r3_a}",
        f"{base_rnx}/{fn_r3_b}",
    ]
    return try_urls(session, urls, dest_dir,
                    f"nav mixed broadcast ({fn_r2} / BRD400DLR / BRDC00IGS)")


def download_sp3(session, year: int, doy: int, week: int, dow: int,
                 dest_dir: Path) -> Path | None:
    """CODE precise orbits SP3.

    Old style (week < 2060): cod{week}{dow}.sp3  <- already GAMP-native
    New style (week >= 2060): COD0MGXFIN_...SP3  <- wizard renames for GAMP
    """
    urls = [
        # Old RINEX 2 style (pre-~2020) — already GAMP-compatible filename
        f"{CDDIS}/gnss/products/{week:04d}/cod{week:04d}{dow}.sp3.Z",
        f"{CDDIS}/gnss/products/{week:04d}/cod{week:04d}{dow}.sp3.gz",
        # New RINEX 3 style (post-~2020) — wizard will rename for GAMP
        f"{CDDIS}/gnss/products/{week:04d}/COD0MGXFIN_{year:04d}{doy:03d}0000_01D_05M_ORB.SP3.gz",
        f"{CDDIS}/gnss/products/{week:04d}/COD0OPSFIN_{year:04d}{doy:03d}0000_01D_05M_ORB.SP3.gz",
        f"{CDDIS}/gnss/products/{week:04d}/IGS0OPSFIN_{year:04d}{doy:03d}0000_01D_15M_ORB.SP3.gz",
        f"{CDDIS}/gnss/products/{week:04d}/IGS0OPSRAP_{year:04d}{doy:03d}0000_01D_15M_ORB.SP3.gz",
    ]
    return try_urls(session, urls, dest_dir, "SP3 (CODE orbits)")


def download_clk(session, year: int, doy: int, week: int, dow: int,
                 dest_dir: Path) -> Path | None:
    """CODE precise clocks CLK (30s interval)."""
    urls = [
        f"{CDDIS}/gnss/products/{week:04d}/cod{week:04d}{dow}.clk.Z",
        f"{CDDIS}/gnss/products/{week:04d}/cod{week:04d}{dow}.clk.gz",
        f"{CDDIS}/gnss/products/{week:04d}/COD0MGXFIN_{year:04d}{doy:03d}0000_01D_30S_CLK.CLK.gz",
        f"{CDDIS}/gnss/products/{week:04d}/COD0OPSFIN_{year:04d}{doy:03d}0000_01D_30S_CLK.CLK.gz",
        f"{CDDIS}/gnss/products/{week:04d}/IGS0OPSFIN_{year:04d}{doy:03d}0000_01D_30S_CLK.CLK.gz",
        f"{CDDIS}/gnss/products/{week:04d}/IGS0OPSRAP_{year:04d}{doy:03d}0000_01D_05M_CLK.CLK.gz",
    ]
    return try_urls(session, urls, dest_dir, "CLK (CODE clocks 30s)")


def download_erp(session, year: int, doy: int, week: int,
                 dest_dir: Path) -> Path | None:
    """CODE earth rotation parameters.

    Old style: cod{week}7.erp (one per week, '7' is GAMP convention)
    New style: daily ERP file (wizard renames to cod{week}7.erp for GAMP)
    """
    urls = [
        f"{CDDIS}/gnss/products/{week:04d}/cod{week:04d}7.erp.Z",
        f"{CDDIS}/gnss/products/{week:04d}/cod{week:04d}7.erp.gz",
        f"{CDDIS}/gnss/products/{week:04d}/COD0MGXFIN_{year:04d}{doy:03d}0000_01D_12H_ERP.ERP.gz",
        f"{CDDIS}/gnss/products/{week:04d}/COD0OPSFIN_{year:04d}{doy:03d}0000_07D_01D_ERP.ERP.gz",
    ]
    return try_urls(session, urls, dest_dir, "ERP (CODE earth rotation)")


def download_ionex(session, year: int, doy: int, dest_dir: Path) -> Path | None:
    """CODE IONEX global ionosphere map.

    Old style: codg{doy}0.{yy}i  (from /ionosphere/ path)
    New style: COD0OPSFIN_...GIM.INX  (from /ionex/ path)
    """
    yy = year % 100
    # Old IONEX path uses "ionosphere" not "ionex"
    base_old = f"{CDDIS}/gnss/products/ionosphere/{year}/{doy:03d}"
    fn_old = f"codg{doy:03d}0.{yy:02d}i"
    # New IONEX path uses "ionex"
    base_new = f"{CDDIS}/gnss/products/ionex/{year}/{doy:03d}"
    urls = [
        f"{base_old}/{fn_old}.Z",
        f"{base_old}/{fn_old}.gz",
        f"{base_new}/COD0OPSFIN_{year:04d}{doy:03d}0000_01D_01H_GIM.INX.gz",
        f"{base_new}/COD0OPSRAP_{year:04d}{doy:03d}0000_01D_01H_GIM.INX.gz",
        f"{base_new}/COD0MGXFIN_{year:04d}{doy:03d}0000_01D_01H_GIM.INX.gz",
    ]
    return try_urls(session, urls, dest_dir, "IONEX (CODE GIM)")


def download_dcb(session, year: int, doy: int, week: int,
                 dest_dir: Path) -> Path | None:
    """CAS differential code biases (BSX format required by GAMP).

    BSX format from CAS MGEX — available from CDDIS MGEX products archive.
    NOTE: newer CAS files (.BIA / OSB format) are NOT compatible with GAMP.
    """
    urls = [
        # MGEX DCB archive (BSX format)
        f"{CDDIS}/gnss/products/mgex/{week:04d}/CAS0MGXRAP_{year:04d}{doy:03d}0000_01D_01D_DCB.BSX.gz",
        f"{CDDIS}/gnss/products/mgex/dcb/{year}/CAS0MGXRAP_{year:04d}{doy:03d}0000_01D_01D_DCB.BSX.gz",
        f"{CDDIS}/gnss/products/bias/{year}/CAS0MGXRAP_{year:04d}{doy:03d}0000_01D_01D_DCB.BSX.gz",
        f"{CDDIS}/gnss/products/bias/{year}/CAS0OPSRAP_{year:04d}{doy:03d}0000_01D_01D_DCB.BSX.gz",
        # Bias product archive
        f"{CDDIS}/gnss/products/bias/{year}/DLR0MGXFIN_{year:04d}0010000_03L_01D_DCB.BSX.gz",
    ]
    result = try_urls(session, urls, dest_dir, "DCB (CAS MGEX BSX)")
    if result is None:
        print(
            f"  {DIM}  DCB is optional for scenario C/D. GAMP will run without it.{RESET}")
    return result


# ===========================================================================
# Main
# ===========================================================================

def parse_args():
    p = argparse.ArgumentParser(
        description="Download RINEX 2 obs + products for GAMP PPP")
    p.add_argument("--year",    type=int, help="Year  (e.g. 2017)")
    p.add_argument("--doy",     type=int, help="Day of year  (e.g. 244)")
    p.add_argument("--station", type=str,
                   help="4-char station name  (e.g. cut0)")
    p.add_argument("--scenario", choices=["A", "B", "C", "D"], default=None,
                   help="GAMP scenario — determines which products to download")
    p.add_argument("--no-obs",   action="store_true",
                   help="Skip observation file")
    p.add_argument("--no-ionex", action="store_true",
                   help="Skip IONEX download")
    p.add_argument("--no-dcb",   action="store_true", help="Skip DCB download")
    return p.parse_args()


def main():
    args = parse_args()

    print(f"\n{BOLD}  GAMP Data Download{RESET}")
    print(f"  {'='*50}")
    print(f"  Project root: {ROOT}")

    # ---- Date ----
    year = args.year
    doy = args.doy
    if not year or not doy:
        print(f"\n  Enter date to download (e.g. 2017/244 = GAMP example dataset):")
        year = int(input(f"    Year [2017]: ").strip() or "2017")
        doy = int(input(f"    DOY  [244]:  ").strip() or "244")

    week, dow = gps_week_dow(year, doy)
    obs_date = date(year, 1, 1) + timedelta(days=doy - 1)
    dow_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    era = "RINEX-2 product names (already GAMP-native)" \
        if week < R2_PRODUCT_WEEK_MAX \
        else "RINEX-3 product names (wizard renames for GAMP)"

    print(
        f"\n  Date       : {year}/{doy:03d}  ({obs_date.strftime('%Y-%m-%d')})")
    print(f"  GPS week   : {week}, DOW {dow} ({dow_names[dow]})")
    print(f"  Product era: {era}")

    # ---- Station ----
    station = (args.station or "").strip().lower()
    if not station:
        station = input(
            f"\n  Station (4-char, e.g. cut0, hkws, zim2): ").strip().lower()
    station = station[:4]
    print(f"  Station    : {station}")

    # ---- Scenario ----
    scenario = args.scenario
    if not scenario:
        print(f"\n  Scenario:")
        print(f"    A = SPP (broadcast nav only, no precise products)")
        print(f"    B = GPS-only precise PPP (IF12)")
        print(f"    C = Multi-GNSS precise PPP (recommended)  <- GAMP default")
        print(f"    D = Multi-GNSS + external IONEX")
        scenario = input(f"  Choose [C]: ").strip().upper() or "C"

    needs_precise = scenario in ("B", "C", "D")
    needs_dcb = scenario in ("C", "D")
    needs_ionex = scenario == "D"

    # ---- Credentials ----
    print()
    user, pw = get_credentials()
    session = make_session(user, pw)

    # ---- Download ----
    print(f"\n  {BOLD}Downloading ...{RESET}\n")
    results = {}

    # Observation
    if not args.no_obs:
        print(f"  [obs]")
        results["obs"] = download_obs(session, year, doy, station, DATA_DIR)

    # Navigation
    print(f"\n  [nav]")
    results["nav"] = download_nav(session, year, doy, PROD_DIR / "nav")

    if needs_precise:
        # GAMP internally expands processing window by ±2.5 hours, so day-1/day+1
        # SP3/CLK files are needed in addition to the target day.
        print(f"\n  [sp3]  (3 consecutive days: doy-1, doy, doy+1)")
        results["sp3"] = None
        for off, label in [(-1, "day-1"), (0, "day0"), (1, "day+1")]:
            y2, d2 = get_adjacent_doy(year, doy, off)
            w2, dw2 = gps_week_dow(y2, d2)
            p = download_sp3(session, y2, d2, w2, dw2, PROD_DIR / "sp3")
            if off == 0:
                results["sp3"] = p
            if p:
                print(f"    {label}: {p.name}")

        print(f"\n  [clk]  (3 consecutive days: doy-1, doy, doy+1)")
        results["clk"] = None
        for off, label in [(-1, "day-1"), (0, "day0"), (1, "day+1")]:
            y2, d2 = get_adjacent_doy(year, doy, off)
            w2, dw2 = gps_week_dow(y2, d2)
            p = download_clk(session, y2, d2, w2, dw2, PROD_DIR / "clk")
            if off == 0:
                results["clk"] = p
            if p:
                print(f"    {label}: {p.name}")

        # ERP remains single-day.
        print(f"\n  [erp]")
        results["erp"] = download_erp(
            session, year, doy, week, PROD_DIR / "erp")

    if needs_dcb and not args.no_dcb:
        print(f"\n  [dcb]")
        results["dcb"] = download_dcb(
            session, year, doy, week, PROD_DIR / "dcb")

    if needs_ionex and not args.no_ionex:
        print(f"\n  [ionex]")
        results["ionex"] = download_ionex(
            session, year, doy, PROD_DIR / "ionex")

    # ---- Summary ----
    print(f"\n  {BOLD}Summary:{RESET}")
    ok = [k for k, v in results.items() if v is not None]
    fail = [k for k, v in results.items() if v is None]
    for k in ok:
        p = results[k]
        ext = p.suffix
        note = ""
        if ext == ".Z":
            note = f"  {YELLOW}(still compressed — install 7-Zip to decompress){RESET}"
        print(f"    {GREEN}OK{RESET}  {k:<8s}  {p.relative_to(ROOT)}{note}")
    for k in fail:
        print(f"    {YELLOW}--{RESET}  {k:<8s}  not downloaded")

    if fail:
        print(
            f"\n  {YELLOW}Note: missing products will be skipped by run_gamp.py.{RESET}")

    print(f"\n  {BOLD}Next steps:{RESET}")
    print(f"    python scripts/run_gamp.py")
    if results.get("obs"):
        obs_name = results["obs"].name
        print(f"    -> Select obs: {obs_name}  (in data/)")
    if week < R2_PRODUCT_WEEK_MAX:
        print(
            f"    -> Old-style products (cod{week:04d}{dow}.sp3 etc.) are already")
        print(f"       in GAMP-native format — no renaming needed by the wizard.")
    print()


if __name__ == "__main__":
    main()
