from pathlib import Path
from datetime import datetime, timedelta
import math

ROOT = Path(r"c:/PPP_PROJECT/RTKLIB_work/results/EXP1")
REFS = {
    "KIRU": (67.857900, 20.967800, 390.900),
    "WUH": (30.531700, 114.357000, 73.400),
}


def llh_to_ecef(lat_deg, lon_deg, h):
    a = 6378137.0
    f = 1 / 298.257223563
    e2 = f * (2 - f)
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    s = math.sin(lat)
    c = math.cos(lat)
    N = a / math.sqrt(1 - e2 * s * s)
    x = (N + h) * c * math.cos(lon)
    y = (N + h) * c * math.sin(lon)
    z = (N * (1 - e2) + h) * s
    return x, y, z


def ecef_to_enu(dx, dy, dz, lat_deg, lon_deg):
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    slat = math.sin(lat)
    clat = math.cos(lat)
    slon = math.sin(lon)
    clon = math.cos(lon)
    e = -slon * dx + clon * dy
    n = -slat * clon * dx - slat * slon * dy + clat * dz
    u = clat * clon * dx + clat * slon * dy + slat * dz
    return e, n, u


def parse_pos(path):
    rows = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if not line.strip() or line.startswith("%"):
                continue
            p = line.split()
            if len(p) < 7:
                continue
            try:
                t = datetime.strptime(
                    p[0] + " " + p[1], "%Y/%m/%d %H:%M:%S.%f")
                lat = float(p[2])
                lon = float(p[3])
                h = float(p[4])
                q = int(float(p[5]))
                ns = int(float(p[6]))
                rows.append((t, lat, lon, h, q, ns))
            except Exception:
                pass
    rows.sort(key=lambda r: r[0])
    return rows


def metrics(path, ref):
    rows = parse_pos(path)
    if not rows:
        return None

    lat0, lon0, h0 = ref
    x0, y0, z0 = llh_to_ecef(lat0, lon0, h0)

    enu = []
    for t, lat, lon, h, q, ns in rows:
        x, y, z = llh_to_ecef(lat, lon, h)
        e, n, u = ecef_to_enu(x - x0, y - y0, z - z0, lat0, lon0)
        enu.append((t, e, n, u, q, ns))

    t_end = enu[-1][0]
    win_start = t_end - timedelta(hours=2)
    use = [r for r in enu if r[0] >= win_start]
    if not use:
        use = enu

    def rms(vals):
        return math.sqrt(sum(v * v for v in vals) / len(vals)) if vals else float("nan")

    e_last, n_last, u_last = enu[-1][1], enu[-1][2], enu[-1][3]
    rms_h = rms([math.hypot(r[1], r[2]) for r in use])
    rms_u = rms([r[3] for r in use])

    conv = None
    for i in range(len(enu)):
        t0 = enu[i][0]
        t1 = t0 + timedelta(minutes=10)
        window = [r for r in enu if t0 <= r[0] <= t1]
        if not window or window[-1][0] < t1:
            continue
        if all((math.hypot(r[1], r[2]) < 0.1 and abs(r[3]) < 0.2) for r in window):
            conv = (t0 - enu[0][0]).total_seconds() / 60.0
            break

    q_counts = {}
    for *_, q in enu:
        q_counts[q] = q_counts.get(q, 0) + 1

    avg_nsat = sum(r[5] for r in rows) / len(rows)

    return {
        "start": enu[0][0],
        "end": enu[-1][0],
        "epochs": len(enu),
        "q_counts": q_counts,
        "avg_nsat": avg_nsat,
        "final_e": e_last,
        "final_n": n_last,
        "final_u": u_last,
        "rms_h_2h": rms_h,
        "rms_u_2h": rms_u,
        "conv_min": conv,
    }


def is_solution_file(p):
    if not p.is_file():
        return False
    nm = p.name.lower()
    if nm.endswith((".conf", ".stat", ".jpg", ".jpeg", ".png")):
        return False
    if "_events" in nm:
        return False

    try:
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            head = "".join([next(f) for _ in range(5)])
        return ("RTKPOST-EX" in head) or ("%  GPST" in head)
    except Exception:
        return False


def station_for_name(name):
    u = name.upper()
    if u.startswith("KIRU"):
        return "KIRU"
    if u.startswith("WUH"):
        return "WUH"
    return None


def main():
    files = [p for p in sorted(ROOT.iterdir()) if is_solution_file(p)]

    print("Found solution files:")
    for p in files:
        print("-", p.name)

    print("\nMETRICS:")
    for p in files:
        st = station_for_name(p.name)
        if not st:
            continue
        m = metrics(p, REFS[st])
        if not m:
            continue
        conv = "never" if m["conv_min"] is None else f"{m['conv_min']:.1f}"
        print(f"\n{p.name}")
        print(
            f"epochs={m['epochs']} span={m['start']} -> {m['end']} Q={m['q_counts']}")
        print(f"avg nsat={m['avg_nsat']:.2f}")
        print(
            f"final ENU(m): E={m['final_e']:.3f} N={m['final_n']:.3f} U={m['final_u']:.3f}"
        )
        print(f"RMS(last2h): H={m['rms_h_2h']:.3f} U={m['rms_u_2h']:.3f}")
        print(f"conv(10cmH+20cmU for 10min): {conv} min")


if __name__ == "__main__":
    main()
