#!/usr/bin/env python3
"""
🌍 MGEX Station Status Checker & Analysis Tool
================================================
Reads IGS MGEX status files and generates comprehensive markdown reports.
Checks file sizes, epoch counts, constellations, and PPP suitability.

UPDATED: 2026-05-01
- Station file verification
- MD5 checksum validation  
- Epoch counting
- Constellation detection
- PPP tool recommendations
- Team-shareable markdown reports

Usage:
    python check_station.py BJFS                          # Detailed report for 1 station
    python check_station.py BJFS GOLD                     # Multiple stations
    python check_station.py --list                        # List ALL stations with ratings
    python check_station.py --list --min-const 4         # Only stations with 4+ constellations
    python check_station.py --list --quality 0-1         # Only excellent/good quality (V=0,1)
    python check_station.py --list --sort-by reliability # Sort by reliability score
    python check_station.py --list --multi-only          # Multi-GNSS only (skip GPS-only)
    python check_station.py --list --gps-only            # GPS-only stations

Requirements:
    - Status files at: C:\\PPP_PROJECT\\Old_data\\products\\status\\
    - Observation files at: C:\\PPP_PROJECT\\Old_data\\data\\
    - Outputs saved to: C:\\PPP_PROJECT\\station_reports\\

Output:
    Markdown report saved to: C:\\PPP_PROJECT\\station_reports\\station_<ID>_analysis.md
"""

import sys
import os
import re
import datetime
import argparse
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime as dt

# Fix Unicode output on Windows (emojis, arrows, etc.)
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# ==============================================================================
#  V2 PARSER  (26015_status.txt)
#  Column layout (0-based):
#  0-3   Mon.ID
#  5-8   RNX Ver
#  9-11  Dly(H)
#  12-16 Dly(M)
#  17-21 No.Exp   ... etc (space-separated numerics first)
#  then fixed-width fields for receiver (20), antenna (20), marker, domes, type
#  then G R E S flags (each X or space)
#  then MD5
# ==============================================================================


def parse_v2_status(filepath: Path) -> dict:
    stations = {}
    with open(filepath, encoding="utf-8", errors="replace") as f:
        for line in f:
            raw = line.rstrip("\n")
            if len(raw) < 4:
                continue
            sid = raw[:4].strip().upper()
            if not sid or not re.match(r'^[A-Z0-9]{2,4}$', sid):
                continue
            rest = raw[4:].strip()
            if not rest:
                stations[sid] = {"id": sid, "v2_data": False}
                continue

            parts = raw.split()
            try:
                rec = {
                    "id":       sid,
                    "v2_data":  True,
                    "rnx_ver":  parts[1],
                    "dly_h":    int(parts[2]),
                    "dly_m":    int(parts[3]),
                    "no_exp":   int(parts[4]),
                    "no_obs":   int(parts[5]),
                    "pts_del":  int(parts[6]),
                    "pct":      float(parts[7]),
                    "mp1":      float(parts[8]),
                    "mp2":      float(parts[9]),
                    "pos_diff": float(parts[10]),
                    "no_slips": float(parts[11]),
                    "v_flag":   parts[12],
                }
            except (IndexError, ValueError):
                stations[sid] = {"id": sid, "v2_data": False}
                continue

            # Receiver (20 chars), Antenna (20 chars) — fixed width fields
            # They start after the 13 space-separated numeric tokens
            # Easiest: use the raw line and known column offsets
            # From analysis: receiver starts at ~col 77, antenna at ~col 98
            # But col positions vary; find them by walking past the numeric block
            numeric_end = 0
            tok_count = 0
            i = 5  # skip station ID (4) + space (1)
            while tok_count < 13 and i < len(raw):
                while i < len(raw) and raw[i] == ' ':
                    i += 1
                while i < len(raw) and raw[i] != ' ':
                    i += 1
                tok_count += 1
            # i is now at end of 13th token
            while i < len(raw) and raw[i] == ' ':
                i += 1
            recv_start = i
            recv_end = min(recv_start + 20, len(raw))
            ant_start = min(recv_end + 1, len(raw))
            ant_end = min(ant_start + 20, len(raw))

            rec["recv_type"] = raw[recv_start:recv_end].strip()
            rec["ant_type"] = raw[ant_start:ant_end].strip()

            # Marker name, DOMES, type, constellations, MD5
            remainder = raw[ant_end:].split()
            rec["mkr_name"] = remainder[0] if len(remainder) > 0 else ""
            rec["mkr_num"] = remainder[1] if len(remainder) > 1 else ""
            rec["typ"] = remainder[2] if len(remainder) > 2 else ""

            # V2 constellation flags: G R E S (4 possible X markers)
            # Find "M " or "G " marker for type, then X flags follow
            m_match = re.search(r'\s(M|G)\s+((?:[X ]\s*){1,4})', raw[ant_end:])
            if m_match:
                flag_str = m_match.group(2)
                labels_v2 = ["G", "R", "E", "S"]
                flags = flag_str.split()
                rec["constellations_v2"] = [labels_v2[j] for j, f in enumerate(flags)
                                            if f == "X" and j < len(labels_v2)]
            else:
                rec["constellations_v2"] = []

            # MD5 = last 32-char hex token
            md5_tok = [t for t in raw.split() if re.match(
                r'^[0-9a-f]{32}$', t)]
            rec["md5"] = md5_tok[0] if md5_tok else ""

            stations[sid] = rec
    return stations


# ==============================================================================
#  V3 PARSER  (26015_V3status.txt)
#  Column layout (0-based, from file header):
#  0-3   Short ID
#  5-13  Full 9-char ID
#  15-18 RNX Ver
#  19-21 Dly(H)
#  22-26 Dly(M)
#  28    V flag
#  30-49 Receiver (20 chars)
#  51-70 Antenna (20 chars)
#  72-75 Mkr Name
#  76-84 Marker Number
#  86-88 Typ
#  90-   G R E C J S I flags (each X or space, space-separated)
#  last  MD5
# ==============================================================================

def parse_v3_status(filepath: Path) -> dict:
    stations = {}
    LABELS_V3 = ["G", "R", "E", "C", "J", "S", "I"]

    with open(filepath, encoding="utf-8", errors="replace") as f:
        for line in f:
            raw = line.rstrip("\n")
            if len(raw) < 4:
                continue
            sid = raw[:4].strip().upper()
            if not sid or not re.match(r'^[A-Z0-9]{2,4}$', sid):
                continue

            rest = raw[4:].strip()
            if not rest:
                stations[sid] = {"id": sid, "v3_data": False, "full_id": "",
                                 "rnx_ver": "", "constellations_v3": [], "md5": ""}
                continue

            parts = raw.split()
            # Need at least: ID FullID RNXver DlyH DlyM Vflag
            if len(parts) < 6:
                stations[sid] = {"id": sid, "v3_data": False, "full_id": parts[1] if len(parts) > 1 else "",
                                 "rnx_ver": "", "constellations_v3": [], "md5": ""}
                continue

            rec = {
                "id":      sid,
                "v3_data": True,
                "full_id": parts[1] if len(parts[1]) == 9 else "",
                "rnx_ver": parts[2],
                "dly_h":   _safe_int(parts[3]),
                "dly_m":   _safe_int(parts[4]),
                "v_flag":  parts[5],
            }

            # Receiver and antenna — find " M  " or "  M  " in line
            # Receiver is 20 chars before antenna which is 20 chars before marker
            # Strategy: locate the "M " or "G " type token and work backwards
            # From empirical testing: receiver ends just before the antenna section
            # which ends just before the marker section
            # Use the "  M  " or "  G  " pattern to anchor
            m_pos = re.search(r'  (M|G)\s+', raw)
            if m_pos:
                type_char = m_pos.group(1)
                rec["typ"] = type_char
                before_type = raw[:m_pos.start()].rstrip()
                # antenna = last 20 chars of before_type (after stripping)
                ant_end = len(before_type)
                ant_start = max(0, ant_end - 20)
                rec["ant_type"] = before_type[ant_start:ant_end].strip()
                # receiver = 20 chars before that
                recv_end = ant_start
                recv_start = max(0, recv_end - 20)
                rec["recv_type"] = before_type[recv_start:recv_end].strip()

                # After "M " comes constellation flags then marker fields
                after_type = raw[m_pos.end():]
                # constellation flags: up to 7 X or space tokens before the MD5
                md5_tok = [t for t in after_type.split(
                ) if re.match(r'^[0-9a-f]{32}$', t)]
                rec["md5"] = md5_tok[0] if md5_tok else ""

                # Between M and MD5, the flags are X separated by spaces
                # Find marker name and DOMES number (they appear as word tokens not X/space)
                # Pattern: flags (X or space), then marker_name, domes, then X X X...
                # Actually the full line after M is: X X X X X X X marker_name domes_num md5
                # Or sometimes:  X X X   marker_name ...  md5
                # Simplest: collect all X tokens up to first non-X, non-space alphabetic token
                flag_section = after_type
                const = []
                tok_iter = flag_section.split()
                for ti, tok in enumerate(tok_iter):
                    if tok == "X" and len(const) < 7:
                        const.append(LABELS_V3[len(const)])
                    elif tok not in ("X", "") and not re.match(r'^[0-9a-f]{32}$', tok) and len(const) < 7:
                        # non-X token — could be marker name or blank constellation
                        # check if next tokens are X (meaning this is a gap)
                        # if it's a multi-char alpha-numeric token, it's likely marker name
                        if len(tok) >= 4:
                            break  # reached marker section
                        # skip
                rec["constellations_v3"] = const

                # Marker name and DOMES — tokens after the flag section
                # Find first token that's not X and not MD5
                non_flag = [t for t in tok_iter
                            if t != "X" and not re.match(r'^[0-9a-f]{32}$', t)
                            and len(t) >= 2]
                rec["mkr_name"] = non_flag[0] if len(non_flag) > 0 else ""
                rec["mkr_num"] = non_flag[1] if len(non_flag) > 1 else ""
            else:
                rec["recv_type"] = ""
                rec["ant_type"] = ""
                rec["typ"] = ""
                rec["constellations_v3"] = []
                rec["mkr_name"] = ""
                rec["mkr_num"] = ""
                rec["md5"] = ""

            stations[sid] = rec
    return stations


def _safe_int(s):
    try:
        return int(s)
    except (ValueError, TypeError):
        return None


# ==============================================================================
#  SCORING AND LABELS
# ==============================================================================

V_FLAG_LABELS = {
    "0": ("Excellent", "Normal full-quality data"),
    "1": ("Good",      "Minor issues, still fully usable for PPP"),
    "2": ("Partial",   "Some data hours missing"),
    "3": ("Mixed",     "Some observation types absent"),
    "4": ("Low",       "Low quality — verify before use"),
    "9": ("RT",        "Real-time / sub-hourly delivery — top tier"),
}

CONSTELLATION_NAMES = {
    "G": "GPS (USA)",        "R": "GLONASS (Russia)",
    "E": "Galileo (EU)",     "C": "BeiDou (China)",
    "J": "QZSS (Japan)",     "S": "SBAS",
    "I": "NavIC (India)"
}

TOP_RECEIVERS = [
    "SEPT POLARX5", "LEICA GR50", "TRIMBLE ALLOY",
    "JAVAD TRE_3", "SEPT POLARX5TR", "SEPT POLARX5S",
    "TRIMBLE NETR9", "TRIMBLE NETR8", "JAVAD TRE_G3TH"
]


def ppp_assessment(v2, v3):
    """Return (overall_str, positives_list, issues_list)."""
    positives, issues = [], []
    score = 0

    # Constellations (merge V2 + V3)
    c2 = v2.get("constellations_v2", [])
    c3 = v3.get("constellations_v3", [])
    consts = list(dict.fromkeys(c2 + c3))  # deduplicate, preserve order

    if "G" in consts:
        positives.append("GPS tracking confirmed")
        score += 2
    else:
        issues.append("GPS not detected in status — check raw data")
    if "E" in consts:
        positives.append("Galileo: reduces convergence ~30–40%")
        score += 2
    else:
        issues.append(
            "No Galileo — convergence will be slower (GPS-only ~20–40 min)")
    if "C" in consts:
        positives.append(
            "BeiDou: excellent in Asia/Pacific — adds 10–15 satellites")
        score += 2
    if "R" in consts:
        positives.append("GLONASS: adds geometry diversity")
        score += 1

    # Completeness
    pct = v2.get("pct")
    if pct is not None:
        if pct >= 99:
            positives.append(
                f"{pct:.0f}% data completeness — full day available")
            score += 2
        elif pct >= 95:
            positives.append(f"{pct:.0f}% completeness — minor gaps, PPP ok")
            score += 1
        elif pct >= 85:
            issues.append(f"Only {pct:.0f}% completeness — some gaps in data")
        else:
            issues.append(
                f"Only {pct:.0f}% completeness — significant data loss")

    # Multipath
    mp1, mp2 = v2.get("mp1"), v2.get("mp2")
    if mp1 is not None:
        avg = (mp1 + (mp2 or mp1)) / 2
        if avg < 0.4:
            positives.append(
                f"Low multipath ({avg:.2f} m) — clean signal environment")
            score += 1
        elif avg < 0.6:
            positives.append(
                f"Moderate multipath ({avg:.2f} m) — acceptable for PPP")
        else:
            issues.append(
                f"High multipath ({avg:.2f} m) — check antenna surroundings")

    # Cycle slips
    slips = v2.get("no_slips")
    if slips is not None:
        if slips <= 10:
            positives.append(
                f"Low cycle slips ({slips:.0f}) — clean carrier phase")
            score += 1
        elif slips <= 50:
            issues.append(
                f"Moderate cycle slips ({slips:.0f}) — acceptable but monitor")
        else:
            issues.append(
                f"High cycle slips ({slips:.0f}) — phase data may be degraded")

    # V flag
    vf = v2.get("v_flag") or v3.get("v_flag")
    if vf in ("0", "1", "9"):
        positives.append(
            f"Data quality flag V={vf} ({V_FLAG_LABELS.get(vf, ('?', ''))[0]})")
        score += 2
    elif vf == "4":
        issues.append(
            f"Quality flag V=4 (low quality) — investigate before use")

    # Receiver
    recv = v3.get("recv_type") or v2.get("recv_type", "")
    if any(r in recv for r in TOP_RECEIVERS):
        positives.append(f"Geodetic-grade receiver: {recv}")
        score += 1

    if score >= 10:
        overall = "EXCELLENT — highly recommended for PPP research"
    elif score >= 7:
        overall = "GOOD — suitable for PPP, ready to use"
    elif score >= 4:
        overall = "FAIR — usable with awareness of limitations"
    else:
        overall = "POOR — investigate issues before using"

    return overall, positives, issues


# ==============================================================================
#  RELIABILITY SCORING (NEW)
# ==============================================================================

def calculate_reliability_score(v2: dict, v3: dict) -> int:
    """
    Calculate a 0-100 reliability score for PPP suitability.
    Factors: constellations, data quality, completeness, multipath, receiver type.
    """
    score = 0

    # Constellations (0-40 points)
    c2 = v2.get("constellations_v2", [])
    c3 = v3.get("constellations_v3", [])
    consts = list(dict.fromkeys(c2 + c3))

    if "G" in consts:
        score += 10
    if "R" in consts:
        score += 10
    if "E" in consts:
        score += 10
    if "C" in consts:
        score += 10

    # Data completeness (0-20 points)
    pct = v2.get("pct")
    if pct is not None:
        score += int(min(20, pct / 5))  # 100% = 20 pts

    # Quality flag (0-15 points)
    vf = v2.get("v_flag") or v3.get("v_flag")
    if vf == "0":
        score += 15
    elif vf == "1":
        score += 13
    elif vf == "9":
        score += 14  # Real-time is high quality
    elif vf in ("2", "3"):
        score += 8
    elif vf == "4":
        score += 2
    else:
        score += 5

    # Multipath (0-10 points)
    mp1 = v2.get("mp1")
    if mp1 is not None:
        mp_avg = (mp1 + (v2.get("mp2") or mp1)) / 2
        if mp_avg < 0.3:
            score += 10
        elif mp_avg < 0.5:
            score += 8
        elif mp_avg < 0.7:
            score += 5
        else:
            score += 2

    # Receiver quality (0-15 points)
    recv = v3.get("recv_type") or v2.get("recv_type", "")
    if any(r in recv for r in TOP_RECEIVERS):
        score += 15
    elif "SEPT" in recv or "LEICA" in recv or "TRIMBLE" in recv or "JAVAD" in recv:
        score += 12
    elif recv:
        score += 5

    return min(100, score)


def get_constellation_string(v2: dict, v3: dict) -> str:
    """Return readable constellation list."""
    c2 = v2.get("constellations_v2", [])
    c3 = v3.get("constellations_v3", [])
    consts = list(dict.fromkeys(c2 + c3))

    if not consts:
        return "—"
    return " ".join(consts)


def get_quality_label(vf) -> str:
    """Return quality label for V flag."""
    if vf in ("0", "1", "9"):
        return "✅"
    elif vf in ("2", "3"):
        return "⚠️"
    else:
        return "❌"


def print_station_list(v2_data: dict, v3_data: dict, args):
    """
    Print formatted table of all stations with constellation info and reliability.
    Supports filtering and sorting.
    """
    # Collect all stations
    all_sids = set(v2_data.keys()) | set(v3_data.keys())

    stations_list = []
    for sid in all_sids:
        v2 = v2_data.get(sid, {"v2_data": False})
        v3 = v3_data.get(sid, {"v3_data": False})

        # Skip if no data
        if not (v2.get("v2_data") or v3.get("v3_data")):
            continue

        c2 = v2.get("constellations_v2", [])
        c3 = v3.get("constellations_v3", [])
        consts = list(dict.fromkeys(c2 + c3))
        num_consts = len(consts)

        vf = v2.get("v_flag") or v3.get("v_flag", "?")
        recv = v3.get("recv_type") or v2.get("recv_type", "")

        reliability = calculate_reliability_score(v2, v3)

        stations_list.append({
            "code": sid,
            "consts": consts,
            "num_consts": num_consts,
            "const_str": get_constellation_string(v2, v3),
            "vf": vf,
            "quality_label": get_quality_label(vf),
            "recv": recv,
            "reliability": reliability,
            "v2_data": v2.get("v2_data", False),
            "v3_data": v3.get("v3_data", False),
        })

    # Apply filters
    if hasattr(args, 'min_const') and args.min_const:
        stations_list = [
            s for s in stations_list if s["num_consts"] >= args.min_const]

    if hasattr(args, 'quality') and args.quality:
        q_str = args.quality
        if "-" in q_str:
            q_min, q_max = map(int, q_str.split("-"))
            stations_list = [s for s in stations_list if int(
                s["vf"]) >= q_min and int(s["vf"]) <= q_max]
        else:
            q_val = int(q_str)
            stations_list = [s for s in stations_list if int(s["vf"]) == q_val]

    if hasattr(args, 'multi_only') and args.multi_only:
        stations_list = [s for s in stations_list if s["num_consts"] > 1]

    if hasattr(args, 'gps_only') and args.gps_only:
        stations_list = [
            s for s in stations_list if s["num_consts"] == 1 and "G" in s["consts"]]

    # Sort
    sort_by = getattr(args, 'sort_by', 'code')
    if sort_by == "reliability":
        stations_list.sort(key=lambda s: (-s["reliability"], s["code"]))
    elif sort_by == "constellation":
        stations_list.sort(
            key=lambda s: (-s["num_consts"], -s["reliability"], s["code"]))
    elif sort_by == "quality":
        stations_list.sort(key=lambda s: (
            s["vf"], -s["reliability"], s["code"]))
    else:  # "code"
        stations_list.sort(key=lambda s: s["code"])

    # Print header
    print("\n" + "=" * 120)
    print("📊 STATION CONSTELLATION COMPLETENESS & RELIABILITY REPORT")
    print("=" * 120)
    print()
    print(f"{'Code':<6} {'V':<2} {'Constellations':<25} {'Cnt':<3} {'Reliability':<12} {'Receiver':<30}")
    print("-" * 120)

    # Print rows
    for s in stations_list:
        rel_bar = f"{'█' * (s['reliability'] // 10)}" + \
            f"{'░' * (10 - s['reliability'] // 10)}"
        rel_pct = f"{s['reliability']:>3}%"

        print(f"{s['code']:<6} {s['quality_label']} {s['const_str']:<25} "
              f"{s['num_consts']:<3} {rel_bar} {rel_pct:<6} {s['recv'][:28]:<30}")

    print()
    print("-" * 120)
    print(f"Total: {len(stations_list)} stations")
    print()
    print("🔍 Legend:")
    print("  ✅ = V-flag 0/1/9 (Excellent/Good/Real-time)  |  ⚠️ = V-flag 2/3 (Partial/Mixed)")
    print("  ❌ = V-flag 4 (Low quality)  |  Cnt = # constellations")
    print("  Reliability bar: Based on constellations, data quality, multipath, receiver type")
    print()
    print("📝 Usage examples:")
    print("  --min-const 4         : Only stations with 4+ constellations")
    print("  --quality 0-1         : Only V-flag 0 or 1 (best quality)")
    print("  --sort-by reliability : Sort by reliability score (highest first)")
    print("  --multi-only          : Skip GPS-only stations")
    print("  --gps-only            : Only GPS-only stations")
    print()
    print(f"💾 To check a specific station in detail:")
    print(f"  python check_station.py BJFS")
    print(f"  python check_station.py GOLD ABMF")
    print()
    print("=" * 120 + "\n")


def generate_report(sid: str, v2: dict, v3: dict, date_str: str) -> str:
    lines = []

    full_id = v3.get("full_id") or f"{sid}00???"
    v2_has = v2.get("v2_data", False)
    v3_has = v3.get("v3_data", False)

    # Merge constellations
    c2 = v2.get("constellations_v2", [])
    c3 = v3.get("constellations_v3", [])
    all_consts = list(dict.fromkeys(c2 + c3))

    lines += [
        f"# IGS / MGEX Station Report: **{sid}**",
        f"",
        f"Generated: {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}  ",
        f"Status files date: **{date_str}**  (GPS Week 2401, Day 5)",
        "",
        "---",
        ""
    ]

    # 1. Availability
    lines += [
        "## 1. Data Availability",
        "",
        "| Status file | Result |",
        "|-------------|--------|",
        f"| `26015_status.txt` (RINEX v2) | {'✅ Data found' if v2_has else '❌ Station listed — no data submitted'} |",
        f"| `26015_V3status.txt` (MGEX v3) | {'✅ Data found' if v3_has else '❌ Station listed — no data submitted'} |",
        "",
    ]

    if not v2_has and not v3_has:
        lines += [
            "> ⛔ **Station submitted NO data on January 15, 2026.**",
            "> Do not attempt to download. Select an alternative station.",
            ""
        ]
        return "\n".join(lines)

    # 2. Identity
    recv = v3.get("recv_type") or v2.get("recv_type", "Unknown")
    ant = v3.get("ant_type") or v2.get("ant_type", "Unknown")
    mkr = v3.get("mkr_name") or v2.get("mkr_name", "Unknown")
    dom = v3.get("mkr_num") or v2.get("mkr_num", "Unknown")
    typ = v3.get("typ") or v2.get("typ", "?")

    lines += [
        "## 2. Station Identity",
        "",
        "| Field | Value |",
        "|-------|-------|",
        f"| 4-char ID | `{sid}` |",
        f"| Full RINEX3 ID | `{full_id}` |",
        f"| Marker name | {mkr} |",
        f"| DOMES number | {dom} |",
        f"| Type | `{typ}` — M = Multi-constellation, G = GPS-only |",
        f"| Receiver | `{recv}` |",
        f"| Antenna | `{ant}` |",
        "",
    ]

    is_top = any(r in recv for r in TOP_RECEIVERS)
    lines += [
        f"> **Receiver:** {'✅ Top-tier geodetic receiver — ideal for PPP' if is_top else '⚠️ Check manufacturer specs for geodetic suitability'}",
        f"> **Antenna:** Verify `{ant}` exists in `igs20.atx`. Missing entry → systematic 1–3 cm height error.",
        "",
    ]

    # 3. Data quality (V2 metrics)
    lines += ["## 3. Data Quality Metrics (RINEX v2 QC)", ""]
    if v2_has:
        pct = v2.get("pct")
        mp1 = v2.get("mp1")
        mp2 = v2.get("mp2")
        slips = v2.get("no_slips")
        vf = v2.get("v_flag", "?")
        no_exp = v2.get("no_exp")
        no_obs = v2.get("no_obs")
        pts_del = v2.get("pts_del")
        dly_h = v2.get("dly_h")
        dly_m = v2.get("dly_m")

        vf_label, vf_desc = V_FLAG_LABELS.get(str(vf), ("?", "Unknown flag"))
        avg_mp = ((mp1 or 0) + (mp2 or mp1 or 0)) / 2 if mp1 else None

        lines += [
            "| Metric | Value | Grade | What it means for PPP |",
            "|--------|-------|-------|------------------------|",
            f"| Delivery delay | {dly_h}h {dly_m}m | {'✅ On-time' if dly_h == 0 else '⚠️ Late'} | Late data misses rapid products window |",
            f"| Observations | {no_obs:,} / {no_exp:,} | {pct:.0f}% | {'✅ Full day' if pct and pct >= 99 else '⚠️ Gaps present'} |",
            f"| Points deleted | {pts_del:,} | — | Removed by QC (multipath / noise) |",
            f"| L1 Multipath (MP1) | {mp1} m | {'✅ Good' if mp1 and mp1 < 0.5 else '⚠️ Elevated'} | Signal bouncing off surroundings |",
            f"| L2 Multipath (MP2) | {mp2} m | {'✅ Good' if mp2 and mp2 < 0.5 else '⚠️ Elevated'} | L2 frequency environment |",
            f"| Cycle slips | {slips:.0f} | {'✅ Clean' if slips and slips <= 10 else '⚠️ Check'} | Phase breaks — too many = noisy PPP |",
            f"| Quality flag | V={vf} ({vf_label}) | {'✅' if vf in ('0', '1', '9') else '⚠️'} | {vf_desc} |",
            "",
        ]
    else:
        lines += ["_No RINEX v2 metrics available for this station._\n"]

    # 4. Constellation analysis
    lines += [
        "## 4. Constellation / Signal Coverage",
        "",
        "> **Why this matters:** More constellations = more satellites = better geometry = faster PPP convergence.",
        "> GPS-only: ~8–12 sats. GPS+Galileo+BeiDou: ~30–40 sats visible simultaneously.",
        "",
        "| System | Code | Available | PPP Contribution |",
        "|--------|------|-----------|-----------------|",
    ]
    ppp_impact = {
        "G": "Essential — core of all PPP processing",
        "R": "Adds geometry; needs GLONASS-specific products",
        "E": "Reduces convergence 30–40%; excellent clock stability",
        "C": "Adds 10–15 satellites in Asia; key for multi-GNSS studies",
        "J": "Supplements GPS in Japan / Asia-Pacific region",
        "S": "SBAS — not used in PPP (navigation augmentation only)",
        "I": "NavIC — regional (India); rarely in PPP products yet",
    }
    for code, name in CONSTELLATION_NAMES.items():
        avail = "✅ YES" if code in all_consts else "— no"
        lines.append(f"| {name} | `{code}` | {avail} | {ppp_impact[code]} |")
    lines.append("")

    # Why file might be small (BJFS explanation)
    if "E" not in all_consts and "C" not in all_consts:
        lines += [
            "> ⚠️  **Why is the file small?**",
            "> This station tracks only GPS" +
            (" + GLONASS" if "R" in all_consts else "") + ".",
            "> A full multi-GNSS station (G+R+E+C) has ~30–40 satellites → ~40 MB/day uncompressed.",
            "> A GPS+GLONASS station has ~15–20 satellites → **~12–18 MB/day** — roughly half the size.",
            "> For larger multi-GNSS files, choose a station with Galileo (E) and BeiDou (C) coverage.",
            "",
        ]

    # 5. File names
    lines += [
        "## 5. File Names and Download URLs",
        "",
        "### RINEX v3 observation file",
        "```",
        f"{full_id}_R_20260150000_01D_30S_MO.rnx.gz",
        "```",
        f"URL: `https://cddis.nasa.gov/archive/gnss/data/daily/2026/015/26d/{full_id}_R_20260150000_01D_30S_MO.rnx.gz`",
        "",
        "### RINEX v2 observation file (alternative / fallback)",
        "```",
        f"{sid.lower()}0150.26o.gz",
        "```",
        f"URL: `https://cddis.nasa.gov/archive/gnss/data/daily/2026/015/26o/{sid.lower()}0150.26o.gz`",
        "",
    ]

    # MD5
    md5 = v3.get("md5") or v2.get("md5", "")
    if md5:
        lines += [
            "### MD5 Checksum — verify after download",
            "```bash",
            f"md5sum {full_id}_R_20260150000_01D_30S_MO.rnx.gz",
            f"# Expected: {md5}",
            "```",
            "",
        ]

    # 6. Suitability
    overall, positives, issues = ppp_assessment(v2, v3)
    lines += [
        "## 6. PPP Suitability Assessment",
        "",
        f"### → {overall}",
        "",
    ]
    if positives:
        lines.append("**Strengths:**")
        for p in positives:
            lines.append(f"- ✅ {p}")
    if issues:
        lines += ["", "**Issues / Cautions:**"]
        for iss in issues:
            lines.append(f"- ⚠️  {iss}")
    lines.append("")

    # 7. Files per tool
    lines += [
        "## 7. Files Required Per Tool",
        "",
        "| Tool | Mode | Required Files | Expected Accuracy |",
        "|------|------|----------------|-------------------|",
        f"| **RTKLib** | Broadcast PPP | `.rnx obs` + `.rnx nav` | ~1–3 m |",
        f"| **RTKLib** | Precise PPP | obs + nav + `.SP3` + `.CLK` + `igs20.atx` | ~5–10 cm |",
        f"| **DEMO5** | PPP-AR | Same as RTKLib precise + `.BIA` (OSB) | ~1–3 cm |",
        f"| **GAMP** | Multi-GNSS PPP | obs + nav + `.SP3` + `.CLK` + `.ERP` + `.BSX/.DCB` + `igs20.atx` + `.blq` | ~2–5 cm |",
        f"| **PRIDE PPP-AR** | PPP-AR | obs only (pdp3 auto-downloads rest) | ~1–3 cm |",
        "",
        "> **DEMO5 location:** See Part 10 of the PPP Complete Guide for running both RTKLib",
        "> and DEMO5 from the same `Program Files` folder.",
        "",
    ]

    # 8. Quick commands
    lines += [
        "## 8. Quick-Start Processing Commands",
        "",
        "### A) RTKLib — broadcast only (simplest, lowest accuracy)",
        "```",
        "RTKPOST settings:",
        f"  Rover:      {full_id}_R_20260150000_01D_30S_MO.rnx",
        "  Nav:        BRDM00DLR_R_20260150000_01D_MN.rnx",
        "  Mode:       PPP-Static",
        "  Ephemeris:  Broadcast",
        "  Expected:   ~1–3 m accuracy",
        "```",
        "",
        "### B) RTKLib / DEMO5 — precise PPP",
        "```",
        "RTKPOST settings:",
        f"  Rover:      {full_id}_R_20260150000_01D_30S_MO.rnx",
        "  Nav:        BRDM00DLR_R_20260150000_01D_MN.rnx",
        "  SP3:        IGS0OPSFIN_20260150000_01D_15M_ORB.SP3",
        "  CLK:        IGS0OPSFIN_20260150000_01D_30S_CLK.CLK",
        "  ATX:        igs20.atx",
        "  Mode:       PPP-Static | Ephemeris: Precise",
        "  Expected:   ~2–5 cm after 20–40 min convergence",
        "```",
        "",
        "### C) GAMP — full multi-GNSS PPP",
        "```ini",
        "# gamp.cfg key settings:",
        "posmode   = 7          # PPP-Static",
        "navsys    = 45         # GPS+GLO+GAL+BDS (use 1 for GPS-only)",
        "ionoopt   = 4          # UC12 uncombined",
        "tropopt   = 3          # estimate ZTD",
        f"# obs: {full_id}_R_20260150000_01D_30S_MO.rnx",
        "# sp3: WUM0MGXFIN_20260150000_01D_15M_ORB.SP3",
        "# clk: WUM0MGXFIN_20260150000_01D_30S_CLK.CLK",
        "# erp: IGS0OPSFIN_20260150000_01D_01D_ERP.ERP",
        "# dcb: CAS0MGXRAP_20260150000_01D_01D_OSB.BIA",
        "```",
        "",
        "### D) PRIDE PPP-AR — highest accuracy",
        "```bash",
        f"# Copy your obs file to working directory, then:",
        f"pdp3 -m S -sys gec {full_id}_R_20260150000_01D_30S_MO.rnx",
        "# pdp3 auto-downloads SP3, CLK, BIA, ERP from Wuhan server",
        "# Expected: ~1–3 cm, ambiguity fixed within 5–15 min",
        "```",
        "",
        "---",
        f"_Report for station {sid} — generated by check_station.py_",
    ]

    return "\n".join(lines)


# ==============================================================================
#  MAIN
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="IGS Station Status Checker")
    parser.add_argument("stations", nargs="*", default=[],
                        help="4-char station IDs e.g. BJFS GOLD")
    parser.add_argument("--list", "-l", action="store_true",
                        help="List all stations with constellation completeness & reliability")
    parser.add_argument("--min-const", type=int, default=None,
                        help="Filter: minimum number of constellations (1-7)")
    parser.add_argument("--quality", type=str, default=None,
                        help="Filter: quality flag range, e.g. '0-1' or '9'")
    parser.add_argument("--multi-only", action="store_true",
                        help="Filter: multi-GNSS only (skip GPS-only stations)")
    parser.add_argument("--gps-only", action="store_true",
                        help="Filter: GPS-only stations")
    parser.add_argument("--sort-by", type=str, default="code",
                        choices=["code", "constellation",
                                 "quality", "reliability"],
                        help="Sort by: code, constellation count, quality, or reliability")
    parser.add_argument("--v2",     default=None,
                        help="Path to 26015_status.txt")
    parser.add_argument("--v3",     default=None,
                        help="Path to 26015_V3status.txt")
    parser.add_argument("--outdir", default=str(Path(__file__).resolve().parent.parent / "station_reports"),
                        help="Output folder for .md reports")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    root_dir = script_dir.parent   # C:\PPP_PROJECT

    # Status files live in Old_data/products/status/ relative to project root
    status_dir = root_dir / "Old_data" / "products" / "status"

    def find_file_extended(given, *names):
        if given and Path(given).exists():
            return Path(given)
        search_dirs = [script_dir, status_dir]
        for name in names:
            for d in search_dirs:
                p = d / name
                if p.exists():
                    return p
        return None

    v2_path = find_file_extended(args.v2,
                                 "26015_status.txt", "26015.status.txt", "26015.status")
    v3_path = find_file_extended(args.v3,
                                 "26015_V3status.txt", "26015.V3status.txt", "26015.V3status")

    v2_data, v3_data = {}, {}
    if v2_path:
        print(f"✓ V2 status: {v2_path}")
        v2_data = parse_v2_status(v2_path)
    else:
        print("⚠️  V2 status file not found — place 26015_status.txt next to this script")

    if v3_path:
        print(f"✓ V3 status: {v3_path}")
        v3_data = parse_v3_status(v3_path)
    else:
        print("⚠️  V3 status file not found — place 26015_V3status.txt next to this script")

    print()

    # Handle --list mode
    if args.list:
        print_station_list(v2_data, v3_data, args)
        return

    # Handle individual station reports
    if not args.stations:
        parser.print_help()
        print("\n💡 TIP: Use --list to see all available stations with ratings:")
        print("    python check_station.py --list")
        print("    python check_station.py --list --min-const 4")
        print("    python check_station.py --list --sort-by reliability")
        return

    out_dir = Path(args.outdir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for station in args.stations:
        sid = station.upper()
        v2 = v2_data.get(sid, {"id": sid, "v2_data": False})
        v3 = v3_data.get(sid, {"id": sid, "v3_data": False,
                         "full_id": "", "constellations_v3": []})

        print(f"── {sid} ─────────────────────────────────────────")
        if v2.get("v2_data"):
            print(
                f"   V2 ✅  pct={v2.get('pct')}%  MP1={v2.get('mp1')}m  MP2={v2.get('mp2')}m  slips={v2.get('no_slips')}  V={v2.get('v_flag')}")
            print(
                f"         receiver={v2.get('recv_type')}  antenna={v2.get('ant_type')}")
            print(f"         constellations(V2)={v2.get('constellations_v2')}")
        else:
            print(f"   V2 ❌  No data")
        if v3.get("v3_data"):
            print(
                f"   V3 ✅  full_id={v3.get('full_id')}  consts={v3.get('constellations_v3')}")
            print(
                f"         receiver={v3.get('recv_type')}  V={v3.get('v_flag')}")
        else:
            print(f"   V3 ❌  No data")

        reliability = calculate_reliability_score(v2, v3)
        print(
            f"   ⭐ Reliability: {reliability}% {'█' * (reliability // 10)}{'░' * (10 - reliability // 10)}")

        report_text = generate_report(sid, v2, v3, "2026-01-15 (DOY 015)")
        out_file = out_dir / f"station_report_{sid}.md"
        out_file.write_text(report_text, encoding="utf-8")
        print(f"   ✓ Saved → {out_file}")
        print()

    print("All done. Share the .md files with your team.")


if __name__ == "__main__":
    main()
