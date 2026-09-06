#!/usr/bin/env python3
"""Gate a finished file's language controls against the languages that were asked for.

    python3 scripts/check_languages.py FILE --languages en,ko
    python3 scripts/check_languages.py FILE --intake intake.json
    python3 scripts/check_languages.py FILE --languages en --json

The authority is the **intake answer**, never the file. `answers.languages` is
what the reader chose to be able to read; a built file is correct when exactly
those languages are reachable from its own chrome — no fewer, and no more.

Both directions are real failures, and each has shipped somewhere in this
class of tool:

  a language chosen but unreachable   the content may well be in the file,
                                      hidden behind `body[data-lang]`, with no
                                      control that selects it. The reader
                                      never learns it is there.
  a language offered but not chosen   a leftover button from the template.
                                      It either shows half-translated
                                      placeholder text or silently does
                                      nothing. `references/applying-answers.md`
                                      already calls a one-language switch "a
                                      control that does nothing"; this is the
                                      check that was missing behind that
                                      sentence.

`scripts/tedandlisa_apply.py` enforces the rule mechanically on
`monomind-deck` alone (`apply_languages` deletes the switch, the
`#google_translate_element` and the translate script when English is all that
is left). On the other ten registry entries it reports `NOT-MECHANICAL` and
hands the work to the agent, because each language there is written content
rather than chrome. That is the right split — but it left nine templates with
a documented rule and nothing checking it. This is that check.

**Why a browser, and not a regular expression.** The templates are deliberately
independent systems (`D-007`), and their language controls have nothing in
common to match on: `.lang-switch` buttons carrying `data-lang` on the
MonoMind deck, `#btnEn`/`#btnKo` calling `setLang()` inline on the web
document, architecture, project and motion sites, a cycling `langToggle` on
the multi-page diagrams, a `#langSeg` segmented control driven by a `LANGS`
array on the evidence deck and the paper brief. A pattern that matched all of
those would match half the buttons in the file. So the harness does what a
reader does: it finds the controls, works out what each one selects, and
believes the result.

Two ways a control is understood, in this order:

  declared   the control names its target — `data-lang="ko"`, `data-code`,
             `data-setlang`, or an inline `onclick="setLang('ko')"`. Believed
             without clicking, which matters for the MonoMind deck, whose
             switch hands off to Google Translate and would otherwise need a
             network round trip to observe.
  observed   everything else visible and clickable is clicked, and kept if
             `documentElement.lang` or `body[data-lang]` moves. A cycling
             control is clicked until it returns to where it started, so one
             button that walks three languages reports all three.

The harness, the server and the Chrome plumbing are `check_overflow.py`'s,
imported rather than copied: same in-page `fetch()` POST back to a local
server, same kill-on-result, same two headless modes, same HARNESS ERROR /
finding split (exit 2 vs exit 1). Do not reintroduce `--virtual-time-budget`
here either; that script's docstring says why.

Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from check_overflow import (  # noqa: E402  (path set above)
    ChromeRun,
    find_chrome,
    run_chrome,
    serve,
)

ROOT = pathlib.Path(__file__).resolve().parent.parent

# How many times a single control is clicked before we stop looking for new
# languages. A cycling toggle returns to its start after one lap; eight covers
# every plausible language count with room to spare, and bounds a control that
# cycles something else entirely.
MAX_CYCLE = 8

# The harness iframes the target (same origin — one server serves both), reads
# the boot language, enumerates the controls, and POSTs one JSON object to
# /r/result. It never reports a verdict: it reports what it found, and Python
# decides. That split is deliberate — the answers the file is judged against
# live on the Python side, and a harness that does not know them cannot be
# accused of grading itself.
HARNESS = """<!doctype html><html><head><meta charset="utf-8"><title>langgate</title></head>
<body style="margin:0">
<iframe id="f" src="%(src)s" style="display:block;border:0;width:1280px;height:800px"></iframe>
<script>
var MAX_CYCLE = %(max_cycle)d;

function sleep(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }

function report(payload) {
  fetch('/r/result', { method: 'POST', body: JSON.stringify(payload),
                       headers: { 'Content-Type': 'application/json' } });
}

/* The document's own statement of what language it is in. Both are read
   because the templates disagree about which one they move: the inline
   bilingual files set body[data-lang] and mirror it onto <html lang>, the
   deck moves <html lang> alone. A file that moves neither is handled by the
   `declared` path instead. */
function langState(doc) {
  var b = doc.body ? (doc.body.getAttribute('data-lang') || '') : '';
  var h = doc.documentElement ? (doc.documentElement.getAttribute('lang') || '') : '';
  return (b || h || '').trim();
}

function visible(el) {
  if (!el.isConnected) return false;
  var r = el.getBoundingClientRect();
  if (r.width < 1 || r.height < 1) return false;
  var s = el.ownerDocument.defaultView.getComputedStyle(el);
  return s.visibility !== 'hidden' && s.display !== 'none' && s.opacity !== '0';
}

/* A BCP-47-ish tag, loose enough for the tags these templates actually use
   (en, ko, zh, zh-TW) and tight enough not to swallow "theme" or "html". */
function tag(v) {
  if (!v) return '';
  v = String(v).trim();
  return /^[a-z]{2}(-[A-Za-z]{2,4})?$/.test(v) ? v : '';
}

/* What a control says it selects, without clicking it. */
function declared(el) {
  var attrs = ['data-lang', 'data-code', 'data-setlang', 'data-language', 'value'];
  for (var i = 0; i < attrs.length; i++) {
    var t = tag(el.getAttribute(attrs[i]));
    if (t) return t;
  }
  var on = el.getAttribute('onclick') || '';
  var m = on.match(/(?:setLang|applyLang|switchLang|setLanguage)\\(\\s*['"]([\\w-]+)['"]/);
  if (m) { var t2 = tag(m[1]); if (t2) return t2; }
  return '';
}

async function main() {
  var frame = document.getElementById('f');
  /* Always wait for the load event. A freshly created iframe is already
     sitting on about:blank with readyState 'complete', so testing readyState
     first resolves instantly against an empty document — which is exactly
     what "the target never became reachable" looked like the first time. */
  await new Promise(function (r) {
    var done = false;
    var fin = function () { if (!done) { done = true; r(); } };
    frame.addEventListener('load', fin, { once: true });
    setTimeout(fin, 20000);
  });
  await sleep(400);

  var doc = frame.contentDocument;
  if (!doc || !doc.body) return report({ errors: ['the target document never became reachable'] });

  var boot = langState(doc);
  var reachable = {};
  if (boot) reachable[boot] = 'boot';
  var controls = [];

  var candidates = [].slice.call(doc.querySelectorAll(
    'button, [role="button"], [role="menuitem"], [role="menuitemradio"], ' +
    '[role="option"], a[href="#"], a[href=""], select option'
  )).filter(visible);

  /* Pass 1 — declared. Believed as-is, and never clicked: the MonoMind
     deck's switch hands off to Google Translate, and clicking it here would
     be a network round trip that proves nothing about the control. */
  var undeclared = [];
  for (var i = 0; i < candidates.length; i++) {
    var d = declared(candidates[i]);
    if (d) {
      reachable[d] = 'declared';
      controls.push({ how: 'declared', lang: d,
                      label: (candidates[i].textContent || '').trim().slice(0, 24) });
    } else {
      undeclared.push(candidates[i]);
    }
  }

  /* Pass 2 — observed. Click, watch the document's own language marker, and
     keep whatever it moves to. A control that cycles is clicked until it
     comes back round, so one button walking three languages reports three. */
  for (var j = 0; j < undeclared.length; j++) {
    var el = undeclared[j];
    var before = langState(doc);
    var seen = [];
    for (var k = 0; k < MAX_CYCLE; k++) {
      try { el.click(); } catch (e) { break; }
      await sleep(160);
      var now = langState(doc);
      if (!now || now === before) break;
      if (seen.indexOf(now) !== -1) break;
      seen.push(now);
      if (!reachable[now]) reachable[now] = 'observed';
      controls.push({ how: 'observed', lang: now,
                      label: (el.textContent || '').trim().slice(0, 24) });
      if (now === boot) break;
      before = now;
    }
    /* Put the document back so the next control is probed from the same
       start, and so a cycling control is not left mid-lap. */
    if (langState(doc) !== boot) {
      for (var z = 0; z < MAX_CYCLE && langState(doc) !== boot; z++) {
        try { el.click(); } catch (e) { break; }
        await sleep(120);
      }
    }
  }

  report({ boot: boot, reachable: Object.keys(reachable).sort(),
           controls: controls, errors: [] });
}

main().catch(function (e) { report({ errors: ['HARNESS ERROR ' + e] }); });
</script></body></html>
"""


def normalise(tag: str) -> str:
    """`zh-tw` and `zh-TW` are one language; `en` and `en-GB` are not merged,
    because a template that ships both is making a distinction we should not
    quietly erase."""
    if "-" in tag:
        base, _, region = tag.partition("-")
        return f"{base.lower()}-{region.upper()}"
    return tag.lower()


def probe(chrome: str, target: pathlib.Path) -> tuple[dict | None, list[str]]:
    """The harness's findings for one file, or None plus diagnostics."""
    attempts: list[tuple[str, ChromeRun]] = []
    with tempfile.TemporaryDirectory() as hd:
        page = HARNESS % {"src": f"/t/{target.name}", "max_cycle": MAX_CYCLE}
        (pathlib.Path(hd) / "harness.html").write_text(page, encoding="utf-8")
        srv = serve(hd, str(target.parent))
        try:
            url = f"http://127.0.0.1:{srv.server_address[1]}/h/harness.html"
            for flag, tmo in (("--headless=new", 90.0), ("--headless", 60.0)):
                run = run_chrome(chrome, url, srv, flag, tmo)
                if run.result:
                    try:
                        found = json.loads(run.result)
                    except ValueError:
                        found = None
                    if isinstance(found, dict):
                        return found, []
                attempts.append((flag, run))
        finally:
            srv.shutdown()
    diag = ["HARNESS ERROR: the harness never POSTed a usable result under any "
            "headless mode — an infrastructure failure, not a language "
            "finding. Per-attempt diagnostics follow:"]
    for flag, run in attempts:
        diag.append(f"-- attempt with {flag}:")
        diag.extend("   " + line for line in run.diagnose())
    return None, diag


def judge(found: dict, chosen: list[str]) -> list[str]:
    """Compare what the reader can reach against what was asked for."""
    problems: list[str] = []
    for e in found.get("errors") or []:
        problems.append(f"HARNESS ERROR: {e}" if "HARNESS" not in e else e)
    if problems:
        return problems

    reachable = {normalise(t) for t in (found.get("reachable") or []) if t}
    want = {normalise(t) for t in chosen}
    controls = found.get("controls") or []

    missing = sorted(want - reachable)
    extra = sorted(reachable - want)

    for tag in missing:
        problems.append(
            f"{tag}: chosen in the intake, but nothing in the file selects it. "
            f"The content may be present and hidden behind the language "
            f"attribute — a reader would never find out.")
    for tag in extra:
        how = next((c["how"] for c in controls if normalise(c.get("lang", "")) == tag),
                   "reachable")
        problems.append(
            f"{tag}: offered by the file ({how}) but not chosen in the intake. "
            f"A leftover control either shows untranslated content or does "
            f"nothing at all.")
    if len(want) == 1 and controls:
        labels = ", ".join(sorted({c.get("label") or "?" for c in controls})[:4])
        problems.append(
            f"one language was chosen ({sorted(want)[0]}) but the file still "
            f"carries a language control ({labels}) — "
            f"a one-language switch is a control that does nothing "
            f"(references/applying-answers.md).")
    return problems


def languages_from_intake(path: pathlib.Path) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    answers = payload.get("answers") if isinstance(payload, dict) else None
    langs = (answers or {}).get("languages") if isinstance(answers, dict) else None
    if not isinstance(langs, list) or not langs:
        raise SystemExit(f"error: {path} has no answers.languages array")
    return [str(x) for x in langs]


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="the finished HTML file to check")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--languages",
                     help="comma-separated tags the intake asked for, e.g. en,ko")
    src.add_argument("--intake", help="an intake.json to read answers.languages from")
    ap.add_argument("--json", action="store_true", dest="as_json",
                    help="machine-readable result on stdout")
    args = ap.parse_args()

    target = pathlib.Path(args.file).expanduser().resolve()
    if not target.is_file():
        print(f"error: {target} not found", file=sys.stderr)
        return 2

    if args.intake:
        chosen = languages_from_intake(pathlib.Path(args.intake).expanduser())
    else:
        chosen = [t.strip() for t in args.languages.split(",") if t.strip()]
    if not chosen:
        print("error: no languages given", file=sys.stderr)
        return 2

    chrome = find_chrome()
    if not chrome:
        print("HARNESS ERROR: no Chrome or Chromium found; set CHROME_BIN.",
              file=sys.stderr)
        return 2

    found, diag = probe(chrome, target)
    if found is None:
        for line in diag:
            print(line, file=sys.stderr)
        return 2

    problems = judge(found, chosen)
    harness_error = any(p.startswith("HARNESS ERROR") for p in problems)

    if args.as_json:
        print(json.dumps({"file": str(target), "chosen": chosen,
                          "boot": found.get("boot"),
                          "reachable": found.get("reachable"),
                          "controls": found.get("controls"),
                          "problems": problems}, indent=2, ensure_ascii=False))
    else:
        reach = ", ".join(found.get("reachable") or []) or "none"
        print(f"{target.name}")
        print(f"  chosen:    {', '.join(chosen)}")
        print(f"  reachable: {reach}")
        if problems:
            for p in problems:
                print(f"  FAIL: {p}")
        else:
            print("  ok — every chosen language is reachable, and nothing else is")

    if harness_error:
        return 2
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
