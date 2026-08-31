# Tempest Weekly Scorecard — 2026-08-31

**Generated:** 2026-08-31 (data through 2026-08-30)  
**Dashboard:** https://damngooddawg.github.io/tempest-forecast-verify/dashboard.html

---

## ⚠️ STATION HEALTH — READ FIRST

| Check | Status |
|---|---|
| Hub online | ✅ Yes |
| Station online streak | 52 days |
| Last snapshot | 0 h ago ✅ |
| Battery | 2.66 V ✅ (OK — warn threshold: ≤2.40 V) |
| CoCoRaHS | ✅ OK |
| Rain sensor | ✅ OK |
| Sensor faults | — *(null = not monitored)* |
| Capture days | 88 |
| **Capture misses** | ⚠️ **1 miss** — one day's capture failed |

> **FLAG:** `capture_misses = 1` — one day of data was not captured. Not critical, but worth investigating whether this caused a scoring gap.

---

## 🏁 Headline Verdict

| | |
|---|---|
| **Status** | 🔴 **TEMPEST BEHIND** |
| **Window** | Rolling 90 days (n = 84 scored days, 2026-06-05 → 2026-08-29) |
| **Summary** | Tempest is within 3°F on **74%** of days vs NWS's **80%** — behind the best public forecast. |
| **Best public** | NWS |
| **DM p-value** | 0.0045 (well below 0.05 — the gap is statistically significant) |

Since the **advantage window opened Aug 1** (29 days in), Tempest sits at 76% within-3°F vs NWS's 84% — too few days for a window verdict, but directionally Tempest is trailing.

---

## 📊 Standings — 1-Day Lead (Rolling 90 days, n=84)

| Provider | MAE °F | % within 3°F | Precip CSI |
|---|---|---|---|
| **NWS** 🥇 | **1.92** | **80%** | 0.35 |
| GFS | 2.14 | 75% | 0.33 |
| NBM | 2.18 | 73% | 0.33 |
| **⭐ Tempest** | **2.25** | **74%** | **0.50** |
| ECMWF | 2.66 | 64% | 0.63 |

*Lower MAE is better. Higher % within 3°F and CSI are better. Tempest leads on precip CSI, trails on temperature.*

### 2-Day Lead

| Provider | MAE °F | % within 3°F | Precip CSI |
|---|---|---|---|
| **NWS** 🥇 | **2.01** | **78%** | 0.37 |
| **⭐ Tempest** | **2.31** | **71%** | **0.37** |
| NBM | 2.34 | 69% | 0.36 |
| GFS | 2.67 | 65% | 0.36 |
| ECMWF | 2.70 | 60% | 0.56 |

### 3-Day Lead

| Provider | MAE °F | % within 3°F | Precip CSI |
|---|---|---|---|
| **NWS** 🥇 | **2.13** | **76%** | 0.29 |
| **⭐ Tempest** | **2.39** | **68%** | **0.25** |
| NBM | 2.40 | 68% | 0.21 |
| GFS | 2.99 | 62% | 0.21 |
| ECMWF | 3.10 | 53% | 0.47 |

---

## 📈 Weekly MAE Trend — Tempest vs NWS (Last 8 Weeks)

| Week of | Tempest MAE | NWS MAE | Gap (T − NWS) |
|---|---|---|---|
| 2026-07-06 | 2.22 | 2.28 | **−0.06** ✅ Tempest ahead |
| 2026-07-13 | 2.34 | 1.59 | +0.75 |
| 2026-07-20 | 2.82 | 2.16 | +0.66 |
| 2026-07-27 | 2.34 | 2.04 | +0.30 |
| 2026-08-03 | 3.07 | 1.77 | +1.30 ❌ bad week |
| 2026-08-10 | **1.29** | 1.64 | **−0.35** ✅ Tempest ahead |
| 2026-08-17 | 1.77 | 1.69 | +0.08 |
| 2026-08-24 | 2.47 | **1.38** | **+1.09** ❌ last week bad |

**Assessment:** Tempest had its best week on 8/10 (MAE 1.29 — beating NWS!) but fell back hard the week of 8/24 (MAE 2.47 vs NWS 1.38). The gap is **not consistently closing**. The busts on 8/28–8/29 (see below) dragged down the latest week.

---

## 💥 Biggest Recent Busts

| Date | Source | Variable | Forecast | Actual | Error |
|---|---|---|---|---|---|
| 2026-08-29 | **Tempest** | High temp | 83°F | 90°F | **−7°F** |
| 2026-08-28 | **Tempest** | High temp | 85°F | 91°F | **−6°F** |
| 2026-08-29 | NBM | High temp | 84°F | 90°F | −6°F |

Two consecutive days where Tempest (and most models) significantly under-forecast the high by 6–7°F. This heat event drove the poor week of 8/24.

---

## 🌧️ Rain Totals — Tempest vs CoCoRaHS (Recent 30 Days)

| Date | Tempest Raw | CoCoRaHS | Flag |
|---|---|---|---|
| 2026-08-10 | 0.641" | 0.28" | *(large but no flag)* |
| 2026-08-11 | 0.001" | 0.22" | ⚠️ **disagree** — Tempest nearly missed 0.22" rain event |
| 2026-08-14 | 0.021" | 0.00" | ⚠️ **disagree** — Tempest reported trace, CoCoRaHS dry |
| 2026-08-15 | 0.142" | 0.34" | *(no flag)* |
| 2026-08-17 | 0.384" | 0.43" | *(close, no flag)* |
| 2026-08-20 | 0.000" | 0.14" | ⚠️ **disagree** — Tempest missed 0.14" event |
| 2026-08-27 | 0.022" | 0.10" | *(no flag)* |

**3 disagree flags** in the recent period. Most notable: Tempest reported 0.001" on Aug 11 while CoCoRaHS logged 0.22". *(Note: data has no separate RainCheck field — corrected = raw throughout.)*

---

## 📅 Guarantee Timeline

| Milestone | Date | Status |
|---|---|---|
| Advantage window opens | 2026-08-01 | ✅ Active (29 days in) |
| 5-month mark | 2026-10-31 | 61 days away |
| Claim deadline | 2027-01-25 | 147 days away |

**Advantage window:** 29 days scored so far (need ~30 for a first directional read, 90 for definitive). With 29 days in-window, Tempest MAE = 2.26 vs NWS = 1.67; 76% vs 84% within-3°F. Tempest would need a sustained turnaround over the coming months to achieve parity.

---

## Notes

- **Tempest wins on precipitation CSI** (0.50 vs NWS 0.35 at 1-day lead) — meaningful advantage for rain forecasting.
- **Tempest Brier score** (probability calibration): 0.207 vs NWS 0.249 — Tempest's rainfall probability forecasts are better calibrated.
- Temperature accuracy (the guarantee metric) is where Tempest trails.
- Weekly n is small (≈7 days); significance requires cumulative n ≥ 30. The 84-day all-time window has p = 0.0045 — the gap is real and growing more statistically significant each week.
