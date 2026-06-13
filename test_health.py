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
