# Tempest Weekly Scorecard (2026-11-23)

*Source: `scores.json` generated 2026-11-22 18:34 UTC (latest capture: data/2026-11-22). Station: Statham, GA.*

## 🔋 Station Health Summary
**The station is healthy. One standing flag, no new problems:**
- **⚠️ `capture_misses = 1`:** This is still the known **2026-07-09** gap. There were **no new misses**: every data/ folder from 06-04 through 11-22 is present except 07-09.
- ✅ **`cocorahs_ok` is back to true.** Last week's flag has cleared: the GA-OC-20 gauge reported 0.20" for Nov 21.
- Battery 2.63 V (fine), hub online, 136-day online streak. Anchor monitor: **OK** (0 watches, 0 faults, 175 days).

## Headline Verdict: **TEMPEST BEHIND**
Over the last 90 days (n_days = 90), Tempest is within 3°F on **63%** of days. The best public forecast, **NWS**, is within 3°F on **76%**. The 90-day 1-day MAE is Tempest 2.55°F vs NWS 2.13°F. The Diebold-Mariano p-value is **~0.000**, so the gap is statistically significant. The verdict has been TEMPEST BEHIND on every daily check since 2026-08-08.

## Standings: 1-Day Lead (all-time, about 167 days)
| Provider | MAE °F | % within 3°F | Precip CSI |
|---|---|---|---|
| Dawg (house, n=66) | 2.01 | 77% | 0.60 |
| Blend (house) | 2.05 | 77% | 0.60 |
| NWS | 2.05 | 78% | 0.39 |
| NBM | 2.29 | 69% | 0.32 |
| **▶ Tempest** | **2.41** | **68%** | **0.51** |
| GFS | 2.43 | 69% | 0.32 |
| ECMWF | 2.99 | 55% | 0.64 |

On the rolling 90-day window, Tempest's numbers are 2.55°F MAE, 63% within 3°F and 0.48 CSI. NWS's are 2.13°F, 76% and 0.50. Tempest loses to NWS on temperature, on precip occurrence (CSI) and on PoP calibration (Brier 0.089 vs 0.082).

## Weekly MAE Trend: Tempest vs NWS (best public)
| Week of | Tempest | NWS | Gap |
|---|---|---|---|
| 10-12 | 3.77 | 2.91 | +0.86 |
| 10-19 | 3.56 | 2.32 | +1.24 |
| 10-26 | 2.04 | 1.89 | +0.15 |
| 11-02 | 2.70 | 2.79 | **−0.09** |
| 11-09 | 3.06 | 3.31 | **−0.25** |
| 11-16* | 2.80 | 2.13 | +0.67 |

*The 11-16 week is partial (through 11-21). **The gap is not closing.** Tempest beat NWS for two weeks running, then fell back behind this week. The weekly n is about 7 days, so these numbers only describe what happened; significance comes from the cumulative 90-day window. Tempest still runs cold (28-day bias −2.2°F), though it is now less cold than NBM (−2.9°F).

## Biggest Busts (this week)
- 11-21 GFS high: forecast 67°F, actual 61°F (+6)
- 11-19 NBM high: forecast 65°F, actual 70°F (−5)
- 11-17 NBM high: forecast 61°F, actual 67°F (−6)

Tempest had no busts in the top list this week.

## Rain Totals (rain days in November)
| Date | Tempest raw | RainCheck | CoCoRaHS gauge |
|---|---|---|---|
| 11-01 | 0.155" | 0.155" | — |
| 11-04 | 0.282" | 0.282" | 0.26" |
| 11-05 | 0.004" | 0.004" | 0.05" ⚠️ disagree |
| 11-21 | 0.101" | 0.101" | 0.20" |

Nov 7–20 was completely dry. On 11-21, Tempest caught about half of what the gauge measured (0.10" vs 0.20"). That fits the known under-catch on light events, and RainCheck applied no correction.

## 🔋 STATION HEALTH
| Metric | Value | Status |
|---|---|---|
| Capture days | 172 | — |
| **Capture misses** | **1** (2026-07-09) | **⚠️ FLAG: known and unchanged, no new misses** |
| Last snapshot | 0 h ago at build (scores.json about 19 h old at report time) | ✅ (< 48 h) |
| Station online streak | 136 days | ✅ (was 129 last week) |
| Hub online | true | ✅ |
| Battery | 2.63 V, battery_warn = false | ✅ (WARN at ≤ 2.40, ALERT at ≤ 2.355) |
| CoCoRaHS feed | cocorahs_ok = true | ✅ (recovered since last week) |
| Rain sensor | ok | ✅ |
| Sensor faults | null | ⚪ not monitored, so this does not mean "healthy" |
| RSSI / hub RSSI | null | ⚪ not monitored |

Anchor check (health.json): overall OK. The 7-day temperature offsets are KWDR +2.03, KAHN −0.35 and WATUGA +2.29°F, all inside the normal band.

## Guarantee Timeline
- Window opened: **2026-08-01** ✅
- 5-month mark: **2026-10-31** ✅ (passed; Tempest was behind)
- **Claim deadline: 2027-01-25**, 63 days from today
- With n = 90, significant results (p ≈ 0) and a performance gap that isn't closing, the data supports a Better Forecast Guarantee claim. File well before the deadline.

Dashboard: https://damngooddawg.github.io/tempest-forecast-verify/dashboard.html
