# Tempest Better Forecast Guarantee — Weekly Scorecard
**Generated:** 2026-10-05 | **Data through:** 2026-10-03 (scores.json built 2026-10-04 15:50 UTC)

---

## ⚠️ STATION HEALTH FLAG
**`capture_misses = 1`**: this is still the known **2026-07-09** gap (123 capture days, 1 miss). **There were no new misses this week.** Every daily capture from Sep 28 to Oct 4 landed. Everything else is nominal: the hub is online, the battery reads 2.65 V and the station has been online for 87 straight days. Today's capture hadn't landed when this ran at 12:25 UTC. The daily job normally commits between ~15:00 and 15:50 UTC.

---

## Headline Verdict

> **🔴 TEMPEST BEHIND**
> Tempest was within 3°F on **74%** of days, vs **85%** for NWS. It trails the best public forecast over the last 90 days.
> (n = 88 days · best public: NWS · DM p = 0.0002, significant)

**The gap widened this week.** Rolling-90 MAE is Tempest 2.21°F vs NWS 1.79°F, a 0.42°F gap. Last week it was 2.18 vs 1.83 (0.35°F). **Since Aug 1 (advantage window, n = 64):** Tempest was within 3°F on 75% of days vs 85% for NWS (MAE 2.16 vs 1.72, p = 0.0003). Tempest still beats NWS on precip detection (CSI 0.44 vs 0.42) and PoP calibration (Brier 0.162 vs 0.176). The guarantee is driven by temperature, though.

---

## 📊 Standings — 1-Day Lead (all-time, n ≈ 118–119 days)

| Provider | MAE (°F) ↓ | % Within 3°F ↑ | Precip CSI ↑ |
|---|---|---|---|
| **NWS** 🥇 | **1.87** | **82%** | 0.38 |
| GFS | 2.10 | 77% | 0.30 |
| NBM | 2.16 | 73% | 0.30 |
| **★ Tempest** | **2.20** | **74%** | **0.51** |
| ECMWF | 2.62 | 65% | 0.63 |

*House rows (not guarantee rivals):* Blend 1.88°F / 82% / CSI 0.60 (n = 119); Dawg 1.59°F / 89% / CSI 0.80 (n = 18, early sample).

Among the 5 public providers, Tempest ranks 4th on temperature and 2nd on precip CSI (only ECMWF is ahead).

---

## 📈 Weekly MAE Trend — 1-Day Lead

| Week of | Tempest | NWS | Best public that week | Gap (T − NWS) |
|---|---|---|---|---|
| 2026-08-31 | 2.74 | 2.22 | GFS 2.06 | +0.52 |
| 2026-09-07 | 1.79 | 1.62 | NWS 1.62 | +0.17 |
| 2026-09-14 | 1.49 | 1.26 | NWS 1.26 | +0.23 |
| 2026-09-21 | 2.29 | 2.15 | NBM 2.07 | +0.14 (revised) |
| **2026-09-28** | **1.93** | **1.37** | **NWS 1.37** | **+0.56** ← latest |

**Closing? No.** Last week's report showed Tempest narrowly beating NWS in the week of Sep 21 (2.11 vs 2.14). With the full week in, that reversed: 2.29 vs 2.15, so Tempest lost. This week Tempest lost by 0.56°F and also trailed NBM (1.46) and GFS (1.52). Tempest has not beaten NWS in a full week since the week of Aug 10. Tempest's cold bias came back to −1.63°F this week, from −0.61°F the week before. Weekly numbers are small-n and descriptive.

---

## 💥 Biggest Busts (last 7 days)

| Date | Provider | Var | Forecast | Actual | Error |
|---|---|---|---|---|---|
| 2026-10-03 | ECMWF | High | 79°F | 85°F | −6°F |
| 2026-10-03 | NBM | High | 81°F | 85°F | −4°F |
| 2026-09-29 | ECMWF | High | 83°F | 86°F | −3°F |

Tempest is not on this week's bust list. Every bust was a warm afternoon that the models forecast too cool. That fits the cold bias seen across the board.

---

## 🌧️ Rain Totals (recent rain days)

| Date | Tempest Raw | Tempest RainCheck | CoCoRaHS Gauge | Flag |
|---|---|---|---|---|
| 2026-09-18 | 0.000 in | 0.000 in | 0.22 in | ⚠️ DISAGREE |
| 2026-09-19 | 0.253 in | 0.253 in | 0.05 in | — |
| 2026-09-20 | 0.493 in | 0.493 in | 0.42 in | ✓ close |
| 2026-09-22 | 0.068 in | 0.068 in | — (no report) | — |
| 2026-09-30 | 0.000 in | 0.000 in | 0.00 in | ✓ |
| 2026-10-03 | 0.002 in | 0.002 in | 0.07 in | ⚠️ DISAGREE |

The week of Sep 28–Oct 3 was essentially dry. On Oct 3 the gauge caught 0.07 in while Tempest logged only 0.002 in. That is the second time in about two weeks that Tempest read near-zero against a measurable gauge total (Sep 18 was the first). Light-rain under-detection by the haptic sensor is worth watching. RainCheck made no corrections: raw equals corrected on every day. A CoCoRaHS null means no report was filed, not that no rain fell.

---

## 🔋 STATION HEALTH

| Metric | Value | Status |
|---|---|---|
| Capture days | 123 | — |
| **Capture misses** | **1** (2026-07-09) | **⚠️ FLAG: known and unchanged, no new misses** |
| Last snapshot | 0 h ago at build (2026-10-04 15:50 UTC) | ✅ |
| Station online streak | 87 days | ✅ (was 80 last week) |
| Hub online | true | ✅ |
| Battery | 2.65 V (battery_warn = false) | ✅ (WARN ≤ 2.40 V · ALERT ≤ 2.355 V) |
| CoCoRaHS ok | true | ✅ |
| Rain sensor ok | true | ✅ (but see the light-rain disagreements above) |
| Sensor faults | null | ⚪ not monitored, so this does not mean "healthy" |
| RSSI / hub RSSI | null | ⚪ not monitored |

**Anchor check (health.json):** overall OK, with 0 active watches and 0 confirmed faults over 126 monitored days. 7-day temperature offsets: KWDR +1.02°F, KAHN −0.89°F, WATUGA +1.97°F. The WATUGA anomaly flagged last week (about −7 to −8°F) has cleared, which confirms it was a problem on WATUGA's side.

---

## 📅 Guarantee Timeline

| Milestone | Date | Status |
|---|---|---|
| Guarantee window opens | 2026-08-01 | ✅ Active (day 66) |
| 5-month mark | 2026-10-31 | **26 days away** |
| Claim deadline | 2027-01-25 | 112 days away |

There are under 4 weeks left before the 5-month mark, and the gap is widening, not closing. The verdict won't plausibly flip by Oct 31. The current evidence supports a claim that Tempest underperforms the best public forecast (rolling-90: n = 88, p = 0.0002; since Aug 1: n = 64, p = 0.0003).

---

*Weekly numbers are small-n and descriptive. Significance comes from the cumulative windows (n ≥ 30).*
*Dashboard: https://damngooddawg.github.io/tempest-forecast-verify/dashboard.html*
