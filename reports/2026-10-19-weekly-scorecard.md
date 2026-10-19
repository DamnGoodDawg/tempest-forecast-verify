# Tempest Better Forecast Guarantee — Weekly Scorecard
**Generated:** 2026-10-19 | **Data through:** 2026-10-17 (scores.json built 2026-10-18 14:39 UTC)

---

## ⚠️ STATION HEALTH FLAG
**`capture_misses = 1`**: this is still the known **2026-07-09** gap (137 capture days, 1 miss). **There were no new misses this week.** Every data/ folder from 2026-06-04 to 2026-10-18 is present except 07-09. Everything else is nominal: the hub is online, the battery reads 2.66 V and the station has been online for 101 straight days. **Last week's WATUGA anchor watch has cleared.** The 7-day offset went from −5.65°F to −0.23°F, and all three anchors are now within ±0.6°F of Tempest. Today's capture had not landed when this ran at 12:12 UTC. The daily job normally commits around 14:30–16:45 UTC.

---

## Headline Verdict

> **🔴 TEMPEST BEHIND**
> Tempest was within 3°F on **72%** of days, vs **83%** for NWS. It trails the best public forecast over the last 90 days.
> (n = 90 days · best public: NWS · DM p < 0.0001, significant)

**The gap stayed about the same this week.** Rolling-90 MAE is Tempest 2.29°F vs NWS 1.87°F, a 0.42°F gap. Last week it was 2.22 vs 1.77 (0.45°F). Both forecasts got worse because of a hard warm spell. **Since Aug 1 (advantage window, n = 78):** Tempest was within 3°F on 71% of days vs 81% for NWS (MAE 2.28 vs 1.84, p < 0.0001). NWS edges Tempest on precip CSI (0.47 vs 0.46). Tempest still wins on PoP Brier (0.145 vs 0.156).

---

## 📊 Standings — 1-Day Lead (all-time, n ≈ 132–133 days)

| Provider | MAE (°F) ↓ | % Within 3°F ↑ | Precip CSI ↑ |
|---|---|---|---|
| **NWS** 🥇 | **1.92** | **80%** | 0.41 |
| NBM | 2.21 | 70% | 0.31 |
| GFS | 2.25 | 74% | 0.31 |
| **★ Tempest** | **2.27** | **72%** | **0.52** |
| ECMWF | 2.71 | 62% | 0.63 |

*House rows (not guarantee rivals):* Blend 1.93°F / 80% / CSI 0.60 (n = 133); Dawg 1.78°F / 83% / CSI 0.70 (n = 32).

Among the 5 public providers, Tempest ranks 4th on temperature, behind NWS, NBM and GFS. It ranks 2nd on precip CSI, behind only ECMWF.

---

## 📈 Weekly MAE Trend — 1-Day Lead

| Week of | Tempest | NWS | Best public that week | Gap (T − NWS) |
|---|---|---|---|---|
| 2026-09-14 | 1.49 | 1.26 | NWS 1.26 | +0.23 |
| 2026-09-21 | 2.29 | 2.15 | NBM 2.07 | +0.14 |
| 2026-09-28 | 1.82 | 1.22 | NWS 1.22 | +0.60 |
| 2026-10-05 | 2.60 | 2.24 | NWS 2.24 | +0.36 (final) |
| **2026-10-12** | **3.40** | **2.82** | **NWS 2.82** | **+0.58** ← latest (partial, Oct 12–17) |

**Closing? No.** This was a rough week for every forecast. Tempest lost to NWS by 0.58°F and also trailed NBM (3.22). It beat GFS (3.97) and ECMWF (4.10). That makes 9 straight weeks without beating NWS, going back to the week of Aug 10. The cold bias came back: Tempest averaged −3.55°F this week vs −3.80°F for NBM. That fits a warm spell where forecast highs came in too low. Weekly numbers are small-n and descriptive.

---

## 💥 Biggest Busts (last 7 days)

| Date | Provider | Var | Forecast | Actual | Error |
|---|---|---|---|---|---|
| 2026-10-12 | GFS | High | 80°F | 88°F | −8°F |
| 2026-10-15 | ECMWF | High | 85°F | 92°F | −7°F |
| 2026-10-13 | ECMWF | High | 84°F | 90°F | −6°F |

Tempest is not on the bust list again this week. Every bust was a forecast high that came in too cool during the Oct 12–15 warm spell, when highs reached 88–92°F.

---

## 🌧️ Rain Totals (recent rain days)

| Date | Tempest Raw | Tempest RainCheck | CoCoRaHS Gauge | Flag |
|---|---|---|---|---|
| 2026-10-03 | 0.002 in | 0.002 in | 0.07 in | ⚠️ DISAGREE |
| 2026-10-04 | 0.112 in | 0.112 in | 0.14 in | ✓ close |
| 2026-10-09 | 0.122 in | 0.122 in | 1.42 in | — |
| 2026-10-10 | 1.349 in | 1.349 in | 0.68 in | — |
| 2026-10-11 | 0.041 in | 0.041 in | — (no report) | — |

**It was a dry week.** Tempest recorded 0.000 in every day from Oct 12 to Oct 17, and CoCoRaHS filed no reports. The latest comparison is still the Oct 9–10 storm: Tempest logged 1.47 in vs 2.10 in at the gauge over the two days, about 30% low. RainCheck made no corrections, so raw equals corrected. A CoCoRaHS null means no report was filed, not that no rain fell.

---

## 🔋 STATION HEALTH

| Metric | Value | Status |
|---|---|---|
| Capture days | 137 | — |
| **Capture misses** | **1** (2026-07-09) | **⚠️ FLAG: known and unchanged, no new misses** |
| Last snapshot | 0 h ago at build (2026-10-18 14:39 UTC) | ✅ |
| Station online streak | 101 days | ✅ (was 94 last week) |
| Hub online | true | ✅ |
| Battery | 2.66 V (battery_warn = false) | ✅ (WARN ≤ 2.40 V · ALERT ≤ 2.355 V) |
| CoCoRaHS ok | true | ✅ |
| Rain sensor ok | true | ✅ |
| Sensor faults | null | ⚪ not monitored, so this does not mean "healthy" |
| RSSI / hub RSSI | null | ⚪ not monitored |

**Anchor check (health.json):** overall OK, with 0 active watches and 0 confirmed faults over 140 monitored days. 7-day temperature offsets: KWDR +0.04°F, KAHN −0.61°F, WATUGA −0.23°F (normal band −5.29 to +4.83). Pressure, RH and wind are all within their bands. The high-temp radiation-shield check shows no suspect signature (split +1.0°F).

---

## 📅 Guarantee Timeline

| Milestone | Date | Status |
|---|---|---|
| Guarantee window opens | 2026-08-01 | ✅ Active (day 80) |
| 5-month mark | 2026-10-31 | **12 days away** |
| Claim deadline | 2027-01-25 | 98 days away |

The 5-month mark is 12 days away, and the gap is steady at about 0.4°F with p < 0.0001. The verdict won't realistically flip by Oct 31. The evidence for a claim is strong at both rolling-90 (n = 90) and since Aug 1 (n = 78).

---

*Weekly numbers are small-n and descriptive. Significance comes from the cumulative windows (n ≥ 30).*
*Dashboard: https://damngooddawg.github.io/tempest-forecast-verify/dashboard.html*
