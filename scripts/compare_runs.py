import os
import glob
import math
import re
from pathlib import Path

runs_dir = r'C:\PPP_PROJECT\RTKLIB_work\runs'
stations = ['KIRU', 'WUH2', 'HKWS', 'ZIM2']
exps = ['1A', '1B', '2A', '2B', '2C', '2D', '3A', '3B',
        '4A', '4B', '4C', '5A', '5B', '5C', '5D', '5E']


def parse_pos(pos_file):
    epochs = []
    config = {}
    with open(pos_file, 'r', errors='ignore') as f:
        for line in f:
            if line.startswith('%'):
                m = re.match(r'%\s+(\w[\w\s/]+?)\s*:\s*(.+)', line)
                if m:
                    config[m.group(1).strip()] = m.group(2).strip()
                continue
            if line.strip() == '':
                continue
            parts = line.split()
            if len(parts) >= 14:
                try:
                    lat = float(parts[2])
                    lon = float(parts[3])
                    hgt = float(parts[4])
                    q = int(parts[5])
                    ns = int(parts[6])
                    sdn = float(parts[7])
                    sde = float(parts[8])
                    sdu = float(parts[9])
                    epochs.append({'lat': lat, 'lon': lon, 'hgt': hgt,
                                  'q': q, 'ns': ns, 'sdn': sdn, 'sde': sde, 'sdu': sdu})
                except:
                    pass
    return epochs, config


results = {}
for station in stations:
    results[station] = {}
    for exp in exps:
        if exp in ['2A', '2B', '2C', '2D']:
            pattern = os.path.join(runs_dir, f'{station}_EXP2*{exp}*')
        else:
            pattern = os.path.join(runs_dir, f'{station}_{exp}_*')
        folders = glob.glob(pattern)
        if not folders:
            continue
        folder = sorted(folders)[-1]
        pos_files = [f for f in glob.glob(
            os.path.join(folder, '*.pos')) if 'events' not in f]
        if not pos_files:
            continue
        epochs, config = parse_pos(pos_files[0])
        if not epochs:
            continue

        n = len(epochs)
        avg_ns = sum(e['ns'] for e in epochs) / n
        avg_sdn = sum(e['sdn'] for e in epochs) / n
        avg_sde = sum(e['sde'] for e in epochs) / n
        avg_sdu = sum(e['sdu'] for e in epochs) / n

        # Final 10% stats (after convergence)
        tail_start = max(0, int(n * 0.9))
        tail = epochs[tail_start:]
        fin_sdn = sum(e['sdn'] for e in tail) / len(tail) if tail else 999
        fin_sde = sum(e['sde'] for e in tail) / len(tail) if tail else 999
        fin_sdu = sum(e['sdu'] for e in tail) / len(tail) if tail else 999
        fin_ns = sum(e['ns'] for e in tail) / len(tail) if tail else 0

        # Convergence: first epoch where sdu < 0.10 m and stays < 0.10 for 10 consecutive epochs
        conv_ep = None
        for i in range(len(epochs) - 9):
            if all(epochs[i+j]['sdu'] < 0.10 for j in range(10)):
                conv_ep = i
                break

        results[station][exp] = {
            'n': n,
            'avg_ns': avg_ns,
            'avg_sdn': avg_sdn, 'avg_sde': avg_sde, 'avg_sdu': avg_sdu,
            'fin_sdn': fin_sdn, 'fin_sde': fin_sde, 'fin_sdu': fin_sdu,
            'fin_ns':  fin_ns,
            'conv_ep': conv_ep,
            'config':  config
        }

# -------------------------------------------------------
# Print config info per experiment (extracted from KIRU)
# -------------------------------------------------------
print('='*90)
print('EXPERIMENT CONFIGURATIONS (from KIRU .pos headers)')
print('='*90)
cfg_keys = ['pos mode', 'freqs', 'navi sys',
            'elev mask', 'dynamics', 'ionos opt', 'tropo opt']
for exp in exps:
    d = results['KIRU'].get(exp)
    if not d:
        d = results['WUH2'].get(exp) or results['HKWS'].get(
            exp) or results['ZIM2'].get(exp)
    if not d:
        continue
    c = d['config']
    print(f'\nEXP {exp}:')
    for k in cfg_keys:
        print(f'  {k:<12}: {c.get(k, "N/A")}')

# -------------------------------------------------------
# Table 1: Epochs processed
# -------------------------------------------------------
print()
print('='*80)
print('TABLE 1: Epochs Processed')
print('='*80)
print(f"{'Exp':<5} | {'KIRU':>6} | {'WUH2':>6} | {'HKWS':>6} | {'ZIM2':>6}")
print('-'*40)
for exp in exps:
    row = f'{exp:<5} |'
    for st in stations:
        d = results[st].get(exp)
        row += f" {d['n']:>6} |" if d else f" {'N/A':>6} |"
    print(row)

# -------------------------------------------------------
# Table 2: Final StdDev N/E/U
# -------------------------------------------------------
print()
print('='*110)
print(
    'TABLE 2: Final StdDev N/E/U (m) [last 10% of session = converged period]')
print('='*110)
print(f"{'Exp':<5} | {'KIRU (sN/sE/sU)':>20} | {'WUH2 (sN/sE/sU)':>20} | {'HKWS (sN/sE/sU)':>20} | {'ZIM2 (sN/sE/sU)':>20}")
print('-'*95)
for exp in exps:
    row = f'{exp:<5} |'
    for st in stations:
        d = results[st].get(exp)
        if d:
            row += f" {d['fin_sdn']:>5.3f}/{d['fin_sde']:>5.3f}/{d['fin_sdu']:>5.3f}     |"
        else:
            row += f" {'N/A':>20} |"
    print(row)

# -------------------------------------------------------
# Table 3: Convergence
# -------------------------------------------------------
print()
print('='*80)
print('TABLE 3: Convergence — epochs (minutes) to sU < 0.10 m (sustained)')
print('  N/C = not converged  |  30s interval so 2 epochs = 1 minute')
print('='*80)
print(f"{'Exp':<5} | {'KIRU':>12} | {'WUH2':>12} | {'HKWS':>12} | {'ZIM2':>12}")
print('-'*60)
for exp in exps:
    row = f'{exp:<5} |'
    for st in stations:
        d = results[st].get(exp)
        if d:
            c = d['conv_ep']
            if c is not None:
                row += f" {c:>4}ep/{c//2:>3}min |"
            else:
                row += f" {'N/C':>12} |"
        else:
            row += f" {'N/A':>12} |"
    print(row)

# -------------------------------------------------------
# Table 4: Average satellites tracked
# -------------------------------------------------------
print()
print('='*60)
print('TABLE 4: Avg Satellites Tracked (final converged period)')
print('='*60)
print(f"{'Exp':<5} | {'KIRU':>6} | {'WUH2':>6} | {'HKWS':>6} | {'ZIM2':>6}")
print('-'*40)
for exp in exps:
    row = f'{exp:<5} |'
    for st in stations:
        d = results[st].get(exp)
        row += f" {d['fin_ns']:>6.1f} |" if d else f" {'N/A':>6} |"
    print(row)

# -------------------------------------------------------
# Summary: Best experiment per station
# -------------------------------------------------------
print()
print('='*80)
print('SUMMARY: Best Experiment per Station (lowest fin_sdu = best vertical precision)')
print('='*80)
for st in stations:
    best_exp = None
    best_sdu = 999
    for exp in exps:
        d = results[st].get(exp)
        if d and d['fin_sdu'] < best_sdu:
            best_sdu = d['fin_sdu']
            best_exp = exp
    if best_exp:
        d = results[st][best_exp]
        print(
            f"  {st}: EXP {best_exp} -> sN={d['fin_sdn']:.3f}m  sE={d['fin_sde']:.3f}m  sU={d['fin_sdu']:.3f}m  (n={d['n']} epochs)")

print()
print('='*80)
print('SUMMARY: Best Station per Experiment (lowest fin_sdu)')
print('='*80)
for exp in exps:
    best_st = None
    best_sdu = 999
    for st in stations:
        d = results[st].get(exp)
        if d and d['fin_sdu'] < best_sdu:
            best_sdu = d['fin_sdu']
            best_st = st
    if best_st:
        d = results[best_st][exp]
        print(
            f"  EXP {exp}: {best_st} -> sU={d['fin_sdu']:.4f}m  sN={d['fin_sdn']:.4f}m  sE={d['fin_sde']:.4f}m")
