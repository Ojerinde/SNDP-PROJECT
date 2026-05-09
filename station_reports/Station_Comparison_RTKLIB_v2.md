# Station Comparison: KIRU, WUH2, HKWS, ZIM2

> **Source:** `RTKLIB_work/runs/` — all four stations processed with identical configurations.  
> **Analysis tool:** `scripts/compare_runs.py`

---

## 0. Quick Answer: HKWS vs ZIM2

| Criterion                         | HKWS                    | ZIM2                 | Winner  |
| --------------------------------- | ----------------------- | -------------------- | ------- |
| Best vertical precision (sU)      | 0.013 m (Exp 2B)        | **0.010 m (Exp 2B)** | ✅ ZIM2 |
| Fastest convergence               | 121 min (Exp 2B)        | **63 min (Exp 2B)**  | ✅ ZIM2 |
| Most epochs processed (best data) | 2880 (Exp 2B)           | **2880 (Exp 2B)**    | Tie     |
| Best in GPS-only DF (Exp 2A)      | **0.013 m**             | 0.014 m              | ✅ HKWS |
| Best in multi-constellation       | ZIM2 wins in 10/16 exps | 10/16 exps           | ✅ ZIM2 |

**CONCLUSION: ZIM2 is the better station between the two.** It converges faster and achieves lower position uncertainty in nearly all multi-constellation experiments.

---

## 1. Experiment Configurations

| Exp    | Mode       | Frequencies | Nav Systems                          | Ionosphere                       | Duration (approx) |
| ------ | ---------- | ----------- | ------------------------------------ | -------------------------------- | ----------------- |
| **1A** | PPP Static | L1+L2       | GPS only                             | Broadcast (single-freq approach) | Full day          |
| **1B** | PPP Static | L1+L2       | GPS only                             | Iono-Free LC (dual-freq)         | Full day          |
| **2A** | PPP Static | L1+L2       | GPS only                             | Iono-Free LC                     | Full day          |
| **2B** | PPP Static | L1+L2       | GPS + Galileo                        | Iono-Free LC                     | Full day          |
| **2C** | PPP Static | L1+L2       | GPS + Galileo + BDS                  | Iono-Free LC                     | ~10h              |
| **2D** | PPP Static | L1+L2       | GPS + GLONASS + Galileo + QZSS + BDS | Iono-Free LC                     | Full day          |
| **3A** | PPP Static | L1+L2       | GPS + Galileo + BDS                  | Iono-Free LC                     | ~10h              |
| **3B** | PPP Static | L1+L2       | GPS + Galileo + BDS                  | Iono-Free LC                     | ~10h              |
| **4A** | PPP Static | **L1 only** | GPS only                             | Broadcast                        | Full day          |
| **4B** | PPP Static | L1+L2       | GPS + Galileo + BDS                  | Iono-Free LC                     | ~10h              |
| **4C** | PPP Static | **L1 only** | GPS only                             | **IONEX TEC**                    | Full day          |
| **5A** | PPP Static | L1+L2       | GPS + Galileo + BDS                  | Iono-Free LC                     | ~12 min           |
| **5B** | PPP Static | L1+L2       | GPS + Galileo + BDS                  | Iono-Free LC                     | ~1.2 h            |
| **5C** | PPP Static | L1+L2       | GPS + Galileo + BDS                  | Iono-Free LC                     | ~2.6 h            |
| **5D** | PPP Static | L1+L2       | GPS + Galileo + BDS                  | Iono-Free LC                     | ~4 h              |
| **5E** | PPP Static | L1+L2       | GPS + Galileo + BDS                  | Iono-Free LC                     | ~10 h             |

> Troposphere: Saastamoinen model in all experiments. Elevation mask: 15°. Dynamics: on.

---

## 2. Epochs Processed (Data Availability)

All 4 stations have data for **2026-01-15**. ✅

| Exp | KIRU     | WUH2 | HKWS    | ZIM2     |
| --- | -------- | ---- | ------- | -------- |
| 1A  | 136      | 76   | 776     | 391      |
| 1B  | 1456     | 1226 | 2847    | 2272     |
| 2A  | 1456     | 1226 | 2847    | 2272     |
| 2B  | 1530     | 1288 | 2880    | **2880** |
| 2C  | 1203     | 1531 | 1560    | 2345     |
| 2D  | **2342** | 1850 | 1714    | 2518     |
| 3A  | 1203     | 1531 | 1560    | 2345     |
| 3B  | 1200     | 1497 | 1566    | 2376     |
| 4A  | **2146** | 1796 | 1722    | 1769     |
| 4B  | 1203     | 1531 | 1560    | 2345     |
| 4C  | **2340** | 1639 | 1986    | 1941     |
| 5A  | 23       | 68   | 100     | 65       |
| 5B  | 142      | 89   | **209** | 115      |
| 5C  | 310      | 201  | **354** | 347      |
| 5D  | 467      | 547  | 479     | **827**  |
| 5E  | 1203     | 1531 | 1560    | 2345     |

> Note: Exp 1A shows fewer epochs because session start/initialization limited data.  
> Exp 5A–5D are short-session tests to study convergence vs. session length.

---

## 3. Final Position Precision: StdDev N / E / U (metres)

_Last 10% of each session (converged period). Lower = better._

| Exp | KIRU sN/sE/sU         | WUH2 sN/sE/sU         | HKWS sN/sE/sU         | ZIM2 sN/sE/sU         |
| --- | --------------------- | --------------------- | --------------------- | --------------------- |
| 1A  | 0.042/0.033/0.098     | 0.041/0.038/0.095     | 0.038/0.040/0.099     | 0.044/0.035/**0.085** |
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

> **Bold** = best result for that experiment.

---

## 4. Convergence Time (epochs and minutes, @ 30 s interval)

_First sustained period where vertical StdDev (sU) stays below 0.10 m for ≥10 consecutive epochs._  
_N/C = did not converge within session. N/A = no data._

| Exp | KIRU                | WUH2              | HKWS              | ZIM2                  |
| --- | ------------------- | ----------------- | ----------------- | --------------------- |
| 1A  | 109 ep / 54 min     | **0 ep / 0 min**  | 717 ep / 358 min  | 115 ep / 57 min       |
| 1B  | 213 ep / 106 min    | 293 ep / 146 min  | 245 ep / 122 min  | **164 ep / 82 min**   |
| 2A  | 213 ep / 106 min    | 293 ep / 146 min  | 245 ep / 122 min  | **164 ep / 82 min**   |
| 2B  | 193 ep / 96 min     | 165 ep / 82 min   | 242 ep / 121 min  | **127 ep / 63 min**   |
| 2C  | **156 ep / 78 min** | 337 ep / 168 min  | 521 ep / 260 min  | 270 ep / 135 min      |
| 2D  | 202 ep / 101 min    | 284 ep / 142 min  | 250 ep / 125 min  | **149 ep / 74 min**   |
| 3A  | **156 ep / 78 min** | 337 ep / 168 min  | 521 ep / 260 min  | 270 ep / 135 min      |
| 3B  | **156 ep / 78 min** | 335 ep / 167 min  | 514 ep / 257 min  | 284 ep / 142 min      |
| 4A  | N/C                 | N/C               | N/C               | 1356 ep / 678 min     |
| 4B  | **156 ep / 78 min** | 337 ep / 168 min  | 521 ep / 260 min  | 270 ep / 135 min      |
| 4C  | 1448 ep / 724 min   | 1173 ep / 586 min | 1477 ep / 738 min | **1236 ep / 618 min** |
| 5A  | N/C                 | N/C               | N/C               | N/C                   |
| 5B  | N/C                 | N/C               | N/C               | N/C                   |
| 5C  | **156 ep / 78 min** | N/C               | N/C               | 270 ep / 135 min      |
| 5D  | **156 ep / 78 min** | 337 ep / 168 min  | N/C               | 270 ep / 135 min      |
| 5E  | **156 ep / 78 min** | 337 ep / 168 min  | 521 ep / 260 min  | 270 ep / 135 min      |

---

## 5. Average Satellites Tracked (Converged Period)

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
| 4A  | 8.1      | 4.8      | 4.1  | **8.1**  |
| 4B  | **14.0** | 12.6     | 9.5  | 7.3      |
| 4C  | **8.3**  | 4.6      | 4.4  | **8.3**  |
| 5A  | **14.0** | 7.9      | 7.3  | 7.0      |
| 5B  | **17.4** | 10.0     | 6.8  | 6.9      |
| 5C  | **15.3** | 12.4     | 8.9  | 8.2      |
| 5D  | **16.4** | 13.5     | 8.1  | 10.0     |
| 5E  | **14.0** | 12.6     | 9.5  | 7.3      |

---

## 6. Best Experiment Per Station

| Station | Best Exp                    | sN (m) | sE (m) | sU (m) | Epochs |
| ------- | --------------------------- | ------ | ------ | ------ | ------ |
| KIRU    | **2D** (all constellations) | 0.016  | 0.017  | 0.021  | 2342   |
| WUH2    | **2B** (GPS+Galileo)        | 0.007  | 0.017  | 0.017  | 1288   |
| HKWS    | **2B** (GPS+Galileo)        | 0.005  | 0.012  | 0.013  | 2880   |
| ZIM2    | **2B** (GPS+Galileo)        | 0.006  | 0.010  | 0.010  | 2880   |

---

## 7. Best Station Per Experiment

| Exp | Best Station | sU (m) | Why                                          |
| --- | ------------ | ------ | -------------------------------------------- |
| 1A  | **ZIM2**     | 0.085  | Best vertical with broadcast iono correction |
| 1B  | **HKWS**     | 0.013  | Best in GPS-only dual-freq                   |
| 2A  | **HKWS**     | 0.013  | Same as 1B config                            |
| 2B  | **ZIM2**     | 0.010  | Best with GPS+Galileo                        |
| 2C  | **ZIM2**     | 0.022  | Best with GPS+Galileo+BDS                    |
| 2D  | **ZIM2**     | 0.016  | Best with all constellations                 |
| 3A  | **ZIM2**     | 0.022  | Same as 2C                                   |
| 3B  | **ZIM2**     | 0.022  | Same config                                  |
| 4A  | **ZIM2**     | 0.090  | Best in L1-only + broadcast (single-freq)    |
| 4B  | **ZIM2**     | 0.022  | Same as 2C                                   |
| 4C  | **ZIM2**     | 0.074  | Best with IONEX TEC correction               |
| 5A  | WUH2         | 0.340  | Short session, all poor                      |
| 5B  | **KIRU**     | 0.124  | Short session, KIRU slightly better          |
| 5C  | **ZIM2**     | 0.071  | ~2.6h session                                |
| 5D  | **ZIM2**     | 0.035  | ~4h session                                  |
| 5E  | **ZIM2**     | 0.022  | Full GPS+Galileo+BDS                         |

---

## 8. Key Findings

### B. ZIM2 is the best station overall

- Wins in **12 out of 16 experiments** on vertical precision
- Fastest convergence in most dual-frequency experiments (e.g. 63 min in Exp 2B)
- Achieves **sU = 0.010 m** in best experiment (Exp 2B, GPS+Galileo, 2880 epochs)

### C. HKWS is second best

- Wins in GPS-only experiments (1B, 2A) — best single-constellation precision
- Slightly slower convergence than ZIM2 in multi-constellation setups
- Best sU = 0.013 m (Exp 2B)

### D. WUH2 ranks third

- Good performance in multi-constellation (sU ≈ 0.017–0.025 m after convergence)
- Slightly fewer epochs than HKWS/ZIM2
- Competitive in Exp 2D/5D

### E. KIRU ranks fourth in final precision but converges fast

- Highest satellite count (KIRU tracks most sats in Exp 5A–5D)
- Good convergence time in some experiments (best in 2C/3A/3B/5C/5D/5E)
- But weaker final precision than ZIM2/HKWS/WUH2

### F. Best experiment configuration (for all stations): **Exp 2B**

- GPS + Galileo, dual-frequency, Iono-Free LC, Saastamoinen troposphere
- Recommended for Saturday demo and week-long analysis (15–21 Jan)

### G. Session length effect (Exp 5A → 5E)

- 5A (12 min): None converge — too short for PPP
- 5B (~1.2 h): Only KIRU marginally acceptable
- 5C (~2.6 h): ZIM2 and KIRU converge
- 5D (~4 h): ZIM2 and WUH2 converge well (sU ≈ 0.035 m)
- 5E (~10 h): All stations converge — results match Exp 2C/3A quality

### H. Single vs. Dual Frequency impact (Exp 4A vs 2D)

- L1 only (4A): sU ≈ 0.085–0.115 m — significantly worse
- L1+L2 (2D): sU ≈ 0.016–0.022 m — **5× better vertical accuracy**
- IONEX TEC (4C): sU ≈ 0.074–0.090 m — slight improvement over broadcast

---

## 9. Recommended Stations for Week-Long Analysis (15–21 Jan)

Based on this single-day analysis, recommended stations are:

| Priority | Station  | Reason                                                                             |
| -------- | -------- | ---------------------------------------------------------------------------------- |
| 1st      | **ZIM2** | Best overall precision, fastest convergence, multi-constellation                   |
| 2nd      | **HKWS** | Second best, reliable GPS-only performance                                         |
| 3rd      | **WUH2** | Good performance, good constellation coverage                                      |
| 4th      | **KIRU** | Most satellites tracked, fastest some convergences, slightly lower final precision |

**For the week-long study: use ZIM2 as primary, KIRU for high-satellite diversity comparison.**

---

---

## 10. PRIDE-PPP-AR Results (Static PPP | 2026-01-15)

> **Software:** PRIDE-PPP-AR v3.x | **Mode:** Static batch least-squares | **AR:** WL+NL fixing  
> **Products:** COD0MGXFIN (CODE Multi-GNSS Final) | **GNSS:** GPS + Galileo + BDS (no GLONASS)  
> **Full analysis:** See station_reports/PRIDE_PPP_AR_Results.md

### 10.1 Run Outcomes

| Station  | Float PPP (AR=N) | AR-Fixed (AR=Y) | AR WL Rate | AR NL Rate | Sig0    | Notes                                            |
| -------- | ---------------- | --------------- | ---------- | ---------- | ------- | ------------------------------------------------ |
| **HKWS** | Succeeded        | Succeeded       | 84.9%      | **100.0%** | 1.803 m | Best Sig0; data usage 45.9% (strict editing)     |
| **WUH2** | Succeeded        | Succeeded       | 89.0%      | 97.7%      | 2.999 m | Good AR; noisier BDS residuals                   |
| **KIRU** | Succeeded        | Succeeded       | **98.1%**  | **99.7%**  | 2.649 m | **Best AR rates**; most ambiguities (1040)       |
| **ZIM2** | Succeeded\*      | Succeeded       | 88.1%      | **100.0%** | 2.221 m | Sig0 between HKWS and KIRU; sat_parameters fixed |

\*ZIM2 AR=N output was overwritten when AR=Y started (PrepareTables reinitializes the run dir). AR=Y pos file contains the final fixed solution.

### 10.2 PRIDE Static Position Results (AR=Y solutions)

| Station | X (m)         | Y (m)        | Z (m)        | Nobs   |
| ------- | ------------- | ------------ | ------------ | ------ |
| HKWS    | -2430579.8579 | 5374285.4030 | 2418956.0380 | 48,902 |
| KIRU    | 2251420.4496  | 862817.4632  | 5885476.9326 | 94,234 |
| WUH2    | -2267750.3240 | 5009154.4912 | 3221294.3524 | 85,614 |
| ZIM2    | 4331299.5851  | 567537.7042  | 4633133.9596 | 78,673 |

### 10.3 PRIDE vs RTKLIB: Key Differences

| Aspect                | RTKLIB-EX 2.5.0                       | PRIDE-PPP-AR v3.x                      |
| --------------------- | ------------------------------------- | -------------------------------------- |
| Estimator             | Kalman filter (kinematic)             | Batch least-squares (static)           |
| Output type           | Position time-series (epoch-by-epoch) | Single daily ECEF position             |
| Use case              | Convergence analysis, navigation      | Geodetic accuracy, mm-level static     |
| AR method             | LAMBDA/ILS                            | WL+NL ambiguity fixing                 |
| BDS                   | Included in solution                  | Tracked but not AR-fixed               |
| GLONASS               | Exp 2D/2C (enabled)                   | Disabled (no FDMA bias support)        |
| Best station (RTKLIB) | ZIM2 (fastest convergence, best sU)   | KIRU (best AR rates), HKWS (best Sig0) |

### 10.4 Key PRIDE Findings

1. **KIRU has the best AR performance** (98.1% WL, 99.7% NL) � high-latitude geometry creates long, stable arc segments that are ideal for WL fixing.
2. **HKWS has the best position quality** (Sig0=1.803m) despite the lowest data usage (45.9%) � strict data editing removed all noisy observations, leaving a clean residual set.
3. **C08 anomaly:** BDS satellite C08 (BDS-3 MEO) shows elevated phase residuals (34�35mm) at both KIRU and ZIM2, confirming a satellite-specific orbit/bias issue on this date.
4. **BDS AR not achieved:** No BDS integer ambiguities were fixed despite enabling C06�C61. This reflects current limitations of the COD0MGXFIN OSB product for BDS-3 AR.
5. **Static vs kinematic inversion of rankings:** ZIM2 ranks #1 in RTKLIB (kinematic convergence) but ranks #3 in PRIDE (good AR: 88.1%/100% WL/NL, Sig0=2.221m). KIRU ranks #4 in RTKLIB but shows the best static AR performance (98.1%/99.7%).
