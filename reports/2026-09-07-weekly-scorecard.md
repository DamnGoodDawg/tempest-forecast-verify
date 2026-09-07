# Tempest Weekly Scorecard — 2026-09-07

**Generated:** 2026-09-07 (data through 2026-09-06, scores through 2026-09-05)  
**Dashboard:** https://damngooddawg.github.io/tempest-forecast-verify/dashboard.html

---

## ⚠️ STATION HEALTH — READ FIRST

| Check | Status |
|---|---|
| Hub online | ✅ Yes |
| Station online streak | 59 days ✅ |
| Last snapshot | 0 h ago ✅ |
| Battery | 2.65 V ✅ (OK — warn threshold: ≤2.40 V) |
| CoCoRaHS | ❌ **NOT OK** (`cocorahs_ok: false`) |
| Rain sensor | ✅ OK |
| Sensor faults | — *(null = not monitored, not "healthy")* |
| Capture days | 95 |
| **Capture misses** | ⚠️ **1 miss** — one day's capture failed |

> **FLAG — CAPTURE MISS:** `capture_misses = 1` — one of 95 capture days has failed. May cause a scoring gap; worth investigating which day and why.  
> **FLAG — CoCoRaHS DOWN:** `cocorahs_ok: false` — CoCoRaHS gauge data is unavailable. Rain comparison will be degraded until restored.

---

## 🏁 Headline Verdict

| | |
|---|---|
| **Status** | 🔴 **TEMPEST BEHIND** |
| **Window** | Rolling 90 days (n = **88** scored days, 2026-06-08 → 2026-09-05) |
| **Summary** | Tempest is within 3°F on **72%** of days vs NWS's **79%** — behind the best public forecast. |
| **Best public** | NWS |
| **DM p-value** | 0.0016 (highly significant — gap is real, not noise) |

**Advantage-window view (since Aug 1):** 36 days in — Tempest 72% within-3°F vs NWS **81%** (p = 0.0011). The gap is larger inside the guarantee window than over the full 90-day period. Tempest trails NWS by 0.56°F MAE (2.36 vs 1.80) since Aug 1.

---

## 📊 Standings — 1-Day Lead (Rolling 90 days, n=88)

| Provider | MAE °F | % within 3°F | Precip CSI |
|---|---|---|---|
| **NWS** 🥇 | **1.96** | **79%** | 0.35 |
| GFS | 2.13 | 76% | 0.33 |
| NBM | 2.26 | 70% | 0.33 |
| **⭐ Tempest** | **2.32** | **72%** | **0.50** |
| ECMWF | 2.62 | 66% | 0.63 |

*Lower MAE is better. Higher % within 3°F and CSI are better.*  
*Tempest leads all public providers on precip CSI (0.50 vs NWS 0.35) — but temperature accuracy is what the guarantee tracks.*

### 2-Day Lead

| Provider | MAE °F | % within 3°F | Precip CSI |
|---|---|---|---|
| **NWS** 🥇 | **2.03** | **77%** | 0.37 |
| **⭐ Tempest** | **2.35** | **69%** | **0.37** |
| NBM | 2.39 | 68% | 0.36 |
| GFS | 2.63 | 67% | 0.36 |
| ECMWF | 2.67 | 62% | 0.56 |

### 3-Day Lead

| Provider | MAE °F | % within 3°F | Precip CSI |
|---|---|---|---|
| **NWS** 🥇 | **2.13** | **75%** | 0.29 |
| **⭐ Tempest** | **2.44** | **66%** | **0.25** |
| NBM | 2.46 | 66% | 0.21 |
| GFS | 2.87 | 64% | 0.21 |
| ECMWF | 3.08 | 53% | 0.47 |

---

## 📈 Weekly MAE Trend — Tempest vs NWS (Last 8 Weeks)

| Week of | Tempest MAE | NWS MAE | Gap (T − NWS) | Note |
|---|---|---|---|---|
| 2026-07-13 | 2.34 | 1.59 | +0.75 | |
| 2026-07-20 | 2.82 | 2.16 | +0.66 | |
| 2026-07-27 | 2.34 | 2.04 | +0.30 | |
| 2026-08-03 | 3.07 | 1.77 | +1.30 | ❌ worst week |
| 2026-08-10 | **1.29** | 1.64 | **−0.35** | ✅ Tempest BEAT NWS |
| 2026-08-17 | 1.77 | 1.69 | +0.08 | nearly tied |
| 2026-08-24 | 2.54 | 1.61 | +0.93 | ❌ fell back hard |
| **2026-08-31** | **2.74** | **2.23** | **+0.51** | heat busts hit both |

**Assessment:** Last week (Aug 31) saw both Tempest and NWS degrade, driven by the Sep 5 heat bust (see below). The gap narrowed slightly (0.93 → 0.51) because NWS also struggled in extreme heat, not because Tempest improved. **The gap is not consistently closing.** The 28-day rolling gap (2.10 vs 1.77, +0.33°F) is slightly better than the 90-day gap (+0.36°F), but the advantage-window gap (since Aug 1) is 0.56°F — the worst of any window.

---

## 💥 Biggest Recent Busts

| Date | Source | Variable | Forecast | Actual | Error |
|---|---|---|---|---|---|
| 2026-09-05 | **Tempest** | High temp | 94°F | **100°F** | **−6°F** |
| 2026-09-05 | NBM | High temp | 94°F | 100°F | −6°F |
| 2026-08-30 | NBM | High temp | 86°F | 92°F | −6°F |

The Sep 5 heat event (100°F actual) caught both Tempest and the NBM by 6°F — a significant bust. NWS and GFS data for that day aren't listed as busts at the ≥6°F threshold, suggesting they may have been slightly better-calibrated on that day. This event dragged down the week-of-Aug-31 MAE for all providers.

---

## 🌧️ Rain Totals — Tempest vs CoCoRaHS (Last 30 Days)

| Date | Tempest Raw | CoCoRaHS | Flag |
|---|---|---|---|
| 2026-08-17 | 0.384" | 0.43" | *(close, no flag)* |
| 2026-08-18 | 0.052" | — | |
| 2026-08-20 | 0.000" | 0.14" | ⚠️ **disagree** |
| 2026-08-21 | 0.150" | — | |
| 2026-08-27 | 0.022" | 0.10" | *(no flag)* |
| 2026-08-28–09-05 | 0.000" | — | dry stretch (9 days) |

**1 disagree flag** in the recent window (Aug 20: Tempest reported 0.000" vs CoCoRaHS 0.14"). CoCoRaHS reporting is currently flagged as `cocorahs_ok: false`, so gauge comparisons are degraded. *(No separate RainCheck field available — corrected = raw throughout.)*

---

## 📅 Guarantee Timeline

| Milestone | Date | Days Away | Status |
|---|---|---|---|
| Advantage window opens | 2026-08-01 | — | ✅ Active (37 days in) |
| 5-month mark | 2026-10-31 | 54 days | ⏳ Approaching |
| Claim deadline | 2027-01-25 | 140 days | ⏳ |

**Advantage-window standing:** 36 scored days (of ~92 through Oct 31). Tempest would need to match or beat NWS over the remaining ~56 window days to overcome the current deficit. At the current gap rate (72% vs 81%), a substantial sustained improvement is required.

---

## Notes

- **Tempest wins on precipitation:** CSI 0.50 vs NWS 0.35 (1-day lead), and Brier score 0.204 vs NWS 0.239 — Tempest's rain probability forecasts are better calibrated. The guarantee tracks temperature, not rain.
- **NBM twin correlation:** r = 0.97 (all-time and 28-day). Tempest and NBM move almost in lockstep, suggesting Tempest's backbone is heavily NBM-influenced.
- **Tempest bias:** −2.21°F (28-day) — consistently under-forecasting high temperatures. The Sep 5 heat event is a clear example.
- **Weekly n is small (~7 days); significance requires cumulative n ≥ 30.** The 88-day rolling window has p = 0.0016 — the gap is real and statistically solid.
