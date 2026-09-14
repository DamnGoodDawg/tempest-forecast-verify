# Tempest Better Forecast Guarantee — Weekly Scorecard
**Generated:** 2026-09-14 | **Data through:** 2026-09-13

---

## ⚠️ STATION HEALTH ALERT
**Capture miss detected:** `capture_misses = 1` — one day of data was not captured. This is a minor flag; all other health indicators are nominal.

---

## Headline Verdict

> **🔴 TEMPEST BEHIND**
> Tempest is within 3°F on **72%** of days vs NWS's **80%** — behind the best public forecast over the last 90 days.
> (n=88 days · best public: NWS · DM p=0.003 — statistically significant)

The gap is persistent and has been the verdict every day since tracking began. Tempest needs to close an 8-point gap on the "within-3°F" metric vs NWS to flip this verdict.

---

## 📊 Standings — 1-Day Lead (All-Time, n=98 days)

| Provider | MAE (°F) ↓ | % Within 3°F ↑ | Precip CSI ↑ |
|---|---|---|---|
| **NWS** 🥇 | **1.92** | **80%** | 0.36 |
| GFS | 2.12 | 77% | 0.31 |
| NBM | 2.23 | 71% | 0.31 |
| **★ Tempest** | **2.26** | **72%** | **0.50** |
| ECMWF | 2.63 | 65% | 0.64 |

*Tempest is 4th on temperature (MAE/within-3°F) but wins vs NWS on precip detection (CSI 0.50 vs 0.36) and rain probability calibration (Brier 0.193 vs 0.222).*

### 2-Day Lead

| Provider | MAE (°F) | % Within 3°F | Precip CSI |
|---|---|---|---|
| NWS 🥇 | 2.03 | 77% | 0.38 |
| **★ Tempest** | **2.33** | **70%** | **0.41** |
| NBM | 2.35 | 69% | 0.37 |
| GFS | 2.57 | 68% | 0.37 |
| ECMWF | 2.68 | 61% | 0.57 |

### 3-Day Lead

| Provider | MAE (°F) | % Within 3°F | Precip CSI |
|---|---|---|---|
| NWS 🥇 | 2.14 | 75% | 0.28 |
| **★ Tempest** | **2.46** | **67%** | **0.26** |
| NBM | 2.46 | 66% | 0.23 |
| GFS | 2.86 | 65% | 0.23 |
| ECMWF | 3.04 | 54% | 0.47 |

---

## 📈 Weekly MAE Trend — Tempest vs NWS (1-Day Lead)

| Week of | Tempest MAE | NWS MAE | Gap (T−NWS) |
|---|---|---|---|
| 2026-08-03 | 3.07 | 1.77 | +1.30 |
| 2026-08-10 | 1.29 | 1.64 | **−0.35** ← Tempest led |
| 2026-08-17 | 1.77 | 1.69 | +0.08 |
| 2026-08-24 | 2.54 | 1.61 | +0.93 |
| 2026-08-31 | 2.74 | 2.22 | +0.52 |
| **2026-09-07** | **1.75** | **1.47** | **+0.28** ← most recent |

**Trend:** The most recent week shows the gap narrowing to +0.28°F — the smallest Tempest-behind gap since mid-August. One week of stronger NWS performance (Aug 10 week) shows Tempest can lead, but the cumulative record favors NWS. Closing but not yet converging.

---

## 💥 Biggest Recent Busts (last 7 days)

| Date | Provider | Variable | Forecast | Actual | Error |
|---|---|---|---|---|---|
| 2026-09-12 | ECMWF | High temp | 78°F | 84°F | −6°F |
| 2026-09-08 | **Tempest** | High temp | 85°F | 90°F | −5°F |
| 2026-09-06 | NBM | High temp | 93°F | 98°F | −5°F |

All three busts were cold-side misses on high temperature. Tempest had the Sep 8 bust (−5°F), consistent with the broader pattern of high-temp underforecasting (all-time bias: Tempest −2.05°F, NBM −2.19°F).

---

## 🌧️ Rain Totals (recent rain days)

| Date | Tempest Raw | Tempest RainCheck | CoCoRaHS Gauge |
|---|---|---|---|
| 2026-08-27 | 0.022 in | 0.022 in | 0.10 in |
| 2026-09-07 | 0.011 in | 0.011 in | — |
| 2026-09-11 | **0.999 in** | **0.999 in** | **0.30 in** ⚠️ |
| 2026-09-12 | 0.309 in | 0.309 in | 0.32 in ✓ |

⚠️ **Sep 11 discrepancy:** Tempest reported 0.999 in vs CoCoRaHS 0.30 in — a 3× overcount. RainCheck did not correct this event. Sep 12 was accurate. Worth monitoring for sensor fouling or splash contamination.

---

## 🔋 Station Health

| Metric | Value | Status |
|---|---|---|
| Station online streak | 66 days | ✅ |
| Hub online | true | ✅ |
| Last snapshot | 0 hours ago | ✅ |
| Battery voltage | 2.66 V | ✅ (nominal; warn threshold: ≤2.40 V) |
| Battery warn flag | false | ✅ |
| CoCoRaHS ok | true | ✅ |
| Rain sensor ok | true | ✅ |
| Capture days | 102 | — |
| **Capture misses** | **1** | **⚠️ FLAG** |
| Sensor faults | null | (not monitored — not 'healthy') |
| RSSI | null | (not monitored) |

**⚠️ FLAG:** `capture_misses = 1` — one data capture was missed in 102 days. Minor, but track whether this recurs.

---

## 📅 Guarantee Timeline

| Milestone | Date | Status |
|---|---|---|
| Guarantee window opens | 2026-08-01 | ✅ Active (44 days in) |
| 5-month mark | 2026-10-31 | 47 days away |
| Claim deadline | 2027-01-25 | — |

**Current verdict window:** n=88 rolling days (need 90 for definitive; essentially at threshold). The advantage window (since Aug 1) shows n=43 days with Tempest at 72% vs NWS 82% within 3°F (p=0.0009 — highly significant gap). At this trajectory Tempest would need a sustained accuracy improvement over the next 6+ weeks to change the verdict before Oct 31.

---

*Dashboard: https://damngooddawg.github.io/tempest-forecast-verify/dashboard.html*
