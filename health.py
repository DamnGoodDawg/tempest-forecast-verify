#!/usr/bin/env python3
"""
health.py - station-health monitor: "is my station's data trustworthy?" (stdlib only).

Companion to extract.py. Forecast scoring uses the Tempest station's OWN readings as
ground truth, so a silently-drifting sensor would poison the scoreboard. This script
compares the Tempest daily aggregates against THREE independent verified anchors and
emits health.json (the Station Health dashboard tab's data contract).

Locked design decisions (station-health-design.md):
  - FLAG, NEVER OVERRIDE. Anchors monitor STABILITY; the scoring truth source stays the
    Tempest station, unchanged. A flag only ANNOTATES the scoreboard.
  - TRIANGULATION. A variable flags only on same-direction divergence vs >= 2 of 3 anchors;
    divergence vs a single anchor is real weather across 6-12 miles, logged but never flagged.
  - WIND IS TREND-ONLY. Fence-post siting vs 33-ft airport towers means a large CONSTANT
    offset; only drift in that offset is meaningful. The rolling baseline absorbs the constant.

Anchors:
  KWDR  Barrow Co. Airport (Winder, AWOS-3, ~6 mi W)  - temp, RH, pressure (no wind/precip)
  KAHN  Athens-Ben Epps     (ASOS,   ~12 mi E)         - temp, RH, wind, pressure, precip
  WATUGA UGA Watkinsville   (UGA AEMN, ~12 mi SE)      - temp, RH, wind, daily rain

Method:
  offset(var, anchor, day) = tempest_daily - anchor_daily.  Pool every capable anchor's
  offsets into one distribution; baseline = the 28-day window ending 7 days ago; band =
  [p5, p95] of that baseline (with a per-variable minimum half-width so a thin early sample
  can't flag on noise). current 7-day mean offset per anchor is tested against the band;
  >= 2 anchors out the SAME side -> the day is "divergent". 3 consecutive divergent days
  (temp/RH) opens a WATCH; 5+ days, or a step-change jump, opens a FLAG. Until the baseline
  has >= MIN_BASELINE days, the variable reads LEARNING (calm warm-up state).

Never crashes the daily run: on any unexpected error it writes a minimal LEARNING
health.json and exits 0 (matching extract.py's contract).

Side effects (all committed by the workflow, the durable evidence vault):
  anchors.csv          - every (day, anchor, var, tempest, anchor, offset), rebuilt each run
  health_state.json    - canonical flag log (opened/resolved per var), persisted across runs
  health_emailed.json  - ledger of flag keys already emailed (no repeat warning emails)
  pending_email.json   - written ONLY when a new flag needs a warning email (notify.py reads it)
"""
import json, os, sys, glob, csv, re, html, math, datetime as dt
from collections import defaultdict
from zoneinfo import ZoneInfo

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
OUT = os.path.join(BASE, "health.json")
ANCHORS_CSV = os.path.join(BASE, "anchors.csv")
STATE_FILE = os.path.join(BASE, "health_state.json")
EMAILED_FILE = os.path.join(BASE, "health_emailed.json")
HISTORY_DIR = os.path.join(BASE, "history")
PENDING_EMAIL = os.path.join(BASE, "pending_email.json")
ANCHOR_BACKFILL = os.path.join(BASE, "anchors_backfill.json")
NY = ZoneInfo("America/New_York")

INSTALL_DATE = "2026-05-31"
STATION_ELEV_M = 252.98          # ~830 ft (CLAUDE.md) — for station-pressure -> sea-level
MIN_BASELINE = 12                # days of baseline offsets before a variable can leave LEARNING
WATCH_DAYS = 3                   # consecutive divergent days to open a WATCH (temp/RH)
FLAG_DAYS = 5                    # consecutive divergent days to escalate WATCH -> FLAG
MIN_ANCHORS = 2                  # triangulation floor: divergence must be vs >= this many anchors
EMAIL_TO = "tkb5047@gmail.com"

# Anchor metadata (mirrors the design + dashboard contract). `vars` = comparable variables.
ANCHORS = [
    {"id": "KWDR",   "name": "Barrow Co. Airport", "type": "AWOS-3",   "place": "Winder",
     "dir": "W",  "miles": 6,  "elev_ft": 919, "vars": ["temp", "rh", "pressure"]},
    {"id": "KAHN",   "name": "Athens-Ben Epps",    "type": "ASOS",     "place": "Athens",
     "dir": "E",  "miles": 12, "elev_ft": 791, "vars": ["temp", "rh", "wind", "pressure"]},
    {"id": "WATUGA", "name": "UGA Watkinsville",   "type": "UGA AEMN", "place": "Watkinsville",
     "dir": "SE", "miles": 12, "elev_ft": 760, "vars": ["temp", "rh", "wind"]},
]
ANCHOR_IDS = [a["id"] for a in ANCHORS]
METAR_IDS = {"KWDR", "KAHN"}

# Per-variable display + flagging config. half: minimum band half-width (noise floor).
VARS = [
    {"var": "temp",     "label": "Temperature", "unit": "°F",  "half": 0.6,  "jump": 3.0,  "flagable": True},
    {"var": "rh",       "label": "Humidity",    "unit": "pts", "half": 4.0,  "jump": 15.0, "flagable": True},
    {"var": "wind",     "label": "Wind",        "unit": "mph", "half": 1.5,  "jump": 6.0,  "flagable": True,  "trend_only": True},
    {"var": "pressure", "label": "Pressure",    "unit": "mb",  "half": 0.6,  "jump": 3.0,  "flagable": True},
    {"var": "rain",     "label": "Rain",        "unit": "in",  "cross_check": "CoCoRaHS GA-OC-20"},
]
WIND_ANCHORS = ["KAHN", "WATUGA"]   # only wind-capable anchors (KWDR has no wind group)

STATE = {"LEARNING": 0, "OK": 1, "WATCH": 2, "FLAG": 3}
STATE_NAME = {v: k for k, v in STATE.items()}


# ----------------------------------------------------------------- small helpers
def d(s):
    return dt.date.fromisoformat(s)

def c_to_f(c):
    return c * 9.0 / 5.0 + 32.0

def load(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None

def mean(xs):
    xs = [x for x in xs if isinstance(x, (int, float))]
    return sum(xs) / len(xs) if xs else None

def median(xs):
    xs = sorted(x for x in xs if isinstance(x, (int, float)))
    n = len(xs)
    if not n:
        return None
    m = n // 2
    return xs[m] if n % 2 else (xs[m - 1] + xs[m]) / 2.0

def percentile(xs, p):
    """Linear-interpolation percentile (p in 0..100). stdlib-only."""
    xs = sorted(x for x in xs if isinstance(x, (int, float)))
    if not xs:
        return None
    if len(xs) == 1:
        return xs[0]
    k = (len(xs) - 1) * (p / 100.0)
    lo = math.floor(k)
    hi = math.ceil(k)
    if lo == hi:
        return xs[int(k)]
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)

def rh_from_t_td(t_c, td_c):
    """Relative humidity (%) from temperature and dewpoint (both °C). Magnus formula."""
    if t_c is None or td_c is None:
        return None
    try:
        a, b = 17.625, 243.04
        return 100.0 * math.exp((a * td_c) / (b + td_c)) / math.exp((a * t_c) / (b + t_c))
    except Exception:
        return None

def station_to_slp(p_mb, t_c, h_m=STATION_ELEV_M):
    """Station pressure (mb) -> sea-level pressure (mb), so it compares to METAR altimeter."""
    if p_mb is None or t_c is None:
        return None
    try:
        return p_mb * (1.0 - (0.0065 * h_m) / (t_c + 0.0065 * h_m + 273.15)) ** -5.257
    except Exception:
        return None

def cell(row, i):
    return row[i] if isinstance(row, (list, tuple)) and len(row) > i else None


# ----------------------------------------------------------------- Tempest daily aggregates
# obs_st positional array (METRIC): 2=wind avg m/s, 6=station pressure mb, 7=air temp C, 8=RH %.
OBS_WIND, OBS_PRES, OBS_TEMP, OBS_RH = 2, 6, 7, 8
MS_TO_MPH = 2.2369362921

def tempest_daily(device_json):
    """Per-minute device obs (obs_st) -> one day's {var: aggregate} keyed by for_date.
    temp = daily MEAN °F; rh = mean %; wind = mean mph; pressure = mean sea-level mb."""
    if not device_json:
        return None, None
    date = device_json.get("for_date")
    obs = ((device_json.get("data") or {}).get("obs")) or []
    if not date or not obs:
        return None, None
    temps_f = [c_to_f(t) for t in (cell(r, OBS_TEMP) for r in obs) if isinstance(t, (int, float))]
    rhs = [r for r in (cell(o, OBS_RH) for o in obs) if isinstance(r, (int, float))]
    winds = [w * MS_TO_MPH for w in (cell(r, OBS_WIND) for r in obs) if isinstance(w, (int, float))]
    slps = []
    for r in obs:
        slp = station_to_slp(cell(r, OBS_PRES), cell(r, OBS_TEMP))
        if slp is not None:
            slps.append(slp)
    agg = {}
    if temps_f:
        agg["temp"] = mean(temps_f)
    if rhs:
        agg["rh"] = mean(rhs)
    if winds:
        agg["wind"] = mean(winds)
    if slps:
        agg["pressure"] = mean(slps)
    return date, (agg or None)


# ----------------------------------------------------------------- anchor daily aggregates
def _iso(epoch):
    return dt.datetime.fromtimestamp(int(epoch), dt.timezone.utc).isoformat().replace("+00:00", "Z")

def current_observations(day_dirs, anchors):
    """Latest reading per station for the 'Current conditions' strip — a real spot-check vs
    the Tempest app, NOT a 7-day mean. EACH station carries its own `as_of` because their
    freshness differs: Tempest (newest station-obs snapshot, metric→converted) and KWDR/KAHN
    (most recent METAR) are instantaneous; WATUGA has no live feed, so it shows its most
    recent DAILY summary, stamped daily. The dashboard's live gist later overrides Tempest/
    KWDR/KAHN with minute-fresh values, leaving WATUGA's daily here as the fallback."""
    out, top_as_of = {}, None
    for dd in reversed(day_dirs):
        sj = load(os.path.join(dd, "tempest_station_obs.json"))
        obs = ((sj or {}).get("data") or {}).get("obs") or []
        if not obs:
            continue
        o = obs[0]
        t = o.get("air_temperature")
        agg = {}
        if isinstance(t, (int, float)):
            agg["temp"] = round(c_to_f(t), 1)
        if isinstance(o.get("relative_humidity"), (int, float)):
            agg["rh"] = round(o["relative_humidity"])
        if isinstance(o.get("wind_avg"), (int, float)):
            agg["wind"] = round(o["wind_avg"] * MS_TO_MPH, 1)
        slp = o.get("sea_level_pressure")
        if isinstance(slp, (int, float)):
            agg["pressure"] = round(slp, 1)
        elif isinstance(o.get("station_pressure"), (int, float)):
            sp = station_to_slp(o["station_pressure"], t)
            if sp is not None:
                agg["pressure"] = round(sp, 1)
        ts = o.get("timestamp")
        if ts:
            agg["as_of"] = top_as_of = _iso(ts)
        if len(agg) > (1 if "as_of" in agg else 0):
            out["Tempest"] = agg
        break
    for dd in reversed(day_dirs):
        mj = load(os.path.join(dd, "anchors_metar.json"))
        rows = (mj or {}).get("data") or []
        if not isinstance(rows, list) or not rows:
            continue
        latest = {}
        for o in rows:
            sid = o.get("icaoId")
            if sid in METAR_IDS and o.get("obsTime") is not None:
                if sid not in latest or o["obsTime"] > latest[sid].get("obsTime", 0):
                    latest[sid] = o
        for sid, o in latest.items():
            t, td = o.get("temp"), o.get("dewp")
            agg = {"as_of": _iso(o["obsTime"])}
            if isinstance(t, (int, float)):
                agg["temp"] = round(c_to_f(t), 1)
            rh = rh_from_t_td(t, td)
            if rh is not None:
                agg["rh"] = round(rh)
            if sid == "KAHN" and isinstance(o.get("wspd"), (int, float)):
                agg["wind"] = round(o["wspd"] * 1.150779, 1)
            if isinstance(o.get("altim"), (int, float)):
                agg["pressure"] = round(float(o["altim"]), 1)
            if len(agg) > 1:
                out[sid] = agg
        break
    # WATUGA is intentionally NOT a current-conditions tile: it has no live feed (only a
    # daily summary), and a daily value in a "current conditions" strip is misleading. It
    # still participates in the offset analysis below. Only stations with a genuine recent
    # reading (Tempest + the METAR anchors) get a tile.
    return {"as_of": top_as_of, "stations": out}


def metar_daily(metar_json):
    """AWC METAR list -> {anchor_id: {date: {var: aggregate}}}. Buckets each ob to its
    local (NY) calendar day; keeps a day only if it has enough obs to be a daily mean."""
    out = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    rows = (metar_json or {}).get("data") or []
    if not isinstance(rows, list):
        return {}
    for o in rows:
        if not isinstance(o, dict):
            continue
        sid = o.get("icaoId")
        if sid not in METAR_IDS:
            continue
        ts = o.get("obsTime")
        if ts is None:
            continue
        try:
            day = dt.datetime.fromtimestamp(int(ts), NY).date().isoformat()
        except Exception:
            continue
        t, td = o.get("temp"), o.get("dewp")
        if isinstance(t, (int, float)):
            out[sid][day]["temp"].append(c_to_f(t))
        rh = rh_from_t_td(t, td)
        if rh is not None:
            out[sid][day]["rh"].append(rh)
        if sid == "KAHN":   # KWDR's wind group is frequently absent; only KAHN carries wind here
            ws = o.get("wspd")
            if isinstance(ws, (int, float)):
                out[sid][day]["wind"].append(ws * 1.150779)   # knots -> mph
        altim = o.get("altim")
        if isinstance(altim, (int, float)):
            out[sid][day]["pressure"].append(float(altim))
    # collapse lists -> means, requiring >= 4 obs for a representative daily mean
    daily = defaultdict(dict)
    for sid, days in out.items():
        for day, vmap in days.items():
            agg = {}
            for var, vals in vmap.items():
                if len(vals) >= 4:
                    agg[var] = mean(vals)
            if agg:
                daily[sid][day] = agg
    return daily


_WATUGA_LABELS = {
    "Maximum Temperature": ("temp_max", float),
    "Minimum Temperature": ("temp_min", float),
    "Relative Humidity": ("rh", float),
    "Atmospheric Pressure": ("pressure_in", float),
    "Wind Speed": ("wind", float),
}

def watuga_daily(watuga_json, for_date):
    """Parse the WATUGA 'Yesterday Condition' daily-summary table. Defensive: returns None
    on any parse trouble (caller then runs on 2 anchors). Attributed to `for_date` (the
    Tempest device for_date), which aligns with WATUGA's 'yesterday' in production."""
    if not watuga_json or not for_date:
        return None
    raw = watuga_json.get("html") or ""
    if not raw:
        return None
    try:
        text = re.sub(r"<script.*?</script>", "", raw, flags=re.S | re.I)
        flat = html.unescape(re.sub(r"<[^>]+>", "|", text))
        cells = [c.strip() for c in flat.split("|") if c.strip()]
        found = {}
        for i, c in enumerate(cells):
            for label, (key, cast) in _WATUGA_LABELS.items():
                if key in found:
                    continue
                if c.startswith(label):
                    # first numeric cell after the label = the most-recent daily-summary column
                    for j in range(i + 1, min(i + 4, len(cells))):
                        m = re.match(r"^-?\d+(\.\d+)?$", cells[j])
                        if m:
                            try:
                                found[key] = cast(cells[j])
                            except ValueError:
                                pass
                            break
        agg = {}
        if "temp_max" in found and "temp_min" in found:
            agg["temp"] = (found["temp_max"] + found["temp_min"]) / 2.0   # WATUGA YC has no mean
        if "rh" in found:
            agg["rh"] = found["rh"]
        if "wind" in found:
            agg["wind"] = found["wind"]
        if "pressure_in" in found:
            agg["pressure"] = found["pressure_in"] * 33.8639               # inHg -> mb
        return {for_date: agg} if agg else None
    except Exception:
        return None


# ----------------------------------------------------------------- offsets + bands
def build_offsets(tempest, anchors):
    """tempest: {date: {var: val}}. anchors: {sid: {date: {var: val}}}.
    -> offsets[var][sid] = {date: tempest - anchor}, plus a flat list of csv rows."""
    offsets = defaultdict(lambda: defaultdict(dict))
    rows = []
    for date, tagg in tempest.items():
        for sid, days in anchors.items():
            aagg = days.get(date)
            if not aagg:
                continue
            for var in ("temp", "rh", "wind", "pressure"):
                if var in tagg and var in aagg:
                    off = round(tagg[var] - aagg[var], 2)
                    offsets[var][sid][date] = off
                    rows.append((date, sid, var, round(tagg[var], 2), round(aagg[var], 2), off))
    rows.sort()
    return offsets, rows


def _window(series, lo_date, hi_date):
    """series: {date_str: value} -> list of values with lo_date <= date <= hi_date."""
    return [v for ds, v in series.items() if lo_date <= ds <= hi_date]


def assess_variable(vcfg, offsets_by_anchor, ref_date):
    """Compute one variable's health from its per-anchor offset series.
    Returns the health.json variable dict + an internal {state, dir}."""
    var = vcfg["var"]
    capable = WIND_ANCHORS if var == "wind" else [a["id"] for a in ANCHORS if var in a["vars"]]
    capable = [sid for sid in capable if offsets_by_anchor.get(sid)]

    # pooled baseline = every capable anchor's offsets in the 28-day window ending 7 days ago
    base_lo = (ref_date - dt.timedelta(days=34)).isoformat()
    base_hi = (ref_date - dt.timedelta(days=7)).isoformat()
    cur_lo = (ref_date - dt.timedelta(days=6)).isoformat()
    cur_hi = ref_date.isoformat()
    pooled_base = []
    for sid in capable:
        pooled_base += _window(offsets_by_anchor[sid], base_lo, base_hi)

    # current 7-day mean offset per anchor (what the dashboard plots)
    offsets_7d = {}
    for sid in capable:
        m = mean(_window(offsets_by_anchor[sid], cur_lo, cur_hi))
        if m is not None:
            offsets_7d[sid] = round(m, 2)

    learning = len(pooled_base) < MIN_BASELINE or len(offsets_7d) < MIN_ANCHORS
    band = None
    if not learning:
        p5, p95 = percentile(pooled_base, 5), percentile(pooled_base, 95)
        med = median(pooled_base)
        half = max(vcfg["half"], (p95 - p5) / 2.0)
        band = [round(med - half, 2), round(med + half, 2)]

    # consecutive divergent days (>= MIN_ANCHORS anchors out the SAME side vs the band)
    direction, days_in_state = 0, 0
    if band:
        med = (band[0] + band[1]) / 2.0
        day = ref_date
        run_dir = None
        while True:
            ds = day.isoformat()
            highs = sum(1 for sid in capable
                        if ds in offsets_by_anchor[sid] and offsets_by_anchor[sid][ds] > band[1])
            lows = sum(1 for sid in capable
                       if ds in offsets_by_anchor[sid] and offsets_by_anchor[sid][ds] < band[0])
            present = any(ds in offsets_by_anchor[sid] for sid in capable)
            this_dir = 1 if highs >= MIN_ANCHORS else (-1 if lows >= MIN_ANCHORS else 0)
            if not present:                 # gap day — stop the run (can't confirm divergence)
                break
            if this_dir == 0:
                break
            if run_dir is None:
                run_dir = this_dir
            elif this_dir != run_dir:
                break
            days_in_state += 1
            day = day - dt.timedelta(days=1)
        direction = run_dir or 0

    # step-change jump: current 7-day offset far outside the band vs >= MIN_ANCHORS anchors
    jump = 0
    if band:
        jhi = band[1] + vcfg["jump"]
        jlo = band[0] - vcfg["jump"]
        jump_hi = sum(1 for sid, o in offsets_7d.items() if o > jhi)
        jump_lo = sum(1 for sid, o in offsets_7d.items() if o < jlo)
        jump = 1 if jump_hi >= MIN_ANCHORS else (-1 if jump_lo >= MIN_ANCHORS else 0)

    if learning or not vcfg.get("flagable"):
        state = "LEARNING" if learning else "OK"
    elif jump and direction:
        state = "FLAG"
    elif direction and days_in_state >= FLAG_DAYS:
        state = "FLAG"
    elif direction and days_in_state >= WATCH_DAYS:
        state = "WATCH"
    else:
        state = "OK"

    return {
        "var": var, "label": vcfg["label"], "unit": vcfg["unit"], "state": state,
        "days_in_state": days_in_state if state in ("WATCH", "FLAG") else 0,
        "current": None,  # filled by caller (Tempest recent value)
        "offsets_7d": offsets_7d,
        "band": band,
        "trend": [],      # filled by caller (weekly per-anchor offsets)
        "trend_only": vcfg.get("trend_only", False),
        "_capable": capable, "_direction": direction,
    }


def weekly_trend(offsets_by_anchor, capable, ref_date, weeks=12):
    """Per-anchor weekly mean offset for the offset-trend chart (most recent `weeks` weeks)."""
    by_week = defaultdict(lambda: defaultdict(list))
    cutoff = (ref_date - dt.timedelta(weeks=weeks)).isoformat()
    for sid in capable:
        for ds, off in offsets_by_anchor.get(sid, {}).items():
            if ds < cutoff:
                continue
            wk = (d(ds) - dt.timedelta(days=d(ds).weekday())).isoformat()
            by_week[wk][sid].append(off)
    rows = []
    for wk in sorted(by_week):
        row = {"week": wk}
        for sid in capable:
            m = mean(by_week[wk].get(sid, []))
            if m is not None:
                row[sid] = round(m, 2)
        rows.append(row)
    return rows


# ----------------------------------------------------------------- flag log + email
def load_state():
    s = load(STATE_FILE) or {}
    s.setdefault("flags", [])
    return s

def update_flag_log(state, variables, ref_date):
    """Maintain the canonical flag log: open a flag when a var enters WATCH/FLAG, resolve it
    when the var returns to OK/LEARNING. Returns (flags_list, newly_opened_keys)."""
    flags = state.get("flags", [])
    by_var_active = {f["var"]: f for f in flags if f.get("resolved") is None}
    newly_opened = []
    today = ref_date.isoformat()
    for v in variables:
        var, st = v["var"], v["state"]
        active = by_var_active.get(var)
        if st in ("WATCH", "FLAG"):
            if active is None:
                ds = sorted(v["offsets_7d"].items())
                desc = _flag_description(v)
                f = {"opened": today, "var": var, "state": st, "description": desc,
                     "action": "Scoreboard annotated", "resolved": None}
                flags.append(f)
                newly_opened.append("%s:%s" % (var, today))
            else:
                active["state"] = st        # WATCH may escalate to FLAG in place
                active["description"] = _flag_description(v)
        else:
            if active is not None:
                active["resolved"] = today
    state["flags"] = flags
    return flags, newly_opened

def _flag_description(v):
    names = ", ".join(sorted(v["offsets_7d"].keys()))
    dirn = "above" if v["_direction"] > 0 else "below"
    return ("%s offset drifted %s the normal band vs %s for %d consecutive days."
            % (v["label"], dirn, names, v["days_in_state"]))

def summarize(overall, variables):
    if overall == "LEARNING":
        return "Building baselines vs the verified anchors — flags arm once enough history accrues."
    flagged = [v for v in variables if v["state"] in ("WATCH", "FLAG")]
    if not flagged:
        return "All variables within their normal range vs the verified anchors."
    v = flagged[0]
    n = len(v["offsets_7d"])
    dirn = "warm" if (v["var"] in ("temp",) and v["_direction"] > 0) else \
           ("cool" if v["var"] == "temp" else ("high" if v["_direction"] > 0 else "low"))
    return "%s running %s vs %d of 3 anchors" % (v["label"], dirn, n)


# ----------------------------------------------------------------- assemble
def minimal_health(note=""):
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    stamp = now.isoformat().replace("+00:00", "Z")
    return {
        "generated_at": stamp, "last_check": stamp,
        "next_check": (now + dt.timedelta(days=1)).isoformat().replace("+00:00", "Z"),
        "overall": "LEARNING",
        "summary": "Building baselines vs the verified anchors." + (" (%s)" % note if note else ""),
        "days_monitored": 0, "active_watches": 0, "confirmed_faults": 0, "last_email": None,
        "location": "Statham, GA", "current_obs": {"as_of": None, "stations": {}},
        "anchors": [{"id": a["id"], "name": a["name"], "type": a["type"], "place": a["place"],
                     "dir": a["dir"], "miles": a["miles"], "elev_ft": a["elev_ft"],
                     "reporting": False, "variables": a["vars"]} for a in ANCHORS],
        "variables": [], "flags": [], "scoreboard_annotations": [],
    }


def archive_daily(payload, day):
    """Write an immutable per-day copy of the full health snapshot (history/health-YYYY-MM-DD.json)
    so a future 'replay this day' feature has the complete record — states, bands, live readings,
    flags — not just the offsets in anchors.csv. Keyed by the snapshot's generated date; same-day
    re-runs overwrite (idempotent). Non-fatal: never crash or trip the daily recovery path."""
    try:
        os.makedirs(HISTORY_DIR, exist_ok=True)
        with open(os.path.join(HISTORY_DIR, "health-%s.json" % day), "w") as f:
            f.write(payload)
    except Exception as e:                                 # noqa: BLE001
        print("[warn] history archive failed (non-fatal): %s" % e)


def main():
    day_dirs = sorted(g for g in glob.glob(os.path.join(DATA, "*")) if os.path.isdir(g))

    # Tempest daily aggregates (daily capture + the install-gap backfill device obs)
    tempest = {}
    anchors = defaultdict(dict)
    reporting = {sid: False for sid in ANCHOR_IDS}
    for dd in day_dirs:
        date, agg = tempest_daily(load(os.path.join(dd, "tempest_device_yesterday.json")))
        if date and agg:
            tempest[date] = agg
        md = metar_daily(load(os.path.join(dd, "anchors_metar.json")))
        for sid, days in md.items():
            anchors[sid].update(days)
            if days:
                reporting[sid] = True
        wd = watuga_daily(load(os.path.join(dd, "watuga.html")), date)
        if wd:
            anchors["WATUGA"].update(wd)
            reporting["WATUGA"] = True
    for bf in sorted(glob.glob(os.path.join(BASE, "backfill", "*.json"))):
        date, agg = tempest_daily(load(bf))
        if date and agg:
            tempest.setdefault(date, agg)

    # historical anchor baseline backfill (METAR aggregates ~June 1+), folded in
    abf = load(ANCHOR_BACKFILL)
    if isinstance(abf, dict):
        for sid, days in (abf.get("anchors") or {}).items():
            if sid in ANCHOR_IDS and isinstance(days, dict):
                for date, agg in days.items():
                    anchors[sid].setdefault(date, agg)
                    if agg:
                        reporting[sid] = True

    offsets, csv_rows = build_offsets(tempest, anchors)

    # rebuild anchors.csv (deterministic evidence vault — never blind-append)
    with open(ANCHORS_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "anchor", "var", "tempest", "anchor", "offset"])
        w.writerows(csv_rows)

    # reference date = the most recent day we have any offset for (anchored to data, not wall clock)
    all_dates = sorted({date for var in offsets.values() for sid in var.values() for date in sid})
    ref_date = d(all_dates[-1]) if all_dates else dt.datetime.now(NY).date()

    variables = []
    for vcfg in VARS:
        if vcfg["var"] == "rain":
            variables.append({"var": "rain", "label": "Rain", "unit": "in", "state": "OK",
                              "days_in_state": 0, "current": None, "offsets_7d": {}, "band": None,
                              "cross_check": vcfg["cross_check"], "trend": [],
                              "_capable": [], "_direction": 0})
            continue
        v = assess_variable(vcfg, offsets.get(vcfg["var"], {}), ref_date)
        # current = Tempest recent (7-day mean) value for this variable
        recent = [tempest[date][vcfg["var"]] for date in all_dates[-7:]
                  if date in tempest and vcfg["var"] in tempest[date]]
        v["current"] = round(mean(recent), 1) if recent else None
        v["trend"] = weekly_trend(offsets.get(vcfg["var"], {}), v["_capable"], ref_date) \
            if vcfg["var"] == "temp" else []
        variables.append(v)

    overall = STATE_NAME[max((STATE[v["state"]] for v in variables), default=STATE["LEARNING"])]

    # flag log + warning-email bookkeeping
    state = load_state()
    flags, newly_opened = update_flag_log(state, variables, ref_date)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

    emailed = load(EMAILED_FILE) or []
    pending_keys = [k for k in newly_opened if k not in emailed]
    last_email = None
    if emailed:
        last_email = max(k.split(":", 1)[1] for k in emailed if ":" in k)
    if pending_keys:
        new_flags = [f for f in flags if "%s:%s" % (f["var"], f["opened"]) in pending_keys]
        worst = max((v["state"] for v in variables if v["state"] in ("WATCH", "FLAG")),
                    key=lambda s: STATE[s], default="WATCH")
        labels = ", ".join(sorted({f["var"] for f in new_flags}))
        subject = "⚠ Station health: %s %s opened (vs KWDR, KAHN, WATUGA)" % (labels, worst)
        body_lines = ["A new station-health flag opened on %s (Statham, GA).\n" % ref_date.isoformat()]
        for f in new_flags:
            body_lines.append("  • %s [%s] — %s" % (f["var"], f["state"], f["description"]))
        body_lines += [
            "",
            "Flag, never override: the flagged days STAY in forecast scoring (annotate-only).",
            "The scoreboard now carries a ⚠ footnote for the overlapping days.",
            "",
            "Dashboard: https://damngooddawg.github.io/tempest-forecast-verify/dashboard.html#health",
        ]
        with open(PENDING_EMAIL, "w") as f:
            json.dump({"to": EMAIL_TO, "subject": subject, "body": "\n".join(body_lines),
                       "keys": pending_keys}, f, indent=2)
    elif os.path.exists(PENDING_EMAIL):
        os.remove(PENDING_EMAIL)   # nothing new this run — clear any stale pending email

    active = [f for f in flags if f.get("resolved") is None]
    annotations = [{"from": f["opened"], "to": f.get("resolved"), "var": f["var"]}
                   for f in active]
    days_monitored = (ref_date - d(INSTALL_DATE)).days + 1 if all_dates else 0

    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    out = {
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "last_check": now.isoformat().replace("+00:00", "Z"),
        "next_check": (now + dt.timedelta(days=1)).isoformat().replace("+00:00", "Z"),
        "overall": overall,
        "summary": summarize(overall, variables),
        "days_monitored": max(0, days_monitored),
        "active_watches": sum(1 for v in variables if v["state"] in ("WATCH", "FLAG")),
        "confirmed_faults": 0,    # named sensor-fault flags are listener-side (REST can't see them)
        "last_email": last_email,
        "location": "Statham, GA",
        "current_obs": current_observations(day_dirs, anchors),
        "anchors": [{"id": a["id"], "name": a["name"], "type": a["type"], "place": a["place"],
                     "dir": a["dir"], "miles": a["miles"], "elev_ft": a["elev_ft"],
                     "reporting": bool(reporting[a["id"]]), "variables": a["vars"]} for a in ANCHORS],
        "variables": [_clean_var(v) for v in variables],
        "flags": flags,
        "scoreboard_annotations": annotations,
    }
    payload = json.dumps(out, indent=2, allow_nan=False)
    with open(OUT, "w") as f:
        f.write(payload)
    archive_daily(payload, out["generated_at"][:10])      # immutable per-day snapshot copy
    print("[ok] health.json  overall=%s  vars=%d  anchor_days=%s  offsets=%d  ref=%s"
          % (overall, len(variables),
             {sid: len(anchors[sid]) for sid in ANCHOR_IDS}, len(csv_rows), ref_date))


def _clean_var(v):
    """Drop internal bookkeeping keys before serializing."""
    out = {k: val for k, val in v.items() if not k.startswith("_")}
    return out


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("health.py: unexpected error, writing minimal LEARNING health.json: %s" % e,
              file=sys.stderr)
        try:
            with open(OUT, "w") as f:
                f.write(json.dumps(minimal_health(note="recovered from an error"),
                                   indent=2, allow_nan=False))
        except Exception as e2:
            print("health.py: could not write fallback health.json: %s" % e2, file=sys.stderr)
        sys.exit(0)
