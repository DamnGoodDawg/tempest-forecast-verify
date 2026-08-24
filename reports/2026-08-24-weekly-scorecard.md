# Tempest Forecast Scorecard — 2026-08-24

_Generated: 2026-08-24 | Data through: 2026-08-23 | 78 scored days (all-time)_

---

## ⚠️ STATION HEALTH FLAG: 1 Capture Miss on Record

> **`capture_misses = 1`** — at least one daily snapshot was lost. Data continuity may have a gap. All other health indicators are nominal.

---

## 🔴 Headline Verdict — TEMPEST BEHIND

**Status: TEMPEST BEHIND** (rolling 90-day window, n=78 days, p=0.025 vs NWS)

Tempest is within 3°F on **74%** of days vs NWS's **79%** — statistically behind the best public forecast. The Diebold-Mariano test confirms the gap is significant (p=0.025). With 78 of the 90 days needed for a definitive window verdict, this is no longer noise.

**Advantage-window note (since Aug 1):** Only 23 days in — still "TOO EARLY" for a formal advantage-window verdict (need ~7 more days for a first read, 90 for definitive). Tempest MAE 2.21°F vs NWS 1.75°F over that window; check back as days accrue.

---

## 📊 Standings — 1-Day Lead (rolling 90d, n=78)

| Provider | MAE °F | % Within 3°F | Precip CSI | Brier |
|----------|--------|-------------|-----------|-------|
| **NWS** | **1.96** | **79%** | 0.34 | 0.258 |
| NBM | 2.15 | 73% | 0.33 | 0.258 |
| GFS | 2.18 | 75% | 0.33 | 0.258 |
| ★ **Tempest** | **2.24** | **74%** | **0.52** | **0.206** |
| ECMWF | 2.68 | 64% | 0.65 | 0.181 |

_Tempest trails NWS by 0.28°F MAE and 5 pct-pts on the "within 3°F" metric. However, Tempest leads all public models on **precipitation CSI** (0.52 vs NWS's 0.34) and has the best Brier score of the non-ECMWF models._

**2-Day Lead:** Tempest MAE 2.32°F vs NWS 2.06°F (Tempest 70%, NWS 77%)  
**3-Day Lead:** Tempest MAE 2.36°F vs NWS 2.17°F (Tempest 68%, NWS 75%)

---

## 📈 Weekly MAE Trend — Tempest vs Best Public (NWS)

| Week of | Tempest | NWS | Gap | Note |
|---------|---------|-----|-----|------|
| 2026-07-27 | 2.34°F | 2.04°F | +0.30 | |
| 2026-08-03 | 3.07°F | 1.77°F | +1.30 | ⬆ Tempest rough week |
| 2026-08-10 | **1.29°F** | **1.64°F** | **-0.35** | ✅ **Tempest beat NWS!** |
| 2026-08-17 | 1.77°F | 1.69°F | +0.08 | Nearly tied |

**Trend: Closing.** After a bad week of Aug 3, Tempest has posted two strong weeks. The Aug 10 week saw Tempest actually outperform NWS, and Aug 17 was near-parity. The cumulative deficit is narrowing but the 78-day all-time MAE gap (+0.28°F) requires sustained outperformance to close.

---

## 💥 Biggest Busts (Recent)

| Date | Provider | Variable | Forecast | Actual | Error |
|------|----------|----------|----------|--------|-------|
| 2026-08-19 | ECMWF | High °F | 98°F | 93°F | +5°F |
| 2026-08-18 | ECMWF | High °F | 96°F | 92°F | +4°F |
| 2026-08-21 | GFS | High °F | 88°F | 93°F | -5°F |

_No Tempest busts in the recent record — all busts belong to public models._

---

## 🌧️ Rain Totals (Aug 17–23)

| Date | Tempest Raw | CoCoRaHS Gauge | Flag |
|------|-------------|---------------|------|
| 2026-08-17 | 0.384" | 0.43" | — |
| 2026-08-18 | 0.052" | — | — |
| 2026-08-19 | 0.00" | — | — |
| 2026-08-20 | 0.00" | 0.14" | ⚠️ DISAGREE |
| 2026-08-21 | 0.15" | — | — |
| 2026-08-22 | 0.00" | — | — |
| 2026-08-23 | 0.00" | — | — |

**Aug 20 rain disagreement:** CoCoRaHS recorded 0.14" while Tempest logged 0.00". Could reflect localized precipitation, gauge timing, or a sensor issue. No RainCheck correction available for this date. Three disagree flags in the last 30 days (Aug 11, Aug 14, Aug 20).

---

## 🏥 Station Health

| Metric | Value | Status |
|--------|-------|--------|
| Capture days | 82 | ✅ |
| **Capture misses** | **1** | ⚠️ **FLAG — 1 missed snapshot** |
| Station online streak | 46 days | ✅ |
| Hub online | true | ✅ |
| Last snapshot | 0 hours ago | ✅ |
| Battery volts | 2.66 V | ✅ (above warn threshold) |
| Battery warn flag | false | ✅ |
| Rain sensor OK | true | ✅ |
| CoCoRaHS OK | true | ✅ |
| Sensor faults | null | ℹ️ Not monitored (not "healthy") |

**Battery reference thresholds:** WARN ≤2.40 V · ALERT ≤2.355 V. Current 2.66 V is well clear.  
**Sensor faults = null** means fault monitoring is not enabled, not that faults were checked and found absent.  
**Capture miss flag:** One daily data snapshot was lost somewhere in the 82 capture days. This is worth noting but is not currently impacting streak or continuity.

---

## 📅 Guarantee Timeline

| Milestone | Date | Status |
|-----------|------|--------|
| Advantage window opens | 2026-08-01 | ✅ Open (23 days in) |
| 5-month mark | 2026-10-31 | 68 days away |
| Claim deadline | 2027-01-25 | 154 days away |
| Definitive verdict (n≥90) | ~2026-11-01 | Rolling 90d full by ~Sep 3 |

The rolling 90-day window will be fully within the advantage period around **2026-09-03** (per `diverges_after`). Until then, the rolling verdict reflects pre-window days. The since-Aug-1 window needs **~7 more scored days** for a first informal read.

---

## 📝 Summary

Tempest is statistically behind NWS on temperature accuracy after 78 days (MAE 2.24 vs 1.96°F, p=0.025). The good news: the last two weeks have been Tempest's best stretch yet, including one week where it outright beat NWS. Precipitation detection is a genuine strength (CSI 0.52 vs NWS's 0.34). The advantage window opened Aug 1 — too early for a formal read yet, but the trajectory matters.

Station is healthy. Flag the one capture miss and the Aug 20 rain disagreement for awareness.

_Dashboard: https://damngooddawg.github.io/tempest-forecast-verify/dashboard.html_
