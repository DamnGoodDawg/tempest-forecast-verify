#!/usr/bin/env python3
"""
notify.py - send the station-health warning email (stdlib only), then record it.

Runs in the daily Actions job AFTER health.py. Sends exactly one email per newly-opened
flag: health.py writes pending_email.json only for flag keys not already in the
health_emailed.json ledger, and this script appends those keys after a successful send,
so a repeat run with no new flag sends nothing.

Secrets (GitHub Secrets -> env; NEVER printed): GMAIL_USER, GMAIL_APP_PASSWORD.
A Gmail App Password (account -> Security -> App passwords), not the account password.

No-ops cleanly (exit 0) when there's nothing to send or credentials are absent, so it can
sit unconditionally in the workflow. The interim email path migrates to Pushover later
(alerts kickoff); the contract here is "one warning per flag-open event, no daily repeats."
"""
import json, os, sys, smtplib, ssl
from email.message import EmailMessage

BASE = os.path.dirname(os.path.abspath(__file__))
PENDING = os.path.join(BASE, "pending_email.json")
EMAILED = os.path.join(BASE, "health_emailed.json")
SMTP_HOST, SMTP_PORT = "smtp.gmail.com", 587


def load(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default


def main():
    pending = load(PENDING)
    if not pending or not pending.get("keys"):
        print("[notify] nothing pending — no email to send")
        return 0

    user = os.environ.get("GMAIL_USER")
    app_pw = os.environ.get("GMAIL_APP_PASSWORD")
    if not user or not app_pw:
        # Credentials not configured (e.g. local run / secret not set). Do NOT crash the
        # daily job and do NOT mark keys emailed, so the warning still fires once configured.
        print("[notify] GMAIL_USER/GMAIL_APP_PASSWORD not set — skipping send (will retry)",
              file=sys.stderr)
        return 0

    msg = EmailMessage()
    msg["From"] = user
    msg["To"] = pending.get("to", user)
    msg["Subject"] = pending["subject"]
    msg.set_content(pending["body"])

    ctx = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as s:
        s.starttls(context=ctx)
        s.login(user, app_pw)
        s.send_message(msg)
    print("[notify] sent warning email for keys: %s" % ", ".join(pending["keys"]))

    # record so the same flag never re-emails
    ledger = load(EMAILED, []) or []
    for k in pending["keys"]:
        if k not in ledger:
            ledger.append(k)
    with open(EMAILED, "w") as f:
        json.dump(ledger, f, indent=2)
    try:
        os.remove(PENDING)
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        # Never block the daily run on a mail hiccup; leave pending_email.json so it retries.
        print("[notify] send failed (will retry next run): %s" % e, file=sys.stderr)
        sys.exit(0)
