# Tempest Weekly Scorecard — 2026-07-06

**Status: TIED** — 30 scored days; Tempest is within 3°F on 73% of days vs NWS's 75% —
statistically tied with the best public forecast (DM p = 0.355, n = 30). ≥ 90 days needed for a
definitive verdict; this is the first-look result, activated this week as n crossed 30.
Guarantee window opens 2026-08-01.

> `scores.json` generated 2026-07-05T11:50:05Z (~24 h ago — within the 48-hour staleness limit).

---

## Headline Verdict

**TIED (n = 30 scored days; best public = NWS; DM p = 0.355)**

Tempest is within 3°F on 73% of days vs NWS's 75% — a 2-percentage-point gap that is not
statistically significant at this sample size (Diebold-Mariano HLN-corrected p = 0.355; p > 0.05
means we cannot distinguish Tempest from the best public model). This is the first-look verdict,
triggered as n reached 30. A definitive verdict requires ≥ 90 days (projected ~late August 2026).
Tempest's precip CSI (0.64) noticeably exceeds the public models at 1-day lead.

---

## Standings at 1-Day Lead (n = 30 days)

| Provider        | MAE (°F) | % Within 3°F | Precip CSI | Precip Brier |
|-----------------|----------|--------------|------------|--------------|
| NWS             | 2.05     | 75%          | 0.31       | 0.194        |
| NBM             | 2.06     | 77%          | 0.31       | 0.189        |
| **Tempest ★**   | **2.20** | **73%**      | **0.64**   | **0.151**    |
| GFS             | 2.37     | 70%          | 0.31       | 0.189        |
| ECMWF           | 2.60     | 65%          | 0.77       | 0.110        |

### 2-Day Lead

| Provider        | MAE (°F) | % Within 3°F | Precip CSI | Precip Brier |
|-----------------|----------|--------------|------------|--------------|
| NWS             | 2.09     | 76%          | 0.39       | 0.181        |
| **Tempest ★**   | **2.42** | **69%**      | **0.31**   | **0.198**    |
| NBM             | 2.36     | 67%          | 0.46       | 0.173        |
| ECMWF           | 2.46     | 60%          | 0.44       | 0.195        |
| GFS             | 2.78     | 69%          | 0.46       | 0.173        |

### 3-Day Lead

| Provider        | MAE (°F) | % Within 3°F | Precip CSI | Precip Brier |
|-----------------|----------|--------------|------------|--------------|
| NWS             | 2.22     | 84%          | 0.39       | 0.203        |
| **Tempest ★**   | **2.37** | **70%**      | **0.29**   | **0.216**    |
| NBM             | 2.42     | 66%          | 0.23       | 0.209        |
| ECMWF           | 2.79     | 55%          | 0.38       | 0.189        |
| GFS             | 3.02     | 66%          | 0.23       | 0.209        |

### Blended (1–3 Day Average)

| Provider        | MAE (°F) | % Within 3°F | Precip CSI | Precip Brier |
|-----------------|----------|--------------|------------|--------------|
| NWS             | 2.12     | 78%          | 0.36       | 0.193        |
| NBM             | 2.27     | 70%          | 0.33       | 0.190        |
| **Tempest ★**   | **2.33** | **71%**      | **0.41**   | **0.188**    |
| ECMWF           | 2.61     | 60%          | 0.53       | 0.164        |
| GFS             | 2.72     | 68%          | 0.33       | 0.190        |

*Tempest ranks 3rd on temperature at all leads; its CSI advantage (precip) is a bright spot.*

---

## Weekly MAE Trend — Tempest vs NWS (Best Public)

| Week of     | Tempest MAE | NWS MAE | Gap (T − NWS) |
|-------------|-------------|---------|----------------|
| 2026-06-01  | 1.53°F      | 1.47°F  | +0.06°F        |
| 2026-06-08  | 2.32°F      | 1.84°F  | +0.48°F        |
| 2026-06-15  | 2.12°F      | 2.25°F  | **−0.13°F** ← Tempest led |
| 2026-06-22  | 2.78°F      | 2.56°F  | +0.22°F        |
| 2026-06-29  | 1.82°F      | 1.77°F  | +0.05°F        |

The gap is oscillating rather than trending. The most recent week (Jun 29) shows near-parity
(0.05°F). Tempest outright led in the week of Jun 15. No clear closing or diverging pattern at n = 5 weeks.

---

## Biggest Busts (≥ 4°F off)

| Date       | Provider | Variable | Forecast | Actual | Error |
|------------|----------|----------|----------|--------|-------|
| 2026-07-02 | ECMWF    | High     | 93°F     | 98°F   | −5°F  |
| 2026-07-03 | GFS      | High     | 100°F    | 95°F   | +5°F  |
| 2026-07-04 | GFS      | High     | 99°F     | 95°F   | +4°F  |

All three busts were temperature highs around the July 4th holiday heat event. Tempest had no
recorded busts in this period.

---

## Rain Totals — Tempest vs CoCoRaHS (Days With Both Readings)

| Date       | Tempest Raw | CoCoRaHS | Note               |
|------------|-------------|----------|--------------------|
| 2026-06-14 | 0.555"      | 0.37"    |                    |
| 2026-06-15 | 0.000"      | 0.04"    | ⚑ DISAGREE flagged |
| 2026-06-16 | 0.149"      | 0.47"    |                    |
| 2026-06-18 | 1.271"      | 1.47"    |                    |
| 2026-06-27 | 0.175"      | 0.17"    | ✓ Close            |
| 2026-06-29 | 0.532"      | 0.11"    |                    |

**Days-with-both totals:** Tempest 2.68" vs CoCoRaHS 2.63" — close in aggregate.
One DISAGREE flag (Jun 15: Tempest missed 0.04" trace). Notable discrepancies on Jun 16
(T under-reports) and Jun 29 (T over-reports vs gauge) but no sustained drift pattern.
CoCoRaHS coverage is sparse; many rainy days have no gauge comparison.

---

## Station Health

| Metric                  | Value         | Status   |
|-------------------------|---------------|----------|
| Capture streak          | 32 days       | ✓ OK     |
| Station online streak   | 32 days       | ✓ OK     |
| Hub online              | true          | ✓ OK     |
| Last snapshot age       | ~24 h ago     | ✓ OK     |
| Capture misses          | 0             | ✓ OK     |
| Battery voltage         | 2.64 V        | ✓ OK     |
| Battery warn flag       | false         | ✓ OK     |
| Rain sensor             | OK            | ✓ OK     |
| CoCoRaHS feed           | OK            | ✓ OK     |
| Sensor faults           | null          | (not monitored via this path — see README) |
| RSSI / Hub RSSI         | null          | (not captured — see README)                |

**All station health indicators are nominal.** No flags, no warnings. Battery at 2.64 V is
well above the 2.40 V warning threshold. Snapshot is current. 32-day clean capture streak.

*Note: sensor_faults = null means sensor-fault diagnostics are not available via the personal token API path; this is by design, not an indication of health.*

---

## Guarantee Timeline

| Milestone                  | Date         | Days Away |
|----------------------------|--------------|-----------|
| Guarantee window opens     | 2026-08-01   | 26 days   |
| 5-month scoring period     | 2026-10-31   | 117 days  |
| Claim submission deadline  | 2027-01-25   | 203 days  |
| Definitive verdict (≥ 90 d)| ~2026-08-29  | ~54 days  |

The guarantee window opens in 26 days. Current verdict (TIED, n = 30) is inconclusive — the
sample is exactly at the minimum for a first-look result, and 60 more days are needed before the
test has enough power to issue a definitive ruling. Keep capturing daily.

---

*Report generated 2026-07-06 | Dashboard: https://damngooddawg.github.io/tempest-forecast-verify/dashboard.html*
