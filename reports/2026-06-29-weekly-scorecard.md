# Tempest Weekly Scorecard — 2026-06-29

**Status: TOO EARLY** — 23 scored days so far; ~7 more needed for a first verdict (~90 for a
definitive one). Capture is running cleanly; projected first-look verdict ~early July 2026.
Significance testing (Diebold-Mariano) requires ≥ 30 days; weekly n is small and descriptive only.

---

## Headline Verdict

**TOO EARLY (n = 23 scored days; best public = NBM)**

Only 23 of the ~30 days needed for a first-look verdict have been scored. The tracking system
has been capturing data daily since 2026-05-31 with zero misses, and the Tempest station is
online and healthy. All numbers below are directional — no statistical conclusions yet.

> `scores.json` generated 2026-06-28T12:00:21Z (~24 h ago — within the 48-hour staleness limit).

---

## Standings at 1-Day Lead (n = 23 days)

| Provider        | MAE (°F) | % Within 3°F | Precip CSI | Precip Brier |
|-----------------|----------|--------------|------------|--------------|
| NBM             | 2.05     | 76%          | 0.36       | 0.184        |
| NWS             | 2.13     | 76%          | 0.36       | 0.194        |
| **Tempest ★**   | **2.24** | **70%**      | **0.75**   | **0.141**    |
| GFS             | 2.35     | 70%          | 0.36       | 0.184        |
| ECMWF           | 2.53     | 70%          | 0.85       | 0.090        |

_Lower MAE/Brier = better; higher % within 3°F / CSI = better. ★ = subject under test._

**Notes:** At 1-day lead, Tempest temperature MAE (2.24°F) trails NBM (2.05°F) and NWS (2.13°F)
by a small margin, but leads on precipitation skill (CSI 0.75 vs NBM/NWS 0.36) and Brier score
(0.141 vs NBM 0.184). ECMWF shows the best CSI (0.85) but worst temperature MAE.

### 2-Day Lead

| Provider   | MAE (°F) | % Within 3°F | Precip CSI |
|------------|----------|--------------|------------|
| NWS        | 2.18     | 75%          | 0.46       |
| NBM        | 2.38     | 66%          | 0.55       |
| Tempest ★  | 2.47     | 64%          | 0.36       |
| ECMWF      | 2.54     | 59%          | 0.46       |
| GFS        | 3.00     | 66%          | 0.55       |

### 3-Day Lead

| Provider   | MAE (°F) | % Within 3°F | Precip CSI |
|------------|----------|--------------|------------|
| NWS        | 2.42     | 81%          | 0.46       |
| Tempest ★  | 2.57     | 64%          | 0.33       |
| NBM        | 2.61     | 64%          | 0.27       |
| ECMWF      | 2.83     | 55%          | 0.39       |
| GFS        | 3.34     | 62%          | 0.27       |

---

## Weekly MAE Trend (1-Day Lead, Tempest vs NBM)

| Week of    | Tempest MAE | NBM MAE | Gap (T−NBM) |
|------------|-------------|---------|-------------|
| 2026-06-01 | 1.53°F      | 1.38°F  | +0.15°F     |
| 2026-06-08 | 2.32°F      | 2.16°F  | +0.16°F     |
| 2026-06-15 | 2.12°F      | 1.80°F  | +0.32°F     |
| 2026-06-22 | 2.65°F      | 2.55°F  | +0.10°F     |

_Positive gap = Tempest worse than NBM._

Both Tempest and NBM saw higher MAE in the most recent week (warm-season variability). The gap
narrowed from +0.32°F (week of 6/15) to +0.10°F (week of 6/22) — but n is far too small to
read a closing trend. All values are directional only.

---

## Biggest Busts (Errors ≥ 5°F)

All three occurred on **2026-06-25** (high temperature, actual = 84°F):

| Provider | Forecast | Actual | Error |
|----------|----------|--------|-------|
| ECMWF    | 92°F     | 84°F   | −8°F  |
| NWS      | 90°F     | 84°F   | −6°F  |
| GFS      | 89°F     | 84°F   | −5°F  |

**Tempest did NOT appear in the busts list on 2026-06-25** — public models significantly
overforecast that day's high while Tempest stayed closer to the observed 84°F.

---

## Rain Totals (Tempest vs CoCoRaHS gauge)

Entries where CoCoRaHS data is available:

| Date       | Tempest Raw (in) | CoCoRaHS (in) | Note              |
|------------|------------------|---------------|-------------------|
| 2026-06-08 | 0.052            | 0.07          | Close             |
| 2026-06-09 | 0.462            | 0.17          | Tempest reads high|
| 2026-06-14 | 0.555            | 0.37          | Tempest reads high|
| 2026-06-15 | 0.000            | 0.04          | ⚠ DISAGREE flag   |
| 2026-06-16 | 0.149            | 0.47          | Tempest reads low |
| 2026-06-18 | 1.271            | 1.47          | Close             |

Recent captures (no CoCoRaHS match yet): 0.234" (2026-06-22), 0.068" (2026-06-23),
0.175" (2026-06-27).

> ⚠ **`cocorahs_ok: false`** — independent CoCoRaHS reports are currently unavailable/unmatched
> for the most recent observation window. Rain cross-check is operating with reduced coverage.
> The one historical "disagree" flag (2026-06-15) was a trace-level difference (0.0" vs 0.04").

---

## Station Health

| Metric                     | Value              | Status  |
|----------------------------|--------------------|---------|
| Overall health             | OK                 | ✓       |
| Hub online                 | true               | ✓       |
| Station online streak      | 25 days            | ✓       |
| Capture days               | 25                 | ✓       |
| Capture misses             | 0                  | ✓       |
| Last snapshot age          | 0 hours ago        | ✓       |
| Battery voltage            | 2.65 V             | ✓       |
| Battery warn flag          | false              | ✓       |
| Rain sensor                | OK                 | ✓       |
| CoCoRaHS cross-check       | **false** ⚠        | WARNING |
| Sensor faults (RSSI)       | null               | Not monitored (no local UDP; not "healthy") |
| Active watches             | 0                  | ✓       |
| Confirmed faults           | 0                  | ✓       |
| Days monitored (anchors)   | 28                 | ✓       |

**Anchor comparison (7-day offsets, Tempest − anchor):**

| Variable    | vs KWDR   | vs KAHN  | vs WATUGA | State |
|-------------|-----------|----------|-----------|-------|
| Temperature | +1.21°F   | +0.05°F  | −0.88°F   | OK    |
| Humidity    | −0.66 pts | +0.36 pts| +1.25 pts | OK    |
| Pressure    | −4.55 mb  | −3.62 mb | —         | OK    |
| Wind        | —         | +0.35 mph| −3.49 mph | OK (trend-only) |
| Rain        | —         | —        | CoCoRaHS  | OK    |

All anchor offsets are within their normal bands. No flags active.

> `sensor_faults: null` — sensor diagnostics and RSSI are not accessible via the personal API
> token (the `/diagnostics` endpoint returns 401). This means "not monitored," not "healthy."

---

## Guarantee Timeline

| Milestone               | Date         |
|-------------------------|--------------|
| Guarantee window opens  | 2026-08-01   |
| 5-month mark            | 2026-10-31   |
| Claim deadline          | 2027-01-25   |
| Projected first verdict | ~early July 2026 (n ≥ 30 scored days) |
| Projected definitive verdict | ~late August 2026 (n ≥ 90 scored days) |

_Install date: 2026-05-31. Station has been online every day with zero capture misses._

---

_Dashboard: https://damngooddawg.github.io/tempest-forecast-verify/dashboard.html_
_Generated by tempest-weekly-scorecard routine · 2026-06-29_
