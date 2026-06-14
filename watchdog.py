#!/usr/bin/env python3
"""
watchdog.py - cloud dead-man's switch for the Tempest Mac (stdlib only).

The local alert engine + listener live on Taylor's Mac. If the WHOLE Mac dies (power, network,
crash, sleep), those local alerts go silent AND can't report their own death. This runs in GitHub
Actions — independent of the Mac — and watches the one cloud-reachable heartbeat the Mac emits:
the `current.json` the publisher pushes to a secret gist every ~3 minutes.

If `published_at` goes stale past the threshold, the Mac/publisher is almost certainly down, so
we email Taylor once (and once more when it recovers). A failed GIST FETCH is treated as unknown
(GitHub/network hiccup), NOT as "Mac down" — we never cry wolf on our own side.

Secrets (GitHub Secrets -> env, never printed): GMAIL_USER, GMAIL_APP_PASSWORD. Reuses the same
Gmail App Password pattern as notify.py. No-ops cleanly (exit 0) if creds are absent.

Env knobs: WATCHDOG_GIST_ID, WATCHDOG_STALE_MIN (default 30), WATCHDOG_TO (default GMAIL_USER).
"""
import os
import sys
import json
import ssl
import smtplib
import datetime as dt
import urllib.request
import urllib.error
from email.message import EmailMessage

BASE = os.path.dirname(os.path.abspath(__file__))
STATE_PATH = os.path.join(BASE, "watchdog_state.json")
GIST_ID = os.environ.get("WATCHDOG_GIST_ID", "2a878ade5ebb53b82ebc7e6aecba97c1")
STALE_MIN = int(os.environ.get("WATCHDOG_STALE_MIN", "30"))
SMTP_HOST, SMTP_PORT = "smtp.gmail.com", 587
UA = "tempest-watchdog/1.0 (tkb5047@gmail.com)"


def _now():
    return dt.datetime.now(dt.timezone.utc)


def _parse_iso(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def load_state():
    try:
        with open(STATE_PATH) as f:
            return json.load(f)
    except Exception:                                  # noqa: BLE001
        return {"status": "ok", "since": None, "notified": False}


def save_state(state):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def fetch_published_epoch(gist_id, token=None):
    """Return the epoch of current.json's `published_at` (fallback `as_of`) from the gist, or
    raise on any fetch/parse failure (caller treats that as 'unknown', not 'down')."""
    headers = {"User-Agent": UA, "Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"https://api.github.com/gists/{gist_id}", headers=headers)
    with urllib.request.urlopen(req, timeout=20) as r:
        gist = json.load(r)
    files = gist.get("files", {})
    f = files.get("current.json") or next(iter(files.values()))
    content = json.loads(f["content"])
    stamp = content.get("published_at") or content.get("as_of")
    if not stamp:
        raise ValueError("current.json has no published_at/as_of")
    return _parse_iso(stamp).timestamp(), stamp


def decide(prev, cur_status, now_iso):
    """Pure state-machine step. Returns (new_state, event) where event is 'down', 'recovered',
    or None. new_state.notified means the CURRENT status has been emailed."""
    prev_status = prev.get("status", "ok")
    prev_notified = bool(prev.get("notified"))
    same = cur_status == prev_status
    since = prev.get("since") if (same and prev.get("since")) else now_iso

    event = None
    if cur_status == "down" and not (prev_status == "down" and prev_notified):
        event = "down"
    elif cur_status == "ok" and prev_status == "down" and prev_notified:
        event = "recovered"

    notified = prev_notified if same else False        # status flipped -> not yet notified
    return {"status": cur_status, "since": since, "notified": notified}, event


def send_email(subject, body):
    user = os.environ.get("GMAIL_USER")
    app_pw = os.environ.get("GMAIL_APP_PASSWORD")
    to = os.environ.get("WATCHDOG_TO") or user
    if not user or not app_pw:
        print("[watchdog] GMAIL creds absent — skipping send (will retry next run)", file=sys.stderr)
        return False
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = user, to, subject
    msg.set_content(body)
    ctx = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as s:
        s.starttls(context=ctx)
        s.login(user, app_pw)
        s.send_message(msg)
    print(f"[watchdog] emailed: {subject}")
    return True


def main():
    now = _now()
    try:
        epoch, stamp = fetch_published_epoch(GIST_ID, os.environ.get("GITHUB_TOKEN"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, KeyError) as e:
        # Our own fetch failed — do NOT declare the Mac down on a GitHub/network hiccup.
        print(f"[watchdog] gist fetch failed ({e}); leaving state unchanged", file=sys.stderr)
        return 0

    age_min = (now.timestamp() - epoch) / 60.0
    cur = "down" if age_min > STALE_MIN else "ok"
    prev = load_state()
    new_state, event = decide(prev, cur, now.isoformat())
    print(f"[watchdog] published {stamp} ({age_min:.1f}m ago, threshold {STALE_MIN}m) -> {cur}"
          f" (was {prev.get('status')}); event={event}")

    if event == "down":
        ok = send_email(
            "⚠️ Tempest station appears DOWN",
            f"The Tempest live feed (gist {GIST_ID}) is stale.\n\n"
            f"Last published: {stamp} (~{age_min:.0f} min ago; threshold {STALE_MIN} min).\n\n"
            "The Mac listener/publisher is likely down — which means the LOCAL iMessage alerts are "
            "also silent right now. Check the Mac (power, network, Messages signed in).\n\n"
            f"Gist: https://gist.github.com/{GIST_ID}")
        new_state["notified"] = ok
    elif event == "recovered":
        send_email("✅ Tempest station back online",
                   f"The live feed is fresh again — last published {stamp} (~{age_min:.0f} min ago).")
        new_state["notified"] = False

    save_state(new_state)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:                              # noqa: BLE001 - never fail the Action red
        print(f"[watchdog] unexpected error (non-fatal): {e}", file=sys.stderr)
        sys.exit(0)
