# Tempest Forecast Verify

A daily automated check of whether a [WeatherFlow Tempest](https://weatherflow.com/tempest-weather-system/)
weather station's forecast for **Statham, GA** is actually more accurate than the public
forecasts — NWS, NBM, ECMWF, and GFS — scored against observed conditions.

This is the verification layer behind WeatherFlow's *Better Forecast Guarantee*: keep an
honest, timestamped, tamper-evident record of forecast accuracy and let the numbers decide.

## How it works

A GitHub Actions job runs once a day (cron `23 10 * * *`, i.e. 10:23 UTC ≈ 06:23 ET — moved
off the congested top-of-hour, where runs had been drifting 1–4 h late) and:

1. **Captures** (`capture.py`) each provider's forecast into `data/YYYY-MM-DD/`:
   - `tempest.json` — Tempest `better_forecast` (the subject under test). Irreplaceable: it has no public archive.
   - `nws.json` — the official National Weather Service gridpoint forecast.
   - `openmeteo.json` — GFS / ECMWF / NBM via Open-Meteo.
   - `tempest_station_obs.json` — the current station observation (current conditions + yesterday's raw/corrected daily rain totals).
   - `tempest_device_yesterday.json` — yesterday's per-minute device observations: the temperature ground truth (daily high/low) plus battery voltage.
   - `cocorahs.json` — nearby CoCoRaHS gauge report (independent precip-amount truth).
2. **Scores** (`extract.py` → `verify.py`) every snapshot and writes `scores.json`:
   mean absolute error and % within 3 °F on temperature, precip-occurrence CSI, PoP Brier
   score, and a paired Diebold-Mariano significance test — at 1-, 2-, 3-day and blended leads.
3. **Checks station health** (`health.py`): compares the Tempest daily aggregates against
   three independent verified anchors and writes `health.json` + `anchors.csv`. On a newly
   opened flag it queues a one-time warning email, sent by `notify.py`.
4. **Publishes** a static dashboard (`dashboard.html` + `scores.json` + `health.json`) via
   GitHub Pages — a two-tab page: **Guarantee Scoreboard** and **Station Health**.

> Station/hub sensor-fault flags and RSSI are **not** captured here: `/diagnostics` returns 401
> for personal tokens and the WebSocket never delivers `device_status` to them. Those live only
> on the local UDP broadcast — see the separate `tempest-local` listener.

Until enough days accrue, the verdict reads **TOO EARLY** — by design.

## Files

| File | Role |
|---|---|
| `capture.py` | Daily snapshot job. Standard library only. Fails loud if the Tempest capture is missed. |
| `extract.py` | Reads snapshots → scores them → emits `scores.json` in the dashboard's data contract. |
| `verify.py` | Scoring engine: MAE/RMSE/bias, %±3 °F, Brier, POD/FAR/CSI, Diebold-Mariano. |
| `health.py` | Station-health monitor: Tempest vs 3 anchors → offsets, bands, flag states → `health.json` + `anchors.csv`. |
| `backfill_anchors.py` | One-time METAR-anchor baseline backfill (AWC history) → `anchors_backfill.json`, so flags arm fast. |
| `notify.py` | Sends the one-per-flag station-health warning email (Gmail SMTP). |
| `dashboard.html` | Self-contained static page that reads `scores.json` + `health.json`. Two tabs. No frameworks, no external calls. |
| `.github/workflows/capture.yml` | The daily cron that ties it together. |

## Configuration

The capture job reads two values from **GitHub Actions secrets** (never stored in this repo):

- `TEMPEST_TOKEN` — a personal access token from tempestwx.com → Settings → Data Authorizations.
- `TEMPEST_STATION_ID` — the station id (discoverable from the Tempest `/stations` endpoint).
- `GMAIL_USER` / `GMAIL_APP_PASSWORD` — *(optional)* a Gmail address + [App Password](https://myaccount.google.com/apppasswords)
  for the station-health warning email. If unset, `notify.py` no-ops cleanly and the dashboard
  badge/flag-log still convey the flag. (Interim path — alerts migrate to Pushover later.)

The station's published coordinates (33.9364, -83.5736) appear in the code, and the retained
raw snapshots under `data/` additionally embed the station's full-precision (5-decimal)
coordinates and its public station name as returned by the APIs. This is accepted: the station
is already publicly listed on the Tempest station map, and the snapshots are kept verbatim as a
tamper-evident evidence record (they are never scrubbed or rewritten).

## Methodology & data

Scores follow the ForecastAdvisor convention (temperature accuracy as % within 3 °F plus
MAE, scored at short leads on a rolling window), extended with Brier scores for
probability-of-precipitation and Diebold-Mariano paired significance tests. Every raw
snapshot is retained in `data/` as the evidence record.

**Diebold-Mariano significance (updated 2026-06).** The DM test now collapses each calendar
date to a **single** loss observation — the mean of the absolute high-temperature error and
the absolute low-temperature error — before testing. Feeding the test high and low errors as
two separate observations per day double-counted strongly correlated errors (they share the
day's airmass); because the verdict uses a 1-day HAC lag, that correlation went entirely
unmodeled and produced optimistically small p-values that could flip the verdict prematurely.
On the collapsed one-per-day series we also apply the **Harvey–Leybourne–Newbold** small-sample
correction and refer the statistic to a Student-t(n−1) distribution rather than the normal —
both shrink the small-sample optimism. Precipitation attribution conventions are unchanged:
PoP is the max over forecast periods touching the target calendar day, and a CoCoRaHS report
dated *D* is attributed back to calendar day *D−1*. NWS overnight lows are attributed to the
morning they actually occur (the night period's start date **+1 day**), per standard NWS
verification practice.

## Station health — is the truth source trustworthy?

Forecast scoring uses the Tempest station's **own** readings as ground truth, so a silently
drifting sensor would quietly poison the scoreboard — and a credible guarantee claim needs
independent evidence the truth source was behaving (Tempest's forecast likely assimilates our
own obs, a home-field advantage). `health.py` provides that evidence by comparing the Tempest
daily aggregates against three verified anchors:

| Anchor | Type | Distance | Variables |
|---|---|---|---|
| **KWDR** Barrow Co. Airport (Winder) | AWOS-3 | ~6 mi W | temp, humidity, pressure |
| **KAHN** Athens–Ben Epps | ASOS (NWS-grade) | ~12 mi E | temp, humidity, wind, pressure |
| **WATUGA** UGA Watkinsville | research-grade (UGA AEMN) | ~12 mi SE | temp, humidity, wind |

KWDR + KAHN come from the NOAA Aviation Weather Center METAR JSON API (no key); WATUGA is the
server-rendered "Yesterday Condition" daily summary from georgiaweather.net, parsed defensively
(a parse failure drops to two anchors rather than crashing the run). Each is dumped raw into the
daily snapshot; `health.py` aggregates and compares.

**Method.** For each variable, `offset = tempest_daily − anchor_daily` is appended (per anchor,
per day) to `anchors.csv` — the evidence vault. The baseline is the **28-day window ending 7
days ago** (the recent week is excluded so live drift can't inflate its own baseline); the
**normal band** is the 5th–95th percentile of that pooled baseline, with a per-variable
minimum half-width so a thin early sample can't flag on noise. The current 7-day mean offset is
tested against the band.

- **Flag, never override.** Anchors monitor *stability*; the scoring truth source stays the
  Tempest station, unchanged. A flag only **annotates** the scoreboard (a ⚠ footnote) — flagged
  days are never excluded from scoring (exclusion rules invite cherry-picking on a claim).
- **Triangulation.** A variable flags only on **same-direction divergence vs ≥ 2 of 3 anchors**
  (wind uses the two wind-capable anchors). Divergence vs a single anchor is real weather across
  6–12 miles — logged, never flagged.
- **States.** `LEARNING` (baseline still warming up, < 12 days) → `OK` → `WATCH` (3 consecutive
  divergent days, temp/RH) → `FLAG` (5+ days, or a step-change jump).
- **Wind is trend-only.** A fence-post vs a 33-ft airport tower guarantees a large *constant*
  offset; the rolling baseline absorbs it, so only **drift** in the offset is meaningful.
  (Pressure is reduced to sea-level before comparison, so its offset is small and centered.)
- **Rain** stays on the existing CoCoRaHS cross-check, not the METAR anchors.

The flag log persists in `health_state.json`; `notify.py` sends exactly one warning email per
flag-open event (a `health_emailed.json` ledger prevents repeats). The METAR baseline is
backfilled from AWC history (`backfill_anchors.py`) so flags arm within days of launch rather
than after a month; WATUGA accumulates from launch.

## Operations

- **Staleness check (next routine edit — not yet automated here):** the Monday
  `tempest-weekly-scorecard` routine should fetch the published `scores.json` and confirm
  `generated_at` is **< 48 h old**, flagging loudly if not. The daily cron can silently stop
  (GitHub drops scheduled events under load, and auto-disables a workflow after 60 days of repo
  inactivity); when it does, `scores.json` freezes. The dashboard now detects this client-side
  (it computes snapshot age from `generated_at` against the viewer's clock), but a server-side
  check in the weekly routine is the belt-and-suspenders backstop.
- **Capture-miss health:** `scores.json → data_health.capture_misses` counts days in the
  expected span (first capture → today) with no irreplaceable Tempest snapshot — including days
  the workflow never ran at all — and any such gap breaks `station_online_streak`.
- **Manual workflows** (`backfill`, `ws-explore`) push directly and are intended to fail red if
  the push fails; the daily `capture` job rebases before pushing and serializes via a
  `concurrency` group.

## License

Personal project. Provided as-is.
