#!/usr/bin/env python3
"""
plot_gamp_enu.py  —  Plot GAMP .pos output as ENU convergence curves.

This is the primary visualization tool for GAMP results because rtkplot
cannot read GAMP's ECEF XYZ format directly.

USAGE:
    cd C:/PPP_PROJECT/GAMP_work

    # Plot one file:
    python scripts/plot_gamp_enu.py result/cut02440.17o.pos

    # Plot two files side by side:
    python scripts/plot_gamp_enu.py result/cut02440.17o.pos result/jfng2440.17o.pos

    # Overlay two files on ONE axes (convergence comparison):
    python scripts/plot_gamp_enu.py --compare result/cut02440.17o.pos results_reference/result_GRCE_kin_DF_noGIM_wum/cut02440.17o.pos

    # No popup — just save PNG:
    python scripts/plot_gamp_enu.py --no-show result/cut02440.17o.pos

OUTPUT (saved next to each .pos file):
    <name>.pos.png     — ENU convergence plot
    <name>.pos.stats   — text statistics summary

GAMP .pos column layout:
    [0-5]  yr mo dy hr mn sec
    [6]    GPS week
    [7]    GPS TOW (sec)
    [8-10] ECEF X Y Z (m)
    [11]   dE error (m)  — East
    [12]   dN error (m)  — North
    [13]   dU error (m)  — Up
    [14]   3D error (m)

NOTES:
    - Empty .pos files (failed runs) are skipped with a warning.
    - Files with fewer than 10 epochs are considered failed/empty.
    - Convergence = first epoch where 2D error < 10 cm and stays < 10 cm for 10 min.
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
# Data reading
# ─────────────────────────────────────────────────────────────────────────────

def read_gamp_pos(filepath):
    """
    Read a GAMP .pos file.

    Returns a dict with numpy arrays:
        t   : time in hours from first epoch (float)
        E   : East error  (m)
        N   : North error (m)
        U   : Up error    (m)
        d3  : 3D error    (m)
        X, Y, Z : ECEF coordinates (m)
    Returns None if file is empty or unreadable.
    """
    if not os.path.isfile(filepath):
        print(f"  ERROR: File not found: {filepath}", file=sys.stderr)
        return None

    t_raw, X, Y, Z, E, N, U, d3 = [], [], [], [], [], [], [], []

    with open(filepath, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith(("%", "#", "!")):
                continue
            cols = line.split()
            if len(cols) < 15:
                continue
            try:
                hr = int(cols[3])
                mn = int(cols[4])
                sc = float(cols[5])
                t_raw.append(hr + mn / 60.0 + sc / 3600.0)
                X.append(float(cols[8]))
                Y.append(float(cols[9]))
                Z.append(float(cols[10]))
                E.append(float(cols[11]))
                N.append(float(cols[12]))
                U.append(float(cols[13]))
                d3.append(float(cols[14]))
            except (ValueError, IndexError):
                continue

    if len(t_raw) < 10:
        print(f"  WARNING: {os.path.basename(filepath)} — too few epochs ({len(t_raw)}), skipping.",
              file=sys.stderr)
        return None

    t_arr = np.array(t_raw, dtype=float)
    # Normalize: first epoch = 0 hours; handle midnight wrap
    t0 = t_arr[0]
    t_arr = t_arr - t0
    t_arr[t_arr < 0] += 24.0

    return {
        "t":  t_arr,
        "E":  np.array(E,  dtype=float),
        "N":  np.array(N,  dtype=float),
        "U":  np.array(U,  dtype=float),
        "d3": np.array(d3, dtype=float),
        "X":  np.array(X,  dtype=float),
        "Y":  np.array(Y,  dtype=float),
        "Z":  np.array(Z,  dtype=float),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Statistics
# ─────────────────────────────────────────────────────────────────────────────

def rms(arr):
    return float(np.sqrt(np.mean(arr ** 2)))


def convergence_time(E, N, U, t, h_thresh=0.10, v_thresh=0.20, window_min=10, interval_s=30):
    """
    Return first epoch time (hours) at which 2D stays < h_thresh m
    and U stays < v_thresh m for 'window_min' consecutive minutes.
    Returns None if convergence never happens.
    """
    window_epochs = max(1, int(window_min * 60 / interval_s))
    d2d = np.sqrt(E ** 2 + N ** 2)
    for i in range(len(t) - window_epochs):
        if (np.all(d2d[i:i + window_epochs] < h_thresh) and
                np.all(np.abs(U[i:i + window_epochs]) < v_thresh)):
            return t[i]
    return None


def stats_summary(data, label=""):
    half = len(data["t"]) // 2
    E2, N2, U2 = data["E"][half:], data["N"][half:], data["U"][half:]
    conv = convergence_time(data["E"], data["N"], data["U"], data["t"])
    lines = [
        f"=== {label} ===",
        f"  Epochs          : {len(data['t'])}",
        f"  Peak 3D error   : {data['d3'].max():.3f} m",
        f"  Convergence     : {f'{conv*60:.0f} min' if conv is not None else '>24h'}",
        f"  RMS (last 12h)  : E={rms(E2)*100:.2f} cm  N={rms(N2)*100:.2f} cm  U={rms(U2)*100:.2f} cm",
    ]
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Plotting helpers
# ─────────────────────────────────────────────────────────────────────────────

def _cap_ylim(ax, cap=1.0):
    """Auto-scale Y axis, but cap at ±cap metres."""
    lines = ax.get_lines()
    if not lines:
        return
    ymax = max(
        min(np.percentile(np.abs(ln.get_ydata()), 99), cap)
        for ln in lines if len(ln.get_ydata())
    )
    ax.set_ylim(-(ymax * 1.15), ymax * 1.15)


def _annotate_stats(ax, data):
    half = len(data["t"]) // 2
    E2, N2, U2 = data["E"][half:], data["N"][half:], data["U"][half:]
    conv = convergence_time(data["E"], data["N"], data["U"], data["t"])
    conv_str = f"{conv*60:.0f} min" if conv is not None else ">24h"
    txt = (
        f"RMS (last 12h):  E={rms(E2)*100:.1f}cm  "
        f"N={rms(N2)*100:.1f}cm  U={rms(U2)*100:.1f}cm\n"
        f"Convergence (2D<10cm):  {conv_str}"
    )
    ax.text(0.98, 0.02, txt,
            transform=ax.transAxes,
            fontsize=8,
            va="bottom",
            ha="right",
            bbox=dict(boxstyle="round,pad=0.3",
                      facecolor="white", alpha=0.85))


def _format_axes(ax, title=""):
    ax.axhline(0, color="k", linewidth=0.5, zorder=0)
    ax.axhline(0.10, color="gray", linewidth=0.5, linestyle=":", zorder=0)
    ax.axhline(-0.10, color="gray", linewidth=0.5, linestyle=":", zorder=0)
    ax.set_xlabel("Time from start (hours)", fontsize=9)
    ax.set_ylabel("Position Error (m)", fontsize=9)
    ax.set_title(title, fontsize=9)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.25)
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    _cap_ylim(ax)


# ─────────────────────────────────────────────────────────────────────────────
# Single-file plot
# ─────────────────────────────────────────────────────────────────────────────

def plot_single(filepath, show=True, save=True):
    data = read_gamp_pos(filepath)
    if data is None:
        return

    fig, ax = plt.subplots(figsize=(13, 5))
    t = data["t"]
    ax.plot(t, data["E"], "b-",  lw=0.9, label="East")
    ax.plot(t, data["N"], "g-",  lw=0.9, label="North")
    ax.plot(t, data["U"], "r-",  lw=0.9, label="Up")
    _annotate_stats(ax, data)
    _format_axes(ax, title=os.path.basename(filepath))

    summary = stats_summary(data, label=os.path.basename(filepath))
    print(summary)

    if save:
        png = filepath + ".png"
        fig.savefig(png, dpi=150, bbox_inches="tight")
        print(f"  Saved plot : {png}")
        stats_file = filepath + ".stats"
        with open(stats_file, "w") as f:
            f.write(summary + "\n")
        print(f"  Saved stats: {stats_file}")

    if show:
        plt.show()
    plt.close(fig)


# ─────────────────────────────────────────────────────────────────────────────
# Multi-file side-by-side plot
# ─────────────────────────────────────────────────────────────────────────────

def plot_side_by_side(filepaths, show=True, save=True):
    datasets = [(fp, read_gamp_pos(fp)) for fp in filepaths]
    valid = [(fp, d) for fp, d in datasets if d is not None]
    if not valid:
        print("No valid files to plot.", file=sys.stderr)
        return

    n = len(valid)
    fig, axes = plt.subplots(n, 1, figsize=(13, 4 * n), sharex=False)
    if n == 1:
        axes = [axes]

    for ax, (fp, data) in zip(axes, valid):
        t = data["t"]
        ax.plot(t, data["E"], "b-",  lw=0.9, label="East")
        ax.plot(t, data["N"], "g-",  lw=0.9, label="North")
        ax.plot(t, data["U"], "r-",  lw=0.9, label="Up")
        _annotate_stats(ax, data)
        _format_axes(ax, title=os.path.basename(fp))
        print(stats_summary(data, label=os.path.basename(fp)))

    fig.tight_layout()

    if save and valid:
        outdir = os.path.dirname(valid[0][0])
        png = os.path.join(outdir, "combined_ENU.png")
        fig.savefig(png, dpi=150, bbox_inches="tight")
        print(f"  Saved: {png}")

    if show:
        plt.show()
    plt.close(fig)


# ─────────────────────────────────────────────────────────────────────────────
# Overlay / comparison plot
# ─────────────────────────────────────────────────────────────────────────────

def plot_compare(filepaths, show=True, save=True):
    """Overlay all files on one set of axes — ideal for GPS-only vs multi-GNSS."""
    COLORS = plt.cm.tab10.colors

    datasets = [(fp, read_gamp_pos(fp)) for fp in filepaths]
    valid = [(fp, d) for fp, d in datasets if d is not None]
    if not valid:
        print("No valid files to plot.", file=sys.stderr)
        return

    fig, ax = plt.subplots(figsize=(14, 5))

    for idx, (fp, data) in enumerate(valid):
        c = COLORS[idx % 10]
        label = os.path.basename(os.path.dirname(fp)) or os.path.basename(fp)
        # Shorten long reference folder names
        label = label.replace("result_", "").replace(
            "_wum", "").replace("_kin_DF", "")
        t = data["t"]
        ax.plot(t, data["E"],  color=c, ls="-",  lw=0.8,  label=f"{label} E")
        ax.plot(t, data["N"],  color=c, ls="--",
                lw=0.7,  alpha=0.8, label=f"{label} N")
        ax.plot(t, data["U"],  color=c, ls=":",
                lw=0.7,  alpha=0.8, label=f"{label} U")
        print(stats_summary(data, label=label))

    ax.legend(fontsize=7, ncol=2, loc="upper right")
    _format_axes(ax, title="GAMP ENU Comparison")

    if save and valid:
        outdir = os.path.dirname(valid[0][0])
        png = os.path.join(outdir, "comparison_ENU.png")
        fig.savefig(png, dpi=150, bbox_inches="tight")
        print(f"\n  Saved: {png}")

    if show:
        plt.show()
    plt.close(fig)


# ─────────────────────────────────────────────────────────────────────────────
# Scatter plot  (E vs N — horizontal accuracy)
# ─────────────────────────────────────────────────────────────────────────────

def plot_scatter(filepaths, show=True, save=True):
    """
    East vs North scatter plot, coloured by time.
    Good for visualising horizontal accuracy distribution.
    """
    COLORS = plt.cm.tab10.colors
    datasets = [(fp, read_gamp_pos(fp)) for fp in filepaths]
    valid = [(fp, d) for fp, d in datasets if d is not None]
    if not valid:
        return

    multi = len(valid) > 1
    fig, ax = plt.subplots(figsize=(7, 6))

    for idx, (fp, data) in enumerate(valid):
        lbl = (os.path.basename(os.path.dirname(fp)) or os.path.basename(fp)) \
            .replace("result_", "").replace("_wum", "").replace("_kin_DF", "")
        c = COLORS[idx % 10] if multi else None
        half = len(data["t"]) // 2
        E_cm = data["E"] * 100
        N_cm = data["N"] * 100
        # First half slightly transparent (convergence period), second half solid
        sc1 = ax.scatter(E_cm[:half], N_cm[:half], s=3, alpha=0.25,
                         color=c or "steelblue", label=None)
        sc2 = ax.scatter(E_cm[half:], N_cm[half:], s=3, alpha=0.75,
                         color=c or "steelblue",
                         label=f"{lbl}  (last 12h)" if multi else "last 12h")
        half_rms = float(np.sqrt(np.mean(E_cm[half:] ** 2 + N_cm[half:] ** 2)))
        circle = plt.Circle((0, 0), half_rms, fill=False,
                            color=c or "steelblue", lw=0.8, ls="--", alpha=0.6)
        ax.add_patch(circle)

    ax.axhline(0, color="k", lw=0.5)
    ax.axvline(0, color="k", lw=0.5)
    # Equal aspect so circles look like circles
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_xlabel("East error (cm)", fontsize=9)
    ax.set_ylabel("North error (cm)", fontsize=9)
    ax.set_title("Horizontal scatter  (E vs N)", fontsize=9)
    ax.legend(fontsize=8, loc="best")
    ax.grid(True, alpha=0.25)
    txt = "Dashed circle = RMS radius (last 12h)\nLight points = convergence period"
    ax.text(0.02, 0.98, txt, transform=ax.transAxes, fontsize=7.5, va="top",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.85))

    if save and valid:
        png = valid[0][0] + ".scatter.png"
        fig.savefig(png, dpi=150, bbox_inches="tight")
        print(f"  Saved: {png}")
    if show:
        plt.show()
    plt.close(fig)


# ─────────────────────────────────────────────────────────────────────────────
# 3D / horizontal error time series
# ─────────────────────────────────────────────────────────────────────────────

def plot_3d_error(filepaths, show=True, save=True):
    """
    Two-panel plot: top = 3D error, bottom = horizontal (2D) error.
    Shows full convergence behaviour and final precision together.
    """
    COLORS = plt.cm.tab10.colors
    datasets = [(fp, read_gamp_pos(fp)) for fp in filepaths]
    valid = [(fp, d) for fp, d in datasets if d is not None]
    if not valid:
        return

    fig, (ax3, ax2) = plt.subplots(2, 1, figsize=(13, 7), sharex=True)

    for idx, (fp, data) in enumerate(valid):
        c = COLORS[idx % 10]
        lbl = (os.path.basename(os.path.dirname(fp)) or os.path.basename(fp)) \
            .replace("result_", "").replace("_wum", "").replace("_kin_DF", "")
        t = data["t"]
        d2d = np.sqrt(data["E"] ** 2 + data["N"] ** 2)
        ax3.plot(t, data["d3"], color=c, lw=0.9, label=f"{lbl} 3D")
        ax2.plot(t, d2d,        color=c, lw=0.9, label=f"{lbl} 2D")

    for ax, ylabel, cap in [(ax3, "3D error (m)", 2.0), (ax2, "2D error (m)", 1.0)]:
        ax.axhline(0.10, color="gray", lw=0.5, ls=":", zorder=0)
        ax.set_ylabel(ylabel, fontsize=9)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.25)
        _cap_ylim(ax, cap=cap)

    ax2.set_xlabel("Time from start (hours)", fontsize=9)
    ax3.set_title("GAMP — 3D and Horizontal Error over Time", fontsize=9)
    fig.tight_layout()

    if save and valid:
        png = valid[0][0] + ".3d.png"
        fig.savefig(png, dpi=150, bbox_inches="tight")
        print(f"  Saved: {png}")
    if show:
        plt.show()
    plt.close(fig)


# ─────────────────────────────────────────────────────────────────────────────
# Summary bar chart  (convergence + RMS across scenarios)
# ─────────────────────────────────────────────────────────────────────────────

def plot_summary_bar(filepaths, show=True, save=True):
    """
    Bar chart comparing convergence time and post-convergence RMS across
    multiple scenarios / stations.  Great for report figures.
    """
    records = []
    for fp in filepaths:
        data = read_gamp_pos(fp)
        if data is None:
            continue
        lbl = (os.path.basename(os.path.dirname(fp)) or os.path.basename(fp)) \
            .replace("result_", "").replace("_wum", "").replace("_kin_DF", "")
        half = len(data["t"]) // 2
        E2, N2, U2 = data["E"][half:], data["N"][half:], data["U"][half:]
        conv = convergence_time(data["E"], data["N"], data["U"], data["t"])
        records.append({
            "label": lbl,
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
    fig, (ax_conv, ax_rms) = plt.subplots(
        1, 2, figsize=(max(10, n * 2.5 + 3), 5))

    # Convergence time
    vals = [r["conv"] for r in records]
    bars = ax_conv.bar(x, vals, width=0.55, color="steelblue", alpha=0.85)
    for bar, v in zip(bars, vals):
        if not np.isnan(v):
            ax_conv.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                         f"{v:.0f}", ha="center", va="bottom", fontsize=8)
    ax_conv.set_xticks(x)
    ax_conv.set_xticklabels([r["label"] for r in records],
                            rotation=15, ha="right", fontsize=8)
    ax_conv.set_ylabel("Convergence time (min)", fontsize=9)
    ax_conv.set_title("Convergence Time  (2D < 10 cm)", fontsize=9)
    ax_conv.grid(axis="y", alpha=0.3)

    # RMS bars
    ax_rms.bar(x - w, [r["rms_E"] for r in records], w,
               label="East",  color="royalblue", alpha=0.85)
    ax_rms.bar(x,     [r["rms_N"] for r in records], w,
               label="North", color="forestgreen", alpha=0.85)
    ax_rms.bar(x + w, [r["rms_U"] for r in records], w,
               label="Up",    color="tomato", alpha=0.85)
    ax_rms.set_xticks(x)
    ax_rms.set_xticklabels([r["label"] for r in records],
                           rotation=15, ha="right", fontsize=8)
    ax_rms.set_ylabel("RMS error  (cm)", fontsize=9)
    ax_rms.set_title("Post-Convergence RMS  (last 12 h)", fontsize=9)
    ax_rms.legend(fontsize=8)
    ax_rms.grid(axis="y", alpha=0.3)

    fig.suptitle("GAMP PPP Scenario Comparison",
                 fontsize=10, fontweight="bold")
    fig.tight_layout()

    if save and filepaths:
        outdir = os.path.dirname(filepaths[0])
        png = os.path.join(outdir, "summary_bar.png")
        fig.savefig(png, dpi=150, bbox_inches="tight")
        print(f"  Saved: {png}")
    if show:
        plt.show()
    plt.close(fig)


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Plot GAMP .pos ENU position errors",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("files", nargs="+", help=".pos file(s) to plot")
    parser.add_argument("--compare", action="store_true",
                        help="Overlay all files on one axes (convergence comparison)")
    parser.add_argument("--scatter", action="store_true",
                        help="Horizontal scatter plot  (E vs N)")
    parser.add_argument("--d3", action="store_true",
                        help="3D + horizontal error time series")
    parser.add_argument("--summary", action="store_true",
                        help="Bar chart: convergence + RMS across scenarios")
    parser.add_argument("--all", dest="all_plots", action="store_true",
                        help="Generate all plot types (ENU + scatter + 3D + summary)")
    parser.add_argument("--no-show", action="store_true",
                        help="Save PNG without opening GUI window")
    args = parser.parse_args()

    # Validate all files exist
    missing = [f for f in args.files if not os.path.isfile(f)]
    if missing:
        for m in missing:
            print(f"  ERROR: not found: {m}", file=sys.stderr)
        sys.exit(1)

    show = not args.no_show

    # Primary ENU plot
    if args.compare:
        plot_compare(args.files, show=show)
    elif len(args.files) == 1 and not (args.scatter or args.d3 or args.summary or args.all_plots):
        plot_single(args.files[0], show=show)
    elif not (args.scatter or args.d3 or args.summary or args.all_plots):
        plot_side_by_side(args.files, show=show)
    elif not any([args.scatter, args.d3, args.summary, args.all_plots]):
        if len(args.files) == 1:
            plot_single(args.files[0], show=show)
        else:
            plot_side_by_side(args.files, show=show)

    # Additional plots
    if args.scatter or args.all_plots:
        plot_scatter(args.files, show=show)
    if args.d3 or args.all_plots:
        plot_3d_error(args.files, show=show)
    if args.summary or args.all_plots:
        plot_summary_bar(args.files, show=show)
    # all_plots also produces the base ENU plot
    if args.all_plots:
        if len(args.files) == 1:
            plot_single(args.files[0], show=show)
        else:
            plot_side_by_side(args.files, show=show)


if __name__ == "__main__":
    main()
