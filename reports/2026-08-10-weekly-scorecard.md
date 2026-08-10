# Tempest Weekly Scorecard — 2026-08-10

> Generated: 2026-08-10 · Data through 2026-08-09 · scores.json generated at 2026-08-10T11:28:13Z

---

## ⚠️ STATION HEALTH — REQUIRES ATTENTION

| Check | Value | Status |
|---|---|---|
| Last snapshot age | 0 h ago | ✅ Current |
| Capture days | 68 days | — |
| **Capture misses** | **1** | **⚠️ FLAG: 1 missed Tempest snapshot in capture window** |
| Station online streak | 32 days | ✅ |
| Hub online | true | ✅ |
| CoCoRaHS OK | true | ✅ |
| Battery voltage | 2.65 V | ✅ (above 2.40 V warn threshold) |
| Battery warn flag | false | ✅ |
| Rain sensor OK | true | ✅ |
| Sensor faults | null | — (not monitored via API; see README) |

> **⚠️ capture_misses = 1**: One irreplaceable Tempest snapshot was missed in the capture window (68 capture days observed vs. expected). A single missed day breaks the station_online_streak at that point and creates a gap in the evidence record. Investigate which date was skipped and whether the GitHub Actions workflow ran that day.

---

## Headline Verdict

| Window | Status | Summary |
|---|---|---|
| **Rolling 90 days** (primary) | 🔴 **TEMPEST BEHIND** | Tempest within 3°F on **71%** of days vs NWS **79%** — behind best public forecast over 64 scored days (DM p=0.0088, statistically significant) |
| Since Aug 1 (guarantee window) | 🟡 **TOO EARLY** | Only **9 scored days** since the guarantee window opened 2026-08-01 — need ~21 more for a first verdict, 90 for a definitive one |
| Last 28 days (trend) | 🔴 Widening gap | Tempest MAE **2.64°F** vs NWS **1.89°F** — the gap is *not* closing |

**Guarantee window opened 2026-08-01.** The advantage-window clock is running but too early to score. The 90-day rolling window — 64 days accumulated since 2026-06-05 — is the current evidence basis. Tempest is statistically behind (p<0.01); the weekly MAE trend is moving in the wrong direction.

---

## Standings — 1-Day Lead (Rolling 90 Days, n=64)

| Rank | Provider | MAE °F | % within 3°F | Precip CSI |
|---|---|---|---|---|
| 1 | **NWS** | **2.02** | **79%** | 0.40 |
| 2 | NBM | 2.24 | 71% | 0.39 |
| 3 | GFS | 2.27 | 73% | 0.39 |
| 4 | **⭐ Tempest** | 2.39 | 71% | **0.60** |
| 5 | ECMWF | 2.65 | 65% | 0.68 |

> Tempest ranks 4th on temperature (MAE, %within3°F) but 2nd on precip occurrence CSI (0.60 vs NWS 0.40), leading NWS on rain detection.

### Standings at 2-Day & 3-Day Lead

| Lead | Provider | MAE °F | % within 3°F |
|---|---|---|---|
| **2-day** | NWS | 2.10 | 77% |
| 2-day | **Tempest** | 2.46 | 67% |
| **3-day** | NWS | 2.20 | 77% |
| 3-day | **Tempest** | 2.47 | 69% |

Tempest is behind NWS at every lead time on temperature accuracy.

---

## Weekly MAE Trend (Tempest vs Best Public — NWS)

| Week | Tempest MAE | NWS MAE | Gap (T−N) |
|---|---|---|---|
| 2026-06-01 | 1.53 | 1.47 | +0.06 |
| 2026-06-08 | 2.32 | 1.84 | +0.48 |
| 2026-06-15 | 2.12 | 2.25 | **−0.13** |
| 2026-06-22 | 2.78 | 2.56 | +0.22 |
| 2026-06-29 | 1.82 | 1.99 | **−0.17** |
| 2026-07-06 | 2.22 | 2.28 | **−0.06** |
| 2026-07-13 | 2.34 | 1.59 | +0.75 |
| 2026-07-20 | 2.82 | 2.16 | +0.66 |
| 2026-07-27 | 2.34 | 2.04 | +0.30 |
| **2026-08-03** | **3.07** | **1.77** | **+1.30 ← widening** |

**Gap is widening.** The most recent week (Aug 3–9) shows Tempest's worst performance of the study: 3.07°F MAE vs NWS's 1.77°F — a 1.30°F deficit, the largest single-week gap recorded. Both Tempest and NBM show a pronounced cold bias this week (Tempest bias −4.39°F, NBM −4.11°F), suggesting a regional pattern but one NWS/GFS handled better.

---

## Biggest Busts (Recent Scoring Window)

| Date | Provider | Variable | Forecast | Actual | Error |
|---|---|---|---|---|---|
| 2026-08-07 | ECMWF | High °F | 82 | 90 | −8 |
| 2026-08-05 | ECMWF | High °F | 82 | 89 | −7 |
| 2026-08-05 | **Tempest** | High °F | 83 | 89 | **−6** |

All three busts are cold misses (forecasting too cool) on high temperatures in early August. ECMWF had back-to-back busts Aug 5–7; Tempest joined the Aug 5 cold bust (−6°F). NWS avoided both dates on the bust list.

---

## Rain Totals (Recent 3 Weeks: 2026-07-20 → 2026-08-09)

| Date | Tempest Raw | CoCoRaHS | Note |
|---|---|---|---|
| 2026-07-21 | 0.019" | — | |
| 2026-07-22 | 0.002" | — | |
| 2026-07-23 | 0.175" | 0.00" | ⚠️ **FLAGGED: disagree** |
| 2026-07-24 | 0.513" | 0.33" | |
| 2026-07-25 | 0.014" | — | |
| 2026-07-28 | 0.847" | 0.72" | |
| 2026-07-29 | 0.465" | — | |
| 2026-08-01 | 0.023" | 0.72" | CoCoRaHS much higher |
| 2026-08-02 | 1.643" | 0.58" | Tempest much higher |
| 2026-08-04 | 0.100" | 0.22" | |
| 2026-08-05 | 0.675" | 0.75" | ✅ Close |
| 2026-08-06 | 0.078" | — | |
| 2026-08-08 | **1.030"** | **0.02"** | ⚠️ Large discrepancy |

**Period totals (Tempest raw):** ~5.58" over 21 days  
**CoCoRaHS (days with readings):** ~3.34" on 8 measured days

Notable discrepancies:
- **2026-07-23**: Tempest 0.175" vs CoCoRaHS 0.00" — formally flagged "disagree"
- **2026-08-01**: Tempest missed most of what CoCoRaHS caught (0.023" vs 0.72")
- **2026-08-08**: Tempest 1.03" vs CoCoRaHS 0.02" — large over-read by Tempest on a likely convective event

Rain comparisons note: `tempest_corrected` = `tempest_raw` for all dates (no RainCheck correction applied in this period). CoCoRaHS coverage is partial (~38% of days).

---

## Guarantee Timeline

| Milestone | Date | Status |
|---|---|---|
| Guarantee window opens | 2026-08-01 | ✅ **Window is open** (9 days in) |
| 5-month scoring mark | 2026-10-31 | ⏳ 82 days away |
| Claim deadline | 2027-01-25 | ⏳ 168 days away |

The guarantee advantage window opened on schedule Aug 1. The scoring clock is running. Current rolling-90 verdict (TEMPEST BEHIND, p=0.0088) is **unfavorable** and the trend is worsening. Tempest needs to close the gap substantially over the coming months to be in contention by Oct 31.

---

## NBM Twin Analysis (Context)

All-time correlation between Tempest and NBM forecasts: **r=0.97** (nearly identical signals). All-time bias: Tempest −1.89°F, NBM −1.96°F. Recent 28-day bias: Tempest −3.14°F, NBM −2.92°F. Both are running cold; Tempest is slightly colder. This high correlation suggests Tempest's forecast is substantially derived from or highly aligned with the NBM model — the "hyperlocal advantage" may be limited in practice.

---

*Dashboard: https://damngooddawg.github.io/tempest-forecast-verify/dashboard.html*  
*Scoring: 1-day lead MAE, %within 3°F, Diebold-Mariano (Harvey-Leybourne-Newbold correction, t(n−1)). n=64 days since 2026-06-05. Significance requires n≥30; definitive verdict at n≥90.*
