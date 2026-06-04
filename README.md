# Tempest Forecast Verify

A daily automated check of whether a [WeatherFlow Tempest](https://weatherflow.com/tempest-weather-system/)
weather station's forecast for **Statham, GA** is actually more accurate than the public
forecasts — NWS, NBM, ECMWF, and GFS — scored against observed conditions.

This is the verification layer behind WeatherFlow's *Better Forecast Guarantee*: keep an
honest, timestamped, tamper-evident record of forecast accuracy and let the numbers decide.

## How it works

A GitHub Actions job runs once a day (~07:00 ET) and:

1. **Captures** (`capture.py`) each provider's forecast into `data/YYYY-MM-DD/`:
   - `tempest.json` — Tempest `better_forecast` (the subject under test). Irreplaceable: it has no public archive.
   - `nws.json` — the official National Weather Service gridpoint forecast.
   - `openmeteo.json` — GFS / ECMWF / NBM via Open-Meteo.
   - `tempest_obs_yesterday.json` — the station's own observed actuals (the ground truth).
   - `diagnostics.json` — station/hub health (online, signal, battery, sensor faults).
2. **Scores** (`extract.py` → `verify.py`) every snapshot and writes `scores.json`:
   mean absolute error and % within 3 °F on temperature, precip-occurrence CSI, PoP Brier
   score, and a paired Diebold-Mariano significance test — at 1-, 2-, 3-day and blended leads.
3. **Publishes** a static dashboard (`dashboard.html` + `scores.json`) via GitHub Pages.

Until enough days accrue, the verdict reads **TOO EARLY** — by design.

## Files

| File | Role |
|---|---|
| `capture.py` | Daily snapshot job. Standard library only. Fails loud if the Tempest capture is missed. |
| `extract.py` | Reads snapshots → scores them → emits `scores.json` in the dashboard's data contract. |
| `verify.py` | Scoring engine: MAE/RMSE/bias, %±3 °F, Brier, POD/FAR/CSI, Diebold-Mariano. |
| `dashboard.html` | Self-contained static page that reads `scores.json`. No frameworks, no external calls. |
| `.github/workflows/capture.yml` | The daily cron that ties it together. |

## Configuration

The capture job reads two values from **GitHub Actions secrets** (never stored in this repo):

- `TEMPEST_TOKEN` — a personal access token from tempestwx.com → Settings → Data Authorizations.
- `TEMPEST_STATION_ID` — the station id (discoverable from the Tempest `/stations` endpoint).

The only location reference in the code is the station's published coordinates
(33.9364, -83.5736), which are already public on the Tempest station map.

## Methodology & data

Scores follow the ForecastAdvisor convention (temperature accuracy as % within 3 °F plus
MAE, scored at short leads on a rolling window), extended with Brier scores for
probability-of-precipitation and Diebold-Mariano paired significance tests. Every raw
snapshot is retained in `data/` as the evidence record.

## License

Personal project. Provided as-is.
