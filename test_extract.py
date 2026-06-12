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
