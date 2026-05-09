#!/usr/bin/env python3
"""
plot_pride_results.py
=====================
Plot PRIDE-PPP-AR output files for all stations.

Generates:
  1. Phase residuals time-series (per station, per constellation)
  2. ZTD (Zenith Troposphere Delay) time-series â€” all stations overlaid
  3. Receiver clock offset time-series
  4. Summary AR fix rate bar chart

Usage:
    python scripts/plot_pride_results.py

Output files saved to: results/PRIDE_plots/
"""

from datetime import datetime, timedelta
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import os
import re
import numpy as np
import matplotlib
matplotlib.use('Agg')  # non-interactive backend

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Configuration
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

PRIDE_RUNS = {
    "HKWS": r"C:\PPP_PROJECT\PRIDE_work\runs\HKWS_run\2026\015",
    "WUH2": r"C:\PPP_PROJECT\PRIDE_work\runs\WUH_run\2026\015",
    "KIRU": r"C:\PPP_PROJECT\PRIDE_work\runs\KIRU_run\2026\015",
    "ZIM2": r"C:\PPP_PROJECT\PRIDE_work\runs\ZIM2_run\2026\015",
}

OUTPUT_DIR = r"C:\PPP_PROJECT\results\PRIDE_plots"
SESSION_DATE = datetime(2026, 1, 15, 0, 0, 0)

STATION_COLORS = {
    "HKWS": "#1f77b4",   # blue
    "WUH2": "#ff7f0e",   # orange
    "KIRU": "#2ca02c",   # green
    "ZIM2": "#d62728",   # red
}

GNSS_COLORS = {
    "G": "#1f77b4",   # GPS â€” blue
    "E": "#2ca02c",   # Galileo â€” green
    "C": "#ff7f0e",   # BDS â€” orange
}

# AR fix rates from processing log (for stations with completed AR=Y)
AR_RATES = {
    "HKWS": {"WL": 84.9, "NL": 100.0},
    "WUH2": {"WL": 89.0, "NL": 97.7},
    "KIRU": {"WL": 98.1, "NL": 99.7},
    "ZIM2": {"WL": 88.1, "NL": 100.0},
}

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Helper functions
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def epoch_to_datetime(year, month, day, hour, minute, second):
    """Convert PRIDE epoch tokens to a Python datetime."""
    return datetime(int(year), int(month), int(day),
                    int(hour), int(minute), int(float(second)))


def find_file(run_dir, prefix):
    """Find a file in run_dir whose name starts with prefix (case-insensitive)."""
    for fname in os.listdir(run_dir):
        if fname.lower().startswith(prefix.lower()):
            return os.path.join(run_dir, fname)
    return None


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Parsers
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def parse_ztd(ztd_file):
    """
    Parse PRIDE ZTD output file.

    Format (after END OF HEADER):
        YYYY M D H MM SS.ssss  ZTD(m)  ZTD_sigma  HTG_NS(m)

    Returns: (times: list[datetime], ztd: list[float])
    """
    times, ztd_vals = [], []
    in_data = False
    try:
        with open(ztd_file, "r") as f:
            for line in f:
                if "END OF HEADER" in line:
                    in_data = True
                    continue
                if not in_data:
                    continue
                parts = line.split()
                if len(parts) < 7:
                    continue
                try:
                    dt = epoch_to_datetime(*parts[:6])
                    ztd = float(parts[6])
                    times.append(dt)
                    ztd_vals.append(ztd)
                except (ValueError, IndexError):
                    continue
    except FileNotFoundError:
        print(f"  [WARNING] ZTD file not found: {ztd_file}")
    return times, ztd_vals


def parse_residuals(res_file, max_epochs=2880):
    """
    Parse PRIDE phase residuals file.

    Returns:
        epochs: list[datetime]
        data:   dict[prn] -> {"times": [], "phase_res": [], "elev": []}
    """
    sat_data = {}
    times_by_epoch = {}   # epoch_sec -> datetime
    in_data = False

    try:
        with open(res_file, "r", encoding="utf-8", errors="ignore") as f:
            current_time = None
            epoch_count = 0

            for line in f:
                line = line.rstrip()
                if "END OF HEADER" in line:
                    in_data = True
                    continue
                if not in_data:
                    continue

                if line.startswith("TIM "):
                    parts = line.split()
                    if len(parts) >= 8:
                        try:
                            current_time = epoch_to_datetime(*parts[1:7])
                            epoch_count += 1
                            if epoch_count > max_epochs:
                                break
                        except ValueError:
                            current_time = None
                    continue

                if current_time is None:
                    continue

                parts = line.split()
                if len(parts) < 8:
                    continue

                prn = parts[0]
                if not re.match(r"^[GEC]\d{2}$", prn):
                    continue

                try:
                    phase_res = float(parts[1]) * 1000.0  # convert m -> mm
                    elev = float(parts[6])
                except (ValueError, IndexError):
                    continue

                if prn not in sat_data:
                    sat_data[prn] = {"times": [], "phase_res": [], "elev": []}
                sat_data[prn]["times"].append(current_time)
                sat_data[prn]["phase_res"].append(phase_res)
                sat_data[prn]["elev"].append(elev)

    except FileNotFoundError:
        print(f"  [WARNING] Residuals file not found: {res_file}")

    return sat_data


def parse_clock(rck_file):
    """
    Parse PRIDE receiver clock file.

    Format lines (after END OF HEADER):
        YYYY M D H MM SS.ssss  clk_G(s)  clk_E(s)  clk_C(s)  clk_C3(s)

    Returns: (times, clk_G, clk_E, clk_C) all in nanoseconds
    """
    times, clk_G, clk_E, clk_C = [], [], [], []
    in_data = False
    NS_PER_S = 1e9

    try:
        with open(rck_file, "r") as f:
            for line in f:
                if "END OF HEADER" in line:
                    in_data = True
                    continue
                if not in_data:
                    continue
                parts = line.split()
                if len(parts) < 8:
                    continue
                try:
                    dt = epoch_to_datetime(*parts[:6])
                    g = float(parts[6]) * NS_PER_S
                    e = float(parts[7]) * NS_PER_S if len(parts) > 7 else None
                    c = float(parts[8]) * NS_PER_S if len(parts) > 8 else None
                    times.append(dt)
                    clk_G.append(g)
                    clk_E.append(e)
                    clk_C.append(c)
                except (ValueError, IndexError):
                    continue
    except FileNotFoundError:
        print(f"  [WARNING] Clock file not found: {rck_file}")

    return times, clk_G, clk_E, clk_C


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Plot functions
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def plot_ztd_all_stations(stations_ztd, output_dir):
    """Plot ZTD time-series for all stations on one figure."""
    fig, ax = plt.subplots(figsize=(12, 5))

    for station, (times, ztd) in stations_ztd.items():
        if not times:
            continue
        ax.plot(times, ztd, label=station, color=STATION_COLORS[station],
                linewidth=1.0, alpha=0.85)

    ax.set_xlabel("UTC Time (2026-01-15)")
    ax.set_ylabel("ZTD (m)")
    ax.set_title(
        "PRIDE-PPP-AR: Zenith Troposphere Delay â€” All Stations\n2026-01-15")
    ax.legend(loc="upper right")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=3))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30)
    ax.grid(True, alpha=0.3)

    ax.annotate("WUH2 highest (continental, winter fog)\n"
                "HKWS intermediate (subtropical)\n"
                "KIRU lowest (cold, subarctic Sweden)",
                xy=(0.02, 0.05), xycoords="axes fraction", fontsize=8,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7))

    plt.tight_layout()
    out = os.path.join(output_dir, "PRIDE_ZTD_all_stations.png")
    plt.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  Saved: {out}")


def plot_phase_residuals(station, sat_data, output_dir):
    """Plot phase residuals time-series for one station, by constellation."""
    gnss_groups = {"G": [], "E": [], "C": []}
    for prn in sat_data:
        prefix = prn[0]
        if prefix in gnss_groups:
            gnss_groups[prefix].append(prn)

    active_groups = {k: v for k, v in gnss_groups.items() if v}
    if not active_groups:
        print(f"  No residuals data for {station}")
        return

    fig, axes = plt.subplots(len(active_groups), 1,
                             figsize=(12, 3.5 * len(active_groups)),
                             sharex=True)
    if len(active_groups) == 1:
        axes = [axes]

    gnss_names = {"G": "GPS", "E": "Galileo", "C": "BDS"}

    for ax, (gnss, prns) in zip(axes, active_groups.items()):
        color = GNSS_COLORS[gnss]
        all_res = []
        for prn in sorted(prns):
            d = sat_data[prn]
            res = np.array(d["phase_res"])
            times = d["times"]
            # Filter out extreme outliers for display (>100mm = likely cycle slip)
            mask = np.abs(res) <= 100
            ax.plot([t for t, m in zip(times, mask) if m],
                    res[mask],
                    ".", markersize=1.5, color=color, alpha=0.4)
            all_res.extend(res[mask].tolist())

        rms = np.sqrt(np.mean(np.square(all_res))) if all_res else 0.0
        ax.set_ylabel(f"{gnss_names[gnss]}\nRes (mm)")
        ax.set_ylim(-60, 60)
        ax.axhline(0, color="black", linewidth=0.5)
        ax.grid(True, alpha=0.3)
        ax.text(0.99, 0.92, f"RMS={rms:.1f} mm  N_sat={len(prns)}",
                transform=ax.transAxes, ha="right", fontsize=9,
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8))

    axes[-1].set_xlabel("UTC Time (2026-01-15)")
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    axes[-1].xaxis.set_major_locator(mdates.HourLocator(interval=3))
    plt.setp(axes[-1].xaxis.get_majorticklabels(), rotation=30)

    fig.suptitle(f"PRIDE-PPP-AR: Phase Residuals â€” {station}  (2026-01-15)",
                 fontsize=12, y=1.01)
    plt.tight_layout()
    out = os.path.join(output_dir, f"PRIDE_residuals_{station}.png")
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out}")


def plot_ar_rates(output_dir):
    """Bar chart of WL and NL ambiguity fix rates per station."""
    stations = [s for s, r in AR_RATES.items() if r["WL"] is not None]
    x = np.arange(len(stations))
    wl = [AR_RATES[s]["WL"] for s in stations]
    nl = [AR_RATES[s]["NL"] for s in stations]

    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 5))
    bars1 = ax.bar(x - width/2, wl, width, label="WL Fix Rate (%)",
                   color=[STATION_COLORS[s] for s in stations], alpha=0.7)
    bars2 = ax.bar(x + width/2, nl, width, label="NL Fix Rate (%)",
                   color=[STATION_COLORS[s] for s in stations], alpha=1.0,
                   edgecolor="black", linewidth=0.8)

    ax.set_xticks(x)
    ax.set_xticklabels(stations, fontsize=12)
    ax.set_ylabel("Fix Rate (%)")
    ax.set_ylim(60, 105)
    ax.set_title(
        "PRIDE-PPP-AR: Ambiguity Resolution Fix Rates\n2026-01-15 (AR=Y runs)")
    ax.axhline(100, color="gray", linestyle="--", linewidth=0.8, alpha=0.5)

    # Legend: use two neutral patches to show WL (faded) vs NL (solid+edge)
    from matplotlib.patches import Patch
    legend_handles = [
        Patch(facecolor="gray", alpha=0.7,
              label="WL Fix Rate  (left bar, faded)"),
        Patch(facecolor="gray", alpha=1.0, edgecolor="black", linewidth=0.8,
              label="NL Fix Rate  (right bar, solid)"),
    ]
    ax.legend(handles=legend_handles, fontsize=9, loc="lower right")

    # Value labels on bars
    for bar in bars1:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 0.3, f"{h:.1f}%",
                ha="center", va="bottom", fontsize=9)
    for bar in bars2:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 0.3, f"{h:.1f}%",
                ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    out = os.path.join(output_dir, "PRIDE_AR_fix_rates.png")
    plt.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  Saved: {out}")


def plot_clock(station, times, clk_G, clk_E, clk_C, output_dir):
    """Plot receiver clock offset time-series."""
    if not times:
        print(f"  No clock data for {station}")
        return

    # Remove GPS mean drift (de-trend) for visualization
    if clk_G:
        g = np.array(clk_G)
        g -= g[0]  # relative to first epoch
    else:
        g = None

    fig, axes = plt.subplots(2, 1, figsize=(12, 6), sharex=True)

    # Top: GPS receiver clock (de-trended)
    if g is not None:
        axes[0].plot(times, g, color=GNSS_COLORS["G"], linewidth=0.8,
                     label="GPS clock (de-trended)")
    axes[0].set_ylabel("GPS clock (ns)")
    axes[0].legend(loc="upper right")
    axes[0].grid(True, alpha=0.3)

    # Bottom: ISB (Inter-System Bias) = GAL_clk - GPS_clk, BDS_clk - GPS_clk
    if clk_E and clk_G:
        isb_gal = [e - gg for e, gg in zip(clk_E, clk_G)
                   if e is not None and gg is not None]
        t_gal = [t for t, e, gg in zip(times, clk_E, clk_G)
                 if e is not None and gg is not None]
        if isb_gal:
            axes[1].plot(t_gal, isb_gal, color=GNSS_COLORS["E"], linewidth=0.8,
                         label="GAL ISB")
    if clk_C and clk_G:
        isb_bds = [c - gg for c, gg in zip(clk_C, clk_G)
                   if c is not None and gg is not None]
        t_bds = [t for t, c, gg in zip(times, clk_C, clk_G)
                 if c is not None and gg is not None]
        if isb_bds:
            axes[1].plot(t_bds, isb_bds, color=GNSS_COLORS["C"], linewidth=0.8,
                         label="BDS ISB")

    axes[1].set_ylabel("ISB vs GPS (ns)")
    axes[1].legend(loc="upper right")
    axes[1].set_xlabel("UTC Time (2026-01-15)")
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    axes[1].xaxis.set_major_locator(mdates.HourLocator(interval=3))
    axes[1].grid(True, alpha=0.3)
    plt.setp(axes[1].xaxis.get_majorticklabels(), rotation=30)

    fig.suptitle(f"PRIDE-PPP-AR: Receiver Clock â€” {station}  (2026-01-15)")
    plt.tight_layout()
    out = os.path.join(output_dir, f"PRIDE_clock_{station}.png")
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out}")


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Main
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def main():
    ensure_dir(OUTPUT_DIR)

    # â”€â”€ Plot 1: AR fix rates (no file parsing needed) â”€â”€
    print("Plotting AR fix rates...")
    plot_ar_rates(OUTPUT_DIR)

    # â”€â”€ Collect ZTD for all stations â”€â”€
    stations_ztd = {}
    for station, run_dir in PRIDE_RUNS.items():
        ztd_file = find_file(run_dir, "ztd_")
        if ztd_file:
            print(f"Parsing ZTD for {station}: {os.path.basename(ztd_file)}")
            times, ztd = parse_ztd(ztd_file)
            stations_ztd[station] = (times, ztd)
        else:
            print(f"  [SKIP] No ZTD file found for {station} in {run_dir}")

    # â”€â”€ Plot 2: ZTD all stations â”€â”€
    if stations_ztd:
        print("Plotting ZTD (all stations)...")
        plot_ztd_all_stations(stations_ztd, OUTPUT_DIR)

    # â”€â”€ Per-station: residuals + clock â”€â”€
    for station, run_dir in PRIDE_RUNS.items():
        print(f"\n--- {station} ---")

        # Phase residuals
        res_file = find_file(run_dir, "res_")
        if res_file:
            print(f"  Parsing residuals: {os.path.basename(res_file)} ...")
            sat_data = parse_residuals(res_file)
            plot_phase_residuals(station, sat_data, OUTPUT_DIR)
        else:
            print(f"  [SKIP] No residuals file found for {station}")

        # Receiver clock
        rck_file = find_file(run_dir, "rck_")
        if rck_file:
            print(f"  Parsing clock: {os.path.basename(rck_file)} ...")
            times, clk_G, clk_E, clk_C = parse_clock(rck_file)
            plot_clock(station, times, clk_G, clk_E, clk_C, OUTPUT_DIR)
        else:
            print(f"  [SKIP] No clock file found for {station}")

    print(f"\nAll plots saved to: {OUTPUT_DIR}")
    print("All plots saved to: " + OUTPUT_DIR)


if __name__ == "__main__":
    main()
