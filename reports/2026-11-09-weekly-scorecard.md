# Tempest Better Forecast Guarantee: Weekly Scorecard
**Generated:** 2026-11-09 | **Data through:** 2026-11-07 (scores.json built 2026-11-08 17:07 UTC)

---

## 🔋 Station Health Summary
**No new problems this week.** The only open flag is the old one:
1. **`capture_misses = 1`:** This is still the known **2026-07-09** gap, and there were **no new misses**. Every data/ folder from 06-04 through 11-08 is present except 07-09.
2. **CoCoRaHS has recovered.** `cocorahs_ok` is **true** again, after three weeks of false. GA-OC-20 filed reports for Nov 4, 5 and 6.
3. **Soft notes (annotate-only):** The Tempest-vs-KAHN pressure offset is −2.52 hPa, which is back inside its normal band (−4.02 to −2.13). The radiation-shield check on high temps still reads **suspect = true**: on calm, sunny days highs read +1.26°F further above the airport stations than on windy days. This changes no scores.

---

## Headline Verdict

> **🔴 TEMPEST BEHIND**
> Tempest was within 3°F on **68%** of days, vs **78%** for NWS. It trails the best public forecast over the last 90 days.
> (n = 90 days · best public: NWS · DM p = 0.0001, significant)

Rolling-90 MAE is **Tempest 2.34°F vs NWS 1.97°F**, a 0.37°F gap. Last week the gap was 0.49°F (2.37 vs 1.88).

**Since Aug 1 (advantage window, n = 99):** Tempest was within 3°F on 67% of days vs 79% for NWS (MAE 2.42 vs 1.96, p < 0.0001). Tempest does beat NWS on precip CSI (0.46 vs 0.44) and on PoP Brier (0.133 vs 0.146). The guarantee is judged on temperature, though, and there Tempest is clearly behind.

---

## 📊 Standings: 1-Day Lead (all-time, n ≈ 153–154 days)

| Provider | MAE (°F) ↓ | % Within 3°F ↑ | Precip CSI ↑ |
|---|---|---|---|
| **NWS** 🥇 | **1.99** | **78%** | 0.40 |
| NBM | 2.27 | 69% | 0.31 |
| GFS | 2.34 | 71% | 0.31 |
| **★ Tempest** | **2.36** | **69%** | **0.51** |
| ECMWF | 2.88 | 58% | 0.63 |

*House rows (not guarantee rivals):* Dawg 1.91°F / 81% / CSI 0.64 (n = 52); Blend 1.99°F / 78% / CSI 0.59 (n = 154).

Among the 5 public providers, Tempest ranks 4th on temperature and 2nd on precip CSI, behind ECMWF.

---

## 📈 Weekly MAE Trend: 1-Day Lead

| Week of | Tempest | NWS | Best public that week | Gap (T − NWS) |
|---|---|---|---|---|
| 2026-10-05 | 2.60 | 2.24 | NWS 2.24 | +0.36 |
| 2026-10-12 | 3.77 | 2.91 | NWS 2.91 | +0.86 |
| 2026-10-19 | 3.56 | 2.32 | NWS 2.32 | +1.24 |
| 2026-10-26 | 2.04 | 1.89 | NWS 1.89 | +0.15 (revised) |
| **2026-11-02** | **2.72** | **2.93** | **★ Tempest 2.72** | **−0.21** ← latest (Nov 2–7) |

**Closing? Yes, for now.** This is the **first week since Aug 10 that Tempest beat NWS**. It also beat every public model: NBM 3.00, ECMWF 3.55, GFS 3.88. It was a hard week for every forecaster, because highs ran warm. The gap has now narrowed for two weeks running. Even so, one partial week (n ≈ 6) is descriptive only. Tempest's cold bias on highs is still about −2.4°F this week, and the rolling-90 verdict is unchanged.

---

## 💥 Biggest Busts

| Date | Provider | Var | Forecast | Actual | Error |
|---|---|---|---|---|---|
| 2026-11-06 | GFS | High | 71°F | 79°F | −8°F |
| 2026-11-05 | GFS | High | 74°F | 81°F | −7°F |
| 2026-11-07 | GFS | High | 66°F | 73°F | −7°F |

All of this week's busts were GFS highs that came in too cool during the early-November warm spell. Tempest is off the bust list for the second week in a row.

---

## 🌧️ Rain Totals

| Date | Tempest Raw | Tempest RainCheck | CoCoRaHS Gauge | Flag |
|---|---|---|---|---|
| 2026-10-31 | 0.000 in | 0.000 in | 0.05 in | disagree |
| 2026-11-01 | 0.155 in | 0.155 in | — | |
| 2026-11-04 | 0.282 in | 0.282 in | 0.26 in | ✅ agrees (+8%) |
| 2026-11-05 | 0.004 in | 0.004 in | 0.05 in | disagree |
| 2026-11-06 | 0.006 in | 0.006 in | — | |
| Nov 2–3, Nov 7 | 0.000 in | 0.000 in | — | |

**The ~3-week dry spell broke.** The Nov 4 event is the first gauge comparison since the Oct 9–10 storm, and Tempest agreed with the gauge to within 0.02 in. The two "disagree" days are small amounts of 0.05 in that Tempest saw as a trace or as nothing. That may be a timing difference between Tempest's day boundary and the gauge's 7 AM reading, rather than a sensor issue. A CoCoRaHS null means no report was filed, not that no rain fell.

---

## 🔋 STATION HEALTH

| Metric | Value | Status |
|---|---|---|
| Capture days | 158 | — |
| **Capture misses** | **1** (2026-07-09) | **⚠️ FLAG: known and unchanged, no new misses** |
| Last snapshot | 0 h ago at build (2026-11-08 17:07 UTC; about 20 h before this report) | ✅ (< 48 h) |
| Station online streak | 122 days | ✅ (was 115 last week) |
| Hub online | true | ✅ |
| Battery | 2.66 V (battery_warn = false) | ✅ (WARN ≤ 2.40 V · ALERT ≤ 2.355 V) |
| CoCoRaHS ok | true | ✅ recovered (false for the prior 3 weeks) |
| Rain sensor ok | true | ✅ |
| Sensor faults | null | ⚪ not monitored, so this does not mean "healthy" |
| RSSI / hub RSSI | null | ⚪ not monitored |

**Anchor check (health.json):** overall OK, with 0 active watches and 0 confirmed faults over 161 monitored days.

| Variable | KWDR | KAHN | WATUGA | Normal band |
|---|---|---|---|---|
| Temp (°F) | +1.49 | +0.04 | −0.21 | −5.64 to +5.21 |
| RH (pts) | +0.96 | +1.23 | +9.05 | −8.90 to +20.78 |
| Wind (mph) | — | −4.16 | −4.92 | −7.22 to +1.22 |
| Pressure (hPa) | −3.43 | −2.52 | — | −4.02 to −2.13 |

---

## 📅 Guarantee Timeline

| Milestone | Date | Status |
|---|---|---|
| Guarantee window opens | 2026-08-01 | ✅ Active (day 101) |
| 5-month mark | 2026-10-31 | ✅ **Passed. Tempest is still behind** (p < 0.0001) |
| Claim deadline | 2027-01-25 | **77 days away** |

**Action:** Tempest's first winning week doesn't change the cumulative picture. In both the rolling-90 (n = 90) and since-Aug-1 (n = 99) windows, Tempest trails NWS by about 0.4–0.5°F MAE and 10–12 points on within-3°F, at p ≤ 0.0001. The claim evidence is strong and stable. If the claim hasn't been filed yet, file it well ahead of Jan 25.

---

*Weekly numbers are small-n and descriptive. Significance comes from the cumulative windows (n ≥ 30).*
*Dashboard: https://damngooddawg.github.io/tempest-forecast-verify/dashboard.html*
