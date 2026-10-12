# Tempest Better Forecast Guarantee — Weekly Scorecard
**Generated:** 2026-10-12 | **Data through:** 2026-10-10 (scores.json built 2026-10-11 16:40 UTC)

---

## ⚠️ STATION HEALTH FLAG
**`capture_misses = 1`**: this is still the known **2026-07-09** gap (130 capture days, 1 miss). **There were no new misses this week.** All 7 daily captures from Oct 5 to Oct 11 landed. Everything else is nominal: the hub is online, the battery reads 2.64 V and the station has been online for 94 straight days. One thing to watch: the WATUGA anchor offset is −5.65°F, just outside its normal band. The overall anchor check is still OK, with KWDR and KAHN both agreeing with Tempest, so the problem looks like it's on WATUGA's side, the same as last month. Today's capture hadn't landed when this ran at 12:28 UTC. The daily job normally commits around 15:00–16:45 UTC.

---

## Headline Verdict

> **🔴 TEMPEST BEHIND**
> Tempest was within 3°F on **74%** of days, vs **85%** for NWS. It trails the best public forecast over the last 90 days.
> (n = 90 days · best public: NWS · DM p < 0.0001, significant)

**The gap stayed about the same this week.** Rolling-90 MAE is Tempest 2.22°F vs NWS 1.77°F, a 0.45°F gap. Last week it was 2.21 vs 1.79 (0.42°F). **Since Aug 1 (advantage window, n = 71):** Tempest was within 3°F on 75% of days vs 84% for NWS (MAE 2.18 vs 1.74, p = 0.0001). Tempest no longer leads NWS on the secondary metrics. NWS now edges it on precip CSI (0.48 vs 0.44), and PoP Brier is tied at 0.159.

---

## 📊 Standings — 1-Day Lead (all-time, n ≈ 125–126 days)

| Provider | MAE (°F) ↓ | % Within 3°F ↑ | Precip CSI ↑ |
|---|---|---|---|
| **NWS** 🥇 | **1.87** | **82%** | 0.41 |
| NBM | 2.16 | 72% | 0.32 |
| GFS | 2.17 | 76% | 0.32 |
| **★ Tempest** | **2.21** | **74%** | **0.51** |
| ECMWF | 2.65 | 64% | 0.62 |

*House rows (not guarantee rivals):* Blend 1.88°F / 81% / CSI 0.59 (n = 126); Dawg 1.65°F / 88% / CSI 0.67 (n = 25, early sample).

Among the 5 public providers, Tempest ranks 4th on temperature and 2nd on precip CSI (only ECMWF is ahead).

---

## 📈 Weekly MAE Trend — 1-Day Lead

| Week of | Tempest | NWS | Best public that week | Gap (T − NWS) |
|---|---|---|---|---|
| 2026-09-07 | 1.79 | 1.62 | NWS 1.62 | +0.17 |
| 2026-09-14 | 1.49 | 1.26 | NWS 1.26 | +0.23 |
| 2026-09-21 | 2.29 | 2.15 | NBM 2.07 | +0.14 |
| 2026-09-28 | 1.82 | 1.22 | NWS 1.22 | +0.60 (revised) |
| **2026-10-05** | **2.58** | **2.16** | **NWS 2.16** | **+0.42** ← latest (partial) |

**Closing? No.** Tempest lost to NWS again this week by 0.42°F. It also trailed NBM (2.47). It beat only GFS (2.94) and ECMWF (3.28). Tempest has not beaten NWS in a full week since the week of Aug 10, which makes 8 straight losing weeks. One bright spot: Tempest's cold bias shrank to −0.27°F this week, from −1.54°F. That is its smallest bias since June, and it's now smaller than NBM's (−1.10°F). Weekly numbers are small-n and descriptive.

---

## 💥 Biggest Busts (last 7 days)

| Date | Provider | Var | Forecast | Actual | Error |
|---|---|---|---|---|---|
| 2026-10-09 | GFS | High | 82°F | 74°F | +8°F |
| 2026-10-04 | GFS | High | 81°F | 73°F | +8°F |
| 2026-10-10 | ECMWF | High | 72°F | 66°F | +6°F |

Tempest is not on the bust list again this week. This week's busts were the opposite of last week's: models forecast highs too warm on cloudy, rainy days (Oct 9–10).

---

## 🌧️ Rain Totals (recent rain days)

| Date | Tempest Raw | Tempest RainCheck | CoCoRaHS Gauge | Flag |
|---|---|---|---|---|
| 2026-09-20 | 0.493 in | 0.493 in | 0.42 in | ✓ close |
| 2026-09-22 | 0.068 in | 0.068 in | — (no report) | — |
| 2026-10-03 | 0.002 in | 0.002 in | 0.07 in | ⚠️ DISAGREE |
| 2026-10-04 | 0.112 in | 0.112 in | 0.14 in | ✓ close |
| 2026-10-09 | 0.122 in | 0.122 in | 1.42 in | — (not flagged) |
| 2026-10-10 | 1.349 in | 1.349 in | 0.68 in | — (not flagged) |

This week's storm on Oct 9–10 was the biggest rain event in weeks. Day by day, the two sources look far apart: Oct 9 was 0.12 vs 1.42 in, and Oct 10 was 1.35 vs 0.68 in. Most of that is timing. CoCoRaHS reports at about 7 AM, and the storm straddled the day boundary. Over the two days combined, **Tempest logged 1.47 in vs 2.10 in at the gauge, about 30% low.** That fits the earlier pattern of Tempest under-reading against the gauge (Sep 18, Oct 3). RainCheck made no corrections: raw equals corrected on every day. A CoCoRaHS null means no report was filed, not that no rain fell.

---

## 🔋 STATION HEALTH

| Metric | Value | Status |
|---|---|---|
| Capture days | 130 | — |
| **Capture misses** | **1** (2026-07-09) | **⚠️ FLAG: known and unchanged, no new misses** |
| Last snapshot | 0 h ago at build (2026-10-11 16:40 UTC) | ✅ |
| Station online streak | 94 days | ✅ (was 87 last week) |
| Hub online | true | ✅ |
| Battery | 2.64 V (battery_warn = false) | ✅ (WARN ≤ 2.40 V · ALERT ≤ 2.355 V) |
| CoCoRaHS ok | true | ✅ |
| Rain sensor ok | true | ✅ (but see the 2-day storm deficit above) |
| Sensor faults | null | ⚪ not monitored, so this does not mean "healthy" |
| RSSI / hub RSSI | null | ⚪ not monitored |

**Anchor check (health.json):** overall OK, with 0 active watches and 0 confirmed faults over 133 monitored days. 7-day temperature offsets: KWDR +1.35°F, KAHN −0.02°F, **WATUGA −5.65°F**, just outside the normal band of −5.38 to +5.22. The two airport anchors agree with Tempest, so this looks like a repeat of WATUGA's own problem from last month, not a Tempest fault.

---

## 📅 Guarantee Timeline

| Milestone | Date | Status |
|---|---|---|
| Guarantee window opens | 2026-08-01 | ✅ Active (day 73) |
| 5-month mark | 2026-10-31 | **19 days away** |
| Claim deadline | 2027-01-25 | 105 days away |

There are under 3 weeks left before the 5-month mark, and the gap is steady at about 0.45°F. The verdict won't plausibly flip by Oct 31. The evidence for a claim keeps getting stronger: Tempest underperforms the best public forecast at rolling-90 (n = 90, p < 0.0001) and since Aug 1 (n = 71, p = 0.0001).

---

*Weekly numbers are small-n and descriptive. Significance comes from the cumulative windows (n ≥ 30).*
*Dashboard: https://damngooddawg.github.io/tempest-forecast-verify/dashboard.html*
