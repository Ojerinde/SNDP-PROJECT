#!/usr/bin/env python3
"""
run_rtklib.py  —  Interactive RTKLIB PPP Run Wizard

Automates all 5 research experiments using RTKLIB-EX 2.5.0 (or 2.4.3).
Generates .conf configuration files and runs rnx2rtkp.exe in batch mode.

USAGE (always run from C:\\PPP_PROJECT):
    python scripts/run_rtklib.py

Results are saved to:
    RTKLIB_work/runs/<station>_<EXP>_<label>_<timestamp>/

EXPERIMENT 2 SPECIAL HANDLING:
    When Exp2 is selected, the script automatically creates separate folders
    for each constellation combination (2A/2B/2C/2D):
        - KIRU_EXP2_2A_<timestamp>/   (GPS only)
        - KIRU_EXP2_2B_<timestamp>/   (GPS + Galileo)
        - KIRU_EXP2_2C_<timestamp>/   (GPS + Galileo + BeiDou)
        - KIRU_EXP2_2D_<timestamp>/   (All systems)
    Each contains its own .pos output and run.conf configuration file.

To plot afterwards in RTKPLOT:
    File -> Open Solution -> select the .pos file in the run folder
    Edit -> Options -> set Reference Position to the station's known coordinates.

For PPP-AR (Experiment 3), RTKLIB-EX 2.5.0 is required.
For all other experiments, either RTKLIB 2.4.3 or 2.5.0 works.

NOTES:
  - rnx2rtkp.exe is the command-line equivalent of the RTKPOST GUI.
  - The .conf file generated for each run can be loaded in the RTKPOST GUI with
    Options -> Load to review or re-run interactively.
  - Results include the .conf and all input file paths for full reproducibility.
"""

import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent   # C:\PPP_PROJECT
RUNS_DIR = ROOT / "RTKLIB_work" / "runs"

# Prefer RTKLIB-EX 2.5.0 (demo5) — has PPP-AR support via BIA files
RNX2RTKP_EX = Path(r"C:\Program Files\RTKLIB_EX_2.5.0\rnx2rtkp.exe")
RNX2RTKP_243 = Path(r"C:\Program Files\RTKLIB\bin\rnx2rtkp.exe")
RTKPLOT_EX = Path(r"C:\Program Files\RTKLIB_EX_2.5.0\rtkplot.exe")

# ── ANSI colours (Windows 10+) ────────────────────────────────────────────────
BOLD = "\033[1m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
DIM = "\033[2m"
RESET = "\033[0m"

# ── Dataset definitions ───────────────────────────────────────────────────────
NEW_DATA_DIR = ROOT / "New_Data"
OLD_DATA_DIR = ROOT / "Old_data"

DATASETS = {
    "new": {
        "label": "New_Data  (KIRU/WUH2 — recommended to start)",
        "obs_dir": NEW_DATA_DIR / "obs" / "RNXDATA",
        "nav_dir": NEW_DATA_DIR / "nav",
        "prod_dir": NEW_DATA_DIR / "DATA_FINAL_ANT_EXTRA",
        "sp3":  "COD0MGXFIN_20260150000_01D_05M_ORB.SP3",
        "clk":  "COD0MGXFIN_20260150000_01D_30S_CLK.CLK",
        "bia":  "COD0MGXFIN_20260150000_01D_01D_OSB.BIA",
        "atx":  "igs20_2401.atx",
        "nav":  "BRDC00IGS_R_20260150000_01D_MN.rnx",
        "stations": {
            "KIRU": {
                "obs":  "KIRU00SWE_R_20260150000_01D_30S_MO.rnx",
                "lat":  67.857900, "lon": 20.967800, "hgt": 390.900,
                "desc": "Kiruna, Sweden  (high-latitude, polar)"
            },
            "WUH2": {
                "obs":  "WUH200CHN_R_20260150000_01D_30S_MO.rnx",
                "lat":  30.531700, "lon": 114.357000, "hgt":  73.400,
                "desc": "Wuhan, China  (mid-latitude, continental)"
            },
        },
    },
    "old": {
        "label": "Old_Data  (ZIM2/HKWS)",
        "obs_dir": OLD_DATA_DIR / "data",
        "nav_dir": OLD_DATA_DIR / "products" / "nav",
        "prod_dir": OLD_DATA_DIR / "products",
        "sp3":  "sp3/COD0MGXFIN_20260150000_01D_05M_ORB.SP3",
        "clk":  "clk/COD0MGXFIN_20260150000_01D_30S_CLK.CLK",
        "bia":  "bia/COD0MGXFIN_20260150000_01D_01D_OSB.BIA",
        "atx":  "atx/igs20_2401.atx",
        "nav":  "BRDC00IGS_R_20260150000_01D_MN.rnx",
        "ionex": "ionex/COD0OPSFIN_20260150000_01D_01H_GIM.INX",
        "stations": {
            "ZIM2": {
                "obs":  "ZIM200CHE_R_20260150000_01D_30S_MO.rnx",
                "lat":  46.877100, "lon":   7.465000, "hgt": 956.400,
                "desc": "Zimmerwald, Switzerland  (mid-latitude, Europe)"
            },
            "HKWS": {
                "obs":  "HKWS00HKG_R_20260150000_01D_30S_MO.rnx",
                "lat":  22.272200, "lon": 114.161400, "hgt":  72.000,
                "desc": "Hong Kong  (low-latitude, coastal)"
            },
        },
    },
}

# ── Experiment definitions ────────────────────────────────────────────────────
# posmode: ppp-static  |  ionoopt: brdc/dual-freq/ionex-tec  |  navsys bitmask
# navsys: 1=GPS 4=GLO 8=GAL 16=QZS 32=BDS  (add for multi-GNSS)
EXPERIMENTS = {
    "1A": dict(
        name="Experiment 1A — Broadcast Ephemeris (Baseline SPP/PPP)",
        desc="GPS only · broadcast nav only · ~1–5 m | baseline comparison",
        posmode="ppp-static",
        freqmode="l1+l2",
        sateph="brdc",        # broadcast
        ionoopt="brdc",        # Klobuchar
        tropopt="saas",
        navsys=1,             # GPS only
        armode="off",
        posopt=False,         # no ATX file — Sat PCV, Rec PCV, PhWU all OFF
        needs_sp3=False, needs_clk=False, needs_bia=False, needs_ionex=False,
    ),
    "1B": dict(
        name="Experiment 1B — Precise Ephemeris (Standard Float PPP)",
        desc="GPS only · precise SP3+CLK · ~5–15 cm | compare with 1A",
        posmode="ppp-static",
        freqmode="l1+l2",
        sateph="prec",        # precise
        ionoopt="dual-freq",   # ionosphere-free combination
        tropopt="saas",
        navsys=1,             # GPS only
        armode="off",
        needs_sp3=True, needs_clk=True, needs_bia=False, needs_ionex=False,
    ),
    "2A": dict(
        name="Experiment 2A — GPS Only",
        desc="GPS only · precise · convergence baseline",
        posmode="ppp-static",
        freqmode="l1+l2",
        sateph="prec",
        ionoopt="dual-freq",
        tropopt="saas",
        navsys=1,             # GPS only
        armode="off",
        needs_sp3=True, needs_clk=True, needs_bia=False, needs_ionex=False,
    ),
    "2B": dict(
        name="Experiment 2B — GPS + Galileo",
        desc="GPS+GAL · precise · faster convergence expected",
        posmode="ppp-static",
        freqmode="l1+l2",
        sateph="prec",
        ionoopt="dual-freq",
        tropopt="saas",
        navsys=1 + 8,         # GPS(1) + Galileo(8) = 9
        armode="off",
        needs_sp3=True, needs_clk=True, needs_bia=False, needs_ionex=False,
    ),
    "2C": dict(
        name="Experiment 2C — GPS + Galileo + BDS (Recommended Multi-GNSS)",
        desc="GPS+GAL+BDS · precise · best convergence in this set",
        posmode="ppp-static",
        freqmode="l1+l2",
        sateph="prec",
        ionoopt="dual-freq",
        tropopt="saas",
        navsys=1 + 8 + 32,   # GPS(1) + Galileo(8) + BDS(32) = 41
        armode="off",
        needs_sp3=True, needs_clk=True, needs_bia=False, needs_ionex=False,
    ),
    "2D": dict(
        name="Experiment 2D — All Systems (GPS+GLO+GAL+QZSS+BDS)",
        desc="All constellations · precise · maximum satellite count",
        posmode="ppp-static",
        freqmode="l1+l2",
        sateph="prec",
        ionoopt="dual-freq",
        tropopt="saas",
        navsys=1 + 4 + 8 + 16 + 32,  # GPS+GLO+GAL+QZS+BDS = 61
        armode="off",
        needs_sp3=True, needs_clk=True, needs_bia=False, needs_ionex=False,
    ),
    "3A": dict(
        name="Experiment 3A — Float PPP (No AR)",
        desc="GPS+GAL+BDS · precise · float ambiguities | convergence baseline",
        posmode="ppp-static",
        freqmode="l1+l2",
        sateph="prec",
        ionoopt="dual-freq",
        tropopt="saas",
        navsys=1 + 8 + 32,
        armode="off",         # Float — no AR
        needs_sp3=True, needs_clk=True, needs_bia=False, needs_ionex=False,
    ),
    "3B": dict(
        name="Experiment 3B — PPP-AR (Integer Ambiguity Resolution)",
        desc="GPS+GAL+BDS · precise + BIA · fixed ambiguities | RTKLIB-EX 2.5.0 only",
        posmode="ppp-static",
        freqmode="l1+l2",
        sateph="prec",
        ionoopt="dual-freq",
        tropopt="saas",
        navsys=1 + 8 + 32,
        armode="cont",        # Continuous AR
        needs_sp3=True, needs_clk=True, needs_bia=True, needs_ionex=False,
    ),
    "4A": dict(
        name="Experiment 4A — Single-Frequency + Klobuchar Ionosphere",
        desc="GPS · L1 only · Klobuchar iono model · broadcast ephemeris",
        posmode="ppp-static",
        freqmode="l1",
        sateph="brdc",
        ionoopt="brdc",        # Klobuchar
        tropopt="saas",
        navsys=1,
        armode="off",
        posopt=False,         # no ATX file — Sat PCV, Rec PCV, PhWU all OFF
        needs_sp3=False, needs_clk=False, needs_bia=False, needs_ionex=False,
    ),
    "4B": dict(
        name="Experiment 4B — Dual-Frequency Ionosphere-Free (Standard)",
        desc="GPS+GAL+BDS · L1+L2 · IF combination · precise ephemeris",
        posmode="ppp-static",
        freqmode="l1+l2",
        sateph="prec",
        ionoopt="dual-freq",
        tropopt="saas",
        navsys=1 + 8 + 32,
        armode="off",
        needs_sp3=True, needs_clk=True, needs_bia=False, needs_ionex=False,
    ),
    "4C": dict(
        name="Experiment 4C — Single-Frequency + IONEX GIM",
        desc="GPS · L1 only · external IONEX GIM · broadcast ephemeris",
        posmode="ppp-static",
        freqmode="l1",
        sateph="brdc",
        ionoopt="ionex-tec",   # External GIM
        tropopt="saas",
        navsys=1,
        armode="off",
        posopt=False,         # no ATX file — Sat PCV, Rec PCV, PhWU all OFF
        needs_sp3=False, needs_clk=False, needs_bia=False, needs_ionex=True,
    ),
    # Session length experiments — same settings as 2C but with time windows
    "5A": dict(
        name="Experiment 5A — 1-Hour Session",
        desc="GPS+GAL+BDS · precise · 00:00–01:00 UTC",
        posmode="ppp-static",
        freqmode="l1+l2",
        sateph="prec",
        ionoopt="dual-freq",
        tropopt="saas",
        navsys=1 + 8 + 32,
        armode="off",
        needs_sp3=True, needs_clk=True, needs_bia=False, needs_ionex=False,
        te="2026/01/15 01:00:00",
    ),
    "5B": dict(
        name="Experiment 5B — 2-Hour Session",
        desc="GPS+GAL+BDS · precise · 00:00–02:00 UTC",
        posmode="ppp-static",
        freqmode="l1+l2",
        sateph="prec",
        ionoopt="dual-freq",
        tropopt="saas",
        navsys=1 + 8 + 32,
        armode="off",
        needs_sp3=True, needs_clk=True, needs_bia=False, needs_ionex=False,
        te="2026/01/15 02:00:00",
    ),
    "5C": dict(
        name="Experiment 5C — 4-Hour Session",
        desc="GPS+GAL+BDS · precise · 00:00–04:00 UTC",
        posmode="ppp-static",
        freqmode="l1+l2",
        sateph="prec",
        ionoopt="dual-freq",
        tropopt="saas",
        navsys=1 + 8 + 32,
        armode="off",
        needs_sp3=True, needs_clk=True, needs_bia=False, needs_ionex=False,
        te="2026/01/15 04:00:00",
    ),
    "5D": dict(
        name="Experiment 5D — 8-Hour Session",
        desc="GPS+GAL+BDS · precise · 00:00–08:00 UTC",
        posmode="ppp-static",
        freqmode="l1+l2",
        sateph="prec",
        ionoopt="dual-freq",
        tropopt="saas",
        navsys=1 + 8 + 32,
        armode="off",
        needs_sp3=True, needs_clk=True, needs_bia=False, needs_ionex=False,
        te="2026/01/15 08:00:00",
    ),
    "5E": dict(
        name="Experiment 5E — Full 24-Hour Session",
        desc="GPS+GAL+BDS · precise · full day",
        posmode="ppp-static",
        freqmode="l1+l2",
        sateph="prec",
        ionoopt="dual-freq",
        tropopt="saas",
        navsys=1 + 8 + 32,
        armode="off",
        needs_sp3=True, needs_clk=True, needs_bia=False, needs_ionex=False,
    ),
}

# ── RTKPOST/rnx2rtkp .conf template ──────────────────────────────────────────
# This template exactly matches the parameter names and default values that
# RTKLIB-EX 2.5.0 writes when you save Options from the GUI.
# Only experiment-specific values are substituted via {template_vars}.
CONF_TEMPLATE = """\
# rtkpost options (auto-generated by run_rtklib.py)
# Generated  : {timestamp}
# Station    : {station}
# Experiment : {exp_key}  —  {exp_name}
# Dataset    : {dataset_label}
# Obs file   : {obs_file}
# Run folder : {run_dir}
#
# Load this file in RTKPOST with: Options -> Load
# Then set your input files and click Execute.
#
pos1-posmode       ={posmode}
pos1-frequency     ={freqmode}
pos1-soltype       =forward
pos1-elmask        =15
pos1-snrmask_r     =off
pos1-snrmask_b     =off
pos1-snrmask_L1    =35,35,35,35,35,35,35,35,35
pos1-snrmask_L2    =35,35,35,35,35,35,35,35,35
pos1-snrmask_L5    =35,35,35,35,35,35,35,35,35
pos1-snrmask_L6    =35,35,35,35,35,35,35,35,35
pos1-dynamics      =on
pos1-tidecorr      =0
pos1-ionoopt       ={ionoopt}
pos1-tropopt       ={tropopt}
pos1-sateph        ={sateph}
pos1-posopt1       ={posopt1}
pos1-posopt2       ={posopt2}
pos1-posopt3       ={posopt3}
pos1-posopt4       =off
pos1-posopt5       =off
pos1-posopt6       =off
pos1-exclsats      =
pos1-navsys        ={navsys}
pos2-armode        ={armode}
pos2-gloarmode     =off
pos2-bdsarmode     ={bdsarmode}
pos2-arfilter      =on
pos2-arthres       =3
pos2-arthresmin    =3
pos2-arthresmax    =3
pos2-arthres1      =0.1
pos2-arthres2      =0
pos2-arthres3      =1e-09
pos2-arthres4      =1e-05
pos2-varholdamb    =0.1
pos2-gainholdamb   =0.01
pos2-arlockcnt     =0
pos2-minfixsats    =4
pos2-minholdsats   =5
pos2-mindropsats   =10
pos2-arelmask      =15
pos2-arminfix      =20
pos2-armaxiter     =1
pos2-elmaskhold    =15
pos2-aroutcnt      =20
pos2-maxage        =30
pos2-syncsol       =off
pos2-slipthres     =0.05
pos2-dopthres      =0
pos2-rejionno      =5
pos2-rejcode       =30
pos2-niter         =1
pos2-baselen       =0
pos2-basesig       =0
out-solformat      =llh
out-outhead        =on
out-outopt         =on
out-outvel         =off
out-timesys        =gpst
out-timeform       =hms
out-timendec       =3
out-degform        =deg
out-fieldsep       =
out-outsingle      =off
out-maxsolstd      =0
out-height         =ellipsoidal
out-geoid          =internal
out-solstatic      =all
out-nmeaintv1      =0
out-nmeaintv2      =0
out-outstat        =residual
stats-eratio1      =300
stats-eratio2      =300
stats-eratio5      =300
stats-eratio6      =300
stats-errphase     =0.003
stats-errphaseel   =0.003
stats-errphasebl   =0
stats-errdoppler   =1
stats-snrmax       =52
stats-errsnr       =0
stats-errrcv       =0
stats-stdbias      =30
stats-stdiono      =0.03
stats-stdtrop      =0.3
stats-prnaccelh    =3
stats-prnaccelv    =1
stats-prnbias      =0.0001
stats-prniono      =0.001
stats-prntrop      =0.0001
stats-prnpos       =0
stats-clkstab      =5e-12
ant1-postype       =rinexhead
ant1-pos1          =90
ant1-pos2          =0
ant1-pos3          =-6335367.6285
ant1-anttype       ={ant1_anttype}
ant1-antdele       =0
ant1-antdeln       =0
ant1-antdelu       =0
ant2-postype       =rinexhead
ant2-pos1          =0
ant2-pos2          =0
ant2-pos3          =0
ant2-anttype       =
ant2-antdele       =0
ant2-antdeln       =0
ant2-antdelu       =0
ant2-maxaveep      =1
ant2-initrst       =on
misc-timeinterp    =on
misc-sbasatsel     =0
misc-rnxopt1       =
misc-rnxopt2       =
misc-pppopt        =
file-satantfile    ={atx_file}
file-rcvantfile    ={atx_file}
file-staposfile    =
file-geoidfile     =
file-ionofile      ={ionex_file}
file-dcbfile       =
file-eopfile       =
file-blqfile       =
file-tempdir       =
file-geexefile     =
file-solstatfile   =
file-tracefile     =
"""


# =============================================================================
# UI helpers
# =============================================================================

def _enable_ansi():
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.kernel32.SetConsoleMode(
                ctypes.windll.kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass


def banner():
    print(f"\n{CYAN}{BOLD}")
    print("  +====================================================+")
    print("  |   RTKLIB PPP Run Wizard                            |")
    print("  |   Based on RTKLIB-EX 2.5.0 (demo5)                |")
    print(f"  |   Project root: {str(ROOT):<36s} |")
    print("  +====================================================+")
    print(RESET)


def section(title, step=None, total=4):
    prefix = f"  Step {step}/{total}  .  " if step else "  "
    print(f"\n{BOLD}{prefix}{title}{RESET}")


def choose(prompt, options, zero_label=None):
    """
    Print numbered options and return the chosen key (1-based).
    options: list of (key, label) tuples.
    """
    for i, (k, label) in enumerate(options, 1):
        print(f"    {CYAN}{i}{RESET}. {label}  {DIM}[{k}]{RESET}")
    if zero_label:
        print(f"    {CYAN}0{RESET}. {zero_label}")
    while True:
        raw = input(f"\n  {prompt} : ").strip()
        if zero_label and raw == "0":
            return None
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1][0]
        print(f"  {RED}Enter a number 1–{len(options)}.{RESET}")


def multi_choose(prompt, options):
    """Return list of chosen keys (comma-separated or 'all')."""
    for i, (k, label) in enumerate(options, 1):
        print(f"    {CYAN}{i}{RESET}. {label}  {DIM}[{k}]{RESET}")
    print(f"    {CYAN}A{RESET}. All experiments")
    while True:
        raw = input(f"\n  {prompt} (e.g. 1,3,4 or A) : ").strip().upper()
        if raw == "A":
            return [k for k, _ in options]
        parts = [p.strip() for p in raw.split(",")]
        chosen = []
        valid = True
        for p in parts:
            if p.isdigit() and 1 <= int(p) <= len(options):
                chosen.append(options[int(p) - 1][0])
            else:
                valid = False
                break
        if valid and chosen:
            return chosen
        print(
            f"  {RED}Invalid input. Enter numbers separated by commas, or A.{RESET}")


# =============================================================================
# Product resolution
# =============================================================================

def resolve_products(dataset_key, ds, exp):
    """
    Return dict of absolute Path objects for all product files needed by exp.
    Missing optional files get Path('') so the conf file stays syntactically valid.
    """
    prod_dir = ds["prod_dir"]

    sp3 = (prod_dir / ds["sp3"]) if exp["needs_sp3"] else Path("")
    clk = (prod_dir / ds["clk"]) if exp["needs_clk"] else Path("")
    bia = (prod_dir / ds["bia"]) if exp["needs_bia"] else Path("")
    atx = prod_dir / ds["atx"]
    ionex = Path("")
    if exp["needs_ionex"]:
        ionex_key = ds.get("ionex", "")
        if ionex_key:
            ionex = prod_dir / ionex_key
        else:
            # ionex not in new_data products folder — try old_data
            ionex = OLD_DATA_DIR / "products" / "ionex" / \
                "COD0OPSFIN_20260150000_01D_01H_GIM.INX"

    # Check existence and warn
    for name, p in [("SP3", sp3), ("CLK", clk), ("BIA (OSB)", bia),
                    ("ATX", atx), ("IONEX", ionex)]:
        if str(p) and not p.exists():
            print(f"  {YELLOW}WARNING: {name} file not found: {p}{RESET}")

    return dict(sp3=sp3, clk=clk, bia=bia, atx=atx, ionex=ionex)


# =============================================================================
# Config file generation
# =============================================================================

def _navsys_str(navsys):
    """Convert navsys integer to human-readable string."""
    bits = {1: "GPS", 4: "GLO", 8: "GAL", 16: "QZS", 32: "BDS", 64: "NavIC"}
    parts = [v for k, v in sorted(bits.items()) if navsys & k]
    return "+".join(parts) if parts else "NONE"


def generate_conf(run_dir, obs_file, nav_file, products, exp, exp_key,
                  station, station_info, dataset_key, dataset_label):
    """
    Write a .conf file to run_dir/run.conf.
    Returns the path to the conf file.
    """
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ionoopt string mapping (RTKLIB-EX conf values)
    ionoopt_map = {
        "off":       "off",
        "brdc":      "brdc",
        "dual-freq": "dual-freq",
        "ionex-tec": "ionex-tec",
        "est-stec":  "est-stec",
    }

    # sateph string mapping — RTKLIB-EX 2.5.0 requires full word "precise", not "prec"
    sateph_map = {
        "brdc": "brdc",
        "prec": "precise",
    }

    # tropopt string mapping
    tropopt_map = {
        "off":     "off",
        "saas":    "saas",
        "est-ztd": "est-ztd",
    }

    # AR mode
    bdsarmode = "on" if exp["armode"] == "cont" else "off"

    # posopt1/2/3: Sat PCV / Rec PCV / Phase Wind-Up
    # OFF for broadcast-only runs (no ATX file loaded), ON for all precise runs
    posopt_val = "on" if exp.get("posopt", True) else "off"
    # ant1-anttype: * (auto from RINEX header) when ATX loaded, empty when no ATX
    ant1_anttype = "*" if exp.get("posopt", True) else ""

    conf_text = CONF_TEMPLATE.format(
        timestamp=ts,
        station=station,
        exp_key=exp_key,
        exp_name=exp["name"],
        dataset_label=dataset_label,
        obs_file=obs_file,
        run_dir=run_dir,
        posmode=exp["posmode"],
        freqmode=exp["freqmode"],
        ionoopt=ionoopt_map.get(exp["ionoopt"], exp["ionoopt"]),
        tropopt=tropopt_map.get(exp["tropopt"], exp["tropopt"]),
        sateph=sateph_map.get(exp["sateph"], exp["sateph"]),
        posopt1=posopt_val,
        posopt2=posopt_val,
        posopt3=posopt_val,
        ant1_anttype=ant1_anttype,
        navsys=exp["navsys"],
        armode=exp["armode"],
        bdsarmode=bdsarmode,
        atx_file=str(products["atx"]),
        ionex_file=str(products["ionex"]),
    )

    conf_path = run_dir / "run.conf"
    conf_path.write_text(conf_text, encoding="utf-8")
    return conf_path


# =============================================================================
# rnx2rtkp execution
# =============================================================================

def _find_rnx2rtkp(needs_ar):
    """Return path to rnx2rtkp.exe; prefer EX 2.5.0 for AR."""
    if RNX2RTKP_EX.exists():
        return RNX2RTKP_EX
    if RNX2RTKP_243.exists():
        if needs_ar:
            print(f"  {YELLOW}WARNING: RTKLIB-EX 2.5.0 not found. "
                  f"PPP-AR (Exp 3B) requires EX 2.5.0 — falling back to 2.4.3.{RESET}")
        return RNX2RTKP_243
    return None


def build_cmd(exe, obs_file, nav_file, products, exp, output_pos):
    """
    Build the rnx2rtkp command-line list.

    rnx2rtkp [options] obs_file nav_file [sp3_file] [clk_file] [...]

    For RTKLIB-EX 2.5.0, additional product files (BIA, IONEX) can be passed
    as extra positional file arguments — RTKLIB auto-detects file type from content.
    """
    cmd = [
        str(exe),
        "-k", str(output_pos.parent / "run.conf"),
        "-o", str(output_pos),
    ]

    # Time window for session-length experiments
    if "te" in exp:
        # te is like "2026/01/15 02:00:00"
        date_str, time_str = exp["te"].split(" ")
        cmd += ["-te", date_str, time_str]

    # Input files: obs file + nav file always come first
    cmd += [str(obs_file), str(nav_file)]

    # Additional product files (SP3, CLK, BIA, IONEX)
    for key in ("sp3", "clk", "bia", "ionex"):
        p = products.get(key, Path(""))
        if str(p) and p.exists():
            cmd.append(str(p))

    return cmd


def stage_inputs(run_dir, obs_file, nav_file, products):
    """
    Copy all input files (obs, nav, products) into run_dir so each run folder
    is fully self-contained and reproducible without the original data paths.
    Returns updated (obs_file, nav_file, products) pointing to the local copies.
    """
    def _copy(src):
        p = Path(src)
        if not src or not p.exists():
            return Path(src)          # keep as-is (empty or missing optional)
        dst = run_dir / p.name
        if not dst.exists():          # skip if already staged (re-run guard)
            shutil.copy2(str(p), str(dst))
        return dst

    new_obs = _copy(obs_file)
    new_nav = _copy(nav_file)
    new_products = {k: _copy(v) for k, v in products.items()}
    return new_obs, new_nav, new_products


def run_experiment(exe, obs_file, nav_file, products, exp, exp_key,
                   run_dir, station, station_info, dataset_key, dataset_label):
    """
    Run a single experiment: stage input files, generate conf, run rnx2rtkp.
    Returns path to the output .pos file (or None on failure).
    Each run_dir is fully self-contained after completion.
    """
    # Copy all inputs into the run folder for reproducibility
    print(f"  {DIM}Staging input files …{RESET}")
    obs_file, nav_file, products = stage_inputs(
        run_dir, obs_file, nav_file, products)

    output_pos = run_dir / f"{station}_{exp_key}.pos"
    conf_path = generate_conf(
        run_dir, obs_file, nav_file, products, exp, exp_key,
        station, station_info, dataset_key, dataset_label)

    cmd = build_cmd(exe, obs_file, nav_file, products, exp, output_pos)

    print(f"\n  {BOLD}Running:{RESET} {exp['name']}")
    print(f"  {DIM}Cmd: {' '.join(cmd[:6])} ...{RESET}")
    print(f"  Output → {output_pos.name}")

    try:
        result = subprocess.run(
            cmd,
            cwd=str(run_dir),
            capture_output=True,
            text=True,
            timeout=600,    # 10 min max per run
        )
    except FileNotFoundError:
        print(f"  {RED}ERROR: rnx2rtkp.exe not found at {exe}{RESET}")
        return None
    except subprocess.TimeoutExpired:
        print(f"  {RED}ERROR: Processing timed out (>10 min){RESET}")
        return None

    if result.returncode != 0 or not output_pos.exists():
        print(f"  {RED}FAILED (exit code {result.returncode}){RESET}")
        if result.stderr:
            for line in result.stderr.strip().split("\n")[-10:]:
                print(f"    {DIM}{line}{RESET}")
        return None

    # Count solution epochs
    n_total = 0
    n_fixed = 0
    n_float = 0
    try:
        with open(output_pos, encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.startswith("%") or not line.strip():
                    continue
                n_total += 1
                # RTKLIB pos format: col 7 = Q (1=fixed, 2=float, 5=single)
                parts = line.split()
                if len(parts) >= 7:
                    q = parts[6]
                    if q == "1":
                        n_fixed += 1
                    elif q == "2":
                        n_float += 1
    except Exception:
        pass

    print(f"  {GREEN}Done.{RESET}  {n_total} epochs  "
          f"(fixed={n_fixed}, float={n_float}, "
          f"single={n_total - n_fixed - n_float})")
    print(f"  Conf file: {conf_path.name}")
    return output_pos


# =============================================================================
# Main wizard
# =============================================================================

def main():
    _enable_ansi()
    banner()

    # ── Check executable ─────────────────────────────────────────────────────
    exe_ex = RNX2RTKP_EX.exists()
    exe_243 = RNX2RTKP_243.exists()
    if not exe_ex and not exe_243:
        print(f"\n  {RED}ERROR: rnx2rtkp.exe not found.{RESET}")
        print(f"  Looked in:")
        print(f"    {RNX2RTKP_EX}")
        print(f"    {RNX2RTKP_243}")
        print(f"\n  Install RTKLIB-EX 2.5.0 or RTKLIB 2.4.3 and retry.")
        sys.exit(1)

    if exe_ex:
        print(f"\n  {GREEN}✓{RESET}  RTKLIB-EX 2.5.0 found: {RNX2RTKP_EX}")
    else:
        print(
            f"\n  {YELLOW}⚠{RESET}  RTKLIB-EX 2.5.0 not found. Using RTKLIB 2.4.3.")
        print(
            f"  {YELLOW}  PPP-AR (Experiment 3B) will not produce AR fixes without EX 2.5.0.{RESET}")

    # ── Step 1: Dataset ───────────────────────────────────────────────────────
    section("Select Dataset", step=1, total=4)
    ds_key = choose("Choose dataset", [
        ("new", DATASETS["new"]["label"]),
        ("old", DATASETS["old"]["label"]),
    ])
    ds = DATASETS[ds_key]

    # ── Step 2: Station ───────────────────────────────────────────────────────
    section("Select Station", step=2, total=4)
    station_list = [(k, f"{k}  —  {v['desc']}")
                    for k, v in ds["stations"].items()]
    station = choose("Choose station", station_list)
    station_info = ds["stations"][station]

    obs_file = ds["obs_dir"] / station_info["obs"]
    nav_file = ds["nav_dir"] / ds["nav"]

    if not obs_file.exists():
        print(f"\n  {RED}ERROR: Observation file not found:{RESET}")
        print(f"  {obs_file}")
        sys.exit(1)
    if not nav_file.exists():
        print(f"\n  {RED}ERROR: Navigation file not found:{RESET}")
        print(f"  {nav_file}")
        sys.exit(1)

    print(f"\n  {GREEN}✓{RESET}  Obs : {obs_file.name}")
    print(f"  {GREEN}✓{RESET}  Nav : {nav_file.name}")

    # ── Step 3: Experiment(s) ─────────────────────────────────────────────────
    section("Select Experiment(s)", step=3, total=4)
    print()
    print(f"  {BOLD}Available experiments:{RESET}\n")
    exp_list = []
    for i, (k, v) in enumerate(EXPERIMENTS.items(), 1):
        marker = f"{YELLOW}⚠ AR{RESET}" if v["armode"] != "off" else ""
        print(f"  {CYAN}{i:2d}{RESET}. {v['name']}  {marker}")
        print(f"       {DIM}{v['desc']}{RESET}")
        exp_list.append((k, v["name"]))
    print()

    chosen_keys = multi_choose("Select experiments", exp_list)

    # ── Step 4: Run ───────────────────────────────────────────────────────────
    section("Processing", step=4, total=4)
    RUNS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_results = []

    # Special handling for Experiment 2: create sub-folders for 2A/2B/2C/2D
    if "2A" in chosen_keys or "2B" in chosen_keys or "2C" in chosen_keys or "2D" in chosen_keys:
        print(
            f"\n  {YELLOW}ℹ Experiment 2 detected: will create separate folders for 2A/2B/2C/2D{RESET}")
        exp2_keys = [k for k in chosen_keys if k in ("2A", "2B", "2C", "2D")]
        other_keys = [k for k in chosen_keys if k not in (
            "2A", "2B", "2C", "2D")]

        # Run Exp2 sub-experiments with explicit folder naming
        for exp_key in exp2_keys:
            exp = EXPERIMENTS[exp_key]
            needs_ar = exp["armode"] != "off"

            # Create explicit Exp2 subfolder: {station}_EXP2_2A_{timestamp}, etc.
            run_dir = RUNS_DIR / f"{station}_EXP2_{exp_key}_{timestamp}"
            run_dir.mkdir(parents=True, exist_ok=True)

            products = resolve_products(ds_key, ds, exp)
            exe = _find_rnx2rtkp(needs_ar)
            if exe is None:
                print(
                    f"  {RED}No rnx2rtkp.exe available — skipping {exp_key}{RESET}")
                continue

            pos_file = run_experiment(
                exe, obs_file, nav_file, products, exp, exp_key,
                run_dir, station, station_info, ds_key, ds["label"])

            if pos_file:
                run_results.append((exp_key, exp["name"], pos_file))

        # Now run remaining (non-Exp2) experiments with standard folder naming
        chosen_keys = other_keys

    # Standard experiment handling for non-Exp2 experiments
    for exp_key in chosen_keys:
        exp = EXPERIMENTS[exp_key]
        needs_ar = exp["armode"] != "off"

        # Per-experiment run folder (standard naming for non-Exp2)
        run_label = re.sub(r"[^A-Za-z0-9_-]", "_", exp_key)
        run_dir = RUNS_DIR / f"{station}_{run_label}_{timestamp}"
        run_dir.mkdir(parents=True, exist_ok=True)

        # Resolve product files
        products = resolve_products(ds_key, ds, exp)

        # Select executable
        exe = _find_rnx2rtkp(needs_ar)
        if exe is None:
            print(f"  {RED}No rnx2rtkp.exe available — skipping {exp_key}{RESET}")
            continue

        # Run
        pos_file = run_experiment(
            exe, obs_file, nav_file, products, exp, exp_key,
            run_dir, station, station_info, ds_key, ds["label"])

        if pos_file:
            run_results.append((exp_key, exp["name"], pos_file))

    # ── Summary ───────────────────────────────────────────────────────────────
    if run_results:
        print(f"\n  {CYAN}{BOLD}=== Run Summary ==={RESET}\n")
        for exp_key, exp_name, pos_file in run_results:
            print(f"  {GREEN}✓{RESET}  {exp_key:4s}  {pos_file}")

        print(f"\n  {BOLD}To visualise in RTKPLOT:{RESET}")
        print(f"    Open: {RTKPLOT_EX}")
        print(f"    File → Open Solution → select the .pos file(s) above")
        print(f"    Edit → Options → Reference Position:")
        print(f"      Lat = {station_info['lat']}")
        print(f"      Lon = {station_info['lon']}")
        print(f"      Hgt = {station_info['hgt']} m")
        print(f"    Select Plot Type: Position  (shows ENU error vs time)")

        if len(run_results) > 1:
            print(f"\n  {BOLD}To compare multiple runs:{RESET}")
            print(f"    File → Open Solution 1 → first .pos")
            print(f"    File → Open Solution 2 → second .pos")
            print(f"    Both appear as overlapping curves on the same plot.")
    else:
        print(f"\n  {RED}No successful runs.{RESET}")

    print()


if __name__ == "__main__":
    main()
