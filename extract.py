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
import json, os, sys, glob, datetime as dt
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
    for p in periods:
        st = p.get("startTime")
        if not st:
            continue
        try:
            target = iso_to_date(st)
        except Exception:
            continue
        lead = lead_of(target, capture)
        if lead not in LEADS:
            continue
        s = slots.setdefault((target, lead), {"high": None, "low": None, "pops": []})
        temp, isday = p.get("temperature"), p.get("isDaytime")
        if temp is not None:
            if isday:
                s["high"] = temp
            else:
                s["low"] = temp
        pop = (p.get("probabilityOfPrecipitation") or {}).get("value")
        if pop is not None:
            s["pops"].append(pop)
    out = []
    for (target, lead), s in slots.items():
        rec(out, target, lead, "NWS", "high", s["high"])
        rec(out, target, lead, "NWS", "low", s["low"])
        if s["pops"]:
            rec(out, target, lead, "NWS", "pop", max(s["pops"]))
    return out


# ---------------------------------------------------------------- actuals + health
def _first(obj, keys):
    for k in keys:
        if isinstance(obj, dict) and obj.get(k) is not None:
            return obj.get(k)
    return None

def parse_actuals(j):
    """Tempest station obs (daily bucket) for one prior day -> {(date,var): value}.
    Keeps it simple for occurrence scoring; CoCoRaHS will arbitrate precip amounts later."""
    out = {}
    if not j:
        return out
    target = j.get("for_date")
    obs = ((j.get("data") or {}).get("obs")) or []
    if not target or not obs:
        return out
    o = obs[-1] if isinstance(obs, list) else obs
    if not isinstance(o, dict):
        return out
    hi = _first(o, ["air_temp_high", "air_temperature_high", "air_temp_high_24h"])
    lo = _first(o, ["air_temp_low", "air_temperature_low", "air_temp_low_24h"])
    # raw haptic and rain-check/NC-corrected are both in the dumped obs; either works
    # for the 0.01" wet/dry test. Prefer the corrected 'final' if present.
    pr = _first(o, ["precip_accum_local_day_final", "precip_accum_local_day",
                    "precip_total_1h", "precipitation_total", "precip"])
    for var, val in (("high", hi), ("low", lo), ("precip_amt", pr)):
        if val is not None:
            try:
                out[(target, var)] = float(val)
            except (TypeError, ValueError):
                pass
    return out

def _find_number(obj, name_substrs, lo=1.0, hi=5.0):
    """Best-effort recursive search for a plausible numeric value whose key contains
    any of name_substrs (used for battery voltage; tolerant of unknown schema)."""
    found = []
    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, (int, float)) and any(s in k.lower() for s in name_substrs):
                    if lo <= v <= hi:
                        found.append(v)
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(obj)
    return found[0] if found else None

def parse_diagnostics(j):
    """Best-effort: battery voltage + any sensor fault flags. Schema-tolerant."""
    out = {"battery_volts": None, "sensor_faults": []}
    if not j:
        return out
    data = j.get("data") or j
    out["battery_volts"] = _find_number(data, ["battery", "voltage", "volt"], 1.0, 5.0)
    # collect any boolean-ish fault/status flags that read as "not ok"
    faults = []
    def walk(o, path=""):
        if isinstance(o, dict):
            for k, v in o.items():
                kl = k.lower()
                if ("fault" in kl or "fail" in kl) and v not in (None, 0, False, "", "0", "ok", "OK"):
                    faults.append(k)
                walk(v, k)
        elif isinstance(o, list):
            for v in o:
                walk(v, path)
    walk(data)
    out["sensor_faults"] = sorted(set(faults))
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

def source_row(records, actuals, wet, src, leads):
    errs, dates = temp_errors(records, actuals, src, leads)
    if not errs:
        return None, dates
    row = {"source": src,
           "mae": round(verify.mae(errs), 2),
           "pct_within_3f": int(round(verify.pct_within(errs)))}
    pop_pairs, yn_pairs = precip_pairs(records, actuals, src, leads, wet)
    row["csi"] = round(verify.contingency(yn_pairs)["csi"], 2) if yn_pairs else None
    row["brier"] = round(verify.brier(pop_pairs)["brier"], 3) if pop_pairs else None
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
def build(records, actuals):
    wet = {dd: v >= WET for (dd, var), v in actuals.items() if var == "precip_amt"}

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
        ta = temp_errors_keyed(records, actuals, "Tempest", 1)
        ba = temp_errors_keyed(records, actuals, best["source"], 1)
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


def data_health(day_dirs, latest_diag):
    capture_days = len(day_dirs)
    # total days missing the irreplaceable Tempest snapshot
    misses = sum(1 for dd in day_dirs if not os.path.exists(os.path.join(dd, "tempest.json")))
    # current streak: consecutive most-recent days that DID capture Tempest
    streak = 0
    for dd in sorted(day_dirs, reverse=True):
        if os.path.exists(os.path.join(dd, "tempest.json")):
            streak += 1
        else:
            break

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

    diag = parse_diagnostics(latest_diag)
    return {
        "capture_days": capture_days,
        "capture_misses": misses,
        "station_online_streak": streak,
        "cocorahs_ok": None,            # CoCoRaHS fetcher not yet wired (README open item) -> n/a
        "last_snapshot_hours_ago": last_hours if last_hours is not None else 0,
        "battery_volts": diag["battery_volts"],
        "rain_sensor_ok": (diag["battery_volts"] is None) or (diag["battery_volts"] > RAIN_SENSOR_MIN_V),
        "sensor_faults": diag["sensor_faults"],
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
        "trend": [], "busts": [],
        "data_health": {"capture_days": 0, "capture_misses": 0, "station_online_streak": 0,
                        "cocorahs_ok": None, "last_snapshot_hours_ago": 0,
                        "battery_volts": None, "rain_sensor_ok": True, "sensor_faults": []},
    }


def main():
    day_dirs = sorted(g for g in glob.glob(os.path.join(DATA, "*")) if os.path.isdir(g))
    records, actuals, latest_diag = [], {}, None
    for dd in day_dirs:
        capture = os.path.basename(dd)
        records += parse_tempest(load(os.path.join(dd, "tempest.json")), capture)
        records += parse_openmeteo(load(os.path.join(dd, "openmeteo.json")), capture)
        records += parse_nws(load(os.path.join(dd, "nws.json")), capture)
        actuals.update(parse_actuals(load(os.path.join(dd, "tempest_obs_yesterday.json"))))
        diag = load(os.path.join(dd, "diagnostics.json"))
        if diag:
            latest_diag = diag

    standings, verdict, trend, busts, n_days = build(records, actuals)
    scores = {
        "generated_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "install_date": INSTALL_DATE, "milestones": MILESTONES,
        "verdict": verdict, "standings": standings, "trend": trend, "busts": busts,
        "data_health": data_health(day_dirs, latest_diag),
    }
    with open(OUT, "w") as f:
        json.dump(scores, f, indent=2)
    print(f"[ok] scores.json  status={verdict['status']}  n_days={n_days}  "
          f"records={len(records)}  actuals={len(actuals)}  days={len(day_dirs)}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Never crash the daily run -- emit a safe TOO EARLY scores.json and carry on.
        print(f"extract.py: unexpected error, writing safe fallback: {e}", file=sys.stderr)
        try:
            with open(OUT, "w") as f:
                json.dump(empty_scores(note="extract recovered from an error"), f, indent=2)
        except Exception as e2:
            print(f"extract.py: could not write fallback scores.json: {e2}", file=sys.stderr)
        sys.exit(0)
