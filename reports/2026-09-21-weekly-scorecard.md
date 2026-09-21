# Tempest Better Forecast Guarantee — Weekly Scorecard
**Generated:** 2026-09-21 | **Data through:** 2026-09-20

---

## ⚠️ STATION HEALTH FLAG
**Capture miss detected:** `capture_misses = 1` — one day's irreplaceable Tempest snapshot was not captured in 109 capture days. All other health indicators are nominal. Monitor for recurrence.

---

## Headline Verdict

> **🔴 TEMPEST BEHIND**
> Tempest is within 3°F on **74%** of days vs NWS's **81%** — behind the best public forecast over the rolling 90-day window.
> (n=88 days · best public: NWS · DM p=0.001 — highly statistically significant)

The verdict has been TEMPEST BEHIND every day since tracking crossed the statistical threshold (Aug 8). The 7-percentage-point gap on within-3°F is consistent and well above noise. Tempest also trails NWS on raw MAE: 2.23°F vs 1.87°F (rolling 90 days). Since the Aug 1 advantage window opened (n=50 days), Tempest is at 76% vs NWS 85% within 3°F (p=0.0008 — even more significant over the claim window). Tempest does beat NWS on precip detection (CSI 0.50 vs 0.36) and rain probability calibration (Brier 0.198 vs 0.227), but temperature is the primary guarantee metric.

---

## 📊 Standings — 1-Day Lead

### Public Providers (All-Time, n≈104–105 days)

| Provider | MAE (°F) ↓ | % Within 3°F ↑ | Precip CSI ↑ |
|---|---|---|---|
| **NWS** 🥇 | **1.88** | **81%** | 0.36 |
| GFS | 2.09 | 78% | 0.31 |
| NBM | 2.19 | 72% | 0.31 |
| **★ Tempest** | **2.21** | **74%** | **0.50** |
| ECMWF | 2.62 | 65% | 0.63 |

*House rows (not eligible as guarantee rivals):* Blend 1.89°F / 81% / CSI 0.60 (n=105); Dawg 1.15°F / 100% / CSI 0.50 (n=5, early sample).

*Tempest beats all public providers on precip detection (CSI 0.50) but ranks 4th of 5 on temperature.*

### 2-Day Lead (n≈103–104 days)

| Provider | MAE (°F) | % Within 3°F | Precip CSI |
|---|---|---|---|
| NWS 🥇 | 2.00 | 78% | 0.39 |
| ★ Tempest | 2.29 | 71% | 0.41 |
| NBM | 2.31 | 70% | 0.38 |
| GFS | 2.51 | 70% | 0.38 |
| ECMWF | 2.66 | 62% | 0.57 |

### 3-Day Lead (n≈102–103 days)

| Provider | MAE (°F) | % Within 3°F | Precip CSI |
|---|---|---|---|
| NWS 🥇 | 2.13 | 75% | 0.27 |
| ★ Tempest | 2.45 | 66% | 0.26 |
| NBM | 2.44 | 66% | 0.23 |
| GFS | 2.82 | 65% | 0.23 |
| ECMWF | 3.00 | 55% | 0.47 |

---

## 📈 Weekly MAE Trend — Tempest vs NWS (1-Day Lead)

| Week of | Tempest MAE | NWS MAE | Gap (T−NWS) |
|---|---|---|---|
| 2026-08-24 | 2.54 | 1.61 | +0.93 |
| 2026-08-31 | 2.74 | 2.22 | +0.52 |
| 2026-09-07 | 1.79 | 1.62 | +0.17 |
| **2026-09-14** | **1.30** | **1.12** | **+0.18** ← most recent |

**Trend:** Both Tempest and NWS improved sharply over the last two weeks as summer heat eased. The weekly gap is essentially flat at +0.17–0.18°F — the narrowest Tempest-behind margin since launch. However, the cumulative rolling-90 gap (MAE 2.23 vs 1.87) has barely moved: rolling verdict history shows Tempest MAE edging from 2.23→2.21°F over the past week while NWS held at 1.87°F. The gap is not closing at the cumulative level.

---

## 💥 Biggest Recent Busts (last 7 days)

| Date | Provider | Variable | Forecast | Actual | Error |
|---|---|---|---|---|---|
| 2026-09-13 | ECMWF | High temp | 87°F | 92°F | −5°F |
| 2026-09-14 | ECMWF | High temp | 92°F | 95°F | −3°F |
| 2026-09-15 | GFS | High temp | 91°F | 88°F | +3°F |

All three busts are on the ECMWF and GFS models. ECMWF missed two consecutive days cold on the high temperature (Sep 13–14). No Tempest busts appear in the top list this week. All-time high-temp bias: Tempest −2.0°F, NBM −2.2°F (both running a bit cold overall — consistent with broader model behavior in the Southeast).

---

## 🌧️ Rain Totals (recent rain days)

| Date | Tempest Raw | Tempest RainCheck | CoCoRaHS Gauge | Flag |
|---|---|---|---|---|
| 2026-09-11 | 0.999 in | 0.999 in | 0.30 in | — (3× overcount, watch) |
| 2026-09-12 | 0.309 in | 0.309 in | 0.32 in | ✓ |
| 2026-09-18 | 0.000 in | 0.000 in | **0.22 in** | ⚠️ **DISAGREE** |
| 2026-09-19 | 0.253 in | 0.253 in | 0.05 in | — |

⚠️ **Sep 18 rain miss:** Tempest recorded 0 in while CoCoRaHS measured 0.22 in — a clear miss flagged as "disagree." This is the second notable discrepancy in 10 days (after the Sep 11 3× overcount). The Sep 11 overcount and Sep 18 miss go in opposite directions; rain sensor behavior worth monitoring. Sep 12 and Sep 19 cross-checks were closer. CoCoRaHS has no report on most days (null = no report filed, not zero rain).

---

## 🔋 Station Health

| Metric | Value | Status |
|---|---|---|
| Station online streak | 73 days | ✅ |
| Hub online | true | ✅ |
| Last snapshot | 0 hours ago | ✅ |
| Battery voltage | 2.65 V | ✅ (nominal; warn: ≤2.40 V · alert: ≤2.355 V) |
| Battery warn flag | false | ✅ |
| CoCoRaHS ok | true | ✅ |
| Rain sensor ok | true | ✅ |
| Capture days | 109 | — |
| **Capture misses** | **1** | **⚠️ FLAG** |
| Sensor faults | null | (not monitored — not "healthy") |
| RSSI | null | (not monitored) |

**Health check — all anchor variables OK:** Temperature, humidity, wind, and pressure are all within their normal bands vs KWDR (Winder), KAHN (Athens), and WATUGA (UGA Watkinsville). Overall health: OK. 0 active watches, 0 confirmed faults (112 days monitored).

**High-temp radiation check:** Daily highs track the aspirated airport highs about the same on calm-sunny and windy days (split Δ +0.7°F, threshold 1.0°F) — no radiation-shield signature detected.

**⚠️ FLAG:** `capture_misses = 1` — one day's irreplaceable Tempest snapshot was missed in 109 capture days. No new misses this week; same flag as prior week. Monitor whether the daily cron workflow remains active.

---

## 📅 Guarantee Timeline

| Milestone | Date | Status |
|---|---|---|
| Guarantee window opens | 2026-08-01 | ✅ Active (51 days in) |
| 5-month mark | 2026-10-31 | 40 days away |
| Claim deadline | 2027-01-25 | — |

**Current status:** 51 days since the Aug 1 window opened. The rolling-90 verdict (n=88, p=0.001) has been TEMPEST BEHIND every day since the statistical threshold was crossed Aug 8. At the current trajectory — NWS leading by 7 pp on within-3°F — Tempest would need a substantial and sustained improvement over the next 6 weeks to change the verdict before the Oct 31 five-month mark. The advantage window standings (n=50 days) are even worse: Tempest 76% vs NWS 85% (p=0.0008).

---

*Dashboard: https://damngooddawg.github.io/tempest-forecast-verify/dashboard.html*
