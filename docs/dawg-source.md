# Dawg & Blend — the two house forecast rows

Added 2026-09-13. Two new scored sources join Tempest and the four public forecasts in the
same standings table:

| Source | What it is | Where it comes from | History on day one |
|---|---|---|---|
| **Dawg** | The house AI meteorologist's own morning call | published by the always-on Mac at ~05:35 ET, captured from a gist | starts at zero, grows daily |
| **Blend** | A deterministic best-source-per-variable baseline | computed in `extract.py` from the already-captured public files | **back-filled across every capture day** |

Both are tagged `house` in `scores.json` and carry a **HOUSE** chip on the dashboard. They are
scored exactly like everyone else — same actuals, same leads, same metrics. What they can
*never* be is the guarantee's rival: see [PUBLIC_SOURCES](#the-public_sources-guard).

---

## 1 · The Dawg file contract

The Mac's publisher PATCHes a plain JSON file, `dawg_forecast.json`, onto the same secret gist
the dashboard already reads `current.json` / `storms.json` from:

```
https://gist.githubusercontent.com/DamnGoodDawg/2a878ade5ebb53b82ebc7e6aecba97c1/raw/dawg_forecast.json
```

```json
{"v": 1, "source": "Dawg", "issued_at": "2026-09-14T05:47:12-04:00", "issued_date": "2026-09-14",
 "kind": "dawg", "model": "claude-fable-5", "label": "Dawg Forecast",
 "summary": "40% storms, best shot 3-7 PM, high near 91",
 "days": [
   {"date": "2026-09-14", "lead": 0, "pop": 40, "high": 91, "low": 71, "amt_in": 0.15,
    "win_start": "15:00", "win_end": "19:00", "conf": "med", "reason": null},
   {"date": "2026-09-15", "lead": 1, "pop": 75, "high": 85, "low": 68, "amt_in": 0.30,
    "conf": "med", "reason": "AFD shortwave; 4 of 6 models wet"}
 ],
 "blend": [
   {"date": "2026-09-14", "lead": 0, "pop": 35, "high": 90, "low": 71, "amt_in": 0.10,
    "sources": {"high": "NWS", "low": "NWS", "pop": "ECMWF+Tempest"}}
 ]}
```

- `days` runs lead 0 through 7. **Any field may be null.**
- `pop` is **0–100** (not a fraction). `high` / `low` are °F max/min for the ET calendar `date`.
- `kind` is `"dawg"` when the LLM call succeeded and `"blend"` when the Mac fell back to its own
  deterministic blend (in which case `days` == `blend` numbers).
- `blend` is the Mac's own live blend, carried for the record. **This repo does not score it** —
  the `Blend` row here is recomputed from the captured files (§3).

### How capture.py handles it

`capture.py` step 8 is a **soft** step — it can never fail the daily run:

1. GET the raw URL with a cache-buster query param and the repo's User-Agent.
2. Parse the JSON. Require `issued_date == the capture's ET date`.
3. If it is stale, missing, or unparseable → append a line to `warnings` in `_capture_log.json`
   and **write no file at all**.
4. Otherwise write `data/<date>/dawg.json` through the usual `write()` wrapper (`meta` + `data`),
   with `source_url` and the **`sha256` of the exact bytes fetched** added to `meta`.

The freshness gate is the whole point: a gist raw URL will happily serve yesterday's file
forever, and silently scoring a stale call against today's leads is the one way this row could
cheat. The filename deliberately has no leading underscore — GitHub Pages does not serve
underscore-prefixed paths.

### How extract.py handles it

`parse_dawg()` re-checks **both** gates before emitting a single record (belt and braces — a
hand-copied or re-committed snapshot must not sneak past capture's check):

- `kind == "dawg"` — a `"blend"` fallback day is **not scored as Dawg**. Crediting the AI for a
  forecast it never made would flatter the row.
- `issued_date == <capture date>`.

Then it emits `high` / `low` / `pop` for **leads 1–3 only** (the repo's `LEADS`); leads 0 and
4–7 are captured and archived but never scored. Leads are derived from the dates, never from
the file's own `lead` field. Nulls are skipped; `pop` passes through unscaled.

`dawg.json` is optional everywhere — the overwhelming majority of historical capture days have
none, and `parse_dawg(None, …)` returns `[]`.

---

## 2 · Is it a fair fight?

Yes, and this is the part worth defending:

- **Same instant.** Dawg's file is fetched inside the same capture run as the Tempest, NWS and
  Open-Meteo snapshots, then committed to `data/` and never rewritten — the same
  tamper-evident evidence record the rest of the scoreboard rests on. `meta.sha256` pins the
  exact bytes.
- **Issued earlier, not later.** Dawg's call is made at ~05:35 ET from live sources. The public
  forecasts it is scored against are frozen roughly 1–5 hours later (whenever the capture run
  fires). If anything, the house row is handicapped: it commits first.
- **No hindsight.** Nothing about a Dawg day can be revised after capture. A late or missing
  publish simply produces no Dawg row for that day, which shows up honestly as a smaller `n`.
- **The `Blend` row measures the RULE, not the Mac.** It is recomputed here from the captured
  public files, so it is reproducible from the repo alone. It is *not* the Mac's live blend
  (which rides along in the file's `blend` key purely for the record).

The cost of the back-fill is worth stating plainly: **Blend arrives with ~90 scored days and
Dawg arrives with none.** That asymmetry is real and the dashboard shows it — every standings
row carries `n_days`, and anything under 10 scored days is greyed out and tagged `early`.

---

## 3 · The Blend rule, verbatim

> **high/low = NWS value, else NBM, else Tempest; pop = mean(ECMWF pop, Tempest pop) when both
> exist, else whichever exists, else NWS.**

Implemented in `extract.blend_records()` and stated in the same words in its docstring and in
`extract.BLEND_TEMP_PREFERENCE`. The Mac's own blend uses this identical rule.

Details:

- Applied per **(target date, lead)**. That tuple pins the capture date exactly
  (`capture = date − lead`), so no capture-date bookkeeping is needed.
- The temperature fallback is **per variable**: if NWS published a high but no low, the high
  comes from NWS and the low falls through to NBM on its own.
- `Dawg` never feeds the Blend. The baseline stays a public/Tempest construction, so
  "Blend beat Dawg" is not partly Dawg grading itself.
- Re-running over records that already contain `Blend` rows is a no-op (it never blends the
  blend).
- Because it derives from the frozen captures, it **back-fills across the entire history**
  automatically — no new fetches, no new files.

---

## 4 · The PUBLIC_SOURCES guard

`extract.py` carries three lists:

```python
SOURCES        = ["Tempest", "Dawg", "Blend", "NBM", "ECMWF", "NWS", "GFS"]   # display order
PUBLIC_SOURCES = ["NBM", "NWS", "ECMWF", "GFS"]
HOUSE_SOURCES  = ["Dawg", "Blend"]
```

`temp_verdict()` picks its rival with `r["source"] in PUBLIC_SOURCES` — **not** "anything that
isn't Tempest", which is what the code did before the house rows existed. Without the
allowlist, a good week from Dawg or Blend would quietly become *"the best public forecast"* in
the verdict sentence and in every row of `verdict_history.json` — turning a claim about the
competition into a claim about a row we wrote ourselves. That would be the single most
embarrassing way to lose a guarantee argument.

The same guard is mirrored on the dashboard in both "best public" computations
(`isPublic()`, which prefers `scores.sources[src].public` from the feed and falls back to a
hardcoded list only for older feeds).

**What is *not* gated:** the `winners` panel's `leader` field, the standings ranking, the trend
chart, `busts`, and the Brier table. The field leader on any metric may be any source,
Dawg and Blend included — that is a fact about the data and it gets reported.

---

## 5 · What the page reads

`scores.json` gained two additive keys (the never-break contract: an older dashboard ignores
unknown keys cleanly).

**Per standings row:**

```json
{ "source": "Dawg", "mae": 1.71, "pct_within_3f": 86, "csi": 0.76, "brier": 0.079,
  "n_days": 6, "house": true }
```

- `n_days` — distinct scored target dates that row rests on. Under `EARLY_N_DAYS` (10) the
  dashboard greys the row and tags it `early`.
- `house` — present and `true` only on Dawg/Blend rows.

**Top level:**

```json
"sources": {
  "Tempest": { "public": false, "house": false, "first_date": "2026-06-05", "n_days": 98 },
  "Dawg":    { "public": false, "house": true,  "first_date": "2026-09-14", "n_days": 3 },
  "Blend":   { "public": false, "house": true,  "first_date": "2026-06-05", "n_days": 98 },
  "NBM":     { "public": true,  "house": false, "first_date": "2026-06-05", "n_days": 98 }
}
```

Only sources that actually have records appear, in display order — so a source that has never
published yet gets no dead legend entry on the chart. The dashboard derives its provider order
and its public/house labelling from this block, falling back to a hardcoded list when the feed
predates it.

### A naming collision to keep straight

`standings["blend"]` (lower-case, `extract.POOLED_KEY`) is the **pooled lead-1–3 row set** and
predates all of this. `"Blend"` (capital B) is the new **source**. They coexist — the pooled
key legitimately contains a `Blend` row. A source only earns a place in the pooled row when it
has records at *every* lead in `LEADS` (`sources_with_all_leads`), so a lead-1-only source
cannot be flattered by an average its rivals pay lead-3 misses into.

---

## 6 · Operational notes

- **The cron moved to `23 11 * * *`** (07:23 EDT / 06:23 EST). It was `23 10` — a punctual
  winter run at 05:23 EST would have beaten Dawg's 05:35 call to the gist every day and fetched
  yesterday's file, which the freshness gate then correctly refuses, losing the row.
- **Dawg's numbers are public.** They are committed to a public repo and rendered on a public
  dashboard. (The *private* forecast journal on the "Dawg's Calls" tab is a separate thing —
  that payload is encrypted.)
- **A missing Dawg day is normal and silent** (a warning line in `_capture_log.json`, nothing
  more). Check `data/<date>/_capture_log.json → warnings` if a day is unexpectedly absent.
