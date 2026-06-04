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
import socket, ssl, base64, struct, time
from zoneinfo import ZoneInfo

LAT, LON = 33.9364, -83.5736
NWS_GRID = "FFC/80,97"
UA = "tempest-forecast-verify/1.0 (tkb5047@gmail.com)"
BASE = os.path.dirname(os.path.abspath(__file__))
COCORAHS_STATION = "GA-OC-20"   # "Bogart 2.4 S", ~2.6 mi away — independent precip truth
COCORAHS_WINDOW_DAYS = 6        # trailing window: the observer reports ~7am, so allow lag

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

# --- minimal stdlib WebSocket client (RFC 6455) -----------------------------
# Just enough to grab one device_status (sensor faults + RSSI) and hub_status.
# device_status/rssi/sensor_status are NOT in any REST endpoint -- only here.
def _ws_send(sock, opcode, payload=b""):
    mask = os.urandom(4)
    n = len(payload)
    hdr = bytearray([0x80 | opcode])
    if n < 126:
        hdr.append(0x80 | n)
    elif n < 65536:
        hdr.append(0x80 | 126); hdr += struct.pack(">H", n)
    else:
        hdr.append(0x80 | 127); hdr += struct.pack(">Q", n)
    hdr += mask
    sock.sendall(bytes(hdr) + bytes(b ^ mask[i % 4] for i, b in enumerate(payload)))

class _WSReader:
    def __init__(self, sock, leftover=b""):
        self.s, self.buf = sock, leftover
    def _need(self, n):
        while len(self.buf) < n:
            chunk = self.s.recv(4096)
            if not chunk:
                raise RuntimeError("ws closed")
            self.buf += chunk
    def frame(self):
        self._need(2)
        b0, b1 = self.buf[0], self.buf[1]
        opcode, masked, ln, idx = b0 & 0x0F, b1 & 0x80, b1 & 0x7F, 2
        if ln == 126:
            self._need(4); ln = struct.unpack(">H", self.buf[2:4])[0]; idx = 4
        elif ln == 127:
            self._need(10); ln = struct.unpack(">Q", self.buf[2:10])[0]; idx = 10
        mask = b""
        if masked:
            self._need(idx + 4); mask = self.buf[idx:idx + 4]; idx += 4
        self._need(idx + ln)
        payload = self.buf[idx:idx + ln]; self.buf = self.buf[idx + ln:]
        if masked:
            payload = bytes(c ^ mask[i % 4] for i, c in enumerate(payload))
        return opcode, payload

def ws_device_status(device_id, token, timeout=150):
    """Connect, subscribe to the device, collect device_status (+ hub_status), close.
    Returns a dict that also carries '_seen' (the message types observed) for diagnostics."""
    host, path = "ws.weatherflow.com", "/swd/data?token=" + urllib.parse.quote(token, safe="")
    ctx = ssl.create_default_context()
    raw = socket.create_connection((host, 443), timeout=20)
    s = ctx.wrap_socket(raw, server_hostname=host)
    try:
        key = base64.b64encode(os.urandom(16)).decode()
        s.sendall((f"GET {path} HTTP/1.1\r\nHost: {host}\r\nUpgrade: websocket\r\n"
                   f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\n"
                   f"Sec-WebSocket-Version: 13\r\n\r\n").encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            chunk = s.recv(1024)
            if not chunk:
                raise RuntimeError("ws closed during handshake")
            buf += chunk
        if b"101" not in buf.split(b"\r\n", 1)[0]:
            raise RuntimeError("ws upgrade not accepted")
        rdr = _WSReader(s, buf.split(b"\r\n\r\n", 1)[1])
        _ws_send(s, 0x1, json.dumps({"type": "listen_start", "device_id": int(device_id), "id": "hc"}).encode())
        s.settimeout(timeout)
        out, seen, end = {}, set(), time.time() + timeout
        while time.time() < end:
            try:
                opcode, payload = rdr.frame()
            except (socket.timeout, RuntimeError):
                break
            if opcode == 0x8:        # close
                break
            if opcode == 0x9:        # ping -> pong
                _ws_send(s, 0xA, payload); continue
            if opcode != 0x1:        # only care about text
                continue
            try:
                m = json.loads(payload.decode())
            except Exception:
                continue
            t = m.get("type")
            if t:
                seen.add(t)
            if t in ("device_status", "hub_status"):
                out[t] = m
            if "device_status" in out:
                break
        out["_seen"] = sorted(seen)
        return out
    finally:
        try: s.close()
        except Exception: pass

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

    # 5b. Device status over WebSocket: sensor fault flags (sensor_status bitmask:
    #     wind/rain/etc. failed) + RSSI + hub status. These are NOT in any REST endpoint
    #     (/diagnostics 401s for personal tokens). device_status is periodic (~60s), so
    #     this can take up to ~80s. SOFT (never blocks the run).
    if token and device_id:
        try:
            ds = ws_device_status(device_id, token)
            seen = ds.pop("_seen", []) if isinstance(ds, dict) else []
            if ds.get("device_status") or ds.get("hub_status"):
                write(outdir, "device_status.json", {"meta": meta, "data": ds})
                ss = (ds.get("device_status") or {}).get("sensor_status")
                print(f"[ok] device_status.json (sensor_status={ss}, types={seen})")
            else:
                warnings.append(f"device_status: no status frame within timeout; saw types={seen} (non-fatal)")
        except Exception as e:
            warnings.append(f"device_status: {e} (non-fatal)")

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

    write(outdir, "_capture_log.json", {"meta": meta, "failures": failures, "warnings": warnings})
    if warnings:
        print("WARNINGS:\n  " + "\n  ".join(warnings), file=sys.stderr)
    if failures:
        print("FAILURES:\n  " + "\n  ".join(failures), file=sys.stderr)
        sys.exit(1)
    print(f"Capture complete: {outdir}")

if __name__ == "__main__":
    main()
