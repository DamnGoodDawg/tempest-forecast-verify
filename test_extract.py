#!/usr/bin/env python3
"""
test_extract.py - smoke tests for the parsing/scoring layer (stdlib unittest).

The Tempest/NWS/Open-Meteo APIs are documented to silently drop response fields, so the
parsers must tolerate missing data without crashing. These tests lock that in, plus the
three regressions the 2026-06 audit fixed: NWS overnight-low attribution (A1), the
NaN-in-scores.json poisoning (A3), and the Diebold-Mariano per-date collapse + HLN
correction (A6). Run: `python -m unittest test_extract -v` (or just `python test_extract.py`).
"""
import json, unittest
import extract, verify

CAP = "2026-06-04"   # capture date used throughout (leads are relative to this)


class TestNWSAttribution(unittest.TestCase):
    def _parse(self, periods):
        j = {"data": {"forecast": {"properties": {"periods": periods}}}}
        return extract.parse_nws(j, CAP)

    def test_overnight_low_attributed_to_next_morning(self):
        # A1: a night period starting the evening of D forecasts the low that occurs the
        # morning of D+1. It must be keyed to D+1, not D.
        periods = [
            # evening of the capture day -> low belongs to 06-05 (lead 1)
            {"startTime": "2026-06-04T18:00:00-04:00", "isDaytime": False, "temperature": 58},
            # daytime 06-05 -> high for 06-05 (lead 1), with a PoP
            {"startTime": "2026-06-05T06:00:00-04:00", "isDaytime": True, "temperature": 85,
             "probabilityOfPrecipitation": {"value": 40}},
            # evening of 06-05 -> low belongs to 06-06 (lead 2); PoP stays on 06-05
            {"startTime": "2026-06-05T18:00:00-04:00", "isDaytime": False, "temperature": 60,
             "probabilityOfPrecipitation": {"value": 70}},
        ]
        recs = self._parse(periods)
        got = {(r["date"], r["var"]): (r["value"], r["lead"]) for r in recs}
        self.assertEqual(got[("2026-06-05", "high")], (85.0, 1))
        self.assertEqual(got[("2026-06-05", "low")], (58.0, 1))   # NOT 60, NOT keyed to 06-05
        self.assertEqual(got[("2026-06-06", "low")], (60.0, 2))   # the 06-05 night low -> 06-06
        # PoP convention unchanged: max over periods touching 06-05, keyed to 06-05/lead1
        self.assertEqual(got[("2026-06-05", "pop")], (70.0, 1))

    def test_missing_fields_tolerated(self):
        periods = [
            {"isDaytime": True, "temperature": 80},                 # no startTime
            {"startTime": "2026-06-05T06:00:00-04:00", "isDaytime": True},  # no temperature
            {"startTime": "garbage", "isDaytime": False, "temperature": 50},
            {"startTime": "2026-06-05T06:00:00-04:00", "isDaytime": True, "temperature": 84},
        ]
        recs = self._parse(periods)   # must not raise
        self.assertIn(("2026-06-05", "high"), {(r["date"], r["var"]) for r in recs})

    def test_none_input(self):
        self.assertEqual(extract.parse_nws(None, CAP), [])
        self.assertEqual(extract.parse_tempest(None, CAP), [])
        self.assertEqual(extract.parse_openmeteo(None, CAP), [])
        self.assertEqual(extract.parse_actuals(None), {})


class TestUnitConversion(unittest.TestCase):
    def test_c_to_f(self):
        self.assertAlmostEqual(extract.c_to_f(0), 32.0)
        self.assertAlmostEqual(extract.c_to_f(100), 212.0)
        self.assertAlmostEqual(extract.c_to_f(20), 68.0)

    def test_parse_actuals_metric_to_f(self):
        # obs_st rows are METRIC regardless of unit params: air_temp C at index 7,
        # daily rain mm at indices 18/20. Build minimal rows.
        def row(tc, rain_mm):
            r = [0] * 21
            r[extract.OBS_AIRTEMP_C] = tc
            r[extract.OBS_RAIN_DAY_MM] = rain_mm
            r[extract.OBS_RAIN_DAY_FINAL_MM] = rain_mm
            return r
        dev = {"for_date": "2026-06-05", "data": {"obs": [row(20.0, 0.0), row(30.0, 25.4)]}}
        a = extract.parse_actuals(dev)
        self.assertAlmostEqual(a[("2026-06-05", "high")], 86.0)   # 30C -> 86F
        self.assertAlmostEqual(a[("2026-06-05", "low")], 68.0)    # 20C -> 68F
        self.assertAlmostEqual(a[("2026-06-05", "precip_amt")], 1.0)  # 25.4mm -> 1.00 in

    def test_parse_actuals_skips_nonnumeric(self):
        dev = {"for_date": "2026-06-05",
               "data": {"obs": [[None] * 21, ["x"] * 21]}}
        self.assertEqual(extract.parse_actuals(dev), {})   # no numeric temps -> empty, no crash


class TestNaNGuard(unittest.TestCase):
    def test_finite_collapses_nan_and_inf(self):
        self.assertIsNone(extract._finite(float("nan"), 2))
        self.assertIsNone(extract._finite(float("inf"), 2))
        self.assertIsNone(extract._finite(None, 2))
        self.assertEqual(extract._finite(0.512, 2), 0.51)

    def test_source_row_csi_never_nan(self):
        # All-dry window: contingency() returns csi=NaN. source_row must emit None so the
        # value survives json.dump(allow_nan=False) instead of poisoning scores.json.
        records = [
            {"date": "2026-06-05", "lead": 1, "source": "NWS", "var": "high", "value": 85},
            {"date": "2026-06-05", "lead": 1, "source": "NWS", "var": "low", "value": 60},
            {"date": "2026-06-05", "lead": 1, "source": "NWS", "var": "pop", "value": 10},
        ]
        actuals = {("2026-06-05", "high"): 84, ("2026-06-05", "low"): 61,
                   ("2026-06-05", "precip_amt"): 0.0}
        wet = {"2026-06-05": False}
        row, _ = extract.source_row(records, actuals, wet, "NWS", 1)
        self.assertIsNone(row["csi"])
        json.dumps(row, allow_nan=False)   # must not raise


def _temp_days(source, dates, high, low, actual_high, actual_low, records, actuals):
    """Helper: append lead-1 high/low records + actuals for each date."""
    for dte in dates:
        records += [
            {"date": dte, "lead": 1, "source": source, "var": "high", "value": high},
            {"date": dte, "lead": 1, "source": source, "var": "low", "value": low},
        ]
        actuals[(dte, "high")] = actual_high
        actuals[(dte, "low")] = actual_low


class TestWindows(unittest.TestCase):
    """v2 windowed scoring: rolling-90 carries the verdict; since-epoch + rolling-28 (trend
    only) + all-time (context); the deliberate rolling-90 == all-time early state is labeled."""

    def _fixture(self, n=35, start="2026-06-05"):
        import datetime as dt
        records, actuals = [], {}
        dates = [(dt.date.fromisoformat(start) + dt.timedelta(days=i)).isoformat()
                 for i in range(n)]
        _temp_days("Tempest", dates, 80, 60, 82, 61, records, actuals)   # per-date loss 1.5
        _temp_days("NWS", dates, 81, 60, 82, 61, records, actuals)       # per-date loss 1.0
        return records, actuals, {}

    def test_filter_by_dates(self):
        records, actuals, wet = self._fixture(n=10)
        recs, acts, _ = extract.filter_by_dates(records, actuals, wet, "2026-06-08", "2026-06-10")
        self.assertEqual(sorted({r["date"] for r in recs}),
                         ["2026-06-08", "2026-06-09", "2026-06-10"])
        self.assertTrue(all("2026-06-08" <= k[0] <= "2026-06-10" for k in acts))

    def test_rolling90_equals_all_time_until_divergence(self):
        records, actuals, wet = self._fixture(n=35)
        w = extract.build_windows(records, actuals, wet)
        self.assertTrue(w["rolling90"]["equals_all_time"])
        self.assertEqual(w["rolling90"]["n_days"], w["all_time"]["n_days"])
        # diverges 90 days after the FIRST scored day
        self.assertEqual(w["rolling90"]["diverges_after"], "2026-09-03")

    def test_rolling90_diverges_past_90_days(self):
        records, actuals, wet = self._fixture(n=100)
        w = extract.build_windows(records, actuals, wet)
        self.assertFalse(w["rolling90"]["equals_all_time"])
        self.assertEqual(w["rolling90"]["n_days"], 90)
        self.assertEqual(w["all_time"]["n_days"], 100)

    def test_rolling28_is_trend_only_no_verdict(self):
        records, actuals, wet = self._fixture(n=35)
        w = extract.build_windows(records, actuals, wet)
        self.assertTrue(w["rolling28"]["trend_only"])
        self.assertNotIn("verdict", w["rolling28"])   # explicitly no verdict/p by design
        self.assertNotIn("winners", w["rolling28"])
        self.assertEqual(w["rolling28"]["n_days"], 28)

    def test_since_epoch_window_and_too_early(self):
        records, actuals, wet = self._fixture(n=35)   # ends 2026-07-09, before the epoch
        w = extract.build_windows(records, actuals, wet)
        self.assertEqual(w["since_epoch"]["epoch"], extract.EPOCH)
        self.assertEqual(w["since_epoch"]["n_days"], 0)
        self.assertEqual(w["since_epoch"]["verdict"]["status"], "TOO EARLY")

    def test_headline_names_the_window(self):
        records, actuals, wet = self._fixture(n=35)
        w = extract.build_windows(records, actuals, wet)
        self.assertIn("over the last 90 days", w["rolling90"]["verdict"]["headline"])
        _, verdict, _, _, _, _ = extract.build(records, actuals, wet)
        # the headline verdict IS the rolling-90 verdict
        self.assertEqual(verdict, w["rolling90"]["verdict"])


class TestWinnersPanel(unittest.TestCase):
    L1 = [
        {"source": "NWS",     "mae": 2.02, "pct_within_3f": 79, "csi": 0.41, "brier": 0.22},
        {"source": "Tempest", "mae": 2.35, "pct_within_3f": 72, "csi": 0.60, "brier": 0.186},
        {"source": "ECMWF",   "mae": 2.64, "pct_within_3f": 65, "csi": 0.69, "brier": 0.157},
    ]

    def test_per_variable_winners_and_rival(self):
        w = extract.winners_panel(self.L1, "NWS")
        self.assertEqual(w["temp"]["leader"], "NWS")
        self.assertFalse(w["temp"]["tempest_wins_rival"])
        # CSI: higher is better — ECMWF leads the field, Tempest beats the headline rival
        self.assertEqual(w["precip_occurrence"]["leader"], "ECMWF")
        self.assertTrue(w["precip_occurrence"]["tempest_wins_rival"])
        self.assertTrue(w["pop_calibration"]["tempest_wins_rival"])

    def test_missing_metric_dropped(self):
        l1 = [{"source": "Tempest", "mae": 2.0, "pct_within_3f": 80, "csi": None, "brier": None},
              {"source": "NWS", "mae": 2.1, "pct_within_3f": 78, "csi": None, "brier": None}]
        w = extract.winners_panel(l1, "NWS")
        self.assertIn("temp", w)
        self.assertNotIn("precip_occurrence", w)
        self.assertNotIn("pop_calibration", w)
        json.dumps(w, allow_nan=False)


class TestVerdictHistory(unittest.TestCase):
    def setUp(self):
        import tempfile, os
        self._orig = extract.HISTORY_OUT
        self._tmp = tempfile.mkdtemp()
        extract.HISTORY_OUT = os.path.join(self._tmp, "verdict_history.json")

    def tearDown(self):
        import shutil
        extract.HISTORY_OUT = self._orig
        shutil.rmtree(self._tmp, ignore_errors=True)

    WIN90 = {"n_days": 62,
             "verdict": {"status": "TEMPEST BEHIND", "best_public": "NWS", "dm_p_value": 0.02},
             "standings_lead1": [{"source": "NWS", "mae": 2.02},
                                 {"source": "Tempest", "mae": 2.35}]}

    def test_appends_one_row_per_day_idempotent(self):
        rows = extract.update_verdict_history(self.WIN90)
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertEqual((r["window_n"], r["tempest_mae"], r["best_public"], r["best_mae"],
                          r["dm_p"], r["status"]),
                         (62, 2.35, "NWS", 2.02, 0.02, "TEMPEST BEHIND"))
        # same-day re-run overwrites its own row, never duplicates
        rows = extract.update_verdict_history(self.WIN90)
        self.assertEqual(len(rows), 1)
        persisted = json.load(open(extract.HISTORY_OUT))
        self.assertEqual(len(persisted), 1)

    def test_empty_window_no_row(self):
        self.assertEqual(extract.update_verdict_history({}), [])
        self.assertEqual(extract.update_verdict_history(None), [])


class TestNbmTwin(unittest.TestCase):
    def _recs(self, pairs):
        """pairs: list of (date, tempest_err, nbm_err) with actual high fixed at 90."""
        records, actuals = [], {}
        for dte, te, ne in pairs:
            records.append({"date": dte, "lead": 1, "source": "Tempest", "var": "high",
                            "value": 90 + te})
            records.append({"date": dte, "lead": 1, "source": "NBM", "var": "high",
                            "value": 90 + ne})
            actuals[(dte, "high")] = 90
        return records, actuals

    def test_lockstep_errors_give_r_1(self):
        pairs = [(f"2026-07-{i+1:02d}", e, e) for i, e in enumerate([-3, -1, 0, 2, -2, 1])]
        records, actuals = self._recs(pairs)
        t = extract.nbm_twin(records, actuals)
        self.assertEqual(t["n_days"], 6)
        self.assertAlmostEqual(t["r_all_time"], 1.0)
        self.assertAlmostEqual(t["bias_all_time"]["tempest"], t["bias_all_time"]["nbm"])
        self.assertTrue(t["weekly"])
        json.dumps(t, allow_nan=False)

    def test_bias_series_signed_not_absolute(self):
        pairs = [("2026-07-06", -2, -3), ("2026-07-07", -2, -3), ("2026-07-08", -2, -3)]
        records, actuals = self._recs(pairs)
        t = extract.nbm_twin(records, actuals)
        self.assertAlmostEqual(t["bias_all_time"]["tempest"], -2.0)
        self.assertAlmostEqual(t["bias_all_time"]["nbm"], -3.0)
        # constant errors -> correlation undefined -> clean None, never NaN
        self.assertIsNone(t["r_all_time"])

    def test_too_few_days_returns_none(self):
        records, actuals = self._recs([("2026-07-06", 1, 1)])
        self.assertIsNone(extract.nbm_twin(records, actuals))


class TestDieboldMariano(unittest.TestCase):
    def test_per_date_collapse(self):
        records = []
        for i in range(12):
            dte = f"2026-06-{i+1:02d}"
            records += [
                {"date": dte, "lead": 1, "source": "Tempest", "var": "high", "value": 80},
                {"date": dte, "lead": 1, "source": "Tempest", "var": "low", "value": 60},
            ]
        actuals = {}
        for i in range(12):
            dte = f"2026-06-{i+1:02d}"
            actuals[(dte, "high")] = 82   # |err| = 2
            actuals[(dte, "low")] = 64    # |err| = 4
        loss = verify.per_date_losses(records, actuals, 1)
        # one collapsed loss per date = mean(2, 4) = 3
        self.assertEqual(len(loss["Tempest"]), 12)
        for v in loss["Tempest"].values():
            self.assertAlmostEqual(v, 3.0)

    def test_hln_correction_present_and_valid_p(self):
        a = [3.0] * 12               # Tempest losses
        b = [1.0, 2.0] * 6           # comparator losses
        dm = verify.diebold_mariano(a, b, h=1)
        self.assertIn("dm_stat_hln", dm)
        self.assertIsNotNone(dm["p_value"])
        self.assertTrue(0.0 <= dm["p_value"] <= 1.0)
        json.dumps(dm, allow_nan=False)   # p_value/stats must be finite

    def test_too_few_pairs(self):
        self.assertEqual(verify.diebold_mariano([1, 2, 3], [1, 1, 1], h=1)["n"], 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
