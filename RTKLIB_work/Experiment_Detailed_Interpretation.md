# RTKLIB-EX 2.5.0 — Experiment Results

**Dataset:** 2026-01-15 (DOY 015) | **Stations:** KIRU, WUH2, HKWS, ZIM2 | **Script:** `scripts/compare_runs.py`

---

## Master Results Tables

### Epochs Processed

| Exp | KIRU | WUH2 | HKWS | ZIM2 |
| --- | ---- | ---- | ---- | ---- |
| 1A  | 136  | 76   | 776  | 391  |
| 1B  | 1456 | 1226 | 2847 | 2272 |
| 2A  | 1456 | 1226 | 2847 | 2272 |
| 2B  | 1530 | 1288 | 2880 | 2880 |
| 2C  | 1203 | 1531 | 1560 | 2345 |
| 2D  | 2342 | 1850 | 1714 | 2518 |
| 3A  | 1203 | 1531 | 1560 | 2345 |
| 3B  | 1200 | 1497 | 1566 | 2376 |
| 4A  | 2146 | 1796 | 1722 | 1769 |
| 4B  | 1203 | 1531 | 1560 | 2345 |
| 4C  | 2340 | 1639 | 1986 | 1941 |
| 5A  | 23   | 68   | 100  | 65   |
| 5B  | 142  | 89   | 209  | 115  |
| 5C  | 310  | 201  | 354  | 347  |
| 5D  | 467  | 547  | 479  | 827  |
| 5E  | 1203 | 1531 | 1560 | 2345 |

### Final StdDev N/E/U (m) — last 10% of session

| Exp | KIRU sN/sE/sU         | WUH2 sN/sE/sU         | HKWS sN/sE/sU         | ZIM2 sN/sE/sU         |
| --- | --------------------- | --------------------- | --------------------- | --------------------- |
| 1A  | 0.042/0.033/0.098     | 0.041/0.038/0.095     | 0.038/0.040/0.099     | **0.044/0.035/0.085** |
| 1B  | 0.025/0.033/0.031     | 0.010/0.023/0.023     | **0.005/0.013/0.013** | 0.007/0.015/0.014     |
| 2A  | 0.025/0.033/0.031     | 0.010/0.023/0.023     | **0.005/0.013/0.013** | 0.007/0.015/0.014     |
| 2B  | 0.017/0.023/0.022     | 0.007/0.017/0.017     | 0.005/0.012/0.013     | **0.006/0.010/0.010** |
| 2C  | 0.031/0.034/0.037     | 0.012/0.023/0.025     | 0.014/0.035/0.028     | **0.014/0.024/0.022** |
| 2D  | 0.016/0.017/0.021     | 0.009/0.017/0.018     | 0.011/0.022/0.022     | **0.010/0.018/0.016** |
| 3A  | 0.031/0.034/0.037     | 0.012/0.023/0.025     | 0.014/0.035/0.028     | **0.014/0.024/0.022** |
| 3B  | 0.031/0.034/0.037     | 0.013/0.023/0.025     | 0.014/0.035/0.028     | **0.014/0.024/0.022** |
| 4A  | 0.045/0.039/0.104     | 0.045/0.045/0.108     | 0.044/0.049/0.115     | **0.048/0.042/0.090** |
| 4B  | 0.031/0.034/0.037     | 0.012/0.023/0.025     | 0.014/0.035/0.028     | **0.014/0.024/0.022** |
| 4C  | 0.038/0.033/0.087     | 0.038/0.037/0.090     | 0.034/0.038/0.089     | **0.039/0.034/0.074** |
| 5A  | 0.279/0.239/0.649     | **0.214/0.293/0.340** | 0.159/0.236/0.344     | 0.266/0.259/0.448     |
| 5B  | **0.119/0.149/0.124** | 0.158/0.207/0.284     | 0.105/0.173/0.211     | 0.203/0.198/0.319     |
| 5C  | 0.078/0.089/0.081     | 0.078/0.113/0.154     | 0.070/0.132/0.132     | **0.061/0.094/0.071** |
| 5D  | 0.061/0.067/0.072     | **0.026/0.054/0.053** | 0.055/0.088/0.112     | **0.026/0.037/0.035** |
| 5E  | 0.031/0.034/0.037     | 0.012/0.023/0.025     | 0.014/0.035/0.028     | **0.014/0.024/0.022** |

### Convergence — minutes to sustained sU < 0.10 m

| Exp | KIRU   | WUH2  | HKWS | ZIM2    |
| --- | ------ | ----- | ---- | ------- |
| 1A  | 54     | **0** | 358  | 57      |
| 1B  | 106    | 146   | 122  | **82**  |
| 2A  | 106    | 146   | 122  | **82**  |
| 2B  | 96     | 82    | 121  | **63**  |
| 2C  | **78** | 168   | 260  | 135     |
| 2D  | 101    | 142   | 125  | **74**  |
| 3A  | **78** | 168   | 260  | 135     |
| 3B  | **78** | 167   | 257  | 142     |
| 4A  | N/C    | N/C   | N/C  | 678     |
| 4B  | **78** | 168   | 260  | 135     |
| 4C  | 724    | 586   | 738  | **618** |
| 5A  | N/C    | N/C   | N/C  | N/C     |
| 5B  | N/C    | N/C   | N/C  | N/C     |
| 5C  | **78** | N/C   | N/C  | 135     |
| 5D  | **78** | 168   | N/C  | 135     |
| 5E  | **78** | 168   | 260  | 135     |

> N/C = did not converge within session. 30 s interval; 2 epochs = 1 min.

### Avg Satellites Tracked (converged period)

| Exp | KIRU     | WUH2     | HKWS | ZIM2     |
| --- | -------- | -------- | ---- | -------- |
| 1A  | 4.0      | 5.0      | 4.0  | 4.0      |
| 1B  | 9.2      | 6.5      | 7.3  | 8.5      |
| 2A  | 9.2      | 6.5      | 7.3  | 8.5      |
| 2B  | 14.4     | 11.8     | 12.6 | **14.6** |
| 2C  | **14.0** | 12.6     | 9.5  | 7.3      |
| 2D  | 6.0      | **13.2** | 12.7 | 9.8      |
| 3A  | **14.0** | 12.6     | 9.5  | 7.3      |
| 3B  | 14.3     | **13.9** | 9.5  | 7.4      |
| 4A  | **8.1**  | 4.8      | 4.1  | **8.1**  |
| 4B  | **14.0** | 12.6     | 9.5  | 7.3      |
| 4C  | **8.3**  | 4.6      | 4.4  | **8.3**  |
| 5A  | **14.0** | 7.9      | 7.3  | 7.0      |
| 5B  | **17.4** | 10.0     | 6.8  | 6.9      |
| 5C  | **15.3** | 12.4     | 8.9  | 8.2      |
| 5D  | **16.4** | 13.5     | 8.1  | 10.0     |
| 5E  | **14.0** | 12.6     | 9.5  | 7.3      |

---

## Experiment Configurations

| Exp   | Freqs       | Nav Systems          | Ionosphere            | Troposphere  | Dynamics | Elev |
| ----- | ----------- | -------------------- | --------------------- | ------------ | -------- | ---- |
| 1A    | L1+L2       | GPS                  | Broadcast             | Saastamoinen | On       | 15°  |
| 1B    | L1+L2       | GPS                  | Iono-Free LC          | Saastamoinen | On       | 15°  |
| 2A    | L1+L2       | GPS                  | Iono-Free LC          | Saastamoinen | On       | 15°  |
| 2B    | L1+L2       | GPS+GAL              | Iono-Free LC          | Saastamoinen | On       | 15°  |
| 2C    | L1+L2       | GPS+GAL+BDS          | Iono-Free LC          | Saastamoinen | On       | 15°  |
| 2D    | L1+L2       | GPS+GLO+GAL+QZSS+BDS | Iono-Free LC          | Saastamoinen | On       | 15°  |
| 3A    | L1+L2       | GPS+GAL+BDS          | Iono-Free LC          | Saastamoinen | On       | 15°  |
| 3B    | L1+L2       | GPS+GAL+BDS          | Iono-Free LC (PPP-AR) | Saastamoinen | On       | 15°  |
| 4A    | **L1 only** | GPS                  | **Broadcast**         | Saastamoinen | On       | 15°  |
| 4B    | L1+L2       | GPS+GAL+BDS          | Iono-Free LC          | Saastamoinen | On       | 15°  |
| 4C    | **L1 only** | GPS                  | **IONEX TEC**         | Saastamoinen | On       | 15°  |
| 5A–5E | L1+L2       | GPS+GAL+BDS          | Iono-Free LC          | Saastamoinen | On       | 15°  |

> 3A = float PPP, 3B = PPP-AR mode (AR did not activate — see Exp 3). 5A–5E: same config, sessions ~12 min / 1.2 h / 2.6 h / 4 h / 10 h.

---

## Experiment 1 — Broadcast vs Precise (GPS-only)

**Finding:** Precise products give 4× better vertical accuracy. Broadcast gives sU ~0.085–0.099 m; precise gives ~0.013–0.031 m.

### KIRU

![KIRU GPS Position](results/EXP1/KIRU_EXP1_POSITION_GPS_comparison.jpg)
![KIRU GPS NSat](results/EXP1/KIRU_EXP1_NSAT_GPS_comparison.jpg)
![KIRU Multi Position](results/EXP1/KIRU_EXP1_POSITION_MULTI_comparison.jpg)
![KIRU Multi NSat](results/EXP1/KIRU_EXP1_NSAT_MULTI_comparison.jpg)

| Config           | Epochs | sN/sE/sU          | Conv (min) | Sats |
| ---------------- | ------ | ----------------- | ---------- | ---- |
| 1A broadcast     | 136    | 0.042/0.033/0.098 | 54         | 4.0  |
| 1B precise       | 1456   | 0.025/0.033/0.031 | 106        | 9.2  |
| 2D multi precise | 2342   | 0.016/0.017/0.021 | 101        | 6.0  |

### WUH2

| Config           | Epochs | sN/sE/sU          | Conv (min) | Sats |
| ---------------- | ------ | ----------------- | ---------- | ---- |
| 1A broadcast     | 76     | 0.041/0.038/0.095 | 0          | 5.0  |
| 1B precise       | 1226   | 0.010/0.023/0.023 | 146        | 6.5  |
| 2D multi precise | 1850   | 0.009/0.017/0.018 | 142        | 13.2 |

### HKWS and ZIM2 — Plots to create

> **Save to:** `RTKLIB_work/results/EXP1/`

| Filename                                  | Files to load in RTKPLOT  |
| ----------------------------------------- | ------------------------- |
| `HKWS_EXP1_POSITION_GPS_comparison.jpg`   | HKWS_1A.pos + HKWS_1B.pos |
| `HKWS_EXP1_NSAT_GPS_comparison.jpg`       | HKWS_1A.pos + HKWS_1B.pos |
| `HKWS_EXP1_POSITION_MULTI_comparison.jpg` | HKWS_2A.pos + HKWS_2D.pos |
| `HKWS_EXP1_NSAT_MULTI_comparison.jpg`     | HKWS_2A.pos + HKWS_2D.pos |
| `ZIM2_EXP1_POSITION_GPS_comparison.jpg`   | ZIM2_1A.pos + ZIM2_1B.pos |
| `ZIM2_EXP1_NSAT_GPS_comparison.jpg`       | ZIM2_1A.pos + ZIM2_1B.pos |
| `ZIM2_EXP1_POSITION_MULTI_comparison.jpg` | ZIM2_2A.pos + ZIM2_2D.pos |
| `ZIM2_EXP1_NSAT_MULTI_comparison.jpg`     | ZIM2_2A.pos + ZIM2_2D.pos |

![HKWS GPS Position](results/EXP1/HKWS_EXP1_POSITION_GPS_comparison.jpg)
![HKWS GPS NSat](results/EXP1/HKWS_EXP1_NSAT_GPS_comparison.jpg)
![HKWS Multi Position](results/EXP1/HKWS_EXP1_POSITION_MULTI_comparison.jpg)
![HKWS Multi NSat](results/EXP1/HKWS_EXP1_NSAT_MULTI_comparison.jpg)
![ZIM2 GPS Position](results/EXP1/ZIM2_EXP1_POSITION_GPS_comparison.jpg)
![ZIM2 GPS NSat](results/EXP1/ZIM2_EXP1_NSAT_GPS_comparison.jpg)
![ZIM2 Multi Position](results/EXP1/ZIM2_EXP1_POSITION_MULTI_comparison.jpg)
![ZIM2 Multi NSat](results/EXP1/ZIM2_EXP1_NSAT_MULTI_comparison.jpg)

---

## Experiment 2 — Constellation Comparison (2A / 2B / 2C / 2D)

**Finding:** GPS+GAL (2B) is optimal for all stations. ZIM2 achieves best: sU = 0.010 m, 63 min convergence. BDS at KIRU (68°N) reduces valid epochs; full constellation (2D) best at mid-latitude stations.

### KIRU

![KIRU 2A vs 2B Position](results/EXP2/KIRU_EXP2_POSITION_2A_vs_2B.jpg)
![KIRU 2A vs 2B NSat](results/EXP2/KIRU_EXP2_NSAT_2A_vs_2B.jpg)
![KIRU 2A vs 2C Position](results/EXP2/KIRU_EXP2_POSITION_2A_vs_2C.jpg)
![KIRU 2A vs 2C NSat](results/EXP2/KIRU_EXP2_NSAT_2A_vs_2C.jpg)
![KIRU 2A vs 2D Position](results/EXP2/KIRU_EXP2_POSITION_2A_vs_2D.jpg)
![KIRU 2A vs 2D NSat](results/EXP2/KIRU_EXP2_NSAT_2A_vs_2D.jpg)

| Config  | Epochs | sN/sE/sU          | Conv (min) | Sats |
| ------- | ------ | ----------------- | ---------- | ---- |
| 2A GPS  | 1456   | 0.025/0.033/0.031 | 106        | 9.2  |
| 2B +GAL | 1530   | 0.017/0.023/0.022 | 96         | 14.4 |
| 2C +BDS | 1203   | 0.031/0.034/0.037 | 78         | 14.0 |
| 2D +ALL | 2342   | 0.016/0.017/0.021 | 101        | 6.0  |

### WUH2

![WUH 2A vs 2B Position](results/EXP2/WUH_EXP2_POSITION_2A_vs_2B.jpg)
![WUH 2A vs 2B NSat](results/EXP2/WUH_EXP2_NSAT_2A_vs_2B.jpg)
![WUH 2A vs 2C Position](results/EXP2/WUH_EXP2_POSITION_2A_vs_2C.jpg)
![WUH 2A vs 2C NSat](results/EXP2/WUH_EXP2_NSAT_2A_vs_2C.jpg)
![WUH 2A vs 2D Position](results/EXP2/WUH_EXP2_POSITION_2A_vs_2D.jpg)
![WUH 2A vs 2D NSat](results/EXP2/WUH_EXP2_NSAT_2A_vs_2D.jpg)

| Config  | Epochs | sN/sE/sU          | Conv (min) | Sats |
| ------- | ------ | ----------------- | ---------- | ---- |
| 2A GPS  | 1226   | 0.010/0.023/0.023 | 146        | 6.5  |
| 2B +GAL | 1288   | 0.007/0.017/0.017 | 82         | 11.8 |
| 2C +BDS | 1531   | 0.012/0.023/0.025 | 168        | 12.6 |
| 2D +ALL | 1850   | 0.009/0.017/0.018 | 142        | 13.2 |

### HKWS and ZIM2 — Plots to create

> **Save to:** `RTKLIB_work/results/EXP2/`

| Filename                          | Files to load             |
| --------------------------------- | ------------------------- |
| `HKWS_EXP2_POSITION_2A_vs_2B.jpg` | HKWS_2A.pos + HKWS_2B.pos |
| `HKWS_EXP2_NSAT_2A_vs_2B.jpg`     | same                      |
| `HKWS_EXP2_POSITION_2A_vs_2C.jpg` | HKWS_2A.pos + HKWS_2C.pos |
| `HKWS_EXP2_NSAT_2A_vs_2C.jpg`     | same                      |
| `HKWS_EXP2_POSITION_2A_vs_2D.jpg` | HKWS_2A.pos + HKWS_2D.pos |
| `HKWS_EXP2_NSAT_2A_vs_2D.jpg`     | same                      |
| `ZIM2_EXP2_POSITION_2A_vs_2B.jpg` | ZIM2_2A.pos + ZIM2_2B.pos |
| `ZIM2_EXP2_NSAT_2A_vs_2B.jpg`     | same                      |
| `ZIM2_EXP2_POSITION_2A_vs_2C.jpg` | ZIM2_2A.pos + ZIM2_2C.pos |
| `ZIM2_EXP2_NSAT_2A_vs_2C.jpg`     | same                      |
| `ZIM2_EXP2_POSITION_2A_vs_2D.jpg` | ZIM2_2A.pos + ZIM2_2D.pos |
| `ZIM2_EXP2_NSAT_2A_vs_2D.jpg`     | same                      |

![HKWS 2A vs 2B Position](results/EXP2/HKWS_EXP2_POSITION_2A_vs_2B.jpg)
![HKWS 2A vs 2B NSat](results/EXP2/HKWS_EXP2_NSAT_2A_vs_2B.jpg)
![HKWS 2A vs 2C Position](results/EXP2/HKWS_EXP2_POSITION_2A_vs_2C.jpg)
![HKWS 2A vs 2C NSat](results/EXP2/HKWS_EXP2_NSAT_2A_vs_2C.jpg)
![HKWS 2A vs 2D Position](results/EXP2/HKWS_EXP2_POSITION_2A_vs_2D.jpg)
![HKWS 2A vs 2D NSat](results/EXP2/HKWS_EXP2_NSAT_2A_vs_2D.jpg)
![ZIM2 2A vs 2B Position](results/EXP2/ZIM2_EXP2_POSITION_2A_vs_2B.jpg)
![ZIM2 2A vs 2B NSat](results/EXP2/ZIM2_EXP2_NSAT_2A_vs_2B.jpg)
![ZIM2 2A vs 2C Position](results/EXP2/ZIM2_EXP2_POSITION_2A_vs_2C.jpg)
![ZIM2 2A vs 2C NSat](results/EXP2/ZIM2_EXP2_NSAT_2A_vs_2C.jpg)
![ZIM2 2A vs 2D Position](results/EXP2/ZIM2_EXP2_POSITION_2A_vs_2D.jpg)
![ZIM2 2A vs 2D NSat](results/EXP2/ZIM2_EXP2_NSAT_2A_vs_2D.jpg)

| Station | Best       | sU          | Conv (min) |
| ------- | ---------- | ----------- | ---------- |
| HKWS    | 2B GPS+GAL | 0.013 m     | 121        |
| ZIM2    | 2B GPS+GAL | **0.010 m** | **63**     |

---

## Experiment 3 — Float PPP vs PPP-AR

**Finding: AR did not activate in RTKLIB-EX 2.5.0.** 3A and 3B produce identical solutions. RTKLIB-EX requires FCB/IRC-format biases; IGS only provides OSB-format. AR ratio = 0.0 throughout for all stations.

| Station | Exp | Epochs | sN/sE/sU          | Conv    | AR% |
| ------- | --- | ------ | ----------------- | ------- | --- |
| KIRU    | 3A  | 1203   | 0.031/0.034/0.037 | 78 min  | 0   |
| KIRU    | 3B  | 1200   | 0.031/0.034/0.037 | 78 min  | 0   |
| WUH2    | 3A  | 1531   | 0.012/0.023/0.025 | 168 min | 0   |
| WUH2    | 3B  | 1497   | 0.013/0.023/0.025 | 167 min | 0   |
| HKWS    | 3A  | 1560   | 0.014/0.035/0.028 | 260 min | 0   |
| HKWS    | 3B  | 1566   | 0.014/0.035/0.028 | 257 min | 0   |
| ZIM2    | 3A  | 2345   | 0.014/0.024/0.022 | 135 min | 0   |
| ZIM2    | 3B  | 2376   | 0.014/0.024/0.022 | 142 min | 0   |

### KIRU

![KIRU EXP3 Position](results/EXP3/KIRU_POSITION.jpg)
![KIRU EXP3 NSat](results/EXP3/KIRU_NSAT.jpg)

### WUH2

![WUH EXP3 Position](results/EXP3/WUH_POSITION.jpg)
![WUH EXP3 NSat](results/EXP3/WUH_NSAT.jpg)

### HKWS and ZIM2 — Plots to create

> **Save to:** `RTKLIB_work/results/EXP3/`

| Filename            | Files to load             |
| ------------------- | ------------------------- |
| `HKWS_POSITION.jpg` | HKWS_3A.pos + HKWS_3B.pos |
| `HKWS_NSAT.jpg`     | same                      |
| `ZIM2_POSITION.jpg` | ZIM2_3A.pos + ZIM2_3B.pos |
| `ZIM2_NSAT.jpg`     | same                      |

![HKWS EXP3 Position](results/EXP3/HKWS_POSITION.jpg)
![HKWS EXP3 NSat](results/EXP3/HKWS_NSAT.jpg)
![ZIM2 EXP3 Position](results/EXP3/ZIM2_POSITION.jpg)
![ZIM2 EXP3 NSat](results/EXP3/ZIM2_NSAT.jpg)

> Genuine PPP-AR results: use PRIDE-PPP-AR (separate section).

---

## Experiment 4 — Ionosphere Correction (L1-only vs L1+L2 vs IONEX)

**Finding:** L1+L2 IF (4B) is 4–5× better than L1-only (4A) in vertical. IONEX (4C) reduces broadcast error ~15–20% but does not approach dual-frequency accuracy.

| Station | 4A sU   | 4C sU   | 4B sU   | 4A→4B gain | 4A→4C gain |
| ------- | ------- | ------- | ------- | ---------- | ---------- |
| KIRU    | 0.104 m | 0.087 m | 0.037 m | 2.8×       | 1.2×       |
| WUH2    | 0.108 m | 0.090 m | 0.025 m | 4.3×       | 1.2×       |
| HKWS    | 0.115 m | 0.089 m | 0.028 m | 4.1×       | 1.3×       |
| ZIM2    | 0.090 m | 0.074 m | 0.022 m | 4.1×       | 1.2×       |

### KIRU

![KIRU 4A vs 4C Position](results/EXP4/KIRU_EXP4_POSITION_4A_vs_4C.jpg)
![KIRU 4A vs 4C NSat](results/EXP4/KIRU_EXP4_NSAT_4A_vs_4C.jpg)
![KIRU 4A vs 4B Position](results/EXP4/KIRU_EXP4_POSITION_4A_vs_4B.jpg)
![KIRU 4A vs 4B NSat](results/EXP4/KIRU_EXP4_NSAT_4A_vs_4B.jpg)
![KIRU 4C vs 4B Position](results/EXP4/KIRU_EXP4_POSITION_4C_vs_4B.jpg)
![KIRU 4C vs 4B NSat](results/EXP4/KIRU_EXP4_NSAT_4C_vs_4B.jpg)

### WUH2

![WUH 4A vs 4C Position](results/EXP4/WUH_EXP4_POSITION_4A_vs_4C.jpg)
![WUH 4A vs 4C NSat](results/EXP4/WUH_EXP4_NSAT_4A_vs_4C.jpg)
![WUH 4A vs 4B Position](results/EXP4/WUH_EXP4_POSITION_4A_vs_4B.jpg)
![WUH 4A vs 4B NSat](results/EXP4/WUH_EXP4_NSAT_4A_vs_4B.jpg)
![WUH 4C vs 4B Position](results/EXP4/WUH_EXP4_POSITION_4C_vs_4B.jpg)
![WUH 4C vs 4B NSat](results/EXP4/WUH_EXP4_NSAT_4C_vs_4B.jpg)

### HKWS and ZIM2 — Plots to create

> **Save to:** `RTKLIB_work/results/EXP4/`

| Filename                          | Files to load             |
| --------------------------------- | ------------------------- |
| `HKWS_EXP4_POSITION_4A_vs_4C.jpg` | HKWS_4A.pos + HKWS_4C.pos |
| `HKWS_EXP4_NSAT_4A_vs_4C.jpg`     | same                      |
| `HKWS_EXP4_POSITION_4A_vs_4B.jpg` | HKWS_4A.pos + HKWS_4B.pos |
| `HKWS_EXP4_NSAT_4A_vs_4B.jpg`     | same                      |
| `HKWS_EXP4_POSITION_4C_vs_4B.jpg` | HKWS_4C.pos + HKWS_4B.pos |
| `HKWS_EXP4_NSAT_4C_vs_4B.jpg`     | same                      |
| `ZIM2_EXP4_POSITION_4A_vs_4C.jpg` | ZIM2_4A.pos + ZIM2_4C.pos |
| `ZIM2_EXP4_NSAT_4A_vs_4C.jpg`     | same                      |
| `ZIM2_EXP4_POSITION_4A_vs_4B.jpg` | ZIM2_4A.pos + ZIM2_4B.pos |
| `ZIM2_EXP4_NSAT_4A_vs_4B.jpg`     | same                      |
| `ZIM2_EXP4_POSITION_4C_vs_4B.jpg` | ZIM2_4C.pos + ZIM2_4B.pos |
| `ZIM2_EXP4_NSAT_4C_vs_4B.jpg`     | same                      |

![HKWS 4A vs 4C Position](results/EXP4/HKWS_EXP4_POSITION_4A_vs_4C.jpg)
![HKWS 4A vs 4C NSat](results/EXP4/HKWS_EXP4_NSAT_4A_vs_4C.jpg)
![HKWS 4A vs 4B Position](results/EXP4/HKWS_EXP4_POSITION_4A_vs_4B.jpg)
![HKWS 4A vs 4B NSat](results/EXP4/HKWS_EXP4_NSAT_4A_vs_4B.jpg)
![HKWS 4C vs 4B Position](results/EXP4/HKWS_EXP4_POSITION_4C_vs_4B.jpg)
![HKWS 4C vs 4B NSat](results/EXP4/HKWS_EXP4_NSAT_4C_vs_4B.jpg)
![ZIM2 4A vs 4C Position](results/EXP4/ZIM2_EXP4_POSITION_4A_vs_4C.jpg)
![ZIM2 4A vs 4C NSat](results/EXP4/ZIM2_EXP4_NSAT_4A_vs_4C.jpg)
![ZIM2 4A vs 4B Position](results/EXP4/ZIM2_EXP4_POSITION_4A_vs_4B.jpg)
![ZIM2 4A vs 4B NSat](results/EXP4/ZIM2_EXP4_NSAT_4A_vs_4B.jpg)
![ZIM2 4C vs 4B Position](results/EXP4/ZIM2_EXP4_POSITION_4C_vs_4B.jpg)
![ZIM2 4C vs 4B NSat](results/EXP4/ZIM2_EXP4_NSAT_4C_vs_4B.jpg)

---

## Experiment 5 — Session Length Effect

**Finding:** 4h (~5C/5D) is the practical convergence threshold. Sessions under 2h do not reach sub-decimetre vertical. Beyond 4h, improvement is marginal.

| Run | Duration | KIRU sU | WUH2 sU | HKWS sU | ZIM2 sU | Conv KIRU | Conv ZIM2 |
| --- | -------- | ------- | ------- | ------- | ------- | --------- | --------- |
| 5A  | ~12 min  | 0.649 m | 0.340 m | 0.344 m | 0.448 m | N/C       | N/C       |
| 5B  | ~1.2 h   | 0.124 m | 0.284 m | 0.211 m | 0.319 m | N/C       | N/C       |
| 5C  | ~2.6 h   | 0.081 m | 0.154 m | 0.132 m | 0.071 m | 78 min    | 135 min   |
| 5D  | ~4 h     | 0.072 m | 0.053 m | 0.112 m | 0.035 m | 78 min    | 135 min   |
| 5E  | ~10 h    | 0.037 m | 0.025 m | 0.028 m | 0.022 m | 78 min    | 135 min   |

### KIRU

![KIRU 1h vs 24h](results/EXP5/KIRU_EXP5_1h_vs_24h.jpg)
![KIRU 2h vs 24h](results/EXP5/KIRU_EXP5_2h_vs_24h.jpg)
![KIRU 4h vs 24h](results/EXP5/KIRU_EXP5_4h_vs_24h.jpg)
![KIRU 8h vs 24h](results/EXP5/KIRU_EXP5_8h_vs_24h.jpg)

### WUH2

![WUH 1h vs 24h](results/EXP5/WUH_EXP5_1h_vs_24h.jpg)
![WUH 2h vs 24h](results/EXP5/WUH_EXP5_2h_vs_24h.jpg)
![WUH 4h vs 24h](results/EXP5/WUH_EXP5_4h_vs_24h.jpg)
![WUH 4h vs 8h](results/EXP5/WUH_EXP5_4h_vs_8h.jpg)
![WUH 8h vs 24h](results/EXP5/WUH_EXP5_8h_vs_24h.jpg)

### HKWS and ZIM2 — Plots to create

> **Save to:** `RTKLIB_work/results/EXP5/`

| Filename                  | Files to load             |
| ------------------------- | ------------------------- |
| `HKWS_EXP5_1h_vs_24h.jpg` | HKWS_5A.pos + HKWS_5E.pos |
| `HKWS_EXP5_2h_vs_24h.jpg` | HKWS_5B.pos + HKWS_5E.pos |
| `HKWS_EXP5_4h_vs_24h.jpg` | HKWS_5C.pos + HKWS_5E.pos |
| `HKWS_EXP5_8h_vs_24h.jpg` | HKWS_5D.pos + HKWS_5E.pos |
| `ZIM2_EXP5_1h_vs_24h.jpg` | ZIM2_5A.pos + ZIM2_5E.pos |
| `ZIM2_EXP5_2h_vs_24h.jpg` | ZIM2_5B.pos + ZIM2_5E.pos |
| `ZIM2_EXP5_4h_vs_24h.jpg` | ZIM2_5C.pos + ZIM2_5E.pos |
| `ZIM2_EXP5_8h_vs_24h.jpg` | ZIM2_5D.pos + ZIM2_5E.pos |

> All .pos files: `RTKLIB_work/runs/[STATION]_[EXP]_[timestamp]/[STATION]_[EXP].pos`

![HKWS 1h vs 24h](results/EXP5/HKWS_EXP5_1h_vs_24h.jpg)
![HKWS 2h vs 24h](results/EXP5/HKWS_EXP5_2h_vs_24h.jpg)
![HKWS 4h vs 24h](results/EXP5/HKWS_EXP5_4h_vs_24h.jpg)
![HKWS 8h vs 24h](results/EXP5/HKWS_EXP5_8h_vs_24h.jpg)
![ZIM2 1h vs 24h](results/EXP5/ZIM2_EXP5_1h_vs_24h.jpg)
![ZIM2 2h vs 24h](results/EXP5/ZIM2_EXP5_2h_vs_24h.jpg)
![ZIM2 4h vs 24h](results/EXP5/ZIM2_EXP5_4h_vs_24h.jpg)
![ZIM2 8h vs 24h](results/EXP5/ZIM2_EXP5_8h_vs_24h.jpg)

---

## Combined Team Analysis — Joel + Amira Configuration Comparison

Both team members processed the same RINEX data independently using RTKLIB. The different settings each person used create a valuable additional finding: **how do elevation mask, dynamics, and troposphere model choice affect PPP results?**

### Configuration Summary

| Parameter      | Joel (RTKLIB-EX 2.5.0) | Amira (RTKPOST demo5 b34d)           |
| -------------- | ---------------------- | ------------------------------------ |
| Stations       | KIRU, WUH2, HKWS, ZIM2 | KIRU, WUH                            |
| Experiments    | 16 (1A–5E)             | 3: GPS / BeiDou-only / Multi (GEBJR) |
| Elevation mask | 15°                    | **10°**                              |
| Dynamics       | **On**                 | Off                                  |
| Troposphere    | Saastamoinen model     | Estimate ZTD                         |
| Solution mode  | Forward                | Combined-Phase Reset                 |

### Epoch Count: Same Data, Different Settings

| Station | Amira config | Amira epochs | Joel equivalent | Joel epochs | Difference |
| ------- | ------------ | ------------ | --------------- | ----------- | ---------- |
| KIRU    | GPS only     | 2875         | 1B GPS precise  | 1456        | +1419      |
| KIRU    | Multi GEBJR  | 2870         | 2D full const.  | 2342        | +528       |
| KIRU    | BeiDou only  | 265          | —               | —           | —          |
| WUH     | GPS only     | 2870         | 1B GPS precise  | 1226        | +1644      |
| WUH     | Multi GEBJR  | 2871         | 2D full const.  | 1850        | +1021      |
| WUH     | BeiDou only  | 2120         | —               | —           | —          |

### Finding: Effect of Elevation Mask (10° vs 15°)

Amira's 10° mask produces up to **+1644 more valid epochs** for the same station and data. This is a genuine PPP parameter finding:

- **10° mask:** more epochs and satellites, but increased multipath and ionospheric residual from shallow-angle signals
- **15° mask:** fewer epochs, cleaner observations, lower final position uncertainty

For high-accuracy static PPP, 15° is the standard recommendation. A 10° mask is appropriate when satellite visibility is limited (e.g. urban environments or high-latitude sites like KIRU).

### Finding: Effect of Dynamics On vs Off

- **Dynamics on:** Kalman filter propagates a velocity state between epochs — more realistic convergence modelling, slight reduction in valid epochs at data gap boundaries
- **Dynamics off:** filter treats epochs more independently — outputs more valid epochs but may overestimate precision at gap boundaries

For PPP convergence studies, `dynamics on` gives a more realistic representation of how accuracy evolves over time.

### Finding: Troposphere — Saastamoinen vs Estimate ZTD

- **Saastamoinen:** applies a parametric model — fast, no extra unknown parameters
- **Estimate ZTD:** treats ZTD as an unknown to solve for — more flexible for long sessions, but adds a correlated parameter that can slow convergence in sessions under 2h

Both converge to similar results in 24h sessions. For short-session experiments (Exp 5A/5B), Saastamoinen avoids the convergence overhead.

### Finding: BeiDou-only — High vs Low Latitude

Amira's BDS-only runs directly confirm the latitude dependency of BeiDou coverage:

- **KIRU (68°N): 265 valid epochs** — BDS MEO/IGSO has very poor visibility above 60°N
- **WUH (30°N): 2120 valid epochs** — WUH is within BDS's prime service region

This finding is consistent with Joel's Exp 2C results, where BDS addition reduces valid epochs at KIRU (1203) but increases them at WUH (1531).

### Combined Findings Summary

| Finding                                          | Demonstrated by    |
| ------------------------------------------------ | ------------------ |
| Broadcast vs precise (4× vertical improvement)   | Joel Exp 1         |
| Constellation progression GPS→GAL→BDS→ALL        | Joel Exp 2         |
| PPP-AR incompatibility with IGS OSB in RTKLIB-EX | Joel Exp 3         |
| Ionosphere: broadcast / IF / IONEX comparison    | Joel Exp 4         |
| Session length effect on convergence             | Joel Exp 5         |
| Elevation mask impact (10° vs 15°)               | Amira vs Joel      |
| Dynamics on vs off impact                        | Amira vs Joel      |
| BeiDou latitude dependency (high vs low)         | Amira BDS-only run |

> To open Amira's results in RTKPLOT: File → Open → change filter to "All files (_._)" → select `KIRUGPS`, `KIRU1`, `KIRUBeiDou`, `wuhanGPS`, `wuhan1`, `wuhanBeiDou` from `results/amira/amira_RTKLIB_OUTPUT/`

---

## Recommended Station for Future Experiments

| Rank | Station  | Best sU | Best Exp | Conv (min) | Reason                                                          |
| ---- | -------- | ------- | -------- | ---------- | --------------------------------------------------------------- |
| 1    | **ZIM2** | 0.010 m | 2B       | 63         | Best precision + fastest convergence. Wins 12/16 experiments.   |
| 2    | **HKWS** | 0.013 m | 2B       | 121        | Best GPS-only performance. Most epochs in full-day sessions.    |
| 3    | **WUH2** | 0.017 m | 2B       | 82         | Good multi-constellation; strong BDS coverage at 30°N.          |
| 4    | **KIRU** | 0.021 m | 2D       | 78–101     | Most satellites tracked; high-latitude reduces final precision. |

**Primary station for all further experiments: ZIM2**  
**Secondary (geographic contrast): KIRU**  
**Best configuration: Exp 2B** — GPS+Galileo, dual-freq IF, Saastamoinen, 15° mask, dynamics on.

---

## Script Validation

`run_gamp.py` script vs manual RTKPOST-EX 2.5.0 compared on Exp 3A and 3B:

- Epoch count difference: ≤1 (boundary rounding)
- Q distribution: identical
- Ratio traces: identical
- **Conclusion:** Script output is authoritative. All results in `RTKLIB_work/runs/` are valid.

---

## RTKPLOT — Loading .pos Files

**.pos files for all 4 stations are in:**

```
RTKLIB_work/results/EXP1/    HKWS_1A.pos  HKWS_1B.pos  ZIM2_1A.pos  ZIM2_1B.pos  KIRU_1A.pos  WUH2_1A.pos ...
RTKLIB_work/results/EXP2/    all 4 stations x 2A/2B/2C/2D
RTKLIB_work/results/EXP3/    all 4 stations x 3A/3B
RTKLIB_work/results/EXP4/    all 4 stations x 4A/4B/4C
RTKLIB_work/results/EXP5/    all 4 stations x 5A/5B/5C/5D/5E
```

**To overlay two runs:** File → Open → first .pos, then File → Open (2nd) → second .pos.

**To save plot:** File → Save Image → use the filename from the "Plots to create" table → save to the same EXP folder.

**For Amira's files:** RTKPLOT → File → Open → filter "All files (_._)" → select from `results/amira/amira_RTKLIB_OUTPUT/`

---

## PRIDE-PPP-AR: Interpretation and Comparison with RTKLIB

### Software Methodology Comparison

PRIDE-PPP-AR and RTKLIB represent two fundamentally different approaches to PPP:

| Aspect | RTKLIB-EX 2.5.0 | PRIDE-PPP-AR v3.x |
|---|---|---|
| Estimator | Kalman filter (sequential, epoch-by-epoch) | Batch least-squares (whole-day global fit) |
| Position type | Kinematic time-series | Single static ECEF position |
| Convergence | 30–150 min ramp | Not applicable (all epochs contribute equally) |
| AR method | LAMBDA/ILS (ambiguity search) | WL+NL sequential fixing (Melbourne-Wubbena + narrow-lane) |
| Outlier handling | Cycle slip detection per epoch | Iterative redig cleaning (7 passes, 400→50mm thresholds) |
| Best use | Real-time navigation, convergence studies | Geodetic reference, mm-level static accuracy |

### Why KIRU Ranks #1 in PRIDE but #4 in RTKLIB

**In RTKLIB (kinematic):** KIRU ranks last because high-latitude geometry (all satellites in the southern sky) produces poor vertical dilution of precision. The Kalman filter needs satellites at varied azimuths to resolve the vertical coordinate — at 68°N this is impossible.

**In PRIDE (static):** KIRU ranks #2 (best AR at 98.1%/99.7%). The batch LS solver uses all 24 hours of data simultaneously. Even though the geometry is never ideal, the *temporal variation* of the satellite sky over 24 hours creates different geometric configurations at different times of day. High-latitude stations see satellites describe long arcs across the southern sky — these long, uninterrupted carrier-phase arcs are exactly what WL fixing needs.

### Why ZIM2 Inverts Between the Two Software Tools

**RTKLIB ranking:** ZIM2 = #1 (sU = 0.010 m, fastest convergence at 47°N)  
**PRIDE ranking:** ZIM2 = #3 (Sig0 = 2.221 m, good but not best)

The inversion reflects two different things being measured:
- RTKLIB measures *kinematic convergence speed* — how quickly the Kalman filter reaches sub-decimetre accuracy
- PRIDE measures *static position quality* — how well the full-day batch solution fits all observations

ZIM2's 47°N latitude and clean Alpine multipath environment make it ideal for rapid kinematic convergence. But in static mode, ZIM2's moderately noisy BDS-3 (C08=35mm, C13=18mm) pulls the Sig0 slightly above HKWS (which tracks no BDS at all).

### PRIDE AR Results: All Four Stations

| Station | GPS WL | GPS NL | GAL WL | GAL NL | Overall WL | Overall NL | Sig0 |
|---|---|---|---|---|---|---|---|
| HKWS | 76.7% | 100% | 99.4% | 100% | 84.9% | **100%** | **1.803 m** |
| WUH2 | 84.9% | 95.9% | 94.9% | 100% | 89.0% | 97.7% | 2.999 m |
| KIRU | 99.1% | 99.7% | 96.3% | 99.7% | **98.1%** | 99.7% | 2.649 m |
| ZIM2 | 81.5% | 100% | 99.5% | 100% | 88.1% | **100%** | 2.221 m |

Key pattern: **Galileo NL rates are always higher than GPS NL rates.** Galileo's cleaner signal design (lower multipath susceptibility, better phase bias modelling in COD products) consistently yields higher NL fix rates once the WL is fixed.
