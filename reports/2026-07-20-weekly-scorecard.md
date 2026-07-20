# Tempest 'Better Forecast Guarantee' — Weekly Scorecard
**Date:** 2026-07-20 | **scores.json generated:** 2026-07-19T11:34:02Z (≈24 h ago — staleness OK)

---

## ⚠️ STATION HEALTH ALERT — 1 CAPTURE MISS

> **capture_misses = 1** — one day in the observation window has no irreplaceable Tempest snapshot. This breaks continuity in the evidence record and means that day cannot be scored.

---

## Headline Verdict

**Status: TIED** (n = 42 days; need ≥ 90 for a definitive verdict)

Tempest is within 3°F on **71%** of days vs NWS's **74%** — statistically tied with the best public forecast so far.  
_(Diebold-Mariano p = 0.1858 vs NWS; p > 0.05 means the difference is not yet statistically significant.)_

⏳ **Guarantee window opens in 12 days: 2026-08-01**

---

## Standings — 1-Day Lead

| Provider | MAE (°F) | % within 3°F | Precip CSI |
|---|---|---|---|
| NWS | 2.05 | 74% | 0.38 |
| NBM | 2.14 | 73% | 0.36 |
| **★ Tempest** | **2.25** | **71%** | **0.65** |
| GFS | 2.35 | 70% | 0.36 |
| ECMWF | 2.51 | 68% | 0.75 |

_Tempest ranks 3rd on temperature (MAE/% within 3°F) but 2nd on precipitation CSI at 1-day lead._

### 2-Day Lead

| Provider | MAE (°F) | % within 3°F | Precip CSI |
|---|---|---|---|
| NWS | 2.13 | 74% | 0.38 |
| **★ Tempest** | **2.38** | **68%** | **0.33** |
| NBM | 2.37 | 65% | 0.43 |
| ECMWF | 2.46 | 62% | 0.54 |
| GFS | 2.60 | 68% | 0.43 |

### 3-Day Lead

| Provider | MAE (°F) | % within 3°F | Precip CSI |
|---|---|---|---|
| NWS | 2.35 | 75% | 0.33 |
| **★ Tempest** | **2.44** | **68%** | **0.27** |
| NBM | 2.45 | 65% | 0.24 |
| GFS | 2.88 | 69% | 0.24 |
| ECMWF | 2.92 | 52% | 0.44 |

---

## Weekly MAE Trend — Tempest vs NWS (Best Public)

| Week of | Tempest MAE | NWS MAE | Gap (T − NWS) |
|---|---|---|---|
| 2026-06-01 | 1.53 | 1.47 | +0.06 |
| 2026-06-08 | 2.32 | 1.84 | +0.48 |
| 2026-06-15 | 2.12 | 2.25 | **−0.13** ✓ |
| 2026-06-22 | 2.78 | 2.56 | +0.22 |
| 2026-06-29 | 1.82 | 1.99 | **−0.17** ✓ |
| 2026-07-06 | 2.22 | 2.28 | **−0.06** ✓ |
| 2026-07-13 | 2.57 | 1.62 | +0.95 ← worst week |

**Assessment:** No clear convergence trend. Tempest bested or matched NWS in 3 of the last 7 weeks, but the week of 7/13 was Tempest's worst margin yet (NWS outperformed by 0.95°F). Mixed.

---

## Biggest Busts (Recent)

| Date | Provider | Variable | Forecast | Actual | Error |
|---|---|---|---|---|---|
| 2026-07-13 | ECMWF | High temp | 77°F | 86°F | −9°F |
| 2026-07-13 | NBM | High temp | 80°F | 86°F | −6°F |
| 2026-07-15 | **Tempest** | High temp | 84°F | 90°F | **−6°F** |

_All three busts underpredicted heat. Tempest's 7/15 miss contributed to its weaker week-of-7/13 stats._

---

## Rain Totals (Tempest vs CoCoRaHS)

| Date | Tempest Raw (in) | CoCoRaHS (in) | Flag |
|---|---|---|---|
| 2026-06-27 | 0.175 | 0.17 | — |
| 2026-06-29 | 0.532 | 0.11 | _(T ~5× high)_ |
| 2026-07-06 | 0.000 | **0.40** | ⚠️ **DISAGREE** |
| 2026-07-09 | 0.032 | — | — |
| 2026-07-10 | 0.231 | — | — |
| 2026-07-11 | 0.251 | 0.31 | — |
| 2026-07-12 | 1.112 | 0.80 | _(T 39% high)_ |
| 2026-07-13 | 1.024 | 1.57 | _(T 35% low)_ |
| 2026-07-14 | 0.164 | 0.34 | _(T 52% low)_ |
| 2026-07-18 | 0.510 | — | — |

**Notable:** The 2026-07-06 "disagree" flag — Tempest recorded zero while CoCoRaHS caught 0.40" — is the most significant rain-sensor discrepancy to date. The heavy-rain events of 7/12–7/13 show bidirectional errors (over then under), possibly from wind-driven splash / drainage effects. Rain-sensor accuracy is a known Tempest limitation.

---

## Station Health

| Item | Value | Status |
|---|---|---|
| scores.json age | ~24 h | ✅ OK (< 48 h) |
| capture_days | 46 | — |
| **capture_misses** | **1** | ⚠️ **FLAG — 1 day unrecoverable** |
| station_online_streak | 10 days | ✅ |
| hub_online | true | ✅ |
| battery_volts | 2.65 V | ✅ OK (warn ≤ 2.40 V, alert ≤ 2.355 V) |
| battery_warn | false | ✅ |
| rain_sensor_ok | true | ✅ |
| cocorahs_ok | true | ✅ |
| last_snapshot_hours_ago | 0 | ✅ Fresh |
| sensor_faults | null | ℹ️ Not monitored (diagnostics endpoint 401) |
| rssi / hub_rssi | null | ℹ️ Not monitored |

> **sensor_faults = null** does not mean healthy — it means the `/diagnostics` endpoint is inaccessible with a personal token. Sensor fault status is unknown.

---

## Guarantee Timeline

| Milestone | Date | Status |
|---|---|---|
| **Window Opens** | **2026-08-01** | **12 days away** |
| 5-Month End | 2026-10-31 | — |
| Claim Deadline | 2027-01-25 | — |

Current n = 42 days (≥ 30 for first read; 90 needed for a definitive verdict). Scoring will count from the window-open date.

---

_Dashboard: https://damngooddawg.github.io/tempest-forecast-verify/dashboard.html_
_Source: DamnGoodDawg/tempest-forecast-verify_
