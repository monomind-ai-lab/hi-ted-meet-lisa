#!/usr/bin/env python3
"""Rendered-overflow gate: fail when any template (or given HTML file) lets
content escape sideways at any tested viewport width.

    python3 scripts/check_overflow.py                 # every first-party template
    python3 scripts/check_overflow.py previews/*.html # specific files
    CHROME_BIN=/path/to/chrome python3 scripts/check_overflow.py

Why this exists: a fixed grid track plus one long unbreakable mono token
(`tedandlisa_thumbs.py` in a 130px command column) overflows the cell and
collides with the neighbouring text without ever widening the document — so
"no horizontal scrollbar" is not enough. Each file is served over localhost,
loaded in headless Chrome inside an iframe (macOS headless Chrome clamps
windows to 500px, so true-375 needs the iframe rig; the wide widths use it
too so one Chrome run covers every width), and measured per width:

  1. document-level: documentElement.scrollWidth vs clientWidth — except when
     the body itself is a horizontal scroll-snap track (the MonoMind deck's
     by-design slide strip); there each snap child must fit the viewport
     instead. The exception is detected from computed style, not a file list.
  2. element-level: any element whose computed overflow-x is `visible` with
     scrollWidth > clientWidth + tolerance has content escaping its own box —
     this is what catches the grid-cell collision. Elements that scroll or
     clip on purpose (overflow-x auto/scroll/hidden, e.g. .tblwrap, .cmd-text)
     are exempt by that same computed style, and so is anything inside a
     horizontally scrolling ancestor (a <pre> in a scrolling code frame is
     contained, not colliding). SVG content is skipped outright — scrollWidth
     has no useful meaning there and diagram label metrics vary by font.

Files with a PAGES/ROUTES hash router keep only the routed page in layout, so
the harness walks every route (in the file's boot language) and measures each.
Chrome is located the way scripts/tedandlisa_thumbs.py locates it, with a
CHROME_BIN environment override for CI. Exit is nonzero with a report naming
file, page, width, and offending element on any failure. Stdlib only.
"""

from __future__ import annotations

import argparse
import http.server
import json
import os
import pathlib
import re
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
]

# (width, height): the two desktop widths the bug class shows at, plus a true
# 375 phone viewport. All rendered inside the iframe of one 2010px window.
WIDTHS = [(1280, 800), (2000, 1100), (375, 667)]
WINDOW = (2010, 1200)
TOLERANCE = 2  # px of sub-pixel rounding forgiven at document/slide level
# Per-element escapes under this are letter-spacing trails, focus-ring slack
# and rounding noise (3-5px was observed on healthy pages); the collision
# class this gate exists for starts well above it (35px+ observed).
ESCAPE_TOLERANCE = 8

SENTINEL = "__OVERFLOW_CHECK_DONE__"

# The harness page iframes the target (same origin, served together), walks
# its hash routes at each width, and appends the JSON verdict in a <pre> that
# the runner greps out of --dump-dom output. Measurement notes:
#  - PAGES/ROUTES are the templates' own global route arrays; the current
#    hash's last segment is swapped per route so the boot language is kept
#    (covers both "#/en/page" and "#en/route" shapes).
#  - inline elements report scrollWidth/clientWidth 0/0 and drop out naturally.
HARNESS = """<!doctype html><html><head><meta charset="utf-8"><title>gate</title></head>
<body style="margin:0">
<iframe id="f" src="%(src)s" style="display:block;border:0;width:1280px;height:800px"></iframe>
<script>
var WIDTHS = %(widths)s, TOL = %(tol)d, ETOL = %(etol)d;
var frame = document.getElementById('f');
function sleep(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }

function measure(win, label) {
  var doc = win.document, de = doc.documentElement, out = [];
  var bodyCS = win.getComputedStyle(doc.body);
  var snapX = /x|both/.test(bodyCS.scrollSnapType) &&
              /(auto|scroll)/.test(bodyCS.overflowX);
  if (snapX) {
    // By-design horizontal slide strip: the document scrolls sideways on
    // purpose; each snap child must fit the viewport instead.
    Array.prototype.forEach.call(doc.body.children, function (s) {
      if (s.clientWidth && s.scrollWidth > s.clientWidth + TOL)
        out.push(label + ' slide <' + s.tagName.toLowerCase() +
                 (s.className ? '.' + String(s.className).trim().split(/\\s+/).join('.') : '') +
                 '> content ' + s.scrollWidth + 'px wide in ' + s.clientWidth + 'px');
      if (s.clientWidth > de.clientWidth + TOL)
        out.push(label + ' slide wider than viewport: ' + s.clientWidth +
                 ' > ' + de.clientWidth);
    });
  } else if (de.scrollWidth > de.clientWidth + TOL) {
    out.push(label + ' document scrolls sideways: scrollWidth ' +
             de.scrollWidth + ' > viewport ' + de.clientWidth);
  }
  Array.prototype.forEach.call(doc.querySelectorAll('body *'), function (el) {
    if (el.namespaceURI !== 'http://www.w3.org/1999/xhtml') return;  // SVG etc.
    if (typeof el.scrollWidth !== 'number' || !el.clientWidth) return;
    if (el.scrollWidth <= el.clientWidth + ETOL) return;
    var cs = win.getComputedStyle(el);
    if (cs.overflowX !== 'visible') return;   // scrolls or clips on purpose
    for (var a = el.parentElement; a && a !== doc.body; a = a.parentElement) {
      var ax = win.getComputedStyle(a).overflowX;
      if (ax === 'auto' || ax === 'scroll') return;  // contained by a scroller
    }
    var name = '<' + el.tagName.toLowerCase() +
               (el.id ? '#' + el.id : '') +
               (el.className && String(el.className).trim() ?
                 '.' + String(el.className).trim().split(/\\s+/).join('.') : '') + '>';
    out.push(label + ' ' + name + ' content escapes its box by ' +
             (el.scrollWidth - el.clientWidth) + 'px');
  });
  return out;
}

async function routesOf(win) {
  var list = win.PAGES || win.ROUTES;
  if (!Array.isArray(list) || !list.length || !win.location.hash) return [null];
  return list.slice();
}

async function main() {
  await new Promise(function (r) {
    if (frame.contentDocument && frame.contentDocument.readyState === 'complete') r();
    else frame.addEventListener('load', r, { once: true });
  });
  await sleep(600);                       // boot scripts, router, reveal arming
  var win = frame.contentWindow, problems = [];
  try { await Promise.race([win.document.fonts.ready, sleep(4000)]); } catch (e) {}
  var routes = await routesOf(win);
  for (var w = 0; w < WIDTHS.length; w++) {
    frame.style.width = WIDTHS[w][0] + 'px';
    frame.style.height = WIDTHS[w][1] + 'px';
    await sleep(300);
    for (var i = 0; i < routes.length; i++) {
      var label = '@' + WIDTHS[w][0];
      if (routes[i] !== null) {
        win.location.hash = win.location.hash.replace(/[^\\/#]+$/, routes[i]);
        await sleep(400);                 // router swap + per-page layout
        label += ' page:' + routes[i];
      }
      try { problems = problems.concat(measure(win, label)); }
      catch (e) { problems.push(label + ' MEASURE ERROR ' + e); }
    }
  }
  var pre = document.createElement('pre');
  pre.id = 'result';
  pre.textContent = '%(sentinel)s' + JSON.stringify(problems);
  document.body.appendChild(pre);
  document.title = '%(sentinel)s';
}
main().catch(function (e) {
  var pre = document.createElement('pre');
  pre.id = 'result';
  pre.textContent = '%(sentinel)s' + JSON.stringify(['HARNESS ERROR ' + e]);
  document.body.appendChild(pre);
});
</script>
</body></html>"""


def find_chrome() -> str | None:
    env = os.environ.get("CHROME_BIN")
    if env:
        if pathlib.Path(env).is_file():
            return env
        # A set-but-wrong CHROME_BIN is a CI misconfiguration; falling back
        # to some other browser would hide it.
        print(f"error: CHROME_BIN is set but not a file: {env}", file=sys.stderr)
        return None
    for c in CHROME_CANDIDATES:
        if pathlib.Path(c).is_file():
            return c
    return shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("chrome")


class TwoTreeHandler(http.server.SimpleHTTPRequestHandler):
    """Serves /h/harness.html from a temp dir and /t/* from the target file's
    own directory, so the harness and the (unmodified) file share an origin."""

    harness_dir: str
    target_dir: str

    def translate_path(self, path):
        path = path.split("?", 1)[0].split("#", 1)[0]
        if path.startswith("/h/"):
            base, rest = self.harness_dir, path[3:]
        elif path.startswith("/t/"):
            base, rest = self.target_dir, path[3:]
        else:
            return os.path.join(self.harness_dir, "does-not-exist")
        rest = os.path.normpath(rest.lstrip("/"))
        if rest.startswith(".."):
            return os.path.join(base, "does-not-exist")
        return os.path.join(base, rest)

    def log_message(self, *args):
        pass


def serve(harness_dir: str, target_dir: str):
    handler = type("H", (TwoTreeHandler,),
                   {"harness_dir": harness_dir, "target_dir": target_dir})
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]


def run_chrome(chrome: str, url: str, timeout: float = 150.0) -> str:
    """Run headless Chrome with --dump-dom, polling stdout for the sentinel so
    a Chrome that writes its output and then fails to exit (a known headless
    quirk, see tedandlisa_thumbs.py) does not stall the whole gate. The
    timeout is generous because a hosted CI runner's first Chrome start is
    cold (font cache, profile creation); the sentinel poll means a healthy
    run never waits it out."""
    with tempfile.TemporaryDirectory() as profile:
        out = pathlib.Path(profile) / "dom.txt"
        cmd = [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
               "--no-first-run", "--no-default-browser-check", "--disable-extensions",
               # Hosted Linux runners need these two or Chrome dies before
               # producing any output: the container has no usable sandbox,
               # and /dev/shm is too small for a renderer. Both are inert on
               # a desktop macOS Chrome, so they are passed unconditionally.
               "--no-sandbox", "--disable-dev-shm-usage",
               f"--user-data-dir={profile}",
               f"--window-size={WINDOW[0]},{WINDOW[1]}",
               "--virtual-time-budget=45000", "--dump-dom", url]
        with open(out, "w") as fo:
            proc = subprocess.Popen(cmd, stdout=fo, stderr=subprocess.DEVNULL,
                                    start_new_session=True)
            deadline = time.monotonic() + timeout
            try:
                while time.monotonic() < deadline:
                    if proc.poll() is not None:
                        break
                    if SENTINEL in out.read_text(encoding="utf-8", errors="replace"):
                        time.sleep(0.5)  # let the dump finish writing
                        break
                    time.sleep(0.5)
            finally:
                if proc.poll() is None:
                    try:
                        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                    except (ProcessLookupError, PermissionError):
                        pass
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        pass
        return out.read_text(encoding="utf-8", errors="replace")


def check_file(chrome: str, target: pathlib.Path) -> list[str]:
    widths_js = json.dumps([[w, h] for w, h in WIDTHS])
    with tempfile.TemporaryDirectory() as hd:
        harness = HARNESS % {"src": f"/t/{target.name}", "widths": widths_js,
                             "tol": TOLERANCE, "etol": ESCAPE_TOLERANCE,
                             "sentinel": SENTINEL}
        (pathlib.Path(hd) / "harness.html").write_text(harness, encoding="utf-8")
        srv, port = serve(hd, str(target.parent))
        try:
            dom = run_chrome(chrome, f"http://127.0.0.1:{port}/h/harness.html")
        finally:
            srv.shutdown()
    m = re.search(re.escape(SENTINEL) + r"(\[.*?\])</pre>", dom, re.DOTALL)
    if not m:
        return ["HARNESS ERROR: Chrome produced no result "
                "(crashed on startup, was killed, or timed out) — "
                "this is an infrastructure failure, not an overflow finding"]
    try:
        import html as _html
        return json.loads(_html.unescape(m.group(1)))
    except ValueError:
        return ["HARNESS ERROR: harness result was not parseable JSON"]


def default_targets() -> list[pathlib.Path]:
    reg = ROOT / "templates" / "templates.json"
    if reg.is_file():
        entries = json.loads(reg.read_text())["templates"]
        files = [ROOT / t["file"] for t in entries
                 if t.get("file") and t.get("kind") != "external"]
        if files:
            return files
    return sorted(ROOT.glob("assets/tedandlisa-template*.html"))


def main() -> int:
    ap = argparse.ArgumentParser(description="Rendered horizontal-overflow gate")
    ap.add_argument("files", nargs="*", type=pathlib.Path,
                    help="HTML files to check (default: every first-party template)")
    args = ap.parse_args()

    chrome = find_chrome()
    if not chrome:
        print("error: no Chrome or Chromium found (set CHROME_BIN)", file=sys.stderr)
        return 2

    targets = [p.resolve() for p in (args.files or default_targets())]
    missing = [str(p) for p in targets if not p.is_file()]
    if missing:
        print("error: not a file: " + ", ".join(missing), file=sys.stderr)
        return 2

    overflowing, broken = 0, 0
    for target in targets:
        problems = check_file(chrome, target)
        rel = os.path.relpath(target)
        # A harness/Chrome breakdown is an infrastructure failure and must
        # not masquerade as a design finding; report and count it apart.
        findings = [p for p in problems
                    if "HARNESS ERROR" not in p and "MEASURE ERROR" not in p]
        errors = [p for p in problems if p not in findings]
        if findings:
            overflowing += 1
            print(f"FAIL {rel}")
        elif errors:
            broken += 1
            print(f"ERROR {rel} — could not be checked")
        else:
            print(f"ok   {rel}")
        for p in findings + errors:
            print(f"     {p}")
    print()
    if overflowing:
        print(f"{overflowing} of {len(targets)} files have horizontal overflow")
    if broken:
        print(f"{broken} of {len(targets)} files could not be checked "
              "(harness or Chrome failure, not an overflow finding)")
    if not overflowing and not broken:
        print(f"all {len(targets)} files clean at "
              + ", ".join(str(w) for w, _ in WIDTHS) + "px")
    return 1 if overflowing else (2 if broken else 0)


if __name__ == "__main__":
    raise SystemExit(main())
