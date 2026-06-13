#!/usr/bin/env python3
"""
backfill_anchors.py - one-time(ish) METAR-anchor baseline backfill (stdlib only).

The AWC METAR JSON API returns up to ~400 records per station per call. For the hourly
KAHN that's ~13-16 days of history; for the more frequent KWDR ~4 days. Fetching each
anchor separately maximizes depth, so the 28-day station-health baseline arms quickly
instead of waiting a month of live captures. WATUGA has no comparable history endpoint, so
it simply accumulates from launch (documented gap).

Writes anchors_backfill.json:
  {"generated_at": "...", "anchors": {"KWDR": {"YYYY-MM-DD": {"temp":.., "rh":.., ...}}, ...}}
which health.py folds in WITHOUT counting as live captures. Re-running overwrites it with a
fresh, deeper-where-possible snapshot; health.py uses setdefault so live days win on overlap.

Usage:  python backfill_anchors.py            # KWDR + KAHN, max history (~400 obs each)
        python backfill_anchors.py 600         # request more hours (still server-capped)
"""
import json, os, sys, urllib.request, urllib.parse, datetime as dt

# Reuse health.py's parsing + aggregation so backfill and live use IDENTICAL math.
import health

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "anchors_backfill.json")
UA = "tempest-forecast-verify/1.0 (tkb5047@gmail.com)"
IDS = ["KWDR", "KAHN"]


def fetch(ids, hours):
    url = "https://aviationweather.gov/api/data/metar?" + urllib.parse.urlencode(
        {"ids": ids, "format": "json", "hours": hours})
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def main():
    hours = int(sys.argv[1]) if len(sys.argv) > 1 else 720   # request 30d; server caps at ~400 obs
    out = {"anchors": {}}
    for sid in IDS:
        try:
            raw = fetch(sid, hours)
        except Exception as e:
            print("backfill_anchors: %s fetch failed: %s" % (sid, e), file=sys.stderr)
            continue
        daily = health.metar_daily({"data": raw})   # {sid: {date: {var: val}}}
        days = daily.get(sid, {})
        # round for a tidy committed artifact
        out["anchors"][sid] = {date: {k: round(v, 2) for k, v in agg.items()}
                               for date, agg in sorted(days.items())}
        print("[ok] %s: %d days (%s .. %s)" % (
            sid, len(days),
            min(days) if days else "-", max(days) if days else "-"))
    out["generated_at"] = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)\
        .isoformat().replace("+00:00", "Z")
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    print("[ok] wrote %s" % OUT)


if __name__ == "__main__":
    main()
