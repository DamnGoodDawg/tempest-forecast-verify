# Tempest Better Forecast Guarantee — Weekly Scorecard
**Generated:** 2026-09-28 | **Data through:** 2026-09-26 (scores.json built 2026-09-27 15:41 UTC)

---

## ⚠️ STATION HEALTH FLAG
**`capture_misses = 1`** — the single missed snapshot is the known **2026-07-09** gap (116 capture days, 1 miss). **No new misses this week**; daily captures ran every day Sep 21–27. Everything else is nominal (hub online, battery 2.66 V, 80-day online streak). Today's capture hadn't landed yet when this ran (12:27 UTC); the daily job normally commits ~15:00–15:50 UTC.

---

## Headline Verdict

> **🔴 TEMPEST BEHIND**
> Tempest is within 3°F on **76%** of days vs NWS's **83%**, so it trails the best public forecast over the last 90 days.
> (n = 88 days · best public: NWS · DM p = 0.0013, significant)

TEMPEST BEHIND every day since Aug 8. Rolling-90 MAE is Tempest 2.18°F vs NWS 1.83°F (a 0.35°F gap, flat week over week: it was 2.23 vs 1.87 on Sep 20). **Since Aug 1 (the advantage window, n = 57):** Tempest 75% vs NWS 84% within 3°F, p = 0.001. Tempest still beats NWS on precip detection (CSI 0.44 vs 0.37) and PoP calibration (Brier 0.194 vs 0.218), but temperature drives the guarantee.

---

## 📊 Standings — 1-Day Lead (all-time, n ≈ 111–112 days)

| Provider | MAE (°F) ↓ | % Within 3°F ↑ | Precip CSI ↑ |
|---|---|---|---|
| **NWS** 🥇 | **1.90** | **81%** | 0.37 |
| GFS | 2.12 | 77% | 0.30 |
| NBM | 2.18 | 73% | 0.30 |
| **★ Tempest** | **2.21** | **74%** | **0.50** |
| ECMWF | 2.61 | 65% | 0.62 |

*House rows (not guarantee rivals):* Blend 1.90°F / 81% / CSI 0.59 (n = 112); Dawg 1.73°F / 88% / CSI 0.75 (n = 12, early sample).

Tempest is 4th of 5 public providers on temperature. On precip CSI it trails only ECMWF.

---

## 📈 Weekly MAE Trend — 1-Day Lead

| Week of | Tempest | NWS | Best public that week | Gap (T − NWS) |
|---|---|---|---|---|
| 2026-08-24 | 2.54 | 1.61 | NWS 1.61 | +0.93 |
| 2026-08-31 | 2.74 | 2.22 | GFS 2.06 | +0.52 |
| 2026-09-07 | 1.79 | 1.62 | NWS 1.62 | +0.17 |
| 2026-09-14 | 1.49 | 1.26 | NWS 1.26 | +0.23 |
| **2026-09-21** | **2.11** | **2.14** | **NBM 1.82** | **−0.03** ← latest |

**Closing?** Tempest edged NWS last week (2.11 vs 2.14), its first weekly win over NWS since the week of Aug 10. It still lost to NBM (1.82). One week is a small, descriptive sample. The cumulative rolling-90 gap hasn't moved (0.36 → 0.35°F), so the verdict isn't changing yet. Tempest's cold bias has eased a lot: −0.27°F last week vs −2 to −4°F in late Aug/early Sep.

---

## 💥 Biggest Busts (last 7 days)

| Date | Provider | Var | Forecast | Actual | Error |
|---|---|---|---|---|---|
| 2026-09-24 | Tempest | High | 73°F | 68°F | +5°F |
| 2026-09-24 | NWS | High | 73°F | 68°F | +5°F |
| 2026-09-24 | Dawg | High | 73°F | 68°F | +5°F |

The Sep 24 high came in 5°F cooler than forecast, and Tempest, NWS and Dawg all missed it by the same amount. So it doesn't count against Tempest relative to NWS.

---

## 🌧️ Rain Totals (recent rain days)

| Date | Tempest Raw | Tempest RainCheck | CoCoRaHS Gauge | Flag |
|---|---|---|---|---|
| 2026-09-11 | 0.999 in | 0.999 in | 0.30 in | — (≈3× overcount) |
| 2026-09-12 | 0.309 in | 0.309 in | 0.32 in | ✓ |
| 2026-09-18 | 0.000 in | 0.000 in | 0.22 in | ⚠️ DISAGREE |
| 2026-09-19 | 0.253 in | 0.253 in | 0.05 in | — |
| 2026-09-20 | 0.493 in | 0.493 in | 0.42 in | ✓ close |
| 2026-09-22 | 0.068 in | 0.068 in | — (no report) | — |

The week of Sep 21–26 was nearly dry, with only 0.068 in on Sep 22. Sep 20 agreed well with the gauge. The Sep 18 zero-vs-0.22 in disagreement is still the open rain-sensor question. A CoCoRaHS null means no report was filed, not zero rain. RainCheck made no corrections (raw = corrected on every day).

---

## 🔋 STATION HEALTH

| Metric | Value | Status |
|---|---|---|
| Capture days | 116 | — |
| **Capture misses** | **1** (2026-07-09) | **⚠️ FLAG, known and unchanged; no new misses** |
| Last snapshot | 0 h ago at build (2026-09-27 15:41 UTC) | ✅ |
| Station online streak | 80 days | ✅ (was 73 last week) |
| Hub online | true | ✅ |
| Battery | 2.66 V (battery_warn = false) | ✅ (WARN ≤ 2.40 V · ALERT ≤ 2.355 V) |
| CoCoRaHS ok | true | ✅ |
| Rain sensor ok | true | ✅ |
| Sensor faults | null | ⚪ not monitored, so not a "healthy" signal |
| RSSI / hub RSSI | null | ⚪ not monitored |

**Anchor check (health.json):** overall OK, 0 active watches, 0 confirmed faults over 119 monitored days. Temperature agrees closely with KWDR (+0.78°F, 7-day) and KAHN (−0.33°F). The WATUGA offset has widened to about −8°F (−8.6°F weekly), well outside its usual −1 to −4°F. Tempest agrees with both airports, so this looks like a WATUGA-side issue rather than a Tempest fault. Worth a look if it continues.

---

## 📅 Guarantee Timeline

| Milestone | Date | Status |
|---|---|---|
| Guarantee window opens | 2026-08-01 | ✅ Active (day 59) |
| 5-month mark | 2026-10-31 | **33 days away** |
| Claim deadline | 2027-01-25 | 119 days away |

To flip the verdict before Oct 31, Tempest would need to beat NWS by a wide margin every week for the next ~5 weeks. Last week's narrow win is a good sign but nowhere near enough. The current evidence (n = 88, p = 0.0013) supports a claim that Tempest underperforms the best public forecast.

---

*Weekly numbers are small-n and descriptive; significance comes from the cumulative windows (n ≥ 30).*
*Dashboard: https://damngooddawg.github.io/tempest-forecast-verify/dashboard.html*
