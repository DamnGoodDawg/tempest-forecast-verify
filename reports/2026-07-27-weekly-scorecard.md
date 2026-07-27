# Tempest Weekly Scorecard — 2026-07-27

> Generated: 2026-07-27 | Data through: 2026-07-26 | n = 49 scored days

---

## Headline Verdict: TIED

**Tempest is within 3°F on 71% of days vs NWS's 77% — statistically tied with the best public forecast.**

- n_days: **49** (≥30 for first-verdict threshold, ≥90 for definitive)
- Best public provider: **NWS**
- Diebold-Mariano p-value: **0.125** (not significant; >0.05 means no reliable difference yet)
- Interpretation: With 49 days, we have enough for a preliminary read but not a statistically conclusive result. Gap needs to widen or more data is needed.

---

## ⚠️ STATION HEALTH — 1 CAPTURE MISS (ACTION NEEDED)

| Metric | Value | Status |
|---|---|---|
| Last snapshot (hours ago) | 0 | ✅ Current |
| Capture days total | 53 | — |
| **Capture misses** | **1** | ⚠️ **FLAG: AT LEAST ONE DAY OF DATA LOST** |
| Station online streak | 17 days | ✅ |
| Hub online | true | ✅ |
| Battery (volts) | 2.66 V | ✅ Healthy (>2.40 V) |
| Battery warning | false | ✅ |
| CoCoRaHS OK | true | ✅ |
| Sensor faults | null | — not monitored (API returns 401 for personal tokens) |
| RSSI / Hub RSSI | null | — not captured |

> **⚠️ capture_misses = 1** — at least one day's Tempest forecast snapshot was lost and cannot be recovered from any public archive. This may affect score completeness. Review `.github/workflows/capture.yml` logs to identify the missed date and root cause.

---

## 1-Day Lead Standings (n = 49 days)

| Provider | MAE (°F) | % within 3°F | Precip CSI |
|---|---|---|---|
| **NWS** | **2.06** | **77%** | 0.37 |
| NBM | 2.15 | 72% | 0.36 |
| GFS | 2.28 | 72% | 0.36 |
| **★ Tempest** | **2.30** | **71%** | **0.62** |
| ECMWF | 2.55 | 66% | 0.74 |

**Notes:**
- Tempest lags NWS by 0.24°F MAE and 6 percentage points on temperature.
- Tempest's precipitation CSI (0.62) is dramatically better than NWS (0.37) and NBM/GFS (0.36) at 1-day lead — a standout strength.
- ECMWF leads precip CSI at 0.74 but lags on temperature.

### 2-Day Lead

| Provider | MAE (°F) | % within 3°F | Precip CSI |
|---|---|---|---|
| NWS | 2.14 | 76% | 0.41 |
| **★ Tempest** | **2.39** | **69%** | **0.37** |
| NBM | 2.39 | 66% | 0.41 |
| GFS | 2.50 | 70% | 0.41 |
| ECMWF | 2.51 | 62% | 0.59 |

### 3-Day Lead

| Provider | MAE (°F) | % within 3°F | Precip CSI |
|---|---|---|---|
| NWS | 2.28 | 77% | 0.39 |
| **★ Tempest** | **2.41** | **68%** | **0.30** |
| NBM | 2.44 | 66% | 0.31 |
| GFS | 2.88 | 67% | 0.31 |
| ECMWF | 2.78 | 56% | 0.50 |

---

## Weekly MAE Trend (Tempest vs NWS, 1-day lead)

| Week of | Tempest MAE | NWS MAE | Gap (T − NWS) |
|---|---|---|---|
| 2026-06-01 | 1.53 | 1.47 | +0.06 |
| 2026-06-08 | 2.32 | 1.84 | +0.48 |
| 2026-06-15 | 2.12 | 2.25 | **−0.13** ← Tempest ahead |
| 2026-06-22 | 2.78 | 2.56 | +0.22 |
| 2026-06-29 | 1.82 | 1.99 | **−0.17** ← Tempest ahead |
| 2026-07-06 | 2.22 | 2.28 | **−0.06** ← Tempest ahead |
| 2026-07-13 | 2.34 | 1.59 | +0.75 |
| **2026-07-20** | **2.87** | **2.27** | **+0.60** ← Gap widening |

**Assessment:** Tempest outperformed NWS in 3 of 8 weeks. The last two weeks show a widening gap in NWS's favor (+0.75 and +0.60). The gap is not closing — summer convective weather may be challenging Tempest's local model. Watch the next 2–3 weeks carefully as the guarantee window opens.

---

## Biggest Busts (Top Misses in Recent Data)

| Date | Provider | Variable | Forecast | Actual | Error |
|---|---|---|---|---|---|
| 2026-07-24 | NWS | High temp | 87°F | 76°F | **−11°F** |
| 2026-07-24 | GFS | High temp | 84°F | 76°F | −8°F |
| 2026-07-24 | NBM | High temp | 84°F | 76°F | −8°F |

> **Tempest is not in the busts list** — Tempest correctly anticipated the cooler high on July 24, a significant win. NWS, GFS, and NBM all badly over-forecast by 8–11°F on what was likely a convective/rainfall cooling event.

---

## Rain Totals (Tempest vs CoCoRaHS)

Recent rainy-day comparisons (raw = corrected for this station):

| Date | Tempest (in) | CoCoRaHS (in) | Flag |
|---|---|---|---|
| 2026-07-06 | 0.000 | 0.400 | ⚠️ disagree |
| 2026-07-11 | 0.251 | 0.310 | ✅ |
| 2026-07-12 | 1.112 | 0.800 | ✅ |
| 2026-07-13 | 1.024 | 1.570 | ✅ |
| 2026-07-14 | 0.164 | 0.340 | ✅ |
| 2026-07-18 | 0.510 | 1.460 | ✅ |
| 2026-07-23 | 0.175 | 0.000 | ⚠️ disagree |
| 2026-07-24 | 0.513 | 0.330 | ✅ |

**2 disagree flags** in recent data:
- **Jul 6**: Tempest measured nothing; CoCoRaHS recorded 0.40". Tempest likely missed a rain event. CoCoRaHS gauges are point-specific so some spatial variability is expected, but 0.40" is a meaningful amount.
- **Jul 23**: Tempest measured 0.175"; CoCoRaHS reported 0.000". Possible that rain fell near the station but not at the CoCoRaHS gauge location.

Overall precipitation agreement is generally good — 6 of 8 compared days within acceptable range.

---

## Guarantee Timeline

| Milestone | Date | Status |
|---|---|---|
| **Guarantee window OPENS** | **2026-08-01** | **⏰ 5 DAYS AWAY** |
| 5-month evaluation end | 2026-10-31 | Upcoming |
| Claim deadline | 2027-01-25 | Future |

> The formal guarantee evaluation window opens in **5 days**. Current standings (TIED, p=0.125) mean Tempest would need to show a consistent advantage over the remainder of the period. Scores from the pre-window period count toward the dataset but the guarantee judgment begins August 1.

---

## Summary

**TIED** at 49 days (p=0.125). Tempest's temperature accuracy slightly lags NWS (MAE 2.30 vs 2.06, 71% vs 77% within 3°F) but its precipitation CSI at 1-day lead (0.62) is nearly twice NWS's (0.37). The July 24 event showed Tempest handled a difficult cooling event better than NWS/GFS/NBM. Weekly trend the last 2 weeks is going in the wrong direction — watch carefully as the guarantee window opens August 1. One capture miss is logged and should be investigated.

*Dashboard: https://damngooddawg.github.io/tempest-forecast-verify/dashboard.html*
