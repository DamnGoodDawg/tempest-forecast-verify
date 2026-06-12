#!/usr/bin/env python3
"""
extract.py - turn raw daily snapshots into scores.json (stdlib only).

Reads every data/YYYY-MM-DD/ snapshot, parses each provider's daily forecast into
tidy (date, lead, source, var, value) records, pulls observed actuals from the
Tempest station obs, scores everyone with verify.py, and writes scores.json in the
exact shape the dashboard expects (see claude-design-brief.md data contract).

Methodology (README.md): ForecastAdvisor-style. Temp accuracy = MAE and % within 3 F
over pooled high+low errors; precip occurrence CSI from PoP >= 50% vs observed wet
(>= 0.01"); PoP calibration Brier; paired Diebold-Mariano on the MAE loss differential
drives the headline verdict. Leads 1/2/3 plus a 1-3 blend.

Degrades gracefully: until >= MIN_VERDICT_N scored days exist the verdict reads
TOO EARLY, and any source/section with no data is simply omitted. This script must
NEVER crash the daily run -- on any unexpected error it still writes a minimal,
valid TOO EARLY scores.json and exits 0.
"""
import json, os, sys, glob, csv, io, datetime as dt
from collections import defaultdict
from zoneinfo import ZoneInfo

import verify

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
OUT = os.path.join(BASE, "scores.json")
NY = ZoneInfo("America/New_York")

INSTALL_DATE = "2026-05-31"
MILESTONES = {"window_opens": "2026-08-01", "five_month": "2026-10-31", "claim_deadline": "2027-01-25"}
LEADS = [1, 2, 3]
MIN_VERDICT_N = 30          # README: DM verdicts once cumulative n >= 30 (definitive at 90)
WET = 0.01                  # inches; matches NWS PoP definition
RAIN_SENSOR_MIN_V = 2.355   # at/below this, the haptic rain sensor silently disables
BATTERY_WARN_V = 2.40       # early-warning threshold (act before the 2.355 V cutoff)
SOURCES = ["Tempest", "NBM", "NWS", "ECMWF", "GFS"]
OM_MODELS = {"gfs_seamless": "GFS", "ecmwf_ifs025": "ECMWF", "ncep_nbm_conus": "NBM"}


# ---------------------------------------------------------------- date helpers
def d(s):  # 'YYYY-MM-DD' -> date
    return dt.date.fromisoformat(s)

def epoch_to_date(ep):
    return dt.datetime.fromtimestamp(int(ep), NY).date().isoformat()

def iso_to_date(s):
    return dt.datetime.fromisoformat(s).astimezone(NY).date().isoformat()

def lead_of(target, capture):
    try:
        return (d(target) - d(capture)).days
    except Exception:
        return None

def monday_of(date_str):
    dd = d(date_str)
    return (dd - dt.timedelta(days=dd.weekday())).isoformat()

def load(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None


# ---------------------------------------------------------------- forecast parsers
# Each returns a list of records {date, lead, source, var, value}; tolerant of gaps.
def rec(out, target, lead, source, var, value):
    if value is None or lead not in LEADS:
        return
    try:
        out.append({"date": target, "lead": lead, "source": source, "var": var, "value": float(value)})
    except (TypeError, ValueError):
        pass

def parse_tempest(j, capture):
    out = []
    daily = ((j or {}).get("data") or {}).get("forecast", {}).get("daily", []) or []
    for e in daily:
        ep = e.get("day_start_local")
        if ep is None:
            continue
        try:
            target = epoch_to_date(ep)
        except Exception:
            continue
        lead = lead_of(target, capture)
        rec(out, target, lead, "Tempest", "high", e.get("air_temp_high"))
        rec(out, target, lead, "Tempest", "low", e.get("air_temp_low"))
        rec(out, target, lead, "Tempest", "pop", e.get("precip_probability"))
    return out

def parse_openmeteo(j, capture):
    out = []
    daily = ((j or {}).get("data") or {}).get("daily", {}) or {}
    times = daily.get("time") or []
    for model, label in OM_MODELS.items():
        hi = daily.get(f"temperature_2m_max_{model}") or []
        lo = daily.get(f"temperature_2m_min_{model}") or []
        pp = daily.get(f"precipitation_probability_max_{model}") or []
        for i, t in enumerate(times):
            lead = lead_of(t, capture)
            if lead not in LEADS:
                continue
            rec(out, t, lead, label, "high", hi[i] if i < len(hi) else None)
            rec(out, t, lead, label, "low", lo[i] if i < len(lo) else None)
            rec(out, t, lead, label, "pop", pp[i] if i < len(pp) else None)
    return out

def parse_nws(j, capture):
    periods = ((j or {}).get("data") or {}).get("forecast", {}).get("properties", {}).get("periods", []) or []
    slots = {}

    def slot(key):
        return slots.setdefault(key, {"high": None, "low": None, "pops": []})

    for p in periods:
        st = p.get("startTime")
        if not st:
            continue
        try:
            base_date = iso_to_date(st)   # calendar date the period STARTS on
        except Exception:
            continue
        temp, isday = p.get("temperature"), p.get("isDaytime")

        # A1: a night period (startTime ~18:00 on day D, isDaytime=false) forecasts the
        # OVERNIGHT LOW that occurs in the EARLY MORNING of D+1. The old code keyed it to D,
        # so every NWS low was scored against a low that happened ~12-30 h earlier, inflating
        # NWS temp MAE. Attribute night-period temps to D+1 (standard NWS verification
        # convention) and re-derive the lead from that target date.
        if temp is not None:
            if isday:
                temp_target = base_date
            else:
                try:
                    temp_target = (d(base_date) + dt.timedelta(days=1)).isoformat()
                except Exception:
                    temp_target = base_date
            temp_lead = lead_of(temp_target, capture)
            if temp_lead in LEADS:
                s = slot((temp_target, temp_lead))
                if isday:
                    s["high"] = temp
                else:
                    s["low"] = temp

        # PoP convention unchanged: keyed to the calendar date the period TOUCHES (its start
        # date D), max over all periods touching D. Kept distinct from the temp target so the
        # A1 night-low shift does not move precip probability.
        pop = (p.get("probabilityOfPrecipitation") or {}).get("value")
        if pop is not None:
            pop_lead = lead_of(base_date, capture)
            if pop_lead in LEADS:
                slot((base_date, pop_lead))["pops"].append(pop)

    out = []
    for (target, lead), s in slots.items():
        rec(out, target, lead, "NWS", "high", s["high"])
        rec(out, target, lead, "NWS", "low", s["low"])
        if s["pops"]:
            rec(out, target, lead, "NWS", "pop", max(s["pops"]))
    return out


# ---------------------------------------------------------------- actuals + health
# Device obs_st positional array indices (raw values are METRIC). WeatherFlow obs_st schema.
OBS_AIRTEMP_C, OBS_BATTERY = 7, 16
OBS_RAIN_DAY_MM, OBS_RAIN_DAY_FINAL_MM = 18, 20  # raw vs RainCheck-corrected daily accum

# device_status.sensor_status bitmask -> hardware fault names (WebSocket-only field).
# Lightning noise/disturber bits (0x2/0x4) are environmental, not faults -> excluded.
SENSOR_FAULTS = [
    (0x00000001, "lightning failed"), (0x00000008, "pressure failed"),
    (0x00000010, "temperature failed"), (0x00000020, "humidity failed"),
    (0x00000040, "wind failed"), (0x00000080, "precip (rain) failed"),
    (0x00000100, "light/UV failed"),
]

def _cell(row, i):
    return row[i] if isinstance(row, (list, tuple)) and len(row) > i else None

def c_to_f(c):
    return c * 9.0 / 5.0 + 32.0

def parse_actuals(device_json):
    """Yesterday's per-minute device obs (obs_st arrays) -> {(date,var): value}.
    Temperature truth = max/min of air_temperature (C->F); precip = corrected daily
    total if present, else raw (mm->in). The Tempest station is the methodology's truth
    source; CoCoRaHS will refine precip amounts later (README open item)."""
    out = {}
    if not device_json:
        return out
    target = device_json.get("for_date")
    obs = ((device_json.get("data") or {}).get("obs")) or []
    if not target or not obs:
        return out
    temps = [_cell(r, OBS_AIRTEMP_C) for r in obs]
    temps = [t for t in temps if isinstance(t, (int, float))]
    if temps:
        out[(target, "high")] = round(c_to_f(max(temps)), 1)
        out[(target, "low")] = round(c_to_f(min(temps)), 1)
    rain_final = [x for x in (_cell(r, OBS_RAIN_DAY_FINAL_MM) for r in obs) if isinstance(x, (int, float))]
    rain_raw = [x for x in (_cell(r, OBS_RAIN_DAY_MM) for r in obs) if isinstance(x, (int, float))]
    series = rain_final or rain_raw   # prefer RainCheck-corrected; either is a daily accumulator
    if series:
        out[(target, "precip_amt")] = round(max(series) / 25.4, 3)  # mm -> in
    return out

def parse_device_health(device_json):
    """Battery voltage from the most recent obs_st row (index 16). Sensor-fault flags
    aren't exposed on personal-token endpoints, so the list stays empty for now."""
    out = {"battery_volts": None, "sensor_faults": []}
    if not device_json:
        return out
    obs = ((device_json.get("data") or {}).get("obs")) or []
    for r in reversed(obs):
        b = _cell(r, OBS_BATTERY)
        if isinstance(b, (int, float)):
            out["battery_volts"] = round(float(b), 3)
            break
    return out

def parse_tempest_rain(device_json):
    """Yesterday's Tempest daily rain totals -> (date, raw_in, corrected_in).
    raw = haptic accumulator (idx 18), corrected = RainCheck/NC (idx 20); mm -> in."""
    if not device_json:
        return None
    target = device_json.get("for_date")
    obs = ((device_json.get("data") or {}).get("obs")) or []
    if not target or not obs:
        return None
    raw = [x for x in (_cell(r, OBS_RAIN_DAY_MM) for r in obs) if isinstance(x, (int, float))]
    cor = [x for x in (_cell(r, OBS_RAIN_DAY_FINAL_MM) for r in obs) if isinstance(x, (int, float))]
    return (target,
            round(max(raw) / 25.4, 3) if raw else None,
            round(max(cor) / 25.4, 3) if cor else None)

def parse_device_status(ds_json):
    """WebSocket device_status/hub_status -> decoded sensor faults + RSSI.
    sensor_faults: list of fault names ([] = all sensors OK), or None if unavailable."""
    out = {"sensor_faults": None, "rssi": None, "hub_rssi": None}
    if not ds_json:
        return out
    data = ds_json.get("data") or {}
    ds = data.get("device_status") or {}
    hs = data.get("hub_status") or {}
    ss = ds.get("sensor_status")
    if ss is not None:
        try:
            out["sensor_faults"] = [name for bit, name in SENSOR_FAULTS if int(ss) & bit]
        except (TypeError, ValueError):
            out["sensor_faults"] = None
    out["rssi"] = ds.get("rssi")
    out["hub_rssi"] = hs.get("rssi")
    return out

def parse_cocorahs(cocorahs_json):
    """CoCoRaHS daily CSV -> {ObservationDate 'YYYY-MM-DD': precip inches}. Trace -> 0.0.
    NOTE on attribution: a CoCoRaHS report dated D is the ~24h total ending at the
    observer's morning reading on D, i.e. mostly calendar day D-1's rain. The caller
    shifts it back one day to align with the Tempest local-calendar-day truth."""
    out = {}
    if not cocorahs_json:
        return out
    text = cocorahs_json.get("csv") or ""
    try:
        for row in csv.DictReader(io.StringIO(text)):
            date = (row.get("ObservationDate") or "").strip()
            amt = (row.get("TotalPrecipAmt") or "").strip()
            if not date:
                continue
            if amt.upper() in ("T", "TRACE"):
                out[date] = 0.0
            elif amt and amt.upper() != "NA":
                try:
                    out[date] = float(amt)
                except ValueError:
                    pass
    except Exception:
        pass
    return out


# ---------------------------------------------------------------- scoring
def temp_errors(records, actuals, src, leads):
    """Combined high+low signed errors for a source over the given lead(s)."""
    leadset = leads if isinstance(leads, (list, tuple, set)) else {leads}
    errs, dates = [], set()
    for r in records:
        if r["source"] == src and r["lead"] in leadset and r["var"] in ("high", "low"):
            key = (r["date"], r["var"])
            if key in actuals:
                errs.append(r["value"] - actuals[key])
                dates.add(r["date"])
    return errs, dates

def temp_errors_keyed(records, actuals, src, lead):
    """{(date,var): error} for paired DM."""
    out = {}
    for r in records:
        if r["source"] == src and r["lead"] == lead and r["var"] in ("high", "low"):
            key = (r["date"], r["var"])
            if key in actuals:
                out[key] = r["value"] - actuals[key]
    return out

def precip_pairs(records, actuals, src, leads, wet):
    leadset = leads if isinstance(leads, (list, tuple, set)) else {leads}
    pop_pairs, yn_pairs = [], []
    for r in records:
        if r["source"] == src and r["lead"] in leadset and r["var"] == "pop" and r["date"] in wet:
            pop_pairs.append((r["value"], wet[r["date"]]))
            yn_pairs.append((r["value"] >= 50, wet[r["date"]]))
    return pop_pairs, yn_pairs

def _finite(x, ndigits):
    """Round x, but collapse None/NaN/inf to None so they never reach json.dump (A3).
    contingency() returns csi=NaN when hits+misses+false_alarms == 0 (an all-dry window);
    a literal NaN poisons scores.json (invalid JSON) and strands the dashboard on sample
    data, so it must become a clean null here."""
    if x is None:
        return None
    try:
        if x != x or x in (float("inf"), float("-inf")):   # NaN or inf
            return None
        return round(x, ndigits)
    except (TypeError, ValueError):
        return None

def source_row(records, actuals, wet, src, leads):
    errs, dates = temp_errors(records, actuals, src, leads)
    if not errs:
        return None, dates
    row = {"source": src,
           "mae": round(verify.mae(errs), 2),
           "pct_within_3f": int(round(verify.pct_within(errs)))}
    pop_pairs, yn_pairs = precip_pairs(records, actuals, src, leads, wet)
    row["csi"] = _finite(verify.contingency(yn_pairs)["csi"], 2) if yn_pairs else None
    row["brier"] = _finite(verify.brier(pop_pairs)["brier"], 3) if pop_pairs else None
    return row, dates

def standings_for(records, actuals, wet, leads):
    rows = []
    for src in SOURCES:
        row, _ = source_row(records, actuals, wet, src, leads)
        if row:
            rows.append(row)
    rows.sort(key=lambda r: r["mae"])
    return rows


# ---------------------------------------------------------------- assemble
def build(records, actuals, wet):
    standings = {f"lead{L}": standings_for(records, actuals, wet, L) for L in LEADS}
    standings["blend"] = standings_for(records, actuals, wet, LEADS)

    # verdict from lead1 MAE + Diebold-Mariano (Tempest vs best public)
    l1 = standings["lead1"]
    _, t_dates = temp_errors(records, actuals, "Tempest", 1)
    n_days = len(t_dates)
    tempest = next((r for r in l1 if r["source"] == "Tempest"), None)
    publics = [r for r in l1 if r["source"] != "Tempest"]
    best = publics[0] if publics else None   # l1 already sorted by mae

    verdict = {"status": "TOO EARLY", "headline": "", "n_days": n_days,
               "dm_p_value": None, "best_public": best["source"] if best else None}

    if tempest and best and n_days >= MIN_VERDICT_N:
        # A6: DM on per-date collapsed losses (mean of |high|,|low|) — one obs per date,
        # not two correlated ones — with the HLN small-sample correction inside verify.
        loss = verify.per_date_losses(records, actuals, 1)
        ta = loss.get("Tempest", {})
        ba = loss.get(best["source"], {})
        common = sorted(set(ta) & set(ba))
        dm = verify.diebold_mariano([ta[k] for k in common], [ba[k] for k in common], h=1) if len(common) >= 10 else {}
        p = dm.get("p_value")
        verdict["dm_p_value"] = p
        tempest_better = tempest["mae"] <= best["mae"]
        if p is not None and p < 0.05:
            verdict["status"] = "TEMPEST AHEAD" if tempest_better else "TEMPEST BEHIND"
        else:
            verdict["status"] = "TIED"
        verb = {"TEMPEST AHEAD": "ahead of", "TEMPEST BEHIND": "behind", "TIED": "statistically tied with"}[verdict["status"]]
        verdict["headline"] = (f"Tempest is within 3°F on {tempest['pct_within_3f']}% of days vs "
                               f"{best['source']}'s {best['pct_within_3f']}% — {verb} the best public forecast so far.")
    else:
        need = max(0, MIN_VERDICT_N - n_days)
        verdict["headline"] = (f"Only {n_days} scored day{'s' if n_days != 1 else ''} so far — "
                               f"need ~{need} more for a first verdict (90 for a definitive one). "
                               f"Capture is running; check back as data accrues.")

    # weekly MAE trend per provider at lead1
    trend = {}
    for r in records:
        if r["lead"] == 1 and r["var"] in ("high", "low") and (r["date"], r["var"]) in actuals:
            wk = monday_of(r["date"])
            trend.setdefault(wk, defaultdict(list))[r["source"]].append(abs(r["value"] - actuals[(r["date"], r["var"])]))
    trend_rows = []
    for wk in sorted(trend):
        row = {"week": wk}
        for src in SOURCES:
            vals = trend[wk].get(src)
            if vals:
                row[src] = round(sum(vals) / len(vals), 2)
        trend_rows.append(row)

    # biggest high-temp busts across the most recent 7 scored target dates
    scored_dates = sorted({r["date"] for r in records
                           if r["lead"] == 1 and r["var"] == "high" and (r["date"], "high") in actuals})
    recent = set(scored_dates[-7:])
    cand = []
    for r in records:
        if r["lead"] == 1 and r["var"] == "high" and r["date"] in recent and (r["date"], "high") in actuals:
            a = actuals[(r["date"], "high")]
            cand.append((abs(r["value"] - a), {"date": r["date"], "source": r["source"], "var": "high",
                                               "forecast": round(r["value"]), "actual": round(a)}))
    cand.sort(key=lambda x: -x[0])
    busts = [c[1] for c in cand[:3] if c[0] >= 3]   # only list genuine misses (>=3 F off)

    return standings, verdict, trend_rows, busts, n_days


def data_health(day_dirs, latest_device, cocorahs_ok, hub_online, latest_ds):
    # A2 / audit M7: count misses against the EXPECTED calendar span, not just the
    # directories that happen to exist. Days the workflow never ran leave no directory at
    # all, so the old `sum over day_dirs` could never see them — the miss count and streak
    # stayed green through a total outage. Build the set of dates that DID capture the
    # irreplaceable Tempest snapshot, then measure against first-capture..today inclusive.
    have_tempest = set()
    for dd in day_dirs:
        if os.path.exists(os.path.join(dd, "tempest.json")):
            try:
                have_tempest.add(d(os.path.basename(dd)))
            except Exception:
                pass

    today_local = dt.datetime.now(NY).date()
    capture_dates = []
    for dd in day_dirs:
        try:
            capture_dates.append(d(os.path.basename(dd)))
        except Exception:
            pass
    if capture_dates:
        first = min(capture_dates)
        expected_days = max((today_local - first).days + 1, len(capture_dates))
    else:
        expected_days = 0
    capture_days = expected_days                       # denominator = days we SHOULD have
    misses = max(0, expected_days - len(have_tempest)) # incl. days with no directory at all

    # current streak: consecutive most-recent CALENDAR days (ending today) that captured.
    # A missing day — even one with no directory — now breaks the streak.
    streak = 0
    cur = today_local
    while cur in have_tempest:
        streak += 1
        cur = cur - dt.timedelta(days=1)

    # hours since newest snapshot
    last_hours = None
    if day_dirs:
        newest = sorted(day_dirs)[-1]
        log = load(os.path.join(newest, "_capture_log.json")) or {}
        stamp = (log.get("meta") or {}).get("captured_at_utc")
        try:
            if stamp:
                ts = dt.datetime.fromisoformat(stamp)
            else:
                ts = dt.datetime.fromisoformat(os.path.basename(newest)).replace(tzinfo=dt.timezone.utc)
            last_hours = int((dt.datetime.now(dt.timezone.utc) - ts).total_seconds() // 3600)
        except Exception:
            last_hours = None

    diag = parse_device_health(latest_device)
    batt = diag["battery_volts"]
    dsx = parse_device_status(latest_ds)   # sensor faults + RSSI from WebSocket device_status
    return {
        "capture_days": capture_days,
        "capture_misses": misses,
        "station_online_streak": streak,
        "hub_online": hub_online,       # latest is_station_online from better_forecast (None if unknown)
        "cocorahs_ok": cocorahs_ok,     # True=feed fresh, False=feed seen but stale/empty, None=never captured
        "last_snapshot_hours_ago": last_hours if last_hours is not None else 0,
        "battery_volts": batt,
        "battery_warn": batt is not None and batt <= BATTERY_WARN_V,   # early warning before 2.355 cutoff
        "rain_sensor_ok": (batt is None) or (batt > RAIN_SENSOR_MIN_V),
        # sensor_faults: list of failed sensors ([] = all OK), or None if the WebSocket
        # device_status poll didn't land this run. rssi/hub_rssi in dBm (None if unknown).
        "sensor_faults": dsx["sensor_faults"],
        "rssi": dsx["rssi"],
        "hub_rssi": dsx["hub_rssi"],
    }


def empty_scores(note=""):
    return {
        "generated_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "install_date": INSTALL_DATE, "milestones": MILESTONES,
        "verdict": {"status": "TOO EARLY",
                    "headline": "No scored data yet — daily capture is running; the first verdict appears once "
                                "forecasts can be checked against observed actuals." + (f" ({note})" if note else ""),
                    "n_days": 0, "dm_p_value": None, "best_public": None},
        "standings": {"lead1": [], "lead2": [], "lead3": [], "blend": []},
        "trend": [], "busts": [], "rain_compare": [],
        "data_health": {"capture_days": 0, "capture_misses": 0, "station_online_streak": 0,
                        "hub_online": None, "cocorahs_ok": None, "last_snapshot_hours_ago": 0,
                        "battery_volts": None, "battery_warn": False, "rain_sensor_ok": True,
                        "sensor_faults": None, "rssi": None, "hub_rssi": None},
    }


def main():
    day_dirs = sorted(g for g in glob.glob(os.path.join(DATA, "*")) if os.path.isdir(g))
    records, actuals, latest_device, latest_ds = [], {}, None, None
    cocorahs, cocorahs_seen, hub_online = {}, False, None
    tempest_rain = {}   # date -> {raw, corrected} daily totals (inches)
    for dd in day_dirs:
        capture = os.path.basename(dd)
        tj = load(os.path.join(dd, "tempest.json"))
        records += parse_tempest(tj, capture)
        if tj:
            online = ((tj.get("data") or {}).get("station") or {}).get("is_station_online")
            if online is not None:
                hub_online = bool(online)
        records += parse_openmeteo(load(os.path.join(dd, "openmeteo.json")), capture)
        records += parse_nws(load(os.path.join(dd, "nws.json")), capture)
        dev = load(os.path.join(dd, "tempest_device_yesterday.json"))
        actuals.update(parse_actuals(dev))
        if dev:
            latest_device = dev
        tr = parse_tempest_rain(dev)
        if tr and (tr[1] is not None or tr[2] is not None):
            tempest_rain[tr[0]] = {"raw": tr[1], "corrected": tr[2]}
        ds = load(os.path.join(dd, "device_status.json"))
        if ds:
            latest_ds = ds
        cj = load(os.path.join(dd, "cocorahs.json"))
        if cj is not None:
            cocorahs_seen = True
            cocorahs.update(parse_cocorahs(cj))

    # Historical device-obs backfill (e.g. the install gap before daily capture began).
    # Folded into actuals + rain totals, but NOT counted as daily captures / health.
    for bf in sorted(glob.glob(os.path.join(BASE, "backfill", "*.json"))):
        bj = load(bf)
        actuals.update(parse_actuals(bj))
        tr = parse_tempest_rain(bj)
        if tr and (tr[1] is not None or tr[2] is not None):
            tempest_rain[tr[0]] = {"raw": tr[1], "corrected": tr[2]}

    # A7: snapshot the Tempest device-obs precip occurrence BEFORE CoCoRaHS overrides the
    # amounts, so the wet/dry truth can be Tempest OR CoCoRaHS rather than CoCoRaHS alone.
    tempest_precip = {dte: v for (dte, var), v in actuals.items() if var == "precip_amt"}

    # CoCoRaHS is the precip-AMOUNT truth (Tempest haptic under-reports). Attribute a
    # report dated D back to calendar day D-1, and override the Tempest precip AMOUNT there.
    cocorahs_cal = {}
    for obsdate, amt in cocorahs.items():
        try:
            cal = (d(obsdate) - dt.timedelta(days=1)).isoformat()
        except Exception:
            continue
        cocorahs_cal[cal] = amt
        actuals[(cal, "precip_amt")] = amt
    today = dt.datetime.now(NY).date()
    fresh = any((today - d(x)).days <= 8 for x in cocorahs_cal)   # keys are valid ISO dates
    cocorahs_ok = True if fresh else (False if cocorahs_seen else None)

    # A7: occurrence (wet/dry) truth = Tempest device-obs OR CoCoRaHS gauge. The haptic can
    # miss light rain; the gauge sits ~2.6 mi away and can miss a convective cell over the
    # station — OR-ing them is the conservative occurrence map. Amounts stay CoCoRaHS-truth
    # (set in actuals above); this only drives the wet/dry classification used for CSI/Brier.
    wet = {dte: (v >= WET) for (dte, var), v in actuals.items() if var == "precip_amt"}
    for dte, v in tempest_precip.items():
        if v is not None and v >= WET:
            wet[dte] = True

    # Rain comparison: Tempest (raw haptic vs RainCheck-corrected) vs the CoCoRaHS gauge.
    # Tests the known haptic under-reporting and whether RainCheck helps or hurts here.
    # A7: surface (don't silently resolve) any wet/dry DISAGREEMENT via a `flag` field.
    rain_compare = []
    for dd_ in sorted(set(tempest_rain) | set(cocorahs_cal))[-21:]:
        tr = tempest_rain.get(dd_, {})
        t_amt = tr.get("corrected") if tr.get("corrected") is not None else tr.get("raw")
        c_amt = cocorahs_cal.get(dd_)
        flag = None
        if t_amt is not None and c_amt is not None and (t_amt >= WET) != (c_amt >= WET):
            flag = "disagree"
        rain_compare.append({
            "date": dd_,
            "tempest_raw": tr.get("raw"),
            "tempest_corrected": tr.get("corrected"),
            "cocorahs": c_amt,
            "flag": flag,
        })

    standings, verdict, trend, busts, n_days = build(records, actuals, wet)
    scores = {
        "generated_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "install_date": INSTALL_DATE, "milestones": MILESTONES,
        "verdict": verdict, "standings": standings, "trend": trend, "busts": busts,
        "rain_compare": rain_compare,
        "data_health": data_health(day_dirs, latest_device, cocorahs_ok, hub_online, latest_ds),
    }
    # A3: serialize to a string with allow_nan=False FIRST, so a stray NaN/inf raises
    # before we truncate the existing good file (and fails loudly rather than emitting
    # invalid JSON that would strand the dashboard on baked-in sample data).
    payload = json.dumps(scores, indent=2, allow_nan=False)
    with open(OUT, "w") as f:
        f.write(payload)
    print(f"[ok] scores.json  status={verdict['status']}  n_days={n_days}  "
          f"records={len(records)}  actuals={len(actuals)}  days={len(day_dirs)}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # A4: never crash the daily run, and never clobber a known-good scores.json. Only
        # write the empty TOO EARLY fallback when no scores.json exists yet; otherwise leave
        # the last good file in place and just stamp it `degraded` so the failure is visible.
        print(f"extract.py: unexpected error, preserving last good scores.json: {e}", file=sys.stderr)
        stamp = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        try:
            if not os.path.exists(OUT):
                payload = json.dumps(empty_scores(note="extract recovered from an error"),
                                     indent=2, allow_nan=False)
                with open(OUT, "w") as f:
                    f.write(payload)
            else:
                # Stamp the retained good file (string-first so a failed write can't corrupt it).
                existing = json.load(open(OUT))
                existing["degraded"] = True
                existing["degraded_at"] = stamp
                existing["degraded_reason"] = str(e)
                payload = json.dumps(existing, indent=2, allow_nan=False)
                with open(OUT, "w") as f:
                    f.write(payload)
        except Exception as e2:
            print(f"extract.py: could not update scores.json fallback: {e2}", file=sys.stderr)
        sys.exit(0)
