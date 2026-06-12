#!/usr/bin/env python3
"""
verify.py - forecast verification engine (stdlib only).

Scores forecast records against actuals. A forecast record is a dict:
  {date: 'YYYY-MM-DD' (valid date), lead: int (days), source: str,
   var: 'high'|'low'|'pop'|'precip_amt', value: float}
Actuals: {date, var, value}  where var in high/low/precip_amt
(precip occurrence derived from precip_amt >= 0.01).

Metrics:
  temp (high/low): MAE, RMSE, bias, pct_within_3F
  pop: Brier score (vs occurrence), resolution via base rate
  precip occurrence (from pop>=50 as yes/no, and from precip_amt>0.005 forecast): POD/FAR/CSI
  Paired comparison: Diebold-Mariano test on |err_A|-|err_B| with HAC variance.
"""
import math, csv, sys, json
from collections import defaultdict

WET_THRESHOLD = 0.01  # inches, matches NWS PoP definition

def mae(e): return sum(abs(x) for x in e)/len(e)
def rmse(e): return math.sqrt(sum(x*x for x in e)/len(e))
def bias(e): return sum(e)/len(e)
def pct_within(e, t=3.0): return 100.0*sum(1 for x in e if abs(x) <= t)/len(e)

def temp_scores(pairs):
    """pairs: list of (forecast, actual)."""
    e = [f-a for f,a in pairs]
    return {"n": len(e), "mae": round(mae(e),2), "rmse": round(rmse(e),2),
            "bias": round(bias(e),2), "pct_within_3F": round(pct_within(e),1)}

def brier(pairs):
    """pairs: list of (pop 0-100, wet bool)."""
    bs = sum((p/100.0 - (1.0 if w else 0.0))**2 for p,w in pairs)/len(pairs)
    base = sum(1 for _,w in pairs if w)/len(pairs)
    bs_clim = base*(1-base)  # Brier of always forecasting climatological base rate
    bss = 1 - bs/bs_clim if bs_clim > 0 else float('nan')
    return {"n": len(pairs), "brier": round(bs,4), "base_rate": round(base,3),
            "bss_vs_base": round(bss,3)}

def contingency(pairs):
    """pairs: list of (forecast_wet bool, observed_wet bool)."""
    h = sum(1 for f,o in pairs if f and o); m = sum(1 for f,o in pairs if not f and o)
    fa = sum(1 for f,o in pairs if f and not o); cn = sum(1 for f,o in pairs if not f and not o)
    pod = h/(h+m) if h+m else float('nan')
    far = fa/(h+fa) if h+fa else float('nan')
    csi = h/(h+m+fa) if h+m+fa else float('nan')
    return {"n": len(pairs), "hits": h, "misses": m, "false_alarms": fa, "correct_nulls": cn,
            "pod": round(pod,3), "far": round(far,3), "csi": round(csi,3)}

def norm_cdf(x): return 0.5*(1+math.erf(x/math.sqrt(2)))

# --- Student-t two-sided p-value (for the HLN small-sample correction below) -------
# stdlib has no t-distribution, so we evaluate it through the regularized incomplete
# beta function (Numerical Recipes betacf/betai); math.lgamma supplies the log-beta.
def _betacf(a, b, x):
    MAXIT, EPS, FPMIN = 300, 3e-16, 1e-300
    qab, qap, qam = a+b, a+1, a-1
    c = 1.0
    dd = 1.0 - qab*x/qap
    if abs(dd) < FPMIN: dd = FPMIN
    dd = 1.0/dd
    h = dd
    for m in range(1, MAXIT+1):
        m2 = 2*m
        aa = m*(b-m)*x/((qam+m2)*(a+m2))
        dd = 1.0 + aa*dd
        if abs(dd) < FPMIN: dd = FPMIN
        c = 1.0 + aa/c
        if abs(c) < FPMIN: c = FPMIN
        dd = 1.0/dd
        h *= dd*c
        aa = -(a+m)*(qab+m)*x/((a+m2)*(qap+m2))
        dd = 1.0 + aa*dd
        if abs(dd) < FPMIN: dd = FPMIN
        c = 1.0 + aa/c
        if abs(c) < FPMIN: c = FPMIN
        dd = 1.0/dd
        de = dd*c
        h *= de
        if abs(de-1.0) < EPS: break
    return h

def _betai(a, b, x):
    if x <= 0.0: return 0.0
    if x >= 1.0: return 1.0
    lbeta = math.lgamma(a+b) - math.lgamma(a) - math.lgamma(b)
    bt = math.exp(lbeta + a*math.log(x) + b*math.log(1.0-x))
    if x < (a+1.0)/(a+b+2.0):
        return bt*_betacf(a, b, x)/a
    return 1.0 - bt*_betacf(b, a, 1.0-x)/b

def t_sf_two_sided(t, v):
    """Two-sided tail prob P(|T_v| > |t|) for Student-t with v degrees of freedom."""
    if v <= 0: return float('nan')
    return _betai(v/2.0, 0.5, v/(v + t*t))

def diebold_mariano(err_a, err_b, h=1):
    """DM test on loss differential d = |err_a| - |err_b| (paired by date).
    HAC variance with lag h-1 (use h = lead days). Negative DM => A better.

    Callers may also pass already-collapsed per-date losses (non-negative) as err_a/err_b
    — abs() is then a no-op and d is just the loss difference, which is the A6 convention.

    A6: applies the Harvey-Leybourne-Newbold small-sample correction — scale the statistic
    by sqrt((n+1-2h+h(h-1)/n)/n) and refer it to Student-t(n-1) instead of N(0,1). Both
    shrink the optimistic small-sample p-values that a raw normal DM produces."""
    d = [abs(a)-abs(b) for a,b in zip(err_a, err_b)]
    n = len(d)
    if n < 10: return {"n": n, "note": "too few pairs"}
    dbar = sum(d)/n
    gamma0 = sum((x-dbar)**2 for x in d)/n
    var = gamma0
    for k in range(1, h):
        gk = sum((d[i]-dbar)*(d[i-k]-dbar) for i in range(k,n))/n
        var += 2*gk
    if var <= 0: var = gamma0
    dm = dbar/math.sqrt(var/n)
    # Harvey-Leybourne-Newbold correction + Student-t reference distribution.
    adj = math.sqrt(max((n + 1 - 2*h + h*(h-1)/n) / n, 0.0))
    dm_hln = dm * adj
    if n - 1 > 0 and adj > 0:
        p = t_sf_two_sided(dm_hln, n-1)
    else:
        p = 2*(1-norm_cdf(abs(dm)))
    return {"n": n, "mean_loss_diff": round(dbar,3), "dm_stat": round(dm,3),
            "dm_stat_hln": round(dm_hln,3), "p_value": round(p,4),
            "better": "A" if dbar < 0 else "B"}

def score(records, actuals):
    """records: forecast records; actuals: {(date,var): value}. Returns nested results."""
    wet = {d: v >= WET_THRESHOLD for (d, var), v in actuals.items() if var == "precip_amt"}
    out = defaultdict(dict)
    groups = defaultdict(list)
    for r in records:
        groups[(r["source"], r["lead"], r["var"])].append(r)
    for (src, lead, var), recs in sorted(groups.items()):
        key = f"{src} lead{lead}"
        if var in ("high","low"):
            pairs = [(r["value"], actuals[(r["date"],var)]) for r in recs if (r["date"],var) in actuals]
            if pairs: out[key][var] = temp_scores(pairs)
        elif var == "pop":
            pairs = [(r["value"], wet[r["date"]]) for r in recs if r["date"] in wet]
            if pairs:
                out[key]["pop"] = brier(pairs)
                out[key]["precip_yn"] = contingency([(p >= 50, w) for p,w in pairs])
    return dict(out)

def paired_temp_errors(records, actuals, var, lead):
    """Returns {source: {date: error}} for DM pairing (single var)."""
    by_src = defaultdict(dict)
    for r in records:
        if r["var"] == var and r["lead"] == lead and (r["date"],var) in actuals:
            by_src[r["source"]][r["date"]] = r["value"] - actuals[(r["date"],var)]
    return by_src

def per_date_losses(records, actuals, lead):
    """A6: one collapsed loss per (source, date) = mean(|high err|, |low err|).

    Feeding the DM test two correlated observations per date (high AND low share an
    airmass) understated its variance — at h=1 the HAC lag terms are zero, so the
    correlation was never modeled — and produced optimistically small p-values. Pooling
    each date into a single mean-absolute loss restores one independent obs per day."""
    by_src = defaultdict(lambda: defaultdict(list))
    for r in records:
        if r["lead"] == lead and r["var"] in ("high", "low") and (r["date"], r["var"]) in actuals:
            by_src[r["source"]][r["date"]].append(abs(r["value"] - actuals[(r["date"], r["var"])]))
    return {s: {dte: sum(v)/len(v) for dte, v in dd.items()} for s, dd in by_src.items()}

def dm_matrix(records, actuals, lead, var=None):
    """Pairwise DM on per-date collapsed losses at the given lead. `var` is accepted for
    backward compatibility but ignored — losses now pool high+low into one per date (A6).
    HAC lag uses h=lead on the collapsed series."""
    loss = per_date_losses(records, actuals, lead)
    srcs = sorted(loss)
    results = {}
    for i, a in enumerate(srcs):
        for b in srcs[i+1:]:
            common = sorted(set(loss[a]) & set(loss[b]))
            if len(common) < 10: continue
            results[f"{a} vs {b}"] = diebold_mariano(
                [loss[a][dte] for dte in common], [loss[b][dte] for dte in common], h=max(1, lead))
    return results

if __name__ == "__main__":
    # CLI: verify.py forecasts.csv actuals.csv -> report json to stdout
    fcsv, acsv = sys.argv[1], sys.argv[2]
    records = []
    with open(fcsv) as f:
        for row in csv.DictReader(f):
            records.append({"date": row["date"], "lead": int(row["lead"]),
                            "source": row["source"], "var": row["var"], "value": float(row["value"])})
    actuals = {}
    with open(acsv) as f:
        for row in csv.DictReader(f):
            actuals[(row["date"], row["var"])] = float(row["value"])
    report = {"scores": score(records, actuals)}
    leads = sorted({r["lead"] for r in records})
    report["significance"] = {f"lead{L}": dm_matrix(records, actuals, L) for L in leads}
    print(json.dumps(report, indent=2))
