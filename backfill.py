#!/usr/bin/env python3
"""
backfill.py - historical Tempest device-obs backfill (stdlib only).

Fetches per-minute device observations for past dates (device history is retained on
WeatherFlow's servers) and writes backfill/<date>.json in the same shape as
tempest_device_yesterday.json. extract.py folds these into actuals + the rain comparison
WITHOUT counting them as daily captures (so capture streak / health are unaffected).

Usage:  python backfill.py [YYYY-MM-DD ...]
        (defaults to the install gap: 2026-05-31 2026-06-01 2026-06-02)
Env:    TEMPEST_TOKEN, TEMPEST_STATION_ID
"""
import json, os, sys, urllib.request, urllib.parse, datetime as dt
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")
UA = "tempest-forecast-verify/1.0 (tkb5047@gmail.com)"
BASE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATES = ["2026-05-31", "2026-06-01", "2026-06-02"]


def get(url, params=None):
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def device_id_for(station, token):
    st = get("https://swd.weatherflow.com/swd/rest/stations", {"token": token})
    for s in st.get("stations", []):
        if str(s.get("station_id")) == str(station):
            for d in s.get("devices", []):
                if d.get("device_type") == "ST":
                    return d.get("device_id")
    return None


def main():
    token, station = os.environ.get("TEMPEST_TOKEN"), os.environ.get("TEMPEST_STATION_ID")
    if not token or not station:
        print("TEMPEST_TOKEN/TEMPEST_STATION_ID not set", file=sys.stderr)
        sys.exit(1)
    dates = sys.argv[1:] or DEFAULT_DATES
    device_id = device_id_for(station, token)
    if not device_id:
        print("could not discover device_id", file=sys.stderr)
        sys.exit(1)

    outdir = os.path.join(BASE, "backfill")
    os.makedirs(outdir, exist_ok=True)
    for ds in dates:
        try:
            day = dt.date.fromisoformat(ds)
        except ValueError:
            print(f"[skip] bad date {ds}", file=sys.stderr)
            continue
        t0 = int(dt.datetime.combine(day, dt.time.min, NY).timestamp())
        t1 = int(dt.datetime.combine(day, dt.time.max, NY).timestamp())
        try:
            dobs = get(f"https://swd.weatherflow.com/swd/rest/observations/device/{device_id}",
                       {"token": token, "time_start": t0, "time_end": t1})
            nobs = len(dobs.get("obs", [])) if isinstance(dobs, dict) else 0
            with open(os.path.join(outdir, f"{ds}.json"), "w") as f:
                json.dump({"for_date": ds, "device_id": device_id, "data": dobs}, f)
            print(f"[ok] backfill/{ds}.json ({nobs} obs)")
        except Exception as e:
            print(f"[warn] {ds}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
