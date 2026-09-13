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


class TestDawgSource(unittest.TestCase):
    """The house AI row. Contract in docs/dawg-source.md; parsed only when the file is BOTH
    a real AI call (kind "dawg") and issued on the capture's own date."""

    def _file(self, **over):
        j = {"meta": {}, "data": {
            "v": 1, "source": "Dawg", "kind": "dawg", "model": "claude-fable-5",
            "issued_at": f"{CAP}T05:47:12-04:00", "issued_date": CAP,
            "days": [
                {"date": CAP, "lead": 0, "pop": 40, "high": 91, "low": 71},                # lead 0
                {"date": "2026-06-05", "lead": 1, "pop": 75, "high": 85, "low": 68},
                {"date": "2026-06-06", "lead": 2, "pop": 20, "high": 88, "low": 70},
                {"date": "2026-06-07", "lead": 3, "pop": 0, "high": 90, "low": 72},
                {"date": "2026-06-11", "lead": 7, "pop": 30, "high": 92, "low": 71},       # lead 7
            ]}}
        j["data"].update(over)
        return j

    def test_normal_parse_leads_1_to_3_only(self):
        recs = extract.parse_dawg(self._file(), CAP)
        got = {(r["date"], r["var"]): (r["value"], r["lead"]) for r in recs}
        self.assertEqual(got[("2026-06-05", "high")], (85.0, 1))
        self.assertEqual(got[("2026-06-05", "low")], (68.0, 1))
        self.assertEqual(got[("2026-06-07", "high")], (90.0, 3))
        self.assertTrue(all(r["source"] == "Dawg" for r in recs))
        self.assertEqual(sorted({r["lead"] for r in recs}), [1, 2, 3])   # 0 and 7 dropped
        self.assertNotIn((CAP, "high"), got)

    def test_pop_passes_through_unscaled_0_100(self):
        recs = extract.parse_dawg(self._file(), CAP)
        pops = {r["date"]: r["value"] for r in recs if r["var"] == "pop"}
        self.assertEqual(pops["2026-06-05"], 75.0)     # already 0-100: no /100, no *100
        self.assertEqual(pops["2026-06-07"], 0.0)      # 0 is a real PoP, not "missing"

    def test_stale_issued_date_yields_no_records(self):
        # A gist raw URL serves yesterday's file forever; scoring it at today's leads would
        # be the one way this row could cheat. capture.py refuses to write it; so does this.
        self.assertEqual(extract.parse_dawg(self._file(issued_date="2026-06-03"), CAP), [])
        self.assertEqual(extract.parse_dawg(self._file(issued_date=None), CAP), [])

    def test_kind_blend_fallback_is_not_scored_as_dawg(self):
        # kind "blend" = the Mac's LLM call failed and it shipped its deterministic fallback.
        # Crediting the AI for a forecast it never made would flatter the row.
        self.assertEqual(extract.parse_dawg(self._file(kind="blend"), CAP), [])
        self.assertEqual(extract.parse_dawg(self._file(kind=None), CAP), [])

    def test_null_and_malformed_fields_tolerated(self):
        j = self._file(days=[
            {"date": "2026-06-05", "lead": 1, "pop": None, "high": 85, "low": None},
            {"date": None, "lead": 2, "pop": 50, "high": 80, "low": 60},        # no date
            {"date": "2026-06-06", "lead": 2},                                  # no values
            "not a dict",
            {"date": "2026-06-07", "lead": 3, "pop": "x", "high": 90, "low": 72},  # bad type
        ])
        recs = extract.parse_dawg(j, CAP)   # must not raise
        got = {(r["date"], r["var"]) for r in recs}
        self.assertEqual(got, {("2026-06-05", "high"), ("2026-06-07", "high"),
                               ("2026-06-07", "low")})

    def test_missing_file_and_junk(self):
        self.assertEqual(extract.parse_dawg(None, CAP), [])
        self.assertEqual(extract.parse_dawg({}, CAP), [])
        self.assertEqual(extract.parse_dawg({"data": None}, CAP), [])


class TestBlendBaseline(unittest.TestCase):
    """The deterministic baseline: high/low = NWS value, else NBM, else Tempest; pop =
    mean(ECMWF pop, Tempest pop) when both exist, else whichever exists, else NWS."""

    def _recs(self, spec, date="2026-06-05", lead=1):
        return [{"date": date, "lead": lead, "source": s, "var": v, "value": float(x)}
                for s, vars_ in spec.items() for v, x in vars_.items()]

    def _blend(self, spec, **kw):
        out = extract.blend_records(self._recs(spec, **kw))
        self.assertTrue(all(r["source"] == "Blend" for r in out))
        return {r["var"]: r["value"] for r in out}

    def test_temps_prefer_nws_then_nbm_then_tempest(self):
        b = self._blend({"NWS": {"high": 85, "low": 65}, "NBM": {"high": 87, "low": 66},
                         "Tempest": {"high": 89, "low": 67}})
        self.assertEqual((b["high"], b["low"]), (85.0, 65.0))
        b = self._blend({"NBM": {"high": 87, "low": 66}, "Tempest": {"high": 89, "low": 67}})
        self.assertEqual((b["high"], b["low"]), (87.0, 66.0))
        b = self._blend({"Tempest": {"high": 89, "low": 67}})
        self.assertEqual((b["high"], b["low"]), (89.0, 67.0))

    def test_temps_fall_back_per_variable(self):
        # NWS gave a high but no low -> the low falls through to NBM on its own.
        b = self._blend({"NWS": {"high": 85}, "NBM": {"high": 87, "low": 66}})
        self.assertEqual((b["high"], b["low"]), (85.0, 66.0))

    def test_pop_is_mean_of_ecmwf_and_tempest(self):
        b = self._blend({"NWS": {"high": 85, "low": 65, "pop": 90},
                         "ECMWF": {"pop": 60}, "Tempest": {"pop": 30}})
        self.assertEqual(b["pop"], 45.0)     # mean(60, 30) — NWS's 90 is the last resort only

    def test_pop_falls_back_to_whichever_exists_then_nws(self):
        self.assertEqual(self._blend({"NWS": {"high": 85, "pop": 90},
                                      "ECMWF": {"pop": 60}})["pop"], 60.0)
        self.assertEqual(self._blend({"NWS": {"high": 85, "pop": 90},
                                      "Tempest": {"pop": 30}})["pop"], 30.0)
        self.assertEqual(self._blend({"NWS": {"high": 85, "pop": 90}})["pop"], 90.0)
        self.assertNotIn("pop", self._blend({"NBM": {"high": 87}}))   # nothing to blend

    def test_backfills_every_date_and_lead_and_is_idempotent(self):
        recs = (self._recs({"NWS": {"high": 85, "low": 65}}, date="2026-06-05", lead=1)
                + self._recs({"NWS": {"high": 80, "low": 60}}, date="2026-06-06", lead=2)
                + self._recs({"NBM": {"high": 70, "low": 50}}, date="2026-06-07", lead=3))
        out = extract.blend_records(recs)
        self.assertEqual(sorted({(r["date"], r["lead"]) for r in out}),
                         [("2026-06-05", 1), ("2026-06-06", 2), ("2026-06-07", 3)])
        # re-running over records that ALREADY contain Blend rows must not blend the blend
        self.assertEqual(extract.blend_records(recs + out), out)

    def test_dawg_never_feeds_the_blend(self):
        # The baseline must stay a PUBLIC/Tempest construction — otherwise "Blend beat Dawg"
        # would be partly Dawg grading itself.
        b = self._blend({"Dawg": {"high": 99, "low": 40, "pop": 100},
                         "NWS": {"high": 85, "low": 65}, "ECMWF": {"pop": 60},
                         "Tempest": {"pop": 30}})
        self.assertEqual((b["high"], b["low"], b["pop"]), (85.0, 65.0, 45.0))

    def test_empty_input(self):
        self.assertEqual(extract.blend_records([]), [])


class TestPublicSourceGuard(unittest.TestCase):
    """The verdict sentence and verdict_history must keep meaning Tempest vs a PUBLIC
    forecast, even when a house row (Dawg/Blend) owns the lowest MAE in the table."""

    L1 = [
        {"source": "Dawg",    "mae": 1.40, "pct_within_3f": 90, "csi": 0.70, "brier": 0.12, "house": True},
        {"source": "Blend",   "mae": 1.60, "pct_within_3f": 88, "csi": 0.68, "brier": 0.13, "house": True},
        {"source": "NBM",     "mae": 1.85, "pct_within_3f": 79, "csi": 0.74, "brier": 0.083},
        {"source": "Tempest", "mae": 1.92, "pct_within_3f": 81, "csi": 0.71, "brier": 0.091},
        {"source": "NWS",     "mae": 2.10, "pct_within_3f": 74, "csi": 0.70, "brier": 0.095},
    ]

    def test_best_public_skips_house_rows(self):
        v = extract.temp_verdict([], {}, self.L1, 5)
        self.assertEqual(v["best_public"], "NBM")          # NOT Dawg, though Dawg has lower MAE
        self.assertNotIn("Dawg", v["headline"])
        for house in extract.HOUSE_SOURCES:
            self.assertIn(house, [r["source"] for r in self.L1])   # they ARE in the table…
            self.assertNotEqual(v["best_public"], house)           # …just never the rival

    def test_public_and_house_lists_are_disjoint_and_complete(self):
        self.assertEqual(set(extract.PUBLIC_SOURCES) & set(extract.HOUSE_SOURCES), set())
        self.assertNotIn("Tempest", extract.PUBLIC_SOURCES)   # the subject is not its own rival
        self.assertEqual(set(extract.SOURCES),
                         {"Tempest"} | set(extract.PUBLIC_SOURCES) | set(extract.HOUSE_SOURCES))

    def test_winners_leader_may_be_a_house_row(self):
        # Taylor's call: the RIVAL must be public, but the field LEADER can be anyone.
        w = extract.winners_panel(self.L1, "NBM")
        self.assertEqual(w["temp"]["leader"], "Dawg")
        self.assertEqual(w["temp"]["rival"], "NBM")

    def test_house_only_field_gives_no_verdict(self):
        l1 = [r for r in self.L1 if r["source"] in ("Tempest",) + tuple(extract.HOUSE_SOURCES)]
        v = extract.temp_verdict([], {}, l1, 99)
        self.assertIsNone(v["best_public"])
        self.assertEqual(v["status"], "TOO EARLY")


class TestStandingsExtras(unittest.TestCase):
    """Additive standings keys (n_days / house / sources) and the pooled-row lead guard."""

    def _fixture(self):
        import datetime as dt
        records, actuals = [], {}
        dates = [(dt.date.fromisoformat("2026-06-05") + dt.timedelta(days=i)).isoformat()
                 for i in range(12)]
        _temp_days("Tempest", dates, 80, 60, 82, 61, records, actuals)
        _temp_days("NWS", dates, 81, 60, 82, 61, records, actuals)
        # Dawg joined late — only the last 4 dates, so its row must read as thin.
        _temp_days("Dawg", dates[-4:], 82, 61, 82, 61, records, actuals)
        # …and only at lead 1, while the two established sources also forecast at leads 2-3.
        records += [dict(r, lead=L) for r in list(records)
                    if r["source"] in ("Tempest", "NWS") for L in (2, 3)]
        return records, actuals, {}

    def test_per_row_n_days_and_house_flag(self):
        records, actuals, wet = self._fixture()
        rows = {r["source"]: r for r in extract.standings_for(records, actuals, wet, 1)}
        self.assertEqual(rows["Tempest"]["n_days"], 12)
        self.assertEqual(rows["NWS"]["n_days"], 12)
        self.assertEqual(rows["Dawg"]["n_days"], 4)       # < EARLY_N_DAYS -> greyed on the page
        self.assertTrue(rows["Dawg"]["house"])
        self.assertNotIn("house", rows["NWS"])
        self.assertNotIn("house", rows["Tempest"])

    def test_pooled_row_excludes_sources_missing_a_lead(self):
        records, actuals, wet = self._fixture()
        # Dawg only ever appears at lead 1 in this fixture -> no pooled row for it.
        pooled = {r["source"] for r in
                  extract.standings_for(records, actuals, wet, extract.LEADS, require_all_leads=True)}
        self.assertNotIn("Dawg", pooled)
        self.assertIn("Tempest", pooled)
        self.assertEqual(extract.POOLED_KEY, "blend")     # the KEY, not the "Blend" SOURCE

    def test_sources_block_labels_public_and_house(self):
        records, actuals, _ = self._fixture()
        s = extract.sources_block(records, actuals)
        self.assertEqual(s["NWS"]["public"], True)
        self.assertEqual(s["NWS"]["house"], False)
        self.assertEqual(s["Dawg"]["public"], False)
        self.assertEqual(s["Dawg"]["house"], True)
        self.assertEqual(s["Tempest"]["public"], False)   # the subject is not a rival
        self.assertEqual(s["Dawg"]["first_date"], "2026-06-13")
        self.assertEqual(s["Dawg"]["n_days"], 4)
        self.assertNotIn("GFS", s)                        # no records -> not listed
        self.assertEqual(list(s), [x for x in extract.SOURCES if x in s])   # display order
        json.dumps(s, allow_nan=False)

    def test_build_emits_standings_and_sources_cleanly(self):
        records, actuals, wet = self._fixture()
        standings, verdict, _, _, _, _ = extract.build(records, actuals, wet)
        self.assertIn(extract.POOLED_KEY, standings)
        self.assertTrue(all("n_days" in r for r in standings["lead1"]))
        self.assertEqual(verdict["best_public"], "NWS")
        json.dumps(standings, allow_nan=False)


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
