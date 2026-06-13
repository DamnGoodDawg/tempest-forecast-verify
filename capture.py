#!/usr/bin/env python3
"""
capture.py - daily forecast snapshot job (stdlib only).

Captures, as raw JSON under data/YYYY-MM-DD/:
  tempest.json    - Tempest better_forecast (the subject under test) + current conditions
  nws.json        - NWS gridpoint forecast + hourly (FFC/80,97)
  openmeteo.json  - Open-Meteo GFS/ECMWF/NBM daily+hourly (also backfillable; captured for tidiness)
  tempest_obs_yesterday.json - station actuals for yesterday (temp/wind truth + rain occurrence)
  diagnostics.json - station/hub health: online, RSSI, battery voltage, sensor faults
  _capture_log.json - capture metadata + failures + warnings

Env vars: TEMPEST_TOKEN, TEMPEST_STATION_ID (skips Tempest gracefully if unset, with loud warning).
Run daily at ~07:00 America/New_York. Idempotent: re-running a day overwrites that day only.

Design notes (June 2026 hardening):
  - Records BOTH station_id and device_id (device-history endpoints 404 without device_id).
  - The whole raw API response is dumped for every source, so if the API silently drops a
    field, the snapshot still carries whatever WAS returned -- extract.py tolerates gaps.
  - Rain: the full station obs is dumped, preserving BOTH the raw-haptic and the
    RainCheck/NC-corrected precip values. We never pick one here; CoCoRaHS arbitrates later.
  - Core sources (tempest/nws/openmeteo/obs) fail LOUD (exit 1) so a missed irreplaceable
    Tempest capture is never silent. Diagnostics is a soft warning (never blocks the run).
"""
import json, os, sys, urllib.request, urllib.parse, datetime as dt
from zoneinfo import ZoneInfo

LAT, LON = 33.9364, -83.5736
NWS_GRID = "FFC/80,97"
UA = "tempest-forecast-verify/1.0 (tkb5047@gmail.com)"
BASE = os.path.dirname(os.path.abspath(__file__))
COCORAHS_STATION = "GA-OC-20"   # "Bogart 2.4 S", ~2.6 mi away — independent precip truth
COCORAHS_WINDOW_DAYS = 6        # trailing window: the observer reports ~7am, so allow lag

# Station-health reference anchors (independent "is my station behaving?" evidence).
#   KWDR + KAHN: NOAA Aviation Weather Center METAR JSON (no key). hours=36 covers the
#     previous full local day with margin; health.py buckets each ob to its local date.
#   WATUGA (UGA Watkinsville, georgiaweather.net): server-rendered "Yesterday Condition"
#     daily-summary table — scraped raw here, parsed defensively in health.py.
# All anchor fetches are SOFT (warnings only) — a missing anchor never blocks capture.
ANCHOR_METAR_IDS = "KWDR,KAHN"
ANCHOR_METAR_HOURS = 36
WATUGA_URL = "http://www.georgiaweather.net/?variable=YC&site=WATUGA"

def get(url, params=None):
    if params: url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())

def get_text(url, params=None):
    if params: url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")

# NOTE on sensor fault flags + RSSI: these live in the WebSocket device_status/hub_status
# messages, which (confirmed June 2026) the public WS does NOT deliver to personal-token
# clients -- a 150 s listen returned only connection_opened/ack/obs_st. /diagnostics also
# 401s, and the REST station/device endpoints carry no sensor_status or rssi. So named
# fault flags ("wind failed"/"rain failed") are not obtainable with a personal token.
# We monitor what IS reachable: battery voltage (device-obs index 16) and hub-online
# (better_forecast is_station_online). extract.py keeps sensor_faults/rssi as null ("n/a").

def write(outdir, name, obj):
    with open(os.path.join(outdir, name), "w") as f:
        json.dump(obj, f)

def discover_device_id(station, token):
    """Find the Tempest (device_type 'ST') device_id for this station. Best-effort."""
    try:
        st = get("https://swd.weatherflow.com/swd/rest/stations", {"token": token})
        for s in st.get("stations", []):
            if str(s.get("station_id")) == str(station):
                for d in s.get("devices", []):
                    if d.get("device_type") == "ST":
                        return d.get("device_id"), s.get("name")
                # fall back to first device with an id
                for d in s.get("devices", []):
                    if d.get("device_id"):
                        return d.get("device_id"), s.get("name")
        return None, None
    except Exception:
        return None, None

def main():
    now_local = dt.datetime.now(ZoneInfo("America/New_York"))
    day = now_local.date().isoformat()
    outdir = os.path.join(BASE, "data", day)
    os.makedirs(outdir, exist_ok=True)
    meta = {"captured_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "captured_at_local": now_local.isoformat(), "lat": LAT, "lon": LON}
    failures = []   # hard failures -> exit 1 (loud)
    warnings = []   # soft issues -> logged, but the run still succeeds

    token, station = os.environ.get("TEMPEST_TOKEN"), os.environ.get("TEMPEST_STATION_ID")
    device_id = None

    # 0. Discover device_id (REQUIRED for device-history endpoints; station_id 404s/401s there)
    if token and station:
        device_id, station_name = discover_device_id(station, token)
        meta["station_id"] = station
        meta["device_id"] = device_id
        meta["station_name"] = station_name
        if not device_id:
            warnings.append("device_id: could not discover from /stations (non-fatal)")

    # 1. Tempest better_forecast -- the one snapshot that can NEVER be backfilled
    if token and station:
        try:
            tf = get("https://swd.weatherflow.com/swd/rest/better_forecast", {
                "station_id": station, "token": token, "units_temp": "f",
                "units_wind": "mph", "units_precip": "in", "units_pressure": "inhg"})
            write(outdir, "tempest.json", {"meta": meta, "data": tf})
            ndaily = len(tf.get("forecast", {}).get("daily", [])) if isinstance(tf, dict) else 0
            print(f"[ok] tempest.json ({ndaily} daily periods)")
        except Exception as e:
            failures.append(f"tempest: {e}")
    else:
        failures.append("tempest: TEMPEST_TOKEN/TEMPEST_STATION_ID not set -- IRREPLACEABLE SNAPSHOT MISSED")

    # 2. NWS official forecast (12h periods + hourly)
    try:
        nws = {"forecast": get(f"https://api.weather.gov/gridpoints/{NWS_GRID}/forecast"),
               "hourly": get(f"https://api.weather.gov/gridpoints/{NWS_GRID}/forecast/hourly")}
        write(outdir, "nws.json", {"meta": meta, "data": nws})
        gen = nws.get("forecast", {}).get("properties", {}).get("generatedAt", "?")
        print(f"[ok] nws.json (generated {gen})")
    except Exception as e:
        failures.append(f"nws: {e}")

    # 3. Open-Meteo multi-model (backfillable via Previous Runs, captured anyway)
    try:
        om = get("https://api.open-meteo.com/v1/forecast", {
            "latitude": LAT, "longitude": LON,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max",
            "hourly": "temperature_2m,precipitation,precipitation_probability",
            "models": "gfs_seamless,ecmwf_ifs025,ncep_nbm_conus",
            "temperature_unit": "fahrenheit", "precipitation_unit": "inch",
            "wind_speed_unit": "mph", "timezone": "America/New_York", "forecast_days": 7})
        write(outdir, "openmeteo.json", {"meta": meta, "data": om})
        print("[ok] openmeteo.json")
    except Exception as e:
        failures.append(f"openmeteo: {e}")

    # 4. Current station observation. Carries current conditions AND yesterday's precip
    #    totals in BOTH forms: precip_accum_local_yesterday (raw haptic) and
    #    precip_accum_local_yesterday_final (RainCheck/NC-corrected). We keep both.
    if token and station:
        try:
            sobs = get(f"https://swd.weatherflow.com/swd/rest/observations/station/{station}", {
                "token": token, "units_temp": "f", "units_wind": "mph",
                "units_precip": "in", "units_pressure": "inhg"})
            write(outdir, "tempest_station_obs.json", {"meta": meta, "data": sobs})
            print("[ok] tempest_station_obs.json")
        except Exception as e:
            failures.append(f"tempest_station_obs: {e}")

    # 5. Yesterday's per-minute device observations -> the temperature TRUTH (daily
    #    high/low computed by extract.py) plus battery voltage + raw/corrected rain.
    #    NOTE: this endpoint returns positional obs_st arrays in METRIC (air_temperature
    #    in C at index 7, rain in mm); extract.py converts. /diagnostics 401s for personal
    #    tokens, so battery comes from obs_st index 16. SOFT (never blocks the run).
    if token and device_id:
        try:
            y = now_local.date() - dt.timedelta(days=1)
            t0 = int(dt.datetime.combine(y, dt.time.min, ZoneInfo("America/New_York")).timestamp())
            t1 = int(dt.datetime.combine(y, dt.time.max, ZoneInfo("America/New_York")).timestamp())
            dobs = get("https://swd.weatherflow.com/swd/rest/observations/device/%s" % device_id, {
                "token": token, "time_start": t0, "time_end": t1})
            write(outdir, "tempest_device_yesterday.json",
                  {"meta": meta, "for_date": y.isoformat(), "data": dobs})
            nobs = len(dobs.get("obs", [])) if isinstance(dobs, dict) else 0
            print(f"[ok] tempest_device_yesterday.json ({nobs} obs)")
        except Exception as e:
            warnings.append(f"tempest_device_yesterday: {e} (non-fatal)")

    # 6. CoCoRaHS daily precip from nearby GA-OC-20 (independent rain-amount truth).
    #    Free CSV export. The observer reports ~7am for the prior 24h, so a trailing
    #    window lets a late entry be picked up on a subsequent day. SOFT (token-free).
    try:
        end = now_local.date()
        start = end - dt.timedelta(days=COCORAHS_WINDOW_DAYS)
        csv_text = get_text("https://data.cocorahs.org/cocorahs/export/exportreports.aspx", {
            "ReportType": "Daily", "dtf": "1", "Format": "CSV", "ReportDateType": "reportdate",
            "Station": COCORAHS_STATION,
            "StartDate": f"{start.month}/{start.day}/{start.year}",
            "EndDate": f"{end.month}/{end.day}/{end.year}"})
        write(outdir, "cocorahs.json", {"meta": meta, "station": COCORAHS_STATION, "csv": csv_text})
        nrows = max(0, csv_text.count("\n") - 1)
        print(f"[ok] cocorahs.json ({nrows} rows)")
    except Exception as e:
        warnings.append(f"cocorahs: {e} (non-fatal)")

    # 7. Station-health anchors (SOFT — never block the run). Raw dumps; health.py parses.
    #    7a. AWC METARs for KWDR + KAHN (JSON, no key). Whole response kept as the evidence
    #        vault; health.py buckets obs to local days and computes daily aggregates.
    try:
        am = get("https://aviationweather.gov/api/data/metar", {
            "ids": ANCHOR_METAR_IDS, "format": "json", "hours": ANCHOR_METAR_HOURS})
        write(outdir, "anchors_metar.json", {"meta": meta, "data": am})
        n = len(am) if isinstance(am, list) else 0
        print(f"[ok] anchors_metar.json ({n} obs)")
    except Exception as e:
        warnings.append(f"anchors_metar: {e} (non-fatal)")

    #    7b. WATUGA "Yesterday Condition" daily-summary page (server-rendered HTML table).
    #        Parsed defensively in health.py; on parse failure the run continues on 2 anchors.
    try:
        watuga_html = get_text(WATUGA_URL)
        write(outdir, "watuga.html", {"meta": meta, "url": WATUGA_URL, "html": watuga_html})
        print(f"[ok] watuga.html ({len(watuga_html)} bytes)")
    except Exception as e:
        warnings.append(f"watuga: {e} (non-fatal)")

    write(outdir, "_capture_log.json", {"meta": meta, "failures": failures, "warnings": warnings})
    if warnings:
        print("WARNINGS:\n  " + "\n  ".join(warnings), file=sys.stderr)
    if failures:
        print("FAILURES:\n  " + "\n  ".join(failures), file=sys.stderr)
        sys.exit(1)
    print(f"Capture complete: {outdir}")

if __name__ == "__main__":
    main()
