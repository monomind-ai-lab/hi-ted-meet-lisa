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

/* Two different things, and conflating them was this gate's first real bug.
   `<html lang>` is the document's statement about itself — a real BCP-47 tag,
   the thing a screen reader and a search engine read. `body[data-lang]` is
   the template's own CSS key, chosen to drive selectors, and it is NOT a
   language tag: sitemap-ia keys Traditional Chinese as `zh` while paper-brief
   keys the same language as `zh-TW`, and both correctly declare `zh-Hant…` on
   <html>. Reading the key would have reported `zh` for a file the intake
   calls `zh-TW`, and failed a correct build in both directions at once.

   So: the *reported* tag is <html lang> when there is one, and the CSS key
   only as a fallback for a file that never sets it. Change detection watches
   the pair, because a template that moves only one of them still moved. */
function langState(doc) {
  var b = doc.body ? (doc.body.getAttribute('data-lang') || '') : '';
  var h = doc.documentElement ? (doc.documentElement.getAttribute('lang') || '') : '';
  return { tag: (h || b || '').trim(), key: (b + '|' + h).trim() };
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

/* What a control says it selects, without clicking it — attributes only.

   `onclick="setLang('zh')"` was read here once and should not be again: the
   argument is the template's own internal key, the same thing body[data-lang]
   carries, and sitemap-ia passes `zh` for a language the intake calls
   `zh-TW`. An attribute named for the language is a claim about the language;
   an argument to a function is an implementation detail. Controls that only
   have the latter fall through to the observed path, which clicks them and
   reads what the document then says about itself. */
function declared(el) {
  var attrs = ['data-lang', 'data-code', 'data-setlang', 'data-language'];
  for (var i = 0; i < attrs.length; i++) {
    var t = tag(el.getAttribute(attrs[i]));
    if (t) return t;
  }
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

  var bootState = langState(doc);
  var boot = bootState.tag;
  var bootKey = bootState.key;
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
    var before = langState(doc).key;
    var seen = [];
    for (var k = 0; k < MAX_CYCLE; k++) {
      try { el.click(); } catch (e) { break; }
      await sleep(160);
      var st = langState(doc);
      if (!st.tag || st.key === before) break;
      if (seen.indexOf(st.key) !== -1) break;
      seen.push(st.key);
      if (!reachable[st.tag]) reachable[st.tag] = 'observed';
      controls.push({ how: 'observed', lang: st.tag,
                      label: (el.textContent || '').trim().slice(0, 24) });
      if (st.key === bootKey) break;
      before = st.key;
    }
    /* Put the document back so the next control is probed from the same
       start, and so a cycling control is not left mid-lap. */
    if (langState(doc).key !== bootKey) {
      for (var z = 0; z < MAX_CYCLE && langState(doc).key !== bootKey; z++) {
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


# The intake offers exactly these, and `answers.languages` never holds
# anything else — so this is the space a file's declared tag has to be folded
# into before the two can be compared at all. `zh-Hant` is the script subtag
# a document uses to say "Traditional"; the panel calls that `zh-TW`, and the
# two templates that carry it declare it as `zh-Hant` and `zh-Hant-TW`
# respectively. Folding them here rather than in the harness keeps the rule
# testable and keeps the browser reporting what it actually saw.
SCRIPT_FOLDS = {
    "zh-hant": "zh-TW",
    "zh-hans": "zh-CN",
}


def normalise(tag: str) -> str:
    """A declared language tag in the intake's own tag space.

    `zh-tw` and `zh-TW` are one language. `zh-Hant-TW` and `zh-Hant` are that
    same language written the way a document declares itself, and both fold to
    `zh-TW`. `en` and `en-GB` are *not* merged: a file shipping both is making
    a distinction that is not ours to erase.
    """
    if not tag:
        return ""
    parts = [p for p in tag.strip().split("-") if p]
    if not parts:
        return ""
    base = parts[0].lower()
    for n in (2, 1):
        if len(parts) >= n + 1:
            key = f"{base}-{parts[1].lower()}"
            if key in SCRIPT_FOLDS:
                return SCRIPT_FOLDS[key]
            break
    if len(parts) == 1:
        return base
    return f"{base}-{parts[1].upper()}"


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


def check_registry(chrome: str, as_json: bool) -> int:
    """Every first-party template against its own `language_tags`.

    The registry's `languages` is prose written for a reader of the gallery
    card ("Every slide written twice, English and Korean"); `language_tags`
    beside it is the same statement in the intake's own tag space, and it is
    what makes a template checkable at all. An entry with no `file` is a
    handoff (`kind: external`) and owns no languages here.
    """
    entries = json.loads((ROOT / "templates" / "templates.json").read_text())
    results, failures, harness_errors = [], 0, 0
    for t in entries["templates"]:
        if not t.get("file"):
            continue
        tags = t.get("language_tags")
        if not tags:
            results.append((t["id"], ["no `language_tags` in the registry — a "
                                     "template that does not say what it "
                                     "offers cannot be checked"], []))
            failures += 1
            continue
        target = ROOT / t["file"]
        found, diag = probe(chrome, target)
        if found is None:
            results.append((t["id"], diag, []))
            harness_errors += 1
            continue
        problems = judge(found, tags)
        if problems:
            failures += 1 if not any(p.startswith("HARNESS ERROR") for p in problems) else 0
            harness_errors += 1 if any(p.startswith("HARNESS ERROR") for p in problems) else 0
        results.append((t["id"], problems, found.get("reachable") or []))

    if as_json:
        print(json.dumps([{"id": i, "problems": p, "reachable": r}
                          for i, p, r in results], indent=2, ensure_ascii=False))
    else:
        for tid, problems, reachable in results:
            mark = "ok  " if not problems else "FAIL"
            # the normalised form, because that is what was compared: a file
            # declaring `zh-Hant` is judged as the `zh-TW` the intake names,
            # and printing the raw tag would make a passing line look wrong.
            shown = ", ".join(sorted({normalise(x) for x in reachable})) or "—"
            print(f"{mark} {tid:<18} {shown}")
            for p in problems:
                print(f"       {p}")
        n = len(results)
        print(f"\nchecked {n} first-party template{'' if n == 1 else 's'}"
              + ("" if not (failures or harness_errors) else
                 f", {failures} with findings, {harness_errors} unreachable"))
    if harness_errors:
        return 2
    return 1 if failures else 0


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
    ap.add_argument("file", nargs="?", help="the finished HTML file to check")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--languages",
                     help="comma-separated tags the intake asked for, e.g. en,ko")
    src.add_argument("--intake", help="an intake.json to read answers.languages from")
    src.add_argument("--registry", action="store_true",
                     help="check every first-party template against its own "
                          "`language_tags`, and nothing else — the CI mode")
    ap.add_argument("--json", action="store_true", dest="as_json",
                    help="machine-readable result on stdout")
    args = ap.parse_args()

    chrome_for_registry = find_chrome()
    if args.registry:
        if not chrome_for_registry:
            print("HARNESS ERROR: no Chrome or Chromium found; set CHROME_BIN.",
                  file=sys.stderr)
            return 2
        return check_registry(chrome_for_registry, args.as_json)

    if not args.file:
        print("error: a file is required unless --registry is given",
              file=sys.stderr)
        return 2
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
