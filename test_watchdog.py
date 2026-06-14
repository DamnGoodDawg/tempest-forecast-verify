"""
Watchdog state-machine tests (stdlib unittest). Run from the repo root:
    python -m unittest test_watchdog -v
Covers: one email per outage, retry when creds were missing, recovery only after a real
down-notify, no recovery email for an un-notified blip, and Z-suffix ISO parsing.
"""
import os
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


class TestEmailModeTests(unittest.TestCase):
    """WATCHDOG_TEST_EMAIL=1 must send a labeled test email and short-circuit BEFORE any gist
    fetch or state read/write, so a manual test can never leave a false down/recovered state."""

    def setUp(self):
        self.sent = []
        self.calls = {"fetch": 0, "load": 0, "save": 0}
        self._orig = {
            "send_email": watchdog.send_email,
            "fetch": watchdog.fetch_published_epoch,
            "load_state": watchdog.load_state,
            "save_state": watchdog.save_state,
        }
        watchdog.send_email = lambda subject, body: self.sent.append((subject, body)) or True
        watchdog.fetch_published_epoch = lambda *a, **k: self.calls.__setitem__(
            "fetch", self.calls["fetch"] + 1) or (_ for _ in ()).throw(
            AssertionError("fetch_published_epoch must not be called in test-email mode"))
        watchdog.load_state = lambda: self.calls.__setitem__(
            "load", self.calls["load"] + 1) or (_ for _ in ()).throw(
            AssertionError("load_state must not be called in test-email mode"))
        watchdog.save_state = lambda s: self.calls.__setitem__(
            "save", self.calls["save"] + 1) or (_ for _ in ()).throw(
            AssertionError("save_state must not be called in test-email mode"))
        self._prev_env = os.environ.get("WATCHDOG_TEST_EMAIL")
        os.environ["WATCHDOG_TEST_EMAIL"] = "1"

    def tearDown(self):
        for name, fn in self._orig.items():
            setattr(watchdog, name, fn)
        if self._prev_env is None:
            os.environ.pop("WATCHDOG_TEST_EMAIL", None)
        else:
            os.environ["WATCHDOG_TEST_EMAIL"] = self._prev_env

    def test_test_mode_sends_and_skips_state(self):
        rc = watchdog.main()
        self.assertEqual(rc, 0)
        self.assertEqual(len(self.sent), 1)
        self.assertIn("[TEST]", self.sent[0][0])
        # No gist fetch and no state read/write happened.
        self.assertEqual(self.calls, {"fetch": 0, "load": 0, "save": 0})


if __name__ == "__main__":
    unittest.main()
