"""
Tevin — SNDP PPP Results Plotting Script
Generates ENU error plots for EXP1–5 across HKWS, KIRU, WUH2, ZIM2.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import AutoMinorLocator

ROOT   = os.path.dirname(os.path.abspath(__file__))
STATIONS = ['HKWS', 'KIRU', 'WUH2', 'ZIM2']
R_EARTH  = 6378137.0

# ── colour palette ──────────────────────────────────────────────────────────
C = {
    'broadcast': '#d62728',
    'precise':   '#1f77b4',
    'GPS':       '#1f77b4',
    'GE':        '#2ca02c',
    'GEC':       '#ff7f0e',
    'GRCEQ':     '#9467bd',
    'float':     '#1f77b4',
    'PPPAR':     '#d62728',
    'L1_Klob':   '#d62728',
    'L1_IONEX':  '#ff7f0e',
    'L1L2_IF':   '#1f77b4',
    '1h':  '#d62728',
    '2h':  '#ff7f0e',
    '4h':  '#2ca02c',
    '8h':  '#1f77b4',
    '24h': '#9467bd',
}

# ── helpers ──────────────────────────────────────────────────────────────────
def parse_pos(filepath):
    rows = []
    with open(filepath, 'r', errors='replace') as f:
        for line in f:
            if line.startswith('%') or not line.strip():
                continue
            p = line.split()
            if len(p) < 7:
                continue
            try:
                rows.append(dict(
                    time=pd.to_datetime(p[0] + ' ' + p[1], format='%Y/%m/%d %H:%M:%S.%f'),
                    lat=float(p[2]), lon=float(p[3]), h=float(p[4]),
                    Q=int(p[5]),   ns=int(p[6]),
                    sdn=float(p[7]) if len(p) > 7 else np.nan,
                    sde=float(p[8]) if len(p) > 8 else np.nan,
                    sdu=float(p[9]) if len(p) > 9 else np.nan,
                ))
            except Exception:
                pass
    return pd.DataFrame(rows)


def pos_file(station, label):
    return os.path.join(ROOT, station, f'{station}_{label}.pos')


def enu(df, ref_lat, ref_lon, ref_h):
    df = df.copy()
    df['dN'] = (df['lat'] - ref_lat) * (np.pi / 180) * R_EARTH
    df['dE'] = (df['lon'] - ref_lon) * (np.pi / 180) * R_EARTH * np.cos(ref_lat * np.pi / 180)
    df['dU'] = df['h'] - ref_h
    return df


def hours(df):
    """Return fractional hours from start of day."""
    t0 = df['time'].iloc[0].normalize()
    return (df['time'] - t0).dt.total_seconds() / 3600.0


def get_ref(station):
    """Reference position = mean of last 120 epochs of 24 h GEC solution."""
    df = parse_pos(pos_file(station, 'EXP5E_24h'))
    tail = df.tail(120)
    return tail['lat'].mean(), tail['lon'].mean(), tail['h'].mean()


def save(fig, station, name):
    out = os.path.join(ROOT, station, f'{station}_{name}.png')
    fig.savefig(out, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  saved: {os.path.relpath(out, ROOT)}')


def save_summary(fig, name):
    out = os.path.join(ROOT, f'summary_{name}.png')
    fig.savefig(out, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  saved: summary_{name}.png')


def enu_axes(ax, df, ref, color, label, lw=0.9, alpha=1.0, component='N'):
    lat, lon, h = ref
    df = enu(df, lat, lon, h)
    t = hours(df)
    col_map = {'E': 'dE', 'N': 'dN', 'U': 'dU'}
    ax.plot(t, df[col_map[component]], color=color, lw=lw, alpha=alpha, label=label)


def style_ax(ax, ylabel, ylim=None, xlim=(0, 24)):
    ax.axhline(0, color='k', lw=0.5, ls='--', alpha=0.4)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.set_xlim(xlim)
    if ylim:
        ax.set_ylim(ylim)
    ax.xaxis.set_minor_locator(AutoMinorLocator(4))
    ax.yaxis.set_minor_locator(AutoMinorLocator(4))
    ax.grid(True, which='major', ls='--', alpha=0.3)
    ax.grid(True, which='minor', ls=':', alpha=0.15)


# ── reference coordinates ────────────────────────────────────────────────────
print('Computing reference coordinates...')
REFS = {st: get_ref(st) for st in STATIONS}
for st, (lat, lon, h) in REFS.items():
    print(f'  {st}: {lat:.7f}°N  {lon:.7f}°E  {h:.4f}m')


# ═══════════════════════════════════════════════════════════════════════════
# EXP1 — Broadcast vs Precise (GPS only)
# ═══════════════════════════════════════════════════════════════════════════
print('\nEXP1 — Broadcast vs Precise...')
for st in STATIONS:
    ref = REFS[st]
    exps = [
        ('EXP1A_broadcast', 'Broadcast (Klobuchar)', C['broadcast']),
        ('EXP1B_precise',   'Precise (IF-LC)',       C['precise']),
    ]
    fig, axes = plt.subplots(3, 2, figsize=(13, 8), sharex='col')
    fig.suptitle(f'{st} — EXP1: Broadcast vs Precise Ephemeris (GPS only)', fontweight='bold')

    for col, (label, name, color) in enumerate(exps):
        df = parse_pos(pos_file(st, label))
        df_e = enu(df, *ref)
        t = hours(df_e)

        # auto ylim: clip to ±20 m for broadcast, ±2 m for precise
        ylim_h = (-20, 20) if 'broadcast' in label else (-2, 2)
        ylim_v = (-40, 40) if 'broadcast' in label else (-4, 4)

        for row, (comp, yl, ylabel) in enumerate(
            [('dE', ylim_h, 'East error (m)'),
             ('dN', ylim_h, 'North error (m)'),
             ('dU', ylim_v, 'Up error (m)')]):
            ax = axes[row, col]
            ax.plot(t, df_e[comp], color=color, lw=0.8)
            style_ax(ax, ylabel, ylim=yl)
            if row == 0:
                ax.set_title(name, fontsize=10, color=color)
            if row == 2:
                ax.set_xlabel('Time (hours, GPST)', fontsize=9)

    fig.tight_layout()
    save(fig, st, 'EXP1_brdc_vs_precise')


# ═══════════════════════════════════════════════════════════════════════════
# EXP2 — Multi-Constellation
# ═══════════════════════════════════════════════════════════════════════════
print('\nEXP2 — Multi-constellation...')
EXP2_RUNS = [
    ('EXP2A_GPS',   'GPS only',          C['GPS']),
    ('EXP2B_GE',    'GPS+GAL',           C['GE']),
    ('EXP2C_GEC',   'GPS+GAL+BDS',       C['GEC']),
    ('EXP2D_GRCEQ', 'GPS+GLO+GAL+BDS+QZSS', C['GRCEQ']),
]
for st in STATIONS:
    ref = REFS[st]
    fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
    fig.suptitle(f'{st} — EXP2: Multi-Constellation Comparison (Precise, IF-LC)', fontweight='bold')

    for label, name, color in EXP2_RUNS:
        df = parse_pos(pos_file(st, label))
        df_e = enu(df, *ref)
        t = hours(df_e)
        for row, (comp, ylabel) in enumerate(
            [('dE', 'East (m)'), ('dN', 'North (m)'), ('dU', 'Up (m)')]):
            axes[row].plot(t, df_e[comp], color=color, lw=0.9, label=name, alpha=0.85)

    for row, ylabel in enumerate(['East (m)', 'North (m)', 'Up (m)']):
        style_ax(axes[row], ylabel, ylim=(-1.5, 1.5) if row < 2 else (-3, 3))
    axes[0].legend(loc='upper right', fontsize=8, ncol=2)
    axes[2].set_xlabel('Time (hours, GPST)', fontsize=9)

    # Mark ±10 cm / ±20 cm convergence bands
    for row, thr in enumerate([0.1, 0.1, 0.2]):
        axes[row].axhspan(-thr, thr, color='green', alpha=0.07, zorder=0)

    fig.tight_layout()
    save(fig, st, 'EXP2_constellation')


# ═══════════════════════════════════════════════════════════════════════════
# EXP3 — Float vs PPP-AR
# ═══════════════════════════════════════════════════════════════════════════
print('\nEXP3 — Float vs PPP-AR...')
EXP3_RUNS = [
    ('EXP3A_float', 'Float PPP',  C['float']),
    ('EXP3B_PPPAR', 'PPP-AR (attempted)', C['PPPAR']),
]
for st in STATIONS:
    ref = REFS[st]
    fig, axes = plt.subplots(3, 1, figsize=(12, 7), sharex=True)
    fig.suptitle(f'{st} — EXP3: Float PPP vs PPP-AR  (GPS+GAL+BDS, Precise)', fontweight='bold')

    for label, name, color in EXP3_RUNS:
        df = parse_pos(pos_file(st, label))
        df_e = enu(df, *ref)
        t = hours(df_e)
        for row, comp in enumerate(['dE', 'dN', 'dU']):
            lw = 1.5 if 'PPPAR' in label else 0.9
            axes[row].plot(t, df_e[comp], color=color, lw=lw, label=name, alpha=0.9,
                          ls='--' if 'PPPAR' in label else '-')

    for row, ylabel in enumerate(['East (m)', 'North (m)', 'Up (m)']):
        style_ax(axes[row], ylabel, ylim=(-1.5, 1.5) if row < 2 else (-3, 3))
        axes[row].axhspan(-0.1, 0.1, color='green', alpha=0.07, zorder=0) if row < 2 else \
        axes[row].axhspan(-0.2, 0.2, color='green', alpha=0.07, zorder=0)
    axes[0].legend(loc='upper right', fontsize=9)
    axes[2].set_xlabel('Time (hours, GPST)', fontsize=9)
    fig.text(0.5, 0.01,
             'Note: PPP-AR result is identical to Float — RTKLIB-EX requires FCB biases; IGS provides OSB.',
             ha='center', fontsize=8, style='italic', color='gray')

    fig.tight_layout(rect=[0, 0.03, 1, 1])
    save(fig, st, 'EXP3_float_vs_AR')


# ═══════════════════════════════════════════════════════════════════════════
# EXP4 — Ionosphere Correction Methods
# ═══════════════════════════════════════════════════════════════════════════
print('\nEXP4 — Ionosphere methods...')
EXP4_RUNS = [
    ('EXP4A_L1_Klobuchar', 'L1+Klobuchar (brdc)',   C['L1_Klob']),
    ('EXP4C_L1_IONEX',     'L1+IONEX TEC (brdc)',   C['L1_IONEX']),
    ('EXP4B_L1L2_IF',      'L1+L2 IF-LC (precise)', C['L1L2_IF']),
]
for st in STATIONS:
    ref = REFS[st]
    fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
    fig.suptitle(f'{st} — EXP4: Ionosphere Correction Comparison (GPS only)', fontweight='bold')

    for label, name, color in EXP4_RUNS:
        df = parse_pos(pos_file(st, label))
        df_e = enu(df, *ref)
        t = hours(df_e)
        lw = 1.4 if 'IF' in label else 0.9
        for row, comp in enumerate(['dE', 'dN', 'dU']):
            axes[row].plot(t, df_e[comp], color=color, lw=lw, label=name, alpha=0.85)

    # use wide ylim to capture broadcast errors
    for row, (ylabel, yl) in enumerate(
        [('East (m)', (-10, 10)), ('North (m)', (-10, 10)), ('Up (m)', (-20, 20))]):
        style_ax(axes[row], ylabel, ylim=yl)
    axes[0].legend(loc='upper right', fontsize=9)
    axes[2].set_xlabel('Time (hours, GPST)', fontsize=9)

    fig.tight_layout()
    save(fig, st, 'EXP4_iono')


# ═══════════════════════════════════════════════════════════════════════════
# EXP5 — Session Length vs Convergence
# ═══════════════════════════════════════════════════════════════════════════
print('\nEXP5 — Session lengths...')
EXP5_RUNS = [
    ('EXP5A_1h',  '1 h',  C['1h'],  1.0),
    ('EXP5B_2h',  '2 h',  C['2h'],  2.0),
    ('EXP5C_4h',  '4 h',  C['4h'],  4.0),
    ('EXP5D_8h',  '8 h',  C['8h'],  8.0),
    ('EXP5E_24h', '24 h', C['24h'], 24.0),
]

conv_times = {st: {} for st in STATIONS}  # for summary chart

for st in STATIONS:
    ref = REFS[st]
    fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=False)
    fig.suptitle(f'{st} — EXP5: Convergence vs Session Length  (GPS+GAL+BDS, Precise)',
                 fontweight='bold')

    for label, name, color, dur in EXP5_RUNS:
        df = parse_pos(pos_file(st, label))
        df_e = enu(df, *ref)
        t = hours(df_e)
        for row, comp in enumerate(['dE', 'dN', 'dU']):
            axes[row].plot(t, df_e[comp], color=color, lw=1.0, label=name, alpha=0.85)

        # compute convergence time (3D ≤ threshold for 10 consecutive epochs)
        mask = (df_e['dE'].abs() < 0.10) & (df_e['dN'].abs() < 0.10) & (df_e['dU'].abs() < 0.20)
        conv_t = np.nan
        for i in range(len(mask) - 20):
            if mask.iloc[i:i+20].all():
                conv_t = t.iloc[i]
                break
        conv_times[st][name] = conv_t

    thresholds = [(0, (-1.0, 1.0)), (1, (-1.0, 1.0)), (2, (-2.0, 2.0))]
    ylabels = ['East (m)', 'North (m)', 'Up (m)']
    thr_vals = [0.1, 0.1, 0.2]
    for row, (ylabel, thr) in enumerate(zip(ylabels, thr_vals)):
        style_ax(axes[row], ylabel,
                 ylim=(-1.0, 1.0) if row < 2 else (-2.0, 2.0))
        axes[row].axhspan(-thr, thr, color='green', alpha=0.07, zorder=0)
    axes[0].legend(loc='upper right', fontsize=9, ncol=5)
    axes[2].set_xlabel('Time (hours, GPST)', fontsize=9)

    fig.tight_layout()
    save(fig, st, 'EXP5_sessions')


# ═══════════════════════════════════════════════════════════════════════════
# SUMMARY 1 — EXP2 best (GEC) all 4 stations on one figure
# ═══════════════════════════════════════════════════════════════════════════
print('\nSummary — EXP2 GEC convergence (all stations)...')
STATION_COLORS = {'HKWS': '#1f77b4', 'KIRU': '#d62728', 'WUH2': '#2ca02c', 'ZIM2': '#ff7f0e'}
fig, axes = plt.subplots(3, 1, figsize=(13, 8), sharex=True)
fig.suptitle('EXP2C — GPS+GAL+BDS Precise PPP: All Stations Compared', fontweight='bold')

for st in STATIONS:
    ref = REFS[st]
    df = parse_pos(pos_file(st, 'EXP2C_GEC'))
    df_e = enu(df, *ref)
    t = hours(df_e)
    for row, comp in enumerate(['dE', 'dN', 'dU']):
        axes[row].plot(t, df_e[comp], color=STATION_COLORS[st], lw=1.0, label=st, alpha=0.85)

for row, (ylabel, thr) in enumerate(
    [('East (m)', 0.1), ('North (m)', 0.1), ('Up (m)', 0.2)]):
    style_ax(axes[row], ylabel, ylim=(-1.0, 1.0) if row < 2 else (-2.0, 2.0))
    axes[row].axhspan(-thr, thr, color='green', alpha=0.07, zorder=0)
axes[0].legend(loc='upper right', fontsize=9)
axes[2].set_xlabel('Time (hours, GPST)', fontsize=9)
fig.tight_layout()
save_summary(fig, 'EXP2_GEC_all_stations')


# ═══════════════════════════════════════════════════════════════════════════
# SUMMARY 2 — EXP5 convergence time bar chart
# ═══════════════════════════════════════════════════════════════════════════
print('\nSummary — EXP5 convergence time bar chart...')
sessions = ['1 h', '2 h', '4 h', '8 h', '24 h']
x = np.arange(len(sessions))
width = 0.2
fig, ax = plt.subplots(figsize=(11, 6))
for i, st in enumerate(STATIONS):
    vals = [conv_times[st].get(s, np.nan) for s in sessions]
    bars = ax.bar(x + i * width, vals, width, label=st, color=STATION_COLORS[st], alpha=0.85)
    for bar, v in zip(bars, vals):
        if not np.isnan(v):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                    f'{v:.1f}h', ha='center', va='bottom', fontsize=7)

ax.set_xlabel('Session duration', fontsize=10)
ax.set_ylabel('Convergence time (hours)', fontsize=10)
ax.set_title('EXP5 — PPP Convergence Time vs Session Length (|E|<10cm, |N|<10cm, |U|<20cm)',
             fontweight='bold')
ax.set_xticks(x + width * 1.5)
ax.set_xticklabels(sessions)
ax.legend(fontsize=9)
ax.grid(axis='y', ls='--', alpha=0.4)
ax.yaxis.set_minor_locator(AutoMinorLocator(4))
fig.tight_layout()
save_summary(fig, 'EXP5_convergence_time')


# ═══════════════════════════════════════════════════════════════════════════
# SUMMARY 3 — EXP4 iono comparison across stations
# ═══════════════════════════════════════════════════════════════════════════
print('\nSummary — EXP4 ionosphere methods (all stations)...')
fig, axes = plt.subplots(4, 3, figsize=(15, 14), sharex=True)
fig.suptitle('EXP4 — Ionosphere Correction Comparison Across All Stations', fontweight='bold',
             fontsize=13)

iono_runs = [
    ('EXP4A_L1_Klobuchar', 'L1+Klobuchar', C['L1_Klob']),
    ('EXP4C_L1_IONEX',     'L1+IONEX',     C['L1_IONEX']),
    ('EXP4B_L1L2_IF',      'L1+L2 IF-LC',  C['L1L2_IF']),
]

for row, st in enumerate(STATIONS):
    ref = REFS[st]
    for col, (label, name, color) in enumerate(iono_runs):
        df = parse_pos(pos_file(st, label))
        df_e = enu(df, *ref)
        t = hours(df_e)
        ax = axes[row, col]
        for comp, ls in [('dE', '-'), ('dN', '--'), ('dU', ':')]:
            lbl = comp[1:] if col == 0 else '_'
            ax.plot(t, df_e[comp], lw=0.8, ls=ls, label=lbl, alpha=0.8,
                    color=color if comp == 'dE' else
                    ('#555' if comp == 'dN' else '#999'))
        style_ax(ax, '' , ylim=(-15, 15))
        ax.set_xlim(0, 24)
        if row == 0:
            ax.set_title(name, fontsize=10, color=color, fontweight='bold')
        if col == 0:
            ax.set_ylabel(f'{st}\nError (m)', fontsize=9)
        if row == 3:
            ax.set_xlabel('Hours (GPST)', fontsize=8)

# legend for E/N/U line styles
from matplotlib.lines import Line2D
legend_els = [Line2D([0], [0], ls='-',  color='k', lw=1, label='East'),
              Line2D([0], [0], ls='--', color='k', lw=1, label='North'),
              Line2D([0], [0], ls=':',  color='k', lw=1, label='Up')]
fig.legend(handles=legend_els, loc='lower center', ncol=3, fontsize=9,
           bbox_to_anchor=(0.5, 0.0))
fig.tight_layout(rect=[0, 0.03, 1, 1])
save_summary(fig, 'EXP4_iono_all_stations')


print('\nAll plots done.')
