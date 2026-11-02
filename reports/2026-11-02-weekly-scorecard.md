# Tempest Better Forecast Guarantee — Weekly Scorecard
**Generated:** 2026-11-02 | **Data through:** 2026-10-31 (scores.json built 2026-11-01 17:10 UTC)

---

## ⚠️ STATION HEALTH FLAGS
1. **`cocorahs_ok = false` (3rd week running):** No CoCoRaHS report from GA-OC-20 since the one covering **2026-10-10**. The Nov 1 capture returned an empty CSV. Tempest logged 0.00 in every day from Oct 12 to Oct 31, so the observer is probably just skipping zero-rain days. Still, the next rain event will have **no gauge truth** unless reports resume.
2. **`capture_misses = 1`:** This is still the known **2026-07-09** gap. **There were no new misses.** Every data/ folder from 06-04 through 11-01 is present except 07-09.
3. **Soft notes:** The Tempest-vs-KAHN pressure offset reads **−2.39 hPa**, just inside the top of its normal band (−4.12 to −2.33). The high-temp radiation-shield check still reads **suspect = true** (calm-sunny split +1.33°F), which is annotate-only and changes no scores. Last week's WATUGA temperature concern has eased: the offset went from −6.44°F to −0.10°F.

Everything else is nominal: the hub is online, the battery reads 2.65 V, the station has been online for 115 straight days, the last snapshot was 0 h before the build, and health.json shows overall OK (0 watches, 0 faults).

---

## Headline Verdict

> **🔴 TEMPEST BEHIND**
> Tempest was within 3°F on **68%** of days, vs **80%** for NWS. It trails the best public forecast over the last 90 days.
> (n = 90 days · best public: NWS · DM p < 0.0001, significant)

Rolling-90 MAE is **Tempest 2.37°F vs NWS 1.88°F**, a 0.49°F gap. That is essentially unchanged from last week (2.39 vs 1.90). **Since Aug 1 (advantage window, n = 92):** Tempest was within 3°F on 68% of days vs 80% for NWS (MAE 2.40 vs 1.89, p < 0.0001). NWS edges Tempest on precip CSI (0.47 vs 0.46). Tempest still wins on PoP Brier (0.123 vs 0.132). The **5-month mark (Oct 31) has now passed, and Tempest is still behind.**

---

## 📊 Standings — 1-Day Lead (all-time, n ≈ 146–147 days)

| Provider | MAE (°F) ↓ | % Within 3°F ↑ | Precip CSI ↑ |
|---|---|---|---|
| **NWS** 🥇 | **1.95** | **79%** | 0.41 |
| NBM | 2.24 | 69% | 0.31 |
| GFS | 2.28 | 73% | 0.31 |
| **★ Tempest** | **2.35** | **70%** | **0.52** |
| ECMWF | 2.86 | 59% | 0.63 |

*House rows (not guarantee rivals):* Dawg 1.77°F / 84% / CSI 0.70 (n = 45); Blend 1.95°F / 79% / CSI 0.60 (n = 147).

Among the 5 public providers, Tempest ranks 4th on temperature. It ranks 2nd on precip CSI, behind only ECMWF.

---

## 📈 Weekly MAE Trend — 1-Day Lead

| Week of | Tempest | NWS | Best public that week | Gap (T − NWS) |
|---|---|---|---|---|
| 2026-09-28 | 1.82 | 1.22 | NWS 1.22 | +0.60 |
| 2026-10-05 | 2.60 | 2.24 | NWS 2.24 | +0.36 |
| 2026-10-12 | 3.77 | 2.91 | NWS 2.91 | +0.86 |
| 2026-10-19 | 3.56 | 2.32 | NWS 2.32 | +1.24 (final) |
| **2026-10-26** | **2.03** | **1.77** | **NWS 1.77** | **+0.26** ← latest (Oct 26–31) |

**Closing? Somewhat, this week.** The gap is the narrowest since the week of Sep 21, and Tempest beat NBM (2.09), GFS (2.22) and ECMWF (3.58). NWS still won, though. That makes 11 straight weeks without Tempest beating NWS, going back to the week of Aug 10. Tempest's cold bias on highs is easing (−2.33°F this week vs −3.09°F the week before). Weekly numbers are small-n and descriptive.

---

## 💥 Biggest Busts

| Date | Provider | Var | Forecast | Actual | Error |
|---|---|---|---|---|---|
| 2026-10-28 | ECMWF | High | 71°F | 77°F | −6°F |
| 2026-10-30 | ECMWF | High | 78°F | 84°F | −6°F |
| 2026-10-28 | NBM | High | 72°F | 77°F | −5°F |

Tempest is off the bust list this week. All the busts were forecast highs that came in too cool during the late-October warm spell.

---

## 🌧️ Rain Totals

| Date | Tempest Raw | Tempest RainCheck | CoCoRaHS Gauge |
|---|---|---|---|
| 2026-10-11 | 0.041 in | 0.041 in | — (no report) |
| Oct 12–31 | 0.000 in every day | 0.000 in | — (no reports) |

**It was a dry week, and the dry spell has now run about 3 weeks.** There is nothing new to compare against the gauge. The most recent comparison is still the Oct 9–10 storm, when Tempest logged 1.47 in vs 2.10 in at the gauge, about 30% low. A CoCoRaHS null means no report was filed, not that no rain fell.

---

## 🔋 STATION HEALTH

| Metric | Value | Status |
|---|---|---|
| Capture days | 151 | — |
| **Capture misses** | **1** (2026-07-09) | **⚠️ FLAG: known and unchanged, no new misses** |
| Last snapshot | 0 h ago at build (2026-11-01 17:10 UTC) | ✅ (< 48 h) |
| Station online streak | 115 days | ✅ (was 108 last week) |
| Hub online | true | ✅ |
| Battery | 2.65 V (battery_warn = false) | ✅ (WARN ≤ 2.40 V · ALERT ≤ 2.355 V) |
| **CoCoRaHS ok** | **false** | **⚠️ FLAG: stale, last report covers Oct 10** |
| Rain sensor ok | true | ✅ |
| Sensor faults | null | ⚪ not monitored, so this does not mean "healthy" |
| RSSI / hub RSSI | null | ⚪ not monitored |

**Anchor check (health.json):** overall OK, with 0 active watches and 0 confirmed faults over 154 monitored days.

| Variable | KWDR | KAHN | WATUGA | Normal band |
|---|---|---|---|---|
| Temp (°F) | +1.43 | −0.78 | −0.10 | −6.28 to +5.87 |
| RH (%) | +2.01 | +7.60 | +8.15 | −10.81 to +23.04 |
| Wind (mph) | — | −4.58 | −3.66 | −6.29 to +1.71 |
| Pressure (hPa) | −3.25 | **−2.39** | — | −4.12 to −2.33 (KAHN is near the edge) |

---

## 📅 Guarantee Timeline

| Milestone | Date | Status |
|---|---|---|
| Guarantee window opens | 2026-08-01 | ✅ Active (day 94) |
| 5-month mark | 2026-10-31 | ✅ **Passed. Tempest is still behind** (p < 0.0001) |
| Claim deadline | 2027-01-25 | **84 days away** |

**Action:** The 5-month mark has passed and the verdict did not flip. Tempest trails NWS by about 0.5°F MAE and 12 points on within-3°F at p < 0.0001, in both the rolling-90 (n = 90) and since-Aug-1 (n = 92) windows. The evidence for a claim is strong and stable, so it's time to prepare and file the claim, well ahead of Jan 25.

---

*Weekly numbers are small-n and descriptive. Significance comes from the cumulative windows (n ≥ 30).*
*Dashboard: https://damngooddawg.github.io/tempest-forecast-verify/dashboard.html*
