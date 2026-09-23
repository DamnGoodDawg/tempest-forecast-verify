// node tests/dawg_experiment.test.mjs — renders the private tab's "Recipe experiment" card and the
// public standings' Dawg-recipe footnote from the REAL inline code in dashboard.html (lifted out between
// its /* <dawg-experiment> */ and /* <house-recipes> */ markers, plus the page's own esc/fmtMD/fmtSpan
// lines) inside a node vm with a tiny element stub — no browser, no network, no real passphrase.
// The payload comes from decrypting tests/fixtures/dawg_journal.enc.json with the fixture passphrase
// "test-pass-only", so this also proves the Mac -> gist -> browser chain carries `experiment` intact.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const DawgCrypto = require("../dawg_crypto.js");

const html = readFileSync(new URL("../dashboard.html", import.meta.url), "utf8");
const blob = JSON.parse(readFileSync(new URL("./fixtures/dawg_journal.enc.json", import.meta.url)));
const plain = JSON.parse(readFileSync(new URL("./fixtures/dawg_journal.plain.json", import.meta.url)));

function block(name) {
  const a = html.indexOf(`/* <${name}>`), b = html.indexOf(`/* </${name}> */`);
  assert.ok(a >= 0 && b > a, `markers for ${name} not found in dashboard.html`);
  return html.slice(a, b);
}
function line(prefix) {
  const l = html.split("\n").find(s => s.startsWith(prefix));
  assert.ok(l, `no line starting ${prefix}`);
  return l;
}
const els = {};
const errors = [];
const ctx = vm.createContext({
  console: { log: console.log, error: (...a) => errors.push(a.join(" ")) },
  dEl: (id) => (els[id] ||= { id, hidden: true, innerHTML: "" }),
});
vm.runInContext([line("const esc = "), line("const parseDate = "), line("const fmtMD = "), line("const fmtSpan = "),
  block("dawg-experiment"), block("house-recipes"),
  "globalThis.T = { dexpHTML, dexpFmt, dexpScale, dexpPill, renderDawgExperiment, houseRecipeFootHTML, fmtSpan, esc };",
].join("\n"), ctx, { filename: "dashboard.html#inline" });
const T = ctx.T;
const clone = (o) => JSON.parse(JSON.stringify(o));
let n = 0;
const test = (name, fn) => { fn(); n++; };

// ---------------------------------------------------------------- page wiring
test("section sits right after the verdict card and is in the lock/hide list", () => {
  assert.match(html, /id="dawgVerdict" hidden><\/section>\s*<section class="card" id="dawgExperiment" aria-labelledby="dawgExperiment-h" hidden><\/section>/);
  assert.match(html, /const DAWG_CARDS = \["dawgVerdict", "dawgExperiment",/);
  assert.match(html, /renderDawgVerdict\(d\); renderDawgExperiment\(d\);/);
  assert.match(html, /\$\{houseRecipeFootHTML\(d, rows\)\}/);
});

// ---------------------------------------------------------------- the fixture, through the real decrypt
const data = await DawgCrypto.decrypt(blob, "test-pass-only");
assert.deepEqual(data, plain);
const X = data.experiment;

test("fixture experiment honours the payload contract", () => {
  for (const k of ["name", "title", "current", "baseline", "candidate", "recipes", "status", "verdict", "decided_date",
                   "early_warning", "progress", "rule", "metrics", "note", "rollback"]) assert.ok(k in X, `missing ${k}`);
  for (const k of ["days", "need_days", "paired", "need_paired", "paired_short", "need_paired_short"]) assert.equal(typeof X.progress[k], "number");
  for (const r of X.recipes) for (const k of ["version", "label", "first_call", "last_call", "days", "tag", "changes"]) assert.ok(k in r, `recipe ${k}`);
  for (const m of X.metrics) {
    for (const k of ["key", "tweak", "headline", "label", "unit", "better", "v1", "v2", "delta", "status"]) assert.ok(k in m, `${m.key}.${k}`);
    assert.ok(["°F", "Brier", "pts", "in", "count", "%"].includes(m.unit), m.unit);
    assert.ok(["higher", "lower", "zero"].includes(m.better));
    assert.ok(["improved", "worse", "same", "insufficient"].includes(m.status));
  }
  assert.equal(X.metrics.filter(m => m.headline).length, 2);
  assert.equal(X.recipes.find(r => r.version === "v2").changes.length, 5);
});

test("collecting card renders every contract section from the fixture", () => {
  T.renderDawgExperiment(data);
  const el = els.dawgExperiment, h = el.innerHTML;
  assert.equal(el.hidden, false);
  assert.match(h, /Recipe experiment · are the tweaks helping\?/);
  assert.match(h, /Dawg recipe v2 — five tweaks/);
  assert.match(h, /chip--learning"><span class="dot"><\/span>Collecting/);
  assert.match(h, /<b>4 \/ 21<\/b>/);
  assert.match(h, /<b>6 \/ 60<\/b>/);
  assert.match(h, /<b>5 \/ 15<\/b>/);
  assert.match(h, /width:19%/);                                  // 4/21
  assert.match(h, /deploy\/2026-09-13-house-forecast/);
  assert.match(h, /deploy\/2026-09-23-dawg-v2/);
  assert.match(h, /Sep 13–23 · 10 days/);
  assert.match(h, /Sep 24–27 · 4 days/);
  assert.match(h, /<span class="dawg-pill ok">live<\/span>/);
  for (const c of X.recipes[1].changes) assert.ok(h.includes(T.esc(c)), `change: ${c}`);
  for (const m of X.metrics) assert.ok(h.includes(T.esc(m.label)), `metric: ${m.label}`);
  assert.ok(h.includes(T.esc(X.rule.text)));
  assert.ok(h.includes(T.esc(X.rollback)));
  assert.ok(h.includes(T.esc(X.note)));
  assert.ok(!/⚠ Early warning/.test(h));                         // no callout (the rule text names the early warning)
  assert.equal((h.match(/<tr class="hl">/g) || []).length, 2);  // headline rows emphasized
  // headline rows come first, then tweaks in order (morning table; the chat table follows it)
  const firstRows = [...h.split("Group-chat calls")[0].matchAll(/<tr(?: class="hl")?><td>(Headline|<span title="[^"]*">T\d<\/span>|T\d)<\/td>/g)].map(m => m[1].replace(/<[^>]+>/g, ""));
  assert.deepEqual(firstRows, ["Headline", "Headline", "T1", "T2", "T3", "T3", "T4", "T4", "T5", "T5"]);
  assert.ok(!h.includes("undefined") && !h.includes("NaN") && !h.includes("null"), "no leaked undefined/NaN/null");
});

test("metric cells: values by unit, Dawg/Blend sub-lines, status pills", () => {
  // the morning table only — the group-chat table below it is dawg_pager.test.mjs's
  const h = els.dawgExperiment.innerHTML.split("Group-chat calls")[0];
  const S = (...a) => a.map(x => `<span class="sub">${x}</span>`).join("");
  assert.ok(h.includes("-0.04°F" + S("n=44", "Dawg 1.91", "Blend 1.87")));                  // H1 v1 (live 09-23 journal)
  assert.ok(h.includes("+0.45°F" + S("n=6", "Dawg 1.62", "Blend 2.07")));                   // H1 v2
  assert.ok(h.includes("+0.002" + S("n=44", "Dawg 0.196", "Blend 0.199")));                 // H2
  assert.ok(h.includes("-1.49°F" + S("n=44", "Dawg -1.49", "Blend -1.55")));                // T1 bias, signed
  assert.ok(h.includes("+17 pts" + S("n=11", "Dawg +17", "Blend +18")));                    // T2 gap as points, signed subs
  assert.ok(h.includes("+5 pts" + S("n=3", "Dawg +5", "Blend —")));                         // missing Blend -> dash
  assert.ok(h.includes(">36%" + S("n=11", "Dawg 36%", "Blend 25%")));                       // T3 rate, unsigned
  assert.ok(h.includes(">6" + S("n=27", "Dawg 6", "Blend 12")));                           // count
  assert.ok(h.includes(">36%" + S("n=44")));                                                // move rate
  assert.ok(h.includes("+0.018&quot;" + S("n=44", "Dawg 0.194", "Blend 0.212")));           // amounts at 3 dp
  assert.match(h, /counts past ±0\.25°F/);
  assert.match(h, /counts past ±0\.010/);
  assert.match(h, /counts past ±10\.0 pts/);
  assert.match(h, /counts past ±0\.030&quot;/);
  assert.match(h, /\+46\.9 pts<\/td>/);                                                   // move_rate change in points
  assert.match(h, /<td class="num">\+0\.025&quot;<\/td>/);                                // 0.025" change doesn't round onto 0.03
  assert.match(h, /<td class="num muted">-11\.9 pts<\/td>/);                                // insufficient change muted
  assert.equal((h.match(/dawg-pill ok">improved/g) || []).length, 4);
  assert.equal((h.match(/dawg-pill pend">too few/g) || []).length, 3);
  assert.equal((h.match(/dawg-pill pend">same/g) || []).length, 3);
});

test("decided verdicts: chip colour, date, latched copy, rollback emphasis", () => {
  const want = { HELPED: "ok", HURT: "fail", MIXED: "warn", NEUTRAL: "learning" };
  for (const [v, chip] of Object.entries(want)) {
    const d = clone(data);
    Object.assign(d.experiment, { status: "decided", verdict: v, decided_date: "2026-10-15" });
    T.renderDawgExperiment(d);
    const h = els.dawgExperiment.innerHTML;
    assert.match(h, new RegExp(`chip--${chip}"><span class="dot"></span>${v}<`), v);
    assert.match(h, /decided Oct 15/);
    assert.match(h, /The verdict is latched/);
    assert.ok(!/Collecting/.test(h) && !/dexp-bars/.test(h), "no progress bars once decided");
    const loud = v === "HURT" || v === "MIXED";
    assert.equal(/<div class="dexp-callout" role="note"><b>Rollback\.<\/b>/.test(h), loud, `${v} rollback callout`);
    assert.equal(/<p class="dawg-note"><b>Rollback:<\/b>/.test(h), !loud, `${v} rollback note`);
  }
});

test("early warning callout", () => {
  const d = clone(data);
  d.experiment.early_warning = { date: "2026-10-01", text: "Rain Brier edge fell 0.024 below v1's (2x the 0.01 threshold)." };
  T.renderDawgExperiment(d);
  assert.match(els.dawgExperiment.innerHTML, /dexp-callout fail" role="note"><b>⚠ Early warning · Oct 1<\/b> — Rain Brier edge fell 0\.024/);
});

test("old payloads and junk hide the card; a throwing field never escapes", () => {
  for (const d of [{}, { experiment: null }, { experiment: "x" }, null]) {
    els.dawgExperiment = { id: "dawgExperiment", hidden: false, innerHTML: "stale" };
    T.renderDawgExperiment(d);
    assert.equal(els.dawgExperiment.hidden, true);
    assert.equal(els.dawgExperiment.innerHTML, "");
  }
  // minimal object: renders, no crash, sensible dashes
  T.renderDawgExperiment({ experiment: {} });
  assert.equal(els.dawgExperiment.hidden, false);
  assert.match(els.dawgExperiment.innerHTML, /No metrics yet/);
  assert.match(els.dawgExperiment.innerHTML, /<b>0 \/ —<\/b>/);
  // metrics with missing sides/values -> em dashes, never "undefined"
  T.renderDawgExperiment({ experiment: { metrics: [{ key: "high_mae_edge", unit: "°F", better: "higher", status: "insufficient" }] } });
  const h = els.dawgExperiment.innerHTML;
  assert.match(h, /—<span class="sub">n=0<\/span>/);
  assert.ok(!h.includes("undefined") && !h.includes("NaN"));
  // a getter that throws mid-render: caught, card hidden, error logged
  const evil = { get metrics() { throw new Error("boom"); } };
  T.renderDawgExperiment({ experiment: evil });
  assert.equal(els.dawgExperiment.hidden, true);
  assert.ok(errors.some(e => /boom/.test(e)));
});

test("everything from the payload is escaped", () => {
  const d = clone(data);
  d.experiment.title = "<img src=x onerror=alert(1)>";
  d.experiment.metrics[0].label = "<script>x</script>";
  d.experiment.recipes[1].changes[0] = '"><b>';
  d.experiment.rollback = "<a href=javascript:1>";
  T.renderDawgExperiment(d);
  const h = els.dawgExperiment.innerHTML;
  assert.ok(!h.includes("<img") && !h.includes("<script") && !h.includes("<a href"));
  assert.ok(h.includes("&lt;script&gt;x&lt;/script&gt;"));
});

// ---------------------------------------------------------------- formatting helpers
test("dexpFmt / dexpScale", () => {
  assert.equal(T.dexpFmt(-1.456, "°F", { signed: true }), "-1.46°F");
  assert.equal(T.dexpFmt(0.001, "°F", { signed: true }), "0.00°F");     // no "+0.00"
  assert.equal(T.dexpFmt(-0.001, "°F", { signed: true }), "0.00°F");    // no "-0.00"
  assert.equal(T.dexpFmt(0.012, "Brier", { signed: true }), "+0.012");
  assert.equal(T.dexpFmt(0.12, "in", { signed: true }), '+0.120"');
  assert.equal(T.dexpFmt(-1.456, "°F", { signed: true, bare: true }), "-1.46");      // sub-line: no unit
  assert.equal(T.dexpFmt(0.39, "%", { scale: 100, bare: true }), "39%");             // …except percentages
  assert.equal(T.dexpFmt(3.4, "count"), "3");
  assert.equal(T.dexpFmt(0.523, "%", { scale: 100 }), "52%");
  assert.equal(T.dexpFmt(0.31, "%", { scale: 100, signed: true, delta: true }), "+31.0 pts");
  assert.equal(T.dexpFmt(0.046, "pts", { scale: 100, signed: true, delta: true }), "+4.6 pts");
  assert.equal(T.dexpFmt(0.196, "pts", { scale: 100, signed: true }), "+20 pts");
  assert.equal(T.dexpFmt(null, "°F"), "—");
  assert.equal(T.dexpFmt(undefined, "%"), "—");
  assert.equal(T.dexpFmt("abc", "in"), "—");
  assert.equal(T.dexpFmt(1.5, "mph"), "1.50 mph");                    // unknown unit degrades
  const m = { unit: "%", v1: { value: 0.4 }, v2: { value: 0.6 }, delta: 0.2 };
  assert.equal(T.dexpScale(m), 100);                                   // fractions -> x100
  assert.equal(T.dexpScale({ unit: "%", v1: { value: 40 }, v2: { value: 60 }, delta: 20 }), 1);  // already percent
  assert.equal(T.dexpScale({ unit: "°F", v1: { value: 0.4 } }), 1);
  assert.match(T.dexpPill("worse"), /dawg-pill miss">worse/);
  assert.match(T.dexpPill("weird"), /dawg-pill pend">weird/);
});

// ---------------------------------------------------------------- public standings footnote
test("house-recipe footnote under the standings", () => {
  const rows = [{ source: "Tempest" }, { source: "Dawg" }];
  const v1 = { version: "v1", first_date: "2026-09-14", last_date: "2026-09-23", n_days: 10, n_scored_days: 8 };
  const v2 = { version: "v2", first_date: "2026-09-24", last_date: "2026-09-30", n_days: 7, n_scored_days: 6 };
  assert.equal(T.houseRecipeFootHTML({}, rows), "");                               // old feed
  assert.equal(T.houseRecipeFootHTML({ house_recipes: [v1] }, rows), "");          // nothing changed yet
  assert.equal(T.houseRecipeFootHTML({ house_recipes: [v1, v2] }, [{ source: "NWS" }]), "");   // no Dawg row shown
  const f = T.houseRecipeFootHTML({ house_recipes: [v1, v2] }, rows);
  assert.match(f, /Dawg's recipe changed <b>Sep 24<\/b> \(v1 Sep 14–23 → v2\)\. Numbers above mix both until v2 has its own 90 days — the private tab tracks the split\./);
  assert.match(f, /class="recipe-foot"/);
  const later = T.houseRecipeFootHTML({ house_recipes: [v1, { ...v2, n_days: 95, last_date: "2026-12-27" }] }, rows);
  assert.match(later, /v1 Sep 14–23 → v2\)\. These all-time rows still include the earlier recipe's days/);
  // rolled back: v1 is making calls again after a v2 detour
  const rb = T.houseRecipeFootHTML({ house_recipes: [{ ...v1, last_date: "2026-10-05" }, { ...v2, last_date: "2026-10-01" }] }, rows);
  assert.match(rb, /Dawg is back on recipe <b>v1<\/b> \(v2 Sep 24–Oct 1 in between\)/);
  assert.equal(T.fmtSpan("2026-09-28", "2026-10-03"), "Sep 28–Oct 3");
  assert.equal(T.fmtSpan("2026-09-24", "2026-09-24"), "Sep 24");
});

// fallback sample in the page itself must carry a valid two-recipe block (it drives the offline render)
test("fallback sample carries house_recipes", () => {
  const m = html.match(/<script type="application\/json" id="fallback-data">([\s\S]*?)<\/script>/);
  assert.ok(m, "fallback-data block");
  const fb = JSON.parse(m[1]);
  assert.equal(fb.house_recipes.length, 2);
  assert.match(T.houseRecipeFootHTML(fb, [{ source: "Dawg" }]), /Dawg's recipe changed <b>Aug 14<\/b>/);
});

console.log(`dawg_experiment: ${n} render checks OK (experiment card + recipe footnote, fixture ${blob.plain_bytes} bytes)`);
