# Tempest Better Forecast Guarantee: Weekly Scorecard
**Generated:** 2026-11-16 | **Data through:** 2026-11-14 (scores.json built 2026-11-15 17:49 UTC, about 19.5 h before this report, so it is fresh)

---

## 🔋 Station Health Summary
**The station is healthy. Two flags are open, and neither affects scoring:**
1. **⚠️ `capture_misses = 1`:** This is still the known **2026-07-09** gap. There were **no new misses**: every data/ folder from 06-04 through 11-15 is present except 07-09.
2. **⚠️ `cocorahs_ok = false` (new this week):** The GA-OC-20 feed is reachable but returns **no reports** in its window. The last gauge report was for Nov 5–6. Nov 7–14 was completely dry, so the observer is probably just not filing zero reports. That would make this benign, but it means there is no gauge cross-check right now. If it is still false after the next rain, look into it.
3. **Soft notes (annotate-only):** The Tempest-vs-KAHN pressure offset is −1.76 hPa, just above its band (−3.93 to −2.05). KWDR is in band at −2.74, so this doesn't meet the 2-of-3 rule and is not flagged. The WATUGA temp offset of −8.82°F is a single-anchor divergence, which is logged but not flagged. The radiation-shield check still reads **suspect = true** (calm-sunny highs are +1.3°F vs windy days). Anchor monitor overall: **OK**, with 0 watches and 0 faults over 168 days.

---

## Headline Verdict

> **🔴 TEMPEST BEHIND**
> Tempest was within 3°F on **65%** of days, vs **76%** for NWS. It trails the best public forecast over the last 90 days.
> (n = 90 days · best public: NWS · DM p = 0.0001, significant)

Rolling-90 MAE is **Tempest 2.48°F vs NWS 2.11°F**, a 0.37°F gap. That is the same gap as last week (2.34 vs 1.97); both rose with a hard forecasting week.

**Since Aug 1 (advantage window, n = 106):** Tempest was within 3°F on 66% of days vs 77% for NWS (p < 0.0001).

---

## 📊 Standings: 1-Day Lead (all-time, n ≈ 160–161 days)

| Provider | MAE (°F) ↓ | % Within 3°F ↑ | Precip CSI ↑ |
|---|---|---|---|
| **NWS** 🥇 | **2.05** | **78%** | 0.40 |
| NBM | 2.29 | 68% | 0.31 |
| **★ Tempest** | **2.39** | **68%** | **0.51** |
| GFS | 2.42 | 70% | 0.31 |
| ECMWF | 2.96 | 57% | 0.63 |

*House rows (not guarantee rivals):* Dawg 1.98°F / 77% / CSI 0.64 (n = 59); Blend 2.06°F / 78% / CSI 0.59 (n = 161).

Among the 5 public providers, Tempest ranks 3rd on temperature MAE, up from 4th because it passed GFS. It ranks 2nd on precip CSI, behind ECMWF.

*Rolling 28 days (Oct 18 – Nov 14, n = 28):* Tempest 2.99°F / 52% within 3°F vs NWS 2.66°F / 66% and NBM 2.66°F / 59%.

---

## 📈 Weekly MAE Trend: 1-Day Lead

| Week of | Tempest | NWS | Best public that week | Gap (T − NWS) |
|---|---|---|---|---|
| 2026-10-12 | 3.77 | 2.91 | NWS 2.91 | +0.86 |
| 2026-10-19 | 3.56 | 2.32 | NWS 2.32 | +1.24 |
| 2026-10-26 | 2.04 | 1.89 | NWS 1.89 | +0.15 |
| 2026-11-02 | 2.70 | 2.79 | ★ Tempest 2.70 | −0.09 (revised) |
| **2026-11-09** | **3.26** | **3.67** | **NBM 2.79** | **−0.41** ← latest (Nov 9–14) |

**Closing? Yes, against NWS week to week.** This is the **second straight week Tempest beat NWS**. It did not beat the best public model this week: NBM did better at 2.79. Every source struggled (ECMWF 5.19, GFS 4.16). Tempest's cold bias on highs is still about −2.3°F. These weekly numbers are small-n and descriptive only. The rolling-90 gap did not shrink (still 0.37°F, p = 0.0001), so the cumulative verdict is unchanged.

---

## 💥 Biggest Busts

| Date | Provider | Var | Forecast | Actual | Error |
|---|---|---|---|---|---|
| 2026-11-12 | GFS | High | 61°F | 67°F | −6°F |
| 2026-11-12 | ECMWF | High | 61°F | 67°F | −6°F |
| 2026-11-10 | ECMWF | High | 71°F | 77°F | −6°F |

Once again, the busts are all models forecasting highs too cool. Tempest is off the bust list for the third week in a row.

---

## 🌧️ Rain Totals

| Period | Tempest Raw | Tempest RainCheck | CoCoRaHS Gauge |
|---|---|---|---|
| Nov 8 – Nov 14 (this week) | 0.000 in | 0.000 in | no reports filed |
| Nov 4 (last gauge match) | 0.282 in | 0.282 in | 0.26 in ✅ |
| Oct 18 – Nov 14 (28 d total) | 0.447 in | 0.447 in | 0.36 in on 3 report days |

It was a **completely dry week**, so there was nothing to compare. RainCheck made no corrections (raw = corrected every day). A CoCoRaHS null means no report was filed, not that no rain fell.

---

## 🔋 STATION HEALTH

| Metric | Value | Status |
|---|---|---|
| Capture days | 165 | — |
| **Capture misses** | **1** (2026-07-09) | **⚠️ FLAG: known and unchanged, no new misses** |
| Last snapshot | 0 h ago at build (scores.json 19.5 h old at report time) | ✅ (< 48 h) |
| Station online streak | 129 days | ✅ (was 122 last week) |
| Hub online | true | ✅ |
| Battery | 2.66 V (battery_warn = false) | ✅ (WARN ≤ 2.40 V · ALERT ≤ 2.355 V) |
| **CoCoRaHS ok** | **false** | **⚠️ feed stale/empty, with no reports since ~Nov 6 (dry week)** |
| Rain sensor ok | true | ✅ |
| Sensor faults | null | ⚪ not monitored, so this does not mean "healthy" |
| RSSI / hub RSSI | null | ⚪ not monitored |

**Anchor check (health.json, 7-day offsets):**

| Variable | KWDR | KAHN | WATUGA | Normal band | State |
|---|---|---|---|---|---|
| Temp (°F) | −0.06 | −1.30 | −8.82 | −6.75 to +6.99 | OK |
| RH (pts) | +5.98 | +8.80 | +2.79 | −9.89 to +21.77 | OK |
| Wind (mph) | — | −2.59 | −2.19 | −7.68 to +0.59 | OK |
| Pressure (hPa) | −2.74 | −1.76 | — | −3.93 to −2.05 | OK |

---

## 📅 Guarantee Timeline

| Milestone | Date | Status |
|---|---|---|
| Guarantee window opens | 2026-08-01 | ✅ Active (day 108) |
| 5-month mark | 2026-10-31 | ✅ **Passed. Tempest is still behind** (p < 0.0001) |
| Claim deadline | 2027-01-25 | **70 days away** |

**Action:** Two winning weeks against NWS haven't moved the cumulative picture. In the rolling-90 (n = 90), since-Aug-1 (n = 106) and all-time (n = 161) windows, Tempest trails NWS by about 0.37°F MAE and 10–11 points on within-3°F, at p ≤ 0.0001. The claim evidence is strong and stable. If the claim hasn't been filed yet, file it well before Jan 25.

---

*Weekly numbers are small-n and descriptive. Significance comes from the cumulative windows (n ≥ 30).*
*Dashboard: https://damngooddawg.github.io/tempest-forecast-verify/dashboard.html*
