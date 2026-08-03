# Tempest Weekly Scorecard — 2026-08-03

> Generated: 2026-08-03 | Data through: 2026-08-02 | n = 56 scored days

---

## Headline Verdict: TIED

**Tempest is within 3°F on 72% of days vs NWS's 79% — statistically tied with the best public forecast so far.**

- n_days: **56** (≥30 for first-verdict threshold, ≥90 for definitive)
- Best public provider: **NWS**
- Diebold-Mariano p-value: **0.09** (not significant at α=0.05; but trending toward a readable difference)
- Interpretation: 56 days is enough for an early read. NWS leads on temperature accuracy; Tempest leads on precipitation. The gap has narrowed this week (p moved from 0.125 → 0.09). Still needs ~34 more days for a statistically definitive result.
- **The guarantee evaluation window is now OPEN** (opened 2026-08-01). Every day from here forward counts directly toward the claim judgment.

---

## STATION HEALTH — OK

| Metric | Value | Status |
|---|---|---|
| Last snapshot (hours ago) | 0 | ✅ Current |
| Capture days total | 60 | — |
| **Capture misses** | **1** | ⚠️ **FLAG: 1 day of Tempest snapshot data is unrecoverable** |
| Station online streak | 24 days | ✅ |
| Hub online | true | ✅ |
| Battery (volts) | 2.65 V | ✅ Healthy (>2.40 V) |
| Battery warning | false | ✅ |
| CoCoRaHS OK | true | ✅ |
| Sensor faults | null | — not monitored (API returns 401 for personal tokens) |
| RSSI / Hub RSSI | null | — not captured |
| Anchor health (temp, RH, wind, pressure, rain) | All OK | ✅ |

> **⚠️ capture_misses = 1** — one day's Tempest forecast snapshot was lost before it could be captured and cannot be recovered from any public archive. This count is unchanged from last week; the gap is historical, not new. Review `.github/workflows/capture.yml` logs to confirm the root cause if not already identified.

> `sensor_faults: null` means fault monitoring is not available (Tempest diagnostics endpoint returns 401 for personal tokens), not that the sensor is confirmed healthy.

> `generated_at` is 2026-08-02T11:37:58Z — approximately **24 hours old**, well within the 48-hour staleness threshold. ✅

---

## 1-Day Lead Standings (n = 56 days)

| Provider | MAE (°F) | % within 3°F | Precip CSI |
|---|---|---|---|
| **NWS** | **2.03** | **79%** | 0.37 |
| NBM | 2.11 | 73% | 0.35 |
| GFS | 2.22 | 73% | 0.35 |
| **★ Tempest** | **2.27** | **72%** | **0.59** |
| ECMWF | 2.57 | 66% | 0.69 |

**Notes:**
- Tempest lags NWS by 0.24°F MAE and 7 percentage points on temperature at 1-day lead.
- Tempest's precipitation CSI (0.59) is nearly **60% better** than NWS (0.37) and NBM/GFS (0.35) — a major strength.
- ECMWF leads on precip CSI (0.69) but has the worst temperature accuracy among all providers.

### 2-Day Lead

| Provider | MAE (°F) | % within 3°F | Precip CSI |
|---|---|---|---|
| **NWS** | **2.11** | **76%** | 0.40 |
| NBM | 2.31 | 68% | 0.40 |
| **★ Tempest** | **2.33** | **70%** | **0.37** |
| GFS | 2.54 | 66% | 0.40 |
| ECMWF | 2.56 | 62% | 0.57 |

### 3-Day Lead

| Provider | MAE (°F) | % within 3°F | Precip CSI |
|---|---|---|---|
| **NWS** | **2.21** | **77%** | 0.38 |
| **★ Tempest** | **2.34** | **70%** | **0.30** |
| NBM | 2.35 | 69% | 0.28 |
| ECMWF | 2.82 | 56% | 0.46 |
| GFS | 2.95 | 63% | 0.28 |

### Blended Lead (1–3 day average)

| Provider | MAE (°F) | % within 3°F | Precip CSI |
|---|---|---|---|
| **NWS** | **2.12** | **77%** | 0.38 |
| NBM | 2.26 | 70% | 0.34 |
| **★ Tempest** | **2.32** | **71%** | **0.42** |
| GFS | 2.56 | 68% | 0.34 |
| ECMWF | 2.65 | 62% | 0.57 |

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
| 2026-07-20 | 2.82 | 2.16 | +0.66 |
| **2026-07-27** | **2.02** | **1.87** | **+0.15** ← Gap narrowing |

**Assessment:** The last week of July (week of Jul 27) saw a notable improvement — the gap narrowed sharply from +0.66 to +0.15, with both providers performing well in the mid-2°F range. Tempest led NWS in 3 of 9 tracked weeks. The trend is heading in the right direction just as the guarantee window opens. Summer convective season remains the challenge.

---

## Biggest Busts (Current Data)

| Date | Provider | Variable | Forecast | Actual | Error |
|---|---|---|---|---|---|
| 2026-07-26 | Tempest | High temp | 87°F | 92°F | **−5°F** |
| 2026-08-01 | Tempest | High temp | 83°F | 88°F | **−5°F** |
| 2026-07-26 | ECMWF | High temp | 87°F | 92°F | **−5°F** |

> Tempest and ECMWF both under-forecast the July 26 heat (87°F predicted, 92°F actual). Tempest also under-forecast August 1 (83°F predicted, 88°F actual). Both are 5°F cold-biased misses on hot summer days — consistent with a pattern of underestimating peak heat during the current stretch.

---

## Rain Totals (Tempest vs CoCoRaHS)

Recent rainy-day comparisons (raw = corrected for this station):

| Date | Tempest (in) | CoCoRaHS (in) | Flag |
|---|---|---|---|
| 2026-07-12 | 1.112 | 0.800 | ✅ |
| 2026-07-13 | 1.024 | 1.570 | ✅ |
| 2026-07-14 | 0.164 | 0.340 | ✅ |
| 2026-07-18 | 0.510 | 1.460 | ✅ |
| 2026-07-23 | 0.175 | 0.000 | ⚠️ disagree |
| 2026-07-24 | 0.513 | 0.330 | ✅ |
| 2026-07-28 | 0.847 | 0.720 | ✅ |

**1 active disagree flag** in recent data:
- **Jul 23**: Tempest measured 0.175"; CoCoRaHS reported 0.000". Possible highly localized convective shower — rain that fell at the station but not at the CoCoRaHS gauge ~6+ miles away.

Overall precipitation agreement is good — 6 of 7 compared days within acceptable range. The July 28 event (0.847" vs 0.720") was the largest recent rain event and shows good agreement.

---

## Guarantee Timeline

| Milestone | Date | Status |
|---|---|---|
| **Guarantee window OPENED** | **2026-08-01** | **✅ NOW OPEN — 2 days in** |
| 5-month evaluation end | 2026-10-31 | 89 days remaining |
| Claim deadline | 2027-01-25 | Future |

> **The guarantee window is open.** Scores from 2026-08-01 onward now count directly toward the claim. Current status: TIED at 56 days (p=0.09), with NWS leading on temperature and Tempest leading on precipitation CSI. For a successful claim, Tempest needs to demonstrate a statistically significant advantage (~90 total days, current gap needs to shift or widen in Tempest's favor). With 89 days remaining in the 5-month window, there is ample time to accumulate that evidence — but the current temperature gap needs to close.

---

## Summary

**TIED** at 56 days (p=0.09). NWS leads on temperature (MAE 2.03 vs 2.27 °F; 79% vs 72% within 3°F). Tempest leads strongly on precipitation CSI (0.59 vs 0.37). The guarantee window just opened August 1 — every day now counts. Good news: last week's MAE gap narrowed sharply (+0.66 → +0.15). Bad news: two 5°F cold busts on hot days (Jul 26, Aug 1) dragged the temperature score. Station health is fully OK — hub online, battery healthy, 24-day streak, no anchor flags. One historical capture miss remains unresolved.

*Dashboard: https://damngooddawg.github.io/tempest-forecast-verify/dashboard.html*
