#!/usr/bin/env python3
"""
plot_pride_enu.py  —  Visualize PRIDE PPP-AR output files (kin_ and pos_).

PRIDE outputs two main position files:
  kin_YYYYDDD_station  — kinematic/per-epoch coordinates (lat/lon/height + ECEF)
  pos_YYYYDDD_station  — static final position (single line with uncertainty)

This script plots ENU convergence from kin_ files and can also convert them
to rtkplot format. The kin_ file already has lat/lon/height, so rtkplot can
read the converted output directly.

USAGE:
    # Run from C:/PPP_PROJECT with your PRIDE_work output files:
    python scripts/plot_pride_enu.py  PRIDE_work/kin_20260150000_hkws

    # Example (run from WSL after PRIDE finishes):
    python /mnt/c/PPP_PROJECT/scripts/plot_pride_enu.py  kin_20260150000_hkws

    # Convergence comparison (GPS-only float vs multi-GNSS AR):
    python scripts/plot_pride_enu.py --compare  kin_float  kin_fixed

    # Convert to rtkplot format:
    python scripts/plot_pride_enu.py --convert-only  kin_20260150000_hkws

    # Print static result from pos_ file:
    python scripts/plot_pride_enu.py --pos  pos_20260150000_hkws

OUTPUT:
    <kin_file>.png          — ENU convergence plot
    <kin_file>.rtklib.pos   — rtkplot-compatible lat/lon format
    <kin_file>.stats        — text statistics

PRIDE kin_ file format (after END OF HEADER):
    * Mjd  Sod  X(m)  Y(m)  Z(m)  Lat(deg)  Lon(deg)  Height(m)  Nsat/...  PDOP
    59434  0.00  ...

PRIDE pos_ file format (after END OF HEADER):
    *Name  Mjd  X  Y  Z  Sx  Sy  Sz  Rxy  Rxz  Ryz  Sig0  Nobs
"""

import numpy as np
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import argparse
import math
import os
import sys

import matplotlib
matplotlib.use("TkAgg")


# ─────────────────────────────────────────────────────────────────────────────
# MJD → calendar date/time helpers
# ─────────────────────────────────────────────────────────────────────────────

def mjd_sod_to_hms(mjd, sod):
    """Return (year, month, day, hour, minute, second) from MJD + seconds-of-day."""
    # MJD epoch: November 17, 1858
    jd = mjd + 2400000.5 + sod / 86400.0
    jd_int = int(jd + 0.5)
    frac = (jd + 0.5) - jd_int

    if jd_int >= 2299161:
        l = jd_int + 68569
        n = (4 * l) // 146097
        l = l - (146097 * n + 3) // 4
        yr = (4000 * (l + 1)) // 1461001
        l = l - (1461 * yr) // 4 + 31
        mo = (80 * l) // 2447
        dy = l - (2447 * mo) // 80
        l = mo // 11
        mo = mo + 2 - 12 * l
        yr = 100 * (n - 49) + yr + l
    else:
        jd_int += 1
        l = jd_int + 1402
        c = (l - 1) // 1461
        l = l - 1461 * c
        n = (l - 1) // 365 - l // 1461
        l = l - 365 * n + 30
        mo = (80 * l) // 2447
        dy = l - (2447 * mo) // 80
        l = mo // 11
        mo = mo + 2 - 12 * l
        yr = 4 * c + n + l - 4716

    tot_sec = frac * 86400.0
    hr = int(tot_sec // 3600)
    mn = int((tot_sec % 3600) // 60)
    sc = tot_sec % 60.0
    return int(yr), int(mo), int(dy), hr, mn, sc


# ─────────────────────────────────────────────────────────────────────────────
# Reference coordinates (ITRF2020) for known stations
# ─────────────────────────────────────────────────────────────────────────────

# Approximate ITRF2020 lat/lon/height for common stations
# Add more as needed: key = 4-char station name (lowercase)
KNOWN_REF = {
    "hkws": {"lat":  22.2722, "lon": 114.1614, "h":  72.0,
             "X": -2414266.880, "Y":  5384648.890, "Z":  2394737.060},
    "zim2": {"lat":  46.8772, "lon":   7.4652, "h": 956.0,
             "X":  4331297.344, "Y":   567555.639, "Z":  4633133.920},
    "abmf": {"lat":  16.2653, "lon": -61.5277, "h": -25.6,
             "X":  2919785.791, "Y": -5383744.959, "Z":  1774604.860},
    "bako": {"lat": -6.4911, "lon": 106.8489, "h":  158.1,
             "X": -1836969.501, "Y":  6065616.960, "Z": -716257.934},
    "brux": {"lat":  50.7979, "lon":   4.3590, "h":  158.5,
             "X":  4027881.790, "Y":   306998.072, "Z":  4919498.571},
}


def get_ref_latlon(station_name):
    key = station_name.strip().lower()[:4]
    return KNOWN_REF.get(key, None)


# ─────────────────────────────────────────────────────────────────────────────
# ECEF → WGS84
# ─────────────────────────────────────────────────────────────────────────────

def ecef_to_geodetic(x, y, z):
    a = 6378137.0
    f = 1.0 / 298.257223563
    b = a * (1 - f)
    e2 = 1 - (b / a) ** 2
    lon = math.atan2(y, x)
    p = math.sqrt(x * x + y * y)
    lat = math.atan2(z, p * (1 - e2))
    for _ in range(10):
        sl = math.sin(lat)
        N = a / math.sqrt(1 - e2 * sl * sl)
        ln = math.atan2(z + e2 * N * sl, p)
        if abs(ln - lat) < 1e-12:
            lat = ln
            break
        lat = ln
    sl = math.sin(lat)
    N = a / math.sqrt(1 - e2 * sl * sl)
    cl = math.cos(lat)
    h = (p / cl - N) if abs(cl) > 1e-10 else (abs(z) / abs(sl) - N * (1 - e2))
    return math.degrees(lat), math.degrees(lon), h


def latlon_to_enu(lat_r, lon_r, h_r, lat, lon, h):
    """
    Compute ENU difference (m) between (lat,lon,h) and reference (lat_r,lon_r,h_r).
    All in degrees/metres.
    """
    lat_r, lon_r = math.radians(lat_r), math.radians(lon_r)
    lat,   lon = math.radians(lat),   math.radians(lon)
    dlat = lat - lat_r
    dlon = lon - lon_r
    dh = h - h_r
    R = 6378137.0  # approximate
    N_e = R * math.cos(lat_r)
    E_m = N_e * dlon
    N_m = R * dlat
    U_m = dh
    return E_m, N_m, U_m


# ─────────────────────────────────────────────────────────────────────────────
# Read PRIDE kin_ file
# ─────────────────────────────────────────────────────────────────────────────

def read_pride_kin(filepath):
    """
    Returns dict with:
        station, t (hours from first epoch), lat, lon, h,
        E, N, U (if ref available), nsat, pdop,
        yr, mo, dy per epoch (for rtkplot timestamp)
    """
    if not os.path.isfile(filepath):
        print(f"  ERROR: not found: {filepath}", file=sys.stderr)
        return None

    station = os.path.basename(filepath).split("_")[-1]
    ref = get_ref_latlon(station)

    in_header = True
    rows = {"mjd": [], "sod": [], "lat": [], "lon": [], "h": [],
            "X": [], "Y": [], "Z": [], "nsat": [], "pdop": []}

    with open(filepath, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.rstrip("\n")
            stripped = line.strip()
            if in_header:
                # Detect station from header
                if stripped and not any(c.isdigit() for c in stripped[:4]):
                    hdr_parts = stripped.split()
                    if len(hdr_parts) == 1 and len(hdr_parts[0]) == 4:
                        station = hdr_parts[0].lower()
                        ref = get_ref_latlon(station)
                if "END OF HEADER" in stripped:
                    in_header = False
                continue
            if stripped.startswith("*"):
                continue  # column header line
            if not stripped:
                continue
            cols = stripped.split()
            if len(cols) < 9:
                continue
            try:
                mjd = int(cols[0])
                sod = float(cols[1])
                X = float(cols[2])
                Y = float(cols[3])
                Z = float(cols[4])
                lat = float(cols[5])
                lon = float(cols[6])
                h = float(cols[7])
                # nsat is like "17" and pdop at end
                nsat = int(cols[8]) if cols[8].isdigit() else 0
                pdop = float(cols[-1]) if len(cols) >= 10 else 0.0
            except (ValueError, IndexError):
                continue
            rows["mjd"].append(mjd)
            rows["sod"].append(sod)
            rows["X"].append(X)
            rows["Y"].append(Y)
            rows["Z"].append(Z)
            rows["lat"].append(lat)
            rows["lon"].append(lon)
            rows["h"].append(h)
            rows["nsat"].append(nsat)
            rows["pdop"].append(pdop)

    n = len(rows["mjd"])
    if n < 10:
        print(f"  WARNING: {os.path.basename(filepath)} — only {n} epochs, skipping.",
              file=sys.stderr)
        return None

    # Build time array (hours from first epoch)
    sod0 = rows["sod"][0]
    t = np.array([(rows["sod"][i] - sod0) / 3600.0 for i in range(n)])
    t[t < 0] += 24.0

    lat_arr = np.array(rows["lat"])
    lon_arr = np.array(rows["lon"])
    h_arr = np.array(rows["h"])

    # Compute ENU errors if reference known
    E_arr = N_arr = U_arr = None
    if ref:
        ENU = [latlon_to_enu(ref["lat"], ref["lon"], ref["h"],
                             lat_arr[i], lon_arr[i], h_arr[i])
               for i in range(n)]
        E_arr = np.array([e[0] for e in ENU])
        N_arr = np.array([e[1] for e in ENU])
        U_arr = np.array([e[2] for e in ENU])

    # Build timestamps for rtkplot output
    timestamps = [mjd_sod_to_hms(rows["mjd"][i], rows["sod"][i])
                  for i in range(n)]

    return {
        "station":   station,
        "ref":       ref,
        "t":         t,
        "lat":       lat_arr,
        "lon":       lon_arr,
        "h":         h_arr,
        "E":         E_arr,
        "N":         N_arr,
        "U":         U_arr,
        "nsat":      np.array(rows["nsat"]),
        "pdop":      np.array(rows["pdop"]),
        "timestamps": timestamps,
        "n":         n,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Read PRIDE pos_ file (static result)
# ─────────────────────────────────────────────────────────────────────────────

def read_pride_pos(filepath):
    """Return dict with final static position and uncertainties."""
    if not os.path.isfile(filepath):
        print(f"  ERROR: not found: {filepath}", file=sys.stderr)
        return None

    in_header = True
    station = os.path.basename(filepath).split("_")[-1]

    with open(filepath, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            stripped = line.strip()
            if in_header:
                if "END OF HEADER" in stripped:
                    in_header = False
                continue
            if stripped.startswith("*"):
                continue
            if not stripped:
                continue
            cols = stripped.split()
            if len(cols) < 12:
                continue
            try:
                name = cols[0]
                mjd = float(cols[1])
                X = float(cols[2])
                Y = float(cols[3])
                Z = float(cols[4])
                Sx = float(cols[5])
                Sy = float(cols[6])
                Sz = float(cols[7])
                sig0 = float(cols[11])
                nobs = int(cols[12])
                lat, lon, h = ecef_to_geodetic(X, Y, Z)
                ref = get_ref_latlon(name)
                result = {
                    "station": name, "X": X, "Y": Y, "Z": Z,
                    "lat": lat, "lon": lon, "h": h,
                    "Sx_mm": math.sqrt(Sx) * 1000 if Sx >= 0 else 0,
                    "Sy_mm": math.sqrt(Sy) * 1000 if Sy >= 0 else 0,
                    "Sz_mm": math.sqrt(Sz) * 1000 if Sz >= 0 else 0,
                    "sig0": sig0, "nobs": nobs,
                }
                if ref:
                    E, N, U = latlon_to_enu(ref["lat"], ref["lon"], ref["h"],
                                            lat, lon, h)
                    result.update(
                        {"dE_cm": E * 100, "dN_cm": N * 100, "dU_cm": U * 100})
                return result
            except (ValueError, IndexError):
                continue
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Plotting
# ─────────────────────────────────────────────────────────────────────────────

def rms(arr):
    return float(np.sqrt(np.mean(arr ** 2)))


def convergence_time(E, N, U, t, h_thresh=0.10, v_thresh=0.20, window_min=10, interval_s=30):
    if E is None:
        return None
    window = max(1, int(window_min * 60 / interval_s))
    d2d = np.sqrt(E ** 2 + N ** 2)
    for i in range(len(t) - window):
        if (np.all(d2d[i:i + window] < h_thresh) and
                np.all(np.abs(U[i:i + window]) < v_thresh)):
            return t[i]
    return None


def _cap_ylim(ax, cap=1.0):
    lines = [ln for ln in ax.get_lines() if len(ln.get_ydata()) > 0]
    if not lines:
        return
    ymax = min(cap, max(np.percentile(np.abs(ln.get_ydata()), 99)
               for ln in lines))
    ax.set_ylim(-ymax * 1.15, ymax * 1.15)


def plot_kin_single(filepath, data, show=True, save=True):
    if data["E"] is None:
        # No reference known — plot absolute height variation
        fig, ax = plt.subplots(figsize=(13, 5))
        h_mean = data["h"].mean()
        ax.plot(data["t"], data["h"] - h_mean, "r-",
                lw=0.9, label="Height deviation")
        ax.set_ylabel("Height deviation (m)")
        ax.set_title(
            f"{os.path.basename(filepath)} — no reference coords for {data['station']}")
        ax.legend()
        ax.grid(True, alpha=0.25)
        note = "Reference coordinates not in KNOWN_REF dict — ENU errors unavailable.\nAdd station to KNOWN_REF in script, or provide ITRF2020 coordinates."
        ax.text(0.98, 0.02, note,
                transform=ax.transAxes,
                fontsize=8,
                va="bottom",
                ha="right",
                bbox=dict(boxstyle="round,pad=0.3",
                          facecolor="white", alpha=0.85))
    else:
        E, N, U, t = data["E"], data["N"], data["U"], data["t"]
        fig, ax = plt.subplots(figsize=(13, 5))
        ax.plot(t, E, "b-",  lw=0.9, label="East")
        ax.plot(t, N, "g-",  lw=0.9, label="North")
        ax.plot(t, U, "r-",  lw=0.9, label="Up")
        ax.axhline(0,     color="k",    lw=0.5, zorder=0)
        ax.axhline(0.10, color="gray", lw=0.5, ls=":", zorder=0)
        ax.axhline(-0.10, color="gray", lw=0.5, ls=":", zorder=0)

        half = len(t) // 2
        conv = convergence_time(E, N, U, t)
        conv_str = f"{conv*60:.0f} min" if conv is not None else ">24h"
        note = (f"RMS (last 12h): E={rms(E[half:])*100:.1f}cm  "
                f"N={rms(N[half:])*100:.1f}cm  U={rms(U[half:])*100:.1f}cm\n"
                f"Convergence (2D<10cm): {conv_str}")
        ax.text(0.98, 0.02, note,
                transform=ax.transAxes,
                fontsize=8,
                va="bottom",
                ha="right",
                bbox=dict(boxstyle="round,pad=0.3",
                          facecolor="white", alpha=0.85))
        _cap_ylim(ax)

        print(f"\n{'='*60}")
        print(f"  File     : {os.path.basename(filepath)}")
        print(f"  Station  : {data['station'].upper()}")
        print(f"  Epochs   : {data['n']}")
        print(
            f"  RMS(last12h): E={rms(E[half:])*100:.2f}cm  N={rms(N[half:])*100:.2f}cm  U={rms(U[half:])*100:.2f}cm")
        print(f"  Convergence: {conv_str}")
        print(f"{'='*60}\n")

    ax.set_xlabel("Time from start (hours)", fontsize=9)
    ax.set_ylabel("Position Error (m)", fontsize=9)
    ax.set_title(f"PRIDE PPP-AR — {os.path.basename(filepath)}", fontsize=9)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.25)
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())

    if save:
        png = filepath + ".png"
        fig.savefig(png, dpi=150, bbox_inches="tight")
        print(f"  Saved: {png}")
    if show:
        plt.show()
    plt.close(fig)


def plot_compare(pairs, show=True, save=True):
    """Overlay multiple kin_ files on one axes."""
    COLORS = plt.cm.tab10.colors
    fig, ax = plt.subplots(figsize=(14, 5))
    outdir = None

    for idx, (fp, data) in enumerate(pairs):
        if data is None or data["E"] is None:
            continue
        c = COLORS[idx % 10]
        label = os.path.basename(fp)
        t = data["t"]
        ax.plot(t, data["E"], color=c, ls="-",  lw=0.8, label=f"{label} E")
        ax.plot(t, data["N"], color=c, ls="--",
                lw=0.7, alpha=0.8, label=f"{label} N")
        ax.plot(t, data["U"], color=c, ls=":",
                lw=0.7, alpha=0.8, label=f"{label} U")
        if outdir is None:
            outdir = os.path.dirname(fp)

    ax.axhline(0,     color="k",    lw=0.5, zorder=0)
    ax.axhline(0.10, color="gray", lw=0.5, ls=":", zorder=0)
    ax.axhline(-0.10, color="gray", lw=0.5, ls=":", zorder=0)
    ax.set_xlabel("Time from start (hours)", fontsize=9)
    ax.set_ylabel("Position Error (m)", fontsize=9)
    ax.set_title("PRIDE PPP-AR — ENU Comparison", fontsize=9)
    ax.legend(fontsize=7, ncol=2)
    ax.grid(True, alpha=0.25)
    _cap_ylim(ax)

    if save and outdir:
        png = os.path.join(outdir, "comparison_ENU.png")
        fig.savefig(png, dpi=150, bbox_inches="tight")
        print(f"  Saved: {png}")
    if show:
        plt.show()
    plt.close(fig)


# ─────────────────────────────────────────────────────────────────────────────
# Scatter plot  (E vs N — horizontal accuracy)
# ─────────────────────────────────────────────────────────────────────────────

def plot_scatter_pride(pairs, show=True, save=True):
    """East vs North scatter, coloured per-file. Dashed circle = RMS radius."""
    COLORS = plt.cm.tab10.colors
    valid = [(fp, d)
             for fp, d in pairs if d is not None and d["E"] is not None]
    if not valid:
        return
    multi = len(valid) > 1
    fig, ax = plt.subplots(figsize=(7, 6))
    for idx, (fp, data) in enumerate(valid):
        c = COLORS[idx % 10]
        lbl = os.path.basename(fp)
        half = len(data["t"]) // 2
        E_cm = data["E"] * 100
        N_cm = data["N"] * 100
        ax.scatter(E_cm[:half], N_cm[:half], s=3, alpha=0.2, color=c)
        ax.scatter(E_cm[half:], N_cm[half:], s=3, alpha=0.75, color=c,
                   label=f"{lbl} (last 12h)" if multi else "last 12h")
        r = float(np.sqrt(np.mean(E_cm[half:] ** 2 + N_cm[half:] ** 2)))
        ax.add_patch(plt.Circle((0, 0), r, fill=False,
                     color=c, lw=0.8, ls="--"))
    ax.axhline(0, color="k", lw=0.5)
    ax.axvline(0, color="k", lw=0.5)
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_xlabel("East error (cm)", fontsize=9)
    ax.set_ylabel("North error (cm)", fontsize=9)
    ax.set_title("PRIDE PPP-AR — Horizontal Scatter (E vs N)", fontsize=9)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.25)
    ax.text(0.02, 0.98,
            "Dashed circle = RMS radius (last 12h)\nLight dots = convergence period",
            transform=ax.transAxes, fontsize=7.5, va="top",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.85))
    if save and valid:
        png = valid[0][0] + ".scatter.png"
        fig.savefig(png, dpi=150, bbox_inches="tight")
        print(f"  Saved: {png}")
    if show:
        plt.show()
    plt.close(fig)


# ─────────────────────────────────────────────────────────────────────────────
# N_sat + PDOP over time
# ─────────────────────────────────────────────────────────────────────────────

def plot_nsat_pdop(pairs, show=True, save=True):
    """
    Two-panel: top = number of tracked satellites, bottom = PDOP.
    Helps assess data quality and explain convergence differences.
    """
    valid = [(fp, d) for fp, d in pairs if d is not None]
    if not valid:
        return
    COLORS = plt.cm.tab10.colors
    fig, (ax_n, ax_p) = plt.subplots(2, 1, figsize=(13, 6), sharex=True)

    for idx, (fp, data) in enumerate(valid):
        c = COLORS[idx % 10]
        lbl = os.path.basename(fp)
        t = data["t"]
        ax_n.plot(t, data["nsat"], color=c, lw=0.8, label=lbl)
        ax_p.plot(t, data["pdop"], color=c, lw=0.8, label=lbl)

    ax_n.set_ylabel("N satellites tracked", fontsize=9)
    ax_p.set_ylabel("PDOP", fontsize=9)
    ax_p.set_xlabel("Time from start (hours)", fontsize=9)
    ax_p.axhline(3.0, color="gray", lw=0.5, ls=":",
                 zorder=0)   # typical PDOP threshold
    ax_n.axhline(4,   color="gray", lw=0.5, ls=":",
                 zorder=0)   # minimum for PPP
    ax_n.set_title("PRIDE PPP-AR — Satellite Count and PDOP", fontsize=9)
    ax_n.legend(fontsize=8)
    ax_n.grid(True, alpha=0.25)
    ax_p.grid(True, alpha=0.25)
    fig.tight_layout()

    if save and valid:
        png = valid[0][0] + ".nsat_pdop.png"
        fig.savefig(png, dpi=150, bbox_inches="tight")
        print(f"  Saved: {png}")
    if show:
        plt.show()
    plt.close(fig)


# ─────────────────────────────────────────────────────────────────────────────
# Summary bar chart  (convergence + RMS across scenarios)
# ─────────────────────────────────────────────────────────────────────────────

def plot_summary_bar_pride(pairs, show=True, save=True):
    """Bar chart: convergence time and RMS per scenario / file."""
    records = []
    for fp, data in pairs:
        if data is None or data["E"] is None:
            continue
        half = len(data["t"]) // 2
        E2, N2, U2 = data["E"][half:], data["N"][half:], data["U"][half:]
        conv = convergence_time(data["E"], data["N"], data["U"], data["t"])
        records.append({
            "label": os.path.basename(fp),
            "conv":  conv * 60 if conv is not None else float("nan"),
            "rms_E": rms(E2) * 100,
            "rms_N": rms(N2) * 100,
            "rms_U": rms(U2) * 100,
        })
    if not records:
        return
    n = len(records)
    x = np.arange(n)
    w = 0.22
    fig, (ax_c, ax_r) = plt.subplots(1, 2, figsize=(max(10, n * 2.5 + 3), 5))
    bars = ax_c.bar(x, [r["conv"] for r in records],
                    0.55, color="steelblue", alpha=0.85)
    for bar, v in zip(bars, [r["conv"] for r in records]):
        if not np.isnan(v):
            ax_c.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                      f"{v:.0f}", ha="center", va="bottom", fontsize=8)
    ax_c.set_xticks(x)
    ax_c.set_xticklabels([r["label"] for r in records],
                         rotation=15, ha="right", fontsize=8)
    ax_c.set_ylabel("Convergence time (min)", fontsize=9)
    ax_c.set_title("Convergence Time  (2D < 10 cm)", fontsize=9)
    ax_c.grid(axis="y", alpha=0.3)
    ax_r.bar(x - w, [r["rms_E"] for r in records], w,
             label="East",  color="royalblue", alpha=0.85)
    ax_r.bar(x,     [r["rms_N"] for r in records], w,
             label="North", color="forestgreen", alpha=0.85)
    ax_r.bar(x + w, [r["rms_U"] for r in records], w,
             label="Up",    color="tomato", alpha=0.85)
    ax_r.set_xticks(x)
    ax_r.set_xticklabels([r["label"] for r in records],
                         rotation=15, ha="right", fontsize=8)
    ax_r.set_ylabel("RMS error  (cm)", fontsize=9)
    ax_r.set_title("Post-Convergence RMS  (last 12 h)", fontsize=9)
    ax_r.legend(fontsize=8)
    ax_r.grid(axis="y", alpha=0.3)
    fig.suptitle("PRIDE PPP-AR Scenario Comparison",
                 fontsize=10, fontweight="bold")
    fig.tight_layout()
    if save and pairs:
        outdir = os.path.dirname(pairs[0][0])
        png = os.path.join(outdir, "summary_bar.png")
        fig.savefig(png, dpi=150, bbox_inches="tight")
        print(f"  Saved: {png}")
    if show:
        plt.show()
    plt.close(fig)


# ─────────────────────────────────────────────────────────────────────────────
# rtkplot converter
# ─────────────────────────────────────────────────────────────────────────────

RTKLIB_HEADER = (
    "%  GPST                          "
    "latitude(deg) longitude(deg)  height(m)   "
    "Q  ns   sdn(m)   sde(m)   sdu(m)  "
    "sdne(m)  sdeu(m)  sdun(m) age(s)  ratio\n"
)


def convert_to_rtklib(filepath, data):
    """
    Write rtkplot-compatible .pos file from PRIDE kin_ data.
    PRIDE already has lat/lon/h, so this is clean.
    """
    outpath = filepath + ".rtklib.pos"
    with open(outpath, "w", newline="\n") as fout:
        fout.write(RTKLIB_HEADER)
        for i in range(data["n"]):
            yr, mo, dy, hr, mn, sc = data["timestamps"][i]
            lat = data["lat"][i]
            lon = data["lon"][i]
            h = data["h"][i]
            dE = data["E"][i] if data["E"] is not None else 0.0
            dN = data["N"][i] if data["N"] is not None else 0.0
            dU = data["U"][i] if data["U"] is not None else 0.0
            fout.write(
                f"{yr:04d}/{mo:02d}/{dy:02d} {hr:02d}:{mn:02d}:{sc:06.3f}   "
                f"{lat:14.9f}  {lon:14.9f}  {h:10.4f}   "
                f"5  {data['nsat'][i]:2d}   "
                f"{dN:9.4f}   {dE:9.4f}   {dU:9.4f}   "
                f"0.0000   0.0000   0.0000   0.00   0.0\n"
            )
    print(f"  rtkplot file: {outpath}")
    return outpath


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Plot / convert PRIDE PPP-AR kin_ output files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("files", nargs="+", help="kin_ or pos_ file(s)")
    parser.add_argument("--compare",      action="store_true",
                        help="Overlay all files on one axes")
    parser.add_argument("--convert-only", action="store_true",
                        help="Convert to rtkplot format only — no plot")
    parser.add_argument("--pos",          action="store_true",
                        help="Read pos_ (static result) instead of kin_")
    parser.add_argument("--scatter",      action="store_true",
                        help="Horizontal scatter plot  (E vs N)")
    parser.add_argument("--nsat",         action="store_true",
                        help="N_sat + PDOP over time")
    parser.add_argument("--summary",      action="store_true",
                        help="Bar chart: convergence + RMS across scenarios")
    parser.add_argument("--all", dest="all_plots", action="store_true",
                        help="Generate all plot types")
    parser.add_argument("--no-show",      action="store_true",
                        help="Save PNG without opening GUI")
    args = parser.parse_args()

    show = not args.no_show

    # ── static pos_ mode ──
    if args.pos:
        for fp in args.files:
            result = read_pride_pos(fp)
            if result:
                print(f"\n{'='*60}")
                print(f"  PRIDE static result: {os.path.basename(fp)}")
                print(f"  Station : {result['station'].upper()}")
                print(f"  Lat     : {result['lat']:.9f} deg")
                print(f"  Lon     : {result['lon']:.9f} deg")
                print(f"  Height  : {result['h']:.4f} m")
                if "dE_cm" in result:
                    print(f"  dE (vs ITRF2020) : {result['dE_cm']:.2f} cm")
                    print(f"  dN (vs ITRF2020) : {result['dN_cm']:.2f} cm")
                    print(f"  dU (vs ITRF2020) : {result['dU_cm']:.2f} cm")
                print(f"  Sig0    : {result['sig0']:.4f}")
                print(f"  N obs   : {result['nobs']}")
                print(f"{'='*60}")
        return

    # ── kinematic kin_ mode ──
    pairs = [(fp, read_pride_kin(fp)) for fp in args.files]
    valid = [(fp, d) for fp, d in pairs if d is not None]

    if not valid:
        print("No valid kin_ files found.", file=sys.stderr)
        sys.exit(1)

    if args.convert_only:
        for fp, data in valid:
            convert_to_rtklib(fp, data)
        print("\nOpen in rtkplot: File → Open Solution 1 → .rtklib.pos")
        print("Plot Type → 'Position'")
        return

    # Primary ENU plot
    if args.compare:
        plot_compare(valid, show=show)
    else:
        for fp, data in valid:
            convert_to_rtklib(fp, data)  # always produce rtkplot file
            plot_kin_single(fp, data, show=show)

    # Additional plots
    if args.scatter or args.all_plots:
        plot_scatter_pride(valid, show=show)
    if args.nsat or args.all_plots:
        plot_nsat_pdop(valid, show=show)
    if args.summary or args.all_plots:
        plot_summary_bar_pride(valid, show=show)


if __name__ == "__main__":
    main()
