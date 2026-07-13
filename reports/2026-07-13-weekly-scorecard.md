# Tempest Forecast Verify — Weekly Scorecard
**Date:** 2026-07-13 | **scores.json generated:** 2026-07-12T11:34:51Z (< 48 h ✓)

---

## ⚠ STATION HEALTH ALERT — READ FIRST

| Check | Value | Status |
|---|---|---|
| Capture misses (gaps in Tempest snapshot record) | **1** | **FLAG — 1 irreplaceable snapshot missing (2026-07-09)** |
| Station online streak | 3 days | Note — streak reset; gap on 2026-07-09 |
| Hub online | true | OK |
| Last snapshot age | 0 h | OK (fresh) |
| Battery voltage | 2.66 V | OK (warn threshold ≤ 2.40 V) |
| Rain sensor | OK | OK |
| CoCoRaHS cross-check | OK | OK |
| Sensor faults | null | Not monitored via this pipeline (personal token, no /diagnostics) |

> **Capture miss on 2026-07-09:** The daily workflow did not produce a Tempest snapshot for that date. This is the single irreplaceable data point lost so far — Tempest's own forecast cannot be recovered retroactively. `station_online_streak` reset to 3. The gap also flags in `capture_misses=1`. No other infrastructure issues are indicated (hub is online, battery healthy, last snapshot is fresh).
>
> **Rain discrepancy flag (2026-07-06):** Tempest raw = 0.00 in, CoCoRaHS = 0.40 in — `flag: "disagree"`. Tempest missed a significant rain event. Also note 2026-06-29: Tempest raw 0.532 in vs CoCoRaHS 0.11 in (large over-read, no formal flag applied by pipeline). These two incidents are the rain record's main anomalies to date.

---

## Headline Verdict

| | |
|---|---|
| **Status** | **TIED** |
| **n_days scored** | 35 |
| **Best public** | NBM |
| **DM p-value (vs NBM)** | 0.0949 (not significant — cannot reject parity at 0.05) |

> Tempest is within 3°F on **73%** of days vs NBM's **74%** — statistically tied with the best public forecast. At 35 days we have enough for a first-look verdict but the 90-day threshold for a definitive result is still ahead (~55 more days, projected ~mid-September 2026). Guarantee **window opens in 19 days (2026-08-01)**.

---

## Standings — 1-Day Lead

| Provider | MAE °F | % within 3°F | Precip CSI |
|---|---|---|---|
| NBM | 2.08 | 74% | 0.29 |
| NWS | 2.12 | 71% | 0.29 |
| **Tempest ★** | **2.19** | **73%** | **0.67** |
| GFS | 2.41 | 69% | 0.29 |
| ECMWF | 2.52 | 67% | 0.81 |

**Tempest's standout metric:** Precipitation CSI of **0.67** vs 0.29 for both NBM and NWS — more than double the precip-detection skill. The rain discrepancy events above are worth watching to see if they erode that lead.

### 2-Day Lead

| Provider | MAE °F | % within 3°F | Precip CSI |
|---|---|---|---|
| NWS | 2.17 | 72% | 0.29 |
| NBM | 2.34 | 65% | 0.35 |
| **Tempest ★** | **2.35** | **69%** | **0.23** |
| ECMWF | 2.51 | 60% | 0.52 |
| GFS | 2.69 | 69% | 0.35 |

### 3-Day Lead

| Provider | MAE °F | % within 3°F | Precip CSI |
|---|---|---|---|
| NWS | 2.34 | 76% | 0.28 |
| **Tempest ★** | **2.42** | **68%** | **0.21** |
| NBM | 2.42 | 65% | 0.17 |
| ECMWF | 2.96 | 51% | 0.41 |
| GFS | 3.00 | 66% | 0.17 |

At 3-day lead Tempest ties NBM on MAE and edges it on %within3°F — a notably strong showing at extended range.

---

## Weekly MAE Trend — Tempest vs NBM (Best Public)

| Week of | Tempest MAE | NBM MAE | Gap (T−NBM) |
|---|---|---|---|
| 2026-06-01 | 1.53 | 1.38 | +0.15 (NBM better) |
| 2026-06-08 | 2.32 | 2.16 | +0.16 (NBM better) |
| 2026-06-15 | 2.12 | 1.80 | +0.32 (NBM better) |
| 2026-06-22 | 2.78 | 2.66 | +0.12 (NBM better, gap narrowing) |
| 2026-06-29 | **1.82** | **1.96** | **−0.14 (Tempest better)** |
| 2026-07-06 | 2.22 | 2.14 | +0.08 (nearly tied) |

**Trend:** Tempest started ~0.15–0.32 MAE behind NBM in early June; the gap has narrowed consistently over six weeks, with Tempest actually outperforming NBM the week of Jun 29. The most recent week (Jul 6) shows near-parity (+0.08). Closing trajectory is positive.

---

## Biggest Busts (Past 2 Weeks)

| Date | Provider | Variable | Forecast | Actual | Error |
|---|---|---|---|---|---|
| 2026-07-11 | NWS | High temp | 92°F | 87°F | +5°F |
| 2026-07-11 | GFS | High temp | 91°F | 87°F | +4°F |
| 2026-07-03 | GFS | High temp | 100°F | 95°F | +5°F |

**No Tempest busts recorded in this period.** Both public-model busts involved high-temperature over-forecasting during the hot stretch (Jul 3 and Jul 11).

---

## Rain Totals (Tempest Raw vs CoCoRaHS)

*Days with any precipitation or a CoCoRaHS report (last ~3 weeks):*

| Date | Tempest raw (in) | CoCoRaHS (in) | Flag |
|---|---|---|---|
| 2026-06-22 | 0.234 | — | — |
| 2026-06-23 | 0.068 | — | — |
| 2026-06-27 | 0.175 | **0.17** | — (good match) |
| 2026-06-29 | **0.532** | **0.11** | ⚠ large over-read (4.8×) |
| 2026-06-30 | 0.070 | — | — |
| 2026-07-04 | 0.002 | — | — |
| 2026-07-05 | 0.023 | — | — |
| 2026-07-06 | **0.000** | **0.40** | **⛔ DISAGREE — Tempest missed 0.40 in** |
| 2026-07-09 | — | — | **Snapshot missing** |
| 2026-07-10 | 0.231 | — | — |
| 2026-07-11 | 0.251 | — | — |

*Note: "RainCheck" corrected column equals raw in all displayed records (no correction applied by pipeline to date).*

Two notable discrepancies: Jun 29 (Tempest over-read ~5×) and Jul 6 (Tempest missed 0.40 in entirely). Jun 27 shows good agreement (0.175 vs 0.17 in). CoCoRaHS reports are sparse; most days lack an independent gauge reading.

---

## Guarantee Timeline

| Milestone | Date | Days Away |
|---|---|---|
| **Guarantee window opens** | 2026-08-01 | **19 days** |
| 5-month scoring mark | 2026-10-31 | 110 days |
| Claim deadline | 2027-01-25 | 196 days |

90-day threshold for a **definitive** verdict (per methodology): ~mid-September 2026.

---

*Dashboard: https://damngooddawg.github.io/tempest-forecast-verify/dashboard.html*
*Scores generated: 2026-07-12T11:34:51Z | Install date: 2026-05-31 | n_days scored: 35 | Capture days: 39 | Capture misses: 1*
