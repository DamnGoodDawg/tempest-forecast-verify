#!/usr/bin/env python3
"""
test_health.py - unit tests for the station-health engine (stdlib unittest).

Covers the gate-A cases from the build kickoff:
  - drift vs >= 2 anchors, same direction, opens WATCH (3 days) then FLAG (5 days)
  - a step-change jump opens FLAG immediately
  - single-anchor divergence does NOT flag ("weather, not fault")
  - WATUGA parse failure returns None (the run continues on 2 anchors)
  - insufficient baseline reads LEARNING
  - the physics helpers (SLP reduction, RH from dewpoint) and METAR bucketing
"""
import unittest, datetime as dt
import health


def vcfg(var):
    return next(v for v in health.VARS if v["var"] == var)


def series(ref, n_base, recent):
    """Build a per-anchor offset series: n_base in-band (0.0) baseline days ending ref-7,
    then `recent` = list of (days_ago, offset) for the current window."""
    s = {}
    for i in range(n_base):
        day = (ref - dt.timedelta(days=8 + i)).isoformat()   # ref-8 backwards (inside baseline)
        s[day] = 0.0
    for days_ago, off in recent:
        s[(ref - dt.timedelta(days=days_ago)).isoformat()] = off
    return s


class TestAssess(unittest.TestCase):
    ref = dt.date(2026, 6, 30)

    def test_learning_when_baseline_thin(self):
        offs = {"KWDR": series(self.ref, 3, [(0, 2.0)]), "KAHN": series(self.ref, 3, [(0, 2.0)])}
        v = health.assess_variable(vcfg("temp"), offs, self.ref)
        self.assertEqual(v["state"], "LEARNING")

    def test_watch_on_3day_drift_two_anchors(self):
        recent = [(0, 2.0), (1, 2.0), (2, 2.0)]
        offs = {"KWDR": series(self.ref, 25, recent), "KAHN": series(self.ref, 25, recent)}
        v = health.assess_variable(vcfg("temp"), offs, self.ref)
        self.assertEqual(v["state"], "WATCH")
        self.assertEqual(v["days_in_state"], 3)
        self.assertEqual(v["_direction"], 1)

    def test_flag_on_5day_drift(self):
        recent = [(i, 2.0) for i in range(5)]
        offs = {"KWDR": series(self.ref, 25, recent), "KAHN": series(self.ref, 25, recent)}
        v = health.assess_variable(vcfg("temp"), offs, self.ref)
        self.assertEqual(v["state"], "FLAG")
        self.assertGreaterEqual(v["days_in_state"], 5)

    def test_jump_flags_immediately(self):
        # one day, but the 7-day mean offset is far past band+jump vs both anchors
        recent = [(0, 6.0)]
        offs = {"KWDR": series(self.ref, 25, recent), "KAHN": series(self.ref, 25, recent)}
        v = health.assess_variable(vcfg("temp"), offs, self.ref)
        self.assertEqual(v["state"], "FLAG")

    def test_single_anchor_divergence_does_not_flag(self):
        # KAHN drifts 3 days; KWDR stays in band -> only 1 anchor diverges -> OK (weather)
        offs = {"KWDR": series(self.ref, 25, [(0, 0.0), (1, 0.0), (2, 0.0)]),
                "KAHN": series(self.ref, 25, [(0, 2.0), (1, 2.0), (2, 2.0)])}
        v = health.assess_variable(vcfg("temp"), offs, self.ref)
        self.assertEqual(v["state"], "OK")
        self.assertEqual(v["days_in_state"], 0)

    def test_opposite_directions_do_not_flag(self):
        # both anchors out of band but OPPOSITE sides -> not same-direction -> OK
        offs = {"KWDR": series(self.ref, 25, [(0, 2.0), (1, 2.0), (2, 2.0)]),
                "KAHN": series(self.ref, 25, [(0, -2.0), (1, -2.0), (2, -2.0)])}
        v = health.assess_variable(vcfg("temp"), offs, self.ref)
        self.assertEqual(v["state"], "OK")

    def test_in_band_is_ok(self):
        recent = [(0, 0.1), (1, -0.1), (2, 0.0)]
        offs = {"KWDR": series(self.ref, 25, recent), "KAHN": series(self.ref, 25, recent)}
        v = health.assess_variable(vcfg("temp"), offs, self.ref)
        self.assertEqual(v["state"], "OK")

    def test_constant_offset_absorbed_by_baseline(self):
        # a large but STABLE offset (e.g. wind siting) must read OK, not flag
        base_const = [-4.0]
        offs = {}
        for sid in ("KAHN", "WATUGA"):
            s = {}
            for i in range(25):
                s[(self.ref - dt.timedelta(days=8 + i)).isoformat()] = -4.0
            for j in range(3):
                s[(self.ref - dt.timedelta(days=j)).isoformat()] = -4.0
            offs[sid] = s
        v = health.assess_variable(vcfg("wind"), offs, self.ref)
        self.assertEqual(v["state"], "OK")


class TestWatuga(unittest.TestCase):
    GOOD = ("<table><tr><td>Maximum Temperature (&degF)</td><td>86.3</td><td>82.8</td></tr>"
            "<tr><td>Minimum Temperature (&degF)</td><td>70.2</td><td>69.7</td></tr>"
            "<tr><td>Relative Humidity (%)</td><td>85.2</td></tr>"
            "<tr><td>Atmospheric Pressure (in)</td><td>30.14</td></tr>"
            "<tr><td>Wind Speed (mph)</td><td>2.3</td></tr></table>")

    def test_parses_daily_summary(self):
        out = health.watuga_daily({"html": self.GOOD}, "2026-06-08")
        self.assertIn("2026-06-08", out)
        agg = out["2026-06-08"]
        self.assertAlmostEqual(agg["temp"], (86.3 + 70.2) / 2.0, places=2)
        self.assertAlmostEqual(agg["rh"], 85.2, places=2)
        self.assertAlmostEqual(agg["wind"], 2.3, places=2)
        self.assertAlmostEqual(agg["pressure"], 30.14 * 33.8639, places=1)

    def test_parse_failure_returns_none(self):
        # garbage HTML must not raise and must yield None -> caller runs on 2 anchors
        self.assertIsNone(health.watuga_daily({"html": "<html>totally broken"}, "2026-06-08"))
        self.assertIsNone(health.watuga_daily({"html": ""}, "2026-06-08"))
        self.assertIsNone(health.watuga_daily(None, "2026-06-08"))


class TestMetar(unittest.TestCase):
    def test_buckets_and_aggregates(self):
        # 4 obs same local day for KAHN -> one daily aggregate; <4 obs dropped
        base = 1781000000
        rows = [{"icaoId": "KAHN", "obsTime": base + i * 600, "temp": 20 + i,
                 "dewp": 10, "wspd": 5, "altim": 1015} for i in range(4)]
        out = health.metar_daily({"data": rows})
        self.assertIn("KAHN", out)
        day = next(iter(out["KAHN"]))
        self.assertIn("temp", out["KAHN"][day])
        self.assertIn("wind", out["KAHN"][day])

    def test_thin_day_dropped(self):
        rows = [{"icaoId": "KAHN", "obsTime": 1781000000, "temp": 20, "dewp": 10, "altim": 1015}]
        out = health.metar_daily({"data": rows})
        self.assertFalse(out.get("KAHN"))   # <4 obs -> no aggregate


class TestHighTruthCheck(unittest.TestCase):
    """v2 daily-HIGH truth check: calm-sunny vs windy split vs the airport anchors.
    Annotate-only — it must never touch the offset/flag machinery."""

    def _tempest(self, dates, high, wind, solar):
        return {dt_: {"temp": high - 8, "high": high, "wind": wind, "solar_max": solar}
                for dt_ in dates}

    def _days(self, n, start="2026-07-01"):
        return [(dt.date.fromisoformat(start) + dt.timedelta(days=i)).isoformat()
                for i in range(n)]

    def test_regime_classification(self):
        # cuts come from the station's own wind terciles (fence-post siting -> low absolute mph)
        self.assertEqual(health._high_regime({"wind": 1.4, "solar_max": 900}, 1.5, 2.5), "calm_sunny")
        self.assertEqual(health._high_regime({"wind": 3.0, "solar_max": 900}, 1.5, 2.5), "windy")
        self.assertIsNone(health._high_regime({"wind": 2.0, "solar_max": 900}, 1.5, 2.5))  # between
        self.assertIsNone(health._high_regime({"wind": 1.0, "solar_max": 300}, 1.5, 2.5))  # calm, dim
        self.assertIsNone(health._high_regime({"wind": None}, 1.5, 2.5))
        self.assertIsNone(health._high_regime({"wind": 1.0}, 1.5, 2.5))                    # no solar

    def test_split_detected_when_calm_sunny_reads_hot(self):
        cs_days, wd_days = self._days(6), self._days(6, "2026-07-10")
        tempest = {}
        tempest.update(self._tempest(cs_days, 95.0, 1.5, 900))   # calm-sunny: reads +3 vs anchor
        tempest.update(self._tempest(wd_days, 92.0, 3.5, 900))   # windy: reads even
        anchors = {"KAHN": {d_: {"temp_max": 92.0} for d_ in cs_days + wd_days}}
        hc = health.high_truth_check(tempest, anchors)
        a = hc["anchors"]["KAHN"]
        self.assertAlmostEqual(a["calm_sunny"], 3.0)
        self.assertAlmostEqual(a["windy"], 0.0)
        self.assertAlmostEqual(hc["split_delta"], 3.0)
        self.assertTrue(hc["suspect"])
        self.assertIn("radiation-shield", hc["note"])

    def test_no_split_reads_clean(self):
        cs_days, wd_days = self._days(6), self._days(6, "2026-07-10")
        tempest = {}
        tempest.update(self._tempest(cs_days, 92.5, 1.5, 900))
        tempest.update(self._tempest(wd_days, 92.5, 3.5, 900))
        anchors = {"KWDR": {d_: {"temp_max": 92.0} for d_ in cs_days + wd_days}}
        hc = health.high_truth_check(tempest, anchors)
        self.assertFalse(hc["suspect"])
        self.assertAlmostEqual(hc["split_delta"], 0.0)

    def test_thin_regimes_report_building(self):
        # wind spread exists (terciles separate) but only 3 calm-sunny days -> no split yet
        days = self._days(3) + self._days(3, "2026-07-10")
        tempest = {}
        tempest.update(self._tempest(self._days(3), 95.0, 1.5, 900))
        tempest.update(self._tempest(self._days(3, "2026-07-10"), 93.0, 3.5, 900))
        anchors = {"KAHN": {d_: {"temp_max": 92.0} for d_ in days}}
        hc = health.high_truth_check(tempest, anchors)
        self.assertIsNone(hc["split_delta"])
        self.assertIsNone(hc["suspect"])
        self.assertIsNone(hc["anchors"]["KAHN"]["calm_sunny"])
        self.assertIn("Building", hc["note"])

    def test_degenerate_wind_spread_reports_honestly(self):
        days = self._days(8)
        tempest = self._tempest(days, 95.0, 2.0, 900)   # every day identical wind
        anchors = {"KAHN": {d_: {"temp_max": 92.0} for d_ in days}}
        hc = health.high_truth_check(tempest, anchors)
        self.assertIsNone(hc["split_delta"])
        self.assertIn("too narrow", hc["note"])

    def test_no_paired_days_returns_none(self):
        self.assertIsNone(health.high_truth_check({}, {}))
        # anchor days without temp_max (e.g. the backfill) contribute nothing
        tempest = self._tempest(self._days(3), 95.0, 2.0, 900)
        anchors = {"KAHN": {d_: {"temp": 90.0} for d_ in self._days(3)}}
        self.assertIsNone(health.high_truth_check(tempest, anchors))

    def test_watuga_never_consulted(self):
        days = self._days(6)
        tempest = self._tempest(days, 95.0, 2.0, 900)
        anchors = {"WATUGA": {d_: {"temp_max": 90.0} for d_ in days}}
        self.assertIsNone(health.high_truth_check(tempest, anchors))   # airports only

    def test_tempest_daily_carries_high_and_solar(self):
        def row(tc, wind_ms, solar):
            r = [0] * 22
            r[health.OBS_TEMP] = tc
            r[health.OBS_WIND] = wind_ms
            r[health.OBS_RH] = 50
            r[health.OBS_PRES] = 985.0
            r[health.OBS_SOLAR] = solar
            return r
        dev = {"for_date": "2026-07-01", "data": {"obs": [row(20.0, 1.0, 100), row(35.0, 2.0, 880)]}}
        date, agg = health.tempest_daily(dev)
        self.assertEqual(date, "2026-07-01")
        self.assertAlmostEqual(agg["high"], 95.0)        # max temp, 35C -> 95F
        self.assertAlmostEqual(agg["solar_max"], 880)
        # the offset machinery's fixed var list must be unaffected by the extra keys
        offs, rows = health.build_offsets({date: agg}, {"KAHN": {date: {"temp": 90.0}}})
        self.assertNotIn("high", offs)
        self.assertNotIn("solar_max", offs)

    def test_metar_daily_max_requires_midday_coverage(self):
        from zoneinfo import ZoneInfo
        midnight = int(dt.datetime(2026, 6, 10, 0, 51, tzinfo=ZoneInfo("America/New_York")).timestamp())
        full = [{"icaoId": "KAHN", "obsTime": midnight + h * 3600, "temp": 20 + (h if h <= 14 else 28 - h),
                 "dewp": 10, "wspd": 5, "altim": 1015} for h in range(24)]
        out = health.metar_daily({"data": full})
        agg = out["KAHN"]["2026-06-10"]
        self.assertAlmostEqual(agg["temp_max"], health.c_to_f(34), places=1)   # peak at 14:51
        # an evening-only partial day (a missed capture's leftover slice) must NOT report a max
        evening = [r for r in full if r["obsTime"] >= midnight + 19 * 3600]
        out = health.metar_daily({"data": evening})
        self.assertNotIn("temp_max", out["KAHN"].get("2026-06-10", {}))


class TestPhysics(unittest.TestCase):
    def test_slp_reduction_adds_about_30mb(self):
        slp = health.station_to_slp(984.6, 22.9)
        self.assertTrue(1010 < slp < 1018, slp)

    def test_rh_from_dewpoint(self):
        self.assertAlmostEqual(health.rh_from_t_td(20, 20), 100.0, places=1)   # T==Td -> 100%
        self.assertLess(health.rh_from_t_td(30, 10), 40.0)

    def test_percentile_and_median(self):
        xs = list(range(1, 101))
        self.assertAlmostEqual(health.percentile(xs, 5), 5.95, places=1)
        self.assertAlmostEqual(health.median([1, 2, 3, 4]), 2.5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
