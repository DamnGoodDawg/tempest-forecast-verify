"""
Watchdog state-machine tests (stdlib unittest). Run from the repo root:
    python -m unittest test_watchdog -v
Covers: one email per outage, retry when creds were missing, recovery only after a real
down-notify, no recovery email for an un-notified blip, and Z-suffix ISO parsing.
"""
import unittest
import datetime as dt

import watchdog

NOW = "2026-06-13T15:00:00+00:00"


class DecideTests(unittest.TestCase):
    def test_ok_steady_no_event_keeps_since(self):
        s, e = watchdog.decide({"status": "ok", "since": "2026-06-13T10:00:00+00:00",
                                "notified": False}, "ok", NOW)
        self.assertIsNone(e)
        self.assertEqual(s["since"], "2026-06-13T10:00:00+00:00")

    def test_ok_to_down_emits_down(self):
        s, e = watchdog.decide({"status": "ok", "since": "x", "notified": False}, "down", NOW)
        self.assertEqual(e, "down")
        self.assertEqual(s["since"], NOW)          # since resets on the flip
        self.assertFalse(s["notified"])

    def test_down_retries_when_not_yet_notified(self):
        # creds were missing last run -> notified False -> we try again
        _, e = watchdog.decide({"status": "down", "since": "x", "notified": False}, "down", NOW)
        self.assertEqual(e, "down")

    def test_down_no_repeat_once_notified(self):
        s, e = watchdog.decide({"status": "down", "since": "x", "notified": True}, "down", NOW)
        self.assertIsNone(e)
        self.assertTrue(s["notified"])

    def test_recovery_only_after_real_down_notify(self):
        s, e = watchdog.decide({"status": "down", "since": "x", "notified": True}, "ok", NOW)
        self.assertEqual(e, "recovered")
        self.assertEqual(s["status"], "ok")

    def test_unnotified_blip_to_ok_is_silent(self):
        _, e = watchdog.decide({"status": "down", "since": "x", "notified": False}, "ok", NOW)
        self.assertIsNone(e)

    def test_parse_iso_z(self):
        d = watchdog._parse_iso("2026-06-13T14:13:32Z")
        self.assertEqual(d.tzinfo, dt.timezone.utc)


if __name__ == "__main__":
    unittest.main()
