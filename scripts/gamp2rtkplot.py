#!/usr/bin/env python3
"""
gamp2rtkplot.py  —  Convert GAMP .pos (ECEF XYZ) to rtkplot-compatible
                    lat/lon/height format so you CAN open it in rtkplot.

USAGE:
    cd C:/PPP_PROJECT

    # Convert one file  (output: GAMP_work/result/cut02440.17o.rtklib.pos)
    python scripts/gamp2rtkplot.py GAMP_work/result/cut02440.17o.pos

    # Convert all .pos files in a folder:
    python scripts/gamp2rtkplot.py GAMP_work/result/

    # Convert and immediately open in rtkplot:
    python scripts/gamp2rtkplot.py --open GAMP_work/result/cut02440.17o.pos

THEN in rtkplot:
    File  →  Open Solution 1  →  select the .rtklib.pos file
    Plot Type dropdown  →  "Position"
    The E/N/U errors are stored in the sde/sdn/sdu columns.

GAMP .pos column layout:
    yr mo dy hr mn sec  GPS_week  GPS_TOW  X  Y  Z  dE  dN  dU  3D
    0  1  2  3  4  5    6         7        8  9  10 11  12  13  14
"""

import argparse
import math
import os
import subprocess
import sys


# ─────────────────────────────────────────────────────────────────────────────
# ECEF  →  WGS84 geodetic
# ─────────────────────────────────────────────────────────────────────────────

def ecef_to_geodetic(x, y, z):
    """Return (lat_deg, lon_deg, height_m) from ECEF XYZ (m)."""
    a = 6378137.0
    f = 1.0 / 298.257223563
    b = a * (1 - f)
    e2 = 1 - (b / a) ** 2
    lon = math.atan2(y, x)
    p = math.sqrt(x * x + y * y)
    lat = math.atan2(z, p * (1 - e2))
    for _ in range(10):
        sin_lat = math.sin(lat)
        N = a / math.sqrt(1 - e2 * sin_lat * sin_lat)
        lat_new = math.atan2(z + e2 * N * sin_lat, p)
        if abs(lat_new - lat) < 1e-12:
            lat = lat_new
            break
        lat = lat_new
    sin_lat = math.sin(lat)
    N = a / math.sqrt(1 - e2 * sin_lat * sin_lat)
    cos_lat = math.cos(lat)
    if abs(cos_lat) > 1e-10:
        h = p / cos_lat - N
    else:
        h = abs(z) / abs(sin_lat) - N * (1 - e2)
    return math.degrees(lat), math.degrees(lon), h


# ─────────────────────────────────────────────────────────────────────────────
# Conversion
# ─────────────────────────────────────────────────────────────────────────────

RTKLIB_HEADER = (
    "%  GPST                          "
    "latitude(deg) longitude(deg)  height(m)   "
    "Q  ns   sdn(m)   sde(m)   sdu(m)  "
    "sdne(m)  sdeu(m)  sdun(m) age(s)  ratio\n"
)


def convert_file(inpath):
    """
    Convert one GAMP .pos file to rtkplot-compatible format.
    Output file: <inpath>.rtklib.pos
    Returns output path, or None on error.
    """
    if not os.path.isfile(inpath):
        print(f"  ERROR: not found: {inpath}", file=sys.stderr)
        return None

    outpath = inpath + ".rtklib.pos"
    rows_written = 0
    first_yr = first_mo = first_dy = None

    with open(inpath, encoding="utf-8", errors="replace") as fin, \
            open(outpath, "w", newline="\n") as fout:

        fout.write(RTKLIB_HEADER)

        for line in fin:
            line = line.strip()
            if not line or line.startswith(("%", "#", "!")):
                continue
            cols = line.split()
            if len(cols) < 15:
                continue
            try:
                yr = int(cols[0])
                mo = int(cols[1])
                dy = int(cols[2])
                hr = int(cols[3])
                mn = int(cols[4])
                sc = float(cols[5])
                x = float(cols[8])
                y = float(cols[9])
                z = float(cols[10])
                dE = float(cols[11])
                dN = float(cols[12])
                dU = float(cols[13])
            except (ValueError, IndexError):
                continue

            if first_yr is None:
                first_yr, first_mo, first_dy = yr, mo, dy

            lat, lon, ht = ecef_to_geodetic(x, y, z)

            # rtkplot GPST timestamp — use the date from the file
            fout.write(
                f"{yr:04d}/{mo:02d}/{dy:02d} {hr:02d}:{mn:02d}:{sc:06.3f}   "
                f"{lat:14.9f}  {lon:14.9f}  {ht:10.4f}   "
                f"5  8   "          # Q=5 (float), ns=8 (placeholder)
                f"{dN:9.4f}   {dE:9.4f}   {dU:9.4f}   "
                f"0.0000   0.0000   0.0000   0.00   0.0\n"
            )
            rows_written += 1

    if rows_written == 0:
        print(
            f"  WARNING: {os.path.basename(inpath)} — no data rows converted.", file=sys.stderr)
        os.remove(outpath)
        return None

    print(f"  Converted {rows_written} epochs → {outpath}")
    return outpath


def convert_folder(folderpath):
    """Convert all .pos files in a folder (not .rtklib.pos files)."""
    pos_files = [
        os.path.join(folderpath, f)
        for f in os.listdir(folderpath)
        if f.endswith(".pos") and not f.endswith(".rtklib.pos")
    ]
    if not pos_files:
        print(f"  No .pos files found in: {folderpath}", file=sys.stderr)
        return []

    results = []
    for fp in sorted(pos_files):
        out = convert_file(fp)
        if out:
            results.append(out)
    return results


def open_in_rtkplot(converted_files):
    """Try to open the first converted file in rtkplot."""
    rtkplot_paths = [
        r"C:\Program Files\RTKLIB\bin\rtkplot.exe",
        r"C:\Program Files\RTKLIB_EX_2.5.0\rtkplot.exe",
    ]
    rtkplot_exe = next((p for p in rtkplot_paths if os.path.isfile(p)), None)
    if rtkplot_exe is None:
        print("  rtkplot.exe not found. Open manually:", file=sys.stderr)
        for f in converted_files:
            print(f"    {f}", file=sys.stderr)
        return

    if converted_files:
        args = [rtkplot_exe] + converted_files[:2]  # rtkplot accepts up to 2
        print(f"  Opening: {rtkplot_exe}")
        subprocess.Popen(args)


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Convert GAMP .pos (ECEF) to rtkplot-compatible lat/lon format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "inputs", nargs="+",
        help=".pos file(s) or folder(s) to convert"
    )
    parser.add_argument(
        "--open", action="store_true",
        help="Open the first converted file in rtkplot.exe automatically"
    )
    args = parser.parse_args()

    all_converted = []
    for inp in args.inputs:
        if os.path.isdir(inp):
            all_converted.extend(convert_folder(inp))
        elif os.path.isfile(inp):
            out = convert_file(inp)
            if out:
                all_converted.append(out)
        else:
            print(f"  ERROR: not found: {inp}", file=sys.stderr)

    if not all_converted:
        print("No files converted.", file=sys.stderr)
        sys.exit(1)

    print(f"\nDone. {len(all_converted)} file(s) converted.")
    print("To open in rtkplot:")
    print("  File → Open Solution 1 → select .rtklib.pos")
    print("  Plot Type → 'Position'  (E/N/U errors displayed)")

    if args.open:
        open_in_rtkplot(all_converted)


if __name__ == "__main__":
    main()
