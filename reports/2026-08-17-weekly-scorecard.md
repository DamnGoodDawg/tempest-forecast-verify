# Tempest Forecast Scorecard — 2026-08-17

**Generated:** 2026-08-17 · **Data through:** 2026-08-16 · **n = 71 scored days** (all-time/rolling-90)

---

## ⚠️ STATION HEALTH ALERT

> **capture_misses = 1** — one day in the expected capture span has no irreplaceable Tempest snapshot. This breaks the station-online-streak count and means one day is permanently excluded from scoring. Investigate which date was missed and whether the daily capture workflow failed silently.

---

## Verdict — TEMPEST BEHIND

**Status:** TEMPEST BEHIND  
**Headline:** Tempest is within 3°F on **73% of days** vs NWS's **79%** — behind the best public forecast over the last 90 days. (n=71, DM p=0.025, best public: NWS)

The gap is statistically significant at p=0.025 (< 0.05 threshold). However, the DM p-value has been *rising* this past week (from 0.006 on Aug 11 to 0.025 today), meaning the lead-1 temperature gap is narrowing as Tempest improved from MAE 2.39 → 2.28 °F over the same span. The verdict remains TEMPEST BEHIND but momentum is shifting slightly.

**Advantage window context:** The guarantee window opened 2026-08-01 — only **16 scored days** so far in that window (TOO EARLY for a formal window verdict; ~14 more needed for a first read, 90 for a definitive one).

---

## Standings — 1-Day Lead (Rolling 90 days, n=71)

| Rank | Provider | MAE (°F) | % within 3°F | Precip CSI |
|------|----------|-----------|--------------|-----------|
| 1 | **NWS** | 1.98 | 79% | 0.35 |
| 2 | NBM | 2.15 | 73% | 0.34 |
| 3 | GFS | 2.21 | 74% | 0.34 |
| 4 | ★ **Tempest** | **2.28** | **73%** | **0.56** |
| 5 | ECMWF | 2.63 | 65% | 0.69 |

★ = subject under test. **Note on precip CSI:** Tempest (0.56) significantly outperforms NWS (0.35) on precipitation occurrence — a genuine bright spot that won't trigger the guarantee but is worth tracking.

### 2-Day Lead

| Provider | MAE (°F) | % within 3°F | Precip CSI |
|----------|-----------|--------------|-----------|
| NWS | 2.06 | 78% | 0.38 |
| **Tempest** | **2.36** | **69%** | **0.38** |
| NBM | 2.36 | 68% | 0.38 |
| GFS | 2.53 | 66% | 0.38 |
| ECMWF | 2.66 | 60% | 0.59 |

### 3-Day Lead

| Provider | MAE (°F) | % within 3°F | Precip CSI |
|----------|-----------|--------------|-----------|
| NWS | 2.11 | 78% | 0.31 |
| **Tempest** | **2.39** | **69%** | **0.27** |
| NBM | 2.42 | 67% | 0.23 |
| GFS | 2.86 | 64% | 0.23 |
| ECMWF | 2.99 | 54% | 0.49 |

---

## Weekly MAE Trend (1-Day Lead, Tempest vs NWS)

| Week of | Tempest MAE | NWS MAE | Gap (T–N) |
|---------|-------------|---------|-----------|
| Jun 1 | 1.53 | 1.47 | +0.06 |
| Jun 8 | 2.32 | 1.84 | +0.48 |
| Jun 15 | 2.12 | 2.25 | **–0.13** ← Tempest wins |
| Jun 22 | 2.78 | 2.56 | +0.22 |
| Jun 29 | 1.82 | 1.99 | **–0.17** ← Tempest wins |
| Jul 6 | 2.22 | 2.28 | **–0.06** ← Tempest wins |
| Jul 13 | 2.34 | 1.59 | +0.75 |
| Jul 20 | 2.82 | 2.16 | +0.66 |
| Jul 27 | 2.34 | 2.04 | +0.30 |
| Aug 3 | 3.07 | 1.77 | +1.30 ← worst week |
| **Aug 10** | **1.29** | **1.64** | **–0.35** ← **Tempest wins!** |

The most recent full week (Aug 10) is Tempest's best performance to date — MAE 1.29°F vs NWS 1.64°F. This is a strong week, though the cumulative gap (71-day) remains in NWS's favor.

---

## Biggest Recent Busts

| Date | Provider | Variable | Forecast | Actual | Error |
|------|----------|----------|----------|--------|-------|
| 2026-08-15 | ECMWF | High temp | 100°F | 95°F | +5°F |
| 2026-08-13 | NWS | High temp | 96°F | 92°F | +4°F |
| 2026-08-10 | GFS | High temp | 89°F | 92°F | –3°F |

*No Tempest busts in the top 3 this period.* NWS and ECMWF had significant high-temp over-forecasts this week (heat not quite as extreme as modeled).

---

## Rain Comparison (Tempest vs CoCoRaHS)

| Date | Tempest Raw (in) | CoCoRaHS (in) | Flag |
|------|-----------------|---------------|------|
| Jul 27 | 0.000 | — | — |
| Jul 28 | 0.847 | 0.72 | — |
| Jul 29 | 0.465 | — | — |
| Jul 30 | 0.000 | — | — |
| Jul 31 | 0.000 | — | — |
| Aug 1 | 0.023 | 0.72 | — |
| Aug 2 | 1.643 | 0.58 | — |
| Aug 3 | 0.000 | — | — |
| Aug 4 | 0.100 | 0.22 | — |
| Aug 5 | 0.675 | 0.75 | — |
| Aug 6 | 0.078 | — | — |
| Aug 7 | 0.000 | — | — |
| **Aug 8** | **1.030** | **0.02** | *(no flag — check)* |
| Aug 9 | 0.000 | — | — |
| Aug 10 | 0.641 | 0.28 | — |
| **Aug 11** | **0.001** | **0.22** | **⚠ DISAGREE** |
| Aug 12 | 0.237 | — | — |
| Aug 13 | 0.000 | — | — |
| **Aug 14** | **0.021** | **0.00** | **⚠ DISAGREE** |
| Aug 15 | 0.142 | 0.34 | — |
| Aug 16 | 0.000 | — | — |

Two "DISAGREE" flags this period (Aug 11, Aug 14). Aug 8 also shows a large discrepancy (Tempest 1.03" vs CoCoRaHS 0.02") with no flag — worth a manual check. Aug 1 shows Tempest 0.023" vs CoCoRaHS 0.72" — another large unflagged gap.

---

## Station Health

| Metric | Value | Status |
|--------|-------|--------|
| Capture days | 75 | — |
| **Capture misses** | **1** | **⚠️ FLAG — one snapshot permanently lost** |
| Station online streak | 39 days | ✅ |
| Hub online | true | ✅ |
| CoCoRaHS OK | true | ✅ |
| Last snapshot age | 0 hours ago | ✅ Fresh |
| Battery voltage | 2.66 V | ✅ Normal |
| Battery warn | false | ✅ |
| Rain sensor | OK | ✅ |
| Sensor faults | null | *(not monitored — not "healthy", just unmonitored)* |
| RSSI / Hub RSSI | null | *(not monitored via this path)* |

**Battery thresholds for reference:** WARN ≤ 2.40 V · ALERT ≤ 2.355 V · Current: 2.66 V ✅ safe margin.

**Sensor faults note:** `null` means sensor-fault monitoring is not available via this capture path (requires local UDP broadcast / tempest-local listener). This is expected per the README — it does not indicate "healthy."

---

## Guarantee Timeline

| Milestone | Date |
|-----------|------|
| ✅ Window opened | 2026-08-01 |
| 5-month scoring end | 2026-10-31 |
| Claim deadline | 2027-01-25 |
| Days elapsed in window | 16 |
| Days remaining in 5-month window | ~75 |

The advantage window opened Aug 1 (16 days scored so far). A formal verdict on the guarantee window requires ~14 more days for a first read and 90 days for a definitive result. The pre-window (all-time) standing shows Tempest BEHIND NWS, which is context — the guarantee window is still too early to call.

---

## Dashboard

🔗 [Live Dashboard](https://damngooddawg.github.io/tempest-forecast-verify/dashboard.html)

---

*Scorecard generated by the tempest-weekly-scorecard scheduled routine · 2026-08-17*
