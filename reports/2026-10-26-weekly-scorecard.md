# Tempest Better Forecast Guarantee — Weekly Scorecard
**Generated:** 2026-10-26 | **Data through:** 2026-10-24 (scores.json built 2026-10-25 14:58 UTC)

---

## ⚠️ STATION HEALTH FLAGS
1. **`cocorahs_ok = false` (NEW):** The CoCoRaHS gauge feed is stale. Its last report covers calendar day **2026-10-10**, and the code calls the feed stale after 8 days with no report. We've had about two weeks with no rain: Tempest logged 0.00 in every day from Oct 12 to Oct 24. The likeliest cause is the observer skipping zero-rain reports, not a broken feed. Still, the next rain event will have **no gauge truth** unless reports resume. Check that the observer is still filing.
2. **`capture_misses = 1`:** This is still the known **2026-07-09** gap (144 capture days). **There were no new misses this week.** Every data/ folder from 06-04 through 10-25 is present except 07-09.
3. **Anchor watch (soft):** The WATUGA 7-day temp offset is **−6.44°F**, close to the lower band edge of −6.72°F. Overall health is still OK with 0 active watches. The high-temp radiation-shield check now reads **suspect = true** (calm-sunny split +1.32°F vs airports). That check is annotate-only and changes no scores.

Everything else is nominal: the hub is online, the battery reads 2.66 V and the station has been online for 108 straight days.

---

## Headline Verdict

> **🔴 TEMPEST BEHIND**
> Tempest was within 3°F on **69%** of days, vs **80%** for NWS. It trails the best public forecast over the last 90 days.
> (n = 90 days · best public: NWS · DM p < 0.0001, significant)

**The gap widened this week.** Rolling-90 MAE is Tempest 2.39°F vs NWS 1.90°F, a **0.49°F** gap. Last week it was 2.29 vs 1.87 (0.42°F). **Since Aug 1 (advantage window, n = 85):** Tempest was within 3°F on 68% of days vs 79% for NWS (MAE 2.42 vs 1.89, p < 0.0001). NWS edges Tempest on precip CSI (0.47 vs 0.46). Tempest still wins on PoP Brier (0.133 vs 0.143).

---

## 📊 Standings — 1-Day Lead (all-time, n ≈ 139–140 days)

| Provider | MAE (°F) ↓ | % Within 3°F ↑ | Precip CSI ↑ |
|---|---|---|---|
| **NWS** 🥇 | **1.95** | **79%** | 0.41 |
| NBM | 2.25 | 69% | 0.31 |
| GFS | 2.29 | 73% | 0.31 |
| **★ Tempest** | **2.36** | **70%** | **0.52** |
| ECMWF | 2.83 | 59% | 0.63 |

*House rows (not guarantee rivals):* Dawg 1.83°F / 82% / CSI 0.70 (n = 39); Blend 1.96°F / 79% / CSI 0.60 (n = 140).

Among the 5 public providers, Tempest still ranks 4th on temperature. It ranks 2nd on precip CSI, behind only ECMWF.

---

## 📈 Weekly MAE Trend — 1-Day Lead

| Week of | Tempest | NWS | Best public that week | Gap (T − NWS) |
|---|---|---|---|---|
| 2026-09-21 | 2.29 | 2.15 | NBM 2.07 | +0.14 |
| 2026-09-28 | 1.82 | 1.22 | NWS 1.22 | +0.60 |
| 2026-10-05 | 2.60 | 2.24 | NWS 2.24 | +0.36 |
| 2026-10-12 | 3.77 | 2.91 | NWS 2.91 | +0.86 (final) |
| **2026-10-19** | **3.68** | **2.32** | **NWS 2.32** | **+1.36** ← latest (partial, Oct 19–24) |

**Closing? No, it's opening up.** This was Tempest's worst gap to NWS since tracking began. Tempest lost to NBM (2.62) and GFS (2.86) as well, and beat only ECMWF (4.83). That makes 10 straight weeks without beating NWS, going back to the week of Aug 10. Weekly numbers are small-n and descriptive.

---

## 💥 Biggest Busts

| Date | Provider | Var | Forecast | Actual | Error |
|---|---|---|---|---|---|
| 2026-10-18 | **★ Tempest** | High | 62°F | 68°F | −6°F |
| 2026-10-19 | ECMWF | High | 66°F | 72°F | −6°F |
| 2026-10-18 | ECMWF | High | 62°F | 68°F | −6°F |

Tempest is back on the bust list this week. Every bust was a forecast high that came in too cool, the same cold bias on highs seen through October.

---

## 🌧️ Rain Totals

| Date | Tempest Raw | Tempest RainCheck | CoCoRaHS Gauge |
|---|---|---|---|
| 2026-10-04 | 0.112 in | 0.112 in | 0.14 in |
| 2026-10-09 | 0.122 in | 0.122 in | 1.42 in |
| 2026-10-10 | 1.349 in | 1.349 in | 0.68 in |
| 2026-10-11 | 0.041 in | 0.041 in | — (no report) |
| Oct 12–24 | 0.000 in every day | 0.000 in | — (no reports) |

**It was a dry week, and the dry spell is now in its second week.** The latest comparison is still the Oct 9–10 storm: Tempest logged 1.47 in vs 2.10 in at the gauge over the two days, about 30% low. RainCheck made no corrections, so raw equals corrected. A CoCoRaHS null means no report was filed (see the health flag), not that no rain fell.

---

## 🔋 STATION HEALTH

| Metric | Value | Status |
|---|---|---|
| Capture days | 144 | — |
| **Capture misses** | **1** (2026-07-09) | **⚠️ FLAG: known and unchanged, no new misses** |
| Last snapshot | 0 h ago at build (2026-10-25 14:58 UTC) | ✅ (< 48 h) |
| Station online streak | 108 days | ✅ (was 101 last week) |
| Hub online | true | ✅ |
| Battery | 2.66 V (battery_warn = false) | ✅ (WARN ≤ 2.40 V · ALERT ≤ 2.355 V) |
| **CoCoRaHS ok** | **false** | **⚠️ FLAG: stale, no report in more than 8 days (last covers Oct 10)** |
| Rain sensor ok | true | ✅ |
| Sensor faults | null | ⚪ not monitored, so this does not mean "healthy" |
| RSSI / hub RSSI | null | ⚪ not monitored |

**Anchor check (health.json):** overall OK, with 0 active watches and 0 confirmed faults over 147 monitored days. 7-day temperature offsets: KWDR +1.66°F, KAHN +0.39°F, WATUGA **−6.44°F** (normal band −6.72 to +6.42, so WATUGA is near the edge). RH, wind and pressure are all within their bands. The high-temp shield check reads **suspect** (split +1.32°F), which is annotate-only.

---

## 📅 Guarantee Timeline

| Milestone | Date | Status |
|---|---|---|
| Guarantee window opens | 2026-08-01 | ✅ Active (day 87) |
| 5-month mark | 2026-10-31 | **5 days away** |
| Claim deadline | 2027-01-25 | 91 days away |

The 5-month mark is this Saturday. Tempest trails NWS by about 0.5°F MAE and 11 points on within-3°F at p < 0.0001, at both rolling-90 (n = 90) and since Aug 1 (n = 85). The verdict will not flip by Oct 31. The evidence for a claim is strong, so consider preparing the claim soon after Oct 31.

---

*Weekly numbers are small-n and descriptive. Significance comes from the cumulative windows (n ≥ 30).*
*Dashboard: https://damngooddawg.github.io/tempest-forecast-verify/dashboard.html*
